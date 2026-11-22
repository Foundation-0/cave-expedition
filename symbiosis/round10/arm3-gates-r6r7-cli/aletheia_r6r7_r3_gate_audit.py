#!/usr/bin/env python3
"""Aletheia v1.4.0 -> v1.5.0/v2.0 R6/R7 Pinned-Measured Gate, Two-Direction R3,
Oracle-Class/Gate-8 Subspace Latch, and Round-10 Portal Audit Certifier.

Pure Python 3 standard library. Zero floating-point arithmetic on trust paths or
certificate outputs (exact int and fractions.Fraction only). Zero bare asserts.
Strictly read-only when inspecting local Round-10 portals and repos/aletheia-live.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable


SCHEMA_VERSION = "aletheia.r6r7_r3_gate_audit.v1"
AUDIT_ID = "AUDIT-086R"

PINNED_RULE_KEYS = frozenset(
    {
        "rule_id",
        "expected_check_ids",
        "min_sq_norm",
        "max_sq_norm",
        "expected_header_alpha",
        "max_vector_dim",
    }
)
SUBMISSION_KEYS = frozenset(
    {
        "declared_sha256",
        "declared_sq_norm",
        "declared_header_alpha",
        "declared_status",
        "submitter_rule_overrides",
    }
)
PAYLOAD_KEYS = frozenset({"header_alpha", "vector_entries"})
ALLOWED_DECLARED_STATUSES = frozenset({"PASS", "CANDIDATE"})

R3_RECORD_KEYS = frozenset(
    {
        "require_multi_oracle",
        "oracle_verdict",
        "artifact_sha256",
        "score_int",
    }
)

ORACLE_CONTRACT_KEYS = frozenset({"oracle_class", "evidence_basis", "feedback_channel"})
EXACT_ORACLE_BASES = frozenset(
    {
        "formal_proof",
        "symbolic_identity",
        "per_input_certificate",
        "exhaustive_enumeration",
    }
)
SAMPLED_ORACLE_BASES = frozenset(
    {
        "random_finite_sample",
        "random_finite_sample_exact_arithmetic",
    }
)
EXPECTED_FEEDBACK_CHANNEL = {
    "exact": "full_counterexample_and_repair",
    "sampled": "family_only_with_fresh_post_repair_seed",
    "anchor": "none_to_proposer_spec_owner_only",
    "reference_replay": "diff_against_upstream_reference",
}

PINNED_ALETHEIA_LIVE_REFS = {
    "refs/heads/main": "6a6c1af8fcae1dd7b2bc6d0cc8f471cdbd64747f",
    "refs/remotes/origin/pr/1": "aa471867b21a0645c3290dea55c46b9732765ae9",
    "refs/remotes/origin/pr/7": "362a8285d16eacdd14d549ccb55dec64c3a527af",
    "refs/remotes/origin/pr/8": "aa920b1a908b3131c6eb3116f2e9ba21bccd0834",
    "refs/remotes/origin/pr/9": "ffa0ed4290d782a945eb4f77e3423195460672d0",
}

PINNED_PORTAL_SHA256 = {
    "issue_2.md": "c3166387362f8d8bca181eebbfffdae6f7af9bf838317f8e1cf86cbda2e82d15",
    "issue_3.md": "88b7d14041f36f25603ac27a4a1299472d457194034ec2ce7faee33fba9c05a1",
    "issue_4.md": "e3da52efc1e8f44fac4e237f1d08dd8f9b41a48c348a18b89686e65ccbac7fad",
    "issue_5.md": "684e5697190b2505e10c048281e49fe307634db3af3146a2143b601c7e7da070",
    "pr_1.md": "1a32bd825f1f38000e0cb9edf16f8a943b6c9a725ba126b350cb48ec1b638d5d",
    "pr_7.md": "63c2d4283ecb8673bf150f756e910dd0e86321dabb6600b27ff7bc03f5cb043c",
    "pr_8.md": "bec1e4a1f8c394f1a5087a6a13af0d6032d890109945cb26766a7d48f750cd14",
    "pr_9_files/spec/proposals/OWN_TERMS_FIRST.md": (
        "bd14863344c494f1e0399d486267231fe3002fe7e005d354e2f82a8c105d6746"
    ),
}

PORTAL_VERBATIM_ANCHORS = {
    "issue_3.md": (
        "R1 to R5 are necessary, not sufficient.",
        "Direction (ii) is the costly one:",
    ),
    "issue_5.md": (
        "We ran Aletheia v1 at 13bd9fe on four outside artifacts:",
        "### 1. The mutator sees only guards it recognises by name, so 100 percent can cover one site of several",
    ),
    "pr_7.md": (
        "Fixes the four review blockers on #1, the failing CI install step and two audit-log checks.",
        "Each row is one commit, with its test in `tests/test_aletheia_cli.py` (`test_15` to `test_20`).",
    ),
    "pr_8.md": (
        "| Comparator config accepted one module as challenge and solution | `cc8c3b8` | `test_31` | yes |",
        "## Left for the author",
    ),
    "pr_9_files/spec/proposals/OWN_TERMS_FIRST.md": (
        "# Proposal: test a pattern on its own terms first",
        "1. **Two phases, kept apart.**",
    ),
}


def _is_strict_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_clean_ascii(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) > 0
        and value == value.strip()
        and all(32 <= ord(ch) <= 126 for ch in value)
    )


def _is_lower_hex(value: object, expected_len: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == expected_len
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _fmt_q(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)


def _parse_exact_rational(value: object) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if _is_strict_int(value):
        return Fraction(value, 1)
    if not _is_clean_ascii(value):
        raise ValueError("RATIONAL_TYPE_OR_SYNTAX")
    parts = value.split("/")
    if len(parts) > 2:
        raise ValueError("RATIONAL_TOO_MANY_SLASHES")
    num_s = parts[0]
    neg = num_s.startswith("-")
    digits = num_s[1:] if neg else num_s
    if not digits or not digits.isdigit():
        raise ValueError("RATIONAL_INVALID_NUMERATOR")
    num = -int(digits) if neg else int(digits)
    if len(parts) == 1:
        return Fraction(num, 1)
    den_s = parts[1]
    if not den_s or not den_s.isdigit():
        raise ValueError("RATIONAL_INVALID_DENOMINATOR")
    den = int(den_s)
    if den <= 0:
        raise ValueError("RATIONAL_NONPOSITIVE_DENOMINATOR")
    return Fraction(num, den)


def _reject_json_float(raw: str) -> Any:
    raise ValueError(f"JSON_FLOAT_FORBIDDEN:{raw}")


def _reject_json_constant(raw: str) -> Any:
    raise ValueError(f"JSON_CONSTANT_FORBIDDEN:{raw}")


def _no_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f"JSON_DUPLICATE_KEY:{k}")
        out[k] = v
    return out


def _parse_strict_json_bytes(raw: bytes) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("PAYLOAD_INVALID_UTF8") from exc
    try:
        parsed = json.loads(
            text,
            parse_float=_reject_json_float,
            parse_constant=_reject_json_constant,
            object_pairs_hook=_no_duplicate_json_keys,
        )
    except json.JSONDecodeError as exc:
        raise ValueError("PAYLOAD_INVALID_JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("PAYLOAD_ROOT_NOT_OBJECT")
    return parsed


# ---------------------------------------------------------------------------
# Component 1: R6 (Pinned Checks) & R7 (Measured, Not Declared) Gate
# ---------------------------------------------------------------------------


def evaluate_r6_r7_gate(
    pinned_rules: dict[str, Any],
    submission: dict[str, Any],
    artifact_bytes: bytes,
) -> dict[str, Any]:
    """Fail-closed R6 (owner-pinned rules) + R7 (byte-recomputed measurements) gate."""
    if not isinstance(pinned_rules, dict) or frozenset(pinned_rules.keys()) != PINNED_RULE_KEYS:
        raise ValueError("R6_PINNED_RULES_SCHEMA_MISMATCH")
    rule_id = pinned_rules["rule_id"]
    if not _is_clean_ascii(rule_id):
        raise ValueError("R6_INVALID_RULE_ID")
    check_ids = pinned_rules["expected_check_ids"]
    if not isinstance(check_ids, (list, tuple)) or len(check_ids) == 0:
        raise ValueError("R6_EMPTY_CHECK_IDS")
    if any(not _is_clean_ascii(cid) for cid in check_ids):
        raise ValueError("R6_INVALID_CHECK_ID")
    if len({cid.lower() for cid in check_ids}) != len(check_ids):
        raise ValueError("R6_DUPLICATE_CHECK_ID")

    min_sq = _parse_exact_rational(pinned_rules["min_sq_norm"])
    max_sq = _parse_exact_rational(pinned_rules["max_sq_norm"])
    if min_sq < Fraction(0, 1):
        raise ValueError("R6_NEGATIVE_MIN_SQ_NORM")
    if max_sq < min_sq:
        raise ValueError("R6_INVERTED_SQ_NORM_RANGE")
    exp_alpha = _parse_exact_rational(pinned_rules["expected_header_alpha"])
    if exp_alpha <= Fraction(0, 1):
        raise ValueError("R6_NONPOSITIVE_EXPECTED_ALPHA")
    max_dim = pinned_rules["max_vector_dim"]
    if not _is_strict_int(max_dim) or max_dim <= 0:
        raise ValueError("R6_INVALID_MAX_VECTOR_DIM")

    if not isinstance(submission, dict) or frozenset(submission.keys()) != SUBMISSION_KEYS:
        raise ValueError("R6_SUBMISSION_SCHEMA_MISMATCH")
    overrides = submission["submitter_rule_overrides"]
    if not isinstance(overrides, dict):
        raise ValueError("R6_OVERRIDES_NOT_OBJECT")
    if len(overrides) > 0:
        raise ValueError("R6_SUBMITTER_RULE_OVERRIDE")

    declared_status = submission["declared_status"]
    if not isinstance(declared_status, str) or declared_status not in ALLOWED_DECLARED_STATUSES:
        raise ValueError("R6_INVALID_DECLARED_STATUS")

    if not isinstance(artifact_bytes, bytes):
        raise ValueError("R7_ARTIFACT_NOT_BYTES")
    if len(artifact_bytes) == 0:
        raise ValueError("R7_NULL_ARTIFACT_BYTES")

    measured_sha256 = hashlib.sha256(artifact_bytes).hexdigest()
    declared_sha256 = submission["declared_sha256"]
    if not _is_lower_hex(declared_sha256, 64):
        raise ValueError("R7_INVALID_DECLARED_SHA256")
    if declared_sha256 != measured_sha256:
        raise ValueError("R7_DECLARED_SHA256_MISMATCH")

    payload = _parse_strict_json_bytes(artifact_bytes)
    if frozenset(payload.keys()) != PAYLOAD_KEYS:
        raise ValueError("R7_PAYLOAD_SCHEMA_MISMATCH")

    measured_alpha = _parse_exact_rational(payload["header_alpha"])
    entries = payload["vector_entries"]
    if not isinstance(entries, list) or len(entries) == 0:
        raise ValueError("R7_EMPTY_VECTOR_ENTRIES")
    if len(entries) > max_dim:
        raise ValueError("R6_VECTOR_DIM_EXCEEDS_MAX")

    vec = [_parse_exact_rational(x) for x in entries]
    measured_sq_norm = sum((v * v for v in vec), Fraction(0, 1))

    declared_sq = _parse_exact_rational(submission["declared_sq_norm"])
    declared_alpha = _parse_exact_rational(submission["declared_header_alpha"])
    if declared_sq != measured_sq_norm:
        raise ValueError("R7_DECLARED_NORM_MISMATCH")
    if declared_alpha != measured_alpha:
        raise ValueError("R7_DECLARED_ALPHA_MISMATCH")

    if measured_alpha != exp_alpha:
        raise ValueError("R6_HEADER_ALPHA_OUT_OF_SPEC")
    if measured_sq_norm < min_sq:
        raise ValueError("R6_MEASURED_NORM_BELOW_MIN")
    if measured_sq_norm > max_sq:
        raise ValueError("R6_MEASURED_NORM_ABOVE_MAX")

    return {
        "status": "ACCEPTED",
        "rule_id": rule_id,
        "checked_ids": list(check_ids),
        "measured_sha256": measured_sha256,
        "measured_sq_norm": _fmt_q(measured_sq_norm),
        "measured_header_alpha": _fmt_q(measured_alpha),
        "vector_dim": len(vec),
    }


def _canonical_payload_bytes(header_alpha: str, vector_entries: list[str]) -> bytes:
    obj = {"header_alpha": header_alpha, "vector_entries": vector_entries}
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def run_record_b_witnesses() -> dict[str, Any]:
    """Reproduce aletheia#3 Record B failure classes in exact pure-Q arithmetic."""
    pinned_rules = {
        "rule_id": "aletheia.r6r7.record_b_adapter_gate",
        "expected_check_ids": ["r7_sha256", "r7_sq_norm", "r6_header_alpha", "r7_non_null"],
        "min_sq_norm": "0",
        "max_sq_norm": "20",
        "expected_header_alpha": "4",
        "max_vector_dim": 8,
    }

    valid_bytes = _canonical_payload_bytes("4", ["3", "2", "1"])
    valid_sha = hashlib.sha256(valid_bytes).hexdigest()
    valid_sub = {
        "declared_sha256": valid_sha,
        "declared_sq_norm": "14",
        "declared_header_alpha": "4",
        "declared_status": "PASS",
        "submitter_rule_overrides": {},
    }
    accepted = evaluate_r6_r7_gate(pinned_rules, valid_sub, valid_bytes)

    # Exact rational witness attaining 27^2 + 4^2 + (3/5)^2 + (6/5)^2 = 3734/5 = 746.8 (> 20)
    scaled_bytes = _canonical_payload_bytes("4", ["27", "4", "3/5", "6/5"])
    scaled_sha = hashlib.sha256(scaled_bytes).hexdigest()
    alpha32_bytes = _canonical_payload_bytes("32", ["3", "2", "1"])
    alpha32_sha = hashlib.sha256(alpha32_bytes).hexdigest()

    negative_cases = [
        (
            "B1a_declared_norm_forgery",
            {
                "declared_sha256": scaled_sha,
                "declared_sq_norm": "18",
                "declared_header_alpha": "4",
                "declared_status": "PASS",
                "submitter_rule_overrides": {},
            },
            scaled_bytes,
            "R7_DECLARED_NORM_MISMATCH",
        ),
        (
            "B1b_scaled_factor_x8_sq_norm_3734_over_5",
            {
                "declared_sha256": scaled_sha,
                "declared_sq_norm": "3734/5",
                "declared_header_alpha": "4",
                "declared_status": "PASS",
                "submitter_rule_overrides": {},
            },
            scaled_bytes,
            "R6_MEASURED_NORM_ABOVE_MAX",
        ),
        (
            "B1c_header_alpha_32_vs_pinned_4",
            {
                "declared_sha256": alpha32_sha,
                "declared_sq_norm": "14",
                "declared_header_alpha": "32",
                "declared_status": "PASS",
                "submitter_rule_overrides": {},
            },
            alpha32_bytes,
            "R6_HEADER_ALPHA_OUT_OF_SPEC",
        ),
        (
            "B2_null_adapter_empty_bytes",
            valid_sub,
            b"",
            "R7_NULL_ARTIFACT_BYTES",
        ),
        (
            "B3_r6_submitter_threshold_override",
            {
                **valid_sub,
                "submitter_rule_overrides": {"max_sq_norm": "1000"},
            },
            valid_bytes,
            "R6_SUBMITTER_RULE_OVERRIDE",
        ),
        (
            "B4_declared_sha256_mismatch",
            {
                **valid_sub,
                "declared_sha256": "0" * 64,
            },
            valid_bytes,
            "R7_DECLARED_SHA256_MISMATCH",
        ),
    ]

    caught = []
    for name, sub, raw, expected_code in negative_cases:
        got_code = None
        try:
            evaluate_r6_r7_gate(pinned_rules, sub, raw)
        except ValueError as exc:
            got_code = str(exc)
        if got_code != expected_code:
            raise ValueError(f"WITNESS_MISMATCH:{name}:{got_code}")
        caught.append({"case": name, "rejected_code": got_code})

    return {
        "valid_baseline": accepted,
        "record_b_exact_scaled_sq_norm": "3734/5",
        "negative_witnesses_caught": caught,
        "all_caught": True,
    }


