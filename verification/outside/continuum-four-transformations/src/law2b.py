"""Listed transformation instances of PREREG section 12a (Law 2b), as separate named functions.

NOT called by the confirmatory path: no other module imports this one (units_check.py verifies it). The instances are
fixed here so that they are available to the fixed rule of section 12a; their statistics are checked against hand-made
counts only. Window names: W whitening, Q Bregman (quadratic generator), H Hellinger, F white floor, M max-plus,
D first differences, O4 order 4, E event-rich domain, B block maxima, R normal scores before block averaging."""
import math
import numpy as np
import patterns
import keys
import ranks


# T1 gauge: W ------------------------------------------------------------------------------------------------
def running_median_reflect(v, width=33):
    """Running median over `width` neighbouring values; the window is reflected at both ends (READING: numpy 'reflect',
    which does not repeat the edge value; see AMENDMENTS_NEEDED.md)."""
    h = width // 2
    padded = np.pad(np.asarray(v, dtype=np.float64), h, mode="reflect")
    win = np.lib.stride_tricks.sliding_window_view(padded, width)
    return np.median(win, axis=1)


def whiten_W(x):
    """Zero-phase whitening: divide the Fourier transform by the square root of the running median of |X(f)|^2 over 33
    neighbouring frequencies, set the zero frequency to 0, transform back."""
    x = np.asarray(x, dtype=np.float64)
    X = np.fft.rfft(x)
    med = running_median_reflect(np.abs(X) ** 2, 33)
    if not np.all(med > 0):
        raise ValueError("whitening needs a positive running median at every frequency")
    Y = X / np.sqrt(med)
    Y[0] = 0.0
    return np.fft.irfft(Y, n=len(x))


# T4 spectral shift: F -----------------------------------------------------------------------------------------
def white_floor_F(x, key):
    """Independent Gaussian noise with standard deviation 1/1000 of the segment's standard deviation, added first. key is the full key of
    the noise draw, keys.f_noise(...): the key the draw has without the instance, with net law2b-F:<run> and purpose law2b-F (D14)."""
    x = np.asarray(x, dtype=np.float64)
    if not (isinstance(key, tuple) and len(key) == 6):
        raise ValueError("a noise key has six fields")
    rng = keys.rng(key)
    return x + (x.std() / 1000.0) * rng.standard_normal(len(x))


# T6 projection: D and O4 ---------------------------------------------------------------------------------------
def differences_D(x):
    """First differences of the segment (lag 1)."""
    x = np.asarray(x, dtype=np.float64)
    return x[1:] - x[:-1]


def o4_lag_js(n):
    """Order-4 lags 2^j, j = 0 .. 9, with 3 tau at most n/4 (exact: 12 tau <= n)."""
    return [j for j in range(10) if 12 * (1 << j) <= n]


def sigma_O4(counts4):
    """Sigma_hat at order 4: 75 patterns, pseudocount 1/2 each, denominator count + 75/2."""
    return patterns.sigma_hat(counts4, 4)


# T2 Bregman, T3 Hellinger, T5 max-plus ----------------------------------------------------------------------
def sigma_Q(counts3):
    """Sum over patterns of (p(pi) - p(rev pi))^2."""
    p = patterns.probs(counts3, 3)
    rev = patterns.tables(3)["rev"]
    return ((p - p[..., rev]) ** 2).sum(axis=-1)


def sigma_H(counts3):
    """Sum over patterns of (sqrt p(pi) - sqrt p(rev pi))^2."""
    p = np.sqrt(patterns.probs(counts3, 3))
    rev = patterns.tables(3)["rev"]
    return ((p - p[..., rev]) ** 2).sum(axis=-1)


def sigma_M(counts3):
    """Largest absolute log ratio over pattern pairs (max-plus limit of the log ratios)."""
    p = patterns.probs(counts3, 3)
    rev = patterns.tables(3)["rev"]
    return np.abs(np.log(p) - np.log(p[..., rev])).max(axis=-1)


def _pair_ix():
    ix = patterns.tables(3)["index"]
    return [(ix[(0, 1, 2)], ix[(2, 1, 0)]), (ix[(0, 2, 1)], ix[(1, 2, 0)]), (ix[(1, 0, 2)], ix[(2, 0, 1)])]


def a_features_Q(counts3):
    """a_k replaced by p(pi_k) - p(rev pi_k). Transforms like a_k under reversal and polarity flip."""
    p = patterns.probs(counts3, 3)
    return tuple(p[..., a] - p[..., b] for a, b in _pair_ix())


def a_features_H(counts3):
    """a_k replaced by sqrt p(pi_k) - sqrt p(rev pi_k)."""
    p = np.sqrt(patterns.probs(counts3, 3))
    return tuple(p[..., a] - p[..., b] for a, b in _pair_ix())


def max_plus_score(w, f):
    """Max-plus form of the score w . f: the largest of w_k f_k."""
    return (np.asarray(w, dtype=np.float64) * np.asarray(f, dtype=np.float64)).max(axis=-1)


# T7 domain and residual: E and R -------------------------------------------------------------------------------
def _order_stat(sorted_vals, p_num, p_den):
    """The order statistic of rank ceil(p n), no interpolation (section 12a, instance E). p = p_num / p_den exactly."""
    n = len(sorted_vals)
    k = -(-p_num * n // p_den)          # ceil(p n) in integers
    return sorted_vals[max(1, k) - 1]


def tail_spread(x):
    """(q99.9 - q0.1) / (q75 - q25) as an exact rational. A quantile q_p is the order statistic of rank ceil(p n), with no
    interpolation (section 12a). Values are floats, converted exactly to rationals."""
    from fractions import Fraction
    v = sorted(float(t) for t in np.asarray(x, dtype=np.float64))
    q = [Fraction(_order_stat(v, a, b)) for (a, b) in ((999, 1000), (1, 1000), (3, 4), (1, 4))]
    den = q[2] - q[3]
    if not den > 0:
        raise ValueError("interquartile range is zero")
    return (q[0] - q[1]) / den


def event_rich_threshold(fit_segments):
    """Median over the instrument's fit segments of the tail spread, as an exact rational (the mean of the two middle values when
    their number is even). Fitted on fit data only."""
    from fractions import Fraction
    t = sorted(tail_spread(s) for s in fit_segments)
    m = len(t)
    if m == 0:
        raise ValueError("no fit segments")
    return t[m // 2] if m % 2 == 1 else (t[m // 2 - 1] + t[m // 2]) / 2


def event_rich(seg, threshold):
    """A verdict segment is event-rich if its tail spread exceeds the threshold (exact comparison)."""
    return tail_spread(seg) > threshold


def flow_normal_scores_R(x):
    """R: normal scores of the ranks before block averaging."""
    return ranks.normal_scores(x)


FLOW_BLOCK_OP_B = "max"             # B: block maxima of 2 replace block means (flow.block_average op)
flow_freq_map_H = np.sqrt           # H: square roots of the class frequencies before standardisation
