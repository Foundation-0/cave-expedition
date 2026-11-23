r"""Second independent re-check of AUDIT-009 and AUDIT-017 (the advocate pass).

Backs these statements in VERDICTS.md: the F_n to D_n fold for n = 3 to 12 (bars, det L(1) =
4n, distinct cosets, kissing number 2n(n-1) for n = 3 to 8, Lemma 4/5 inequalities and
Bernstein signs on 245,122 box pairs and about 6,000 random pairs); the Type-I census of
4x4 matrices (2016 with det 16, 864 genuine D_4 endpoints, 48 nilpotent, 96 with I+S PSD),
which resolves the 864 against 2016 discrepancy; the E_8 endpoint (even unimodular, shells
240 and 2160 of Lambda found by filtering the E_8 shells, 16 distinct cosets) with a numeric
sweep at 41 values of s; and the Cartan determinants behind Theorem 2 (E_6 = 3, E_7 = 2).
Own code, written from the statements in the proofs. Shares no code with the verifiers
under test or with check_dn.py and check_e8.py.

Needs: Python 3, SymPy, numpy (numeric sweep only). No clone and no network. Fixed seed
20261120 (printed). Floats in the numeric sweep are rounded to 9 places so that output does
not depend on the platform.
Run:   python3 -I -B recheck_folds.py
Time:  about 3 minutes.
Result: one line starting RESULT, exit code 0 only if every check held.
"""
import itertools
import math
import random
import sys
from fractions import Fraction as Fr

import sympy as sp

FAIL = []


def check(cond, label):
    if not cond:
        FAIL.append(label)
    return cond


