# Amendment 1 to the pre-registration

Status: draft amendment. It changes `PREREG.md` as fixed at commit `24d7757309b5b6b7b5179be2a65387af58fd5f9b`. Line numbers below refer to that commit.

## Timeline

1. 2026-11-21: plan fixed at commit `24d7757` (draft PR #6).
2. 2026-11-22, 04:25:04 to 04:28:56 UTC: all 26 files in `DATA_REQUEST.md` downloaded with the project's approval. Every byte count matches the request. SHA-256 and fetch time of each file are in `FETCH_MANIFEST.tsv`. None was opened or parsed. Each was read once as raw bytes to compute its hash.
3. 2026-11-22, 05:54:09 UTC: review of the plan by the authors of the claim under test: https://github.com/Foundation-0/cave-expedition/pull/6#pullrequestreview-6010617857
4. No data file has been opened, parsed or decompressed, and no statistic has been computed on real data.
5. 2026-11-22, 07:34 UTC: the code built to the frozen plan (Foundation-0/cave-expedition commit `71142c1`, draft PR 8) recorded its known-answer results on synthetic series: four of the six tests failed (A12).
6. 2026-11-22: section 12a reconciled with the published text of the project's rule Law 2b, and the plan checked against Aletheia version 2.0.0 (a branch under review), before any data file was opened.
7. This amendment was made after the download and before any file was opened.

Where the file-specific numbers in this amendment come from. None was read from a downloaded file.

- TESS cadence counts (115,338 for sector 38 and 120,486 for sector 65): an upper bound from sector duration at 20-second cadence, before gaps and flags.
They are computed in `checks/check_budget.py` as (t_max - t_min) x 86,400 / 20, rounded down, where t_min and t_max are the catalog start and end times (MJD) of the 20-second observations in MAST's observation records, returned by a MAST API query (service Mast.Caom.Filtered) on 2026-11-21, before any download.
File sizes alone give a slightly different bound under an assumed file layout (for example 115,344 rows for sector 38 with 100-byte rows and 11 non-table blocks, as the clean-room check found).
The conclusions that use these counts follow from sector length alone: flow level 2 needs 202,752 samples, more than any 27- to 28-day sector holds at 20 seconds, so the highest level is 1 and at least 5 of 7 aligned levels are empty, and level 1 gives 13 and 14 blocks.
- Radio cadence of about 33 seconds: an illustration, not a measurement, from the archive listing sizes (about 8 MB per daily file), assuming 256 frequency channels and three 4-byte values per channel per sweep, with no compression. The channel count is an assumption taken from the archive's description of the older RAD2 product.
Daily sizes range from 6.40 to 8.81 MB, so the cadence is not constant.
The plan does not depend on this figure: the real cadence, and from it the Wind/WAVES window length, is read from the fit files under the rule in section 8.

Deviation from the plan, recorded here. Section 10 (line 202) and `DATA_REQUEST.md` (step 1 of the pinning list) said files would be fetched only after the analysis code and the known-answer outputs were committed. The files were fetched before that. They were hash-pinned on arrival and none has been opened, so every choice in this amendment was made without access to their contents.
The commit order in section 11 is updated to match.

## How each item was checked

Every check is a script in `checks/`, run under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error` with identical output in all three modes (`checks/run3.sh`). Exact checks use integers, booleans and `fractions.Fraction` only. Two checks are sampled on synthetic series with fixed seeds stated in their output. No real data were read.

| Script | Kind | What it checks |
|---|---|---|
| `check_binomial.py` | exact | control rule, K2 cutoffs and their power, Holm thresholds, smallest p of template tests |
| `check_symmetry.py` | exact | action of polarity flip, time reversal and both on the order-3 features, and a sawtooth |
| `check_endmatch.py` | exact | segment offset choice under increasing maps and polarity flip |
| `check_budget.py` | exact | segment budgets for TESS, Wind/WAVES, window lengths and the Arm B outline |
| `check_outcomes.py` | exact, exhaustive | one outcome for every result state, and the Wind/WAVES channel rule |
| `check_compute.py` | exact arithmetic on stated counts | the compute estimate of A12 |
| `sim_features.py` | sampled | features of the K3 shot process, tied windows after quantization |
| `sim_iaaft_maps.py` | sampled | whether the surrogate pool changes under polarity flip and increasing maps |
| `sim_iaaft_spread.py` | sampled | how far segment p-values move under increasing maps, over two sets of 12 segments (run with `run3par.sh`, which runs the three modes at once) |

Each change states which way it moves the chance of the outcomes it affects. Where two options were equally defensible, the stricter one was kept.

## A1. Control rule (review item PREREG-01a): accepted as proposed

Raised by: the review (https://github.com/Foundation-0/cave-expedition/pull/6#pullrequestreview-6010617857).

Old text, line 150 (C2 row, used by C3 and C4):

```text
K below the binomial 1 percent excess point (K < 4 when S = 12, K < 6 when S = 32) and K/S at most 0.10
```

New text:

```text
K below the binomial 1 percent excess point, the smallest k with P(Binomial(S, 0.05) >= k) at most 0.01 (K < 4 when S = 12, K < 5 when S = 24, K < 6 when S = 32)
```

Reason. The ratio clause binds before the binomial clause at every S tested, so the stated 1 percent level was dead text. With a perfectly calibrated pipeline the old rule invalidates one control with probability 0.118360 at S = 12 and 0.073805 at S = 32.
For one instrument with three independent controls that is 0.314711 and 0.205477, and the chance that at least one of three instruments is invalid is 0.678173 and 0.498444. With the binomial rule alone the per-instrument figures are 0.006694 and 0.013736. These reproduce the review's numbers to rounding.

Check: `check_binomial.py`, section PREREG-01a.

Effect: a calibrated instrument is far less likely to be marked invalid, so the chance of every outcome that needs valid instruments rises (supported, partial, evidence against), and the chance of "inconclusive" falls.

## A2. Calibration cutoff in K2 (review item PREREG-01b): diagnosis accepted, different fix

Raised by: the review (https://github.com/Foundation-0/cave-expedition/pull/6#pullrequestreview-6010617857). The change in the number of draws comes from this amendment's own check.

Old text, lines 209 and 211:

```text
- K2 Nothing found in noise. 200 seeds per class, N = 4,096.
  - The per-segment rejection rate at 0.05 must be at most 0.086 (the 99 percent binomial bound for 200 draws). A class above it is flagged.
```

New text:

```text
- K2 Nothing found in noise. 1,000 seeds per class at each window length.
  - A class is flagged if 68 or more of its 1,000 segments have p at most 0.05. 68 is the smallest k with P(Binomial(1000, 0.05) >= k) at most 0.01 (the tail at 68 is 0.0074).
```

This text was changed again by A12 (9 classes) and A13 (two lengths, flag points 74 and 129, a gate on the whole run).

Reason. A rate of 0.086 of 200 passes K up to 17, and P(Binomial(200, 0.05) >= 18) = 0.012089, above the stated 1 percent. The exact 1 percent point for 200 draws is to fail at 19 or more (tail 0.0058236).
The review names two cutoffs: "True `<= 1%` cutoff is `K <= 18` (`0.090`, tail `0.005823`), and `K <= 20` brings `21`-class FWER to **`2.41%`**." Its first cutoff (pass up to 18) is the same as this exact 1 percent point, and its tail is the same value truncated.
The review gives no catch rate and does not say which of its two cutoffs it recommends. Its second cutoff (pass up to 20, so fail at 21 or more) is not adopted, because a looser cutoff lets a miscalibrated class through, and a miscalibrated class can produce a false "presence".
How often each cutoff catches a class whose true per-segment rate is 0.08: 200 draws failing at 19 or more (the review's first cutoff), 0.2506. 200 draws failing at 21 or more (its second), 0.1225. 1,000 draws failing at 68 or more (adopted), 0.9302. At a true rate of 0.07 the three figures are 0.1093, 0.0418 and 0.6155. A rate of 0.08 gives a false presence at S = 32 with probability 0.0119.
A false flag costs a valid result, not a false claim, so the per-class 1 percent level is kept.

Check: `check_binomial.py`, section PREREG-01b.

Effect: more miscalibrated classes are caught, so the chance of supported, partial and evidence against falls and the chance of "inconclusive" rises. The cost falls on calibrated instruments too: each check flags a calibrated class with probability 0.0074, and an instrument is marked not calibrated if any of the checks for its matched class flags.
With 3 versions (raw, exp, cube) at 3 window lengths that was 9 checks and a chance of 0.0647, and 0.0854 with 12 checks. Stricter option kept. These figures are superseded: A12 made the exp and cube versions identical to the plain ones, and A13 replaced the per-instrument mark by a gate on the whole run.

## A3. Split of the irreversibility transfer test, and a sign-aware null (review item PREREG-02): accepted with a different fix

Raised by: the review (https://github.com/Foundation-0/cave-expedition/pull/6#pullrequestreview-6010617857) for the split. The sign-aware null and the exact limit statement come from this amendment's own check.

Old text, lines 91, 94 and 95:

```text
Levels -4 to +5 are kept, giving 30 features. A level outside a series' range is set to 0.
Matched random detectors are R = 9,999 random permutations of the entries of w_A. They keep the same weights, signs and form. The transfer p-value is (1 + number of permuted templates with AUC_B at least that of w_A) / 10,000.
This compares the arrangement of the template, not just "irreversible or not". A plain irreversibility signal in B helps permuted templates as much as the real one.
```

New text: section 4.3 of the amended plan now defines an arrow transfer (the 10 u features, random detectors made of a permutation and an independent random sign per entry) and a profile transfer (the 20 m1 and m23 features, permutations only), each with its own template. It adds an exact limit paragraph. The confirmatory family grows from 28 to 40 tests (section 9).
Support for T3 needs the arrow transfer, and a profile-only pass gives at most "partial" (section 12). K4 is rewritten so A to C is judged on the arrow test, with a reported sawtooth case (section 10). The arrow test's blind spot is listed in section 13.

Reason, checked exactly. With s = a2 + a3 and u = a2 - a3, polarity flip maps (a1, s, u) to (-a1, -s, +u), time reversal to (-a1, -s, -u), and the two together to (+a1, +s, -u). These maps agree with the review's. Two consequences follow:

- m1 and m23 do not change under time reversal. A time-reversed copy C of A has the same expected m features, so the 20 magnitude entries of the old template score C as positively as A. The old K4 requirement (A to C below the 2.5th percentile) works against itself.
- On (a1, s) polarity flip and time reversal act identically. So no polarity-free function of (a1, s) can carry a time arrow. The only polarity-free arrow is u, and u is odd under reversal composed with polarity flip. If a series' statistics are unchanged by that composition, its time reverse has the same statistics as its polarity flip, and no polarity-free statistic can tell it from its reverse.

On a noiseless sawtooth rising in ramps (x_t = t mod 64, 4,096 samples) u is exactly 0 at lags 1, 2, 4, 8 and 16, by integer comparison of (2 n021 + 1)(2 n201 + 1) and (2 n120 + 1)(2 n102 + 1). At lag 1 the counts are n(120) = n(201) = 63 and n(021) = n(102) = 0. A falling ramp swaps the two pairs.
The review states that such waveforms satisfy "`n(021) == n(102)` and `n(120) == n(201) == 0` at every lag". That is wrong in general, not only for the sawtooth: what symmetry under reversal composed with polarity flip gives is n(120) = n(201) and n(021) = n(102), not zero counts. The review's conclusion that u = 0 for such series is right, and it is the review's finding.
The reversed sawtooth and the negated sawtooth give identical counts.

The K3 shot process is not of this kind. On one series of 2^20 samples (seed 20261122) u is +0.025, +0.062, +0.095, +0.072 and +0.027 at lags 1, 2, 4, 8 and 16, and it changes sign under reversal and not under polarity flip.
Over 200 independent segments of 4,096 samples (segment i with seed 20261123 + i, `sim_features.py`) the mean of u at lag 4 is +0.087 and the per-segment standard deviation (ddof 1) is 0.072. So the mean over segment standard deviation is about 1.2, and the mean is about 17 standard errors from zero (mean divided by standard deviation over the square root of 200).
The clean-room check found mean over standard deviation between 1.18 and 1.37 in its own runs, which gives 17 to 19 standard errors at 200 segments. The figure is a sample estimate and is not more precise than that. Either way the rewritten K4 is attainable.

A further problem, not in the review. A permutation null keeps the sign mix of the template. If B's arrow features are the same at every level and A's arrow entries share a sign, every permuted template scores exactly as w_A does and the permutation p-value is 1, so a shared direction could never pass. With profiles that vary across levels this holds only partly.
The arrow test therefore draws an independent random sign for each entry as well. For a same-sign template and a level-flat B, the exact p-value then falls from 1 to 1/2^m with m populated levels. The profile and scale-flow tests keep permutations only, since their features have no sign to share.

Checks: `check_symmetry.py` (exact), `sim_features.py` (sampled).

Effect.
- Supported: mixed, and the net direction cannot be fixed before data. Requiring the arrow transfer lowers it, because the arrow test is blind to series symmetric under reversal composed with polarity flip, and because 40 tests lower the smallest Holm threshold from 0.00179 to 0.00125.
The sign-aware null raises it, because it is easier to beat than a permutation null for a template whose entries share a sign.
- Partial: raised, because a pass on the profile transfer alone now counts as partial.
- Evidence against: the adverse rule now uses the arrow test only, against a sign-aware null.
- This change leaves the presence thresholds as they were (K >= 5 of 12, K >= 7 of 32). A11 raises them.

## A4. Segment offsets and amplitude maps (review item PREREG-03): accepted, extended

Raised by: the review (https://github.com/Foundation-0/cave-expedition/pull/6#pullrequestreview-6010617857) for the offset rule. The amplitude-map nets come from this amendment's own check.

Old text, line 163:

```text
Inside each kept block, the N-sample segment starts at the offset in 0 to 128 that best matches the segment's ends (smallest sum of the squared jump between first and last value and the squared jump between first and last slope). This limits a known IAAFT artefact and uses the same rule everywhere.
```

New text (section 7): the same cost computed on the exact mid-ranks of the whole block, with ties sharing the mean rank, and the smallest offset taken among equal costs.

Old text, line 134:

```text
| Amplitude map | strictly increasing maps, polarity flip | exact code checks, not statistical runs (K1) |
```

New text (section 5): two rows. Polarity stays an exact code check, now including the surrogate pool. Increasing maps become statistical nets with two fixed maps, normal scores of the ranks and exp of the standardised segment, applied to presence and to all three transfer tests. Section 4.1 notes that the scale flow uses block means and so depends on amplitudes.

Reason. The review's counterexample reproduces exactly: on the block [10, 10, 0, 1, 11, 11, 2, 2] with segment length 6, raw costs are [1, 65, 5] and select offset 0. After x^3 + x they are [110224, 1103684, 104] and select offset 2. After 2^x they are [1048576, 2082841, 10], also offset 2. Polarity flip leaves the raw costs unchanged.
On mid-ranks the costs are [4, 17/4, 29/4] under the identity, x^3 + x, 2^x and polarity flip, all selecting offset 0.

The same kind of problem goes further than the offset. Pattern counts of the real series do not change under an increasing map, but IAAFT surrogates are built from amplitudes and the scale flow averages amplitudes.
Two sampled checks show this. In `sim_iaaft_maps.py` (one segment of 1,024 samples, seed 20261123, surrogate seed 20261124, 200 IAAFT iterations, Sigma_hat at lag 1) the real Sigma_hat is identical under x, -x, exp(x) and x^3, and the surrogate pool for -x is exactly the negated pool for x, but the pool for exp(x) differs.
How far p-values move is measured in `sim_iaaft_spread.py`: two sets of 12 segments of 4,096 samples (segment i with seed 20261130 + i, surrogate seed 20261230 + i, the same for every variant), 99 surrogates per variant, a fixed 50 IAAFT iterations, the full per-segment statistic T of section 4.3 at lags 1 to 512 with tied patterns kept.

| Segments | Map | Mean absolute shift of p | Median | Largest | Segments shifted by 0.02 or less |
|---|---|---|---|---|---|
| K3 shots on AR(1) 0.9 (strongly irreversible) | exp | 0.012 | 0.000 | 0.12 | 11 of 12 |
| K3 shots on AR(1) 0.9 | cube | 0.005 | 0.000 | 0.05 | 11 of 12 |
| AR(1) 0.9 alone (reversible) | exp | 0.303 | 0.340 | 0.65 | 1 of 12 |
| AR(1) 0.9 alone | cube | 0.212 | 0.200 | 0.45 | 2 of 12 |

Where a segment is strongly irreversible its p-value sits at the floor of 0.01 and barely moves. On reversible segments the shifts are large, consistent with the clean-room check (mean absolute shift 0.08 to 0.22, largest 0.52, over its own settings), and the single example in an earlier draft (0.66 to 0.64) was a mild case.
The shifts on reversible segments are mostly downward: exp lowered p in all 12 and the cube in 11. A strictly increasing map of a Gaussian series is still reversible, so at 50 iterations the surrogates of a skewed series are not well calibrated.
This is the failure the frozen plan's K2 caught (A12). It led to surrogates made from normal scores, which make the exp and cube versions identical to the plain ones, and the controls C2 to C4 now run in every net run (A11).
So the old table claimed an exact invariance the pipeline does not have.

Checks: `check_endmatch.py` (exact), `sim_iaaft_maps.py` (sampled).

Effect: the offset rule is neutral. The new amplitude-map nets lower the chance of supported and partial, since more nets must pass, and raise the chance of "net-dependent".

## A5. Quantization bins and tied patterns (new, from this amendment's re-read)

Raised by: this amendment.

Old text, lines 65, 68 (last sentence), 133 and 142:

```text
p(pi) = (n(pi) + 1/2) / (sum of n + 3)
Windows with tied values are left out and their number is recorded.
| Quantization | 12 bits and 8 bits, uniform bins over the segment's 0.1 to 99.9 percent range | tied windows dropped and counted |
If more than 20 percent of a segment's windows are tied, the segment counts as not rejecting.
```

New text: tied patterns are kept as patterns of their own (13 patterns at order 3, with their reversal pairs), the pseudocount denominator becomes sum of n + 13/2, quantization uses equal-count bins on mid-ranks, and the 20 percent rule is removed (sections 4, 4.3 and 5).

Reason. From `sim_features.py`, part 2: 200 AR(1) series per coefficient, 4,096 samples each, start state drawn from the stationary law, standard normal innovations, case k and series i with seed 20261124 + 1000 k + i. Uniform bins are 256 equal-width bins over each series' own 0.1 to 99.9 percent quantile range, floored and clipped to 0 to 255.
The share of order-3 windows at lag 1 with a tie, as mean (standard deviation) over the 200 series:

| Series | Uniform bins | Equal-count bins |
|---|---|---|
| AR(1), coefficient 0.9 | 0.058 (0.006) | 0.049 (0.005) |
| AR(1), coefficient 0.99 | 0.151 (0.020) | 0.129 (0.015) |
| AR(1), coefficient 0.999 | 0.292 (0.059) | 0.252 (0.049) |
| AR(1), coefficient 0.9999 | 0.346 (0.085) | 0.294 (0.065) |
| exp(3 z), z an AR(1) series with coefficient 0.9 scaled to unit standard deviation | 0.914 (0.033) | 0.049 (0.005) |

An earlier draft gave single-series figures (0.324 and 0.294 at 0.999 and 0.9999, and 0.923 for the heavy-tailed case) that do not hold up over 200 series. The figures above replace them.

Strain sampled at 4 kHz and dominated by low frequencies is at the strongly correlated end. Under the old rule, segments with more than 20 percent tied windows count as not rejecting, so the quantization net would fail by construction for the strain and radio data, measuring the quantizer rather than the series.
Keeping tied patterns gives a statistic that is still zero in expectation for a reversible series. Equal-count bins do not depend on whether a positive quantity is stored on a linear or a log scale.

Related change to K3 (section 10). K3 now requires at least 50 percent detection under every statistical net of section 5 except the instrument net, not only under both quantizations. If any net fails, the run stops for an amendment before any verdict file is opened.

Check: `sim_features.py`, part 2.

Effect: removing a failure built into the quantization net raises the chance of supported and partial, and lowers the chance of "net-dependent" and of a presence failure counting toward "evidence against". The broader K3 requirement does not move any outcome directly. It raises the chance that the run stops for an amendment before the verdict.

## A6. Sample budgets, Wind/WAVES and window lengths (review item PREREG-04, budgets): diagnosis accepted, different fix

Raised by: the review (https://github.com/Foundation-0/cave-expedition/pull/6#pullrequestreview-6010617857) for the budgets. The time overlap problem, the window-length change, the gap rule and the channel rule come from this amendment and from the clean-room check.

Old text, line 180:

```text
For Wind/WAVES the four channels used are those at positions round((q + 0.5) F / 4), q = 0 to 3, in the file's frequency list of length F. Segments from the four channels are pooled before the every-k rule.
```

Old text, line 137, and line 104:

```text
| Window length | 2,048 and 8,192 samples | where the data allow 12 or more segments |
- The flow is block averaging by 2, applied to the whole valid stretch of a file, levels l = 0, 1, 2 and so on, as long as a level still gives at least 12 segments.
```

New text (sections 4.1, 5, 7 and 8):

- Wind/WAVES segments never overlap in time. The eight daily files are joined into one sweep sequence, blocks are numbered across day boundaries, the every-k rule selects blocks, and the i-th selected block is taken from channel i mod 4.
- N for Wind/WAVES is the largest of 4,096, 2,048, 1,024 and 512 that gives at least 12 valid blocks in the fit set (superseded by A13: only 4,096 or 2,048). It is found by reading, from the fit files only, the sweep times, the frequency list, the fill-value attribute and the values of the four selected channels, and is committed before the verdict files are opened.
- Wind/WAVES validity is stated exactly: finite values different from the fill value, sweep intervals within 10 percent of the block median, no interval above twice the median.
- The window-length net becomes N/2 and N/4 for every instrument (superseded by A13: N/2 only, and only where it is at least 2,048).
- Block averaging runs within contiguous valid runs only.

Reason. The budget arithmetic reproduces. Twelve blocks of 4,224 samples need 50,688 samples, times 2^l at flow level l. TESS sectors last 27 to 28 days, so at 20-second cadence they hold at most about 115,000 to 120,000 cadences before gaps and flags (upper bounds from sector duration, timeline above).
Level 2 would need 202,752, so the highest level is 1 (13 and 14 blocks), and at least 5 of 7 aligned flow levels are empty.
Under the old Wind/WAVES rule, 12 blocks need a cadence of at most 600/11 = 54.5 seconds. One correction: the review gives 10 blocks at 60 seconds and 3 at 192 seconds, which is the count for channels joined end to end. The plan numbers blocks within each channel, which gives 8 and 0.
Further problems. The four channels at the same time are strongly dependent (one radio burst crosses many channels), while the binomial count assumes independent segments. With time-disjoint segments the cadence limits for 12 blocks are 13.6 s (N = 4,096), 26.5 s (2,048), 50 s (1,024) and 90 s (512). After A13 only the first two matter.
As an illustration only, at 33 seconds N would be 1,024 with 18 blocks.
The plan does not use that figure.
An earlier draft took block b from channel b mod 4. With every-k thinning that uses a single channel for 160 of the 688 values of J from 32 to 719, and two or three channels for 176 more. Assigning channels in selection order uses all four channels with counts differing by at most one for every J in that range.
The old window-length net at 8,192 was "where the data allow", so a short record made an instrument net-incomplete and unable to count. N/2 and N/4 were always available. A13 later removed N/4 and every length below 2,048.

Checks: `check_budget.py`, `check_outcomes.py` (channel rule).

Effect, which is mixed (as of this item. A13 changed the lengths, see its item 11). Supported and partial: the Wind/WAVES rule raises the chance that Wind/WAVES has enough segments to count, and support needs all three of GW, SEIS and Wind/WAVES. Shorter windows in the window-length net and a shorter Wind/WAVES N lower per-segment power and so lower these chances.
Removing the overlap removes a source of false presence and lowers them further.
Evidence against: a powered Wind/WAVES makes a valid adverse result possible, while lower power raises the chance of an "absent" status, so this moves both ways too. Inconclusive: falls, since Wind/WAVES is less likely to be underpowered. The balance depends on the real cadence, which is not known before the fit files are opened.

## A7. Template permutations on the populated support (review item PREREG-04, permutations): accepted, with a floor

Raised by: the review (https://github.com/Foundation-0/cave-expedition/pull/6#pullrequestreview-6010617857).

Old text: line 94 (quoted under A3).

New text (section 4.3): random detectors permute only entries at levels populated in both instruments. An arrow transfer with fewer than 6 jointly populated levels, or a profile or scale-flow transfer with fewer than 8 jointly populated features, counts as not rejecting.
R is 99,999 for every transfer test, and a run counts as not passing unless (1 + R/D)/(R + 1) is within its per-run level, with D the number of distinct random detectors.

Reason. Entries at levels empty in B multiply zeros. Permuting weight onto them weakens the random detectors and makes w_A easier to beat, which favours a pass. The floor comes from the smallest reachable p: with m features, permutations alone give at least 1/m! (1/720 = 0.00139 at m = 6, above the new Holm threshold 0.00125, and 1/5040 at m = 7).
Permutations with signs give 1/(m! 2^m) (1/384 at m = 4, 1/3,840 at m = 5).
The clean-room check added a point these exact floors miss: with sampled detectors, draws identical to w_A tie with it, so the reachable p is about (1 + R/D)/(R + 1). With R = 9,999 that is 3.0e-4 at 7 features with permutations, above the per-run level of 0.00025 set by A11, so a floor of 7 would not have been reachable.
With R = 99,999 it is 3.2e-5 at 6 levels with signs and 3.5e-5 at 8 features with permutations, and the floors are set there. The review's remark on the 7 independent degrees of freedom of the 8 order-4 class frequencies needs no change: a permutation test does not need independent features.

Check: `check_binomial.py`, last section.

Effect: lowers the chance of supported and partial, and raises the chance of "does not discriminate". The larger R and the floor of 8 lower it further for pairs with few populated levels.

## A8. Transformations searched before an adverse outcome is final (the project's rule Law 2b)

Raised by: a request, during this amendment, to provide before data are opened for the project's rule Law 2b, "Transformational Steelman (Morphism Before Dismissal)", identifier LAW2B_TRANSFORM_BEFORE_DISMISSAL. A first draft of section 12a was written from the rule's name while its text was not public.
The text became public before any data file was opened, and section 12a was rewritten against it on 2026-11-22.

Basis: the reference specification, Foundation-0/cave-expedition commit `80606f1`, `symbiosis/round10/arm5-transformational-steelman/TRANSFORMATIONAL_STEELMAN_REPORT.md`, lines 36 to 44 (families), 48 to 53 (guards) and 95 to 104 (protocol), and the field list of its reference certifier, read and not run. Section 12a uses the reference's family identifiers.
The one-row statement in Aletheia version 2.0.0 (Foundation-0/aletheia commit `0b60322`, `spec/LAWS_AND_GATES.md` line 14, on a branch with an open change request, not merged) is used only for the wording of the G1 resolution condition.
An outside review of that branch found that its code port of the gate certifies from declared metadata, that five of its seven family identifiers differ from the reference, that its code accepts a null rate of zero although its table requires null_total x max_null_rate >= 1, and that its self-test passes with gates broken. So no part of section 12a depends on the port's identifiers or verdicts.

Old text: none (new section 12a, replacing the first draft).

New text: section 12a of the amended plan. It cites the rule, states that the analogue of "closed as falsified" here is the outcome "evidence against" and that no such outcome is final before the search is complete, and searches all seven families for each of the three ways an adverse outcome can arise:

| Family | Presence (a) | Arrow transfer (b) | Scale-flow transfer (c) |
|---|---|---|---|
| T1_GAUGE_SIMILARITY | W zero-phase whitening first | W | W |
| T2_AFFINE_BREGMAN | no admissible instance (exact rank argument). Superseded by A13: instance Q | no admissible instance. Superseded by A13: instance Q | no admissible instance (kept by A13, with its reason) |
| T3_METRIC_CHART | H Hellinger form of Sigma_hat | H Hellinger form of the features | H square-root frequencies |
| T4_SPECTRAL_PSD_SHIFT | F white floor of 1/1000 of the standard deviation | F | F |
| T5_SEMIRING_TROPICAL | M max-plus limit of Sigma_hat | M max-plus score | B block maxima in the flow |
| T6_SUBSPACE_PROJECTION | D increments, O4 order 4 | D | D |
| T7_ORDER_DOMAIN_RESIDUAL | E event-rich domain | E (normal scores before surrogates became part of every test, A12) | R normal scores before block averaging |

The four transformations of the first draft: order 4 and increments move to T6 (O4 and D), the rank-based flow moves to T7 (R), and the signed arrow between Wind/WAVES and TESS is dropped, because TESS never enters the outcome procedure and the test could not change any recorded outcome.

Guards, with the arithmetic:
- G1: every instance is a non-degenerate map. Each instance that passes on the real data runs on 10 null replicates and may pass on at most 1 (rate at most 1/10), and 10 x 1/10 = 1 meets the resolution condition as the version 2.0.0 laws table words it (a rate of zero is not used). As the reference requires, a rescue needs one instance to pass for every item that triggered the adverse outcome.
Each instance also passes the synthetic tests of its paired test before data are opened.
- G2: counting every constant in an instance's definition, transform_dof is at most 2 (E: a quantile pair and a threshold fitted on fit data only). Held-out constraints are the verdict segments, at least 12. 2 < 12 for every instance, and every instance is fixed by this text before any verdict file is opened.
- G3: a ledger of preserved core and scope change is written for each instance. The rule's zero-residual condition is for exact results. Our sampled analogue: a passing instance is always recorded as a bounded core, never exact, with both p-values and the scope change reported.
- G4: all seven families are searched for each adverse type, T2 with an exact reason. "Evidence against" is final only if no instance passes and the pre-stated obstruction holds in every instance (presence still failing for (a), the transfer still adverse both ways for (b) and (c)), which is our sampled analogue of a transform-invariant obstruction.
Every adverse outcome ends in one of three recorded states: transformed core (one instance passes for every triggering item), final (no instance passes for any item and the obstruction holds), or unresolved (anything else, neither final nor a rescue).
The exact limit of section 4.3 does not qualify: it limits what the arrow test can see, gives "neither" rather than "adverse", and so cannot trigger outcome (b).

Multiplicity: 21 + 36 + 36 = 93 tests in their own family under Holm at 0.05 (smallest threshold 0.000538), after A12 removed the normal-score instance for the arrow transfer. Each uses the nets and Bonferroni split of its paired test. Presence instances can reach their smallest per-run level of 5.4e-5 (K >= 6 of 12, 9 of 32).
Instances are computed by a fixed rule for every adverse outcome that occurs, and tests not computed enter Holm with p = 1. A13 adds instance Q and the family becomes 102 tests.
Transfer instances use R = 99,999 random detectors and floors of 8 features (permutations) or 6 (with signs), within their smallest per-run level of 1.0e-4.

Check: `check_binomial.py`, sections on the Bonferroni split and null resolution.

Effect: none on supported, partial or the other non-adverse outcomes, since these tests cannot produce them. They lower the chance that an adverse outcome is recorded as final, more than the first draft did, since there are now 15 or more instances per adverse type and an obstruction must hold in all of them.

## A9. Outcome procedure (from the clean-room check)

Raised by: the clean-room check of this draft. Under a literal reading of the old outcome table, many result states matched no row and many matched two or more.

Old text: the outcome table, lines 240 to 247.

New text: section 12 of the amended plan, a decision procedure with a fixed precedence for T3 (invalid, evidence against, supported, net-dependent, partial, does not discriminate, inconclusive) and for the scale-flow half of T1, which has no presence test (invalid, evidence against, supported, partial, does not discriminate, inconclusive).
Each input is defined (instrument status, pair results, what "adverse" requires) and TESS stays outside the procedure.

Reason and check. `check_outcomes.py` defines each outcome's condition on its own, enumerates every state (11,664,000 for T3 and 11,664 for T1), and confirms that every state meets at least one condition and receives exactly one outcome by precedence. For T3, 11,200 "evidence against" states and all 64 "supported" and 448 "net-dependent" states also meet a lower-ranked condition.
For T1, all 25 "evidence against" states and the single "supported" state do.

Effect. "Evidence against" ranks above "partial" and "does not discriminate" where both apply (the stricter choice), which lowers the chance of "partial" in those states. An adverse pair result needs the primary run and every transfer net, the same standard as a pass, which lowers the chance of "evidence against" compared with judging the primary run alone.
"Inconclusive" is new and takes the states with too few usable instruments.

## A10. Choices that were still open (from the clean-room check)

Raised by: the clean-room check of this draft. Each item below would otherwise be decided after data are opened.

- Lags (section 4.3): lags 2^j are kept only if 2 tau is at most n/4 for a segment of length n, for every window length and decimated segment. Effect: neutral (it states what lag 512 at n = 1,024 would have forced).
- Ranks and rank maps (section 4): mid-ranks from 1, normal scores Phi^-1((r - 1/2)/n), equal-count bins floor(2^b (r - 1/2)/n). Tied values (the seismometer counts are integers) get the same score and bin. Effect: neutral.
- Ties in the order-4 flow features (section 4.1): frequencies over all windows, 8 classes without ties plus one class for every tied window, 9 features per level, 63 in all. Effect: neutral.
- IAAFT (section 4): stop when the rank order is unchanged between two successive iterations, or after 1,000 iterations, and return the rank-remapped series. Effect: neutral.
- K2 class matching (section 10): slope fitted over 10^-1.5 to 10^-0.5 times the Nyquist frequency, matched to the nearest base class and to every class tied at that distance. The instrument is not calibrated if any version (raw, exp or cube) of any matched class is flagged. Effect: lowers the chance of supported, partial and evidence against, and raises "inconclusive" (stricter tie-break).
- Wind/WAVES: what is read and when, validity, blocks across file boundaries and the channel rule (under A6).
- TESS in the family (section 9): 19 of the 40 tests involve TESS, which cannot count toward support. They stay in the family of 40. Moving them out would let the other 21 face a smallest threshold of about 0.0024, which is less strict, and every test can still reach 0.00125. Effect: keeps the chance of supported, partial and evidence against lower than the alternative would.

## A11. Requirements of Aletheia version 2.0.0 (branch under review)

Raised by: the same request, which asked for every version 2.0.0 requirement the plan does not meet to be met or explained. Source: Foundation-0/aletheia commit `0b60322`, `spec/LAWS_AND_GATES.md` and `spec/proposals/OWN_TERMS_FIRST.md` (five tightenings OTF-TIGHT-01 to 05), on a branch under review, not merged.

New text: section 12b of the amended plan lists each requirement and where it stands. Requirements not met by the plan before this change, and what was done:

- Bonferroni budgeting across nets (OTF-TIGHT-01). Before, every net run was judged at the test's full level, which controls error for an intersection test but is not the budgeting the method asks for. Now each test's level is split across its runs: 13 for presence (12 for TESS), 5 for transfer.
A12 later reduced these to 10 (9), 3 for the arrow and profile transfers and 5 for the scale flow, and A13 reduced presence to 8 (7).
At the smallest confirmatory level a presence run needed K >= 6 of 12, 8 of 24 or 9 of 32 (before: 5, 6 and 7. After A13: 6, 7 and 8), and the arrow transfer floor rises from 5 to 6 jointly populated levels, since 1/3,840 at 5 levels is above the per-run level of 0.00025.
- IID and spectrum-preserving nulls with a margin, and negative controls with a ceiling, in every net (OTF-TIGHT-03 and Rule 5). Before, the controls ran in the primary run only, with no margin.
Now every run needs its share of rejecting segments to exceed each of C2, C3 and C4 in that run by at least 1/4, with each control share at most c_max(S) (4/12, 5/16, 6/24, 7/32, the 1 percent point split over 39 checks). A calibrated pipeline breaches a ceiling in any of the 39 checks with probability at most 0.0072 (superseded: 30 checks and 0.0056 after A12, 24 checks and 0.0045 after A13).
The transfer tests now also check B's C3 series as well as its C2 series in every run.
- Gate 10 advocate. Every adverse or narrowing outcome goes to an independent advocate before it is final.
- R5 mutation testing and R6, R7 for the analysis code. Every condition is computed by the plan's own code and second checker. Running the branch's tools is an extra, not the basis, because the outside review found the branch's code checks less than its text.
- Arm B: the orthogonal model ladder (OTF-TIGHT-02) is noted in the outline.

Check: `check_binomial.py`, sections on the Bonferroni split and the control ceiling.

Effect: lowers the chance of supported, partial and net-dependent (higher counts per run, a margin over every control, a higher arrow floor), and raises the chance of an "absent" status and so of "evidence against" before the Law 2b search. Stricter option kept.

## A12. Changes after the known-answer tests failed on the frozen plan

Raised by: the results of the code built to the frozen plan, Foundation-0/cave-expedition branch `outside/continuum-four-transformations-code`, commit `71142c18383467f14c6da4dd17528afb3a9e7f2c` (draft PR 8), files `AMENDMENTS_NEEDED.md`, `known_answer/RESULTS.md` and `known_answer/out/`, all on synthetic series. The code was read to understand the results and was not rerun here.

Record. The frozen plan failed four of its own six known-answer tests before any data file was opened:

| Test | Result | Observed |
|---|---|---|
| K1 | pass | 228 exact checks, 0 failures |
| K2 | fail | 11 of 21 classes above the bound, all of them exp or cube versions. Highest rate 0.295 (AR(1) 0.9 after exp). Plain classes 0.040 to 0.065. Raising the IAAFT cap from 100 to 1,000 rounds moves the worst rates by at most 0.017 |
| K3 | fail | 4 of 9 cells below the criterion: shots after whitening 0.440, sawtooth 0.215, 0.400 and 0.185 (the sawtooth passes in every seed under the other reading of the noise level) |
| K4 | fail | A to B p = 0.2025. A to C AUC 1.000 against 2.5th percentiles of 0.404 and 0.438. The 20 magnitude features saturate the AUC |
| K5 | fail | exponential ratio 2.57. The cascade criterion passes at 0.70, but a shuffled cascade also passes it (1.946). Two transfer criteria could not be run |
| K6 | pass | six refusal branches, removal of each flagged |

The builder also found that the 56 flow features could not be transferred as written (no segment owns all of them) and listed 13 choices the plan had left open.

### K2: the null was miscalibrated after a static map

Cause. Pattern counts do not change under an increasing map, but IAAFT surrogates are built from amplitudes. For a linear Gaussian series passed through exp or a cube, the surrogates did not reproduce the null, and the test flagged irreversibility up to 30 percent of the time where it should flag about 5 percent.
This is the same problem as A4's finding that the surrogate pool moves under increasing maps (on reversible segments, exp lowered p in 12 of 12 and the cube in 11 of 12 in `sim_iaaft_spread.py`). Real radio power and photometry are heavy-tailed, so this would manufacture "presence".

Decision. Surrogates are made from the normal scores of the segment, Phi^-1((r - 1/2)/n) on mid-ranks, never from its raw values (section 4). Every series then enters the surrogate step with a Gaussian marginal.
Because the statistic depends only on order, the real series' statistic is unchanged, and the whole pipeline (normal scores, surrogate pool, standardised features, segment p-value) becomes exactly the same for a series and for any strictly increasing map of it. The exp and cube versions of a class therefore give exactly the results of the plain class with the same seeds.
The null of the test is now stated plainly as "an increasing map of a stationary linear Gaussian process". That is narrower than "reversible", so two reversible series of another kind (g^2 and |h| of AR(1) series) are added to K2 to measure how often the test flags them.

Amended K2. 9 classes (the 7 plain classes and the 2 new ones), 1,000 seeds per class at each window length, a class flagged at 68 or more segments with p at most 0.05. The bound is exact: P(Binomial(1000, 0.05) >= 68) = 0.0074, the smallest such tail at or below 0.01. K1 checks exactly, for every class and 20 seeds, that the exp and cube versions give identical pools and p-values.
A13 changed the flag points (74 for the null classes, 129 for the reversible ones), the lengths (4,096 and 2,048) and the consequence (a flag stops the whole run), and removed class matching.

Effect on the two amplitude-map nets. For presence and for the arrow and profile transfers they are now exact identities, checked in K1, and are no longer statistical runs. The scale flow still averages amplitudes, so for it they stay as statistical nets.
Presence runs fall from 13 to 10 once whitening also leaves (below), the arrow and profile transfers from 5 to 3 runs, and the scale flow keeps 5. The control ceiling is now split over 30 checks (probability of any breach at most 0.0056). A13 later reduces presence to 8 runs and the ceiling to 24 checks.
Direction: removing a source of false presence lowers the chance of a false "supported" and of "partial". Fewer runs raise each run's level (presence 0.000125 instead of 0.000096 at the smallest step), which raises the chance of passing for a real signature. The net change cannot be signed before data. The miscalibration it removes was large, so the change was made whatever its direction.

### K3

Causes. Shots after whitening (0.440): the order-3 estimate loses power when the segment's own spectrum is divided out, although the true path divergence is unchanged by that zero-phase filter. Sawtooth (0.215, 0.400, 0.185): the plan's "noise of half its amplitude" was ambiguous.
At noise standard deviation 0.5 for a peak-to-peak 1 sawtooth the planted signal is weaker than the noise, while at half the sawtooth's standard deviation (0.144) it is found in every seed on every net.
Decisions. Whitening leaves the confirmatory nets and stays as Law 2b instance W. It is not one of the changes of net the essay names (sensors, sampling rates, polarizations, bases) nor one of those set for this test, and the known-answer result shows that keeping it would fail planted, truly irreversible series for reasons of the estimate, not of invariance.
This is not a tie, so the stricter option did not apply. The direction is to raise the chance of "supported" and lower that of "net-dependent".
The sawtooth uses noise at half its standard deviation. This reading was chosen after seeing the builder's result and is labelled so in section 10. The noisier reading is run and reported and does not gate. K3's criterion is unchanged (80 percent native, 50 percent in every other non-instrument net).

### K4

Cause. The review's symmetry point (A3): 20 of 30 template features did not change under time reversal, and the AUC against a series' own surrogates saturates at 1 for any strong arrow, so every template, real or random, scored near the top. The amended plan already split the test (A3).
The builder's diagnostic with the 10 sign-sensitive entries and a permutation null separated A from C (AUC 0.19 against 0.27) but left A to B at p = 0.29.
Decisions. The transfer score is now the mean standardised score S_B(w), which does not saturate, and "adverse" is defined on it. The arrow null carries random signs (A3).
K4 is rewritten (section 10): the builder's construction of B and C, 10 seeds, criteria required in every run in at least 9 of 10 seeds, and a must-fail control (a shuffled, surrogate-replaced copy of A must not pass in more than 1 of 10 seeds).
Direction: the non-saturating score gives the transfer tests power they did not have, which raises the chance of "supported" and "partial" when the arrows are shared, and of an adverse transfer when they are opposite.

### K5 and the flow transfer

Cause. The "norm halves" criterion measured noise: for independent values every order-4 class is equally likely, so the level-0 norm is sampling noise, and coarser levels with fewer segments have larger noise. The cascade criterion was passed by a shuffled cascade, so it could not tell structure from noise.
Decisions. K5 now judges departure per level against each unit's own pool, with exact binomial points, and requires: no departure at any level for independent exponential values (an exact null case after normal scores) and for the shuffled cascade, departure at level 0 and at the top level for the cascade, and transfer criteria including a shuffled-cascade control (section 10).
The flow transfer uses the builder's first reading: each (level, segment) pair is a unit filling only its own level's 9 entries, and B's score averages over levels with equal weight. The second reading copies coarse features into many fine units and so counts them more than once, and the third has no unit-level variation, so no null.
Direction: the old K5 could not fail informatively, so this change mainly makes K5 able to gate. On outcomes it is neutral.

### The builder's 13 open choices, closed in the plan text

| Builder item | Closed as | Section |
|---|---|---|
| A1 IAAFT start and stop | random permutation of the normal scores, stop when ranks are unchanged in two successive iterations or after 1,000, end on the rank step | 4 |
| A2 lag for the tied-window rule | rule removed, tied patterns kept (A5) | 4.3 |
| A3 lags at lower sampling rates | lags 2^j with 2 tau at most n/4, for every segment length | 4.3 |
| A4 running-median edges | reflection at the edges (used only by instance W) | 12a |
| A5 K2 classes | the builder's sinusoid and power-law construction, scaled to mean 0 and standard deviation 1, plus the two new classes | 10 |
| A6 K3 shots and sawtooth | the builder's shot reading, logistic start and burn-in. Sawtooth noise at half its standard deviation, labelled as chosen after the run | 10 |
| A7 K4 half-rate construction | the builder's construction | 10 |
| A8 K4 and K5 scoring and seeds | 10 seeds, criteria in every run, pass in at least 9 of 10, must-fail in at most 1 of 10 | 10 |
| A9 cascade parameters | dyadic, log-normal weights, mean 1, log standard deviation 0.5 | 10 |
| A10 class matching | slope of the normal scores' median periodogram over 10^-1.5 to 10^-0.5 times Nyquist, nearest of 9 classes, ties to all tied classes | 10 |
| A11 order-4 normaliser | pseudocount 1/2 for each of 75 patterns, denominator count plus 75/2 | 4.1 |
| A12 zero-spread standardisation | the lag is left out of that series' maximum and the segment flagged. If every lag has zero spread, the segment counts as not rejecting | 4.3 |
| A13 tau0 | mid-ranks, biased autocorrelation about the mean, level shift log2(tau0) rounded half up | 4.3 |

### Gate

No data file is opened until the code has been updated to the amended plan and every amended known-answer test (K1 to K6, and the instance tests of section 12a) passes in all three Python modes with its must-fail control flagged. If any fails, the plan is amended again, with the date logged, before any data file is opened. The amended known-answer tests have not yet been run.

### Compute

Estimate in `checks/check_compute.py`, at the builder's measured cost of about 2.3 processor-seconds per 4,096-sample pool (9,600 processor-seconds for the frozen K2's 4,200 segments per mode):

| Stage | One mode | Three modes |
|---|---|---|
| Amended known-answer tests | about 25 h (K2 10, K3 3, K4 1.4, K5 4, instance tests 5.6) | about 75 h |
| Fit stage | about 1 h | about 3 h |
| Confirmatory verdict run | about 8 h | about 24 h |
| Law 2b search, worst case (all three adverse kinds occur, every instance passes) | about 65 h | about 195 h |

Without an adverse outcome the total is about 100 processor-hours (about 90 after A13). For comparison, the frozen plan's K2 alone took about 8 processor-hours over three modes.
Trims that weaken no guard: the exp and cube K2 classes are covered by an exact identity instead of 12,000 more runs per window length. Pools are made once and reused by presence, the arrow and profile transfers, and the statistic-only Law 2b instances (H, M, O4, E).
Law 2b instances are computed by a fixed rule only for adverse outcomes that occurred, and their null replicates only for instances that pass on the real data, since neither can change any outcome otherwise. Null replicates stop at their first failing run. Law 2b instance tests run at window length 4,096 with 200 seeds per class (A13 sets their flag points at 24 and 36).
Not trimmed: three Python modes for every run, the 1,000 seeds of K2, and the controls in every net run.

## A13. Changes after the second clean-room check

Raised by: the second clean-room check of this draft (ten defects and a list of points that could wait, the latter taken now), and decisions sent with it. Each item gives what changed and its direction.

1. Instance W was named but not defined. Section 12a now gives the recipe: divide the segment's Fourier transform by the square root of the running median of the periodogram over 33 neighbouring frequencies, the window reflected at both ends, zero frequency set to 0. Direction: none, a definition.
2. K2 gating rule, stated before any run. K2 is now a gate on the whole run, not a per-instrument mark, and class matching is removed. K2a (the 7 null classes): a flag at 74 or more of 1,000 at either length fails K2 and stops the run, since after normal scores these classes are exactly the test's null.
74 is the 1 percent point split over 14 checks, so a calibrated set is flagged with probability at most 0.0090.
K2b (g^2 and |h|): a flag at 129 or more of 1,000 (a rate clearly above 0.10) stops the run. A rate up to 0.10 is reported and does not stop it. The one-run figure first given here (0.0033) is corrected by A14 item 1. The clean-room check measured these classes at 0.05 to 0.09.
K2 now covers every length a confirmatory run can use, 4,096 and 2,048 (item 11). Direction: the gate is looser per check than the earlier 68 (it catches a class at a true rate of 0.07 with probability 0.33 per check, against 0.62), so a mild miscalibration is more likely to pass. A14 item 1 gives the exact chance that such a rate passes a presence run.
With the same 14 checks, the old point of 68 would stop a calibrated run with probability 0.099. The new point brings that to at most 0.009.
3. False-flag figures. The earlier 0.022 and 0.029 were the probability that a class whose true rate is exactly 0.05 is flagged at one or more of 3 or 4 length checks. Wind/WAVES used 3 lengths, not 4. Across three instruments the chance was up to 0.065, and it grew fast above a true rate of 0.05 (0.129 at 0.055 over three lengths).
The builder's plain classes ran 0.040 to 0.065, so such rates were not excluded. Those figures are superseded by the whole-run gate of item 2, whose false-stop chance is at most 0.009 at a true rate of 0.05, 0.025 at 0.052, 0.091 at 0.055 and 0.43 at 0.06.
4. Must-fail controls.
Every known-answer test now has one: K1 three broken variants (a counter that drops the last window, a counter that orders ties by position, raw-value surrogates under exp), K2 the frozen plan's raw-value surrogates on AR(1) 0.9 after exp, K3 circular-shift surrogates (at most 20 of 200 detected), K4 a shuffled surrogate copy for both the arrow and the profile transfer, K5 the shuffled cascade, K6 its six refusals.
Direction: the run is more likely to stop for an amendment before data.
5. Outcome procedure. Rule 7 now counts adverse pairs inside V. Net-dependent uses the per-run level of the 8 runs now in use (0.00125 / 8). A pair whose arrow transfer is adverse in either direction no longer counts toward "partial" through its profile (the stricter option, which goes beyond pairs adverse both ways).
`check_outcomes.py` was rerun: every one of the 11,664,000 states still gets one outcome, and "partial" falls from 215,506 to 129,867 states, the difference moving to "does not discriminate". Direction: lowers "partial".
6. T2. The reference family is the Bregman form, not only affine maps, so it is not empty. Instance Q (the Bregman divergence with the quadratic generator, the sum of squared differences between pattern probabilities and their reverses) is added for presence and for the arrow transfer. It can order two series oppositely to the log-likelihood ratio.
The scale flow has no divergence in it, so T2 has no instance there, with that reason. "Positive slope" is now stated for the affine case, and the stale "AUC" is gone. The Law 2b family grows from 93 to 102 tests (smallest threshold 0.00049). Direction: lowers the chance that an adverse outcome is recorded as final.
7. G3 and G2. The sampled translation has no numeric residual gap. What replaces it is the pre-written scope change for each instance and the reported pair of p-values, and a passing instance is always a bounded core. E has 5 constants (four quantile levels and a fitted threshold), so the largest count is 5, still below 12. Direction: none.
8. Section 12b. The advocate is a reviewer who wrote neither this plan nor its code. The authors of the essay's claim are invited first, on the pull request, with the full record. After seven days without a response an independent reviewer with no part in the analysis takes the role.
The advocate may point to a listed transformation not run or to a defect, but may not add transformations or change thresholds, and the ruling and what was done are recorded. The R5 mutation test is defined (refusal deleted, comparison flipped, threshold moved by one unit, every mutant killed or recorded as equivalent before data).
Gate 9 is not exercised: every result here is N0, and a later higher label needs that search first. Direction: "falls" can stop an adverse outcome from being final, which lowers the chance of "evidence against, final".
9. Duplicated and stale text removed or corrected (repeated K2 matching lines, a repeated commit-order sentence, the K2 note in A4, the A2 effect figures and the K2 quotation in A2 now marked as superseded, the compute sum, the blind-spot sawtooth reading, the floor reasoning).
10. K5 sizes: every series has 2^19 samples (cascade depth 19), levels 0 to 3 with 32, 32, 31 and 15 units. When two or three kinds of adverse outcome trigger at once, each kind is searched and recorded separately. The outcome is final if any triggered kind is final, since each kind alone is enough for rule 2.
Otherwise it is a transformed core if rule 2 no longer applies after all rescues, and unresolved if not. Direction: a final "evidence against" is reachable through any one kind, the stricter reading.
11. Short windows, set after measurements. The clean-room check measured detection of planted shots at 0.925 (4,096 samples), 0.60 (2,048) and 0.30 (1,024). A run needs a rejecting share of about 0.30 to pass, so a length where planted arrows are found in 30 percent of segments cannot separate presence from its absence.
K3's existing requirement of 50 percent at every confirmatory length was kept, and the lengths that cannot reach it were removed: block mean by 4 and window length N/4 are no longer nets, sampling-rate and window-length nets apply only where the result has at least 2,048 samples, and Wind/WAVES must reach N = 2,048 or is underpowered.
Presence has up to 8 runs (7 for TESS), and the control ceiling is split over 24 checks (any breach at most 0.0045). This was set after the measurements, and the criterion was not lowered to make K3 pass. Direction: fewer nets raise the chance of "supported". A Wind/WAVES cadence above 26.5 seconds now makes Wind/WAVES underpowered and support impossible, which lowers it.
12. Smaller points taken now: K1 checks that each map leaves the number of distinct values unchanged and states that the identity depends on one fixed implementation of Phi^-1. C4 is noted as outside the identity. The floors of 8 features and 6 levels are said to come from the Law 2b levels. The ceiling bounds are stated as bounds (0.0045 for 24 checks).
T5's M is described as a max-plus limit of the log ratios, and O4 as a refinement. The K4 blind-spot sawtooth uses the K3 reading. The whitening entry now says that the essay's "bases" could cover it, so that dropping it from the confirmatory nets makes "supported" easier while making a final "evidence against" harder through instance W.
Direction of the sawtooth reading (A12): it lowers the chance that K3 stops the run, and it does not move any outcome.

Compute after A13 (`check_compute.py`): known-answer tests about 21 processor-hours per mode (64 for three), fit stage about 1, confirmatory verdict run about 8 (23 for three). Without an adverse outcome the total is about 90 processor-hours (about 103 after A14 item 6). The Law 2b search adds up to about 68 per mode (203 for three) in the worst case.

## A14. Corrections after the third clean-room check

Raised by: the third clean-room check of this draft. It confirmed every K2 gate figure, one outcome per state (129,867 "partial" states), 40 and 102 tests, that every test can reject, instance Q, the new controls and the K5 sizes, and asked for six fixes and some smaller ones.

1. False-presence bound (section 10, K2b). "At most 0.0033" was the value at 16 segments only. The exact one-run chance for a series whose segment rate is 0.10 is at most 0.0117 if every control share were 0 (at 32 segments) and at most 0.0043 with control shares near 0.05 (0.0008 at 32 segments). At the stopping line, 0.129, these are 0.046 and 0.013.
The runs of one instrument are not independent, so the chance over all runs lies between the product of the run chances and the largest single-run chance. "Supported" also needs all three counting instruments present and the transfers to pass. The earlier wording "cannot by themselves produce presence" overstated this and is withdrawn. Direction: none, a correction of the stated figure.
2. "Net-dependent" uses the test's own per-run level, not 0.00125 / 8, since TESS has 7 runs and Wind/WAVES at N = 2,048 has 5. Direction: none, a correction.
3. K3 at 2,048 samples. The 80 percent native requirement applies at 4,096 samples. At 2,048 samples (the native length of Wind/WAVES if its N is 2,048) the requirement is the general 50 percent, because the clean-room check measured native detection of the K3 shots at 0.70 there, and an 80 percent rule would fail almost surely. This was set after that measurement.
The other reading, 80 percent at both lengths, was rejected because it would stop the run for a length the plan keeps on purpose. An instrument whose native length is 2,048 enters with lower power, which makes "supported" harder for it, not easier. Direction: lowers the chance that K3 stops the run, and does not raise the chance of "supported".
4. A6, A11 and A8's T2 row are now marked as superseded where later items changed them.
5. Section 10 now says that the K2 gate is looser per check than the earlier point of 68 (a class at a true rate of 0.07 caught with probability 0.33 against 0.62), with the gain in spurious stops (0.009 against 0.099).
6. K4 and K5 templates. Every synthetic instrument and K5 case has two independent streams per seed, a fit stream that gives tau0 and the template and a verdict stream that is scored. Direction: none on outcomes.
It doubles the K4 and K5 streams, so the known-answer tests now take about 26 processor-hours per mode and the total without an adverse outcome is about 103 processor-hours over three modes (`check_compute.py`).

Smaller items: the interval method is named (Clopper-Pearson). "Positive slope" is added to the scale-flow cell of T2. G3 is named as the one exception to "the stricter reading is used". In section 12b the independent reviewer is selected by the session coordinating this check, with the selection and reason recorded. "Respond" means a written reply on the pull request.
Narrowing outcomes are partial, net-dependent, does not discriminate and evidence against. "stands_narrowed" is reported in the narrower form the advocate gives. The mutation test's unit is 1 for integer thresholds, the smallest step of the stated decimal for rational ones, one representable step for floating tolerances, and one bin or sample for window, lag and bin counts.

The frozen plan stays retrievable at commit `24d7757`. This amendment and the amended plan are in the commit that adds this file.

## Items considered and not changed

- Quorum margin (review item PREREG-04). Support needs presence in GW, SEIS and Wind/WAVES, because TESS has no second sensor in this run. The margin is zero. A second "instrument" for TESS could only be another on-board product from the same pixels, which is not a different sensor. Not changed. Effect: keeps the chance of support where it was.
- Arm B capacity (review item PREREG-04). The outline's rule of at least 50 windows per pattern gives order 4 at most per 4,096-sample segment (order 5 needs 6,000 windows), and order-6 transitions need 216,000 windows against 131,072 in 32 pooled segments.
Arm B is an outline, not part of this test, so the note is added to `ARM_B_OUTLINE.md` and pooling will be fixed in Arm B's own pre-registration.

## Files

- `PREREG.md`: the amended plan, with a change log at the top.
- `FETCH_MANIFEST.tsv`: file name, URL, bytes, SHA-256 and fetch time of each of the 26 files.
- `checks/`: the scripts above, `run3.sh` and `run3par.sh`, and their outputs in the three modes.
- `README.md`, `DATA_REQUEST.md` and `ARM_B_OUTLINE.md`: status lines and the Arm B note updated.

The scripts that applied these edits to the plan by exact text replacement are kept outside this folder and are not part of the commit. The amended plan and the git diff against `24d7757` are the record of the change.
