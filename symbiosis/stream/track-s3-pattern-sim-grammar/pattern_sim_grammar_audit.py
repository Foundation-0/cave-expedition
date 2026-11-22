#!/usr/bin/env python3
"""AUDIT-099 Dual-Mode CLI & Provenance Certifier for `apl-md` vs. `simgrammar`.

Modes:
  - Default (`--live`): Reads the staged raw corpora directly from `--intake-root`
    (default: `../intake-2026-11-22`), verifies git HEAD commits and paper SHA-256
    fail-closed (rejecting symlink escapes), runs the pure-Q zero-float oracle and
    B=200 degree-preserving / permutation nulls, reconciles `simgrammar_paper.md`
    headline claims, and certifies conservation & Law-5 anti-smuggling invariants.
  - `--standalone`: Explicit offline fixture replay (`execution_mode:
    "standalone_fixture_replay"`, `live_corpus_recounted: false`). Never silently
    substituted when `--live` inputs are missing.

Zero floats, zero bare asserts, 100% Python 3 stdlib.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import pattern_sim_grammar_oracle as oracle  # noqa: E402
from pattern_sim_grammar_oracle import GrammarAuditError, _require  # noqa: E402

SCHEMA_VERSION = "audit-099.pattern-sim-grammar.v1"
AUDIT_ID = "AUDIT-099"
HONEST_TIER = "N0"

PINNED_APL_COMMIT = "c622b25f0b4267363d854eba3da6a82516dd5af9"
PINNED_SIMGRAMMAR_COMMIT = "a1156e80714de0221fefdb037bf2732824a6d156"
PINNED_PAPER_SHA256 = "4f75e9929e34809ff73e4ad6f89dad8fb91cdda00719e81cb588e439765de99a"
PINNED_PAPER_BYTES = 528025
PINNED_PAPER_DATASET_SHA256 = "f9ac0d88ac86202e2f48efd28caea7807f09bbde00cfb9ae99b2bea5ab38106e"

DEFAULT_PINS: dict[str, Any] = {
    "apl_md_commit": PINNED_APL_COMMIT,
    "simgrammar_commit": PINNED_SIMGRAMMAR_COMMIT,
    "simgrammar_paper_sha256": PINNED_PAPER_SHA256,
    "simgrammar_paper_bytes": PINNED_PAPER_BYTES,
    "simgrammar_paper_dataset_sha256": PINNED_PAPER_DATASET_SHA256,
}

_SHA1_HEX_RE = re.compile(r"^[0-9a-f]{40}$")
_DATASET_SHA_RE = re.compile(r'^dataset_sha256:\s*"([0-9a-f]{64})"\s*$', re.M)


def canonical_json_bytes(obj: Any) -> bytes:
    """Deterministic UTF-8 canonical JSON encoding with sorted keys."""
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)).encode("utf-8")


def canonical_sha256(obj: Any) -> str:
    """SHA-256 hex digest of canonical JSON encoding."""
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def _require_contained_path(root: Path, child: Path, label: str) -> Path:
    """Verify `child` is not a symlink and resolves strictly inside `root`."""
    _require(not child.is_symlink(), f"symlink-refused:{label}")
    resolved_root = root.resolve()
    resolved_child = child.resolve()
    _require(resolved_child.is_relative_to(resolved_root), f"escape-refused:{label}")
    return resolved_child


def read_git_head_commit(repo_dir: Path) -> str:
    """Read exact 40-char git HEAD commit hash from `.git/` using pure stdlib."""
    git_dir = repo_dir / ".git"
    _require(git_dir.is_dir() and not git_dir.is_symlink(), f"git-dir-missing:{repo_dir.name}")
    head_file = git_dir / "HEAD"
    _require(head_file.is_file() and not head_file.is_symlink(), f"git-head-missing:{repo_dir.name}")
    head_text = head_file.read_text(encoding="utf-8").strip()

    if head_text.startswith("ref:"):
        ref_rel = head_text[4:].strip()
        _require(ref_rel.startswith("refs/") and ".." not in ref_rel, f"git-ref-invalid:{repo_dir.name}")
        ref_path = git_dir / ref_rel
        if ref_path.is_file() and not ref_path.is_symlink():
            commit = ref_path.read_text(encoding="utf-8").strip()
        else:
            packed = git_dir / "packed-refs"
            _require(packed.is_file() and not packed.is_symlink(), f"git-ref-unresolved:{repo_dir.name}")
            commit = ""
            for line in packed.read_text(encoding="utf-8").splitlines():
                if not line or line.startswith("#") or line.startswith("^"):
                    continue
                parts = line.split(" ", 1)
                if len(parts) == 2 and parts[1].strip() == ref_rel:
                    commit = parts[0].strip()
                    break
    else:
        commit = head_text

    _require(_SHA1_HEX_RE.match(commit) is not None, f"git-commit-malformed:{repo_dir.name}")
    return commit


def verify_intake_provenance(
    intake_root: Path, expected_pins: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Fail-closed verification of staged intake repos and paper snapshot."""
    pins = DEFAULT_PINS if expected_pins is None else expected_pins
    _require(intake_root.is_dir() and not intake_root.is_symlink(), "intake-root-missing")

    apl_repo = _require_contained_path(intake_root, intake_root / "repos" / "apl-md", "apl-md")
    sg_repo = _require_contained_path(intake_root, intake_root / "repos" / "simgrammar", "simgrammar")
    paper_path = _require_contained_path(
        intake_root, intake_root / "sources" / "simgrammar_paper.md", "simgrammar_paper"
    )
    _require(apl_repo.is_dir() and sg_repo.is_dir() and paper_path.is_file(), "intake-entries-missing")

    apl_patterns = _require_contained_path(apl_repo, apl_repo / "Patterns", "apl-patterns")
    sg_data = _require_contained_path(sg_repo, sg_repo / "data", "sg-data")
    _require(apl_patterns.is_dir() and sg_data.is_dir(), "intake-data-dirs-missing")

    apl_commit = read_git_head_commit(apl_repo)
    sg_commit = read_git_head_commit(sg_repo)
    paper_bytes = paper_path.read_bytes()
    paper_sha256 = hashlib.sha256(paper_bytes).hexdigest()
    paper_text = paper_bytes.decode("utf-8")
    m_ds = _DATASET_SHA_RE.search(paper_text)
    _require(m_ds is not None, "paper-dataset-sha256-missing")
    dataset_sha256 = m_ds.group(1)

    _require(apl_commit == pins["apl_md_commit"], "pin-mismatch:apl_md_commit")
    _require(sg_commit == pins["simgrammar_commit"], "pin-mismatch:simgrammar_commit")
    _require(len(paper_bytes) == pins["simgrammar_paper_bytes"], "pin-mismatch:simgrammar_paper_bytes")
    _require(paper_sha256 == pins["simgrammar_paper_sha256"], "pin-mismatch:simgrammar_paper_sha256")
    _require(dataset_sha256 == pins["simgrammar_paper_dataset_sha256"], "pin-mismatch:dataset_sha256")

    return {
        "apl_md_commit": apl_commit,
        "simgrammar_commit": sg_commit,
        "simgrammar_paper_sha256": paper_sha256,
        "simgrammar_paper_bytes": len(paper_bytes),
        "simgrammar_paper_dataset_sha256": dataset_sha256,
        "pinned_inputs_verified": True,
    }


