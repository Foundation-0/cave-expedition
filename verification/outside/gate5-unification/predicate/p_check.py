"""Predicate evaluator for the ledger's "is a Schur-complement instance" criterion.

Exact arithmetic only (Fraction and null_panel.QI for Q(i)); no floats, no numpy,
no bare assert. Evaluates, on every system of the null panel(s):

  P0   strict existence: pivot block A invertible, S = D - C A^-1 B exists
  P0g  generalized existence with a Moore-Penrose inverse (SF-01 wording G_oo^+)
  P1   Haynsworth inertia additivity In(M) = In(A) + In(S)      (Hermitian)
  P1g  the same with the generalized S (needs a range condition)
  P2   exact congruence V* M V = diag(A, S)                     (Hermitian)
  P3   integer Bareiss pivots: Jacobi sign rule matches inertia (Hermitian)
  P4a  positive rescaling; P4b block-diagonal congruence; P4c mixing congruence
  P5   det M = det A * det S
  P6   quotient property (M/A11)/(A/A11) = M/A
  P8   Loewner monotonicity of S (PSD systems with PD pivot block)

Inertia is computed two ways that share no algorithm: exact congruence
elimination (1x1 and 2x2 pivots) and Faddeev-LeVerrier characteristic
polynomial plus Descartes' rule (exact for real-rooted polynomials).

Must-fail controls are run first. Exit code: 0 all good; 1 a control passed
(a control must fail); 2 a textbook identity failed on the panel.
Output is JSON on stdout only. Run with python3 -I -B.
"""
import hashlib
import importlib.util
import json
import os
import random
import sys
from fractions import Fraction
from math import gcd

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("null_panel", os.path.join(_HERE, "null_panel.py"))
null_panel = importlib.util.module_from_spec(_spec)
sys.modules["null_panel"] = null_panel
_spec.loader.exec_module(null_panel)
QI = null_panel.QI

PANEL_SEEDS = (20261121, 11235813)  # the second seed is fresh: not used while building
PER_CELL = 30


class Refusal(ValueError):
    def __init__(self, code):
        ValueError.__init__(self, code)
        self.code = code


# ---------------------------------------------------------------- field utils
def const(x, v):
    return QI(v, 0) if isinstance(x, QI) else Fraction(v)


def conj(x):
    return x.conjugate()


def real_of(x):
    if isinstance(x, QI):
        if x.im != 0:
            raise Refusal("non_real_diagonal")
        return x.re
    return Fraction(x)


def sgn(x):
    r = real_of(x)
    return (r > 0) - (r < 0)


def zeros(r, c, x):
    z = const(x, 0)
    return [[z for _ in range(c)] for _ in range(r)]


def ident(n, x):
    Z = zeros(n, n, x)
    for i in range(n):
        Z[i][i] = const(x, 1)
    return Z


def mmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    out = []
    for i in range(n):
        row = []
        for j in range(p):
            acc = const(A[0][0], 0)
            for t in range(m):
                acc = acc + A[i][t] * B[t][j]
            row.append(acc)
        out.append(row)
    return out


def madd(A, B):
    return [[a + b for a, b in zip(r, s)] for r, s in zip(A, B)]


def msub(A, B):
    return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]


def mscale(c, A):
    return [[c * a for a in r] for r in A]


def ctr(A):
    return [[conj(A[i][j]) for i in range(len(A))] for j in range(len(A[0]))]


def sub(M, r0, r1, c0, c1):
    return [row[c0:c1] for row in M[r0:r1]]


def is_square(M):
    return len(M) > 0 and all(len(r) == len(M) for r in M)


def is_hermitian(M):
    n = len(M)
    return all(M[i][j] == conj(M[j][i]) for i in range(n) for j in range(n))


def inverse(A):
    n = len(A)
    if n == 0 or any(len(r) != n for r in A):
        raise Refusal("not_square")
    x = A[0][0]
    W = [list(A[i]) + ident(n, x)[i] for i in range(n)]
    for c in range(n):
        p = next((r for r in range(c, n) if W[r][c] != 0), None)
        if p is None:
            raise Refusal("singular_pivot")
        W[c], W[p] = W[p], W[c]
        inv = const(x, 1) / W[c][c]
        W[c] = [inv * v for v in W[c]]
        for r in range(n):
            if r != c and W[r][c] != 0:
                f = W[r][c]
                W[r] = [a - f * b for a, b in zip(W[r], W[c])]
    return [row[n:] for row in W]


