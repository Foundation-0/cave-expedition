#!/usr/bin/env python3
"""Exact pure-Q pre-registration statistical-power, net-invariance, and knowledge-factory certifier.

Targets (strictly read-only, 0 external writes):
  - Foundation-0/cave-expedition PR #6 (outside/continuum-four-transformations-prereg @ 24d77573)
  - Foundation-0/aletheia PR #6 (feat/nichochar-knowledge-factories-capture @ 98db54c3)
  - Foundation-0/continuum PR #1 (continuum.md @ 8d3e7345)
  - Cross-audit against verified AUDIT-076R (symbiosis/round8/arm5-langchain-knowledge-factory/)

100% pure Python 3 stdlib using exact int/Fraction arithmetic.
Zero floating-point literals or values; zero bare assert statements.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
from typing import Any, Sequence


SCHEMA_VERSION = "prereg-raw-data-audit-v1"
AUDIT_ID = "AUDIT-087"
PINNED_CAVE_PR6_COMMIT = "24d7757309b5b6b7b5179be2a65387af58fd5f9b"
PINNED_ALETHEIA_PR6_COMMIT = "98db54c39812546e9acb8e7f9f2b39fffd46e487"
HOLM_MIN_THRESHOLD = Fraction(1, 560)
MAX_EXPERIMENT_FALSE_INVALID = Fraction(1, 10)
MAX_K2_FWER = Fraction(1, 10)

ALLOWED_PREREG_KEYS = frozenset(
    {
        "segments_per_instrument",
        "segment_alpha",
        "control_k_limit",
        "control_rate_cap",
        "control_combine_mode",
        "num_controls_per_instrument",
        "calibrated_instruments",
        "required_support_quorum",
        "max_per_instrument_false_invalid",
        "rank_end_matching",
        "split_time_odd_transfer",
        "restrict_perm_to_joint_support",
        "k2_seeds",
        "k2_max_rejects",
        "k2_num_classes",
        "max_k2_per_class_alpha",
    }
)
ALLOWED_COMBINE_MODES = ("and", "or", "binom_only")

ALLOWED_KF_KEYS = frozenset(
    {
        "actor_role",
        "reviewer_role",
        "target_layer",
        "source_integrity",
        "target_required_integrity",
        "source_confidentiality",
        "target_max_confidentiality",
        "human_signoff",
        "outside_err_before",
        "outside_err_after",
        "proxy_err_before",
        "proxy_err_after",
        "store_epoch",
        "butler_loaded_epoch",
        "in_flight_nudge_sent",
    }
)
ALLOWED_ACTOR_ROLES = ("butler", "gardener")
ALLOWED_REVIEWER_ROLES = ("gardener", "independent_reviewer")
ALLOWED_TARGET_LAYERS = ("skill", "data_access_guidance", "domain_knowledge", "ephemeral_memory")
LAYER_MIN_INTEGRITY: dict[str, int] = {
    "skill": 3,
    "data_access_guidance": 3,
    "domain_knowledge": 2,
    "ephemeral_memory": 1,
}
LAYER_MAX_CONFIDENTIALITY: dict[str, int] = {
    "skill": 0,
    "data_access_guidance": 0,
    "domain_knowledge": 1,
    "ephemeral_memory": 2,
}

PINNED_PORTAL_DIGESTS: dict[str, dict[str, Any]] = {
    "round10/portals/cave-expedition/pr_6.md": {
        "bytes": 2245,
        "sha256": "76b2266f81b15a479324a0fa240d73e9866fa842e90a31df9c6c4c7ef5592b5b",
    },
    "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md": {
        "bytes": 25192,
        "sha256": "8ed03fb9f3f5b712d961b04ebdc2f539c398cac6e5e1fbecb6eeacb6041b5483",
    },
    "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/DATA_REQUEST.md": {
        "bytes": 5814,
        "sha256": "0ebf6b137ce13d644b06a4f947d10bdc59947ca369393b471369d0569064a314",
    },
    "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/ARM_B_OUTLINE.md": {
        "bytes": 2476,
        "sha256": "893b7744d6503e2857ac1d9eca97c1a63cb2bab6386d2e90b73071eac4896de1",
    },
    "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/README.md": {
        "bytes": 844,
        "sha256": "c7918d85041e4d6c1ceac552cc2f64839971cd1e28608f1b3abd276ce6cb1644",
    },
    "round10/portals/aletheia/pr_6.md": {
        "bytes": 2048,
        "sha256": "088f40fd8e8e5b0e404dff43295b2b38542edb2ef8651088b287e0358f74269b",
    },
    "round10/portals/aletheia/pr_6_files/captures/2026-11-21-nichochar-knowledge-factories/post.md": {
        "bytes": 22609,
        "sha256": "d433ac2988fefd9fb3434dfaa5c9fa4257830b3dd71ff3258a0e1068d3dd900b",
    },
    "round10/portals/aletheia/pr_6_files/captures/2026-11-21-nichochar-knowledge-factories/analysis.md": {
        "bytes": 13707,
        "sha256": "53edaf8612a959a16d0d86401f2fe55f65680c484e8de648ee86759cbee0473c",
    },
    "round10/portals/continuum/pr_1_files/continuum.md": {
        "bytes": 10121,
        "sha256": "516f6080563f223a4d8da437d37aaff479988f08f9079bfa48116cbb4fdc3150",
    },
    "round8/arm5-langchain-knowledge-factory/knowledge_factory_certificate.json": {
        "bytes": 11975,
        "sha256": "7f84e852283d072902207ba106f70b3384d00b2fd4041ff12cc21be25e08974b",
    },
}

VERBATIM_ANCHORS: tuple[tuple[str, str, int, str], ...] = (
    (
        "PREREG-LAPLACE",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        65,
        "p(pi) = (n(pi) + 1/2) / (sum of n + 3)",
    ),
    (
        "PREREG-U-FEATURE",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        85,
        "u  = a2 - a3                 changes sign under time reversal, unchanged by polarity flip",
    ),
    (
        "PREREG-S4-ORBITS",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        105,
        "summed over the 8 classes of patterns that map to each other under time reversal and polarity flip",
    ),
    (
        "PREREG-AMPLITUDE-SKIP",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        134,
        "exact code checks, not statistical runs (K1)",
    ),
    (
        "PREREG-C2-RULE",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        150,
        "K below the binomial 1 percent excess point (K < 4 when S = 12, K < 6 when S = 32) and K/S at most 0.10",
    ),
    (
        "PREREG-END-MATCH",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        163,
        "smallest sum of the squared jump between first and last value and the squared jump between first and last slope",
    ),
    (
        "PREREG-HOLM-28",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        184,
        "The confirmatory family has 28 tests. Holm's step-down method controls the family-wise error rate at 0.05.",
    ),
    (
        "PREREG-PRESENCE-K",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        188,
        "Needs K >= 5 of 12, or K >= 7 of 32",
    ),
    (
        "PREREG-K2-BOUND",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        211,
        "The per-segment rejection rate at 0.05 must be at most 0.086",
    ),
    (
        "PREREG-TESS-EXCLUDED",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        238,
        "TESS in this run, which has no second channel",
    ),
    (
        "DATA-REQ-TOTAL",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/DATA_REQUEST.md",
        6,
        "Total 634,994,866 bytes (about 635 MB).",
    ),
    (
        "ARMB-50-WINDOWS",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/ARM_B_OUTLINE.md",
        14,
        "at least 50 windows per pattern on average",
    ),
    (
        "KF-POST-GARDENER",
        "round10/portals/aletheia/pr_6_files/captures/2026-11-21-nichochar-knowledge-factories/post.md",
        46,
        "I call these gardeners: agents that are attached to a space, rather than a person",
    ),
    (
        "KF-POST-LENTON",
        "round10/portals/aletheia/pr_6_files/captures/2026-11-21-nichochar-knowledge-factories/post.md",
        242,
        "nudge the butlers when a page they're already using gets corrected",
    ),
    (
        "KF-POST-AUTOMERGE",
        "round10/portals/aletheia/pr_6_files/captures/2026-11-21-nichochar-knowledge-factories/post.md",
        314,
        "We see skills often want a user sign off. Other forms of memory fine to merge",
    ),
    (
        "KF-ANALYSIS-SPLIT",
        "round10/portals/aletheia/pr_6_files/captures/2026-11-21-nichochar-knowledge-factories/analysis.md",
        33,
        "skills often want a user sign off; other forms of memory fine to merge",
    ),
    (
        "KF-ANALYSIS-RETIRE",
        "round10/portals/aletheia/pr_6_files/captures/2026-11-21-nichochar-knowledge-factories/analysis.md",
        61,
        "procedural skills require a human sign-off to retire or replace; other memory may merge",
    ),
    (
        "KF-ANALYSIS-COPYRIGHT",
        "round10/portals/aletheia/pr_6_files/captures/2026-11-21-nichochar-knowledge-factories/analysis.md",
        87,
        "already lives on a public repository",
    ),
)


class PreregAuditError(ValueError):
    """Fail-closed refusal raised whenever any protocol, statistical, or governance invariant fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PreregAuditError(message)


