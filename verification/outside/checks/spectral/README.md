# Outside checks: spectral (AUDIT-002, AUDIT-014, AUDIT-016R)

These scripts check the spectral-inertia results with code that shares nothing with the expedition's own verifiers. They cover the rank envelope R_opt and its sharpness, the higher-moment bounds A2, A3 and A4, and the two inertia-certificate checkers. Each script prints one result line and exits 0 only if every check in it held.

## Setup

Python 3 with numpy, SciPy and SymPy. Four scripts read the clones below through two environment variables. The others need no clone. Nothing here uses the network.

```
git clone https://github.com/Foundation-0/spectral-inertia.git
git clone https://github.com/siliconcordat/loom.git
git -C loom fetch origin pull/7/head && git -C loom checkout FETCH_HEAD
export SPECTRAL_INERTIA_DIR=$PWD/spectral-inertia
export LOOM_SCRIPTS_DIR=$PWD/loom/scripts
```

Run each script from this folder as `python3 -I -B <script>`. Every script finishes in under 3 minutes. All three modes (`-I -B`, `-I -O -B`, `-I -B -W error`) gave identical output.

## Scripts

| Script | What it backs | Command | Runtime | Result line |
|---|---|---|---|---|
| check_rank_envelope_and_moments.py | R_opt chain and bound hold on fresh exact matrices, A2, A3, A4 never exceed n+(H_perp), null controls fire (002, 014) | `python3 -I -B check_rank_envelope_and_moments.py` | 45 s | `RESULT check_rank_envelope_and_moments: PASS cases=800 complex=488 noncommuting=399 A2=5378 A3=3662 A4=3200 witnesses, 0 violations, null controls fired (A2 29, A4 232, R_opt 177)` |
| check_sharpness.py | explicit matrices of rank exactly max(1, ceil R_opt) (002) | `python3 -I -B check_sharpness.py 800 777` | 15 s | `RESULT check_sharpness: PASS tuples=1102 realised_exactly=1102 failures=0 max_rank=114` |
| check_dual_checkers.py | the two inertia checkers agree on 400 matrices and 800 tampered certificates (016R) | `python3 -I -B check_dual_checkers.py` | 8 s | `RESULT check_dual_checkers: PASS matrices=400 tampered=800 wrong_inertia_or_wrong_accept_or_crash_or_disagreement=0 (raw string formats rejected without mapping: 400 of 400 and 400 of 400)` |
| check_must_fail_controls.py | each checker rejects the other's must-fail inputs (016R) | `python3 -I -B check_must_fail_controls.py` | 8 s | `RESULT check_must_fail_controls: PASS 29 controls rejected by both checkers, known-good accepted by both, n=8,16,24 agree` |
| check_interop_formats.py | the dual oracle rejects raw loom certificates at head, accepts them at 1dc18e4, and both agree after conversion (016R, sentence for repair, loom docs/11) | `python3 -I -B check_interop_formats.py` | 1 s | `RESULT check_interop_formats: PASS matrices=4 converted certificates accepted with equal inertia by both checkers=yes; raw loom certificates rejected by the dual oracle: 4 of 4; raw dual-oracle certificates rejected by the loom checker: 4 of 4` |
| check_recount_420.py | R_opt is never below the docs/10 best member, strictly above on 417 of 420, integer gain on 202 (002, second pass) | `python3 -I -B check_recount_420.py` | 1 s | `RESULT check_recount_420: PASS total=420 strict=417 ties=3 below=0 chain_violations=0 ceil_gain=202 docs10_positive=15` |
| check_moment_bounds_a2.py | the Christoffel-function remark fails for n+, A2 is a restricted case of the sharp degree-4 bound (014, second pass) | `python3 -I -B check_moment_bounds_a2.py` | 11 s | `RESULT check_moment_bounds_a2: PASS christoffel_counterexamples=hold lp_exceeds_A2_by_0.1=174 of 200 lp_below_A2=0 lp_above_n_plus=0` |
| check_a4_vs_a2.py | A4 beats A2 and R_opt on a structured class, never on generic samples (014, second pass) | `python3 -I -B check_a4_vs_a2.py` | 2.5 min | `RESULT check_a4_vs_a2: PASS violations=0 A4_beats_A2_and_R_opt: generic=0 of 600, weak=29 of 300, team_examples=both` |
| check_a4_vs_sharp_deg4.py | A4's gain over the sharp degree-4 moment bound comes from tr Q (014, second pass) | `python3 -I -B check_a4_vs_sharp_deg4.py` | 1 min | `RESULT check_a4_vs_sharp_deg4: PASS A4 beats max(A2,R_opt) in 24 of 300 weak samples, sharp degree-4 LP reaches A4's integer in 0 of them, A4 above LP in 24, LP above n_plus in 0` |
| check_fixed_n_sharpness.py | no fixed-size counterexample to sharpness in a numerical probe (002, second pass) | `python3 -I -B check_fixed_n_sharpness.py` | 10 s | `RESULT check_fixed_n_sharpness: PASS tested=41 realised_at_same_n=41 candidate_failures=0` |
| selftest_exactlib_a.py | the first exact helper library matches NumPy eigenvalue signs | `python3 -I -B selftest_exactlib_a.py` | 2 s | `RESULT selftest_exactlib_a: PASS cases=300 mismatches=0` |
| selftest_exactlib_b.py | the second exact helper library matches NumPy eigenvalue signs | `python3 -I -B selftest_exactlib_b.py` | 1 s | `RESULT selftest_exactlib_b: PASS cases=300 mismatches=0` |

`exactlib_a.py`, `exactlib_b.py` and `common.py` are libraries, not scripts.

Second runs.

- `check_rank_envelope_and_moments.py 800 777` gives the other 800 matrices: complex=523 noncommuting=426 A2=5426 A3=3708 A4=3200 witnesses, 0 violations, null controls fired (A2 18, A4 210, R_opt 175).
- `check_sharpness.py` with no arguments gives 552 tuples.
- `check_interop_formats.py` against commit 1dc18e4 gives 0 of 4 raw loom certificates rejected.
- `check_a4_vs_a2.py 202` gives weak=19 of 300. `check_a4_vs_sharp_deg4.py` uses seed 303 and gives the line above.

## Targets

| Repository | Commit |
|---|---|
| Foundation-0/spectral-inertia, default branch | 8394da989912bbc3a0e8702124aeec1d05b4801f |
| Foundation-0/spectral-inertia, interop comparison only | 1dc18e495b1ecd018bb8d819d6b61f8441eb6586 |
| siliconcordat/loom, draft pull request 7, files scripts/inertia_cert.py and scripts/verify_inertia.py | e853638ef186868a21762787a95c11d47c2d0ebe |

## Differences from the reports

Every number in VERDICTS.md and the reports that these scripts back reproduced exactly. Three of them need a note on how they are reached.

- Sharpness, 1,102 parameter sets. One run of the original size gives 552 tuples. A run with 800 random tuples and seed 777 gives 1,102. The original arguments for the second set were not in the logs, so this match is by count.
- Matrices, 1,600. Two runs of 800 (seeds 20261121 and 777) give 1,600. The 12,240 witnesses are the first run alone.
- A4 field a4_lt_h4_real. In the original general family the field was 9 in one run and 0 in the other with the same seed. The rerun gives 0. No result line depends on it.

## Not covered

The Lean file, the expedition's own verifiers and their stale checks, the speed timings of the two checkers, and the prior-art reading are not packaged here. The 420-case recount rebuilds the matrices from the team's random call order and does not import the team's script. The float searches in the A4 and fixed-size scripts can move slightly with the SciPy version.
