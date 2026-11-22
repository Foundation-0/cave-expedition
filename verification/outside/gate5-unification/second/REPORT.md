# Clean-room verification report (gate 5): C1, C2, C3

Method: own code from the mathematical specs only; exact Fraction / Q(sqrt2) / Q(i) arithmetic, no floats. Predicate `.py` files, hermitian/lattice/tropical `src/`, and every `out/` or `objects/` folder under gate5 were not opened. Each script was run in the sandbox under `-I -B`, `-I -O -B` and `-I -B -W error`: exit 0, empty stderr, identical stdout and out-file hashes (`out/hashes.txt`). Controls exit 2 if any passes; none did.

## Verdicts
**C1 VERIFIED.** 576 systems (9 families x 64, sizes 2..10, seeds 4100000+1000*family+t; integer symmetric, banded, circulant, Hilbert-type incl. indefinite, PSD and indefinite rank-deficient Gram, Hermitian over Q(i) (Gaussian-integer entries), Hermitian Gram, sparse zero-diagonal). Inertia by exact characteristic polynomial plus Descartes count (Hermitian via the 2n real embedding, halved), not LDL. Invertible pivot: 461; all three identities (inertia sum, det, V*MV = diag(A, M/A)) pass 461/461. Singular pivot: 115, refused 115/115; [[0,1],[1,0]] k=1 refused. Counterexamples: none. Controls: D + C A^-1 B passes everything on only 19/461, D - C A B on 74/461 (the survivors are trivial cases such as C = 0). Caveat: the identities are textbooks, so this says nothing about any domain, as claimed.

**C2 VERIFIED, with C5 as corrected; the "iff" wording is FALSIFIED (as the SPEC already says).**
- E8 s=1, E8 s=1/2, D8 s=1, D8 s=1/2 (Q(sqrt2)), D8 (4/3,1/3): C1 congruence R_el = R_lat Phi and H_el = Phi^T H_lat Phi exact; C2 defect exactly zero; Schur(Phi^T H Phi) = S_el; S_el = (1/2) ae^T Pi ae. d0 rank 99, H0 29, H1 21. S_el rank 1, inertia (1,0,35); S_lat (1,0,63). Traces 114/23, 23/4, 17297/1488; S_00 27/92 and 1/8; det L 16, 32. inertia(2I+H) = (4,4,0).
- C4: S_el = c sigma sigma^T and S_lat = c w w^T with equal c on all five (E8 c=3/92, D8 c=1/32, D8 (4/3,1/3) c=189/3968); c scales 1/lambda^2.
- Upstream anchor (untouched, sandbox): all four listed cases match, including S_00, trace, H0/H1, inertia, the normalised mode row, and rotational_locking_rank = 7.
- C6: carried change leaves S_el unchanged and S_lat' follows the Kronecker rule exactly (n=8 E8/D8, 2 U each; and 45/45 at n=3..5). Naive U L: collapse lost 44/45 at n=3..5 and 4/4 at n=8, but not always; U = diag(+-1) keeps it 45/45.
- C7: global scale gives S -> lambda^4 S exactly (2, 1/3, 5/2, -1). L-only scaling keeps (1,0,35).
- Defect test (n=3,4, 12 draws): true Phi, random [[I,X],[0,R]], and random [[P,X],[0,R]] all give zero defect 12/12; dense random maps give zero 0/12. So zero defect does not distinguish the true Phi from random block-upper-triangular maps; only R_el = R_lat Phi does.

**C5 table, 904 lattices** (440 main seed 7000000+; 176 fresh seed 9500000+; 264 fresh seed 9900000+; 24 at n=8 seed 9700000+; n=3..6 plus n=8; 11 families):
| dim Z_B | rank S counts |
|---|---|
| 0 | 0:374 |
| 1 | 0:19, 1:350 |
| 2 | 1:9, 2:29 |
| 3 | 0:2, 1:8, 2:19, 3:29 |
| 4 | 0:1, 1:2, 2:2, 3:2, 4:15 |
| 5 | 0:2, 1:1, 2:2, 3:3, 4:2, 5:10 |
| 6 | 0:1, 2:2, 3:2, 4:2, 5:1, 6:12 |
| 8 | 8:3 |

