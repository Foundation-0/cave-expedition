# Pre-registered test of the four-transformations claim

This folder fixes, before any data file is opened, a test of one sentence in the continuum essay (Foundation-0/continuum, PR #1, `continuum.md` line 16).
That sentence says raw sensor data from very different domains show the same four transformations.

Status: pre-registered, then amended three times (`AMENDMENT_1.md`, `AMENDMENT_2.md`, `AMENDMENT_3.md`) after the files were fetched and before any was opened. No statistic has been computed on real data.
On synthetic series the frozen plan failed four of its six known-answer tests. The amended tests have been run only as smoke runs of the code: one twentieth of the plan's seeds, with the full 10 seeds for K4 and K5 under Amendment 1, and smoke runs of the ported code since.
Their outcomes were known to the code's author and to the party who routed the questions. The plan's author has read none of their outputs.
What reached the plan's author is disclosed in the amendments: the observed behaviour behind items B5, B6, B7 and B9, one smoke figure used in B11, a K5 smoke run that stopped on an overflow at seed 0, the code's author's count that the old map overflows in 9 of 10 seeds, and a K1 smoke run that failed on a fault of the test harness.
No full-count run of K1 to K3 has been made. No data file will be opened until every test passes at its full count.

`PREREG.md` is the plan as amended: claim, repaired claim, statistics, controls, thresholds and outcomes. The frozen plan stays retrievable at commit `24d7757`, and `AMENDMENT_1.md` to `AMENDMENT_3.md` list every change.
`DATA_REQUEST.md` lists the public raw files the test needs (about 635 MB). All were fetched on 2026-11-22 and none has been opened.
`ARM_B_OUTLINE.md` sketches a later test of the project's working hypothesis itself.
`FETCH_MANIFEST.tsv` pins each fetched file by SHA-256. `checks/` holds the scripts behind Amendment 1, `checks/amendment_2/` those behind Amendment 2 and `checks/amendment_3/` those behind Amendment 3.
The check scripts use the Python standard library only, except the three `checks/sim_*.py` scripts and `checks/amendment_3/amp_maps.py`, which need numpy, and `checks/amendment_2/derive_yprime.py`, which needs numpy and scipy (versions in `checks/amendment_2/ENVIRONMENT.md`).

Claim type: sampled. Two of the four transformations get a measurable form here. The other two, and half of a third, need an operational definition from the essay's authors.

SHA-256 of the plan files as of Amendment 3:

| File | SHA-256 |
|---|---|
| `PREREG.md` | `68b94fbff0bcb8ff41b28150e5f275c68658f7696834f2584281647aaa1f73a0` |
| `AMENDMENT_1.md` | `771c5d4c44a233ef14837d3d91a0349413ccca080cfc1214649592d838e3157a` |
| `AMENDMENT_2.md` | `93e170b3f3d01405d1a92ed8131095dca85844f7eae8c5843da38019bf088d90` |
| `AMENDMENT_3.md` | `8ecde959deffbc6f4ead303b33b0b7e705e94387989d79fb7b4aa2af15a498a1` |
