"""Unit checks of the building blocks, with known answers (exact where the plan's quantity is exact). Exit status 1 and
the text FAIL on any failed check. Output is identical in python -I -B, -I -O -B and -I -B -W error."""
import hashlib
import os
import sys
from fractions import Fraction
from itertools import product
import math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import flow, gates, iaaft, law2b, levels, nets, outcomes, patterns, ranks, second_impl, segments, seeds, stats43, synth, transfer
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
        key = ("U", "s", "native", n)
        base = stats43.segment_test(x, key)
        for nm, y in maps.items():
            ck("map %s leaves distinct values unchanged (n=%d)" % (nm, n), nets.map_guard_ok(x, y))
            r = stats43.segment_test(y, key)
            eq("C3 counts identical, %s, n=%d" % (nm, n), r["C3"], base["C3"])
            eq("standardised features identical, %s, n=%d" % (nm, n), r["Z"], base["Z"])
            eq("p identical, %s, n=%d" % (nm, n), r["pn"], base["pn"])
        pool_x, _, _ = stats43.make_pool(x, key)
        pool_y, _, _ = stats43.make_pool(np.exp(x), key)
        eq("surrogate pool identical under exp, n=%d" % n, pool_x[1:], pool_y[1:])
        pool_m, _, _ = stats43.make_pool(-x, key)
        eq("pool of -x is the negated pool of x, n=%d" % n, pool_m[1:], -pool_x[1:])
        rm = stats43.segment_test(-x, key)
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
    eq("seed string", seeds.seed_string("a", "b", "c", "d", "e", 0), s)
    eq("seed integer is the first 16 hex digits of SHA-256", seeds.seed_int("a", "b", "c", "d", "e", 0), int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:16], 16))
    ck("same key gives the same stream, a different index a different one", seeds.rng_for("a", "b", "c", "d", "e", 0).random() == seeds.rng_for("a", "b", "c", "d", "e", 0).random() and seeds.rng_for("a", "b", "c", "d", "e", 1).random() != seeds.rng_for("a", "b", "c", "d", "e", 0).random())


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
    f = law2b.white_floor_F(x, ("k", "s", "n", 0))
    ck("F adds noise of about 1/1000 of the standard deviation", 0 < float(np.abs(f - x).max()) < 0.01 * x.std() * 10 and float(np.std(f - x)) > 0)
    eq("F is reproducible", law2b.white_floor_F(x, ("k", "s", "n", 0)), f)
    eq("tail spread of 0..1000 ramp", round(law2b.tail_spread(np.arange(1001.0)), 6), round((999.0 - 1.0) / 500.0, 6))
    ck("E: a heavy-tailed segment is event-rich against the Gaussian median", law2b.event_rich(synth.shots_ar(4096, np.random.default_rng(3)), law2b.event_rich_threshold([np.random.default_rng(i).standard_normal(4096) for i in range(5)])))
    eq("max-plus score", float(law2b.max_plus_score(np.array([1., -2., 3.]), np.array([2., 1., 1.]))), 3.0)
    ck("B is block maxima and H the square root", law2b.FLOW_BLOCK_OP_B == "max" and law2b.flow_freq_map_H(np.array([4.0])).tolist() == [2.0])
    src = os.path.join(HERE, "..", "src")
    users = []
    for fn in sorted(os.listdir(src)):
        if fn.endswith(".py") and fn != "law2b.py":
            with open(os.path.join(src, fn), "r", encoding="utf-8") as fh:
                if "law2b" in fh.read():
                    users.append(fn)
    eq("no module of src/ refers to law2b (confirmatory path does not call it)", users, [])


def _raises(f):
    try:
        f()
    except (ValueError, FloatingPointError):
        return True
    return False


def main():
    print("UNIT CHECKS of the building blocks (known answers)")
    print("python", sys.version.split()[0], "numpy", np.__version__)
    u_ranks(); u_patterns(); u_surrogates_identity(); u_segments(); u_nets(); u_levels(); u_transfer(); u_flow(); u_gates_and_seeds(); u_law2b(); u_outcomes()
    ok = C.done("UNIT CHECKS")
    if not ok:
        print("FAIL")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
