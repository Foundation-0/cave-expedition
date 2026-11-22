# Results: does the ledger's "is an instance" criterion separate the listed domains from unrelated systems?

Short answer (sampled and exact, scope below): **No predicate extractable from the ledger's wording separates them.** Every Hermitian or quadratic predicate (P0, P1, P2, P4a, P4b, P5, P6, P8) is either a textbook theorem or a plain existence test, and the null panel of unrelated systems passes each at 100 percent of the cases where its hypothesis holds. The one place the criterion can fail is a singular pivot block, which a deliberately random indefinite family produces at 1.7 percent in one of two seeds; nothing in the ledger says the listed domains were tested for that or that it marks them apart. The README's eight are not even uniform under the criterion: one is tropical (no additive Schur complement exists) and one is a non-Hermitian Lindbladian (the inertia predicates cannot apply).

What this does not show: it does not show that the domains are unrelated, or that any listed claim is wrong. It shows that "an instance of the Schur-complement invariant" as the ledger words it has no discriminating power, so by itself it is not evidence of unity (Gate 5 item 4). The repaired forms S1 to S5 in PREDICATE.md are the next tests; they need the real objects.

## Panel (exact generation; sampled evaluation)

- Two independent panels, each 360 systems, 720 in total, sizes n = 2..12. Master seeds 20261121 and 11235813 (the second was not touched while building; fresh seed).
- Six families, each in a native and a scrambled-partition version, 30 per cell: random positive-definite rational (Gram plus identity); random indefinite symmetric rational; Kron-reduction Laplacians of random connected graphs; Gaussian covariance conditioning (Kac-Murdock-Szego type, random rational scales); least-squares normal equations with nuisance columns eliminated; random Hermitian over Q(i). Scrambled = the same matrix under a uniformly random index permutation, same pivot size.
- Size histogram, seed 20261121: 2:18, 3:36, 4:52, 5:32, 6:34, 7:22, 8:24, 9:42, 10:32, 11:34, 12:34. Seed 11235813: 2:46, 3:36, 4:30, 5:38, 6:44, 7:32, 8:26, 9:34, 10:24, 11:30, 12:20.
- Panel digests (SHA-256 over the matrix hashes): a68af6ba822448571f45e0dbfc9b38e4da1c760380d8aa4b2bbe963c0c1c2a6a and 5940596fed76fcb1eead943ce74f9184b36a5efa13bc7deae6783cda07f25f10.
- Every system also passes both inertia checkers (congruence elimination and Faddeev-LeVerrier plus Descartes) agreeing on every call; the pseudo-inverse passes all four Penrose equations on every pivot block. Zero identity defects in 720 systems.

## Pass rates on the null panel (sampled)

| predicate | what | seed 20261121: pass/all, pass/applicable | seed 11235813 (fresh): pass/all, pass/applicable |
|---|---|---|---|
| P0 | strict existence (A invertible) | 360/360 (100.00%), 360/360 | 354/360 (98.33%), 354/360 |
| P0g | generalized existence (pseudo-inverse, SF-01 wording) | 360/360 (100.00%), 360/360 | 360/360 (100.00%), 360/360 |
| P1 | Haynsworth inertia additivity | 360/360 (100.00%), 360/360 | 354/360 (98.33%), 354/354 |
| P1g | inertia additivity with generalized S | 360/360 (100.00%), 360/360 | 354/360 (98.33%), 354/360 |
| P2 | exact congruence V*MV = diag(A,S) | 360/360 (100.00%), 360/360 | 354/360 (98.33%), 354/354 |
| P3 | integer Bareiss sign rule | 289/360 (80.27%), 289/289 | 279/360 (77.50%), 279/279 |
| P4a | positive rescaling | 360/360 (100.00%), 360/360 | 354/360 (98.33%), 354/354 |
| P4b | block-diagonal congruence | 360/360 (100.00%), 360/360 | 354/360 (98.33%), 354/354 |
| P4c | mixing congruence (measured, not a theorem) | 310/360 (86.11%), 310/359 | 311/360 (86.38%), 311/351 |
| P5 | det M = det A det S | 360/360 (100.00%), 360/360 | 354/360 (98.33%), 354/354 |
| P6 | quotient property | 246/360 (68.33%), 246/246 | 250/360 (69.44%), 250/250 |
| P8 | Loewner monotonicity | 240/360 (66.66%), 240/240 | 240/360 (66.66%), 240/240 |


Reading the table:

- "pass/all" counts a system as failing when the predicate is not applicable. "pass/applicable" excludes systems where the hypothesis does not hold. P0 and P0g are the existence tests; P0g is 100 percent in both panels because a pseudo-inverse always exists.
- The 6 failures of P0 in seed 11235813 are all in `indefinite_symmetric` (3 of 30 in each of native and scrambled), where the pivot block was singular. The same 6 systems are the 6 where P1g fails, and they are exactly the 6 where the range condition `A A^+ B = B` fails (exact: generalized additivity held in all 714 systems where the range condition held, as the theorem says).
- P3 is undefined on 71 and 81 systems: all Laplacians (the full Laplacian is singular, so its last leading minor is zero) plus indefinite and Hermitian systems with an accidental zero leading minor. P6 needs k at least 2 and invertible nested pivots; P8 needs PSD with PD pivot block. These are applicability limits, not failures.
- P4c is a measurement. For positive definite systems the mixing congruence never changes `In(S)` (it is determined by `In(M)` and a positive definite `A`). For indefinite and Hermitian systems, `In(S)` changed in 49 of 359 and 40 of 351 defined cases, so the invariant belongs to the form together with its partition, not to the form alone. The ledger's "coordinate-free" wording holds only for partition-respecting transformations.
- Native vs scrambled partition: pass counts are the same within sampling noise for every theorem predicate (see `native_vs_scrambled_pass` in `results.json`). The criterion does not detect a scrambled partition.

