# Independent check of Amendment 4

This folder holds the clean-room check of Amendment 4 (`AMENDMENT_4.md`). The checker wrote its own code and shared none with the author's tool. It opened no data file and no build folder. It read the public outcome log of the code branch (`OUTCOME_LOG_12cba0d.md`, a copy of the file at commit `12cba0d`) and nothing else about the code's outcomes.

## What Amendment 4 does

C1 replaces the transfer rule of reading D8: a transfer is adverse in a run if and only if fewer than R/40 of the random detectors score at or below the template's score, ties counted as at or below. C2 says what follows when a Law 2b instance fails its pre-data check. C3 defines a round of repair to a known-answer test, limits the rounds to two per test, and adds a key epoch for reruns.

## The passes and their verdicts

The checker read eight drafts. Seven were not ready. The eighth was ready, apart from one blank (the publication time) that the publisher fills at commit time.

1. First draft. Not ready. The account of the tie conflict was wrong (it lies inside item B8, not between D8 and B8), the stated direction of effect missed the moves to Partial, C2 left the Law 2b state of an untested instance open, and C3 did not say what a round is.
2. Second draft. Not ready. The key epoch was new and had no stated scope, "seen" and "definition" were undefined, and one sentence could override "transformed core".
3. Third draft. Not ready. An epoch 0 run had no stated meaning, the table of epochs needed the reading that an outcome includes runs on the same data draws, and a code-only change could retry a test on seen seeds.
4. Fourth draft. Not ready. Carrying out Amendment 4 in the code was not determined for K5 and K6.
5. Fifth draft. Not ready. An outcome that comes to exist after publication was not covered.
6. Sixth draft, with the outcomes paragraph filled by another hand. Not ready. The repair rule was not scoped to the code built for Amendment 3, and the paragraph needed attributions and one reading time.
7. Seventh draft. Not ready. Two sentences of the paragraph contradicted the later scope fixes.
8. Eighth draft. Ready.

## What was rebuilt with the checker's own code

- The collapse of "adverse under both readings" to the amended rule: every case with 1 to 160 detectors (708,560 class cases), 406,912 finite value cases with tolerance edges and all-tied blocks, and 25,704 cases with infinite and undefined scores. The amended rule never gives an adverse verdict that the old rule does not.
- The effect on outcomes, over all 5,832,000 states of the transfer rules with the known-answer tests passing. A change from adverse to neither can move Evidence against to Partial, Does not discriminate or Inconclusive, and Does not discriminate to Partial. It cannot create Supported or Net-dependent. The scale-flow outcomes behave alike.
- The Holm treatment of an untested instance (p = 1, family size kept): no test outside the failed set gains a rejection, in 521,017 exact cases.
- The key epoch: all 417,545 keys of the Amendment 3 families are distinct in every epoch, 1,252,635 keys and seeds are distinct across three epochs, and also across mixed epochs of different tests.
- Every quotation of the published plan, against commit `4c6ecd1`.
- That the author's tool rebuilds `PREREG.md` and `README.md` from `4c6ecd1` and `AMENDMENT_4.md` byte for byte.

## What was not verified

- Who read which outcome, and when. The paragraph in `AMENDMENT_4.md` gives these as statements of the code's author and the coordinator. Only the outcome log can be read.
- The git facts the code's author gives about the code of K4 and K5.
- That the plan's author saw no outcome. A file cannot show it.
- Whether the first K4 and K5 runs started on the working tree that git records.

## Rerun

From inside the repository, with Python 3.12 or later (standard library only): `independent_check/amendment_4/run_all.sh`. It reads the base files with git from commit `4c6ecd1`, runs each script in the three modes `-I -B`, `-I -O -B` and `-I -B -W error` one at a time, and compares them. `check_published.sh` compares the published files with `PUBLISH_MANIFEST.tsv`.

## The published commit

The check was made on the published commit `11cb5883e2fddbb9133956bb8154d96195cdb3b3` on `outside/continuum-four-transformations-prereg`, on top of `2d24771`, committer date 2026-11-23T11:40:28Z. Author and committer are the noreply address, and the message names no person and no path.
SHA-256 of the published files: `AMENDMENT_4.md` `79c321b750024e7746c7061291821fe8c706ff0aca1f103d16a0e643e6ddf712` (25,954 bytes), `README.md` `1dd1af4cfa92e6c643f98ec075c0e4940433a7ae22d2c1654fa57023c7223e60` (3,017 bytes), `PREREG.md` `3adc9cdbc2b13fc15a0f3de5a67a4c033601e6d747139767cc4002b90eaaa206` (118,319 bytes). `PUBLISH_MANIFEST.tsv` lists all 13 files of the commit.

## Results after the push

- The commit touches exactly 13 paths, and all 13 equal the manifest in SHA-256 and size.
- `AMENDMENT_1.md` to `AMENDMENT_3.md`, `independent_check/`, `checks/amendment_2/` and `checks/amendment_3/` are identical to `2d24771`.
- The only change in `AMENDMENT_4.md` against the draft the checker last read is the publication time, 11:40:28Z. It equals the committer date, and the `git log --diff-filter=A` command in the text returns this commit.
- The hash table in `README.md` is right. The author's tool rebuilds `PREREG.md` and `README.md` from the published `AMENDMENT_4.md` byte for byte.
- `check-prose.py` exits 0 on the three plan files, and the 13 files hold no local path, email or name.
- The scripts in `src/` were rerun on the published files in the three modes, with identical output and every RESULT line passing (`out/`).

## What this folder does not cover

- Who read which outcome and when, the git facts about the code of K4 and K5, and the statement that the plan's author saw no outcome. They are statements of other people.
- Whether the code carries out the amendment. No code was checked.
- Any data file. None was opened.
- The description text on the pull request.
