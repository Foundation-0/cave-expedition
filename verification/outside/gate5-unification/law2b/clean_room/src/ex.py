"""Exact arithmetic library for the second (clean-room) checker.  Standard library only.
Nothing here uses floats.  No bare assert: failures raise RuntimeError via req()."""
from fractions import Fraction as F
import math


def req(cond, msg):
    if not cond:
        raise RuntimeError("REQUIRE FAILED: " + msg)


# ------------------------------------------------------------------ matrices (lists of lists of Fraction)
def fm(rows):
    return [[F(x) for x in r] for r in rows]


def zeros(n, m):
    return [[F(0)] * m for _ in range(n)]


def eye(n):
    return [[F(1) if i == j else F(0) for j in range(n)] for i in range(n)]


def tr(A):
    return [list(c) for c in zip(*A)] if A else []


def mmul(A, B):
    Bt = tr(B)
    out = []
    for r in A:
        nzr = [(k, a) for k, a in enumerate(r) if a != 0]
        row = []
        for c in Bt:
            s = F(0)
            for k, a in nzr:
                b = c[k]
                if b != 0:
                    s += a * b
            row.append(s)
        out.append(row)
    return out


def madd(A, B):
    return [[a + b for a, b in zip(r, s)] for r, s in zip(A, B)]


def msub(A, B):
    return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]


def msc(c, A):
    c = F(c)
    return [[c * a for a in r] for r in A]


def sym_part(A):
    return [[(A[i][j] + A[j][i]) / 2 for j in range(len(A))] for i in range(len(A))]


def is_sym(A):
    n = len(A)
    return all(A[i][j] == A[j][i] for i in range(n) for j in range(i))


def sub(A, R, C):
    return [[A[i][j] for j in C] for i in R]


def rank(A):
    M = [list(r) for r in A]
    if not M:
        return 0
    n, m = len(M), len(M[0])
    r = 0
    for c in range(m):
        p = None
        for i in range(r, n):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        for i in range(r + 1, n):
            if M[i][c] != 0:
                f = M[i][c] / pv
                row_r = M[r]
                M[i] = [a - f * b for a, b in zip(M[i], row_r)]
        r += 1
        if r == n:
            break
    return r


def rref(A):
    M = [list(r) for r in A]
    n = len(M)
    m = len(M[0]) if M else 0
    piv = []
    r = 0
    for c in range(m):
        p = None
        for i in range(r, n):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [a / pv for a in M[r]]
        for i in range(n):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        piv.append(c)
        r += 1
        if r == n:
            break
    return M, piv


def nullspace(A, ncols=None):
    """basis (list of vectors) of {x : A x = 0}"""
    m = ncols if ncols is not None else (len(A[0]) if A else 0)
    if not A:
        return [[F(1) if i == j else F(0) for i in range(m)] for j in range(m)]
    R, piv = rref(A)
    free = [c for c in range(m) if c not in piv]
    basis = []
    for f in free:
        v = [F(0)] * m
        v[f] = F(1)
        for r, pc in enumerate(piv):
            v[pc] = -R[r][f]
        basis.append(v)
    return basis


def solve(A, B):
    """one solution X of A X = B (free variables 0) or None.  B is a matrix (list of rows)."""
    n, m = len(A), len(A[0])
    k = len(B[0])
    aug = [list(A[i]) + list(B[i]) for i in range(n)]
    R, piv = rref(aug)
    X = zeros(m, k)
    for r, pc in enumerate(piv):
        if pc >= m:
            return None
        for j in range(k):
            X[pc][j] = R[r][m + j]
    return X


def inv(A):
    n = len(A)
    aug = [list(A[i]) + [F(1) if i == j else F(0) for j in range(n)] for i in range(n)]
    R, piv = rref(aug)
    if piv[:n] != list(range(n)):
        return None
    return [r[n:] for r in R[:n]]


def det(A):
    n = len(A)
    M = [list(r) for r in A]
    d = F(1)
    for c in range(n):
        p = None
        for i in range(c, n):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            return F(0)
        if p != c:
            M[c], M[p] = M[p], M[c]
            d = -d
        d *= M[c][c]
        for i in range(c + 1, n):
            if M[i][c] != 0:
                f = M[i][c] / M[c][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[c])]
    return d


def schur(M, R, C):
    """Schur complement of the pivot block C in M: M[R,R] - M[R,C] M[C,C]^-1 M[C,R].  None if M[C,C] singular."""
    A = sub(M, C, C)
    if rank(A) < len(C):
        return None
    X = solve(A, sub(M, C, R))
    return msub(sub(M, R, R), mmul(sub(M, R, C), X))


