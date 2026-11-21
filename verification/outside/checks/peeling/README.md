# Peeling checks (AUDIT-004 Part A, AUDIT-008R)

These scripts check the peeling tower and the 008R identities of quotient-lp-bounds draft pull request 5 with code that shares nothing with the sibling team's. Three scripts come from the first pass (the evaluator). Two come from the second pass (the advocate), which narrowed the strict-dominance finding. Each script prints one result line and exits 0 only if every check in it held.

## Scripts

Run each one from this folder. `CLONE` is the path of a local clone of quotient-lp-bounds at the commit below. Setting `QLB_CLONE` works in place of the argument. All five are exact (fractions, SymPy). Two use NumPy and SciPy.

| Script | What it backs | Command | Runtime | Result line |
|---|---|---|---|---|
| `peel_tower_check.py` | Tower 64 / 112 / 124, optimum 124, fair baseline 84, hardin 114 against 237/2, optimality theorem, rounding rule | `python3 -I -B peel_tower_check.py CLONE` | 6 to 7 s | `PEELING_TOWER_CHECK OK: PR5 instance 64/112/124 (single quotients 64, 84), 12 orders 52 to 124, hardin 114 < 237/2, repo3 best 60 (orders 16 to 60) LP 68 truth 80, optimality repair 0 failures in 10272, seed 777` |
| `peel_tower_supplement.py` | Smallest witnesses per hypothesis, per-layer rounding bound (needs `peel_tower_check.py` beside it) | `python3 -I -B peel_tower_supplement.py CLONE` | 1 s | `PEELING_SUPPLEMENT_CHECK OK: 3 witness classes, 3396 rounding checks (max ratio 2/3), 14 zsl layers feasible, seed 31337` |
| `peel_008R_check.py` | 008R identities R1 to R3, cone example where Claim 10(c) fails | `python3 -I -B peel_008R_check.py` | 1 to 2 s | `PEELING_008R_CHECK OK: R1 40 graphs 0 stochastic; R2 root only q = 1/2; R3 identity on 60 on-family, fails on 54 off-family; claim 10(c) 3 -> 1` |
| `peel_advocate_tower.py` | Counterexample behind the dominance sentence: hardin 114 against 237/2, baseline 84 | `python3 -I -B peel_advocate_tower.py CLONE` | under 1 s | `PEELING_ADVOCATE_TOWER OK: PR5 instance 64/84 -> 112 -> 124 (LP 124); hardin 114 < 237/2 (72 of 104 edges slack); imb->y 52 < 56; y->x ties 84; repo3 LP 68, truth 80` |
| `peel_advocate_f2_f4_f5.py` | True narrowed dominance form, Doob reading, optimality by brute force (needs `peel_advocate_tower.py` beside it) | `python3 -I -B peel_advocate_f2_f4_f5.py CLONE` | 18 to 20 s | `PEELING_ADVOCATE_F2_F4_F5 OK: F2 0 failures in 822, F4 0 stochastic rows, F5 0 failures on 17067 graphs, seed 20261120` |

Every script gives byte-identical output under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`. The scripts open no network connection and use no bare assert.

## Targets

- Foundation-0/quotient-lp-bounds, draft pull request 5, head commit 996108af84dd03598df1ffca43281a9c331faa72. Fetch it with `git fetch origin pull/5/head`.
- The repo's own instances are read from `certificate.json` in that commit (soko, hardin, cyclic switch). The 32-state system is rebuilt from the pull request's docstring.

## Not covered

- The sibling team's own verifier is not rerun here.
- The N0 label for the tower and the optimality theorem rests on reading Keller et al. (IJCAI 2016) and Seipp, Keller and Helmert (JAIR 2020). No script checks that.
- The 185 km/s, 011R and other physics results belong to other areas.
- The quotients are the ones in the pull request and its certificate. Other instances are not tested.
- The span LP in `peel_advocate_tower.py` uses HiGHS to propose a solution. Its primal and dual are then checked exactly.
