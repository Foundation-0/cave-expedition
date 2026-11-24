"""Shared helpers of the known-answer scripts: command line, header, size labelling (SMOKE, FULL or DIAGNOSTIC), the code commit,
checks of the part files a combine script joins, and checks without bare assert.

Command line of a known-answer script (PREREG section 10, repair rule, and reading D14 as amended by Amendment 4):
    <script> smoke [epoch=0] [part=<p>/<n>]
    <script> full epoch=<k> [part=<p>/<n>]
    <combine script> smoke|full epoch=<k> <part files ...>     (smoke: epoch=0 or no epoch)
A smoke run uses epoch 0 and refuses any other epoch. A full run names its epoch. A full run on epoch 0 is a diagnostic: it cannot pass a
test, and its header and SUMMARY line say DIAGNOSTIC. K6 has no random draws and takes no epoch; the size word has no effect on it, and any
run of it is a full run (Amendment 4). The options are named, so that a part number can never be read from the wrong position.
A full run of a seeded test on an epoch from 1 (not a combine run) is refused unless the ledger EPOCHS.tsv of this checkout allows the
test that epoch (epochs.check_full_run): the lowest epoch from 1 the test has not used. All parts and modes of one run read the same
ledger, since the checkout is not edited while it runs. The ledger of a checkout cannot hold the rows of runs of that same commit that
were recorded after it; run_full.sh also checks the ledger of the runs started from its build folder (FULL_RUN.md)."""
import os
import re
import subprocess
import sys
import numpy as np
import seeds
import epochs

FULL = {"K1_SEEDS": 20, "K2_SEEDS": 1000, "K2_CTRL_SEEDS": 200, "K3_SEEDS": 200, "K4_SEEDS": 10, "K5_SEEDS": 10}
SMOKE_DIV = 20
SMOKE_MIN = 10
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
USAGE = """usage: <script> smoke [epoch=0] [part=<p>/<n>]
       <script> full epoch=<k> [part=<p>/<n>]
       <combine script> smoke|full epoch=<k> <part files ...>
K6 takes no epoch. A smoke run uses epoch 0. A full run on epoch 0 is a diagnostic."""


class UsageError(ValueError):
    pass


