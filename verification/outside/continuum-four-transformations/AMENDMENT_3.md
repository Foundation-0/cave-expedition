# Amendment 3 to the pre-registration

Date: 2026-11-22. Base: branch `outside/continuum-four-transformations-prereg` at commit `1aa53fb` (Amendment 2 at `fba51a3`, with the independent check of Amendment 2 added on top). Line numbers below refer to `PREREG.md` at that commit.

No data file has been opened or parsed.

What had been run before this amendment, and who saw what:

- Under Amendment 1, the code (commit `99533df`) ran smoke versions of the known-answer tests: one twentieth of the plan's seeds, and the full 10 seeds for K4 and K5 (`AMENDMENT_2.md` lines 9 to 15). Their outcomes were known to the code's author and to the party who routed the questions between the code's author and the plan's author, and were not read by the plan's author.
- After Amendment 2, the ported code ran further smoke runs, with whatever keys the code used. Their outcomes were known to the code's author and to the routing party. The plan's author read no outcome of them.
- Two failures of those runs were reported to the plan's author: a smoke run of the redesigned K5 that crashed on an overflow at seed 0 (which led to SK8), and a K1 smoke run that failed on a fault of the test harness.
- No one has opened a data file. The code's author reports no full-count run of K1 to K3. No known-answer test has been run at its full count under the plan as amended by Amendment 2 or this amendment.

How the seed-key items were found:

- Amendment 2's last edit wrote out the seed-rule fields for every use (reading D14). That edit was published without an independent check of the keys.
- The independent check made after publication (`independent_check/amendment_2/`, script `seed_keys`) built the keys as D14 words them and found SK1, SK3 and SK4. The same review of the keys after publication raised SK2.
- Going through every key family of D14, this amendment's own check (`checks/amendment_3/seed_keys.py`) found SK5 and SK6 and the gaps filled by SK7.

How SK8 was found: the code's author hit an overflow, which stopped a smoke run of the redesigned K5 at seed 0 with no result. The code's author also reported, through the routing party, that the map overflows in 9 of 10 seeds.
The plan's author does not know how that figure was made. By the builder's report it is not from a K5 run, since that run stopped at seed 0.
The plan's own figure comes from `checks/amendment_3/amp_maps.py`, which applies the map to cascades it generates with seeds that no test uses, and finds the overflow in 10 of 10.
The plan's author was told of the crash and of the builder's count, and read no outcome of the run. The cause and the ruling below come from the plan text and from `amp_maps.py`.

What the items change:

- SK1 to SK7 change no threshold, test definition, net, control or decision rule, with one exception: reading D20 (SK7) makes K4 pass only if it passes under two readings of its stream set. Otherwise they change only which random numbers some draws receive, and they fill fields the old text left open.
- Known-answer draws that get new keys: every K5 flow-unit pool (SK1, SK2), every K5 random detector (SK4), every K3 pool (SK3, a new instrument string, although the old keys were already distinct), and in K4 the A' fit-stream draws, the A' pools and the detectors of the pair A>Aprime (SK4, SK7).
  In the code at `99533df` the other K4 detectors already had the keys now written. K1 and K2 keep their keys.
- On real data, SK4 to SK6 fix keys for draws that no run has made yet: random detectors, control pools, the Law 2b instance tests and the G1 null replicates.
- SK8 changes one net and one known-answer series: the scale flow's second amplitude-map net, and the mapped cascade of K5's positive criterion. It changes no threshold or decision rule. Its effect on real-data statistics is stated under SK8.
- SK9 corrects the K3 row of the compute estimate, which priced 7 of the 8 uses that section 10 lists. It changes no test or outcome.

`AMENDMENT_1.md` and `AMENDMENT_2.md` are left as published. Where Amendment 2's D14 text or its K5 map is quoted below, this amendment supersedes it.

## SK1. The seed number in the key of each K5 flow-unit pool

Found by: the independent check of Amendment 2.

Old text, `PREREG.md` lines 428 to 429 (reading D14, K5):

```text
  - K5 (B9): instrument `K5b:<case>`, split `fit` or `verdict`, net `native`, segment the seed number, purpose `data`. Random detectors use `detectors-flow`. Each flow unit's pool uses instrument `K5b:<case>`, split `fit` or `verdict`, net `native`, segment `flow-L<level>-q<unit>`, purpose `surrogates`.
  The whole-series surrogate that makes the IAAFT cascade starts from the generator of instrument `K5b:cascade_iaaft`, split `fit`, net `native`, segment the seed number, purpose `whole-surrogate`.
```

The segment field `flow-L<level>-q<unit>` has no seed number, so the 10 seeds of a case share one key per unit. Built from the plan's counts (10 series sets of 110 units, 10 seeds), the 11,000 pools have 880 distinct keys. The independent check counted 14 series per seed and found 15,400 pools with 1,540 keys. Both counts show the same fault.

New text: segment `s<seed>-flow-L<level>-q<unit>` (full text under SK7).

Reason: the 10 seeds are independent replicates, and independent replicates must not share random starts. With shared starts the "9 of 10 seeds" rule would count one random start ten times.

Effect: new draws for every K5 flow-unit pool. No threshold or criterion changes.

## SK2. The run in the key of each K5 flow-unit pool

Found by: the review of the keys after publication.

Old text: the same lines, net `native` for every pool. The three runs of the mapped cascade (the primary run and the two amplitude-map runs) cut different streams into units, but their pools take one key per seed and unit.

