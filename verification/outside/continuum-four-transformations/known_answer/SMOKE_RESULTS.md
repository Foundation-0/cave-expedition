# Smoke results of the Amendment 3 code (outputs in `out_smoke_amendment3/`)

The code now implements the plan as amended by Amendment 3 (plan commit 2d24771). K1 to K3 ran at one twentieth of the plan's seeds (at least 10). K4 and K5 have 10 seeds in the plan, so their runs are at the full count.

Smoke runs are not results, and the K4 and K5 runs are diagnostics only because the seed keys are going to change. The full runs are on hold. No data file has been opened. `OUTCOME_LOG.md` lists every run with its time, the state of the code and who has read it.

- K1: PASS. 7,614 checks, 0 failed, 132 (class version, map) combinations all representable, four must-fail controls flagged. Rule: every identity exact, at least 9 of 10 representable seeds per combination at this size.
- K2: FAIL. No class is flagged (null classes need 10 or more of 50, reversible classes 13 or more of 50). The must-fail control is judged by the K2a rule at its own seed count: 10 seeds, flag point 5, and it shows 4. It is not flagged. At the plan's 200 seeds the flag point is 22.
- K3: FAIL. Rule: native at 4,096 needs at least 8 of 10 and every other use at least 5 of 10, and the circular-shift control at most 1 of 10. Shots at `wlen2048` shows 4 of 10 and logistic subsampling 1 of 10, both below. The control shows 2 of 10 and is not flagged.
- K4: FAIL. Reading 1 PASS (A to B 9 of 10, A to C 10 of 10, control 0 and 0). Reading 2 FAIL (A to B 7 of 10 against 9 needed). K4 passes only if both readings pass. The blind spot is reported for both detectors: the arrow transfer rejects in 0 runs and the profile transfer in 20 of 20 (reading 1) and 40 of 40 (reading 2) seed-direction-runs.
- K5: PASS. Every criterion in at least 9 of 10 seeds, and the shuffled-cascade control in 0 of 10. The first run stopped on a naming fault in the report code and is kept.
- K6: PASS. Six refusal codes, every deletion flagged.

Processor time, first mode, this code: K1 710 s, K2 955 s, K3 257 s, K4 6,605 s (rerun, 6,917 s first run), K5 12,294 s.

Unit checks, key check, review witnesses and K6 give identical output in the three Python modes. K1, K2 and K3 were also run in all three modes with identical output.

# Earlier smoke results

## Amendment 2 code (outputs in `out_smoke_amendment2/`)

The code now implements the plan as amended by Amendment 2 (plan commit fba51a3). These are smoke runs at one twentieth of the plan's seeds (at least 10). They are not results. The full runs are on hold. No data file has been opened.

| Test | Smoke outcome |
|---|---|
| unit checks | 336 checks, 0 failed, identical output in the three Python modes |
| review witnesses | no unguarded failure, identical in the three modes |
| K1 | first run FAILED on a fault in my test code (the 18-of-20 coverage rule was applied to the single tied waveform, which has no seeds). The output is kept as `k1_exact_checks_SMOKE_first_run_coverage_rule_fault.txt`. After the fix: 7,614 checks, 0 failed, all four must-fail controls flagged, no case recorded as "map not representable". Identical in the three modes |
| K2 | no class flagged. The must-fail control is not flagged at 10 seeds (4 of 10 against a flag point of 5). Identical in the three modes, and identical to the earlier smoke run |
| K3 | one gating cell below 50 percent (logistic map under subsampling by 2, 3 of 10). Control flagged. Identical in the three modes |
| K4 | passes: A to B in 9 of 10 seeds, A to C in 10 of 10, the A to A prime control reaches p at most 0.01 in no run. First mode only |
| K5 | stopped with an error at seed 0 (a non-finite series). The second amplitude-map run takes the exp of the standardised exp-mapped cascade, which overflows (about 724 standard deviations, and exp of that is infinite). No result. The error text is kept as it came out, with the local folder name in its paths replaced by `<build folder>`. See `AMENDMENTS_NEEDED.md`, entry BLOCK-1 |
| K6 | passes, seven deletions of a refusal all flagged. Identical in the three modes |

