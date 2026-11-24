"""Independent derivation of the y' constant c.
Claim to test: for g a stationary Gaussian AR(1) series with lag-k correlation c^k, the population mid-rank autocorrelation of g^2 at lag k
is 12 E[(2 Phi(|X|) - 1)(2 Phi(|Y|) - 1)] - 3, X, Y standard normal with correlation rho = c^k.
Route 1 (this script): Mehler / Hermite expansion. h(x) = 2 Phi(|x|) - 1 is even, so E[h(X) h(Y)] = sum_m rho^m b_m^2 with b_m = E[h(X) psi_m(X)] and
psi_m the orthonormal probabilists' Hermite polynomials (m even only). b_m by a fine one-dimensional trapezoid sum. No two-dimensional integration.
Route 2: a direct simulation of the finite-sample statistic (ranks of g^2, biased autocorrelation) in batches, with a standard error.
numpy only. No bare assert. Seeds are printed."""
import math
import sys
import numpy as np
from math import erf, sqrt

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


# ---- route 1 ----
H = 2e-4
x = np.arange(-12.0, 12.0 + H / 2, H)
phi = np.exp(-x * x / 2) / math.sqrt(2 * math.pi)
Phi = 0.5 * (1.0 + np.vectorize(erf)(np.abs(x) / sqrt(2.0)))   # Phi(|x|)
h = 2 * Phi - 1
M = 600
b = np.zeros(M + 1)
psi_prev = np.zeros_like(x)
psi = np.ones_like(x)
b[0] = np.sum(h * psi * phi) * H
for m in range(0, M):
    nxt = (x * psi - math.sqrt(m) * psi_prev) / math.sqrt(m + 1)
    psi_prev, psi = psi, nxt
    b[m + 1] = np.sum(h * psi * phi) * H
b2 = b ** 2
print(f"INFO b_0 = {b[0]:.10f} (E[h] = 1/2), sum of b_m^2 = {b2.sum():.8f} (E[h^2] = 1/3)")


def r_of_rho(rho):
    m = np.arange(0, M + 1)
    return 12.0 * float(np.sum(b2 * rho ** m)) - 3.0


print(f"INFO r(rho = 1) = {r_of_rho(1.0):.6f} (must be 1), r(0) = {r_of_rho(0.0):.6f} (must be 0)")
print(f"INFO small-rho Spearman check: r(0.5) = {r_of_rho(0.5):.6f}; Pearson-to-Spearman for a plain Gaussian pair would be 6/pi asin(rho/2) = {6/math.pi*math.asin(0.25):.6f} (a different statistic: here the series is |g|, not g)")


def solve(lag, target=0.5):
    lo, hi = 0.5, 0.99999
    for _ in range(200):
        mid = (lo + hi) / 2
        if r_of_rho(mid ** lag) > target:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


c16 = solve(16)
print(f"RESULT route 1: c at which the mid-rank autocorrelation of g^2 equals 1/2 at lag 16: {c16:.6f}")
c_down = math.floor(c16 * 1e4) / 1e4
print(f"RESULT rounded down to 4 decimals: {c_down:.4f}")
for c in (c_down, c16, 0.9852, 2.0 ** (-1 / 32)):
    row = " ".join(f"lag {k}: {r_of_rho(c ** k):.4f}" for k in (14, 15, 16, 17, 18))
    print(f"   c = {c:.5f}: {row}")
first = next(k for k in range(1, 60) if r_of_rho(c_down ** k) < 0.5)
print(f"RESULT with c = {c_down:.4f} the first lag below 1/2 is {first}; at lag 15 it is {r_of_rho(c_down**15):.4f}, at lag 16 {r_of_rho(c_down**16):.4f}, at lag 17 {r_of_rho(c_down**17):.4f}")
# check of the integration scheme itself: halve the step
Hs = H * 2
xs = x[::2]
phis = phi[::2]
hs = h[::2]
b0s = np.sum(hs * phis) * Hs
print(f"INFO step doubled: b_0 = {b0s:.10f}; relative change {abs(b0s - b[0]) / b[0]:.2e}")

# ---- route 2: simulation ----
def midranks(v):
    order = np.argsort(v, kind="stable")
    r = np.empty(len(v))
    r[order] = np.arange(1, len(v) + 1)
    return r


def acf_biased(v, lags):
    v = v - v.mean()
    n = len(v)
    f = np.fft.rfft(v, 2 * n)
    a = np.fft.irfft(f * np.conj(f))[: max(lags) + 1]
    return a[list(lags)] / a[0]


def ar1_batch(rng, n, c, nb):
    e = rng.standard_normal((nb, n)) * math.sqrt(1 - c * c)
    g = np.empty((nb, n))
    g[:, 0] = rng.standard_normal(nb)
    for t in range(1, n):
        g[:, t] = c * g[:, t - 1] + e[:, t]
    return g


LAGS = (15, 16, 17)
for c, seed in ((c_down, 20268001), (0.9852, 20268002)):
    rng = np.random.default_rng(seed)
    n = 2 ** 15
    nb = 400
    vals = []
    g = ar1_batch(rng, n, c, nb)
    for i in range(nb):
        vals.append(acf_biased(midranks(g[i] ** 2), LAGS))
    vals = np.array(vals)
    mean = vals.mean(0)
    se = vals.std(0, ddof=1) / math.sqrt(nb)
    print(f"RESULT route 2 (seed {seed}, c = {c:.4f}, {nb} series of {n}): biased mid-rank autocorrelation at lags 15, 16, 17 = " + ", ".join(f"{m:.4f} +- {s:.4f}" for m, s in zip(mean, se)))
    pop = [r_of_rho(c ** k) for k in LAGS]
    print(f"   population values from route 1: " + ", ".join(f"{p:.4f}" for p in pop) + f"; finite-n biased estimate is lower by about {np.mean(np.array(pop) - mean):.4f} (the mean is removed and the sum is over n - k terms)")
# a larger-n check for the biased shrinkage: n = 2^19 single series
rng = np.random.default_rng(20268003)
g = ar1_batch(rng, 2 ** 19, c_down, 4)
v = np.array([acf_biased(midranks(g[i] ** 2), LAGS) for i in range(4)])
print(f"INFO 4 series of 2^19: lags 15, 16, 17 mean {v.mean(0).round(4)} (+- {v.std(0, ddof=1).round(4) / 2})")
control("route 1 flags a wrong target (c = 2^(-1/32) is not the 1/2 point at lag 16)", abs(r_of_rho((2.0 ** (-1 / 32)) ** 16) - 0.5) > 0.05)
control("route 1 flags that 0.9852 gives r(lag 16) away from 1/2", abs(r_of_rho(0.9852 ** 16) - 0.5) > 0.002)
control("check that c = 0.9859 puts lag 15 above and lag 16 below one half", r_of_rho(c_down ** 15) > 0.5 > r_of_rho(c_down ** 16))
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE yprime_const")