def build_paper_reconciliation(sg_res: dict[str, Any]) -> dict[str, Any]:
    """Reconcile `simgrammar_paper.md` (v0.8) headline metrics against our pure-Q recount."""
    cnt = sg_res["counts"]
    gm = sg_res["game_mechanic_bipartite"]
    tm = sg_res["technique_mechanic_bipartite"]
    mr = sg_res["mechanic_relation_graph"]
    sp = sg_res["spearman_rubric_correlations"]
    nulls = sg_res["nulls"]

    pre2k_frac = Fraction(gm["pre2000_vocab_count"], cnt["mechanics"])
    p2010_frac = (
        Fraction(gm["post2010_from_pre2000_uses"], gm["post2010_uses"])
        if gm["post2010_uses"] > 0
        else Fraction(0, 1)
    )
    cooc_frac = Fraction(gm["cooc_pairs"], gm["total_possible_pairs"])
    unl_frac = Fraction(tm["unlinked_uses"], gm["gm_edges"])

    checks = {
        "games_179": cnt["games"] == 179,
        "mechanics_199": cnt["mechanics"] == 199,
        "families_21": cnt["families"] == 21,
        "techniques_46": cnt["techniques"] == 46,
        "live_opportunities_42_of_43_yaml": (
            cnt["total_opportunity_files"] == 43
            and cnt["live_opportunities"] == 42
            and cnt["deprecated_opportunities"] == 1
        ),
        "gm_edges_2069": gm["gm_edges"] == 2069,
        "tm_edges_225": tm["tm_edges"] == 225,
        "unlinked_mechs_97": tm["unlinked_mechs"] == 97,
        "unlinked_uses_approx_49pct": Fraction(48, 100) <= unl_frac <= Fraction(50, 100),
        "pre2000_vocab_approx_69pct": Fraction(68, 100) <= pre2k_frac <= Fraction(70, 100),
        "post2010_old_uses_approx_84pct": Fraction(84, 100) <= p2010_frac <= Fraction(85, 100),
        "cooc_approx_28_5pct": Fraction(28, 100) <= cooc_frac <= Fraction(29, 100),
        "mech_relations_16_4_102_11_iso_55": (
            mr["typed_edge_counts"] == {"requires": 16, "specializes": 4, "synergy": 102, "tension": 11}
            and mr["isolated_mechs"] == 55
        ),
        "spearman_em_lg_neg_approx_042": (
            sp["emergence_vs_legibility_sign"] == -1
            and sp["emergence_vs_legibility_abs_rho_dec6"].startswith("0.417")
        ),
        "spearman_em_tn_pos_approx_061": (
            sp["emergence_vs_tuning_sign"] == 1
            and sp["emergence_vs_tuning_abs_rho_dec6"].startswith("0.611")
        ),
    }

    return {
        "paper_version": "0.8",
        "paper_date": "2026-11-04",
        "all_headline_counts_matched": all(checks.values()),
        "checks": checks,
        "opportunity_43_vs_42_resolution": (
            "data/opportunities/ holds 43 YAML files: 42 live opportunities plus 1 deprecated file "
            "(weather-coupled-grids.yaml, superseded_by: learned-weather-layer)."
        ),
        "global_family_renyi2_audit_nuance": (
            "While the top 4 families carry 96/225 technique edges and within-technique family "
            f"specialization is highly significant (p={nulls['within_tech_r2_p']}), pooled global "
            f"family Renyi-2 concentration is {nulls['global_family_r2_status']} "
            f"(p={nulls['global_family_r2_p']}, <= {nulls['global_family_r2_p_upper_dec6']}) "
            "once catalog family sizes are preserved by mechanic-family permutation."
        ),
    }


