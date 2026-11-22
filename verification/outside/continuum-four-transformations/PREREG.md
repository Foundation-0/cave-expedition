# Pre-registration: a raw-data test of the four-transformations claim

Status: plan only. No data fetched, no code run. The commit that adds this file fixes the plan.
Claim type: sampled. Novelty: N0 (the statistics used here are known methods).

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

Scope: single-channel series from the four instruments in `DATA_REQUEST.md`, windows of 4,096 samples, lags of 1 to 512 samples. Neural and other biomedical recordings are left out of this first run.
Comparison with existing physical theory is not part of this test. The statistics are judged on their own terms, against surrogates and generated noise.

## 4. Operational definitions, one transformation at a time

Two shared tools. An ordinal pattern is the order of the values in a short window. For three values (a, b, c) with b < c < a the pattern is written 201, meaning the first value is largest, the second smallest, the third in the middle.
Ordinal patterns do not change under any strictly increasing change of the values, so units, offsets, gains and amplitude scales drop out. This is the "labels and grids stripped" step of the essay, made exact.
A surrogate is a scrambled copy of a series that keeps its power spectrum and its set of values but destroys everything else. We use the iterative amplitude adjusted Fourier transform method (IAAFT, Physical Review Letters 77, 635, 1996).
A linear Gaussian process, or any strictly increasing function of one, looks the same forwards and backwards in time. So an IAAFT surrogate is a series with no time arrow by construction.

### 4.3 Irreversibility (transformation 3): main test

Measurable form. The essay's formula averages to the Kullback-Leibler divergence between the statistics of forward paths and of reversed paths. On ordinal patterns of order d = 3 at lag tau:

```text
Sigma_hat(tau) = sum over patterns pi of p(pi) * ln( p(pi) / p(rev pi) )
p(pi) = (n(pi) + 1/2) / (sum of n + 3)
```

Here n(pi) counts windows (x_t, x_{t+tau}, x_{t+2tau}) with pattern pi, and rev pi is the pattern of the reversed window (012 and 210 form a pair, 021 and 120, 102 and 201). Windows with tied values are left out and their number is recorded.
Sigma_hat is zero in expectation for a reversible series and positive for an irreversible one.

Two exact facts make this statistic fit the essay's standard. Pattern counts are unchanged by any strictly increasing map. Flipping polarity (x to -x) relabels patterns by a bijection that commutes with reversal, so Sigma_hat is unchanged.
At the level of whole paths, the true divergence is also unchanged by any invertible filter that commutes with time reversal, such as a zero-phase whitening filter. The finite-order estimate is not exactly invariant under filtering, which is why whitening is tested as a net.

Per-segment statistic. Lags tau = 2^j for j = 0 to 9 (1 to 512 samples). Each segment gives a pool of 100 series: the real one and M = 99 IAAFT surrogates.
For every series in the pool and every lag, Sigma_hat is standardised by the mean and standard deviation of the other 99 series in the pool. T is the largest standardised value over the ten lags.
The segment p-value is (1 + number of surrogates with T at least the real T) / 100. Values within 1e-12 relative of each other count as ties against the real series. This handles the ten lags inside each segment.

Presence in an instrument. S verdict segments give S p-values. K is the number with p at most 0.05. Under the null each segment has probability exactly 5/100 of this.
The instrument p-value is the upper tail P(Binomial(S, 0.05) >= K), computed in exact rational arithmetic. Order d = 4 is computed and reported but is not part of the verdict.

Sameness (transfer). For each segment and lag level, three features that do not depend on instrument polarity:

```text
a1 = ln( n(012) / n(210) )   a2 = ln( n(021) / n(120) )   a3 = ln( n(102) / n(201) )   (counts + 1/2)
u  = a2 - a3                 changes sign under time reversal, unchanged by polarity flip
m1 = |a1|,  m23 = |a2 + a3|  magnitudes of the parts whose sign depends on polarity
```

Under polarity flip (a1, a2, a3) becomes (-a1, -a3, -a2), so u is a time arrow that does not depend on which way the sensor is wired. Each feature is standardised against the pool, as above.
Lag levels are aligned across instruments by each instrument's own time scale: tau0 is the median, over fit segments, of the smallest lag at which the autocorrelation of the rank-transformed segment drops below 1/2 (capped at 512). The aligned level is j minus round(log2 tau0).
Levels -4 to +5 are kept, giving 30 features. A level outside a series' range is set to 0.
The template w_A is the mean feature vector over instrument A's fit segments, scaled to unit length. The score of a series is w_A dotted with its features.
On instrument B's verdict segments, AUC_B is the average over segments of the fraction of surrogates the real series outscores (ties count one half).
Matched random detectors are R = 9,999 random permutations of the entries of w_A. They keep the same weights, signs and form. The transfer p-value is (1 + number of permuted templates with AUC_B at least that of w_A) / 10,000.
This compares the arrangement of the template, not just "irreversible or not". A plain irreversibility signal in B helps permuted templates as much as the real one.

