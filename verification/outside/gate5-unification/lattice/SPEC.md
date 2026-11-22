# Specification of the lattice pair (bar framework, Phi, claims)

This text defines every object with integers and Fractions (and a + b*sqrt2 over Q(sqrt2) for interior fold points). It names no code of mine. Upstream names appear only in section 6.

## 1. Construction for a general basis matrix L

Conventions. L is an n x n matrix whose ROWS r_i are the basis vectors. the lattice is {m L : m in Z^n} with m a row vector. B = L - 2I has rows b_i = r_i - 2 e_i. Indices run 0..n-1. Everything below is stated for n = 8. the formulas hold for any n >= 3 (the counts change).

Vertices. 2n vertices, indexed v = 2*a + s with axis a in 0..n-1 and sign bit s in {0,1}. Coordinates x_v = +e_a if s = 0 and -e_a if s = 1. For n = 8 there are 16 vertices.

Bars. Each bar is a tuple (u, v, m, ell) with translation m in Z^n and bar vector ell = x_v - x_u + m L. There are 2n(n-1) + n bars (120 for n = 8), in two groups.
- Intra-cell bars (112): for every i < j and every s_i, s_j in {0,1}: v = 2i + s_i, u = 2j + s_j, m = 0, so ell = x_v - x_u. The selection rule is "two vertices on different axes" (squared distance 2). Vertices on the same axis are not joined.
- Bridge bars (8): for each i: u = 2i (the vertex +e_i), v = 2i + 1 (the vertex -e_i), m = e_i, so ell = -2 e_i + r_i = b_i. This is the bar from +e_i in cell 0 to -e_i in cell e_i.
The bridge bars are selected by index, not by a distance test. For a general L they do not have squared length 2. All bars carry weight W = 1/2, whatever their length.

Coordinates.
- u-coordinates: u in Q^(2n^2) (128), entry index v*n + k is coordinate k of the displacement of vertex v.
- Strain coordinates: eps is a symmetric n x n matrix, coordinatised by the n diagonal entries eps_kk (indices 0..n-1) followed by the entries eps_kl for k < l in lexicographic order (indices n, n+1, ...). The coordinate is the matrix entry itself (eps_kl = eps_lk). there is no factor 2 or 1/2 in the coordinate. There are n(n+1)/2 = 36 coordinates.
- dL-coordinates: a lattice deformation dL is an arbitrary n x n matrix, entry (k,l) at index k*n + l (64).

Rigidity maps. The elongation of a bar is e = ell . (du_v - du_u) + ell . (strain term), which is half the first variation of |ell|^2.
- R_el acts on (u | eps) and has one row per bar: the u-part has +ell_k at index v*n+k and -ell_k at index u*n+k. the strain part is (ell_k^2 for k = 0..n-1 | 2 ell_k ell_l for k < l), i.e. e = ell eps ell^T.
- R_lat acts on (dx | dL) and has the same u-part (now acting on dx, the vertex displacement), and the dL part has entry m_k * ell_l at index k*n+l, i.e. e = ell . (m dL).
Write d0 for the common 120 x 128 u-part, ae for the 120 x 36 strain part and Z for the 120 x 64 dL part. Intra-cell bars have m = 0, so their Z rows are zero.

Hessians and Schur complements. H_el = R_el^T W R_el (164 x 164, partition 128 | 36). H_lat = R_lat^T W R_lat (192 x 192, partition 128 | 64). With W = (1/2) I:
- K = ae^T W ae (36 x 36), B_el = d0^T W ae (128 x 36), Delta = d0^T W d0 (128 x 128). The lattice side has K_lat = Z^T W Z, B_lat = d0^T W Z.
- Pseudo-inverse convention: Delta is singular (rank 99 at n = 8 for the real pairs). S = K + B_el^T X where X is any solution of Delta X = -B_el. The system is always consistent because H is positive semidefinite, and S does not depend on the solution chosen (upstream sets the free variables to 0). S_lat is defined the same way from K_lat, B_lat.
- Equivalent form: let Pi be the orthogonal projector (standard inner product on Q^120) onto the self-stress space ker(d0^T). Then S_el = (1/2) ae^T Pi ae and S_lat = (1/2) Z^T Pi Z.
- Volume normalisation: C = S / det L. Upstream's printed S_cell is the unnormalised S. upstream divides by a volume only in its jammed-network code (4n for D_n).