def assemble_certificate(
    apl_res: dict[str, Any],
    sg_res: dict[str, Any],
    comparison: dict[str, Any],
    audit_gate: dict[str, Any],
    provenance: dict[str, Any],
    execution_mode: str,
    live_corpus_recounted: bool,
    include_paper_reconciliation: bool = True,
) -> dict[str, Any]:
    """Assemble fail-closed deterministic AUDIT-099 certificate envelope."""
    _require(
        execution_mode in ("live_corpus_recount", "standalone_fixture_replay"),
        f"invalid-exec-mode:{execution_mode}",
    )
    _require(isinstance(live_corpus_recounted, bool), "live-flag-bool")
    _require(
        live_corpus_recounted == (execution_mode == "live_corpus_recount"),
        "live-flag-mode-mismatch",
    )
    _require(
        type(audit_gate.get("certified")) is bool and audit_gate["certified"],
        "audit-gate-not-certified",
    )

    core_payload = {
        "apl_summary": apl_res,
        "simgrammar_summary": sg_res,
        "law5_comparison": comparison,
        "audit_gate": audit_gate,
    }
    payload_sha = canonical_sha256(core_payload)

    envelope: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "honest_tier": HONEST_TIER,
        "execution_mode": execution_mode,
        "live_corpus_recounted": live_corpus_recounted,
        "provenance": provenance,
        "apl_summary": apl_res,
        "simgrammar_summary": sg_res,
        "law5_comparison": comparison,
        "audit_gate": audit_gate,
        "payload_sha256": payload_sha,
    }
    if include_paper_reconciliation:
        envelope["paper_reconciliation"] = build_paper_reconciliation(sg_res)

    envelope["certificate_sha256"] = canonical_sha256(envelope)
    return envelope


