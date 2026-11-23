"""Amendment 3, item SK8: the amplitude map of the scale flow and of K5's mapped cascade.

Part 1 (exact bounds, standard library).
- On n values standardised to unit variance every |z| is below sqrt(n), so exp(z) and z^3 are finite for n <= 4,096
  (K1 versions, K2 control), and exp(z) can overflow at n = 2^19 (K5).
- Normal scores Phi^-1((r - 1/2) / n) of mid-ranks r lie within Phi^-1(1 - 1/(2n)) of 0, so exp of them is finite.
  Distinct mid-ranks differ by at least 1, so distinct scores differ by at least sqrt(2 pi)/n (the smallest slope of
  Phi^-1 is sqrt(2 pi), at 1/2). Tied values share a mid-rank and so a score.

Part 2 (sampled, numpy). Seeds from the plan's seed rule with instrument tags `A3-amp:<stream>`, which no test uses.
(a) The old map: exp of the standardised series, on the K5 cascade (2^19 samples, 10 seeds) and on the cascade after
    that map: does it overflow, and how many distinct values survive.
(b) Candidates for the scale flow's second amplitude net, on four streams: AR(1) 0.9 (light tails), the same with 5
    spikes of 1,000 standard deviations (rare large events), the same AR(1) made integer-valued as round(8 z) (ties),
    and the K5 cascade. Maps: cube = y^3 + y with y = x / max|x|; lognormal = exp of the normal scores of the mid-ranks;
    scores = the normal scores themselves (the existing net); ranks = the mid-ranks.
    Measures: the guard (finite, as many distinct values as the input); top1 = share of the sum of squared deviations
    carried by the largest 1 percent of values; r = Pearson correlation between the stream and the mapped stream
    (r = 1 means a linear rescaling, which the flow does not see, so 1 - r measures how much the net can change).
(c) Dependence on one extreme value: the AR(1) stream, and the same with its middle value replaced by 10^6 standard
    deviations. For each map, r between the stream and the mapped stream over the other values.
(d) K5: the mapped cascade must differ from the cascade, and the rank-based nets give the same series for every
    increasing map of the cascade (checked exactly on mid-ranks).
Identical output under python3 -I -B, -I -O -B and -I -B -W error. No bare assert.
"""
import hashlib
import math
import statistics
import sys

import numpy as np

out = []
w = out.append
ND = statistics.NormalDist(0.0, 1.0)
LN_MAX = math.log(sys.float_info.max)

w("Part 1, exact bounds")
w("ln(largest double) = %.6f" % LN_MAX)
for n in (1024, 2048, 4096):
    w("n = %d: |z| < %.1f, exp(z) < %.4g, |z|^3 < %.4g: finite (K1 versions, K2 control)" % (n, math.sqrt(n), math.exp(math.sqrt(n)), math.sqrt(n) ** 3))
w("n = 2^19: |z| < %.2f, above ln(largest double): exp(z) can overflow (old K5 map)" % math.sqrt(2 ** 19))
for n in (2 ** 19, 10 ** 8, 10 ** 12):
    smax = -ND.inv_cdf(1.0 / (2 * n))
    w("n = %.4g: |normal score| <= %.4f, exp(score) <= %.4f, distinct scores differ by >= %.3g" % (n, smax, math.exp(smax), math.sqrt(2 * math.pi) / n))
ok1 = math.sqrt(4096) < LN_MAX < math.sqrt(2 ** 19) and -ND.inv_cdf(1.0 / (2 * 10 ** 12)) < 8

MASTER = 20261121


def rng(case, seed):
    s = "%d|A3-amp:%s|verdict|native|%d|data|0" % (MASTER, case, seed)
    return np.random.default_rng(int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:16], 16))


def cascade(g, n=2 ** 19):
    x = np.ones(1)
    for j in range(19):
        z = g.standard_normal(2 ** (j + 1))
        x = np.repeat(x, 2) * np.exp(0.5 * z - 0.125)
    return x[:n]


def ar1(g, c=0.9, n=2 ** 16):
    e = g.standard_normal(n) * math.sqrt(1.0 - c * c)
    x = np.empty(n)
    x[0] = g.standard_normal()
    for t in range(1, n):
        x[t] = c * x[t - 1] + e[t]
    return x


def standardise(x):
    return (x - x.mean()) / x.std()


def old_map(x):
    z = standardise(x)
    with np.errstate(over="ignore", under="ignore"):
        return np.exp(z)


def old_map_centred(x):
    z = standardise(x)
    with np.errstate(over="ignore", under="ignore"):
        return np.exp(z - (z.max() + z.min()) / 2.0)


def midranks(x):
    u, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    start = np.concatenate(([0], np.cumsum(cnt)[:-1]))
    return (start + (cnt + 1) / 2.0)[inv]


def scores(x):
    """Normal scores Phi^-1((r - 1/2)/n) of mid-ranks, lower half by inv_cdf and the upper half reflected (D1)."""
    n = len(x)
    r = midranks(x)
    vals = np.unique(r)
    table = {}
    for v in vals.tolist():
        lo = v - 0.5
        hi = n - v + 0.5
        table[v] = ND.inv_cdf(lo / n) if lo <= hi else -ND.inv_cdf(hi / n)
    return np.array([table[v] for v in r.tolist()])


def cube(x):
    y = x / np.abs(x).max()
    return y * y * y + y


def lognormal(x):
    return np.exp(scores(x))