def _require_exact_int(value: Any, name: str) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool), f"exact-int:{name}")
    return value


def _require_exact_bool(value: Any, name: str) -> bool:
    _require(isinstance(value, bool), f"exact-bool:{name}")
    return value


def _require_exact_fraction(value: Any, name: str) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Fraction(value, 1)
    raise PreregAuditError(f"exact-fraction:{name}")


def _require_exact_choice(value: Any, allowed: tuple[str, ...], name: str) -> str:
    _require(isinstance(value, str) and value in allowed, f"exact-choice:{name}")
    return value


def frac_str(value: Fraction) -> str:
    v = _require_exact_fraction(value, "frac_str")
    return f"{v.numerator}/{v.denominator}"


def frac_dec6(value: Fraction) -> str:
    """Exact truncated 6-decimal fixed-point string computed purely in integer arithmetic."""
    v = _require_exact_fraction(value, "frac_dec6")
    sign = "-" if v < 0 else ""
    av = abs(v)
    scaled = (av.numerator * 1_000_000) // av.denominator
    whole, rem = divmod(scaled, 1_000_000)
    return f"{sign}{whole}.{rem:06d}"


def binom_upper_tail(n: int, p: Fraction, k: int) -> Fraction:
    """Exact pure-Q upper tail P(Binomial(n, p) >= k)."""
    n_i = _require_exact_int(n, "n")
    k_i = _require_exact_int(k, "k")
    p_f = _require_exact_fraction(p, "p")
    _require(n_i >= 1, "binom-n-pos")
    _require(Fraction(0, 1) < p_f < Fraction(1, 1), "binom-p-open-unit")
    _require(0 <= k_i <= n_i + 1, "binom-k-range")
    q_f = Fraction(1, 1) - p_f
    total = Fraction(0, 1)
    for j in range(k_i, n_i + 1):
        total += Fraction(math.comb(n_i, j), 1) * (p_f**j) * (q_f ** (n_i - j))
    return total


def count_d3_ordinal_patterns(series: Sequence[Fraction | int], tau: int = 1) -> dict[str, Any]:
    """Exact d=3 ordinal pattern counter under PREREG.md:54 rank-by-position convention."""
    _require(isinstance(series, (list, tuple)) and len(series) >= 3, "d3-series-len")
    tau_i = _require_exact_int(tau, "tau")
    _require(tau_i >= 1 and 2 * tau_i < len(series), "d3-tau-range")
    vals = [_require_exact_fraction(x, f"series[{i}]") for i, x in enumerate(series)]
    counts = {k: 0 for k in ("012", "210", "021", "120", "102", "201")}
    ties = 0
    total_windows = len(vals) - 2 * tau_i
    for idx in range(total_windows):
        a, b, c = vals[idx], vals[idx + tau_i], vals[idx + 2 * tau_i]
        if a == b or b == c or a == c:
            ties += 1
            continue
        triple = (a, b, c)
        ranks = tuple(sum(1 for other in triple if other < item) for item in triple)
        counts[f"{ranks[0]}{ranks[1]}{ranks[2]}"] += 1
    return {
        "tau": tau_i,
        "total_windows": total_windows,
        "ties": ties,
        "valid_windows": total_windows - ties,
        "counts": counts,
    }


