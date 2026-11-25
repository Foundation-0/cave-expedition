#!/usr/bin/env python3
"""
AUDIT-118A (`track-s19a-torus-activity-tomography`):
Pure-Z/Q Exact Meta-Recursive Activity, Process & Multi-Family Verification Oracle.

Applies all five Laws of The Aletheia Method to the live telemetry snapshot of
the expedition itself (strict immutable cutoff `2026-11-22T19:22:59Z`, board
messages `#1..#1018`, `AUDIT_LOG.md` `280` rows covering `AUDIT-001..117` plus
pre-cutoff PR/review/special clearances, `108` coordinator task logs including
`51` external Zone-B runs, and `17` frozen agent transcripts):
  - Pillar 1: Empirical Audit Outcome, Convergence & Erlang Non-Churn (`AUDIT-110R`)
  - Pillar 2: Cross-Continent / Multi-Family Orthogonal Catch Matrix
  - Pillar 3: Pareto-Ranked Recurring Defect-Class Taxonomy (`15` defect classes)
  - Pillar 4: Swarm Throughput, Verifier Latency (`@verifier-2`) & Bottleneck Tomography
  - Pillar 5: Looping Back In — `aletheia v2.1` Upgrades, Live 12-Vector Zone-B
              Pre-Flight Fuzz Self-Check & Exact Counterfactual Rework Elimination

Strict discipline:
  - Pure Python 3 standard library (`int`, `fractions.Fraction`, `0` floats).
  - Zero bare `assert` statements (100% `python3 -O` parity).
  - Strict `type()` checks rejecting `bool`-as-`int`, `int`-as-`bool`, and lying
    `Sequence`/`Mapping`/builtin subclasses.
  - Explicit `bit_length()` integer cap (`2048` bits) blocking `10**5000`.
  - Strictly iterative JSON tree validation (`max_depth=64`) blocking `1,500`-deep
    lists and cycles with zero recursion.
  - Strict 64-lowercase-ASCII-hex digest validation before `hmac.compare_digest`.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import hmac
import json
from typing import Any

MAX_JSON_DEPTH = 64
MAX_JSON_BYTES = 2_000_000
MAX_INT_BITS = 2048
MAX_INT_DIGITS = 620
MAX_SEQ_LEN = 256
_HEX_LOWER = frozenset("0123456789abcdef")

SNAPSHOT_CUTOFF_UTC = "2026-11-22T19:22:59Z"
SNAPSHOT_BOARD_CUTOFF_SEQ = 1018
SNAPSHOT_BOARD_PREFIX_SHA256 = "5f5f7a66dc70ad3e249e5ddb322f8469beff3669290670ef35536150373c7e1d"
SNAPSHOT_AUDIT_SLICE_SHA256 = "21d020375e48237b1db6be657a5ac027755d5d1edfc5b4c057f7fb2aae9e0b49"
SNAPSHOT_TASKS_MANIFEST_SHA256 = "39a49ca5910f739fa896ca582e741be2a90f5d37efac6aac7456dca8c66f0c4d"


class TorusActivityError(ValueError):
    """Fail-closed typed error (never stripped under `python3 -O`)."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


# ---------------------------------------------------------------------------
# Strict Input Hardening, Iterative JSON & Constant-Time Hex-Digest Guards
# ---------------------------------------------------------------------------

def require_int(
    val: Any,
    label: str = "int",
    *,
    lo: int | None = None,
    hi: int | None = None,
) -> int:
    if type(val) is not int:
        raise TorusActivityError("INVALID_INT_TYPE", f"{label} must be strict int")
    if val.bit_length() > MAX_INT_BITS:
        raise TorusActivityError("INT_BIT_LIMIT", f"{label} exceeds {MAX_INT_BITS}-bit cap")
    if lo is not None and val < lo:
        raise TorusActivityError("INT_BELOW_MIN", f"{label} below min {lo}")
    if hi is not None and val > hi:
        raise TorusActivityError("INT_ABOVE_MAX", f"{label} above max {hi}")
    return val


def require_bool(val: Any, label: str = "bool") -> bool:
    if type(val) is not bool:
        raise TorusActivityError("INVALID_BOOL_TYPE", f"{label} must be strict bool")
    return val


def require_str(val: Any, label: str = "str", *, min_len: int = 1, max_len: int = 256) -> str:
    if type(val) is not str:
        raise TorusActivityError("INVALID_STR_TYPE", f"{label} must be strict str")
    if len(val) < min_len:
        raise TorusActivityError("STR_TOO_SHORT", f"{label} shorter than {min_len}")
    if len(val) > max_len:
        raise TorusActivityError("STR_TOO_LONG", f"{label} longer than {max_len}")
    return val


def require_seq(
    val: Any,
    label: str = "seq",
    *,
    min_len: int = 1,
    max_len: int = MAX_SEQ_LEN,
) -> tuple[Any, ...]:
    if type(val) not in (list, tuple):
        raise TorusActivityError("INVALID_SEQ_TYPE", f"{label} must be strict list or tuple")
    n = len(val)
    if n < min_len:
        raise TorusActivityError("SEQ_TOO_SHORT", f"{label} length {n} < {min_len}")
    if n > max_len:
        raise TorusActivityError("SEQ_TOO_LONG", f"{label} length {n} > {max_len}")
    return tuple(val)


def require_mapping(val: Any, label: str = "mapping") -> dict[str, Any]:
    if type(val) is not dict:
        raise TorusActivityError("INVALID_MAPPING_TYPE", f"{label} must be strict dict")
    for k in val:
        if type(k) is not str:
            raise TorusActivityError("NON_STR_KEY", f"{label} keys must be strict str")
    return val


def require_hex64_ascii(val: Any, label: str = "sha256") -> str:
    if type(val) is not str:
        raise TorusActivityError("INVALID_DIGEST_TYPE", f"{label} must be strict str")
    if len(val) != 64:
        raise TorusActivityError("INVALID_DIGEST_LEN", f"{label} must have length 64")
    for ch in val:
        if ch not in _HEX_LOWER:
            raise TorusActivityError("INVALID_DIGEST_HEX", f"{label} must be lowercase ASCII hex")
    return val


def constant_time_hex64_equal(left: Any, right: Any, label: str = "sha256") -> bool:
    """Validate both digests as strict 64-lowercase-ASCII-hex BEFORE hmac.compare_digest."""
    a = require_hex64_ascii(left, f"{label}.left")
    b = require_hex64_ascii(right, f"{label}.right")
    return hmac.compare_digest(a, b)


def fmt_q(q: Fraction) -> str:
    if type(q) is not Fraction:
        raise TorusActivityError("INVALID_FRACTION_TYPE", "q must be strict Fraction")
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"


def ratio_q(num: int, den: int, label: str = "ratio") -> Fraction:
    n = require_int(num, f"{label}.num")
    d = require_int(den, f"{label}.den", lo=1)
    return Fraction(n, d)


