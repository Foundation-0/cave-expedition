#!/usr/bin/env python3
"""
Audit 001: Independent Exact-Rational Verification of Generalized Lemma 3.2 (S2:F[62,96])
and Adversarial TCB Audit of session2/code_blocks/pair_06_block_00.py.

Zero external dependencies (Python stdlib only). Safe under:
  python3 -B check_001_lemma32_and_tcb.py
  python3 -O -B check_001_lemma32_and_tcb.py
  python3 -B -W error check_001_lemma32_and_tcb.py
"""
from __future__ import annotations
import os

from fractions import Fraction
import importlib.util
import json
import random
import sys
from pathlib import Path

GEMINI_SESSIONS_DIR = Path(os.environ.get("GEMINI_SESSIONS_DIR", "gemini-sessions"))
TARGET_PATH = (
    GEMINI_SESSIONS_DIR
    / "20261120-155823_2cf295ad46d56eb5_formal-verification-consolidation"
    / "code_blocks/pair_06_block_00.py"
)


def require(cond: bool, msg: str) -> None:
    """Explicit non-assert check (never stripped by python3 -O)."""
    if not cond:
        raise RuntimeError(f"CHECK FAILED: {msg}")


def load_target():
    spec = importlib.util.spec_from_file_location("pair_06_block_00", TARGET_PATH)
    require(spec is not None and spec.loader is not None, "failed to load target spec")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------- Exact rational linear algebra helpers ----------
Mat = list[list[Fraction]]


def zeros(n: int, m: int) -> Mat:
    return [[Fraction(0) for _ in range(m)] for _ in range(n)]


def eye(n: int) -> Mat:
    return [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]


def mat_add(A: Mat, B: Mat) -> Mat:
    return [[a + b for a, b in zip(rA, rB)] for rA, rB in zip(A, B)]


def mat_sub(A: Mat, B: Mat) -> Mat:
    return [[a - b for a, b in zip(rA, rB)] for rA, rB in zip(A, B)]


def mat_scale(s: Fraction, A: Mat) -> Mat:
    return [[s * v for v in row] for row in A]


def mat_t(A: Mat) -> Mat:
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def mat_mul(A: Mat, B: Mat) -> Mat:
    n, k, m = len(A), len(B), len(B[0])
    require(len(A[0]) == k, "mat_mul dimension mismatch")
    return [
        [sum((A[i][t] * B[t][j] for t in range(k)), Fraction(0)) for j in range(m)]
        for i in range(n)
    ]


def trace(A: Mat) -> Fraction:
    return sum((A[i][i] for i in range(len(A))), Fraction(0))


def hs_sq(A: Mat) -> Fraction:
    return sum((v * v for row in A for v in row), Fraction(0))


