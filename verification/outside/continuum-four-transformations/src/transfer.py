"""Sameness (transfer) test of PREREG 4.3: features, aligned lag levels, template, permutation null."""
from fractions import Fraction
import numpy as np
import stats43

LEVELS = list(range(-4, 6))  # aligned levels -4 .. +5, 10 levels x 3 features = 30


def tau0_segment(x, cap=512):
    """Smallest lag at which the autocorrelation of the rank-transformed segment drops below 1/2 (capped at 512).
    Ranks by stable argsort (ties by position); autocorrelation about the mean, divided by the lag-0 sum."""
    x = np.asarray(x, dtype=np.float64)
    r = np.argsort(np.argsort(x, kind="stable"), kind="stable").astype(np.float64)
    r -= r.mean()
    den = float(r @ r)
    for tau in range(1, cap + 1):
        if float(r[:-tau] @ r[tau:]) / den < 0.5:
            return tau
    return cap


def level_shift(segments):
    """tau0 = median over fit segments; shift = round(log2 tau0) (halves round up)."""
    t0 = float(np.median([tau0_segment(s) for s in segments]))
    return t0, int(np.floor(np.log2(t0) + 0.5))


def t3_features(C3, js, shift, arrow_blind=False):
    """C3: (P, L, 6) counts at lags 2^js, row 0 the real series. Returns (P, 30).
    arrow_blind=True is the MUST-FAIL variant that replaces u by |u|."""
    n = C3.astype(np.float64) + 0.5
    ln = np.log(n)
    a1 = ln[..., 0] - ln[..., 5]  # 012 / 210
    a2 = ln[..., 1] - ln[..., 3]  # 021 / 120
    a3 = ln[..., 2] - ln[..., 4]  # 102 / 201
    u = a2 - a3
    if arrow_blind:
        u = np.abs(u)
    raw = [u, np.abs(a1), np.abs(a2 + a3)]
    z = [stats43.loo_standardise(v)[0] for v in raw]
    P = C3.shape[0]
    out = np.zeros((P, 30))
    for lev in LEVELS:
        j = lev + shift
        if j in js:
            li = js.index(j)
            for f in range(3):
                out[:, (lev + 4) * 3 + f] = z[f][:, li]
    return out


def build_template(F_fit_real):
    """F_fit_real: (S, 30) real-series features of A's fit segments. Mean, scaled to unit length."""
    w = np.asarray(F_fit_real).mean(axis=0)
    nrm = float(np.sqrt(w @ w))
    if not nrm > 0:
        raise ValueError("template has zero length")
    return w / nrm


def _auc2(F, W):
    """F: (S, P, 30) with row 0 real; W: (30, c). Integer AUC numerators, summed over segments: shape (c,).
    Per segment: 2 * #(real > surrogate) + #(real == surrogate); AUC = total / (2 * M * S)."""
    S, P, D = F.shape
    sc = (F.reshape(S * P, D) @ W).reshape(S, P, -1)
    real = sc[:, 0:1, :]
    sur = sc[:, 1:, :]
    return (2 * (real > sur).sum(axis=1) + (real == sur).sum(axis=1)).sum(axis=0)


def transfer_test(w, F, rng, R=9999, chunk=400):
    """Template w against features F (S, P, 30) of instrument B's verdict segments.
    Returns dict: auc, p (exact fraction), q025 of the permuted AUCs, count of permuted AUC >= real."""
    S, P, D = F.shape
    M = P - 1
    den = 2 * M * S
    tot = int(_auc2(F, np.asarray(w)[:, None])[0])
    ge = 0
    allv = []
    done = 0
    while done < R:
        c = min(chunk, R - done)
        perm = np.argsort(rng.random((c, D)), axis=1)
        v = _auc2(F, np.asarray(w)[perm].T)
        ge += int((v >= tot).sum())
        allv.append(v)
        done += c
    allv = np.concatenate(allv)
    return {"auc": tot / den, "p": Fraction(1 + ge, R + 1), "q025": float(np.percentile(allv / den, 2.5)),
            "n_ge": ge, "perm_mean": float((allv / den).mean())}
