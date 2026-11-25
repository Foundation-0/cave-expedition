#!/usr/bin/env python3
"""
Track S20c: Real Public Raw Physical Telemetry Portal (MP-04).

Zero-float pure-Z/Q cross-domain relational operator oracle & Zone-B-hardened
certificate engine testing stripped real physical telemetry from 4 unrelated
scientific domains (LIGO GWOSC GW150914 strain, USGS Boulder G5 geomagnetic
superstorm, NOAA CO-OPS San Francisco tide, USGS NWIS Potomac River discharge)
under Gate-8 pre-registered exact surrogate nulls (IID, Block-16, WHT-256).

Zero floats on the verification/trust path; zero bare `assert` statements;
full `strict_cert_io`-grade Zone-B hardening (`MAX_INT_BITS=2048`,
`MAX_JSON_DEPTH=64`, strict 64-lowercase-ASCII-hex before `hmac.compare_digest`,
unpaired surrogate & NUL path guards, zero untrusted-int f-string formatting).
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from fractions import Fraction
import hashlib
import hmac
import json
from operator import add, sub
import os
from pathlib import Path
import stat
from typing import Any

SCHEMA_VERSION = "s20c-physical-telemetry-cert/v1"
TRACK_ID = "TRACK-S20C"
MAX_JSON_DEPTH = 64
MAX_JSON_BYTES = 2_000_000
MAX_INT_BITS = 2048
MAX_INT_DIGITS = 620
MAX_SEQ_LEN = 4096
WINDOW_LEN = 256
TOTAL_SAMPLES = 512
SEAM1_WINDOW = 32
SURROGATE_COUNT = 99
BLOCK_SIZE = 16
ALPHA_NUM = 5
ALPHA_DEN = 100
_HEX_LOWER = frozenset("0123456789abcdef")
_STREAM_IDS = ("STREAM_A", "STREAM_B", "STREAM_C", "STREAM_D")
_NULL_FAMILIES = ("IID_PERM", "BLOCK_16", "WHT_PHASE")
_HYPOTHESIS_IDS = (
    "H1_SEAM1_SHOCK",
    "H2a_SEAM3_HVG_BETTI1",
    "H2b_SEAM3_IRREV_PHI",
    "H3a_F3_TRANSIENT_WITNESS",
    "H3b_F3_COMMUTATOR",
)


class TelemetryPortalError(ValueError):
    """Fail-closed typed error (never stripped under `python3 -O`)."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


# ---------------------------------------------------------------------------
# Zone-B strict primitive & canonical JSON I/O helpers (zero floats, zero DoS)
# ---------------------------------------------------------------------------


def _require_valid_utf8_str(s: str, label: str = "str") -> str:
    try:
        s.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise TelemetryPortalError("INVALID_UTF8", f"{label} contains unpaired UTF-16 surrogate") from exc
    return s


def require_int(
    val: Any,
    label: str = "int",
    *,
    lo: int | None = None,
    hi: int | None = None,
) -> int:
    if type(val) is not int:
        raise TelemetryPortalError("INVALID_INT_TYPE", f"{label} must be strict int, got {type(val).__name__}")
    blen = val.bit_length()
    if blen > MAX_INT_BITS:
        raise TelemetryPortalError("INT_BIT_LIMIT", f"{label} bit_length={blen} exceeds {MAX_INT_BITS}")
    if lo is not None:
        if type(lo) is not int:
            raise TelemetryPortalError("INVALID_INT_BOUND", f"{label} lo must be strict int")
        if val < lo:
            raise TelemetryPortalError("INT_BELOW_MIN", f"{label} bit_length={blen} below min_bits={lo.bit_length()}")
    if hi is not None:
        if type(hi) is not int:
            raise TelemetryPortalError("INVALID_INT_BOUND", f"{label} hi must be strict int")
        if val > hi:
            raise TelemetryPortalError("INT_ABOVE_MAX", f"{label} bit_length={blen} above max_bits={hi.bit_length()}")
    return val


def require_bool(val: Any, label: str = "bool") -> bool:
    if type(val) is not bool:
        raise TelemetryPortalError("INVALID_BOOL_TYPE", f"{label} must be strict bool, got {type(val).__name__}")
    return val


def require_str(val: Any, label: str = "str", *, min_len: int = 1, max_len: int = 1024) -> str:
    if type(val) is not str:
        raise TelemetryPortalError("INVALID_STR_TYPE", f"{label} must be strict str, got {type(val).__name__}")
    _require_valid_utf8_str(val, label)
    n = len(val)
    if n < min_len:
        raise TelemetryPortalError("STR_TOO_SHORT", f"{label} length {n} < min_bits={min_len.bit_length()}")
    if n > max_len:
        raise TelemetryPortalError("STR_TOO_LONG", f"{label} length {n} > max_bits={max_len.bit_length()}")
    return val


def require_seq(
    val: Any,
    label: str = "seq",
    *,
    min_len: int = 1,
    max_len: int = MAX_SEQ_LEN,
) -> tuple[Any, ...]:
    if type(val) not in (list, tuple):
        raise TelemetryPortalError("INVALID_SEQ_TYPE", f"{label} must be strict list or tuple")
    n = len(val)
    if n < min_len:
        raise TelemetryPortalError("SEQ_TOO_SHORT", f"{label} length {n} < min_bits={min_len.bit_length()}")
    if n > max_len:
        raise TelemetryPortalError("SEQ_TOO_LONG", f"{label} length {n} > max_bits={max_len.bit_length()}")
    return tuple(val)


def require_mapping(val: Any, label: str = "mapping") -> dict[str, Any]:
    if type(val) is not dict:
        raise TelemetryPortalError("INVALID_MAPPING_TYPE", f"{label} must be strict dict")
    for k in val:
        if type(k) is not str:
            raise TelemetryPortalError("NON_STR_KEY", f"{label} keys must be strict str")
        _require_valid_utf8_str(k, f"{label}.key")
    return val


def require_hex64_ascii(val: Any, label: str = "sha256") -> str:
    if type(val) is not str:
        raise TelemetryPortalError("INVALID_DIGEST_TYPE", f"{label} must be strict str")
    if len(val) != 64:
        raise TelemetryPortalError("INVALID_DIGEST_LEN", f"{label} must have length 64")
    for ch in val:
        if ch not in _HEX_LOWER:
            raise TelemetryPortalError("INVALID_DIGEST_HEX", f"{label} must be lowercase ASCII hex")
    return val


def constant_time_hex64_equal(left: Any, right: Any, label: str = "sha256") -> bool:
    a = require_hex64_ascii(left, f"{label}.left")
    b = require_hex64_ascii(right, f"{label}.right")
    return hmac.compare_digest(a, b)


def fmt_q(q: Fraction) -> str:
    if type(q) is not Fraction:
        raise TelemetryPortalError("INVALID_FRACTION_TYPE", "q must be strict Fraction")
    nb = q.numerator.bit_length()
    db = q.denominator.bit_length()
    if nb > MAX_INT_BITS or db > MAX_INT_BITS:
        raise TelemetryPortalError("FRACTION_BIT_LIMIT", f"fraction bit_lengths=({nb},{db}) exceed {MAX_INT_BITS}")
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"


def parse_q_str(val: Any, label: str = "q") -> Fraction:
    s = require_str(val, label, min_len=1, max_len=1300)
    parts = s.split("/")
    if len(parts) == 1:
        num = _parse_capped_int_token(parts[0])
        return Fraction(num, 1)
    if len(parts) == 2:
        num = _parse_capped_int_token(parts[0])
        den = _parse_capped_int_token(parts[1])
        if den <= 0:
            raise TelemetryPortalError("INVALID_FRACTION_DEN", f"{label} denominator must be positive")
        return Fraction(num, den)
    raise TelemetryPortalError("INVALID_FRACTION_STR", f"{label} malformed rational string")


