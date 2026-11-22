"""Exact arithmetic helpers: Fraction, Q(sqrt2), Q(i), sparse Gauss-Jordan.
No floats anywhere."""
from fractions import Fraction


def F(x):
    if isinstance(x, (Fraction, QS2, Gq)):
        return x
    return Fraction(x)


class QS2:
    """a + b*sqrt(2), a,b rational."""
    __slots__ = ("a", "b")

    def __init__(self, a=0, b=0):
        self.a = Fraction(a)
        self.b = Fraction(b)

    @staticmethod
    def c(x):
        if isinstance(x, QS2):
            return x
        if isinstance(x, (int, Fraction)):
            return QS2(x, 0)
        return NotImplemented

    def __add__(s, o):
        o = QS2.c(o)
        if o is NotImplemented:
            return o
        return QS2(s.a + o.a, s.b + o.b)
    __radd__ = __add__

    def __neg__(s):
        return QS2(-s.a, -s.b)

    def __sub__(s, o):
        o = QS2.c(o)
        if o is NotImplemented:
            return o
        return QS2(s.a - o.a, s.b - o.b)

    def __rsub__(s, o):
        o = QS2.c(o)
        if o is NotImplemented:
            return o
        return QS2(o.a - s.a, o.b - s.b)

    def __mul__(s, o):
        o = QS2.c(o)
        if o is NotImplemented:
            return o
        return QS2(s.a * o.a + 2 * s.b * o.b, s.a * o.b + s.b * o.a)
    __rmul__ = __mul__

    def inv(s):
        d = s.a * s.a - 2 * s.b * s.b
        if d == 0:
            raise ZeroDivisionError("QS2 inverse of zero")
        return QS2(s.a / d, -s.b / d)

    def __truediv__(s, o):
        o = QS2.c(o)
        if o is NotImplemented:
            return o
        return s * o.inv()

    def __rtruediv__(s, o):
        o = QS2.c(o)
        if o is NotImplemented:
            return o
        return o * s.inv()

    def __eq__(s, o):
        o = QS2.c(o)
        if o is NotImplemented:
            return False
        return s.a == o.a and s.b == o.b

    def __ne__(s, o):
        return not s.__eq__(o)

    def __bool__(s):
        return bool(s.a) or bool(s.b)

    def __hash__(s):
        return hash((s.a, s.b))

    def __repr__(s):
        return "%s%+d/%d*r2" % (s.a, s.b.numerator, s.b.denominator) if s.b else str(s.a)

    def sq_is_pos_check(s):
        return None


class Gq:
    """re + im*i, rational parts."""
    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re = Fraction(re)
        self.im = Fraction(im)

    @staticmethod
    def c(x):
        if isinstance(x, Gq):
            return x
        if isinstance(x, (int, Fraction)):
            return Gq(x, 0)
        return NotImplemented

    def __add__(s, o):
        o = Gq.c(o)
        if o is NotImplemented:
            return o
        return Gq(s.re + o.re, s.im + o.im)
    __radd__ = __add__

    def __neg__(s):
        return Gq(-s.re, -s.im)

    def __sub__(s, o):
        o = Gq.c(o)
        if o is NotImplemented:
            return o
        return Gq(s.re - o.re, s.im - o.im)

    def __rsub__(s, o):
        o = Gq.c(o)
        if o is NotImplemented:
            return o
        return Gq(o.re - s.re, o.im - s.im)

    def __mul__(s, o):
        o = Gq.c(o)
        if o is NotImplemented:
            return o
        return Gq(s.re * o.re - s.im * o.im, s.re * o.im + s.im * o.re)
    __rmul__ = __mul__

    def conj(s):
        return Gq(s.re, -s.im)

    def inv(s):
        d = s.re * s.re + s.im * s.im
        if d == 0:
            raise ZeroDivisionError("Gq inverse of zero")
        return Gq(s.re / d, -s.im / d)

    def __truediv__(s, o):
        o = Gq.c(o)
        if o is NotImplemented:
            return o
        return s * o.inv()

    def __rtruediv__(s, o):
        o = Gq.c(o)
        if o is NotImplemented:
            return o
        return o * s.inv()

    def __eq__(s, o):
        o = Gq.c(o)
        if o is NotImplemented:
            return False
        return s.re == o.re and s.im == o.im

    def __ne__(s, o):
        return not s.__eq__(o)

    def __bool__(s):
        return bool(s.re) or bool(s.im)

    def __hash__(s):
        return hash((s.re, s.im))

    def __repr__(s):
        if s.im:
            return "(%s%+di)" % (s.re, 0) if False else "(%s,%s)" % (s.re, s.im)
        return str(s.re)


