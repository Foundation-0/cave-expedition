# Amendments needed

`PREREG.md` is unchanged. This file lists what the code could not take from the plan as written, and what the known-answer runs showed about the plan.

Part A: the plan leaves a number or a rule open. The code uses the choice written here so that the tests can run. Each choice needs a dated amendment to the plan before real data are opened.

Part B: a part of the plan that cannot be computed as written. Nothing is implemented for it.

Part C: findings from the known-answer runs. They are results, not tuning. No threshold, detector or test was changed after a run.

## Part A: provisional choices

A1. IAAFT (section 4, "Two shared tools"). The plan names the method and fixes no rule for the iteration.

The code starts each surrogate from a random permutation of the segment. It alternates the spectrum step and the rank step. It stops when the rank order stops changing, or after 100 rounds. It ends on the rank step, so a surrogate has exactly the values of the segment.

K2 and K3 depend on this rule. For white noise 46 rounds were needed on average. For the exp and cube classes the cap of 100 was reached almost always. X3 raises the cap to 1,000 for the three worst K2 classes, and the rejection rates move by at most 0.017.

A2. Tied windows (section 5). "More than 20 percent of a segment's windows are tied" does not say at which lag. The code uses the lag with the largest tied share in the real series. No K test has ties.

A3. Lags for the shorter series of the sampling-rate nets (section 5, "lags limited to fit the shorter segment"). The code keeps lags 2^j that are at most 512 divided by the rate ratio. That gives 10 lags native, 9 for block mean by 2 and subsampling by 2, and 8 for block mean by 4.

A4. Whitening (section 5). The edges of the 33-bin running median use reflection.

A5. K2 classes. Three sinusoids have frequencies 0.0137, 0.0781 and 0.2113 cycles per sample, unit amplitude, random phases, and white noise of standard deviation 1. Power-law noise comes from Fourier synthesis with random phases. Each class is scaled to mean 0 and standard deviation 1 before the exp and cube maps.

A6. K3 series. Shots start at each sample with probability 0.01, the decay kernel is cut at 100 samples, and the height is 3 times the exact standard deviation of the AR(1) background. The logistic map starts from a random point and drops 1,000 steps.

The sawtooth has peak to peak amplitude 1 and white noise of standard deviation 0.5, one reading of "half its amplitude". With this reading the sawtooth fails every K3 criterion. With noise at half the sawtooth's standard deviation (0.144) it is detected in all 200 seeds on every net (X4). The K3 sawtooth result depends on the reading.

A7. K4 series. Instrument B is made at twice the rate (shots decaying over 10 fine samples, 1/f background), every second sample is kept, and the sign is flipped. Instrument C is the time reverse of a fresh series of kind A. Each stream has 33 blocks, so the primary grid and the grid shifted by half a block both give 32 segments.

A8. K4 and K5 scoring. The A to C criterion is required in every run (primary and shifted grid). K5 gives no number of seeds, so the scored result is the first seed of each case. Other seeds are shown and not scored.

A9. K5 cascade. A dyadic cascade with log-normal weights of mean 1 and log standard deviation 0.5.

A10. Class matching (K2). "Central decade of frequencies" is read as the decade of log frequency centred on the middle of the range from 1/N to 1/2. The match is the class with the nearest slope among all 21 classes.

A11. Order 4. Only d = 3 has an explicit formula. For d = 4 the same form is used with the 24 patterns, so the denominator is the count plus 12.

A12. Zero spread. When the other 99 series have zero spread at a lag, the standardised value is set to 0 and the segment is flagged. This did not occur in any known-answer run.

A13. tau0 (section 4.3). Ranks come from a stable sort, with ties by position. The autocorrelation is the biased estimate about the mean. The level shift is log2(tau0) rounded half up.

## Part B: not implemented

B1. Transfer of the 56 scale-flow features (sections 4.1 and 10 K5). The plan says to apply the transfer test of 4.3 to them, and that test averages an AUC over segments.

At level l the segments cover 2^l times as much time and there are about 32 / 2^l of them, so no segment owns a vector with all 56 features. Three readings exist.

