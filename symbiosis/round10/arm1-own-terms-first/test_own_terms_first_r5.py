"""Comprehensive R5 mutation-killing & red-team test suite for AUDIT-084.

Covers BOTH own_terms_first_oracle.py AND own_terms_first_audit.py under
-I -O -B -W error with zero bare assert statements and zero floats on trust paths.
"""

from __future__ import annotations

import contextlib
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Callable

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import own_terms_first_audit as audit_mod
import own_terms_first_oracle as oracle


class TestFailure(RuntimeError):
    """Explicit assertion-free test failure."""


def check_eq(actual: Any, expected: Any, label: str) -> None:
    if actual != expected or type(actual) is not type(expected):
        raise TestFailure(f"{label}: expected {expected!r} ({type(expected).__name__}), got {actual!r} ({type(actual).__name__})")


def check_raises(fn: Callable[[], Any], expected_code: str, label: str) -> None:
    try:
        fn()
    except oracle.OtfOracleError as exc:
        if exc.code != expected_code:
            raise TestFailure(f"{label}: expected code {expected_code!r}, got {exc.code!r} ({exc})") from exc
        return
    raise TestFailure(f"{label}: expected OtfOracleError({expected_code!r}) but succeeded")


def _base_valid_nets() -> list[dict[str, str]]:
    return [
        {"axis": "sampling_rate", "net_id": "N1", "obs_score": "4/5", "iid_null_score": "1/10", "spec_null_score": "1/5", "control_score": "1/20"},
        {"axis": "quantisation", "net_id": "N2", "obs_score": "4/5", "iid_null_score": "1/10", "spec_null_score": "1/5", "control_score": "1/20"},
        {"axis": "amplitude_scale", "net_id": "N3", "obs_score": "4/5", "iid_null_score": "1/10", "spec_null_score": "1/5", "control_score": "1/20"},
        {"axis": "window", "net_id": "N4", "obs_score": "4/5", "iid_null_score": "1/10", "spec_null_score": "1/5", "control_score": "1/20"},
        {"axis": "instrument", "net_id": "N5", "obs_score": "4/5", "iid_null_score": "1/10", "spec_null_score": "1/5", "control_score": "1/20"},
    ]


def _base_spec() -> dict[str, Any]:
    return {
        "min_signal_margin": "1/2",
        "max_net_spread": "1/10",
        "max_control_score": "1/10",
        "fwer_alpha": "1/20",
        "per_test_alpha": "1/100",
        "unseen_data_verified": True,
        "input_sha256_pinned": True,
        "measurable_definition_present": True,
    }


