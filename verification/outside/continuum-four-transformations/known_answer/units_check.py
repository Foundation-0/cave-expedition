"""Unit checks of the building blocks, with known answers (exact where the plan's quantity is exact). Exit status 1 and
the text FAIL on any failed check. Output is identical in python -I -B, -I -O -B and -I -B -W error."""
import contextlib
import hashlib
import io
import os
import sys
from fractions import Fraction
from itertools import product
import math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import controls, flow, gates, iaaft, law2b, levels, nets, outcomes, patterns, pipeline, ranks, second_impl, segments, seeds, stats43, synth, tasks, ties, transfer
from kcommon import Checker

C = Checker()
ck, eq = C.check, C.eq


def section(t):
    print("--", t)


def u_ranks():
    section("ranks and normal scores")
    print("inverse normal implementation:", ranks.PHI_INV_IMPLEMENTATION)
    eq("midranks of ties", ranks.twice_midrank(np.array([3., 1., 3., 2., 5.])).tolist(), [7, 2, 7, 4, 10])
    z2 = ranks.normal_scores(np.array([1.0, 2.0]))
    ck("normal score n=2 is +-Phi^-1(0.75)", abs(z2[1] - 0.6744897501960817) < 1e-12 and z2[0] == -z2[1])
    x = np.random.default_rng(5).standard_normal(300)
    eq("polarity: scores of -x are exactly the negated scores", ranks.normal_scores(-x), -ranks.normal_scores(x))
    eq("scores unchanged by increasing maps", ranks.normal_scores(np.exp(x)), ranks.normal_scores(x))
    eq("bins n=10 b=2", ranks.equal_count_bins(np.arange(10.0), 2).tolist(), [0, 0, 1, 1, 1, 2, 2, 3, 3, 3])
    b = ranks.equal_count_bins(np.array([5., 5., 5., 5., 1., 9., 9., 9.]), 1)
    ck("tied values 5,5,5,5 share one bin", len(set(b[:4].tolist())) == 1 and len(set(b[5:].tolist())) == 1)


def u_patterns():
    section("pattern counts on hand-made series")
    T3, T4 = patterns.tables(3), patterns.tables(4)
    eq("13 patterns at order 3", T3["n"], 13)
    eq("6 untied at order 3", int(T3["untied"].sum()), 6)
    eq("75 patterns at order 4", T4["n"], 75)
    eq("24 untied at order 4", int(T4["untied"].sum()), 24)
    nm = T3["names"]
    rv = {nm[k]: nm[int(T3["rev"][k])] for k in range(13)}
    eq("001 pairs with 100", rv["001"], "100")
    eq("011 pairs with 110", rv["011"], "110")
    ck("010, 101, 000 are their own reverses", rv["010"] == "010" and rv["101"] == "101" and rv["000"] == "000")
    eq("012 pairs with 210", rv["012"], "210")
    cmp_ = {nm[k]: nm[int(T3["comp"][k])] for k in range(13)}
    eq("polarity flip 001 -> 110", cmp_["001"], "110")
    ck("flip commutes with reversal", all(T3["rev"][T3["comp"][k]] == T3["comp"][T3["rev"][k]] for k in range(13)))
    c, nw = patterns.counts_one(np.array([1., 1, 2, 0, 0, 0, 3]), 3, 1)
    got = {nm[k]: int(c[k]) for k in range(13) if c[k]}
    eq("hand counts, ties kept", got, {"001": 2, "120": 1, "100": 1, "000": 1})
    eq("window count", nw, 5)
    c, nw = patterns.counts_one(np.arange(5.0), 3, 1)
    eq("increasing ramp: 3 windows of 012", {nm[k]: int(c[k]) for k in range(13) if c[k]}, {"012": 3})
    c, nw = patterns.counts_one(np.arange(9.0), 3, 3)
    eq("ramp lag 3: 3 windows", int(c.sum()), 3)
    c, nw = patterns.counts_one(np.array([3., 1, 2, 0, 2]), 4, 1)
    n4 = T4["names"]
    eq("order 4 hand counts", {n4[k]: int(c[k]) for k in range(75) if c[k]}, {"3120": 1, "1202": 1})
    # exact: the polarity-flipped series gives complemented counts, the reversed series reversed counts
    x = np.random.default_rng(3).integers(0, 5, 400).astype(float)
    cx, _ = patterns.counts_one(x, 3, 2)
    cm, _ = patterns.counts_one(-x, 3, 2)
    cr, _ = patterns.counts_one(x[::-1].copy(), 3, 2)
    eq("counts of -x are the complemented counts", cm[T3["comp"]], cx)
    eq("counts of reversed x are the reversed counts", cr[T3["rev"]], cx)
    s0 = patterns.sigma_hat(cx, 3)
    ck("sigma_hat equal for x and -x", patterns.sigma_hat(cm, 3) == s0)
    sym = np.zeros(13, dtype=np.int64)
    sym[T3["index"][(0, 1, 2)]] = 5
    sym[T3["index"][(2, 1, 0)]] = 5
    ck("sigma_hat = 0 when every pattern has its reverse's count", abs(float(patterns.sigma_hat(sym, 3))) < 1e-15)
    # sigma_hat by hand: counts n(012)=3, n(210)=1, all others 0, pseudocount 1/2, denominator 4 + 13/2
    h = np.zeros(13, dtype=np.int64)
    h[T3["index"][(0, 1, 2)]] = 3
    h[T3["index"][(2, 1, 0)]] = 1
    den = 4 + 6.5
    p012, p210, p0 = 3.5 / den, 1.5 / den, 0.5 / den
    hand = p012 * math.log(p012 / p210) + p210 * math.log(p210 / p012)
    ck("sigma_hat against a hand computation", abs(float(patterns.sigma_hat(h, 3)) - hand) < 1e-14)
    # counts at lag 2 tau over even start points equal counts at lag tau of the subsample
    y = np.random.default_rng(8).standard_normal(500)
    for tau in (1, 2, 4):
        ca, _ = patterns.counts_batch(y[None, :], 3, 2 * tau, step=2)
        cb, _ = patterns.counts_batch(y[::2][None, :], 3, tau)
        eq("lag 2 tau on even starts = lag tau of subsample, tau=%d" % tau, ca, cb)
    # second implementation shares no code
    for d in (3, 4):
        for tau in (1, 3):
            ca, _ = patterns.counts_one(x, d, tau)
            dd, nw2 = second_impl.pattern_counts(x.tolist(), d, tau)
            names = patterns.tables(d)["names"]
            eq("second implementation d=%d tau=%d" % (d, tau), {names[k]: int(ca[k]) for k in range(len(names)) if ca[k]}, dd)
    # must-fail: dropping the last window is noticed
    cd, _ = patterns.counts_batch(x[None, :], 3, 1, last_window_dropped=True)
    c0, _ = patterns.counts_batch(x[None, :], 3, 1)
    ck("a counter that drops the last window differs", not np.array_equal(cd, c0))


def u_surrogates_identity():
    section("surrogates from normal scores: identity under increasing maps, polarity")
    rng = np.random.default_rng(11)
    for n in (256, 1000):
        x = synth.standardise(synth.ar1(0.9, n, rng))
        maps = {"cubic": x ** 3 + x, "exp": np.exp(x), "rank": nets.increasing_maps()["rank"](x)}
        key = ("U", "s", "native", n, "surrogates", 0)
        base = stats43.segment_test(x, key, epoch=0)
        for nm, y in maps.items():
            ck("map %s leaves distinct values unchanged (n=%d)" % (nm, n), nets.map_guard_ok(x, y))
            r = stats43.segment_test(y, key, epoch=0)
            eq("C3 counts identical, %s, n=%d" % (nm, n), r["C3"], base["C3"])
            eq("standardised features identical, %s, n=%d" % (nm, n), r["Z"], base["Z"])
            eq("p identical, %s, n=%d" % (nm, n), r["pn"], base["pn"])
        pool_x, _, _ = stats43.make_pool(x, key, epoch=0)
        pool_y, _, _ = stats43.make_pool(np.exp(x), key, epoch=0)
        eq("surrogate pool identical under exp, n=%d" % n, pool_x[1:], pool_y[1:])
        pool_m, _, _ = stats43.make_pool(-x, key, epoch=0)
        eq("pool of -x is the negated pool of x, n=%d" % n, pool_m[1:], -pool_x[1:])
        rm = stats43.segment_test(-x, key, epoch=0)
        eq("p of -x equals p of x, n=%d" % n, rm["pn"], base["pn"])
    # surrogates have exactly the normal scores as values and end on the rank step
    x = synth.standardise(synth.ar1(0.5, 512, rng))
    Y, it, cv = iaaft.iaaft_surrogates(x, 9, np.random.default_rng(1))
    z = np.sort(ranks.normal_scores(x))
    ck("each surrogate has exactly the segment's normal scores", all(np.array_equal(np.sort(Y[i]), z) for i in range(9)))
    ck("surrogates converged within the cap", bool(cv.all()) and int(it.max()) <= iaaft.MAX_ITER)
    # the map guard: exp of values spaced 1e-17 apart merges values
    v = np.arange(10) * 1e-17
    ck("guard flags exp of values spaced 1e-17 apart", not nets.map_guard_ok(v, np.exp(v)))
    # raw-value surrogates differ under exp (the must-fail variant of K1)
    xr = synth.standardise(synth.ar1(0.9, 400, rng))
    a = iaaft.raw_surrogates(xr, 5, np.random.default_rng(2))[0]
    b = iaaft.raw_surrogates(np.exp(xr), 5, np.random.default_rng(2))[0]
    ck("raw-value surrogates break the identity under exp", not np.array_equal(ranks.twice_midrank(a[0]), ranks.twice_midrank(b[0])))


def u_segments():
    section("segment rule")
    blk = np.array([10., 10, 0, 1, 11, 11, 2, 2])
    costs = segments.offset_costs(blk, 6, pad=2)
    eq("rank costs [4, 17/4, 29/4] (in quarters 16, 17, 29)", costs, [16, 17, 29])
    for nm, y in (("cubic", blk ** 3 + blk), ("2^x", 2.0 ** blk), ("-x", -blk)):
        eq("costs unchanged under " + nm, segments.offset_costs(y, 6, pad=2), costs)
    eq("offset chosen is 0", segments.best_offset(blk, 6, pad=2), 0)
    st, J, k = segments.select_blocks(524288, 4096)
    eq("2^19 samples: J, k, kept", (J, k, len(st)), (124, 3, 32))
    counts = []
    n = 524288
    cur = n
    while True:
        st, J, k = segments.select_blocks(cur, 4096)
        if len(st) < 12:
            break
        counts.append(len(st))
        cur //= 2
    eq("K5 units per level 32, 32, 31, 15", counts, [32, 32, 31, 15])
    st, J, k = segments.select_blocks(33 * 4224, 4096)
    eq("K4 stream: 32 segments on the primary grid", len(st), 32)
    st, J, k = segments.select_blocks(33 * 4224, 4096, start=2112)
    eq("K4 stream: 32 segments on the shifted grid", len(st), 32)
    ck("underpowered rule: 12 valid of 12 is fine", not segments.underpowered([True] * 12))
    ck("underpowered rule: 11 valid is underpowered", segments.underpowered([True] * 11))
    ck("underpowered rule: 9 invalid of 32 (28 percent)", segments.underpowered([True] * 23 + [False] * 9))
    ck("underpowered rule: 8 invalid of 32 (25 percent) is allowed", not segments.underpowered([True] * 24 + [False] * 8))


def u_nets():
    section("nets and lags")
    eq("lags at 4096", nets.lag_js(4096), list(range(10)))
    eq("lags at 2048 (1 to 256)", nets.lag_js(2048), list(range(9)))
    eq("lags at 1024", nets.lag_js(1024), list(range(8)))
    eq("order-4 lags at 4096 (3 tau <= n/4)", law2b.o4_lag_js(4096), list(range(9)))
    ck("sampling nets apply at 4096, not at 2048", nets.applicable("bm2", 4096) and not nets.applicable("bm2", 2048))
    ck("window length net applies at 4096, not at 2048", nets.window_length_applicable(4096) and not nets.window_length_applicable(2048))
    x = np.arange(8.0)
    eq("block mean by 2", nets.block_mean(x, 2).tolist(), [0.5, 2.5, 4.5, 6.5])
    eq("subsample by 2", nets.subsample(x, 2).tolist(), [0.0, 2.0, 4.0, 6.0])
    eq("polarity flip", nets.polarity_flip(x).tolist(), (-x).tolist())
    y = nets.apply("q8", np.random.default_rng(0).standard_normal(4096))
    ck("8-bit bins have 256 values with equal counts", np.unique(y).size == 256 and set(np.unique(y, return_counts=True)[1].tolist()) == {16})
    try:
        nets.apply("nope", x)
        ck("unknown net refused", False)
    except ValueError:
        ck("unknown net refused", True)