def validate_json_value(obj: Any, *, max_depth: int = MAX_JSON_DEPTH) -> None:
    limit = require_int(max_depth, "max_depth", lo=1, hi=128)
    stack: list[tuple[Any, int]] = [(obj, 0)]
    while stack:
        cur, depth = stack.pop()
        if depth > limit:
            raise TelemetryPortalError("MAX_DEPTH_EXCEEDED", f"JSON nesting exceeds {limit}")
        t = type(cur)
        if t is dict:
            for k, v in cur.items():
                if type(k) is not str:
                    raise TelemetryPortalError("NON_STR_KEY", "JSON object keys must be strict str")
                _require_valid_utf8_str(k, "json_key")
                stack.append((v, depth + 1))
        elif t is list:
            for item in cur:
                stack.append((item, depth + 1))
        elif t is int:
            blen = cur.bit_length()
            if blen > MAX_INT_BITS:
                raise TelemetryPortalError("INT_BIT_LIMIT", f"JSON int bit_length={blen} exceeds {MAX_INT_BITS}")
        elif t is str:
            _require_valid_utf8_str(cur, "json_str")
        elif t is bool or cur is None:
            continue
        elif t is float:
            raise TelemetryPortalError("FLOAT_FORBIDDEN", "float values are forbidden in exact JSON")
        else:
            raise TelemetryPortalError("UNSUPPORTED_JSON_TYPE", f"unsupported JSON type {t.__name__}")


def _reject_float_token(tok: str) -> Any:
    raise TelemetryPortalError("JSON_FLOAT_FORBIDDEN", f"float literal forbidden: {tok!r}")


def _reject_constant_token(tok: str) -> Any:
    raise TelemetryPortalError("JSON_CONSTANT_FORBIDDEN", f"non-RFC8259 constant forbidden: {tok!r}")


def _parse_capped_int_token(tok: str) -> int:
    digits = tok[1:] if tok.startswith("-") else tok
    if not digits or not digits.isascii() or not digits.isdigit():
        raise TelemetryPortalError("INVALID_INT_TOKEN", "integer token must be ASCII digits")
    if len(digits) > MAX_INT_DIGITS:
        raise TelemetryPortalError("INT_DIGIT_LIMIT", f"integer token exceeds {MAX_INT_DIGITS} digits")
    val = int(tok)
    blen = val.bit_length()
    if blen > MAX_INT_BITS:
        raise TelemetryPortalError("INT_BIT_LIMIT", f"integer token bit_length={blen} exceeds {MAX_INT_BITS}")
    return val


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise TelemetryPortalError("JSON_DUPLICATE_KEY", f"duplicate JSON key: {k!r}")
        out[k] = v
    return out


def parse_strict_json_text(raw_text: str, *, require_object: bool = True) -> Any:
    req_obj = require_bool(require_object, "require_object")
    if type(raw_text) is not str:
        raise TelemetryPortalError("INVALID_JSON_INPUT", "JSON text must be strict str")
    encoded = _require_valid_utf8_str(raw_text, "json_text").encode("utf-8")
    if len(encoded) > MAX_JSON_BYTES:
        raise TelemetryPortalError("JSON_TOO_LARGE", f"JSON exceeds {MAX_JSON_BYTES} bytes")
    if not raw_text.strip():
        raise TelemetryPortalError("EMPTY_JSON_INPUT", "JSON text must be non-empty")
    try:
        obj = json.loads(
            raw_text,
            parse_float=_reject_float_token,
            parse_constant=_reject_constant_token,
            parse_int=_parse_capped_int_token,
            object_pairs_hook=_reject_duplicate_keys,
        )
    except TelemetryPortalError:
        raise
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise TelemetryPortalError("JSON_PARSE_ERROR", f"invalid JSON: {type(exc).__name__}") from exc
    if req_obj and type(obj) is not dict:
        raise TelemetryPortalError("JSON_ROOT_NOT_OBJECT", "JSON root must be a strict object")
    validate_json_value(obj)
    return obj


def canonical_json_bytes(obj: Any) -> bytes:
    validate_json_value(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def sha256_canonical(obj: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def require_safe_path(path: Path, label: str = "path") -> Path:
    if type(path) is not type(Path()):
        raise TelemetryPortalError("INVALID_PATH_TYPE", f"{label} must be a strict Path")
    raw_str = str(path)
    if "\x00" in raw_str:
        raise TelemetryPortalError("INVALID_PATH_NUL", f"{label} contains embedded NUL byte")
    _require_valid_utf8_str(raw_str, label)
    if not path.is_absolute():
        pwd_env = os.environ.get("PWD")
        if pwd_env and os.path.realpath(pwd_env) == os.path.realpath(os.getcwd()):
            pwd_path = Path(pwd_env)
            if pwd_path.is_symlink():
                raise TelemetryPortalError("SYMLINK_ANCESTOR_FORBIDDEN", f"{label} has symlink PWD")
            for p_anc in pwd_path.parents:
                if p_anc.is_symlink():
                    raise TelemetryPortalError("SYMLINK_ANCESTOR_FORBIDDEN", f"{label} has symlink PWD ancestor")
    if path.is_symlink():
        raise TelemetryPortalError("SYMLINK_FORBIDDEN", f"{label} must not be a symlink")
    for parent in path.parents:
        if parent.is_symlink():
            raise TelemetryPortalError("SYMLINK_ANCESTOR_FORBIDDEN", f"{label} has symlink ancestor")
    return path


def load_safe_bytes(path: Path, label: str = "file") -> bytes:
    require_safe_path(path, label)
    try:
        st = path.stat()
    except OSError as exc:
        raise TelemetryPortalError("FILE_STAT_ERROR", f"{label} unreadable: {exc.strerror}") from exc
    if not stat.S_ISREG(st.st_mode):
        raise TelemetryPortalError("NON_REGULAR_FILE", f"{label} must be a regular file")
    if st.st_size > MAX_JSON_BYTES:
        raise TelemetryPortalError("FILE_TOO_LARGE", f"{label} exceeds {MAX_JSON_BYTES} bytes")
    try:
        return path.read_bytes()
    except OSError as exc:
        raise TelemetryPortalError("FILE_READ_ERROR", f"{label} read failed: {exc.strerror}") from exc


def load_strict_json_file(path: Path, label: str = "json_file") -> dict[str, Any]:
    raw = load_safe_bytes(path, label)
    if b"\r" in raw:
        raise TelemetryPortalError("CR_FORBIDDEN", f"{label} must use LF line endings only")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TelemetryPortalError("INVALID_UTF8", f"{label} is not valid UTF-8") from exc
    return parse_strict_json_text(text, require_object=True)


# ---------------------------------------------------------------------------
# Stage A: Lossless decimal -> exact integer ingestion & monotone ranking
# ---------------------------------------------------------------------------


def parse_decimal_to_scaled_int(raw_val: Any, scale_exp10: int, label: str = "sample") -> int:
    """Convert raw decimal string/Decimal/int into exact scaled integer via DecimalTuple (zero rounding, zero DoS)."""
    exp10 = require_int(scale_exp10, "scale_exp10", lo=0, hi=60)
    if type(raw_val) is int:
        val = require_int(raw_val, label)
        if val == 0:
            return 0
        scaled_int = val * (10**exp10)
        return require_int(scaled_int, label)
    if type(raw_val) is Decimal:
        dec = raw_val
    elif type(raw_val) is str:
        s = require_str(raw_val, label, min_len=1, max_len=128).strip()
        try:
            dec = Decimal(s)
        except InvalidOperation as exc:
            raise TelemetryPortalError("INVALID_DECIMAL", f"{label} is not a valid decimal") from exc
    else:
        raise TelemetryPortalError("INVALID_SAMPLE_TYPE", f"{label} unsupported type {type(raw_val).__name__}")
    if not dec.is_finite():
        raise TelemetryPortalError("NON_FINITE_SAMPLE", f"{label} must be finite")
    tup = dec.as_tuple()
    digits = tup.digits
    exp: int = tup.exponent  # type: ignore[assignment]
    first_nz = -1
    last_nz = -1
    for i, d in enumerate(digits):
        if d != 0:
            if first_nz < 0:
                first_nz = i
            last_nz = i
    if first_nz < 0:
        return 0
    sig = digits[first_nz : last_nz + 1]
    eff_exp = exp + (len(digits) - 1 - last_nz) + exp10
    if eff_exp < 0:
        raise TelemetryPortalError("PRECISION_LOSS", f"{label} loses digits at 10^{exp10}")
    if len(sig) + eff_exp > MAX_INT_DIGITS:
        raise TelemetryPortalError("INT_DIGIT_LIMIT", f"{label} scaled digits exceed {MAX_INT_DIGITS}")
    mag = int("".join(str(d) for d in sig) + ("0" * eff_exp))
    val = -mag if tup.sign else mag
    return require_int(val, label)


def _require_int_vec(
    vec: Any,
    label: str = "vec",
    *,
    min_len: int = 4,
    max_len: int = MAX_SEQ_LEN,
) -> tuple[int, ...]:
    seq = require_seq(vec, label, min_len=min_len, max_len=max_len)
    for item in seq:
        if type(item) is not int:
            raise TelemetryPortalError("INVALID_INT_TYPE", f"{label} elements must be strict int")
        if item.bit_length() > MAX_INT_BITS:
            raise TelemetryPortalError("INT_BIT_LIMIT", f"{label} element exceeds {MAX_INT_BITS} bits")
    return seq  # type: ignore[return-value]


def load_stripped_physical_streams(track_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, tuple[int, ...]]]:
    """Verify FETCH_MANIFEST & PREREG_S20C SHA pins and load Stage-A stripped exact int series."""
    require_safe_path(track_dir, "track_dir")
    manifest_path = track_dir / "FETCH_MANIFEST.json"
    prereg_path = track_dir / "PREREG_S20C.json"
    manifest_bytes = load_safe_bytes(manifest_path, "FETCH_MANIFEST.json")
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    manifest = load_strict_json_file(manifest_path, "FETCH_MANIFEST.json")
    prereg = load_strict_json_file(prereg_path, "PREREG_S20C.json")
    if not constant_time_hex64_equal(prereg.get("fetch_manifest_sha256"), manifest_sha, "fetch_manifest_sha256"):
        raise TelemetryPortalError("MANIFEST_PIN_MISMATCH", "PREREG_S20C fetch_manifest_sha256 mismatch")

    sources = require_seq(manifest.get("sources"), "sources", min_len=4, max_len=4)
    streams: dict[str, tuple[int, ...]] = {}
    for entry in sources:
        src = require_mapping(entry, "source")
        sid = require_str(src.get("stream_id"), "stream_id")
        rel_file = require_str(src.get("local_file"), "local_file")
        if rel_file.startswith("/") or ".." in Path(rel_file).parts:
            raise TelemetryPortalError("INVALID_LOCAL_PATH", f"unsafe local_file for {sid}")
        raw_path = track_dir / rel_file
        raw_bytes = load_safe_bytes(raw_path, rel_file)
        actual_sha = hashlib.sha256(raw_bytes).hexdigest()
        if not constant_time_hex64_equal(src.get("local_sha256"), actual_sha, f"{sid}.local_sha256"):
            raise TelemetryPortalError("RAW_SHA_MISMATCH", f"raw file SHA mismatch for {sid}")
        scale_exp10 = require_int(src.get("scale_exp10"), f"{sid}.scale_exp10", lo=0, hi=60)
        slice_len = require_int(src.get("slice_length"), f"{sid}.slice_length", lo=TOTAL_SAMPLES, hi=TOTAL_SAMPLES)

        try:
            if sid == "STREAM_A":
                lines = [ln.strip() for ln in raw_bytes.decode("ascii").splitlines() if ln.strip()]
                raw_samples: list[Any] = lines[:slice_len]
            elif sid == "STREAM_B":
                obj = json.loads(
                    raw_bytes.decode("utf-8"),
                    parse_float=Decimal,
                    parse_int=_parse_capped_int_token,
                    parse_constant=_reject_constant_token,
                )
                vals = [v for v in obj["values"][0]["values"] if v is not None]
                raw_samples = vals[:slice_len]
            elif sid == "STREAM_C":
                obj = json.loads(
                    raw_bytes.decode("utf-8"),
                    parse_float=Decimal,
                    parse_int=_parse_capped_int_token,
                    parse_constant=_reject_constant_token,
                )
                vals = [row["v"] for row in obj["data"] if row.get("v")]
                raw_samples = vals[:slice_len]
            elif sid == "STREAM_D":
                obj = json.loads(
                    raw_bytes.decode("utf-8"),
                    parse_float=Decimal,
                    parse_int=_parse_capped_int_token,
                    parse_constant=_reject_constant_token,
                )
                pts = obj["value"]["timeSeries"][0]["values"][0]["value"]
                vals = [p["value"] for p in pts if p.get("value") not in (None, "", "-999999")]
                raw_samples = vals[:slice_len]
            else:
                raise TelemetryPortalError("UNKNOWN_STREAM_ID", f"unsupported stream_id {sid!r}")
        except TelemetryPortalError:
            raise
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError, RecursionError) as exc:
            raise TelemetryPortalError("RAW_PARSE_ERROR", f"failed to parse raw telemetry for {sid}: {type(exc).__name__}") from exc

        if len(raw_samples) != TOTAL_SAMPLES:
            raise TelemetryPortalError("INSUFFICIENT_SAMPLES", f"{sid} yielded {len(raw_samples)} != {TOTAL_SAMPLES}")
        streams[sid] = tuple(
            parse_decimal_to_scaled_int(v, scale_exp10, f"{sid}[{idx}]") for idx, v in enumerate(raw_samples)
        )
    return manifest, prereg, streams


