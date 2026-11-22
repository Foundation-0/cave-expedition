"""The nets of PREREG section 5 as transformations of one series, and the lag rule of section 4.3."""
import numpy as np
import ranks

MIN_CONFIRMATORY = 2048  # no confirmatory run uses a segment shorter than this (section 5)

STATISTICAL_NETS = ("native", "bm2", "sub2", "q12", "q8")  # applied to the segment; placement and length change the segment itself


def block_mean(x, b):
    x = np.asarray(x, dtype=np.float64)
    m = (len(x) // b) * b
    return x[:m].reshape(-1, b).mean(axis=1)


def subsample(x, b):
    return np.asarray(x, dtype=np.float64)[::b].copy()


def quantize(x, bits):
    """Equal-count bins floor(2^b (r - 1/2) / n) on mid-ranks (ranks.equal_count_bins). Tied values stay tied."""
    return ranks.equal_count_bins(x, bits)


def polarity_flip(x):
    return -np.asarray(x, dtype=np.float64)


def apply(net, x):
    if net == "native":
        return np.asarray(x, dtype=np.float64)
    if net == "bm2":
        return block_mean(x, 2)
    if net == "sub2":
        return subsample(x, 2)
    if net == "q12":
        return quantize(x, 12)
    if net == "q8":
        return quantize(x, 8)
    raise ValueError("unknown net " + str(net))


def applicable(net, N):
    """Sampling-rate nets apply only where the result has at least 2,048 samples. Quantization and the native run
    always apply."""
    if net in ("bm2", "sub2"):
        return N // 2 >= MIN_CONFIRMATORY
    return True


def window_length_applicable(N):
    """Window length net N/2 applies only where N/2 is at least 2,048."""
    return N // 2 >= MIN_CONFIRMATORY


def lag_js(n):
    """Lags tau = 2^j for j = 0 .. 9, keeping lags with 2 tau at most n/4 (exact integer test 8 tau <= n)."""
    return [j for j in range(10) if 8 * (1 << j) <= n]


# amplitude maps ---------------------------------------------------------------------------------------------
def increasing_maps():
    """The three maps of K1: x^3 + x, exp, and the (mid-)ranks."""
    return {"cubic": lambda v: v ** 3 + v, "exp": np.exp, "rank": lambda v: ranks.twice_midrank(v).astype(np.float64) / 2.0}


def amp_normal_scores(x):
    """Amplitude-map net 1 (scale-flow transfer only): normal scores of the ranks."""
    return ranks.normal_scores(x)


def amp_exp_standardised(x):
    """Amplitude-map net 2 (scale-flow transfer only): exp of the series standardised to mean 0, unit variance."""
    x = np.asarray(x, dtype=np.float64)
    sd = x.std() if x.size > 1 else 0.0
    if not (np.isfinite(sd) and sd > 0.0):
        raise ValueError("cannot standardise a constant or non-finite series (standard deviation is zero)")
    return np.exp((x - x.mean()) / sd)


def map_guard_ok(x, y):
    """A map is usable in the exact identity only if it leaves the number of distinct values unchanged."""
    return ranks.n_distinct(x) == ranks.n_distinct(y)
