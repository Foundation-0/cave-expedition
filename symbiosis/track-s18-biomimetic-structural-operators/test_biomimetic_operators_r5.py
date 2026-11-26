#!/usr/bin/env python3
"""
AUDIT-117 Assertion-Free R5 Unit & Mutation-Isolation Test Suite (`test_biomimetic_operators_r5.py`).

Zero bare `assert` statements (100% `python3 -O` parity). Covers:
  - All 5 exact-Q / Q[sqrt(2), sqrt(3)] biomimetic structural operators & cross-checks
  - All must-fail negative controls, boundary attacks, and adversarial JSON/CLI inputs
  - 100.0% refusal-site & BoolOp mutation isolation across oracle + audit CLI
"""
from __future__ import annotations

from collections.abc import Sequence
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

import biomimetic_operators_audit as audit
import biomimetic_operators_oracle as oracle


class _LyingSequence(Sequence):
    """Adversarial Sequence subclass whose __len__ lies relative to __iter__."""

    def __init__(self, items: list[int]) -> None:
        self._items = items

    def __len__(self) -> int:
        return 2

    def __getitem__(self, idx: int) -> int:
        return self._items[idx]

    def __iter__(self):
        return iter(self._items)


class TestHardeningAndCoreAlgebra(unittest.TestCase):
    def test_primitive_validators_and_boundaries(self) -> None:
        self.assertEqual(oracle.require_int(5, "x"), 5)
        self.assertEqual(oracle.require_int(2, "x", lo=2, hi=5), 2)
        self.assertEqual(oracle.require_int(5, "x", lo=2, hi=5), 5)
        for bad in (True, False, 1.0, "1", None):
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                oracle.require_int(bad, "x")
            self.assertEqual(cm.exception.code, "INVALID_INT_TYPE")
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.require_int(1, "x", lo=2, hi=5)
        self.assertEqual(cm.exception.code, "INT_BELOW_MIN")
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.require_int(6, "x", lo=2, hi=5)
        self.assertEqual(cm.exception.code, "INT_ABOVE_MAX")

        self.assertEqual(oracle.require_rat(3, "q"), Fraction(3, 1))
        self.assertEqual(oracle.require_rat(Fraction(-2, 3), "q"), Fraction(-2, 3))
        for bad in (True, False, 1.5, "1/2", None):
            with self.assertRaises(oracle.BiomimeticOpError):
                oracle.require_rat(bad, "q")
        self.assertEqual(oracle.require_pos_rat(Fraction(1, 7), "p"), Fraction(1, 7))
        for nonpos in (0, -1, Fraction(0, 1), Fraction(-1, 5)):
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                oracle.require_pos_rat(nonpos, "p")
            self.assertEqual(cm.exception.code, "NON_POSITIVE_RATIONAL")

        self.assertEqual(oracle.require_seq([1], "s", min_len=1, max_len=2), (1,))
        self.assertEqual(oracle.require_seq((1, 2), "s", min_len=1, max_len=2), (1, 2))
        for bad_seq in (_LyingSequence([1, 2, 3]), "abc", {1: 2}, None):
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                oracle.require_seq(bad_seq, "s", min_len=1, max_len=3)
            self.assertEqual(cm.exception.code, "INVALID_SEQ_TYPE")
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.require_seq([], "s", min_len=1, max_len=2)
        self.assertEqual(cm.exception.code, "SEQ_TOO_SHORT")
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.require_seq([1, 2, 3], "s", min_len=1, max_len=2)
        self.assertEqual(cm.exception.code, "SEQ_TOO_LONG")

        self.assertEqual(oracle.fmt_q(Fraction(4, 2)), "2")
        self.assertEqual(oracle.fmt_q(Fraction(-3, 5)), "-3/5")

    def test_strict_json_iterative_depth_digit_and_type_guards(self) -> None:
        # Exact boundaries pass
        exact_depth: object = 0
        for _ in range(oracle.MAX_JSON_DEPTH):
            exact_depth = [exact_depth]
        oracle.validate_json_value(exact_depth)
        self.assertEqual(oracle.canonical_json_bytes({"b": True, "a": None, "c": "x", "d": 0}), b'{"a":null,"b":true,"c":"x","d":0}')
        oracle.validate_json_value({"big": oracle.MAX_JSON_INT, "neg": -oracle.MAX_JSON_INT})

        # Exceeding depth cap (including extreme 1500 nesting without RecursionError!)
        over_depth = [exact_depth]
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.validate_json_value(over_depth)
        self.assertEqual(cm.exception.code, "MAX_DEPTH_EXCEEDED")

        deep_py: object = 1
        for _ in range(1500):
            deep_py = [deep_py]
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.canonical_json_bytes(deep_py)
        self.assertEqual(cm.exception.code, "MAX_DEPTH_EXCEEDED")

        # Deep raw JSON text (rejected cleanly without uncaught RecursionError)
        deep_txt = "[" * 1500 + "0" + "]" * 1500
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.parse_strict_json(deep_txt)
        self.assertIn(cm.exception.code, ("MAX_DEPTH_EXCEEDED", "JSON_PARSE_ERROR"))

        # Non-str dict keys, floats, unsupported types, oversized ints
        for bad_obj, code in (
            ({1: "a"}, "NON_STR_KEY"),
            ({True: "a"}, "NON_STR_KEY"),
            ({"x": 1.0}, "FLOAT_FORBIDDEN"),
            ({"x": (1, 2)}, "UNSUPPORTED_JSON_TYPE"),
            ({"x": Fraction(1, 2)}, "UNSUPPORTED_JSON_TYPE"),
            ({"x": oracle.MAX_JSON_INT + 1}, "INT_TOO_LARGE"),
            ({"x": -(oracle.MAX_JSON_INT + 1)}, "INT_TOO_LARGE"),
        ):
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                oracle.validate_json_value(bad_obj)
            self.assertEqual(cm.exception.code, code)

        # Raw JSON parser checks including exact 400-digit vs 401-digit vs 5000-digit int
        ok_400 = '{"n":' + ("9" * oracle.MAX_INT_DIGITS) + ',"m":-' + ("9" * oracle.MAX_INT_DIGITS) + "}"
        parsed_400 = oracle.parse_strict_json(ok_400)
        self.assertEqual(parsed_400["n"], 10**oracle.MAX_INT_DIGITS - 1)
        for bad_txt, code in (
            ('{"n":' + ("9" * (oracle.MAX_INT_DIGITS + 1)) + "}", "INT_DIGIT_LIMIT"),
            ('{"n":-' + ("9" * (oracle.MAX_INT_DIGITS + 1)) + "}", "INT_DIGIT_LIMIT"),
            ('{"n":' + ("9" * 5000) + "}", "INT_DIGIT_LIMIT"),
            ('{"x":1.0}', "JSON_FLOAT_FORBIDDEN"),
            ('{"x":1e5}', "JSON_FLOAT_FORBIDDEN"),
            ('{"x":NaN}', "JSON_CONSTANT_FORBIDDEN"),
            ('{"x":Infinity}', "JSON_CONSTANT_FORBIDDEN"),
            ('{"a":1,"a":2}', "JSON_DUPLICATE_KEY"),
            ("", "EMPTY_JSON"),
            ("   \n  ", "EMPTY_JSON"),
            ("{bad", "JSON_PARSE_ERROR"),
        ):
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                oracle.parse_strict_json(bad_txt)
            self.assertEqual(cm.exception.code, code)

        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.parse_strict_json(b"{}")  # type: ignore[arg-type]
        self.assertEqual(cm.exception.code, "INVALID_JSON_INPUT")

        exact_cap = '{"s":"' + ("a" * (oracle.MAX_JSON_BYTES - 8)) + '"}'
        self.assertEqual(len(exact_cap.encode("utf-8")), oracle.MAX_JSON_BYTES)
        self.assertIn("s", oracle.parse_strict_json(exact_cap))
        over_cap = '{"s":"' + ("a" * (oracle.MAX_JSON_BYTES - 7)) + '"}'
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.parse_strict_json(over_cap)
        self.assertEqual(cm.exception.code, "JSON_TOO_LARGE")

    def test_exact_linear_algebra_sylvester_and_q23_sign(self) -> None:
        # solve_linear_multi_q & solve_linear_q: pivot swap, multi-RHS, singular, dim mismatch
        x = oracle.solve_linear_q([[0, 2], [3, 1]], [4, 5])
        self.assertEqual(x, [Fraction(1), Fraction(2)])
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.solve_linear_q([[1, 2], [2, 4]], [3, 6])
        self.assertEqual(cm.exception.code, "SINGULAR_MATRIX")
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.solve_linear_multi_q([[1, 0], [0, 1]], [[1]])
        self.assertEqual(cm.exception.code, "DIM_MISMATCH")

        # rank_and_nullspace_q: rank-deficient + full-row early exit
        rk, ns = oracle.rank_and_nullspace_q([[0, 1, 2], [1, 0, 1]], 3)
        self.assertEqual(rk, 2)
        self.assertEqual(ns, [[Fraction(-1), Fraction(-2), Fraction(1)]])

        # sylvester_inertia_q: symmetry guard, 1x1 pos/neg/swap, 2x2 zero-diag, 4x4 block pivot + zero tail
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.sylvester_inertia_q([[1, 2], [3, 1]])
        self.assertEqual(cm.exception.code, "NON_SYMMETRIC_MATRIX")
        self.assertEqual(oracle.sylvester_inertia_q([[0, 0], [0, -3]]), (0, 1, 1))
        self.assertEqual(oracle.sylvester_inertia_q([[0, 1], [1, 0]]), (1, 1, 0))
        self.assertEqual(oracle.sylvester_inertia_q([[0, 0, 1], [0, 0, 0], [1, 0, 0]]), (1, 1, 1))
        self.assertEqual(
            oracle.sylvester_inertia_q([
                [0, 0, 1, 1],
                [0, 0, 1, 0],
                [1, 1, 0, 0],
                [1, 0, 0, 0],
            ]),
            (2, 2, 0),
        )
        self.assertEqual(oracle.sylvester_inertia_q([[0, 0], [0, 0]]), (0, 0, 2))

        # q23_mul & q23_sign exhaustive sign branch coverage (kills every BoolOp in _sign_q_sqrt2 & q23_sign)
        self.assertEqual(
            oracle.q23_mul(
                (Fraction(0), Fraction(1), Fraction(0), Fraction(0)),
                (Fraction(0), Fraction(0), Fraction(1), Fraction(0)),
            ),
            (Fraction(0), Fraction(0), Fraction(0), Fraction(1)),
        )
        sign_cases = [
            ((0, 0, 0, 0), 0),
            ((1, 0, 0, 0), 1),
            ((0, 1, 0, 0), 1),
            ((-1, 0, 0, 0), -1),
            ((0, -1, 0, 0), -1),
            ((2, -1, 0, 0), 1),     # 2 - sqrt(2) > 0
            ((1, -1, 0, 0), -1),    # 1 - sqrt(2) < 0
            ((-2, 1, 0, 0), -1),    # -2 + sqrt(2) < 0
            ((-1, 1, 0, 0), 1),     # -1 + sqrt(2) > 0
            ((0, 0, 1, 0), 1),
            ((0, 0, -1, 0), -1),
            ((2, 0, -1, 0), 1),     # 2 - sqrt(3) > 0 (s_u > 0, s_v < 0, s_diff > 0)
            ((1, 0, -1, 0), -1),    # 1 - sqrt(3) < 0 (s_u > 0, s_v < 0, s_diff < 0)
            ((-2, 0, 1, 0), -1),    # -2 + sqrt(3) < 0 (s_u < 0, s_v > 0, s_diff > 0)
            ((-1, 0, 1, 0), 1),     # -1 + sqrt(3) > 0 (s_u < 0, s_v > 0, s_diff < 0)
            ((0, -3, 2, 0), -1),    # -3*sqrt(2) + 2*sqrt(3) < 0 (18 > 12)
            ((0, -1, 1, 0), 1),     # -sqrt(2) + sqrt(3) > 0 (3 > 2)
        ]
        for tup, expected_sign in sign_cases:
            q_tup = tuple(Fraction(v) for v in tup)
            self.assertEqual(oracle.q23_sign(q_tup), expected_sign)