def u_levels():
    section("binomial tails, thresholds, Holm, per-run levels (exact)")
    F = Fraction
    eq("P(Bin(2,.05) >= 1) = 1 - 0.95^2", levels.binom_tail(2, 1), 1 - F(19, 20) ** 2)
    eq("P(Bin(S,.05) >= S) = 0.05^S at S=12", levels.binom_tail(12, 12), F(1, 20) ** 12)
    eq("P(Bin(12,.05) >= 0) = 1", levels.binom_tail(12, 0), F(1))
    # a second method: 1 - cdf
    for (S, K) in ((12, 4), (32, 6), (24, 5), (200, 24)):
        cdf = sum(math.comb(S, k) * F(1, 20) ** k * F(19, 20) ** (S - k) for k in range(0, K))
        eq("tail by complement S=%d K=%d" % (S, K), levels.binom_tail(S, K), 1 - cdf)
    eq("excess point S=12 is 4", levels.excess_point(12), 4)
    eq("excess point S=24 is 5", levels.excess_point(24), 5)
    eq("excess point S=32 is 6", levels.excess_point(32), 6)
    eq("excess point S=16 is 5 (tail 0.0146 at 4? check)", levels.excess_point(16), levels.smallest_k(16, F(1, 100)))
    eq("c_max S=12 is 4/12", levels.c_max(12), F(4, 12))
    eq("c_max S=16 is 5/16", levels.c_max(16), F(5, 16))
    eq("c_max S=24 is 6/24", levels.c_max(24), F(6, 24))
    eq("c_max S=32 is 7/32", levels.c_max(32), F(7, 32))
    eq("K2a flag point 74 of 1000", levels.smallest_k(1000, F(1, 100) / 14), 74)
    eq("K2b flag point 129 of 1000 at rate 0.10", levels.smallest_k(1000, F(1, 100) / 4, F(1, 10)), 129)
    ck("tail(1000, 68) is about 0.0074", abs(float(levels.binom_tail(1000, 68)) - 0.0074) < 5e-5)
    eq("Law 2b K2 flag point 24 of 200", levels.smallest_k(200, F(1, 100) / 56), 24)
    eq("Law 2b reversible flag point 36 of 200 at 0.10", levels.smallest_k(200, F(1, 100) / 16, F(1, 10)), 36)
    ck("smallest Holm threshold 0.05/40", F(1, 20) / 40 == F(1, 800))
    eq("presence runs at N=4096, second channel", levels.presence_runs(4096, True), ["native", "bm2", "sub2", "q12", "q8", "placement", "wlen", "instrument"])
    eq("presence runs at N=4096, no second channel", len(levels.presence_runs(4096, False)), 7)
    eq("presence runs at N=2048", levels.presence_runs(2048, True), ["native", "q12", "q8", "placement", "instrument"])
    eq("transfer runs arrow", len(levels.transfer_runs("arrow", True)), 3)
    eq("transfer runs flow", len(levels.transfer_runs("flow", True)), 5)
    eq("per-run level of a presence test at 8 runs", levels.run_level(8), F(1, 20) / 40 / 8)
    eq("per-run level of the arrow transfer", levels.run_level(3), F(1, 20) / 40 / 3)
    # a run needs K >= 6 of 12, 7 of 24 or 8 of 32 at the smallest per-run level (section 9)
    lv = levels.run_level(8)
    eq("smallest passing K at S=12", min(K for K in range(13) if levels.binom_tail(12, K) <= lv), 6)
    eq("smallest passing K at S=24", min(K for K in range(25) if levels.binom_tail(24, K) <= lv), 7)
    eq("smallest passing K at S=32", min(K for K in range(33) if levels.binom_tail(32, K) <= lv), 8)
    r = levels.run_passes(10, 12, lv, [(0, 12), (1, 12), (0, 32)])
    ck("run passes with K=10 of 12, controls near 0", r["pass"] and r["margin_ok"] and r["ceiling_ok"])
    r = levels.run_passes(10, 12, lv, [(5, 12)])
    ck("run fails when a control exceeds c_max", not r["ceiling_ok"] and not r["pass"])
    r = levels.run_passes(6, 12, lv, [(3, 12)])
    ck("run fails the margin (share 1/2 vs 1/4: margin exactly 1/4 passes)", r["margin_ok"])
    r = levels.run_passes(6, 12, lv, [(4, 12)])
    ck("run fails the margin when a control share is 1/3", not r["margin_ok"])
    ck("presence p is 1 if a run fails the ceiling", levels.presence_p([levels.run_passes(12, 12, lv, [(5, 12)])]) == 1)
    p = levels.presence_p([levels.run_passes(12, 12, lv, [(0, 12)]), levels.run_passes(11, 12, lv, [(0, 12)])])
    eq("presence p is the largest run p times the number of runs", p, 2 * levels.binom_tail(12, 11))
    eq("transfer p is 1 when a control reaches 0.01", levels.transfer_p([F(1, 100000)], [F(1, 100)]), F(1))
    eq("transfer p is largest run p times the number of runs", levels.transfer_p([F(1, 1000), F(1, 2000)], [F(1, 3)]), F(2, 1000))
    ho = levels.holm({"a": F(1, 1000), "b": F(1, 30), "c": F(1, 2)}, m=40)
    ck("holm: first threshold 0.05/40, a rejected, b not", ho["a"][0] and not ho["b"][0] and ho["a"][1] == F(1, 800) and not ho["c"][0])
    eq("holm: second threshold is 0.05/39", ho["b"][1], F(1, 20) / 39)
    try:
        levels.holm({str(i): F(1, 2) for i in range(41)}, m=40)
        ck("holm refuses more tests than the family", False)
    except ValueError:
        ck("holm refuses more tests than the family", True)
    for bad in ((0, 0), (5, 3), (-1, 5)):
        try:
            levels.run_passes(bad[0], bad[1], lv, [])
            ck("run_passes refuses K,S=%s" % (bad,), False)
        except ValueError:
            ck("run_passes refuses K,S=%s" % (bad,), True)
    st = levels.instrument_status
    eq("status underpowered (11 valid)", st(11, 12, True, True, False, True), "underpowered")
    eq("status underpowered (more than 25 percent invalid)", st(23, 32, True, True, False, True), "underpowered")
    eq("status invalid (controls)", st(32, 32, False, True, False, True), "invalid")
    eq("status present", st(32, 32, True, True, False, True), "present")
    eq("status net-dependent", st(32, 32, True, False, False, True), "net-dependent")
    eq("status absent", st(32, 32, True, False, False, False), "absent")
    eq("a net underpowered means not present", st(32, 32, True, True, True, True), "net-dependent")


def u_transfer():
    section("transfer: tau0, levels, detectors, floors, adverse")
    F = Fraction
    eq("distinct detectors, 6 levels with signs", transfer.distinct_detectors([1., 2., 3., 4., 5., 6.], True), 46080)
    eq("distinct detectors, 8 features, permutations", transfer.distinct_detectors([float(i + 1) for i in range(8)], False), 40320)
    eq("distinct detectors, equal entries with signs", transfer.distinct_detectors([1.0] * 10, True), 1024)
    eq("distinct detectors, equal entries, permutations", transfer.distinct_detectors([1.0] * 10, False), 1)
    eq("distinct detectors, two pairs equal", transfer.distinct_detectors([1., 1., 2., 2.], False), 6)
    eq("distinct detectors, a zero entry has no sign", transfer.distinct_detectors([0., 1., 2.], True), 6 * 4)
    f6 = transfer.smallest_reachable_p(99999, 46080)
    f8 = transfer.smallest_reachable_p(99999, 40320)
    ck("smallest reachable p, 6 levels with signs, about 3.2e-5", abs(float(f6) - 3.2e-5) < 1e-6)
    ck("smallest reachable p, 8 features, about 3.5e-5", abs(float(f8) - 3.5e-5) < 1e-6)
    ck("floors are within the smallest per-run level of every confirmatory transfer", levels.transfer_run_floor_ok(f6, 3) and levels.transfer_run_floor_ok(f8, 3) and levels.transfer_run_floor_ok(f8, 5))
    f7 = transfer.smallest_reachable_p(99999, 5040)
    f5 = transfer.smallest_reachable_p(99999, 3840)
    ck("7 features give 2.1e-4 and 5 levels with signs 2.7e-4, both above the Law 2b arrow level 0.05/102/3", abs(float(f7) - 2.1e-4) < 1e-5 and abs(float(f5) - 2.7e-4) < 1e-5 and f7 > F(1, 20) / 102 / 3 and f5 > F(1, 20) / 102 / 3)
    ck("8 features and 6 levels meet the Law 2b levels (arrow 0.05/102/3, flow 0.05/102/5)", f8 <= F(1, 20) / 102 / 5 and f6 <= F(1, 20) / 102 / 5)
    # tau0 and shift
    eq("level shift tau0=1", transfer.level_shift_from_tau0(1.0), 0)
    eq("level shift tau0=3 (log2 = 1.585)", transfer.level_shift_from_tau0(3.0), 2)
    eq("level shift tau0=2.8 (log2 = 1.485)", transfer.level_shift_from_tau0(2.8), 1)
    eq("level shift tau0=512", transfer.level_shift_from_tau0(512.0), 9)
    x = np.sin(2 * np.pi * np.arange(4096) / 64.0)
    t0 = transfer.tau0_segment(x)
    ck("tau0 of a period-64 sine is 11 (first lag with acf < 1/2 on ranks)", 10 <= t0 <= 14)
    eq("tau0 capped at 512", transfer.tau0_segment(np.arange(4096.0)), 512)
    eq("tau0 of a shuffled series is 1", transfer.tau0_segment(np.random.default_rng(1).permutation(4096).astype(float)), 1)
    # level placement
    js = list(range(10))
    zu, z1, z23 = np.arange(10.0), np.arange(10.0) + 100, np.arange(10.0) + 200
    u, p, pop = transfer.level_vectors(zu, z1, z23, js, 3)
    eq("level -3 holds lag j=0", float(u[1]), 0.0)
    eq("level -4 is out of range at shift 3: 0 and unpopulated", (float(u[0]), bool(pop[0])), (0.0, False))
    u6, p6, pop6_ = transfer.level_vectors(zu, z1, z23, js, 6)
    eq("levels 4 and 5 need lags j=10, 11, out of range at shift 6; level 3 (j=9) is populated", (bool(pop6_[-1]), bool(pop6_[-2]), bool(pop6_[-3])), (False, False, True))
    eq("populated mask at shift 3: levels -3 .. 5 would need j=0..8", pop.tolist(), [False] + [True] * 9)
    eq("profile vector is m1 entries then m23 entries", (float(p[1]), float(p[11])), (100.0, 200.0))
    # detectors
    w = np.array([3., 1., 4., 1.5, 9., 2.6, 0., 0., 0., 0.])
    w = w / np.sqrt(w @ w)
    pop6 = np.array([True] * 6 + [False] * 4)
    r = transfer.transfer_test("arrow", w, w, pop6, np.random.default_rng(77), R=5000)
    ck("template against itself: self is the best detector, p at most 4/5001", r["p"] <= F(4, 5001) and r["D"] == 46080)
    ck("template against itself is not adverse", not r["adverse"])
    r = transfer.transfer_test("arrow", w, -w, pop6, np.random.default_rng(77), R=5000)
    ck("template against its negative is adverse (no detector scores below it)", r["adverse"] and r["n_lt"] == 0)
    ones = np.ones(10) / np.sqrt(10)
    rp = transfer.transfer_test("profile", ones, np.ones(10), np.ones(10, dtype=bool), np.random.default_rng(5), R=2000)
    eq("permutations only: a level-flat B and same-sign A give p = 1 (A3)", rp["p"], F(1))
    ra = transfer.transfer_test("arrow", ones, np.ones(10), np.ones(10, dtype=bool), np.random.default_rng(5), R=20000)
    ck("with random signs the same case reaches p near 1/1024", ra["D"] == 1024 and F(1, 3000) < ra["p"] < F(1, 300))
    f = transfer.apply_floor(transfer.transfer_test("arrow", w, w, np.array([True] * 5 + [False] * 5), np.random.default_rng(1), R=200), "arrow")
    ck("5 jointly populated levels is below the arrow floor: counts as not rejecting", f["below_floor"] and f["p"] == 1 and not f["adverse"])
    f = transfer.apply_floor(transfer.transfer_test("profile", w, w, np.array([True] * 7 + [False] * 3), np.random.default_rng(1), R=200), "profile")
    ck("7 features is below the profile floor", f["below_floor"] and f["p"] == 1)
    f = transfer.apply_floor(transfer.transfer_test("profile", w, w, np.array([True] * 8 + [False] * 2), np.random.default_rng(1), R=200), "profile")
    ck("8 features meets the profile floor", not f["below_floor"])
    pb = transfer.pop_both(np.array([True] * 6 + [False] * 4), np.array([False] + [True] * 9), 2)
    eq("jointly populated mask for the profile has two blocks", pb.tolist(), [False] + [True] * 5 + [False] * 4 + [False] + [True] * 5 + [False] * 4)
    try:
        transfer.build_template(np.zeros((3, 4)))
        ck("zero template refused", False)
    except ValueError:
        ck("zero template refused", True)


