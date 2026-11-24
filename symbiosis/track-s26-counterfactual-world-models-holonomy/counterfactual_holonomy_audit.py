#!/usr/bin/env python3
"""Track S26: Zone-B Hardened CLI, Full Pure-Q Replay & Secondary Algebraic Auditor.

Zero external dependencies, zero floats, zero bare asserts, zero RNG.
Race-free per-component `dir_fd` (`openat`) traversal eliminates intermediate-symlink
TOCTOU (`renameat2` swap race), catches deleted-CWD (`CWD_UNAVAILABLE`), rejects
symlinked `PWD`, FIFO/device hangs (`O_NONBLOCK` + `S_ISREG`), pre-ftruncate hardlink
clobbering (`st_nlink > 1`), zero-size pseudofile OOM (`/proc/kallsyms`), lone UTF-16
surrogates, and flag-like CLI values.
"""
from __future__ import annotations

import errno
from fractions import Fraction
import hashlib
import os
from pathlib import Path
import stat
import sys
from typing import Any, Sequence

_THIS_DIR = str(Path(__file__).resolve().parent)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from counterfactual_holonomy_oracle import (
    CounterfactualHolonomyError,
    MAX_JSON_BYTES,
    SCHEMA_VERSION,
    TRACK_ID,
    build_standalone_certificate,
    canonical_json_bytes,
    parse_exact_rational,
    parse_strict_json_text,
    require_str,
    validate_certificate_payload,
)

_EXACT_PATH_TYPE = type(Path("."))
_READ_CHUNK_BYTES = 65536
_DIR_OPEN_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


# ---------------------------------------------------------------------------
# Race-Free Zone-B File I/O (Per-Component `dir_fd` / `openat` Traversal)
# ---------------------------------------------------------------------------

def _open_dir_chain(anchor: str, parts: Sequence[str]) -> int:
    """Walk directory components atomically via `openat(..., O_DIRECTORY | O_NOFOLLOW)`."""
    try:
        dfd = os.open(anchor, _DIR_OPEN_FLAGS)
    except OSError as exc:
        raise CounterfactualHolonomyError("PATH_STAT_ERROR", f"cannot open anchor dir: {type(exc).__name__}") from exc

    for part in parts:
        try:
            nxt = os.open(part, _DIR_OPEN_FLAGS, dir_fd=dfd)
        except OSError as exc:
            os.close(dfd)
            if exc.errno in (errno.ELOOP, errno.ENOTDIR):
                raise CounterfactualHolonomyError("SYMLINK_FORBIDDEN", "symlink or non-dir forbidden in directory path") from exc
            if exc.errno == errno.ENOENT:
                raise CounterfactualHolonomyError("PATH_NOT_FOUND", "directory component not found") from exc
            raise CounterfactualHolonomyError("PATH_STAT_ERROR", f"cannot traverse dir: {type(exc).__name__}") from exc
        os.close(dfd)
        dfd = nxt
    return dfd


def _validate_path_and_split(path: Any) -> tuple[str, list[str]]:
    if type(path) is not _EXACT_PATH_TYPE:
        raise CounterfactualHolonomyError("INVALID_PATH_TYPE", "path must be exact pathlib.Path")
    raw_str = require_str(str(path), "path")
    if "\x00" in raw_str:
        raise CounterfactualHolonomyError("INVALID_PATH", "path contains NUL byte")

    if not path.is_absolute():
        try:
            Path.cwd()
        except OSError as exc:
            raise CounterfactualHolonomyError("CWD_UNAVAILABLE", f"cannot resolve cwd: {type(exc).__name__}") from exc
        pwd_env = os.environ.get("PWD", "")
        if pwd_env.startswith("/"):
            pwd_path = Path(pwd_env)
            pwd_parts = [p for p in pwd_path.parts[1:] if p not in ("", ".")]
            try:
                pwd_fd = _open_dir_chain(pwd_path.anchor, pwd_parts)
            except CounterfactualHolonomyError as exc:
                if exc.code != "PATH_NOT_FOUND":
                    raise
            else:
                os.close(pwd_fd)
        rel_parts = [p for p in path.parts if p not in ("", ".")]
        return ".", rel_parts
    abs_parts = [p for p in path.parts[1:] if p not in ("", ".")]
    return path.anchor, abs_parts


def require_safe_path(path: Any) -> Path:
    """Validate path type, CWD/PWD, and atomic `openat` directory chain with zero symlinks."""
    anchor, parts = _validate_path_and_split(path)
    if not parts:
        return path
    dfd = _open_dir_chain(anchor, parts[:-1])
    try:
        try:
            st = os.lstat(parts[-1], dir_fd=dfd)
        except FileNotFoundError:
            return path
        except OSError as exc:
            raise CounterfactualHolonomyError("PATH_STAT_ERROR", f"cannot lstat leaf: {type(exc).__name__}") from exc
        if stat.S_ISLNK(st.st_mode):
            raise CounterfactualHolonomyError("SYMLINK_FORBIDDEN", "symlink forbidden at leaf")
    finally:
        os.close(dfd)
    return path


