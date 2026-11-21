#!/usr/bin/env python3
"""
Audit 010: Independent Re-Audit of spectral-prover commit dfc8516 (#63) closing AUDIT-015 & AUDIT-016.
Verifies:
  - All 3 #59 non-Hermitian PolyMatrix/RatMatrix exploits are now REJECTED with CertError.
  - Extra adversarial RatMatrix cases (non-real den, zero den, equivalent reduced/unreduced Hermitian
    fractions accepted, non-Hermitian cross-product rejected, callable non-Hermitian interval rejected).
  - Strict canonical lowest-terms R3 rational parser rejects "0/1", "0/5", "3/1", "2/4", "-4/6"
    while accepting canonical "0", "3", "-3", "1/2", "-2/3".
  - fibral_truss_box coordinate consistency & taut/buckled/full certification.

Run under all 3 R4 modes:
  python3 -I -B check_010_spectral_inertia_reaudit.py
  python3 -I -O -B check_010_spectral_inertia_reaudit.py
  python3 -I -B -W error check_010_spectral_inertia_reaudit.py
"""
from __future__ import annotations
import os
from pathlib import Path

from fractions import Fraction
import json
import sys

EXPEDITION_ROOT = Path(os.environ.get("EXPEDITION_ROOT", Path(__file__).resolve().parents[2]))
CHECKS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EXPEDITION_ROOT / "branches/spectral-inertia"))

import spectral_inertia.exact_qi as eqi
import spectral_inertia.box_certifier as bc
from spectral_inertia.examples.fibral_truss_box import run_fibral_truss_validation


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(f"CHECK FAILED: {msg}")


def expect_cert_error(fn, label: str) -> str:
    try:
        fn()
    except eqi.CertError as exc:
        return exc.code
    raise RuntimeError(f"Expected CertError for {label}, but succeeded!")


def main() -> None:
    x = bc.MultiPoly.var(1, 0)
    one = bc.MultiPoly.const(1, 1)
    zero = bc.MultiPoly(1)
    i_poly = bc.MultiPoly.const(1, eqi.Qi(Fraction(0), Fraction(1)))

    codes = {}
    # 1. All 3 original #59 exploits MUST now fail with CertError!
    codes["ex1_polymat_nonreal_diag"] = expect_cert_error(
        lambda: bc.PolyMatrix(1, [[one + i_poly * x, zero], [zero, one]]),
        "PolyMatrix non-real diagonal",
    )
    codes["ex2_polymat_asymmetric_lower"] = expect_cert_error(
        lambda: bc.PolyMatrix(1, [[one, zero], [100 * x, one]]),
        "PolyMatrix asymmetric lower triangle",
    )
    codes["ex3_ratmat_nonreal_diag"] = expect_cert_error(
        lambda: bc.RatMatrix(1, [[one + i_poly * x, zero], [zero, one]], [[one, one], [one, one]]),
        "RatMatrix non-real diagonal",
    )

    # 2. Extra adversarial RatMatrix & callable interval forgeries!
    codes["ex4_ratmat_nonreal_den"] = expect_cert_error(
        lambda: bc.RatMatrix(1, [[one, zero], [zero, one]], [[one + i_poly * x, one], [one, one]]),
        "RatMatrix non-real denominator",
    )
    codes["ex5_ratmat_zero_den"] = expect_cert_error(
        lambda: bc.RatMatrix(1, [[one, zero], [zero, one]], [[zero, one], [one, one]]),
        "RatMatrix identically zero denominator",
    )
    codes["ex6_ratmat_asymmetric_cross"] = expect_cert_error(
        lambda: bc.RatMatrix(
            1,
            [[2 * one, one], [one - x, 2 * one]],
            [[one, one + x], [(one + x) * (one + x), one]],
        ),
        "RatMatrix asymmetric cross-product",
    )
    # Positive control: equivalent Hermitian RatMatrix with unreduced common factor (1+x) on (1,0) MUST work!
    rm_equiv = bc.RatMatrix(
        1,
        [[3 * one, one + i_poly * x], [(one - i_poly * x) * (one + x), 3 * one]],
        [[one, one + x], [(one + x) * (one + x), one]],
    )
    res_rm_ok = bc.certify_hermitian_box(rm_equiv, [(Fraction(-1, 4), Fraction(1, 4))])
    require(
        res_rm_ok.status == "CERTIFIED_CONSTANT_INERTIA" and res_rm_ok.certified_inertia == (2, 0, 0),
        f"Equivalent Hermitian RatMatrix failed: {res_rm_ok.to_summary_dict()}",
    )

    # Callable interval matrix with non-real diagonal or asymmetric off-diagonal MUST raise CertError!
    codes["ex7_callable_nonreal_diag_interval"] = expect_cert_error(
        lambda: bc.certify_hermitian_box(
            lambda pt: [[eqi.ONE, eqi.ZERO], [eqi.ZERO, eqi.ONE]],
            [(Fraction(-1, 2), Fraction(1, 2))],
            eval_box_fn=lambda sub: [
                [bc.QiInterval(bc.QInterval.pt(1), bc.QInterval(Fraction(-1, 10), Fraction(1, 10))), bc.QiInterval.pt(0)],
                [bc.QiInterval.pt(0), bc.QiInterval.pt(1)],
            ],
        ),
        "Callable non-real diagonal interval",
    )
    codes["ex8_callable_asymmetric_interval"] = expect_cert_error(
        lambda: bc.certify_hermitian_box(
            lambda pt: [[eqi.ONE, eqi.ZERO], [eqi.ZERO, eqi.ONE]],
            [(Fraction(-1, 2), Fraction(1, 2))],
            eval_box_fn=lambda sub: [
                [bc.QiInterval.pt(1), bc.QiInterval.pt(0)],
                [bc.QiInterval(bc.QInterval(Fraction(-1, 10), Fraction(1, 10)), bc.QInterval.pt(0)), bc.QiInterval.pt(1)],
            ],
        ),
        "Callable asymmetric off-diagonal interval",
    )

    # 3. Strict canonical lowest-terms R3 rational parser check (AUDIT-016)
    nonreduced_codes = {}
    for bad in ("0/1", "0/5", "3/1", "-3/1", "2/4", "-4/6", "10/5"):
        nonreduced_codes[bad] = expect_cert_error(
            lambda s=bad: eqi.parse_strict_fraction(s), f"nonreduced {bad}"
        )
    for good, exp in [("0", Fraction(0)), ("3", Fraction(3)), ("-3", Fraction(-3)), ("1/2", Fraction(1, 2)), ("-2/3", Fraction(-2, 3))]:
        require(eqi.parse_strict_fraction(good) == exp, f"Valid canonical {good} failed")

    # 4. fibral_truss_box re-check
    truss = run_fibral_truss_validation()
    require(truss["full_box_0p7_1p3_x_0p9_1p5"]["status"] == "SINGULARITY_DETECTED", "Truss full box failed")
    require(truss["taut_subbox_certified_PD"]["status"] == "CERTIFIED_CONSTANT_INERTIA", "Truss taut box failed")
    require(truss["buckled_subbox_certified_PD"]["status"] == "CERTIFIED_CONSTANT_INERTIA", "Truss buckled box failed")

    print(json.dumps({
        "audit_015R_exploits_blocked": codes,
        "audit_015R_equiv_ratmat_certified": res_rm_ok.to_summary_dict()["status"],
        "audit_016R_nonreduced_blocked": nonreduced_codes,
        "fibral_truss_recheck_ok": True,
    }, indent=2))


if __name__ == "__main__":
    main()
