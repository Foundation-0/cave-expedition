"""Per-segment irreversibility test of PREREG 4.3."""
import numpy as np
import iaaft
import patterns
import seeds


def loo_standardise(V):
    """Row i is standardised by the mean and the (population) standard deviation of the other rows.
    The ddof choice scales every value alike and cannot change a p-value or an AUC.
    Returns (z, degenerate flags)."""
    V = np.asarray(V, dtype=np.float64)
    m = V.shape[0] - 1
    Vc = V - V.mean(axis=0)
    S = Vc.sum(axis=0)
    Q = (Vc ** 2).sum(axis=0)
    mean = (S - Vc) / m
    var = (Q - Vc ** 2) / m - mean ** 2
    scale = Q / V.shape[0]
    deg = ~(var > 1e-12 * scale)
    sd = np.sqrt(np.where(deg, 1.0, var))
    z = np.where(deg, 0.0, (Vc - mean) / sd)
    return z, deg


def make_pool(x, M, rng, kind="iaaft", max_iter=iaaft.MAX_ITER):
    if kind == "iaaft":
        Y, it, cv = iaaft.iaaft_surrogates(x, M, rng, max_iter)
    elif kind == "leaky":
        Y, it, cv = iaaft.leaky_surrogates(x, M, rng)
    else:
        raise ValueError("unknown surrogate kind " + str(kind))
    return np.vstack([np.asarray(x, dtype=np.float64)[None, :], Y]), it, cv


def analyse(x, key, js, M=99, kind="iaaft", d4=False, tie_limit=0.20, max_iter=iaaft.MAX_ITER):
    """key = (instrument, split, net, segment). Pool = real series (row 0) + M surrogates.
    Returns a dict with the counts, standardised Sigma, T, p and flags."""
    x = np.asarray(x, dtype=np.float64)
    rng = seeds.rng_for(*key, "surrogates", 0)
    pool, it, cv = make_pool(x, M, rng, kind, max_iter)
    L = len(js)
    C3 = np.zeros((M + 1, L, 6), dtype=np.int64)
    ties = np.zeros((M + 1, L), dtype=np.int64)
    nwin = np.zeros(L, dtype=np.int64)
    sig = np.zeros((M + 1, L))
    for li, j in enumerate(js):
        c, t, nw = patterns.counts_batch(pool, 3, 2 ** j)
        C3[:, li, :] = c
        ties[:, li] = t
        nwin[li] = nw
        for i in range(M + 1):
            sig[i, li] = patterns.sigma_hat(c[i], 3)
    Z, deg = loo_standardise(sig)
    T = Z.max(axis=1)
    Tr, Ts = T[0], T[1:]
    ge = (Ts >= Tr) | (np.abs(Ts - Tr) <= 1e-12 * np.maximum(np.abs(Ts), np.abs(Tr)))
    n_ge = int(ge.sum())
    tie_frac = float(np.max(ties[0] / nwin))
    tie_excluded = tie_frac > tie_limit
    pn = 1 + n_ge  # p = pn / (M + 1)
    # per-lag counts, only used by the must-fail 'uncorrected best lag' control
    lag_ge = (Z[1:] >= Z[0][None, :]).sum(axis=0)
    res = {"pn": pn, "den": M + 1, "reject": (not tie_excluded) and pn * 20 <= (M + 1),
           "T": float(Tr), "Z": Z, "sigma": sig, "C3": C3, "ties": ties, "nwin": nwin,
           "tie_frac": tie_frac, "tie_excluded": bool(tie_excluded), "degenerate": bool(deg.any()),
           "iters": int(it.sum()), "nconv": int(cv.sum()), "lag_min_pn": int(1 + lag_ge.min()), "js": list(js)}
    if d4:
        C4 = np.zeros((M + 1, L, 24), dtype=np.int64)
        for li, j in enumerate(js):
            C4[:, li, :] = patterns.counts_batch(pool, 4, 2 ** j)[0]
        sig4 = np.array([[patterns.sigma_hat(C4[i, li], 4) for li in range(L)] for i in range(M + 1)])
        Z4, _ = loo_standardise(sig4)
        res["T4"] = float(Z4.max(axis=1)[0])
    return res