class TestFiveBiomimeticOperators(unittest.TestCase):
    def test_operator1_spider_webs_and_controls(self) -> None:
        res = oracle.certify_operator1_spider_webs()
        self.assertTrue(res["passed"])
        self.assertTrue(res["monotone_spiral_localization"])
        self.assertTrue(res["connelly_whiteley_prestress_tension_only"]["omega_int_strictly_pd"])
        self.assertGreaterEqual(res["connelly_whiteley_compression_negative_control"]["omega_int_inertia"][1], 1)

        # Must-fail controls: self-loop, disconnected graph, bridge cut, imbalanced tensions
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.laplacian_pseudoinverse_q(3, [(0, 0), (0, 1), (1, 2)], [1, 1, 1])
        self.assertEqual(cm.exception.code, "SELF_LOOP_FORBIDDEN")
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.laplacian_pseudoinverse_q(4, [(0, 1), (2, 3)], [1, 1])
        self.assertEqual(cm.exception.code, "DISCONNECTED_GRAPH")
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.sherman_morrison_lodf_q(3, [(0, 1), (1, 2)], [1, 1], 0)
        self.assertEqual(cm.exception.code, "BRIDGE_EDGE_CUT")

        # Partial-positive tension check kills `and -> or` on `w_sp > 0 and w_in > 0 and w_out > 0`
        imbalanced = oracle.verify_cable_web_prestress_q(Fraction(1), Fraction(10), Fraction(12))
        self.assertFalse(imbalanced["interior_equilibrium_zero_residual"])
        self.assertTrue(imbalanced["strictly_tension_only"])
        mixed_sign = oracle.verify_cable_web_prestress_q(Fraction(1), Fraction(-10), Fraction(11))
        self.assertFalse(mixed_sign["strictly_tension_only"])

    def test_operator2_beaver_dams_and_controls(self) -> None:
        res = oracle.certify_operator2_beaver_dams()
        self.assertTrue(res["passed"])
        self.assertEqual(res["equal_stage_statics"][3]["peak_moment_reduction_ratio"], "512")
        self.assertEqual(res["equal_stage_statics"][3]["total_shear_reduction_ratio"], "8")
        self.assertTrue(res["non_uniform_k4_suboptimal"])
        self.assertTrue(res["flood_peak_monotone_attenuation"])
        self.assertTrue(res["feedback_contrast_t5"]["piping_over_choke_ratio_gt_500"])

        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.analyze_weir_cascade_statics_q(Fraction(8), [Fraction(3), Fraction(3)])
        self.assertEqual(cm.exception.code, "HEAD_SUM_MISMATCH")
        for bad_alpha in (Fraction(1), Fraction(3, 2)):
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                oracle.simulate_flood_cascade_q(2, bad_alpha, 4)
            self.assertEqual(cm.exception.code, "DRAIN_RATE_OUT_OF_RANGE")
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.simulate_conductance_feedback_q(1, 1, Fraction(1, 4), 2, "invalid")
        self.assertEqual(cm.exception.code, "UNKNOWN_FEEDBACK_MODE")
        # Exact steps boundaries 1 and 6 pass; 0 and 7 fail
        self.assertEqual(oracle.simulate_conductance_feedback_q(1, 1, Fraction(1, 4), 1, "choke")["steps"], 1)
        self.assertEqual(oracle.simulate_conductance_feedback_q(1, 1, Fraction(1, 4), 6, "choke")["steps"], 6)
        with self.assertRaises(oracle.BiomimeticOpError):
            oracle.simulate_conductance_feedback_q(1, 1, Fraction(1, 4), 0, "choke")
        with self.assertRaises(oracle.BiomimeticOpError):
            oracle.simulate_conductance_feedback_q(1, 1, Fraction(1, 4), 7, "choke")

    def test_operator3_insect_tunnels_and_controls(self) -> None:
        res = oracle.certify_operator3_insect_tunnels()
        self.assertTrue(res["passed"])
        self.assertEqual(res["ventilation_obstruction"]["tree_advective_power"], "0")
        self.assertTrue(res["ventilation_obstruction"]["cycle_night_exact_reversal"])
        self.assertTrue(res["ventilation_obstruction"]["cycle_coboundary_zero_flux"])
        self.assertEqual(res["digging_congestion_markov"]["clogged_opt_k"], 2)
        self.assertEqual(res["digging_congestion_markov"]["uncrowded_control_opt_k"], 6)

        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.evaluate_cavein_cuts_q(4, [(0, 1), (2, 3)])
        self.assertEqual(cm.exception.code, "DISCONNECTED_BURROW")
        with self.assertRaises(oracle.BiomimeticOpError):
            oracle.evaluate_cavein_cuts_q(2, [(0, 1)])
        self.assertEqual(oracle.solve_digging_markov_q(1, Fraction(1, 2), 1)["n_active"], 1)
        with self.assertRaises(oracle.BiomimeticOpError):
            oracle.solve_digging_markov_q(0, Fraction(1, 2), 1)
        with self.assertRaises(oracle.BiomimeticOpError):
            oracle.solve_digging_markov_q(13, Fraction(1, 2), 1)

    def test_operator4_tailorbird_nests_and_controls(self) -> None:
        res = oracle.certify_operator4_tailorbird_nests()
        self.assertTrue(res["passed"])
        self.assertEqual(res["seam_optimum"]["m_star"], 4)
        self.assertEqual(res["seam_optimum"]["w_cap_star"], "28/11")
        self.assertEqual(res["graded_end_spacing_m4_alpha4"]["graded_net_capacity"], "20/7")
        self.assertEqual(res["graded_end_spacing_m6_alpha6"]["graded_fmax"], "7/22")

        # Boundary m = 2 (n = 1 bay) exact symmetry
        sol2 = oracle.solve_volkersen_discrete_q([Fraction(5)], Fraction(4))
        self.assertEqual(sol2["rivet_forces"], [Fraction(1, 2), Fraction(1, 2)])
        self.assertTrue(sol2["tridiagonal_residual_zero"])

        # Boundary L / dh == 2 rejected; L / dh == 5/2 accepted (m_max = 2)
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.evaluate_tailorbird_seam_q(Fraction(2), Fraction(1), Fraction(4), Fraction(1), Fraction(5))
        self.assertEqual(cm.exception.code, "SEAM_TOO_SHORT_FOR_INTERIOR")
        ok_short = oracle.evaluate_tailorbird_seam_q(Fraction(5, 2), Fraction(1), Fraction(4), Fraction(1), Fraction(5))
        self.assertEqual(ok_short["m_max"], 2)

    def test_operator5_euplectella_maraldi_and_controls(self) -> None:
        res = oracle.certify_operator5_bonus_geometries()
        self.assertTrue(res["passed"])
        self.assertTrue(res["euplectella_4x4_cylindrical_shell"]["passed"])
        self.assertEqual(res["maraldi_rhombic_dodecahedral_base"]["cos_maraldi_theta"], "-1/3")
        self.assertEqual(res["maraldi_rhombic_dodecahedral_base"]["s_maraldi_sq_over_s_flat_sq"], "2/3")

        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.analyze_euplectella_shell_q(4, 4, "bad_pattern")
        self.assertEqual(cm.exception.code, "UNKNOWN_BRACING_PATTERN")
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.analyze_euplectella_shell_q(4, 4, "none", continuous_longitudinal_beams=1)  # type: ignore[arg-type]
        self.assertEqual(cm.exception.code, "INVALID_BOOL_TYPE")

        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            oracle.certify_maraldi_angle_q((Fraction(-1, 10),))
        self.assertEqual(cm.exception.code, "NEGATIVE_APEX_OFFSET")
        ok_zero = oracle.certify_maraldi_angle_q((Fraction(0),))
        self.assertTrue(ok_zero["passed"])


