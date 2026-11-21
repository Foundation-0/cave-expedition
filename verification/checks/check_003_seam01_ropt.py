#!/usr/bin/env python3
"""
Audit 003: Independent Exact Complex-Hermitian Verification of SEAM-01 (R_opt)
and Prototype Second Independent Exact Rational Hermitian Inertia Checker (SEAM-08)
via Faddeev-LeVerrier Characteristic Polynomial + Exact Descartes' Rule of Signs.

Zero external dependencies (Python stdlib only, zero shared code with loom#7 inertia_cert.py).
Safe under:
  python3 -B check_003_seam01_ropt.py
  python3 -O -B check_003_seam01_ropt.py
  python3 -B -W error check_003_seam01_ropt.py
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json
import math
import random


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(f"CHECK FAILED: {msg}")


# ---------- Exact Gaussian Rationals Q(i) ----------
@dataclass(frozen=True)
class Qi:
    re: Fraction
    im: Fraction = Fraction(0)

    def __add__(self, o: Qi) -> Qi:
        return Qi(self.re + o.re, self.im + o.im)

    def __sub__(self, o: Qi) -> Qi:
        return Qi(self.re - o.re, self.im - o.im)

    def __neg__(self) -> Qi:
        return Qi(-self.re, -self.im)

    def __mul__(self, o: Qi) -> Qi:
        return Qi(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    def conj(self) -> Qi:
        return Qi(self.re, -self.im)

    def norm_sq(self) -> Fraction:
        return self.re * self.re + self.im * self.im

    def __truediv__(self, o: Qi) -> Qi:
        d = o.norm_sq()
        require(d != 0, "division by zero in Q(i)")
        c = o.conj()
        num = self * c
        return Qi(num.re / d, num.im / d)

    def is_zero(self) -> bool:
        return self.re == 0 and self.im == 0


ZERO = Qi(Fraction(0))
ONE = Qi(Fraction(1))
CMat = list[list[Qi]]


def czeros(n: int, m: int) -> CMat:
    return [[ZERO for _ in range(m)] for _ in range(n)]


def ceye(n: int) -> CMat:
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def cadd(A: CMat, B: CMat) -> CMat:
    return [[a + b for a, b in zip(rA, rB)] for rA, rB in zip(A, B)]


def csub(A: CMat, B: CMat) -> CMat:
    return [[a - b for a, b in zip(rA, rB)] for rA, rB in zip(A, B)]


def cmul(A: CMat, B: CMat) -> CMat:
    n, k, m = len(A), len(B), len(B[0])
    require(len(A[0]) == k, "cmul dimension mismatch")
    out = czeros(n, m)
    for i in range(n):
        for j in range(m):
            s = ZERO
            for t in range(k):
                s = s + A[i][t] * B[t][j]
            out[i][j] = s
    return out


def cdagger(A: CMat) -> CMat:
    return [[A[i][j].conj() for i in range(len(A))] for j in range(len(A[0]))]


def is_hermitian(A: CMat) -> bool:
    n = len(A)
    if n == 0 or any(len(row) != n for row in A):
        return False
    for i in range(n):
        if A[i][i].im != 0:
            return False
        for j in range(i + 1, n):
            if A[i][j] != A[j][i].conj():
                return False
    return True


def ctrace_real(A: CMat) -> Fraction:
    s = ZERO
    for i in range(len(A)):
        s = s + A[i][i]
    require(s.im == 0, "Hermitian trace has nonzero imaginary part")
    return s.re


def cfrob_sq(A: CMat) -> Fraction:
    return sum((v.norm_sq() for row in A for v in row), Fraction(0))


def cmat_inv(A: CMat) -> CMat:
    n = len(A)
    M = [row[:] + ceye(n)[i] for i, row in enumerate(A)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if not M[r][col].is_zero():
                piv = r
                break
        require(piv is not None, "singular matrix in cmat_inv")
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and not M[r][col].is_zero():
                f = M[r][col]
                M[r] = [M[r][c] - f * M[col][c] for c in range(2 * n)]
    return [row[n:] for row in M]


def crank(A: CMat) -> int:
    """Exact rank over Q(i) via Gauss elimination."""
    n = len(A)
    m = len(A[0])
    M = [row[:] for row in A]
    r = 0
    for col in range(m):
        piv = None
        for i in range(r, n):
            if not M[i][col].is_zero():
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][col]
        for i in range(r + 1, n):
            if not M[i][col].is_zero():
                f = M[i][col] / pv
                for j in range(col, m):
                    M[i][j] = M[i][j] - f * M[r][j]
        r += 1
    return r


def cayley_unitary(n: int, rng: random.Random) -> CMat:
    """Exact rational unitary U = (I - K)(I + K)^{-1} in Q(i)^{n x n} with K* = -K."""
    K = czeros(n, n)
    for i in range(n):
        K[i][i] = Qi(Fraction(0), Fraction(rng.randint(-2, 2), rng.randint(1, 2)))
        for j in range(i + 1, n):
            re = Fraction(rng.randint(-2, 2), rng.randint(1, 2))
            im = Fraction(rng.randint(-2, 2), rng.randint(1, 2))
            K[i][j] = Qi(re, im)
            K[j][i] = Qi(-re, im)  # K[j][i] = -conj(K[i][j])
    I = ceye(n)
    return cmul(csub(I, K), cmat_inv(cadd(I, K)))


# ---------- Independent Exact Hermitian Inertia Checker (Faddeev-LeVerrier + Descartes) ----------
def hermitian_inertia_descartes(H: CMat) -> tuple[int, int, int]:
    """
    Independent exact inertia (n_pos, n_neg, n_zero) of Hermitian H in Q(i)^{n x n}.
    Uses Faddeev-LeVerrier to compute exact characteristic polynomial
      p(x) = det(xI - H) = sum_{k=0}^n c_k x^{n-k}  (c_0 = 1, all c_k in Q).
    Because H is Hermitian, ALL roots of p(x) are real!
    Therefore Descartes' rule of signs is EXACT (not merely an upper bound):
      - n_zero = multiplicity of root 0 (trailing zero coefficients)
      - n_pos  = sign changes in nonzero coefficients of p(x)
      - n_neg  = sign changes in nonzero coefficients of p(-x)
      and n_pos + n_neg + n_zero == n holds identically!
    """
    require(is_hermitian(H), "matrix must be Hermitian")
    n = len(H)
    # Faddeev-LeVerrier: B_1 = H, c_1 = -tr(B_1); B_k = H (B_{k-1} + c_{k-1} I), c_k = -tr(B_k)/k
    coeffs: list[Fraction] = [Fraction(1)]
    B = H
    c1 = -ctrace_real(B)
    coeffs.append(c1)
    for k in range(2, n + 1):
        # B_prev + c_{k-1} I
        shifted = [row[:] for row in B]
        ck_prev = Qi(coeffs[-1])
        for i in range(n):
            shifted[i][i] = shifted[i][i] + ck_prev
        B = cmul(H, shifted)
        ck = -ctrace_real(B) / Fraction(k)
        coeffs.append(ck)
    # Verify Cayley-Hamilton residue B_n + c_n I == 0 as internal self-check!
    cn = Qi(coeffs[-1])
    for i in range(n):
        for j in range(n):
            val = B[i][j] + (cn if i == j else ZERO)
            require(val.is_zero(), "Faddeev-LeVerrier Cayley-Hamilton check failed")

    # Factor out trailing zeros (root 0 multiplicity)
    n_zero = 0
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
        n_zero += 1

    def sign_changes(seq: list[Fraction]) -> int:
        nz = [x for x in seq if x != 0]
        return sum(1 for a, b in zip(nz, nz[1:]) if (a > 0) != (b > 0))

    n_pos = sign_changes(coeffs)
    # p(-x): multiply coefficient of x^{deg - k} by (-1)^{deg - k}; equivalently alternate signs
    alt = [c if (k % 2 == 0) else -c for k, c in enumerate(coeffs)]
    n_neg = sign_changes(alt)
    require(n_pos + n_neg + n_zero == n, f"Descartes sum mismatch: {(n_pos, n_neg, n_zero)} vs {n}")
    return (n_pos, n_neg, n_zero)


# ---------- Rank Bounds: R_opt (guarded), Fable's R_G, Fixed c=2 Lemma 3.2 ----------
def R_opt_guarded(u: Fraction, t: Fraction, S: Fraction, b: int) -> Fraction:
    """Guarded exact rational R_opt(u, t, S, b) fixing u=0 (0/0) and negative else-branch."""
    if u <= 0 or (u + t) <= 0:
        return Fraction(0)
    require(S > 0, "S must be > 0 when u + t > 0")
    if b > 0 and t > 0 and t * (u + t) >= Fraction(b) * S:
        denom = S - (t * t) / Fraction(b)
        require(denom > 0, "S > t^2/b violated for feasible u > 0, t > 0")
        return (u * u) / denom
    val = ((u + t) * (u + t)) / S - Fraction(b)
    return val if val > 0 else Fraction(0)


def R_opt_raw_peer_weaver(u: Fraction, t: Fraction, S: Fraction, b: int) -> Fraction:
    """Exact transcription of peer-weaver #17 formula (to probe edge-case defects)."""
    if b > 0 and t > 0 and t * (u + t) >= Fraction(b) * S:
        return (u * u) / (S - (t * t) / Fraction(b))
    elif u + t > 0:
        return ((u + t) * (u + t)) / S - Fraction(b)
    else:
        return Fraction(0)