def validate_json_value(obj: Any, *, max_depth: int = MAX_JSON_DEPTH) -> None:
    """Iterative zero-float, depth-capped, bit-length-capped, strict-type JSON validator."""
    limit = require_int(max_depth, "max_depth", lo=1, hi=128)
    stack: list[tuple[Any, int]] = [(obj, 0)]
    while stack:
        cur, depth = stack.pop()
        if depth > limit:
            raise TorusActivityError("MAX_DEPTH_EXCEEDED", f"JSON nesting exceeds {limit}")
        t = type(cur)
        if t is dict:
            for k, v in cur.items():
                if type(k) is not str:
                    raise TorusActivityError("NON_STR_KEY", "JSON object keys must be strict str")
                stack.append((v, depth + 1))
        elif t is list:
            for item in cur:
                stack.append((item, depth + 1))
        elif t is int:
            if cur.bit_length() > MAX_INT_BITS:
                raise TorusActivityError("INT_BIT_LIMIT", f"JSON int exceeds {MAX_INT_BITS}-bit cap")
        elif t in (str, bool) or cur is None:
            continue
        elif t is float:
            raise TorusActivityError("FLOAT_FORBIDDEN", "float values are forbidden in exact JSON")
        else:
            raise TorusActivityError("UNSUPPORTED_JSON_TYPE", f"unsupported JSON type {t.__name__}")


def _reject_float_token(tok: str) -> Any:
    raise TorusActivityError("JSON_FLOAT_FORBIDDEN", f"float literal forbidden: {tok!r}")


def _reject_constant_token(tok: str) -> Any:
    raise TorusActivityError("JSON_CONSTANT_FORBIDDEN", f"non-RFC8259 constant forbidden: {tok!r}")


def _parse_capped_int_token(tok: str) -> int:
    digits = tok[1:] if tok.startswith("-") else tok
    if len(digits) > MAX_INT_DIGITS:
        raise TorusActivityError("INT_DIGIT_LIMIT", f"integer token exceeds {MAX_INT_DIGITS} digits")
    val = int(tok)
    if val.bit_length() > MAX_INT_BITS:
        raise TorusActivityError("INT_BIT_LIMIT", f"integer token exceeds {MAX_INT_BITS}-bit cap")
    return val


