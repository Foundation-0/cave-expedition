"""K3. Usage: k3_planted_structure.py [part]
Without an argument all three cases run in one process. With a part number 0 to 2, one case runs.
k3_combine.py joins the part outputs."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import par, seeds, synth, tasks
from kcommon import header, summary

NSEED = 200
NETS = (("native", 0.80), ("bm2", 0.50), ("whiten", 0.50))


def main():
    part = int(sys.argv[1]) if len(sys.argv) > 1 else None
    cases = synth.K3_CASES if part is None else (synth.K3_CASES[part],)
    header("K3", "planted structure found: 200 seeds per case, N = 4096" + ("" if part is None else " (part %d of 3: case %s)" % (part, cases[0])))
    print("cases:", ", ".join(cases), "| seed example, %s idx 0: %d" % (cases[0], seeds.seed_int("K3:" + cases[0], "synthetic", "native", 0, "data", 0)))
    print("nets: native (need >= 0.80), block mean by 2 (need >= 0.50), zero-phase whitening (need >= 0.50)")
    jobs = [(c, n, i, "iaaft") for c in cases for n, _ in NETS for i in range(NSEED)]
    jobs += [(c, "native", i, "leaky") for c in cases for i in range(NSEED)]
    res = par.pmap(tasks.k3_task, jobs)
    par.close()
    k = 0
    allpass = True
    rows = []
    print("%-10s %-8s %7s %7s %6s %8s %8s" % ("case", "net", "detect", "rate", "need", "result", "tie-excl"))
    for c in cases:
        for n, need in NETS:
            rr = res[k:k + NSEED]
            k += NSEED
            nd = sum(1 for r in rr if r["reject"])
            rate = nd / NSEED
            ok = rate >= need
            allpass = allpass and ok
            print("%-10s %-8s %7d %7.3f %6.2f %8s %8d" % (c, n, nd, rate, need, "PASS" if ok else "FAIL", sum(1 for r in rr if r["tie"])))
            rows.append("ROW|%s|%s|%d|%.2f" % (c, n, nd, need))
    print("--- must-fail control: surrogate generator that leaks the time arrow (circular shifts of the series), native net")
    flagged_all = True
    for c in cases:
        rr = res[k:k + NSEED]
        k += NSEED
        nd = sum(1 for r in rr if r["reject"])
        rate = nd / NSEED
        flagged = rate < 0.80
        flagged_all = flagged_all and flagged
        print("%-10s leaky    %7d %7.3f  need>=0.80 -> %s" % (c, nd, rate, "FLAGGED (below criterion)" if flagged else "NOT FLAGGED"))
        rows.append("ROW|%s|leaky|%d|0.80" % (c, nd))
    for r in rows:
        print(r)
    status = "PASS" if (allpass and flagged_all) else "FAIL"
    tag = "K3" if part is None else "K3-part%d" % part
    summary(tag, status if part is None else "PART", "detection criteria %s; leaky-surrogate control %s" % ("all met" if allpass else "NOT all met", "flagged in all cases" if flagged_all else "NOT flagged in all cases"))


if __name__ == "__main__":
    main()