### 4.1 Subtractive selection (transformation 1)

Interference and stationary phase. The essay writes a stationary-action condition. A single raw series has no action functional, and the essay gives no rule to build one from data.
Status: needs the authors' operational definition. Nothing is tested for this half.

Scale flow. The essay says that under repeated coarse-graining "microscopic accidents die off" and disparate systems are driven into the same classes at fixed points. A measurable form needs no physics:

- The flow is block averaging by 2, applied to the whole valid stretch of a file, levels l = 0, 1, 2 and so on, as long as a level still gives at least 12 segments.
- At each level, segments are cut as in section 7. The feature vector is the frequency of ordinal patterns of order 4 at lag 1, summed over the 8 classes of patterns that map to each other under time reversal and polarity flip, standardised against the pool of 99 IAAFT surrogates of that segment.
- These 8 features are unchanged by polarity and by time reversal, so this test measures time-symmetric structure beyond the spectrum. It does not overlap with the irreversibility test.
- Levels are aligned by intrinsic scale as in 4.3 (aligned level = l minus round(log2 tau0)), levels -3 to +3 are kept, 56 features.

"Dies off" alone does not discriminate. Averaging a short-memory series drives it towards a Gaussian series, so the departure from surrogates shrinks for almost any noise. Generated noise will be shown to do this (test K5).
So the decay is reported but is not counted as evidence. The verdict for this half rests only on sameness: the transfer test of 4.3, applied to the 56 flow features.

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
| Sampling rate | block mean by 2, block mean by 4, plain subsampling by 2 | lags limited to fit the shorter segment |
| Quantization | 12 bits and 8 bits, uniform bins over the segment's 0.1 to 99.9 percent range | tied windows dropped and counted |
| Amplitude map | strictly increasing maps, polarity flip | exact code checks, not statistical runs (K1) |
| Zero-phase whitening | divide the Fourier transform by the square root of a 33-bin running median of the periodogram | true path divergence is invariant, the estimate may move |
| Window placement | block grid shifted by half a block | new segments |
| Window length | 2,048 and 8,192 samples | where the data allow 12 or more segments |
| Instrument | second channel: L1 for H1, SP for VBB, S antenna for Z antenna | TESS has no second channel in this run |

Presence counts for an instrument only if the primary run and every applicable net run each pass at the corrected level of section 9. The instrument's presence p-value is the largest p over the primary run and its net runs. This is an intersection test, so requiring all nets adds no false positives.
If a net version yields fewer than 12 valid segments, that net is "underpowered" for that instrument and the instrument is marked net-incomplete.
If more than 20 percent of a segment's windows are tied, the segment counts as not rejecting.
For the transfer tests, the nets applied are the instrument net and window placement, and the transfer p-value is the largest over the primary and these runs.

## 6. Controls and what "absent" means

| Control | Built from | Absent means |
|---|---|---|
| C1 IAAFT surrogates | each segment | reference pool inside every test |
| C2 Surrogate as data | one fixed surrogate per verdict segment, run through the whole pipeline with its own 99 surrogates | K below the binomial 1 percent excess point (K < 4 when S = 12, K < 6 when S = 32) and K/S at most 0.10 |
| C3 Shuffle | random permutation of each verdict segment | same rule as C2 |
| C4 Generated noise | 32 series per instrument with the fit-set median periodogram and fit-set value distribution | same rule as C2 |
| C5 Transfer on surrogates | transfer test with B's C2 series in place of B | transfer p above 0.01 |
| C6 Instrument noise | TESS background flux (SAP_BKG). GW blocks containing the event time | descriptive, no pass or fail |

If C2, C3 or C4 fails for an instrument, the test is not calibrated there and that instrument's result is "invalid", whatever the real data give.
C6 is descriptive because "no known source" does not mean "no time arrow": the instrument chain can be irreversible itself. If instrument noise shows the same signature at the same strength, the report attributes it to the instrument chain, not to the source.

## 7. Segment rule

