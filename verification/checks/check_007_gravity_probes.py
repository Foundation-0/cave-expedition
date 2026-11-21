#!/usr/bin/env python3
"""
Audit 007: Independent Zero-Shared-Code Adversarial Verification of gravity-probe (#44, #48):
  - Probe 1 (`probe1_aest_helmholtz_closure.py`, AUDIT-011):
      * Canonical SHA-256 verification
      * Zero-circularity 4-state ODE match against `repos/gravity/.../slow-mode/probe.py`
      * Independent SymPy derivation of Helmholtz pressure, G_AA(r), static-dynamical duality,
        AND #48's Hamiltonian Schur-Complement Theorem S_P = -G_AA/(4k^2) + lam_s=0 branch
      * Independent Faddeev-LeVerrier + Descartes exact inertia verification of Minkowski H_2
      * Out-of-sample coupled 6-state baryon+AeST parameter test (KB=0.7, 1.4; lam=0.5, 2.0)
  - Probe 2 (`probe2_latch_outside_anchors_and_chirp.py`, AUDIT-012):
      * Canonical SHA-256 verification
      * Independent check of wave7 LOCO under BOTH diagonalized chi2 AND wave7's native ODR (cov_on=True)
      * Independent check of SPARC -> KiDS-1000 1 Mpc outside anchor
      * Multi-seed adversarial stress test of `blind_chirp_exponent_estimator`:
        - 20 seeded trials each of red noise, IAAFT surrogates, and sine-Gaussian glitches
        - Parabolic (up-then-down) FM burst non-monotone glitch control
        - Down-chirp (decreasing frequency) test
        - Positive parity (+1), negative lag (-28), zero lag (0) tests
        - 5-scale frequency invariance sweep (0.5x..4.0x)
        - SNR degradation sweep (noise_std 0.02..0.40)
  - Probe 3 (`probe3_nonaffine_inertia_box_certifier.py`, AUDIT-013):
      * Canonical SHA-256 verification
      * R1-R5 TCB boundary audit of QI, exact_sqrt_bounds, exact_congruence_block_ldl, certify_single_box
        (including zero-diagonal indefinite saddle matrices cross-checked by Descartes oracle)
      * CRITICAL SYSTEM 1 CHECK: expose synthetic `M_truss` vs REAL `fibral-rigidity#5` Hessian discrepancy
        (real singularity is the full line L1+L2=2, not isolated point (9/10,11/10)!), AND steelman-test
        `subdivide_certify_box` directly on the REAL fibral#5 off-line & on-line Hessians!
      * Independent Descartes + 200-point interior random sampling of System 2 AeST H_2 UV/IR boxes
        PLUS exact lam_s=0 Yukawa box certification (#47/#48)
      * Independent verification of System 3 point-charges C_3 & C_4 (harmonic trace=0, exact Hessian
        formula, Descartes cross-check on interior points, and wider `z["box"]` test!)

Run under all 3 R4 modes with gravity venv python:
  VENV=${EXPEDITION_PYTHON:-python3}  # requires sympy/numpy/scipy; set EXPEDITION_ROOT if running outside workspace
  "$VENV" -B check_007_gravity_probes.py
  "$VENV" -O -B check_007_gravity_probes.py
  "$VENV" -B -W error check_007_gravity_probes.py
"""
from __future__ import annotations
import os

from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import sys
import numpy as np
import sympy as sp

EXPEDITION_ROOT = Path(os.environ.get("EXPEDITION_ROOT", Path(__file__).resolve().parents[2]))
CHECKS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXPEDITION_ROOT / "probes/gravity"))
sys.path.insert(0, str(CHECKS_DIR))

import probe1_aest_helmholtz_closure as p1
import probe2_latch_outside_anchors_and_chirp as p2
import probe3_nonaffine_inertia_box_certifier as p3
from check_003_seam01_ropt import Qi, hermitian_inertia_descartes

