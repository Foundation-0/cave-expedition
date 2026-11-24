# Law 2b applied to the gate5 unification rulings

This part re-reads the rulings of this package against the owner's rule "Law 2b". The rule says a formula may not be closed as false until a fixed set of transformations has been searched for one under which it holds.

Two checkers did the work, and they share no code. `src/law2b_check.py` is the first. The scripts in `clean_room/src/` are the second, written by a worker who had not read the first. Everything below is exact arithmetic (`int` and `Fraction`) unless it says "sampled".

Result in short. The sentence in README section 1 is false for row 6 and the rule certifies that (G5-17). For row 4 the elimination step has an exact transformed form (G5-18). The inertia clause of row 4 gets neither certificate, and the reason is stated in section 6 (G5-19).

The two exact repairs found are true of nearly any system of the same shape, so they give no link between fields (G5-20).

## 1. What Law 2b requires

The specification is in Foundation-0/cave-expedition on PR #1, head `80606f1`, file `symbiosis/round10/arm5-transformational-steelman/TRANSFORMATIONAL_STEELMAN_REPORT.md`. Those files are not in this repository.

- Lines 32 to 44 list seven families of global transformations, T1 to T7: gauge or similarity, affine or Bregman shift, metric chart, spectral or PSD shift, semiring or tropicalization, subspace or quotient or dual projection, order chart with a domain split.
- The identifiers of the seven families in the reference specification at that commit are T1_GAUGE_SIMILARITY, T2_AFFINE_BREGMAN, T3_METRIC_CHART, T4_SPECTRAL_PSD_SHIFT, T5_SEMIRING_TROPICAL, T6_SUBSPACE_PROJECTION and T7_ORDER_DOMAIN_RESIDUAL. This report writes them as T1 to T7, and `specs/specs.json` uses the full identifiers. The method's later code uses the same identifiers.
  No other commit of the reference was read.
- Lines 46 to 53 give four guards. G1: the transformation must not pass nearly everything (null false-pass rate at most 1/10, with enough nulls to resolve that rate). G2: free parameters fewer than constraints, fixed before the held-out data. G3: an explicit ledger of what the claim becomes, with zero gap for "transformed-exact".
  G4: a falsification needs all seven families searched and an invariant obstruction.
- Lines 95 to 99 (protocol) say the transformation and its parameter budget are fixed globally first, and a final falsified verdict needs the certificate of G4 (line 104).

Outcome names used here: transformed-exact (a transformation holds, with its ledger), invariant-falsified (an obstruction survives every family) and search incomplete (neither). Where the specification's terms are defined for statistical claims, the analogues used for exact algebra are our readings. They are listed in section 8.

## 2. The claims searched

Only G5-14 had verdict FALSIFIED. These are the rulings that close a claim by saying it fails.

| id | claim closed | outcome |
|---|---|---|
| G5-14, G5-02 row 6 | Sylvester inertia is additive for the Liouvillian (17 points) | invariant-falsified |
| G5-02 row 4, elimination | the (min,+) object has an additive Schur complement | transformed-exact on a stated domain |
| G5-02 row 4, inertia | the row 4 object satisfies the inertia statement | neither certificate |
| G5-04 | rows 1, 5 and 6 are partition-respecting equivalent | invariant-falsified |
| G5-05, second sentence | zero commuting defect singles out Phi | stands, repair rejected by G1 and G2 |
| G5-06, converse | rank 1 collapse holds iff the symmetrizer is unique | stands, rank formula holds |
| G5-06, basis change | the collapse survives a change of basis | carried change is transformed-exact |
| G5-01, pseudo-inverse | inertia adds with the pseudo-inverse for every matrix | sufficient condition, not necessary |

Where each statement is recorded is listed in section 10.

Not searched, with the reason. G5-01 (rest) and G5-08 say a predicate is true of every system, and no transformation repairs that. G5-03 is a fact about a text. G5-15, G5-09, G5-11 and G5-12 are positive. G5-16 is NOT_SHOWN. G5-07, G5-10 and G5-13 were not closed.

