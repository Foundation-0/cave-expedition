"""Exact Gaussian-rational helpers (library, second pass). Not a script.

Used by the check_*.py scripts for audit 014 and the 420-case recount. Written separately from
exactlib_a.py and shares no code with Foundation-0/spectral-inertia.

Gaussian rationals are plain tuples (re, im) of Fractions. Inertia is read from an exact
Hermitian LDL* elimination with 1x1 and 2x2 pivots (Sylvester's law), a different route from
the characteristic-polynomial + Descartes method used by the team.
"""
from fractions import Fraction as F
import math
import random


def need(ok, msg):
    if not ok:
        raise RuntimeError("CHECK FAILED: " + msg)


Z = (F(0), F(0))
O = (F(1), F(0))


def cadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def csub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def cmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def conj(a):
    return (a[0], -a[1])


def cdiv(a, b):
    d = b[0] * b[0] + b[1] * b[1]
    need(d != 0, "division by zero")
    n = cmul(a, conj(b))
    return (n[0] / d, n[1] / d)


def zeros(n, m=None):
    m = n if m is None else m
    return [[Z for _ in range(m)] for _ in range(n)]


def eye(n):
    return [[O if i == j else Z for j in range(n)] for i in range(n)]


def madd(A, B):
    return [[cadd(a, b) for a, b in zip(r, s)] for r, s in zip(A, B)]


def msub(A, B):
    return [[csub(a, b) for a, b in zip(r, s)] for r, s in zip(A, B)]


def mmul(A, B):
    n, k, m = len(A), len(B), len(B[0])
    out = zeros(n, m)
    for i in range(n):
        Ai = A[i]
        for j in range(m):
            re = F(0)
            im = F(0)
            for t in range(k):
                a = Ai[t]
                b = B[t][j]
                if a[0] == 0 and a[1] == 0:
                    continue
                re += a[0] * b[0] - a[1] * b[1]
                im += a[0] * b[1] + a[1] * b[0]
            out[i][j] = (re, im)
    return out


def dag(A):
    return [[conj(A[i][j]) for i in range(len(A))] for j in range(len(A[0]))]


def scal(s, A):
    return [[(s * a[0], s * a[1]) for a in r] for r in A]


def tr(A):
    s = Z
    for i in range(len(A)):
        s = cadd(s, A[i][i])
    need(s[1] == 0, "trace of Hermitian matrix not real")
    return s[0]


def frob2(A):
    return sum((a[0] * a[0] + a[1] * a[1] for r in A for a in r), F(0))


def is_herm(A):
    n = len(A)
    return all(A[i][j] == conj(A[j][i]) for i in range(n) for j in range(n))


def inv(A):
    n = len(A)
    M = [list(A[i]) + list(eye(n)[i]) for i in range(n)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != Z), None)
        need(p is not None, "singular")
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [cdiv(x, pv) for x in M[c]]
        for r in range(n):
            if r != c and M[r][c] != Z:
                f = M[r][c]
                M[r] = [csub(M[r][j], cmul(f, M[c][j])) for j in range(2 * n)]
    return [row[n:] for row in M]


