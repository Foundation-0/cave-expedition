"""Ordinal-pattern counts and the irreversibility statistic (PREREG 4.3).
A pattern is the string of ranks: for (a, b, c) with b < c < a it is '201'.
Counts are exact integers. Windows with a tied pair of values are left out and counted."""
import itertools
import math
import numpy as np

_TABLES = {}


def tables(d):
    if d not in _TABLES:
        perms = list(itertools.permutations(range(d)))
        index = {p: k for k, p in enumerate(perms)}
        codes = np.zeros(len(perms), dtype=np.int64)
        for k, p in enumerate(perms):
            c = 0
            for r in p:
                c = c * d + r
            codes[k] = c
        rev = np.array([index[tuple(reversed(p))] for p in perms], dtype=np.int64)
        comp = np.array([index[tuple(d - 1 - r for r in p)] for p in perms], dtype=np.int64)
        names = ["".join(str(r) for r in p) for p in perms]
        _TABLES[d] = (perms, codes, rev, comp, names)
    return _TABLES[d]


def counts_batch(Y, d, tau, step=1):
    """Y: (M, n) array. Windows (y_t, y_{t+tau}, ..., y_{t+(d-1)tau}) for t = 0, step, 2 step, ...
    Returns (counts (M, d!) int64 in lexicographic pattern order, ties (M,), n_windows)."""
    Y = np.atleast_2d(np.asarray(Y, dtype=np.float64))
    M, n = Y.shape
    span = (d - 1) * tau
    if n <= span:
        raise ValueError("series of %d samples is too short for order %d at lag %d" % (n, d, tau))
    nall = n - span
    cols = [Y[:, k * tau:k * tau + nall:step] for k in range(d)]
    nwin = cols[0].shape[1]
    tied = np.zeros((M, nwin), dtype=bool)
    for i in range(d):
        for j in range(i + 1, d):
            tied |= cols[i] == cols[j]
    D = d ** d
    code = np.zeros((M, nwin), dtype=np.int64)
    for i in range(d):
        r = np.zeros((M, nwin), dtype=np.int64)
        for j in range(d):
            if j != i:
                r += cols[j] < cols[i]
        code = code * d + r
    code = np.where(tied, D, code)
    flat = (code + np.arange(M, dtype=np.int64)[:, None] * (D + 1)).ravel()
    cnt = np.bincount(flat, minlength=M * (D + 1)).reshape(M, D + 1)
    perms, codes, rev, comp, names = tables(d)
    counts = cnt[:, codes].astype(np.int64)
    ties = cnt[:, D].astype(np.int64)
    if not np.all(counts.sum(axis=1) + ties == nwin):
        raise RuntimeError("pattern counts do not add up to the number of windows")
    return counts, ties, nwin


def counts_one(x, d, tau, step=1):
    c, t, nw = counts_batch(np.asarray(x, dtype=np.float64)[None, :], d, tau, step)
    return c[0], int(t[0]), nw


def sigma_hat(counts_row, d=3, rev=None):
    """Sum over patterns of p ln(p / p(rev)), p = (n + 1/2) / (sum n + d!/2). For d = 3 this is the
    plan's formula; for d = 4 the same form with 24 patterns (the plan states only d = 3)."""
    if rev is None:
        rev = tables(d)[2]
    n = [int(c) for c in counts_row]
    norm = sum(n) + math.factorial(d) / 2.0
    p = [(c + 0.5) / norm for c in n]
    terms = [p[k] * math.log(p[k] / p[int(rev[k])]) for k in range(len(p))]
    return math.fsum(sorted(terms))
