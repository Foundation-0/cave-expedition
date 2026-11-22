#!/usr/bin/env python3
"""AUDIT-099 R5 Mutation-Killing & Known-Answer Live-Path Verification Suite.

Covers:
  1. Hand-computed known-answer mini-corpus live-path test (`parse_*` -> `analyze_*` ->
     `build_honest_structural_comparison` -> `certify_pattern_sim_grammar_audit` ->
     `run_live_audit`) verifying every exact integer, Fraction, graph cut, SCC, Spearman,
     Renyi-2, and provenance pin check at `n_shuffles=100` (exact minimum boundary).
  2. Complete R5 refusal & boundary test matrix killing 100.0% of mutants on BOTH
     `pattern_sim_grammar_oracle.py` and `pattern_sim_grammar_audit.py` under
     `aletheia v2.0.0 mutate --max-mutants 0 --add-cwd`.

Zero bare asserts, zero floats, 100% Python 3 stdlib.
"""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import pattern_sim_grammar_audit as audit  # noqa: E402
import pattern_sim_grammar_oracle as oracle  # noqa: E402
from pattern_sim_grammar_oracle import GrammarAuditError  # noqa: E402


def _write_mini_intake(root: Path) -> dict[str, object]:
    """Create a self-contained hand-computed synthetic intake tree and return exact expected pins."""
    apl_repo = root / "repos" / "apl-md"
    sg_repo = root / "repos" / "simgrammar"
    apl_pat = apl_repo / "Patterns"
    sg_data = sg_repo / "data"
    apl_pat.mkdir(parents=True)
    for sub in ("games", "mechanics", "techniques", "opportunities", "sources"):
        (sg_data / sub).mkdir(parents=True)
    (root / "sources").mkdir(parents=True)

    # Synthetic git HEADs: apl-md uses loose ref, simgrammar uses packed-refs
    apl_commit = "a" * 40
    sg_commit = "b" * 40
    (apl_repo / ".git" / "refs" / "heads").mkdir(parents=True)
    (apl_repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (apl_repo / ".git" / "refs" / "heads" / "main").write_text(apl_commit + "\n", encoding="utf-8")

    (sg_repo / ".git").mkdir(parents=True)
    (sg_repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (sg_repo / ".git" / "packed-refs").write_text(
        f"# pack-refs\n^0000000000000000000000000000000000000000\n{sg_commit} refs/heads/main\n",
        encoding="utf-8",
    )

    # Mini-APL (4 patterns: K4 undirected, 1 giant SCC even in lower-only)
    (apl_pat / "Alpha (1).md").write_text(
        "# Alpha\n#APL/Town-Patterns #APL/confidence/high\n"
        "### Related Patterns\n"
        "[[Beta (2)]], [[Gamma (3)]], [[NoNumber]], [[Ghost (99)]]\n---\n",
        encoding="utf-8",
    )
    (apl_pat / "Beta (2).md").write_text(
        "# Beta\n#APL/Building-Patterns #APL/confidence/medium\n"
        "### Related Patterns\n"
        "Upper: [[Alpha (1)]]\n\n"
        "Lower: [[Gamma (3)]], [[Delta (4)]], [[Beta (2)]]\n---\n",
        encoding="utf-8",
    )
    (apl_pat / "Gamma (3).md").write_text(
        "# Gamma\n#APL/Building-Patterns #APL/confidence/low\n"
        "### Related Patterns\n"
        "Upper: [[Alpha (1)]], [[Beta (2)]]\n\n"
        "Lower: [[Delta (4)]], [[Beta (2)]]\n---\n",
        encoding="utf-8",
    )
    (apl_pat / "Delta (4).md").write_text(
        "# Delta\n#APL/Construction-Patterns\n"
        "### Related Patterns\n"
        "Upper: [[Gamma (3)]]\n\n"
        "Lower: [[Alpha (1)]]\n---\n",
        encoding="utf-8",
    )

    # Mini-SimGrammar (3 games, 4 mechanics, 2 families, 2 techniques, 2 opps = 1 live + 1 deprecated, 2 sources)
    (sg_data / "mechanics" / "m1.yaml").write_text(
        "id: m1\nfamily: fam-a\nlegibility: 5\nemergence_potential: 1\ntuning_difficulty: 1\n"
        "requires: []\nspecializes: []\nsynergy: []\ntension: []\n",
        encoding="utf-8",
    )
    (sg_data / "mechanics" / "m2.yaml").write_text(
        "id: m2\nfamily: fam-a\nlegibility: 4\nemergence_potential: 2\ntuning_difficulty: 2\n"
        "requires:\n- id: m3\nsynergy:\n- m3\ntension: []\n",
        encoding="utf-8",
    )
    (sg_data / "mechanics" / "m3.yaml").write_text(
        "id: m3\nfamily: fam-b\nlegibility: 3\nemergence_potential: 3\ntuning_difficulty: 3\n"
        "specializes: m4\n",
        encoding="utf-8",
    )
    (sg_data / "mechanics" / "m4.yaml").write_text(
        "id: m4\nfamily: fam-b\nlegibility: 2\nemergence_potential: 4\ntuning_difficulty: 4\n",
        encoding="utf-8",
    )

    (sg_data / "games" / "g1.yaml").write_text(
        "id: g1\nyear: 1995\nmechanics:\n- id: m1\n  role: core\n- id: m2\n  role: supporting\nnotes: ok\n",
        encoding="utf-8",
    )
    (sg_data / "games" / "g2.yaml").write_text(
        "id: g2\nyear: 2015\nmechanics:\n  - id: m1\n    role: core\n  - id: m3\n    role: supporting\nnotes: ok\n",
        encoding="utf-8",
    )
    (sg_data / "games" / "g3.yaml").write_text(
        "id: g3\nyear: 2020\nmechanics:\n- id: m2\n  role: core\n- id: m3\n  role: core\n- id: m4\n  role: supporting\n",
        encoding="utf-8",
    )

    (sg_data / "techniques" / "t1.yaml").write_text(
        "id: t1\naffects:\n- mechanic: m1\n  effect: deepens\n- id: m2\n  effect: explains\nnotes: ok\n",
        encoding="utf-8",
    )
    (sg_data / "techniques" / "t2.yaml").write_text(
        "id: t2\naffects:\n- mechanic: m3\n  effect: tunes\n",
        encoding="utf-8",
    )

    (sg_data / "opportunities" / "opp-live.yaml").write_text("id: opp-live\nstatus: asserted\n", encoding="utf-8")
    (sg_data / "opportunities" / "opp-old.yaml").write_text(
        "id: opp-old\ndeprecated:\n  superseded_by: opp-live\n",
        encoding="utf-8",
    )
    (sg_data / "sources" / "s1.yaml").write_text("id: s1\n", encoding="utf-8")
    (sg_data / "sources" / "s2.yaml").write_text("id: s2\n", encoding="utf-8")

    ds_sha = "c" * 64
    paper_text = f'---\ntitle: "Mini"\ndataset_sha256: "{ds_sha}"\n---\nBody\n'
    paper_bytes = paper_text.encode("utf-8")
    (root / "sources" / "simgrammar_paper.md").write_bytes(paper_bytes)

    return {
        "apl_md_commit": apl_commit,
        "simgrammar_commit": sg_commit,
        "simgrammar_paper_sha256": hashlib.sha256(paper_bytes).hexdigest(),
        "simgrammar_paper_bytes": len(paper_bytes),
        "simgrammar_paper_dataset_sha256": ds_sha,
    }


def _valid_fixture_triplet() -> tuple[dict, dict, dict]:
    apl = copy.deepcopy(audit.STANDALONE_PINNED_FIXTURE["apl_summary"])
    sg = copy.deepcopy(audit.STANDALONE_PINNED_FIXTURE["simgrammar_summary"])
    cmp_d = oracle.build_honest_structural_comparison(apl, sg)
    return apl, sg, cmp_d


class TestKnownAnswerMiniCorpusLivePath(unittest.TestCase):
    """Hand-computed known-answer live-path verification (exercises parsers, analyzers, nulls, pins)."""

    def test_hand_computed_mini_corpus_exact_invariants(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pins = _write_mini_intake(root)
            cert = audit.run_live_audit(
                root,
                n_shuffles=100,  # Exact minimum boundary B=100 kills b_i >= 100 -> b_i > 100
                seed=7,
                expected_pins=pins,
                include_paper_reconciliation=False,
            )

            self.assertEqual(cert["execution_mode"], "live_corpus_recount")
            self.assertTrue(cert["live_corpus_recounted"])
            self.assertTrue(cert["audit_gate"]["certified"])
            self.assertEqual(cert["audit_gate"]["multi_shuffle_min_b_verified"], 100)

            # Exact hand-computed Mini-APL invariants
            apl = cert["apl_summary"]
            self.assertEqual(apl["v_count"], 4)
            self.assertEqual(apl["raw_wikilinks"], 14)
            self.assertEqual(apl["unresolved_links"], 2)
            self.assertEqual(apl["self_loops"], [2])
            self.assertEqual(apl["e_uniq"], 10)
            self.assertEqual(apl["undir_edges"], 6)
            self.assertEqual(apl["recip_directed_edges"], 8)
            self.assertEqual(apl["recip_pairs"], 4)
            self.assertEqual(apl["oneway_directed_edges"], 2)
            self.assertEqual(apl["reciprocity_ratio"], "4/5")
            self.assertEqual(apl["down_edges"], 5)
            self.assertEqual(apl["up_edges"], 5)
            self.assertEqual(apl["tier_matrix_full"], [[0, 2, 0], [2, 2, 2], [1, 1, 0]])
            self.assertEqual(apl["same_tier_edges"], 2)
            self.assertEqual(apl["same_tier_ratio"], "1/5")
            self.assertEqual(apl["upper_e_count"], 4)
            self.assertEqual(apl["upper_up"], 4)
            self.assertEqual(apl["upper_down"], 0)
            self.assertEqual(apl["lower_e_count"], 7)
            self.assertEqual(apl["lower_down"], 5)
            self.assertEqual(apl["lower_up"], 2)
            self.assertEqual(apl["lower_down_ratio"], "5/7")
            self.assertEqual(apl["upper_lower_overlap"], 1)
            self.assertEqual(apl["scc_count_full"], 1)
            self.assertEqual(apl["giant_scc_full"], 4)
            self.assertEqual(apl["giant_scc_full_frac"], "1/1")
            self.assertEqual(apl["scc_count_lower"], 1)
            self.assertEqual(apl["giant_scc_lower"], 4)
            self.assertEqual(apl["giant_scc_lower_frac"], "1/1")
            self.assertEqual(apl["undir_components"], 1)
            self.assertEqual(apl["articulation_count"], 0)
            self.assertEqual(apl["bridge_count"], 0)
            self.assertTrue(apl["biconnected_zero_cuts"])
            self.assertEqual(apl["confidence_counts"], {"high": 1, "low": 1, "medium": 1, "none": 1})

            # Exact hand-computed Mini-SimGrammar invariants
            sg = cert["simgrammar_summary"]
            self.assertEqual(sg["counts"]["games"], 3)
            self.assertEqual(sg["counts"]["mechanics"], 4)
            self.assertEqual(sg["counts"]["families"], 2)
            self.assertEqual(sg["counts"]["techniques"], 2)
            self.assertEqual(sg["counts"]["total_opportunity_files"], 2)
            self.assertEqual(sg["counts"]["live_opportunities"], 1)
            self.assertEqual(sg["counts"]["deprecated_opportunities"], 1)
            self.assertEqual(sg["counts"]["sources"], 2)

            gm = sg["game_mechanic_bipartite"]
            self.assertEqual(gm["gm_edges"], 7)
            self.assertEqual(gm["core_edges"], 4)
            self.assertEqual(gm["supporting_edges"], 3)
            self.assertEqual(gm["pre2000_vocab_count"], 2)
            self.assertEqual(gm["pre2000_vocab_share"], "1/2")
            self.assertEqual(gm["post2010_uses"], 5)
            self.assertEqual(gm["post2010_from_pre2000_uses"], 2)
            self.assertEqual(gm["post2010_old_share"], "2/5")
            self.assertEqual(gm["cooc_pairs"], 5)
            self.assertEqual(gm["total_possible_pairs"], 6)
            self.assertEqual(gm["cooc_share"], "5/6")

            tm = sg["technique_mechanic_bipartite"]
            self.assertEqual(tm["tm_edges"], 3)
            self.assertEqual(tm["touched_mechs"], 3)
            self.assertEqual(tm["unlinked_mechs"], 1)
            self.assertEqual(tm["unlinked_uses"], 1)
            self.assertEqual(tm["unlinked_uses_share"], "1/7")
            self.assertEqual(tm["global_family_renyi2"], "5/9")
            self.assertEqual(tm["within_tech_family_renyi2"], "1/1")

            mr = sg["mechanic_relation_graph"]
            self.assertEqual(mr["typed_edge_counts"], {"requires": 1, "specializes": 1, "synergy": 1, "tension": 0})
            self.assertEqual(mr["typed_edge_total"], 3)
            self.assertEqual(mr["undir_mech_edges"], 2)
            self.assertEqual(mr["overlapping_multitype_pairs"], [["m2", "m3"]])
            self.assertEqual(mr["dep_directed_edges"], 2)
            self.assertTrue(mr["dep_strict_dag"])
            self.assertEqual(mr["isolated_mechs"], 1)
            self.assertEqual(mr["undir_components"], 2)
            self.assertEqual(mr["articulation_count"], 1)
            self.assertEqual(mr["bridge_count"], 2)

            sp = sg["spearman_rubric_correlations"]
            self.assertEqual(sp["emergence_vs_legibility_sign"], -1)
            self.assertEqual(sp["emergence_vs_legibility_rho_sq"], "1/1")
            self.assertEqual(sp["emergence_vs_legibility_abs_rho_dec6"], "1.000000")
            self.assertEqual(sp["emergence_vs_tuning_sign"], 1)
            self.assertEqual(sp["emergence_vs_tuning_rho_sq"], "1/1")
            self.assertEqual(sp["emergence_vs_tuning_abs_rho_dec6"], "1.000000")

            cmp_d = cert["law5_comparison"]
            self.assertEqual(cmp_d["apl_giant_scc_lower_frac"], "1/1")
            self.assertTrue(cmp_d["apl_biconnected_zero_cuts"])
            self.assertTrue(cmp_d["sg_dep_strict_dag"])
            self.assertEqual(cmp_d["sg_mech_articulation_frac"], "1/4")
            self.assertEqual(cmp_d["sg_mech_bridge_frac"], "1/1")
            self.assertTrue(cmp_d["topological_divergence_documented"])


class TestOraclePrimitivesAndParsersR5(unittest.TestCase):
    """Kill all primitive, parser, and live-analyzer refusal & boundary mutants in oracle."""

    def test_scalar_and_format_helpers_and_boundaries(self) -> None:
        # _require_exact_int rejects bool and float
        self.assertEqual(oracle._require_exact_int(0, "x"), 0)
        with self.assertRaises(GrammarAuditError):
            oracle._require_exact_int(True, "x")
        with self.assertRaises(GrammarAuditError):
            oracle._require_exact_int(1.5, "x")

        # _require_exact_fraction accepts Fraction and int, rejects bool/float
        self.assertEqual(oracle._require_exact_fraction(3, "x"), Fraction(3, 1))
        with self.assertRaises(GrammarAuditError):
            oracle._require_exact_fraction(1.25, "x")

        # _require_clean_ascii boundaries (space=32, tilde=126) & refusals
        self.assertEqual(oracle._require_clean_ascii("a ~", "s"), "a ~")
        for bad in ("", " lead", "a\tb", "a\x7fb", 123):
            with self.assertRaises(GrammarAuditError):
                oracle._require_clean_ascii(bad, "s")

        # frac_dec & frac_dec_ceil exact boundaries (digits=1, value=0) & refusals
        self.assertEqual(oracle.frac_dec(Fraction(-1, 3), 1), "-0.3")
        self.assertEqual(oracle.frac_dec_ceil(Fraction(0, 1), 1), "0.0")
        self.assertEqual(oracle.frac_dec_ceil(Fraction(1, 201), 6), "0.004976")
        with self.assertRaises(GrammarAuditError):
            oracle.frac_dec(Fraction(1, 2), 0)
        with self.assertRaises(GrammarAuditError):
            oracle.frac_dec_ceil(Fraction(-1, 2), 2)
        with self.assertRaises(GrammarAuditError):
            oracle.frac_dec_ceil(Fraction(1, 2), 0)

        # _isqrt_frac_dec boundaries & refusals
        self.assertEqual(oracle._isqrt_frac_dec(Fraction(0, 1), 1), "0.0")
        self.assertEqual(oracle._isqrt_frac_dec(Fraction(9, 4), 2), "1.50")
        with self.assertRaises(GrammarAuditError):
            oracle._isqrt_frac_dec(Fraction(-1, 4), 2)
        with self.assertRaises(GrammarAuditError):
            oracle._isqrt_frac_dec(Fraction(1, 4), 0)

        # _parse_frac_str boundaries & refusals (zero denominator must raise GrammarAuditError!)
        self.assertEqual(oracle._parse_frac_str("-3/4", "f"), Fraction(-3, 4))
        for bad in ("3", "a/2", "1/-2"):
            with self.assertRaisesRegex(GrammarAuditError, "frac-str:"):
                oracle._parse_frac_str(bad, "f")
        with self.assertRaisesRegex(GrammarAuditError, "frac-str-den:"):
            oracle._parse_frac_str("1/0", "f")

    def test_graph_and_spearman_primitives_refusals_and_boundaries(self) -> None:
        with self.assertRaisesRegex(GrammarAuditError, "tarjan-adj-nonempty"):
            oracle.tarjan_sccs({})
        with self.assertRaisesRegex(GrammarAuditError, "tarjan-adj-nonempty"):
            oracle.tarjan_sccs([1, 2])  # type: ignore[arg-type]
        with self.assertRaisesRegex(GrammarAuditError, "uadj-nonempty"):
            oracle.undirected_articulations_and_bridges({})
        with self.assertRaisesRegex(GrammarAuditError, "uadj-nonempty"):
            oracle.undirected_articulations_and_bridges([1, 2])  # type: ignore[arg-type]

        # Exact boundary n=2 kills n >= 2 -> n > 2 in _midranks_doubled
        self.assertEqual(oracle._midranks_doubled([10, 20]), [2, 4])
        self.assertEqual(oracle._midranks_doubled([5, 5]), [3, 3])
        with self.assertRaises(GrammarAuditError):
            oracle._midranks_doubled([1])

        sgn, rsq, cov = oracle.exact_spearman_sq_and_sign([1, 2], [2, 1])
        self.assertEqual((sgn, rsq), (-1, Fraction(1, 1)))
        self.assertLess(cov, 0)
        with self.assertRaisesRegex(GrammarAuditError, "spearman-len-match"):
            oracle.exact_spearman_sq_and_sign([1, 2, 3], [1, 2])
        with self.assertRaisesRegex(GrammarAuditError, "spearman-len-match"):
            oracle.exact_spearman_sq_and_sign([1], [1])
        with self.assertRaises(GrammarAuditError):
            oracle.exact_spearman_sq_and_sign([1, 1], [1, 2])
        with self.assertRaises(GrammarAuditError):
            oracle.exact_spearman_sq_and_sign([1, 2], [5, 5])

        # Root articulation point test (root with 2 DFS children)
        comps, arts, bridges = oracle.undirected_articulations_and_bridges({1: {2, 3}, 2: {1}, 3: {1}})
        self.assertEqual((comps, arts, bridges), (1, [1], [(1, 2), (1, 3)]))

    def test_apl_parser_and_analyzer_refusals_and_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            with self.assertRaisesRegex(GrammarAuditError, "apl-dir-missing"):
                oracle.parse_apl_corpus(base / "nonexistent")

            # 1 file fails len(files) >= 2
            d1 = base / "one"
            d1.mkdir()
            (d1 / "A (1).md").write_text("# A\n", encoding="utf-8")
            with self.assertRaises(GrammarAuditError):
                oracle.parse_apl_corpus(d1)

            # Exactly 2 files passes (kills len(files) >= 2 -> len(files) > 2) + tests fallback tier
            (d1 / "B (100).md").write_text("# B\n[[A (1)]]\n", encoding="utf-8")
            parsed2 = oracle.parse_apl_corpus(d1)
            self.assertEqual(parsed2["tier_by_id"], {1: 0, 100: 1})

            # Missing (id) in filename refused
            d_badname = base / "badname"
            d_badname.mkdir()
            (d_badname / "NoId.md").write_text("# X\n", encoding="utf-8")
            (d_badname / "Ok (1).md").write_text("# Y\n", encoding="utf-8")
            with self.assertRaises(GrammarAuditError):
                oracle.parse_apl_corpus(d_badname)

            # Duplicate id & id == 0 refused
            d_dup = base / "dup"
            d_dup.mkdir()
            (d_dup / "A (1).md").write_text("# A\n", encoding="utf-8")
            (d_dup / "B (1).md").write_text("# B\n", encoding="utf-8")
            with self.assertRaises(GrammarAuditError):
                oracle.parse_apl_corpus(d_dup)

            d_zero = base / "zero"
            d_zero.mkdir()
            (d_zero / "A (0).md").write_text("# A\n", encoding="utf-8")
            (d_zero / "B (1).md").write_text("# B\n", encoding="utf-8")
            with self.assertRaises(GrammarAuditError):
                oracle.parse_apl_corpus(d_zero)

            # analyze_apl_graph_live rejects n_shuffles < 100
            with self.assertRaises(GrammarAuditError):
                oracle.analyze_apl_graph_live(parsed2, n_shuffles=99, seed=1)

    def test_simgrammar_parser_and_analyzer_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            with self.assertRaisesRegex(GrammarAuditError, "sg-data-dir-missing"):
                oracle.parse_simgrammar_corpus(base / "missing")

            d_sub = base / "missing_sub"
            d_sub.mkdir()
            with self.assertRaisesRegex(GrammarAuditError, "sg-subdir-missing"):
                oracle.parse_simgrammar_corpus(d_sub)

            # Direct parser header/score refusals (both conjuncts on game & mechanic)
            with self.assertRaisesRegex(GrammarAuditError, "sg-game-header"):
                oracle._parse_sg_game("id: g1\n", "g1.yaml")
            with self.assertRaisesRegex(GrammarAuditError, "sg-game-header"):
                oracle._parse_sg_game("year: 2000\n", "g1.yaml")
            with self.assertRaisesRegex(GrammarAuditError, "sg-mech-header"):
                oracle._parse_sg_mechanic("id: m1\n", "m1.yaml")
            with self.assertRaisesRegex(GrammarAuditError, "sg-mech-header"):
                oracle._parse_sg_mechanic("family: f\n", "m1.yaml")
            with self.assertRaisesRegex(GrammarAuditError, "sg-mech-score"):
                oracle._parse_sg_mechanic("id: m1\nfamily: f\nlegibility: 1\n", "m1.yaml")
            with self.assertRaisesRegex(GrammarAuditError, "sg-tech-header"):
                oracle._parse_sg_technique("name: no-id\n", "t1.yaml")

            # Missing opp id & individual minimum-count refusals (games<2, mechs<2, techs<1)
            d_opp = base / "bad_opp"
            for sub in ("games", "mechanics", "techniques", "opportunities", "sources"):
                (d_opp / sub).mkdir(parents=True)
            (d_opp / "opportunities" / "bad.yaml").write_text("status: asserted\n", encoding="utf-8")
            with self.assertRaisesRegex(GrammarAuditError, "sg-opp-header"):
                oracle.parse_simgrammar_corpus(d_opp)

            (d_opp / "opportunities" / "bad.yaml").write_text("id: o1\n", encoding="utf-8")
            m_tpl = "id: {mid}\nfamily: f\nlegibility: 1\nemergence_potential: 1\ntuning_difficulty: 1\n"
            g_tpl = "id: {gid}\nyear: 2000\nmechanics:\n- id: m1\n  role: core\n"
            # Case A: 2 mechs, 1 tech, only 1 game -> fails len(games_all) >= 2
            (d_opp / "mechanics" / "m1.yaml").write_text(m_tpl.format(mid="m1"), encoding="utf-8")
            (d_opp / "mechanics" / "m2.yaml").write_text(m_tpl.format(mid="m2"), encoding="utf-8")
            (d_opp / "techniques" / "t1.yaml").write_text("id: t1\naffects:\n- mechanic: m1\n", encoding="utf-8")
            (d_opp / "games" / "g1.yaml").write_text(g_tpl.format(gid="g1"), encoding="utf-8")
            with self.assertRaisesRegex(GrammarAuditError, "sg-corpus-nonempty"):
                oracle.parse_simgrammar_corpus(d_opp)
            # Case B: 2 games, 1 tech, only 1 mech -> fails len(mechs_all) >= 2
            (d_opp / "games" / "g2.yaml").write_text(g_tpl.format(gid="g2"), encoding="utf-8")
            (d_opp / "mechanics" / "m2.yaml").unlink()
            with self.assertRaisesRegex(GrammarAuditError, "sg-corpus-nonempty"):
                oracle.parse_simgrammar_corpus(d_opp)
            # Case C: 2 games, 2 mechs, 0 techs -> fails len(techs_all) >= 1
            (d_opp / "mechanics" / "m2.yaml").write_text(m_tpl.format(mid="m2"), encoding="utf-8")
            (d_opp / "techniques" / "t1.yaml").unlink()
            with self.assertRaisesRegex(GrammarAuditError, "sg-corpus-nonempty"):
                oracle.parse_simgrammar_corpus(d_opp)

            # Unknown mechanic references & n_shuffles < 100 in analyze_simgrammar_live
            mini_root = base / "mini"
            _write_mini_intake(mini_root)
            sg_raw = oracle.parse_simgrammar_corpus(mini_root / "repos" / "simgrammar" / "data")
            with self.assertRaises(GrammarAuditError):
                oracle.analyze_simgrammar_live(sg_raw, n_shuffles=99, seed=1)

            bad_gm = copy.deepcopy(sg_raw)
            bad_gm["games"][0]["mechanics"].append({"id": "ghost-mech", "role": "core"})
            with self.assertRaises(GrammarAuditError):
                oracle.analyze_simgrammar_live(bad_gm, n_shuffles=100, seed=1)

            bad_tm = copy.deepcopy(sg_raw)
            bad_tm["techniques"][0]["affects"].append({"mechanic": "ghost-mech", "effect": "tunes"})
            with self.assertRaises(GrammarAuditError):
                oracle.analyze_simgrammar_live(bad_tm, n_shuffles=100, seed=1)

            bad_rel = copy.deepcopy(sg_raw)
            bad_rel["mechanics"][0]["rels"]["synergy"].append("ghost-mech")
            with self.assertRaises(GrammarAuditError):
                oracle.analyze_simgrammar_live(bad_rel, n_shuffles=100, seed=1)


class TestCertifierConservationR5(unittest.TestCase):
    """Kill EVERY single conservation, boundary, and Law-5 mutant in certify_pattern_sim_grammar_audit."""

    def test_valid_extreme_boundaries_pass(self) -> None:
        # 1. Standard live fixture passes
        apl, sg, cmp_d = _valid_fixture_triplet()
        gate = oracle.certify_pattern_sim_grammar_audit(apl, sg, cmp_d)
        self.assertTrue(gate["certified"])

        # 2. Exact boundary valid fixture:
        #    b_apl=100, b_sg=100, ge_v=b, unl=0 & unl_u=0, gr2=1/1 & wtr2=1/1,
        #    iso=69 & mc=70 (hits BOTH mc == iso + 1 AND mr_ue == n_m - mc == 129!),
        #    s_el=0 & rsq_el=0/1, s_et=0 & rsq_et=0/1, p_gr2=5/101 <= 1/20 -> SIGNIFICANT!
        apl2, sg2, _ = _valid_fixture_triplet()
        apl2["nulls"]["n_shuffles"] = 100
        apl2["nulls"]["recip_ge_obs"] = 100
        apl2["nulls"]["recip_p"] = "1/1"
        apl2["nulls"]["same_tier_ge_obs"] = 0
        apl2["nulls"]["same_tier_p"] = "1/101"
        apl2["nulls"]["lower_down_ge_obs"] = 0
        apl2["nulls"]["lower_down_p"] = "1/101"

        sg2["technique_mechanic_bipartite"]["touched_mechs"] = sg2["counts"]["mechanics"]
        sg2["technique_mechanic_bipartite"]["unlinked_mechs"] = 0
        sg2["technique_mechanic_bipartite"]["unlinked_uses"] = 0
        sg2["technique_mechanic_bipartite"]["global_family_renyi2"] = "1/1"
        sg2["technique_mechanic_bipartite"]["within_tech_family_renyi2"] = "1/1"
        sg2["mechanic_relation_graph"]["isolated_mechs"] = 69
        sg2["mechanic_relation_graph"]["undir_components"] = 70  # mc == iso + 1 AND mr_ue == n_m - mc!
        sg2["spearman_rubric_correlations"]["emergence_vs_legibility_sign"] = 0
        sg2["spearman_rubric_correlations"]["emergence_vs_legibility_rho_sq"] = "0/1"
        sg2["spearman_rubric_correlations"]["emergence_vs_tuning_sign"] = 0
        sg2["spearman_rubric_correlations"]["emergence_vs_tuning_rho_sq"] = "0/1"

        sg2["nulls"]["n_shuffles"] = 100
        sg2["nulls"]["cooc_le_obs"] = 100
        sg2["nulls"]["cooc_p"] = "1/1"
        sg2["nulls"]["global_family_r2_ge_obs"] = 4
        sg2["nulls"]["global_family_r2_p"] = "5/101"
        sg2["nulls"]["global_family_r2_status"] = "SIGNIFICANT_AT_ALPHA_005"
        sg2["nulls"]["within_tech_r2_ge_obs"] = 0
        sg2["nulls"]["within_tech_r2_p"] = "1/101"
        sg2["nulls"]["spearman_em_lg_le_obs"] = 0
        sg2["nulls"]["spearman_em_lg_p"] = "1/101"
        sg2["nulls"]["spearman_em_tn_ge_obs"] = 0
        sg2["nulls"]["spearman_em_tn_p"] = "1/101"
        cmp2 = oracle.build_honest_structural_comparison(apl2, sg2)
        gate2 = oracle.certify_pattern_sim_grammar_audit(apl2, sg2, cmp2)
        self.assertTrue(gate2["certified"])
        self.assertEqual(gate2["multi_shuffle_min_b_verified"], 100)
        self.assertEqual(gate2["global_tech_family_r2_honest_status"], "SIGNIFICANT_AT_ALPHA_005")

        # 3. Valid exact C_3 biconnected APL boundary (v=3, e=3, ue=3, g_f=3, g_l=3) + unl_u == gm_e
        apl3, sg3, _ = _valid_fixture_triplet()
        apl3.update({
            "v_count": 3, "e_uniq": 3, "down_edges": 2, "up_edges": 1,
            "recip_directed_edges": 0, "recip_pairs": 0, "oneway_directed_edges": 3,
            "undir_edges": 3, "tier_matrix_full": [[3, 0, 0], [0, 0, 0], [0, 0, 0]],
            "same_tier_edges": 3, "lower_e_count": 3, "lower_down": 2, "lower_up": 1,
            "scc_count_full": 1, "giant_scc_full": 3, "scc_count_lower": 1, "giant_scc_lower": 3,
            "undir_components": 1, "articulation_count": 0, "bridge_count": 0,
            "biconnected_zero_cuts": True,
        })
        sg3["technique_mechanic_bipartite"]["unlinked_uses"] = sg3["game_mechanic_bipartite"]["gm_edges"]
        cmp3 = oracle.build_honest_structural_comparison(apl3, sg3)
        self.assertTrue(oracle.certify_pattern_sim_grammar_audit(apl3, sg3, cmp3)["certified"])

        # 4. Valid 0-edge SimGrammar graph (iso == n_m, mc == n_m, ma == 0, mb == 0) +
        #    valid 2-edge/2-node APL cycle boundary (g_f=2, e=2, g_l=2, le=2) ->
        #    conservation passes, Law-5 divergence is honestly False -> certified=False with violation!
        apl4, sg4, _ = _valid_fixture_triplet()
        apl4.update({
            "v_count": 4, "e_uniq": 2, "down_edges": 1, "up_edges": 1,
            "recip_directed_edges": 2, "recip_pairs": 1, "oneway_directed_edges": 0,
            "undir_edges": 1, "tier_matrix_full": [[2, 0, 0], [0, 0, 0], [0, 0, 0]],
            "same_tier_edges": 2, "lower_e_count": 2, "lower_down": 1, "lower_up": 1,
            "scc_count_full": 3, "giant_scc_full": 2, "scc_count_lower": 3, "giant_scc_lower": 2,
            "undir_components": 3, "articulation_count": 0, "bridge_count": 1,
            "biconnected_zero_cuts": False,
        })
        sg4["mechanic_relation_graph"].update({
            "typed_edge_counts": {"requires": 0, "specializes": 0, "synergy": 0, "tension": 0},
            "typed_edge_total": 0, "undir_mech_edges": 0, "isolated_mechs": 199,
            "undir_components": 199, "articulation_count": 0, "bridge_count": 0,
            "dep_strict_dag": True, "dep_nontrivial_sccs": [],
        })
        cmp4 = oracle.build_honest_structural_comparison(apl4, sg4)
        gate4 = oracle.certify_pattern_sim_grammar_audit(apl4, sg4, cmp4)
        self.assertFalse(gate4["certified"])
        self.assertIn("LAW5_TOPOLOGICAL_DIVERGENCE_NOT_DOCUMENTED", gate4["violations"])

        # Tight bipartite upper-bound equality (gm_edges == n_g * n_m and tm_edges == n_t * n_m) passes!
        apl5, sg5, cmp5 = _valid_fixture_triplet()
        n_g5 = sg5["counts"]["games"]
        n_m5 = sg5["counts"]["mechanics"]
        n_t5 = sg5["counts"]["techniques"]
        sg5["game_mechanic_bipartite"].update({"gm_edges": n_g5 * n_m5, "core_edges": n_g5 * n_m5, "supporting_edges": 0})
        sg5["technique_mechanic_bipartite"]["tm_edges"] = n_t5 * n_m5
        self.assertTrue(oracle.certify_pattern_sim_grammar_audit(apl5, sg5, cmp5)["certified"])

    def test_every_conservation_and_law5_refusal(self) -> None:
        # Non-dict arguments (all 3 conjuncts)
        apl0, sg0, cmp0 = _valid_fixture_triplet()
        with self.assertRaisesRegex(GrammarAuditError, "audit-dicts"):
            oracle.certify_pattern_sim_grammar_audit("bad", sg0, cmp0)  # type: ignore[arg-type]
        with self.assertRaisesRegex(GrammarAuditError, "audit-dicts"):
            oracle.certify_pattern_sim_grammar_audit(apl0, "bad", cmp0)  # type: ignore[arg-type]
        with self.assertRaisesRegex(GrammarAuditError, "audit-dicts"):
            oracle.certify_pattern_sim_grammar_audit(apl0, sg0, "bad")  # type: ignore[arg-type]

        def assert_mutated_refused(mutator, err_regex: str | None = None) -> None:
            a, s, c = _valid_fixture_triplet()
            mutator(a, s, c)
            if err_regex is None:
                with self.assertRaises(GrammarAuditError):
                    oracle.certify_pattern_sim_grammar_audit(a, s, c)
            else:
                with self.assertRaisesRegex(GrammarAuditError, err_regex):
                    oracle.certify_pattern_sim_grammar_audit(a, s, c)

        # APL tmat shape (all 3 conjuncts: list, len==3, row shape)
        assert_mutated_refused(lambda a, s, c: a.__setitem__("tier_matrix_full", tuple(a["tier_matrix_full"])), "apl.tmat-shape")
        assert_mutated_refused(lambda a, s, c: a.__setitem__("tier_matrix_full", [[1, 2, 3], [4, 5, 6]]), "apl.tmat-shape")
        assert_mutated_refused(lambda a, s, c: a.__setitem__("tier_matrix_full", [[1, 2], [3, 4], [5, 6]]), "apl.tmat-shape")

        def bad_tmat_neg(a, s, c):
            a["tier_matrix_full"][0][1] = -1
            a["tier_matrix_full"][0][2] += 200

        assert_mutated_refused(bad_tmat_neg, "apl.tmat-nonneg")

        # APL v >= 2 and 0 <= e <= v*(v-1) (both conjuncts isolated!)
        def bad_v_lt_2(a, s, c):
            a.update({
                "v_count": 1, "e_uniq": 0, "down_edges": 0, "up_edges": 0,
                "recip_directed_edges": 0, "recip_pairs": 0, "oneway_directed_edges": 0,
                "undir_edges": 0, "tier_matrix_full": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                "same_tier_edges": 0, "lower_e_count": 0, "lower_down": 0, "lower_up": 0,
                "scc_count_full": 1, "giant_scc_full": 1, "scc_count_lower": 1, "giant_scc_lower": 1,
                "undir_components": 1, "articulation_count": 0, "bridge_count": 0,
            })
            c["apl_giant_scc_lower_frac"] = "1/1"
            c["apl_biconnected_zero_cuts"] = True

        assert_mutated_refused(bad_v_lt_2, "apl-v-e-bounds")

        def bad_v_e_bounds(a, s, c):
            a["v_count"] = 2
            a["e_uniq"] = 3
            a["down_edges"] = 3
            a["up_edges"] = 0
            a["recip_directed_edges"] = 0
            a["recip_pairs"] = 0
            a["oneway_directed_edges"] = 3
            a["undir_edges"] = 3
            a["tier_matrix_full"] = [[3, 0, 0], [0, 0, 0], [0, 0, 0]]
            a["same_tier_edges"] = 3
            a["lower_e_count"] = 0
            a["lower_down"] = 0
            a["lower_up"] = 0
            a["scc_count_full"] = 1
            a["giant_scc_full"] = 2
            a["scc_count_lower"] = 2
            a["giant_scc_lower"] = 1
            a["undir_components"] = 1
            a["articulation_count"] = 0
            a["bridge_count"] = 0
            c["apl_giant_scc_lower_frac"] = "1/2"
            c["apl_biconnected_zero_cuts"] = True

        assert_mutated_refused(bad_v_e_bounds, "apl-v-e-bounds")

        # APL dn >= 0, up >= 0, dn + up == e (all 3 conjuncts!)
        assert_mutated_refused(lambda a, s, c: a.update({"down_edges": -1, "up_edges": a["e_uniq"] + 1}), "apl-down-up-sum")
        assert_mutated_refused(lambda a, s, c: a.update({"down_edges": a["e_uniq"] + 1, "up_edges": -1}), "apl-down-up-sum")
        assert_mutated_refused(lambda a, s, c: a.__setitem__("down_edges", a["down_edges"] + 1), "apl-down-up-sum")

        # APL rd >= 0, ow >= 0, rd % 2 == 0, rp == rd // 2, rd + ow == e (all 5 conjuncts!)
        assert_mutated_refused(
            lambda a, s, c: a.update({"recip_directed_edges": -2, "recip_pairs": -1, "oneway_directed_edges": a["e_uniq"] + 2, "undir_edges": a["e_uniq"] + 1}),
            "apl-recip-sum",
        )
        assert_mutated_refused(
            lambda a, s, c: a.update({"recip_directed_edges": a["e_uniq"] + 1, "recip_pairs": (a["e_uniq"] + 1) // 2, "oneway_directed_edges": -1, "undir_edges": (a["e_uniq"] + 1) // 2 - 1}),
            "apl-recip-sum",
        )
        assert_mutated_refused(
            lambda a, s, c: a.update({"recip_directed_edges": 1013, "recip_pairs": 506, "oneway_directed_edges": 1252, "undir_edges": 1758}),
            "apl-recip-sum",
        )
        assert_mutated_refused(
            lambda a, s, c: a.update({"recip_pairs": 508, "undir_edges": 1759}),
            "apl-recip-sum",
        )
        assert_mutated_refused(
            lambda a, s, c: a.update({"oneway_directed_edges": 1250, "undir_edges": 1757}),
            "apl-recip-sum",
        )
        assert_mutated_refused(lambda a, s, c: a.__setitem__("undir_edges", a["undir_edges"] + 1), "apl-undir-edge-identity")

        # APL tmat_sum == e and tmat_diag == st (both conjuncts!)
        assert_mutated_refused(lambda a, s, c: a["tier_matrix_full"][0].__setitem__(1, a["tier_matrix_full"][0][1] + 1), "apl-tier-matrix-conservation")
        assert_mutated_refused(lambda a, s, c: a.__setitem__("same_tier_edges", a["same_tier_edges"] + 1), "apl-tier-matrix-conservation")

        # APL ld >= 0, lu >= 0, ld + lu == le, le <= e (all 4 conjuncts!)
        assert_mutated_refused(lambda a, s, c: a.update({"lower_down": -1, "lower_up": a["lower_e_count"] + 1}), "apl-lower-sum")
        assert_mutated_refused(lambda a, s, c: a.update({"lower_down": a["lower_e_count"] + 1, "lower_up": -1}), "apl-lower-sum")
        assert_mutated_refused(lambda a, s, c: a.__setitem__("lower_down", a["lower_down"] + 1), "apl-lower-sum")
        assert_mutated_refused(lambda a, s, c: a.update({"lower_e_count": a["e_uniq"] + 1, "lower_down": a["e_uniq"] + 1, "lower_up": 0}), "apl-lower-sum")

        # APL scc full & lower (all 3 zero-redundancy conjuncts each + min-edge guards!)
        assert_mutated_refused(lambda a, s, c: a.update({"scc_count_full": -1, "giant_scc_full": -300}), "apl-scc-full-pigeonhole")
        assert_mutated_refused(lambda a, s, c: a.__setitem__("giant_scc_full", a["v_count"]), "apl-scc-full-pigeonhole")
        assert_mutated_refused(lambda a, s, c: a.update({"scc_count_full": 2, "giant_scc_full": 100}), "apl-scc-full-pigeonhole")
        assert_mutated_refused(lambda a, s, c: (a.update({"scc_count_lower": -1, "giant_scc_lower": -300}), c.__setitem__("apl_giant_scc_lower_frac", "-300/253")), "apl-scc-lower-pigeonhole")
        assert_mutated_refused(lambda a, s, c: a.__setitem__("scc_count_lower", a["v_count"]), "apl-scc-lower-pigeonhole")
        assert_mutated_refused(lambda a, s, c: (a.update({"scc_count_lower": 2, "giant_scc_lower": 100}), c.__setitem__("apl_giant_scc_lower_frac", "100/253")), "apl-scc-lower-pigeonhole")

        def bad_scc_full_edge_min(a, s, c):
            a.update({
                "v_count": 4, "e_uniq": 1, "down_edges": 1, "up_edges": 0,
                "recip_directed_edges": 0, "recip_pairs": 0, "oneway_directed_edges": 1,
                "undir_edges": 1, "tier_matrix_full": [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
                "same_tier_edges": 1, "lower_e_count": 0, "lower_down": 0, "lower_up": 0,
                "scc_count_full": 3, "giant_scc_full": 2, "scc_count_lower": 4, "giant_scc_lower": 1,
                "undir_components": 3, "articulation_count": 0, "bridge_count": 1,
                "biconnected_zero_cuts": False,
            })

        assert_mutated_refused(bad_scc_full_edge_min, "apl-scc-full-edge-min")

        def bad_scc_lower_edge_min(a, s, c):
            a.update({
                "v_count": 4, "e_uniq": 3, "down_edges": 2, "up_edges": 1,
                "recip_directed_edges": 0, "recip_pairs": 0, "oneway_directed_edges": 3,
                "undir_edges": 3, "tier_matrix_full": [[3, 0, 0], [0, 0, 0], [0, 0, 0]],
                "same_tier_edges": 3, "lower_e_count": 1, "lower_down": 1, "lower_up": 0,
                "scc_count_full": 2, "giant_scc_full": 3, "scc_count_lower": 3, "giant_scc_lower": 2,
                "undir_components": 1, "articulation_count": 0, "bridge_count": 0,
                "biconnected_zero_cuts": True,
            })

        assert_mutated_refused(bad_scc_lower_edge_min, "apl-scc-lower-edge-min")

        # APL u_c, arts, brdg (all 3 conjuncts!)
        assert_mutated_refused(lambda a, s, c: a.update({"undir_components": 0, "biconnected_zero_cuts": False}), "apl-cut-bounds")
        assert_mutated_refused(lambda a, s, c: a.update({"articulation_count": a["v_count"] - 1, "biconnected_zero_cuts": False}), "apl-cut-bounds")
        assert_mutated_refused(lambda a, s, c: a.update({"bridge_count": a["undir_edges"] + 1, "biconnected_zero_cuts": False}), "apl-cut-bounds")

        # PSG99-BYPASS-01: Empty 0-edge APL graph claimed connected/biconnected + biconnected edge-min!
        def bypass_01_empty_apl_connected(a, s, c):
            a.update({
                "v_count": 10, "e_uniq": 0, "down_edges": 0, "up_edges": 0,
                "recip_directed_edges": 0, "recip_pairs": 0, "oneway_directed_edges": 0,
                "undir_edges": 0, "tier_matrix_full": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
                "same_tier_edges": 0, "lower_e_count": 0, "lower_down": 0, "lower_up": 0,
                "scc_count_full": 10, "giant_scc_full": 1, "scc_count_lower": 10, "giant_scc_lower": 1,
                "undir_components": 1, "articulation_count": 0, "bridge_count": 0,
                "biconnected_zero_cuts": True,
            })
            c["apl_giant_scc_lower_frac"] = "1/10"
            c["apl_biconnected_zero_cuts"] = True

        assert_mutated_refused(bypass_01_empty_apl_connected, "apl-undir-edge-comp-bounds")

        def bad_apl_ue_above_complete(a, s, c):
            # v=2, e=2 (both directions 1->2, 2->1) => ue max is 1, but claim ow=2, rd=0 => ue=2 > v*(v-1)//2 = 1!
            a.update({
                "v_count": 2, "e_uniq": 2, "down_edges": 1, "up_edges": 1,
                "recip_directed_edges": 0, "recip_pairs": 0, "oneway_directed_edges": 2,
                "undir_edges": 2, "tier_matrix_full": [[2, 0, 0], [0, 0, 0], [0, 0, 0]],
                "same_tier_edges": 2, "lower_e_count": 0, "lower_down": 0, "lower_up": 0,
                "scc_count_full": 1, "giant_scc_full": 2, "scc_count_lower": 2, "giant_scc_lower": 1,
                "undir_components": 1, "articulation_count": 0, "bridge_count": 0,
                "biconnected_zero_cuts": True,
            })

        assert_mutated_refused(bad_apl_ue_above_complete, "apl-undir-edge-comp-bounds")

        def bad_apl_biconn_v2(a, s, c):
            # v=2, ue=1, u_c=1, arts=0, brdg=0 -> fails v >= 3 in apl-biconnected-edge-min!
            a.update({
                "v_count": 2, "e_uniq": 2, "down_edges": 1, "up_edges": 1,
                "recip_directed_edges": 2, "recip_pairs": 1, "oneway_directed_edges": 0,
                "undir_edges": 1, "tier_matrix_full": [[2, 0, 0], [0, 0, 0], [0, 0, 0]],
                "same_tier_edges": 2, "lower_e_count": 2, "lower_down": 1, "lower_up": 1,
                "scc_count_full": 1, "giant_scc_full": 2, "scc_count_lower": 1, "giant_scc_lower": 2,
                "undir_components": 1, "articulation_count": 0, "bridge_count": 0,
                "biconnected_zero_cuts": True,
            })

        assert_mutated_refused(bad_apl_biconn_v2, "apl-biconnected-edge-min")

        def bad_apl_biconn_tree(a, s, c):
            # v=4, ue=3, u_c=1, arts=0, brdg=0 -> fails ue >= v in apl-biconnected-edge-min!
            a.update({
                "v_count": 4, "e_uniq": 3, "down_edges": 3, "up_edges": 0,
                "recip_directed_edges": 0, "recip_pairs": 0, "oneway_directed_edges": 3,
                "undir_edges": 3, "tier_matrix_full": [[3, 0, 0], [0, 0, 0], [0, 0, 0]],
                "same_tier_edges": 3, "lower_e_count": 3, "lower_down": 3, "lower_up": 0,
                "scc_count_full": 4, "giant_scc_full": 1, "scc_count_lower": 4, "giant_scc_lower": 1,
                "undir_components": 1, "articulation_count": 0, "bridge_count": 0,
                "biconnected_zero_cuts": True,
            })

        assert_mutated_refused(bad_apl_biconn_tree, "apl-biconnected-edge-min")

        # APL biconnected_zero_cuts exact-bool & flag consistency
        assert_mutated_refused(lambda a, s, c: a.__setitem__("biconnected_zero_cuts", 1), "exact-bool:apl.biconnected_zero_cuts")
        assert_mutated_refused(lambda a, s, c: a.__setitem__("biconnected_zero_cuts", False), "apl-biconn-flag-match")

        def bad_apl_shuffles(a, s, c):
            a["nulls"]["n_shuffles"] = 99
            a["nulls"]["recip_p"] = "1/100"
            a["nulls"]["same_tier_p"] = "1/100"
            a["nulls"]["lower_down_p"] = "1/100"

        assert_mutated_refused(bad_apl_shuffles, "apl-shuffles-min")

        def bad_apl_ge(a, s, c):
            a["nulls"]["recip_ge_obs"] = 201
            a["nulls"]["recip_p"] = "202/201"

        assert_mutated_refused(bad_apl_ge, "apl-ge-range")
        assert_mutated_refused(lambda a, s, c: a["nulls"].__setitem__("recip_p", "2/201"), "apl-p-formula")

        # SimGrammar conservation refusals (every single conjunct in section 2!)
        assert_mutated_refused(lambda a, s, c: s["counts"].__setitem__("games", 1), "sg-entity-mins")
        assert_mutated_refused(lambda a, s, c: s["counts"].__setitem__("mechanics", 1), "sg-entity-mins")
        assert_mutated_refused(lambda a, s, c: s["counts"].__setitem__("techniques", 0), "sg-entity-mins")
        assert_mutated_refused(lambda a, s, c: s["counts"].update({"live_opportunities": -1, "deprecated_opportunities": 44}), "sg-opp-partition")
        assert_mutated_refused(lambda a, s, c: s["counts"].update({"live_opportunities": 44, "deprecated_opportunities": -1}), "sg-opp-partition")
        assert_mutated_refused(lambda a, s, c: s["counts"].__setitem__("live_opportunities", 41), "sg-opp-partition")

        assert_mutated_refused(lambda a, s, c: s["game_mechanic_bipartite"].update({"core_edges": -1, "supporting_edges": 2070}), "sg-gm-role-sum")
        assert_mutated_refused(lambda a, s, c: s["game_mechanic_bipartite"].update({"core_edges": 2070, "supporting_edges": -1}), "sg-gm-role-sum")
        assert_mutated_refused(lambda a, s, c: s["game_mechanic_bipartite"].__setitem__("core_edges", 1), "sg-gm-role-sum")
        assert_mutated_refused(
            lambda a, s, c: s["game_mechanic_bipartite"].update({"gm_edges": 0, "core_edges": 0, "supporting_edges": 0, "post2010_uses": 0, "post2010_from_pre2000_uses": 0}) or s["technique_mechanic_bipartite"].__setitem__("unlinked_uses", 0),
            "sg-gm-role-sum",
        )
        # Bipartite upper bound gm_edges <= n_g * n_m (179 * 199 = 35621; 35622 MUST be refused!)
        assert_mutated_refused(
            lambda a, s, c: s["game_mechanic_bipartite"].update({"gm_edges": 35622, "core_edges": 35622, "supporting_edges": 0}),
            "sg-gm-role-sum",
        )
        assert_mutated_refused(lambda a, s, c: s["game_mechanic_bipartite"].__setitem__("pre2000_vocab_count", 200), "sg-temporal-bounds")
        assert_mutated_refused(lambda a, s, c: s["game_mechanic_bipartite"].__setitem__("post2010_from_pre2000_uses", 1418), "sg-temporal-bounds")
        assert_mutated_refused(lambda a, s, c: s["game_mechanic_bipartite"].__setitem__("total_possible_pairs", 19700), "sg-cooc-bounds")
        assert_mutated_refused(lambda a, s, c: s["game_mechanic_bipartite"].__setitem__("cooc_pairs", 20000), "sg-cooc-bounds")

        assert_mutated_refused(lambda a, s, c: s["technique_mechanic_bipartite"].__setitem__("tm_edges", 0), "sg-tm-mech-partition")
        # Bipartite upper bound tm_edges <= n_t * n_m (46 * 199 = 9154; 9155 MUST be refused!)
        assert_mutated_refused(lambda a, s, c: s["technique_mechanic_bipartite"].__setitem__("tm_edges", 9155), "sg-tm-mech-partition")
        assert_mutated_refused(lambda a, s, c: s["technique_mechanic_bipartite"].update({"touched_mechs": 0, "unlinked_mechs": 199}), "sg-tm-mech-partition")
        assert_mutated_refused(lambda a, s, c: s["technique_mechanic_bipartite"].update({"touched_mechs": 200, "unlinked_mechs": -1}), "sg-tm-mech-partition")
        assert_mutated_refused(lambda a, s, c: s["technique_mechanic_bipartite"].__setitem__("unlinked_mechs", 96), "sg-tm-mech-partition")
        assert_mutated_refused(lambda a, s, c: s["technique_mechanic_bipartite"].__setitem__("unlinked_uses", 2070), "sg-unlinked-uses-bounds")

        def bad_unl_zero(a, s, c):
            s["technique_mechanic_bipartite"]["touched_mechs"] = s["counts"]["mechanics"]
            s["technique_mechanic_bipartite"]["unlinked_mechs"] = 0
            s["technique_mechanic_bipartite"]["unlinked_uses"] = 1

        assert_mutated_refused(bad_unl_zero, "sg-unlinked-zero-pigeonhole")
        assert_mutated_refused(lambda a, s, c: s["technique_mechanic_bipartite"].__setitem__("global_family_renyi2", "0/1"), "sg-global-r2-range")
        assert_mutated_refused(lambda a, s, c: s["technique_mechanic_bipartite"].__setitem__("within_tech_family_renyi2", "0/1"), "sg-wt-r2-range")

        assert_mutated_refused(
            lambda a, s, c: s["mechanic_relation_graph"]["typed_edge_counts"].update({"tension": -1, "synergy": 114}),
            "sg-typed-rel-sum",
        )
        assert_mutated_refused(lambda a, s, c: s["mechanic_relation_graph"]["typed_edge_counts"].__setitem__("tension", 12), "sg-typed-rel-sum")
        assert_mutated_refused(lambda a, s, c: s["mechanic_relation_graph"].__setitem__("undir_mech_edges", 134), "sg-mech-edge-bounds")
        assert_mutated_refused(lambda a, s, c: s["mechanic_relation_graph"].__setitem__("isolated_mechs", -1), "sg-mech-edge-bounds")
        assert_mutated_refused(
            lambda a, s, c: s["mechanic_relation_graph"].update({"isolated_mechs": 0, "undir_components": 0}),
            "sg-mech-comp-bounds",
        )
        assert_mutated_refused(
            lambda a, s, c: s["mechanic_relation_graph"].update({"isolated_mechs": 199, "undir_components": 198}),
            "sg-mech-comp-bounds",
        )
        assert_mutated_refused(lambda a, s, c: s["mechanic_relation_graph"].__setitem__("articulation_count", 198), "sg-mech-comp-bounds")
        assert_mutated_refused(lambda a, s, c: s["mechanic_relation_graph"].__setitem__("bridge_count", 130), "sg-mech-comp-bounds")

        # PSG99-BYPASS-02: 0-edge SimGrammar graph claimed 1 component & 0 isolated + all 3 conjuncts isolated!
        def bypass_02_empty_sg_connected(a, s, c):
            s["mechanic_relation_graph"].update({
                "typed_edge_counts": {"requires": 0, "specializes": 0, "synergy": 0, "tension": 0},
                "typed_edge_total": 0, "undir_mech_edges": 0, "isolated_mechs": 0,
                "undir_components": 1, "articulation_count": 0, "bridge_count": 0,
            })

        assert_mutated_refused(bypass_02_empty_sg_connected, "sg-mech-edge-comp-bounds")
        # Conjunct 1 (mr_ue >= n_m - mc): 129 < 199 - 60 = 139 while 2*129 >= 144 and 129 <= C(144,2)
        assert_mutated_refused(lambda a, s, c: s["mechanic_relation_graph"].__setitem__("undir_components", 60), "sg-mech-edge-comp-bounds")
        # Conjunct 2 (mr_ue <= non_iso*(non_iso-1)//2): iso=197 (non_iso=2), mr_ue=2 > C(2,2)=1 while mr_ue >= 199-198=1 and 2*2 >= 2
        assert_mutated_refused(
            lambda a, s, c: s["mechanic_relation_graph"].update({
                "typed_edge_counts": {"requires": 0, "specializes": 0, "synergy": 2, "tension": 0},
                "typed_edge_total": 2, "undir_mech_edges": 2, "isolated_mechs": 197,
                "undir_components": 198, "articulation_count": 0, "bridge_count": 0,
            }),
            "sg-mech-edge-comp-bounds",
        )
        # Conjunct 3 (2 * mr_ue >= non_iso): iso=195 (non_iso=4), mr_ue=1 => 2 < 4 while mr_ue >= 199-198=1 and 1 <= C(4,2)=6
        assert_mutated_refused(
            lambda a, s, c: s["mechanic_relation_graph"].update({
                "typed_edge_counts": {"requires": 0, "specializes": 0, "synergy": 1, "tension": 0},
                "typed_edge_total": 1, "undir_mech_edges": 1, "isolated_mechs": 195,
                "undir_components": 198, "articulation_count": 0, "bridge_count": 1,
            }),
            "sg-mech-edge-comp-bounds",
        )
        # Isolated sg-mech-noniso-comp-pigeonhole: iso=196 (non_iso=3), mc=196, mr_ue=3 satisfies all 3 prior bounds!
        assert_mutated_refused(
            lambda a, s, c: s["mechanic_relation_graph"].update({
                "typed_edge_counts": {"requires": 0, "specializes": 0, "synergy": 3, "tension": 0},
                "typed_edge_total": 3, "undir_mech_edges": 3, "isolated_mechs": 196,
                "undir_components": 196, "articulation_count": 0, "bridge_count": 0,
            }),
            "sg-mech-noniso-comp-pigeonhole",
        )
        # dep_strict_dag exact-bool & dep_nontrivial_sccs consistency (empty tuple kills isinstance(..., list) alone!)
        assert_mutated_refused(lambda a, s, c: s["mechanic_relation_graph"].__setitem__("dep_strict_dag", 1), "exact-bool:sg.dep_strict_dag")
        assert_mutated_refused(lambda a, s, c: s["mechanic_relation_graph"].__setitem__("dep_nontrivial_sccs", ()), "sg-dep-dag-scc-match")
        assert_mutated_refused(lambda a, s, c: s["mechanic_relation_graph"].__setitem__("dep_nontrivial_sccs", [["a", "b"]]), "sg-dep-dag-scc-match")

        assert_mutated_refused(lambda a, s, c: s["spearman_rubric_correlations"].__setitem__("emergence_vs_legibility_sign", 2), "sg-spearman-signs")
        assert_mutated_refused(lambda a, s, c: s["spearman_rubric_correlations"].__setitem__("emergence_vs_tuning_sign", 2), "sg-spearman-signs")
        assert_mutated_refused(lambda a, s, c: s["spearman_rubric_correlations"].__setitem__("emergence_vs_legibility_rho_sq", "2/1"), "sg-spearman-bounds")
        assert_mutated_refused(lambda a, s, c: s["spearman_rubric_correlations"].__setitem__("emergence_vs_tuning_rho_sq", "2/1"), "sg-spearman-bounds")

        # PSG99-BYPASS-03: Spearman sign/magnitude contradiction (both pairs, both directions!)
        assert_mutated_refused(lambda a, s, c: s["spearman_rubric_correlations"].__setitem__("emergence_vs_legibility_sign", 0), "sg-spearman-sign-zero-match")
        assert_mutated_refused(lambda a, s, c: s["spearman_rubric_correlations"].__setitem__("emergence_vs_legibility_rho_sq", "0/1"), "sg-spearman-sign-zero-match")
        assert_mutated_refused(lambda a, s, c: s["spearman_rubric_correlations"].__setitem__("emergence_vs_tuning_sign", 0), "sg-spearman-sign-zero-match")
        assert_mutated_refused(lambda a, s, c: s["spearman_rubric_correlations"].__setitem__("emergence_vs_tuning_rho_sq", "0/1"), "sg-spearman-sign-zero-match")

        def bad_sg_shuffles(a, s, c):
            # Syncs all 5 p-values to denominator 100 so ONLY sg-shuffles-min fails!
            s["nulls"]["n_shuffles"] = 99
            s["nulls"]["cooc_p"] = "1/100"
            s["nulls"]["global_family_r2_p"] = "3/10"
            s["nulls"]["within_tech_r2_p"] = "1/100"
            s["nulls"]["spearman_em_lg_p"] = "1/100"
            s["nulls"]["spearman_em_tn_p"] = "1/100"

        assert_mutated_refused(bad_sg_shuffles, "sg-shuffles-min")

        def bad_sg_ge(a, s, c):
            # Syncs p-value to 202/201 so ONLY sg-ge-range fails!
            s["nulls"]["cooc_le_obs"] = 201
            s["nulls"]["cooc_p"] = "202/201"

        assert_mutated_refused(bad_sg_ge, "sg-ge-range")
        assert_mutated_refused(lambda a, s, c: s["nulls"].__setitem__("cooc_p", "2/201"), "sg-p-formula")

        # Honest status & Law-5 comparison consistency + PSG99-BYPASS-04 strict bool refusals (section 3)
        assert_mutated_refused(lambda a, s, c: s["nulls"].__setitem__("global_family_r2_status", "SIGNIFICANT_AT_ALPHA_005"), "sg-honest-r2-status")
        assert_mutated_refused(lambda a, s, c: c.__setitem__("sg_global_tech_family_r2_status", "SIGNIFICANT_AT_ALPHA_005"), "comp-honest-r2-status")
        assert_mutated_refused(lambda a, s, c: c.__setitem__("apl_giant_scc_lower_frac", "1/1"), "comp-apl-scc-match")
        assert_mutated_refused(lambda a, s, c: c.__setitem__("apl_biconnected_zero_cuts", 1), "exact-bool:comp.apl_biconnected_zero_cuts")
        assert_mutated_refused(lambda a, s, c: c.__setitem__("apl_biconnected_zero_cuts", False), "comp-apl-biconn-match")
        assert_mutated_refused(lambda a, s, c: c.__setitem__("sg_dep_strict_dag", 1), "exact-bool:comp.sg_dep_strict_dag")
        assert_mutated_refused(lambda a, s, c: c.__setitem__("sg_dep_strict_dag", False), "comp-sg-dag-match")
        assert_mutated_refused(lambda a, s, c: c.__setitem__("sg_mech_articulation_frac", "0/1"), "comp-sg-art-frac-match")
        assert_mutated_refused(lambda a, s, c: c.__setitem__("sg_mech_bridge_frac", "0/1"), "comp-sg-bridge-frac-match")
        assert_mutated_refused(lambda a, s, c: c.__setitem__("topological_divergence_documented", "false"), "exact-bool:comp.topological_divergence_documented")
        assert_mutated_refused(lambda a, s, c: c.__setitem__("topological_divergence_documented", False), "comp-divergence-flag-match")


class TestAuditProvenanceAndCliR5(unittest.TestCase):
    """Kill EVERY single provenance, symlink, git-HEAD, envelope, and CLI mutant in audit."""

    def test_git_head_and_containment_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            outside = base / "outside"
            outside.mkdir()
            root = base / "root"
            root.mkdir()
            inside_real = root / "inside_real"
            inside_real.mkdir()

            # Direct child symlink pointing INSIDE root: only M001 catches it!
            link = root / "child_link"
            link.symlink_to(inside_real)
            with self.assertRaisesRegex(GrammarAuditError, "symlink-refused"):
                audit._require_contained_path(root, link, "link")

            # Parent symlink escape where leaf itself is not a symlink (M002)
            (outside / "inner").mkdir()
            parent_link = root / "via"
            parent_link.symlink_to(outside)
            with self.assertRaisesRegex(GrammarAuditError, "escape-refused"):
                audit._require_contained_path(root, parent_link / "inner", "escape")

            # read_git_head_commit:
            # 1a) missing .git dir -> kills git_dir.is_dir()
            repo_nogit = base / "repo_nogit"
            repo_nogit.mkdir()
            with self.assertRaisesRegex(GrammarAuditError, "git-dir-missing"):
                audit.read_git_head_commit(repo_nogit)

            # 1b) symlinked .git pointing to valid git dir -> kills not git_dir.is_symlink()
            real_git = base / "real_git"
            real_git.mkdir()
            (real_git / "HEAD").write_text("e" * 40 + "\n", encoding="utf-8")
            repo_symgit = base / "repo_symgit"
            repo_symgit.mkdir()
            (repo_symgit / ".git").symlink_to(real_git)
            with self.assertRaisesRegex(GrammarAuditError, "git-dir-missing"):
                audit.read_git_head_commit(repo_symgit)

            # 2a) missing HEAD -> kills head_file.is_file()
            repo = base / "repo"
            (repo / ".git").mkdir(parents=True)
            with self.assertRaisesRegex(GrammarAuditError, "git-head-missing"):
                audit.read_git_head_commit(repo)

            # 2b) symlinked HEAD pointing to valid commit file -> kills not head_file.is_symlink()
            (repo / ".git" / "HEAD").symlink_to(real_git / "HEAD")
            with self.assertRaisesRegex(GrammarAuditError, "git-head-missing"):
                audit.read_git_head_commit(repo)
            (repo / ".git" / "HEAD").unlink()

            # 3a) non-refs/ relative ref pointing to a REAL valid file -> kills ref_rel.startswith("refs/")
            (repo / ".git" / "heads").mkdir()
            (repo / ".git" / "heads" / "ok").write_text("f" * 40 + "\n", encoding="utf-8")
            (repo / ".git" / "HEAD").write_text("ref: heads/ok\n", encoding="utf-8")
            with self.assertRaisesRegex(GrammarAuditError, "git-ref-invalid"):
                audit.read_git_head_commit(repo)

            # 3b) refs/.. traversal ref pointing to a REAL valid file -> kills ".." not in ref_rel
            (repo / ".git" / "refs").mkdir()
            (repo / ".git" / "ok_ref").write_text("f" * 40 + "\n", encoding="utf-8")
            (repo / ".git" / "HEAD").write_text("ref: refs/../ok_ref\n", encoding="utf-8")
            with self.assertRaisesRegex(GrammarAuditError, "git-ref-invalid"):
                audit.read_git_head_commit(repo)

            # 4a) unresolved packed-refs (missing file) -> kills packed.is_file()
            (repo / ".git" / "HEAD").write_text("ref: refs/heads/missing\n", encoding="utf-8")
            with self.assertRaisesRegex(GrammarAuditError, "git-ref-unresolved"):
                audit.read_git_head_commit(repo)

            # 4b) symlinked packed-refs pointing to real valid file -> kills not packed.is_symlink()
            real_packed = base / "real_packed"
            real_packed.write_text("a" * 40 + " refs/heads/missing\n", encoding="utf-8")
            (repo / ".git" / "packed-refs").symlink_to(real_packed)
            with self.assertRaisesRegex(GrammarAuditError, "git-ref-unresolved"):
                audit.read_git_head_commit(repo)
            (repo / ".git" / "packed-refs").unlink()

            # 5) malformed commit (M007)
            (repo / ".git" / "HEAD").write_text("not-a-sha1\n", encoding="utf-8")
            with self.assertRaisesRegex(GrammarAuditError, "git-commit-malformed"):
                audit.read_git_head_commit(repo)

            # 6) detached HEAD success
            detached = "d" * 40
            (repo / ".git" / "HEAD").write_text(detached + "\n", encoding="utf-8")
            self.assertEqual(audit.read_git_head_commit(repo), detached)

    def test_verify_intake_provenance_all_pin_and_structure_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            # Nonexistent intake_root -> kills intake_root.is_dir()
            with self.assertRaisesRegex(GrammarAuditError, "intake-root-missing"):
                audit.verify_intake_provenance(base / "does_not_exist")

            root = base / "intake"
            pins = _write_mini_intake(root)
            prov = audit.verify_intake_provenance(root, expected_pins=pins)
            self.assertTrue(prov["pinned_inputs_verified"])

            # Symlinked intake_root pointing to valid intake -> kills not intake_root.is_symlink()
            sym_root = base / "intake_link"
            sym_root.symlink_to(root)
            with self.assertRaisesRegex(GrammarAuditError, "intake-root-missing"):
                audit.verify_intake_provenance(sym_root, expected_pins=pins)

            # Pin mismatch tests (M012-M021)
            for key, bad_val in (
                ("apl_md_commit", "0" * 40),
                ("simgrammar_commit", "0" * 40),
                ("simgrammar_paper_bytes", 1),
                ("simgrammar_paper_sha256", "0" * 64),
                ("simgrammar_paper_dataset_sha256", "0" * 64),
            ):
                bad_pins = dict(pins)
                bad_pins[key] = bad_val
                with self.assertRaises(GrammarAuditError):
                    audit.verify_intake_provenance(root, expected_pins=bad_pins)

            # Missing dataset_sha256 in paper (M011)
            paper_p = root / "sources" / "simgrammar_paper.md"
            orig_paper = paper_p.read_bytes()
            paper_p.write_text("# No dataset hash\n", encoding="utf-8")
            with self.assertRaisesRegex(GrammarAuditError, "paper-dataset-sha256-missing"):
                audit.verify_intake_provenance(root, expected_pins=pins)
            paper_p.write_bytes(orig_paper)

            # Missing Patterns/ dir & missing sg data/ dir (both conjuncts of M010!)
            pat_dir = root / "repos" / "apl-md" / "Patterns"
            pat_bak = root / "repos" / "apl-md" / "Patterns_bak"
            pat_dir.rename(pat_bak)
            with self.assertRaisesRegex(GrammarAuditError, "intake-data-dirs-missing"):
                audit.verify_intake_provenance(root, expected_pins=pins)
            pat_bak.rename(pat_dir)

            sg_data = root / "repos" / "simgrammar" / "data"
            sg_data_bak = root / "repos" / "simgrammar" / "data_bak"
            sg_data.rename(sg_data_bak)
            with self.assertRaisesRegex(GrammarAuditError, "intake-data-dirs-missing"):
                audit.verify_intake_provenance(root, expected_pins=pins)
            sg_data_bak.rename(sg_data)

            # Missing apl-md, missing simgrammar, missing paper (all 3 conjuncts of M009!)
            apl_dir = root / "repos" / "apl-md"
            apl_bak = root / "repos" / "apl-md-bak"
            apl_dir.rename(apl_bak)
            with self.assertRaisesRegex(GrammarAuditError, "intake-entries-missing"):
                audit.verify_intake_provenance(root, expected_pins=pins)
            apl_bak.rename(apl_dir)

            sg_dir = root / "repos" / "simgrammar"
            sg_bak = root / "repos" / "simgrammar-bak"
            sg_dir.rename(sg_bak)
            with self.assertRaisesRegex(GrammarAuditError, "intake-entries-missing"):
                audit.verify_intake_provenance(root, expected_pins=pins)
            sg_bak.rename(sg_dir)

            paper_p.unlink()
            with self.assertRaisesRegex(GrammarAuditError, "intake-entries-missing"):
                audit.verify_intake_provenance(root, expected_pins=pins)

    def test_assemble_certificate_standalone_and_cli_refusals(self) -> None:
        apl, sg, cmp_d = _valid_fixture_triplet()
        gate = oracle.certify_pattern_sim_grammar_audit(apl, sg, cmp_d)
        prov = {"pinned_inputs_verified": False}

        # Invalid execution_mode (M022)
        with self.assertRaises(GrammarAuditError):
            audit.assemble_certificate(apl, sg, cmp_d, gate, prov, "bad_mode", False)

        # Non-bool live_corpus_recounted (M023)
        with self.assertRaises(GrammarAuditError):
            audit.assemble_certificate(apl, sg, cmp_d, gate, prov, "standalone_fixture_replay", 0)  # type: ignore[arg-type]

        # Mismatched live flag vs execution mode (M024, M025)
        with self.assertRaises(GrammarAuditError):
            audit.assemble_certificate(apl, sg, cmp_d, gate, prov, "standalone_fixture_replay", True)
        with self.assertRaises(GrammarAuditError):
            audit.assemble_certificate(apl, sg, cmp_d, gate, prov, "live_corpus_recount", False)

        # Uncertified or non-bool certified gate refused (kills both conjuncts of M026!)
        bad_gate = dict(gate, certified=False)
        with self.assertRaisesRegex(GrammarAuditError, "audit-gate-not-certified"):
            audit.assemble_certificate(apl, sg, cmp_d, bad_gate, prov, "standalone_fixture_replay", False)
        bad_gate_str = dict(gate, certified="false")
        with self.assertRaisesRegex(GrammarAuditError, "audit-gate-not-certified"):
            audit.assemble_certificate(apl, sg, cmp_d, bad_gate_str, prov, "standalone_fixture_replay", False)
        bad_gate_int = dict(gate, certified=1)
        with self.assertRaisesRegex(GrammarAuditError, "audit-gate-not-certified"):
            audit.assemble_certificate(apl, sg, cmp_d, bad_gate_int, prov, "standalone_fixture_replay", False)

        # Standalone replay & CLI output + --standalone param lock refusal (M027)
        std_cert = audit.run_standalone_replay()
        self.assertEqual(std_cert["execution_mode"], "standalone_fixture_replay")
        self.assertFalse(std_cert["live_corpus_recounted"])
        self.assertTrue(std_cert["paper_reconciliation"]["all_headline_counts_matched"])

        buf_json = io.StringIO()
        with redirect_stdout(buf_json):
            rc = audit.main(["--standalone", "--json"])
        self.assertEqual(rc, 0)
        parsed = json.loads(buf_json.getvalue())
        self.assertEqual(parsed["certificate_sha256"], std_cert["certificate_sha256"])

        buf_human = io.StringIO()
        with redirect_stdout(buf_human):
            rc2 = audit.main(["--standalone"])
        self.assertEqual(rc2, 0)
        self.assertIn("standalone_fixture_replay", buf_human.getvalue())

        with tempfile.TemporaryDirectory() as td:
            out_p = Path(td) / "cert.json"
            buf_w = io.StringIO()
            with redirect_stdout(buf_w):
                rc3 = audit.main(["--standalone", "--write-cert", str(out_p)])
            self.assertEqual(rc3, 0)
            self.assertEqual(json.loads(out_p.read_text(encoding="utf-8")), std_cert)

        # Standalone rejects custom --shuffles or --seed (M027)
        with self.assertRaises(GrammarAuditError):
            audit.main(["--standalone", "--shuffles", "150"])
        with self.assertRaises(GrammarAuditError):
            audit.main(["--standalone", "--seed", "1"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
