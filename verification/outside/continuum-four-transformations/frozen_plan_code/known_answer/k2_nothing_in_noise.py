"""K2. Usage: k2_nothing_in_noise.py [part]
Without an argument all 21 classes run in one process (about 2.7 hours of processor time).
With a part number 0 to 6, only the three classes of one base noise run (plain, exp, cube).
k2_combine.py joins the part outputs into the K2 verdict."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import calibration, par, seeds, synth, tasks
from kcommon import header, summary

NSEED = 200
BOUND = 0.086


def main():
    part = int(sys.argv[1]) if len(sys.argv) > 1 else None
    allc = synth.k2_class_names()
    classes = allc if part is None else [c for c in allc if c.partition("|")[0] == synth.K2_BASES[part]]
    header("K2", "nothing found in noise: 200 seeds per class, N = 4096" + ("" if part is None else " (part %d of 7: base noise %s)" % (part, synth.K2_BASES[part])))
    print("classes in this run:", len(classes), "| seed example, class %s idx 0: %d" % (classes[0], seeds.seed_int("K2:" + classes[0], "synthetic", "native", 0, "data", 0)))
    print("IAAFT: provisional rule, start from a random permutation, stop when ranks stop changing or at 100 rounds")
    jobs = [(c, i) for c in classes for i in range(NSEED)]
    res = par.pmap(tasks.k2_task, jobs)
    par.close()
    print("%-18s %6s %7s %8s %8s %9s %8s %7s" % ("class", "reject", "rate", "flagged", "tie/deg", "iters/surr", "converged", "slope"))
    nflag = 0
    slopes = {}
    broken_rate = {}
    rows = []
    k = 0
    for c in classes:
        rr = res[k:k + NSEED]
        k += NSEED
        nrej = sum(1 for r in rr if r["reject"])
        rate = nrej / NSEED
        flagged = rate > BOUND
        nflag += int(flagged)
        meds = np.median(np.stack([r["pg"] for r in rr]), axis=0)
        sl = calibration.loglog_slope(meds, 4096)
        slopes[c] = sl
        nb = sum(1 for r in rr if r["lag_min_pn"] * 20 <= 100)
        broken_rate[c] = nb / NSEED
        it = sum(r["iters"] for r in rr) / (NSEED * 99.0)
        cv = sum(r["nconv"] for r in rr) / (NSEED * 99.0)
        nd = sum(1 for r in rr if r["tie"] or r["deg"])
        print("%-18s %6d %7.3f %8s %8d %9.1f %8.3f %7.2f" % (c, nrej, rate, "FLAGGED" if flagged else "ok", nd, it, cv, sl))
        rows.append("ROW|%s|%d|%d|%d|%.6f" % (c, nrej, nb, nd, sl))
    print("classes flagged (rate > %.3f): %d of %d" % (BOUND, nflag, len(classes)))
    print("must-fail control, detector with no correction for the ten lags (rejects if the best single-lag p <= 0.05), rate per class:")
    for c in classes:
        print("  %-18s %.3f %s" % (c, broken_rate[c], "above the bound" if broken_rate[c] > BOUND else "inside the bound"))
    for r in rows:
        print(r)
    if part is None:
        # matching rule, shown on synthetic periodograms (no real instrument is touched)
        demo = {}
        for c in ("ar1_0.9", "pl_1", "white"):
            pg = np.median(np.stack([np.abs(np.fft.rfft(synth.k2_series(c, 1000 + i))) ** 2 for i in range(20)]), axis=0)
            demo[c] = calibration.match_class(calibration.loglog_slope(pg, 4096), slopes)
        print("slope matching demo (fresh seeds 1000..1019, true class -> matched class):", ", ".join("%s -> %s" % (a, b) for a, b in demo.items()))
        flagged_control = broken_rate["white"] > BOUND
        status = "PASS" if (nflag == 0 and flagged_control) else "FAIL"
        summary("K2", status, "%d of %d classes above the 0.086 bound; must-fail control %s" % (nflag, len(classes), "flagged" if flagged_control else "NOT flagged"))
    else:
        summary("K2-part%d" % part, "PART", "%d of %d classes above the 0.086 bound" % (nflag, len(classes)))


if __name__ == "__main__":
    main()
