# Pre-registration: a raw-data test of the four-transformations claim

Status: plan as amended by Amendments 1 and 2. Files fetched and hash-pinned (`FETCH_MANIFEST.tsv`), none opened, no statistic computed on real data.
Claim type: sampled. Novelty: N0 (the statistics used here are known methods).

Change log. The plan was fixed at commit `24d7757309b5b6b7b5179be2a65387af58fd5f9b`. Amendment 1 (`AMENDMENT_1.md`) was made after the files were downloaded and before any file was opened. It changes:

- A1 control rule (section 6).
- A2 calibration cutoff and draws (K2).
- A3 split of the irreversibility transfer test into an arrow test and a profile test, with a sign-aware null (sections 4.3, 9, 10, 12, 13).
- A4 rank-based segment offsets, and amplitude maps as statistical nets (sections 5, 7, 10).
- A5 quantization bins and tied patterns (sections 4.3, 5).
- A6 Wind/WAVES window rule, window-length net and gaps (sections 4.1, 5, 7, 8).
- A7 template permutations restricted to populated features (section 4.3).
- A8 listed transformations before an adverse outcome is final (new section 12a).
- A9 outcome table replaced by a decision procedure with a fixed precedence (section 12).
- A10 choices that were still open closed: lag rule, rank maps, binning of tied values, ties in the flow features, IAAFT stopping rule, K2 class matching, Wind/WAVES validity and channel rule (sections 4, 4.1, 4.3, 5, 7, 8, 10).
- A11 requirements of Aletheia version 2.0.0 (a branch under review): Bonferroni split of each test's level across its net runs, IID and spectrum-preserving nulls with a fixed signal margin and a control ceiling in every net run, advocate review of adverse outcomes, gate-integrity checks for the analysis code (sections 4.3, 5, 6, 9, 11, 12, new section 12b).
- A12 changes after the known-answer tests failed on the frozen plan (builder commit `71142c1`): normal scores before surrogates, whitening out of the confirmatory nets, a non-saturating transfer score, new K2, K3, K4 and K5 tests, the scale-flow transfer defined, the builder's 13 open choices closed, a gate before data, and a compute estimate (sections 4, 4.1, 4.3, 5, 6, 9, 10, 11, 12, 12a, 13).
- A13 changes after the second clean-room check: K2 gate rule, must-fail controls for every known-answer test, window lengths below 2,048 out of the confirmatory nets, a Bregman instance for Law 2b, instance W defined, the advocate, mutation testing and prior-art requirements defined, and the outcome procedure tightened (sections 4, 5, 6, 8, 9, 10, 11, 12, 12a, 12b, 13).
- A14 corrections after the third clean-room check: the false-presence bound, the per-run level in "net-dependent", K3 at 2,048 samples, the template and verdict streams of K4 and K5, the advocate's details and the mutation-test units (sections 10, 11, 12, 12a, 12b).

Amendment 2 (`AMENDMENT_2.md`, 2026-11-22) was made before any data file was opened or parsed, and before any known-answer result under the amended plan had been seen. Items B1 to B4 change no threshold, test, net, control, decision rule or seed, and nothing the detector code implements, and B2 adds three procedural conditions on the independent reviewer.
Items B5 to B12 change the definition of known-answer tests K1, K4 and K5, add a validity rule for constant segments, fix the tie tolerance, and turn the code builder's provisional readings into plan text. B7, B8 and B10 can change what is computed on real data. Changes:

- B1 the false-presence figures for the reversible K2 classes, now exact maxima over a stated domain (section 10).
- B2 the independent reviewer of the advocate step, now defined by properties, with three procedural conditions added (section 12b).
- B3 the order of this change log (A11 before A12, A13 and A14).
- B4 the compute estimate, now a component table whose total is the exact sum of its rows, each row marked as a plan count, a measured cost or an assumption (section 11).
- B5 K1 covers all 27 class versions, with comparison maps that are representable on every class, a representability guard and a minimum coverage (section 10).
- B6 K1 includes tied inputs: a time-symmetric tied waveform and integer-valued series (section 10).
- B7 a segment whose values are all equal is invalid (section 7).
- B8 exact comparisons where the quantity is exact, one tie tolerance with an absolute floor for floats, and the rule for zero-spread transfer entries (sections 4.3 and 7).
- B9 K5's negative transfer criteria repaired so that they can fail (section 10).
- B10 the code builder's provisional readings D1 to D18 adopted or replaced (new section 11a).
- B11 other points from the code build: the K2 control's flag point, the K4 control, the instance tests and the mutation scope (sections 10 and 11).
- B12 the compute table updated to B5, B6 and B9 (section 11).

The original text stays in git history.

## 1. The claim as written

Source: repository Foundation-0/continuum, pull request #1 (open), head commit `8d3e7345f593378fd0ba6a020509d52afc9f362e`, file `continuum.md`.
The longer file in the same commit, `Distill to teach to humans as best as possible _n....md`, holds the display equations that `continuum.md` leaves blank.

Line 16, verbatim:

```text
Once labels, grids, and single-sense silos are stripped away, raw telemetry across wildly different physical domains—from spacetime strain and radio bursts to planetary vibrations and neural arrays—reveals the same four universal transformations sculpting reality.
```

The four transformations (lines 17 to 28): (1) Subtractive Selection, interference and scale flow. (2) Symmetry Fracture and topological memory. (3) Irreversibility as geometry. (4) Duality and emergent space.
For (3) the essay gives a formula, at line 38 of the longer file: entropy production along a path is the log-likelihood ratio of the path and its time reverse.

```text
\Sigma[\Gamma] = \ln \frac{dP[\Gamma]}{dP[\Theta\Gamma]}
```

The essay also gives its own standard for what is real (line 3): "the invariant that survives every change of net."
Line 11 names the changes of net it means: "different sensors, sampling rates, polarizations, and bases".
This test uses that standard as its acceptance rule.

## 2. The draft's defects, kept apart from the idea

Defects of the draft. These are reasons the sentence cannot be checked as written. None of them shows the idea is wrong.

- D1. Line 16 states a result ("reveals") but the pull request links no run, data file, log or ledger entry. A read-only search of the organisation's repositories found no run on real instrument data behind it. Earlier checks used simulated systems or constructed matrices.
- D2. The display equations are blank in `continuum.md` and appear only in the longer file.
- D3. The four transformations are written in terms of objects a single raw series does not come with: an action functional, a coupling constant and its flow, a symmetry group and the space a field lives on, a boundary and its area. The essay gives no rule that turns a raw series into these objects.
- D4. "The same" is not defined. The essay does not say which quantity must match, or how closely.
- D5. Section I also has a numbered list of four items (habits to replace). They are not the four transformations.
- D6. The data are named only by category (spacetime strain, radio bursts, planetary vibrations, neural arrays). No instrument, archive or file is named.

The idea, in its strongest form: label-free statistics of raw sensor series can show structure that the series' spectrum and value distribution do not explain, that structure survives the changes of net listed in line 11, and the same structure appears in instruments from unrelated domains.

## 3. The repaired claim under test

A transformation T "is revealed in raw telemetry" if there is a statistic, computed without units, labels or a physical model, such that all of the following hold:

1. Presence. In each instrument, the statistic departs from what matched surrogates give (section 6), at the pre-set level.
2. Invariance. The departure survives every change of net in section 5.
3. Sameness. A detector built from the statistic and fixed on instrument A works unchanged on instrument B, better than matched random detectors of the same form, for every pair of instruments in which T is present.

Scope: single-channel series from the four instruments in `DATA_REQUEST.md`, windows of 4,096 samples (Wind/WAVES by the rule in section 8), lags of 1 to 512 samples. Neural and other biomedical recordings are left out of this first run.
Comparison with existing physical theory is not part of this test. The statistics are judged on their own terms, against surrogates and generated noise.

## 4. Operational definitions, one transformation at a time

Two shared tools. An ordinal pattern is the order of the values in a short window. For three values (a, b, c) with b < c < a the pattern is written 201, meaning the first value is largest, the second smallest, the third in the middle.
Ordinal patterns do not change under any strictly increasing change of the values, so units, offsets, gains and amplitude scales drop out. This is the "labels and grids stripped" step of the essay, made exact.
A surrogate is a scrambled copy of a series that keeps its power spectrum and its set of values but destroys everything else. We use the iterative amplitude adjusted Fourier transform method (IAAFT, Physical Review Letters 77, 635, 1996).
Surrogates are always made from the normal scores of the segment, never from its raw values. Each segment (after its net is applied) is replaced by its normal scores Phi^-1((r - 1/2) / n), so every series enters the surrogate step with a Gaussian marginal, and its surrogates are made from those scores. Pattern counts depend only on order, so the real series' statistic is unchanged by this step.
The surrogate pool, and so the segment p-value, is then exactly the same for a series and for any strictly increasing map of it, provided the map leaves the number of distinct values unchanged (in floating point an increasing map can merge values, for example exp of values closer than 1e-16) and the same implementation of Phi^-1 is used throughout (one implementation, recorded with the code commit).
Control C4 (section 6) is built from the fit set's raw values, so it is not covered by this identity.
Each surrogate starts from a seeded random permutation of the normal scores and alternates two steps: impose the Fourier amplitudes of the normal scores, then replace values by the sorted normal scores in the current rank order.
It stops when the rank order is unchanged between two successive iterations, or after 1,000 iterations, and ends on the rank step, so a surrogate has exactly the segment's normal scores as its values.
Ranks are mid-ranks counted from 1 (tied values share the mean of their ranks). Two rank-based maps are used below: normal scores Phi^-1((r - 1/2) / n), with Phi^-1 the inverse standard normal distribution function, and equal-count bins floor(2^b (r - 1/2) / n). Tied values get the same score and the same bin.
A linear Gaussian process, or any strictly increasing function of one, looks the same forwards and backwards in time. So an IAAFT surrogate is a series with no time arrow by construction. The null hypothesis of the surrogate test is therefore "a strictly increasing map of a stationary linear Gaussian process".
That is narrower than "reversible": a reversible series of another kind can depart from it. K2 measures how often this happens for two such series (section 10).

### 4.3 Irreversibility (transformation 3): main test

Measurable form. The essay's formula averages to the Kullback-Leibler divergence between the statistics of forward paths and of reversed paths. On ordinal patterns of order d = 3 at lag tau:

```text
Sigma_hat(tau) = sum over patterns pi of p(pi) * ln( p(pi) / p(rev pi) )
p(pi) = (n(pi) + 1/2) / (sum of n + 13/2)
```