Upstream versus mine. Upstream's: the cell (2n vertices, same index convention), the intra-cell and bridge bars, weight 1/2, the strain row (ell_k^2 | 2 ell_k ell_l), the Schur convention with free variables 0, and bridges of the form b_i = a e_i + t C_i for a given integer or Fraction matrix C.

My generalisations: a bridge for an arbitrary L (b_i = r_i - 2e_i, no length test), the lattice-side coordinates (dx | dL), R_lat, H_lat, the normalisation by det L, and the self-stress form of S.

## 2. Phi

Phi has shape (128 + 64) x (128 + 36) = 192 x 164, rows indexed by (dx | dL), columns by (u | eps):

    Phi = [ I_128   X   ]
          [   0    R_L  ]

- X (128 x 36): for vertex v and coordinate l, row v*n+l. For a diagonal strain coordinate k: X[v*n+k][k] = x_{v,k}. For an off-diagonal coordinate c = (k,l), k < l: X[v*n+l][n+c'] gets x_{v,k} and X[v*n+k][n+c'] gets x_{v,l} (n+c' is the strain index). This is x_v eps, the affine displacement of vertex v.
- R_L (64 x 36): the map eps -> L eps, (L eps)_{kl} = sum_j L_kj eps_jl, written in the dL-coordinates above. Concretely, for a diagonal coordinate j: R_L[k*n+j][j] = L_kj for all k. For an off-diagonal coordinate (j,l): R_L[k*n+l][idx] = L_kj and R_L[k*n+j][idx] = L_kl for all k.
- Entries of X are integers. Entries of R_L are entries of L.

Identity: R_el = R_lat Phi. Proof for one bar: ell . (X eps)_v - ell . (X eps)_u = ell . ((x_v - x_u) eps), and ell . (m L eps) is the dL-part applied to dL = L eps. The sum is ell . ((x_v - x_u + m L) eps) = ell eps ell^T. Consequently H_el = Phi^T H_lat Phi.

## 3. Instances

H is the 8 x 8 Sylvester matrix, H_ij = (-1)^{popcount(i AND j)} for i, j in 0..7. I+ = {0,3,5,6} (H_ii = +1), I- = {1,2,4,7}.

E8 at s = 1: L = 2I + H/2. The diagonal is 5/2 at indices 0,3,5,6 and 3/2 at 1,2,4,7. every off-diagonal entry is H_ij/2, which is +1/2 or -1/2. Rows of H: row0 all +. row1 + - + - + - + -. row2 + + - - + + - -. row3 + - - + + - - +. row4 + + + + - - - -. row5 + - + - - + - +. row6 + + - - - - + +. row7 + - - + - + + -. det L = 16, L is symmetric, B = H/2.

D8 at s = 1: L = 2I + C with C = C_8, the twisted 8-cycle: C[0][1] = C[0][7] = -1. C[1][0] = +1, C[1][2] = -1. C[k][k-1] = C[k][k+1] = -1 for k = 2..6. C[7][0] = +1, C[7][6] = -1. all other entries 0. Rows of L:

    r0 = ( 2,-1, 0, 0, 0, 0, 0,-1)
    r1 = ( 1, 2,-1, 0, 0, 0, 0, 0)
    r2 = ( 0,-1, 2,-1, 0, 0, 0, 0)
    r3 = ( 0, 0,-1, 2,-1, 0, 0, 0)
    r4 = ( 0, 0, 0,-1, 2,-1, 0, 0)
    r5 = ( 0, 0, 0, 0,-1, 2,-1, 0)
    r6 = ( 0, 0, 0, 0, 0,-1, 2,-1)
    r7 = ( 1, 0, 0, 0, 0, 0,-1, 2)

det L = 32, L is not symmetric.

Fold curves (interior points, s a rational in [0,1]).
- E8: L8(s) has L_ii = a_+(s) for i in I+, a_-(s) for i in I-, and L_ij = b_+(s) H_ij (i in I+) or b_-(s) H_ij (i in I-) for i != j.

  With D_+ = (1+2 sqrt2) + (-1+2 sqrt2) s^2 and D_- = (-1+2 sqrt2) + (1+2 sqrt2) s^2: a_+ = ((6+5 sqrt2) + (-6+5 sqrt2) s^2)/D_+, a_- = ((2+3 sqrt2) + (-2+3 sqrt2) s^2)/D_-, b_+ = 2 sqrt2 s / D_+, b_- = 2 sqrt2 s / D_-. Checks: L8(0) = (2+sqrt2) I, L8(1) = 2I + H/2, and |b_i|^2 = 2 for every row at every s.
- D8: L(s) = (2 + a) I + t C_8 with t = 2s/(1+s^2), a = sqrt2 (1-s^2)/(1+s^2). Any rational point (a,t) with a^2 + 2 t^2 = 2, for example (4/3, 1/3), also gives a valid instance over Q.
Instances used: E8 s = 1, E8 s = 1/2, D8 s = 1, D8 s = 1/2, D8 at (a,t) = (4/3,1/3).

## 4. Claims and expected exact values

Let Schur_128(M) denote the Schur complement of the leading 128 x 128 block of M with the convention of section 1.

C1. Congruence: H_el = Phi^T H_lat Phi exactly (164 x 164), for every instance.

C2. Defect. defect = Schur_128(Phi^T H_lat Phi) - R_L^T Schur_128(H_lat) R_L, a 36 x 36 matrix. Expected: exactly zero for the five instances. Also Schur_128(Phi^T H_lat Phi) equals S_el computed directly from K, B_el, Delta. This is a general fact for any symmetric H_lat when the leading block of Phi is the identity (naturality of the Schur complement).

C3. Shape of S at n = 8 for all five instances: S_el has rank 1, inertia (positive, negative, zero) = (1,0,35). S_lat has inertia (1,0,63). d0 has rank 99, so 128 - 99 = 29 and 120 - 99 = 21 (these are H0 and H1). Traces: E8 s=1: 114/23. D8 s=1: 23/4. D8 at (4/3,1/3): 17297/1488. Upstream S_00: E8 27/92, D8 s=1 1/8.

C4. Closed form. Let z be a nonzero vector with diag(z) B symmetric (equivalently diag(z) L symmetric, see C5). Define sigma = sym(L^T diag(z) B), sym(M) = (M + M^T)/2, and the coordinate vector sigma_c = (sigma_ii for i | 2 sigma_ij for i < j).

Then S_el = c sigma_c sigma_c^T with c a scalar, and S_lat = c w w^T with w_{k*n+l} = z_k B_kl. With z = (1,...,1) for E8 s=1: sigma = 2I + H, c = 3/92. With z = (-1,1,...,1) for D8 s=1: c = 1/32. c scales as 1/lambda^2 if z is scaled by lambda. For the interior points c_el = c_lat exactly (same scalar on both sides).

C5. Rank-1 criterion (what I claim, see section 5 for status). Let Z_B = {z in Q^n : z_i B_ij = z_j B_ji for all i < j}. This is the same as the set of z with diag(z) L symmetric, because diag(z) B = diag(z) L - 2 diag(z) and 2 diag(z) is symmetric. "Exists" means a NONZERO z.

D = diag(z) need not be invertible or positive (z may have zero entries and negative entries). "Unique" means dim Z_B = 1. The statement I can support: rank S_el equals the rank of the linear map z -> sigma_c(z) on Z_B.

Hence Z_B = {0} gives S_el = 0, and dim Z_B = 1 with sigma(z) != 0 gives rank exactly 1. The statement "rank 1 if and only if dim Z_B = 1" is false as written. see section 5.

C6. Basis change. Replace L by L' = U L with U integer, det U = +-1 ("naive": keep the bridge bars m = e_i, so the bars change) versus "carried" (keep the same bars: m' = m U^{-1}, so every ell is unchanged).