def det(A):
    n = len(A)
    if n == 0 or any(len(r) != n for r in A):
        raise Refusal("not_square")
    W = [list(r) for r in A]
    d = const(A[0][0], 1)
    for c in range(n):
        p = next((r for r in range(c, n) if W[r][c] != 0), None)
        if p is None:
            return const(A[0][0], 0)
        if p != c:
            W[c], W[p] = W[p], W[c]
            d = -d
        d = d * W[c][c]
        for r in range(c + 1, n):
            if W[r][c] != 0:
                f = W[r][c] / W[c][c]
                W[r] = [a - f * b for a, b in zip(W[r], W[c])]
    return d


def blocks(M, k):
    n = len(M)
    if not is_square(M) or not (1 <= k <= n - 1):
        raise Refusal("bad_partition")
    return sub(M, 0, k, 0, k), sub(M, 0, k, k, n), sub(M, k, n, 0, k), sub(M, k, n, k, n)


def schur(M, k):
    """S = D - C A^-1 B; refuses a singular pivot block."""
    A, B, C, D = blocks(M, k)
    return msub(D, mmul(mmul(C, inverse(A)), B))


# ------------------------------------------------------------ inertia, way 1
def inertia_congruence(M):
    """Exact (n+, n-, n0) of a Hermitian matrix by congruence elimination."""
    if not is_square(M) or not is_hermitian(M):
        raise Refusal("not_hermitian")
    H = [list(r) for r in M]
    npos = nneg = 0
    while len(H) > 0:
        m = len(H)
        i = next((t for t in range(m) if H[t][t] != 0), None)
        if i is not None:
            H[0], H[i] = H[i], H[0]
            for r in H:
                r[0], r[i] = r[i], r[0]
            if sgn(H[0][0]) > 0:
                npos += 1
            else:
                nneg += 1
            inv = const(H[0][0], 1) / H[0][0]
            H = [[H[a][b] - H[a][0] * inv * H[0][b] for b in range(1, m)] for a in range(1, m)]
            continue
        pair = next(((a, b) for a in range(m) for b in range(a + 1, m) if H[a][b] != 0), None)
        if pair is None:
            return (npos, nneg, m)
        a, b = pair
        H[0], H[a] = H[a], H[0]
        for r in H:
            r[0], r[a] = r[a], r[0]
        H[1], H[b] = H[b], H[1]
        for r in H:
            r[1], r[b] = r[b], r[1]
        npos += 1
        nneg += 1
        binv = inverse([[H[0][0], H[0][1]], [H[1][0], H[1][1]]])
        if m > 2:
            Cc = [row[:2] for row in H[2:]]
            Bb = [row[2:] for row in H[:2]]
            upd = mmul(mmul(Cc, binv), Bb)
            H = [[H[2 + p][2 + q] - upd[p][q] for q in range(m - 2)] for p in range(m - 2)]
        else:
            H = []
    return (npos, nneg, 0)


# ------------------------------------------------------------ inertia, way 2
def charpoly_fl(M):
    """Faddeev-LeVerrier: coefficients c[0..n], p(x) = sum c[j] x^j, c[n] = 1."""
    n = len(M)
    x = M[0][0]
    c = [const(x, 0)] * (n + 1)
    c[n] = const(x, 1)
    Mk = zeros(n, n, x)
    for k in range(1, n + 1):
        Mk = madd(mmul(M, Mk), mscale(c[n - k + 1], ident(n, x)))
        prod = mmul(M, Mk)
        t = const(x, 0)
        for i in range(n):
            t = t + prod[i][i]
        c[n - k] = -t / const(x, k)
    return [real_of(v) for v in c]


def _changes(seq):
    s = [v for v in seq if v != 0]
    return sum(1 for a, b in zip(s, s[1:]) if (a > 0) != (b > 0))


