#!/usr/bin/env python3
"""R5 must-fail controls for verification/checks/verify_round10_standalone.py.

The verifier promises strict zero-float JSON parsing and SHA-256 parity of each Round-10
certifier's stdout (its docstring, lines 7-9). PROTOCOL.md R5 asks that each of those
refusals have a control that trips it. The verify_arm controls build a fake arm in a
temporary directory, so the real symbiosis/round10 tree is neither read nor changed, and
each control compares the full error list.

Run (all three R4 modes):
  python3 -I -B verification/tests/test_verify_round10_r5.py
  python3 -I -O -B verification/tests/test_verify_round10_r5.py
  python3 -I -B -W error verification/tests/test_verify_round10_r5.py
Needs: Python 3 standard library only. Takes under 1 second.
"""
from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import types
import unittest
from pathlib import Path

VERIFIER = Path(__file__).resolve().parents[1] / "checks" / "verify_round10_standalone.py"
ARM = "fake-arm"
GOOD_STDOUT = b'{"ok": 1}\n'


def _load_verifier() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("cave_verify_round10_under_test", VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {VERIFIER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V = _load_verifier()


def certifier_source(stdout: bytes, exit_code: int) -> str:
    # The certifier leaves a marker so a control can tell whether it ran.
    return (
        "import pathlib, sys\n"
        "pathlib.Path('certifier_ran.marker').touch()\n"
        f"sys.stdout.buffer.write({stdout!r})\n"
        f"raise SystemExit({exit_code})\n"
    )


class StrictJson(unittest.TestCase):
    def refused(self, raw: bytes) -> str:
        with self.assertRaises(ValueError) as ctx:
            V.parse_strict_zero_float_json(raw)
        return str(ctx.exception)

    def test_accepts_integer_object(self):
        self.assertEqual(V.parse_strict_zero_float_json(b'{"a": 1, "b": [2, "x"]}'), {"a": 1, "b": [2, "x"]})

    def test_duplicate_key(self):
        self.assertEqual(self.refused(b'{"a": 1, "a": 2}'), "DUPLICATE_JSON_KEY: a")

    def test_nan(self):
        self.assertEqual(self.refused(b'{"a": NaN}'), "NONFINITE_JSON_CONSTANT: NaN")

    def test_float(self):
        self.assertEqual(self.refused(b'{"a": 1.5}'), "FLOAT_FORBIDDEN_IN_JSON: 1.5")

    def test_top_level_list(self):
        self.assertEqual(self.refused(b"[1, 2]"), "TOP_LEVEL_JSON_MUST_BE_OBJECT")


class VerifyArm(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.arm_dir = self.root / "symbiosis" / "round10" / ARM

    def tearDown(self):
        self._tmp.cleanup()

    def build(self, stdout=GOOD_STDOUT, cert_exit=0, test_exit=0, expected_sha=None, extra_expected=()):
        self.arm_dir.mkdir(parents=True)
        (self.arm_dir / "cert.py").write_text(certifier_source(stdout, cert_exit), encoding="utf-8")
        (self.arm_dir / "suite.py").write_text(f"raise SystemExit({test_exit})\n", encoding="utf-8")
        return {
            "audit_id": "AUDIT-TEST",
            "arm": ARM,
            "cert_script": "cert.py",
            "cert_args": ["--json"],
            "test_script": "suite.py",
            "expected_standalone_stdout_sha256": expected_sha or hashlib.sha256(stdout).hexdigest(),
            "expected_files": ("cert.py", "suite.py", *extra_expected),
        }

    def test_passing_arm(self):
        result = V.verify_arm(self.build(), self.root)
        self.assertEqual(result["errors"], [])
        self.assertIs(result["passed"], True)
        self.assertEqual(result["standalone_stdout_sha256"], hashlib.sha256(GOOD_STDOUT).hexdigest())

    def test_missing_arm_dir(self):
        spec = self.build()
        spec["arm"] = "absent-arm"
        result = V.verify_arm(spec, self.root)
        self.assertEqual(result["errors"], ["MISSING_ARM_DIR: absent-arm"])
        self.assertIs(result["passed"], False)

    def test_missing_file_stops_before_the_certifier(self):
        result = V.verify_arm(self.build(extra_expected=("absent.txt",)), self.root)
        self.assertEqual(result["errors"], [f"MISSING_FILE: {ARM}/absent.txt"])
        self.assertIs(result["passed"], False)
        self.assertFalse((self.arm_dir / "certifier_ran.marker").exists(), "the certifier ran despite a missing file")

    def test_sha_mismatch(self):
        wrong = "0" * 64
        result = V.verify_arm(self.build(expected_sha=wrong), self.root)
        got = hashlib.sha256(GOOD_STDOUT).hexdigest()
        self.assertEqual(result["errors"], [f"STANDALONE_SHA256_MISMATCH: got={got} expected={wrong}"])

    def test_certifier_exit_3(self):
        result = V.verify_arm(self.build(cert_exit=3), self.root)
        self.assertEqual(result["errors"], ["CERTIFIER_NONZERO_EXIT: rc=3"])
        self.assertEqual(result["cert_rc"], 3)

    def test_float_in_certifier_output(self):
        result = V.verify_arm(self.build(stdout=b'{"x": 1.5}\n'), self.root)
        self.assertEqual(result["errors"], ["STRICT_JSON_ERROR: FLOAT_FORBIDDEN_IN_JSON: 1.5"])

    def test_r5_suite_exit_1(self):
        result = V.verify_arm(self.build(test_exit=1), self.root)
        self.assertEqual(result["errors"], ["R5_TEST_NONZERO_EXIT: rc=1"])
        self.assertEqual(result["test_rc"], 1)


if __name__ == "__main__":
    unittest.main()