def end_match_cost_raw(segment: Sequence[Fraction | int]) -> Fraction:
    """Exact PREREG.md:163 end-matching objective (value jump^2 + slope jump^2)."""
    _require(isinstance(segment, (list, tuple)) and len(segment) >= 4, "end-match-len")
    v = [_require_exact_fraction(x, f"seg[{i}]") for i, x in enumerate(segment)]
    dj = v[-1] - v[0]
    ds = (v[1] - v[0]) - (v[-1] - v[-2])
    return dj * dj + ds * ds


def rank_transform_exact(block: Sequence[Fraction | int]) -> tuple[Fraction, ...]:
    """Mid-rank exact rational transform invariant under every strictly increasing map."""
    _require(isinstance(block, (list, tuple)) and len(block) >= 1, "rank-block-len")
    vals = [_require_exact_fraction(x, f"block[{i}]") for i, x in enumerate(block)]
    out: list[Fraction] = []
    for x in vals:
        less = sum(1 for y in vals if y < x)
        eq = sum(1 for y in vals if y == x)
        out.append(Fraction(2 * less + eq - 1, 2))
    return tuple(out)


def analyze_pillar1_control_power_and_holm() -> dict[str, Any]:
    """Pillar 1: Exact Holm thresholds, PREREG-01a C2/C3/C4 conjunction trap, and PREREG-01b K2 bound."""
    alpha_seg = Fraction(1, 20)
    holm_min = alpha_seg / 28  # 1/560

    # Presence thresholds (PREREG.md:188)
    s12_k4 = binom_upper_tail(12, alpha_seg, 4)
    s12_k5 = binom_upper_tail(12, alpha_seg, 5)
    s32_k6 = binom_upper_tail(32, alpha_seg, 6)
    s32_k7 = binom_upper_tail(32, alpha_seg, 7)

    # C2/C3/C4 conjunction trap (PREREG.md:150): K < K_1% AND K/S <= 1/10 -> fails at K >= floor(S/10) + 1
    s12_fail_10pct = binom_upper_tail(12, alpha_seg, 2)
    s12_inst3 = Fraction(1, 1) - (Fraction(1, 1) - s12_fail_10pct) ** 3
    s12_3inst = Fraction(1, 1) - (Fraction(1, 1) - s12_inst3) ** 3
    s12_4inst = Fraction(1, 1) - (Fraction(1, 1) - s12_inst3) ** 4

    s32_fail_10pct = binom_upper_tail(32, alpha_seg, 4)
    s32_inst3 = Fraction(1, 1) - (Fraction(1, 1) - s32_fail_10pct) ** 3
    s32_3inst = Fraction(1, 1) - (Fraction(1, 1) - s32_inst3) ** 3
    s32_4inst = Fraction(1, 1) - (Fraction(1, 1) - s32_inst3) ** 4

    # K2 noise bound (PREREG.md:210-211): n=200, threshold 0.086 -> fails at K >= 18
    k2_ge18 = binom_upper_tail(200, alpha_seg, 18)
    k2_ge19 = binom_upper_tail(200, alpha_seg, 19)
    k2_21_fwer_ge18 = Fraction(1, 1) - (Fraction(1, 1) - k2_ge18) ** 21
    k2_21_fwer_ge19 = Fraction(1, 1) - (Fraction(1, 1) - k2_ge19) ** 21

    return {
        "holm_min_threshold": frac_str(holm_min),
        "holm_min_dec6": frac_dec6(holm_min),
        "presence_thresholds_verified": {
            "S12_K4_tail_dec6": frac_dec6(s12_k4),
            "S12_K4_reaches_holm": s12_k4 <= holm_min,
            "S12_K5_tail_dec6": frac_dec6(s12_k5),
            "S12_K5_reaches_holm": s12_k5 <= holm_min,
            "S32_K6_tail_dec6": frac_dec6(s32_k6),
            "S32_K6_reaches_holm": s32_k6 <= holm_min,
            "S32_K7_tail_dec6": frac_dec6(s32_k7),
            "S32_K7_reaches_holm": s32_k7 <= holm_min,
        },
        "prereg01a_control_conjunction_trap": {
            "S12": {
                "binom_1pct_fail_k": 4,
                "binom_1pct_fail_prob_dec6": frac_dec6(s12_k4),
                "rate_cap_fail_k": 2,
                "rate_cap_fail_prob_dec6": frac_dec6(s12_fail_10pct),
                "inflation_ratio_dec6": frac_dec6(s12_fail_10pct / s12_k4),
                "per_instrument_3controls_false_invalid_dec6": frac_dec6(s12_inst3),
                "three_instruments_any_false_invalid_dec6": frac_dec6(s12_3inst),
                "four_instruments_any_false_invalid_dec6": frac_dec6(s12_4inst),
            },
            "S32": {
                "binom_1pct_fail_k": 6,
                "binom_1pct_fail_prob_dec6": frac_dec6(s32_k6),
                "rate_cap_fail_k": 4,
                "rate_cap_fail_prob_dec6": frac_dec6(s32_fail_10pct),
                "inflation_ratio_dec6": frac_dec6(s32_fail_10pct / s32_k6),
                "per_instrument_3controls_false_invalid_dec6": frac_dec6(s32_inst3),
                "three_instruments_any_false_invalid_dec6": frac_dec6(s32_3inst),
                "four_instruments_any_false_invalid_dec6": frac_dec6(s32_4inst),
            },
        },
        "prereg01b_k2_quantile_and_multiplicity": {
            "n_seeds": 200,
            "prereg_rate_threshold": "43/500",
            "prereg_fail_k": 18,
            "p_ge18_dec6": frac_dec6(k2_ge18),
            "p_ge18_le_1pct": k2_ge18 <= Fraction(1, 100),
            "true_1pct_fail_k": 19,
            "p_ge19_dec6": frac_dec6(k2_ge19),
            "p_ge19_le_1pct": k2_ge19 <= Fraction(1, 100),
            "num_noise_classes": 21,
            "fwer_21_classes_at_k18_dec6": frac_dec6(k2_21_fwer_ge18),
            "fwer_21_classes_at_k19_dec6": frac_dec6(k2_21_fwer_ge19),
        },
    }


