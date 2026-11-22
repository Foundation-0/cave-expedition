"""Exact arithmetic for the Hermitian-triple check. Stdlib only, no floats, no bare assert.
Base rings: Q (Fraction) and Q(i) (Qi). Matrices are lists of lists."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import gcd, isqrt


class CheckFailure(Exception):
    pass


def require(cond, msg):
    if not cond:
        raise CheckFailure(msg)


def fr(x):
    if isinstance(x, bool) or isinstance(x, float):
        raise TypeError("float/bool rejected")
    return Fraction(x)


class Qi:
    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        object.__setattr__(self, "re", fr(re))
        object.__setattr__(self, "im", fr(im))

    def __setattr__(self, k, v):
        raise AttributeError("immutable")

    def _c(self, o):
        return o if isinstance(o, Qi) else Qi(o, 0)

    def __add__(self, o):
        o = self._c(o)
        return Qi(self.re + o.re, self.im + o.im)

    __radd__ = __add__

    def __sub__(self, o):
        o = self._c(o)
        return Qi(self.re - o.re, self.im - o.im)

    def __rsub__(self, o):
        return self._c(o) - self

    def __neg__(self):
        return Qi(-self.re, -self.im)

    def __mul__(self, o):
        o = self._c(o)
        return Qi(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def conj(self):
        return Qi(self.re, -self.im)

    def norm(self):
        return self.re * self.re + self.im * self.im

    def __truediv__(self, o):
        o = self._c(o)
        n = o.norm()
        if n == 0:
            raise ZeroDivisionError("Q(i) division by zero")
        p = self * o.conj()
        return Qi(p.re / n, p.im / n)

    def __rtruediv__(self, o):
        return self._c(o) / self

    def __eq__(self, o):
        if isinstance(o, bool):
            return False
        if isinstance(o, Qi):
            return self.re == o.re and self.im == o.im
        if isinstance(o, (int, Fraction)):
            return self.im == 0 and self.re == o
        return NotImplemented

    def __hash__(self):
        return hash((self.re, self.im))

    def iszero(self):
        return self.re == 0 and self.im == 0

    def __repr__(self):
        return "Qi(%s,%s)" % (self.re, self.im)


def cj(x):
    return x.conj() if isinstance(x, Qi) else x


def iz(x):
    return x.iszero() if isinstance(x, Qi) else x == 0


def realpart(x):
    if isinstance(x, Qi):
        require(x.im == 0, "expected real element")
        return x.re
    return x


def enc(x):
    """canonical string of a scalar"""
    if isinstance(x, Qi):
        return "%s%s%si" % (x.re, "+" if x.im >= 0 else "-", abs(x.im)) if x.im != 0 else str(x.re)
    return str(x)


# ---- matrices ----
def zeros(n, m, z=Fraction(0)):
    return [[z for _ in range(m)] for _ in range(n)]


def eye(n):
    return [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]


def mm(A, B):
    n, k, m = len(A), len(B), len(B[0])
    require(len(A[0]) == k, "mm shape")
    out = []
    for i in range(n):
        row = []
        for j in range(m):
            s = Fraction(0)
            for t in range(k):
                if iz(A[i][t]) or iz(B[t][j]):
                    continue
                s = s + A[i][t] * B[t][j]
            row.append(s)
        out.append(row)
    return out


def madd(A, B):
    return [[a + b for a, b in zip(r, s)] for r, s in zip(A, B)]


def msub(A, B):
    return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]


def mscale(c, A):
    return [[c * a for a in r] for r in A]


def tr(A):
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def dag(A):
    return [[cj(A[i][j]) for i in range(len(A))] for j in range(len(A[0]))]


def sub(A, rows, cols):
    return [[A[i][j] for j in cols] for i in rows]


def is_zero_mat(A):
    return all(iz(x) for r in A for x in r)


def is_hermitian(A):
    n = len(A)
    if any(len(r) != n for r in A):
        return False
    for i in range(n):
        for j in range(i, n):
            if A[i][j] != cj(A[j][i]):
                return False
    return True


def is_symmetric(A):
    n = len(A)
    return all(len(r) == n for r in A) and all(A[i][j] == A[j][i] for i in range(n) for j in range(n))


def is_antisymmetric(A):
    n = len(A)
    return all(A[i][j] == -A[j][i] for i in range(n) for j in range(n))


def is_real_entries(A):
    return all((not isinstance(x, Qi)) or x.im == 0 for r in A for x in r)


def symm_part(A):
    n = len(A)
    return [[(A[i][j] + A[j][i]) / 2 for j in range(n)] for i in range(n)]


def antisymm_part(A):
    n = len(A)
    return [[(A[i][j] - A[j][i]) / 2 for j in range(n)] for i in range(n)]


def _rref_rank_det(A):
    n, m = len(A), len(A[0])
    M = [list(r) for r in A]
    rank = 0
    det = Fraction(1)
    sq = n == m
    for c in range(m):
        p = None
        for r in range(rank, n):
            if not iz(M[r][c]):
                p = r
                break
        if p is None:
            if sq:
                det = Fraction(0)
            continue
        if p != rank:
            M[rank], M[p] = M[p], M[rank]
            det = -det
        pv = M[rank][c]
        det = det * pv
        for r in range(rank + 1, n):
            if iz(M[r][c]):
                continue
            f = M[r][c] / pv
            M[r] = [x - f * y for x, y in zip(M[r], M[rank])]
        rank += 1
    if sq and rank < n:
        det = Fraction(0)
    return rank, det


def rank(A):
    return _rref_rank_det(A)[0]


def det(A):
    require(len(A) == len(A[0]), "det of non-square")
    return _rref_rank_det(A)[1]


def inv(A):
    n = len(A)
    M = [list(A[i]) + [Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]
    for c in range(n):
        p = None
        for r in range(c, n):
            if not iz(M[r][c]):
                p = r
                break
        require(p is not None, "singular matrix in inv")
        M[c], M[p] = M[p], M[c]
        pv = M[c][c]
        M[c] = [x / pv for x in M[c]]
        for r in range(n):
            if r != c and not iz(M[r][c]):
                f = M[r][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [r[n:] for r in M]


def schur(A, piv, rest):
    """A_rr - A_rp A_pp^{-1} A_pr"""
    App = sub(A, piv, piv)
    Arp = sub(A, rest, piv)
    Apr = sub(A, piv, rest)
    Arr = sub(A, rest, rest)
    return msub(Arr, mm(mm(Arp, inv(App)), Apr))


# ---- inertia of a Hermitian matrix: method A (congruence) ----
def inertia_congruence(H):
    """(n+, n-, n0) of a Hermitian matrix over Q or Q(i) by exact symmetric elimination."""
    require(is_hermitian(H), "inertia_congruence needs Hermitian")
    n = len(H)
    A = [list(r) for r in H]
    pos = neg = 0
    idx = list(range(n))
    while idx:
        k = None
        for i in idx:
            if not iz(A[i][i]):
                k = i
                break
        if k is None:
            pair = None
            for i in idx:
                for j in idx:
                    if i < j and not iz(A[i][j]):
                        pair = (i, j)
                        break
                if pair:
                    break
            if pair is None:
                break
            i, j = pair
            # v = e_i + a e_j with a in {1, i}; q = v* A v
            chosen = None
            for a in (Fraction(1), Qi(0, 1)):
                q = A[i][i] + cj(a) * A[j][i] + A[i][j] * a + cj(a) * a * A[j][j]
                if not iz(q):
                    chosen = a
                    break
            require(chosen is not None, "no isotropy-breaking vector")
            a = chosen
            # column op: col_i += a col_j ; row op: row_i += conj(a) row_j
            for r in range(n):
                A[r][i] = A[r][i] + A[r][j] * a
            for c in range(n):
                A[i][c] = A[i][c] + cj(a) * A[j][c]
            k = i
        d = A[k][k]
        dr = realpart(d)
        if dr > 0:
            pos += 1
        else:
            neg += 1
        for r in idx:
            if r == k or iz(A[r][k]):
                continue
            f = A[r][k] / d
            for c in idx:
                A[r][c] = A[r][c] - f * A[k][c]
        idx = [i for i in idx if i != k]
        for r in idx:
            A[r][k] = Fraction(0)
            A[k][r] = Fraction(0)
    return pos, neg, n - pos - neg


# ---- method B: Faddeev-LeVerrier + Descartes (all roots real) ----
def charpoly(A):
    """coefficients c[0..n], p(x)=sum c[k] x^(n-k), via Faddeev-LeVerrier over Q(i)"""
    n = len(A)
    M = zeros(n, n)
    c = [Fraction(1)]
    I = eye(n)
    for k in range(1, n + 1):
        M = madd(mm(A, M), mscale(c[-1], I)) if k > 1 else I
        AM = mm(A, M)
        ck = -sum((AM[i][i] for i in range(n)), Fraction(0)) / k
        c.append(ck)
    return [realpart(x) for x in c]


def inertia_descartes(H):
    require(is_hermitian(H), "inertia_descartes needs Hermitian")
    c = charpoly(H)
    n = len(H)
    z = 0
    while z < n and c[n - z] == 0:
        z += 1
    cp = c[: n - z + 1]

    def changes(seq):
        s = [x for x in seq if x != 0]
        return sum(1 for a, b in zip(s, s[1:]) if (a > 0) != (b > 0))

    m = len(cp) - 1
    pos = changes(cp)
    cm = [cp[k] * (-1 if (m - k) % 2 else 1) for k in range(m + 1)]
    neg = changes(cm)
    require(pos + neg == m, "Descartes count inconsistent (non-real roots?)")
    return pos, neg, z


def inertia(H):
    a = inertia_congruence(H)
    b = inertia_descartes(H)
    require(a == b, "inertia checkers disagree %s %s" % (a, b))
    return a


# ---- factoring and square classes ----
def _is_prime(n):
    if n < 2:
        return False
    sp = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in sp:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in sp:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _rho(n):
    if n % 2 == 0:
        return 2
    c = 1
    while True:
        x = y = 2
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = gcd(abs(x - y), n)
        if d != n:
            return d
        c += 1


def factor(n):
    require(n >= 1, "factor of non-positive")
    out = {}
    stack = [n]
    while stack:
        m = stack.pop()
        if m == 1:
            continue
        for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
            while m % p == 0:
                out[p] = out.get(p, 0) + 1
                m //= p
        if m == 1:
            continue
        if _is_prime(m):
            out[m] = out.get(m, 0) + 1
            continue
        r = isqrt(m)
        if r * r == m:
            stack += [r, r]
            continue
        d = _rho(m)
        stack += [d, m // d]
    return out


def sqfree_class(q):
    """class of rational q != 0 in Q*/Q*^2 as (sign, squarefree positive integer)"""
    q = fr(q)
    require(q != 0, "square class of zero")
    s = 1 if q > 0 else -1
    f = factor(abs(q.numerator) * q.denominator)
    sf = 1
    for p, e in f.items():
        if e % 2:
            sf *= p
    return (s, sf)


def norm_class(q):
    """class of rational q != 0 in Q*/N(Q(i)*): (sign, product of primes = 3 mod 4 with odd exponent)"""
    q = fr(q)
    require(q != 0, "norm class of zero")
    s = 1 if q > 0 else -1
    f = factor(abs(q.numerator) * q.denominator)
    sf = 1
    for p, e in f.items():
        if e % 2 and p % 4 == 3:
            sf *= p
    return (s, sf)


# ---- seeded RNG, independent of the random module ----
class Rng:
    def __init__(self, seed):
        self.s = seed & 0xFFFFFFFFFFFFFFFF

    def next(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)

    def randint(self, a, b):
        return a + self.next() % (b - a + 1)

    def frac(self, lo, hi, den_lo=1, den_hi=4):
        return Fraction(self.randint(lo, hi), self.randint(den_lo, den_hi))


def canon_json(obj):
    def default(x):
        if isinstance(x, Fraction):
            return str(x)
        if isinstance(x, Qi):
            return enc(x)
        raise TypeError(type(x).__name__)

    return json.dumps(obj, sort_keys=True, indent=1, default=default) + "\n"


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def matstr(A):
    return [[enc(x) for x in r] for r in A]
