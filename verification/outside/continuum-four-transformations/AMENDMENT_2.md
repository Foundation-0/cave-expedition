# Amendment 2 to the pre-registration

Date: 2026-11-22. Base: branch `outside/continuum-four-transformations-prereg` at commit `f584897` (Amendment 1 at `5cc2b2d`, with the independent check added on top). Line numbers below refer to that commit.

No data file has been opened or parsed.

What was known when each item was written:

- B1 to B4 were written from the independent check of Amendment 1, before the plan's author had seen any known-answer result under the amended plan.
- B5 to B12 were written after the code built for Amendment 1 (code commit `99533df`) had run a smoke version of the known-answer tests: one twentieth of the plan's seeds, and the plan's full seed count of 10 for K4 and K5.
  Its outcomes were known to the code's author and to the party who routed the questions to the plan's author.
The plan's author ruled from the code builder's written questions (file `AMENDMENTS_NEEDED.md`, Parts D to G), without reading the smoke outputs or their summary.
- The questions themselves state some observed behaviour, and four items were prompted by it: B5 (exp(exp(z)) overflowing for the exp version of g^2 in a 5-seed probe),
  B6 (a witness run of the tied waveform on the ported code, seen by the code builder before B6 was written), B7 (constant segments reaching functions that refused them) and B9 (the K5 negative criteria met only through the populated-feature floor in the smoke run).
B11 also uses a smoke figure the builder reported (the K2 control at 4 of 10 seeds).

What the items change:

