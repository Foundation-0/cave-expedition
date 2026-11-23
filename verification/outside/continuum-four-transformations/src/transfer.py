"""Sameness (transfer) tests of PREREG 4.3: aligned levels, arrow and profile features, templates, matched random
detectors, the exact count of distinct detectors, the smallest reachable p, and the adverse rule.

The same machinery serves the scale-flow transfer (flow.py), whose features are entries of a vector too."""
import math
from collections import Counter
from fractions import Fraction
import numpy as np
import ranks
import stats43
import ties

LEVELS = list(range(-4, 6))  # aligned levels -4 .. +5
R_DETECTORS = 99999
ARROW_MIN_LEVELS = 6
PROFILE_MIN_FEATURES = 8
FLOW_MIN_FEATURES = 8
ADVERSE_NUM, ADVERSE_DEN = 1, 40  # 2.5 percent


def tau0_segment(x, cap=512):
    """Smallest lag at which the (biased, about the mean) autocorrelation of the segment's mid-ranks drops below 1/2,
    capped at 512."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 1 or x.size < 2:
        raise ValueError("tau0 needs a 1-D segment of at least 2 samples")
    if not np.all(np.isfinite(x)):
        raise ValueError("tau0 needs finite values")
    n = x.size
    if n > 6000:
        raise ValueError("tau0 uses 64-bit integers and is limited to segments of at most 6,000 samples")
    t = ranks.twice_midrank(x)
    u = n * t - int(t.sum())          # integers: 2 n (r - mean r), so the autocorrelation is exact in integers
    den = int(u @ u)
    if den == 0:
        raise ValueError("tau0 is undefined for a constant segment (it is invalid, section 7)")
    for tau in range(1, min(cap, n - 1) + 1):
        num = int(u[:-tau] @ u[tau:])
        if 2 * num < den:             # "autocorrelation below 1/2", exact
            return tau
    return cap


def segments_constant(s):
    """A segment whose values are all equal carries no order and is invalid (section 7, B7)."""
    s = np.asarray(s)
    if s.size and s.dtype.kind == "f" and not np.all(np.isfinite(s)):
        raise ValueError("a non-finite segment is neither constant nor valid")
    return bool(s.size == 0 or np.all(s == s.flat[0]))


def level_shift_from_tau0(t0):
    """round(log2 tau0), halves rounded up."""
    return int(math.floor(math.log2(t0) + 0.5))


def level_shift(fit_segments):
    """tau0 = median over fit segments of tau0_segment; shift = round half up of log2 tau0."""
    fit_segments = [s for s in fit_segments if s is not None and not segments_constant(s)]
    if not fit_segments:
        raise ValueError("no fit segment with order: tau0 needs at least one non-constant fit segment")
    t0 = float(np.median([tau0_segment(s) for s in fit_segments]))
    return t0, level_shift_from_tau0(t0)


def level_vectors(zu, z1, z23, js, shift):
    """Place the real series' standardised features (1-D arrays over the lags in js) at aligned levels -4 .. +5.
    Returns arrow vector (10,), profile vector (20,) (m1 entries then m23 entries) and the populated mask (10,)
    of levels inside the range of this series' lags."""
    u = np.zeros(10)
    m1 = np.zeros(10)
    m23 = np.zeros(10)
    pop = np.zeros(10, dtype=bool)
    for lev in LEVELS:
        j = lev + shift
        if j in js:
            li = js.index(j)
            k = lev + 4
            u[k], m1[k], m23[k] = zu[li], z1[li], z23[li]
            pop[k] = True
    return u, np.concatenate([m1, m23]), pop


def segment_vectors(C3, js, shift):
    zu, z1, z23 = stats43.arrow_profile_features(C3)
    return level_vectors(zu[0], z1[0], z23[0], js, shift)


def build_template(F):
    """F: (S, D) features of A's fit segments. Mean over segments, scaled to unit length."""
    F = np.asarray(F, dtype=np.float64)
    if F.ndim != 2 or F.shape[0] < 1:
        raise ValueError("template needs a 2-D array with at least one segment")
    if not np.all(np.isfinite(F)):
        raise ValueError("template features must be finite")
    w = F.mean(axis=0)
    nrm = float(np.sqrt(w @ w))
    if not nrm > 0:
        raise ValueError("template has zero length")
    return w / nrm


