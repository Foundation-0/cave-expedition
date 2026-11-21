#!/usr/bin/env python3
"""
Audit 005: Independent Adversarial Audit of Instrument 5 (`portal78_homotopy_bregman_bridge.py`, #39):
  - Independent verification of Portal 7 Doob similarity & accidental single-q lumpability
    (plus checking unnormalized Cole-Hopf K_q vs row-normalized Boltzmann Markov chain P_q!)
  - Independent verification of Portal 8 Cubic-Bregman Global Pythagoras on 50 non-block-constant
    random rational curved points + exact comparison of FINITE curved anchor step vs TANGENT
    Fisher-Rao phase boundary (testing curvature-induced boundary shift!).

Run under all three R4 modes:
  python3 -B check_005_portal78.py
  python3 -O -B check_005_portal78.py
  python3 -B -W error check_005_portal78.py
"""
from __future__ import annotations
import os
from pathlib import Path

from fractions import Fraction
import json
import random
import sys

EXPEDITION_ROOT = Path(os.environ.get("EXPEDITION_ROOT", Path(__file__).resolve().parents[2]))
CHECKS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXPEDITION_ROOT / "synthesis"))
import portal78_homotopy_bregman_bridge as p78


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(f"CHECK FAILED: {msg}")


def audit_portal7() -> dict:
    # 1. Independently check K_q' == D_h^{-1} K_q D_h algebraic identity on random integer-cost directed graph
    rng = random.Random(2026)
    n = 6
    edges = []
    for u in range(n):
        for v in range(n):
            if rng.random() < 0.45:
                edges.append((u, v, Fraction(rng.randint(1, 4))))
    h = [Fraction(rng.randint(0, 3)) for _ in range(n)]
    # Shift costs up if needed so c_red >= 0
    min_cr = min(w + h[v] - h[u] for u, v, w in edges)
    if min_cr < 0:
        edges = [(u, v, w - min_cr) for u, v, w in edges]
    red = [(u, v, w + h[v] - h[u]) for u, v, w in edges]
    for q in (Fraction(1, 2), Fraction(1, 3), Fraction(1, 5)):
        K1 = p78.build_cole_hopf_matrix(n, red, q)
        K2 = p78.doob_similarity_transform(p78.build_cole_hopf_matrix(n, edges, q), h, q)
        require(K1 == K2, f"independent Doob identity failed at q={q}")

    # 2. Check subtle distinction on acc_edges: unnormalized Cole-Hopf K_q vs row-normalized Boltzmann P_q!
    # In p78's acc_edges, vertices 1 & 2 ONLY go to fiber {0,3}, so row-normalized P_q is trivially lumpable for ALL q!
    acc_edges = [(0, 0, Fraction(1)), (3, 3, Fraction(1)), (1, 0, Fraction(1)), (2, 0, Fraction(2)), (2, 3, Fraction(2))]
    acc_pi = [0, 1, 1, 0]
    row_norm_defects_p78_acc = {}
    for q in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)):
        Kq = p78.build_cole_hopf_matrix(4, acc_edges, q)
        Pq = [[v / sum(row, Fraction(0)) for v in row] for row in Kq]
        row_norm_defects_p78_acc[str(q)] = str(p78.linear_markov_commutation_defect_sq(Pq, acc_pi))
    require(all(v == "0" for v in row_norm_defects_p78_acc.values()), "expected row-normalized p78 acc_edges to be lumpable at all q")

    # Construct a 5-state witness that has accidental single-q lumpability at q=1/2 EVEN AFTER row normalization!
    # Fibers: Y0={0,3}, X={1,2}, Y2={4}.
    # 1->0 (cost 1), 1->4 (cost 2) => P(1->Y0) = q/(q+q^2) = 1/(1+q)
    # 2->0 (cost 2), 2->3 (cost 2), 2->4 (cost 2) => P(2->Y0) = 2q^2/(3q^2) = 2/3
    # Equal iff 1/(1+q) == 2/3 <=> q == 1/2!
    rn_edges = [
        (0, 0, Fraction(1)), (3, 3, Fraction(1)), (4, 4, Fraction(1)),
        (1, 0, Fraction(1)), (1, 4, Fraction(2)),
        (2, 0, Fraction(2)), (2, 3, Fraction(2)), (2, 4, Fraction(2)),
    ]
    rn_pi = [0, 1, 1, 0, 2]
    rn_sweep = {}
    for q in (Fraction(1, 4), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)):
        Kq = p78.build_cole_hopf_matrix(5, rn_edges, q)
        Pq = [[v / sum(row, Fraction(0)) for v in row] for row in Kq]
        d2 = p78.linear_markov_commutation_defect_sq(Pq, rn_pi)
        rn_sweep[str(q)] = str(d2)
        require((q == Fraction(1, 2)) == (d2 == 0), f"row-normalized accidental witness failed at q={q}")

    return {
        "random_graph_doob_identity_exact": True,
        "p78_acc_edges_row_normalized_defects_all_zero": row_norm_defects_p78_acc,
        "row_normalized_boltzmann_accidental_q_half_witness": rn_sweep,
    }


