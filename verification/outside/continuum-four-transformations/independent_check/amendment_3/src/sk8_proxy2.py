"""SK8 proxy (sampled, NOT the plan's statistic): can K5's new positive criterion pass and can it fail?
The plan's flow statistic needs the code under test (surrogate pools, 99,999 random detectors). This proxy keeps only the idea:
a departure profile = z-scores of the order-3 pattern frequencies (6 classes, no ties) of the block-mean series at block sizes 2^0..2^8
against the iid value 1/6, and the cosine between two profiles stands for 'the same departure shape'. numpy and the standard library."""
import hashlib, math, statistics, sys
import numpy as np
ND = statistics.NormalDist()
def rng(tag, i):
    return np.random.default_rng(int(hashlib.sha256(f"A3verify|proxy|{tag}|{i}".encode()).hexdigest()[:16], 16))
def cascade(rg):
    a = np.array([1.0])
    for j in range(19):
        a = np.repeat(a, 2) * np.exp(0.5 * rg.standard_normal(2 ** (j + 1)) - 0.125)
    return a
def ar1(rg, n, c):
    e = rg.standard_normal(n); x = np.empty(n); x[0] = e[0]; s = math.sqrt(1 - c * c)
    # linear recursion by blocks of doubling (fast): use a loop over numpy in chunks via lfilter-free method
    for t in range(1, n):
        x[t] = c * x[t - 1] + s * e[t]
    return x
def midranks(x):
    o = np.argsort(x, kind="stable"); r = np.empty(len(x)); r[o] = np.arange(1, len(x) + 1); return r
def scores(x):
    u = (midranks(x) - 0.5) / len(x)
    return np.array([ND.inv_cdf(float(p)) for p in u])
def profile(x):
    v = []
    for k in range(9):
        b = 2 ** k
        bm = x.reshape(-1, b).mean(1)
        a, c, d = bm[:-2], bm[1:-1], bm[2:]
        code = (a < c).astype(int) * 4 + (c < d).astype(int) * 2 + (a < d).astype(int)
        # six permutation classes are the codes 0,2,3,4,5,7 (codes 1 and 6 are impossible)
        cls = {0: 0, 2: 1, 3: 2, 4: 3, 5: 4, 7: 5}
        cnt = np.zeros(6)
        for cd, i in cls.items():
            cnt[i] = np.sum(code == cd)
        f = cnt / cnt.sum(); m = cnt.sum()
        v.extend(((f - 1 / 6) / math.sqrt((1 / 6) * (5 / 6) / m)).tolist())
    return np.array(v)
def cosine(a, b):
    return float(a @ b / math.sqrt((a @ a) * (b @ b)))
rows = {k: [] for k in ("cascade fit vs cascade verdict (raw)", "cascade fit vs rank-mapped cascade (primary run)", "scores(cascade fit) vs scores(rank-mapped) (amp_scores run)",
                         "cascade fit vs y' (negative)", "cascade fit vs shuffled cascade (negative)")}
for s in range(10):
    cf = cascade(rng("cf", s)); cv = cascade(rng("cv", s)); sh = cascade(rng("sh", s)); np.random.default_rng(s).shuffle(sh)
    yp = ar1(rng("y", s), 2 ** 19, 0.9859) ** 2
    pf = profile(cf)
    rows["cascade fit vs cascade verdict (raw)"].append(cosine(pf, profile(cv)))
    rows["cascade fit vs rank-mapped cascade (primary run)"].append(cosine(pf, profile(midranks(cv))))
    rows["scores(cascade fit) vs scores(rank-mapped) (amp_scores run)"].append(cosine(profile(scores(cf)), profile(scores(midranks(cv)))))
    rows["cascade fit vs y' (negative)"].append(cosine(pf, profile(yp)))
    rows["cascade fit vs shuffled cascade (negative)"].append(cosine(pf, profile(sh)))
for k, v in rows.items():
    print(f"{k}: cosine min {min(v):.3f}, median {sorted(v)[5]:.3f}, max {max(v):.3f}")
# must-fail control: a profile against its own sign flip has cosine -1
p0 = profile(cascade(rng("ctl", 0)))
print(f"control: cosine of a profile with its negative = {cosine(p0, -p0):.3f} (must be -1)")
print("These are proxies. They show whether the shape of the departure survives the map, not the plan's p-values.")
