# Smoke results of the amended known-answer tests

These are smoke runs: one twentieth of the plan's seeds, at least 10, the same seed rule. They exist to find faults in the code and to estimate run time. They are not results. The full runs have not been started and no data file has been opened.

K4 and K5 have 10 seeds in the plan, so their smoke runs use all 10. The outputs are in `out_smoke/`, with the three-mode runs in `out_smoke/modes/`.

| Test | Smoke size | Observed | Must-fail control |
|---|---|---|---|
| K1 | 10 seeds per class, 2,928 checks | 0 failed | all three flagged (82, 58 and 1,379 failing checks) |
| K2 | 50 seeds per class, two lengths | no class flagged. Null classes 0 to 8 of 50 reject. Reversible classes 0 to 5 of 50 | raw-value surrogates: 4 of 10 reject, flag point at 10 seeds is 5. Not flagged |
| K3 | 10 seeds per case | one gating cell below the 50 percent criterion: logistic map under subsampling by 2 (3 of 10). The noisier sawtooth is reported and does not gate | circular shifts: 1 of 10 detected, bound 1. Flagged |
| K4 | 10 seeds | A to B passes in 9 of 10 seeds. A to C arrow adverse in 10 of 10. Blind spot: no rejection in 20 of 20 | A to A': no seed reaches p at most 0.01 (arrow 0, profile 0). Flagged |
| K5 | 10 seeds | every criterion met in at least 9 of 10 seeds. The two p above 0.05 criteria passed in 20 of 20 transfers only through the populated-feature floor | shuffled cascade meets the cascade criterion in 0 of 10 seeds. Flagged |
| K6 | none | six refusals fire, removal of each flagged | all six flagged |

The unit checks (240) pass. The unit checks, K1, K2, K3 and K6 give identical output in `-I -B`, `-I -O -B` and `-I -B -W error`. K4 and K5 were run in the first mode only.

## Run time

Wall and processor seconds in the first mode, from `out_smoke/timing.txt` (K4 and K5, run while the machine was heavily loaded) and `out_smoke/modes/timing_modes.txt` (the others, load low). Processor time is the figure to scale from.

| Test | Processor seconds (smoke) | Wall seconds (smoke, 6 workers) |
|---|---|---|
| unit checks | 30 | 35 |
| K1 | 332 | 92 |
| K2 | 933 | 264 |
| K3 | 262 | 49 |
| K4 | 4,648 | 1,161 |
| K5 | 8,765 | 1,562 |
| K6 | 0.1 | 0.1 |

Estimate for a full run in one mode, scaling processor time by the seed ratio: K1 about 660 s (20 seeds against 10), K2 about 5.2 hours (20 times the smoke seeds, plus the control at 200 seeds), K3 about 1.5 hours (20 times), K4 and K5 equal to their smoke runs (the same 10 seeds), so about 1.3 and 2.4 hours. The K4 and K5 times were measured under heavy load and may be high.

The total is about 11 processor-hours per mode, about 1.9 hours of wall time at 6 workers if the machine stays quiet. Three modes triple this.