def analyze_pillar2_ordinal_symmetry_and_offset_leakage() -> dict[str, Any]:
    """Pillar 2: Burnside S_4/V_4 orbit proof, PREREG-02 R o P u=0 theorem, PREREG-03 offset leakage."""
    # Exact Burnside enumeration of S_4 under V_4 = {I, R, P, R o P}
    perms = list(itertools.permutations(range(4)))
    visited: set[tuple[int, ...]] = set()
    orbit_sizes: list[int] = []
    for perm in perms:
        if perm in visited:
            continue
        rev_p = perm[::-1]
        pol_p = tuple(3 - x for x in perm)
        rp_p = pol_p[::-1]
        orb = {perm, rev_p, pol_p, rp_p}
        visited |= orb
        orbit_sizes.append(len(orb))
    orbit_sizes.sort()

    # PREREG-02: Sawtooth (period 16, 16 cycles = 256 samples) & periodic exponential-like geometric decay
    # (period 16, 16 cycles = 256 samples; using exact strictly decreasing integer heights 16..1 -> identical ordinal patterns!)
    sawtooth = [15 - (t % 16) for t in range(256)]
    saw_by_tau = []
    for tau in (1, 2, 4, 8):
        res = count_d3_ordinal_patterns(sawtooth, tau=tau)
        c = res["counts"]
        u_zero = (c["021"] == c["102"]) and (c["120"] == c["201"])
        saw_by_tau.append(
            {
                "tau": tau,
                "n_012": c["012"],
                "n_210": c["210"],
                "n_021": c["021"],
                "n_120": c["120"],
                "n_102": c["102"],
                "n_201": c["201"],
                "ties": res["ties"],
                "u_equals_zero_identically": u_zero,
            }
        )

    # Time-reversed sawtooth (Synthetic C analogy): verify exact swap (012<->210, 021<->120, 102<->201)
    # and exact invariance of time-even magnitudes |a1| and |a2 + a3| via count-ratio reciprocals!
    saw_rev = list(reversed(sawtooth))
    c_fwd = count_d3_ordinal_patterns(sawtooth, tau=1)["counts"]
    c_rev = count_d3_ordinal_patterns(saw_rev, tau=1)["counts"]
    rev_swaps_exact = (
        c_fwd["012"] == c_rev["210"]
        and c_fwd["210"] == c_rev["012"]
        and c_fwd["021"] == c_rev["120"]
        and c_fwd["120"] == c_rev["021"]
        and c_fwd["102"] == c_rev["201"]
        and c_fwd["201"] == c_rev["102"]
    )
    # R o P (180-deg rotation: reversed AND polarity-flipped) leaves sawtooth counts 100% IDENTICAL!
    saw_rp = [-x for x in saw_rev]
    c_rp = count_d3_ordinal_patterns(saw_rp, tau=1)["counts"]

    # PREREG-03: End-matching offset selection leakage under K1 monotone map f(x) = x^3 + x
    block = (10, 10, 0, 1, 11, 11, 2, 2)
    mapped_block = tuple(x * x * x + x for x in block)
    n_seg = 6
    raw_costs = [end_match_cost_raw(block[o : o + n_seg]) for o in range(len(block) - n_seg + 1)]
    mapped_costs = [
        end_match_cost_raw(mapped_block[o : o + n_seg]) for o in range(len(mapped_block) - n_seg + 1)
    ]
    raw_best_o = raw_costs.index(min(raw_costs))
    mapped_best_o = mapped_costs.index(min(mapped_costs))

    # Rank-transformed fix restores 100% exact invariance under EVERY strictly increasing map!
    rank_raw = rank_transform_exact(block)
    rank_mapped = rank_transform_exact(mapped_block)
    rank_costs_raw = [end_match_cost_raw(rank_raw[o : o + n_seg]) for o in range(len(block) - n_seg + 1)]
    rank_costs_mapped = [
        end_match_cost_raw(rank_mapped[o : o + n_seg]) for o in range(len(block) - n_seg + 1)
    ]
    rank_best_raw = rank_costs_raw.index(min(rank_costs_raw))
    rank_best_mapped = rank_costs_mapped.index(min(rank_costs_mapped))

    return {
        "burnside_s4_v4_orbits": {
            "num_orbits": len(orbit_sizes),
            "orbit_sizes": orbit_sizes,
            "matches_prereg_l105_eight_classes": len(orbit_sizes) == 8,
            "simplex_dof_per_level": len(orbit_sizes) - 1,
        },
        "prereg02_rp_symmetry_obstruction": {
            "sawtooth_period": 16,
            "sawtooth_by_tau": saw_by_tau,
            "all_lags_u_zero": all(row["u_equals_zero_identically"] for row in saw_by_tau),
            "time_reversal_swaps_counts_exact": rev_swaps_exact,
            "rp_rotation_preserves_all_six_counts_exact": c_rp == c_fwd,
            "time_even_feature_fraction": "2/3",
        },
        "prereg03_end_match_offset_leakage": {
            "block": list(block),
            "mapped_block_x3_plus_x": list(mapped_block),
            "raw_costs": [frac_str(x) for x in raw_costs],
            "raw_best_offset": raw_best_o,
            "mapped_costs": [frac_str(x) for x in mapped_costs],
            "mapped_best_offset": mapped_best_o,
            "monotone_map_changes_selected_offset": raw_best_o != mapped_best_o,
            "rank_costs_raw": [frac_str(x) for x in rank_costs_raw],
            "rank_costs_mapped": [frac_str(x) for x in rank_costs_mapped],
            "rank_best_offset_raw": rank_best_raw,
            "rank_best_offset_mapped": rank_best_mapped,
            "rank_fix_restores_exact_invariance": (
                rank_costs_raw == rank_costs_mapped and rank_best_raw == rank_best_mapped
            ),
        },
    }


