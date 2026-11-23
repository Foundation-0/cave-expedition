# folds_dn_e8: outside checks of AUDIT-009 and AUDIT-017

These scripts check the F_n to D_n fold family, the nilpotent C_4 fold and the F_8 to E_8 fold from outside. They share no code with the verifiers in results/expedition-dn-e8-folds. They rebuild the curves from the written definitions and recompute the claims in exact arithmetic. None needs a clone of the target and none uses the network.

| Script | What it backs | Command | Runtime | Result line |
|---|---|---|---|---|
| check_dn.py | AUDIT-009: bars constant as symbolic identities, endpoints for n = 3 to 10 and nilpotent C_4 (det 4n, distinct cosets, kissing 2n(n-1)), Lemma 4 and 5 inequalities and Bernstein signs on 1,298,468 box pairs and 19,995 random pairs, Lemma 5 formulas as identities, exact search at 48 rational s, no overlaps | `python3 -I -B check_dn.py` | about 3 min | `RESULT check_dn: PASS (0 failed checks)` |
| check_e8.py | AUDIT-017: endpoint is sqrt 2 E_8 (shells 240, 2160, 6720, and 240 contacts per ball), all 32,640 degree-8 polynomials recomputed (0 negative Bernstein coefficients, 976 zeros), an exact search at 30 rational s, Gram determinants E_6 = 3, E_7 = 2, E_8 = 1 | `python3 -I -B check_e8.py` | about 3 min | `RESULT check_e8: PASS (0 failed checks)` |
| check_e8_loewner.py | AUDIT-017: the step G(s) >= G(1) re-derived by invariant planes and exact root isolation, not Bernstein coefficients | `python3 -I -B check_e8_loewner.py` | about 3 s | `RESULT check_e8_loewner: PASS (0 failed checks)` |
| recheck_folds.py | AUDIT-009 and 017, second pass: det L(1) = 4n for n = 3 to 12, Lemma 4 and 5 on 245,122 box pairs and 5,999 random pairs, Type-I census (2016, 864, 48), E_8 shells filtered to 240 and 2160, a numeric sweep at 41 values of s, Cartan determinants | `python3 -I -B recheck_folds.py` | about 2.5 min | `RESULT recheck_folds: PASS (0 failed checks)` |

common.py holds helpers for check_dn.py and check_e8.py. Each script exits 0 only if every check in it held.

Each one also carries must-fail controls: a perturbed input that the same code must refuse. A control that does not fail counts as a failed check.

The controls are a Hadamard matrix or a `C_n` matrix with one sign flipped (the endpoint determinant or Gram matrix is wrong, and a negative Bernstein coefficient appears), `s` = 11/10 just above the endpoint (an overlap appears, or the Loewner test goes negative), a wrong base point and a negated entry in the Loewner test. The result lines are unchanged.

Seeds are fixed and printed. Needs Python 3 and SymPy, plus numpy for recheck_folds.py. Tested with Python 3.14, SymPy 1.14 and numpy 2.5.

Each script was run under `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`. The three outputs were identical for every script.

## Target

The scripts were run against Foundation-0/incentre-lattices draft pull request 106, folder results/expedition-dn-e8-folds, at commit 33ff6da0c52b2fb3023ca06d200eab1bec32c0a3. The fold files themselves are at 6d577b5e221eda06e4ba0ea6cd553c91f7a0d758 in that branch. The scripts read nothing from the clone, so the commit fixes which definitions they were written against.

## Not covered

- The literature search and the labels for what is new. No script backs them.
- The wording defects (the "optimal 4D packing" phrase, "computer-free", "uniqueness" for Theorem 2). They are in the verdicts, not in the scripts.
- Overlap-freedom at irrational s and for n above 12. The proofs cover them. The scripts test sampled and exact rational s, and boxes.
- The Barnes-Wall and Leech results (AUDIT-020R), checked in another folder.
- Whether the team's own verifiers pass. That is not rerun here.
