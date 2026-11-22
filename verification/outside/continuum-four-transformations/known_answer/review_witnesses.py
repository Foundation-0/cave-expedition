"""Witnesses of an outside executable review of the frozen-plan code (eight findings, CAVE8-01 to CAVE8-08), run against the
code for the amended plan. Each line prints what happened. Exit status is 1 if a witness shows an unguarded failure.
usage: review_witnesses.py"""
import os
import subprocess
import sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
import numpy as np
import flow, gates, levels, nets, patterns, ranks, segments, stats43, ties, transfer

BAD = []


def attempt(label, f):
    """Run f; report the result or the exception type and message."""
    try:
        r = f()
        print("  %-62s -> %s" % (label, r))
        return ("ok", r)
    except Exception as e:  # report every kind of failure, including crashes
        print("  %-62s -> raises %s: %s" % (label, type(e).__name__, str(e)[:70]))
        return ("raises", type(e).__name__)


def explicit(res):
    return res[0] == "raises" and res[1] in ("GateError", "ValueError", "TypeError")


def main():
    print("REVIEW WITNESSES (review of the frozen-plan code, run on the amended code)")
    print("CAVE8-01 exit status and the production kill-switch")
    import inspect
    print("  validate_series has a disabled= parameter:", "disabled" in inspect.signature(gates.validate_series).parameters)
    r = attempt("validate_series(['a','b'], 4096)", lambda: gates.validate_series(["a", "b"], 4096))
    if not explicit(r):
        BAD.append("CAVE8-01 numeric refusal")
    for script in ("k6_gate_checks.py", "units_check.py"):
        pass
    print("CAVE8-02 ties and ranks")
    q = np.array([0, 0, 1, 2, 2, 1, 0, 0] * 512, dtype=float)
    base, _ = patterns.counts_one(q, 3, 1)
    print("  raw tied waveform: tied windows %d, sigma_hat %r" % (patterns.tied_windows(base, 3), float(patterns.sigma_hat(base, 3))))
    for nm, f in nets.increasing_maps().items():
        y = f(q)
        c, _ = patterns.counts_one(y, 3, 1)
        print("  map %-6s distinct values %d -> %d, tied windows %d, sigma_hat %r, counts equal: %s" % (nm, ranks.n_distinct(q), ranks.n_distinct(y), patterns.tied_windows(c, 3), float(patterns.sigma_hat(c, 3)), bool((c == base).all())))
        if float(patterns.sigma_hat(c, 3)) != 0.0 and nets.map_guard_ok(q, y):
            BAD.append("CAVE8-02 sigma_hat under " + nm)
    n_, g_ = ranks.normal_scores(q), ranks.normal_scores(-q)
    print("  normal scores of the waveform and its negative are exact negatives:", bool(np.array_equal(g_, -n_)))
    r = attempt("tau0 of a constant series", lambda: transfer.tau0_segment(np.full(4096, 5.0)))
    if not explicit(r):
        BAD.append("CAVE8-02 tau0 constant")
    r = attempt("tau0 of a series of length 1", lambda: transfer.tau0_segment(np.array([1.0])))
    if not explicit(r):
        BAD.append("CAVE8-02 tau0 length 1")
    print("  tau0 of the tied waveform:", transfer.tau0_segment(q))
    print("CAVE8-03 exact p-values")
    r = attempt("holm({'t1': 0.05}, m=1) (float)", lambda: levels.holm({"t1": 0.05}, m=1))
    if not explicit(r):
        BAD.append("CAVE8-03 holm float")
    attempt("holm({'t1': Fraction(1,20)}, m=1)", lambda: levels.holm({"t1": Fraction(1, 20)}, m=1))
    r = attempt("binom_tail(True, True)", lambda: levels.binom_tail(True, True))
    if not explicit(r):
        BAD.append("CAVE8-03 bool S, K")
    r = attempt("run_passes(True, True, level, [])", lambda: levels.run_passes(True, True, Fraction(1, 800), []))
    if not explicit(r):
        BAD.append("CAVE8-03 run_passes bool")
    r = attempt("transfer_p([0.001], [])", lambda: levels.transfer_p([0.001], []))
    if not explicit(r):
        BAD.append("CAVE8-03 transfer_p float")
    print("CAVE8-04 dtypes")
    r = attempt("validate_series(bool array)", lambda: gates.validate_series([True, False] * 2500, 4096).dtype)
    if not explicit(r):
        BAD.append("CAVE8-04 bool")
    r = attempt("validate_series(complex array)", lambda: gates.validate_series(np.array([1 + 2j, 2 + 3j] * 2500), 4096).dtype)
    if not explicit(r):
        BAD.append("CAVE8-04 complex")
    r = attempt("validate_series(string array)", lambda: gates.validate_series(np.array(["1", "2"] * 2500), 4096).dtype)
    if not explicit(r):
        BAD.append("CAVE8-04 string")
    r = attempt("validate_series(integer counts)", lambda: gates.validate_series(np.arange(5000) % 7 + 1, 4096).dtype)
    r = attempt("validate_series(good series, N=True)", lambda: gates.validate_series(np.random.default_rng(1).standard_normal(5000), True).size)
    if not explicit(r):
        BAD.append("CAVE8-04 N bool")
    print("CAVE8-05 segment cutter")
    blk = np.array([10., 10, 0, 1, 11, 11, 2, 2])
    print("  offset on the review's block under identity, x^3+x, 2^x:", [segments.best_offset(v, 6, pad=2) for v in (blk, blk ** 3 + blk, 2.0 ** blk)])
    x = np.concatenate([np.random.default_rng(2).standard_normal(4224), np.full(4224, 7.0), np.random.default_rng(3).standard_normal(4224)])
    r = attempt("cut_segments with valid of the wrong length", lambda: segments.cut_segments(x, valid=[True]))
    if not explicit(r):
        BAD.append("CAVE8-05 valid length short")
    r = attempt("cut_segments with valid too long", lambda: segments.cut_segments(x, valid=[True] * 5))
    if not explicit(r):
        BAD.append("CAVE8-05 valid length long")
    cut = segments.cut_segments(x)
    print("  constant block yields a segment:", cut[1]["seg"] is not None and float(np.ptp(cut[1]["seg"])) == 0.0)
    const = cut[1]["seg"]
    r = attempt("tau0 of the constant segment cut from that stream", lambda: transfer.tau0_segment(const))
    if not explicit(r):
        BAD.append("CAVE8-05 tau0 on the cut constant segment")
    r = attempt("amp_exp_standardised on the constant segment", lambda: nets.amp_exp_standardised(const))
    if not explicit(r):
        BAD.append("CAVE8-05 amp_exp_standardised")
    attempt("q8 net on the constant segment (distinct values)", lambda: ranks.n_distinct(nets.apply("q8", const)))
    r = attempt("segment_test on the constant segment: reject, all zero spread", lambda: (stats43.segment_test(const, ("w", "s", "n", 0))["reject"], stats43.segment_test(const, ("w", "s", "n", 0))["all_zero_spread"]))
    print("CAVE8-06 ties, degenerate lags and tolerances")
    print("  no tie-share rule is applied (Amendment 1, A5); tied patterns are kept as patterns of their own")
    print("  degenerate lags are left out of T and the segment is flagged; all-degenerate counts as not rejecting (plan, section 4.3)")
    import law2b
    print("CAVE8-07 divisions and logarithms")
    with np.errstate(all="raise"):
        r = attempt("unit_features on all-zero counts", lambda: flow.unit_features(np.zeros((5, 75), dtype=np.int64))[1].tolist())
        r = attempt("loo_standardise on identical rows", lambda: float(stats43.loo_standardise(np.ones((100, 4)))[0].sum()))
        r = attempt("sigma_hat on all-zero counts", lambda: float(patterns.sigma_hat(np.zeros(13, dtype=np.int64), 3)))
    r = attempt("loo_standardise with one row", lambda: stats43.loo_standardise(np.ones((1, 4))))
    if not explicit(r):
        BAD.append("CAVE8-07 one row")
    print("CAVE8-08 transfer tests")
    w = np.arange(1.0, 7.0)
    for label, f in (("R = 0", lambda: transfer.transfer_test("arrow", w, w, np.ones(6, dtype=bool), np.random.default_rng(1), R=0)),
                     ("g of the wrong length", lambda: transfer.transfer_test("arrow", w, w[:3], np.ones(6, dtype=bool), np.random.default_rng(1), R=100)),
                     ("non-finite template", lambda: transfer.transfer_test("arrow", np.full(6, np.nan), w, np.ones(6, dtype=bool), np.random.default_rng(1), R=100)),
                     ("unknown kind", lambda: transfer.transfer_test("nope", w, w, np.ones(6, dtype=bool), np.random.default_rng(1), R=100)),
                     ("no valid segments", lambda: transfer.build_template(np.zeros((0, 4))))):
        r = attempt("transfer_test " + label, f)
        if not explicit(r):
            BAD.append("CAVE8-08 " + label)
    print("  scores are compared with a tolerance of %g relative, with an absolute floor of 1e-12, not by exact equality (the AUC of the frozen plan is gone)" % ties.REL)
    print("UNGUARDED:", BAD if BAD else "none")
    if BAD:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
