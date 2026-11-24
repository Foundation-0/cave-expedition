#!/usr/bin/env python3
"""
R5 Mutation-Hardened Independent Test Suite for AUDIT-085
(unification_bridge_audit.py).

Runs cleanly under: python3 -I -O -B -W error test_r5_unification_bridge.py
Zero floats. Zero bare asserts. Pure Python 3 stdlib only.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

# Ensure local module import works under python3 -I (isolated mode)
for _p in (str(Path.cwd()), str(Path(__file__).resolve().parent)):
    if _p not in sys.path:
        sys.path.append(_p)

import unification_bridge_audit as uba


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(f"TEST_FAIL: {msg}")


def expect_audit_error(fn: Callable[[], Any], expected_code: str, label: str) -> None:
    try:
        fn()
    except uba.AuditError as exc:
        check(
            exc.code == expected_code,
            f"{label}: expected code {expected_code}, got {exc.code} ({exc})",
        )
        return
    raise RuntimeError(f"TEST_FAIL: {label} did not raise AuditError({expected_code})")


def test_exact_validators_and_poly_ring() -> None:
    # Exact type guards
    check(uba.as_exact_int(3, "x") == 3, "as_exact_int accepts int")
    expect_audit_error(lambda: uba.as_exact_int(True, "x"), "ERR_NON_EXACT_INT", "reject bool int")
    expect_audit_error(lambda: uba.as_exact_int("3", "x"), "ERR_NON_EXACT_INT", "reject str int")

    check(uba.as_exact_fraction(Fraction(2, 3), "x") == Fraction(2, 3), "as_exact_fraction Fraction")
    check(uba.as_exact_fraction(5, "x") == Fraction(5), "as_exact_fraction int")
    expect_audit_error(
        lambda: uba.as_exact_fraction(False, "x"), "ERR_NON_EXACT_RATIONAL", "reject bool frac"
    )
    expect_audit_error(
        lambda: uba.as_exact_fraction("1/2", "x"), "ERR_NON_EXACT_RATIONAL", "reject str frac"
    )

    check(uba.as_exact_bool(True, "b") is True, "as_exact_bool True")
    check(uba.as_exact_bool(False, "b") is False, "as_exact_bool False")
    expect_audit_error(lambda: uba.as_exact_bool(1, "b"), "ERR_INVALID_BOOL", "reject int bool")

    # Polynomial ring arithmetic & edge cases
    p0 = uba.poly_from_terms({})
    check(p0 == [], "zero poly empty")
    check(uba.poly_val(p0) is None, "zero poly val is None")
    check(uba.poly_lead(p0) == Fraction(0), "zero poly lead is 0")
    check(uba.poly_deg(p0) == -1, "zero poly deg is -1")
    check(uba.poly_coeff_at(p0, 0) == Fraction(0), "coeff_at empty is 0")
    check(uba.poly_coeff_at([Fraction(2)], -1) == Fraction(0), "coeff_at neg deg is 0")

    expect_audit_error(
        lambda: uba.poly_from_terms("bad"), "ERR_INVALID_POLY", "reject non-dict poly"
    )
    expect_audit_error(
        lambda: uba.poly_from_terms({-1: 1}), "ERR_NEGATIVE_DEGREE", "reject negative degree"
    )

    p1 = uba.poly_from_terms({0: 1, 2: Fraction(3, 2)})
    p2 = uba.poly_from_terms({1: -1, 2: Fraction(-3, 2)})
    p_sum = uba.poly_add(p1, p2)
    check(p_sum == [Fraction(1), Fraction(-1)], "poly_add trims leading cancel")
    check(uba.poly_sub(p1, p1) == [], "poly_sub self is zero")
    check(uba.poly_mul(p0, p1) == [], "poly_mul with zero")
    check(uba.poly_mul(p1, p0) == [], "poly_mul rhs zero")
    prod = uba.poly_mul(uba.poly_from_terms({1: 2}), uba.poly_from_terms({0: 1, 2: -3}))
    check(prod == [Fraction(0), Fraction(2), Fraction(0), Fraction(-6)], "poly_mul exact")
    check(uba.poly_val(prod) == 1 and uba.poly_lead(prod) == Fraction(2), "poly val/lead")
    check(uba.poly_deg(prod) == 3, "poly deg exact")
    check(uba.poly_coeff_at(prod, 3) == Fraction(-6), "poly_coeff_at exact")
    check(uba.poly_coeff_at(prod, 4) == Fraction(0), "poly_coeff_at OOB is 0")

    # Determinant & adjugate 0x0, 1x1, 2x2, 3x3 (including zero first-row entry)
    check(uba.poly_det([]) == [Fraction(1)], "det 0x0 = 1")
    check(uba.poly_adj([]) == [], "adj 0x0 = []")
    m1 = [[uba.poly_from_terms({0: 3})]]
    check(uba.poly_det(m1) == [Fraction(3)], "det 1x1")
    check(uba.poly_adj(m1) == [[[Fraction(1)]]], "adj 1x1")
    m2 = [
        [uba.poly_from_terms({0: 1, 1: -1}), uba.poly_from_terms({1: 2})],
        [uba.poly_from_terms({1: 3}), uba.poly_from_terms({0: 1})],
    ]
    # det = (1 - q) - 6 q^2
    check(uba.poly_det(m2) == [Fraction(1), Fraction(-1), Fraction(-6)], "det 2x2 exact")
    adj2 = uba.poly_adj(m2)
    check(adj2[0][0] == [Fraction(1)] and adj2[0][1] == [Fraction(0), Fraction(-2)], "adj 2x2 row0")
    check(adj2[1][0] == [Fraction(0), Fraction(-3)] and adj2[1][1] == [Fraction(1), Fraction(-1)], "adj 2x2 row1")

    m3 = [
        [p0, uba.poly_from_terms({0: 2}), uba.poly_from_terms({0: 1})],
        [uba.poly_from_terms({0: 1}), p0, uba.poly_from_terms({0: 3})],
        [uba.poly_from_terms({0: 4}), uba.poly_from_terms({0: 5}), p0],
    ]
    # det = 0 - 2*(0 - 12) + 1*(5 - 0) = 24 + 5 = 29
    check(uba.poly_det(m3) == [Fraction(29)], "det 3x3 exact with zero pivot")
    check(uba.mat_transpose([]) == [], "transpose empty")


def test_pillar1_reconciliation_and_manifest() -> None:
    # Manifest verifier positive & negative paths (UNIF-BUG-01a/b hardened)
    ok = uba.verify_pinned_digests(dict(uba.PINNED_STAGED_DIGESTS))
    check(ok["all_digests_verified"] is True and ok["pinned_count"] == 12, "pinned manifest ok")
    expect_audit_error(
        lambda: uba.verify_pinned_digests("not_a_dict"), "ERR_INVALID_MANIFEST", "non-dict manifest"
    )
    rogue_float = dict(uba.PINNED_STAGED_DIGESTS)
    rogue_float["rogue_float"] = float(314) / 100
    expect_audit_error(
        lambda: uba.verify_pinned_digests(rogue_float),
        "ERR_INVALID_DIGEST_TYPE",
        "reject float digest value",
    )
    bad_key_type = dict(uba.PINNED_STAGED_DIGESTS)
    bad_key_type[123] = "a" * 64  # type: ignore[index]
    expect_audit_error(
        lambda: uba.verify_pinned_digests(bad_key_type),
        "ERR_INVALID_DIGEST_TYPE",
        "reject non-str manifest key",
    )
    bad_len = dict(uba.PINNED_STAGED_DIGESTS)
    bad_len["cave_pr_5"] = "a" * 63
    expect_audit_error(
        lambda: uba.verify_pinned_digests(bad_len),
        "ERR_INVALID_DIGEST_FORMAT",
        "reject short hex digest",
    )
    bad_upper = dict(uba.PINNED_STAGED_DIGESTS)
    bad_upper["cave_pr_5"] = "A" * 64
    expect_audit_error(
        lambda: uba.verify_pinned_digests(bad_upper),
        "ERR_INVALID_DIGEST_FORMAT",
        "reject uppercase hex digest",
    )
    extra_key = dict(uba.PINNED_STAGED_DIGESTS)
    extra_key["rogue_extra"] = "a" * 64
    expect_audit_error(
        lambda: uba.verify_pinned_digests(extra_key),
        "ERR_EXTRA_DIGEST_KEY",
        "reject unexpected extra key",
    )
    missing = dict(uba.PINNED_STAGED_DIGESTS)
    missing.pop("cave_pr_5")
    expect_audit_error(
        lambda: uba.verify_pinned_digests(missing), "ERR_MISSING_DIGEST", "missing digest rejected"
    )
    tampered = dict(uba.PINNED_STAGED_DIGESTS)
    tampered["cave_pr_5"] = "0" * 64
    expect_audit_error(
        lambda: uba.verify_pinned_digests(tampered), "ERR_DIGEST_MISMATCH", "tampered digest rejected"
    )

    # Live disk digest helper negative & positive paths (UNIF-BUG-01b)
    expect_audit_error(
        lambda: uba.compute_staged_digests_from_root(Path("nonexistent_round10_root_xyz")),
        "ERR_STAGED_ROOT_MISSING",
        "reject missing expedition root",
    )
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp_root = Path(tmp_str)
        expect_audit_error(
            lambda: uba.compute_staged_digests_from_root(tmp_root),
            "ERR_STAGED_FILE_MISSING",
            "reject missing staged file",
        )
        expected_syn: dict[str, str] = {}
        for key, rel in uba.STAGED_RELATIVE_PATHS.items():
            fpath = tmp_root / rel
            fpath.parent.mkdir(parents=True, exist_ok=True)
            data = f"fixture:{key}\n".encode("utf-8")
            fpath.write_bytes(data)
            expected_syn[key] = hashlib.sha256(data).hexdigest()
        computed = uba.compute_staged_digests_from_root(tmp_root)
        check(computed == expected_syn, "compute_staged_digests_from_root exact hashes")
        expect_audit_error(
            lambda: uba.build_certificate(standalone=False, expedition_root=tmp_root),
            "ERR_DIGEST_MISMATCH",
            "live build_certificate fails closed on mismatched staged files",
        )
    expect_audit_error(
        lambda: uba.build_certificate(standalone=1),  # type: ignore[arg-type]
        "ERR_INVALID_BOOL",
        "build_certificate rejects non-bool standalone",
    )

    p1 = uba.audit_external_reconciliation_oracles()
    check(p1["verified"] is True, "P1 verified")
    check(p1["CS_08_non_reversal"]["no_tool_diff"] == "-16/2881", "CS-08 no-tool exact diff")
    check(p1["CS_08_non_reversal"]["tool_diff"] == "-1/14", "CS-08 tool exact diff")
    check(p1["CS_08_non_reversal"]["overall_diff"] == "-2/25", "CS-08 overall exact diff")
    check(p1["CS_08_non_reversal"]["simpson_reversal_absent"] is True, "CS-08 no reversal")

    check(p1["AUDIT_004_peeling"]["hardin_deficit"] == "-9/2", "AUDIT-004 hardin exact -9/2")
    check(p1["AUDIT_004_peeling"]["fair_2layer_gain"] == "28/1", "AUDIT-004 fair gain 28")
    check(p1["AUDIT_004_peeling"]["overstated_gain"] == "48/1", "AUDIT-004 overstated gain 48")
    check(p1["AUDIT_004_peeling"]["strict_dominance_refuted"] is True, "AUDIT-004 strict dom refuted")
    check(p1["AUDIT_004_peeling"]["greedy_lt_lp_lt_opt"] is True, "AUDIT-004 60<68<80")

    check(p1["AUDIT_005_rls_boundaries"]["exact_ties_at_0_and_2_verified"] is True, "AUDIT-005 ties")

    check(p1["AUDIT_008R_maslov_doob"]["opt_row0_ordinary_sum"] == "5/4", "AUDIT-008R row0 sum 5/4")
    check(p1["AUDIT_008R_maslov_doob"]["opt_row0_max_times"] == "1/1", "AUDIT-008R row0 max 1")
    check(p1["AUDIT_008R_maslov_doob"]["bad_row0_max_times"] == "1/2", "AUDIT-008R bad max 1/2")
    check(p1["AUDIT_008R_maslov_doob"]["ordinary_doob_fails"] is True, "AUDIT-008R ordinary fails")
    check(p1["AUDIT_008R_maslov_doob"]["tropical_doob_exact_at_dstar"] is True, "AUDIT-008R trop ok")
    check(p1["AUDIT_008R_maslov_doob"]["tropical_doob_breaks_off_dstar"] is True, "AUDIT-008R off d*")

    check(p1["AUDIT_010_zerolog_rays"]["readme_first_moments"] == [-1, -1], "AUDIT-010 readme moments")
    check(p1["AUDIT_010_zerolog_rays"]["code_first_moments"] == [0, 0], "AUDIT-010 code moments")
    check(p1["AUDIT_010_zerolog_rays"]["verified"] is True, "AUDIT-010 verified")

    check(p1["AUDIT_018_lindblad_o2_gap"]["gamma_schur"] == "41/20", "AUDIT-018 gamma_schur")
    check(p1["AUDIT_018_lindblad_o2_gap"]["gamma_slow_o2"] == "37/18", "AUDIT-018 gamma_slow_o2")
    check(p1["AUDIT_018_lindblad_o2_gap"]["exact_o2_gap"] == "1/180", "AUDIT-018 exact gap 1/180")
    check(p1["AUDIT_018_lindblad_o2_gap"]["det_product_value"] == "41/1", "AUDIT-018 det 41")
    check(p1["AUDIT_018_lindblad_o2_gap"]["verified"] is True, "AUDIT-018 verified")

    ext = p1["external_tallies"]
    check(ext["cave_pr_4"]["total"] == 36 and ext["cave_pr_5"]["total"] == 16, "PR4/PR5 totals")
    check(ext["cave_pr_5_partial_ids_closed_here"] == ["G5-07", "G5-10", "G5-13"], "3 PARTIAL IDs")
    check(ext["tallies_consistent"] is True, "tallies consistent")


def test_pillar2_algebraic_tropical_bridge() -> None:
    p2 = uba.prove_algebraic_tropical_elimination_bridge()
    check(p2["verified"] is True, "P2 verified")

    # R1: Positive cyclic B2 — check exact (0,1): direct q^4, path 0->2->3->1 is q^{1+1+1}=q^3 => T=3, L=1
    r1 = p2["R1_positive_gibbs_cyclic_B2"]
    check(r1["is_regular_pivot"] is True and r1["val_det_I_minus_KBB"] == 0, "R1 regular det val 0")
    check(r1["degree_upper_bound"] == 15, "R1 deg upper bound (2+1)*5=15")
    check(not r1["has_cancellation_defect"] and not r1["has_negative_gap"], "R1 zero defect")
    r1_map = {tuple(e["pair"]): e for e in r1["entries"]}
    check(r1_map[(0, 1)]["val_S"] == 3 and r1_map[(0, 1)]["T_trop"] == 3, "R1 (0,1) val=T=3")
    check(r1_map[(0, 1)]["lead_walk_sum"] == "1/1" and r1_map[(0, 1)]["cancellation_gap"] == 0, "R1 (0,1) L=1")
    check(r1_map[(0, 0)]["val_S"] == 4 and r1_map[(0, 0)]["T_trop"] == 4, "R1 (0,0) val=T=4")
    check(r1_map[(1, 1)]["val_S"] == 3 and r1_map[(1, 1)]["T_trop"] == 3, "R1 (1,1) val=T=3")
    check(r1_map[(1, 0)]["val_S"] == 4 and r1_map[(1, 0)]["T_trop"] == 4, "R1 (1,0) val=T=4")

    # R2: Signed non-cancelling: L_01 = 1 - 2 = -1 => gap = 0
    r2 = p2["R2_signed_noncancelling"]
    r2_map = {tuple(e["pair"]): e for e in r2["entries"]}
    check(r2_map[(0, 1)]["val_S"] == 2 and r2_map[(0, 1)]["T_trop"] == 2, "R2 (0,1) val=T=2")
    check(r2_map[(0, 1)]["lead_walk_sum"] == "-1/1" and r2_map[(0, 1)]["cancellation_gap"] == 0, "R2 L=-1")
    check(r2_map[(0, 0)]["cancellation_gap"] == "UNREACHABLE", "R2 (0,0) unreachable")

    # R3: Finite cancellation gap Delta = 1
    r3 = p2["R3_finite_cancellation_gap"]
    r3_map = {tuple(e["pair"]): e for e in r3["entries"]}
    check(r3["max_finite_gap"] == 1 and r3["has_cancellation_defect"] is True, "R3 gap=1")
    check(r3_map[(0, 1)]["val_S"] == 3 and r3_map[(0, 1)]["T_trop"] == 2, "R3 val=3 T=2")
    check(r3_map[(0, 1)]["lead_walk_sum"] == "0/1" and r3_map[(0, 1)]["cancellation_gap"] == 1, "R3 L=0 gap=1")

    # R4: Total annihilation Delta = INF
    r4 = p2["R4_exact_total_annihilation"]
    r4_map = {tuple(e["pair"]): e for e in r4["entries"]}
    check(r4["annihilated_pairs"] == [[0, 1]], "R4 annihilated (0,1)")
    check(r4_map[(0, 1)]["val_S"] == "INF" and r4_map[(0, 1)]["T_trop"] == 2, "R4 val=INF T=2")
    check(r4_map[(0, 1)]["cancellation_gap"] == "INF" and r4_map[(0, 1)]["lead_walk_sum"] == "0/1", "R4 gap INF")

    # R5: Non-regular pivot negative gap -1
    r5 = p2["R5_nonregular_pivot_negative_gap"]
    r5_map = {tuple(e["pair"]): e for e in r5["entries"]}
    check(r5["is_regular_pivot"] is False and r5["val_det_I_minus_KBB"] == 1, "R5 non-regular det val=1")
    check(r5["has_negative_gap"] is True and r5["all_lower_bound_hold"] is False, "R5 negative gap")
    check(r5_map[(0, 1)]["val_S"] == 1 and r5_map[(0, 1)]["T_trop"] == 2, "R5 val=1 < T=2")
    check(r5_map[(0, 1)]["cancellation_gap"] == -1 and r5_map[(0, 1)]["lead_walk_sum"] is None, "R5 gap=-1")

    # Extra test: multi-step cancellation inside B + higher-gap (Delta = 2) + input validation errors
    z = uba.poly_from_terms({})
    k_gap2 = [
        [z, uba.poly_from_terms({2: 1}), uba.poly_from_terms({1: 1})],
        [z, z, z],
        [z, uba.poly_from_terms({1: -1}), uba.poly_from_terms({2: 1})],
    ]
    res_g2 = uba.evaluate_algebraic_tropical_bridge(k_gap2, [0, 1], [2])
    check(res_g2["max_finite_gap"] == 2 and res_g2["all_iff_hold"] is True, "Delta=2 witness exact")

    # Input validation negatives on evaluate_algebraic_tropical_bridge
    expect_audit_error(
        lambda: uba.evaluate_algebraic_tropical_bridge([[z]], [0], []),
        "ERR_INVALID_MATRIX",
        "1x1 matrix rejected",
    )
    expect_audit_error(
        lambda: uba.evaluate_algebraic_tropical_bridge([[z, z], [z]], [0], [1]),
        "ERR_NON_SQUARE_MATRIX",
        "ragged matrix rejected",
    )
    expect_audit_error(
        lambda: uba.evaluate_algebraic_tropical_bridge([[z, "bad"], [z, z]], [0], [1]),
        "ERR_INVALID_POLY",
        "non-list poly entry rejected",
    )
    expect_audit_error(
        lambda: uba.evaluate_algebraic_tropical_bridge([[z, z], [z, z]], "0", [1]),
        "ERR_INVALID_PARTITION",
        "non-list partition rejected",
    )
    expect_audit_error(
        lambda: uba.evaluate_algebraic_tropical_bridge([[z, z], [z, z]], [0, 1], []),
        "ERR_EMPTY_BLOCK",
        "empty block rejected",
    )
    expect_audit_error(
        lambda: uba.evaluate_algebraic_tropical_bridge([[z, z], [z, z]], [0], [0]),
        "ERR_INVALID_PARTITION",
        "overlapping partition rejected",
    )
    # Singular pivot: K_11 = 1 => I - K_BB = 0 => det = 0
    k_sing = [[z, z], [z, uba.poly_from_terms({0: 1})]]
    expect_audit_error(
        lambda: uba.evaluate_algebraic_tropical_bridge(k_sing, [0], [1]),
        "ERR_SINGULAR_PIVOT",
        "singular pivot det=0 rejected",
    )


def test_pillar3_lattice_symmetrizer_rank() -> None:
    p3 = uba.prove_lattice_symmetrizer_rank_theorem()
    check(p3["verified"] is True, "P3 verified")
    check(p3["all_n_ge_3_pass"] is True, "P3 all n>=3 pass")
    check(p3["n2_sharpness_verified"] is True, "P3 n=2 sharpness verified")

    univ = p3["universal_n_ge_3_cases"]
    check(univ["n3_diag_3_2_2"]["dim_Z_B"] == 3 and univ["n3_diag_3_2_2"]["rank_S_el_actual"] == 1, "diag(3,2,2)")
    check(univ["n3_diag_3_2_2"]["nonzero_rows_of_L_Lminus2I"] == [0], "diag(3,2,2) nz_rows=[0]")
    check(univ["n3_low_tri_2"]["dim_Z_B"] == 1 and univ["n3_low_tri_2"]["rank_S_el_actual"] == 0, "low_tri_2")
    check(univ["n3_two_I"]["dim_Z_B"] == 3 and univ["n3_two_I"]["rank_S_el_actual"] == 0, "2I rank 0")
    check(univ["n3_nonsym_symmetrizable"]["dim_Z_B"] == 1 and univ["n3_nonsym_symmetrizable"]["rank_S_el_actual"] == 1, "nonsym_symmetrizable")
    check(univ["n4_D4_upper"]["intra_motion_dim"] == 10 and univ["n4_D4_upper"]["rigid_motion_dim"] == 10, "D4 10 rigid motions")
    check(univ["n4_D4_upper"]["dim_Z_B"] == 1 and univ["n4_D4_upper"]["rank_S_el_actual"] == 1, "D4 rank 1")

    # Generic asymmetric n=3 matrix with dim(Z_B) = 0 -> rank_S_el = 0 (exercises empty global_stresses branch if any, and dim=0)
    res_zero_zb = uba.verify_lattice_rank_instance([[2, 1, 2], [3, 2, 1], [1, 5, 2]])
    check(res_zero_zb["dim_Z_B"] == 0 and res_zero_zb["rank_S_el_actual"] == 0, "dim Z_B=0 => rank 0")
    check(res_zero_zb["formula_matches"] is True and res_zero_zb["intra_rigid"] is True, "dim Z_B=0 formula matches")

    # Sharpness counterexamples at n = 2
    sharp = p3["sharpness_n_eq_2_counterexamples"]
    check(sharp["n2_sharpness_diag_3_2"]["formula_matches"] is False, "n=2 diag(3,2) breaks formula")
    check(sharp["n2_sharpness_diag_3_2"]["rank_S_el_actual"] == 0, "n=2 diag(3,2) actual=0")
    check(sharp["n2_sharpness_diag_3_2"]["g5_07_predicted_rank"] == 1, "n=2 diag(3,2) pred=1")
    check(sharp["n2_sharpness_diag_3_3"]["formula_matches"] is False, "n=2 diag(3,3) breaks formula")
    check(sharp["n2_sharpness_diag_3_3"]["rank_S_el_actual"] == 1, "n=2 diag(3,3) actual=1")
    check(sharp["n2_sharpness_diag_3_3"]["g5_07_predicted_rank"] == 2, "n=2 diag(3,3) pred=2")

    # Input validation negatives on verify_lattice_rank_instance
    expect_audit_error(
        lambda: uba.verify_lattice_rank_instance([[1]]), "ERR_INVALID_LATTICE", "1x1 lattice rejected"
    )
    expect_audit_error(
        lambda: uba.verify_lattice_rank_instance([[1, 2], [3]]),
        "ERR_NON_SQUARE_LATTICE",
        "ragged lattice rejected",
    )


def test_pillar4_sf01_taxonomy() -> None:
    p4 = uba.classify_sf01_honest_taxonomy()
    check(p4["verified"] is True, "P4 verified")
    check(p4["sf01_actual_entry_count"] == 29, "SF-01 actual count 29")
    check(p4["count_drift_detected"] is True, "29 != 30 drift detected")
    check(p4["sf01_class_counts"] == {"QH": 23, "QN": 4, "T": 0, "L": 2}, "exact SF-01 partition")
    check(p4["readme_8_table_class_counts"] == {"QH": 6, "QN": 1, "T": 1, "L": 0}, "README 8-row partition")
    check(len(p4["sf01_qn_entries"]) == 4, "4 QN entries")
    check(len(p4["sf01_label_only_entries"]) == 2, "2 L entries")
    check(len(p4["verified_cross_domain_morphisms"]) == 3, "3 verified morphisms")
    check(p4["m2_pullback_exact"] is True, "M2 Fisher pullback exact")


def test_pillar5_hardened_certifier_fail_closed() -> None:
    z = uba.poly_from_terms({})
    k_sym_pos = [
        [z, uba.poly_from_terms({2: 1}), uba.poly_from_terms({1: 1})],
        [uba.poly_from_terms({2: 1}), z, uba.poly_from_terms({1: 1})],
        [uba.poly_from_terms({1: 1}), uba.poly_from_terms({1: 1}), uba.poly_from_terms({1: 1})],
    ]
    k_pos = [
        [z, uba.poly_from_terms({2: 1}), uba.poly_from_terms({1: 1})],
        [z, z, z],
        [z, uba.poly_from_terms({1: 1}), uba.poly_from_terms({1: 1})],
    ]
    k_cancel = [
        [z, uba.poly_from_terms({2: 1}), uba.poly_from_terms({1: 1})],
        [z, z, z],
        [z, uba.poly_from_terms({1: -1}), uba.poly_from_terms({1: 1})],
    ]
    k_nonreg = [
        [z, z, uba.poly_from_terms({1: 1})],
        [z, z, z],
        [z, uba.poly_from_terms({1: 1}), uba.poly_from_terms({0: 1, 1: -1})],
    ]
    k_sym_sing = [
        [z, z],
        [z, uba.poly_from_terms({0: 1})],
    ]
    k_float_bypass = [
        [[float(3) / 2], []],
        [[], []],
    ]

    # Positive paths
    r_qh = uba.certify_unification_bridge_hardened(
        "QH", ["haynsworth_inertia", "schur_exists"], True, True
    )
    check(r_qh["verdict"] == "CERTIFIED" and r_qh["cross_domain_unification_certified"] is True, "QH certified")
    check(r_qh["bridge_summary"] is None, "QH bridge_summary None")

    r_qh_sym = uba.certify_unification_bridge_hardened(
        "QH",
        ["haynsworth_inertia", "tropical_bridge_exact"],
        True,
        True,
        k_sym_pos,
        [0, 1],
        [2],
    )
    check(r_qh_sym["verdict"] == "CERTIFIED" and r_qh_sym["bridge_summary"]["max_finite_gap"] == 0, "QH symmetric bridge certified")

    r_qn = uba.certify_unification_bridge_hardened("QN", ["schur_exists"], False, False)
    check(r_qn["verdict"] == "CERTIFIED" and r_qn["cross_domain_unification_certified"] is False, "QN certified")

    r_te = uba.certify_unification_bridge_hardened(
        "T", ["tropical_bridge_exact"], True, True, k_pos, [0, 1], [2]
    )
    check(r_te["verdict"] == "CERTIFIED" and r_te["bridge_summary"]["has_cancellation_defect"] is False, "T exact certified")

    r_tb = uba.certify_unification_bridge_hardened(
        "T", ["tropical_bridge_bound"], False, False, k_cancel, [0, 1], [2]
    )
    check(r_tb["verdict"] == "CERTIFIED" and r_tb["bridge_summary"]["max_finite_gap"] == 1, "T bound certified")

    # Every fail-closed error code triggered explicitly (incl. UNIF-BUG-02a/b)
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("BAD", ["schur_exists"]),
        "ERR_INVALID_CLASS",
        "invalid class",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("QH", []),
        "ERR_INVALID_INVARIANT",
        "empty invariants",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("QH", ["unknown_inv"]),
        "ERR_INVALID_INVARIANT",
        "unknown invariant",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("QH", ["schur_exists"], 1, False),
        "ERR_INVALID_BOOL",
        "non-bool unification flag",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("QH", ["schur_exists"], False, "yes"),
        "ERR_INVALID_BOOL",
        "non-bool morphism flag",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened(
            "QH", ["schur_exists"], False, False, k_sym_pos, None, None
        ),
        "ERR_INCOMPLETE_BRIDGE_DATA",
        "partial bridge args refused",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened(
            "QH", ["schur_exists"], False, False, k_float_bypass, [0], [1]  # type: ignore[arg-type]
        ),
        "ERR_NON_EXACT_RATIONAL",
        "UNIF-BUG-02a raw float in k_poly refused when needs_bridge=False",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened(
            "QH", ["haynsworth_inertia", "tropical_bridge_exact"], False, False, k_pos, [0, 1], [2]
        ),
        "ERR_NONSYMMETRIC_QH_MATRIX",
        "UNIF-BUG-02b asymmetric QH matrix refused",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened(
            "QH", ["schur_exists"], False, False, k_pos, [0, 1], [2]
        ),
        "ERR_NONSYMMETRIC_QH_MATRIX",
        "asymmetric QH matrix refused even without tropical_bridge",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened(
            "QH", ["schur_exists"], False, False, k_sym_sing, [0], [1]
        ),
        "ERR_SINGULAR_PIVOT",
        "singular pivot refused when k_poly supplied for schur_exists",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("L", ["schur_exists"]),
        "ERR_LABEL_ONLY_UNBUILT",
        "class L refused",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("QH", ["schur_exists"], True, False),
        "ERR_TAXONOMY_CONFLATED_WITH_UNIFICATION",
        "unification without morphism refused",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("QN", ["haynsworth_inertia"]),
        "ERR_INERTIA_UNDEFINED_FOR_CLASS",
        "Haynsworth on QN refused",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("T", ["haynsworth_inertia"]),
        "ERR_INERTIA_UNDEFINED_FOR_CLASS",
        "Haynsworth on T refused",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("T", ["additive_schur"]),
        "ERR_NO_ADDITIVE_INVERSE_IN_TROPICAL",
        "additive_schur on T refused",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("T", ["schur_exists"]),
        "ERR_NO_ADDITIVE_INVERSE_IN_TROPICAL",
        "schur_exists on T refused",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened("T", ["tropical_bridge_exact"]),
        "ERR_MISSING_BRIDGE_DATA",
        "missing bridge data refused",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened(
            "T", ["tropical_bridge_bound"], False, False, k_nonreg, [0, 1], [2]
        ),
        "ERR_NONREGULAR_PIVOT_CONSTANT_TERM",
        "non-regular pivot refused",
    )
    expect_audit_error(
        lambda: uba.certify_unification_bridge_hardened(
            "T", ["tropical_bridge_exact"], False, False, k_cancel, [0, 1], [2]
        ),
        "ERR_CANCELLATION_DEFECT_NONZERO",
        "cancelling matrix refused for exact bridge",
    )


def test_certificate_and_cli_determinism() -> None:
    buf1 = io.StringIO()
    with redirect_stdout(buf1):
        rc1 = uba.main(["--standalone"])
    buf2 = io.StringIO()
    with redirect_stdout(buf2):
        rc2 = uba.main(["--standalone"])
    check(rc1 == 0 and rc2 == 0, "main --standalone returns 0")
    out1 = buf1.getvalue()
    out2 = buf2.getvalue()
    check(out1 == out2, "--standalone stdout bit-identical across runs")

    cert = json.loads(out1)
    check(cert["schema"] == uba.SCHEMA_VERSION, "schema exact")
    check(cert["audit_id"] == "AUDIT-085", "audit_id exact")
    check(cert["novelty_grade"] == "N1", "novelty grade N1")
    check(cert["law4_quarantine_honored"] is True, "Law-4 quarantine True")
    check(cert["live_staged_digest_verification"]["mode"] == "standalone", "standalone mode recorded")
    check(cert["live_staged_digest_verification"]["disk_io_performed"] is False, "standalone zero disk io")
    check(cert["all_pillars_verified"] is True, "all_pillars_verified True")
    check(cert["pillar_5_hardened_certifier_smoke"]["verified"] is True, "P5 smoke verified")

    # Independent canonical SHA-256 verification
    digest_claimed = cert.pop("canonical_sha256")
    recomputed = hashlib.sha256(
        json.dumps(cert, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    check(digest_claimed == recomputed, "canonical_sha256 matches independent recomputation")

    # When running inside the expedition workspace, verify live disk digest mode end-to-end too
    parents = Path(__file__).resolve().parents
    if len(parents) > 3 and (parents[3] / uba.STAGED_RELATIVE_PATHS["aletheia_issue_2"]).is_file():
        buf_live = io.StringIO()
        with redirect_stdout(buf_live):
            rc_live = uba.main([])
        check(rc_live == 0, "live main() returns 0")
        live_cert = json.loads(buf_live.getvalue())
        check(live_cert["live_staged_digest_verification"]["mode"] == "live", "live mode recorded")
        check(live_cert["live_staged_digest_verification"]["disk_io_performed"] is True, "live disk io True")
        check(live_cert["live_staged_digest_verification"]["all_digests_verified"] is True, "live 12/12 verified")
        check(live_cert["all_pillars_verified"] is True, "live all_pillars_verified True")


def main() -> int:
    test_exact_validators_and_poly_ring()
    test_pillar1_reconciliation_and_manifest()
    test_pillar2_algebraic_tropical_bridge()
    test_pillar3_lattice_symmetrizer_rank()
    test_pillar4_sf01_taxonomy()
    test_pillar5_hardened_certifier_fail_closed()
    test_certificate_and_cli_determinism()
    sys.stdout.write("ALL_R5_TESTS_PASSED\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