def rank(A):
    M = [list(r) for r in A]
    n, m = len(M), len(M[0])
    r = 0
    for c in range(m):
        p = next((i for i in range(r, n) if M[i][c] != Z), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        for i in range(r + 1, n):
            if M[i][c] != Z:
                f = cdiv(M[i][c], M[r][c])
                M[i] = [csub(M[i][j], cmul(f, M[r][j])) for j in range(m)]
        r += 1
    return r


def inertia(A):
    """Exact inertia of a Hermitian matrix by LDL* with 1x1 / 2x2 pivots (Sylvester)."""
    need(is_herm(A), "inertia: not Hermitian")
    M = [list(r) for r in A]
    pos = neg = 0
    while M:
        n = len(M)
        k = next((i for i in range(n) if M[i][i] != Z), None)
        if k is not None:
            d = M[k][k][0]
            pos += d > 0
            neg += d < 0
            idx = [i for i in range(n) if i != k]
            M = [[csub(M[i][j], cdiv(cmul(M[i][k], M[k][j]), M[k][k])) for j in idx] for i in idx]
            continue
        pr = next(((i, j) for i in range(n) for j in range(n) if i != j and M[i][j] != Z), None)
        if pr is None:
            break  # remaining block is zero
        i0, j0 = pr
        # 2x2 block [[0, h], [conj h, 0]] has inertia (1, 1)
        pos += 1
        neg += 1
        h = M[i0][j0]
        # inverse of [[0,h],[hb,0]] is [[0, 1/hb],[1/h, 0]]
        ih = cdiv(O, h)
        ihb = cdiv(O, conj(h))
        idx = [i for i in range(n) if i not in (i0, j0)]
        new = []
        for i in idx:
            row = []
            for j in idx:
                # S = M_ij - [M_i,i0 M_i,j0] Binv [M_i0,j ; M_j0,j]
                t1 = cmul(cmul(M[i][i0], ihb), M[j0][j])
                t2 = cmul(cmul(M[i][j0], ih), M[i0][j])
                row.append(csub(csub(M[i][j], t1), t2))
            new.append(row)
        M = new
    nn = len(A)
    return (pos, neg, nn - pos - neg)


def cayley(n, rng, lo=-2, hi=2, den=3):
    K = zeros(n)
    for i in range(n):
        K[i][i] = (F(0), F(rng.randint(lo, hi), rng.randint(1, den)))
        for j in range(i + 1, n):
            a = (F(rng.randint(lo, hi), rng.randint(1, den)), F(rng.randint(lo, hi), rng.randint(1, den)))
            K[i][j] = a
            K[j][i] = (-a[0], a[1])
    I = eye(n)
    U = mmul(msub(I, K), inv(madd(I, K)))
    need(mmul(U, dag(U)) == I, "Cayley not unitary")
    return U


def from_eigs(U, vals):
    n = len(U)
    D = [[(F(vals[i]), F(0)) if i == j else Z for j in range(n)] for i in range(n)]
    return mmul(mmul(U, D), dag(U))


def moments(H, kmax=6):
    out = {}
    X = H
    out[1] = tr(X)
    for k in range(2, kmax + 1):
        X = mmul(X, H)
        out[k] = tr(X)
    return out


# ------------------------------------------------------------------ bounds
def ropt(u, t, S, b):
    if u <= 0 or u + t <= 0:
        return F(0)
    if b > 0 and t > 0 and t * (u + t) >= b * S:
        return u * u / (S - t * t / b)
    v = (u + t) ** 2 / S - b
    return v if v > 0 else F(0)


def docs10_best(u, t, S, b):
    """docs/10 section 3.3 best member over c >= 0 (C = 1 + c/2 >= 1)."""
    if b > 0 and t >= b:
        return 2 * u + t * t / b - S
    return 2 * (u + t) - S - b


def _solve(A, y):
    n = len(A)
    M = [list(A[i]) + [y[i]] for i in range(n)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            return None
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c and M[r][c] != 0:
                f = M[r][c] / M[c][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(n + 1)]
    return [M[i][n] / M[i][i] for i in range(n)]


def hankel_best(S, m):
    """max over a in Q_{>=0}^m of tr(1 - q_a(H)^2), q_a = 1 + sum (-1)^k a_k x^k.
    Objective g(a) = 2 sum_k (-1)^{k-1} a_k S_k - sum_{j,k} (-1)^{j+k} a_j a_k S_{j+k}: concave
    (Hankel Gram form). Exact KKT by enumerating active sets; returns (value, a)."""
    best = (F(0), [F(0)] * m)
    for mask in range(1, 2 ** m):
        J = [k for k in range(1, m + 1) if mask >> (k - 1) & 1]
        A = [[(-1) ** (j + k) * S[j + k] for k in J] for j in J]
        y = [(-1) ** (j - 1) * S[j] for j in J]
        sol = _solve(A, y)
        if sol is None or any(x < 0 for x in sol):
            continue
        a = [F(0)] * m
        for j, x in zip(J, sol):
            a[j - 1] = x
        val = sum(2 * (-1) ** (k - 1) * a[k - 1] * S[k] for k in range(1, m + 1)) - sum(
            (-1) ** (j + k) * a[j - 1] * a[k - 1] * S[j + k] for j in range(1, m + 1) for k in range(1, m + 1))
        # KKT check for inactive coordinates: gradient <= 0
        ok = True
        for k in range(1, m + 1):
            if a[k - 1] == 0:
                g = 2 * (-1) ** (k - 1) * S[k] - 2 * sum((-1) ** (j + k) * a[j - 1] * S[j + k] for j in range(1, m + 1))
                if g > 0:
                    ok = False
        if ok and val > best[0]:
            best = (val, a)
    return best


def a4_value(S, t, T3, b, s, p, g1, g3, kap):
    beta = s + g3 / p
    alpha = 1 - (beta * beta - s * s + kap) / (2 * p)
    lam0 = (s + g1 - alpha * beta) / kap
    M = alpha * alpha + kap * lam0 * lam0
    return 2 * s * S[1] - (s * s + 2 * p) * S[2] + 2 * s * p * S[3] - p * p * S[4] + 2 * g1 * t + 2 * g3 * T3 - b * M


def cert_int(x):
    """Integer certified by n_+ >= x."""
    return max(0, math.ceil(x))
