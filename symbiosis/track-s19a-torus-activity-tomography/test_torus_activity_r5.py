#!/usr/bin/env python3
"""
AUDIT-118A Assertion-Free R5 Unit, Zone-B Adversarial & Mutation-Isolation Suite
(`test_torus_activity_r5.py`).

Zero bare `assert` statements (100% `python3 -O` parity). Covers:
  - Strict primitive type/boundary validators (rejecting bool-as-int, int-as-bool,
    lying Sequence/Mapping, builtin subclasses, 2048-bit & 620-digit integer caps)
  - Iterative depth-capped JSON (`max_depth=64`, blocking 1,500-deep list, 100-deep
    JSON, cycles, floats, NaN/Inf, duplicate keys, non-str/mixed keys, oversized JSON)
  - Strict 64-lowercase-ASCII-hex check BEFORE `hmac.compare_digest` (blocking `'é'*64`
    and lone surrogate `chr(0xD800)*64` with zero raw `TypeError`)
  - All 5 exact-Z/Q meta-recursive telemetry pillars + every must-fail negative control
  - Full CLI (`--standalone --json`, `--write`, `--check`), symlink/ancestor/CRLF/UTF-8
    guards, and 100.0% refusal-site & AST `BoolOp` mutation isolation.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextlib import redirect_stderr, redirect_stdout
import copy
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import torus_activity_audit as audit
import torus_activity_oracle as oracle


class _LyingSequence(Sequence):
    """Adversarial Sequence whose __len__ lies relative to __iter__."""

    def __init__(self, items: list[int]) -> None:
        self._items = items

    def __len__(self) -> int:
        return 1

    def __getitem__(self, idx: int) -> int:
        return self._items[idx]

    def __iter__(self):
        return iter(self._items)


class _LyingMapping(Mapping):
    """Adversarial Mapping subclass that is not a strict dict."""

    def __init__(self, data: dict[str, int]) -> None:
        self._data = data

    def __getitem__(self, key: str) -> int:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


class _IntSub(int):
    pass


class _ListSub(list):
    pass


class _DictSub(dict):
    pass


class _StrSub(str):
    pass


class TestZoneBHardeningPrimitives(unittest.TestCase):
    def test_primitive_validators_subclasses_and_boundaries(self) -> None:
        # require_int exact boundaries & bit_length cap
        max_2048 = (1 << oracle.MAX_INT_BITS) - 1
        self.assertEqual(oracle.require_int(max_2048, "big"), max_2048)
        self.assertEqual(oracle.require_int(-max_2048, "neg_big"), -max_2048)
        self.assertEqual(oracle.require_int(2, "x", lo=2, hi=5), 2)
        self.assertEqual(oracle.require_int(5, "x", lo=2, hi=5), 5)

        for bad in (True, False, _IntSub(1), 1.0, "1", None):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.require_int(bad, "x")
            self.assertEqual(cm.exception.code, "INVALID_INT_TYPE")

        for over_bits in (1 << oracle.MAX_INT_BITS, -(1 << oracle.MAX_INT_BITS), 10**5000):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.require_int(over_bits, "x")
            self.assertEqual(cm.exception.code, "INT_BIT_LIMIT")

        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.require_int(1, "x", lo=2, hi=5)
        self.assertEqual(cm.exception.code, "INT_BELOW_MIN")
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.require_int(6, "x", lo=2, hi=5)
        self.assertEqual(cm.exception.code, "INT_ABOVE_MAX")

        # require_bool
        self.assertIs(oracle.require_bool(True, "b"), True)
        self.assertIs(oracle.require_bool(False, "b"), False)
        for bad in (0, 1, "true", None):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.require_bool(bad, "b")
            self.assertEqual(cm.exception.code, "INVALID_BOOL_TYPE")

        # require_str
        self.assertEqual(oracle.require_str("a", "s", min_len=1, max_len=3), "a")
        self.assertEqual(oracle.require_str("abc", "s", min_len=1, max_len=3), "abc")
        for bad in (_StrSub("a"), 1, None, b"a"):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.require_str(bad, "s")
            self.assertEqual(cm.exception.code, "INVALID_STR_TYPE")
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.require_str("", "s", min_len=1, max_len=3)
        self.assertEqual(cm.exception.code, "STR_TOO_SHORT")
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.require_str("abcd", "s", min_len=1, max_len=3)
        self.assertEqual(cm.exception.code, "STR_TOO_LONG")

        # require_seq (rejects lying Sequence & list subclass)
        self.assertEqual(oracle.require_seq([1], "q", min_len=1, max_len=2), (1,))
        self.assertEqual(oracle.require_seq((1, 2), "q", min_len=1, max_len=2), (1, 2))
        for bad in (_LyingSequence([1, 2, 3]), _ListSub([1]), "ab", {1: 2}, None):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.require_seq(bad, "q", min_len=1, max_len=3)
            self.assertEqual(cm.exception.code, "INVALID_SEQ_TYPE")
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.require_seq([], "q", min_len=1, max_len=2)
        self.assertEqual(cm.exception.code, "SEQ_TOO_SHORT")
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.require_seq([1, 2, 3], "q", min_len=1, max_len=2)
        self.assertEqual(cm.exception.code, "SEQ_TOO_LONG")

        # require_mapping (rejects lying Mapping, dict subclass, non-str keys)
        self.assertEqual(oracle.require_mapping({"a": 1}, "m"), {"a": 1})
        for bad in (_LyingMapping({"a": 1}), _DictSub({"a": 1}), [("a", 1)], None):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.require_mapping(bad, "m")
            self.assertEqual(cm.exception.code, "INVALID_MAPPING_TYPE")
        for bad_k in ({1: "a"}, {True: "a"}, {_StrSub("a"): 1}):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.require_mapping(bad_k, "m")
            self.assertEqual(cm.exception.code, "NON_STR_KEY")

        # require_hex64_ascii & constant_time_hex64_equal BEFORE hmac.compare_digest
        good = "0123456789abcdef" * 4
        other = "fedcba9876543210" * 4
        self.assertEqual(oracle.require_hex64_ascii(good), good)
        self.assertTrue(oracle.constant_time_hex64_equal(good, good))
        self.assertFalse(oracle.constant_time_hex64_equal(good, other))
        for bad_t in (123, None, _StrSub(good), b"a" * 64):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.require_hex64_ascii(bad_t)
            self.assertEqual(cm.exception.code, "INVALID_DIGEST_TYPE")
        for bad_len in ("a" * 63, "a" * 65, ""):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.require_hex64_ascii(bad_len)
            self.assertEqual(cm.exception.code, "INVALID_DIGEST_LEN")
        for bad_hex in ("\u00e9" * 64, chr(0xD800) * 64, "A" * 64, "g" * 64):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.constant_time_hex64_equal(bad_hex, good)
            self.assertEqual(cm.exception.code, "INVALID_DIGEST_HEX")

        # fmt_q & ratio_q
        self.assertEqual(oracle.fmt_q(Fraction(4, 2)), "2")
        self.assertEqual(oracle.fmt_q(Fraction(3, 5)), "3/5")
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.fmt_q(1)  # type: ignore[arg-type]
        self.assertEqual(cm.exception.code, "INVALID_FRACTION_TYPE")
        self.assertEqual(oracle.ratio_q(3, 6), Fraction(1, 2))
        with self.assertRaises(oracle.TorusActivityError):
            oracle.ratio_q(1, 0)

    def test_strict_json_depth_bits_digits_and_types(self) -> None:
        # Exact depth boundary 64 passes, 65 fails
        exact64: object = 0
        for _ in range(oracle.MAX_JSON_DEPTH):
            exact64 = [exact64]
        oracle.validate_json_value(exact64)
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.validate_json_value([exact64])
        self.assertEqual(cm.exception.code, "MAX_DEPTH_EXCEEDED")

        # 1500-deep Python list & cyclic list never trigger RecursionError
        deep1500: object = 0
        for _ in range(1500):
            deep1500 = [deep1500]
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.canonical_json_bytes(deep1500)
        self.assertEqual(cm.exception.code, "MAX_DEPTH_EXCEEDED")
        cyc: list[object] = []
        cyc.append(cyc)
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.validate_json_value(cyc)
        self.assertEqual(cm.exception.code, "MAX_DEPTH_EXCEEDED")

        # 100-deep JSON and 1500-deep JSON both cleanly rejected
        for depth in (100, 1500):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.parse_strict_json("[" * depth + "0" + "]" * depth)
            self.assertIn(cm.exception.code, ("MAX_DEPTH_EXCEEDED", "JSON_PARSE_ERROR"))

        # Exact 2048-bit & 620-digit parser boundaries (including direct hook check)
        max_2048 = (1 << oracle.MAX_INT_BITS) - 1
        over_2048 = 1 << oracle.MAX_INT_BITS
        self.assertEqual(oracle._parse_capped_int_token(str(max_2048)), max_2048)
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle._parse_capped_int_token(str(over_2048))
        self.assertEqual(cm.exception.code, "INT_BIT_LIMIT")
        self.assertEqual(oracle.parse_strict_json(f'{{"n":{max_2048},"m":-{max_2048}}}')["n"], max_2048)
        self.assertEqual(oracle.canonical_sha256({"b": True, "a": None, "c": "x", "d": 0}), hashlib.sha256(b'{"a":null,"b":true,"c":"x","d":0}').hexdigest())

        for bad_obj, code in (
            ({1: "a"}, "NON_STR_KEY"),
            ({True: "a"}, "NON_STR_KEY"),
            ({"x": 1.0}, "FLOAT_FORBIDDEN"),
            ({"x": (1, 2)}, "UNSUPPORTED_JSON_TYPE"),
            ({"x": _IntSub(1)}, "UNSUPPORTED_JSON_TYPE"),
            ({"x": _ListSub([1])}, "UNSUPPORTED_JSON_TYPE"),
            ({"x": _DictSub({"k": 1})}, "UNSUPPORTED_JSON_TYPE"),
            ({"x": over_2048}, "INT_BIT_LIMIT"),
            ({"x": 10**5000}, "INT_BIT_LIMIT"),
        ):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.validate_json_value(bad_obj)
            self.assertEqual(cm.exception.code, code)

        ok_620_neg_zero = '{"n":' + ("1" + "0" * (oracle.MAX_INT_DIGITS - 1)) + "}"
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.parse_strict_json(ok_620_neg_zero)
        self.assertEqual(cm.exception.code, "INT_BIT_LIMIT")

        for bad_txt, code in (
            (f'{{"n":{over_2048}}}', "INT_BIT_LIMIT"),
            (f'{{"n":-{over_2048}}}', "INT_BIT_LIMIT"),
            ('{"n":' + ("9" * (oracle.MAX_INT_DIGITS + 1)) + "}", "INT_DIGIT_LIMIT"),
            ('{"n":-' + ("9" * (oracle.MAX_INT_DIGITS + 1)) + "}", "INT_DIGIT_LIMIT"),
            ('{"n":' + ("9" * 5000) + "}", "INT_DIGIT_LIMIT"),
            ('{"x":1.5}', "JSON_FLOAT_FORBIDDEN"),
            ('{"x":1e3}', "JSON_FLOAT_FORBIDDEN"),
            ('{"x":NaN}', "JSON_CONSTANT_FORBIDDEN"),
            ('{"x":Infinity}', "JSON_CONSTANT_FORBIDDEN"),
            ('{"a":1,"a":2}', "JSON_DUPLICATE_KEY"),
            ("", "EMPTY_JSON"),
            ("   \n ", "EMPTY_JSON"),
            ("{bad", "JSON_PARSE_ERROR"),
        ):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.parse_strict_json(bad_txt)
            self.assertEqual(cm.exception.code, code)

        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.parse_strict_json(b"{}")  # type: ignore[arg-type]
        self.assertEqual(cm.exception.code, "INVALID_JSON_INPUT")
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.parse_strict_json('{"s":"' + chr(0xD800) + '"}')
        self.assertEqual(cm.exception.code, "INVALID_UTF8")

        exact_cap = '{"s":"' + ("a" * (oracle.MAX_JSON_BYTES - 8)) + '"}'
        self.assertEqual(len(exact_cap.encode("utf-8")), oracle.MAX_JSON_BYTES)
        self.assertIn("s", oracle.parse_strict_json(exact_cap))
        over_cap = '{"s":"' + ("a" * (oracle.MAX_JSON_BYTES - 7)) + '"}'
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.parse_strict_json(over_cap)
        self.assertEqual(cm.exception.code, "JSON_TOO_LARGE")


class TestFiveTelemetryPillars(unittest.TestCase):
    def test_pillar1_audit_outcomes_convergence_and_erlang(self) -> None:
        p1 = oracle.certify_pillar1_audit_and_erlang()
        self.assertTrue(p1["passed"])
        self.assertEqual(p1["total_rows"], 280)
        self.assertEqual(p1["verified_rate_q"], "7/10")
        self.assertEqual(p1["r2_convergence_rate_q"], "74/77")
        self.assertEqual(p1["core_total_ids"], 117)
        self.assertEqual(p1["core_logged_ids"], 116)
        self.assertEqual(p1["core_mean_passes_to_verified_q"], "199/113")
        self.assertTrue(p1["erlang_churn_eliminated"])
        self.assertEqual(p1["gate8_prereg_rows_logged"], 0)

        # Must-fail controls killing every guard and BoolOp in Pillar 1
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar1_audit_and_erlang(
                categories=({"category": "CORE", "verified": 0, "partial_fragile": 0, "falsified": 0},),
            )
        self.assertEqual(cm.exception.code, "EMPTY_AUDIT_TABLE")

        # Each of rd_v, rd_pf, rd_f mismatch independently (kills or->and & !=)
        for field in ("verified", "partial_fragile", "falsified"):
            bad_rounds = copy.deepcopy(list(oracle.AUDIT_ROUND_COUNTS))
            bad_rounds[0][field] += 1
            with self.assertRaises(oracle.TorusActivityError) as cm:
                oracle.certify_pillar1_audit_and_erlang(rounds=tuple(bad_rounds))
            self.assertEqual(cm.exception.code, "AUDIT_PARTITION_DRIFT")

        # r2_tot == 0 branch
        no_r2_rounds = ({"round": "R1", "verified": 196, "partial_fragile": 83, "falsified": 1},)
        res_no_r2 = oracle.certify_pillar1_audit_and_erlang(rounds=no_r2_rounds)
        self.assertEqual(res_no_r2["r2_convergence_rate_q"], "0")

        # zero verified core tracks
        bad_conv = dict(oracle.CORE_CONVERGENCE_TABLE)
        for k in ("verified_pass_1", "verified_pass_2", "verified_pass_3", "verified_pass_4", "verified_pass_5"):
            bad_conv[k] = 0
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar1_audit_and_erlang(convergence=bad_conv)
        self.assertEqual(cm.exception.code, "NO_VERIFIED_CORE_TRACKS")

        # Erlang sum & split drift
        bad_erl = copy.deepcopy(oracle.ERLANG_BOUNDARY_COUNTS)
        bad_erl["pre_erlang"]["verified"] = 1
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar1_audit_and_erlang(erlang=bad_erl)
        self.assertEqual(cm.exception.code, "PRE_ERLANG_SUM_DRIFT")

        bad_erl2 = copy.deepcopy(oracle.ERLANG_BOUNDARY_COUNTS)
        bad_erl2["post_erlang"]["verified"] = 1
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar1_audit_and_erlang(erlang=bad_erl2)
        self.assertEqual(cm.exception.code, "POST_ERLANG_SUM_DRIFT")

        bad_erl3 = copy.deepcopy(oracle.ERLANG_BOUNDARY_COUNTS)
        bad_erl3["post_erlang"]["total"] += 1
        bad_erl3["post_erlang"]["verified"] += 1
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar1_audit_and_erlang(erlang=bad_erl3)
        self.assertEqual(cm.exception.code, "ERLANG_SPLIT_DRIFT")

        # BoolOp isolation on `passed` & `erlang_churn_eliminated`
        # (a) overall_delta <= 0 only
        e_low_ov = copy.deepcopy(oracle.ERLANG_BOUNDARY_COUNTS)
        e_low_ov["post_erlang"]["verified"] = 50
        e_low_ov["post_erlang"]["partial_fragile"] = 43
        r_ov = oracle.certify_pillar1_audit_and_erlang(erlang=e_low_ov)
        self.assertFalse(r_ov["passed"])
        self.assertTrue(r_ov["erlang_churn_eliminated"])
        # (b) r1_delta <= 0 only
        e_low_r1 = copy.deepcopy(oracle.ERLANG_BOUNDARY_COUNTS)
        e_low_r1["post_erlang"]["r1_verified"] = 20
        self.assertFalse(oracle.certify_pillar1_audit_and_erlang(erlang=e_low_r1)["passed"])
        # (c) post_churn >= pre_churn (and pre_churn=1, post_churn=1 kills churn BoolOp)
        e_churn = copy.deepcopy(oracle.ERLANG_BOUNDARY_COUNTS)
        e_churn["post_erlang"]["mid_audit_churn_incidents"] = 1
        r_ch = oracle.certify_pillar1_audit_and_erlang(erlang=e_churn)
        self.assertFalse(r_ch["passed"])
        self.assertFalse(r_ch["erlang_churn_eliminated"])
        # (d) pre_churn=0, post_churn=0 kills churn BoolOp other side
        e_nochurn = copy.deepcopy(oracle.ERLANG_BOUNDARY_COUNTS)
        e_nochurn["pre_erlang"]["mid_audit_churn_incidents"] = 0
        self.assertFalse(oracle.certify_pillar1_audit_and_erlang(erlang=e_nochurn)["erlang_churn_eliminated"])

    def test_pillar2_multifamily_catch_matrix(self) -> None:
        p2 = oracle.certify_pillar2_multifamily_catch_matrix()
        self.assertTrue(p2["passed"])
        self.assertEqual(p2["external_runs_total"], 51)
        self.assertEqual(p2["external_completed"], 41)
        self.assertEqual(p2["external_catches"], 18)
        self.assertEqual(p2["external_harness_failures"], 10)
        self.assertEqual(p2["east_asia_completion_rate_q"], "34/35")
        self.assertEqual(p2["us_eu_completion_rate_q"], "7/16")
        self.assertTrue(p2["no_single_family_complete"])

        # Duplicate family, outcome drift, run drift, missing strata
        dup_f = (oracle.VERIFIER_FAMILIES_TABLE[0], oracle.VERIFIER_FAMILIES_TABLE[0])
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar2_multifamily_catch_matrix(families=dup_f)
        self.assertEqual(cm.exception.code, "DUPLICATE_FAMILY")

        bad_out = copy.deepcopy(list(oracle.VERIFIER_FAMILIES_TABLE))
        bad_out[3]["passes"] = 0
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar2_multifamily_catch_matrix(families=tuple(bad_out))
        self.assertEqual(cm.exception.code, "FAMILY_OUTCOME_DRIFT")

        bad_run = copy.deepcopy(list(oracle.VERIFIER_FAMILIES_TABLE))
        bad_run[3]["timeouts"] = 1
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar2_multifamily_catch_matrix(families=tuple(bad_run))
        self.assertEqual(cm.exception.code, "FAMILY_RUN_DRIFT")

        no_ea = tuple(r for r in oracle.VERIFIER_FAMILIES_TABLE if r["region"] != "east_asia")
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar2_multifamily_catch_matrix(families=no_ea)
        self.assertEqual(cm.exception.code, "MISSING_REGION_STRATUM")

        no_useu = tuple(r for r in oracle.VERIFIER_FAMILIES_TABLE if r["region"] not in ("us_eu", "us_eu_or_ea_tui"))
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar2_multifamily_catch_matrix(families=no_useu)
        self.assertEqual(cm.exception.code, "MISSING_REGION_STRATUM")

        # Signature errors
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar2_multifamily_catch_matrix(
                signatures=({"signature": "s", "families": ["ghost"], "example": "e"},),
            )
        self.assertEqual(cm.exception.code, "UNKNOWN_SIGNATURE_FAMILY")

        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar2_multifamily_catch_matrix(
                signatures=({"signature": "s", "families": ["glm_53", "glm_53"], "example": "e"},),
            )
        self.assertEqual(cm.exception.code, "DUPLICATE_SIGNATURE_FAMILY")

        # BoolOp isolation on `passed`: (a) single family complete; (b) exclusive_signatures == 3
        dom_sigs = tuple(
            {"signature": f"s{i}", "families": ["deepseek_v41_flash"], "example": "e"}
            for i in range(4)
        )
        self.assertFalse(oracle.certify_pillar2_multifamily_catch_matrix(signatures=dom_sigs)["passed"])
        low_ex_sigs = (
            {"signature": "s1", "families": ["deepseek_v41_flash"], "example": "e"},
            {"signature": "s2", "families": ["glm_53"], "example": "e"},
            {"signature": "s3", "families": ["muse_code"], "example": "e"},
            {"signature": "s4", "families": ["glm_53", "muse_code"], "example": "e"},
        )
        self.assertFalse(oracle.certify_pillar2_multifamily_catch_matrix(signatures=low_ex_sigs)["passed"])
        # Exact boundary exclusive_signatures == 4 passes
        exact4_sigs = (
            {"signature": "s1", "families": ["deepseek_v41_flash"], "example": "e"},
            {"signature": "s2", "families": ["glm_53"], "example": "e"},
            {"signature": "s3", "families": ["muse_code"], "example": "e"},
            {"signature": "s4", "families": ["claude_code"], "example": "e"},
        )
        self.assertTrue(oracle.certify_pillar2_multifamily_catch_matrix(signatures=exact4_sigs)["passed"])

    def test_pillar3_pareto_defect_taxonomy(self) -> None:
        p3 = oracle.certify_pillar3_pareto_defect_taxonomy()
        self.assertTrue(p3["passed"])
        self.assertEqual(p3["defect_class_count"], 15)
        self.assertEqual(p3["total_incidents"], 93)
        self.assertEqual(p3["zone_b_api_incidents"], 57)
        self.assertEqual(p3["hygiene_ops_incidents"], 36)
        self.assertEqual(p3["pareto_80pct_knee_rank"], 9)

        # Duplicate id, invalid zone, Pareto order violation
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar3_pareto_defect_taxonomy(
                taxonomy=(
                    {"id": "D1", "name": "a", "zone": "zone_b_api", "incidents": 5, "board_msgs": 1},
                    {"id": "D1", "name": "b", "zone": "hygiene_ops", "incidents": 4, "board_msgs": 1},
                ),
            )
        self.assertEqual(cm.exception.code, "DUPLICATE_DEFECT_ID")

        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar3_pareto_defect_taxonomy(
                taxonomy=(
                    {"id": "D1", "name": "a", "zone": "bad_zone", "incidents": 5, "board_msgs": 1},
                    {"id": "D2", "name": "b", "zone": "hygiene_ops", "incidents": 4, "board_msgs": 1},
                ),
            )
        self.assertEqual(cm.exception.code, "INVALID_DEFECT_ZONE")

        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar3_pareto_defect_taxonomy(
                taxonomy=(
                    {"id": "D1", "name": "a", "zone": "zone_b_api", "incidents": 3, "board_msgs": 1},
                    {"id": "D2", "name": "b", "zone": "hygiene_ops", "incidents": 5, "board_msgs": 1},
                ),
            )
        self.assertEqual(cm.exception.code, "PARETO_ORDER_VIOLATION")

        # BoolOp & exact boundary isolation on `passed` & 80% knee (cum * 5 == 4 * total)
        hyg_heavy = (
            {"id": "D1", "name": "a", "zone": "hygiene_ops", "incidents": 4, "board_msgs": 1},
            {"id": "D2", "name": "b", "zone": "zone_b_api", "incidents": 1, "board_msgs": 1},
        )
        r_hyg = oracle.certify_pillar3_pareto_defect_taxonomy(taxonomy=hyg_heavy)
        self.assertFalse(r_hyg["passed"])
        self.assertEqual(r_hyg["pareto_80pct_knee_rank"], 1)

        # 11 equal zone_b_api classes -> zone_b > hygiene True, top5_sum*2 = 10 < 11 False
        flat11 = tuple(
            {"id": f"D{i}", "name": f"n{i}", "zone": "zone_b_api", "incidents": 1, "board_msgs": 0}
            for i in range(11)
        )
        self.assertFalse(oracle.certify_pillar3_pareto_defect_taxonomy(taxonomy=flat11)["passed"])
        # Exact boundary 10 equal -> top5_sum*2 == 10 == total -> True
        flat10 = flat11[:10]
        self.assertTrue(oracle.certify_pillar3_pareto_defect_taxonomy(taxonomy=flat10)["passed"])

    def test_pillar4_throughput_latency_and_bottlenecks(self) -> None:
        p4 = oracle.certify_pillar4_throughput_latency_bottlenecks()
        self.assertTrue(p4["passed"])
        self.assertEqual(p4["agent_count"], 17)
        self.assertEqual(p4["total_steps"], 44040)
        self.assertEqual(p4["total_turns"], 11856)
        self.assertEqual(p4["total_tool_calls"], 23199)
        self.assertEqual(p4["total_board_posts"], 1018)
        self.assertEqual(p4["best_batching_core_agent"], "verifier")
        self.assertEqual(p4["worst_batching_core_agent"], "monitor")
        self.assertEqual(p4["monitor_turns_per_post_q"], "187")
        self.assertEqual(p4["aletheia_pr1_polling_share_q"], "8/27")

        # Duplicate agent, turn drift, post drift, missing core role, empty tasks
        dup_ag = (oracle.AGENT_TELEMETRY_17[0], oracle.AGENT_TELEMETRY_17[0])
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar4_throughput_latency_bottlenecks(agents=dup_ag)
        self.assertEqual(cm.exception.code, "DUPLICATE_AGENT")

        bad_t = copy.deepcopy(list(oracle.AGENT_TELEMETRY_17))
        bad_t[0]["serial_turns"] += 1
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar4_throughput_latency_bottlenecks(agents=tuple(bad_t))
        self.assertEqual(cm.exception.code, "AGENT_TURN_DRIFT")

        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar4_throughput_latency_bottlenecks(expected_board_posts=999)
        self.assertEqual(cm.exception.code, "BOARD_POST_SUM_DRIFT")

        no_mon = tuple(r for r in oracle.AGENT_TELEMETRY_17 if r["agent"] != "monitor")
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar4_throughput_latency_bottlenecks(agents=no_mon, expected_board_posts=1012)
        self.assertEqual(cm.exception.code, "MISSING_CORE_ROLE")

        no_coord = tuple(r for r in oracle.AGENT_TELEMETRY_17 if r["agent"] != "coordinator")
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar4_throughput_latency_bottlenecks(agents=no_coord, expected_board_posts=733)
        self.assertEqual(cm.exception.code, "MISSING_CORE_ROLE")

        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar4_throughput_latency_bottlenecks(tasks={"github_aletheia_pr1_polling": 0})
        self.assertEqual(cm.exception.code, "EMPTY_TASK_COUNTS")

        # BoolOp isolation on `passed`: each of post_mean_q, post_max, post_qmax failing individually
        l_mean = copy.deepcopy(oracle.VERIFIER_LATENCY_SNAPSHOT)
        l_mean["post_v2_active"]["sum_latency_s"] = 50000
        self.assertFalse(oracle.certify_pillar4_throughput_latency_bottlenecks(latency=l_mean)["passed"])

        l_max = copy.deepcopy(oracle.VERIFIER_LATENCY_SNAPSHOT)
        l_max["post_v2_active"]["max_s"] = 3867
        self.assertFalse(oracle.certify_pillar4_throughput_latency_bottlenecks(latency=l_max)["passed"])

        l_q = copy.deepcopy(oracle.VERIFIER_LATENCY_SNAPSHOT)
        l_q["post_v2_active"]["max_queue_depth"] = 7
        self.assertFalse(oracle.certify_pillar4_throughput_latency_bottlenecks(latency=l_q)["passed"])

    def test_pillar5_upgrades_hooks_routing_fuzz_and_counterfactual(self) -> None:
        p5 = oracle.certify_pillar5_v21_upgrades_and_counterfactual()
        self.assertTrue(p5["passed"])
        cf = p5["counterfactual_strata"]
        self.assertEqual(cf["core_audit_001_117"]["full_elimination_rate_q"], "5/38")
        self.assertEqual(cf["core_audit_001_117"]["any_zone_b_impact_rate_q"], "27/76")
        self.assertEqual(cf["modern_zone_b_097_117"]["full_elimination_rate_q"], "7/22")
        self.assertEqual(cf["latest_wave_112_116"]["full_elimination_rate_q"], "3/4")
        self.assertEqual(p5["zone_b_preflight_fuzz_12_vectors"]["vectors_blocked"], 12)

        # Empty counterfactual stratum guard
        bad_cf = copy.deepcopy(oracle.COUNTERFACTUAL_REWORK_COUNTS)
        bad_cf["core_audit_001_117"] = {"full_zone_b_fuzz": 0, "hybrid_zone_b_plus_domain": 0, "doc_linter_hooks": 0, "irreducible_domain": 0}
        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.certify_pillar5_v21_upgrades_and_counterfactual(counterfactual=bad_cf)
        self.assertEqual(cm.exception.code, "EMPTY_COUNTERFACTUAL_STRATUM")

        # Fuzz matrix BoolOp isolation (unblocked vector vs mismatched positive control)
        f_unblocked = oracle.run_zone_b_preflight_fuzz_matrix(extra_vectors=(("V_NOOP", lambda: None),))
        self.assertFalse(f_unblocked["passed"])
        f_bad_pos = oracle.run_zone_b_preflight_fuzz_matrix(positive_digest="b" * 64)
        self.assertFalse(f_bad_pos["passed"])

        # Pre-push git hook: every individual violation & BoolOp boundary
        base_rec = {
            "has_dco_signoff": True,
            "repo_is_private": False,
            "explicit_private_allowed": False,
            "git_changed_files": 100,
            "graphql_files_listed": 100,
            "openblas_num_threads": 1,
            "pr_is_self_authored": False,
            "review_action": "COMMENT",
        }
        self.assertTrue(oracle.evaluate_prepush_git_hook(base_rec)["passed"])

        # Private allowed explicitly passes (kills `and -> or` on `is_priv and not allow_priv`)
        priv_ok = dict(base_rec, repo_is_private=True, explicit_private_allowed=True)
        self.assertTrue(oracle.evaluate_prepush_git_hook(priv_ok)["passed"])
        priv_bad = dict(base_rec, repo_is_private=True, explicit_private_allowed=False)
        self.assertEqual(oracle.evaluate_prepush_git_hook(priv_bad)["violations"], ["PRIVATE_REPO_BLOCKED"])

        # Self-authored COMMENT passes, self-authored REQUEST_CHANGES fails (kills `and -> or`)
        self_comment = dict(base_rec, pr_is_self_authored=True, review_action="COMMENT")
        self.assertTrue(oracle.evaluate_prepush_git_hook(self_comment)["passed"])
        self_rc = dict(base_rec, pr_is_self_authored=True, review_action="REQUEST_CHANGES")
        self.assertEqual(oracle.evaluate_prepush_git_hook(self_rc)["violations"], ["SELF_AUTHORED_REVIEW_422"])

        # GraphQL boundary 101 > 100 fails
        gql_bad = dict(base_rec, git_changed_files=101, graphql_files_listed=100)
        self.assertEqual(oracle.evaluate_prepush_git_hook(gql_bad)["violations"], ["GRAPHQL_100_FILE_TRUNCATION"])

        with self.assertRaises(oracle.TorusActivityError) as cm:
            oracle.evaluate_prepush_git_hook(dict(base_rec, review_action="BOGUS"))
        self.assertEqual(cm.exception.code, "INVALID_REVIEW_ACTION")

        # Dual-verifier routing boundaries (q2 < q1 vs q2 == q1, wait == 1800 vs 1801)
        r_eq = oracle.route_dual_verifier(2, 2, 1800, starvation_cap_s=1800)
        self.assertEqual(r_eq["target"], "verifier")
        self.assertFalse(r_eq["starvation_reroute"])
        r_starve = oracle.route_dual_verifier(1, 3, 1801, starvation_cap_s=1800)
        self.assertEqual(r_starve["target"], "verifier-2")
        self.assertTrue(r_starve["starvation_reroute"])
        r_q2_less = oracle.route_dual_verifier(3, 1, 100, starvation_cap_s=1800)
        self.assertEqual(r_q2_less["target"], "verifier-2")
        self.assertFalse(r_q2_less["starvation_reroute"])


class TestAuditCertificateAndCLI(unittest.TestCase):
    def test_verify_certificate_dict_all_rejection_paths(self) -> None:
        cert = audit.build_certificate()
        ok = audit.verify_certificate_dict(cert)
        self.assertTrue(ok["valid"])

        for bad_root in ([], "x", None, _DictSub(cert)):
            with self.assertRaises(oracle.TorusActivityError) as cm:
                audit.verify_certificate_dict(bad_root)
            self.assertEqual(cm.exception.code, "CERT_NOT_DICT")

        # Mixed non-str key raises clean TorusActivityError (never raw TypeError on sorted!)
        with self.assertRaises(oracle.TorusActivityError) as cm:
            audit.verify_certificate_dict({"schema": "x", 1: 2})
        self.assertEqual(cm.exception.code, "NON_STR_KEY")

        c_extra = copy.deepcopy(cert)
        c_extra["rogue"] = 1
        with self.assertRaises(oracle.TorusActivityError) as cm:
            audit.verify_certificate_dict(c_extra)
        self.assertEqual(cm.exception.code, "CERT_SCHEMA_KEYS")

        c_schema = copy.deepcopy(cert)
        c_schema["schema"] = "wrong"
        with self.assertRaises(oracle.TorusActivityError) as cm:
            audit.verify_certificate_dict(c_schema)
        self.assertEqual(cm.exception.code, "CERT_SCHEMA_MISMATCH")

        c_schema_sub = copy.deepcopy(cert)
        c_schema_sub["schema"] = _StrSub(audit.CERT_SCHEMA)
        with self.assertRaises(oracle.TorusActivityError) as cm:
            audit.verify_certificate_dict(c_schema_sub)
        self.assertEqual(cm.exception.code, "UNSUPPORTED_JSON_TYPE")

        c_aid = copy.deepcopy(cert)
        c_aid["audit_id"] = "AUDIT-999"
        with self.assertRaises(oracle.TorusActivityError) as cm:
            audit.verify_certificate_dict(c_aid)
        self.assertEqual(cm.exception.code, "CERT_AUDIT_ID_MISMATCH")

        # Non-ASCII 64-char payload_sha256 & certificate_sha256 rejected BEFORE hmac.compare_digest
        c_nonascii = copy.deepcopy(cert)
        c_nonascii["payload_sha256"] = "\u00e9" * 64
        with self.assertRaises(oracle.TorusActivityError) as cm:
            audit.verify_certificate_dict(c_nonascii)
        self.assertEqual(cm.exception.code, "INVALID_DIGEST_HEX")

        c_psha = copy.deepcopy(cert)
        c_psha["payload_sha256"] = "0" * 64
        with self.assertRaises(oracle.TorusActivityError) as cm:
            audit.verify_certificate_dict(c_psha)
        self.assertEqual(cm.exception.code, "PAYLOAD_SHA_MISMATCH")

        c_csha = copy.deepcopy(cert)
        c_csha["certificate_sha256"] = "0" * 64
        with self.assertRaises(oracle.TorusActivityError) as cm:
            audit.verify_certificate_dict(c_csha)
        self.assertEqual(cm.exception.code, "CERTIFICATE_SHA_MISMATCH")

        # Forged re-signed payload (both digests recomputed, including bool-as-int forgery!)
        c_forged = copy.deepcopy(cert)
        c_forged["payload"]["pillar1_audit_outcomes_and_erlang"]["total_rows"] = True
        p_sha = hashlib.sha256(oracle.canonical_json_bytes(c_forged["payload"])).hexdigest()
        c_forged["payload_sha256"] = p_sha
        env = {k: c_forged[k] for k in ("schema", "audit_id", "payload_sha256", "payload")}
        c_forged["certificate_sha256"] = hashlib.sha256(oracle.canonical_json_bytes(env)).hexdigest()
        with self.assertRaises(oracle.TorusActivityError) as cm:
            audit.verify_certificate_dict(c_forged)
        self.assertEqual(cm.exception.code, "RECOMPUTED_PAYLOAD_DRIFT")

    def test_file_checks_and_cli_roundtrip(self) -> None:
        with self.assertRaises(oracle.TorusActivityError) as cm:
            audit.check_certificate_file("not_a_path")  # type: ignore[arg-type]
        self.assertEqual(cm.exception.code, "INVALID_PATH_TYPE")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cert_path = root / "cert.json"
            written = audit.write_certificate_file(cert_path)
            self.assertTrue(written["valid"])

            # Without trailing newline also accepted
            no_nl = root / "no_nl.json"
            no_nl.write_bytes(cert_path.read_bytes().rstrip(b"\n"))
            self.assertTrue(audit.check_certificate_file(no_nl)["valid"])

            # Missing file
            with self.assertRaises(oracle.TorusActivityError) as cm:
                audit.check_certificate_file(root / "missing.json")
            self.assertEqual(cm.exception.code, "CERT_FILE_NOT_FOUND")

            # Symlink target & symlink ancestor
            sym_file = root / "sym.json"
            sym_file.symlink_to(cert_path)
            with self.assertRaises(oracle.TorusActivityError) as cm:
                audit.check_certificate_file(sym_file)
            self.assertEqual(cm.exception.code, "SYMLINK_FORBIDDEN")

            real_sub = root / "real_sub"
            real_sub.mkdir()
            (real_sub / "c.json").write_bytes(cert_path.read_bytes())
            sym_dir = root / "sym_dir"
            sym_dir.symlink_to(real_sub)
            with self.assertRaises(oracle.TorusActivityError) as cm:
                audit.check_certificate_file(sym_dir / "c.json")
            self.assertEqual(cm.exception.code, "SYMLINK_ANCESTOR_FORBIDDEN")

            # Exact MAX_JSON_BYTES file passes size guard (fails later at schema), +1 fails size guard
            exact_cap_file = root / "exact_cap.json"
            exact_cap_file.write_bytes(b'{"s":"' + b"a" * (oracle.MAX_JSON_BYTES - 8) + b'"}')
            with self.assertRaises(oracle.TorusActivityError) as cm:
                audit.check_certificate_file(exact_cap_file)
            self.assertEqual(cm.exception.code, "CERT_SCHEMA_KEYS")

            big = root / "big.json"
            big.write_bytes(b"a" * (oracle.MAX_JSON_BYTES + 1))
            with self.assertRaises(oracle.TorusActivityError) as cm:
                audit.check_certificate_file(big)
            self.assertEqual(cm.exception.code, "CERT_FILE_TOO_LARGE")

            # CRLF & bare CR
            crlf = root / "crlf.json"
            crlf.write_bytes(cert_path.read_bytes().replace(b"\n", b"\r\n"))
            with self.assertRaises(oracle.TorusActivityError) as cm:
                audit.check_certificate_file(crlf)
            self.assertEqual(cm.exception.code, "CR_LINE_ENDINGS_FORBIDDEN")

            # Invalid UTF-8
            bad_utf8 = root / "bad.json"
            bad_utf8.write_bytes(b"\xff\xfe\x00")
            with self.assertRaises(oracle.TorusActivityError) as cm:
                audit.check_certificate_file(bad_utf8)
            self.assertEqual(cm.exception.code, "INVALID_UTF8")

            # Non-canonical JSON (extra whitespace / double newline)
            non_can = root / "noncan.json"
            non_can.write_bytes(cert_path.read_bytes() + b"\n")
            with self.assertRaises(oracle.TorusActivityError) as cm:
                audit.check_certificate_file(non_can)
            self.assertEqual(cm.exception.code, "NON_CANONICAL_CERT_BYTES")

            # CLI modes: --standalone --json, human default, --write, --check PASS & FAIL (rc=2)
            out_buf, err_buf = io.StringIO(), io.StringIO()
            with redirect_stdout(out_buf), redirect_stderr(err_buf):
                rc = audit.main(["--standalone"])
            self.assertEqual(rc, 0)
            self.assertIn("OK AUDIT-118A", out_buf.getvalue())

            w_path = root / "cli_written.json"
            out_buf = io.StringIO()
            with redirect_stdout(out_buf):
                rc = audit.main(["--write", str(w_path)])
            self.assertEqual(rc, 0)
            self.assertIn("WROTE AUDIT-118A", out_buf.getvalue())

            out_buf = io.StringIO()
            with redirect_stdout(out_buf):
                rc = audit.main(["--check", str(w_path)])
            self.assertEqual(rc, 0)
            self.assertIn("OK AUDIT-118A", out_buf.getvalue())

            # CLI --check fail-closed on non-ASCII digest & 5000-digit int -> clean exit 2
            bad_cli = root / "nonascii_sha.json"
            tampered = json.loads(cert_path.read_text(encoding="utf-8"))
            tampered["payload_sha256"] = "\u00e9" * 64
            bad_cli.write_bytes(json.dumps(tampered, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n")
            err_buf = io.StringIO()
            with redirect_stderr(err_buf):
                rc = audit.main(["--check", str(bad_cli)])
            self.assertEqual(rc, 2)
            self.assertIn("REJECT", err_buf.getvalue())

            big_int_cli = root / "big5000.json"
            big_int_cli.write_bytes(('{"n":' + ("9" * 5000) + "}\n").encode("ascii"))
            err_buf = io.StringIO()
            with redirect_stderr(err_buf):
                rc = audit.main(["--check", str(big_int_cli)])
            self.assertEqual(rc, 2)
            self.assertIn("INT_DIGIT_LIMIT", err_buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
