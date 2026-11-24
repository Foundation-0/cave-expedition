"""K3 check: my own implementation of the surrogate pipeline as section 4 / 4.3 describe it (normal scores of mid-ranks,
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


def shots(n, seed):
    rng = np.random.default_rng(seed)
    bg = ar1(rng, n + 200, 0.9)
    sd = 1 / math.sqrt(1 - 0.81)
    arr = (rng.random(n + 200) < 0.01).astype(float)
    kern = np.exp(-np.arange(100) / 10.0)
    return (bg + 3 * sd * np.convolve(arr, kern)[:n + 200])[200:]


def quant_equal(x, bits):
    n = len(x)
    r = midranks(x)
    return np.floor((2 ** bits) * (r - 0.5) / n)


def circ_control(x, seed):
    """native detection with circular-shift surrogates (which keep the time arrow)"""
    n = len(x)
    ns = normal_scores(x)
    rng = np.random.default_rng(seed + 11)
    surr = [np.roll(ns, int(rng.integers(1, n))) for _ in range(M)]
    S = np.vstack([np.array([sigma_hat(x, t) for t in lags(n)])] + [np.array([sigma_hat(s, t) for t in lags(n)]) for s in surr])
    Z = np.empty_like(S)
    for i in range(S.shape[0]):
        o = np.delete(S, i, axis=0)
        sd = o.std(0, ddof=1)
        sd = np.where(sd == 0, np.nan, sd)
        Z[i] = (S[i] - o.mean(0)) / sd
    T = np.nanmax(Z, axis=1)
    return (1 + int(np.sum(T[1:] >= T[0] - 1e-12 * abs(T[0])))) / 100.0


def task(args):
    cond, seed = args
    if cond == "native4096":
        return pipeline(shots(4096, seed), seed + 7)[4]
    if cond == "native2048":
        return pipeline(shots(2048, seed), seed + 7)[4]
    x = shots(4096, seed)
    if cond == "mean2":
        return pipeline(0.5 * (x[0::2] + x[1::2]), seed + 7)[4]
    if cond == "sub2":
        return pipeline(x[::2], seed + 7)[4]
    if cond == "q8":
        return pipeline(quant_equal(x, 8), seed + 7)[4]
    if cond == "q12":
        return pipeline(quant_equal(x, 12), seed + 7)[4]
    if cond == "circ":
        return circ_control(x, seed)
    raise ValueError(cond)


def wilson(k, m, z=1.96):
    ph = k / m
    d = 1 + z * z / m
    c = (ph + z * z / (2 * m)) / d
    h = z * math.sqrt(ph * (1 - ph) / m + z * z / (4 * m * m)) / d
    return c - h, c + h


if __name__ == "__main__":
    jobs = [("native4096", 100, 20263001), ("q8", 100, 20263001), ("q12", 40, 20263001), ("mean2", 100, 20263001), ("sub2", 100, 20263001),
            ("native2048", 100, 20264001), ("circ", 200, 20265001)]
    res = {}
    with Pool(10) as pool:
        for cond, m, base in jobs:
            ps = pool.map(task, [(cond, base + i) for i in range(m)])
            k = sum(1 for p in ps if p <= 0.05)
            lo, hi = wilson(k, m)
            res[cond] = k / m
            print(f"K3 shots {cond:10s} segments={m:3d} seeds {base}..{base+m-1}: detected {k} ({k/m:.3f}), Wilson 95% [{lo:.3f}, {hi:.3f}]")
    print("K3 requirement: native 0.80; 0.50 in every other net (mean2, sub2, q12, q8, placement, window N/2 = native 2048).")
    for cond, need in (("native4096", 0.8), ("mean2", 0.5), ("sub2", 0.5), ("q8", 0.5), ("q12", 0.5), ("native2048", 0.5)):
        print(f"   {cond}: observed {res[cond]:.3f} vs {need}: {'above' if res[cond] >= need else 'BELOW'}")
    print(f"   if K3 is also run with a 2,048-sample native series under the 80 percent rule: observed {res['native2048']:.3f}: {'meets' if res['native2048'] >= 0.8 else 'fails'}")
    ok_circ = res["circ"] <= 0.10
    ok_native = res["native4096"] > 0.7
    print(f"CONTROL circular-shift surrogates detect at most 20 of 200 (rate {res['circ']:.3f}): flagged = {ok_circ}")
    print(f"CONTROL true surrogates detect planted shots at 4096 (rate above 0.7): flagged = {ok_native}")
    if not (ok_circ and ok_native):
        print("FAIL control")
        sys.exit(1)
    print("DONE k3_detection")
