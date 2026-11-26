#!/usr/bin/env python3
"""
AUDIT-114 (`track-s17-zone-canon-sylvester-inertia`):
Cross-Org Exact-Operator Unification — Pure-Z/Q Stdlib Reference Oracle.

Unifies three exact typed operators across siliconcordat, Foundation-0, and aska-physical
using strictly Python 3 standard library (`int`, `fractions.Fraction`, `hashlib`, `json`, `re`):
  1. `zone-canon-v0` vs `aletheia v2.0/v2.1` Canonical-JSON Differential Oracle (`mde#8 @ 3c8e5a26`)
  2. Independent Zero-Shared-Code Exact-Q Sylvester Inertia Certifier (`P M P^T = L D L^T` with
     1x1 & 2x2 Bunch-Kaufman block pivots + independent Faddeev-LeVerrier/Descartes cross-check),
     exact 4-region proof for `fibral-rigidity#5 @ 4753275f` two-bar truss, and `loom#7 @ 64c797d3`
     trace rank bounds (`R_A`, `R_B`, `R_G`, `R_opt`) & low-rank adapter spectral bounds
  3. Typed Fail-Closed Gate-Axiom Counterexample Witness Suite (`loom#9 @ b2c5c33a` Contracts C1-C4
     / AG-VBC Axioms A1-A4) formalizing live cross-org defects (`warp#14`, `finite-state-proofs#5`,
     `fractals#58`, `loom#9`, `formal-claims-audit#19`).

Zero floats on trust paths. Zero bare `assert`s (100% `python3 -O` parity). Zero external deps.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
import re
from typing import Any, Mapping

ZONE_CANON_INT_LIMIT = (1 << 53) - 1
MAX_RATIONAL_DIGITS = 4000
MAX_MATRIX_DIM = 32
MAX_JSON_DEPTH = 64
MAX_V21_INT_BITS = 14000

_CANON_LOOM7_MARGIN_RE = re.compile(r"\A-?(?:0|[1-9][0-9]*)/[1-9][0-9]*\Z", re.ASCII)
_CANON_SPECTRAL2_RE = re.compile(r"\A(?:0|-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z", re.ASCII)
_RAW_RAT_RE = re.compile(r"\A-?[0-9]+/[0-9]+\Z", re.ASCII)

# Pinned upstream commit & file SHA-256 receipts (read-only snapshots, zero mutations)
UPSTREAM_PINS: dict[str, dict[str, str]] = {
    "siliconcordat/mde#8": {
        "head_sha": "3c8e5a267b570b6e5b0b2c2febe61700631cddfb",
        "file": "vectors/zone-canon-v0.json",
        "file_sha256": "725358287e66cd9a9773afee832a292f3ac965c3fe8544375ff6a755d555bd24",
    },
    "siliconcordat/loom#7": {
        "head_sha": "64c797d30da167db74df7196685c45db3dd22797",
        "file": "scripts/inertia_cert.py",
        "file_sha256": "f1b188f120a8b01aa6ff9e4b36dab42897e107964fa6328b2a5a8ac46fcafede",
    },
    "siliconcordat/loom#9": {
        "head_sha": "b2c5c33a3dbd486cbad0c6524391fc5cfc2400f8",
        "file": "scripts/gatecheck.py",
        "file_sha256": "cddaa58665890770f5b7be3ad582a783ee527c4de1898e4529e548d65f493ca3",
    },
    "siliconcordat/warp#14": {
        "head_sha": "ef7c292d7beba0eddebaba418488d66fc836f964",
        "file": "src/warp_modeld/cli.py",
        "file_sha256": "50dde4f311cad688811acbeed6d2e794c4cf4450f8a6c4dd5ab21efcbc24195e",
    },
    "Foundation-0/spectral-inertia#2": {
        "head_sha": "ef1a77db5924aa958b45c8affbb2424dcb1d9e2b",
        "file": "spectral_inertia/dual_oracle.py",
        "file_sha256": "78d5d1ccc6226a2a0340671290234817e17d5d52d51495216a7e61339ee3b8e8",
    },
    "aska-physical/fibral-rigidity#5": {
        "head_sha": "4753275f65c2999a9e10357025fc129b584d5c74",
        "file": "length_box.py",
        "file_sha256": "c6afbb367dc5e8fdb5981ee3035a4304d156a96e23a539cd7513212fa3dd0bb9",
    },
    "Foundation-0/finite-state-proofs#5": {
        "head_sha": "dd810d4078e9b3969a9ed9c2abf272bbbbf69015",
        "file": "square/verify.py",
        "file_sha256": "e6a29e44d78e7b8be2f76065c1aa62234e67c7cc2b2d785351e09413acf7d60f",
    },
    "Foundation-0/fractals#58": {
        "head_sha": "934e30c33d9d28903f73f12480db52bc80cddf90",
        "file": "scaling-check/check.mjs",
        "file_sha256": "30eb375c6f331fa246d95f399e2e37446e52d8389101421f385ff93fdfe69ad2",
    },
    "Foundation-0/formal-claims-audit#19": {
        "head_sha": "f9f3e4307cbbb17fa62ff339fa01eb6e3fcb25d0",
        "file": "scripts/check_verdicts.py",
        "file_sha256": "44ebb34710d67bcbfb751e564cbae5aaf0a7911c1be3ba12cdbcbecd955f1815",
    },
}

# Exact 17 (7 accept + 10 reject) golden test vectors from siliconcordat/mde#8 @ 3c8e5a26
MDE_PR8_ACCEPT_VECTORS: tuple[tuple[str, str, str, str], ...] = (
    (
        "empty_object",
        "{}",
        "{}",
        "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
    ),
    (
        "key_order_nested",
        '{"b":[1,{"z":true,"a":null}],"a":"x"}',
        '{"a":"x","b":[1,{"a":null,"z":true}]}',
        "96c83c1cb81829f839e9b502d34eba2f7af11c7e11fd8d82237d49873cbbe110",
    ),
    (
        "non_ascii_raw_utf8",
        '{"\u00e9":"\u65e5\u672c","a":"\\u00e9"}',
        '{"a":"\u00e9","\u00e9":"\u65e5\u672c"}',
        "f15a8b198ffb5b295dcf905075fc46543ac327dafdb37de84d819ccd4fd1c66c",
    ),
    (
        "astral_key_sorts_after_ffff",
        '{"\\ud83d\\ude00":1,"\\uffff":2}',
        '{"\uffff":2,"\U0001f600":1}',
        "92db27167c6f89fc43ff6c1997a7954a2e5bec81936fbe5ee12b4b6615b09596",
    ),
    (
        "control_chars_escaped",
        '{"k":"a\\u0001b\\n\\u007f"}',
        '{"k":"a\\u0001b\\n\x7f"}',
        "74713a64bb9f1fc65c596326c6ecdc32ad30f0ead0bde4c090cb4dc39809a42e",
    ),
    (
        "max_safe_integer",
        '{"n":9007199254740991,"m":-9007199254740991}',
        '{"m":-9007199254740991,"n":9007199254740991}',
        "3f54c80abdfbc38f08ed5654622eea6e7d7e58cbac36cf5a0670c8aeb054703d",
    ),
    (
        "scale_as_integer_over_1024",
        '{"scale_den_log2":10,"scales_num":{"corpus":205,"weft-eido":1024}}',
        '{"scale_den_log2":10,"scales_num":{"corpus":205,"weft-eido":1024}}',
        "e4e6e651a0b26c4d259173081cfcd990c191060167431003334412ec9985c333",
    ),
)

MDE_PR8_REJECT_VECTORS: tuple[tuple[str, str], ...] = (
    ("float_small_0.00001", '{"s":0.00001}'),
    ("float_small_1e-05", '{"s":1e-05}'),
    ("float_1e16", '{"s":1e16}'),
    ("float_1e+16", '{"s":1e+16}'),
    ("float_zero_point_zero", '{"s":0.0}'),
    ("negative_zero", '{"s":-0}'),
    ("integer_2_pow_53", '{"n":9007199254740992}'),
    ("integer_above_u64", '{"n":18446744073709551616}'),
    ("duplicate_key", '{"a":1,"a":2}'),
    ("nan_token", '{"n":NaN}'),
)


# ---------------------------------------------------------------------------
# Typed Error & Strict Pure-Z/Q Primitives
# ---------------------------------------------------------------------------

class Audit114Error(ValueError):
    """Structured fail-closed error (never stripped by python3 -O)."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def require_strict_int(
    val: Any,
    label: str = "int",
    *,
    lo: int | None = None,
    hi: int | None = None,
) -> int:
    if type(val) is not int:
        raise Audit114Error("INVALID_INT_TYPE", f"{label} must be strict int, got {type(val).__name__}")
    if lo is not None and val < lo:
        raise Audit114Error("INT_BELOW_MIN", f"{label} (bit_length={val.bit_length()}) < {lo}")
    if hi is not None and val > hi:
        raise Audit114Error("INT_ABOVE_MAX", f"{label} (bit_length={val.bit_length()}) > {hi}")
    return val


def require_strict_bool(val: Any, label: str = "bool") -> bool:
    if type(val) is not bool:
        raise Audit114Error("INVALID_BOOL_TYPE", f"{label} must be strict bool, got {type(val).__name__}")
    return val


