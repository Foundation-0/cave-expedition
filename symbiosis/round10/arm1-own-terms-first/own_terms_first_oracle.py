"""Pure-stdlib, zero-float exact rational oracle for AUDIT-084 (OWN_TERMS_FIRST).

Audits Foundation-0/aletheia#9 (OWN_TERMS_FIRST.md), Foundation-0/continuum#1
(continuum.md), and Foundation-0/cave-expedition#7 (symbology-and-raw-data-map)
in exact rational arithmetic (Q) across four operational pillars:
  1. Phase-1 Net-Invariance, Stratified Null (Tier 4A IID + Tier 4B Spectrum),
     Negative Control, R6/R7 Pre-Pinned Input/Threshold, & Exact FWER Budget Gate
     (Rules 3, 4, 5, 6 + OTF-TIGHT-01, OTF-TIGHT-03).
  2. Exact Pure-Q Orthogonal Model-Ladder Continuum-Remainder Identifiability
     Oracle proving finite-class model misspecification vs. ladder-surviving
     structured remainder (OWN_TERMS_FIRST.md:34-39 + OTF-TIGHT-02).
  3. Exact Rule-2 Symbol-Utility & Renaming Classifier applied honestly to our
     own 8 Aletheia glyphs (OP-01..OP-08, GLYPHS.md + OTF-TIGHT-04).
  4. Phase-1 / Phase-2 Orthogonality & Anti-Novelty-Inflation Composer uniting
     OWN_TERMS_FIRST with Aletheia Laws 1-5 and R6/R7 (OTF-TIGHT-05).

Strict Aletheia v1.4.0 invariants: zero floats, zero bare asserts, deterministic JSON.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import re
from typing import Any


_STRICT_NUMBER_RE = re.compile(r"\A[+-]?(?:\d+(?:\.\d+)?|\d+/\d+)\Z")
_REQUIRED_NET_AXES = frozenset({"sampling_rate", "quantisation", "amplitude_scale", "window", "instrument"})
_VALID_PHASE1_VERDICTS = frozenset(
    {
        "P1_VERIFIED_INVARIANT",
        "P1_STRUCTURED_REMAINDER",
        "P1_FAILED_NET_INVARIANCE",
        "P1_FAILED_NULL_OR_CONTROL",
        "P1_UNMEASURABLE_RETURNED",
    }
)
_VALID_PHASE2_STATUSES = frozenset(
    {
        "N0_KNOWN_BY_MECHANISM",
        "N1_NEW_BRIDGE_OR_SYNTHESIS",
        "N2_GENUINELY_NOVEL",
        "DOES_NOT_TRANSLATE",
        "PENDING_PHASE2",
    }
)


class OtfOracleError(ValueError):
    """Fail-closed validation or invariant refusal with machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code


def verify_no_floats(obj: Any, path: str = "root") -> None:
    """Recursively refuse any float in keys or values."""
    if isinstance(obj, float):
        raise OtfOracleError("FLOAT_FORBIDDEN", f"float forbidden at {path}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            verify_no_floats(k, f"{path}.<key>")
            verify_no_floats(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple, set)):
        for idx, item in enumerate(obj):
            verify_no_floats(item, f"{path}[{idx}]")


