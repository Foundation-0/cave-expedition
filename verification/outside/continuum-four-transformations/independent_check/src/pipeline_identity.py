"""My own implementation of the surrogate pipeline as section 4 / 4.3 describe it (normal scores of mid-ranks,
IAAFT on the normal scores, 13-pattern Sigma_hat, standardise against the other 99, max over lags, p-value), and exact
identity checks under strictly increasing maps and polarity. numpy only. No bare assert.
Seeds are printed. Series length n = 1024 (lags 2^j with 2 tau <= n/4, so j = 0..7)."""
import sys
from statistics import NormalDist
from itertools import product
import numpy as np

FAILS = []
ND = NormalDist()
M = 99
CAP = 1000


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


def verdict(tag, desc, text, mine, ok):
    print(f"CLAIM {tag} | {desc} | text={text} | mine={mine} | {'REPRODUCED' if ok else 'DIFFERS'}")


def midranks(x):
    """Mid-ranks counted from 1; tied values share the mean of their ranks. Exact in float (halves)."""
    n = len(x)
    order = np.argsort(x, kind="stable")
    xs = x[order]
    r = np.empty(n)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1] == xs[i]:
            j += 1
        r[order[i:j + 1]] = (i + 1 + j + 1) / 2.0
        i = j + 1
    return r


def normal_scores(x):
    n = len(x)
    r = midranks(np.asarray(x, dtype=float))
    return np.array([ND.inv_cdf((float(v) - 0.5) / n) for v in r])


def surrogate(ns, srt, amp, rng):
    y = ns[rng.permutation(len(ns))]
    prev = np.argsort(np.argsort(y, kind="stable"), kind="stable")
    for it in range(CAP):
        Y = np.fft.rfft(y)
        z = np.fft.irfft(amp * np.exp(1j * np.angle(Y)), n=len(ns))
        rk = np.argsort(np.argsort(z, kind="stable"), kind="stable")
        y = srt[rk]
        if np.array_equal(rk, prev):
            break
        prev = rk
    return y


def lags(n):
    return [2 ** j for j in range(10) if 2 * 2 ** j <= n // 4]


valid = sorted({(int(np.sign(b - a)), int(np.sign(c - b)), int(np.sign(c - a))) for a, b, c in product(range(3), repeat=3)})
code = lambda t: 9 * (t[0] + 1) + 3 * (t[1] + 1) + (t[2] + 1)
vcodes = np.array([code(t) for t in valid])
pos = {c: i for i, c in enumerate(vcodes)}
rev_idx = np.array([pos[code((-t[1], -t[0], -t[2]))] for t in valid])
# strict patterns by index for features
def pat_index(t):
    return pos[code(t)]
S012 = pat_index((1, 1, 1)); S210 = pat_index((-1, -1, -1))
S021 = pat_index((1, -1, -1 + 0)) if False else None


def counts(x, tau):
    a, b, c = x[:-2 * tau], x[tau:-tau], x[2 * tau:]
    idx = 9 * (np.sign(b - a).astype(int) + 1) + 3 * (np.sign(c - b).astype(int) + 1) + (np.sign(c - a).astype(int) + 1)
    return np.bincount(idx, minlength=27)[vcodes].astype(float)


def sigma_hat(x, tau):
    cnt = counts(x, tau)
    p = (cnt + 0.5) / (cnt.sum() + 6.5)
    return float(np.sum(p * np.log(p / p[rev_idx])))


def pool_stats(series, n):
    return np.array([[sigma_hat(s, t) for t in lags(n)] for s in series])


def pipeline(x_raw, seed):
    """returns normal scores, pool (100 x n, row 0 = the real series' normal scores), statistic matrix, standardised matrix, p"""
    x_raw = np.asarray(x_raw, dtype=float)
    n = len(x_raw)
    ns = normal_scores(x_raw)
    srt = np.sort(ns)
    amp = np.abs(np.fft.rfft(ns))
    rng = np.random.default_rng(seed)
    surr = [surrogate(ns, srt, amp, rng) for _ in range(M)]
    # the real series' patterns are read from the raw values (ties as recorded); surrogates from their own values
    S = np.vstack([np.array([sigma_hat(x_raw, t) for t in lags(n)])] + [np.array([sigma_hat(s, t) for t in lags(n)]) for s in surr])
    Z = np.empty_like(S)
    for i in range(S.shape[0]):
        o = np.delete(S, i, axis=0)
        Z[i] = (S[i] - o.mean(0)) / o.std(0, ddof=1)
    T = Z.max(1)
    p = (1 + int(np.sum(T[1:] >= T[0] - 1e-12 * abs(T[0])))) / 100.0
    return ns, np.vstack([ns] + surr), S, Z, p


def ar1(rng, n, phi):
    e = rng.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0] / np.sqrt(1 - phi * phi)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    return x


