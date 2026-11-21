# twoloop_stack: outside checks for AUDIT-005 and AUDIT-006R

These scripts check the two-loop identities (AUDIT-005), the stacked-adapter certificate Q_stack (AUDIT-006R) and the trace-slack law (AUDIT-006 Check 4) from the expedition-synthesis work in continuum draft pull request 3.

Two passes wrote them. An evaluator checked each claim with code that shares nothing with the expedition's. An advocate then argued the expedition's side and narrowed or confirmed each finding. The scripts use Fractions and SymPy for exact work. One script adds NumPy for a seeded search.

| Script | What it backs | Command | Runtime | Result line |
|---|---|---|---|---|
| eval_twoloop_identities.py | The two-loop identities hold exactly on 383 fresh instances, including rank-deficient and noisy ones, with several anchors, soft absorption, error against the truth, and a wrong revision. | `python3 -I -B eval_twoloop_identities.py` | 1 s | `RESULT: PASS eval_twoloop_identities: 383 core instances (127 rank-deficient, 200 noisy), 150 multi-anchor, 183 soft-absorption, noisy-truth identity and ensemble checks held` |
| advocate_twoloop_rls_falsifier6.py | Identity 1 equals textbook restricted least squares. Ties at x = 0 and x = 2. A partial or wrong revision does not settle Claim 9. Falsifier 6 is miscalibrated in the model. | `python3 -I -B advocate_twoloop_rls_falsifier6.py` | 1 s | `RESULT: PASS advocate_twoloop_rls_falsifier6: 142 instances match textbook restricted least squares, ties at x=0 and x=2, partial and wrong revisions behave as stated, outside gap unchanged in all 178 Falsifier 6 instances (174 of them show same-kind anchors improving)` |
| eval_stack_certificate.py | Q_stack is PSD exactly when sigma_max^2 <= s on 324 probes. Integer-only certificate with refused tampering. Gain table. | `python3 -I -B eval_stack_certificate.py` | 2 s | `RESULT: PASS eval_stack_certificate: Q_stack PSD iff sigma_max^2 <= s on 324 probes (exact), integer checker agrees, 7 must-fail controls refused, gain table and N=4 demo held` |
| advocate_stack_certificate.py | Q_stack is the existing section 5.1 test on stacked factors, and the worked example inertias. | `python3 -I -B advocate_stack_certificate.py` | 1 s | `RESULT: PASS advocate_stack_certificate: B_stack A_stack = sum B_k A_k and PSD equivalence agree on 240 probes, worked example inertias match` |
| advocate_trace_slack.py | The trace-slack law is a sufficient condition, not an exact one. Worst-case crossing is 4.8 percent above the law. | `python3 -I -B advocate_trace_slack.py` | 2 s | `RESULT: PASS advocate_trace_slack: law 5 tau = 1/360 is sufficient on every case; worst exact crossing 0.0029113 is 4.8 percent above it, exact R at the law is 32761/32019 > 1` |
| advocate_trace_law_general.py | The law stays sufficient for n = 3, 4, 5, 8 and 20 (symbolic sign check). | `python3 -I -B advocate_trace_law_general.py` | 1 s | `RESULT: PASS advocate_trace_law_general: F at the law has all-positive coefficients over a positive denominator for n in 3, 4, 5, 8, 20` |

Each script printed identical output under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`, and exits 0 only if every check held. Seeds are fixed and printed. No script reads a clone or the network, so no repository path is needed.

## Target repos and commits

- Foundation-0/continuum, draft pull request 3, folder expedition-synthesis/, head commit 12a1686516d768f62ded8cfbdb174093c383295b. The claims checked come from two_loop_omitted_variable.py and optimal_inertia_rank.py at that commit.
- The scripts do not import or run that code. They re-derive each claim from its stated setting.
- The Q_stack example limits come from siliconcordat/warp issue 15, as stated in the expedition's audit.

## Not covered

- The expedition's own verifiers are not rerun here.
- The noisy and per-anchor forms of Claim 9 stay open, and the scripts only show counterexamples to stronger readings.
- Exact-arithmetic checks cover the sampled instances, not all inputs. The trace-slack search covers six noise families and 4000 random draws.
- The warp integer certificate is checked on random cases here, not inside warp's own loader.
- The prior-art readings behind the labels (restricted least squares, Lemma 3.2 and similar) were done by reading papers and are not scripts.