def format_rational(q: Fraction, *, dialect: str = "spectral2") -> str:
    """Bijective canonical rational serializer across `spectral2` ('p' / 'p/q') & `loom7_margin` ('p/q')."""
    if type(q) is not Fraction:
        raise Audit114Error("INVALID_FRACTION_OBJ", f"expected Fraction, got {type(q).__name__}")
    if dialect == "loom7_margin":
        return f"{q.numerator}/{q.denominator}"
    if dialect == "spectral2":
        if q.denominator == 1:
            return str(q.numerator)
        return f"{q.numerator}/{q.denominator}"
    raise Audit114Error("UNKNOWN_DIALECT", f"unknown rational dialect: {dialect!r}")


def parse_rational(val: Any, *, dialect: str = "any") -> Fraction:
    """
    Strict exact-Q rational parser supporting `loom7_margin`, `spectral2`, and `any`.
    Rejects bool, float, whitespace, trailing newline, non-ASCII digits, unreduced forms,
    '-0'/'-0/1', zero denominators, and oversized digit tokens.
    """
    if dialect not in ("any", "loom7_margin", "spectral2"):
        raise Audit114Error("UNKNOWN_DIALECT", f"unknown rational dialect: {dialect!r}")
    if dialect == "any":
        if type(val) is Fraction:
            return val
        if type(val) is int:
            return Fraction(val, 1)
    if type(val) is not str:
        raise Audit114Error("INVALID_RATIONAL_TYPE", f"expected canonical rational, got {type(val).__name__}")
    if dialect == "loom7_margin":
        if _CANON_LOOM7_MARGIN_RE.fullmatch(val) is None or val == "-0/1":
            raise Audit114Error("INVALID_LOOM7_RATIONAL", f"not canonical loom7 p/q: {val!r}")
        p_s, q_s = val.split("/")
        if len(p_s.lstrip("-")) > MAX_RATIONAL_DIGITS or len(q_s) > MAX_RATIONAL_DIGITS:
            raise Audit114Error("RATIONAL_TOO_LONG", "rational digit cap exceeded")
        p_i = int(p_s)
        q_i = int(q_s)
        if math.gcd(abs(p_i), q_i) != 1:
            raise Audit114Error("UNREDUCED_RATIONAL", f"not lowest terms: {val!r}")
        return Fraction(p_i, q_i)
    if _CANON_SPECTRAL2_RE.fullmatch(val) is None:
        raise Audit114Error("INVALID_RATIONAL_SYNTAX", f"invalid rational syntax: {val!r}")
    if "/" not in val:
        if len(val.lstrip("-")) > MAX_RATIONAL_DIGITS:
            raise Audit114Error("RATIONAL_TOO_LONG", "rational digit cap exceeded")
        return Fraction(int(val), 1)
    p_s, q_s = val.split("/")
    if len(p_s.lstrip("-")) > MAX_RATIONAL_DIGITS or len(q_s) > MAX_RATIONAL_DIGITS:
        raise Audit114Error("RATIONAL_TOO_LONG", "rational digit cap exceeded")
    p_i = int(p_s)
    q_i = int(q_s)
    if dialect == "spectral2" and q_i == 1:
        raise Audit114Error("SPECTRAL2_UNIT_DENOM_FORBIDDEN", f"spectral2 forbids '/1': {val!r}")
    if math.gcd(abs(p_i), q_i) != 1:
        raise Audit114Error("UNREDUCED_RATIONAL", f"not lowest terms: {val!r}")
    return Fraction(p_i, q_i)


# ---------------------------------------------------------------------------
# Pillar 1: `zone-canon-v0` vs `aletheia v2.0/v2.1` Canonical-JSON Differential Oracle
# ---------------------------------------------------------------------------

def _reject_float_token(tok: str) -> Any:
    raise Audit114Error("JSON_FLOAT_FORBIDDEN", f"float literal forbidden: {tok!r}")


def _reject_constant_token(tok: str) -> Any:
    raise Audit114Error("JSON_CONSTANT_FORBIDDEN", f"non-RFC8259 constant forbidden: {tok!r}")


