"""Per-segment irreversibility test of PREREG 4.3 and the standardised features that the transfer tests use."""
import numpy as np
import iaaft
import nets
import patterns
import ranks
import seeds

REL_TIE = 1e-12  # values within 1e-12 relative of each other count as ties against the real series (section 4.3)


def loo_standardise(V):
    """V: (P, L). Row i is standardised, column by column, by the mean and the (population) standard deviation of
    the other P - 1 rows. The ddof choice scales every value alike and cannot change a p-value or a transfer p-value.
    Zero spread is decided exactly (all other rows equal). Returns (z, degenerate (P, L) bool); z = 0 where degenerate."""
    V = np.asarray(V, dtype=np.float64)
    if V.ndim != 2 or V.shape[0] < 2:
        raise ValueError("need a 2-D array with at least 2 rows (the real series and one surrogate)")
    if not np.all(np.isfinite(V)):
        raise ValueError("non-finite values cannot be standardised")
    P = V.shape[0]
    m = P - 1
    mean = (V.sum(axis=0)[None, :] - V) / m
    diff = V[None, :, :] - mean[:, None, :]  # (i, k, l)
    sq = diff * diff
    idx = np.arange(P)
    sq[idx, idx, :] = 0.0
    var = sq.sum(axis=1) / m
    s = np.sort(V, axis=0)
    vmin, vmax = s[0], s[-1]
    cmin = (V == vmin[None, :]).sum(axis=0)
    cmax = (V == vmax[None, :]).sum(axis=0)
    omin = np.where((V == vmin[None, :]) & (cmin[None, :] == 1), s[1][None, :], vmin[None, :])
    omax = np.where((V == vmax[None, :]) & (cmax[None, :] == 1), s[-2][None, :], vmax[None, :])
    deg = omin == omax
    sd = np.sqrt(np.where(deg, 1.0, var))
    z = np.where(deg, 0.0, (V - mean) / np.where(deg, 1.0, sd))
    return z, deg


def make_pool(x, key, M=99, kind="iaaft"):
    """Pool = real series (row 0, raw values; patterns depend only on order) + M surrogates made from the normal
    scores of x. key = (instrument, split, net, segment). kinds: iaaft (confirmatory), raw and leaky (must-fail)."""
    x = np.asarray(x, dtype=np.float64)
    rng = seeds.rng_for(*key, "surrogates", 0)
    if kind == "iaaft":
        Y, it, cv = iaaft.iaaft_surrogates(x, M, rng)
    elif kind == "raw":
        Y, it, cv = iaaft.raw_surrogates(x, M, rng)
    elif kind == "leaky":
        Y, it, cv = iaaft.leaky_surrogates(x, M, rng)
    else:
        raise ValueError("unknown surrogate kind " + str(kind))
    return np.vstack([x[None, :], Y]), it, cv


def counts3(pool, js):
    """(P, L, 13) order-3 counts of every pool member at lags 2^j, j in js, and the window counts (L,)."""
    P = pool.shape[0]
    C = np.zeros((P, len(js), 13), dtype=np.int64)
    nw = np.zeros(len(js), dtype=np.int64)
    for li, j in enumerate(js):
        c, w = patterns.counts_batch(pool, 3, 1 << j)
        C[:, li, :] = c
        nw[li] = w
    return C, nw


def presence_stats(C3):
    """T and the segment p-value from order-3 counts (P, L, 13), row 0 real. T is the largest standardised
    Sigma_hat over the lags kept (non-degenerate lags), -inf if none. p = (1 + #surrogates with T >= real T) / P
    where P = 100, with 1e-12 relative ties counted against the real series. If every lag of the real series has zero
    spread the segment counts as not rejecting."""
    P = C3.shape[0]
    sig = patterns.sigma_hat(C3, 3)  # (P, L)
    Z, deg = loo_standardise(sig)
    Zm = np.where(deg, -np.inf, Z)
    T = Zm.max(axis=1)
    Tr, Ts = T[0], T[1:]
    if not np.isfinite(Tr):
        return {"pn": P, "den": P, "reject": False, "T": float("-inf"), "Z": Z, "deg": deg, "flag_zero_spread": True,
                "all_zero_spread": True, "sigma": sig}
    fin = np.isfinite(Ts)
    scale = np.maximum(np.abs(np.where(fin, Ts, 0.0)), abs(Tr))
    ge = (Ts >= Tr) | (fin & (np.abs(np.where(fin, Ts, 0.0) - Tr) <= REL_TIE * scale))
    pn = 1 + int(ge.sum())
    # reject iff p = pn / P <= 0.05, exactly, in integers
    return {"pn": pn, "den": P, "reject": pn * 20 <= P, "T": float(Tr), "Z": Z, "deg": deg,
            "flag_zero_spread": bool(deg[0].any()), "all_zero_spread": False, "sigma": sig}


def segment_test(x, key, M=99, kind="iaaft"):
    """Presence test of one segment (series after its net): returns presence_stats plus the counts and pool facts."""
    x = np.asarray(x, dtype=np.float64)
    js = nets.lag_js(len(x))
    pool, it, cv = make_pool(x, key, M, kind)
    C3, nw = counts3(pool, js)
    r = presence_stats(C3)
    r.update({"C3": C3, "js": js, "iters": int(it.sum()), "nconv": int(cv.sum())})
    return r


def arrow_profile_features(C3):
    """From order-3 counts (P, L, 13): standardised u, m1 and m23 (each (P, L)) against the pool. Degenerate
    entries are 0."""
    a1, a2, a3 = patterns.a_features(C3)
    u = a2 - a3
    m1 = np.abs(a1)
    m23 = np.abs(a2 + a3)
    zu, _ = loo_standardise(u)
    z1, _ = loo_standardise(m1)
    z23, _ = loo_standardise(m23)
    return zu, z1, z23
