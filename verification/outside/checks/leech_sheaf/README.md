# leech_sheaf checks

These scripts re-check AUDIT-020R (Barnes-Wall and Leech realizations, arcs and the D_n obstruction) and AUDIT-019 (fold-sheaf rank-1 collapse) from an outside view. Each script is exact, has no network access, writes no files and prints one result line. It exits 0 only if every check in it held. Two passes wrote them: an evaluator, then an advocate who argued the repository's side.

The folder also holds three helper modules, `target.py`, `eval_common.py` and `eval_velocity_lib.py`. They are not checks. Scripts that read the target need the folder of a clone as the first argument, or in the environment variable `INCENTRE_LATTICES_PR106`. They read the target's witness tables as data and never run its code.

Run all commands from this folder. `CLONE` is the clone folder of PR 106 at the commit listed below.

| Script | What it backs | Command | Runtime | Result line (abridged, after `RESULT leech_sheaf/<script>: PASS`) |
|---|---|---|---|---|
| `eval_lattices.py` | Both lattices rebuilt from an independent Golay code: 4,320 and 196,560 minimal vectors, Leech by Conway's uniqueness, BW16 as a section of it, contact counts 137,280 and 9,432,672 | `python3 -I -B eval_lattices.py CLONE` | 25 s | BW16 4320 min vectors, Leech 196560 min vectors, Leech identified, contacts 137280 and 9432672 (14 checks) |
| `adv_lattice.py` | Same lattices rebuilt a second way, exact velocity of every contact, the natural Leech seed fails on 28 contacts | `python3 -I -B adv_lattice.py CLONE` | 50 s | BW16 4320 min vectors, 0 negative and 32 bar zeros of 137280, Leech 196560, target seed 0 negative and 48 bar zeros of 9432672, natural seed 28 negative |
| `eval_velocity.py` | Repaired gate is sufficient, velocities and Lemma B gates, the 28-contact failure of the natural Leech seed | `python3 -I -B eval_velocity.py CLONE` | 70 s | BW16 0 negative and 32 bar zeros of 137280, Leech target seed 0 negative and 48 bar zeros of 9432672, natural Leech seed 28 negative |
| `eval_bw16_arc_probe.py` | BW16 arc beyond the certified radius: separated at tau 1/30, overlaps at 1/10, so 1/4000 is conservative | `python3 -I -B eval_bw16_arc_probe.py CLONE` | 30 s | arc separated at tau 1/4000 and 1/30, overlaps at 1/10 (min excess 8.258e-05, 0.005485, -0.011) |
| `eval_leech_arc_probe.py` | Leech arc must be checked exactly: float distances at tau 1e-10 are negative, exact ones positive | `python3 -I -B eval_leech_arc_probe.py CLONE` | 30 s | all 12 worst contacts positive in exact arithmetic (min 3.58e-10), 12 negative in float (min -7.75e-09) |
| `adv_arc.py` | Sentence to repair "positive symmetric part of I + A implies det > 1" (counterexample I/2), repaired step holds, all non-bar contacts open strictly | `python3 -I -B adv_arc.py CLONE` | 95 s | literal det step fails (I/2 has det 1/8), repaired step holds on BW16 and Leech arcs, 960 motif and 32 bar contacts at exactly 2, 137248 others strictly above |
| `adv_obstruction.py` | Theorem 1 holds and is elementary: D_16 roots are connected, E_8 + E_8 roots are not | `python3 -I -B adv_obstruction.py` | 1 s | D16 roots form 1 component of 480 (rank 16), E8+E8 roots form 2 components of 240 |
| `eval_sheaf.py` | AUDIT-019 by a different route: rank 1 for C_3 to C_6 and C4_nilp at k = 1, 2, 3, rank n at s = 0, rank 0 control, E_8 path rank 1, virial formula, A(D_n) = 2/(n-2) | `python3 -I -B eval_sheaf.py` | 30 s | rank 1 for C3 to C6 and C4_nilp at k=1,2,3 and s=1, rank n at s=0, rank 0 for the control, rank 1 on the E8 path (25 cases) |
| `adv_sheaf.py` | AUDIT-019 from scratch: rank S = virial span = diagonal symmetrizers, Lubensky 2015 eq. A4 equals the Schur complement | `python3 -I -B adv_sheaf.py` | 10 s | 18 cases, ranks agree (1 for twisted cycles, C4_nilp and H8, 0 for the control, 2 for two blocks), A4 equals the Schur complement |

Each script gave identical output under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`. The numbers match VERDICTS.md and the reports. Runtimes are wall-clock on one laptop while other jobs ran.

## Targets

- Foundation-0/incentre-lattices draft PR 106, head `33ff6da0c52b2fb3023ca06d200eab1bec32c0a3` (the lattice scripts read its `verify_bw16_leech24.py` tables).
- Foundation-0/incentre-lattices draft PR 107, head `edc795b0073d660576649937af0e6174ac2e229a`. The sheaf scripts build their frameworks from scratch and read nothing from it. Both heads were checked out and are the commits the original runs used.

Tested with Python 3.14, NumPy 2.5 and SymPy 1.14.

## Not covered

- The repository's own verifiers, certificates and controls are not rerun here.
- The AUDIT-019 script `fold_sheaf_collapse.py` is not wrapped.
- The proof text is read by people, not by these scripts. The wording repairs in VERDICTS.md section 3 are backed only where a number or counterexample is listed above.
- The prior-art readings (Kallus and Torquato, Borcea and Streinu, Lubensky, Norris) are not scripted.
- E_8 interior points over Q(sqrt 2) are checked only for rank and the virial identity, not for inertia.
- The arcs are local. No global fold for Leech is checked.