n = 1024
seed_series, seed_sur = 20261401, 20261402
print(f"seeds: series {seed_series}, surrogate {seed_sur}; n={n}; lags {lags(n)}")
rng = np.random.default_rng(seed_series)
x = ar1(rng, n, 0.9)
base = pipeline(x, seed_sur)
print(f"base p = {base[4]}")
maps = {"exp(x)": np.exp(x), "x^3": x ** 3, "x^3+x": x ** 3 + x, "ranks of x": midranks(x), "7x+3": 7 * x + 3}
allok = True
for name, y in maps.items():
    r = pipeline(y, seed_sur)
    same = [np.array_equal(base[0], r[0]), np.array_equal(base[1], r[1]), np.array_equal(base[2], r[2]), np.array_equal(base[3], r[3]), base[4] == r[4]]
    print(f"no ties, {name}: normal scores / pool / statistics / standardised / p identical: {same}")
    allok = allok and all(same)
verdict("id-noties", "pool, features, p identical for x, exp(x), x^3, x^3+x, ranks (no ties, same seeds)", "exactly equal", "exactly equal" if allok else "not equal", allok)

# ties: quantise to 64 levels
xq = np.floor((x - x.min()) / (x.max() - x.min()) * 63.999)
print(f"tied series: {len(np.unique(xq))} distinct values in {n}")
bq = pipeline(xq, seed_sur)
ok_t = True
for name, y in {"exp": np.exp(xq / 8.0), "cube": (xq - 20) ** 3, "ranks": midranks(xq)}.items():
    r = pipeline(y, seed_sur)
    same = [np.array_equal(bq[0], r[0]), np.array_equal(bq[1], r[1]), np.array_equal(bq[2], r[2]), np.array_equal(bq[3], r[3]), bq[4] == r[4]]
    print(f"with ties, {name}: identical: {same}")
    ok_t = ok_t and all(same)
verdict("id-ties", "same identity for a series with exact ties (text: tied values get the same score, mid-ranks)", "exactly equal", "exactly equal" if ok_t else "not equal", ok_t)
print(f"   tied-window share at lag 1 in the real series: {1 - counts(xq,1)[[pos[code(t)] for t in valid if 0 not in t]].sum()/counts(xq,1).sum():.3f}")

# float caveat: a strictly increasing map that creates ties in float arithmetic
xe = 1e-17 * np.arange(1, 9)
print(f"float caveat: exp of values spaced 1e-17 near 0 gives {len(np.unique(np.exp(xe)))} distinct values from {len(np.unique(xe))}")
xc = 1e-120 * (np.arange(1, 9) + 0.0)
print(f"float caveat: cube of values of size 1e-120 gives {len(np.unique(xc ** 3))} distinct values from {len(np.unique(xc))} (underflow)")
control("exp creates ties in float arithmetic (so 'strictly increasing' must hold in floats)", len(np.unique(np.exp(xe))) < len(np.unique(xe)))
control("cube underflow creates ties", len(np.unique(xc ** 3)) < len(np.unique(xc)))

# polarity: -x
nb = pipeline(-x, seed_sur)
nsneg_exact = np.array_equal(nb[0], -base[0])
pool_exact = np.array_equal(nb[1], -base[1])
print(f"polarity: normal scores of -x equal -(normal scores of x) bitwise: {nsneg_exact}; max abs difference {np.abs(nb[0] + base[0]).max():.3e}")
print(f"polarity: pool of -x equals the negated pool bitwise: {pool_exact}; segment p {base[4]} vs {nb[4]}")
verdict("id-polarity-p", "segment p-value equal for x and -x", "equal", f"{base[4]} vs {nb[4]}", base[4] == nb[4])
verdict("id-polarity-pool", "pool of -x is exactly the negated pool of x (K1, line 263)", "exact", "bitwise equal" if pool_exact else "NOT bitwise equal", pool_exact)
# many series: how often is ns(-x) != -ns(x) bitwise
cnt_bad = 0
for k in range(20):
    xx = np.random.default_rng(900 + k).standard_normal(1024)
    if not np.array_equal(normal_scores(-xx), -normal_scores(xx)):
        cnt_bad += 1
print(f"normal scores of -x differ bitwise from -(normal scores of x) in {cnt_bad} of 20 random series of length 1024")

# must-fail control: a non-increasing map must NOT give identical results
xs_ = np.sin(3 * x)
r = pipeline(xs_, seed_sur)
control("a non-monotone map is detected as different", not np.array_equal(base[1], r[1]))
# must-fail: raw-value surrogates (old pipeline) are not identical under exp
def raw_pool_changes():
    def raw_surr(v):
        srt = np.sort(v)
        amp = np.abs(np.fft.rfft(v))
        rg = np.random.default_rng(seed_sur)
        y = v[rg.permutation(len(v))]
        for _ in range(30):
            Y = np.fft.rfft(y)
            z = np.fft.irfft(amp * np.exp(1j * np.angle(Y)), n=len(v))
            y = srt[np.argsort(np.argsort(z))]
        return y
    a = raw_surr(x)
    b = raw_surr(np.exp(x))
    ra = np.argsort(np.argsort(a))
    rb = np.argsort(np.argsort(b))
    return not np.array_equal(ra, rb)
control("old raw-value surrogates are NOT invariant under exp (the problem the change removes)", raw_pool_changes())
if FAILS:
    print("FAILED CONTROLS:", FAILS); sys.exit(1)
print("DONE pipeline_identity")
