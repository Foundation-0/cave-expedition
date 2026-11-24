# Predicate extraction: what the ledger counts as a "Schur-complement instance"

Scope: text analysis plus exact computation on a null panel. Labels used below: **exact** (proved or computed in exact arithmetic, stated scope), **sampled** (measured on the seeded panel), **anchor** (a quote or fact read from the ledger at a named commit). Nothing here checks the ledger's own domain objects; other workers extract those. Classifications of the listed instances come from the ledger's wording only.

Source: foundation-0/cave-expedition, local ref `pr1` = commit `a7f837042d2e421c5a97cb1a25e5962dd96c1d9e`. Where noted, `pr4` = `742f3b2bf82cb4f8c1b4beb31cbe867c3d3bd574` (it has the README and Portal 10 statements at other line numbers, and no `structural_fingerprints.json`). Issue #2 read with `gh issue view 2` (read only).

## 1. Quotes (anchor)

**How the unification is stated**

- `README.md` @pr1 L16: "## 1. The Eight-Way Exact Schur-Complement Unification"
- `README.md` @pr1 L18: "eight distinct physical, geometric, statistical, and formal-verification frontiers across `Foundation-0` and `siliconcordat` are governed by the exact same Schur-complement / quadratic-block elimination invariant". (pr4: `README.md` L9 and L11.)
- `cartography/frontier_portals.md` @pr1 L227 (heading): "Four-Way Exact Schur-Complement / Fiber-Elimination Unification Across `gravity`, `incentre-lattices`, `spectral-inertia` & `quotient-lp-bounds`". Its own section 2 at L242-243: "Not a linguistic analogy—eight **exact, algebraic fiber-elimination equations** across the swarm are all instances of eliminating fast/internal/nuisance/quotient/moment/block fibers via an exact Schur complement / gauge projection". (pr4: L224 and L239.)
- `cartography/symbiosis/structural_fingerprints.json` @pr1 L39-43, entry SF-01 (the file holds 27 instances, L44-207):
  - `coordinate_free_signature` (L41): "Elimination of fiber V_obs from bilinear form G on V_obs (+) V_hid yields S = G_hh - G_ho G_oo^+ G_oh with GL(V)-invariant Sylvester inertia (n_+, n_0, n_-) certifiable in Z via Reduced Bareiss / Haynsworth additivity."
  - `invariance_group` (L42): "GL(V) basis changes & positive rescalings"
  - `null_condition` (L43): "Exact integer pivot signs & zero-residual congruence congruence V^T G V = D; zero floating-point eigenvalues."
- Issue #2 (title: "Synthesis: Scientific & Meta-Structural Implications of the Eight-Way Schur-Complement Unification (AUDIT-001–020R)"), section 2: "All eight tracks partition degrees of freedom into observed/boundary/slow ($x$) and hidden/internal/fast ($y$) under a quadratic or convex/tropical functional. Partial minimization yields $S = A - B D^{-1} B^\dagger$ (or Farkas dual projection), preserving Loewner order and exact inertia counts ($n_+(M) = n_+(D) + n_+(S)$)." Same section: "Taxonomy by elimination category: ... Quadratic/Hermitian elimination (Schur complement, Loewner order, $\mathbb{Q}(i)$ inertia) and Polyhedral/Tropical elimination (Farkas peeling, infimal convolution)".
- Other counts for the same label SF-01: `README.md` @pr1 L154 "29-Way Exact Schur-Complement Unification (`SF-01`)"; `cartography/symbiosis/cross_pollination_graph.json` L1791 "29-Way"; `cartography/symbiosis/RAMANUJAN_PORTALS_R4.md` L12 "17-Way"; `cartography/symbiosis/GLYPH_REGISTRY.md` L48 "17→21-Way"; `cartography/symbiosis/LAB_PORTALS_R3.md` L95 and `PRELINGUISTIC_PORTAL.md` L42 "15-Way". The SF-01 JSON lists 27 instances.

