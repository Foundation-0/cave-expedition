"""Sampled check of the K3 shot-process claims: u at lags 1,2,4,8,16 over 2^20 samples
(amendment: +0.025, +0.062, +0.095, +0.072, +0.027), per-4096-segment mean/sd at lag 4 (1.21),
sign change under reversal and not under polarity flip.
Shot process as the plan words it: exponential shots (instant rise, decay over 10 samples, rate 0.01 per sample,
height 3 background standard deviations) in AR(1) background with coefficient 0.9.
Unspecified: arrival model (Bernoulli or Poisson), overlap rule (sum or max), decay meaning (e-folding or finite support),
background sd convention, whether the background is the marginal sd. Variants listed. numpy only."""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

L = 2 ** 20
LAGS = (1, 2, 4, 8, 16)


def u_stat(x, tau):
    a, b, c = x[:-2 * tau], x[tau:-tau], x[2 * tau:]
    n021 = np.sum((a < c) & (c < b))   # ranks a=0,b=2,c=1
    n120 = np.sum((c < a) & (a < b))   # a=1,b=2,c=0
    n102 = np.sum((b < a) & (a < c))   # a=1,b=0,c=2
    n201 = np.sum((b < c) & (c < a))   # a=2,b=0,c=1
    return float(np.log((n021 + .5) / (n120 + .5)) - np.log((n102 + .5) / (n201 + .5)))


def ar1(rng, n, phi):
    e = rng.standard_normal(n)
    # AR(1) via lfilter-free loop in chunks is slow; use exact recursion with numpy cumulative trick
    x = np.empty(n)
    x[0] = e[0] / np.sqrt(1 - phi * phi)
    # blockwise recursion
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    return x


def make(rng, variant):
    phi = 0.9
    bg = ar1(rng, L, phi)
    marg_sd = 1 / np.sqrt(1 - phi * phi)
    if variant["bgnorm"] == "marginal":
        bg = bg / marg_sd
        sd = 1.0
    else:  # unit innovations, "background standard deviation" read as the marginal sd of that series
        sd = marg_sd
    height = 3 * sd
    # shots
    if variant["arrival"] == "bernoulli":
        arr = (rng.random(L) < 0.01).astype(float)
    else:
        arr = rng.poisson(0.01, L).astype(float)
    kern_len = 200 if variant["decay"] == "efold" else 10
    k = np.arange(kern_len)
    kern = np.exp(-k / 10.0) if variant["decay"] == "efold" else np.exp(-k / 10.0)
    if variant["overlap"] == "sum":
        shots = np.convolve(arr, kern)[:L] * height
    else:  # max: each shot contributes its own tail, take the maximum
        idx = np.nonzero(arr)[0]
        shots = np.zeros(L)
        for i in idx:
            m = min(kern_len, L - i)
            shots[i:i + m] = np.maximum(shots[i:i + m], kern[:m])
        shots *= height
    return bg + shots


rng = np.random.default_rng(20261241)
variants = [
    dict(bgnorm="marginal", arrival="bernoulli", decay="efold", overlap="sum"),
    dict(bgnorm="marginal", arrival="bernoulli", decay="efold", overlap="max"),
    dict(bgnorm="unit_innov", arrival="bernoulli", decay="efold", overlap="sum"),
    dict(bgnorm="marginal", arrival="poisson", decay="efold", overlap="sum"),
]
print("amendment: u at lags 1,2,4,8,16 = +0.025, +0.062, +0.095, +0.072, +0.027; per-segment mean/sd at lag 4 = 1.21")
for seed in (20261241, 20261242):
    for v in variants:
        rng = np.random.default_rng(seed)
        x = make(rng, v)
        us = [u_stat(x, t) for t in LAGS]
        # per segment lag 4
        segs = x.reshape(-1, 4096)
        su = np.array([u_stat(s, 4) for s in segs])
        print(f"seed {seed} {v['bgnorm']:10s} {v['arrival']:9s} {v['overlap']:3s}: u = " +
              ", ".join(f"{u:+.3f}" for u in us) +
              f" | lag-4 segments: mean {su.mean():+.4f} sd {su.std(ddof=1):.4f} mean/sd {su.mean()/su.std(ddof=1):.2f}"
              f" mean/(sd/sqrt(256)) {su.mean()/(su.std(ddof=1)/16):.1f}")
        if seed == 20261241 and v is variants[0]:
            xr = x[::-1].copy()
            xn = -x
            print("   reversal: u = " + ", ".join(f"{u_stat(xr, t):+.3f}" for t in LAGS) +
                  " | polarity: u = " + ", ".join(f"{u_stat(xn, t):+.3f}" for t in LAGS))
print("DONE sim_shots")