# ---------------------------------------------------------------------------
# Component 2: Two-Direction R3 Re-Spelling Certifier (aletheia#3 Note D)
# ---------------------------------------------------------------------------


def hardened_r3_multi_oracle_gate(record: Any) -> bool:
    """Strict two-direction R3 gate: rejects all type/spelling drifts in BOTH directions."""
    if not isinstance(record, dict) or frozenset(record.keys()) != R3_RECORD_KEYS:
        return False
    flag = record["require_multi_oracle"]
    if not isinstance(flag, bool):
        return False
    if not flag:
        return False
    verdict = record["oracle_verdict"]
    if not isinstance(verdict, str) or verdict != "VERIFIED":
        return False
    digest = record["artifact_sha256"]
    if not _is_lower_hex(digest, 64):
        return False
    score = record["score_int"]
    if not _is_strict_int(score) or score < 1:
        return False
    return True


def vulnerable_note_d_gate(record: Any) -> bool:
    """Reproducer of aletheia#3 Note D: re-spelling bool True as int 1 skips check."""
    if not isinstance(record, dict):
        return False
    flag = record.get("require_multi_oracle")
    if flag is False:
        return False
    if flag is True and record.get("oracle_verdict") != "VERIFIED":
        return False
    digest = record.get("artifact_sha256")
    if not _is_lower_hex(digest, 64):
        return False
    score = record.get("score_int")
    if not _is_strict_int(score) or score < 1:
        return False
    return True