def inertia_descartes(M):
    """(n+, n-, n0) of a Hermitian matrix from its characteristic polynomial.
    Exact because all roots are real. Refuses when the counts do not add up."""
    if not is_square(M) or not is_hermitian(M):
        raise Refusal("not_hermitian")
    n = len(M)
    c = charpoly_fl(M)
    n0 = 0
    while n0 < n and c[n0] == 0:
        n0 += 1
    npos = _changes(c)
    nneg = _changes([c[j] * (1 if j % 2 == 0 else -1) for j in range(n + 1)])
    if npos + nneg + n0 != n:
        raise Refusal("descartes_inconsistent")
    return (npos, nneg, n0)


def inertia(M):
    a = inertia_congruence(M)
    b = inertia_descartes(M)
    if a != b:
        raise Refusal("inertia_checkers_disagree")
    return a


def iadd(a, b):
    return tuple(x + y for x, y in zip(a, b))


# ---------------------------------------------------------------- pinv exact
def rref(A):
    R = [list(r) for r in A]
    rows, cols = len(R), len(R[0])
    piv = []
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        p = next((t for t in range(r, rows) if R[t][c] != 0), None)
        if p is None:
            continue
        R[r], R[p] = R[p], R[r]
        inv = const(R[r][c], 1) / R[r][c]
        R[r] = [inv * v for v in R[r]]
        for t in range(rows):
            if t != r and R[t][c] != 0:
                f = R[t][c]
                R[t] = [a - f * b for a, b in zip(R[t], R[r])]
        piv.append(c)
        r += 1
    return R, piv


def pinv(A):
    m, n = len(A), len(A[0])
    R, piv = rref(A)
    r = len(piv)
    if r == 0:
        return zeros(n, m, A[0][0])
    F = [[A[i][c] for c in piv] for i in range(m)]
    G = R[:r]
    Gs, Fs = ctr(G), ctr(F)
    return mmul(mmul(mmul(Gs, inverse(mmul(G, Gs))), inverse(mmul(Fs, F))), Fs)


def penrose_ok(A, P):
    AP, PA = mmul(A, P), mmul(P, A)
    return mmul(AP, A) == A and mmul(PA, P) == P and ctr(AP) == AP and ctr(PA) == PA


# ------------------------------------------------------------------ results
def res(status, **kw):
    d = {"status": status}
    d.update(kw)
    return d


def p0(M, k):
    try:
        schur(M, k)
    except Refusal as e:
        return res("fail", why=e.code)
    return res("pass")


def p0g(M, k):
    A = blocks(M, k)[0]
    return res("pass") if penrose_ok(A, pinv(A)) else res("defect", why="penrose")


def check_haynsworth(M, k, S=None):
    if not is_hermitian(M):
        raise Refusal("not_hermitian")
    A = sub(M, 0, k, 0, k)
    if S is None:
        S = schur(M, k)
    return inertia(M) == iadd(inertia(A), inertia(S))


def p1(M, k):
    try:
        ok = check_haynsworth(M, k)
    except Refusal as e:
        return res("na", why=e.code)
    return res("pass" if ok else "defect")


def generalized_S(M, k):
    A, B, C, D = blocks(M, k)
    P = pinv(A)
    return msub(D, mmul(mmul(C, P), B)), mmul(mmul(A, P), B) == B


def p1g(M, k):
    if not is_hermitian(M):
        return res("na", why="not_hermitian")
    S, range_ok = generalized_S(M, k)
    A = sub(M, 0, k, 0, k)
    add_ok = inertia(M) == iadd(inertia(A), inertia(S))
    if range_ok and not add_ok:
        return res("defect", why="range_condition_holds_but_additivity_fails", range_condition=True)
    return res("pass" if add_ok else "fail", range_condition=range_ok)


def check_congruence(M, k, S=None):
    n = len(M)
    A, B, C, D = blocks(M, k)
    if not is_hermitian(M):
        raise Refusal("not_hermitian")
    Ai = inverse(A)
    if S is None:
        S = msub(D, mmul(mmul(C, Ai), B))
    x = M[0][0]
    V = ident(n, x)
    X = mscale(const(x, -1), mmul(Ai, B))
    for i in range(k):
        for j in range(n - k):
            V[i][k + j] = X[i][j]
    T = mmul(mmul(ctr(V), M), V)
    target = zeros(n, n, x)
    for i in range(k):
        for j in range(k):
            target[i][j] = A[i][j]
    for i in range(n - k):
        for j in range(n - k):
            target[k + i][k + j] = S[i][j]
    return T == target


