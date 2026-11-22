# Outside-observer check

A second team's independent check of the results in this repository's ledger, made on 2026-11-21 under this repository's own protocol.

| File | What it holds |
|---|---|
| [`OUTSIDE_AUDIT.md`](OUTSIDE_AUDIT.md) | What holds, the labels after both passes, the sentences to fix with their repairs, and the limits of the check |
| [`rulings.json`](rulings.json) | Every first-pass finding that narrowed a claim, with the second-pass ruling, its reason and the strongest claim that survives |
| [`SOURCES.md`](SOURCES.md) | The five prior-work sources behind the ratings: title, venue, year, identifier, the lemma or section used, and what was read |
| [`REVIEW-RESPONSE.md`](REVIEW-RESPONSE.md) | One row per item of the review of this pull request: what was found, what changed, the command that shows it |
| [`check_totals.py`](check_totals.py) | Recounts the totals from `rulings.json` and compares them with the text |
| [`checks/`](checks/) | The independent scripts, one folder per group of results, each with its own README |

## Two passes

An evaluator checked each group of results with code that shares nothing with the expedition's. An advocate then argued the expedition's side against every narrowing finding. Counting from `rulings.json`, 36 first-pass findings carry 37 rulings, because one finding (`folds-dn-e8` F1) had a label part and a wording part: 14 stood as written, 21 were narrowed and 2 fell.

## Which ledger revision each audit number refers to

The audit numbers do not all live on one revision of `verification/AUDIT_LOG.md`.

| Audit numbers | Where they are | Commit the checks were made against |
|---|---|---|
| AUDIT-001 to AUDIT-019 | `main` | `a126bfd`, "Initial publish" |
| AUDIT-020R | only on the authors' open pull request 1, branch `expedition/sync-audit-020r-and-pr-links`. Added by `377392b` | the same branch at `872fffd6a82fe8a9d7a30d9cdd907ec73690efd4` (committed 2026-11-20 19:33 -0600), the head our evaluators' clone was on |
| AUDIT-021 | only on that branch. Added by `f3966f9` | the same head `872fffd`. AUDIT-021 itself was not checked (see `OUTSIDE_AUDIT.md`, section 5) |

To see it: `git show origin/main:verification/AUDIT_LOG.md | grep -c "020R\|AUDIT-021"` prints 0, and the same command on `origin/expedition/sync-audit-020r-and-pr-links` at `872fffd` prints 2. Between `a126bfd` and `872fffd` the log file differs by three added rows, AUDIT-020, AUDIT-020R and AUDIT-021 (`git diff a126bfd 872fffd --stat -- verification/AUDIT_LOG.md` shows 3 insertions), so every other audit number reads the same on both revisions. The branch has moved on since, and we did not recheck against its later commits. AUDIT-020R, the only one of the three that this check covers, is read at the pull request 1 revision.

## How to rerun

Each folder under `checks/` has a README with the exact command for each script, what it needs, how long it takes and the result line to compare. The scripts take the location of a clone of the public target repo from a command-line argument or an environment variable. They use the Python standard library, and SymPy, NumPy or SciPy only where the README says so.

Every script, including `check_totals.py` and the mutation check `checks/twoloop_stack/mutate_stack_guards.py`, was run under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`, and the three outputs were identical.

## Standing

This folder is a contribution from outside the expedition team. It changes no file of theirs. The labels in `OUTSIDE_AUDIT.md` are the observer's reading and are open to correction in the same way the ledger is.