Here n(pi) counts windows (x_t, x_{t+tau}, x_{t+2tau}) with pattern pi, and rev pi is the pattern of the reversed window (012 and 210 form a pair, 021 and 120, 102 and 201). Patterns with tied values are kept as patterns of their own (13 patterns in all: 001 pairs with 100, 011 with 110, and 010, 101 and 000 are their own reverses). The number of tied windows is recorded.
Sigma_hat is zero in expectation for a reversible series and positive for an irreversible one.

Two exact facts make this statistic fit the essay's standard. Pattern counts are unchanged by any strictly increasing map. Flipping polarity (x to -x) relabels patterns by a bijection that commutes with reversal, so Sigma_hat is unchanged.
At the level of whole paths, the true divergence is also unchanged by any invertible filter that commutes with time reversal, such as a zero-phase whitening filter. The finite-order estimate is not exactly invariant under filtering. The known-answer tests showed it losing power after whitening, so whitening is used only as a Law 2b instance (section 12a), not as a confirmatory net.

Per-segment statistic. Lags tau = 2^j for j = 0 to 9 (1 to 512 samples), keeping only lags with 2 tau at most n/4 for a segment of length n. This one rule sets the lags for every window length, decimated segment and the Wind/WAVES N (at n = 2,048 the lags are 1 to 256). Each segment gives a pool of 100 series: the real one and M = 99 IAAFT surrogates.
For every series in the pool and every lag, Sigma_hat is standardised by the mean and standard deviation of the other 99 series in the pool. If those 99 values have zero spread at a lag, that lag is left out of the maximum for that series and the segment is flagged. If every lag has zero spread, the segment counts as not rejecting. T is the largest standardised value over the lags kept.
The segment p-value is (1 + number of surrogates with T at least the real T) / 100. Two floating values a and b count as tied when |a - b| <= 1e-12 x max(1, |a|, |b|), and ties count against the real series. This handles the several lags inside each segment.

Presence in an instrument. S verdict segments give S p-values. K is the number with p at most 0.05. Under the null each segment has probability exactly 5/100 of this.
The instrument p-value is the upper tail P(Binomial(S, 0.05) >= K), computed in exact rational arithmetic. Order d = 4 is the Law 2b instance O4 (section 12a) and is not part of the confirmatory verdict.

Sameness (transfer). For each segment and lag level, three features that do not depend on instrument polarity:

```text
a1 = ln( n(012) / n(210) )   a2 = ln( n(021) / n(120) )   a3 = ln( n(102) / n(201) )   (counts + 1/2)
u  = a2 - a3                 changes sign under time reversal, unchanged by polarity flip
m1 = |a1|,  m23 = |a2 + a3|  magnitudes of the parts whose sign depends on polarity
```

Under polarity flip (a1, a2, a3) becomes (-a1, -a3, -a2), and under time reversal it becomes (-a1, -a2, -a3). So u is a time arrow that does not depend on which way the sensor is wired, while m1 and m23 do not change under time reversal. Each feature is standardised against the pool, as above.
Limit, exact. With s = a2 + a3, polarity flip and time reversal act the same way on (a1, s), so no polarity-free statistic of (a1, s) carries a time arrow. The polarity-free arrow u changes sign under reversal composed with polarity flip.
For any series whose statistics are unchanged by that composition (a sawtooth is one), u is zero in expectation, and reversing time is the same as flipping polarity. The arrow test is blind to such series.
Lag levels are aligned across instruments by each instrument's own time scale: tau0 is the median, over fit segments, of the smallest lag at which the autocorrelation of the segment's mid-ranks (biased estimate, about the mean) drops below 1/2, capped at 512.
The comparison is exact: it uses n times the doubled mid-ranks minus their sum, which are integers, so the numerator and denominator of the autocorrelation are integers, and "below 1/2" means twice the numerator is less than the denominator. The aligned level is j minus log2(tau0) rounded half up.
Levels -4 to +5 are kept. A level outside a series' range is set to 0.
Two transfer tests are built from these features:

- Arrow transfer: the u features only, 10 per series. Matched random detectors are R = 99,999 draws, each a random permutation of the entries of w_A combined with an independent random sign for each entry. The signs matter because a shared arrow direction is what "the same arrow" means, and a permutation alone keeps the sign mix of w_A.
- Profile transfer: the m1 and m23 features, 20 per series, which do not change under time reversal. Matched random detectors are R = 99,999 random permutations of the entries of w_A. This test compares the shape of the irreversibility profile across scales, not its direction.

For each test, the template w_A is the mean feature vector over instrument A's fit segments, scaled to unit length, and the score of a series is w_A dotted with its features.
On instrument B's verdict segments, the score S_B(w) is the mean over segments of w dotted with the segment's standardised features. The transfer p-value is (1 + number of random detectors with S_B at least S_B(w_A)) / 100,000. A transfer is "adverse" when S_B(w_A) is below the 2.5th percentile of the random detectors' S_B.
An earlier version compared each real series with its own surrogates by an AUC. The known-answer tests showed that this saturates at 1 for any strongly irreversible series and leaves the null without power, so the mean standardised score, which does not saturate, replaces it.
Random detectors permute only the entries at levels populated in both A and B. Entries elsewhere are left in place (they multiply zeros). If fewer than 6 levels are populated in both, the arrow transfer counts as not rejecting. If fewer than 8 features are populated in both, the profile transfer counts as not rejecting.
Random detectors identical to w_A tie with it, so a sampled test cannot go below (1 + R/D)/(R + 1), where D is the number of distinct random detectors that w_A's entries allow (computed exactly from them). A transfer run counts as not passing unless that value is within its per-run level (section 5).
With R = 99,999 and distinct entries the value is 3.2e-5 for 6 levels with signs (D = 46,080) and 3.5e-5 for 8 features with permutations (D = 40,320), within the smallest per-run level of a confirmatory transfer test, 0.00125 / 5 = 0.00025 (scale flow) and 0.00125 / 3 = 0.00042 (arrow and profile).
The confirmatory levels alone would allow 7 features or 5 levels. The floors of 8 features and 6 levels, and R = 99,999, are set by the smaller per-run levels of the Law 2b family (section 12a), where 7 features give 2.1e-4 and 5 levels 2.7e-4, both too large.

### 4.1 Subtractive selection (transformation 1)

Interference and stationary phase. The essay writes a stationary-action condition. A single raw series has no action functional, and the essay gives no rule to build one from data.
Status: needs the authors' operational definition. Nothing is tested for this half.

Scale flow. The essay says that under repeated coarse-graining "microscopic accidents die off" and disparate systems are driven into the same classes at fixed points. A measurable form needs no physics:

- The flow is block averaging by 2, applied separately to each contiguous valid run of a file (no average crosses a gap or flagged sample), levels l = 0, 1, 2 and so on, as long as a level still gives at least 12 segments.
- At each level, segments are cut as in section 7. The feature vector is the frequency, over all windows, of ordinal patterns of order 4 at lag 1, summed over the 8 classes of patterns without ties that map to each other under time reversal and polarity flip, plus a ninth class holding every window with a tie.
Each of the 9 frequencies is standardised against the pool of 99 IAAFT surrogates of that segment (made from its normal scores, as everywhere). For order 4 the pseudocount is 1/2 for each of the 75 tied and untied patterns, so the denominator is the count plus 75/2.
- These 9 features are unchanged by polarity and by time reversal, so this test measures time-symmetric structure beyond the spectrum. It does not overlap with the irreversibility test.
- Levels are aligned by intrinsic scale as in 4.3 (aligned level = l minus round(log2 tau0)), levels -3 to +3 are kept, 63 features.

"Dies off" alone does not discriminate. Averaging a short-memory series drives it towards a Gaussian series, so the departure from surrogates shrinks for almost any noise. Generated noise will be shown to do this (test K5).
So the decay is reported but is not counted as evidence. The verdict for this half rests only on sameness: the transfer test of 4.3, with permutations only (as for the profile transfer) and the same rule on levels populated in both instruments.
The unit of the flow transfer is a (level, segment) pair: a segment at flow level l fills the 9 entries of its own aligned level and the other entries are 0. For instrument B, S_B(w) is the mean over B's aligned levels of the mean over that level's units of w dotted with the unit's features, so each level counts equally however many segments it has.
Units are never copied across levels, so no feature is counted twice.
Block averaging uses amplitudes, so this flow is unchanged by linear rescaling but not by other increasing maps. The two amplitude maps of section 5 are therefore run as nets for this test (and only for this test).

### 4.2 Symmetry fracture and topological memory (transformation 2)

The essay's objects are a continuous symmetry group G, a subgroup H, the space G/H, a field that settles over space, and defects classified by homotopy groups of G/H.
A single raw time series comes with none of these. The essay does not say what the field is, what space it lives on, or what G is for a strain record, a seismogram, a radio spectrum or a light curve.
Status: needs the authors' operational definition. Nothing is tested.
One route the authors could take is in their own section I, item 4: a pattern as "a persistent homology class that refuses to contract away when the data is stretched or resampled". If they adopt it, it can be pre-registered with the same nets and controls.

### 4.4 Duality and emergent space (transformation 4)

The dualities named (adjunctions, tau to -1/tau, waves to frequencies) are either exact mathematical identities that hold for every series (the Fourier pair) or need a coupling parameter a raw series does not have.
The emergent-space part says distance comes from mutual information. Its plain reading on a sensor array, "information falls with sensor distance", is true of almost any smooth field and would not discriminate.
Status: needs the authors' operational definition, including what it predicts beyond what linear correlation between channels already gives. Nothing is tested.

## 5. Nets (changes of observation)

Each net is applied to the real segment first. Fresh surrogates are then made from the changed segment.

