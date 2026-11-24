# Record of the code change that carries out Amendment 4

Date: 2026-11-24. Written by the code author, the orda-aska account, an automated Claude Code session. Revised the same day after a review of the uncommitted change: the round accounting, the outcomes seen, the items not yet stated, the ledger guards, the mutation tool and its results. Revised once more by the same account before the first commit: K1's run history, the keys of the K4 diagnostic run, and what the code author read to settle them.

This is the dated record of the code change that `AMENDMENT_4.md` (item C3) asks for: what changed, which tests' code it touches, the round of repair it is, the outcomes the code author had seen when it was made, and the scripts run for it.
The change was made on the branch `study/amendment4-code`, based on commit `b2ef206` of `main`. The commit that holds it is the first commit on that branch whose tree holds this file.

## What changed

### C1: ties in the adverse decision (reading D8 as amended)

- `src/transfer.py`: a pure function `adverse_rule(n_le, R)` decides "adverse" on exact integers: adverse if and only if 40 x n_le < R. It refuses a bool, a float or any other type, R below 1, and a count outside 0 to R.
- `transfer_test` counts the R detectors separately: below S_B(w_A) beyond the tie tolerance (`n_lt`), tied with it under `ties.tied` (`n_tie`, an exact equality is a tie), at or below (`n_le = n_lt + n_tie`), and with a non-finite score (`n_nonfinite`). It decides "adverse" by `adverse_rule(n_le, R)`.
- The transfer p-value is unchanged: a tie counts against w_A, `n_ge = R - n_lt` and p = (1 + n_ge) / (R + 1). The random detectors are drawn exactly as before.
- A run in which S_B(w_A) or any detector score is not finite is neither adverse nor passing: `adverse` is False, p = 1 and the result carries `nonfinite = True`. The score sums are computed with numpy's overflow warning off, so an overflow gives this flag in every Python mode instead of a warning.
- With no jointly populated entry (m = 0) every detector is w_A itself and ties with it: `n_ge = n_tie = n_le = R`, `n_lt = 0`, not adverse, p = 1.
- `transfer.pair_result(runs, passes_holm)` gives the result of one ordered pair for the rules of section 12: "adverse" if every run is adverse, "pass" if the test passes at its Holm step, otherwise "neither". A pair with a non-finite run is "neither". No verdict-stage code calls it, because the real-data stage is not built.
- `flow.py` and `pipeline.py` pass the result through `apply_floor`, which keeps the new fields. `outcomes.py` takes the strings "pass", "adverse" and "neither" and needed no change. `law2b.py` makes no transfer decision.
- K4 records `n_le` and `nonfinite` for every transfer. Reading (question Q4-1 in `AMENDMENTS_NEEDED.md`): in K4 a non-finite run fails the A to B and A to C criteria and counts against the must-fail control, and in K5 it counts as not evaluable, so a non-finite score can never help a test pass.
- This reading departs from `AMENDMENT_4.md`, whose paragraph on the direction of the change says that only K4 can change, through its A to C criterion, and that K5's criteria and the K4 control use p-values. Read through p = 1 alone, a non-finite run would never trip the K4 control and would meet K5's negative criteria. Under the code's reading it counts against the K4 control and makes a K5 seed not evaluable, which fails K5's criterion for that seed. For K4's A to B and A to C criteria the reading changes nothing, since p = 1 and "not adverse" already fail them. The departure is stricter, cannot help a test pass, and touches only non-finite scores, which finite unit-length inputs cannot give. The code keeps it until Q4-1 is answered.
- `src/ties.py`: the docstring now says that a tie counts as at or below S_B(w_A) in the adverse decision, under Amendment 4, item C1, in place of B8's clause.
- `units_check.py` holds the all-tied case (not adverse), the boundary counts 2,499 (adverse) and 2,500 (not adverse) at R = 99,999, the count R/40 exactly (2 of 80, not adverse), the partly tied case, the case m = 0, a non-finite S_B(w_A), a non-finite detector score, and the refusals.
- `review_witnesses.py` had no witness that pinned the old all-tied behaviour. It gains one, under CAVE8-08, that pins the amended behaviour (not adverse) and says that the code before Amendment 4 gave "adverse" there. `tie_inputs.py` prints the tie counts.

### Reading D14: the key epoch

