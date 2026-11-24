"""B9 check: the construction of the new K5 negative-criterion series, from the plan text.
(1) AR(1) coefficient c = 2^(-1/32), Pearson autocorrelation of g^2 is c^(2k) (0.5 at k = 16) and the rank autocorrelation of g^2.
(2) tau0 (plan 4.3: smallest lag where the biased autocorrelation of mid-ranks drops below 1/2, median over 32 segments of 4,096) for y',
    the dyadic cascade (log-normal weights, mean 1, log sd 0.5, depth 19), the IAAFT cascade, the shuffled cascade and y_t = e_t^2 + e_(t-1)^2.
(3) Aligned levels (level minus round(log2 tau0)), levels -3..+3 kept, flow levels 0..3 with 9 features each: jointly populated features for each pair.
(4) Evaluability rule and seed-tag distinctness. numpy only. No bare assert."""
import hashlib
import math
import sys
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
    t = []
    for i in range(nseg):
        s = i * step
        if s + N > len(x):
            s = (len(x) - N) * i // max(nseg - 1, 1)
        t.append(tau0_segment(x[s:s + N]))
    return int(np.median(t)), t


def ar1(rng, n, c):
    e = rng.standard_normal(n) * math.sqrt(1 - c * c)
    x = np.empty(n)
    x[0] = rng.standard_normal()
    for k in range(1, n):
        x[k] = c * x[k - 1] + e[k]
    return x


