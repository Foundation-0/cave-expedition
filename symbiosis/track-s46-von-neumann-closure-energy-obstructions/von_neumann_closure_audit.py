#!/usr/bin/env python3
"""Track S46 (Portal 46): Zone-B Hardened CLI, Full Pure-Z/Q Replay & Deep Secondary Auditor.

100% pure Python 3 stdlib, zero IEEE-754 floats, zero bare asserts, zero .isdigit(),
zero mathematical RNG (secrets.token_hex used strictly for atomic temp filename uniqueness).
"""
from __future__ import annotations

import errno
from fractions import Fraction
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import secrets
import stat
import sys
import threading
from typing import Any, Sequence

_THIS_DIR = str(Path(__file__).resolve().parent)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import von_neumann_closure_oracle as oracle  # noqa: E402

MAX_JSON_BYTES = 1_048_576
MAX_ALLOWED_CAP_BYTES = 64 * 1024 * 1024
_READ_CHUNK_BYTES = 65_536
MAX_JSON_DEPTH = 64
MAX_JSON_INT_DIGITS = oracle.MAX_INT_DIGITS
_EXACT_PATH_TYPES = (Path, type(Path()))
_HEX_LOWER = frozenset("0123456789abcdef")
_ASCII_DIGITS = frozenset("0123456789")
_DIR_OPEN_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
_TEMP_NAME_LOCK = threading.Lock()
_TEMP_COUNTER = 0

_CERT_KEYS = frozenset({"schema_version", "track_id", "payload_sha256", "certificate_sha256", "payload"})
_PAYLOAD_KEYS = frozenset({
    "track_id",
    "portal_ref",
    "novelty_class",
    "prior_literature_n0",
    "pillar1_mars_energy_hierarchy",
    "pillar2_leontief_hawkins_simon",
    "pillar3_schur_vitamin_bottleneck",
    "pillar4_radiative_and_eigen",
    "summary",
})
_P1_KEYS = frozenset({
    "pi_enclosure_q",
    "m_atm_1bar_kg_sci",
    "m_atm_over_current_lo_dec6",
    "u_grav_mars_J_sci",
    "e_chem_5eV_28u_hi_J_sci",
    "e_orb_10kms_hi_J_sci",
    "e_nuc_1MeV_lo_J_sci",
    "e_nuc_8MeV_lo_J_sci",
    "nuc_1MeV_over_u_grav_lo_dec6",
    "nuc_8MeV_over_u_grav_lo_dec6",
    "nuc_1MeV_over_orbital_lo_sci",
    "nuc_1MeV_solar_years_lo_dec6",
    "nuc_8MeV_solar_years_lo_dec6",
    "inequality_checks",
    "all_verified",
})
_P1_CHECK_KEYS = frozenset({
    "m_atm_1bar_in_3p87e18_to_3p89e18_kg",
    "m_atm_1bar_gt_150x_current",
    "u_grav_in_4p86e30_to_4p87e30_J",
    "chemical_bond_energy_lt_1e26_J",
    "orbital_import_10kms_lt_2e26_J",
    "nuclear_1MeV_exceeds_70x_u_grav",
    "nuclear_1MeV_exceeds_76x_u_grav",
    "nuclear_8MeV_exceeds_615x_u_grav",
    "nuclear_1MeV_exceeds_1e6x_orbital_import",
})
_P2_KEYS = frozenset({"sectors", "productive_closure", "deficit_negative_control", "all_verified"})
_P2_GOOD_KEYS = frozenset({
    "matrix_q",
    "leading_principal_minors_q",
    "all_leading_minors_positive",
    "det_I_minus_A_q",
    "leontief_inverse_exact_identity",
    "leontief_inverse_all_positive",
    "collatz_wielandt_rho_bounds_q",
    "rho_strictly_lt_1",
    "balanced_growth_surplus_lb_q",
    "verified",
})
_P2_BAD_KEYS = frozenset({
    "matrix_q",
    "leading_principal_minors_q",
    "hawkins_simon_violated",
    "det_I_minus_A_q",
    "collatz_wielandt_rho_bounds_q",
    "rho_strictly_gt_1",
    "verified",
})
_P3_KEYS = frozenset({
    "bulk_sectors",
    "vitamin_sector",
    "unclosed_vitamin_blocked",
    "design_for_closure_restored",
    "all_verified",
})
_P3_BLOCKED_KEYS = frozenset({
    "a_lv_q",
    "a_vl_q",
    "a_vv_q",
    "bulk_det_I_minus_ALL_q",
    "schur_complement_S_VV_q",
    "det_I_minus_A5_q",
    "block_det_identity_exact",
    "schur_strictly_nonpositive",
    "unit_demand_solution_q",
    "autonomous_fixed_point_infeasible",
    "import_leverage_bulk_to_vitamin_q",
    "verified",
})
_P3_RESTORED_KEYS = frozenset({
    "a_lv_q",
    "a_vl_q",
    "a_vv_q",
    "schur_complement_S_VV_q",
    "det_I_minus_A5_q",
    "block_det_identity_exact",
    "schur_strictly_positive",
    "coupled_inverse_all_positive",
    "collatz_wielandt_rho_bounds_q",
    "rho_strictly_lt_1",
    "vitamin_removed_bulk_rho_ub_q",
    "verified",
})
_P4_KEYS = frozenset({"radiative_ceiling", "eigen_metrology_threshold", "all_verified"})
_P4_RAD_KEYS = frozenset({
    "sigma_sb_enclosure_q",
    "emissivity_q",
    "temperature_K",
    "volumetric_heat_W_per_m3",
    "r_crit_m_enclosure_dec6",
    "pi_cancels_identically",
    "cases",
    "all_verified",
})
_P4_RAD_ROW_KEYS = frozenset({
    "name",
    "radius_m_q",
    "compact_heat_to_rad_lo_dec6",
    "compact_heat_to_rad_hi_dec6",
    "compact_cooling_feasible",
    "swarm_split_k",
    "swarm_unit_count_k3",
    "swarm_area_gain_factor",
    "swarm_heat_to_rad_hi_dec6",
    "swarm_cooling_feasible",
    "verified",
})
_P4_EIGEN_KEYS = frozenset({"cases", "metrology_necessary_for_imperfect_fidelity", "all_verified"})
_P4_EIGEN_ROW_KEYS = frozenset({
    "name",
    "expected_regime",
    "q_fidelity_q",
    "length_L",
    "sigma_advantage_q",
    "Q_master_copy_prob_q",
    "Q_crit_q",
    "Q_times_sigma_q",
    "p0_q",
    "p_final_q",
    "p_final_dec6",
    "strictly_increasing",
    "strictly_decreasing",
    "stationary",
    "closed_form_odds_identity_exact",
    "verified",
})
_SUMMARY_KEYS = frozenset({
    "pillar_count",
    "all_four_pillars_verified",
    "float_count_on_trust_path",
    "bare_assert_count",
    "rng_calls",
})


