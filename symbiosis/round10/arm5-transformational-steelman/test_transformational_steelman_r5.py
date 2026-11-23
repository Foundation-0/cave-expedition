#!/usr/bin/env python3
"""Wave 2 Round 10 — Arm R10-5 (AUDIT-088):
Exhaustive R1-R5 unit, boundary, adversarial red-team, and live+standalone
verification suite for transformational_steelman_certifier.py.

Zero bare asserts; zero floats; isolated -I compatible.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

_THIS_DIR = str(Path(__file__).resolve().parent)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import transformational_steelman_certifier as mod


def _assert_no_floats(tc: unittest.TestCase, obj: object, path: str = "root") -> None:
    tc.assertIsNot(type(obj), float, f"float leaked at {path}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            tc.assertIsNot(type(k), float, f"float key at {path}")
            _assert_no_floats(tc, v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            _assert_no_floats(tc, item, f"{path}[{i}]")


def _base_rescue_spec() -> dict[str, object]:
    return {
        "claim_id": "TEST-RESCUE-01",
        "proposed_verdict": "TRANSFORMED_EXACT",
        "literal_failed": True,
        "literal_failure_witness": "Literal formula fails at x=1",
        "families_searched": ["T1_GAUGE_SIMILARITY"],
        "applied_family": "T1_GAUGE_SIMILARITY",
        "transform_dof": 1,
        "held_out_constraints": 2,
        "fixed_globally_before_holdout": True,
        "target_pass_count": 2,
        "target_total_count": 2,
        "null_false_pass_count": 0,
        "null_total_count": 10,
        "max_null_false_pass_rate": Fraction(1, 10),
        "transform_rank": 1,
        "preserved_invariant_core": "Spectrum preserved",
        "modified_hypotheses": "Diagonal gauge similarity",
        "residual_gap": Fraction(0, 1),
        "max_residual_gap": Fraction(0, 1),
        "relabelled_as_literal": False,
        "obstruction_invariant": None,
        "obstruction_survives_all_searched": False,
    }


def _base_obstruction_spec() -> dict[str, object]:
    return {
        "claim_id": "TEST-OBS-01",
        "proposed_verdict": "INVARIANT_FALSIFIED",
        "literal_failed": True,
        "literal_failure_witness": "Identical observables yield opposite truth values",
        "families_searched": list(mod.MORPHISM_FAMILIES),
        "applied_family": None,
        "transform_dof": 0,
        "held_out_constraints": 4,
        "fixed_globally_before_holdout": True,
        "target_pass_count": 0,
        "target_total_count": 4,
        "null_false_pass_count": 0,
        "null_total_count": 10,
        "max_null_false_pass_rate": Fraction(1, 10),
        "transform_rank": 0,
        "preserved_invariant_core": None,
        "modified_hypotheses": None,
        "residual_gap": Fraction(1, 1),
        "max_residual_gap": Fraction(1, 1),
        "relabelled_as_literal": False,
        "obstruction_invariant": "Data-processing invariant across identical observables",
        "obstruction_survives_all_searched": True,
    }


class TestPrimitivesAndHelpers(unittest.TestCase):
    def test_exact_primitives(self) -> None:
        self.assertEqual(mod.frac_to_dict(Fraction(3, 4)), {"num": 3, "den": 4})
        with self.assertRaises(TypeError):
            mod.frac_to_dict(3)  # type: ignore[arg-type]

        self.assertEqual(mod.exact_frac(5, "x"), Fraction(5, 1))
        self.assertEqual(mod.exact_frac(Fraction(2, 7), "x"), Fraction(2, 7))
        for bad in (True, False, 1 / 2, "1/2", None):
            with self.assertRaises(ValueError):
                mod.exact_frac(bad, "x")

        self.assertEqual(mod.exact_int(0, "n"), 0)
        for bad in (True, False, 1 / 1, "1", None):
            with self.assertRaises(ValueError):
                mod.exact_int(bad, "n")

        self.assertIs(mod.exact_bool(True, "b"), True)
        for bad in (0, 1, "true", None):
            with self.assertRaises(ValueError):
                mod.exact_bool(bad, "b")

    def test_clean_ascii_strings_and_families(self) -> None:
        self.assertEqual(mod.clean_ascii_str("ok ~!", "s"), "ok ~!")
        self.assertIsNone(mod.opt_clean_ascii_str(None, "s"))
        self.assertEqual(mod.opt_clean_ascii_str("abc", "s"), "abc")
        # Boundary ASCII codes 32 (space inside) and 126 (~) allowed; 31, 127, ZWSP, padded rejected
        self.assertEqual(mod.clean_ascii_str("a ~", "s"), "a ~")
        for bad in (
            123,
            "",
            " lead",
            "trail ",
            "a\x1fb",
            "a\x7fb",
            "a\u200bb",
            "a\nb",
        ):
            with self.assertRaises(ValueError, msg=f"bad={bad!r}"):
                mod.clean_ascii_str(bad, "s")

        self.assertEqual(
            mod.parse_families_searched(("T1_GAUGE_SIMILARITY", "T2_AFFINE_BREGMAN")),
            ("T1_GAUGE_SIMILARITY", "T2_AFFINE_BREGMAN"),
        )
        for bad_fams in (
            {"T1_GAUGE_SIMILARITY"},
            {"T1_GAUGE_SIMILARITY": 1},
            "T1_GAUGE_SIMILARITY",
            ["UNKNOWN_FAMILY"],
            ["T1_GAUGE_SIMILARITY", "T1_GAUGE_SIMILARITY"],
        ):
            with self.assertRaises(ValueError, msg=f"bad_fams={bad_fams!r}"):
                mod.parse_families_searched(bad_fams)

    def test_symmetric_inertia_pivots(self) -> None:
        # 2x2 zero-diagonal antidiagonal [[0, 2], [2, 0]] -> (1, 1, 0)
        self.assertEqual(
            mod._symmetric_inertia_exact(
                [[Fraction(0, 1), Fraction(2, 1)], [Fraction(2, 1), Fraction(0, 1)]]
            ),
            (1, 1, 0),
        )
        # 3x3 swap diagonal pivot + zero eigenvalue
        self.assertEqual(
            mod._symmetric_inertia_exact(
                [
                    [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)],
                    [Fraction(0, 1), Fraction(3, 1), Fraction(0, 1)],
                    [Fraction(0, 1), Fraction(0, 1), Fraction(-2, 1)],
                ]
            ),
            (1, 1, 1),
        )
        # 3x3 off-diagonal swap needed (off_k == idx + 2)
        self.assertEqual(
            mod._symmetric_inertia_exact(
                [
                    [Fraction(0, 1), Fraction(0, 1), Fraction(1, 1)],
                    [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)],
                    [Fraction(1, 1), Fraction(0, 1), Fraction(0, 1)],
                ]
            ),
            (1, 1, 1),
        )
        # TS-BUG-03: fail-closed on empty, non-sequence, non-square, ragged, float, skew/asymmetric!
        for bad_mat in (
            "not-a-matrix",
            [],
            ["row-not-seq"],
            [[Fraction(1, 1), Fraction(2, 1)]],
            [[Fraction(1, 1), Fraction(0, 1)], [Fraction(0, 1)]],
            [[1 / 2]],
            [[Fraction(0, 1), Fraction(1, 1)], [Fraction(-1, 1), Fraction(0, 1)]],
            [[Fraction(1, 1), Fraction(10, 1)], [Fraction(-10, 1), Fraction(1, 1)]],
        ):
            with self.assertRaises(ValueError, msg=f"bad_mat={bad_mat!r}"):
                mod._symmetric_inertia_exact(bad_mat)


class TestCertifierSchemaBoundariesAndRedTeam(unittest.TestCase):
    def test_schema_and_domain_rejections(self) -> None:
        with self.assertRaises(ValueError):
            mod.certify_transformational_steelman(["not-a-dict"])

        s_miss = _base_rescue_spec()
        del s_miss["claim_id"]
        with self.assertRaises(ValueError):
            mod.certify_transformational_steelman(s_miss)

        s_extra = _base_rescue_spec()
        s_extra["extra"] = 1
        with self.assertRaises(ValueError):
            mod.certify_transformational_steelman(s_extra)

        for key, bad_val in (
            ("proposed_verdict", "VERIFIED"),
            ("applied_family", "T99_FAKE"),
            ("transform_dof", -1),
            ("held_out_constraints", 0),
            ("target_total_count", 0),
            ("target_pass_count", -1),
            ("target_pass_count", 3),
            ("null_total_count", 0),
            ("null_false_pass_count", -1),
            ("null_false_pass_count", 11),
            ("max_null_false_pass_rate", Fraction(-1, 100)),
            ("max_null_false_pass_rate", Fraction(11, 100)),
            ("transform_rank", -1),
            ("residual_gap", Fraction(-1, 10)),
            ("max_residual_gap", Fraction(-1, 10)),
        ):
            spec = _base_rescue_spec()
            spec[key] = bad_val
            with self.assertRaises(ValueError, msg=f"{key}={bad_val!r}"):
                mod.certify_transformational_steelman(spec)

    def test_admitted_exact_boundaries_for_rescues_and_obstructions(self) -> None:
        # 1. Exact rescue at exact boundaries: dof=0, constraints=1, null=1/10==max, rank=1, gap=0
        s = _base_rescue_spec()
        s["transform_dof"] = 0
        s["held_out_constraints"] = 1
        s["target_pass_count"] = 1
        s["target_total_count"] = 1
        s["null_false_pass_count"] = 1
        s["null_total_count"] = 10
        s["max_null_false_pass_rate"] = Fraction(1, 10)
        s["transform_rank"] = 1
        r = mod.certify_transformational_steelman(s)
        self.assertTrue(r["admitted"])
        self.assertEqual(r["status"], "CERTIFIED_TRANSFORMED_EXACT")
        self.assertEqual(r["reasons"], [])

        # 2. Bounded rescue at exact gap == max_residual_gap > 0 and max_null_rate == 0 with null_total == 1
        sb = _base_rescue_spec()
        sb["proposed_verdict"] = "BOUNDED_TRANSFORM_CORE"
        sb["residual_gap"] = Fraction(1, 5)
        sb["max_residual_gap"] = Fraction(1, 5)
        sb["max_null_false_pass_rate"] = Fraction(0, 1)
        sb["null_total_count"] = 1
        rb = mod.certify_transformational_steelman(sb)
        self.assertTrue(rb["admitted"])
        self.assertEqual(rb["status"], "CERTIFIED_BOUNDED_TRANSFORM_CORE")

        # 3. Invariant falsified at exact boundaries (7/7 families, 3/4 passing -> 1 failing!)
        so = _base_obstruction_spec()
        so["target_pass_count"] = 3
        so["target_total_count"] = 4
        ro = mod.certify_transformational_steelman(so)
        self.assertTrue(ro["admitted"])
        self.assertEqual(ro["status"], "CERTIFIED_INVARIANT_FALSIFIED")

    def test_every_individual_guard_refusal_and_boundary(self) -> None:
        # G0a: literal_failed == False
        s = _base_rescue_spec()
        s["literal_failed"] = False
        self.assertEqual(
            mod.certify_transformational_steelman(s)["reasons"],
            ["G0_LITERAL_CLAIM_NOT_FAILED"],
        )

        # G0b: applied_family not in families_searched
        s = _base_rescue_spec()
        s["families_searched"] = ["T2_AFFINE_BREGMAN"]
        self.assertEqual(
            mod.certify_transformational_steelman(s)["reasons"],
            ["G0_APPLIED_FAMILY_NOT_IN_SEARCH"],
        )

        # G0c: missing applied_family on rescue
        s = _base_rescue_spec()
        s["applied_family"] = None
        self.assertEqual(
            mod.certify_transformational_steelman(s)["reasons"],
            ["G0_MISSING_APPLIED_FAMILY"],
        )

        # G0d: contradictory obstruction metadata on rescue (either field alone triggers refusal!)
        s_co1 = _base_rescue_spec()
        s_co1["obstruction_invariant"] = "Unbreakable invariant"
        self.assertEqual(
            mod.certify_transformational_steelman(s_co1)["reasons"],
            ["G0_CONTRADICTORY_OBSTRUCTION_ON_RESCUE"],
        )
        s_co2 = _base_rescue_spec()
        s_co2["obstruction_survives_all_searched"] = True
        self.assertEqual(
            mod.certify_transformational_steelman(s_co2)["reasons"],
            ["G0_CONTRADICTORY_OBSTRUCTION_ON_RESCUE"],
        )

        # G1a: degenerate rank 0
        s = _base_rescue_spec()
        s["transform_rank"] = 0
        self.assertEqual(
            mod.certify_transformational_steelman(s)["reasons"],
            ["G1_DEGENERATE_ZERO_RANK_TRANSFORM"],
        )

        # G1b: target_pass < target_total
        s = _base_rescue_spec()
        s["target_pass_count"] = 1
        self.assertEqual(
            mod.certify_transformational_steelman(s)["reasons"],
            ["G1_TRANSFORMED_TARGET_FAILED"],
        )

        # G1c: null_rate > max_null_rate (2/10 > 1/10)
        s = _base_rescue_spec()
        s["null_false_pass_count"] = 2
        self.assertEqual(
            mod.certify_transformational_steelman(s)["reasons"],
            ["G1_VACUOUS_NULL_DISCRIMINATION_FAILED"],
        )

        # G1d (TS-BUG-04): under-resolved null suite (9 * 1/10 < 1 -> REJECT; 10 * 1/10 == 1 -> ADMIT)
        s_ur = _base_rescue_spec()
        s_ur["null_total_count"] = 9
        self.assertEqual(
            mod.certify_transformational_steelman(s_ur)["reasons"],
            ["G1_INSUFFICIENT_NULL_RESOLUTION"],
        )
        s_ur["null_total_count"] = 1
        self.assertEqual(
            mod.certify_transformational_steelman(s_ur)["reasons"],
            ["G1_INSUFFICIENT_NULL_RESOLUTION"],
        )

        # G2a: post-hoc patching
        s = _base_rescue_spec()
        s["fixed_globally_before_holdout"] = False
        self.assertEqual(
            mod.certify_transformational_steelman(s)["reasons"],
            ["G2_POST_HOC_PER_INSTANCE_PATCHING"],
        )

        # G2b: overparameterized exact boundary dof == held_out_constraints MUST reject
        s = _base_rescue_spec()
        s["transform_dof"] = 2
        s["held_out_constraints"] = 2
        self.assertEqual(
            mod.certify_transformational_steelman(s)["reasons"],
            ["G2_OVERPARAMETERIZED_EPICYCLE_DOF"],
        )

        # G3a: silent goalpost moving (both rescue and falsified)
        s = _base_rescue_spec()
        s["relabelled_as_literal"] = True
        self.assertEqual(
            mod.certify_transformational_steelman(s)["reasons"],
            ["G3_SILENT_GOALPOST_MOVING"],
        )

        # G3b: incomplete scope-delta ledger (missing preserved_core OR modified_hyp)
        for field in ("preserved_invariant_core", "modified_hypotheses"):
            s = _base_rescue_spec()
            s[field] = None
            self.assertEqual(
                mod.certify_transformational_steelman(s)["reasons"],
                ["G3_INCOMPLETE_SCOPE_DELTA_LEDGER"],
            )

        # G3c: exact rescue has nonzero gap OR contradictory nonzero max_residual_gap (TS-BUG-04)
        s = _base_rescue_spec()
        s["residual_gap"] = Fraction(1, 100)
        self.assertEqual(
            mod.certify_transformational_steelman(s)["reasons"],
            ["G3_EXACT_RESCUE_HAS_NONZERO_GAP"],
        )
        s_mg = _base_rescue_spec()
        s_mg["max_residual_gap"] = Fraction(1000, 1)
        self.assertEqual(
            mod.certify_transformational_steelman(s_mg)["reasons"],
            ["G3_EXACT_RESCUE_HAS_NONZERO_GAP"],
        )

        # G3d: bounded rescue gap == 0 OR gap > max_residual_gap
        sb0 = _base_rescue_spec()
        sb0["proposed_verdict"] = "BOUNDED_TRANSFORM_CORE"
        sb0["residual_gap"] = Fraction(0, 1)
        sb0["max_residual_gap"] = Fraction(1, 2)
        self.assertEqual(
            mod.certify_transformational_steelman(sb0)["reasons"],
            ["G3_BOUNDED_RESCUE_GAP_OUT_OF_RANGE"],
        )
        sb1 = dict(sb0)
        sb1["residual_gap"] = Fraction(3, 5)
        self.assertEqual(
            mod.certify_transformational_steelman(sb1)["reasons"],
            ["G3_BOUNDED_RESCUE_GAP_OUT_OF_RANGE"],
        )

        # G4a: premature raw FALSIFIED
        sf = _base_obstruction_spec()
        sf["proposed_verdict"] = "FALSIFIED_RAW"
        self.assertEqual(
            mod.certify_transformational_steelman(sf)["reasons"],
            ["G4_PREMATURE_FALSIFIED_NO_MORPHISM_GATE"],
        )

        # G4b: INVARIANT_FALSIFIED must not apply a rescue family
        so = _base_obstruction_spec()
        so["applied_family"] = "T1_GAUGE_SIMILARITY"
        self.assertEqual(
            mod.certify_transformational_steelman(so)["reasons"],
            ["G4_FALSIFIED_MUST_NOT_APPLY_RESCUE_FAMILY"],
        )

        # G4c: INVARIANT_FALSIFIED with target_pass == target_total (no failing target!)
        so = _base_obstruction_spec()
        so["target_pass_count"] = 4
        self.assertEqual(
            mod.certify_transformational_steelman(so)["reasons"],
            ["G4_FALSIFIED_CLAIM_HAS_NO_FAILING_TARGET"],
        )

        # G4d: INVARIANT_FALSIFIED with 6/7 families searched (1 short of exhaustive!)
        so = _base_obstruction_spec()
        so["families_searched"] = list(mod.MORPHISM_FAMILIES[:-1])
        self.assertEqual(
            mod.certify_transformational_steelman(so)["reasons"],
            ["G4_INSUFFICIENT_MORPHISM_SEARCH"],
        )

        # G4e: INVARIANT_FALSIFIED missing obstruction_invariant
        so = _base_obstruction_spec()
        so["obstruction_invariant"] = None
        self.assertEqual(
            mod.certify_transformational_steelman(so)["reasons"],
            ["G4_MISSING_TRANSFORM_INVARIANT_OBSTRUCTION"],
        )

        # G4f: INVARIANT_FALSIFIED obstruction does not survive all searched
        so = _base_obstruction_spec()
        so["obstruction_survives_all_searched"] = False
        self.assertEqual(
            mod.certify_transformational_steelman(so)["reasons"],
            ["G4_OBSTRUCTION_NOT_INVARIANT_ACROSS_FAMILIES"],
        )

        # G4g (TS-BUG-02): contradictory rescue fields / zero gap / post-hoc / vacuous null on INVARIANT_FALSIFIED
        for key, bad_val, expected_code in (
            ("preserved_invariant_core", "Rescued core", "G4_CONTRADICTORY_RESCUE_FIELDS_ON_FALSIFIED"),
            ("modified_hypotheses", "Shifted +5I", "G4_CONTRADICTORY_RESCUE_FIELDS_ON_FALSIFIED"),
            ("transform_rank", 1, "G4_CONTRADICTORY_RESCUE_FIELDS_ON_FALSIFIED"),
            ("transform_dof", 1, "G4_CONTRADICTORY_RESCUE_FIELDS_ON_FALSIFIED"),
            ("residual_gap", Fraction(0, 1), "G4_FALSIFIED_HAS_ZERO_GAP"),
            ("fixed_globally_before_holdout", False, "G2_POST_HOC_PER_INSTANCE_PATCHING"),
            ("null_false_pass_count", 2, "G1_VACUOUS_NULL_DISCRIMINATION_FAILED"),
        ):
            so_bad = _base_obstruction_spec()
            so_bad[key] = bad_val
            self.assertEqual(
                mod.certify_transformational_steelman(so_bad)["reasons"],
                [expected_code],
                msg=f"TS-BUG-02 field={key}",
            )


class TestVaultProofsAndCertifierCases(unittest.TestCase):
    def test_all_seven_rescue_proofs_and_three_obstructions(self) -> None:
        cert = mod.build_certificate(standalone=True)
        p = cert["pure_q_vault_proofs"]

        t1 = p["t1_gauge_similarity"]
        self.assertTrue(t1["literal_doob_stochastic_fails"])
        self.assertEqual(t1["sim_row_sums"], [{"num": 3, "den": 2}, {"num": 3, "den": 4}])
        self.assertEqual(t1["sim_row0_max_times"], {"num": 1, "den": 1})
        self.assertTrue(t1["charpoly_preserved_exact"])
        self.assertEqual(t1["trace"], {"num": 1, "den": 1})
        self.assertEqual(t1["det"], {"num": 0, "den": 1})

        t2 = p["t2_affine_bregman"]
        self.assertEqual(t2["clipped_anti_teacher_grad"], {"num": 1, "den": 504})
        self.assertEqual(t2["bregman_aligned_grad"], {"num": -496, "den": 63})
        self.assertEqual(t2["forward_kl_grad"], {"num": -31, "den": 64})
        self.assertTrue(t2["literal_reverses_sign"])
        self.assertTrue(t2["bregman_rescues_sign"])

        t3 = p["t3_metric_chart"]
        self.assertEqual(t3["raw_lower_dead_zone_bound"], {"num": -1, "den": 1})
        self.assertEqual(t3["raw_upper_overflow_qmax"], {"num": 1, "den": 1})
        self.assertTrue(t3["raw_fails_both_boundaries"])
        self.assertEqual(t3["bern_delta_1_50_qmin"], {"num": 18, "den": 25})
        self.assertEqual(t3["bern_delta_1_50_qmax"], {"num": 22, "den": 25})
        self.assertEqual(t3["bern_dist_to_simplex_edge"], {"num": 1, "den": 8})
        self.assertTrue(t3["bern_strictly_interior"])

        t4 = p["t4_spectral_psd_shift"]
        self.assertEqual(t4["inertia_A_minus_3I"], [1, 9, 0])
        self.assertEqual(t4["inertia_A_plus_3I"], [9, 1, 0])
        self.assertTrue(t4["literal_squaring_inverts_spectrum"])
        self.assertEqual(t4["inertia_A0_plus_5I"], [10, 0, 0])
        self.assertTrue(t4["steelman_strictly_pd"])

        t5 = p["t5_semiring_tropical"]
        self.assertEqual(t5["no_cancel_gap"], 0)
        self.assertEqual(t5["cancel_gap"], 1)
        self.assertTrue(t5["bridge_exact_when_nocancel_and_measured_when_cancel"])

        t6 = p["t6_subspace_projection"]
        self.assertEqual(t6["bpo_weight"], {"num": 50, "den": 1})
        self.assertTrue(t6["bpo_equals_top1_sc"])
        self.assertTrue(t6["bpo_jacobian_cancellation_exact"])
        self.assertEqual(t6["prereg02_raw_mixed_score"], {"num": 1, "den": 3})
        self.assertEqual(t6["prereg02_odd_subspace_score"], {"num": -1, "den": 1})
        self.assertTrue(t6["prereg02_subspace_restores_reversal"])
        self.assertEqual(t6["cs08_diff_no_unread"], {"num": -16, "den": 2881})
        self.assertEqual(t6["cs08_diff_some_unread"], {"num": -1, "den": 14})
        self.assertEqual(t6["cs08_diff_overall"], {"num": -2, "den": 25})
        self.assertTrue(t6["cs08_literal_simpson_absent"])
        self.assertEqual(t6["cs08_principal_stratum_66_diff"], {"num": 1, "den": 66})
        self.assertTrue(t6["cs08_principal_stratum_reverses_sign"])

        t7 = p["t7_order_domain_residual"]
        self.assertEqual(t7["prereg03_raw_argmin"], 0)
        self.assertEqual(t7["prereg03_mapped_argmin"], 2)
        self.assertTrue(t7["prereg03_raw_leaks"])
        self.assertTrue(t7["prereg03_rank_costs_equal"])
        self.assertEqual(t7["prereg03_rank_argmin"], 0)
        self.assertTrue(t7["zhihu_l112_in_domain_A_1_1"]["pythagorean_identity_exact"])
        self.assertEqual(t7["zhihu_l112_in_domain_A_1_1"]["delta_l2_sq"], {"num": -1, "den": 8})
        self.assertTrue(t7["zhihu_l112_out_domain_A_3_m1"]["pythagorean_identity_exact"])
        self.assertEqual(t7["zhihu_l112_out_domain_A_3_m1"]["delta_l2_sq"], {"num": 1, "den": 8})
        self.assertTrue(t7["zhihu_l112_domain_separates_sign"])

        obs = p["transform_invariant_obstructions"]
        self.assertEqual(obs["audit070_pillar_a_tseitin_k4"]["models_sat"], 8)
        self.assertEqual(obs["audit070_pillar_a_tseitin_k4"]["models_unsat"], 0)
        self.assertTrue(obs["audit070_pillar_a_tseitin_k4"]["gramians_identical_8I6"])
        self.assertTrue(obs["audit070_pillar_a_tseitin_k4"]["linear_biases_identical_zero"])
        self.assertEqual(obs["audit070_pillar_c_sidewalk_tsp"]["sigma0"], {"num": 1000, "den": 1})
        self.assertEqual(obs["audit070_pillar_c_sidewalk_tsp"]["best_without_01"], 16055)
        self.assertEqual(obs["audit070_pillar_c_sidewalk_tsp"]["best_with_01"], 16056)
        self.assertTrue(obs["audit070_pillar_c_sidewalk_tsp"]["shortest_edge_strictly_suboptimal"])
        self.assertEqual(obs["audit073_sng02_bootstrap_n1"]["two_scale_null_fwer"], {"num": 3, "den": 4})
        self.assertTrue(obs["audit073_sng02_bootstrap_n1"]["rank_zero_collapse"])

    def test_certified_vault_cases_matrix(self) -> None:
        cases = mod._build_certified_vault_cases()
        self.assertEqual(len(cases["certified_rescues"]), 7)
        for name, res in cases["certified_rescues"].items():
            self.assertTrue(res["admitted"], msg=f"rescue failed: {name} -> {res}")
        self.assertEqual(len(cases["certified_obstructions"]), 3)
        for name, res in cases["certified_obstructions"].items():
            self.assertTrue(res["admitted"], msg=f"obstruction failed: {name} -> {res}")
            self.assertEqual(res["status"], "CERTIFIED_INVARIANT_FALSIFIED")

        rej = cases["rejected_anti_epicycles"]
        self.assertEqual(
            set(rej["REJ1_degenerate_zero_rank"]["reasons"]),
            {"G1_DEGENERATE_ZERO_RANK_TRANSFORM", "G1_VACUOUS_NULL_DISCRIMINATION_FAILED"},
        )
        self.assertEqual(
            set(rej["REJ2_overparameterized_per_instance"]["reasons"]),
            {"G2_POST_HOC_PER_INSTANCE_PATCHING", "G2_OVERPARAMETERIZED_EPICYCLE_DOF"},
        )
        self.assertEqual(
            set(rej["REJ3_silent_goalpost_moving"]["reasons"]),
            {"G3_SILENT_GOALPOST_MOVING", "G3_INCOMPLETE_SCOPE_DELTA_LEDGER"},
        )
        self.assertEqual(
            set(rej["REJ4_premature_falsified_no_search"]["reasons"]),
            {
                "G4_INSUFFICIENT_MORPHISM_SEARCH",
                "G4_MISSING_TRANSFORM_INVARIANT_OBSTRUCTION",
                "G4_OBSTRUCTION_NOT_INVARIANT_ACROSS_FAMILIES",
            },
        )


class TestAnchorsCertificateAndCLI(unittest.TestCase):
    def test_standalone_certificate_zero_float_and_hash(self) -> None:
        c1 = mod.build_certificate(standalone=True)
        c2 = mod.build_certificate(standalone=True)
        self.assertEqual(c1, c2)
        self.assertEqual(c1["anchors"]["anchor_mode"], "standalone")
        self.assertIsNone(c1["anchors"]["all_anchors_matched"])
        _assert_no_floats(self, c1)
        copy_c = dict(c1)
        obs_sha = copy_c.pop("canonical_sha256")
        raw = json.dumps(copy_c, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(obs_sha, hashlib.sha256(raw).hexdigest())

    def test_verify_live_anchors_missing_and_tampered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            res0 = mod.verify_live_vault_anchors(tdir)
            self.assertFalse(res0["all_file_digests_matched"])
            self.assertFalse(res0["all_anchors_matched"])
            self.assertEqual(res0["line_anchors_verified"], 0)

            p = tdir / "round10/portals/aletheia/pr_9_files/spec/proposals/OWN_TERMS_FIRST.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            lines = [""] * 50
            lines[20] = "1. **Two phases, kept apart.**"
            lines[43] = "Ordinary and tropical elimination agree exactly when nothing cancels"
            p.write_text("\n".join(lines), encoding="utf-8")
            res1 = mod.verify_live_vault_anchors(tdir)
            self.assertFalse(res1["all_file_digests_matched"])
            self.assertEqual(res1["line_anchors_verified"], 2)
            self.assertFalse(res1["all_anchors_matched"])

    def test_live_vault_if_present(self) -> None:
        sym = Path(__file__).resolve().parent.parent.parent
        if not (sym / "round10/portals/aletheia").is_dir():
            return
        cert = mod.build_certificate(symbiosis_dir=sym, standalone=False)
        self.assertTrue(cert["anchors"]["all_file_digests_matched"])
        self.assertTrue(cert["anchors"]["all_anchors_matched"])
        self.assertEqual(cert["anchors"]["line_anchors_verified"], len(mod.VAULT_LINE_ANCHORS))
        _assert_no_floats(self, cert)

    def test_cli_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "cert.json"
            buf = io.StringIO()
            with mock.patch.object(sys, "stdout", buf):
                rc = mod.main(["--standalone", "--write-cert", str(out_path)])
            self.assertEqual(rc, 0)
            self.assertEqual(buf.getvalue(), "")
            loaded = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["audit_id"], "AUDIT-088")
            _assert_no_floats(self, loaded)

            buf2 = io.StringIO()
            with mock.patch.object(sys, "stdout", buf2):
                rc2 = mod.main(["--standalone", "--json", "--write-cert", str(out_path)])
            self.assertEqual(rc2, 0)
            self.assertEqual(buf2.getvalue(), out_path.read_text(encoding="utf-8"))

            buf3 = io.StringIO()
            with mock.patch.object(sys, "stdout", buf3):
                rc3 = mod.main(["--symbiosis-dir", tmp, "--json"])
            self.assertEqual(rc3, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
