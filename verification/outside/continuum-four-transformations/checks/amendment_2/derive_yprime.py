"""Amendment 2, item B9: the coefficient of y' = g^2 and the time scales of y' and the cascade.

Part 1 (deterministic, trapezoid rule in double precision): the population Spearman (mid-rank) correlation of
(g_t^2, g_(t+k)^2) for a stationary Gaussian AR(1) series g with coefficient c, whose correlation at lag k
is rho = c^k:  rho_S = 12 E[(2 Phi(|X|) - 1)(2 Phi(|Y|) - 1)] - 3, with (X, Y) standard bivariate normal
of correlation rho (the grade of g^2 is 2 Phi(|g|) - 1). The expectation is a 2-D trapezoid sum on [-10, 10] with step 0.004.
The rule: c is the value at which rho_S at lag 16 equals 1/2, found by bisection, rounded down to 4 decimals
so that rho_S is first below 1/2 at lag 16.

Part 2 (sampled, seeds stated): tau0 as the plan defines it, on 32 level-0 fit segments of a 2^19-sample
series, for y' at the derived c, for y' at the earlier c = 2^(-1/32), and for the cascade built as the plan
now states. Seeds use the plan's seed rule with the instrument tag `A2-derive:<case>`, which no test uses.
"""
import hashlib
import math
import sys
import numpy as np

out = []
w = out.append

# ---- Part 1 ----
from scipy.special import erf

H = 0.004
GRID = np.arange(-10.0, 10.0 + H / 2.0, H)          # contains 0, where |x| has its kink
PHI = np.exp(-GRID * GRID / 2.0) / math.sqrt(2.0 * math.pi)
TW = np.full(len(GRID), H)                          # trapezoid weights
TW[0] = TW[-1] = H / 2.0
WPHI = TW * PHI
GRADE = erf(np.abs(GRID) / math.sqrt(2.0))          # 2 Phi(|x|) - 1


def spearman_sq(rho):
    """Trapezoid rule on [-10, 10] with step 0.004 in both variables (Y = rho X + sqrt(1 - rho^2) Z)."""
    if not -1.0 < rho < 1.0:
        raise ValueError("rho must lie in (-1, 1)")
    s = math.sqrt(1.0 - rho * rho)
    inner = np.empty(len(GRID))
    for i in range(0, len(GRID)):
        inner[i] = float(np.dot(WPHI, erf(np.abs(rho * GRID[i] + s * GRID) / math.sqrt(2.0))))
    return 12.0 * float(np.dot(WPHI * GRADE, inner)) - 3.0


def first_lag_below_half(c):
    k = 1
    while spearman_sq(c ** k) >= 0.5:
        k += 1
        if k > 512:
            return 512
    return k


w("== Part 1: population mid-rank autocorrelation of g^2 ==")
w(f"check at rho = 0: {spearman_sq(0.0):.6f} (should be 0); at rho = 0.999999: {spearman_sq(0.999999):.6f} (should be near 1)")
lo, hi = 0.95, 0.9999
for _ in range(40):
    mid = (lo + hi) / 2.0
    if spearman_sq(mid ** 16) < 0.5:
        lo = mid
    else:
        hi = mid
c_new = (lo + hi) / 2.0
c4 = math.floor(c_new * 10000.0) / 10000.0
w(f"derived c (rho_S at lag 16 = 1/2): {c_new:.6f} (rho_S at lag 16 = {spearman_sq(c_new ** 16):.6f}); rounded down to 4 decimals: {c4:.4f}")
w(f"with c = {c4}: rho_S at lags 15, 16, 17 = {spearman_sq(c4 ** 15):.4f}, {spearman_sq(c4 ** 16):.4f}, {spearman_sq(c4 ** 17):.4f}; first lag below 1/2: {first_lag_below_half(c4)}")
c_old = 2.0 ** (-1.0 / 32.0)
w(f"earlier c = 2^(-1/32) = {c_old:.6f}: value correlation c^(2k) = 1/2 at k = 16, but mid-rank rho_S at lag 16 = {spearman_sq(c_old ** 16):.4f}; first lag below 1/2: {first_lag_below_half(c_old)}")

# ---- Part 2 ----
MASTER = 20261121


def rng_for(instrument, split, net, segment, purpose, index):
    s = "|".join(str(v) for v in (MASTER, instrument, split, net, segment, purpose, index))
    return np.random.default_rng(int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:16], 16))


def midranks(x):
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    xs = x[order]
    i = 0
    n = len(x)
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1] == xs[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def tau0_segment(seg):
    r = midranks(seg)
    r = r - r.mean()
    den = float(np.dot(r, r))
    for k in range(1, 513):
        if float(np.dot(r[:-k], r[k:])) / den < 0.5:
            return k
    return 512


def fit_segments(x, n=4096, pad=128):
    block = n + pad
    J = len(x) // block
    k = max(1, J // 32)
    starts = [b * block for b in range(J) if b % k == 0][:32]
    segs = []
    for s0 in starts:
        blk = x[s0:s0 + block]
        r = midranks(blk)
        best, best_o = None, 0
        for o in range(pad + 1):
            seg = r[o:o + n]
            cost = (seg[-1] - seg[0]) ** 2 + ((seg[1] - seg[0]) - (seg[-1] - seg[-2])) ** 2
            if best is None or cost < best:
                best, best_o = cost, o
        segs.append(blk[best_o:best_o + n])
    return segs


def ar1(rng, n, c):
    e = rng.standard_normal(n) * math.sqrt(1.0 - c * c)
    g = np.empty(n)
    g[0] = rng.standard_normal()
    for t in range(1, n):
        g[t] = c * g[t - 1] + e[t]
    return g


def cascade(n, rng, sigma=0.5):
    depth = int(math.ceil(math.log2(n)))
    x = np.ones(1)
    for lev in range(depth):
        wgt = np.exp(sigma * rng.standard_normal(2 ** (lev + 1)) - sigma * sigma / 2.0)
        x = np.repeat(x, 2) * wgt
    return x[:n]


def shift(t):
    return int(math.floor(math.log2(t) + 0.5))


N = 2 ** 19
w("== Part 2: tau0 (median over 32 fit segments) and level shift, 10 seeds each ==")
for label, make in (("y' at derived c", lambda rng: ar1(rng, N, c4) ** 2),
                    ("y' at c = 2^(-1/32)", lambda rng: ar1(rng, N, c_old) ** 2),
                    ("cascade", lambda rng: cascade(N, rng))):
    taus = []
    for s in range(10):
        x = make(rng_for("A2-derive:" + label, "fit", "native", s, "data", 0))
        taus.append(float(np.median([tau0_segment(seg) for seg in fit_segments(x)])))
    w(f"{label}: tau0 by seed {taus}; shifts {[shift(t) for t in taus]}")
sys.stdout.write("\n".join(out) + "\n")
