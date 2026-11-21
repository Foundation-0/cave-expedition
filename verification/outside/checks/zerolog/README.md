# Checks for AUDIT-010 (zero-log theorems and the Sabra and percolation measurements)

These scripts check the claims of AUDIT-010 on code that shares nothing with the study's own verifier. Two exact scripts test Theorems A and B against independent oracles. Two sampled scripts rerun the live Sabra and percolation models on fresh seeds. Each script prints one result line and exits 0 only if every check in it held.

## Scripts

Set `FRACTALS_REPO` to a clone of Foundation-0/fractals at the commit below, or pass the path as the first argument. The sampled scripts also need `node`. The exact evaluator script needs SymPy. Nothing uses the network.

| Script | What it backs | Command | Runtime | Result line (start) |
|---|---|---|---|---|
| `check_exact_evaluator.py` | Theorems A, B, C hold (chain oracle, Fourier-Motzkin, chord triples, each ray needed), and the README witness defect | `python3 -I -B check_exact_evaluator.py "$FRACTALS_REPO"` | 4 s | `ZEROLOG_EXACT_EVALUATOR OK: A 1500/1500 agree ... B 1500/1500 ... rays needed 4/4` |
| `check_exact_advocate.py` | Same theorems by a second route (Bellman-Ford witness, convex hull), the smallest example, sliding four-point windows misdecide for m at least 5, and the README witness defect | `python3 -I -B check_exact_advocate.py "$FRACTALS_REPO"` | 1 s | `ZEROLOG_EXACT_ADVOCATE OK: A STP 1500/1500 (87 feasible ...) ... sliding windows wrong m=5,6,7 4,10,4` |
| `check_sampled_evaluator.py` | K41 fails the all-pairs test at 5 SE on 16 of 16 seeds, the period-2 ripple is real, and percolation D_eff rises | `python3 -I -B check_sampled_evaluator.py "$FRACTALS_REPO"` | 185 s | `ZEROLOG_SAMPLED_EVALUATOR OK: K41 all-pairs pass F2 0/16 F6 0/16 F3 16/16; ...` |
| `check_sampled_advocate.py` | "Refutes period 3" has no power, the seed 7 value is 0.5639 and not 0.659, and the unshipped shuffle p-values are rebuilt | `python3 -I -B check_sampled_advocate.py "$FRACTALS_REPO"` | 50 s | `ZEROLOG_SAMPLED_ADVOCATE OK: replay identical True; seed 7 p=3 dev 0.563938 ...` |

`sabra_dump.js`, `sabra_dump_seeds.js` and `perc_dump.js` are helpers. The Python scripts call them to run the live models. Two node runs of each give identical output, apart from a timing field in `sabra_dump.js` that no script reads.

## Target

Foundation-0/fractals, draft pull request 60, head commit `f6cb822d9ac5fd8c4247c5994a51b1058bca0af9` (base `48b923bd25dbcfef7fa8e8399d4144592145f0ef`). The live models are `turbulence/model.js` and `critical/model.js` in that same checkout.

Each script gave the same output under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`. Add `--details` to print the full JSON. Seeds are fixed and printed: 77123, 4242 and 777 for the Python code, and fixed seeds in the dump calls.

## Not covered

The prior-art readings (Dechter, Meiri and Pearl 1991, Baron, Matkowski and Nikodem 1994, L'vov et al. 1998) and the N0 labels are reading, not code, so no script backs them. The study's own verifier and the check_006 deliverables are not rerun here. The second percolation octave change is not resolved by 20 seeds. The law for the helicity flux is computed in the evaluator's details but not asserted.