## 3. The search, ruling by ruling

Coverage labels. CLASS: the whole family as the specification writes it was proved or enumerated. REDUCTION: the family reduces to another searched family. INSTANCES: only listed cases. NO INSTANCE: no admissible instance, with the reason.

### 3.1 Row 6, the Liouvillian (G5-14, G5-02)

Claim. For each of 17 points M (16 by 16, rational) is Hermitian, the pivot block A (indices 8 to 15) is invertible, and In(M) = In(A) + In(S) with S = D - C A^-1 B.

Literal failure. M is not symmetric at 17 of 17 points. The coupling C equals -B^T with B non-zero at 17 of 17. At the 15 points with omega = 0 every non-zero coupling entry is +-2g, so the coupling is linear in g. M - M^T has rank 8, or 12 where omega is not zero. In(sym M) = (0,12,4), In(A) = (0,8,0), and the symmetric part of S(M) has inertia (0,6,2). The sum (0,14,2) is not (0,12,4).

Seven families.

- T1, CLASS for diagonal D, block-diagonal P (any complex invertible blocks) and congruence. For a coupled pair the product M_ij M_ji is unchanged by a diagonal D and is negative at every coupled pair (68 pairs over the 17 points). A Hermitian matrix needs it to be at least 0.
- T1, block-diagonal P. For C = -B* the Hermitian condition becomes -B* Gr = Gp B*, with Gr = Pr Pr* and Gp = Pp Pp* positive definite. Multiply by B and take traces. The left side is at most 0 and the right side at least 0, so both are 0 and B = 0. That contradicts B non-zero. The second checker followed every step and found no gap.
- T1, congruence. rank(M - M*) is unchanged by P* M P, and it is 8 or 12.
- T1, general P. M is similar to a real symmetric matrix exactly when it is diagonalizable with real spectrum. All 17 points are diagonalizable. 10 have real spectrum and 7 have 8 non-real eigenvalues. Where P exists it is not block-diagonal, so S is not carried along. This is not admissible for an elimination claim.
- T2, CLASS. Adding a symmetric G (the Hessian of a convex function) or shifting coordinates leaves M - M^T unchanged. The form x^T M x sees only sym(M), and S(sym M) = sym(D) at 17 of 17, so the variational Schur complement is not S(M). The coupling cancels in the form.
- T3, REDUCTION. A chart keeps a linear operator linear only if it is linear, which is T1 or a congruence.
- T4, CLASS. For c M + lambda I with c and lambda complex, M is Hermitian only if Re c = 0 and sym(M) is scalar. sym(M) is not scalar at 17 of 17. The exact real-linear system for (Re c, Im c, Im lambda) has only the zero solution.
- T5, NO INSTANCE. M has no Laurent parameter. The entries +3 and -3 have the same valuation, so a tropical image erases the sign pattern that is the failure.
- T6, CLASS. A compression to V = Vr + Vp is Hermitian only if the compressed coupling is zero, and then its Schur complement is the compressed D. All 65,025 partition-respecting coordinate subsets at the first point were enumerated by both checkers. 20,225 are Hermitian and every one is decoupled.
- T7, CLASS in g. At the omega = 0 points M is Hermitian only at g = 0, where S = D.

The one exact repair. Replace Sylvester inertia of the form by spectral inertia of the operator: count eigenvalues by the sign of their real part. M, A and S are all dissipative (negative semidefinite symmetric part) at 17 of 17 points. For a dissipative matrix the eigenvalues on the imaginary axis lie in the kernel of the symmetric part and are semisimple.
The first checker counted them as the largest invariant subspace inside that kernel. The second used the gcd of p(x) and p(-x) and a Cauchy index. Both give In_spec(M) = In_spec(A) + In_spec(S) = (0,14,2) at 17 of 17.

