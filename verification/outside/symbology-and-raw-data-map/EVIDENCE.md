# Evidence for line 16 of the continuum essay, and the data inventory

Read on 2026-11-21. Heads: Foundation-0/continuum PR #1 `8d3e7345f593378fd0ba6a020509d52afc9f362e`, continuum PR #3 `7fe4ee2202dad0e5c5420756a037c212fd3e52ee`, cave-expedition PR #1 `1c589cfa5980c10af0073f85b6048d7280c10689`. Files were read, not run.

## 1. The sentence

`continuum.md` line 16 (continuum PR #1): "Once labels, grids, and single-sense silos are stripped away, raw telemetry across wildly different physical domains ... reveals the same four universal transformations sculpting reality."

The sentence states a result. The essay names categories of telemetry (spacetime strain, radio bursts, planetary vibrations, neural arrays) and no archive, mission, file or script. Search: `grep -nE "https?://|github|AUDIT|\.py|\.csv|\.fits" continuum.md` gave 0 hits.

## 2. Evidence status of line 16

Classes: (i) a run on measured data, (ii) a run on simulated or constructed data, (iii) model text, (iv) not found.

| Item | Location | Class | What it is |
|---|---|---|---|
| Any run on measured telemetry attached to PR #1 | PR #1 file list (5 files) and PR body | (iv) | The body is one summary sentence and three short lines. No script, data file, log or audit id is linked |
| Archive pointers in the session export | `session_raw_verbatim_export.json`, turn 18 (`GWOSC Open Archive // Record GPS-1126259462`), turn 20 (`MAST / K2 Archive // Record EPIC-200164267`) | (iii) | Both turns have role `model`. The export's `notes` field says raw audio and video bytes of the live portion "are not accessible" |
| The same pointers in the cave-expedition map | `cartography/session1_instrument_map.md` line 51 | (iii) | "model-synthesized structural reductions of known public archives, NOT outputs of live data downloads" |
| Continuum PR #3 (draft) | `expedition-synthesis/*.py` (6 scripts) and `expedition-double-slit-continuum/*.py`, ledger ids AUDIT-004 to AUDIT-008R and AUDIT-019 | (ii) | Exact-arithmetic checks on constructed matrices. `audit_continuum_probes.py` integrates a simulated Rossler system (function `integrate_rossler`, line 179). Search `grep -nE "urlopen|requests|urllib|astroquery|gwpy|h5py|np\.load|read_csv|wget|curl"` over both folders: 0 hits. PR #1 does not link PR #3 |
| cave-expedition AUDIT-003 | `verification/AUDIT_LOG.md` line 12, `verification/checks/check_002_session1_instruments.py` | (ii) | Tests the code blueprints from the session on generated signals (`np.random.default_rng` at lines 42 and 148) |
| gravity PR #30 chirp estimator | `studies/expedition-aest-helmholtz-probes/probe2_latch_outside_anchors_and_chirp.py`, `make_pair` at line 554 | (ii) | Generated chirps, glitches and an IAAFT surrogate (a noise copy with the same spectrum). No download or file read found |
| Planned run on real strain | cave-expedition `NEXT_WAVES_COMPUTE.md` lines 114 to 125, item `W2B-3`, `next_waves_manifest.json` line 135 | planned | The run is described as a future compute task. No result for `W2B-3` is in the files |
| Any run showing the four transformations in measured data | all clones, and GitHub code search over the owner's default branches | (iv) | Search strings and scope are in `SEARCHES.md` |

## 3. The four transformations as written

All four are written as standard formulas in `continuum.md` lines 17 to 28.

| # | Name | Line | Formulas |
|---|---|---|---|
| 1 | Subtractive Selection (Interference and Scale Flow) | 17 to 19 | stationary phase, renormalization group operator, fixed point condition |
| 2 | Symmetry Fracture and Topological Memory | 20 to 21 | vacuum manifold G/H, defects classified by homotopy groups |
| 3 | Irreversibility as Geometry | 22 to 26 | gradient flow in the Wasserstein metric, entropy production as a path log-likelihood ratio (display equation blank in `continuum.md`, present in the `Distill` file at line 38) |
| 4 | Duality and Emergent Space | 27 to 28 | adjunctions, modular inversion, entropy as area over 4G |

Section I (lines 5 to 14) lists four different "habits to replace". Those are not the four transformations.

## 4. Data inventory

"Raw" follows what each repo says. "Hash pinned" asks whether the input files have a recorded hash. Output files with recorded hashes are noted separately.

| Dataset | Repo, path, head | Committed or fetched | Hash pinned (inputs) | Terms stated | Raw or reduced |
|---|---|---|---|---|---|
| DASCH light curves, ASASSN-21co and about 360 comparison stars | plate-eclipses `c0b7b0b`, `src/fetch.py`, `src/dasch.py` line 3, README line 46 | Fetched at run time (about 200 MB, git-ignored). Committed derived: `results/asassn21co_plates.csv`, 3,163 rows | No | README line 238: raw light curves and cutouts not redistributed, "DASCH states no data licence". Code Apache-2.0 | Reduced: DASCH-calibrated magnitudes |
| DASCH plate cutouts | plate-eclipses, `src/cutouts.py`, `src/remeasure.py` | Fetched, not stored | No | same | Scanned plate images. The re-measurement is the project's own |
| DASCH light curves, 5 novae | plate-novae `9183100`, `pilot/fetch.sh` lines 7 and 15 | Fetched with `curl`. Committed: `results/pilot-2026-10-19.txt` | No | Not stated in README. Apache-2.0 code | Reduced |
| TESS 2-minute light curves, TESS full-frame cutouts, Gaia DR3 | exoplanets-frontier `3bc0163`, `mast_data.py` lines 12 and 23, `deep_search.py` | Fetched at run time. Committed: `results/` files and figures | No. Outputs only: `results/convergence_certificates.json` records `files_sha256` of result files | Not stated in README. MIT code | Reduced: pipeline products |
| Published bin tables typed into code (SPARC, KiDS-1000) | gravity PR #30 `00d8b1b`, `wave3_empirical_audit.py` line 36 onward | Committed as literals in the script. `RARbins.mrt` is named at lines 7 and 8 and is not in the tree | No (script hashes in `SHA256SUMS`) | Apache-2.0 code, CC-BY-4.0 results | Reduced: published bin means |
| Ten-Form Atlas archive pointers (GW150914, K2, Planck, FRB 121102, EPICA and others) | cave-expedition PR #1, `cartography/session1_instrument_map.md`, section 3 | Not fetched by any committed script found | No | Not stated | None held. Written from model memory, as the repo states (line 51, `cartography/frontier_portals.md` line 16) |
| Archive inventories | physics0 `913468f`, `data/seismic-networks/candidates.csv`, `data/noaa-climate-rescue/scans.csv` | Committed lists made by `inventory.py` | No | Not stated | Metadata only |

Findings from the table:

- No raw instrument file is committed in any repo read. Search: `git ls-files` over 15 clones, filtered for `.fits .fit .h5 .hdf5 .sac .edf .mseed .gwf .npy .npz .parquet .wav .fil`: 0 files.
- Three repos fetch measured data at run time and record no hash for the inputs: plate-eclipses, plate-novae and exoplanets-frontier. Search: `grep -rIlE "sha256|hashlib|md5"` over the three repos found hashing only of files written to `results/` (`hz_vet.py` lines 107 to 108, `cool_vet.py` lines 105 to 106, `refresh_dr4.py` lines 77 to 78, `report_v3.py` line 33).
- Three repos in the table (plate-eclipses, plate-novae, exoplanets-frontier) test known models on measured data. Their checks include nulls and unseen data.
- plate-eclipses: README line 15 (period scan against 40 null runs) and line 115 (none of the 40 reaches the peak height).
- exoplanets-frontier: `CLAIMS.md` C-01 at line 14 (held-out Sectors 106 and 107, 22 of 39 pairs recovered) and C-03 at line 24 (0 of 10 scrambled-null false alarms).
- plate-novae: README line 31 (five stars are too few to measure a false-alarm rate).
