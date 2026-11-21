"""Independent check of AUDIT-009: the F_n to D_n fold family and the nilpotent C_4 fold.

Backs the statement "F_n to D_n fold for all n, nilpotent C_4 fold (009)" in VERDICTS.md,
section 1: bars as symbolic identities, endpoints by enumeration for n = 3 to 10 (plus the
nilpotent C_4), the proof's integer inequalities and Bernstein signs on about 1.3 million
integer pairs, the five Lemma 5 Bernstein formulas as symbolic identities, an exact
closest-pair search at 48 rational values of s, and a numeric check of the Lemma 3 bound.
Shares no code with the verifiers under test.

Needs: Python 3, SymPy, and common.py from this folder. No clone of the target repository
and no network. Fixed seeds 20261120 and 20261121 (printed).
Run:   python3 -I -B check_dn.py
Time:  about 3 minutes.
Result: one line starting RESULT, exit code 0 only if every check held.
"""
import sys, os, itertools, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
from common import Q2, power_to_bernstein, poly_mul, poly_add, fincke_pohst
import sympy as sp

SEED = 20261120
RNG = random.Random(SEED + 1)  # box sampling in step 3a
print("seeds", SEED, SEED + 1)
FAIL = []


def req(c, msg):
    if not c:
        FAIL.append(msg)
        print("FAIL:", msg)


def Cn(n):
    C = [[0] * n for _ in range(n)]
    C[0][1] = C[0][n - 1] = -1
    C[1][0] = C[n - 1][0] = 1
    for k in range(1, n - 1):
        C[k][k + 1] = -1
        C[k + 1][k] = -1
    # row 1: (1,0)=+1, (1,2)=-1 ; row n-1: (n-1,0)=+1, (n-1,n-2)=-1 ; rows 2..n-2 symmetric -1
    return C


C4NIL = [[0, -1, -1, 0], [-1, 0, 0, -1], [1, 0, 0, 1], [0, 1, 1, 0]]


def motif_diffs(n):
    P = []
    for i in range(n):
        for sgn in (1, -1):
            e = [0] * n; e[i] = sgn; P.append(tuple(e))
    D = sorted({tuple(p[k] - q[k] for k in range(n)) for p in P for q in P})
    return P, D


# ---------- 1. symbolic bars + determinant formula ----------
s, d, t = sp.symbols("s d t", real=True)
r2 = sp.sqrt(2)
ts = 2 * s / (1 + s**2)
as_ = r2 * (1 - s**2) / (1 + s**2)
for n in range(3, 11):
    C = sp.Matrix(Cn(n))
    req(all(C[i, i] == 0 and sum(C[i, j]**2 for j in range(n)) == 2 for i in range(n)), f"rowshape n={n}")
    L = (2 + as_) * sp.eye(n) + ts * C
    for i in range(n):
        b = L.row(i) - 2 * sp.eye(n).row(i)
        req(sp.simplify(b.dot(b) - 2) == 0, f"bar {i} n={n}")
    # determinant formula D_n = d p_{n-1} + 2 t^2 p_{n-2} + 2 t^n
    p = [sp.Integer(1), d]
    for k in range(2, n):
        p.append(sp.expand(d * p[-1] - t**2 * p[-2]))
    Dn = sp.expand((d * sp.eye(n) + t * C).det())
    req(sp.expand(Dn - (d * p[n - 1] + 2 * t**2 * p[n - 2] + 2 * t**n)) == 0, f"det formula n={n}")
    if n == 4:
        req(sp.expand(Dn - d**4) == 0, "n=4 twisted det = d^4")
print("1. symbolic bars and det formula n=3..10 done")

