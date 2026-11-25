#!/usr/bin/env python3
"""
AUDIT-114 Standalone CLI & Fail-Closed Certificate Checker (`zone_sylvester_audit.py`).

Pure Python 3 standard library (`0` floats, `0` bare asserts, `0` external deps).
Supports:
  - `--standalone --json`: emit canonical AUDIT-114 certificate JSON to stdout
  - `--write [PATH]`: write canonical certificate to `zone_sylvester_certificate.json` (or PATH)
  - `--check PATH`: fail-closed verification of a committed certificate file (symlink guard,
    strict UTF-8 & canonical JSON check, SHA-256 commitment check, and full exact recomputation).
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from zone_sylvester_oracle import (
    Audit114Error,
    build_audit114_payload,
    canonical_json_bytes_v21,
    parse_aletheia_strict_nofloat,
)

CERT_SCHEMA = "audit114.certificate.v1"
DEFAULT_CERT_PATH = HERE / "zone_sylvester_certificate.json"


def build_certificate() -> dict[str, Any]:
    """Build deterministic self-contained AUDIT-114 certificate with SHA-256 payload binding."""
    payload = build_audit114_payload()
    payload_sha256 = hashlib.sha256(canonical_json_bytes_v21(payload)).hexdigest()
    return {
        "schema": CERT_SCHEMA,
        "audit_id": "AUDIT-114",
        "payload_sha256": payload_sha256,
        "payload": payload,
    }


def _require_no_symlink_path(path: Path) -> None:
    """Reject symlink target or any symlinked ancestor directory."""
    if path.is_symlink():
        raise Audit114Error("SYMLINK_FORBIDDEN", f"symlink path forbidden: {path}")
    for parent in path.parents:
        if parent.is_symlink():
            raise Audit114Error("SYMLINK_ANCESTOR_FORBIDDEN", f"symlink ancestor forbidden: {parent}")


def verify_certificate_dict(cert: Any) -> dict[str, Any]:
    """Fail-closed exact verification of a parsed AUDIT-114 certificate dictionary."""
    if type(cert) is not dict:
        raise Audit114Error("CERT_NOT_DICT", "certificate root must be a JSON object")
    if any(type(k) is not str for k in cert):
        raise Audit114Error("CERT_NON_STRING_KEY", "certificate keys must all be str")
    if set(cert.keys()) != {"schema", "audit_id", "payload_sha256", "payload"}:
        raise Audit114Error("CERT_SCHEMA_KEYS", f"unexpected keys: {sorted(cert.keys())}")
    if cert["schema"] != CERT_SCHEMA or cert["audit_id"] != "AUDIT-114":
        raise Audit114Error("CERT_HEADER_MISMATCH", "schema or audit_id mismatch")
    stored_sha = cert["payload_sha256"]
    if type(stored_sha) is not str or len(stored_sha) != 64 or any(c not in "0123456789abcdef" for c in stored_sha):
        raise Audit114Error("INVALID_PAYLOAD_SHA", "payload_sha256 must be 64 lowercase hex chars")

    computed_sha = hashlib.sha256(canonical_json_bytes_v21(cert["payload"])).hexdigest()
    if not hmac.compare_digest(stored_sha, computed_sha):
        raise Audit114Error("PAYLOAD_SHA_MISMATCH", f"stored {stored_sha} != computed {computed_sha}")

    expected = build_certificate()
    if not hmac.compare_digest(computed_sha, expected["payload_sha256"]):
        raise Audit114Error("RECOMPUTED_PAYLOAD_DRIFT", "certificate payload differs from exact recomputation")

    cert_sha256 = hashlib.sha256(canonical_json_bytes_v21(cert)).hexdigest()
    return {
        "valid": True,
        "audit_id": "AUDIT-114",
        "payload_sha256": computed_sha,
        "certificate_sha256": cert_sha256,
    }


def check_certificate_file(path: Path) -> dict[str, Any]:
    """Fail-closed file check: rejects symlinks, CRLF, invalid UTF-8, non-canonical JSON, or tamper."""
    if not isinstance(path, Path):
        raise Audit114Error("INVALID_PATH_TYPE", "path must be a pathlib.Path")
    _require_no_symlink_path(path)
    if not path.is_file():
        raise Audit114Error("CERT_FILE_NOT_FOUND", f"certificate file not found: {path}")
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise Audit114Error("CRLF_FORBIDDEN", "CRLF line endings forbidden in certificate")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Audit114Error("INVALID_UTF8", f"invalid UTF-8: {exc}") from exc
    parsed = parse_aletheia_strict_nofloat(text)
    result = verify_certificate_dict(parsed)
    canonical_raw = canonical_json_bytes_v21(parsed)
    if raw not in (canonical_raw, canonical_raw + b"\n"):
        raise Audit114Error("NON_CANONICAL_CERT_BYTES", "certificate file is not canonical JSON")
    return result


def write_certificate_file(path: Path) -> dict[str, Any]:
    """Write canonical UTF-8 LF certificate file and verify it immediately."""
    _require_no_symlink_path(path)
    cert = build_certificate()
    raw = canonical_json_bytes_v21(cert) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return check_certificate_file(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUDIT-114 zone-canon & Sylvester inertia certifier")
    parser.add_argument("--standalone", action="store_true", help="Run full standalone exact verification")
    parser.add_argument("--json", action="store_true", help="Emit canonical JSON certificate to stdout")
    parser.add_argument("--write", nargs="?", const=str(DEFAULT_CERT_PATH), help="Write canonical certificate file")
    parser.add_argument("--check", type=str, help="Fail-closed verification of a certificate JSON file")
    args = parser.parse_args(argv)

    try:
        if args.check is not None:
            res = check_certificate_file(Path(args.check))
            print(f"OK AUDIT-114 payload_sha256={res['payload_sha256']} certificate_sha256={res['certificate_sha256']}")
            return 0
        if args.write is not None:
            res = write_certificate_file(Path(args.write))
            print(f"WROTE AUDIT-114 payload_sha256={res['payload_sha256']} certificate_sha256={res['certificate_sha256']}")
            return 0
        cert = build_certificate()
        if args.json:
            sys.stdout.buffer.write(canonical_json_bytes_v21(cert) + b"\n")
            return 0
        print(f"OK AUDIT-114 payload_sha256={cert['payload_sha256']} all_passed={cert['payload']['all_passed']}")
        return 0
    except Audit114Error as exc:
        print(f"REJECT {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
