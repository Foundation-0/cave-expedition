"""Ranks and rank-based maps of PREREG section 4 (Amendment 1, A4, A5, A10).

Mid-ranks are counted from 1 and tied values share the mean of their ranks. To stay exact, ranks are
carried as twice_rank = 2 r, an integer.

NORMAL SCORE IMPLEMENTATION (one fixed implementation, recorded here and with the code commit):
Phi^-1 is `statistics.NormalDist(0.0, 1.0).inv_cdf` of the Python standard library (Wichura's algorithm AS 241),
evaluated only on the lower half. The table g[m], m = 2 r - 1 in 1 .. 2n - 1, is
  g[m] = inv_cdf(m / (2 n))    for m < n
  g[n] = 0.0
  g[m] = -g[2 n - m]           for m > n
so that the score of the polarity-flipped series is exactly the negated score, bit for bit.
The score of a value with mid-rank r is g[2 r - 1] = Phi^-1((r - 1/2) / n)."""
import statistics
import numpy as np

PHI_INV_IMPLEMENTATION = "statistics.NormalDist(0.0, 1.0).inv_cdf (AS 241), lower half, odd reflection"

_TABLES = {}


def twice_midrank(x):
    """Integer array 2 r of the mid-ranks of x (ties share the mean rank). Exact."""
    x = np.asarray(x)
    _, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    before = np.cumsum(cnt) - cnt
    return (2 * before + cnt + 1)[inv.reshape(-1)].astype(np.int64)


def n_distinct(x):
    return int(np.unique(np.asarray(x)).size)


def score_table(n):
    """g[m] for m = 0 .. 2 n (entries 0 and 2 n unused)."""
    if n not in _TABLES:
        nd = statistics.NormalDist(0.0, 1.0)
        g = np.zeros(2 * n + 1, dtype=np.float64)
        for m in range(1, n):
            g[m] = nd.inv_cdf(m / (2.0 * n))
        g[n] = 0.0
        for m in range(n + 1, 2 * n):
            g[m] = -g[2 * n - m]
        _TABLES[n] = g
    return _TABLES[n]


def normal_scores(x):
    """Phi^-1((r - 1/2) / n) for mid-ranks r of x."""
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    t = twice_midrank(x)
    return score_table(n)[t - 1].copy()


def equal_count_bins(x, bits):
    """floor(2^b (r - 1/2) / n) on mid-ranks, as exact integer arithmetic: floor(2^b (2 r - 1) / (2 n)).
    Tied values get the same bin. Returned as float64 bin numbers."""
    x = np.asarray(x, dtype=np.float64)
    n = x.size
    t = twice_midrank(x)
    q = ((1 << bits) * (t - 1)) // (2 * n)
    return q.astype(np.float64)
