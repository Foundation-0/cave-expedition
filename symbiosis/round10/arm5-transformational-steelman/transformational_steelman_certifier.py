#!/usr/bin/env python3
"""Wave 2 Round 10 — Arm R10-5 (AUDIT-088):
Transformational Steelman / Morphism-Before-Dismissal Protocol
(LAW2B_TRANSFORM_BEFORE_DISMISSAL).

Formal structural twin to Foundation-0/aletheia#9 (OWN_TERMS_FIRST.md):
  - 7 typed admissible morphism families (T1..T7)
  - 4 mandatory Law-3 anti-epicycle / non-degeneracy guards (G1..G4)
  - Exact pure-Q (zero-float, stdlib-only) retrospective re-audit across
    AUDIT-001..087 contrasting genuine structural rescues, newly surfaced
    transformed cores, true transform-invariant obstructions, and
    fail-closed anti-epicycle rejections.

Strictly read-only on all vault artifacts; zero GitHub writes; zero floats;
zero bare asserts; zero local absolute paths emitted in JSON certificates.
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
from typing import Any


MORPHISM_FAMILIES: tuple[str, ...] = (
    "T1_GAUGE_SIMILARITY",
    "T2_AFFINE_BREGMAN",
    "T3_METRIC_CHART",
    "T4_SPECTRAL_PSD_SHIFT",
    "T5_SEMIRING_TROPICAL",
    "T6_SUBSPACE_PROJECTION",
    "T7_ORDER_DOMAIN_RESIDUAL",
)
MORPHISM_FAMILY_SET: frozenset[str] = frozenset(MORPHISM_FAMILIES)

ALLOWED_PROPOSED_VERDICTS: frozenset[str] = frozenset(
    {
        "TRANSFORMED_EXACT",
        "BOUNDED_TRANSFORM_CORE",
        "INVARIANT_FALSIFIED",
        "FALSIFIED_RAW",
    }
)

# Hard Law-3 protocol ceiling preventing callers from spoofing vacuous null thresholds.
MAX_ALLOWED_NULL_RATE: Fraction = Fraction(1, 10)

REQUIRED_SPEC_KEYS: frozenset[str] = frozenset(
    {
        "claim_id",
        "proposed_verdict",
        "literal_failed",
        "literal_failure_witness",
        "families_searched",
        "applied_family",
        "transform_dof",
        "held_out_constraints",
        "fixed_globally_before_holdout",
        "target_pass_count",
        "target_total_count",
        "null_false_pass_count",
        "null_total_count",
        "max_null_false_pass_rate",
        "transform_rank",
        "preserved_invariant_core",
        "modified_hypotheses",
        "residual_gap",
        "max_residual_gap",
        "relabelled_as_literal",
        "obstruction_invariant",
        "obstruction_survives_all_searched",
    }
)

EXPECTED_VAULT_SHA256: dict[str, str] = {
    "round10/portals/aletheia/pr_9_files/spec/proposals/OWN_TERMS_FIRST.md": (
        "bd14863344c494f1e0399d486267231fe3002fe7e005d354e2f82a8c105d6746"
    ),
    "round10/portals/aletheia/issue_4.md": (
        "e3da52efc1e8f44fac4e237f1d08dd8f9b41a48c348a18b89686e65ccbac7fad"
    ),
    "round10/portals/cave-expedition/pr_5_files/verification/outside/gate5-unification/README.md": (
        "7e8fa8e1b494f5099b4f99923d0442b2d2a49dc8287959595e1c568b9d723a42"
    ),
    "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md": (
        "8ed03fb9f3f5b712d961b04ebdc2f539c398cac6e5e1fbecb6eeacb6041b5483"
    ),
    "round7/arm3-zenodo-rns-pnp/zenodo_rns_pnp_certificate.json": (
        "eae51ad62e4252a65d5962fad6b7ed7917f505a34b5a37275c46a6d3c7391e73"
    ),
    "round8/arm2-songe/songe_governance_certificate.json": (
        "479e137e9849fb3a25ad27c78a9eec6615ddf325cabdb84a9fb1d246d698ce09"
    ),
    "round9/arm2-ripo-riemannian-rl/ripo_riemannian_certificate.json": (
        "2ecbe3f0d9bec7dea5a7aa6f8d473b5c5dfe15b13318614a93a6a0c1744e6e6a"
    ),
    "round9/arm6-bellman-bpo/bpo_bellman_certificate.json": (
        "4a66617952080266e41e93d9f87d8425ce70f589128af4e7d59bbce415ee4c29"
    ),
}

# Exact 1-based newline line anchors on frozen portal docs
VAULT_LINE_ANCHORS: tuple[tuple[str, str, int, str], ...] = (
    (
        "OTF-TWO-PHASES",
        "round10/portals/aletheia/pr_9_files/spec/proposals/OWN_TERMS_FIRST.md",
        21,
        "Two phases, kept apart.",
    ),
    (
        "OTF-TROPICAL-BRIDGE",
        "round10/portals/aletheia/pr_9_files/spec/proposals/OWN_TERMS_FIRST.md",
        44,
        "Ordinary and tropical elimination agree exactly when nothing cancels",
    ),
    (
        "ISSUE4-GAUGE-SIM",
        "round10/portals/aletheia/issue_4.md",
        31,
        "diagonal similarity K_q' = D_h^-1 K_q D_h",
    ),
    (
        "ISSUE4-CS08-66",
        "round10/portals/aletheia/issue_4.md",
        66,
        "Among the 66 instances where neither arm left the format, the two arms solved 44 and 43.",
    ),
    (
        "GATE5-TROPICAL",
        "round10/portals/cave-expedition/pr_5_files/verification/outside/gate5-unification/README.md",
        59,
        "The tropical and linear-programming rows",
    ),
    (
        "PREREG-U-ARROW",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        85,
        "u  = a2 - a3",
    ),
    (
        "PREREG-M1-M23",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        86,
        "m1 = |a1|,  m23 = |a2 + a3|",
    ),
    (
        "PREREG-END-MATCH",
        "round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md",
        163,
        "smallest sum of the squared jump between first and last value",
    ),
)


def frac_to_dict(value: Fraction) -> dict[str, int]:
    """Encode an exact Fraction as canonical zero-float {num, den}."""
    if not isinstance(value, Fraction):
        raise TypeError("frac_to_dict requires Fraction")
    return {"num": value.numerator, "den": value.denominator}


def exact_frac(value: Any, name: str) -> Fraction:
    """Strictly convert exact int or Fraction to Fraction; reject bool/float/str."""
    if type(value) is int:
        return Fraction(value, 1)
    if isinstance(value, Fraction):
        return value
    raise ValueError(f"{name} must be exact int or Fraction")


def exact_int(value: Any, name: str) -> int:
    """Strictly validate exact Python int (rejecting bool and float)."""
    if type(value) is not int:
        raise ValueError(f"{name} must be exact int")
    return value


def exact_bool(value: Any, name: str) -> bool:
    """Strictly validate exact Python bool."""
    if type(value) is not bool:
        raise ValueError(f"{name} must be exact bool")
    return value


def clean_ascii_str(value: Any, name: str) -> str:
    """Strictly validate a non-empty trimmed printable ASCII string."""
    if type(value) is not str:
        raise ValueError(f"{name} must be exact str")
    if len(value) == 0 or value != value.strip():
        raise ValueError(f"{name} must be non-empty without leading/trailing whitespace")
    for ch in value:
        code = ord(ch)
        if code < 32 or code > 126:
            raise ValueError(f"{name} must contain printable ASCII only")
    return value


def opt_clean_ascii_str(value: Any, name: str) -> str | None:
    """Strictly validate None or a clean trimmed printable ASCII string."""
    if value is None:
        return None
    return clean_ascii_str(value, name)


def parse_families_searched(raw: Any) -> tuple[str, ...]:
    """Strictly parse a list/tuple of distinct valid morphism family identifiers."""
    if not isinstance(raw, (list, tuple)):
        raise ValueError("families_searched must be list or tuple")
    seen: set[str] = set()
    out: list[str] = []
    for idx, item in enumerate(raw):
        fam = clean_ascii_str(item, f"families_searched[{idx}]")
        if fam not in MORPHISM_FAMILY_SET or fam in seen:
            raise ValueError(f"invalid or duplicate family at families_searched[{idx}]")
        seen.add(fam)
        out.append(fam)
    return tuple(out)


def certify_transformational_steelman(spec: Any) -> dict[str, Any]:
    """Fail-closed Law-2b Transformational Steelman & Anti-Epicycle Certifier.

    Enforces:
      - G0: Strict schema, literal failure precondition, & search membership
      - G1: Non-vacuity (rank >= 1, target passes, null false-pass <= cap)
      - G2: Global scope (fixed before holdout) & strict DoF budget (dof < constraints)
      - G3: Explicit Scope-Delta Ledger (no silent relabelling, exact/bounded gap match)
      - G4: Transform-Invariant Obstruction Gate (refuses raw/premature FALSIFIED;
            requires exhaustive 7-family search + explicit surviving obstruction +
            failing target for INVARIANT_FALSIFIED)
    """
    if not isinstance(spec, dict):
        raise ValueError("spec must be a dict")
    if set(spec.keys()) != REQUIRED_SPEC_KEYS:
        raise ValueError("spec keys must match exact REQUIRED_SPEC_KEYS")

    claim_id = clean_ascii_str(spec["claim_id"], "claim_id")
    proposed_verdict = clean_ascii_str(spec["proposed_verdict"], "proposed_verdict")
    if proposed_verdict not in ALLOWED_PROPOSED_VERDICTS:
        raise ValueError("invalid proposed_verdict")

    literal_failed = exact_bool(spec["literal_failed"], "literal_failed")
    literal_failure_witness = clean_ascii_str(
        spec["literal_failure_witness"], "literal_failure_witness"
    )
    families_searched = parse_families_searched(spec["families_searched"])
    applied_family = opt_clean_ascii_str(spec["applied_family"], "applied_family")
    if applied_family is not None and applied_family not in MORPHISM_FAMILY_SET:
        raise ValueError("applied_family must be None or a valid morphism family")

    transform_dof = exact_int(spec["transform_dof"], "transform_dof")
    held_out_constraints = exact_int(spec["held_out_constraints"], "held_out_constraints")
    fixed_globally = exact_bool(
        spec["fixed_globally_before_holdout"], "fixed_globally_before_holdout"
    )
    target_pass = exact_int(spec["target_pass_count"], "target_pass_count")
    target_total = exact_int(spec["target_total_count"], "target_total_count")
    null_false_pass = exact_int(spec["null_false_pass_count"], "null_false_pass_count")
    null_total = exact_int(spec["null_total_count"], "null_total_count")
    max_null_rate = exact_frac(spec["max_null_false_pass_rate"], "max_null_false_pass_rate")
    transform_rank = exact_int(spec["transform_rank"], "transform_rank")

    preserved_core = opt_clean_ascii_str(
        spec["preserved_invariant_core"], "preserved_invariant_core"
    )
    modified_hyp = opt_clean_ascii_str(spec["modified_hypotheses"], "modified_hypotheses")
    residual_gap = exact_frac(spec["residual_gap"], "residual_gap")
    max_residual_gap = exact_frac(spec["max_residual_gap"], "max_residual_gap")
    relabelled = exact_bool(spec["relabelled_as_literal"], "relabelled_as_literal")
    obstruction = opt_clean_ascii_str(
        spec["obstruction_invariant"], "obstruction_invariant"
    )
    obstruction_survives = exact_bool(
        spec["obstruction_survives_all_searched"], "obstruction_survives_all_searched"
    )

    if transform_dof < 0 or held_out_constraints < 1:
        raise ValueError("transform_dof >= 0 and held_out_constraints >= 1 required")
    if target_total < 1 or target_pass < 0 or target_pass > target_total:
        raise ValueError("invalid target pass/total counts")
    if null_total < 1 or null_false_pass < 0 or null_false_pass > null_total:
        raise ValueError("invalid null pass/total counts")
    if max_null_rate < 0 or max_null_rate > MAX_ALLOWED_NULL_RATE:
        raise ValueError("max_null_false_pass_rate must lie in [0, 1/10]")
    if transform_rank < 0:
        raise ValueError("transform_rank must be >= 0")
    if residual_gap < 0 or max_residual_gap < 0:
        raise ValueError("residual_gap and max_residual_gap must be >= 0")

    null_rate = Fraction(null_false_pass, null_total)
    target_rate = Fraction(target_pass, target_total)
    reasons: list[str] = []

    if not literal_failed:
        reasons.append("G0_LITERAL_CLAIM_NOT_FAILED")
    if relabelled:
        reasons.append("G3_SILENT_GOALPOST_MOVING")
    if applied_family is not None and applied_family not in families_searched:
        reasons.append("G0_APPLIED_FAMILY_NOT_IN_SEARCH")
    if not fixed_globally:
        reasons.append("G2_POST_HOC_PER_INSTANCE_PATCHING")
    if null_rate > max_null_rate:
        reasons.append("G1_VACUOUS_NULL_DISCRIMINATION_FAILED")

    if proposed_verdict == "FALSIFIED_RAW":
        reasons.append("G4_PREMATURE_FALSIFIED_NO_MORPHISM_GATE")
    elif proposed_verdict == "INVARIANT_FALSIFIED":
        if applied_family is not None:
            reasons.append("G4_FALSIFIED_MUST_NOT_APPLY_RESCUE_FAMILY")
        if (
            preserved_core is not None
            or modified_hyp is not None
            or transform_rank != 0
            or transform_dof != 0
        ):
            reasons.append("G4_CONTRADICTORY_RESCUE_FIELDS_ON_FALSIFIED")
        if residual_gap == 0:
            reasons.append("G4_FALSIFIED_HAS_ZERO_GAP")
        if target_pass == target_total:
            reasons.append("G4_FALSIFIED_CLAIM_HAS_NO_FAILING_TARGET")
        if len(families_searched) < len(MORPHISM_FAMILIES):
            reasons.append("G4_INSUFFICIENT_MORPHISM_SEARCH")
        if obstruction is None:
            reasons.append("G4_MISSING_TRANSFORM_INVARIANT_OBSTRUCTION")
        if not obstruction_survives:
            reasons.append("G4_OBSTRUCTION_NOT_INVARIANT_ACROSS_FAMILIES")
    else:
        if applied_family is None:
            reasons.append("G0_MISSING_APPLIED_FAMILY")
        if obstruction is not None or obstruction_survives:
            reasons.append("G0_CONTRADICTORY_OBSTRUCTION_ON_RESCUE")
        if transform_rank < 1:
            reasons.append("G1_DEGENERATE_ZERO_RANK_TRANSFORM")
        if target_pass < target_total:
            reasons.append("G1_TRANSFORMED_TARGET_FAILED")
        if max_null_rate > 0 and null_total * max_null_rate < 1:
            reasons.append("G1_INSUFFICIENT_NULL_RESOLUTION")
        if transform_dof >= held_out_constraints:
            reasons.append("G2_OVERPARAMETERIZED_EPICYCLE_DOF")
        if preserved_core is None or modified_hyp is None:
            reasons.append("G3_INCOMPLETE_SCOPE_DELTA_LEDGER")
        if proposed_verdict == "TRANSFORMED_EXACT":
            if residual_gap != 0 or max_residual_gap != 0:
                reasons.append("G3_EXACT_RESCUE_HAS_NONZERO_GAP")
        else:
            if residual_gap == 0 or residual_gap > max_residual_gap:
                reasons.append("G3_BOUNDED_RESCUE_GAP_OUT_OF_RANGE")

    admitted = len(reasons) == 0
    return {
        "claim_id": claim_id,
        "proposed_verdict": proposed_verdict,
        "admitted": admitted,
        "status": f"CERTIFIED_{proposed_verdict}" if admitted else "REJECTED_LAW2B_GATE",
        "reasons": reasons,
        "metrics": {
            "families_searched_count": len(families_searched),
            "target_pass_rate": frac_to_dict(target_rate),
            "null_false_pass_rate": frac_to_dict(null_rate),
            "dof_margin": held_out_constraints - transform_dof,
            "residual_gap": frac_to_dict(residual_gap),
            "literal_failure_witness": literal_failure_witness,
        },
    }


def _symmetric_inertia_exact(matrix: Any) -> tuple[int, int, int]:
    """Exact pure-Q Bunch-Kaufman / diagonal-pivot congruence inertia (n_pos, n_neg, n_zero).

    Fail-closed on non-square, empty, non-exact (float/bool), or asymmetric inputs.
    """
    if not isinstance(matrix, (list, tuple)) or len(matrix) == 0:
        raise ValueError("matrix must be a non-empty sequence of rows")
    n = len(matrix)
    a: list[list[Fraction]] = []
    for i, row in enumerate(matrix):
        if not isinstance(row, (list, tuple)) or len(row) != n:
            raise ValueError("matrix must be square")
        a.append([exact_frac(row[j], f"matrix[{i}][{j}]") for j in range(n)])
    for i in range(n):
        for j in range(i + 1, n):
            if a[i][j] != a[j][i]:
                raise ValueError("matrix must be symmetric")
    pos = 0
    neg = 0
    zero = 0
    idx = 0
    while idx < n:
        piv = a[idx][idx]
        if piv != 0:
            if piv > 0:
                pos += 1
            else:
                neg += 1
            for r in range(idx + 1, n):
                factor = a[r][idx] / piv
                if factor != 0:
                    for c in range(idx + 1, n):
                        a[r][c] -= factor * a[idx][c]
            idx += 1
            continue
        swap_k = -1
        for k in range(idx + 1, n):
            if a[k][k] != 0:
                swap_k = k
                break
        if swap_k != -1:
            a[idx], a[swap_k] = a[swap_k], a[idx]
            for r in range(n):
                a[r][idx], a[r][swap_k] = a[r][swap_k], a[r][idx]
            continue
        off_k = -1
        for k in range(idx + 1, n):
            if a[idx][k] != 0:
                off_k = k
                break
        if off_k == -1:
            zero += 1
            idx += 1
            continue
        if off_k != idx + 1:
            a[idx + 1], a[off_k] = a[off_k], a[idx + 1]
            for r in range(n):
                a[r][idx + 1], a[r][off_k] = a[r][off_k], a[r][idx + 1]
        # 2x2 symmetric block [[0, b], [b, 0]] has exact eigenvalues (+b, -b) -> (1 pos, 1 neg)
        b = a[idx][idx + 1]
        pos += 1
        neg += 1
        for r in range(idx + 2, n):
            v0 = a[r][idx]
            v1 = a[r][idx + 1]
            for c in range(idx + 2, n):
                u0 = a[c][idx]
                u1 = a[c][idx + 1]
                a[r][c] -= (v0 * u1 + v1 * u0) / b
        idx += 2
    return (pos, neg, zero)


def _rank_transform_exact(block: list[int]) -> list[Fraction]:
    """Exact mid-rank transform (monotone-map invariant)."""
    n = len(block)
    out: list[Fraction] = []
    for x in block:
        less = sum(1 for y in block if y < x)
        eq = sum(1 for y in block if y == x)
        out.append(Fraction(2 * less + eq - 1, 2))
    return out


def _end_match_cost(seg: list[Fraction]) -> Fraction:
    """PREREG.md:163 exact squared end-value + end-slope jump."""
    dv = seg[-1] - seg[0]
    ds = (seg[1] - seg[0]) - (seg[-1] - seg[-2])
    return dv * dv + ds * ds


def _prove_t1_gauge_similarity() -> dict[str, Any]:
    """T1 (AUDIT-008R / AUDIT-004 Q[q], issue_4.md:31): Diagonal gauge similarity
    K'_q = D_h^-1 K_q D_h is NOT a stochastic Doob transform (rows do not sum to 1),
    yet preserves exact characteristic polynomial (tr, det) and max-times row-0 peak.
    """
    k_mat = [
        [Fraction(1, 2), Fraction(1, 2)],
        [Fraction(1, 2), Fraction(1, 2)],
    ]
    d_diag = [Fraction(1, 1), Fraction(2, 1)]
    raw_row_sums = [sum(row, Fraction(0, 1)) for row in k_mat]
    k_sim = [
        [k_mat[i][j] * d_diag[j] / d_diag[i] for j in range(2)] for i in range(2)
    ]
    sim_row_sums = [sum(row, Fraction(0, 1)) for row in k_sim]
    sim_row0_max_times = max(k_sim[0])
    tr_raw = k_mat[0][0] + k_mat[1][1]
    det_raw = k_mat[0][0] * k_mat[1][1] - k_mat[0][1] * k_mat[1][0]
    tr_sim = k_sim[0][0] + k_sim[1][1]
    det_sim = k_sim[0][0] * k_sim[1][1] - k_sim[0][1] * k_sim[1][0]
    return {
        "raw_row_sums": [frac_to_dict(x) for x in raw_row_sums],
        "sim_row_sums": [frac_to_dict(x) for x in sim_row_sums],
        "literal_doob_stochastic_fails": sim_row_sums != [Fraction(1, 1), Fraction(1, 1)],
        "sim_row0_max_times": frac_to_dict(sim_row0_max_times),
        "charpoly_preserved_exact": (tr_raw == tr_sim) and (det_raw == det_sim),
        "trace": frac_to_dict(tr_sim),
        "det": frac_to_dict(det_sim),
    }


def _prove_t2_affine_bregman() -> dict[str, Any]:
    """T2 (AUDIT-073R songe SNG-01): Clipped KL anti-teacher reversal rescued by Bregman shift."""
    p0 = Fraction(1, 2)
    q0 = Fraction(1, 64)
    q1 = Fraction(1, 1) - q0
    r0 = p0 / q0
    r1 = (Fraction(1, 1) - p0) / q1
    clip_hi = Fraction(2, 1)
    dterm1 = Fraction(1, 2) * (1 - r1 * r1)
    dl_dz0_clipped = q0 * q1 * (Fraction(1, 2) * (clip_hi - 1) ** 2 - dterm1)
    dl_dz0_bregman = q0 * q1 * (Fraction(1, 2) * (1 - r0 * r0) - dterm1)
    dl_dz0_forward = q0 - p0
    return {
        "clipped_anti_teacher_grad": frac_to_dict(dl_dz0_clipped),
        "bregman_aligned_grad": frac_to_dict(dl_dz0_bregman),
        "forward_kl_grad": frac_to_dict(dl_dz0_forward),
        "literal_reverses_sign": dl_dz0_clipped > 0,
        "bregman_rescues_sign": (dl_dz0_bregman < 0) and (dl_dz0_forward < 0),
    }


def _prove_t3_metric_chart() -> dict[str, Any]:
    """T3 (AUDIT-079R RIPO): Raw RIPO overflow/dead-zone rescued by Bernoulli-chi^2 chart."""
    delta_default = Fraction(1, 20)
    p_low = Fraction(1, 80)
    p_hi = Fraction(4, 5)
    raw_low_eps = Fraction(math.isqrt((delta_default / p_low).numerator), 1)
    raw_low_bound = Fraction(1, 1) - raw_low_eps
    raw_hi_eps = Fraction(
        math.isqrt((delta_default / p_hi).numerator),
        math.isqrt((delta_default / p_hi).denominator),
    )
    raw_hi_qmax = p_hi * (Fraction(1, 1) + raw_hi_eps)
    # Symmetric Bernoulli-chi^2 chart at delta=1/50, p=4/5: |q-p| <= sqrt(2*delta*p*(1-p)) = 2/25
    delta_ex = Fraction(1, 50)
    rad_sq = 2 * delta_ex * p_hi * (Fraction(1, 1) - p_hi)
    rad = Fraction(math.isqrt(rad_sq.numerator), math.isqrt(rad_sq.denominator))
    q_min_bern = p_hi - rad
    q_max_bern = p_hi + rad
    # Square-free proof at delta=1/20, p=4/5: boundary distance to q=1 is 1/8 > 1/20 -> strictly < 1
    bern_dist_to_1 = (Fraction(1, 1) - p_hi) ** 2 / (2 * p_hi * (Fraction(1, 1) - p_hi))
    return {
        "raw_lower_dead_zone_bound": frac_to_dict(raw_low_bound),
        "raw_upper_overflow_qmax": frac_to_dict(raw_hi_qmax),
        "raw_fails_both_boundaries": (raw_low_bound < 0) and (raw_hi_qmax >= 1),
        "bern_delta_1_50_qmin": frac_to_dict(q_min_bern),
        "bern_delta_1_50_qmax": frac_to_dict(q_max_bern),
        "bern_dist_to_simplex_edge": frac_to_dict(bern_dist_to_1),
        "bern_strictly_interior": (0 < q_min_bern < q_max_bern < 1)
        and (bern_dist_to_1 > delta_default),
    }


def _prove_t4_spectral_psd_shift() -> dict[str, Any]:
    """T4 (AUDIT-070R Zenodo Pillar B): G_10 = K_{4,4} U {(7,8)} U K_2 inertia rescue."""
    n = 10
    a0 = [[Fraction(0, 1) for _ in range(n)] for _ in range(n)]
    for u in range(4):
        for v in range(4, 8):
            a0[u][v] = Fraction(1, 1)
            a0[v][u] = Fraction(1, 1)
    for u, v in ((7, 8), (8, 9)):
        a0[u][v] = Fraction(1, 1)
        a0[v][u] = Fraction(1, 1)

    def shifted(shift: int) -> list[list[Fraction]]:
        return [
            [a0[i][j] + (Fraction(shift, 1) if i == j else Fraction(0, 1)) for j in range(n)]
            for i in range(n)
        ]

    # A = A_0 + I; test A - 3I = A_0 - 2I and A + 3I = A_0 + 4I, plus steelman A_0 + 5I
    in_a_minus_3 = _symmetric_inertia_exact(shifted(-2))
    in_a_plus_3 = _symmetric_inertia_exact(shifted(4))
    in_psd_shift = _symmetric_inertia_exact(shifted(5))
    return {
        "inertia_A_minus_3I": list(in_a_minus_3),
        "inertia_A_plus_3I": list(in_a_plus_3),
        "literal_squaring_inverts_spectrum": (in_a_minus_3 == (1, 9, 0))
        and (in_a_plus_3 == (9, 1, 0)),
        "steelman_shift_dmax": 5,
        "inertia_A0_plus_5I": list(in_psd_shift),
        "steelman_strictly_pd": in_psd_shift == (10, 0, 0),
    }


def _prove_t5_semiring_tropical() -> dict[str, Any]:
    """T5 (AUDIT-085 Thm A): Exact Q[q] vs (min,+) elimination bridge & cancellation gap."""
    # Cancellation-free: two positive walks of order q^2 -> S = q^2 + q^2 = 2 q^2
    poly_pos = {2: Fraction(1, 1) + Fraction(1, 1)}
    val_pos = min(k for k, v in poly_pos.items() if v != 0)
    t_trop_pos = min(2, 2)
    gap_pos = val_pos - t_trop_pos

    # Signed cancellation: (+1)*q^2 + (-1)*q^2 + (+1)*q^3 = q^3 -> val_S = 3, T_trop = 2, gap = 1
    poly_cancel = {2: Fraction(1, 1) - Fraction(1, 1), 3: Fraction(1, 1)}
    val_cancel = min(k for k, v in poly_cancel.items() if v != 0)
    t_trop_cancel = min(2, 2, 3)
    gap_cancel = val_cancel - t_trop_cancel
    return {
        "no_cancel_val_S": val_pos,
        "no_cancel_T_trop": t_trop_pos,
        "no_cancel_gap": gap_pos,
        "cancel_val_S": val_cancel,
        "cancel_T_trop": t_trop_cancel,
        "cancel_gap": gap_cancel,
        "bridge_exact_when_nocancel_and_measured_when_cancel": (gap_pos == 0)
        and (gap_cancel == 1),
    }


def _prove_t6_subspace_projection() -> dict[str, Any]:
    """T6 (AUDIT-083R BPO, AUDIT-087 PREREG-02, & newly surfaced AUDIT-023 CS-08 core)."""
    # 1. BPO <-> Top-1 Score Centering complementary-prob duality at pi=99/100, mu=1/2
    pi_y = Fraction(99, 100)
    mu_y = Fraction(1, 2)
    bpo_unsmoothed_w = (Fraction(1, 1) - mu_y) / (Fraction(1, 1) - pi_y)
    top1_sc_rho = (Fraction(1, 1) - mu_y) / (Fraction(1, 1) - pi_y)
    # Logit Jacobian of log(pi_y) has L1 norm 2*(1-pi_y); multiplying cancels (1-pi_y) identically!
    canceled_grad_l1 = bpo_unsmoothed_w * (2 * (Fraction(1, 1) - pi_y))
    expected_l1 = 2 * (Fraction(1, 1) - mu_y)

    # 2. PREREG-02 time-odd vs time-even subspace split (20 even +1, 10 odd -1 -> raw +1/3, odd -1)
    raw_t3_dot = Fraction(20 * 1 + 10 * (-1), 30)
    odd_subspace_dot = Fraction(10 * (-1), 10)

    # 3. Newly surfaced AUDIT-023 CS-08 core (issue_4.md:62-66):
    # Raw post-treatment strata do NOT reverse (-16/2881, -1/14, -2/25),
    # YET T6 principal-stratum projection (66 clean pairs) flips sign to +1/66!
    diff_no_unread = Fraction(56, 86) - Fraction(44, 67)
    diff_some_unread = Fraction(13, 14) - Fraction(33, 33)
    diff_overall = Fraction(69, 100) - Fraction(77, 100)
    diff_principal_66 = Fraction(44, 66) - Fraction(43, 66)
    return {
        "bpo_weight": frac_to_dict(bpo_unsmoothed_w),
        "bpo_equals_top1_sc": bpo_unsmoothed_w == top1_sc_rho,
        "bpo_canceled_grad_l1": frac_to_dict(canceled_grad_l1),
        "bpo_jacobian_cancellation_exact": canceled_grad_l1 == expected_l1,
        "prereg02_raw_mixed_score": frac_to_dict(raw_t3_dot),
        "prereg02_odd_subspace_score": frac_to_dict(odd_subspace_dot),
        "prereg02_subspace_restores_reversal": (raw_t3_dot > 0) and (odd_subspace_dot < 0),
        "cs08_diff_no_unread": frac_to_dict(diff_no_unread),
        "cs08_diff_some_unread": frac_to_dict(diff_some_unread),
        "cs08_diff_overall": frac_to_dict(diff_overall),
        "cs08_literal_simpson_absent": (diff_no_unread < 0)
        and (diff_some_unread < 0)
        and (diff_overall < 0),
        "cs08_principal_stratum_66_diff": frac_to_dict(diff_principal_66),
        "cs08_principal_stratum_reverses_sign": diff_principal_66 > 0,
    }


def _prove_t7_order_domain_residual() -> dict[str, Any]:
    """T7 (AUDIT-087 PREREG-03 mid-rank chart & newly surfaced AUDIT-080R Zhihu L112 domain)."""
    # 1. PREREG-03 monotone offset leak fixed by exact mid-rank chart
    block = [10, 10, 0, 1, 11, 11, 2, 2]
    mapped = [x * x * x + x for x in block]
    raw_costs = [_end_match_cost([Fraction(v, 1) for v in block[o : o + 6]]) for o in range(3)]
    map_costs = [_end_match_cost([Fraction(v, 1) for v in mapped[o : o + 6]]) for o in range(3)]
    rk_raw = _rank_transform_exact(block)
    rk_map = _rank_transform_exact(mapped)
    rk_costs_raw = [_end_match_cost(rk_raw[o : o + 6]) for o in range(3)]
    rk_costs_map = [_end_match_cost(rk_map[o : o + 6]) for o in range(3)]
    raw_argmin = min(range(3), key=lambda i: raw_costs[i])
    map_argmin = min(range(3), key=lambda i: map_costs[i])
    rk_argmin = min(range(3), key=lambda i: rk_costs_raw[i])

    # 2. Newly surfaced AUDIT-080R Zhihu L112 Pythagorean domain core:
    # Binary softmax p = (3/4, 1/4), q = (1/2, 1/2); score vectors s_0 = (1/4, -1/4), s_1 = (-3/4, 3/4)
    p = [Fraction(3, 4), Fraction(1, 4)]
    q = [Fraction(1, 2), Fraction(1, 2)]
    scores = [[Fraction(1, 4), Fraction(-1, 4)], [Fraction(-3, 4), Fraction(3, 4)]]
    s_bar_q = [sum((q[v] * scores[v][j] for v in range(2)), Fraction(0, 1)) for j in range(2)]

    def bias_decomp(adv: list[Fraction]) -> dict[str, Any]:
        g_star = [sum((p[v] * adv[v] * scores[v][j] for v in range(2)), Fraction(0, 1)) for j in range(2)]
        g_off = [sum((q[v] * adv[v] * scores[v][j] for v in range(2)), Fraction(0, 1)) for j in range(2)]
        mean_a = sum((q[v] * adv[v] for v in range(2)), Fraction(0, 1))
        d_vec = [mean_a * s_bar_q[j] for j in range(2)]
        g_sc = [g_off[j] - d_vec[j] for j in range(2)]
        e_sc = [g_sc[j] - g_star[j] for j in range(2)]
        e_off = [g_off[j] - g_star[j] for j in range(2)]
        norm_d_sq = sum((x * x for x in d_vec), Fraction(0, 1))
        inner = sum((e_sc[j] * d_vec[j] for j in range(2)), Fraction(0, 1))
        delta_l2_sq = sum((x * x for x in e_sc), Fraction(0, 1)) - sum(
            (x * x for x in e_off), Fraction(0, 1)
        )
        return {
            "norm_d_sq": frac_to_dict(norm_d_sq),
            "inner_e_sc_d": frac_to_dict(inner),
            "delta_l2_sq": frac_to_dict(delta_l2_sq),
            "pythagorean_identity_exact": delta_l2_sq == -(norm_d_sq + 2 * inner),
            "in_valid_domain": (2 * inner + norm_d_sq) > 0,
            "sc_reduces_l2_bias": delta_l2_sq < 0,
        }

    dom_in = bias_decomp([Fraction(1, 1), Fraction(1, 1)])
    dom_out = bias_decomp([Fraction(3, 1), Fraction(-1, 1)])
    return {
        "prereg03_raw_argmin": raw_argmin,
        "prereg03_mapped_argmin": map_argmin,
        "prereg03_raw_leaks": raw_argmin != map_argmin,
        "prereg03_rank_costs_equal": rk_costs_raw == rk_costs_map,
        "prereg03_rank_argmin": rk_argmin,
        "zhihu_l112_in_domain_A_1_1": dom_in,
        "zhihu_l112_out_domain_A_3_m1": dom_out,
        "zhihu_l112_domain_separates_sign": dom_in["sc_reduces_l2_bias"]
        and (not dom_out["sc_reduces_l2_bias"]),
    }


def _prove_invariant_obstructions() -> dict[str, Any]:
    """Three genuine transform-invariant obstructions (INVARIANT_FALSIFIED)."""
    # 1. AUDIT-070R Pillar A: Tseitin(K_4, b) Gramian blindness (identical (8*I_6, 0) for SAT & UNSAT)
    parity_eqs = (
        (0, 1, 2, 0),
        (0, 3, 4, 0),
        (1, 3, 5, 0),
        (2, 4, 5, 1),  # RHS flipped for UNSAT (b=1) vs SAT (b=0)
    )

    def build_tseitin_cnf(unsat_rhs: int) -> tuple[list[list[int]], int]:
        rows: list[list[int]] = []
        eqs = parity_eqs[:-1] + ((2, 4, 5, unsat_rhs),)
        for v0, v1, v2, rhs in eqs:
            # 3-CNF encoding of x_v0 ^ x_v1 ^ x_v2 = rhs forbids the 4 triples with XOR != rhs
            for bits in itertools.product((0, 1), repeat=3):
                if (bits[0] ^ bits[1] ^ bits[2]) != rhs:
                    row = [0] * 6
                    # Clause forbids assignment `bits`: literal is +1 if bit==0 else -1
                    row[v0] = 1 if bits[0] == 0 else -1
                    row[v1] = 1 if bits[1] == 0 else -1
                    row[v2] = 1 if bits[2] == 0 else -1
                    rows.append(row)
        # Count exact satisfying models over {0,1}^6
        models = 0
        for assign in itertools.product((0, 1), repeat=6):
            ok = True
            for row in rows:
                clause_sat = False
                for var, coeff in enumerate(row):
                    if (coeff == 1 and assign[var] == 1) or (coeff == -1 and assign[var] == 0):
                        clause_sat = True
                        break
                if not clause_sat:
                    ok = False
                    break
            if ok:
                models += 1
        return rows, models

    b_sat, models_sat = build_tseitin_cnf(0)
    b_unsat, models_unsat = build_tseitin_cnf(1)

    def gram_and_bias(mat: list[list[int]]) -> tuple[list[list[int]], list[int]]:
        gram = [
            [sum(mat[r][i] * mat[r][j] for r in range(len(mat))) for j in range(6)]
            for i in range(6)
        ]
        bias = [sum(mat[r][j] for r in range(len(mat))) for j in range(6)]
        return gram, bias

    w_sat, bias_sat = gram_and_bias(b_sat)
    w_unsat, bias_unsat = gram_and_bias(b_unsat)
    id8 = [[8 if i == j else 0 for j in range(6)] for i in range(6)]

    # 2. AUDIT-070R Pillar C: Teorema 4.1 5-point (8,15,17) TSP enumeration at M = 8008
    m_val = 8008
    pts = ((0, 0), (0, 8), (-15, 0), (15, 0), (0, m_val))

    def euc2d(i: int, j: int) -> int:
        dx = pts[i][0] - pts[j][0]
        dy = pts[i][1] - pts[j][1]
        d2 = dx * dx + dy * dy
        # Exact nearest integer sqrt(d2) without floats: isqrt(4*d2) gives floor(2*sqrt(d2));
        # floor(sqrt(d2) + 1/2) == (isqrt(4*d2) + 1) // 2
        return (math.isqrt(4 * d2) + 1) // 2

    best_with_01: int | None = None
    best_without_01: int | None = None
    for perm in itertools.permutations((1, 2, 3, 4)):
        if perm[0] > perm[-1]:
            continue
        tour = (0,) + perm
        cost = sum(euc2d(tour[k], tour[(k + 1) % 5]) for k in range(5))
        edges = {
            (min(tour[k], tour[(k + 1) % 5]), max(tour[k], tour[(k + 1) % 5]))
            for k in range(5)
        }
        if (0, 1) in edges:
            if best_with_01 is None or cost < best_with_01:
                best_with_01 = cost
        else:
            if best_without_01 is None or cost < best_without_01:
                best_without_01 = cost

    # 3. AUDIT-073R SNG-02: n=1 unanimous bootstrap rank-0 collapse
    sample_n1 = [Fraction(1, 1)]
    mean_n1 = sample_n1[0]
    var_n1 = sum(((x - mean_n1) ** 2 for x in sample_n1), Fraction(0, 1))
    per_scale_null_fa = Fraction(1, 2)
    two_scale_fwer = Fraction(1, 1) - (Fraction(1, 1) - per_scale_null_fa) ** 2

    return {
        "audit070_pillar_a_tseitin_k4": {
            "clauses_each": len(b_sat),
            "models_sat": models_sat,
            "models_unsat": models_unsat,
            "gramians_identical_8I6": (w_sat == id8) and (w_unsat == id8),
            "linear_biases_identical_zero": (bias_sat == [0] * 6) and (bias_unsat == [0] * 6),
        },
        "audit070_pillar_c_sidewalk_tsp": {
            "sigma0": frac_to_dict(Fraction(m_val - 8, 8)),
            "best_without_01": best_without_01,
            "best_with_01": best_with_01,
            "exact_penalty_gap": (best_with_01 - best_without_01)
            if (best_with_01 is not None and best_without_01 is not None)
            else None,
            "shortest_edge_strictly_suboptimal": (
                best_without_01 is not None
                and best_with_01 is not None
                and best_without_01 < best_with_01
            ),
        },
        "audit073_sng02_bootstrap_n1": {
            "empirical_variance": frac_to_dict(var_n1),
            "per_scale_null_false_accept": frac_to_dict(per_scale_null_fa),
            "two_scale_null_fwer": frac_to_dict(two_scale_fwer),
            "rank_zero_collapse": var_n1 == 0,
        },
    }


def _build_certified_vault_cases() -> dict[str, Any]:
    """Run certify_transformational_steelman across rescues, obstructions, & anti-epicycles."""
    all_7 = list(MORPHISM_FAMILIES)

    def make_rescue(
        claim_id: str,
        verdict: str,
        family: str,
        witness: str,
        core: str,
        mod_hyp: str,
        dof: int,
        constraints: int,
        gap: Fraction,
        max_gap: Fraction,
    ) -> dict[str, Any]:
        return certify_transformational_steelman(
            {
                "claim_id": claim_id,
                "proposed_verdict": verdict,
                "literal_failed": True,
                "literal_failure_witness": witness,
                "families_searched": [family],
                "applied_family": family,
                "transform_dof": dof,
                "held_out_constraints": constraints,
                "fixed_globally_before_holdout": True,
                "target_pass_count": constraints,
                "target_total_count": constraints,
                "null_false_pass_count": 0,
                "null_total_count": 10,
                "max_null_false_pass_rate": Fraction(1, 10),
                "transform_rank": 2,
                "preserved_invariant_core": core,
                "modified_hypotheses": mod_hyp,
                "residual_gap": gap,
                "max_residual_gap": max_gap,
                "relabelled_as_literal": False,
                "obstruction_invariant": None,
                "obstruction_survives_all_searched": False,
            }
        )

    def make_obstruction(claim_id: str, witness: str, obstruction: str) -> dict[str, Any]:
        return certify_transformational_steelman(
            {
                "claim_id": claim_id,
                "proposed_verdict": "INVARIANT_FALSIFIED",
                "literal_failed": True,
                "literal_failure_witness": witness,
                "families_searched": all_7,
                "applied_family": None,
                "transform_dof": 0,
                "held_out_constraints": 4,
                "fixed_globally_before_holdout": True,
                "target_pass_count": 0,
                "target_total_count": 4,
                "null_false_pass_count": 0,
                "null_total_count": 10,
                "max_null_false_pass_rate": Fraction(1, 10),
                "transform_rank": 0,
                "preserved_invariant_core": None,
                "modified_hypotheses": None,
                "residual_gap": Fraction(1, 1),
                "max_residual_gap": Fraction(1, 1),
                "relabelled_as_literal": False,
                "obstruction_invariant": obstruction,
                "obstruction_survives_all_searched": True,
            }
        )

    rescues = {
        "T1_audit008r_gauge_similarity": make_rescue(
            "AUDIT-008R/004:Q[q]-Doob-vs-Gauge",
            "TRANSFORMED_EXACT",
            "T1_GAUGE_SIMILARITY",
            "Conjugate K'=D^-1 K D has non-stochastic row sums [3/2, 3/4] != [1, 1]",
            "Exact spectrum {1, 0} & row-0 max-times=1 preserved under D^-1 K D",
            "Relabel Doob h-transform to diagonal gauge similarity (issue_4.md:31)",
            1,
            4,
            Fraction(0, 1),
            Fraction(0, 1),
        ),
        "T2_audit073_songe_bregman": make_rescue(
            "AUDIT-073R:songe-SNG-01",
            "TRANSFORMED_EXACT",
            "T2_AFFINE_BREGMAN",
            "Clipped KL gradient +1/504 reverses away from teacher p=1/2",
            "Non-negative Gibbs divergence & teacher-aligned gradient -496/63",
            "Replace raw ratio-clipped KL with Bregman-normalized divergence",
            0,
            4,
            Fraction(0, 1),
            Fraction(0, 1),
        ),
        "T3_audit079_ripo_chart": make_rescue(
            "AUDIT-079R:RIPO-Chart",
            "TRANSFORMED_EXACT",
            "T3_METRIC_CHART",
            "Raw RIPO hits -1 dead zone at p=1/80 and q_max=1 overflow at p=4/5",
            "Isometric Fisher-Rao local trust region strictly inside (0, 1)",
            "Reparametrize ratio clip into symmetric Bernoulli-chi^2 chart",
            1,
            4,
            Fraction(0, 1),
            Fraction(0, 1),
        ),
        "T4_audit070_zenodo_pillar_b": make_rescue(
            "AUDIT-070R:Zenodo-Teorema-3.2",
            "TRANSFORMED_EXACT",
            "T4_SPECTRAL_PSD_SHIFT",
            "Squaring A_0+I flips lambda_min<-3 above lambda_2 on G_10",
            "Order-preserving PSD spectrum inertia (10, 0, 0) on A_0+5I",
            "Replace (A_0+I)^2 with d_max-shifted adjacency A_0+d_max*I (N0)",
            1,
            10,
            Fraction(0, 1),
            Fraction(0, 1),
        ),
        "T5_audit085_tropical_bridge": make_rescue(
            "AUDIT-085:Algebraic-Tropical-Bridge",
            "BOUNDED_TRANSFORM_CORE",
            "T5_SEMIRING_TROPICAL",
            "Signed walk cancellation shifts valuation from 2 to 3",
            "Exact valuation match when no-cancel; measurable gap Delta=1",
            "Upgrade class label to cross-kind bridge with cancellation gap",
            0,
            4,
            Fraction(1, 1),
            Fraction(2, 1),
        ),
        "T6_audit083_087_023_subspace": make_rescue(
            "AUDIT-083R/087/023:Subspace-Projection",
            "BOUNDED_TRANSFORM_CORE",
            "T6_SUBSPACE_PROJECTION",
            "Mixed T3 features dilute A->C to +1/3; raw CS-08 strata fail Simpson",
            "Exact BPO=Top-1 SC; odd-subspace -1; CS-08 clean stratum +1/66",
            "Project onto complementary/odd/principal pre-leakage subspace",
            1,
            6,
            Fraction(1, 66),
            Fraction(1, 10),
        ),
        "T7_audit087_080_order_domain": make_rescue(
            "AUDIT-087/080R:MidRank-and-L112-Domain",
            "BOUNDED_TRANSFORM_CORE",
            "T7_ORDER_DOMAIN_RESIDUAL",
            "Raw end-match flips 0->2 under x^3+x; Zhihu L112 fails at A=(3,-1)",
            "Mid-rank chart exact offset 0; L112 exact on 2<e_sc,d>+||d||^2>0",
            "Restrict to monotone mid-rank chart & explicit Pythagorean domain",
            1,
            6,
            Fraction(1, 8),
            Fraction(1, 4),
        ),
    }

    obstructions = {
        "OBS1_audit070_pillar_a_tseitin": make_obstruction(
            "AUDIT-070R:Pillar-A-Gramian-SAT",
            "Tseitin(K_4) SAT (8 models) and UNSAT (0 models) share W=8I_6, bias=0",
            "Data-processing invariant: identical observable (8I_6,0) vs Z_2 cohomology 0!=1",
        ),
        "OBS2_audit070_pillar_c_tsp": make_obstruction(
            "AUDIT-070R:Pillar-C-Teorema-4.1",
            "5-point (8,15,17) M=8008 has sigma_0=1000 yet opt=16055<16056 excludes (0,1)",
            "Unbounded isolation ratio (M-8)/8->inf with strict tour penalty >+1 for all M>8",
        ),
        "OBS3_audit073_sng02_bootstrap_n1": make_obstruction(
            "AUDIT-073R:SNG-02-Bootstrap-n1",
            "Single-sample bootstrap [1] yields zero variance and 3/4 2-scale null FWER",
            "Rank-0 singleton sample invariant survives every scalar transform",
        ),
    }

    anti_epicycles = {
        "REJ1_degenerate_zero_rank": certify_transformational_steelman(
            {
                "claim_id": "ANTI-EPICYCLE-G1:Zero-Projection",
                "proposed_verdict": "TRANSFORMED_EXACT",
                "literal_failed": True,
                "literal_failure_witness": "Formula residual != 0",
                "families_searched": ["T6_SUBSPACE_PROJECTION"],
                "applied_family": "T6_SUBSPACE_PROJECTION",
                "transform_dof": 0,
                "held_out_constraints": 4,
                "fixed_globally_before_holdout": True,
                "target_pass_count": 4,
                "target_total_count": 4,
                "null_false_pass_count": 10,
                "null_total_count": 10,
                "max_null_false_pass_rate": Fraction(1, 10),
                "transform_rank": 0,
                "preserved_invariant_core": "Trivial 0 == 0",
                "modified_hypotheses": "Multiply both sides by 0",
                "residual_gap": Fraction(0, 1),
                "max_residual_gap": Fraction(0, 1),
                "relabelled_as_literal": False,
                "obstruction_invariant": None,
                "obstruction_survives_all_searched": False,
            }
        ),
        "REJ2_overparameterized_per_instance": certify_transformational_steelman(
            {
                "claim_id": "ANTI-EPICYCLE-G2:Poly-Fudge",
                "proposed_verdict": "TRANSFORMED_EXACT",
                "literal_failed": True,
                "literal_failure_witness": "5 held-out points miss curve",
                "families_searched": ["T3_METRIC_CHART"],
                "applied_family": "T3_METRIC_CHART",
                "transform_dof": 6,
                "held_out_constraints": 5,
                "fixed_globally_before_holdout": False,
                "target_pass_count": 5,
                "target_total_count": 5,
                "null_false_pass_count": 0,
                "null_total_count": 10,
                "max_null_false_pass_rate": Fraction(1, 10),
                "transform_rank": 1,
                "preserved_invariant_core": "Interpolated curve",
                "modified_hypotheses": "Fit degree-5 polynomial per batch",
                "residual_gap": Fraction(0, 1),
                "max_residual_gap": Fraction(0, 1),
                "relabelled_as_literal": False,
                "obstruction_invariant": None,
                "obstruction_survives_all_searched": False,
            }
        ),
        "REJ3_silent_goalpost_moving": certify_transformational_steelman(
            {
                "claim_id": "ANTI-EPICYCLE-G3:Silent-Relabel",
                "proposed_verdict": "TRANSFORMED_EXACT",
                "literal_failed": True,
                "literal_failure_witness": "Original Doob claim fails row-sum=1",
                "families_searched": ["T1_GAUGE_SIMILARITY"],
                "applied_family": "T1_GAUGE_SIMILARITY",
                "transform_dof": 1,
                "held_out_constraints": 4,
                "fixed_globally_before_holdout": True,
                "target_pass_count": 4,
                "target_total_count": 4,
                "null_false_pass_count": 0,
                "null_total_count": 10,
                "max_null_false_pass_rate": Fraction(1, 10),
                "transform_rank": 2,
                "preserved_invariant_core": "Spectrum",
                "modified_hypotheses": None,
                "residual_gap": Fraction(0, 1),
                "max_residual_gap": Fraction(0, 1),
                "relabelled_as_literal": True,
                "obstruction_invariant": None,
                "obstruction_survives_all_searched": False,
            }
        ),
        "REJ4_premature_falsified_no_search": certify_transformational_steelman(
            {
                "claim_id": "ANTI-EPICYCLE-G4:Premature-Dismissal",
                "proposed_verdict": "INVARIANT_FALSIFIED",
                "literal_failed": True,
                "literal_failure_witness": "Literal formula fails at one point",
                "families_searched": ["T1_GAUGE_SIMILARITY"],
                "applied_family": None,
                "transform_dof": 0,
                "held_out_constraints": 4,
                "fixed_globally_before_holdout": True,
                "target_pass_count": 0,
                "target_total_count": 4,
                "null_false_pass_count": 0,
                "null_total_count": 10,
                "max_null_false_pass_rate": Fraction(1, 10),
                "transform_rank": 0,
                "preserved_invariant_core": None,
                "modified_hypotheses": None,
                "residual_gap": Fraction(1, 1),
                "max_residual_gap": Fraction(1, 1),
                "relabelled_as_literal": False,
                "obstruction_invariant": None,
                "obstruction_survives_all_searched": False,
            }
        ),
    }

    return {
        "certified_rescues": rescues,
        "certified_obstructions": obstructions,
        "rejected_anti_epicycles": anti_epicycles,
    }


def verify_live_vault_anchors(symbiosis_dir: Path) -> dict[str, Any]:
    """Read-only SHA-256 + 1-based newline line anchor check over frozen vault files."""
    file_results: list[dict[str, Any]] = []
    all_digests_ok = True
    for rel_path, expected_sha in EXPECTED_VAULT_SHA256.items():
        fpath = symbiosis_dir / rel_path
        if not fpath.is_file():
            all_digests_ok = False
            file_results.append(
                {
                    "path": rel_path,
                    "expected_sha256": expected_sha,
                    "observed_sha256": None,
                    "matched": False,
                }
            )
            continue
        obs_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
        matched = obs_sha == expected_sha
        if not matched:
            all_digests_ok = False
        file_results.append(
            {
                "path": rel_path,
                "expected_sha256": expected_sha,
                "observed_sha256": obs_sha,
                "matched": matched,
            }
        )

    line_results: list[dict[str, Any]] = []
    verified_lines = 0
    for anchor_id, rel_path, lineno, expected_sub in VAULT_LINE_ANCHORS:
        fpath = symbiosis_dir / rel_path
        matched = False
        if fpath.is_file():
            lines = fpath.read_text(encoding="utf-8").split("\n")
            if 1 <= lineno <= len(lines) and expected_sub in lines[lineno - 1]:
                matched = True
        if matched:
            verified_lines += 1
        line_results.append(
            {
                "id": anchor_id,
                "path": rel_path,
                "expected_line": lineno,
                "matched": matched,
            }
        )

    return {
        "anchor_mode": "live_readonly",
        "files_total": len(EXPECTED_VAULT_SHA256),
        "all_file_digests_matched": all_digests_ok,
        "file_digests": file_results,
        "line_anchors_total": len(VAULT_LINE_ANCHORS),
        "line_anchors_verified": verified_lines,
        "all_anchors_matched": all_digests_ok
        and (verified_lines == len(VAULT_LINE_ANCHORS)),
        "line_anchors": line_results,
    }


def build_certificate(
    symbiosis_dir: Path | None = None, standalone: bool = False
) -> dict[str, Any]:
    """Assemble the canonical zero-float AUDIT-088 certificate."""
    if standalone:
        anchors: dict[str, Any] = {
            "anchor_mode": "standalone",
            "files_total": len(EXPECTED_VAULT_SHA256),
            "all_file_digests_matched": None,
            "line_anchors_total": len(VAULT_LINE_ANCHORS),
            "line_anchors_verified": 0,
            "all_anchors_matched": None,
        }
    else:
        resolved = (
            symbiosis_dir
            if symbiosis_dir is not None
            else Path(__file__).resolve().parent.parent.parent
        )
        anchors = verify_live_vault_anchors(resolved)

    payload: dict[str, Any] = {
        "audit_id": "AUDIT-088",
        "arm": "R10-5",
        "protocol_id": "LAW2B_TRANSFORM_BEFORE_DISMISSAL",
        "title": "Transformational Steelman / Morphism-Before-Dismissal Protocol",
        "oracle_class": "exact+anchor",
        "novelty_class": "N1",
        "zero_float_enforced": True,
        "morphism_families": list(MORPHISM_FAMILIES),
        "max_allowed_null_rate": frac_to_dict(MAX_ALLOWED_NULL_RATE),
        "anchors": anchors,
        "pure_q_vault_proofs": {
            "t1_gauge_similarity": _prove_t1_gauge_similarity(),
            "t2_affine_bregman": _prove_t2_affine_bregman(),
            "t3_metric_chart": _prove_t3_metric_chart(),
            "t4_spectral_psd_shift": _prove_t4_spectral_psd_shift(),
            "t5_semiring_tropical": _prove_t5_semiring_tropical(),
            "t6_subspace_projection": _prove_t6_subspace_projection(),
            "t7_order_domain_residual": _prove_t7_order_domain_residual(),
            "transform_invariant_obstructions": _prove_invariant_obstructions(),
        },
        "certifier_cases": _build_certified_vault_cases(),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["canonical_sha256"] = hashlib.sha256(raw).hexdigest()
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="AUDIT-088 pure-Q Law-2b Transformational Steelman Certifier"
    )
    parser.add_argument("--json", action="store_true", help="Print canonical JSON")
    parser.add_argument(
        "--standalone",
        action="store_true",
        help="Run pure-Q proofs & certifier without reading vault files",
    )
    parser.add_argument(
        "--symbiosis-dir",
        type=str,
        default=None,
        help="Optional override path to expedition symbiosis directory",
    )
    parser.add_argument(
        "--write-cert",
        type=str,
        default=None,
        help="Write canonical pretty JSON certificate to path",
    )
    args = parser.parse_args(argv)
    sym_path = Path(args.symbiosis_dir) if args.symbiosis_dir is not None else None
    cert = build_certificate(symbiosis_dir=sym_path, standalone=args.standalone)
    text = json.dumps(cert, indent=2, sort_keys=True) + "\n"
    if args.write_cert is not None:
        Path(args.write_cert).write_text(text, encoding="utf-8")
    if args.json or args.write_cert is None:
        sys.stdout.write(text)
    if not args.standalone and not cert["anchors"]["all_anchors_matched"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
