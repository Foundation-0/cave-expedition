import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src")); sys.path.insert(0, HERE)
from fractions import Fraction
import numpy as np
import nets, patterns, presence, segments, seeds, stats43, transfer
from kcommon import header, summary

checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok)))
    print("%-4s %s %s" % ("PASS" if ok else "FAIL", name, detail))


def main():
    header("X1", "extra exact checks of the plan's own arithmetic and of the small functions (not a section 10 test)")
    # plan arithmetic
    check("plan 9: smallest Holm threshold 0.05/28", Fraction(1, 20) / 28 == Fraction(1, 560), "= %.5f" % (1 / 560))
    for S, claimed in ((12, 5), (32, 7)):
        need = min(K for K in range(S + 1) if presence.presence_p(K, S) <= Fraction(1, 560))
        check("plan 9: K needed to reach 0.00179 at S=%d is %d" % (S, claimed), need == claimed,
              "computed %d; p(K=%d)=%.6f, p(K=%d)=%.6f" % (need, claimed - 1, float(presence.presence_p(claimed - 1, S)), claimed, float(presence.presence_p(claimed, S))))
    check("plan 9: 0.05^12 = 2.4e-16 and 0.05^32 = 2.3e-42", abs(float(presence.presence_p(12, 12)) / 2.4e-16 - 1) < 0.02 and abs(float(presence.presence_p(32, 32)) / 2.3e-42 - 1) < 0.05)
    check("plan 6: 1 percent excess point is K=4 at S=12", presence.excess_point(12) == 4, "computed %d" % presence.excess_point(12))
    check("plan 6: 1 percent excess point is K=6 at S=32", presence.excess_point(32) == 6, "computed %d" % presence.excess_point(32))
    k200 = min(K for K in range(202) if presence.binom_tail(200, K) <= Fraction(1, 100))
    check("plan K2: 99 percent bound for 200 draws is 0.086", Fraction(k200 - 1, 200) <= Fraction(86, 1000) < Fraction(k200, 200), "smallest K with tail <= 0.01 is %d, so rates up to %d/200 = %.3f are inside the bound" % (k200, k200 - 1, (k200 - 1) / 200))
    p18 = presence.binom_tail(200, 18)
    print("note: P(Binomial(200, 0.05) >= 18) = %.4f, so a rate of 0.086 or less is a %.4f chance event per class; with 21 classes the chance that at least one calibrated class is flagged is %.3f" % (float(p18), float(p18), 1 - (1 - float(p18)) ** 21))
    print("note: 0.086 equals 0.05 + 2.326 * sqrt(0.05 * 0.95 / 200) = %.4f, the normal approximation" % (0.05 + 2.326 * (0.05 * 0.95 / 200) ** 0.5))
    check("plan 6: control rule at S=12 accepts K=1, rejects K=2", presence.control_absent(1, 12) and not presence.control_absent(2, 12))
    check("plan 6: control rule at S=32 accepts K=3, rejects K=4", presence.control_absent(3, 32) and not presence.control_absent(4, 32))
    # Holm
    h = presence.holm({"a": Fraction(5, 1000), "b": Fraction(10, 1000), "c": Fraction(30, 1000), "d": Fraction(40, 1000)}, m=4)
    check("Holm textbook case (m=4)", [h[k][0] for k in "abcd"] == [True, True, False, False])
    h = presence.holm({"x": Fraction(1, 560), "y": Fraction(2, 560)})
    check("Holm m=28: p = 1/560 rejected, 2/560 not", h["x"][0] and not h["y"][0])
    h = presence.holm({"x": Fraction(1, 560) + Fraction(1, 10 ** 9)})
    check("Holm m=28: p just above 1/560 not rejected", not h["x"][0])
    check("combination rule: largest p over runs", presence.combine_runs([Fraction(1, 100), Fraction(1, 10), Fraction(1, 1000)]) == Fraction(1, 10))
    # patterns and exact statistic
    c, t, nw = patterns.counts_one(np.array([3.0, 1.0, 2.0]), 3, 1)
    check("plan 4: (a,b,c) with b<c<a is pattern 201", c[patterns.tables(3)[4].index("201")] == 1 and c.sum() == 1)
    c, t, nw = patterns.counts_one(np.array([1.0, 1.0, 2.0, 3.0]), 3, 1)
    check("tied window dropped and counted", t == 1 and c.sum() == 1 and nw == 2)
    # segment rule
    s, J, k = segments.select_blocks(32 * 4224)
    check("segment rule: 32 blocks -> k=1, 32 selected", k == 1 and len(s) == 32 and s[1] == 4224)
    s, J, k = segments.select_blocks(100 * 4224)
    check("segment rule: 100 blocks -> k=3, 32 selected, last block index 93", k == 3 and len(s) == 32 and s[-1] == 93 * 4224)
    s, J, k = segments.select_blocks(20 * 4224)
    check("segment rule: 20 blocks -> 20 selected", k == 1 and len(s) == 20)
    rng = seeds.rng_for("X1", "synthetic", "native", 0, "data", 0)
    blk = rng.standard_normal(4096 + 128) * 5
    o = 37
    blk[o + 4095] = blk[o]
    blk[o + 1] = blk[o] + 0.25
    blk[o + 4094] = blk[o + 4095] - 0.25
    check("segment rule: planted best offset is found", segments.best_offset(blk, 4096) == 37)
    x = rng.standard_normal(8000)
    a = segments.select_blocks(len(x))
    b = segments.select_blocks(len(x))
    check("segment rule: block choice depends on length only", a == b)
    # nets
    check("net block mean by 2", np.array_equal(nets.block_mean(np.arange(6.0), 2), [0.5, 2.5, 4.5]))
    check("net lag ranges: native 10, bm2 9, bm4 8, sub2 9", [len(nets.lag_js(n)) for n in ("native", "bm2", "bm4", "sub2")] == [10, 9, 8, 9])
    q = nets.quantize(rng.standard_normal(4096), 8)
    check("net quantize 8 bits: at most 256 levels, integer valued", len(np.unique(q)) <= 256 and np.array_equal(q, np.round(q)))
    w = nets.whiten(synth_ar := np.cumsum(rng.standard_normal(4096)) * 0 + np.convolve(rng.standard_normal(4096 + 9), np.ones(10) / 10, "valid"))
    pg0 = np.abs(np.fft.rfft(synth_ar)) ** 2
    pg1 = np.abs(np.fft.rfft(w)) ** 2
    check("net whitening flattens a coloured spectrum", np.std(np.log(pg1[50:2000])) < np.std(np.log(pg0[50:2000])) , "log-periodogram sd %.2f -> %.2f" % (np.std(np.log(pg0[50:2000])), np.std(np.log(pg1[50:2000]))))
    # tau0
    check("tau0: white noise gives 1, a ramp is capped at 512", transfer.tau0_segment(rng.standard_normal(4096)) == 1 and transfer.tau0_segment(np.arange(4096.0)) == 512)
    # features: u flips under reversal, unchanged under polarity flip; m1, m23 unchanged by both
    y = np.stack([rng.standard_normal(4096) + np.convolve(rng.standard_normal(4096 + 3), np.ones(4) / 4, "valid") for _ in range(30)])
    y[:, 1:] += 0.3 * np.maximum(y[:, :-1], 0)  # asymmetric on purpose
    js = list(range(10))
    def feats(Y):
        C = np.stack([patterns.counts_batch(Y, 3, 2 ** j)[0] for j in js], axis=1)
        return transfer.t3_features(C, js, 3)
    f0, fr, ff = feats(y), feats(y[:, ::-1].copy()), feats(-y)
    idx_u = [i for i in range(30) if i % 3 == 0]
    idx_m = [i for i in range(30) if i % 3 != 0]
    active = np.any(f0 != 0, axis=0)
    check("features: u changes sign under reversal", np.allclose(fr[:, idx_u], -f0[:, idx_u], atol=1e-9) and np.any(f0[:, idx_u] != 0))
    check("features: u unchanged by polarity flip", np.allclose(ff[:, idx_u], f0[:, idx_u], atol=1e-9))
    check("features: m1 and m23 unchanged by reversal and by flip", np.allclose(fr[:, idx_m], f0[:, idx_m], atol=1e-9) and np.allclose(ff[:, idx_m], f0[:, idx_m], atol=1e-9))
    check("features: levels outside the range are zero", not np.any(f0[:, :3 * 1]) and np.any(f0[:, 3 * 4:3 * 5]), "shift 3 -> level -4 is lag 2^-1, absent")
    z, deg = stats43.loo_standardise(np.arange(10.0)[:, None] ** 2)
    others = np.delete(np.arange(10.0) ** 2, 4)
    check("leave-one-out standardisation by hand", abs(z[4, 0] - (16.0 - others.mean()) / others.std()) < 1e-12)
    ok = all(c[1] for c in checks)
    summary("X1", "PASS" if ok else "FAIL", "%d of %d checks pass" % (sum(1 for c in checks if c[1]), len(checks)))


if __name__ == "__main__":
    main()