def p2(M, k):
    try:
        ok = check_congruence(M, k)
    except Refusal as e:
        return res("na", why=e.code)
    return res("pass" if ok else "defect")


def lcm(a, b):
    return a * b // gcd(a, b)


def bareiss_minors(M):
    """Scale to Gaussian-integer entries by a positive integer, then run
    fraction-free Bareiss. Returns (minors, integral), or (None, integral)
    when a leading pivot is zero (the sign rule is then undefined)."""
    n = len(M)
    den = 1
    for row in M:
        for v in row:
            if isinstance(v, QI):
                den = lcm(lcm(den, v.re.denominator), v.im.denominator)
            else:
                den = lcm(den, v.denominator)
    N = [[v * den for v in row] for row in M]
    integral = True
    prev = const(N[0][0], 1)
    minors = []
    for kk in range(n):
        if N[kk][kk] == 0:
            return None, integral
        minors.append(real_of(N[kk][kk]))
        for i in range(kk + 1, n):
            for j in range(kk + 1, n):
                v = (N[i][j] * N[kk][kk] - N[i][kk] * N[kk][j]) / prev
                if isinstance(v, QI):
                    if v.re.denominator != 1 or v.im.denominator != 1:
                        integral = False
                elif v.denominator != 1:
                    integral = False
                N[i][j] = v
        prev = N[kk][kk]
    return minors, integral


def p3(M, k):
    if not is_hermitian(M):
        return res("na", why="not_hermitian")
    minors, integral = bareiss_minors(M)
    if minors is None:
        return res("na", why="zero_leading_minor")
    seq = [Fraction(1)] + minors
    neg = sum(1 for a, b in zip(seq, seq[1:]) if (a > 0) != (b > 0))
    ok = (len(M) - neg, neg, 0) == inertia(M) and integral
    return res("pass" if ok else "defect")


def rand_invertible(rng, n, x, lo=-2, hi=2):
    while True:
        C = [[const(x, rng.randint(lo, hi)) for _ in range(n)] for _ in range(n)]
        if det(C) != 0:
            return C


def blockdiag(P, Q):
    a, b = len(P), len(Q)
    Z = zeros(a + b, a + b, P[0][0])
    for i in range(a):
        for j in range(a):
            Z[i][j] = P[i][j]
    for i in range(b):
        for j in range(b):
            Z[a + i][a + j] = Q[i][j]
    return Z


def _hermitian_schur(M, k):
    """Return S, or a result dict to short-circuit."""
    if not is_hermitian(M):
        return None, res("na", why="not_hermitian")
    try:
        return schur(M, k), None
    except Refusal as e:
        return None, res("na", why=e.code)


def p4a(M, k, rng):
    S, early = _hermitian_schur(M, k)
    if early:
        return early
    c = const(M[0][0], 1) * Fraction(rng.randint(1, 9), rng.randint(1, 9))
    S2 = schur(mscale(c, M), k)
    return res("pass" if S2 == mscale(c, S) and inertia(S2) == inertia(S) else "defect")


def p4b(M, k, rng):
    S, early = _hermitian_schur(M, k)
    if early:
        return early
    n, x = len(M), M[0][0]
    Co, Ch = rand_invertible(rng, k, x), rand_invertible(rng, n - k, x)
    C = blockdiag(Co, Ch)
    S2 = schur(mmul(mmul(ctr(C), M), C), k)
    return res("pass" if S2 == mmul(mmul(ctr(Ch), S), Ch) and inertia(S2) == inertia(S) else "defect")


def p4c(M, k, rng):
    """Measured, not a theorem: a mixing congruence changes what the partition
    means. Reports preserved / changed / undefined."""
    S, early = _hermitian_schur(M, k)
    if early:
        return early
    C = rand_invertible(rng, len(M), M[0][0])
    try:
        S2 = schur(mmul(mmul(ctr(C), M), C), k)
    except Refusal:
        return res("undefined")
    return res("preserved" if inertia(S2) == inertia(S) else "changed")