1. Each (level, segment) pair is a unit. It fills the 8 slots of its own aligned level, and the other slots are 0.
2. Units are the level 0 segments. At coarser levels each takes the features of the coarse segment that covers it.
3. One vector per instrument from per-level means. The AUC is then undefined.

The two K5 transfer criteria (cascade to cascade, cascade to shots) were not run.

B2. Section 11 asks for a second checker that repeats the verdict with its own surrogates and seeds, and recounts patterns on saved surrogate files. The recount exists (`src/second_impl.py`, used in K1). The repeated verdict belongs to the real-data stage and is not built.

B3. C6, the file readers and the validity flags of section 7 need real files and are out of scope here. `cut_segments` accepts a list of validity flags from a reader.

## Part C: findings

C1. K2 fails. 11 of 21 classes are above the 0.086 bound, all of them exp or cube classes. The rates are ar1_0.5 exp 0.100 and cube 0.090, ar1_0.9 exp 0.295 and cube 0.155, ar1_0.99 exp 0.250 and cube 0.240, pl_1 exp 0.220 and cube 0.095, pl_2 exp 0.090 and cube 0.135, and sines3 exp 0.100.

White noise after exp is at 0.085, inside the bound. Every plain class is inside the bound (0.040 to 0.065). An increasing map leaves the order patterns of the series unchanged but changes what IAAFT surrogates look like. That is a likely cause and was not tested further. Raising the iteration cap does not remove the excess (A1, X3). By the plan's own rule, an instrument matched to such a class is not calibrated.

C2. K2 matching. Classes with and without a map have almost the same slope, for example ar1_0.9 at -0.81 and ar1_0.9 after exp at -0.65. A match by slope alone cannot tell them apart. In the joined K2 output, the nearest other class to plain white noise is white after cube, and to plain pl_1 it is pl_1 after exp. The plan needs a rule for this, for example matching on slope and on the skewness of the values.

C3. K2 bound. The value 0.086 is the normal approximation (0.05 plus 2.326 standard errors). The exact 99 percent binomial point is 18 of 200 (0.090). At 0.086 a perfectly calibrated class is flagged with probability 0.012. Over 21 classes the chance that at least one calibrated class is flagged is 0.225 (X1).

C4. K3 fails in four of nine cells. Shots after whitening are detected at 0.440 (need 0.50). The sawtooth is detected at 0.215 native, 0.400 after block mean by 2, and 0.185 after whitening, but this depends on the reading of the noise level (A6). Shots native (0.915), shots after block mean by 2 (0.545) and the logistic map in all nets (1.000) pass.

C5. K4 fails. A to B gives transfer p = 0.2025 (largest over the two runs), and the plan needs 0.001. A to C gives AUC 1.000 in both runs, and the criterion needs it below the 2.5th percentile of permuted templates (0.404 and 0.438). Even A to a new sample of the same kind gives p = 0.0125.

A time-reversed signal still scores 1.000 because 20 of the 30 features (m1 and m23) are magnitudes that do not know the direction of time. A strong arrow in B raises them for every template. The permuted templates then also reach AUC near 0.9, and the real AUC is capped at 1.

A diagnostic cut of the template to its 10 sign-sensitive entries separates A to C (AUC 0.19 against a 2.5th percentile of 0.27) but still gives A to B p = 0.29. The permutation null does not have the power the plan assumes.

C6. K5 fails. For independent exponential values every order pattern has the same chance at lag 1, so the level 0 norm is only noise (0.38 to 0.56 over six seeds) and cannot be halved. The top level has fewer segments and a larger noise norm (0.60 to 0.98). The scored ratio is 2.57.

The cascade criterion passes (ratio 0.70), but the shuffled cascade, which has no structure, passes it too (ratio 1.95). That criterion does not discriminate. A short-memory series after exp (ar1_0.5, ratio 0.76) is not below half either.

C7. Run time. K2 needs about 2.7 hours of processor time. The first unsplit K2 run finished in 24 minutes on a ten-core machine shared with other jobs. A second unsplit run was stopped by the 30 minute limit while the machine load average was about 150. K2 was then run in seven parts and K3 in three, with the same seeds and the same work. `known_answer/out/timing.txt` has the times.