def require_non_empty_str(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise OtfOracleError("TYPE_ERROR", f"{field} must be str")
    stripped = value.strip()
    if not stripped:
        raise OtfOracleError("EMPTY_STRING", f"{field} must be non-empty")
    if any(ord(ch) < 32 or ord(ch) > 126 for ch in stripped):
        raise OtfOracleError("INVALID_CHAR", f"{field} must contain printable ASCII only")
    return stripped


def require_exact_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise OtfOracleError("TYPE_ERROR", f"{field} must be bool")
    return value


def require_exact_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise OtfOracleError("TYPE_ERROR", f"{field} must be exact int")
    return value


def require_exact_fraction(value: Any, field: str) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise OtfOracleError("TYPE_ERROR", f"{field} cannot be bool")
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        raise OtfOracleError("FLOAT_FORBIDDEN", f"{field} cannot be float")
    if isinstance(value, str):
        if _STRICT_NUMBER_RE.match(value) is None:
            raise OtfOracleError("INVALID_RATIONAL", f"{field} has invalid numeric format: {value!r}")
        try:
            return Fraction(value)
        except ZeroDivisionError as exc:
            raise OtfOracleError("ZERO_DENOMINATOR", f"{field} has zero denominator") from exc
    raise OtfOracleError("TYPE_ERROR", f"{field} must be Fraction, int, or numeric str")


def require_list_or_tuple(value: Any, field: str) -> tuple[Any, ...]:
    if not isinstance(value, (list, tuple)):
        raise OtfOracleError("TYPE_ERROR", f"{field} must be list or tuple")
    if len(value) == 0:
        raise OtfOracleError("EMPTY_SEQUENCE", f"{field} must be non-empty")
    return tuple(value)


def frac_str(val: Fraction) -> str:
    if not isinstance(val, Fraction):
        raise OtfOracleError("TYPE_ERROR", "frac_str requires Fraction")
    return f"{val.numerator}/{val.denominator}"


def format_exact_decimal(val: Fraction, places: int) -> str:
    if not isinstance(val, Fraction):
        raise OtfOracleError("TYPE_ERROR", "val must be Fraction")
    places_i = require_exact_int(places, "places")
    if places_i < 0:
        raise OtfOracleError("INVALID_RANGE", "places must be >= 0")
    neg = val < 0
    mag = -val if neg else val
    scale = 10 ** places_i
    quot, rem = divmod(mag.numerator * scale, mag.denominator)
    if 2 * rem >= mag.denominator:
        quot += 1
    sign = "-" if neg and quot > 0 else ""
    if places_i == 0:
        return f"{sign}{quot}"
    int_part, frac_part = divmod(quot, scale)
    return f"{sign}{int_part}.{frac_part:0{places_i}d}"


def canonical_json_bytes(obj: Any) -> bytes:
    verify_no_floats(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


# ---------------------------------------------------------------------------
# Pillar 1: Phase-1 Net-Invariance, Stratified Null, Control & FWER Gate
# ---------------------------------------------------------------------------


def audit_phase1_net_invariance_gate(
    net_measurements: Any,
    pinned_spec: Any,
) -> dict[str, Any]:
    """Certify a Phase-1 pattern on its own terms under Rules 3-6 + R6/R7 + OTF-TIGHT-01/03."""
    verify_no_floats(net_measurements, "net_measurements")
    verify_no_floats(pinned_spec, "pinned_spec")
    spec_keys = {
        "min_signal_margin",
        "max_net_spread",
        "max_control_score",
        "fwer_alpha",
        "per_test_alpha",
        "unseen_data_verified",
        "input_sha256_pinned",
        "measurable_definition_present",
    }
    if not isinstance(pinned_spec, dict) or set(pinned_spec.keys()) != spec_keys:
        raise OtfOracleError("SCHEMA_ERROR", "pinned_spec has invalid keys")

    min_margin = require_exact_fraction(pinned_spec["min_signal_margin"], "min_signal_margin")
    if min_margin <= 0:
        raise OtfOracleError("INVALID_RANGE", "min_signal_margin must be > 0")
    max_spread = require_exact_fraction(pinned_spec["max_net_spread"], "max_net_spread")
    if max_spread < 0:
        raise OtfOracleError("INVALID_RANGE", "max_net_spread must be >= 0")
    max_ctrl = require_exact_fraction(pinned_spec["max_control_score"], "max_control_score")
    if max_ctrl < 0:
        raise OtfOracleError("INVALID_RANGE", "max_control_score must be >= 0")
    fwer_alpha = require_exact_fraction(pinned_spec["fwer_alpha"], "fwer_alpha")
    if fwer_alpha <= 0 or fwer_alpha >= 1:
        raise OtfOracleError("INVALID_RANGE", "fwer_alpha must be in (0, 1)")
    per_alpha = require_exact_fraction(pinned_spec["per_test_alpha"], "per_test_alpha")
    if per_alpha <= 0 or per_alpha >= 1:
        raise OtfOracleError("INVALID_RANGE", "per_test_alpha must be in (0, 1)")
    unseen_ok = require_exact_bool(pinned_spec["unseen_data_verified"], "unseen_data_verified")
    input_pinned = require_exact_bool(pinned_spec["input_sha256_pinned"], "input_sha256_pinned")
    measurable_ok = require_exact_bool(pinned_spec["measurable_definition_present"], "measurable_definition_present")

    # Rule 6 (OWN_TERMS_FIRST.md:26): unmeasurable claims are returned to authors without strawmanning.
    if not measurable_ok:
        return {
            "phase1_verdict": "P1_UNMEASURABLE_RETURNED",
            "violation_count": 1,
            "violation_codes": ["RULE6_NEEDS_MEASURABLE_DEFINITION"],
            "net_count": 0,
            "missing_axes": sorted(_REQUIRED_NET_AXES),
            "independent_fwer": "0/1",
            "independent_fwer_pct": "0.00",
            "bonferroni_upper": "0/1",
            "bonferroni_upper_pct": "0.00",
        }

    items = require_list_or_tuple(net_measurements, "net_measurements")
    item_keys = {"axis", "net_id", "obs_score", "iid_null_score", "spec_null_score", "control_score"}
    seen_ids: set[str] = set()
    axes_seen: set[str] = set()
    obs_scores: list[Fraction] = []
    iid_margins: list[Fraction] = []
    spec_margins: list[Fraction] = []
    ctrl_scores: list[Fraction] = []
    ctrl_margins: list[Fraction] = []

    for idx, entry in enumerate(items):
        if not isinstance(entry, dict) or set(entry.keys()) != item_keys:
            raise OtfOracleError("SCHEMA_ERROR", f"net_measurements[{idx}] has invalid keys")
        axis = require_non_empty_str(entry["axis"], f"net_measurements[{idx}].axis").lower()
        if axis not in _REQUIRED_NET_AXES:
            raise OtfOracleError("INVALID_AXIS", f"unknown net axis: {axis!r}")
        nid = require_non_empty_str(entry["net_id"], f"net_measurements[{idx}].net_id")
        nid_key = nid.lower()
        if nid_key in seen_ids:
            raise OtfOracleError("DUPLICATE_ID", f"duplicate net_id: {nid}")
        seen_ids.add(nid_key)
        axes_seen.add(axis)

        obs = require_exact_fraction(entry["obs_score"], f"net_measurements[{idx}].obs_score")
        iid_n = require_exact_fraction(entry["iid_null_score"], f"net_measurements[{idx}].iid_null_score")
        spec_n = require_exact_fraction(entry["spec_null_score"], f"net_measurements[{idx}].spec_null_score")
        ctrl = require_exact_fraction(entry["control_score"], f"net_measurements[{idx}].control_score")
        obs_scores.append(obs)
        iid_margins.append(obs - abs(iid_n))
        spec_margins.append(obs - abs(spec_n))
        ctrl_scores.append(ctrl)
        ctrl_margins.append(obs - abs(ctrl))

    m_tests = len(items)
    exact_fwer = Fraction(1, 1) - ((Fraction(1, 1) - per_alpha) ** m_tests)
    bonf_raw = per_alpha * m_tests
    bonf_upper = bonf_raw if bonf_raw < Fraction(1, 1) else Fraction(1, 1)

    obs_spread = max(obs_scores) - min(obs_scores)
    min_iid_m = min(iid_margins)
    min_spec_m = min(spec_margins)
    max_ctrl_obs = max(abs(c) for c in ctrl_scores)
    min_ctrl_m = min(ctrl_margins)
    missing_axes = sorted(_REQUIRED_NET_AXES - axes_seen)

    violations: list[str] = []
    if not input_pinned:
        violations.append("R7_UNPINNED_RAW_INPUT")
    if not unseen_ok:
        violations.append("RULE4_NO_UNSEEN_DATA")
    if len(missing_axes) > 0:
        violations.append("RULE3_INCOMPLETE_NET_AXES")
    if bonf_upper > fwer_alpha:
        violations.append("OTF_TIGHT01_FWER_EXCEEDED")
    if obs_spread > max_spread:
        violations.append("RULE3_NET_INVARIANCE_FAILED")
    if min_iid_m < min_margin:
        violations.append("RULE4A_IID_NULL_FAILED")
    if min_spec_m < min_margin:
        violations.append("RULE4B_RED_NOISE_SPECTRUM_NULL_FAILED")
    if max_ctrl_obs > max_ctrl or min_ctrl_m < min_margin:
        violations.append("RULE5_NEGATIVE_CONTROL_CONTAMINATED")

    if len(violations) == 0:
        verdict = "P1_VERIFIED_INVARIANT"
    elif any(v in {"RULE4A_IID_NULL_FAILED", "RULE4B_RED_NOISE_SPECTRUM_NULL_FAILED", "RULE5_NEGATIVE_CONTROL_CONTAMINATED", "RULE4_NO_UNSEEN_DATA"} for v in violations):
        verdict = "P1_FAILED_NULL_OR_CONTROL"
    else:
        verdict = "P1_FAILED_NET_INVARIANCE"

    return {
        "phase1_verdict": verdict,
        "violation_count": len(violations),
        "violation_codes": violations,
        "net_count": m_tests,
        "missing_axes": missing_axes,
        "obs_spread": frac_str(obs_spread),
        "min_iid_margin": frac_str(min_iid_m),
        "min_spec_margin": frac_str(min_spec_m),
        "min_control_margin": frac_str(min_ctrl_m),
        "max_abs_control_observed": frac_str(max_ctrl_obs),
        "independent_fwer": frac_str(exact_fwer),
        "independent_fwer_pct": format_exact_decimal(exact_fwer * 100, 2),
        "bonferroni_upper": frac_str(bonf_upper),
        "bonferroni_upper_pct": format_exact_decimal(bonf_upper * 100, 2),
    }


# ---------------------------------------------------------------------------
# Pillar 2: Orthogonal Model-Ladder Continuum-Remainder Identifiability
# ---------------------------------------------------------------------------


def _dot_q(a: tuple[Fraction, ...], b: tuple[Fraction, ...]) -> Fraction:
    return sum((x * y for x, y in zip(a, b)), Fraction(0, 1))


def audit_continuum_remainder_ladder_exact(
    train_signal: Any,
    unseen_signal: Any,
    basis_vectors: Any,
    scrambled_null_corr_sq: Any,
    min_unseen_corr_sq: Any,
    min_remainder_energy_ratio: Any,
) -> dict[str, Any]:
    """Distinguish finite-class model misspecification from a ladder-surviving structured remainder."""
    t_raw = require_list_or_tuple(train_signal, "train_signal")
    u_raw = require_list_or_tuple(unseen_signal, "unseen_signal")
    if len(t_raw) < 2 or len(t_raw) != len(u_raw):
        raise OtfOracleError("INVALID_LENGTH", "train_signal and unseen_signal must have equal length >= 2")
    n_len = len(t_raw)
    y_train = tuple(require_exact_fraction(v, f"train_signal[{i}]") for i, v in enumerate(t_raw))
    y_unseen = tuple(require_exact_fraction(v, f"unseen_signal[{i}]") for i, v in enumerate(u_raw))

    e_train = _dot_q(y_train, y_train)
    e_unseen = _dot_q(y_unseen, y_unseen)
    if e_train == 0 or e_unseen == 0:
        raise OtfOracleError("ZERO_ENERGY", "train_signal and unseen_signal must have nonzero energy")

    b_raw = require_list_or_tuple(basis_vectors, "basis_vectors")
    if len(b_raw) < 2:
        raise OtfOracleError("INVALID_LENGTH", "model ladder requires at least 2 escalating rungs")
    null_raw = require_list_or_tuple(scrambled_null_corr_sq, "scrambled_null_corr_sq")
    if len(b_raw) != len(null_raw):
        raise OtfOracleError("LENGTH_MISMATCH", "basis_vectors and scrambled_null_corr_sq must have equal length")

    min_corr = require_exact_fraction(min_unseen_corr_sq, "min_unseen_corr_sq")
    if min_corr <= 0 or min_corr > 1:
        raise OtfOracleError("INVALID_RANGE", "min_unseen_corr_sq must be in (0, 1]")
    min_eratio = require_exact_fraction(min_remainder_energy_ratio, "min_remainder_energy_ratio")
    if min_eratio <= 0 or min_eratio >= 1:
        raise OtfOracleError("INVALID_RANGE", "min_remainder_energy_ratio must be in (0, 1)")

    basis: list[tuple[Fraction, ...]] = []
    null_corrs: list[Fraction] = []
    for k, (bv_raw, nc_raw) in enumerate(zip(b_raw, null_raw)):
        bv_seq = require_list_or_tuple(bv_raw, f"basis_vectors[{k}]")
        if len(bv_seq) != n_len:
            raise OtfOracleError("INVALID_LENGTH", f"basis_vectors[{k}] length != {n_len}")
        bv = tuple(require_exact_fraction(x, f"basis_vectors[{k}][{j}]") for j, x in enumerate(bv_seq))
        if _dot_q(bv, bv) == 0:
            raise OtfOracleError("ZERO_BASIS_VECTOR", f"basis_vectors[{k}] cannot be zero")
        for prev in basis:
            if _dot_q(prev, bv) != 0:
                raise OtfOracleError("NON_ORTHOGONAL_BASIS", "basis_vectors must be pairwise orthogonal")
        nc = require_exact_fraction(nc_raw, f"scrambled_null_corr_sq[{k}]")
        if nc < 0 or nc > 1:
            raise OtfOracleError("INVALID_RANGE", f"scrambled_null_corr_sq[{k}] must be in [0, 1]")
        basis.append(bv)
        null_corrs.append(nc)

    # Incremental orthogonal projections onto M_k^perp separately for y_train and y_unseen
    # so in-model shifts P_{M_k}(y_unseen - y_train) cannot contaminate out-of-model residuals.
    y_hat_tr = [Fraction(0, 1)] * n_len
    y_hat_un = [Fraction(0, 1)] * n_len
    rungs: list[dict[str, Any]] = []
    for idx, (bv, nc) in enumerate(zip(basis, null_corrs), start=1):
        bv_norm_sq = _dot_q(bv, bv)
        coeff_tr = _dot_q(y_train, bv) / bv_norm_sq
        coeff_un = _dot_q(y_unseen, bv) / bv_norm_sq
        for j in range(n_len):
            y_hat_tr[j] += coeff_tr * bv[j]
            y_hat_un[j] += coeff_un * bv[j]
        r_tr = tuple(y_train[j] - y_hat_tr[j] for j in range(n_len))
        r_un = tuple(y_unseen[j] - y_hat_un[j] for j in range(n_len))
        e_r_tr = _dot_q(r_tr, r_tr)
        e_r_un = _dot_q(r_un, r_un)
        e_ratio_tr = e_r_tr / e_train
        e_ratio_un = e_r_un / e_unseen
        if e_r_tr == 0 or e_r_un == 0:
            cross = Fraction(0, 1)
            corr_sq = Fraction(0, 1)
        else:
            cross = _dot_q(r_tr, r_un)
            corr_sq = (cross * cross) / (e_r_tr * e_r_un)
        pos_aligned = cross > 0
        structured = (
            (e_ratio_tr >= min_eratio)
            and (e_ratio_un >= min_eratio)
            and pos_aligned
            and (corr_sq >= min_corr)
            and (corr_sq > nc)
        )
        rungs.append(
            {
                "rung_k": idx,
                "train_coeff": frac_str(coeff_tr),
                "unseen_coeff": frac_str(coeff_un),
                "train_residual_energy_ratio": frac_str(e_ratio_tr),
                "unseen_residual_energy_ratio": frac_str(e_ratio_un),
                "unseen_positive_alignment": pos_aligned,
                "unseen_residual_corr_sq": frac_str(corr_sq),
                "scrambled_null_corr_sq": frac_str(nc),
                "structured_at_rung": structured,
            }
        )

    any_earlier_structured = any(r["structured_at_rung"] for r in rungs[:-1])
    final_structured = rungs[-1]["structured_at_rung"]
    if final_structured:
        classification = "STRUCTURED_REMAINDER_SURVIVING_LADDER"
    elif any_earlier_structured:
        classification = "FINITE_MODEL_MISSPECIFICATION"
    else:
        classification = "NO_STRUCTURED_REMAINDER"

    return {
        "signal_length": n_len,
        "ladder_depth": len(rungs),
        "train_energy": frac_str(e_train),
        "classification": classification,
        "single_model_test_confounded": any_earlier_structured and not final_structured,
        "rungs": rungs,
    }


# ---------------------------------------------------------------------------
# Pillar 3: Rule-2 Symbol-Utility & Renaming Classifier (GLYPHS.md)
# ---------------------------------------------------------------------------


def audit_symbol_utility_rule2(symbols: Any) -> dict[str, Any]:
    """Classify symbols strictly by operational use vs. renaming (OWN_TERMS_FIRST Rule 2)."""
    items = require_list_or_tuple(symbols, "symbols")
    expected_keys = {
        "symbol",
        "op_id",
        "reproducible_from_rules",
        "unseen_physical_prediction",
        "adds_rule_beyond_standard",
        "overloads_distinct_constructs",
    }
    seen_ops: set[str] = set()
    seen_syms: set[str] = set()
    counts = {
        "OPERATIONAL_NEW_PRIMITIVE": 0,
        "TYPED_ENGINEERING_OPERATOR": 0,
        "COMPOSITION_SHORTHAND_RENAMING": 0,
        "OVERLOADED_RENAMING": 0,
        "NON_REPRODUCIBLE_SYMBOL": 0,
    }
    records: list[dict[str, Any]] = []

    for idx, entry in enumerate(items):
        if not isinstance(entry, dict) or set(entry.keys()) != expected_keys:
            raise OtfOracleError("SCHEMA_ERROR", f"symbols[{idx}] has invalid keys")
        sym = require_non_empty_str(entry["symbol"], f"symbols[{idx}].symbol")
        op_id = require_non_empty_str(entry["op_id"], f"symbols[{idx}].op_id")
        op_key = op_id.lower()
        if op_key in seen_ops:
            raise OtfOracleError("DUPLICATE_ID", f"duplicate op_id: {op_id}")
        seen_ops.add(op_key)
        sym_key = sym.lower()
        if sym_key in seen_syms:
            raise OtfOracleError("DUPLICATE_SYMBOL", f"duplicate symbol collision: {sym}")
        seen_syms.add(sym_key)
        repro = require_exact_bool(entry["reproducible_from_rules"], f"symbols[{idx}].reproducible_from_rules")
        pred = require_exact_bool(entry["unseen_physical_prediction"], f"symbols[{idx}].unseen_physical_prediction")
        adds = require_exact_bool(entry["adds_rule_beyond_standard"], f"symbols[{idx}].adds_rule_beyond_standard")
        overload = require_exact_bool(entry["overloads_distinct_constructs"], f"symbols[{idx}].overloads_distinct_constructs")

        if not repro:
            cls = "NON_REPRODUCIBLE_SYMBOL"
        elif overload:
            cls = "OVERLOADED_RENAMING"
        elif adds and pred:
            cls = "OPERATIONAL_NEW_PRIMITIVE"
        elif adds:
            cls = "TYPED_ENGINEERING_OPERATOR"
        else:
            cls = "COMPOSITION_SHORTHAND_RENAMING"

        counts[cls] += 1
        records.append({"op_id": op_id, "symbol": sym, "classification": cls})

    total = len(items)
    renaming_total = counts["COMPOSITION_SHORTHAND_RENAMING"] + counts["OVERLOADED_RENAMING"]
    renaming_ratio = Fraction(renaming_total, total)
    primitive_ratio = Fraction(counts["OPERATIONAL_NEW_PRIMITIVE"], total)
    return {
        "total_symbols": total,
        "counts": counts,
        "renaming_total": renaming_total,
        "renaming_ratio": frac_str(renaming_ratio),
        "renaming_pct": format_exact_decimal(renaming_ratio * 100, 2),
        "new_primitive_ratio": frac_str(primitive_ratio),
        "records": records,
    }


# ---------------------------------------------------------------------------
# Pillar 4: Phase-1 / Phase-2 Orthogonality & Anti-Novelty-Inflation Composer
# ---------------------------------------------------------------------------


def compose_phase1_phase2_verdict(
    phase1_verdict: Any,
    phase2_status: Any,
    full_text_prior_art_checked: Any,
    owner_direction_confirmed: Any,
) -> dict[str, Any]:
    """Compose decoupled Phase-1 empirical and Phase-2 prior-art verdicts under Laws 1-5."""
    p1 = require_non_empty_str(phase1_verdict, "phase1_verdict")
    if p1 not in _VALID_PHASE1_VERDICTS:
        raise OtfOracleError("INVALID_PHASE1_VERDICT", f"unsupported phase1_verdict: {p1!r}")
    p2 = require_non_empty_str(phase2_status, "phase2_status")
    if p2 not in _VALID_PHASE2_STATUSES:
        raise OtfOracleError("INVALID_PHASE2_STATUS", f"unsupported phase2_status: {p2!r}")
    prior_checked = require_exact_bool(full_text_prior_art_checked, "full_text_prior_art_checked")
    owner_ok = require_exact_bool(owner_direction_confirmed, "owner_direction_confirmed")

    if p1 == "P1_UNMEASURABLE_RETURNED" and p2 != "PENDING_PHASE2":
        raise OtfOracleError("PREMATURE_PHASE2_ON_UNMEASURABLE", "Rule 6 forbids Phase-2 judgment on unmeasurable claims")

    if p2 != "PENDING_PHASE2" and not prior_checked:
        raise OtfOracleError("PRIOR_ART_CHECK_REQUIRED", f"{p2} requires full_text_prior_art_checked=True")

    p1_valid = p1 in {"P1_VERIFIED_INVARIANT", "P1_STRUCTURED_REMAINDER"}
    if not p1_valid and p2 not in {"PENDING_PHASE2", "N0_KNOWN_BY_MECHANISM"}:
        raise OtfOracleError("NOVELTY_INFLATION_REFUSED", f"{p2} requires valid Phase-1 result")

    return {
        "phase1_verdict": p1,
        "phase2_status": p2,
        "phase1_empirical_valid": p1_valid,
        "phase2_overrides_phase1": False,
        "full_text_prior_art_checked": prior_checked,
        "owner_direction_confirmed": owner_ok,
        "policy_adoption_ready": owner_ok and p1_valid,
    }