def _pairs_no_dup(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise Audit114Error("JSON_DUPLICATE_KEY", f"duplicate JSON key: {k!r}")
        out[k] = v
    return out


def _parse_zone_int(tok: str) -> int:
    if tok == "-0":
        raise Audit114Error("ZONE_NEGATIVE_ZERO", "negative zero '-0' forbidden in zone-canon-v0")
    if len(tok) > 40:
        raise Audit114Error("ZONE_INT_TOO_LONG", f"integer token too long: {tok[:24]}")
    n = int(tok)
    if abs(n) > ZONE_CANON_INT_LIMIT:
        raise Audit114Error("ZONE_INT_OUT_OF_RANGE", f"integer (bit_length={n.bit_length()}) exceeds 2^53 - 1")
    return n


def _check_max_depth(root: Any) -> None:
    """Iterative nesting depth cap (immune to RecursionError on deep or cyclic graphs)."""
    stack: list[tuple[Any, int]] = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if depth > MAX_JSON_DEPTH:
            raise Audit114Error("JSON_DEPTH_EXCEEDED", f"nesting depth exceeds {MAX_JSON_DEPTH}")
        if type(node) in (list, tuple):
            next_depth = depth + 1
            for item in node:
                stack.append((item, next_depth))
        elif type(node) is dict:
            next_depth = depth + 1
            for v in node.values():
                stack.append((v, next_depth))


def parse_zone_canon_v0(text: str) -> Any:
    """Strict `zone-canon-v0` JSON parser (`mde#8` rules)."""
    if type(text) is not str or len(text.strip()) == 0:
        raise Audit114Error("EMPTY_JSON", "JSON input must be a non-empty str")
    try:
        obj = json.loads(
            text,
            parse_int=_parse_zone_int,
            parse_float=_reject_float_token,
            parse_constant=_reject_constant_token,
            object_pairs_hook=_pairs_no_dup,
        )
    except Audit114Error:
        raise
    except Exception as exc:
        raise Audit114Error("JSON_SYNTAX_ERROR", str(exc)) from exc
    _check_max_depth(obj)
    return obj


def _escape_zone_str(s: str) -> str:
    out: list[str] = ['"']
    for ch in s:
        cp = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif cp == 0x08:
            out.append("\\b")
        elif cp == 0x0C:
            out.append("\\f")
        elif cp == 0x0A:
            out.append("\\n")
        elif cp == 0x0D:
            out.append("\\r")
        elif cp == 0x09:
            out.append("\\t")
        elif cp < 0x20:
            out.append(f"\\u{cp:04x}")
        elif 0xD800 <= cp <= 0xDFFF:
            raise Audit114Error("ZONE_LONE_SURROGATE", f"lone surrogate U+{cp:04X} forbidden")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _encode_zone_val(val: Any) -> str:
    if val is None:
        return "null"
    if type(val) is bool:
        return "true" if val else "false"
    if type(val) is int:
        if abs(val) > ZONE_CANON_INT_LIMIT:
            raise Audit114Error("ZONE_INT_OUT_OF_RANGE", f"integer (bit_length={val.bit_length()}) exceeds 2^53 - 1")
        return str(val)
    if type(val) is str:
        return _escape_zone_str(val)
    if type(val) in (list, tuple):
        return "[" + ",".join(_encode_zone_val(item) for item in val) + "]"
    if type(val) is dict:
        for k in val:
            if type(k) is not str:
                raise Audit114Error("NON_STRING_KEY", f"object key must be str, got {type(k).__name__}")
        items = sorted(val.items(), key=lambda kv: kv[0])
        return "{" + ",".join(f"{_escape_zone_str(k)}:{_encode_zone_val(v)}" for k, v in items) + "}"
    raise Audit114Error("UNSUPPORTED_JSON_TYPE", f"unsupported type {type(val).__name__}")


def encode_zone_canon_v0(obj: Any) -> bytes:
    """Encode an in-memory Python object to `zone-canon-v0` canonical UTF-8 bytes."""
    _check_max_depth(obj)
    return _encode_zone_val(obj).encode("utf-8")


def canonicalize_zone_canon_v0(text: str) -> tuple[bytes, str]:
    """Parse and canonicalize JSON text under `zone-canon-v0`, returning `(bytes, sha256_hex)`."""
    raw = encode_zone_canon_v0(parse_zone_canon_v0(text))
    return raw, hashlib.sha256(raw).hexdigest()


def parse_aletheia_strict_nofloat(text: str) -> Any:
    """
    Model of `aletheia v2.0 strict_io.parse_strict_json_text(allow_float=False, require_object=False)`:
    rejects floats, NaN/Infinity, and duplicate keys, while accepting `-0`, unbounded `int`,
    and lone UTF-16 surrogates.
    """
    if type(text) is not str or len(text.strip()) == 0:
        raise Audit114Error("EMPTY_JSON", "JSON input must be a non-empty str")
    try:
        obj = json.loads(
            text,
            parse_float=_reject_float_token,
            parse_constant=_reject_constant_token,
            object_pairs_hook=_pairs_no_dup,
        )
    except Audit114Error:
        raise
    except Exception as exc:
        raise Audit114Error("JSON_SYNTAX_ERROR", str(exc)) from exc
    _check_max_depth(obj)
    return obj


def _check_exact_v21_obj(root: Any) -> None:
    """Iterative type, key, depth, and int-size guard for `canonical_json_bytes_v21`."""
    stack: list[tuple[Any, int]] = [(root, 0)]
    while stack:
        obj, depth = stack.pop()
        if depth > MAX_JSON_DEPTH:
            raise Audit114Error("JSON_DEPTH_EXCEEDED", f"nesting depth exceeds {MAX_JSON_DEPTH}")
        if obj is None or type(obj) in (bool, str):
            continue
        if type(obj) is int:
            if obj.bit_length() > MAX_V21_INT_BITS:
                raise Audit114Error("V21_INT_TOO_LARGE", f"integer bit_length exceeds {MAX_V21_INT_BITS}")
            continue
        if type(obj) in (list, tuple):
            next_depth = depth + 1
            for item in obj:
                stack.append((item, next_depth))
            continue
        if type(obj) is dict:
            next_depth = depth + 1
            for k, v in obj.items():
                if type(k) is not str:
                    raise Audit114Error("NON_STRING_KEY", f"object key must be str, got {type(k).__name__}")
                stack.append((v, next_depth))
            continue
        raise Audit114Error("V21_FORBIDDEN_TYPE", f"type {type(obj).__name__} forbidden on trust path")


def canonical_json_bytes_v21(obj: Any) -> bytes:
    """
    Exact replica of `aletheia v2.1 supervision_airlock.canonical_json_bytes`:
    forbids floats & non-str dict keys, allows unbounded exact `int`, emits ASCII JSON (`ensure_ascii=True`).
    """
    _check_exact_v21_obj(obj)
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def audit_zone_canon_differential() -> dict[str, Any]:
    """Certify 17/17 `mde#8` vectors and map the exact set-difference vs `aletheia v2.0/v2.1`."""
    accept_records: list[dict[str, Any]] = []
    byte_divergences_on_mde8: list[str] = []
    accept_exact_count = 0
    for name, inp, exp_canon, exp_sha in MDE_PR8_ACCEPT_VECTORS:
        z_bytes, z_sha = canonicalize_zone_canon_v0(inp)
        exact_match = all((z_bytes == exp_canon.encode("utf-8"), z_sha == exp_sha))
        if exact_match:
            accept_exact_count += 1
        v21_bytes = canonical_json_bytes_v21(parse_aletheia_strict_nofloat(inp))
        v21_sha = hashlib.sha256(v21_bytes).hexdigest()
        same_bytes = z_bytes == v21_bytes
        if not same_bytes:
            byte_divergences_on_mde8.append(name)
        accept_records.append({
            "name": name,
            "mde8_exact_match": exact_match,
            "zone_canon_v0_sha256": z_sha,
            "aletheia_v21_sha256": v21_sha,
            "bytes_identical": same_bytes,
        })

    reject_records: list[dict[str, Any]] = []
    domain_diff_from_mde8: list[str] = []
    reject_blocked_count = 0
    for name, inp in MDE_PR8_REJECT_VECTORS:
        z_rejected = False
        try:
            canonicalize_zone_canon_v0(inp)
        except Audit114Error:
            z_rejected = True
        if z_rejected:
            reject_blocked_count += 1

        v21_accepted = False
        try:
            canonical_json_bytes_v21(parse_aletheia_strict_nofloat(inp))
            v21_accepted = True
        except Audit114Error:
            v21_accepted = False
        if v21_accepted:
            domain_diff_from_mde8.append(name)
        reject_records.append({
            "name": name,
            "zone_canon_v0_rejected": z_rejected,
            "aletheia_v21_accepted": v21_accepted,
        })

    # Exhaustive 128-code-point ASCII comparison (0x00..0x7F)
    ascii_diff_codepoints: list[int] = []
    for cp in range(128):
        sample = {"k": chr(cp)}
        if encode_zone_canon_v0(sample) != canonical_json_bytes_v21(sample):
            ascii_diff_codepoints.append(cp)

    # Extra boundary differential witnesses beyond the 17 mde#8 vectors
    extra_probes: list[tuple[str, str]] = [
        ("neg_2_pow_53", '{"n":-9007199254740992}'),
        ("lone_surrogate_text", '{"s":"\\ud800"}'),
        ("nfc_vs_nfd_distinct_keys", '{"\u00e9":1,"e\u0301":2}'),
        ("del_0x7f_raw", '{"k":"\x7f"}'),
    ]
    extra_results: list[dict[str, Any]] = []
    for name, raw_txt in extra_probes:
        z_ok = False
        z_sha_opt: str | None = None
        try:
            _, z_sha_opt = canonicalize_zone_canon_v0(raw_txt)
            z_ok = True
        except Audit114Error:
            z_ok = False
        v21_ok = False
        v21_sha_opt: str | None = None
        try:
            v21_sha_opt = hashlib.sha256(canonical_json_bytes_v21(parse_aletheia_strict_nofloat(raw_txt))).hexdigest()
            v21_ok = True
        except Audit114Error:
            v21_ok = False
        extra_results.append({
            "name": name,
            "zone_canon_v0_accepted": z_ok,
            "aletheia_v21_accepted": v21_ok,
            "same_sha256_when_both_accept": all((z_ok, v21_ok, z_sha_opt == v21_sha_opt)),
        })

    non_str_rejected_count = 0
    for bad_obj in ({1: "a"}, {True: "a"}):
        for fn in (encode_zone_canon_v0, canonical_json_bytes_v21):
            try:
                fn(bad_obj)
            except Audit114Error:
                non_str_rejected_count += 1

    return {
        "mde8_vectors_sha256": UPSTREAM_PINS["siliconcordat/mde#8"]["file_sha256"],
        "mde8_accept_certified": accept_exact_count,
        "mde8_reject_certified": reject_blocked_count,
        "mde8_byte_divergences_vs_v21": byte_divergences_on_mde8,
        "mde8_domain_set_diff_v21_minus_zone": domain_diff_from_mde8,
        "ascii_0_127_divergent_codepoints": ascii_diff_codepoints,
        "non_str_dict_keys_rejected_count": non_str_rejected_count,
        "accept_records": accept_records,
        "reject_records": reject_records,
        "extra_boundary_probes": extra_results,
    }


# ---------------------------------------------------------------------------
# Pillar 2: Zero-Shared-Code Exact-Q Sylvester Inertia Certifier (Bunch-Kaufman)
# ---------------------------------------------------------------------------

QMat = list[list[Fraction]]


def parse_sym_matrix_q(rows: Any, *, max_dim: int = MAX_MATRIX_DIM, dialect: str = "any") -> QMat:
    if type(rows) not in (list, tuple) or len(rows) == 0:
        raise Audit114Error("EMPTY_MATRIX", "matrix must be a non-empty list of rows")
    n = len(rows)
    if n > max_dim:
        raise Audit114Error("MATRIX_DIM_EXCEEDED", f"n={n} > max_dim={max_dim}")
    mat: QMat = []
    for i, row in enumerate(rows):
        if type(row) not in (list, tuple) or len(row) != n:
            raise Audit114Error("MATRIX_NOT_SQUARE", f"row {i} does not have length {n}")
        mat.append([parse_rational(v, dialect=dialect) for v in row])
    for i in range(n):
        for j in range(i + 1, n):
            if mat[i][j] != mat[j][i]:
                raise Audit114Error("MATRIX_NOT_SYMMETRIC", f"M[{i}][{j}] != M[{j}][{i}]")
    return mat


def _parse_general_matrix_q(rows: Any, n: int, *, dialect: str = "any") -> QMat:
    if type(rows) not in (list, tuple) or len(rows) != n:
        raise Audit114Error("MATRIX_DIM_MISMATCH", f"expected {n} rows")
    out: QMat = []
    for i, row in enumerate(rows):
        if type(row) not in (list, tuple) or len(row) != n:
            raise Audit114Error("MATRIX_DIM_MISMATCH", f"row {i} does not have length {n}")
        out.append([parse_rational(v, dialect=dialect) for v in row])
    return out


def _mat_mul_q(A: QMat, B: QMat) -> QMat:
    ra = len(A)
    ca = len(A[0])
    cb = len(B[0])
    z = Fraction(0)
    out = [[z for _ in range(cb)] for _ in range(ra)]
    for i in range(ra):
        for k in range(ca):
            aik = A[i][k]
            if aik == 0:
                continue
            for j in range(cb):
                bkj = B[k][j]
                if bkj != 0:
                    out[i][j] += aik * bkj
    return out


def _mat_transpose_q(A: QMat) -> QMat:
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def block_2x2_inertia_q(a: Any, b: Any, c: Any) -> tuple[int, int, int]:
    """
    Complete exact classification of symmetric 2x2 block [[a, b], [b, c]] with b != 0.
    Covers all 5 rows (det < 0; det > 0 with tr > 0 or tr < 0; det == 0 with tr > 0 or tr < 0).
    """
    if type(a) is not Fraction or type(b) is not Fraction or type(c) is not Fraction:
        raise Audit114Error("BLOCK_2X2_ENTRY_NOT_FRACTION", "2x2 block entries must be strict Fractions")
    if b == 0:
        raise Audit114Error("BLOCK_2X2_ZERO_OFFDIAG", "2x2 block requires b != 0")
    det = a * c - b * b
    tr = a + c
    if det < 0:
        return (1, 1, 0)
    if det > 0:
        return (2, 0, 0) if tr > 0 else (0, 2, 0)
    return (1, 0, 1) if tr > 0 else (0, 1, 1)


def d_block_inertia_q(D: Any) -> tuple[int, int, int]:
    """Validate symmetric non-overlapping 1x1/2x2 block-diagonal D (strict Fractions) and return exact inertia."""
    if type(D) not in (list, tuple) or len(D) == 0:
        raise Audit114Error("D_EMPTY_OR_BAD_TYPE", "D must be a non-empty list/tuple of rows")
    n = len(D)
    if n > MAX_MATRIX_DIM:
        raise Audit114Error("D_DIM_EXCEEDED", f"D dim {n} > max_dim={MAX_MATRIX_DIM}")
    for i, row in enumerate(D):
        if type(row) not in (list, tuple) or len(row) != n:
            raise Audit114Error("D_NOT_SQUARE", f"D row {i} does not have length {n}")
        for j, entry in enumerate(row):
            if type(entry) is not Fraction:
                raise Audit114Error("D_ENTRY_NOT_FRACTION", f"D[{i}][{j}] must be Fraction, got {type(entry).__name__}")
    for i in range(n):
        for j in range(i + 1, n):
            if D[i][j] != D[j][i]:
                raise Audit114Error("D_NOT_SYMMETRIC", f"D[{i}][{j}] != D[{j}][{i}]")
    for i in range(n):
        for j in range(n):
            if abs(i - j) > 1 and D[i][j] != 0:
                raise Audit114Error("D_OUTSIDE_BAND", f"nonzero D[{i}][{j}] outside tridiagonal band")
    for i in range(n - 2):
        if D[i][i + 1] != 0 and D[i + 1][i + 2] != 0:
            raise Audit114Error("D_OVERLAPPING_BLOCKS", f"overlapping 2x2 blocks at index {i}")
    pos = neg = zero = i = 0
    while i < n:
        if i + 1 < n and D[i][i + 1] != 0:
            p, q, z = block_2x2_inertia_q(D[i][i], D[i][i + 1], D[i + 1][i + 1])
            pos += p
            neg += q
            zero += z
            i += 2
        else:
            d = D[i][i]
            if d > 0:
                pos += 1
            elif d < 0:
                neg += 1
            else:
                zero += 1
            i += 1
    return (pos, neg, zero)


def bunch_kaufman_factor_q(M_raw: Any, *, dialect: str = "spectral2") -> dict[str, Any]:
    """
    Exact-Q symmetric Bunch-Kaufman factorization P M P^T = L D L^T with 1x1 and 2x2 block pivots.
    Explicitly handles zero-diagonal indefinite matrices (e.g., [[0,1],[1,0]]) via exact 2x2 blocks.
    """
    M = parse_sym_matrix_q(M_raw)
    n = len(M)
    A = [row[:] for row in M]
    perm = list(range(n))
    L = [[Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)]
    D = [[Fraction(0) for _ in range(n)] for _ in range(n)]

    def swap_rc(u: int, v: int, done_cols: int) -> None:
        if u == v:
            return
        perm[u], perm[v] = perm[v], perm[u]
        A[u], A[v] = A[v], A[u]
        for row in A:
            row[u], row[v] = row[v], row[u]
        for col in range(done_cols):
            L[u][col], L[v][col] = L[v][col], L[u][col]

    k = 0
    while k < n:
        best_diag = None
        best_val = Fraction(0)
        for i in range(k, n):
            av = abs(A[i][i])
            if av > best_val:
                best_val = av
                best_diag = i

        if best_diag is not None:
            swap_rc(k, best_diag, k)
            piv = A[k][k]
            D[k][k] = piv
            for i in range(k + 1, n):
                L[i][k] = A[i][k] / piv
            for i in range(k + 1, n):
                lik = L[i][k]
                if lik == 0:
                    continue
                for j in range(k + 1, n):
                    A[i][j] -= lik * A[k][j]
            k += 1
            continue

        pair = None
        for i in range(k, n):
            for j in range(i + 1, n):
                if A[i][j] != 0:
                    pair = (i, j)
                    break
            if pair is not None:
                break
        if pair is None:
            break

        p_i, p_j = pair
        swap_rc(k, p_i, k)
        swap_rc(k + 1, p_j, k)
        b = A[k][k + 1]
        D[k][k + 1] = b
        D[k + 1][k] = b
        for i in range(k + 2, n):
            L[i][k] = A[i][k + 1] / b
            L[i][k + 1] = A[i][k] / b
        for i in range(k + 2, n):
            l0 = L[i][k]
            l1 = L[i][k + 1]
            for j in range(k + 2, n):
                A[i][j] -= l0 * A[k][j] + l1 * A[k + 1][j]
        k += 2

    inertia = d_block_inertia_q(D)
    return {
        "M": [[format_rational(v, dialect=dialect) for v in row] for row in M],
        "P": perm,
        "L": [[format_rational(v, dialect=dialect) for v in row] for row in L],
        "D": [[format_rational(v, dialect=dialect) for v in row] for row in D],
        "claim": [inertia[0], inertia[1], inertia[2]],
    }


def verify_pldl_certificate_q(cert: Any, *, dialect: str = "any") -> tuple[int, int, int]:
    """Fail-closed exact-Q verifier for `P M P^T = L D L^T` certificates."""
    if type(cert) is not dict:
        raise Audit114Error("CERT_NOT_DICT", "certificate must be a dict")
    if any(type(k) is not str for k in cert):
        raise Audit114Error("CERT_NON_STRING_KEY", "certificate keys must all be str")
    keys = set(cert.keys())
    if keys not in ({"M", "P", "L", "D"}, {"M", "P", "L", "D", "claim"}):
        raise Audit114Error("CERT_KEYS_MISMATCH", f"unexpected certificate keys: {sorted(keys)}")

    M = parse_sym_matrix_q(cert["M"], dialect=dialect)
    n = len(M)
    P_raw = cert["P"]
    if type(P_raw) not in (list, tuple) or len(P_raw) != n:
        raise Audit114Error("INVALID_PERMUTATION_LEN", f"P must have length {n}")
    P = [require_strict_int(x, "P[i]", lo=0, hi=n - 1) for x in P_raw]
    if len(set(P)) != n:
        raise Audit114Error("INVALID_PERMUTATION_DUP", "P contains duplicate indices")

    L = _parse_general_matrix_q(cert["L"], n, dialect=dialect)
    for i in range(n):
        if L[i][i] != 1:
            raise Audit114Error("L_NOT_UNIT", f"L[{i}][{i}] != 1")
        for j in range(i + 1, n):
            if L[i][j] != 0:
                raise Audit114Error("L_NOT_LOWER", f"L[{i}][{j}] != 0")

    D = parse_sym_matrix_q(cert["D"], dialect=dialect)
    if len(D) != n:
        raise Audit114Error("D_DIM_MISMATCH", f"D dim {len(D)} != {n}")
    inertia = d_block_inertia_q(D)

    pmpt = [[M[P[i]][P[j]] for j in range(n)] for i in range(n)]
    ldlt = _mat_mul_q(_mat_mul_q(L, D), _mat_transpose_q(L))
    if pmpt != ldlt:
        raise Audit114Error("PLDL_IDENTITY_FAIL", "P M P^T != L D L^T")

    if "claim" in cert:
        cl = cert["claim"]
        if type(cl) not in (list, tuple) or len(cl) != 3:
            raise Audit114Error("INVALID_CLAIM_SHAPE", "claim must be 3-element sequence")
        claimed = (
            require_strict_int(cl[0], "claim[0]", lo=0, hi=n),
            require_strict_int(cl[1], "claim[1]", lo=0, hi=n),
            require_strict_int(cl[2], "claim[2]", lo=0, hi=n),
        )
        if claimed != inertia:
            raise Audit114Error("CLAIM_MISMATCH", f"claimed {claimed} != verified {inertia}")

    return inertia


def translate_pldl_dialect(cert: Mapping[str, Any], target_dialect: str) -> dict[str, Any]:
    """Bijective spelling morphism translating a valid PLDL certificate between `loom7_margin` & `spectral2`."""
    verify_pldl_certificate_q(cert, dialect="any")
    out: dict[str, Any] = {
        "M": [[format_rational(parse_rational(v), dialect=target_dialect) for v in row] for row in cert["M"]],
        "P": list(cert["P"]),
        "L": [[format_rational(parse_rational(v), dialect=target_dialect) for v in row] for row in cert["L"]],
        "D": [[format_rational(parse_rational(v), dialect=target_dialect) for v in row] for row in cert["D"]],
    }
    if "claim" in cert:
        out["claim"] = list(cert["claim"])
    return out


def cayley_hamilton_holds_q(M_raw: Any, coeffs_desc: list[Fraction]) -> bool:
    """Evaluate exact matrix polynomial p(M) = sum c_k M^(n-k) == 0 over Q (Horner's scheme)."""
    M = parse_sym_matrix_q(M_raw)
    n = len(M)
    if type(coeffs_desc) is not list or len(coeffs_desc) != n + 1:
        raise Audit114Error("INVALID_CHARPOLY_LEN", f"expected {n + 1} coefficients")
    acc: QMat = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for c in coeffs_desc:
        cq = parse_rational(c)
        acc = _mat_mul_q(acc, M)
        for i in range(n):
            acc[i][i] += cq
    return all(acc[i][j] == 0 for i in range(n) for j in range(n))


def independent_charpoly_descartes_inertia_q(M_raw: Any) -> tuple[int, int, int]:
    """
    Zero-shared-code independent exact-Q inertia oracle:
    Faddeev-LeVerrier characteristic polynomial + exact Descartes' rule of signs.
    """
    M = parse_sym_matrix_q(M_raw)
    n = len(M)
    coeffs: list[Fraction] = [Fraction(1)]
    B = [row[:] for row in M]
    tr1 = sum((B[i][i] for i in range(n)), Fraction(0))
    coeffs.append(-tr1)
    for k in range(2, n + 1):
        shifted = [row[:] for row in B]
        ck_prev = coeffs[-1]
        for i in range(n):
            shifted[i][i] += ck_prev
        B = _mat_mul_q(M, shifted)
        trk = sum((B[i][i] for i in range(n)), Fraction(0))
        coeffs.append(-trk / Fraction(k))

    d_coeffs = coeffs[:]
    n_zero = 0
    while len(d_coeffs) > 1 and d_coeffs[-1] == 0:
        d_coeffs.pop()
        n_zero += 1

    def sign_changes(seq: list[Fraction]) -> int:
        nz = [x for x in seq if x != 0]
        return sum(1 for u, v in zip(nz, nz[1:]) if (u > 0) != (v > 0))

    n_pos = sign_changes(d_coeffs)
    alt = [c if (idx % 2 == 0) else -c for idx, c in enumerate(d_coeffs)]
    n_neg = sign_changes(alt)
    return (n_pos, n_neg, n_zero)


def audit_zero_diagonal_and_blocks() -> dict[str, Any]:
    """Certify zero-diagonal indefinite matrices, all 5 2x2 block classes, and dialect bijection."""
    zero_diag_cases: list[tuple[str, list[list[int]], tuple[int, int, int]]] = [
        ("Z2_swap", [[0, 1], [1, 0]], (1, 1, 0)),
        ("Z3_zero_plus_swap", [[0, 0, 0], [0, 0, 1], [0, 1, 0]], (1, 1, 1)),
        ("Z4_path", [[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], (2, 2, 0)),
    ]
    z_records: list[dict[str, Any]] = []
    for label, mat, expected in zero_diag_cases:
        c_s2 = bunch_kaufman_factor_q(mat, dialect="spectral2")
        in_bk = verify_pldl_certificate_q(c_s2, dialect="spectral2")
        in_fd = independent_charpoly_descartes_inertia_q(mat)
        c_l7 = translate_pldl_dialect(c_s2, "loom7_margin")
        in_l7 = verify_pldl_certificate_q(c_l7, dialect="loom7_margin")
        s2_fails_l7 = False
        try:
            verify_pldl_certificate_q(c_s2, dialect="loom7_margin")
        except Audit114Error:
            s2_fails_l7 = True
        l7_fails_s2 = False
        try:
            verify_pldl_certificate_q(c_l7, dialect="spectral2")
        except Audit114Error:
            l7_fails_s2 = True
        z_records.append({
            "name": label,
            "inertia": list(in_bk),
            "expected_matched": all((in_bk == expected, in_fd == expected, in_l7 == expected)),
            "raw_cross_dialect_rejected": all((s2_fails_l7, l7_fails_s2)),
        })

    block_rows: list[tuple[str, list[list[int]], tuple[int, int, int]]] = [
        ("det_neg", [[0, 1], [1, 0]], (1, 1, 0)),
        ("det_pos_tr_pos", [[2, 1], [1, 2]], (2, 0, 0)),
        ("det_pos_tr_neg", [[-2, 1], [1, -2]], (0, 2, 0)),
        ("det_zero_tr_pos", [[1, 1], [1, 1]], (1, 0, 1)),
        ("det_zero_tr_neg", [[-1, 1], [1, -1]], (0, 1, 1)),
    ]
    block_records: list[dict[str, Any]] = []
    for label, mat, expected in block_rows:
        cert = {
            "M": [[format_rational(Fraction(v)) for v in row] for row in mat],
            "P": [0, 1],
            "L": [["1", "0"], ["0", "1"]],
            "D": [[format_rational(Fraction(v)) for v in row] for row in mat],
            "claim": list(expected),
        }
        in_direct = verify_pldl_certificate_q(cert, dialect="spectral2")
        in_fd = independent_charpoly_descartes_inertia_q(mat)
        block_records.append({
            "case": label,
            "inertia": list(in_direct),
            "verified": all((in_direct == expected, in_fd == expected)),
        })

    return {
        "zero_diagonal_matrices": z_records,
        "block_2x2_five_row_table": block_records,
        "upstream_finding": {
            "loom7_handles_zero_diagonal_indefinite": True,
            "spectral_inertia2_handles_zero_diagonal_indefinite": True,
            "loom7_margin_cert_diagonal_only_for_psd_shifts": True,
            "raw_cross_repo_incompatible_due_to_p_over_1_vs_p_spelling": True,
            "bijective_spelling_morphism_restores_100pct_agreement": True,
        },
    }


def truss_hessian_congruent_q(L1: Fraction, L2: Fraction) -> QMat:
    """
    Exact-Q equilibrium Hessian for `aska-physical/fibral-rigidity#5` two-bar truss
    (pins at (-1,0) and (1,0), EA = 1):
      - L1 + L2 <= 2: exact on-line Hessian at x = (L1 - L2)/(L1 + L2), y = 0
      - L1 + L2 > 2 and |L1 - L2| < 2: exact Sylvester-congruent matrix diag(1, 1/y) H_raw diag(1, 1/y).
    """
    l1 = parse_rational(L1)
    l2 = parse_rational(L2)
    if l1 <= 0 or l2 <= 0:
        raise Audit114Error("TRUSS_NONPOSITIVE_LENGTH", "bar lengths must be strictly positive")
    s = l1 + l2
    if s <= 2:
        a = s / (l1 * l2)
        c = a * (Fraction(1) - s / 2)
        return [[a, Fraction(0)], [Fraction(0), c]]
    if abs(l1 - l2) >= 2:
        raise Audit114Error("TRUSS_TRIANGLE_VIOLATED", "|L1 - L2| must be < 2 for off-line equilibrium")
    x = (l1 * l1 - l2 * l2) / 4
    l1_3 = l1 * l1 * l1
    l2_3 = l2 * l2 * l2
    A = ((1 + x) ** 2) / l1_3 + ((x - 1) ** 2) / l2_3
    B = (1 + x) / l1_3 + (x - 1) / l2_3
    C = Fraction(1) / l1_3 + Fraction(1) / l2_3
    return [[A, B], [B, C]]


def audit_fibral_rigidity_truss() -> dict[str, Any]:
    """
    Exact-Q certification of `aska-physical/fibral-rigidity#5 @ 4753275f`:
      - Verified exact parameter box: [7/10, 13/10] x [9/10, 15/10]
      - All 4 corners strictly PD (2, 0, 0)
      - Complete 4-region pure-Q proof that interior (9/10, 11/10) has ZERO PD equilibria in R^2
      - Exact rational non-convexity certificate of stability set S (t = 1/3 along corner1 -> corner4)
      - Exact matrix-space convexity contrast proving H(L1, L2) is non-affine
      - Near-flat PD point (9/10, 11/10 + 10^-9) exact (2, 0, 0).
    """
    corners: list[tuple[str, Fraction, Fraction]] = [
        ("corner_1", Fraction(7, 10), Fraction(9, 10)),
        ("corner_2", Fraction(7, 10), Fraction(3, 2)),
        ("corner_3", Fraction(13, 10), Fraction(9, 10)),
        ("corner_4", Fraction(13, 10), Fraction(3, 2)),
    ]
    corner_mats: list[QMat] = []
    corner_records: list[dict[str, Any]] = []
    for label, l1, l2 in corners:
        H = truss_hessian_congruent_q(l1, l2)
        in_bk = verify_pldl_certificate_q(bunch_kaufman_factor_q(H))
        in_fd = independent_charpoly_descartes_inertia_q(H)
        corner_mats.append(H)
        corner_records.append({
            "label": label,
            "L1": format_rational(l1),
            "L2": format_rational(l2),
            "H": [[format_rational(v) for v in row] for row in H],
            "inertia": list(in_bk),
            "dual_oracle_pd": all((in_bk == (2, 0, 0), in_fd == (2, 0, 0))),
        })

    l1_int = Fraction(9, 10)
    l2_int = Fraction(11, 10)
    t_seg = Fraction(1, 3)
    seg_matches = all((
        (1 - t_seg) * corners[0][1] + t_seg * corners[3][1] == l1_int,
        (1 - t_seg) * corners[0][2] + t_seg * corners[3][2] == l2_int,
    ))

    # Region 1: (-1, 1) -> x = -1/10, H = diag(200/99, 0), inertia (1, 0, 1)
    x_mid = (l1_int - l2_int) / (l1_int + l2_int)
    H_mid = truss_hessian_congruent_q(l1_int, l2_int)
    in_mid_bk = verify_pldl_certificate_q(bunch_kaufman_factor_q(H_mid))
    in_mid_fd = independent_charpoly_descartes_inertia_q(H_mid)

    # Region 2: (-inf, -1) -> x = -109/100, H = diag(200/99, -2000/209), inertia (1, 1, 0)
    x_left = -(2 * l1_int * l2_int + l2_int - l1_int) / (l1_int + l2_int)
    d1_left = -1 - x_left
    d2_left = 1 - x_left
    f_left = (d1_left - l1_int) / l1_int + (d2_left - l2_int) / l2_int
    k_ax_left = Fraction(1) / l1_int + Fraction(1) / l2_int
    k_tr_left = (d1_left - l1_int) / (l1_int * d1_left) + (d2_left - l2_int) / (l2_int * d2_left)
    H_left = [[k_ax_left, Fraction(0)], [Fraction(0), k_tr_left]]
    in_left_bk = verify_pldl_certificate_q(bunch_kaufman_factor_q(H_left))
    in_left_fd = independent_charpoly_descartes_inertia_q(H_left)

    # Region 3: (1, +inf) -> candidate root 89/100 < 1 => 0 roots
    x_right_cand = (2 * l1_int * l2_int + l1_int - l2_int) / (l1_int + l2_int)

    # Region 4: off-line y != 0 -> y^2 == 0 => 0 off-line equilibria
    y2_int = ((l1_int + l2_int) ** 2 - 4) * (4 - (l1_int - l2_int) ** 2) / 16

    # Matrix-space convexity contrast
    weights = (Fraction(4, 9), Fraction(2, 9), Fraction(2, 9), Fraction(1, 9))
    H_conv: QMat = [
        [sum((w * M[i][j] for w, M in zip(weights, corner_mats)), Fraction(0)) for j in range(2)]
        for i in range(2)
    ]
    in_conv_bk = verify_pldl_certificate_q(bunch_kaufman_factor_q(H_conv))
    in_conv_fd = independent_charpoly_descartes_inertia_q(H_conv)

    H_near = truss_hessian_congruent_q(Fraction(9, 10), Fraction(11, 10) + Fraction(1, 10**9))
    in_near_bk = verify_pldl_certificate_q(bunch_kaufman_factor_q(H_near))
    in_near_fd = independent_charpoly_descartes_inertia_q(H_near)

    return {
        "verified_box": [["7/10", "13/10"], ["9/10", "3/2"]],
        "corners": corner_records,
        "interior_point": ["9/10", "11/10"],
        "non_convexity_segment": {
            "p0": ["7/10", "9/10"],
            "p1": ["13/10", "3/2"],
            "t": "1/3",
            "segment_exact_match": seg_matches,
            "interior_has_zero_pd_equilibria_in_R2": all((
                in_mid_bk == (1, 0, 1),
                in_mid_fd == (1, 0, 1),
                x_left < -1,
                f_left == 0,
                in_left_bk == (1, 1, 0),
                in_left_fd == (1, 1, 0),
                x_right_cand < 1,
                y2_int == 0,
            )),
        },
        "interior_four_region_proof": {
            "region_between_pins_root_x": format_rational(x_mid),
            "region_between_pins_H": [[format_rational(v) for v in row] for row in H_mid],
            "region_between_pins_inertia": list(in_mid_bk),
            "region_left_of_pin_root_x": format_rational(x_left),
            "region_left_of_pin_force_residual": format_rational(f_left),
            "region_left_of_pin_H": [[format_rational(v) for v in row] for row in H_left],
            "region_left_of_pin_inertia": list(in_left_bk),
            "region_right_of_pin_candidate_x": format_rational(x_right_cand),
            "region_right_of_pin_roots": 0 if x_right_cand < 1 else 1,
            "region_offline_y2": format_rational(y2_int),
            "region_offline_roots": 0 if y2_int == 0 else 2,
        },
        "matrix_convex_combination_weights": ["4/9", "2/9", "2/9", "1/9"],
        "matrix_convex_combination_inertia": list(in_conv_bk),
        "matrix_convex_combination_pd": all((in_conv_bk == (2, 0, 0), in_conv_fd == (2, 0, 0))),
        "near_flat_1e_minus_9_inertia": list(in_near_bk),
        "near_flat_1e_minus_9_pd": all((in_near_bk == (2, 0, 0), in_near_fd == (2, 0, 0))),
    }


def compute_rank_bounds_q(u: Fraction, t: Fraction, S: Fraction, b: int) -> dict[str, Fraction]:
    """
    Exact-Q rank lower bounds from `loom#7` §3 & `spectral-inertia#2` Theorem A1:
      - R_A (c=0): 2(u+t) - S - b
      - R_B (c=2, Alpoge-Furman Lemma 3.2): 2u + 4t - 4b - S
      - R_G (Knausgard Lemma 6.1 optimal c >= 0 at s=1): 2u + t^2/b - S if t >= b > 0 else R_A
      - R_opt (joint scale+weight optimum):
          0                          if u <= 0 or u + t <= 0
          u^2 / (S - t^2 / b)        if b > 0 and t > 0 and t * (u + t) >= b * S
          max(0, (u + t)^2 / S - b)  otherwise.
    """
    u_q = parse_rational(u)
    t_q = parse_rational(t)
    s_q = parse_rational(S)
    b_i = require_strict_int(b, "b", lo=0)
    if s_q <= 0:
        raise Audit114Error("NONPOSITIVE_FROB_SQ", "S = ||M||_F^2 must be > 0")
    tr_m = u_q + t_q
    r_a = 2 * tr_m - s_q - b_i
    r_b = 2 * u_q + 4 * t_q - 4 * b_i - s_q
    if b_i > 0 and t_q >= b_i:
        r_g = 2 * u_q + (t_q * t_q) / Fraction(b_i) - s_q
    else:
        r_g = r_a

    if u_q <= 0 or tr_m <= 0:
        r_opt = Fraction(0)
    elif b_i > 0 and t_q > 0 and t_q * tr_m >= b_i * s_q:
        denom = s_q - (t_q * t_q) / Fraction(b_i)
        if denom <= 0:
            raise Audit114Error("INFEASIBLE_TRACE_TUPLE", "S <= t^2 / b is impossible for Hermitian M")
        r_opt = (u_q * u_q) / denom
    else:
        val = (tr_m * tr_m) / s_q - b_i
        r_opt = val if val > 0 else Fraction(0)

    return {"R_A": r_a, "R_B": r_b, "R_G": r_g, "R_opt": r_opt}


def _matrix_trace_frob_q(M: QMat) -> tuple[Fraction, Fraction]:
    n = len(M)
    tr = sum((M[i][i] for i in range(n)), Fraction(0))
    frob = sum((v * v for row in M for v in row), Fraction(0))
    return tr, frob


def audit_loom7_rank_and_adapter_bounds() -> dict[str, Any]:
    """
    Exact-Q certification of `loom#7` §3 (trace rank bounds + sharpness) and §5 (low-rank adapter
    spectral bound Q(s) = s G_B - G_B G_A G_B <=> s I - B G_A B^T, including singular G_B & 5-case forgery).
    """
    tight_cases: list[tuple[str, QMat, QMat, int]] = [
        (
            "tight_A_c0",
            [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]],
            [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]],
            1,
        ),
        (
            "tight_B_c2",
            [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]],
            [[Fraction(2), Fraction(0)], [Fraction(0), Fraction(0)]],
            1,
        ),
        (
            "tight_G_c4_beats_B",
            [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]],
            [[Fraction(3), Fraction(0)], [Fraction(0), Fraction(0)]],
            1,
        ),
        (
            "sharp_Ropt_low_r2_b1",
            [
                [Fraction(0), Fraction(0), Fraction(0)],
                [Fraction(0), Fraction(3), Fraction(0)],
                [Fraction(0), Fraction(0), Fraction(3)],
            ],
            [
                [Fraction(2), Fraction(0), Fraction(0)],
                [Fraction(0), Fraction(-1), Fraction(0)],
                [Fraction(0), Fraction(0), Fraction(-1)],
            ],
            2,
        ),
        (
            "sharp_Ropt_high_r2_b1",
            [
                [Fraction(0), Fraction(0), Fraction(0)],
                [Fraction(0), Fraction(2), Fraction(0)],
                [Fraction(0), Fraction(0), Fraction(2)],
            ],
            [
                [Fraction(5), Fraction(0), Fraction(0)],
                [Fraction(0), Fraction(0), Fraction(0)],
                [Fraction(0), Fraction(0), Fraction(0)],
            ],
            2,
        ),
    ]
    bound_records: list[dict[str, Any]] = []
    for label, P1, Q, exp_rank in tight_cases:
        n = len(P1)
        p_pos, p_neg, _ = verify_pldl_certificate_q(bunch_kaufman_factor_q(P1))
        q_pos, _, _ = verify_pldl_certificate_q(bunch_kaufman_factor_q(Q))
        M = [[P1[i][j] + Q[i][j] for j in range(n)] for i in range(n)]
        u, _ = _matrix_trace_frob_q(P1)
        t, _ = _matrix_trace_frob_q(Q)
        _, S = _matrix_trace_frob_q(M)
        bnds = compute_rank_bounds_q(u, t, S, q_pos)
        rg_id_ok = any((
            q_pos == 0,
            t < q_pos,
            all((
                q_pos > 0,
                bnds["R_G"] - bnds["R_B"] == (t - 2 * q_pos) ** 2 / Fraction(max(q_pos, 1)),
                bnds["R_G"] - bnds["R_A"] == (t - q_pos) ** 2 / Fraction(max(q_pos, 1)),
            )),
        ))
        chain_ok = all((
            p_neg == 0,
            p_pos == exp_rank,
            bnds["R_A"] <= bnds["R_G"] <= bnds["R_opt"] <= exp_rank,
            bnds["R_B"] <= bnds["R_G"],
            bnds["R_B"] - bnds["R_A"] == 2 * t - 3 * q_pos,
            rg_id_ok,
        ))
        bound_records.append({
            "case": label,
            "exact_rank_P1": exp_rank,
            "certified_b": q_pos,
            "R_A": format_rational(bnds["R_A"]),
            "R_B": format_rational(bnds["R_B"]),
            "R_G": format_rational(bnds["R_G"]),
            "R_opt": format_rational(bnds["R_opt"]),
            "chain_and_identities_verified": chain_ok,
        })

    # Forged-b negative control: declaring b=0 on sharp_Ropt_high overshoots true rank 2 (27/11 > 2)
    forged_bnds = compute_rank_bounds_q(Fraction(4), Fraction(5), Fraction(33), 0)

    def check_adapter(name: str, B_rows: QMat, A_rows: QMat, s_pass: Fraction, s_fail: Fraction) -> dict[str, Any]:
        d_out = len(B_rows)
        B_T = _mat_transpose_q(B_rows)
        A_T = _mat_transpose_q(A_rows)
        G_B = _mat_mul_q(B_T, B_rows)
        G_A = _mat_mul_q(A_rows, A_T)
        G_BG_AG_B = _mat_mul_q(_mat_mul_q(G_B, G_A), G_B)
        K = _mat_mul_q(_mat_mul_q(B_rows, G_A), B_T)
        r = len(G_B)

        def eval_s(s: Fraction) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
            Q_s = [[s * G_B[i][j] - G_BG_AG_B[i][j] for j in range(r)] for i in range(r)]
            S_s = [[(s if i == j else Fraction(0)) - K[i][j] for j in range(d_out)] for i in range(d_out)]
            return (
                verify_pldl_certificate_q(bunch_kaufman_factor_q(Q_s)),
                independent_charpoly_descartes_inertia_q(S_s),
            )

        q_pass_in, k_pass_in = eval_s(s_pass)
        q_fail_in, k_fail_in = eval_s(s_fail)
        return {
            "name": name,
            "s_pass": format_rational(s_pass),
            "Q_pass_inertia": list(q_pass_in),
            "sI_minus_K_pass_inertia": list(k_pass_in),
            "s_fail": format_rational(s_fail),
            "Q_fail_inertia": list(q_fail_in),
            "sI_minus_K_fail_inertia": list(k_fail_in),
            "equivalence_and_bracket_verified": all((
                q_pass_in[1] == 0,
                k_pass_in[1] == 0,
                q_fail_in[1] > 0,
                k_fail_in[1] > 0,
            )),
        }

    B_full: QMat = [
        [Fraction(1, 2), Fraction(0)],
        [Fraction(0), Fraction(1, 2)],
        [Fraction(1, 4), Fraction(1, 4)],
    ]
    A_full: QMat = [
        [Fraction(1), Fraction(1, 2), Fraction(0)],
        [Fraction(0), Fraction(1, 2), Fraction(1)],
    ]
    B_sing: QMat = [
        [Fraction(1, 2), Fraction(1, 2)],
        [Fraction(1, 2), Fraction(1, 2)],
        [Fraction(0), Fraction(0)],
    ]
    ad_full = check_adapter("full_rank_3x2_adapter", B_full, A_full, Fraction(1), Fraction(1, 4))
    ad_sing = check_adapter("rank_deficient_singular_GB", B_sing, A_full, Fraction(4), Fraction(1, 2))

    # 5-case forgery matrix (scale B -> 8*B => sigma_max^2 scales by 64)
    B_forged: QMat = [[8 * v for v in row] for row in B_full]
    G_B_old = _mat_mul_q(_mat_transpose_q(B_full), B_full)
    G_A_mat = _mat_mul_q(A_full, _mat_transpose_q(A_full))
    G_old_mid = _mat_mul_q(_mat_mul_q(G_B_old, G_A_mat), G_B_old)
    Q_old = [[Fraction(1) * G_B_old[i][j] - G_old_mid[i][j] for j in range(2)] for i in range(2)]
    G_B_new = _mat_mul_q(_mat_transpose_q(B_forged), B_forged)
    G_new_mid = _mat_mul_q(_mat_mul_q(G_B_new, G_A_mat), G_B_new)
    Q_forged_old_s = [[Fraction(1) * G_B_new[i][j] - G_new_mid[i][j] for j in range(2)] for i in range(2)]
    Q_forged_64s = [[Fraction(64) * G_B_new[i][j] - G_new_mid[i][j] for j in range(2)] for i in range(2)]

    cert_old = bunch_kaufman_factor_q(Q_old)
    cert_forged_old_s = bunch_kaufman_factor_q(Q_forged_old_s)
    cert_forged_64s = bunch_kaufman_factor_q(Q_forged_64s)

    forgery_replay_blocked = parse_sym_matrix_q(cert_old["M"]) != Q_forged_old_s
    in_forged_old = verify_pldl_certificate_q(cert_forged_old_s)
    forgery_claim_rejected = False
    try:
        verify_pldl_certificate_q(dict(cert_forged_old_s, claim=[2, 0, 0]))
    except Audit114Error:
        forgery_claim_rejected = True
    forgery_ld_rejected = False
    try:
        verify_pldl_certificate_q(dict(cert_old, M=cert_forged_old_s["M"]))
    except Audit114Error:
        forgery_ld_rejected = True
    in_forged_64 = verify_pldl_certificate_q(cert_forged_64s)

    return {
        "rank_bound_witnesses": bound_records,
        "forged_b_overshoot_R_opt": format_rational(forged_bnds["R_opt"]),
        "forged_b_overshoots_true_rank_2": forged_bnds["R_opt"] > Fraction(2),
        "adapter_spectral_equivalences": [ad_full, ad_sing],
        "adapter_five_case_forgery": {
            "replay_old_cert_blocked_by_recomputation": forgery_replay_blocked,
            "fresh_cert_old_bound_inertia": list(in_forged_old),
            "tampered_claim_rejected": forgery_claim_rejected,
            "old_LD_under_new_M_rejected": forgery_ld_rejected,
            "fresh_cert_64s_inertia": list(in_forged_64),
        },
    }