def test_primitives_and_refusals() -> None:
    oracle.verify_no_floats({"a": [1, (2, "x"), {3}]})
    check_raises(lambda: oracle.verify_no_floats(1.5), "FLOAT_FORBIDDEN", "scalar float")
    check_raises(lambda: oracle.verify_no_floats({1.0: "x"}), "FLOAT_FORBIDDEN", "dict key float")
    check_raises(lambda: oracle.verify_no_floats({"a": [1.0]}), "FLOAT_FORBIDDEN", "nested float")

    check_eq(oracle.require_non_empty_str("  ok  ", "f"), "ok", "strip str")
    check_raises(lambda: oracle.require_non_empty_str(1, "f"), "TYPE_ERROR", "non-str")
    check_raises(lambda: oracle.require_non_empty_str("   ", "f"), "EMPTY_STRING", "blank str")
    check_raises(lambda: oracle.require_non_empty_str("id\u200b", "f"), "INVALID_CHAR", "zwsp rejected")
    check_raises(lambda: oracle.require_non_empty_str("id\x07", "f"), "INVALID_CHAR", "ctrl char rejected")

    check_eq(oracle.require_exact_bool(True, "b"), True, "bool True")
    check_raises(lambda: oracle.require_exact_bool(1, "b"), "TYPE_ERROR", "int not bool")

    check_eq(oracle.require_exact_int(5, "i"), 5, "int 5")
    check_raises(lambda: oracle.require_exact_int(False, "i"), "TYPE_ERROR", "bool not int")
    check_raises(lambda: oracle.require_exact_int(5.0, "i"), "TYPE_ERROR", "float not int")

    check_eq(oracle.require_exact_fraction(Fraction(2, 3), "x"), Fraction(2, 3), "Fraction")
    check_eq(oracle.require_exact_fraction(-3, "x"), Fraction(-3, 1), "int")
    check_eq(oracle.require_exact_fraction("0.25", "x"), Fraction(1, 4), "dec str")
    check_eq(oracle.require_exact_fraction("-3/4", "x"), Fraction(-3, 4), "frac str")
    check_raises(lambda: oracle.require_exact_fraction(True, "x"), "TYPE_ERROR", "bool frac")
    check_raises(lambda: oracle.require_exact_fraction(0.5, "x"), "FLOAT_FORBIDDEN", "float frac")
    check_raises(lambda: oracle.require_exact_fraction("1/0", "x"), "ZERO_DENOMINATOR", "div0")
    check_raises(lambda: oracle.require_exact_fraction("1.0\n", "x"), "INVALID_RATIONAL", "newline")
    check_raises(lambda: oracle.require_exact_fraction([], "x"), "TYPE_ERROR", "list frac")

    check_eq(oracle.require_list_or_tuple([1], "s"), (1,), "list")
    check_raises(lambda: oracle.require_list_or_tuple("abc", "s"), "TYPE_ERROR", "str not seq")
    check_raises(lambda: oracle.require_list_or_tuple([], "s"), "EMPTY_SEQUENCE", "empty list")

    check_eq(oracle.frac_str(Fraction(4, 2)), "2/1", "frac_str")
    check_raises(lambda: oracle.frac_str(2), "TYPE_ERROR", "frac_str non-Fraction")
    check_eq(oracle.format_exact_decimal(Fraction(1, 2), 0), "1", "0dp half up")
    check_eq(oracle.format_exact_decimal(Fraction(1, 3), 0), "0", "0dp below half")
    check_eq(oracle.format_exact_decimal(Fraction(-1, 200), 2), "-0.01", "neg half up")
    check_eq(oracle.format_exact_decimal(Fraction(-1, 1000), 2), "0.00", "neg zero no sign")
    check_raises(lambda: oracle.format_exact_decimal(1, 2), "TYPE_ERROR", "format non-Fraction")
    check_raises(lambda: oracle.format_exact_decimal(Fraction(1, 2), -1), "INVALID_RANGE", "neg places")

    check_eq(oracle.canonical_json_bytes({"b": 1, "a": 2}), b'{"a":2,"b":1}', "canonical json")
    check_eq(len(oracle.canonical_sha256({"a": 1})), 64, "sha len")
    check_raises(lambda: oracle.canonical_json_bytes({"a": 1.0}), "FLOAT_FORBIDDEN", "json float")