class TestAuditCertificateAndCLI(unittest.TestCase):
    def test_certificate_verification_and_all_rejection_paths(self) -> None:
        cert = audit.build_certificate()
        ok = audit.verify_certificate_dict(cert)
        self.assertTrue(ok["valid"])
        self.assertEqual(ok["payload_sha256"], cert["payload_sha256"])
        self.assertEqual(ok["certificate_sha256"], cert["certificate_sha256"])

        # Non-dict root
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            audit.verify_certificate_dict([])
        self.assertEqual(cm.exception.code, "CERT_NOT_DICT")

        # Missing & extra keys
        missing = copy.deepcopy(cert)
        del missing["payload"]
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            audit.verify_certificate_dict(missing)
        self.assertEqual(cm.exception.code, "CERT_SCHEMA_KEYS")

        extra = copy.deepcopy(cert)
        extra["extra"] = 1
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            audit.verify_certificate_dict(extra)
        self.assertEqual(cm.exception.code, "CERT_SCHEMA_KEYS")

        # Wrong schema & wrong audit_id
        bad_schema = copy.deepcopy(cert)
        bad_schema["schema"] = "wrong"
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            audit.verify_certificate_dict(bad_schema)
        self.assertEqual(cm.exception.code, "CERT_SCHEMA_MISMATCH")

        bad_id = copy.deepcopy(cert)
        bad_id["audit_id"] = "AUDIT-999"
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            audit.verify_certificate_dict(bad_id)
        self.assertEqual(cm.exception.code, "CERT_AUDIT_ID_MISMATCH")

        # Digest type, length, non-hex
        for field in ("payload_sha256", "certificate_sha256"):
            for bad_val, code in (
                (123, "INVALID_DIGEST_TYPE"),
                ("a" * 63, "INVALID_DIGEST_LEN"),
                ("a" * 65, "INVALID_DIGEST_LEN"),
                ("A" + "a" * 63, "INVALID_DIGEST_HEX"),
                ("g" + "a" * 63, "INVALID_DIGEST_HEX"),
            ):
                mut = copy.deepcopy(cert)
                mut[field] = bad_val
                with self.assertRaises(oracle.BiomimeticOpError) as cm:
                    audit.verify_certificate_dict(mut)
                self.assertEqual(cm.exception.code, code)

        # Payload SHA mismatch
        bad_psha = copy.deepcopy(cert)
        first = "1" if cert["payload_sha256"][0] == "0" else "0"
        bad_psha["payload_sha256"] = first + cert["payload_sha256"][1:]
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            audit.verify_certificate_dict(bad_psha)
        self.assertEqual(cm.exception.code, "PAYLOAD_SHA_MISMATCH")

        # Certificate SHA mismatch (valid payload_sha256, flipped certificate_sha256)
        bad_csha = copy.deepcopy(cert)
        cfirst = "1" if cert["certificate_sha256"][0] == "0" else "0"
        bad_csha["certificate_sha256"] = cfirst + cert["certificate_sha256"][1:]
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            audit.verify_certificate_dict(bad_csha)
        self.assertEqual(cm.exception.code, "CERTIFICATE_SHA_MISMATCH")

        # Re-hashed nested bool-as-int forgery (`kappa: 1 -> True`) rejected by RECOMPUTED_PAYLOAD_DRIFT
        forged = copy.deepcopy(cert)
        forged["payload"]["operators"]["op1_spider_webs"]["hierarchy_sweep"][0]["kappa"] = True
        forged_psha = hashlib.sha256(oracle.canonical_json_bytes(forged["payload"])).hexdigest()
        forged["payload_sha256"] = forged_psha
        env = {
            "schema": forged["schema"],
            "audit_id": forged["audit_id"],
            "payload_sha256": forged_psha,
            "payload": forged["payload"],
        }
        forged["certificate_sha256"] = hashlib.sha256(oracle.canonical_json_bytes(env)).hexdigest()
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            audit.verify_certificate_dict(forged)
        self.assertEqual(cm.exception.code, "RECOMPUTED_PAYLOAD_DRIFT")

    def test_file_io_symlinks_canonical_and_cli_exit_codes(self) -> None:
        with self.assertRaises(oracle.BiomimeticOpError) as cm:
            audit.check_certificate_file("not_a_path.json")  # type: ignore[arg-type]
        self.assertEqual(cm.exception.code, "INVALID_PATH_TYPE")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            w_path = root / "written.json"
            w_out = io.StringIO()
            with redirect_stdout(w_out):
                self.assertEqual(audit.main(["--write", str(w_path)]), 0)
            self.assertIn("WROTE AUDIT-117", w_out.getvalue())

            # --standalone --json matches written & committed certificate byte-for-byte
            out_buf = io.BytesIO()
            fake_stdout = io.TextIOWrapper(out_buf, encoding="utf-8")
            with redirect_stdout(fake_stdout):
                rc_json = audit.main(["--standalone", "--json"])
            fake_stdout.flush()
            self.assertEqual(rc_json, 0)
            raw_valid = w_path.read_bytes()
            self.assertEqual(out_buf.getvalue(), raw_valid)
            self.assertEqual(audit.DEFAULT_CERT_PATH.read_bytes(), raw_valid)

            # Default summary & --check CLI paths
            s_out = io.StringIO()
            with redirect_stdout(s_out):
                self.assertEqual(audit.main([]), 0)
            self.assertIn("OK AUDIT-117", s_out.getvalue())

            c_out = io.StringIO()
            with redirect_stdout(c_out):
                self.assertEqual(audit.main(["--check", str(w_path)]), 0)
            self.assertIn("OK AUDIT-117", c_out.getvalue())

            # Symlink target & symlink ancestor rejected
            link_file = root / "link.json"
            link_file.symlink_to(w_path)
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                audit.check_certificate_file(link_file)
            self.assertEqual(cm.exception.code, "SYMLINK_FORBIDDEN")

            real_dir = root / "real_dir"
            real_dir.mkdir()
            link_dir = root / "link_dir"
            link_dir.symlink_to(real_dir)
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                audit.check_certificate_file(link_dir / "cert.json")
            self.assertEqual(cm.exception.code, "SYMLINK_ANCESTOR_FORBIDDEN")

            # Missing file & directory
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                audit.check_certificate_file(root / "missing.json")
            self.assertEqual(cm.exception.code, "CERT_FILE_NOT_FOUND")
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                audit.check_certificate_file(real_dir)
            self.assertEqual(cm.exception.code, "CERT_FILE_NOT_FOUND")

            # Exact MAX_JSON_BYTES file clears size guard (hits EMPTY_JSON); MAX_JSON_BYTES + 1 fails size guard
            cap_file = root / "cap.json"
            cap_file.write_bytes(b" " * oracle.MAX_JSON_BYTES)
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                audit.check_certificate_file(cap_file)
            self.assertEqual(cm.exception.code, "EMPTY_JSON")

            big_file = root / "big.json"
            big_file.write_bytes(b" " * (oracle.MAX_JSON_BYTES + 1))
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                audit.check_certificate_file(big_file)
            self.assertEqual(cm.exception.code, "CERT_FILE_TOO_LARGE")

            # CRLF bytes, invalid UTF-8, non-canonical JSON (extra whitespace / double newline)
            crlf_file = root / "crlf.json"
            crlf_file.write_bytes(raw_valid.rstrip(b"\n") + b"\r\n")
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                audit.check_certificate_file(crlf_file)
            self.assertEqual(cm.exception.code, "CRLF_FORBIDDEN")

            bad_utf8 = root / "bad_utf8.json"
            bad_utf8.write_bytes(b"\xff\xfe{}")
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                audit.check_certificate_file(bad_utf8)
            self.assertEqual(cm.exception.code, "INVALID_UTF8")

            non_canon = root / "non_canon.json"
            non_canon.write_bytes(raw_valid + b"\n")
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                audit.check_certificate_file(non_canon)
            self.assertEqual(cm.exception.code, "NON_CANONICAL_CERT_BYTES")

            pretty = root / "pretty.json"
            pretty.write_text(json.dumps(json.loads(raw_valid.decode("utf-8")), indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(oracle.BiomimeticOpError) as cm:
                audit.check_certificate_file(pretty)
            self.assertEqual(cm.exception.code, "NON_CANONICAL_CERT_BYTES")

            # CLI exit code 2 on 5000-digit int, deep 1500 nesting, missing file
            huge_int_file = root / "huge_int.json"
            huge_int_file.write_text('{"n":' + ("9" * 5000) + "}\n", encoding="utf-8")
            deep_file = root / "deep.json"
            deep_file.write_text("[" * 1500 + "0" + "]" * 1500 + "\n", encoding="utf-8")
            for bad_path in (huge_int_file, deep_file, root / "does_not_exist.json"):
                err_buf = io.StringIO()
                with redirect_stderr(err_buf):
                    rc = audit.main(["--check", str(bad_path)])
                self.assertEqual(rc, 2)
                self.assertIn("REJECT", err_buf.getvalue())


if __name__ == "__main__":
    unittest.main()