| Net | Versions | Notes |
|---|---|---|
| Native | as recorded | primary |
| Sampling rate | block mean by 2, plain subsampling by 2 | applies only where the result has at least 2,048 samples. Lags follow the rule in 4.3 |
| Quantization | 12 bits and 8 bits, as equal-count bins floor(2^b (r - 1/2) / n) on mid-ranks, b = 12 and 8 | tied patterns kept (section 4.3). Values tied before binning stay tied |
| Amplitude map | strictly increasing maps | exact for presence and for the arrow and profile transfers, because surrogates are made from normal scores (K1). Run as two statistical nets (normal scores of the ranks, and exp of the series standardised to unit variance, each applied to the whole stream before block averaging, as reading D10 states) for the scale-flow transfer only |
| Polarity | x to -x | exact code check (K1), including the surrogate pool |
| Zero-phase whitening | not a confirmatory net | used as Law 2b instance W (section 12a). The known-answer tests showed the order-3 estimate losing power after whitening on planted shots, which the true path divergence does not. The essay's own list of nets includes "bases", and a Fourier-domain whitening can reasonably be called a change of basis, so dropping it from the confirmatory nets makes "supported" easier and puts that net among the rescue routes, which makes a final "evidence against" harder |
| Window placement | block grid shifted by half a block | new segments |
| Window length | N/2 | applies only where N/2 is at least 2,048. Lags follow the rule in 4.3 |
| Instrument | second channel: L1 for H1, SP for VBB, S antenna for Z antenna | TESS has no second channel in this run |

Presence counts for an instrument only if the primary run and every applicable net run each pass.
A test's level from section 9 is split equally across its runs (Bonferroni, as Aletheia version 2.0.0 requires): a presence test has up to 8 runs (native, two sampling rates, two quantizations, window placement, one window length, instrument), 7 for TESS, which has no instrument net, so each run is judged at the test's Holm level divided by the number of runs that apply.
No confirmatory run uses a segment shorter than 2,048 samples. On synthetic shots (the K3 series) the clean-room check measured detection of 0.925 at 4,096 samples, 0.60 at 2,048 and 0.30 at 1,024.
A run needs a share of rejecting segments of at least 0.30 (a margin of 1/4 over a control near 0.05), so a length where a planted arrow is found in only 30 percent of segments cannot tell "presence" from its absence. The plan requires 50 percent detection of the K3 series at every confirmatory length (section 10), and 1,024 samples cannot reach it, so lengths below 2,048 were removed.
This was set after those measurements.
The instrument's presence p-value is the largest p over its runs, multiplied by the number of runs, and set to 1 if any run fails the margin or ceiling rule below. That adjusted value enters the Holm procedure.
A run passes only if three things hold in that run: its binomial p is within the run's level, the share of rejecting segments K/S exceeds the share in each of the controls C2 (spectrum-preserving null), C3 (IID shuffle null) and C4 (generated noise), run in that same net, by at least 1/4, and each of those control shares is at most c_max(S) (section 6).
If a net version yields fewer than 12 valid segments, that net is "underpowered" for that instrument and the instrument is marked net-incomplete.
For the arrow and profile transfers the runs are the primary, the instrument net and window placement, 3 in all. For the scale-flow transfer they are those 3 and the two amplitude maps, 5 in all.
A transfer p-value is the largest over its runs, multiplied by the number of runs, and set to 1 if in any run the same transfer with B's C2 series or with B's C3 series in place of B reaches p at most 0.01.

## 6. Controls and what "absent" means

| Control | Built from | Absent means |
|---|---|---|
| C1 IAAFT surrogates | each segment | reference pool inside every test |
| C2 Surrogate as data | one fixed surrogate per verdict segment, run through the whole pipeline with its own 99 surrogates | K below the binomial 1 percent excess point, the smallest k with P(Binomial(S, 0.05) >= k) at most 0.01 (K < 4 when S = 12, K < 5 when S = 24, K < 6 when S = 32) |
| C3 Shuffle | random permutation of each verdict segment | same rule as C2 |
| C4 Generated noise | 32 series per instrument with the fit-set median periodogram and fit-set value distribution | same rule as C2 |
| C5 Transfer on surrogates | each transfer test with B's C2 series in place of B | transfer p above 0.01 |
| C6 Instrument noise | TESS background flux (SAP_BKG). GW blocks containing the event time | descriptive, no pass or fail |

If C2, C3 or C4 fails in the primary run under the rule above, the test is not calibrated for that instrument and its result is "invalid", whatever the real data give.
The control ceiling used in every run (section 5) is c_max(S) = (k - 1)/S, with k the smallest count whose tail P(Binomial(S, 0.05) >= k) is at most 0.01/24 (three controls in each of 8 runs): 4/12 at S = 12, 5/16 at S = 16, 6/24 at S = 24 and 7/32 at S = 32. A calibrated pipeline exceeds it in any of the 24 checks with probability at most 0.0045 (0.00441 at S = 12, the largest).
The signal margin is 1/4 in every run.
C6 is descriptive because "no known source" does not mean "no time arrow": the instrument chain can be irreversible itself. If instrument noise shows the same signature at the same strength, the report attributes it to the instrument chain, not to the source.

## 7. Segment rule

All blocks are fixed by position before any value is read. A block is N + 128 samples, numbered from the start of the file. N = 4,096 except for Wind/WAVES (below).
With J complete blocks, k = max(1, floor(J / 32)). Blocks with index divisible by k are selected, and the first 32 selected are kept.
Inside each kept block, the N-sample segment starts at the offset in 0 to 128 that best matches the segment's ends: the smallest sum of the squared jump between first and last value and the squared jump between first and last slope, computed on the exact mid-ranks of the whole block (tied values share the mean rank). Among equal costs the smallest offset is taken.
Ranks make the choice unchanged by any increasing map and by polarity flip. This limits a known IAAFT artefact and uses the same rule everywhere.
Validity, decided from flags, sample times and missing-value markers only: GW, every second has the DATA and CBC_CAT1 bits set, no hardware injection bit, no missing value. SEIS, no gap or overlap in sample times, no sample at full scale.
Wind/WAVES (series indexed by sweep): every value of the four channels in the block is finite and differs from the variable's fill value, every interval between successive sweeps in the block is within 10 percent of the block's median interval, and no interval exceeds twice that median.
The median of m intervals is the order statistic of rank ceil(m/2), the lower of the two middle values when m is even.
These comparisons are exact: each stored time value is a binary fraction, and intervals, medians and both bounds are computed and compared as exact rationals, with no tolerance. TESS, QUALITY equal to 0 and finite flux on every cadence.
A segment whose values, after its offset and its net are applied, are all equal is invalid too: it carries no order. Like any invalid block it counts as a non-rejecting segment and stays in the denominator S. It gives no tau0, no template contribution, no transfer feature and no flow unit. Its C2 and C3 series, made from it, are invalid and non-rejecting.
Its C4 series does not depend on it and is computed as usual.
An invalid selected block counts as a non-rejecting segment. It is not dropped from the denominator. If more than 25 percent of selected blocks are invalid, the instrument is underpowered for that net.
On-source extra: for GW only, the block containing the event time is analysed as a labelled extra and reported descriptively. It is not part of S.

## 8. Split between fitting and verdict

| Instrument | Fit set (may be inspected) | Verdict set (opened once) |
|---|---|---|
| GW strain | GW150914 4,096-second files, H1 and L1 | GW151226 4,096-second files, H1 and L1 |
| Mars seismometer | 2019 day 143, VBB and SP | 2019 day 207, VBB and SP |
| Solar radio | Wind/WAVES RAD2, 2015-01-01 to 2015-01-08 | 2015-07-01 to 2015-07-08 |
| Stellar photometry | TESS 20-second light curve, sector 38 | sector 65 |

The fit set fixes only these free choices: each instrument's tau0 and level shift, the transfer templates, the Wind/WAVES N, and the event-rich threshold of Law 2b instance E. Every statistic, threshold and lag above is fixed by this document.
The verdict files are hashed on download and not otherwise opened until the fit results are committed. The verdict run is one run of the committed code, identified by its hash.

For Wind/WAVES the four channels used are those at positions round((q + 0.5) F / 4), q = 0 to 3, in the file's frequency list of length F. Channels at the same time are strongly dependent, so segments never overlap in time.
The eight daily files of a set are joined in date order into one sweep sequence, and blocks are numbered along it across day boundaries (a block that spans a gap is invalid by the rule in section 7). The every-k rule selects blocks, and the i-th selected block (i = 0, 1, 2, and so on) is taken from channel i mod 4.
This uses all four channels whenever 4 or more blocks are selected, with counts differing by at most one (checked for every J from 32 to 719).
N for Wind/WAVES is the larger of 4,096 and 2,048 for which the fit set gives at least 12 valid blocks under this rule. It is found by reading, from the fit files only, the sweep times, the frequency list, the fill-value attribute and the values of the four selected channels, and counting valid blocks. No other quantity is computed.
The count and the chosen N are committed before the verdict files are opened. If even 2,048 gives fewer than 12, Wind/WAVES is underpowered, and support for T3 is then impossible in this run, since it needs all three counting instruments. Twelve time-disjoint blocks of 2,048 + 128 sweeps in 8 days need a cadence of at most 26.5 seconds. The cadence is not known before the fit files are opened.
Lags are limited to 2 tau at most N/4.

## 9. Confirmatory tests, multiplicity and the smallest reachable p

The confirmatory family has 40 tests. Holm's step-down method controls the family-wise error rate at 0.05. The smallest Holm threshold is 0.05 / 40 = 0.00125.
19 of the 40 tests involve TESS, which cannot count toward support. They stay in the family. Moving them to their own family would let the other 21 face a smallest threshold of about 0.0024, which is less strict, and every test can still reach 0.00125. This keeps the chance of every outcome other than "inconclusive" lower than the alternative would.

| Test | Count | Smallest p reachable | Reaches 0.00125? |
|---|---|---|---|
| T3 presence, one per instrument (up to 8 runs, each at the Holm level / 8) | 4 | per run 0.05^S: 2.4e-16 at S = 12, 2.3e-42 at S = 32 | yes. At 0.00125 / 8 a run needs K >= 6 of 12, 7 of 24 or 8 of 32 |
| T3 arrow transfer, ordered instrument pairs (3 runs) | 12 | per run (1 + R/D)/(R + 1) = 3.2e-5 at 6 jointly populated levels, R = 99,999 | yes, per run level 0.00042 |
| T3 profile transfer, ordered pairs (3 runs) | 12 | per run 3.5e-5 at 8 jointly populated features, R = 99,999 | yes |
| T1 scale-flow transfer, ordered pairs (5 runs) | 12 | per run 3.5e-5 at 8 jointly populated features | yes, per run level 0.00025 |

Tests flagged now because they cannot reject at the family level, so they are descriptive only:

- One segment against its surrogates: smallest p is 1/100. It feeds the count K and is never used alone.
- The GW on-source block: smallest p is 1/100.
- An instrument with fewer than 12 valid segments: reported as underpowered.
- A transfer test below the populated-feature counts of section 4.3: counts as not rejecting.