# ============================================================================
# 1. Zone-B Path, CWD, Atomic dir_fd Traversal & Durable 0o600 Atomic Write
# ============================================================================

def _require_utf8_no_surrogate(text: Any, label: str) -> str:
    if type(text) is not str:
        raise oracle.VonNeumannClosureError("INVALID_STR", f"{label}: exact str required")
    oracle.require_ok("\x00" not in text, "NUL_BYTE_FORBIDDEN", f"{label}: NUL byte forbidden")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise oracle.VonNeumannClosureError("INVALID_UTF8_SURROGATE", f"{label}: lone UTF-16 surrogate forbidden") from exc
    return text


def _require_concrete_path(path: Any, label: str) -> Path:
    oracle.require_ok(type(path) in _EXACT_PATH_TYPES, "INVALID_PATH_TYPE", f"{label}: concrete pathlib.Path required")
    _require_utf8_no_surrogate(str(path), label)
    return path


def _safe_cwd(label: str) -> Path:
    try:
        return Path.cwd()
    except OSError as exc:
        raise oracle.VonNeumannClosureError("CWD_UNAVAILABLE", f"{label}: CWD unavailable ({type(exc).__name__})") from exc


def _check_pwd_no_symlinks(label: str) -> None:
    pwd = os.environ.get("PWD", "")
    if pwd.startswith("/"):
        _require_utf8_no_surrogate(pwd, f"{label} PWD")
        pwd_path = Path(pwd)
        try:
            dfd = os.open("/", _DIR_OPEN_FLAGS)
        except OSError as exc:
            raise oracle.VonNeumannClosureError("CWD_UNAVAILABLE", f"{label}: cannot open root for PWD") from exc
        try:
            for part in pwd_path.parts[1:]:
                if part == ".":
                    continue
                try:
                    next_fd = os.open(part, _DIR_OPEN_FLAGS, dir_fd=dfd)
                except OSError as exc:
                    if exc.errno in (errno.ELOOP, errno.ENOTDIR):
                        raise oracle.VonNeumannClosureError(
                            "SYMLINK_ANCESTOR_FORBIDDEN", f"{label}: symlink PWD ancestor forbidden"
                        ) from exc
                    raise oracle.VonNeumannClosureError(
                        "CWD_UNAVAILABLE", f"{label}: PWD ancestor unavailable ({type(exc).__name__})"
                    ) from exc
                os.close(dfd)
                dfd = next_fd
        finally:
            os.close(dfd)


