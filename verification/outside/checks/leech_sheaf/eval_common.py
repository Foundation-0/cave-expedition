"""Helpers for the evaluator-side lattice checks (exact integer tools, LLL, short vectors).

Not a check by itself. Shares no code with the target's verifier; it reads only its
witness tables as data, through target.py. Needs numpy.
"""
import math
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from target import team_data  # noqa: E402,F401


def fail(msg):
    raise SystemExit("CHECK FAILED: " + msg)


# ---------------- exact integer lattice tools ----------------

def int_row_basis(gens):
    """Row-style integer echelon basis (HNF-like) of the Z-span of integer vectors."""
    rows = [list(g) for g in gens if any(g)]
    n = len(rows[0])
    basis = []
    col = 0
    while rows and col < n:
        nz = [r for r in rows if r[col] != 0]
        z = [r for r in rows if r[col] == 0]
        if not nz:
            col += 1
            continue
        # Euclid on column col
        while len(nz) > 1:
            nz.sort(key=lambda r: abs(r[col]))
            p = nz[0]
            new = [p]
            for r in nz[1:]:
                q = r[col] // p[col]
                rr = [a - q * b for a, b in zip(r, p)]
                if rr[col] != 0:
                    new.append(rr)
                elif any(rr):
                    z.append(rr)
            nz = new
        p = nz[0]
        if p[col] < 0:
            p = [-a for a in p]
        basis.append(p)
        rows = [r for r in z if any(r)]
        col += 1
    return basis


def det_frac(M):
    n = len(M)
    A = [[Fraction(x) for x in r] for r in M]
    d = Fraction(1)
    for k in range(n):
        piv = next((i for i in range(k, n) if A[i][k] != 0), None)
        if piv is None:
            return Fraction(0)
        if piv != k:
            A[k], A[piv] = A[piv], A[k]
            d = -d
        d *= A[k][k]
        for i in range(k + 1, n):
            f = A[i][k] / A[k][k]
            if f:
                for j in range(k, n):
                    A[i][j] -= f * A[k][j]
    return d


def inv_frac(M):
    n = len(M)
    A = [[Fraction(x) for x in r] + [Fraction(int(i == j)) for j in range(n)] for i, r in enumerate(M)]
    for k in range(n):
        piv = next(i for i in range(k, n) if A[i][k] != 0)
        A[k], A[piv] = A[piv], A[k]
        pv = A[k][k]
        A[k] = [x / pv for x in A[k]]
        for i in range(n):
            if i != k and A[i][k] != 0:
                f = A[i][k]
                A[i] = [a - f * b for a, b in zip(A[i], A[k])]
    return [r[n:] for r in A]


def gram(B):
    return [[sum(a * b for a, b in zip(r, s)) for s in B] for r in B]


def lll(B, delta=0.99):
    """Integer LLL (basis kept exact as ints; Gram-Schmidt in floats only steers the reduction)."""
    B = [list(r) for r in B]
    n = len(B)

    def gs(B):
        Bs = []
        mu = [[0.0] * n for _ in range(n)]
        for i in range(n):
            v = [float(x) for x in B[i]]
            for j in range(i):
                mu[i][j] = sum(float(a) * b for a, b in zip(B[i], Bs[j])) / sum(b * b for b in Bs[j])
                v = [a - mu[i][j] * b for a, b in zip(v, Bs[j])]
            Bs.append(v)
        return Bs, mu

    Bs, mu = gs(B)
    k = 1
    it = 0
    while k < n:
        it += 1
        for j in range(k - 1, -1, -1):
            q = round(mu[k][j])
            if q:
                B[k] = [a - q * b for a, b in zip(B[k], B[j])]
                Bs, mu = gs(B)
        nk = sum(x * x for x in Bs[k])
        nk1 = sum(x * x for x in Bs[k - 1])
        if nk >= (delta - mu[k][k - 1] ** 2) * nk1:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            Bs, mu = gs(B)
            k = max(k - 1, 1)
    return B


