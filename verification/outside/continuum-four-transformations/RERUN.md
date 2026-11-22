# Rerun

This folder holds the code and the known-answer runs for the plan in `PREREG.md` as amended by Amendment 1. It touches no real data and downloads nothing.

You need Python 3.14 with numpy 2.5.4. The standard library and numpy are the only dependencies. The recorded runs used Python 3.14.6.

## Layout

- `src/` is the analysis code for the amended plan. `src/law2b.py` holds the listed transformation instances of section 12a. Nothing else imports it, so the confirmatory path never calls it.
- `known_answer/` holds the unit checks (`units_check.py`), the known-answer tests K1 to K6 and the files that join their parts. Outputs of the smoke runs are in `known_answer/out_smoke/`.
- `known_answer/review_witnesses.py` runs the witnesses of an outside review of the earlier code against this code. Its outputs, before and after the fixes, are in `known_answer/out_review/`.
- `known_answer/out_frozen_plan/` holds, unchanged, the recorded results of the code built for the frozen plan (four of six tests failed there).
- `frozen_plan_code/` holds the code and scripts that produced those results, as they were at the earlier commit. They are kept for the record and are not part of the amended plan.

## Running a script

Run each script in three modes. The printed output must be identical in all three. From this folder:

```text
python3.14 -I -B           known_answer/units_check.py
python3.14 -I -O -B        known_answer/units_check.py
python3.14 -I -B -W error  known_answer/units_check.py
```

The known-answer scripts take a size as their first argument: `smoke` (one twentieth of the plan's seeds, at least 10) or `full`. Smoke output is labelled SMOKE in its first lines and in its summary line. A smoke run is not a result.

```text
python3.14 -I -B known_answer/k1_exact_checks.py smoke
python3.14 -I -B known_answer/k6_gate_checks.py smoke
```

K2 and K3 can be split into parts with the same seeds: add the part number and the number of parts (`k2_nothing_in_noise.py full 3 12`). Each part prints counts only. Join the parts with `k2_combine.py full <part files>` and `k3_combine.py full <part files>`. K4 and K5 split by seed in the same way and join with `k4_combine.py` and `k5_combine.py`.

Every script ends with exit status 1 if its result is FAIL and 0 if PASS (`kcommon.summary`). The smoke driver records each exit status in `known_answer/out_smoke/status.txt`, and the three-mode runs in `known_answer/out_smoke/modes/status_modes.txt`.

At most 6 worker processes are used. The worker count does not change any result.

## Sandbox

The recorded runs had no network access and write access only to the build folder:

```text
env -u ANTHROPIC_API_KEY -u CEREBRAS_API_KEY -u ANTHROPIC_BASE_URL PYTHONDONTWRITEBYTECODE=1 sandbox-exec -p '(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath "<build folder>") (literal "/dev/null"))' perl -e 'alarm N; exec @ARGV' python3.14 -I -B known_answer/<script>.py smoke
```

## Hashes and times

`MANIFEST.sha256` lists the hash of every file here. Check it with `shasum -a 256 -c MANIFEST.sha256`. Wall and processor times of the smoke runs are in `known_answer/out_smoke/timing.txt`.
