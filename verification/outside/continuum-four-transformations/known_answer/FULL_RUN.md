# Running a known-answer test at full count

This note says how a worker runs K1 to K6 at the plan's full seed count, in the three Python modes, from a clean checkout of a named commit. The code that carries out Amendment 4 is described in `AMENDMENT4_CODE_RECORD.md`. Full-count runs wait until the coordinator names the reviewed commit to run.

The part option is fixed. Earlier the K2, K3, K4 and K5 scripts read the part number from the wrong argument positions and ignored it. The scripts now take named options (`epoch=<k>` and `part=<p>/<n>`), `run_full.sh` passes them by name, and an argument a script does not know is refused.

## The key epoch

Every full-count run of a seeded test (K1 to K5) runs on a key epoch (`PREREG.md` section 10, repair rule, and reading D14 as amended by Amendment 4). In epoch 0 the master field of the seed string is `20261121`. On epoch k, from 1, it is `20261121e<k>`, and every other field of every key is unchanged.

- Epoch 0 is the diagnostic epoch. Smoke runs use it and refuse any other epoch. A full run on epoch 0 is a diagnostic: it cannot pass a test, and its header and SUMMARY line say DIAGNOSTIC. Every run before Amendment 4 was carried out used epoch 0.
- A full-count run of a test uses the lowest epoch from 1 that the test has not used. Every rerun after a full-count outcome uses a new epoch, whatever was changed.
- Epochs belong to one test. A test's must-fail controls run in the same script on the same epoch. The Law 2b pre-data checks that reuse a test's draws use that test's epoch.
- K6 has no random draws. It takes no epoch and is exempt from the epoch rule only.

## Pick and record the epoch

`known_answer/EPOCHS.tsv` is the ledger of the epochs each test has used. It has one row per run: test, epoch, code commit, start date, kind and a note. The kind is `full-count`, `diagnostic` (epoch 0 only), `law2b-check`, or `draws-seen` (from epoch 1 only), which marks an epoch as used when an outcome of some other run that used that epoch's data draws, even under other surrogate or detector keys, was seen. At the commit that adds it, it has no row on an epoch from 1.

Before a run, ask the ledger for the test's epoch and check it:

```text
python3.14 -I -B known_answer/epochs.py next K4
python3.14 -I -B known_answer/epochs.py check K4 1
```

`check` exits with status 1 and says why when the epoch is 0, when the test has used it, or when it is not the lowest unused epoch from 1.

Record the epoch as soon as the run starts, before anyone reads an outcome: add the run's rows to `EPOCHS.tsv` on the code branch in a commit of its own, exactly as written. `run_full.sh` writes these rows to `<results dir>/EPOCHS_rows.tsv`. A run made without `run_full.sh` gets its row written by hand in the same form. Never edit the checkout under test while it runs: the scripts record the code commit, and a changed tracked file marks it `+modified`.

What the checks can see:

- The checkout under test never holds the rows of its own runs, since they are committed afterwards. So the ledger of a checkout cannot refuse a second run of the same commit on the same epoch.
- `run_full.sh` therefore also appends the run's rows, before any test starts, to `<build folder>/EPOCHS_started.tsv`, and checks every later call with that build folder against it as well. A second run of a test on the same epoch from the same build folder is refused. It also refuses a results folder that exists and is not empty, so an earlier run's record is never overwritten.
- A seeded script run by hand with `full epoch=<k>`, for k from 1, checks the epoch against the ledger of its checkout and stops with exit status 2, before any draw, if that ledger refuses it. It cannot see the build folder's ledger.
- Every write that records the run is checked. After appending, `run_full.sh` reads the build folder's ledger back and starts no test unless it now shows each seeded test of the run on this epoch. A run is never started unrecorded.
- A rerun from another build folder, or by hand, is refused only if the ledger it reads holds the earlier rows. Start it from a commit whose `EPOCHS.tsv` holds them, or check it first with `epochs.py check <test> <epoch> <build folder>/EPOCHS_started.tsv`.

## Round accounting

K4 and K5 each have a full-count outcome on epoch 0 on the code built for Amendment 3. Carrying out Amendment 4 in the code is therefore round 1 of repair for each of them, and the first run of each on epoch 1 ends that round. After it, one round is left for that test (section 10 allows two).

K2 and K3 also have full-count runs on epoch 0 on that code: because of the part-option fault, each K3 "part" ran the full K3 and the K2 "part 0" ran the full K2 (`DIAGNOSIS_EPOCH0.md`, lines 17 to 19). Whether this makes the change round 1 for them is question Q4-5 in `../AMENDMENTS_NEEDED.md`. Until it is answered the stricter reading applies: the change is round 1 for K2 and K3 too, the first epoch-1 run of each ends it, and one round is then left for each.

K1 has no full-count run on that code. `OUTCOME_LOG.md`, which lists every run on that code once, has one K1 row, a smoke run, and `DIAGNOSIS_EPOCH0.md` lists no K1 run. So carrying out Amendment 4 is not a round for K1, as Amendment 4 says.