def mat_inv(A: Mat) -> Mat:
    """Exact Gauss-Jordan inverse over Q."""
    n = len(A)
    M = [row[:] + eye(n)[i] for i, row in enumerate(A)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if M[r][col] != 0:
                piv = r
                break
        require(piv is not None, "singular matrix in mat_inv")
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [M[r][c] - f * M[col][c] for c in range(2 * n)]
    return [row[n:] for row in M]


def gram_schmidt_projector(cols: list[list[Fraction]], n: int) -> tuple[Mat, int]:
    """Exact orthogonal projector over Q onto span(cols) in R^n."""
    basis: list[list[Fraction]] = []
    norms_sq: list[Fraction] = []
    for v in cols:
        w = v[:]
        for b, nsq in zip(basis, norms_sq):
            dot = sum((wi * bi for wi, bi in zip(w, b)), Fraction(0))
            coef = dot / nsq
            w = [wi - coef * bi for wi, bi in zip(w, b)]
        nsq = sum((wi * wi for wi in w), Fraction(0))
        if nsq > 0:
            basis.append(w)
            norms_sq.append(nsq)
    Pi = zeros(n, n)
    for b, nsq in zip(basis, norms_sq):
        for i in range(n):
            for j in range(n):
                Pi[i][j] += (b[i] * b[j]) / nsq
    return Pi, len(basis)


def cayley_orthogonal(n: int, rng: random.Random) -> Mat:
    """Generate a non-trivial exact rational orthogonal matrix O = (I - K)(I + K)^-1."""
    K = zeros(n, n)
    for i in range(n):
        for j in range(i + 1, n):
            val = Fraction(rng.randint(-3, 3), rng.randint(1, 3))
            K[i][j] = val
            K[j][i] = -val
    I = eye(n)
    return mat_mul(mat_sub(I, K), mat_inv(mat_add(I, K)))


def is_psd_via_exact_pivots(A: Mat) -> bool:
    """Exact symmetric PSD check via congruence (Handles zero pivots via 2x2 check)."""
    n = len(A)
    M = [row[:] for row in A]
    for i in range(n):
        for j in range(i + 1, n):
            if M[i][j] != M[j][i]:
                return False
    # Principal diagonal elimination: if M_ii < 0 -> False; if M_ii == 0, row/col must be 0
    for k in range(n):
        if M[k][k] < 0:
            return False
        if M[k][k] == 0:
            for j in range(k + 1, n):
                if M[k][j] != 0:
                    return False
            continue
        piv = M[k][k]
        for i in range(k + 1, n):
            f = M[i][k] / piv
            for j in range(k + 1, n):
                M[i][j] -= f * M[k][j]
    return True


# ---------- Part 1: Adversarial Audit of pair_06_block_00.py ----------
def audit_tcb_bugs(mod) -> dict:
    findings = {}

    # 1A. Critical Exploit: certify_mode_b_lemma32 omits P = H - Q >= 0 check
    H = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    Q = [[Fraction(10), Fraction(0)], [Fraction(0), Fraction(0)]]
    I2 = eye(2)
    forged = mod.certify_mode_b_lemma32(
        H, Q, I2, I2, [Fraction(10), Fraction(0)], c=Fraction(2), target_rank_gt=116
    )
    require(forged["certified_min_rank"] == 117, "expected forged rank >= 117")
    require(forged["exact_bound"] == "117", "expected exact_bound == 117")
    # Also certify >= 118 with target_rank_gt=116? Wait: 117 > 116 => certified_min_rank=117;
    # What if H=diag(1,0), Q=diag(10,0)? T_c = -9 + 20 = 11, T_c^2 = 121, 121/1 - 4 = 117.
    # For rank >= 118 we need strictly > 117 -> e.g. Q=diag(11,0): T_c = -10+22=12 -> 144-4=140.
    # Check exact cartographer claim: cartographer wrote bound=117 => rank >= 118;
    # Wait! STRICT inequality lhs > rhs means target_rank_gt=116 gives 117 > 116 => certified_min_rank=117!
    # At target_rank_gt=117, lhs=121 <= (117+4)*1 = 121 -> REJECTS 118, ACCEPTS 117!
    # Still a catastrophic forgery (rank >= 117 on a 2x2 matrix!). And Q=diag(11,0) forges >= 140!
    accepted_118 = False
    try:
        mod.certify_mode_b_lemma32(
            H, Q, I2, I2, [Fraction(10), Fraction(0)], c=Fraction(2), target_rank_gt=117
        )
        accepted_118 = True
    except ValueError:
        accepted_118 = False
    forged_140 = mod.certify_mode_b_lemma32(
        H, [[Fraction(11), Fraction(0)], [Fraction(0), Fraction(0)]],
        I2, I2, [Fraction(11), Fraction(0)], c=Fraction(2), target_rank_gt=139
    )
    findings["exploit_1_missing_P_psd"] = {
        "H_diag_1_0_Q_diag_10_0_exact_bound": forged["exact_bound"],
        "certified_min_rank_Q10": forged["certified_min_rank"],
        "note_strict_ineq_at_117": not accepted_118,
        "certified_min_rank_Q11": forged_140["certified_min_rank"],
    }

    # 1B. Missing is_symmetric(H) in Mode B
    H_nonsym = [[Fraction(2), Fraction(1)], [Fraction(0), Fraction(2)]]
    Q_zero = zeros(2, 2)
    res_nonsym = mod.certify_mode_b_lemma32(
        H_nonsym, Q_zero, I2, I2, [Fraction(0), Fraction(0)], c=Fraction(1), target_rank_gt=1
    )
    require(res_nonsym["certified_min_rank"] == 2, "expected non-symmetric H accepted")
    findings["exploit_2_missing_H_symmetric"] = res_nonsym

    # 1C. Missing dimension match len(H) == len(Q) in Mode B
    H_3x3 = eye(3)
    res_dim = mod.certify_mode_b_lemma32(
        H_3x3, Q_zero, I2, I2, [Fraction(0), Fraction(0)], c=Fraction(1), target_rank_gt=2
    )
    require(res_dim["certified_min_rank"] == 3, "expected 3x3 H with 2x2 Q accepted")
    findings["exploit_3_mismatched_H_Q_dims"] = res_dim

    # 1D. Missing dimension check in verify_congruence_inertia (non-square C / extra D_diag)
    C_3x2 = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)], [Fraction(99), Fraction(99)]]
    b_nonsq = mod.verify_congruence_inertia(Q_zero, C_3x2, I2, [Fraction(0), Fraction(0), Fraction(5)])
    require(b_nonsq == 1, "expected oversized D_diag/non-square C accepted")
    findings["exploit_4_nonsquare_C_and_extra_D_diag"] = {
        "returned_n_plus": b_nonsq,
        "true_n_plus_of_zero_matrix": 0,
    }

    # 1E. R3 encoding & type leaks in to_frac
    r3_leaks = {}
    for label, inp in [
        ("bool_True", True),
        ("bool_False", False),
        ("trailing_newline", "1/2\n"),
        ("padded_whitespace", "  3/4  "),
        ("decimal_string", "0.5"),
        ("underscore_separator", "1_000"),
        ("arabic_indic_digits", "\u0661/\u0662"),
    ]:
        try:
            val = mod.to_frac(inp)
            r3_leaks[label] = str(val)
        except Exception as exc:
            r3_leaks[label] = f"REJECTED({exc})"
    findings["exploit_5_R3_to_frac_leaks"] = r3_leaks

    # 1F. Negative target_rank_gt accepted in both Mode A and Mode B
    res_neg = mod.certify_mode_b_lemma32(
        [[Fraction(1)]], [[Fraction(0)]], [[Fraction(1)]], [[Fraction(1)]],
        [Fraction(0)], c=Fraction(1), target_rank_gt=-5
    )
    findings["exploit_6_negative_target_rank_gt"] = res_neg

    # 1G. Mode A external noise-floor trust boundary (single-species rank-1 signal + rank-1 noise > tau I)
    # P_sig = diag(1, 0), N = diag(0, 1), G = I_2, noise_diag = [1/10, 1/10] (violates N <= D_tau)
    res_mode_a_noise = mod.certify_mode_a_chimeric(
        eye(2), [Fraction(1, 10), Fraction(1, 10)], target_rank_gt=1
    )
    findings["mode_a_noise_boundary_false_rank2"] = res_mode_a_noise

    # 1H. Verify exact 6 calibration rows from Session 2 Pair 6 (lines 565-573)
    w1 = Fraction(6404, 10000) ** 2
    w2 = Fraction(3596, 10000) ** 2
    # For G = w1 c1 c1^T + w2 c2 c2^T with ||c1||=||c2||=1, c1^T c2 = rho, in R^T (T=5):
    # tr(G) = w1 + w2
    # tr(G^2) = w1^2 + w2^2 + 2 w1 w2 rho^2
    # H = G - tau I_T => tr(H) = (w1 + w2) - T*tau
    # tr(H^2) = tr(G^2) - 2*tau*tr(G) + T*tau^2
    table_checks = []
    for label, rho, tau, claimed in [
        ("ModeA_rho0_tau0", Fraction(0), Fraction(0), 1.574),
        ("ModeA_rho0.5_tau0", Fraction(1, 2), Fraction(0), 1.376),
        ("ModeA_rho0.9_tau0", Fraction(9, 10), Fraction(0), 1.074),
        ("ModeA_rho0.5_tau0.01", Fraction(1, 2), Fraction(1, 100), 1.191),
        ("ModeA_rho0.5_tau0.02", Fraction(1, 2), Fraction(2, 100), 1.007),
    ]:
        T = 5
        trG = w1 + w2
        trG2 = w1 * w1 + w2 * w2 + 2 * w1 * w2 * rho * rho
        trH = trG - T * tau
        trH2 = trG2 - 2 * tau * trG + T * tau * tau
        exact_b = (trH * trH) / trH2
        diff = abs(float(exact_b) - claimed)
        require(diff < 0.001, f"table row mismatch for {label}: {float(exact_b)} vs {claimed}")
        table_checks.append({"row": label, "exact_float": round(float(exact_b), 6), "claimed": claimed})
    # Mode B row: rho=0, tau=0, c=2, b=1, Q = w1 e1 e1^T, P = w2 e2 e2^T
    T2 = w2 + 2 * w1
    trH2_b = w1 * w1 + w2 * w2
    exact_b_modeb = (T2 * T2) / trH2_b - 4
    require(abs(float(exact_b_modeb) - 0.876) < 0.001, "Mode B table row mismatch")
    table_checks.append({"row": "ModeB_rho0_tau0_c2_b1", "exact_float": round(float(exact_b_modeb), 6), "claimed": 0.876})
    findings["pair6_calibration_table_exact"] = table_checks

    return findings