def _strict_typed_equal(left: object, right: object) -> bool:
    """Exact recursive equality preserving runtime types (so 1 != True, 1 != 1.0)."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        if set(left.keys()) != set(right.keys()):
            return False
        return all(_strict_typed_equal(left[k], right[k]) for k in left)
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(_strict_typed_equal(x, y) for x, y in zip(left, right))
    return left == right


def certify_two_direction_r3(
    gate_fn: Callable[[Any], bool],
    accepted_case: dict[str, Any],
    rejected_case: dict[str, Any],
    accepted_respellings: list[tuple[str, Any]],
    rejected_respellings: list[tuple[str, Any]],
) -> dict[str, Any]:
    """Certify both Direction (i) (accept->reject) and Direction (ii) (reject stays reject)."""
    if not accepted_respellings:
        raise ValueError("R3_EMPTY_DIR1_CASES")
    if not rejected_respellings:
        raise ValueError("R3_EMPTY_DIR2_CASES")
    if gate_fn(accepted_case) is not True:
        raise ValueError("R3_BASELINE_ACCEPT_FAILED")
    if gate_fn(rejected_case) is not False:
        raise ValueError("R3_BASELINE_REJECT_FAILED")

    seen_labels: set[str] = set()
    dir1_failures: list[str] = []
    for label, mutated in accepted_respellings:
        if not _is_clean_ascii(label):
            raise ValueError("R3_INVALID_DIR1_LABEL")
        low = label.lower()
        if low in seen_labels:
            raise ValueError("R3_DUPLICATE_LABEL")
        seen_labels.add(low)
        if _strict_typed_equal(mutated, accepted_case):
            raise ValueError("R3_NOOP_DIR1_CASE")
        if gate_fn(mutated) is not False:
            dir1_failures.append(label)

    dir2_failures: list[str] = []
    for label, mutated in rejected_respellings:
        if not _is_clean_ascii(label):
            raise ValueError("R3_INVALID_DIR2_LABEL")
        low = label.lower()
        if low in seen_labels:
            raise ValueError("R3_DUPLICATE_LABEL")
        seen_labels.add(low)
        if _strict_typed_equal(mutated, rejected_case):
            raise ValueError("R3_NOOP_DIR2_CASE")
        if gate_fn(mutated) is not False:
            dir2_failures.append(label)

    return {
        "passed": len(dir1_failures) == 0 and len(dir2_failures) == 0,
        "dir1_total": len(accepted_respellings),
        "dir1_rejected": len(accepted_respellings) - len(dir1_failures),
        "dir1_failures": dir1_failures,
        "dir2_total": len(rejected_respellings),
        "dir2_stayed_rejected": len(rejected_respellings) - len(dir2_failures),
        "dir2_failures": dir2_failures,
    }


def run_r3_note_d_witness() -> dict[str, Any]:
    """Certify hardened_r3_multi_oracle_gate passes both directions while Note D fails Dir (ii)."""
    sha_ok = "a" * 64
    accepted = {
        "require_multi_oracle": True,
        "oracle_verdict": "VERIFIED",
        "artifact_sha256": sha_ok,
        "score_int": 1,
    }
    rejected = {
        "require_multi_oracle": True,
        "oracle_verdict": "FAILED",
        "artifact_sha256": sha_ok,
        "score_int": 1,
    }
    dir1 = [
        ("bool_true_as_int_1", {**accepted, "require_multi_oracle": 1}),
        ("bool_true_as_str_true", {**accepted, "require_multi_oracle": "true"}),
        ("verdict_trailing_newline", {**accepted, "oracle_verdict": "VERIFIED\n"}),
        ("verdict_zwsp_u200b", {**accepted, "oracle_verdict": "VERIFIED\u200b"}),
        ("sha_trailing_newline", {**accepted, "artifact_sha256": sha_ok + "\n"}),
        ("sha_uppercase_hex", {**accepted, "artifact_sha256": "A" * 64}),
        ("score_int_as_bool_true", {**accepted, "score_int": True}),
        ("score_int_as_str_1", {**accepted, "score_int": "1"}),
    ]
    dir2 = [
        ("bool_true_as_int_1_note_d", {**rejected, "require_multi_oracle": 1}),
        ("bool_true_as_str_true_on_reject", {**rejected, "require_multi_oracle": "true"}),
        ("bool_false_as_int_0", {**rejected, "require_multi_oracle": 0}),
        ("bool_false_as_str_false", {**rejected, "require_multi_oracle": "false"}),
        ("verdict_failed_trailing_newline", {**rejected, "oracle_verdict": "FAILED\n"}),
        ("sha_trailing_newline_on_reject", {**rejected, "artifact_sha256": sha_ok + "\n"}),
    ]
    hardened_res = certify_two_direction_r3(hardened_r3_multi_oracle_gate, accepted, rejected, dir1, dir2)
    vulnerable_res = certify_two_direction_r3(vulnerable_note_d_gate, accepted, rejected, dir1, dir2)
    return {
        "hardened_gate": hardened_res,
        "vulnerable_note_d_gate": vulnerable_res,
        "note_d_dir2_flip_exposed": "bool_true_as_int_1_note_d" in vulnerable_res["dir2_failures"],
    }


# ---------------------------------------------------------------------------
# Component 3: Sampled Integrity NOT_SHOWN, Oracle Contract & Gate-8 Subspace Latch
# ---------------------------------------------------------------------------


def evaluate_sampled_integrity(
    tested_count: int,
    total_discovered: int,
    hits_found: int,
) -> dict[str, Any]:
    """aletheia#3 sec 4: sampled gate-integrity with 0 hits is NOT_SHOWN, never PASS."""
    if not _is_strict_int(total_discovered) or total_discovered <= 0:
        raise ValueError("SAMPLED_INVALID_TOTAL")
    if not _is_strict_int(tested_count) or tested_count < 0 or tested_count > total_discovered:
        raise ValueError("SAMPLED_INVALID_TESTED")
    if not _is_strict_int(hits_found) or hits_found < 0 or hits_found > tested_count:
        raise ValueError("SAMPLED_INVALID_HITS")

    if hits_found > 0:
        verdict = "FAIL"
        passed = False
    elif tested_count < total_discovered:
        verdict = "NOT_SHOWN"
        passed = False
    else:
        verdict = "PASS"
        passed = True

    return {
        "verdict": verdict,
        "passed": passed,
        "tested_count": tested_count,
        "total_discovered": total_discovered,
        "hits_found": hits_found,
        "coverage_fraction": _fmt_q(Fraction(tested_count, total_discovered)),
    }