New text: net the run (`native`, `amp_scores` or `amp_lognormal`), as for the K4 pools.

Reason: the runs are separate tests, each judged at its own level, whose p-values are combined by the rule of section 5 (largest p times the number of runs). They are not a pairing the design intends, so their pools must not share random starts. With the seed added but the run missing, the 11,000 pools still have only 8,800 keys.

Effect: new draws for the pools of the two amplitude-map runs. No threshold or criterion changes.

## SK3. The K3 pool instrument

Found by: the independent check of Amendment 2.

Old text, `PREREG.md` line 425:

```text
  Each pool uses instrument `K3:<case>`, split `synthetic`, net the use, segment the seed number, purpose `surrogates`. The circular-shift control draws its shifts from the pool key of `native4096`.
```

New text: each pool uses the instrument of the data draw its segment comes from, `K3:<case>:<length>`. `<length>` is now defined as the length of the drawn block, N + 128 samples (D16): 4224 for `native4096` and `placement`, 2176 for `native2048` and `wlen2048`.

Reason: the general rule says a pool takes the key of its segment. The net field (the use) already kept the keys apart, so no two pools shared a key (6,400 pools, 6,400 keys either way).

Effect: the instrument string of every K3 pool changes, so K3 pools get new draws. The code at `99533df` used `K3:<case>`. No threshold or criterion changes.

## SK4. Random detectors keyed by their pair or criterion

Found by: the independent check of Amendment 2 (K4 and K5). Real data added by this amendment.

Old text, `PREREG.md` line 426 (K4) and line 428 (K5), the detector sentences:

```text
Random detectors use purposes `detectors-arrow` and `detectors-profile`, with net the run.
```

```text
Random detectors use `detectors-flow`.
```

