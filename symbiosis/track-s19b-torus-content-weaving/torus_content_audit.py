#!/usr/bin/env python3
"""
AUDIT-118B Standalone CLI & Fail-Closed Certificate Checker (`torus_content_audit.py`).

Pure Python 3 standard library (`0` floats, `0` bare asserts, `0` external deps).
Supports:
  - `--standalone --json`: emit canonical AUDIT-118B certificate JSON to stdout
  - `--write [PATH]`: write canonical certificate to `torus_content_certificate.json` (or PATH)
  - `--check PATH`: fail-closed verification of a committed certificate file (symlink guard,
    size cap, CR/CRLF/UTF-8 check, strict zero-float iterative depth-64 bit-capped JSON check,
    strict 64-lowercase-ASCII-hex check BEFORE `hmac.compare_digest`, exact recomputation,
    and canonical byte-for-byte parity). Exits cleanly with code `2` on any typed or OS error.
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

from torus_content_oracle import (
    MAX_JSON_BYTES,
    TorusContentError,
    build_audit118b_payload,
    canonical_json_bytes,
    parse_strict_json,
)

CERT_SCHEMA = "audit118b.torus_content_weaving.certificate.v1"
CERT_AUDIT_ID = "AUDIT-118B"
DEFAULT_CERT_PATH = HERE / "torus_content_certificate.json"
_HEX_LOWER = frozenset("0123456789abcdef")
_CERT_KEYS = frozenset({"schema", "audit_id", "payload_sha256", "certificate_sha256", "payload"})


def _require_sha256_hex(val: Any, label: str) -> str:
    """Strict 64-lowercase-ASCII-hex guard BEFORE hmac.compare_digest."""
    if type(val) is not str:
        raise TorusContentError("INVALID_DIGEST_TYPE", f"{label} must be strict str")
    if len(val) != 64:
        raise TorusContentError("INVALID_DIGEST_LEN", f"{label} must have length 64")
    if any(ch not in _HEX_LOWER for ch in val):
        raise TorusContentError("INVALID_DIGEST_HEX", f"{label} must be lowercase ASCII hex")
    return val


def build_certificate() -> dict[str, Any]:
    """Build deterministic self-contained AUDIT-118B certificate with payload & envelope SHA-256."""
    payload = build_audit118b_payload()
    payload_sha256 = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    envelope = {
        "schema": CERT_SCHEMA,
        "audit_id": CERT_AUDIT_ID,
        "payload_sha256": payload_sha256,
        "payload": payload,
    }
    certificate_sha256 = hashlib.sha256(canonical_json_bytes(envelope)).hexdigest()
    return {
        "schema": CERT_SCHEMA,
        "audit_id": CERT_AUDIT_ID,
        "payload_sha256": payload_sha256,
        "certificate_sha256": certificate_sha256,
        "payload": payload,
    }


def _require_no_symlink_path(path: Path) -> None:
    """Reject symlink target or any symlinked ancestor directory."""
    if path.is_symlink():
        raise TorusContentError("SYMLINK_FORBIDDEN", f"symlink path forbidden: {path}")
    for parent in path.parents:
        if parent.is_symlink():
            raise TorusContentError("SYMLINK_ANCESTOR_FORBIDDEN", f"symlink ancestor forbidden: {parent}")


def verify_certificate_dict(cert: Any) -> dict[str, Any]:
    """Fail-closed exact verification of a parsed AUDIT-118B certificate dictionary."""
    if type(cert) is not dict:
        raise TorusContentError("CERT_NOT_DICT", "certificate root must be a strict dict")
    if set(cert.keys()) != _CERT_KEYS:
        raise TorusContentError("CERT_SCHEMA_KEYS", f"unexpected keys: {sorted(map(repr, cert.keys()))}")
    if cert["schema"] != CERT_SCHEMA:
        raise TorusContentError("CERT_SCHEMA_MISMATCH", "schema mismatch")
    if cert["audit_id"] != CERT_AUDIT_ID:
        raise TorusContentError("CERT_AUDIT_ID_MISMATCH", "audit_id mismatch")

    stored_payload_sha = _require_sha256_hex(cert["payload_sha256"], "payload_sha256")
    stored_cert_sha = _require_sha256_hex(cert["certificate_sha256"], "certificate_sha256")

    computed_payload_sha = hashlib.sha256(canonical_json_bytes(cert["payload"])).hexdigest()
    if not hmac.compare_digest(stored_payload_sha, computed_payload_sha):
        raise TorusContentError("PAYLOAD_SHA_MISMATCH", "payload_sha256 mismatch")

    envelope = {
        "schema": cert["schema"],
        "audit_id": cert["audit_id"],
        "payload_sha256": stored_payload_sha,
        "payload": cert["payload"],
    }
    computed_cert_sha = hashlib.sha256(canonical_json_bytes(envelope)).hexdigest()
    if not hmac.compare_digest(stored_cert_sha, computed_cert_sha):
        raise TorusContentError("CERTIFICATE_SHA_MISMATCH", "certificate_sha256 mismatch")

    expected = build_certificate()
    if not hmac.compare_digest(computed_payload_sha, expected["payload_sha256"]):
        raise TorusContentError("RECOMPUTED_PAYLOAD_DRIFT", "payload digest differs from exact recomputation")

    return {
        "valid": True,
        "audit_id": CERT_AUDIT_ID,
        "payload_sha256": computed_payload_sha,
        "certificate_sha256": computed_cert_sha,
    }


def check_certificate_file(path: Path) -> dict[str, Any]:
    """Fail-closed file check: rejects symlinks, oversized files, CR/CRLF, bad UTF-8, or drift."""
    if not isinstance(path, Path):
        raise TorusContentError("INVALID_PATH_TYPE", "path must be a pathlib.Path")
    _require_no_symlink_path(path)
    if not path.is_file():
        raise TorusContentError("CERT_FILE_NOT_FOUND", f"certificate file not found: {path}")
    if path.stat().st_size > MAX_JSON_BYTES:
        raise TorusContentError("CERT_FILE_TOO_LARGE", "certificate file exceeds byte cap")
    raw = path.read_bytes()
    if b"\r" in raw:
        raise TorusContentError("CR_FORBIDDEN", "CR/CRLF line endings forbidden in certificate")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TorusContentError("INVALID_UTF8", f"invalid UTF-8: {exc}") from exc
    parsed = parse_strict_json(text)
    canonical_raw = canonical_json_bytes(parsed)
    if raw not in (canonical_raw, canonical_raw + b"\n"):
        raise TorusContentError("NON_CANONICAL_CERT_BYTES", "certificate file is not canonical JSON")
    return verify_certificate_dict(parsed)


def write_certificate_file(path: Path) -> dict[str, Any]:
    """Write canonical UTF-8 LF certificate file and verify it immediately."""
    _require_no_symlink_path(path)
    cert = build_certificate()
    raw = canonical_json_bytes(cert) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return check_certificate_file(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUDIT-118B torus-knot content weaving exact-Q certifier")
    parser.add_argument("--standalone", action="store_true", help="Run full standalone exact verification")
    parser.add_argument("--json", action="store_true", help="Emit canonical JSON certificate to stdout")
    parser.add_argument("--write", nargs="?", const=str(DEFAULT_CERT_PATH), help="Write canonical certificate file")
    parser.add_argument("--check", type=str, help="Fail-closed verification of a certificate JSON file")
    args = parser.parse_args(argv)

    try:
        if args.check is not None:
            res = check_certificate_file(Path(args.check))
            print(
                f"OK {CERT_AUDIT_ID} payload_sha256={res['payload_sha256']} "
                f"certificate_sha256={res['certificate_sha256']}"
            )
            return 0
        if args.write is not None:
            res = write_certificate_file(Path(args.write))
            print(
                f"WROTE {CERT_AUDIT_ID} payload_sha256={res['payload_sha256']} "
                f"certificate_sha256={res['certificate_sha256']}"
            )
            return 0
        cert = build_certificate()
        if args.json:
            sys.stdout.buffer.write(canonical_json_bytes(cert) + b"\n")
            return 0
        print(
            f"OK {CERT_AUDIT_ID} payload_sha256={cert['payload_sha256']} "
            f"certificate_sha256={cert['certificate_sha256']} "
            f"all_passed={cert['payload']['all_passed']}"
        )
        return 0
    except (TorusContentError, ValueError, RecursionError, OSError) as exc:
        print(f"REJECT {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