def doubled_mid_ranks(series: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    """Exact monotone-invariant doubled mid-ranks in [0, 2*(N-1)] (sum == N*(N-1) identically)."""
    vals = _require_int_vec(series, "series", min_len=4, max_len=MAX_SEQ_LEN)
    n = len(vals)
    order = sorted(range(n), key=lambda idx: vals[idx])
    ranks = [0] * n
    pos = 0
    while pos < n:
        end = pos + 1
        cur_val = vals[order[pos]]
        while end < n and vals[order[end]] == cur_val:
            end += 1
        # Exact sum of low rank (pos) and high rank (end - 1)
        doubled_rank = pos + (end - 1)
        for k in range(pos, end):
            ranks[order[k]] = doubled_rank
        pos = end
    if len(set(vals)) < 2:
        raise TelemetryPortalError("CONSTANT_SERIES", "series must not be constant")
    return tuple(ranks)


def center_doubled_ranks(ranks: tuple[int, ...]) -> tuple[int, ...]:
    """Shift exact doubled mid-ranks by -(N-1) so exact sum is identically zero."""
    vals = _require_int_vec(ranks, "ranks", min_len=4, max_len=MAX_SEQ_LEN)
    offset = len(vals) - 1
    return tuple(r - offset for r in vals)


# ---------------------------------------------------------------------------
# Pure-Z/Q Exact Linear Algebra & Relational Operators (OP1, OP2, OP3)
# ---------------------------------------------------------------------------


def _det_adj_3x3_int(m: tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]) -> tuple[int, tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]]:
    """Exact determinant and adjugate of a 3x3 integer matrix."""
    (a, b, c), (d, e, f), (g, h, i) = m
    c00 = e * i - f * h
    c01 = -(d * i - f * g)
    c02 = d * h - e * g
    c10 = -(b * i - c * h)
    c11 = a * i - c * g
    c12 = -(a * h - b * g)
    c20 = b * f - c * e
    c21 = -(a * f - c * d)
    c22 = a * e - b * d
    det = a * c00 + b * c01 + c * c02
    adj = (
        (c00, c10, c20),
        (c01, c11, c21),
        (c02, c12, c22),
    )
    return det, adj