def _open_leaf_no_toctou(path: Path, flags: int, mode: int, err_code: str) -> int:
    """Atomically traverse every directory component via `dir_fd` and open the final leaf."""
    anchor, parts = _validate_path_and_split(path)
    if not parts:
        raise CounterfactualHolonomyError("NON_REGULAR_FILE", "target path refers to a directory")
    dfd = _open_dir_chain(anchor, parts[:-1])
    try:
        try:
            return os.open(parts[-1], flags | os.O_NOFOLLOW | os.O_NONBLOCK, mode, dir_fd=dfd)
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise CounterfactualHolonomyError("SYMLINK_FORBIDDEN", "symlink forbidden at leaf") from exc
            raise CounterfactualHolonomyError(err_code, f"cannot open leaf: {type(exc).__name__}") from exc
    finally:
        os.close(dfd)


def read_regular_file_bytes(path: Path) -> bytes:
    fd = _open_leaf_no_toctou(path, os.O_RDONLY, 0, "FILE_READ_ERROR")
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise CounterfactualHolonomyError("NON_REGULAR_FILE", "target is not a regular file")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, _READ_CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_JSON_BYTES:
                raise CounterfactualHolonomyError("FILE_TOO_LARGE", f"file exceeds {MAX_JSON_BYTES} bytes")
            chunks.append(chunk)
        return b"".join(chunks)
    except CounterfactualHolonomyError:
        raise
    except OSError as exc:
        raise CounterfactualHolonomyError("FILE_READ_ERROR", f"failed reading file: {type(exc).__name__}") from exc
    finally:
        os.close(fd)


def write_regular_file_bytes(path: Path, data: bytes) -> None:
    if type(data) is not bytes:
        raise CounterfactualHolonomyError("INVALID_WRITE_DATA", "data must be exact bytes")
    fd = _open_leaf_no_toctou(path, os.O_WRONLY | os.O_CREAT, 0o644, "FILE_WRITE_ERROR")
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise CounterfactualHolonomyError("NON_REGULAR_FILE", "cannot write to non-regular file")
        if st.st_nlink > 1:
            raise CounterfactualHolonomyError("HARDLINK_FORBIDDEN", "cannot write through hardlinked file")
        os.ftruncate(fd, 0)
        os.lseek(fd, 0, os.SEEK_SET)
        view = memoryview(data)
        written = 0
        while written < len(data):
            written += os.write(fd, view[written:])
    except CounterfactualHolonomyError:
        raise
    except OSError as exc:
        raise CounterfactualHolonomyError("FILE_WRITE_ERROR", f"failed writing file: {type(exc).__name__}") from exc
    finally:
        os.close(fd)


# ---------------------------------------------------------------------------
# Secondary Algebraic Cross-Check of Certificate Payload
# ---------------------------------------------------------------------------

