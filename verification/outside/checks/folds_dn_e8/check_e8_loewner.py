"""Independent check of the Loewner step G(s) >= G(1) in the F_8 to E_8 fold (AUDIT-017).

Backs the statement "Loewner step re-derived a different way" under "F_8 to E_8 fold (017)"
in VERDICTS.md, section 1: exact root isolation instead of Bernstein coefficients.
Shares no code with the verifiers under test. SymPy only, no clone, no network, no randomness.
Run:   python3 -I -B check_e8_loewner.py
Time:  about 1 minute.
Result: one line starting RESULT, exit code 0 only if every check held.

Method. 
L = D1 + D2 H with D1 = diag(a_i - b_i H_ii), D2 = diag(b_i). For an eigenvector u of K (P^T H P = [[K,K],[K,-K]])
with eigenvalue mu, span{f1=(u,0), f2=(0,u)} is invariant under H, D1, D2, so L acts there (on columns) as
A_mu = [[al + mu b+, mu b+], [mu b-, be - mu b-]], al = a+ - b+, be = a- + b-, and G = L L^T acts as A A^T.
We (1) verify L B = B blockdiag(A_mu) exactly at rational s, (2) prove A A^T - A(1)A(1)^T >= 0 on [0,1] exactly."""
import sys
from fractions import Fraction as Fr
import sympy as sp

s = sp.symbols("s", real=True); r2 = sp.sqrt(2)
Dp = (1 + 2 * r2) + (-1 + 2 * r2) * s**2
Dm = (-1 + 2 * r2) + (1 + 2 * r2) * s**2
ap = ((6 + 5 * r2) + (-6 + 5 * r2) * s**2) / Dp
bp = 2 * r2 * s / Dp
am = ((2 + 3 * r2) + (-2 + 3 * r2) * s**2) / Dm
bm = 2 * r2 * s / Dm
H = sp.Matrix(8, 8, lambda i, j: (-1) ** bin(i & j).count("1"))
Ip = [0, 3, 5, 6]
perm = [0, 3, 5, 6, 7, 4, 2, 1]
Pm = sp.zeros(8, 8)
for j, i in enumerate(perm):
    Pm[i, j] = 1
HH = Pm.T * H * Pm
K = HH[:4, :4]
FAIL = []


def req(c, msg):
    if not c:
        FAIL.append(msg)
        print("FAIL:", msg)


assert_ok = HH[:4, 4:] == K and HH[4:, :4] == K and HH[4:, 4:] == -K
req(assert_ok, "K-block form")
print("K-block form:", assert_ok, " K eigenvalues:", K.eigenvals())
basis = []; mus = []
for val, mult, vecs in K.eigenvects():
    for u in sp.GramSchmidt(vecs, True):
        basis.append(Pm * sp.Matrix.vstack(u, sp.zeros(4, 1)))
        basis.append(Pm * sp.Matrix.vstack(sp.zeros(4, 1), u))
        mus.append(val)
B = sp.Matrix.hstack(*basis)
req(sp.simplify(B.T * B) == sp.eye(8), "B orthonormal")
print("B orthonormal:", sp.simplify(B.T * B) == sp.eye(8))


def Lmat(sv):
    L = sp.zeros(8, 8)
    for i in range(8):
        a_, b_ = (ap, bp) if i in Ip else (am, bm)
        for j in range(8):
            L[i, j] = (a_ if i == j else b_ * H[i, j]).subs(s, sv)
    return L


def Amu(mu, sv=None):
    al = ap - bp; be = am + bm
    A = sp.Matrix([[al + mu * bp, mu * bp], [mu * bm, be - mu * bm]])
    return A if sv is None else A.subs(s, sv)


ok = True
for sv in [sp.Rational(1, 3), sp.Rational(5, 7), sp.Rational(1, 1), sp.Rational(0)]:
    L = Lmat(sv)
    Blk = sp.diag(*[Amu(mu, sv) for mu in mus])
    diff = (B.T * L * B - Blk).applyfunc(lambda e: sp.nsimplify(sp.simplify(e)))
    ok = ok and diff == sp.zeros(8, 8)
req(ok, "L = B blockdiag(A_mu) B^T")
print("L = B blockdiag(A_mu) B^T at s in {1/3,5/7,1,0}:", ok)
# the identity is in fact polynomial in (a+,b+,a-,b-), check it with free symbols too
A1, B1, A2, B2 = sp.symbols("A1 B1 A2 B2")
Lg = sp.zeros(8, 8)
for i in range(8):
    a_, b_ = (A1, B1) if i in Ip else (A2, B2)
    for j in range(8):
        Lg[i, j] = a_ if i == j else b_ * H[i, j]
Blk = sp.diag(*[sp.Matrix([[A1 - B1 + mu * B1, mu * B1], [mu * B2, A2 + B2 - mu * B2]]) for mu in mus])
gen_ok = (B.T * Lg * B - Blk).applyfunc(sp.simplify) == sp.zeros(8, 8)
req(gen_ok, "generic-symbol identity")
print("generic-symbol identity B^T L B = blockdiag:", gen_ok)