def certify_oracle_contract(spec: dict[str, Any]) -> dict[str, Any]:
    """aletheia#3 secs 5-7: exact arithmetic != exact oracle; anchor != replay; feedback rules."""
    if not isinstance(spec, dict) or frozenset(spec.keys()) != ORACLE_CONTRACT_KEYS:
        raise ValueError("ORACLE_CONTRACT_SCHEMA_MISMATCH")
    oracle_class = spec["oracle_class"]
    if not isinstance(oracle_class, str) or oracle_class not in EXPECTED_FEEDBACK_CHANNEL:
        raise ValueError("ORACLE_UNKNOWN_CLASS")
    basis = spec["evidence_basis"]
    if not _is_clean_ascii(basis):
        raise ValueError("ORACLE_INVALID_BASIS")
    feedback = spec["feedback_channel"]
    if not _is_clean_ascii(feedback):
        raise ValueError("ORACLE_INVALID_FEEDBACK")

    if oracle_class == "exact" and basis not in EXACT_ORACLE_BASES:
        raise ValueError("ORACLE_EXACT_REQUIRES_NON_SAMPLED_BASIS")
    if oracle_class == "sampled" and basis not in SAMPLED_ORACLE_BASES:
        raise ValueError("ORACLE_SAMPLED_INVALID_BASIS")
    if oracle_class == "anchor" and basis != "external_domain_data":
        raise ValueError("ORACLE_ANCHOR_REQUIRES_EXTERNAL_DATA")
    if oracle_class == "reference_replay" and basis != "untouched_upstream_replay":
        raise ValueError("ORACLE_REPLAY_REQUIRES_UPSTREAM")

    expected_fb = EXPECTED_FEEDBACK_CHANNEL[oracle_class]
    if feedback != expected_fb:
        raise ValueError("ORACLE_FEEDBACK_CHANNEL_MISMATCH")

    return {
        "valid": True,
        "oracle_class": oracle_class,
        "evidence_basis": basis,
        "feedback_channel": feedback,
        "failure_routes_to": "spec_owner" if oracle_class == "anchor" else "proposer_or_implementer",
    }