## Must-fail controls (exact)

14 controls, each runs the checker on corrupted or out-of-scope input; none passed; script exit code 0.

singular 1x1 pivot refused (fired); singular 2x2 pivot fails P0 (fired); singular pivot not passed by P2 (fired); (min,+) system reported as having no additive Schur complement (fired); non-symmetric system refused for the inertia identity (fired); complex-symmetric but non-Hermitian system refused (fired); corrupted S breaks the congruence (fired) and the determinant identity (fired); sign-flipped S breaks inertia additivity (fired); pseudo-inverse S without the range condition fails P1g (fired); zero leading minor is not passed by P3 (fired); quotient property with singular A11 not passed (fired); Loewner comparison in the wrong direction fails (fired); the Descartes inertia checker disagrees with the congruence checker on a different matrix (fired).
`tropical_has_additive_schur` returns True only in the degenerate case where the cross terms are the semiring zero (checked once by hand: `[[1,None],[None,5]]` gives True, `[[1,5],[7,3]]` gives False), so the control is not constant.

## Which predicates each listed instance could satisfy in principle (anchor classification, not verified objects)

Counts (full table in `results.json`, `instances`):

| source | QH literal, Hermitian | QN literal, non-Hermitian | T tropical/polyhedral | N none visible |
|---|---|---|---|---|
| README s1 (8) | 6 | 1 (Lindblad Zeno) | 1 (coarse-graining) | 0 |
| Portal 10 table (8) | 6 | 1 (Lindblad Zeno) | 1 (tropical peeling) | 0 |
| SF-01 list (27) | 23 | 2 (GKSL Zeno, double-slit) | 0 | 2 (heedle, jacobian-lens) |

- QH can in principle satisfy P0, P0g, P1, P2, P3, P4a, P4b, P5, P6, and P8 if PSD; P1g only with the range condition. Two QH entries use Z[sqrt 2] or Q(sqrt 2) (Hadamard fold), where the inertia sign test lies outside the Q and Q(i) panel.
- QN can satisfy P0, P0g, P5, P6 only. The inertia identities need Hermitian input.
- T satisfies none: (min,+) has no additive inverses, and a tropical Schur complement `D - C A^-1 B` has neither the inverse nor the subtraction.
- N: nothing to test from the text read.
- Consequence: any predicate that holds for all QH instances (P1, P2, P4, P5, P6, P8) also holds for every unrelated QH-type system (the panel), and the predicates that hold for QN and QH alike (P0, P5, P6) hold for every matrix with an invertible block. A predicate that the tropical row could satisfy does not exist in this family.

## Reproduction (exact)

Runs under `/opt/homebrew/bin/python3.12` (plain python3 here is 3.14.6 and was not run). Three modes, each run for both scripts, run concurrently; exit code 0 each time; stderr empty. Outputs are identical across modes.

| script | mode | exit | SHA-256 of stdout |
|---|---|---|---|
| p_check.py | `-I -B` | 0 | 00c21561b92759e6799dd66283e6f662f0b125e9ccd39f3d59b7b45fd405e31a |
| p_check.py | `-I -O -B` | 0 | 00c21561b92759e6799dd66283e6f662f0b125e9ccd39f3d59b7b45fd405e31a |
| p_check.py | `-I -B -W error` | 0 | 00c21561b92759e6799dd66283e6f662f0b125e9ccd39f3d59b7b45fd405e31a |
| null_panel.py | `-I -B` | 0 | f35da609412363f5020cc269a838461a01b508fe151e7a56e8f3141947349c1b |
| null_panel.py | `-I -O -B` | 0 | f35da609412363f5020cc269a838461a01b508fe151e7a56e8f3141947349c1b |
| null_panel.py | `-I -B -W error` | 0 | f35da609412363f5020cc269a838461a01b508fe151e7a56e8f3141947349c1b |

`results.json` is the stdout of `p_check.py` (about 100 seconds). `null_panel.py` prints the panel log (seed, size, pivot size, permutation and a matrix hash per system) for seed 20261121; give another seed as its first argument.

Code rules: exact arithmetic on every decision path, no floats, no numpy; no bare assert; LF line endings; no absolute paths in any file; no `__pycache__` left behind.

## Limits

- The domain objects themselves were not built or run; the instance table classifies wording only. The sources were read at `pr1` (and `pr4` for the README and Portal 10 statements).
- The panel has no Q(sqrt 2), p-adic, symbolic-parameter or tropical-LP families beyond the tropical control.
- The null panel contains the textbook mechanisms that several domains are said to use (Kron reduction, conditioning, nuisance elimination). That is the point of the test, and also why a pass there says nothing about the domains' own claims.
- Panel 2 is a single fresh draw; the 1.7 percent singular-pivot rate is sampled, not exact.