All blocks are fixed by position before any value is read. A block is N + 128 samples, N = 4,096, numbered from the start of the file (or channel).
With J complete blocks, k = max(1, floor(J / 32)). Blocks with index divisible by k are selected, and the first 32 selected are kept.
Inside each kept block, the N-sample segment starts at the offset in 0 to 128 that best matches the segment's ends (smallest sum of the squared jump between first and last value and the squared jump between first and last slope). This limits a known IAAFT artefact and uses the same rule everywhere.
Validity, decided from flags and sample times only: GW, every second has the DATA and CBC_CAT1 bits set, no hardware injection bit, no missing value. SEIS, no gap or overlap in sample times, no sample at full scale. Wind/WAVES, one receiver mode across the block, no fill values, series indexed by sweep. TESS, QUALITY equal to 0 and finite flux on every cadence.
An invalid selected block counts as a non-rejecting segment. It is not dropped from the denominator. If more than 25 percent of selected blocks are invalid, the instrument is underpowered for that net.
On-source extra: for GW only, the block containing the event time is analysed as a labelled extra and reported descriptively. It is not part of S.

## 8. Split between fitting and verdict

| Instrument | Fit set (may be inspected) | Verdict set (opened once) |
|---|---|---|
| GW strain | GW150914 4,096-second files, H1 and L1 | GW151226 4,096-second files, H1 and L1 |
| Mars seismometer | 2019 day 143, VBB and SP | 2019 day 207, VBB and SP |
| Solar radio | Wind/WAVES RAD2, 2015-01-01 to 2015-01-08 | 2015-07-01 to 2015-07-08 |
| Stellar photometry | TESS 20-second light curve, sector 38 | sector 65 |

The fit set fixes only these free choices: each instrument's tau0 and level shift, the transfer templates, and the matching of each instrument to a calibration class from K2. Every statistic, threshold and lag above is fixed by this document.
The verdict files are hashed on download and not otherwise opened until the fit results are committed. The verdict run is one run of the committed code, identified by its hash.

For Wind/WAVES the four channels used are those at positions round((q + 0.5) F / 4), q = 0 to 3, in the file's frequency list of length F. Segments from the four channels are pooled before the every-k rule.

## 9. Confirmatory tests, multiplicity and the smallest reachable p

The confirmatory family has 28 tests. Holm's step-down method controls the family-wise error rate at 0.05. The smallest Holm threshold is 0.05 / 28 = 0.00179.

| Test | Count | Smallest p reachable | Reaches 0.00179? |
|---|---|---|---|
| T3 presence, one per instrument (all nets must pass) | 4 | 0.05^S: 2.4e-16 at S = 12, 2.3e-42 at S = 32 | yes. Needs K >= 5 of 12, or K >= 7 of 32 |
| T3 transfer, ordered instrument pairs | 12 | 1 / 10,000 | yes |
| T1 scale-flow transfer, ordered pairs | 12 | 1 / 10,000 | yes |

Tests flagged now because they cannot reject at the family level, so they are descriptive only:

- One segment against its surrogates: smallest p is 1/100. It feeds the count K and is never used alone.
- The GW on-source block: smallest p is 1/100.
- An instrument with fewer than 12 valid segments: reported as underpowered.

The binomial tail assumes segments are independent given the null. The every-k spacing keeps segments apart (128 seconds for GW, about 42 minutes for SEIS). As a robustness check, not part of the verdict, presence is recomputed on every second verdict segment.

## 10. Known-answer tests, run before any real data

All synthetic, with logged seeds. Real files are fetched only after these pass and their outputs are committed.

- K1 Exact checks. Integer counts are compared exactly.
  - Pattern counts are equal under strictly increasing maps (x^3 + x, exp, rank).
  - Counts of -x equal counts of x relabelled by complement. Counts of the reversed series equal counts relabelled by reversal. Sigma_hat is equal for x and -x.
  - Counts at lag 2 tau over even start points equal counts at lag tau of the series subsampled by 2.
  - A second implementation that shares no code must match every integer count.
- K2 Nothing found in noise. 200 seeds per class, N = 4,096.
  - Classes: white Gaussian, AR(1) with coefficient 0.5, 0.9 and 0.99, power-law noise with spectral slope 1 and 2, three sinusoids in white noise. Each class also passed through exp and through a cube.
  - The per-segment rejection rate at 0.05 must be at most 0.086 (the 99 percent binomial bound for 200 draws). A class above it is flagged.
  - Each instrument is matched to the class nearest in log-log spectral slope of its fit-set median periodogram over the central decade of frequencies. An instrument matched to a flagged class is marked not calibrated before verdict data are opened.
