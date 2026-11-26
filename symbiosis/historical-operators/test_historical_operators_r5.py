#!/usr/bin/env python3
"""Must-fail R5 verification suite for symbiosis/historical-operators.

Enforces:
  - Zero AST float literals, zero float() calls, zero math.log, zero bare asserts.
  - Complete truth-table coverage of all boolean predicates.
  - Complete negative boundary and shape-guard coverage of all require_ok checks.
  - Hardened forged-witness refusal (including recomputed payload/certificate SHA-256).
  - Unconditional verification of the committed historical_operators_certificate.json.
"""

from __future__ import annotations

import ast
import copy
from fractions import Fraction
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import verify_historical_operators as vho


VERIFIER_PATH = SCRIPT_DIR / "verify_historical_operators.py"
TEST_PATH = Path(__file__).resolve()


def resign_cert(cert: dict) -> dict:
    """Recompute payload_sha256 and certificate_sha256 on a modified certificate dict."""
    unsigned = {
        k: v for k, v in cert.items() if k not in ("payload_sha256", "certificate_sha256")
    }
    cert["payload_sha256"] = vho.sha256_bytes(vho.canonical_json_bytes(unsigned))
    with_p = dict(unsigned)
    with_p["payload_sha256"] = cert["payload_sha256"]
    cert["certificate_sha256"] = vho.sha256_bytes(vho.canonical_json_bytes(with_p))
    return cert


class TestHistoricalOperatorsHygiene(unittest.TestCase):
    """Static AST hygiene and path-leak checks."""

    def test_zero_floats_zero_logs_zero_bare_asserts(self) -> None:
        forbidden_attrs = {
            "log",
            "log2",
            "log10",
            "log1p",
            "sin",
            "cos",
            "tan",
            "asin",
            "acos",
            "atan",
            "sqrt",
        }
        for path in (VERIFIER_PATH, TEST_PATH):
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src, filename=path.name)
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant):
                    self.assertIsNot(
                        type(node.value),
                        float,
                        f"Forbidden float literal in {path.name}:{getattr(node, 'lineno', 0)}",
                    )
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.assertNotEqual(node.func.id, "float")
                    if isinstance(node.func, ast.Attribute):
                        self.assertNotIn(node.func.attr, forbidden_attrs)
                self.assertNotIsInstance(node, ast.Assert)

    def test_no_user_path_leaks_and_committed_json_valid(self) -> None:
        forbidden_tokens = ("/" + "home" + "/", "/" + "Users" + "/")
        checked = vho.check_certificate_file(vho.DEFAULT_CERT_PATH)
        self.assertTrue(checked["overall_passed"])
        cert_text = vho.DEFAULT_CERT_PATH.read_text(encoding="utf-8")
        for text in (VERIFIER_PATH.read_text(encoding="utf-8"), cert_text):
            for tok in forbidden_tokens:
                self.assertNotIn(tok, text)


