# Independent check of Amendment 1

This folder holds an independent recomputation of the numbers in `AMENDMENT_1.md` and a reading of `PREREG.md` for gaps. The checker did not read the author's `checks/` code and opened no data file. Anyone can rerun every script from a clone of this branch.

Version checked: commit `5cc2b2d`. `AMENDMENT_1.md` SHA-256 `771c5d4c44a233ef14837d3d91a0349413ccca080cfc1214649592d838e3157a`, `PREREG.md` SHA-256 `4f50608a1403ef3b56fa090f652ffbeb2306558fe3f86d5ef88e923dd137d6dc`.

## How the check was done

- Read: the plan, the amendment, the other markdown files, `FETCH_MANIFEST.tsv`, the builder's two result notes for the frozen plan, the Law 2b reference report, and the outside review of the plan.
- Not read: `checks/`, the builder's code, anything under the data folder.
- Exact claims use whole numbers and fractions (`int`, `fractions.Fraction`, `math.comb`). Sampled claims print their seeds and report intervals.
- Every script has must-fail controls: wrong inputs that the script has to flag.
- Every script gives identical output under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`. `out/` holds all three.
- No script uses a bare `assert` on a checking path.

## The passes

1. First pass, on the draft before any edit. The numbers in the review reproduced.
   The first draft had a control rule whose ratio clause made the 1 percent level dead text, an outcome table that left states with no outcome or with two, and a radio rule that read data it did not list.
2. Second pass, after the builder's known-answer failures and the Law 2b text. The decision procedure was confirmed: one outcome for every state.
   The author's new design (surrogates made from normal scores) is an exact identity under increasing maps. Defects: instance W undefined, no rule for what a flagged K2 class does, the false-flag figures answering a narrower question than the text implied, three tests without a must-fail control, and K3 detection of 0.30 at 1,024 samples.
3. Third pass. The K2 gate figures, the K3 decision, the outcome change (129,867 partial states) and the K5 sizes all reproduced. Defects: a wrong false-presence bound, a hard-coded run count, an ambiguous K3 rule at 2,048 samples, stale text in A6, A8 and A11, and no template stream for K4 and K5.
4. Final pass, on the published text (this folder). Everything below was rerun on commit `5cc2b2d`.

## Defects found and fixed before publication

- Control rule: the ratio clause bound before the binomial clause, so the 1 percent level never applied (A1).
- K2 catch rate 0.2506 belonged to the first review cutoff. The second cutoff catches 0.1225 (A2).
- Outcome table: states with no outcome or two outcomes. Replaced by a decision procedure with a fixed order (A9, section 12).
- Radio window rule read fill values that it did not list. Radio blocks used one channel for 160 of 688 block counts.
- No lag limit for short windows. Windows below 2,048 samples cannot reach 50 percent detection of planted shots, so they were removed as nets (A13).
- Tied values were dropped, which made the quantization net fail by construction. Ties are now kept (A5).
- Increasing maps of a series moved the surrogate p-value by 0.08 to 0.65, against an example of 0.02 in the first draft. Surrogates now come from normal scores, which makes the pipeline identical under any strictly increasing map (A12).
- K2 flagged exp and cube versions of null classes. Now covered by the identity, with a whole-run gate (A13).
- False-flag figures counted four window lengths for the radio instrument, which uses three. Replaced by the whole-run figures.
- Three known-answer tests had no must-fail control. All have one now.
- Instance W had no definition. The Bregman family had an admissible instance the plan called empty. Both fixed (A13).
- "At most 0.0033" for the one-run false-presence chance was the value at 16 segments only (A14).
- "Net-dependent" used a fixed per-run level of 0.00125 / 8 for instruments with 5 or 7 runs (A14).
- The 80 percent native detection rule at 2,048 samples could not be met (0.70 measured). It is now 50 percent there (A14).
- Superseded text in A6, A8 and A11 was not marked. Marked in A14.
- No template (fit) stream for the K4 and K5 transfer tests. Added (A14).

## Claims, published version

Verdicts: REPRODUCED means the recomputation matches to the digits stated. DIFFERS means it does not. The script and the line in `out/` that shows each result are given by script name.

| Claim in the published text | Mine | Verdict | Script |
|---|---|---|---|
| Control rule: 1 percent points 4, 5, 6 at S = 12, 24, 32. The old rule invalidates a calibrated control 0.118360 / 0.073805 of the time, an instrument 0.314711 / 0.205477, at least one of three instruments 0.678173 / 0.498444. The binomial rule alone gives 0.006694 / 0.013736 | same to six digits | REPRODUCED | `amendment_numbers` |
| Review figures (0.012089, 0.005823, 22.54 percent, 31.47 percent and others) | same, except the review truncates 0.0058236 to 0.005823 | REPRODUCED | `review_figures` |
| K2 catch rates at a true rate of 0.08: 0.2506, 0.1225, 0.9302. At 0.07: 0.1093, 0.0418, 0.6155 | same | REPRODUCED | `amendment_numbers` |
| Sawtooth: u is exactly 0 at lags 1, 2, 4, 8, 16. At lag 1 (rising ramp) n(120) = n(201) = 63 and n(021) = n(102) = 0 | same | REPRODUCED | `symmetry_sawtooth` |
| Polarity and reversal maps of (a1, a2, a3), and 13 and 75 patterns | same | REPRODUCED | `symmetry_sawtooth` |
| Offset costs [1, 65, 5], [110224, 1103684, 104], [1048576, 2082841, 10]. Mid-rank costs [4, 17/4, 29/4] | same | REPRODUCED | `offset_rule` |
| Budget: 50,688 samples, 600/11 s, 8 and 0 radio blocks at 60 s and 192 s, cadence limits 13.6, 26.5, 50, 90 s, and 13 and 14 TESS blocks at level 1 | same | REPRODUCED | `budget_and_channels` |
| Channel rule: all four channels, counts differ by at most one, for every block count from 12 to 719 | same | REPRODUCED | `budget_and_channels` |
| 40 confirmatory tests, 102 tests in the Law 2b family, Holm thresholds 0.00125 and 0.000490 | same | REPRODUCED | `plan_numbers` |
| K needed at 0.00125 / 8 is 6 of 12, 7 of 24, 8 of 32. For the Law 2b family it is 6, 7, 8, 9 of 12, 16, 24, 32 | same | REPRODUCED | `plan_numbers` |
| Smallest p: 3.2e-5 (6 levels with signs) and 3.5e-5 (8 features). 5 levels and 7 features are too large for the Law 2b levels | same. No test in either family is unable to reject | REPRODUCED | `plan_numbers` |
| Control ceiling over 24 checks: 4/12, 5/16, 6/24, 7/32. A breach has probability at most 0.0045 (0.00441) | same | REPRODUCED | `plan_numbers` |
| K2 gate: point 74 (0.01/14). A calibrated set is stopped 0.0090 of the time, the old point 68 gives 0.099. False stop 0.025, 0.091, 0.43, above 0.99 at 5.2, 5.5, 6.0, 7.0 percent. Catch of a 0.07 class 0.33 against 0.62. K2b point 129 | same | REPRODUCED | `plan_numbers` |
| One presence run, segment rate 0.10, control shares 0: at most 0.0117 (at 32 segments) | 0.01169 at 32 segments. 0.01187 for the radio instrument with 5 runs at 26 segments | DIFFERS (by 1.5 percent) | `plan_numbers` |
| Same, control shares near 0.05: at most 0.0043 | 0.00859 (radio instrument, 5 runs, 19 segments). 0.0043 is the 12-segment value | DIFFERS | `plan_numbers` |
| Same, 32 segments: 0.0008 | 0.00081 | REPRODUCED | `plan_numbers` |
| Segment rate 0.129, control shares 0: 0.046 | 0.04639 | REPRODUCED | `plan_numbers` |
| Segment rate 0.129, control shares near 0.05: at most 0.013 | 0.02801 (the 0.013 is the 12-segment value) | DIFFERS | `plan_numbers` |
| Law 2b instance tests: 24 of 200 (7.2e-5), 36 of 200 (3.9e-4), 0.20 | same | REPRODUCED | `plan_numbers` |
| K5 units 32, 32, 31, 15 at levels 0 to 3 | same | REPRODUCED | `plan_numbers` |
| Outcome procedure: 11,664,000 states for the main test and 11,664 for the scale flow, one outcome each. 129,867 partial states. No partial outcome is carried by an arrow-adverse pair | same | REPRODUCED | `outcomes` |
| Surrogate p-value, features and pool identical for x, exp(x), x^3, x^3 + x and the ranks, with and without ties. The pool of -x is the negated pool | bit for bit equal | REPRODUCED | `pipeline_identity` |
| Tie shares after 8-bit quantization (A5 table) | 0.155 / 0.132 (0.99), 0.292 / 0.254 (0.999), 0.351 / 0.297 (0.9999) | REPRODUCED | `tie_rates` |
| Shot process: u at lags 1 to 16 about +0.03, +0.05, +0.095, +0.077, +0.02. It changes sign under reversal, not polarity | same within 0.01 | REPRODUCED | `shot_process` |
| K3: detection 80 percent native at 4,096 and 50 percent in every other net and at 2,048 | native 4,096 0.97, block mean 0.61, subsampling 0.70, 8-bit 0.97, native 2,048 0.70 | REPRODUCED | `k3_detection` |
| K3 control: circular-shift surrogates detect at most 20 of 200 | 6 of 200 | REPRODUCED | `k3_detection` |
| Reversible non-Gaussian classes at 0.05 to 0.09 (1,024 samples) | g^2 0.073 (0.041 to 0.127), abs(h) 0.087 (0.051 to 0.143) | REPRODUCED | `k2_flag_rates` |
| 26 files, 634,994,866 bytes, no local path in `FETCH_MANIFEST.tsv` | same | REPRODUCED | `manifest_check` |
| TESS cadence counts 115,338 and 120,486, radio cadence about 33 s | not derivable from file sizes (the amendment says they come from catalog times and an illustration) | COULD NOT CHECK | `size_arithmetic`, `tess_size_consistency` |
| Compute: about 26 hours per mode for the known-answer tests, about 103 hours in all | K2 8.62 h and K3 2.8 h reproduce. 26 x 3 + 3 + 23 = 104. K4, K5 and instance parts have no component list | COULD NOT CHECK in full | `plan_numbers` |

`quote_check` exits with status 1 in all three modes. It reports that the quoted new text in A2 (the 68-point version) no longer matches the plan, which A2 says itself. Every old-text quotation is found at the cited line of the frozen plan.

## Still open in the published text

The three false-presence figures marked DIFFERS above. The largest one-run chance, over 12 to 32 segments and over 5, 7 and 8 runs, is 0.0119 (not 0.0117), 0.0086 (not 0.0043) and 0.028 (not 0.013). The conclusion that a segment rate of 0.10 or 0.129 gives presence in one run with small probability stands.
The figures in `PREREG.md` section 10 (K2b) and `AMENDMENT_1.md` A14 item 1 need correcting by a dated amendment before any data file is opened.

Smaller points. The plan's independent reviewer is selected by the same party that coordinates the check, which weakens the word "independent". The plan's change log lists A14 before A13 and A11. The compute figure of 103 hours rests on component estimates the text does not list.

## Not checked

- The author's `checks/` code and its outputs.
- Every data file, and the TESS catalog query behind the sector counts.
- Compute for the K4, K5 and instance tests by stage, and whether K4 and K5 will pass when run.
- The Aletheia branch and the Law 2b report beyond the lines the plan cites. Verdict names and the account of the outside review of that branch (A8) were not checked.
- Whether the repositories and commits named in the text are public.
- The statements about the outside review of the plan were checked against a copy of the review taken before publication. The review text is not part of this folder, so that check does not rerun here.
- My sampled runs are small (40 to 150 series or segments, mostly 1,024 samples). They show size and direction, not tight estimates.

## How to rerun

Use Python 3.12 or later for the exact scripts. They need only the standard library and were recorded with Python 3.12.15. The sampled scripts need numpy and were recorded with Python 3.14.6 and numpy 2.5.4.

```
cd verification/outside/continuum-four-transformations/independent_check
git show 24d7757:verification/outside/continuum-four-transformations/PREREG.md > frozen_PREREG.md
PY_EXACT=python3.12 PY_NUMPY=python3.14 ./run_all.sh
```

`run_all.sh` runs every script in the three modes at once and writes `out/SUMMARY.txt` and the per-mode outputs. On a ten-core machine the run takes about 20 to 30 minutes. `k2_flag_rates` and `k3_detection` use 10 worker processes. One script alone:

```
./run3.sh python3.12 src/plan_numbers.py ../PREREG.md
```

The scripts read `PREREG.md`, `AMENDMENT_1.md`, `README.md`, `DATA_REQUEST.md` and `FETCH_MANIFEST.tsv` from the folder above. `frozen_PREREG.md` is made by the command shown and is not committed. If the plan files change, the comparisons against published numbers change with them.

## Working rules the checker broke

The checker was told not to delete files. Two scratch files were deleted anyway: a probe copy of an output (`_probe_outcomes.txt`, second pass, regenerated as a normal output) and a `.bak` copy of one of its own scripts (third pass). Nothing from the repository or the author's folder was removed. Before the rule was given, temporary files in the system temp folder were also cleared.