- `src/seeds.py`: the master field is `20261121` in epoch 0 and `20261121e<k>` in epoch k from 1, with every other field unchanged. The epoch is a required keyword of `seed_string`, `seed_int` and `rng_for`. It must be an int of at least 0. A bool, a float, a string or None is refused.
- `src/keys.py`: `rng(key, epoch)` takes the epoch as a required argument. Every function of `src/` that draws (`stats43.make_pool` and `segment_test`, `flow.analyse_unit` and `stream_units`, the series of `synth.py`, `controls.py`, `law2b.white_floor_F`, `pipeline.analyse_list`) takes it as a required keyword, so a call that forgets it fails at once.
- `par.pmap` starts its workers with the spawn method, so a value set in the parent process would not reach them. The epoch travels as the last field of every work item (`tasks.py`), and an item without it fails to unpack. No environment variable is read.
  `key_count.py` checks this with 3 spawned workers on a key of no test (instrument `unit-epoch`) on epoch 1: they give the results of the same tasks run in the parent on epoch 1, not those of epoch 0. The check lives there, not in the unit checks, because the mutation test runs 4 copies of the unit checks at once and the spawned workers would exceed the limit of 4 processes.
- Real-data draws keep epoch 0 (`keys.REAL_DATA_EPOCH`, used by `pipeline.py`).
- `key_check.py` builds every key of the plan in epoch 0 and shows that the epoch-0 strings are byte for byte those of the code before the change. A SHA-256 digest of the 417,545 distinct strings, computed with the code at `b2ef206` before any edit, is pinned and reproduced, and each key's string equals the old formula.
- It also shows that the strings of epochs 0 to 3 never coincide (1,670,180 distinct strings and as many distinct 64-bit seeds), that no key field contains the separator `|`, and that the master fields of epochs 0 to 10,000 are distinct, so no two epochs can give one string. A planted fault, epoch-1 strings built without the epoch, is flagged.
- `key_count.py` runs the seed-making code of K3, K4 and K5 on epoch 0 with the pools and transfer tests stubbed. It hands the scripts the epoch as a numpy integer and checks that this very object reaches every draw and the last field of every work item. A literal 0 or a default anywhere on the way would be found. The K4 and K5 code still builds exactly the plan's 6,100 and 11,130 keys.

### C3: rounds, epochs and the runs

- Command line (`kcommon.py`): `<script> smoke [epoch=0] [part=<p>/<n>]` or `<script> full epoch=<k> [part=<p>/<n>]`. A smoke run uses epoch 0 and refuses any other epoch. A full run must name its epoch.
- K6 takes no epoch. The size word has no effect on it and any run of it is a full run (`AMENDMENT_4.md`: "K6 has no seeds, so any run of it is a full run"), so a K6 run is never marked a diagnostic. A K6 smoke run's SIZE line says it is the same run as FULL, and its SUMMARY line carries no SMOKE word.
- A seeded script run by hand as `full epoch=<k>`, for k from 1, checks the epoch against the ledger `EPOCHS.tsv` of its checkout (`kcommon.ledger_refusal`, which uses `epochs.check_full_run`). If the ledger refuses it, the script stops with exit status 2 before any draw. The combine scripts are not checked here, since they check the epoch of their parts.
- A full run on epoch 0 is a diagnostic: its header says "FULL, DIAGNOSTIC" and its SUMMARY line "DIAGNOSTIC PASS" or "DIAGNOSTIC FAIL". The header prints the epoch, the master field in use, the code commit (with `+modified` when a tracked file of the package differs from it) and a `RUN` line. The exit status rule is kept: status 1 on FAIL.
- The part-option fault is fixed. The K2, K3, K4 and K5 scripts read the part from the named option `part=<p>/<n>`, `run_full.sh` passes it so, `FULL_RUN.md` shows it, and an argument a script does not know is refused, so the old positional form fails loudly.
- The combine scripts refuse parts that are not all parts of their test, of their size and epoch, from one clean commit equal to the combine run's own, covering each part number once (`kcommon.check_parts`). `k5_combine.py` imported a module name that does not exist (`k5_transfer`), and now imports `k5_scale_flow`.
- `EPOCHS.tsv` is the ledger of used epochs per test (test, epoch, code commit, date, kind, note). At the commit that adds it, it has no row on an epoch from 1. `epochs.py` validates it, gives a test's lowest unused epoch from 1 (`next`), and refuses a full-count run on epoch 0, on an epoch the test has used, or on any epoch but the lowest unused one (`check`). Epochs are per test. K6 is exempt.
- The kinds of row are `full-count`, `diagnostic` (epoch 0 only), `law2b-check` and `draws-seen` (from epoch 1 only). A `draws-seen` row marks an epoch as used when an outcome of some other run that used that epoch's data draws, even under other surrogate or detector keys, was seen (`PREREG.md` section 10).
- `epochs.py next` and `check` can read further ledger files joined to `EPOCHS.tsv`. A row that an earlier file holds counts once, and two different full-count rows of one test and epoch are refused.
- `run_full.sh` takes the epoch and optionally the tests to run. It refuses a missing epoch, epoch 0, an unknown test, a checkout with changed tracked files, a results folder that exists and is not empty, and any seeded test that the ledger check refuses. It records the epoch in `run_info.txt`, writes the ledger rows of the run to `EPOCHS_rows.tsv`, and passes `epoch=<k>` to every seeded script. It stays POSIX sh.
- The checkout under test never holds the rows of its own runs, which are committed afterwards, so its ledger alone cannot refuse a second run of the same commit on the same epoch. `run_full.sh` therefore also appends the run's rows, before any test starts, to `<build folder>/EPOCHS_started.tsv`, and checks every later call with that build folder against it as well. `FULL_RUN.md` states what each check can and cannot see.
- `FULL_RUN.md` says how to pick and record the epoch, and that the first epoch-1 run of K4 or of K5 ends round 1 of repair, with one round left. Under the stricter reading of Q4-5 the same holds for K2 and K3. None of these runs may start on unreviewed code. `RERUN.md` and this folder's `README.md` follow the new command line.