# ---------- Part 2: Exact Proof & Rational Identity Audit of Non-Commuting Lemma 3.2 ----------
def audit_lemma32_exact_identity() -> dict:
    """
    Verify the exact non-commuting algebraic identity over Q:
      Let P >= 0 (rank r), Q = Q_+ - Q_- (n_+(Q) = b_+ <= b), c >= 1.
      Let V_1 = range(Q_+), W = range(P) + V_1, V_2 = W cap V_1^perp (dim <= r),
      A = c * Pi_{V_1} + Pi_{V_2}.
      Then:
        (r + c^2 b) - (2 tr(P) + 2 c tr(Q) - ||P + Q||_HS^2)
          == ||(P + Q) - A||_HS^2
           + 2(c - 1) * (tr(P Pi_{V_1}) + tr(Q_-))
           + 2 * tr(Q_- (I - Pi_{V_2}))
           + (r - dim(V_2))
           + c^2 * (b - b_+).
      Every term on the RHS is provably >= 0 over R/C for arbitrary non-commuting Hermitian P, Q.
    """
    rng = random.Random(20261120)
    checked = 0
    noncommuting_count = 0
    min_slack_unscaled = None
    min_slack_scaled = None

    configs = [
        (2, 1, 1, 1, Fraction(2)),
        (2, 1, 1, 1, Fraction(5, 2)),
        (3, 1, 1, 1, Fraction(2)),
        (3, 1, 2, 2, Fraction(3)),
        (3, 2, 1, 2, Fraction(7, 3)),
        (4, 1, 1, 1, Fraction(2)),
        (4, 2, 1, 1, Fraction(4)),
        (4, 2, 2, 2, Fraction(3, 2)),
        (4, 1, 0, 0, Fraction(3)),
        (3, 1, 1, 1, Fraction(1)),
    ]

    for n, r_req, b_plus_req, b_bound, c in configs:
        for _ in range(25):
            # Build exact non-commuting P >= 0 of rank r via rational orthogonal basis O_P
            O_P = cayley_orthogonal(n, rng)
            eigs_P = [Fraction(rng.randint(1, 5), rng.randint(1, 3)) for _ in range(r_req)] + [Fraction(0)] * (n - r_req)
            P = zeros(n, n)
            cols_P = []
            for k in range(r_req):
                col = [O_P[i][k] for i in range(n)]
                cols_P.append(col)
                for i in range(n):
                    for j in range(n):
                        P[i][j] += eigs_P[k] * col[i] * col[j]

            # Build exact Q = Q_+ - Q_- in an independent rational orthogonal basis O_Q
            O_Q = cayley_orthogonal(n, rng)
            Q_plus = zeros(n, n)
            Q_minus = zeros(n, n)
            cols_V1 = []
            for k in range(b_plus_req):
                col = [O_Q[i][k] for i in range(n)]
                cols_V1.append(col)
                lam = Fraction(rng.randint(1, 5), rng.randint(1, 3))
                for i in range(n):
                    for j in range(n):
                        Q_plus[i][j] += lam * col[i] * col[j]
            for k in range(b_plus_req, n):
                col = [O_Q[i][k] for i in range(n)]
                lam = Fraction(rng.randint(0, 4), rng.randint(1, 3))
                for i in range(n):
                    for j in range(n):
                        Q_minus[i][j] += lam * col[i] * col[j]
            Q = mat_sub(Q_plus, Q_minus)
            H = mat_add(P, Q)

            # Check non-commutativity
            comm = mat_sub(mat_mul(P, Q), mat_mul(Q, P))
            if hs_sq(comm) > 0:
                noncommuting_count += 1

            # Exact projectors Pi_1 onto V_1, Pi_W onto range(P) + V_1, Pi_2 = Pi_W - Pi_1
            Pi1, dim_V1 = gram_schmidt_projector(cols_V1, n)
            PiW, dim_W = gram_schmidt_projector(cols_V1 + cols_P, n)
            Pi2 = mat_sub(PiW, Pi1)
            dim_V2 = dim_W - dim_V1
            require(dim_V1 == b_plus_req, "V1 dimension mismatch")
            require(dim_V2 <= r_req, "dim(V2) > rank(P) impossible")

            # Verify projector identities exactly
            require(mat_mul(Pi1, Pi2) == zeros(n, n), "Pi1 Pi2 != 0")
            require(mat_mul(Pi2, Pi2) == Pi2, "Pi2 not idempotent")

            A = mat_add(mat_scale(c, Pi1), Pi2)

            lhs_slack = (Fraction(r_req) + c * c * Fraction(b_bound)) - (
                2 * trace(P) + 2 * c * trace(Q) - hs_sq(H)
            )
            term_sq = hs_sq(mat_sub(H, A))
            term_c_p = 2 * (c - 1) * trace(mat_mul(P, Pi1))
            term_c_qm = 2 * (c - 1) * trace(Q_minus)
            term_qm_orth = 2 * trace(mat_mul(Q_minus, mat_sub(eye(n), Pi2)))
            term_dim = Fraction(r_req - dim_V2)
            term_b = c * c * Fraction(b_bound - dim_V1)

            rhs_slack = term_sq + term_c_p + term_c_qm + term_qm_orth + term_dim + term_b

            # Exact algebraic identity must hold with ZERO error!
            require(lhs_slack == rhs_slack, f"EXACT IDENTITY FAILED: {lhs_slack} != {rhs_slack}")
            # Every individual summand must be >= 0!
            require(term_sq >= 0 and term_c_p >= 0 and term_c_qm >= 0 and term_qm_orth >= 0
                    and term_dim >= 0 and term_b >= 0, "negative summand in slack decomposition")
            require(lhs_slack >= 0, "unscaled Lemma 3.2 violated")

            if min_slack_unscaled is None or lhs_slack < min_slack_unscaled:
                min_slack_unscaled = lhs_slack

            Tc = trace(P) + c * trace(Q)
            sH = hs_sq(H)
            if Tc > 0:
                require(sH > 0, "Tc > 0 with H == 0 impossible")
                scaled_slack = (Fraction(r_req) + c * c * Fraction(b_bound)) - (Tc * Tc) / sH
                require(scaled_slack >= 0, "scale-optimized Lemma 3.2 violated")
                if min_slack_scaled is None or scaled_slack < min_slack_scaled:
                    min_slack_scaled = scaled_slack

            checked += 1

    # Tightness witness: equality attained identically (slack == 0)
    P_tight = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]]
    Q_tight = [[Fraction(2), Fraction(0)], [Fraction(0), Fraction(0)]]
    c_tight = Fraction(2)
    H_tight = mat_add(P_tight, Q_tight)
    tight_unscaled = (Fraction(1) + c_tight * c_tight * 1) - (
        2 * trace(P_tight) + 2 * c_tight * trace(Q_tight) - hs_sq(H_tight)
    )
    tight_scaled = (Fraction(1) + c_tight * c_tight * 1) - (
        (trace(P_tight) + c_tight * trace(Q_tight)) ** 2
    ) / hs_sq(H_tight)
    require(tight_unscaled == 0 and tight_scaled == 0, "tightness witness failed")

    # Sharpness counterexample when c < 1 (proving c >= 1 is necessary):
    # P = [[1]], Q = [[-9/10]], b = 0, c = 1/2
    P_badc = [[Fraction(1)]]
    Q_badc = [[Fraction(-9, 10)]]
    H_badc = mat_add(P_badc, Q_badc)  # [[1/10]]
    c_bad = Fraction(1, 2)
    Tc_bad = trace(P_badc) + c_bad * trace(Q_badc)  # 11/20
    bound_badc = (Tc_bad * Tc_bad) / hs_sq(H_badc)  # 121/4 = 30.25 > 1 = rank(P)
    require(bound_badc == Fraction(121, 4) and bound_badc > 1, "c < 1 counterexample failed")

    return {
        "exact_rational_instances_checked": checked,
        "strictly_noncommuting_instances": noncommuting_count,
        "identity_max_abs_error": "0",
        "min_unscaled_slack_float": round(float(min_slack_unscaled), 6),
        "min_scaled_slack_float": round(float(min_slack_scaled), 6),
        "tightness_equality_attained": True,
        "c_lt_1_counterexample_bound_vs_rank": f"{bound_badc} (= {float(bound_badc)}) > rank 1 at c=1/2",
    }


def main() -> None:
    mod = load_target()
    tcb = audit_tcb_bugs(mod)
    thm = audit_lemma32_exact_identity()
    print(json.dumps({"tcb_audit": tcb, "lemma32_exact_audit": thm}, indent=2))


if __name__ == "__main__":
    main()
