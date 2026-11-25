#!/usr/bin/env python3
"""
Track S20c R5 Verification & Zone-B Adversarial Test Suite.

Zero bare `assert` statements; zero IEEE-754 floats on trust paths;
independent zero-shared-code brute-force cross-checks for HVG, SEAM-1,
3x3 Sylvester inertia, Jury stability, WHT-256, Stage-A ingestion,
and complete Zone-B / CLI / mutant coverage.
"""
from __future__ import annotations

import copy
from decimal import Decimal
from fractions import Fraction
import hashlib
import inspect
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import physical_telemetry_audit as audit_cli
import physical_telemetry_oracle as oracle


class _IntSub(int):
    pass


class _StrSub(str):
    pass


class _ListSub(list):
    pass


class _DictSub(dict):
    pass


class _FracSub(Fraction):
    pass


def _brute_force_hvg_edges(seq: tuple[int, ...]) -> int:
    """Independent O(N^3) Horizontal Visibility Graph edge counter (zero shared code)."""
    n = len(seq)
    edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            cap = min(seq[i], seq[j])
            visible = True
            for k in range(i + 1, j):
                if seq[k] >= cap:
                    visible = False
                    break
            if visible:
                edges += 1
    return edges


def _brute_force_invert_3x3_q(m: list[list[Fraction]]) -> list[list[Fraction]]:
    """Independent Gauss-Jordan inverse over Q for 3x3 matrices (zero shared code)."""
    aug = [m[i][:] + [Fraction(1 if i == j else 0) for j in range(3)] for i in range(3)]
    for col in range(3):
        piv = col
        while aug[piv][col] == 0:
            piv += 1
        aug[col], aug[piv] = aug[piv], aug[col]
        scale = aug[col][col]
        aug[col] = [x / scale for x in aug[col]]
        for r in range(3):
            if r != col and aug[r][col] != 0:
                fac = aug[r][col]
                aug[r] = [aug[r][c] - fac * aug[col][c] for c in range(6)]
    return [row[3:] for row in aug]


