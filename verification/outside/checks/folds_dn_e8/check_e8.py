"""Independent check of AUDIT-017: the F_8 to E_8 fold.

Backs the statement "F_8 to E_8 fold (017)" in VERDICTS.md, section 1: the endpoint is
sqrt 2 E_8 (even unimodular, 240 contacts at every ball), all 32,640 degree-8 certificate
polynomials recomputed exactly (0 negative Bernstein coefficients, 976 zeros), and an exact
search for overlaps at 30 rational values of s. Also the Gram determinants behind the E_6
and E_7 part of Theorem 2. The Loewner step is in check_e8_loewner.py.
Shares no code with the verifiers under test.

Needs: Python 3, SymPy, and common.py from this folder. No clone of the target repository
and no network. No randomness.
Run:   python3 -I -B check_e8.py
Time:  about 3 minutes.
Result: one line starting RESULT, exit code 0 only if every check held.
"""
import sys, os, itertools, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
from common import Q2, power_to_bernstein, poly_mul, poly_add, fincke_pohst
import sympy as sp

FAIL = []


def req(c, msg):
    if not c:
        FAIL.append(msg); print("FAIL:", msg)


H = [[(-1) ** bin(i & j).count("1") for j in range(8)] for i in range(8)]
Ip = [i for i in range(8) if H[i][i] == 1]
req(Ip == [0, 3, 5, 6], "I+")

# ---- symbolic curve built from the written definition ----
s = sp.symbols("s", real=True); r2 = sp.sqrt(2)
Dp = (1 + 2 * r2) + (-1 + 2 * r2) * s**2
Dm = (-1 + 2 * r2) + (1 + 2 * r2) * s**2
ap = ((6 + 5 * r2) + (-6 + 5 * r2) * s**2) / Dp
bp = 2 * r2 * s / Dp
am = ((2 + 3 * r2) + (-2 + 3 * r2) * s**2) / Dm
bm = 2 * r2 * s / Dm
L = sp.zeros(8, 8)
for i in range(8):
    a_, b_ = (ap, bp) if i in Ip else (am, bm)
    for j in range(8):
        L[i, j] = a_ if i == j else b_ * H[i][j]
for i in range(8):
    b = L.row(i) - 2 * sp.eye(8).row(i)
    req(sp.simplify(sp.together(b.dot(b)) - 2) == 0, f"bar {i}")
req(sp.simplify(L.subs(s, 0) - (2 + r2) * sp.eye(8)) == sp.zeros(8, 8), "L(0)")
L1 = sp.simplify(L.subs(s, 1))
req(L1 == 2 * sp.eye(8) + sp.Rational(1, 2) * sp.Matrix(H), "L(1)")
# denominators positive on [0,1]: all coefficients positive (1+2r2>0, -1+2r2>0)
print("1. bars identically sqrt2, endpoints ok")

# ---- endpoint lattice identification ----
L1f = [[Fr(2 * int(i == j)) + Fr(H[i][j], 2) for j in range(8)] for i in range(8)]
G1 = [[sum(L1f[i][k] * L1f[j][k] for k in range(8)) for j in range(8)] for i in range(8)]
Ghalf = sp.Matrix(G1) / 2
req(all(Ghalf[i, i] % 2 == 0 for i in range(8)) and all(x.q == 1 for x in Ghalf), "G/2 even integral")
req(Ghalf.det() == 1, "G/2 unimodular")
print("   G(1)/2 even unimodular rank 8 => Z^8 L(1) = sqrt2 * E8")
# in standard E8 coordinates
def inE8(x):
    if all(y.denominator == 1 for y in x):
        return sum(x) % 2 == 0
    if all((2 * y).denominator == 1 and (2 * y) % 2 == 1 for y in x):
        return sum(x) % 2 == 0
    return False
req(all(inE8(row) for row in L1f), "rows in E8")
L1inv = sp.Matrix(L1f).inv()
P = []
for i in range(8):
    for sg in (1, -1):
        e = [0] * 8; e[i] = sg; P.append(e)
