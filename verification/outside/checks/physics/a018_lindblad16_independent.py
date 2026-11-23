#!/usr/bin/env python3
"""Independent check of the 16x16 Lindblad reduction (AUDIT-018). Shares no code with the team.

Backs: VERDICTS section 1 row "16x16 Lindblad reduction (018)": an independent
symbolic build matches all eight Schur diagonals and the Jordan ranks at the
stated exceptional points; and the section 2 label (second-order adiabatic
elimination, mathematics N0). It also backs the statement that the Schur
complement is exact only as the s = 0 reduction: the true slow rate differs
from it at order g^2 when gamma_tid is not 0.

Model, as stated in the report: two qubits (centre-of-mass qubit and internal
qubit), operators on C^2 (x) C^2, so a 16-dimensional space; GKSL generator
L(rho) = -i[H, rho] + gCM (Z1 rho Z1 - rho) + gt (ZZ rho ZZ - rho),
H = g X(x)Z + w I(x)Z, gCM = N^2 g1. Built with SymPy Kronecker products on the
16 Pauli strings (normalised Hilbert-Schmidt basis). Exact arithmetic, no
random numbers, no repository needed.

Needs: Python 3, sympy.
Run:   python3 -I -B a018_lindblad16_independent.py   (add --verbose for details)
Time:  about 1 to 2 seconds.
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
LABELS = [a + b for a in "IXYZ" for b in "IXYZ"]
BASIS = {l: sp.kronecker_product(P[l[0]], P[l[1]]) for l in LABELS}

g, g1, gt, w, N, s = sp.symbols("g gamma1 gammatid omega N s", positive=True)
gCM = N**2 * g1


NAME = "a018_lindblad16_independent"
FAILS = []
COUNT = [0]


def check(cond, msg):
    COUNT[0] += 1
    if not cond:
        FAILS.append(msg)


def generator(H, jumps):
    def act(A):
        out = -sp.I * (H * A - A * H)
        for rate, Lj in jumps:
            out += rate * (Lj * A * Lj.H - (Lj.H * Lj * A + A * Lj.H * Lj) / 2)
        return out
    M = sp.zeros(16, 16)
    for j, lj in enumerate(LABELS):
        img = act(BASIS[lj])
        for i, li in enumerate(LABELS):
            M[i, j] = sp.simplify((BASIS[li].H * img).trace() / 4)
    return M


def main():
    H = g * BASIS["XZ"] + w * BASIS["IZ"]
    jumps = [(gCM, BASIS["ZI"]), (gt, BASIS["ZZ"])]
    L = generator(H, jumps)
    out = {"real_matrix": all(sp.im(sp.simplify(e)) == 0 for e in L)}
    inv = [i for i, l in enumerate(LABELS) if l[0] in "IZ"]
    wit = [i for i, l in enumerate(LABELS) if l[0] in "XY"]
    Lii, Liw, Lwi, Lww = L.extract(inv, inv), L.extract(inv, wit), L.extract(wit, inv), L.extract(wit, wit)
    for tag, wv in (("omega0", 0), ("omega_general", w)):
        S = sp.simplify((Lii - Liw * Lww.inv() * Lwi).subs(w, wv))
        off = [(LABELS[inv[i]], LABELS[inv[j]], str(S[i, j])) for i in range(8) for j in range(8) if i != j and sp.simplify(S[i, j]) != 0]
        out[f"schur_{tag}"] = {"diag": {LABELS[inv[i]]: str(sp.factor(S[i, i])) for i in range(8)}, "nonzero_offdiag": off}
    # Is the Schur rate the decay rate? exact eigenvalues of the IX block vs Schur
    blk = L.extract([LABELS.index("IX"), LABELS.index("XY")], [LABELS.index("IX"), LABELS.index("XY")]).subs(w, 0)
    lam = sp.symbols("lam")
    cp = sp.factor((blk - lam * sp.eye(2)).det())
    roots = sp.solve(cp, lam)
    out["IX_block"] = {"matrix": str(blk), "charpoly": str(cp), "eigs": [str(r) for r in roots]}
    schurIX = -(2 * gt + 2 * g**2 / gCM)
    slow = max(roots, key=lambda r: sp.N(r.subs({g: 1, g1: 1, gt: sp.Rational(1, 10), N: 10})))
    c2_gt = sp.simplify(sp.series(sp.simplify(slow - schurIX), g, 0, 6).removeO().coeff(g, 2))
    out["IX_slow_eig_minus_schur_series_in_g"] = str(sp.series(sp.simplify(slow - schurIX), g, 0, 6))
    # EP conditions: discriminant of each 2x2 block
    out["IX_disc"] = str(sp.factor(sp.discriminant(cp, lam)))
    # Jordan ranks at the stated EP points
    def ranks(Lnum):
        ev = Lnum.eigenvals()
        res = {}
        for e, mult in ev.items():
            A = Lnum - e * sp.eye(16)
            r1, r2 = A.rank(), (A * A).rank()
            if r2 < r1 or mult > 1:
                res[str(e)] = {"alg_mult": int(mult), "rank1": int(r1), "rank2": int(r2)}
        return res
    sub_deg = {N: 4, g: 2, g1: sp.Rational(1, 4), gt: 0, w: 0}   # gCM = 4 = 2g
    sub_split = {N: sp.sqrt(5), g: 2, g1: 1, gt: 1, w: 0}         # gCM = 5, gCM - gt = 4 = 2g
    out["EP_degenerate"] = ranks(L.subs(sub_deg))
    out["EP_split"] = ranks(L.subs(sub_split))
    # KMS / modular statement: rho in V_inv commutes with Z(x)I, so D[Z(x)I] commutes with A -> rho A rho^-1
    r0 = sp.Matrix([[sp.Rational(3, 5), sp.Rational(1, 5)], [sp.Rational(1, 5), sp.Rational(2, 5)]])
    r1 = sp.Matrix([[sp.Rational(1, 2), sp.I / 5], [-sp.I / 5, sp.Rational(1, 2)]])
    rho = sp.diag(sp.Rational(2, 5) * r0, sp.Rational(3, 5) * r1)
    ZI = BASIS["ZI"]
    comm = [sp.simplify(ZI * rho * A * rho.inv() * ZI - rho * ZI * A * ZI * rho.inv()) for A in BASIS.values()]
    out["modular_commutes_with_D_CM"] = all(c == sp.zeros(4, 4) for c in comm)
    out["rho_commutes_with_ZI"] = (ZI * rho - rho * ZI) == sp.zeros(4, 4)
    check(out["real_matrix"], "the generator is not real in the Pauli basis")
    d0 = out["schur_omega0"]["diag"]
    want = {"II": "0", "IZ": "0", "ZX": "-2*gammatid", "ZY": "-2*gammatid",
            "IX": "-2*(N**2*gamma1*gammatid + g**2)/(N**2*gamma1)", "IY": "-2*(N**2*gamma1*gammatid + g**2)/(N**2*gamma1)",
            "ZI": "-2*g**2/(N**2*gamma1 + gammatid)", "ZZ": "-2*g**2/(N**2*gamma1 + gammatid)"}
    check(d0 == want, "the eight Schur diagonals at omega = 0 differ from the report")
    check(out["schur_omega0"]["nonzero_offdiag"] == [], "the omega = 0 Schur complement is not diagonal")
    check(len(out["schur_omega_general"]["nonzero_offdiag"]) == 4, "at omega != 0 the off-diagonal pattern is not the four IX-IY and ZX-ZY entries")
    check(out["IX_block"]["matrix"] == "Matrix([[-2*gammatid, -2*g], [2*g, -2*N**2*gamma1]])", "the IX block differs")
    # the Schur rate is not the exact slow rate: the g^2 coefficient differs when gamma_tid is not 0
    check(sp.simplify(c2_gt.subs({N: 10, g1: 1, gt: sp.Rational(1, 10)})) != 0, "g^2 coefficient is zero at gamma_tid = 1/10")
    check(sp.simplify(c2_gt.subs({N: 10, g1: 1, gt: 0})) == 0, "g^2 coefficient is not zero at gamma_tid = 0")
    ep_deg, ep_split = out["EP_degenerate"], out["EP_split"]
    check(ep_deg.get("-4") == {"alg_mult": 8, "rank1": 12, "rank2": 8}, "degenerate exceptional point is not Jordan ranks (12, 8)")
    check(ep_split.get("-6") == {"alg_mult": 4, "rank1": 14, "rank2": 12}, "split exceptional point is not Jordan ranks (14, 12)")
    check(out["modular_commutes_with_D_CM"] and out["rho_commutes_with_ZI"], "the modular statement fails")
    if "--verbose" in sys.argv:
        print(json.dumps(out, indent=1))
    if FAILS:
        print("RESULT %s: FAIL %d of %d checks: %s" % (NAME, len(FAILS), COUNT[0], "; ".join(FAILS[:4])))
        sys.exit(1)
    print("RESULT %s: PASS %d of %d checks; eight Schur diagonals match; Jordan ranks (12,8) and (14,12); "
          "slow rate differs from the s=0 Schur rate at O(g^2) when gamma_tid is not 0" % (NAME, COUNT[0], COUNT[0]))


if __name__ == "__main__":
    main()
