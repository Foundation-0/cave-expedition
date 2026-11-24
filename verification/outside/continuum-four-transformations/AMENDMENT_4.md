# Amendment 4 to the pre-registration

Date: 2026-11-23. Base: branch `outside/continuum-four-transformations-prereg` at commit `4c6ecd1` (Amendment 3). Line numbers below refer to that commit.

This amendment was drafted before the plan's author saw any outcome of the code built for Amendment 3.
It is published on its own, before any full-count outcome of K1, K2 or K3 on that code exists. K6 has no seeds, so any run of it is a full run. Whether K4 and K5, whose full seed count is 10, had run on that code by then is stated in the disclosure below. Any repair to a known-answer test is a later amendment under C3.

No data file has been opened or parsed.

## What was known, and who shaped each item

- The tie question (C1) was raised by the team's audit of the detector code and by the code's author, who found that B8's clause, which counts a tie as not "below" in the adverse decision, lets a tie favour the adverse verdict, against B8's own reason and effect.
- The code's author and the coordinator, who routes the questions, had seen outcomes on the code built for Amendment 3 of smoke runs at 10 seeds for K1, K2 and K3 and of a run of K6 (which has no seeds), and smoke runs of K4 and K5 were running when this amendment was first drafted.
- The plan's author knew no outcome from the code built for Amendment 3 at any point while writing this amendment, and has not opened the build folder.
- First draft, fixed at 2026-11-23T06:27:08Z (`date -u`, SHA-256 `b43141e3e84a6f75cb09d49bd74f8c38136508e46a43959c39e0941b98868332`): C1, C2 and C3 from the plan's author's own reading of the plan text, with a reserved Part B.
- Rulings of the coordinator, who had seen the smoke outcomes above, recorded at 06:29:16Z: C1 accepted. C2 accepted with an added sentence that a failed instance is reported as "not tested" and that the final wording names each untested rescue route. C3 accepted with its limit of two rounds, to be stated as this amendment's choice. Part B removed, so that this amendment holds no repair.
- An independent check then asked for six corrections and suggested nine smaller ones. Its corrections are applied:
  the account of the tie conflict (C1), "if and only if" in each run (C1), the full direction of effect (C1), the Law 2b state of an untested instance (C2), and the definition of a round of repair (C3).
  Its smaller suggestions are applied too: the exact quotation of B8's clause, "at or below", the integer form, non-finite scores, exact equality as a tie, a mutation-test case for the tie rule, the place of the C2 text, and this list.
- A second check asked for six more corrections: K6 named apart because it has no seeds, the scope of an epoch and its table, the meaning of "seen" and of a definition, "transformed core" kept under C2, an instance check that does not close the data, and the reason for two rounds. All are applied. C3 now also treats a code-only change made after a full-count outcome as a repair.
- A third check asked for three more: what an epoch 0 run is (a diagnostic), the reading that an outcome of an epoch includes runs on the same data draws, which the table needs for K3 and K5, and a new epoch for every rerun after a full-count outcome, whatever changed.
  All are applied. Whether a code-only change counts as a round was decided by the plan's author without knowing any outcome: it does. The smaller suggestions are applied too.
- The new key epoch for repair reruns (C3, reading D14) was suggested by the coordinator, who had seen 10-seed smoke outcomes on the code built for Amendment 3. The plan's author adopted it and wrote the rest of C3, including which earlier amendments count as rounds, without knowing any outcome.

<!-- OUTCOME FACTS: BEGIN. This paragraph is filled by another hand, so that the plan's author stays blind. Nothing else in this file is changed when it is filled. -->
Outcomes on the code built for Amendment 3, and who had read them. Another hand than the plan's author wrote this paragraph, so that the plan's author stays blind. Times are UTC. Every run listed was made on key epoch 0. The code's author wrote a log of every run, `verification/outside/continuum-four-transformations/known_answer/OUTCOME_LOG.md`, on the code branch `outside/continuum-four-transformations-code` at commit `12cba0d`, which is public.

Where the log's column "Read by" does not give it, the times of reading, the exact K6 finishing times, the commit of the last change to the code K6 exercises, the statements on ties, and the statement that the plan's author was shown no outcome are statements of the code's author and the coordinator. The plan's author and the independent check could not verify them. Times of first reading are approximate.