The binomial tail assumes segments are independent given the null. The every-k spacing keeps segments apart (128 seconds for GW, about 42 minutes for SEIS), and Wind/WAVES segments never overlap in time. As a robustness check, not part of the verdict, presence is recomputed on every second verdict segment.

## 10. Known-answer tests, run before any real data

All synthetic, with logged seeds. K2 and K3 are run at every window length a confirmatory run can use: 4,096 and 2,048 samples.
Record.
On the frozen plan (commit `24d7757`), the code at builder commit `71142c1` failed four of the six known-answer tests before any data file was opened.
K1 passed (228 exact checks), K2 failed (11 of 21 classes above the bound, all exp or cube versions, highest 0.295), K3 failed (4 of 9 cells), K4 failed (A to B p = 0.2025, A to C saturated at AUC 1.000), K5 failed (its cascade criterion was also passed by a shuffled cascade), K6 passed.
The tests below are the amended ones. They have not yet been run.
Gate. No data file is opened until the code has been updated to this amended plan and every test below passes in all three Python modes with its must-fail control flagged. Every test has one: K1 has three broken variants, K2 one, K3 one, K4 two, K5 one (the shuffled cascade) and K6 six.
If any test fails, or any must-fail control is not flagged, the plan is amended again, with the date logged, before any data file is opened.

- K1 Exact checks. Integer counts are compared exactly.
  - Pattern counts are equal under the comparison maps y^3 + y, exp(y) and the ranks of x, with y = x / max|x| (as below).
  - Counts of -x equal counts of x relabelled by complement. Counts of the reversed series equal counts relabelled by reversal. Sigma_hat is equal for x and -x.
  - With the same seeds, the surrogate pool of -x is the negated pool of x, so the segment p-value of -x equals that of x. The segment offset chosen in a block is the same for x, -x and any increasing map of x.
  - With the same seeds, the normal scores, the surrogate pool, every standardised feature and the segment p-value are identical for x and for each comparison map of x: y^3 + y, exp(y) and the ranks of x, where y = x / max|x|. Dividing by max|x| keeps every argument in [-1, 1], so no map can overflow.
  Class versions. All 9 K2 classes, each in three versions (plain, exp and cube of the standardised series), 27 versions in all, 20 seeds each, at 1,024 samples for the whole pipeline. At 4,096 and 2,048 samples the normal scores of the exp and cube versions are compared with those of the plain version exactly.
  Per class and seed, 13 series go through the pipeline: the plain series, its three maps, its negation, the exp and cube versions, and the three maps of each version. All are compared with the plain series (the negation by the polarity relation).
  Representability guard, stated before any run. A (class version, map, seed) case counts only if the mapped series is finite and has as many distinct values as its input. A case that fails is recorded as "map not representable", never as a pass. For each class version and map, at least 18 of the 20 seeds must be representable, or K1 fails.
  The guard itself is tested on exp of values spaced 1e-17 apart.
  This identity is why the exp and cube versions need no separate statistical run in K2.
  - Tied inputs (integer sensor counts are tied). (a) The waveform [0, 0, 1, 2, 2, 1, 0, 0] repeated 512 times (4,096 samples), which is exactly time-symmetric. At every lag used, each pattern count, tied patterns included, must equal the count of its reversed pattern, so Sigma_hat and the features a1, a2 and a3 are exactly 0, and every pattern count must be identical under the three maps.
  (b) Each of the 7 null classes at 1,024 samples, made integer-valued as round(8 z) with z the standardised series, 20 seeds: the pipeline identity above must hold, with mid-ranks giving tied values equal scores.
  - Counts at lag 2 tau over even start points equal counts at lag tau of the series subsampled by 2.
  - A second implementation that shares no code must match every integer count.
  - Must-fail controls, each to be flagged: a counter that drops the last window, a counter that orders tied values by position instead of keeping tied patterns, a surrogate step that uses the raw values instead of the normal scores (the identity must then fail under exp), and a ranking that breaks ties in time order instead of using mid-ranks (Sigma_hat on the tied waveform must then be non-zero).
