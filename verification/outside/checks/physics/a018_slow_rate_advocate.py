#!/usr/bin/env python3
"""Advocate check of the 16x16 Lindblad slow rate (AUDIT-018). Own SymPy build, no shared code.

Backs: VERDICTS section 2, row "Lindblad reduction (018)" (second-order adiabatic
elimination, mathematics N0). In exact SymPy arithmetic: (a) the 8x8 Schur
complement at s = 0 on span{I,Z} (x) Paulis is diagonal with the eight reported
entries; (b) the exact slow rate of the (IX, XY) block is
2 gt + 2 g^2/(gCM - gt) + O(g^4), which differs from the Schur rate
2 gt + 2 g^2/gCM at O(g^2) when gt is not 0 and agrees when gt = 0;
(c) the eigenvalue product identity holds exactly and the ratio of true to Schur
rate tends to 1 as N grows (rate gCM = N^2 gamma1); (d) the frequency-dependent
Schur complement has its fixed point exactly at the slow eigenvalue.

H = g X(x)Z + w I(x)Z; jumps sqrt(gcm) Z(x)I, sqrt(gt) Z(x)Z. Exact arithmetic,
no random numbers, no repository needed.

Needs: Python 3, sympy.
Run:   python3 -I -B a018_slow_rate_advocate.py   (add --verbose for details)
Time:  about 1 to 3 seconds.
Exit:  0 only if every check holds.
"""
import json
import sys
import sympy as sp

I2 = sp.eye(2)
X = sp.Matrix([[0, 1], [1, 0]])
Y = sp.Matrix([[0, -sp.I], [sp.I, 0]])
Z = sp.Matrix([[1, 0], [0, -1]])
P = {"I": I2, "X": X, "Y": Y, "Z": Z}
LAB = [a + b for a in "IZ" for b in "IXYZ"] + [a + b for a in "XY" for b in "IXYZ"]
BAS = [sp.kronecker_product(P[l[0]], P[l[1]]) / 2 for l in LAB]  # Hilbert-Schmidt orthonormal


NAME = "a018_slow_rate_advocate"
FAILS = []
COUNT = [0]


def need(c, m):
    COUNT[0] += 1
    if not c:
        FAILS.append(m)


def gksl(g, w, gcm, gt):
    H = g * sp.kronecker_product(X, Z) + w * sp.kronecker_product(I2, Z)
    Ls = [(gcm, sp.kronecker_product(Z, I2)), (gt, sp.kronecker_product(Z, Z))]
    M = sp.zeros(16, 16)
    for c, B in enumerate(BAS):
        out = -sp.I * (H * B - B * H)
        for gam, L in Ls:
            out += gam * (L * B * L.H - (L.H * L * B + B * L.H * L) / 2)
        for r in range(16):
            M[r, c] = sp.nsimplify(sp.expand((BAS[r].H * out).trace()))
    return M


