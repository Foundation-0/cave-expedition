# Known-answer folder of the code branch

This file belongs to the code branch. The plan's own `README.md` one level up is the published plan file and is not edited here.

What is where:

- `units_check.py`, `key_check.py`, `review_witnesses.py`: checks of the building blocks, of every seed key (D14) and of the outside reviews' witnesses. Each exits with status 1 on a failure.
- `k1_exact_checks.py` to `k6_gate_checks.py` and the files that join their parts: the known-answer tests.
- `mutation_test.py`, `key_count.py`: the mutation tool and a counter of the keys the K4 and K5 code builds.
- `OUTCOME_LOG.md`: every run on the Amendment 3 code, with its time, the state of the code and who has read it. `hygiene.sh`: the checks to run before every push, including that the plan files are byte-identical to the plan branch tip. `FULL_RUN.md`: how to run one family at full count (on hold).
- `run_full.sh`, `sbpy.sh`: the driver of the full runs. It has not been run, and the full runs are on hold.
- `SMOKE_RESULTS.md` and the `out_smoke*` folders: smoke runs (one twentieth of the plan's seeds, at least 10). They are not results. `out_amendment3/` holds the outputs of the Amendment 3 build.
- `out_frozen_plan/`: the recorded results of the frozen plan's code, unchanged.

`../RERUN.md` says how to run everything. `../AMENDMENTS_NEEDED.md` lists every choice the plan left open and every question for the plan's author.