- K2 Nothing found in noise. 1,000 seeds per class at 4,096 and at 2,048 samples, for 9 classes.
  - Classes: white Gaussian, AR(1) with coefficient 0.5, 0.9 and 0.99, power-law noise with spectral slope 1 and 2 (Fourier synthesis with random phases), and three sinusoids (0.0137, 0.0781 and 0.2113 cycles per sample, unit amplitude, random phases) in white noise of standard deviation 1. Each is scaled to mean 0 and standard deviation 1.
  - Two reversible series that are not an increasing map of a linear Gaussian process: g^2 and |h|, with g an AR(1) series with coefficient 0.9 and h one with coefficient 0.99, both of unit variance.
  - The exp and cube versions of the 7 classes above enter the pipeline with exactly the normal scores of their plain versions (K1), so they are covered by the plain runs.
  - K2a, the 7 null classes. A class is flagged at a length if 74 or more of its 1,000 segments have p at most 0.05. 74 is the smallest k with P(Binomial(1000, 0.05) >= k) at most 0.01/14 (7 classes at 2 lengths), so if every class is calibrated the chance that any is flagged is at most 0.0090.
  If the true rate of every class were 0.055 that chance would be 0.091, at 0.06 it would be 0.43, and at 0.07 above 0.99. Any flag fails K2 and stops the run before data (gate), because after normal scores these classes are exactly the null of the test.
  This gate is looser per check than the earlier point of 68: a class whose true rate is 0.07 is caught at one length with probability 0.33, against 0.62 before. In exchange, a calibrated run is stopped by mistake with probability at most 0.009, against 0.099.
  - K2b, the 2 reversible non-Gaussian classes. Their rates are reported with exact (Clopper-Pearson) 99 percent intervals. A class is flagged at a length if 129 or more of its 1,000 segments have p at most 0.05, the smallest k with P(Binomial(1000, 0.10) >= k) at most 0.01/4, so a flag shows a rate clearly above 0.10. Any flag fails K2 and stops the run.
  A rate up to 0.10 does not stop it. The chance that a series whose segment rate is r passes one presence run was computed exactly as a maximum over every segment count S from 12 to 32 and every run count in use (8 runs for GW and SEIS and for Wind/WAVES at N = 4,096, 7 for TESS, 5 for Wind/WAVES at N = 2,048), at the smallest Holm step, where the per-run level is 0.05/40 divided by the runs.
  Figures are rounded up.
  At r = 0.10 the chance is at most 0.012 if every control share in the run were 0 (attained at 5 runs, S = 26), and at most 0.0086 if every control share were 0.05, so that the 1/4 margin needs a share of 0.30 (attained at 5 runs, S = 19). At S = 32 the second figure is 0.00081 for every run count.
  At the stopping line, r = 0.129, the two figures are at most 0.047 (5 runs, S = 32) and at most 0.029 (5 runs, S = 19). In every case the 5-run instrument, Wind/WAVES at N = 2,048, attains the maximum. At r = 0.129 with control shares 0 the 7- and 8-run instruments tie with it at S = 32 (exact, `checks/amendment_2/recompute_k2b.py`).
  A presence test judged at a later Holm step has a larger per-run level, and these chances are then larger. At the largest step, 0.05 divided by the runs, which a presence test reaches only if every other confirmatory test has already rejected, they are at most 0.069 and 0.035 at r = 0.10, and 0.142 and 0.076 at r = 0.129.
  With control shares 0 these maxima fall at S = 16, K >= 4, for 5 or 7 runs. With control shares 0.05 they fall at S = 13, K >= 4, for every run count.
  These figures bound one run only. Such a series must pass every run of its presence test. The runs of one instrument are not independent (the native run and the two quantizations are nearly the same series), so the chance of passing all of them lies between the product of the single-run chances and the largest single-run chance.
  So a reversible class just below the stopping line could pass a whole presence test with a chance of a few percent at most at the smallest Holm step, and more at later steps.
  A "supported" outcome needs, in addition, all three counting instruments present and the transfers to pass. The clean-room check measured these classes at 0.05 to 0.09 (at 1,024 samples).
  - No class is matched to an instrument any more. K2 is a gate on the whole run. Calibration for each instrument is checked by its own controls C2 to C4 (section 6).
  - Must-fail control, to be flagged: surrogates made from the raw values, applied to AR(1) 0.9 after exp at 4,096 samples (the frozen plan's version, measured at 59 of 200), run on 200 seeds and judged by the K2a rule at its own seed count: flagged at 22 or more of 200 (the smallest k with P(Binomial(200, 0.05) >= k) at most 0.01/14).
- K3 Planted structure found, 200 seeds per case.
  - Exponential shots: a shot starts at each sample with probability 0.01, rises at once to 3 times the exact standard deviation of the background and decays over 10 samples (kernel cut at 100 samples), on an AR(1) background with coefficient 0.9.
  - The logistic map at r = 4 from a random start, the first 1,000 steps dropped, with Gaussian observation noise of 0.1 of its standard deviation.
  - A sawtooth of period 64 samples, rising in ramps through the values k/64, k = 0 to 63 (peak to peak 63/64), with white noise of standard deviation equal to half the sawtooth's standard deviation (0.144). This reading of the old text "half its amplitude" was chosen after the builder's run showed the other reading (standard deviation 0.5) failing every criterion, and is labelled so.
  The noisier case (0.5) is run and reported, but does not gate.
  - Required: segment detection at least 80 percent on the native net at 4,096 samples, and at least 50 percent at 2,048 samples (the native length of Wind/WAVES if its N is 2,048) and under every other statistical net of section 5 except the instrument net (block mean by 2, subsampling by 2, two quantizations, window placement, window length N/2).
  The clean-room check measured native detection of the K3 shots at 0.70 at 2,048 samples, so an 80 percent rule there would fail almost surely. The split was set after that measurement. An instrument whose native length is 2,048 therefore enters with lower power, which makes "supported" harder for it, not easier.
  50 percent at every confirmatory length is the detection a net needs for a pass of its run to be likely when an arrow is present (with 32 segments, a rate of 0.5 gives K >= 10 with probability about 0.99).
  - Must-fail control, to be flagged: surrogates made by circular shifts (which keep the time arrow) on the shots must give native detection of at most 20 of 200 segments.
  - If any net fails this, the run stops before any verdict file is opened, and the net is changed only by a dated amendment that the report lists.
- K4 Transfer.
  - Synthetic A: the shots of K3. Synthetic B: shots made at twice the rate (decay over 10 fine samples) on power-law noise of slope 1, then every second sample kept and the sign flipped. Synthetic C: the time reverse of a fresh series of kind A. Each stream has 33 blocks, so the primary grid and the grid shifted by half a block both give 32 segments.
  Every synthetic instrument has two independent streams per seed, made with different seed purposes: a fit stream, whose segments give tau0 and the template, and a verdict stream, whose segments are scored. Templates come only from fit streams and scores only from verdict streams. 10 seeds.
  - A to B must give arrow transfer p and profile transfer p at most 0.001 in every run, in at least 9 of the 10 seeds.
  - A to C must give an arrow transfer score S_B(w_A) below the 2.5th percentile of its random detectors in every run, in at least 9 of the 10 seeds. The profile transfer A to C is expected to pass, because the profile does not change under reversal, and its result is reported.
  - Must-fail controls: A to A' where A' is A cut into its 33 blocks, the block order shuffled and each block replaced by an IAAFT surrogate of itself, with its own fit stream made the same way.
  Neither the arrow transfer nor the profile transfer may reach p at most 0.01 in more than 1 of the 10 seeds, where a seed counts as reaching it if p is at most 0.01 in any run (primary grid or shifted grid).
  - Blind spot, reported: a sawtooth rising in ramps (period 64, values k/64, k = 0 to 63, peak to peak 63/64) with white noise of standard deviation half the sawtooth's standard deviation (0.144), and its time reverse. The arrow transfer between them is expected not to reject in either direction (section 4.3, limit).
- K5 Scale flow.
  - Every K5 series has 2^19 = 524,288 samples (the cascade has depth 19), cut by the segment rule at flow levels 0 to 3, which give 32, 32, 31 and 15 units. Level 4 would give 7 and is not used. For the transfer criteria each case has two independent series per seed, a fit series that gives tau0 and the template and a verdict series that is scored, as in K4.
  - Per level, the flow departure of a unit is its sum of squared standardised features. A unit "departs" if at most 4 of its 99 surrogates have a sum at or above its own, so that its p-value is at most 0.05. Sums count as equal under the float tolerance of section 4.3, and an equal sum counts as at or above, so a tie never makes a unit depart.
  A level "shows departure" if the count of departing units is at or above the binomial 1 percent point for its number of units at rate 0.05. 10 seeds per case, criteria required in at least 9 of 10.
  - Independent exponential values (an increasing map of white noise, so exactly a null case after normal scores): no level shows departure.
  - A dyadic random cascade with log-normal weights of mean 1 and log standard deviation 0.5: departure shown at level 0 and at the highest populated level. Construction: start from the one-element array [1].
  For each of 19 steps, step j = 0 to 18, draw 2^(j+1) standard normal values Z in order from the series' generator, form the weights W = exp(0.5 Z - 0.125), repeat each element of the array twice, and multiply element by element by W. After step 18 the array has 2^19 = 524,288 elements.
  - The same cascade shuffled in time (no structure): no level shows departure. This is the control that the old cascade criterion failed.
  - y_t = e_t^2 + e_(t-1)^2 with e white Gaussian (reversible, non-Gaussian, short memory): departure at level 0, reported at higher levels (expected to fade).
  - Two further series for the negative transfer criteria, meant to share the cascade's time scale:
  the IAAFT cascade (an IAAFT surrogate of the whole cascade series, made from its normal scores, which keeps its spectrum and so, approximately, its mid-rank time scale, but removes its nonlinear structure), and y' = g^2 with g a stationary AR(1) series of unit variance and coefficient c = 0.9859 (reversible, non-Gaussian, with a long memory).
  The rule for c: the population mid-rank autocorrelation of g^2 at lag k is 12 E[(2 Phi(|X|) - 1)(2 Phi(|Y|) - 1)] - 3 for standard normal X and Y of correlation c^k, and c is the value at which it equals 1/2 at lag 16, rounded down to 4 decimals, so that it is first below 1/2 at lag 16 (`checks/amendment_2/derive_yprime.py`).
  Lag 16 is the cascade's tau0 as the code builder reported it. Simulated with the construction above, the cascade's tau0 varies by seed (9 to 18 in 10 seeds of a check, level shifts 3 and 4), while y' gives shift 4 in every seed. Either way the two share at least 2 aligned levels.
  The guarantee that each negative criterion can fail is the evaluability rule below, not the matching of these constants.
  - Transfer criteria. Cascade (fit) to cascade after a monotone map (exp of the standardised series, verdict) must give flow transfer p at most 0.001 in the primary run and in both amplitude-map runs. Cascade (fit) to y' (verdict) must give p above 0.05. IAAFT cascade (fit) to cascade (verdict) must give p above 0.05. The negative criteria are judged on the primary run.
  - Every transfer criterion must be evaluable: at least 8 features populated in both series in at least 9 of the 10 seeds. Otherwise K5 fails. A seed with fewer counts as failing its criterion. This rule, not the choice of y' or the IAAFT cascade, is what guarantees that a negative criterion can fail.
  - Series per seed: the independent exponential values, the cascade (fit and verdict), the shuffled cascade, y_t, y' (verdict), the IAAFT cascade (fit), and the exp-mapped cascade (verdict) in three runs, 10 sets of 110 units. These draws use the seed-rule instrument tag `K5b:<case>`, so they do not reuse the draws of the earlier K5 definition.
- K6 Gate checks.
  - Empty input, missing values, a constant series and a series shorter than N are rejected with explicit errors.
  - Each refusal has a must-fail input that trips it. Removing any refusal branch must make the test suite fail.

## 11. Seeds, code and reruns

Master seed 20261121. Every random draw uses a seed made from the first 16 hex digits of SHA-256 of the string `master|instrument|split|net|segment|purpose|index`, fed to numpy's default generator.
Every script must give identical output under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`. No bare `assert` on any validation path.
The analysis code meets the gate-integrity contracts R1 to R7 of Aletheia version 2.0.0: it rejects empty, missing or malformed input (R1, R2), type-checks before comparing values (R3), runs identically in the three modes (R4),
has a must-fail control for every refusal and is mutation-tested (R5, defined below), takes every check and threshold from this document only (R6), and recomputes every compared value from the hash-pinned bytes (R7).
Mutation test for R5. For every refusal, comparison and threshold in the analysis code, three kinds of mutant are made: the refusal deleted, the comparison flipped between strict and non-strict, and the threshold moved by one unit.
A unit is 1 for an integer threshold (a count of segments, units or seeds), the smallest step of the stated decimal for a rational threshold (0.001 for 0.050, 0.01 for 0.30), one representable step for a floating tolerance such as 1e-12, and one bin or one sample for window, lag and bin counts. The known-answer suite must kill every mutant.
A mutant that survives is either killed by an added test or recorded as equivalent with its reason, before any data file is opened.
Every condition in sections 5, 6, 12 and 12a is computed by the plan's own analysis code from measured values, and is checked by the second checker. No outcome depends on a verdict from any outside tool. Running the published certifiers of the Law 2b reference specification or of Aletheia version 2.0.0 on the same values is an extra and never the basis of an outcome.
Effects that were not pre-registered are reported separately as leads, and every miss stays in the record.
A second checker with no shared code recounts all patterns on the saved surrogate files (exact integer match required) and repeats the verdict with its own surrogates and seeds. If the two disagree on any outcome category, that outcome is recorded as unresolved.
Commit order: this plan (`24d7757`), then Amendment 1 with the data manifest (files fetched and hash-pinned, none opened), then the analysis code updated to the amended plan with the outputs of the amended K1 to K6, which must all pass (section 10, gate), then the fit-stage results (tau0, level shifts, templates, the Wind/WAVES N, the threshold of instance E), then the verdict.
Any change to this plan before the verdict files are opened is added as a dated amendment with its reason. Changes after that are not allowed, and a test changed after that is reported as exploratory.
Compute (estimate, `checks/check_compute.py`, recomputed in Amendment 2 by `checks/amendment_2/compute_components.py`). The unit cost is the builder's measured 2.29 processor-seconds per 4,096-sample pool (builder commit `71142c1`, `known_answer/out/timing.txt`), and a pool on fewer samples is costed in proportion (a 2,048-sample pool counts as 1/2).
In the Count column, "plan" marks a count stated in this plan (with its section), "measured" a cost measured by the builder, and "assumption" a figure this estimate assumes. Components per Python mode:

| Component | Count | Processor-seconds |
|---|---|---|
| K2 | plan, section 10: 9 classes x 1,000 seeds x 1.5 pools (4,096 and 2,048 samples) | 30,915.00 |
| K1 identity check | plan, section 10 (B5, B6): 9 classes x 20 seeds x 13 series, and 7 classes x 20 seeds x 4 integer-valued series, at 1,024 samples (1/4 pool each), plus 4 pools for the tied waveform | 1,669.41 |
| K3 | plan, section 10: 4 cases x 200 seeds x 5.5 pools (7 runs), plus 200 pools for the must-fail control | 10,534.00 |
| K4 | plan, section 10: 10 seeds x 2 streams (fit and verdict). Measured: 490 s per set of streams (builder commit `71142c1`, `known_answer/out/timing.txt`, K4 at 488.6 to 489.9 processor-seconds per mode, rounded up) | 9,800.00 |
| K5 | plan, section 10 (B9): 10 series x 10 seeds x 110 units | 25,190.00 |
| Law 2b instance K2 and K3 on new pools | plan, section 12a: 12 cases (9 K2 classes and 3 gating K3 cases) x 200 seeds, for each of the 3 instances that change the series (W, F, D) | 16,488.00 |
| Law 2b instance K2 and K3 on saved pools | assumption: the instances that change only the statistic or the selection (Q, H, M, O4, E, B, R) reuse saved pools, with a 1-hour allowance | 3,600.00 |
| Law 2b instances, paired K4 | plan, section 12a: the K4 cost above for each of W, F, D | 29,400.00 |
| Law 2b instances, paired K5 | plan, section 12a: the K5 cost above for each of W, F, D, B, R | 125,950.00 |
| Known-answer tests, total | | 253,546.41 |
| Fit stage | 7 channels (plan, sections 5 and 8: GW H1 and L1, SEIS VBB and SP, Wind/WAVES Z and S, TESS one) x (32 segments, plan section 7, + 150 flow units, assumption) | 2,917.46 |
| Presence | plan, sections 5 to 7: (3 instruments x 6.5 + TESS x 5.5) pools x 32 segments x 4 (real, C2, C3, C4). Wind/WAVES is costed at N = 4,096, an upper bound | 7,328.00 |
| Arrow and profile transfers | reuse the presence pools | 0.00 |
| Scale flow | 4 instruments x 5 runs (plan, section 5) x 150 units (assumption) x 3 pools (real, C2, C3) | 20,610.00 |
| Confirmatory verdict run, total | | 27,938.00 |

The 150 flow units per instrument are an assumption: by the segment rule and the 7 aligned levels kept, an instrument has at most 7 x 32 = 224 units, and fewer where its record is short. One mode without an adverse outcome: 253,546.41 + 2,917.46 + 27,938.00 = 284,401.87 processor-seconds, about 79.0 processor-hours. Three modes: 853,205.61 processor-seconds, about 237.0 processor-hours.
Parts E and F of the code build (code commit `99533df`) give no new timings, so the measured costs above stay those of commit `71142c1`.
The Law 2b search adds, in the worst case where all three kinds of adverse outcome occur and every instance passes:
17,147.52 (new presence pools for W, F, D on 3 instruments, plan counts) + 77,287.50 (new flow pools for W, F, D, B, R on 3 instruments x 5 runs x 150 units, the last an assumption, x 3 pools) + 149,491.20
(G1 null replicates: 102 tests x 10 replicates x 64 pools, an assumption that a replicate stops after about 2 pools for each of 32 segments) = 243,926.22 processor-seconds per mode, about 67.8 processor-hours, and about 203.3 over three modes, and nothing when no adverse outcome occurs.

## 11a. Implementation readings fixed by Amendment 2

These readings were provisional choices of the code built for Amendment 1 (code commit `99533df`, items D1 to D18). Amendment 2 makes them plan text, with the changes stated.

- D1. Phi^-1 is the standard library `statistics.NormalDist(0.0, 1.0).inv_cdf` on the lower half of the rank table, reflected oddly for the upper half, so the scores of -x are exactly the negated scores of x.
- D2. An IAAFT iteration stops when the array produced by the rank step equals the array that entered the iteration. The random start counts as the first iterate. The cap is 1,000 iterations.
- D3. Standardisation uses the population divisor over the other 99 series. Zero spread means all other values are exactly equal. A zero-spread transfer feature entry is set to 0. A segment with zero spread at every lag gives no transfer feature (B8).
- D4. Replaced by B8: exact comparisons for exact quantities, and the tolerance |a - b| <= 1e-12 x max(1, |a|, |b|) for floats, in both the segment p-value and the transfer test.
- D5. A pattern is the tuple of dense ranks of the window (the rank of a value is the number of distinct window values below it), giving 13 patterns at order 3 and 75 at order 4.
- D6. An order-4 class frequency is the sum of the pseudocounted frequencies of its member patterns, (count + m/2) / (windows + 75/2) for a class of m patterns. The ninth class holds the 51 tied patterns.
- D7. The 13 terms of Sigma_hat are summed in sorted order, so x and -x give identical sums.
- D8. A transfer is adverse if fewer than 1/40 of the random detectors score below S_B(w_A) by more than the tie tolerance. No interpolated percentile is used.
- D9. The flow template is the mean of the units at each aligned level, each level counting equally, the same construction as the score, and is then scaled to unit length as in section 4.3. The scaling changes no p-value, since every random detector has the same entries as the template and so scales alike, except through the absolute floor of the tie rule (section 4.3) for scores below 1e-12.
- D10. The flow amplitude maps are applied to the whole stream before block averaging.
- D11. The window-length net N/2 cuts blocks of N/2 + 128 samples by the rule of section 7 with segment length N/2.
- D12. Inside a net run, C2 and C3 are made from the native segment and then put through the run's net. C4 uses the pooled fit-set values and the median fit-set periodogram at the native length, then the run's net.
- D13. An instrument that is both underpowered and has a failed control is reported as underpowered, with both facts recorded. Both statuses keep it out of V, so the outcome is the same.
- D14. The seed-rule fields are master|instrument|split|net|segment|purpose|index, with index 0 unless stated. One generator per key gives a whole series or a whole pool in order. A pool's key is that of its segment with purpose `surrogates`. Fields for each use:
  - K2: instrument `K2:<class>:<length>`, split `synthetic`, net `native`, segment the seed number, purpose `data` for the series and `surrogates` for its pool. The must-fail control (raw-value surrogates) uses the key of its class and length with purpose `surrogates`, and draws its raw-value surrogates from that generator.
  - K1: instrument `K1:<class>:<length>` with the K2 fields otherwise. The exp and cube versions and the comparison maps are maps of the plain draw and use its seed. The integer-valued series of B6 use `K1int:<class>:1024`. The tied waveform is fixed, and its pool uses `K1wave:4096`.
  - K3: the data draw uses instrument `K3:<case>:<length>`, split `synthetic`, net the use, segment the seed number, purpose `data`. Four uses have their own data draw: `native4096`, `native2048`, `placement` and `wlen2048`. The nets `bm2`, `sub2`, `q12` and `q8` are applied to the `native4096` draw.
  Each pool uses instrument `K3:<case>`, split `synthetic`, net the use, segment the seed number, purpose `surrogates`. The circular-shift control draws its shifts from the pool key of `native4096`.
  - K4: instrument `K4:<kind>` (kinds `A`, `B`, `C`, `S`, `Sr`), split `fit` or `verdict`, net `native`, segment the seed number, purpose `data`. A' uses `K4:Aprime:<tag>` with purposes `shuffle` and `block-surrogate` (index the block number). Random detectors use purposes `detectors-arrow` and `detectors-profile`, with net the run.
  Each segment's pool uses instrument `K4:<kind>:s<seed>`, split `fit` or `verdict`, net the run, segment the segment number, purpose `surrogates`.
  - K5 (B9): instrument `K5b:<case>`, split `fit` or `verdict`, net `native`, segment the seed number, purpose `data`. Random detectors use `detectors-flow`. Each flow unit's pool uses instrument `K5b:<case>`, split `fit` or `verdict`, net `native`, segment `flow-L<level>-q<unit>`, purpose `surrogates`.
  The whole-series surrogate that makes the IAAFT cascade starts from the generator of instrument `K5b:cascade_iaaft`, split `fit`, net `native`, segment the seed number, purpose `whole-surrogate`.
  - Controls: C2, C3 and C4 use purposes `C2`, `C3` and `C4` with the key of their segment (for C4, segment the series number). Law 2b instance F uses `law2b-F` and the G1 null replicates `law2b-null`.
  - Real data: instrument the instrument and channel, split `fit` or `verdict`, net the run, segment the segment number.
  - Draws not listed here follow the `data` and `surrogates` names above. The order of draws inside each generator, and the random-number calls used, are fixed by the generator source at the code commit recorded with the known-answer results. That commit's hash is recorded with every result, and any later change to a generator is a plan amendment.
- D15. For g and h, unit variance means a stationary AR(1) series with innovations of standard deviation sqrt(1 - c^2). The 7 null classes are standardised by their sample mean and standard deviation. The K2 control's flag point is evaluated at its own seed count (B11).
- D16. In K3 each seed draws a block of N + 128 samples and cuts it by the offset rule. The window-placement and window-length nets use independent draws of the same process, and native at 2,048 samples is its own draw. The nets block mean by 2, subsampling by 2 and the two quantizations are applied to the native 4,096-sample draw (D14).
The sawtooth takes the values k/64, k = 0 to 63 (peak to peak 63/64, standard deviation sqrt(4095/12)/64), and its noise has standard deviation half of that, 0.1443.
- D17. K4: A' as stated in section 10, with "reaches p at most 0.01" meaning in any run (replacing the builder's reading of the largest p over the runs, which made the control harder to trip). The K4 runs are the primary grid and the shifted grid. The sawtooth blind-spot streams are fresh draws, primary run only. K5: as in section 10 (B9).
A unit departs if at most 4 of its 99 surrogates have a sum of squared features at or above its own. The cascade's highest populated level is level 3.
- D18. K1 runs the whole pipeline at 1,024 samples and compares the normal scores at 4,096 and 2,048 samples, as section 10 states after B5.

## 12. Outcomes and what each would mean

The outcome is set by the procedure below, which maps every combination of results to exactly one outcome. `checks/check_outcomes.py` enumerates every combination (11,664,000 for T3, 11,664 for T1) and confirms this. TESS results are reported but do not enter the procedure, because TESS has no second sensor and cannot count toward support. The counting instruments are GW, SEIS and Wind/WAVES.

Inputs for T3:

- Known-answer tests: all of K1 to K6 pass, or not.
- Status of each counting instrument, one of five. Invalid: C2, C3 or C4 fails in the primary run. Underpowered: the primary run has fewer than 12 valid segments, or more than 25 percent of its selected blocks are invalid.
Present: the presence test passes at its Holm step, which requires the primary run and every applicable net run to pass under section 5, with no net underpowered. Net-dependent: the primary run alone passes under section 5 at the test's per-run level, but the presence test does not pass. Absent: otherwise.
- For each ordered pair of counting instruments, the arrow transfer is "pass" (passes at its Holm step), "adverse" (S_B(w_A) below the 2.5th percentile of its random detectors in every run) or "neither". The profile transfer is "pass" or "neither". A pair whose C5 control fails, or which is below the populated-feature floor of 4.3, is "neither".

Let P be the present instruments, Q the present or net-dependent ones, and V the instruments that are present, net-dependent or absent. A pair "passes both ways" if its result is "pass" in both directions, and likewise for "adverse both ways". The first rule that applies sets the outcome:

1. Invalid: some known-answer test fails.
2. Evidence against: at least 2 counting instruments are absent, or the arrow transfer is adverse both ways for at least 2 pairs inside V.
3. Supported, tested form: all 3 counting instruments are present, and the arrow transfer passes both ways for all 3 pairs.
4. Net-dependent: all 3 are in Q, fewer than 3 are present, and the arrow transfer passes both ways for all 3 pairs.
5. Partial: at least 2 instruments are present, and some pair inside P passes both ways on the arrow transfer, or passes both ways on the profile transfer while its arrow transfer is adverse in neither direction. An opposite arrow with a shared shape is not partial support.
6. Does not discriminate: at least 2 instruments are present, and no pair inside P meets the condition of rule 5.
7. Inconclusive: at most 1 instrument is present, at most 1 is absent, and at most 1 pair inside V is adverse both ways.

The scale-flow half of T1 has no presence test. Its inputs are the known-answer tests, whether each counting instrument is usable (not invalid for T3, and at least 12 segments at some flow level), and the transfer result for each ordered pair ("pass", "adverse" or "neither", defined as for the arrow transfer). With V the usable instruments, the first rule that applies sets the outcome:

1. Invalid: some known-answer test fails.
2. Evidence against: the transfer is adverse both ways for at least 2 pairs inside V.
3. Supported, tested form: all 3 instruments are usable and all 3 pairs pass both ways.
4. Partial: at least 1 pair inside V passes both ways.
5. Does not discriminate: at least 2 instruments are usable and no pair inside V passes both ways.
6. Inconclusive: at most 1 instrument is usable.

What the outcomes mean. Supported: the signature is shared and survives the essay's own nets, within this scope. Net-dependent: shared, but not an invariant by the essay's standard. Partial: shared in part, not universal. A pass on the profile transfer alone shows a shared shape of irreversibility, not a shared direction.
Does not discriminate: the instruments share only the generic fact of departing from surrogates, which holds for many unrelated nonlinear systems. Evidence against: at this scope the series show no shared time arrow, or opposite forms. Inconclusive and Invalid: no conclusion.

For line 16 as a whole: even full support for T3 and for scale flow leaves T2, T4 and the interference half of T1 untested. The strongest possible verdict from this run is "partial support for line 16, two transformations in their tested forms".
"Evidence against" for T3 would bear directly on line 16, because T3 is the one transformation the essay states as a formula that applies to any series.

## 12a. Transformations searched before an adverse outcome is final (Law 2b)

The rule. Law 2b, "Transformational Steelman (Morphism Before Dismissal)", identifier LAW2B_TRANSFORM_BEFORE_DISMISSAL.
The families and guards used here are defined by the reference specification: Foundation-0/cave-expedition, commit `80606f1`, `symbiosis/round10/arm5-transformational-steelman/TRANSFORMATIONAL_STEELMAN_REPORT.md`, lines 36 to 44 (the seven families, identifiers T1_GAUGE_SIMILARITY, T2_AFFINE_BREGMAN, T3_METRIC_CHART, T4_SPECTRAL_PSD_SHIFT, T5_SEMIRING_TROPICAL, T6_SUBSPACE_PROJECTION, T7_ORDER_DOMAIN_RESIDUAL),
lines 48 to 53 (the four guards and the maximum null false-pass rate of 1/10) and lines 95 to 104 (protocol statement).
The one-row statement in Aletheia version 2.0.0 (Foundation-0/aletheia, commit `0b60322`, `spec/LAWS_AND_GATES.md` line 14, on a branch under review with an open change request, not merged) is used for the G1 resolution condition null_total x max_null_rate >= 1. Its code port and the port's family identifiers are not used, and no outcome here depends on any verdict from it.
Where the texts differ, the stricter reading is used, with one exception: G3's residual gap, which the sampled translation replaces as stated under G3 below.
This section was reconciled with the published rule on 2026-11-22, before any data file was opened.

How it applies to a sampled test. The rule is written for exact claims: before a theorem or formula is closed as falsified, seven families of admissible transformations must be searched, and a final "falsified" needs an obstruction that survives all seven. This test is sampled. The rule does not say how its guards translate to sampled tests, so the translations below are ours and are labelled so.
The analogue of "closed as falsified" is the outcome "evidence against" of section 12, for T3 and for the scale-flow half of T1. No "evidence against" is recorded as final until the search in this section is complete. Other outcomes are not falsifications under the rule ("does not discriminate" and "inconclusive" correspond to the method's NOT_SHOWN, see section 12b) and are recorded unchanged.

An "evidence against" outcome arises in three ways (section 12): (a) at least two counting instruments absent, (b) the arrow transfer adverse both ways for at least two pairs, (c) the scale-flow transfer adverse both ways for at least two pairs. For each, every one of the seven families is searched below, either with a transformation fixed now or with the reason it has no admissible instance here.

### Families and instances

| Family | (a) presence, per absent counting instrument | (b) arrow transfer, per adverse pair | (c) scale-flow transfer, per adverse pair |
|---|---|---|---|
| T1_GAUGE_SIMILARITY | W: zero-phase whitening applied first, as a change of coordinates, with all other nets on top. Recipe: take the discrete Fourier transform X(f) of the native segment, divide it by the square root of the running median of |X(f)|^2 over 33 neighbouring frequencies (the window reflected at both ends of the frequency range), set the zero frequency to 0, and transform back | W, applied to both instruments' series before features | W, applied before the flow |
| T2_AFFINE_BREGMAN | Q: Sigma_hat replaced by the Bregman divergence with the quadratic generator, the sum over patterns of (p(pi) - p(rev pi))^2. It can order two series oppositely to the log-likelihood ratio, so it is a real alternative. (An affine map with positive slope, applied alike to the statistic of a series and its pool, changes no rank, so it has no instance) | Q: a_k replaced by p(pi_k) - p(rev pi_k), which transforms like a_k under reversal and polarity flip, then u, m1, m23 as before | none: the flow features are class frequencies standardised against their pool, with no divergence and so no generator to change, and an affine map with positive slope applied alike to a unit and its pool leaves the standardised features unchanged |
| T3_METRIC_CHART | H: Sigma_hat replaced by the Hellinger form, the sum over patterns of (sqrt p(pi) - sqrt p(rev pi))^2 | H: a_k replaced by sqrt p(pi_k) - sqrt p(rev pi_k), which transforms like a_k under reversal and polarity flip, then u, m1, m23 as before | H: class frequencies replaced by their square roots before standardisation |
| T4_SPECTRAL_PSD_SHIFT | F: independent Gaussian noise with standard deviation 1/1000 of the segment's standard deviation added before every other step (a white floor in the spectrum) | F | F |
| T5_SEMIRING_TROPICAL | M: the largest absolute log ratio over pattern pairs, the max-plus limit of the log ratios (not of the terms p ln(p/p') of Sigma_hat) | M: the score w_A . f replaced by its max-plus form, the largest of w_k f_k, with random detectors of the same form | B: block maxima of 2 replace block means in the flow (the max-plus coarse-graining) |
| T6_SUBSPACE_PROJECTION | D: first differences of each segment (quotient by constant offsets), and O4: order-4 patterns at lags with 3 tau at most n/4. O4 is a refinement, not a projection (order-3 patterns are a quotient of order-4 ones), so it fits this family only loosely | D | D |
| T7_ORDER_DOMAIN_RESIDUAL | E: the claim restricted to the event-rich domain, verdict segments whose tail spread (q99.9 - q0.1)/(q75 - q25) of the native values exceeds the median over the instrument's fit segments. A quantile q_p is the order statistic of rank ceil(p n), with no interpolation, and the ratio, the median and "exceeds" are computed exactly as rationals | E. (Normal scores before surrogates are now part of every confirmatory test, so they are no longer a separate instance here) | R: normal scores of the ranks before block averaging |

Notes. The arrow test's time-odd and time-even split (section 4.3) is itself a T6 projection inside the confirmatory plan. The tail spread used by E depends only on the multiset of values, which an IAAFT surrogate shares exactly with its segment, so choosing segments by it cannot shift any segment's p-value. If E leaves fewer than 12 valid segments, its test counts as not passing.
An earlier draft listed a signed arrow between Wind/WAVES and TESS. It is dropped: TESS never enters the outcome procedure, so it could not change any recorded outcome and would only cost multiplicity.

### Counting and multiplicity

Instances: 8 per absent counting instrument for (a) (W, Q, H, F, M, D, O4, E), 3 instruments, 24 tests. 7 per ordered pair for (b) (W, Q, H, F, M, D, E), 6 ordered pairs, 42 tests. 6 per ordered pair for (c) (W, H, F, B, D, R), 6 ordered pairs, 36 tests. The family has 102 tests under Holm at 0.05, smallest threshold 0.05 / 102 = 0.000490.
When to compute. A fixed rule, with no choice: whenever an adverse outcome of kind (a), (b) or (c) occurs, every instance listed for that kind is computed for every triggering item, in the same verdict run. Instances for kinds that did not occur cannot change any outcome and are not computed. Every one of the 102 tests that is not computed enters the Holm procedure with p = 1.
Each instance uses the nets and Bonferroni split of its paired test (up to 8 runs for presence, 3 for the arrow transfer, 5 for the scale flow). Smallest per-run levels are 6.1e-5 for presence, 1.6e-4 for the arrow transfer and 9.8e-5 for the scale flow. Presence runs can reach them (K >= 6 of 12, 7 of 16, 8 of 24, 9 of 32).
Transfer instances use R = 99,999 random detectors (smallest p 1e-5) and need at least 8 jointly populated features with permutations only, or 6 with signs. Below these floors a test counts as not passing. With these, no test in the family is unable to reject.

### Guards (Law 2b, G1 to G4)

G1, non-vacuity and null resolution (reference line 50, with the resolution condition worded as in the version 2.0.0 laws table). Every instance is a non-degenerate map (rank at least 1: W, F and R are invertible on the segment, D has rank n - 1, H and M are injective on pattern frequencies, B and O4 are non-constant, E keeps at least 12 segments or does not pass).
An instance that passes on the real data is then run on 10 independent null replicates (fresh C2 surrogate-as-data sets, seeds from the master rule with purpose "law2b-null"). An instance that does not pass cannot rescue, so its null replicates would change nothing and are not run. An instance whose test passes on more than 1 of its 10 replicates is vacuous and cannot rescue.
That is a null false-pass rate of at most 1/10, and the resolution condition holds: 10 x 1/10 = 1 >= 1.
A replicate's evaluation stops at its first failing run. Before data are opened, each instance passes, with the instance applied and at window length 4,096 only, K2 with 200 seeds per class, K3 on the native net, and the paired K4 or K5 test. For the 8 presence instances K2 has 56 null checks (7 classes) and 16 checks of the reversible classes.
A null class is flagged at 24 or more of 200 (P(Binomial(200, 0.05) >= 24) = 7.2e-5, at most 0.01/56), so a calibrated set is flagged anywhere with probability at most 0.004. A reversible class is flagged at 36 or more (P(Binomial(200, 0.10) >= 36) = 3.9e-4, at most 0.01/16).
With 200 seeds these checks find only large miscalibration (a null rate of 0.10 is caught with probability 0.20 per check). They are an extra guard on top of G1.
As the reference requires, a rescue also needs every transformed target to hold: one instance must pass for every item that triggered the adverse outcome (every absent counting instrument for (a), every adverse pair for (b) or (c)).

G2, global scope and degrees of freedom (reference line 51). Every instance is fixed by this text before any verdict file is opened.
Counting every constant in its definition as a degree of freedom: W 1 (the 33-bin smoothing width), Q 0, H 0, F 1 (the 1/1000 floor), M 0, D 1 (the difference lag), O4 1 (the order), E 5 (the four quantile levels 99.9, 0.1, 75 and 25, and the threshold, fitted on fit data only), R 0, B 0.
The held-out constraints are the verdict segments a test is judged on, at least 12 by the floors above. So transform_dof is at most 5 and held_out_constraints at least 12, and 5 < 12 holds for every instance.

G3, scope-delta ledger, written now (reference line 52). A passing instance never relabels the confirmatory claim as met. It is recorded as a transformed core with the scope change below.

| Instance | Preserved core | Modified hypothesis (scope change if it passes) |
|---|---|---|
| W | forward and backward path statistics differ | in the whitened coordinates, not in the raw ones |
| Q | forward and backward path statistics differ | measured by a squared difference of pattern probabilities, not by the essay's log-likelihood ratio |
| H | forward and backward path statistics differ | measured by a Hellinger distance, not by the essay's log-likelihood ratio |
| F | forward and backward path statistics differ | after a white floor of 1/1000 of the standard deviation is added |
| M | a pattern pair is asymmetric | for the most asymmetric pair, not on average |
| D | the increments have a time arrow | in increments, not in levels |
| O4 | ordinal path statistics differ from their reverse | at order 4, not order 3 |
| E | forward and backward path statistics differ | only in the event-rich half of the segments |
| R | the flow profile is shared | with block averaging applied to rank-based normal scores, not to raw amplitudes |
| B | the flow profile is shared | under coarse-graining by maxima, not means |

The reference asks a bounded core to state a maximum residual gap and to stay within it. The sampled translation has no numeric residual gap: a transformed test either passes at its level, with all its nets, its controls and the null check of G1, or it does not.
What replaces the gap is the pre-written scope change above, which is the whole of what the claim gives up if the instance passes, together with the reported pair of p-values (confirmatory and transformed). A passing instance is always recorded as a bounded core, never as exact.

G4, obstruction before a final "evidence against" (reference line 53). All seven families are searched for each adverse type, T2 with the exact reason given in the table.
The adverse outcome is recorded as final only if no instance passes and the following obstruction holds under the confirmatory run and every instance (our sampled analogue of a transform-invariant obstruction): for (a), each absent counting instrument's presence test fails, so its series shows no time arrow beyond its surrogates at the tested orders, lags and nets, in every listed representation.
For (b) and (c), the transfer is adverse both ways, not merely failing, for the same pairs in every instance.
The exact limit of section 4.3 (a polarity-free statistic cannot tell time reversal from polarity flip in a series unchanged by both together) does not qualify as an obstruction. It obstructs the test's ability to see an arrow, not the claim. Such a series gives "neither" on the arrow test, never "adverse", so it cannot trigger outcome (b), and it is reported as a limit (section 13).

Recording. Each "evidence against" ends in exactly one of three states:

- Transformed core: one instance, not vacuous under G1, passes for every item that triggered the outcome. Recorded as "evidence against at the confirmatory level, transformed core passed under instance k", with that instance's ledger row, and the instance becomes a candidate for a new pre-registration on new data.
- Final: no instance passes for any triggering item and the obstruction above holds. Recorded as "evidence against, final", after the advocate review of section 12b.
- Unresolved: anything else, for example an instance that passes for one absent instrument but not the other. Recorded as "evidence against at the confirmatory level, Law 2b search unresolved". It is not final and it is not a rescue.

When more than one kind triggers at once, each kind is searched with its own instances and ends in its own state. Each kind alone is enough for rule 2 of section 12, so the outcome is "evidence against, final" if any triggered kind is final, with the other kinds' states recorded beside it.
If none is final, it is "transformed core" when rule 2 no longer applies once the rescued items of every kind in that state are treated as present or not adverse, and "unresolved" otherwise.

Effect on the chance of each outcome: none on supported, partial or the other non-adverse outcomes, since these tests cannot produce them. They lower the chance that an adverse outcome is recorded as final. The family is closed with respect to results: nothing is added, removed or tuned after any result is seen.
Any later change, logged with its date, is allowed only before any data file is opened.

## 12b. Requirements of Aletheia version 2.0.0

Source of the requirements: Foundation-0/aletheia, commit `0b60322`, `spec/LAWS_AND_GATES.md` and `spec/proposals/OWN_TERMS_FIRST.md`, version 2.0.0, on a branch under review with an open change request (pull request 1, not merged).
Each requirement below is stated in this plan's own words and checked by this plan's own analysis code and second checker (section 11). An outside review of the branch found that its code checks less than its text says, so no guarantee here rests on that code. Running the branch's tools is an extra. A later change to the branch does not change any threshold in this plan.

| Requirement | Where it stands in this plan |
|---|---|
| Law 1, active portal keeper | a rule for running research teams, not for a fixed test. Anomalies found here go to a new pre-registration (section 12a, recording) |
| Law 2, steelman before falsify | sections 2 and 3 |
| Law 2b, transformational steelman | section 12a |
| Law 3, independent verification across bases | second checker with no shared code (section 11) |
| Law 4, N0 by default, oracle class and scope stated | header and section 3. Every result of this test is labelled N0. Gate 9's mechanism-first prior-art search is not part of this test. Any later label above N0 needs that search first: the mechanism restated in plain terms and in those of at least two neighbouring fields, full texts searched and read, and the record kept |
| Law 5 and Gate 5, cross-domain link | the transfer tests are the link: typed objects (aligned feature vectors), an explicit map (identity after the level shift), a closure defect beating matched random detectors (the mean standardised score against theirs), and predictive transfer (a template fixed on A, tested on B) |
| Own terms first, Phase 1 and Phase 2 kept apart | Phase 1 only. No comparison with existing theory is made (section 3) |
| OTF-TIGHT-01, pre-pinned nets and Bonferroni budgeting | nets fixed in section 5, each test's level split across its runs |
| OTF-TIGHT-03 and Rule 5, IID and spectrum-preserving nulls with a margin, negative controls with a ceiling | in every run: margin 1/4 over C2 (spectrum-preserving), C3 (IID shuffle) and C4, and control shares at most c_max(S) (sections 5 and 6) |
| OTF-TIGHT-04, operational utility of new symbols | no new symbols are proposed. The features a1, s, u, m1 and m23 are named combinations of pattern counts |
| Rule 6, return to author when nothing is measurable | the interference half of T1, T2 and T4 (section 4), recorded as RETURN_TO_AUTHOR_FOR_DEFINITION |
| OTF-TIGHT-02, orthogonal model ladder | applies to a remainder test, so to Arm B, not to this test. Noted in `ARM_B_OUTLINE.md` |
| Gate 8, hashed pre-registration, second reader, misses kept | the plan and this amendment are committed before any file is opened. The second checker reproduces every outcome. All results, misses included, are reported |
| Gate 8, subspace latch for adaptive fits | templates and tau0 are fitted on the fit set and judged only on the verdict set, so no audit is read after adapting on the same data |
| Gate 10, advocate for adverse or narrowing findings | the advocate is a reviewer who wrote neither this plan nor its code. The authors of the essay's claim are invited first, on the pull request that holds the result, and are given the adverse or narrowing outcome with its full record (data hashes, code commit, every run, the Law 2b search) before it is called final. If they do not respond within seven days, an independent reviewer takes the role. "Respond" means a written reply on the pull request. The independent reviewer is someone who took no part in writing or checking this plan, its code or its results, and who shares no code with either. The reviewer is named in the results pull request before being shown the outcome. If a conflict of interest is recorded in the results pull request, the repository owners may name a replacement who meets the same conditions, before the outcome is shown to that person. "Narrowing" outcomes are partial, net-dependent, does not discriminate and evidence against, which all go to the advocate. Invalid and inconclusive carry no finding and do not. A ruling of "stands_narrowed" is recorded with the narrower statement the advocate gives, and the outcome is reported in that narrower form. The advocate may point to a listed Law 2b transformation that was not run, or to a defect in the analysis. They may not add transformations or change thresholds. Their ruling ("stands", "stands_narrowed" or "falls") and what was done about it are recorded with the outcome. A defect they find is handled by the rules of section 11, and "falls" means the outcome is not recorded as final |
| R1 to R7 gate-integrity contracts | section 11 |
| Verdict names | Supported maps to VERIFIED within scope, net-dependent and partial to PARTIAL/FRAGILE, a final "evidence against" to INVARIANT_FALSIFIED under Law 2b, does not discriminate and inconclusive to NOT_SHOWN. Invalid gives no verdict |
| CS-08, fixed compute cap when comparing arms | not applicable: no arms are compared |

## 13. What this test cannot show

- It does not compare anything with physical theory, and it cannot say what causes a signature.
- It cannot separate the source from the instrument chain. Any causal filter in acquisition or calibration (GW high-pass and calibration filters, on-board decimation filters, TESS calibration, receiver electronics) can create a time arrow from a non-Gaussian input. C6 gives a partial contrast only.
- Ordinal patterns of order 3 and 4 see only part of the path statistics. Absence here means absence at these orders and lags, not reversibility of the full process.
- Four instruments, one star, two days of Mars data, sixteen days of radio data and two 4,096-second strain stretches are a small sample of "raw telemetry". Neural arrays are not covered.
- Where only presence passes, the result cannot show "the same transformation", only a shared departure from linear Gaussian behaviour.
- The polarity-free arrow test cannot see the arrow of a series whose statistics are unchanged by time reversal composed with polarity flip (section 4.3). For such series, time direction and sensor polarity cannot be told apart without knowing the polarity.
- The surrogate null is "an increasing map of a linear Gaussian process", which is narrower than "reversible". A reversible series of another kind can show segment-level departures. K2 measures this rate for two such series and stops the run if it is clearly above 0.10, but it cannot cover every kind.
- Lengths below 2,048 samples are not tested. A signature visible only at short windows, or a Wind/WAVES record whose cadence does not allow 2,048-sweep blocks, is outside this run.
- The scale flow depends on amplitudes through the block means. Its invariance under increasing maps is tested on two fixed maps, not proved for all maps. Presence and the arrow and profile transfers are exactly invariant under increasing maps.
- Transformations 2 and 4 and the interference half of 1 are not tested. Their status is a request to the authors for definitions, not a falsification.
