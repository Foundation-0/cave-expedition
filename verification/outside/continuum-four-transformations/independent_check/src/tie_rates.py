"""Sampled check: share of order-3 windows (lag 1) with a tie after b-bit quantization.
AR(1) series of 4,096 samples; uniform bins over the 0.1 to 99.9 percent range (values outside clipped to end bins)
or 2^b equal-count bins. Two seeds. numpy only. No bare assert.
What the amendment leaves unspecified: marginal variance of the AR(1), burn-in, clipping rule, number of series,
what counts as a tie (here: any two of the three values equal), the AR coefficient and scale for the exp series."""
import sys
import numpy as np

NSER = 400
N = 4096


def ar1(rng, phi, n, unit_marginal=True):
    e = rng.standard_normal(n + 500)
    x = np.empty(n + 500)
    x[0] = e[0]
    for t in range(1, n + 500):
        x[t] = phi * x[t - 1] + e[t]
    x = x[500:]
    if unit_marginal:
        x = x / np.sqrt(1.0 / (1.0 - phi * phi))
    return x


def ar1_fast(rng, phi, n):
    # exact stationary start, vectorised through scipy-free recursion using lfilter-like loop
    e = rng.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0] / np.sqrt(1 - phi * phi)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + e[t]
    return x * np.sqrt(1 - phi * phi)  # unit marginal variance


def quant_uniform(x, bits):
    lo, hi = np.percentile(x, [0.1, 99.9])
    nb = 2 ** bits
    q = np.floor((x - lo) / (hi - lo) * nb).astype(np.int64)
    return np.clip(q, 0, nb - 1)


def quant_equal(x, bits):
    nb = 2 ** bits
    r = np.argsort(np.argsort(x, kind="stable"), kind="stable")
    return (r * nb // len(x)).astype(np.int64)


def tie_share(q):
    a, b, c = q[:-2], q[1:-1], q[2:]
    t = (a == b) | (b == c) | (a == c)
    return float(t.mean())


def run(seed):
    rng = np.random.default_rng(seed)
    print(f"seed {seed}")
    for phi in (0.99, 0.999, 0.9999):
        su, se = [], []
        for _ in range(NSER):
            x = ar1_fast(rng, phi, N)
            su.append(tie_share(quant_uniform(x, 8)))
            se.append(tie_share(quant_equal(x, 8)))
        print(f"  AR(1) phi={phi}: 8-bit uniform bins tie share mean {np.mean(su):.3f} (sd {np.std(su):.3f}); "
              f"equal-count bins {np.mean(se):.3f} (sd {np.std(se):.3f})")
    # heavy-tailed: exp of an AR(1); coefficient and scale are not given in the amendment
    for phi in (0.5, 0.9, 0.99):
        for sc in (1.0, 2.0):
            su, se = [], []
            for _ in range(NSER // 2):
                x = np.exp(sc * ar1_fast(rng, phi, N))
                su.append(tie_share(quant_uniform(x, 8)))
                se.append(tie_share(quant_equal(x, 8)))
            print(f"  exp({sc:g}*AR(1)) phi={phi}: uniform {np.mean(su):.3f}, equal-count {np.mean(se):.3f}")


for seed in (20261211, 20261212):
    run(seed)
print("DONE sim_ties")