def R_G_fable(u: Fraction, t: Fraction, S: Fraction, b: int) -> Fraction:
    """Fable's docs/10 §3.3 best unscaled member R_G."""
    if b > 0 and t >= Fraction(b):
        return 2 * u + (t * t) / Fraction(b) - S
    return 2 * (u + t) - S - Fraction(b)


def R_lemma32_c2(u: Fraction, t: Fraction, S: Fraction, b: int) -> Fraction:
    """Session 2 scale-optimized Lemma 3.2 at fixed c = 2."""
    T2 = u + 2 * t
    if T2 <= 0 or S <= 0:
        return Fraction(0)
    val = (T2 * T2) / S - Fraction(4 * b)
    return val if val > 0 else Fraction(0)


# ---------- Part 1: Edge-Case Audit of peer-weaver #17 Formula ----------
def audit_edge_cases() -> dict:
    # Edge 1: u = 0, P1 = 0, Q = diag(1, 0), b = 1 -> t = 1, S = 1, t(u+t) = 1 == b*S -> 0/0!
    div0_bug = None
    try:
        R_opt_raw_peer_weaver(Fraction(0), Fraction(1), Fraction(1), 1)
    except ZeroDivisionError as exc:
        div0_bug = f"ZeroDivisionError: {exc}"
    require(div0_bug is not None, "expected raw #17 formula to hit ZeroDivisionError at u=0, t=b=S=1")
    guarded_zero = R_opt_guarded(Fraction(0), Fraction(1), Fraction(1), 1)
    require(guarded_zero == 0, "guarded R_opt must return 0 when u=0")

    # Edge 2: Negative value in raw else-branch (u=1, t=1, S=10, b=5 -> 4/10 - 5 = -4.6)
    raw_neg = R_opt_raw_peer_weaver(Fraction(1), Fraction(1), Fraction(10), 5)
    require(raw_neg < 0, "expected raw #17 formula to return negative value")
    guarded_nonneg = R_opt_guarded(Fraction(1), Fraction(1), Fraction(10), 5)
    require(guarded_nonneg == 0, "guarded R_opt must clamp negative branch to 0")

    return {
        "edge1_u0_t1_S1_b1_raw_peer_weaver": div0_bug,
        "edge1_guarded_R_opt": str(guarded_zero),
        "edge2_raw_negative_else_branch": str(raw_neg),
        "edge2_guarded_clamped": str(guarded_nonneg),
    }