def main():
    res = {}
    g, gcm, gt, s = sp.symbols("g gamma_CM gamma_tid s", positive=True)
    L = gksl(g, 0, gcm, gt)
    need(L.is_real if hasattr(L, "is_real") else True, "real")
    A, B, C, F = L[:8, :8], L[:8, 8:], L[8:, :8], L[8:, 8:]
    S0 = (A - B * F.inv() * C).applyfunc(sp.simplify)
    res["schur_s0_diag"] = {LAB[i]: str(sp.factor(S0[i, i])) for i in range(8)}
    res["schur_s0_offdiag_zero"] = all(sp.simplify(S0[i, j]) == 0 for i in range(8) for j in range(8) if i != j)
    # (b) exact block (IX, XY)
    iIX, iXY = LAB.index("IX"), LAB.index("XY")
    blk = L.extract([iIX, iXY], [iIX, iXY])
    res["block_IX_XY"] = str(blk)
    ev = list(blk.eigenvals().keys())
    need(len(ev) == 2, "the block does not have two eigenvalues")
    if len(ev) != 2:
        raise SystemExit("The IX-XY block did not give two eigenvalues; cannot continue.")
    pt = {g: 1, gcm: 10, gt: 1}
    slow = max(ev, key=lambda e: float(sp.N(e.subs(pt))))
    gam_slow = sp.simplify(-slow)
    res["exact_slow_rate"] = str(gam_slow)
    ser = sp.series(gam_slow, g, 0, 5).removeO()
    res["slow_rate_series_g4"] = str(sp.simplify(ser))
    schur = 2 * gt + 2 * g**2 / gcm
    alt = 2 * gt + 2 * g**2 / (gcm - gt)
    res["g2_coeff_true_minus_schur"] = str(sp.factor(sp.simplify(sp.diff(gam_slow, g, 2).subs(g, 0) / 2 - 2 / gcm)))
    res["g2_coeff_true_minus_alt"] = str(sp.simplify(sp.diff(gam_slow, g, 2).subs(g, 0) / 2 - 2 / (gcm - gt)))
    # (c) product identity
    prod = sp.simplify(sp.prod([-e for e in ev]))
    res["product_minus_2gcm_schur"] = str(sp.simplify(prod - 2 * gcm * schur))
    # (d) frequency-dependent Schur fixed point on the 2x2 block: S(s) = a - b c/(f - s)
    Ss = blk[0, 0] - blk[0, 1] * blk[1, 0] / (blk[1, 1] - s)
    res["S(lambda_slow)-lambda_slow"] = str(sp.simplify(Ss.subs(s, slow) - slow))
    # numeric table at the team's parameters (g = 3/2, gamma1 = 1/4, gamma_tid = 1/100 guessed) and N
    num = []
    for (gv, g1, gtv) in ((sp.Rational(3, 2), sp.Rational(1, 4), sp.Rational(1, 2)), (sp.Rational(3, 2), sp.Rational(1, 4), 0)):
        for N in (5, 10, 20, 100):
            sub = {g: gv, gcm: N * N * g1, gt: gtv}
            t = sp.N(gam_slow.subs(sub), 30)
            num.append({"g": str(gv), "gamma1": str(g1), "gamma_tid": str(gtv), "N": N,
                        "true_over_schur": float(t / sp.N(schur.subs(sub), 30)),
                        "true_over_alt": float(t / sp.N(alt.subs(sub), 30))})
    res["numeric"] = num
    need(res["schur_s0_offdiag_zero"], "the s = 0 Schur complement is not diagonal")
    want = {"II": "0", "IZ": "0", "ZX": "-2*gamma_tid", "ZY": "-2*gamma_tid",
            "IX": "-2*(g**2 + gamma_CM*gamma_tid)/gamma_CM", "IY": "-2*(g**2 + gamma_CM*gamma_tid)/gamma_CM",
            "ZI": "-2*g**2/(gamma_CM + gamma_tid)", "ZZ": "-2*g**2/(gamma_CM + gamma_tid)"}
    need(res["schur_s0_diag"] == want, "the eight Schur diagonals differ from the report")
    need(res["block_IX_XY"] == "Matrix([[-2*gamma_tid, -2*g], [2*g, -2*gamma_CM]])", "the IX-XY block differs")
    need(res["product_minus_2gcm_schur"] == "0", "the eigenvalue product identity fails")
    need(res["S(lambda_slow)-lambda_slow"] == "0", "the frequency-dependent Schur complement has no fixed point at the slow eigenvalue")
    # g^2 coefficient of (true slow rate - Schur rate) is 2 gt / (gCM (gCM - gt)): nonzero only when gt is not 0
    c2 = sp.sympify(res["g2_coeff_true_minus_schur"], locals={"g": g, "gamma_CM": gcm, "gamma_tid": gt})
    point = {gcm: 10, gt: 1}
    need(sp.simplify(c2.subs(point) - sp.Rational(2, 90)) == 0, "g^2 coefficient is not 2 gt/(gCM (gCM - gt)) at gCM=10, gt=1")
    need(sp.simplify(c2.subs({gcm: 10, gt: 0})) == 0, "g^2 coefficient is not zero at gt = 0")
    c2a = sp.sympify(res["g2_coeff_true_minus_alt"], locals={"g": g, "gamma_CM": gcm, "gamma_tid": gt})
    need(sp.simplify(c2a.subs(point)) == 0, "the 2 gt + 2 g^2/(gCM - gt) form does not match at O(g^2)")
    nums = res["numeric"]
    for row in nums:
        if row["gamma_tid"] == "0":
            need(abs(row["true_over_schur"] - row["true_over_alt"]) < 1e-12, "at gt = 0 the two reference rates differ")
        else:
            need(abs(row["true_over_schur"] - 1) > abs(row["true_over_alt"] - 1), "at gt != 0 the Schur rate is not the worse approximation (N=%d)" % row["N"])
    last = {r["gamma_tid"]: r for r in nums if r["N"] == 100}
    need(abs(last["0"]["true_over_schur"] - 1.00000036) < 1e-8, "ratio at N = 100, gt = 0 is not 1.00000036")
    need(abs(nums[0]["true_over_schur"] - 1.0724684781) < 1e-8 and abs(nums[4]["true_over_schur"] - 1.0653777085) < 1e-8,
         "ratio at N = 5 is not 1.0725 (gt = 1/2) and 1.0654 (gt = 0)")
    ratios = [r["true_over_schur"] for r in nums if r["gamma_tid"] == "0"]
    need(all(ratios[i] > ratios[i + 1] > 1 for i in range(len(ratios) - 1)), "the ratio does not fall toward 1 as N grows")
    if "--verbose" in sys.argv:
        print(json.dumps(res, indent=1, sort_keys=True))
    if FAILS:
        print("RESULT %s: FAIL %d of %d checks: %s" % (NAME, len(FAILS), COUNT[0], "; ".join(FAILS[:4])))
        sys.exit(1)
    print("RESULT %s: PASS %d of %d checks; Schur diagonals exact; true slow rate minus Schur rate is 2 g^2 gt/(gCM(gCM-gt)) at O(g^2); "
          "ratio %.7f at N=100, gt=0" % (NAME, COUNT[0], COUNT[0], last["0"]["true_over_schur"]))


if __name__ == "__main__":
    main()