def _brute_force_op1_seam1(centered: tuple[int, ...], window_w: int) -> dict[str, object]:
    """Independent pure-Q SEAM-1 reference implementation (zero shared code)."""
    n = len(centered)
    scale_c = Fraction(n - 1, 1)
    lam = scale_c * scale_c
    us = [[scale_c, Fraction(centered[t], 1), Fraction(centered[t - 1], 1)] for t in range(1, n)]
    hs: list[Fraction] = []
    max_h = Fraction(-1, 1)
    max_idx = -1
    for idx in range(window_w, len(us)):
        g = [[lam if i == j else Fraction(0, 1) for j in range(3)] for i in range(3)]
        for s in range(idx - window_w, idx):
            u = us[s]
            for i in range(3):
                for j in range(3):
                    g[i][j] += u[i] * u[j]
        ginv = _brute_force_invert_3x3_q(g)
        u = us[idx]
        q = sum(u[i] * ginv[i][j] * u[j] for i in range(3) for j in range(3))
        h = q / (Fraction(1, 1) + q)
        hs.append(h)
        if h > max_h:
            max_h = h
            max_idx = idx + 1
    med_h = sorted(hs)[len(hs) // 2]
    return {
        "steps": len(hs),
        "max_leverage_index": max_idx,
        "max_h": max_h,
        "median_h": med_h,
        "shock_ratio": max_h / med_h,
    }


def _rehash_cert(cert: dict[str, object]) -> dict[str, object]:
    out = copy.deepcopy(cert)
    payload_sha = oracle.sha256_canonical(out["payload"])
    out["payload_sha256"] = payload_sha
    out["certificate_sha256"] = oracle.sha256_canonical(
        {
            "schema_version": out["schema_version"],
            "track_id": out["track_id"],
            "payload_sha256": payload_sha,
        }
    )
    return out


class TestA_ConstantsAndPrimitives(unittest.TestCase):
    """Fast constant pins and Zone-B primitive hardening tests."""

    def test_constants_and_defaults_pinned(self) -> None:
        self.assertEqual(oracle.SCHEMA_VERSION, "s20c-physical-telemetry-cert/v1")
        self.assertEqual(oracle.TRACK_ID, "TRACK-S20C")
        self.assertEqual(oracle.MAX_JSON_DEPTH, 64)
        self.assertEqual(oracle.MAX_JSON_BYTES, 2_000_000)
        self.assertEqual(oracle.MAX_INT_BITS, 2048)
        self.assertEqual(oracle.MAX_INT_DIGITS, 620)
        self.assertEqual(oracle.MAX_SEQ_LEN, 4096)
        self.assertEqual(oracle.WINDOW_LEN, 256)
        self.assertEqual(oracle.TOTAL_SAMPLES, 512)
        self.assertEqual(oracle.SEAM1_WINDOW, 32)
        self.assertEqual(oracle.SURROGATE_COUNT, 99)
        self.assertEqual(oracle.BLOCK_SIZE, 16)
        self.assertEqual(oracle.ALPHA_NUM, 5)
        self.assertEqual(oracle.ALPHA_DEN, 100)
        self.assertEqual(oracle._STREAM_IDS, ("STREAM_A", "STREAM_B", "STREAM_C", "STREAM_D"))
        self.assertEqual(oracle._NULL_FAMILIES, ("IID_PERM", "BLOCK_16", "WHT_PHASE"))
        self.assertEqual(
            oracle._HYPOTHESIS_IDS,
            (
                "H1_SEAM1_SHOCK",
                "H2a_SEAM3_HVG_BETTI1",
                "H2b_SEAM3_IRREV_PHI",
                "H3a_F3_TRANSIENT_WITNESS",
                "H3b_F3_COMMUTATOR",
            ),
        )
        for fn in (
            oracle.evaluate_series_against_surrogates,
            oracle.run_known_answer_controls,
            oracle.build_certificate,
            oracle.validate_certificate_payload,
        ):
            self.assertEqual(inspect.signature(fn).parameters["surrogate_count"].default, 99)

    def test_require_int_and_bool_zone_b(self) -> None:
        self.assertEqual(oracle.require_int(0, lo=0, hi=0), 0)
        max_ok = (1 << oracle.MAX_INT_BITS) - 1
        self.assertEqual(oracle.require_int(max_ok), max_ok)
        self.assertEqual(oracle.require_int(-max_ok), -max_ok)

        for bad in (True, False, 1.0, "1", _IntSub(1), None):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_int(bad)
            self.assertEqual(ctx.exception.code, "INVALID_INT_TYPE")

        for huge in (1 << oracle.MAX_INT_BITS, -(1 << oracle.MAX_INT_BITS), 10**5000):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_int(huge)
            self.assertEqual(ctx.exception.code, "INT_BIT_LIMIT")

        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_int(4, lo=5)
        self.assertEqual(ctx.exception.code, "INT_BELOW_MIN")

        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_int(5, lo=10**5000)
        self.assertEqual(ctx.exception.code, "INT_BELOW_MIN")

        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_int(6, hi=5)
        self.assertEqual(ctx.exception.code, "INT_ABOVE_MAX")

        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_int(5, hi=-(10**5000))
        self.assertEqual(ctx.exception.code, "INT_ABOVE_MAX")

        for bad_bound in (True, _IntSub(1), "1"):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_int(5, lo=bad_bound)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "INVALID_INT_BOUND")
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_int(5, hi=bad_bound)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "INVALID_INT_BOUND")

        self.assertIs(oracle.require_bool(True), True)
        self.assertIs(oracle.require_bool(False), False)
        for bad in (1, 0, "true", None):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_bool(bad)
            self.assertEqual(ctx.exception.code, "INVALID_BOOL_TYPE")

    def test_require_str_seq_mapping_hex_and_fractions(self) -> None:
        self.assertEqual(oracle.require_str("a", min_len=1, max_len=1), "a")
        for bad in (1, _StrSub("a"), b"a"):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_str(bad)
            self.assertEqual(ctx.exception.code, "INVALID_STR_TYPE")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_str("\ud800")
        self.assertEqual(ctx.exception.code, "INVALID_UTF8")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_str("", min_len=1)
        self.assertEqual(ctx.exception.code, "STR_TOO_SHORT")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_str("ab", max_len=1)
        self.assertEqual(ctx.exception.code, "STR_TOO_LONG")

        self.assertEqual(oracle.require_seq([1, 2], min_len=2, max_len=2), (1, 2))
        self.assertEqual(oracle.require_seq((1,), min_len=1, max_len=1), (1,))
        for bad in ("ab", {1, 2}, _ListSub([1])):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_seq(bad)
            self.assertEqual(ctx.exception.code, "INVALID_SEQ_TYPE")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_seq([], min_len=1)
        self.assertEqual(ctx.exception.code, "SEQ_TOO_SHORT")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_seq([1, 2], max_len=1)
        self.assertEqual(ctx.exception.code, "SEQ_TOO_LONG")

        self.assertEqual(oracle.require_mapping({"k": 1}), {"k": 1})
        for bad in ([], _DictSub({"a": 1})):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_mapping(bad)
            self.assertEqual(ctx.exception.code, "INVALID_MAPPING_TYPE")
        for bad in ({1: "a"}, {_StrSub("k"): 1}):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_mapping(bad)
            self.assertEqual(ctx.exception.code, "NON_STR_KEY")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_mapping({"\ud800": 1})
        self.assertEqual(ctx.exception.code, "INVALID_UTF8")

        good_hex = "0123456789abcdef" * 4
        other_hex = "fedcba9876543210" * 4
        self.assertEqual(oracle.require_hex64_ascii(good_hex), good_hex)
        self.assertTrue(oracle.constant_time_hex64_equal(good_hex, good_hex))
        self.assertFalse(oracle.constant_time_hex64_equal(good_hex, other_hex))
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_hex64_ascii(123)
        self.assertEqual(ctx.exception.code, "INVALID_DIGEST_TYPE")
        for bad_len in ("0" * 63, "0" * 65):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_hex64_ascii(bad_len)
            self.assertEqual(ctx.exception.code, "INVALID_DIGEST_LEN")
        for bad_ch in ("A" + "0" * 63, "é" + "0" * 63, "\ud800" + "0" * 63, "g" + "0" * 63):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_hex64_ascii(bad_ch)
            self.assertEqual(ctx.exception.code, "INVALID_DIGEST_HEX")

        max_ok = (1 << oracle.MAX_INT_BITS) - 1
        self.assertEqual(oracle.fmt_q(Fraction(7, 1)), "7")
        self.assertEqual(oracle.fmt_q(Fraction(-5, 7)), "-5/7")
        self.assertEqual(oracle.fmt_q(Fraction(max_ok, 1)), str(max_ok))
        self.assertEqual(oracle.fmt_q(Fraction(1, max_ok)), f"1/{max_ok}")
        for bad in (1, "1/2", _FracSub(1, 2)):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.fmt_q(bad)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "INVALID_FRACTION_TYPE")
        for huge_q in (Fraction(1 << oracle.MAX_INT_BITS, 1), Fraction(1, 1 << oracle.MAX_INT_BITS)):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.fmt_q(huge_q)
            self.assertEqual(ctx.exception.code, "FRACTION_BIT_LIMIT")

        self.assertEqual(oracle.parse_q_str("42"), Fraction(42, 1))
        self.assertEqual(oracle.parse_q_str("-5/7"), Fraction(-5, 7))
        self.assertEqual(oracle.parse_q_str("0" * 619 + "1"), Fraction(1, 1))
        self.assertEqual(oracle.parse_q_str(str(max_ok)), Fraction(max_ok, 1))
        for bad_den in ("1/0", "1/-3"):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.parse_q_str(bad_den)
            self.assertEqual(ctx.exception.code, "INVALID_FRACTION_DEN")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_q_str("1/2/3")
        self.assertEqual(ctx.exception.code, "INVALID_FRACTION_STR")
        for bad_tok in ("-", "١٢٣", "12a", "/2", "1/"):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.parse_q_str(bad_tok)
            self.assertEqual(ctx.exception.code, "INVALID_INT_TOKEN")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_q_str("0" * 620 + "1")
        self.assertEqual(ctx.exception.code, "INT_DIGIT_LIMIT")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_q_str(str(1 << oracle.MAX_INT_BITS))
        self.assertEqual(ctx.exception.code, "INT_BIT_LIMIT")

    def test_json_validation_and_strict_parser_zone_b(self) -> None:
        nested_ok: object = 1
        for _ in range(4):
            nested_ok = [nested_ok]
        oracle.validate_json_value(nested_ok, max_depth=4)
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_json_value([nested_ok], max_depth=4)
        self.assertEqual(ctx.exception.code, "MAX_DEPTH_EXCEEDED")

        cyclic: list[object] = []
        cyclic.append(cyclic)
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_json_value(cyclic)
        self.assertEqual(ctx.exception.code, "MAX_DEPTH_EXCEEDED")

        oracle.validate_json_value({"a": [True, False, None, (1 << oracle.MAX_INT_BITS) - 1, "ok"]})
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_json_value({1: "x"})
        self.assertEqual(ctx.exception.code, "NON_STR_KEY")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_json_value({"\ud800": "x"})
        self.assertEqual(ctx.exception.code, "INVALID_UTF8")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_json_value({"a": "\ud800"})
        self.assertEqual(ctx.exception.code, "INVALID_UTF8")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_json_value({"a": 1 << oracle.MAX_INT_BITS})
        self.assertEqual(ctx.exception.code, "INT_BIT_LIMIT")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_json_value({"a": 1.5})
        self.assertEqual(ctx.exception.code, "FLOAT_FORBIDDEN")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_json_value({"a": {1, 2}})
        self.assertEqual(ctx.exception.code, "UNSUPPORTED_JSON_TYPE")

        self.assertEqual(oracle.parse_strict_json_text("[1,2]", require_object=False), [1, 2])
        self.assertEqual(oracle.parse_strict_json_text('{"b":1,"a":2}'), {"b": 1, "a": 2})
        self.assertEqual(oracle.canonical_json_bytes({"b": 1, "a": 2}), b'{"a":2,"b":1}')
        self.assertEqual(
            oracle.sha256_canonical({"b": 1, "a": 2}),
            hashlib.sha256(b'{"a":2,"b":1}').hexdigest(),
        )

        # Exact MAX_JSON_BYTES boundary passes, +1 byte fails
        exact_pad = "{}" + (" " * (oracle.MAX_JSON_BYTES - 2))
        self.assertEqual(oracle.parse_strict_json_text(exact_pad), {})
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_strict_json_text(exact_pad + " ")
        self.assertEqual(ctx.exception.code, "JSON_TOO_LARGE")

        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_strict_json_text(b"{}")  # type: ignore[arg-type]
        self.assertEqual(ctx.exception.code, "INVALID_JSON_INPUT")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_strict_json_text("   ")
        self.assertEqual(ctx.exception.code, "EMPTY_JSON_INPUT")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_strict_json_text('{"x":1.5}')
        self.assertEqual(ctx.exception.code, "JSON_FLOAT_FORBIDDEN")
        for tok in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.parse_strict_json_text(f'{{"x":{tok}}}')
            self.assertEqual(ctx.exception.code, "JSON_CONSTANT_FORBIDDEN")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_strict_json_text('{"a":1,"a":2}')
        self.assertEqual(ctx.exception.code, "JSON_DUPLICATE_KEY")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_strict_json_text("[1,2]", require_object=True)
        self.assertEqual(ctx.exception.code, "JSON_ROOT_NOT_OBJECT")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_strict_json_text("[1,2]", require_object=0)  # type: ignore[arg-type]
        self.assertEqual(ctx.exception.code, "INVALID_BOOL_TYPE")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_strict_json_text("{bad")
        self.assertEqual(ctx.exception.code, "JSON_PARSE_ERROR")
        deep_json = "[" * 2000 + "]" * 2000
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_strict_json_text(deep_json, require_object=False)
        self.assertIn(ctx.exception.code, ("MAX_DEPTH_EXCEEDED", "JSON_PARSE_ERROR"))

    def test_safe_path_and_file_loading_zone_b(self) -> None:
        class _EvilPath(type(Path())):
            pass

        for bad_path in ("/tmp/x", _EvilPath("/tmp/x")):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.require_safe_path(bad_path)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "INVALID_PATH_TYPE")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_safe_path(Path("bad\x00name"))
        self.assertEqual(ctx.exception.code, "INVALID_PATH_NUL")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.require_safe_path(Path("bad\ud800name"))
        self.assertEqual(ctx.exception.code, "INVALID_UTF8")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            real_file = root / "ok.json"
            real_file.write_bytes(b'{"a":1}\n')
            self.assertEqual(oracle.load_strict_json_file(real_file), {"a": 1})

            sym_file = root / "sym.json"
            sym_file.symlink_to(real_file)
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_safe_bytes(sym_file)
            self.assertEqual(ctx.exception.code, "SYMLINK_FORBIDDEN")

            real_dir = root / "sub"
            real_dir.mkdir()
            deep_dir = real_dir / "nested"
            deep_dir.mkdir()
            (real_dir / "f.json").write_bytes(b'{"k":1}\n')
            sym_dir = root / "sym_sub"
            sym_dir.symlink_to(real_dir)
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_safe_bytes(sym_dir / "f.json")
            self.assertEqual(ctx.exception.code, "SYMLINK_ANCESTOR_FORBIDDEN")

            # Relative paths with symlinked PWD or symlinked PWD ancestor must fail closed
            orig_cwd = os.getcwd()
            orig_pwd = os.environ.get("PWD")
            try:
                os.chdir(real_dir)
                os.environ["PWD"] = str(sym_dir)
                with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                    oracle.require_safe_path(Path("f.json"))
                self.assertEqual(ctx.exception.code, "SYMLINK_ANCESTOR_FORBIDDEN")

                os.chdir(deep_dir)
                os.environ["PWD"] = str(sym_dir / "nested")
                with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                    oracle.require_safe_path(Path("f.json"))
                self.assertEqual(ctx.exception.code, "SYMLINK_ANCESTOR_FORBIDDEN")

                # Stale symlinked PWD that does NOT match os.getcwd() must not falsely reject
                os.chdir(root)
                os.environ["PWD"] = str(sym_dir)
                self.assertEqual(oracle.require_safe_path(Path("ok.json")), Path("ok.json"))
            finally:
                os.chdir(orig_cwd)
                if orig_pwd is None:
                    os.environ.pop("PWD", None)
                else:
                    os.environ["PWD"] = orig_pwd

            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_safe_bytes(root / "does_not_exist.json")
            self.assertEqual(ctx.exception.code, "FILE_STAT_ERROR")

            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_safe_bytes(real_dir)
            self.assertEqual(ctx.exception.code, "NON_REGULAR_FILE")

            fifo_path = root / "pipe.fifo"
            os.mkfifo(fifo_path)
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_safe_bytes(fifo_path)
            self.assertEqual(ctx.exception.code, "NON_REGULAR_FILE")

            big_file = root / "big.bin"
            big_file.write_bytes(b"a" * oracle.MAX_JSON_BYTES)
            self.assertEqual(len(oracle.load_safe_bytes(big_file)), oracle.MAX_JSON_BYTES)
            big_file.write_bytes(b"a" * (oracle.MAX_JSON_BYTES + 1))
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_safe_bytes(big_file)
            self.assertEqual(ctx.exception.code, "FILE_TOO_LARGE")

            crlf_file = root / "crlf.json"
            crlf_file.write_bytes(b'{"a":1}\r\n')
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_strict_json_file(crlf_file)
            self.assertEqual(ctx.exception.code, "CR_FORBIDDEN")

            bad_utf8 = root / "bad_utf8.json"
            bad_utf8.write_bytes(b"\xff\xfe")
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_strict_json_file(bad_utf8)
            self.assertEqual(ctx.exception.code, "INVALID_UTF8")

            if os.geteuid() != 0:
                unreadable = root / "unreadable.json"
                unreadable.write_bytes(b"{}\n")
                unreadable.chmod(0o000)
                try:
                    with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                        oracle.load_safe_bytes(unreadable)
                    self.assertEqual(ctx.exception.code, "FILE_READ_ERROR")
                finally:
                    unreadable.chmod(0o600)