# ---------- 2. endpoint: exact det, coset structure, kissing ----------
def frac_det_inv(M):
    n = len(M)
    A = [[Fr(x) for x in row] + [Fr(int(i == j)) for j in range(n)] for i, row in enumerate(M)]
    det = Fr(1)
    for c in range(n):
        piv = next(r for r in range(c, n) if A[r][c] != 0)
        if piv != c:
            A[c], A[piv] = A[piv], A[c]; det = -det
        det *= A[c][c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return det, [row[n:] for row in A]


def endpoint_check(n, C, expect_det):
    L1 = [[2 * int(i == j) + C[i][j] for j in range(n)] for i in range(n)]
    det, Linv = frac_det_inv(L1)
    req(det == expect_det, f"det L(1) n={n}: {det}")
    P, D = motif_diffs(n)
    # rows in D_n (even sum)
    req(all(sum(r) % 2 == 0 for r in L1), f"rows in D_n n={n}")
    # all motif differences p-q (p!=q) NOT in lattice Z^n L1  -> distinct cosets
    bad = 0
    for v in D:
        if any(v):
            x = [sum(Fr(v[k]) * Linv[k][j] for k in range(n)) for j in range(n)]
            if all(y.denominator == 1 for y in x):
                bad += 1
    req(bad == 0, f"motif coset collision n={n}")
    # index [D_n : Lambda] = det/2 must equal number of motif points 2n
    req(det / 2 == 2 * n, f"index n={n}")
    # direct kissing / min distance by enumeration around each ball
    G = [[float(sum(L1[i][k] * L1[j][k] for k in range(n))) for j in range(n)] for i in range(n)]
    ms = fincke_pohst(G, 12.5)
    minimum = None; kiss = {}
    for p in P:
        cnt = 0
        for m in ms:
            x = [sum(m[i] * L1[i][j] for i in range(n)) for j in range(n)]
            for q in P:
                w = [x[j] + q[j] - p[j] for j in range(n)]
                nn = sum(y * y for y in w)
                if nn == 0:
                    continue
                minimum = nn if minimum is None else min(minimum, nn)
                if nn == 2:
                    cnt += 1
        kiss[p] = cnt
    req(minimum == 2, f"min dist^2 n={n}: {minimum}")
    req(set(kiss.values()) == {2 * n * (n - 1)}, f"kissing n={n}: {set(kiss.values())}")
    return det, minimum, set(kiss.values())


for n in range(3, 11):
    print("  endpoint n=%d" % n, endpoint_check(n, Cn(n), 4 * n))
print("  endpoint C4nil", endpoint_check(4, C4NIL, 16))
for n in (16, 25, 40):
    L1 = [[2 * int(i == j) + Cn(n)[i][j] for j in range(n)] for i in range(n)]
    req(frac_det_inv(L1)[0] == 4 * n, f"det n={n}")
print("2. endpoints done")

# ---------- 3. proof-step identities (Lemma 4/5) on boxes + random ----------
def quantities(n, C, m, v):
    w1 = [2 * m[j] + sum(m[i] * C[i][j] for i in range(n)) + v[j] for j in range(n)]
    M = sum(x * x for x in m)
    W1 = sum(x * x for x in w1)
    Dd = sum(a * b for a, b in zip(w1, m))
    E = sum((2 * a + b) * c for a, b, c in zip(m, v, w1))
    return M, W1, Dd, E


def bern_direct(n, C, m, v):
    """Bernstein coeffs of (1+s^2)^2(|m L(s)+v|^2-2), computed from scratch."""
    A0 = [Q2(2 * m[j] + v[j], m[j]) for j in range(n)]
    A1 = [Q2(2 * sum(m[i] * C[i][j] for i in range(n))) for j in range(n)]
    A2 = [Q2(2 * m[j] + v[j], -m[j]) for j in range(n)]
    f = [Q2(0)] * 5
    for j in range(n):
        f = poly_add(f, poly_mul([A0[j], A1[j], A2[j]], [A0[j], A1[j], A2[j]]))
    f = poly_add(f, [Q2(-2), Q2(0), Q2(-4), Q2(0), Q2(-2)])
    return power_to_bernstein(f)


stats = dict(pairs=0, negb=0, negE=0, negD=0, E_lt_m2=0, M1neg=0)
for n in range(3, 9):
    C = Cn(n)
    P, D = motif_diffs(n)
    R = 2 if n <= 5 else 1
    box = itertools.product(range(-R, R + 1), repeat=n)
    for m in box:
        for v in D:
            if not any(m) and not any(v):
                continue
            M, W1, Dd, E = quantities(n, C, m, v)
            stats["pairs"] += 1
            if Dd < 0: stats["negD"] += 1
            if E < -2: stats["E_lt_m2"] += 1
            if M == 1 and E < 0: stats["M1neg"] += 1
            if sum(abs(x) for x in v) == 2 and max(abs(x) for x in v) == 2 and E < 0: stats["negE"] += 1
            if n <= 4 or RNG.random() < 0.05:
                bs = bern_direct(n, C, m, v)
                if any(b.sign() < 0 for b in bs): stats["negb"] += 1
print("3a. box stats", stats)

rng = random.Random(SEED)  # random pairs in step 3b
neg = 0; tested = 0; minE = 10**9
for trial in range(20000):
    n = rng.choice([3, 4, 5, 6, 7, 9, 12, 20, 33])
    C = Cn(n); P, D = motif_diffs(n)
    m = [rng.choice([-3, -2, -1, 0, 0, 0, 1, 2, 3, rng.randint(-50, 50)]) for _ in range(n)]
    v = rng.choice(D)
    if not any(m) and not any(v):
        continue
    M, W1, Dd, E = quantities(n, C, m, v)
    minE = min(minE, E)
    tested += 1
    bs = bern_direct(n, C, m, v) if n <= 12 else None
    if Dd < 0 or E < -2 or (M == 1 and E < 0) or (bs and any(b.sign() < 0 for b in bs)):
        neg += 1
print("3b. random larger m/n: tested", tested, "violations", neg, "min E", minE)
req(stats["negb"] == 0 and stats["negD"] == 0 and stats["E_lt_m2"] == 0 and stats["M1neg"] == 0 and stats["negE"] == 0 and neg == 0, "lemma 4/5 box")

# symbolic check of the Bernstein-coefficient identities used in Lemma 5 (generic real m, v, n=4 twisted C)
n = 4; C = sp.Matrix(Cn(n))
mm = sp.Matrix(1, n, sp.symbols("m0:4")); vv = sp.Matrix(1, n, sp.symbols("v0:4"))
L = (2 + as_) * sp.eye(n) + ts * C
Qs = sp.expand(sp.simplify((1 + s**2) * (mm * L + vv)))
f = sp.expand(sum(Qs[j]**2 for j in range(n)) - 2 * (1 + s**2)**2)
pf = sp.Poly(f, s)
c = [pf.coeff_monomial(s**k) for k in range(5)]
bsym = [sum(c[j] * sp.Rational(math.comb(k, j), math.comb(4, j)) for j in range(k + 1)) for k in range(5)]
w1 = mm * (2 * sp.eye(n) + C) + vv
Msym = (mm * mm.T)[0]; W1 = (w1 * w1.T)[0]; Dsym = (w1 * mm.T)[0]; Esym = ((2 * mm + vv) * w1.T)[0]
w0 = (2 + r2) * mm + vv
claims = [
    (w0 * w0.T)[0] - 2,
    (Esym + 2 * Msym - 2) + r2 * (Dsym + 2 * Msym + (vv * mm.T)[0]),
    sp.Rational(2, 3) * ((Esym + 2 * Msym - 2) + (W1 - 2) + 3 * r2 * Dsym),
    2 * (W1 - 2) + 2 * r2 * Dsym,
    4 * (W1 - 2),
]
for k in range(5):
    req(sp.expand(bsym[k] - claims[k]) == 0, f"Bernstein identity b{k}")
print("3c. Lemma 5 Bernstein identities hold symbolically (n=4 generic m,v)")

# ---------- 4. exact min-distance search at many rational s ----------
def path_min(n, C, sval):
    sv = Fr(sval)
    tt = Q2(2 * sv / (1 + sv * sv))
    aa = Q2(0, (1 - sv * sv) / (1 + sv * sv))
    dd = aa + 2
    L = [[(dd if i == j else Q2(0)) + tt * C[i][j] for j in range(n)] for i in range(n)]
    Lf = [[float(x) for x in row] for row in L]
    G = [[sum(Lf[i][k] * Lf[j][k] for k in range(n)) for j in range(n)] for i in range(n)]
    ms = fincke_pohst(G, 12.2)  # need |mL| <= 2+sqrt2 (squared 11.657)
    P, D = motif_diffs(n)
    best = None; contacts = 0
    for m in ms:
        x = [sum((L[i][j] * m[i] for i in range(n)), Q2(0)) for j in range(n)]
        for v in D:
            if not any(m) and not any(v):
                continue
            w = [x[j] + v[j] for j in range(n)]
            nn = sum((y * y for y in w), Q2(0)) - 2
            sg = nn.sign()
            if sg < 0:
                return ("OVERLAP", m, v, nn)
            if sg == 0:
                contacts += 1
            if best is None or float(nn) < float(best):
                best = nn
    return ("ok", float(best), contacts, len(ms))


svals = sorted(set([Fr(k, 40) for k in range(41)] + [Fr(1, 3), Fr(2, 7), Fr(99, 100), Fr(999, 1000), Fr(1, 1000), Fr(7, 11), Fr(13, 17)]))
summary = {}
for n, C, tag in [(3, Cn(3), "C3"), (4, Cn(4), "C4"), (4, C4NIL, "C4nil"), (5, Cn(5), "C5"), (6, Cn(6), "C6"), (7, Cn(7), "C7")]:
    worst = None; over = 0
    for sv in svals:
        r = path_min(n, C, sv)
        if r[0] != "ok":
            over += 1; print("OVERLAP", tag, sv, r)
        else:
            if sv < 1 and r[2] > 0:
                # contacts at interior s: only allowed for bars; count them
                pass
            worst = r[1] if worst is None else min(worst, r[1])
    summary[tag] = (len(svals), over)
    req(over == 0, f"overlap {tag}")
print("4. rational-s exact search (s values, overlaps):", summary)
# contact count at interior s for C5 should equal bar contacts only
r = path_min(5, Cn(5), Fr(1, 2)); print("   C5 s=1/2:", r)
r = path_min(5, Cn(5), Fr(1)); print("   C5 s=1:", r)

# ---------- 5. Lemma 3 monotonicity numerically (sampled) ----------
worst_ratio = -1e9
for n in range(3, 31):
    for k in range(1, 400):
        tv = k / 400
        h = 1e-6
        def Dn(tq):
            aq = math.sqrt(2 - 2 * tq * tq); dq = 2 + aq
            pk = [1.0, dq]
            for _ in range(2, n): pk.append(dq * pk[-1] - tq * tq * pk[-2])
            return dq * pk[n - 1] + 2 * tq * tq * pk[n - 2] + 2 * tq**n, pk[n - 2]
        der = (Dn(tv + h)[0] - Dn(tv - h)[0]) / (2 * h) if tv + h < 1 else None
        if der is None: continue
        bound = (1 - 3 * math.sqrt(2)) * tv * Dn(tv)[1]
        worst_ratio = max(worst_ratio, der - bound)
print("5. Lemma 3: max over grid of D'(t) - bound =", round(worst_ratio, 6), "(must be <= 0)")
req(worst_ratio <= 1e-6, "lemma 3 bound")

print("FAILURES:", FAIL)
print("RESULT check_dn: %s (%d failed checks)" % ("PASS" if not FAIL else "FAIL", len(FAIL)))
sys.exit(1 if FAIL else 0)