def _exact_median_pair(pairs: list[tuple[int, int]]) -> tuple[int, int]:
    """Exact O(K) integer median of positive rational pairs (num, den) with zero floats (fast 64-bit monotone key + exact tie-break)."""
    n = len(pairs)
    target = n // 2
    keyed = [((a << 64) // b, a, b) for a, b in pairs]
    keyed.sort(key=lambda t: t[0])
    mid_key = keyed[target][0]
    lo = target
    while lo > 0 and keyed[lo - 1][0] == mid_key:
        lo -= 1
    hi = target
    while hi + 1 < n and keyed[hi + 1][0] == mid_key:
        hi += 1
    if lo == hi:
        return (keyed[target][1], keyed[target][2])
    # Exact cross-multiplication quickselect on tied bucket only
    arr = [(keyed[i][1], keyed[i][2]) for i in range(lo, hi + 1)]
    sub_target = target - lo
    while True:
        pa, pb = arr[len(arr) // 2]
        less: list[tuple[int, int]] = []
        equal: list[tuple[int, int]] = []
        greater: list[tuple[int, int]] = []
        for item in arr:
            lhs = item[0] * pb
            rhs = pa * item[1]
            if lhs < rhs:
                less.append(item)
            elif lhs > rhs:
                greater.append(item)
            else:
                equal.append(item)
        if sub_target < len(less):
            arr = less
        elif sub_target < len(less) + len(equal):
            return equal[0]
        else:
            sub_target -= len(less) + len(equal)
            arr = greater


def op1_seam1_leverage_shock(centered: tuple[int, ...], *, window_w: int = SEAM1_WINDOW) -> dict[str, Any]:
    """SEAM-1: Exact sliding rank-1 Sherman-Morrison leverage shock ratio max_h / median_h over Q."""
    vals = _require_int_vec(centered, "centered", min_len=8, max_len=MAX_SEQ_LEN)
    n = len(vals)
    w = require_int(window_w, "window_w", lo=4, hi=n - 4)
    scale_c = n - 1
    lam = scale_c * scale_c

    # Lag-3 vectors u_s = (scale_c, vals[s+1], vals[s]) for s = 0 .. n-2
    g00 = lam + w * lam
    g01 = 0
    g02 = 0
    g11 = lam
    g12 = 0
    g22 = lam
    for s in range(w):
        u1 = vals[s + 1]
        u2 = vals[s]
        g01 += scale_c * u1
        g02 += scale_c * u2
        g11 += u1 * u1
        g12 += u1 * u2
        g22 += u2 * u2

    # Evaluate causal rank-1 leverage h_t = q_t / (1 + q_t) for s = w .. n-2
    lev_pairs: list[tuple[int, int]] = []
    max_num = -1
    max_den = 1
    max_idx = -1

    for idx in range(w, n - 1):
        u1 = vals[idx + 1]
        u2 = vals[idx]
        c00 = g11 * g22 - g12 * g12
        c01 = g02 * g12 - g01 * g22
        c02 = g01 * g12 - g02 * g11
        c11 = g00 * g22 - g02 * g02
        c12 = g01 * g02 - g00 * g12
        c22 = g00 * g11 - g01 * g01
        det = g00 * c00 + g01 * c01 + g02 * c02
        num_q = (
            scale_c * (c00 * scale_c + c01 * u1 + c02 * u2)
            + u1 * (c01 * scale_c + c11 * u1 + c12 * u2)
            + u2 * (c02 * scale_c + c12 * u1 + c22 * u2)
        )
        den_h = det + num_q
        lev_pairs.append((num_q, den_h))
        if num_q * max_den > max_num * den_h:
            max_num = num_q
            max_den = den_h
            max_idx = idx + 1

        # Slide window forward by 1: add (u1, u2), remove (o1, o2)
        o1 = vals[idx - w + 1]
        o2 = vals[idx - w]
        g01 += scale_c * (u1 - o1)
        g02 += scale_c * (u2 - o2)
        g11 += u1 * u1 - o1 * o1
        g12 += u1 * u2 - o1 * o2
        g22 += u2 * u2 - o2 * o2

    med_num, med_den = _exact_median_pair(lev_pairs)
    median_h = Fraction(med_num, med_den)
    max_h = Fraction(max_num, max_den)
    shock_ratio = max_h / median_h
    return {
        "steps": len(lev_pairs),
        "max_leverage_index": max_idx,
        "max_h": max_h,
        "median_h": median_h,
        "shock_ratio": shock_ratio,
    }


def op2_seam3_hvg_and_ordinal(ranks: tuple[int, ...]) -> dict[str, Any]:
    """SEAM-3: Exact HVG H^1 Betti-1 + directed ordinal (m=3) Hodge-curl irreversibility."""
    vals = _require_int_vec(ranks, "ranks", min_len=4, max_len=MAX_SEQ_LEN)
    n = len(vals)
    # O(N) exact monotonic-stack Horizontal Visibility Graph
    stack: list[int] = []
    edges = 0
    for j in range(n):
        rj = vals[j]
        while stack and vals[stack[-1]] < rj:
            stack.pop()
            edges += 1
        if stack:
            edges += 1
            if vals[stack[-1]] == rj:
                stack.pop()
        stack.append(j)
    betti1 = edges - (n - 1)

    # Exact ordinal m=3 pattern states: 0..5 for strict permutations, 6 for any tie
    states: list[int] = []
    for t in range(n - 2):
        a, b, c = vals[t], vals[t + 1], vals[t + 2]
        if a == b or b == c or a == c:
            states.append(6)
        elif a < b:
            if b < c:
                states.append(0)  # a < b < c
            elif a < c:
                states.append(1)  # a < c < b
            else:
                states.append(2)  # c < a < b
        else:
            if a < c:
                states.append(3)  # b < a < c
            elif b < c:
                states.append(4)  # b < c < a
            else:
                states.append(5)  # c < b < a

    counts = [[0] * 7 for _ in range(7)]
    for t in range(len(states) - 1):
        counts[states[t]][states[t + 1]] += 1

    asym_num = 0
    asym_den = 0
    signed_net_flux = 0
    for a in range(7):
        for b in range(a + 1, 7):
            cab = counts[a][b]
            cba = counts[b][a]
            diff = cab - cba
            tot = cab + cba
            asym_num += diff * diff
            asym_den += tot * tot
            signed_net_flux += diff
    phi_asym = Fraction(asym_num, asym_den) if asym_den > 0 else Fraction(0, 1)

    # Explicit directed Farkas cycle witness on positive transitions (2-cycle or 3-cycle)
    farkas_cycle: list[int] = []
    for a in range(7):
        if farkas_cycle:
            break
        for b in range(a + 1, 7):
            if counts[a][b] > 0 and counts[b][a] > 0:
                farkas_cycle = [a, b, a]
                break
    if not farkas_cycle:
        for a in range(7):
            if farkas_cycle:
                break
            for b in range(7):
                if b == a or counts[a][b] == 0:
                    continue
                for c in range(7):
                    if counts[b][c] > 0 and counts[c][a] > 0:
                        farkas_cycle = [a, b, c, a]
                        break
                if farkas_cycle:
                    break

    return {
        "hvg_edges": edges,
        "hvg_betti1": betti1,
        "forward_hvg_dag_grounded": True,
        "ordinal_phi_asym": phi_asym,
        "ordinal_signed_net_flux": signed_net_flux,
        "farkas_directed_cycle_witness": farkas_cycle,
        "has_directed_cycle": len(farkas_cycle) > 0,
    }


def exact_symmetric_inertia_3x3(mat: list[list[Fraction]]) -> tuple[int, int, int]:
    """Exact Sylvester inertia (n_pos, n_neg, n_zero) of a 3x3 symmetric rational matrix."""
    rows = require_seq(mat, "mat", min_len=3, max_len=3)
    a: list[list[Fraction]] = []
    for r_idx in range(3):
        row = require_seq(rows[r_idx], f"mat[{r_idx}]", min_len=3, max_len=3)
        parsed_row: list[Fraction] = []
        for c_idx in range(3):
            entry = row[c_idx]
            if type(entry) is not Fraction:
                raise TelemetryPortalError("INVALID_FRACTION_TYPE", "matrix entries must be strict Fraction")
            parsed_row.append(entry)
        a.append(parsed_row)
    if a[0][1] != a[1][0] or a[0][2] != a[2][0] or a[1][2] != a[2][1]:
        raise TelemetryPortalError("NON_SYMMETRIC_MATRIX", "matrix must be symmetric")
    n_pos = 0
    n_neg = 0
    n_zero = 0
    idx = 0
    n = 3
    while idx < n:
        # Search for non-zero diagonal pivot in [idx..n-1]
        piv = -1
        for k in range(idx, n):
            if a[k][k] != 0:
                piv = k
                break
        if piv != -1:
            if piv != idx:
                a[idx], a[piv] = a[piv], a[idx]
                for r in range(n):
                    a[r][idx], a[r][piv] = a[r][piv], a[r][idx]
            d = a[idx][idx]
            if d > 0:
                n_pos += 1
            else:
                n_neg += 1
            for r in range(idx + 1, n):
                factor = a[r][idx] / d
                if factor != 0:
                    for c in range(idx + 1, n):
                        a[r][c] -= factor * a[idx][c]
            idx += 1
            continue
        # All remaining diagonal entries are zero: check for non-zero off-diagonal 2x2 hyperbolic block
        pair: tuple[int, int] | None = None
        for r in range(idx, n):
            for c in range(r + 1, n):
                if a[r][c] != 0:
                    pair = (r, c)
                    break
            if pair is not None:
                break
        if pair is None:
            n_zero += n - idx
            break
        # Symmetric 2x2 zero-diagonal hyperbolic block [[0, b], [b, 0]] has eigenvalues +b, -b -> (1 pos, 1 neg)
        r0, c0 = pair
        if r0 != idx:
            a[idx], a[r0] = a[r0], a[idx]
            for k in range(n):
                a[k][idx], a[k][r0] = a[k][r0], a[k][idx]
        if c0 != idx + 1:
            a[idx + 1], a[c0] = a[c0], a[idx + 1]
            for k in range(n):
                a[k][idx + 1], a[k][c0] = a[k][c0], a[k][idx + 1]
        b = a[idx][idx + 1]
        n_pos += 1
        n_neg += 1
        # Schur complement onto remaining 1x1 block (if idx == 0, remaining row/col is 2)
        if idx + 2 < n:
            u = a[2][idx]
            v = a[2][idx + 1]
            a[2][2] -= (2 * u * v) / b
        idx += 2
    return (n_pos, n_neg, n_zero)


def _is_schur_stable_cubic(c2: Fraction, c1: Fraction, c0: Fraction) -> bool:
    """Exact 3rd-order Jury / Schur-Cohn stability test for p(mu) = mu^3 + c2*mu^2 + c1*mu + c0."""
    p_plus1 = Fraction(1, 1) + c2 + c1 + c0
    neg_p_minus1 = Fraction(1, 1) - c2 + c1 - c0
    return (
        p_plus1 > 0
        and neg_p_minus1 > 0
        and abs(c0) < 1
        and abs(c0 * c0 - 1) > abs(c0 * c2 - c1)
    )


def _passes_alpha(p_val: Fraction) -> bool:
    return p_val <= Fraction(ALPHA_NUM, ALPHA_DEN)


def op3_f3_var1_inertia(centered: tuple[int, ...]) -> dict[str, Any]:
    """F3: Exact rational ridge VAR(1) Schur-Cohn stability, Bareiss/Congruence In(I - T^T T), commutator."""
    vals = _require_int_vec(centered, "centered", min_len=4, max_len=MAX_SEQ_LEN)
    n = len(vals)
    lam = (n - 1) * (n - 1)
    s00 = 0
    s01 = 0
    s02 = 0
    s11 = 0
    s12 = 0
    s22 = 0
    c00 = 0
    c01 = 0
    c02 = 0
    for t in range(2, n - 1):
        z0 = vals[t]
        z1 = vals[t - 1]
        z2 = vals[t - 2]
        w0 = vals[t + 1]
        s00 += z0 * z0
        s01 += z0 * z1
        s02 += z0 * z2
        s11 += z1 * z1
        s12 += z1 * z2
        s22 += z2 * z2
        c00 += w0 * z0
        c01 += w0 * z1
        c02 += w0 * z2

    cz = (
        (c00, c01, c02),
        (s00, s01, s02),
        (s01, s11, s12),
    )
    det_g, adj_g = _det_adj_3x3_int(
        (
            (s00 + lam, s01, s02),
            (s01, s11 + lam, s12),
            (s02, s12, s22 + lam),
        )
    )

    # Exact integer numerator matrix T_num = C_z @ adj(G_z), so T = T_num / det_g
    t_num = [
        [sum(cz[i][k] * adj_g[k][j] for k in range(3)) for j in range(3)]
        for i in range(3)
    ]

    # Exact characteristic polynomial p_T(mu) = mu^3 + c2*mu^2 + c1*mu + c0
    tr_num = t_num[0][0] + t_num[1][1] + t_num[2][2]
    m01 = t_num[0][0] * t_num[1][1] - t_num[0][1] * t_num[1][0]
    m02 = t_num[0][0] * t_num[2][2] - t_num[0][2] * t_num[2][0]
    m12 = t_num[1][1] * t_num[2][2] - t_num[1][2] * t_num[2][1]
    det_t_num, _ = _det_adj_3x3_int(
        ((t_num[0][0], t_num[0][1], t_num[0][2]), (t_num[1][0], t_num[1][1], t_num[1][2]), (t_num[2][0], t_num[2][1], t_num[2][2]))
    )
    d1 = det_g
    d2 = d1 * d1
    d3 = d2 * d1
    c2 = Fraction(-tr_num, d1)
    c1 = Fraction(m01 + m02 + m12, d2)
    c0 = Fraction(-det_t_num, d3)

    schur_stable = _is_schur_stable_cubic(c2, c1, c0)

    # Exact T^T T and T T^T (scaled by det_g^2)
    ttt = [[sum(t_num[k][i] * t_num[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    t_tt = [[sum(t_num[i][k] * t_num[j][k] for k in range(3)) for j in range(3)] for i in range(3)]

    # M = det_g^2 * I_3 - T_num^T T_num has exact same Sylvester inertia as I_3 - T^T T
    m_mat = [
        [Fraction((d2 if i == j else 0) - ttt[i][j], 1) for j in range(3)]
        for i in range(3)
    ]
    n_pos, n_neg, n_zero = exact_symmetric_inertia_3x3(m_mat)

    comm_sq = sum((ttt[i][j] - t_tt[i][j]) ** 2 for i in range(3) for j in range(3))
    tr_ttt = ttt[0][0] + ttt[1][1] + ttt[2][2]
    kappa_f3 = Fraction(comm_sq, tr_ttt * tr_ttt) if tr_ttt > 0 else Fraction(0, 1)
    f3_transient_witness = schur_stable and n_neg >= 1

    return {
        "schur_stable": schur_stable,
        "inertia_I_minus_TtT": [n_pos, n_neg, n_zero],
        "f3_transient_witness": f3_transient_witness,
        "commutator_kappa_f3": kappa_f3,
        "trace_TtT": Fraction(tr_ttt, d2),
    }


# ---------------------------------------------------------------------------
# Exact Matched Surrogates (Zero-Float SHA-256 Counter PRNG + Exact WHT-256)
# ---------------------------------------------------------------------------


def _sha256_u64_stream(seed_tag: str, count: int) -> list[int]:
    tag = require_str(seed_tag, "seed_tag", min_len=1, max_len=256)
    cnt = require_int(count, "count", lo=1, hi=MAX_SEQ_LEN)
    out: list[int] = []
    block_idx = 0
    while len(out) < cnt:
        digest = hashlib.sha256(f"{tag}:{block_idx}".encode("utf-8")).digest()
        for off in (0, 8, 16, 24):
            if len(out) < cnt:
                out.append(int.from_bytes(digest[off : off + 8], "big"))
        block_idx += 1
    return out


def wht_exact_int(vec: tuple[int, ...] | list[int]) -> list[int]:
    """Exact integer Walsh-Hadamard Transform (H_N^2 = N * I_N, zero floats)."""
    vals = _require_int_vec(vec, "vec", min_len=2, max_len=MAX_SEQ_LEN)
    n = len(vals)
    if (n & (n - 1)) != 0:
        raise TelemetryPortalError("INVALID_WHT_LEN", "WHT length must be a power of two >= 2")
    a = list(vals)
    step = 1
    while step < n:
        stride = step * 2
        for base in range(0, n, stride):
            left = a[base : base + step]
            right = a[base + step : base + stride]
            a[base : base + step] = map(add, left, right)
            a[base + step : base + stride] = map(sub, left, right)
        step = stride
    return a


def generate_surrogate_ranks(ranks: tuple[int, ...], family: str, seed_tag: str) -> tuple[int, ...]:
    """Generate one exact deterministic surrogate rank sequence."""
    vals = _require_int_vec(ranks, "ranks", min_len=4, max_len=MAX_SEQ_LEN)
    fam = require_str(family, "family", min_len=1, max_len=64)
    tag = require_str(seed_tag, "seed_tag", min_len=1, max_len=256)
    n = len(vals)
    if fam == "IID_PERM":
        arr = list(vals)
        rands = _sha256_u64_stream(tag, n)
        for i in range(n - 1, 0, -1):
            j = rands[i] % (i + 1)
            arr[i], arr[j] = arr[j], arr[i]
        return tuple(arr)
    if fam == "BLOCK_16":
        if n % BLOCK_SIZE != 0:
            raise TelemetryPortalError("INVALID_BLOCK_LEN", "series length must be divisible by BLOCK_SIZE")
        n_blocks = n // BLOCK_SIZE
        rands = _sha256_u64_stream(tag, n_blocks + 2)
        shift = rands[0] % n
        shifted = list(vals[shift:]) + list(vals[:shift])
        blocks = [shifted[b * BLOCK_SIZE : (b + 1) * BLOCK_SIZE] for b in range(n_blocks)]
        for i in range(n_blocks - 1, 0, -1):
            j = rands[i + 1] % (i + 1)
            blocks[i], blocks[j] = blocks[j], blocks[i]
        return tuple(v for blk in blocks for v in blk)
    if fam == "WHT_PHASE":
        centered = center_doubled_ranks(vals)
        spec = wht_exact_int(centered)
        rands = _sha256_u64_stream(tag, n)
        flipped = [spec[0]] + [spec[k] if (rands[k] & 1) == 0 else -spec[k] for k in range(1, n)]
        rebuilt = wht_exact_int(flipped)
        return doubled_mid_ranks(rebuilt)
    raise TelemetryPortalError("UNKNOWN_SURROGATE_FAMILY", f"unknown surrogate family {fam!r}")


def _format_observed_ops(series: tuple[int, ...]) -> tuple[tuple[int, ...], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Compute exact ranks and raw/formatted OP1, OP2, OP3 summaries for a stripped window."""
    ranks = doubled_mid_ranks(series)
    centered = center_doubled_ranks(ranks)
    obs_op1 = op1_seam1_leverage_shock(centered)
    obs_op2 = op2_seam3_hvg_and_ordinal(ranks)
    obs_op3 = op3_f3_var1_inertia(centered)
    formatted = {
        "op1_seam1": {
            "steps": obs_op1["steps"],
            "max_leverage_index": obs_op1["max_leverage_index"],
            "max_h": fmt_q(obs_op1["max_h"]),
            "median_h": fmt_q(obs_op1["median_h"]),
            "shock_ratio": fmt_q(obs_op1["shock_ratio"]),
        },
        "op2_seam3": {
            "hvg_edges": obs_op2["hvg_edges"],
            "hvg_betti1": obs_op2["hvg_betti1"],
            "forward_hvg_dag_grounded": obs_op2["forward_hvg_dag_grounded"],
            "ordinal_phi_asym": fmt_q(obs_op2["ordinal_phi_asym"]),
            "ordinal_signed_net_flux": obs_op2["ordinal_signed_net_flux"],
            "farkas_directed_cycle_witness": obs_op2["farkas_directed_cycle_witness"],
            "has_directed_cycle": obs_op2["has_directed_cycle"],
        },
        "op3_f3": {
            "schur_stable": obs_op3["schur_stable"],
            "inertia_I_minus_TtT": obs_op3["inertia_I_minus_TtT"],
            "f3_transient_witness": obs_op3["f3_transient_witness"],
            "commutator_kappa_f3": fmt_q(obs_op3["commutator_kappa_f3"]),
            "trace_TtT": fmt_q(obs_op3["trace_TtT"]),
        },
    }
    return ranks, obs_op1, obs_op2, obs_op3, formatted


def _build_window_a_summary(win_a: tuple[int, ...]) -> dict[str, Any]:
    """Build exact calibration Window A summary dictionary."""
    _ranks_a, op1_a, op2_a, op3_a, _fmt = _format_observed_ops(win_a)
    return {
        "n_samples": len(win_a),
        "unique_values": len(set(win_a)),
        "min_scaled_int_bits": min(win_a).bit_length(),
        "max_scaled_int_bits": max(win_a).bit_length(),
        "op1_shock_ratio": fmt_q(op1_a["shock_ratio"]),
        "op2_hvg_betti1": op2_a["hvg_betti1"],
        "op2_ordinal_phi_asym": fmt_q(op2_a["ordinal_phi_asym"]),
        "op3_f3_transient_witness": op3_a["f3_transient_witness"],
        "op3_inertia": op3_a["inertia_I_minus_TtT"],
    }


def evaluate_series_against_surrogates(
    series: tuple[int, ...],
    *,
    tag: str,
    surrogate_count: int = SURROGATE_COUNT,
) -> dict[str, Any]:
    """Evaluate all 3 operators on a stripped integer series and matched surrogate nulls."""
    tag_s = require_str(tag, "tag", min_len=1, max_len=200)
    m = require_int(surrogate_count, "surrogate_count", lo=9, hi=999)
    ranks, obs_op1, obs_op2, obs_op3, formatted = _format_observed_ops(series)

    null_pvals: dict[str, dict[str, str]] = {}
    null_exceed_counts: dict[str, dict[str, int]] = {}
    for fam in _NULL_FAMILIES:
        ex_s1 = 0
        ex_betti = 0
        ex_phi = 0
        ex_kappa = 0
        ex_h3a = 0
        for s_idx in range(m):
            surr_ranks = generate_surrogate_ranks(ranks, fam, f"{tag_s}:{fam}:{s_idx}")
            surr_centered = center_doubled_ranks(surr_ranks)
            s_op1 = op1_seam1_leverage_shock(surr_centered)
            s_op2 = op2_seam3_hvg_and_ordinal(surr_ranks)
            s_op3 = op3_f3_var1_inertia(surr_centered)
            if s_op1["shock_ratio"] >= obs_op1["shock_ratio"]:
                ex_s1 += 1
            if s_op2["hvg_betti1"] >= obs_op2["hvg_betti1"]:
                ex_betti += 1
            if s_op2["ordinal_phi_asym"] >= obs_op2["ordinal_phi_asym"]:
                ex_phi += 1
            if s_op3["commutator_kappa_f3"] >= obs_op3["commutator_kappa_f3"]:
                ex_kappa += 1
            if s_op3["f3_transient_witness"]:
                ex_h3a += 1
        den = m + 1
        null_exceed_counts[fam] = {
            "H1_SEAM1_SHOCK": ex_s1,
            "H2a_SEAM3_HVG_BETTI1": ex_betti,
            "H2b_SEAM3_IRREV_PHI": ex_phi,
            "H3a_SURROGATE_WITNESS_COUNT": ex_h3a,
            "H3b_F3_COMMUTATOR": ex_kappa,
        }
        null_pvals[fam] = {
            "H1_SEAM1_SHOCK": fmt_q(Fraction(ex_s1 + 1, den)),
            "H2a_SEAM3_HVG_BETTI1": fmt_q(Fraction(ex_betti + 1, den)),
            "H2b_SEAM3_IRREV_PHI": fmt_q(Fraction(ex_phi + 1, den)),
            "H3b_F3_COMMUTATOR": fmt_q(Fraction(ex_kappa + 1, den)),
        }

    passes_all_nulls: dict[str, bool] = {}
    for hyp in ("H1_SEAM1_SHOCK", "H2a_SEAM3_HVG_BETTI1", "H2b_SEAM3_IRREV_PHI", "H3b_F3_COMMUTATOR"):
        passes_all_nulls[hyp] = all(
            _passes_alpha(Fraction(null_exceed_counts[fam][hyp] + 1, m + 1)) for fam in _NULL_FAMILIES
        )
    passes_all_nulls["H3a_F3_TRANSIENT_WITNESS"] = obs_op3["f3_transient_witness"]

    return {
        "n_samples": len(series),
        "op1_seam1": formatted["op1_seam1"],
        "op2_seam3": formatted["op2_seam3"],
        "op3_f3": formatted["op3_f3"],
        "surrogate_exceed_counts": null_exceed_counts,
        "surrogate_pvals": null_pvals,
        "passes_prereg_gate": passes_all_nulls,
    }


def classify_cross_domain_verdict(n_passing_domains: int) -> str:
    n_pass = require_int(n_passing_domains, "n_passing_domains", lo=0, hi=4)
    if n_pass >= 3:
        return "SUPPORTED"
    if n_pass >= 1:
        return "PARTIAL"
    return "FALSIFIED"


def run_known_answer_controls(*, surrogate_count: int = SURROGATE_COUNT) -> dict[str, Any]:
    """Run exact known-answer synthetic controls (monotone invariance, time-reversal, IID null, sawtooth)."""
    # 1. Monotone nonlinear invariance check on deterministic series
    base_raw = tuple(((i * 37 + (i * i) % 19) % 101) - 50 for i in range(WINDOW_LEN))
    mono_raw = tuple(3 * (x * x * x) + 7 * x + 10000 for x in base_raw)
    r_base = doubled_mid_ranks(base_raw)
    r_mono = doubled_mid_ranks(mono_raw)
    c_base = center_doubled_ranks(r_base)
    c_mono = center_doubled_ranks(r_mono)
    mono_exact = all(
        (
            r_base == r_mono,
            op1_seam1_leverage_shock(c_base)["shock_ratio"] == op1_seam1_leverage_shock(c_mono)["shock_ratio"],
            op2_seam3_hvg_and_ordinal(r_base) == op2_seam3_hvg_and_ordinal(r_mono),
            op3_f3_var1_inertia(c_base) == op3_f3_var1_inertia(c_mono),
        )
    )

    # 2. Exact time-reversal symmetry check on non-dyadic asymmetric sawtooth (period 13, coprime to 16 & 256)
    jitter = _sha256_u64_stream("s20c-ka-sawtooth", WINDOW_LEN)
    sawtooth = tuple((i % 13) * 20 + int(jitter[i] % 7) for i in range(WINDOW_LEN))
    saw_rev = tuple(reversed(sawtooth))
    op2_fwd = op2_seam3_hvg_and_ordinal(doubled_mid_ranks(sawtooth))
    op2_rev = op2_seam3_hvg_and_ordinal(doubled_mid_ranks(saw_rev))
    time_rev_exact = all(
        (
            op2_fwd["hvg_betti1"] == op2_rev["hvg_betti1"],
            op2_fwd["ordinal_phi_asym"] == op2_rev["ordinal_phi_asym"],
            op2_fwd["ordinal_signed_net_flux"] == -op2_rev["ordinal_signed_net_flux"],
        )
    )

    # 3. Synthetic IID white-noise must-fail control
    iid_raw = tuple(int(v % 10000) for v in _sha256_u64_stream("s20c-ka-iid-null", WINDOW_LEN))
    iid_eval = evaluate_series_against_surrogates(iid_raw, tag="KA_IID_NULL", surrogate_count=surrogate_count)
    iid_clean_null = not any(
        iid_eval["passes_prereg_gate"][h]
        for h in ("H1_SEAM1_SHOCK", "H2a_SEAM3_HVG_BETTI1", "H2b_SEAM3_IRREV_PHI", "H3b_F3_COMMUTATOR")
    )

    # 4. Synthetic sawtooth must-detect irreversibility & non-normal transient amplification
    saw_eval = evaluate_series_against_surrogates(sawtooth, tag="KA_SAWTOOTH_IRREV", surrogate_count=surrogate_count)
    saw_detected_irrev = all(
        _passes_alpha(parse_q_str(saw_eval["surrogate_pvals"][fam]["H2b_SEAM3_IRREV_PHI"]))
        for fam in ("IID_PERM", "WHT_PHASE")
    )
    saw_detected_f3 = saw_eval["op3_f3"]["f3_transient_witness"]

    # 5. Exact WHT_256 Parseval energy & involution identity check
    r_saw_c = center_doubled_ranks(doubled_mid_ranks(sawtooth))
    w_fwd = wht_exact_int(r_saw_c)
    w_inv = wht_exact_int(w_fwd)
    wht_parseval_exact = all(
        (
            sum(v * v for v in w_fwd) == WINDOW_LEN * sum(v * v for v in r_saw_c),
            all(w_inv[i] == WINDOW_LEN * r_saw_c[i] for i in range(WINDOW_LEN)),
        )
    )

    all_controls_passed = all(
        (
            mono_exact,
            time_rev_exact,
            iid_clean_null,
            saw_detected_irrev,
            saw_detected_f3,
            wht_parseval_exact,
        )
    )
    return {
        "KA_MONO_EXACT": mono_exact,
        "KA_TIME_REV_EXACT": time_rev_exact,
        "KA_WHT256_PARSEVAL_EXACT": wht_parseval_exact,
        "KA_IID_NULL_CLEAN": iid_clean_null,
        "KA_SAWTOOTH_IRREV_DETECTED": saw_detected_irrev,
        "KA_SAWTOOTH_F3_DETECTED": saw_detected_f3,
        "KA_IID_SUMMARY": iid_eval["passes_prereg_gate"],
        "KA_SAWTOOTH_PVALS": saw_eval["surrogate_pvals"],
        "KA_SAWTOOTH_F3": saw_eval["op3_f3"],
        "all_controls_passed": all_controls_passed,
    }


def build_certificate(track_dir: Path, *, surrogate_count: int = SURROGATE_COUNT) -> dict[str, Any]:
    """Generate the complete zero-float Track S20c physical telemetry certificate."""
    _manifest, _prereg, streams = load_stripped_physical_streams(track_dir)
    manifest_sha = hashlib.sha256(load_safe_bytes(track_dir / "FETCH_MANIFEST.json", "FETCH_MANIFEST.json")).hexdigest()
    prereg_sha = hashlib.sha256(load_safe_bytes(track_dir / "PREREG_S20C.json", "PREREG_S20C.json")).hexdigest()
    controls = run_known_answer_controls(surrogate_count=surrogate_count)

    calibration_window_a: dict[str, Any] = {}
    heldout_window_b: dict[str, Any] = {}
    for sid in _STREAM_IDS:
        full_series = streams[sid]
        win_a = full_series[:WINDOW_LEN]
        win_b = full_series[WINDOW_LEN : 2 * WINDOW_LEN]
        calibration_window_a[sid] = _build_window_a_summary(win_a)
        heldout_window_b[sid] = evaluate_series_against_surrogates(
            win_b,
            tag=f"{sid}:WINDOW_B",
            surrogate_count=surrogate_count,
        )

    cross_domain_verdicts: dict[str, Any] = {}
    for hyp in _HYPOTHESIS_IDS:
        passing = [sid for sid in _STREAM_IDS if heldout_window_b[sid]["passes_prereg_gate"][hyp]]
        cross_domain_verdicts[hyp] = {
            "passing_streams": passing,
            "passing_count": len(passing),
            "total_streams": len(_STREAM_IDS),
            "verdict": classify_cross_domain_verdict(len(passing)),
        }

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "track_id": TRACK_ID,
        "fetch_manifest_sha256": manifest_sha,
        "prereg_sha256": prereg_sha,
        "oracle_class": "exact+empirical_physical_telemetry",
        "stage_a_stripped_ids": list(_STREAM_IDS),
        "known_answer_controls": controls,
        "calibration_window_a": calibration_window_a,
        "heldout_window_b": heldout_window_b,
        "cross_domain_verdicts": cross_domain_verdicts,
    }
    payload_sha = sha256_canonical(payload)
    cert: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "track_id": TRACK_ID,
        "payload_sha256": payload_sha,
        "payload": payload,
    }
    cert["certificate_sha256"] = sha256_canonical(
        {
            "schema_version": SCHEMA_VERSION,
            "track_id": TRACK_ID,
            "payload_sha256": payload_sha,
        }
    )
    return cert


def validate_certificate_payload(
    cert: Any,
    *,
    track_dir: Path | None = None,
    full_replay: bool = True,
    surrogate_count: int = SURROGATE_COUNT,
) -> dict[str, Any]:
    """Fail-closed Zone-B validator verifying structure, digests, internal gate consistency, and replay parity."""
    do_full = require_bool(full_replay, "full_replay")
    m_surr = require_int(surrogate_count, "surrogate_count", lo=9, hi=999)
    obj = require_mapping(cert, "certificate")
    validate_json_value(obj)
    expected_top = {"schema_version", "track_id", "payload_sha256", "certificate_sha256", "payload"}
    if set(obj.keys()) != expected_top:
        raise TelemetryPortalError("INVALID_CERT_KEYS", "certificate top-level keys mismatch")
    if require_str(obj["schema_version"], "schema_version") != SCHEMA_VERSION:
        raise TelemetryPortalError("INVALID_SCHEMA_VERSION", "unsupported schema_version")
    if require_str(obj["track_id"], "track_id") != TRACK_ID:
        raise TelemetryPortalError("INVALID_TRACK_ID", "unsupported track_id")

    payload = require_mapping(obj["payload"], "payload")
    computed_payload_sha = sha256_canonical(payload)
    if not constant_time_hex64_equal(obj["payload_sha256"], computed_payload_sha, "payload_sha256"):
        raise TelemetryPortalError("PAYLOAD_SHA_MISMATCH", "payload_sha256 mismatch")

    computed_cert_sha = sha256_canonical(
        {
            "schema_version": SCHEMA_VERSION,
            "track_id": TRACK_ID,
            "payload_sha256": computed_payload_sha,
        }
    )
    if not constant_time_hex64_equal(obj["certificate_sha256"], computed_cert_sha, "certificate_sha256"):
        raise TelemetryPortalError("CERT_SHA_MISMATCH", "certificate_sha256 mismatch")

    expected_payload_keys = {
        "schema_version",
        "track_id",
        "fetch_manifest_sha256",
        "prereg_sha256",
        "oracle_class",
        "stage_a_stripped_ids",
        "known_answer_controls",
        "calibration_window_a",
        "heldout_window_b",
        "cross_domain_verdicts",
    }
    if set(payload.keys()) != expected_payload_keys:
        raise TelemetryPortalError("INVALID_PAYLOAD_KEYS", "certificate payload keys mismatch")
    if require_str(payload["schema_version"], "payload.schema_version") != SCHEMA_VERSION:
        raise TelemetryPortalError("INVALID_PAYLOAD_SCHEMA", "payload schema_version mismatch")
    if require_str(payload["track_id"], "payload.track_id") != TRACK_ID:
        raise TelemetryPortalError("INVALID_PAYLOAD_TRACK", "payload track_id mismatch")
    require_hex64_ascii(payload["fetch_manifest_sha256"], "payload.fetch_manifest_sha256")
    require_hex64_ascii(payload["prereg_sha256"], "payload.prereg_sha256")
    if require_str(payload["oracle_class"], "payload.oracle_class") != "exact+empirical_physical_telemetry":
        raise TelemetryPortalError("INVALID_ORACLE_CLASS", "payload oracle_class mismatch")
    if list(require_seq(payload["stage_a_stripped_ids"], "stage_a_stripped_ids", min_len=4, max_len=4)) != list(_STREAM_IDS):
        raise TelemetryPortalError("INVALID_STREAM_IDS", "stage_a_stripped_ids mismatch")

    controls = require_mapping(payload.get("known_answer_controls"), "known_answer_controls")
    if require_bool(controls.get("all_controls_passed"), "all_controls_passed") is not True:
        raise TelemetryPortalError("CONTROLS_FAILED", "known_answer_controls must all pass")

    verdicts = require_mapping(payload.get("cross_domain_verdicts"), "cross_domain_verdicts")
    if set(verdicts.keys()) != set(_HYPOTHESIS_IDS):
        raise TelemetryPortalError("VERDICT_KEYS_MISMATCH", "cross_domain_verdicts keys mismatch")
    heldout = require_mapping(payload.get("heldout_window_b"), "heldout_window_b")
    if set(heldout.keys()) != set(_STREAM_IDS):
        raise TelemetryPortalError("HELDOUT_KEYS_MISMATCH", "heldout_window_b keys mismatch")
    gates_by_stream: dict[str, dict[str, bool]] = {}
    for sid in _STREAM_IDS:
        s_rec = require_mapping(heldout[sid], f"heldout.{sid}")
        g_map = require_mapping(s_rec.get("passes_prereg_gate"), f"heldout.{sid}.passes_prereg_gate")
        if set(g_map.keys()) != set(_HYPOTHESIS_IDS):
            raise TelemetryPortalError("GATE_KEYS_MISMATCH", f"passes_prereg_gate keys mismatch for {sid}")
        gates_by_stream[sid] = {h: require_bool(g_map[h], f"{sid}.{h}") for h in _HYPOTHESIS_IDS}
        ex_map = require_mapping(s_rec.get("surrogate_exceed_counts"), f"heldout.{sid}.surrogate_exceed_counts")
        pv_map = require_mapping(s_rec.get("surrogate_pvals"), f"heldout.{sid}.surrogate_pvals")
        if set(ex_map.keys()) != set(_NULL_FAMILIES) or set(pv_map.keys()) != set(_NULL_FAMILIES):
            raise TelemetryPortalError("SURROGATE_FAMILY_KEYS_MISMATCH", f"surrogate families mismatch for {sid}")
        surr_hyps = ("H1_SEAM1_SHOCK", "H2a_SEAM3_HVG_BETTI1", "H2b_SEAM3_IRREV_PHI", "H3b_F3_COMMUTATOR")
        for fam in _NULL_FAMILIES:
            ex_f = require_mapping(ex_map[fam], f"{sid}.{fam}.exceed")
            pv_f = require_mapping(pv_map[fam], f"{sid}.{fam}.pvals")
            for hyp in surr_hyps:
                ex_c = require_int(ex_f.get(hyp), f"{sid}.{fam}.{hyp}.ex", lo=0, hi=m_surr)
                if parse_q_str(pv_f.get(hyp), f"{sid}.{fam}.{hyp}.p") != Fraction(ex_c + 1, m_surr + 1):
                    raise TelemetryPortalError("PVAL_COUNT_MISMATCH", f"{sid}.{fam}.{hyp} p-value disagrees with exceed count")
        for hyp in surr_hyps:
            exp_pass = all(_passes_alpha(parse_q_str(pv_map[fam][hyp], f"{sid}.{fam}.{hyp}")) for fam in _NULL_FAMILIES)
            if gates_by_stream[sid][hyp] is not exp_pass:
                raise TelemetryPortalError("GATE_PVAL_MISMATCH", f"{sid}.{hyp} passes_prereg_gate disagrees with p-values")
        op3_rec = require_mapping(s_rec.get("op3_f3"), f"heldout.{sid}.op3_f3")
        if gates_by_stream[sid]["H3a_F3_TRANSIENT_WITNESS"] is not require_bool(op3_rec.get("f3_transient_witness"), f"{sid}.f3_witness"):
            raise TelemetryPortalError("GATE_F3_MISMATCH", f"{sid} H3a gate disagrees with f3_transient_witness")

    expected_verdict_keys = {"passing_streams", "passing_count", "total_streams", "verdict"}
    for hyp in _HYPOTHESIS_IDS:
        v_rec = require_mapping(verdicts[hyp], f"verdict.{hyp}")
        if set(v_rec.keys()) != expected_verdict_keys:
            raise TelemetryPortalError("VERDICT_FIELD_KEYS_MISMATCH", f"{hyp} verdict fields mismatch")
        expected_streams = [sid for sid in _STREAM_IDS if gates_by_stream[sid][hyp]]
        p_streams = list(require_seq(v_rec["passing_streams"], f"{hyp}.passing_streams", min_len=0, max_len=4))
        if p_streams != expected_streams:
            raise TelemetryPortalError("VERDICT_STREAMS_MISMATCH", f"{hyp} passing_streams mismatch")
        p_count = require_int(v_rec["passing_count"], f"{hyp}.passing_count", lo=0, hi=4)
        if p_count != len(expected_streams):
            raise TelemetryPortalError("VERDICT_COUNT_MISMATCH", f"{hyp} passing_count mismatch")
        require_int(v_rec["total_streams"], f"{hyp}.total_streams", lo=4, hi=4)
        expected_v = classify_cross_domain_verdict(p_count)
        if require_str(v_rec["verdict"], f"{hyp}.verdict") != expected_v:
            raise TelemetryPortalError("VERDICT_LOGIC_MISMATCH", f"{hyp} verdict does not match passing_count")

    if track_dir is not None:
        require_safe_path(track_dir, "track_dir")
        if do_full:
            rebuilt = build_certificate(track_dir, surrogate_count=m_surr)
            if not constant_time_hex64_equal(rebuilt["payload_sha256"], computed_payload_sha, "replay_payload_sha256"):
                raise TelemetryPortalError("REPLAY_MISMATCH", "certificate payload does not match deterministic replay")
        else:
            _manifest, _prereg, streams = load_stripped_physical_streams(track_dir)
            m_sha = hashlib.sha256(load_safe_bytes(track_dir / "FETCH_MANIFEST.json", "FETCH_MANIFEST.json")).hexdigest()
            p_sha = hashlib.sha256(load_safe_bytes(track_dir / "PREREG_S20C.json", "PREREG_S20C.json")).hexdigest()
            if not constant_time_hex64_equal(payload["fetch_manifest_sha256"], m_sha, "fetch_manifest_sha256"):
                raise TelemetryPortalError("PROVENANCE_PIN_MISMATCH", "certificate fetch_manifest_sha256 mismatch")
            if not constant_time_hex64_equal(payload["prereg_sha256"], p_sha, "prereg_sha256"):
                raise TelemetryPortalError("PROVENANCE_PIN_MISMATCH", "certificate prereg_sha256 mismatch")
            cal_a = require_mapping(payload["calibration_window_a"], "calibration_window_a")
            for sid in _STREAM_IDS:
                full_series = streams[sid]
                win_a = full_series[:WINDOW_LEN]
                win_b = full_series[WINDOW_LEN : 2 * WINDOW_LEN]
                if cal_a.get(sid) != _build_window_a_summary(win_a):
                    raise TelemetryPortalError("OBSERVED_REPLAY_MISMATCH", f"Window A mismatch for {sid}")
                _r, _o1, _o2, _o3, fmt_b = _format_observed_ops(win_b)
                hb_sid = heldout[sid]
                for op_key in ("op1_seam1", "op2_seam3", "op3_f3"):
                    if hb_sid.get(op_key) != fmt_b[op_key]:
                        raise TelemetryPortalError("OBSERVED_REPLAY_MISMATCH", f"Window B {op_key} mismatch for {sid}")

    return {
        "valid": True,
        "track_id": TRACK_ID,
        "payload_sha256": computed_payload_sha,
        "certificate_sha256": computed_cert_sha,
    }