def p5(M, k, S=None):
    A = sub(M, 0, k, 0, k)
    try:
        if S is None:
            S = schur(M, k)
    except Refusal as e:
        return res("na", why=e.code)
    return res("pass" if det(M) == det(A) * det(S) else "defect")


def p6(M, k, rng):
    if k < 2:
        return res("na", why="k_lt_2")
    k1 = rng.randint(1, k - 1)
    try:
        S1 = schur(M, k1)
        S12 = schur(S1, k - k1)
        S = schur(M, k)
    except Refusal as e:
        return res("na", why=e.code)
    return res("pass" if S12 == S else "defect")


def p8(M, k, rng):
    if not is_hermitian(M):
        return res("na", why="not_hermitian")
    n, x = len(M), M[0][0]
    iM, iA = inertia(M), inertia(sub(M, 0, k, 0, k))
    if iM[1] != 0 or iA != (k, 0, 0):
        return res("na", why="not_psd_with_pd_pivot")
    r = rng.randint(1, 2)
    U = [[const(x, rng.randint(-2, 2)) for _ in range(n)] for _ in range(r)]
    M2 = madd(M, mmul(ctr(U), U))
    gap = msub(schur(M2, k), schur(M, k))
    return res("pass" if inertia(gap)[1] == 0 else "defect")


PREDICATES = ("P0", "P0g", "P1", "P1g", "P2", "P3", "P4a", "P4b", "P4c", "P5", "P6", "P8")


def evaluate(sysd, seed_tag):
    M, k = sysd["M"], sysd["k"]
    rng = random.Random("%s|%s|checks" % (seed_tag, sysd["id"]))
    return {
        "P0": p0(M, k),
        "P0g": p0g(M, k),
        "P1": p1(M, k),
        "P1g": p1g(M, k),
        "P2": p2(M, k),
        "P3": p3(M, k),
        "P4a": p4a(M, k, rng),
        "P4b": p4b(M, k, rng),
        "P4c": p4c(M, k, rng),
        "P5": p5(M, k),
        "P6": p6(M, k, rng),
        "P8": p8(M, k, rng),
    }


# ----------------------------------------------------------------- controls
def tropical_has_additive_schur(Mt, k):
    """(min,+) semiring: oplus = min, otimes = +, zero element None (= +inf).
    An additive Schur complement D - C A^-1 B needs (a) a semiring inverse of A,
    which exists only for generalized permutation matrices, and (b) an additive
    inverse for the subtraction, which exists only for the zero element.
    Returns True only if both hold."""
    A = [row[:k] for row in Mt[:k]]
    for row in A:
        if sum(1 for v in row if v is not None) != 1:
            return False
    for c in range(k):
        if sum(1 for r in range(k) if A[r][c] is not None) != 1:
            return False
    B = [row[k:] for row in Mt[:k]]
    C = [row[:k] for row in Mt[k:]]
    if any(v is not None for row in B for v in row) and any(v is not None for row in C for v in row):
        return False
    return True


