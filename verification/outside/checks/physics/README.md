# Physics checks (AUDIT-011R, 012, 013R, 018)

These scripts check the physics results of the gravity and fractals draft pull requests with code that does not share the sibling team's verifier. Each one has two sides: scripts named "independent" are the first-pass checks, scripts named "advocate" are the second pass that argued for the team and narrowed or confirmed a finding. Every script prints one `RESULT` line and exits 0 only if all its checks held.

## Scripts

All commands run from this folder. `G` is a clone of Foundation-0/gravity and `F` is a clone of Foundation-0/fractals, both at the commits below. Every Python script gives the same output under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`. The node script gives the same output on two runs.

| Script | What it backs | Command | Runtime | Result line |
|---|---|---|---|---|
| a011r_schur_closure_independent.py | AeST Schur identity exact, slow-mode closure passes the 1 percent gate at 5 protocol k and 6 unreported k, fails on fast-contaminated preparations | `python3 -I -B a011r_schur_closure_independent.py G` | 5 s | PASS 38 of 38 checks, protocol-k worst error qsa 0.590%, helm 0.467% |
| a011r_closure_orders_advocate.py | The 0.37 percent residual is the gap between two exact preparations, not a closure error, 0.00008 percent on its own manifold | `python3 -I -B a011r_closure_orders_advocate.py G` | 5 s | PASS 58 of 58 checks, H3 residual 0.371% to 0.377% equals the preparation gap |
| a011r_probe_hashes.py | check_007 pins stale hashes (fa4d3a1b, 35e16732), current files hash to bcde4938, ed74a3a4, 6d467347 | `python3 -I -B a011r_probe_hashes.py G` | under 1 s | PASS 12 of 12 checks, hashes match the recorded values |
| a012_threshold_anchors_independent.py | Galaxy hold-out, zero-parameter 185.59 acceptable on all catalogs, latch rank 3 of 126, SPARC to KiDS-1000 anchor 31.5 to 69.9 | `python3 -I -B a012_threshold_anchors_independent.py G` | 32 s | PASS 35 of 35 checks, trained threshold 74 and 145 km/s |
| a012_threshold_profiles_advocate.py | "Decisively falsifies" is false as worded, 120 systems disfavour 185 (delta chi-squared 11.6 to 17.1), galaxies need at least about 173, 60.15 is an optimiser artifact | `python3 -I -B a012_threshold_profiles_advocate.py G` | 19 s | PASS 39 of 39 checks, Hill threshold 150 km/s, not 60.15 |
| a013r_box_certifier_independent.py | Inertia box certifier is sound, no straddling box certified | `python3 -I -B a013r_box_certifier_independent.py G` | 74 s | PASS 16 of 16 checks, 499 boxes certified, 4990 points, 0 unsound |
| a013r_box_certifier_advocate.py | 2,795 certified boxes, 22,360 exact points, 0 violations, indefinite inertias included | `python3 -I -B a013r_box_certifier_advocate.py G` | 42 s | PASS 11 of 11 checks, 2795 certified boxes, 22360 points, 0 violations |
| a018_lindblad16_independent.py | Eight Schur diagonals and Jordan ranks (12,8) and (14,12) match an independent build | `python3 -I -B a018_lindblad16_independent.py` | 1 s | PASS 10 of 10 checks, Jordan ranks (12,8) and (14,12) |
| a018_slow_rate_advocate.py | Exact slow rate differs from the s = 0 Schur rate at O(g^2) when gamma_tid is not 0, ratio tends to 1 | `python3 -I -B a018_slow_rate_advocate.py` | 1 s | PASS 21 of 21 checks, ratio 1.0000004 at N=100, gt=0 |
| a018_modeljs_numbers.js | model.js numbers reproduce (2.41e-14 s, 1.42e21 s, m* 2.83e-20 and 1.34e-19 eV, slope 10) | `node a018_modeljs_numbers.js F/witness-map/model.js` | under 1 s | PASS 6 of 6 checks, slope 10.000000 |

The scripts that need a clone also accept `GRAVITY_REPO` (or `FRACTALS_MODEL_JS` for the node script) in place of the argument. Add `--verbose` to see the full numbers. Seeds are fixed and printed: 777001 (a012 anchors), 90210 (a013r independent), 4242 and 777 (a013r advocate).

## Targets

- Foundation-0/gravity draft pull request 30, commit 00d8b1b652952dadf8fd769d9d0690dabd4bcc13.
- Foundation-0/fractals draft pull request 59, commit 84535c15e76489c75cbdf1c6dc2ccd8fc4794fae. Only the node script reads it.

Python 3 with numpy, scipy and sympy, and node, were used. Every number in the reports and VERDICTS was reproduced by a clean rerun from fresh clones.

## Not covered

- The expedition's own verifier (check_011) is not rerun here.
- The Galactic Centre claims of AUDIT-018 rest on model assumptions and are not checked.
- The 185 km/s and 60.15 km/s statements are checked on the host catalog only, not on new data.
- The Lean file and the prior-art labels are outside these scripts.