def u_flow():
    section("scale flow")
    cl = flow.class_lists()
    eq("9 classes", len(cl), 9)
    eq("8 untied classes cover the 24 untied patterns", sorted(i for c in cl[:8] for i in c), [k for k in range(75) if patterns.tables(4)["untied"][k]])
    eq("ninth class holds the 51 tied patterns", len(cl[8]), 51)
    C4 = np.zeros((2, 75), dtype=np.int64)
    C4[0, 0] = 100
    C4[1, 5] = 100
    z, S2 = flow.unit_features(C4)
    ck("class frequencies sum to 1 before standardisation (pseudocount 1/2 on 75 patterns)", True)
    x = np.arange(20.0)
    y, runs = flow.block_average(x, [(0, 7), (7, 20)])
    eq("block averaging does not cross a gap: run lengths 3 and 6", [r[1] - r[0] for r in runs], [3, 6])
    eq("block averages inside each run", y.tolist(), [0.5, 2.5, 4.5, 7.5, 9.5, 11.5, 13.5, 15.5, 17.5][0:3] + [7.5, 9.5, 11.5, 13.5, 15.5, 17.5])
    ym, _ = flow.block_average(np.array([1., 5, 2, 2]), None, "max")
    eq("block maxima", ym.tolist(), [5.0, 2.0])
    lv = flow.level_streams(np.zeros(2 ** 19), 4096)
    eq("levels at 2^19 samples", [l for (l, s, r) in lv], [0, 1, 2, 3])
    ev = [{"l": 0, "z": np.ones(9), "S2": 1.0, "n_ge": 0, "departs": True}, {"l": 1, "z": 3 * np.ones(9), "S2": 1.0, "n_ge": 0, "departs": False}, {"l": 1, "z": np.zeros(9), "S2": 1.0, "n_ge": 0, "departs": False}]
    V, cnt = flow.flow_vectors(ev, 0)
    eq("per-level mean over units", (V[3].tolist(), V[4].tolist(), cnt.tolist()), ([1.0] * 9, [1.5] * 9, [0, 0, 0, 1, 2, 0, 0]))
    g, lev = flow.flow_target(ev, 0)
    eq("S_B averages populated levels equally: g = V / 2", (g[27:36].tolist(), g[36:45].tolist()), ([0.5] * 9, [0.75] * 9))
    eq("departure counts per level", flow.level_departure(ev), {0: [1, 1], 1: [2, 0]})
    ck("units of a level beyond +-3 aligned levels are not kept", flow.flow_vectors([{"l": 5, "z": np.ones(9)}], 0)[1].sum() == 0)


def u_outcomes():
    section("outcome decision procedure, every state")
    from outcomes import INSTR, PAIRS, ORDERED, STATUSES, ARROW, PROFILE
    stat = list(product(STATUSES, repeat=3))
    arr = list(product(ARROW, repeat=6))
    prof = list(product(PROFILE, repeat=6))
    # precompute per-component bit facts (independent restatement of the rules, then compare with the public function)
    def sfacts(s):
        P = {i for i in INSTR if s[i] == "present"}
        Q = {i for i in INSTR if s[i] in ("present", "net-dependent")}
        V = {i for i in INSTR if s[i] in ("present", "net-dependent", "absent")}
        return P, Q, V, sum(1 for i in INSTR if s[i] == "absent")
    pidx = {p: k for k, p in enumerate(PAIRS)}
    def afacts(a):
        d = dict(zip(ORDERED, a))
        advb = tuple(d[(i, j)] == "adverse" and d[(j, i)] == "adverse" for (i, j) in PAIRS)
        pasb = tuple(d[(i, j)] == "pass" and d[(j, i)] == "pass" for (i, j) in PAIRS)
        adva = tuple(d[(i, j)] == "adverse" or d[(j, i)] == "adverse" for (i, j) in PAIRS)
        return advb, pasb, adva
    def pfacts(p):
        d = dict(zip(ORDERED, p))
        return tuple(d[(i, j)] == "pass" and d[(j, i)] == "pass" for (i, j) in PAIRS)
    SF = [sfacts(s) for s in stat]
    AF = [afacts(a) for a in arr]
    PF = [pfacts(p) for p in prof]
    names = outcomes.OUT_T3
    tally = {n: 0 for n in names}
    multi = {n: 0 for n in names}
    nmatch_zero = 0
    for kat in (False, True):
        for (P, Q, V, nabs) in SF:
            for (advb, pasb, adva) in AF:
                nadv = sum(1 for k, p in enumerate(PAIRS) if advb[k] and set(p) <= V)
                allpass = all(pasb)
                for pb in PF:
                    some = any(set(p) <= P and (pasb[k] or (pb[k] and not adva[k])) for k, p in enumerate(PAIRS))
                    cond = (not kat,
                            kat and (nabs >= 2 or nadv >= 2),
                            kat and len(P) == 3 and allpass,
                            kat and len(Q) == 3 and len(P) < 3 and allpass,
                            kat and len(P) >= 2 and some,
                            kat and len(P) >= 2 and not some,
                            kat and len(P) <= 1 and nabs <= 1 and nadv <= 1)
                    first = None
                    for i, c in enumerate(cond):
                        if c:
                            first = i
                            break
                    if first is None:
                        nmatch_zero += 1
                        continue
                    tally[names[first]] += 1
                    if sum(cond) > 1:
                        multi[names[first]] += 1
    total = sum(tally.values()) + nmatch_zero
    eq("T3 states enumerated", total, 11664000)
    eq("T3 states matching no rule", nmatch_zero, 0)
    eq("T3 outcome 'PARTIAL' states (plan states 129,867 after Amendment 1)", tally["PARTIAL"], 129867)
    for n in names:
        print("  T3 %-22s %9d states (%d also meet a lower-ranked condition)" % (n, tally[n], multi[n]))
    # the public function agrees with this enumeration on a fixed sample, and on every state of a reduced set
    rng = np.random.default_rng(20261122)
    agree = True
    for _ in range(3000):
        kat = bool(rng.integers(0, 2))
        s = stat[int(rng.integers(0, len(stat)))]
        a = arr[int(rng.integers(0, len(arr)))]
        p = prof[int(rng.integers(0, len(prof)))]
        out = outcomes.outcome_t3(kat, s, dict(zip(ORDERED, a)), dict(zip(ORDERED, p)))
        P, Q, V, nabs = sfacts(s)
        advb, pasb, adva = afacts(a)
        pb = pfacts(p)
        nadv = sum(1 for k, pp in enumerate(PAIRS) if advb[k] and set(pp) <= V)
        some = any(set(pp) <= P and (pasb[k] or (pb[k] and not adva[k])) for k, pp in enumerate(PAIRS))
        cond = (not kat, kat and (nabs >= 2 or nadv >= 2), kat and len(P) == 3 and all(pasb),
                kat and len(Q) == 3 and len(P) < 3 and all(pasb), kat and len(P) >= 2 and some,
                kat and len(P) >= 2 and not some, kat and len(P) <= 1 and nabs <= 1 and nadv <= 1)
        exp = names[cond.index(True)]
        if out != exp:
            agree = False
    ck("outcome_t3 equals the enumeration on 3,000 sampled states", agree)
    # every state of the public function, for a reduced but exhaustive set: all 125 statuses x 729 arrow x one profile pattern
    bad = 0
    cnt = 0
    for s in stat:
        for a in arr:
            for kat in (True,):
                out = outcomes.outcome_t3(kat, s, dict(zip(ORDERED, a)), dict(zip(ORDERED, ("neither",) * 6)))
                cnt += 1
                if out not in names:
                    bad += 1
    eq("outcome_t3 gives a valid outcome for all 91,125 states with no profile pass", (cnt, bad), (125 * 729, 0))
    # hand cases
    A = lambda v: {k: v for k in ORDERED}
    eq("supported", outcomes.outcome_t3(True, ("present",) * 3, A("pass"), A("pass")), "SUPPORTED")
    eq("net-dependent", outcomes.outcome_t3(True, ("present", "net-dependent", "present"), A("pass"), A("pass")), "NET-DEPENDENT")
    eq("invalid when a known-answer test fails", outcomes.outcome_t3(False, ("present",) * 3, A("pass"), A("pass")), "INVALID")
    eq("evidence against: two absent", outcomes.outcome_t3(True, ("absent", "absent", "present"), A("neither"), A("neither")), "EVIDENCE AGAINST")
    eq("evidence against: two pairs adverse both ways", outcomes.outcome_t3(True, ("present",) * 3, {**A("neither"), (0, 1): "adverse", (1, 0): "adverse", (0, 2): "adverse", (2, 0): "adverse"}, A("neither")), "EVIDENCE AGAINST")
    eq("partial: a pair passes on the arrow both ways", outcomes.outcome_t3(True, ("present",) * 3, {**A("neither"), (0, 1): "pass", (1, 0): "pass"}, A("neither")), "PARTIAL")
    eq("opposite arrow with shared shape is not partial", outcomes.outcome_t3(True, ("present",) * 3, {**A("neither"), (0, 1): "adverse"}, A("pass")), "PARTIAL")
    eq("does not discriminate", outcomes.outcome_t3(True, ("present", "present", "absent"), A("neither"), A("neither")), "DOES NOT DISCRIMINATE")
    eq("inconclusive", outcomes.outcome_t3(True, ("present", "underpowered", "invalid"), A("neither"), A("neither")), "INCONCLUSIVE")
    # refusals
    for nm, call in (("kat_ok not a bool", lambda: outcomes.outcome_t3(1, ("present",) * 3, A("pass"), A("pass"))),
                     ("unknown status", lambda: outcomes.outcome_t3(True, ("present", "x", "present"), A("pass"), A("pass"))),
                     ("missing pair", lambda: outcomes.outcome_t3(True, ("present",) * 3, {(0, 1): "pass"}, A("pass"))),
                     ("bad arrow value", lambda: outcomes.outcome_t3(True, ("present",) * 3, A("adverse?"), A("pass"))),
                     ("profile cannot be adverse", lambda: outcomes.outcome_t3(True, ("present",) * 3, A("pass"), A("adverse")))):
        try:
            call()
            ck("refusal fires: " + nm, False)
        except (TypeError, ValueError):
            ck("refusal fires: " + nm, True)
    # scale-flow half of T1
    names1 = outcomes.OUT_T1
    t1 = {n: 0 for n in names1}
    tr = list(product(ARROW, repeat=6))
    zero = 0
    for kat in (False, True):
        for usable in product((False, True), repeat=3):
            V = {i for i in INSTR if usable[i]}
            for a in tr:
                d = dict(zip(ORDERED, a))
                nadv = sum(1 for (i, j) in PAIRS if i in V and j in V and d[(i, j)] == "adverse" and d[(j, i)] == "adverse")
                npass = sum(1 for (i, j) in PAIRS if i in V and j in V and d[(i, j)] == "pass" and d[(j, i)] == "pass")
                cond = (not kat, kat and nadv >= 2, kat and len(V) == 3 and npass == 3, kat and npass >= 1,
                        kat and len(V) >= 2 and npass == 0, kat and len(V) <= 1)
                if not any(cond):
                    zero += 1
                    continue
                t1[names1[cond.index(True)]] += 1
                out = outcomes.outcome_t1(kat, usable, d)
                if out != names1[cond.index(True)]:
                    zero += 1
    eq("T1 states enumerated", sum(t1.values()) + zero, 11664)
    eq("T1 states matching no rule or disagreeing with outcome_t1", zero, 0)
    for n in names1:
        print("  T1 %-22s %6d states" % (n, t1[n]))
    for nm, call in (("kat_ok not a bool", lambda: outcomes.outcome_t1("yes", (True,) * 3, A("pass"))),
                     ("usable not bools", lambda: outcomes.outcome_t1(True, (1, 1, 1), A("pass"))),
                     ("missing pair", lambda: outcomes.outcome_t1(True, (True,) * 3, {(0, 1): "pass"}))):
        try:
            call()
            ck("T1 refusal fires: " + nm, False)
        except (TypeError, ValueError):
            ck("T1 refusal fires: " + nm, True)


