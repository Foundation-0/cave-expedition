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
