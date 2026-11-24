"""Mutation test of the analysis code (PREREG section 11, R5, and B11: every module of src/).
For every refusal, comparison and threshold in src/*.py three kinds of mutant are made:
  refusal   : a `raise` statement replaced by `pass` (the refusal deleted);
  flip      : a comparison <, <=, >, >= replaced by its strict / non-strict counterpart;
  threshold : a numeric constant that is an operand of a comparison moved by one unit (up and down). A unit is 1 for an integer, the
              smallest step of the stated decimal for a decimal (0.05 -> 0.01), one representable step for a float written in
              exponent form (1e-12).
Each mutant is run against the suite (K6, the key check and the unit checks). A mutant is killed if the suite exits non-zero or runs
out of time. Survivors are listed; each is to be killed by an added test or recorded as equivalent with its reason.
Each work copy holds src/, the scripts of known_answer/ and the data files the suite reads there (DATA_FILES). Before any mutant, the
suite runs on the unmutated code in every work copy, and the run stops with exit status 1 unless it passes there: a suite that fails
on correct code would count every mutant as killed.
usage: mutation_test.py count
       mutation_test.py run <work dir> [module ...]      (at most 4 worker processes)
       mutation_test.py run <work dir> --lines <file>    (only mutants on the lines listed as "module.py:lineno", one per line)"""
import ast
import copy
import math
import os
import shutil
import subprocess
import sys
import concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "src")
KA = HERE
FLIP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt}
WORKERS = 4
TIMEOUT = 400
DATA_FILES = ("EPOCHS.tsv",)   # files of known_answer/ other than scripts that the suite reads (the ledger of used key epochs)
SUITE = (("known_answer/k6_gate_checks.py", "smoke"), ("known_answer/key_check.py",), ("known_answer/units_check.py",))


def unit_of(const_node, source_segment):
    """One unit for a numeric constant: 1 for an int, the smallest step of the written decimal, or one representable step."""
    v = const_node.value
    if isinstance(v, int):
        return 1
    text = (source_segment or repr(v)).strip().lower()
    if "e" in text:
        return None  # one representable step, handled by nextafter
    if "." in text:
        return 10.0 ** (-len(text.split(".")[1]))
    return 1.0


def sites(path):
    """Enumerate mutation sites of one module: list of dicts (kind, lineno, col, detail)."""
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            out.append({"kind": "refusal", "lineno": node.lineno, "col": node.col_offset, "id": ("raise", node.lineno, node.col_offset)})
        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if type(op) in FLIP:
                    out.append({"kind": "flip", "lineno": node.lineno, "col": node.col_offset, "idx": i, "id": ("cmp", node.lineno, node.col_offset, i)})
            for operand in [node.left] + list(node.comparators):
                if isinstance(operand, ast.Constant) and isinstance(operand.value, (int, float)) and not isinstance(operand.value, bool):
                    seg = ast.get_source_segment(src, operand)
                    for sign in (+1, -1):
                        out.append({"kind": "threshold", "lineno": operand.lineno, "col": operand.col_offset, "sign": sign,
                                    "seg": seg, "id": ("thr", operand.lineno, operand.col_offset, sign)})
    return src, tree, out


def apply(src, tree, site):
    """Return the mutated source text for one site."""
    t = copy.deepcopy(tree)
    kind = site["kind"]
    for node in ast.walk(t):
        if kind == "refusal" and isinstance(node, ast.Raise) and (node.lineno, node.col_offset) == (site["lineno"], site["col"]):
            new = ast.Pass()
            ast.copy_location(new, node)
            for parent in ast.walk(t):
                for fld, val in ast.iter_fields(parent):
                    if isinstance(val, list):
                        for k, item in enumerate(val):
                            if item is node:
                                val[k] = new
            break
        if kind == "flip" and isinstance(node, ast.Compare) and (node.lineno, node.col_offset) == (site["lineno"], site["col"]):
            node.ops[site["idx"]] = FLIP[type(node.ops[site["idx"]])]()
            break
        if kind == "threshold" and isinstance(node, ast.Constant) and (node.lineno, node.col_offset) == (site["lineno"], site["col"]) \
                and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            v = node.value
            u = unit_of(node, site.get("seg"))
            if isinstance(v, int):
                node.value = v + site["sign"] * 1
            elif u is None:
                node.value = float(math.nextafter(v, math.inf if site["sign"] > 0 else -math.inf))
            else:
                node.value = round(v + site["sign"] * u, 12)
            break
    ast.fix_missing_locations(t)
    return ast.unparse(t) + "\n"