### C2: a Law 2b instance that fails its pre-data check

The instance checks themselves are not built. `src/law2b.py` gains the minimal representation that C2 needs:

- `untested_instances(checks)`: an instance that failed any of its pre-data checks is "not tested".
- `holm_family(computed, untested)`: Holm over the 102 tests with `levels.holm`, in which a test of an untested instance has no computed p and is left out of the dict, so it counts with p = 1. A computed p for such a test is refused.
- `search_state(kind, items, untested, passes, vacuous, obstruction)`: the state of one triggered kind. An untested instance cannot rescue. If a tested instance that is not vacuous passes for every triggering item, the state is "transformed core". Otherwise, with an untested instance listed for the kind, it is "evidence against at the confirmatory level, Law 2b search unresolved", never final. With every instance tested the rules of section 12a apply unchanged.
- `untested_routes`: the wording names each rescue route that could not be tested, as "not tested", never as evidence against.

Not wired yet: the instance checks, the verdict stage that would call these functions, and the combination of several triggered kinds (section 12a, "When more than one kind triggers at once").

### The mutation tool

- `mutation_test.py` copies into each work copy the scripts of `known_answer/` and the data files the suite reads there (`EPOCHS.tsv`). Before any mutant it runs the suite on the unmutated code in every work copy, and stops with exit status 1 unless the suite passes there. A suite that fails on correct code would otherwise count every mutant as killed (see Results).

## Which tests' code changes

- K4: reading D8 (the adverse decision of its A to C criterion) and the epoch field of its keys.
- K1, K2, K3 and K5: the epoch field of their keys. K5's criteria read p-values only. Amendment 4 changes no p-value of a run whose scores are finite, and K5 now counts a non-finite flow transfer run as not evaluable.
- K6: nothing that it computes. It takes no epoch, and its command line and header come from the shared helper. A K6 smoke run is labelled as the full run it is.

On epoch 0 every key, and so every draw, of every test is unchanged. For finite scores every p-value is unchanged, and "adverse" can only change from true to false.

## Round accounting under C3

- K4 and K5 each have a full-count outcome on epoch 0 on the code built for Amendment 3. This change is therefore round 1 of repair for each of them. Each one's first full-count run on epoch 1 ends its round 1, and one round is then left for it.
- K2 and K3 have full-count runs on epoch 0 on the code built for Amendment 3. They were made as diagnostics, and because of the part-option fault each K3 "part" ran the full K3 and the K2 "part 0" ran the full K2 (`DIAGNOSIS_EPOCH0.md`, lines 17 to 19). This change changes the code that computes K2 and K3: the epoch field of their keys, through `synth.k2_series`, `synth.k3_series`, `tasks.k2_task`, `tasks.k3_task` and `keys.rng`. Under `PREREG.md` section 10 it is then a repair and counts as a round for them.
  Amendment 4 names K2 and K3 among the tests with no such outcome "so far". Whether the accidental runs change that is question Q4-5 in `AMENDMENTS_NEEDED.md`. Until it is answered the stricter reading applies: this change is round 1 for K2 and for K3, each one's first full-count run on epoch 1 ends it, and one round is then left for each. Their first epoch-1 runs must not start on unreviewed code.