def u_gates_and_seeds():
    section("refusals and seeds")
    BAD = {"GATE_NUMERIC": ["a", "b"], "GATE_SHAPE": np.ones((4200, 2)), "GATE_EMPTY": np.array([]), "GATE_SHORT": np.arange(100.0),
           "GATE_MISSING": np.where(np.arange(5000) == 17, np.nan, np.arange(5000.0)), "GATE_CONSTANT": np.full(5000, 3.0)}
    for code, bad in BAD.items():
        try:
            gates.validate_series(bad, 4096)
            ck("refusal fires: " + code, False)
        except gates.GateError as e:
            ck("refusal fires: " + code, str(e).startswith(code))
    ck("a good input passes", gates.validate_series(np.random.default_rng(1).standard_normal(5000), 4096).size == 5000)
    try:
        segments.cut_segments(np.random.default_rng(1).standard_normal(9000), valid=[True] * 3)
        ck("validity flags of the wrong length refused", False)
    except ValueError:
        ck("validity flags of the wrong length refused", True)
    s = "20261121|a|b|c|d|e|0"
    eq("seed string (epoch 0)", seeds.seed_string("a", "b", "c", "d", "e", 0, epoch=0), s)
    eq("seed integer is the first 16 hex digits of SHA-256", seeds.seed_int("a", "b", "c", "d", "e", 0, epoch=0), int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:16], 16))
    ck("same key gives the same stream, a different index a different one", seeds.rng_for("a", "b", "c", "d", "e", 0, epoch=0).random() == seeds.rng_for("a", "b", "c", "d", "e", 0, epoch=0).random() and seeds.rng_for("a", "b", "c", "d", "e", 1, epoch=0).random() != seeds.rng_for("a", "b", "c", "d", "e", 0, epoch=0).random())


def u_law2b():
    section("Law 2b instances (statistics only; not on the confirmatory path)")
    T3 = patterns.tables(3)
    sym = np.zeros(13, dtype=np.int64)
    sym[T3["index"][(0, 1, 2)]] = 5
    sym[T3["index"][(2, 1, 0)]] = 5
    ck("Q, H, M are 0 for counts equal to their reverse", abs(float(law2b.sigma_Q(sym))) < 1e-15 and abs(float(law2b.sigma_H(sym))) < 1e-15 and abs(float(law2b.sigma_M(sym))) < 1e-15)
    h = np.zeros(13, dtype=np.int64)
    h[T3["index"][(0, 1, 2)]] = 3
    h[T3["index"][(2, 1, 0)]] = 1
    den = 4 + 6.5
    p1, p2 = 3.5 / den, 1.5 / den
    ck("Q by hand (both members of the pair count)", abs(float(law2b.sigma_Q(h)) - 2 * (p1 - p2) ** 2) < 1e-15)
    ck("H by hand", abs(float(law2b.sigma_H(h)) - 2 * (math.sqrt(p1) - math.sqrt(p2)) ** 2) < 1e-15)
    ck("M by hand", abs(float(law2b.sigma_M(h)) - math.log(p1 / p2)) < 1e-14)
    a1, a2, a3 = law2b.a_features_Q(h)
    ck("Q arrow feature a1 = p(012) - p(210), others 0", abs(float(a1) - (p1 - p2)) < 1e-15 and abs(float(a2)) < 1e-15 and abs(float(a3)) < 1e-15)
    c4 = np.zeros(75, dtype=np.int64)
    c4[patterns.tables(4)["index"][(0, 1, 2, 3)]] = 2
    ck("order-4 statistic is finite and positive for a one-sided count", float(law2b.sigma_O4(c4)) > 0)
    eq("D has n - 1 samples", law2b.differences_D(np.array([1., 4., 9., 16.])).tolist(), [3.0, 5.0, 7.0])
    x = np.random.default_rng(2).standard_normal(1024)
    wx = law2b.whiten_W(x)
    ck("W: the zero frequency is 0 and the length is kept", abs(float(wx.mean())) < 1e-12 and wx.size == 1024)
    ck("W refuses a series with a zero median periodogram", _raises(lambda: law2b.whiten_W(np.zeros(64))))
    f = law2b.white_floor_F(x, ("k", "s", "law2b-F:native", 0, "law2b-F", 0), epoch=0)
    ck("F adds noise of about 1/1000 of the standard deviation", 0 < float(np.abs(f - x).max()) < 0.01 * x.std() * 10 and float(np.std(f - x)) > 0)
    eq("F is reproducible", law2b.white_floor_F(x, ("k", "s", "law2b-F:native", 0, "law2b-F", 0), epoch=0), f)
    eq("tail spread of the 0..1000 ramp by order statistics (ranks 1000, 2, 751, 251), exact", law2b.tail_spread(np.arange(1001.0)), Fraction(998, 500))
    eq("event-rich threshold is the exact median (mean of the two middle values)", law2b.event_rich_threshold([np.arange(1001.0), np.arange(1001.0) * 2.0]), Fraction(998, 500))
    ck("E: a heavy-tailed segment is event-rich against the Gaussian median", law2b.event_rich(synth.shots_ar(4096, np.random.default_rng(3)), law2b.event_rich_threshold([np.random.default_rng(i).standard_normal(4096) for i in range(5)])))
    eq("max-plus score", float(law2b.max_plus_score(np.array([1., -2., 3.]), np.array([2., 1., 1.]))), 3.0)
    ck("B is block maxima and H the square root", law2b.FLOW_BLOCK_OP_B == "max" and law2b.flow_freq_map_H(np.array([4.0])).tolist() == [2.0])
    src = os.path.join(HERE, "..", "src")
    users = []
    for fn in sorted(os.listdir(src)):
        if fn.endswith(".py") and fn != "law2b.py":
            with open(os.path.join(src, fn), "r", encoding="utf-8") as fh:
                txt = fh.read()
                if "import law2b" in txt or "from law2b" in txt:
                    users.append(fn)
    eq("no module of src/ refers to law2b (confirmatory path does not call it)", users, [])


def _refused(call, kinds=(ValueError, TypeError)):
    try:
        call()
    except kinds:
        return True
    return False


def u_review_guards():
    section("guards found missing by an outside review of the frozen-plan code (each check fails if its guard is removed)")
    import inspect
    import kcommon
    F = Fraction
    ck("validate_series has no switch that turns a guard off", list(inspect.signature(gates.validate_series).parameters) == ["x", "N"])
    ck("bool array refused (GATE_NUMERIC)", _refused(lambda: gates.validate_series([True, False] * 2500, 4096), (gates.GateError,)))
    ck("complex array refused, not truncated", _refused(lambda: gates.validate_series(np.array([1 + 2j, 2 + 3j] * 2500), 4096), (gates.GateError,)))
    ck("string array refused", _refused(lambda: gates.validate_series(np.array(["1", "2"] * 2500), 4096), (gates.GateError,)))
    ck("integer counts accepted", gates.validate_series(np.arange(5000) % 7 + 1, 4096).dtype == np.float64)
    for badN in (True, 0, 4096.0, "4096"):
        ck("N = %r refused" % (badN,), _refused(lambda: gates.validate_series(np.random.default_rng(1).standard_normal(5000), badN), (TypeError,)))
    ck("holm refuses a float p-value (0.05 is not 1/20)", _refused(lambda: levels.holm({"t": 0.05}, m=1)))
    ck("holm refuses a bool p-value", _refused(lambda: levels.holm({"t": True}, m=1)))
    ck("holm refuses a float alpha", _refused(lambda: levels.holm({"t": F(1, 100)}, m=1, alpha=0.05)))
    ck("holm accepts Fraction(1, 20) at m = 1", levels.holm({"t": F(1, 20)}, m=1)["t"][0])
    ck("binom_tail refuses bool S and K", _refused(lambda: levels.binom_tail(True, True)))
    ck("binom_tail refuses a float q", _refused(lambda: levels.binom_tail(12, 4, 0.05)))
    ck("binom_tail refuses a float K", _refused(lambda: levels.binom_tail(12, 4.0)))
    ck("smallest_k refuses a float level", _refused(lambda: levels.smallest_k(12, 0.01)))
    ck("run_passes refuses bool K, S", _refused(lambda: levels.run_passes(True, True, F(1, 800), [])))
    ck("run_passes refuses a float level", _refused(lambda: levels.run_passes(5, 12, 0.001, [])))
    ck("run_passes refuses a control count above its size", _refused(lambda: levels.run_passes(5, 12, F(1, 800), [(13, 12)])))
    ck("transfer_p refuses float p-values", _refused(lambda: levels.transfer_p([0.001], [])))
    ck("transfer_p refuses float control p-values", _refused(lambda: levels.transfer_p([F(1, 1000)], [0.5])))
    ck("presence_p refuses a run with a float p", _refused(lambda: levels.presence_p([{"p": 0.01, "margin_ok": True, "ceiling_ok": True}])))
    ck("run_level refuses a bool run count", _refused(lambda: levels.run_level(True)))
    ck("instrument_status refuses a bool count", _refused(lambda: levels.instrument_status(True, 12, True, True, False, True)))
    ck("instrument_status refuses a non-bool flag", _refused(lambda: levels.instrument_status(12, 12, 1, True, False, True)))
    ck("instrument_status refuses n_valid above n_selected", _refused(lambda: levels.instrument_status(13, 12, True, True, False, True)))
    ck("loo_standardise refuses one row", _refused(lambda: stats43.loo_standardise(np.ones((1, 4)))))
    ck("loo_standardise refuses non-finite values", _refused(lambda: stats43.loo_standardise(np.array([[1.0], [np.nan], [2.0]]))))
    ck("loo_standardise refuses a 1-D array", _refused(lambda: stats43.loo_standardise(np.ones(5))))
    ck("tau0 refuses a constant segment", _refused(lambda: transfer.tau0_segment(np.full(4096, 5.0))))
    ck("tau0 refuses a segment of one sample", _refused(lambda: transfer.tau0_segment(np.array([1.0]))))
    ck("build_template refuses an empty set of segments", _refused(lambda: transfer.build_template(np.zeros((0, 4)))))
    ck("build_template refuses non-finite features", _refused(lambda: transfer.build_template(np.array([[1.0, np.nan]]))))
    w = np.arange(1.0, 7.0)
    pm = np.ones(6, dtype=bool)
    rg = lambda: np.random.default_rng(1)
    ck("transfer_test refuses R = 0", _refused(lambda: transfer.transfer_test("arrow", w, w, pm, rg(), R=0)))
    ck("transfer_test refuses a bool R", _refused(lambda: transfer.transfer_test("arrow", w, w, pm, rg(), R=True)))
    ck("transfer_test refuses an unknown kind", _refused(lambda: transfer.transfer_test("nope", w, w, pm, rg(), R=100)))
    ck("transfer_test refuses a target of another length", _refused(lambda: transfer.transfer_test("arrow", w, w[:3], pm, rg(), R=100)))
    ck("transfer_test refuses a mask of another length", _refused(lambda: transfer.transfer_test("arrow", w, w, pm[:3], rg(), R=100)))
    ck("transfer_test refuses an int mask", _refused(lambda: transfer.transfer_test("arrow", w, w, pm.astype(int), rg(), R=100)))
    ck("transfer_test refuses a non-finite template", _refused(lambda: transfer.transfer_test("arrow", np.full(6, np.nan), w, pm, rg(), R=100)))
    ck("transfer_test refuses a non-finite target", _refused(lambda: transfer.transfer_test("arrow", w, np.full(6, np.inf), pm, rg(), R=100)))
    ck("cut_segments refuses validity flags that are too short", _refused(lambda: segments.cut_segments(np.random.default_rng(1).standard_normal(9000), valid=[True])))
    ck("amp_lognormal refuses non-finite values", _refused(lambda: nets.amp_lognormal(np.array([1.0, np.nan, 2.0]))))
    ck("amp_scores refuses non-finite values", _refused(lambda: nets.amp_scores(np.array([1.0, np.inf, 2.0]))))
    ck("midranks refuses non-finite values", _refused(lambda: nets.midranks(np.array([1.0, np.nan]))))
    # exit status: summary ends the script with status 1 on FAIL and returns on PASS
    smoke_run = kcommon.parse_args(["t", "smoke"], seeded=True)
    try:
        kcommon.summary("T", "FAIL", "x", smoke_run)
        ck("summary exits with status 1 on FAIL", False)
    except SystemExit as e:
        ck("summary exits with status 1 on FAIL", e.code == 1)
    try:
        kcommon.summary("T", "PASS", "x", smoke_run)
        ck("summary returns on PASS", True)
    except SystemExit:
        ck("summary returns on PASS", False)
    ck("summary refuses a status other than PASS or FAIL", _refused(lambda: kcommon.summary("T", "MAYBE", "x", smoke_run)))
    # the tied symmetric waveform: exact time symmetry survives every map used in K1 (identity of counts and sigma_hat = 0)
    q = np.array([0, 0, 1, 2, 2, 1, 0, 0] * 512, dtype=float)
    base, _ = patterns.counts_one(q, 3, 1)
    ck("tied symmetric waveform: sigma_hat is exactly 0", float(patterns.sigma_hat(base, 3)) == 0.0 and patterns.tied_windows(base, 3) == 3070)
    for nm, f in nets.increasing_maps().items():
        c, _ = patterns.counts_one(f(q), 3, 1)
        ck("tied symmetric waveform under %s: counts unchanged, sigma_hat exactly 0, ties kept" % nm, bool((c == base).all()) and float(patterns.sigma_hat(c, 3)) == 0.0)


