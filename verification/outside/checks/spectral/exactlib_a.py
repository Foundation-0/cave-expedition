"""Exact Gaussian-rational helpers (library, first pass). Not a script.

Used by check_rank_envelope_and_moments.py, check_sharpness.py, check_dual_checkers.py and
check_must_fail_controls.py. Shares no code with Foundation-0/spectral-inertia or with loom scripts/inertia_cert.py.
Complex numbers are (re, im) pairs of Fractions. Matrices are lists of lists.
Two inertia methods:
  inertia_cong  : congruence elimination with 1x1 pivots; when every remaining diagonal entry is
                  zero it creates a nonzero pivot with e_i <- e_i + w e_j (w = 1 or -i).
  inertia_sympy : sympy charpoly (Berkowitz) + square-free factorization + sympy real-root counting.
"""
from fractions import Fraction as Fr
import random

Z = (Fr(0), Fr(0))
O = (Fr(1), Fr(0))


class Bad(Exception):
    pass


def chk(ok, msg):
    if not ok:
        raise Bad(msg)


def ca(a, b):
    return (a[0] + b[0], a[1] + b[1])


def cs(a, b):
    return (a[0] - b[0], a[1] - b[1])


def cm(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def cc(a):
    return (a[0], -a[1])


def cabs2(a):
    return a[0] * a[0] + a[1] * a[1]


def cdiv(a, b):
    d = cabs2(b)
    chk(d != 0, "div0")
    n = cm(a, cc(b))
    return (n[0] / d, n[1] / d)


def zeros(n, m=None):
    m = n if m is None else m
    return [[Z] * m for _ in range(n)]


def eye(n):
    return [[O if i == j else Z for j in range(n)] for i in range(n)]


def mmul(A, B):
    n, k, m = len(A), len(B), len(B[0])
    out = [[Z] * m for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        oi = out[i]
        for t in range(k):
            a = Ai[t]
            if a == Z:
                continue
            Bt = B[t]
            for j in range(m):
                b = Bt[j]
                if b != Z:
                    oi[j] = ca(oi[j], cm(a, b))
    return out


def dag(A):
    return [[cc(A[i][j]) for i in range(len(A))] for j in range(len(A[0]))]


def madd(A, B, s=Fr(1)):
    return [[(a[0] + s * b[0], a[1] + s * b[1]) for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def mscale(A, s):
    return [[(x[0] * s, x[1] * s) for x in r] for r in A]


def tr(A):
    s = Z
    for i in range(len(A)):
        s = ca(s, A[i][i])
    chk(s[1] == 0, "nonreal trace")
    return s[0]


def fro2(A):
    return sum((cabs2(x) for r in A for x in r), Fr(0))


def is_herm(A):
    n = len(A)
    return all(A[i][j] == cc(A[j][i]) for i in range(n) for j in range(n))


def rank(A):
    """Exact rank by row reduction over Q(i)."""
    if not A or not A[0]:
        return 0
    R = [r[:] for r in A]
    n, m = len(R), len(R[0])
    rk = 0
    for col in range(m):
        piv = next((i for i in range(rk, n) if R[i][col] != Z), None)
        if piv is None:
            continue
        R[rk], R[piv] = R[piv], R[rk]
        for i in range(n):
            if i != rk and R[i][col] != Z:
                f = cdiv(R[i][col], R[rk][col])
                R[i] = [cs(x, cm(f, y)) for x, y in zip(R[i], R[rk])]
        rk += 1
    return rk


def inertia_cong(H):
    """(pos, neg, zero) of a Hermitian matrix by congruence elimination."""
    chk(is_herm(H), "not Hermitian")
    A = [r[:] for r in H]
    pos = neg = 0
    while A:
        m = len(A)
        k = next((i for i in range(m) if A[i][i][0] != 0), None)
        if k is None:
            pair = next(((i, j) for i in range(m) for j in range(i + 1, m) if A[i][j] != Z), None)
            if pair is None:
                return (pos, neg, len(H) - pos - neg)
            i, j = pair
            w = O if A[i][j][0] != 0 else (Fr(0), Fr(-1))
            # column op: col_i += w col_j ; row op: row_i += conj(w) row_j  (congruence T* A T)
            for r in range(m):
                A[r][i] = ca(A[r][i], cm(w, A[r][j]))
            wc = cc(w)
            A[i] = [ca(A[i][c], cm(wc, A[j][c])) for c in range(m)]
            chk(A[i][i][1] == 0 and A[i][i][0] != 0, "pivot creation failed")
            k = i
        d = A[k][k][0]
        if d > 0:
            pos += 1
        else:
            neg += 1
        rest = [r for r in range(m) if r != k]
        A = [[cs(A[r][c], cm(A[r][k], (A[k][c][0] / d, A[k][c][1] / d))) for c in rest] for r in rest]
    return (pos, neg, len(H) - pos - neg)


def inertia_sympy(H):
    import sympy as sp
    x = sp.Symbol("x")
    n = len(H)
    M = sp.Matrix(n, n, lambda i, j: sp.Rational(H[i][j][0].numerator, H[i][j][0].denominator)
                  + sp.I * sp.Rational(H[i][j][1].numerator, H[i][j][1].denominator))
    coeffs = [sp.expand(c) for c in M.charpoly(x).all_coeffs()]
    chk(all(sp.im(c) == 0 for c in coeffs), "complex charpoly coeff")
    p = sp.Poly([sp.re(c) for c in coeffs], x)
    z = 0
    while p.degree() > 0 and p.eval(0) == 0:
        p = sp.Poly(sp.quo(p.as_expr(), x), x)
        z += 1
    pos = neg = 0
    _, facs = sp.sqf_list(p)
    for f, mult in facs:
        if f.degree() == 0:
            continue
        pos += mult * f.count_roots(0, None)
        neg += mult * f.count_roots(None, 0)
    chk(pos + neg + z == n, "sympy counts do not sum to n")
    return (pos, neg, z)


def inertia(H, both=True):
    a = inertia_cong(H)
    if both:
        b = inertia_sympy(H)
        chk(a == b, "my two inertia methods disagree %r %r" % (a, b))
    return a


# ---------- random exact objects ----------

def rq(rng, lo=-4, hi=4, dens=(1, 1, 2, 3)):
    return Fr(rng.randint(lo, hi), rng.choice(dens))


def rcz(rng, cplx=True):
    return (rq(rng), rq(rng) if cplx else Fr(0))


def householder(v):
    """I - 2 v v* / (v* v): exact unitary over Q(i) for nonzero v."""
    n = len(v)
    nn = sum((cabs2(a) for a in v), Fr(0))
    chk(nn != 0, "zero householder vector")
    f = Fr(2) / nn
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            e = cm(v[i], cc(v[j]))
            row.append(((1 if i == j else 0) - f * e[0], -f * e[1]))
        out.append(row)
    return out


def rand_unitary(rng, n, cplx=True, k=3):
    U = eye(n)
    for _ in range(k):
        v = [rcz(rng, cplx) for _ in range(n)]
        if all(a == Z for a in v):
            v[0] = O
        U = mmul(U, householder(v))
    # random unit phases
    ph = [O, (Fr(-1), Fr(0))] + ([(Fr(0), Fr(1)), (Fr(0), Fr(-1))] if cplx else [])
    D = [[rng.choice(ph) if i == j else Z for j in range(n)] for i in range(n)]
    return mmul(U, D)


def from_eig(U, eigs):
    n = len(U)
    D = [[(eigs[i], Fr(0)) if i == j else Z for j in range(n)] for i in range(n)]
    return mmul(mmul(U, D), dag(U))


def rand_psd(rng, n, r, cplx=True):
    X = [[rcz(rng, cplx) for _ in range(r)] for _ in range(n)] if r > 0 else None
    if X is None:
        return zeros(n)
    return mmul(X, dag(X))


def rand_herm(rng, n, cplx=True):
    H = zeros(n)
    for i in range(n):
        H[i][i] = (rq(rng), Fr(0))
        for j in range(i + 1, n):
            H[i][j] = rcz(rng, cplx)
            H[j][i] = cc(H[i][j])
    return H
