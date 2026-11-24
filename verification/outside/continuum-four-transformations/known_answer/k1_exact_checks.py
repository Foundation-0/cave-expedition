"""K1 Exact checks (PREREG section 10, as amended by Amendment 2, B5 and B6). Integer counts are compared exactly. The identities
of the pipeline under the comparison maps (y^3 + y, exp(y), ranks, with y = x / max|x|), under polarity and over the 27 class versions
are compared bit for bit through digests. Tied inputs: the time-symmetric tied waveform and integer-valued null classes. Four must-fail
controls. Every draw from a K1 seed key uses the run's key epoch (reading D14 as amended by Amendment 4).
usage: k1_exact_checks.py smoke [epoch=0] | full epoch=<k>"""
import io
import contextlib
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import nets, par, patterns, ranks, second_impl, segments, stats43, synth, tasks
from kcommon import Checker, header, summary, parse_cli, sizes

PIPE_N = 1024
REAL_N = (4096, 2048)
VERSIONS = ("", "|exp", "|cube")
MAPS = ("cubic", "exp", "rank")


def min_coverage(nseeds):
    """At least 18 of 20 representable seeds; at smoke size the same fraction, rounded up."""
    return -(-9 * nseeds // 10)


def series_for_counts():
    rng = np.random.default_rng(20261121)
    a = synth.standardise(synth.ar1(0.9, 4096, rng))
    b = np.floor(3.0 * synth.standardise(synth.ar1(0.5, 4096, rng)))
    c = synth.shots_ar(4096, np.random.default_rng(7))
    return {"ar1_0.9": a, "tied_integers": b, "shots": c, "tied_waveform": synth.tied_waveform()}


def counts_tiebreak_by_position(x, d, tau, step=1):
    """MUST-FAIL variant: ties ordered by position (stable argsort) instead of being kept as patterns of their own."""
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


def rank_time_order(x):
    """MUST-FAIL variant (B6): ranks that break ties in time order (double stable argsort) instead of mid-ranks."""
    x = np.asarray(x, dtype=np.float64)
    return np.argsort(np.argsort(x, kind="stable"), kind="stable").astype(np.float64)


def representable(x, y):
    """Representability guard: the mapped series is finite and has as many distinct values as its input."""
    return bool(np.all(np.isfinite(y))) and ranks.n_distinct(x) == ranks.n_distinct(y)


def run_count_checks(C, counter, tag, with_second=True):
    """Integer-count identities using `counter(x, d, tau, step)` -> counts. Cases whose map is not representable are recorded
    as 'map not representable' and are never counted as passes. Returns the number of such cases."""
    S = series_for_counts()
    notrep = 0
    for name, x in S.items():
        with np.errstate(all="ignore"):
            maps = {"cubic": tasks.k1_map(x, "cubic"), "exp": tasks.k1_map(x, "exp"), "rank": tasks.k1_map(x, "rank")}
        for d in (3, 4):
            T = patterns.tables(d)
            for j in range(10):
                tau = 1 << j
                if (d - 1) * tau >= len(x) - 8:
                    continue
                cx = counter(x, d, tau, 1)
                for mn, y in maps.items():
                    if representable(x, y):
                        C.eq("%s counts under %s: %s d=%d tau=%d" % (tag, mn, name, d, tau), counter(y, d, tau, 1), cx)
                    else:
                        notrep += 1
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
    return notrep


def waveform_checks(C, tag, ranker=None):
    """B6 (a): the tied symmetric waveform. At every lag used each pattern count (tied patterns included) equals the count of its
    reversed pattern, so Sigma_hat and a1, a2, a3 are exactly 0, and every pattern count is identical under the three maps.
    With `ranker` (the must-fail time-order ranking) the series is replaced by its ranks first."""
    w = synth.tied_waveform()
    x = w if ranker is None else ranker(w)
    T = patterns.tables(3)
    for j in nets.lag_js(len(x)):
        tau = 1 << j
        c, _ = patterns.counts_one(x, 3, tau)
        C.eq("%s waveform: counts equal reversed counts, tau=%d" % (tag, tau), c, c[T["rev"]])
        C.check("%s waveform: Sigma_hat exactly 0, tau=%d" % (tag, tau), float(patterns.sigma_hat(c, 3)) == 0.0)
        a1, a2, a3 = patterns.a_features(c)
        C.check("%s waveform: a1, a2, a3 exactly 0, tau=%d" % (tag, tau), float(a1) == 0.0 and float(a2) == 0.0 and float(a3) == 0.0)
        if ranker is None:
            with np.errstate(all="ignore"):
                for mn in MAPS:
                    y = tasks.k1_map(x, mn)
                    if representable(x, y):
                        cy, _ = patterns.counts_one(y, 3, tau)
                        C.eq("%s waveform: counts identical under %s, tau=%d" % (tag, mn, tau), cy, c)


def identity_jobs(nseeds, kind, epoch):
    jobs = []
    for base in synth.K2_CLASSES:
        for idx in range(nseeds):
            for ver in VERSIONS:
                cls = base + ver
                variants = ("id", "cubic", "exp", "rank", "neg") if ver == "" else ("id", "cubic", "exp", "rank")
                for v in variants:
                    jobs.append(("class", cls, idx, PIPE_N, v, kind, epoch))
    for base in synth.K2A_CLASSES:
        for idx in range(nseeds):
            for v in ("id", "cubic", "exp", "rank"):
                jobs.append(("int", base, idx, PIPE_N, v, kind, epoch))
    for v in ("id", "cubic", "exp", "rank"):
        jobs.append(("wave", "waveform", 0, 4096, v, kind, epoch))
    return jobs


def pipeline_identity(C, nseeds, tag, kind, epoch):
    """The whole pipeline over the class versions, the integer-valued classes and the waveform. Every case that is representable is
    compared with the plain series bit for bit. Returns (failed checks, coverage dict, case counts)."""
    jobs = identity_jobs(nseeds, kind, epoch)
    res = par.pmap(tasks.k1_task, jobs)
    R = {(j[0], j[1], j[2], j[4]): r for j, r in zip(jobs, res)}
    cov = {}
    nfail0 = len(C.failed)
    ncase = 0
    for (src, cls, idx, n, v, kd, _), r in zip(jobs, res):
        base, _, ver = cls.partition("|")
        refkey = (src, base, idx, "id")
        ref = R[refkey]
        label = "%s %s seed %d %s" % (src, cls, idx, v)
        if src == "class":
            if ver == "" and v == "id":
                continue
            ck = (cls, v if not (ver and v == "id") else "version")
        elif src == "int":
            if v == "id":
                continue
            ck = ("int:" + cls, v)
        else:
            if v == "id":
                continue
            ck = ("wave", v)
        c = cov.setdefault(ck, [0, 0])
        c[1] += 1
        if not r["representable"]:
            print("  map not representable: %s" % label)
            continue
        c[0] += 1
        ncase += 1
        if v == "neg":
            C.eq("%s pool of -x is the negated pool of x: %s" % (tag, label), r["pool"], ref["negpool"])
            C.eq("%s p of -x equals p of x: %s" % (tag, label), r["pn"], ref["pn"])
            C.eq("%s features of -x equal those of x: %s" % (tag, label), r["Z"], ref["Z"])
            continue
        C.eq("%s scores identical: %s" % (tag, label), r["scores"], ref["scores"])
        C.eq("%s pool identical: %s" % (tag, label), r["pool"], ref["pool"])
        C.eq("%s counts identical: %s" % (tag, label), r["C3"], ref["C3"])
        C.eq("%s features identical: %s" % (tag, label), r["Z"], ref["Z"])
        C.eq("%s p identical: %s" % (tag, label), r["pn"], ref["pn"])
    return len(C.failed) - nfail0, cov, ncase


def coverage_report(C, cov, nseeds):
    need = min_coverage(nseeds)
    low = []
    for k in sorted(cov):
        ok, tot = cov[k]
        # the waveform is a single fixed series, not 20 seeds: each of its maps must be representable (1 of 1)
        if ok < (tot if k[0] == "wave" else need):
            low.append((k, ok, tot))
    print("coverage: %d (class version or input, map) combinations; each needs at least %d of %d representable seeds" % (len(cov), need, nseeds))
    for k, ok, tot in low:
        print("  BELOW MINIMUM COVERAGE %s: %d of %d" % (k, ok, tot))
    C.check("minimum coverage: every (class version, map) has at least %d of %d representable seeds" % (need, nseeds), not low)
    nr = sum(tot - ok for ok, tot in cov.values())
    print("cases recorded as 'map not representable': %d (never counted as passes)" % nr)
    return nr


def real_length_scores(C, nseeds, epoch):
    """At 4,096 and 2,048 samples the normal scores of the exp and cube versions equal those of the plain version, exactly, for
    all 9 classes. A version that is not representable is recorded and not counted."""
    n_checked = 0
    notrep = 0
    for n in REAL_N:
        for cls in synth.K2_CLASSES:
            for idx in range(nseeds):
                x = synth.k1_series(cls, idx, n, epoch=epoch)
                z = ranks.normal_scores(x)
                for m in ("exp", "cube"):
                    y = synth.k1_series(cls + "|" + m, idx, n, epoch=epoch)
                    if not representable(x, y):
                        notrep += 1
                        print("  version not representable: %s|%s n=%d seed %d" % (cls, m, n, idx))
                        continue
                    C.eq("normal scores of %s|%s equal the plain class: n=%d seed %d" % (cls, m, n, idx), ranks.normal_scores(y), z)
                    n_checked += 1
    return n_checked, notrep


def offset_identity(C, nseeds, epoch):
    for cls in synth.K2_CLASSES:
        for idx in range(min(nseeds, 10)):
            blk = synth.k1_series(cls, idx, 4096 + 128, epoch=epoch)
            o = segments.best_offset(blk, 4096)
            for nm in ("neg", "cubic", "exp", "rank"):
                with np.errstate(all="ignore"):
                    y = tasks.k1_map(blk, nm)
                if representable(blk, y):
                    C.eq("segment offset of %s under %s: seed %d" % (cls, nm, idx), segments.best_offset(y, 4096), o)


def guard_checks(C):
    v = np.arange(10) * 1e-17
    C.check("guard: exp of values spaced 1e-17 apart is not representable", not representable(v, np.exp(v)))
    C.check("guard: an infinity is not representable", not representable(np.array([1.0, 2.0]), np.array([1.0, np.inf])))
    C.check("guard: a map that keeps the distinct values is representable", representable(v, v * 3.0))
    with np.errstate(all="ignore"):
        z = synth.standardise(np.arange(300.0))
        C.check("guard: exp(exp(z)) is not representable (overflow), the rescaled map is", (not representable(z, np.exp(np.exp(z * 4)))) and representable(z, tasks.k1_map(np.exp(z * 4), "exp")))


def main():
    run = parse_cli(sys.argv, seeded=True, test="K1")
    ep = run["epoch"]
    sz = sizes(run["mode"])
    ns = sz["K1_SEEDS"]
    header("K1", "exact checks", run)
    print("seeds per class version: %d; pipeline identity at n = %d; scores at n = %s; 27 class versions" % (ns, PIPE_N, REAL_N))
    C = Checker()
    print("-- integer counts, complement, reversal, sigma_hat, lag doubling, second implementation (maps on y = x / max|x|)")
    notrep_counts = run_count_checks(C, lambda x, d, tau, step: patterns.counts_batch(np.asarray(x, dtype=np.float64)[None, :], d, tau, step)[0][0], "count")
    print("count-check cases recorded as 'map not representable': %d" % notrep_counts)
    print("-- tied waveform (B6 a): exact symmetry and map identity")
    waveform_checks(C, "wave")
    print("-- representability guard")
    guard_checks(C)
    print("-- offset identity")
    offset_identity(C, ns, ep)
    print("-- normal scores of the exp and cube versions at the K2 lengths, all 9 classes")
    nsc, nrs = real_length_scores(C, ns, ep)
    print("score checks: %d, versions not representable: %d" % (nsc, nrs))
    print("-- pipeline identity: pool, features, p-value (27 class versions, integer-valued classes, waveform)")
    nf, cov, ncase = pipeline_identity(C, ns, "pipe", "iaaft", ep)
    nrep = coverage_report(C, cov, ns)
    print("pipeline identity failures: %d over %d representable cases" % (nf, ncase))
    ok_main = C.done("K1 main checks")
    print("-- must-fail controls (each must produce failing checks)")
    flags = {}
    buf = io.StringIO()
    Cd = Checker()
    with contextlib.redirect_stdout(buf):
        run_count_checks(Cd, lambda x, d, tau, step: patterns.counts_batch(np.asarray(x, dtype=np.float64)[None, :], d, tau, step, last_window_dropped=True)[0][0], "dropped-last-window")
    flags["counter that drops the last window"] = len(Cd.failed)
    Ct = Checker()
    with contextlib.redirect_stdout(buf):
        run_count_checks(Ct, lambda x, d, tau, step: counts_tiebreak_by_position(np.asarray(x, dtype=np.float64), d, tau, step), "tie-break-by-position")
    flags["counter that orders ties by position"] = len(Ct.failed)
    Cr = Checker()
    with contextlib.redirect_stdout(buf):
        nfr, _, _ = pipeline_identity(Cr, min(ns, 10), "raw-surrogates", "raw", ep)
    flags["surrogate step that uses the raw values (identity under exp)"] = nfr
    Cw = Checker()
    with contextlib.redirect_stdout(buf):
        waveform_checks(Cw, "time-order-ranking", rank_time_order)
    flags["ranking that breaks ties in time order (Sigma_hat on the waveform must be non-zero)"] = len(Cw.failed)
    allflag = True
    for k, v in flags.items():
        fl = v > 0
        allflag = allflag and fl
        print("  %-90s failing checks %6d: %s" % (k, v, "FLAGGED" if fl else "NOT FLAGGED"))
    status = "PASS" if (ok_main and allflag) else "FAIL"
    par.close()
    summary("K1", status, "%d main checks, %d failed; cases not representable %d; must-fail controls all flagged: %s" % (C.n, len(C.failed), nrep + nrs + notrep_counts, "yes" if allflag else "NO"), run)


if __name__ == "__main__":
    main()