def guard(y, x):
    return bool(np.all(np.isfinite(y))) and len(np.unique(y)) == len(np.unique(x))


def top1(v):
    d = (v - v.mean()) ** 2
    k = max(1, len(v) // 100)
    idx = np.argsort(v, kind="stable")[-k:]
    return float(d[idx].sum() / d.sum())


def pearson(a, b):
    return float(np.corrcoef(a, b)[0, 1])


w("")
w("Part 2 (a), the old map on the K5 cascade, 10 seeds (tag A3-amp:cascade)")
over_b = over_net = lost_b = lost_plain = 0
nd_net = []
for s in range(10):
    x = cascade(rng("cascade", s))
    b = old_map_centred(x)
    over_b += bool(standardise(x).max() > LN_MAX)
    over_net += bool(standardise(b).max() > LN_MAX)
    lost_b += not guard(b, x)
    lost_plain += not guard(old_map(x), x)
    nd_net.append(len(np.unique(standardise(b))))
w("exp(z) of the cascade overflows in %d of 10 seeds. Computed directly it loses distinct values in %d of 10, in the centred form exp(z - (max z + min z)/2) in %d of 10" % (over_b, lost_plain, lost_b))
w("exp(z) of the exp-mapped cascade overflows in %d of 10 seeds; after standardising, the exp-mapped cascade keeps %d to %d distinct values of 524,288" % (
    over_net, min(nd_net), max(nd_net)))

w("")
w("Part 2 (b), candidate maps: guard, top1 (share of squared deviations in the largest 1 percent), r (Pearson with the stream)")
g = rng("ar1", 0)
base = ar1(g)
spiky = base.copy()
pos = rng("spikes", 0).choice(len(base), 5, replace=False)
spiky[pos] = spiky[pos] + 1000.0 * base.std()
integer = np.round(8.0 * standardise(base))
casc = cascade(rng("cascade", 0))
streams = (("AR(1) 0.9", base), ("AR(1) 0.9 with 5 spikes", spiky), ("integer-valued AR(1)", integer), ("K5 cascade", casc))
maps = (("cube", cube), ("lognormal", lognormal), ("scores", scores), ("ranks", midranks))
res = {}
w("stream | native top1 | " + " | ".join("%s: guard, top1, r" % m for m, _ in maps))
for name, x in streams:
    row = ["%s | %.4f" % (name, top1(x))]
    for m, f in maps:
        y = f(x)
        res[(name, m)] = (guard(y, x), top1(y), pearson(x, y))
        row.append("%s %.4f %.4f" % res[(name, m)])
    w(" | ".join(row))

w("")
w("Part 2 (c), one extreme value: r over the other values, without and with the middle value replaced by 10^6 standard deviations")
one = base.copy()
k = len(one) // 2
one[k] = 1e6 * base.std()
mask = np.ones(len(one), dtype=bool)
mask[k] = False
dep = {}
for m, f in maps[:2]:
    r0 = pearson(base[mask], f(base)[mask])
    r1 = pearson(one[mask], f(one)[mask])
    dep[m] = (r0, r1)
    w("%s: r = %.6f without, %.6f with (1 - r: %.2e and %.2e)" % (m, r0, r1, 1 - r0, 1 - r1))
lb = lognormal(base)
lo = lognormal(one)
rel = np.abs(lo[mask] / lb[mask] - 1)
w("lognormal: the other values move by at most one rank. Largest relative change of a mapped value %.3g (in the top tail, where one rank moves the score most), share of values changed by more than 0.1 percent %.4f" % (
    float(rel.max()), float(np.mean(rel > 1e-3))))

w("")
w("Part 2 (d), K5: rank-based nets see the same series for every increasing map of the cascade")
cube_c = cube(casc)
rank_c = midranks(casc)
w("scores of the cascade equal scores of its cube map: %s, of its mid-ranks: %s" % (
    bool(np.array_equal(scores(casc), scores(cube_c))), bool(np.array_equal(scores(casc), scores(rank_c)))))
w("mapped cascade candidates, top1 against the cascade's %.4f and r with the cascade: cube %.4f %.4f, lognormal %.4f %.4f, ranks %.4f %.4f" % (
    top1(casc), top1(cube_c), pearson(casc, cube_c), top1(lognormal(casc)), pearson(casc, lognormal(casc)), top1(rank_c), pearson(casc, rank_c)))

# must-fail controls of the guard and of the measures
x0 = np.array([0.0, 1e-17, 2e-17, 1.0])
ctl1 = not guard(np.exp(x0), x0)
x1 = np.array([1.0, 2.0, 1e308])
with np.errstate(over="ignore"):
    ctl2 = not guard(np.exp(x1), x1)
ctl3 = abs(pearson(base, 3.0 * base + 1.0) - 1.0) < 1e-12 and abs(top1(base) - top1(3.0 * base + 1.0)) < 1e-12
w("control: guard flags exp of values 1e-17 apart: %s; flags an overflow: %s; r = 1 and top1 unchanged under a linear rescaling: %s" % (ctl1, ctl2, ctl3))
lognormal_ok = all(res[(n, "lognormal")][0] for n, _ in streams)
good = ok1 and lognormal_ok and ctl1 and ctl2 and ctl3 and res[("K5 cascade", "ranks")][0]
w("DONE amp_maps: %s" % ("all checks hold" if good else "A CHECK FAILED"))
sys.stdout.write("\n".join(out) + "\n")
sys.exit(0 if good else 1)