- Outcomes seen for K2 and K3: the table in #8's description lists K2 fail and K3 fail. Before the first commit the code author also read the K2 and K3 full-count rows of `OUTCOME_LOG.md`: both failed on epoch 0 (next section).
- K1 has no full-count run on the code built for Amendment 3. `OUTCOME_LOG.md`, which lists every run on that code once, has one K1 row, a smoke run, and `DIAGNOSIS_EPOCH0.md` lists no K1 run. K1 runs in one piece, so the part-option fault does not apply to it. This change is therefore not a round for K1, as Amendment 4 says. Its first full-count run uses epoch 1.
- K6 depends on no key or transfer code, so this change is not a round for K6.

## Outcomes the code author had seen when the change was made

As of opening issue #24, the issue's paragraph "What the code author has seen", copied word for word:

> This is recorded for C3, as of opening this issue. I have read #8's description, including its smoke and diagnostic table (K1 pass, K2 fail, K3 fail, K4 reading 2 fail at 7 of 10, K5 pass, K6 pass). I have also read the outcome-facts paragraph of `AMENDMENT_4.md`, including K4 A to C at 10 of 10 under both readings on epoch 0.
>
> I have run no known-answer test and opened no output file under `known_answer/out_*`.

Added for this change: while making it, and while revising it after review, the code author opened no output file of a known-answer run, under `known_answer/out_*` or elsewhere, and did not open `diagnostics/`, `SMOKE_RESULTS.md` or the run rows of `OUTCOME_LOG.md`. Of `DIAGNOSIS_EPOCH0.md` the code author read only its lines 17 to 19, which describe the part-option fault and say which K2 and K3 runs reached the full count. They give no outcome.
The review of the change quoted the name of one file under `known_answer/out_diagnostics_epoch0/`. Its name says it is a K4 run on seeds 0 to 9 with other keys. Its content was not read.

Added before the first commit, to settle the items the revision had left open: the code author's session read the header of `OUTCOME_LOG.md` (lines 1 to 12, among them the one K1 row, a smoke run that passed) and its K2 and K3 full-count rows (lines 35 and 36). Both are epoch-0 outcomes: K3 at full count failed on its logistic sub2 cell, and K2 at full count failed with one class flagged and its must-fail control flagged. It also read the lines of `DIAGNOSIS_EPOCH0.md` that name full-count runs, K2, K3 or a code commit (among them the epoch-0 figures of its sections 2 and 4), and the lines of `diagnostics/diag_k4.py` and `diagnostics/diag_tasks.py` that build keys. No output file was opened.
Every outcome read is an epoch-0 outcome, which cannot pass a test, and the tests it concerns already need an epoch from 1. No outcome of an epoch from 1 exists.

## Not yet stated in this record

`PREREG.md` section 10 asks the record to state the outcomes seen and who had seen them, where "seen" means read by anyone who works on the plan, the code, the checks or the routing of questions. The code author cannot state the following, and the party named here is asked to add it to this record before the full-count runs start:

- The outcomes the coordinator had seen when the change was made. The coordinator adds them.

Settled before the first commit:

- The keys of the K4 diagnostic run with other keys, made after Amendment 4 was published. Under section 10 an outcome of an epoch includes any run that used the same data draws as that epoch, even under other surrogate or detector keys. `diagnostics/diag_k4.py` draws through `keys.rng(key)` with one argument, which reaches `seeds.rng_for` of the code before this change, whose master field is the fixed `20261121` in every version of `src/seeds.py` on `main`. Its alternative keys change only the purpose field (`diag-` for pools in `diagnostics/diag_tasks.py`, `diag1-` to `diag3-` for detectors), and its data series use the real keys. `DIAGNOSIS_EPOCH0.md` says the same and that no epoch-1 key was built.
  So every draw of that run is an epoch-0 draw, none has the master field of an epoch from 1 (`20261121e<k>`), and `EPOCHS.tsv` needs no `draws-seen` row for it.