Carried: S_el is exactly unchanged. S_lat' = (U^{-1} kron I)^T S_lat (U^{-1} kron I) with (U kron I) acting on the dL index k*n+l as dL' = U dL. the defect stays zero. Naive: the collapse is generically lost (rank 0 in the samples), not always.

C7. Scaling. Global scale by lambda (scale x_v and L together, so every ell becomes lambda*ell): d0 -> lambda d0, ae -> lambda^2 ae, hence S -> lambda^4 S exactly. Scaling only L (positions fixed) is not a law. in samples with factors 2, 1/3, 5/2 and -1 the inertia stayed (1,0,35).

## 5. Status of the criterion, families, counts, edge cases

Argued (not machine-proved in general). Self-stresses (y, z) with y on intra bars and z on bridges satisfy A y + D(b) z = 0, where A (128 x 112) maps intra stresses to vertex forces and D(b) maps z to forces -z_i b_i at vertex 2i and +z_i b_i at vertex 2i+1. Total force vanishes automatically.

Total torque about the origin is -2 sum_i z_i (e_i wedge b_i), so z is equilibrated by some y exactly when diag(z) B is symmetric, PROVIDED the only infinitesimal motions of the intra-cell framework are translations and rotations (so the left kernel of A has dimension n + n(n-1)/2 = 36).

