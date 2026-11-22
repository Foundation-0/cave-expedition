# Known-answer results

All data are synthetic. Every series comes from a logged seed (master seed 20261121, the rule of `PREREG.md` section 11). The recorded outputs are in `out/`. Python 3.14.6, numpy 2.5.4.

K2, K3, K4 and K5 fail, and two K5 criteria were not run. K1 and K6 pass. The plan needs an amendment before real data are opened (see `../AMENDMENTS_NEEDED.md`). No detector, threshold or test was changed after a run.

| Test | What it plants | Criterion | Observed | Result |
|---|---|---|---|---|
| K1 | Exact identities of the pattern counts: three increasing maps, polarity flip, time reversal, lag doubling, and a second implementation that shares no code. 228 checks, orders 3 and 4, lags 1 to 512, with and without ties | Every integer count equal | 0 failures in 228 checks | PASS |
| K2 | Nothing: 21 noise classes (7 noises, each plain, after exp, after cube), 200 seeds each | Rejection rate at most 0.086 in every class | 11 of 21 classes above the bound, all of them exp or cube classes. Highest 0.295 (AR(1) 0.9 after exp). Plain classes 0.040 to 0.065 | FAIL |
| K3 | Shots in AR(1) noise, logistic map, sawtooth. 200 seeds per case | Detection at least 0.80 native, at least 0.50 after block mean by 2 and after whitening | Shots 0.915, 0.545, 0.440. Logistic 1.000, 1.000, 1.000. Sawtooth 0.215, 0.400, 0.185. Four of nine cells below the criterion | FAIL |
| K4 | Shots (A), shots in 1/f noise at half rate with flipped sign (B), time-reversed shots (C) | A to B: p at most 0.001. A to C: AUC below the 2.5th percentile of permuted templates | A to B p = 0.2025. A to C AUC 1.000 against 0.404 (primary) and 0.438 (shifted grid) | FAIL |
| K5 | Independent exponential values, and a random cascade, under block averaging | Norm falls below half (exponential), stays at least half (cascade). Two transfer criteria | Exponential ratio 2.573 (fails). Cascade ratio 0.702 (passes). Transfer criteria not run | FAIL |
| K6 | Empty, missing, constant and short input, plus wrong type and shape | Each refused with its own code. Removing a refusal fails the suite | 6 branches, all refused. Removal of each flagged | PASS |
| X1 | Extra: the plan's own arithmetic, segment rule, nets, features | Exact values | 29 of 30 checks. The one failure is the K2 bound (0.086 against an exact 0.090) | FAIL |
| X2 | Extra: controls C2, C3, C4 on shots data | Control rule of section 6 | K = 3, 1, 1 of S = 32, all absent. Leaky control K = 28 | PASS |
| X3 | Extra, descriptive: K2 with the IAAFT cap at 1,000 rounds | None | Three worst classes move from 0.283, 0.233, 0.183 to 0.267, 0.217, 0.167 | not scored |
| X4 | Extra, descriptive: sawtooth with the other reading of the noise level | None | Detection 1.000 on all three nets | not scored |

## Must-fail controls

Each control is a broken variant that the test must flag.

| Test | Broken variant | Flagged |
|---|---|---|
| K1 | Counter that drops the last window, counter that breaks ties by position, wrong reversal pairing in the statistic | Yes, all three (136, 20 and 10 failing checks) |
| K2 | Detector with no correction for the ten lags | Yes. White noise rate 0.315, all 21 classes above the bound |
| K3 | Surrogates made by circular shifts, which keep the time arrow | Yes. Detection 0.060, 0.135, 0.055 |
| K4 | Template that uses the size of the arrow feature, not its sign | Yes. A to C AUC 1.000 against 0.571 and 0.621 |
| K5 | The cascade criterion applied to a shuffled cascade | No. The shuffled cascade passes it (ratio 1.946) |
| K6 | Each refusal removed in turn | Yes, all six |
| X2 | Leaky generator in place of C2 | Yes. K = 28 of 32 |

## Notes

K4 diagnostics (not scored): a template cut to its sign-sensitive entries gives A to C AUC 0.186 against a 2.5th percentile of 0.270, but A to B p = 0.293. A template cut to the size entries gives AUC 1.000 for every target.

K3 passes for the logistic map in every net. The shots fail only after whitening (0.440). The sawtooth fails with the reading "noise standard deviation 0.5 at peak to peak amplitude 1" and is detected in every seed with the other reading (X4).

Three modes: every output is identical in `-I -B`, `-I -O -B` and `-I -B -W error`. The hashes are in `out/three_mode_check.txt`.

Run times are in `out/timing.txt`. K2 is run in seven parts, K3 in three and X3 in three, because an unsplit K2 attempt and an unsplit X3 attempt were stopped by the 30 minute limit on a machine under heavy load from other jobs.