# Exact live-recounted core payload pinned from intake-2026-11-22 (n_shuffles=200, seed=20261122).
# Used ONLY when `--standalone` is explicitly passed (`live_corpus_recounted: false`).
STANDALONE_PINNED_FIXTURE: dict[str, Any] = {
    "apl_summary": {
        "articulation_count": 0,
        "biconnected_zero_cuts": True,
        "bridge_count": 0,
        "confidence_counts": {"high": 84, "low": 54, "medium": 115},
        "down_edges": 1200,
        "e_uniq": 2265,
        "giant_scc_full": 250,
        "giant_scc_full_frac": "250/253",
        "giant_scc_lower": 228,
        "giant_scc_lower_frac": "228/253",
        "lower_down": 1172,
        "lower_down_ratio": "586/705",
        "lower_e_count": 1410,
        "lower_tier_matrix": [[324, 190, 22], [29, 527, 140], [0, 14, 164]],
        "lower_up": 238,
        "non_giant_sccs_full": [[229, 230], [253]],
        "nulls": {
            "lower_down_ge_obs": 0,
            "lower_down_null_mean_dec4": "880.5100",
            "lower_down_p": "1/201",
            "lower_down_p_upper_dec6": "0.004976",
            "n_shuffles": 200,
            "recip_ge_obs": 0,
            "recip_null_mean_dec4": "99.1300",
            "recip_p": "1/201",
            "recip_p_upper_dec6": "0.004976",
            "same_tier_ge_obs": 0,
            "same_tier_null_mean_dec4": "884.2050",
            "same_tier_p": "1/201",
            "same_tier_p_upper_dec6": "0.004976",
            "seed": 20261122,
        },
        "oneway_directed_edges": 1251,
        "raw_wikilinks": 2370,
        "recip_directed_edges": 1014,
        "recip_pairs": 507,
        "reciprocity_dec6": "0.447682",
        "reciprocity_ratio": "338/755",
        "same_tier_edges": 1636,
        "same_tier_ratio": "1636/2265",
        "scc_count_full": 3,
        "scc_count_lower": 24,
        "self_loops": [137],
        "tier_matrix_full": [[590, 199, 22], [140, 808, 140], [3, 125, 238]],
        "undir_components": 1,
        "undir_edges": 1758,
        "unresolved_links": 0,
        "up_edges": 1065,
        "upper_down": 41,
        "upper_e_count": 921,
        "upper_lower_overlap": 68,
        "upper_up": 880,
        "v_count": 253,
    },
    "simgrammar_summary": {
        "counts": {
            "deprecated_opportunities": 1,
            "deprecated_opportunity_details": [
                {"id": "weather-coupled-grids", "superseded_by": "learned-weather-layer"}
            ],
            "families": 21,
            "games": 179,
            "live_opportunities": 42,
            "mechanics": 199,
            "sources": 770,
            "techniques": 46,
            "total_opportunity_files": 43,
        },
        "game_mechanic_bipartite": {
            "cooc_dec4": "0.2845",
            "cooc_pairs": 5605,
            "cooc_share": "5605/19701",
            "core_edges": 598,
            "gm_edges": 2069,
            "post2010_from_pre2000_uses": 1197,
            "post2010_old_dec4": "0.8447",
            "post2010_old_share": "1197/1417",
            "post2010_uses": 1417,
            "pre2000_vocab_count": 137,
            "pre2000_vocab_dec4": "0.6884",
            "pre2000_vocab_share": "137/199",
            "supporting_edges": 1471,
            "total_possible_pairs": 19701,
        },
        "mechanic_relation_graph": {
            "articulation_count": 71,
            "bridge_count": 120,
            "dep_directed_edges": 20,
            "dep_nontrivial_sccs": [],
            "dep_strict_dag": True,
            "isolated_mechs": 55,
            "overlapping_multitype_pairs": [
                ["budget-treasury", "loans-debt"],
                ["comparative-histograms", "design-performance-rating"],
                ["natural-selection", "trait-inheritance"],
                ["rci-demand", "zoning"],
            ],
            "typed_edge_counts": {"requires": 16, "specializes": 4, "synergy": 102, "tension": 11},
            "typed_edge_total": 133,
            "undir_components": 73,
            "undir_mech_edges": 129,
        },
        "nulls": {
            "cooc_le_obs": 0,
            "cooc_null_mean_pairs_dec2": "7110.42",
            "cooc_null_mean_share_dec4": "0.3609",
            "cooc_p": "1/201",
            "cooc_p_upper_dec6": "0.004976",
            "global_family_r2_ge_obs": 29,
            "global_family_r2_null_mean_dec6": "0.068352",
            "global_family_r2_p": "10/67",
            "global_family_r2_p_upper_dec6": "0.149254",
            "global_family_r2_status": "NON_SIGNIFICANT_AT_ALPHA_005",
            "n_shuffles": 200,
            "seed": 20261122,
            "spearman_em_lg_le_obs": 0,
            "spearman_em_lg_p": "1/201",
            "spearman_em_lg_p_upper_dec6": "0.004976",
            "spearman_em_tn_ge_obs": 0,
            "spearman_em_tn_p": "1/201",
            "spearman_em_tn_p_upper_dec6": "0.004976",
            "within_tech_r2_ge_obs": 0,
            "within_tech_r2_null_mean_dec6": "0.223204",
            "within_tech_r2_p": "1/201",
            "within_tech_r2_p_upper_dec6": "0.004976",
        },
        "spearman_rubric_correlations": {
            "emergence_vs_legibility_abs_rho_dec6": "0.417917",
            "emergence_vs_legibility_rho_sq": "225386613001/1290470145216",
            "emergence_vs_legibility_sign": -1,
            "emergence_vs_tuning_abs_rho_dec6": "0.611911",
            "emergence_vs_tuning_rho_sq": "17038976983/45505823736",
            "emergence_vs_tuning_sign": 1,
        },
        "technique_mechanic_bipartite": {
            "global_family_eff_diversity_d2_dec4": "13.4892",
            "global_family_renyi2": "139/1875",
            "global_family_renyi2_dec6": "0.074133",
            "tm_edges": 225,
            "top_families": [
                ["agents-behavior", 27],
                ["narrative-generation", 24],
                ["physics-materials", 24],
                ["control-automation", 21],
                ["space-construction", 16],
                ["social-relations", 15],
            ],
            "touched_mechs": 102,
            "unlinked_mechs": 97,
            "unlinked_uses": 1008,
            "unlinked_uses_dec4": "0.4871",
            "unlinked_uses_share": "1008/2069",
            "within_tech_family_renyi2": "403/1245",
            "within_tech_family_renyi2_dec6": "0.323694",
        },
    },
}


