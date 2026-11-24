#!/usr/bin/env python3
"""Track S26 R5 Regression, Adversarial Zone-B & Mutation-Killing Test Suite.

Zero bare asserts, zero floats on trust paths, zero external dependencies, zero RNG.
"""
from __future__ import annotations

import ast
import copy
from fractions import Fraction
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import counterfactual_holonomy_audit as aud  # noqa: E402
import counterfactual_holonomy_oracle as orc  # noqa: E402


class _EvilPath(type(Path("."))):
    """Adversarial Path subclass rejected by require_safe_path."""


class _EvilInt(int):
    """Adversarial int subclass rejected by require_int."""


class _EvilStr(str):
    """Adversarial str subclass rejected by require_str."""


class _EvilFrac(Fraction):
    """Adversarial Fraction subclass rejected by require_fraction."""


class TestStaticHygieneAndPrimitives(unittest.TestCase):
    def test_zero_bare_asserts_and_zero_float_literals_in_track(self) -> None:
        for fname in (
            "counterfactual_holonomy_oracle.py",
            "counterfactual_holonomy_audit.py",
            "test_counterfactual_holonomy_r5.py",
        ):
            src = (_THIS_DIR / fname).read_text(encoding="utf-8")
            tree = ast.parse(src)
            asserts = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
            self.assertEqual(asserts, [], f"bare assert in {fname}: {asserts}")
            float_lits = [
                n.lineno
                for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and type(n.value) is float
            ]
            self.assertEqual(float_lits, [], f"float literal in {fname}: {float_lits}")
            float_calls = [
                n.lineno
                for n in ast.walk(tree)
                if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name)
                and n.func.id == "float"
            ]
            self.assertEqual(float_calls, [], f"float() call in {fname}: {float_calls}")

    def test_strict_primitive_validators_and_boundaries(self) -> None:
        # require_bool
        self.assertIs(orc.require_bool(True), True)
        self.assertIs(orc.require_bool(False), False)
        for bad_b in (1, 0, "true", None):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.require_bool(bad_b)
            self.assertEqual(cm.exception.code, "INVALID_BOOL")

        # require_int exact boundary (+/- (10**1000 - 1) OK, +/- 10**1000 rejected)
        lim = 10**orc.MAX_INT_DIGITS
        self.assertEqual(orc.require_int(lim - 1), lim - 1)
        self.assertEqual(orc.require_int(-(lim - 1)), -(lim - 1))
        for bad_i in (True, False, _EvilInt(1), "1", None):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.require_int(bad_i)
            self.assertEqual(cm.exception.code, "INVALID_INT")
        for huge_i in (lim, -lim, 10**5000, -(10**5000)):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.require_int(huge_i)
            self.assertEqual(cm.exception.code, "INT_DIGIT_LIMIT")

        # require_str & lone UTF-16 surrogates
        self.assertEqual(orc.require_str("ok"), "ok")
        for bad_s in (_EvilStr("ok"), b"ok", 123, None):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.require_str(bad_s)
            self.assertEqual(cm.exception.code, "INVALID_STR")
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_sur:
            orc.require_str("bad\ud800surrogate")
        self.assertEqual(cm_sur.exception.code, "INVALID_UTF8_SURROGATE")

        # require_sha256_hex
        good_h = "0123456789abcdef" * 4
        self.assertEqual(orc.require_sha256_hex(good_h), good_h)
        for bad_h in ("a" * 63, "a" * 65, "A" * 64, "g" * 64, "\u00e9" * 64):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.require_sha256_hex(bad_h)
            self.assertEqual(cm.exception.code, "INVALID_SHA256")

        # require_fraction & bit-length boundary (exact 4000 bits OK, 4001 bits rejected on num & den)
        max_4000 = (1 << orc.MAX_RATIONAL_BITS) - 1
        over_4000 = 1 << orc.MAX_RATIONAL_BITS
        self.assertEqual(orc.require_fraction(Fraction(max_4000, 1)), Fraction(max_4000, 1))
        self.assertEqual(orc.require_fraction(Fraction(1, max_4000)), Fraction(1, max_4000))
        self.assertEqual(orc.format_rational(Fraction(5, 1)), "5")
        self.assertEqual(orc.format_rational(Fraction(-7, 3)), "-7/3")
        for bad_f in (1, "1/2", _EvilFrac(1, 2)):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.require_fraction(bad_f)
            self.assertEqual(cm.exception.code, "INVALID_RATIONAL")
        for big_f in (Fraction(over_4000, 1), Fraction(1, over_4000)):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.require_fraction(big_f)
            self.assertEqual(cm.exception.code, "RATIONAL_BIT_LIMIT")

        # parse_exact_int_str & parse_exact_rational strict grammar
        self.assertEqual(orc.parse_exact_int_str("0"), 0)
        self.assertEqual(orc.parse_exact_int_str("10"), 10)
        self.assertEqual(orc.parse_exact_int_str("-1"), -1)
        self.assertEqual(orc.parse_exact_int_str("9" * orc.MAX_INT_DIGITS), int("9" * orc.MAX_INT_DIGITS))
        for bad_istr in ("", "-", "01", "-01", "-0", "+1", " 1", "1_0", "1a", "\u0661"):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.parse_exact_int_str(bad_istr)
            self.assertEqual(cm.exception.code, "INVALID_INT_STR")
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_bigs:
            orc.parse_exact_int_str("1" + "0" * orc.MAX_INT_DIGITS)
        self.assertEqual(cm_bigs.exception.code, "INT_DIGIT_LIMIT")

        self.assertEqual(orc.parse_exact_rational("0"), Fraction(0))
        self.assertEqual(orc.parse_exact_rational("-7/3"), Fraction(-7, 3))
        for bad_r, code in (
            ("1/2/3", "INVALID_RATIONAL_STR"),
            ("3/1", "INVALID_RATIONAL_STR"),
            ("3/0", "INVALID_RATIONAL_STR"),
            ("3/-2", "INVALID_RATIONAL_STR"),
            ("2/4", "NON_CANONICAL_RATIONAL"),
        ):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.parse_exact_rational(bad_r)
            self.assertEqual(cm.exception.code, code)

    def test_strict_json_parser_and_canonical_serializer(self) -> None:
        # Valid nested up to exact MAX_JSON_DEPTH
        obj: object = {"v": [None, True, False, 0, -7, "ok"]}
        raw_b = orc.canonical_json_bytes(obj)
        self.assertEqual(orc.parse_strict_json_text(raw_b.decode("ascii"), require_object=True), obj)
        self.assertEqual(orc.parse_strict_json_text("[1,2]", require_object=False), [1, 2])

        # Root non-object rejected when require_object=True
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_root:
            orc.parse_strict_json_text("[1,2]", require_object=True)
        self.assertEqual(cm_root.exception.code, "JSON_ROOT_NOT_OBJECT")

        # Exact MAX_JSON_BYTES text succeeds; MAX_JSON_BYTES + 1 fails
        exact_json = '{"k":"' + ("a" * (orc.MAX_JSON_BYTES - 8)) + '"}'
        self.assertEqual(len(exact_json.encode("utf-8")), orc.MAX_JSON_BYTES)
        self.assertEqual(len(orc.parse_strict_json_text(exact_json, require_object=True)["k"]), orc.MAX_JSON_BYTES - 8)

        # Duplicate keys, unicode-escaped duplicate keys, floats, NaN/Inf, huge ints, deep nesting, oversized
        for bad_txt, code in (
            ('{"a": 1, "a": 2}', "DUPLICATE_JSON_KEY"),
            ('{"a": 1, "\\u0061": 2}', "DUPLICATE_JSON_KEY"),
            ('{"x": 1e2}', "FLOAT_LITERAL_FORBIDDEN"),
            ('{"x": NaN}', "NONFINITE_LITERAL_FORBIDDEN"),
            ('{"x": Infinity}', "NONFINITE_LITERAL_FORBIDDEN"),
            ('{"x": ' + "9" * (orc.MAX_INT_DIGITS + 1) + "}", "INT_DIGIT_LIMIT"),
            ("{broken", "JSON_PARSE_ERROR"),
            ('{"a":' * (orc.MAX_JSON_DEPTH + 1) + "1" + "}" * (orc.MAX_JSON_DEPTH + 1), "JSON_DEPTH_LIMIT"),
            ('{"k": "' + "a" * orc.MAX_JSON_BYTES + '"}', "JSON_TOO_LARGE"),
        ):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.parse_strict_json_text(bad_txt, require_object=True)
            self.assertEqual(cm.exception.code, code)

        # Exact depth MAX_JSON_DEPTH succeeds, MAX_JSON_DEPTH+1 fails in canonical_json_bytes
        deep_ok: Any = 1
        for _ in range(orc.MAX_JSON_DEPTH):
            deep_ok = [deep_ok]
        self.assertTrue(orc.canonical_json_bytes(deep_ok).startswith(b"["))
        deep_bad = [deep_ok]
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_d:
            orc.canonical_json_bytes(deep_bad)
        self.assertEqual(cm_d.exception.code, "JSON_DEPTH_LIMIT")

        # Unsupported types & non-str dict keys in canonical_json_bytes
        for bad_obj, code in (
            ({1: "x"}, "INVALID_STR"),
            ({"s": "\ud800"}, "INVALID_UTF8_SURROGATE"),
            ({"k": (1, 2)}, "FORBIDDEN_JSON_TYPE"),
            ({"k": 10**5000}, "INT_DIGIT_LIMIT"),
        ):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm:
                orc.canonical_json_bytes(bad_obj)
            self.assertEqual(cm.exception.code, code)