# ------------------------------------------------------------------ inertia of a symmetric rational matrix
def inertia_cong(A):
    """(pos, neg, zero) by exact symmetric elimination (Sylvester).  A must be symmetric."""
    n = len(A)
    req(is_sym(A), "inertia_cong needs a symmetric matrix")
    M = [list(r) for r in A]
    pos = neg = 0
    active = list(range(n))
    while active:
        piv = None
        for i in active:
            if M[i][i] != 0:
                piv = i
                break
        if piv is None:
            pair = None
            for i in active:
                for j in active:
                    if i < j and M[i][j] != 0:
                        pair = (i, j)
                        break
                if pair:
                    break
            if pair is None:
                break
            i, j = pair
            for k in range(n):
                M[i][k] += M[j][k]
            for k in range(n):
                M[k][i] += M[k][j]
            continue
        d = M[piv][piv]
        if d > 0:
            pos += 1
        else:
            neg += 1
        rest = [i for i in active if i != piv]
        for i in rest:
            if M[i][piv] != 0:
                f = M[i][piv] / d
                for j in rest:
                    M[i][j] -= f * M[piv][j]
        for i in rest:
            M[i][piv] = F(0)
            M[piv][i] = F(0)
        active = rest
    return (pos, neg, len(active))


# ------------------------------------------------------------------ polynomials over Q (low -> high, Fractions)
def pstrip(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def pdeg(p):
    return len(pstrip(p)) - 1


def padd(a, b):
    n = max(len(a), len(b))
    return pstrip([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)])


def psub(a, b):
    n = max(len(a), len(b))
    return pstrip([(a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) for i in range(n)])


def pmul(a, b):
    a, b = pstrip(a), pstrip(b)
    if not a or not b:
        return []
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x != 0:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return pstrip(out)


def pdivmod(a, b):
    a, b = pstrip(a), pstrip(b)
    req(len(b) > 0, "division by zero polynomial")
    q = [F(0)] * max(len(a) - len(b) + 1, 0)
    r = list(a)
    while len(r) >= len(b) and r:
        c = r[-1] / b[-1]
        k = len(r) - len(b)
        q[k] = c
        for i, y in enumerate(b):
            r[i + k] -= c * y
        r = pstrip(r)
    return pstrip(q), r


def pder(a):
    return pstrip([i * a[i] for i in range(1, len(a))])


def pmonic(a):
    a = pstrip(a)
    return [x / a[-1] for x in a] if a else a