def independent_audit_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Secondary algebraic cross-check over parsed certificate rational strings."""
    t1 = payload["theorem1_paper_reproduction"]
    for fc in t1["flow_and_gauge_cases"]:
        if not fc["cayley_so2_gauge_exact"] or not fc["step2_nilpotent_exact"]:
            raise CounterfactualHolonomyError("AUDIT_T1_FLOW_GAUGE", "flow gauge or step-2 nilpotency failed")
    for mc in t1["minimax_gap_cases"]:
        c_q = parse_exact_rational(mc["C"])
        h_q = parse_exact_rational(mc["h"])
        k_q = c_q * h_q
        rr_q = parse_exact_rational(mc["mse_residual_reuse"])
        b_q = parse_exact_rational(mc["mse_bayes_midpoint"])
        if rr_q != Fraction(4) * c_q * c_q * (h_q**4) or b_q * (Fraction(1) + k_q * k_q) != rr_q:
            raise CounterfactualHolonomyError("AUDIT_T1_MINIMAX_FAILED", "Eq. (56) minimax identity failed")
    vm = t1["variance_matched_transport_cases"]
    if parse_exact_rational(vm[0]["mse_bayes"]) >= parse_exact_rational(vm[0]["mse_vm"]):
        raise CounterfactualHolonomyError("AUDIT_T1_VM_CHAIN", "Pythagorean Bayes < VM violated")
    if parse_exact_rational(vm[0]["mse_vm"]) >= parse_exact_rational(vm[0]["mse_rr"]):
        raise CounterfactualHolonomyError("AUDIT_T1_VM_GAIN", "Pythagorean VM < RR violated")
    if parse_exact_rational(vm[2]["mse_vm"]) != parse_exact_rational(vm[2]["mse_rr"]):
        raise CounterfactualHolonomyError("AUDIT_T1_VM_SYM", "q0=0 symmetric VM == RR tie violated")

    t2 = payload["theorem2_gauge_anisotropy"]
    for dc in t2["diagonal_anisotropy_cases"]:
        th = dc["theta"]
        c_q = parse_exact_rational(dc["C"])
        q0_q = parse_exact_rational(dc["q0"])
        a_q = parse_exact_rational(dc["a"])
        h_q = parse_exact_rational(dc["h"])
        s1_q = parse_exact_rational(dc["sigma1_sq"])
        s2_q = parse_exact_rational(dc["sigma2_sq"])
        s12_q = parse_exact_rational(dc["sigma12_observed"])
        if s12_q != h_q * h_q * Fraction(th) * c_q * (Fraction(2) * q0_q + a_q * h_q) * (s1_q - s2_q):
            raise CounterfactualHolonomyError("AUDIT_T2_SIGMA12", "Sigma_12 anisotropy identity failed")
        if parse_exact_rational(dc["cf_err_sq"]) != 0:
            raise CounterfactualHolonomyError("AUDIT_T2_CF_ZERO", "anisotropic counterfactual error nonzero")
    for gc in t2["general_psd_coordinate_free_cases"]:
        if not gc["commutator_identity_exact"] or parse_exact_rational(gc["recovered_theta_c"]) != Fraction(gc["theta"]) * parse_exact_rational(gc["C"]):
            raise CounterfactualHolonomyError("AUDIT_T2_GENERAL_PSD", "general PSD commutator/recovery failed")
    if not t2["isotropic_negative_control"]["recovery_rejected_cleanly"]:
        raise CounterfactualHolonomyError("AUDIT_T2_ISO_CONTROL", "isotropic negative control not rejected")

    t3 = payload["theorem3_two_step_holonomy"]
    for tc in t3["two_step_isotropic_cases"]:
        exp_tc = Fraction(tc["theta"]) * parse_exact_rational(tc["C"])
        if parse_exact_rational(tc["recovered_theta_c_norm_diff"]) != exp_tc:
            raise CounterfactualHolonomyError("AUDIT_T3_NORM_DIFF", "2-step norm-diff recovery mismatch")
        if parse_exact_rational(tc["recovered_theta_c_universal"]) != exp_tc:
            raise CounterfactualHolonomyError("AUDIT_T3_UNIVERSAL", "2-step universal recovery mismatch")
        if parse_exact_rational(tc["cf_err_sq_extrapolation"]) != 0:
            raise CounterfactualHolonomyError("AUDIT_T3_EXTRAP_ZERO", "2-step extrapolation error nonzero")
    for row in t3["nonlinear_commutator_h6_scaling"]["rows"]:
        if parse_exact_rational(row["two_step_err_sq_div_h6"]) != Fraction(3825, 2):
            raise CounterfactualHolonomyError("AUDIT_T3_H6_SCALING", "nonlinear O(h^6) coefficient != 3825/2")
    sa = t3["self_advection_dg_g_obstruction"]
    if parse_exact_rational(sa["two_step_err_x2"]) != Fraction(9, 20) or not sa["three_step_exact_cancellation"]:
        raise CounterfactualHolonomyError("AUDIT_T3_SELF_ADVECTION", "self-advection witness or 3-step closure failed")
    if not t3["curved_encoder_d2e_obstruction"]["d2e_identity_exact"]:
        raise CounterfactualHolonomyError("AUDIT_T3_CURVED_ENCODER", "curved encoder D^2E obstruction failed")

    t4 = payload["theorem4_multiplicative_steelman"]
    for pc in t4["pure_multiplicative_cases"]:
        if parse_exact_rational(pc["multiplicative_ratio_err"]) != 0:
            raise CounterfactualHolonomyError("AUDIT_T4_MULT", "multiplicative ratio error nonzero")
    for mc in t4["mixed_two_step_cases"]:
        if parse_exact_rational(mc["two_step_cf_err"]) != 0:
            raise CounterfactualHolonomyError("AUDIT_T4_MIXED", "mixed 2-step counterfactual error nonzero")
    if not t4["singular_a0_eq_a1_control"]["inversion_rejected_cleanly"]:
        raise CounterfactualHolonomyError("AUDIT_T4_SINGULAR", "singular a0==a1 control not rejected")

    return {
        "independent_audit_passed": True,
        "minimax_cases_checked": len(t1["minimax_gap_cases"]),
        "anisotropy_cases_checked": len(t2["diagonal_anisotropy_cases"]),
        "two_step_cases_checked": len(t3["two_step_isotropic_cases"]),
        "mixed_cases_checked": len(t4["mixed_two_step_cases"]),
    }


def check_certificate_file(path: Path) -> dict[str, Any]:
    raw = read_regular_file_bytes(path)
    if b"\r" in raw:
        raise CounterfactualHolonomyError("CRLF_FORBIDDEN", "CRLF line endings forbidden in certificate")
    if not raw.endswith(b"\n"):
        raise CounterfactualHolonomyError("MISSING_TRAILING_LF", "certificate must end with a single LF")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CounterfactualHolonomyError("INVALID_UTF8", "certificate is not valid UTF-8") from exc
    cert = parse_strict_json_text(text, require_object=True)
    canonical_raw = canonical_json_bytes(cert)
    if raw != canonical_raw + b"\n":
        raise CounterfactualHolonomyError("NON_CANONICAL_BYTES", "certificate bytes are not canonical ASCII JSON + LF")
    res = validate_certificate_payload(cert, full_replay=True)
    indep = independent_audit_payload(cert["payload"])
    res["canonical_sha256"] = hashlib.sha256(canonical_raw).hexdigest()
    res["file_sha256"] = hashlib.sha256(raw).hexdigest()
    res["independent_audit"] = indep
    return res


def write_certificate_file(path: Path) -> dict[str, Any]:
    cert = build_standalone_certificate()
    canonical_raw = canonical_json_bytes(cert)
    raw = canonical_raw + b"\n"
    write_regular_file_bytes(path, raw)
    return {
        "written": True,
        "schema": SCHEMA_VERSION,
        "track_id": TRACK_ID,
        "payload_sha256": cert["payload_sha256"],
        "certificate_sha256": cert["certificate_sha256"],
        "file_sha256": hashlib.sha256(raw).hexdigest(),
    }


# ---------------------------------------------------------------------------
# Strict Fail-Closed CLI Parsing
# ---------------------------------------------------------------------------

def _parse_cli_argv(argv: Sequence[str]) -> tuple[str, Path | None, bool]:
    if type(argv) not in (list, tuple):
        raise CounterfactualHolonomyError("INVALID_ARGV", "argv must be exact list or tuple")
    for item in argv:
        require_str(item, "argv_item")

    mode: str | None = None
    target: Path | None = None
    as_json = False
    i = 0
    n = len(argv)
    while i < n:
        tok = argv[i]
        if tok == "--json":
            if as_json:
                raise CounterfactualHolonomyError("DUPLICATE_FLAG", "duplicate --json flag")
            as_json = True
            i += 1
        elif tok == "--standalone":
            if mode is not None:
                raise CounterfactualHolonomyError("CONFLICTING_MODE", "multiple mode flags forbidden")
            mode = "standalone"
            i += 1
        elif tok in ("--check", "--write"):
            if mode is not None:
                raise CounterfactualHolonomyError("CONFLICTING_MODE", "multiple mode flags forbidden")
            if i + 1 >= n:
                raise CounterfactualHolonomyError("MISSING_PATH_ARG", f"{tok} requires a path argument")
            val = argv[i + 1]
            if not val or val.startswith("-"):
                raise CounterfactualHolonomyError("INVALID_PATH_ARG", f"{tok} path cannot be empty or flag-like")
            mode = "check" if tok == "--check" else "write"
            target = Path(val)
            i += 2
        else:
            raise CounterfactualHolonomyError("UNKNOWN_FLAG", f"unrecognized CLI argument: {tok}")

    if mode is None:
        mode = "standalone"
    return mode, target, as_json


def main(argv: Sequence[str] | None = None) -> int:
    raw_argv: Any = sys.argv[1:] if argv is None else argv
    try:
        mode, target, as_json = _parse_cli_argv(raw_argv)
        if mode == "standalone":
            out: dict[str, Any] = build_standalone_certificate()
        elif mode == "write":
            out = write_certificate_file(target)  # type: ignore[arg-type]
        else:
            out = check_certificate_file(target)  # type: ignore[arg-type]
    except CounterfactualHolonomyError as exc:
        err = {"valid": False, "error_code": exc.code, "error_message": exc.message}
        sys.stderr.write(canonical_json_bytes(err).decode("ascii") + "\n")
        return 2

    if as_json:
        sys.stdout.write(canonical_json_bytes(out).decode("ascii") + "\n")
    else:
        sys.stdout.write(
            f"OK {SCHEMA_VERSION} payload_sha256={out['payload_sha256']} "
            f"certificate_sha256={out['certificate_sha256']}\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