C8. X1 passes every check except one: the K2 bound of C3. The plan's own arithmetic in sections 6 and 9 holds (excess points 4 and 6, and 5 and 7 hits to reach 0.00179).

# Amendment 1 build (code for the amended plan)

The sections above belong to the frozen plan and stay as recorded. This section covers the code rebuilt for the plan as amended by Amendment 1 (plan commit 5cc2b2d). The plan files are unchanged. Where the plan is silent or unclear, the code uses the reading named here, provisionally.

Each reading needs a dated amendment before real data are opened, or a confirmation that the reading is acceptable. Nothing was tuned: no seed, threshold or generator was changed after a result was seen.

## Part D: readings the plan leaves open (provisional choices)

D1. Inverse normal (section 4: "one implementation, recorded with the code commit"). The code uses the standard library `statistics.NormalDist(0.0, 1.0).inv_cdf` (algorithm AS 241) on the lower half of the rank table and reflects it oddly for the upper half. This makes the scores of a polarity-flipped series exactly the negated scores, bit for bit. Recorded in `src/ranks.py`.

D2. IAAFT stop rule (section 4: "the rank order is unchanged between two successive iterations"). Read as: the array produced by the rank step equals the array that entered the iteration. The random start counts as the first iterate. The cap is 1,000 iterations.

D3. Standardisation (section 4.3). The standard deviation of the other 99 series uses the population divisor. No p-value or transfer p-value depends on this choice, because it scales every value alike. Zero spread is decided exactly (all other values equal). In the transfer features a zero-spread entry is set to 0.

Only the segment statistic T leaves such a lag out, as the plan says.

D4. Ties. The tolerance of 1e-12 relative to the larger absolute value is used for the segment p-value, as the plan states. The plan gives no tolerance for the transfer test, where a random detector identical to w_A must tie with it. The code uses the same relative tolerance there.

D5. Tied patterns (section 4.3). A pattern is the tuple of dense ranks of the window (the rank of a value is the number of distinct window values below it). This gives the 13 patterns at order 3 and 75 at order 4 that the plan counts.

D6. Order-4 class frequency (section 4.1). A class frequency is the sum of the pseudocounted pattern frequencies of its members, so for a class with m patterns it is (count + m/2) / (windows + 75/2). The ninth class holds the 51 tied patterns.

D7. Sigma_hat summation. The 13 terms are summed in sorted order so that x and -x give bit-identical sums (the plan says Sigma_hat is equal for x and -x).

D8. "Below the 2.5th percentile" (sections 4.3 and 12). Defined by counting: S_B(w_A) is adverse if fewer than 1/40 of the random detectors score below it (strictly, beyond the tie tolerance). No interpolated percentile is used.

D9. Flow template (section 4.1). The plan says the template is the mean feature vector over A's fit segments, and gives the score as an equal-weight mean over levels. The code builds the template the same way as the score: the mean of the units at each aligned level, each level counting equally.

D10. Flow amplitude maps (section 5, "exp of the segment standardised to unit variance"). The flow averages amplitudes over whole streams, so the maps are applied to the whole stream before block averaging, not to a segment. The maps exist in `src/nets.py`.

K5 judges its transfer criteria on the primary run only (see D17), so the two amplitude-map runs are built but not exercised by a known-answer test.

D11. Window length net N/2 (section 5). Read as blocks of N/2 + 128 samples cut by the same rule of section 7 with segment length N/2.

D12. Controls inside a net run (section 5). C2 and C3 are made from the native segment and then put through the run's net. C4 uses the pooled fit-set values and the median fit-set periodogram at the native length, then the run's net.

D13. Status order (section 12). If an instrument is both underpowered and has a failed control, the code reports "underpowered".

D14. Reading of "two independent streams per seed" and the seed rule. The seed rule has fields master|instrument|split|net|segment|purpose|index. For synthetic data the code fills them as follows.

K1 and K2: instrument `K2:<class>:<length>` (K1 uses `K1:<class>:<length>`), split `synthetic`, net `native`, segment the seed index, purpose `data` for the series and `surrogates` for the pool.

