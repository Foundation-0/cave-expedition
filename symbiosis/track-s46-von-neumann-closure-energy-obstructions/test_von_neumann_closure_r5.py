#!/usr/bin/env python3
"""Assertion-free R5 verification, mutation-killing & Zone-B adversarial test suite
for Track S46 (Portal 46: Von Neumann/Leontief Closure, Schur Vitamin Bottleneck,
Planetary Energy Hierarchy, Radiative Ceiling & Eigen Metrology Gate).

100% pure Python 3 stdlib unittest, zero bare asserts, zero AST floats, zero float(),
zero .isdigit(), zero islink, zero mathematical RNG.
"""
from __future__ import annotations

import ast
import copy
import ctypes
from fractions import Fraction
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import threading
import unittest
from unittest import mock

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import von_neumann_closure_audit as audit  # noqa: E402
import von_neumann_closure_oracle as oracle  # noqa: E402


def _resign_payload(payload: dict[str, object]) -> dict[str, object]:
    p_sha = audit._sha256_canonical(payload)
    outer = {
        "schema_version": oracle.SCHEMA_VERSION,
        "track_id": oracle.TRACK_ID,
        "payload_sha256": p_sha,
        "payload": payload,
    }
    c_sha = audit._sha256_canonical(outer)
    return {
        "schema_version": oracle.SCHEMA_VERSION,
        "track_id": oracle.TRACK_ID,
        "payload_sha256": p_sha,
        "certificate_sha256": c_sha,
        "payload": payload,
    }


def _call_main(argv: list[str]) -> tuple[int, str, str]:
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    with mock.patch.object(sys, "stdout", out_buf), mock.patch.object(sys, "stderr", err_buf):
        rc = audit.main(argv)
    return rc, out_buf.getvalue(), err_buf.getvalue()