The mutation test over `src/` (`out_mutation/`) killed 148 of 284 mutants with the unit checks and K6 as the suite. The 136 survivors are listed and have not been triaged. The seed-key counts are in `out_keys/`.

Smoke processor seconds: K1 715, K2 910, K3 252, K4 4,473, unit checks 27.

# Smoke results of the Amendment 1 code (first push, kept for the record)

These are smoke runs: one twentieth of the plan's seeds, at least 10, the same seed rule. They exist to find faults in the code and to estimate run time. They are not results. The full runs have not been started and no data file has been opened.

K4 and K5 have 10 seeds in the plan, so their smoke runs use all 10. The outputs are in `out_smoke/`, with the three-mode runs in `out_smoke/modes/`.

| Test | Smoke size | Observed | Must-fail control |
|---|---|---|---|
| K1 | 10 seeds per class, 2,928 checks | 0 failed | all three flagged (82, 58 and 1,379 failing checks) |
| K2 | 50 seeds per class, two lengths | no class flagged. Null classes 0 to 8 of 50 reject. Reversible classes 0 to 5 of 50 | raw-value surrogates: 4 of 10 reject, flag point at 10 seeds is 5. Not flagged |
| K3 | 10 seeds per case | one gating cell below the 50 percent criterion: logistic map under subsampling by 2 (3 of 10). The noisier sawtooth is reported and does not gate | circular shifts: 1 of 10 detected, bound 1. Flagged |
| K4 | 10 seeds | A to B passes in 9 of 10 seeds. A to C arrow adverse in 10 of 10. Blind spot: no rejection in 20 of 20 | A to A': no seed reaches p at most 0.01 (arrow 0, profile 0). Flagged |
| K5 | 10 seeds | every criterion met in at least 9 of 10 seeds. The two p above 0.05 criteria passed in 20 of 20 transfers only through the populated-feature floor | shuffled cascade meets the cascade criterion in 0 of 10 seeds. Flagged |
| K6 | none | six refusal codes fire on their must-fail inputs, including bool and complex arrays | each of 7 deletions of a refusal from a copy of the source is flagged |

The unit checks (294) pass.

After the fixes for an outside review (see `AMENDMENTS_NEEDED.md`, Part G) all six smoke tests were run again. The outputs of K1 to K5 are byte-identical to the first smoke run, so no smoke number changed.

The K6 output changed because K6 now deletes each refusal from a copy of the source (the earlier file is kept as `out_smoke/k6_gate_checks_SMOKE_before_review_fixes.txt`). The unit checks, the review witnesses, K1, K2, K3 and K6 give identical output in `-I -B`, `-I -O -B` and `-I -B -W error`. K4 and K5 were run in the first mode only.

## Run time

Wall and processor seconds in the first mode, from `out_smoke/timing_rerun_after_review_fixes.txt` (K4, run while the machine was heavily loaded) and `out_smoke/modes/timing_modes.txt` (the others, load low). Processor time is the figure to scale from.

| Test | Processor seconds (smoke) | Wall seconds (smoke, 6 workers) |
|---|---|---|
| unit checks | 27 | 27 |
| K1 | 305 | 57 |
| K2 | 900 | 160 |
| K3 | 250 | 43 |
| K4 | 4,648 | 1,161 |
| K5 | 8,668 | 1,492 |
| K6 | 0.1 | 0.1 |

Estimate for a full run in one mode, scaling processor time by the seed ratio: K1 about 610 s (20 seeds against 10), K2 about 5 hours (20 times the smoke seeds, plus the control at 200 seeds), K3 about 1.4 hours (20 times), K4 and K5 equal to their smoke runs (the same 10 seeds), so about 1.3 and 2.4 hours. The K4 time was measured under heavy load and may be high.

The total is about 10 processor-hours per mode, about 1.8 hours of wall time at 6 workers if the machine stays quiet. Three modes triple this.