def conj(x):
    if isinstance(x, Gq):
        return x.conj()
    return x


# ---------------------------------------------------------------- matrices
def zeros(r, c):
    return [[Fraction(0)] * c for _ in range(r)]


def eye(n):
    M = zeros(n, n)
    for i in range(n):
        M[i][i] = Fraction(1)
    return M


def T(A):
    return [list(col) for col in zip(*A)] if A else []


def ct(A):
    return [[conj(x) for x in col] for col in zip(*A)] if A else []


def mm(A, B):
    """Product with zero skipping."""
    nb = len(B[0]) if B else 0
    nz = [[(j, v) for j, v in enumerate(row) if v] for row in B]
    out = []
    for row in A:
        acc = {}
        for k, a in enumerate(row):
            if a:
                for j, b in nz[k]:
                    if j in acc:
                        acc[j] = acc[j] + a * b
                    else:
                        acc[j] = a * b
        r = [Fraction(0)] * nb
        for j, v in acc.items():
            r[j] = v
        out.append(r)
    return out


def madd(A, B, sgn=1):
    return [[x + sgn * y for x, y in zip(ra, rb)] for ra, rb in zip(A, B)]


def msc(c, A):
    return [[c * x for x in r] for r in A]


def is_zero(A):
    return all(not x for r in A for x in r)


def eq(A, B):
    if len(A) != len(B):
        return False
    for ra, rb in zip(A, B):
        if len(ra) != len(rb):
            return False
        for x, y in zip(ra, rb):
            if x != y:
                return False
    return True


def sub(A, r0, r1, c0, c1):
    return [list(r[c0:c1]) for r in A[r0:r1]]


# ------------------------------------------------------------ elimination
def rref(rows, ncols):
    """Gauss-Jordan on dict rows, pivoting only in columns < ncols.
    Returns (rows, pivots) with pivots = list of pivot columns (row i has pivot i)."""
    rows = [dict(r) for r in rows]
    piv = []
    r = 0
    nr = len(rows)
    for c in range(ncols):
        pr = None
        best = None
        for i in range(r, nr):
            if rows[i].get(c):
                ln = len(rows[i])
                if best is None or ln < best:
                    best = ln
                    pr = i
        if pr is None:
            continue
        rows[r], rows[pr] = rows[pr], rows[r]
        p = rows[r][c]
        if p != 1:
            rows[r] = {k: v / p for k, v in rows[r].items()}
        prow = rows[r]
        for i in range(nr):
            if i != r:
                f = rows[i].get(c)
                if f:
                    ri = rows[i]
                    for k, v in prow.items():
                        nv = ri.get(k, 0) - f * v
                        if nv:
                            ri[k] = nv
                        else:
                            ri.pop(k, None)
        piv.append(c)
        r += 1
        if r == nr:
            break
    return rows, piv


def todict(M):
    return [{j: v for j, v in enumerate(r) if v} for r in M]


def rank(M):
    if not M or not M[0]:
        return 0
    return len(rref(todict(M), len(M[0]))[1])


def nullspace(M, ncols):
    """Right nullspace basis (list of vectors length ncols)."""
    rows, piv = rref(todict(M), ncols)
    ps = set(piv)
    basis = []
    for f in range(ncols):
        if f in ps:
            continue
        v = [Fraction(0)] * ncols
        v[f] = Fraction(1)
        for i, pc in enumerate(piv):
            x = rows[i].get(f)
            if x:
                v[pc] = -x
        basis.append(v)
    return basis