- B1 to B4 change no threshold, test, net, control, decision rule or seed, and nothing the detector code implements. B2 adds three procedural conditions on the independent reviewer of the advocate step. The other three correct stated figures, reorder a list and replace the compute estimate by a component table.
- B5, B6, B9 and B11 change the definition of known-answer tests (K1, K2's control, K4's control and K5). They do not change what is computed on real data, but they decide whether the gate before data can open.
- B7 (constant segments invalid), B8 (exact comparisons and one tie tolerance) and B10 (the builder's readings D1 to D18 made plan text) fix how real-data statistics, segment counts and ties are computed. Each can affect a real-data outcome, in the rare cases that reach it. All were fixed before any data file was opened.
- B12 updates the compute estimate.

`AMENDMENT_1.md` is left as published. Where its A14 item 1 and item 6 give the figures corrected here, this amendment supersedes them.

## B1. False-presence figures for the reversible K2 classes

Found by: the independent check.

Old text, `PREREG.md` lines 286 and 287 (and the same figures in `AMENDMENT_1.md` line 500, A14 item 1):

```text
  A rate up to 0.10 does not stop it. A series whose segment rate is 0.10 passes one presence run with probability at most 0.0117 if every control share in that run were 0 (the largest value, at S = 32, where the binomial level needs K >= 8), and at most 0.0043 if the control shares are near 0.05, so that the 1/4 margin needs a share of 0.30 (0.0008 at S = 32).
  At the stopping line, a rate of 0.129, these are 0.046 and 0.013 (exact, `checks/check_binomial.py`).
```

New text (section 10, K2b): the chance is computed exactly as a maximum over every segment count S from 12 to 32 and every run count in use (8 runs for GW, SEIS and Wind/WAVES at N = 4,096, 7 for TESS, 5 for Wind/WAVES at N = 2,048), at the smallest Holm step, with each figure rounded up:

| Segment rate | Control shares | Old figure | New figure (rounded up) | Exact maximum | Attained at |
|---|---|---|---|---|---|
| 0.10 | 0 | 0.0117 | 0.012 | 0.011869 | 5 runs, S = 26 |
| 0.10 | 0.05 | 0.0043 | 0.0086 | 0.008593 | 5 runs, S = 19 |
| 0.10, at S = 32 | 0.05 | 0.0008 | 0.00081 | 0.000809 | every run count |
| 0.129 | 0 | 0.046 | 0.047 | 0.046395 | 5 runs, S = 32 (7 and 8 runs tie) |
| 0.129 | 0.05 | 0.013 | 0.029 | 0.028009 | 5 runs, S = 19 |

The new text also says that the maximum is attained by the 5-run instrument (Wind/WAVES at N = 2,048), that a test judged at a later Holm step faces a larger per-run level and so larger chances
(at the largest step, 0.05 divided by the runs: at most 0.069 and 0.035 at r = 0.10, and 0.142 and 0.076 at r = 0.129, falling at S = 16, K >= 4, for 5 or 7 runs with control shares 0, and at S = 13, K >= 4, for every run count with control shares 0.05), and that these figures bound one run only.
The conclusion is restated to match: a reversible class just below the stopping line could pass a whole presence test with a chance of a few percent at most at the smallest Holm step, and more at later steps. "Supported" also needs all three counting instruments present and the transfers to pass.

Reason. The published figures for control shares near 0.05 were the values at S = 12, not the maxima. The figure for rate 0.10 with control shares 0 was the maximum over 8 runs only, and the 5-run instrument gives slightly more. The earlier text also did not say that the figures hold at the smallest Holm step only.

Check. `checks/amendment_2/recompute_k2b.py` computes every figure in exact rational arithmetic, confirms the four maxima by a second route that shares no helper with the first (direct sums), and has a must-fail control (an off-by-one threshold gives a strictly larger value). It gives identical output under `python3 -I -B`, `-I -O -B` and `-I -B -W error`.
Every one of the five figures agrees with the independent check's own recomputation (0.01187, 0.00859, 0.00081, 0.04639, 0.02801) to the digits it gives.

Effect: none on any outcome or rule. The figures describe the K2b stopping line, which is unchanged.

## B2. The independent reviewer in the advocate step

Found by: the independent check.

Old text, `PREREG.md` line 480 (section 12b, Gate 10 row), the part changed:

```text
If they do not respond within seven days, an independent reviewer with no part in the analysis takes the role. "Respond" means a written reply on the pull request. The independent reviewer is selected by the session coordinating this check, and the selection and its reason are recorded.
```

New text:

```text
If they do not respond within seven days, an independent reviewer takes the role. "Respond" means a written reply on the pull request. The independent reviewer is someone who took no part in writing or checking this plan, its code or its results, and who shares no code with either. The reviewer is named in the results pull request before being shown the outcome. If a conflict of interest is recorded in the results pull request, the repository owners may name a replacement who meets the same conditions, before the outcome is shown to that person.
```

Reason. Selection by a working session is internal wording and weakens "independent". The reviewer is now defined by properties that anyone can check. The order is unchanged: the essay's authors first, through the pull request, then after seven days the independent reviewer.

Effect: this is not only a rewording. It adds three procedural conditions on the reviewer: the reviewer shares no code with the plan or its checking, is named in the results pull request before being shown the outcome, and can be replaced only after a conflict of interest is recorded, by someone who meets the same conditions and before the outcome is shown to them.
No outcome rule, threshold or test changes.

## B3. Order of the change log

Found by: the independent check.

Old text, `PREREG.md` lines 18 to 21: the entries A12, A14, A13, A11, in that order. New text: A11, A12, A13, A14, followed by the entries of this amendment (B1 to B4). Reason: the list was out of order. Effect: none.

## B4. Compute estimate with its components

Found by: the independent check, which got 104 processor-hours from the rounded figures and could not recompute the K4 and K5 stream doubling because the text gave no component list.

Old text, `PREREG.md` lines 335 and 336:

```text
Compute (estimate, `checks/check_compute.py`, at the builder's measured cost of about 2.3 processor-seconds per 4,096-sample pool): the amended known-answer tests about 26 processor-hours per Python mode, the fit stage about 1, the confirmatory verdict run about 8. With all three modes that is about 103 processor-hours.
The Law 2b search adds up to about 68 per mode (about 203 for three) in the worst case, where all three kinds of adverse outcome occur and every instance passes, and nothing when no adverse outcome occurs.
```

New text (section 11): a table of components per Python mode in processor-seconds. Each row says whether its count is stated in the plan (with its section), measured by the builder, or assumed by the estimate.
The rows cover K2, K1, K3, K4, K5, the Law 2b instance tests (K2 and K3 on new and on saved pools, and the paired K4 and K5), the fit stage, presence, the transfers and the scale flow. Their figures after B5, B6 and B9 are given in B12.
The Law 2b worst case is listed the same way: 17,147.52 + 77,287.50 + 149,491.20 = 243,926.22 processor-seconds per mode, about 67.8 hours, about 203.3 over three modes.

Reason. The published estimate gave no components.
A first draft of this item listed components but did not say which counts came from the plan and which were assumed or measured, left out the paired K4 and K5 tests that every Law 2b instance must pass before data, costed K1 at 14 classes and one series where the plan compares x with three maps, and costed the fit stage at 8 channels where the plan has 7.
The table now marks each count, adds the missing rows, and gives a total that is the exact sum of its rows. A reader can recompute every row from the plan, the builder's measured costs and the assumptions named in the table. The K1 count, left open in a draft of this item because the plan did not fix how many class versions K1 covers, is settled by B5.

Check. `checks/amendment_2/compute_components.py`, exact rational arithmetic, identical output in the three modes.

Effect: none on any outcome or rule. No design choice was changed.

## B5. K1 scope: which class versions, and which maps

Found by: the code builder's question F1 to F3, prompted by a 5-seed probe in which exp(exp(z)) overflowed for the exp version of g^2 at both lengths (with ties created in most seeds) and the cube version of g^2 overflowed in 2 of 5 seeds at 4,096 samples. The builder had implemented 21 class versions.

Old text, `PREREG.md` lines 273 and 274 (section 10, K1):

```text
  - With the same seeds, the normal scores, the surrogate pool, every standardised feature and the segment p-value are identical for x, x^3 + x, exp(x) and the ranks of x. Each map is first checked to leave the number of distinct values unchanged. If a map merges values, that case is reported and excluded from the identity, and the guard itself is tested on exp of values spaced 1e-17 apart.
  This is checked exactly for every K2 class (plain, exp and cube versions, 20 seeds each), which is why the exp and cube versions need no separate statistical run in K2.
```

New text (section 10, K1): the comparison maps are y^3 + y, exp(y) and the ranks of x, with y = x / max|x|, so every argument lies in [-1, 1] and no map can overflow. The first K1 bullet (pattern counts under the maps) names the same maps. K1 covers all 9 K2 classes in three versions each (27 versions), 20 seeds, the whole pipeline at 1,024 samples and the normal scores at 4,096 and 2,048.
Per class and seed 13 series go through the pipeline.
A representability guard is stated in advance: a (class version, map, seed) case counts only if the mapped series is finite and keeps its number of distinct values, a failing case is recorded as "map not representable" and never as a pass, and each class version and map needs at least 18 of 20 representable seeds or K1 fails.

Reason. The widest coverage that is well defined is all 27 versions. The overflow came from applying exp to a series that was already exponentiated, a property of the maps and not of the classes, so the maps are rescaled rather than the coverage narrowed. The guard and the minimum coverage are fixed now, not by which cases pass.
Exp and cube versions of the two reversible classes are defined here as exp and cube of the standardised series, for K1 only. K2's statistical runs are unchanged.

Effect: changes the K1 test (wider coverage, rescaled maps, a stated minimum). It does not change any real-data statistic: presence and the arrow and profile transfers depend only on order, which none of the maps changes. Code change needed: yes.

## B6. Tied inputs in K1

Found by: the code builder's item C1, from an outside review of the frozen-plan code. A ranking that breaks ties in time order turns a time-symmetric tied waveform into an apparent time arrow, and K1 used only tie-free series.
A witness run of the review's waveform on the ported code (which uses mid-ranks) had already been seen by the code builder before this item was written: Sigma_hat exactly 0, raw and under the three maps, with 3,070 tied windows kept.

Old text: `PREREG.md` lines 273 and 277 (section 10, K1) name no tied input. Line 277:

```text
  - Must-fail controls, each to be flagged: a counter that drops the last window, a counter that orders tied values by position instead of keeping tied patterns, and a surrogate step that uses the raw values instead of the normal scores (the identity must then fail under exp).
```

New text (section 10, K1): two tied inputs. (a) The waveform [0, 0, 1, 2, 2, 1, 0, 0] repeated 512 times (4,096 samples): at every lag used, each pattern count, tied patterns included, must equal the count of its reversed pattern, so Sigma_hat and the features a1, a2 and a3 are exactly 0, and every pattern count must be identical under the three maps.
(b) Each of the 7 null classes at 1,024 samples made integer-valued as round(8 z), 20 seeds: the whole pipeline identity must hold, with mid-ranks giving tied values equal scores. A fourth must-fail control is added: a ranking that breaks ties in time order must give a non-zero Sigma_hat on the waveform.

Reason. Real integer counts (the seismometer's) contain ties, so K1 must show that ties cannot create an arrow. The requirement is exact.

Effect: changes the K1 test. No real-data statistic changes, since the code already uses mid-ranks. Code change needed: yes (the test and the control).

## B7. Constant segments

Found by: the code builder's item C2, from a reproducer in which a block of equal values was cut as a segment and reached functions that refused it.

Old text, `PREREG.md` line 216 (section 7):

```text
An invalid selected block counts as a non-rejecting segment. It is not dropped from the denominator. If more than 25 percent of selected blocks are invalid, the instrument is underpowered for that net.
```

New text (section 7, before that sentence): a segment whose values, after its offset and its net are applied, are all equal is invalid. Like any invalid block it counts as a non-rejecting segment and stays in the denominator S. It gives no tau0, no template contribution, no transfer feature and no flow unit. Its C2 and C3 series, made from it, are invalid and non-rejecting.
Its C4 series does not depend on it and is computed as usual.

Reason. A constant segment carries no order, so it cannot be scored. Treating it as invalid uses the plan's existing accounting: it stays in S as a non-rejecting segment (it could not reject anyway, since every lag has zero spread), and it counts toward the 25 percent limit on invalid blocks.
Its controls are treated exactly as the code treated them before (C2 and C3 of a constant segment are constant and so do not reject, C4 is independent of it), so the control shares, the margin and the ceiling are unchanged. Refusing the whole stream was rejected because one flat stretch would end an instrument.
Keeping the segment with an invented statistic was rejected because it would score something that carries no order.

Effect on S and the controls: S is unchanged, K cannot rise, control shares are unchanged, and the invalid count can rise, which can only make an instrument underpowered. So it cannot raise the chance of a "present" outcome. It can affect a real-data outcome by making an instrument underpowered or by removing a segment from the transfers and the flow.
Direction on outcomes, from the independent check's enumeration: an instrument that would otherwise be "absent" can become "underpowered". That moves outcomes out of "evidence against", mostly to "inconclusive" and in a few states to "does not discriminate" or "partial". It never produces "supported" or "net-dependent".
This is the plan's existing rule for underpowered instruments reached by a new route, and it takes 9 or more constant segments of 32 (more than 25 percent). Code change needed: yes.

## B8. Zero-spread transfer entries, exact comparisons and the tie tolerance

Found by: the code builder's item C3 and reading D4.

Old text, `PREREG.md` line 102 (section 4.3), the part changed:

```text
Values within 1e-12 relative of each other count as ties against the real series.
```

New text (section 4.3 and section 11a, D3 and D4): every quantity that can be computed exactly is compared exactly: pattern counts and ranks as integers or mid-ranks, and binomial tails, levels and thresholds as rationals.
Floating values (Sigma_hat, standardised values, T, the transfer scores S_B and the K5 unit sums) count as tied when |a - b| <= 1e-12 x max(1, |a|, |b|), which is the plan's relative tolerance with an absolute floor near zero.
A tie never creates a verdict in either direction: it counts against the real series in the segment p-value, against w_A in the transfer p-value, against departure for a K5 unit, and not as "below" when deciding an adverse transfer.
The other comparisons the plan makes are exact, with no tolerance: tau0's "autocorrelation below 1/2" (integers: n times the doubled mid-ranks minus their sum), the Wind/WAVES interval checks "within 10 percent" and "twice the median" (exact rationals from the stored time values), and the event-rich test "exceeds the median" (quantiles as order statistics, compared as exact rationals).
A zero-spread transfer feature entry is set to 0, as the code does, and a segment with zero spread at every lag gives no transfer feature (it already counts as not rejecting).

Reason. Exact quantities should not depend on a tolerance. Where floats are unavoidable, one stated tolerance with an absolute floor removes the edge case where two values near zero differ only by rounding. Because a tie counts against whichever verdict it would otherwise help, no tie can produce a finding in either direction.
A feature entry of 0 is the neutral value when no departure can be measured, and a segment with no measurable lag carries no transfer information.

Effect: can change a p-value or an adverse decision in rare cases, and only away from a verdict. Can change a transfer score by removing segments that carry no information. Code change needed: yes (the absolute floor, the exact comparisons where not already exact, and the exclusion of all-zero-spread segments from the transfers).

## B9. K5 negative transfer criteria

Found by: the code builder's item E1, from a smoke run at the plan's full seed count for K5 (10 seeds). The cascade's tau0 is 16 (level shift 4), while the shuffled cascade and y_t have tau0 = 1 (shift 0), so they share no aligned level with the cascade and both "p above 0.05" criteria were met only through the populated-feature floor, in 20 of 20 seed-transfers.
A criterion that cannot fail tests nothing.

Old text, `PREREG.md` line 316 (section 10, K5):

```text
  - Cascade to cascade after a monotone map (exp of the standardised series) must give flow transfer p at most 0.001. Cascade to the y_t series must give p above 0.05. Shuffled cascade to cascade must give p above 0.05.
```

New text (section 10, K5): the cascade's construction is written out (start from [1], and at each of 19 steps repeat every element twice and multiply by fresh log-normal weights exp(0.5 Z - 0.125), the code builder's construction adopted as plan text).
Two new series are meant to share the cascade's time scale: the IAAFT cascade (an IAAFT surrogate of the whole cascade series, from its normal scores, which keeps its spectrum and so, approximately, its mid-rank time scale, but removes its nonlinear structure) and y' = g^2 with g an AR(1) series of unit variance and coefficient c = 0.9859.
The negative criteria become cascade to y' (p above 0.05) and IAAFT cascade to cascade (p above 0.05), judged on the primary run. The positive criterion (cascade to its exp map, p at most 0.001) must now hold in the primary run and in both amplitude-map runs. Every transfer criterion must be evaluable, with at least 8 features populated in both series in at least 9 of 10 seeds, or K5 fails.
The shuffled cascade and y_t stay as departure cases. The redefined draws use the seed-rule tag `K5b:<case>`.

Reason. The repair keeps each negative criterion and makes it able to fail. The guarantee is the evaluability rule: a criterion with fewer than 8 jointly populated features in more than 1 of 10 seeds fails K5 instead of passing it. The choice of comparison series only makes evaluability likely.
The coefficient of y' is set by a stated rule on the mid-ranks that tau0 uses: c is the value at which the population mid-rank autocorrelation of g^2 equals 1/2 at lag 16, 12 E[(2 Phi(|X|) - 1)(2 Phi(|Y|) - 1)] - 3 with X and Y standard normal of correlation c^16, rounded down to 4 decimals.
This gives c = 0.98596 before rounding and 0.9859 after, first below 1/2 at lag 16 (`checks/amendment_2/derive_yprime.py`, a trapezoid integration, with a sampled check).
A draft of this item used c = 2^(-1/32) on the argument that the autocorrelation of g^2 is c^(2k). That holds for the values, not for the mid-ranks: the population mid-rank autocorrelation at that c is 0.368 at lag 16 and first below 1/2 at lag 11, and the sampled tau0 is 10 to 11.5 (level shift 3 in 9 of 10 seeds).
The independent check found the same (lag 11, 0.373 at lag 16). Its figure of c near 0.9852 was a rough estimate, superseded by the exact value.
In the sampled check at c = 0.9859, the median tau0 of y' is 15 to 17 in 10 of 10 seeds (shift 4). Lag 16 is the cascade's tau0 as the code builder reported it. The plan did not define the cascade, so its tau0 depended on the implementation (the independent check's own cascade gave 11 to 12).
With the construction now written out, the sampled check gives the cascade a tau0 of 9 to 18 by seed (shifts 3 and 4). The two then share at least 2 aligned levels (18 features) whenever the cascade's shift is 2 to 5, but that is a likelihood, not the guarantee. The amplitude-map runs of the positive criterion exercise code paths that no known-answer test used before (the builder's reading D10).

Effect: changes the K5 test only. Code change needed: yes (new series, new criteria, the evaluability rule, the amplitude-map runs, the new tag).

## B10. The code builder's provisional readings D1 to D18

Found by: the code builder (Part D of `AMENDMENTS_NEEDED.md`, code commit `99533df`).

Old text: none. The plan was silent or unclear at each point.

New text: section 11a lists each reading as plan text. Rulings:

| Reading | Ruling | Could it change a statistic or a decision? |
|---|---|---|
| D1 inverse normal, odd reflection | adopted: exact polarity symmetry | no, it fixes one implementation |
| D2 IAAFT stop rule | adopted: a precise reading of the plan's rule | yes, it defines the surrogates |
| D3 population divisor, exact zero spread, zero-spread entries 0 | adopted, extended by B8 (all-zero-spread segments give no transfer feature) | the divisor no, the transfer rule yes |
| D4 tie tolerance in the transfer test | replaced by B8 (exact where exact, one float tolerance with an absolute floor) | yes, rarely, and only upward |
| D5 dense-rank patterns | adopted: gives the plan's 13 and 75 patterns | yes, it defines the statistic |
| D6 order-4 class frequency, ninth class of 51 tied patterns | adopted | yes, it defines the flow features |
| D7 sorted summation | adopted: makes x and -x bit-identical | no |
| D8 counting definition of the 2.5th percentile | adopted, with ties not counted as below (B8) | yes, it defines "adverse" |
| D9 flow template as equal-weight level means | adopted: the same construction as the score, then scaled to unit length (which changes no p-value) | yes, it defines the template |
| D10 flow amplitude maps on the whole stream | adopted, and section 5's table changed to say the maps act on the whole stream. K5's positive criterion now exercises these runs (B9) | yes, it defines those runs |
| D11 window-length net blocks of N/2 + 128 | adopted | yes, it defines the segments |
| D12 controls inside a net run | adopted | yes, it defines the controls |
| D13 underpowered reported over a failed control | adopted, with both facts recorded | no: both keep the instrument out of V |
| D14 seed-rule fields | adopted and written into section 11a for every use, with new tags for B6 and B9 (K1 keeps the plain draw's key for its versions and maps) | yes: the draws determine the surrogates and so the p-values |
| D15 unit variance of g and h, standardisation, K2 control flag point at its own seed count | adopted (see B11 for the flag point) | defines the K2 series and control |
| D16 K3 draws and the sawtooth noise 0.1443 (the ramp's peak to peak range is 63/64, now stated exactly in section 10) | adopted. The smoke-size scaling of the circular-shift bound is not a plan matter | defines K3 |
| D17 K4 and K5 constructions | adopted, with one change: the K4 control counts a seed as reaching p at most 0.01 if any run does, not only if the largest p over the runs does. The builder's reading made the control harder to trip | defines K4's control (stricter) and K5 |
| D18 K1 at 1,024 samples, normal scores at 4,096 and 2,048 | adopted, widened by B5 | defines K1 |

No reading was left open, and none needed an outcome to rule on.

Effect: the readings marked "yes" define real-data statistics or known-answer criteria. All are fixed before any data file is opened. Code change needed: D3 (all-zero-spread segments), D4 (B8), D14 (new tags), D17 (the K4 control). The others are already as the code has them.

## B11. Other points from the code build

Found by: the code builder (Parts E to G).

- K2 control flag point (F4, D15). Old text, `PREREG.md` line 291, says the control "must be flagged by the K2a rule" without the seed count. New text: the control runs on 200 seeds and is judged by the K2a rule at its own seed count, flagged at 22 or more of 200 (the smallest k with P(Binomial(200, 0.05) >= k) at most 0.01/14).
The builder reported the control at 4 of 10 seeds in the smoke run, one short of the 10-seed point of 5, which is why the seed count is fixed here at the plan's 200. Effect: defines the control. Code change: none beyond running it at 200.
- K4 control (D17). Old text, `PREREG.md` line 307, says "Neither the arrow transfer nor the profile transfer may reach p at most 0.01 in more than 1 of the 10 seeds". New text adds the block construction of A' and that a seed reaches p at most 0.01 if any run does. Effect: a stricter control. Code change: yes.
- Law 2b instance tests (E4). Not built yet. The requirement that each instance passes its tests before any data file is opened stands. No reason to change it was found.
- Second checker, mutation test and real-data readers (E5 and Part G). The mutation test of section 11 covers every module, not only `gates.py`. These remain conditions of the gate.

## B12. Compute table after B5, B6 and B9

Found by: this amendment, following B5, B6 and B9.

New text (section 11): K1 becomes 1,669.41 processor-seconds per mode (9 classes x 20 seeds x 13 series and 7 classes x 20 seeds x 4 integer-valued series at 1,024 samples, plus 4 pools for the tied waveform). K5 becomes 25,190.00 (10 series x 10 seeds x 110 units), and the Law 2b instances' paired K5 125,950.00 (5 instances). The known-answer total becomes 253,546.41.
One mode without an adverse outcome: 284,401.87 processor-seconds, about 79.0 processor-hours. Three modes: 853,205.61, about 237.0 processor-hours. The Law 2b worst case is unchanged (243,926.22 per mode). Parts E and F give no new timings, so the measured costs stay those of commit `71142c1`.
The K4 figure of 490 seconds per set of streams is now labelled with its source (`known_answer/out/timing.txt` at that commit, 488.6 to 489.9 processor-seconds per mode, rounded up).

Check. `checks/amendment_2/compute_components.py`, exact rational arithmetic, identical output in the three modes.

Effect: none on any outcome or rule.

## Also updated

`README.md`: the status line and file list now name Amendment 2, and a table gives the SHA-256 of `PREREG.md`, `AMENDMENT_1.md` and this file. The package README had no such table before.

## What was not changed

- `AMENDMENT_1.md` is left as published, so that its hash stays as the independent check recorded it. This amendment supersedes its A14 item 1 figures and its A14 item 6 total.
- The folder `independent_check/` is not touched.