def test_pillar1_net_invariance_gate() -> None:
    # Passing exact boundary case: bonf_upper == fwer_alpha (5 * 1/100 == 1/20), max_spread==0, max_ctrl==0
    nets = _base_valid_nets()
    spec = _base_spec()
    ok = oracle.audit_phase1_net_invariance_gate(nets, spec)
    check_eq(ok["phase1_verdict"], "P1_VERIFIED_INVARIANT", "valid 5-axis passes")
    check_eq(ok["bonferroni_upper"], "1/20", "exact boundary bonferroni")

    # Boundary: max_net_spread == 0 and max_control_score == 0 allowed
    nets_zero_ctrl = [dict(n, control_score="0") for n in nets]
    ok_zero = oracle.audit_phase1_net_invariance_gate(nets_zero_ctrl, dict(spec, max_net_spread="0", max_control_score="0"))
    check_eq(ok_zero["phase1_verdict"], "P1_VERIFIED_INVARIANT", "zero spread & zero ctrl boundaries pass")

    # Rule 6 unmeasurable returned immediately, AFTER zero-float validation (OTF-BUG-01)
    unm = oracle.audit_phase1_net_invariance_gate([], dict(spec, measurable_definition_present=False))
    check_eq(unm["phase1_verdict"], "P1_UNMEASURABLE_RETURNED", "Rule 6 returns unmeasurable")
    check_raises(
        lambda: oracle.audit_phase1_net_invariance_gate([0.75], dict(spec, measurable_definition_present=False)),
        "FLOAT_FORBIDDEN",
        "float in net_measurements refused before Rule 6 return (OTF-BUG-01)",
    )

    # OTF-BUG-02a/b: negative nulls cannot rescue zero signal; control stronger than obs MUST fail Rule 5!
    zero_neg_null = [dict(n, obs_score="0", iid_null_score="-1", spec_null_score="-1", control_score="1/20") for n in nets]
    r_zn = oracle.audit_phase1_net_invariance_gate(zero_neg_null, spec)
    check_eq(r_zn["phase1_verdict"], "P1_FAILED_NULL_OR_CONTROL", "zero signal with negative nulls refused (OTF-BUG-02a)")
    check_eq(
        r_zn["violation_codes"],
        ["RULE4A_IID_NULL_FAILED", "RULE4B_RED_NOISE_SPECTRUM_NULL_FAILED", "RULE5_NEGATIVE_CONTROL_CONTAMINATED"],
        "all 3 magnitude checks fire",
    )

    ctrl_dom = [dict(n, obs_score="1/50", iid_null_score="0", spec_null_score="0", control_score="1/20") for n in nets]
    r_cd = oracle.audit_phase1_net_invariance_gate(ctrl_dom, dict(spec, min_signal_margin="1/100"))
    check_eq(r_cd["phase1_verdict"], "P1_FAILED_NULL_OR_CONTROL", "control 2.5x stronger than obs refused (OTF-BUG-02b)")
    check_eq(r_cd["violation_codes"], ["RULE5_NEGATIVE_CONTROL_CONTAMINATED"], "Rule 5 dominance check fires")

    # Case-insensitive duplicate net_id check (OTF-BUG-04)
    check_raises(
        lambda: oracle.audit_phase1_net_invariance_gate([nets[0], dict(nets[0], net_id="n1")], spec),
        "DUPLICATE_ID",
        "case-variant net_id refused",
    )

    # Red-team: Bonferroni dependence check catches per_alpha=101/10000 (indep FWER 4.95% < 5%, Bonf 5.05% > 5%!)
    dep_fwer = oracle.audit_phase1_net_invariance_gate(nets, dict(spec, per_test_alpha="101/10000"))
    check_eq(dep_fwer["phase1_verdict"], "P1_FAILED_NET_INVARIANCE", "dependent Bonferroni FWER exceeded")
    check_eq(dep_fwer["violation_codes"], ["OTF_TIGHT01_FWER_EXCEEDED"], "FWER code")

    # Bonferroni cap at 1/1 when M * per_alpha >= 1
    huge_fwer = oracle.audit_phase1_net_invariance_gate(nets, dict(spec, per_test_alpha="1/2"))
    check_eq(huge_fwer["bonferroni_upper"], "1/1", "bonferroni capped at 1")

    # Red-team: negative control with large NEGATIVE magnitude (-1/2) MUST fail Rule 5 via abs()!
    neg_ctrl_nets = _base_valid_nets()
    neg_ctrl_nets[0]["control_score"] = "-1/2"
    r_neg_ctrl = oracle.audit_phase1_net_invariance_gate(neg_ctrl_nets, spec)
    check_eq(r_neg_ctrl["phase1_verdict"], "P1_FAILED_NULL_OR_CONTROL", "negative control magnitude caught")
    check_eq(r_neg_ctrl["violation_codes"], ["RULE5_NEGATIVE_CONTROL_CONTAMINATED"], "Rule 5 code")

    # Each individual failure branch
    r_unpin = oracle.audit_phase1_net_invariance_gate(nets, dict(spec, input_sha256_pinned=False))
    check_eq(r_unpin["violation_codes"], ["R7_UNPINNED_RAW_INPUT"], "R7 unpinned")

    r_unseen = oracle.audit_phase1_net_invariance_gate(nets, dict(spec, unseen_data_verified=False))
    check_eq(r_unseen["phase1_verdict"], "P1_FAILED_NULL_OR_CONTROL", "no unseen data")
    check_eq(r_unseen["violation_codes"], ["RULE4_NO_UNSEEN_DATA"], "Rule 4 unseen")

    r_missing_ax = oracle.audit_phase1_net_invariance_gate(nets[:4], spec)
    check_eq(r_missing_ax["missing_axes"], ["instrument"], "missing instrument axis")
    check_eq(r_missing_ax["violation_codes"], ["RULE3_INCOMPLETE_NET_AXES"], "Rule 3 incomplete axes")

    spread_nets = _base_valid_nets()
    spread_nets[0]["obs_score"] = "1"
    r_spread = oracle.audit_phase1_net_invariance_gate(spread_nets, spec)
    check_eq(r_spread["violation_codes"], ["RULE3_NET_INVARIANCE_FAILED"], "Rule 3 spread failed")

    iid_fail_nets = [dict(n, iid_null_score="3/5") for n in nets]
    r_iid = oracle.audit_phase1_net_invariance_gate(iid_fail_nets, spec)
    check_eq(r_iid["violation_codes"], ["RULE4A_IID_NULL_FAILED"], "Rule 4A IID null failed")

    spec_fail_nets = [dict(n, spec_null_score="3/5") for n in nets]
    r_spec = oracle.audit_phase1_net_invariance_gate(spec_fail_nets, spec)
    check_eq(r_spec["violation_codes"], ["RULE4B_RED_NOISE_SPECTRUM_NULL_FAILED"], "Rule 4B red-noise failed")

    # Exact boundary: margin == min_signal_margin passes
    margin_eq_nets = [dict(n, obs_score="7/10", iid_null_score="1/5", spec_null_score="1/5") for n in nets]
    r_meq = oracle.audit_phase1_net_invariance_gate(margin_eq_nets, spec)
    check_eq(r_meq["phase1_verdict"], "P1_VERIFIED_INVARIANT", "exact margin boundary passes")

    # Schema & range refusals
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate(nets, {"bad": 1}), "SCHEMA_ERROR", "bad spec keys")
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate(nets, dict(spec, min_signal_margin="0")), "INVALID_RANGE", "margin<=0")
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate(nets, dict(spec, max_net_spread="-1")), "INVALID_RANGE", "spread<0")
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate(nets, dict(spec, max_control_score="-1")), "INVALID_RANGE", "ctrl<0")
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate(nets, dict(spec, fwer_alpha="0")), "INVALID_RANGE", "fwer=0")
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate(nets, dict(spec, fwer_alpha="1")), "INVALID_RANGE", "fwer=1")
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate(nets, dict(spec, per_test_alpha="0")), "INVALID_RANGE", "per_alpha=0")
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate(nets, dict(spec, per_test_alpha="1")), "INVALID_RANGE", "per_alpha=1")
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate([{"bad": 1}], spec), "SCHEMA_ERROR", "bad net keys")
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate([dict(nets[0], axis="unknown")], spec), "INVALID_AXIS", "bad axis")
    check_raises(lambda: oracle.audit_phase1_net_invariance_gate([nets[0], nets[0]], spec), "DUPLICATE_ID", "dup net_id")