# ---------------------------------------------------------------------------
# Pillar 3: Typed Fail-Closed Gate-Axiom Witness Suite (`loom#9` Axioms + Live Bugs)
# ---------------------------------------------------------------------------

def hardened_warp14_bool_config(cfg: Mapping[str, Any], key: str, *, default: bool = True) -> bool:
    """Hardened operator closing `siliconcordat/warp#14` (`null`/0/"" -> False truthiness coercion)."""
    if type(cfg) is not dict:
        raise Audit114Error("WARP14_CFG_NOT_DICT", "config must be a dict")
    if key not in cfg:
        return require_strict_bool(default, "default")
    return require_strict_bool(cfg[key], key)


def hardened_fsp5_nonneg_int(val: Any, label: str = "nilpotency_s") -> int:
    """Hardened operator closing `Foundation-0/finite-state-proofs#5` (`bool`-as-`int` via isinstance)."""
    return require_strict_int(val, label, lo=0)


def hardened_fractals58_exponent_in(
    x_a: Any,
    x_b: Any,
    y_a: Any,
    y_b: Any,
    lo: Any,
    hi: Any,
) -> bool:
    """
    Hardened pure-Q operator closing `Foundation-0/fractals#58` (`0/0` duplicate scale + descending flip):
    requires x_b > x_a > 0, y_a > 0, y_b > 0, lo <= hi before exact rational power cross-multiplication.
    """
    xa = parse_rational(x_a)
    xb = parse_rational(x_b)
    ya = parse_rational(y_a)
    yb = parse_rational(y_b)
    lo_q = parse_rational(lo)
    hi_q = parse_rational(hi)
    if xa <= 0 or xb <= 0 or ya <= 0 or yb <= 0:
        raise Audit114Error("FRACTALS58_NONPOSITIVE_DATA", "scales and values must be strictly positive")
    if xb <= xa:
        raise Audit114Error("FRACTALS58_NON_INCREASING_SCALE", "requires x_b > x_a strictly")
    if lo_q > hi_q:
        raise Audit114Error("FRACTALS58_INVERTED_BRACKET", "bracket requires lo <= hi")

    yr = yb / ya
    xr = xb / xa
    lo_lhs = yr ** lo_q.denominator
    lo_rhs = xr ** lo_q.numerator if lo_q.numerator >= 0 else Fraction(1) / (xr ** (-lo_q.numerator))
    hi_lhs = yr ** hi_q.denominator
    hi_rhs = xr ** hi_q.numerator if hi_q.numerator >= 0 else Fraction(1) / (xr ** (-hi_q.numerator))
    return lo_lhs >= lo_rhs and hi_lhs <= hi_rhs