- Publication: 2026-11-23T11:40:28Z, the committer date of the commit that first adds this file to the branch, set to this time when the commit is made. That commit's id cannot be written into the file it adds. It is the first commit on the branch whose tree holds this file, found with `git log --diff-filter=A --format=%H -- verification/outside/continuum-four-transformations/AMENDMENT_4.md`. The SHA-256 of this file is in the hash table of `README.md`.
- Before the rules were fixed: K1, K2 and K3 had smoke runs that finished at 06:09, 06:17 and 06:11 on 2026-11-23. K1 had 10 seeds per class version (full count 20), K2 had 50 per class with 10 for its control (full count 1,000 per class), and K3 had 10 per case (full count 200). None is a full-count outcome.
- K6 has no seeds, so any run of it is a full run. Its runs finished at 06:06:42Z and at 10:34:55Z. The first ran with the all-tied guard in the code and the last with it out. K6 never calls the transfer test, and the code K6 exercises last changed in commit `99533df`, so nothing it exercises changed after either run. The 10:34:55Z run is after the rules were fixed.
- The coordinator first read the outcome of the 10:34:55Z K6 run when the code's author reported it, at about 11:10Z, an approximate time.
- The code's author ran K1, K2, K3 and K6 and read each first run within about 15 minutes of its finishing. The coordinator read the K1, K2, K3 and K6 first runs before the first draft was fixed at 06:27:08Z. The plan's author read none.
- Text fixed: all text of this file outside this paragraph, and PREREG.md, was fixed by 07:09:31Z (`RECORD_7.txt`), except the two scope fixes in the next bullet. The README status sentence was corrected at about 11:23Z.
- Two scope fixes were made later by the plan's author, who stayed blind (`RECORD_10.txt`, 11:29:49Z). They concern which outcomes start a round of repair under C3 and from when rounds are counted. They were made after the K4 and K5 outcomes existed, and without the plan's author seeing any outcome.
- K4 has a full-count outcome, 10 seeds. Its first run finished at 08:11 and started with the all-tied guard in the code, which was reverted during the run. A rerun with the guard out finished at 09:33 and its output was byte-identical to the first, so the guard made no difference in that run.
- K4 readers: the code's author read the first run within minutes of its finishing and the rerun about an hour after. The coordinator first read the K4 outcome at about 09:05, and both learned of the identical rerun after the text was fixed.
- After the text was fixed, the code's author and the coordinator read the K4 outcome, including A to C 10 of 10 under both readings.
- K5 has a full-count outcome, 10 seeds. Its first run, at 08:11, stopped at the report step on a naming fault and gave no result. The rerun finished at 09:05. The code's author read the first run within minutes and the rerun about an hour after. The coordinator first read the rerun at about 10:45.
- The 10-seed K4 and K5 runs in the log are the full count for those tests. They are the runs that the disclosure above calls smoke runs of K4 and K5 still running when this amendment was first drafted. The log lists no other K4 or K5 run on this code.
- Code of K4 and K5 between their first runs and publication, as the code's author reports from git. The first full-count runs of K4 and K5 started on an uncommitted working tree. It later became commit `4238034` (without the all-tied guard) and commit `fbee977` (with it). The start state of each run was not written down, so the commit boundaries are the only git evidence.
- Between `4238034` and the pushed head `12cba0d`, one file changed in the code that K4 and K5 exercise (the source folder, the K4 and K5 scripts, the shared helper and the combine scripts). It is the K5 script, in two lines: the printed header text and the run name `amp_exp`, changed to `amp_lognormal`. The guard was added in `fbee977` and reverted in `8591b1a`, so it nets to zero.
- Limit of the record: git cannot show whether the working tree differed from `4238034` plus the guard at the moment each first run started.
- No K4 A to C outcome was known to the code's author or the coordinator before the text of C1, C2 and C3 was fixed at 07:09:31Z.
- Ties: the code's author never counted tied transfers in any K4 or K5 run and saw tied cases only in constructed test inputs. The coordinator never saw a tie count. As far as they report, nobody knows more about ties than that the K4 rerun with the guard removed was byte-identical to the first run. The tie question in C1 arose before any K4 outcome on this code.
- Round 1 under C3: K4 and K5 each have a full-count epoch 0 outcome, so carrying out Amendment 4 in the code is round 1 for each, and the first run of each on epoch 1 ends it. It is not a round for K1, K2 or K3, which have no full-count outcome, nor for K6.
- Epochs: K1 to K6 have run only on epoch 0. No run on epoch 1 or later exists.
- The plan's author has seen no outcome on this code since `RECORD_5.txt` (07:05:02Z), through `RECORD_10.txt`, and has been shown none up to publication.
<!-- OUTCOME FACTS: END -->

What the items change:

- C1 changes when a transfer is "adverse". It can only remove "adverse", and so moves outcomes towards Partial or towards weaker negative outcomes, never towards Supported or Net-dependent.
- C2 fills a gap in Law 2b: what follows when an instance fails its own pre-data check.
- C3 defines a round of repair to a known-answer test, limits the rounds, and adds a key epoch for repair reruns (reading D14).
- None changes a threshold, a level, an existing seed key, a test count or a compute figure.

## C1. Ties in the adverse decision

Old text, `PREREG.md` line 440 (reading D8):

```text
- D8. A transfer is adverse if fewer than 1/40 of the random detectors score below S_B(w_A) by more than the tie tolerance. No interpolated percentile is used.
```

and `AMENDMENT_2.md` line 179 (item B8):

```text
A tie never creates a verdict in either direction: it counts against the real series in the segment p-value, against w_A in the transfer p-value, against departure for a K5 unit, and not as "below" when deciding an adverse transfer.
```

The conflict. D8 and B8's clause agree: both leave a tied detector out of "below", and `AMENDMENT_2.md` line 231 records D8 as "adopted, with ties not counted as below (B8)". The conflict is inside B8. Its clause, and not as "below" when deciding an adverse transfer, makes "adverse" more likely when detectors tie.
B8's own reason (line 183) says "no tie can produce a finding in either direction", and its effect (line 186) says "only away from a verdict". In the extreme case every random detector ties with w_A: no detector is below, and the clause gives "adverse" although the data carry no information against the template.

The two readings. In one run, let b be the number of random detectors that score below S_B(w_A) by more than the tie tolerance, and t the number that tie with it. B8's clause, with D8, gives "adverse" when b < R/40. B8's reason and effect count ties as below and give "adverse" when b + t < R/40.
Since b is at most b + t, every transfer that is adverse under the second reading is adverse under the first. So the rule "adverse only under both readings", the form D20 used for K4, is the second reading itself.

New text, replacing reading D8 (section 11a):

```text
- D8 (as amended by Amendment 4). In each run, a transfer is adverse if and only if fewer than R/40 of the random detectors score at or below S_B(w_A), that is, if 40 times that count is less than R. A detector counts as at or below if its score is below S_B(w_A), equal to it, or tied with it under the tolerance of section 4.3.
  A run in which S_B(w_A) or any detector score is not finite is neither adverse nor passing. No interpolated percentile is used. This is the reading of item B8's reason and effect, that a tie never creates a verdict, and it replaces B8's clause "and not as 'below' when deciding an adverse transfer".
  The code's test suite holds an all-tied case and the boundary counts 2,499 and 2,500 at R = 99,999, so that the mutants of this rule (section 11) are killed.
```

Section 4.3 (line 166), the K4 criterion for A to C (line 361) and section 12 (line 516) state "adverse" through "the 2.5th percentile" of the random detectors. Each gains the words "as reading D8 defines it". Line 528 takes the definition from the arrow transfer and needs no change.

Direction of effect. The change can only remove "adverse". No transfer that was not adverse becomes adverse.

- Known-answer tests: only K4 can change, through its A to C criterion, which requires an adverse arrow transfer in every run in 9 of 10 seeds (line 361), under both readings of D20, and through the Law 2b paired K4 checks of the arrow instances. The change can only make that criterion harder to meet. K1, K2, K3 and K6 use no transfer. K5's criteria (line 379), the K4 control and the blind spot use p-values.
- T3 outcomes (section 12, rules at lines 520 to 526): a pair that was adverse through ties becomes "neither". An outcome can move from Evidence against to Partial, Does not discriminate or Inconclusive, and from Does not discriminate to Partial, through rule 5's profile branch (a pair whose profile transfer passes both ways now has an arrow adverse in neither direction).
  Moves to Partial favour the claim. The change cannot create Supported or Net-dependent, since they need the arrow transfer to pass, and passing is unchanged.
- Scale-flow outcomes (lines 530 to 535): an outcome can move from Evidence against to Partial or Does not discriminate, never to Supported.
- Law 2b: fewer adverse outcomes trigger the search, and the obstruction of G4 (line 613), which needs "adverse both ways" under every instance, is judged by the same rule.

## C2. A Law 2b instance that fails its pre-data check

Old text, `PREREG.md` line 584: "Before data are opened, each instance passes, with the instance applied and at window length 4,096 only, K2 with 200 seeds per class, K3 on the native net, and the paired K4 or K5 test." Line 585 says when a check is flagged. The plan does not say what follows if an instance fails.

New text (section 12a, after line 586):