# ---------------------------------------------------------------- Z[sqrt2] helpers
class Q2:
    """a + b*sqrt2 with Fraction a, b."""
    __slots__ = ("a", "b")

    def __init__(self, a, b=0):
        self.a = Fr(a)
        self.b = Fr(b)

    def __add__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __sub__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(self.a - o.a, self.b - o.b)

    def __mul__(self, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(self.a * o.a + 2 * self.b * o.b, self.a * o.b + self.b * o.a)

    __rmul__ = __mul__

    def sign(self):
        a, b = self.a, self.b
        if a >= 0 and b >= 0:
            return 0 if (a == 0 and b == 0) else 1
        if a <= 0 and b <= 0:
            return -1
        # opposite signs: compare a^2 with 2 b^2
        if a > 0:
            return 1 if a * a > 2 * b * b else (0 if a * a == 2 * b * b else -1)
        return 1 if 2 * b * b > a * a else (0 if a * a == 2 * b * b else -1)


def bern_from_power(c):
    """power coefficients c0..cN -> Bernstein coefficients on [0,1] (same degree)."""
    N = len(c) - 1
    out = []
    for k in range(N + 1):
        acc = Q2(0)
        for j in range(k + 1):
            acc = acc + c[j] * Fr(math.comb(k, j), math.comb(N, j))
        out.append(acc)
    return out


# ---------------------------------------------------------------- Part A: D_n family
def Cn(n):
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


def motif(n):
    P = []
    for i in range(n):
        for sgn in (1, -1):
            v = [0] * n
            v[i] = sgn
            P.append(tuple(v))
    return P


def endpoint_checks(n, C):
    """L(1) = 2I + C. Returns (det, cosets_distinct, motif_in_odd_Dn, rows_even)."""
    L1 = sp.Matrix(n, n, lambda i, j: (2 if i == j else 0) + C[i][j])
    det = L1.det()
    inv = L1.inv()
    P = motif(n)
    distinct = True
    for p, q in itertools.combinations(P, 2):
        d = sp.Matrix([[p[k] - q[k] for k in range(n)]]) * inv
        if all(x.is_integer for x in d):
            distinct = False
            break
    rows_even = all(sum(L1[i, j] for j in range(n)) % 2 == 0 for i in range(n))
    return int(det), distinct, rows_even, L1


def min_norm_and_kissing(L1, n, radius_box=2):
    """Min squared distance and contacts at ball +e0 in P + Z^n L1, by enumeration of
    D_n vectors of norm 2 (the endpoint is D_n + e0, contacts are norm-2 differences)."""
    P = motif(n)
    Pset = set(P)
    inv = L1.inv()
    # A point x of D_n+e0 is in the packing iff x - p in lattice for some p in P.
    contacts = 0
    base = P[0]
    for i, j in itertools.combinations(range(n), 2):
        for si in (1, -1):
            for sj in (1, -1):
                w = [0] * n
                w[i] = si
                w[j] = sj
                x = tuple(base[k] + w[k] for k in range(n))
                inpack = False
                for p in P:
                    d = sp.Matrix([[x[k] - p[k] for k in range(n)]]) * inv
                    if all(z.is_integer for z in d):
                        inpack = True
                        break
                contacts += 1 if inpack else 0
    return contacts


def lemma4_quantities(n, C, m, v):
    """Q_n(m)=m(2I+S)m, w1 = m(2I+C)+v, D = w1.m, E=(2m+v).w1, M=|m|^2, W1=|w1|^2."""
    w1 = [2 * m[j] + sum(m[i] * C[i][j] for i in range(n)) + v[j] for j in range(n)]
    D = sum(w1[j] * m[j] for j in range(n))
    E = sum((2 * m[j] + v[j]) * w1[j] for j in range(n))
    M = sum(x * x for x in m)
    W1 = sum(x * x for x in w1)
    Q = sum(m[i] * ((2 if i == j else 0) * m[j]) for i in range(n) for j in range(n)) + sum(
        m[i] * C[i][j] * m[j] for i in range(n) for j in range(n))
    return Q, D, E, M, W1


def quartic_bernstein(n, C, m, v):
    """f(s)=(1+s^2)^2(|mL(s)+v|^2-2), L = dI+tC, t=2s/(1+s^2), a=sqrt2(1-s^2)/(1+s^2).
    (1+s^2)(mL+v) = A0 + A1 s + A2 s^2 with
    A0=(2+sqrt2)m+v, A1=2 mC, A2=(2-sqrt2)m+v."""
    mC = [sum(m[i] * C[i][j] for i in range(n)) for j in range(n)]
    A0 = [Q2(2 * m[j] + v[j], m[j]) for j in range(n)]
    A1 = [Q2(2 * mC[j]) for j in range(n)]
    A2 = [Q2(2 * m[j] + v[j], -m[j]) for j in range(n)]

    def dot(X, Y):
        acc = Q2(0)
        for x, y in zip(X, Y):
            acc = acc + x * y
        return acc
    c0 = dot(A0, A0) - 2
    c1 = 2 * dot(A0, A1)
    c2 = dot(A1, A1) + 2 * dot(A0, A2) - 4
    c3 = 2 * dot(A1, A2)
    c4 = dot(A2, A2) - 2
    return bern_from_power([c0, c1, c2, c3, c4])


def part_A(rng):
    out = {}
    s = sp.symbols("s", real=True)
    r2 = sp.sqrt(2)
    t = 2 * s / (1 + s ** 2)
    a = r2 * (1 - s ** 2) / (1 + s ** 2)
    d = 2 + a
    for n in range(3, 13):
        C = Cn(n)
        # bar identity |a e_i + t C_i|^2 == 2, symbolic
        bar_ok = all(sp.simplify(a ** 2 + t ** 2 * sum(C[i][j] ** 2 for j in range(n)) - 2) == 0
                     for i in range(n))
        diag_zero = all(C[i][i] == 0 for i in range(n))
        det, distinct, rows_even, L1 = endpoint_checks(n, C)
        kiss = min_norm_and_kissing(L1, n) if n <= 8 else None
        check(bar_ok and diag_zero, f"Dn bar n={n}")
        check(det == 4 * n, f"Dn det n={n}")
        check(distinct and rows_even, f"Dn cosets n={n}")
        if kiss is not None:
            check(kiss == 2 * n * (n - 1), f"Dn kissing n={n}")
        # closed-form determinant D_n(d,t) = d p_{n-1} + 2 t^2 p_{n-2} + 2 t^n
        dd, tt = sp.symbols("d t")
        Mx = sp.Matrix(n, n, lambda i, j: (dd if i == j else 0) + tt * C[i][j])
        p = [sp.Integer(1), dd]
        for k in range(2, n):
            p.append(sp.expand(dd * p[-1] - tt ** 2 * p[-2]))
        cf = sp.expand(dd * p[n - 1] + 2 * tt ** 2 * p[n - 2] + 2 * tt ** n)
        det_ok = sp.expand(Mx.det() - cf) == 0 if n <= 9 else None
        if det_ok is not None:
            check(det_ok, f"Dn closed det n={n}")
        out[n] = dict(bar=bar_ok, det1=det, cosets=distinct, kissing=kiss, closed_det=det_ok)
    # Lemma 4 / Lemma 5 inequalities: exhaustive small boxes + random large
    P_diff = {}
    viol = 0
    pairs = 0
    neg_b = 0
    for n in (3, 4, 5):
        C = Cn(n)
        P = motif(n)
        V = sorted({tuple(p[k] - q[k] for k in range(n)) for p in P for q in P})
        R = 3 if n <= 4 else 2
        for m in itertools.product(range(-R, R + 1), repeat=n):
            for v in V:
                if not any(m) and not any(v):
                    continue
                pairs += 1
                Q, D, E, M, W1 = lemma4_quantities(n, C, m, v)
                inf = max(abs(x) for x in m)
                if Q < 2 * inf or D < 0 or E < -2 or (M == 1 and E < 0) or W1 < 2:
                    viol += 1
                b = quartic_bernstein(n, C, m, v)
                if any(x.sign() < 0 for x in b):
                    neg_b += 1
    rand_pairs = 0
    for _ in range(6000):
        n = rng.randint(3, 30)
        C = Cn(n)
        m = [rng.randint(-40, 40) if rng.random() < 0.3 else rng.randint(-2, 2) for _ in range(n)]
        i, j = rng.sample(range(n), 2)
        v = [0] * n
        if rng.random() < 0.4:
            v[i] = rng.choice((2, -2))
        else:
            v[i] = rng.choice((1, -1))
            v[j] = rng.choice((1, -1))
        if not any(m):
            continue
        rand_pairs += 1
        Q, D, E, M, W1 = lemma4_quantities(n, C, m, v)
        inf = max(abs(x) for x in m)
        if Q < 2 * inf or D < 0 or E < -2 or (M == 1 and E < 0) or W1 < 2:
            viol += 1
        b = quartic_bernstein(n, C, m, v)
        if any(x.sign() < 0 for x in b):
            neg_b += 1
    check(viol == 0 and neg_b == 0, "Dn lemma4/5")
    out["lemma45"] = dict(box_pairs=pairs, random_pairs=rand_pairs, violations=viol, negative_bernstein=neg_b)
    return out


# ---------------------------------------------------------------- Part B: nilpotent C4 and census
C4N = [[0, -1, -1, 0], [-1, 0, 0, -1], [1, 0, 0, 1], [0, 1, 1, 0]]


def part_B():
    out = {}
    C = sp.Matrix(C4N)
    out["C2_zero"] = (C * C == sp.zeros(4, 4))
    dd, tt = sp.symbols("d t")
    out["det_d4"] = sp.expand((dd * sp.eye(4) + tt * C).det() - dd ** 4) == 0
    det, distinct, rows_even, L1 = endpoint_checks(4, C4N)
    out["endpoint"] = dict(det=det, cosets_distinct=distinct, rows_even=rows_even,
                           kissing=min_norm_and_kissing(L1, 4))
    check(out["C2_zero"] and out["det_d4"] and det == 16 and distinct, "C4nilp endpoint")
    # Does the analytic Lemma-4/5 route (D>=0, E+2M-2>=0, W1>=2) hold for C4nilp on a box?
    P = motif(4)
    V = sorted({tuple(p[k] - q[k] for k in range(4)) for p in P for q in P})
    bad_D = bad_E = bad_W = 0
    neg = 0
    tot = 0
    first_bad = None
    for m in itertools.product(range(-4, 5), repeat=4):
        for v in V:
            if not any(m) and not any(v):
                continue
            tot += 1
            Q, D, E, M, W1 = lemma4_quantities(4, C4N, m, v)
            if D < 0:
                bad_D += 1
                first_bad = first_bad or ("D", m, v, D)
            if M >= 1 and E + 2 * M - 2 < 0:
                bad_E += 1
                first_bad = first_bad or ("E", m, v, E)
            if W1 < 2:
                bad_W += 1
            b = quartic_bernstein(4, C4N, m, v)
            if any(x.sign() < 0 for x in b):
                neg += 1
    out["lemma_route_box4"] = dict(pairs=tot, D_neg=bad_D, E_plus_2M_minus_2_neg=bad_E,
                                   W1_lt_2=bad_W, negative_bernstein=neg, first_bad=str(first_bad))
    check(neg == 0, "C4nilp bernstein box")
    # 4D Type-I census: C_ii = 0, each row has two entries +-1 off the diagonal
    rows = []
    for i in range(4):
        opts = []
        off = [j for j in range(4) if j != i]
        for pair in itertools.combinations(off, 2):
            for s1 in (1, -1):
                for s2 in (1, -1):
                    r = [0] * 4
                    r[pair[0]] = s1
                    r[pair[1]] = s2
                    opts.append(r)
        rows.append(opts)
    total = det16 = valid = nilp = psd = 0
    for combo in itertools.product(*rows):
        total += 1
        Cm = sp.Matrix(combo)
        L1 = 2 * sp.eye(4) + Cm
        if L1.det() != 16:
            continue
        det16 += 1
        inv = L1.inv()
        ok = True
        for p, q in itertools.combinations(motif(4), 2):
            dv = sp.Matrix([[p[k] - q[k] for k in range(4)]]) * inv
            if all(x.is_integer for x in dv):
                ok = False
                break
        if not ok:
            continue
        valid += 1
        if Cm * Cm == sp.zeros(4, 4):
            nilp += 1
        S = (Cm + Cm.T) / 2
        IS = sp.eye(4) + S
        # exact PSD test: every principal minor >= 0
        if all(IS.extract(list(idx), list(idx)).det() >= 0
               for r in range(1, 5) for idx in itertools.combinations(range(4), r)):
            psd += 1
    out["census"] = dict(total=total, det16=det16, valid_D4_endpoint=valid, nilpotent_valid=nilp,
                         I_plus_S_psd_valid=psd)
    return out


# ---------------------------------------------------------------- Part C: E8 fold
def popc(x):
    return bin(x).count("1")


def H8():
    return [[(-1) ** popc(i & j) for j in range(8)] for i in range(8)]


def part_C():
    out = {}
    H = H8()
    r2 = sp.sqrt(2)
    s = sp.symbols("s", real=True)
    Dp = (1 + 2 * r2) + (-1 + 2 * r2) * s ** 2
    Dm = (-1 + 2 * r2) + (1 + 2 * r2) * s ** 2
    ap = ((6 + 5 * r2) + (-6 + 5 * r2) * s ** 2) / Dp
    bp = 2 * r2 * s / Dp
    am = ((2 + 3 * r2) + (-2 + 3 * r2) * s ** 2) / Dm
    bm = 2 * r2 * s / Dm
    Ip = {i for i in range(8) if H[i][i] == 1}

    def Ls(sv):
        M = sp.zeros(8, 8)
        for i in range(8):
            A, B = (ap, bp) if i in Ip else (am, bm)
            for j in range(8):
                M[i, j] = (A if i == j else B * H[i][j])
        return M.subs(s, sv) if sv is not None else M

    Lsym = Ls(None)
    bars = [sp.simplify(sum((Lsym[i, j] - (2 if i == j else 0)) ** 2 for j in range(8)) - 2) for i in range(8)]
    out["bars_identically_2"] = all(b == 0 for b in bars)
    L0 = Ls(0).applyfunc(sp.nsimplify)
    L1 = Ls(1).applyfunc(sp.simplify)
    out["L0_is_(2+r2)I"] = all(sp.simplify(L0[i, j] - ((2 + r2) if i == j else 0)) == 0 for i in range(8) for j in range(8))
    Hm = sp.Matrix(H)
    out["L1_is_2I+H/2"] = sp.simplify(L1 - (2 * sp.eye(8) + Hm / 2)) == sp.zeros(8, 8)
    G1 = (2 * sp.eye(8) + Hm / 2) * (2 * sp.eye(8) + Hm / 2).T
    half = G1 / 2
    out["G1_is_6I+2H"] = G1 == 6 * sp.eye(8) + 2 * Hm
    out["G1/2_integral_even_unimodular"] = (all(x.is_integer for x in half) and all(half[i, i] % 2 == 0 for i in range(8))
                                         and half.det() == 1)
    check(out["bars_identically_2"] and out["L0_is_(2+r2)I"] and out["L1_is_2I+H/2"]
          and out["G1/2_integral_even_unimodular"], "E8 basic")
    # Endpoint cosets: p - e0 in E8, and (p-q) L1^{-1} non-integral for p != q
    L1r = 2 * sp.eye(8) + Hm / 2
    inv = L1r.inv()
    P = motif(8)
    distinct = all(not all(x.is_integer for x in (sp.Matrix([[p[k] - q[k] for k in range(8)]]) * inv))
                   for p, q in itertools.combinations(P, 2))
    out["motif_16_distinct_cosets"] = distinct
    check(distinct, "E8 cosets")
    # Enumerate E8 vectors of norm 4 and 8 (E8 normalised to min norm 2), keep those in
    # Lambda = Z^8 L1; these are exactly the m with m G1 m in {4,8}.
    Linv = [[float(inv[i, j]) for j in range(8)] for i in range(8)]
    Hf = [[float(x) for x in r] for r in H]
    shell = {4: [], 8: []}
    for x in itertools.product(range(-2, 3), repeat=8):
        nn = sum(c * c for c in x)
        if nn in (4, 8) and sum(x) % 2 == 0:
            shell[nn].append(tuple(Fr(c) for c in x))
    # half-integer coset: y = 2x all odd, |x|^2 = |y|^2/4, sum(x) even <=> sum(y) = 0 mod 4
    for y in itertools.product((-5, -3, -1, 1, 3, 5), repeat=8):
        ny = sum(c * c for c in y)
        if ny in (16, 32) and sum(y) % 4 == 0:
            shell[ny // 4].append(tuple(Fr(c, 2) for c in y))
    e8_counts = {k: len(v) for k, v in shell.items()}
    invF = [[Fr(int(sp.numer(inv[i, j])), int(sp.denom(inv[i, j]))) for j in range(8)] for i in range(8)]
    ms = {4: [], 8: []}
    for nn, vecs in shell.items():
        for x in vecs:
            m = [sum(x[i] * invF[i][j] for i in range(8)) for j in range(8)]
            if all(c.denominator == 1 for c in m):
                ms[nn].append(tuple(int(c) for c in m))
    out["E8_shell_counts_norm4_norm8"] = e8_counts
    out["Lambda_vectors_mG1m_4_8"] = {k: len(v) for k, v in ms.items()}
    check(e8_counts == {4: 2160, 8: 17520} and len(ms[4]) == 240 and len(ms[8]) == 2160, "E8 shells")
    # Numeric sweep: Loewner G(s)-G(1) >= 0 and min distance over m with mG1m<=8 (others are
    # covered by the triangle inequality once G(s) >= G(1)), at 41 s values.
    import numpy as np  # noqa: E402  (numeric sweep only; exact facts are above)
    G1f = np.array([[float(x) for x in row] for row in G1.tolist()])
    V = sorted({tuple(p[k] - q[k] for k in range(8)) for p in P for q in P})
    Vn = np.array(V, dtype=float)
    allm = np.array(ms[4] + ms[8], dtype=float)
    min_eig = 1e9
    min_gap_interior = 1e9
    min_gap_all = 1e9
    for k in range(41):
        sv = k / 40
        Lnum = np.array(Lsym.subs(s, sp.Rational(k, 40)).evalf(30).tolist(), dtype=float)
        G = Lnum @ Lnum.T
        min_eig = min(min_eig, float(np.linalg.eigvalsh(G - G1f).min()))
        W = allm @ Lnum  # (N,8)
        d2 = ((W[:, None, :] + Vn[None, :, :]) ** 2).sum(axis=2) - 2.0
        # exclude persistent bars m = e_i? those have mG1m = 4 or 8? m=e_i gives row i of L1
        # ; bars are exactly zero, so report min over all and min over entries > 1e-9 separately
        min_gap_all = min(min_gap_all, float(d2.min()))
        if 0 < k < 40:
            nz = d2[np.abs(d2) > 1e-9]
            min_gap_interior = min(min_gap_interior, float(nz.min()))
    out["numeric_min_eig_G(s)-G(1)"] = round(min_eig, 9) + 0.0
    out["numeric_min_(dist2-2)_all"] = round(min_gap_all, 9) + 0.0
    out["numeric_min_nonzero_(dist2-2)_interior"] = round(min_gap_interior, 9) + 0.0
    check(min_eig > -1e-9 and min_gap_all > -1e-9, "E8 numeric sweep")
    # Must-fail control: the same Loewner test just above the endpoint, at s = 11/10, must go negative.
    L_above = np.array(Lsym.subs(s, sp.Rational(11, 10)).evalf(30).tolist(), dtype=float)
    eig_above = float(np.linalg.eigvalsh(L_above @ L_above.T - G1f).min())
    out["control_numeric_min_eig_G(11/10)-G(1)"] = round(eig_above, 6) + 0.0
    check(eig_above < -1e-6, "control: Loewner test at s = 11/10 must fail")
    return out


# ---------------------------------------------------------------- Part D: Theorem 2 facts
def cartan(typ, n):
    A = sp.zeros(n, n)
    for i in range(n):
        A[i, i] = 2
    if typ == "D":
        for i in range(n - 2):
            A[i, i + 1] = A[i + 1, i] = -1
        A[n - 3, n - 1] = A[n - 1, n - 3] = -1
    else:  # E_n, Bourbaki: chain 1-3-4-5-...; node 2 attached to 4
        edges = [(0, 2), (1, 3), (2, 3)] + [(k, k + 1) for k in range(3, n - 1)]
        for i, j in edges:
            A[i, j] = A[j, i] = -1
    return A


def part_D():
    out = {}
    dets = {"E6": cartan("E", 6).det(), "E7": cartan("E", 7).det(), "E8": cartan("E", 8).det()}
    dets.update({f"D{n}": cartan("D", n).det() for n in range(4, 9)})
    out["gram_dets"] = {k: int(v) for k, v in dets.items()}
    out["4/3_square"] = sp.Rational(4, 3).is_integer
    out["4/2_square"] = math.isqrt(2) ** 2 == 2
    # D_n^+ half coset minimal norm n/4 (all coordinates +-1/2)
    out["Dn_plus_half_coset_min_norm"] = {n: str(Fr(n, 4)) for n in (4, 6, 8, 10, 12)}
    check(out["gram_dets"]["E6"] == 3 and out["gram_dets"]["E7"] == 2 and out["gram_dets"]["E8"] == 1
          and all(out["gram_dets"][f"D{n}"] == 4 for n in range(4, 9)), "cartan dets")
    return out


# ---------------------------------------------------------------- Part E: must-fail controls
def part_E():
    """Perturbed inputs that the exact checks above must refuse. A control that does not fail is a failure."""
    out = {}
    # (1) Hadamard with one sign flipped: G(1)/2 must stop being even, integral and unimodular.
    Hb = H8()
    Hb[1][2] = -Hb[1][2]
    Hbm = sp.Matrix(Hb)
    L1b = 2 * sp.eye(8) + Hbm / 2
    half = (L1b * L1b.T) / 2
    good = (all(x.is_integer for x in half) and all(half[i, i] % 2 == 0 for i in range(8)) and half.det() == 1)
    out["flipped_hadamard_gram_even_unimodular"] = bool(good)
    check(not good, "control: flipped-sign Hadamard must not give an even unimodular Gram matrix")
    # (2) C_4 with one sign flipped: det L(1) must not be 4n = 16, and the Bernstein scan must go negative.
    Cb = Cn(4)
    Cb[0][1] = 1
    det_b, _, _, _ = endpoint_checks(4, Cb)
    out["flipped_C4_det_L1"] = det_b
    check(det_b != 16, "control: flipped-sign C4 must not give det 16")
    P = motif(4)
    V = sorted({tuple(p[k] - q[k] for k in range(4)) for p in P for q in P})
    neg = 0
    for m in itertools.product(range(-2, 3), repeat=4):
        for v in V:
            if (any(m) or any(v)) and any(x.sign() < 0 for x in quartic_bernstein(4, Cb, m, v)):
                neg += 1
    out["flipped_C4_pairs_with_negative_bernstein"] = neg
    check(neg > 0, "control: flipped-sign C4 must show a negative Bernstein coefficient")
    return out


def main():
    seed = 20261120
    print("seed", seed)
    rng = random.Random(seed)
    res = {"A_Dn": part_A(rng), "B_C4nilp_census": part_B(), "C_E8": part_C(), "D_thm2": part_D(), "E_controls": part_E()}
    for k, v in res.items():
        print(f"== {k}")
        if isinstance(v, dict):
            for kk, vv in v.items():
                print(f"  {kk}: {vv}")
    print("FAILURES:", FAIL)
    print("RESULT recheck_folds: %s (%d failed checks)" % ("PASS" if not FAIL else "FAIL", len(FAIL)))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