def split(poly_expr):
    P = sp.Poly(sp.expand(poly_expr), s)
    c1 = []; c2 = []
    for c in P.all_coeffs():
        c = sp.expand(c); q2 = sp.expand(c.coeff(r2)); q1 = sp.expand(c - q2 * r2)
        if not (q1.is_rational and q2.is_rational):
            raise SystemExit("split: coefficient is not in Q(sqrt 2)")
        c1.append(q1); c2.append(q2)
    return sp.Poly(c1, s), sp.Poly(c2, s)


def sgnQ2(a, b):
    a = Fr(str(a)); b = Fr(str(b))
    sa = (a > 0) - (a < 0); sb = (b > 0) - (b < 0)
    if sa == 0: return sb
    if sb == 0 or sa == sb: return sa
    dd = a * a - 2 * b * b
    return sa if dd > 0 else (-sa if dd < 0 else 0)


def nonneg01(expr):
    num, den = sp.fraction(sp.cancel(sp.together(expr)))
    parts = [split(num), split(den)]
    pts = {sp.Integer(0), sp.Integer(1)}
    for P1, P2 in parts:
        N = P1**2 - 2 * P2**2
        if N.is_zero: continue
        for (lo, hi), _ in N.intervals():
            for x in (lo, hi):
                if 0 <= x <= 1: pts.add(x)
    pts = sorted(pts); test = set(pts)
    for x, y in zip(pts, pts[1:]): test.add((x + y) / 2)
    bad = [x for x in test if sgnQ2(parts[0][0].eval(x), parts[0][1].eval(x)) * sgnQ2(parts[1][0].eval(x), parts[1][1].eval(x)) < 0]
    return bad


allok = True
for mu in sorted(set(mus)):
    A = Amu(mu); A1m = Amu(mu, 1)
    X = (A * A.T - A1m * A1m.T).applyfunc(sp.cancel)
    for name, e in (("x00", X[0, 0]), ("x11", X[1, 1]), ("det", sp.cancel(X[0, 0] * X[1, 1] - X[0, 1] * X[1, 0]))):
        bad = nonneg01(e)
        print(f"  mu={mu} {name}: negative test points on [0,1]: {len(bad)}")
        allok = allok and not bad
    # also: is it strictly PD in the interior? sample sign of det at s=1/2
    print(f"  mu={mu} det at s=1/2 sign:", sp.sign(sp.N(X[0, 0] * X[1, 1] - X[0, 1] ** 2, 30).subs(s, sp.Rational(1, 2))) if False else sp.N((X[0, 0] * X[1, 1] - X[0, 1] * X[1, 0]).subs(s, sp.Rational(1, 2)), 20))
req(allok, "Loewner inequality")
print("LOEWNER G(s) >= G(1) on [0,1]:", "PROVED (exact root isolation)" if allok else "FAILED")
# ---- must-fail controls: wrong inputs that the exact test nonneg01 must refuse ----
# A test that can only pass proves nothing. nonneg01 returns the list of test points where its argument is negative.
CONTROLS = 0
mu0 = sorted(set(mus))[0]
A0m = Amu(mu0); A1c = Amu(mu0, 1)
X0 = (A0m * A0m.T - A1c * A1c.T).applyfunc(sp.cancel)
# (a) the sign-flipped (1,1) entry of G(s) - G(1) must be refused: it is negative inside (0, 1).
bad_a = nonneg01(-X0[0, 0])
print("control (a), minus the (1,1) entry:", len(bad_a), "negative test points (must be > 0)")
req(len(bad_a) > 0, "control (a): negated Loewner entry must be refused")
CONTROLS += 1
# (b) the wrong base point: G(s) - G(1/2) is not >= 0 on [0, 1] (it is negative for s < 1/2).
A12 = Amu(mu0, sp.Rational(1, 2))
Xh = (A0m * A0m.T - A12 * A12.T).applyfunc(sp.cancel)
bad_b = nonneg01(Xh[0, 0]) + nonneg01(Xh[1, 1])
print("control (b), base point s = 1/2:", len(bad_b), "negative test points (must be > 0)")
req(len(bad_b) > 0, "control (b): base point 1/2 must be refused")
CONTROLS += 1
# (c) a flipped sign in the Hadamard matrix breaks the invariant-plane identity L B = B blockdiag(A_mu).
Hbad = H.copy(); Hbad[1, 2] = -Hbad[1, 2]
Lg_bad = sp.zeros(8, 8)
for i in range(8):
    a_, b_ = (A1, B1) if i in Ip else (A2, B2)
    for j in range(8):
        Lg_bad[i, j] = a_ if i == j else b_ * Hbad[i, j]
still_ok = (B.T * Lg_bad * B - Blk).applyfunc(sp.simplify) == sp.zeros(8, 8)
print("control (c), flipped-sign Hadamard keeps the block identity?", still_ok, "(must be False)")
req(not still_ok, "control (c): flipped-sign Hadamard must break the block identity")
CONTROLS += 1
print("must-fail controls that failed as required:", CONTROLS - sum(1 for f in FAIL if f.startswith("control")), "of", CONTROLS)

print("RESULT check_e8_loewner: %s (%d failed checks)" % ("PASS" if not FAIL else "FAIL", len(FAIL)))
sys.exit(1 if FAIL else 0)