Guards for the repair. G2 passes (0 free parameters, 17 constraints). G3 ledger: the preserved core is that eigenvalues counted by the sign of their real part add over the Schur split. The modified hypotheses are that the form's inertia is replaced by the operator's spectral inertia and that the symmetric part is negative semidefinite. G1 fails, and the rate depends on the panel (section 5).

Outcome. Invariant-falsified for the Hermitian-form claim. The obstruction is the antisymmetric coupling C = -B^T with B non-zero. T1 (diagonal, block-diagonal, congruence), T2, T4 and T6 keep it or reduce to a decoupled system. T3 reduces to T1. T5 has no instance. T7 leaves only g = 0. The one exact repair is vacuous under G1. Two readings carry this.
T1's operator form is diagonal or block-diagonal, and a repair rejected by G1 does not block a falsification.

### 3.2 Row 4, the elimination clause (G5-02, G5-18)

Object. `tropical/objects/cole_hopf.json`: K over Q[q], 32 states, 89 entries, and the Doob-peeled K'. The (min,+) semiring has no negation, so D - C A^-1 B has no meaning for the (min,+) object as worded. K has 9 one-way edges (10,0), (12,2), (14,4), (18,8), (20,10), (22,12), (26,16), (28,18), (30,20). At each one-way pair B = {i,j} the block K_BB is non-zero and nilpotent.

- T1, instance. The Doob gauge D^-1 K D with D = diag(q^d*) reproduces the stored peeled matrix at all 89 entries.
- T2, REDUCTION. The tower objective is polyhedral, so its Hessian is zero almost everywhere.
- T3, REDUCTION to T5. The log chart q = exp(-1/eps) is the valuation.
- T4, instance. I - K is the object itself.
- T5, CLASS on non-negative coefficients with val(K_BB) >= 1. The valuation of the Schur complement equals the (min,+) Kleene-star elimination on 528 of 528 blocks of K (sizes 1 and 2) and on 479 of 479 in-hypothesis blocks of K'. The 49 blocks of K' outside the hypothesis also match on these matrices (second checker).
- T6, instance. The tower sums to 124 and H_total equals d*, as the package says.
- T7, domain split. Outside non-negative coefficients the bridge is an inequality. K_00 = -q^2, K_01 = K_10 = q, K_11 = 0 satisfies val(K_BB) >= 1 and is a cancellation witness: val(S_00) is infinite against a tropical value of 2. The witness outside the hypothesis val(K_BB) >= 1 is K_22 = 1 - q, K_02 = K_21 = q, where val(S_01) = 1 against 2.

Guards. G1 uses random non-decreasing exponent maps in place of the valuation as the null. 2 of 40 commute with elimination, and f(e) = c e commutes for c = 1, 2, 3. G2: 0 free parameters, 528 constraints. G3 ledger: the object is the Q[q] lift of the (min,+) matrix with non-negative coefficients, the inverse becomes a Kleene star, and the inertia statement is not part of the claim.
Gap 0 on the domain.

Outcome. Transformed-exact (T5) on that domain. The ruling that no additive Schur complement exists for the (min,+) object itself stays true as worded.

### 3.3 Row 4, the inertia clause (G5-19)

Seven families.

- T1, diagonal gauge: CLASS. A diagonal D keeps the support, so the 9 one-way edges stay.
- T1, block-diagonal P: decided at fixed q only, in section 6.
- T1, general P: at q = 1/10, 1/100 and 1/1000 the matrix K(q) has 32 distinct real eigenvalues, so some non-block-diagonal P symmetrizes it. At q = 1/2 only 24 of the 32 are real, and no real P of any shape exists.
- T2, CLASS. Symmetric additive shifts leave the skew part unchanged.
- T3, REDUCTION to T5.
- T4, CLASS. Complex affine maps cannot make a non-symmetric matrix with this support symmetric.
- T5, NO INSTANCE for inertia, because (min,+) has no negation.
- T6 and T7, CLASS. A compression to a symmetric sub-support gives a Hermitian system with I - K positive definite, so every inertia is (size, 0, 0).