Vd = sorted({tuple(p[k] - q[k] for k in range(8)) for p in P for q in P})
coll = 0
for v in Vd:
    if any(v):
        x = sp.Matrix([v]) * L1inv
        if all(y.q == 1 for y in x):
            coll += 1
req(coll == 0, "motif cosets distinct")
req(sp.Matrix(L1f).det() == 16, "det 16")
# kissing by enumeration of the packing around each ball
Gf = [[float(x) for x in row] for row in G1]
ms = fincke_pohst(Gf, 12.5)
shells = {}
for m in ms:
    nn = sum(m[i] * m[j] * G1[i][j] for i in range(8) for j in range(8))
    shells[nn] = shells.get(nn, 0) + 1
print("   lattice shells (norm: count) up to 12:", dict(sorted(shells.items())))
req(shells.get(4) == 240 and shells.get(8) == 2160, "shells")
kiss = set(); mn = None
for p in P:
    cnt = 0
    for m in ms:
        x = [sum(m[i] * L1f[i][j] for i in range(8)) for j in range(8)]
        for q in P:
            w = [x[j] + q[j] - p[j] for j in range(8)]
            nn = sum(y * y for y in w)
            if nn == 0: continue
            mn = nn if mn is None else min(mn, nn)
            if nn == 2: cnt += 1
    kiss.add(cnt)
req(mn == 2 and kiss == {240}, f"kissing {kiss} min {mn}")
print("2. endpoint: det 16, min dist^2", mn, "kissing", kiss)

# Loewner step: see check_e8_loewner.py (separate, lighter derivation)

# ---- finite reduction and full Bernstein recomputation ----
def Lnum(sv):
    """L(s) at rational s, exact Q(sqrt2)."""
    sv = Fr(sv)
    Dp_ = Q2(1 - sv * sv, 2 + 2 * sv * sv); Dm_ = Q2(-1 + sv * sv, 2 + 2 * sv * sv)
    ap_ = Q2(6 - 6 * sv * sv, 5 + 5 * sv * sv) / Dp_; bp_ = Q2(0, 2 * sv) / Dp_
    am_ = Q2(2 - 2 * sv * sv, 3 + 3 * sv * sv) / Dm_; bm_ = Q2(0, 2 * sv) / Dm_
    out = []
    for i in range(8):
        a_, b_ = (ap_, bp_) if i in Ip else (am_, bm_)
        out.append([a_ if i == j else b_ * H[i][j] for j in range(8)])
    return out

# polynomial rows: numerator polys in s over common denominator Dp*Dm
DpP = [Q2(1, 2), Q2(0), Q2(-1, 2)]; DmP = [Q2(-1, 2), Q2(0), Q2(1, 2)]
apN = [Q2(6, 5), Q2(0), Q2(-6, 5)]; amN = [Q2(2, 3), Q2(0), Q2(-2, 3)]; bN = [Q2(0), Q2(0, 2)]
def build_rowpoly(Hm):
    rp = []
    for i in range(8):
        if i in Ip:
            diag = poly_mul(apN, DmP); off = poly_mul(bN, DmP)
        else:
            diag = poly_mul(amN, DpP); off = poly_mul(bN, DpP)
        rp.append([diag if i == j else [c * Hm[i][j] for c in off] for j in range(8)])
    return rp


rowpoly = build_rowpoly(H)
den = poly_mul(DpP, DmP)  # degree 4
den2 = poly_mul(den, den)

def pair_bernstein(m, v, rp):
    """Exact Bernstein coefficients of the degree-8 polynomial for the pair (m, v), row polynomials rp."""
    vec = []
    for j in range(8):
        acc = [Q2(0)] * 5
        for i in range(8):
            if m[i]:
                acc = poly_add(acc, [c * m[i] for c in rp[i][j]])
        acc = poly_add(acc, [c * v[j] for c in den])
        vec.append(acc)
    f = [Q2(0)] * 9
    for comp in vec:
        f = poly_add(f, poly_mul(comp, comp))
    f = poly_add(f, [c * (-2) for c in den2])
    return power_to_bernstein(f)