class TestFourTheoremsAndControls(unittest.TestCase):
    def test_chiral_domain_guards_and_matrix_validation(self) -> None:
        # Invalid theta, non-positive C/h, bad vec2, bad PSD matrix
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_th:
            orc.chiral_flow_matrix(0, Fraction(1), Fraction(0), Fraction(1), Fraction(1))
        self.assertEqual(cm_th.exception.code, "INVALID_THETA")

        for bad_c in (Fraction(0), Fraction(-1)):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_c:
                orc.chiral_flow_matrix(1, bad_c, Fraction(0), Fraction(1), Fraction(1))
            self.assertEqual(cm_c.exception.code, "NON_POSITIVE_PARAM")

        for bad_v in ([Fraction(1), Fraction(2)], (Fraction(1),)):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_v:
                orc.chiral_flow_step(1, Fraction(1), Fraction(0), bad_v, Fraction(1), Fraction(1), (Fraction(1), Fraction(0)))  # type: ignore[arg-type]
            self.assertEqual(cm_v.exception.code, "INVALID_VEC2")

        # PSD guard: non-tuple, wrong len, non-symmetric, negative trace (det>0), negative det (trace>0)
        for bad_m, code in (
            ([[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]], "INVALID_MAT2"),
            (((Fraction(1), Fraction(0)),), "INVALID_MAT2"),
            (((Fraction(1), Fraction(2)), (Fraction(0), Fraction(1))), "NON_SYMMETRIC_COV"),
            (((Fraction(-1), Fraction(0)), (Fraction(0), Fraction(-1))), "NON_PSD_COV"),
            (((Fraction(1), Fraction(2)), (Fraction(2), Fraction(1))), "NON_PSD_COV"),
        ):
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_m:
                orc.recover_theta_c_from_anisotropic_cov(
                    bad_m,  # type: ignore[arg-type]
                    ((Fraction(3), Fraction(0)), (Fraction(0), Fraction(1))),
                    Fraction(1),
                    Fraction(1),
                    Fraction(1),
                )
            self.assertEqual(cm_m.exception.code, code)

        # ZERO_DRIFT_MOMENT when 2*q0 + a*h == 0
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_zdm:
            orc.recover_theta_c_from_anisotropic_cov(
                ((Fraction(3), Fraction(0)), (Fraction(0), Fraction(1))),
                ((Fraction(3), Fraction(0)), (Fraction(0), Fraction(1))),
                Fraction(1, 2),
                Fraction(-1),
                Fraction(1),
            )
        self.assertEqual(cm_zdm.exception.code, "ZERO_DRIFT_MOMENT")

        # ZERO_SIGNED_AREA & DEGENERATE_ACTION_SUM on 2-step helpers
        zero_v = (Fraction(0), Fraction(0))
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_za1:
            orc.recover_theta_c_two_step_norm_diff(zero_v, zero_v, Fraction(0), Fraction(1), Fraction(2), Fraction(1))
        self.assertEqual(cm_za1.exception.code, "ZERO_SIGNED_AREA")

        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_za2:
            orc.recover_theta_c_two_step_universal(zero_v, zero_v, Fraction(1), Fraction(2), Fraction(1))
        self.assertEqual(cm_za2.exception.code, "ZERO_SIGNED_AREA")

        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_ext:
            orc.predict_cf_two_step_extrapolation(zero_v, zero_v, zero_v, Fraction(2), Fraction(-2), Fraction(1))
        self.assertEqual(cm_ext.exception.code, "DEGENERATE_ACTION_SUM")

    def test_all_four_theorems_certified_and_independent_audit_tamper_kills(self) -> None:
        cert = orc.build_standalone_certificate()
        self.assertTrue(cert["payload"]["summary"]["all_theorems_verified"])
        self.assertEqual(cert["payload"]["summary"]["float_count_on_trust_path"], 0)
        res = orc.validate_certificate_payload(cert, full_replay=True)
        self.assertTrue(res["valid"])
        res_no_replay = orc.validate_certificate_payload(cert, full_replay=False)
        self.assertTrue(res_no_replay["valid"])
        self.assertFalse(res_no_replay["full_replay"])

        indep = aud.independent_audit_payload(cert["payload"])
        self.assertTrue(indep["independent_audit_passed"])

        # Verify validate_certificate_payload rejects every malformed structure & tamper
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_t:
            orc.validate_certificate_payload([])
        self.assertEqual(cm_t.exception.code, "INVALID_CERT_TYPE")

        bad_keys = dict(cert)
        bad_keys["extra"] = 1
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_k:
            orc.validate_certificate_payload(bad_keys)
        self.assertEqual(cm_k.exception.code, "INVALID_CERT_KEYS")

        bad_schema = dict(cert, schema="wrong")
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_sc:
            orc.validate_certificate_payload(bad_schema)
        self.assertEqual(cm_sc.exception.code, "INVALID_SCHEMA")

        bad_track = dict(cert, track_id="wrong")
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_tr:
            orc.validate_certificate_payload(bad_track)
        self.assertEqual(cm_tr.exception.code, "INVALID_TRACK_ID")

        bad_pay = dict(cert, payload=[1, 2])
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_pt:
            orc.validate_certificate_payload(bad_pay)
        self.assertEqual(cm_pt.exception.code, "INVALID_PAYLOAD_TYPE")

        flipped_p = ("0" if cert["payload_sha256"][0] != "0" else "1") + cert["payload_sha256"][1:]
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_ps:
            orc.validate_certificate_payload(dict(cert, payload_sha256=flipped_p))
        self.assertEqual(cm_ps.exception.code, "PAYLOAD_SHA256_MISMATCH")

        flipped_c = ("0" if cert["certificate_sha256"][0] != "0" else "1") + cert["certificate_sha256"][1:]
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_cs:
            orc.validate_certificate_payload(dict(cert, certificate_sha256=flipped_c))
        self.assertEqual(cm_cs.exception.code, "CERT_SHA256_MISMATCH")

        # Re-signed tampered payload passes full_replay=False but fails full_replay=True!
        resigned = copy.deepcopy(cert)
        resigned["payload"]["summary"]["rng_calls"] = 1
        resigned["payload_sha256"] = orc.sha256_canonical(resigned["payload"])
        resigned["certificate_sha256"] = orc.sha256_canonical(
            {k: resigned[k] for k in ("schema", "track_id", "payload_sha256", "payload")}
        )
        self.assertTrue(orc.validate_certificate_payload(resigned, full_replay=False)["valid"])
        with self.assertRaises(orc.CounterfactualHolonomyError) as cm_rep:
            orc.validate_certificate_payload(resigned, full_replay=True)
        self.assertEqual(cm_rep.exception.code, "REPLAY_MISMATCH")

        # Kill every independent_audit_payload branch individually
        def _tamper_indep(mutator: Any, expected_code: str) -> None:
            p = copy.deepcopy(cert["payload"])
            mutator(p)
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_in:
                aud.independent_audit_payload(p)
            self.assertEqual(cm_in.exception.code, expected_code)

        def _scale_minimax_both(p: dict[str, Any]) -> None:
            mc0 = p["theorem1_paper_reproduction"]["minimax_gap_cases"][0]
            mc0["mse_residual_reuse"] = orc.format_rational(Fraction(2) * orc.parse_exact_rational(mc0["mse_residual_reuse"]))
            mc0["mse_bayes_midpoint"] = orc.format_rational(Fraction(2) * orc.parse_exact_rational(mc0["mse_bayes_midpoint"]))

        _tamper_indep(lambda p: p["theorem1_paper_reproduction"]["flow_and_gauge_cases"][0].__setitem__("cayley_so2_gauge_exact", False), "AUDIT_T1_FLOW_GAUGE")
        _tamper_indep(lambda p: p["theorem1_paper_reproduction"]["flow_and_gauge_cases"][0].__setitem__("step2_nilpotent_exact", False), "AUDIT_T1_FLOW_GAUGE")
        _tamper_indep(_scale_minimax_both, "AUDIT_T1_MINIMAX_FAILED")
        _tamper_indep(lambda p: p["theorem1_paper_reproduction"]["minimax_gap_cases"][0].__setitem__("mse_bayes_midpoint", "99"), "AUDIT_T1_MINIMAX_FAILED")
        _tamper_indep(lambda p: p["theorem1_paper_reproduction"]["variance_matched_transport_cases"][0].__setitem__("mse_bayes", p["theorem1_paper_reproduction"]["variance_matched_transport_cases"][0]["mse_vm"]), "AUDIT_T1_VM_CHAIN")
        _tamper_indep(lambda p: p["theorem1_paper_reproduction"]["variance_matched_transport_cases"][0].__setitem__("mse_vm", p["theorem1_paper_reproduction"]["variance_matched_transport_cases"][0]["mse_rr"]), "AUDIT_T1_VM_GAIN")
        _tamper_indep(lambda p: p["theorem1_paper_reproduction"]["variance_matched_transport_cases"][2].__setitem__("mse_vm", "99"), "AUDIT_T1_VM_SYM")
        _tamper_indep(lambda p: p["theorem2_gauge_anisotropy"]["diagonal_anisotropy_cases"][0].__setitem__("sigma12_observed", "99"), "AUDIT_T2_SIGMA12")
        _tamper_indep(lambda p: p["theorem2_gauge_anisotropy"]["diagonal_anisotropy_cases"][0].__setitem__("cf_err_sq", "1"), "AUDIT_T2_CF_ZERO")
        _tamper_indep(lambda p: p["theorem2_gauge_anisotropy"]["general_psd_coordinate_free_cases"][0].__setitem__("commutator_identity_exact", False), "AUDIT_T2_GENERAL_PSD")
        _tamper_indep(lambda p: p["theorem2_gauge_anisotropy"]["general_psd_coordinate_free_cases"][0].__setitem__("recovered_theta_c", "99"), "AUDIT_T2_GENERAL_PSD")
        _tamper_indep(lambda p: p["theorem2_gauge_anisotropy"]["isotropic_negative_control"].__setitem__("recovery_rejected_cleanly", False), "AUDIT_T2_ISO_CONTROL")
        _tamper_indep(lambda p: p["theorem3_two_step_holonomy"]["two_step_isotropic_cases"][0].__setitem__("recovered_theta_c_norm_diff", "99"), "AUDIT_T3_NORM_DIFF")
        _tamper_indep(lambda p: p["theorem3_two_step_holonomy"]["two_step_isotropic_cases"][0].__setitem__("recovered_theta_c_universal", "99"), "AUDIT_T3_UNIVERSAL")
        _tamper_indep(lambda p: p["theorem3_two_step_holonomy"]["two_step_isotropic_cases"][0].__setitem__("cf_err_sq_extrapolation", "1"), "AUDIT_T3_EXTRAP_ZERO")
        _tamper_indep(lambda p: p["theorem3_two_step_holonomy"]["nonlinear_commutator_h6_scaling"]["rows"][0].__setitem__("two_step_err_sq_div_h6", "1"), "AUDIT_T3_H6_SCALING")
        _tamper_indep(lambda p: p["theorem3_two_step_holonomy"]["self_advection_dg_g_obstruction"].__setitem__("two_step_err_x2", "1"), "AUDIT_T3_SELF_ADVECTION")
        _tamper_indep(lambda p: p["theorem3_two_step_holonomy"]["self_advection_dg_g_obstruction"].__setitem__("three_step_exact_cancellation", False), "AUDIT_T3_SELF_ADVECTION")
        _tamper_indep(lambda p: p["theorem3_two_step_holonomy"]["curved_encoder_d2e_obstruction"].__setitem__("d2e_identity_exact", False), "AUDIT_T3_CURVED_ENCODER")
        _tamper_indep(lambda p: p["theorem4_multiplicative_steelman"]["pure_multiplicative_cases"][0].__setitem__("multiplicative_ratio_err", "1"), "AUDIT_T4_MULT")
        _tamper_indep(lambda p: p["theorem4_multiplicative_steelman"]["mixed_two_step_cases"][0].__setitem__("two_step_cf_err", "1"), "AUDIT_T4_MIXED")
        _tamper_indep(lambda p: p["theorem4_multiplicative_steelman"]["singular_a0_eq_a1_control"].__setitem__("inversion_rejected_cleanly", False), "AUDIT_T4_SINGULAR")