class TestB_StageAIngestionAndExactMath(unittest.TestCase):
    """Exact Stage-A ingestion, ranking, HVG, SEAM-1, inertia, Jury, and WHT tests."""

    def test_parse_decimal_to_scaled_int(self) -> None:
        self.assertEqual(oracle.parse_decimal_to_scaled_int(0, 60), 0)
        self.assertEqual(oracle.parse_decimal_to_scaled_int(7, 0), 7)
        self.assertEqual(oracle.parse_decimal_to_scaled_int(Decimal("1.25"), 2), 125)
        self.assertEqual(oracle.parse_decimal_to_scaled_int(Decimal("1." + "0" * 99 + "0"), 0), 1)
        self.assertEqual(oracle.parse_decimal_to_scaled_int("0e999999", 0), 0)
        self.assertEqual(oracle.parse_decimal_to_scaled_int(" -2.5e-19 ", 40), -25 * (10**20))
        self.assertEqual(oracle.parse_decimal_to_scaled_int("1", 60), 10**60)

        # S20C-DS-01 regressions: 101-digit Decimal cannot silently round; 1e999999 cannot DoS/overflow
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_decimal_to_scaled_int(Decimal("1." + "0" * 99 + "1"), 0)
        self.assertEqual(ctx.exception.code, "PRECISION_LOSS")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_decimal_to_scaled_int("1e999999", 0)
        self.assertEqual(ctx.exception.code, "INT_DIGIT_LIMIT")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_decimal_to_scaled_int("1e620", 0)
        self.assertEqual(ctx.exception.code, "INT_DIGIT_LIMIT")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_decimal_to_scaled_int("1e619", 0)
        self.assertEqual(ctx.exception.code, "INT_BIT_LIMIT")
        self.assertEqual(oracle.parse_decimal_to_scaled_int("1e616", 0), 10**616)
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_decimal_to_scaled_int(10**600, 30)
        self.assertEqual(ctx.exception.code, "INT_BIT_LIMIT")

        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_decimal_to_scaled_int(1.25, 2)
        self.assertEqual(ctx.exception.code, "INVALID_SAMPLE_TYPE")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_decimal_to_scaled_int("not-a-num", 2)
        self.assertEqual(ctx.exception.code, "INVALID_DECIMAL")
        for non_fin in (Decimal("NaN"), Decimal("Infinity"), "NaN", "-Infinity"):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.parse_decimal_to_scaled_int(non_fin, 2)
            self.assertEqual(ctx.exception.code, "NON_FINITE_SAMPLE")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.parse_decimal_to_scaled_int("1.234", 2)
        self.assertEqual(ctx.exception.code, "PRECISION_LOSS")

    def test_load_stripped_physical_streams_and_tamper_guards(self) -> None:
        manifest, prereg, streams = oracle.load_stripped_physical_streams(_HERE)
        self.assertEqual(manifest["schema_version"], "s20c-fetch-manifest/v1")
        self.assertEqual(prereg["prereg_status"], "LOCKED_BEFORE_WINDOW_B_EVALUATION")
        self.assertEqual(set(streams.keys()), set(oracle._STREAM_IDS))
        for sid in oracle._STREAM_IDS:
            self.assertEqual(len(streams[sid]), 512)
            self.assertTrue(all(type(v) is int for v in streams[sid]))

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            shutil.copytree(_HERE / "raw_telemetry", tmp / "raw_telemetry")
            shutil.copy2(_HERE / "FETCH_MANIFEST.json", tmp / "FETCH_MANIFEST.json")
            shutil.copy2(_HERE / "PREREG_S20C.json", tmp / "PREREG_S20C.json")

            # 1. Tampered PREREG manifest pin
            bad_prereg = copy.deepcopy(prereg)
            bad_prereg["fetch_manifest_sha256"] = "0" * 64
            (tmp / "PREREG_S20C.json").write_bytes(oracle.canonical_json_bytes(bad_prereg) + b"\n")
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_stripped_physical_streams(tmp)
            self.assertEqual(ctx.exception.code, "MANIFEST_PIN_MISMATCH")

            def _write_manifest_and_pin(m_obj: dict[str, object]) -> None:
                m_raw = oracle.canonical_json_bytes(m_obj) + b"\n"
                (tmp / "FETCH_MANIFEST.json").write_bytes(m_raw)
                p_obj = copy.deepcopy(prereg)
                p_obj["fetch_manifest_sha256"] = hashlib.sha256(m_raw).hexdigest()
                (tmp / "PREREG_S20C.json").write_bytes(oracle.canonical_json_bytes(p_obj) + b"\n")

            # 2. Unsafe local_file paths (absolute & parent traversal)
            for bad_rel in ("/etc/passwd", "../raw_telemetry/gwosc_gw150914_h1_512.txt"):
                m_bad = copy.deepcopy(manifest)
                m_bad["sources"][0]["local_file"] = bad_rel
                _write_manifest_and_pin(m_bad)
                with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                    oracle.load_stripped_physical_streams(tmp)
                self.assertEqual(ctx.exception.code, "INVALID_LOCAL_PATH")

            # 3. Unknown stream_id
            m_unk = copy.deepcopy(manifest)
            m_unk["sources"][0]["stream_id"] = "STREAM_Z"
            _write_manifest_and_pin(m_unk)
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_stripped_physical_streams(tmp)
            self.assertEqual(ctx.exception.code, "UNKNOWN_STREAM_ID")

            # 4. Raw SHA mismatch
            _write_manifest_and_pin(manifest)
            raw_a = tmp / "raw_telemetry" / "gwosc_gw150914_h1_512.txt"
            orig_a = raw_a.read_bytes()
            raw_a.write_bytes(b"1.0\n2.0\n")
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_stripped_physical_streams(tmp)
            self.assertEqual(ctx.exception.code, "RAW_SHA_MISMATCH")

            # 5. Insufficient samples with valid SHA pin
            m_short = copy.deepcopy(manifest)
            m_short["sources"][0]["local_sha256"] = hashlib.sha256(b"1.0\n2.0\n").hexdigest()
            _write_manifest_and_pin(m_short)
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_stripped_physical_streams(tmp)
            self.assertEqual(ctx.exception.code, "INSUFFICIENT_SAMPLES")

            # 6. S20C-DS-03: corrupt raw telemetry (non-ASCII / missing JSON keys) wrapped as RAW_PARSE_ERROR
            raw_a.write_bytes(b"\xff\xfe\n")
            m_bad_a = copy.deepcopy(manifest)
            m_bad_a["sources"][0]["local_sha256"] = hashlib.sha256(b"\xff\xfe\n").hexdigest()
            _write_manifest_and_pin(m_bad_a)
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_stripped_physical_streams(tmp)
            self.assertEqual(ctx.exception.code, "RAW_PARSE_ERROR")
            raw_a.write_bytes(orig_a)

            raw_b = tmp / "raw_telemetry" / "usgs_geomag_bou_20240510.json"
            orig_b = raw_b.read_bytes()
            raw_b.write_bytes(b"{}")
            m_bad_b = copy.deepcopy(manifest)
            m_bad_b["sources"][1]["local_sha256"] = hashlib.sha256(b"{}").hexdigest()
            _write_manifest_and_pin(m_bad_b)
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.load_stripped_physical_streams(tmp)
            self.assertEqual(ctx.exception.code, "RAW_PARSE_ERROR")
            raw_b.write_bytes(orig_b)

    def test_doubled_mid_ranks_and_centering(self) -> None:
        self.assertEqual(oracle.doubled_mid_ranks((0, 1, 0, 1)), (1, 5, 1, 5))
        ranks = oracle.doubled_mid_ranks((5, 5, 10, 10, 20, 20))
        self.assertEqual(ranks, (1, 1, 5, 5, 9, 9))
        self.assertEqual(sum(ranks), 6 * 5)
        centered = oracle.center_doubled_ranks(ranks)
        self.assertEqual(centered, (-4, -4, 0, 0, 4, 4))
        self.assertEqual(sum(centered), 0)

        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.doubled_mid_ranks((7, 7, 7, 7))
        self.assertEqual(ctx.exception.code, "CONSTANT_SERIES")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.doubled_mid_ranks((1, 2, 3))
        self.assertEqual(ctx.exception.code, "SEQ_TOO_SHORT")

    def test_det_adj_median_and_op1_against_brute_force(self) -> None:
        mat = ((2, -1, 3), (0, 4, -2), (5, 1, 1))
        det, adj = oracle._det_adj_3x3_int(mat)
        self.assertEqual(det, 2 * (4 + 2) - (-1) * (0 + 10) + 3 * (0 - 20))
        for i in range(3):
            for j in range(3):
                entry = sum(mat[i][k] * adj[k][j] for k in range(3))
                self.assertEqual(entry, det if i == j else 0)

        pairs = [(3, 4), (1, 2), (2, 4), (5, 6), (1, 5), (2, 3), (1, 2)]
        ma, mb = oracle._exact_median_pair(pairs)
        self.assertEqual(Fraction(ma, mb), sorted(Fraction(a, b) for a, b in pairs)[len(pairs) // 2])
        # Also test tied 64-bit bucket fallback (all share floor key 0) with strictly smaller/equal/larger pivots
        b65 = 1 << 65
        tied_pairs = [(1, b65 + 5), (1, b65 + 1), (1, b65 + 3), (2, 2 * (b65 + 3)), (1, b65 + 2)]
        self.assertEqual(Fraction(*oracle._exact_median_pair(tied_pairs)), Fraction(1, b65 + 3))
        self.assertEqual(Fraction(*oracle._exact_median_pair([(1, b65 + 9), (1, b65 + 1), (1, b65 + 2)])), Fraction(1, b65 + 2))
        self.assertEqual(Fraction(*oracle._exact_median_pair([(1, b65 + 1), (1, b65 + 9), (1, b65 + 8)])), Fraction(1, b65 + 8))
        self.assertEqual(Fraction(*oracle._exact_median_pair([(9, 10), (1, 10), (2, 10)])), Fraction(2, 10))
        self.assertEqual(Fraction(*oracle._exact_median_pair([(1, 10), (9, 10), (8, 10)])), Fraction(8, 10))

        raw = tuple(((i * 29 + (i * i) % 13) % 47) - 23 for i in range(40))
        centered = oracle.center_doubled_ranks(oracle.doubled_mid_ranks(raw))
        got = oracle.op1_seam1_leverage_shock(centered, window_w=8)
        ref = _brute_force_op1_seam1(centered, window_w=8)
        self.assertEqual(got, ref)

        with self.assertRaises(oracle.TelemetryPortalError):
            oracle.op1_seam1_leverage_shock(centered, window_w=3)
        with self.assertRaises(oracle.TelemetryPortalError):
            oracle.op1_seam1_leverage_shock(centered, window_w=37)

    def test_op2_hvg_and_ordinal_against_brute_force(self) -> None:
        # Equal-height ties + strict peaks + monotone runs
        cases = [
            (3, 1, 3, 2, 3, 0, 5, 2, 2, 4),
            (10, 9, 8, 7, 6, 5, 4, 3),
            (1, 5, 2, 6, 3, 7, 4, 8, 4, 1),
        ]
        for seq in cases:
            res = oracle.op2_seam3_hvg_and_ordinal(seq)
            bf_edges = _brute_force_hvg_edges(seq)
            self.assertEqual(res["hvg_edges"], bf_edges)
            self.assertEqual(res["hvg_betti1"], bf_edges - (len(seq) - 1))
            self.assertTrue(res["forward_hvg_dag_grounded"])

        # Cover all 7 ordinal states (0..5 strict permutations + 6 for all 3 tie positions)
        # 0:(1,2,3), 1:(2,4,3), 2:(4,3,5)->wait explicit triples:
        seq_all = (1, 2, 4, 3, 6, 5, 2, 2, 3, 2, 4, 4, 1)
        res_all = oracle.op2_seam3_hvg_and_ordinal(seq_all)
        self.assertEqual(res_all["hvg_edges"], _brute_force_hvg_edges(seq_all))
        self.assertTrue(res_all["has_directed_cycle"])

        # Pure 3-cycle Farkas witness with ZERO 2-cycles: states [1, 4, 0, 1] -> [0, 1, 4, 0]
        seq_3cyc = (10, 50, 30, 40, 60, 50)
        res_3cyc = oracle.op2_seam3_hvg_and_ordinal(seq_3cyc)
        self.assertEqual(res_3cyc["farkas_directed_cycle_witness"], [0, 1, 4, 0])
        self.assertTrue(res_3cyc["has_directed_cycle"])
        self.assertEqual(res_3cyc["ordinal_phi_asym"], Fraction(1, 1))
        self.assertEqual(res_3cyc["ordinal_signed_net_flux"], 1)

        # Acyclic 2-edge chain (states [1, 4, 0], transitions 1->4, 4->0 only) -> no 3-cycle
        res_acyc = oracle.op2_seam3_hvg_and_ordinal((10, 50, 30, 40, 60))
        self.assertEqual(res_acyc["farkas_directed_cycle_witness"], [])
        self.assertFalse(res_acyc["has_directed_cycle"])

        # Constant ranks -> asym_den == 0, no directed cycle
        res_zero = oracle.op2_seam3_hvg_and_ordinal((0, 0, 0, 0))
        self.assertEqual(res_zero["ordinal_phi_asym"], Fraction(0, 1))
        self.assertEqual(res_zero["farkas_directed_cycle_witness"], [])
        self.assertFalse(res_zero["has_directed_cycle"])
        self.assertEqual(res_zero["hvg_edges"], 3)
        self.assertEqual(res_zero["hvg_betti1"], 0)

    def test_exact_inertia_schur_alpha_and_op3(self) -> None:
        def _q(rows: list[list[int]]) -> list[list[Fraction]]:
            return [[Fraction(x, 1) for x in r] for r in rows]

        self.assertEqual(oracle.exact_symmetric_inertia_3x3(_q([[2, 0, 0], [0, 3, 0], [0, 0, 5]])), (3, 0, 0))
        self.assertEqual(oracle.exact_symmetric_inertia_3x3(_q([[-1, 0, 0], [0, -4, 0], [0, 0, -9]])), (0, 3, 0))
        self.assertEqual(oracle.exact_symmetric_inertia_3x3(_q([[0, 0, 0], [0, 2, 1], [0, 1, -1]])), (1, 1, 1))
        self.assertEqual(oracle.exact_symmetric_inertia_3x3(_q([[0, 0, 0], [0, 0, 0], [0, 0, 0]])), (0, 0, 3))
        # Hyperbolic 2x2 block at (0, 1) with negative vs positive Schur complement onto (2, 2)
        self.assertEqual(oracle.exact_symmetric_inertia_3x3(_q([[0, 2, 3], [2, 0, 5], [3, 5, 0]])), (1, 2, 0))
        self.assertEqual(oracle.exact_symmetric_inertia_3x3(_q([[0, 2, 3], [2, 0, -5], [3, -5, 0]])), (2, 1, 0))
        # Hyperbolic 2x2 block at (0, 2) -> c0 != idx + 1 swap
        self.assertEqual(oracle.exact_symmetric_inertia_3x3(_q([[0, 0, 3], [0, 0, 0], [3, 0, 0]])), (1, 1, 1))
        # Hyperbolic 2x2 block at (1, 2) when idx == 0 -> r0 != idx and c0 != idx + 1 swaps
        self.assertEqual(oracle.exact_symmetric_inertia_3x3(_q([[0, 0, 0], [0, 0, 3], [0, 3, 0]])), (1, 1, 1))
        # Hyperbolic 2x2 block at (1, 2) when idx == 1 -> idx + 2 == n (no Schur step)
        self.assertEqual(oracle.exact_symmetric_inertia_3x3(_q([[4, 0, 0], [0, 0, 3], [0, 3, 0]])), (2, 1, 0))

        # Public API Zone-B hardening across all vector/matrix/path entry points
        max_ok = (1 << oracle.MAX_INT_BITS) - 1
        self.assertEqual(oracle.doubled_mid_ranks((max_ok, 0, 1, 2)), (6, 0, 2, 4))
        for bad_vec, expected_code in (
            (None, "INVALID_SEQ_TYPE"),
            ((True, 1, 2, 3), "INVALID_INT_TYPE"),
            ((_IntSub(1), 2, 3, 4), "INVALID_INT_TYPE"),
            ((1 << oracle.MAX_INT_BITS, 0, 1, 2), "INT_BIT_LIMIT"),
        ):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.center_doubled_ranks(bad_vec)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, expected_code)

        for fn in (
            oracle.op1_seam1_leverage_shock,
            oracle.op2_seam3_hvg_and_ordinal,
            oracle.op3_f3_var1_inertia,
            oracle.wht_exact_int,
        ):
            with self.assertRaises(oracle.TelemetryPortalError):
                fn(None)  # type: ignore[arg-type]
            with self.assertRaises(oracle.TelemetryPortalError):
                fn((True, False, True, False, True, False, True, False))  # type: ignore[arg-type]

        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.load_stripped_physical_streams(None)  # type: ignore[arg-type]
        self.assertEqual(ctx.exception.code, "INVALID_PATH_TYPE")

        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.evaluate_series_against_surrogates(tuple(range(64)), tag=10**5000)  # type: ignore[arg-type]
        self.assertEqual(ctx.exception.code, "INVALID_STR_TYPE")

        # exact_symmetric_inertia_3x3 non-Fraction, bad shape, and all 3 non-symmetric pairs
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.exact_symmetric_inertia_3x3([[1, 0, 0], [0, 1, 0], [0, 0, 1]])  # type: ignore[list-item]
        self.assertEqual(ctx.exception.code, "INVALID_FRACTION_TYPE")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.exact_symmetric_inertia_3x3([[Fraction(1)]])
        self.assertEqual(ctx.exception.code, "SEQ_TOO_SHORT")
        for asym_mat in (
            _q([[0, 1, 0], [2, 0, 0], [0, 0, 0]]),
            _q([[0, 0, 1], [0, 0, 0], [2, 0, 0]]),
            _q([[0, 0, 0], [0, 0, 1], [0, 2, 0]]),
        ):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.exact_symmetric_inertia_3x3(asym_mat)
            self.assertEqual(ctx.exception.code, "NON_SYMMETRIC_MATRIX")

        # All 4 independent Jury / Schur-Cohn inequalities
        self.assertTrue(oracle._is_schur_stable_cubic(Fraction(-3, 2), Fraction(3, 4), Fraction(-1, 8)))
        self.assertFalse(oracle._is_schur_stable_cubic(Fraction(-1, 1), Fraction(0, 1), Fraction(0, 1)))
        self.assertFalse(oracle._is_schur_stable_cubic(Fraction(1, 1), Fraction(0, 1), Fraction(0, 1)))
        self.assertFalse(oracle._is_schur_stable_cubic(Fraction(0, 1), Fraction(1, 1), Fraction(1, 1)))
        self.assertFalse(oracle._is_schur_stable_cubic(Fraction(-1, 2), Fraction(1, 1), Fraction(-1, 2)))

        # Alpha boundary exactness
        self.assertTrue(oracle._passes_alpha(Fraction(5, 100)))
        self.assertTrue(oracle._passes_alpha(Fraction(1, 100)))
        self.assertFalse(oracle._passes_alpha(Fraction(6, 100)))

        # op3 on zero centered vector hits tr_ttt == 0 branch
        op3_zero = oracle.op3_f3_var1_inertia((0, 0, 0, 0, 0))
        self.assertTrue(op3_zero["schur_stable"])
        self.assertEqual(op3_zero["inertia_I_minus_TtT"], [3, 0, 0])
        self.assertFalse(op3_zero["f3_transient_witness"])
        self.assertEqual(op3_zero["commutator_kappa_f3"], Fraction(0, 1))
        self.assertEqual(op3_zero["trace_TtT"], Fraction(0, 1))

        # Independent pure-Q verification of op3_f3_var1_inertia on non-trivial series
        raw = tuple(((i * 17 + (i % 7) * 11) % 31) - 15 for i in range(32))
        centered = oracle.center_doubled_ranks(oracle.doubled_mid_ranks(raw))
        got_op3 = oracle.op3_f3_var1_inertia(centered)
        lam = Fraction((len(centered) - 1) ** 2, 1)
        g_ref = [[lam if i == j else Fraction(0, 1) for j in range(3)] for i in range(3)]
        c_ref = [[Fraction(0, 1)] * 3 for _ in range(3)]
        for t in range(2, len(centered) - 1):
            zv = [Fraction(centered[t]), Fraction(centered[t - 1]), Fraction(centered[t - 2])]
            wv = [Fraction(centered[t + 1]), Fraction(centered[t]), Fraction(centered[t - 1])]
            for i in range(3):
                for j in range(3):
                    g_ref[i][j] += zv[i] * zv[j]
                    c_ref[i][j] += wv[i] * zv[j]
        ginv = _brute_force_invert_3x3_q(g_ref)
        t_ref = [[sum(c_ref[i][k] * ginv[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
        ttt_ref = [[sum(t_ref[k][i] * t_ref[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
        t_tt_ref = [[sum(t_ref[i][k] * t_ref[j][k] for k in range(3)) for j in range(3)] for i in range(3)]
        tr_ref = ttt_ref[0][0] + ttt_ref[1][1] + ttt_ref[2][2]
        comm_ref = sum((ttt_ref[i][j] - t_tt_ref[i][j]) ** 2 for i in range(3) for j in range(3))
        self.assertEqual(got_op3["trace_TtT"], tr_ref)
        self.assertEqual(got_op3["commutator_kappa_f3"], comm_ref / (tr_ref * tr_ref))

    def test_wht_surrogates_and_verdict_classification(self) -> None:
        for vec in ((3, -1), (1, -2, 4, 7), tuple(range(-8, 8))):
            n = len(vec)
            fwd = oracle.wht_exact_int(vec)
            inv = oracle.wht_exact_int(fwd)
            self.assertEqual(sum(x * x for x in fwd), n * sum(x * x for x in vec))
            self.assertEqual(inv, [n * x for x in vec])
        for bad_short in ((), (1,)):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.wht_exact_int(bad_short)
            self.assertEqual(ctx.exception.code, "SEQ_TOO_SHORT")
        for bad_vec in ((1, 2, 3), (1, 2, 3, 4, 5, 6)):
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.wht_exact_int(bad_vec)
            self.assertEqual(ctx.exception.code, "INVALID_WHT_LEN")

        # Non-ASCII valid UTF-8 seed_tag works; lone surrogate rejected cleanly
        ranks_t = oracle.doubled_mid_ranks((1, 4, 2, 3))
        self.assertEqual(len(oracle.generate_surrogate_ranks(ranks_t, "IID_PERM", "tag-é")), 4)
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.generate_surrogate_ranks(ranks_t, "IID_PERM", "\ud800")
        self.assertEqual(ctx.exception.code, "INVALID_UTF8")

        ranks = oracle.doubled_mid_ranks(tuple((i * 19) % 32 for i in range(32)))
        s_iid = oracle.generate_surrogate_ranks(ranks, "IID_PERM", "seed:iid")
        self.assertEqual(sorted(s_iid), sorted(ranks))
        self.assertEqual(s_iid, oracle.generate_surrogate_ranks(ranks, "IID_PERM", "seed:iid"))

        s_blk = oracle.generate_surrogate_ranks(ranks, "BLOCK_16", "seed:blk")
        self.assertEqual(sorted(s_blk), sorted(ranks))
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.generate_surrogate_ranks(ranks[:30], "BLOCK_16", "seed:bad")
        self.assertEqual(ctx.exception.code, "INVALID_BLOCK_LEN")

        s_wht = oracle.generate_surrogate_ranks(ranks, "WHT_PHASE", "seed:wht")
        self.assertEqual(sum(s_wht), 32 * 31)
        self.assertNotEqual(s_wht, oracle.generate_surrogate_ranks(ranks, "WHT_PHASE", "seed:wht2"))

        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.generate_surrogate_ranks(ranks, "UNKNOWN", "seed:u")
        self.assertEqual(ctx.exception.code, "UNKNOWN_SURROGATE_FAMILY")

        self.assertEqual(oracle.classify_cross_domain_verdict(0), "FALSIFIED")
        self.assertEqual(oracle.classify_cross_domain_verdict(1), "PARTIAL")
        self.assertEqual(oracle.classify_cross_domain_verdict(2), "PARTIAL")
        self.assertEqual(oracle.classify_cross_domain_verdict(3), "SUPPORTED")
        self.assertEqual(oracle.classify_cross_domain_verdict(4), "SUPPORTED")
        with self.assertRaises(oracle.TelemetryPortalError):
            oracle.classify_cross_domain_verdict(-1)
        with self.assertRaises(oracle.TelemetryPortalError):
            oracle.classify_cross_domain_verdict(5)

        # Surrogate evaluation bounds
        with self.assertRaises(oracle.TelemetryPortalError):
            oracle.evaluate_series_against_surrogates(tuple(range(64)), tag="t", surrogate_count=8)
        with self.assertRaises(oracle.TelemetryPortalError):
            oracle.evaluate_series_against_surrogates(tuple(range(64)), tag="t", surrogate_count=1000)


class TestC_CertificateValidationAndCLI(unittest.TestCase):
    """Zone-B certificate rejection tests and standalone CLI tests."""

    def test_real_certificate_and_all_tamper_rejections(self) -> None:
        cert_path = _HERE / "physical_telemetry_certificate.json"
        res = audit_cli.verify_certificate_file(cert_path, track_dir=None)
        self.assertTrue(res["valid"])
        self.assertEqual(res["track_id"], "TRACK-S20C")

        cert = oracle.load_strict_json_file(cert_path)
        self.assertEqual(
            cert["payload"]["fetch_manifest_sha256"],
            hashlib.sha256((_HERE / "FETCH_MANIFEST.json").read_bytes()).hexdigest(),
        )
        self.assertEqual(
            cert["payload"]["prereg_sha256"],
            hashlib.sha256((_HERE / "PREREG_S20C.json").read_bytes()).hexdigest(),
        )
        self.assertEqual(
            {k: v["verdict"] for k, v in cert["payload"]["cross_domain_verdicts"].items()},
            {
                "H1_SEAM1_SHOCK": "FALSIFIED",
                "H2a_SEAM3_HVG_BETTI1": "FALSIFIED",
                "H2b_SEAM3_IRREV_PHI": "PARTIAL",
                "H3a_F3_TRANSIENT_WITNESS": "SUPPORTED",
                "H3b_F3_COMMUTATOR": "FALSIFIED",
            },
        )

        # Fast observed-operator & provenance replay against real TRACK_DIR
        self.assertIs(inspect.signature(oracle.validate_certificate_payload).parameters["full_replay"].default, True)
        self.assertIs(inspect.signature(audit_cli.verify_certificate_file).parameters["full_replay"].default, True)
        res_obs = audit_cli.verify_certificate_file(cert_path, track_dir=_HERE, full_replay=False)
        self.assertTrue(res_obs["valid"])
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(cert, track_dir=None, full_replay=1)  # type: ignore[arg-type]
        self.assertEqual(ctx.exception.code, "INVALID_BOOL_TYPE")
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(cert, track_dir=_HERE, full_replay=1)  # type: ignore[arg-type]
        self.assertEqual(ctx.exception.code, "INVALID_BOOL_TYPE")

        for prov_key in ("fetch_manifest_sha256", "prereg_sha256"):
            bad_prov = copy.deepcopy(cert)
            bad_prov["payload"][prov_key] = "0" * 64
            bad_prov = _rehash_cert(bad_prov)
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                oracle.validate_certificate_payload(bad_prov, track_dir=_HERE, full_replay=False)
            self.assertEqual(ctx.exception.code, "PROVENANCE_PIN_MISMATCH")

        bad_wa = copy.deepcopy(cert)
        bad_wa["payload"]["calibration_window_a"]["STREAM_A"]["unique_values"] = 1
        bad_wa = _rehash_cert(bad_wa)
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(bad_wa, track_dir=_HERE, full_replay=False)
        self.assertEqual(ctx.exception.code, "OBSERVED_REPLAY_MISMATCH")

        bad_wb = copy.deepcopy(cert)
        bad_wb["payload"]["heldout_window_b"]["STREAM_A"]["op2_seam3"]["hvg_betti1"] = 0
        bad_wb = _rehash_cert(bad_wb)
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(bad_wb, track_dir=_HERE, full_replay=False)
        self.assertEqual(ctx.exception.code, "OBSERVED_REPLAY_MISMATCH")

        # CLI --observed-only runs observed-operator check on DEFAULT_CERT_PATH; conflicting replay flags rejected
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            rc = audit_cli.main(["--observed-only"])
        self.assertEqual(rc, 0)
        self.assertTrue(json.loads(out_buf.getvalue())["valid"])

        for bad_flags in (
            ["--no-replay", "--full-replay"],
            ["--no-replay", "--observed-only"],
            ["--observed-only", "--full-replay"],
        ):
            out_buf = io.StringIO()
            err_buf = io.StringIO()
            with redirect_stdout(out_buf), redirect_stderr(err_buf):
                rc = audit_cli.main(bad_flags)
            self.assertEqual(rc, 1)
            self.assertEqual(json.loads(err_buf.getvalue())["error_code"], "INVALID_CLI_ARGS")
        c_extra = copy.deepcopy(cert)
        c_extra["extra"] = 1
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(c_extra)
        self.assertEqual(ctx.exception.code, "INVALID_CERT_KEYS")

        c_schema = copy.deepcopy(cert)
        c_schema["schema_version"] = "wrong/v0"
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(c_schema)
        self.assertEqual(ctx.exception.code, "INVALID_SCHEMA_VERSION")

        c_track = copy.deepcopy(cert)
        c_track["track_id"] = "WRONG"
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(c_track)
        self.assertEqual(ctx.exception.code, "INVALID_TRACK_ID")

        c_psha = copy.deepcopy(cert)
        c_psha["payload_sha256"] = "0" * 64
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(c_psha)
        self.assertEqual(ctx.exception.code, "PAYLOAD_SHA_MISMATCH")

        c_csha = copy.deepcopy(cert)
        c_csha["certificate_sha256"] = "0" * 64
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(c_csha)
        self.assertEqual(ctx.exception.code, "CERT_SHA_MISMATCH")

        # Payload-level tampers (re-hashed so digest checks pass and semantic checks fire!)
        tampers = [
            ("INVALID_PAYLOAD_KEYS", lambda p: p.update({"extra": 1})),
            ("INVALID_PAYLOAD_SCHEMA", lambda p: p.update({"schema_version": "bad"})),
            ("INVALID_PAYLOAD_TRACK", lambda p: p.update({"track_id": "BAD"})),
            ("INVALID_ORACLE_CLASS", lambda p: p.update({"oracle_class": "synthetic"})),
            ("INVALID_STREAM_IDS", lambda p: p.update({"stage_a_stripped_ids": ["STREAM_D", "STREAM_C", "STREAM_B", "STREAM_A"]})),
            ("CONTROLS_FAILED", lambda p: p["known_answer_controls"].update({"all_controls_passed": False})),
            ("VERDICT_KEYS_MISMATCH", lambda p: p["cross_domain_verdicts"].pop("H1_SEAM1_SHOCK")),
            ("HELDOUT_KEYS_MISMATCH", lambda p: p["heldout_window_b"].pop("STREAM_D")),
            ("GATE_KEYS_MISMATCH", lambda p: p["heldout_window_b"]["STREAM_A"]["passes_prereg_gate"].pop("H1_SEAM1_SHOCK")),
            ("SURROGATE_FAMILY_KEYS_MISMATCH", lambda p: p["heldout_window_b"]["STREAM_A"]["surrogate_exceed_counts"].pop("IID_PERM")),
            ("SURROGATE_FAMILY_KEYS_MISMATCH", lambda p: p["heldout_window_b"]["STREAM_A"]["surrogate_pvals"].pop("WHT_PHASE")),
            ("PVAL_COUNT_MISMATCH", lambda p: p["heldout_window_b"]["STREAM_A"]["surrogate_pvals"]["IID_PERM"].update({"H1_SEAM1_SHOCK": "1/100"})),
            ("GATE_PVAL_MISMATCH", lambda p: p["heldout_window_b"]["STREAM_C"]["passes_prereg_gate"].update({"H2b_SEAM3_IRREV_PHI": True})),
            ("GATE_F3_MISMATCH", lambda p: p["heldout_window_b"]["STREAM_A"]["op3_f3"].update({"f3_transient_witness": False})),
            ("VERDICT_FIELD_KEYS_MISMATCH", lambda p: p["cross_domain_verdicts"]["H1_SEAM1_SHOCK"].update({"x": 1})),
            ("VERDICT_STREAMS_MISMATCH", lambda p: p["cross_domain_verdicts"]["H1_SEAM1_SHOCK"].update({"passing_streams": ["STREAM_A"]})),
            ("VERDICT_COUNT_MISMATCH", lambda p: p["cross_domain_verdicts"]["H1_SEAM1_SHOCK"].update({"passing_count": 1})),
            ("INT_ABOVE_MAX", lambda p: p["cross_domain_verdicts"]["H1_SEAM1_SHOCK"].update({"total_streams": 5})),
            ("VERDICT_LOGIC_MISMATCH", lambda p: p["cross_domain_verdicts"]["H1_SEAM1_SHOCK"].update({"verdict": "SUPPORTED"})),
        ]
        for expected_code, mutate_fn in tampers:
            bad = copy.deepcopy(cert)
            mutate_fn(bad["payload"])
            bad = _rehash_cert(bad)
            with self.assertRaises(oracle.TelemetryPortalError, msg=expected_code) as ctx:
                oracle.validate_certificate_payload(bad)
            self.assertEqual(ctx.exception.code, expected_code)

    def test_cli_verify_generate_errors_and_isolated_subprocess(self) -> None:
        cert_path = _HERE / "physical_telemetry_certificate.json"
        cert = oracle.load_strict_json_file(cert_path)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # Non-canonical bytes, CRLF, invalid UTF-8 rejected by verify_certificate_file
            non_canon = root / "non_canon.json"
            non_canon.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                audit_cli.verify_certificate_file(non_canon)
            self.assertEqual(ctx.exception.code, "NON_CANONICAL_CERT_BYTES")

            crlf = root / "crlf.json"
            crlf.write_bytes(oracle.canonical_json_bytes(cert) + b"\r\n")
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                audit_cli.verify_certificate_file(crlf)
            self.assertEqual(ctx.exception.code, "CR_FORBIDDEN")

            bad_u8 = root / "bad_u8.json"
            bad_u8.write_bytes(b"\xff\xfe")
            with self.assertRaises(oracle.TelemetryPortalError) as ctx:
                audit_cli.verify_certificate_file(bad_u8)
            self.assertEqual(ctx.exception.code, "INVALID_UTF8")

            # CLI --check --no-replay success
            out_buf = io.StringIO()
            err_buf = io.StringIO()
            with redirect_stdout(out_buf), redirect_stderr(err_buf):
                rc = audit_cli.main(["--check", str(cert_path), "--no-replay"])
            self.assertEqual(rc, 0)
            parsed = json.loads(out_buf.getvalue())
            self.assertTrue(parsed["valid"])
            self.assertEqual(parsed["file_sha256"], hashlib.sha256(cert_path.read_bytes()).hexdigest())

            # CLI --check failure returns exit 1 + JSON error on stderr
            out_buf = io.StringIO()
            err_buf = io.StringIO()
            with redirect_stdout(out_buf), redirect_stderr(err_buf):
                rc = audit_cli.main(["--check", str(non_canon), "--no-replay"])
            self.assertEqual(rc, 1)
            err_obj = json.loads(err_buf.getvalue())
            self.assertFalse(err_obj["valid"])
            self.assertEqual(err_obj["error_code"], "NON_CANONICAL_CERT_BYTES")

            # CLI --generate happy path + FILE_WRITE_ERROR path (fast via temporary stub)
            orig_builder = audit_cli.build_certificate
            audit_cli.build_certificate = lambda _td: cert  # type: ignore[assignment]
            try:
                gen_out = root / "gen_cert.json"
                out_buf = io.StringIO()
                err_buf = io.StringIO()
                with redirect_stdout(out_buf), redirect_stderr(err_buf):
                    rc = audit_cli.main(["--generate", "--out", str(gen_out), "--track-dir", str(_HERE)])
                self.assertEqual(rc, 0)
                summary = json.loads(out_buf.getvalue())
                self.assertTrue(summary["generated"])
                self.assertTrue(summary["controls_passed"])
                self.assertEqual(gen_out.read_bytes(), cert_path.read_bytes())

                # Writing to an existing directory or FIFO triggers fail-closed FILE_WRITE_ERROR (no hang)
                out_fifo = root / "out.fifo"
                os.mkfifo(out_fifo)
                for bad_out in (root, out_fifo):
                    out_buf = io.StringIO()
                    err_buf = io.StringIO()
                    with redirect_stdout(out_buf), redirect_stderr(err_buf):
                        rc = audit_cli.main(["--generate", "--out", str(bad_out), "--track-dir", str(_HERE)])
                    self.assertEqual(rc, 1)
                    self.assertEqual(json.loads(err_buf.getvalue())["error_code"], "FILE_WRITE_ERROR")
                # Overwriting an existing regular file succeeds cleanly
                out_buf = io.StringIO()
                err_buf = io.StringIO()
                with redirect_stdout(out_buf), redirect_stderr(err_buf):
                    rc = audit_cli.main(["--generate", "--out", str(gen_out), "--track-dir", str(_HERE)])
                self.assertEqual(rc, 0)
            finally:
                audit_cli.build_certificate = orig_builder

            # CLI invalid argv types/elements fail closed cleanly with exit 1
            for bad_argv, expected_code in (
                ("not-a-list", "INVALID_CLI_ARGS"),
                ([123], "INVALID_STR_TYPE"),
                ([_StrSub("--no-replay")], "INVALID_STR_TYPE"),
                (["\ud800"], "INVALID_UTF8"),
            ):
                out_buf = io.StringIO()
                err_buf = io.StringIO()
                with redirect_stdout(out_buf), redirect_stderr(err_buf):
                    rc = audit_cli.main(bad_argv)  # type: ignore[arg-type]
                self.assertEqual(rc, 1)
                self.assertEqual(json.loads(err_buf.getvalue())["error_code"], expected_code)

            # Isolated -I subprocess from foreign cwd kills sys.path insertion & __main__ mutants
            proc = subprocess.run(
                [sys.executable, "-I", "-O", "-B", str(_HERE / "physical_telemetry_audit.py"), "--check", str(cert_path), "--no-replay"],
                cwd=td,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(json.loads(proc.stdout)["valid"])


class TestZ_EndToEndReplayIntegration(unittest.TestCase):
    """End-to-end deterministic build + replay parity + replay tamper rejection (m=19)."""

    def test_z_build_and_replay_parity_m19(self) -> None:
        cert19 = oracle.build_certificate(_HERE, surrogate_count=19)
        self.assertTrue(cert19["payload"]["known_answer_controls"]["all_controls_passed"])
        res = oracle.validate_certificate_payload(cert19, track_dir=_HERE, full_replay=True, surrogate_count=19)
        self.assertTrue(res["valid"])

        # Mismatched surrogate_count caught by internal p-value consistency check
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(cert19, track_dir=_HERE, full_replay=True, surrogate_count=9)
        self.assertEqual(ctx.exception.code, "PVAL_COUNT_MISMATCH")

        # Tamper a descriptive field and re-hash -> passes digest & schema, fails REPLAY_MISMATCH
        tampered = copy.deepcopy(cert19)
        tampered["payload"]["calibration_window_a"]["STREAM_A"]["unique_values"] = 1
        tampered = _rehash_cert(tampered)
        with self.assertRaises(oracle.TelemetryPortalError) as ctx:
            oracle.validate_certificate_payload(tampered, track_dir=_HERE, full_replay=True, surrogate_count=19)
        self.assertEqual(ctx.exception.code, "REPLAY_MISMATCH")


if __name__ == "__main__":
    unittest.main()
