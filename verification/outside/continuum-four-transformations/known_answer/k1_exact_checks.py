"""K1 Exact checks (PREREG section 10). Integer counts compared exactly; identities of the pipeline under increasing maps and
polarity compared bit for bit through digests; three must-fail controls. usage: k1_exact_checks.py smoke|full"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import nets, par, patterns, ranks, second_impl, segments, stats43, synth, tasks
from kcommon import Checker, header, summary, parse_mode, sizes

PIPE_N = 1024      # segment length of the pipeline identity checks (the identity does not depend on length; chosen for cost)
REAL_N = (4096, 2048)


def series_for_counts():
    rng = np.random.default_rng(20261121)
    a = synth.standardise(synth.ar1(0.9, 4096, rng))
    b = np.floor(3.0 * synth.standardise(synth.ar1(0.5, 4096, rng)))      # integer values: many ties
    c = synth.shots_ar(4096, np.random.default_rng(7))
    return {"ar1_0.9": a, "tied_integers": b, "shots": c}


def counts_tiebreak_by_position(x, d, tau, step=1):
    """MUST-FAIL variant: ties are ordered by position (stable argsort) instead of being kept as patterns of their own.
    Returns counts over the untied patterns of patterns.tables(d), in table order."""
    T = patterns.tables(d)
    n = len(x)
    cnt = np.zeros(T["n"], dtype=np.int64)
    for t in range(0, n - (d - 1) * tau, step):
        w = [x[t + k * tau] for k in range(d)]
        order = sorted(range(d), key=lambda k: (w[k], k))
        rk = [0] * d
        for r, k in enumerate(order):
            rk[k] = r
        cnt[T["index"][tuple(rk)]] += 1
    return cnt


def run_count_checks(C, counter, tag, with_second=True, tie_break=False):
    """The integer-count identities of K1 using `counter(x, d, tau, step)` -> counts. Returns nothing; failures are recorded."""
    S = series_for_counts()
    for name, x in S.items():
        maps = {"cubic": x ** 3 + x, "exp": np.exp(x), "rank": nets.increasing_maps()["rank"](x)}
        for d in (3, 4):
            T = patterns.tables(d)
            for j in range(10):
                tau = 1 << j
                if (d - 1) * tau >= len(x) - 8:
                    continue
                cx = counter(x, d, tau, 1)
                for mn, y in maps.items():
                    if nets.map_guard_ok(x, y):
                        C.eq("%s counts under %s: %s d=%d tau=%d" % (tag, mn, name, d, tau), counter(y, d, tau, 1), cx)
                cm = counter(-x, d, tau, 1)
                C.eq("%s complement: %s d=%d tau=%d" % (tag, name, d, tau), cm[T["comp"]], cx)
                cr = counter(x[::-1].copy(), d, tau, 1)
                C.eq("%s reversal: %s d=%d tau=%d" % (tag, name, d, tau), cr[T["rev"]], cx)
                if d == 3:
                    C.check("%s sigma_hat equal for x and -x: %s tau=%d" % (tag, name, tau), patterns.sigma_hat(cm, 3) == patterns.sigma_hat(cx, 3))
                if 2 * tau * 2 < len(x) // 2:
                    ca = counter(x, d, 2 * tau, 2)
                    cb = counter(x[::2].copy(), d, tau, 1)
                    C.eq("%s lag 2 tau on even starts = lag tau of subsample: %s d=%d tau=%d" % (tag, name, d, tau), ca, cb)
    if with_second:
        for name, x in S.items():
            for d in (3, 4):
                names = patterns.tables(d)["names"]
                for tau in (1, 2, 16, 256):
                    ca = counter(x, d, tau, 1)
                    dd, nw = second_impl.pattern_counts(x.tolist(), d, tau)
                    mine = {names[k]: int(ca[k]) for k in range(len(names)) if ca[k]}
                    C.eq("%s second implementation: %s d=%d tau=%d" % (tag, name, d, tau), mine, dd)


def pm_counter(x, d, tau, step):
    return patterns.counts_batch(np.asarray(x, dtype=np.float64)[None, :], d, tau, step)[0][0]


def dropped_counter(x, d, tau, step):
    return patterns.counts_batch(np.asarray(x, dtype=np.float64)[None, :], d, tau, step, last_window_dropped=True)[0][0]


def tiebreak_counter(x, d, tau, step):
    return counts_tiebreak_by_position(np.asarray(x, dtype=np.float64), d, tau, step)


def pipeline_identity(C, nseeds, tag, kind):
    """Pipeline identity over the 7 null classes: for every class and seed the normal scores, the surrogate pool, every
    standardised feature and the p-value are identical for x, x^3+x, exp(x), the ranks, and (up to sign) -x; the exp and cube
    versions of the class give the plain class's results exactly. Returns the number of identity checks that failed."""
    jobs = []
    for cls in synth.K2A_CLASSES:
        for idx in range(nseeds):
            for v in ("id", "cubic", "exp", "rank", "neg", "classexp", "classcube"):
                jobs.append((cls, idx, PIPE_N, v, kind))
    res = par.pmap(tasks.k1_task, jobs)
    R = {(j[0], j[1], j[3]): r for j, r in zip(jobs, res)}
    nfail0 = len(C.failed)
    skipped = 0
    for cls in synth.K2A_CLASSES:
        for idx in range(nseeds):
            base = R[(cls, idx, "id")]
            for v in ("cubic", "exp", "rank", "classexp", "classcube"):
                r = R[(cls, idx, v)]
                if not r["guard"]:
                    skipped += 1
                    print("  map %s merges values for %s seed %d: excluded from the identity" % (v, cls, idx))
                    continue
                C.eq("%s scores identical: %s seed %d %s" % (tag, cls, idx, v), r["scores"], base["scores"])
                C.eq("%s pool identical: %s seed %d %s" % (tag, cls, idx, v), r["pool"], base["pool"])
                C.eq("%s counts identical: %s seed %d %s" % (tag, cls, idx, v), r["C3"], base["C3"])
                C.eq("%s features identical: %s seed %d %s" % (tag, cls, idx, v), r["Z"], base["Z"])
                C.eq("%s p identical: %s seed %d %s" % (tag, cls, idx, v), r["pn"], base["pn"])
            ng = R[(cls, idx, "neg")]
            C.eq("%s pool of -x is the negated pool of x: %s seed %d" % (tag, cls, idx), ng["pool"], base["negpool"])
            C.eq("%s p of -x equals p of x: %s seed %d" % (tag, cls, idx), ng["pn"], base["pn"])
            C.eq("%s features of -x equal those of x: %s seed %d" % (tag, cls, idx), ng["Z"], base["Z"])
    return len(C.failed) - nfail0, skipped