def test_pillar2_continuum_remainder_ladder() -> None:
    w1 = [1, 1, 1, 1, -1, -1, -1, -1]
    w2 = [1, 1, -1, -1, 1, 1, -1, -1]
    w3 = [1, -1, 1, -1, 1, -1, 1, -1]
    y2 = [4 * a + 2 * b for a, b in zip(w1, w2)]
    y3 = [4 * a + 2 * b + 2 * c for a, b, c in zip(w1, w2, w3)]

    # Finite model misspecification confound
    r_mis = oracle.audit_continuum_remainder_ladder_exact(y2, y2, [w1, w2], ["1/10", "1/10"], "4/5", "1/10")
    check_eq(r_mis["classification"], "FINITE_MODEL_MISSPECIFICATION", "2-mode discrete misspecification")
    check_eq(r_mis["single_model_test_confounded"], True, "1-model confounded")
    check_eq(r_mis["rungs"][0]["train_residual_energy_ratio"], "1/5", "rung 1 ratio 1/5")
    check_eq(r_mis["rungs"][1]["train_residual_energy_ratio"], "0/1", "rung 2 collapses to 0")

    # Ladder-surviving structured remainder (including exact boundary min_unseen_corr_sq == 1)
    r_surv = oracle.audit_continuum_remainder_ladder_exact(y3, y3, [w1, w2], ["1/10", "1/10"], "1", "1/6")
    check_eq(r_surv["classification"], "STRUCTURED_REMAINDER_SURVIVING_LADDER", "3-mode survives 2-rung ladder")
    check_eq(r_surv["single_model_test_confounded"], False, "not confounded")

    # OTF-BUG-03: in-model shift P_{M_k}(y_unseen - y_train) MUST NOT inflate out-of-model unseen energy!
    y_tr_shift = [Fraction(5, 2) * a + b + c for a, b, c in zip(w1, w2, w3)]
    y_un_shift = [3 * a + b + c for a, b, c in zip(w1, w2, w3)]
    r_shift = oracle.audit_continuum_remainder_ladder_exact(y_tr_shift, y_un_shift, [w1, w2], ["1/10", "1/10"], "4/5", "1/10")
    check_eq(r_shift["rungs"][1]["unseen_residual_energy_ratio"], "1/11", "orthogonal unseen remainder ratio 1/11 (OTF-BUG-03)")
    check_eq(r_shift["rungs"][1]["structured_at_rung"], False, "1/11 < 1/10 fails rung 2")
    check_eq(r_shift["classification"], "FINITE_MODEL_MISSPECIFICATION", "in-model shift cannot fake ladder survival")

    # Mixed-mode unmasking: rung 1 has corr_sq=1/2 < 4/5; rung 2 projects both onto M_2^perp -> corr_sq=1/1 >= 4/5
    y3_mixed = [4 * a + 4 * c for a, c in zip(w1, w3)]
    r_unmask = oracle.audit_continuum_remainder_ladder_exact(y3, y3_mixed, [w1, w2], ["1/10", "1/10"], "4/5", "1/10")
    check_eq(r_unmask["rungs"][0]["structured_at_rung"], False, "rung 1 masked by w2 mismatch (corr_sq=1/2)")
    check_eq(r_unmask["rungs"][1]["structured_at_rung"], True, "rung 2 exposes persistent w3 (corr_sq=1/1)")
    check_eq(r_unmask["classification"], "STRUCTURED_REMAINDER_SURVIVING_LADDER", "final rung survival classified accurately")

    # Red-team: anti-correlated unseen residual (opposite sign y_unseen = 4*w1 - 2*w2 - 2*w3) MUST NOT pass!
    y3_neg_rem = [4 * a - 2 * b - 2 * c for a, b, c in zip(w1, w2, w3)]
    r_anti = oracle.audit_continuum_remainder_ladder_exact(y3, y3_neg_rem, [w1, w2], ["1/10", "1/10"], "4/5", "1/10")
    check_eq(r_anti["classification"], "NO_STRUCTURED_REMAINDER", "anti-correlated unseen residual refused")
    check_eq(r_anti["rungs"][0]["unseen_positive_alignment"], False, "negative sign caught")

    # Red-team: vanishing-amplitude unseen residual (y_unseen = 4*w1 + (1/100)*w2 + (1/100)*w3) MUST NOT pass!
    y3_tiny = [4 * a + Fraction(1, 100) * b + Fraction(1, 100) * c for a, b, c in zip(w1, w2, w3)]
    r_tiny = oracle.audit_continuum_remainder_ladder_exact(y3, y3_tiny, [w1, w2], ["1/10", "1/10"], "4/5", "1/10")
    check_eq(r_tiny["classification"], "NO_STRUCTURED_REMAINDER", "vanishing unseen residual energy refused")

    # Red-team: null_corr == 1 prevents passing (strict > nc)
    r_null_tie = oracle.audit_continuum_remainder_ladder_exact(y3, y3, [w1, w2], ["1", "1"], "4/5", "1/10")
    check_eq(r_null_tie["classification"], "NO_STRUCTURED_REMAINDER", "null tie fails strict >")

    # Refusals
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1], [1], [[1], [1]], ["0", "0"], "1/2", "1/10"), "INVALID_LENGTH", "len < 2")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 2], [1, 2, 3], [[1, 1], [1, -1]], ["0", "0"], "1/2", "1/10"), "INVALID_LENGTH", "unequal signal len")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([0, 0], [1, 1], [[1, 1], [1, -1]], ["0", "0"], "1/2", "1/10"), "ZERO_ENERGY", "zero train energy")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [0, 0], [[1, 1], [1, -1]], ["0", "0"], "1/2", "1/10"), "ZERO_ENERGY", "zero unseen energy")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[1, 1]], ["0"], "1/2", "1/10"), "INVALID_LENGTH", "1-rung ladder refused")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[1, 1], [1, -1]], ["0"], "1/2", "1/10"), "LENGTH_MISMATCH", "null len mismatch")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[1, 1], [1, -1]], ["0", "0"], "0", "1/10"), "INVALID_RANGE", "min_corr <= 0")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[1, 1], [1, -1]], ["0", "0"], "2", "1/10"), "INVALID_RANGE", "min_corr > 1")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[1, 1], [1, -1]], ["0", "0"], "1/2", "0"), "INVALID_RANGE", "min_eratio <= 0")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[1, 1], [1, -1]], ["0", "0"], "1/2", "1"), "INVALID_RANGE", "min_eratio >= 1")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[1, 1, 1], [1, -1]], ["0", "0"], "1/2", "1/10"), "INVALID_LENGTH", "basis wrong len")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[0, 0], [1, -1]], ["0", "0"], "1/2", "1/10"), "ZERO_BASIS_VECTOR", "zero basis")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[1, 1], [1, 0]], ["0", "0"], "1/2", "1/10"), "NON_ORTHOGONAL_BASIS", "non-orthogonal")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[1, 1], [1, -1]], ["-1/10", "0"], "1/2", "1/10"), "INVALID_RANGE", "neg null corr")
    check_raises(lambda: oracle.audit_continuum_remainder_ladder_exact([1, 1], [1, 1], [[1, 1], [1, -1]], ["2", "0"], "1/2", "1/10"), "INVALID_RANGE", ">1 null corr")


