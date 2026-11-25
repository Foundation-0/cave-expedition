#!/usr/bin/env python3
"""
Assertion-free R5 mutation-hardened test suite for AUDIT-114
(`zone_sylvester_oracle.py` & `zone_sylvester_audit.py`).

Zero bare `assert`s (100% `python3 -O` parity). Zero floats on trust paths.
Designed for 100.0% `aletheia v2.0.0 mutate --max-mutants 0` and AST BoolOp kill rates.
"""
from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import zone_sylvester_audit as za
import zone_sylvester_oracle as zo


class Audit114R5Test(unittest.TestCase):
    def _assert_err(self, code: str, fn, *args, **kwargs) -> None:
        with self.assertRaises(zo.Audit114Error) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code)

    # ------------------------------------------------------------------
    # 1. Strict Primitives & Rational Dialects
    # ------------------------------------------------------------------
    def test_01_strict_int_bool_and_rational_dialects(self) -> None:
        self.assertEqual(zo.require_strict_int(0, "x", lo=0, hi=0), 0)
        self.assertEqual(zo.require_strict_int(5, "x", lo=0, hi=5), 5)
        self._assert_err("INVALID_INT_TYPE", zo.require_strict_int, True, "x")
        self._assert_err("INVALID_INT_TYPE", zo.require_strict_int, "1", "x")
        self._assert_err("INT_BELOW_MIN", zo.require_strict_int, -1, "x", lo=0)
        self._assert_err("INT_ABOVE_MAX", zo.require_strict_int, 6, "x", hi=5)

        self.assertIs(zo.require_strict_bool(True, "b"), True)
        self.assertIs(zo.require_strict_bool(False, "b"), False)
        self._assert_err("INVALID_BOOL_TYPE", zo.require_strict_bool, 1, "b")
        self._assert_err("INVALID_BOOL_TYPE", zo.require_strict_bool, None, "b")

        # format_rational
        self.assertEqual(zo.format_rational(Fraction(0, 1), dialect="loom7_margin"), "0/1")
        self.assertEqual(zo.format_rational(Fraction(3, 1), dialect="spectral2"), "3")
        self.assertEqual(zo.format_rational(Fraction(-2, 5), dialect="spectral2"), "-2/5")
        self._assert_err("INVALID_FRACTION_OBJ", zo.format_rational, 1)
        self._assert_err("UNKNOWN_DIALECT", zo.format_rational, Fraction(1), dialect="bad")

        # parse_rational across dialects
        self.assertEqual(zo.parse_rational(Fraction(3, 4)), Fraction(3, 4))
        self.assertEqual(zo.parse_rational(7), Fraction(7, 1))
        self.assertEqual(zo.parse_rational("7/1", dialect="any"), Fraction(7, 1))
        self.assertEqual(zo.parse_rational("0/1", dialect="loom7_margin"), Fraction(0, 1))
        self.assertEqual(zo.parse_rational("-3/4", dialect="loom7_margin"), Fraction(-3, 4))
        self.assertEqual(zo.parse_rational("0", dialect="spectral2"), Fraction(0, 1))
        self.assertEqual(zo.parse_rational("-3/4", dialect="spectral2"), Fraction(-3, 4))
        self._assert_err("UNKNOWN_DIALECT", zo.parse_rational, "1", dialect="nope")
        self._assert_err("INVALID_RATIONAL_TYPE", zo.parse_rational, True)
        self._assert_err("INVALID_RATIONAL_TYPE", zo.parse_rational, 1.5)
        self._assert_err("INVALID_RATIONAL_TYPE", zo.parse_rational, 1, dialect="spectral2")
        max_d = zo.MAX_RATIONAL_DIGITS
        self._assert_err("RATIONAL_TOO_LONG", zo.parse_rational, "1" + "0" * max_d)
        self.assertEqual(zo.parse_rational("1" + "0" * (max_d - 1)), Fraction(10 ** (max_d - 1)))
        self._assert_err("RATIONAL_TOO_LONG", zo.parse_rational, "1/" + "9" * (max_d + 1), dialect="spectral2")
        self._assert_err("RATIONAL_TOO_LONG", zo.parse_rational, "1" + "0" * max_d + "/3", dialect="spectral2")
        self.assertEqual(zo.parse_rational("1/" + "9" * max_d, dialect="spectral2"), Fraction(1, int("9" * max_d)))
        self._assert_err("RATIONAL_TOO_LONG", zo.parse_rational, "1/" + "9" * (max_d + 1), dialect="loom7_margin")
        self._assert_err("RATIONAL_TOO_LONG", zo.parse_rational, "1" + "0" * max_d + "/1", dialect="loom7_margin")
        self.assertEqual(zo.parse_rational("1/" + "9" * max_d, dialect="loom7_margin"), Fraction(1, int("9" * max_d)))
        self._assert_err("INVALID_LOOM7_RATIONAL", zo.parse_rational, "0", dialect="loom7_margin")
        self._assert_err("INVALID_LOOM7_RATIONAL", zo.parse_rational, "-0/1", dialect="loom7_margin")
        self._assert_err("UNREDUCED_RATIONAL", zo.parse_rational, "2/4", dialect="loom7_margin")
        self._assert_err("INVALID_RATIONAL_SYNTAX", zo.parse_rational, "01", dialect="spectral2")
        self._assert_err("INVALID_RATIONAL_SYNTAX", zo.parse_rational, "1/2\n", dialect="spectral2")
        self._assert_err("SPECTRAL2_UNIT_DENOM_FORBIDDEN", zo.parse_rational, "1/1", dialect="spectral2")
        self._assert_err("UNREDUCED_RATIONAL", zo.parse_rational, "2/4", dialect="spectral2")

    # ------------------------------------------------------------------
    # 2. Pillar 1: `zone-canon-v0` vs `aletheia v2.0/v2.1`
    # ------------------------------------------------------------------
    def test_02_zone_canon_v0_and_v21_differential(self) -> None:
        # Exact boundary integers +/- (2^53 - 1) accepted; +/- 2^53 and >40-digit rejected
        lim = zo.ZONE_CANON_INT_LIMIT
        self.assertEqual(zo.parse_zone_canon_v0(f'{{"a":{lim},"b":{-lim}}}'), {"a": lim, "b": -lim})
        self.assertEqual(zo.encode_zone_canon_v0({"a": lim, "b": -lim}), f'{{"a":{lim},"b":{-lim}}}'.encode("utf-8"))
        self.assertEqual(zo.encode_zone_canon_v0([None, True, False, (1,)]), b"[null,true,false,[1]]")
        # All control escapes in _escape_zone_str: ", \, \b, \f, \n, \r, \t, \x00, \x1f, space 0x20, DEL 0x7f
        ctrl_in = '"\\\b\f\n\r\t\x00\x1f \x7f'
        self.assertEqual(
            zo.encode_zone_canon_v0(ctrl_in),
            b'"\\"\\\\\\b\\f\\n\\r\\t\\u0000\\u001f \x7f"',
        )
        # Boundary around surrogates U+D7FF, U+D800, U+DFFF, U+E000
        self.assertEqual(zo.encode_zone_canon_v0("\ud7ff\ue000"), '"\ud7ff\ue000"'.encode("utf-8"))
        self._assert_err("ZONE_LONE_SURROGATE", zo.encode_zone_canon_v0, "\ud800")
        self._assert_err("ZONE_LONE_SURROGATE", zo.encode_zone_canon_v0, "\udfff")

        # Parser error paths
        self._assert_err("EMPTY_JSON", zo.parse_zone_canon_v0, "")
        self._assert_err("EMPTY_JSON", zo.parse_zone_canon_v0, "   ")
        self._assert_err("EMPTY_JSON", zo.parse_zone_canon_v0, None)
        self._assert_err("JSON_SYNTAX_ERROR", zo.parse_zone_canon_v0, "{bad")
        self._assert_err("ZONE_NEGATIVE_ZERO", zo.parse_zone_canon_v0, '{"x":-0}')
        self._assert_err("ZONE_INT_TOO_LONG", zo.parse_zone_canon_v0, '{"x":' + "9" * 41 + "}")
        self._assert_err("ZONE_INT_OUT_OF_RANGE", zo.parse_zone_canon_v0, '{"x":' + "9" * 40 + "}")
        self._assert_err("ZONE_INT_OUT_OF_RANGE", zo.parse_zone_canon_v0, f'{{"x":{lim + 1}}}')
        self._assert_err("ZONE_INT_OUT_OF_RANGE", zo.encode_zone_canon_v0, lim + 1)
        # S17-BUG-07: oversized in-memory ints must not trigger Python's 4,300-digit ValueError in f-strings
        self._assert_err("ZONE_INT_OUT_OF_RANGE", zo.encode_zone_canon_v0, 10**5000)
        self._assert_err("ZONE_INT_OUT_OF_RANGE", zo.encode_zone_canon_v0, -(10**5000))
        self._assert_err("INT_ABOVE_MAX", zo.require_strict_int, 10**5000, hi=10)
        self._assert_err("INT_BELOW_MIN", zo.require_strict_int, -(10**5000), lo=0)
        self._assert_err("JSON_FLOAT_FORBIDDEN", zo.parse_zone_canon_v0, '{"x":0.0}')
        self._assert_err("JSON_CONSTANT_FORBIDDEN", zo.parse_zone_canon_v0, '{"x":NaN}')
        self._assert_err("JSON_DUPLICATE_KEY", zo.parse_zone_canon_v0, '{"a":1,"a":2}')
        self._assert_err("NON_STRING_KEY", zo.encode_zone_canon_v0, {1: "a"})
        self._assert_err("UNSUPPORTED_JSON_TYPE", zo.encode_zone_canon_v0, 1.5)

        # Aletheia v2.0/v2.1 strict parser + encoder
        self._assert_err("EMPTY_JSON", zo.parse_aletheia_strict_nofloat, "")
        self._assert_err("EMPTY_JSON", zo.parse_aletheia_strict_nofloat, "   ")
        self._assert_err("EMPTY_JSON", zo.parse_aletheia_strict_nofloat, 123)
        self._assert_err("JSON_SYNTAX_ERROR", zo.parse_aletheia_strict_nofloat, "{bad")
        self._assert_err("JSON_FLOAT_FORBIDDEN", zo.parse_aletheia_strict_nofloat, '{"s":1e-05}')
        self._assert_err("JSON_CONSTANT_FORBIDDEN", zo.parse_aletheia_strict_nofloat, '{"s":Infinity}')
        self._assert_err("JSON_DUPLICATE_KEY", zo.parse_aletheia_strict_nofloat, '{"a":1,"a":2}')
        self._assert_err("NON_STRING_KEY", zo.canonical_json_bytes_v21, {True: "a"})
        self._assert_err("V21_FORBIDDEN_TYPE", zo.canonical_json_bytes_v21, {"x": 0.5})
        self.assertEqual(zo.canonical_json_bytes_v21({"x": (1, None, True)}), b'{"x":[1,null,true]}')

        # S17-BUG-05: iterative depth cap (depth==64 accepted, depth==65/1200 & cyclic rejected) + int cap
        ok_nested_list: object = 1
        for _ in range(zo.MAX_JSON_DEPTH):
            ok_nested_list = [ok_nested_list]
        self.assertTrue(zo.encode_zone_canon_v0(ok_nested_list).startswith(b"["))
        self.assertTrue(zo.canonical_json_bytes_v21(ok_nested_list).startswith(b"["))
        ok_json_64 = "[" * zo.MAX_JSON_DEPTH + "1" + "]" * zo.MAX_JSON_DEPTH
        self.assertEqual(zo.parse_zone_canon_v0(ok_json_64), ok_nested_list)
        self.assertEqual(zo.parse_aletheia_strict_nofloat(ok_json_64), ok_nested_list)
        too_deep_list = [ok_nested_list]
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.encode_zone_canon_v0, too_deep_list)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.canonical_json_bytes_v21, too_deep_list)
        bad_json_65 = "[" * (zo.MAX_JSON_DEPTH + 1) + "1" + "]" * (zo.MAX_JSON_DEPTH + 1)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.parse_zone_canon_v0, bad_json_65)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.parse_aletheia_strict_nofloat, bad_json_65)
        too_deep_dict: object = 1
        for _ in range(zo.MAX_JSON_DEPTH + 1):
            too_deep_dict = {"a": too_deep_dict}
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.encode_zone_canon_v0, too_deep_dict)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.canonical_json_bytes_v21, too_deep_dict)
        bad_dict_json_65 = '{"a":' * (zo.MAX_JSON_DEPTH + 1) + "1" + "}" * (zo.MAX_JSON_DEPTH + 1)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.parse_zone_canon_v0, bad_dict_json_65)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.parse_aletheia_strict_nofloat, bad_dict_json_65)
        deep_1200: object = 1
        for _ in range(1200):
            deep_1200 = [deep_1200]
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.encode_zone_canon_v0, deep_1200)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.canonical_json_bytes_v21, deep_1200)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.parse_zone_canon_v0, "[" * 1200 + "]" * 1200)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.parse_aletheia_strict_nofloat, "[" * 1200 + "]" * 1200)
        cyc_list: list[object] = []
        cyc_list.append(cyc_list)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.encode_zone_canon_v0, cyc_list)
        self._assert_err("JSON_DEPTH_EXCEEDED", zo.canonical_json_bytes_v21, cyc_list)
        max_v21_int = (1 << zo.MAX_V21_INT_BITS) - 1
        self.assertTrue(zo.canonical_json_bytes_v21(max_v21_int).isdigit())
        self._assert_err("V21_INT_TOO_LARGE", zo.canonical_json_bytes_v21, 1 << zo.MAX_V21_INT_BITS)
        self._assert_err("V21_INT_TOO_LARGE", zo.canonical_json_bytes_v21, 10**5000)
        self._assert_err("JSON_SYNTAX_ERROR", zo.parse_aletheia_strict_nofloat, '{"n":' + "9" * 5000 + "}")

        # Full differential audit checks
        p1 = zo.audit_zone_canon_differential()
        self.assertEqual(p1["mde8_accept_certified"], 7)
        self.assertEqual(p1["mde8_reject_certified"], 10)
        self.assertEqual(
            p1["mde8_byte_divergences_vs_v21"],
            ["non_ascii_raw_utf8", "astral_key_sorts_after_ffff", "control_chars_escaped"],
        )
        self.assertEqual(
            p1["mde8_domain_set_diff_v21_minus_zone"],
            ["negative_zero", "integer_2_pow_53", "integer_above_u64"],
        )
        self.assertEqual(p1["ascii_0_127_divergent_codepoints"], [127])
        self.assertEqual(p1["non_str_dict_keys_rejected_count"], 4)
        probes = {r["name"]: r for r in p1["extra_boundary_probes"]}
        self.assertFalse(probes["neg_2_pow_53"]["zone_canon_v0_accepted"])
        self.assertTrue(probes["neg_2_pow_53"]["aletheia_v21_accepted"])
        self.assertFalse(probes["lone_surrogate_text"]["zone_canon_v0_accepted"])
        self.assertTrue(probes["lone_surrogate_text"]["aletheia_v21_accepted"])
        self.assertTrue(probes["nfc_vs_nfd_distinct_keys"]["zone_canon_v0_accepted"])
        self.assertTrue(probes["nfc_vs_nfd_distinct_keys"]["aletheia_v21_accepted"])
        self.assertFalse(probes["nfc_vs_nfd_distinct_keys"]["same_sha256_when_both_accept"])

    # ------------------------------------------------------------------
    # 3. Pillar 2: Sylvester Inertia, Zero-Diagonal Blocks, Truss & Loom#7
    # ------------------------------------------------------------------
    def test_03_sylvester_certifier_guards_and_zero_diag(self) -> None:
        # Matrix parser guards
        self._assert_err("EMPTY_MATRIX", zo.parse_sym_matrix_q, [])
        self._assert_err("EMPTY_MATRIX", zo.parse_sym_matrix_q, "notlist")
        self._assert_err("MATRIX_DIM_EXCEEDED", zo.parse_sym_matrix_q, [[0, 0], [0, 0]], max_dim=1)
        self.assertEqual(len(zo.parse_sym_matrix_q([[0]], max_dim=1)), 1)
        self._assert_err("MATRIX_NOT_SQUARE", zo.parse_sym_matrix_q, [[1, 0]])
        self._assert_err("MATRIX_NOT_SQUARE", zo.parse_sym_matrix_q, ["bad"])
        self._assert_err("MATRIX_NOT_SYMMETRIC", zo.parse_sym_matrix_q, [[1, 2], [3, 1]])

        # Block 2x2 guards (incl. S17-BUG-02 strict Fraction check) & all 5 rows
        self._assert_err("BLOCK_2X2_ENTRY_NOT_FRACTION", zo.block_2x2_inertia_q, 1.5, Fraction(1), Fraction(1))
        self._assert_err("BLOCK_2X2_ENTRY_NOT_FRACTION", zo.block_2x2_inertia_q, Fraction(1), True, Fraction(1))
        self._assert_err("BLOCK_2X2_ENTRY_NOT_FRACTION", zo.block_2x2_inertia_q, Fraction(1), Fraction(1), float("nan"))
        self._assert_err("BLOCK_2X2_ENTRY_NOT_FRACTION", zo.block_2x2_inertia_q, None, Fraction(1), Fraction(1))
        self._assert_err("BLOCK_2X2_ENTRY_NOT_FRACTION", zo.block_2x2_inertia_q, "1", Fraction(1), Fraction(1))
        self._assert_err("BLOCK_2X2_ZERO_OFFDIAG", zo.block_2x2_inertia_q, Fraction(1), Fraction(0), Fraction(1))
        self.assertEqual(zo.block_2x2_inertia_q(Fraction(0), Fraction(1), Fraction(0)), (1, 1, 0))
        self.assertEqual(zo.block_2x2_inertia_q(Fraction(2), Fraction(1), Fraction(2)), (2, 0, 0))
        self.assertEqual(zo.block_2x2_inertia_q(Fraction(-2), Fraction(1), Fraction(-2)), (0, 2, 0))
        self.assertEqual(zo.block_2x2_inertia_q(Fraction(1), Fraction(1), Fraction(1)), (1, 0, 1))
        self.assertEqual(zo.block_2x2_inertia_q(Fraction(-1), Fraction(1), Fraction(-1)), (0, 1, 1))

        # D block guards (incl. S17-BUG-01 direct-API shape/type/symmetry + band + overlap)
        for bad_d in (None, "x", 123, 1.5, []):
            self._assert_err("D_EMPTY_OR_BAD_TYPE", zo.d_block_inertia_q, bad_d)
        self._assert_err("D_NOT_SQUARE", zo.d_block_inertia_q, [None])
        self._assert_err("D_NOT_SQUARE", zo.d_block_inertia_q, [[Fraction(1), Fraction(2)]])
        self._assert_err("D_ENTRY_NOT_FRACTION", zo.d_block_inertia_q, [[True]])
        self._assert_err("D_ENTRY_NOT_FRACTION", zo.d_block_inertia_q, [[1]])
        self._assert_err("D_NOT_SYMMETRIC", zo.d_block_inertia_q, [[Fraction(0), Fraction(1)], [Fraction(0), Fraction(0)]])
        self._assert_err("D_NOT_SYMMETRIC", zo.d_block_inertia_q, [[Fraction(1), Fraction(10)], [Fraction(-10), Fraction(1)]])
        d_max = [[Fraction(1) if i == j else Fraction(0) for j in range(zo.MAX_MATRIX_DIM)] for i in range(zo.MAX_MATRIX_DIM)]
        self.assertEqual(zo.d_block_inertia_q(d_max), (zo.MAX_MATRIX_DIM, 0, 0))
        d_over = [[Fraction(0) for _ in range(zo.MAX_MATRIX_DIM + 1)] for _ in range(zo.MAX_MATRIX_DIM + 1)]
        self._assert_err("D_DIM_EXCEEDED", zo.d_block_inertia_q, d_over)
        D_band = [[Fraction(0), Fraction(0), Fraction(1)], [Fraction(0), Fraction(0), Fraction(0)], [Fraction(1), Fraction(0), Fraction(0)]]
        self._assert_err("D_OUTSIDE_BAND", zo.d_block_inertia_q, D_band)
        D_overlap = [[Fraction(1), Fraction(1), Fraction(0)], [Fraction(1), Fraction(1), Fraction(1)], [Fraction(0), Fraction(1), Fraction(1)]]
        self._assert_err("D_OVERLAPPING_BLOCKS", zo.d_block_inertia_q, D_overlap)

        # verify_pldl_certificate_q fail-closed guards (incl. S17-BUG-03 mixed-type keys)
        valid = zo.bunch_kaufman_factor_q([[0, 1], [1, 0]])
        self.assertEqual(zo.verify_pldl_certificate_q(valid), (1, 1, 0))
        valid_no_claim = {k: v for k, v in valid.items() if k != "claim"}
        self.assertEqual(zo.verify_pldl_certificate_q(valid_no_claim), (1, 1, 0))

        self._assert_err("CERT_NOT_DICT", zo.verify_pldl_certificate_q, [])
        self._assert_err("CERT_NON_STRING_KEY", zo.verify_pldl_certificate_q, {**valid, 2: "bad"})
        self._assert_err("CERT_KEYS_MISMATCH", zo.verify_pldl_certificate_q, {**valid, "extra": 1})
        self._assert_err("INVALID_PERMUTATION_LEN", zo.verify_pldl_certificate_q, {**valid, "P": [0]})
        self._assert_err("INVALID_PERMUTATION_LEN", zo.verify_pldl_certificate_q, {**valid, "P": "01"})
        self._assert_err("INVALID_PERMUTATION_DUP", zo.verify_pldl_certificate_q, {**valid, "P": [0, 0]})
        self._assert_err("MATRIX_DIM_MISMATCH", zo.verify_pldl_certificate_q, {**valid, "L": [["1"]]})
        self._assert_err("MATRIX_DIM_MISMATCH", zo.verify_pldl_certificate_q, {**valid, "L": [["1", "0"]]})
        self._assert_err("MATRIX_DIM_MISMATCH", zo.verify_pldl_certificate_q, {**valid, "L": 123})
        self._assert_err("MATRIX_DIM_MISMATCH", zo.verify_pldl_certificate_q, {**valid, "L": "bad"})
        self._assert_err("MATRIX_DIM_MISMATCH", zo.verify_pldl_certificate_q, {**valid, "L": [["1"], ["0", "1"]]})
        self._assert_err("MATRIX_DIM_MISMATCH", zo.verify_pldl_certificate_q, {**valid, "L": ["bad", ["0", "1"]]})
        self._assert_err("L_NOT_UNIT", zo.verify_pldl_certificate_q, {**valid, "L": [["2", "0"], ["0", "1"]]})
        self._assert_err("L_NOT_LOWER", zo.verify_pldl_certificate_q, {**valid, "L": [["1", "1"], ["0", "1"]]})
        self._assert_err("D_DIM_MISMATCH", zo.verify_pldl_certificate_q, {**valid, "D": [["1"]]})
        self._assert_err("PLDL_IDENTITY_FAIL", zo.verify_pldl_certificate_q, {**valid, "D": [["1", "0"], ["0", "1"]]})
        self._assert_err("INVALID_CLAIM_SHAPE", zo.verify_pldl_certificate_q, {**valid, "claim": [1, 1]})
        self._assert_err("INVALID_CLAIM_SHAPE", zo.verify_pldl_certificate_q, {**valid, "claim": "bad"})
        self._assert_err("CLAIM_MISMATCH", zo.verify_pldl_certificate_q, {**valid, "claim": [2, 0, 0]})

        # translate_pldl_dialect with and without claim
        t_no_claim = zo.translate_pldl_dialect(valid_no_claim, "loom7_margin")
        self.assertNotIn("claim", t_no_claim)
        self.assertEqual(zo.verify_pldl_certificate_q(t_no_claim, dialect="loom7_margin"), (1, 1, 0))

        # Cayley-Hamilton check (valid and tampered)
        Z2 = [[0, 1], [1, 0]]
        self.assertTrue(zo.cayley_hamilton_holds_q(Z2, [Fraction(1), Fraction(0), Fraction(-1)]))
        self.assertFalse(zo.cayley_hamilton_holds_q(Z2, [Fraction(1), Fraction(0), Fraction(1)]))
        self._assert_err("INVALID_CHARPOLY_LEN", zo.cayley_hamilton_holds_q, Z2, [Fraction(1)])
        self._assert_err("INVALID_CHARPOLY_LEN", zo.cayley_hamilton_holds_q, Z2, "bad")

        # 1x1 and larger zero-diag / non-zero-diag factorization coverage
        self.assertEqual(zo.verify_pldl_certificate_q(zo.bunch_kaufman_factor_q([[0]])), (0, 0, 1))
        self.assertEqual(zo.verify_pldl_certificate_q(zo.bunch_kaufman_factor_q([[-3]])), (0, 1, 0))
        # Matrix forcing swap_rc with done_cols > 0 (diag pivot at k=0, then zero-diag 2x2 block at k=1,2, then trailing col at 3)
        M4_mix = [[2, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0]]
        self.assertEqual(
            zo.verify_pldl_certificate_q(zo.bunch_kaufman_factor_q(M4_mix)),
            zo.independent_charpoly_descartes_inertia_q(M4_mix),
        )
        # Matrix with zero diagonal at k=0,1 and nonzero entry coupling to k=2 (tests L update after 2x2 block!)
        M3_chain = [[0, 1, 2], [1, 0, 3], [2, 3, 0]]
        self.assertEqual(
            zo.verify_pldl_certificate_q(zo.bunch_kaufman_factor_q(M3_chain)),
            zo.independent_charpoly_descartes_inertia_q(M3_chain),
        )

        # Full Pillar 2 zero-diag audit
        p2z = zo.audit_zero_diagonal_and_blocks()
        self.assertTrue(all(r["expected_matched"] and r["raw_cross_dialect_rejected"] for r in p2z["zero_diagonal_matrices"]))
        self.assertTrue(all(r["verified"] for r in p2z["block_2x2_five_row_table"]))

    def test_04_fibral_truss_and_loom7_bounds(self) -> None:
        # Truss boundary guards
        self._assert_err("TRUSS_NONPOSITIVE_LENGTH", zo.truss_hessian_congruent_q, Fraction(0), Fraction(1))
        self._assert_err("TRUSS_NONPOSITIVE_LENGTH", zo.truss_hessian_congruent_q, Fraction(1), Fraction(0))
        self._assert_err("TRUSS_TRIANGLE_VIOLATED", zo.truss_hessian_congruent_q, Fraction(3), Fraction(1))
        # Boundary s == 2 -> on-line singular Hessian
        self.assertEqual(zo.truss_hessian_congruent_q(Fraction(1), Fraction(1)), [[Fraction(2), Fraction(0)], [Fraction(0), Fraction(0)]])

        truss = zo.audit_fibral_rigidity_truss()
        self.assertEqual(truss["verified_box"], [["7/10", "13/10"], ["9/10", "3/2"]])
        self.assertTrue(all(c["dual_oracle_pd"] for c in truss["corners"]))
        self.assertTrue(truss["non_convexity_segment"]["segment_exact_match"])
        self.assertTrue(truss["non_convexity_segment"]["interior_has_zero_pd_equilibria_in_R2"])
        self.assertEqual(truss["interior_four_region_proof"]["region_between_pins_root_x"], "-1/10")
        self.assertEqual(truss["interior_four_region_proof"]["region_left_of_pin_root_x"], "-109/100")
        self.assertEqual(truss["interior_four_region_proof"]["region_right_of_pin_candidate_x"], "89/100")
        self.assertTrue(truss["matrix_convex_combination_pd"])
        self.assertTrue(truss["near_flat_1e_minus_9_pd"])

        # Rank bounds edge & guard coverage
        self._assert_err("NONPOSITIVE_FROB_SQ", zo.compute_rank_bounds_q, Fraction(1), Fraction(0), Fraction(0), 0)
        self._assert_err("INFEASIBLE_TRACE_TUPLE", zo.compute_rank_bounds_q, Fraction(1), Fraction(2), Fraction(4), 1)
        # u <= 0 and u + t <= 0 -> R_opt == 0
        self.assertEqual(zo.compute_rank_bounds_q(Fraction(0), Fraction(2), Fraction(4), 1)["R_opt"], Fraction(0))
        self.assertEqual(zo.compute_rank_bounds_q(Fraction(1), Fraction(-1), Fraction(2), 0)["R_opt"], Fraction(0))
        # Regime 2 clamped to 0 when (u+t)^2/S - b <= 0
        self.assertEqual(zo.compute_rank_bounds_q(Fraction(1), Fraction(0), Fraction(2), 1)["R_opt"], Fraction(0))
        # Boundary t == b > 0 and t * (u + t) == b * S
        b_eq = zo.compute_rank_bounds_q(Fraction(1), Fraction(1), Fraction(2), 1)
        self.assertEqual(b_eq["R_G"], Fraction(1))
        self.assertEqual(b_eq["R_opt"], Fraction(1))
        # Regime where b > 0, t > 0, t*(u+t) < b*S (falls to else branch)
        b_low = zo.compute_rank_bounds_q(Fraction(2), Fraction(1, 2), Fraction(5), 1)
        self.assertEqual(b_low["R_opt"], Fraction(1, 4))

        l7 = zo.audit_loom7_rank_and_adapter_bounds()
        self.assertTrue(all(r["chain_and_identities_verified"] for r in l7["rank_bound_witnesses"]))
        self.assertTrue(l7["forged_b_overshoots_true_rank_2"])
        self.assertTrue(all(a["equivalence_and_bracket_verified"] for a in l7["adapter_spectral_equivalences"]))
        f5 = l7["adapter_five_case_forgery"]
        self.assertTrue(f5["replay_old_cert_blocked_by_recomputation"])
        self.assertEqual(f5["fresh_cert_old_bound_inertia"], [0, 2, 0])
        self.assertTrue(f5["tampered_claim_rejected"])
        self.assertTrue(f5["old_LD_under_new_M_rejected"])
        self.assertEqual(f5["fresh_cert_64s_inertia"], [2, 0, 0])

    # ------------------------------------------------------------------
    # 4. Pillar 3: Gate-Axiom Witnesses (All 5 Hardened Operators + Bounds)
    # ------------------------------------------------------------------
    def test_05_gate_axiom_witnesses_and_hardened_operators(self) -> None:
        # W1 warp#14
        self._assert_err("WARP14_CFG_NOT_DICT", zo.hardened_warp14_bool_config, [], "k")
        self._assert_err("INVALID_BOOL_TYPE", zo.hardened_warp14_bool_config, {}, "k", default=1)
        self.assertIs(zo.hardened_warp14_bool_config({}, "k", default=False), False)

        # W3 fractals#58 positive/negative/zero exponents & boundary checks
        self._assert_err("FRACTALS58_NONPOSITIVE_DATA", zo.hardened_fractals58_exponent_in, 0, 2, 1, 2, 0, 1)
        self._assert_err("FRACTALS58_NONPOSITIVE_DATA", zo.hardened_fractals58_exponent_in, 1, 0, 1, 2, 0, 1)
        self._assert_err("FRACTALS58_NONPOSITIVE_DATA", zo.hardened_fractals58_exponent_in, 1, 2, 0, 2, 0, 1)
        self._assert_err("FRACTALS58_NONPOSITIVE_DATA", zo.hardened_fractals58_exponent_in, 1, 2, 1, 0, 0, 1)
        self._assert_err("FRACTALS58_NON_INCREASING_SCALE", zo.hardened_fractals58_exponent_in, 2, 2, 1, 1, 0, 1)
        self._assert_err("FRACTALS58_NON_INCREASING_SCALE", zo.hardened_fractals58_exponent_in, 4, 2, 16, 4, 1, 3)
        self._assert_err("FRACTALS58_INVERTED_BRACKET", zo.hardened_fractals58_exponent_in, 1, 2, 1, 4, 3, 2)
        # Exact boundary equality lo == hi == slope (including negative slope -1 and zero slope 0)
        self.assertTrue(zo.hardened_fractals58_exponent_in(1, 2, 1, 4, 2, 2))
        self.assertTrue(zo.hardened_fractals58_exponent_in(1, 2, 4, 2, -1, -1))
        self.assertTrue(zo.hardened_fractals58_exponent_in(1, 2, 3, 3, 0, 0))
        self.assertFalse(zo.hardened_fractals58_exponent_in(1, 2, 1, 8, 1, 2))
        self.assertFalse(zo.hardened_fractals58_exponent_in(1, 2, 1, 2, 2, 3))

        # W4 loom#9 safe rational mutant
        self._assert_err("LOOM9_NON_STR_TOKEN", zo.hardened_loom9_safe_rational_mutant, 123)
        self.assertEqual(zo.hardened_loom9_safe_rational_mutant("not-a-frac"), [])
        self.assertEqual(zo.hardened_loom9_safe_rational_mutant("1/0"), [])
        self.assertEqual(zo.hardened_loom9_safe_rational_mutant("9" * (zo.MAX_RATIONAL_DIGITS + 1) + "/1"), [])
        self.assertEqual(zo.hardened_loom9_safe_rational_mutant("1/" + "9" * (zo.MAX_RATIONAL_DIGITS + 1)), [])
        self.assertEqual(len(zo.hardened_loom9_safe_rational_mutant("1" + "0" * (zo.MAX_RATIONAL_DIGITS - 1) + "/1")), 1)
        self.assertEqual(
            zo.hardened_loom9_safe_rational_mutant("-1/4"),
            [("rational-as-fixed-decimal-string", "-0.2500")],
        )
        self.assertEqual(
            zo.hardened_loom9_safe_rational_mutant("0/5"),
            [("rational-as-fixed-decimal-string", "0.0000")],
        )

        # W5 formal-claims-audit#19
        self._assert_err("FCA19_EMPTY_VERDICTS", zo.hardened_fca19_require_nonempty_verdicts, [])
        self._assert_err("FCA19_EMPTY_VERDICTS", zo.hardened_fca19_require_nonempty_verdicts, "VERIFIED")
        self._assert_err("FCA19_INVALID_VERDICT_ENTRY", zo.hardened_fca19_require_nonempty_verdicts, [123])
        self._assert_err("FCA19_INVALID_VERDICT_ENTRY", zo.hardened_fca19_require_nonempty_verdicts, ["   "])
        self.assertEqual(zo.hardened_fca19_require_nonempty_verdicts(("VERIFIED",)), 1)

        p3 = zo.audit_gate_axiom_witnesses()
        self.assertEqual(p3["witness_count"], 5)
        self.assertTrue(p3["all_witnesses_verified"])

    # ------------------------------------------------------------------
    # 5. Audit CLI, Fail-Closed `--check`, Symlinks & Tamper Controls
    # ------------------------------------------------------------------
    def test_06_certificate_check_cli_and_tamper_controls(self) -> None:
        cert = za.build_certificate()
        self.assertTrue(cert["payload"]["all_passed"])
        ok_res = za.verify_certificate_dict(cert)
        self.assertTrue(ok_res["valid"])

        # Dict-level tamper controls (incl. S17-BUG-03 mixed-type keys & S17-BUG-04 bool->int forgery!)
        self._assert_err("CERT_NOT_DICT", za.verify_certificate_dict, [])
        self._assert_err("CERT_NON_STRING_KEY", za.verify_certificate_dict, {1: "a", "schema": za.CERT_SCHEMA})
        self._assert_err("CERT_SCHEMA_KEYS", za.verify_certificate_dict, {**cert, "bogus": 1})
        self._assert_err("CERT_HEADER_MISMATCH", za.verify_certificate_dict, {**cert, "schema": "wrong"})
        self._assert_err("CERT_HEADER_MISMATCH", za.verify_certificate_dict, {**cert, "audit_id": "AUDIT-999"})
        self._assert_err("INVALID_PAYLOAD_SHA", za.verify_certificate_dict, {**cert, "payload_sha256": 123})
        self._assert_err("INVALID_PAYLOAD_SHA", za.verify_certificate_dict, {**cert, "payload_sha256": "abc"})
        self._assert_err("INVALID_PAYLOAD_SHA", za.verify_certificate_dict, {**cert, "payload_sha256": "Z" * 64})
        self._assert_err("INVALID_PAYLOAD_SHA", za.verify_certificate_dict, {**cert, "payload_sha256": "\u00e9" * 64})
        self._assert_err("PAYLOAD_SHA_MISMATCH", za.verify_certificate_dict, {**cert, "payload_sha256": "0" * 64})
        tampered_payload = copy.deepcopy(cert["payload"])
        tampered_payload["all_passed"] = False
        rehashed_sha = hashlib.sha256(zo.canonical_json_bytes_v21(tampered_payload)).hexdigest()
        self._assert_err(
            "RECOMPUTED_PAYLOAD_DRIFT",
            za.verify_certificate_dict,
            {**cert, "payload": tampered_payload, "payload_sha256": rehashed_sha},
        )

        # S17-BUG-04 regression: replacing all bools with 1/0 (Python True == 1) and re-signing MUST fail closed!
        def bools_to_ints(obj: object) -> object:
            if type(obj) is bool:
                return 1 if obj else 0
            if type(obj) is dict:
                return {k: bools_to_ints(v) for k, v in obj.items()}
            if type(obj) is list:
                return [bools_to_ints(v) for v in obj]
            return obj

        forged_int_payload = bools_to_ints(cert["payload"])
        forged_int_sha = hashlib.sha256(zo.canonical_json_bytes_v21(forged_int_payload)).hexdigest()
        forged_int_cert = {**cert, "payload": forged_int_payload, "payload_sha256": forged_int_sha}
        self._assert_err("RECOMPUTED_PAYLOAD_DRIFT", za.verify_certificate_dict, forged_int_cert)

        # File-level checks (valid with & without trailing \n, CRLF, bad UTF-8, non-canonical, symlink target/parent, missing)
        self._assert_err("INVALID_PATH_TYPE", za.check_certificate_file, "not_a_path")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cert_path = root / "cert.json"
            wr = za.write_certificate_file(cert_path)
            self.assertEqual(wr["payload_sha256"], cert["payload_sha256"])

            # Exact canonical bytes without trailing newline also accepted
            bare_path = root / "bare.json"
            bare_path.write_bytes(zo.canonical_json_bytes_v21(cert))
            self.assertTrue(za.check_certificate_file(bare_path)["valid"])

            # Missing file & directory rejected
            self._assert_err("CERT_FILE_NOT_FOUND", za.check_certificate_file, root / "missing.json")
            self._assert_err("CERT_FILE_NOT_FOUND", za.check_certificate_file, root)
            # Deep nesting JSON file rejected cleanly (S17-BUG-05)
            deep_path = root / "deep_1200.json"
            deep_path.write_bytes(("[" * 1200 + "]" * 1200).encode("ascii"))
            self._assert_err("JSON_DEPTH_EXCEEDED", za.check_certificate_file, deep_path)
            # CRLF rejected
            crlf_path = root / "crlf.json"
            crlf_path.write_bytes(zo.canonical_json_bytes_v21(cert) + b"\r\n")
            self._assert_err("CRLF_FORBIDDEN", za.check_certificate_file, crlf_path)
            # Invalid UTF-8 rejected
            bad_utf8 = root / "bad_utf8.json"
            bad_utf8.write_bytes(b"\xff\xfe")
            self._assert_err("INVALID_UTF8", za.check_certificate_file, bad_utf8)
            # Non-canonical JSON (extra whitespace) rejected
            pretty_path = root / "pretty.json"
            pretty_path.write_bytes(b" " + zo.canonical_json_bytes_v21(cert) + b"\n")
            self._assert_err("NON_CANONICAL_CERT_BYTES", za.check_certificate_file, pretty_path)
            # Symlink target rejected
            sym_file = root / "sym_cert.json"
            os.symlink(cert_path, sym_file)
            self._assert_err("SYMLINK_FORBIDDEN", za.check_certificate_file, sym_file)
            # Symlink ancestor directory rejected
            real_sub = root / "real_sub"
            real_sub.mkdir()
            (real_sub / "c.json").write_bytes(zo.canonical_json_bytes_v21(cert) + b"\n")
            sym_dir = root / "sym_dir"
            os.symlink(real_sub, sym_dir)
            self._assert_err("SYMLINK_ANCESTOR_FORBIDDEN", za.check_certificate_file, sym_dir / "c.json")

            # CLI paths: --write, --check (valid, non-canonical, bool->int forged), --standalone --json, plain summary
            forged_path = root / "forged_int_bool.json"
            forged_path.write_bytes(zo.canonical_json_bytes_v21(forged_int_cert) + b"\n")
            out_buf = io.StringIO()
            err_buf = io.StringIO()
            cli_cert = root / "cli_cert.json"
            with mock.patch("sys.stdout", out_buf), mock.patch("sys.stderr", err_buf):
                self.assertEqual(za.main(["--write", str(cli_cert)]), 0)
                self.assertEqual(za.main(["--check", str(cli_cert)]), 0)
                self.assertEqual(za.main(["--check", str(pretty_path)]), 1)
                self.assertEqual(za.main(["--check", str(forged_path)]), 1)
                self.assertEqual(za.main(["--standalone"]), 0)
            self.assertIn("REJECT NON_CANONICAL_CERT_BYTES", err_buf.getvalue())
            self.assertIn("REJECT RECOMPUTED_PAYLOAD_DRIFT", err_buf.getvalue())

            raw_out = io.BytesIO()
            fake_stdout = mock.Mock()
            fake_stdout.buffer = raw_out
            with mock.patch("sys.stdout", fake_stdout):
                self.assertEqual(za.main(["--standalone", "--json"]), 0)
            self.assertEqual(raw_out.getvalue(), zo.canonical_json_bytes_v21(cert) + b"\n")


if __name__ == "__main__":
    unittest.main()