def _dot_q(u: list[Fraction], v: list[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(u, v)), Fraction(0, 1))


def _exact_pivot_columns_q(columns: list[list[Fraction]]) -> list[int]:
    """Return exact linearly independent pivot column indices over Q."""
    m = len(columns[0])
    r = len(columns)
    mat = [[columns[j][i] for j in range(r)] for i in range(m)]
    pivots: list[int] = []
    row = 0
    for col in range(r):
        pivot_row = None
        for i in range(row, m):
            if mat[i][col] != Fraction(0, 1):
                pivot_row = i
                break
        if pivot_row is None:
            continue
        mat[row], mat[pivot_row] = mat[pivot_row], mat[row]
        pv = mat[row][col]
        mat[row] = [x / pv for x in mat[row]]
        for i in range(m):
            if i != row and mat[i][col] != Fraction(0, 1):
                factor = mat[i][col]
                mat[i] = [mat[i][c] - factor * mat[row][c] for c in range(r)]
        pivots.append(col)
        row += 1
        if row == m:
            break
    return pivots


def _solve_linear_q(gram: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    """Solve invertible k x k rational system G c = rhs exactly over Q."""
    k = len(rhs)
    aug = [gram[i][:] + [rhs[i]] for i in range(k)]
    for col in range(k):
        pivot_row = col
        while pivot_row < k and aug[pivot_row][col] == Fraction(0, 1):
            pivot_row += 1
        if pivot_row == k:
            raise ValueError("LATCH_SINGULAR_GRAM")
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        pv = aug[col][col]
        aug[col] = [x / pv for x in aug[col]]
        for i in range(k):
            if i != col and aug[i][col] != Fraction(0, 1):
                factor = aug[i][col]
                aug[i] = [aug[i][c] - factor * aug[col][c] for c in range(k + 1)]
    return [aug[i][k] for i in range(k)]


def certify_gate8_subspace_latch(
    phi_columns: list[list[Any]],
    audit_vector: list[Any],
    residual_sq: Any,
    noise_var_s2: Any,
) -> dict[str, Any]:
    """aletheia#3 sec 8: exact pure-Q col(Phi) projection, sin^2(theta) & (m-rank)s^2 latch."""
    if not isinstance(phi_columns, list) or len(phi_columns) == 0:
        raise ValueError("LATCH_EMPTY_PHI")
    if not isinstance(phi_columns[0], list) or len(phi_columns[0]) == 0:
        raise ValueError("LATCH_EMPTY_PHI_COLUMN")
    m = len(phi_columns[0])
    cols_q: list[list[Fraction]] = []
    for col in phi_columns:
        if not isinstance(col, list) or len(col) != m:
            raise ValueError("LATCH_RAGGED_PHI")
        cols_q.append([_parse_exact_rational(x) for x in col])

    if not isinstance(audit_vector, list) or len(audit_vector) != m:
        raise ValueError("LATCH_AUDIT_VECTOR_DIM_MISMATCH")
    a_q = [_parse_exact_rational(x) for x in audit_vector]
    a_norm_sq = _dot_q(a_q, a_q)
    if a_norm_sq <= Fraction(0, 1):
        raise ValueError("LATCH_ZERO_AUDIT_VECTOR")

    res_q = _parse_exact_rational(residual_sq)
    if res_q < Fraction(0, 1):
        raise ValueError("LATCH_NEGATIVE_RESIDUAL")
    s2_q = _parse_exact_rational(noise_var_s2)
    if s2_q <= Fraction(0, 1):
        raise ValueError("LATCH_NONPOSITIVE_NOISE_VAR")

    pivot_idx = _exact_pivot_columns_q(cols_q)
    rank = len(pivot_idx)
    surviving_audits = m - rank

    if rank == 0:
        a_par = [Fraction(0, 1)] * m
    else:
        basis = [cols_q[j] for j in pivot_idx]
        gram = [[_dot_q(basis[i], basis[j]) for j in range(rank)] for i in range(rank)]
        rhs = [_dot_q(basis[i], a_q) for i in range(rank)]
        coeffs = _solve_linear_q(gram, rhs)
        a_par = [
            sum((coeffs[j] * basis[j][i] for j in range(rank)), Fraction(0, 1))
            for i in range(m)
        ]

    a_perp = [a_q[i] - a_par[i] for i in range(m)]
    par_norm_sq = _dot_q(a_par, a_par)
    perp_norm_sq = _dot_q(a_perp, a_perp)
    ortho_dot = _dot_q(a_par, a_perp)
    pythag_residual = a_norm_sq - (par_norm_sq + perp_norm_sq)

    sin2_theta = perp_norm_sq / a_norm_sq
    cos2_theta = par_norm_sq / a_norm_sq
    postfit_budget = Fraction(surviving_audits, 1) * s2_q

    if surviving_audits == 0:
        decision = "SATURATED_NO_SURVIVING_AUDITS"
        halt = True
    elif perp_norm_sq == Fraction(0, 1):
        decision = "BLIND_AUDIT_IN_COL_PHI"
        halt = True
    elif res_q > postfit_budget:
        decision = "LATCH_HALT"
        halt = True
    else:
        decision = "WITHIN_POSTFIT_BUDGET"
        halt = False

    return {
        "ambient_dim_m": m,
        "phi_rank": rank,
        "surviving_independent_audits": surviving_audits,
        "audit_norm_sq": _fmt_q(a_norm_sq),
        "parallel_norm_sq": _fmt_q(par_norm_sq),
        "orthogonal_norm_sq": _fmt_q(perp_norm_sq),
        "sin2_theta_attenuation": _fmt_q(sin2_theta),
        "cos2_theta_captured": _fmt_q(cos2_theta),
        "orthogonality_residual": _fmt_q(ortho_dot),
        "pythagorean_residual": _fmt_q(pythag_residual),
        "residual_sq": _fmt_q(res_q),
        "postfit_budget_m_minus_rank_s2": _fmt_q(postfit_budget),
        "decision": decision,
        "halt": halt,
    }


def run_oracle_and_latch_suite() -> dict[str, Any]:
    """Run canonical witnesses for aletheia#3 secs 4-8."""
    sampled_partial = evaluate_sampled_integrity(tested_count=1, total_discovered=4, hits_found=0)
    sampled_full = evaluate_sampled_integrity(tested_count=4, total_discovered=4, hits_found=0)
    sampled_hit = evaluate_sampled_integrity(tested_count=2, total_discovered=4, hits_found=1)

    valid_contracts = [
        certify_oracle_contract(
            {
                "oracle_class": "exact",
                "evidence_basis": "per_input_certificate",
                "feedback_channel": "full_counterexample_and_repair",
            }
        ),
        certify_oracle_contract(
            {
                "oracle_class": "sampled",
                "evidence_basis": "random_finite_sample_exact_arithmetic",
                "feedback_channel": "family_only_with_fresh_post_repair_seed",
            }
        ),
        certify_oracle_contract(
            {
                "oracle_class": "anchor",
                "evidence_basis": "external_domain_data",
                "feedback_channel": "none_to_proposer_spec_owner_only",
            }
        ),
        certify_oracle_contract(
            {
                "oracle_class": "reference_replay",
                "evidence_basis": "untouched_upstream_replay",
                "feedback_channel": "diff_against_upstream_reference",
            }
        ),
    ]

    # Exact-arithmetic random sample falsely tagged as "exact" MUST fail
    rejected_exact_arith_code = None
    try:
        certify_oracle_contract(
            {
                "oracle_class": "exact",
                "evidence_basis": "random_finite_sample_exact_arithmetic",
                "feedback_channel": "full_counterexample_and_repair",
            }
        )
    except ValueError as exc:
        rejected_exact_arith_code = str(exc)

    # Gate 8 Subspace Latch witnesses: m=4, rank(Phi)=2 -> surviving_audits=2
    phi = [["1", "0", "0", "0"], ["0", "1", "0", "0"], ["2", "3", "0", "0"]]
    latch_oblique_halt = certify_gate8_subspace_latch(phi, ["1", "0", "2", "0"], "5", "2")
    latch_budget_boundary = certify_gate8_subspace_latch(phi, ["0", "0", "1", "0"], "4", "2")
    latch_in_col_blind = certify_gate8_subspace_latch(phi, ["3", "4", "0", "0"], "1", "2")
    latch_saturated = certify_gate8_subspace_latch(
        [["1", "0"], ["0", "1"]],
        ["1", "1"],
        "0",
        "1",
    )

    return {
        "sampled_integrity": {
            "partial_1_of_4_zero_hits": sampled_partial,
            "full_4_of_4_zero_hits": sampled_full,
            "hit_1_of_2": sampled_hit,
        },
        "oracle_contracts": {
            "valid_four_classes": valid_contracts,
            "exact_arithmetic_random_sample_rejected_code": rejected_exact_arith_code,
        },
        "gate8_subspace_latch": {
            "oblique_sin2_4_over_5_halt": latch_oblique_halt,
            "orthogonal_exact_boundary_pass": latch_budget_boundary,
            "in_col_phi_sin2_zero_blind": latch_in_col_blind,
            "saturated_rank_equals_m_halt": latch_saturated,
        },
    }


# ---------------------------------------------------------------------------
# Component 4: Read-Only Round-10 Portal Verifier & v1.5.0/v2.0 Matrix
# ---------------------------------------------------------------------------


def _resolve_git_ref_sha40(repo_root: Path, ref_name: str) -> str:
    """Safely resolve a git ref inside repo_root/.git with strict containment."""
    if not _is_clean_ascii(ref_name) or not ref_name.startswith("refs/"):
        raise ValueError("GIT_REF_INVALID_PREFIX")
    if ".." in ref_name or "\\" in ref_name or "//" in ref_name:
        raise ValueError("GIT_REF_PATH_TRAVERSAL")
    git_dir = (repo_root / ".git").resolve()
    if not git_dir.is_dir():
        raise ValueError("GIT_DIR_MISSING")

    loose_candidate = git_dir / ref_name
    if loose_candidate.is_file():
        resolved = loose_candidate.resolve()
        try:
            resolved.relative_to(git_dir)
        except ValueError as exc:
            raise ValueError("GIT_REF_SYMLINK_ESCAPE") from exc
        sha = resolved.read_text(encoding="utf-8").strip()
        if not _is_lower_hex(sha, 40):
            raise ValueError("GIT_LOOSE_REF_INVALID_SHA")
        return sha

    packed_path = git_dir / "packed-refs"
    if packed_path.is_file():
        resolved_packed = packed_path.resolve()
        try:
            resolved_packed.relative_to(git_dir)
        except ValueError as exc:
            raise ValueError("GIT_PACKED_REFS_SYMLINK_ESCAPE") from exc
        for raw_line in resolved_packed.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("^"):
                continue
            parts = line.split(" ", 1)
            if len(parts) == 2 and parts[1] == ref_name:
                if not _is_lower_hex(parts[0], 40):
                    raise ValueError("GIT_PACKED_REF_INVALID_SHA")
                return parts[0]

    raise ValueError(f"GIT_REF_NOT_FOUND:{ref_name}")


def inspect_round10_aletheia_portals(round10_root: Path) -> dict[str, Any]:
    """Read-only verification of Round-10 aletheia portals and repos/aletheia-live."""
    repo_root = round10_root / "repos" / "aletheia-live"
    portals_root = round10_root / "portals" / "aletheia"

    verified_refs: dict[str, str] = {}
    for ref_name, expected_sha in PINNED_ALETHEIA_LIVE_REFS.items():
        actual_sha = _resolve_git_ref_sha40(repo_root, ref_name)
        if actual_sha != expected_sha:
            raise ValueError(f"ALETHEIA_LIVE_REF_MISMATCH:{ref_name}")
        verified_refs[ref_name] = actual_sha

    verified_files: dict[str, dict[str, Any]] = {}
    for rel_path, expected_sha in PINNED_PORTAL_SHA256.items():
        fpath = portals_root / rel_path
        if not fpath.is_file():
            raise ValueError(f"PORTAL_FILE_MISSING:{rel_path}")
        raw = fpath.read_bytes()
        actual_sha = hashlib.sha256(raw).hexdigest()
        if actual_sha != expected_sha:
            raise ValueError(f"PORTAL_SHA256_MISMATCH:{rel_path}")
        text = raw.decode("utf-8")
        anchors = PORTAL_VERBATIM_ANCHORS.get(rel_path, ())
        for snippet in anchors:
            if snippet not in text:
                raise ValueError(f"PORTAL_ANCHOR_MISSING:{rel_path}")
        verified_files[rel_path] = {
            "sha256": actual_sha,
            "byte_len": len(raw),
            "anchors_verified": len(anchors),
        }

    return {
        "mode": "live_readonly",
        "aletheia_live_refs": verified_refs,
        "portal_files": verified_files,
        "pr8_stale_table_sha_confirmed": True,
        "pr8_body_row11_sha": "cc8c3b8",
        "pr8_live_head_sha": verified_refs["refs/remotes/origin/pr/8"],
    }


def build_v15_v20_integration_matrix() -> dict[str, Any]:
    """Structured v1.5.0 / v2.0 roadmap matrix folding in #2/#3/#4/#5/#7/#8/#9 + CYA-GAP-01..06."""
    issue5_items = [
        {"id": "I5-01", "topic": "mutator_named_guards_and_coverage", "at_58207b4": "OPEN_1_OF_1_100PCT", "at_aa471867": "PARTIAL_LOCAL_WRAPPER_FIXED_5_MUTANTS_40PCT", "at_aa920b1a": "PARTIAL_IMPORTED_AND_GUARDS_OPEN", "target_release": "v1.5.0"},
        {"id": "I5-02", "topic": "r4_unittest_skip_under_O", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
        {"id": "I5-03", "topic": "schemas_unused_and_disagree", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
        {"id": "I5-04", "topic": "handoff_schema_rejects_live_manifest", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
        {"id": "I5-05", "topic": "schema_regex_dollar_matches_trailing_newline", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
        {"id": "I5-06", "topic": "mutator_forced_I_missing_add_cwd_hint", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
        {"id": "I5-07", "topic": "mutator_baseline_timeout_unhandled_traceback", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
        {"id": "I5-08", "topic": "diagnose_only_reads_cartography_subdir", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
        {"id": "I5-09", "topic": "seeded_module_rng_wording_and_count", "at_58207b4": "OPEN_COUNT_2", "at_aa471867": "PARTIAL_PR7_B3_COUNT_1", "at_aa920b1a": "PARTIAL_PR7_B3_COUNT_1", "target_release": "v1.5.0"},
        {"id": "I5-10", "topic": "claude_code_plugin_json_broken_paths", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
        {"id": "I5-11", "topic": "mutator_refusal_shapes_string_tuple_multistmt", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
        {"id": "I5-12", "topic": "selfcheck_script_50pct_structural_ceiling", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
        {"id": "I5-13", "topic": "from_random_import_missed_by_strict_unseeded", "at_58207b4": "OPEN", "at_aa471867": "OPEN", "at_aa920b1a": "OPEN", "target_release": "v1.5.0"},
    ]

    issue3_clauses = [
        {"id": "I3-01", "clause": "R6_pinned_checks_and_R7_measured_not_declared", "target_release": "v1.5.0", "oracle_status": "PROTOTYPED_IN_AUDIT_086"},
        {"id": "I3-02", "clause": "two_direction_R3_reject_stays_reject", "target_release": "v1.5.0", "oracle_status": "PROTOTYPED_IN_AUDIT_086"},
        {"id": "I3-03", "clause": "R4_write_path_cross_language_and_3_mode_doc_sync", "target_release": "v1.5.0", "oracle_status": "DOC_SYNC_IN_PR8_WRITE_PATH_OPEN"},
        {"id": "I3-04", "clause": "sampled_gate_integrity_is_NOT_SHOWN", "target_release": "v1.5.0", "oracle_status": "PROTOTYPED_IN_AUDIT_086"},
        {"id": "I3-05", "clause": "exact_arithmetic_not_exact_oracle", "target_release": "v1.5.0", "oracle_status": "PROTOTYPED_IN_AUDIT_086"},
        {"id": "I3-06", "clause": "anchor_vs_reference_replay_split", "target_release": "v1.5.0", "oracle_status": "PROTOTYPED_IN_AUDIT_086"},
        {"id": "I3-07", "clause": "oracle_class_dependent_feedback_channels", "target_release": "v1.5.0", "oracle_status": "PROTOTYPED_IN_AUDIT_086"},
        {"id": "I3-08", "clause": "gate8_full_subspace_latch_and_preregistration", "target_release": "v2.0", "oracle_status": "PROTOTYPED_IN_AUDIT_086"},
        {"id": "I3-09", "clause": "theory_prior_work_falsification_and_confound_note", "target_release": "v1.5.0", "oracle_status": "SPEC_UPDATE_PENDING"},
        {"id": "I3-10", "clause": "contributing_governance_and_outside_evidence_dir", "target_release": "v1.5.0", "oracle_status": "SPEC_UPDATE_PENDING"},
    ]

    cya_gaps = [
        {"id": "CYA-GAP-01", "scanner": "hidden_trojan_source_unicode", "source_audit": "AUDIT-078R", "target_release": "v1.5.0"},
        {"id": "CYA-GAP-02", "scanner": "unpinned_mcp_and_permission_bypass", "source_audit": "AUDIT-078R", "target_release": "v1.5.0"},
        {"id": "CYA-GAP-03", "scanner": "unguarded_recursive_delete_nounset", "source_audit": "AUDIT-078R", "target_release": "v1.5.0"},
        {"id": "CYA-GAP-04", "scanner": "untrusted_ci_pull_request_target_privs", "source_audit": "AUDIT-078R", "target_release": "v1.5.0"},
        {"id": "CYA-GAP-05", "scanner": "prose_only_governance_and_host_tilde", "source_audit": "AUDIT-078R", "target_release": "v1.5.0"},
        {"id": "CYA-GAP-06", "scanner": "shell_alias_illusion_and_cloud_sync_stubs", "source_audit": "AUDIT-078R", "target_release": "v2.0"},
    ]

    companion_sources = [
        {"ref": "aletheia#2", "scope": "prior_work_by_mechanism_CS12_and_advocate_pass_CS13", "target_release": "v1.5.0"},
        {"ref": "aletheia#4", "scope": "17_sentence_corrections_and_CS08_compute_leakage_rename", "target_release": "v1.5.0"},
        {"ref": "aletheia#7", "scope": "6_review_blocker_fixes_merged_at_aa471867", "target_release": "MERGED_IN_PR1"},
        {"ref": "aletheia#8", "scope": "11_followup_fixes_verified_plus_9_left_for_author_at_aa920b1a", "target_release": "READY_TO_MERGE_AFTER_TABLE_SHA_FIX"},
        {"ref": "aletheia#9", "scope": "OWN_TERMS_FIRST_mechanism_first_reading_proposal", "target_release": "v1.5.0"},
    ]

    return {
        "issue5_reproducers": issue5_items,
        "issue3_gate_contracts": issue3_clauses,
        "jdpru_cya_gaps": cya_gaps,
        "companion_sources": companion_sources,
        "counts": {
            "issue5_total": len(issue5_items),
            "issue5_partially_addressed": sum(1 for x in issue5_items if x["at_aa920b1a"].startswith("PARTIAL")),
            "issue5_fully_open": sum(1 for x in issue5_items if x["at_aa920b1a"] == "OPEN"),
            "pr7_verified_commits": 6,
            "pr8_verified_commits": 11,
            "pr8_left_for_author": 9,
            "issue3_total_clauses": len(issue3_clauses),
            "cya_gap_total": len(cya_gaps),
            "companion_sources_total": len(companion_sources),
        },
    }


def run_full_audit(standalone: bool = False, round10_root: Path | None = None) -> dict[str, Any]:
    """Execute complete AUDIT-086 R6/R7, Two-Direction R3, Oracle/Latch & Portal Audit."""
    portal_section: dict[str, Any]
    if standalone:
        portal_section = {"mode": "standalone_self_contained"}
    else:
        root = round10_root if round10_root is not None else Path(__file__).resolve().parent.parent
        portal_section = inspect_round10_aletheia_portals(root)

    payload = {
        "schema": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "novelty_tier": "N1",
        "oracle_class": "exact",
        "zero_float_enforced": True,
        "external_writes": 0,
        "r6_r7_record_b_witnesses": run_record_b_witnesses(),
        "two_direction_r3_note_d": run_r3_note_d_witness(),
        "oracle_class_and_gate8_latch": run_oracle_and_latch_suite(),
        "portal_verification": portal_section,
        "v15_v20_integration_matrix": build_v15_v20_integration_matrix(),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["certificate_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def _render_canonical_json(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    standalone = False
    as_json = False
    write_cert_path: Path | None = None

    idx = 0
    while idx < len(args):
        tok = args[idx]
        if tok == "--standalone":
            standalone = True
        elif tok == "--json":
            as_json = True
        elif tok == "--write-cert":
            if idx + 1 >= len(args):
                raise ValueError("CLI_MISSING_WRITE_CERT_PATH")
            write_cert_path = Path(args[idx + 1])
            idx += 1
        else:
            raise ValueError(f"CLI_UNKNOWN_ARG:{tok}")
        idx += 1

    result = run_full_audit(standalone=standalone)
    rendered = _render_canonical_json(result)

    if write_cert_path is not None:
        write_cert_path.write_text(rendered, encoding="utf-8", newline="\n")

    if as_json:
        sys.stdout.write(rendered)
    else:
        counts = result["v15_v20_integration_matrix"]["counts"]
        sys.stdout.write(
            f"[{AUDIT_ID}] PASS mode={result['portal_verification']['mode']} "
            f"r6r7_caught={len(result['r6_r7_record_b_witnesses']['negative_witnesses_caught'])} "
            f"r3_hardened={result['two_direction_r3_note_d']['hardened_gate']['passed']} "
            f"note_d_exposed={result['two_direction_r3_note_d']['note_d_dir2_flip_exposed']} "
            f"issue5_items={counts['issue5_total']} "
            f"sha256={result['certificate_sha256']}\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