- Whether K1 has a full-count run on the code built for Amendment 3: it has none (section "Round accounting under C3").

## Scripts run for this change

All runs were from the package folder, with `python3` (Python 3.13 and numpy 2.5.3 on the machine used), at most 4 processes, and `-B` so that no byte code was written.

- Before any edit, to compare outputs: `units_check.py`, `key_check.py`, `review_witnesses.py` and `k6_gate_checks.py full`, each once with `-I -B`.
- `known_answer/units_check.py`, `known_answer/key_check.py`, `known_answer/review_witnesses.py` and `known_answer/k6_gate_checks.py full`, each under `-I -B`, `-I -O -B` and `-I -B -W error`, with the outputs compared.
- `known_answer/k6_gate_checks.py full epoch=1`, to see the epoch refused (exit status 2).
- `known_answer/key_count.py .`, on epoch 0, with the pools and transfer tests stubbed, and its spawn check on a key of no test on epoch 1.
- `known_answer/mutation_test.py run <scratch folder> --lines <file>`, on the mutation sites of the lines changed in `src/transfer.py`, `src/seeds.py` and `src/law2b.py`. Its suite is K6 smoke, the key check and the unit checks.
- `known_answer/hygiene.sh origin/main origin/main`, under `sh` and under `bash`.
- Short Python snippets that import `src/` modules or `key_check.py`: the digest of the epoch-0 strings before the change, a probe of numpy's overflow warning, one non-finite transfer case on hand-made input, and the list of mutation sites on the changed lines. None drew from a key of a known-answer test.
- Syntax checks only, with nothing executed: `sh -n`, `dash -n` and `bash -n` on `run_full.sh` and `hygiene.sh`, and Python `compile` with a static scan for undefined names on the K1 to K5 scripts and the combine scripts.

`key_count.py` ran three times: the first run stopped at the K4 report step because its stub transfer result lacked the new fields, which were then added to the stub, and the third run added the spawn check. The first mutation run was stopped before it reported, when the spawn check was moved out of the unit checks, and was then run again in full.

Revision after review, the same day, with the same machine and flags:

- `known_answer/units_check.py`, `known_answer/key_check.py`, `known_answer/review_witnesses.py`, `known_answer/k6_gate_checks.py full` and `known_answer/k6_gate_checks.py smoke`, each under `-I -B`, `-I -O -B` and `-I -B -W error`, with the outputs compared. `known_answer/k6_gate_checks.py full epoch=1` once more, to see the epoch refused.
- `known_answer/units_check.py` once under `-I -B` in a scratch copy of `src/` and of the scripts and ledger of `known_answer/`, whose `EPOCHS.tsv` had two rows added as after a recorded run (K4 full-count and K2 law2b-check, both on epoch 1), and in that copy `epochs.py next K4`, `epochs.py check K4 1` and `epochs.py check K4 2`. The copy was then deleted. No known-answer test ran there.
- `known_answer/epochs.py check` with a further ledger file, in a scratch folder, before and after rows were appended to it as `run_full.sh` appends them.
- The two new fragments of `run_full.sh` (the results-folder guard, and the rows appended to the build folder's ledger), copied into a scratch shell script and run under `dash` and `bash`. `run_full.sh` itself was not run. `sh -n`, `dash -n` and `bash -n` on `run_full.sh`.
- Python `compile` of every script of `known_answer/`, with a check that each call of `parse_cli` binds to its signature. Nothing was executed.
- `known_answer/mutation_test.py run <scratch folder> --lines <file>` on all 305 lines that this change adds or changes in `src/` (from `git diff -U0 b2ef206 -- src/`), with the ledger copied into each work copy and the new baseline step. A first attempt did not start, because `/usr/bin/time` is not installed on the machine used (exit status 127, no mutant run).
- `mutation_test.run_suite`, from a short snippet, on one work copy made by `mutation_test.prepare`: once with that copy's `EPOCHS.tsv` deleted and once as prepared, to see that the baseline step stops on a missing ledger. The copy was then deleted.
- `known_answer/key_count.py .` once more, since `kcommon.py` now imports `epochs.py`, on epoch 0 with the pools and transfer tests stubbed, with its spawn check on a key of no test on epoch 1.
- `known_answer/hygiene.sh origin/main origin/main`, under `sh` and under `bash`.
- A read of issue #24's body through the GitHub API, without its comments, to copy its paragraph word for word.

No run of K1, K2, K3, K4 or K5 was made, at any epoch, size or mode, and `run_full.sh` was not run. No code drew from a key of a known-answer test on an epoch from 1. Every draw on epoch 1 in the unit checks and in `key_count.py` uses a key of no test (instrument `unit-epoch`).

## Results

- `units_check.py`: 484 checks, 0 failed, PASS, exit status 0 in each of the three modes, with identical output. The first version had 472. It checked that the shipped ledger had no row on an epoch from 1, which would have failed on correct code after the first recorded run. It now checks only that the shipped ledger parses and meets the rules.
  With a ledger holding the rows of a recorded run it also passes (484 checks, 0 failed).
- `key_check.py`: 53 checks, 0 failed, PASS, exit status 0 in each mode, identical output. The epoch-0 digest is reproduced, and epochs 0 to 3 give 1,670,180 strings with none shared.
- `review_witnesses.py`: "UNGUARDED: none", exit status 0 in each mode, identical output.
- `k6_gate_checks.py full` and `smoke`: "SUMMARY K6 PASS", exit status 0 in each mode, identical output. The smoke run's SIZE line says it is the same run as FULL. With `epoch=1` it refuses and exits with status 2. Under `-I -B` and `-I -O -B` the run writes one numpy ComplexWarning to standard error, from a deliberately mutated copy of the gate code. Standard output is identical.
- `key_count.py`: the K4 code builds exactly the plan's 6,100 keys and the K5 code its 11,130 keys. The run's epoch reaches every draw and every work item of K3, K4 and K5, and the spawned workers draw in the epoch of their work items. The run after the revision gave the same results.
- `mutation_test.py --lines`, first version: these results are void. The tool copied only the scripts of `known_answer/` into its work copies, not `EPOCHS.tsv`, so the unmutated unit checks crashed there, and every mutant was counted as killed. The reported "37 of 37 killed" and "6 of 6" show nothing and do not count toward the pre-data mutation condition of section 11. The review found, with the ledger present, that one of the 37 survived (`transfer.py`, the refusal of a non-bool Holm result in `pair_result`). Its unit check accepted any exception, and the deleted refusal let a later ValueError fire.
  The tool now copies the ledger and runs the suite on the unmutated code in every work copy first, and stops unless it passes there. The unit check now asks for TypeError on a run that is not adverse.
- `mutation_test.py --lines`, after the revision: 37 mutants on the 305 changed lines of `src/`, 16 in `transfer.py`, 7 in `seeds.py` and 14 in `law2b.py`. The other changed modules have no mutation site on their changed lines. The baseline passed in all 4 work copies, and all 37 mutants were killed, among them the refusal in `transfer.pair_result` that the review found surviving. Wall time 7.5 minutes.
- The baseline step itself: in a work copy without `EPOCHS.tsv` the suite fails (exit status 1 in `units_check.py`), and with the ledger it passes.
- `hygiene.sh origin/main origin/main`, under `sh` and under `bash`: every check ok, the prose check skipped because its checker is not installed, last line "HYGIENE PASS (check-prose not run: checker not installed)", exit status 0.

## Limits

- The K1 to K5 scripts and the combine scripts were not executed. They were compiled and scanned, their shared helpers are unit-checked, and `key_count.py` ran the K4 and K5 seed-making code on epoch 0. The ledger guard of a hand run was not run through the scripts: `kcommon.ledger_refusal` and `kcommon.parse_cli` are unit-checked on fixed ledgers and on the shipped one.
- `run_full.sh` was not run. Its two new fragments were run on their own in a scratch shell script.
- The ledger checks see only the ledgers they read: the checkout's `EPOCHS.tsv` and, in `run_full.sh`, the build folder's `EPOCHS_started.tsv`. A rerun from another build folder on a commit whose ledger lacks the earlier rows is not refused (`FULL_RUN.md`).
- The archived diagnostic scripts under `diagnostics/` were read only where they build keys, and were not run. They will not run against the new signatures, since `keys.rng` now needs the epoch.
- `key_check.py`'s K1 family does not list the 4,224-sample keys (`K1:<class>:4224`) that K1's offset identity check draws. They follow the K1 names of reading D14 and take the epoch like every other K1 draw.
- The prose checker that `hygiene.sh` calls is not installed on the machine used, so it was not run on the changed markdown files. `hygiene.sh` now prints a SKIP line in that case.
