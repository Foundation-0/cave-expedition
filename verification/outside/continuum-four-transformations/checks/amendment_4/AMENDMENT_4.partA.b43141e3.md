# Amendment 4 to the pre-registration

Date: 2026-11-23. Base: branch `outside/continuum-four-transformations-prereg` at commit `4c6ecd1` (Amendment 3). Line numbers below refer to that commit.

Status of this file: Part A is a draft, fixed before the plan's author saw any outcome of the code built for Amendment 3. Part B is reserved and empty.

No data file has been opened or parsed.

## What was known when Part A was written

- The tie question (C1) was raised by the team's audit of the detector code and by the code's author, who found that D8 and B8 can pull in different directions when random detectors tie with the template.
- The code's author and the party who routes the questions have seen smoke outcomes on the code built for Amendment 3, at 10 seeds, for K1, K2, K3 and K6. Smoke runs of K4 and K5 were running.
- The plan's author knew no outcome from the code built for Amendment 3 when C1 to C3 were drafted. C2 and C3 come from the plan's author's own reading of the plan text.
- [PLACEHOLDER: anything added to Part A after this draft, with its date and time and what was known then.]

What the items change:

- C1 changes when a transfer is "adverse". It moves outcomes only away from "adverse".
- C2 fills a gap in Law 2b: what follows when an instance fails its own pre-data check.
- C3 limits the rounds of repair to a known-answer test.
- None changes a threshold, a level, a key or a compute figure.

## Part A

### C1. Ties in the adverse decision

Old text, `PREREG.md` line 440 (reading D8):

```text
- D8. A transfer is adverse if fewer than 1/40 of the random detectors score below S_B(w_A) by more than the tie tolerance. No interpolated percentile is used.
```

and `AMENDMENT_2.md` line 179 (item B8):

```text
A tie never creates a verdict in either direction: it counts against the real series in the segment p-value, against w_A in the transfer p-value, against departure for a K5 unit, and not as "below" when deciding an adverse transfer.
```

B8 gives its reason at line 183 ("Because a tie counts against whichever verdict it would otherwise help, no tie can produce a finding in either direction") and its effect at line 186 ("only away from a verdict").

The inconsistency. In the adverse decision, a detector that ties with w_A is not counted as below. That makes "adverse" more likely, not less, so B8's operative clause helps the verdict that its own principle says a tie must never help.
In the extreme case every random detector ties with w_A. Then no detector is below, and D8 and B8's clause both give "adverse", although the data carry no information against the template. With some detectors tied, the tied ones still count towards "adverse".

The two readings. Let b be the number of random detectors that score below S_B(w_A) by more than the tie tolerance, and t the number that tie with it (B8's tolerance). The literal reading (D8, B8's clause) gives "adverse" when b < R/40. The reading of B8's principle counts ties as below and gives "adverse" when b + t < R/40.
Since b is at most b + t, every transfer that is adverse under the second reading is adverse under the first. So the rule "adverse only under both readings", the form D20 used for K4, is the second reading itself.

New text, replacing reading D8 (section 11a):

```text
- D8 (as amended by Amendment 4). A transfer is adverse only if fewer than R/40 of the random detectors score at or below S_B(w_A), where a detector that ties with S_B(w_A) under the tolerance of section 4.3 counts as at or below. No interpolated percentile is used. This is the reading of item B8's principle that a tie never creates a verdict, and it replaces B8's clause "not as below".
```

Section 4.3 (line 166), the K4 criterion for A to C (line 361) and section 12 (line 516) state "adverse" through "the 2.5th percentile" of the random detectors. Each gains the words "as reading D8 defines it".

Direction of effect: only away from "adverse". No transfer that was not adverse becomes adverse.

- Known-answer tests: only K4 can change. Its A to C criterion requires an adverse arrow transfer in every run in 9 of 10 seeds (line 361), so the change can only make that criterion harder to meet. K1, K2, K3 and K6 use no transfer. K5's criteria use p-values (line 379), not "adverse". The K4 control and blind spot use p-values.
- Real data: a pair that was "adverse" through ties becomes "neither" (line 516). This can remove an "evidence against" outcome of kind (b) or (c) and the Law 2b search it triggers. The obstruction of G4 (line 613), which needs "adverse both ways" under every instance, is judged by the same rule. No verdict can be created by the change.

### C2. A Law 2b instance that fails its pre-data check

Old text, `PREREG.md` line 584: "Before data are opened, each instance passes, with the instance applied and at window length 4,096 only, K2 with 200 seeds per class, K3 on the native net, and the paired K4 or K5 test." The plan does not say what follows if an instance fails.

New text (section 12a, after line 584): "An instance that fails any of these checks is recorded with the failure and cannot rescue. Each of its tests enters the Holm procedure with p = 1, as an instance that is not computed does. The list of usable instances is fixed before any data file is opened. A failed check is not repaired after a data file has been opened."

Reason. This is the most conservative reading. An instance that fails is miscalibrated, so it must not be able to turn an adverse outcome into a rescue. Treating the failure as making the whole test invalid was rejected, because a failing guard would then shield the claim from "evidence against". With the rule above, an instance's failure can only leave an adverse outcome standing.

### C3. A limit on repair rounds

The gate (lines 310 to 311) and section 11 (line 400) allow a known-answer test to be repaired by dated amendments before any data file is opened, but set no limit on the number of rounds.

New text (section 10, after the gate): "A repair to a known-answer test is made only by a dated amendment. The amendment records the full-count outcomes that prompted it, who had seen them, and what changes, and the full-count outcomes of every round stay in the record. After a repair, every test it touches is rerun at its full count with its must-fail control.
A test that still fails after two rounds of repair is declared not validated, no further repair is made in this run of the plan, and the outcome stays Invalid (section 12, rule 1)."

Reason. Without a limit, a test could be repaired until it passes, and each round would use outcomes the earlier round had seen. Two rounds allow one correction and one check of it. The record of every round lets a reader judge what the repairs were fitted to.

## Part B (reserved)

Part B would hold repairs to known-answer tests. It is written only if a full-count run fails, after the plan's author has been shown those outcomes, and it follows C3. It is empty in this draft.