def run_live_audit(
    intake_root: Path,
    n_shuffles: int = 200,
    seed: int = 20261122,
    expected_pins: dict[str, Any] | None = None,
    include_paper_reconciliation: bool = True,
) -> dict[str, Any]:
    """Run full live raw-corpus recount, null tests, and fail-closed certification."""
    provenance = verify_intake_provenance(intake_root, expected_pins=expected_pins)
    apl_raw = oracle.parse_apl_corpus(intake_root / "repos" / "apl-md" / "Patterns")
    sg_raw = oracle.parse_simgrammar_corpus(intake_root / "repos" / "simgrammar" / "data")
    apl_res = oracle.analyze_apl_graph_live(apl_raw, n_shuffles=n_shuffles, seed=seed)
    sg_res = oracle.analyze_simgrammar_live(sg_raw, n_shuffles=n_shuffles, seed=seed)
    comparison = oracle.build_honest_structural_comparison(apl_res, sg_res)
    audit_gate = oracle.certify_pattern_sim_grammar_audit(apl_res, sg_res, comparison)
    return assemble_certificate(
        apl_res=apl_res,
        sg_res=sg_res,
        comparison=comparison,
        audit_gate=audit_gate,
        provenance=provenance,
        execution_mode="live_corpus_recount",
        live_corpus_recounted=True,
        include_paper_reconciliation=include_paper_reconciliation,
    )


def run_standalone_replay() -> dict[str, Any]:
    """Replay pinned offline fixture through the exact same comparison & conservation certifier."""
    apl_res = json.loads(json.dumps(STANDALONE_PINNED_FIXTURE["apl_summary"]))
    sg_res = json.loads(json.dumps(STANDALONE_PINNED_FIXTURE["simgrammar_summary"]))
    comparison = oracle.build_honest_structural_comparison(apl_res, sg_res)
    audit_gate = oracle.certify_pattern_sim_grammar_audit(apl_res, sg_res, comparison)
    provenance = {
        "apl_md_commit": PINNED_APL_COMMIT,
        "simgrammar_commit": PINNED_SIMGRAMMAR_COMMIT,
        "simgrammar_paper_sha256": PINNED_PAPER_SHA256,
        "simgrammar_paper_bytes": PINNED_PAPER_BYTES,
        "simgrammar_paper_dataset_sha256": PINNED_PAPER_DATASET_SHA256,
        "pinned_inputs_verified": False,
        "replay_note": "Offline fixture replay; raw corpora were NOT re-read in this invocation.",
    }
    return assemble_certificate(
        apl_res=apl_res,
        sg_res=sg_res,
        comparison=comparison,
        audit_gate=audit_gate,
        provenance=provenance,
        execution_mode="standalone_fixture_replay",
        live_corpus_recounted=False,
        include_paper_reconciliation=True,
    )