def pprim(a):
    """positive-scaled primitive integer-coefficient version (same roots, same sign pattern at every point)"""
    a = pstrip([F(x) for x in a])
    if not a:
        return a
    den = 1
    for x in a:
        den = den * x.denominator // math.gcd(den, x.denominator)
    ints = [int(x * den) for x in a]
    g = 0
    for x in ints:
        g = math.gcd(g, x)
    return [F(x // g) for x in ints]


def pgcd(a, b):
    a, b = pprim(a), pprim(b)
    while b:
        _, r = pdivmod(a, b)
        a, b = b, pprim(r)
    return pmonic(a)


def peval(a, x):
    s = F(0)
    x = F(x)
    for c in reversed(a):
        s = s * x + c
    return s


def sgn(x):
    return (x > 0) - (x < 0)


def sturm_chain(p, q=None):
    """generalised Sturm chain p0=p, p1=q (default p'), p_{k+1} = -rem(p_{k-1}, p_k), positively rescaled"""
    p = pprim(p)
    q = pprim(pder(p) if q is None else q)
    chain = [p]
    if q:
        chain.append(q)
    while len(chain) >= 2:
        _, r = pdivmod(chain[-2], chain[-1])
        if not r:
            break
        chain.append(pprim([-x for x in r]))
    return chain


def var_inf(chain, plus):
    signs = []
    for c in chain:
        s = sgn(c[-1])
        if not plus and (len(c) - 1) % 2 == 1:
            s = -s
        if s != 0:
            signs.append(s)
    return sum(1 for i in range(len(signs) - 1) if signs[i] != signs[i + 1])


def var_at(chain, x):
    signs = [sgn(peval(c, x)) for c in chain]
    signs = [s for s in signs if s != 0]
    return sum(1 for i in range(len(signs) - 1) if signs[i] != signs[i + 1])


def n_real_distinct(p):
    p = pstrip(p)
    if len(p) <= 1:
        return 0
    ch = sturm_chain(p)
    return var_inf(ch, False) - var_inf(ch, True)


def n_roots_between(p, a, b):
    """distinct real roots in (a, b], p(a), p(b) must be non-zero or the count is of the half-open interval by Sturm"""
    ch = sturm_chain(p)
    return var_at(ch, a) - var_at(ch, b)


def cauchy_index(D, N):
    """Cauchy index over R of N/D (jumps from -inf to +inf count +1) = Var(-inf) - Var(+inf) of chain (D, N, ...)"""
    D, N = pstrip(D), pstrip(N)
    if not N:
        return 0
    ch = sturm_chain(D, N)
    return var_inf(ch, False) - var_inf(ch, True)


def yun(p):
    """squarefree factorisation: list of (i, f_i), p ~ prod f_i^i, f_i squarefree, pairwise coprime, monic"""
    p = pmonic(p)
    out = []
    if len(p) <= 1:
        return out
    a = pgcd(p, pder(p))
    b, r0 = pdivmod(p, a)
    req(not r0, "yun division")
    c, r1 = pdivmod(pder(p), a)
    req(not r1, "yun division 2")
    d = psub(c, pder(b))
    i = 1
    while pdeg(b) > 0:
        ai = pgcd(b, d) if d else pmonic(b)
        if pdeg(ai) > 0:
            out.append((i, ai))
        b, r2 = pdivmod(b, ai)
        req(not r2, "yun step")
        c, r3 = pdivmod(d, ai)
        req(not r3, "yun step 2")
        d = psub(c, pder(b))
        i += 1
    return out


def n_real_with_mult(p):
    return sum(i * n_real_distinct(f) for i, f in yun(p))


# ------------------------------------------------------------------ characteristic polynomial
def charpoly(A):
    """monic characteristic polynomial, low->high, exact Faddeev-LeVerrier"""
    n = len(A)
    Mk = zeros(n, n)
    c = [F(0)] * (n + 1)
    c[n] = F(1)
    for k in range(1, n + 1):
        Mk = mmul(A, Mk)
        for i in range(n):
            Mk[i][i] += c[n - k + 1]
        AM = mmul(A, Mk)
        t = sum(AM[i][i] for i in range(n))
        c[n - k] = -t / k
    return c


def charpoly_int(A):
    """integer matrix -> integer charpoly coefficients (low->high), Faddeev-LeVerrier with exact division"""
    n = len(A)
    nz = [[(j, a) for j, a in enumerate(r) if a != 0] for r in A]

    def mul(Mx):
        out = []
        for i in range(n):
            row = [0] * n
            for k, a in nz[i]:
                rk = Mx[k]
                for j in range(n):
                    if rk[j]:
                        row[j] += a * rk[j]
            out.append(row)
        return out

    Mk = [[0] * n for _ in range(n)]
    c = [0] * (n + 1)
    c[n] = 1
    for k in range(1, n + 1):
        Mk = mul(Mk)
        for i in range(n):
            Mk[i][i] += c[n - k + 1]
        AM = mul(Mk)
        t = sum(AM[i][i] for i in range(n))
        req(t % k == 0, "Faddeev-LeVerrier exact division")
        c[n - k] = -t // k
    return c


def meval(p, A):
    n = len(A)
    R = zeros(n, n)
    for c in reversed(pstrip(p)):
        R = mmul(R, A)
        for i in range(n):
            R[i][i] += c
    return R


# ------------------------------------------------------------------ spectral inertia of a real polynomial (roots with Re>0, Re<0, Re=0)
def _iy_parts(p):
    U, V = [], []
    for k, c in enumerate(p):
        z = [(1, 0), (0, 1), (-1, 0), (0, -1)][k % 4]
        U.append(c * z[0])
        V.append(c * z[1])
    return pstrip(U), pstrip(V)


def n_imag_axis(p):
    """number of roots (with multiplicity) of real polynomial p on the imaginary axis (including 0).
    z = valuation at 0; S = gcd(p(x), p(-x)) = x^z T(x^2); nonzero imaginary roots <-> negative real roots t of T, each gives +-i sqrt(-t)."""
    p = pstrip([F(x) for x in p])
    z = 0
    while z < len(p) and p[z] == 0:
        z += 1
    pm = [c * (-1) ** k for k, c in enumerate(p)]
    S = pgcd(p, pm)
    # strip x^z
    req(all(S[i] == 0 for i in range(z)) and S[z] != 0, "S has exactly x^z at the origin")
    S2 = S[z:]
    req(all(S2[k] == 0 for k in range(1, len(S2), 2)), "S/x^z is even")
    T = [S2[k] for k in range(0, len(S2), 2)]
    total = z
    for i, f in yun(T):
        ch = sturm_chain(f)
        neg = var_inf(ch, False) - var_at(ch, F(0))
        total += 2 * i * neg
    return total


def spectral_inertia_poly(p):
    """(n_pos, n_neg, n_zero) = counts of roots of real polynomial p with Re>0, Re<0, Re=0, with multiplicity"""
    p = pstrip([F(x) for x in p])
    n = len(p) - 1
    nim = n_imag_axis(p)
    m = n - nim
    if m == 0:
        return (0, 0, nim)
    U, V = _iy_parts(p)
    if not U or not V:
        d = 0  # p even or odd: root set symmetric under x -> -x, so equal numbers in both open half planes
    else:
        I1 = cauchy_index(U, V)   # Ind(V/U)
        I2 = cauchy_index(V, U)   # Ind(U/V)
        even_nim = (nim % 2 == 0)
        even_m = (m % 2 == 0)
        if even_nim and even_m:
            d = -I1
        elif even_nim and not even_m:
            d = I2
        elif (not even_nim) and even_m:
            d = I2
        else:
            d = -I1
    req((m + d) % 2 == 0 and abs(d) <= m, "RHP/LHP difference consistent")
    nL = (m + d) // 2
    nR = (m - d) // 2
    return (nR, nL, nim)


def spectral_inertia(A):
    return spectral_inertia_poly(charpoly(A))