def hardened_loom9_safe_rational_mutant(token: Any) -> list[tuple[str, str]]:
    """
    Hardened pure-Z/Q operator closing `siliconcordat/loom#9` (`gatecheck.py:242-244` leaf_mutants crash):
    guards digit length and zero denominator without float() conversion, preventing ZeroDivisionError,
    Python 4,300-digit ValueError, and float OverflowError on rejected rational fixtures.
    """
    if type(token) is not str:
        raise Audit114Error("LOOM9_NON_STR_TOKEN", "leaf token must be str")
    if _RAW_RAT_RE.fullmatch(token) is None:
        return []
    n_s, d_s = token.split("/")
    if len(n_s.lstrip("-")) > MAX_RATIONAL_DIGITS or len(d_s) > MAX_RATIONAL_DIGITS:
        return []
    n_i = int(n_s)
    d_i = int(d_s)
    if d_i == 0:
        return []
    q = Fraction(n_i, d_i)
    scaled = (q.numerator * 10000) // q.denominator
    sign = "-" if scaled < 0 else ""
    mag = abs(scaled)
    return [("rational-as-fixed-decimal-string", f"{sign}{mag // 10000}.{mag % 10000:04d}")]


def hardened_fca19_require_nonempty_verdicts(verdicts: Any) -> int:
    """Hardened operator closing `Foundation-0/formal-claims-audit#19` (empty glob vacuous pass)."""
    if type(verdicts) not in (list, tuple) or len(verdicts) == 0:
        raise Audit114Error("FCA19_EMPTY_VERDICTS", "at least one verdict record is required (R1 default reject)")
    for i, item in enumerate(verdicts):
        if type(item) is not str or len(item.strip()) == 0:
            raise Audit114Error("FCA19_INVALID_VERDICT_ENTRY", f"verdict entry {i} must be non-empty str")
    return len(verdicts)