That proviso I observed for n = 3..8 (self-stress space has dimension 20 = n(n-3)/2 when Z_B = 0, 21 when dim Z_B = 1 at n = 8) but did not prove for general n. Pure intra stresses have zero virial (sum y_e ell_e ell_e^T = sum_v x_v f_v = 0), so they do not enter S.

The lift of z contributes the row sigma_c(z). With a positive definite Gram matrix on the self-stress basis this gives rank S_el = rank of z -> sigma_c(z). The identity sigma_c = R_L^T w (up to the symmetrisation) was verified exactly on the instances with dim Z_B = 1.

Direction status. "Z_B = {0} implies S = 0" and "dim Z_B = 1 and sigma != 0 implies rank 1" follow from the argument and were confirmed on samples.

The converse is false: for L = diag(3,2,2,2,2,2,2,2) the space Z_B has dimension 8 and S has inertia (1,0,35). for L = diag(3,4,2,...,2) dim Z_B = 8 and S has inertia (2,0,34). for L = 2I (B = 0) dim Z_B = 8 and S = 0. for L equal to 2I with a symmetric 2 x 2 block off the diagonal, dim Z_B = 7 and rank 1.

So a rank 1 collapse does not force uniqueness of D. In a development run with a sparser sampler (6 trials per family, logs not kept) I also saw dim Z_B = 2 with rank 1 and dim Z_B = 3 with rank 3. Earlier wording of mine ("rank 1 iff a diagonal D exists, unique up to scale") overstated this and should be read as C5.

Families sampled for the final records (200 per family and instance, instances E8 s=1 and D8 s=1). Let d be the Smith diagonal of the integer matrix den*L (den = 2 for E8, 1 for D8), U, U1, U2 random unimodular matrices (products of 40 random steps I +- e_i e_j^T with i != j, steps with i = j skipped), Q a random signed permutation.
- c1: L' = (1/den) U1 diag(d) U2 (same determinant and Smith form, nonsymmetric).
- c2: L' = (1/den) U1^T diag(d) U1 (symmetric).
- c3: L' = U L (naive basis change of the same lattice).
- c4: L' = Q L Q^T (isometric copy, symmetric basis).
Counts of dim Z_B and collapse (S inertia (1,0,35)), E8: c1 0/200, c2 200/200 (always dim 1), c3 0/200, c4 200/200. D8: c1 1/200, c2 200/200, c3 0/200, c4 200/200. No final sample had dim Z_B >= 2. The seeds are splitmix64 seeds 100000 + t, 200000 + t, 300000 + t, 700000 + t for c1..c4, t = 0..199.
Real pairs: dim Z_B = 1 on all five instances (rank of the 28 equations is 7).

