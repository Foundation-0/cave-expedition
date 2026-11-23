#!/usr/bin/env python3
"""R5 adversarial & mutation-killing test suite for aletheia_r6r7_r3_gate_audit.py.

Zero bare asserts (unittest TestCase assertions only). Exercises every fail-closed
guard, boundary condition, red-team bypass vector, live read-only portal anchor,
and standalone execution path.
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

import aletheia_r6r7_r3_gate_audit as mod


def _valid_r6_rules(**overrides):
    base = {
        "rule_id": "rule.test.v1",
        "expected_check_ids": ["c1", "c2"],
        "min_sq_norm": "0",
        "max_sq_norm": "20",
        "expected_header_alpha": "4",
        "max_vector_dim": 4,
    }
    base.update(overrides)
    return base


def _valid_bytes_and_sub(alpha: str = "4", vec: list[str] | None = None, **sub_overrides):
    vec_val = ["3", "2", "1"] if vec is None else vec
    raw = mod._canonical_payload_bytes(alpha, vec_val)
    sq = sum((mod._parse_exact_rational(x) ** 2 for x in vec_val), Fraction(0, 1))
    sub = {
        "declared_sha256": hashlib.sha256(raw).hexdigest(),
        "declared_sq_norm": mod._fmt_q(sq),
        "declared_header_alpha": alpha,
        "declared_status": "PASS",
        "submitter_rule_overrides": {},
    }
    sub.update(sub_overrides)
    return raw, sub


def _assert_no_floats(tc: unittest.TestCase, obj: object) -> None:
    if isinstance(obj, float):
        tc.fail(f"Forbidden float encountered: {obj!r}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _assert_no_floats(tc, k)
            _assert_no_floats(tc, v)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _assert_no_floats(tc, item)


class TestRationalAndStrictJson(unittest.TestCase):
    def test_rational_valid_and_boundaries(self) -> None:
        self.assertEqual(mod._parse_exact_rational(Fraction(3, 4)), Fraction(3, 4))
        self.assertEqual(mod._parse_exact_rational(0), Fraction(0, 1))
        self.assertEqual(mod._parse_exact_rational(-5), Fraction(-5, 1))
        self.assertEqual(mod._parse_exact_rational("5/1"), Fraction(5, 1))
        self.assertEqual(mod._parse_exact_rational("-7/3"), Fraction(-7, 3))
        self.assertEqual(mod._parse_exact_rational("0/1"), Fraction(0, 1))
        self.assertEqual(mod._fmt_q(Fraction(4, 1)), "4")
        self.assertEqual(mod._fmt_q(Fraction(3, 5)), "3/5")

    def test_rational_rejections(self) -> None:
        bad_cases = [
            (True, "RATIONAL_TYPE_OR_SYNTAX"),
            (False, "RATIONAL_TYPE_OR_SYNTAX"),
            (1.5, "RATIONAL_TYPE_OR_SYNTAX"),
            ("", "RATIONAL_TYPE_OR_SYNTAX"),
            (" 1/2", "RATIONAL_TYPE_OR_SYNTAX"),
            ("1/2\n", "RATIONAL_TYPE_OR_SYNTAX"),
            ("1/2\u200b", "RATIONAL_TYPE_OR_SYNTAX"),
            ("1/2/3", "RATIONAL_TOO_MANY_SLASHES"),
            ("-", "RATIONAL_INVALID_NUMERATOR"),
            ("abc", "RATIONAL_INVALID_NUMERATOR"),
            ("1.5", "RATIONAL_INVALID_NUMERATOR"),
            ("1/", "RATIONAL_INVALID_DENOMINATOR"),
            ("1/-2", "RATIONAL_INVALID_DENOMINATOR"),
            ("1/abc", "RATIONAL_INVALID_DENOMINATOR"),
            ("1/0", "RATIONAL_NONPOSITIVE_DENOMINATOR"),
        ]
        for val, code in bad_cases:
            with self.assertRaisesRegex(ValueError, code):
                mod._parse_exact_rational(val)

    def test_strict_json_bytes_rejections(self) -> None:
        with self.assertRaisesRegex(ValueError, "PAYLOAD_INVALID_UTF8"):
            mod._parse_strict_json_bytes(b"\xff\xfe")
        with self.assertRaisesRegex(ValueError, "PAYLOAD_INVALID_JSON"):
            mod._parse_strict_json_bytes(b"{not json")
        with self.assertRaisesRegex(ValueError, "JSON_FLOAT_FORBIDDEN"):
            mod._parse_strict_json_bytes(b'{"a": 1.5}')
        with self.assertRaisesRegex(ValueError, "JSON_CONSTANT_FORBIDDEN"):
            mod._parse_strict_json_bytes(b'{"a": NaN}')
        with self.assertRaisesRegex(ValueError, "JSON_DUPLICATE_KEY"):
            mod._parse_strict_json_bytes(b'{"a": 1, "a": 2}')
        with self.assertRaisesRegex(ValueError, "PAYLOAD_ROOT_NOT_OBJECT"):
            mod._parse_strict_json_bytes(b"[1, 2]")


class TestR6R7Gate(unittest.TestCase):
    def test_exact_boundary_accepts(self) -> None:
        # Exact min boundary (0), exact max boundary (20), exact max_vector_dim (4), status CANDIDATE
        raw0, sub0 = _valid_bytes_and_sub(alpha="4", vec=["0"], declared_status="CANDIDATE")
        res0 = mod.evaluate_r6_r7_gate(_valid_r6_rules(min_sq_norm="0", max_sq_norm="0", max_vector_dim=1), sub0, raw0)
        self.assertEqual(res0["status"], "ACCEPTED")
        self.assertEqual(res0["measured_sq_norm"], "0")

        # Exact max_sq_norm = 20 and exact max_vector_dim = 4: 4^2 + 2^2 + 0^2 + 0^2 = 20
        raw20, sub20 = _valid_bytes_and_sub(alpha="4", vec=["4", "2", "0", "0"])
        res20 = mod.evaluate_r6_r7_gate(_valid_r6_rules(min_sq_norm="20", max_sq_norm="20", max_vector_dim=4), sub20, raw20)
        self.assertEqual(res20["measured_sq_norm"], "20")
        self.assertEqual(res20["vector_dim"], 4)

    def test_pinned_rules_guards(self) -> None:
        raw, sub = _valid_bytes_and_sub()
        with self.assertRaisesRegex(ValueError, "R6_PINNED_RULES_SCHEMA_MISMATCH"):
            mod.evaluate_r6_r7_gate([], sub, raw)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "R6_PINNED_RULES_SCHEMA_MISMATCH"):
            mod.evaluate_r6_r7_gate({**_valid_r6_rules(), "extra": 1}, sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_INVALID_RULE_ID"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(rule_id="bad\n"), sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_EMPTY_CHECK_IDS"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(expected_check_ids=[]), sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_EMPTY_CHECK_IDS"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(expected_check_ids="c1"), sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_INVALID_CHECK_ID"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(expected_check_ids=["c1", " "]), sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_DUPLICATE_CHECK_ID"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(expected_check_ids=["c1", "c1"]), sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_DUPLICATE_CHECK_ID"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(expected_check_ids=["c1", "C1"]), sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_NEGATIVE_MIN_SQ_NORM"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(min_sq_norm="-1/100"), sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_INVERTED_SQ_NORM_RANGE"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(min_sq_norm="10", max_sq_norm="9"), sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_NONPOSITIVE_EXPECTED_ALPHA"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(expected_header_alpha="0"), sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_INVALID_MAX_VECTOR_DIM"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(max_vector_dim=0), sub, raw)
        with self.assertRaisesRegex(ValueError, "R6_INVALID_MAX_VECTOR_DIM"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(max_vector_dim=True), sub, raw)

    def test_submission_and_artifact_guards(self) -> None:
        rules = _valid_r6_rules()
        raw, sub = _valid_bytes_and_sub()

        with self.assertRaisesRegex(ValueError, "R6_SUBMISSION_SCHEMA_MISMATCH"):
            mod.evaluate_r6_r7_gate(rules, [], raw)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "R6_SUBMISSION_SCHEMA_MISMATCH"):
            mod.evaluate_r6_r7_gate(rules, {**sub, "injected": 1}, raw)
        with self.assertRaisesRegex(ValueError, "R6_OVERRIDES_NOT_OBJECT"):
            mod.evaluate_r6_r7_gate(rules, {**sub, "submitter_rule_overrides": []}, raw)
        with self.assertRaisesRegex(ValueError, "R6_SUBMITTER_RULE_OVERRIDE"):
            mod.evaluate_r6_r7_gate(rules, {**sub, "submitter_rule_overrides": {"max_sq_norm": "999"}}, raw)
        with self.assertRaisesRegex(ValueError, "R6_INVALID_DECLARED_STATUS"):
            mod.evaluate_r6_r7_gate(rules, {**sub, "declared_status": "PASS\n"}, raw)
        with self.assertRaisesRegex(ValueError, "R6_INVALID_DECLARED_STATUS"):
            mod.evaluate_r6_r7_gate(rules, {**sub, "declared_status": 1}, raw)
        with self.assertRaisesRegex(ValueError, "R7_ARTIFACT_NOT_BYTES"):
            mod.evaluate_r6_r7_gate(rules, sub, "not-bytes")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "R7_NULL_ARTIFACT_BYTES"):
            mod.evaluate_r6_r7_gate(rules, sub, b"")
        with self.assertRaisesRegex(ValueError, "R7_INVALID_DECLARED_SHA256"):
            mod.evaluate_r6_r7_gate(rules, {**sub, "declared_sha256": sub["declared_sha256"] + "\n"}, raw)
        with self.assertRaisesRegex(ValueError, "R7_DECLARED_SHA256_MISMATCH"):
            mod.evaluate_r6_r7_gate(rules, {**sub, "declared_sha256": "0" * 64}, raw)

        # Payload schema & vector bounds
        bad_payload = b'{"header_alpha":"4","vector_entries":["1"],"extra":1}\n'
        sub_bp = {**sub, "declared_sha256": hashlib.sha256(bad_payload).hexdigest()}
        with self.assertRaisesRegex(ValueError, "R7_PAYLOAD_SCHEMA_MISMATCH"):
            mod.evaluate_r6_r7_gate(rules, sub_bp, bad_payload)

        empty_vec = mod._canonical_payload_bytes("4", [])
        sub_ev = {**sub, "declared_sha256": hashlib.sha256(empty_vec).hexdigest()}
        with self.assertRaisesRegex(ValueError, "R7_EMPTY_VECTOR_ENTRIES"):
            mod.evaluate_r6_r7_gate(rules, sub_ev, empty_vec)

        nonlist_vec = b'{"header_alpha":"4","vector_entries":"1"}\n'
        sub_nlv = {**sub, "declared_sha256": hashlib.sha256(nonlist_vec).hexdigest()}
        with self.assertRaisesRegex(ValueError, "R7_EMPTY_VECTOR_ENTRIES"):
            mod.evaluate_r6_r7_gate(rules, sub_nlv, nonlist_vec)

        big_vec, sub_bv = _valid_bytes_and_sub(vec=["1", "1", "1", "1", "1"])
        with self.assertRaisesRegex(ValueError, "R6_VECTOR_DIM_EXCEEDS_MAX"):
            mod.evaluate_r6_r7_gate(rules, sub_bv, big_vec)

        # Declared vs measured mismatches & pinned bounds
        with self.assertRaisesRegex(ValueError, "R7_DECLARED_NORM_MISMATCH"):
            mod.evaluate_r6_r7_gate(rules, {**sub, "declared_sq_norm": "13"}, raw)
        with self.assertRaisesRegex(ValueError, "R7_DECLARED_ALPHA_MISMATCH"):
            mod.evaluate_r6_r7_gate(rules, {**sub, "declared_header_alpha": "5"}, raw)

        raw_a8, sub_a8 = _valid_bytes_and_sub(alpha="8", vec=["1"])
        with self.assertRaisesRegex(ValueError, "R6_HEADER_ALPHA_OUT_OF_SPEC"):
            mod.evaluate_r6_r7_gate(rules, sub_a8, raw_a8)

        raw_low, sub_low = _valid_bytes_and_sub(vec=["1"])
        with self.assertRaisesRegex(ValueError, "R6_MEASURED_NORM_BELOW_MIN"):
            mod.evaluate_r6_r7_gate(_valid_r6_rules(min_sq_norm="2"), sub_low, raw_low)

        raw_hi, sub_hi = _valid_bytes_and_sub(vec=["5"])
        with self.assertRaisesRegex(ValueError, "R6_MEASURED_NORM_ABOVE_MAX"):
            mod.evaluate_r6_r7_gate(rules, sub_hi, raw_hi)

    def test_record_b_witnesses(self) -> None:
        res = mod.run_record_b_witnesses()
        self.assertTrue(res["all_caught"])
        self.assertEqual(len(res["negative_witnesses_caught"]), 6)
        self.assertEqual(res["record_b_exact_scaled_sq_norm"], "3734/5")

        # Kill M050 (guard_if_reject on got_code != expected_code inside run_record_b_witnesses)
        orig_eval = mod.evaluate_r6_r7_gate

        def wrong_code_on_empty(rules, sub, raw):
            if raw == b"":
                raise ValueError("UNEXPECTED_OTHER_CODE")
            return orig_eval(rules, sub, raw)

        with mock.patch.object(mod, "evaluate_r6_r7_gate", side_effect=wrong_code_on_empty):
            with self.assertRaisesRegex(ValueError, "WITNESS_MISMATCH:B2_null_adapter_empty_bytes"):
                mod.run_record_b_witnesses()


class TestTwoDirectionR3(unittest.TestCase):
    def test_hardened_and_vulnerable_note_d_gates(self) -> None:
        sha = "b" * 64
        ok = {"require_multi_oracle": True, "oracle_verdict": "VERIFIED", "artifact_sha256": sha, "score_int": 1}
        self.assertTrue(mod.hardened_r3_multi_oracle_gate(ok))
        self.assertFalse(mod.hardened_r3_multi_oracle_gate([]))
        self.assertFalse(mod.hardened_r3_multi_oracle_gate({**ok, "extra": 1}))
        self.assertFalse(mod.hardened_r3_multi_oracle_gate({**ok, "require_multi_oracle": False}))
        self.assertFalse(mod.hardened_r3_multi_oracle_gate({**ok, "require_multi_oracle": 1}))
        self.assertFalse(mod.hardened_r3_multi_oracle_gate({**ok, "oracle_verdict": 1}))
        self.assertFalse(mod.hardened_r3_multi_oracle_gate({**ok, "oracle_verdict": "VERIFIED\n"}))
        self.assertFalse(mod.hardened_r3_multi_oracle_gate({**ok, "artifact_sha256": sha + "\n"}))
        self.assertFalse(mod.hardened_r3_multi_oracle_gate({**ok, "score_int": 0}))
        self.assertFalse(mod.hardened_r3_multi_oracle_gate({**ok, "score_int": True}))

        # Vulnerable Note D gate branches
        self.assertFalse(mod.vulnerable_note_d_gate("not-dict"))
        self.assertFalse(mod.vulnerable_note_d_gate({**ok, "require_multi_oracle": False}))
        self.assertFalse(mod.vulnerable_note_d_gate({**ok, "oracle_verdict": "FAILED"}))
        self.assertTrue(mod.vulnerable_note_d_gate({**ok, "require_multi_oracle": 1, "oracle_verdict": "FAILED"}))
        self.assertFalse(mod.vulnerable_note_d_gate({**ok, "artifact_sha256": "bad"}))
        self.assertFalse(mod.vulnerable_note_d_gate({**ok, "score_int": 0}))
        self.assertFalse(mod.vulnerable_note_d_gate({**ok, "score_int": True}))

    def test_certify_two_direction_r3_guards_and_note_d_witness(self) -> None:
        sha = "c" * 64
        ok = {"require_multi_oracle": True, "oracle_verdict": "VERIFIED", "artifact_sha256": sha, "score_int": 1}
        bad = {**ok, "oracle_verdict": "FAILED"}
        bad_resp = {**bad, "require_multi_oracle": 1}
        ok_resp = {**ok, "require_multi_oracle": 1}

        # Direct unit checks on _strict_typed_equal (covering int vs bool, dict keys, lists/tuples)
        self.assertTrue(mod._strict_typed_equal({"a": [1, (True, "x")]}, {"a": [1, (True, "x")]}))
        self.assertFalse(mod._strict_typed_equal(1, True))
        self.assertFalse(mod._strict_typed_equal({"a": 1}, {"a": 1, "b": 2}))
        self.assertFalse(mod._strict_typed_equal({"a": 1}, {"b": 1}))
        self.assertFalse(mod._strict_typed_equal([1, 2], [1]))
        self.assertFalse(mod._strict_typed_equal([1], [True]))

        with self.assertRaisesRegex(ValueError, "R3_EMPTY_DIR1_CASES"):
            mod.certify_two_direction_r3(mod.hardened_r3_multi_oracle_gate, ok, bad, [], [("d2", bad_resp)])
        with self.assertRaisesRegex(ValueError, "R3_EMPTY_DIR2_CASES"):
            mod.certify_two_direction_r3(mod.hardened_r3_multi_oracle_gate, ok, bad, [("d1", ok_resp)], [])
        with self.assertRaisesRegex(ValueError, "R3_BASELINE_ACCEPT_FAILED"):
            mod.certify_two_direction_r3(mod.hardened_r3_multi_oracle_gate, bad, bad, [("d1", ok_resp)], [("d2", bad_resp)])
        with self.assertRaisesRegex(ValueError, "R3_BASELINE_REJECT_FAILED"):
            mod.certify_two_direction_r3(mod.hardened_r3_multi_oracle_gate, ok, ok, [("d1", ok_resp)], [("d2", bad_resp)])
        with self.assertRaisesRegex(ValueError, "R3_INVALID_DIR1_LABEL"):
            mod.certify_two_direction_r3(mod.hardened_r3_multi_oracle_gate, ok, bad, [(" ", ok_resp)], [("d2", bad_resp)])
        with self.assertRaisesRegex(ValueError, "R3_INVALID_DIR2_LABEL"):
            mod.certify_two_direction_r3(mod.hardened_r3_multi_oracle_gate, ok, bad, [("d1", ok_resp)], [("", bad_resp)])

        # Duplicate labels (within dir1, within dir2, and across dir1/dir2)
        with self.assertRaisesRegex(ValueError, "R3_DUPLICATE_LABEL"):
            mod.certify_two_direction_r3(
                mod.hardened_r3_multi_oracle_gate,
                ok,
                bad,
                [("dup", ok_resp), ("DUP", {**ok, "score_int": "1"})],
                [("d2", bad_resp)],
            )
        with self.assertRaisesRegex(ValueError, "R3_DUPLICATE_LABEL"):
            mod.certify_two_direction_r3(
                mod.hardened_r3_multi_oracle_gate,
                ok,
                bad,
                [("d1", ok_resp)],
                [("dup2", bad_resp), ("DUP2", {**bad, "require_multi_oracle": 0})],
            )
        with self.assertRaisesRegex(ValueError, "R3_DUPLICATE_LABEL"):
            mod.certify_two_direction_r3(
                mod.hardened_r3_multi_oracle_gate,
                ok,
                bad,
                [("shared", ok_resp)],
                [("SHARED", bad_resp)],
            )

        # Noop unmutated copy rejections in Dir (i) and Dir (ii)
        with self.assertRaisesRegex(ValueError, "R3_NOOP_DIR1_CASE"):
            mod.certify_two_direction_r3(
                mod.hardened_r3_multi_oracle_gate, ok, bad, [("noop1", dict(ok))], [("d2", bad_resp)]
            )
        with self.assertRaisesRegex(ValueError, "R3_NOOP_DIR2_CASE"):
            mod.certify_two_direction_r3(
                mod.hardened_r3_multi_oracle_gate, ok, bad, [("d1", ok_resp)], [("noop2", dict(bad))]
            )

        # Real non-noop Dir (i) failure detection (score_int=2 accepted by gate)
        dir1_fail = mod.certify_two_direction_r3(
            mod.hardened_r3_multi_oracle_gate,
            ok,
            bad,
            [("mutated_accept_score_2", {**ok, "score_int": 2})],
            [("still_reject_int_1", bad_resp)],
        )
        self.assertFalse(dir1_fail["passed"])
        self.assertEqual(dir1_fail["dir1_failures"], ["mutated_accept_score_2"])

        witness = mod.run_r3_note_d_witness()
        self.assertTrue(witness["hardened_gate"]["passed"])
        self.assertFalse(witness["vulnerable_note_d_gate"]["passed"])
        self.assertTrue(witness["note_d_dir2_flip_exposed"])


class TestSampledOracleAndGate8Latch(unittest.TestCase):
    def test_sampled_integrity_boundaries_and_guards(self) -> None:
        self.assertEqual(mod.evaluate_sampled_integrity(0, 1, 0)["verdict"], "NOT_SHOWN")
        self.assertEqual(mod.evaluate_sampled_integrity(1, 4, 0)["verdict"], "NOT_SHOWN")
        self.assertEqual(mod.evaluate_sampled_integrity(4, 4, 0)["verdict"], "PASS")
        self.assertEqual(mod.evaluate_sampled_integrity(4, 4, 4)["verdict"], "FAIL")

        with self.assertRaisesRegex(ValueError, "SAMPLED_INVALID_TOTAL"):
            mod.evaluate_sampled_integrity(0, 0, 0)
        with self.assertRaisesRegex(ValueError, "SAMPLED_INVALID_TOTAL"):
            mod.evaluate_sampled_integrity(0, True, 0)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "SAMPLED_INVALID_TESTED"):
            mod.evaluate_sampled_integrity(-1, 2, 0)
        with self.assertRaisesRegex(ValueError, "SAMPLED_INVALID_TESTED"):
            mod.evaluate_sampled_integrity(3, 2, 0)
        with self.assertRaisesRegex(ValueError, "SAMPLED_INVALID_TESTED"):
            mod.evaluate_sampled_integrity(False, 2, 0)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "SAMPLED_INVALID_HITS"):
            mod.evaluate_sampled_integrity(2, 2, -1)
        with self.assertRaisesRegex(ValueError, "SAMPLED_INVALID_HITS"):
            mod.evaluate_sampled_integrity(2, 2, 3)
        with self.assertRaisesRegex(ValueError, "SAMPLED_INVALID_HITS"):
            mod.evaluate_sampled_integrity(2, 2, True)  # type: ignore[arg-type]

    def test_oracle_contract_guards(self) -> None:
        with self.assertRaisesRegex(ValueError, "ORACLE_CONTRACT_SCHEMA_MISMATCH"):
            mod.certify_oracle_contract({})
        with self.assertRaisesRegex(ValueError, "ORACLE_CONTRACT_SCHEMA_MISMATCH"):
            mod.certify_oracle_contract([])  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "ORACLE_UNKNOWN_CLASS"):
            mod.certify_oracle_contract({"oracle_class": "heuristic", "evidence_basis": "x", "feedback_channel": "y"})
        with self.assertRaisesRegex(ValueError, "ORACLE_UNKNOWN_CLASS"):
            mod.certify_oracle_contract({"oracle_class": 1, "evidence_basis": "x", "feedback_channel": "y"})
        with self.assertRaisesRegex(ValueError, "ORACLE_INVALID_BASIS"):
            mod.certify_oracle_contract({"oracle_class": "exact", "evidence_basis": "", "feedback_channel": "y"})
        with self.assertRaisesRegex(ValueError, "ORACLE_INVALID_FEEDBACK"):
            mod.certify_oracle_contract({"oracle_class": "exact", "evidence_basis": "formal_proof", "feedback_channel": " "})
        with self.assertRaisesRegex(ValueError, "ORACLE_EXACT_REQUIRES_NON_SAMPLED_BASIS"):
            mod.certify_oracle_contract(
                {
                    "oracle_class": "exact",
                    "evidence_basis": "random_finite_sample_exact_arithmetic",
                    "feedback_channel": "full_counterexample_and_repair",
                }
            )
        with self.assertRaisesRegex(ValueError, "ORACLE_SAMPLED_INVALID_BASIS"):
            mod.certify_oracle_contract(
                {
                    "oracle_class": "sampled",
                    "evidence_basis": "formal_proof",
                    "feedback_channel": "family_only_with_fresh_post_repair_seed",
                }
            )
        with self.assertRaisesRegex(ValueError, "ORACLE_ANCHOR_REQUIRES_EXTERNAL_DATA"):
            mod.certify_oracle_contract(
                {
                    "oracle_class": "anchor",
                    "evidence_basis": "untouched_upstream_replay",
                    "feedback_channel": "none_to_proposer_spec_owner_only",
                }
            )
        with self.assertRaisesRegex(ValueError, "ORACLE_REPLAY_REQUIRES_UPSTREAM"):
            mod.certify_oracle_contract(
                {
                    "oracle_class": "reference_replay",
                    "evidence_basis": "external_domain_data",
                    "feedback_channel": "diff_against_upstream_reference",
                }
            )
        with self.assertRaisesRegex(ValueError, "ORACLE_FEEDBACK_CHANNEL_MISMATCH"):
            mod.certify_oracle_contract(
                {
                    "oracle_class": "anchor",
                    "evidence_basis": "external_domain_data",
                    "feedback_channel": "full_counterexample_and_repair",
                }
            )

    def test_gate8_subspace_latch_exact_and_guards(self) -> None:
        # Zero-rank Phi column -> sin^2(theta) = 1, surviving = m
        res_zero = mod.certify_gate8_subspace_latch([["0", "0"]], ["3", "4"], "0", "1")
        self.assertEqual(res_zero["phi_rank"], 0)
        self.assertEqual(res_zero["sin2_theta_attenuation"], "1")
        self.assertEqual(res_zero["decision"], "WITHIN_POSTFIT_BUDGET")

        # Pivot swap needed in both _exact_pivot_columns_q and _solve_linear_q
        phi_swap = [["0", "1", "0"], ["1", "0", "0"], ["0", "0", "0"]]
        res_swap = mod.certify_gate8_subspace_latch(phi_swap, ["1", "2", "2"], "3", "3")
        self.assertEqual(res_swap["phi_rank"], 2)
        self.assertEqual(res_swap["surviving_independent_audits"], 1)
        self.assertEqual(res_swap["sin2_theta_attenuation"], "4/9")
        self.assertEqual(res_swap["orthogonality_residual"], "0")
        self.assertEqual(res_swap["pythagorean_residual"], "0")
        self.assertEqual(res_swap["decision"], "WITHIN_POSTFIT_BUDGET")

        # Singular Gram guard directly
        with self.assertRaisesRegex(ValueError, "LATCH_SINGULAR_GRAM"):
            mod._solve_linear_q([[Fraction(1), Fraction(1)], [Fraction(1), Fraction(1)]], [Fraction(1), Fraction(1)])

        # Row-swap inside _solve_linear_q directly
        sol = mod._solve_linear_q([[Fraction(0), Fraction(2)], [Fraction(3), Fraction(1)]], [Fraction(4), Fraction(5)])
        self.assertEqual(sol, [Fraction(1), Fraction(2)])

        # Input guards
        with self.assertRaisesRegex(ValueError, "LATCH_EMPTY_PHI"):
            mod.certify_gate8_subspace_latch([], ["1"], "0", "1")
        with self.assertRaisesRegex(ValueError, "LATCH_EMPTY_PHI"):
            mod.certify_gate8_subspace_latch("bad", ["1"], "0", "1")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "LATCH_EMPTY_PHI_COLUMN"):
            mod.certify_gate8_subspace_latch([[]], ["1"], "0", "1")
        with self.assertRaisesRegex(ValueError, "LATCH_EMPTY_PHI_COLUMN"):
            mod.certify_gate8_subspace_latch(["bad"], ["1"], "0", "1")  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "LATCH_RAGGED_PHI"):
            mod.certify_gate8_subspace_latch([["1", "0"], ["1"]], ["1", "0"], "0", "1")
        with self.assertRaisesRegex(ValueError, "LATCH_RAGGED_PHI"):
            mod.certify_gate8_subspace_latch([["1", "0"], "bad"], ["1", "0"], "0", "1")  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "LATCH_AUDIT_VECTOR_DIM_MISMATCH"):
            mod.certify_gate8_subspace_latch([["1", "0"]], ["1"], "0", "1")
        with self.assertRaisesRegex(ValueError, "LATCH_AUDIT_VECTOR_DIM_MISMATCH"):
            mod.certify_gate8_subspace_latch([["1", "0"]], "10", "0", "1")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "LATCH_ZERO_AUDIT_VECTOR"):
            mod.certify_gate8_subspace_latch([["1", "0"]], ["0", "0"], "0", "1")
        with self.assertRaisesRegex(ValueError, "LATCH_NEGATIVE_RESIDUAL"):
            mod.certify_gate8_subspace_latch([["1", "0"]], ["0", "1"], "-1/10", "1")
        with self.assertRaisesRegex(ValueError, "LATCH_NONPOSITIVE_NOISE_VAR"):
            mod.certify_gate8_subspace_latch([["1", "0"]], ["0", "1"], "0", "0")

        suite = mod.run_oracle_and_latch_suite()
        self.assertEqual(suite["sampled_integrity"]["partial_1_of_4_zero_hits"]["verdict"], "NOT_SHOWN")
        self.assertEqual(
            suite["oracle_contracts"]["exact_arithmetic_random_sample_rejected_code"],
            "ORACLE_EXACT_REQUIRES_NON_SAMPLED_BASIS",
        )
        self.assertEqual(suite["gate8_subspace_latch"]["oblique_sin2_4_over_5_halt"]["sin2_theta_attenuation"], "4/5")
        self.assertEqual(suite["gate8_subspace_latch"]["oblique_sin2_4_over_5_halt"]["decision"], "LATCH_HALT")
        self.assertEqual(suite["gate8_subspace_latch"]["in_col_phi_sin2_zero_blind"]["decision"], "BLIND_AUDIT_IN_COL_PHI")
        self.assertTrue(suite["gate8_subspace_latch"]["in_col_phi_sin2_zero_blind"]["halt"])
        self.assertEqual(suite["gate8_subspace_latch"]["saturated_rank_equals_m_halt"]["decision"], "SATURATED_NO_SURVIVING_AUDITS")


class TestGitRefPortalAndCli(unittest.TestCase):
    def test_git_ref_resolution_and_security_guards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            with self.assertRaisesRegex(ValueError, "GIT_DIR_MISSING"):
                mod._resolve_git_ref_sha40(root, "refs/heads/main")

            git_dir = root / ".git"
            (git_dir / "refs" / "heads").mkdir(parents=True)
            sha1 = "1" * 40
            sha2 = "2" * 40
            (git_dir / "refs" / "heads" / "main").write_text(sha1 + "\n", encoding="utf-8")
            (git_dir / "refs" / "heads" / "bad").write_text("not_a_sha\n", encoding="utf-8")
            outside = Path(tmp) / "outside_secret"
            outside.write_text(sha1 + "\n", encoding="utf-8")
            (git_dir / "refs" / "heads" / "escape").symlink_to(outside)
            (git_dir / "packed-refs").write_text(
                "# pack-refs with: peeled\n"
                f"{sha2} refs/remotes/origin/packed\n"
                f"^{sha1}\n"
                "badsha refs/remotes/origin/badpacked\n",
                encoding="utf-8",
            )

            self.assertEqual(mod._resolve_git_ref_sha40(root, "refs/heads/main"), sha1)
            self.assertEqual(mod._resolve_git_ref_sha40(root, "refs/remotes/origin/packed"), sha2)

            with self.assertRaisesRegex(ValueError, "GIT_REF_INVALID_PREFIX"):
                mod._resolve_git_ref_sha40(root, "HEAD")
            with self.assertRaisesRegex(ValueError, "GIT_REF_INVALID_PREFIX"):
                mod._resolve_git_ref_sha40(root, "refs/heads/main\n")
            with self.assertRaisesRegex(ValueError, "GIT_REF_PATH_TRAVERSAL"):
                mod._resolve_git_ref_sha40(root, "refs/heads/../ORIG_HEAD")
            with self.assertRaisesRegex(ValueError, "GIT_REF_PATH_TRAVERSAL"):
                mod._resolve_git_ref_sha40(root, "refs/heads\\main")
            with self.assertRaisesRegex(ValueError, "GIT_REF_PATH_TRAVERSAL"):
                mod._resolve_git_ref_sha40(root, "refs//heads/main")
            with self.assertRaisesRegex(ValueError, "GIT_REF_SYMLINK_ESCAPE"):
                mod._resolve_git_ref_sha40(root, "refs/heads/escape")
            with self.assertRaisesRegex(ValueError, "GIT_LOOSE_REF_INVALID_SHA"):
                mod._resolve_git_ref_sha40(root, "refs/heads/bad")
            with self.assertRaisesRegex(ValueError, "GIT_PACKED_REF_INVALID_SHA"):
                mod._resolve_git_ref_sha40(root, "refs/remotes/origin/badpacked")
            with self.assertRaisesRegex(ValueError, "GIT_REF_NOT_FOUND"):
                mod._resolve_git_ref_sha40(root, "refs/heads/nonexistent")
            with self.assertRaisesRegex(ValueError, "GIT_REF_NOT_FOUND"):
                mod._resolve_git_ref_sha40(root, "refs/heads")

            # packed-refs symlink escape guard
            (git_dir / "packed-refs").unlink()
            (git_dir / "packed-refs").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "GIT_PACKED_REFS_SYMLINK_ESCAPE"):
                mod._resolve_git_ref_sha40(root, "refs/remotes/origin/packed")

    def test_portal_inspection_mismatch_guards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repos" / "aletheia-live" / ".git"
            repo.mkdir(parents=True)
            lines = [f"{sha} {ref}" for ref, sha in mod.PINNED_ALETHEIA_LIVE_REFS.items()]
            (repo / "packed-refs").write_text("\n".join(lines) + "\n", encoding="utf-8")

            # Wrong ref SHA
            bad_lines = [f"{'0' * 40} refs/heads/main"] + lines[1:]
            (repo / "packed-refs").write_text("\n".join(bad_lines) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ALETHEIA_LIVE_REF_MISMATCH"):
                mod.inspect_round10_aletheia_portals(root)

            # Fix refs, missing portal file
            (repo / "packed-refs").write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "PORTAL_FILE_MISSING"):
                mod.inspect_round10_aletheia_portals(root)

            # Wrong portal SHA
            portals = root / "portals" / "aletheia"
            for rel in mod.PINNED_PORTAL_SHA256:
                p = portals / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "PORTAL_SHA256_MISMATCH"):
                mod.inspect_round10_aletheia_portals(root)

            # Anchor missing check via temporary table override
            fake_text = b"no matching anchor text here\n"
            fake_sha = hashlib.sha256(fake_text).hexdigest()
            (portals / "issue_3.md").write_bytes(fake_text)
            orig_sha = mod.PINNED_PORTAL_SHA256["issue_3.md"]
            try:
                mod.PINNED_PORTAL_SHA256["issue_3.md"] = fake_sha
                # Also write matching real shas for earlier files? issue_2.md comes first!
                # Populate issue_2.md too with fake_sha so issue_3.md anchor guard executes.
                orig_sha2 = mod.PINNED_PORTAL_SHA256["issue_2.md"]
                (portals / "issue_2.md").write_bytes(fake_text)
                mod.PINNED_PORTAL_SHA256["issue_2.md"] = fake_sha
                try:
                    with self.assertRaisesRegex(ValueError, "PORTAL_ANCHOR_MISSING:issue_3.md"):
                        mod.inspect_round10_aletheia_portals(root)
                finally:
                    mod.PINNED_PORTAL_SHA256["issue_2.md"] = orig_sha2
            finally:
                mod.PINNED_PORTAL_SHA256["issue_3.md"] = orig_sha

    def test_live_and_standalone_audit_and_cli(self) -> None:
        standalone_res = mod.run_full_audit(standalone=True)
        _assert_no_floats(self, standalone_res)
        self.assertEqual(standalone_res["portal_verification"]["mode"], "standalone_self_contained")
        self.assertEqual(standalone_res["v15_v20_integration_matrix"]["counts"]["issue5_total"], 13)
        self.assertEqual(standalone_res["v15_v20_integration_matrix"]["counts"]["cya_gap_total"], 6)

        # Always exercise full live-portal inspection happy path on a self-contained synthetic tree
        with tempfile.TemporaryDirectory() as tmp:
            syn_root = Path(tmp)
            syn_git = syn_root / "repos" / "aletheia-live" / ".git"
            syn_git.mkdir(parents=True)
            syn_lines = [f"{sha} {ref}" for ref, sha in mod.PINNED_ALETHEIA_LIVE_REFS.items()]
            (syn_git / "packed-refs").write_text("\n".join(syn_lines) + "\n", encoding="utf-8")

            syn_portals = syn_root / "portals" / "aletheia"
            orig_shas = dict(mod.PINNED_PORTAL_SHA256)
            try:
                for rel in mod.PINNED_PORTAL_SHA256:
                    anchors = mod.PORTAL_VERBATIM_ANCHORS.get(rel, ("placeholder",))
                    raw_bytes = ("\n".join(anchors) + "\n").encode("utf-8")
                    p = syn_portals / rel
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(raw_bytes)
                    mod.PINNED_PORTAL_SHA256[rel] = hashlib.sha256(raw_bytes).hexdigest()
                syn_res = mod.run_full_audit(standalone=False, round10_root=syn_root)
                _assert_no_floats(self, syn_res)
                self.assertEqual(syn_res["portal_verification"]["mode"], "live_readonly")
                self.assertTrue(syn_res["portal_verification"]["pr8_stale_table_sha_confirmed"])
            finally:
                mod.PINNED_PORTAL_SHA256.clear()
                mod.PINNED_PORTAL_SHA256.update(orig_shas)

        # Also exercise the actual live workspace tree when running inside symbiosis/round10/
        real_root = Path(__file__).resolve().parent.parent
        if (real_root / "repos" / "aletheia-live" / ".git").is_dir():
            live_res = mod.run_full_audit(standalone=False)
            _assert_no_floats(self, live_res)
            self.assertEqual(live_res["portal_verification"]["mode"], "live_readonly")
            self.assertTrue(live_res["portal_verification"]["pr8_stale_table_sha_confirmed"])

        with tempfile.TemporaryDirectory() as tmp:
            cert_path = Path(tmp) / "cert.json"
            buf_json = io.StringIO()
            with mock.patch("sys.stdout", buf_json):
                rc = mod.main(["--standalone", "--json", "--write-cert", str(cert_path)])
            self.assertEqual(rc, 0)
            parsed = json.loads(cert_path.read_text(encoding="utf-8"))
            _assert_no_floats(self, parsed)
            self.assertEqual(parsed["certificate_sha256"], standalone_res["certificate_sha256"])
            self.assertEqual(json.loads(buf_json.getvalue())["certificate_sha256"], standalone_res["certificate_sha256"])

            buf_txt = io.StringIO()
            with mock.patch("sys.stdout", buf_txt):
                rc_txt = mod.main(["--standalone"])
            self.assertEqual(rc_txt, 0)
            self.assertIn("[AUDIT-086R] PASS", buf_txt.getvalue())

        with self.assertRaisesRegex(ValueError, "CLI_MISSING_WRITE_CERT_PATH"):
            mod.main(["--write-cert"])
        with self.assertRaisesRegex(ValueError, "CLI_UNKNOWN_ARG"):
            mod.main(["--bogus-flag"])


if __name__ == "__main__":
    unittest.main()