def controls():
    F = Fraction
    rows = []

    def add(name, accepted):
        rows.append({"name": name, "wrongly_accepted": bool(accepted)})

    try:
        schur([[F(0), F(1)], [F(1), F(2)]], 1)
        add("singular_1x1_pivot_refused", True)
    except Refusal:
        add("singular_1x1_pivot_refused", False)
    M = [[F(1), F(2), F(0)], [F(2), F(4), F(1)], [F(0), F(1), F(3)]]
    add("singular_2x2_pivot_p0", p0(M, 2)["status"] == "pass")
    add("singular_pivot_p2_not_pass", p2(M, 2)["status"] == "pass")
    T = [[1, 5, 2], [7, 3, 4], [None, 2, 9]]
    add("tropical_min_plus_no_additive_schur", tropical_has_additive_schur(T, 1))
    NS = [[F(2), F(1), F(0)], [F(5), F(3), F(1)], [F(0), F(1), F(1)]]
    try:
        check_haynsworth(NS, 1)
        add("nonsymmetric_refused_haynsworth", True)
    except Refusal:
        add("nonsymmetric_refused_haynsworth", False)
    CS = [[QI(1), QI(0, 1)], [QI(0, 1), QI(3)]]
    try:
        check_haynsworth(CS, 1)
        add("qi_symmetric_not_hermitian_refused", True)
    except Refusal:
        add("qi_symmetric_not_hermitian_refused", False)
    H = [[F(2), F(1)], [F(1), F(-3)]]
    S = schur(H, 1)
    add("corrupted_S_congruence", check_congruence(H, 1, S=[[S[0][0] + 1]]))
    add("corrupted_S_det", p5(H, 1, S=[[S[0][0] + 1]])["status"] == "pass")
    add("sign_flipped_S_inertia", check_haynsworth(H, 1, S=[[-S[0][0]]]))
    Z = [[F(0), F(1)], [F(1), F(0)]]
    add("pinv_without_range_condition_p1g", p1g(Z, 1)["status"] == "pass")
    add("bareiss_zero_leading_minor", p3(Z, 1)["status"] == "pass")
    Q3 = [[F(0), F(1), F(1)], [F(1), F(2), F(1)], [F(1), F(1), F(3)]]
    add("quotient_singular_A11", p6(Q3, 2, random.Random("ctl"))["status"] == "pass")
    M1 = [[F(1), F(0)], [F(0), F(1)]]
    M2 = [[F(1), F(0)], [F(0), F(2)]]
    add("loewner_wrong_direction", inertia(msub(schur(M1, 1), schur(M2, 1)))[1] == 0)
    add("inertia_checkers_vs_other_matrix", inertia_congruence(H) == inertia_descartes([[F(2), F(1)], [F(1), F(3)]]))
    return rows


