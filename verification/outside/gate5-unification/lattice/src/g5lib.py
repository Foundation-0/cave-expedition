"""Clean-room exact toolkit for the Gate 5 lattice pair.

Fields: int / Fraction (Q) and Q2 (Q(sqrt 2), pairs a + b*sqrt 2).  No floats, no numpy,
no bare assert.  Everything here is written from the mathematics of the bar framework
(cross-polytope cell, bridge bars, strain), not copied from the upstream scripts.
"""
from fractions import Fraction
import hashlib
import json

NS = 8  # default dimension


class LibError(Exception):
    pass


def require(cond, msg):
    if not cond:
        raise LibError(msg)


# ------------------------------------------------------------------ Q(sqrt 2)
class Q2:
    __slots__ = ("a", "b")

    def __init__(self, a=0, b=0):
        self.a = Fraction(a)
        self.b = Fraction(b)

    @staticmethod
    def lift(x):
        return x if isinstance(x, Q2) else Q2(x, 0)

    def __add__(self, o):
        o = Q2.lift(o)
        return Q2(self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __sub__(self, o):
        o = Q2.lift(o)
        return Q2(self.a - o.a, self.b - o.b)

    def __rsub__(self, o):
        return Q2.lift(o) - self

    def __neg__(self):
        return Q2(-self.a, -self.b)

    def __mul__(self, o):
        o = Q2.lift(o)
        return Q2(self.a * o.a + 2 * self.b * o.b, self.a * o.b + self.b * o.a)

    __rmul__ = __mul__

    def norm(self):
        return self.a * self.a - 2 * self.b * self.b

    def __truediv__(self, o):
        o = Q2.lift(o)
        n = o.norm()
        require(n != 0, "Q2 division by zero")
        return self * Q2(o.a / n, -o.b / n)

    def __rtruediv__(self, o):
        return Q2.lift(o) / self

    def __eq__(self, o):
        if isinstance(o, (int, Fraction)):
            return self.b == 0 and self.a == o
        if isinstance(o, Q2):
            return self.a == o.a and self.b == o.b
        return NotImplemented

    def __ne__(self, o):
        r = self.__eq__(o)
        return r if r is NotImplemented else not r

    def __hash__(self):
        return hash((self.a, self.b))

    def __bool__(self):
        return self.a != 0 or self.b != 0

    def sign(self):
        a, b = self.a, self.b
        if a == 0 and b == 0:
            return 0
        if a >= 0 and b >= 0:
            return 1
        if a <= 0 and b <= 0:
            return -1
        d = a * a - 2 * b * b
        if a > 0:
            return 1 if d > 0 else -1
        return -1 if d > 0 else 1

    def __repr__(self):
        return enc(self)


def sgn(x):
    if isinstance(x, Q2):
        return x.sign()
    return (x > 0) - (x < 0)


def enc(x):
    if isinstance(x, Q2):
        if x.b == 0:
            return enc(x.a)
        return enc(x.a) + "+" + enc(x.b) + "*sqrt2"
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else "%d/%d" % (x.numerator, x.denominator)


def dec(s):
    if "sqrt2" in s:
        a, b = s.split("+", 1) if not s.startswith("-") else (s[: s.index("+")], s[s.index("+") + 1:])
        return Q2(Fraction(a), Fraction(b.replace("*sqrt2", "")))
    return Fraction(s)


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def encmat(M):
    return [[enc(x) for x in row] for row in M]


# ------------------------------------------------------------------ RNG
class Rng:
    """splitmix64: version independent, seeded."""

    def __init__(self, seed):
        self.s = seed & 0xFFFFFFFFFFFFFFFF

    def next(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)

    def below(self, n):
        lim = (1 << 64) - ((1 << 64) % n)
        while True:
            x = self.next()
            if x < lim:
                return x % n

    def rng(self, lo, hi):  # inclusive
        return lo + self.below(hi - lo + 1)


# ------------------------------------------------------------------ small dense algebra
def zeros(r, c):
    return [[0] * c for _ in range(r)]


def eye(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def transpose(A):
    return [list(r) for r in zip(*A)] if A else []


def matmul(A, B):
    Bt = transpose(B)
    out = []
    for row in A:
        nzr = [(k, v) for k, v in enumerate(row) if v != 0]
        o = []
        for col in Bt:
            acc = 0
            for k, v in nzr:
                w = col[k]
                if w != 0:
                    acc = acc + v * w
            o.append(acc)
        out.append(o)
    return out


def madd(A, B, sign=1):
    return [[a + sign * b for a, b in zip(r, s)] for r, s in zip(A, B)]


def mscale(c, A):
    return [[c * x for x in r] for r in A]


def is_zero_mat(A):
    return all(x == 0 for r in A for x in r)


def det_small(M):
    n = len(M)
    A = [list(r) for r in M]
    d = 1
    for c in range(n):
        p = next((r for r in range(c, n) if A[r][c] != 0), None)
        if p is None:
            return 0
        if p != c:
            A[c], A[p] = A[p], A[c]
            d = -d
        d = d * A[c][c]
        inv = 1 / A[c][c] if not isinstance(A[c][c], int) else Fraction(1, A[c][c])
        for r in range(c + 1, n):
            if A[r][c] != 0:
                f = A[r][c] * inv
                for k in range(c, n):
                    A[r][k] = A[r][k] - f * A[c][k]
    return d


def solve_dense(G, V):
    """G (k x k, invertible) X = V (k x q). Exact."""
    k = len(G)
    q = len(V[0]) if V else 0
    A = [list(G[i]) + list(V[i]) for i in range(k)]
    for c in range(k):
        p = next((r for r in range(c, k) if A[r][c] != 0), None)
        require(p is not None, "singular Gram in solve_dense")
        A[c], A[p] = A[p], A[c]
        inv = Fraction(1) / A[c][c] if isinstance(A[c][c], (int, Fraction)) else 1 / A[c][c]
        A[c] = [x * inv for x in A[c]]
        for r in range(k):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [A[i][k:] for i in range(k)]


# ------------------------------------------------------------------ sparse RREF
def rref_sparse(rows, ncols):
    """rows: list of dict col->val.  Returns dict pivotcol -> row (dict, pivot normalised to 1, fully reduced)."""
    piv = {}
    for row in rows:
        r = dict(row)
        # reduce by existing pivots
        for pc in sorted(c for c in r if c in piv):
            if pc in r:
                f = r[pc]
                if f != 0:
                    for c2, v2 in piv[pc].items():
                        nv = r.get(c2, 0) - f * v2
                        if nv == 0:
                            r.pop(c2, None)
                        else:
                            r[c2] = nv
        r = {c: v for c, v in r.items() if v != 0}
        # a reduction by one pivot may re-create entries in earlier pivot columns; loop until stable
        changed = True
        while changed:
            changed = False
            for pc in [c for c in r if c in piv]:
                f = r[pc]
                for c2, v2 in piv[pc].items():
                    nv = r.get(c2, 0) - f * v2
                    if nv == 0:
                        r.pop(c2, None)
                    else:
                        r[c2] = nv
                changed = True
        if not r:
            continue
        pc = min(r)
        inv = 1 / r[pc] if not isinstance(r[pc], int) else Fraction(1, r[pc])
        r = {c: v * inv for c, v in r.items()}
        # eliminate new pivot column from old pivot rows
        for opc, orow in piv.items():
            if pc in orow:
                f = orow[pc]
                for c2, v2 in r.items():
                    nv = orow.get(c2, 0) - f * v2
                    if nv == 0:
                        orow.pop(c2, None)
                    else:
                        orow[c2] = nv
        piv[pc] = r
    return piv


def nullspace_sparse(rows, ncols):
    piv = rref_sparse(rows, ncols)
    free = [c for c in range(ncols) if c not in piv]
    basis = []
    for f in free:
        v = [0] * ncols
        v[f] = 1
        for pc, row in piv.items():
            if f in row:
                v[pc] = -row[f]
        basis.append(v)
    return basis, len(piv)


def rank_sparse(rows, ncols):
    return len(rref_sparse(rows, ncols))


def solve_consistent(Delta, Rhs):
    """Delta X = Rhs, Delta (m x m) possibly singular, consistent; free variables 0. Exact; verified."""
    m = len(Delta)
    q = len(Rhs[0])
    rows = []
    for i in range(m):
        d = {j: v for j, v in enumerate(Delta[i]) if v != 0}
        for j in range(q):
            if Rhs[i][j] != 0:
                d[m + j] = Rhs[i][j]
        rows.append(d)
    piv = rref_sparse(rows, m + q)
    X = [[0] * q for _ in range(m)]
    for pc, row in piv.items():
        require(pc < m, "inconsistent system in solve_consistent")
        for j in range(q):
            X[pc][j] = row.get(m + j, 0)
    chk = matmul(Delta, X)
    require(chk == Rhs, "solve_consistent verification failed")
    return X


# ------------------------------------------------------------------ inertia, SNF, classes
def congruence_diagonal(S):
    """Diagonalise symmetric S by congruence over the field; return the nonzero diagonal entries."""
    n = len(S)
    A = [list(r) for r in S]
    require(all(A[i][j] == A[j][i] for i in range(n) for j in range(n)), "matrix not symmetric")
    diag = []
    idx = list(range(n))
    while True:
        m = len(A)
        if m == 0:
            break
        p = next((i for i in range(m) if A[i][i] != 0), None)
        if p is None:
            pr = next(((i, j) for i in range(m) for j in range(i + 1, m) if A[i][j] != 0), None)
            if pr is None:
                break
            i, j = pr
            # replace e_i by e_i + e_j: new A[i][i] = 2 A[i][j]
            for k in range(m):
                A[i][k] = A[i][k] + A[j][k]
            for k in range(m):
                A[k][i] = A[k][i] + A[k][j]
            p = i
        d = A[p][p]
        inv = Fraction(1) / d if isinstance(d, (int, Fraction)) else 1 / d
        keep = [i for i in range(m) if i != p]
        B = [[A[i][j] - A[i][p] * inv * A[p][j] for j in keep] for i in keep]
        diag.append(d)
        A = B
    return diag


def inertia(S):
    d = congruence_diagonal(S)
    pos = sum(1 for x in d if sgn(x) > 0)
    neg = sum(1 for x in d if sgn(x) < 0)
    return [pos, neg, len(S) - pos - neg]


def squarefree_class(q, limit=2_000_000):
    """class of a nonzero rational mod squares: (sign, squarefree numerator*denominator part, unresolved flag)."""
    q = Fraction(q)
    require(q != 0, "zero has no square class")
    sign = -1 if q < 0 else 1
    n = abs(q.numerator) * abs(q.denominator)
    out = 1
    p = 2
    unresolved = False
    while p * p <= n and p <= limit:
        c = 0
        while n % p == 0:
            n //= p
            c += 1
        if c % 2:
            out *= p
        p += 1 if p == 2 else 2
    if n > 1:
        from math import isqrt
        if isqrt(n) ** 2 == n:
            pass
        elif n < limit * limit:
            out *= n
        else:
            unresolved = True
            out *= n
    return [sign, out, unresolved]


def q2_is_square(x):
    x = Q2.lift(x)
    if x == 0:
        return True
    from math import isqrt
    N = x.norm()
    if N < 0:
        return False
    num, den = N.numerator, N.denominator
    rn, rd = isqrt(num), isqrt(den)
    if rn * rn != num or rd * rd != den:
        return False
    n = Fraction(rn, rd)
    for sg in (1, -1):
        c2 = (x.a + sg * n) / 2
        if c2 < 0:
            continue
        a, b = c2.numerator, c2.denominator
        ra, rb = isqrt(a), isqrt(b)
        if ra * ra == a and rb * rb == b:
            c = Fraction(ra, rb)
            if c == 0:
                if x.b == 0 and x.a >= 0:
                    d2 = x.a / 2
                    da, db = isqrt(d2.numerator), isqrt(d2.denominator)
                    if da * da == d2.numerator and db * db == d2.denominator:
                        return True
                continue
            return True
    return False


def snf_diag(M):
    """Smith normal form diagonal of an integer matrix (list of lists of int)."""
    A = [[int(x) for x in r] for r in M]
    m, n = len(A), len(A[0])
    out = []
    r0 = 0
    while r0 < min(m, n):
        # find smallest nonzero entry in submatrix
        best = None
        for i in range(r0, m):
            for j in range(r0, n):
                if A[i][j] != 0 and (best is None or abs(A[i][j]) < abs(A[best[0]][best[1]])):
                    best = (i, j)
        if best is None:
            break
        i, j = best
        A[r0], A[i] = A[i], A[r0]
        for row in A:
            row[r0], row[j] = row[j], row[r0]
        while True:
            p = A[r0][r0]
            done = True
            for i in range(r0 + 1, m):
                if A[i][r0] != 0:
                    q = A[i][r0] // p
                    A[i] = [x - q * y for x, y in zip(A[i], A[r0])]
                    if A[i][r0] != 0:
                        A[r0], A[i] = A[i], A[r0]
                        done = False
                        break
            if not done:
                continue
            for j in range(r0 + 1, n):
                if A[r0][j] != 0:
                    q = A[r0][j] // p
                    for row in A:
                        row[j] -= q * row[r0]
                    if A[r0][j] != 0:
                        for row in A:
                            row[r0], row[j] = row[j], row[r0]
                        done = False
                        break
            if not done:
                continue
            # divisibility condition
            bad = None
            for i in range(r0 + 1, m):
                for j in range(r0 + 1, n):
                    if A[i][j] % p != 0:
                        bad = i
                        break
                if bad is not None:
                    break
            if bad is not None:
                A[r0] = [x + y for x, y in zip(A[r0], A[bad])]
                continue
            break
        out.append(abs(A[r0][r0]))
        r0 += 1
    return out


def clear_denominators(M):
    from math import gcd
    den = 1
    for r in M:
        for x in r:
            d = Fraction(x).denominator
            den = den * d // gcd(den, d)
    return den, [[int(Fraction(x) * den) for x in r] for r in M]


# ------------------------------------------------------------------ the bar framework
def off_pairs(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def dims(n):
    return {"n": n, "u": 2 * n * n, "eps": n * (n + 1) // 2, "dL": n * n}


def vertex_pos(v, n):
    ax, sg = divmod(v, 2)
    x = [0] * n
    x[ax] = 1 if sg == 0 else -1
    return x


def sylvester(n3=3):
    N = 1 << n3
    return [[1 if bin(i & j).count("1") % 2 == 0 else -1 for j in range(N)] for i in range(N)]


def twisted_cycle(n):
    require(n >= 3, "n >= 3")
    C = [[0] * n for _ in range(n)]
    C[0][1] = -1
    C[0][n - 1] = -1
    C[1][0] = 1
    C[1][2] = -1
    for k in range(2, n - 1):
        C[k][k - 1] = -1
        C[k][k + 1] = -1
    C[n - 1][0] = 1
    C[n - 1][n - 2] = -1
    return C


def lattice_from_bridge(Bm):
    """L = 2I + B  (rows r_i = 2 e_i + b_i)."""
    n = len(Bm)
    return [[Bm[i][j] + (2 if i == j else 0) for j in range(n)] for i in range(n)]


def build_bars(L, lam=1, U=None):
    """Bars of the framework for lattice basis matrix L (rows).  A bar is (u, v, m, ell):
    length vector ell = x_v - x_u + m.L, with m the integer translation vector."""
    n = len(L)
    bars = []
    for i in range(n):
        for j in range(i + 1, n):
            for si in (0, 1):
                for ti in (0, 1):
                    v = 2 * i + si
                    u = 2 * j + ti
                    xv, xu = vertex_pos(v, n), vertex_pos(u, n)
                    ell = [lam * (xv[k] - xu[k]) for k in range(n)]
                    bars.append((u, v, [0] * n, ell))
    # bridge i joins +e_i (cell 0) to -e_i in cell e_i.  U (integer, unimodular) re-expresses the same
    # bars in a new basis: new basis rows L_new = U L_old, translation m_new = e_i U^{-1}; here L is the OLD
    # basis and U is the optional pair (U, Uinv) given to move to the new one (used by the carried test).
    for i in range(n):
        u, v = 2 * i, 2 * i + 1
        m = [1 if k == i else 0 for k in range(n)]
        xv, xu = vertex_pos(v, n), vertex_pos(u, n)
        ell = [lam * (xv[k] - xu[k]) + L[i][k] for k in range(n)]
        bars.append((u, v, m, ell))
    if U is not None:
        Um, Uinv = U
        out = []
        for (u, v, m, ell) in bars:
            m2 = [sum(m[k] * Uinv[k][j] for k in range(n)) for j in range(n)]
            out.append((u, v, m2, ell))
        bars = out
    return bars


def row_d0(bar, n):
    u, v, m, ell = bar
    d = {}
    for k in range(n):
        if ell[k] != 0:
            d[v * n + k] = ell[k]
            d[u * n + k] = -ell[k]
    return d


def row_ae(bar, n):
    ell = bar[3]
    d = {}
    for k in range(n):
        x = ell[k] * ell[k]
        if x != 0:
            d[k] = x
    for idx, (k, l) in enumerate(off_pairs(n)):
        x = 2 * ell[k] * ell[l]
        if x != 0:
            d[n + idx] = x
    return d


def row_Z(bar, n):
    m, ell = bar[2], bar[3]
    d = {}
    for k in range(n):
        if m[k] != 0:
            for l in range(n):
                if ell[l] != 0:
                    d[k * n + l] = m[k] * ell[l]
    return d


def densify(rows, ncols):
    out = []
    for r in rows:
        o = [0] * ncols
        for c, v in r.items():
            o[c] = v
        out.append(o)
    return out


def gram_w(rowsA, rowsB, ncolsA, ncolsB, w=Fraction(1, 2)):
    """A^T W B for sparse-row matrices, W = w I.  Dense result."""
    out = [[0] * ncolsB for _ in range(ncolsA)]
    for ra, rb in zip(rowsA, rowsB):
        for i, a in ra.items():
            wa = w * a
            oi = out[i]
            for j, b in rb.items():
                oi[j] = oi[j] + wa * b
    return out


def matrix_X(n, lam=1):
    """strain coordinates (eps) -> affine vertex displacement x_v . eps   (2n^2 x n(n+1)/2), integers."""
    nu, ne = 2 * n * n, n * (n + 1) // 2
    X = [[0] * ne for _ in range(nu)]
    pairs = off_pairs(n)
    for v in range(2 * n):
        x = [lam * c for c in vertex_pos(v, n)]
        for k in range(n):
            if x[k] != 0:
                X[v * n + k][k] += x[k]
        for c, (k, l) in enumerate(pairs):
            if x[k] != 0:
                X[v * n + l][n + c] += x[k]
            if x[l] != 0:
                X[v * n + k][n + c] += x[l]
    return X


def matrix_R(L):
    """strain coordinates (eps) -> lattice deformation dL = L . eps   (n^2 x n(n+1)/2)."""
    n = len(L)
    ne = n * (n + 1) // 2
    R = [[0] * ne for _ in range(n * n)]
    pairs = off_pairs(n)
    for j in range(n):
        for k in range(n):
            R[k * n + j][j] += L[k][j]
    for c, (j, l) in enumerate(pairs):
        for k in range(n):
            R[k * n + l][n + c] += L[k][j]
            R[k * n + j][n + c] += L[k][l]
    return R


def matrix_Phi(L, lam=1, Rmat=None):
    """Phi : (u, eps) -> (dx, dL) = (u + X eps, L eps), block upper triangular, shape (u + n^2) x (u + eps)."""
    n = len(L)
    nu, ne = 2 * n * n, n * (n + 1) // 2
    X = matrix_X(n, lam)
    R = matrix_R(L) if Rmat is None else Rmat
    rows = []
    for i in range(nu):
        r = [0] * (nu + ne)
        r[i] = 1
        for c in range(ne):
            r[nu + c] = X[i][c]
        rows.append(r)
    for i in range(n * n):
        r = [0] * (nu + ne)
        for c in range(ne):
            r[nu + c] = R[i][c]
        rows.append(r)
    return rows


class Framework:
    """All exact objects of one (lattice, bar set) pair."""

    def __init__(self, L, lam=1, U=None):
        self.L = [list(r) for r in L]
        self.lam = lam
        self.n = len(L)
        n = self.n
        self.nu = 2 * n * n
        self.ne = n * (n + 1) // 2
        self.ndl = n * n
        self.bars = build_bars(self.L, lam, U)
        self.nb = len(self.bars)
        self.d0 = [row_d0(b, n) for b in self.bars]
        self.ae = [row_ae(b, n) for b in self.bars]
        self.Z = [row_Z(b, n) for b in self.bars]

    # ---- direct (upstream-style) matrices: K, B, Delta, S, C
    def KBD(self):
        n = self.n
        Delta = gram_w(self.d0, self.d0, self.nu, self.nu)
        B = gram_w(self.d0, self.ae, self.nu, self.ne)
        K = gram_w(self.ae, self.ae, self.ne, self.ne)
        return K, B, Delta

    def schur_direct(self):
        K, B, Delta = self.KBD()
        nb = [[-x for x in r] for r in B]
        X = solve_consistent(Delta, nb)
        BT = transpose(B)
        S = madd(K, matmul(BT, X))
        return S, (K, B, Delta)

    def lat_KBD(self):
        Delta = gram_w(self.d0, self.d0, self.nu, self.nu)
        B = gram_w(self.d0, self.Z, self.nu, self.ndl)
        K = gram_w(self.Z, self.Z, self.ndl, self.ndl)
        return K, B, Delta

    def schur_lat_direct(self):
        K, B, Delta = self.lat_KBD()
        X = solve_consistent(Delta, [[-x for x in r] for r in B])
        S = madd(K, matmul(transpose(B), X))
        return S, (K, B, Delta)

    # ---- self-stress engine (a different elimination: S = 1/2 M^T Pi_Sigma M)
    def self_stress(self):
        rows = {}
        for e, d in enumerate(self.d0):
            for dof, v in d.items():
                rows.setdefault(dof, {})[e] = v
        basis, rk = nullspace_sparse([rows[k] for k in sorted(rows)], self.nb)
        return basis, rk

    def schur_selfstress(self, macro_rows, ncols, Y=None):
        if Y is None:
            Y, _ = self.self_stress()
        k = len(Y)
        if k == 0:
            return [[0] * ncols for _ in range(ncols)]
        G = [[sum((a * b for a, b in zip(Y[i], Y[j])), 0) for j in range(k)] for i in range(k)]
        V = []
        for y in Y:
            row = [0] * ncols
            for e, ye in enumerate(y):
                if ye != 0:
                    for c, v in macro_rows[e].items():
                        row[c] = row[c] + ye * v
            V.append(row)
        GV = solve_dense(G, V)
        VT = transpose(V)
        half = Fraction(1, 2)
        return [[half * sum((VT[i][t] * GV[t][j] for t in range(k)), 0) for j in range(ncols)] for i in range(ncols)]


def lattice_pullback(S_lat, R):
    return matmul(transpose(R), matmul(S_lat, R))


def tr(M):
    return sum((M[i][i] for i in range(len(M))), 0)


# ------------------------------------------------------------------ the two real fold curves
R2 = Q2(0, 1)


def _p(a, b):
    return Q2(a, b)


def L8_of_s(s):
    """AUDIT-017 curve L_8(s) over Q(sqrt 2), s rational: rows a_pm on the diagonal, b_pm * H_ij off it."""
    s = Fraction(s)
    s2 = s * s
    Dp = _p(1, 2) + _p(-1, 2) * s2
    Dm = _p(-1, 2) + _p(1, 2) * s2
    Nap = _p(6, 5) + _p(-6, 5) * s2
    Nam = _p(2, 3) + _p(-2, 3) * s2
    Nb = _p(0, 2) * s
    H = sylvester(3)
    ap, am = Nap / Dp, Nam / Dm
    bp, bm = Nb / Dp, Nb / Dm
    Iplus = [i for i in range(8) if H[i][i] == 1]
    L = []
    for i in range(8):
        row = []
        for j in range(8):
            if i == j:
                row.append(ap if i in Iplus else am)
            else:
                row.append((bp if i in Iplus else bm) * H[i][j])
        L.append(row)
    return L, Iplus


def Ln_of_s(n, s):
    """AUDIT-009 curve L_n(s) = d I + t C_n, t = 2s/(1+s^2), a = sqrt2 (1-s^2)/(1+s^2), d = 2 + a."""
    s = Fraction(s)
    t = 2 * s / (1 + s * s)
    a = R2 * (Fraction(1) - s * s) / (1 + s * s)
    d = a + 2
    C = twisted_cycle(n)
    return [[(d if i == j else 0) + t * C[i][j] for j in range(n)] for i in range(n)]


def L_Dn_rational_point(n, a, t):
    require(a * a + 2 * t * t == 2, "point not on the bar conic a^2 + 2 t^2 = 2")
    C = twisted_cycle(n)
    return [[(2 + a if i == j else 0) + t * C[i][j] for j in range(n)] for i in range(n)]


def L_E8_s1():
    H = sylvester(3)
    return [[(2 if i == j else 0) + Fraction(H[i][j], 2) for j in range(8)] for i in range(8)]
