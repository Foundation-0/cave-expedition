# Independent check of Amendment 3

This folder holds the clean-room check of Amendment 3 (`AMENDMENT_3.md`, published at commit `4c6ecd1`). The checker wrote its own code and shared none with the author's `checks/amendment_3/`. It read the author's scripts only after it had its own numbers. It opened no data file and read no smoke output.

## What each of the five passes checked, and the verdict

Each pass was made on a draft before publication. Nothing was published until the fifth.

1. Draft `PREREG.md` fcf587da. Every seed-key family rebuilt, the amplitude-map change (SK8), the compute row (SK9), the opening and disclosure, every changed block against `1aa53fb`, quotations, hashes, prose. **Not ready**, for these reasons:

   - The Amendment 2 account needed an erratum, and the disclosure over-claimed.
   - The K5 pool instrument could be read to collide, and the null replicates had no net named.
   - One step of reading D19 did not follow (a bound of 7.2 does not give 1,300), and the K1 draw count used two conventions.
2. Draft 213308ba. The corrected disclosure, D14 pools named by their own series, D20 and D21. **Not ready.** The status line and README said the author had read no outcomes, while the amendments show some reached the author. The "9 of 10" overflow figure was not attributed. D20 was adopted from the code's source, so a smoke outcome could have shaped it.
3. Draft 316ac5de. The attributed disclosure and the D20 basis. **Not ready.** The code author's overflow count was missing from the lists of what reached the plan's author. The D20 basis did not say whether the code's stream set predates its smoke run.
4. Draft 641a4663. A new criterion: K4 must pass under D20 and under a second reading. **Not ready.** It needed a pointer in section 10 and in the gate sentence, the detectors of the blind spot in the placement run spelled out, the Law 2b paired K4 tests given a reason for using D20 alone, and a statement that real data does not use the second reading.
5. Draft 68b94fbf. Wording only. **Ready.** The published files match `PUBLISH_MANIFEST.tsv`, 27 of 27, and the commit touches only those paths.

## Numbers rebuilt with the checker's own code

- Seed keys, own key builder, one key per independent random start in every family, no key with two owners.
- K1 6,884 draws on 1,001 keys. K2 36,400 on 36,000. K3 13,000 on 9,600. K4 under D20 alone 4,480 on 4,460, and with its second reading 6,180 on 6,100 (1,600 new pool draws, 40 new detector sets, 60 draws shared with D20 by design). K5, the plan's 10 series sets, 11,150 on 11,130.
- All families together 417,545 distinct keys and 417,545 distinct 64-bit seeds. The K4 superset family already holds the second reading's keys, so the total does not grow with it.
- Must-fail controls flagged: the old K5 pool keys (11,000 draws on 880 keys), the old detector keys, the other reading of the K5 pool instrument (11,000 on 8,800), null replicates without the instance in the net (3,120 collisions), control pools keyed like segment pools, a Law 2b net without the run.
- Compute, exact rationals: K3 row 11,450.00, K4 second reading 3,664.00, known-answer total 258,126.41, one mode 288,981.87, three modes 866,945.61.
- SK8: the old map collapses the K5 cascade (2 to 8 distinct values of 524,288 in 10 seeds, overflow in 93 percent of 200). `amp_lognormal` is finite, keeps ties and creates none, and the two nets are bit-identical on a cascade and on its mid-ranks. The table numbers agree within sampling error. Reading D19 bound: below 7.131, so below 1,251.
- 40 confirmatory tests, 102 Law 2b tests, 11,664,000 and 11,664 outcome states with one outcome each.

## What could not be verified

- The git facts in the D20 basis (commit `a894e31`, the timing, the byte-identical rerun). They are the code author's report, labelled so in the plan.
- Whether K5's new positive criterion passes. That needs the flow code. A proxy of the checker's own (order-3 pattern profiles of block means) keeps the departure shape under the rank map. It is not the plan's statistic.
- The numpy version behind the older `checks/sim_*.py` outputs was not recorded.

## Rerun

From inside the repository, with a Python 3.12 or later that has numpy: `PY=python3 independent_check/amendment_3/run_all.sh`. It runs each script in the three modes `-I -B`, `-I -O -B` and `-I -B -W error` and compares them, reruns the author's three scripts against their committed outputs, and runs `check_published.sh`. The outputs here were made with Python 3.14.6 and numpy 2.5.4. `PUBLISH_MANIFEST.tsv` lists the 27 files of the published commit with their SHA-256 and size.

## Confirmed commit

The published files were compared byte for byte with the manifest at commit `4c6ecd11ec63a07a5900995fd7dc1df2383ee9b7`: 27 of 27 equal. That commit touches only those 27 paths, and `AMENDMENT_1.md`, `AMENDMENT_2.md` and `independent_check/` are identical to `1aa53fb`.
