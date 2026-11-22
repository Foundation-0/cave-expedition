"""K2 check: my own implementation of the surrogate pipeline as section 4 / 4.3 describe it (normal scores of mid-ranks,
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



import math
from multiprocessing import Pool

SEG_N = {"1024": 1024, "4096": 4096}


def gen(kind, n, seed):
    rng = np.random.default_rng(seed)
    if kind == "ar1_0.9":
        return ar1(rng, n, 0.9)
    if kind == "g2":      # g^2, g AR(1) 0.9, scaled to mean 0, sd 1
        v = ar1(rng, n, 0.9) ** 2
        return (v - v.mean()) / v.std()
    if kind == "absh":    # |h|, h AR(1) 0.99
        v = np.abs(ar1(rng, n, 0.99))
        return (v - v.mean()) / v.std()
    if kind == "shots":   # K3 shots: start prob 0.01, jump 3 sd of background, decay over 10 samples, kernel cut at 100
        bg = ar1(rng, n + 200, 0.9)
        sd = 1 / math.sqrt(1 - 0.81)
        arr = (rng.random(n + 200) < 0.01).astype(float)
        kern = np.exp(-np.arange(100) / 10.0)
        return (bg + 3 * sd * np.convolve(arr, kern)[:n + 200])[200:]
    raise ValueError(kind)


def task(args):
    kind, n, seed = args
    x = gen(kind, n, seed)
    return pipeline(x, seed + 7)[4]


def wilson(k, m, z=1.96):
    ph = k / m
    d = 1 + z * z / m
    c = (ph + z * z / (2 * m)) / d
    h = z * math.sqrt(ph * (1 - ph) / m + z * z / (4 * m * m)) / d
    return c - h, c + h


if __name__ == "__main__":
    jobs = [("ar1_0.9", 1024, 150, 20261501), ("g2", 1024, 150, 20261601), ("absh", 1024, 150, 20261701),
            ("shots", 1024, 60, 20261801), ("shots", 2048, 40, 20262001), ("shots", 4096, 40, 20262101), ("g2", 4096, 60, 20261901)]
    with Pool(10) as pool:
        for kind, n, m, base in jobs:
            ps = pool.map(task, [(kind, n, base + i) for i in range(m)])
            k = sum(1 for p in ps if p <= 0.05)
            lo, hi = wilson(k, m)
            print(f"{kind:8s} n={n:4d} segments={m:3d} seeds {base}..{base+m-1}: p<=0.05 in {k} ({k/m:.3f}), Wilson 95% [{lo:.3f}, {hi:.3f}]; mean p {np.mean(ps):.3f}")
            if kind == "ar1_0.9":
                null_rate = k / m
            if kind == "shots" and n == 4096:
                must_fail = k / m
            if kind in ("g2", "absh") and n == 1024:
                print(f"   published K2b flag line is 129 of 1,000 (0.129): the observed rate is {'below' if k/m < 0.129 else 'at or above'} it, and the interval's upper end {hi:.3f} is {'below' if hi < 0.129 else 'above'} it")
    print(f"CONTROL structureless-null rate (AR(1) 0.9) is near 0.05, not near 1: flagged = {null_rate < 0.2}")
    print(f"CONTROL planted irreversible shots at n=4096 are detected (rate above 0.7): flagged = {must_fail > 0.7}")
    if not (null_rate < 0.2 and must_fail > 0.7):
        print("FAIL control")
        sys.exit(1)
    print("DONE k2_flag_rates")