def analyze_pillar3_data_budgets_and_scale_flow() -> dict[str, Any]:
    """Pillar 3: DATA_REQUEST byte accounting, PREREG-04 scale-flow starvation, ARM_B rung budgets."""
    gw_bytes = (130_158_262, 125_865_927, 69_367_295, 128_039_935)
    seis_bytes = (6_480_384, 5_137_920, 7_340_032, 5_035_008)
    waves_fit = (8_049_179, 8_286_263, 8_806_252, 6_401_232, 8_192_307, 8_270_051, 8_330_045, 8_465_653)
    waves_ver = (8_861_501, 8_602_397, 8_823_131, 8_727_663, 8_782_498, 8_815_711, 9_109_882, 7_398_658)
    tess_bytes = (11_566_080, 12_081_600)

    sum_waves_fit = sum(waves_fit)
    sum_waves_ver = sum(waves_ver)
    total_bytes = sum(gw_bytes) + sum(seis_bytes) + sum_waves_fit + sum_waves_ver + sum(tess_bytes)
    drop_l1_fit = total_bytes - gw_bytes[1]

    block_len = 4096 + 128  # 4224 samples per PREREG.md:161
    min_blocks = 12  # PREREG.md:104, 141
    instruments = (
        ("GW_4096s_4096Hz", 16_777_216),
        ("SEIS_VBB_1day_20Hz", 1_728_003),
        ("TESS_27d_20s_nogap_upper_bound", 116_640),
        ("WAVES_8d_4ch_60s_cadence", 46_080),
        ("WAVES_8d_4ch_192s_cadence", 14_400),
    )
    scale_rows = []
    for name, n_samples in instruments:
        blocks_l0 = n_samples // block_len
        max_level = -1
        for lvl in range(12):
            if (n_samples // (2**lvl)) // block_len >= min_blocks:
                max_level = lvl
        populated_of_7 = min(7, max_level + 1)
        zero_padded_features = (7 - populated_of_7) * 8
        scale_rows.append(
            {
                "instrument_case": name,
                "samples": n_samples,
                "blocks_level0": blocks_l0,
                "max_scale_flow_level": max_level,
                "populated_aligned_levels_max": populated_of_7,
                "min_zero_padded_t1_features_of_56": zero_padded_features,
            }
        )

    # Exact maximum average cadence (seconds) for 4 pooled Wind/WAVES channels over 8 days (691,200 s)
    # to yield >= 12 complete blocks of 4,224 samples
    waves_max_cadence_sec = Fraction(8 * 86_400 * 4, min_blocks * block_len)  # 600/11 s

    # ARM_B_OUTLINE.md:14 exact finite-sample rung capacities (50 windows per pattern)
    arm_b_rungs = []
    for d in (3, 4, 5, 6):
        n_pat = math.factorial(d)
        min_win_pat = 50 * n_pat
        min_win_markov_edge = 50 * n_pat * d  # at least d outgoing transitions per d-pattern
        arm_b_rungs.append(
            {
                "order_d": d,
                "num_patterns": n_pat,
                "min_windows_50_per_pattern": min_win_pat,
                "fits_single_4096_segment": min_win_pat <= 4096,
                "min_windows_50_per_transition_edge": min_win_markov_edge,
                "fits_32_pooled_fit_segments_131072": min_win_markov_edge <= 32 * 4096,
            }
        )

    return {
        "data_request_byte_sums": {
            "waves_fit_bytes": sum_waves_fit,
            "waves_fit_matches_claimed": sum_waves_fit == 64_800_982,
            "waves_verdict_bytes": sum_waves_ver,
            "waves_verdict_matches_claimed": sum_waves_ver == 69_121_441,
            "total_bytes": total_bytes,
            "total_matches_claimed": total_bytes == 634_994_866,
            "drop_l1_fit_bytes": drop_l1_fit,
            "drop_l1_fit_matches_claimed": drop_l1_fit == 509_128_939,
        },
        "scale_flow_sample_budgets": scale_rows,
        "waves_max_avg_cadence_for_12_blocks_sec": frac_str(waves_max_cadence_sec),
        "waves_max_avg_cadence_dec6": frac_dec6(waves_max_cadence_sec),
        "arm_b_finite_sample_rungs": arm_b_rungs,
    }


def certify_prereg_protocol(spec: Any) -> dict[str, Any]:
    """Fail-closed pure-Q Pre-Registration Protocol & Surrogate-Control Certifier."""
    _require(isinstance(spec, dict), "prereg-spec-dict")
    unknown = sorted(set(spec.keys()) - ALLOWED_PREREG_KEYS)
    _require(len(unknown) == 0, f"prereg-unknown-keys:{','.join(unknown)}")
    missing = sorted(ALLOWED_PREREG_KEYS - set(spec.keys()))
    _require(len(missing) == 0, f"prereg-missing-keys:{','.join(missing)}")

    s_seg = _require_exact_int(spec["segments_per_instrument"], "segments_per_instrument")
    _require(s_seg >= 1, "prereg-segments-pos")
    alpha_seg = _require_exact_fraction(spec["segment_alpha"], "segment_alpha")
    _require(Fraction(0, 1) < alpha_seg < Fraction(1, 1), "prereg-alpha-range")
    k_lim = _require_exact_int(spec["control_k_limit"], "control_k_limit")
    _require(1 <= k_lim <= s_seg, "prereg-k-limit-range")
    rate_cap = _require_exact_fraction(spec["control_rate_cap"], "control_rate_cap")
    _require(Fraction(0, 1) < rate_cap < Fraction(1, 1), "prereg-rate-cap-range")
    combine = _require_exact_choice(spec["control_combine_mode"], ALLOWED_COMBINE_MODES, "control_combine_mode")
    n_ctrl = _require_exact_int(spec["num_controls_per_instrument"], "num_controls_per_instrument")
    _require(n_ctrl >= 1, "prereg-num-controls-pos")
    n_inst = _require_exact_int(spec["calibrated_instruments"], "calibrated_instruments")
    _require(n_inst >= 1, "prereg-num-instruments-pos")
    quorum = _require_exact_int(spec["required_support_quorum"], "required_support_quorum")
    _require(quorum >= 1, "prereg-quorum-pos")
    max_false_inv = _require_exact_fraction(
        spec["max_per_instrument_false_invalid"], "max_per_instrument_false_invalid"
    )
    _require(Fraction(0, 1) < max_false_inv < Fraction(1, 1), "prereg-max-false-inv-range")
    rank_end = _require_exact_bool(spec["rank_end_matching"], "rank_end_matching")
    split_odd = _require_exact_bool(spec["split_time_odd_transfer"], "split_time_odd_transfer")
    joint_perm = _require_exact_bool(
        spec["restrict_perm_to_joint_support"], "restrict_perm_to_joint_support"
    )
    k2_seeds = _require_exact_int(spec["k2_seeds"], "k2_seeds")
    _require(k2_seeds >= 1, "prereg-k2-seeds-pos")
    k2_max_rej = _require_exact_int(spec["k2_max_rejects"], "k2_max_rejects")
    _require(0 <= k2_max_rej < k2_seeds, "prereg-k2-max-rej-range")
    k2_classes = _require_exact_int(spec["k2_num_classes"], "k2_num_classes")
    _require(k2_classes >= 1, "prereg-k2-classes-pos")
    max_k2_alpha = _require_exact_fraction(spec["max_k2_per_class_alpha"], "max_k2_per_class_alpha")
    _require(Fraction(0, 1) < max_k2_alpha < Fraction(1, 1), "prereg-max-k2-alpha-range")

    # Effective control failure threshold K_fail (control FAILS when K >= K_fail)
    # Under "and": passes iff K < k_lim AND K/S <= rate_cap => fails at min(k_lim, floor(S*rate_cap)+1)
    # Under "or":  passes iff K < k_lim OR  K/S <= rate_cap => fails at max(k_lim, floor(S*rate_cap)+1)
    # Under "binom_only": passes iff K < k_lim => fails at k_lim
    rate_fail_k = (s_seg * rate_cap.numerator) // rate_cap.denominator + 1
    if combine == "and":
        eff_fail_k = min(k_lim, rate_fail_k)
    elif combine == "or":
        eff_fail_k = max(k_lim, rate_fail_k)
    else:
        eff_fail_k = k_lim

    p_ctrl_fail = binom_upper_tail(s_seg, alpha_seg, eff_fail_k)
    p_inst_false_inv = Fraction(1, 1) - (Fraction(1, 1) - p_ctrl_fail) ** n_ctrl
    p_any_inst_false_inv = Fraction(1, 1) - (Fraction(1, 1) - p_inst_false_inv) ** n_inst

    p_k2_class_fail = binom_upper_tail(k2_seeds, alpha_seg, k2_max_rej + 1)
    p_k2_fwer = Fraction(1, 1) - (Fraction(1, 1) - p_k2_class_fail) ** k2_classes
    min_reachable_presence_p = alpha_seg**s_seg

    violations: list[str] = []
    if 2 * (eff_fail_k - 1) >= s_seg:
        violations.append("PREREG01_VACUOUS_CONTROL_THRESHOLD")
    if p_inst_false_inv > max_false_inv:
        violations.append("PREREG01_EXCESS_CONTROL_FALSE_INVALIDATION")
    if p_any_inst_false_inv > MAX_EXPERIMENT_FALSE_INVALID:
        violations.append("PREREG01_EXPERIMENT_FALSE_INVALID_EXCEEDED")
    if 4 * k2_max_rej >= k2_seeds:
        violations.append("PREREG01B_VACUOUS_K2_THRESHOLD")
    if p_k2_class_fail > max_k2_alpha:
        violations.append("PREREG01B_K2_PER_CLASS_ALPHA_EXCEEDED")
    if p_k2_fwer > MAX_K2_FWER:
        violations.append("PREREG01B_K2_FWER_EXCEEDED")
    if not split_odd:
        violations.append("PREREG02_TIME_EVEN_TRANSFER_DILUTION")
    if not rank_end:
        violations.append("PREREG03_RAW_END_MATCH_MONOTONE_LEAKAGE")
    if not joint_perm:
        violations.append("PREREG04_ZERO_PADDED_PERM_DILUTION")
    if n_inst < quorum:
        violations.append("PREREG04_INSUFFICIENT_INSTRUMENT_QUORUM")
    if min_reachable_presence_p > HOLM_MIN_THRESHOLD:
        violations.append("PREREG04_ZERO_HOLM_PRESENCE_POWER")

    return {
        "certified": len(violations) == 0,
        "violations": violations,
        "effective_control_fail_k": eff_fail_k,
        "single_control_false_fail_dec6": frac_dec6(p_ctrl_fail),
        "per_instrument_false_invalid_dec6": frac_dec6(p_inst_false_inv),
        "experiment_any_false_invalid_dec6": frac_dec6(p_any_inst_false_inv),
        "k2_per_class_fail_dec6": frac_dec6(p_k2_class_fail),
        "k2_fwer_dec6": frac_dec6(p_k2_fwer),
        "min_reachable_presence_p_reaches_holm": min_reachable_presence_p <= HOLM_MIN_THRESHOLD,
    }


def certify_knowledge_factory_promotion(proposal: Any) -> dict[str, Any]:
    """Unified fail-closed Knowledge-Factory Governor synthesizing aletheia#6 + AUDIT-076R (KF-01..05)."""
    _require(isinstance(proposal, dict), "kf-proposal-dict")
    unknown = sorted(set(proposal.keys()) - ALLOWED_KF_KEYS)
    _require(len(unknown) == 0, f"kf-unknown-keys:{','.join(unknown)}")
    missing = sorted(ALLOWED_KF_KEYS - set(proposal.keys()))
    _require(len(missing) == 0, f"kf-missing-keys:{','.join(missing)}")

    actor = _require_exact_choice(proposal["actor_role"], ALLOWED_ACTOR_ROLES, "actor_role")
    reviewer = _require_exact_choice(proposal["reviewer_role"], ALLOWED_REVIEWER_ROLES, "reviewer_role")
    layer = _require_exact_choice(proposal["target_layer"], ALLOWED_TARGET_LAYERS, "target_layer")
    src_int = _require_exact_int(proposal["source_integrity"], "source_integrity")
    req_int = _require_exact_int(proposal["target_required_integrity"], "target_required_integrity")
    src_conf = _require_exact_int(proposal["source_confidentiality"], "source_confidentiality")
    max_conf = _require_exact_int(proposal["target_max_confidentiality"], "target_max_confidentiality")
    _require(0 <= src_int <= 4 and 0 <= req_int <= 4, "kf-integrity-range")
    _require(0 <= src_conf <= 3 and 0 <= max_conf <= 3, "kf-conf-range")
    _require(req_int >= LAYER_MIN_INTEGRITY[layer], "kf-layer-integrity-floor")
    _require(max_conf <= LAYER_MAX_CONFIDENTIALITY[layer], "kf-layer-conf-ceiling")
    signoff = _require_exact_bool(proposal["human_signoff"], "human_signoff")
    out_before = _require_exact_fraction(proposal["outside_err_before"], "outside_err_before")
    out_after = _require_exact_fraction(proposal["outside_err_after"], "outside_err_after")
    prx_before = _require_exact_fraction(proposal["proxy_err_before"], "proxy_err_before")
    prx_after = _require_exact_fraction(proposal["proxy_err_after"], "proxy_err_after")
    _require(out_before >= 0 and out_after >= 0 and prx_before >= 0 and prx_after >= 0, "kf-err-nonneg")
    store_epoch = _require_exact_int(proposal["store_epoch"], "store_epoch")
    loaded_epoch = _require_exact_int(proposal["butler_loaded_epoch"], "butler_loaded_epoch")
    _require(store_epoch >= 1 and 1 <= loaded_epoch <= store_epoch, "kf-epoch-range")
    nudge_sent = _require_exact_bool(proposal["in_flight_nudge_sent"], "in_flight_nudge_sent")

    violations: list[str] = []
    # Charriere gardener-only write policy
    if actor != "gardener":
        violations.append("KF00_BUTLER_DIRECT_WRITE_FORBIDDEN")
    # KF-05: independent reviewer separation (gardener cannot self-approve)
    if reviewer == actor:
        violations.append("KF05_CURATOR_SELF_APPROVAL_FORBIDDEN")
    # KF-01: Biba integrity & BLP confidentiality lattice
    if src_int < req_int:
        violations.append("KF01_BIBA_INTEGRITY_ESCALATION")
    if src_conf > max_conf:
        violations.append("KF01_BLP_CONFIDENTIALITY_LEAK")
    # KF-02: Frozen outside-anchor Goodhart latch + proxy non-regression
    if out_after > out_before:
        violations.append("KF02_GOODHART_OUTSIDE_ANCHOR_DRIFT")
    if prx_after > prx_before:
        violations.append("KF02_PROXY_REGRESSION")
    # KF-03d: Lenton in-flight stale-skill read guard
    if loaded_epoch < store_epoch and not nudge_sent:
        violations.append("KF03D_INFLIGHT_STALE_READ_UNNOTIFIED")
    # KF-04: Close aletheia#6 analysis.md:33,61 auto-merge loophole — skills, data_access_guidance,
    # AND domain_knowledge ALL require human sign-off (only ephemeral_memory may auto-merge!)
    if layer != "ephemeral_memory" and not signoff:
        violations.append("KF04_HIGH_IMPACT_LAYER_REQUIRES_SIGNOFF")

    return {
        "admitted": len(violations) == 0,
        "violations": violations,
        "actor_role": actor,
        "reviewer_role": reviewer,
        "target_layer": layer,
    }


def analyze_pillar4_certifiers_and_kf_cross_audit() -> dict[str, Any]:
    """Pillar 4: Certified before/after PREREG runs + aletheia#6 vs AUDIT-076R cross-audit receipts."""
    # 1. Exact PREREG.md as written (S=32) -> FAILS 5 defects!
    prereg_as_written = certify_prereg_protocol(
        {
            "segments_per_instrument": 32,
            "segment_alpha": Fraction(1, 20),
            "control_k_limit": 6,
            "control_rate_cap": Fraction(1, 10),
            "control_combine_mode": "and",
            "num_controls_per_instrument": 3,
            "calibrated_instruments": 3,
            "required_support_quorum": 3,
            "max_per_instrument_false_invalid": Fraction(1, 20),
            "rank_end_matching": False,
            "split_time_odd_transfer": False,
            "restrict_perm_to_joint_support": False,
            "k2_seeds": 200,
            "k2_max_rejects": 17,
            "k2_num_classes": 21,
            "max_k2_per_class_alpha": Fraction(1, 100),
        }
    )

    # 2. Hardened pre-data amended PREREG -> CERTIFIED (0 violations, FWER < 10%, non-vacuous, Holm-powered)!
    prereg_hardened = certify_prereg_protocol(
        {
            "segments_per_instrument": 32,
            "segment_alpha": Fraction(1, 20),
            "control_k_limit": 6,
            "control_rate_cap": Fraction(1, 10),
            "control_combine_mode": "binom_only",
            "num_controls_per_instrument": 3,
            "calibrated_instruments": 4,
            "required_support_quorum": 3,
            "max_per_instrument_false_invalid": Fraction(1, 20),
            "rank_end_matching": True,
            "split_time_odd_transfer": True,
            "restrict_perm_to_joint_support": True,
            "k2_seeds": 200,
            "k2_max_rejects": 20,
            "k2_num_classes": 21,
            "max_k2_per_class_alpha": Fraction(1, 100),
        }
    )

    # 3. Knowledge Factory cross-audit: aletheia#6 analysis.md:33,61 auto-merge loophole on data_access_guidance
    kf_automerge_loophole = certify_knowledge_factory_promotion(
        {
            "actor_role": "gardener",
            "reviewer_role": "independent_reviewer",
            "target_layer": "data_access_guidance",
            "source_integrity": 3,
            "target_required_integrity": 3,
            "source_confidentiality": 0,
            "target_max_confidentiality": 0,
            "human_signoff": False,
            "outside_err_before": Fraction(1, 4),
            "outside_err_after": Fraction(1, 4),
            "proxy_err_before": Fraction(1, 1),
            "proxy_err_after": Fraction(3, 4),
            "store_epoch": 2,
            "butler_loaded_epoch": 1,
            "in_flight_nudge_sent": False,
        }
    )

    # 4. Knowledge Factory hardened admission (gardener + independent reviewer + sign-off + nudge + Biba/BLP + Goodhart OK)
    kf_hardened_admitted = certify_knowledge_factory_promotion(
        {
            "actor_role": "gardener",
            "reviewer_role": "independent_reviewer",
            "target_layer": "data_access_guidance",
            "source_integrity": 3,
            "target_required_integrity": 3,
            "source_confidentiality": 0,
            "target_max_confidentiality": 0,
            "human_signoff": True,
            "outside_err_before": Fraction(1, 4),
            "outside_err_after": Fraction(1, 5),
            "proxy_err_before": Fraction(1, 1),
            "proxy_err_after": Fraction(3, 4),
            "store_epoch": 2,
            "butler_loaded_epoch": 1,
            "in_flight_nudge_sent": True,
        }
    )

    # 5. AUDIT-076R exact blast-radius & Goodhart constants cross-referenced
    blast_prob = Fraction(1, 1) - Fraction(19, 20) ** 120

    return {
        "prereg_certifier_as_written": prereg_as_written,
        "prereg_certifier_hardened": prereg_hardened,
        "kf_cross_audit_automerge_loophole_and_lenton": kf_automerge_loophole,
        "kf_cross_audit_hardened_admitted": kf_hardened_admitted,
        "audit_076r_blast_radius_ge1_dec6": frac_dec6(blast_prob),
    }


def _sha256_file(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def audit_live_portals(symbiosis_root: Path) -> dict[str, Any]:
    """Read-only SHA-256 and verbatim file:line verification of pinned Round 10 Arm R10-4 portals."""
    _require(symbiosis_root.is_dir(), f"symbiosis-root-missing:{symbiosis_root.name}")
    root_resolved = symbiosis_root.resolve()
    digest_results: dict[str, dict[str, Any]] = {}
    for rel_path, expected in PINNED_PORTAL_DIGESTS.items():
        full_path = (root_resolved / rel_path).resolve()
        _require(full_path.is_relative_to(root_resolved), f"portal-path-escape:{rel_path}")
        _require(full_path.is_file(), f"portal-file-missing:{rel_path}")
        actual_bytes, actual_sha = _sha256_file(full_path)
        _require(actual_bytes == expected["bytes"], f"portal-bytes-mismatch:{rel_path}")
        _require(actual_sha == expected["sha256"], f"portal-sha256-mismatch:{rel_path}")
        digest_results[rel_path] = {"bytes": actual_bytes, "sha256": actual_sha, "verified": True}

    anchor_results: list[dict[str, Any]] = []
    for anchor_id, rel_path, line_no, needle in VERBATIM_ANCHORS:
        lines = (root_resolved / rel_path).read_text(encoding="utf-8").splitlines()
        _require(1 <= line_no <= len(lines), f"anchor-line-range:{anchor_id}")
        _require(needle in lines[line_no - 1], f"anchor-text-mismatch:{anchor_id}")
        anchor_results.append(
            {"anchor_id": anchor_id, "file": rel_path, "line": line_no, "verified": True}
        )

    return {
        "mode": "live_read_only",
        "pinned_cave_pr6_commit": PINNED_CAVE_PR6_COMMIT,
        "pinned_aletheia_pr6_commit": PINNED_ALETHEIA_PR6_COMMIT,
        "verified_files": len(digest_results),
        "verified_anchors": len(anchor_results),
        "file_digests": digest_results,
        "anchors": anchor_results,
    }


def build_certificate(symbiosis_root: Path | None = None) -> dict[str, Any]:
    """Build deterministic zero-float JSON certificate with canonical SHA-256."""
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "pinned_cave_pr6_commit": PINNED_CAVE_PR6_COMMIT,
        "pinned_aletheia_pr6_commit": PINNED_ALETHEIA_PR6_COMMIT,
        "pillar1_control_power_and_holm": analyze_pillar1_control_power_and_holm(),
        "pillar2_ordinal_symmetry_and_offset_leakage": analyze_pillar2_ordinal_symmetry_and_offset_leakage(),
        "pillar3_data_budgets_and_scale_flow": analyze_pillar3_data_budgets_and_scale_flow(),
        "pillar4_certifiers_and_kf_cross_audit": analyze_pillar4_certifiers_and_kf_cross_audit(),
        "live_portal_verification": (
            audit_live_portals(symbiosis_root)
            if symbiosis_root is not None
            else {"mode": "standalone_pure_q", "verified_files": 0, "verified_anchors": 0}
        ),
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    body["certificate_sha256"] = hashlib.sha256(canonical.encode("ascii")).hexdigest()
    return body


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Round 10 Arm R10-4 pre-registration & KF certifier.")
    parser.add_argument("--symbiosis-root", type=Path, default=None, help="Staged read-only symbiosis root.")
    parser.add_argument("--json", action="store_true", help="Emit canonical JSON to stdout.")
    parser.add_argument("--write-cert", type=Path, default=None, help="Write JSON certificate path.")
    args = parser.parse_args(argv)

    cert = build_certificate(symbiosis_root=args.symbiosis_root)
    rendered = json.dumps(cert, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if args.write_cert is not None:
        args.write_cert.write_text(rendered, encoding="utf-8")
    if args.json:
        sys.stdout.write(rendered)
    else:
        lv = cert["live_portal_verification"]
        sys.stdout.write(
            f"{AUDIT_ID} | mode={lv['mode']} | files={lv['verified_files']} "
            f"| anchors={lv['verified_anchors']} | sha256={cert['certificate_sha256']}\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