**What the protocol requires of a bridge**

- `verification/PROTOCOL.md` @pr1 L67-72 (Gate 5): "Shared vocabulary ... is **zero evidence** of mathematical unity." A bridge passes "**only if** it supplies": (1) "Explicit typed objects"; (2) "Explicit map / functor / intertwiner: Runnable code or exact formula implementing Phi"; (3) "Commuting diagram / quantitative defect bound ... (or proven/measured closure defect ..., strictly beating matched-dimension random null maps)"; (4) "Non-triviality & predictive transfer: Phi must not be degenerate ... or tautological ("both domains have a graph Laplacian"). It must transport a non-trivial theorem, bound, obstruction, or testable prediction".

## 2. The operational criterion the quotes imply

Test input: a block system `(M, k)`: a square matrix `M` over a base ring `K` (with an involution when `K` has one), partitioned into a pivot block `A = M[:k,:k]` (the "fiber" eliminated) and the rest `(B, C, D)`.

**P0 (exact).** The system is an instance iff `A` is invertible over `K`, so `S = D - C A^-1 B` exists. This is the weakest reading and the one the README sentence uses ("Schur-complement / quadratic-block elimination"). SF-01 writes `G_oo^+`, a pseudo-inverse. Over Q and Q(i) a Moore-Penrose inverse always exists, so with that wording the criterion holds for every matrix and every partition. I call that **P0g**; it is vacuous.

The ledger's wording is richer than P0 in these places, so each is written as its own predicate:

- **P1 (Haynsworth inertia additivity).** `M` Hermitian, `A` invertible: `(n+,n-,n0)(M) = (n+,n-,n0)(A) + (n+,n-,n0)(S)` (SF-01 L41; issue #2 "n_+(M) = n_+(D) + n_+(S)"). **P1g** is the same with the pseudo-inverse `S`; it needs the range condition `A A^+ B = B` (not stated in the ledger).
- **P2 (zero-residual congruence).** `V* M V = diag(A, S)` exactly with `V = [[I, -A^-1 B],[0, I]]` (SF-01 L43).
- **P3 (integer Bareiss sign rule).** After clearing denominators by a positive integer, fraction-free Bareiss gives integer pivots (all divisions exact) whose Jacobi sign pattern reproduces the inertia (SF-01 L41 "certifiable in Z via Reduced Bareiss"). Defined only when every leading principal minor is nonzero.
- **P4 (invariance, "GL(V) basis changes & positive rescalings", SF-01 L42).** P4a: `M -> cM`, `c > 0` gives `S -> cS`, same inertia. P4b: block-diagonal congruence `C = diag(C_o, C_h)` gives `S -> C_h* S C_h`, same inertia. P4c (measured, not a theorem): a mixing congruence in GL(V) that does not respect the partition; reports whether `In(S)` is preserved. This separates "invariant of the form" from "invariant of the form plus its partition".
- **P5 (determinant identity).** `det M = det A * det S`.
- **P6 (quotient property).** `(M/A11)/(A/A11) = M/A` for nested pivots (the ledger's "tower" and "multi-quotient" language needs it).
- **P8 (Loewner monotonicity).** If `M` is PSD with PD pivot block, adding a PSD matrix increases `S` in Loewner order (issue #2 "preserving Loewner order"; README rows 3 and 7).
- Integrality/sharpness (README row 1: "integer-exact pointwise sharp") is specific to `R_opt` and is not a property of the elimination; no generic predicate is extractable from it.

P1, P2, P4a, P4b, P5, P6 and P8 are textbook theorems (Haynsworth 1968, Crabtree-Haynsworth 1969, standard congruence). Each holds for every system meeting its stated hypothesis. A predicate that is a theorem for all matrices cannot separate any listed domain from an unrelated system (exact, argument; also measured below).

## 3. Listed instances (anchor classification, from the ledger's wording)

Mechanism classes: Hermitian/quadratic elimination with a literal matrix Schur complement (QH); literal Schur complement of a non-Hermitian matrix (QN); tropical/polyhedral elimination, with LP duality (T); no built object visible in the text read (N). "Evidence" says what the ledger text shows: a formula, a label naming Schur, a label that only implies a Gram/Laplacian/Bareiss structure, or nothing. Base rings are as the ledger states them or as the structure implies.

Counts: README eight = 6 QH, 1 QN (Lindblad), 1 T (coarse-graining). Portal 10 eight = 6 QH, 1 QN, 1 T. SF-01 list of 27 = 23 QH (21 of them only named or implied by a label; 2 have a formula in the text), 2 QN (GKSL Zeno, double-slit GKSL), 2 N (heedle, jacobian-lens). The README eight and the Portal 10 eight are the same eight domains in a different order.

### 3a. README section 1 (eight)

| id | item | mechanism class | base ring | literal D - C A^-1 B | evidence |
|---|---|---|---|---|---|
| R1 | Spectral Inertia R_opt | Hermitian/quadratic elimination, literal Schur | Q(i) Hermitian, rational entries | yes | formula in text |
| R2 | Higher-moment Stieltjes-Hankel | Hermitian/quadratic elimination, literal Schur | Q, Q(i) witnesses | yes | formula in text |
| R3 | Lattice elasticity sheaf Laplacian | Hermitian/quadratic elimination, literal Schur | Q | yes | formula in text |
| R4 | Coarse-graining / Maslov (Farkas peeling and Doob h-transform (a diagonal similarity); no D - C A^-1 B shown) | tropical/polyhedral (+ LP duality) | (min,+) semiring; Q[q] | no | formula in text |
| R5 | AeST Hamiltonian (Schur part only; Fenichel and Helmholtz parts are not Schur) | Hermitian/quadratic elimination, literal Schur | Q (rational functions of k) | yes | formula in text |
| R6 | GKSL Lindblad Zeno (Lindbladian is non-Hermitian (EP2 Jordan blocks); Haynsworth cannot apply) | literal Schur, non-Hermitian | Q(i) / symbolic | yes (non-Hermitian) | formula in text |
| R7 | Sylvester-Hadamard F8 to E8 (2x2 block only; headline fold and kissing results are not Schur objects) | Hermitian/quadratic elimination, literal Schur | Z[sqrt 2] / Q(sqrt 2) | yes | formula in text |
| R8 | Kigami resistance renormalization (Kron reduction; full Laplacian singular, eliminated interior block invertible) | Hermitian/quadratic elimination, literal Schur | Q | yes | formula in text |


### 3b. Portal 10 table (eight)

| id | item | mechanism class | base ring | literal D - C A^-1 B | evidence |
|---|---|---|---|---|---|
| P1 | spectral R_opt | Hermitian/quadratic elimination, literal Schur | Q(i) | yes | formula in text |
| P2 | Hankel hierarchy R_H4 | Hermitian/quadratic elimination, literal Schur | Q | yes | formula in text |
| P3 | F8 to E8 2x2 block M_{+-2}(s) | Hermitian/quadratic elimination, literal Schur | Z[sqrt 2] | yes | formula in text |
| P4 | Elastic tensor C | Hermitian/quadratic elimination, literal Schur | Q | yes | formula in text |
| P5 | Tropical (min,+) Schur/Doob peeling (update is c(j) = c(j-1) + d0(pi* h*): add a coboundary, no block inverse) | tropical/polyhedral (+ LP duality) | (min,+) semiring | no | formula in text |
| P6 | AeST Hamiltonian S_P | Hermitian/quadratic elimination, literal Schur | Q (rational functions) | yes | formula in text |
| P7 | Lindblad Zeno Schur (non-Hermitian) | literal Schur, non-Hermitian | Q(i) / symbolic | yes (non-Hermitian) | formula in text |
| P8 | Kigami Schur L_{n+1}/L_int (status in that table: routed to a probe, not marked verified) | Hermitian/quadratic elimination, literal Schur | Q | yes | formula in text |


### 3c. SF-01 instance list (27)

| id | item | mechanism class | base ring | literal D - C A^-1 B | evidence |
|---|---|---|---|---|---|
| SF-01#1 | gravity AeST dark-matter closure | Hermitian/quadratic elimination, literal Schur | Q | yes | formula in text |
| SF-01#2 | incentre-lattices elastic rigidity unjamming | Hermitian/quadratic elimination, literal Schur | Q | yes | formula in text |
| SF-01#3 | fractals GKSL Lindblad Zeno | literal Schur, non-Hermitian | Q(i) / symbolic | yes (non-Hermitian) | formula in text |
| SF-01#4 | warp#17 stacked LoRA Q_stack(s) (label-only classification) | Hermitian/quadratic elimination, literal Schur | Q | yes | label implies it |
| SF-01#5 | heedle blind-subspace drift Shed/hidden_move (label-only classification) | no built object visible | unknown | not shown | nothing shown |
| SF-01#6 | soko grounded-Laplacian R_eff (label-only classification) | Hermitian/quadratic elimination, literal Schur | Q | yes | label implies it |
| SF-01#7 | jacobian-lens verbalizable Jacobian vs dark kernel (fp16) (label-only classification) | no built object visible | dyadic Q (fp16 data) | not shown | nothing shown |
| SF-01#8 | FlashProve Schatten-nuclear vs Bareiss PSD (label-only classification) | Hermitian/quadratic elimination, literal Schur | Z/Q | yes | label implies it |
| SF-01#9 | formal-conjectures Hadamard.lean Bareiss Schur converse | Hermitian/quadratic elimination, literal Schur | Z | yes | label names Schur |
| SF-01#10 | DisTrO H_8 Schur ceiling | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#11 | RPC-Bench parallel-sum / 2x2 Plucker Schur commutator | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#12 | gravity Arm H1 Haynsworth-Schur Krein | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#13 | incentre-lattices Arm H2 p-adic BTZ DtN iterated Schur | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#14 | hawking Arm R4-4 indefinite DtN Krein flip (label-only classification) | Hermitian/quadratic elimination, literal Schur | Q | yes | label implies it |
| SF-01#15 | formal-conjectures Arm R4-2 Hankel/Stieltjes Schur | Hermitian/quadratic elimination, literal Schur | Z/Q | yes | label names Schur |
| SF-01#16 | openai/math Ramanujan-sum Schur projection | Hermitian/quadratic elimination, literal Schur | Z | yes | label names Schur |
| SF-01#17 | zeta-explorer Weil/Li/NB Gram/Schur PSD | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#18 | canculus 2x2 feedback Schur S = 1 + alpha g h | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#19 | Euler Leray projection as rank-1 Schur | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#20 | navier-stokes SignedTree multifrontal Schur | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#21 | continuum double-slit GKSL Schur pinching | literal Schur, non-Hermitian | Q(i) | yes (non-Hermitian) | label names Schur |
| SF-01#22 | aletheia 8-glyph operator calculus Loewner screening (label-only classification) | Hermitian/quadratic elimination, literal Schur | Q | yes | label implies it |
| SF-01#23 | camail linear-attention/SSM Schur pushforward | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#24 | alphaxiv Hilbert-operator Bareiss Schur conditioning | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#25 | quantum#1 U(1) severing / Looped-Schur | Hermitian/quadratic elimination, literal Schur | Q(i) | yes | label names Schur |
| SF-01#26 | warp-drive Bareiss Gram Schur Q_stack | Hermitian/quadratic elimination, literal Schur | Q | yes | label names Schur |
| SF-01#27 | zenodo rns-pnp coupling Gramian W = B^T B (label-only classification) | Hermitian/quadratic elimination, literal Schur | Z/Q | yes | label implies it |


Readings that follow from the wording (anchor, not verified against the artifacts):

- Two of the eight (the tropical coarse-graining row, and the Lindblad row) are not instances of the Hermitian invariant the SF-01 signature names. The tropical update `c(j) = c(j-1) + d0(pi* h*)` has no block inverse and no subtraction; (min,+) has no additive inverses. A Lindbladian is non-Hermitian (the README itself cites EP2 Jordan blocks), so `V* M V = D` and Haynsworth additivity cannot apply; only P0, P5 and P6 can.
- Issue #2 itself splits the eight into "Quadratic/Hermitian" and "Polyhedral/Tropical", which already concedes that README line 18's "exact same" does not cover row 4.
- README row 8 (Kigami) cites `AUDIT-010`, whose ledger entry (README section 2) is about 4-ray multiplicative Farkas curvature and Sabra checks, not a Kron reduction. Portal 10's own table (L254) marks the Kigami Schur row "Exact algebraic portal routed to `@fractals-probe`", not verified.
- The `V_obs` label is inverted between sources: SF-01 eliminates `V_obs`; issue #2 keeps observed variables and eliminates hidden ones.

## 4. Strongest repaired forms (to be tested by the next workers)

Written before any judgment of the claim.

- **S1 (equivalence over a base ring, partition-respecting).** For two domains with objects `(M_1, k_1)` over `K_1` and `(M_2, k_2)` over `K_2` (a common field `K`, or an explicit embedding of both into one), there exist `P_o, P_h` invertible over `K` such that `M_2 = diag(P_o, P_h)* M_1 diag(P_o, P_h)` (and `k_1 = k_2`). Then `S_2 = P_h* S_1 P_h` exactly, and `In(A_2) = In(A_1)`, `In(S_2) = In(S_1)`. This is Gate 5 items 1-3 with `Phi` = block-diagonal congruence. It is falsifiable on two extracted systems: the inertia pairs must agree. Over R, and for Hermitian forms over C, `(In A, In S)` is a complete invariant of `(V, G, V_obs)` when `A` is nondegenerate. Over Q the isometry class needs more (discriminant and Hasse invariants), which the inertia pair does not see.
- **S2 (coordinate-free exact invariant that unrelated systems do not share).** Take the pair `(In(A), In(S))` (equivalently `(In(M), In(A))`) as the invariant, and require that the listed domains' values lie in a restricted set `R` that is fixed before inspection and that matched unrelated systems leave with probability well below 1. As stated in the ledger no `R` is given, and every Hermitian block system with invertible `A` has such a pair, so the unrestricted S2 is satisfied by everything. The test needs the real inertia pairs from the extracted domain objects and a matched null (same size, same ring, same definiteness profile).
- **S3 (functoriality).** The domains compose their eliminations, and the composites obey the quotient property (P6) on their real towers (README row 4 "peeling tower", Portal 10 "iterated"). Test on the extracted towers: staged elimination equals one-shot elimination.
- **S4 (shared operation, not shared formula).** All eight perform partial minimization (infimal projection) of a convex function over a fiber. For a quadratic with `A` positive definite this equals `x* S x` exactly; for polyhedral functions it is Fourier-Motzkin or LP-dual elimination. This is the version issue #2 uses ("Partial minimization yields ... or Farkas dual projection"). It is the only form under which the tropical row can belong. It is true for any convex function on a product space (closure under projection), so it is a taxonomy, not a discriminating test; I did not implement an exact LP-elimination panel.
- **S5 (Gate 5 as written, applied to the SF-01 criterion).** Require a map `Phi` between two extracted objects that commutes with elimination, and score its defect against matched random maps. P4b is the statement that block-diagonal congruences commute; the null for S1 is a random pair of same-inertia matrices, which `null_panel.py` can supply.

## 5. Files

`null_panel.py` (generator), `p_check.py` (predicates, controls, instance table), `results.json`, `RESULTS.md`.