def test_pillar3_symbols_and_pillar4_composer() -> None:
    # All 5 symbol classifications exercised
    mix_syms = [
        {"op_id": "S1", "symbol": "prim", "reproducible_from_rules": True, "unseen_physical_prediction": True, "adds_rule_beyond_standard": True, "overloads_distinct_constructs": False},
        {"op_id": "S2", "symbol": "eng", "reproducible_from_rules": True, "unseen_physical_prediction": False, "adds_rule_beyond_standard": True, "overloads_distinct_constructs": False},
        {"op_id": "S3", "symbol": "short", "reproducible_from_rules": True, "unseen_physical_prediction": False, "adds_rule_beyond_standard": False, "overloads_distinct_constructs": False},
        {"op_id": "S4", "symbol": "over", "reproducible_from_rules": True, "unseen_physical_prediction": True, "adds_rule_beyond_standard": True, "overloads_distinct_constructs": True},
        {"op_id": "S5", "symbol": "nonrep", "reproducible_from_rules": False, "unseen_physical_prediction": True, "adds_rule_beyond_standard": True, "overloads_distinct_constructs": False},
    ]
    res = oracle.audit_symbol_utility_rule2(mix_syms)
    check_eq(res["counts"]["OPERATIONAL_NEW_PRIMITIVE"], 1, "1 primitive")
    check_eq(res["counts"]["TYPED_ENGINEERING_OPERATOR"], 1, "1 eng op")
    check_eq(res["counts"]["COMPOSITION_SHORTHAND_RENAMING"], 1, "1 shorthand")
    check_eq(res["counts"]["OVERLOADED_RENAMING"], 1, "1 overloaded")
    check_eq(res["counts"]["NON_REPRODUCIBLE_SYMBOL"], 1, "1 non-reproducible")
    check_eq(res["renaming_ratio"], "2/5", "2/5 renaming")

    # 8-glyph audit matches 7/8 renaming
    g8 = oracle.audit_symbol_utility_rule2(list(audit_mod.ALETHEIA_8_GLYPHS_AUDIT))
    check_eq(g8["renaming_ratio"], "7/8", "7/8 Aletheia glyphs are renamings")
    check_eq(g8["counts"]["OVERLOADED_RENAMING"], 1, "OP-04 overloaded")
    check_eq(g8["counts"]["TYPED_ENGINEERING_OPERATOR"], 1, "OP-08 engineering op")

    check_raises(lambda: oracle.audit_symbol_utility_rule2([{"bad": 1}]), "SCHEMA_ERROR", "bad symbol keys")
    check_raises(lambda: oracle.audit_symbol_utility_rule2([mix_syms[0], mix_syms[0]]), "DUPLICATE_ID", "dup op_id")
    check_raises(
        lambda: oracle.audit_symbol_utility_rule2([mix_syms[0], dict(mix_syms[0], op_id="s1", symbol="other")]),
        "DUPLICATE_ID",
        "case-variant op_id refused (OTF-BUG-04)",
    )
    check_raises(
        lambda: oracle.audit_symbol_utility_rule2([mix_syms[0], dict(mix_syms[0], op_id="S99", symbol="PRIM")]),
        "DUPLICATE_SYMBOL",
        "duplicate symbol collision refused (OTF-BUG-04)",
    )

    # Pillar 4 composer: valid decoupling + refusals
    c1 = oracle.compose_phase1_phase2_verdict("P1_VERIFIED_INVARIANT", "N0_KNOWN_BY_MECHANISM", True, False)
    check_eq(c1["phase1_empirical_valid"], True, "N0 preserves P1 validity")
    check_eq(c1["policy_adoption_ready"], False, "owner confirmation gates adoption")

    c2 = oracle.compose_phase1_phase2_verdict("P1_FAILED_NET_INVARIANCE", "N0_KNOWN_BY_MECHANISM", True, True)
    check_eq(c2["phase1_empirical_valid"], False, "failed P1 stays False")

    c3 = oracle.compose_phase1_phase2_verdict("P1_VERIFIED_INVARIANT", "N2_GENUINELY_NOVEL", True, True)
    check_eq(c3["policy_adoption_ready"], True, "verified N2 ready")

    check_raises(lambda: oracle.compose_phase1_phase2_verdict("BAD", "PENDING_PHASE2", False, False), "INVALID_PHASE1_VERDICT", "bad p1")
    check_raises(lambda: oracle.compose_phase1_phase2_verdict("P1_VERIFIED_INVARIANT", "BAD", False, False), "INVALID_PHASE2_STATUS", "bad p2")
    check_raises(lambda: oracle.compose_phase1_phase2_verdict("P1_UNMEASURABLE_RETURNED", "N0_KNOWN_BY_MECHANISM", True, False), "PREMATURE_PHASE2_ON_UNMEASURABLE", "Rule 6 blocks Phase 2")
    check_raises(lambda: oracle.compose_phase1_phase2_verdict("P1_VERIFIED_INVARIANT", "DOES_NOT_TRANSLATE", False, False), "PRIOR_ART_CHECK_REQUIRED", "DOES_NOT_TRANSLATE needs prior-art check")
    check_raises(lambda: oracle.compose_phase1_phase2_verdict("P1_FAILED_NULL_OR_CONTROL", "N2_GENUINELY_NOVEL", True, False), "NOVELTY_INFLATION_REFUSED", "failed P1 cannot be N2")
    check_raises(lambda: oracle.compose_phase1_phase2_verdict("P1_FAILED_NULL_OR_CONTROL", "N1_NEW_BRIDGE_OR_SYNTHESIS", True, False), "NOVELTY_INFLATION_REFUSED", "failed P1 cannot be N1")