(a) no violation. (b) no violation (dim 1 and sigma != 0 gives rank 1). Converse of (b) fails: smallest rank-1 witness diag(3,2,2), dim 3. Smallest dim-1 witness with rank 0: L = [[2,0,0],[-1,2,0],[-1,1,2]] (sigma = 0), which is why the sigma != 0 qualifier is needed. "Rank 1 iff dim = 1" is violated on 19 main-panel lattices. The SPEC rule rank S = rank(z -> sigma_c(z) on Z_B) holds 904/904, and agrees with a separate route rank(ae^T N), N = self-stress basis. Conjecture, derived by me before running it: on Z_B, sigma(z) = diag(z) L (L-2I), so rank S = dim Z_B - dim{z in Z_B : z_i = 0 wherever row i of L(L-2I) is non-zero}. It held 904/904 including the fresh seeds. The proviso (only rigid motions of the intra-cell framework) was checked exactly for n=3..8.

**C3 VERIFIED.** 2400 instances (modes all-positive, mixed, planted tie, planted exact annihilation; n=4,5; 300 each; seeds 5200000+100000*mode+10000*(n-4)+t), 19456 entries. val(S) >= T: 0 violations. Equality iff leading-walk sum non-zero: 0 violations. Classes: equal 15113, strictly above T with zero lead sum 844, S_ij = 0 exactly while T finite 1206, both infinite 2293. Order N = (|B|+1)D + 1 (D = max entry degree), because S = P/det(I-K_BB), det has constant term 1 and deg P <= (|B|+1)D, so val(S) < N or S = 0. The truncated series matched the exact polynomial P in every entry. Controls falsified as required: "val = T always" (2050), "val <= T" (2050), single-hop T (139), sign-blind sum (2050).

## SPEC notes
No ambiguity found that changed a result. Section 4 says the naive collapse is "rank 0 in the samples"; I found rare exceptions. The SPEC calls the defect identity a general fact, which my random-map test confirms; it is weak evidence for Phi.

## Not done
pr106 certificate hash and its verify functions; mod-p check; n between 9 and beyond; Hermitian entries beyond Gaussian integers; complex L; rank-deficient pivots beyond refusal.

## Files and SHA-256 (paths relative to this directory)
Sources: src/exact.py 922d4f2bf899f6701027888ed5cc4bbcdc81ef6fc2f2a0a8eaef8c3fab2af2dc; src/lat.py 071d79fde1b250bc0ec8ad5912510296863de3f5298a1514065cec0059af6bb4; src/c1_block.py 3041ccfc102e9a2d047694508e97cd6cd285737e94d983d6f294a4547bbcfa2c; src/c2_real.py c7ed3c6d8472100b5da4479b4f95e5e76630645965acb95ccaa6e83c4c9b3f74; src/c2_panel.py 9e9928d938628bd061e7c875da7477714dc9d97394fadf9436c8fc31d1502892; src/c2_anchor.py 8e375c47fdabdeaae28e8ac68bd9678f0caaabc3201a11639f4627d8c2dc99b9; src/c3_trop.py 385d1ce2ef8351037bafc7016e9bc74b8a1bc5ad4ac799042cf060c3e4276914; src/run_hashes.sh d8945b2b3bbc019221c99025cbba1d00e578d40aa6bce6919400ee8b14021604
Outputs: out/c1_block.txt f2d420e9131e2084be8b5cc8b4c2865a92454688ca4556c1d16d45a013ff0914; out/c2_real.txt 92c16d8d69001594aa199a2a27ce8e6e2cb86f24c45d1f5b6fe81fcf88dbdc26; out/c2_panel.txt c555cdfbc103b00a8ea3938139c64824d301b3f22a881adafcc9a2e9af97b067; out/c2_anchor.txt df34a49f376f94ddca7d63079dec00b10b52e5df47e4be67ddb0cc3f233d3581; out/c3_trop.txt a3db319d0ed6b88ea452842b49f40efd7284d94aca06e850087faf965f464765; out/hashes.txt (the three-flag record).