Edge cases. (a) The single D8 c1 hit has first row e_0 untouched by the sampler, so z = e_0 works (a z with zero entries, supported on one row). (b) Zero or repeated rows of L were not part of the families.

Single probes: L with two equal rows 2e_0 (singular) gave dim Z_B = 7 and S = 0. L = 2I gives S = 0 with dim Z_B = 8. A bridge with b_i = 0 makes a zero bar row and leaves z_i unconstrained.

I did not study it beyond these probes. (c) The naive basis change is not always lossy: U = diag(+-1) gives U L symmetrizable by diag(z)U, so the collapse persists. the claim is generic only.

(d) Rank deficient L and complex or irrational L outside Q(sqrt2) were not tested. (e) The mod-p second check reproduced S for the five instances and the ranks on a stride-4 subset (200 of 800 lattices) per instance.

## 6. Anchoring against upstream

Target: Foundation-0/incentre-lattices. PR 107 head edc795b0073d660576649937af0e6174ac2e229a, file results/expedition-fold-sheaf-collapse/fold_sheaf_collapse.py.

PR 106 head 33ff6da0c52b2fb3023ca06d200eab1bec32c0a3, file results/expedition-dn-e8-folds/verify_e8_spinor_fold.py. Load by path under a sandbox that denies writes. the second file writes a certificate beside itself in its main(), so call its functions instead of running it.

fold_sheaf_collapse.py:
- make_twisted_cycle_Cn(n) returns the integer matrix C_n (n >= 3).
- compute_fold_sheaf_elastic(C_mat, a, t) builds bridges b_i = t*C_i + a*e_i (it requires a^2 + 2t^2 = 2 but never tests |b_i|^2, and Fraction entries in C_mat are accepted).

  It returns a dict with n, a, t, H0 (128-rank d0 for n=8), H1 (bars - rank d0), euler_H0_minus_H1, S_cell_inertia ([positive, negative, zero]), tr_S_cell (string), S_00, axial_block_identically_zero, rank1_mode_normalized (row of S at the first nonzero diagonal entry divided by that entry, as strings). S_cell is my S (unnormalised, W = 1/2).
- rotational_locking_rank(C) returns the rank of the map z -> antisymmetric part of diag(z) C (7 for C_8 and for H/2).
- compute_portal9_E8_spinor_collapse_and_jamming() returns, under sylvester_hadamard_H8_rank1_bifurcation, rk_M_rot = 7, H0 = 29, H1 = 21, S_cell_rank = 1 and the inertia (4,4,0) of 2I + H.
- The command line (with --json) prints run_suite().
verify_e8_spinor_fold.py: build_sylvester_H8(), verify_lemmas_1_to_4(H), verify_lemma_5_bernstein_and_kissing(H, R2_cutoff=11), verify_lemma_6_uniqueness(), verify_b8_gauge_invariance(H), run_must_fail_controls(H).

The committed certificate's SHA-256 is e4f14b928a3b08897e562ed56e334c6471ccf12e6bd55f52b6273f2577b0ef31, the hash of json.dumps(cert, indent=2, sort_keys=True) plus a newline, with cert assembled as in main().

Expected upstream outputs for n = 8, compute_fold_sheaf_elastic: C_8 with (a,t) = (0,1): H0 29, H1 21, S_00 1/8, tr 23/4, inertia [1,0,35]. C_8 with (4/3,1/3): S_00 2527/2976, tr 17297/1488.

C_8 with (8/9,7/9): S_00 1925/28296, tr 2149217/155628. (1/2)H8 as C_mat with (0,1): S_00 27/92, tr 114/23, inertia [1,0,35]. The script itself only runs n = 3..7. the n = 8 inertia needs a direct call. Upstream has no E8 interior elasticity point.