def _open_dir_chain(target: Path, label: str, *, create_parents: bool) -> tuple[int, str]:
    if target.is_absolute():
        parts = target.parts[1:]
    else:
        cwd = _safe_cwd(label)
        _check_pwd_no_symlinks(label)
        parts = cwd.parts[1:] + target.parts
    oracle.require_ok(
        len(parts) >= 1 and parts[-1] not in ("", ".", ".."),
        "NOT_A_REGULAR_FILE",
        f"{label}: path does not name a regular file leaf",
    )
    parent_parts = parts[:-1]
    leaf = parts[-1]
    err_code = "FILE_WRITE_ERROR" if create_parents else "FILE_READ_ERROR"
    try:
        dfd = os.open("/", _DIR_OPEN_FLAGS)
    except OSError as exc:
        raise oracle.VonNeumannClosureError(err_code, f"{label}: cannot open root") from exc
    try:
        for part in parent_parts:
            if part == ".":
                continue
            try:
                next_fd = os.open(part, _DIR_OPEN_FLAGS, dir_fd=dfd)
            except OSError as exc:
                if create_parents and exc.errno == errno.ENOENT:
                    try:
                        os.mkdir(part, 0o755, dir_fd=dfd)
                    except FileExistsError:
                        pass
                    except OSError as mk_exc:
                        raise oracle.VonNeumannClosureError(
                            "FILE_WRITE_ERROR", f"{label}: mkdir failed ({type(mk_exc).__name__})"
                        ) from mk_exc
                    try:
                        next_fd = os.open(part, _DIR_OPEN_FLAGS, dir_fd=dfd)
                    except OSError as re_exc:
                        raise oracle.VonNeumannClosureError(
                            "FILE_WRITE_ERROR", f"{label}: cannot open created dir ({type(re_exc).__name__})"
                        ) from re_exc
                elif exc.errno in (errno.ELOOP, errno.ENOTDIR):
                    raise oracle.VonNeumannClosureError(
                        "SYMLINK_FORBIDDEN", f"{label}: symlink or non-directory ancestor forbidden"
                    ) from exc
                else:
                    raise oracle.VonNeumannClosureError(
                        err_code, f"{label}: cannot traverse ancestor ({type(exc).__name__})"
                    ) from exc
            os.close(dfd)
            dfd = next_fd
        return dfd, leaf
    except BaseException:
        os.close(dfd)
        raise