# ---------- Part 2: Exact Complex Hermitian Verification over Q(i) ----------
def audit_complex_hermitian() -> dict:
    rng = random.Random(20261120)
    total = 0
    noncommuting = 0
    strict_imag = 0
    beats_RG = 0
    ties_RG = 0
    beats_c2 = 0
    strictly_sharper_proj_rank = 0
    strictly_sharper_proj_inertia = 0
    regime_1_count = 0
    regime_2_count = 0
    regime_0_count = 0

    for mode in ("general", "regime1_targeted"):
        for n in (2, 3, 4):
            for _ in range(70):
                if mode == "regime1_targeted":
                    b_true = rng.randint(1, n - 1)
                    r_true = rng.randint(1, n)
                else:
                    r_true = rng.randint(0, n)
                    b_true = rng.randint(0, n)

                U_P = cayley_unitary(n, rng)
                U_Q = cayley_unitary(n, rng)

                # Build P1 = U_P diag(eigs_P) U_P^*
                P1 = czeros(n, n)
                for k in range(r_true):
                    if mode == "regime1_targeted":
                        lam = Fraction(rng.randint(1, 3), rng.randint(2, 5))
                    else:
                        lam = Fraction(rng.randint(1, 5), rng.randint(1, 3))
                    for i in range(n):
                        for j in range(n):
                            P1[i][j] = P1[i][j] + Qi(lam) * U_P[i][k] * U_P[j][k].conj()

                # Build Q = U_Q diag(eigs_Q) U_Q^* with exact b_true positive eigenvalues
                Q = czeros(n, n)
                for k in range(b_true):
                    if mode == "regime1_targeted":
                        # Near-uniform large positive eigs on W to probe Regime 1: t(u+t) >= b*S
                        lam = Fraction(rng.randint(8, 12), 2)
                    else:
                        lam = Fraction(rng.randint(1, 5), rng.randint(1, 3))
                    for i in range(n):
                        for j in range(n):
                            Q[i][j] = Q[i][j] + Qi(lam) * U_Q[i][k] * U_Q[j][k].conj()
                for k in range(b_true, n):
                    if mode == "regime1_targeted":
                        lam = -Fraction(rng.randint(0, 1), 10)
                    else:
                        lam = -Fraction(rng.randint(0, 5), rng.randint(1, 3))
                    if lam != 0:
                        for i in range(n):
                            for j in range(n):
                                Q[i][j] = Q[i][j] + Qi(lam) * U_Q[i][k] * U_Q[j][k].conj()

                # Random global positive scaling alpha to test scale invariance
                alpha = Fraction(rng.randint(1, 7), rng.randint(1, 4))
                P1 = [[Qi(alpha) * v for v in row] for row in P1]
                Q = [[Qi(alpha) * v for v in row] for row in Q]
                M = cadd(P1, Q)

                # Independent exact rank & inertia verification
                r_exact = crank(P1)
                require(r_exact == r_true, "exact rank mismatch")
                n_pos_Q, n_neg_Q, n_zero_Q = hermitian_inertia_descartes(Q)
                require(n_pos_Q == b_true, f"independent Descartes inertia mismatch: {n_pos_Q} vs {b_true}")
                p_pos, p_neg, p_zero = hermitian_inertia_descartes(P1)
                require(p_neg == 0 and p_pos == r_true, "P1 PSD verification failed")

                # Exact W^perp compression: columns b_true..n-1 of U_Q are an exact orthonormal basis of W^perp!
                m_perp = n - b_true
                if m_perp > 0:
                    U_perp = [[U_Q[i][b_true + j] for j in range(m_perp)] for i in range(n)]
                    U_perp_dag = cdagger(U_perp)
                    P22 = cmul(cmul(U_perp_dag, P1), U_perp)
                    H22 = cmul(cmul(U_perp_dag, M), U_perp)
                    rank_P_perp = crank(P22)
                    n_pos_H_perp, _, _ = hermitian_inertia_descartes(H22)
                else:
                    rank_P_perp = 0
                    n_pos_H_perp = 0

                # Exact block-slack identity check for Portal 1 at c = 2 (and optimal c when Regime 1)
                U_Q_dag = cdagger(U_Q)
                P_blk = cmul(cmul(U_Q_dag, P1), U_Q)
                Q_blk = cmul(cmul(U_Q_dag, Q), U_Q)
                P11_tr = sum((P_blk[i][i].re for i in range(b_true)), Fraction(0))
                Q_minus_tr = sum((-Q_blk[i][i].re for i in range(b_true, n)), Fraction(0))
                P12_frob2 = sum(
                    (P_blk[i][j].norm_sq() for i in range(b_true) for j in range(b_true, n)),
                    Fraction(0),
                )
                c_test = Fraction(2)
                W_err2 = Fraction(0)
                for i in range(b_true):
                    for j in range(b_true):
                        v = P_blk[i][j] + Q_blk[i][j] - (Qi(c_test) if i == j else ZERO)
                        W_err2 += v.norm_sq()
                u = ctrace_real(P1)
                t = ctrace_real(Q)
                S = cfrob_sq(M)
                b = n_pos_Q
                lhs_gap = (Fraction(n_pos_H_perp) + c_test * c_test * Fraction(b)) - (2 * u + 2 * c_test * t - S)
                rhs_lb = 2 * (c_test - 1) * (P11_tr + Q_minus_tr) + 2 * P12_frob2 + W_err2
                require(lhs_gap >= rhs_lb and rhs_lb >= 0, f"Portal 1 slack bound violated: {lhs_gap} < {rhs_lb}")

                # Track non-commuting and genuinely complex Hermitian instances
                comm = csub(cmul(P1, Q), cmul(Q, P1))
                if cfrob_sq(comm) > 0:
                    noncommuting += 1
                if any(v.im != 0 for row in M for v in row):
                    strict_imag += 1

                ropt = R_opt_guarded(u, t, S, b)
                rg = R_G_fable(u, t, S, b)
                rc2 = R_lemma32_c2(u, t, S, b)

                # Core strengthened chain: rank(P1) >= rank(P_perp) >= n_+(H_perp) >= R_opt >= max(R_G, R_c2)
                require(r_exact >= rank_P_perp >= n_pos_H_perp, "projected rank/inertia chain violated")
                require(Fraction(n_pos_H_perp) >= ropt, f"STRENGTHENED R_opt VIOLATED: n_+(H_perp)={n_pos_H_perp} < {ropt}")
                require(ropt >= rg, f"R_opt < R_G violated: {ropt} < {rg}")
                require(ropt >= rc2, f"R_opt < R_c2 violated: {ropt} < {rc2}")

                if rank_P_perp < r_exact:
                    strictly_sharper_proj_rank += 1
                if n_pos_H_perp < rank_P_perp:
                    strictly_sharper_proj_inertia += 1

                # Verify scale invariance explicitly (scale by 17/5)
                sc = Fraction(17, 5)
                ropt_scaled = R_opt_guarded(sc * u, sc * t, sc * sc * S, b)
                require(ropt_scaled == ropt, "R_opt not scale-invariant!")

                if ropt > rg:
                    beats_RG += 1
                elif ropt == rg:
                    ties_RG += 1
                if ropt > rc2:
                    beats_c2 += 1

                if u <= 0 or u + t <= 0:
                    regime_0_count += 1
                elif b > 0 and t > 0 and t * (u + t) >= Fraction(b) * S:
                    regime_1_count += 1
                else:
                    regime_2_count += 1

                total += 1

    require(regime_1_count >= 50, f"expected >= 50 Regime 1 instances, got {regime_1_count}")

    # Scan 23848 Mode B exact comparison across rho = 0, 0.5, 0.75, 0.9
    w1 = Fraction(6404, 10000) ** 2
    w2 = Fraction(3596, 10000) ** 2
    scan23848_comp = {}
    for rho_s, rho in [("0.0", Fraction(0)), ("0.5", Fraction(1, 2)), ("0.75", Fraction(3, 4)), ("0.9", Fraction(9, 10))]:
        S_r = w1 * w1 + w2 * w2 + 2 * w1 * w2 * rho * rho
        scan23848_comp[f"rho={rho_s}"] = {
            "R_opt": round(float(R_opt_guarded(w2, w1, S_r, 1)), 6),
            "R_opt_exact_is_1": R_opt_guarded(w2, w1, S_r, 1) == Fraction(1),
            "Lemma32_c2": round(float(R_lemma32_c2(w2, w1, S_r, 1)), 6),
        }

    return {
        "complex_hermitian_instances_Q_i": total,
        "strictly_noncommuting": noncommuting,
        "strictly_complex_nonzero_imag": strict_imag,
        "violations_strengthened_chain_n_pos_H_perp_ge_R_opt": 0,
        "instances_with_rank_P_perp_strictly_lt_rank_P": strictly_sharper_proj_rank,
        "instances_with_n_pos_H_perp_strictly_lt_rank_P_perp": strictly_sharper_proj_inertia,
        "R_opt_strictly_beats_Fable_RG": beats_RG,
        "R_opt_ties_Fable_RG": ties_RG,
        "R_opt_strictly_beats_fixed_c2": beats_c2,
        "regime_counts": {"regime1_u2_over_S_minus_t2_b": regime_1_count,
                          "regime2_u_plus_t_sq_over_S_minus_b": regime_2_count,
                          "regime0_zero": regime_0_count},
        "scale_invariance_exact": True,
        "scan23848_mode_b_comparison": scan23848_comp,
    }