- K3 Planted structure found, 200 seeds per case.
  - Exponential shots (instant rise, decay over 10 samples, rate 0.01 per sample, height 3 background standard deviations) in AR(1) background with coefficient 0.9.
  - The logistic map at r = 4 with Gaussian observation noise of 0.1 of its standard deviation.
  - A sawtooth of period 64 samples with white noise of half its amplitude.
  - Required: segment detection at least 80 percent on the native net, and at least 50 percent after block mean by 2 and after whitening.
- K4 Transfer.
  - Synthetic A: the shots of K3. Synthetic B: the same shots with power-law background of slope 1, sampled at half the rate, polarity flipped. Synthetic C: time-reversed shots (slow rise, instant fall).
  - A to B must give transfer p at most 0.001. A to C must give an AUC below the 2.5th percentile of permuted templates.
- K5 Scale flow.
  - Independent exponential values: the norm of the mean flow feature at the top level must be below half its level-0 value. This shows that decay alone does not discriminate.
  - A random multiplicative cascade: the norm at the top level must stay at least half its level-0 value.
  - Cascade to cascade after a monotone map must give transfer p at most 0.001. Cascade to shots must give transfer p above 0.05.
- K6 Gate checks.
  - Empty input, missing values, a constant series and a series shorter than N are rejected with explicit errors.
  - Each refusal has a must-fail input that trips it. Removing any refusal branch must make the test suite fail.

## 11. Seeds, code and reruns

Master seed 20261121. Every random draw uses a seed made from the first 16 hex digits of SHA-256 of the string `master|instrument|split|net|segment|purpose|index`, fed to numpy's default generator.
Every script must give identical output under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`. No bare `assert` on any validation path.
A second checker with no shared code recounts all patterns on the saved surrogate files (exact integer match required) and repeats the verdict with its own surrogates and seeds. If the two disagree on any outcome category, that outcome is recorded as unresolved.
Commit order: this plan, then the analysis code with K1 to K6 outputs, then the data manifest with hashes, then the verdict. Any change to this plan before the verdict files are opened is added as a dated amendment with its reason. Changes after that are not allowed, and a test changed after that is reported as exploratory.

## 12. Outcomes and what each would mean

Per transformation tested (T3, and the scale-flow half of T1). An instrument that is net-incomplete (TESS in this run, which has no second channel) is reported but does not count toward the three instruments needed for support.

| Outcome | Condition | Meaning |
|---|---|---|
| Supported, tested form | presence in at least 3 calibrated instruments with all nets, and transfer passes in both directions for every pair among them (for T1, transfer only) | the signature is shared and survives the essay's own nets, within this scope |
| Partial | presence in at least 2 instruments and transfer in both directions for at least one pair | shared in part, not universal |
| Does not discriminate | presence passes, but transfer is no better than permuted templates for every pair among the instruments with presence | the instruments share only the generic fact of departing from surrogates, which holds for many unrelated nonlinear systems |
| Net-dependent | primary passes but some net fails | not an invariant by the essay's standard |
| Evidence against | calibrated instruments with K3 power, presence fails in at least 2, or the transfer AUC falls below the 2.5th percentile of permuted templates in both directions for at least 2 pairs | at this scope the series show no shared time arrow (T3) or opposite forms |
| Invalid | C2, C3 or C4 fails, or K1 to K6 fail | no conclusion |

For line 16 as a whole: even full support for T3 and for scale flow leaves T2, T4 and the interference half of T1 untested. The strongest possible verdict from this run is "partial support for line 16, two transformations in their tested forms".
"Evidence against" for T3 would bear directly on line 16, because T3 is the one transformation the essay states as a formula that applies to any series.

## 13. What this test cannot show

- It does not compare anything with physical theory, and it cannot say what causes a signature.
- It cannot separate the source from the instrument chain. Any causal filter in acquisition or calibration (GW high-pass and calibration filters, on-board decimation filters, TESS calibration, receiver electronics) can create a time arrow from a non-Gaussian input. C6 gives a partial contrast only.
- Ordinal patterns of order 3 and 4 see only part of the path statistics. Absence here means absence at these orders and lags, not reversibility of the full process.
- Four instruments, one star, two days of Mars data, sixteen days of radio data and two 4,096-second strain stretches are a small sample of "raw telemetry". Neural arrays are not covered.
- Where only presence passes, the result cannot show "the same transformation", only a shared departure from linear Gaussian behaviour.
- Transformations 2 and 4 and the interference half of 1 are not tested. Their status is a request to the authors for definitions, not a falsification.