def prepare(work):
    for sub in ("src", "known_answer"):
        d = os.path.join(work, sub)
        if os.path.isdir(d):
            shutil.rmtree(d)
    shutil.copytree(SRC, os.path.join(work, "src"), ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(os.path.join(work, "known_answer"))
    for f in os.listdir(KA):
        if f.endswith(".py") or f in DATA_FILES:
            shutil.copy(os.path.join(KA, f), os.path.join(work, "known_answer", f))


def run_suite(work):
    """Run the suite in one work copy: (failed, why). failed is True if a script exits non-zero or runs out of time."""
    try:
        for script in SUITE:
            r = subprocess.run([sys.executable, "-I", "-B", *script], cwd=work, capture_output=True, text=True, timeout=TIMEOUT)
            if r.returncode != 0:
                return True, "exit %d in %s" % (r.returncode, script[0].split("/")[-1])
    except subprocess.TimeoutExpired:
        return True, "timeout"
    return False, ""


def run_one(args):
    work, module, original, mutated, site = args
    path = os.path.join(work, "src", module)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(mutated)
    try:
        killed, why = run_suite(work)
    finally:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(original)
    return killed, why


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("count", "run"):
        print(__doc__)
        raise SystemExit(2)
    mods = sorted(f for f in os.listdir(SRC) if f.endswith(".py"))
    if sys.argv[1] == "count":
        tot = 0
        for m in mods:
            _, _, s = sites(os.path.join(SRC, m))
            c = {k: sum(1 for x in s if x["kind"] == k) for k in ("refusal", "flip", "threshold")}
            tot += len(s)
            print("%-14s refusal %3d  flip %3d  threshold %3d" % (m, c["refusal"], c["flip"], c["threshold"]))
        print("total mutants", tot)
        return
    work_root = sys.argv[2]
    rest = sys.argv[3:]
    only_lines = None
    if rest[:1] == ["--lines"]:
        only_lines = set()
        with open(rest[1], "r", encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln:
                    mod, no = ln.split(":")
                    only_lines.add((mod, int(no)))
        rest = []
    only = rest
    jobs = []
    for m in mods:
        if only and m not in only:
            continue
        src, tree, ss = sites(os.path.join(SRC, m))
        for s in ss:
            if only_lines is not None and (m, s["lineno"]) not in only_lines:
                continue
            jobs.append((m, src, apply(src, tree, s), s))
    print("mutants to run: %d" % len(jobs))
    # one work copy per worker slot
    slots = [os.path.join(work_root, "w%d" % k) for k in range(WORKERS)]
    for w in slots:
        os.makedirs(w, exist_ok=True)
        prepare(w)
    # baseline: the suite must pass on the unmutated code in every work copy, or no mutant result means anything
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        base = list(ex.map(run_suite, slots))
    bad = [(w, why) for w, (failed, why) in zip(slots, base) if failed]
    if bad:
        for w, why in bad:
            print("BASELINE FAIL in work copy %s: %s" % (os.path.basename(w), why))
        print("STOPPED: the suite fails on the unmutated code, so no mutant was run")
        raise SystemExit(1)
    print("baseline: the suite passes on the unmutated code in all %d work copies" % len(slots))
    results = [None] * len(jobs)

    def worker(k):
        mine = [i for i in range(len(jobs)) if i % WORKERS == k]
        for i in mine:
            m, src, mut, s = jobs[i]
            results[i] = run_one((slots[k], m, src, mut, s))
        return k

    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(worker, range(WORKERS)))
    surv = []
    per = {}
    for (m, src, mut, s), (killed, why) in zip(jobs, results):
        c = per.setdefault(m, {"refusal": [0, 0], "flip": [0, 0], "threshold": [0, 0]})
        c[s["kind"]][1] += 1
        if killed:
            c[s["kind"]][0] += 1
        else:
            surv.append((m, s))
    lines = src_lines = {}
    for m in sorted(per):
        c = per[m]
        print("%-14s killed/total: refusal %d/%d  flip %d/%d  threshold %d/%d" % (m, c["refusal"][0], c["refusal"][1], c["flip"][0], c["flip"][1], c["threshold"][0], c["threshold"][1]))
    tk = sum(1 for r in results if r[0])
    print("TOTAL killed %d of %d, survived %d" % (tk, len(jobs), len(surv)))
    for m, s in surv:
        with open(os.path.join(SRC, m), "r", encoding="utf-8") as fh:
            ln = fh.read().split("\n")[s["lineno"] - 1].strip()
        extra = ""
        if s["kind"] == "threshold":
            extra = " %+d on %s" % (s["sign"], s.get("seg"))
        print("SURVIVOR %s:%d %s%s | %s" % (m, s["lineno"], s["kind"], extra, ln[:110]))


if __name__ == "__main__":
    main()