So the first epoch-1 run of K2, K3, K4 or K5 must not start on unreviewed code. Start it only on the commit the coordinator names after review. The same holds for K1. K6 is not changed.

Before the first epoch-1 run of K1, question Q4-2 (K1's fixed draws, which two of its must-fail controls also use) needs an answer. The keys of the K4 diagnostic run with other keys are stated in `AMENDMENT4_CODE_RECORD.md`. They are all epoch-0 keys, so no epoch from 1 is marked as seen for K4.

## Set up

Use a separate checkout of the commit, so that nothing edited later can change the code under test, and a build folder that holds the checkout and the outputs. The sandbox lets a run write only inside the build folder.

```text
git worktree add --detach <build folder>/code <commit>
cd <build folder>/code/verification/outside/continuum-four-transformations
git rev-parse HEAD > <build folder>/results/commit.txt
python3.14 --version > <build folder>/results/python.txt
```

Python 3.14 and numpy 2.5 are needed. Nothing else is installed or downloaded.

## Run with run_full.sh

```text
known_answer/run_full.sh <results dir> <build folder> <epoch> [test ...]
```

The tests are any of K1 K2 K3 K4 K5 K6, all six by default. Tests whose next epochs differ are run in separate calls. The script refuses a missing epoch, epoch 0, an epoch of more than 9 digits, a build folder that is not a writable folder, an unknown test, a checkout whose tracked files differ from its commit, a results folder that exists and is not empty, and any seeded test for which `epochs.py check` refuses the epoch, with the checkout's ledger joined to `<build folder>/EPOCHS_started.tsv`. It records the code commit, the epoch and the tests in `<results dir>/run_info.txt`, appends the run's rows to `<build folder>/EPOCHS_started.tsv`, and passes `epoch=<epoch>` to every seeded script. K6 runs without an epoch.

## Run one test by hand

`known_answer/sbpy.sh` starts Python with no network access and with writes confined to the build folder. Its arguments are the build folder, an alarm in seconds, and then the Python flags, the script and its arguments. Always put `nice -n 10` in front and use `/usr/bin/time -p` to record the times. The scripts use at most 4 worker processes.

The three modes are `-I -B`, `-I -O -B` and `-I -B -W error`. Run one mode after another, never at the same time. Every script prints identical output in the three modes.

K6 and K1 run in one piece (K6 takes a second):

```text
nice -n 10 known_answer/sbpy.sh <build folder> 172800 -I -B known_answer/k6_gate_checks.py full > <out>/k6.txt 2> <out>/k6.err
nice -n 10 known_answer/sbpy.sh <build folder> 172800 -I -B known_answer/k1_exact_checks.py full epoch=<k> > <out>/k1.txt 2> <out>/k1.err
```

K2, K3, K4 and K5 run in parts with the same seeds: K3 in 4 parts, K2 in 8, K4 and K5 in 10 (by seed). Each part prints counts only, and a join script gives the result. The part numbers run from 0 to one less than the number of parts:

```text
nice -n 10 known_answer/sbpy.sh <build folder> 172800 -I -B known_answer/k3_planted_structure.py full epoch=<k> part=<p>/4 > <out>/k3.part<p>.txt 2> <out>/k3.part<p>.err
nice -n 10 known_answer/sbpy.sh <build folder> 172800 -I -B known_answer/k3_combine.py full epoch=<k> <out>/k3.part0.txt <out>/k3.part1.txt <out>/k3.part2.txt <out>/k3.part3.txt > <out>/k3.txt 2> <out>/k3.err
```

K2 is the same with `k2_nothing_in_noise.py`, 8 parts and `k2_combine.py`. K4 uses `k4_transfer.py` and `k4_combine.py`, K5 `k5_scale_flow.py` and `k5_combine.py`, each with 10 parts.

Every part prints a `RUN` line with its test, size, epoch, part and code commit. The join script refuses the parts unless all are parts of that test, of its size and epoch, from one clean commit equal to its own, and cover each part number once.

## Record the result

Each script ends with exit status 1 if its result is FAIL and 0 if PASS, a DIAGNOSTIC PASS included. Write the exit status of every command next to its output (`echo "<name> <mode> exit $?" >> <out>/status.txt`). A FAIL is a result. Do not rerun with other seeds or other settings, and do not change any code. A rerun after a full-count outcome is a new round on a new epoch and needs the dated record that section 10 asks for.

Write down the start and end times. Compare the combined outputs of the three modes with `cmp`.

## Expected run time

K1, K2 and K3 times are from the smoke runs on the Amendment 3 code at 4 processes, scaled by the seed ratio. K4 and K5 times are the plan's compute estimate per mode (`PREREG.md` section 11), divided by 4 for the wall time. These are estimates.

| Test | Processor time | Wall time at 4 processes |
|---|---|---|
| K6 | under 1 second | under 1 second |
| K1 | about 24 minutes | about 7 minutes |
| K3 | about 1.4 hours | about 25 minutes |
| K2 | about 5.3 hours | about 1.4 hours |
| K4 | about 3.7 hours (both readings of D20) | about 56 minutes |
| K5 | about 7.0 hours | about 1.75 hours |

Each of these is for one mode.