def distinct_detectors(vals, signs):
    """Exact number D of distinct random detectors that the entries `vals` allow: all permutations (distinct
    arrangements of a multiset), times an independent sign per non-zero entry when signs is True."""
    vals = [float(v) for v in vals]
    m = len(vals)
    if signs:
        cnt = Counter(abs(v) for v in vals)
        nz = sum(1 for v in vals if v != 0.0)
    else:
        cnt = Counter(vals)
        nz = 0
    d = math.factorial(m)
    for c in cnt.values():
        d //= math.factorial(c)
    return d * (1 << nz)


def smallest_reachable_p(R, D):
    """(1 + R / D) / (R + 1), exact: draws identical to w_A tie with it."""
    return (1 + Fraction(R, D)) / (R + 1)


def transfer_test(kind, w, g, pop_mask, rng, R=R_DETECTORS, chunk=20000):
    """One transfer test of template w against B's mean feature vector g (S_B(w) = w . g).
    kind 'arrow': permutation of the entries at jointly populated positions with an independent random sign for each;
    kind 'profile' or 'flow': permutations only. pop_mask: positions populated in both A and B.
    Returns a dict: m (entries permuted), D, p (Fraction), floor (smallest reachable p), n_ge, n_lt, S_A, adverse."""
    if kind not in ("arrow", "profile", "flow"):
        raise ValueError("unknown transfer kind " + str(kind))
    if isinstance(R, (bool, np.bool_)) or not isinstance(R, (int, np.integer)) or R < 1:
        raise ValueError("R must be an int of at least 1")
    w = np.asarray(w, dtype=np.float64)
    g = np.asarray(g, dtype=np.float64)
    pop_mask = np.asarray(pop_mask)
    if w.ndim != 1 or g.shape != w.shape or pop_mask.shape != w.shape or pop_mask.dtype != bool:
        raise ValueError("template, target and population mask must be 1-D arrays of one length (mask of bool)")
    if not (np.all(np.isfinite(w)) and np.all(np.isfinite(g))):
        raise ValueError("template and target must be finite")
    pos = np.flatnonzero(pop_mask)
    m = int(pos.size)
    signs = kind == "arrow"
    S_A = float(w @ g)
    out = {"m": m, "kind": kind, "S_A": S_A}
    if m == 0:
        out.update({"D": 1, "p": Fraction(1), "floor": Fraction(1), "n_ge": R, "n_lt": 0, "adverse": False})
        return out
    wp, gp = w[pos], g[pos]
    S_pop = float(wp @ gp)
    rest = S_A - S_pop  # entries outside the jointly populated set stay in place; they multiply zeros
    D = distinct_detectors(wp, signs)
    n_ge = 0
    done = 0
    while done < R:
        c = min(chunk, R - done)
        perm = np.argsort(rng.random((c, m)), axis=1)
        ww = wp[perm]
        if signs:
            ww = ww * (rng.integers(0, 2, size=(c, m)) * 2 - 1)
        sc = np.einsum("rm,m->r", ww, gp) + rest
        n_ge += int(c - ties.below(sc, S_A).sum())   # a tie counts as at or above, never as below
        done += c
    n_lt = R - n_ge
    out.update({"D": D, "p": Fraction(1 + n_ge, R + 1), "floor": smallest_reachable_p(R, D), "n_ge": n_ge,
                "n_lt": n_lt, "adverse": ADVERSE_DEN * n_lt < ADVERSE_NUM * R})
    return out


def apply_floor(res, kind):
    """Populated-feature floors of section 4.3: fewer than 6 jointly populated levels (arrow) or fewer than 8
    jointly populated features (profile and flow) counts as not rejecting (p = 1, not adverse)."""
    need = ARROW_MIN_LEVELS if kind == "arrow" else PROFILE_MIN_FEATURES
    if res["m"] < need:
        r = dict(res)
        r.update({"p": Fraction(1), "adverse": False, "below_floor": True})
        return r
    r = dict(res)
    r["below_floor"] = False
    return r


def pop_both(popA, popB, per_level=1):
    """Jointly populated mask; per_level entries belong to each level (1 for u, 2 for m1 and m23 in two blocks)."""
    a = np.asarray(popA, dtype=bool)
    b = np.asarray(popB, dtype=bool)
    both = a & b
    if per_level == 1:
        return both
    return np.tile(both, per_level)