# ---------- Part 3: Constructive Exact & Integer-Exact Pointwise Sharpness ----------
def construct_sharp_diagonal(u: float, t: float, S: float, b: int) -> tuple[list[float], list[float]]:
    """
    Construct diagonal real symmetric (P1_diag, Q_diag) with P1 >= 0, n_+(Q) <= b,
    tr(P1) = u, tr(Q) = t, ||P1 + Q||_F^2 = S, and rank(P1) == max(1, ceil(R_opt(u,t,S,b))),
    for ANY feasible (u, t, S, b) with u > 0.
    """
    require(u > 0, "requires u > 0")
    # Compute R_opt in float for branching
    if u + t <= 0:
        # Rank 1 ALWAYS suffices!
        # Put P1 = [u, 0, ...], Q = [-a, ...].
        if b == 0:
            # Feasible range for b=0, u+t<=0: S in [(u+t)^2 / k -> 0+, u^2 + t^2]
            # Use P1 = [u, 0, ..., 0], Q = [-alpha, -beta, ..., -beta] (k copies of -beta)
            # Choose alpha = u (so first entry of M is 0) if S <= (u+t)^2, else alpha in [0, u]
            if S <= (u + t) ** 2 + 1e-12:
                m_neg = max(1, int(math.ceil((u + t) ** 2 / S)))
                # Solve (m-1) x^2 + y^2 = S, (m-1)x + y = -(u+t) =: A > 0
                A = -(u + t)
                if m_neg == 1:
                    q_rest = [-A]
                else:
                    # x = (A - sqrt(disc)) / m, y = (A + (m-1)*sqrt(disc)) / m
                    disc = max(0.0, (m_neg * S - A * A) / (m_neg - 1))
                    rt = math.sqrt(disc)
                    x = (A - rt) / m_neg
                    y = (A + (m_neg - 1) * rt) / m_neg
                    q_rest = [-x] * (m_neg - 1) + [-y]
                return [u] + [0.0] * len(q_rest), [-u] + q_rest
            else:
                # S in ((u+t)^2, u^2 + t^2]: M = [u - a, t + a], S = (u-a)^2 + (t+a)^2 = 2a^2 + 2(t-u)a + u^2+t^2
                # Solve 2a^2 + 2(t-u)a + (u^2 + t^2 - S) = 0 for a in [0, u]
                disc = max(0.0, (t - u) ** 2 - 2.0 * (u * u + t * t - S))
                a = ((u - t) - math.sqrt(disc)) / 2.0
                return [u, 0.0], [-a, t + a]
        else:
            # b >= 1, u + t <= 0: rank 1 with Q having 1 positive eigenvalue q > 0 and negative ones
            # Put P1 = [u, 0, 0], Q = [-u, q, -(q - (u+t))] => tr(Q) = -u + u + t = t,
            # S = q^2 + (q - (u+t))^2 = 2 q^2 - 2(u+t) q + (u+t)^2 >= (u+t)^2.
            if S >= (u + t) ** 2:
                A = -(u + t)
                # 2 q^2 + 2 A q + A^2 - S = 0 => q = (-A + sqrt(2S - A^2)) / 2 >= 0
                q = (-A + math.sqrt(max(0.0, 2.0 * S - A * A))) / 2.0
                return [u, 0.0, 0.0], [-u, q, -(q + A)]
            else:
                # Same small-S construction as b=0 (using <= b positive eigenvalues, namely 0)
                return construct_sharp_diagonal(u, t, S, 0)

    # Now u > 0 and u + t > 0
    if b > 0 and t > 0 and t * (u + t) >= b * S - 1e-12:
        ropt = (u * u) / (S - (t * t) / b)
        r = max(1, int(math.ceil(ropt - 1e-12)))
        target_p2 = S - (t * t) / b
        if target_p2 <= u * u + 1e-12:
            # Orthogonal V1 (dim b, Q = t/b) and V2 (dim r, P1 diag sum=u, sumsq=target_p2)
            if r == 1:
                p_vals = [u]
            else:
                disc = max(0.0, (r * target_p2 - u * u) / (r - 1))
                rt = math.sqrt(disc)
                p_lo = (u - rt) / r
                p_hi = (u + (r - 1) * rt) / r
                p_vals = [p_lo] * (r - 1) + [p_hi]
            return [0.0] * b + p_vals, [t / b] * b + [0.0] * r
        else:
            # r == 1 and S > u^2 + t^2/b: add orthogonal negative eigenvalue -s0 to Q, boost Q_+ to (t+s0)/b
            # u^2 + (t+s0)^2/b + s0^2 = S => (1 + 1/b) s0^2 + (2t/b) s0 + (u^2 + t^2/b - S) = 0
            A_q = 1.0 + 1.0 / b
            B_q = 2.0 * t / b
            C_q = u * u + (t * t) / b - S
            s0 = (-B_q + math.sqrt(max(0.0, B_q * B_q - 4.0 * A_q * C_q))) / (2.0 * A_q)
            return [u] + [0.0] * (b + 1), [0.0] + [(t + s0) / b] * b + [-s0]
    else:
        ropt = max(0.0, ((u + t) ** 2) / S - b)
        r = max(1, int(math.ceil(ropt - 1e-12)))
        if b > 0 and t > 0 and r > (b * u) / t + 1e-12:
            # Case B: t^2/b + u^2/r < S strictly; use orthogonal Q_+ and P1!
            target_p2 = S - (t * t) / b
            if target_p2 <= u * u + 1e-12:
                if r == 1:
                    p_vals = [u]
                else:
                    disc = max(0.0, (r * target_p2 - u * u) / (r - 1))
                    rt = math.sqrt(disc)
                    p_vals = [(u - rt) / r] * (r - 1) + [(u + (r - 1) * rt) / r]
                return [0.0] * b + p_vals, [t / b] * b + [0.0] * r
            else:
                A_q = 1.0 + 1.0 / b
                B_q = 2.0 * t / b
                C_q = u * u + (t * t) / b - S
                s0 = (-B_q + math.sqrt(max(0.0, B_q * B_q - 4.0 * A_q * C_q))) / (2.0 * A_q)
                return [u] + [0.0] * (b + 1), [0.0] + [(t + s0) / b] * b + [-s0]

        # Case A: either b==0, t<=0, or r <= b*u/t
        k = r + b
        if S <= (u + t) ** 2 + 1e-12:
            # Pick h_1 >= h_2 == ... == h_k > 0 with sum = u+t, sumsq = S
            if k == 1:
                hs = [u + t]
            else:
                disc = max(0.0, (k * S - (u + t) ** 2) / (k - 1))
                rt = math.sqrt(disc)
                h_hi = ((u + t) + (k - 1) * rt) / k
                h_lo = ((u + t) - rt) / k
                hs = [h_hi] + [h_lo] * (k - 1)
            # Top b go to Q_+ (with P1=0); remaining r go to P1 - Q_-
            sum_top_b = sum(hs[:b])
            delta = sum_top_b - t
            require(delta >= -1e-10, f"Case A delta < 0: {delta}")
            delta = max(0.0, delta)
            P_diag = [0.0] * b + [h + delta / r for h in hs[b:]]
            Q_diag = hs[:b] + [-delta / r] * r
            return P_diag, Q_diag
        else:
            # S > (u+t)^2 => r == 1!
            require(r == 1, f"expected r==1 when S > (u+t)^2, got r={r}")
            if b == 0:
                # S in ((u+t)^2, u^2 + t^2]
                disc = max(0.0, (t - u) ** 2 - 2.0 * (u * u + t * t - S))
                a = ((u - t) - math.sqrt(disc)) / 2.0
                return [u, 0.0], [-a, t + a]
            else:
                # Put M = [u+t+s0, -s0] with Q = [t+s0, -s0], P1 = [u, 0] if t+s0 >= 0;
                # or M = [u, q, -s0] with q - s0 = t => S = u^2 + q^2 + (q-t)^2
                if S <= (u + t) ** 2 + 1e12:
                    # Choose Q = [q, -(q - t)], P1 = [u, 0] if u+q >= 0: M = [u+q, t-q]
                    # S = (u+q)^2 + (t-q)^2 = 2q^2 + 2(u-t)q + u^2 + t^2
                    # Wait: at q = -t (Wait, q can be <= 0? No, if we put P1 = [u, 0, 0], Q = [0, q, -(q-t)]):
                    # Better: P1 = [u, 0], Q = [q1, -(q1-t)] -> wait, for S >= (u+t)^2:
                    # Let x >= 0: M = [u + t + x, -x] has sum = u+t, sumsq = (u+t+x)^2 + x^2,
                    # sweeping [(u+t)^2, +inf) continuously!
                    # Split M[0] = u + (t + x) => P1 = [u, 0], Q = [t + x, -x]!
                    # Wait: Q has at most 1 positive entry (t+x could be >0, -x <= 0), so n_+(Q) <= 1 <= b!
                    # Solve 2 x^2 + 2(u+t)x + (u+t)^2 - S = 0:
                    A_s = u + t
                    x = (-A_s + math.sqrt(max(0.0, 2.0 * S - A_s * A_s))) / 2.0
                    return [u, 0.0], [t + x, -x]


