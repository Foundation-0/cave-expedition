"""Helpers for check_dn.py and check_e8.py. Not run on its own.

Exact Q(sqrt2) numbers, float Fincke-Pohst enumeration with a safety margin, and exact
Bernstein conversion. Standard library only. Shares no code with the fold verifiers
under test."""
from fractions import Fraction as Fr
import math


class Q2:
    """a + b*sqrt(2), a, b rational."""
    __slots__ = ("a", "b")

    def __init__(self, a=0, b=0):
        self.a = Fr(a)
        self.b = Fr(b)

    def __add__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(self.a + o.a, self.b + o.b)
    __radd__ = __add__

    def __neg__(self):
        return Q2(-self.a, -self.b)

    def __sub__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(self.a - o.a, self.b - o.b)

    def __rsub__(self, o):
        return Q2(o) - self

    def __mul__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(self.a * o.a + 2 * self.b * o.b, self.a * o.b + self.b * o.a)
    __rmul__ = __mul__

    def conj(self):
        return Q2(self.a, -self.b)

    def inv(self):
        n = self.a * self.a - 2 * self.b * self.b
        if n == 0:
            raise ZeroDivisionError
        return Q2(self.a / n, -self.b / n)

    def __truediv__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return self * o.inv()

    def sign(self):
        a, b = self.a, self.b
        sa = (a > 0) - (a < 0)
        sb = (b > 0) - (b < 0)
        if sa == 0:
            return sb
        if sb == 0 or sa == sb:
            return sa
        # opposite signs: compare a^2 with 2 b^2
        d = a * a - 2 * b * b
        return sa if d > 0 else (-sa if d < 0 else 0)

    def __float__(self):
        return float(self.a) + float(self.b) * math.sqrt(2.0)

    def __eq__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return self.a == o.a and self.b == o.b

    def __hash__(self):
        return hash((self.a, self.b))

    def __repr__(self):
        return f"({self.a}+{self.b}r2)"


def binom(n, k):
    return math.comb(n, k)


def power_to_bernstein(c):
    """c[j] power coeffs (degree N=len(c)-1) -> Bernstein coeffs on [0,1]."""
    N = len(c) - 1
    out = []
    for k in range(N + 1):
        acc = Q2(0)
        for j in range(k + 1):
            acc = acc + c[j] * Fr(binom(k, j), binom(N, j))
        out.append(acc)
    return out


def poly_mul(p, q):
    r = [Q2(0) for _ in range(len(p) + len(q) - 1)]
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            r[i + j] = r[i + j] + x * y
    return r


def poly_add(p, q):
    n = max(len(p), len(q))
    return [(p[i] if i < len(p) else Q2(0)) + (q[i] if i < len(q) else Q2(0)) for i in range(n)]


def fincke_pohst(G, R):
    """All integer m (as tuples) with m G m^T <= R, using floats. G: list of float rows (SPD).
    Caller must add a margin to R and re-check exactly."""
    n = len(G)
    # Cholesky-type decomposition q[i][i], q[i][j] (j>i): m G m = sum_i q_ii (m_i + sum_{j>i} q_ij m_j)^2
    A = [row[:] for row in G]
    q = [[0.0] * n for _ in range(n)]
    for i in range(n):
        q[i][i] = A[i][i]
        for j in range(i + 1, n):
            q[i][j] = A[i][j] / A[i][i]
        for j in range(i + 1, n):
            for k in range(j, n):
                A[j][k] -= q[i][j] * q[i][k] * q[i][i]
                A[k][j] = A[j][k]
    out = []
    m = [0] * n

    def rec(i, rem):
        c = -sum(q[i][j] * m[j] for j in range(i + 1, n))
        if rem < 0:
            return
        w = math.sqrt(rem / q[i][i])
        lo = math.ceil(c - w - 1e-9)
        hi = math.floor(c + w + 1e-9)
        for x in range(lo, hi + 1):
            m[i] = x
            r = rem - q[i][i] * (x - c) ** 2
            if i == 0:
                if r >= -1e-9:
                    out.append(tuple(m))
            else:
                rec(i - 1, r)
        m[i] = 0

    rec(n - 1, R)
    return out
