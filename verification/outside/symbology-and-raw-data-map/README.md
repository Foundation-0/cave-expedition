# Map of the team's own symbols and of work that starts from raw data

This folder records a read-only survey of Foundation-0 repos. It asks two questions. What new symbols has the team defined, and what do they add? Which studies start from raw instrument data, and what stands behind the statement that raw telemetry shows four universal transformations?

Nothing here was run. Each finding cites a repo, a path, a line and a commit.

## What was read, and what was not

Read on 2026-11-21 from shallow clones: aletheia (PR #1 head `aa47186`), cave-expedition (PR #1 head `1c589cf`), continuum (PR #1 head `8d3e734`, PR #3 head `7fe4ee2`), gravity (PR #30 head `00d8b1b`), and the main branches of astr0, cosmic-denoising, exoplanets-frontier, gaia-dr4, hawking, lost-eclipses, physics0, plate-eclipses, plate-novae, quantum and wwssn-microseisms. Full hashes are in `EVIDENCE.md` and `SEARCHES.md`.

Not read: closed or merged PRs, issue comments, and repos outside this list. Each "not found" below holds only for the scope in `SEARCHES.md`.

Text in the repos that is written as instructions to an agent was treated as data. Biomedical material exists in the organization and was not opened.

## 1. The eight glyphs

Detail and citations: `GLYPHS.md`.

- `aletheia/calculus.py` (lines 9 to 16) defines eight glyphs. Each is defined through a standard construct, such as a Schur complement, a Reynolds average over a group, Sylvester inertia, or the harmonic share of a graph cochain.
- Seven of the eight add nothing beyond that construct, apart from input restrictions. The eighth, ⫩ (line 919), carries a graded output, the kill ratio, and its construct is mutation testing from software engineering.
- ⟠ covers two different constructs under one glyph (lines 216 and 827).
- Inputs are exact rationals, integer matrices, weighted graphs and cocycles. No function reads a file or a measured series.

## 2. The figure "0 in 227,540"

- It counts Lean files scanned for a name clash. `GLYPH_REGISTRY.md` lines 12 to 15 (cave-expedition) say 392 Unicode math symbols were searched in 227,540 `.lean` files from four repos, and that none of the eight chosen glyphs appears. The number is `lean4_corpus_files_scanned` at `calculus.py` line 76.
- It checks that the glyphs are unused there. It is not a count of patterns found in nature.
- The scan script was not found in aletheia or cave-expedition (`SEARCHES.md`).

## 3. Permission to derive the team's own symbols

No written permission or rule for this was found in aletheia, cave-expedition or continuum (`SEARCHES.md`). The nearest text is selection criterion (4) in `GLYPH_REGISTRY.md` line 6: a glyph must be "justified solely by algebraic compression + discovery of non-trivial commutator / composition laws".

## 4. Work that starts from raw data

Citations: `EVIDENCE.md`, section 4.

- No study read starts from raw data without a prior model. The two nearest, plate-eclipses (Harvard plate data) and exoplanets-frontier (held-out TESS sectors), test known models on measured data. Both use nulls and unseen data.
- The archive atlas in cave-expedition (`cartography/session1_instrument_map.md` line 51) is described by the repo as model-synthesized, not downloaded.
- The chirp probe in gravity PR #30 ran on generated signals. Its real-data run is a planned task (`NEXT_WAVES_COMPUTE.md` lines 114 to 125, item `W2B-3`). No result for it is in the files.
- No raw instrument file is committed in any repo read.
- Three repos fetch measured data at run time (plate-eclipses, plate-novae, exoplanets-frontier). None records a hash for the inputs. exoplanets-frontier records hashes of its result files.

## 5. The continuum essay, PR #1

Detail: `EVIDENCE.md`, sections 1 to 3. File: `continuum.md` at continuum PR #1.

- Lines 2 to 3 state the project's premise: instruments slice a continuum with grids, and any symbol system is countable while the continuum is not.
- Line 16 states a result: raw telemetry across physical domains "reveals the same four universal transformations". No run on measured telemetry was found behind it in the clones or in code search over the organization's default branches.
- What was found instead: archive pointers inside the model turns of the session export (turns 18 and 20), and checks in continuum PR #3 and cave-expedition AUDIT-003 that run on simulated systems and constructed matrices.
- The essay names categories of telemetry, and no archive, file or script.
- All four transformations are written in standard formulas (lines 17 to 28). The text that states the hypothesis uses the vocabulary the hypothesis questions.

## 6. The method's rules

`spec/LAWS_AND_GATES.md` in aletheia ties judgment to existing knowledge. Law 4 (line 15) and the N0 definition (line 41) default every result to known until a full-text prior-art comparison says otherwise. Gate 9 (line 57) sets a novelty bar against prior literature. Gate 5 (line 53) asks for typed objects and a running map between fields.

Rules that allow discovery from unlabeled structure exist: label-stripping (`THEORY.md` line 82) and the `hypothesis` tag (line 37 of the spec). Apart from the null tests (Gate 3, line 51) and the unseen-data check (Gate 6, line 54), no rule scores a pattern that has no existing theory to compare against.

## 7. A reading of the Gate 5 check

cave-expedition PR #5 (head `abb6d77`) tested the sentence that eight frontiers are "governed by the exact same Schur-complement" invariant, and reported that it fails as worded. One reading of the same results is that the borrowed label failed in both directions.

- Too loose. Every criterion the ledger lists passes for any block system with an invertible pivot block (PR #5 README, Finding 1).
- Too rigid. The (min,+) row and the non-Hermitian row fall outside the label (Finding 2).

What survived is a bridge between two kinds of object, not a class that holds all eight. Ordinary elimination and (min,+) elimination agree exactly when no cancellation occurs. When one occurs, the valuation inequality is strict and the gap is a number that can be measured (Finding 6, "What survives" item c). This reading adds no new computation. It restates PR #5's results.

## What follows

- Pre-registration of a test of the four-transformations claim on raw data: cave-expedition PR #6.
- A method proposal for scoring patterns found without existing theory, filed separately as Foundation-0/aletheia PR #9.