def format_human_summary(cert: dict[str, Any]) -> str:
    """Deterministic human-readable summary of AUDIT-099 certificate."""
    apl = cert["apl_summary"]
    sg = cert["simgrammar_summary"]
    cmp_d = cert["law5_comparison"]
    mr = sg["mechanic_relation_graph"]
    lines = [
        f"AUDIT-099 Pattern-Language & Simulation-Grammar Audit ({cert['honest_tier']})",
        f"Execution Mode : {cert['execution_mode']} (live_corpus_recounted={cert['live_corpus_recounted']})",
        f"Certified      : {cert['audit_gate']['certified']} (min B={cert['audit_gate']['multi_shuffle_min_b_verified']})",
        f"APL-MD         : V={apl['v_count']}, E_dir={apl['e_uniq']}, E_undir={apl['undir_edges']}, "
        f"giant_SCC_lower={apl['giant_scc_lower_frac']}, biconnected={apl['biconnected_zero_cuts']} "
        f"(arts={apl['articulation_count']}, bridges={apl['bridge_count']})",
        f"SimGrammar     : games={sg['counts']['games']}, mechs={sg['counts']['mechanics']}, "
        f"techs={sg['counts']['techniques']}, opps={sg['counts']['live_opportunities']}/{sg['counts']['total_opportunity_files']} "
        f"(1 deprecated), gm_edges={sg['game_mechanic_bipartite']['gm_edges']}, tm_edges={sg['technique_mechanic_bipartite']['tm_edges']}",
        f"SG Mech Graph  : dep_DAG={mr['dep_strict_dag']}, isolated={mr['isolated_mechs']}, "
        f"comps={mr['undir_components']}, arts={mr['articulation_count']}, bridges={mr['bridge_count']}/{mr['undir_mech_edges']}",
        f"SG Global R2   : {sg['technique_mechanic_bipartite']['global_family_renyi2']} "
        f"(p={sg['nulls']['global_family_r2_p']}, <= {sg['nulls']['global_family_r2_p_upper_dec6']}, "
        f"{sg['nulls']['global_family_r2_status']})",
        f"SG Within R2   : {sg['technique_mechanic_bipartite']['within_tech_family_renyi2']} "
        f"(p={sg['nulls']['within_tech_r2_p']}, <= {sg['nulls']['within_tech_r2_p_upper_dec6']})",
        f"Law-5 Diverged : {cmp_d['topological_divergence_documented']}",
        f"Payload SHA256 : {cert['payload_sha256']}",
        f"Cert SHA256    : {cert['certificate_sha256']}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AUDIT-099 pure-Q pattern & simulation grammar certifier")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--live", action="store_true", help="Recount raw corpora directly from --intake-root (default)")
    mode.add_argument(
        "--standalone",
        action="store_true",
        help="Offline fixture replay (explicitly marks live_corpus_recounted=false)",
    )
    default_intake = Path(__file__).resolve().parent.parent / "intake-2026-11-22"
    parser.add_argument("--intake-root", type=Path, default=default_intake, help="Path to staged intake directory")
    parser.add_argument("--shuffles", type=int, default=200, help="Null shuffle count B (>= 100)")
    parser.add_argument("--seed", type=int, default=20261122, help="Deterministic integer PRNG seed")
    parser.add_argument("--json", action="store_true", help="Emit canonical JSON certificate to stdout")
    parser.add_argument("--write-cert", type=Path, default=None, help="Write canonical JSON certificate to file")
    args = parser.parse_args(argv)

    if args.standalone:
        _require(args.shuffles == 200 and args.seed == 20261122, "standalone-fixed-params")
        cert = run_standalone_replay()
    else:
        cert = run_live_audit(args.intake_root, n_shuffles=args.shuffles, seed=args.seed)

    rendered_json = json.dumps(cert, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if args.write_cert is not None:
        args.write_cert.write_text(rendered_json, encoding="utf-8")

    if args.json:
        sys.stdout.write(rendered_json)
    else:
        sys.stdout.write(format_human_summary(cert) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