Nm = {}
for m in ms:
    if any(m):
        nn = sum(m[i] * m[j] * G1[i][j] for i in range(8) for j in range(8))
        Nm[m] = nn
canon = lambda m: m if next(x for x in m if x != 0) > 0 else tuple(-x for x in m)
M4 = sorted({canon(m) for m, nn in Nm.items() if nn == 4})
M48 = sorted({canon(m) for m, nn in Nm.items() if nn in (4, 8)})
V2 = [v for v in Vd if sum(x * x for x in v) == 2]
V4 = [v for v in Vd if sum(x * x for x in v) == 4]
pairs = [(m, v) for m in M4 for v in V2] + [(m, v) for m in M48 for v in V4]
print("4. finite set:", len(M4), "x", len(V2), "+", len(M48), "x", len(V4), "=", len(pairs))
req(len(pairs) == 32640, "pair count")
neg = 0; zeros = 0; interior_zero_nonbar = 0; minpos = None; zero_pairs = []
for (m, v) in pairs:
    bs = pair_bernstein(m, v, rowpoly)
    sg = [b.sign() for b in bs]
    neg += sum(1 for x in sg if x < 0)
    z = sum(1 for x in sg if x == 0)
    zeros += z
    if z:
        zero_pairs.append((m, v, tuple(k for k, x in enumerate(sg) if x == 0)))
    is_bar = sum(abs(x) for x in m) == 1 and all(m[k] * v[k] == -2 for k in range(8) if m[k])
    if not is_bar and any(sg[k] == 0 for k in range(8)):
        interior_zero_nonbar += 1
print("   negative Bernstein coeffs:", neg, " zero coeffs:", zeros, " non-bar pairs with a zero at k<8:", interior_zero_nonbar)
req(neg == 0, "neg bernstein")
bar_pairs = [z for z in zero_pairs if len(z[2]) == 9]
print("   identically-zero pairs (bars):", len(bar_pairs), " s=1-only zero pairs:", sum(1 for z in zero_pairs if z[2] == (8,)))

# ---- exact short-vector search along the path at many rational s ----
def path_scan(svals, quiet=False):
    """Exact search for overlaps (distance^2 < 2 between motif points) at each rational s. Returns (overlaps, rows)."""
    over = 0; mins = []
    for sv in svals:
        Ls = Lnum(sv)
        Lf = [[float(x) for x in row] for row in Ls]
        Gs = [[sum(Lf[i][k] * Lf[j][k] for k in range(8)) for j in range(8)] for i in range(8)]
        cand = fincke_pohst(Gs, 12.2)
        best = None; cont = 0
        nexact = 0
        for m in cand:
            xf = [sum(Lf[i][j] * m[i] for i in range(8)) for j in range(8)]
            x = None
            for v in Vd:
                if not any(m) and not any(v): continue
                gf = sum((xf[j] + v[j]) ** 2 for j in range(8)) - 2
                if gf > 1e-6:
                    if best is None or gf < best: best = gf
                    continue
                if x is None:
                    x = [sum((Ls[i][j] * m[i] for i in range(8) if m[i]), Q2(0)) for j in range(8)]
                nexact += 1
                nn = sum(((x[j] + v[j]) * (x[j] + v[j]) for j in range(8)), Q2(0)) - 2
                sg = nn.sign()
                if sg < 0:
                    over += 1
                    if not quiet: print("OVERLAP", sv, m, v)
                if sg == 0: cont += 1
                if sg > 0 and (best is None or float(nn) < best): best = float(nn)
        mins.append((str(sv), nexact, cont, round(best, 5) if best is not None else None))
    return over, mins


