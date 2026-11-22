# Independent check of Amendment 2

This folder holds an independent recomputation of the numbers in `AMENDMENT_2.md` and a reading of the amended `PREREG.md` for gaps. The checker did not read the author's `checks/` code before it had its own numbers, did not read any run output of the detector code, and opened no data file. Anyone can rerun every script from a clone of this branch.

It sits beside the check of Amendment 1 (`../README.md`) and reuses its runner and its outcome enumeration.

Version checked: commit `fba51a3`. `PREREG.md` SHA-256 `1dfc2c8cc191a09418938193c06bf2feda367f6162251df0e422474c02441b3f`, `AMENDMENT_2.md` SHA-256 `93e170b3f3d01405d1a92ed8131095dca85844f7eae8c5843da38019bf088d90`.

## How the check was done

- Every number was recomputed from the plan text with the checker's own code. Exact claims use whole numbers and fractions. Sampled claims print their seeds and give intervals.
- Every script has must-fail controls: wrong inputs that the script has to flag.
- Every script gives identical output under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`. `out/` holds all three. No script uses a bare `assert`.
- Python needed: the exact scripts use only the standard library (recorded with Python 3.12.15). The sampled scripts need numpy (recorded with Python 3.14.6 and numpy 2.5.4).

## What each script checks

| Script | What it checks | Result on the published files |
|---|---|---|
| `published_files_check` | Hashes of the plan files, the README hash table, line endings, local paths, names and emails | table matches the files, nothing found |
| `quotes` | Every old-text quotation in `AMENDMENT_2.md` against commit `f584897` at the cited line | all found at the cited lines |
| `classify_diff` | Every changed block of `PREREG.md` against `f584897` | 21 blocks, each one traces to an item of the amendment |
| `test_counts` | The two test families and the Holm thresholds | 40 confirmatory tests, 102 Law 2b tests, 0.00125 and 0.000490 |
| `../src/outcomes.py` | The decision procedure over every state | one outcome for each of 11,664,000 main-test states and 11,664 scale-flow states, 129,867 partial states |
| `holm_steps` | B1: the largest chance that a series with a segment rate of 0.10 or 0.129 passes one presence run, at the smallest and the largest Holm step, over 12 to 32 segments and 8, 7 or 5 runs | the nine figures of B1 reproduce (0.012, 0.0086, 0.00081, 0.047, 0.029 at the smallest step, 0.069, 0.035, 0.142, 0.076 at the largest) |
| `compute_and_points` | B4 and B12: every row and sum of the compute table, the K2 control flag point, the series counts of B5 and B9 | the table sums exactly (284,401.87 processor-seconds per mode, 853,205.61 for three modes, 243,926.22 for the Law 2b worst case), the flag point is 22 of 200, 13 and 10 series counts agree |
| `k1_scope` | B5: the representability guard on all 9 classes in 3 versions at 4,096, 2,048 and 1,024 samples, 20 seeds, with the rescaled maps and with the old maps | 0 failures in 4,860 cases with the rescaled maps, 62 failures with the old maps (all in the squared-Gaussian class), so the rescaling is needed. Division by the maximum can merge neighbouring doubles (9 to 12 percent of one-step-apart pairs), which never happened in the classes |
| `k1_normal_scores` | B5: normal scores of the exp and cube versions against the plain version | equal in all 540 comparisons |
| `tied_waveform` | B6: the tied waveform, pattern counts against reversed counts, the three maps, and the must-fail ranking that breaks ties in time order | exact zeros, 3,070 tied windows, the control gives a non-zero statistic at every lag |
| `integer_identity` | B6: the whole pipeline on integer-valued null classes | identical under the three maps in 21 of 21 class-seeds |
| `constant_segments` | B7: what an extra invalid segment can do, and what happens when an absent instrument becomes underpowered | K cannot rise. Moving an instrument from absent to underpowered takes 1,138,944 of 3,499,200 flips out of "evidence against", never into supported or net-dependent |
| `tau0_integer_form` | B8: the integer form of "autocorrelation below 1/2" | equal to the exact rational test in 23,505 cases, an exact one half is not counted as below |
| `saw_noise` | The sawtooth: peak to peak 63/64, noise 0.1443 | reproduces |
| `yprime_const` | B9: the constant of y' by a Hermite expansion (one-dimensional integration) and by simulation | c = 0.985964, so 0.9859. Lags 15, 16 and 17 give 0.5178, 0.4986, 0.4804. First lag below 1/2 is 16. The simulation agrees within about one standard error |
| `k5_series_checks` | B9: the earlier constant, the new series and the jointly populated features | for c = 2^(-1/32) the first lag below 1/2 is 11, the new criteria are evaluable |
| `cascade_tau0` | B9: the cascade as section 10 states it, tau0 by seed, y' and the surrogate cascade, joint features | cascade tau0 8 to 17 over 12 seeds (shifts 3 and 4), y' shift 4 in all seeds, at least 27 jointly populated features |
| `seed_keys` | Reading D14: are the seed keys of the known-answer tests distinct? | see the open points below |

## History of the three passes

Pass 1 checked the first draft (items B1 to B4). It confirmed the false-presence figures and the Holm-step figures. It asked for three corrections, which the author applied:

- The compute table had counts that the plan did not state (K1 classes, the K4 timing, the fit stage channels, the flow units) and left out the paired K4 and K5 tests of every Law 2b instrument.
- The reviewer could be replaced without any recorded reason.
- The reviewer item was described as a rewording although it added three procedural conditions.

Pass 2 checked the enlarged draft (items B5 to B12). It confirmed the K1 guard, the tied waveform, the constant-segment rule, the compute sums and the test counts. It asked for four corrections, applied by the author:

- The claim that the rank autocorrelation of the squared Gaussian series follows c to the power 2k was wrong. It holds for the values, not for the mid-ranks. The cascade was also not defined.
- Section 5 said the amplitude maps act on the segment, while reading D10 said the whole stream.
- The constant-segment item did not say that an absent instrument can become underpowered.
- Several float comparisons had no stated rule.

Six smaller points followed: the first K1 bullet still named the old maps, the seed fields were not written out, the sawtooth range, the template scaling note, the K2 control in the opening list, and the source of the 490 second timing.

Pass 3 checked the changed lines. It reproduced the constant of y' by a different integration (0.985964, not the 0.9852 that an earlier rough estimate had suggested). It confirmed the cascade construction by seed, the integer form of the tau0 comparison and the new rules. It found two gaps, both fixed in the published text:

- The seed fields still left some draws unspecified (the two must-fail controls, the pool surrogates, the draw order).
- The tau0 sentence said the numerator and denominator were integers without saying how.

Pass 4 checked the published text against the last draft: the seed fields, the tau0 sentence, the median of the Wind/WAVES intervals, the template note and the wording about the 0.9852 estimate. All are in. It reran the author's three scripts in `checks/amendment_2/` from a clean clone. The output is identical in the three modes and equal to the committed outputs.

## Still open in the published text

Found by `seed_keys`, not yet corrected:

- Section 11a, reading D14, gives each flow unit's surrogate pool a key without the seed number (`flow-L<level>-q<unit>`). The 10 seeds of one K5 case then share one key per unit: 15,400 pools, 1,540 distinct keys. Adding the seed number to the segment field makes them distinct.
- The K3 pool key is written without the length (`K3:<case>`), while the general rule says a pool takes the key of its segment. The nets keep the keys distinct, so this is a wording difference only.
- The random-detector keys of K4 and K5 state the purpose and the run but not the instrument pair or the criterion, so the three K5 criteria could share one detector key.

These need a dated amendment before the detector code is built.

## Not checked

- The whole K5 test and the K4 test: only the construction of their series and the joint-support rule were checked.
- Anything that depends on the detector code, its smoke runs or the code commit named in section 11a.
- The measured timings behind the compute table (the 2.29 and 490 second costs) and the sector and cadence counts.
- Data files: none were opened.
- Reading D1 to D18 beyond the points listed above, and the Aletheia and Law 2b texts beyond the lines the plan cites.
- The sampled checks are small (12 seeds for the cascade, 20 for the K1 guard, 3 per class for the integer-valued identity). They show size and direction.

## How to rerun

From inside a clone of this branch (the scripts that compare with the base commit use `git`):

```
PY_EXACT=python3.12 PY_NUMPY=python3.14 verification/outside/continuum-four-transformations/independent_check/amendment_2/run_all.sh
```

`run_all.sh` runs every script in the three modes at once and writes `out/SUMMARY.txt` and the per-mode outputs. It takes a few minutes. One script alone, from the `amendment_2` folder:

```
../run3.sh python3.12 src/holm_steps.py
```

The scripts read `PREREG.md`, `AMENDMENT_2.md`, `README.md` and `AMENDMENT_1.md` two folders up. If those files change, the comparisons with the published figures change with them.

## Working rules

No file was deleted in the four passes of this check. The first check records the two earlier deletions of scratch files in its own README.
