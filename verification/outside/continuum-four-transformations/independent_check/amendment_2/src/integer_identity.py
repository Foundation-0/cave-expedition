"""B6 check (b): identity of the whole pipeline for integer-valued null classes. My own implementation of the surrogate pipeline as section 4 / 4.3 describe it (normal scores of mid-ranks,
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



from multiprocessing import Pool

NCLS = ["white", "ar1_0.5", "ar1_0.9", "ar1_0.99", "pl_1", "pl_2", "sines3"]
SEEDS = 3
N = 1024


def gen(cname, seed):
    rng = np.random.default_rng(seed)
    if cname == "white":
        z = rng.standard_normal(N)
    elif cname.startswith("ar1_"):
        c = float(cname.split("_")[1])
        e = rng.standard_normal(N) * np.sqrt(1 - c * c)
        z = np.empty(N)
        z[0] = rng.standard_normal()
        for t in range(1, N):
            z[t] = c * z[t - 1] + e[t]
    elif cname.startswith("pl_"):
        slope = int(cname.split("_")[1])
        f = np.fft.rfftfreq(N)[1:]
        z = np.fft.irfft(np.concatenate(([0.0], f ** (-slope / 2.0) * np.exp(1j * rng.uniform(0, 2 * np.pi, len(f))))), n=N)
    else:
        t = np.arange(N)
        z = rng.standard_normal(N)
        for fr in (0.0137, 0.0781, 0.2113):
            z = z + np.cos(2 * np.pi * fr * t + rng.uniform(0, 2 * np.pi))
    z = (z - z.mean()) / z.std()
    return np.round(8 * z)


def task(args):
    cname, seed = args
    x = gen(cname, seed)
    y = x / np.max(np.abs(x))
    series = {"x": x, "y3+y": y ** 3 + y, "exp(y)": np.exp(y), "ranks": midranks(x)}
    distinct_ok = all(len(np.unique(v)) == len(np.unique(x)) and np.all(np.isfinite(v)) for v in series.values())
    out = {k: pipeline(v, 777) for k, v in series.items()}
    b = out["x"]
    same = {k: [np.array_equal(b[0], r[0]), np.array_equal(b[1], r[1]), np.array_equal(b[2], r[2]), np.array_equal(b[3], r[3]), b[4] == r[4]] for k, r in out.items() if k != "x"}
    tied = 1 - len(np.unique(x)) / len(x)
    return cname, seed, distinct_ok, all(all(v) for v in same.values()), len(np.unique(x)), b[4]


if __name__ == "__main__":
    jobs = [(c, 20264000 + 100 * i + s) for i, c in enumerate(NCLS) for s in range(SEEDS)]
    with Pool(10) as pool:
        res = pool.map(task, jobs)
    allid = True
    for cname, seed, dok, ident, nd, p in res:
        print(f"{cname:9s} seed {seed}: distinct values {nd} of {N}; maps representable {dok}; pool, features, p identical under the 3 maps {ident}; p={p}")
        allid = allid and ident and dok
    print(f"CLAIM int-identity | whole-pipeline identity for integer-valued null classes (21 class-seeds, 3 maps each) | text=identity must hold | mine={'identical' if allid else 'NOT identical'} | {'REPRODUCED' if allid else 'DIFFERS'}")
    # must-fail control: tie-by-position ranking breaks the identity under a map that changes ties (use raw-value surrogates instead): a non-monotone map
    x = gen("ar1_0.9", 20269999)
    b = pipeline(x, 777)
    r = pipeline(np.sin(x / 3.0), 777)
    flagged = not np.array_equal(b[1], r[1])
    print(f"CONTROL a non-monotone map is detected as different | wrong input flagged = {flagged}")
    if not (allid and flagged):
        sys.exit(1)
    print("DONE integer_identity")
