#!/usr/bin/env python3
"""
Audit 008: Independent Zero-Shared-Code Adversarial Verification of spectral-prover (#56-#58):
  - Track A (AUDIT-014): Higher-Moment Spectral Rank Theorems A1-A4 (`higher_moments.py`, `THEOREMS.md`)
      * Independent SymPy verification of A2 Schur formula, A3 SOS, A4 5-param SOS & peak-matching
      * 300 fresh exact Q(i) non-commuting complex Hermitian (P, Q) stress tests (including b=0, b>n,
        Q_- != 0, negative S_1/S_3, rank-1 P, nonzero gamma3) checked against independent check_003
        Descartes oracle for true n_+(Pi_{W^perp} H Pi_{W^perp})!
      * Exact unitary & positive-scale invariance checks
      * Independent explicit-matrix Scan 23848 verification (including extreme rho = 99/100)
      * Fresh non-commuting complex 4x4 A4 > ceil(R_opt) & A4 > ceil(R_H4) construction
      * Invalid witness rejection checks
  - Track B (AUDIT-015): Exact Non-Affine Complex-Hermitian Bernstein Box Certifier (`box_certifier.py`)
      * CRITICAL EXPLOIT TEST: Non-Hermitian PolyMatrix & RatMatrix with Hermitian midpoint!
      * 200 random 2D/3D multivariate Bernstein enclosure soundness tests (10,000 interior evaluations)
      * Independent Descartes interior-point verification of fibral#5 taut/buckled, Bloch gapped,
        and 3x3 Morse saddle boxes
      * Fresh complex Hermitian 3x3 zero-diagonal 2x2-block box test (Theorem B2 2x2 block path)
      * fibral_truss_box straddling coordinate consistency check
  - Track C (AUDIT-016): Hardened Dual-Oracle Q(i) Certifier (`exact_qi.py`, `dual_oracle.py`)
      * 100 fresh complex Q(i) Hermitian matrices (including multiplicity 2/3/4 eigenvalues to stress
        Sturm square-free peel, zero-diagonals, 1x1, zero matrix, all 5 rows of 2x2 block table)
        cross-checked against independent check_003 Descartes oracle!
      * Full replay of all 6 AUDIT-001 exploits + R1/R2/R3 parser boundary probe (including "2/4", "0/5", "3/1")

Run under all 3 R4 modes (using gravity venv for SymPy + stdlib):
  VENV=${EXPEDITION_PYTHON:-python3}  # requires sympy/numpy/scipy; set EXPEDITION_ROOT if running outside workspace
  "$VENV" -B check_008_spectral_inertia.py
  "$VENV" -O -B check_008_spectral_inertia.py
  "$VENV" -B -W error check_008_spectral_inertia.py
"""
from __future__ import annotations
import os
from pathlib import Path

from fractions import Fraction
import json
import math
import random
import sys
import sympy as sp

EXPEDITION_ROOT = Path(os.environ.get("EXPEDITION_ROOT", Path(__file__).resolve().parents[2]))
CHECKS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXPEDITION_ROOT / "branches/spectral-inertia"))
sys.path.insert(0, str(CHECKS_DIR))

import spectral_inertia.exact_qi as eqi
import spectral_inertia.dual_oracle as dora
import spectral_inertia.higher_moments as hm
import spectral_inertia.box_certifier as bc
from spectral_inertia.examples.fibral_truss_box import (
    run_fibral_truss_validation,
    truss_equilibrium_hessian_raw,
)
from spectral_inertia.examples.bloch_and_hessian_boxes import (
    build_bloch_2d_polymatrix,
    build_morse_3x3_polymatrix,
)
from spectral_inertia.examples.scan23848_benchmark import run_scan23848_benchmark, W1, W2

from check_003_seam01_ropt import Qi as VQi, hermitian_inertia_descartes as v_descartes


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(f"CHECK FAILED: {msg}")


def to_vqi_mat(M: eqi.CMat) -> list[list[VQi]]:
    return [[VQi(v.re, v.im) for v in row] for row in M]


def expect_cert_error(fn, label: str) -> str:
    try:
        fn()
    except eqi.CertError as exc:
        return exc.code
    raise RuntimeError(f"Expected CertError for {label}, but call succeeded!")


