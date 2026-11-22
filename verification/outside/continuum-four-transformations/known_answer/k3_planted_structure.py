"""K3 Planted structure found (PREREG section 10). Cases: exponential shots on AR(1) 0.9, the logistic map at r = 4, a sawtooth of
period 64 with noise at half its standard deviation (gates), and the same sawtooth with noise standard deviation 0.5 (reported, does not
gate). 200 seeds per case (smoke: one twentieth, at least 10).
Required: segment detection (p <= 0.05) of at least 80 percent on the native net at 4,096 samples and at least 50 percent at 2,048
samples (native) and under block mean by 2, subsampling by 2, 12 and 8 bit quantization, window placement and window length N/2.
Must-fail control: circular-shift surrogates on the shots must give native detection of at most 20 of 200 (smoke: the same fraction).
usage: k3_planted_structure.py smoke|full [part nparts]"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import par, synth, tasks
from kcommon import header, summary, parse_mode, sizes

USES = ("native4096", "native2048", "bm2", "sub2", "q12", "q8", "placement", "wlen2048")
GATING = ("shots", "logistic", "sawtooth")
NEED_80 = {"native4096"}


def items(ns):
    out = []
    for case in synth.K3_CASES:
        for use in USES:
            for idx in range(ns):
                out.append((case, use, idx, "iaaft"))
    for idx in range(ns):
        out.append(("shots", "native4096", idx, "leaky"))
    return out


def evaluate(counts, ns):
    need80 = -(-8 * ns // 10)   # ceil(0.8 ns)
    need50 = -(-5 * ns // 10)   # ceil(0.5 ns)
    cap = (20 * ns) // 200      # at most 20 of 200
    print("seeds per case %d; need at least %d detections native at 4096 and at least %d elsewhere; control must stay at most %d" % (ns, need80, need50, cap))
    print("case              " + " ".join("%-10s" % u for u in USES))
    fails = []
    for case in synth.K3_CASES:
        row = []
        for use in USES:
            k = counts[(case, use, "iaaft")]
            need = need80 if use in NEED_80 else need50
            ok = k >= need
            row.append("%3d/%d%s" % (k, ns, "" if ok else "*"))
            if (not ok) and case in GATING:
                fails.append((case, use, k))
        print("%-16s  %s%s" % (case, " ".join("%-10s" % r for r in row), "" if case in GATING else "   (reported, does not gate)"))
    kc = counts[("shots", "native4096", "leaky")]
    ctrl = kc <= cap
    print("must-fail control (circular-shift surrogates, shots, native 4096): %d of %d detected, bound %d: %s" % (kc, ns, cap, "FLAGGED (control behaves)" if ctrl else "NOT FLAGGED"))
    print("cells below the criterion on gating cases (marked *): %s" % (fails if fails else "none"))
    ok = (not fails) and ctrl
    return ("PASS" if ok else "FAIL"), "%d gating cells below criterion; control flagged: %s" % (len(fails), ctrl)


def main():
    mode = parse_mode(sys.argv)
    ns = sizes(mode)["K3_SEEDS"]
    part = None
    if len(sys.argv) >= 5:
        part, nparts = int(sys.argv[3]), int(sys.argv[4])
    allitems = items(ns)
    mine = allitems if part is None else [it for i, it in enumerate(allitems) if i % nparts == part]
    header("K3", "planted structure found", mode)
    print("segments in this run: %d of %d%s" % (len(mine), len(allitems), "" if part is None else " (part %d of %d)" % (part, nparts)))
    res = par.pmap(tasks.k3_task, mine)
    counts, tot = {}, {}
    for (case, use, idx, kind), r in zip(mine, res):
        key = (case, use, kind)
        counts[key] = counts.get(key, 0) + (1 if r["reject"] else 0)
        tot[key] = tot.get(key, 0) + 1
    if part is not None:
        for key in sorted(counts):
            print("K3COUNT %s %s %s %d %d" % (key[0], key[1], key[2], counts[key], tot[key]))
        par.close()
        return
    status, text = evaluate(counts, ns)
    summary("K3", status, text, mode)
    par.close()
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