class TestVonNeumannClosureR5(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cert = audit.build_standalone_certificate()
        cls.payload = cls.cert["payload"]

    def _expect_err(self, code: str, fn, *args, **kwargs) -> oracle.VonNeumannClosureError:
        with self.assertRaises(oracle.VonNeumannClosureError) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code)
        return ctx.exception

    # ------------------------------------------------------------------
    # 1. Static AST & Hygiene
    # ------------------------------------------------------------------
    def test_01_static_ast_hygiene(self) -> None:
        files = (
            _THIS_DIR / "von_neumann_closure_oracle.py",
            _THIS_DIR / "von_neumann_closure_audit.py",
            _THIS_DIR / "test_von_neumann_closure_r5.py",
        )
        for fp in files:
            src = fp.read_text(encoding="utf-8")
            self.assertNotIn("\r", src)
            tree = ast.parse(src, filename=str(fp))
            for node in ast.walk(tree):
                self.assertNotIsInstance(node, ast.Assert, f"bare assert in {fp.name}")
                if isinstance(node, ast.Constant):
                    self.assertIsNot(type(node.value), float, f"float literal in {fp.name}")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotEqual(node.func.id, "float", f"float() call in {fp.name}")
                if isinstance(node, ast.Attribute):
                    self.assertNotIn(node.attr, ("isdigit", "islink", "is_symlink"), f"forbidden attr in {fp.name}")

    # ------------------------------------------------------------------
    # 2. Strict Primitives, Bit Caps & Exact Formatters
    # ------------------------------------------------------------------
    def test_02_strict_primitives_and_formatters(self) -> None:
        oracle.require_ok(True, "OK", "ok")
        self._expect_err("BOOM", oracle.require_ok, False, "BOOM", "fail")
        self._expect_err("INVALID_CONDITION_TYPE", oracle.require_ok, 1, "X", "bad")
        self.assertIs(oracle.require_exact_bool(True), True)
        self.assertIs(oracle.require_exact_bool(False), False)
        self._expect_err("INVALID_BOOL_TYPE", oracle.require_exact_bool, 1)

        max_ok = (1 << oracle.MAX_INT_BITS) - 1
        self.assertEqual(oracle.require_exact_int(max_ok, "m", lo=0, hi=max_ok), max_ok)
        self.assertEqual(oracle.require_exact_int(0, "z", lo=0, hi=0), 0)
        self._expect_err("INVALID_INT_TYPE", oracle.require_exact_int, True)
        self._expect_err("INT_BIT_LIMIT", oracle.require_exact_int, 1 << oracle.MAX_INT_BITS)
        self._expect_err("INVALID_BOUND_TYPE", oracle.require_exact_int, 5, lo="0")
        self._expect_err("INVALID_BOUND_TYPE", oracle.require_exact_int, 5, hi="9")
        self._expect_err("INT_OUT_OF_RANGE", oracle.require_exact_int, -1, lo=0)
        self._expect_err("INT_OUT_OF_RANGE", oracle.require_exact_int, 10, hi=9)

        self.assertEqual(oracle.require_exact_fraction(Fraction(max_ok, 1)), Fraction(max_ok, 1))
        self.assertEqual(oracle.require_exact_fraction(Fraction(1, max_ok)), Fraction(1, max_ok))
        self._expect_err("INVALID_FRACTION_TYPE", oracle.require_exact_fraction, 3)
        self._expect_err("RATIONAL_BIT_LIMIT", oracle.require_exact_fraction, Fraction(1 << oracle.MAX_RATIONAL_BITS, 1))
        self._expect_err("RATIONAL_BIT_LIMIT", oracle.require_exact_fraction, Fraction(1, 1 << oracle.MAX_RATIONAL_BITS))

        self.assertEqual(oracle.format_rational(Fraction(5, 1)), "5")
        self.assertEqual(oracle.format_rational(Fraction(-3, 4)), "-3/4")
        self.assertEqual(oracle.format_decimal(Fraction(1, 200), 2), "0.01")
        self.assertEqual(oracle.format_decimal(Fraction(1, 201), 2), "0.00")
        self.assertEqual(oracle.format_decimal(Fraction(-1, 10000), 2), "0.00")
        self.assertEqual(oracle.format_decimal(Fraction(-7, 2), 0), "-4")
        self.assertEqual(oracle.format_decimal(Fraction(7, 2), 0), "4")
        self.assertEqual(oracle.format_decimal(Fraction(0), 0), "0")
        self._expect_err("INT_OUT_OF_RANGE", oracle.format_decimal, Fraction(1), -1)
        self._expect_err("INT_OUT_OF_RANGE", oracle.format_decimal, Fraction(1), 13)

        self.assertEqual(oracle.format_sci(Fraction(3880, 1), 4), "3.880e+03")
        self.assertEqual(oracle.format_sci(Fraction(99999, 10000), 4), "1.000e+01")
        self.assertEqual(oracle.format_sci(Fraction(1, 400), 4), "2.500e-03")
        self.assertEqual(oracle.format_sci(Fraction(1, 2), 2), "5.0e-01")
        self.assertEqual(oracle.format_sci(Fraction(9, 10), 4), "9.000e-01")
        self.assertEqual(oracle.format_sci(Fraction(10, 3), 4), "3.333e+00")
        self._expect_err("SCI_NONPOSITIVE", oracle.format_sci, Fraction(0))
        self._expect_err("SCI_NONPOSITIVE", oracle.format_sci, Fraction(-1))
        self._expect_err("INT_OUT_OF_RANGE", oracle.format_sci, Fraction(1), 1)
        self._expect_err("INT_OUT_OF_RANGE", oracle.format_sci, Fraction(1), 9)

    # ------------------------------------------------------------------
    # 3. Exact Q Linear Algebra & Eigen Recursion Guards
    # ------------------------------------------------------------------
    def test_03_linear_algebra_and_eigen_guards(self) -> None:
        self._expect_err("INVALID_MATRIX", oracle.require_square_q_matrix, "bad")
        self._expect_err("INVALID_MATRIX", oracle.require_square_q_matrix, [])
        self._expect_err("NON_SQUARE_MATRIX", oracle.require_square_q_matrix, ["a"])
        self._expect_err("NON_SQUARE_MATRIX", oracle.require_square_q_matrix, [[Fraction(1), Fraction(2)]])
        self._expect_err("INVALID_FRACTION_TYPE", oracle.require_square_q_matrix, [[1]])

        m1 = [[Fraction(1)]]
        m2 = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
        self._expect_err("DIM_MISMATCH", oracle.mat_mul_q, m1, m2)
        self.assertEqual(oracle.mat_mul_q(m2, m2), [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]])

        self._expect_err("VEC_DIM_MISMATCH", oracle.mat_vec_q, m2, "ab")
        self._expect_err("VEC_DIM_MISMATCH", oracle.mat_vec_q, m2, [Fraction(1)])
        self.assertEqual(oracle.mat_vec_q(m2, [Fraction(2), Fraction(3)]), [Fraction(3), Fraction(2)])

        det_swap, inv_swap = oracle.exact_det_and_inv_q(m2)
        self.assertEqual(det_swap, Fraction(-1))
        self.assertEqual(inv_swap, m2)
        self._expect_err("SINGULAR_MATRIX", oracle.exact_det_and_inv_q, [[Fraction(1), Fraction(1)], [Fraction(1), Fraction(1)]])

        self._expect_err("NEGATIVE_MATRIX_ENTRY", oracle.check_collatz_wielandt_bounds, [[Fraction(-1)]], [Fraction(1)])
        self._expect_err("NONPOSITIVE_WITNESS", oracle.check_collatz_wielandt_bounds, [[Fraction(1)]], [Fraction(0)])
        self.assertEqual(oracle.check_collatz_wielandt_bounds(m2, [Fraction(1), Fraction(1)]), (Fraction(1), Fraction(1)))

        self._expect_err("INVALID_P0", oracle.step_eigen_quasispecies, Fraction(0), Fraction(1, 2), 2, Fraction(2), 3)
        self._expect_err("INVALID_P0", oracle.step_eigen_quasispecies, Fraction(1), Fraction(1, 2), 2, Fraction(2), 3)
        self._expect_err("INVALID_Q_FIDELITY", oracle.step_eigen_quasispecies, Fraction(1, 2), Fraction(0), 2, Fraction(2), 3)
        self._expect_err("INVALID_Q_FIDELITY", oracle.step_eigen_quasispecies, Fraction(1, 2), Fraction(1), 2, Fraction(2), 3)
        self._expect_err("INVALID_SIGMA", oracle.step_eigen_quasispecies, Fraction(1, 2), Fraction(1, 2), 2, Fraction(1, 2), 3)

    # ------------------------------------------------------------------
    # 4. Exact Four-Pillar Mathematical Payload Checks
    # ------------------------------------------------------------------
    def test_04_four_pillars_exact_values(self) -> None:
        pl = self.payload
        self.assertEqual(pl["track_id"], oracle.TRACK_ID)
        self.assertEqual(pl["portal_ref"], "Portal 46")
        self.assertEqual(pl["novelty_class"], "N1")

        p1 = pl["pillar1_mars_energy_hierarchy"]
        self.assertTrue(p1["all_verified"])
        self.assertEqual(p1["m_atm_over_current_lo_dec6"], "155.200566")
        self.assertEqual(p1["nuc_1MeV_over_u_grav_lo_dec6"], "76.947702")
        self.assertEqual(p1["nuc_8MeV_over_u_grav_lo_dec6"], "615.581618")

        p2 = pl["pillar2_leontief_hawkins_simon"]
        self.assertTrue(p2["all_verified"])
        self.assertEqual(p2["productive_closure"]["det_I_minus_A_q"], "83377/160000")
        self.assertEqual(p2["productive_closure"]["balanced_growth_surplus_lb_q"], "2/3")
        self.assertEqual(p2["deficit_negative_control"]["det_I_minus_A_q"], "-22857/160000")
        self.assertEqual(p2["deficit_negative_control"]["collatz_wielandt_rho_bounds_q"], ["23/20", "23/20"])

        p3 = pl["pillar3_schur_vitamin_bottleneck"]
        self.assertTrue(p3["all_verified"])
        self.assertEqual(p3["unclosed_vitamin_blocked"]["schur_complement_S_VV_q"], "-331139/833770")
        self.assertEqual(p3["unclosed_vitamin_blocked"]["det_I_minus_A5_q"], "-331139/1600000")
        self.assertEqual(p3["design_for_closure_restored"]["schur_complement_S_VV_q"], "138867/166754")
        self.assertEqual(p3["design_for_closure_restored"]["det_I_minus_A5_q"], "138867/320000")

        p4 = pl["pillar4_radiative_and_eigen"]
        self.assertTrue(p4["all_verified"])
        self.assertEqual(p4["radiative_ceiling"]["r_crit_m_enclosure_dec6"], ["3.919363", "3.919363"])
        self.assertEqual([c["compact_cooling_feasible"] for c in p4["radiative_ceiling"]["cases"]], [True, False, False, False])
        self.assertEqual([c["expected_regime"] for c in p4["eigen_metrology_threshold"]["cases"]], ["increasing", "decreasing", "decreasing", "stationary"])

    # ------------------------------------------------------------------
    # 5. Strict Parsers, Binding 3,321-Bit Cap & Canonical JSON
    # ------------------------------------------------------------------
    def test_05_parsers_binding_bit_cap_and_canonical_json(self) -> None:
        self.assertEqual(audit.require_hex64_lower_ascii("a" * 64), "a" * 64)
        self._expect_err("INVALID_HEX64", audit.require_hex64_lower_ascii, "a" * 63)
        self._expect_err("INVALID_HEX64", audit.require_hex64_lower_ascii, "A" * 64)
        self._expect_err("INVALID_HEX64", audit.require_hex64_lower_ascii, "g" * 64)
        self._expect_err("INVALID_STR", audit.require_hex64_lower_ascii, 123)

        self.assertEqual(audit.parse_exact_rational("0"), Fraction(0))
        self.assertEqual(audit.parse_exact_rational("-5"), Fraction(-5))
        self.assertEqual(audit.parse_exact_rational("-7/11"), Fraction(-7, 11))
        for bad in ("-0", "01", "", "-", "1/0", "1/1", "2/4", "1/2/3", "\u0661", "1/02", "9" * 1001):
            with self.assertRaises(oracle.VonNeumannClosureError):
                audit.parse_exact_rational(bad)

        max_ok = (1 << oracle.MAX_INT_BITS) - 1
        self.assertEqual(len(str(max_ok)), oracle.MAX_INT_DIGITS)
        rt = audit.parse_strict_json_text(f'{{"x":{max_ok}}}')
        self.assertEqual(rt["x"], max_ok)
        self.assertEqual(audit.canonical_json_bytes(rt), f'{{"x":{max_ok}}}'.encode("ascii"))

        # Binding 3,321-bit cap rejects 10**1000 - 1 (1,000 digits, 3,322 bits) with INT_BIT_LIMIT
        self._expect_err("INT_BIT_LIMIT", audit._parse_bounded_int, "9" * 1000)
        self._expect_err("INT_BIT_LIMIT", audit.canonical_json_bytes, {"x": 1 << oracle.MAX_INT_BITS})
        self._expect_err("INT_BIT_LIMIT", audit.parse_strict_json_text, f'{{"x":{1 << oracle.MAX_INT_BITS}}}')
        self._expect_err("INT_DIGIT_LIMIT", audit.parse_strict_json_text, '{"x":1' + "0" * 4300 + "}")
        self._expect_err("FLOAT_LITERAL_FORBIDDEN", audit.parse_strict_json_text, '{"x":1.5}')
        self._expect_err("FLOAT_LITERAL_FORBIDDEN", audit.parse_strict_json_text, '{"x":1e2}')
        self._expect_err("NONFINITE_LITERAL_FORBIDDEN", audit.parse_strict_json_text, '{"x":NaN}')
        self._expect_err("DUPLICATE_JSON_KEY", audit.parse_strict_json_text, '{"a":1,"a":2}')
        self._expect_err("JSON_PARSE_ERROR", audit.parse_strict_json_text, '{"a":')
        self._expect_err("JSON_ROOT_NOT_OBJECT", audit.parse_strict_json_text, "[1,2]")
        self.assertEqual(audit.parse_strict_json_text("[1,null,true,false]", require_object=False), [1, None, True, False])
        self.assertEqual(audit.parse_strict_json_text('{"a":1}', max_bytes=7), {"a": 1})
        self._expect_err("JSON_TOO_LARGE", audit.parse_strict_json_text, '{"a":"0123456789"}', max_bytes=10)
        self._expect_err("INT_OUT_OF_RANGE", audit.parse_strict_json_text, "{}", max_bytes=1 << 100)
        self._expect_err("NUL_BYTE_FORBIDDEN", audit.parse_strict_json_text, '{"a":"\x00"}')
        self._expect_err("INVALID_UTF8_SURROGATE", audit.parse_strict_json_text, '{"a":"\ud800"}')
        self._expect_err("FORBIDDEN_JSON_TYPE", audit.canonical_json_bytes, {"a": {1, 2}})

        d64 = "[" * 64 + "0" + "]" * 64
        d65 = "[" * 65 + "0" + "]" * 65
        self.assertIsInstance(audit.parse_strict_json_text(d64, require_object=False), list)
        self._expect_err("JSON_DEPTH_LIMIT", audit.parse_strict_json_text, d65, require_object=False)
        self.assertEqual(audit.canonical_json_bytes({"b": "\u00e9", "a": 1}), b'{"a":1,"b":"\\u00e9"}')

    # ------------------------------------------------------------------
    # 6. Deep Secondary Auditor & 42 Re-Signed full_replay=False Tamper Kills
    # ------------------------------------------------------------------
    def test_06_secondary_audit_and_resigned_tamper_matrix(self) -> None:
        self.assertTrue(audit.verify_certificate_dict(self.cert, full_replay=True)["valid"])
        self.assertTrue(audit.verify_certificate_dict(self.cert, full_replay=False)["valid"])
        self._expect_err("INVALID_BOOL_TYPE", audit.verify_certificate_dict, self.cert, full_replay=1)

        # Envelope tampers
        self._expect_err("INVALID_CERT_TYPE", audit.verify_certificate_dict, [])
        c_extra = copy.deepcopy(self.cert)
        c_extra["rogue"] = 1
        self._expect_err("INVALID_CERT_KEYS", audit.verify_certificate_dict, c_extra, full_replay=False)
        c_sch = copy.deepcopy(self.cert)
        c_sch["schema_version"] = "bad"
        self._expect_err("INVALID_SCHEMA", audit.verify_certificate_dict, c_sch, full_replay=False)
        c_tid = copy.deepcopy(self.cert)
        c_tid["track_id"] = "bad"
        self._expect_err("INVALID_TRACK_ID", audit.verify_certificate_dict, c_tid, full_replay=False)
        c_pt = copy.deepcopy(self.cert)
        c_pt["payload"] = []
        self._expect_err("INVALID_PAYLOAD_TYPE", audit.verify_certificate_dict, c_pt, full_replay=False)
        c_psha = copy.deepcopy(self.cert)
        c_psha["payload_sha256"] = "0" * 64
        self._expect_err("PAYLOAD_SHA256_MISMATCH", audit.verify_certificate_dict, c_psha, full_replay=False)
        c_csha = copy.deepcopy(self.cert)
        c_csha["certificate_sha256"] = "0" * 64
        self._expect_err("CERT_SHA256_MISMATCH", audit.verify_certificate_dict, c_csha, full_replay=False)

        self._expect_err("INVALID_SCHEMA_DICT", audit._req_dict, [], "row", frozenset())

        def mutate_and_expect(mutator, exp_code: str) -> None:
            pl = copy.deepcopy(self.payload)
            mutator(pl)
            resigned = _resign_payload(pl)
            self._expect_err(exp_code, audit.verify_certificate_dict, resigned, full_replay=False)

        # 42 re-signed full_replay=False tampers across ALL 4 pillars, nested keys, types & shadow values
        tampers = [
            (lambda p: p.__setitem__("track_id", "WRONG"), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p.__setitem__("portal_ref", "Portal 99"), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p.__setitem__("novelty_class", "N0"), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p.__setitem__("prior_literature_n0", ["forged"]), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p.__setitem__("extra_top", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar1_mars_energy_hierarchy"].__setitem__("extra_p1", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar1_mars_energy_hierarchy"]["inequality_checks"].__setitem__("extra_chk", True), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar1_mars_energy_hierarchy"]["inequality_checks"].__setitem__("nuclear_1MeV_exceeds_70x_u_grav", 1), "INVALID_BOOL_TYPE"),
            (lambda p: p["pillar1_mars_energy_hierarchy"]["inequality_checks"].__setitem__("nuclear_1MeV_exceeds_70x_u_grav", False), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar1_mars_energy_hierarchy"].__setitem__("pi_enclosure_q", ["3", "4"]), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar1_mars_energy_hierarchy"].__setitem__("pi_enclosure_q", {"a": 1, "b": 2}), "INVALID_SCHEMA_LIST"),
            (lambda p: p["pillar1_mars_energy_hierarchy"].__setitem__("pi_enclosure_q", ["3"]), "INVALID_SCHEMA_LIST"),
            (lambda p: p["pillar1_mars_energy_hierarchy"].__setitem__("u_grav_mars_J_sci", "9.999e+30"), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar2_leontief_hawkins_simon"].__setitem__("extra_p2", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar2_leontief_hawkins_simon"]["productive_closure"].__setitem__("extra_g", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar2_leontief_hawkins_simon"]["deficit_negative_control"].__setitem__("extra_b", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar2_leontief_hawkins_simon"]["productive_closure"].__setitem__("det_I_minus_A_q", "1/2"), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar2_leontief_hawkins_simon"]["productive_closure"].__setitem__("rho_strictly_lt_1", 1), "INVALID_BOOL_TYPE"),
            (lambda p: p["pillar2_leontief_hawkins_simon"]["productive_closure"]["matrix_q"][0].__setitem__(0, "1/5"), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar2_leontief_hawkins_simon"]["deficit_negative_control"].__setitem__("det_I_minus_A_q", "1/2"), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar3_schur_vitamin_bottleneck"].__setitem__("extra_p3", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar3_schur_vitamin_bottleneck"]["unclosed_vitamin_blocked"].__setitem__("extra_vb", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar3_schur_vitamin_bottleneck"]["design_for_closure_restored"].__setitem__("extra_vr", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar3_schur_vitamin_bottleneck"]["unclosed_vitamin_blocked"].__setitem__("schur_complement_S_VV_q", "1/2"), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar3_schur_vitamin_bottleneck"]["design_for_closure_restored"].__setitem__("schur_complement_S_VV_q", "-1/2"), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar3_schur_vitamin_bottleneck"]["design_for_closure_restored"].__setitem__("rho_strictly_lt_1", 1), "INVALID_BOOL_TYPE"),
            (lambda p: p["pillar4_radiative_and_eigen"].__setitem__("extra_p4", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar4_radiative_and_eigen"]["radiative_ceiling"].__setitem__("extra_rad", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar4_radiative_and_eigen"]["radiative_ceiling"]["cases"][0].__setitem__("extra_rr", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar4_radiative_and_eigen"]["radiative_ceiling"]["cases"][0].__setitem__("swarm_unit_count_k3", 99), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar4_radiative_and_eigen"]["radiative_ceiling"]["cases"][0].__setitem__("swarm_split_k", True), "INVALID_INT_TYPE"),
            (lambda p: p["pillar4_radiative_and_eigen"]["radiative_ceiling"].__setitem__("temperature_K", 500), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar4_radiative_and_eigen"]["radiative_ceiling"].__setitem__("r_crit_m_enclosure_dec6", ["1.000000", "1.000000"]), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar4_radiative_and_eigen"]["eigen_metrology_threshold"].__setitem__("extra_eig", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar4_radiative_and_eigen"]["eigen_metrology_threshold"]["cases"][0].__setitem__("extra_er", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["pillar4_radiative_and_eigen"]["eigen_metrology_threshold"]["cases"][0].__setitem__("verified", False), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["pillar4_radiative_and_eigen"]["eigen_metrology_threshold"]["cases"][0].__setitem__("length_L", True), "INVALID_INT_TYPE"),
            (lambda p: p["pillar4_radiative_and_eigen"]["eigen_metrology_threshold"]["cases"][0].__setitem__("p_final_dec6", "0.500000"), "SECONDARY_AUDIT_FAILED"),
            (lambda p: p["summary"].__setitem__("extra_s", 1), "INVALID_SCHEMA_KEYS"),
            (lambda p: p["summary"].__setitem__("pillar_count", True), "INVALID_INT_TYPE"),
            (lambda p: p["summary"].__setitem__("all_four_pillars_verified", 1), "INVALID_BOOL_TYPE"),
            (lambda p: p["summary"].__setitem__("float_count_on_trust_path", 1), "SECONDARY_AUDIT_FAILED"),
        ]
        self.assertGreaterEqual(len(tampers), 40)
        for mutator, exp_code in tampers:
            mutate_and_expect(mutator, exp_code)

        # Replay digest mismatch guard independently verified
        with mock.patch.object(audit, "build_standalone_certificate", return_value={"payload_sha256": "0" * 64}):
            self._expect_err("REPLAY_MISMATCH", audit.verify_certificate_dict, self.cert, full_replay=True)

    # ------------------------------------------------------------------
    # 7. Zone-B File I/O, Symlink/PWD/Hardlink/FIFO, Streaming Cap & CLI
    # ------------------------------------------------------------------
    def test_07_zone_b_io_and_cli(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            cert_path = root / "sub" / "cert.json"
            wres = audit.write_certificate_file(cert_path)
            self.assertTrue(wres["written"])
            self.assertEqual(stat.S_IMODE(os.lstat(cert_path).st_mode), 0o600)
            cres = audit.check_certificate_file(cert_path, full_replay=True)
            self.assertTrue(cres["valid"])
            self.assertEqual(cres["file_sha256"], wres["file_sha256"])

            missing_dir = root / "never_created"
            self._expect_err("FILE_READ_ERROR", audit.read_regular_bytes_capped, missing_dir / "x.json")
            self.assertFalse(missing_dir.exists())

            crlf_p = root / "crlf.json"
            crlf_p.write_bytes(cert_path.read_bytes().replace(b"\n", b"\r\n"))
            self._expect_err("CRLF_FORBIDDEN", audit.check_certificate_file, crlf_p)

            nolf_p = root / "nolf.json"
            nolf_p.write_bytes(cert_path.read_bytes()[:-1])
            self._expect_err("MISSING_TRAILING_LF", audit.check_certificate_file, nolf_p)

            badu_p = root / "badu.json"
            badu_p.write_bytes(b"\xff\xfe\n")
            self._expect_err("INVALID_UTF8", audit.check_certificate_file, badu_p)

            pretty_p = root / "pretty.json"
            pretty_p.write_bytes((json.dumps(self.cert, indent=2) + "\n").encode("utf-8"))
            self._expect_err("NON_CANONICAL_BYTES", audit.check_certificate_file, pretty_p)

            sym_leaf = root / "sym_leaf.json"
            os.symlink(cert_path, sym_leaf)
            self._expect_err("SYMLINK_FORBIDDEN", audit.read_regular_bytes_capped, sym_leaf)
            self._expect_err("SYMLINK_FORBIDDEN", audit.write_regular_bytes_safe, sym_leaf, b"x")

            sym_dir = root / "sym_dir"
            os.symlink(root / "sub", sym_dir)
            self._expect_err("SYMLINK_FORBIDDEN", audit.read_regular_bytes_capped, sym_dir / "cert.json")
            self._expect_err("SYMLINK_FORBIDDEN", audit.write_regular_bytes_safe, sym_dir / "new.json", b"x")

            self._expect_err("NOT_A_REGULAR_FILE", audit.read_regular_bytes_capped, root / "sub")
            self._expect_err("NOT_A_REGULAR_FILE", audit.write_regular_bytes_safe, root / "sub", b"x")
            self._expect_err("NOT_A_REGULAR_FILE", audit.read_regular_bytes_capped, Path("/"))
            self._expect_err("NOT_A_REGULAR_FILE", audit.read_regular_bytes_capped, missing_dir / "..")
            self._expect_err("NOT_A_REGULAR_FILE", audit.read_regular_bytes_capped, Path("/dev/null"))

            fifo_p = root / "pipe.fifo"
            os.mkfifo(fifo_p)
            self._expect_err("NOT_A_REGULAR_FILE", audit.read_regular_bytes_capped, fifo_p)

            hl_p = root / "hardlink.json"
            os.link(cert_path, hl_p)
            self._expect_err("HARDLINK_FORBIDDEN", audit.write_regular_bytes_safe, hl_p, b"x")
            os.unlink(hl_p)

            big_p = root / "big70k.bin"
            big_p.write_bytes(b"A" * 70_000)
            self.assertEqual(len(audit.read_regular_bytes_capped(big_p, "exact", 70_000)), 70_000)
            self._expect_err("FILE_TOO_LARGE", audit.read_regular_bytes_capped, big_p, "big", 65_536)
            if Path("/proc/kallsyms").exists():
                self._expect_err("FILE_TOO_LARGE", audit.read_regular_bytes_capped, Path("/proc/kallsyms"), "ks", 1024)

            fake_st = os.stat_result((stat.S_IFREG | 0o600, 1, 1, 2, 0, 0, 1, 0, 0, 0))
            with mock.patch.object(os, "fstat", return_value=fake_st):
                self._expect_err("HARDLINK_FORBIDDEN", audit.write_regular_bytes_safe, root / "race_nlink.bin", b"x")

            self._expect_err("INVALID_PATH_TYPE", audit.read_regular_bytes_capped, str(cert_path))  # type: ignore[arg-type]
            self._expect_err("INVALID_PAYLOAD_BYTES", audit.write_regular_bytes_safe, root / "t.bin", "str")  # type: ignore[arg-type]

            orig_cwd = os.getcwd()
            orig_pwd = os.environ.get("PWD")
            try:
                os.chdir(root)
                os.environ["PWD"] = str(root)
                rel_p = Path("rel_out.json")
                audit.write_regular_bytes_safe(rel_p, b"{}\n")
                self.assertEqual(audit.read_regular_bytes_capped(rel_p), b"{}\n")

                os.environ["PWD"] = str(sym_dir)
                self._expect_err("SYMLINK_ANCESTOR_FORBIDDEN", audit.read_regular_bytes_capped, Path("rel_out.json"))

                ghost = root / "ghost_dir"
                ghost.mkdir()
                os.chdir(ghost)
                os.environ["PWD"] = str(ghost)
                ghost.rmdir()
                self._expect_err("CWD_UNAVAILABLE", audit.read_regular_bytes_capped, Path("rel.json"))
            finally:
                os.chdir(orig_cwd)
                if orig_pwd is None:
                    os.environ.pop("PWD", None)
                else:
                    os.environ["PWD"] = orig_pwd

            rc, out, err = _call_main([])
            self.assertEqual((rc, err), (0, ""))
            self.assertIn("OK ", out)

            rc, out, err = _call_main(["--standalone", "--json"])
            self.assertEqual((rc, err), (0, ""))
            self.assertEqual(json.loads(out)["certificate_sha256"], self.cert["certificate_sha256"])

            cli_w = root / "cli_w.json"
            rc, out, err = _call_main(["--write", str(cli_w), "--json"])
            self.assertEqual((rc, err), (0, ""))
            self.assertTrue(json.loads(out)["written"])

            rc, out, err = _call_main(["--check", str(cli_w), "--json"])
            self.assertEqual((rc, err), (0, ""))
            self.assertTrue(json.loads(out)["valid"])

            cli_w2 = root / "cli_w2.json"
            rc, out, err = _call_main([f"--write={cli_w2}"])
            self.assertEqual((rc, err), (0, ""))
            rc, out, err = _call_main([f"--check={cli_w2}", "--json"])
            self.assertEqual((rc, err), (0, ""))
            self.assertTrue(json.loads(out)["valid"])

            for bad_argv, exp_code in (
                (["--unknown"], "UNKNOWN_FLAG"),
                (["--json", "--json"], "DUPLICATE_FLAG"),
                (["--standalone", "--check", str(cli_w)], "CONFLICTING_MODE"),
                (["--check", str(cli_w), "--standalone"], "CONFLICTING_MODE"),
                (["--standalone", f"--check={cli_w}"], "CONFLICTING_MODE"),
                (["--check"], "MISSING_PATH_ARG"),
                (["--check", ""], "INVALID_PATH_ARG"),
                (["--check", "-bad"], "INVALID_PATH_ARG"),
                (["--check="], "INVALID_PATH_ARG"),
                (["--write=-bad"], "INVALID_PATH_ARG"),
                (["--check", "a\x00b"], "NUL_BYTE_FORBIDDEN"),
            ):
                rc, _o, e = _call_main(bad_argv)
                self.assertEqual(rc, 2)
                self.assertEqual(json.loads(e)["error_code"], exp_code)

            rc, _o, e = _call_main("not-a-list")  # type: ignore[arg-type]
            self.assertEqual(rc, 2)
            self.assertEqual(json.loads(e)["error_code"], "INVALID_ARGV")

    # ------------------------------------------------------------------
    # 8. Concurrency & Kernel Races (16T/80T + 550 renameat2 + 550 hardlink)
    # ------------------------------------------------------------------
    def test_08_concurrency_and_kernel_races(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()

            errs: list[Exception] = []
            def w_distinct(idx: int) -> None:
                try:
                    p = root / f"d_{idx}.bin"
                    audit.write_regular_bytes_safe(p, f"payload-{idx}\n".encode("ascii"))
                    if stat.S_IMODE(os.lstat(p).st_mode) != 0o600:
                        raise RuntimeError("bad mode")
                except Exception as exc:
                    errs.append(exc)

            ts = [threading.Thread(target=w_distinct, args=(i,)) for i in range(16)]
            for t in ts:
                t.start()
            for t in ts:
                t.join()
            self.assertEqual(errs, [])

            shared = root / "shared.bin"
            def w_same(idx: int) -> None:
                try:
                    audit.write_regular_bytes_safe(shared, f"v-{idx}\n".encode("ascii"))
                except Exception as exc:
                    errs.append(exc)

            for count in (16, 80):
                ts = [threading.Thread(target=w_same, args=(i,)) for i in range(count)]
                for t in ts:
                    t.start()
                for t in ts:
                    t.join()
            self.assertEqual(errs, [])
            self.assertEqual([p.name for p in root.iterdir() if p.name.endswith(".tmp")], [])

            libc = ctypes.CDLL("libc.so.6", use_errno=True)
            sys_renameat2 = 316
            rename_exchange = 2
            at_fdcwd = -100
            victim_dir = root / "victim_outside"
            victim_dir.mkdir()
            real_sub = root / "race_slot_a"
            real_sub.mkdir()
            sym_sub = root / "race_slot_b"
            os.symlink(victim_dir, sym_sub)

            stop_flag = threading.Event()
            b_a = os.fsencode(str(real_sub))
            b_b = os.fsencode(str(sym_sub))

            def flipper() -> None:
                while not stop_flag.is_set():
                    libc.syscall(sys_renameat2, at_fdcwd, b_a, at_fdcwd, b_b, rename_exchange)

            fl = threading.Thread(target=flipper)
            fl.start()
            try:
                for i in range(550):
                    try:
                        audit.write_regular_bytes_safe(real_sub / "x.bin", f"{i}\n".encode("ascii"))
                    except oracle.VonNeumannClosureError:
                        pass
            finally:
                stop_flag.set()
                fl.join()
            self.assertEqual(list(victim_dir.iterdir()), [])

            hl_dir = root / "hl_race"
            hl_dir.mkdir()
            hl_target = hl_dir / "target.bin"
            hl_victim = hl_dir / "victim.bin"
            hl_victim.write_bytes(b"ORIGINAL_VICTIM\n")

            stop_hl = threading.Event()
            def hl_attacker() -> None:
                while not stop_hl.is_set():
                    try:
                        os.unlink(hl_target)
                    except OSError:
                        pass
                    try:
                        os.link(hl_victim, hl_target)
                    except OSError:
                        pass

            ha = threading.Thread(target=hl_attacker)
            ha.start()
            try:
                for i in range(550):
                    try:
                        audit.write_regular_bytes_safe(hl_target, f"safe-{i}\n".encode("ascii"))
                    except oracle.VonNeumannClosureError:
                        pass
            finally:
                stop_hl.set()
                ha.join()
            self.assertEqual(hl_victim.read_bytes(), b"ORIGINAL_VICTIM\n")


if __name__ == "__main__":
    unittest.main()
