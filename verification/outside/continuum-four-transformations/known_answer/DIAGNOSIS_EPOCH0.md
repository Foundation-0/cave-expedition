# Diagnosis of the epoch-0 shortfalls (K2 control, K3, K4 reading 2)

This file reports extra runs on the present seed keys (epoch 0). They are diagnostics. They cannot pass a test, and they change no code under test. The scripts are in `diagnostics/` and the outputs in `out_diagnostics_epoch0/`.

An alternative key differs from the real one only in its purpose field, which gets the prefix `diag-` (pools) or `diag1-` to `diag3-` (detectors). No epoch-1 key was built. The plan's author has not seen any of this.

## What was run

| Run | Seeds | Command (python3.14 -I -B, sandboxed, niced) | Output |
|---|---|---|---|
| Controls: K2 control, K3 circular-shift control, each with its real pool key and an alternative pool key, and the plan's method on the same series | 200 | `known_answer/diagnostics/diag_controls.py` | `DIAG_controls.txt` |
| K4 A to B, both readings, seeds 0 to 9, with three alternative detector keys and an alternative pool key | 10 | `diagnostics/diag_k4.py 0 9 1` | `DIAG_k4_seeds0_9_with_alt_keys.txt` |
| K4 A to B, both readings, more seeds | 10 to 49 | `diagnostics/diag_k4.py 10 49 0` | `DIAG_k4_seeds10_49.txt` |
| K3 at the plan's full count | 200 per case | `k3_planted_structure.py full` | `DIAG_k3_full_part0.txt` |
| K2 at the plan's full count | 1,000 per class, control 200 | `k2_nothing_in_noise.py full` | `DIAG_k2_full_part0.txt` |

A fault of the code that matters for later runs: the part option of `k2`, `k3`, `k4` and `k5` is read from `argv[3]` and `argv[4]`, but the usage and `run_full.sh` give the part number and the number of parts as `argv[2]` and `argv[3]`. With one token too few, the option is ignored and the whole test runs.

The K3 "parts" 0 to 3 therefore each ran the full K3 (four identical outputs), and the K2 "part 0" ran the full K2. The K2 "part 1" duplicate was stopped. Nothing was changed. `FULL_RUN.md` and `run_full.sh` will not split a run until this is fixed.

## 1. K2 control: 4 of 10 against a flag point of 5

| Measurement | Count |
|---|---|
| Raw-value surrogates, real pool key, rejecting segments at 10, 20, 50, 100, 200 seeds | 4, 7, 10, 20, 46 |
| The same with an alternative pool key | 5, 7, 11, 18, 45 |
| The plan's normal-score surrogates on the same series | 0, 1, 2, 5, 11 |
| Flag points of the K2a rule at its own seed count | 5 of 10, 22 of 200 |

| Possibility | Evidence | Status |
|---|---|---|
| Fault in the code against the plan | The path is the plan's: raw-value surrogates (cap 100 iterations, start from a permutation of the raw values), the exp version of AR(1) 0.9 at 4,096 samples, the pool key of the plain draw. The plan's method on the same series gives 11 of 200, close to the null rate of 0.05 | no fault found |
| Too little power at the planned size | At the plan's 200 seeds the control gives 46 of 200 against a flag point of 22. At 10 seeds the flag point is 5, and with a rate near 0.23 a count of 5 or more has probability about 0.06 | shown: the 10-seed smoke count is a sampling miss |
| Dependence on the pool draw | Changing only the pool key gives 45 of 200 instead of 46 | shown: no dependence |
| Flaw in how the known answer is built | The effect is there: 46 of 200 with raw values against 11 of 200 with normal scores on the same series. The control is a case that must be flagged and is flagged at its full count | shown: no flaw |

## 2. K3: shots at `wlen2048`, logistic subsampling, and the circular-shift control

Full count on epoch 0 (200 seeds per case): native 4,096 shots 190, logistic 200, sawtooth 200. Shots: native 2,048 143, bm2 119, sub2 144, q12 192, q8 183, placement 185, `wlen2048` 117. Logistic: sub2 74, every other use 199 or 200.

The circular-shift control: 11 of 200 against a bound of 20 (9 of 200 with an alternative pool key). The plain-draw shots detection with the plan's method: 190 of 200. Result at full count: FAIL, with one gating cell below its criterion, logistic sub2 at 74 of 200 (needs 100).

| Item | Smoke | Full count (200) | Status |
|---|---|---|---|
| Shots `wlen2048` | 4 of 10 against 5 | 117 of 200 (0.585, Wilson 95% interval 0.52 to 0.65) against 100 | shown: sampling miss at 10 seeds. Probability of 4 or fewer of 10 at this rate is about 0.19. At 200 seeds it passes |
| Circular-shift control | 2 of 10 against a bound of 1 | 11 of 200 (0.055) against 20 | shown: sampling at 10 seeds (and 2 of 10 is not unusual at 0.055). The control behaves at full count. An alternative pool key gives 9 of 200, so no dependence on the shared draw |
| Logistic sub2 | 1 of 10 against 5 | 74 of 200 (0.37, interval 0.31 to 0.44) against 100 | shown: below the line at full count, by 26 segments. Cause of the weak detection: unknown. The same series is detected 199 or 200 of 200 under every other use. The plan's own known answer asks for 50 percent here |

