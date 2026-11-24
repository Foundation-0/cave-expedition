# Rerun

This folder holds the code and the known-answer runs for the plan in `PREREG.md`. It touches no real data and downloads nothing.

You need Python 3.14 with numpy 2.5.4. The standard library and numpy are the only dependencies. The recorded runs used Python 3.14.6.

Run each script in three modes. The printed output must be identical in all three. From this folder:

```text
python3.14 -I -B           known_answer/k1_exact_checks.py
python3.14 -I -O -B        known_answer/k1_exact_checks.py
python3.14 -I -B -W error  known_answer/k1_exact_checks.py
```

Scripts without parts: `k1_exact_checks`, `k4_transfer`, `k5_scale_flow`, `k6_gate_checks`, `x1_plan_arithmetic`, `x2_controls`, `x4_sawtooth_reading`. Each output is in `known_answer/out/<script>.txt`.

K2 runs in seven parts (`k2_nothing_in_noise.py 0` to `6`), K3 in three (`k3_planted_structure.py 0` to `2`) and X3 in three (`x3_iaaft_cap_sensitivity.py 0` to `2`). Part outputs are in `out/k2_part*.txt`, `out/k3_part*.txt` and `out/x3_part*.txt`. Join the parts with:

```text
python3.14 -I -B known_answer/k2_combine.py <folder holding k2_part0.txt to k2_part6.txt>
python3.14 -I -B known_answer/k3_combine.py <folder holding k3_part0.txt to k3_part2.txt>
```

The recorded runs had no network access and write access only to the build folder:

```text
sandbox-exec -p '(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath "<build folder>") (literal "/dev/null"))' perl -e 'alarm 1800; exec @ARGV' python3.14 -I -B known_answer/<script>.py
```

K2, K3, K4, K5 and X3 use a pool of worker processes. The worker count does not change any result.

Check the file hashes with `shasum -a 256 -c MANIFEST.sha256`. The hashes of every run in the three modes are in `known_answer/out/three_mode_check.txt`. Run times are in `known_answer/out/timing.txt`.
