#!/usr/bin/env python3
"""Lemma B step and strict opening on the certified arcs (advocate check).

First, the literal step "I + A has positive symmetric part implies det(I + A) > 1" is
false as written: M = I/2 has positive definite symmetric part and det 1/8. Second, the
repaired step holds on the actual arcs, in exact rational LDL^T: A has symmetric part at
least (lambda_0 tau / 2) I, (I+A)^T (I+A) exceeds (1 + lambda_0 tau / 2)^2 I, and
det(I+A) > 1 for BW16 at tau = 1/4000 and Leech at tau = 1e-10. Third, at tau = 1/4000 on
the BW16 arc: the 960 motif contacts and the 32 bar contacts stay at squared distance
exactly 2, and all 137,248 other inter-cell contacts are strictly above 2.
The target's verifier is read as data only (its code is never run).
Backs: AUDIT-020R, VERDICTS.md section 3 rows "020R summary phrases" (all non-bar
contacts strictly open) and "020R proof section 3" (use the symmetric part of A).
Needs: Python 3, numpy, a clone of the target at the head of draft PR 106
(first argument, or environment variable INCENTRE_LATTICES_PR106). Uses adv_lattice.py.
Run: python3 -I -B adv_arc.py /path/to/incentre-lattices
Time: about 2 minutes. Only the fixed-seed lookup hash of adv_lattice.py (seed 12345) is
random, and every hit is rechecked exactly. Writes no files.
"""
import hashlib
import json
import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import adv_lattice as rl  # noqa: E402
from target import need  # noqa: E402


def ldl_pd(M):
    n = len(M)
    A = [row[:] for row in M]
    for k in range(n):
        if A[k][k] <= 0:
            return False
        for i in range(k + 1, n):
            f = A[i][k] / A[k][k]
            for j in range(k, n):
                A[i][j] -= f * A[k][j]
    return True


def det(M):
    _, d = rl.frac_inverse(M)
    return d


def mm(A, B):
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(r, c)) for c in Bt] for r in A]


def cayley_L(Ck, k, X, tau):
    n = len(Ck)
    C = [[Fr(Ck[i][j], k) for j in range(n)] for i in range(n)]
    L = [[C[i][j] + (2 if i == j else 0) for j in range(n)] for i in range(n)]
    V = mm(L, X)
    Lt = []
    for i in range(n):
        v2 = sum(x * x for x in V[i])
        den = 4 + v2 * tau * tau / 2
        u = [((4 - v2 * tau * tau / 2) * C[i][j] + 4 * tau * V[i][j]) / den for j in range(n)]
        need(sum(x * x for x in u) == 2, "bar length on arc")
        Lt.append([u[j] + (2 if i == j else 0) for j in range(n)])
    return L, Lt