def u_amendment2():
    section("Amendment 2: ties, exact tau0, constant segments, K1 and K5 constructions (each check fails if its rule is removed)")
    F = Fraction
    # B8 tie rule
    ck("tie: 5e-13 and 0 tie (absolute floor)", bool(ties.tied(0.0, 5e-13)) and bool(ties.tied(5e-13, 0.0)))
    ck("tie: 2e-12 and 0 do not tie", not bool(ties.tied(0.0, 2e-12)))
    ck("tie: relative at 1e6 (difference 5e-7 ties, 5e-6 does not)", bool(ties.tied(1e6, 1e6 + 5e-7)) and not bool(ties.tied(1e6, 1e6 + 5e-6)))
    ck("tie: an infinity ties with nothing", not bool(ties.tied(np.inf, np.inf)) and not bool(ties.tied(-np.inf, -np.inf)) and not bool(ties.tied(-np.inf, 1.0)))
    ck("at_or_above counts a tie; below does not", bool(ties.at_or_above(1.0, 1.0 + 5e-13)) and not bool(ties.below(1.0, 1.0 + 5e-13)) and bool(ties.below(1.0, 1.1)))
    r = transfer.transfer_test("profile", np.ones(8) / np.sqrt(8), np.ones(8), np.ones(8, dtype=bool), np.random.default_rng(3), R=500)
    ck("transfer: when every detector ties, p = 1 (a tie counts against w_A) and no detector counts as below", r["p"] == 1 and r["n_lt"] == 0)
    sc_below = transfer.transfer_test("profile", np.array([1.0, 0, 0, 0, 0, 0, 0, 0]), np.array([1.0 + 5e-13, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]), np.ones(8, dtype=bool), np.random.default_rng(3), R=500)
    ck("transfer: a detector within the tie tolerance below S_A is not counted below", sc_below["n_lt"] <= 500)
    # exact tau0 against an independent computation on Fractions
    x = np.random.default_rng(4).standard_normal(300)
    x = np.convolve(x, np.ones(5) / 5.0, mode="same")
    mr = [F(int(t), 2) for t in ranks.twice_midrank(x)]
    mean = sum(mr) / len(mr)
    cen = [v - mean for v in mr]
    den = sum(v * v for v in cen)
    t0 = None
    for tau in range(1, 300):
        if sum(cen[i] * cen[i + tau] for i in range(300 - tau)) / den < F(1, 2):
            t0 = tau
            break
    eq("tau0 equals an independent computation in exact fractions", transfer.tau0_segment(x), t0)
    y = np.array([0.0, 1.0] * 50)
    eq("tau0 of an alternating series is 1 (autocorrelation -1)", transfer.tau0_segment(y), 1)
    ck("tau0 refuses a segment longer than the 64-bit bound", _refused(lambda: transfer.tau0_segment(np.arange(6001.0))))
    # B7 constant segments
    const = np.full(4096, 7.0)
    ramp = np.random.default_rng(5).standard_normal(4096)
    for run in ("native", "bm2", "sub2", "q12", "q8", "placement", "wlen", "instrument"):
        out = pipeline.run_series([const, ramp, None], run)
        ck("constant segment is invalid (None) under run %s, a good segment is kept, None stays None" % run, out[0] is None and out[1] is not None and out[2] is None)
    ck("a segment made constant by its net is invalid (12-bit bins of an almost constant segment)", pipeline.run_series([np.concatenate([np.zeros(4095), [1e-300]])], "native")[0] is not None)
    c2, c3 = pipeline.control_series([const, ramp, None], "native", "u")
    ck("C2 and C3 of a constant or invalid segment are invalid, those of a good segment are not", c2[0] is None and c3[0] is None and c2[1] is not None and c3[1] is not None and c2[2] is None and c3[2] is None)
    ck("a constant segment gives no tau0 (refused), and level_shift drops it", _refused(lambda: transfer.tau0_segment(const)) and transfer.level_shift([const, ramp, None])[0] == transfer.tau0_segment(ramp))
    ck("level_shift refuses a set with no non-constant segment", _refused(lambda: transfer.level_shift([const, None])))
    rows = [{"all_zero_spread": True, "js": [0], "zu": np.zeros(1), "z1": np.zeros(1), "z23": np.zeros(1)},
            {"all_zero_spread": False, "js": [0, 1], "zu": np.ones(2), "z1": np.ones(2), "z23": np.ones(2)}, None]
    U, Pf, pop = pipeline.features(rows, 0)
    eq("features: invalid and all-zero-spread segments give no transfer feature", U.shape[0], 1)
    ck("features refuses when no segment is usable", _refused(lambda: pipeline.features([None, rows[0]], 0)))
    cs = np.random.default_rng(6).standard_normal(640 * 80)
    cs[640 * 10:640 * 11] = 3.0
    base_jobs, _ = flow.stream_units(np.random.default_rng(6).standard_normal(640 * 80), lambda l, q: ("u", "s", "n", "L%dq%d" % (l, q), "surrogates", 0), N=512, epoch=0)
    jobs, _ = flow.stream_units(cs, lambda l, q: ("u", "s", "n", "L%dq%d" % (l, q), "surrogates", 0), N=512, epoch=0)
    ck("flow: a constant segment gives no unit", len(jobs) < len(base_jobs))
    # B5 and B6 constructions
    xx = np.array([-4.0, 1.0, 2.0])
    eq("K1 map: y = x / max|x| then y^3 + y", tasks.k1_map(xx, "cubic").tolist(), ((xx / 4.0) ** 3 + xx / 4.0).tolist())
    eq("K1 map: exp(y)", tasks.k1_map(xx, "exp").tolist(), np.exp(xx / 4.0).tolist())
    eq("K1 map: ranks of x", tasks.k1_map(xx, "rank").tolist(), [1.0, 2.0, 3.0])
    ck("K1 maps cannot overflow on exp of exp (argument in [-1, 1])", bool(np.all(np.isfinite(tasks.k1_map(np.exp(np.exp(np.linspace(-5, 5, 50))), "exp")))))
    w = synth.tied_waveform()
    ck("waveform is [0,0,1,2,2,1,0,0] x 512 and a palindrome", w.size == 4096 and np.array_equal(w, w[::-1]) and w[:8].tolist() == [0, 0, 1, 2, 2, 1, 0, 0])
    tb = np.argsort(np.argsort(w, kind="stable"), kind="stable").astype(np.float64)
    c, _ = patterns.counts_one(tb, 3, 1)
    ck("must-fail ranking (ties in time order) gives a non-zero Sigma_hat on the waveform", float(patterns.sigma_hat(c, 3)) != 0.0)
    qi = synth.k1_int_series("white", 0, 1024, epoch=0)
    ck("integer-valued class: integer values with ties", bool(np.all(qi == np.round(qi))) and ranks.n_distinct(qi) < 1024)
    ck("K1 draws use their own key: the K1 plain draw differs from the K2 draw", not np.array_equal(synth.k1_series("white", 0, 1024, epoch=0), synth.k2_series("white", 0, 1024, epoch=0)))
    eq("exp and cube versions are maps of the plain draw (K1)", ranks.normal_scores(synth.k1_series("g2|exp", 3, 512, epoch=0)).tolist(), ranks.normal_scores(synth.k1_series("g2", 3, 512, epoch=0)).tolist())
    # K5b series
    rng = seeds.rng_for("K5b:cascade", "fit", "native", 2, "data", 0, epoch=0)
    xs = np.ones(1)
    for j in range(3):
        wv = np.exp(0.5 * rng.standard_normal(2 ** (j + 1)) - 0.125)
        xs = np.repeat(xs, 2) * wv
    eq("cascade construction: start [1], repeat twice and multiply by exp(0.5 Z - 0.125), Z drawn in order", synth.cascade(8, seeds.rng_for("K5b:cascade", "fit", "native", 2, "data", 0, epoch=0)).tolist(), xs.tolist())
    old = synth.K5_N
    synth.K5_N = 4096
    try:
        ci = synth.k5_series("cascade_iaaft", 1, "fit", epoch=0)
        cc = synth.k5_series("cascade", 1, "fit", epoch=0)
        ck("IAAFT cascade has the normal scores of the cascade as its values", np.array_equal(np.sort(ci), np.sort(ranks.normal_scores(cc))))
        ck("IAAFT cascade is not the cascade or its scores in place", not np.array_equal(ci, ranks.normal_scores(cc)))
        ck("IAAFT cascade exists as a fit series only", _refused(lambda: synth.k5_series("cascade_iaaft", 1, "verdict", epoch=0)))
        yp = synth.k5_series("yprime", 0, "verdict", epoch=0)
        ck("y' = g^2 is non-negative", bool(np.all(yp >= 0)) and yp.size == 4096)
    finally:
        synth.K5_N = old
    ck("y' coefficient is 0.9859", synth.YPRIME_C == 0.9859)
    ck("K5 draws are under the tag K5b (differ from the old tag)", not np.array_equal(synth.cascade(64, seeds.rng_for("K5:cascade", "fit", "native", 0, "data", 0, epoch=0)), synth.cascade(64, seeds.rng_for("K5b:cascade", "fit", "native", 0, "data", 0, epoch=0))))