Agreement with the independent check's own K3 implementation (`independent_check/out/k3_detection.mode1.txt`, other seeds and its own surrogates): shots native 4,096 0.97 (mine 0.95), sub2 0.70 (mine 0.72), native 2,048 0.70 (mine 0.715), mean by 2 0.61 (mine 0.595), circular shifts 0.03 (mine 0.055).

The independent check has no logistic case. Fault in the code against the plan for the shots path: none found, since the two implementations agree within sampling.

Expected result of K3 at full count: it fails, on the logistic sub2 cell (74 of 200 observed, so at 0.37 the chance of reaching 100 is far below 0.01). The shots cells, the sawtooth and the control pass.

## 3. K4 reading 2: A to B in 7 of 10 seeds

A to B on seeds 0 to 49, default keys (arrow p and profile p at most 0.001 in every run):

| Reading | Seeds 0 to 9 | Seeds 10 to 49 | All 50 |
|---|---|---|---|
| 1 (D20) | 9 | 28 of 40 | 37 of 50 (0.74) |
| 2 | 7 | 21 of 40 | 28 of 50 (0.56) |

Every failure is the arrow transfer. The profile transfer passes in all 50 seeds in both runs. Arrow p at or below 0.001: reading 1 native 39 of 50, placement 38 of 50. Reading 2 native 39 of 50, placement 32 of 50.

The median arrow p is 5.3e-4 (native), 4.3e-4 (reading 1 placement) and 3.8e-4 (reading 2 placement), so the threshold of 0.001 lies inside the distribution of the p-values. In reading 2 the level shift of B differs between the two grids in 19 of 50 seeds (by +1 in 12 and by -1 in 7). A never differs.

Seeds passing the placement run under (reading 1, reading 2): 28 (yes, yes), 8 (no, no), 10 (yes, no), 4 (no, yes).

With the probability that a seed passes taken as 0.74 (reading 1) and 0.56 (reading 2), the chance of 9 or more passing seeds out of 10 is about 0.22 and 0.03.

| Possibility | Evidence | Status |
|---|---|---|
| Fault in the code against the plan | The reading-2 path follows D20's second reading (templates and level shifts from the fit streams of the run's own grid, pools for the extra fit and verdict streams, the same detector keys as reading 1). No difference from the text found | no fault found |
| Too little power at the planned size | A to B arrow p is small (median about 5e-4) but not far enough below 0.001. The per-seed pass rate is 0.56 to 0.74 and does not move with more seeds (first 10 seeds 0.9 and 0.7, next 40 seeds 0.70 and 0.525) | shown |
| Dependence on the detector pool or a shared draw | Seeds 0 to 9, reading 2, three alternative detector keys and one alternative pool key: the arrow p of the placement run moves by at most a factor of 1.5 and only the borderline seed 0 (9.0e-4, 6.6e-4 to 6.7e-4, 6.4e-4) crosses the line. Passing seeds out of 10: 7 (real keys), 7, 7, 6 (detector keys), 6 (pool key). Seeds 2, 4 and 6 fail under every key | shown: small effect on the borderline seeds only. No two seeds share a pool (the key check) |
| Flaw in how the known answer is built | The planted effect is present (profile p at or below 0.001 in 50 of 50 seeds, arrow p small in every seed, A to C adverse in 10 of 10 seeds). The criterion asks for 9 of 10 seeds at p at most 0.001 in every run, which needs a per-seed pass probability near 0.95 | shown: the criterion is out of reach at the observed power under either reading |
| Why reading 2 is lower than reading 1 | 32 against 38 of 50 in the placement run, with discordant seeds 10 against 4 | unknown: the difference is not large (a sign test on 10 against 4 gives about 0.18), and it may be sampling |

## 4. Whether the full count would be expected to pass

K3: no (logistic sub2, shown above). K2 on epoch 0: FAIL. One class is flagged: AR(1) 0.99 at 2,048 samples gives 75 of 1,000 against a flag point of 74 (Wilson 95% interval 0.060 to 0.093).

The other null classes give 43 to 59 of 1,000, the reversible classes give 49 and 68 (4,096) and 42 and 82 (2,048) of 1,000 against a flag point of 129, and the control is flagged (46 of 200 against 22). The class rate is not known well. If its true rate were 0.06 the chance of a flag on a fresh draw is about 0.04.

At 0.0625 it is 0.08 and at 0.07 it is 0.33. For a fresh draw, K2 would pass with a chance between about 0.15 (rate 0.093) and 0.96 (rate 0.06), and about 0.5 at the observed rate of 0.075. This run cannot narrow that uncertainty.

## Not determined

- Why the logistic map after subsampling by 2 is detected at 0.37 while every other use of it is detected at 0.995 or more.
- Whether the lower pass rate of reading 2 against reading 1 is systematic.
- The true rate of AR(1) 0.99 at 2,048 samples.
