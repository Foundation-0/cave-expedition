import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import par, tasks
from kcommon import header, summary

NSEED = 60
CLASSES = ("ar1_0.9|exp", "pl_1|exp", "ar1_0.9|cube")
CAPS = (100, 1000)


def main():
    part = int(sys.argv[1]) if len(sys.argv) > 1 else None
    classes = CLASSES if part is None else (CLASSES[part],)
    header("X3", "extra, descriptive: K2 rejection rate of the worst flagged classes with the IAAFT iteration cap at 100 and at 1000 (first 60 seeds of K2)" + ("" if part is None else " (part %d of 3: %s)" % (part, classes[0])))
    print("not a plan test; the K2 verdict stays as K2 reports it. The plan fixes no iteration cap (AMENDMENTS_NEEDED.md, A1).")
    jobs = [(c, i, cap) for c in classes for cap in CAPS for i in range(NSEED)]
    res = par.pmap(tasks.sens_task, jobs)
    par.close()
    k = 0
    print("%-14s %5s %7s %7s %11s %10s" % ("class", "cap", "reject", "rate", "iters/surr", "converged"))
    rates = {}
    for c in classes:
        for cap in CAPS:
            rr = res[k:k + NSEED]
            k += NSEED
            n = sum(1 for r in rr if r["reject"])
            rates[(c, cap)] = n / NSEED
            print("%-14s %5d %7d %7.3f %11.1f %10.3f" % (c, cap, n, n / NSEED, sum(r["iters"] for r in rr) / (NSEED * 99.0), sum(r["nconv"] for r in rr) / (NSEED * 99.0)))
    summary("X3" if part is None else "X3-part%d" % part, "DESCRIPTIVE", "rates at cap 100 vs 1000: " + ", ".join("%s %.3f -> %.3f" % (c, rates[(c, 100)], rates[(c, 1000)]) for c in classes))


if __name__ == "__main__":
    main()