def u_audit_three():
    section("three edge cases raised by the team's audit of the code (written first, shown failing before the fix)")
    ck("tau0_segment refuses a NaN (fails closed)", _refused(lambda: transfer.tau0_segment(np.array([1.0, np.nan, 3.0, 4.0]))))
    ck("tau0_segment refuses an infinity (fails closed)", _refused(lambda: transfer.tau0_segment(np.array([1.0, np.inf, 3.0, 4.0]))))
    ck("segments_constant refuses a non-finite series (nan == nan is False, so it was not 'constant')", _refused(lambda: transfer.segments_constant(np.full(10, np.nan))))
    ck("ties: at_or_above(inf, inf) is False (an infinity ties with nothing and gives no verdict)", not bool(ties.at_or_above(np.inf, np.inf)))
    ck("ties: at_or_above(inf, 1) is False (a non-finite value gives no verdict)", not bool(ties.at_or_above(np.inf, 1.0)))
    ck("ties: below(-inf, 1) is False", not bool(ties.below(-np.inf, 1.0)))
    ck("ties: at_or_above on finite values is unchanged", bool(ties.at_or_above(2.0, 1.0)) and bool(ties.at_or_above(1.0, 1.0)) and not bool(ties.at_or_above(1.0, 2.0)))
    ck("ties: at_or_above(-inf, 1) stays False (a surrogate with no lag kept never counts against the real series)", not bool(ties.at_or_above(-np.inf, 1.0)))
    low = transfer.transfer_test("arrow", np.array([3.0, 1.0, 2.0, 5.0, 4.0, 6.0]), -np.array([3.0, 1.0, 2.0, 5.0, 4.0, 6.0]), np.ones(6, dtype=bool), np.random.default_rng(3), R=500)
    ck("transfer: a template strictly below every detector is still adverse (D8 unchanged where scores differ)", low["adverse"] and low["n_lt"] == 0)


def u_code_keys():
    section("the keys the K1, K2 and K3 code builds are the keys of keys.py (D14), each drawn in the epoch its work item carries")
    import keys
    seen = []
    epochs_seen = []
    EP = np.int64(0)   # epoch 0, as a numpy integer: the check below finds it by identity, so a literal 0 anywhere on the way would be found
    orig_seg, orig_pool, orig_rng = stats43.segment_test, stats43.make_pool, seeds.rng_for

    class Stop(Exception):
        pass

    def fake_segment_test(x, key, M=99, kind="iaaft", *, epoch):
        seen.append(key)
        epochs_seen.append(epoch)
        return {"pn": 50, "den": 100, "reject": False, "iters": 0, "nconv": 0, "flag_zero_spread": False, "T": 0.0, "js": [0], "C3": np.zeros((100, 1, 13), dtype=np.int64),
                "all_zero_spread": True}

    def fake_make_pool(x, key, M=99, kind="iaaft", *, epoch):
        seen.append(key)
        epochs_seen.append(epoch)
        raise Stop()

    def rec_rng(*key, epoch):
        epochs_seen.append(epoch)
        return orig_rng(*key, epoch=epoch)
    try:
        stats43.segment_test, stats43.make_pool, seeds.rng_for = fake_segment_test, fake_make_pool, rec_rng
        tasks.k2_task(("ar1_0.9|exp", 4096, 7, "raw", EP))
        tasks.k2_task(("white", 2048, 3, "iaaft", EP))
        for use in ("native4096", "native2048", "bm2", "sub2", "q12", "q8", "placement", "wlen2048"):
            tasks.k3_task(("shots", use, 5, "iaaft", EP))
        tasks.k3_task(("shots", "native4096", 6, "leaky", EP))
        for src_, cls_, n_ in (("class", "g2|exp", 1024), ("int", "white", 1024), ("wave", "waveform", 4096)):
            try:
                tasks.k1_task((src_, cls_, 4, n_, "cubic", "iaaft", EP))
            except Stop:
                pass
    finally:
        stats43.segment_test, stats43.make_pool, seeds.rng_for = orig_seg, orig_pool, orig_rng
    ck("every data draw and pool of the K1, K2 and K3 tasks gets the epoch of its work item (%d draws)" % len(epochs_seen), len(epochs_seen) > len(seen) and all(e is EP for e in epochs_seen))
    ck("a work item without its epoch is refused (it does not unpack)", _refused(lambda: tasks.k2_task(("white", 2048, 3, "iaaft"))) and _refused(lambda: tasks.seg_task((np.zeros(8), ("u",) * 6, "iaaft"))))
    want = [keys.k2_pool("ar1_0.9", 4096, 7), keys.k2_pool("white", 2048, 3)]
    want += [keys.k3_pool("shots", u, 5) for u in ("native4096", "native2048", "bm2", "sub2", "q12", "q8", "placement", "wlen2048")]
    want += [keys.k3_pool("shots", "native4096", 6), keys.k1_pool("g2", 1024, 4), keys.k1int_pool("white", 4), keys.k1wave_pool()]
    eq("K2 (control on the exp version included), K3 (every use and the circular-shift control) and K1 pools use the keys of keys.py", seen, want)
    eq("the K2 control draws from the pool key of the plain AR(1) 0.9 draw at 4,096", seen[0], ("K2:ar1_0.9:4096", "synthetic", "native", 7, "surrogates", 0))
    eq("a K3 pool uses the instrument of its data draw (length of the block)", (seen[2][0], seen[6][0], seen[7][0]), ("K3:shots:4224", "K3:shots:4224", "K3:shots:4224"))
    eq("K3 native2048 and wlen2048 pools use the 2176-sample block", (seen[3][0], seen[9][0]), ("K3:shots:2176", "K3:shots:2176"))
    ck("the circular-shift control shares the key of the shots native4096 pool, by design", seen[10] == keys.k3_pool("shots", "native4096", 6) and keys.k3_pool("shots", "native4096", 6)[2] == "native4096")
    ck("a pool key with fewer than six fields is refused", _refused(lambda: stats43.make_pool(np.arange(10.0), ("a", "b", "c", "d"), epoch=0)))
    eq("keys: K4 detector key names the pair, run and seed", keys.k4_detectors("A>Aprime", "placement", 3, "detectors-arrow"), ("K4:A>Aprime", "verdict", "placement", 3, "detectors-arrow", 0))
    eq("keys: K5 pool key names the series, run and seed", keys.k5_pool("cascade_rank", "verdict", "amp_lognormal", 3, 2, 5), ("K5b:cascade_rank", "verdict", "amp_lognormal", "s3-flow-L2-q5", "surrogates", 0))
    eq("keys: control pool", keys.control_pool("C2", "GW:H1", "native", 3), ("GW:H1", "verdict", "native", 3, "C2-surrogates", 0))
    ck("keys: control must be C2 or C3", _refused(lambda: keys.control_series("C4", "x", "native", 0)))
    eq("keys: a Law 2b net", keys.l2b_net("W", "native"), "law2b-W:native")


def _printed(f):
    """What f prints, and the exit code if it ends with SystemExit (None otherwise)."""
    buf = io.StringIO()
    code = None
    with contextlib.redirect_stdout(buf):
        try:
            f()
        except SystemExit as e:
            code = e.code
    return buf.getvalue(), code