```text
An instance that fails any of these checks is not tested. It cannot rescue, and each of its tests enters the Holm procedure with p = 1, as an instance that is not computed does. A failed check does not delay the opening of data, and the list of untested instances is fixed before any data file is opened.
A check may be repaired before then only by a dated amendment under the repair rule of section 10, and each such repair counts as a round for that instance. A repaired instance check is rerun on the lowest epoch from 1 that it has not used, with the data draws of that epoch of the known-answer test whose draws it reuses.
For an instance check, two failed rounds leave the instance untested and do not close the data. A failed check is not repaired after a data file has been opened.
An untested instance leaves the Law 2b search incomplete for every kind of adverse outcome that lists it, so such an outcome cannot be recorded as final. It is recorded as "transformed core" if another instance passes for every triggering item, and otherwise as "evidence against at the confirmatory level, Law 2b search unresolved".
In the report an untested instance is described as "not tested", never as evidence against the claim, and the final wording on the claim names each rescue route that could not be tested.
```

Reason. An instance that fails its check is miscalibrated, so it must not rescue. It also cannot be searched, and Law 2b allows a final "evidence against" only after every family has been searched (line 611) and the obstruction holds under every instance (line 613).
So the adverse outcome stands at the confirmatory level, as rule 2 of section 12 records it, and is not final, unless another instance rescues it, which the untested instance cannot prevent.
An instance check is a guard on the rescue, not a known-answer test of the confirmatory pipeline, so its failure does not close the data, as a failed known-answer test does.
Treating the failure as making the whole test invalid was rejected, because a failing guard would then remove the evidence against altogether. Leaving the untested instance out of "every instance" was rejected too, because it would record a search as complete that was not.

## C3. Rounds of repair to a known-answer test

The gate (lines 310 to 311) and section 11 (line 400) allow a known-answer test to be repaired by dated amendments before any data file is opened, but do not say what a round of repair is or how many there may be. The gate's own rule means no data file is opened while a test fails, so a failing test cannot lead to an Invalid result on data.

New text (section 10, after the gate):

```text
A repair to a known-answer test is a change to its definition, or to the code that computes it, made after a full-count outcome of that test on the code built for Amendment 3, or a later build, exists. A test's definition is its text in section 10, the readings of section 11a that fix what it computes, its seed keys and its thresholds.
A change to the code made before any such full-count outcome of the test exists is not a repair, and it is recorded with the outcomes that had been seen when it was made.
A code-only change made after such a full-count outcome exists is a repair and counts as a round, because a rerun after an outcome is a retry whatever was changed, and a limit that code-only retries could bypass would not limit tuning.
A repair is made only by a dated amendment, which records the outcomes that prompted it, who had seen them, and what changes.
An outcome is seen when anyone who works on the plan, the code, the checks or the routing of questions has read it or a summary of it, at any seed count, in a smoke run or a full run. The disclosures of the amendments and the record files fix when.
A run on epoch 0, and a smoke run on any epoch, is a diagnostic and cannot pass a test. Smoke runs use epoch 0. A full-count run uses the lowest epoch from 1 that the test has not used, and every rerun after a full-count outcome uses a new epoch, whatever was changed.
A round of repair starts when a repair is published and ends when every test it touches has been rerun at its full count, with its must-fail control, on a new key epoch for that test (reading D14), and the outcomes are recorded.
A repair made after a full-count outcome on epoch 0 is round 1, and its rerun on epoch 1 ends that round. The outcomes of every round stay in the record.
A key epoch belongs to one test: every draw of that test, its must-fail controls and the Law 2b pre-data checks that reuse its draws use the same epoch. Real-data draws keep epoch 0. K6 has no random draws and is exempt from the epoch rule only.
A test passes only on a key epoch whose outcomes for that test nobody had seen when its definition was last changed. An outcome of an epoch includes any run that used the same data draws as that epoch, even under other surrogate or detector keys.
Rounds are counted per test from the publication of Amendment 4. The changes of Amendments 1 to 3, and code changes made before Amendment 4 was published other than carrying out Amendment 4 itself, are not counted as rounds.
Amendment 4 is the dated amendment for carrying it out in the code. For each of K4 and K5 whose full-count outcome on epoch 0 on the code built for Amendment 3 exists at any time before the code carries out Amendment 4, whether before or after Amendment 4 is published, carrying it out changes the code that computes the test (the epoch field in the keys, and for K4 the transfer rule of reading D8).
For an outcome that comes to exist after publication, the dated record of the code change states the outcomes seen when it was made, in place of a further amendment.
That is a repair and is round 1 for that test, and the test's first run on epoch 1 ends the round. It is not a repair for a test with no full-count outcome on the code built for Amendment 3, or a later build, as K1, K2 and K3 so far. K6 depends on no key or transfer code, so carrying it out does not change K6 and is not a round for K6.
K6 is exempt from the epoch rule only: a repair to K6 after a K6 run is a round that ends when K6 is rerun with its must-fail control, and K6 has the same two rounds. The disclosure states for which tests Amendment 4 is round 1.
Applied today, the rule gives this table. Each "seen" entry is taken from the public record, not from any outcome. Readings D1 to D13 apply to every test that uses them, and the table lists the readings that name a test.

| Test | Readings that name it | Last change to its definition | Epoch 0 outcomes seen before that change | Epoch it passes on |
|---|---|---|---|---|
| K1 | D14, D18, D19, D21 | Amendment 3 (reading D21) | yes: the frozen-plan full-count run (code commit `71142c1`), the smoke run of the code built for Amendment 1, and the K1 smoke run of the ported code disclosed in Amendment 3 | 1 or later |
| K2 | D14, D15, D19 | Amendment 2 (item B11, the control's seed count). Reading D19 (a) of Amendment 3 states a bound only | yes: the frozen-plan full-count run, and the smoke run of the code built for Amendment 1, whose control figure B11 used | 1 or later |
| K3 | D14, D16 | Amendment 3 (item SK3, its pool keys) | yes: the frozen-plan full-count run, and the smoke run of the code built for Amendment 1, on the same data draws | 1 or later |
| K4 | D8, D14, D17, D20 | Amendment 4 (item C1, reading D8) | yes: the frozen-plan full-count run, and the smoke run of the code built for Amendment 1, at the full 10 seeds | 1 or later |
| K5 | D14, D17, D19 | Amendment 3 (items SK1, SK2, SK4 and SK8) | yes: the frozen-plan full-count run, and the smoke run of the code built for Amendment 1, at the full 10 seeds, on the same data draws where the keys were kept | 1 or later |
| K6 | D14 | no random draws | not applicable | exempt |

A known-answer test that still fails after two rounds is not validated: no further repair is made in this run of the plan, no data file is opened, and the plan is reported as not validated, with the outcomes of every round.
```