The sentences give the purpose and, for K4, the run, but not the pair or criterion. Read with the other fields of their lines (instrument of the template's kind, segment the seed number), A>B, A>C and A>Aprime share one detector key per seed, run and purpose (200 detector sets, 120 keys). In K5 the three runs of the positive criterion and the y' criterion share one key per seed (50 sets, 20 keys).

New text: K4 detectors use instrument `K4:<A>><B>` for the ordered pair (`A>B`, `A>C`, `A>Aprime`, `S>Sr`, `Sr>S`), split `verdict`, net the run, segment the seed number. K5 detectors use instrument `K5b:<A>><B>` for the criterion (`cascade>cascade_rank`, `cascade>yprime`, `cascade_iaaft>cascade`), split `verdict`, net the run, segment the seed number.
Real-data detectors use instrument `<A>><B>` for the ordered pair of instruments, split `verdict`, net the run, segment `0`.

Reason: each criterion is a separate test with its own random detectors, not a pairing the design intends. One sharing is intended and is now stated: the same transfer with B's C2 or C3 series in place of B (section 5, C5) uses the detectors of the transfer it checks, so that only B changes.

Effect: new draws for every K5 detector set. In K4, the code at `99533df` already named the pair (`K4:A>B` and so on), so only the A' pair changes, from `A>Ap` to `A>Aprime`.

## SK5. Pools and F noise of control series

Found by: this amendment's key check.

Old text, `PREREG.md` line 421 and line 430, the general rule and the controls:

```text
- D14. The seed-rule fields are master|instrument|split|net|segment|purpose|index, with index 0 unless stated. One generator per key gives a whole series or a whole pool in order. A pool's key is that of its segment with purpose `surrogates`. Fields for each use:
```

```text
  - Controls: C2, C3 and C4 use purposes `C2`, `C3` and `C4` with the key of their segment (for C4, segment the series number). Law 2b instance F uses `law2b-F` and the G1 null replicates `law2b-null`.
```

C2 and C3 take "the key of their segment". By the general rule their pools then take that key with purpose `surrogates`, which is the key of the real segment's own pool. C4 series i likewise takes the pool key of real segment i. At the plan's upper bounds, 28,224 control and segment pools have 16,736 keys.

New text: a draw made from a control series (its pool, or instance F's noise) puts the control's name and a hyphen before the purpose it would have on a segment: `C2-surrogates`, `C3-law2b-F`, `C4-surrogates`. C4 series i uses the instrument and channel, split `verdict`, net the run, segment i, purpose `C4`.

Reason: a control must be independent of the segment it is compared with. A control pool that starts from the segment pool's random start would tie the control's result partly to the real segment's result by construction.

Effect: real data only, and no run has made these draws. (The code at `99533df` kept them apart with a tag of its own, which the plan did not state.) No known-answer test uses C2 to C4.

## SK6. Keys for Law 2b

Found by: this amendment's key check.

Old text, `PREREG.md` line 430 (quoted under SK5): "Law 2b instance F uses `law2b-F` and the G1 null replicates `law2b-null`."

Three faults:

- The 10 null replicates of a test have no field that tells them apart, so all 10 take one key (at a reduced grid of segments, 14,480 replicate series have 200 keys).
- The pools of a series changed by an instance (W, F, D, and in the scale flow B and R) take, by the general rule, the key of the unchanged segment's pool (4,864 pools, 1,216 keys at the upper bounds of presence segments).
- The pre-data checks of each instance (section 12a, G1) have no stated keys.

New text: an instance is applied to the data and control series of its paired test, which keep their keys. Every random draw made after an instance is applied uses the key the same draw has without the instance, with net `law2b-<instance>:<run>`.
Where F is added to a whole stream before block averaging, its segment field is the seed number in K5 and `stream` on real data. Null replicate r of an instance, for r from 1 to 10, draws its C2 series with net `law2b-<instance>:<run>`, purpose `law2b-null` and index r, and every draw made in the replicate uses index r.
Keying the replicate's C2 series by the instance is a choice: without it, the rule above would keep the net of the series without the instance, and the replicates of different instances would share random starts. G1 asks for 10 independent replicates for each instance that passes, so they are keyed apart.

Reason: the 10 replicates are independent replicates and must not share random starts. A transformed test is not a pairing with the untransformed one, so its new pools get new starts. Two sharings are intended and stated: Q, H, M, O4 and E use the pools of their paired test, since they change only the statistic or the selection (the compute table already assumes this).
And a series under one instance has one pool and one set of null replicates, used by every test that uses it, as the confirmatory tests share one pool per segment.

Effect: the Law 2b instance tests are not built yet (Amendment 2, B11), so no existing draw changes.

## SK7. Fields left open, and the keys shared by design

Found by: this amendment's key check.

Old text, `PREREG.md` lines 421 to 432 (reading D14, whole):

```text
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
```

Fields the old text left open, now stated: seeds are numbered from 0. The tied waveform's pool has split `synthetic`, net `native`, segment `0`. The must-fail variants of K1 use the keys of the series they run on. A' has instrument `K4:Aprime:<split>`, split `<split>`, and its block index is the position in the shuffled order.
A' pools use kind `Aprime`. The K4 runs are named `native` and `placement`. The K5 cases are named, including `cascade_shuffled`, drawn from its own generator, and the fit series of y' that gives its level shift. Real-data runs and flow units are named.
A flow unit's pool is named by the series it is cut from, not by the draw that series is made from (`K5b:cascade_rank`, `K5b:cascade_iaaft`): read the other way, the rank-mapped cascade's pools in the primary run would share the keys of the cascade (verdict) pools, and the IAAFT cascade's those of the cascade (fit).
A list of every key used by more than one draw, with its reason, closes D14.
Two counts the plan did not fix become readings D20 and D21: which K4 streams each criterion scores, and the seed count of K1's comparison at 4,096 and 2,048 samples (20, as both checks of the keys had assumed).

New text, replacing reading D14 (section 11a) in full:

```text
- D14 (as amended by Amendment 3). The seed-rule fields are master|instrument|split|net|segment|purpose|index. Index is 0 unless stated, and seeds are numbered from 0. One generator per key gives a whole series, a whole pool or a whole set of random detectors, in order.
  Two draws that the plan treats as independent never share a key. Keys used by more than one draw are listed under "Shared by design" below, each with its reason. `checks/amendment_3/seed_keys.py` builds every key and checks both statements.
  A pool's key is that of the series it is made from, with purpose `surrogates`. A draw made from a control series (its pool, or instance F's noise) puts the control's name and a hyphen before the purpose it would have on a segment: `C2-surrogates`, `C3-law2b-F`, `C4-surrogates`.
  - K2: instrument `K2:<class>:<length>`, split `synthetic`, net `native`, segment the seed number, purpose `data` for the series and `surrogates` for its pool. The must-fail control (raw-value surrogates) runs on the exp version of the AR(1) 0.9 draw at 4,096 samples, seeds 0 to 199, and draws its raw-value surrogates from that draw's pool key.
  - K1: instrument `K1:<class>:<length>` with the K2 fields otherwise. The exp and cube versions, the negation and the comparison maps are maps of the plain draw and use its data and pool keys. The integer-valued series of B6 use `K1int:<class>:1024` with the K2 fields otherwise, and their maps use the same keys.
  The tied waveform is fixed. Its pool, used by the waveform and its three maps, has instrument `K1wave:4096`, split `synthetic`, net `native`, segment `0`, purpose `surrogates`. The must-fail variants run on the same series with the same keys.
  - K3: the data draw uses instrument `K3:<case>:<length>`, split `synthetic`, net the use, segment the seed number, purpose `data`. `<length>` is the length of the drawn block, N + 128 samples (D16): 4224 for `native4096` and `placement`, 2176 for `native2048` and `wlen2048`, the four uses with their own data draw.
  The nets `bm2`, `sub2`, `q12` and `q8` are applied to the `native4096` draw. Each pool uses the instrument of the data draw its segment comes from (`K3:<case>:<length>`), split `synthetic`, net the use, segment the seed number, purpose `surrogates`. The circular-shift control draws its shifts from the pool key of the shots at `native4096`.
  - K4: instrument `K4:<kind>` (kinds `A`, `B`, `C`, `S`, `Sr`), split `fit` or `verdict`, net `native`, segment the seed number, purpose `data`. A' is made from the A stream of the same split. Its draws use instrument `K4:Aprime:<split>`, split `<split>`, net `native`, segment the seed number, purposes `shuffle` and `block-surrogate`.
  For `block-surrogate` the index is the block's position in the shuffled order, 0 to 32. Each segment's pool uses instrument `K4:<kind>:s<seed>` (kind `Aprime` for A'), split `fit` or `verdict`, net the run (`native` for the primary grid, `placement` for the grid shifted by half a block), segment the segment number, purpose `surrogates`.
  Random detectors use instrument `K4:<A>><B>` for the ordered pair (`A>B`, `A>C`, `A>Aprime`, `S>Sr`, `Sr>S`), split `verdict`, net the run, segment the seed number, purposes `detectors-arrow` and `detectors-profile`.
  - K5 (B9): data draws use instrument `K5b:<case>`, split `fit` or `verdict`, net `native`, segment the seed number, purpose `data`. The cases with their own draw are `expo`, `cascade`, `cascade_shuffled` (a cascade drawn from its own generator, then shuffled with the same generator), `y` and `yprime` (fit and verdict, the fit series giving its level shift).
  The IAAFT cascade is made from the cascade (fit) series, starting from the generator of instrument `K5b:cascade_iaaft`, split `fit`, net `native`, segment the seed number, purpose `whole-surrogate`. The rank-mapped cascade (`cascade_rank`, SK8) is a map of the cascade (verdict) draw.
  Each flow unit's pool uses instrument `K5b:<case>` named by the series it is cut from, not by the draw that series is made from (`K5b:cascade_rank` for the rank-mapped cascade, `K5b:cascade_iaaft` for the IAAFT cascade), split `fit` or `verdict`, net the run (`native`, `amp_scores` or `amp_lognormal`), segment `s<seed>-flow-L<level>-q<unit>`, purpose `surrogates`.
  Random detectors use instrument `K5b:<A>><B>` for the criterion (`cascade>cascade_rank`, `cascade>yprime`, `cascade_iaaft>cascade`), split `verdict`, net the run, segment the seed number, purpose `detectors-flow`.
  - Real data: instrument the instrument and channel (in the instrument net, the second channel), split `fit` or `verdict`, net the run, segment the segment number, or `flow-L<level>-q<unit>` for a flow unit. The runs are named `native`, `bm2`, `sub2`, `q12`, `q8`, `placement`, `wlen`, `instrument`, `amp_scores` and `amp_lognormal`.
  Random detectors use instrument `<A>><B>` for the ordered pair of instruments, split `verdict`, net the run, segment `0`, purposes `detectors-arrow`, `detectors-profile` and `detectors-flow`.
  - Controls: C2 and C3 use the key of their verdict segment or flow unit with purposes `C2` and `C3`. C4 series i, for i from 0 to 31, uses the instrument and channel, split `verdict`, net the run, segment i, purpose `C4`. Their pools follow the rule for control series above.
  - Law 2b (section 12a): an instance is applied to the data and control series of its paired test, which keep their keys. Every random draw made after an instance is applied (instance F's noise, purpose `law2b-F`, the pools of a series the instance changes, random detectors) uses the key the same draw has without the instance, with net `law2b-<instance>:<run>`.
  The instances that change the series are W, F and D, and in the scale flow also B and R. Where F is added to a whole stream before block averaging, its segment field is the seed number in K5 and `stream` on real data. The pre-data checks of each instance follow the same rule on the known-answer draws.
  G1 null replicate r of an instance, for r from 1 to 10, draws its C2 series with net `law2b-<instance>:<run>`, purpose `law2b-null` and index r, so replicates of different instances never share random starts. Every draw made in the replicate (its controls, pools, F noise and random detectors) also uses index r.
  - Shared by design (the only keys used by more than one draw):
  (1) K1: the 13 series of a class and seed share the plain draw's data and pool keys, the 4 series of an integer-valued class and seed share theirs, and the waveform and its 3 maps share one pool key. The identities of K1 need the same random start. The versions compared at 4,096 and 2,048 samples share the plain draw.
  (2) K2: the must-fail control uses the AR(1) 0.9 data and pool keys at 4,096 for seeds 0 to 199. Only the surrogate method differs, so a flag can only come from the method.
  (3) K3: the nets `bm2`, `sub2`, `q12` and `q8` use the `native4096` data draw, because a net is a change of observation of the same series. The circular-shift control uses the shots' `native4096` pool key, so that only the surrogate method differs.
  (4) K4: A' is made from the A stream of the same split and seed, because the control removes structure from that stream. Under D20's second reading, the placement-run detectors of A>B, A>C and A>Aprime use the keys of D20's own, so that only the template differs between the two readings.
  (5) K5: the rank-mapped cascade is a map of the cascade (verdict) draw, and the IAAFT cascade is made from the cascade (fit) draw, as their criteria require.
  (6) Real data: the arrow and profile transfers use the presence pools of the same segments (no new draw). The same transfer with B's C2 or C3 series in place of B (section 5, C5) uses the random detectors of the transfer it checks, so that only B changes.
  (7) Law 2b: an instance runs on the data and control series of its paired test (no new draw), and Q, H, M, O4 and E use its pools, since they change only the statistic or the selection. A series under one instance has one pool and one set of null replicates, used by every test that uses that series under that instance, as the confirmatory tests share one pool per segment.
  The pre-data checks use the known-answer data draws (K2 seeds 0 to 199 at 4,096, K3 `native4096`, K4, K5), so that only the instance differs from the known-answer test.
  - Draws not listed here follow the names above. The order of draws inside each generator, and the random-number calls used, are fixed by the generator source at the code commit recorded with the known-answer results. That commit's hash is recorded with every result, and any later change to a generator is a plan amendment.
```

Reason: each open field was a place where two builders could make different draws, and the list of shared keys makes every pairing a stated design choice.

New readings D20 and D21 (section 11a), each with the basis on which it was chosen:

```text
- D20 (Amendment 3). The streams each K4 criterion uses. Templates come from the fit streams of A, S and Sr in the primary grid, so those segments have pools, and the placement run reuses those templates. Level shifts come from the fit streams of every kind, A' included, and need no pools.
  Pools are drawn for the verdict streams of B, C and A' in both runs (`native` and `placement`), and for the verdict streams of Sr and S in the primary run. Random detectors, arrow and profile, are drawn for A>B, A>C and A>Aprime in both runs, and for S>Sr and Sr>S in the primary run, where the blind spot is reported.
  Basis: the plan text before Amendment 3 did not fix this stream set. D20 adopts the set in the code's K4 script. The plan's author read that source and chose D20 on 2026-11-22 while writing Amendment 3, knowing no K4 outcome.
  The code's author reports, from its git history and run outputs, the following, which the plan's author and the independent check could not verify. The set first appears in code commit `a894e31` (the commit before it had an older, smaller set).
  The code's author had seen the K4 results of the frozen-plan code before writing this set, and no output of this set. The set was in the working tree when the first K4 smoke run was made and was committed about 1 hour 45 minutes after that run finished. A rerun on the committed script reproduced that run's output byte for byte, so the set scored in the smoke run is the committed set.
  No later commit changed which streams are scored (`a714ef7` changed only the A' control rule of D17). End of the code's author's report. Those smoke outcomes were known to the code's author and to the party who routed the questions. So an earlier K4 outcome, under the frozen plan, could have shaped this scoring choice.
  Bound: K4 passes only if it passes under D20 and also under a second reading, fixed now, in which each run takes its templates and level shifts from the fit streams cut in that run's own grid. The second reading draws pools for the fit streams of A, S and Sr in the placement grid and, to score the blind spot in both runs, for the verdict streams of S and Sr in that grid.
  It also draws random detectors, arrow and profile, for S>Sr and Sr>S in the placement run.
  The control's rule that a seed counts if p is at most 0.01 in any run is judged within each reading, never across the two readings pooled.
  Both readings are reported. A failure under either is a failure of K4, and agreement of the two cannot rescue a failed criterion or control.
  The Law 2b instances' paired K4 tests (section 12a) use D20 alone, because those checks are an extra guard on top of G1, and a second reading there would add 3 x 3,664 processor-seconds per mode. The code is checked against D20 and its second reading and changed where it differs: it now prints only the arrow p of the blind spot, and D20 asks for both detectors.
  Real data: the plan does not settle which template the window-placement run of a transfer uses. This is a new choice, made on the same basis and at the same time: that run uses instrument A's fit-stage template from the primary grid, as K4 does under D20. The second reading is not used on real data.
  Reason: templates are fit-stage results, committed before any verdict file is opened (section 11, commit order), and the placement net changes only how B's verdict segments are cut.
- D21 (Amendment 3). At 4,096 and 2,048 samples K1 compares normal scores on 20 seeds per class (seeds 0 to 19 of `K1:<class>:<length>`), the same count as at 1,024 samples.
  Basis: chosen on 2026-11-22 while writing Amendment 3, from the count at 1,024 samples. It adds identity checks only and changes no criterion.
```

D20 needs more than a count. The plan text did not fix the K4 stream set, and D20 adopts the set in the code's K4 script. The code's author wrote that set after seeing the K4 results of the frozen-plan code (D20 gives the history of the script, as the code's author reported it from git history and run outputs).
So an earlier K4 outcome could have shaped the scoring. Three bounds were weighed. Showing from the plan text alone that D20's set is the only reading is not possible: the text does not say which template the placement run uses or in which runs the blind spot is scored.
A non-governing sensitivity report under another reading would still let a K4 pass rest on the adopted set. The stricter bound is chosen: K4 passes only if it passes under D20 and under a second reading fixed now (each run takes its templates and level shifts from the fit streams cut in its own grid, and the blind spot is scored in both runs).
A pass can then not depend on which of the two readings was chosen. Section 10 (K4) and the gate sentence before the known-answer tests point to this rule, and the compute row of the Law 2b paired K4 tests now says it uses the K4 row (D20 alone). The second reading adds 1,600 pools and 40 detector sets, keyed by D14 as written, with 60 detector sets shared by design with D20's own.
It adds 3,664.00 processor-seconds per mode to the compute estimate (SK9).

Effect: in the code at `99533df`, A' used split `verdict` for both streams and kind `Ap` for its pools, so the A' fit-stream draws and the A' pools change. The other stated fields were not compared field by field with the code. Before the full known-answer run, the code's keys are checked against D14 as amended.

Check. `checks/amendment_3/seed_keys.py`, standard library only, identical output in the three modes. It builds every key from the plan's counts, names for each draw the random start it is meant to use, and passes a family only when random starts and keys correspond one to one. Where the plan does not fix which streams a run scores, it also builds a superset.
Real-data counts are the plan's upper bounds (32 segments per run, 7 levels of at most 32 flow units), and the null replicates use a reduced grid of segments that exercises every field the replicate rule adds. The published wording of each corrected part must show its fault, and two planted faults must be flagged. All hold.

| Family | Draws | Distinct keys | Shared by design |
|---|---|---|---|
| K1 | 6,884 | 1,001 | 5,163 draws: the 13 series of a class and seed and the 4 integer-valued series (data and pool keys), the waveform and its maps. 720 draws: the versions compared at 4,096 and 2,048 |
| K2 | 36,400 | 36,000 | 400 draws: the must-fail control's data and pool keys |
| K3 | 13,000 | 9,600 | 3,200 draws: four nets on the `native4096` draw. 200 draws: the circular-shift control |
| K4, the streams of D20 and its second reading | 6,180 | 6,100 | 20 draws: A' made from A. 60 draws: the second reading's placement-run detectors of A>B, A>C and A>Aprime |
| K4, every kind, split and run | 8,680 | 8,660 | the same 20 |
| K5, the 10 series sets of B9 | 11,150 | 11,130 | 20 draws: the rank-mapped cascade and the IAAFT cascade made from the cascade |
| K5, every case, split and run | 46,420 | 46,400 | the same 20 |
| Real data: pools and detectors, upper bounds | 7,436 | 7,172 | 264 draws: the C5 transfers use the detectors of the transfer they check |
| Controls C2 to C4 with the segment pools beside them | 28,224 | 28,224 | none |
| Law 2b pre-data checks | 104,320 | 99,520 | 4,800 draws: the checks reuse the known-answer data draws |
| Law 2b instance tests, real data | 89,376 | 89,376 | none |
| Law 2b null replicates, reduced grid | 99,240 | 99,240 | none |
| All amended families together | | 417,545 | no key used by two families, 417,545 distinct 64-bit seeds |

The published wording, built the same way: K5 pools 11,000 draws with 880 keys (8,800 with the seed added, 1,100 with the run added). K4 detectors 200 with 120. K5 detectors 50 with 20. Controls with segment pools 28,224 with 16,736. Law 2b changed-series pools 4,864 with 1,216. Null replicates 14,480 with 200. K3 pools 6,400 with 6,400 (wording only).
K5 pools with the mapped series named by their source draw 11,000 with 8,800.

## SK8. Amplitude maps that cannot overflow or lose values

Found by: the code's author, from a crash (overflow) in a smoke run of the redesigned K5 at seed 0. See the opening for what the plan's author saw.

Old text, `PREREG.md` line 191 (section 5, the amplitude-map row), line 356 (K5, first sentence) and line 358 (K5, the series list):

```text
| Amplitude map | strictly increasing maps | exact for presence and for the arrow and profile transfers, because surrogates are made from normal scores (K1). Run as two statistical nets (normal scores of the ranks, and exp of the series standardised to unit variance, each applied to the whole stream before block averaging, as reading D10 states) for the scale-flow transfer only |
```

```text
  - Transfer criteria. Cascade (fit) to cascade after a monotone map (exp of the standardised series, verdict) must give flow transfer p at most 0.001 in the primary run and in both amplitude-map runs.
```

```text
the IAAFT cascade (fit), and the exp-mapped cascade (verdict) in three runs, 10 sets of 110 units.
```

### The cause

For n values standardised to unit variance every |z| is below sqrt(n). exp(z) overflows above 709.78. At n = 2^19 (K5) |z| can reach 724, and the exp-mapped cascade, standardised, reaches it whenever one value dominates the series.
The overflow is not the whole fault. Computed in a form that cannot overflow (exp(z - (max z + min z)/2), a positive multiple of exp(z), which the flow does not see), the map still destroys the values.
In 10 seeds of the cascade (`checks/amendment_3/amp_maps.py`, seeds outside every test), the exp-mapped cascade after standardising keeps 2 to 16 distinct values of 524,288, so no floating-point form of exp of it keeps the values apart.
The exp-mapped cascade itself keeps its distinct values when exp(z) is computed directly, but loses some in 2 of the 10 seeds in the overflow-safe centred form exp(z - (max z + min z)/2), so centring is no general cure.
So K5's positive criterion as Amendment 2 wrote it could not be evaluated. A real stream with rare large events puts a standardised series in the same position, so the real-data net shares the fault.

### The candidates

Two replacements were weighed, on the same synthetic streams, before any known-answer run under this amendment and without any outcome:

- cube: y^3 + y with y = x / max|x|, the first map of B5.
- lognormal: exp of the normal scores Phi^-1((r - 1/2) / n) of the mid-ranks r. The scores are those the surrogate step already computes.

Streams: AR(1) 0.9 (2^16 samples, light tails), the same with 5 spikes of 1,000 standard deviations (rare large events), the same AR(1) made integer-valued as round(8 z) (ties), and the K5 cascade (2^19 samples). Two measures of how much a map changes the marginal:
top1, the share of the sum of squared deviations carried by the largest 1 percent of values, and r, the Pearson correlation between the stream and the mapped stream. r = 1 is a linear rescaling, which the flow does not see, so 1 - r is what the net can change. The rank correlation is 1 for every candidate by construction.

| Stream | native top1 | cube: top1, r | lognormal: top1, r | normal scores (`amp_scores`): top1, r |
|---|---|---|---|---|
| AR(1) 0.9 | 0.070 | 0.102, 0.993 | 0.484, 0.760 | 0.072, 1.000 |
| AR(1) 0.9 with 5 spikes | 0.988 | 0.997, 0.998 | 0.484, 0.305 | 0.072, 0.148 |
| integer-valued AR(1) | 0.070 | 0.102, 0.993 | 0.481, 0.762 | 0.072, 1.000 |
| K5 cascade | 0.956 | 0.968, 0.974 | 0.486, 0.724 | 0.072, 0.290 |

Comparison on the four questions:

1. Representability for every finite stream. Cube is finite (|y^3 + y| at most 2), but the division by max|x| can merge neighbouring values, so it needs the guard. Lognormal depends on the stream only through its mid-ranks. Its values lie below exp(Phi^-1(1 - 1/(2n))), which is below 1,251 for n up to 10^12. Tied values share a mid-rank and so a value.
Distinct mid-ranks give scores at least sqrt(2 pi) / n apart, more than a thousand times their rounding for streams shorter than 10^12 samples. So it keeps ties as ties and creates none. Both passed the guard on all four streams, including the tied one.
2. How much the marginal changes. Cube changes it little and least where it matters: on the spiky stream and the cascade, top1 stays near its native value and r stays above 0.97. Lognormal gives every stream the same skewed, heavy-tailed marginal (top1 0.48), so it differs strongly from the native run on every stream, and from the Gaussian marginal of `amp_scores` (top1 0.07).
3. Dependence on one extreme value. With the middle value of the AR(1) stream replaced by 10^6 standard deviations, cube becomes a linear rescaling of every other value (1 - r falls from 0.0072 to 0 at the printed precision), so the net turns into the primary run.
   Lognormal moves every other value by at most one rank (1 - r 0.240 without, 0.235 with). Only 0.5 percent of the other mapped values change by more than 0.1 percent, the largest by 22 percent, in the top tail, where one rank moves the score most.
4. K5 and the real-data net. Cube would make the mapped cascade almost the cascade (top1 0.968 against 0.956, r 0.974), so passing would show little. On real streams with rare large events, cube would leave the net close to the primary run, which is the weakness that the net exists to avoid.

### The ruling

The scale flow's second amplitude-map net becomes `amp_lognormal`, exp of the normal scores of the mid-ranks, applied to the whole stream before block averaging (D10). With the primary run and `amp_scores` it spans three clearly different marginals: the stream's own, Gaussian, and log-normal.
The guard of K1 still applies, as everywhere, but by D19 it cannot fail for streams shorter than 10^12 samples. The rule for a map that is not representable stays in section 5: that run does not pass and is never adverse, so the pair is "neither". Never a pass.

K5's mapped cascade becomes the rank-mapped cascade, the mid-ranks of the cascade (verdict). Both amplitude nets depend on a stream only through its mid-ranks, so for any increasing map of the cascade that keeps its distinct values they give exactly the series they give for the cascade itself (checked exactly in `amp_maps.py`).
The map of the mapped cascade therefore matters only in the primary run, and it should differ from both nets and from the cascade. Lognormal would make the primary run identical to the `amp_lognormal` run. The mid-ranks give a uniform marginal (top1 0.029, r 0.205 with the cascade), the farthest from the cascade's own (0.956).
The three runs of the positive criterion then see a uniform, a Gaussian and a log-normal marginal, none of them the cascade's.

New text: section 5, the amplitude-map row:

```text
Run as two statistical nets for the scale-flow transfer only: `amp_scores`, normal scores of the ranks, and `amp_lognormal`, exp of those normal scores, each applied to the whole stream before block averaging, as reading D10 states. Both depend on the stream only through its mid-ranks, so they are finite, keep tied values tied and create no new ties (reading D19). A map is representable on a stream if the mapped stream is finite and has as many distinct values as the stream (the guard of K1). If a map is not representable on a stream that a run uses, that run counts as not passing and never as adverse, so the pair is "neither" for that transfer, recorded as "map not representable" (Amendment 3, SK8)
```

Section 10, K5: the monotone map of the positive criterion becomes "the rank-mapped cascade, the mid-ranks of the cascade", and "A seed in which this map or a run's amplitude map fails the representability guard counts as failing the criterion." The series list says "rank-mapped cascade". Seed keys (D14): case `cascade_rank`, run `amp_lognormal`.
New reading D19 (section 11a) makes every exp or power overflow-safe by rule:

```text
- D19 (Amendment 3, SK8). Every exp or power that this plan applies to a series is overflow-safe by rule, and every amplitude map is judged by the representability guard of K1 (the mapped series is finite and has as many distinct values as its input).
  (a) On a series of n samples standardised to unit variance, every |z| is below sqrt(n). For the exp and cube versions of K1 and the K2 control, n is at most 4,096, so exp(z) < 6.3e27 and |z|^3 < 2.7e5.
  (b) The scale flow's amplitude maps depend on a stream only through its mid-ranks r: `amp_scores` is the normal scores Phi^-1((r - 1/2) / n), and `amp_lognormal` is exp of those scores. The scores lie within Phi^-1(1 - 1/(2n)) of 0, which is below 7.131 for n up to 10^12, so exp of them is below 1,251.
  Tied values share a mid-rank and so a score. Distinct mid-ranks differ by at least 1, so their scores differ by at least sqrt(2 pi) / n, which for streams shorter than 10^12 samples is more than a thousand times the rounding of the scores. These maps therefore keep ties as ties, create none, and pass the guard.
  K5's rank-mapped cascade is the mid-ranks themselves. K1's comparison maps act on y = x / max|x|, with |y| at most 1, so y^3 + y and exp(y) are finite.
  (c) The synthetic generators apply exp and powers only to Gaussian draws or to bounded quantities: the cascade weights exp(0.5 Z - 0.125), g^2, |h|, y_t and y', the decay kernel of the shots (exp of minus the lag over 10, for lags up to 100), the frequency powers of the power-law spectra, and x(1 - x) in the logistic map, with x in [0, 1].
  A cascade value overflows only if one of its 19 standard normal draws exceeds 74.9.
  No other exp or power is applied to data or to a standardised series. A map that fails the guard is handled as section 5 states for the scale-flow nets, and as section 10 states for K1 and K5.
```

### Does the change alter a statistic where the old map was representable?

- Presence, the arrow transfer and the profile transfer: no. Amplitude maps are not runs of these tests, and their statistics are exactly unchanged by any strictly increasing map that keeps the distinct values, because surrogates are made from normal scores (section 4.3, K1).
- The scale flow: yes, in the `amp_lognormal` run. Block averaging uses amplitudes, so the flow is unchanged by linear rescaling but not by other increasing maps (section 4.1). A different map is a different net, and that run gives a different statistic on every stream.
  The flow's other four runs (primary, instrument, window placement, `amp_scores`) are unchanged.
- K5: the rank-mapped cascade replaces the exp-mapped one, so the primary run of the positive criterion changes, and its second amplitude run now uses `amp_lognormal`. Its `amp_scores` run is unchanged.

Real-data nets touched: the second amplitude-map run of the scale-flow transfer, for every ordered pair. Known-answer tests touched: K5's positive criterion, and the paired K5 tests of the Law 2b instances, which use the same runs. K1, K2 and the other places in D19 keep their definitions, and are now safe by a stated bound. No threshold or run count changes.

Check. `checks/amendment_3/amp_maps.py` (needs numpy), identical output in the three modes: the exact bounds, the old map on the cascade, the candidate table, the single-value test and the K5 identity above, with must-fail controls of the guard and of the two measures.

## SK9. The K3 row of the compute estimate

Found by: this amendment, while counting K3's keys.

Old text, `PREREG.md` line 384:

```text
| K3 | plan, section 10: 4 cases x 200 seeds x 5.5 pools (7 runs), plus 200 pools for the must-fail control | 10,534.00 |
```

Section 10 lists 8 K3 uses: native at 4,096 and at 2,048 samples, block mean by 2, subsampling by 2, two quantizations, window placement and window length N/2. Priced at their lengths (a pool on n samples costs n/4096), they come to 1 + 1/2 + 1/2 + 1/2 + 1 + 1 + 1 + 1/2 = 6 pools per case and seed. The row priced 5.5 pools for 7 runs, which leaves out native at 2,048.

New text: "4 cases x 200 seeds x 6 pools (8 uses), plus 200 pools for the must-fail control | 11,450.00". A new row prices the second reading of D20 (SK7): "10 seeds x 160 pools ... | 3,664.00".
The known-answer total becomes 258,126.41 processor-seconds per mode. One mode without an adverse outcome: 258,126.41 + 2,917.46 + 27,938.00 = 288,981.87 processor-seconds, about 80.3 processor-hours.
Three modes: 866,945.61, about 240.8 processor-hours. The Law 2b worst case is unchanged (243,926.22 per mode), since its K3 checks use the native net only. The Law 2b instances' paired K4 tests use D20 alone, so their row is unchanged.

Check. `checks/amendment_3/compute_k3.py`, exact rational arithmetic, identical output in the three modes. It is Amendment 2's component script with the K3 row changed and the K4 row of D20's second reading added.

Effect: the compute estimate only, 916 processor-seconds more per mode for K3, and 3,664 for D20's second reading.

## Erratum to Amendment 2

`AMENDMENT_2.md` stays unedited as a frozen record. Two statements in the published files were wrong:

- `PREREG.md` line 23 (change log) said that Amendment 2 was made "before any known-answer result under the amended plan had been seen". `AMENDMENT_2.md` lines 9 to 15 say that items B5 to B12 were written after the code built for Amendment 1 had run a smoke version of the known-answer tests, and that the builder's questions stated some observed behaviour. Lines 9 to 15 govern.
  The change-log sentence is replaced by: "Items B1 to B4 were written before the plan's author had seen any known-answer result under the amended plan. Items B5 to B12 were written after the code built for Amendment 1 had run a smoke version of the known-answer tests (one twentieth of the plan's seeds, and the full 10 seeds for K4 and K5).
  Its outcomes were known to the code's author and to the party who routed the questions. The plan's author read none of its outputs, but the builder's written questions state some observed behaviour, and B11 uses one smoke figure (`AMENDMENT_2.md` lines 9 to 15, which govern)."
  The independent check proposed that B1 to B4 were written "before the code builder's smoke run of the known-answer tests had been seen". `AMENDMENT_2.md` says only that the plan's author had not then seen any result, so the replacement says that.
- `AMENDMENT_2.md` line 83 (item B3) says the change log is followed by "the entries of this amendment (B1 to B4)". It meant B1 to B12, which is what the published change log holds.

## Also updated

`PREREG.md`: the status line, which now says what has been run, the change log (the account of Amendment 2 corrected as in the erratum, and an Amendment 3 paragraph with items SK1 to SK9), the heading of section 11a, the compute row of K3 and its totals, and the compute header sentence of section 11, which now names `checks/amendment_3/compute_k3.py` (SK9).
`README.md`: the status line, which now says what has been run, the file list and the hash table, now with `AMENDMENT_3.md`, and a note on what the check scripts need.
`checks/amendment_2/ENVIRONMENT.md` records what the check scripts of Amendments 2 and 3 need, and the versions behind their committed outputs. It is a note, not a plan change.

## What was not changed

- `AMENDMENT_1.md` and `AMENDMENT_2.md` are left as published. This amendment supersedes Amendment 2's D14 and its K5 map.
- No threshold or test count. The only decision rule made stricter is K4's, by D20 (SK7). The compute changes are listed under SK9.
- The folder `independent_check/` is not touched.
