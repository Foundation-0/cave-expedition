"""Cascade construction as the section 10 text states it, tau0 by seed, y' with c = 0.9859, IAAFT cascade, and the jointly populated features.
Construction (text): start from [1]; for step j = 0..18 draw 2^(j+1) standard normals in order from the series' generator, W = exp(0.5 Z - 0.125),
repeat each element twice, multiply element by element by W; 2^19 elements. tau0 as in plan 4.3: median over 32 fit segments of 4,096 of the smallest lag
where the biased autocorrelation of mid-ranks is below 1/2 (cap 512); segments at block starts 4,224 x 3 x i (offset 0).
Flow levels 0..3, aligned level = l - round_half_up(log2 tau0), levels -3..+3 kept, 9 features per level. numpy only. No bare assert."""
import math
import sys
from statistics import NormalDist
import numpy as np

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


def midranks(x):
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


def acf_biased(v, maxlag=512):
    v = v - v.mean()
    n = len(v)
    f = np.fft.rfft(v, 2 * n)
    a = np.fft.irfft(f * np.conj(f))[: maxlag + 1]
    return a / a[0]


def tau0_segment(seg):
    a = acf_biased(midranks(seg))
    for k in range(1, 513):
        if a[k] < 0.5:
            return k
    return 512


def tau0_series(x, nseg=32, N=4096, step=3 * 4224):
    return int(np.median([tau0_segment(x[i * step:i * step + N]) for i in range(nseg)]))


def shift_of(t):
    return int(math.floor(math.log2(t) + 0.5))


def cascade(rng):
    a = np.ones(1)
    for j in range(19):
        z = rng.standard_normal(2 ** (j + 1))
        w = np.exp(0.5 * z - 0.125)
        a = np.repeat(a, 2) * w
    return a


def ar1(rng, n, c):
    e = rng.standard_normal(n) * math.sqrt(1 - c * c)
    x = np.empty(n)
    x[0] = rng.standard_normal()
    for k in range(1, n):
        x[k] = c * x[k - 1] + e[k]
    return x


def iaaft_whole(x, rng):
    n = len(x)
    nd = NormalDist()
    ns = np.array([nd.inv_cdf((v - 0.5) / n) for v in midranks(x)])
    srt = np.sort(ns)
    amp = np.abs(np.fft.rfft(ns))
    y = ns[rng.permutation(n)]
    prev = np.argsort(np.argsort(y, kind="stable"), kind="stable")
    for it in range(1000):
        z = np.fft.irfft(amp * np.exp(1j * np.angle(np.fft.rfft(y))), n=n)
        rk = np.argsort(np.argsort(z, kind="stable"), kind="stable")
        y = srt[rk]
        if np.array_equal(rk, prev):
            break
        prev = rk
    return y


def pop(s):
    return {l - s for l in range(4)} & set(range(-3, 4))


def joint(sa, sb):
    return 9 * len(pop(sa) & pop(sb))


# mean of the cascade weights is 1: check numerically
w = np.exp(0.5 * np.random.default_rng(1).standard_normal(2_000_000) - 0.125)
print(f"INFO mean of exp(0.5 Z - 0.125) over 2e6 draws: {w.mean():.4f} (text: mean 1); exact value exp(-0.125 + 0.125) = 1")
c = 0.9859
SEEDS = 12
rows = []
for s in range(SEEDS):
    seed = 20269000 + s
    rng = np.random.default_rng(seed)
    x = cascade(rng)
    t_c = tau0_series(x)
    rng2 = np.random.default_rng(seed + 500)
    y = ar1(rng2, 2 ** 19, c) ** 2
    t_y = tau0_series(y)
    rows.append((seed, len(x), t_c, shift_of(t_c), t_y, shift_of(t_y)))
print(f"seeds 20269000..{20269000 + SEEDS - 1} for the cascade, +500 for y'; lengths {set(r[1] for r in rows)} (text 2^19 = 524288)")
for seed, ln, tc, sc, ty, sy in rows:
    print(f"   seed {seed}: cascade tau0 {tc} shift {sc}; y' tau0 {ty} shift {sy}; joint features cascade -> y' {joint(sc, sy)}")
tcs = [r[2] for r in rows]
print(f"RESULT cascade tau0 over {SEEDS} seeds: min {min(tcs)}, max {max(tcs)}, median {int(np.median(tcs))}; shifts {sorted(set(r[3] for r in rows))} (text: 9 to 18 in 10 seeds, shifts 3 and 4)")
tys = [r[4] for r in rows]
print(f"RESULT y' tau0 over {SEEDS} seeds: {sorted(set(tys))}; shifts {sorted(set(r[5] for r in rows))} (text: shift 4 in every seed)")
joint_all = [joint(r[3], r[5]) for r in rows]
print(f"RESULT cascade -> y': jointly populated features {sorted(set(joint_all))}; at least 8 in all seeds: {min(joint_all) >= 8}; at least 2 aligned levels (18 features) in all seeds: {min(joint_all) >= 18}")
# IAAFT cascade
jr = []
for s in range(6):
    seed = 20269000 + s
    rng = np.random.default_rng(seed)
    x = cascade(rng)
    ia = iaaft_whole(x, np.random.default_rng(seed + 900))
    t_i = tau0_series(ia)
    jr.append((seed, rows[s][2], t_i, joint(rows[s][3], shift_of(t_i))))
    print(f"   IAAFT cascade seed {seed}: cascade tau0 {rows[s][2]} (shift {rows[s][3]}), IAAFT cascade tau0 {t_i} (shift {shift_of(t_i)}); joint features IAAFT cascade -> cascade {jr[-1][3]}")
print(f"RESULT IAAFT cascade -> cascade: jointly populated features {sorted(set(j[3] for j in jr))}; at least 8 in all {len(jr)} seeds: {min(j[3] for j in jr) >= 8}")
# the plan's claim of two shared levels for any pair of shifts 3 and 4
print(f"INFO shared aligned levels for shift pairs: (3,3) {len(pop(3) & pop(3))}, (3,4) {len(pop(3) & pop(4))}, (4,4) {len(pop(4) & pop(4))}, (3,5) {len(pop(3) & pop(5))}, (2,5) {len(pop(2) & pop(5))}, (4,0) {len(pop(4) & pop(0))}")
control("a pair of shifts 4 and 0 shares no level and is flagged non-evaluable", joint(4, 0) < 8)
control("the construction has the stated length", all(r[1] == 2 ** 19 for r in rows))
if FAILS or min(joint_all) < 8:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE cascade_tau0")
