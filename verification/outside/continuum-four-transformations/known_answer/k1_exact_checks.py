import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import iaaft, nets, patterns, second_impl, seeds, synth
from kcommon import header, summary

TAUS = [2 ** j for j in range(10)]


def count_ok(fn, x, d, tau, step=1):
    c, t, nw = fn(x, d, tau, step)
    return c, t, nw


def good_counts(x, d, tau, step=1):
    return patterns.counts_one(x, d, tau, step)


def broken_off_by_one(x, d, tau, step=1):
    """MUST-FAIL: drops the last window."""
    c, t, nw = patterns.counts_one(np.asarray(x)[:-1], d, tau, step)
    return c, t, nw


def broken_ties(x, d, tau, step=1):
    """MUST-FAIL: breaks ties by position instead of dropping the window."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    perms, codes, rev, comp, names = patterns.tables(d)
    idx = {nm: k for k, nm in enumerate(names)}
    counts = np.zeros(len(perms), dtype=np.int64)
    nw = 0
    for t in range(0, n - (d - 1) * tau, step):
        w = [x[t + k * tau] for k in range(d)]
        nw += 1
        s = "".join(str(sum(1 for j in range(d) if (w[j] < w[i]) or (w[j] == w[i] and j < i))) for i in range(d))
        counts[idx[s]] += 1
    return counts, 0, nw


def suite(fn, sigma_rev=None):
    """Return a list of failure strings; empty means every check passed."""
    fails = []
    d_list = (3, 4)
    perms3, codes3, rev3, comp3, names3 = patterns.tables(3)
    rng = seeds.rng_for("K1", "synthetic", "native", 0, "data", 0)
    x = rng.standard_normal(4096)
    n_checks = 0
    # 1. strictly increasing maps
    for mname, mf in nets.increasing_maps().items():
        y = mf(x)
        for d in d_list:
            for tau in TAUS:
                n_checks += 1
                a = fn(x, d, tau)
                b = fn(y, d, tau)
                if not (np.array_equal(a[0], b[0]) and a[1] == b[1] and a[2] == b[2]):
                    fails.append("monotone map %s d=%d tau=%d" % (mname, d, tau))
    # 2. polarity flip and 3. time reversal relabelling
    for d in d_list:
        perms, codes, rev, comp, names = patterns.tables(d)
        for tau in TAUS:
            n_checks += 2
            a = fn(x, d, tau)
            f = fn(-x, d, tau)
            r = fn(x[::-1].copy(), d, tau)
            if not np.array_equal(f[0], a[0][comp]):
                fails.append("polarity flip d=%d tau=%d" % (d, tau))
            if not np.array_equal(r[0], a[0][rev]):
                fails.append("time reversal d=%d tau=%d" % (d, tau))
    # 4. Sigma_hat equal for x and -x (bitwise)
    for tau in TAUS:
        n_checks += 1
        s1 = patterns.sigma_hat(fn(x, 3, tau)[0], 3, sigma_rev)
        s2 = patterns.sigma_hat(fn(-x, 3, tau)[0], 3, sigma_rev)
        if s1 != s2:
            fails.append("Sigma_hat x vs -x tau=%d (%r vs %r)" % (tau, s1, s2))
    # 5. lag 2 tau over even starts equals lag tau of the series subsampled by 2
    for d in d_list:
        for tau in TAUS[:9]:
            n_checks += 1
            a = fn(x, d, 2 * tau, 2)
            b = fn(x[::2].copy(), d, tau)
            if not (np.array_equal(a[0], b[0]) and a[1] == b[1] and a[2] == b[2]):
                fails.append("lag doubling d=%d tau=%d" % (d, tau))
    # 6. second implementation, every integer count, on series with and without ties
    ys = {"gaussian": x, "ar1_0.9": synth.ar1(0.9, 4096, rng), "quantised_5bit": nets.quantize(x, 5),
          "iaaft_surrogate": iaaft.iaaft_surrogates(x, 1, rng)[0][0],
          "shots": synth.k3_series("shots", 0)}
    for nm, y in ys.items():
        yl = [float(v) for v in y]
        for d in d_list:
            names = patterns.tables(d)[4]
            for tau in TAUS:
                n_checks += 1
                a = fn(y, d, tau)
                b, bt, bn = second_impl.pattern_counts(yl, d, tau)
                bc = np.array([b.get(s, 0) for s in names], dtype=np.int64)
                if not (np.array_equal(a[0], bc) and a[1] == bt and a[2] == bn):
                    fails.append("second implementation %s d=%d tau=%d" % (nm, d, tau))
    return fails, n_checks


def main():
    header("K1", "exact checks")
    fails, n = suite(good_counts)
    print("checks run:", n)
    print("production code failures:", len(fails))
    for f in fails[:10]:
        print("  FAIL", f)
    ok_main = len(fails) == 0
    print("--- must-fail controls (each must be flagged by the suite)")
    all_flagged = True
    wrong_rev = np.array([4, 3, 5, 1, 0, 2], dtype=np.int64)  # pairs 012-201 etc: not the reversal map
    for name, fn, srev in (("off_by_one_window_counter", broken_off_by_one, None),
                           ("tie_breaking_counter", broken_ties, None),
                           ("wrong_reversal_pairing_in_sigma", good_counts, wrong_rev)):
        f, _ = suite(fn, srev)
        flagged = len(f) > 0
        all_flagged = all_flagged and flagged
        print("  %s: %s (%d failing checks)" % (name, "FLAGGED" if flagged else "NOT FLAGGED", len(f)))
    status = "PASS" if (ok_main and all_flagged) else "FAIL"
    summary("K1", status, "%d checks, %d production failures, must-fail controls %s" % (n, len(fails), "all flagged" if all_flagged else "NOT all flagged"))


if __name__ == "__main__":
    main()