New text, reading D14 (section 11a), before its last item:

```text
  - Key epoch: in epoch 0 the master field is `20261121`. A known-answer test run on epoch k, for k from 1, uses master field `20261121e<k>` with every other field unchanged, so the keys of different epochs never coincide. Epochs are counted per test (section 10, repair rule). Real-data draws keep epoch 0, and K6 has no random draws.
  Adding the epoch is not a change to any test's definition, because epoch 0 keeps every key. Carrying it out changes the code that computes each seeded test, and section 10 says when that is a round.
```

Reason. A cap guards against endless repair, but the direct risk of repair is tuning a test to the seeds whose outcomes were seen. A new key epoch for every rerun, and the rule that a test passes only on seeds nobody had seen at its last change, guard against that directly.
The limit of two rounds is a choice made in this amendment, not a figure taken from the plan: two rounds allow two corrections, each checked on seeds nobody had seen, so that a wrong first correction can be corrected once, and no further fitting to outcomes already seen is possible.
Which amendments count was decided by the plan's author without knowing any outcome on the code built for Amendment 3. Amendment 1 followed full-count failures of the frozen plan, and Amendments 2 and 3 changed tests after smoke outcomes, so counting them would be defensible.
They are not counted because they were made under a plan with no round rule, they are disclosed in full, and the epoch rule already prevents a test from passing on seeds seen before its last change, which is the harm a count of those changes would guard against.
The table shows the epoch rule applied to every seeded test, K2 and K4 included: each must pass on epoch 1 or later.
The definitions of a definition and of "seen", the scope of an epoch and the table were written by the plan's author without knowing any outcome on the code built for Amendment 3, after the independent check asked for them.

## Also updated

`PREREG.md`: the status line (Amendments 1 to 4), an Amendment 4 paragraph in the change log, the heading of section 11a, reading D8, the key epoch in reading D14, the three places that state "adverse" through the 2.5th percentile (lines 166, 361 and 516), the new text of C2 in section 12a and of C3 in section 10.
`README.md`: the status line, the file list and the hash table, now with `AMENDMENT_4.md`.

## What was not changed

- `AMENDMENT_1.md`, `AMENDMENT_2.md` and `AMENDMENT_3.md` are left as published. This amendment supersedes B8's clause and reading D8 as Amendment 2 wrote it.
- No threshold, level, existing seed key, test count or compute figure. Epoch 0 keeps every key of reading D14.
- The folder `independent_check/` is not touched.