def _pairs_no_dup(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise TorusActivityError("JSON_DUPLICATE_KEY", f"duplicate JSON key: {k!r}")
        out[k] = v
    return out


def parse_strict_json(text: str, *, max_depth: int = MAX_JSON_DEPTH) -> Any:
    """Fail-closed zero-float, no-duplicate-key, depth-capped, bit-capped JSON parser."""
    if type(text) is not str:
        raise TorusActivityError("INVALID_JSON_INPUT", "JSON input must be strict str")
    try:
        encoded = text.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise TorusActivityError("INVALID_UTF8", f"JSON input contains unpaired surrogate: {exc}") from exc
    if len(encoded) > MAX_JSON_BYTES:
        raise TorusActivityError("JSON_TOO_LARGE", f"JSON exceeds {MAX_JSON_BYTES} bytes")
    if len(text.strip()) == 0:
        raise TorusActivityError("EMPTY_JSON", "JSON input must be non-empty")
    try:
        parsed = json.loads(
            text,
            parse_float=_reject_float_token,
            parse_constant=_reject_constant_token,
            parse_int=_parse_capped_int_token,
            object_pairs_hook=_pairs_no_dup,
        )
    except TorusActivityError:
        raise
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise TorusActivityError("JSON_PARSE_ERROR", str(exc)) from exc
    validate_json_value(parsed, max_depth=max_depth)
    return parsed


def canonical_json_bytes(obj: Any) -> bytes:
    """Serialize strictly validated exact JSON tree to canonical ASCII bytes."""
    validate_json_value(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


# ---------------------------------------------------------------------------
# Frozen Empirical Corpus Snapshot Tables (Cutoff: 2026-11-22T19:22:59Z / #1018)
# ---------------------------------------------------------------------------

AUDIT_CATEGORY_COUNTS: tuple[dict[str, Any], ...] = (
    {"category": "CORE_TRACK", "verified": 121, "partial_fragile": 75, "falsified": 1},
    {"category": "PR_CLEARANCE", "verified": 27, "partial_fragile": 1, "falsified": 0},
    {"category": "REVIEW_CLEARANCE", "verified": 39, "partial_fragile": 6, "falsified": 0},
    {"category": "SPECIAL", "verified": 9, "partial_fragile": 1, "falsified": 0},
)

AUDIT_ROUND_COUNTS: tuple[dict[str, Any], ...] = (
    {"round": "R1", "verified": 105, "partial_fragile": 76, "falsified": 1},
    {"round": "R2", "verified": 74, "partial_fragile": 3, "falsified": 0},
    {"round": "R3a", "verified": 0, "partial_fragile": 2, "falsified": 0},
    {"round": "R3", "verified": 12, "partial_fragile": 1, "falsified": 0},
    {"round": "R4", "verified": 3, "partial_fragile": 1, "falsified": 0},
    {"round": "R5", "verified": 2, "partial_fragile": 0, "falsified": 0},
)

CORE_CONVERGENCE_TABLE: dict[str, int] = {
    "verified_pass_1": 43,
    "verified_pass_2": 60,
    "verified_pass_3": 6,
    "verified_pass_4": 2,
    "verified_pass_5": 2,
    "terminal_falsified": 1,
    "open_or_catalog_pf": 2,
    "unlogged_queue_starved": 1,
}

ERLANG_BOUNDARY_COUNTS: dict[str, dict[str, int]] = {
    "pre_erlang": {
        "total": 187,
        "verified": 119,
        "partial_fragile": 67,
        "falsified": 1,
        "r1_total": 117,
        "r1_verified": 55,
        "core_total": 176,
        "core_verified": 108,
        "non_core_total": 11,
        "non_core_verified": 11,
        "mid_audit_churn_incidents": 1,
    },
    "post_erlang": {
        "total": 93,
        "verified": 77,
        "partial_fragile": 16,
        "falsified": 0,
        "r1_total": 65,
        "r1_verified": 50,
        "core_total": 21,
        "core_verified": 13,
        "non_core_total": 72,
        "non_core_verified": 64,
        "mid_audit_churn_incidents": 0,
    },
}

VERIFIER_FAMILIES_TABLE: tuple[dict[str, Any], ...] = (
    {"family": "swarm_verifier_1", "region": "internal", "runs": 261, "completed": 261, "catches": 78, "passes": 183, "timeouts": 0, "cli_fails": 0},
    {"family": "swarm_verifier_2", "region": "internal", "runs": 19, "completed": 19, "catches": 6, "passes": 13, "timeouts": 0, "cli_fails": 0},
    {"family": "blinded_airgapped", "region": "internal_zone_b", "runs": 5, "completed": 5, "catches": 4, "passes": 1, "timeouts": 0, "cli_fails": 0},
    {"family": "deepseek_v41_flash", "region": "east_asia", "runs": 16, "completed": 16, "catches": 7, "passes": 9, "timeouts": 0, "cli_fails": 0},
    {"family": "muse_code", "region": "east_asia", "runs": 15, "completed": 14, "catches": 3, "passes": 11, "timeouts": 0, "cli_fails": 1},
    {"family": "glm_53", "region": "east_asia", "runs": 4, "completed": 4, "catches": 3, "passes": 1, "timeouts": 0, "cli_fails": 0},
    {"family": "claude_code", "region": "us_eu", "runs": 5, "completed": 4, "catches": 4, "passes": 0, "timeouts": 0, "cli_fails": 1},
    {"family": "gpt_6_luna", "region": "us_eu", "runs": 1, "completed": 1, "catches": 1, "passes": 0, "timeouts": 0, "cli_fails": 0},
    {"family": "grok_cli", "region": "us_eu", "runs": 3, "completed": 1, "catches": 0, "passes": 1, "timeouts": 0, "cli_fails": 2},
    {"family": "mistral_vibe", "region": "us_eu", "runs": 4, "completed": 1, "catches": 0, "passes": 1, "timeouts": 3, "cli_fails": 0},
    {"family": "qwen_code", "region": "us_eu_or_ea_tui", "runs": 3, "completed": 0, "catches": 0, "passes": 0, "timeouts": 2, "cli_fails": 1},
)

ORTHOGONAL_CATCH_SIGNATURES: tuple[dict[str, Any], ...] = (
    {"signature": "c11_py_js_inf_nan_and_hidden_skip", "families": ["deepseek_v41_flash"], "example": "weft#224_task4306"},
    {"signature": "zone_b_4300_recursion_lyingseq_hmac", "families": ["deepseek_v41_flash", "muse_code", "claude_code", "swarm_verifier_1"], "example": "AUDIT-115_116_ap_rank3"},
    {"signature": "mixed_tuple_key_and_reply_home_leak", "families": ["glm_53", "muse_code", "swarm_verifier_1"], "example": "AUDIT-105R_v21_wd30_114"},
    {"signature": "ast_boolop_conjunct_deletion_survivors", "families": ["blinded_airgapped"], "example": "AUDIT-103_104R_24_and_20_survivors"},
    {"signature": "live_mid_audit_snapshot_churn", "families": ["claude_code", "blinded_airgapped"], "example": "AUDIT-103_task2846_99ff3821"},
    {"signature": "utf32_bom_trojan_and_utf16_threshold_mutant", "families": ["claude_code"], "example": "aletheia_pr1_task3238"},
    {"signature": "graphql_100_cap_and_krawczyk_5488_boxes", "families": ["swarm_verifier_2"], "example": "mcproof17_rigid21"},
    {"signature": "deep_domain_proof_and_muse_missed_api_bugs", "families": ["swarm_verifier_1"], "example": "AUDIT-020_107_110_113"},
)

PARETO_DEFECT_TAXONOMY: tuple[dict[str, Any], ...] = (
    {"id": "DEF-01", "name": "non_canonical_json_float_int_keys_rationals", "zone": "zone_b_api", "incidents": 14, "board_msgs": 67},
    {"id": "DEF-02", "name": "bool_as_int_and_bool_coercion_forgery", "zone": "zone_b_api", "incidents": 11, "board_msgs": 34},
    {"id": "DEF-03", "name": "symlink_0o022_crlf_utf8_utf32_path_leak", "zone": "hygiene_ops", "incidents": 10, "board_msgs": 89},
    {"id": "DEF-04", "name": "bare_asserts_stripped_under_O_mode", "zone": "hygiene_ops", "incidents": 9, "board_msgs": 14},
    {"id": "DEF-05", "name": "surviving_r5_boolop_and_hollow_validators", "zone": "zone_b_api", "incidents": 8, "board_msgs": 32},
    {"id": "DEF-06", "name": "journal_vs_ledger_and_manifest_drift", "zone": "zone_b_api", "incidents": 7, "board_msgs": 17},
    {"id": "DEF-07", "name": "citation_line_anchor_and_prose_count_drift", "zone": "hygiene_ops", "incidents": 7, "board_msgs": 24},
    {"id": "DEF-08", "name": "lying_sequence_mapping_and_builtin_subclasses", "zone": "zone_b_api", "incidents": 5, "board_msgs": 10},
    {"id": "DEF-09", "name": "recursion_error_deep_json_and_list_nesting", "zone": "zone_b_api", "incidents": 5, "board_msgs": 14},
    {"id": "DEF-10", "name": "int_4300_digit_dos_missing_bit_length_cap", "zone": "zone_b_api", "incidents": 4, "board_msgs": 13},
    {"id": "DEF-11", "name": "stale_upstream_pins_and_snapshot_churn", "zone": "hygiene_ops", "incidents": 4, "board_msgs": 5},
    {"id": "DEF-12", "name": "non_ascii_hmac_compare_digest_typeerror", "zone": "zone_b_api", "incidents": 3, "board_msgs": 7},
    {"id": "DEF-13", "name": "missing_dco_signoff_trailer", "zone": "hygiene_ops", "incidents": 3, "board_msgs": 10},
    {"id": "DEF-14", "name": "openblas_thread_deadlock_and_gh_review_422", "zone": "hygiene_ops", "incidents": 2, "board_msgs": 7},
    {"id": "DEF-15", "name": "graphql_100_file_cap_truncation", "zone": "hygiene_ops", "incidents": 1, "board_msgs": 2},
)

AGENT_TELEMETRY_17: tuple[dict[str, Any], ...] = (
    {"agent": "coordinator", "group": "coordinator", "steps": 5091, "turns": 1460, "tc_turns": 1369, "tool_calls": 2313, "serial_turns": 665, "batched_turns": 704, "board_posts": 285},
    {"agent": "verifier", "group": "verifier", "steps": 6839, "turns": 1642, "tc_turns": 1512, "tool_calls": 3954, "serial_turns": 449, "batched_turns": 1063, "board_posts": 228},
    {"agent": "verifier-2", "group": "verifier", "steps": 834, "turns": 208, "tc_turns": 195, "tool_calls": 447, "serial_turns": 66, "batched_turns": 129, "board_posts": 17},
    {"agent": "session-cartographer", "group": "worker", "steps": 4649, "turns": 1263, "tc_turns": 1180, "tool_calls": 2307, "serial_turns": 644, "batched_turns": 536, "board_posts": 93},
    {"agent": "peer-weaver", "group": "worker", "steps": 4562, "turns": 1181, "tc_turns": 1071, "tool_calls": 2546, "serial_turns": 506, "batched_turns": 565, "board_posts": 87},
    {"agent": "fractals-probe", "group": "worker", "steps": 4551, "turns": 1252, "tc_turns": 1108, "tool_calls": 2495, "serial_turns": 476, "batched_turns": 632, "board_posts": 84},
    {"agent": "spectral-prover", "group": "worker", "steps": 4399, "turns": 1180, "tc_turns": 1041, "tool_calls": 2449, "serial_turns": 483, "batched_turns": 558, "board_posts": 80},
    {"agent": "continuum-bridge", "group": "worker", "steps": 4307, "turns": 1159, "tc_turns": 1039, "tool_calls": 2418, "serial_turns": 398, "batched_turns": 641, "board_posts": 74},
    {"agent": "gravity-probe", "group": "worker", "steps": 3990, "turns": 1113, "tc_turns": 997, "tool_calls": 2143, "serial_turns": 458, "batched_turns": 539, "board_posts": 62},
    {"agent": "monitor", "group": "monitor", "steps": 4001, "turns": 1122, "tc_turns": 1122, "tool_calls": 1706, "serial_turns": 552, "batched_turns": 570, "board_posts": 6},
    {"agent": "bio-geometry", "group": "worker", "steps": 303, "turns": 85, "tc_turns": 71, "tool_calls": 163, "serial_turns": 23, "batched_turns": 48, "board_posts": 2},
    {"agent": "browser-subagent", "group": "browser", "steps": 125, "turns": 44, "tc_turns": 35, "tool_calls": 52, "serial_turns": 20, "batched_turns": 15, "board_posts": 0},
    {"agent": "blinded-verifier-1", "group": "blinded", "steps": 98, "turns": 38, "tc_turns": 33, "tool_calls": 52, "serial_turns": 21, "batched_turns": 12, "board_posts": 0},
    {"agent": "blinded-verifier-2", "group": "blinded", "steps": 116, "turns": 38, "tc_turns": 32, "tool_calls": 69, "serial_turns": 13, "batched_turns": 19, "board_posts": 0},
    {"agent": "blinded-verifier-3", "group": "blinded", "steps": 62, "turns": 26, "tc_turns": 24, "tool_calls": 32, "serial_turns": 19, "batched_turns": 5, "board_posts": 0},
    {"agent": "blinded-verifier-4", "group": "blinded", "steps": 62, "turns": 25, "tc_turns": 19, "tool_calls": 29, "serial_turns": 13, "batched_turns": 6, "board_posts": 0},
    {"agent": "blinded-verifier-5", "group": "blinded", "steps": 51, "turns": 20, "tc_turns": 15, "tool_calls": 24, "serial_turns": 10, "batched_turns": 5, "board_posts": 0},
)

VERIFIER_LATENCY_SNAPSHOT: dict[str, dict[str, int]] = {
    "pre_v2_all": {"matched": 203, "sum_latency_s": 165017, "median_x2_s": 830, "p90_s": 1299, "max_s": 12638, "sum_queue_depth": 356, "max_queue_depth": 7},
    "pre_v2_active_le_7200s": {"matched": 199, "sum_latency_s": 117940, "median_x2_s": 824, "p90_s": 1180, "max_s": 3867, "sum_queue_depth": 351, "max_queue_depth": 7},
    "post_v2_active": {"matched": 27, "sum_latency_s": 14455, "median_x2_s": 722, "p90_s": 1176, "max_s": 1660, "sum_queue_depth": 45, "max_queue_depth": 4},
}

COORDINATOR_TASK_DRAG_COUNTS: dict[str, int] = {
    "external_zone_b_audit_run": 51,
    "github_aletheia_pr1_polling": 32,
    "git_github_ops_and_triage": 13,
    "other_misc_shell": 10,
    "external_cli_probe_discovery": 2,
}

COUNTERFACTUAL_REWORK_COUNTS: dict[str, dict[str, int]] = {
    "core_audit_001_117": {"full_zone_b_fuzz": 10, "hybrid_zone_b_plus_domain": 17, "doc_linter_hooks": 2, "irreducible_domain": 47},
    "modern_zone_b_097_117": {"full_zone_b_fuzz": 7, "hybrid_zone_b_plus_domain": 8, "doc_linter_hooks": 0, "irreducible_domain": 7},
    "latest_wave_112_116": {"full_zone_b_fuzz": 3, "hybrid_zone_b_plus_domain": 1, "doc_linter_hooks": 0, "irreducible_domain": 0},
    "all_84_pf_falsified": {"full_zone_b_fuzz": 10, "hybrid_zone_b_plus_domain": 19, "doc_linter_hooks": 8, "irreducible_domain": 47},
}


# ---------------------------------------------------------------------------
# Pillar 1: Empirical Audit Outcomes, Convergence & Erlang Non-Churn
# ---------------------------------------------------------------------------

def certify_pillar1_audit_and_erlang(
    categories: tuple[dict[str, Any], ...] = AUDIT_CATEGORY_COUNTS,
    rounds: tuple[dict[str, Any], ...] = AUDIT_ROUND_COUNTS,
    convergence: dict[str, int] = CORE_CONVERGENCE_TABLE,
    erlang: dict[str, dict[str, int]] = ERLANG_BOUNDARY_COUNTS,
) -> dict[str, Any]:
    cats = require_seq(categories, "categories")
    rds = require_seq(rounds, "rounds")
    conv = require_mapping(convergence, "convergence")
    erl = require_mapping(erlang, "erlang")

    cat_v = cat_pf = cat_f = 0
    for row in cats:
        m = require_mapping(row, "category_row")
        require_str(m.get("category"), "category")
        cat_v += require_int(m.get("verified"), "verified", lo=0)
        cat_pf += require_int(m.get("partial_fragile"), "partial_fragile", lo=0)
        cat_f += require_int(m.get("falsified"), "falsified", lo=0)
    total_rows = cat_v + cat_pf + cat_f
    if total_rows <= 0:
        raise TorusActivityError("EMPTY_AUDIT_TABLE", "total audit rows must be positive")

    rd_v = rd_pf = rd_f = 0
    r2_v = r2_tot = 0
    for row in rds:
        m = require_mapping(row, "round_row")
        rname = require_str(m.get("round"), "round")
        rv = require_int(m.get("verified"), "round.verified", lo=0)
        rpf = require_int(m.get("partial_fragile"), "round.partial_fragile", lo=0)
        rf = require_int(m.get("falsified"), "round.falsified", lo=0)
        rd_v += rv
        rd_pf += rpf
        rd_f += rf
        if rname == "R2":
            r2_v = rv
            r2_tot = rv + rpf + rf

    if rd_v != cat_v or rd_pf != cat_pf or rd_f != cat_f:
        raise TorusActivityError("AUDIT_PARTITION_DRIFT", "category and round totals disagree")

    p1 = require_int(conv.get("verified_pass_1"), "verified_pass_1", lo=0)
    p2 = require_int(conv.get("verified_pass_2"), "verified_pass_2", lo=0)
    p3 = require_int(conv.get("verified_pass_3"), "verified_pass_3", lo=0)
    p4 = require_int(conv.get("verified_pass_4"), "verified_pass_4", lo=0)
    p5 = require_int(conv.get("verified_pass_5"), "verified_pass_5", lo=0)
    term_f = require_int(conv.get("terminal_falsified"), "terminal_falsified", lo=0)
    open_pf = require_int(conv.get("open_or_catalog_pf"), "open_or_catalog_pf", lo=0)
    starved = require_int(conv.get("unlogged_queue_starved"), "unlogged_queue_starved", lo=0)

    core_verified_tracks = p1 + p2 + p3 + p4 + p5
    if core_verified_tracks <= 0:
        raise TorusActivityError("NO_VERIFIED_CORE_TRACKS", "verified core tracks must be positive")
    logged_core_tracks = core_verified_tracks + term_f + open_pf
    total_core_ids = logged_core_tracks + starved
    total_passes_to_verify = p1 + 2 * p2 + 3 * p3 + 4 * p4 + 5 * p5
    mean_passes = ratio_q(total_passes_to_verify, core_verified_tracks, "mean_passes")

    pre = require_mapping(erl.get("pre_erlang"), "pre_erlang")
    post = require_mapping(erl.get("post_erlang"), "post_erlang")
    pre_tot = require_int(pre.get("total"), "pre.total", lo=1)
    pre_v = require_int(pre.get("verified"), "pre.verified", lo=0, hi=pre_tot)
    pre_pf = require_int(pre.get("partial_fragile"), "pre.pf", lo=0)
    pre_f = require_int(pre.get("falsified"), "pre.f", lo=0)
    if pre_v + pre_pf + pre_f != pre_tot:
        raise TorusActivityError("PRE_ERLANG_SUM_DRIFT", "pre-Erlang verdict counts do not sum to total")

    post_tot = require_int(post.get("total"), "post.total", lo=1)
    post_v = require_int(post.get("verified"), "post.verified", lo=0, hi=post_tot)
    post_pf = require_int(post.get("partial_fragile"), "post.pf", lo=0)
    post_f = require_int(post.get("falsified"), "post.f", lo=0)
    if post_v + post_pf + post_f != post_tot:
        raise TorusActivityError("POST_ERLANG_SUM_DRIFT", "post-Erlang verdict counts do not sum to total")

    if pre_tot + post_tot != total_rows:
        raise TorusActivityError("ERLANG_SPLIT_DRIFT", "pre + post Erlang counts do not equal total rows")

    pre_r1_tot = require_int(pre.get("r1_total"), "pre.r1_total", lo=1)
    pre_r1_v = require_int(pre.get("r1_verified"), "pre.r1_verified", lo=0, hi=pre_r1_tot)
    post_r1_tot = require_int(post.get("r1_total"), "post.r1_total", lo=1)
    post_r1_v = require_int(post.get("r1_verified"), "post.r1_verified", lo=0, hi=post_r1_tot)
    pre_core_tot = require_int(pre.get("core_total"), "pre.core_total", lo=1)
    pre_core_v = require_int(pre.get("core_verified"), "pre.core_verified", lo=0, hi=pre_core_tot)
    post_core_tot = require_int(post.get("core_total"), "post.core_total", lo=1)
    post_core_v = require_int(post.get("core_verified"), "post.core_verified", lo=0, hi=post_core_tot)
    pre_churn = require_int(pre.get("mid_audit_churn_incidents"), "pre.churn", lo=0)
    post_churn = require_int(post.get("mid_audit_churn_incidents"), "post.churn", lo=0)

    overall_delta = ratio_q(post_v, post_tot) - ratio_q(pre_v, pre_tot)
    r1_delta = ratio_q(post_r1_v, post_r1_tot) - ratio_q(pre_r1_v, pre_r1_tot)
    core_delta = ratio_q(post_core_v, post_core_tot) - ratio_q(pre_core_v, pre_core_tot)

    return {
        "passed": overall_delta > 0 and r1_delta > 0 and post_churn < pre_churn,
        "total_rows": total_rows,
        "verified_rows": cat_v,
        "partial_fragile_rows": cat_pf,
        "falsified_rows": cat_f,
        "verified_rate_q": fmt_q(ratio_q(cat_v, total_rows)),
        "partial_fragile_rate_q": fmt_q(ratio_q(cat_pf, total_rows)),
        "falsified_rate_q": fmt_q(ratio_q(cat_f, total_rows)),
        "r2_convergence_rate_q": fmt_q(ratio_q(r2_v, r2_tot)) if r2_tot > 0 else "0",
        "core_total_ids": total_core_ids,
        "core_logged_ids": logged_core_tracks,
        "core_verified_ids": core_verified_tracks,
        "core_mean_passes_to_verified_q": fmt_q(mean_passes),
        "core_two_pass_cumulative_rate_q": fmt_q(ratio_q(p1 + p2, core_verified_tracks)),
        "erlang_pre_verified_rate_q": fmt_q(ratio_q(pre_v, pre_tot)),
        "erlang_post_verified_rate_q": fmt_q(ratio_q(post_v, post_tot)),
        "erlang_overall_delta_q": fmt_q(overall_delta),
        "erlang_pre_r1_pass_rate_q": fmt_q(ratio_q(pre_r1_v, pre_r1_tot)),
        "erlang_post_r1_pass_rate_q": fmt_q(ratio_q(post_r1_v, post_r1_tot)),
        "erlang_r1_delta_q": fmt_q(r1_delta),
        "erlang_core_only_delta_q": fmt_q(core_delta),
        "erlang_churn_eliminated": pre_churn > 0 and post_churn == 0,
        "gate8_prereg_rows_logged": 0,
        "audit_log_short_5col_rows": 2,
    }


# ---------------------------------------------------------------------------
# Pillar 2: Cross-Continent / Multi-Family Orthogonal Catch Matrix
# ---------------------------------------------------------------------------

def certify_pillar2_multifamily_catch_matrix(
    families: tuple[dict[str, Any], ...] = VERIFIER_FAMILIES_TABLE,
    signatures: tuple[dict[str, Any], ...] = ORTHOGONAL_CATCH_SIGNATURES,
) -> dict[str, Any]:
    fams = require_seq(families, "families")
    sigs = require_seq(signatures, "signatures")

    seen_fams: set[str] = set()
    ext_runs = ext_comp = ext_catch = ext_timeout = ext_cli_fail = 0
    ea_runs = ea_comp = ea_catch = 0
    useu_runs = useu_comp = useu_catch = 0
    per_family: list[dict[str, Any]] = []

    for row in fams:
        m = require_mapping(row, "family_row")
        fname = require_str(m.get("family"), "family")
        if fname in seen_fams:
            raise TorusActivityError("DUPLICATE_FAMILY", f"duplicate family {fname}")
        seen_fams.add(fname)
        region = require_str(m.get("region"), "region")
        runs = require_int(m.get("runs"), "runs", lo=1)
        comp = require_int(m.get("completed"), "completed", lo=0, hi=runs)
        catches = require_int(m.get("catches"), "catches", lo=0, hi=comp)
        passes = require_int(m.get("passes"), "passes", lo=0, hi=comp)
        timeouts = require_int(m.get("timeouts"), "timeouts", lo=0)
        cli_fails = require_int(m.get("cli_fails"), "cli_fails", lo=0)
        if catches + passes != comp:
            raise TorusActivityError("FAMILY_OUTCOME_DRIFT", f"{fname}: catches + passes != completed")
        if comp + timeouts + cli_fails != runs:
            raise TorusActivityError("FAMILY_RUN_DRIFT", f"{fname}: completed + timeouts + cli_fails != runs")

        if region not in ("internal", "internal_zone_b"):
            ext_runs += runs
            ext_comp += comp
            ext_catch += catches
            ext_timeout += timeouts
            ext_cli_fail += cli_fails
        if region == "east_asia":
            ea_runs += runs
            ea_comp += comp
            ea_catch += catches
        elif region in ("us_eu", "us_eu_or_ea_tui"):
            useu_runs += runs
            useu_comp += comp
            useu_catch += catches

        per_family.append({
            "family": fname,
            "region": region,
            "runs": runs,
            "completed": comp,
            "catches": catches,
            "completion_rate_q": fmt_q(ratio_q(comp, runs)),
            "catch_rate_completed_q": fmt_q(ratio_q(catches, comp)) if comp > 0 else "0",
        })

    if ea_runs == 0 or useu_runs == 0:
        raise TorusActivityError("MISSING_REGION_STRATUM", "east_asia and us_eu strata required")

    fam_coverage: dict[str, int] = {f: 0 for f in seen_fams}
    exclusive_signatures = 0
    for sig in sigs:
        sm = require_mapping(sig, "signature")
        require_str(sm.get("signature"), "signature.name")
        require_str(sm.get("example"), "signature.example")
        sig_fams = require_seq(sm.get("families"), "signature.families", min_len=1)
        unique_sf: set[str] = set()
        for sf in sig_fams:
            sfn = require_str(sf, "signature.family")
            if sfn not in seen_fams:
                raise TorusActivityError("UNKNOWN_SIGNATURE_FAMILY", f"unknown family {sfn}")
            if sfn in unique_sf:
                raise TorusActivityError("DUPLICATE_SIGNATURE_FAMILY", f"duplicate {sfn} in signature")
            unique_sf.add(sfn)
            fam_coverage[sfn] += 1
        if len(unique_sf) == 1:
            exclusive_signatures += 1

    max_single_coverage = max(fam_coverage.values())
    total_signatures = len(sigs)
    no_single_family_complete = max_single_coverage < total_signatures

    return {
        "passed": no_single_family_complete and exclusive_signatures >= 4,
        "external_runs_total": ext_runs,
        "external_completed": ext_comp,
        "external_catches": ext_catch,
        "external_harness_failures": ext_timeout + ext_cli_fail,
        "external_harness_failure_rate_q": fmt_q(ratio_q(ext_timeout + ext_cli_fail, ext_runs)),
        "east_asia_completion_rate_q": fmt_q(ratio_q(ea_comp, ea_runs)),
        "east_asia_catch_rate_completed_q": fmt_q(ratio_q(ea_catch, ea_comp)),
        "us_eu_completion_rate_q": fmt_q(ratio_q(useu_comp, useu_runs)),
        "orthogonal_signature_count": total_signatures,
        "single_family_exclusive_signatures": exclusive_signatures,
        "max_single_family_signature_coverage": max_single_coverage,
        "max_single_family_coverage_q": fmt_q(ratio_q(max_single_coverage, total_signatures)),
        "no_single_family_complete": no_single_family_complete,
        "per_family": per_family,
    }


# ---------------------------------------------------------------------------
# Pillar 3: Pareto-Ranked Recurring Defect-Class Taxonomy
# ---------------------------------------------------------------------------

def certify_pillar3_pareto_defect_taxonomy(
    taxonomy: tuple[dict[str, Any], ...] = PARETO_DEFECT_TAXONOMY,
) -> dict[str, Any]:
    rows = require_seq(taxonomy, "taxonomy", min_len=2)
    seen_ids: set[str] = set()
    prev_inc: int | None = None
    total_incidents = 0
    total_board_msgs = 0
    zone_b_incidents = 0
    hygiene_incidents = 0
    parsed: list[dict[str, Any]] = []

    for row in rows:
        m = require_mapping(row, "defect_row")
        did = require_str(m.get("id"), "defect.id")
        if did in seen_ids:
            raise TorusActivityError("DUPLICATE_DEFECT_ID", f"duplicate defect id {did}")
        seen_ids.add(did)
        dname = require_str(m.get("name"), "defect.name")
        zone = require_str(m.get("zone"), "defect.zone")
        if zone not in ("zone_b_api", "hygiene_ops"):
            raise TorusActivityError("INVALID_DEFECT_ZONE", f"unknown defect zone {zone}")
        inc = require_int(m.get("incidents"), "defect.incidents", lo=1)
        bmsgs = require_int(m.get("board_msgs"), "defect.board_msgs", lo=0)
        if prev_inc is not None and inc > prev_inc:
            raise TorusActivityError("PARETO_ORDER_VIOLATION", f"{did} violates descending Pareto order")
        prev_inc = inc
        total_incidents += inc
        total_board_msgs += bmsgs
        if zone == "zone_b_api":
            zone_b_incidents += inc
        else:
            hygiene_incidents += inc
        parsed.append({"id": did, "name": dname, "zone": zone, "incidents": inc, "board_msgs": bmsgs})

    cum = 0
    knee_80_rank = 0
    ranked: list[dict[str, Any]] = []
    for idx, item in enumerate(parsed, start=1):
        cum += item["incidents"]
        share = ratio_q(item["incidents"], total_incidents)
        cum_share = ratio_q(cum, total_incidents)
        if knee_80_rank == 0 and cum * 5 >= 4 * total_incidents:
            knee_80_rank = idx
        ranked.append({
            "rank": idx,
            "id": item["id"],
            "name": item["name"],
            "zone": item["zone"],
            "incidents": item["incidents"],
            "board_msgs": item["board_msgs"],
            "share_q": fmt_q(share),
            "cumulative_share_q": fmt_q(cum_share),
        })

    top5_sum = sum(item["incidents"] for item in parsed[:5])
    return {
        "passed": zone_b_incidents > hygiene_incidents and top5_sum * 2 >= total_incidents,
        "defect_class_count": len(ranked),
        "total_incidents": total_incidents,
        "total_board_citations": total_board_msgs,
        "zone_b_api_incidents": zone_b_incidents,
        "hygiene_ops_incidents": hygiene_incidents,
        "zone_b_api_share_q": fmt_q(ratio_q(zone_b_incidents, total_incidents)),
        "top5_share_q": fmt_q(ratio_q(top5_sum, total_incidents)),
        "pareto_80pct_knee_rank": knee_80_rank,
        "ranked_classes": ranked,
    }


# ---------------------------------------------------------------------------
# Pillar 4: Swarm Throughput, Verifier Latency & Bottleneck Tomography
# ---------------------------------------------------------------------------

def certify_pillar4_throughput_latency_bottlenecks(
    agents: tuple[dict[str, Any], ...] = AGENT_TELEMETRY_17,
    latency: dict[str, dict[str, int]] = VERIFIER_LATENCY_SNAPSHOT,
    tasks: dict[str, int] = COORDINATOR_TASK_DRAG_COUNTS,
    expected_board_posts: int = SNAPSHOT_BOARD_CUTOFF_SEQ,
) -> dict[str, Any]:
    ag_seq = require_seq(agents, "agents")
    lat = require_mapping(latency, "latency")
    tsk = require_mapping(tasks, "tasks")
    exp_posts = require_int(expected_board_posts, "expected_board_posts", lo=1)

    seen_agents: set[str] = set()
    tot_steps = tot_turns = tot_tct = tot_tc = tot_ser = tot_bat = tot_posts = 0
    mon_turns = mon_posts = coord_ser = coord_tct = 0
    best_batch_agent = ""
    best_batch_q = Fraction(-1, 1)
    worst_core_batch_agent = ""
    worst_core_batch_q = Fraction(10**9, 1)
    per_agent: list[dict[str, Any]] = []

    for row in ag_seq:
        m = require_mapping(row, "agent_row")
        aname = require_str(m.get("agent"), "agent")
        if aname in seen_agents:
            raise TorusActivityError("DUPLICATE_AGENT", f"duplicate agent {aname}")
        seen_agents.add(aname)
        grp = require_str(m.get("group"), "group")
        steps = require_int(m.get("steps"), "steps", lo=1)
        turns = require_int(m.get("turns"), "turns", lo=1)
        tct = require_int(m.get("tc_turns"), "tc_turns", lo=1, hi=turns)
        tc = require_int(m.get("tool_calls"), "tool_calls", lo=tct)
        ser = require_int(m.get("serial_turns"), "serial_turns", lo=0)
        bat = require_int(m.get("batched_turns"), "batched_turns", lo=0)
        posts = require_int(m.get("board_posts"), "board_posts", lo=0)
        if ser + bat != tct:
            raise TorusActivityError("AGENT_TURN_DRIFT", f"{aname}: serial + batched != tc_turns")

        tot_steps += steps
        tot_turns += turns
        tot_tct += tct
        tot_tc += tc
        tot_ser += ser
        tot_bat += bat
        tot_posts += posts
        ratio = ratio_q(tc, tct)

        if aname == "monitor":
            mon_turns = turns
            mon_posts = posts
        if aname == "coordinator":
            coord_ser = ser
            coord_tct = tct
        if grp in ("coordinator", "verifier", "worker", "monitor"):
            if ratio > best_batch_q:
                best_batch_q = ratio
                best_batch_agent = aname
            if ratio < worst_core_batch_q:
                worst_core_batch_q = ratio
                worst_core_batch_agent = aname

        per_agent.append({
            "agent": aname,
            "group": grp,
            "steps": steps,
            "turns": turns,
            "tc_turns": tct,
            "tool_calls": tc,
            "serial_turns": ser,
            "batched_turns": bat,
            "board_posts": posts,
            "calls_per_tc_turn_q": fmt_q(ratio),
            "batched_turn_share_q": fmt_q(ratio_q(bat, tct)),
        })

    if tot_posts != exp_posts:
        raise TorusActivityError("BOARD_POST_SUM_DRIFT", f"agent board posts {tot_posts} != {exp_posts}")
    if mon_posts <= 0 or coord_tct <= 0:
        raise TorusActivityError("MISSING_CORE_ROLE", "monitor and coordinator telemetry required")

    pre_act = require_mapping(lat.get("pre_v2_active_le_7200s"), "pre_v2_active_le_7200s")
    post_act = require_mapping(lat.get("post_v2_active"), "post_v2_active")
    pre_all = require_mapping(lat.get("pre_v2_all"), "pre_v2_all")

    pre_n = require_int(pre_act.get("matched"), "pre.matched", lo=1)
    pre_sum = require_int(pre_act.get("sum_latency_s"), "pre.sum_latency_s", lo=1)
    pre_med2 = require_int(pre_act.get("median_x2_s"), "pre.median_x2_s", lo=1)
    pre_max = require_int(pre_act.get("max_s"), "pre.max_s", lo=1)
    pre_qmax = require_int(pre_act.get("max_queue_depth"), "pre.max_queue_depth", lo=1)

    post_n = require_int(post_act.get("matched"), "post.matched", lo=1)
    post_sum = require_int(post_act.get("sum_latency_s"), "post.sum_latency_s", lo=1)
    post_med2 = require_int(post_act.get("median_x2_s"), "post.median_x2_s", lo=1)
    post_max = require_int(post_act.get("max_s"), "post.max_s", lo=1)
    post_qmax = require_int(post_act.get("max_queue_depth"), "post.max_queue_depth", lo=1)

    pre_all_n = require_int(pre_all.get("matched"), "pre_all.matched", lo=pre_n)
    pre_all_sum = require_int(pre_all.get("sum_latency_s"), "pre_all.sum_latency_s", lo=pre_sum)

    pre_mean_q = ratio_q(pre_sum, pre_n)
    post_mean_q = ratio_q(post_sum, post_n)
    mean_drop_q = Fraction(pre_mean_q - post_mean_q, pre_mean_q)
    max_speedup_q = ratio_q(pre_max, post_max)
    qmax_drop_q = ratio_q(pre_qmax - post_qmax, pre_qmax)

    task_total = 0
    for k, v in tsk.items():
        task_total += require_int(v, f"task.{k}", lo=0)
    if task_total <= 0:
        raise TorusActivityError("EMPTY_TASK_COUNTS", "task total must be positive")
    gh_poll = require_int(tsk.get("github_aletheia_pr1_polling"), "github_aletheia_pr1_polling", lo=0, hi=task_total)

    return {
        "passed": post_mean_q < pre_mean_q and post_max < pre_max and post_qmax < pre_qmax,
        "agent_count": len(per_agent),
        "total_steps": tot_steps,
        "total_turns": tot_turns,
        "total_tc_turns": tot_tct,
        "total_tool_calls": tot_tc,
        "total_serial_turns": tot_ser,
        "total_batched_turns": tot_bat,
        "total_board_posts": tot_posts,
        "swarm_calls_per_tc_turn_q": fmt_q(ratio_q(tot_tc, tot_tct)),
        "swarm_batched_turn_share_q": fmt_q(ratio_q(tot_bat, tot_tct)),
        "best_batching_core_agent": best_batch_agent,
        "best_batching_core_q": fmt_q(best_batch_q),
        "worst_batching_core_agent": worst_core_batch_agent,
        "worst_batching_core_q": fmt_q(worst_core_batch_q),
        "monitor_turns_per_post_q": fmt_q(ratio_q(mon_turns, mon_posts)),
        "monitor_turn_share_q": fmt_q(ratio_q(mon_turns, tot_turns)),
        "coordinator_serial_share_q": fmt_q(ratio_q(coord_ser, coord_tct)),
        "pre_v2_all_mean_s_q": fmt_q(ratio_q(pre_all_sum, pre_all_n)),
        "pre_v2_active_mean_s_q": fmt_q(pre_mean_q),
        "post_v2_active_mean_s_q": fmt_q(post_mean_q),
        "v2_active_mean_reduction_q": fmt_q(mean_drop_q),
        "pre_v2_active_median_s_q": fmt_q(ratio_q(pre_med2, 2)),
        "post_v2_active_median_s_q": fmt_q(ratio_q(post_med2, 2)),
        "v2_active_tail_max_speedup_q": fmt_q(max_speedup_q),
        "v2_max_queue_depth_reduction_q": fmt_q(qmax_drop_q),
        "audit_114_starvation_wait_s": 7091,
        "coordinator_task_total": task_total,
        "aletheia_pr1_polling_tasks": gh_poll,
        "aletheia_pr1_polling_share_q": fmt_q(ratio_q(gh_poll, task_total)),
        "per_agent": per_agent,
    }


# ---------------------------------------------------------------------------
# Pillar 5: Looping Back In — v2.1 Upgrades, Live Zone-B Fuzz & Counterfactuals
# ---------------------------------------------------------------------------

def evaluate_prepush_git_hook(record: dict[str, Any]) -> dict[str, Any]:
    """Deterministic `aletheia v2.1` pre-push DCO / isPrivate / GraphQL / OpenBLAS gate."""
    m = require_mapping(record, "prepush_record")
    dco = require_bool(m.get("has_dco_signoff"), "has_dco_signoff")
    is_priv = require_bool(m.get("repo_is_private"), "repo_is_private")
    allow_priv = require_bool(m.get("explicit_private_allowed"), "explicit_private_allowed")
    git_files = require_int(m.get("git_changed_files"), "git_changed_files", lo=0)
    gql_files = require_int(m.get("graphql_files_listed"), "graphql_files_listed", lo=0)
    openblas = require_int(m.get("openblas_num_threads"), "openblas_num_threads", lo=0)
    self_author = require_bool(m.get("pr_is_self_authored"), "pr_is_self_authored")
    action = require_str(m.get("review_action"), "review_action")
    if action not in ("NONE", "COMMENT", "APPROVE", "REQUEST_CHANGES"):
        raise TorusActivityError("INVALID_REVIEW_ACTION", f"unknown review_action {action}")

    violations: list[str] = []
    if not dco:
        violations.append("MISSING_DCO_SIGNOFF")
    if is_priv and not allow_priv:
        violations.append("PRIVATE_REPO_BLOCKED")
    if git_files > gql_files:
        violations.append("GRAPHQL_100_FILE_TRUNCATION")
    if openblas != 1:
        violations.append("OPENBLAS_THREADS_UNPINNED")
    if self_author and action in ("APPROVE", "REQUEST_CHANGES"):
        violations.append("SELF_AUTHORED_REVIEW_422")

    return {"passed": len(violations) == 0, "violations": violations}


def route_dual_verifier(
    v1_queue: int,
    v2_queue: int,
    oldest_wait_s: int,
    *,
    starvation_cap_s: int = 1800,
) -> dict[str, Any]:
    """Load-balanced dual-verifier routing policy closing `AUDIT-114` queue starvation."""
    q1 = require_int(v1_queue, "v1_queue", lo=0)
    q2 = require_int(v2_queue, "v2_queue", lo=0)
    wait = require_int(oldest_wait_s, "oldest_wait_s", lo=0)
    cap = require_int(starvation_cap_s, "starvation_cap_s", lo=60)

    starvation_reroute = wait > cap
    if q2 < q1 or starvation_reroute:
        target = "verifier-2"
    else:
        target = "verifier"
    return {
        "target": target,
        "starvation_reroute": starvation_reroute,
        "queue_imbalance": abs(q1 - q2),
    }


def run_zone_b_preflight_fuzz_matrix(
    *,
    extra_vectors: tuple[tuple[str, Any], ...] = (),
    positive_digest: str = "a" * 64,
) -> dict[str, Any]:
    """Execute all 12 recurring Zone-B attacks live against our own `strict_cert_io` contract."""

    class _IntSub(int):
        pass

    class _ListSub(list):
        pass

    class _DictSub(dict):
        pass

    deep_list: Any = 0
    for _ in range(1500):
        deep_list = [deep_list]
    deep_json = "[" * 100 + "0" + "]" * 100
    good_hex = require_hex64_ascii(positive_digest, "positive_digest")

    attacks: list[tuple[str, Any]] = [
        ("V01_non_ascii_hmac_digest", lambda: constant_time_hex64_equal("\u00e9" * 64, good_hex)),
        ("V02_lone_surrogate_hmac_digest", lambda: constant_time_hex64_equal(chr(0xD800) * 64, good_hex)),
        ("V03_in_memory_10_pow_5000", lambda: canonical_json_bytes({"x": 10**5000})),
        ("V04_json_5000_digit_int", lambda: parse_strict_json('{"n":' + ("9" * 5000) + "}")),
        ("V05_deep_1500_python_list", lambda: validate_json_value(deep_list)),
        ("V06_deep_100_json_text", lambda: parse_strict_json(deep_json)),
        ("V07_bool_as_int_forgery", lambda: require_int(True, "count")),
        ("V08_int_subclass_bypass", lambda: validate_json_value({"n": _IntSub(1)})),
        ("V09_list_subclass_bypass", lambda: require_seq(_ListSub([1, 2]), "items")),
        ("V10_dict_subclass_bypass", lambda: require_mapping(_DictSub({"a": 1}), "cfg")),
        ("V11_duplicate_json_key", lambda: parse_strict_json('{"a":1,"a":2}')),
        ("V12_json_float_and_nan", lambda: parse_strict_json('{"x":NaN}')),
    ]
    for item in require_seq(extra_vectors, "extra_vectors", min_len=0):
        attacks.append(item)

    blocked = 0
    results: list[dict[str, Any]] = []
    for name, fn in attacks:
        try:
            fn()
        except TorusActivityError as exc:
            blocked += 1
            results.append({"vector": name, "blocked": True, "code": exc.code})
        else:
            results.append({"vector": name, "blocked": False, "code": "UNBLOCKED"})

    pos_ok = constant_time_hex64_equal(good_hex, "a" * 64)
    return {
        "passed": blocked == len(attacks) and pos_ok,
        "vectors_run": len(attacks),
        "vectors_blocked": blocked,
        "positive_control_ok": pos_ok,
        "results": results,
    }


def certify_pillar5_v21_upgrades_and_counterfactual(
    counterfactual: dict[str, dict[str, int]] = COUNTERFACTUAL_REWORK_COUNTS,
) -> dict[str, Any]:
    cf = require_mapping(counterfactual, "counterfactual")
    strata_out: dict[str, dict[str, Any]] = {}
    for key in ("core_audit_001_117", "modern_zone_b_097_117", "latest_wave_112_116", "all_84_pf_falsified"):
        row = require_mapping(cf.get(key), key)
        full_zb = require_int(row.get("full_zone_b_fuzz"), f"{key}.full", lo=0)
        hyb_zb = require_int(row.get("hybrid_zone_b_plus_domain"), f"{key}.hybrid", lo=0)
        doc_l = require_int(row.get("doc_linter_hooks"), f"{key}.doc", lo=0)
        irred = require_int(row.get("irreducible_domain"), f"{key}.irred", lo=0)
        tot = full_zb + hyb_zb + doc_l + irred
        if tot <= 0:
            raise TorusActivityError("EMPTY_COUNTERFACTUAL_STRATUM", f"{key} total must be positive")
        strata_out[key] = {
            "total_rework_loops": tot,
            "full_eliminated_zone_b_fuzz": full_zb,
            "hybrid_partially_caught": hyb_zb,
            "doc_linter_eliminated": doc_l,
            "irreducible_domain_semantic": irred,
            "full_elimination_rate_q": fmt_q(ratio_q(full_zb, tot)),
            "any_zone_b_impact_rate_q": fmt_q(ratio_q(full_zb + hyb_zb, tot)),
            "irreducible_domain_share_q": fmt_q(ratio_q(irred, tot)),
        }

    fuzz = run_zone_b_preflight_fuzz_matrix()

    clean_hook = evaluate_prepush_git_hook({
        "has_dco_signoff": True,
        "repo_is_private": False,
        "explicit_private_allowed": False,
        "git_changed_files": 4,
        "graphql_files_listed": 4,
        "openblas_num_threads": 1,
        "pr_is_self_authored": False,
        "review_action": "APPROVE",
    })
    bad_hook = evaluate_prepush_git_hook({
        "has_dco_signoff": False,
        "repo_is_private": True,
        "explicit_private_allowed": False,
        "git_changed_files": 463,
        "graphql_files_listed": 100,
        "openblas_num_threads": 16,
        "pr_is_self_authored": True,
        "review_action": "APPROVE",
    })
    route_audit114 = route_dual_verifier(v1_queue=4, v2_queue=0, oldest_wait_s=7091)
    route_balanced = route_dual_verifier(v1_queue=1, v2_queue=2, oldest_wait_s=300)

    checks = (
        fuzz["passed"],
        clean_hook["passed"],
        not bad_hook["passed"],
        len(bad_hook["violations"]) == 5,
        route_audit114["target"] == "verifier-2",
        route_audit114["starvation_reroute"],
        route_balanced["target"] == "verifier",
        not route_balanced["starvation_reroute"],
    )

    return {
        "passed": all(checks),
        "counterfactual_strata": strata_out,
        "zone_b_preflight_fuzz_12_vectors": fuzz,
        "prepush_git_hook_demo": {"clean_passed": clean_hook["passed"], "all5_violations": bad_hook["violations"]},
        "dual_verifier_routing_demo": {"audit_114_reroute": route_audit114, "balanced_route": route_balanced},
    }


def build_audit118a_payload() -> dict[str, Any]:
    """Build deterministic self-contained pure-Z/Q payload for Track S19a (AUDIT-118A)."""
    p1 = certify_pillar1_audit_and_erlang()
    p2 = certify_pillar2_multifamily_catch_matrix()
    p3 = certify_pillar3_pareto_defect_taxonomy()
    p4 = certify_pillar4_throughput_latency_bottlenecks()
    p5 = certify_pillar5_v21_upgrades_and_counterfactual()
    all_passed = all(p["passed"] for p in (p1, p2, p3, p4, p5))
    return {
        "audit_id": "AUDIT-118A",
        "track": "track-s19a-torus-activity-tomography",
        "oracle_class": "exact+empirical-corpus",
        "novelty_class": "N1",
        "snapshot_cutoff": {
            "utc": SNAPSHOT_CUTOFF_UTC,
            "board_cutoff_seq": SNAPSHOT_BOARD_CUTOFF_SEQ,
            "board_prefix_sha256": SNAPSHOT_BOARD_PREFIX_SHA256,
            "audit_log_280_slice_sha256": SNAPSHOT_AUDIT_SLICE_SHA256,
            "tasks_108_manifest_sha256": SNAPSHOT_TASKS_MANIFEST_SHA256,
        },
        "all_passed": all_passed,
        "pillar1_audit_outcomes_and_erlang": p1,
        "pillar2_multifamily_catch_matrix": p2,
        "pillar3_pareto_defect_taxonomy": p3,
        "pillar4_throughput_latency_bottlenecks": p4,
        "pillar5_v21_upgrades_and_counterfactual": p5,
    }