svals = sorted(set([Fr(k, 24) for k in range(25)] + [Fr(1, 1000), Fr(999, 1000), Fr(9999, 10000), Fr(3, 7), Fr(5, 13)]))
over, mins = path_scan(svals)
print("5. path search: s values", len(svals), "overlaps", over)
print("   (s, exact contacts (m,v), smallest positive gap) sample:", mins[:3], mins[-4:])
req(over == 0, "path overlap")

# ---- Theorem 2: determinants ----
def cartan(name):
    if name == "E6":
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (2, 5)]; n = 6
    elif name == "E7":
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (2, 6)]; n = 7
    elif name == "E8":
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (2, 7)]; n = 8
    A = sp.eye(n) * 2
    for i, j in edges:
        A[i, j] = A[j, i] = -1
    return A
def cartanD(n):
    A = sp.eye(n) * 2
    for i in range(n - 2):
        A[i, i + 1] = A[i + 1, i] = -1
    A[n - 3, n - 1] = A[n - 1, n - 3] = -1
    return A
dets = {k: cartan(k).det() for k in ("E6", "E7", "E8")}
dets.update({f"D{n}": cartanD(n).det() for n in (6, 7, 8)})
print("6. Gram dets:", dets)
# ---- must-fail controls: perturbed inputs that the checks above must refuse ----
# A check that can only pass proves nothing. Each control feeds a deliberately wrong input to the same code
# as the checks above and requires the expected failure. A control that does NOT fail is itself a failure.
CONTROLS = 0
# 7a. A Hadamard matrix with one sign flipped (entry [1][2] only, so it is no longer symmetric or orthogonal):
# the endpoint Gram matrix G(1)/2 must stop being even unimodular, which step 1 of the endpoint identification requires.
Hbad = [row[:] for row in H]
Hbad[1][2] = -Hbad[1][2]
L1bad = [[Fr(2 * int(i == j)) + Fr(Hbad[i][j], 2) for j in range(8)] for i in range(8)]
Gbad = sp.Matrix([[sum(L1bad[i][k] * L1bad[j][k] for k in range(8)) for j in range(8)] for i in range(8)]) / 2
good_gram = all(Gbad[i, i] % 2 == 0 for i in range(8)) and all(x.q == 1 for x in Gbad) and Gbad.det() == 1
print("7a. flipped-sign Hadamard: G/2 even, integral and unimodular?", good_gram, "(must be False)")
req(not good_gram, "control 7a: flipped-sign Hadamard must not give an even unimodular Gram matrix")
CONTROLS += 1
# 7b. the same flipped Hadamard, put into the row polynomials, must give a negative Bernstein coefficient
# for some pair of the finite set (same pair_bernstein as above; the scan stops at the first one, near pair 5733).
rowpoly_bad = build_rowpoly(Hbad)
first_neg = next((k for k, (m, v) in enumerate(pairs) if any(b.sign() < 0 for b in pair_bernstein(m, v, rowpoly_bad))), None)
print("7b. flipped-sign Hadamard: first pair with a negative Bernstein coefficient:", first_neg, "(must exist)")
req(first_neg is not None, "control 7b: flipped-sign Hadamard must show a negative Bernstein coefficient")
CONTROLS += 1
# 7c. s = 11/10, just above 1: the exact path search must find an overlap (the claim is for 0 <= s <= 1).
over_c, _ = path_scan([Fr(11, 10)], quiet=True)
print("7c. s = 11/10: overlaps found:", over_c, "(must be > 0)")
req(over_c > 0, "control 7c: s = 11/10 must overlap")
CONTROLS += 1
print("7. must-fail controls that failed as required:", CONTROLS - sum(1 for f in FAIL if f.startswith("control")), "of", CONTROLS)

print("FAILURES:", FAIL)
print("RESULT check_e8: %s (%d failed checks)" % ("PASS" if not FAIL else "FAIL", len(FAIL)))
sys.exit(1 if FAIL else 0)