class TestHistoricalOperatorsPredicatesAndQs2(unittest.TestCase):
    """Truth-table coverage for boolean predicates, Qs2 arithmetic, and rational helpers."""

    def test_primitives_and_parsers(self) -> None:
        vho.require_ok(True, "ok")
        with self.assertRaisesRegex(ValueError, "boom"):
            vho.require_ok(False, "boom")

        self.assertEqual(vho.require_fraction(Fraction(2, 3), "f"), Fraction(2, 3))
        for bad in (1, True, "2/3", None):
            with self.assertRaisesRegex(ValueError, "must be Fraction"):
                vho.require_fraction(bad, "bad")

        self.assertTrue(vho.is_exact_int(0))
        self.assertTrue(vho.is_exact_int(-9))
        self.assertFalse(vho.is_exact_int(True))
        self.assertFalse(vho.is_exact_int(False))
        self.assertFalse(vho.is_exact_int("4"))

        self.assertTrue(vho.is_hex64("0123456789abcdef" * 4))
        self.assertFalse(vho.is_hex64(123))
        self.assertFalse(vho.is_hex64("a" * 63))
        self.assertFalse(vho.is_hex64("a" * 65))
        self.assertFalse(vho.is_hex64("A" + "a" * 63))
        self.assertFalse(vho.is_hex64("g" + "a" * 63))

        self.assertEqual(vho.ceil_q(Fraction(6, 3)), 2)
        self.assertEqual(vho.ceil_q(Fraction(7, 3)), 3)
        with self.assertRaisesRegex(ValueError, "must be Fraction"):
            vho.ceil_q(3)  # type: ignore[arg-type]

        self.assertEqual(vho.q_to_str(Fraction(-3, 6)), "-1/2")
        with self.assertRaisesRegex(ValueError, "must be Fraction"):
            vho.q_to_str(1)  # type: ignore[arg-type]
        self.assertEqual(vho.str_to_q("-1/2", "x"), Fraction(-1, 2))
        for bad_s in (99, "3", "1/2/3", "/2", "1/", "a/2", "1/b", "1/0", "1/-2", "2/4"):
            with self.assertRaises(ValueError):
                vho.str_to_q(bad_s, "x")

    def test_boolean_predicate_truth_tables(self) -> None:
        f0, f1, f2 = Fraction(0, 1), Fraction(1, 1), Fraction(2, 1)
        self.assertTrue(vho.is_strict_open_bracket_q(f0, f1, f2))
        self.assertFalse(vho.is_strict_open_bracket_q(f1, f1, f2))
        self.assertFalse(vho.is_strict_open_bracket_q(f0, f2, f2))
        self.assertFalse(vho.is_strict_open_bracket_q(f2, f1, f0))
        with self.assertRaisesRegex(ValueError, "lo must be Fraction"):
            vho.is_strict_open_bracket_q(0, f1, f2)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "val must be Fraction"):
            vho.is_strict_open_bracket_q(f0, 1, f2)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "hi must be Fraction"):
            vho.is_strict_open_bracket_q(f0, f1, 2)  # type: ignore[arg-type]

        self.assertTrue(vho.are_inertias_congruence_compatible((4, 4, 0), (4, 4, 0)))
        self.assertFalse(vho.are_inertias_congruence_compatible((3, 4, 0), (4, 4, 0)))
        self.assertFalse(vho.are_inertias_congruence_compatible((4, 3, 0), (4, 4, 0)))
        self.assertFalse(vho.are_inertias_congruence_compatible((4, 4, 1), (4, 4, 0)))
        for bad_in, pat in (
            ([4, 4, 0], "must be tuple"),
            ((4, 4, 0, 0), "length 3"),
            ((True, 4, 0), "must be int"),
            ((-1, 4, 0), "must be >= 0"),
        ):
            with self.assertRaisesRegex(ValueError, pat):
                vho.are_inertias_congruence_compatible(bad_in, (4, 4, 0))  # type: ignore[arg-type]
            with self.assertRaisesRegex(ValueError, pat):
                vho.are_inertias_congruence_compatible((4, 4, 0), bad_in)  # type: ignore[arg-type]

        self.assertTrue(vho.all_three_theorems_certified(True, True, True))
        self.assertFalse(vho.all_three_theorems_certified(False, True, True))
        self.assertFalse(vho.all_three_theorems_certified(True, False, True))
        self.assertFalse(vho.all_three_theorems_certified(True, True, False))

    def test_farkas_4ray_all_truth_branches_and_shape_guards(self) -> None:
        u1 = (Fraction(1, 1), Fraction(1, 1))
        self.assertTrue(vho.farkas_4ray_log_concave_status_q((u1, u1, u1, u1))["global_4ray_ok"])

        r_10_fail = vho.farkas_4ray_log_concave_status_q(
            (
                (Fraction(10, 1), Fraction(10, 1)),
                (Fraction(1, 1), Fraction(2, 1)),
                (Fraction(1, 1), Fraction(10, 1)),
                u1,
            )
        )
        self.assertFalse(r_10_fail["ray_10"])
        self.assertTrue(r_10_fail["ray_01"])
        self.assertFalse(r_10_fail["local_3pt_ok"])

        r_01_fail = vho.farkas_4ray_log_concave_status_q(
            (
                u1,
                (Fraction(1, 1), Fraction(10, 1)),
                (Fraction(1, 1), Fraction(2, 1)),
                (Fraction(10, 1), Fraction(10, 1)),
            )
        )
        self.assertTrue(r_01_fail["ray_10"])
        self.assertFalse(r_01_fail["ray_01"])
        self.assertFalse(r_01_fail["local_3pt_ok"])

        r_21_only = vho.farkas_4ray_log_concave_status_q(
            (
                (Fraction(4, 1), Fraction(5, 1)),
                (Fraction(1, 1), Fraction(3, 1)),
                (Fraction(2, 1), Fraction(4, 1)),
                (Fraction(2, 1), Fraction(5, 1)),
            )
        )
        self.assertTrue(r_21_only["local_3pt_ok"])
        self.assertFalse(r_21_only["ray_21"])
        self.assertTrue(r_21_only["ray_12"])
        self.assertFalse(r_21_only["nonlocal_4pt_ok"])

        r_12_only = vho.farkas_4ray_log_concave_status_q(
            (
                (Fraction(2, 1), Fraction(5, 1)),
                (Fraction(2, 1), Fraction(4, 1)),
                (Fraction(1, 1), Fraction(3, 1)),
                (Fraction(4, 1), Fraction(5, 1)),
            )
        )
        self.assertTrue(r_12_only["local_3pt_ok"])
        self.assertTrue(r_12_only["ray_21"])
        self.assertFalse(r_12_only["ray_12"])
        self.assertFalse(r_12_only["nonlocal_4pt_ok"])

        with self.assertRaisesRegex(ValueError, "boxes must be tuple"):
            vho.farkas_4ray_log_concave_status_q([])  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "length 4"):
            vho.farkas_4ray_log_concave_status_q((u1, u1, u1))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "boxes\\[0\\] must be tuple"):
            vho.farkas_4ray_log_concave_status_q(([Fraction(1, 1), Fraction(1, 1)], u1, u1, u1))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "boxes\\[0\\] must have length 2"):
            vho.farkas_4ray_log_concave_status_q(((Fraction(1, 1),), u1, u1, u1))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "must be > 0"):
            vho.farkas_4ray_log_concave_status_q(((Fraction(0, 1), Fraction(1, 1)), u1, u1, u1))
        with self.assertRaisesRegex(ValueError, "lo <= hi"):
            vho.farkas_4ray_log_concave_status_q(((Fraction(2, 1), Fraction(1, 1)), u1, u1, u1))
        with self.assertRaisesRegex(ValueError, "must be Fraction"):
            vho.farkas_4ray_log_concave_status_q(((1, Fraction(1, 1)), u1, u1, u1))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "must be Fraction"):
            vho.farkas_4ray_log_concave_status_q(((Fraction(1, 1), 1), u1, u1, u1))  # type: ignore[arg-type]

        z_box = (Fraction(0, 1), Fraction(1, 1))
        self.assertTrue(vho.fourier_motzkin_log_concave_additive_q((z_box, z_box, z_box, z_box)))
        with self.assertRaisesRegex(ValueError, "boxes must be tuple"):
            vho.fourier_motzkin_log_concave_additive_q(None)  # type: ignore[arg-type]

    def test_qs2_field_and_sign_quadrants(self) -> None:
        with self.assertRaisesRegex(ValueError, "Qs2.a must be Fraction"):
            vho.Qs2(1, Fraction(0, 1))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "Qs2.b must be Fraction"):
            vho.Qs2(Fraction(0, 1), 1)  # type: ignore[arg-type]

        z = vho.Qs2(Fraction(0, 1), Fraction(0, 1))
        with self.assertRaisesRegex(ValueError, "addend must be Qs2"):
            _ = z + 1  # type: ignore[operator]
        with self.assertRaisesRegex(ValueError, "subtrahend must be Qs2"):
            _ = z - 1  # type: ignore[operator]
        with self.assertRaisesRegex(ValueError, "multiplier must be Qs2"):
            _ = z * 1  # type: ignore[operator]
        with self.assertRaisesRegex(ValueError, "divisor must be Qs2"):
            z.div(1)  # type: ignore[arg-type]
        self.assertEqual(z, vho.Qs2(Fraction(0, 1), Fraction(0, 1)))
        self.assertNotEqual(z, "bad")
        self.assertNotEqual(z, vho.Qs2(Fraction(1, 1), Fraction(0, 1)))
        self.assertNotEqual(z, vho.Qs2(Fraction(0, 1), Fraction(1, 1)))
        self.assertFalse(z.is_strictly_positive())
        with self.assertRaisesRegex(ValueError, "division by zero"):
            z.inv()

        self.assertFalse(vho.Qs2(Fraction(-1, 1), Fraction(-1, 1)).is_strictly_positive())
        self.assertFalse(vho.Qs2(Fraction(-1, 1), Fraction(0, 1)).is_strictly_positive())
        self.assertFalse(vho.Qs2(Fraction(0, 1), Fraction(-1, 1)).is_strictly_positive())
        self.assertTrue(vho.Qs2(Fraction(1, 1), Fraction(0, 1)).is_strictly_positive())
        self.assertTrue(vho.Qs2(Fraction(0, 1), Fraction(1, 1)).is_strictly_positive())
        self.assertTrue(vho.Qs2(Fraction(3, 1), Fraction(-2, 1)).is_strictly_positive())
        self.assertFalse(vho.Qs2(Fraction(1, 1), Fraction(-1, 1)).is_strictly_positive())
        self.assertTrue(vho.Qs2(Fraction(-1, 1), Fraction(1, 1)).is_strictly_positive())
        self.assertFalse(vho.Qs2(Fraction(-3, 1), Fraction(2, 1)).is_strictly_positive())


