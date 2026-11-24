"""Spectral-slope matching of an instrument to a K2 class (PREREG K2).
PROVISIONAL reading of 'central decade of frequencies' (item A10): the decade of log10 frequency centred on
the middle of the log10 range from the lowest bin (1/N) to the Nyquist frequency (1/2)."""
import math
import numpy as np


def loglog_slope(pg, N):
    f = np.arange(len(pg), dtype=np.float64) / N
    lo, hi = math.log10(1.0 / N), math.log10(0.5)
    mid = (lo + hi) / 2.0
    sel = (np.log10(np.maximum(f, 1e-300)) >= mid - 0.5) & (np.log10(np.maximum(f, 1e-300)) <= mid + 0.5) & (f > 0)
    lx = np.log10(f[sel])
    ly = np.log10(pg[sel])
    lx = lx - lx.mean()
    return float((lx * (ly - ly.mean())).sum() / (lx * lx).sum())


def match_class(slope, class_slopes):
    """class_slopes: dict name -> slope. Nearest class by absolute slope difference (ties: first name in sorted order)."""
    return min(sorted(class_slopes), key=lambda c: abs(class_slopes[c] - slope))
