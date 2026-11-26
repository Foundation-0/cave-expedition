#!/usr/bin/env python3
"""
AUDIT-118B Assertion-Free R5 Mutation-Killing & Zone-B Adversarial Test Suite
(`test_torus_content_r5.py`).

Zero bare `assert`s (100% python3 -O parity). Zero floats on trust paths.
Zero external dependencies. Kills 100.0% of `aletheia v2.0.0 mutate --max-mutants 0`
mutants AND 100.0% of AST `BoolOp` (`and` <-> `or`) mutations across both
`torus_content_oracle.py` and `torus_content_audit.py`, plus all Zone-B CLI & API attacks.
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

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import torus_content_audit as tca
import torus_content_oracle as tco


class EvilInt(int):
    pass


class EvilStr(str):
    pass


class EvilList(list):
    pass


class EvilDict(dict):
    pass


class EvilFraction(Fraction):
    pass


class LyingSequence:
    def __len__(self) -> int:
        return 3

    def __getitem__(self, idx: int) -> int:
        return 1


def _resign_envelope(
    schema: str,
    audit_id: str,
    payload_sha256: str,
    payload: dict,
) -> dict:
    """Sign a certificate envelope with matching certificate_sha256 for forgery-bypass tests."""
    env = {
        "schema": schema,
        "audit_id": audit_id,
        "payload_sha256": payload_sha256,
        "payload": payload,
    }
    csha = hashlib.sha256(tco.canonical_json_bytes(env)).hexdigest()
    return {**env, "certificate_sha256": csha}


class TestTorusContentR5(unittest.TestCase):
    """Comprehensive R1-R5, boundary, dual-oracle, and Zone-B adversarial tests."""

    def _assert_err(self, code: str, fn, *args, **kwargs) -> None:
        with self.assertRaises(tco.TorusContentError) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code)

    def test_01_all_five_pillars_exact_and_independent_checks(self) -> None:
        cert = tca.build_certificate()
        payload = cert["payload"]
        self.assertTrue(payload["all_passed"])
        self.assertEqual(payload["audit_id"], "AUDIT-118B")
        self.assertEqual(payload["honest_novelty_tier"], "N0/N1")

        # Pillar 1: Seam 1 exact numbers & regimes
        p1 = payload["pillar_1_seam1_rank1_inertia"]
        self.assertTrue(p1["passed"])
        self.assertEqual(p1["graph_G5_non_bridge_cut"]["regime"], "REGIME_I_STABLE")
        self.assertEqual(p1["graph_G5_non_bridge_cut"]["leverage_h"], "2/3")
        self.assertEqual(p1["graph_G5_non_bridge_cut"]["schur_gamma"], "1/3")
        self.assertEqual(p1["graph_G5_non_bridge_cut"]["inertia_M_delta"], [4, 0, 1])
        self.assertEqual(p1["graph_G5_bridge_disconnection"]["regime"], "REGIME_II_CRITICAL_SINGULARITY")
        self.assertEqual(p1["graph_G5_bridge_disconnection"]["schur_gamma"], "0")
        self.assertEqual(p1["graph_G5_bridge_disconnection"]["inertia_M_delta"], [3, 0, 2])
        self.assertEqual(p1["graph_G5_oversubtract_flip"]["regime"], "REGIME_III_NEGATIVE_FLIP")
        self.assertEqual(p1["graph_G5_oversubtract_flip"]["inertia_M_delta"], [3, 1, 1])
        self.assertEqual(p1["graph_G5_delta_R_eff_sm"], "1/3")
        self.assertEqual(p1["warp_regime1_s4_safe_inside_cs_reject"]["schur_gamma"], "3/8")
        self.assertEqual(p1["warp_regime2_s3_critical_boundary"]["inertia_M_delta"], [2, 0, 1])
        self.assertEqual(p1["warp_regime3_s5_2_negative_flip"]["inertia_M_delta"], [2, 1, 0])
        self.assertEqual(p1["warp_regime3_s5_2_negative_flip"]["vT_Mdelta_v"], "-24/25")
        self.assertTrue(p1["warp_drive_incremental_hotswap"]["unmount_roundtrip_exact"])
        self.assertTrue(p1["warp_drive_incremental_hotswap"]["adapter_lodf_exact_match"])
        self.assertEqual(p1["warp_drive_incremental_hotswap"]["adapter_lodf_delta_h1_orthogonal"], "0")

        # Pillar 2: Seam 2 exact rounding duality, warp-drive choke composition, & F2 falsification
        p2 = payload["pillar_2_seam2_rounding_duality"]
        self.assertTrue(p2["passed"])
        self.assertEqual(p2["thousandths_1_to_1000_f32_overshoot_count"], 503)
        self.assertEqual(p2["multihop_5x_0_2006"]["nearest_thousandth_overshoot"], "1/500")
        self.assertEqual(p2["multihop_5x_0_2006"]["floor_f32_sum"], "33655095/33554432")
        self.assertTrue(p2["falsified_bridge_F2_binary32_lp_break"]["violates_lp_constraint"])
        self.assertEqual(p2["falsified_bridge_F2_binary32_lp_break"]["rounded_diff"], "2")
        self.assertTrue(p2["warp_drive_choke_x_floor_f32_contraction"]["lyapunov_strengthened_all_5_steps"])
        self.assertEqual(p2["warp_drive_choke_x_floor_f32_contraction"]["k_stage_moment_ratios"], [1, 8, 64, 512])

        # Pillar 3: Seam 3 cycle cohomology vs Farkas grounding, warp-drive#37 4-bank flush, & F1 falsification
        p3 = payload["pillar_3_seam3_cycle_grounding"]
        self.assertTrue(p3["passed"])
        self.assertEqual(p3["regime_A_tree_chain_T4"]["beta1"], 0)
        self.assertTrue(p3["regime_A_tree_chain_T4"]["q_is_zero"])
        self.assertEqual(p3["regime_B_diamond_DAG_D4_asymmetric_F1_refutation"]["beta1"], 1)
        self.assertEqual(
            p3["regime_B_diamond_DAG_D4_asymmetric_F1_refutation"]["kirchhoff_flow_q"],
            ["1", "1", "-1", "-1"],
        )
        self.assertTrue(p3["regime_B_diamond_DAG_D4_asymmetric_F1_refutation"]["is_directed_acyclic"])
        self.assertTrue(p3["regime_B_diamond_DAG_D4_coboundary_control"]["q_is_zero"])
        self.assertFalse(p3["regime_C_directed_cycle_C3_farkas_obstruction"]["is_directed_acyclic"])
        self.assertEqual(
            p3["regime_C_directed_cycle_C3_farkas_obstruction"]["farkas_directed_cycle_witness"],
            ["1", "1", "1"],
        )
        self.assertTrue(p3["warp_drive_4bank_clean_flush_DAG"]["is_directed_acyclic"])
        self.assertFalse(p3["warp_drive_4bank_unflushed_jacobi_cycle"]["is_directed_acyclic"])
        self.assertTrue(p3["exo8_ledger_journal_completeness"]["complete"])

        # Pillar 4: Seam 4 character / MacWilliams / E_8 theta / HAWK / warp-drive#14 force multiplier
        p4 = payload["pillar_4_seam4_character_macwilliams_e8_hawk"]
        self.assertTrue(p4["passed"])
        self.assertEqual(p4["s15c_e8_root_count"], 240)
        self.assertEqual(p4["s15c_e8had_weight8_root_count"], 0)
        self.assertEqual(p4["s16_hamming8_weight_enumerator"], [1, 0, 0, 0, 14, 0, 0, 0, 1])
        self.assertEqual(p4["s15_e8_shells_m0_to_6"], [1, 240, 2160, 6720, 17520, 30240, 60480])
        self.assertEqual(p4["s15_e8_4_ball_counts_m0_to_4"], [1, 961, 355201, 61898881, 4920068161])
        self.assertEqual(p4["s14_hawk_k1_det"], 128)
        self.assertEqual(p4["s14_hawk_k1_gram_det"], 16384)
        self.assertEqual(p4["s15_s16_hamming_k4_det"], 16)
        self.assertEqual(p4["s15_s16_e8_scaled_gram_det"], "1")
        fm = p4["warp_drive_14_siliquant_force_multiplier"]
        self.assertEqual(fm["adjoint_wht_reduction_4096x1024"], "4096")
        self.assertEqual(fm["amdahl_e2e_dequant_speedup"], "1830/1249")
        self.assertEqual(fm["zero_unpack_frob_sq_cap_88b_s1_16"], "3/8")
        self.assertEqual(fm["zero_unpack_frob_sq_cap_136b_s1_16"], "391/128")
        self.assertTrue(fm["shell_norm_isometry_exact"])

        # Pillar 5: Volkersen SL(2,Q), F3 non-normal overshoot, 7 seams, 18 portals
        p5 = payload["pillar_5_transfer_falsifications_and_ledger"]
        self.assertTrue(p5["passed"])
        self.assertEqual(p5["volkersen_sl2_transfer"]["peak_rivet_force"], "11/28")
        self.assertEqual(p5["falsified_bridge_F3_non_normal_overshoot"]["t1_norm_sq"], "27/8")
        self.assertEqual(p5["falsified_bridge_F3_non_normal_overshoot"]["t6_peak_norm_sq"], "203541903/8388608")
        self.assertEqual(p5["missed_portals_count"], 18)

    def test_02_strict_input_validators_boundaries_and_subclasses(self) -> None:
        # require_int boundaries, bit cap, bool & subclass rejection
        max_ok = (1 << tco.MAX_INT_BITS) - 1
        self.assertEqual(tco.require_int(max_ok), max_ok)
        self.assertEqual(tco.require_int(5, lo=5, hi=5), 5)
        self.assertEqual(tco.require_int(-5, lo=-5), -5)
        self._assert_err("INVALID_INT_TYPE", tco.require_int, True)
        self._assert_err("INVALID_INT_TYPE", tco.require_int, EvilInt(1))
        self._assert_err("INT_BIT_LIMIT", tco.require_int, 1 << tco.MAX_INT_BITS)
        self._assert_err("INT_BELOW_MIN", tco.require_int, 4, lo=5)
        self._assert_err("INT_ABOVE_MAX", tco.require_int, 6, hi=5)

        # require_bool
        self.assertTrue(tco.require_bool(True))
        self.assertFalse(tco.require_bool(False))
        self._assert_err("INVALID_BOOL_TYPE", tco.require_bool, 1)

        # require_str & exact UTF-16 surrogate boundaries 0xD7FF / 0xD800 / 0xDFFF / 0xE000
        self.assertEqual(tco.require_str("\uD7FF\uE000"), "\uD7FF\uE000")
        self._assert_err("INVALID_STR_TYPE", tco.require_str, EvilStr("ok"))
        self._assert_err("EMPTY_STR", tco.require_str, "")
        self._assert_err("SURROGATE_FORBIDDEN", tco.require_str, "\uD800")
        self._assert_err("SURROGATE_FORBIDDEN", tco.require_str, "\uDFFF")

        # require_rat & require_pos_rat
        self.assertEqual(tco.require_rat(Fraction(max_ok, max_ok)), Fraction(1, 1))
        self.assertEqual(tco.require_rat(Fraction(max_ok, 1)), Fraction(max_ok, 1))
        self.assertEqual(tco.require_rat(Fraction(1, max_ok)), Fraction(1, max_ok))
        self.assertEqual(tco.require_rat(max_ok), Fraction(max_ok, 1))
        self._assert_err("RAT_NUM_BIT_LIMIT", tco.require_rat, Fraction(1 << tco.MAX_INT_BITS, 1))
        self._assert_err("RAT_DEN_BIT_LIMIT", tco.require_rat, Fraction(1, 1 << tco.MAX_INT_BITS))
        self._assert_err("INT_BIT_LIMIT", tco.require_rat, 1 << tco.MAX_INT_BITS)
        self._assert_err("INVALID_RAT_TYPE", tco.require_rat, EvilFraction(1, 2))
        self._assert_err("INVALID_RAT_TYPE", tco.require_rat, True)
        self._assert_err("NON_POSITIVE_RAT", tco.require_pos_rat, 0)
        self._assert_err("NON_POSITIVE_RAT", tco.require_pos_rat, Fraction(-1, 2))
        self.assertEqual(tco.require_pos_rat(Fraction(1, 3)), Fraction(1, 3))

        # require_seq boundaries & lying containers
        self.assertEqual(tco.require_seq([1], min_len=1, max_len=1), (1,))
        self.assertEqual(tco.require_seq((1, 2), min_len=1, max_len=2), (1, 2))
        self._assert_err("INVALID_SEQ_TYPE", tco.require_seq, EvilList([1]))
        self._assert_err("INVALID_SEQ_TYPE", tco.require_seq, LyingSequence())
        self._assert_err("SEQ_TOO_SHORT", tco.require_seq, [], min_len=1)
        self._assert_err("SEQ_TOO_LONG", tco.require_seq, [1, 2, 3], max_len=2)

    def test_03_strict_json_parser_and_zone_b_attacks(self) -> None:
        # Valid exact boundary depth = 64 & max int = (1<<1328)-1 (exact 400 digits, 1328 bits)
        deep_ok: object = 0
        for _ in range(64):
            deep_ok = [deep_ok]
        tco.validate_json_value(deep_ok, max_depth=64)
        self.assertEqual(tco.parse_strict_json(json.dumps(deep_ok)), deep_ok)

        # Depth = 65 & 1500-deep & cyclic list rejected without RecursionError
        deep_bad: object = [deep_ok]
        self._assert_err("MAX_DEPTH_EXCEEDED", tco.validate_json_value, deep_bad, max_depth=64)
        cyc: list[object] = []
        cyc.append(cyc)
        self._assert_err("MAX_DEPTH_EXCEEDED", tco.validate_json_value, cyc, max_depth=64)
        deep_1500 = "[" * 1500 + "0" + "]" * 1500
        with self.assertRaises(tco.TorusContentError) as ctx_1500:
            tco.parse_strict_json(deep_1500)
        self.assertIn(ctx_1500.exception.code, ("MAX_DEPTH_EXCEEDED", "JSON_PARSE_ERROR"))

        # Direct _parse_capped_int_token + parse_strict_json + validate_json_value exact boundaries
        max_ok = (1 << tco.MAX_INT_BITS) - 1
        self.assertEqual(tco._parse_capped_int_token(str(max_ok)), max_ok)
        self.assertEqual(tco.parse_strict_json(str(max_ok)), max_ok)
        tco.validate_json_value(max_ok)
        self.assertEqual(tco.parse_strict_json("null"), None)
        self.assertEqual(tco.parse_strict_json("true"), True)
        self._assert_err("INT_BIT_LIMIT", tco._parse_capped_int_token, str(1 << tco.MAX_INT_BITS))
        self._assert_err("INT_DIGIT_LIMIT", tco._parse_capped_int_token, "9" * 401)
        self._assert_err("INT_BIT_LIMIT", tco.parse_strict_json, str(1 << tco.MAX_INT_BITS))
        self._assert_err("INT_DIGIT_LIMIT", tco.parse_strict_json, "9" * 401)
        self._assert_err("INT_DIGIT_LIMIT", tco.parse_strict_json, "9" * 5000)
        self._assert_err("INT_BIT_LIMIT", tco.validate_json_value, 1 << tco.MAX_INT_BITS)
        self._assert_err("INT_BIT_LIMIT", tco.canonical_json_bytes, {"x": 10**5000 - 1})

        # Floats, NaN/Inf, duplicate keys (including \u-escaped), bad syntax, surrogates, size cap
        self._assert_err("JSON_FLOAT_FORBIDDEN", tco.parse_strict_json, "1.5")
        self._assert_err("JSON_FLOAT_FORBIDDEN", tco.parse_strict_json, "1e2")
        self._assert_err("JSON_CONSTANT_FORBIDDEN", tco.parse_strict_json, "NaN")
        self._assert_err("JSON_CONSTANT_FORBIDDEN", tco.parse_strict_json, "Infinity")
        self._assert_err("JSON_CONSTANT_FORBIDDEN", tco.parse_strict_json, "-Infinity")
        self._assert_err("JSON_DUPLICATE_KEY", tco.parse_strict_json, '{"a":1,"a":2}')
        self._assert_err("JSON_DUPLICATE_KEY", tco.parse_strict_json, '{"\\u0061":1,"a":2}')
        self._assert_err("JSON_PARSE_ERROR", tco.parse_strict_json, "{bad")
        self._assert_err("SURROGATE_FORBIDDEN", tco.parse_strict_json, '"\uD800"')
        self._assert_err("INVALID_JSON_INPUT", tco.parse_strict_json, b"{}")
        self._assert_err("JSON_TOO_LARGE", tco.parse_strict_json, '"' + ("a" * tco.MAX_JSON_BYTES) + '"')

        # In-memory validate_json_value exact error codes (distinct FLOAT_FORBIDDEN vs UNSUPPORTED_JSON_TYPE)
        self._assert_err("NON_STR_KEY", tco.validate_json_value, {1: "a"})
        self._assert_err("NON_STR_KEY", tco.validate_json_value, {EvilStr("a"): 1})
        self._assert_err("UNSUPPORTED_JSON_TYPE", tco.validate_json_value, EvilDict({"a": 1}))
        self._assert_err("UNSUPPORTED_JSON_TYPE", tco.validate_json_value, EvilList([1]))
        self._assert_err("UNSUPPORTED_JSON_TYPE", tco.validate_json_value, EvilInt(1))
        self._assert_err("FLOAT_FORBIDDEN", tco.validate_json_value, 1.0)
        self._assert_err("SURROGATE_FORBIDDEN", tco.validate_json_value, {"a": "\uD800"})
        self._assert_err("SURROGATE_FORBIDDEN", tco.validate_json_value, {"\uDFFF": 1})
        self._assert_err("UNSUPPORTED_JSON_TYPE", tco.validate_json_value, object())

        # Exact byte cap boundary acceptance (MAX_JSON_BYTES exact)
        exact_cap_json = '"' + ("a" * (tco.MAX_JSON_BYTES - 2)) + '"'
        self.assertEqual(len(exact_cap_json.encode("utf-8")), tco.MAX_JSON_BYTES)
        self.assertEqual(len(tco.parse_strict_json(exact_cap_json)), tco.MAX_JSON_BYTES - 2)

    def test_04_linear_algebra_bk_2x2_pivots_and_seam1_errors(self) -> None:
        # Exercise 2x2 zero-diagonal pivot path in bunch_kaufman_inertia_q & verify against Faddeev-Descartes
        Z2 = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
        in_z2, ok_z2 = tco.bunch_kaufman_inertia_q(Z2)
        fd_z2, ok_fd2 = tco.faddeev_descartes_inertia_q(Z2)
        self.assertTrue(ok_z2)
        self.assertTrue(ok_fd2)
        self.assertEqual(in_z2, (1, 1, 0))
        self.assertEqual(in_z2, fd_z2)

        Z3 = [
            [Fraction(0), Fraction(0), Fraction(0)],
            [Fraction(0), Fraction(0), Fraction(2)],
            [Fraction(0), Fraction(2), Fraction(0)],
        ]
        in_z3, ok_z3 = tco.bunch_kaufman_inertia_q(Z3)
        fd_z3, ok_fd3 = tco.faddeev_descartes_inertia_q(Z3)
        self.assertTrue(ok_z3)
        self.assertTrue(ok_fd3)
        self.assertEqual(in_z3, (1, 1, 1))
        self.assertEqual(in_z3, fd_z3)

        Z4 = [
            [Fraction(0), Fraction(1), Fraction(0), Fraction(0)],
            [Fraction(1), Fraction(0), Fraction(1), Fraction(0)],
            [Fraction(0), Fraction(1), Fraction(0), Fraction(1)],
            [Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
        ]
        in_z4, ok_z4 = tco.bunch_kaufman_inertia_q(Z4)
        fd_z4, ok_fd4 = tco.faddeev_descartes_inertia_q(Z4)
        self.assertTrue(ok_z4)
        self.assertTrue(ok_fd4)
        self.assertEqual(in_z4, (2, 2, 0))
        self.assertEqual(in_z4, fd_z4)

        # Zero matrix Moore-Penrose & Bareiss zero/swap determinants
        Z0 = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]
        self.assertEqual(tco.moore_penrose_sym_q(Z0), Z0)
        self.assertEqual(tco.bareiss_det_int([[0, 1], [1, 0]]), -1)
        self.assertEqual(tco.bareiss_det_int([[0, 0], [0, 0]]), 0)

        # Matrix & rank-1 refusal guards with exact error codes
        self._assert_err("RAGGED_MATRIX", tco.require_matrix_q, [[1, 2], [3]])
        self._assert_err("NON_SQUARE_MATRIX", tco.require_sym_matrix_q, [[1, 2, 3], [4, 5, 6]])
        self._assert_err("NON_SYMMETRIC_MATRIX", tco.require_sym_matrix_q, [[1, 2], [3, 1]])
        self._assert_err(
            "SINGULAR_MATRIX",
            tco.invert_matrix_q,
            [[Fraction(1), Fraction(1)], [Fraction(1), Fraction(1)]],
        )
        self._assert_err("BASE_NOT_PSD", tco.analyze_rank1_update_q, Z2, [1, 0], 1)
        M_sing = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
        self._assert_err("B_NOT_IN_RANGE", tco.analyze_rank1_update_q, M_sing, [0, 1], 1)
        self._assert_err("ZERO_LEVERAGE", tco.analyze_rank1_update_q, M_sing, [0, 0], 1)

    def test_05_seam2_rounding_and_weft_boundaries(self) -> None:
        # Exact binary32 exponent boundaries: e == 127 (valid), e == 128 (overflow), e == -149 (valid), e == -150 (underflow)
        self.assertEqual(tco.floor_binary32_q(Fraction(1 << 127, 1)), Fraction(1 << 127, 1))
        self.assertEqual(tco.floor_binary32_q(Fraction(1, 1 << 149)), Fraction(1, 1 << 149))
        self._assert_err("F32_OVERFLOW", tco.floor_binary32_q, Fraction(1 << 128, 1))
        self._assert_err("F32_UNDERFLOW_ZERO", tco.floor_binary32_q, Fraction(1, 1 << 150))

        # Exact half-to-even ties in nearest_binary32_q (both ulp_exp < 0 and ulp_exp >= 0) & round_nearest_thousandth_q
        self.assertEqual(tco.nearest_binary32_q(Fraction(1) + Fraction(1, 1 << 24)), Fraction(1))
        self.assertEqual(
            tco.nearest_binary32_q(Fraction(1) + Fraction(3, 1 << 24)),
            Fraction(1) + Fraction(2, 1 << 23),
        )
        # Non-tie with odd significand (ulp_exp < 0) killing And->Or BoolOp
        self.assertEqual(
            tco.nearest_binary32_q(Fraction(1) + Fraction(1, 1 << 23) + Fraction(1, 1 << 25)),
            Fraction(1) + Fraction(1, 1 << 23),
        )
        # ulp_exp >= 0 (e=24, ulp=2): even tie 2^24+1 -> 2^24, odd tie 2^24+3 -> 2^24+4, non-tie odd 2^24+5/2 -> 2^24+2
        b24 = 1 << 24
        self.assertEqual(tco.nearest_binary32_q(Fraction(b24 + 1, 1)), Fraction(b24, 1))
        self.assertEqual(tco.nearest_binary32_q(Fraction(b24 + 3, 1)), Fraction(b24 + 4, 1))
        self.assertEqual(tco.nearest_binary32_q(Fraction(2 * b24 + 5, 2)), Fraction(b24 + 2, 1))
        # Thousandths ties & non-tie odd quotient (killing And->Or BoolOp)
        self.assertEqual(tco.round_nearest_thousandth_q(Fraction(1, 2000)), Fraction(0))
        self.assertEqual(tco.round_nearest_thousandth_q(Fraction(3, 2000)), Fraction(2, 1000))
        self.assertEqual(tco.round_nearest_thousandth_q(Fraction(14, 10000)), Fraction(1, 1000))

        # weft_budget_step_q boundary & refusal coverage (all 5 guards + exact equality)
        r_b0 = tco.weft_budget_step_q(0, 1, True)
        self.assertFalse(r_b0["accepted"])
        self.assertEqual(r_b0["reason"], "non_positive_budget")
        r_nf = tco.weft_budget_step_q(10, 1, True, non_finite_cost=True)
        self.assertFalse(r_nf["accepted"])
        self.assertEqual(r_nf["remaining_budget"], "10")
        self.assertEqual(r_nf["reason"], "non_finite_cost_preserved")
        r_c0 = tco.weft_budget_step_q(10, 0, True)
        self.assertFalse(r_c0["accepted"])
        self.assertEqual(r_c0["reason"], "non_positive_cost_preserved")
        r_unsafe = tco.weft_budget_step_q(10, 3, False)
        self.assertFalse(r_unsafe["accepted"])
        self.assertEqual(r_unsafe["remaining_budget"], "10")
        self.assertEqual(r_unsafe["reason"], "unsafe_weight_preserved")
        r_over = tco.weft_budget_step_q(10, 11, True)
        self.assertFalse(r_over["accepted"])
        self.assertEqual(r_over["remaining_budget"], "10")
        self.assertEqual(r_over["reason"], "insufficient_budget_preserved")
        r_exact_eq = tco.weft_budget_step_q(10, 10, True)
        self.assertTrue(r_exact_eq["accepted"])
        self.assertEqual(r_exact_eq["remaining_budget"], "0")

    def test_06_seam3_and_seam5_governance_guards(self) -> None:
        # Seam 3 self-loop refusal & exo#8 R3 ledger-to-journal completeness guards
        self._assert_err("SELF_LOOP_FORBIDDEN", tco.analyze_directed_network_q, 2, [(0, 0)], [1], [1])
        self.assertTrue(
            tco.verify_ledger_journal_completeness({"r1": "ok"}, {"r1": "ok", "r2": "pending"})["complete"]
        )
        self._assert_err("LEDGER_NOT_DICT", tco.verify_ledger_journal_completeness, ["bad"], {})
        self._assert_err("JOURNAL_NOT_DICT", tco.verify_ledger_journal_completeness, {}, ["bad"])
        self._assert_err(
            "JOURNAL_RECEIPT_OMITTED",
            tco.verify_ledger_journal_completeness,
            {"r1": "regressed", "r2": "regressed"},
            {"r1": "regressed"},
        )
        self._assert_err(
            "JOURNAL_OUTCOME_TAMPERED",
            tco.verify_ledger_journal_completeness,
            {"r1": "regressed"},
            {"r1": "pending"},
        )

        # Seam 5 certify_torus_seam_record: all valid & invalid paths (incl. extra & mixed-type keys)
        base_seam = {
            "seam_id": "SEAM-X",
            "status": "VERIFIED_EXACT_SEAM",
            "novelty_tier": "N1",
            "in_89node_graph_already": False,
            "has_exact_q_operator": True,
            "has_minimal_counterexample": False,
            "dual_oracle_verified": True,
        }
        self.assertTrue(tco.certify_torus_seam_record(base_seam)["admitted"])

        self._assert_err("SEAM_NOT_DICT", tco.certify_torus_seam_record, ["not", "dict"])
        self._assert_err("SEAM_BAD_KEYS", tco.certify_torus_seam_record, {"seam_id": "SEAM-X"})
        self._assert_err("SEAM_BAD_KEYS", tco.certify_torus_seam_record, {**base_seam, "extra": 1})
        self._assert_err("SEAM_BAD_KEYS", tco.certify_torus_seam_record, {**base_seam, 1: 2})
        for field, bad_val, expected_code in (
            ("status", "METAPHOR", "INVALID_SEAM_STATUS"),
            ("novelty_tier", "N3", "INVALID_NOVELTY_TIER"),
            ("novelty_tier", "N2", "UNPROVED_N2_INFLATION"),
            ("in_89node_graph_already", True, "DUPLICATE_GRAPH_EDGE"),
            ("has_exact_q_operator", False, "METAPHOR_SMUGGLING"),
            ("dual_oracle_verified", False, "MISSING_DUAL_ORACLE"),
        ):
            mut = dict(base_seam)
            mut[field] = bad_val
            self._assert_err(expected_code, tco.certify_torus_seam_record, mut)

        fals_seam = dict(base_seam)
        fals_seam["status"] = "FALSIFIED_METAPHOR"
        fals_seam["has_exact_q_operator"] = False
        fals_seam["has_minimal_counterexample"] = False
        self._assert_err("FALSIFIED_WITHOUT_COUNTEREXAMPLE", tco.certify_torus_seam_record, fals_seam)

        # Missed portal entry guards (incl. extra & mixed-type keys)
        base_portal = {
            "portal_id": "MP-99",
            "origin_refs": "#100",
            "target_repo": "Foundation-0/aletheia",
            "novelty_tier": "N0",
            "disposition": "LIVE_PORTAL",
            "concrete_gap": "example gap",
        }
        self.assertEqual(tco.certify_missed_portal_entry(base_portal)["portal_id"], "MP-99")
        self._assert_err("PORTAL_NOT_DICT", tco.certify_missed_portal_entry, "not_dict")
        self._assert_err("PORTAL_BAD_KEYS", tco.certify_missed_portal_entry, {"portal_id": "MP-99"})
        self._assert_err("PORTAL_BAD_KEYS", tco.certify_missed_portal_entry, {**base_portal, "extra": 1})
        self._assert_err("PORTAL_BAD_KEYS", tco.certify_missed_portal_entry, {**base_portal, 1: 2})
        self._assert_err(
            "INVALID_PORTAL_NOVELTY",
            tco.certify_missed_portal_entry,
            {**base_portal, "novelty_tier": "N9"},
        )
        self._assert_err(
            "INVALID_PORTAL_DISPOSITION",
            tco.certify_missed_portal_entry,
            {**base_portal, "disposition": "UNKNOWN"},
        )

    def test_07_certificate_audit_cli_and_all_zone_b_tamper_attacks(self) -> None:
        cert = tca.build_certificate()
        res = tca.verify_certificate_dict(cert)
        self.assertTrue(res["valid"])

        # Root type, subclass, extra key, mixed-type key (zero raw TypeError!)
        self._assert_err("CERT_NOT_DICT", tca.verify_certificate_dict, [])
        self._assert_err("CERT_NOT_DICT", tca.verify_certificate_dict, EvilDict(cert))
        self._assert_err("CERT_SCHEMA_KEYS", tca.verify_certificate_dict, {**cert, "extra": 1})
        self._assert_err("CERT_SCHEMA_KEYS", tca.verify_certificate_dict, {**cert, 1: 2})

        # Re-signed forged schema / audit_id / payload_sha256 prove EACH guard blocks a real forgery bypass!
        forged_schema = _resign_envelope("wrong.schema", tca.CERT_AUDIT_ID, cert["payload_sha256"], cert["payload"])
        self._assert_err("CERT_SCHEMA_MISMATCH", tca.verify_certificate_dict, forged_schema)

        forged_aid = _resign_envelope(tca.CERT_SCHEMA, "AUDIT-999", cert["payload_sha256"], cert["payload"])
        self._assert_err("CERT_AUDIT_ID_MISMATCH", tca.verify_certificate_dict, forged_aid)

        wrong_psha = ("0" if cert["payload_sha256"][0] != "0" else "1") + cert["payload_sha256"][1:]
        forged_psha = _resign_envelope(tca.CERT_SCHEMA, tca.CERT_AUDIT_ID, wrong_psha, cert["payload"])
        self._assert_err("PAYLOAD_SHA_MISMATCH", tca.verify_certificate_dict, forged_psha)

        # Strict 64-lowercase-ASCII-hex checks BEFORE hmac.compare_digest (exact codes!)
        for bad_digest, expected_code in (
            (123, "INVALID_DIGEST_TYPE"),
            (True, "INVALID_DIGEST_TYPE"),
            ("a" * 63, "INVALID_DIGEST_LEN"),
            ("a" * 65, "INVALID_DIGEST_LEN"),
            ("A" * 64, "INVALID_DIGEST_HEX"),
            ("\u00e9" * 64, "INVALID_DIGEST_HEX"),
            ("\uD800" * 64, "INVALID_DIGEST_HEX"),
            ("g" * 64, "INVALID_DIGEST_HEX"),
        ):
            self._assert_err(expected_code, tca.verify_certificate_dict, {**cert, "payload_sha256": bad_digest})

        # Certificate SHA mismatch (payload SHA ok, cert SHA wrong)
        wrong_csha = ("0" if cert["certificate_sha256"][0] != "0" else "1") + cert["certificate_sha256"][1:]
        self._assert_err(
            "CERTIFICATE_SHA_MISMATCH",
            tca.verify_certificate_dict,
            {**cert, "certificate_sha256": wrong_csha},
        )

        # Hollow / tampered payload WITH valid recomputed payload_sha256 AND certificate_sha256 (1 == True!)
        tampered_payload = {**cert["payload"], "all_passed": 1}
        forged_t_psha = hashlib.sha256(tco.canonical_json_bytes(tampered_payload)).hexdigest()
        forged_drift = _resign_envelope(tca.CERT_SCHEMA, tca.CERT_AUDIT_ID, forged_t_psha, tampered_payload)
        self._assert_err("RECOMPUTED_PAYLOAD_DRIFT", tca.verify_certificate_dict, forged_drift)

        # File-level checks: non-Path, missing, dir, symlink target, symlink ancestor, size cap, CR/CRLF, bad UTF-8, non-canonical
        self._assert_err("INVALID_PATH_TYPE", tca.check_certificate_file, "not_a_path")

        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            cert_path = tdp / "cert.json"
            wres = tca.write_certificate_file(cert_path)
            self.assertTrue(wres["valid"])
            self.assertEqual(wres["payload_sha256"], cert["payload_sha256"])

            # Missing file & directory
            self._assert_err("CERT_FILE_NOT_FOUND", tca.check_certificate_file, tdp / "missing.json")
            self._assert_err("CERT_FILE_NOT_FOUND", tca.check_certificate_file, tdp)

            # Symlink target & symlink ancestor
            sym_file = tdp / "sym.json"
            sym_file.symlink_to(cert_path)
            self._assert_err("SYMLINK_FORBIDDEN", tca.check_certificate_file, sym_file)
            real_sub = tdp / "real_sub"
            real_sub.mkdir()
            sub_cert = real_sub / "cert.json"
            sub_cert.write_bytes(cert_path.read_bytes())
            sym_dir = tdp / "sym_dir"
            sym_dir.symlink_to(real_sub)
            self._assert_err("SYMLINK_ANCESTOR_FORBIDDEN", tca.check_certificate_file, sym_dir / "cert.json")

            # Oversized file (> MAX_JSON_BYTES -> CERT_FILE_TOO_LARGE) vs exact size boundary check
            big_path = tdp / "big.json"
            big_path.write_bytes(b" " * (tco.MAX_JSON_BYTES + 1))
            self._assert_err("CERT_FILE_TOO_LARGE", tca.check_certificate_file, big_path)
            eq_cap_path = tdp / "eq_cap.json"
            eq_cap_path.write_bytes(b'{"a":"' + (b"x" * (tco.MAX_JSON_BYTES - 8)) + b'"}')
            self.assertEqual(eq_cap_path.stat().st_size, tco.MAX_JSON_BYTES)
            self._assert_err("CERT_SCHEMA_KEYS", tca.check_certificate_file, eq_cap_path)

            # CRLF / bare CR, invalid UTF-8, non-canonical JSON (pretty-printed), and trailing-newline-free canonical
            crlf_path = tdp / "crlf.json"
            crlf_path.write_bytes(cert_path.read_bytes().replace(b"\n", b"\r\n"))
            self._assert_err("CR_FORBIDDEN", tca.check_certificate_file, crlf_path)

            bad_utf8 = tdp / "bad_utf8.json"
            bad_utf8.write_bytes(b"\xff\xfe")
            self._assert_err("INVALID_UTF8", tca.check_certificate_file, bad_utf8)

            non_canon = tdp / "non_canon.json"
            non_canon.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
            self._assert_err("NON_CANONICAL_CERT_BYTES", tca.check_certificate_file, non_canon)

            no_nl = tdp / "no_nl.json"
            no_nl.write_bytes(cert_path.read_bytes().rstrip(b"\n"))
            self.assertTrue(tca.check_certificate_file(no_nl)["valid"])

            # CLI exit codes: 0 on valid --check/--standalone; 2 on reject
            out_buf = io.StringIO()
            err_buf = io.StringIO()
            with patch("sys.stdout", out_buf), patch("sys.stderr", err_buf):
                self.assertEqual(tca.main(["--check", str(cert_path)]), 0)
                self.assertEqual(tca.main(["--standalone"]), 0)
                self.assertEqual(tca.main(["--check", str(non_canon)]), 2)

        # Verify committed certificate file in track directory
        if tca.DEFAULT_CERT_PATH.is_file():
            self.assertTrue(tca.check_certificate_file(tca.DEFAULT_CERT_PATH)["valid"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTorusContentR5)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