K3: instrument `K3:<case>:<length>`, net is the use (native4096, native2048, bm2, sub2, q12, q8, placement, wlen2048), segment the seed index. K4: instrument `K4:<kind>` (or `K4:<kind>:s<seed>` for segments), split `fit` or `verdict`, segment the seed or segment number. K5: instrument `K5:<case>` (and `:s<seed>` for units).

Detectors use purposes `detectors-arrow`, `detectors-profile` and `detectors-flow`. The exp and cube versions of a K2 class share the seed of the plain class, so they are the same draw mapped.

D15. K2 series. Unit variance for g and h means a stationary AR(1) series whose innovations have standard deviation sqrt(1 - c^2) for coefficient c. The 7 null classes are standardised by their sample mean and standard deviation. For the must-fail control, the flag point is the K2a rule (smallest k with tail at most 0.01/14) evaluated at the control's own number of seeds.

D16. K3 on synthetic data. Each seed draws a block of N + 128 samples and cuts it by the offset rule.

The window placement net and the window length net are independent draws of the same process (the processes are stationary, with a random phase for the sawtooth), cut by the same rule. "Native at 2,048 samples" is its own independent draw. The sawtooth noise at half its standard deviation is 0.1443 (the ramp k/64, k = 0 to 63).

The circular-shift control bound of 20 of 200 is scaled to the same fraction (10 percent) at smoke size.

D17. K4 and K5 constructions. K4: A' is built from blocks (the stream cut into its 33 blocks, block order shuffled, each block replaced by an IAAFT surrogate of itself) so that both grids exist. Its tau0 comes from its own fit stream built the same way. "Reaches p at most 0.01" means the largest p over the two runs.

The runs are the primary grid and the shifted grid (no second channel). The sawtooth blind-spot streams are fresh draws, primary run only. K5: the transfer criteria are judged on the primary run only, because every extra run needs a further 110 pools per series and the plan does not say which runs K5 uses.

A unit departs if at most 4 of its 99 surrogates have a sum of squared features at or above its own (p at most 0.05). The cascade's highest populated level is level 3.

D18. K1 sizes. The full pipeline identity (pool, features, p-value) runs on segments of 1,024 samples for every seed, for the plain class, the exp and cube versions, the three maps and the polarity flip, for the 7 null classes.

At the K2 lengths (4,096 and 2,048) the code checks the normal scores of every exp and cube version exactly. The pool is a deterministic function of those scores and the seed. The plan asks for 20 seeds per class, and the full size uses 20.

## Part E: points where the plan cannot be implemented as written, or may not do what it intends

E1. Flow alignment and the populated-feature floor (sections 4.1 and 10 K5). The level shift is round(log2 tau0) and only aligned levels -3 to +3 are kept. A series with a long memory has a large tau0.

In the K5 smoke run the cascade's tau0 is 16 (shift 4) in every seed, so its flow levels 0 to 3 land at aligned levels -4 to -1 and only 3 levels (27 features) are kept. The shuffled cascade and the y series have tau0 = 1 (shift 0), so their levels land at 0 to 3.

These share no level with the cascade, so every transfer between them has no jointly populated feature.

Where fewer than 8 features are populated in both A and B, the transfer "counts as not rejecting". Two K5 criteria ask for p above 0.05 (cascade to y, shuffled cascade to cascade). In the smoke run all 20 of these 20 seed-transfers passed only through that floor, so those two criteria do not test anything as the plan is written. The K5 output reports the count.

E2. Seeds for K1 under the plan's own count. K1 asks for 20 seeds per class for all 21 class versions with full pipeline equality. At 4,096 samples that is 1,680 pools per mode, more than K1's description suggests. The code keeps the identity exact and moves its pipeline part to 1,024 samples (D18).