def main():
    T = rl.load_tables()
    out = {}
    # F3 literal counterexample: M = I/2 has positive definite symmetric part, det(M) = 2^-n < 1
    M = [[Fr(1, 2) if i == j else Fr(0) for j in range(3)] for i in range(3)]
    out["F3_literal_counterexample_I_over_2"] = {"sym_part_pd": ldl_pd(M), "det": str(det(M))}
    # rotation-like: A with A_sym = 0 but I+A has PD symmetric part and det > 1 (not a contradiction, just illustration)
    cases = {}
    F16 = rl.Framework(16, 2, T["C2_16_WITNESS"])
    I16 = [[Fr(int(i == j)) for j in range(16)] for i in range(16)]
    X16, _, _ = rl.project_bar(F16.Ck, 2, I16)
    F24 = rl.Framework(24, 4, T["U24_WITNESS"])
    X24, _, _ = rl.project_bar(F24.Ck, 4, [[Fr(T["X0_24_INT_256"][i][j], 256) for j in range(24)] for i in range(24)])
    for name, F, X, k, tau in (("BW16", F16, X16, 2, Fr(1, 4000)), ("Leech", F24, X24, 4, Fr(1, 10 ** 10))):
        n = F.n
        L, Lt = cayley_L(F.Ck, k, X, tau)
        Linv, dL = rl.frac_inverse(L)
        IA = mm(Lt, Linv)  # row convention: L(tau) = L (I + A)?  team: L(tau) = L + tau V + R, A = tau X + L^-1 R
        IA = mm(Linv, Lt)  # I + A with L(tau) = L (I + A)
        A = [[IA[i][j] - (1 if i == j else 0) for j in range(n)] for i in range(n)]
        Asym = [[(A[i][j] + A[j][i]) / 2 for j in range(n)] for i in range(n)]
        lam0 = Fr(1, 5)
        shift = [[Asym[i][j] - (lam0 * tau / 2 if i == j else 0) for j in range(n)] for i in range(n)]
        G = mm([list(r) for r in zip(*IA)], IA)
        s2 = (1 + lam0 * tau / 2) ** 2
        Gs = [[G[i][j] - (s2 if i == j else 0) for j in range(n)] for i in range(n)]
        cases[name] = {
            "A_sym_minus_lam0_tau_over_2_PD": ldl_pd(shift),
            "sigma_min_sq_minus_(1+lam0tau/2)^2_PD": ldl_pd(Gs),
            "det_ratio_gt_1": det(IA) > 1,
            "det_ratio_minus_1_float": float(det(IA) - 1),
        }
    out["F3_repaired_steps_on_arcs"] = cases
    # F2 on BW16 at tau*
    F16.setup_cosets()
    W, _ = rl.bw16_min_vectors(F16)
    L, Lt = cayley_L(F16.Ck, 2, X16, Fr(1, 4000))
    Linv, _ = rl.frac_inverse(L)
    Ltk = [[x for x in row] for row in Lt]
    cw = (W @ F16.adj) % F16.mod
    stats = {"motif_contacts_at_sqrt2": 0, "bar_contacts_at_sqrt2": 0, "other_intercell_min_d2_minus_2": None,
             "other_intercell_count": 0, "other_intercell_not_strict": 0}
    import math
    Lk2 = [[2 * x for x in row] for row in L]
    Linv2, D2 = rl.frac_inverse(Lk2)
    adjfull = [[int(Linv2[i][j] * D2) for j in range(16)] for i in range(16)]
    D2 = int(D2)
    dent = 1
    for row in Lt:
        for v in row:
            dent = dent * v.denominator // math.gcd(dent, v.denominator)
    Ltn = np.array([[int(v * dent) for v in row] for row in Lt], dtype=object)
    adjo = np.array(adjfull, dtype=object)
    Pk = np.array(F16.P, dtype=np.int64)
    allp = []
    for pi in range(32):
        pk = 2 * Pk[pi]
        cl = (cw + pk @ F16.adj) % F16.mod
        h = F16.hash(cl)
        qidx = np.array([F16.hash_to_p[int(v)] for v in h])
        X2 = W + pk - 2 * Pk[qidx]            # 2x
        intra = ~X2.any(axis=1)
        stats["motif_contacts_at_sqrt2"] += int(intra.sum())
        rows = np.nonzero(~intra)[0]
        mnum = X2[rows].astype(object).dot(adjo)
        need(all(v % D2 == 0 for v in mnum.ravel()), "m not integral")
        m = mnum // D2
        pos = m.dot(Ltn) + ((Pk[qidx[rows]] - Pk[pi]).astype(object) * dent)
        d2n = (pos * pos).sum(axis=1)          # = d2 * dent^2
        i = pi // 2
        sgn = 1 if pi % 2 == 0 else -1
        for r_local, r in enumerate(rows):
            qi = int(qidx[r])
            mr = m[r_local]
            is_bar = (qi // 2 == i and qi != pi and int(mr[i]) == sgn and sum(1 for v in mr if v != 0) == 1)
            val = d2n[r_local]
            if is_bar:
                need(val == 2 * dent * dent, "bar distance changed")
                stats["bar_contacts_at_sqrt2"] += 1
            else:
                stats["other_intercell_count"] += 1
                if val <= 2 * dent * dent:
                    stats["other_intercell_not_strict"] += 1
                g = Fr(val - 2 * dent * dent, dent * dent)
                if stats["other_intercell_min_d2_minus_2"] is None or g < stats["other_intercell_min_d2_minus_2"]:
                    stats["other_intercell_min_d2_minus_2"] = g
    stats["other_intercell_min_d2_minus_2"] = float(stats["other_intercell_min_d2_minus_2"])
    out["F2_BW16_tau_1_over_4000"] = stats
    txt = json.dumps(out, sort_keys=True, indent=1)
    print(txt)
    print("SHA256", hashlib.sha256(txt.encode()).hexdigest())
    problems = []
    lit = out["F3_literal_counterexample_I_over_2"]
    if not (lit["sym_part_pd"] and lit["det"] == "1/8"):
        problems.append("literal counterexample")
    for name, c in out["F3_repaired_steps_on_arcs"].items():
        if not (c["A_sym_minus_lam0_tau_over_2_PD"] and c["sigma_min_sq_minus_(1+lam0tau/2)^2_PD"]
                and c["det_ratio_gt_1"]):
            problems.append("repaired step on " + name)
    st = out["F2_BW16_tau_1_over_4000"]
    if not (st["motif_contacts_at_sqrt2"] == 960 and st["bar_contacts_at_sqrt2"] == 32
            and st["other_intercell_count"] == 137248 and st["other_intercell_not_strict"] == 0
            and st["other_intercell_min_d2_minus_2"] > 0):
        problems.append("strict opening on BW16 arc")
    if problems:
        raise SystemExit("CHECK FAILED: " + "; ".join(problems))
    print("RESULT leech_sheaf/adv_arc: PASS literal det step fails (I/2 has det 1/8), repaired step holds on BW16 "
          "and Leech arcs; BW16 at tau 1/4000: 960 motif and 32 bar contacts at exactly 2, "
          "137248 others strictly above (min excess %.3g)" % st["other_intercell_min_d2_minus_2"])


if __name__ == "__main__":
    main()