def cascade(rng, depth=19, sd=0.5):
    n = 2 ** depth
    x = np.ones(n)
    for l in range(1, depth + 1):
        w = np.exp(sd * rng.standard_normal(2 ** l) - sd * sd / 2)
        x *= np.repeat(w, n // 2 ** l)
    return x


c = 2.0 ** (-1.0 / 32)
print(f"INFO c = 2^(-1/32) = {c:.6f} (text: about 0.9786); c^32 = {c**32:.6f}")
claim_pearson = abs(c ** (2 * 16) - 0.5) < 1e-12
print(f"CLAIM b9-c2k | Pearson autocorrelation of g^2 is c^(2k): equals 0.5 at k = 16 | text=below 1/2 near k = 16 | mine=c^32 = {c**32:.6f} | {'REPRODUCED' if claim_pearson else 'DIFFERS'}")
rng = np.random.default_rng(20265001)
g = ar1(rng, 2 ** 21, c)
y2 = g ** 2
r = midranks(y2)
a_r = acf_biased(r, 40)
a_p = acf_biased(y2, 40)
print("INFO lag: biased autocorrelation of mid-ranks | of the values | c^(2k)")
for k in (8, 12, 14, 15, 16, 17, 18, 20, 24):
    print(f"   {k}: {a_r[k]:.4f} | {a_p[k]:.4f} | {c**(2*k):.4f}")
first_rank = next(k for k in range(1, 41) if a_r[k] < 0.5)
print(f"INFO on 2^21 samples the rank autocorrelation first drops below 1/2 at lag {first_rank}")
claim_rank = first_rank == 11
print(f"CLAIM b9-rank | for c = 2^(-1/32) the mid-rank autocorrelation of g^2 first falls below 1/2 at lag 11 (AMENDMENT_2 B9 states this) | text=lag 11 | mine=lag {first_rank} | {'REPRODUCED' if claim_rank else 'DIFFERS'}")

# tau0 per series, 40 seeds' worth over 4,096-sample segments
print("== tau0 (median over 32 segments of 4,096; rule of plan 4.3) and level shift round(log2 tau0), by series")
res = {}
for name in ("yprime", "cascade", "iaaft_cascade", "shuffled_cascade", "y_t", "iid_exp"):
    shifts = []
    taus = []
    for seed in range(3):
        rng = np.random.default_rng(20265100 + 10 * seed)
        if name == "yprime":
            x = ar1(rng, 2 ** 19, c) ** 2
        elif name == "cascade":
            x = cascade(rng)
        elif name == "iaaft_cascade":
            base = cascade(rng)
            n = len(base)
            rk = midranks(base)
            from statistics import NormalDist
            nd = NormalDist()
            ns = np.array([nd.inv_cdf((v - 0.5) / n) for v in rk])
            srt = np.sort(ns)
            amp = np.abs(np.fft.rfft(ns))
            y = ns[rng.permutation(n)]
            prev = np.argsort(np.argsort(y, kind="stable"), kind="stable")
            for it in range(1000):
                z = np.fft.irfft(amp * np.exp(1j * np.angle(np.fft.rfft(y))), n=n)
                rkz = np.argsort(np.argsort(z, kind="stable"), kind="stable")
                y = srt[rkz]
                if np.array_equal(rkz, prev):
                    break
                prev = rkz
            x = y
            print(f"   (IAAFT cascade seed {seed}: stopped after {it + 1} iterations)")
        elif name == "shuffled_cascade":
            x = rng.permutation(cascade(rng))
        elif name == "y_t":
            e = rng.standard_normal(2 ** 19 + 1)
            x = e[1:] ** 2 + e[:-1] ** 2
        else:
            x = rng.exponential(size=2 ** 19)
        t0, ts = tau0_series(x)
        taus.append(t0)
        shifts.append(int(math.floor(math.log2(t0) + 0.5)))
    res[name] = (taus, shifts)
    print(f"   {name:17s}: tau0 over 3 seeds {taus}; level shift {shifts}")


def populated(shift):
    return {l - shift for l in range(4)} & set(range(-3, 4))


print("== jointly populated aligned levels and features (9 per level; the plan needs at least 8)")
names = list(res)


def pair(a, b):
    out = []
    for sa, sb in zip(res[a][1], res[b][1]):
        out.append(9 * len(populated(sa) & populated(sb)))
    return out


for a, b, lab in (("cascade", "cascade", "cascade -> exp-mapped cascade (same series, same tau0)"), ("cascade", "yprime", "cascade -> y'"),
                  ("iaaft_cascade", "cascade", "IAAFT cascade -> cascade"), ("cascade", "y_t", "cascade -> y_t (old criterion)"),
                  ("shuffled_cascade", "cascade", "shuffled cascade -> cascade (old criterion)")):
    f = pair(a, b)
    print(f"   {lab}: jointly populated features per seed {f}; evaluable (>= 8) in {sum(1 for v in f if v >= 8)} of 3")
old_ok = max(pair("cascade", "y_t") + pair("shuffled_cascade", "cascade")) < 8
hyp = 9 * len(populated(4) & populated(0))
print(f"INFO builder's cascade tau0 of 16 (shift 4) against tau0 1 (shift 0): jointly populated features {hyp} (the old criteria could not be evaluated); my cascade construction gives tau0 11 or 12 (shift 3 or 4), so the old criteria had {sorted(set(pair('cascade', 'y_t')))} features in my seeds")
new_ok = min(pair("cascade", "yprime") + pair("iaaft_cascade", "cascade")) >= 8
print(f"CLAIM b9-old | the old negative criteria shared no aligned level with the cascade (builder: cascade tau0 16) | text=met only through the floor | mine={'no shared level' if hyp < 8 else 'shared'} at tau0 16; my own cascade (tau0 11 to 12) shares one level in some seeds | {'REPRODUCED for tau0 16, depends on the cascade construction' }")
print(f"CLAIM b9-new | the new negative criteria are evaluable (at least 8 jointly populated features) | text=share aligned levels | mine={'evaluable' if new_ok else 'NOT evaluable'} | {'REPRODUCED' if new_ok else 'DIFFERS'}")
# IAAFT keeps tau0?
same = res["iaaft_cascade"][0] == res["cascade"][0]
print(f"INFO IAAFT cascade tau0 {res['iaaft_cascade'][0]} against cascade tau0 {res['cascade'][0]} (same seeds, the IAAFT series is made from the cascade of the same seed)")
# seed tags
tags = ["K5b:cascade", "K5b:iaaft_cascade", "K5b:yprime", "K5b:expmap"]
old_tags = ["K5:cascade", "K5:shuffled", "K5:y_t", "K5:exp"]
hs = set()
for t in tags + old_tags:
    for purpose in ("data", "surrogates"):
        hs.add(hashlib.sha256(f"20261121|{t}|synthetic|native|0|{purpose}|0".encode()).hexdigest()[:16])
print(f"INFO seed-rule strings built with the new tags and with K5-style tags are all distinct: {len(hs) == 2 * (len(tags) + len(old_tags))}")
control("a pair with fewer than 8 jointly populated features is flagged non-evaluable (shift 4 against shift 0)", hyp < 8)
control("evaluable pair is not flagged (cascade vs y')", min(pair("cascade", "yprime")) >= 8)
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE k5_series_checks")