def real_length_scores(C, nseeds):
    """Exact, cheap: at the lengths of K2 (4,096 and 2,048) the normal scores of every exp and cube version equal those of its
    plain class, for every class (7 null classes), seed and length."""
    n_checked = 0
    for n in REAL_N:
        for cls in synth.K2A_CLASSES:
            for idx in range(nseeds):
                x = synth.k2_series(cls, idx, n)
                z = ranks.normal_scores(x)
                for m in ("exp", "cube"):
                    y = synth.k2_series(cls + "|" + m, idx, n)
                    if not nets.map_guard_ok(x, y):
                        print("  version %s merges values: %s n=%d seed %d excluded" % (m, cls, n, idx))
                        continue
                    C.eq("normal scores of %s|%s equal the plain class: n=%d seed %d" % (cls, m, n, idx), ranks.normal_scores(y), z)
                    n_checked += 1
    return n_checked


def offset_identity(C, nseeds):
    for cls in synth.K2A_CLASSES:
        for idx in range(min(nseeds, 10)):
            blk = synth.k2_series(cls, idx, 4096 + 128)
            o = segments.best_offset(blk, 4096)
            for nm, y in (("neg", -blk), ("cubic", blk ** 3 + blk), ("exp", np.exp(blk)), ("rank", nets.increasing_maps()["rank"](blk))):
                if nets.map_guard_ok(blk, y):
                    C.eq("segment offset of %s under %s: %s seed %d" % (cls, nm, cls, idx), segments.best_offset(y, 4096), o)


def main():
    mode = parse_mode(sys.argv)
    sz = sizes(mode)
    ns = sz["K1_SEEDS"]
    header("K1", "exact checks", mode)
    print("seeds per class: %d; pipeline identity at n = %d; scores at n = %s" % (ns, PIPE_N, REAL_N))
    C = Checker()
    print("-- integer counts, complement, reversal, sigma_hat, lag doubling, second implementation")
    run_count_checks(C, pm_counter, "count")
    n_after_counts = C.n
    print("-- offset identity")
    offset_identity(C, ns)
    print("-- normal scores of the exp and cube versions at the K2 lengths")
    nsc = real_length_scores(C, ns)
    print("-- pipeline identity: pool, features, p-value (kind iaaft)")
    nf, skipped = pipeline_identity(C, ns, "pipe", "iaaft")
    print("pipeline identity failures: %d, cases excluded by the distinct-value guard: %d" % (nf, skipped))
    ok_main = C.done("K1 main checks")
    # must-fail controls
    print("-- must-fail controls (each must produce failing checks)")
    flags = {}
    Cd = Checker()
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        run_count_checks(Cd, dropped_counter, "dropped-last-window")
    flags["counter that drops the last window"] = len(Cd.failed)
    Ct = Checker()
    with contextlib.redirect_stdout(buf):
        run_count_checks(Ct, tiebreak_counter, "tie-break-by-position", with_second=True)
    flags["counter that orders ties by position"] = len(Ct.failed)
    Cr = Checker()
    with contextlib.redirect_stdout(buf):
        nfr, _ = pipeline_identity(Cr, min(ns, 10), "raw-surrogates", "raw")
    flags["surrogate step that uses the raw values (identity under exp)"] = nfr
    allflag = True
    for k, v in flags.items():
        fl = v > 0
        allflag = allflag and fl
        print("  %-62s failing checks %6d: %s" % (k, v, "FLAGGED" if fl else "NOT FLAGGED"))
    status = "PASS" if (ok_main and allflag) else "FAIL"
    summary("K1", status, "%d main checks, %d failed; guard exclusions %d; must-fail controls all flagged: %s" % (C.n, len(C.failed), skipped, "yes" if allflag else "NO"), mode)
    if status != "PASS":
        raise SystemExit(1)
    par.close()


if __name__ == "__main__":
    main()