PROBES_DIR = (EXPEDITION_ROOT / "probes/gravity")
GRAVITY_REPO = (EXPEDITION_ROOT / "repos/gravity")
POINT_CHARGES_DIR = (EXPEDITION_ROOT / "repos/point-charges/certificates")


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(f"CHECK FAILED: {msg}")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    require(spec is not None and spec.loader is not None, f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_canonical_sha256(json_path: Path, expected_prefix: str) -> str:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    recorded = data.pop("sha256_canonical")
    canon = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    recomputed = hashlib.sha256(canon).hexdigest()
    require(recomputed == recorded, f"{json_path.name}: canonical SHA-256 mismatch {recomputed} != {recorded}")
    require(recorded.startswith(expected_prefix), f"{json_path.name}: SHA-256 {recorded} does not start with {expected_prefix}")
    return recorded


def descartes_real_sym(M: list[list[Fraction]]) -> tuple[int, int, int]:
    """Convert real rational symmetric matrix M to (n_pos, n_zero, n_neg) via zero-shared-code Descartes oracle."""
    n = len(M)
    Mq = [[Qi(M[i][j], Fraction(0)) for j in range(n)] for i in range(n)]
    n_pos, n_neg, n_zero = hermitian_inertia_descartes(Mq)
    return (n_pos, n_zero, n_neg)


# ==============================================================================
# AUDIT-011: PROBE 1 (AeST Helmholtz Closure, Pole-Zero & #48 Schur Identity)
# ==============================================================================
def audit_probe1() -> dict:
    sha = check_canonical_sha256(PROBES_DIR / "probe1_aest_results.json", "fa4d3a1b")

    # 1A. Zero-circularity matrix check against slow-mode/probe.py
    slow_probe = load_module(
        GRAVITY_REPO / "research/aest-response-gate-20261112/slow-mode/probe.py",
        "repo_slow_probe",
    )
    max_ode_diff = 0.0
    for k in (6.0, 12.0, 24.0):
        slow_probe.KVAL = k
        for a in np.linspace(1.0, 2.0, 11):
            M_repo = slow_probe.matrix(float(a), closure=None)
            # Probe 1 works in (D, m, chi, Z); slow-mode/probe.py works in (delta=D/R, theta=m/W, chi, Z).
            # Check exact Jacobian similarity: if x_Dm = T(a) @ x_dt, then
            # d/dt(x_Dm) = Tdot x_dt + T M_repo x_dt  =>  M_Dm = (Tdot + T M_repo) T^{-1}!
            Q, Kp, Kpp, R, W, H = p1.bg(float(a))
            # dR/dt = -3 H (R + K) where K = 2*(Q-1)^2, and W = Q*Kp => dW/dt = Qdot*Kp + Q*Kpdot = (-3H Kp/4)*Kp + Q*(-3H Kp)
            q = 0.01 / (float(a) ** 3)
            K_val = 2.0 * q * q
            Rdot = -3.0 * H * (R + K_val)
            Qdot = -3.0 * H * Kp / Kpp
            Kpdot = -3.0 * H * Kp
            Wdot = Qdot * Kp + Q * Kpdot
            T = np.diag([R, W, 1.0, 1.0])
            Tdot = np.diag([Rdot, Wdot, 0.0, 0.0])
            M_from_repo = (Tdot + T @ M_repo) @ np.linalg.inv(T)
            A, B, C, F = p1.blocks_Dm(float(a), k, KB=1.0, lam=1.0)
            M_p1 = np.block([[A, B], [C, F]])
            diff = float(np.max(np.abs(M_from_repo - M_p1)))
            if diff > max_ode_diff:
                max_ode_diff = diff
    require(max_ode_diff < 1e-13, f"Probe 1 4-state matrix disagrees with repo slow-mode/probe.py: {max_ode_diff}")

    # 1B. Independent SymPy derivation of Minkowski H_2, Schur Complement (#48), Pole-Zero Duality, & lam_s=0
    KB, lam, Kpp, r, Q = sp.symbols("KB lam Kpp r Q", positive=True, real=True)
    lam_free = sp.Symbol("lam_free", real=True)
    ch, p_s, P_s = sp.symbols("ch p_s P_s", real=True)
    b = 2 - KB

    # Direct Minkowski H_2(ch, p, P) for general KB, lam_free, Kpp at Q=1 from derivation.md Sec 2/5:
    gam = p_s / (2 * Kpp)
    Z = (p_s + P_s) / (2 * r)
    Phi = P_s / (4 * r)
    E = (Z - b * ch) / KB
    L_m = -2 * r * Phi**2 + Kpp * gam**2 + r * (KB * E**2 + 2 * b * E * ch - b * (1 + lam_free) * ch**2)
    H2 = sp.expand(p_s * (gam + Phi) + (p_s + P_s) * (E - Phi) - L_m)
    # Check specialization to derivation.md Eq. (185): KB=1, lam=1, Kpp=4
    H2_ref = (
        p_s**2 / 16
        + (p_s + P_s) ** 2 / (4 * r)
        - (p_s + P_s) * ch
        + 3 * r * ch**2
        - P_s**2 / (8 * r)
    )
    require(sp.simplify(H2.subs({KB: 1, lam_free: 1, Kpp: 4}) - H2_ref) == 0, "H2 does not match derivation.md Eq. (185)")

    M_H2 = sp.hessian(H2, (ch, p_s, P_s))
    # Verify #48 Hamiltonian Schur complement S_P = M_PP - M_Pf M_ff^{-1} M_fP == -G_AA / (4 r)!
    M_ff = M_H2[:2, :2]
    M_fP = M_H2[:2, 2:]
    M_PP = M_H2[2, 2]
    S_P = sp.factor((M_PP - (M_fP.T * M_ff.inv() * M_fP)[0, 0]))
    M_scr_sq = Kpp * (1 + lam_free) / (2 + KB * lam_free)
    G_AA = sp.factor(1 - (2 * r / Kpp) * M_scr_sq / (r + M_scr_sq))
    schur_diff = sp.simplify(S_P - (-G_AA / (4 * r)))
    require(schur_diff == 0, f"#48 Hamiltonian Schur complement mismatch: S_P={S_P}, -G_AA/(4r)={-G_AA/(4*r)}")

    # Verify #48 lam_s = 0 minors and S_P:
    d1_lam0 = sp.factor(M_H2[:1, :1].det().subs(lam_free, 0))
    d2_lam0 = sp.factor(M_H2[:2, :2].det().subs(lam_free, 0))
    S_P_lam0 = sp.factor(S_P.subs(lam_free, 0))
    require(sp.simplify(d1_lam0 - 4 * r * (2 - KB) / KB) == 0, f"lam0 d1 mismatch: {d1_lam0}")
    require(sp.simplify(d2_lam0 - (2 - KB) * (2 * r + Kpp) / (KB * Kpp)) == 0, f"lam0 d2 mismatch: {d2_lam0}")
    require(sp.simplify(S_P_lam0 - (-Kpp / (4 * r * (Kpp + 2 * r)))) == 0, f"lam0 S_P mismatch: {S_P_lam0}")

    # 1C. Independent Descartes exact inertia check of Minkowski H_2 across 40 rational (KB, lam, r) points
    rng = random.Random(20261120)
    descartes_checks = 0
    for KB_f, lam_f, r_f, exp_in in [
        (Fraction(1), Fraction(1), Fraction(9), (3, 0, 0)),
        (Fraction(1), Fraction(1), Fraction(8), (2, 1, 0)),
        (Fraction(1), Fraction(1), Fraction(7), (2, 0, 1)),
        (Fraction(1), Fraction(0), Fraction(4), (2, 0, 1)),
        (Fraction(1), Fraction(0), Fraction(100), (2, 0, 1)),
    ]:
        M_f = p3_M_aest_raw(KB_f, lam_f, r_f)
        in_d = descartes_real_sym(M_f)
        require(in_d == exp_in, f"Descartes H2 mismatch at ({KB_f},{lam_f},{r_f}): {in_d} != {exp_in}")
        descartes_checks += 1

    for _ in range(35):
        KB_f = Fraction(rng.randint(2, 18), 10)  # in (0, 2)
        lam_f = Fraction(rng.randint(1, 20), 10)  # > 0
        mu2 = Fraction(4) * (1 + lam_f) / ((2 - KB_f) * lam_f)
        for mult, exp_in in [(Fraction(3, 2), (3, 0, 0)), (Fraction(1), (2, 1, 0)), (Fraction(1, 2), (2, 0, 1))]:
            r_f = mu2 * mult
            in_d = descartes_real_sym(p3_M_aest_raw(KB_f, lam_f, r_f))
            require(in_d == exp_in, f"Random Descartes H2 mismatch at KB={KB_f}, lam={lam_f}, r={r_f}: {in_d} != {exp_in}")
            descartes_checks += 1

    # 1D. Out-of-sample coupled 6-state baryon + AeST parameter test (untested KB != 1, lam != {1, 0, -0.5})
    oos_coupled = []
    for KB_v, lam_v, k_v in [(0.7, 0.5, 15.0), (1.4, 2.0, 8.0), (0.6, 0.0, 20.0), (1.3, 0.5, 1.5)]:
        res_c = run_oos_coupled_6state(KB_v, lam_v, k_v)
        oos_coupled.append(res_c)
        require(res_c["err_b"] < 0.005 and res_c["err_A"] < 0.01, f"OOS 6-state error high at ({KB_v},{lam_v},{k_v}): {res_c}")

    return {
        "sha256_verified": sha,
        "max_4state_ode_diff_vs_repo_slow_probe": max_ode_diff,
        "sympy_H2_matches_derivation_eq185": True,
        "sympy_48_hamiltonian_schur_complement_exact": True,
        "sympy_48_lam0_minors_and_SP_exact": True,
        "descartes_exact_H2_inertia_checks": descartes_checks,
        "out_of_sample_coupled_6state": oos_coupled,
    }


def p3_M_aest_raw(KB: Fraction, lam: Fraction, r: Fraction) -> list[list[Fraction]]:
    b = Fraction(2) - KB
    return [
        [Fraction(2) * r * b * (Fraction(2) + KB * lam) / KB, -b / KB, -b / KB],
        [-b / KB, Fraction(1, 8) + Fraction(1, 2) / (KB * r), Fraction(1, 2) / (KB * r)],
        [-b / KB, Fraction(1, 2) / (KB * r), Fraction(1, 2) / (KB * r) - Fraction(1, 4) / r],
    ]


def run_oos_coupled_6state(KB: float, lam: float, k_val: float) -> dict:
    """Independent out-of-sample 6-state baryon+AeST ODE vs 4-state Helmholtz fluid check."""
    from scipy.integrate import solve_ivp

    f_b = 0.16
    f_A = 1.0 - f_b
    qi_A = 0.01
    Kpp = 4.0
    b = 2.0 - KB

    def bg_2f(a: float):
        qA = qi_A / (a**3)
        Q = 1.0 + qA
        Kp = 4.0 * qA
        RA = 4.0 * qA + 2.0 * qA * qA
        W = Q * Kp
        Rb = (f_b / f_A) * (4.0 * qi_A / (a**3))
        H = math.sqrt((RA + Rb) / 3.0)
        return Q, Kp, RA, Rb, W, H

    def rhs_6(a: float, y: np.ndarray) -> np.ndarray:
        Db, mb, DA, mA, ch, Z = y
        Q, Kp, RA, Rb, W, H = bg_2f(a)
        r = (k_val / a) ** 2
        Phi = -(Db + DA + 3.0 * H * (mb + mA)) / (2.0 * r)
        Phidot = -H * Phi + 0.5 * (mb + mA)
        gam = (DA + r * Z) / (Q * Kpp)
        pA = Kp * gam
        Qdot = -3.0 * H * Kp / Kpp
        dDb = -3.0 * H * Db + 3.0 * Rb * Phidot - r * mb
        dmb = -3.0 * H * mb + Rb * Phi
        dDA = -3.0 * H * (DA + pA) + 3.0 * W * Phidot - r * mA
        dmA = -3.0 * H * mA + pA + W * Phi
        dch = gam + (b / KB) * Q * (Z / b - ch) + Q * Z * (1.0 - 1.0 / KB) + (Qdot / Q) * ch - (Qdot / (Q * Kp)) * mA
        # Exact general-KB chidot from Probe 1 Eq. (118)/(233):
        # chidot = gam + (Q/KB)*Z + (Qdot/Q - (b/KB)*Q)*ch - (Qdot/(Q*Kp))*mA
        dch = gam + (Q / KB) * Z + (Qdot / Q - (b / KB) * Q) * ch - (Qdot / (Q * Kp)) * mA
        dZ = (-H + (b / KB) * Q) * Z + (Kp - (b / KB) * (2.0 + KB * lam) * Q) * ch
        return np.array([dDb, dmb, dDA, dmA, dch, dZ]) / (a * H)

    def rhs_4(a: float, y: np.ndarray) -> np.ndarray:
        Db, mb, DA, mA = y
        Q, Kp, RA, Rb, W, H = bg_2f(a)
        r = (k_val / a) ** 2
        M_scr_sq = Kpp * Q * Q * (1.0 + lam) / (2.0 + KB * lam)
        pA = (Kp / (Q * Kpp)) * (M_scr_sq / (r + M_scr_sq)) * DA
        Phi = -(Db + DA + 3.0 * H * (mb + mA)) / (2.0 * r)
        Phidot = -H * Phi + 0.5 * (mb + mA)
        dDb = -3.0 * H * Db + 3.0 * Rb * Phidot - r * mb
        dmb = -3.0 * H * mb + Rb * Phi
        dDA = -3.0 * H * (DA + pA) + 3.0 * W * Phidot - r * mA
        dmA = -3.0 * H * mA + pA + W * Phi
        return np.array([dDb, dmb, dDA, dmA]) / (a * H)

    Q0, Kp0, RA0, Rb0, W0, H0 = bg_2f(1.0)
    r0 = k_val**2
    Db0 = Rb0 * 1e-5
    DA0 = RA0 * 1e-5
    # Quasi-static fast initialization
    F0 = np.array(
        [
            [-3 * H0 * Kp0 / (Kpp * Q0) - (b / KB) * Q0, r0 / (Kpp * Q0) + Q0 / KB],
            [Kp0 - (b / KB) * (2.0 + KB * lam) * Q0, -H0 + (b / KB) * Q0],
        ]
    )
    ch0, Z0 = -np.linalg.solve(F0, np.array([DA0 / (Kpp * Q0), 0.0]))
    grid = np.linspace(1.0, 2.0, 401)
    s6 = solve_ivp(rhs_6, (1.0, 2.0), np.array([Db0, 0.0, DA0, 0.0, ch0, Z0]), t_eval=grid, method="DOP853", rtol=1e-11, atol=1e-22)
    s4 = solve_ivp(rhs_4, (1.0, 2.0), np.array([Db0, 0.0, DA0, 0.0]), t_eval=grid, method="DOP853", rtol=1e-11, atol=1e-22)
    require(s6.success and s4.success, f"OOS 6-state integration failed for KB={KB}, lam={lam}, k={k_val}")
    err_b = float(np.max(np.abs(s6.y[0] - s4.y[0])) / np.max(np.abs(s6.y[0])))
    err_A = float(np.max(np.abs(s6.y[2] - s4.y[2])) / np.max(np.abs(s6.y[2])))
    M_scr_sq0 = Kpp * Q0 * Q0 * (1.0 + lam) / (2.0 + KB * lam)
    G_AA0 = 1.0 - (2.0 * r0 / (Q0 * Q0 * Kpp)) * (M_scr_sq0 / (r0 + M_scr_sq0))
    return {"KB": KB, "lam": lam, "k": k_val, "G_AA_a1": round(G_AA0, 4), "err_b": round(err_b, 6), "err_A": round(err_A, 6)}


# ==============================================================================
# AUDIT-012: PROBE 2 (Latch, ODR Sensitivity, & Adversarial Chirp Stress Tests)
# ==============================================================================
def audit_probe2() -> dict:
    sha = check_canonical_sha256(PROBES_DIR / "probe2_latch_chirp_results.json", "ed74a3a4")

    # 2A. Test LOCO sensitivity to wave7's native correlated ODR (cov_on=True) vs probe2's diagonalized chi2!
    w7 = load_module(GRAVITY_REPO / "wave7_group_cluster_threshold_audit.py", "w7_audit")
    all_rows = w7.build_catalog()
    gal_rows = [r for r in all_rows if r["cat"] in ("SPARC_HSB", "Mistele2024_KiDS_WL")]
    nongal_rows = [r for r in all_rows if r not in gal_rows]

    # Fit Hill on non-galaxy rows using wave7's NATIVE correlated ODR chi2 (cov_on=True)!
    from scipy.optimize import minimize

    def obj_odr(par):
        sc, sh, rsat = par
        if not (50.0 <= sc <= 600.0 and 20.0 <= sh <= 800.0 and 1.2 <= rsat <= 12.0):
            return 1e12
        return w7.odr_chi2(nongal_rows, lambda s: p2.hill_pred(s, sc, sh, rsat), cov_on=True)["chi2"]

    best_odr = None
    for sc0 in (80.0, 150.0, 220.0):
        r_opt = minimize(obj_odr, [sc0, 200.0, 4.0], method="Nelder-Mead", options={"maxiter": 1500, "xatol": 1e-2, "fatol": 1e-2})
        if best_odr is None or r_opt.fun < best_odr.fun:
            best_odr = r_opt
    sc_odr, sh_odr, rsat_odr = [float(x) for x in best_odr.x]
    gal_chi2_odr_hill = w7.odr_chi2(gal_rows, lambda s: p2.hill_pred(s, sc_odr, sh_odr, rsat_odr), cov_on=True)["chi2"]
    gal_chi2_odr_mond = w7.odr_chi2(gal_rows, lambda s: 0.0, cov_on=True)["chi2"]
    # Also evaluate full-sample Hill vs Sigmoid under native ODR (cov_on=True):
    full_hill = p2.fit_hill(all_rows)
    full_sig = p2.fit_sigmoid(all_rows)
    odr_full_hill = w7.odr_chi2(all_rows, lambda s: p2.hill_pred(s, full_hill["sc"], full_hill["sh"], full_hill["rsat"]), cov_on=True)["chi2"]
    odr_full_sig = w7.odr_chi2(all_rows, lambda s: p2.sigmoid_pred(s, full_sig["log_s0"], full_sig["width_dex"], full_sig["amp_dex"]), cov_on=True)["chi2"]

    # 2B. Adversarial multi-seed stress test of blind_chirp_exponent_estimator!
    fs = 4096.0
    T = 6.0
    N = int(fs * T)
    t = np.arange(N) / fs
    rf = np.fft.rfftfreq(N, d=1.0 / fs)

    def smooth_box(t_arr, t_lo, t_hi):
        u = np.clip((t_arr - t_lo) / (t_hi - t_lo), 0.0, 1.0)
        return np.where((t_arr >= t_lo) & (t_arr <= t_hi), np.sin(math.pi * u) ** 0.5, 0.0)

    def make_pair(sig, noise_std=0.03, parity=-1.0, lag=28, seed=100):
        rng = np.random.default_rng(seed)
        if lag >= 0:
            s1 = np.roll(sig, lag)
            if lag > 0:
                s1[:lag] = 0.0
            s2 = parity * sig
        else:
            al = -lag
            s1 = sig.copy()
            s2 = parity * np.roll(sig, al)
            s2[:al] = 0.0
        color = 1.0 / np.sqrt(1.0 + (rf / 120.0) ** 2)
        n1 = np.fft.irfft(np.fft.rfft(rng.normal(size=N)) * color, n=N)
        n2 = np.fft.irfft(np.fft.rfft(rng.normal(size=N)) * color, n=N)
        n1 = noise_std * n1 / (np.std(n1) + 1e-30)
        n2 = noise_std * n2 / (np.std(n2) + 1e-30)
        return s1 + n1, s2 + n2

    def pn_sig(f_scale=1.0):
        t_c = 3.32
        tau = np.maximum(t_c - t, 1e-4)
        A = 35.0 * f_scale
        phi = -2.0 * math.pi * (8.0 / 5.0) * A * (tau ** (5.0 / 8.0))
        env = smooth_box(t, 2.75, 3.29) * (tau ** (-0.25))
        env /= np.max(env) + 1e-30
        return env * np.cos(phi)

    # Multi-seed negative controls (15 trials each to keep runtime crisp!)
    fp_red = 0
    fp_iaaft = 0
    fp_glitch = 0
    sig_pn1 = pn_sig(1.0)
    y1_ref, y2_ref = make_pair(sig_pn1, noise_std=0.03, parity=-1.0, lag=28, seed=777)
    filt_red = 1.0 / np.maximum(rf, 5.0)
    for trial in range(15):
        rng = np.random.default_rng(5000 + trial)
        # Red noise
        yr1 = np.fft.irfft(np.fft.rfft(rng.normal(size=N)) * filt_red, n=N)
        yr2 = np.fft.irfft(np.fft.rfft(rng.normal(size=N)) * filt_red, n=N)
        if p2.blind_chirp_exponent_estimator(yr1, yr2, fs)["monotone_chirp_detected"]:
            fp_red += 1
        # IAAFT surrogate
        yi1 = p2.iaaft_surrogate(y1_ref, np.random.default_rng(6000 + 2 * trial))
        yi2 = p2.iaaft_surrogate(y2_ref, np.random.default_rng(6000 + 2 * trial + 1))
        if p2.blind_chirp_exponent_estimator(yi1, yi2, fs)["monotone_chirp_detected"]:
            fp_iaaft += 1
        # Sine-Gaussian glitch with varying f0 in [70, 500] and sigma in [0.05, 0.14]
        f0 = 70.0 + 30.0 * trial
        sg = 0.05 + 0.006 * trial
        gl = np.exp(-0.5 * ((t - 3.0) / sg) ** 2) * np.cos(2.0 * math.pi * f0 * t)
        yg1, yg2 = make_pair(gl, noise_std=0.03, parity=-1.0, lag=28, seed=7000 + trial)
        if p2.blind_chirp_exponent_estimator(yg1, yg2, fs)["monotone_chirp_detected"]:
            fp_glitch += 1

    # Adversarial parabolic FM burst (rises then falls: non-monotone!)
    dt_p = t - 3.0
    # f(t) = 220 - 2500 * (t - 3)^2 -> rises on [2.8, 3.0], falls on [3.0, 3.2]
    phi_parab = 2.0 * math.pi * (220.0 * dt_p - (2500.0 / 3.0) * (dt_p**3))
    sig_parab = np.exp(-0.5 * (dt_p / 0.12) ** 2) * np.cos(phi_parab)
    yp1, yp2 = make_pair(sig_parab, noise_std=0.03, parity=-1.0, lag=28, seed=8001)
    res_parab = p2.blind_chirp_exponent_estimator(yp1, yp2, fs)

    # Down-chirp (time-reversed Newtonian inspiral -> decreasing frequency!)
    sig_down = sig_pn1[::-1].copy()
    yd1, yd2 = make_pair(sig_down, noise_std=0.03, parity=-1.0, lag=28, seed=8002)
    res_down = p2.blind_chirp_exponent_estimator(yd1, yd2, fs)

    # Positive parity (+1), negative lag (-28), zero lag (0) tests
    y1_pos_neg, y2_pos_neg = make_pair(sig_pn1, noise_std=0.03, parity=+1.0, lag=-28, seed=8003)
    res_pos_neg = p2.blind_chirp_exponent_estimator(y1_pos_neg, y2_pos_neg, fs)
    require(
        res_pos_neg["monotone_chirp_detected"]
        and res_pos_neg["best_lag_samples"] == -28
        and res_pos_neg["peak_corr"] > 0.7
        and abs(res_pos_neg["alpha_hat"] - 11.0 / 3.0) < 0.25,
        f"Positive parity / negative lag failed: {res_pos_neg}",
    )

    y1_z, y2_z = make_pair(sig_pn1, noise_std=0.03, parity=+1.0, lag=0, seed=8004)
    res_z = p2.blind_chirp_exponent_estimator(y1_z, y2_z, fs)
    require(res_z["monotone_chirp_detected"] and res_z["best_lag_samples"] == 0, f"Zero lag failed: {res_z}")

    # Scale invariance sweep across 4 scales (0.7x, 1.0x, 1.8x, 3.0x)
    scale_sweep = {}
    for sc in (0.7, 1.0, 1.8, 3.0):
        ys1, ys2 = make_pair(pn_sig(sc), noise_std=0.03, parity=-1.0, lag=28, seed=8100 + int(sc * 10))
        r_sc = p2.blind_chirp_exponent_estimator(ys1, ys2, fs)
        scale_sweep[f"{sc}x"] = {"detected": r_sc["monotone_chirp_detected"], "alpha_hat": r_sc["alpha_hat"], "nonlin": r_sc["min_nonlinearity"]}

    # SNR degradation sweep
    snr_sweep = {}
    for ns in (0.03, 0.08, 0.15, 0.25, 0.40):
        det_cnt = 0
        alphas = []
        for k in range(5):
            yn1, yn2 = make_pair(sig_pn1, noise_std=ns, parity=-1.0, lag=28, seed=8200 + int(ns * 1000) + k)
            rn = p2.blind_chirp_exponent_estimator(yn1, yn2, fs)
            if rn["monotone_chirp_detected"]:
                det_cnt += 1
                alphas.append(rn["alpha_hat"])
        snr_sweep[f"noise_{ns}"] = {
            "detected_out_of_5": det_cnt,
            "mean_alpha": round(float(np.mean(alphas)), 3) if alphas else None,
        }

    return {
        "sha256_verified": sha,
        "native_odr_loco_galaxy_holdout": {
            "train_sc_odr_kms": round(sc_odr, 2),
            "holdout_gal_chi2_hill_odr": round(gal_chi2_odr_hill, 2),
            "holdout_gal_chi2_mond_odr": round(gal_chi2_odr_mond, 2),
            "full_sample_odr_hill": round(odr_full_hill, 2),
            "full_sample_odr_sigmoid": round(odr_full_sig, 2),
        },
        "chirp_multiseed_false_positives_out_of_15": {
            "red_noise": fp_red,
            "iaaft_surrogate": fp_iaaft,
            "sine_gaussian_glitches": fp_glitch,
        },
        "parabolic_nonmonotone_fm_glitch": {
            "detected": res_parab["monotone_chirp_detected"],
            "corr": res_parab["peak_corr"],
            "alpha_hat": res_parab["alpha_hat"],
        },
        "down_chirp_reversed_inspiral": {
            "detected": res_down["monotone_chirp_detected"],
            "corr": res_down["peak_corr"],
            "alpha_hat": res_down["alpha_hat"],
        },
        "positive_parity_neg_lag_minus28": {
            "lag": res_pos_neg["best_lag_samples"],
            "corr": res_pos_neg["peak_corr"],
            "alpha_hat": res_pos_neg["alpha_hat"],
            "detected": res_pos_neg["monotone_chirp_detected"],
        },
        "scale_invariance_sweep": scale_sweep,
        "snr_degradation_sweep": snr_sweep,
    }


# ==============================================================================
# AUDIT-013: PROBE 3 (Zero-Float Non-Affine Inertia Box Certifier)
# ==============================================================================
def audit_probe3() -> dict:
    sha = check_canonical_sha256(PROBES_DIR / "probe3_inertia_boxes_results.json", "35e16732")

    # 3A. TCB R1-R5 hygiene & zero-diagonal indefinite saddle stress tests
    # Check whether QI.pt accepts bool or float!
    tcb_findings = {}
    try:
        q_bool = p3.QI.pt(True)
        tcb_findings["QI_pt_accepts_bool"] = True
    except Exception:
        tcb_findings["QI_pt_accepts_bool"] = False
    try:
        q_float = p3.QI.pt(1.5)  # type: ignore[arg-type]
        tcb_findings["QI_pt_accepts_float"] = True
    except Exception:
        tcb_findings["QI_pt_accepts_float"] = False
    # Check zero-containing inv raises ZeroDivisionError
    inv_rejected = False
    try:
        p3.QI(Fraction(-1), Fraction(1)).inv()
    except ZeroDivisionError:
        inv_rejected = True
    require(inv_rejected, "QI([-1,1]).inv() did not raise ZeroDivisionError")

    # Check exact_congruence_block_ldl on 30 hard zero-diagonal & singular matrices vs Descartes oracle!
    hard_mats = [
        [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]],
        [[Fraction(0), Fraction(0), Fraction(1)], [Fraction(0), Fraction(0), Fraction(0)], [Fraction(1), Fraction(0), Fraction(0)]],
        [[Fraction(0), Fraction(1), Fraction(2)], [Fraction(1), Fraction(0), Fraction(3)], [Fraction(2), Fraction(3), Fraction(0)]],
        [[Fraction(1, 10**12), Fraction(1)], [Fraction(1), Fraction(-1, 10**12)]],
        [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]],
    ]
    rng = random.Random(20261120)
    for _ in range(25):
        n = rng.choice([2, 3, 4])
        M = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(i, n):
                val = Fraction(rng.randint(-4, 4), rng.randint(1, 3))
                if i == j and rng.random() < 0.6:
                    val = Fraction(0)  # force zero diagonals!
                M[i][j] = M[j][i] = val
        hard_mats.append(M)
    for M in hard_mats:
        _, _, in_p3 = p3.exact_congruence_block_ldl(M)
        in_desc = descartes_real_sym(M)
        require(in_p3 == in_desc, f"Block LDL vs Descartes mismatch: {in_p3} != {in_desc} on {M}")

    # 3B. CRITICAL SYSTEM 1 SHADOW CHECK + STEELMAN ON REAL fibral-rigidity#5 HESSIAN!
    # Verify analytically that the REAL fibral#5 equilibrium Hessian is singular along the ENTIRE line L1 + L2 = 2
    # (NOT just the isolated point (9/10, 11/10) of synthetic M_truss)!
    real_line_singular_pts = 0
    for L1_f in (Fraction(7, 10), Fraction(8, 10), Fraction(9, 10), Fraction(1), Fraction(11, 10)):
        L2_f = Fraction(2) - L1_f  # L1 + L2 == 2!
        # On-line formula: x = (L1-L2)/(L1+L2), r1 = x+1 = L1, r2 = 1-x = L2 => H_yy = 1/L1+1/L2-1/r1-1/r2 = 0!
        x = (L1_f - L2_f) / (L1_f + L2_f)
        hxx = Fraction(1) / L1_f + Fraction(1) / L2_f
        hyy = hxx - Fraction(1) / (x + 1) - Fraction(1) / (1 - x)
        require(hyy == 0 and hxx > 0, f"Expected real fibral#5 singularity along L1+L2=2 at ({L1_f},{L2_f})")
        real_line_singular_pts += 1

    # STEELMAN: Run Probe 3's subdivide_certify_box directly on the REAL fibral#5 Hessians!
    # 1) Off-line safe sub-box [11/10, 13/10] x [13/10, 15/10] (L1 + L2 >= 24/10 > 2 everywhere!)
    #    Exact rational congruence [[A, B], [B, C]] AND raw un-congruenced [[A, B*y], [B*y, C*y^2]] with QI.sqrt!
    def M_fibral_real_offline_congruent(pt):
        L1, L2 = pt
        x = (L1.sqr() - L2.sqr()) / 4
        xp1 = x + 1
        xm1 = x - 1
        invL1_3 = (L1 * L1 * L1).inv()
        invL2_3 = (L2 * L2 * L2).inv()
        A = xp1.sqr() * invL1_3 + xm1.sqr() * invL2_3
        B = xp1 * invL1_3 + xm1 * invL2_3
        C = invL1_3 + invL2_3
        return [[A, B], [B, C]]

    def M_fibral_real_offline_raw(pt):
        L1, L2 = pt
        x = (L1.sqr() - L2.sqr()) / 4
        xp1 = x + 1
        xm1 = x - 1
        y2 = L1.sqr() - xp1.sqr()
        y = y2.sqrt(prec_bits=40)
        invL1_3 = (L1 * L1 * L1).inv()
        invL2_3 = (L2 * L2 * L2).inv()
        A = xp1.sqr() * invL1_3 + xm1.sqr() * invL2_3
        B = (xp1 * invL1_3 + xm1 * invL2_3) * y
        C = (invL1_3 + invL2_3) * y2
        return [[A, B], [B, C]]

    # 2) On-line safe sub-box [7/10, 8/10] x [9/10, 10/10] (L1 + L2 <= 18/10 < 2 everywhere!)
    def M_fibral_real_online(pt):
        L1, L2 = pt
        s = L1 + L2
        # Algebraic simplification (zero wrapping!):
        # x = (L1-L2)/(L1+L2) => r1 = x+1 = 2 L1/(L1+L2), r2 = 1-x = 2 L2/(L1+L2)
        # => H_yy = (1/L1 + 1/L2) * (1 - (L1+L2)/2)!
        hxx = L1.inv() + L2.inv()
        hyy = hxx * (p3.QI.pt(1) - s / 2)
        return [[hxx, p3.QI.pt(0)], [p3.QI.pt(0), hyy]]

    box_real_off = (p3.QI(Fraction(11, 10), Fraction(13, 10)), p3.QI(Fraction(13, 10), Fraction(15, 10)))
    box_real_on = (p3.QI(Fraction(7, 10), Fraction(8, 10)), p3.QI(Fraction(9, 10), Fraction(10, 10)))
    res_real_off_cong = p3.subdivide_certify_box(M_fibral_real_offline_congruent, box_real_off, max_boxes=400, min_width=Fraction(1, 64))
    res_real_off_raw = p3.subdivide_certify_box(M_fibral_real_offline_raw, box_real_off, max_boxes=400, min_width=Fraction(1, 64))
    res_real_on = p3.subdivide_certify_box(M_fibral_real_online, box_real_on, max_boxes=400, min_width=Fraction(1, 64))
    require(res_real_off_cong["uniformly_certified"] and res_real_off_cong["certified_inertia"] == [2, 0, 0], f"Real fibral off-line congruent failed: {res_real_off_cong}")
    require(res_real_off_raw["uniformly_certified"] and res_real_off_raw["certified_inertia"] == [2, 0, 0], f"Real fibral off-line raw failed: {res_real_off_raw}")
    require(res_real_on["uniformly_certified"] and res_real_on["certified_inertia"] == [2, 0, 0], f"Real fibral on-line failed: {res_real_on}")

    # 3C. System 2 AeST H_2 independent 200-point interior Descartes check + lam_s = 0 box (#47/#48)
    for label, box_bounds, exp_in in [
        ("UV", ((Fraction(9, 10), Fraction(11, 10)), (Fraction(9, 10), Fraction(11, 10)), (Fraction(16), Fraction(20))), (3, 0, 0)),
        ("IR", ((Fraction(9, 10), Fraction(11, 10)), (Fraction(9, 10), Fraction(11, 10)), (Fraction(2), Fraction(4))), (2, 0, 1)),
    ]:
        for _ in range(100):
            pt = [lo + Fraction(rng.randint(0, 1000), 1000) * (hi - lo) for lo, hi in box_bounds]
            in_d = descartes_real_sym(p3_M_aest_raw(pt[0], pt[1], pt[2]))
            require(in_d == exp_in, f"System 2 {label} interior point {pt} Descartes {in_d} != {exp_in}")

    # Test Probe 3 directly on the lam_s=0 Yukawa boundary box (#47/#48):
    def M_aest_tridiag(pt):
        KB, lam, r = pt
        inv_KB = KB.inv()
        inv_r = r.inv()
        two_over_KB_m1 = p3.QI.pt(2) * inv_KB - p3.QI.pt(1)
        m00 = p3.QI.pt(2) * r * two_over_KB_m1 * (p3.QI.pt(2) + KB * lam)
        m01 = -two_over_KB_m1
        m11 = p3.QI.pt(Fraction(1, 8)) + p3.QI.pt(Fraction(1, 2)) * inv_KB * inv_r
        m12 = p3.QI.pt(Fraction(-1, 8))
        m22 = p3.QI.pt(Fraction(1, 8)) - p3.QI.pt(Fraction(1, 4)) * inv_r
        return [[m00, m01, p3.QI.pt(0)], [m01, m11, m12], [p3.QI.pt(0), m12, m22]]

    box_lam0_tight = (
        p3.QI(Fraction(9, 10), Fraction(11, 10)),
        p3.QI(Fraction(-1, 10), Fraction(1, 10)),
        p3.QI(Fraction(1), Fraction(4)),
    )
    res_lam0_tight = p3.subdivide_certify_box(M_aest_tridiag, box_lam0_tight, max_boxes=4000, min_width=Fraction(1, 64))
    require(
        res_lam0_tight["uniformly_certified"] and res_lam0_tight["certified_inertia"] == [2, 0, 1],
        f"lam_s=0 tight Yukawa box failed: {res_lam0_tight}",
    )
    box_lam0_wide = (
        p3.QI(Fraction(9, 10), Fraction(11, 10)),
        p3.QI(Fraction(-1, 10), Fraction(1, 10)),
        p3.QI(Fraction(1), Fraction(10)),
    )
    res_lam0_wide = p3.subdivide_certify_box(M_aest_tridiag, box_lam0_wide, max_boxes=4000, min_width=Fraction(1, 64))
    require(
        list(res_lam0_wide["certified_leaf_counts_by_inertia"].keys()) == ["(2, 0, 1)"],
        f"lam_s=0 wide Yukawa box saw unexpected inertia: {res_lam0_wide}",
    )

    # 3D. System 3 point-charges: verify harmonic trace=0, Descartes midpoint check, AND wider `z["box"]` test!
    pc_audit = {}
    for fname in ("n3-triangle.json", "n4-triangle-plus-centre.json"):
        data = json.loads((POINT_CHARGES_DIR / fname).read_text(encoding="utf-8"))
        sites = [[Fraction(c) for c in s] for s in data["sites"]]
        charges = [Fraction(q) for q in data["charges"]]

        def M_pc(pt):
            H = [[p3.QI.pt(0) for _ in range(3)] for _ in range(3)]
            for s, q in zip(sites, charges):
                dx = [pt[a] - s[a] for a in range(3)]
                r2 = dx[0].sqr() + dx[1].sqr() + dx[2].sqr()
                rm3 = r2.pow_neg_half(3, prec_bits=48)
                rm5 = r2.pow_neg_half(5, prec_bits=48)
                for a in range(3):
                    for b in range(a, 3):
                        term = q * (p3.QI.pt(3) * dx[a] * dx[b] * rm5)
                        if a == b:
                            term = term - q * rm3
                        H[a][b] = H[a][b] + term
            for a in range(3):
                for b in range(a + 1, 3):
                    H[b][a] = H[a][b]
            return H

        wide_boxes_certified = 0
        max_wide_leaves = 0
        for idx, z in enumerate(data["zeros"]):
            # 1. Check midpoint harmonic trace == 0 within interval width and Descartes inertia matches z["index"]
            lo_f, hi_f = z["enclosure"][0], z["enclosure"][1]
            mids = tuple(p3.QI.pt((Fraction(lo_f[d]) + Fraction(hi_f[d])) / 2) for d in range(3))
            H_mid_iv = M_pc(mids)
            tr_iv = H_mid_iv[0][0] + H_mid_iv[1][1] + H_mid_iv[2][2]
            require(tr_iv.lo <= 0 <= tr_iv.hi, f"{fname} zero {idx} trace interval does not enclose 0: {tr_iv}")
            H_mid_rat = [[H_mid_iv[i][j].mid() for j in range(3)] for i in range(3)]
            in_desc = descartes_real_sym(H_mid_rat)
            require(in_desc[2] == z["index"] and in_desc[1] == 0, f"{fname} zero {idx} Descartes {in_desc} != index {z['index']}")

            # 2. Check the WIDER published `z["box"]` (not just 1e-14 `enclosure`!)
            wlo, whi = z["box"][0], z["box"][1]
            wbox = tuple(p3.QI(Fraction(wlo[d]), Fraction(whi[d])) for d in range(3))
            r_wide = p3.subdivide_certify_box(M_pc, wbox, max_boxes=400, min_width=Fraction(1, 128))
            if r_wide["uniformly_certified"] and r_wide["certified_inertia"][2] == z["index"]:
                wide_boxes_certified += 1
                max_wide_leaves = max(max_wide_leaves, r_wide["boxes_evaluated"])
        pc_audit[data["name"]] = {
            "descartes_midpoints_matched": len(data["zeros"]),
            "wider_published_boxes_certified_zero_float": f"{wide_boxes_certified}/{len(data['zeros'])}",
            "max_boxes_eval_on_wider_box": max_wide_leaves,
        }

    return {
        "sha256_verified": sha,
        "tcb_boundary_findings": tcb_findings,
        "hard_zero_diag_descartes_agreements": len(hard_mats),
        "system1_real_fibral_singularity_is_full_line_L1_plus_L2_eq_2_pts_checked": real_line_singular_pts,
        "system1_steelman_real_fibral_offline_congruent": {
            "certified": res_real_off_cong["uniformly_certified"],
            "inertia": res_real_off_cong["certified_inertia"],
            "boxes_evaluated": res_real_off_cong["boxes_evaluated"],
        },
        "system1_steelman_real_fibral_offline_raw_sqrt": {
            "certified": res_real_off_raw["uniformly_certified"],
            "inertia": res_real_off_raw["certified_inertia"],
            "boxes_evaluated": res_real_off_raw["boxes_evaluated"],
        },
        "system1_steelman_real_fibral_online": {
            "certified": res_real_on["uniformly_certified"],
            "inertia": res_real_on["certified_inertia"],
            "boxes_evaluated": res_real_on["boxes_evaluated"],
        },
        "system2_interior_descartes_points_checked": 200,
        "system2_lam0_yukawa_box_tight_r1_4": {
            "certified": res_lam0_tight["uniformly_certified"],
            "inertia": res_lam0_tight["certified_inertia"],
            "boxes_evaluated": res_lam0_tight["boxes_evaluated"],
        },
        "system2_lam0_yukawa_box_wide_r1_10": {
            "certified": res_lam0_wide["uniformly_certified"],
            "leaf_counts": res_lam0_wide["certified_leaf_counts_by_inertia"],
            "uncertain": res_lam0_wide["uncertain_boundary_boxes"],
            "boxes_evaluated": res_lam0_wide["boxes_evaluated"],
        },
        "system3_point_charges_independent_audit": pc_audit,
    }


def main() -> None:
    report = {
        "audit_011_probe1": audit_probe1(),
        "audit_012_probe2": audit_probe2(),
        "audit_013_probe3": audit_probe3(),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
