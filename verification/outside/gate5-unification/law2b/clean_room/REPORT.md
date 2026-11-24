Text of the second (clean-room) checker's report, kept for the record. Style and paths were edited on 2026-11-22 (relative paths, periods in place of semicolons, shorter lines, the table turned into a list). The numbers and claims are untouched. The numbered claims are the 25 claims of the first checker's report. Its first lines say it did not read the first checker's code or outputs.

# Second (clean-room) check of the Law 2b package results

Folder: `law2b/clean_room/` (`src/` the scripts, `out/` the outputs). The package was read at branch outside/gate5-unification, commit b0434fa. I did not read the first worker's `law2b/src` or `law2b/out`. Python 3.12 stdlib, Fractions and ints only, no floats on any decision path, no bare assert.

Convention for row 6: M = [[D, B'],[C, A]], D = M[0:8,0:8], B' = M[0:8,8:16], C = M[8:16,0:8], A = M[8:16,8:16] (pivot block = indices 8..15, the package's own pivot_indices). S = D - B' A^-1 C. "A has inertia" means the symmetric part of A (A is symmetric at all 17 points anyway for omega=0. Checked via sym part throughout).

## 1. Table

- Claim 1. First worker: not symmetric 17/17. C=-B^T 17/17. Every nonzero coupling entry +-2g at the 15 omega=0 points. Second checker: 17/17, 17/17, 15/15 (also +-2g at all 17). Verdict: reproduced. Method: direct entry tests.
- Claim 2. First worker: rank(M-M^T) 8 / 12. Second checker: 8 at the 15 omega=0 points, 12 at the other 2. Verdict: reproduced. Method: exact rank.
- Claim 3. First worker: sym(M) (0,12,4) all 17. A (0,8,0). Sym(S) (0,6,2). Sum (0,14,2) differs. Second checker: same, 17/17. Verdict: reproduced. Method: symmetric elimination, cross-checked by charpoly + Descartes (real-rooted).
- Claim 4. First worker: Schur(sym M) = sym(D) 17/17. Second checker: 17/17. Verdict: reproduced. Method: exact Schur.
- Claim 5. First worker: M_ij M_ji < 0 on every coupled pair. Second checker: 68 coupled pairs (summed over 17 points), 0 violations (both entries nonzero and product negative). Verdict: reproduced. Method: enumeration.
- Claim 6. First worker: trace proof. Second checker: every step follows (section 2). Also checked on all 17 objects as a linear identity. Verdict: reproduced. Method: argument + exact linear solve.
- Claim 7. First worker: rank(M-M^*) congruence invariant. Second checker: invariant, argument in section 2. 17/17 on random invertible X. Singular X and similarity are the must-fail contrasts. Verdict: reproduced. Method: argument + exact rank.
- Claim 8. First worker: 10 real-diagonalizable, 7 with non-real pair. Second checker: 10 and 7. All 17 are diagonalizable. The 7 have 8 non-real eigenvalues each (4 pairs). Verdict: reproduced. Method: charpoly, squarefree part q = p/gcd(p,p'), Sturm count on q, q(M)=0 test.
- Claim 9. First worker: cM+lambda I Hermitian only if Re c=0 and sym(M) scalar. Not scalar 17/17. Second checker: not scalar 17/17. Exact solve of the real-linear system for (Re c, Im c, Im lambda) has only the zero solution at 17/17, so c=0. Verdict: reproduced (with c != 0 assumed). Method: exact nullspace.
- Claim 10. First worker: 65,025 subsets. 20,225 symmetric. Schur = compressed D in each. Second checker: 65,025. Symmetric <=> compressed coupling zero for all 65,025. 20,225 symmetric. Schur = compressed D 20,225/20,225. No singular pivot sub-block. Verdict: reproduced. Method: full enumeration, exact Schur per subset.
- Claim 11. First worker: dissipative 17/17. In_spec(M)=In_spec(A)+In_spec(S)=(0,14,2). Second checker: 17/17 and (0,14,2) at 17/17. Zero eigenvalue algebraic multiplicity 2 = dim ker M = 2. Verdict: reproduced. Method: own method: imaginary-axis count via gcd(p(x),p(-x)) = x^z T(x^2), negative real roots of T by Yun + Sturm.
  Right-half-plane count by Cauchy index of Im/Re of p(iy), with a parity rule I derived and validated on 1,423 constructed polynomials (axis roots, multiplicities).
- Claim 12. First worker: 56 of 58. Second checker: my panels (180 random 8+8 systems, three panels, own seeds): 137 of 180 = 0.76 pooled. Dense independent coupling 77 of 120 (rate falls with coupling size: 14/15, 13/15, 4/15, 4/15 and 15/15, 13/15, 8/15, 6/15 at scales 1/4, 1/2, 1, 2). Row-6 support pattern with independent values 60 of 60.
  Verdict: differs in value (0.76 vs 0.97), conclusion holds: far above 1/10. Method: spectral inertia of M vs A + S, exact.
- Claim 13. First worker: 9 one-way edges, listed. K_BB nonzero nilpotent. Second checker: the same 9. Each K_BB nonzero with K_BB^2=0. Verdict: reproduced. Method: polynomial matrices.
- Claim 14. First worker: 528/528 on K. 479/479 on K' with val>=1. 49 outside. Second checker: K: 528/528 (all 528 satisfy val(K_BB)>=1. 477,152 entries, 0 mismatches). K': 479 blocks satisfy the hypothesis, equal on 479/479. The 49 blocks outside also match (0 mismatches). Lower bound val >= T on 49,547/49,547 entries with finite T. Verdict: reproduced.
  Extra: the 49 outside blocks show no failure on these matrices. Method: exact over Q(q) (numerator/denominator valuations) vs (min,+) Kleene star. Second method: Neumann series mod q^10 agrees 528/528 and 479/479.
- Claim 15. First worker: witness K00=-q^2, K01=K10=q, K11=0 is "outside the hypothesis". Second checker: Schur entry S_00 (eliminating state 1) is identically 0, tropical value 2: reproduced. But this witness satisfies val(K_BB) >= 1 (K11=0, or K00=-q^2 if state 0 is eliminated, where S_11 = q^2/(1+q^2) has val 2 = T), so it is not outside that hypothesis.
  It is a cancellation witness (-q^2 + q^2) inside it. Verdict: numbers reproduced, label differs. Method: exact polynomials.
- Claim 15b. First worker: (not claimed). Second checker: the witness that is outside, K22=1-q, K02=K21=q, K01=0: val(S01)=1 < T01=2. Verdict: extra. Method: exact.
- Claim 16. First worker: q=1/10, 1/1000: 32 distinct real. Q=1/2: 24 of 32 real. Second checker: 32 distinct real at 1/10, 1/100, 1/1000. At 1/2: 24 real with multiplicity and 24 distinct, 8 non-real. Verdict: reproduced. Method: integer charpoly (Faddeev-LeVerrier), Sturm. Controls diag(1..32), two rotation blocks, repeated eigenvalue.
- Claim 17. First worker: strictly row diagonally dominant at q=1/100. Second checker: I-K yes. I-K_BB 528/528. I-K_eff 528/528. Control q=1/2: I-K not dominant, I-K_eff dominant 0/528. Verdict: reproduced. Method: exact Fractions.
- Claim 18. First worker: undecided. Second checker: decided, see section 3. Verdict: decided. Method: exact nullspace + positive definiteness test.
- Claim 19. First worker: 0 of 168. 108 fail on inertia of reduced block, 60 on square class of det A. Second checker: 0 of 168. First failing criterion: inertia of S 108, square class of det A 60. Independently, every one of the 168 pairs fails on the square class of det A and of det S, and none fails on inertia of A. (The package README splits 108/59/1 under another order of checks.
  The 59+1 are the same 60.). Verdict: reproduced. Method: row-1 object B = [[S,t,u],[t,b,0],[u,0,0]] rebuilt from stored scalars and matched to the stored pivot determinants and Schur entries. Row-5 3x3 Hessians. Square classes by testing whether the ratio is a rational square (integer isqrt), cross-checked by an explicit sign or odd p-adic valuation witness at a prime below 20,000 for all 168.
- Claim 20. First worker: lambda = 871. All 168 pairs agree after the shift. Same for random pairs. Second checker: lambda = 871 for the objects of the 168 pairs (largest row sum 870, row-5 object). Row 1 B and the Hermitian M_full are below. All 38 row-1 and row-5 objects plus 871 I are positive definite. 168/168 agree. 200/200 random symmetric 3x3 pairs agree.
  Without the shift random pairs differ in inertia in 100/200. Scope note: the row-6 Liouvillian matrices have row sums up to 5003.02, and sym(M)+871 I is positive definite at only 15 of 17 of them, so 871 is the right shift only for rows 1 and 5. Verdict: reproduced, with the scope stated. Method: exact.
- Claim 21. First worker: rank S_el = 1, dim Z_B = 3 for diag(3,2,2). Second checker: rank 1, dim Z_B = 3. Two constructions of S_el agree (Schur with Delta X = -B, and (1/2) ae^T Pi ae with Pi the projector on self-stresses). Inertia (1,0,5). Extra: L = 2I gives S = 0 with dim Z_B = 3. Verdict: reproduced. Method: own construction from SPEC section 1.
- Claim 22. First worker: 16/16 carried, 0/16 naive. Second checker: 16/16 carried (S_el unchanged exactly, and S_lat' law exact), 0/16 naive keep rank 1 (my random unimodular U, not signed permutations. N=3: 8, n=4: 8). Controls: wrong law (U instead of U^-1) flagged 16/16. Naive S_el differs 16/16. A signed permutation keeps the collapse (SPEC 5(c)). Verdict: reproduced. Method: exact.
- Claim 23. First worker: (existence). Second checker: witnesses below. Verdict: reproduced. Method: exact Moore-Penrose by full-rank factorization, Penrose equations checked.
- Claim 24. First worker: diag(9/4,49/2,0). Second checker: same. Verdict: reproduced. Method: exact.
- Claim 25. First worker: accepts consistent invented witness. Refuses zero-gap falsified. Second checker: same. Verdict: reproduced. Method: team certifier imported by path.

### Claim 23 witnesses (symmetric M = [[A,B],[B^T,D]], S = D - B^T A^+ B, A singular)
- Condition holds and additivity holds: A = [[-1,-1],[-1,-1]], B = [-1,-1]^T, D = [-1]. A^+ = (-1/4)[[1,1],[1,1]], S = [0], In(M) = (0,1,2) = (0,1,1) + (0,0,1). The congruence M = E^T diag(A,S) E with E = [[I, A^+B],[0,I]] is verified exactly, which proves the general statement: if A A^+ B = B then M is congruent to diag(A,S), so inertia adds.
- Condition fails and additivity fails: A = [0], B = [1], D = [0]. A^+ = [0], S = [0], In(M) = (1,1,0) but In(A)+In(S) = (0,0,2).
- Condition fails and additivity holds: A = [0], B = [[1,0]], D = [[0,1],[1,0]]. A^+ = [0], S = D, M is the path graph on 3 vertices with eigenvalues +-sqrt2 and 0, In(M) = (1,1,1) = (0,0,1) + (1,1,0).
- Exhaustive counts (entries in {-1,0,1}): search 1 (singular 2x2 A, B 2x1, D 1x1. 243 systems): condition holds 75, all additive. Fails 168, none additive. Search 2 (A=[0], B 1x2, D 2x2. 243 systems): condition holds 27, all additive. Fails 216, of which 32 are additive.

### Claim 25 inputs
Input 1: TRANSFORMED_EXACT, families_searched [T1], applied T1, dof 1 of 2 constraints, 2 of 2 targets, null 0 of 10 at cap 1/10, rank 1, gap 0, witness the invented sentence "The literal identity fails at a point nobody computed. This sentence is invented". Result: CERTIFIED_TRANSFORMED_EXACT, admitted True, reasons []. A second invented witness ("Two plus two equals five fails") also admitted.
Input 2: INVARIANT_FALSIFIED with all 7 families, 0 of 4 targets, invented obstruction string, residual_gap = max_residual_gap = 0. Result: REJECTED_LAW2B_GATE, reason G4_FALSIFIED_HAS_ZERO_GAP only. Same input with gap 1 is admitted.
Controls: target 1 of 2 on an exact rescue refused (G1_TRANSFORMED_TARGET_FAILED), dof not below constraints refused, extra key / float / null cap above 1/10 raise ValueError. So the certifier checks numbers and schema and never evaluates the witness or obstruction text.

## 2. Claims 6 and 7, step by step

Claim 6. Let P = diag(Pr, Pp), invertible, and N = P^-1 M P Hermitian with M = [[D,B],[C,A]] and C = -B^* (B nonzero. In my convention B is the upper right block B').
1. The lower-left block of N is Pp^-1 C Pr = -Pp^-1 B^* Pr. The upper-right block is Pr^-1 B Pp, whose adjoint is Pp^* B^* Pr^-*. Hermitian means these are equal. Follows.
2. Multiply on the left by Pp and on the right by Pr^*: -B^* Pr Pr^* = Pp Pp^* B^*. With Gr = Pr Pr^*, Gp = Pp Pp^* (both positive definite because Pr, Pp are invertible) this is -B^* Gr = Gp B^*. Follows. Only the off-diagonal blocks are used. D and A play no role.
3. Multiply on the right by B: -B^* Gr B = Gp B^* B (square matrices, sizes match). Take traces: -tr(B^* Gr B) = tr(Gp B^* B). Follows.
4. Tr(B^* Gr B) = ||Gr^(1/2) B||_F^2 >= 0, so the left side is <= 0. B^*B is positive semidefinite and Gp is positive definite, so tr(Gp B^*B) = tr(Gp^(1/2) B^*B Gp^(1/2)) >= 0. Hence both sides are 0. Follows.
5. Tr(B^* Gr B) = 0 with Gr positive definite forces Gr^(1/2) B = 0, so B = 0, contradicting B nonzero. Follows.
No repair needed. Remarks: it holds over C (Hermitian Gr, Gp) and for rectangular B. The condition is on similarity by a block-diagonal P (so it covers diagonal D^-1 M D). It says nothing about non-block-diagonal similarity, and similarity does not preserve rank(M-M^T) (my control shows the rank changes), which is why claim 7 does not replace it.
I also checked it computationally: on all 17 objects the exact linear solution space of (Gr,Gp) (30 of 72 dimensions at point 0) satisfies tr(B^T Gr B) + tr(Gp B^T B) = 0 identically, which is the identity of step 3. With Gr, Gp positive definite the two terms have the same sign, so only B=0 survives. Control: with C = +B^T, Gr=Gp=I solves the equation.

Claim 7. For invertible X, (X^* M X) - (X^* M X)^* = X^*(M - M^*)X, so its rank equals rank(M - M^*) because multiplying by invertible matrices on both sides preserves rank. If M is not Hermitian, rank(M-M^*) > 0, so no congruence X^* M X is Hermitian. (Row 6 has rank 8 or 12.) It is about congruence only. Verified exactly on 17/17 with random invertible integer X.
A singular X (projection onto the first 8 coordinates) does change the rank, so the test can see a change.

Claim 5 consequence: for diagonal d invertible (complex allowed), (D^-1 M D) Hermitian needs M_ij |d_j|^2 = M_ji |d_i|^2 for every pair (M real). Opposite signs, both nonzero, so impossible. This is the claim 6 argument in scalar form and agrees.

## 3. Claim 18: decided

Treated: P = diag(P_A, P_B), where for each of the 528 partitions (B a block of size 1 or 2 from claim 14, A its complement), and additionally the fully diagonal P (gauge similarity D^-1 K D) and the unrestricted P. The package has no single partition for row 4, so the 528 blocks are the natural set, since they are the blocks eliminated in claim 14. Equivalent form used:
G = P P^T positive definite, block diagonal, with K G symmetric (K G = G K^T). P^-1 (I-K) P = I - P^-1 K P, so I-K and K need the same P. K is taken at the exact rational points q = 1/10, 1/100, 1/1000 (the statement is for K(q) at fixed q. Symbolic q was not decided, see section 6).

Method. W = {X symmetric : K X = X K^T} is a linear space, computed exactly by sparse elimination over Q (dimension 32 at every q. Basis verified exactly). Because K has 32 distinct real eigenvalues at these q (claim 16), W = {V diag(d) V^T}, so unrestricted G exists (V V^T). For a partition, the block-diagonal members are the subspace of W with X_AB = 0.
A rank computation modulo a 61-bit prime gives nullity at least the true nullity, so nullity 0 mod p proves the exact solution space is {0}. Partitions with a nonzero candidate space were then solved exactly, each solution verified exactly to be block diagonal with K X symmetric, and tested for positive definiteness (symmetric elimination, second method: Cholesky pivots).

Result, identical at the three q (counts differ slightly):
- Fully diagonal G: solution space {0} at all three q. No gauge similarity symmetrizes K. (The 9 one-way edges already forbid it: K_ij g_j = K_ji g_i = 0 would force g_j = 0.)
- Unrestricted P: yes (V V^T).
- Of the 528 block partitions, 480 have solution space exactly {0}: no P. The other 48 (32 singletons, 16 antipodal pairs (0,30), (1,31), ... (15,17)) have a one-dimensional solution space. The 16 pairs: the generator has inertia (16,16,0), never positive or negative definite: no P.
  For the 32 singletons the generator is positive definite for some b: 8 singletons at q=1/10 (B = {0},{7},{13},{14},{16},{19},{25},{30}), 18 at q=1/100 and 1/1000 (B = {0},{2},{3},{7},{9},{10},{13},{14},{15},{16},{17},{19},{20},{23},{25},{28},{29},{30}). For the others the generator is indefinite (inertia such as (30,2,0), (31,1,0), (1,31,0), (28,4,0)): no P.
  For those PD cases P exists, so the answer is YES for those partitions, with the exact witness G (block diagonal, positive definite by two methods, K G symmetric exactly), reproducible by `clean_room/src/r4b.py`.
- None of the 9 one-way pairs has a P, at any q. This holds for every q by the structural argument: K_BB = [[0,k],[0,0]], K_BB G_B symmetric forces (G_B)_22 = 0.
- At q = 1/2 K has non-real eigenvalues (claim 16), so no real P of any shape exists (P^-1 K P symmetric forces a real spectrum). I did not run the partition solve there.
- Count explanation for the singletons: W has dimension 32 and X_AB = 0 imposes 31 conditions, so a one-dimensional solution always exists. Positivity is the real condition and it depends on b and q. For pairs, 60 conditions leave {0} except the 16 antipodal pairs.
Answer to the open item: no for the fully diagonal P, no for 480 of 528 small-block partitions, no for all one-way pairs. Yes for 8 (q=1/10) or 18 (q=1/100, 1/1000) singleton partitions. Undecided for none of the tested cases.

## 4. Three-mode results

Each script was run as `sandbox-exec` (network denied) with `/opt/homebrew/bin/python3.12` in `-I -B`, `-I -O -B` and `-I -B -W error`. Scripts: r6 (claims 1-12), r4 (13-17), r4b (18), r156 (19-20), lat (21-22), oth (23-24), cert (25). Exit 0 and identical stdout in all three modes for every script:

```
r6 mode1 rc=0 sha256(stdout)=0130f8857be29aaf12fe17f26f7ebaf56a876b33c9908c11befac08ff7915910 stderr_bytes=0
r6 mode2 rc=0 sha256(stdout)=0130f8857be29aaf12fe17f26f7ebaf56a876b33c9908c11befac08ff7915910 stderr_bytes=0
r6 mode3 rc=0 sha256(stdout)=0130f8857be29aaf12fe17f26f7ebaf56a876b33c9908c11befac08ff7915910 stderr_bytes=0
r6 IDENTICAL_ACROSS_MODES
r4 mode1 rc=0 sha256(stdout)=e2b71e165186c03d380185e31ce74c9a470d49714eba4192723723899c06ca13 stderr_bytes=0
r4 mode2 rc=0 sha256(stdout)=e2b71e165186c03d380185e31ce74c9a470d49714eba4192723723899c06ca13 stderr_bytes=0
r4 mode3 rc=0 sha256(stdout)=e2b71e165186c03d380185e31ce74c9a470d49714eba4192723723899c06ca13 stderr_bytes=0
r4 IDENTICAL_ACROSS_MODES
r4b mode1 rc=0 sha256(stdout)=76016fe596e564b5a5fd6a2a3804906004446f86a216c4c5322f889bd3af956d stderr_bytes=0
r4b mode2 rc=0 sha256(stdout)=76016fe596e564b5a5fd6a2a3804906004446f86a216c4c5322f889bd3af956d stderr_bytes=0
r4b mode3 rc=0 sha256(stdout)=76016fe596e564b5a5fd6a2a3804906004446f86a216c4c5322f889bd3af956d stderr_bytes=0
r4b IDENTICAL_ACROSS_MODES
r156 mode1 rc=0 sha256(stdout)=93f9d5c67a824f597aad765e7a60c632991930ecc0333837e6306cc691685d96 stderr_bytes=0
r156 mode2 rc=0 sha256(stdout)=93f9d5c67a824f597aad765e7a60c632991930ecc0333837e6306cc691685d96 stderr_bytes=0
r156 mode3 rc=0 sha256(stdout)=93f9d5c67a824f597aad765e7a60c632991930ecc0333837e6306cc691685d96 stderr_bytes=0
r156 IDENTICAL_ACROSS_MODES
lat mode1 rc=0 sha256(stdout)=92895e2082f8126823eb9147273bbe2fa85f099ced7f9e634b5aa61a01482926 stderr_bytes=0
lat mode2 rc=0 sha256(stdout)=92895e2082f8126823eb9147273bbe2fa85f099ced7f9e634b5aa61a01482926 stderr_bytes=0
lat mode3 rc=0 sha256(stdout)=92895e2082f8126823eb9147273bbe2fa85f099ced7f9e634b5aa61a01482926 stderr_bytes=0
lat IDENTICAL_ACROSS_MODES
oth mode1 rc=0 sha256(stdout)=a8d87a4eeb38bcb89750f29e543c68f5dfa0b85b6fde66170f245ae61a85fc0d stderr_bytes=0
oth mode2 rc=0 sha256(stdout)=a8d87a4eeb38bcb89750f29e543c68f5dfa0b85b6fde66170f245ae61a85fc0d stderr_bytes=0
oth mode3 rc=0 sha256(stdout)=a8d87a4eeb38bcb89750f29e543c68f5dfa0b85b6fde66170f245ae61a85fc0d stderr_bytes=0
oth IDENTICAL_ACROSS_MODES
cert mode1 rc=0 sha256(stdout)=46f6f23d5897266083fea0f6685ebc4cc855530f0242f37bde01096683a8b8d8 stderr_bytes=0
cert mode2 rc=0 sha256(stdout)=46f6f23d5897266083fea0f6685ebc4cc855530f0242f37bde01096683a8b8d8 stderr_bytes=0
cert mode3 rc=0 sha256(stdout)=46f6f23d5897266083fea0f6685ebc4cc855530f0242f37bde01096683a8b8d8 stderr_bytes=0
cert IDENTICAL_ACROSS_MODES
```
Stderr was empty in every run. Total lines "OK" / "FAIL" in the mode-1 outputs: see `out/*.mode1.out`. No FAIL line anywhere.

Must-fail controls (each is a line starting CTRL in the outputs, all passing, meaning my code flagged the wrong input): symmetric matrix recognised as symmetric and its sign-product test silent. Haynsworth additivity succeeds on the symmetrized M (positive control) while failing on the real M. C=-B^T vs +B^T in the claim-6 equation. Singular congruence changes rank. Similarity changes rank.
Jordan block flagged non-diagonalizable, rotation flagged non-real. Symmetric M has a nonzero (c, lambda) solution. A non-symmetric subset where Schur differs from compressed D. Spectral-inertia counter on four known matrices plus 1,423 constructed polynomials. Two-way pair not nilpotent. Perturbed tropical value flagged.
Diag(1..32), two rotation blocks and a repeated eigenvalue in the Sturm counter. Q=1/2 fails strict dominance. Self-agreement and rescaled-by-squares agreement in the square-class test, and a x2 rescale breaking it. Shift-free random pairs differ in inertia. Non-symmetrizable L gives S=0. Wrong S_lat law and naive S_el flagged on all 16. Wrong Moore-Penrose inverse rejected. Wrong p in claim 24.
Certifier schema and number controls. Claim 18: a matrix built to be diagonally symmetrizable gives a nonzero solution space in the same screen.

## 5. Ambiguities and what I assumed

- Row 6 block convention: stated at the top. A is the pivot block (8..15). "B' / B" in claim 1 read as the upper right block.
- Claim 3 "A has (0,8,0)": inertia of the symmetric part of A.
- Claim 8: "all-real spectrum and diagonalizable" read as minimal polynomial squarefree with only real roots. All 17 points are diagonalizable. They differ in reality of the spectrum.
- Claim 9: c = 0 (and lambda real) trivially works. I read the claim for c nonzero.
- Claim 11: "spectral inertia" counts roots with Re>0, Re<0, Re=0 with algebraic multiplicity. Zero eigenvalues count in the third entry.
- Claim 12: "matched" is under-specified. I took diagonal A and D with strictly negative entries, entries and coupling from small rationals, B' and C drawn independently, coupling scale varied. The rate depends strongly on coupling scale and on whether the support pattern is row 6's (60/60) or dense (77/120).
  Because D is strictly negative there, my random systems typically have no zero eigenvalues, so they match the additivity identity but not the specific shape (0,14,2). The conclusion (rate far above 1/10) holds for every reading I tried.
- Claim 15: "outside the hypothesis" is inconsistent with the stated hypothesis val(K_BB) >= 1 (see table). I computed both blocks of the witness.
- Claim 18: the package has no single row-4 partition, so I treated the 528 small blocks, the diagonal case and the unrestricted case. K fixed at rational q, P allowed to depend on q.
- Claim 19: row 1 object taken as the 3x3 bordered matrix B (the one with the same dimension as the row-5 Hessian. The package stores only its invariants, so I rebuilt it from the stored scalars and matched stored pivot determinants and Schur entries). Inertia of A and S, then square classes, in that order.
- Claim 20: "all the objects" read as the objects of the 168 pairs (rows 1 and 5). Including row 6 changes the largest row sum to 5003.02.
- Claim 21/22: n = 3 and 4 only. Base lattices symmetric with dim Z_B = 1 and rank S_el = 1.

## 6. What I did not check

- Claim 18 at symbolic q (generic q) and at q = 1/2 partition by partition (only the real-spectrum argument was used there). P with q-dependence was not examined. Block sizes above 2.
- Claims 21-22 at n = 8 (the package size). SPEC's proviso (only rigid motions) was not checked.
- Row 1/5 as objects with M_full (Q(i)) in claim 19. Only the 3x3 real objects.
- Claim 12 with the first worker's exact generator. Claim 14 over the general theorem (only the stored matrices).
- Novelty or prior-art for anything. The certifier's own vault anchors and generated certificate were not run.
- No GitHub writes were made. The clone used the orda-aska token for reading only.
