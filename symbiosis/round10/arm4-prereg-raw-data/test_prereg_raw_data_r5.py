#!/usr/bin/env python3
"""R1-R5, boundary, red-team bypass, and 100% mutation-kill test suite for AUDIT-087.

Runs cleanly under `python3 -I -O -B -W error test_prereg_raw_data_r5.py`.
Zero floats; zero bare assert statements.
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
from unittest.mock import patch

_THIS_DIR = str(Path(__file__).resolve().parent)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import prereg_raw_data_certifier as prc


class TestPrimitivesAndExactMath(unittest.TestCase):
    def test_exact_type_and_formatting_guards(self) -> None:
        self.assertEqual(prc.frac_str(Fraction(3, 4)), "3/4")
        self.assertEqual(prc.frac_str(5), "5/1")
        self.assertEqual(prc.frac_dec6(Fraction(-1, 8)), "-0.125000")
        self.assertEqual(prc.frac_dec6(Fraction(0, 1)), "0.000000")
        with self.assertRaisesRegex(prc.PreregAuditError, r"exact-fraction:frac_str"):
            prc.frac_str(True)  # type: ignore[arg-type]
        with self.assertRaisesRegex(prc.PreregAuditError, r"exact-fraction:frac_str"):
            prc.frac_str("1/2")  # type: ignore[arg-type]

    def test_binom_upper_tail_exact_and_refusals(self) -> None:
        self.assertEqual(prc.binom_upper_tail(1, Fraction(1, 2), 0), Fraction(1, 1))
        self.assertEqual(prc.binom_upper_tail(1, Fraction(1, 2), 1), Fraction(1, 2))
        self.assertEqual(prc.binom_upper_tail(1, Fraction(1, 2), 2), Fraction(0, 1))
        with self.assertRaisesRegex(prc.PreregAuditError, r"exact-int:n"):
            prc.binom_upper_tail(True, Fraction(1, 2), 1)  # type: ignore[arg-type]
        with self.assertRaisesRegex(prc.PreregAuditError, r"binom-n-pos"):
            prc.binom_upper_tail(0, Fraction(1, 2), 0)
        with self.assertRaisesRegex(prc.PreregAuditError, r"binom-p-open-unit"):
            prc.binom_upper_tail(5, Fraction(0, 1), 1)
        with self.assertRaisesRegex(prc.PreregAuditError, r"binom-p-open-unit"):
            prc.binom_upper_tail(5, Fraction(1, 1), 1)
        with self.assertRaisesRegex(prc.PreregAuditError, r"binom-k-range"):
            prc.binom_upper_tail(5, Fraction(1, 2), -1)
        with self.assertRaisesRegex(prc.PreregAuditError, r"binom-k-range"):
            prc.binom_upper_tail(5, Fraction(1, 2), 7)

    def test_ordinal_end_match_and_rank_primitives(self) -> None:
        res = prc.count_d3_ordinal_patterns([3, 1, 2], tau=1)
        self.assertEqual(res["counts"]["201"], 1)
        self.assertEqual(res["ties"], 0)
        res_tie = prc.count_d3_ordinal_patterns([1, 1, 2, 3, 2], tau=1)
        self.assertEqual(res_tie["ties"], 2)
        self.assertEqual(res_tie["counts"]["012"], 1)
        self.assertEqual(res_tie["valid_windows"], 1)
        with self.assertRaisesRegex(prc.PreregAuditError, r"d3-series-len"):
            prc.count_d3_ordinal_patterns([1, 2], tau=1)
        with self.assertRaisesRegex(prc.PreregAuditError, r"d3-tau-range"):
            prc.count_d3_ordinal_patterns([1, 2, 3, 4], tau=0)
        with self.assertRaisesRegex(prc.PreregAuditError, r"d3-tau-range"):
            prc.count_d3_ordinal_patterns([1, 2, 3, 4], tau=2)

        self.assertEqual(prc.end_match_cost_raw([1, 2, 3, 4]), Fraction(9, 1))
        with self.assertRaisesRegex(prc.PreregAuditError, r"end-match-len"):
            prc.end_match_cost_raw([1, 2, 3])
        self.assertEqual(prc.rank_transform_exact([10]), (Fraction(0, 1),))
        self.assertEqual(
            prc.rank_transform_exact([5, 5, 10]),
            (Fraction(1, 2), Fraction(1, 2), Fraction(2, 1)),
        )
        with self.assertRaisesRegex(prc.PreregAuditError, r"rank-block-len"):
            prc.rank_transform_exact([])


class TestFourPillarsExactValues(unittest.TestCase):
    def test_pillar1_control_power_and_holm(self) -> None:
        p1 = prc.analyze_pillar1_control_power_and_holm()
        self.assertEqual(p1["holm_min_threshold"], "1/560")
        pr = p1["presence_thresholds_verified"]
        self.assertFalse(pr["S12_K4_reaches_holm"])
        self.assertTrue(pr["S12_K5_reaches_holm"])
        self.assertFalse(pr["S32_K6_reaches_holm"])
        self.assertTrue(pr["S32_K7_reaches_holm"])

        trap = p1["prereg01a_control_conjunction_trap"]
        self.assertEqual(trap["S12"]["binom_1pct_fail_prob_dec6"], "0.002236")
        self.assertEqual(trap["S12"]["rate_cap_fail_prob_dec6"], "0.118359")
        self.assertEqual(trap["S12"]["per_instrument_3controls_false_invalid_dec6"], "0.314710")
        self.assertEqual(trap["S12"]["three_instruments_any_false_invalid_dec6"], "0.678173")
        self.assertEqual(trap["S12"]["four_instruments_any_false_invalid_dec6"], "0.779455")
        self.assertEqual(trap["S32"]["binom_1pct_fail_prob_dec6"], "0.004599")
        self.assertEqual(trap["S32"]["rate_cap_fail_prob_dec6"], "0.073805")
        self.assertEqual(trap["S32"]["per_instrument_3controls_false_invalid_dec6"], "0.205476")
        self.assertEqual(trap["S32"]["three_instruments_any_false_invalid_dec6"], "0.498443")
        self.assertEqual(trap["S32"]["four_instruments_any_false_invalid_dec6"], "0.601501")

        k2 = p1["prereg01b_k2_quantile_and_multiplicity"]
        self.assertEqual(k2["p_ge18_dec6"], "0.012089")
        self.assertFalse(k2["p_ge18_le_1pct"])
        self.assertEqual(k2["p_ge19_dec6"], "0.005823")
        self.assertTrue(k2["p_ge19_le_1pct"])
        self.assertEqual(k2["fwer_21_classes_at_k18_dec6"], "0.225413")

    def test_pillar2_ordinal_symmetry_and_offset_leakage(self) -> None:
        p2 = prc.analyze_pillar2_ordinal_symmetry_and_offset_leakage()
        b = p2["burnside_s4_v4_orbits"]
        self.assertEqual(b["num_orbits"], 8)
        self.assertEqual(b["orbit_sizes"], [2, 2, 2, 2, 4, 4, 4, 4])
        self.assertTrue(b["matches_prereg_l105_eight_classes"])
        self.assertEqual(b["simplex_dof_per_level"], 7)

        rp = p2["prereg02_rp_symmetry_obstruction"]
        self.assertTrue(rp["all_lags_u_zero"])
        self.assertTrue(rp["time_reversal_swaps_counts_exact"])
        self.assertTrue(rp["rp_rotation_preserves_all_six_counts_exact"])
        self.assertEqual(rp["sawtooth_by_tau"][-1]["ties"], 240)

        off = p2["prereg03_end_match_offset_leakage"]
        self.assertEqual(off["raw_costs"], ["1/1", "65/1", "5/1"])
        self.assertEqual(off["raw_best_offset"], 0)
        self.assertEqual(off["mapped_costs"], ["110224/1", "1103684/1", "104/1"])
        self.assertEqual(off["mapped_best_offset"], 2)
        self.assertTrue(off["monotone_map_changes_selected_offset"])
        self.assertEqual(off["rank_best_offset_raw"], 0)
        self.assertEqual(off["rank_best_offset_mapped"], 0)
        self.assertTrue(off["rank_fix_restores_exact_invariance"])

    def test_pillar3_data_budgets_and_scale_flow(self) -> None:
        p3 = prc.analyze_pillar3_data_budgets_and_scale_flow()
        dr = p3["data_request_byte_sums"]
        self.assertTrue(dr["waves_fit_matches_claimed"])
        self.assertTrue(dr["waves_verdict_matches_claimed"])
        self.assertTrue(dr["total_matches_claimed"])
        self.assertTrue(dr["drop_l1_fit_matches_claimed"])
        self.assertEqual(p3["waves_max_avg_cadence_for_12_blocks_sec"], "600/11")

        by_name = {r["instrument_case"]: r for r in p3["scale_flow_sample_budgets"]}
        self.assertEqual(by_name["GW_4096s_4096Hz"]["max_scale_flow_level"], 8)
        self.assertEqual(by_name["SEIS_VBB_1day_20Hz"]["max_scale_flow_level"], 5)
        self.assertEqual(by_name["TESS_27d_20s_nogap_upper_bound"]["max_scale_flow_level"], 1)
        self.assertEqual(by_name["TESS_27d_20s_nogap_upper_bound"]["min_zero_padded_t1_features_of_56"], 40)
        self.assertEqual(by_name["WAVES_8d_4ch_60s_cadence"]["max_scale_flow_level"], -1)
        self.assertEqual(by_name["WAVES_8d_4ch_192s_cadence"]["blocks_level0"], 3)

        rungs = {r["order_d"]: r for r in p3["arm_b_finite_sample_rungs"]}
        self.assertTrue(rungs[4]["fits_single_4096_segment"])
        self.assertFalse(rungs[5]["fits_single_4096_segment"])
        self.assertFalse(rungs[6]["fits_32_pooled_fit_segments_131072"])

    def test_pillar4_certifier_receipts(self) -> None:
        p4 = prc.analyze_pillar4_certifiers_and_kf_cross_audit()
        aw = p4["prereg_certifier_as_written"]
        self.assertFalse(aw["certified"])
        self.assertEqual(
            aw["violations"],
            [
                "PREREG01_EXCESS_CONTROL_FALSE_INVALIDATION",
                "PREREG01_EXPERIMENT_FALSE_INVALID_EXCEEDED",
                "PREREG01B_K2_PER_CLASS_ALPHA_EXCEEDED",
                "PREREG01B_K2_FWER_EXCEEDED",
                "PREREG02_TIME_EVEN_TRANSFER_DILUTION",
                "PREREG03_RAW_END_MATCH_MONOTONE_LEAKAGE",
                "PREREG04_ZERO_PADDED_PERM_DILUTION",
            ],
        )
        hd = p4["prereg_certifier_hardened"]
        self.assertTrue(hd["certified"])
        self.assertEqual(hd["violations"], [])
        self.assertTrue(hd["min_reachable_presence_p_reaches_holm"])

        kf_bad = p4["kf_cross_audit_automerge_loophole_and_lenton"]
        self.assertFalse(kf_bad["admitted"])
        self.assertEqual(
            kf_bad["violations"],
            ["KF03D_INFLIGHT_STALE_READ_UNNOTIFIED", "KF04_HIGH_IMPACT_LAYER_REQUIRES_SIGNOFF"],
        )
        kf_ok = p4["kf_cross_audit_hardened_admitted"]
        self.assertTrue(kf_ok["admitted"])
        self.assertEqual(p4["audit_076r_blast_radius_ge1_dec6"], "0.997877")


class TestRedTeamCertifierGates(unittest.TestCase):
    def _valid_prereg(self, **overrides: object) -> dict[str, object]:
        base: dict[str, object] = {
            "segments_per_instrument": 32,
            "segment_alpha": Fraction(1, 20),
            "control_k_limit": 6,
            "control_rate_cap": Fraction(1, 10),
            "control_combine_mode": "binom_only",
            "num_controls_per_instrument": 3,
            "calibrated_instruments": 3,
            "required_support_quorum": 3,
            "max_per_instrument_false_invalid": Fraction(1, 20),
            "rank_end_matching": True,
            "split_time_odd_transfer": True,
            "restrict_perm_to_joint_support": True,
            "k2_seeds": 200,
            "k2_max_rejects": 20,
            "k2_num_classes": 21,
            "max_k2_per_class_alpha": Fraction(1, 100),
        }
        base.update(overrides)
        return base

    def _valid_kf(self, **overrides: object) -> dict[str, object]:
        base: dict[str, object] = {
            "actor_role": "gardener",
            "reviewer_role": "independent_reviewer",
            "target_layer": "skill",
            "source_integrity": 3,
            "target_required_integrity": 3,
            "source_confidentiality": 0,
            "target_max_confidentiality": 0,
            "human_signoff": True,
            "outside_err_before": Fraction(1, 4),
            "outside_err_after": Fraction(1, 4),
            "proxy_err_before": Fraction(1, 1),
            "proxy_err_after": Fraction(1, 1),
            "store_epoch": 1,
            "butler_loaded_epoch": 1,
            "in_flight_nudge_sent": False,
        }
        base.update(overrides)
        return base

    def test_prereg_certifier_modes_boundaries_and_refusals(self) -> None:
        # Exact "or" combine mode + exact equality boundaries:
        # alpha_seg**s_seg == 1/560, p_inst == max_false_inv, p_k2_class_fail == max_k2_alpha
        ok_exact_holm = prc.certify_prereg_protocol(
            self._valid_prereg(
                segments_per_instrument=1,
                segment_alpha=Fraction(1, 560),
                control_k_limit=1,
                control_rate_cap=Fraction(1, 2),
                control_combine_mode="or",
                num_controls_per_instrument=1,
                calibrated_instruments=1,
                required_support_quorum=1,
                max_per_instrument_false_invalid=Fraction(1, 560),
                k2_seeds=1,
                k2_max_rejects=0,
                k2_num_classes=1,
                max_k2_per_class_alpha=Fraction(1, 560),
            )
        )
        self.assertTrue(ok_exact_holm["certified"])
        self.assertEqual(ok_exact_holm["effective_control_fail_k"], 1)
        self.assertTrue(ok_exact_holm["min_reachable_presence_p_reaches_holm"])

        # Exact closed boundaries on MAX_EXPERIMENT_FALSE_INVALID == 1/10 and MAX_K2_FWER == 1/10
        bd_fwer = prc.certify_prereg_protocol(
            self._valid_prereg(
                segments_per_instrument=1,
                segment_alpha=Fraction(1, 10),
                control_k_limit=1,
                control_rate_cap=Fraction(1, 2),
                num_controls_per_instrument=1,
                calibrated_instruments=1,
                required_support_quorum=1,
                max_per_instrument_false_invalid=Fraction(1, 10),
                k2_seeds=1,
                k2_max_rejects=0,
                k2_num_classes=1,
                max_k2_per_class_alpha=Fraction(1, 10),
            )
        )
        self.assertEqual(bd_fwer["violations"], ["PREREG04_ZERO_HOLM_PRESENCE_POWER"])
        self.assertFalse(bd_fwer["min_reachable_presence_p_reaches_holm"])

        # Verify "or" picks max(k_lim, rate_fail_k) > k_lim when rate_fail_k > k_lim
        ok_or_max = prc.certify_prereg_protocol(
            self._valid_prereg(
                segments_per_instrument=20,
                control_k_limit=2,
                control_rate_cap=Fraction(1, 4),
                control_combine_mode="or",
            )
        )
        self.assertEqual(ok_or_max["effective_control_fail_k"], 6)

        # PREREG-BUG-01 repros: vacuous control_k_limit=32 + k2_max_rejects=199, and "or" rate_cap=31/32
        vac_a = prc.certify_prereg_protocol(
            self._valid_prereg(control_k_limit=32, k2_max_rejects=199)
        )
        self.assertFalse(vac_a["certified"])
        self.assertIn("PREREG01_VACUOUS_CONTROL_THRESHOLD", vac_a["violations"])
        self.assertIn("PREREG01B_VACUOUS_K2_THRESHOLD", vac_a["violations"])

        vac_b = prc.certify_prereg_protocol(
            self._valid_prereg(control_combine_mode="or", control_rate_cap=Fraction(31, 32))
        )
        self.assertFalse(vac_b["certified"])
        self.assertIn("PREREG01_VACUOUS_CONTROL_THRESHOLD", vac_b["violations"])

        # Exact closed vacuity boundaries: 2*(eff_fail_k-1) == S (fails) vs S-1 (passes); 4*k2_max_rej == k2_seeds (fails)
        vac_bd = prc.certify_prereg_protocol(
            self._valid_prereg(segments_per_instrument=4, control_k_limit=3, k2_seeds=4, k2_max_rejects=1)
        )
        self.assertIn("PREREG01_VACUOUS_CONTROL_THRESHOLD", vac_bd["violations"])
        self.assertIn("PREREG01B_VACUOUS_K2_THRESHOLD", vac_bd["violations"])
        nonvac_bd = prc.certify_prereg_protocol(
            self._valid_prereg(segments_per_instrument=5, control_k_limit=3, k2_seeds=5, k2_max_rejects=1)
        )
        self.assertNotIn("PREREG01_VACUOUS_CONTROL_THRESHOLD", nonvac_bd["violations"])
        self.assertNotIn("PREREG01B_VACUOUS_K2_THRESHOLD", nonvac_bd["violations"])

        # PREREG-BUG-02 repro: k2_num_classes=1000, calibrated_instruments=100 -> rejected on FWER & exp false invalid!
        bug2 = prc.certify_prereg_protocol(
            self._valid_prereg(k2_num_classes=1000, calibrated_instruments=100)
        )
        self.assertFalse(bug2["certified"])
        self.assertIn("PREREG01_EXPERIMENT_FALSE_INVALID_EXCEEDED", bug2["violations"])
        self.assertIn("PREREG01B_K2_FWER_EXCEEDED", bug2["violations"])

        # PREREG-BUG-03 repro: S=1 at alpha=1/20 -> zero Holm presence power!
        bug3 = prc.certify_prereg_protocol(
            self._valid_prereg(
                segments_per_instrument=1,
                control_k_limit=1,
                num_controls_per_instrument=1,
                max_per_instrument_false_invalid=Fraction(1, 10),
            )
        )
        self.assertFalse(bug3["certified"])
        self.assertIn("PREREG04_ZERO_HOLM_PRESENCE_POWER", bug3["violations"])

        # Insufficient quorum violation
        bad_q = prc.certify_prereg_protocol(self._valid_prereg(calibrated_instruments=2, required_support_quorum=3))
        self.assertFalse(bad_q["certified"])
        self.assertIn("PREREG04_INSUFFICIENT_INSTRUMENT_QUORUM", bad_q["violations"])

        # Boundary k_lim == S (accepted by range check, flagged vacuous), k2_max_rejects == k2_seeds - 1 (same)
        bd_kmax = prc.certify_prereg_protocol(
            self._valid_prereg(segments_per_instrument=2, control_k_limit=2, k2_seeds=2, k2_max_rejects=1)
        )
        self.assertFalse(bd_kmax["certified"])
        self.assertIn("PREREG01_VACUOUS_CONTROL_THRESHOLD", bd_kmax["violations"])
        self.assertIn("PREREG01B_VACUOUS_K2_THRESHOLD", bd_kmax["violations"])

        # Schema & range refusals (including vacuous-control k_lim == S + 1 and rate_cap == 1!)
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-spec-dict"):
            prc.certify_prereg_protocol(["bad"])
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-unknown-keys:extra"):
            prc.certify_prereg_protocol(self._valid_prereg(extra=1))
        missing = self._valid_prereg()
        del missing["k2_seeds"]
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-missing-keys:k2_seeds"):
            prc.certify_prereg_protocol(missing)
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-segments-pos"):
            prc.certify_prereg_protocol(self._valid_prereg(segments_per_instrument=0))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-alpha-range"):
            prc.certify_prereg_protocol(self._valid_prereg(segment_alpha=Fraction(0, 1)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-alpha-range"):
            prc.certify_prereg_protocol(self._valid_prereg(segment_alpha=Fraction(1, 1)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-k-limit-range"):
            prc.certify_prereg_protocol(self._valid_prereg(control_k_limit=0))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-k-limit-range"):
            prc.certify_prereg_protocol(self._valid_prereg(control_k_limit=33))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-rate-cap-range"):
            prc.certify_prereg_protocol(self._valid_prereg(control_rate_cap=Fraction(0, 1)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-rate-cap-range"):
            prc.certify_prereg_protocol(self._valid_prereg(control_rate_cap=Fraction(1, 1)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"exact-choice:control_combine_mode"):
            prc.certify_prereg_protocol(self._valid_prereg(control_combine_mode=" AND "))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-num-controls-pos"):
            prc.certify_prereg_protocol(self._valid_prereg(num_controls_per_instrument=0))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-num-instruments-pos"):
            prc.certify_prereg_protocol(self._valid_prereg(calibrated_instruments=0))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-quorum-pos"):
            prc.certify_prereg_protocol(self._valid_prereg(required_support_quorum=0))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-max-false-inv-range"):
            prc.certify_prereg_protocol(self._valid_prereg(max_per_instrument_false_invalid=Fraction(0, 1)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-max-false-inv-range"):
            prc.certify_prereg_protocol(self._valid_prereg(max_per_instrument_false_invalid=Fraction(1, 1)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"exact-bool:rank_end_matching"):
            prc.certify_prereg_protocol(self._valid_prereg(rank_end_matching=1))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-k2-seeds-pos"):
            prc.certify_prereg_protocol(self._valid_prereg(k2_seeds=0))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-k2-max-rej-range"):
            prc.certify_prereg_protocol(self._valid_prereg(k2_max_rejects=-1))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-k2-max-rej-range"):
            prc.certify_prereg_protocol(self._valid_prereg(k2_max_rejects=200))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-k2-classes-pos"):
            prc.certify_prereg_protocol(self._valid_prereg(k2_num_classes=0))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-max-k2-alpha-range"):
            prc.certify_prereg_protocol(self._valid_prereg(max_k2_per_class_alpha=Fraction(0, 1)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"prereg-max-k2-alpha-range"):
            prc.certify_prereg_protocol(self._valid_prereg(max_k2_per_class_alpha=Fraction(1, 1)))

    def test_kf_governor_boundaries_attacks_and_refusals(self) -> None:
        # Clean boundary values: integrity 1..4, conf 0..2, errors 0, ephemeral auto-merge OK
        ok_eph = prc.certify_knowledge_factory_promotion(
            self._valid_kf(
                target_layer="ephemeral_memory",
                source_integrity=4,
                target_required_integrity=1,
                source_confidentiality=2,
                target_max_confidentiality=2,
                human_signoff=False,
                outside_err_before=Fraction(0, 1),
                outside_err_after=Fraction(0, 1),
                proxy_err_before=Fraction(0, 1),
                proxy_err_after=Fraction(0, 1),
            )
        )
        self.assertTrue(ok_eph["admitted"])

        # Exact min/max boundary source_integrity 0 and 4, source_confidentiality 3 -> caught by Biba/BLP (not range error)
        biba_zero = prc.certify_knowledge_factory_promotion(
            self._valid_kf(source_integrity=0, target_required_integrity=3, source_confidentiality=3)
        )
        self.assertEqual(
            biba_zero["violations"], ["KF01_BIBA_INTEGRITY_ESCALATION", "KF01_BLP_CONFIDENTIALITY_LEAK"]
        )
        ok_int4 = prc.certify_knowledge_factory_promotion(
            self._valid_kf(source_integrity=4, target_required_integrity=4)
        )
        self.assertTrue(ok_int4["admitted"])

        # All 7 violation flags triggered cleanly (with valid domain_knowledge layer bounds: req_int=2, max_conf=1)
        bad_all = prc.certify_knowledge_factory_promotion(
            self._valid_kf(
                actor_role="butler",
                reviewer_role="gardener",
                target_layer="domain_knowledge",
                source_integrity=1,
                target_required_integrity=2,
                source_confidentiality=2,
                target_max_confidentiality=1,
                human_signoff=False,
                outside_err_before=Fraction(1, 4),
                outside_err_after=Fraction(1, 2),
                proxy_err_before=Fraction(1, 2),
                proxy_err_after=Fraction(3, 4),
                store_epoch=3,
                butler_loaded_epoch=2,
                in_flight_nudge_sent=False,
            )
        )
        self.assertEqual(
            bad_all["violations"],
            [
                "KF00_BUTLER_DIRECT_WRITE_FORBIDDEN",
                "KF01_BIBA_INTEGRITY_ESCALATION",
                "KF01_BLP_CONFIDENTIALITY_LEAK",
                "KF02_GOODHART_OUTSIDE_ANCHOR_DRIFT",
                "KF02_PROXY_REGRESSION",
                "KF03D_INFLIGHT_STALE_READ_UNNOTIFIED",
                "KF04_HIGH_IMPACT_LAYER_REQUIRES_SIGNOFF",
            ],
        )

        # Self-approval refusal
        self_app = prc.certify_knowledge_factory_promotion(
            self._valid_kf(actor_role="gardener", reviewer_role="gardener")
        )
        self.assertEqual(self_app["violations"], ["KF05_CURATOR_SELF_APPROVAL_FORBIDDEN"])

        # Layer policy spoofing refusals (cannot weaken req_int or raise max_conf below/above layer floor/ceiling!)
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-layer-integrity-floor"):
            prc.certify_knowledge_factory_promotion(
                self._valid_kf(target_layer="skill", source_integrity=0, target_required_integrity=2)
            )
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-layer-integrity-floor"):
            prc.certify_knowledge_factory_promotion(
                self._valid_kf(target_layer="ephemeral_memory", source_integrity=0, target_required_integrity=0)
            )
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-layer-conf-ceiling"):
            prc.certify_knowledge_factory_promotion(
                self._valid_kf(target_layer="skill", source_confidentiality=1, target_max_confidentiality=1)
            )
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-layer-conf-ceiling"):
            prc.certify_knowledge_factory_promotion(
                self._valid_kf(
                    target_layer="ephemeral_memory",
                    target_required_integrity=1,
                    source_confidentiality=3,
                    target_max_confidentiality=3,
                )
            )

        # Schema & range refusals
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-proposal-dict"):
            prc.certify_knowledge_factory_promotion("nope")
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-unknown-keys:extra"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(extra=1))
        miss = self._valid_kf()
        del miss["store_epoch"]
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-missing-keys:store_epoch"):
            prc.certify_knowledge_factory_promotion(miss)
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-integrity-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(source_integrity=-1))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-integrity-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(source_integrity=5))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-integrity-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(target_required_integrity=-1))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-integrity-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(target_required_integrity=5))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-conf-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(source_confidentiality=-1))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-conf-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(source_confidentiality=4))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-conf-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(target_max_confidentiality=-1))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-conf-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(target_max_confidentiality=4))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-err-nonneg"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(outside_err_before=Fraction(-1, 10)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-err-nonneg"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(outside_err_after=Fraction(-1, 10)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-err-nonneg"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(proxy_err_before=Fraction(-1, 10)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-err-nonneg"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(proxy_err_after=Fraction(-1, 10)))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-epoch-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(store_epoch=0, butler_loaded_epoch=0))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-epoch-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(store_epoch=2, butler_loaded_epoch=0))
        with self.assertRaisesRegex(prc.PreregAuditError, r"kf-epoch-range"):
            prc.certify_knowledge_factory_promotion(self._valid_kf(store_epoch=2, butler_loaded_epoch=3))


class TestLivePortalAuditAndCLI(unittest.TestCase):
    def _build_synthetic_portals(self, root: Path) -> dict[str, dict[str, object]]:
        digests: dict[str, dict[str, object]] = {}
        for rel_path in prc.PINNED_PORTAL_DIGESTS:
            fp = root / rel_path
            fp.parent.mkdir(parents=True, exist_ok=True)
            lines = ["line"] * 320
            for _, a_rel, line_no, needle in prc.VERBATIM_ANCHORS:
                if a_rel == rel_path:
                    lines[line_no - 1] = needle
            fp.write_text("\n".join(lines) + "\n", encoding="utf-8")
            raw = fp.read_bytes()
            digests[rel_path] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        return digests

    def test_portal_verifier_tamper_and_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "symbiosis"
            with self.assertRaisesRegex(prc.PreregAuditError, r"symbiosis-root-missing"):
                prc.audit_live_portals(root)

            root.mkdir()
            digests = self._build_synthetic_portals(root)
            with patch.object(prc, "PINNED_PORTAL_DIGESTS", digests):
                ok = prc.audit_live_portals(root)
                self.assertEqual(ok["verified_files"], len(digests))
                self.assertEqual(ok["verified_anchors"], len(prc.VERBATIM_ANCHORS))

            # Symlink escape outside root
            outside = Path(tmp) / "outside.txt"
            outside.write_text("escape\n", encoding="utf-8")
            first_rel = next(iter(digests))
            target = root / first_rel
            target.unlink()
            target.symlink_to(outside)
            with patch.object(prc, "PINNED_PORTAL_DIGESTS", digests):
                with self.assertRaisesRegex(prc.PreregAuditError, r"portal-path-escape"):
                    prc.audit_live_portals(root)
            target.unlink()

            # Missing file, bytes mismatch, sha256 mismatch
            with patch.object(prc, "PINNED_PORTAL_DIGESTS", digests):
                with self.assertRaisesRegex(prc.PreregAuditError, r"portal-file-missing"):
                    prc.audit_live_portals(root)

            digests = self._build_synthetic_portals(root)
            raw = target.read_bytes()
            target.write_bytes(b"X" + raw[1:])
            with patch.object(prc, "PINNED_PORTAL_DIGESTS", digests):
                with self.assertRaisesRegex(prc.PreregAuditError, r"portal-sha256-mismatch"):
                    prc.audit_live_portals(root)
            target.write_bytes(raw + b"!")
            with patch.object(prc, "PINNED_PORTAL_DIGESTS", digests):
                with self.assertRaisesRegex(prc.PreregAuditError, r"portal-bytes-mismatch"):
                    prc.audit_live_portals(root)

            # Anchor mismatch, line range, and exact closed boundary line_no == 1 == len(lines)
            digests = self._build_synthetic_portals(root)
            prereg_rel = "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md"
            prereg_p = root / prereg_rel
            prereg_p.write_text("onlyone\n", encoding="utf-8")
            raw_one = prereg_p.read_bytes()
            digests[prereg_rel] = {"bytes": len(raw_one), "sha256": hashlib.sha256(raw_one).hexdigest()}
            with patch.object(prc, "PINNED_PORTAL_DIGESTS", digests):
                with self.assertRaisesRegex(prc.PreregAuditError, r"anchor-line-range:PREREG-LAPLACE"):
                    prc.audit_live_portals(root)
                with patch.object(prc, "VERBATIM_ANCHORS", (("BD-1", prereg_rel, 1, "onlyone"),)):
                    ok_bd = prc.audit_live_portals(root)
                    self.assertEqual(ok_bd["verified_anchors"], 1)
                with patch.object(prc, "VERBATIM_ANCHORS", (("BD-BAD", prereg_rel, 1, "missing"),)):
                    with self.assertRaisesRegex(prc.PreregAuditError, r"anchor-text-mismatch:BD-BAD"):
                        prc.audit_live_portals(root)

    def test_standalone_zero_float_cli_and_live_workspace(self) -> None:
        c1 = prc.build_certificate(symbiosis_root=None)
        c2 = prc.build_certificate(symbiosis_root=None)
        self.assertEqual(c1["certificate_sha256"], c2["certificate_sha256"])

        def _reject_float(token: str) -> None:
            raise AssertionError(f"float-found:{token}")

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "cert.json"
            buf_json = io.StringIO()
            with patch("sys.stdout", buf_json):
                rc = prc.main(["--json", "--write-cert", str(out_path)])
            self.assertEqual(rc, 0)
            written = out_path.read_text(encoding="utf-8")
            self.assertEqual(buf_json.getvalue(), written)
            parsed = json.loads(written, parse_float=_reject_float)
            self.assertEqual(parsed["certificate_sha256"], c1["certificate_sha256"])

            buf_human = io.StringIO()
            with patch("sys.stdout", buf_human):
                rc_h = prc.main([])
            self.assertEqual(rc_h, 0)
            self.assertIn(prc.AUDIT_ID, buf_human.getvalue())
            self.assertIn(c1["certificate_sha256"], buf_human.getvalue())

        sym_root = Path(__file__).resolve().parent.parent.parent
        if (sym_root / "round10" / "portals" / "cave-expedition" / "pr_6.md").is_file():
            live_c = prc.build_certificate(symbiosis_root=sym_root)
            self.assertEqual(live_c["live_portal_verification"]["verified_files"], 10)
            self.assertEqual(live_c["live_portal_verification"]["verified_anchors"], 18)


if __name__ == "__main__":
    unittest.main()