def audit_gate_axiom_witnesses() -> dict[str, Any]:
    """
    Execute all 5 live cross-org counterexample witnesses: prove BOTH that the unguarded upstream
    pattern fails (false accept / sign flip / crash) AND that the hardened typed operator fails closed.
    """
    # W1: warp#14 null/0/"" -> False coercion
    w1_leaky_disabled = [bool({"require_adapter_file": bad}.get("require_adapter_file", True)) for bad in (None, 0, "", [], {})]
    w1_leaky_false_str = bool({"require_adapter_file": "false"}.get("require_adapter_file", True))
    w1_hardened_rejected = 0
    for bad in (None, 0, "", [], {}, "false"):
        try:
            hardened_warp14_bool_config({"require_adapter_file": bad}, "require_adapter_file")
        except Audit114Error:
            w1_hardened_rejected += 1
    w1_ok = all((
        all(v is False for v in w1_leaky_disabled),
        w1_leaky_false_str is True,
        w1_hardened_rejected == 6,
        hardened_warp14_bool_config({}, "require_adapter_file") is True,
        hardened_warp14_bool_config({"require_adapter_file": False}, "require_adapter_file") is False,
    ))

    # W2: finite-state-proofs#5 bool-as-int
    w2_leaky_accepted = [isinstance(v, int) and v >= 0 for v in (False, True, -1)]
    w2_hardened_rejected = 0
    for bad in (False, True, -1):
        try:
            hardened_fsp5_nonneg_int(bad)
        except Audit114Error:
            w2_hardened_rejected += 1
    w2_ok = all((w2_leaky_accepted == [True, True, False], w2_hardened_rejected == 3, hardened_fsp5_nonneg_int(0) == 0))

    # W3: fractals#58 0/0 duplicate scale & descending scale sign flip
    def leaky_exponent_in(xa: Fraction, xb: Fraction, ya: Fraction, yb: Fraction, lo: Fraction, hi: Fraction) -> bool:
        yr = yb / ya
        xr = xb / xa
        return (yr ** lo.denominator >= xr ** lo.numerator) and (yr ** hi.denominator <= xr ** hi.numerator)

    w3_dup_false_accept = leaky_exponent_in(Fraction(2), Fraction(2), Fraction(1), Fraction(1), Fraction(100), Fraction(100))
    w3_desc_false_reject = not leaky_exponent_in(Fraction(4), Fraction(2), Fraction(16), Fraction(4), Fraction(1), Fraction(3))
    w3_out_of_bracket = not leaky_exponent_in(Fraction(1), Fraction(2), Fraction(1), Fraction(8), Fraction(1), Fraction(2))
    w3_hardened_rejected = 0
    for args in (
        (Fraction(2), Fraction(2), Fraction(1), Fraction(1), Fraction(100), Fraction(100)),
        (Fraction(4), Fraction(2), Fraction(16), Fraction(4), Fraction(1), Fraction(3)),
    ):
        try:
            hardened_fractals58_exponent_in(*args)
        except Audit114Error:
            w3_hardened_rejected += 1
    w3_valid_pass = hardened_fractals58_exponent_in(Fraction(2), Fraction(4), Fraction(4), Fraction(16), Fraction(1), Fraction(3))
    w3_ok = all((w3_dup_false_accept, w3_desc_false_reject, w3_out_of_bracket, w3_hardened_rejected == 2, w3_valid_pass))

    # W4: loom#9 leaf_mutants ZeroDivisionError / ValueError / OverflowError
    w4_cases: list[tuple[str, str, type[BaseException]]] = [
        ("zero_denom", "1/0", ZeroDivisionError),
        ("digit_limit_5000", "1/" + "9" * 5000, ValueError),
        ("float_overflow_1e400", "1" + "0" * 400 + "/1", OverflowError),
    ]
    w4_crashes_reproduced = 0
    w4_hardened_safe = 0
    for _, tok, expected_exc in w4_cases:
        try:
            n_i, d_i = map(int, tok.split("/"))
            _ = format(float(Fraction(n_i, d_i)), ".17g")
        except expected_exc:
            w4_crashes_reproduced += 1
        if type(hardened_loom9_safe_rational_mutant(tok)) is list:
            w4_hardened_safe += 1
    w4_ok = all((w4_crashes_reproduced == 3, w4_hardened_safe == 3))

    # W5: formal-claims-audit#19 empty glob vacuous pass
    w5_leaky_vacuous_pass = all(True for _ in [])
    w5_hardened_rejected = False
    try:
        hardened_fca19_require_nonempty_verdicts([])
    except Audit114Error:
        w5_hardened_rejected = True
    w5_ok = all((w5_leaky_vacuous_pass, w5_hardened_rejected, hardened_fca19_require_nonempty_verdicts(["VERIFIED"]) == 1))

    return {
        "witness_count": 5,
        "all_witnesses_verified": all((w1_ok, w2_ok, w3_ok, w4_ok, w5_ok)),
        "witnesses": [
            {
                "id": "W1_WARP14_NULL_TO_FALSE",
                "source_pr": "siliconcordat/warp#14 @ ef7c292d",
                "loom9_axioms_violated": ["C1_Clause2_AbsentMeansFail", "C1_Clause3_OneSpelling", "R2", "R3", "AG_VBC_A1"],
                "leaky_false_opt_outs": 5,
                "hardened_rejected": w1_hardened_rejected,
                "verified": w1_ok,
            },
            {
                "id": "W2_FSP5_BOOL_AS_INT",
                "source_pr": "Foundation-0/finite-state-proofs#5 @ dd810d40",
                "loom9_axioms_violated": ["C1_Clause3_OneSpelling", "R3", "AG_VBC_A3"],
                "leaky_bool_accepts": 2,
                "hardened_rejected": w2_hardened_rejected,
                "verified": w2_ok,
            },
            {
                "id": "W3_FRACTALS58_ZERO_OVER_ZERO_SCALE",
                "source_pr": "Foundation-0/fractals#58 @ 934e30c3",
                "loom9_axioms_violated": ["C2_ExactOracleSoundness", "C1_Clause1_PinnedDomain", "AG_VBC_A3"],
                "dup_scale_false_accept_reproduced": w3_dup_false_accept,
                "desc_scale_sign_flip_reproduced": w3_desc_false_reject,
                "hardened_rejected": w3_hardened_rejected,
                "verified": w3_ok,
            },
            {
                "id": "W4_LOOM9_LEAF_MUTANTS_CRASH",
                "source_pr": "siliconcordat/loom#9 @ b2c5c33a",
                "loom9_axioms_violated": ["C1_Clause3_OneSpelling", "C1_Clause4_OneFunction", "R3", "R4"],
                "crashes_reproduced": w4_crashes_reproduced,
                "hardened_safe_returns": w4_hardened_safe,
                "verified": w4_ok,
            },
            {
                "id": "W5_FCA19_EMPTY_GLOB_VACUOUS_PASS",
                "source_pr": "Foundation-0/formal-claims-audit#19 @ f9f3e430",
                "loom9_axioms_violated": ["C1_Clause2_AbsentMeansFail", "R1_DefaultReject", "AG_VBC_A1", "AG_VBC_A4"],
                "leaky_vacuous_pass_reproduced": w5_leaky_vacuous_pass,
                "hardened_rejected": w5_hardened_rejected,
                "verified": w5_ok,
            },
        ],
    }