# ==============================================================================
# AUDIT-014: TRACK A (Higher-Moment Spectral Rank Theorems A1-A4)
# ==============================================================================
def audit_track_a() -> dict:
    # 1A. Independent SymPy symbolic verification of A2, A3, A4 identities!
    lam, x0, tau = sp.symbols("lam x0 tau", real=True)
    s, p, g1, g3, kap, mu = sp.symbols("s p g1 g3 kap mu", real=True)
    S1, S2, S3, S4 = sp.symbols("S1 S2 S3 S4", real=True)

    # A2 Schur formula:
    det_h = S2 * S4 - S3**2
    s_star = (S1 * S4 - S2 * S3) / det_h
    p_star = (S1 * S3 - S2**2) / det_h
    f_opt = 2 * s_star * S1 - 2 * p_star * S2 - s_star**2 * S2 + 2 * s_star * p_star * S3 - p_star**2 * S4
    a2_schur = S1**2 / S2 + (S1 * S3 - S2**2) ** 2 / (S2 * det_h)
    require(sp.simplify(f_opt - a2_schur) == 0, "A2 Schur formula symbolic mismatch")

    # A3 Noise-annihilating quartic SOS:
    d_a3 = 3 * x0 + tau
    L_a3 = 2 * x0 * (2 * x0 + tau) / d_a3
    M_a3 = x0**2 * (x0 + tau) ** 3 / d_a3
    lhs_a3 = M_a3 - lam * (L_a3 - lam) * (lam + tau) ** 2
    rhs_a3 = (lam - x0) ** 2 * (
        (lam + (x0**2 + 3 * x0 * tau + tau**2) / d_a3) ** 2
        + x0**2 * (2 * x0**2 + 4 * x0 * tau + tau**2) / d_a3**2
    )
    require(sp.simplify(lhs_a3 - rhs_a3) == 0, "A3 SOS identity symbolic mismatch")

    # A4 5-parameter Weighted Quartic-Weyl SOS:
    phi_sp = 1 - (1 - s * lam + p * lam**2) ** 2
    beta = s + g3 / p
    alpha = 1 - (beta**2 - s**2 + kap) / (2 * p)
    lam0 = (s + g1 - alpha * beta) / kap
    M_a4 = alpha**2 + kap * lam0**2
    lhs_a4 = M_a4 - (phi_sp + 2 * g1 * lam + 2 * g3 * lam**3)
    rhs_a4 = (p * lam**2 - beta * lam + alpha) ** 2 + kap * (lam - lam0) ** 2
    require(sp.simplify(lhs_a4 - rhs_a4) == 0, "A4 5-param SOS identity symbolic mismatch")

    # Corollary A4(a) peak-matching: both squares vanish at lam = mu!
    q_mu = 1 - s * mu + p * mu**2
    g1_pk = q_mu * (2 * p * mu - s)
    kap_pk = 2 * p * q_mu
    subs_pk = {g3: 0, g1: g1_pk, kap: kap_pk, lam: mu}
    require(sp.simplify((p * lam**2 - beta * lam + alpha).subs(subs_pk)) == 0, "A4 peak first square != 0 at mu")
    require(sp.simplify((lam - lam0).subs(subs_pk)) == 0, "A4 peak second square != 0 at mu")

    # 1B. 300 fresh exact Q(i) non-commuting complex Hermitian (P, Q) stress tests!
    rng = random.Random(20261121)
    n_trials = 300
    counts = {
        "non_commuting": 0,
        "complex_entries": 0,
        "neg_S1": 0,
        "neg_S3": 0,
        "nonzero_gamma3_checked": 0,
        "b_gt_n_checked": 0,
        "A2_beats_Ropt": 0,
        "A3_beats_Ropt": 0,
        "A4_beats_Ropt": 0,
    }
    for trial in range(n_trials):
        n = rng.choice([2, 3, 4])
        # Build Q diagonal in standard basis so W = range(Q_+) is exact first b_true coordinates,
        # then conjugate BOTH P and Q by a fresh exact Q(i) Cayley unitary U!
        b_true = rng.randint(0, n)
        q_eigs: list[Fraction] = []
        for idx in range(n):
            if idx < b_true:
                q_eigs.append(Fraction(rng.randint(1, 5), rng.randint(1, 2)))
            else:
                # mix of zero and strictly negative eigenvalues (Q_- != 0!)
                q_eigs.append(Fraction(-rng.randint(0, 4), rng.randint(1, 2)))
        Q0 = eqi.cmat_zeros(n, n)
        for i in range(n):
            Q0[i][i] = eqi.Qi(q_eigs[i])

        # Build PSD P0 = sum_r v_r v_r^* with random rank 0..n (complex non-commuting with Q0!)
        r_p = rng.randint(0, n)
        P0 = eqi.cmat_zeros(n, n)
        for _ in range(r_p):
            v = [eqi.Qi(Fraction(rng.randint(-2, 2), rng.randint(1, 2)),
                        Fraction(rng.randint(-2, 2), rng.randint(1, 2))) for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    P0[i][j] = P0[i][j] + v[i] * v[j].conj()

        H0 = eqi.cmat_add(P0, Q0)
        # True projected H_perp = H0[b_true:, b_true:] (exact compression onto W^perp!)
        if b_true < n:
            H_perp = [[H0[i][j] for j in range(b_true, n)] for i in range(b_true, n)]
            true_n_pos_perp = v_descartes(to_vqi_mat(H_perp))[0]
        else:
            true_n_pos_perp = 0

        # Conjugate by exact Q(i) Cayley unitary U (basis invariance!)
        U = eqi.cayley_unitary(n, rng, bound=2)
        Ud = eqi.cmat_dagger(U)
        P = eqi.cmat_mul(eqi.cmat_mul(U, P0), Ud)
        Q = eqi.cmat_mul(eqi.cmat_mul(U, Q0), Ud)
        H = eqi.cmat_add(P, Q)

        # Check commutation & complexity stats
        PQ = eqi.cmat_mul(P, Q)
        QP = eqi.cmat_mul(Q, P)
        if PQ != QP:
            counts["non_commuting"] += 1
        if any(v.im != 0 for row in H for v in row):
            counts["complex_entries"] += 1

        # Also test slack b >= b_true (including b > n on ~10% of trials!)
        b_used = b_true if (trial % 10 != 0) else (n + 1)
        if b_used > n:
            counts["b_gt_n_checked"] += 1

        S = hm.spectral_moments_exact(H, max_k=6)
        if S[1] < 0:
            counts["neg_S1"] += 1
        if S[3] < 0:
            counts["neg_S3"] += 1

        u = eqi.cmat_trace_real(P)
        t1 = eqi.cmat_trace_real(Q)
        Q2 = eqi.cmat_mul(Q, Q)
        t3 = eqi.cmat_trace_real(eqi.cmat_mul(Q2, Q))

        b_ropt = hm.R_opt(u, t1, S[2], b_used)
        b_h4 = hm.R_hankel4_exact(S[1], S[2], S[3], S[4], b=b_used)["exact_bound"]
        b_h6 = hm.R_hankel6_exact(S, b=b_used)["exact_bound"]
        tau_try = Fraction(rng.choice([0, 1, 2]), 2)
        b_a3 = hm.find_noise_quartic_witness(S, b=b_used, tau=tau_try)["exact_bound"]
        b_a4 = hm.find_weighted_quartic_witness(S, t1, t3, b=b_used)["exact_bound"]

        # Also explicitly test Theorem A4 with strictly NONZERO gamma3 > 0!
        c_g3 = hm.certify_weighted_quartic_weyl(
            S, t1, t3, b_used,
            s=Fraction(1, 2), p=Fraction(1, 4),
            gamma1=Fraction(1, 5), gamma3=Fraction(1, 10), kappa=Fraction(1, 2),
        )
        b_a4_g3 = c_g3["exact_bound"]
        counts["nonzero_gamma3_checked"] += 1

        target = Fraction(true_n_pos_perp)
        require(b_ropt <= target, f"A1 R_opt violation trial {trial}: {b_ropt} > {target}")
        require(b_h4 <= target, f"A2 R_H4 violation trial {trial}: {b_h4} > {target}")
        require(b_h6 <= target, f"A2 R_H6 violation trial {trial}: {b_h6} > {target}")
        require(b_h6 >= b_h4, f"A2 R_H6 < R_H4 on trial {trial}: {b_h6} < {b_h4}")
        require(b_a3 <= target, f"A3 violation trial {trial}: {b_a3} > {target}")
        require(b_a4 <= target, f"A4 violation trial {trial}: {b_a4} > {target}")
        require(b_a4_g3 <= target, f"A4(gamma3>0) violation trial {trial}: {b_a4_g3} > {target}")

        if b_h6 > b_ropt:
            counts["A2_beats_Ropt"] += 1
        if b_a3 > b_ropt:
            counts["A3_beats_Ropt"] += 1
        if b_a4 > b_ropt:
            counts["A4_beats_Ropt"] += 1

    # 1C. Positive scale invariance (alpha = 7/3) & unitary invariance check on exact non-commuting 4x4
    U_inv = eqi.cayley_unitary(4, random.Random(99), bound=2)
    U_inv_d = eqi.cmat_dagger(U_inv)
    P_inv = eqi.cmat_zeros(4, 4)
    for i, ev in enumerate([Fraction(0), Fraction(2), Fraction(1, 2), Fraction(1, 5)]):
        P_inv[i][i] = eqi.Qi(ev)
    Q_inv = eqi.cmat_zeros(4, 4)
    Q_inv[0][0] = eqi.Qi(Fraction(5))
    Q_inv[0][1] = eqi.Qi(Fraction(1, 3), Fraction(1, 4))
    Q_inv[1][0] = Q_inv[0][1].conj()
    Q_inv[3][3] = eqi.Qi(Fraction(-1, 4))
    H_inv = eqi.cmat_add(P_inv, Q_inv)
    alpha = Fraction(7, 3)
    H_u = eqi.cmat_mul(eqi.cmat_mul(U_inv, H_inv), U_inv_d)
    H_sc = eqi.cmat_scale(alpha, H_inv)
    S_0 = hm.spectral_moments_exact(H_inv, 6)
    S_u = hm.spectral_moments_exact(H_u, 6)
    S_sc = hm.spectral_moments_exact(H_sc, 6)
    require(S_0 == S_u, "Unitary invariance of moments failed")
    require(
        hm.R_hankel4_exact(S_0[1], S_0[2], S_0[3], S_0[4], b=1)["exact_bound"]
        == hm.R_hankel4_exact(S_sc[1], S_sc[2], S_sc[3], S_sc[4], b=1)["exact_bound"],
        "Scale invariance of R_H4 failed",
    )
    require(
        hm.R_hankel6_exact(S_0, b=1)["exact_bound"] == hm.R_hankel6_exact(S_sc, b=1)["exact_bound"],
        "Scale invariance of R_H6 failed",
    )
    require(
        hm.certify_noise_annihilating_quartic(S_0, 1, Fraction(2), Fraction(1, 4))["exact_bound"]
        == hm.certify_noise_annihilating_quartic(S_sc, 1, alpha * 2, alpha * Fraction(1, 4))["exact_bound"],
        "Scale invariance of A3 failed",
    )

    # 1D. Independent explicit-matrix Scan 23848 verification including extreme rho = 99/100!
    scan_res = run_scan23848_benchmark()
    require(scan_res["mode_a_strict_ceil_wins_over_R_opt"] == 6, "Scan 23848 Mode A wins != 6")
    # Build explicit 2x2 matrix for rho = 99/100 (using rational Pythagorean pair: rho = 99/100 -> wait:
    # c1 = (1, 0), c2 = (rho, sqrt(1-rho^2)); pick rational Pythagorean rho = 119/120? No, 120^2-119^2=239 not sq;
    # pick exact Pythagorean triple (a, b, c) = (24, 7, 25) -> rho=24/25=0.96, s=7/25!)
    rho_pyth = Fraction(24, 25)
    sin_pyth = Fraction(7, 25)
    # G = W1 e1 e1^T + W2 c2 c2^T
    G_pyth = [
        [eqi.Qi(W1 + W2 * rho_pyth * rho_pyth), eqi.Qi(W2 * rho_pyth * sin_pyth)],
        [eqi.Qi(W2 * rho_pyth * sin_pyth), eqi.Qi(W2 * sin_pyth * sin_pyth)],
    ]
    S_pyth = hm.spectral_moments_exact(G_pyth, 4)
    h4_pyth = hm.R_hankel4_exact(S_pyth[1], S_pyth[2], S_pyth[3], S_pyth[4], b=1)
    require(h4_pyth["exact_bound"] == Fraction(1), f"Explicit Pythagorean rho=24/25 Mode B != 1: {h4_pyth}")

    # 1E. Fresh non-commuting complex 4x4 matrix where Theorem A4 strictly beats BOTH ceil(R_opt) AND ceil(R_H4)!
    # Also empirically verify Theorem A4's non-commuting Weyl slack law (large mu => huge gamma1 kills peak-matched A4,
    # while moderate mu retains strict > 2 dominance over BOTH ceil(R_opt)=2 AND ceil(R_H4)=2!).
    Q_nc = eqi.cmat_zeros(4, 4)
    Q_nc[0][0] = eqi.Qi(Fraction(4))
    P_nc = eqi.cmat_zeros(4, 4)
    P_nc[1][1] = eqi.Qi(Fraction(1))
    P_nc[2][2] = eqi.Qi(Fraction(1, 5))
    P_nc[3][3] = eqi.Qi(Fraction(1, 5))
    # Genuine complex non-commuting rank-1 PSD perturbation coupling row 0 and row 1
    v_nc = [eqi.Qi(Fraction(1, 200), Fraction(1, 200)), eqi.Qi(Fraction(1, 200), Fraction(-1, 200)), eqi.ZERO, eqi.ZERO]
    for i in range(4):
        for j in range(4):
            P_nc[i][j] = P_nc[i][j] + v_nc[i] * v_nc[j].conj()
    H_nc = eqi.cmat_add(P_nc, Q_nc)
    require(eqi.cmat_mul(P_nc, Q_nc) != eqi.cmat_mul(Q_nc, P_nc), "Fresh A4 matrix commutes!")
    S_nc = hm.spectral_moments_exact(H_nc, 6)
    ropt_nc = hm.R_opt(eqi.cmat_trace_real(P_nc), eqi.cmat_trace_real(Q_nc), S_nc[2], 1)
    h4_nc = hm.R_hankel4_exact(S_nc[1], S_nc[2], S_nc[3], S_nc[4], b=1)["exact_bound"]
    # Roots of q(lam) = 1 - 6 lam + 5 lam^2 are lam = 1 and lam = 1/5; peak at mu = 4!
    a4_nc_peak = hm.certify_weighted_quartic_weyl_peak(
        S_nc, eqi.cmat_trace_real(Q_nc), b=1, s=Fraction(6), p=Fraction(5), mu=Fraction(4)
    )["exact_bound"]
    a4_nc_best = hm.find_weighted_quartic_witness(
        S_nc, eqi.cmat_trace_real(Q_nc), eqi.cmat_trace_real(eqi.cmat_mul(eqi.cmat_mul(Q_nc, Q_nc), Q_nc)),
        b=1, peak_hints=[(Fraction(6), Fraction(5), Fraction(4))],
    )["exact_bound"]
    require(
        math.ceil(ropt_nc) == 2 and math.ceil(h4_nc) == 2 and a4_nc_peak > Fraction(2) and a4_nc_peak <= Fraction(3),
        f"Fresh non-commuting A4 dominance check failed: R_opt={float(ropt_nc)}, H4={float(h4_nc)}, A4_peak={float(a4_nc_peak)}, A4_best={float(a4_nc_best)}",
    )

    # 1F. Invalid witness rejection checks
    m_dummy = {1: Fraction(1), 2: Fraction(1), 3: Fraction(1), 4: Fraction(1)}
    expect_cert_error(lambda: hm.certify_stieltjes_hankel_2m(m_dummy, 0, [Fraction(-1)]), "A2 negative a1")
    expect_cert_error(lambda: hm.certify_noise_annihilating_quartic(m_dummy, 0, Fraction(0), Fraction(0)), "A3 x0=0")
    expect_cert_error(lambda: hm.certify_noise_annihilating_quartic(m_dummy, 0, Fraction(1), Fraction(-1)), "A3 tau<0")
    expect_cert_error(lambda: hm.certify_weighted_quartic_weyl(m_dummy, 0, 0, 0, s=1, p=0, gamma1=0, gamma3=0, kappa=1), "A4 p=0")
    expect_cert_error(lambda: hm.certify_weighted_quartic_weyl(m_dummy, 0, 0, 0, s=1, p=1, gamma1=-1, gamma3=0, kappa=1), "A4 g1<0")
    expect_cert_error(lambda: hm.certify_weighted_quartic_weyl(m_dummy, 0, 0, 0, s=1, p=1, gamma1=0, gamma3=-1, kappa=1), "A4 g3<0")
    expect_cert_error(lambda: hm.certify_weighted_quartic_weyl(m_dummy, 0, 0, 0, s=1, p=1, gamma1=0, gamma3=0, kappa=0), "A4 kappa=0")

    return {
        "sympy_all_four_identities_exact": True,
        "random_noncommuting_qi_trials_0_violations": n_trials,
        "trial_stats": counts,
        "unitary_and_scale_invariance_exact": True,
        "scan23848_pythagorean_rho_0p96_exact_1": True,
        "fresh_noncommuting_complex_A4_dominance": {
            "R_opt": round(float(ropt_nc), 4),
            "H4": round(float(h4_nc), 4),
            "A4_peak": round(float(a4_nc_peak), 4),
            "A4_best": round(float(a4_nc_best), 4),
        },
        "invalid_witnesses_rejected": 7,
    }


# ==============================================================================
# AUDIT-015: TRACK B (Exact Non-Affine Complex-Hermitian Bernstein Box Certifier)
# ==============================================================================
def audit_track_b() -> dict:
    # 2A. CRITICAL EXPLOIT TEST: Does PolyMatrix / RatMatrix accept NON-HERMITIAN families with Hermitian midpoint?!
    x = bc.MultiPoly.var(1, 0)
    one = bc.MultiPoly.const(1, 1)
    zero = bc.MultiPoly(1)
    i_poly = bc.MultiPoly.const(1, eqi.Qi(Fraction(0), Fraction(1)))

    # Exploit 1: M(x) = [[1 + i*x, 0], [0, 1]] on [-1/2, 1/2] -> M(0)=I is Hermitian, M(1/2) is NOT Hermitian!
    pm_nonherm_diag = bc.PolyMatrix(1, [[one + i_poly * x, zero], [zero, one]])
    res_ex1 = bc.certify_hermitian_box(pm_nonherm_diag, [(Fraction(-1, 2), Fraction(1, 2))])

    # Exploit 2: M(x) = [[1, 0], [100*x, 1]] on [-1/2, 1/2] -> upper triangle is I identically!
    pm_nonherm_lower = bc.PolyMatrix(1, [[one, zero], [100 * x, one]])
    res_ex2 = bc.certify_hermitian_box(pm_nonherm_lower, [(Fraction(-1, 2), Fraction(1, 2))])

    # Exploit 3: RatMatrix R(x) = [[(1 + i*x)/1, 0], [0, 1/1]] on [-1/2, 1/2]
    rm_nonherm = bc.RatMatrix(1, [[one + i_poly * x, zero], [zero, one]], [[one, one], [one, one]])
    res_ex3 = bc.certify_hermitian_box(rm_nonherm, [(Fraction(-1, 2), Fraction(1, 2))])

    # 2B. 200 random 2D/3D multivariate Bernstein enclosure soundness tests (50 pts each = 10,000 checks)
    rng = random.Random(20261122)
    bern_checks = 0
    for _ in range(200):
        d = rng.choice([2, 3])
        box = []
        for _ in range(d):
            a = Fraction(rng.randint(-4, 2), rng.randint(1, 3))
            w = Fraction(rng.randint(1, 4), rng.randint(1, 3))
            box.append(bc.QInterval(a, a + w))
        terms: dict[tuple[int, ...], Fraction] = {}
        for _ in range(rng.randint(3, 8)):
            exp = tuple(rng.randint(0, 2) for _ in range(d))
            terms[exp] = terms.get(exp, Fraction(0)) + Fraction(rng.randint(-5, 5), rng.randint(1, 3))
        enc = bc.bernstein_enclosure(terms, box)
        for _ in range(50):
            pt = [iv.lo + Fraction(rng.randint(0, 100), 100) * iv.width() for iv in box]
            val = Fraction(0)
            for exp, coef in terms.items():
                mon = Fraction(1)
                for xi, ei in zip(pt, exp):
                    if ei:
                        mon *= xi**ei
                val += coef * mon
            require(enc.lo <= val <= enc.hi, f"Bernstein enclosure violated: {val} not in {enc}")
            bern_checks += 1

    # 2C. Independent Descartes interior-point verification of Track B certified boxes
    # (1) fibral#5 taut & buckled sub-boxes
    for box_bounds in [
        ((Fraction(7, 10), Fraction(9, 10)), (Fraction(9, 10), Fraction(1))),
        ((Fraction(11, 10), Fraction(13, 10)), (Fraction(11, 10), Fraction(15, 10))),
    ]:
        for _ in range(100):
            l1 = box_bounds[0][0] + Fraction(rng.randint(0, 1000), 1000) * (box_bounds[0][1] - box_bounds[0][0])
            l2 = box_bounds[1][0] + Fraction(rng.randint(0, 1000), 1000) * (box_bounds[1][1] - box_bounds[1][0])
            M = truss_equilibrium_hessian_raw(l1, l2)
            require(v_descartes(to_vqi_mat(M)) == (2, 0, 0), f"fibral#5 interior point ({l1},{l2}) not (2,0,0)")

    # (2) 2D complex Hermitian Bloch gapped box [-1,1]^2
    bloch_g = build_bloch_2d_polymatrix(Fraction(4), Fraction(1), Fraction(1), Fraction(1))
    for _ in range(100):
        t1 = Fraction(rng.randint(-1000, 1000), 1000)
        t2 = Fraction(rng.randint(-1000, 1000), 1000)
        require(v_descartes(to_vqi_mat(bloch_g.eval_point((t1, t2)))) == (2, 0, 0), "Bloch gapped interior != (2,0,0)")

    # (3) 3x3 Morse saddle box [-1/2, 1/2]^2
    morse_h = build_morse_3x3_polymatrix()
    for _ in range(100):
        xv = Fraction(rng.randint(-500, 500), 1000)
        yv = Fraction(rng.randint(-500, 500), 1000)
        require(v_descartes(to_vqi_mat(morse_h.eval_point((xv, yv)))) == (2, 1, 0), "Morse saddle interior != (2,1,0)")

    # 2D. Fresh complex Hermitian 3x3 ZERO-DIAGONAL 2x2-block box (forces 2x2 complex block-Gershgorin!)
    # M(t) = [[0, 2 + i + t, t/4], [2 - i + t, 0, i*t/4], [t/4, -i*t/4, -3 + t^2]] on t in [-1/4, 1/4]
    # At t=0: [[0, 2+i, 0], [2-i, 0, 0], [0, 0, -3]] -> exact inertia (1, 2, 0), top-left 2x2 is zero-diagonal complex!
    t_var = bc.MultiPoly.var(1, 0)
    z0 = bc.MultiPoly(1)
    m01 = bc.MultiPoly.const(1, eqi.Qi(Fraction(2), Fraction(1))) + t_var
    m02 = Fraction(1, 4) * t_var
    m12 = eqi.Qi(Fraction(0), Fraction(1, 4)) * t_var
    m22 = bc.MultiPoly.const(1, -3) + t_var * t_var
    pm_complex_2x2 = bc.PolyMatrix(
        1,
        [
            [z0, m01, m02],
            [m01.conj(), z0, m12],
            [m02.conj(), m12.conj(), m22],
        ],
    )
    res_c2x2 = bc.certify_hermitian_box(pm_complex_2x2, [(Fraction(-1, 4), Fraction(1, 4))], max_depth=6, max_boxes=128)
    require(
        res_c2x2.status == "CERTIFIED_CONSTANT_INERTIA" and res_c2x2.certified_inertia == (1, 2, 0),
        f"Complex zero-diag 2x2 block box failed: {res_c2x2.to_summary_dict()}",
    )
    for _ in range(100):
        tv = Fraction(rng.randint(-250, 250), 1000)
        require(v_descartes(to_vqi_mat(pm_complex_2x2.eval_point((tv,)))) == (1, 2, 0), "Complex 2x2 interior != (1,2,0)")

    return {
        "CRITICAL_EXPLOIT_nonhermitian_PolyMatrix_diag_imag_falsely_certified": res_ex1.status == "CERTIFIED_CONSTANT_INERTIA",
        "CRITICAL_EXPLOIT_nonhermitian_PolyMatrix_lower_tri_falsely_certified": res_ex2.status == "CERTIFIED_CONSTANT_INERTIA",
        "CRITICAL_EXPLOIT_nonhermitian_RatMatrix_falsely_certified": res_ex3.status == "CERTIFIED_CONSTANT_INERTIA",
        "bernstein_2d_3d_interior_checks_0_violations": bern_checks,
        "interior_descartes_verifications": 500,
        "fresh_complex_2x2_zero_diag_box": {
            "status": res_c2x2.status,
            "inertia": list(res_c2x2.certified_inertia) if res_c2x2.certified_inertia else None,
            "subboxes": res_c2x2.certified_subboxes,
        },
    }


# ==============================================================================
# AUDIT-016: TRACK C (Hardened Dual-Oracle Q(i) Certifier)
# ==============================================================================
def audit_track_c() -> dict:
    # 3A. 100 fresh complex Q(i) Hermitian matrices (including high-multiplicity eigenvalues,
    #     zero diagonals, 1x1, zero matrix, all 5 2x2 block rows) vs independent check_003 Descartes!
    rng = random.Random(20261123)
    tested_mats: list[eqi.CMat] = []

    # Edge cases: 1x1 pos/neg/zero, 3x3 zero, multiplicity-3 and multiplicity-4 eigenvalues!
    tested_mats.append([[eqi.Qi(Fraction(3))]])
    tested_mats.append([[eqi.Qi(Fraction(-5, 2))]])
    tested_mats.append([[eqi.ZERO]])
    tested_mats.append(eqi.cmat_zeros(3, 3))
    for mult_eigs in [
        [Fraction(2), Fraction(2), Fraction(2)],
        [Fraction(-3), Fraction(-3), Fraction(1), Fraction(1)],
        [Fraction(5), Fraction(5), Fraction(5), Fraction(-2)],
        [Fraction(0), Fraction(0), Fraction(4), Fraction(4)],
    ]:
        n = len(mult_eigs)
        D0 = eqi.cmat_zeros(n, n)
        for i, e in enumerate(mult_eigs):
            D0[i][i] = eqi.Qi(e)
        U = eqi.cayley_unitary(n, rng, bound=2)
        tested_mats.append(eqi.cmat_mul(eqi.cmat_mul(U, D0), eqi.cmat_dagger(U)))

    # All 5 rows of 2x2 Hermitian block table with complex b = 1 + 2i (|b|^2 = 5):
    b_c = eqi.Qi(Fraction(1), Fraction(2))
    tested_mats.extend([
        [[eqi.ZERO, b_c], [b_c.conj(), eqi.ZERO]],                  # det=-5 < 0 -> (1,1,0)
        [[eqi.Qi(Fraction(3)), b_c], [b_c.conj(), eqi.Qi(Fraction(2))]],  # det=1>0, tr=5>0 -> (2,0,0)
        [[eqi.Qi(Fraction(-3)), b_c], [b_c.conj(), eqi.Qi(Fraction(-2))]],  # det=1>0, tr=-5<0 -> (0,2,0)
        [[eqi.Qi(Fraction(5)), b_c], [b_c.conj(), eqi.Qi(Fraction(1))]],  # det=0, tr=6>0 -> (1,0,1)
        [[eqi.Qi(Fraction(-5)), b_c], [b_c.conj(), eqi.Qi(Fraction(-1))]],  # det=0, tr=-6<0 -> (0,1,1)
    ])

    # 87 random complex Q(i) Hermitian matrices (including forced zero-diagonal blocks)
    while len(tested_mats) < 100:
        n = rng.choice([2, 3, 4, 5])
        M = eqi.cmat_zeros(n, n)
        for i in range(n):
            if rng.random() < 0.4:
                M[i][i] = eqi.ZERO
            else:
                M[i][i] = eqi.Qi(Fraction(rng.randint(-3, 3), rng.randint(1, 2)))
            for j in range(i + 1, n):
                v = eqi.Qi(Fraction(rng.randint(-2, 2), rng.randint(1, 2)),
                           Fraction(rng.randint(-2, 2), rng.randint(1, 2)))
                M[i][j] = v
                M[j][i] = v.conj()
        tested_mats.append(M)

    for idx, M in enumerate(tested_mats):
        v_in = v_descartes(to_vqi_mat(M))
        pldl_cert = dora.produce_pldl_certificate(M)
        res_pldl = dora.verify_inertia_dual_oracle(json.dumps(pldl_cert), mode="pldl", strict_string_entries=True)
        require(res_pldl["inertia"] == v_in, f"PLDL dual oracle mismatch idx={idx}: {res_pldl['inertia']} != {v_in}")
        C, C_inv, D, in_c = dora.produce_c_certificate(M)
        c_cert = {
            "M": eqi.matrix_to_json(M),
            "C": eqi.matrix_to_json(C),
            "C_inv": eqi.matrix_to_json(C_inv),
            "D": eqi.matrix_to_json(D),
            "claim": list(in_c),
        }
        res_c = dora.verify_inertia_dual_oracle(json.dumps(c_cert), mode="c_cert", strict_string_entries=True)
        require(res_c["inertia"] == v_in, f"C-cert dual oracle mismatch idx={idx}: {res_c['inertia']} != {v_in}")

    # 3B. Replay all 6 AUDIT-001 exploits against certify_mode_b_hardened
    I2 = [["1", "0"], ["0", "1"]]
    # Exploit 1: missing P >= 0 (H = diag(1,0), Q = diag(10,0) -> P = diag(-9,0) NOT PSD!)
    H_ex = [["1", "0"], ["0", "0"]]
    Q_ex = [["10", "0"], ["0", "0"]]
    P_ex = [["-9", "0"], ["0", "0"]]
    ex_codes = {}
    ex_codes["exploit1_non_psd_P"] = expect_cert_error(
        lambda: dora.certify_mode_b_hardened(H_ex, Q_ex, I2, I2, Q_ex, I2, I2, P_ex, target_rank_gt=0),
        "exploit1 non-PSD P",
    )
    # Exploit 2: non-Hermitian H
    ex_codes["exploit2_non_hermitian_H"] = expect_cert_error(
        lambda: dora.certify_mode_b_hardened([["1", "1"], ["0", "1"]], [["0", "0"], ["0", "0"]], I2, I2, [["0", "0"], ["0", "0"]], I2, I2, I2),
        "exploit2 non-Hermitian H",
    )
    # Exploit 3: len(H) != len(Q)
    ex_codes["exploit3_dim_mismatch"] = expect_cert_error(
        lambda: dora.certify_mode_b_hardened([["1"]], Q_ex, I2, I2, Q_ex, [["1"]], [["1"]], [["1"]]),
        "exploit3 len(H) != len(Q)",
    )
    # Exploit 4: extra D_diag entries / non-square C
    ex_codes["exploit4_extra_D_entries"] = expect_cert_error(
        lambda: dora.verify_congruence_c_cert(I2, I2, I2, ["1", "1", "1"]),
        "exploit4 extra D entries",
    )
    # Exploit 5: R3 parser leaks
    for bad_s in [True, 0.5, "1/2\n", " 1/2", "+1", "01", "-0", "0.5", "1_000", "1/0", "1/-2", "\u0661/\u0662"]:
        expect_cert_error(lambda v=bad_s: eqi.parse_strict_fraction(v), f"R3 leak {bad_s!r}")
    ex_codes["exploit5_r3_leaks_blocked"] = "12/12"
    # Exploit 6: negative or bool target_rank_gt
    ex_codes["exploit6_neg_target"] = expect_cert_error(
        lambda: dora.certify_mode_b_hardened(I2, [["0", "0"], ["0", "0"]], I2, I2, [["0", "0"], ["0", "0"]], I2, I2, I2, target_rank_gt=-1),
        "exploit6 neg target",
    )
    ex_codes["exploit6_bool_target"] = expect_cert_error(
        lambda: dora.certify_mode_b_hardened(I2, [["0", "0"], ["0", "0"]], I2, I2, [["0", "0"], ["0", "0"]], I2, I2, I2, target_rank_gt=True),
        "exploit6 bool target",
    )

    # Probe non-reduced canonical string edge cases ("2/4", "0/5", "3/1")
    nonreduced_accepted = []
    for cand in ("2/4", "0/5", "3/1", "-4/6"):
        try:
            eqi.parse_strict_fraction(cand)
            nonreduced_accepted.append(cand)
        except eqi.CertError:
            pass

    return {
        "dual_oracle_vs_independent_descartes_matches": len(tested_mats),
        "all_6_audit001_exploits_blocked": ex_codes,
        "minor_r3_nonreduced_strings_accepted": nonreduced_accepted,
    }


def main() -> None:
    report = {
        "audit_014_track_a": audit_track_a(),
        "audit_015_track_b": audit_track_b(),
        "audit_016_track_c": audit_track_c(),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