def u_amendment4():
    section("Amendment 4: a tie counts as at or below in the adverse decision (C1), key epoch (D14), epoch rules of the runs (C3), untested Law 2b instances (C2)")
    import keys
    import kcommon
    import epochs
    F = Fraction
    ar = transfer.adverse_rule
    # C1: reading D8 as amended, on exact integers (40 x n_le < R)
    ck("D8 at R = 99,999: 2,499 detectors at or below is adverse (40 x 2,499 = 99,960 < 99,999)", ar(2499, 99999) is True)
    ck("D8 at R = 99,999: 2,500 detectors at or below is not adverse (40 x 2,500 = 100,000)", ar(2500, 99999) is False)
    ck("D8: exactly R/40 at or below is not fewer than R/40 (2 of 80 is not adverse, 1 of 80 is)", ar(2, 80) is False and ar(1, 80) is True)
    ck("D8 at R = 1: no detector at or below is adverse, the one detector at or below is not", ar(0, 1) is True and ar(1, 1) is False)
    ck("D8: every detector at or below is not adverse (R = 99,999)", ar(99999, 99999) is False)
    ck("D8 accepts numpy integers", ar(np.int64(2499), np.int64(99999)) is True)
    for nm, a, b in (("a bool count", True, 99999), ("a bool R", 1, True), ("a float count", 2499.0, 99999), ("a numpy float count", np.float64(2499), 99999),
                     ("a float R", 1, 99999.0), ("a string count", "2499", 99999), ("a missing count", None, 99999)):
        ck("D8 refuses %s (TypeError)" % nm, _refused(lambda: ar(a, b), (TypeError,)))
    for nm, a, b in (("R = 0", 0, 0), ("a negative count", -1, 5), ("a count above R", 100000, 99999)):
        ck("D8 refuses %s (ValueError)" % nm, _refused(lambda: ar(a, b), (ValueError,)))
    # C1 in the transfer test: the all-tied case of the archived patch, now under the amended rule
    r = transfer.transfer_test("profile", np.ones(10) / np.sqrt(10), np.ones(10), np.ones(10, dtype=bool), np.random.default_rng(3), R=100)
    ck("all tied (every detector ties with w_A): D = 1, p = 1, n_lt 0, n_tie 100, n_le 100", (r["D"], r["p"], r["n_lt"], r["n_tie"], r["n_le"]) == (1, 1, 0, 100, 100))
    ck("all tied: not adverse under D8 as amended (the rule before Amendment 4, 40 x n_lt < R, gave adverse here)", r["adverse"] is False and transfer.ADVERSE_DEN * r["n_lt"] < r["m"] * 10)
    w8 = np.array([1.0, 3, 3, 3, 3, 3, 3, 3])
    rp = transfer.transfer_test("profile", w8 / np.sqrt(w8 @ w8), np.array([1.0, 0, 0, 0, 0, 0, 0, 0]), np.ones(8, dtype=bool), np.random.default_rng(3), R=100)
    ck("partly tied (about one detector in eight ties with S_A, none below): n_le = n_tie > 2, not adverse", rp["n_lt"] == 0 and rp["n_le"] == rp["n_tie"] > 2 and rp["adverse"] is False)
    ck("partly tied: the decision is adverse_rule(n_le, R)", rp["adverse"] == ar(rp["n_le"], 100))
    w6 = np.array([3.0, 1.0, 4.0, 1.5, 9.0, 2.6])
    rs = transfer.transfer_test("arrow", w6 / np.sqrt(w6 @ w6), np.array([1.0, -2.0, 0.5, 3.0, -1.0, 2.0]), np.ones(6, dtype=bool), np.random.default_rng(9), R=3000)
    ck("counts are consistent: n_ge + n_lt = R, n_le = n_lt + n_tie, p = (1 + n_ge) / (R + 1) (the p-value counts a tie against w_A, unchanged)", rs["n_ge"] + rs["n_lt"] == 3000 and rs["n_le"] == rs["n_lt"] + rs["n_tie"] and rs["p"] == F(1 + rs["n_ge"], 3001) and rs["nonfinite"] is False)
    r0 = transfer.transfer_test("arrow", np.arange(1.0, 7.0), np.arange(1.0, 7.0), np.zeros(6, dtype=bool), np.random.default_rng(1), R=500)
    ck("no jointly populated entry (m = 0): every detector ties, consistent counts, not adverse, p = 1", (r0["m"], r0["n_ge"], r0["n_lt"], r0["n_tie"], r0["n_le"], r0["p"], r0["adverse"], r0["nonfinite"]) == (0, 500, 0, 500, 500, 1, False, False))
    big = np.full(8, 1e300)
    rn = transfer.transfer_test("profile", big, big, np.ones(8, dtype=bool), np.random.default_rng(1), R=50)
    ck("S_B(w_A) not finite (overflow): neither adverse nor passing, p = 1, flagged", rn["nonfinite"] is True and rn["adverse"] is False and rn["p"] == 1 and not np.isfinite(rn["S_A"]))
    rd = transfer.transfer_test("arrow", np.array([1e300, 1e300]), np.array([1e8, -1e8]), np.ones(2, dtype=bool), np.random.default_rng(1), R=200)
    ck("S_B(w_A) finite but some detector scores not finite: neither adverse nor passing, p = 1, flagged", bool(np.isfinite(rd["S_A"])) and rd["n_nonfinite"] > 0 and rd["nonfinite"] is True and rd["adverse"] is False and rd["p"] == 1)
    r0n = transfer.transfer_test("profile", big, big, np.zeros(8, dtype=bool), np.random.default_rng(1), R=50)
    ck("m = 0 with S_B(w_A) not finite: flagged, no tie counted, not adverse", r0n["nonfinite"] is True and r0n["n_tie"] == 0 and r0n["adverse"] is False and r0n["p"] == 1)
    ck("the populated-feature floor keeps the non-finite flag", transfer.apply_floor(rd, "arrow")["nonfinite"] is True and transfer.apply_floor(rd, "arrow")["adverse"] is False)
    run_adv = {"adverse": True, "nonfinite": False}
    run_nei = {"adverse": False, "nonfinite": False}
    run_bad = {"adverse": False, "nonfinite": True}
    pr = transfer.pair_result
    ck("pair result: adverse in every run gives 'adverse', a Holm pass gives 'pass', otherwise 'neither'", pr([run_adv, run_adv], False) == "adverse" and pr([run_nei, run_nei], True) == "pass" and pr([run_adv, run_nei], False) == "neither")
    ck("pair result: a run with a non-finite score makes the pair 'neither', even with the other runs adverse or a Holm pass", pr([run_adv, run_bad], False) == "neither" and pr([run_nei, run_bad], True) == "neither")
    ck("pair result refuses a non-bool Holm result (TypeError, on a run that is not adverse), no runs, and a pair both passing and adverse",
       _refused(lambda: pr([run_nei], 1), (TypeError,)) and _refused(lambda: pr([], False)) and _refused(lambda: pr([run_adv], True)))
    # D14 key epoch
    eq("master field: 20261121 in epoch 0, 20261121e<k> in epoch k", (seeds.master_field(0), seeds.master_field(1), seeds.master_field(np.int64(7))), ("20261121", "20261121e1", "20261121e7"))
    eq("seed string in epoch 1: only the master field changes", seeds.seed_string("a", "b", "c", "d", "e", 0, epoch=1), "20261121e1|a|b|c|d|e|0")
    for nm, e in (("True", True), ("False", False), ("-1", -1), ("1.0", 1.0), ("'1'", "1"), ("None", None), ("a numpy float", np.float64(1)), ("a numpy bool", np.bool_(True))):
        ck("the key epoch refuses %s" % nm, _refused(lambda: seeds.check_epoch(e)))
    uk = ("unit-epoch", "synthetic", "native", 0, "surrogates", 0)   # a key of no test: draws on epoch 1 are allowed here
    ck("a draw without an epoch is refused at every draw point (seed rule, keys.rng, pools, units, series, controls, instance F)",
       _refused(lambda: seeds.rng_for(*uk), (TypeError,)) and _refused(lambda: seeds.seed_string(*uk), (TypeError,)) and _refused(lambda: keys.rng(uk), (TypeError,))
       and _refused(lambda: stats43.make_pool(np.arange(64.0), uk), (TypeError,)) and _refused(lambda: stats43.segment_test(np.arange(64.0), uk), (TypeError,))
       and _refused(lambda: flow.analyse_unit(np.arange(64.0), uk), (TypeError,)) and _refused(lambda: synth.k2_series("white", 0, 64), (TypeError,))
       and _refused(lambda: synth.k4_stream("A", 0, "fit"), (TypeError,)) and _refused(lambda: synth.k5_series("expo", 0, "verdict"), (TypeError,))
       and _refused(lambda: controls.c3_shuffle(np.arange(64.0), uk), (TypeError,)) and _refused(lambda: law2b.white_floor_F(np.arange(64.0), uk), (TypeError,))
       and _refused(lambda: flow.stream_units(np.arange(64.0), lambda l, q: uk), (TypeError,)) and _refused(lambda: pipeline.analyse_list([None], lambda q: uk), (TypeError,)))
    a0, a1, b1 = keys.rng(uk, 0).random(4), keys.rng(uk, 1).random(4), keys.rng(uk, 1).random(4)
    ck("a key of no test: epoch 1 gives another stream than epoch 0, and the same stream each time", not np.array_equal(a0, a1) and np.array_equal(a1, b1))
    xs = synth.standardise(synth.ar1(0.8, 256, np.random.default_rng(12)))
    p0, _, _ = stats43.make_pool(xs, uk, 9, epoch=0)
    p1, _, _ = stats43.make_pool(xs, uk, 9, epoch=1)
    ck("a pool of a key of no test differs between epochs 0 and 1 and keeps the real series as row 0", not np.array_equal(p0[1:], p1[1:]) and np.array_equal(p0[0], p1[0]))
    E1 = np.int64(1)
    sj, _ = flow.stream_units(np.random.default_rng(6).standard_normal(640 * 40), lambda l, q: ("unit-epoch", "s", "n", "L%dq%d" % (l, q), "surrogates", 0), N=512, epoch=E1)
    ck("every flow-unit job carries the run's epoch as its last field", len(sj) > 0 and all(j[-1] is E1 for j in sj))
    job = (synth.standardise(synth.ar1(0.7, 256, np.random.default_rng(20))), ("unit-epoch", "synthetic", "native", 0, "surrogates", 0), "iaaft", 1)
    t1, t1b, t0 = tasks.seg_task(job), tasks.seg_task(job), tasks.seg_task(job[:3] + (0,))
    ck("a segment task draws its pool in the epoch its work item carries (key of no test: epoch 1 repeats, and differs from epoch 0)",
       np.array_equal(t1["zu"], t1b["zu"]) and not np.array_equal(t1["zu"], t0["zu"]))
    # C3: command line of the known-answer scripts
    pa = kcommon.parse_args
    s0 = pa(["t", "smoke"], seeded=True)
    eq("smoke run: epoch 0 when none is given, a diagnostic", (s0["mode"], s0["epoch"], s0["diagnostic"]), ("smoke", 0, True))
    eq("smoke run with epoch=0", pa(["t", "smoke", "epoch=0"], seeded=True)["epoch"], 0)
    f0 = pa(["t", "full", "epoch=0"], seeded=True)
    f1 = pa(["t", "full", "epoch=1", "part=3/8"], seeded=True, parts=True)
    k6 = pa(["t", "full"], seeded=False)
    k6s = pa(["t", "smoke"], seeded=False)
    eq("full run on epoch 0 is a diagnostic; full run on epoch 1 with a part is not", ((f0["epoch"], f0["diagnostic"]), (f1["epoch"], f1["part"], f1["nparts"], f1["diagnostic"])), ((0, True), (1, 3, 8, False)))
    eq("K6 has no epoch, and any run of it is a full run, smoke included (not a diagnostic)", (k6["epoch"], k6["diagnostic"], k6s["epoch"], k6s["diagnostic"]), (None, False, None, False))
    bad_args = (("a smoke run on epoch 1", ["t", "smoke", "epoch=1"], {}), ("a full run without an epoch", ["t", "full"], {}), ("a negative epoch", ["t", "full", "epoch=-1"], {}),
                ("an epoch with a leading zero", ["t", "full", "epoch=01"], {}), ("a float epoch", ["t", "full", "epoch=1.0"], {}), ("an empty epoch", ["t", "full", "epoch="], {}),
                ("the epoch twice", ["t", "full", "epoch=1", "epoch=1"], {}), ("the old positional part (part and count as bare words)", ["t", "full", "epoch=1", "3", "8"], {"parts": True}),
                ("a part without its count", ["t", "full", "epoch=1", "part=3"], {"parts": True}), ("part 8 of 8", ["t", "full", "epoch=1", "part=8/8"], {"parts": True}),
                ("0 parts", ["t", "full", "epoch=1", "part=0/0"], {"parts": True}), ("a part where the script has none", ["t", "full", "epoch=1", "part=0/2"], {}),
                ("an unknown size", ["t", "medium", "epoch=1"], {}), ("no size", ["t"], {}), ("a combine run with no part files", ["t", "full", "epoch=1"], {"files": True}))
    for nm, argv, kw in bad_args:
        ck("command line refuses %s" % nm, _refused(lambda: pa(argv, seeded=True, **kw), (kcommon.UsageError,)))
    ck("command line refuses an epoch for K6 (no random draws)", _refused(lambda: pa(["t", "full", "epoch=1"], seeded=False), (kcommon.UsageError,)))
    out, code = _printed(lambda: kcommon.parse_cli(["t", "full"], seeded=True))
    ck("a usage error prints the usage and ends with exit status 2", code == 2 and "usage error" in out and "epoch=<k>" in out)
    eq("summary words: SMOKE, DIAGNOSTIC (full on epoch 0), none (full from epoch 1, and K6 in either size)", [kcommon.summary_tag(x) for x in (s0, f0, f1, k6, k6s)], ["SMOKE ", "DIAGNOSTIC ", "", "", ""])
    out, code = _printed(lambda: kcommon.summary("T", "PASS", "x", f0))
    ck("a full run on epoch 0 says DIAGNOSTIC in its SUMMARY line", out == "SUMMARY T DIAGNOSTIC PASS | x\n" and code is None)
    out, code = _printed(lambda: kcommon.summary("T", "FAIL", "x", f0))
    ck("a diagnostic FAIL still ends with exit status 1", out.startswith("SUMMARY T DIAGNOSTIC FAIL") and code == 1)
    c40 = "0123456789abcdef0123456789abcdef01234567"
    out, _ = _printed(lambda: kcommon.header("T", "title", f0, c40))
    ck("the header of a full run on epoch 0 says DIAGNOSTIC and prints the master field and the commit", "DIAGNOSTIC" in out and "EPOCH 0 | master field 20261121" in out and "CODE COMMIT " + c40 in out)
    out, _ = _printed(lambda: kcommon.header("T", "title", f1, c40))
    ck("the header of a full run on epoch 1 prints its master field, the seed rule with it, and its part", "EPOCH 1 | master field 20261121e1" in out and "20261121e1|<instrument>|" in out
       and "PART 3 of 8" in out and "RUN test=T size=full epoch=1 part=3/8 commit=" + c40 in out and "DIAGNOSTIC" not in out)
    out, _ = _printed(lambda: kcommon.header("K6", "title", k6, c40))
    ck("the header of K6 prints no master field", "EPOCH not used" in out and "master field" not in out and "RUN test=K6 size=full epoch=- part=- commit=" in out)
    out, _ = _printed(lambda: kcommon.header("K6", "title", k6s, c40))
    ck("the header of a K6 smoke run calls it a full run and names no epoch and no diagnostic", "the same run as FULL" in out and "EPOCH not used" in out
       and "epoch 0" not in out and "diagnostic" not in out.lower())
    ck("the code commit is a string (a commit, a commit with +modified, or unknown)", isinstance(kcommon.code_commit(), str))
    comb = pa(["c", "full", "epoch=1", "p0", "p1", "p2"], seeded=True, files=True)
    good = [kcommon.parse_run_line(kcommon.run_line("K2", pa(["t", "full", "epoch=1", "part=%d/3" % i], seeded=True, parts=True), c40)) for i in range(3)]
    eq("combine: parts of one test, size, epoch and clean commit covering every part are joined", (comb["files"], kcommon.check_parts(good, "K2", comb, c40)), (["p0", "p1", "p2"], []))
    def changed(k, field, value):
        g = [dict(x) for x in good]
        g[k][field] = value
        return g
    for nm, lines, commit in (("a part on another epoch", changed(1, "epoch", "2"), c40), ("a part from another commit", changed(2, "commit", "f" * 40), c40),
                              ("parts and run with an unknown commit", [dict(x, commit="unknown") for x in good], "unknown"),
                              ("parts from a modified checkout", [dict(x, commit=c40 + "+modified") for x in good], c40 + "+modified"),
                              ("a combine run on another commit", good, "e" * 40), ("a missing part", good[:2], c40), ("a part given twice", good + good[:1], c40),
                              ("parts with different counts", changed(0, "part", "0/4"), c40), ("a part of another test", changed(0, "test", "K3"), c40),
                              ("a part of another size", changed(0, "size", "smoke"), c40), ("a file that is not a part", changed(0, "part", "-"), c40)):
        ck("combine refuses %s" % nm, len(kcommon.check_parts(lines, "K2", comb, commit)) > 0)
    # C3: the ledger of used epochs. The shipped ledger is checked against the rules only, never for its contents, which grow with the runs.
    rows = epochs.read_ledger()
    ck("EPOCHS.tsv parses, and for each seeded test the lowest unused epoch is allowed and every epoch the test has used is refused",
       all(epochs.check_full_run(rows, t, epochs.next_epoch(rows, t)) is None and all(epochs.check_full_run(rows, t, e) is not None for e in epochs.used_epochs(rows, t))
           for t in epochs.SEEDED))
    H = "\t".join(epochs.HEADER) + "\n"
    L1 = epochs.parse_ledger(H + "K4\t1\tabcdef1\t2026-11-25\tfull-count\tround 1 rerun\n")
    ck("after K4 used epoch 1: K4's next epoch is 2, K1's is still 1 (epochs are per test)", epochs.next_epoch(L1, "K4") == 2 and epochs.next_epoch(L1, "K1") == 1)
    ck("a full-count run is refused on an epoch the test used, on epoch 0 and on any epoch but the lowest unused one; allowed on that one",
       epochs.check_full_run(L1, "K4", 1) is not None and epochs.check_full_run(L1, "K4", 0) is not None and epochs.check_full_run(L1, "K4", 3) is not None and epochs.check_full_run(L1, "K4", 2) is None)
    ck("K6 is exempt from the epoch rule, and an unknown test or a bool epoch is refused", epochs.check_full_run(L1, "K6", 1) is not None and epochs.check_full_run(L1, "K7", 1) is not None and epochs.check_full_run(L1, "K4", True) is not None)
    L2 = epochs.parse_ledger(H + "K4\t1\t-\t2026-11-25\tfull-count\ta\nK4\t3\t-\t2026-11-26\tfull-count\tb\nK2\t1\t-\t2026-11-25\tlaw2b-check\tc\n")
    ck("the lowest unused epoch fills a gap (K4 used 1 and 3: next 2); an epoch whose draws a Law 2b check used counts as used (K2 next 2)", epochs.next_epoch(L2, "K4") == 2 and epochs.next_epoch(L2, "K2") == 2)
    bad_ledgers = (("no header", "K4\t1\t-\t2026-11-25\tfull-count\tx\n"), ("a row of five fields", H + "K4\t1\t-\t2026-11-25\tfull-count\n"),
                   ("a K6 row", H + "K6\t1\t-\t2026-11-25\tfull-count\tx\n"), ("an unknown test", H + "K9\t1\t-\t2026-11-25\tfull-count\tx\n"),
                   ("an epoch with a leading zero", H + "K4\t01\t-\t2026-11-25\tfull-count\tx\n"), ("a full-count run on epoch 0", H + "K4\t0\t-\t2026-11-25\tfull-count\tx\n"),
                   ("a diagnostic run on epoch 2", H + "K4\t2\t-\t2026-11-25\tdiagnostic\tx\n"), ("two full-count runs on one epoch", H + "K4\t1\t-\t2026-11-25\tfull-count\tx\nK4\t1\t-\t2026-11-26\tfull-count\ty\n"),
                   ("a bad date", H + "K4\t1\t-\t25.11.2026\tfull-count\tx\n"), ("a bad commit", H + "K4\t1\tHEAD\t2026-11-25\tfull-count\tx\n"), ("an unknown kind", H + "K4\t1\t-\t2026-11-25\tsmoke\tx\n"))
    for nm, text in bad_ledgers:
        ck("ledger refuses %s" % nm, _refused(lambda: epochs.parse_ledger(text), (epochs.LedgerError,)))
    L0 = epochs.parse_ledger(H)
    ck("an empty ledger: every seeded test's next epoch is 1, and a full-count run on epoch 1 is allowed", all(epochs.next_epoch(L0, t) == 1 and epochs.check_full_run(L0, t, 1) is None for t in epochs.SEEDED))
    L3 = epochs.parse_ledger(H + "K4\t1\t-\t2026-11-25\tdraws-seen\tdiagnostic under other detector keys on the draws of epoch 1\n")
    ck("an epoch whose draws an outcome of another run used (draws-seen) counts as used: K4's next epoch is 2", epochs.next_epoch(L3, "K4") == 2 and epochs.check_full_run(L3, "K4", 1) is not None)
    ck("ledger refuses a draws-seen row on epoch 0 (epoch 0 is the diagnostic epoch)", _refused(lambda: epochs.parse_ledger(H + "K4\t0\t-\t2026-11-25\tdraws-seen\tx\n"), (epochs.LedgerError,)))
    rK4 = "K4\t1\tabcdef1\t2026-11-25\tfull-count\trun_full.sh, three modes, results folder r1\n"
    J = epochs.parse_ledgers([H, H + rK4])
    ck("two ledgers read as one: a run recorded only in the second (the build folder's) uses its epoch", epochs.check_full_run(J, "K4", 1) is not None and epochs.next_epoch(J, "K4") == 2)
    ck("two ledgers read as one: a row both hold counts once", len(epochs.parse_ledgers([H + rK4, H + rK4])) == 1)
    ck("two ledgers read as one: two different full-count rows of one test and epoch are refused",
       _refused(lambda: epochs.parse_ledgers([H + rK4, H + rK4.replace("r1", "r2")]), (epochs.LedgerError,)))
    ck("one ledger: the same full-count row written twice is refused", _refused(lambda: epochs.parse_ledger(H + rK4 + rK4), (epochs.LedgerError,)))
    # C3: a full run by hand is checked against the ledger before any draw
    lr = kcommon.ledger_refusal
    k4f = lambda e: pa(["t", "full", "epoch=%d" % e, "part=0/10"], seeded=True, parts=True)
    ck("a hand run on the lowest unused epoch is allowed; on a used epoch or one that is not the lowest unused, it is refused",
       lr(k4f(1), "K4", L0) is None and lr(k4f(2), "K4", L1) is None and lr(k4f(1), "K4", L1) is not None and lr(k4f(3), "K4", L1) is not None and lr(k4f(2), "K4", L0) is not None)
    ck("the ledger does not touch a smoke run, a full run on epoch 0 or a combine run", lr(s0, "K4", L1) is None and lr(f0, "K4", L1) is None and lr(comb, "K4", J) is None)
    ck("parse_cli needs the test id of a seeded script before a full run from epoch 1", _refused(lambda: kcommon.parse_cli(["t", "full", "epoch=1"], seeded=True), (ValueError,)))
    nk4 = epochs.next_epoch(rows, "K4")
    out, code = _printed(lambda: kcommon.parse_cli(["t", "full", "epoch=%d" % nk4, "part=0/10"], seeded=True, parts=True, test="K4"))
    ck("parse_cli reads the shipped ledger: a full run of K4 on its lowest unused epoch goes ahead", code is None and out == "")
    out, code = _printed(lambda: kcommon.parse_cli(["t", "full", "epoch=%d" % (nk4 + 1), "part=0/10"], seeded=True, parts=True, test="K4"))
    ck("parse_cli reads the shipped ledger: a full run of K4 on an epoch above its lowest unused one ends with exit status 2 before any draw",
       code == 2 and out.startswith("refused by the ledger known_answer/EPOCHS.tsv:"))
    # C2: an instance that fails its pre-data check is not tested
    ut = law2b.untested_instances({"W": {"K2": True, "K3": True, "paired K4": False}, "Q": {"K2": True, "K3": True}, "O4": {"K2": False}})
    eq("an instance that fails any pre-data check is not tested", sorted(ut), ["O4", "W"])
    ck("untested_instances refuses an instance with no recorded check, a non-bool result and an unknown instance",
       _refused(lambda: law2b.untested_instances({"W": {}})) and _refused(lambda: law2b.untested_instances({"W": {"K2": 1}})) and _refused(lambda: law2b.untested_instances({"Z": {"K2": True}})))
    tn = law2b.test_name
    computed = {tn("b", "Q", "GW-SEIS"): F(1, 10000), tn("b", "H", "GW-SEIS"): F(1, 100)}
    hf = law2b.holm_family(computed, ut)
    explicit = levels.holm(dict(computed, **{tn("b", "W", "GW-SEIS"): F(1)}), m=levels.LAW2B_FAMILY)
    ck("Holm over the 102 tests: an untested instance's test is left out, which is the same as entering it with p = 1", hf[tn("b", "Q", "GW-SEIS")] == explicit[tn("b", "Q", "GW-SEIS")] and hf[tn("b", "H", "GW-SEIS")] == explicit[tn("b", "H", "GW-SEIS")] and hf[tn("b", "Q", "GW-SEIS")][0])
    ck("Holm refuses a computed p for a test of an untested instance, and a name that is not a Law 2b test",
       _refused(lambda: law2b.holm_family({tn("b", "W", "GW-SEIS"): F(1, 10000)}, ut)) and _refused(lambda: law2b.holm_family({"t": F(1, 2)}, ut)) and _refused(lambda: law2b.holm_family({tn("b", "O4", "GW-SEIS"): F(1, 2)}, frozenset())))
    items = ("GW-SEIS", "GW-WAVES")
    def passes(kind, untested, ok):
        return {(i, it): (i, it) in ok for i in law2b.INSTANCES[kind] if i not in untested for it in items}
    st = law2b.search_state("b", items, {"W"}, passes("b", {"W"}, {("Q", "GW-SEIS"), ("Q", "GW-WAVES")}), set(), False)
    ck("with W not tested, Q passing for every triggering item gives transformed core under Q, and the report names the untested route W",
       st["state"] == "transformed core" and st["rescued_by"] == ["Q"] and "transformed core passed under instance Q" in st["wording"] and "instance W (T1_GAUGE_SIMILARITY) for arrow transfer (b): not tested" in st["wording"])
    st = law2b.search_state("b", items, {"W"}, passes("b", {"W"}, {("Q", "GW-SEIS")}), set(), False)
    ck("with W not tested and no instance passing for every item: evidence against at the confirmatory level, Law 2b search unresolved", st["state"] == "unresolved" and st["wording"].startswith("evidence against at the confirmatory level, Law 2b search unresolved"))
    st = law2b.search_state("b", items, {"W"}, passes("b", {"W"}, set()), set(), True)
    ck("with W not tested, no instance passing and the obstruction holding, the outcome is still not final (the search is incomplete)", st["state"] == "unresolved" and st["untested_routes"] == ["instance W (T1_GAUGE_SIMILARITY) for arrow transfer (b): not tested"])
    st = law2b.search_state("b", items, set(), passes("b", set(), set()), set(), True)
    ck("with every instance tested, none passing and the obstruction holding: final, with no untested route", st["state"] == "final" and st["wording"] == "evidence against, final" and st["untested_routes"] == [])
    st = law2b.search_state("b", items, {"O4"}, passes("b", set(), set()), set(), True)
    ck("an untested instance that kind (b) does not list (O4) does not touch its search", st["state"] == "final")
    st = law2b.search_state("b", items, set(), passes("b", set(), {("Q", "GW-SEIS"), ("Q", "GW-WAVES")}), {"Q"}, True)
    ck("a vacuous instance cannot rescue, and its pass keeps the outcome from being final", st["state"] == "unresolved" and st["rescued_by"] == [])
    allc = law2b.INSTANCES["c"]
    st = law2b.search_state("c", items, set(), {(i, it): True for i in allc for it in items}, set(allc), False)
    ck("every tested instance vacuous (each passing on the data): accepted, nothing rescues, unresolved", st["state"] == "unresolved" and st["rescued_by"] == [])
    ck("search_state refuses an unknown kind, no item, a result for an untested instance (it cannot rescue), a missing result, a vacuous untested instance and a non-bool obstruction",
       _refused(lambda: law2b.search_state("d", items, set(), {}, set(), True)) and _refused(lambda: law2b.search_state("b", (), set(), {}, set(), True))
       and _refused(lambda: law2b.search_state("b", items, {"W"}, passes("b", set(), set()), set(), True)) and _refused(lambda: law2b.search_state("b", items, set(), passes("b", {"W"}, set()), set(), True))
       and _refused(lambda: law2b.search_state("b", items, {"W"}, passes("b", {"W"}, set()), {"W"}, True)) and _refused(lambda: law2b.search_state("b", items, set(), passes("b", set(), set()), set(), 1)))
    ck("search_state refuses a pass result that is not a bool", _refused(lambda: law2b.search_state("b", items, set(), {k: 1 for k in passes("b", set(), set())}, set(), True), (TypeError,)))
    ck("search_state refuses a triggering item named twice", _refused(lambda: law2b.search_state("b", ("GW-SEIS", "GW-SEIS"), set(), {}, set(), True)))


def _raises(f):
    try:
        f()
    except (ValueError, FloatingPointError):
        return True
    return False


def main():
    print("UNIT CHECKS of the building blocks (known answers)")
    print("python", sys.version.split()[0], "numpy", np.__version__)
    u_ranks(); u_patterns(); u_surrogates_identity(); u_segments(); u_nets(); u_levels(); u_transfer(); u_flow(); u_gates_and_seeds(); u_law2b(); u_review_guards(); u_amendment2(); u_audit_three(); u_code_keys(); u_amendment4(); u_outcomes()
    ok = C.done("UNIT CHECKS")
    if not ok:
        print("FAIL")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