# ------------------------------------------------------------------- panels
def pct(p, q):
    if q == 0:
        return "n/a"
    v = (10000 * p) // q
    return "%d.%02d" % (v // 100, v % 100)


def tally(items):
    c = {}
    for s in items:
        c[s] = c.get(s, 0) + 1
    return {k: c[k] for k in sorted(c)}


GOOD = ("pass", "preserved")


def summarize(results):
    out = {}
    for pr in PREDICATES:
        total = len(results)
        status = tally(r[pr]["status"] for _, r in results)
        n_pass = sum(status.get(g, 0) for g in GOOD)
        appl = total - status.get("na", 0) - status.get("undefined", 0)
        entry = {
            "total": total,
            "status_counts": status,
            "pass_over_all": "%d/%d" % (n_pass, total),
            "pass_rate_over_all_pct": pct(n_pass, total),
            "applicable": appl,
            "pass_over_applicable": "%d/%d" % (n_pass, appl),
            "pass_rate_over_applicable_pct": pct(n_pass, appl),
        }
        cells, bys = {}, {}
        for s, r in results:
            st = r[pr]["status"]
            cell = cells.setdefault("%s|%s" % (s["family"], s["mode"]), {"total": 0, "pass": 0, "applicable": 0})
            cell["total"] += 1
            cell["pass"] += st in GOOD
            cell["applicable"] += st not in ("na", "undefined")
            bn = bys.setdefault(str(s["n"]), {"total": 0, "pass": 0})
            bn["total"] += 1
            bn["pass"] += st in GOOD
        entry["by_family_mode"] = {k: cells[k] for k in sorted(cells)}
        entry["by_size_n"] = {k: bys[k] for k in sorted(bys, key=int)}
        entry["native_vs_scrambled_pass"] = {
            mode: "%d/%d" % (
                sum(1 for s, r in results if s["mode"] == mode and r[pr]["status"] in GOOD),
                sum(1 for s, r in results if s["mode"] == mode),
            )
            for mode in null_panel.MODES
        }
        out[pr] = entry
    return out


def run_panel(master):
    systems = null_panel.generate_panel(master, PER_CELL)
    results = [(s, evaluate(s, str(master))) for s in systems]
    defects = [
        {"id": s["id"], "predicate": pr, "why": r[pr].get("why", "")}
        for s, r in results
        for pr in PREDICATES
        if r[pr]["status"] == "defect"
    ]
    sizes = tally(s["n"] for s in systems)
    return {
        "master_seed": master,
        "per_cell": PER_CELL,
        "system_count": len(systems),
        "families": list(null_panel.FAMILIES),
        "size_histogram": {str(k): sizes[k] for k in sorted(sizes)},
        "panel_sha256": hashlib.sha256(
            "".join(null_panel.mat_hash(s["M"]) for s in systems).encode("ascii")
        ).hexdigest(),
        "predicates": summarize(results),
        "P1g_range_condition_counts": tally(
            str(r["P1g"].get("range_condition")) for _, r in results if r["P1g"]["status"] in ("pass", "fail")
        ),
        "identity_defects": defects,
    }


# ------------------------------------------------------- ledger instance table
# cls: QH Hermitian/quadratic elimination with a literal matrix Schur complement;
#      QN literal Schur complement of a non-Hermitian matrix; T tropical or
#      polyhedral elimination; N no built object visible in the ledger text read.
# evidence: F formula shown in the ledger text; L label names Schur/Haynsworth;
#      I label only implies a Gram, Laplacian or Bareiss structure; X nothing shown.
def inst(src, ident_, label, cls, ring, ev, note=""):
    return {"source": src, "id": ident_, "label": label, "cls": cls, "ring": ring,
            "evidence": ev, "note": note}


def ledger_instances():
    R, P, S = "README.md s1", "frontier_portals.md Portal 10", "SF-01"
    out = [
        inst(R, "R1", "Spectral Inertia R_opt", "QH", "Q(i) Hermitian, rational entries", "F"),
        inst(R, "R2", "Higher-moment Stieltjes-Hankel", "QH", "Q, Q(i) witnesses", "F"),
        inst(R, "R3", "Lattice elasticity sheaf Laplacian", "QH", "Q", "F"),
        inst(R, "R4", "Coarse-graining / Maslov", "T", "(min,+) semiring; Q[q]", "F",
             "Farkas peeling and Doob h-transform (a diagonal similarity); no D - C A^-1 B shown"),
        inst(R, "R5", "AeST Hamiltonian", "QH", "Q (rational functions of k)", "F",
             "Schur part only; Fenichel and Helmholtz parts are not Schur"),
        inst(R, "R6", "GKSL Lindblad Zeno", "QN", "Q(i) / symbolic", "F",
             "Lindbladian is non-Hermitian (EP2 Jordan blocks); Haynsworth cannot apply"),
        inst(R, "R7", "Sylvester-Hadamard F8 to E8", "QH", "Z[sqrt 2] / Q(sqrt 2)", "F",
             "2x2 block only; headline fold and kissing results are not Schur objects"),
        inst(R, "R8", "Kigami resistance renormalization", "QH", "Q", "F",
             "Kron reduction; full Laplacian singular, eliminated interior block invertible"),
        inst(P, "P1", "spectral R_opt", "QH", "Q(i)", "F"),
        inst(P, "P2", "Hankel hierarchy R_H4", "QH", "Q", "F"),
        inst(P, "P3", "F8 to E8 2x2 block M_{+-2}(s)", "QH", "Z[sqrt 2]", "F"),
        inst(P, "P4", "Elastic tensor C", "QH", "Q", "F"),
        inst(P, "P5", "Tropical (min,+) Schur/Doob peeling", "T", "(min,+) semiring", "F",
             "update is c(j) = c(j-1) + d0(pi* h*): add a coboundary, no block inverse"),
        inst(P, "P6", "AeST Hamiltonian S_P", "QH", "Q (rational functions)", "F"),
        inst(P, "P7", "Lindblad Zeno Schur", "QN", "Q(i) / symbolic", "F", "non-Hermitian"),
        inst(P, "P8", "Kigami Schur L_{n+1}/L_int", "QH", "Q", "F",
             "status in that table: routed to a probe, not marked verified"),
    ]
    sf = [
        ("gravity AeST dark-matter closure", "QH", "Q", "F"),
        ("incentre-lattices elastic rigidity unjamming", "QH", "Q", "F"),
        ("fractals GKSL Lindblad Zeno", "QN", "Q(i) / symbolic", "F"),
        ("warp#17 stacked LoRA Q_stack(s)", "QH", "Q", "I"),
        ("heedle blind-subspace drift Shed/hidden_move", "N", "unknown", "X"),
        ("soko grounded-Laplacian R_eff", "QH", "Q", "I"),
        ("jacobian-lens verbalizable Jacobian vs dark kernel (fp16)", "N", "dyadic Q (fp16 data)", "X"),
        ("FlashProve Schatten-nuclear vs Bareiss PSD", "QH", "Z/Q", "I"),
        ("formal-conjectures Hadamard.lean Bareiss Schur converse", "QH", "Z", "L"),
        ("DisTrO H_8 Schur ceiling", "QH", "Q", "L"),
        ("RPC-Bench parallel-sum / 2x2 Plucker Schur commutator", "QH", "Q", "L"),
        ("gravity Arm H1 Haynsworth-Schur Krein", "QH", "Q", "L"),
        ("incentre-lattices Arm H2 p-adic BTZ DtN iterated Schur", "QH", "Q", "L"),
        ("hawking Arm R4-4 indefinite DtN Krein flip", "QH", "Q", "I"),
        ("formal-conjectures Arm R4-2 Hankel/Stieltjes Schur", "QH", "Z/Q", "L"),
        ("openai/math Ramanujan-sum Schur projection", "QH", "Z", "L"),
        ("zeta-explorer Weil/Li/NB Gram/Schur PSD", "QH", "Q", "L"),
        ("canculus 2x2 feedback Schur S = 1 + alpha g h", "QH", "Q", "L"),
        ("Euler Leray projection as rank-1 Schur", "QH", "Q", "L"),
        ("navier-stokes SignedTree multifrontal Schur", "QH", "Q", "L"),
        ("continuum double-slit GKSL Schur pinching", "QN", "Q(i)", "L"),
        ("aletheia 8-glyph operator calculus Loewner screening", "QH", "Q", "I"),
        ("camail linear-attention/SSM Schur pushforward", "QH", "Q", "L"),
        ("alphaxiv Hilbert-operator Bareiss Schur conditioning", "QH", "Q", "L"),
        ("quantum#1 U(1) severing / Looped-Schur", "QH", "Q(i)", "L"),
        ("warp-drive Bareiss Gram Schur Q_stack", "QH", "Q", "L"),
        ("zenodo rns-pnp coupling Gramian W = B^T B", "QH", "Z/Q", "I"),
    ]
    for i, (lab, cls, ring, ev) in enumerate(sf, 1):
        out.append(inst(S, "SF-01#%d" % i, lab, cls, ring, ev,
                        "label-only classification" if ev in ("I", "X") else ""))
    return out


def possible(cls, ring):
    """Which predicates the mechanism class could satisfy in principle."""
    if cls == "QH":
        d = {"P0": "yes", "P0g": "yes", "P1": "yes", "P1g": "yes_if_range_condition",
             "P2": "yes", "P3": "yes", "P4a": "yes", "P4b": "yes", "P5": "yes",
             "P6": "yes", "P8": "yes_if_psd"}
        if "sqrt" in ring:
            d["P3"] = "needs_ordered_field_signs_outside_panel"
        return d
    if cls == "QN":
        na = "inapplicable_not_hermitian"
        return {"P0": "yes", "P0g": "yes", "P1": na, "P1g": na, "P2": na, "P3": na,
                "P4a": na, "P4b": na, "P5": "yes", "P6": "yes", "P8": na}
    if cls == "T":
        return {p: "no_additive_inverse_in_semiring" for p in PREDICATES if p not in ("P4c",)}
    return {p: "unknown_no_object_visible" for p in PREDICATES if p not in ("P4c",)}


def instance_table():
    rows = []
    for r in ledger_instances():
        d = dict(r)
        d["could_satisfy_in_principle"] = possible(r["cls"], r["ring"])
        rows.append(d)
    counts = {}
    for r in rows:
        key = "%s|%s" % (r["source"], r["cls"])
        counts[key] = counts.get(key, 0) + 1
    return rows, {k: counts[k] for k in sorted(counts)}


def main():
    ctl = controls()
    ctl_bad = [c["name"] for c in ctl if c["wrongly_accepted"]]
    rows, counts = instance_table()
    panels = [run_panel(m) for m in PANEL_SEEDS]
    defects = sum(len(p["identity_defects"]) for p in panels)
    out = {
        "schema": "gate5.predicate_panel.v1",
        "controls": ctl,
        "controls_that_wrongly_passed": ctl_bad,
        "panels": panels,
        "identity_defect_total": defects,
        "instance_class_counts": counts,
        "instances": rows,
    }
    sys.stdout.write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    if ctl_bad:
        return 1
    if defects:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