def test_audit_runner_and_refusals() -> None:
    cert_s = audit_mod.run_audit(standalone=True)
    check_eq(cert_s["verdict"], "VERIFIED", "standalone verified")
    check_eq(cert_s["pillar3_honest_8_glyph_audit"]["renaming_ratio"], "7/8", "standalone 7/8")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        out_file = tmp_path / "otf_cert.json"

        buf_j = io.StringIO()
        with contextlib.redirect_stdout(buf_j):
            rc = audit_mod.main(["--standalone", "--json", "--output", str(out_file)])
        check_eq(rc, 0, "cli json rc=0")
        check_eq(out_file.read_text(encoding="ascii"), buf_j.getvalue(), "file == stdout")

        buf_s = io.StringIO()
        with contextlib.redirect_stdout(buf_s):
            rc2 = audit_mod.main(["--standalone"])
        check_eq(rc2, 0, "cli summary rc=0")
        check_eq(json.loads(buf_s.getvalue())["certificate_sha256"], cert_s["certificate_sha256"], "summary sha matches")

        # Live runner refusal paths
        empty_r10 = tmp_path / "empty_r10"
        empty_r10.mkdir()
        check_raises(lambda: audit_mod.run_audit(standalone=False, round10_root=empty_r10), "MISSING_FILE", "missing portals")

        # SHA mismatch
        bad_sha_r10 = tmp_path / "bad_sha_r10"
        first_rel = next(iter(audit_mod.PINNED_PORTAL_SHA256.keys()))
        first_fp = bad_sha_r10 / "portals" / first_rel
        first_fp.parent.mkdir(parents=True, exist_ok=True)
        first_fp.write_bytes(b"corrupt")
        check_raises(lambda: audit_mod.run_audit(standalone=False, round10_root=bad_sha_r10), "SHA_MISMATCH", "corrupt portal sha")

        # Synthetic live portals to test anchor, export schema/role, missing repo, git show failure, calculus mismatch
        orig_pins = dict(audit_mod.PINNED_PORTAL_SHA256)
        orig_commit = audit_mod.PINNED_ALETHEIA_PR1_COMMIT
        try:
            syn_r10 = tmp_path / "syn_r10"
            def _write_portals(otf_s: str, cont_s: str, exp_obj: Any) -> None:
                for rel in orig_pins:
                    fp = syn_r10 / "portals" / rel
                    fp.parent.mkdir(parents=True, exist_ok=True)
                    if rel.endswith("OWN_TERMS_FIRST.md"):
                        b = otf_s.encode("utf-8")
                    elif rel.endswith("continuum.md"):
                        b = cont_s.encode("utf-8")
                    elif rel.endswith("session_raw_verbatim_export.json"):
                        b = json.dumps(exp_obj).encode("utf-8")
                    else:
                        b = b"stub\n"
                    fp.write_bytes(b)
                    audit_mod.PINNED_PORTAL_SHA256[rel] = hashlib.sha256(b).hexdigest()

            good_otf = "\n".join(
                [
                    "The project owner is asked to confirm or correct it.",
                    "Two phases, kept apart.",
                    "New symbols are judged by use.",
                    "Where a claim gives nothing measurable, hand it back to its authors for a definition.",
                    "leave a remainder that is not noise",
                ]
            )
            good_cont = "reveals the same four universal transformations"
            good_exp = {"turns": [{"role": "model"} for _ in range(20)]}

            _write_portals("bad otf", good_cont, good_exp)
            check_raises(lambda: audit_mod.run_audit(standalone=False, round10_root=syn_r10), "ANCHOR_MISMATCH", "bad otf anchor")

            _write_portals(good_otf, "bad cont", good_exp)
            check_raises(lambda: audit_mod.run_audit(standalone=False, round10_root=syn_r10), "ANCHOR_MISMATCH", "bad cont anchor")

            _write_portals(good_otf, good_cont, {"turns": []})
            check_raises(lambda: audit_mod.run_audit(standalone=False, round10_root=syn_r10), "SCHEMA_ERROR", "short export turns")

            bad_role_exp = {"turns": [{"role": "user"} for _ in range(20)]}
            _write_portals(good_otf, good_cont, bad_role_exp)
            check_raises(lambda: audit_mod.run_audit(standalone=False, round10_root=syn_r10), "ANCHOR_MISMATCH", "non-model turns")

            _write_portals(good_otf, good_cont, good_exp)
            check_raises(lambda: audit_mod.run_audit(standalone=False, round10_root=syn_r10), "MISSING_REPO", "missing aletheia-live")

            # Create minimal git repo for git show failure and calculus line mismatch
            fake_repo = syn_r10 / "repos" / "aletheia-live"
            fake_repo.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "-C", str(fake_repo), "init", "-q"], check=True)
            check_raises(lambda: audit_mod.run_audit(standalone=False, round10_root=syn_r10), "GIT_SHOW_FAILED", "bad commit sha")

            # Commit short calculus.py to trigger calculus mismatch
            (fake_repo / "aletheia").mkdir(exist_ok=True)
            (fake_repo / "aletheia" / "calculus.py").write_text("# short\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(fake_repo), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(fake_repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"],
                check=True,
            )
            head_sha = subprocess.check_output(["git", "-C", str(fake_repo), "rev-parse", "HEAD"], text=True).strip()
            audit_mod.PINNED_ALETHEIA_PR1_COMMIT = head_sha
            check_raises(lambda: audit_mod.run_audit(standalone=False, round10_root=syn_r10), "ANCHOR_MISMATCH", "calculus line mismatch")
        finally:
            audit_mod.PINNED_PORTAL_SHA256.clear()
            audit_mod.PINNED_PORTAL_SHA256.update(orig_pins)
            audit_mod.PINNED_ALETHEIA_PR1_COMMIT = orig_commit

    # Live run against workspace round10 portals (when present)
    default_r10 = Path(__file__).resolve().parent.parent
    if (default_r10 / "portals" / "aletheia" / "pr_9_files" / "spec" / "proposals" / "OWN_TERMS_FIRST.md").is_file():
        cert_l = audit_mod.run_audit(standalone=False)
        check_eq(cert_l["execution_mode"], "live_readonly", "live mode")
        check_eq(cert_l["verdict"], "VERIFIED", "live verified")
        check_eq(cert_l["live_code_cross_checks"]["calculus_py_lines"], 2079, "live calculus lines")
        check_eq(cert_l["live_code_cross_checks"]["calculus_py_file_io_hits"], 0, "live zero file I/O")
        buf_l = io.StringIO()
        with contextlib.redirect_stdout(buf_l):
            rc_l = audit_mod.main(["--round10-root", str(default_r10)])
        check_eq(rc_l, 0, "cli live rc=0")


def main() -> int:
    tests = [
        ("primitives_and_refusals", test_primitives_and_refusals),
        ("pillar1_net_invariance_gate", test_pillar1_net_invariance_gate),
        ("pillar2_continuum_remainder_ladder", test_pillar2_continuum_remainder_ladder),
        ("pillar3_symbols_and_pillar4_composer", test_pillar3_symbols_and_pillar4_composer),
        ("audit_runner_and_refusals", test_audit_runner_and_refusals),
    ]
    for _name, fn in tests:
        fn()
    sys.stdout.write(json.dumps({"passed": len(tests), "status": "PASS", "suite": "test_own_terms_first_r5"}, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
