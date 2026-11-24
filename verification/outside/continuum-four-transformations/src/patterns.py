"""Ordinal-pattern counts and the irreversibility statistic (PREREG 4.3, Amendment 1, A5).

A pattern is the tuple of dense ranks of the window values: the rank of a value is the number of
distinct window values below it. For (a, b, c) with b < c < a it is '201'. Windows with tied values are
patterns of their own: 13 patterns at order 3 (6 untied, 7 tied) and 75 at order 4 (24 untied, 51 tied).
Counts are exact integers. The reversal of a pattern is the reversed tuple, the complement (polarity flip)
maps rank r to (top rank - r)."""
import itertools
import math
import numpy as np

_TABLES = {}


def _dense(t):
    vals = sorted(set(t))
    return tuple(vals.index(v) for v in t)


def tables(d):
    """Returns dict with names, tuples, rev, comp (index arrays), untied (bool array) and the cmp-code lookup."""
    if d in _TABLES:
        return _TABLES[d]
    pats = sorted({_dense(t) for t in itertools.product(range(d), repeat=d)},
                  key=lambda p: (len(set(p)) < d, p))
    index = {p: k for k, p in enumerate(pats)}
    rev = np.array([index[tuple(reversed(p))] for p in pats], dtype=np.int64)
    comp = np.array([index[tuple(max(p) - r for r in p)] for p in pats], dtype=np.int64)
    pairs = [(i, j) for i in range(d) for j in range(i + 1, d)]
    npairs = len(pairs)
    lookup = -np.ones(3 ** npairs, dtype=np.int64)
    for k, p in enumerate(pats):
        code = 0
        for (i, j) in pairs:
            c = 0 if p[i] < p[j] else (1 if p[i] == p[j] else 2)
            code = code * 3 + c
        lookup[code] = k
    T = {"names": ["".join(str(r) for r in p) for p in pats], "tuples": pats, "rev": rev, "comp": comp,
         "untied": np.array([len(set(p)) == d for p in pats]), "lookup": lookup, "pairs": pairs,
         "index": index, "n": len(pats)}
    _TABLES[d] = T
    return T


def counts_batch(Y, d, tau, step=1, last_window_dropped=False):
    """Y: (M, n) array. Windows (y_t, y_{t+tau}, ..., y_{t+(d-1)tau}) for t = 0, step, 2 step, ...
    Returns (counts (M, P) int64 in table order, n_windows). `last_window_dropped=True` is the MUST-FAIL
    variant of the K1 control."""
    Y = np.atleast_2d(np.asarray(Y, dtype=np.float64))
    M, n = Y.shape
    span = (d - 1) * tau
    if n <= span:
        raise ValueError("series of %d samples is too short for order %d at lag %d" % (n, d, tau))
    nall = n - span
    cols = [Y[:, k * tau:k * tau + nall:step] for k in range(d)]
    nwin = cols[0].shape[1]
    T = tables(d)
    code = np.zeros((M, nwin), dtype=np.int64)
    for (i, j) in T["pairs"]:
        c = np.where(cols[i] < cols[j], 0, np.where(cols[i] == cols[j], 1, 2))
        code = code * 3 + c
    pid = T["lookup"][code]
    if np.any(pid < 0):
        raise RuntimeError("a window matched no pattern")
    P = T["n"]
    if last_window_dropped:
        pid = pid[:, :-1]
    flat = (pid + np.arange(M, dtype=np.int64)[:, None] * P).ravel()
    counts = np.bincount(flat, minlength=M * P).reshape(M, P).astype(np.int64)
    expect = nwin - 1 if last_window_dropped else nwin
    if not np.all(counts.sum(axis=1) == expect):
        raise RuntimeError("pattern counts do not add up to the number of windows")
    return counts, nwin


def counts_one(x, d, tau, step=1):
    c, nw = counts_batch(np.asarray(x, dtype=np.float64)[None, :], d, tau, step)
    return c[0], nw


def tied_windows(counts_row, d):
    return int(np.asarray(counts_row)[~tables(d)["untied"]].sum())


def probs(counts, d):
    """p(pi) = (n(pi) + 1/2) / (sum n + P/2), P the number of patterns (13 at order 3, 75 at order 4).
    counts: (..., P)."""
    c = np.asarray(counts, dtype=np.float64)
    P = tables(d)["n"]
    return (c + 0.5) / (c.sum(axis=-1, keepdims=True) + P / 2.0)


def sigma_hat(counts, d=3):
    """Sum over patterns of p ln(p / p(rev pi)). counts: (..., P); returns (...,)."""
    p = probs(counts, d)
    rev = tables(d)["rev"]
    terms = p * (np.log(p) - np.log(p[..., rev]))
    # the terms are summed in sorted order, so equal multisets of terms (x and -x) give bit-identical sums
    return np.sort(terms, axis=-1).sum(axis=-1)


def a_features(counts):
    """a1, a2, a3 of PREREG 4.3 from order-3 counts (+1/2): ln n(012)/n(210), ln n(021)/n(120), ln n(102)/n(201)."""
    T = tables(3)
    c = np.asarray(counts, dtype=np.float64) + 0.5
    ln = np.log(c)
    ix = T["index"]
    out = []
    for a, b in (((0, 1, 2), (2, 1, 0)), ((0, 2, 1), (1, 2, 0)), ((1, 0, 2), (2, 0, 1))):
        out.append(ln[..., ix[a]] - ln[..., ix[b]])
    return out[0], out[1], out[2]