def build_audit114_payload() -> dict[str, Any]:
    """Assemble the full deterministic pure-Z/Q AUDIT-114 verification payload (zero floats)."""
    p1 = audit_zone_canon_differential()
    p2_z = audit_zero_diagonal_and_blocks()
    p2_truss = audit_fibral_rigidity_truss()
    p2_loom7 = audit_loom7_rank_and_adapter_bounds()
    p3 = audit_gate_axiom_witnesses()
    all_passed = all((
        p1["mde8_accept_certified"] == 7,
        p1["mde8_reject_certified"] == 10,
        p1["ascii_0_127_divergent_codepoints"] == [127],
        p1["non_str_dict_keys_rejected_count"] == 4,
        all(all((r["expected_matched"], r["raw_cross_dialect_rejected"])) for r in p2_z["zero_diagonal_matrices"]),
        all(r["verified"] for r in p2_z["block_2x2_five_row_table"]),
        all(c["dual_oracle_pd"] for c in p2_truss["corners"]),
        p2_truss["non_convexity_segment"]["segment_exact_match"],
        p2_truss["non_convexity_segment"]["interior_has_zero_pd_equilibria_in_R2"],
        p2_truss["matrix_convex_combination_pd"],
        p2_truss["near_flat_1e_minus_9_pd"],
        all(r["chain_and_identities_verified"] for r in p2_loom7["rank_bound_witnesses"]),
        p2_loom7["forged_b_overshoots_true_rank_2"],
        all(a["equivalence_and_bracket_verified"] for a in p2_loom7["adapter_spectral_equivalences"]),
        p2_loom7["adapter_five_case_forgery"]["replay_old_cert_blocked_by_recomputation"],
        p2_loom7["adapter_five_case_forgery"]["tampered_claim_rejected"],
        p2_loom7["adapter_five_case_forgery"]["old_LD_under_new_M_rejected"],
        p3["all_witnesses_verified"],
    ))
    return {
        "schema": "audit114.zone_canon_sylvester_inertia.v1",
        "audit_id": "AUDIT-114",
        "oracle_class": "exact",
        "honest_novelty_scope": "N0_known_math_N1_cross_org_differential_and_4region_truss_proof",
        "upstream_pins": UPSTREAM_PINS,
        "pillar1_zone_canon_differential": p1,
        "pillar2_sylvester_zero_diag_and_blocks": p2_z,
        "pillar2_fibral_rigidity_truss_box": p2_truss,
        "pillar2_loom7_rank_and_adapter_bounds": p2_loom7,
        "pillar3_gate_axiom_witnesses": p3,
        "all_passed": all_passed,
    }
