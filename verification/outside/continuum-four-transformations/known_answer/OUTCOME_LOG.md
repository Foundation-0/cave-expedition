# Outcome log of the known-answer runs on the Amendment 3 code

Every run of K1 to K6 on the code built for Amendment 3 (plan commits 4c6ecd1 and 2d24771) is listed once. Times are the times the output files were last written, in UTC. Local time of the machine is six hours behind UTC.

K4 and K5 have 10 seeds in the plan, so a run with 10 seeds is a full-count run. K6 has no seeds. K1 to K3 at the sizes below are smoke runs, at one twentieth of the plan's seeds, and are not results. The seed keys of this code are going to be replaced by a coming amendment, so the K4 and K5 runs here count as diagnostics only. Outputs are in `out_smoke_amendment3/`.

Guard column: whether the all-tied guard (the narrow rule that is now archived in `archived_patches/`) was in the code when the run started. K1, K2, K3 and K6 never call the transfer test, so it could not matter to them.

| Family | Run | Seeds (full count) | Full count? | Guard | Finished (UTC) | Outcome under the plan's rule | Read by |
|---|---|---|---|---|---|---|---|
| K1 | smoke | 10 per class version (20) | no | in | 2026-11-23 06:09 | PASS. 7,614 checks, 0 failed. 132 (class version, map) combinations, all representable. Four must-fail controls flagged | me, routing party |
| K2 | smoke | 50 per class (1,000), control 10 (200) | no | in | 2026-11-23 06:17 | FAIL. No class flagged (null classes flagged at 10 or more of 50, reversible classes at 13 or more of 50). The must-fail control is judged at its own seed count: 4 of 10 reject and its flag point is 5, so it is not flagged | me, routing party |
| K3 | smoke | 10 per case (200) | no | in | 2026-11-23 06:11 | FAIL. Native at 4,096 needs at least 8 of 10 and every other use at least 5 of 10. Two gating cells are below: shots at `wlen2048` 4 of 10 and logistic subsampling 1 of 10. The circular-shift control must stay at 1 or fewer of 10 and shows 2 of 10, so it is not flagged | me, routing party |
| K4 | first run | 10 (10) | yes | in (it was reverted during the run) | 2026-11-23 08:11 | FAIL. Reading 1 PASS: A to B 9 of 10 (need 9), A to C 10 of 10, control 0 and 0 (allowed 1). Reading 2 FAIL: A to B 7 of 10 (need 9), A to C 10 of 10, control 0 and 0. Combined FAIL | me, routing party |
| K4 | rerun on the code to be pushed | 10 (10) | yes | out | 2026-11-23 09:33 | Output byte-identical to the first run. Reading 1 PASS, reading 2 FAIL, combined FAIL | me |
| K5 | first run | 10 (10) | yes | out | 2026-11-23 08:11 | No result. It stopped at the report step on a naming fault in my report code (the old run name `amp_exp`) | me, routing party |
| K5 | rerun with the naming fixed | 10 (10) | yes | out | 2026-11-23 09:05 | PASS. Every criterion in at least 9 of 10 seeds (shuffled cascade none 9 of 10, the others 10 of 10), the control 0 of 10 | me |
| K6 | three modes | none | yes | in, then out | 2026-11-23 06:06, and again in the final run | PASS. Six refusal codes, 7 deletions all flagged | me, routing party |

K5 report code change: in `k5_scale_flow.py` the report step looked up the run name `amp_exp`, which Amendment 3 renamed `amp_lognormal`. The two occurrences were changed. No computed value changed (the criteria and counts are computed from the same results). The first run's output and error are kept as `k5_scale_flow_SMOKE_first_run_evaluate_fault.*`.

Error files kept with their paths show the local folder as `<build folder>`.

The plan's author has been told of the K5 crash and the K1 harness fault of earlier builds, and has been told no outcome of the runs above.

## Diagnostic runs on epoch 0 (extra runs, after the log above)

These runs use the present keys (epoch 0). They cannot pass a test, and they were made to find why three smoke results fell short. Details and conclusions are in `DIAGNOSIS_EPOCH0.md`. Times are local time of the machine on 2026-11-23, six hours behind UTC. The routing party has seen only the summary of the controls run (in an earlier report). The plan's author has seen none of them.

| Run | Seeds | Finished (local) | Outcome | Read by |
|---|---|---|---|---|
| Controls (K2 control and K3 circular-shift control, real and alternative pool key, plan's method on the same series) | 200 | 05:51 | K2 control 46 of 200 (flag point 22). K3 control 11 of 200 (bound 20) | me, routing party (summary) |
| K4 A to B, both readings, with alternative detector and pool keys | 0 to 9 | 06:05 | reading 1 9 of 10, reading 2 7 of 10 (6 to 7 under the alternative keys) | me |
| K4 A to B, both readings | 10 to 49 | 06:37 | reading 1 28 of 40, reading 2 21 of 40 | me |
| K3 at the plan's full count, run four times by mistake (the part option was ignored) with identical outputs | 200 per case | 07:09 to 08:50 | FAIL: logistic sub2 74 of 200 below 100. Control 11 of 200 | me |
| K2 at the plan's full count (the part option was ignored, so part 0 ran everything) | 1,000 per class, control 200 | 10:17 | FAIL: AR(1) 0.99 at 2,048 samples flagged (75 of 1,000 against 74). Control flagged (46 of 200) | me |
| K2 duplicate (part 1, which also ran everything) | | stopped | cut off, no result. Its partial files are kept | |

The guard column does not apply: the all-tied guard was out of the code for all of these. Processor time of the diagnostic runs: about 51,500 s (14 hours).
