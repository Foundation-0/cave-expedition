# Pre-registered test of the four-transformations claim

This folder fixes, before any data file is opened, a test of one sentence in the continuum essay (Foundation-0/continuum, PR #1, `continuum.md` line 16).
That sentence says raw sensor data from very different domains show the same four transformations.

Status: pre-registered, then amended once (`AMENDMENT_1.md`) after the files were fetched and before any was opened. No statistic has been computed on real data.
On synthetic series the frozen plan failed four of its six known-answer tests. The amended tests have not yet been run, and no data file will be opened until they all pass.

`PREREG.md` is the plan as amended: claim, repaired claim, statistics, controls, thresholds and outcomes. The frozen plan stays retrievable at commit `24d7757`, and `AMENDMENT_1.md` lists every change.
`DATA_REQUEST.md` lists the public raw files the test needs (about 635 MB). All were fetched on 2026-11-22 and none has been opened.
`ARM_B_OUTLINE.md` sketches a later test of the project's working hypothesis itself.
`FETCH_MANIFEST.tsv` pins each fetched file by SHA-256. `checks/` holds the scripts behind Amendment 1.

Claim type: sampled. Two of the four transformations get a measurable form here. The other two, and half of a third, need an operational definition from the essay's authors.