class TestHistoricalOperatorsLinearAlgebraAndHelpers(unittest.TestCase):
    """Matrix shape, Schur, 2x2-hyperbolic congruence, Sona, and Madhava guard tests."""

    def test_matrix_shape_schur_and_congruence_guards(self) -> None:
        with self.assertRaisesRegex(ValueError, "^m must be list$"):
            vho.require_rect_matrix_q(([Fraction(1, 1)],), "m")
        with self.assertRaisesRegex(ValueError, "non-empty"):
            vho.require_rect_matrix_q([], "m")
        with self.assertRaisesRegex(ValueError, "m\\[0\\] must be list"):
            vho.require_rect_matrix_q(["bad"], "m")
        with self.assertRaisesRegex(ValueError, ">= 1 column"):
            vho.require_rect_matrix_q([[]], "m")
        with self.assertRaisesRegex(ValueError, "m\\[1\\] must be list"):
            vho.require_rect_matrix_q([[Fraction(1, 1)], "bad"], "m")  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "rectangular"):
            vho.require_rect_matrix_q([[Fraction(1, 1), Fraction(0, 1)], [Fraction(1, 1)]], "m")
        with self.assertRaisesRegex(ValueError, "must be Fraction"):
            vho.require_rect_matrix_q([[1]], "m")  # type: ignore[list-item]

        with self.assertRaisesRegex(ValueError, "inner matrix dimensions"):
            vho.mat_mul_q([[Fraction(1, 1), Fraction(2, 1)]], [[Fraction(1, 1)]])

        with self.assertRaisesRegex(ValueError, "a_mat must be square"):
            vho.exact_solve_q([[Fraction(1, 1), Fraction(2, 1)]], [[Fraction(1, 1)]])
        with self.assertRaisesRegex(ValueError, "rhs row count"):
            vho.exact_solve_q(
                [[Fraction(1, 1), Fraction(0, 1)], [Fraction(0, 1), Fraction(1, 1)]],
                [[Fraction(1, 1)]],
            )
        with self.assertRaisesRegex(ValueError, "singular"):
            vho.exact_solve_q(
                [[Fraction(0, 1), Fraction(0, 1)], [Fraction(0, 1), Fraction(1, 1)]],
                [[Fraction(1, 1)], [Fraction(1, 1)]],
            )
        sol = vho.exact_solve_q(
            [[Fraction(0, 1), Fraction(2, 1)], [Fraction(4, 1), Fraction(0, 1)]],
            [[Fraction(6, 1)], [Fraction(8, 1)]],
        )
        self.assertEqual(sol, [[Fraction(2, 1)], [Fraction(3, 1)]])

        self.assertEqual(vho.exact_rank_q([[Fraction(5, 1)]]), 1)
        self.assertEqual(
            vho.exact_rank_q([[Fraction(0, 1), Fraction(2, 1)], [Fraction(3, 1), Fraction(0, 1)]]),
            2,
        )

        e_ok = [(0, 1, Fraction(1, 1))]
        self.assertEqual(len(vho.build_conductance_laplacian_q(128, e_ok)), 128)
        with self.assertRaisesRegex(ValueError, "n_nodes must be int"):
            vho.build_conductance_laplacian_q(True, e_ok)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, ">= 2"):
            vho.build_conductance_laplacian_q(1, e_ok)
        with self.assertRaisesRegex(ValueError, "exceeds bounded limit 128"):
            vho.build_conductance_laplacian_q(129, e_ok)
        with self.assertRaisesRegex(ValueError, "edges must be list"):
            vho.build_conductance_laplacian_q(2, tuple(e_ok))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "non-empty"):
            vho.build_conductance_laplacian_q(2, [])
        with self.assertRaisesRegex(ValueError, "edge must be tuple"):
            vho.build_conductance_laplacian_q(2, [[0, 1, Fraction(1, 1)]])  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "edge must have length 3"):
            vho.build_conductance_laplacian_q(2, [(0, 1, Fraction(1, 1), 99)])  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "edge u must be int"):
            vho.build_conductance_laplacian_q(2, [(False, 1, Fraction(1, 1))])  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "edge v must be int"):
            vho.build_conductance_laplacian_q(2, [(0, True, Fraction(1, 1))])  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "conductance must be > 0"):
            vho.build_conductance_laplacian_q(2, [(0, 1, Fraction(0, 1))])
        with self.assertRaisesRegex(ValueError, "u < 0"):
            vho.build_conductance_laplacian_q(2, [(-1, 1, Fraction(1, 1))])
        with self.assertRaisesRegex(ValueError, "u >= n_nodes"):
            vho.build_conductance_laplacian_q(2, [(2, 1, Fraction(1, 1))])
        with self.assertRaisesRegex(ValueError, "v < 0"):
            vho.build_conductance_laplacian_q(2, [(0, -1, Fraction(1, 1))])
        with self.assertRaisesRegex(ValueError, "v >= n_nodes"):
            vho.build_conductance_laplacian_q(2, [(0, 2, Fraction(1, 1))])
        with self.assertRaisesRegex(ValueError, "self-loop"):
            vho.build_conductance_laplacian_q(2, [(0, 0, Fraction(1, 1))])
        with self.assertRaisesRegex(ValueError, "shunts must be list"):
            vho.build_conductance_laplacian_q(2, e_ok, ((0, Fraction(0, 1)),))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "shunt must be tuple"):
            vho.build_conductance_laplacian_q(2, e_ok, [[0, Fraction(0, 1)]])  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "shunt must have length 2"):
            vho.build_conductance_laplacian_q(2, e_ok, [(0, Fraction(0, 1), 9)])  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "shunt node must be int"):
            vho.build_conductance_laplacian_q(2, e_ok, [(False, Fraction(0, 1))])  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "shunt conductance must be >= 0"):
            vho.build_conductance_laplacian_q(2, e_ok, [(0, Fraction(-1, 2))])
        with self.assertRaisesRegex(ValueError, "shunt node < 0"):
            vho.build_conductance_laplacian_q(2, e_ok, [(-1, Fraction(0, 1))])
        with self.assertRaisesRegex(ValueError, "shunt node >= n_nodes"):
            vho.build_conductance_laplacian_q(2, e_ok, [(2, Fraction(0, 1))])
        lap2 = vho.build_conductance_laplacian_q(2, e_ok, [(0, Fraction(0, 1))])

        with self.assertRaisesRegex(ValueError, "mat must be square"):
            vho.schur_pushforward_with_congruence_q([[Fraction(1, 1), Fraction(0, 1)]], (0,))
        with self.assertRaisesRegex(ValueError, "dim must be >= 2"):
            vho.schur_pushforward_with_congruence_q([[Fraction(1, 1)]], (0,))
        with self.assertRaisesRegex(ValueError, "boundary must be tuple"):
            vho.schur_pushforward_with_congruence_q(lap2, [0])  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "boundary must be non-empty"):
            vho.schur_pushforward_with_congruence_q(lap2, ())
        with self.assertRaisesRegex(ValueError, "interior must be non-empty"):
            vho.schur_pushforward_with_congruence_q(lap2, (0, 1))
        with self.assertRaisesRegex(ValueError, "boundary index must be int"):
            vho.schur_pushforward_with_congruence_q(lap2, (False,))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "boundary index must be int"):
            vho.schur_pushforward_with_congruence_q(lap2, ([0],))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            vho.schur_pushforward_with_congruence_q(
                vho.build_conductance_laplacian_q(
                    3, [(0, 1, Fraction(1, 1)), (1, 2, Fraction(1, 1))]
                ),
                (0, 0),
            )
        with self.assertRaisesRegex(ValueError, "boundary index < 0"):
            vho.schur_pushforward_with_congruence_q(lap2, (-1,))
        with self.assertRaisesRegex(ValueError, "boundary index >= n"):
            vho.schur_pushforward_with_congruence_q(lap2, (2,))

        with self.assertRaisesRegex(ValueError, "matrix must be square"):
            vho.certified_symmetric_congruence_inertia_q([[Fraction(1, 1), Fraction(0, 1)]])
        with self.assertRaisesRegex(ValueError, "symmetric"):
            vho.certified_symmetric_congruence_inertia_q(
                [[Fraction(1, 1), Fraction(2, 1)], [Fraction(3, 1), Fraction(1, 1)]]
            )

        hyp3_a = [
            [Fraction(0, 1), Fraction(0, 1), Fraction(5, 1)],
            [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)],
            [Fraction(5, 1), Fraction(0, 1), Fraction(0, 1)],
        ]
        hyp3_b = [
            [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)],
            [Fraction(0, 1), Fraction(0, 1), Fraction(-3, 1)],
            [Fraction(0, 1), Fraction(-3, 1), Fraction(0, 1)],
        ]
        self.assertEqual(vho.certified_symmetric_congruence_inertia_q(hyp3_a)["inertia"], (1, 1, 1))
        self.assertEqual(vho.certified_symmetric_congruence_inertia_q(hyp3_b)["inertia"], (1, 1, 1))

        id2 = [[Fraction(1, 1), Fraction(0, 1)], [Fraction(0, 1), Fraction(1, 1)]]
        z2 = [[Fraction(0, 1), Fraction(0, 1)], [Fraction(0, 1), Fraction(0, 1)]]
        vho.verify_congruence_certificate_q(id2, id2, [Fraction(1, 1), Fraction(1, 1)])
        with self.assertRaisesRegex(ValueError, "mat must be square"):
            vho.verify_congruence_certificate_q([[Fraction(1, 1), Fraction(0, 1)]], id2, [Fraction(1, 1)])
        with self.assertRaisesRegex(ValueError, "p_mat row mismatch"):
            vho.verify_congruence_certificate_q(id2, [[Fraction(1, 1), Fraction(0, 1)]], [Fraction(1, 1), Fraction(1, 1)])
        with self.assertRaisesRegex(ValueError, "p_mat col mismatch"):
            vho.verify_congruence_certificate_q(id2, [[Fraction(1, 1)], [Fraction(0, 1)]], [Fraction(1, 1), Fraction(1, 1)])
        with self.assertRaisesRegex(ValueError, "diag must be list"):
            vho.verify_congruence_certificate_q(id2, id2, (Fraction(1, 1), Fraction(1, 1)))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "diag length mismatch"):
            vho.verify_congruence_certificate_q(id2, id2, [Fraction(1, 1)])
        with self.assertRaisesRegex(ValueError, "diag entry must be Fraction"):
            vho.verify_congruence_certificate_q(id2, id2, [1, Fraction(1, 1)])  # type: ignore[list-item]
        with self.assertRaisesRegex(ValueError, "P\\^T M P == diag"):
            vho.verify_congruence_certificate_q(id2, id2, [Fraction(2, 1), Fraction(1, 1)])
        with self.assertRaisesRegex(ValueError, "must be invertible"):
            vho.verify_congruence_certificate_q(id2, z2, [Fraction(0, 1), Fraction(0, 1)])

    def test_t2_and_t3_domain_guards(self) -> None:
        self.assertEqual(vho.pingala_nasta_bits(1, 1), (0,))
        self.assertEqual(vho.pingala_nasta_bits(1, 2), (1,))
        self.assertEqual(len(vho.pingala_nasta_bits(32, 1)), 32)
        with self.assertRaisesRegex(ValueError, "n_syllables must be int"):
            vho.pingala_nasta_bits(True, 1)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, ">= 1"):
            vho.pingala_nasta_bits(0, 1)
        with self.assertRaisesRegex(ValueError, "exceeds bounded limit 32"):
            vho.pingala_nasta_bits(33, 1)
        with self.assertRaisesRegex(ValueError, "k_one_based must be int"):
            vho.pingala_nasta_bits(3, True)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "< 1"):
            vho.pingala_nasta_bits(3, 0)
        with self.assertRaisesRegex(ValueError, "> 2\\^n"):
            vho.pingala_nasta_bits(3, 9)

        self.assertEqual(vho.sona_sheaf_laplacian_nullity_q(8, 1)["sheaf_ker_dim"], 1)
        self.assertEqual(vho.sona_sheaf_laplacian_nullity_q(1, 8)["sheaf_ker_dim"], 1)
        with self.assertRaisesRegex(ValueError, "m_rows must be int"):
            vho.sona_sheaf_laplacian_nullity_q(True, 2)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "n_cols must be int"):
            vho.sona_sheaf_laplacian_nullity_q(2, True)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "m_rows must be >= 1"):
            vho.sona_sheaf_laplacian_nullity_q(0, 2)
        with self.assertRaisesRegex(ValueError, "n_cols must be >= 1"):
            vho.sona_sheaf_laplacian_nullity_q(2, 0)
        with self.assertRaisesRegex(ValueError, "m_rows exceeds bounded"):
            vho.sona_sheaf_laplacian_nullity_q(9, 1)
        with self.assertRaisesRegex(ValueError, "n_cols exceeds bounded"):
            vho.sona_sheaf_laplacian_nullity_q(1, 9)
        with self.assertRaisesRegex(ValueError, "vertical_mirrors must be tuple"):
            vho.sona_sheaf_laplacian_nullity_q(2, 2, [(2, 1)])  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "mirror entry must be tuple"):
            vho.sona_sheaf_laplacian_nullity_q(2, 2, ([2, 1],))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "mirror entry must have length 2"):
            vho.sona_sheaf_laplacian_nullity_q(2, 2, ((2, 1, 0),))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "mirror x must be int"):
            vho.sona_sheaf_laplacian_nullity_q(2, 2, ((True, 1),))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "mirror y must be int"):
            vho.sona_sheaf_laplacian_nullity_q(2, 2, ((2, True),))  # type: ignore[arg-type]

        with self.assertRaisesRegex(ValueError, "kappa_sq must be Qs2"):
            vho.biruni_stereographic_meridian_qs2(1, Fraction(0, 1))  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "s_param must be Fraction"):
            vho.biruni_stereographic_meridian_qs2(vho.Qs2(Fraction(1, 1)), 0)  # type: ignore[arg-type]

        f1, f2 = Fraction(1, 1), Fraction(2, 1)
        with self.assertRaisesRegex(ValueError, "eig1 must be > 0"):
            vho.stieltjes_hankel_rh4_interval_q(Fraction(0, 1), f1, Fraction(0, 1), f1)
        with self.assertRaisesRegex(ValueError, "eig2 must be > 0"):
            vho.stieltjes_hankel_rh4_interval_q(f2, Fraction(0, 1), Fraction(0, 1), f1)
        with self.assertRaisesRegex(ValueError, "eig3_lo must be >= 0"):
            vho.stieltjes_hankel_rh4_interval_q(f2, f1, Fraction(-1, 5), f1)
        with self.assertRaisesRegex(ValueError, "eig3_lo must be <= eig3_hi"):
            vho.stieltjes_hankel_rh4_interval_q(f2, f1, f2, f1)
        with self.assertRaisesRegex(ValueError, "Hankel determinant"):
            vho.stieltjes_hankel_rh4_interval_q(f1, f1, f1, f1)

        self.assertLess(vho.madhava_sigma_enclosures_even_n_q(128)["madhava_lo"], Fraction(4, 5))
        with self.assertRaisesRegex(ValueError, "must be int"):
            vho.madhava_sigma_enclosures_even_n_q(True)  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, ">= 2"):
            vho.madhava_sigma_enclosures_even_n_q(0)
        with self.assertRaisesRegex(ValueError, "exceeds bounded limit 128"):
            vho.madhava_sigma_enclosures_even_n_q(130)
        with self.assertRaisesRegex(ValueError, "must be even"):
            vho.madhava_sigma_enclosures_even_n_q(3)