def sizes(mode):
    """mode 'full' or 'smoke'. Smoke is one twentieth of the plan's seeds, at least 10, the same seed rule."""
    if mode == "full":
        return dict(FULL)
    if mode == "smoke":
        return {k: max(SMOKE_MIN, v // SMOKE_DIV) for k, v in FULL.items()}
    raise ValueError("size must be 'smoke' or 'full'")


def _whole(text, what):
    """A whole number written in decimal digits with no sign and no leading zero (0 itself allowed)."""
    if not re.fullmatch(r"0|[1-9][0-9]*", text):
        raise UsageError("%s must be a whole number written in digits, got %r" % (what, text))
    return int(text)


def parse_args(argv, seeded, parts=False, files=False):
    """The run a known-answer script is asked for. argv as sys.argv. seeded: the script draws from seed keys (K1 to K5 and their combine
    scripts), so it takes an epoch; K6 does not. parts: the script may run one part (part=<p>/<n>, 0 <= p < n). files: a combine script,
    whose remaining arguments are part files. Raises UsageError on anything else. Returns dict(mode, epoch, part, nparts, files,
    diagnostic): epoch None for a script without draws, diagnostic True for every run that cannot pass a test (a smoke run or a full run
    on epoch 0, of a seeded test). A script without draws has no epoch and no size effect: any run of it is a full run, so it is never a
    diagnostic (Amendment 4: K6 has no seeds, so any run of it is a full run)."""
    if len(argv) < 2 or argv[1] not in ("smoke", "full"):
        raise UsageError("the first argument is the size, smoke or full")
    mode = argv[1]
    epoch = part = nparts = None
    paths = []
    for tok in argv[2:]:
        if tok.startswith("epoch="):
            if not seeded:
                raise UsageError("this test has no random draws and takes no epoch")
            if epoch is not None:
                raise UsageError("the epoch is given twice")
            epoch = _whole(tok[len("epoch="):], "the epoch")
        elif tok.startswith("part="):
            if not parts:
                raise UsageError("this script does not run in parts")
            if part is not None:
                raise UsageError("the part is given twice")
            p, sep, n = tok[len("part="):].partition("/")
            if sep != "/":
                raise UsageError("a part is written part=<p>/<n>")
            part, nparts = _whole(p, "the part number"), _whole(n, "the number of parts")
            if nparts < 1 or part >= nparts:
                raise UsageError("need 0 <= part < number of parts")
        elif files:
            paths.append(tok)
        else:
            raise UsageError("unknown argument %r" % (tok,))
    if seeded:
        if mode == "smoke":
            if epoch is None:
                epoch = 0
            if epoch != 0:
                raise UsageError("a smoke run uses epoch 0 (PREREG section 10), not epoch %d" % epoch)
        elif epoch is None:
            raise UsageError("a full run names its key epoch: epoch=<k> (the lowest epoch from 1 the test has not used, see EPOCHS.tsv)")
    if files and not paths:
        raise UsageError("a combine script needs the part files")
    diagnostic = seeded and (mode == "smoke" or epoch == 0)
    return {"mode": mode, "epoch": epoch, "part": part, "nparts": nparts, "files": paths, "diagnostic": diagnostic}


def ledger_refusal(run, test, rows):
    """Why the ledger rows refuse this run, or None. Only a full run of a seeded test on an epoch from 1 that is not a combine run is
    checked: it must be allowed by epochs.check_full_run (the lowest epoch from 1 the test has not used). A combine run joins parts whose
    epoch it checks, and a run on epoch 0 or without an epoch is not a full-count run under the epoch rule."""
    if run["epoch"] is None or run["mode"] != "full" or run["epoch"] < 1 or run["files"]:
        return None
    return epochs.check_full_run(rows, test, run["epoch"])


def parse_cli(argv, seeded, parts=False, files=False, test=None):
    """parse_args for a script's main: a usage error prints the usage and ends the script with exit status 2. test: the test id of a
    seeded script that is not a combine script; its full run on an epoch from 1 is checked against the ledger EPOCHS.tsv of this
    checkout (ledger_refusal), and a refusal also ends the script with exit status 2, before any draw."""
    try:
        run = parse_args(argv, seeded, parts, files)
    except UsageError as e:
        print("usage error:", e)
        print(USAGE)
        raise SystemExit(2)
    if seeded and not files and run["mode"] == "full" and run["epoch"] >= 1:
        if test is None:
            raise ValueError("parse_cli needs the test id of a seeded script to check its epoch against the ledger")
        try:
            why = ledger_refusal(run, test, epochs.read_ledger())
        except (OSError, epochs.LedgerError) as e:
            why = "the ledger cannot be read: %s" % (e,)
        if why is not None:
            print("refused by the ledger known_answer/EPOCHS.tsv:", why)
            raise SystemExit(2)
    return run


def label(run):
    """The SIZE text of the header."""
    if run["epoch"] is None:
        if run["mode"] == "smoke":
            return "SMOKE, the same run as FULL (this test has no random draws, so the size has no effect and any run of it is a full run)"
        return "FULL"
    if run["mode"] == "smoke":
        return "SMOKE (one twentieth of the plan's seeds, at least 10, on epoch 0; a diagnostic, NOT a result)"
    if run["epoch"] == 0:
        return "FULL, DIAGNOSTIC (epoch 0: a run on epoch 0 is a diagnostic and cannot pass a test, PREREG section 10)"
    return "FULL"


def summary_tag(run):
    """The word put before PASS or FAIL in the SUMMARY line: SMOKE, DIAGNOSTIC or nothing. A run of a test without draws is a full run
    whatever its size word, so it has none."""
    if run["epoch"] is None:
        return ""
    if run["mode"] == "smoke":
        return "SMOKE "
    if run["epoch"] == 0:
        return "DIAGNOSTIC "
    return ""


def code_commit():
    """The git commit of the checkout that holds this package, with '+modified' when a tracked file of the package differs from it,
    or 'unknown' when git cannot tell. Reads only (optional locks off), so it also works where writes are refused."""
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    try:
        h = subprocess.run(["git", "-C", PKG, "rev-parse", "HEAD"], capture_output=True, text=True, encoding="utf-8", timeout=120, env=env)
        s = subprocess.run(["git", "-C", PKG, "status", "--porcelain", "--untracked-files=no", "--", "."], capture_output=True, text=True,
                           encoding="utf-8", timeout=120, env=env)
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    commit = h.stdout.strip()
    if h.returncode != 0 or s.returncode != 0 or not re.fullmatch(r"[0-9a-f]{40}", commit):
        return "unknown"
    return commit + ("+modified" if s.stdout.strip() else "")


def run_line(tid, run, commit):
    """The machine-readable line of the header, which a combine script checks for every part."""
    part = "-" if run["part"] is None else "%d/%d" % (run["part"], run["nparts"])
    epoch = "-" if run["epoch"] is None else str(run["epoch"])
    return "RUN test=%s size=%s epoch=%s part=%s commit=%s" % (tid, run["mode"], epoch, part, commit)


def header(tid, title, run, commit=None):
    """Print the header. commit defaults to code_commit()."""
    commit = code_commit() if commit is None else commit
    print("TEST", tid, "-", title)
    print("SIZE", label(run))
    if run["epoch"] is None:
        print("EPOCH not used (this test has no random draws)")
    else:
        print("EPOCH %d | master field %s" % (run["epoch"], seeds.master_field(run["epoch"])))
    print("CODE COMMIT", commit)
    if run["part"] is not None:
        print("PART %d of %d (parts 0 to %d)" % (run["part"], run["nparts"], run["nparts"] - 1))
    print(run_line(tid, run, commit))
    print("python", sys.version.split()[0], "numpy", np.__version__)
    if run["epoch"] is not None:
        print("seed rule: first 16 hex digits of SHA-256 of", seeds.seed_string("<instrument>", "<split>", "<net>", "<segment>", "<purpose>", "<index>", epoch=run["epoch"]))


def summary(tid, status, text, run):
    """Print the summary line. Any status other than PASS ends the script with exit status 1 (never 0 on FAIL). The line says SMOKE for a
    smoke run and DIAGNOSTIC for a full run on epoch 0, of a seeded test."""
    if status not in ("PASS", "FAIL"):
        raise ValueError("status must be PASS or FAIL")
    print("SUMMARY", tid, summary_tag(run) + status, "|", text)
    sys.stdout.flush()
    if status != "PASS":
        raise SystemExit(1)


def parse_run_line(line):
    """The fields of a RUN line as a dict of strings."""
    toks = line.split()
    if not toks or toks[0] != "RUN":
        raise ValueError("not a RUN line")
    out = {}
    for t in toks[1:]:
        k, sep, v = t.partition("=")
        if sep != "=" or k in out:
            raise ValueError("bad RUN line: %r" % (line,))
        out[k] = v
    if set(out) != {"test", "size", "epoch", "part", "commit"}:
        raise ValueError("bad RUN line: %r" % (line,))
    return out


def read_run_line(path):
    """The RUN line of a part file (its first one), as parse_run_line gives it."""
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("RUN "):
                return parse_run_line(line)
    raise ValueError("%s has no RUN line" % path)


def check_parts(lines, tid, run, commit):
    """Refusals of a combine script. lines: the RUN line fields of each part file. Every part must be a part of test tid, of the same
    size and key epoch as this combine run, from one clean commit equal to this combine run's commit, and the parts must cover part 0 to
    n - 1 exactly once with one n. Returns a list of faults (empty when the parts may be joined)."""
    faults = []
    if not lines:
        return ["no part files"]
    want_epoch = "-" if run["epoch"] is None else str(run["epoch"])
    if commit == "unknown" or commit.endswith("+modified"):
        faults.append("the combine run's own code commit is %s: parts can be joined only on one clean commit" % commit)
    seen, ns = [], set()
    for k, f in enumerate(lines):
        if f["test"] != tid:
            faults.append("part file %d is of test %s, not %s" % (k, f["test"], tid))
        if f["size"] != run["mode"]:
            faults.append("part file %d has size %s, the combine run %s" % (k, f["size"], run["mode"]))
        if f["epoch"] != want_epoch:
            faults.append("part file %d is on epoch %s, the combine run on epoch %s" % (k, f["epoch"], want_epoch))
        if f["commit"] != commit:
            faults.append("part file %d is from code commit %s, the combine run from %s" % (k, f["commit"], commit))
        p, sep, n = f["part"].partition("/")
        if sep != "/" or not (p.isdigit() and n.isdigit()):
            faults.append("part file %d is not a part (part=%s)" % (k, f["part"]))
            continue
        seen.append(int(p))
        ns.add(int(n))
    if len(ns) > 1:
        faults.append("the parts disagree on the number of parts: %s" % sorted(ns))
    elif ns and sorted(seen) != list(range(ns.pop())):
        faults.append("the parts do not cover each part number exactly once: %s" % sorted(seen))
    return faults


def join_parts(tid, run):
    """For a combine script: read the RUN line of every part file and refuse (exit status 1) unless check_parts finds no fault. Returns
    the commit, which the combine script prints in its own header."""
    commit = code_commit()
    try:
        lines = [read_run_line(p) for p in run["files"]]
    except (OSError, ValueError) as e:
        print("FAIL: cannot read the parts:", e)
        raise SystemExit(1)
    faults = check_parts(lines, tid, run, commit)
    if faults:
        print("FAIL: the parts cannot be joined:")
        for x in faults:
            print("  " + x)
        raise SystemExit(1)
    return commit


class Checker:
    """Collects checks. Never uses assert. fail() count decides the exit status."""

    def __init__(self):
        self.n = 0
        self.failed = []

    def check(self, name, cond):
        self.n += 1
        if not bool(cond):
            self.failed.append(name)
            print("  FAIL", name)
        return bool(cond)

    def eq(self, name, a, b):
        ok = (a == b)
        if isinstance(ok, np.ndarray):
            ok = bool(ok.all()) and np.shape(a) == np.shape(b)
        return self.check(name, ok)

    def done(self, tag):
        print("%s: %d checks, %d failed" % (tag, self.n, len(self.failed)))
        return len(self.failed) == 0
