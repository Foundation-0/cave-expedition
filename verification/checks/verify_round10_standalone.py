#!/usr/bin/env python3
"""
Portable Zero-Dependency Standalone Verifier for Wave 2 Round 10 (AUDIT-084R..088R).

Runs all five committed Round-10 standalone certifiers and R5 test suites directly
from this repository checkout under isolated Python execution (`-I -B -W error` /
`-I -O -B -W error`), enforces strict zero-float JSON parsing (zero duplicate keys,
zero NaN/Infinity, zero IEEE-754 floats), and verifies exact bit-identical SHA-256
parity against the independently audited standalone certificates.

Pure Python 3 stdlib only. Zero bare `assert`s. Zero hardcoded absolute paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

ROUND10_SPECS: tuple[dict[str, Any], ...] = (
    {
        "audit_id": "AUDIT-084R",
        "arm": "arm1-own-terms-first",
        "cert_script": "own_terms_first_audit.py",
        "cert_args": ["--standalone", "--json"],
        "test_script": "test_own_terms_first_r5.py",
        "expected_standalone_stdout_sha256": (
            "de380f4b83c182280cbcb9a5b4d1fa7ecc44474a82eea779090662c001897c39"
        ),
        "expected_files": (
            "OWN_TERMS_FIRST_AUDIT_REPORT.md",
            "own_terms_first_audit.py",
            "own_terms_first_certificate.json",
            "own_terms_first_oracle.py",
            "test_own_terms_first_r5.py",
        ),
    },
    {
        "audit_id": "AUDIT-085R",
        "arm": "arm2-unification-and-novelty",
        "cert_script": "unification_bridge_audit.py",
        "cert_args": ["--standalone"],
        "test_script": "test_r5_unification_bridge.py",
        "expected_standalone_stdout_sha256": (
            "86dc7577334bc121defbb20f7f647b3853302b760c6e9ae3d7e8021df938eaba"
        ),
        "expected_files": (
            "REPORT_R10_2_UNIFICATION_AND_NOVELTY.md",
            "test_r5_unification_bridge.py",
            "unification_bridge_audit.py",
            "unification_bridge_certificate.json",
        ),
    },
    {
        "audit_id": "AUDIT-086R",
        "arm": "arm3-gates-r6r7-cli",
        "cert_script": "aletheia_r6r7_r3_gate_audit.py",
        "cert_args": ["--standalone", "--json"],
        "test_script": "test_aletheia_r6r7_r3_r5.py",
        "expected_standalone_stdout_sha256": (
            "e56cac167a3869eef0ad0d6292e74a9e09374428108fde76c94dbd96f3c5adb8"
        ),
        "expected_files": (
            "ALETHEIA_R6R7_CLI_AUDIT_REPORT.md",
            "aletheia_r6r7_r3_certificate.json",
            "aletheia_r6r7_r3_gate_audit.py",
            "test_aletheia_r6r7_r3_r5.py",
        ),
    },
    {
        "audit_id": "AUDIT-087R",
        "arm": "arm4-prereg-raw-data",
        "cert_script": "prereg_raw_data_certifier.py",
        "cert_args": ["--json"],
        "test_script": "test_prereg_raw_data_r5.py",
        "expected_standalone_stdout_sha256": (
            "a8331c8f44bbeab4e2154b1780f6215bb016b53cd82f247ac4aea92fc7815887"
        ),
        "expected_files": (
            "PREREG_RAW_DATA_AUDIT_REPORT.md",
            "prereg_raw_data_certificate.json",
            "prereg_raw_data_certifier.py",
            "test_prereg_raw_data_r5.py",
        ),
    },
    {
        "audit_id": "AUDIT-088R",
        "arm": "arm5-transformational-steelman",
        "cert_script": "transformational_steelman_certifier.py",
        "cert_args": ["--standalone", "--json"],
        "test_script": "test_transformational_steelman_r5.py",
        "expected_standalone_stdout_sha256": (
            "54d07116cf2d9ece84c4217083ce29c4c404f668d3905ded33eafc97573870ef"
        ),
        "expected_files": (
            "TRANSFORMATIONAL_STEELMAN_REPORT.md",
            "test_transformational_steelman_r5.py",
            "transformational_steelman_certificate.json",
            "transformational_steelman_certifier.py",
        ),
    },
)


def _strict_no_dups_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f"DUPLICATE_JSON_KEY: {k}")
        out[k] = v
    return out


def _forbid_constant(val: str) -> Any:
    raise ValueError(f"NONFINITE_JSON_CONSTANT: {val}")


def _forbid_float(val: str) -> Any:
    raise ValueError(f"FLOAT_FORBIDDEN_IN_JSON: {val}")


def parse_strict_zero_float_json(raw_bytes: bytes) -> dict[str, Any]:
    text = raw_bytes.decode("utf-8")
    parsed = json.loads(
        text,
        object_pairs_hook=_strict_no_dups_hook,
        parse_constant=_forbid_constant,
        parse_float=_forbid_float,
    )
    if not isinstance(parsed, dict):
        raise ValueError("TOP_LEVEL_JSON_MUST_BE_OBJECT")
    return parsed


def verify_arm(spec: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    arm_dir = repo_root / "symbiosis" / "round10" / spec["arm"]
    errors: list[str] = []

    if not arm_dir.is_dir():
        return {
            "audit_id": spec["audit_id"],
            "arm": spec["arm"],
            "passed": False,
            "errors": [f"MISSING_ARM_DIR: {spec['arm']}"],
        }

    for fname in spec["expected_files"]:
        if not (arm_dir / fname).is_file():
            errors.append(f"MISSING_FILE: {spec['arm']}/{fname}")

    if errors:
        return {
            "audit_id": spec["audit_id"],
            "arm": spec["arm"],
            "passed": False,
            "errors": errors,
        }

    # 1. Execute standalone certifier under isolated -I -B -W error
    cert_cmd = [sys.executable, "-I", "-B", "-W", "error", spec["cert_script"], *spec["cert_args"]]
    cert_proc = subprocess.run(cert_cmd, cwd=str(arm_dir), capture_output=True)
    cert_sha = hashlib.sha256(cert_proc.stdout).hexdigest()
    if cert_proc.returncode != 0:
        errors.append(f"CERTIFIER_NONZERO_EXIT: rc={cert_proc.returncode}")
    if cert_sha != spec["expected_standalone_stdout_sha256"]:
        errors.append(
            f"STANDALONE_SHA256_MISMATCH: got={cert_sha} expected={spec['expected_standalone_stdout_sha256']}"
        )
    try:
        parse_strict_zero_float_json(cert_proc.stdout)
    except ValueError as exc:
        errors.append(f"STRICT_JSON_ERROR: {exc}")

    # 2. Execute R5 test suite under -I -O -B -W error
    test_cmd = [sys.executable, "-I", "-O", "-B", "-W", "error", spec["test_script"]]
    test_proc = subprocess.run(test_cmd, cwd=str(arm_dir), capture_output=True)
    if test_proc.returncode != 0:
        errors.append(f"R5_TEST_NONZERO_EXIT: rc={test_proc.returncode}")

    return {
        "audit_id": spec["audit_id"],
        "arm": spec["arm"],
        "passed": len(errors) == 0,
        "standalone_stdout_sha256": cert_sha,
        "cert_rc": cert_proc.returncode,
        "test_rc": test_proc.returncode,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run all 5 committed Round-10 standalone certifiers & R5 test suites."
    )
    parser.add_argument("--json", action="store_true", help="Emit canonical JSON report.")
    args = parser.parse_args(argv)

    results = [verify_arm(spec, REPO_ROOT) for spec in ROUND10_SPECS]
    all_passed = all(r["passed"] for r in results)
    summary = {
        "schema": "expedition.round10_standalone_check.v1",
        "arms_checked": len(results),
        "arms_passed": sum(1 for r in results if r["passed"]),
        "passed": all_passed,
        "status": "PASS" if all_passed else "FAIL",
        "results": results,
    }

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"ROUND10_STANDALONE_CHECK: {summary['status']} ({summary['arms_passed']}/{summary['arms_checked']} arms)")
        for r in results:
            tag = "PASS" if r["passed"] else "FAIL"
            sha16 = r.get("standalone_stdout_sha256", "")[:16]
            print(f"  [{tag}] {r['audit_id']} ({r['arm']}): sha256={sha16} cert_rc={r.get('cert_rc')} test_rc={r.get('test_rc')}")
            for err in r["errors"]:
                print(f"         ERROR: {err}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
