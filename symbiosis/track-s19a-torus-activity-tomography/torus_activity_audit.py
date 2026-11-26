#!/usr/bin/env python3
"""
AUDIT-118A Standalone CLI & Fail-Closed Zone-B Certificate Checker (`torus_activity_audit.py`).

Pure Python 3 standard library (`0` floats, `0` bare `assert`s, `0` external deps).
Supports:
  - `--standalone --json`: emit canonical AUDIT-118A certificate JSON to stdout
  - `--write [PATH]`: write canonical certificate JSON to disk and re-verify
  - `--check PATH`: fail-closed Zone-B verification rejecting symlinks, symlinked
    ancestors, oversized files, CRLF/bare-CR, invalid UTF-8, floats/NaN/Infinity,
    duplicate keys, non-ASCII/malformed digests (validated BEFORE `hmac.compare_digest`),
    over-2048-bit / 5000-digit ints, over-depth (>64) trees, non-canonical bytes,
    and any drift from exact pure-Z/Q oracle recomputation (clean exit `2`).
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from torus_activity_oracle import (
    MAX_JSON_BYTES,
    TorusActivityError,
    build_audit118a_payload,
    canonical_json_bytes,
    constant_time_hex64_equal,
    parse_strict_json,
    require_hex64_ascii,
)

CERT_SCHEMA = "audit118a.torus_activity_tomography.certificate.v1"
CERT_AUDIT_ID = "AUDIT-118A"
DEFAULT_CERT_PATH = HERE / "torus_activity_certificate.json"
_CERT_KEYS = frozenset({"schema", "audit_id", "payload_sha256", "certificate_sha256", "payload"})


@lru_cache(maxsize=1)
def _cached_certificate_bytes() -> bytes:
    payload = build_audit118a_payload()
    payload_sha256 = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    envelope = {
        "schema": CERT_SCHEMA,
        "audit_id": CERT_AUDIT_ID,
        "payload_sha256": payload_sha256,
        "payload": payload,
    }
    certificate_sha256 = hashlib.sha256(canonical_json_bytes(envelope)).hexdigest()
    cert = {
        "schema": CERT_SCHEMA,
        "audit_id": CERT_AUDIT_ID,
        "payload_sha256": payload_sha256,
        "certificate_sha256": certificate_sha256,
        "payload": payload,
    }
    return canonical_json_bytes(cert)


def build_certificate() -> dict[str, Any]:
    """Build deterministic self-contained AUDIT-118A certificate."""
    return parse_strict_json(_cached_certificate_bytes().decode("ascii"))


def _require_no_symlink_path(path: Path) -> None:
    if path.is_symlink():
        raise TorusActivityError("SYMLINK_FORBIDDEN", f"symlink path forbidden: {path}")
    for parent in path.parents:
        if parent.is_symlink():
            raise TorusActivityError("SYMLINK_ANCESTOR_FORBIDDEN", f"symlink ancestor forbidden: {parent}")


def verify_certificate_dict(cert: Any) -> dict[str, Any]:
    """Fail-closed exact verification of a parsed AUDIT-118A certificate dictionary."""
    if type(cert) is not dict:
        raise TorusActivityError("CERT_NOT_DICT", "certificate root must be a JSON object")
    for k in cert:
        if type(k) is not str:
            raise TorusActivityError("NON_STR_KEY", "certificate keys must be strict str")
    if set(cert.keys()) != _CERT_KEYS:
        raise TorusActivityError("CERT_SCHEMA_KEYS", f"unexpected keys: {sorted(cert.keys())}")
    if cert["schema"] != CERT_SCHEMA:
        raise TorusActivityError("CERT_SCHEMA_MISMATCH", "schema mismatch")
    if cert["audit_id"] != CERT_AUDIT_ID:
        raise TorusActivityError("CERT_AUDIT_ID_MISMATCH", "audit_id mismatch")

    stored_payload_sha = require_hex64_ascii(cert["payload_sha256"], "payload_sha256")
    stored_cert_sha = require_hex64_ascii(cert["certificate_sha256"], "certificate_sha256")

    computed_payload_sha = hashlib.sha256(canonical_json_bytes(cert["payload"])).hexdigest()
    if not constant_time_hex64_equal(stored_payload_sha, computed_payload_sha, "payload_sha256"):
        raise TorusActivityError("PAYLOAD_SHA_MISMATCH", "payload_sha256 mismatch")

    envelope = {
        "schema": cert["schema"],
        "audit_id": cert["audit_id"],
        "payload_sha256": stored_payload_sha,
        "payload": cert["payload"],
    }
    computed_cert_sha = hashlib.sha256(canonical_json_bytes(envelope)).hexdigest()
    if not constant_time_hex64_equal(stored_cert_sha, computed_cert_sha, "certificate_sha256"):
        raise TorusActivityError("CERTIFICATE_SHA_MISMATCH", "certificate_sha256 mismatch")

    expected = build_certificate()
    if not constant_time_hex64_equal(computed_payload_sha, expected["payload_sha256"], "oracle_parity"):
        raise TorusActivityError("RECOMPUTED_PAYLOAD_DRIFT", "payload digest differs from exact oracle")

    return {
        "valid": True,
        "audit_id": CERT_AUDIT_ID,
        "payload_sha256": computed_payload_sha,
        "certificate_sha256": computed_cert_sha,
    }


def check_certificate_file(path: Path) -> dict[str, Any]:
    """Fail-closed file check: symlinks, size cap, CRLF/CR, UTF-8, canonical bytes, digests, oracle."""
    if not isinstance(path, Path):
        raise TorusActivityError("INVALID_PATH_TYPE", "path must be a pathlib.Path")
    _require_no_symlink_path(path)
    if not path.is_file():
        raise TorusActivityError("CERT_FILE_NOT_FOUND", f"certificate file not found: {path}")
    if path.stat().st_size > MAX_JSON_BYTES:
        raise TorusActivityError("CERT_FILE_TOO_LARGE", "certificate file exceeds byte cap")
    raw = path.read_bytes()
    if b"\r" in raw:
        raise TorusActivityError("CR_LINE_ENDINGS_FORBIDDEN", "CR/CRLF line endings forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TorusActivityError("INVALID_UTF8", f"invalid UTF-8: {exc}") from exc
    parsed = parse_strict_json(text)
    canonical_raw = canonical_json_bytes(parsed)
    if raw not in (canonical_raw, canonical_raw + b"\n"):
        raise TorusActivityError("NON_CANONICAL_CERT_BYTES", "certificate file is not canonical JSON")
    return verify_certificate_dict(parsed)


def write_certificate_file(path: Path) -> dict[str, Any]:
    """Write canonical UTF-8 LF certificate file and verify it immediately."""
    _require_no_symlink_path(path)
    raw = _cached_certificate_bytes() + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return check_certificate_file(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUDIT-118A meta-recursive activity tomography certifier")
    parser.add_argument("--standalone", action="store_true", help="Run standalone exact verification")
    parser.add_argument("--json", action="store_true", help="Emit canonical JSON certificate to stdout")
    parser.add_argument("--write", nargs="?", const=str(DEFAULT_CERT_PATH), help="Write canonical certificate")
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
        raw_bytes = _cached_certificate_bytes()
        if args.json:
            sys.stdout.buffer.write(raw_bytes + b"\n")
            return 0
        cert = parse_strict_json(raw_bytes.decode("ascii"))
        print(
            f"OK {CERT_AUDIT_ID} payload_sha256={cert['payload_sha256']} "
            f"certificate_sha256={cert['certificate_sha256']} "
            f"all_passed={cert['payload']['all_passed']}"
        )
        return 0
    except (TorusActivityError, ValueError, RecursionError, OSError) as exc:
        print(f"REJECT {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