def solve_consistent(A, RHS):
    """Solve A X = RHS, free variables set to 0. RHS list of rows. Raises if inconsistent."""
    n = len(A)
    m = len(RHS[0]) if RHS else 0
    rows = []
    for i in range(n):
        d = {j: v for j, v in enumerate(A[i]) if v}
        for j, v in enumerate(RHS[i]):
            if v:
                d[n + j] = v
        rows.append(d)
    rows, piv = rref(rows, len(A[0]))
    for i in range(len(piv), n):
        if rows[i]:
            raise ValueError("inconsistent system")
    X = [[Fraction(0)] * m for _ in range(len(A[0]))]
    for i, pc in enumerate(piv):
        for k, v in rows[i].items():
            if k >= len(A[0]):
                X[pc][k - len(A[0])] = v
    return X


def inverse(A):
    n = len(A)
    rows = []
    for i in range(n):
        d = {j: v for j, v in enumerate(A[i]) if v}
        d[n + i] = Fraction(1)
        rows.append(d)
    rows, piv = rref(rows, n)
    if len(piv) < n:
        raise ValueError("singular")
    X = zeros(n, n)
    for i, pc in enumerate(piv):
        for k, v in rows[i].items():
            if k >= n:
                X[pc][k - n] = v
    return X


def det(A):
    n = len(A)
    M = [list(r) for r in A]
    d = Fraction(1)
    for c in range(n):
        p = None
        for i in range(c, n):
            if M[i][c]:
                p = i
                break
        if p is None:
            return Fraction(0)
        if p != c:
            M[c], M[p] = M[p], M[c]
            d = -d
        d = d * M[c][c]
        inv = 1 / M[c][c] if not isinstance(M[c][c], (QS2, Gq)) else M[c][c].inv()
        for i in range(c + 1, n):
            if M[i][c]:
                f = M[i][c] * inv
                for k in range(c, n):
                    M[i][k] = M[i][k] - f * M[c][k]
    return d


def schur_blocks(A, B, Cc, D, solver=None):
    """D - C A^-1 B; refuses singular A."""
    Ai = inverse(A)  # raises on singular
    return madd(D, mm(Cc, mm(Ai, B)), -1)


def charpoly(M):
    """Faddeev-LeVerrier. Returns coefficients c[0..n] of det(xI - M) ascending
    (c[n] = 1). Entries must be Fractions."""
    n = len(M)
    if n == 0:
        return [Fraction(1)]
    coeff = [Fraction(0)] * (n + 1)
    coeff[n] = Fraction(1)
    Mk = eye(n)  # M_1 = I
    for k in range(1, n + 1):
        AM = mm(M, Mk)
        tr = sum((AM[i][i] for i in range(n)), Fraction(0))
        ck = -tr / k
        coeff[n - k] = ck
        # M_{k+1} = A M_k + c_{n-k} I
        Mk = [[AM[i][j] + (ck if i == j else 0) for j in range(n)] for i in range(n)]
    return coeff


def sign_changes(cs):
    s = [c for c in cs if c]
    return sum(1 for a, b in zip(s, s[1:]) if (a > 0) != (b > 0))


def inertia_charpoly(M):
    """(n+, n-, n0) of a real symmetric rational matrix via Descartes on the
    characteristic polynomial (all roots real)."""
    n = len(M)
    cs = charpoly(M)
    z = 0
    while z < n and not cs[z]:
        z += 1
    q = cs[z:]  # ascending, q[0] != 0
    deg = len(q) - 1
    pos = sign_changes(q[::-1])
    qm = [c if (i % 2 == 0) else -c for i, c in enumerate(q)]
    neg = sign_changes(qm[::-1])
    if pos + neg != deg:
        raise ValueError("Descartes count inconsistent: matrix not real-diagonalisable?")
    return (pos, neg, z)
