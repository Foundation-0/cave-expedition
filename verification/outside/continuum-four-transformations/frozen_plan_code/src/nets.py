"""The nets of PREREG section 5 as transformations of one series (or one grid rule)."""
import numpy as np

RATIO = {"native": 1, "bm2": 2, "bm4": 4, "sub2": 2, "q12": 1, "q8": 1, "whiten": 1}


def block_mean(x, b):
    x = np.asarray(x, dtype=np.float64)
    m = (len(x) // b) * b
    return x[:m].reshape(-1, b).mean(axis=1)


def subsample(x, b):
    return np.asarray(x, dtype=np.float64)[::b].copy()


def quantize(x, bits):
    """Uniform bins over the 0.1 to 99.9 percent range of the segment; values outside go to the end bins."""
    x = np.asarray(x, dtype=np.float64)
    lo, hi = np.percentile(x, [0.1, 99.9])
    if not hi > lo:
        raise ValueError("quantization range is empty")
    nb = 2 ** bits
    q = np.floor((np.clip(x, lo, hi) - lo) / (hi - lo) * nb)
    return np.minimum(q, nb - 1).astype(np.float64)


def running_median(v, width=33):
    h = width // 2
    padded = np.pad(v, h, mode="reflect")  # PROVISIONAL edge rule (AMENDMENTS_NEEDED.md, item A4)
    win = np.lib.stride_tricks.sliding_window_view(padded, width)
    return np.median(win, axis=1)


def whiten(x):
    """Zero-phase whitening: divide the Fourier transform by the square root of a 33-bin
    running median of the periodogram."""
    x = np.asarray(x, dtype=np.float64)
    X = np.fft.rfft(x)
    med = running_median(np.abs(X) ** 2, 33)
    if not np.all(med > 0):
        raise ValueError("whitening needs a positive running median at every bin")
    return np.fft.irfft(X / np.sqrt(med), n=len(x))


def increasing_maps():
    return {"cubic": lambda v: v ** 3 + v, "exp": np.exp, "rank": lambda v: np.argsort(np.argsort(v, kind="stable"), kind="stable").astype(np.float64)}


def polarity_flip(x):
    return -np.asarray(x, dtype=np.float64)


def apply(net, x):
    if net == "native":
        return np.asarray(x, dtype=np.float64)
    if net == "bm2":
        return block_mean(x, 2)
    if net == "bm4":
        return block_mean(x, 4)
    if net == "sub2":
        return subsample(x, 2)
    if net == "q12":
        return quantize(x, 12)
    if net == "q8":
        return quantize(x, 8)
    if net == "whiten":
        return whiten(x)
    raise ValueError("unknown net " + str(net))


def lag_js(net):
    """Lags 2^j with 2^j <= 512 / rate ratio: the same physical lag range, limited to fit the
    shorter series. PROVISIONAL reading of 'lags limited to fit the shorter segment' (item A3)."""
    r = RATIO[net]
    top = 9 - (r.bit_length() - 1)
    return list(range(top + 1))
