# Outside-observer check

A second team's independent check of the results in this repository's ledger, made on 2026-11-21 under this repository's own protocol.

| File | What it holds |
|---|---|
| [`OUTSIDE_AUDIT.md`](OUTSIDE_AUDIT.md) | What holds, the labels after both passes, the sentences to fix with their repairs, and the limits of the check |
| [`rulings.json`](rulings.json) | Every first-pass finding that narrowed a claim, with the second-pass ruling, its reason and the strongest claim that survives |
| [`checks/`](checks/) | The independent scripts, one folder per group of results, each with its own README |

## Two passes

An evaluator checked each group of results with code that shares nothing with the expedition's. An advocate then argued the expedition's side against every narrowing finding. Of 36 such findings, 13 stood as written, 22 were narrowed and 1 fell.

## How to rerun

Each folder under `checks/` has a README with the exact command for each script, what it needs, how long it takes and the result line to compare. The scripts take the location of a clone of the public target repo from a command-line argument or an environment variable. They use the Python standard library, and SymPy, NumPy or SciPy only where the README says so.

Every script was run under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`.

## Standing

This folder is a contribution from outside the expedition team. It changes no file of theirs. The labels in `OUTSIDE_AUDIT.md` are the observer's reading and are open to correction in the same way the ledger is.