class TestZoneBHardeningAndCLI(unittest.TestCase):
    def test_zone_b_io_guards_symlinks_pwd_hardlink_fifo_and_caps(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            real_dir = root / "real"
            real_dir.mkdir()
            cert_path = real_dir / "cert.json"

            # Write and check clean certificate
            w_res = aud.write_certificate_file(cert_path)
            self.assertTrue(w_res["written"])
            c_res = aud.check_certificate_file(cert_path)
            self.assertTrue(c_res["valid"])
            self.assertEqual(w_res["file_sha256"], c_res["file_sha256"])

            # EvilPath & NUL byte rejected
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_ep:
                aud.require_safe_path(_EvilPath(str(cert_path)))
            self.assertEqual(cm_ep.exception.code, "INVALID_PATH_TYPE")
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_nul:
                aud.require_safe_path(Path("a\x00b"))
            self.assertEqual(cm_nul.exception.code, "INVALID_PATH")

            # require_safe_path standalone checks (root, dot, missing leaf, leaf symlink, missing parent)
            self.assertEqual(aud.require_safe_path(Path("/")), Path("/"))
            self.assertEqual(aud.require_safe_path(Path(".")), Path("."))
            self.assertEqual(aud.require_safe_path(real_dir / "nonexistent_leaf.json"), real_dir / "nonexistent_leaf.json")
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_miss_dir:
                aud.require_safe_path(root / "no_such_dir" / "leaf.json")
            self.assertEqual(cm_miss_dir.exception.code, "PATH_NOT_FOUND")

            # Direct symlink (read, write, & require_safe_path) & unnormalized sym/../real/cert.json rejected
            sym_file = root / "sym_cert.json"
            sym_file.symlink_to(cert_path)
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_rs:
                aud.require_safe_path(sym_file)
            self.assertEqual(cm_rs.exception.code, "SYMLINK_FORBIDDEN")
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_sf:
                aud.read_regular_file_bytes(sym_file)
            self.assertEqual(cm_sf.exception.code, "SYMLINK_FORBIDDEN")
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_swf:
                aud.write_regular_file_bytes(sym_file, b"nope")
            self.assertEqual(cm_swf.exception.code, "SYMLINK_FORBIDDEN")

            sym_dir = root / "sym_dir"
            sym_dir.symlink_to(real_dir)
            sneaky = Path(f"{sym_dir}/../real/cert.json")
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_sd:
                aud.read_regular_file_bytes(sneaky)
            self.assertEqual(cm_sd.exception.code, "SYMLINK_FORBIDDEN")

            # Root / dot / parent-dir targets rejected as NON_REGULAR_FILE
            for dir_target in (Path("/"), Path("."), Path("..")):
                with self.assertRaises(orc.CounterfactualHolonomyError) as cm_dt:
                    aud.read_regular_file_bytes(dir_target)
                self.assertEqual(cm_dt.exception.code, "NON_REGULAR_FILE")

            # Relative path with clean PWD vs symlinked PWD vs stale/empty/relative PWD + deleted-CWD (D2/S26-BUG-01)
            orig_cwd = os.getcwd()
            try:
                os.chdir(real_dir)
                with mock.patch.dict(os.environ, {"PWD": str(real_dir)}, clear=False):
                    self.assertEqual(aud.read_regular_file_bytes(Path("./cert.json")), cert_path.read_bytes())
                with mock.patch.dict(os.environ, {"PWD": str(root / "stale_gone_pwd")}, clear=False):
                    self.assertEqual(aud.read_regular_file_bytes(Path("cert.json")), cert_path.read_bytes())
                with mock.patch.dict(os.environ, {"PWD": ""}, clear=False):
                    self.assertEqual(aud.read_regular_file_bytes(Path("cert.json")), cert_path.read_bytes())
                with mock.patch.dict(os.environ, {"PWD": "relative/pwd"}, clear=False):
                    self.assertEqual(aud.read_regular_file_bytes(Path("cert.json")), cert_path.read_bytes())
                with mock.patch.dict(os.environ, {"PWD": str(sym_dir)}, clear=False):
                    with self.assertRaises(orc.CounterfactualHolonomyError) as cm_pwd:
                        aud.read_regular_file_bytes(Path("cert.json"))
                    self.assertEqual(cm_pwd.exception.code, "SYMLINK_FORBIDDEN")

                # Deleted-CWD regression (in-process + CLI --check / --write all return clean CWD_UNAVAILABLE, rc=2)
                doomed_dir = root / "doomed_cwd"
                doomed_dir.mkdir()
                os.chdir(doomed_dir)
                doomed_dir.rmdir()
                with self.assertRaises(orc.CounterfactualHolonomyError) as cm_dcwd:
                    aud.require_safe_path(Path("rel.json"))
                self.assertEqual(cm_dcwd.exception.code, "CWD_UNAVAILABLE")
                for cli_args in (["--check", "rel.json", "--json"], ["--write", "rel.json", "--json"]):
                    err_dcwd = io.StringIO()
                    with redirect_stderr(err_dcwd):
                        rc_dcwd = aud.main(cli_args)
                    self.assertEqual(rc_dcwd, 2)
                    self.assertEqual(json.loads(err_dcwd.getvalue())["error_code"], "CWD_UNAVAILABLE")
            finally:
                os.chdir(orig_cwd)

            # FIFO read & write refuse cleanly without blocking; directory read/write refused
            fifo = root / "pipe.fifo"
            os.mkfifo(fifo)
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_fr:
                aud.read_regular_file_bytes(fifo)
            self.assertEqual(cm_fr.exception.code, "NON_REGULAR_FILE")
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_fw:
                aud.write_regular_file_bytes(fifo, b"x")
            self.assertIn(cm_fw.exception.code, ("FILE_WRITE_ERROR", "NON_REGULAR_FILE"))

            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_dr:
                aud.read_regular_file_bytes(real_dir)
            self.assertEqual(cm_dr.exception.code, "NON_REGULAR_FILE")
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_dw:
                aud.write_regular_file_bytes(real_dir, b"x")
            self.assertEqual(cm_dw.exception.code, "FILE_WRITE_ERROR")

            # Hardlink refusal WITHOUT truncating the original file!
            hl_src = root / "hl_src.json"
            hl_src.write_bytes(b"PRESERVE_ME\n")
            hl_dst = root / "hl_dst.json"
            os.link(hl_src, hl_dst)
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_hl:
                aud.write_regular_file_bytes(hl_dst, b"CLOBBER\n")
            self.assertEqual(cm_hl.exception.code, "HARDLINK_FORBIDDEN")
            self.assertEqual(hl_src.read_bytes(), b"PRESERVE_ME\n")

            # Write non-bytes rejected; write non-regular (mocked fstat) rejected
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_nb:
                aud.write_regular_file_bytes(root / "nb.json", "not_bytes")  # type: ignore[arg-type]
            self.assertEqual(cm_nb.exception.code, "INVALID_WRITE_DATA")

            fake_stat = mock.Mock(st_mode=stat.S_IFCHR | 0o600, st_nlink=1)
            with mock.patch("os.fstat", return_value=fake_stat):
                with self.assertRaises(orc.CounterfactualHolonomyError) as cm_nrw:
                    aud.write_regular_file_bytes(root / "dev_mock.json", b"x")
                self.assertEqual(cm_nrw.exception.code, "NON_REGULAR_FILE")

            # Oversized file (> MAX_JSON_BYTES) refused on chunked read
            big_f = root / "big.json"
            big_f.write_bytes(b" " * (orc.MAX_JSON_BYTES + 1))
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_big:
                aud.read_regular_file_bytes(big_f)
            self.assertEqual(cm_big.exception.code, "FILE_TOO_LARGE")

            # Exact MAX_JSON_BYTES read succeeds at read_regular_file_bytes boundary
            exact_f = root / "exact.bin"
            exact_f.write_bytes(b"a" * orc.MAX_JSON_BYTES)
            self.assertEqual(len(aud.read_regular_file_bytes(exact_f)), orc.MAX_JSON_BYTES)

            # Missing file & unreadable chmod 000 file wrapped cleanly
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_miss:
                aud.read_regular_file_bytes(root / "nope.json")
            self.assertEqual(cm_miss.exception.code, "FILE_READ_ERROR")

            if os.geteuid() != 0:
                locked = root / "locked.json"
                locked.write_bytes(b"{}\n")
                locked.chmod(0)
                try:
                    with self.assertRaises(orc.CounterfactualHolonomyError) as cm_lk:
                        aud.read_regular_file_bytes(locked)
                    self.assertEqual(cm_lk.exception.code, "FILE_READ_ERROR")
                finally:
                    locked.chmod(0o644)

                # lstat OSError inside unreadable parent dir
                noexec_dir = root / "noexec"
                noexec_dir.mkdir()
                noexec_dir.chmod(0)
                try:
                    with self.assertRaises(orc.CounterfactualHolonomyError) as cm_ls:
                        aud.require_safe_path(noexec_dir / "child.json")
                    self.assertEqual(cm_ls.exception.code, "PATH_STAT_ERROR")
                finally:
                    noexec_dir.chmod(0o755)

            # Format checks in check_certificate_file: CRLF, missing LF, invalid UTF-8, non-canonical bytes
            raw_valid = cert_path.read_bytes()
            crlf_f = root / "crlf.json"
            crlf_f.write_bytes(raw_valid[:-1] + b"\r\n")
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_cr:
                aud.check_certificate_file(crlf_f)
            self.assertEqual(cm_cr.exception.code, "CRLF_FORBIDDEN")

            nolf_f = root / "nolf.json"
            nolf_f.write_bytes(raw_valid[:-1])
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_nl:
                aud.check_certificate_file(nolf_f)
            self.assertEqual(cm_nl.exception.code, "MISSING_TRAILING_LF")

            badu_f = root / "badutf8.json"
            badu_f.write_bytes(b"\xff\xfe\n")
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_bu:
                aud.check_certificate_file(badu_f)
            self.assertEqual(cm_bu.exception.code, "INVALID_UTF8")

            noncan_f = root / "noncan.json"
            noncan_f.write_bytes(b" " + raw_valid)
            with self.assertRaises(orc.CounterfactualHolonomyError) as cm_nc:
                aud.check_certificate_file(noncan_f)
            self.assertEqual(cm_nc.exception.code, "NON_CANONICAL_BYTES")

    def test_cli_modes_and_adversarial_argv(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cert_path = Path(td).resolve() / "out.json"

            # Default mode (standalone text) & --standalone --json
            out1 = io.StringIO()
            with redirect_stdout(out1):
                self.assertEqual(aud.main([]), 0)
            self.assertIn("OK ", out1.getvalue())

            out2 = io.StringIO()
            with redirect_stdout(out2):
                self.assertEqual(aud.main(["--standalone", "--json"]), 0)
            standalone_bytes = out2.getvalue().encode("ascii")

            # --write & --check --json byte-identical parity
            out3 = io.StringIO()
            with redirect_stdout(out3):
                self.assertEqual(aud.main(["--write", str(cert_path), "--json"]), 0)
            self.assertTrue(json.loads(out3.getvalue())["written"])
            self.assertEqual(cert_path.read_bytes(), standalone_bytes)

            out4 = io.StringIO()
            with redirect_stdout(out4):
                self.assertEqual(aud.main(["--check", str(cert_path), "--json"]), 0)
            chk = json.loads(out4.getvalue())
            self.assertTrue(chk["valid"])
            self.assertTrue(chk["independent_audit"]["independent_audit_passed"])

            # Adversarial CLI argv cases all fail closed with exit 2 and JSON error on stderr
            bad_argvs: list[tuple[Any, str]] = [
                ("not_a_list", "INVALID_ARGV"),
                ([123], "INVALID_STR"),
                ([_EvilStr("--standalone")], "INVALID_STR"),
                (["\ud800"], "INVALID_UTF8_SURROGATE"),
                (["--json", "--json"], "DUPLICATE_FLAG"),
                (["--standalone", "--standalone"], "CONFLICTING_MODE"),
                (["--standalone", "--check", str(cert_path)], "CONFLICTING_MODE"),
                (["--check"], "MISSING_PATH_ARG"),
                (["--write"], "MISSING_PATH_ARG"),
                (["--check", ""], "INVALID_PATH_ARG"),
                (["--check", "--json"], "INVALID_PATH_ARG"),
                (["--write", "--json"], "INVALID_PATH_ARG"),
                (["--bogus"], "UNKNOWN_FLAG"),
            ]
            for bad_argv, expected_code in bad_argvs:
                err_buf = io.StringIO()
                with redirect_stderr(err_buf):
                    rc = aud.main(bad_argv)
                self.assertEqual(rc, 2)
                err_obj = json.loads(err_buf.getvalue())
                self.assertFalse(err_obj["valid"])
                self.assertEqual(err_obj["error_code"], expected_code)


if __name__ == "__main__":
    unittest.main()