def read_regular_bytes_capped(path: Path, label: str = "file", max_bytes: int = MAX_JSON_BYTES) -> bytes:
    target = _require_concrete_path(path, label)
    oracle.require_exact_int(max_bytes, "max_bytes", lo=1, hi=MAX_ALLOWED_CAP_BYTES)
    dfd, leaf = _open_dir_chain(target, label, create_parents=False)
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        try:
            fd = os.open(leaf, flags, dir_fd=dfd)
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise oracle.VonNeumannClosureError("SYMLINK_FORBIDDEN", f"{label}: symlink leaf forbidden") from exc
            raise oracle.VonNeumannClosureError(
                "FILE_READ_ERROR", f"{label}: cannot open ({type(exc).__name__})"
            ) from exc
    finally:
        os.close(dfd)

    chunks: list[bytes] = []
    total = 0
    try:
        st_f = os.fstat(fd)
        oracle.require_ok(stat.S_ISREG(st_f.st_mode), "NOT_A_REGULAR_FILE", f"{label}: not a regular file")
        while total <= max_bytes:
            chunk = os.read(fd, min(_READ_CHUNK_BYTES, max_bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
    except oracle.VonNeumannClosureError:
        raise
    except OSError as exc:
        raise oracle.VonNeumannClosureError("FILE_READ_ERROR", f"{label}: read failed ({type(exc).__name__})") from exc
    finally:
        os.close(fd)
    oracle.require_ok(total <= max_bytes, "FILE_TOO_LARGE", f"{label}: exceeds {max_bytes} bytes")
    return b"".join(chunks)


def write_regular_bytes_safe(path: Path, payload: bytes, label: str = "output") -> None:
    global _TEMP_COUNTER
    oracle.require_ok(type(payload) is bytes, "INVALID_PAYLOAD_BYTES", f"{label}: payload must be exact bytes")
    target = _require_concrete_path(path, label)
    dfd, leaf = _open_dir_chain(target, label, create_parents=True)
    tmp_name: str | None = None
    try:
        try:
            st_existing = os.lstat(leaf, dir_fd=dfd)
        except FileNotFoundError:
            st_existing = None
        except OSError as exc:
            raise oracle.VonNeumannClosureError(
                "FILE_WRITE_ERROR", f"{label}: lstat failed ({type(exc).__name__})"
            ) from exc
        if st_existing is not None:
            oracle.require_ok(not stat.S_ISLNK(st_existing.st_mode), "SYMLINK_FORBIDDEN", f"{label}: symlink leaf forbidden")
            oracle.require_ok(stat.S_ISREG(st_existing.st_mode), "NOT_A_REGULAR_FILE", f"{label}: non-regular target")
            oracle.require_ok(st_existing.st_nlink <= 1, "HARDLINK_FORBIDDEN", f"{label}: hardlinked target forbidden")

        pid = os.getpid()
        for _ in range(32):
            with _TEMP_NAME_LOCK:
                _TEMP_COUNTER += 1
                seq_num = _TEMP_COUNTER
                cand = f".s46.{pid}.{seq_num}.{secrets.token_hex(8)}.tmp"
            try:
                fd = os.open(
                    cand,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_NONBLOCK,
                    0o600,
                    dir_fd=dfd,
                )
                tmp_name = cand
                break
            except FileExistsError:
                continue
            except OSError as exc:
                raise oracle.VonNeumannClosureError(
                    "FILE_WRITE_ERROR", f"{label}: create temp failed ({type(exc).__name__})"
                ) from exc
        else:
            raise oracle.VonNeumannClosureError("FILE_WRITE_ERROR", f"{label}: exhausted temp file slots")

        try:
            view = memoryview(payload)
            written = 0
            while written < len(view):
                written += os.write(fd, view[written:])
            os.fsync(fd)
            st_tmp = os.fstat(fd)
            oracle.require_ok(st_tmp.st_nlink == 1, "HARDLINK_FORBIDDEN", f"{label}: temp link count altered")
        except oracle.VonNeumannClosureError:
            raise
        except OSError as exc:
            raise oracle.VonNeumannClosureError(
                "FILE_WRITE_ERROR", f"{label}: write failed ({type(exc).__name__})"
            ) from exc
        finally:
            os.close(fd)

        try:
            os.replace(tmp_name, leaf, src_dir_fd=dfd, dst_dir_fd=dfd)
            tmp_name = None
            os.fsync(dfd)
        except OSError as exc:
            raise oracle.VonNeumannClosureError(
                "FILE_WRITE_ERROR", f"{label}: atomic replace failed ({type(exc).__name__})"
            ) from exc
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name, dir_fd=dfd)
            except OSError:
                pass
        os.close(dfd)


# ============================================================================
# 2. Strict ASCII Parsers, Binding 3,321-Bit Cap & Canonical JSON
# ============================================================================

def require_hex64_lower_ascii(val: Any, label: str = "sha256") -> str:
    s = _require_utf8_no_surrogate(val, label)
    oracle.require_ok(len(s) == 64, "INVALID_HEX64", f"{label}: expected 64-char lowercase ASCII hex")
    for ch in s:
        oracle.require_ok(ch in _HEX_LOWER, "INVALID_HEX64", f"{label}: non-hex-lowercase char")
    return s


def _parse_bounded_int(token: str) -> int:
    s = _require_utf8_no_surrogate(token, "json_int")
    oracle.require_ok(s != "-0", "INVALID_JSON_INT", "negative zero forbidden")
    digits = s[1:] if s.startswith("-") else s
    oracle.require_ok(len(digits) >= 1, "INVALID_JSON_INT", "JSON int has no digits")
    oracle.require_ok(len(digits) <= MAX_JSON_INT_DIGITS, "INT_DIGIT_LIMIT", "JSON int exceeds digit cap")
    oracle.require_ok(digits == "0" or not digits.startswith("0"), "INVALID_JSON_INT", "leading zero forbidden")
    for ch in digits:
        oracle.require_ok(ch in _ASCII_DIGITS, "INVALID_JSON_INT", "non-ASCII digit forbidden")
    val = int(s)
    oracle.require_ok(val.bit_length() <= oracle.MAX_INT_BITS, "INT_BIT_LIMIT", "JSON int exceeds 3,321-bit cap")
    return val


def parse_exact_rational(token: Any, label: str = "rational") -> Fraction:
    s = _require_utf8_no_surrogate(token, label)
    parts = s.split("/")
    oracle.require_ok(len(parts) in (1, 2), "INVALID_RATIONAL", f"{label}: expected 'n' or 'n/d'")
    num = _parse_bounded_int(parts[0])
    if len(parts) == 1:
        return oracle.require_exact_fraction(Fraction(num, 1), label)
    den = _parse_bounded_int(parts[1])
    oracle.require_ok(den >= 2, "INVALID_RATIONAL", f"{label}: denominator must be >= 2")
    oracle.require_ok(math.gcd(abs(num), den) == 1, "NON_CANONICAL_RATIONAL", f"{label}: not in lowest terms")
    return oracle.require_exact_fraction(Fraction(num, den), label)


def _validate_json_tree(root: Any, label: str = "json") -> None:
    stack: list[tuple[Any, int]] = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        oracle.require_ok(depth <= MAX_JSON_DEPTH, "JSON_DEPTH_LIMIT", f"{label}: nesting exceeds {MAX_JSON_DEPTH}")
        t = type(node)
        if node is None or t is bool:
            continue
        if t is int:
            oracle.require_ok(node.bit_length() <= oracle.MAX_INT_BITS, "INT_BIT_LIMIT", f"{label}: int exceeds 3,321 bits")
            continue
        if t is str:
            _require_utf8_no_surrogate(node, label)
            continue
        if t is list:
            nxt = depth + 1
            for item in node:
                stack.append((item, nxt))
            continue
        if t is dict:
            nxt = depth + 1
            for k, v in node.items():
                _require_utf8_no_surrogate(k, f"{label}.key")
                stack.append((v, nxt))
            continue
        raise oracle.VonNeumannClosureError("FORBIDDEN_JSON_TYPE", f"{label}: unsupported type {t.__name__}")


def _reject_float(token: str) -> Any:
    raise oracle.VonNeumannClosureError("FLOAT_LITERAL_FORBIDDEN", f"float literal forbidden: {token}")


def _reject_constant(token: str) -> Any:
    raise oracle.VonNeumannClosureError("NONFINITE_LITERAL_FORBIDDEN", f"non-finite constant forbidden: {token}")


def _strict_pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        _require_utf8_no_surrogate(k, "json_key")
        oracle.require_ok(k not in out, "DUPLICATE_JSON_KEY", f"duplicate key {k!r}")
        out[k] = v
    return out


def parse_strict_json_text(text: Any, *, require_object: bool = True, max_bytes: int = MAX_JSON_BYTES) -> Any:
    s = _require_utf8_no_surrogate(text, "json_text")
    oracle.require_exact_bool(require_object, "require_object")
    oracle.require_exact_int(max_bytes, "max_bytes", lo=1, hi=MAX_ALLOWED_CAP_BYTES)
    oracle.require_ok(len(s.encode("utf-8")) <= max_bytes, "JSON_TOO_LARGE", "JSON text exceeds byte cap")
    try:
        parsed = json.loads(
            s,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
            parse_int=_parse_bounded_int,
            object_pairs_hook=_strict_pairs_hook,
        )
    except oracle.VonNeumannClosureError:
        raise
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise oracle.VonNeumannClosureError("JSON_PARSE_ERROR", f"invalid JSON ({type(exc).__name__})") from exc
    _validate_json_tree(parsed, "parsed_json")
    if require_object and type(parsed) is not dict:
        raise oracle.VonNeumannClosureError("JSON_ROOT_NOT_OBJECT", "JSON root must be an object")
    return parsed


def canonical_json_bytes(obj: Any) -> bytes:
    _validate_json_tree(obj, "canonical_json")
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _sha256_canonical(obj: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


# ============================================================================
# 3. Deep Schema-Safe Secondary Auditor (Live Algebraic & Strict Nested Keys)
# ============================================================================

def _req_dict(val: Any, label: str, expected_keys: frozenset[str]) -> dict[str, Any]:
    oracle.require_ok(type(val) is dict, "INVALID_SCHEMA_DICT", f"{label}: exact dict required")
    oracle.require_ok(frozenset(val.keys()) == expected_keys, "INVALID_SCHEMA_KEYS", f"{label}: key set mismatch")
    return val


def _req_list(val: Any, label: str, exact_len: int) -> list[Any]:
    oracle.require_ok(type(val) is list and len(val) == exact_len, "INVALID_SCHEMA_LIST", f"{label}: list len {exact_len} required")
    return val


def _req_int_f(obj: dict[str, Any], key: str, label: str) -> int:
    return oracle.require_exact_int(obj[key], f"{label}.{key}")


def _req_bool_f(obj: dict[str, Any], key: str, label: str) -> bool:
    return oracle.require_exact_bool(obj[key], f"{label}.{key}")


def _parse_q_matrix(val: Any, dim: int, label: str) -> list[list[Fraction]]:
    rows = _req_list(val, label, dim)
    return [[parse_exact_rational(tok, f"{label}[{i}][{j}]") for j, tok in enumerate(_req_list(row, f"{label}[{i}]", dim))] for i, row in enumerate(rows)]


def _parse_q_vec(val: Any, dim: int, label: str) -> list[Fraction]:
    items = _req_list(val, label, dim)
    return [parse_exact_rational(tok, f"{label}[{i}]") for i, tok in enumerate(items)]


def secondary_audit_payload(payload: Any) -> dict[str, Any]:
    """Fail-closed strict-nested-keyset + live algebraic cross-check across ALL 4 pillars."""
    pl = _req_dict(payload, "payload", _PAYLOAD_KEYS)
    p1 = _req_dict(pl["pillar1_mars_energy_hierarchy"], "p1", _P1_KEYS)
    p1_chk = _req_dict(p1["inequality_checks"], "p1.checks", _P1_CHECK_KEYS)
    p2 = _req_dict(pl["pillar2_leontief_hawkins_simon"], "p2", _P2_KEYS)
    p2_g = _req_dict(p2["productive_closure"], "p2.good", _P2_GOOD_KEYS)
    p2_b = _req_dict(p2["deficit_negative_control"], "p2.bad", _P2_BAD_KEYS)
    p3 = _req_dict(pl["pillar3_schur_vitamin_bottleneck"], "p3", _P3_KEYS)
    p3_b = _req_dict(p3["unclosed_vitamin_blocked"], "p3.blocked", _P3_BLOCKED_KEYS)
    p3_r = _req_dict(p3["design_for_closure_restored"], "p3.restored", _P3_RESTORED_KEYS)
    p4 = _req_dict(pl["pillar4_radiative_and_eigen"], "p4", _P4_KEYS)
    p4_rad = _req_dict(p4["radiative_ceiling"], "p4.rad", _P4_RAD_KEYS)
    p4_eig = _req_dict(p4["eigen_metrology_threshold"], "p4.eigen", _P4_EIGEN_KEYS)
    summ = _req_dict(pl["summary"], "summary", _SUMMARY_KEYS)

    # Exact reference recomputation of lightweight P1..P4 invariants (< 10 ms!)
    ref_p1 = oracle.certify_pillar1_mars_energy_hierarchy()
    ref_p2 = oracle.certify_pillar2_leontief_hawkins_simon()
    ref_p3 = oracle.certify_pillar3_schur_vitamin_bottleneck()
    ref_p4 = oracle.certify_pillar4_radiative_and_eigen()

    # Validate strict bool types on ALL bool fields across P1..P4 + summary (catches bool-as-int even on full_replay=False!)
    p1_bools_ok = all((
        _req_bool_f(p1, "all_verified", "p1"),
        *(_req_bool_f(p1_chk, k, "p1.checks") for k in _P1_CHECK_KEYS),
    ))
    # Parse P1 rationals
    pi_enc = _parse_q_vec(p1["pi_enclosure_q"], 2, "p1.pi")
    p1_ok = all((p1_bools_ok, pi_enc == [Fraction(333, 106), Fraction(355, 113)], p1 == ref_p1))

    # P2: Live linear-algebra cross-check on submitted matrices + strict types
    a_g = _parse_q_matrix(p2_g["matrix_q"], 4, "p2.good.A")
    a_b = _parse_q_matrix(p2_b["matrix_q"], 4, "p2.bad.A")
    det_g, _ = oracle.exact_det_and_inv_q(oracle.identity_minus_q(a_g))
    det_b, _ = oracle.exact_det_and_inv_q(oracle.identity_minus_q(a_b))
    p2_bools_ok = all((
        _req_bool_f(p2, "all_verified", "p2"),
        _req_bool_f(p2_g, "all_leading_minors_positive", "p2.good"),
        _req_bool_f(p2_g, "leontief_inverse_exact_identity", "p2.good"),
        _req_bool_f(p2_g, "leontief_inverse_all_positive", "p2.good"),
        _req_bool_f(p2_g, "rho_strictly_lt_1", "p2.good"),
        _req_bool_f(p2_g, "verified", "p2.good"),
        _req_bool_f(p2_b, "hawkins_simon_violated", "p2.bad"),
        _req_bool_f(p2_b, "rho_strictly_gt_1", "p2.bad"),
        _req_bool_f(p2_b, "verified", "p2.bad"),
    ))
    p2_ok = all((
        p2_bools_ok,
        parse_exact_rational(p2_g["det_I_minus_A_q"], "p2.good.det") == det_g,
        parse_exact_rational(p2_b["det_I_minus_A_q"], "p2.bad.det") == det_b,
        p2 == ref_p2,
    ))

    # P3: Live Schur complement cross-check + strict types
    s_b = parse_exact_rational(p3_b["schur_complement_S_VV_q"], "p3.b.S")
    d5_b = parse_exact_rational(p3_b["det_I_minus_A5_q"], "p3.b.det5")
    dll = parse_exact_rational(p3_b["bulk_det_I_minus_ALL_q"], "p3.b.detLL")
    s_r = parse_exact_rational(p3_r["schur_complement_S_VV_q"], "p3.r.S")
    d5_r = parse_exact_rational(p3_r["det_I_minus_A5_q"], "p3.r.det5")
    p3_bools_ok = all((
        _req_bool_f(p3, "all_verified", "p3"),
        _req_bool_f(p3_b, "block_det_identity_exact", "p3.b"),
        _req_bool_f(p3_b, "schur_strictly_nonpositive", "p3.b"),
        _req_bool_f(p3_b, "autonomous_fixed_point_infeasible", "p3.b"),
        _req_bool_f(p3_b, "verified", "p3.b"),
        _req_bool_f(p3_r, "block_det_identity_exact", "p3.r"),
        _req_bool_f(p3_r, "schur_strictly_positive", "p3.r"),
        _req_bool_f(p3_r, "coupled_inverse_all_positive", "p3.r"),
        _req_bool_f(p3_r, "rho_strictly_lt_1", "p3.r"),
        _req_bool_f(p3_r, "verified", "p3.r"),
    ))
    p3_ok = all((p3_bools_ok, d5_b == dll * s_b, d5_r == dll * s_r, p3 == ref_p3))

    # P4: Strict nested row keysets & exact int/bool types across radiative + Eigen cases
    rad_cases = _req_list(p4_rad["cases"], "p4.rad.cases", 4)
    rad_rows_ok = True
    for i, row in enumerate(rad_cases):
        rd = _req_dict(row, f"p4.rad[{i}]", _P4_RAD_ROW_KEYS)
        k_sp = _req_int_f(rd, "swarm_split_k", f"p4.rad[{i}]")
        if not all((
            _req_int_f(rd, "swarm_unit_count_k3", f"p4.rad[{i}]") == k_sp**3,
            _req_int_f(rd, "swarm_area_gain_factor", f"p4.rad[{i}]") == k_sp,
            type(_req_bool_f(rd, "compact_cooling_feasible", f"p4.rad[{i}]")) is bool,
            _req_bool_f(rd, "swarm_cooling_feasible", f"p4.rad[{i}]"),
            _req_bool_f(rd, "verified", f"p4.rad[{i}]"),
        )):
            rad_rows_ok = False

    eig_cases = _req_list(p4_eig["cases"], "p4.eigen.cases", 4)
    eig_rows_ok = True
    for i, row in enumerate(eig_cases):
        ed = _req_dict(row, f"p4.eigen[{i}]", _P4_EIGEN_ROW_KEYS)
        _req_int_f(ed, "length_L", f"p4.eigen[{i}]")
        _req_bool_f(ed, "strictly_increasing", f"p4.eigen[{i}]")
        _req_bool_f(ed, "strictly_decreasing", f"p4.eigen[{i}]")
        _req_bool_f(ed, "stationary", f"p4.eigen[{i}]")
        if not all((
            _req_bool_f(ed, "closed_form_odds_identity_exact", f"p4.eigen[{i}]"),
            _req_bool_f(ed, "verified", f"p4.eigen[{i}]"),
        )):
            eig_rows_ok = False

    p4_ok = all((
        _req_int_f(p4_rad, "temperature_K", "p4.rad") == 400,
        _req_int_f(p4_rad, "volumetric_heat_W_per_m3", "p4.rad") == 1000,
        _req_bool_f(p4_rad, "pi_cancels_identically", "p4.rad"),
        _req_bool_f(p4_rad, "all_verified", "p4.rad"),
        _req_bool_f(p4_eig, "metrology_necessary_for_imperfect_fidelity", "p4.eig"),
        _req_bool_f(p4_eig, "all_verified", "p4.eig"),
        _req_bool_f(p4, "all_verified", "p4"),
        rad_rows_ok,
        eig_rows_ok,
        p4 == ref_p4,
    ))

    ok_all = all((
        pl["track_id"] == oracle.TRACK_ID,
        pl["portal_ref"] == "Portal 46",
        pl["novelty_class"] == "N1",
        pl["prior_literature_n0"] == oracle.build_payload()["prior_literature_n0"],
        p1_ok,
        p2_ok,
        p3_ok,
        p4_ok,
        _req_int_f(summ, "pillar_count", "summary") == 4,
        _req_bool_f(summ, "all_four_pillars_verified", "summary"),
        _req_int_f(summ, "float_count_on_trust_path", "summary") == 0,
        _req_int_f(summ, "bare_assert_count", "summary") == 0,
        _req_int_f(summ, "rng_calls", "summary") == 0,
    ))
    oracle.require_ok(ok_all, "SECONDARY_AUDIT_FAILED", "secondary algebraic cross-check failed")
    return {"secondary_audit_passed": True, "pillars_audited": 4}


def build_standalone_certificate() -> dict[str, Any]:
    payload = oracle.build_payload()
    payload_sha = _sha256_canonical(payload)
    outer = {
        "schema_version": oracle.SCHEMA_VERSION,
        "track_id": oracle.TRACK_ID,
        "payload_sha256": payload_sha,
        "payload": payload,
    }
    cert_sha = _sha256_canonical(outer)
    return {
        "schema_version": oracle.SCHEMA_VERSION,
        "track_id": oracle.TRACK_ID,
        "payload_sha256": payload_sha,
        "certificate_sha256": cert_sha,
        "payload": payload,
    }


def verify_certificate_dict(cert: Any, *, full_replay: bool = True) -> dict[str, Any]:
    oracle.require_exact_bool(full_replay, "full_replay")
    oracle.require_ok(type(cert) is dict, "INVALID_CERT_TYPE", "certificate must be exact dict")
    _validate_json_tree(cert, "cert")
    oracle.require_ok(frozenset(cert.keys()) == _CERT_KEYS, "INVALID_CERT_KEYS", "certificate keys mismatch")
    oracle.require_ok(cert["schema_version"] == oracle.SCHEMA_VERSION, "INVALID_SCHEMA", "schema_version mismatch")
    oracle.require_ok(cert["track_id"] == oracle.TRACK_ID, "INVALID_TRACK_ID", "track_id mismatch")
    oracle.require_ok(type(cert["payload"]) is dict, "INVALID_PAYLOAD_TYPE", "payload must be exact dict")

    claimed_p = require_hex64_lower_ascii(cert["payload_sha256"], "payload_sha256")
    claimed_c = require_hex64_lower_ascii(cert["certificate_sha256"], "certificate_sha256")

    actual_p = _sha256_canonical(cert["payload"])
    oracle.require_ok(hmac.compare_digest(claimed_p, actual_p), "PAYLOAD_SHA256_MISMATCH", "payload_sha256 mismatch")

    outer = {
        "schema_version": cert["schema_version"],
        "track_id": cert["track_id"],
        "payload_sha256": claimed_p,
        "payload": cert["payload"],
    }
    actual_c = _sha256_canonical(outer)
    oracle.require_ok(hmac.compare_digest(claimed_c, actual_c), "CERT_SHA256_MISMATCH", "certificate_sha256 mismatch")

    sec = secondary_audit_payload(cert["payload"])
    if full_replay:
        ref = build_standalone_certificate()
        oracle.require_ok(hmac.compare_digest(actual_p, ref["payload_sha256"]), "REPLAY_MISMATCH", "replay mismatch")

    return {
        "valid": True,
        "schema_version": oracle.SCHEMA_VERSION,
        "track_id": oracle.TRACK_ID,
        "payload_sha256": actual_p,
        "certificate_sha256": actual_c,
        "full_replay": full_replay,
        "secondary_audit": sec,
    }


def check_certificate_file(path: Path, *, full_replay: bool = True) -> dict[str, Any]:
    raw = read_regular_bytes_capped(path, "certificate", MAX_JSON_BYTES)
    oracle.require_ok(b"\r" not in raw, "CRLF_FORBIDDEN", "CRLF line endings forbidden")
    oracle.require_ok(raw.endswith(b"\n"), "MISSING_TRAILING_LF", "certificate must end with LF")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise oracle.VonNeumannClosureError("INVALID_UTF8", "certificate is not valid UTF-8") from exc
    cert = parse_strict_json_text(text, require_object=True)
    canon = canonical_json_bytes(cert)
    oracle.require_ok(raw == canon + b"\n", "NON_CANONICAL_BYTES", "certificate is not canonical ASCII JSON + LF")
    res = verify_certificate_dict(cert, full_replay=full_replay)
    res["canonical_sha256"] = hashlib.sha256(canon).hexdigest()
    res["file_sha256"] = hashlib.sha256(raw).hexdigest()
    return res


def write_certificate_file(path: Path) -> dict[str, Any]:
    cert = build_standalone_certificate()
    canon = canonical_json_bytes(cert)
    raw = canon + b"\n"
    write_regular_bytes_safe(path, raw, "certificate")
    return {
        "written": True,
        "schema_version": oracle.SCHEMA_VERSION,
        "track_id": oracle.TRACK_ID,
        "payload_sha256": cert["payload_sha256"],
        "certificate_sha256": cert["certificate_sha256"],
        "file_sha256": hashlib.sha256(raw).hexdigest(),
    }


# ============================================================================
# 4. Strict Fail-Closed CLI (Space & Equals Flag-Like Rejection)
# ============================================================================

def _reject_bad_path_arg(tok: str, val: str) -> Path:
    oracle.require_ok(bool(val) and not val.startswith("-"), "INVALID_PATH_ARG", f"{tok} path empty or flag-like")
    return Path(val)


def _parse_cli_argv(argv: Sequence[str]) -> tuple[str, Path | None, bool]:
    oracle.require_ok(type(argv) in (list, tuple), "INVALID_ARGV", "argv must be list or tuple")
    for item in argv:
        _require_utf8_no_surrogate(item, "argv_item")

    mode: str | None = None
    target: Path | None = None
    as_json = False
    i = 0
    n = len(argv)
    while i < n:
        tok = argv[i]
        if tok == "--json":
            oracle.require_ok(not as_json, "DUPLICATE_FLAG", "duplicate --json flag")
            as_json = True
            i += 1
        elif tok == "--standalone":
            oracle.require_ok(mode is None, "CONFLICTING_MODE", "multiple mode flags forbidden")
            mode = "standalone"
            i += 1
        elif tok in ("--check", "--write"):
            oracle.require_ok(mode is None, "CONFLICTING_MODE", "multiple mode flags forbidden")
            oracle.require_ok(i + 1 < n, "MISSING_PATH_ARG", f"{tok} requires a path argument")
            target = _reject_bad_path_arg(tok, argv[i + 1])
            mode = "check" if tok == "--check" else "write"
            i += 2
        elif tok.startswith("--check=") or tok.startswith("--write="):
            oracle.require_ok(mode is None, "CONFLICTING_MODE", "multiple mode flags forbidden")
            flag_name, val = tok.split("=", 1)
            target = _reject_bad_path_arg(flag_name, val)
            mode = "check" if flag_name == "--check" else "write"
            i += 1
        else:
            raise oracle.VonNeumannClosureError("UNKNOWN_FLAG", f"unrecognized CLI argument: {tok}")

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
    except oracle.VonNeumannClosureError as exc:
        err = {"valid": False, "error_code": exc.code, "error_message": exc.detail}
        sys.stderr.write(canonical_json_bytes(err).decode("ascii") + "\n")
        return 2

    if as_json:
        sys.stdout.write(canonical_json_bytes(out).decode("ascii") + "\n")
    else:
        sys.stdout.write(
            f"OK {oracle.SCHEMA_VERSION} payload_sha256={out['payload_sha256']} "
            f"certificate_sha256={out['certificate_sha256']}\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