class TestHistoricalOperatorsForgedCertificateAndCli(unittest.TestCase):
    """Per-field invariant refusal, re-hashed forgery refusal, monkeypatch R5, and CLI tests."""

    def test_verify_core_invariants_and_rehashed_forgery_refusal(self) -> None:
        base = vho.build_certificate()
        vho.validate_certificate(base)

        with self.assertRaisesRegex(ValueError, "core must be dict"):
            vho.verify_core_invariants([])

        def assert_core_tamper(tamper_fn, pat: str) -> None:
            bad = copy.deepcopy(base)
            tamper_fn(bad)
            with self.assertRaisesRegex(ValueError, pat):
                vho.verify_core_invariants(bad)

        assert_core_tamper(lambda c: c.__setitem__("schema_version", "v0"), "schema_version")
        assert_core_tamper(lambda c: c.__setitem__("arithmetic_domain", "bad"), "arithmetic_domain")
        assert_core_tamper(lambda c: c.__setitem__("gate5_scope_statement", "bad"), "gate5_scope")
        assert_core_tamper(lambda c: c.__setitem__("provenance_digests", "bad"), "provenance_digests must be dict")
        assert_core_tamper(
            lambda c: c["provenance_digests"].__setitem__("extra", "a" * 64), "provenance keys"
        )
        assert_core_tamper(
            lambda c: c["provenance_digests"].__setitem__(
                "primary_arabic_heritage_engines_cert", "a" * 63
            ),
            "must be 64-hex",
        )
        assert_core_tamper(
            lambda c: c["provenance_digests"].__setitem__(
                "primary_arabic_heritage_engines_cert", "0" * 64
            ),
            "mismatch",
        )
        assert_core_tamper(lambda c: c.__setitem__("theorems", "bad"), "theorems must be dict")

        # T1 core guards
        assert_core_tamper(lambda c: c["theorems"].__setitem__("t1_schur_and_gate5", "bad"), "t1 must be dict")
        for fn, pat in (
            ("passed", "t1 passed"),
            ("haynsworth_unitriangular_additivity_verified", "haynsworth flag"),
            ("true_sylvester_congruence_h8_pair_verified", "congruence flag"),
            ("gate5_passive_hydraulic_non_congruence_verified", "gate5 flag"),
        ):
            assert_core_tamper(lambda c, f=fn: c["theorems"]["t1_schur_and_gate5"].__setitem__(f, False), pat)
        assert_core_tamper(
            lambda c: c["theorems"]["t1_schur_and_gate5"].__setitem__("petra_surge_unvented", "1/2"),
            "petra 1/3",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t1_schur_and_gate5"].__setitem__("petra_surge_vented", "1/15"),
            "petra 64/1365",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t1_schur_and_gate5"].__setitem__("casarabe_conductance", "3/2"),
            "casarabe g",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t1_schur_and_gate5"].__setitem__("inertias_pos_neg_zero", "bad"),
            "inertias must be dict",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t1_schur_and_gate5"]["inertias_pos_neg_zero"].__setitem__(
                "sigma_star_h8_fold_sheaf", [8, 0, 0]
            ),
            "sigma_star inertia",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t1_schur_and_gate5"]["inertias_pos_neg_zero"].__setitem__(
                "hydraulic_conduit_8x8", [4, 4, 0]
            ),
            "hydraulic_8x8 inertia",
        )

        # T2 core guards
        assert_core_tamper(lambda c: c["theorems"].__setitem__("t2_parity_sona_biruni", "bad"), "t2 must be dict")
        for fn, pat in (
            ("passed", "t2 passed"),
            ("pingala_nasta3_equals_sylvester_h8", "pingala h8"),
            ("bamana_rm14_orth_a16_verified", "rm14 orth"),
            ("sona_16_grids_gcd_ker_verified", "sona gcd"),
            ("biruni_stereographic_f8_e8_identity_verified", "biruni fold"),
        ):
            assert_core_tamper(lambda c, f=fn: c["theorems"]["t2_parity_sona_biruni"].__setitem__(f, False), pat)
        assert_core_tamper(
            lambda c: c["theorems"]["t2_parity_sona_biruni"].__setitem__("ifa_even_parity_e8_spinor_roots", 64),
            "128 spinor",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t2_parity_sona_biruni"].__setitem__("e8_total_kissing_roots", 239),
            "240 roots",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t2_parity_sona_biruni"].__setitem__("sona_2x2_ker_raw_to_walled", [2, 2]),
            "2x2 merge",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t2_parity_sona_biruni"].__setitem__("sona_2x3_ker_raw_to_walled", [1, 1]),
            "2x3 split",
        )

        # T3 core guards (including exact thresholds 2/1 and 1314574 vs 1314575!)
        assert_core_tamper(
            lambda c: c["theorems"].__setitem__("t3_farkas_and_madhava_hankel", "bad"), "t3 must be dict"
        )
        for fn, pat in (
            ("passed", "t3 passed"),
            ("farabi_local_steps_pass_31_53", "farabi local"),
            ("zu_chongzhi_4ray_local_3pt_ok", "zu local"),
            ("fourier_motzkin_equivalence_verified", "fm flag"),
        ):
            assert_core_tamper(
                lambda c, f=fn: c["theorems"]["t3_farkas_and_madhava_hankel"].__setitem__(f, False), pat
            )
        assert_core_tamper(
            lambda c: c["theorems"]["t3_farkas_and_madhava_hankel"].__setitem__(
                "farabi_global_span_pass_31_53", True
            ),
            "farabi global must be False",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t3_farkas_and_madhava_hankel"].__setitem__(
                "zu_chongzhi_4ray_nonlocal_4pt_ok", True
            ),
            "zu nonlocal must be False",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t3_farkas_and_madhava_hankel"].__setitem__("n2_ceil_ropt_2moment", 3),
            "ceil ropt == 2",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t3_farkas_and_madhava_hankel"].__setitem__("n2_ceil_rh4_raw_leibniz", 3),
            "ceil rh4 raw == 2",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t3_farkas_and_madhava_hankel"].__setitem__("n2_ceil_rh4_madhava_r2_r3", 2),
            "ceil rh4 madhava == 3",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t3_farkas_and_madhava_hankel"].__setitem__("n2_rh4_madhava_lower", "2/1"),
            "rh4_lo > 2",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t3_farkas_and_madhava_hankel"].__setitem__(
                "n20_rh4_width_tightening_floor", True
            ),
            "tightening floor must be int",
        )
        assert_core_tamper(
            lambda c: c["theorems"]["t3_farkas_and_madhava_hankel"].__setitem__(
                "n20_rh4_width_tightening_floor", 1314574
            ),
            ">= 1314575",
        )
        assert_core_tamper(lambda c: c.__setitem__("overall_passed", False), "overall_passed")

        # Validate_certificate hash & re-hashed unpinned-witness forgery refusal!
        for key, val, pat in (
            ("payload_sha256", "bad", "payload_sha256 must be 64-hex"),
            ("certificate_sha256", "bad", "certificate_sha256 must be 64-hex"),
            ("payload_sha256", "0" * 64, "payload_sha256 digest mismatch"),
            ("certificate_sha256", "0" * 64, "certificate_sha256 digest mismatch"),
        ):
            bh = copy.deepcopy(base)
            bh[key] = val
            with self.assertRaisesRegex(ValueError, pat):
                vho.validate_certificate(bh)

        # Forged secondary witness field WITH recomputed payload_sha256 & certificate_sha256 MUST FAIL!
        forged = copy.deepcopy(base)
        forged["theorems"]["t3_farkas_and_madhava_hankel"]["n20_rh4_width_tightening_floor"] = 9999999
        resign_cert(forged)
        with self.assertRaisesRegex(ValueError, "diverges from freshly recomputed pure-Q oracle"):
            vho.validate_certificate(forged)

        # Bool-for-int type-confusion forgery ([2, True] == [2, 1] in Python ==) MUST ALSO FAIL!
        bool_forged = copy.deepcopy(base)
        bool_forged["theorems"]["t2_parity_sona_biruni"]["sona_2x2_ker_raw_to_walled"] = [2, True]
        resign_cert(bool_forged)
        with self.assertRaisesRegex(ValueError, "diverges from freshly recomputed pure-Q oracle"):
            vho.validate_certificate(bool_forged)

    def test_in_memory_monkeypatch_refusal_and_cli_modes(self) -> None:
        fake_in = {"inertia": (8, 0, 0), "diag": [], "p_mat": [], "certified_congruence_ok": True}
        with mock.patch.object(vho, "certified_symmetric_congruence_inertia_q", return_value=fake_in):
            with self.assertRaises(ValueError):
                vho.build_certificate()

        fake_sona = {
            "n_segments": 4,
            "loop_count": 1,
            "coboundary_rank": 3,
            "sheaf_ker_dim": 99,
            "internal_floppy_modes": 98,
        }
        with mock.patch.object(vho, "sona_sheaf_laplacian_nullity_q", return_value=fake_sona):
            with self.assertRaises(ValueError):
                vho.build_certificate()

        fake_enc = {
            "raw_lo": Fraction(2, 3),
            "raw_hi": Fraction(1, 1),
            "madhava_lo": Fraction(2, 3),
            "madhava_hi": Fraction(79, 100),
        }
        with mock.patch.object(vho, "madhava_sigma_enclosures_even_n_q", return_value=fake_enc):
            with self.assertRaises(ValueError):
                vho.build_certificate()

        with tempfile.TemporaryDirectory() as tmp:
            cpath = Path(tmp) / "cert.json"
            with self.assertRaisesRegex(ValueError, "cert_path must be Path"):
                vho.check_certificate_file(str(cpath))  # type: ignore[arg-type]
            with self.assertRaisesRegex(ValueError, "certificate file not found"):
                vho.check_certificate_file(cpath)

            buf_w = io.StringIO()
            with mock.patch("sys.stdout", buf_w):
                self.assertEqual(vho.main(["--write", "--cert-path", str(cpath)]), 0)
            self.assertIn("WROTE", buf_w.getvalue())

            # Both default (no mode arg) and --check must succeed identically
            for cli_args in (["--cert-path", str(cpath)], ["--check", "--cert-path", str(cpath)]):
                buf_c = io.StringIO()
                with mock.patch("sys.stdout", buf_c):
                    self.assertEqual(vho.main(cli_args), 0)
                self.assertIn("PASS", buf_c.getvalue())

            buf_j = io.StringIO()
            with mock.patch("sys.stdout", buf_j):
                self.assertEqual(vho.main(["--json"]), 0)
            self.assertEqual(buf_j.getvalue(), cpath.read_text(encoding="utf-8"))

            # Mutually exclusive flags rejected by argparse
            with mock.patch("sys.stderr", io.StringIO()):
                with self.assertRaises(SystemExit):
                    vho.main(["--write", "--check"])

            cpath.write_text(buf_j.getvalue() + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "formatting is not canonical"):
                vho.check_certificate_file(cpath)

            cmd = [sys.executable, "-I", "-B"]
            if "error" in sys.warnoptions:
                cmd.extend(["-W", "error"])
            cmd.extend([str(VERIFIER_PATH), "--json"])
            proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.assertEqual(proc.stdout, buf_j.getvalue())


if __name__ == "__main__":
    unittest.main()
