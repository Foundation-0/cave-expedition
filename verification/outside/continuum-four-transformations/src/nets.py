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


def midranks(x):
    """The mid-ranks of x as floats (tied values share the mean rank). K5's rank-mapped cascade is the mid-ranks of the cascade (SK8)."""
    x = np.asarray(x, dtype=np.float64)
    if not np.all(np.isfinite(x)):
        raise ValueError("mid-ranks need finite values")
    return ranks.twice_midrank(x).astype(np.float64) / 2.0


def amp_scores(x):
    """Amplitude-map net `amp_scores` (scale-flow transfer only): normal scores of the mid-ranks. Depends on the stream only through its
    mid-ranks, so it is finite, keeps tied values tied and creates no ties (D19)."""
    if not np.all(np.isfinite(np.asarray(x, dtype=np.float64))):
        raise ValueError("amp_scores needs finite values")
    return ranks.normal_scores(x)


def amp_lognormal(x):
    """Amplitude-map net `amp_lognormal` (scale-flow transfer only): exp of the normal scores of the mid-ranks. The scores lie within
    Phi^-1(1 - 1/(2n)) of 0, below 7.131 for n up to 10^12, so exp of them is below 1,251 (D19)."""
    return np.exp(amp_scores(x))


def map_guard_ok(x, y):
    """The representability guard (K1, section 5): the mapped series is finite and has as many distinct values as its input."""
    y = np.asarray(y)
    return bool(np.all(np.isfinite(y))) and ranks.n_distinct(x) == ranks.n_distinct(y)