The only exact inertia statement that survives is spectral inertia of I - K. At q = 1/100 the matrices I - K, I - K_BB and I - K_eff are strictly row-diagonally dominant on 528 of 528 blocks, so every spectrum has positive real part. 40 of 40 random supports behave the same, so G1 rejects it as vacuous.

Outcome. Neither certificate applies. It is not invariant-falsified, because block-diagonal symmetrizations exist for some singleton blocks. It is not transformed-exact, because where a symmetric form exists the matrix is positive definite and the inertia statement is true of any such system. Section 6 has the exact record.

### 3.4 Rows 1, 5 and 6 are not equivalent (G5-04)

Claim. For the 168 pairs (12 spectral-inertia points, 14 AeST points) there is a partition-respecting congruence class: the same dimension, the same In(A) and In(S), and the same square class of det A and det S over Q.

Literal failure. 0 of 168 pairs agree. 108 fail on the inertia of the reduced block, which reproduces the package. 60 more fail on the square class of det A. Counted separately, all 168 fail on the square class of det A and all 168 on det S, and none fails on the inertia of A.
The package's counts of 59 and 1 use norm classes over Q(i), a different class group from the square classes over Q used here. Row 6 is 16 by 16 and not symmetric, and rows 1 and 5 are 3 by 3 and symmetric.

- T1, CLASS. Partition-respecting congruence keeps (In A, In S): 156 of 156 random cases at the first checker. For symmetric objects spectral inertia equals Sylvester inertia, so similarity adds nothing.
- T2, CLASS. Additive linear terms leave the Hessian unchanged.
- T3, REDUCTION. A linear chart is a congruence.
- T4, CLASS. A global shift M + 871 I makes all 38 objects of rows 1 and 5 positive definite, so 168 of 168 pairs then agree, and so do 10 of 10 random pairs at the first checker and 200 of 200 at the second. Vacuous.
- T4, scope. The value 871 is a bound for rows 1 and 5 only. The row 6 matrices have row sums up to about 5,003, and sym(M) + 871 I is positive definite at only 15 of their 17 points.
- T5, NO INSTANCE. The objects are real symmetric with no Laurent parameter.
- T6, CLASS. Comparing only the 2 by 2 pivot blocks: 168 of 168 pairs agree and so do 60 of 60 random positive definite pairs. Vacuous, because the Schur block and the coupling are dropped.
- T7. The set of pairs whose inertia agrees has 60 pairs and is defined by the outcome, so it is post hoc. A per-pair unit rescale matches 0 pairs.

Outcome. Invariant-falsified. The obstruction is the dimension and the pair (In A, In S). Congruences, linear charts and linear terms keep it. The maps that change it, the global shift and the compressions, are vacuous under G1.

### 3.5 The lattice pair (G5-05, G5-06)

Both checkers built the pair from `lattice/SPEC.md` sections 1 and 2. The identities R_el = R_lat Phi, H_el = Phi^T H_lat Phi and S_el = R_L^T S_lat R_L hold at n = 3 and 4. The first checker also ran n = 8 for E8 and D8 at s = 1 (rank 1, inertia (1,0,35), traces 114/23 and 23/4).

