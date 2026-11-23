# Running one known-answer family at full count

Full-count runs wait for the next amendment, which changes the seed keys. This note says how a worker runs them once that amendment is implemented and the commit to run is named.

This note says how to run K1, K2, K3 or K6 at the plan's full seed count, in one Python mode, from a clean checkout of the pushed commit. K4 and K5 full runs wait for the next amendment. Do not run them from this note.

## Set up

Use a separate checkout of the commit, so that nothing edited later can change the code under test, and a build folder that holds the checkout and the outputs. The sandbox lets a run write only inside the build folder.

```text
git worktree add --detach <build folder>/code <commit>
cd <build folder>/code/verification/outside/continuum-four-transformations
git rev-parse HEAD > <build folder>/results/commit.txt
python3.14 --version > <build folder>/results/python.txt
```

Python 3.14 and numpy 2.5 are needed. Nothing else is installed or downloaded.

## Run a test

`known_answer/sbpy.sh` starts Python with no network access and with writes confined to the build folder. Its arguments are the build folder, an alarm in seconds, and then the Python flags, the script and its arguments. Always put `nice -n 10` in front and use `/usr/bin/time -p` to record the times. The scripts use at most 4 worker processes.

The three modes are `-I -B`, `-I -O -B` and `-I -B -W error`. Run one mode after another, never at the same time. Every script prints identical output in the three modes.

K6 and K1 run in one piece (K6 takes a second):

```text
nice -n 10 known_answer/sbpy.sh <build folder> 172800 -I -B known_answer/k6_gate_checks.py full > <out>/k6.txt 2> <out>/k6.err
nice -n 10 known_answer/sbpy.sh <build folder> 172800 -I -B known_answer/k1_exact_checks.py full > <out>/k1.txt 2> <out>/k1.err
```

K2 and K3 run in parts with the same seeds. Each part prints counts only, and a join script gives the result. K3 in 4 parts and K2 in 8 parts (the part numbers run from 0 to one less than the number of parts):

```text
nice -n 10 known_answer/sbpy.sh <build folder> 172800 -I -B known_answer/k3_planted_structure.py full <part> 4 > <out>/k3.part<part>.txt 2> <out>/k3.part<part>.err
nice -n 10 known_answer/sbpy.sh <build folder> 172800 -I -B known_answer/k3_combine.py full <out>/k3.part0.txt <out>/k3.part1.txt <out>/k3.part2.txt <out>/k3.part3.txt > <out>/k3.txt 2> <out>/k3.err
```

K2 is the same with `k2_nothing_in_noise.py`, 8 parts and `k2_combine.py`.

## Record the result

Each script ends with exit status 1 if its result is FAIL and 0 if PASS. Write the exit status of every command next to its output (`echo "<name> <mode> exit $?" >> <out>/status.txt`). A FAIL is a result. Do not rerun with other seeds or other settings, and do not change any code.

Write down the start and end times. Compare the combined outputs of the three modes with `cmp`.

## Expected run time

From the smoke runs on this code at 4 processes, scaled by the seed ratio. These are estimates.

| Test | Processor time | Wall time at 4 processes |
|---|---|---|
| K6 | under 1 second | under 1 second |
| K1 | about 24 minutes | about 7 minutes |
| K3 | about 1.4 hours | about 25 minutes |
| K2 | about 5.3 hours | about 1.4 hours |

Each of these is for one mode.