def audit_sharpness() -> dict:
    # 1. Exact rational equality attainment in both regimes (zero error over Q)
    # Regime 1: r=2, b=1, P1 = diag(0, 3, 3) (u=6), Q = diag(5, 0, 0) (t=5), S = 43.
    # Check t(u+t) = 55 >= 1*43, R_opt = 36 / (43 - 25) = 2 == r!
    r1_val = R_opt_guarded(Fraction(6), Fraction(5), Fraction(43), 1)
    require(r1_val == Fraction(2), f"exact Regime 1 tightness failed: {r1_val}")

    # Regime 2 (t > 0, t(u+t) < bS): r=9, b=1, u=10, t=1, S=121/10 -> R_opt = 9 == r!
    # Realized by Q = diag(11/10, -1/90, ..., -1/90), P1 = diag(0, 10/9, ..., 10/9)
    r2_pos_t = R_opt_guarded(Fraction(10), Fraction(1), Fraction(121, 10), 1)
    require(r2_pos_t == Fraction(9), f"exact Regime 2 (t>0) tightness failed: {r2_pos_t}")

    # Regime 2 (t < 0, b = 1): r=2, b=1, lambda=2, P1=diag(0, 5, 5) (u=10), Q=diag(2, -3, -3) (t=-4),
    # M = diag(2, 2, 2), S = 12, (u+t)^2/S - b = 36/12 - 1 = 2 == r!
    r2_neg_t = R_opt_guarded(Fraction(10), Fraction(-4), Fraction(12), 1)
    require(r2_neg_t == Fraction(2), f"exact Regime 2 (t<0) tightness failed: {r2_neg_t}")

    # Regime 2 (b = 0, t < 0): r=3, b=0, P1=diag(2, 2, 2) (u=6), Q=diag(-1, -1, -1) (t=-3),
    # M = diag(1, 1, 1), S = 3, (u+t)^2/S - 0 = 9/3 = 3 == r!
    r2_b0 = R_opt_guarded(Fraction(6), Fraction(-3), Fraction(3), 0)
    require(r2_b0 == Fraction(3), f"exact Regime 2 (b=0) tightness failed: {r2_b0}")

    # 2. Constructive integer-exact sharpness over 150 random feasible tuples (incl. non-integer R_opt!)
    rng = random.Random(999)
    realized = 0
    max_err = 0.0
    subcases_hit = {"R1": 0, "R2_caseA": 0, "R2_caseB": 0, "u_plus_t_le_0": 0}

    for idx in range(200):
        # Generate a genuinely feasible tuple from a random diagonal matrix first
        n = rng.randint(2, 6)
        if idx < 50:
            # Specifically hit Regime 1 (disjoint Q_+ large, P1 smaller, Q_- tiny/zero)
            b_src = rng.randint(1, n - 1)
            r_src = rng.randint(1, n - b_src)
            p_src = [0.0] * b_src + [rng.uniform(0.2, 1.5) for _ in range(r_src)] + [0.0] * (n - b_src - r_src)
            q_src = [rng.uniform(4.0, 6.0) for _ in range(b_src)] + [0.0] * (n - b_src)
        else:
            r_src = rng.randint(1, n)
            b_src = rng.randint(0, n)
            p_src = [rng.uniform(0.2, 4.0) for _ in range(r_src)] + [0.0] * (n - r_src)
            rng.shuffle(p_src)
            q_pos = [rng.uniform(0.2, 4.0) for _ in range(b_src)]
            q_neg = [-rng.uniform(0.0, 4.0) for _ in range(n - b_src)]
            q_src = q_pos + q_neg
            rng.shuffle(q_src)

        u = sum(p_src)
        t = sum(q_src)
        S = sum((pi + qi) ** 2 for pi, qi in zip(p_src, q_src))
        b = b_src
        if S < 1e-9:
            continue

        if u + t <= 0:
            ropt_f = 0.0
            subcases_hit["u_plus_t_le_0"] += 1
        elif b > 0 and t > 0 and t * (u + t) >= b * S:
            ropt_f = (u * u) / (S - (t * t) / b)
            subcases_hit["R1"] += 1
        else:
            ropt_f = max(0.0, ((u + t) ** 2) / S - b)
            r_tar = max(1, int(math.ceil(ropt_f - 1e-12)))
            if b > 0 and t > 0 and r_tar > (b * u) / t:
                subcases_hit["R2_caseB"] += 1
            else:
                subcases_hit["R2_caseA"] += 1

        r_target = max(1, int(math.ceil(ropt_f - 1e-12)))
        P_d, Q_d = construct_sharp_diagonal(u, t, S, b)

        r_built = sum(1 for x in P_d if x > 1e-12)
        b_built = sum(1 for x in Q_d if x > 1e-12)
        u_built = sum(P_d)
        t_built = sum(Q_d)
        S_built = sum((pi + qi) ** 2 for pi, qi in zip(P_d, Q_d))

        require(all(x >= -1e-12 for x in P_d), f"built P1 not PSD: {P_d}")
        require(r_built <= r_target, f"built rank {r_built} > target {r_target}")
        require(b_built <= b, f"built n_+(Q) {b_built} > b={b}")
        err = max(abs(u_built - u), abs(t_built - t), abs(S_built - S))
        require(err < 1e-9, f"constructed tuple mismatch err={err}")
        max_err = max(max_err, err)
        realized += 1

    return {
        "exact_rational_equality_witnesses_verified": 4,
        "constructive_integer_sharpness_tuples_verified": realized,
        "max_construction_error": max_err,
        "subcases_covered": subcases_hit,
    }


def main() -> None:
    out = {
        "edge_cases_audit": audit_edge_cases(),
        "complex_hermitian_audit": audit_complex_hermitian(),
        "sharpness_audit": audit_sharpness(),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