def audit_portal8() -> dict:
    # 1. Verify general cubic Bregman Pythagoras on 50 NON-BLOCK-CONSTANT random curved rational instances!
    # Pick any positive q_star, q_adapt in Q_{>0}^5, define Phi = [grad F(q_star), grad F(q_adapt)] (so BOTH
    # q_star and q_adapt lie on E_Phi with non-orthogonal curved columns!), and pick arbitrary r_star in ker(Phi^T)
    # small enough that p = q_star + r_star > 0!
    rng = random.Random(2026)
    checked = 0
    for _ in range(60):
        qs = [Fraction(rng.randint(2, 5)) for _ in range(5)]
        qa = [Fraction(rng.randint(2, 5)) for _ in range(5)]
        if qs == qa:
            continue
        g_s = [x * x for x in qs]
        g_a = [x * x for x in qa]
        # Find an exact rational r in ker([g_s, g_a]^T) by solving 2 equations in 5 unknowns (fix r[2..4])
        # det of first 2 cols: g_s[0]*g_a[1] - g_s[1]*g_a[0]
        det = g_s[0] * g_a[1] - g_s[1] * g_a[0]
        if det == 0:
            continue
        r2, r3, r4 = Fraction(rng.randint(-1, 1), 4), Fraction(rng.randint(-1, 1), 4), Fraction(rng.randint(-1, 1), 4)
        rhs0 = -(g_s[2] * r2 + g_s[3] * r3 + g_s[4] * r4)
        rhs1 = -(g_a[2] * r2 + g_a[3] * r3 + g_a[4] * r4)
        r0 = (rhs0 * g_a[1] - rhs1 * g_s[1]) / det
        r1 = (g_s[0] * rhs1 - g_a[0] * rhs0) / det
        r = [r0, r1, r2, r3, r4]
        # Rescale r so p = qs + r > 0 strictly
        scale = Fraction(1)
        while any(qs[i] + scale * r[i] <= 0 for i in range(5)):
            scale /= 2
        r = [scale * x for x in r]
        p = [qs[i] + r[i] for i in range(5)]
        require(sum(g_s[i] * r[i] for i in range(5)) == 0 and sum(g_a[i] * r[i] for i in range(5)) == 0, "orth failed")
        d_pa = p78.cubic_bregman_div(p, qa)
        d_ps = p78.cubic_bregman_div(p, qs)
        d_sa = p78.cubic_bregman_div(qs, qa)
        require(d_pa == d_ps + d_sa and d_sa > 0, "general cubic Bregman Pythagoras failed!")
        checked += 1

    # 2. Check curvature-induced shift between FINITE curved anchor step vs TANGENT Fisher-Rao boundary!
    # In p78's own model: Phi = [[1,1],[1,1],[1,-1],[1,-1]], q* = [2,2,3,3], p = [3,1,4,2], r* = [1,-1,1,-1].
    # Anchor a1_f = [1,0,1,0], e1_f = 2.
    # For any q(a,b) = [a,a,b,b] in E_Phi silencing a1_f: <a1_f, p - q> = (3-a) + (4-b) = 0 => a + b = 7!
    # Exact finite minimizer of D_F(q* || q(a, 7-a)) over a in (0, 7):
    # D_F(q* || [a,a,7-a,7-a]) = (2/3)[(2-a)^2(2+2a) + (3-(7-a))^2(3+2(7-a))]
    # Wait: test a concrete exact finite point on E_Phi silencing a1_f, e.g. a=3, b=4 -> q_fin = [3,3,4,4] (a+b=7!),
    # vs tangent shift q* + dq_G = [2+6/5, 2+6/5, 3+4/5, 3+4/5] = [16/5, 16/5, 19/5, 19/5] (Notice 16/5+19/5 = 7!).
    # Wait: on this particular E_Phi = {[a,a,b,b]}, q(a,b) IS affine in (a,b) even though eta = [a^2,a^2,b^2,b^2] is curved!
    # What if Phi has NON-block-constant columns so E_Phi = {q : q^{odot 2} = Phi theta} is genuinely curved in q-space?!
    # Test: Phi_c = [[1],[4]]? Wait: for 1D theta, q = sqrt(theta) * [1, 2] is still a ray!
    # Take 2D theta on Q^3: Phi_c = [[1, 0], [0, 1], [1, 1]] => q_3 = sqrt(q_1^2 + q_2^2) (GENUINELY CURVED CONE in q-space!).
    # Exact Pythagorean triple points on E_{Phi_c}:
    #   q* = [3, 4, 5]  (3^2 + 4^2 = 5^2 = 25 -> theta* = [9, 16])!
    #   q_adapt = [5, 12, 13] (5^2 + 12^2 = 13^2 = 169 -> theta_adapt = [25, 144])!
    # Check Latch optimality Phi_c^T r* = 0: r* = [1, 1, -1] => 1*1 + 0 + 1*(-1) = 0, 0 + 1*1 + 1*(-1) = 0!
    # So p = q* + r* = [4, 5, 4] > 0 strictly!
    q_s3 = [Fraction(3), Fraction(4), Fraction(5)]
    q_a3 = [Fraction(5), Fraction(12), Fraction(13)]
    r_s3 = [Fraction(1), Fraction(1), Fraction(-1)]
    p3 = [q_s3[i] + r_s3[i] for i in range(3)]  # [4, 5, 4]
    # Verify exact global Bregman Pythagoras on genuinely curved cone q_3 = sqrt(q_1^2 + q_2^2)!
    d3_pa = p78.cubic_bregman_div(p3, q_a3)
    d3_ps = p78.cubic_bregman_div(p3, q_s3)
    d3_sa = p78.cubic_bregman_div(q_s3, q_a3)
    require(d3_pa == d3_ps + d3_sa and d3_sa > 0, "curved cone Bregman Pythagoras failed!")

    # Now pick anchor a1 = [1, 0, 0]? No, pick a1 silenced by q_a3: <a1, p3 - q_a3> = 0.
    # p3 - q_a3 = [-1, -7, -9]. Pick a1 = [-7, 1, 0] -> <a1, p3 - q_a3> = 7 - 7 = 0!
    # Check e1 = <a1, r_s3> = -7 + 1 = -6 != 0!
    # Compare TANGENT Fisher-Rao prediction vs FINITE curved step q_a3 on fresh anchor a2 = [0, 0, 1] (e2 = -1):
    # Tangent space at q*=[3,4,5]: H_F = diag(6, 8, 10), J = H_F^{-1} Phi_c = [[1/6, 0], [0, 1/8], [1/10, 1/10]]
    Phi_c = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)], [Fraction(1), Fraction(1)]]
    H_inv = [Fraction(1, 6), Fraction(1, 8), Fraction(1, 10)]
    J3 = [[H_inv[r] * Phi_c[r][c] for c in range(2)] for r in range(3)]
    G3 = p78.mat_mul(p78.mat_t(Phi_c), J3)
    M3 = p78.mat_mul(p78.mat_mul(J3, p78.mat_inv_exact(G3)), p78.mat_t(J3))
    a1_c = [Fraction(-7), Fraction(1), Fraction(0)]
    e1_c = p78.dot(a1_c, r_s3)  # -6
    p1_c = p78.mat_vec(M3, a1_c)
    denom_c = p78.dot(a1_c, p1_c)
    dq_c = p78.vec_scale(e1_c / denom_c, p1_c)
    # Test fresh anchor a2_c = [0, 0, 1]: e2 = -1
    a2_c = [Fraction(0), Fraction(0), Fraction(1)]
    e2_c = p78.dot(a2_c, r_s3)
    tangent_ratio = (p78.dot(a2_c, p1_c) / denom_c) / (e2_c / e1_c)
    tangent_fires = Fraction(0) < tangent_ratio < Fraction(2)
    finite_err_before_sq = e2_c * e2_c
    finite_err_after_sq = p78.dot(a2_c, p78.vec_sub(p3, q_a3)) ** 2
    finite_fires = finite_err_after_sq < finite_err_before_sq
    # Also check tangent vs finite discrepancy in predicted shift on a2_c
    tangent_err_after_sq = (e2_c - p78.dot(a2_c, dq_c)) ** 2

    return {
        "random_nonblock_cubic_bregman_pythagoras_verified": checked,
        "genuinely_curved_cone_pythagorean_triple_exact": {
            "q_star": [3, 4, 5],
            "q_adapt": [5, 12, 13],
            "D_p_qstar": str(d3_ps),
            "D_qstar_qadapt": str(d3_sa),
            "D_p_qadapt": str(d3_pa),
            "exact_pythagoras": d3_pa == d3_ps + d3_sa,
            "tangent_fisher_ratio_on_a2": str(tangent_ratio),
            "tangent_after_sq_vs_finite_after_sq": [str(tangent_err_after_sq), str(finite_err_after_sq)],
            "note": "Global Bregman Pythagoras is EXACT at finite step even on genuinely curved q_3=sqrt(q_1^2+q_2^2), whereas Fisher-Rao 0<ratio<2 is a LOCAL tangent approximation (differs from finite curved step!). Note p78's [a,a,b,b] example is affine in q-space so tangent=finite there.",
        },
    }


def main() -> None:
    print(json.dumps({"portal7_audit": audit_portal7(), "portal8_audit": audit_portal8()}, indent=2))


if __name__ == "__main__":
    main()