def short_vectors(G_int, bound, slack=1e-6):
    """All nonzero integer coefficient vectors x (up to sign) with x^T G x <= bound, G exact int PD.

    Float Cholesky steers the search with an additive slack; every reported vector is then
    re-checked exactly with integer arithmetic.  Returns list of coefficient tuples (one of each +-pair).
    """
    import numpy as np
    n = len(G_int)
    G = np.array(G_int, dtype=float)
    # q(x) = sum_i Q[i][i] (x_i + sum_{j>i} Q[i][j] x_j)^2
    Q = G.copy()
    for i in range(n):
        for j in range(i + 1, n):
            Q[j][i] = Q[i][j]
            Q[i][j] = Q[i][j] / Q[i][i]
        for k in range(i + 1, n):
            for l in range(k, n):
                Q[k][l] -= Q[k][i] * Q[i][l]
    diag = [Q[i][i] for i in range(n)]
    up = [[Q[i][j] if j > i else 0.0 for j in range(n)] for i in range(n)]
    out = []
    x = [0] * n
    B = bound + slack

    def rec(i, rem):
        c = -sum(up[i][j] * x[j] for j in range(i + 1, n))
        r = math.sqrt(max(rem, 0.0) / diag[i])
        lo = math.ceil(c - r - 1e-9)
        hi = math.floor(c + r + 1e-9)
        for v in range(lo, hi + 1):
            t = rem - diag[i] * (v - c) ** 2
            if t < -slack:
                continue
            x[i] = v
            if i == 0:
                out.append(tuple(x))
            else:
                rec(i - 1, t)
        x[i] = 0

    rec(n - 1, B)
    res = []
    for v in out:
        if not any(v):
            continue
        # keep one of +-v: first nonzero positive
        fnz = next(a for a in v if a != 0)
        if fnz < 0:
            continue
        q = sum(v[i] * G_int[i][j] * v[j] for i in range(n) for j in range(n))
        if q <= bound:
            res.append((v, q))
    return res


def analyse(name, n, C_scaled, scale):
    """C_scaled: integer matrix = scale * C, L = 2I + C. Gamma_gen = Z^n L + span(P - e0).

    Returns (result dict, basis B, minimal vectors scaled by `scale`, scale*L as integers).
    """
    L_int = [[(2 * scale if i == j else 0) + C_scaled[i][j] for j in range(n)] for i in range(n)]  # = scale*L
    P = [[s * scale if j == i else 0 for j in range(n)] for i in range(n) for s in (1, -1)]
    e0 = P[0]
    gens = L_int + [[a - b for a, b in zip(p, e0)] for p in P]
    B = int_row_basis(gens)
    if len(B) != n:
        fail(name + " rank")
    detB = abs(det_frac(B))
    covol = detB / Fraction(scale) ** n
    detL = det_frac(L_int) / Fraction(scale) ** n
    index = detL / covol
    # coset injectivity of P - e0 modulo Z^n L
    Linv = inv_frac(L_int)  # inverse of scale*L
    keys = set()
    for p in P:
        d = [a - b for a, b in zip(p, e0)]
        coords = [sum(Fraction(d[k]) * Linv[k][j] for k in range(n)) for j in range(n)]  # d (scale L)^{-1}
        keys.add(tuple(c - (c.numerator // c.denominator) for c in coords))
    bar_ok = all(sum(c * c for c in row) == 2 * scale * scale for row in C_scaled)
    # Gram of basis of sqrt2 * Gamma: 2 * (B B^T) / scale^2
    Gq = [[Fraction(2 * v, scale * scale) for v in r] for r in gram(B)]
    integral = all(v.denominator == 1 for r in Gq for v in r)
    even = integral and all(Gq[i][i].numerator % 2 == 0 for i in range(n))
    Gint = [[int(v) for v in r] for r in Gq]
    det2 = det_frac(Gint)
    Bred = lll(B)
    if abs(det_frac(Bred)) != detB:
        fail("LLL changed det")
    Gr = [[Fraction(2 * v, scale * scale) for v in r] for r in gram(Bred)]
    Gr_int = [[int(v) for v in r] for r in Gr]
    sv = short_vectors(Gr_int, 4)  # sqrt2-scaled norm <= 4  <=>  Gamma norm <= 2
    by_norm = {}
    for v, q in sv:
        by_norm[q] = by_norm.get(q, 0) + 2
    minvecs = []
    for v, q in sv:
        if q == 4:
            w = [sum(v[i] * Bred[i][j] for i in range(n)) for j in range(n)]  # = scale * w
            minvecs.append(w)
            minvecs.append([-a for a in w])
    res = {
        "covolume": str(covol), "det_L": str(detL), "index_ZL_in_Gamma": str(index),
        "distinct_cosets_of_P_minus_e0": len(keys), "bars_norm2": bar_ok,
        "sqrt2_scaled_gram_integral": integral, "even": even, "det_sqrt2_gram": str(det2),
        "short_vector_counts_by_sqrt2norm": {str(k): by_norm[k] for k in sorted(by_norm)},
    }
    return res, B, minvecs, L_int


_MV = {}


def bw16_minvecs():
    """(L_x2, minvecs_x2) for the target's BW16 basis, computed once per process."""
    if "bw16" not in _MV:
        _, _, mv, L = analyse("BW16", 16, team_data("C2_16_WITNESS"), 2)
        _MV["bw16"] = (L, mv)
    return _MV["bw16"]


def leech_minvecs():
    """(L_x4, minvecs_x4) for the target's Leech basis, computed once per process (about 20 s)."""
    if "leech" not in _MV:
        _, _, mv, L = analyse("Leech", 24, team_data("U24_WITNESS"), 4)
        _MV["leech"] = (L, mv)
    return _MV["leech"]