E3. Smoke size for K4 and K5. The smoke rule (one twentieth of the plan's seeds, at least 10) gives 10 seeds for K4 and K5, which is the plan's own number. Their smoke runs are therefore full-size in seeds. They are still labelled SMOKE and are not results.

E4. Instance tests of section 12a. The section asks that each Law 2b instance passes K2 (200 seeds per class), K3 native and its paired K4 or K5 test before data are opened. The instances exist as functions (`src/law2b.py`) and have unit checks, but these instance tests are not built.

E5. Second checker, mutation test (section 11) and the real-data readers are not built. The second implementation of the pattern count exists (`src/second_impl.py`).

## Part F: answers to the designer's questions on K1 (asked after the first smoke run)

F1. Reading of "for every K2 class (plain, exp and cube versions, 20 seeds each)" (section 10, K1). The code implements 21 class versions: the 7 null classes, each in three versions (plain, exp, cube). The 2 reversible classes (g^2 and |h|) have no exp or cube version in K2 and are not in the K1 identity.

Not implemented: the 23-version reading (adding the two reversible classes plain) and the 27-version reading (all 9 classes in three versions).

F2. Series compared per seed. For each of the 7 null classes and each seed the full pipeline runs on 7 series: x, x^3 + x, exp(x), the ranks of x, -x, and the exp and cube versions of the class. Six are compared with x. The plan names the first four.

The last three are added: -x for the polarity identity of the pool, and the exp and cube versions because K2 relies on them. That is 49 pipeline runs per seed over the 7 classes. At the K2 lengths (4,096 and 2,048) only the normal scores of the exp and cube versions are compared (exactly), not the whole pipeline.

F3. Would the 27-version reading run cleanly? A quick run on 5 seeds at 4,096 and at 2,048 samples applied x^3 + x, exp(x) and the ranks to all 27 versions. All 21 versions of the 7 null classes were clean: no non-finite value and no tie created. The reversible class |h| was also clean in all three versions.

The versions of g^2 were not. Here the exp and cube versions of g^2 were taken as exp and cube of the standardised series. exp(exp(z)) overflowed to infinity in all 5 seeds for g^2 exp at both lengths, and in 2 of 5 seeds for g^2 cube at 4,096 samples.

Where it overflowed, the infinite values are tied, which creates ties that were not in the input, in 4 of 5 seeds at 4,096 and 5 of 5 at 2,048 for g^2 exp. The distinct-value guard flags these cases, and the plan says such cases are reported and excluded.

So the 27-version reading runs, but it would exclude most seeds of g^2 exp and some of g^2 cube. It never creates ties or non-finite values for the 7 null classes or for |h|.

F4. K2 must-fail control at smoke size. The plan's rule is the K2a flag point, the smallest k with P(Binomial(n, 0.05) >= k) at most 0.01/14. At the plan's full size of 1,000 seeds it is 74 (7.4 percent). The control itself is specified at 200 seeds (the frozen plan measured 59 of 200).

The code applies the same rule at the control's own number of seeds: at 200 seeds the flag point is 22 of 200 (11 percent), and at the smoke size of 10 seeds it is 5 of 10 (P(Binomial(10, 0.05) >= 4) = 0.00103 is above 0.01/14 = 0.00071, and P(>= 5) = 0.000064 is below).

The smoke control rejected 4 of 10 (rate 0.40, higher than the frozen 59 of 200 = 0.295), one short of the smoke flag point. The same rate at full size (80 of 200) is far above the full-size flag point of 22 and would be flagged. The smoke flag point is coarse at 10 seeds and the control is recorded as NOT FLAGGED at that size.
## Part G: an outside executable review of the frozen-plan code (eight findings)

An outside reviewer ran eight witnesses against the frozen-plan code (CAVE8-01 to CAVE8-08). Each was run again against the code for the amended plan (`known_answer/review_witnesses.py`, output before and after the fixes in `known_answer/out_review/`). Class A means the amended code does not have the defect.

Class B means a code defect that no plan text governs, fixed now with a check that fails when the guard is removed. Class C means a fix could change a statistic, a threshold, a rejection rule, what counts as a valid segment or the definition of a known-answer test.

Class C items are not changed and are listed below for the plan's designer.

| Finding | Class | Witness on the amended code | Action |
|---|---|---|---|
| 01 exit status and `disabled=` switch | A and B | Scripts exit 1 on FAIL (K2 and K3 smoke runs exit 1). The `disabled=` switch was still in `validate_series` | Switch removed. `summary` in `kcommon.py` ends the script with exit 1 on FAIL. K6 now deletes each refusal from a copy of the source (7 deletions, 6 codes) and requires the suite to fail. Exit codes are recorded in `status.txt` files |
| 02 ties and ranks | A and B | Tied waveform: sigma_hat exactly 0.0 raw and under x^3+x, exp and the ranks, 3,070 tied windows kept, counts equal. tau0 of the tied waveform is 2. tau0 of a constant series was a ZeroDivisionError | Mid-ranks were already used. tau0 now refuses a constant segment and a segment of one sample with a ValueError. Adding the waveform to K1 is class C (C1) |
| 03 float and bool p-values | B | `holm` with the float 0.05 gave the wrong answer, and bool was accepted | Every exact quantity in `levels.py` refuses float and bool with a TypeError |
| 04 dtypes | B | bool and string arrays were converted, and complex arrays were truncated | Only integer and float dtypes pass, checked before conversion. N must be an int |
| 05 cutter | A, B and C | Wrong-length `valid` raises ValueError (short and long). Offsets on the review's block are 0 under every map (mid-ranks). A constant block is cut and analysed without a crash. `tau0_segment` and `amp_exp_standardised` crashed or warned on it | The two functions now refuse a constant segment with a ValueError. The segment rule itself is unchanged. Constant segments are class C (C2) |
| 06 ties, degenerate, tolerance | A and C | No tie-share rule exists. A segment with zero spread at every lag is "not rejecting" by the plan. Features of flagged segments enter the transfer | Nothing changed. See C3 |
| 07 divisions and logarithms | A and B | No warning under `-W error` on all-zero counts or identical rows. One row to `loo_standardise` was an IndexError | `loo_standardise` refuses fewer than 2 rows, non-finite values and non-2-D input |
| 08 transfer comparisons | A and B | Scores are compared with a relative tolerance, not by exact equality. R = 0, mismatched lengths, a non-finite template and an unknown kind were not refused | Explicit refusals added to `transfer_test` and `build_template` |

Class C list for the plan's designer.

C1. K1 and a tied symmetric waveform. K1 only used tie-free series in its increasing-map checks. The review's waveform `[0,0,1,2,2,1,0,0]` repeated 512 times is exactly time-symmetric. The amended code gives sigma_hat exactly 0 on it and keeps all 3,070 tied windows under x^3+x, exp and the ranks (unit checks, not K1).

Option: add tied series to K1's map checks. This does not change a statistic. It changes what K1 tests.

C2. Constant segments (also the second review's items 4 and 5). Reproducer: a stream of 4,224 samples of a ramp followed by 4,224 samples of the value 7.0. `cut_segments` cuts the second block as a segment (it checks only the whole stream).

The presence test then analyses it without a crash: every lag has zero spread, so it counts as not rejecting and stays in S. `transfer.tau0_segment` and `nets.amp_exp_standardised` refuse a constant segment with a ValueError (they crashed or warned before).

A pipeline run that reaches either function with a constant fit or flow segment therefore stops with an explicit error.

The plan's validity rule (section 7) does not mention constancy, so what a constant segment does to the segment count is a plan question.

Options: (a) refuse the stream, (b) mark the segment invalid, so it counts as not rejecting, and drop it from the usable count (more than 25 percent of such blocks makes the instrument underpowered, and the instrument still needs 12 valid segments), (c) keep it with a defined statistic (for example a fixed tau0 and fixed features).

The code applies none of these rules. No smoke number changed.

C3. Zero-spread lags and transfer features. The plan says a lag with zero spread is left out of the maximum for that series and the segment is flagged, and a segment with every lag at zero spread does not reject. The plan does not say what happens to such a segment in the transfer features.

The code sets zero-spread feature entries to 0 and keeps the segment in the template and the score. Options: exclude flagged segments from the transfer, or keep them (as now). Related: the tie tolerance of 1e-12 relative to the larger absolute value is the plan's, and is also used for detector ties (D4).

When both values are 0 it is an exact comparison. An absolute floor is a possible addition. Either choice can change a p-value in rare cases.

Not done for the other modules: the plan's mutation test (section 11) is built only for the refusals in `gates.py`. Mutation of comparisons and thresholds in the other modules is not built.
