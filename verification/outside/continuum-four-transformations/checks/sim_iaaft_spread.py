"""Sampled check on synthetic series only: how far the segment p-value moves when an increasing map is
applied before the IAAFT surrogates are made. Two sets of 12 segments: K3 shots on an AR(1) 0.9 background, and the AR(1) 0.9 background alone
(stationary start), 4,096 samples, segment i with seed 20261130 + i in each set, standardised. 99 surrogates per variant from surrogate seed
20261230 + i (the same for every variant). IAAFT runs a fixed 50 iterations. Statistic: Sigma_hat at
order 3 with tied patterns kept and pseudocount 1/2, lags 2^j with 2 tau <= n/4, standardised within the
pool (leave-one-out), T = max over lags, p = (1 + #{surrogates with T >= real T}) / 100."""
import sys
import numpy as np
from scipy.signal import lfilter

N, M, ITERS, NSEG = 4096, 99, 50, 12
LAGS = [2 ** j for j in range(10) if 2 * 2 ** j <= N // 4]
out = []
w = out.append


def ar1(rng, n, phi):
    e = rng.standard_normal(n)
    e[0] = e[0] / np.sqrt(1.0 - phi * phi)
    return lfilter([1.0], [1.0, -phi], e)


def shots(rng, n):
    bg = ar1(rng, n, 0.9)
    bg = bg / bg.std()
    kern = np.exp(-np.arange(100) / 10.0)
    return bg + 3.0 * np.convolve((rng.random(n) < 0.01).astype(float), kern)[:n]


def iaaft(x, rng):
    amp = np.abs(np.fft.rfft(x))
    srt = np.sort(x)
    s = rng.permutation(x)
    for _ in range(ITERS):
        s = np.fft.irfft(amp * np.exp(1j * np.angle(np.fft.rfft(s))), n=len(x))
        s = srt[np.argsort(np.argsort(s, kind="stable"), kind="stable")]
    return s


def weak_codes(a, b, c):
    """Code each window by the signs of (b-a), (c-b), (c-a): a weak ordering, ties kept (13 used codes)."""
    s1, s2, s3 = np.sign(b - a), np.sign(c - b), np.sign(c - a)
    return ((s1 + 1) * 9 + (s2 + 1) * 3 + (s3 + 1)).astype(int)


def rev_code(code):
    s1, s2, s3 = code // 9 - 1, (code // 3) % 3 - 1, code % 3 - 1
    # reversed window (c, b, a): signs (b-c, a-b, a-c) = (-s2, -s1, -s3)
    return (-s2 + 1) * 9 + (-s1 + 1) * 3 + (-s3 + 1)


REV = np.array([rev_code(k) for k in range(27)])


POSSIBLE = sorted({int(weak_codes(np.array([a]), np.array([b]), np.array([c]))[0])
                   for a in range(3) for b in range(3) for c in range(3)})
if len(POSSIBLE) != 13:
    raise SystemExit("expected 13 weak orderings of 3 values")


def sigma_hat(x, tau):
    n = len(x) - 2 * tau
    codes = weak_codes(x[:n], x[tau:tau + n], x[2 * tau:2 * tau + n])
    cnt = np.bincount(codes, minlength=27).astype(float)
    p = np.zeros(27)
    p[POSSIBLE] = (cnt[POSSIBLE] + 0.5) / (cnt.sum() + 0.5 * 13)
    return float(sum(p[k] * np.log(p[k] / p[REV[k]]) for k in POSSIBLE))


def seg_p(y, seed):
    rng = np.random.default_rng(seed)
    pool = [y] + [iaaft(y, rng) for _ in range(M)]
    S = np.array([[sigma_hat(z, t) for t in LAGS] for z in pool])
    T = np.empty(len(pool))
    for i in range(len(pool)):
        others = np.delete(S, i, axis=0)
        T[i] = np.max((S[i] - others.mean(axis=0)) / others.std(axis=0, ddof=1))
    return (1 + int(np.sum(T[1:] >= T[0] - 1e-12 * max(1.0, abs(T[0]))))) / (M + 1)


for label, maker in (("K3 shots on AR(1) 0.9 (strongly irreversible)", shots),
                     ("AR(1) 0.9 alone (reversible, the null case)", lambda r, n: ar1(r, n, 0.9))):
    d_exp, d_cube = [], []
    w(f"== {label}, {NSEG} segments ==")
    for i in range(NSEG):
        x = maker(np.random.default_rng(20261130 + i), N)
        z = (x - x.mean()) / x.std()
        p0 = seg_p(z, 20261230 + i)
        pe = seg_p(np.exp(z), 20261230 + i)
        pc = seg_p(z ** 3, 20261230 + i)
        d_exp.append(abs(pe - p0))
        d_cube.append(abs(pc - p0))
        w(f"segment {i}: p(x) {p0:.2f}, p(exp x) {pe:.2f}, p(x^3) {pc:.2f}")
    for name, d in (("exp", d_exp), ("cube", d_cube)):
        d = np.array(d)
        w(f"{name}: mean |shift| {d.mean():.3f}, median {np.median(d):.3f}, max {d.max():.2f}, "
          f"segments with shift <= 0.02: {int(np.sum(d <= 0.02 + 1e-12))} of {NSEG}")
w(f"lags used: {LAGS}; 13 tied and untied patterns, pseudocount 1/2 each")
sys.stdout.write("\n".join(out) + "\n")
