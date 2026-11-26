#!/usr/bin/env python3
"""
Standalone CLI for Track S20c Physical Telemetry Portal (`--generate` / `--check`).

Zero floats, zero bare `assert`s, strict Zone-B fail-closed validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import Sequence

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from physical_telemetry_oracle import (
    TelemetryPortalError,
    build_certificate,
    canonical_json_bytes,
    load_safe_bytes,
    parse_strict_json_text,
    require_safe_path,
    require_str,
    validate_certificate_payload,
)

DEFAULT_CERT_PATH = _HERE / "physical_telemetry_certificate.json"


def verify_certificate_file(
    cert_path: Path,
    *,
    track_dir: Path | None = None,
    full_replay: bool = True,
) -> dict[str, object]:
    raw = load_safe_bytes(cert_path, "certificate_file")
    if b"\r" in raw:
        raise TelemetryPortalError("CR_FORBIDDEN", "certificate file must use LF endings only")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TelemetryPortalError("INVALID_UTF8", "certificate file is not valid UTF-8") from exc
    obj = parse_strict_json_text(text, require_object=True)
    expected_raw = canonical_json_bytes(obj) + b"\n"
    if raw != expected_raw:
        raise TelemetryPortalError("NON_CANONICAL_CERT_BYTES", "certificate file bytes are not canonical JSON + LF")
    res = validate_certificate_payload(obj, track_dir=track_dir, full_replay=full_replay)
    res["file_sha256"] = hashlib.sha256(raw).hexdigest()
    return res


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Track S20c Physical Telemetry Portal CLI")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--generate", action="store_true", help="Generate canonical certificate JSON")
    group.add_argument("--check", metavar="CERT_PATH", help="Verify canonical certificate JSON against raw telemetry")
    parser.add_argument("--out", default=str(DEFAULT_CERT_PATH), help="Output path for --generate")
    parser.add_argument("--track-dir", default=str(_HERE), help="Track directory containing FETCH_MANIFEST.json")
    parser.add_argument("--no-replay", action="store_true", help="Validate schema, digests, and gate consistency only")
    parser.add_argument("--observed-only", action="store_true", help="Replay Stage-A provenance and observed Window A/B operators without surrogates")
    parser.add_argument("--full-replay", action="store_true", help="Recompute all 99x3 exact surrogates and known-answer controls (default for --check)")

    try:
        if argv is not None:
            if type(argv) not in (list, tuple):
                raise TelemetryPortalError("INVALID_CLI_ARGS", "argv must be a strict list or tuple")
            raw_argv: list[str] | None = [require_str(x, "argv", min_len=0) for x in argv]
        else:
            raw_argv = None
        args = parser.parse_args(raw_argv)
        replay_flags = int(args.no_replay) + int(args.observed_only) + int(args.full_replay)
        if replay_flags > 1:
            raise TelemetryPortalError("INVALID_CLI_ARGS", "replay mode flags (--no-replay, --observed-only, --full-replay) are mutually exclusive")
        track_dir = require_safe_path(Path(args.track_dir), "track_dir")
        if args.generate:
            out_path = require_safe_path(Path(args.out), "out")
            if os.path.lexists(out_path) and not stat.S_ISREG(os.lstat(out_path).st_mode):
                raise TelemetryPortalError("FILE_WRITE_ERROR", "out path must not be a directory or special file")
            cert = build_certificate(track_dir)
            raw = canonical_json_bytes(cert) + b"\n"
            try:
                out_path.write_bytes(raw)
            except OSError as exc:
                raise TelemetryPortalError("FILE_WRITE_ERROR", f"out write failed: {exc.strerror}") from exc
            summary = {
                "generated": True,
                "file_sha256": hashlib.sha256(raw).hexdigest(),
                "payload_sha256": cert["payload_sha256"],
                "certificate_sha256": cert["certificate_sha256"],
                "controls_passed": cert["payload"]["known_answer_controls"]["all_controls_passed"],
                "verdicts": {
                    k: v["verdict"] for k, v in cert["payload"]["cross_domain_verdicts"].items()
                },
            }
            print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
            return 0
        target_cert = args.check if args.check is not None else str(DEFAULT_CERT_PATH)
        cert_path = require_safe_path(Path(target_cert), "check_path")
        replay_dir = None if args.no_replay else track_dir
        do_full = not args.observed_only
        res = verify_certificate_file(cert_path, track_dir=replay_dir, full_replay=do_full)
        print(json.dumps(res, sort_keys=True, separators=(",", ":")))
        return 0
    except TelemetryPortalError as exc:
        print(json.dumps({"valid": False, "error_code": exc.code, "error": exc.message}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