- Converse. L = diag(3,2,2) has rank S_el = 1 and dim Z_B = 3. The transformed statement that holds is the rank formula of G5-07, on 26 lattices at n = 3 and 4 and on the 1,725 instances behind G5-07. Family T6.
- Basis change. A plain change L -> U L keeps the collapse in 0 of 16 cases. A carried change, which keeps every bar vector (translations m' = m U^-1), leaves S_el unchanged and gives S_lat' = (U^-1 x I)^T S_lat (U^-1 x I) in 16 of 16. Family T1. G2: 0 free parameters, 16 constraints. G1: the null is the plain change, 0 of 16 pass.
- Commuting test. At n = 3, 12 of 12 random block-upper-triangular maps give zero defect, 0 of 12 dense maps do, and 0 of 12 satisfy R_el = R_lat Phi. The repaired statement (block-upper-triangular class, T6) is exact. G1 fails (12 of 12 nulls pass) and G2 fails (162 free entries against 21 independent constraints). The ruling stands.

The proviso in G5-06 that the intra-cell framework has only rigid motions is removed for every n >= 3. The flex classification in Theorem B's proof shows it, and at n = 2 an extra flex exists. The basis is exact tests on instances plus a step-by-step reading of the proof. It is not machine-checked.

### 3.6 Pseudo-inverse additivity (G5-01)

If the range condition A A^+ B = B holds, M is congruent to diag(A, S) and the inertia adds. The condition is therefore sufficient. It is not necessary. Three exact witnesses with symmetric M = [[A,B],[B^T,D]]:

- A = [[-1,-1],[-1,-1]], B = [-1,-1]^T, D = [-1]. The condition holds and In(M) = (0,1,2) = (0,1,1) + (0,0,1).
- A = [0], B = [1], D = [0]. The condition fails and In(M) = (1,1,0) is not (0,0,2).
- A = [0], B = [[1,0]], D = [[0,1],[1,0]]. The condition fails and the inertia still adds: (1,1,1) = (0,0,1) + (1,1,0).

Exhaustive searches with entries in {-1, 0, 1}: the condition held in 75 and 27 of 243 systems with additivity in all of them, and failed in 168 and 216 with additivity in 0 and 32. The first checker's panel of 300 random systems gave 158 with the condition, all additive, and 3 of 142 additive without it.

### 3.7 The team's three morphisms

- M1 (AUDIT-017 and 019): an exact statement. Family T1 (block congruence Phi^T H Phi) with the Schur step a T6 quotient. 0 free parameters. The identity R_el = R_lat Phi identifies Phi. The commuting test does not.
- M2 (AUDIT-064 and 079R): one Gram matrix at one point with chosen tangents, not a map between two objects. W^T diag(1/p) W = diag(9/4, 49/2, 0) at p = (1/2,1/4,1/4) is exact. The tangents are chosen, with six free parameters against three off-diagonal constraints, so G2 would flag it. No Schur complement is computed. Family T3.
- M3 (Q[q] and (min,+)): an exact statement. Family T5, with the Doob gauge (T1) inside. Domain: val(K_BB) >= 1 (G5-10, G5-13).

## 4. The guards, with numbers

Fields are our analogues for algebraic claims. dof counts free parameters. Constraints are the independent equations the transformed claim must meet. Target counts instances that pass. Null counts matched random systems that pass, and must stay at or below 1/10. Specifications are in `specs/specs.json`, the team certifier's answers in `specs/certifier_answers.json`.

| spec | proposed | dof | constraints | target | null | certifier | first checker's guards |
|---|---|---|---|---|---|---|---|
| R1a row 4 elimination, T5 | transformed-exact | 0 | 528 | 528/528 | 2/40 | certified | admit |
| R1b row 4 inertia | invariant-falsified | 0 | 528 | 0/528 | 0/40 | rejected, G4 | reject |
| R2 row 6 Hermitian inertia | invariant-falsified | 0 | 17 | 0/17 | 0/60 | certified | admit |
| R2x row 6 spectral inertia, T1 | transformed-exact | 0 | 17 | 17/17 | 56/58 | rejected, G1 | reject |
| R3 equivalence | invariant-falsified | 0 | 168 | 0/168 | 0/156 | certified | admit |
| R3x global shift, T4 | transformed-exact | 1 | 168 | 168/168 | 10/10 | rejected, G1 | reject |
| R3y pivot only, T6 | transformed-exact | 0 | 168 | 168/168 | 60/60 | rejected, G1 | reject |
| R4a carried basis change, T1 | transformed-exact | 0 | 16 | 16/16 | 0/16 | certified | admit |
| R5 block-upper class, T6 | transformed-exact | 162 | 21 | 12/12 | 12/12 | rejected, G1 and G2 | reject |

For the invariant-falsified specs the null column counts Hermitian or congruent systems on which the obstruction invariant fires wrongly (0 of 60 and 0 of 156). The certifier refuses a falsified spec with zero gap, so the gap field holds a measured failure size.
R1b is fed as if falsified with the obstruction marked as not surviving, and the certifier rejects it, which is the point: that claim is not certified.

## 5. The null panel for the row 6 repair depends on the panel

The rate at which random systems pass the spectral-inertia repair depends on how the nulls are drawn. The first checker drew 58 sparse random systems with independent coupling and 56 passed. The second drew 180 systems in three panels and got 137 of 180 pooled.
Dense independent coupling gave 77 of 120, falling as the coupling grows (14 of 15, 13 of 15, 4 of 15, 4 of 15 and 15 of 15, 13 of 15, 8 of 15, 6 of 15 at scales 1/4, 1/2, 1 and 2). Row 6's own support pattern with independent values gave 60 of 60.

The first checker's dense panel, added after the comparison: 48 of 60 (dense independent coupling, 15 systems at each of four coupling scales).

Every reading is far above the cap of 1/10, so the verdict does not move. The rate does, and nothing in the specification says which panel is the matched null.

## 6. Row 4 inertia clause: what is shown about block-diagonal symmetrization

Question. Is there a block-diagonal invertible P with P^-1 (I - K) P real symmetric, for a partition of the 32 states into B and its complement? Equivalent form: a positive definite block-diagonal G with K G = G K^T. K is taken at fixed rational q.

Method. W = {X symmetric : K X = X K^T} is a linear space of dimension 32 at each q (K has 32 distinct real eigenvalues). The block-diagonal members are those with X_AB = 0. Both checkers solved this exactly. The second screened by rank modulo a prime, and the first restricted a verified basis of W.
Each solution was checked exactly to be block diagonal with K G symmetric, and positive definiteness was tested by exact elimination.

Result at q = 1/10, 1/100 and 1/1000, blocks B of size 1 and 2 (528 partitions):

- No fully diagonal G (gauge similarity): the solution space is {0} at all three q.
- For 480 of 528 partitions the solution space is {0}, so no P exists.
- The 9 pairs that contain a one-way edge have no P at any q. K_BB = [[0,k],[0,0]] forces a zero diagonal entry in G_B.
- The 16 antipodal pairs have a one-dimensional solution, indefinite with inertia (16,16,0), so no P.
- Singletons: a positive definite solution exists for 8 of 32 at q = 1/10 and for 18 of 32 at q = 1/100 and 1/1000. For the others the one-dimensional solution is indefinite.
- Unrestricted P exists at these q. At q = 1/2 no real P of any shape exists, because the spectrum has non-real eigenvalues.

Check of the second checker's argument. I reran `clean_room/src/r4b.py` in the sandbox in the three modes. It exits 0, the output is identical in all three, and its SHA-256 equals the recorded one.
Then I redid the question with my own code (`src/law2b_check.py`, section claim18), which gets W by its own sparse elimination, screens each partition by rank modulo a prime and solves the survivors exactly.
It gives the same counts at all three q: 480 of 528 partitions with solution space {0}, the same 16 indefinite antipodal pairs, the same lists of positive definite singletons (8 at q = 1/10 and 18 at q = 1/100 and 1/1000), and no positive definite solution for any of the 9 one-way pairs.
The singleton lists are {0, 7, 13, 14, 16, 19, 25, 30} at q = 1/10 and {0, 2, 3, 7, 9, 10, 13, 14, 15, 16, 17, 19, 20, 23, 25, 28, 29, 30} at q = 1/100 and 1/1000. For the one-way pairs I used the necessary condition alone: the (B,B) block of K G must be symmetric, and for K_BB = [[0,k],[0,0]] that forces a zero diagonal entry in G_B. I checked this for all 9 pairs at each q.
For every positive definite singleton the solution was verified exactly to be block diagonal with K G symmetric, including B = {0} and B = {30} at q = 1/10. I found no disagreement with the second checker on claim 18.

Decision. Where a block-diagonal P exists, I - K is positive definite, so every inertia is (size, 0, 0) and the inertia statement is true of any such system (G1). Where no P exists, the obstruction is real. Both happen, so no single obstruction survives and no non-vacuous transformed form exists.
In the rule's vocabulary neither certificate applies: invariant-falsified fails because some blocks do symmetrize, and transformed-exact fails because the statement is vacuous where it holds.

Not decided: symbolic q, blocks of size 3 or more, and P that depends on q beyond these three values.

## 7. Where the two checkers agree, and the three places they differed

The second checker reproduced 22 of 25 numbered claims, including every row 6 number, the trace proof step by step, the 65,025-subset enumeration, the spectral inertia by a different method, the 528 of 528 valuation result, 0 of 168 pairs, the lattice results and the team certifier's behaviour. Three differed.

1. Null rate for the row 6 repair. First 56 of 58, second 137 of 180 pooled. Resolution: the rate depends on the panel (section 5). The conclusion holds under every reading, so both are recorded.
2. Label of a witness. The first checker called K_00 = -q^2, K_01 = K_10 = q, K_11 = 0 "outside the hypothesis". It satisfies val(K_BB) >= 1, so it is not. It is a cancellation witness, and it violates non-negative coefficients. The witness outside the hypothesis is K_22 = 1 - q, K_02 = K_21 = q. Resolution: the second checker is right. The labels are fixed in this part and in G5-18.
3. Scope of lambda = 871. It is a bound for rows 1 and 5 only. Resolution: the second checker is right. The scope is stated in section 3.4 and in G5-04.

Two additions from the second checker were adopted. All 17 row 6 matrices are diagonalizable (10 with real spectrum, 7 with 8 non-real eigenvalues). All 168 pairs fail on the square class of both det A and det S.

## 8. Limits

- Several terms of the rule are defined for statistical claims, and our analogues for exact algebra are readings. Line numbers refer to `TRANSFORMATIONAL_STEELMAN_REPORT.md` at `80606f1`. Line 38: T1 is titled "Conjugacy" but its operator form is `D^-1 M D`, so we searched diagonal and block-diagonal P and reported general P separately. Lines 39 and 40:
  T2 and T3 are written for divergences and charts on simplices, so we used symmetric additive shifts and linear charts. Line 41: T4 is `A + lambda I`, and we allowed complex c and lambda. Line 42: T5 needs a Laurent parameter. Line 43: T6 lists "P_V, 1 - pi, or paired principal stratum", and we used partition-respecting compressions and the symmetric-part projection.
- Line 50 (G1): the null false-pass rate assumes a measured null. We used matched random systems of the same size and ring, or random exponent maps for a morphism. The resolution test uses the cap, not the actual rate. Line 51 (G2): what counts as a constraint for an algebraic claim is not defined, so we counted independent equations.
  Line 52 (G3): nothing says what a gap means for a falsified claim, so we used a measured failure size, because the certifier refuses zero. Line 53 (G4): `obstruction_survives_all_searched` is a flag the caller sets. We set it when each family has no instance, reduces to another, keeps the obstruction, or offers only a repair that G1 rejects.
  Lines 95 to 99: "fixed globally before holdout" has no meaning in an after-the-fact audit. Our transformations are fixed by their definitions.
- The null panels are our choice, and the rates depend on them (section 5). A different matched null could change a G1 verdict.
- The team's certifier checks numbers and schema. It admits an invented witness string and an obstruction string it cannot read, and refuses a falsified spec with zero gap. So "certified" here rests on the arithmetic of the two checkers.
- The team's standalone verifier passes (5 of 5 arms in three modes) but cannot run its live anchor check, because the anchored files are not in the repository. The arm 5 test returns early when they are missing.
- The team's specification and certifier are on PR #1, not in this repository. `run_law2b.sh` takes the certifier path as an argument.
- No prior-art search was done. Novelty is N0 for everything here.
- Not run: row 4 at symbolic q and for blocks of size 3 or more. Rows 2 and 8 as objects.
- Not run: the package's n = 8 counts for G5-05 and G5-06 beyond the first checker's two instances, and the team's Theorem B proof beyond the independent reading already recorded.
- Not run: M2's tangent vectors beyond the numeric matrix, Hasse invariants (square classes were used), Liouvillian parameters beyond the 17 points, and charts for T3 beyond the reduction argument.

## 9. The team's verifier and certifier, as run

Both ran at `80606f1` with Python 3.12.15 in the sandbox (no network, writes only to the output folder). The recorded outputs are in `out/team_verifier/` and `out/team_arm5/`.

- The standalone verifier (`verification/checks/verify_round10_standalone.py --json`) exits 0 in `-I -B`, `-I -O -B` and `-I -B -W error`, with the same stdout (SHA-256 `0567dddc10e7a86692c398bdc4c62653f3a526ef4a59efc2f441a39658402fcb`) and empty stderr. It prints PASS for 5 of 5 arms. Files `out/team_verifier/mode{1,2,3}.{stdout,stderr,rc}`.
- Arm 5 run directly: the certifier with `--standalone --json` exits 0 with stdout hash `54d07116cf2d9ece84c4217083ce29c4c404f668d3905ded33eafc97573870ef` in all three modes (`out/team_arm5/cert{1,2,3}.*`). The test file runs 12 tests, OK, in all three (`test{1,2,3}.*`).
  Without `--standalone` the certifier exits 1 in all three modes because the 8 anchored files are missing (`live{1,2,3}.*`, `all_anchors_matched` is false).
- The test `test_live_vault_if_present` returns at once when the anchored folder is absent. This is read from the test file at `80606f1` (lines 616 to 619). It is not an output of this package.
- The certifier's answers to our nine specifications are in `specs/certifier_answers.json`, with the specifications in `specs/specs.json`. The answers are identical in three modes (`out/feed.mode{1,2,3}.out`).

## 10. A fault found and fixed, and where each statement is recorded

An intermediate run of the first checker exited 1. The cause was a new count of failures of the square class of det S: one AeST point has reduced Schur complement 0, so a ratio divided by zero. It was a fault in that count, not a disagreement between the checkers or with a ruling. It was fixed (zero is equal only to zero) before the recorded run, and the failing output was overwritten.

- Sections 3.1 to 3.7 and 4, first checker: `out/law2b_check.mode1.out` (JSON, keys `numbers`, `specs`, `controls`, `checks`).
- Sections 3.1 to 3.7, second checker: `clean_room/out/{r6,r4,r4b,r156,lat,oth,cert}.mode1.out`, and its report `clean_room/REPORT.md`.
- Section 6: `clean_room/out/r4b.mode1.out` and the `claim18` part of `out/law2b_check.mode1.out`.
- Hashes and run times of every run in three modes: `out/hashes.txt` and `clean_room/out/hashes.txt`.
- The G5-06 proviso: `second/out/c5_thmB.txt` and the step-by-step reading in the independent reader's report, which is not part of this package.

## 11. Rerun

`sh run_law2b.sh <path to transformational_steelman_certifier.py>` from this folder runs both checkers in three modes in the sandbox and writes `out/hashes.txt` and `clean_room/out/hashes.txt`. Without the argument the certifier steps are skipped. The README of the package lists the expected hashes and the run times recorded from inside a fresh clone.
