# Map of the team's own symbols and of work that starts from raw data

This folder records a read-only survey of Foundation-0 repos. It asks two questions. What new symbols has the team defined, and what do they add? Which studies start from raw instrument data, and what stands behind the statement that raw telemetry shows four universal transformations?

Nothing here was run. Each finding cites a repo, a path, a line and a commit.

## What was read, and what was not

Read on 2026-11-21 from shallow clones of 15 repos: aletheia (PR #1 head `aa47186`), cave-expedition (PR #1 head `1c589cf`), continuum (PR #1 head `8d3e734`, PR #3 head `7fe4ee2`), gravity (PR #30 head `00d8b1b`), and the main branches of astr0, cosmic-denoising, exoplanets-frontier, gaia-dr4, hawking, lost-eclipses, physics0, plate-eclipses, plate-novae, quantum and wwssn-microseisms. Full hashes are in `EVIDENCE.md` and `SEARCHES.md`.

This list covers the first 15 repos. A second pass over the rest of the organization is in section 8. Not read in either pass: closed or merged PRs, issue comments, and private repos. Each "not found" below holds only for the scope in `SEARCHES.md`.

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

## 8. Org-wide sweep

The organization has 51 repos. 15 were read in sections 1 to 7. 30 more were swept on 2026-11-21: 25 non-biomedical repos, and 5 repos of a biomedical kind that were checked only for the presence of fetch code and not read further. 6 repos are not public and were not opened.

Method: shallow clones of the default branches. Each clone was searched for data-file extensions, CSV files over 1 MB, fetch code, archive names, and the words "raw", "sensor", "archive" and "measured" in READMEs. Open PR titles were listed. Five open PR heads were fetched where a title suggested measured or live data. Nothing was run. Commands are in `SEARCHES.md`.

Result: across the 30 swept repos, no committed file has the extension fit, fits, h5, hdf5, mseed, sac, cdf, nc, edf, wav, parquet or gwf, and no CSV is over 1 MB. The only `.npy` and `.npz` files (7, all in `incentre-lattices`) are optimizer outputs. The only measured data is in `incentre-lattices`.

Classes: (a) starts from data with no model. (b) tests a known model on measured data. (c) synthetic data only. (d) names archives only.

| Repo, path (line) | What | Class | Evidence |
|---|---|---|---|
| incentre-lattices `2d374ff`, `research/chemistry/fetch_borides.py` line 1, `research/chemistry/cod/` (45 CIF files, 508 KB), `research/chemistry/cod_index.json` | Crystal structures fetched from the Crystallography Open Database. Terms are in `NOTICE` lines 13 and 14. No hash on the files was found | (b) | `borides_real.py` line 1: compares real MB6 and MB12 structures "with the 'dot' ideal", the project's own geometric model |
| incentre-lattices, `research/chemistry/data/TableS1.csv` (36,379 bytes) | Published table of 576 perovskite entries. `NOTICE` lines 24 to 28 give the source, an MIT licence, and a byte-identical check | (b) | `perovskite_mu.py` lines 1 to 2: tests whether a radius-ratio limit separates perovskites from non-perovskites in that table |
| incentre-lattices, `autoresearch-fold/` and `results/fold-*/` (7 `.npy` and `.npz` files) | Optimizer outputs | (c) | No measured source named |
| fractals main `48b923b`, `README.md` lines 5 and 138 to 139 | Numbers quoted from papers. No data files | (b) | Line 138: "the simulated Eridanus II-like halo" of a published paper |
| fractals PR #26 `ff05f9b`, `cosmic-homogeneity/README.md` lines 6 to 8 and 146 to 147 | Galaxy-survey homogeneity scale, compared with published WiggleZ values typed into a table. No survey data fetched | (b) | The study computes the scale from the standard cosmological model and "checks it against the surveys" |
| fractals PR #37 `cf660ee`, `orbits/README.md` line 154 | Orbit and rotation-curve numbers quoted from papers | (b) | Compares a computed precession with the paper's quoted 12.1 arcmin and its measured ratio 1.10 +/- 0.19 |
| fractals PR #56 `5bd60bb`, `scripts/pont_witness.py` lines 55 and 63 | Names TIC stars from exoplanets-frontier, but generates its own series | (c) | `synth_fgn(n, hurst, seed=7)` and `synth_mdwarf_lightcurve(...)`. No download call found |
| fractals PR #60 `f6cb822`, `studies/expedition-mult-farkas-dsi/verify_mult_farkas_dsi.py` lines 335 to 336 | "Live" Sabra and percolation runs are the repo's own simulators | (c) | Docstring: "Reproduce live Sabra K41 ... (seed=1 & seed=7)" |
| f0, `deep-fields/scouting/astronomy.md`, `physics-earth-humanities.md`, `2026-10-19.md` | Scouting reports naming NASA, ESA, DASCH, TESS and Gaia | (d) | Report text. Its one run became plate-eclipses |
| rigid-realizations, relative-equilibria, certified-orbits, gfq-codes, covering-min-modulus, rism-anon: `notes/reports/fact-check.md` and one subject report each | Copies of the scouting reports | (d) | Report text |
| thermal-capture, ductricity (6 files each, no code) | Question records | (d) | thermal-capture README line 5 says it tests each route "against measured numbers". No numbers or code in the repo |
| math0 `data/codetables/census.py`, gfq-codes `scripts/delsarte_sweep.py` | Fetch coding-theory bounds tables from codetables.de | not observational | `census.py` docstring: fetch the colour table and read each entry as lower and upper bounds |
| math0 PR #20 `14f5a28`, `studies/workers-dns-tcp-channel-capacity/` | The Domain Name System over TCP, a software study | not observational | Directory name and report |
| rism-anon, overdue-data | Music-manuscript catalogue and dataset-deposit metadata | not observational | READMEs |
| proven-commons, `.github`, st0a, f0 `scripts/fetch.py` | Fetch code for toolchains, labels or PR feeds | not observational | File names and docstrings |
| f0 `scripts/exoplanets_data.py` | Rebuilds a candidate table from another project's published tables | not observational | Docstring lines 1 to 12 |

Conclusion: no study in any repo read starts from measured data without a prior model. Every study that touches measured data compares it with a stated model or a published number (class b). The rest use synthetic data or name archives only.

Scope of the conclusion: the 45 repos opened (15 + 30), their default branches, the five PR heads above, and the two PR heads read earlier (aletheia PR #1, cave-expedition PR #1) and continuum PRs #1 and #3 and gravity PR #30.

Not reached: the 6 repos that are not public. The contents of the 5 biomedical-kind repos beyond fetch-code presence. Closed and merged PRs. Open PR heads other than the ones named (the other open PR titles look like mathematics or process work and were not fetched). Issues and discussions.

## What follows

- Pre-registration of a test of the four-transformations claim on raw data: cave-expedition PR #6.
- A method proposal for scoring patterns found without existing theory, filed separately as Foundation-0/aletheia PR #9.
