# Outside check of the eight-way unification claim against Gate 5

This folder tests one sentence in the cave-expedition ledger, README section 1: eight research frontiers "are governed by the exact same Schur-complement / quadratic-block elimination invariant". A Schur complement is what is left of a matrix after one block of its variables has been eliminated.

The ledger's own PROTOCOL, Gate 5, says a claimed link between fields needs typed objects and a running map that beats matched random maps. No audit in the ledger applies Gate 5 to this sentence, and PR #4 (`verification/outside/`) does not rule on it.

The row-level mathematics of the eight rows is not in question here. This check complements PR #4. It asks only whether the shared-invariant sentence is supported.

Five workers did the check separately. `predicate/` tests the ledger's criteria on unrelated systems. `hermitian/` compares three matrix domains exactly. `lattice/` tests the one cross-domain map that exists as code. `tropical/` covers the tropical and linear-programming rows. `second/` is a second checker that shares no code with the others.
On 2026-11-22 two theorem checks were added to `second/` (`c4_thmA.py`, `c5_thmB.py`).

On 2026-11-22 a sixth part, `law2b/`, applied the owner's rule Law 2b to the rulings. It holds two checkers that share no code (`law2b/src/` and `law2b/clean_room/src/`), their recorded outputs, the specifications fed to the team's certifier and a write-up (`law2b/REPORT.md`). Six rulings changed and four were added (G5-17 to G5-20). See the section Law 2b below.

Each finding carries a label. **Exact**: computed in exact arithmetic or proved, with the scope stated. **Sampled**: measured on seeded random panels. **Anchor**: a fact read from the ledger or a third-party repository at a pinned commit (`SOURCES.json`). Novelty is N0 for every item, because no prior-art reading was done.

## Finding 1. The stated criterion does not discriminate (sampled, with exact textbook theorems)

Every test that can be read out of README section 1, Portal 10 and SF-01 is a theorem for any block system with an invertible pivot block. The tests are:

- A Schur complement exists.
- Inertia adds up (Haynsworth). The counts of positive, negative and zero eigenvalues of the whole matrix are the sums for the pivot block and the Schur complement.
- The matrix is congruent to diag(A, S).
- The determinant and quotient identities hold.
- Loewner monotonicity holds. The matrix order is preserved.

The tests ran on two panels of 360 unrelated systems each (master seeds 20261121 and 11235813, sizes 2 to 12) and on an independent third panel of 576 systems built by the second checker (sizes 2 to 10).

The systems are random positive-definite, indefinite, graph Laplacian, covariance, least-squares and Hermitian matrices over Q and Q(i). Every test passes in every system where it is defined. In the second panel, 6 of 360 systems have a singular pivot block, where the tests are undefined. In the third panel, 115 of 576 have one, and all three identities hold in the other 461 of 461.

Scrambling the partition (a random reordering of the indices, same pivot size) leaves the pass count of every theorem test unchanged. Two tests that are not pure theorems, the integer sign rule (P3) and a mixing congruence (P4c), vary by a few systems.

The pseudo-inverse form in SF-01 gives a Schur complement for every matrix (360 of 360 in both panels). Inertia additivity with that form holds only where the range condition `A A^+ B = B` holds: 714 of 714 such systems, and it fails in the 6 where the condition fails.
None of 14 must-fail controls passed, and a wrong formula such as D + C A^-1 B passes all three identities in only 19 of 461 systems.

## Finding 2. Two listed rows are outside the stated invariant (exact), and one cites no reduction (anchor)

Row 4 is a (min,+) system. It has no additive inverse, so no additive Schur complement exists for that object itself. Its Q[q] lift does have an exact elimination (G5-18). Row 6 is a non-Hermitian Liouvillian. Inertia is undefined for it, its coupling is antisymmetric, and its pivot block is negative definite, so no minimum exists. This holds at 17 of 17 parameter points tested.

Row 8 cites AUDIT-010. That ledger entry contains no such reduction, and Portal 10 marks the row as routed to a probe, not built. This is an anchor reading of the ledger text. The row 8 object was not built here.

## Finding 3. No equivalence among the three matrix rows tested (exact, near-match rate sampled)

The rows are spectral inertia (row 1), AeST (row 5) and the Liouvillian (row 6). Each pairing fails on size, symmetry type or reduced inertia.

Of the 168 spectral inertia against AeST pairs, 108 fail on the inertia of the reduced block, 59 on the pivot determinant class and 1 on the reduced determinant class. The one near-match holds only after a rescaling chosen for that pair. Such a match appears in 1 of 168 real pairs and in 12 of 1,401 random symmetric 3x3 pairs.

Only one regime of R_opt is a Schur value: 51 of the ledger's own 420 instances. The other 279 and 90 fall in a regime outside the Schur form and in the zero regime.

## Finding 4. The one running map is real, and its commuting test cannot single it out (exact, null maps sampled)

For AUDIT-017 and AUDIT-019, the map Phi = [[I, X],[0, R_L]] gives R_el = R_lat Phi and H_el = Phi^T H_lat Phi. The commuting defect is exactly zero on five n=8 instances (E8 at s=1 and s=1/2, D8 at s=1 and s=1/2, D8 at (4/3, 1/3)). Both sides share one rank-1 stress with the same scalar: 3/92 for E8 at s=1 and 1/32 for D8 at s=1.

The zero defect does not identify Phi. On E8 s=1 and on D8 s=1, every random block-upper-triangular map gives zero defect (200 of 200 on each), and no dense random map does (0 of 200 on each). The identity R_el = R_lat Phi is what identifies Phi.

## Finding 5. The rank-1 collapse belongs to the basis (exact on every instance, proviso removed for n >= 3 on 2026-11-22)

If no diagonal D makes D L symmetric, S is zero. If such a D exists, is unique up to scale and the stress is non-zero, S has rank 1. The converse fails: the smallest witness is diag(3,2,2). Both implications are argued in `lattice/SPEC.md` section 5 under the proviso that the intra-cell framework has only rigid motions. That proviso was checked exactly for n=3 to 8.
On 2026-11-22 it was removed for every n >= 3: the flex classification in Theorem B's proof shows that for n >= 3 the only flexes are rigid motions, and at n = 2 an extra flex exists. The basis is exact tests on instances plus a step-by-step reading of the proof by an independent reader. It is not machine-checked.

A plain change of basis of the same lattice loses the collapse in 44 of 45 small cases and in 4 of 4 at n=8. A carried change, which keeps the same bars, leaves S_el unchanged.

A conjectured exact rule for rank S held on 904 of 904 lattices. As stated in `second/REPORT.md`: on Z_B, sigma(z) = diag(z) L (L - 2I), and rank S = dim Z_B - dim{z in Z_B : z_i = 0 wherever row i of L (L - 2I) is non-zero}. It was derived before running. It was a conjecture when first written. On 2026-11-22 it was ruled VERIFIED for n >= 3 and refuted at n = 2 (G5-07, section Theorems A and B).

## Finding 6. The tropical and linear-programming rows (exact, general rule sampled)

Rows 4 and 8 are exact partial minimizations of convex functions. So are 300 of 300 unrelated convex problems. Partial minimization therefore classifies these rows and does not discriminate.

The valuation map commutes with elimination on the ledger's own Cole-Hopf matrices: in 45 witness blocks, and in 528 eliminations of the 32-state matrix. In general val(S_ij) >= T_ij, with equality exactly when the leading-coefficient sum over the minimizing walks is non-zero.

The second checker confirmed this on 19,456 entries in 2,400 instances with no violation. No proof was included at first. On 2026-11-22 the statement was ruled VERIFIED only under val(K_BB) >= 1 (G5-10, section Theorems A and B).

## What survives

(a) A taxonomy, not an invariant. Partial minimization covers the symmetric, tropical and LP rows. Schur reduction of a linear operator covers the matrix rows. The two coincide on symmetric positive-definite pivots, where both are classical. (exact)

(b) One exact cross-domain congruence, AUDIT-017 with AUDIT-019, with the symmetrizer criterion of Finding 5. (exact, n=8)

(c) One running map between the Q[q] and (min,+) objects, with an exact no-cancellation condition. (exact on the ledger's matrices, the condition sampled). Since 2026-11-22 this is ruled VERIFIED only under val(K_BB) >= 1 (G5-13).

Novelty is N0 for all three. None of them was checked against prior work.

## Theorems A and B (added 2026-11-22)

The team reviewed this package (https://github.com/Foundation-0/cave-expedition/pull/5#pullrequestreview-6010617792) and offered two theorems that they say close the three rulings we had left PARTIAL. A worker of ours tested both without the team's code. The scripts are `second/src/c4_thmA.py` and `second/src/c5_thmB.py`, with outputs `second/out/c4_thmA.txt` and `second/out/c5_thmB.txt`.
The theorem statements were taken from the team's review text.

Basis for G5-07, G5-10 and G5-13: exact arithmetic on the stated finite sets of instances, with must-fail controls, plus a step-by-step reading of the proof. Not machine-checked. Nothing here is a machine-checked proof, and no ruling says "proved".

**G5-07, Theorem B: VERIFIED, scope n >= 3, rational L.** Here n is the size of L. The rank formula of the old G5-07 holds on 1,725 instances (900 at n = 3, 600 at n = 4, 180 at n = 5 and 45 at n = 6, across 15 families) with 0 mismatches. Two constructions of S_el agree on 40 of 40.

Four must-fail controls were caught (677, 1,725, 486 and 737 of 1,725 instances disagree). The proof was read step by step for all n >= 3. Instances were tested for n = 3 to 6.

The formula is refuted at n = 2. L = diag(3,2) has rank 0 and the formula says 1. L = 3I has rank 1 and the formula says 2. On 400 random 2x2 instances the formula is wrong in 237. The earlier G5-07 carried no restriction on n. That was a defect in our wording.

**G5-10, Theorem A: VERIFIED, scope val(K_BB) >= 1 over Q[q].** Under that condition val(S_ij) >= T_ij, with equality exactly when the leading-coefficient sum over the minimizing walks is non-zero. When that sum is zero and S_ij is non-zero, 1 <= val(S_ij) - T_ij <= (|B|+1)D - T_ij, where D is the largest degree of an entry.

The check covered 7,600 instances (n = 3 to 6) and 27,502 entries with T finite, with 0 violations of the lower bound, the leading-term identity or the equality condition.

The gap bound held on 1,416 of 1,416 entries where it applies and was attained on 21. An exhaustive family of 177,147 small systems attains the bound val(S) <= 2D in 520. Six must-fail controls were caught.

The team's sentence that the regularity condition is necessary is not adopted.

What was observed: in a random panel that allowed val(K_BB) = 0, the lower bound failed only where det(I - K_BB)(0) = 0 (1,377 violations in 3,733 entries) and never where it was non-zero (0 violations in 41,702 entries). This is sampled-exact evidence, not a proof.

The output does not count how many of the 41,702 entries have val(K_BB) = 0. One hand-built system with val(K_BB) = 0 and det(I - K_BB) = -1 satisfies the bound.

**G5-13: VERIFIED only under val(K_BB) >= 1.** The map from Q[q] to (min,+) by valuation is ruled for that hypothesis and is not extended to general matrices. Outside it the ruling is NOT_SHOWN.

The lower bound is refuted by the witness K_22 = 1 - q, K_02 = K_21 = q (val(S_01) = 1, T_01 = 2). Where det(I - K_BB)(0) is non-zero the bound held on the sampled entries above, with no proof, and the minimizing walks can be infinite in number there.

The team's own check script for these theorems and its proof files are not in the repository at the team ledger's head `4564fd6`. Our check is the only one a reader can run from the repository. No prior-art search was done for either theorem, so novelty stays N0.

## The SF-01 instance count (added 2026-11-22)

The team's fingerprints file has 29 instances in class SF-01 at `4564fd6`, so the team's figure is right. Our predicate panel read 27 rows from the older snapshot at `a7f8370` (`SOURCES.json`, PR 1). The file has no field for the kind of each instance, so a reader cannot check the team's split of those 29 into kinds from the file.

This package does not say 30 anywhere (searched). The figure 30 appears at `4564fd6` in the team's own material: the ledger README ("30-way"), `schur_unification_summary` in the cross-pollination graph, `PRELINGUISTIC_PORTAL.md`, `ROUND10_PORTALS.md`, an instance reference string "SF-01 #30", and the team's review text.

## Law 2b (added 2026-11-22)

The owner's rule Law 2b says a formula may not be closed as false until seven families of global transformations have been searched for one under which it holds, with four guards against rescues that explain nothing. The specification is on PR #1 of this repository at `80606f1` (`symbiosis/round10/arm5-transformational-steelman/TRANSFORMATIONAL_STEELMAN_REPORT.md`, lines 32 to 53 and 95 to 99).
It is not in this repository.

Two checkers applied it to the rulings that close a claim as false. They share no code. `law2b/src/law2b_check.py` is the first. `law2b/clean_room/src/` is the second, written without reading the first. Both are exact (`int` and `Fraction`), run in three Python modes with the same output, and have must-fail controls. The full account is `law2b/REPORT.md`.

- G5-17. Row 6: Sylvester inertia additivity is invariant-falsified. The obstruction is the antisymmetric coupling. All seven families were searched.
- G5-18. Row 4, elimination clause: transformed-exact by valuation (family T5) on non-negative coefficients with val(K_BB) >= 1.
- G5-19. Row 4, inertia clause: neither certificate applies. Block-diagonal symmetrizations exist for some singleton blocks. Where they exist the matrix is positive definite and the statement is true of any such system. Decided at q = 1/10, 1/100 and 1/1000 for blocks of size 1 and 2. Not decided at symbolic q or for larger blocks.
- G5-20. The exact repairs (spectral inertia for row 6 and for the row 4 lift, a global shift for G5-04) are true of nearly any system of the same shape, so they give no link between fields.

Where the two checkers differ: the null rate for the row 6 repair depends on the panel (56 of 58 against 137 of 180, both far above 1/10). A witness was mislabelled as outside the valuation hypothesis. The shift 871 is a bound for rows 1 and 5 only. The second checker was right on the last two.

Limits. Several terms of the rule are defined for statistical claims, and our analogues for exact algebra are readings (listed with line numbers in `law2b/REPORT.md`, section 8). The null panels are our choice. The team's certifier checks numbers and schema, and admits an invented witness string, so "certified" here rests on the two checkers' arithmetic.
The team's standalone verifier passes but cannot run its live anchor check, because the anchored files are not in the repository. No prior-art search was done, so novelty is N0.

## Ruling history

Rulings that were replaced stay on record in `RULINGS.json`, in the `history` list of each entry, with the old text verbatim. G5-17 to G5-20 are new on 2026-11-22 and replace nothing.

| id | superseded ruling | superseded on | reason |
|---|---|---|---|
| G5-07 | PARTIAL, sampled: conjecture on the rank formula, 904 of 904 lattices, not proved, no restriction on n | 2026-11-22 | Theorem B read and tested independently. VERIFIED for n >= 3, refuted at n = 2. |
| G5-10 | PARTIAL, sampled: val(S_ij) >= T_ij in general, 2,400 instances, no proof | 2026-11-22 | Theorem A read and tested independently. VERIFIED under val(K_BB) >= 1. The old wording had no condition. |
| G5-13 | PARTIAL, exact: map exact on the Cole-Hopf matrices, no-cancellation condition sampled | 2026-11-22 | With G5-10 ruled under val(K_BB) >= 1, the map is ruled for that hypothesis and not extended. |
| G5-14 | FALSIFIED: false for rows 4 and 6 | 2026-11-22 | Law 2b. Row 6 is invariant-falsified. Row 4 fails as worded but its inertia clause gets neither certificate. The verdict stays FALSIFIED on row 6 alone. |
| G5-02 | VERIFIED: rows 4 and 6 outside the invariant | 2026-11-22 | Law 2b added that the statement for row 4 is about the (min,+) object itself, and that the quadratic form of the Liouvillian does not see the coupling. |
| G5-04 | VERIFIED: no equivalence among the three matrix rows | 2026-11-22 | Law 2b added that no transformation rescues it non-vacuously, the scope of the shift 871, and square-class counts next to the norm-class counts. |
| G5-05 | VERIFIED: commuting test does not single Phi out | 2026-11-22 | Law 2b added the numbers for the repaired statement, which guards G1 and G2 reject. |
| G5-06 | VERIFIED: with the rigid-motions proviso | 2026-11-22 | The proviso is removed for n >= 3. The transformed statements are named. |
| G5-01 | VERIFIED: range condition 'needed' for pseudo-inverse additivity | 2026-11-22 | The condition is sufficient, not necessary. Three exact witnesses. |

## Verdict on the sentence as worded

With SF-01's inertia invariant, the sentence is false for row 6. Under Law 2b that is invariant-falsified (G5-17). For row 4 it fails as worded. Its elimination clause has an exact transformed form (valuation, family T5, on the stated domain, G5-18).
Its inertia clause gets neither certificate: block-diagonal symmetrizations exist for some small blocks, and where they exist the inertia statement is true of any such system (G5-19).

In its weakest reading, that each row uses block elimination, the sentence is true of any block system. The two exact repairs found are true of nearly any system of the same shape, so they give no link between fields (G5-20). Gate 5 is not met for the eight-way claim.

Proposed wording for README section 1:

> Eight frontiers each use block elimination. One pair, AUDIT-017 and AUDIT-019, is linked by an exact congruence. A shared invariant beyond the elimination identity has not been shown.

## Not covered

Row 2 and row 8 as objects. BW16 and Leech. Equivalence over Q by Hasse invariants. The live percolation boxes. The gravity anchor used the committed JSON because numpy was missing. No prior-art audit was done.

Law 2b limits: several terms of the rule are defined for statistical claims and our analogues for exact algebra are readings. The null panels are our choice and the rates depend on them. The team's certifier checks numbers and schema only. No prior-art search was done. See `law2b/REPORT.md` section 8.

## Files

`RULINGS.json` has one entry per finding and per surviving statement (verdict, label, scope, evidence paths, whether `second/` covers it). `law2b/` holds the Law 2b part: `REPORT.md`, `src/` (checker and certifier feed), `clean_room/` (second checker, `src/` and `out/`), `out/` (recorded runs of the first checker), `specs/` (the nine specifications and the certifier's answers) and `run_law2b.sh`.

G5-07, G5-10 and G5-13 also carry `ruled_on`, `basis` and a `history` list with the superseded ruling. `SOURCES.json` lists the third-party repositories with owner, PR number and pinned commit. `MANIFEST_sha256.txt` has the SHA-256 of every other file here. Each part keeps its own notes and outputs:
`predicate/PREDICATE.md` and `RESULTS.md`, `lattice/SPEC.md`, `second/REPORT.md`, and the `out/` folders. The part `tropical` reads `hermitian/objects/`, so the relative layout must stay as it is.

Left out: every `upstream/` folder (third-party clones), bytecode and temporary files. No file is over 1 MB, so none was left out for size. Three byte-for-byte copies of third-party files that `hermitian/src/run_anchor.sh` makes under `hermitian/out/` were left out. Their SHA-256 values and the command that regenerates them are below.

| file | SHA-256 | regenerate |
|---|---|---|
| `hermitian/out/anchor_fractals/probe4_witness_zeno_schur.py` | `f81fd8800693cbf3c4b470edafefb40738ea05a4f2426ec86f3ea5e26d0cae36` | `sh hermitian/src/run_anchor.sh <absolute path of hermitian/>` with the clones in place |
| `hermitian/out/anchor_fractals/committed_results.json` | `899d65178959d397a1121ec0a494dbe9cf6a5e7fd2ef2ecb29ef4f22b30c3451` | same command |
| `hermitian/out/anchor_gravity/probe1_aest_helmholtz_closure.py` | `09d29dd1304f5d925e6575c3f70dccd01c20939042acbe272e44023461769e80` | same command |

The probe1 script cannot run without numpy. Its recorded failure is in `hermitian/out/anchor_probe1.stderr`.

## How to rerun

Needs macOS with `sandbox-exec` and Python 3.12 (standard library only, no numpy). Run every script in three modes: `-I -B`, `-I -O -B` and `-I -B -W error`. Exit code and stdout must be the same in all three. From this folder:

```
PKG="$(pwd)"
SB="(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath \"$PKG\") (literal \"/dev/null\"))"
run() { d="$1"; shift; ( cd "$PKG/$d" && PYTHONDONTWRITEBYTECODE=1 sandbox-exec -p "$SB" perl -e 'alarm 3600; exec @ARGV' /opt/homebrew/bin/python3.12 "$@" ); }
run second -I -B src/c1_block.py | shasum -a 256
```

The sandbox blocks network access and allows writes only inside this folder. The scripts that build objects write them into `objects/` (identical bytes each time).

The lattice scripts take an objects folder. Mode `-I -B` uses `lattice/objects`, mode `-I -O -B` uses `lattice/out/objB` and mode `-I -B -W error` uses `lattice/out/objC`. Run the lattice scripts in this order: `build_objects.py`, then `gate5_real.py`, `gate5_null_lattices.py` and `gate5_null_maps.py`, then `checker2.py` and `anchor.py`, because the last two read what the earlier ones write.
The `hermitian` objects must be built before `tropical/src/tropical_audit.py s4bridge` runs.

Expected SHA-256 of stdout (the same in all three modes). Paths are relative to the part folder. `OBJ` is the objects folder for the mode.

| part | command (after `run <part> <flags>`) | SHA-256 of stdout |
|---|---|---|
| predicate | `p_check.py` | `00c21561b92759e6799dd66283e6f662f0b125e9ccd39f3d59b7b45fd405e31a` |
| predicate | `null_panel.py` | `f35da609412363f5020cc269a838461a01b508fe151e7a56e8f3141947349c1b` |
| second | `src/c1_block.py` | `f2d420e9131e2084be8b5cc8b4c2865a92454688ca4556c1d16d45a013ff0914` |
| second | `src/c2_real.py` | `92c16d8d69001594aa199a2a27ce8e6e2cb86f24c45d1f5b6fe81fcf88dbdc26` |
| second | `src/c2_panel.py` | `c555cdfbc103b00a8ea3938139c64824d301b3f22a881adafcc9a2e9af97b067` |
| hermitian | `src/build_objects.py "$PKG/hermitian/objects"` | `2e72b11e6fcfbbf047a420532aa105abba234d46566d9b665c99be3cf475b343` |
| hermitian | `src/compare.py "$PKG/hermitian/objects"` | `165fd8bc6c005bfe5b671ee14057b31e7cc93efe9b21bb7edea27281d839e10b` |
| lattice | `src/build_objects.py OBJ` | `9fd55f770f8767dc877992187e6742a94b3f09b693a9cee2bb63aa0767ad7c49` |
| lattice | `src/gate5_real.py` | `f01b48b264cdcc05efe2e28b31bdd16f8106f19dd6b3156592fe30c013a00c33` |
| lattice | `src/gate5_null_lattices.py e8_s1 OBJ` | `105cdf96bf2d335b75c8f29c312a1d8683e1bae1aea9da73cb425cb49b14fee8` |
| lattice | `src/gate5_null_lattices.py d8_s1 OBJ` | `4e7528a447304d23edb76570b1b36f243940d1f150f8aabfd1f3c1901111143b` |
| lattice | `src/gate5_null_maps.py e8_s1 OBJ` | `b748b2e4818cccb964b06eec8ff4a3530ef52d661afb28ae233c34b10ac13224` |
| lattice | `src/gate5_null_maps.py d8_s1 OBJ` | `f3d1a64d01fd10b5cf5e6b3b27ead746d3e3df20322acefd938ebec203fed960` |
| lattice | `src/checker2.py OBJ` | `6369daddde75d19e453dd460779565a14448668b25d0025964497130dce23198` |
| lattice | `src/anchor.py OBJ "$PKG/lattice/out"` | `cf9e523af0bf9279ca25eabb394e3f5c78d28fc90aff4ab13ebd544d26bf1113` |
| second | `src/c3_trop.py` | `a3db319d0ed6b88ea452842b49f40efd7284d94aca06e850087faf965f464765` |
| second | `src/c4_thmA.py` | `44bd591fa1eb917cc197d25646931ba63af282c66541bcf069ec2c41c87a95b0` |
| second | `src/c5_thmB.py` | `760a9bb926dcffc2a027ef8300b602077d93aff7e8c1c40bdbc13de31d7f3cce` |
| tropical | `src/make_objects.py tower` | `852e5dbee0fa7430619b1e19f14eeb153776dc6d05f277597eec02513121b1fa` |
| tropical | `src/make_objects.py cole_hopf` | `cd7b0cbc544eadab655c62655d2dec11dff5602ed1ad85ad470f2c5eef86a714` |
| tropical | `src/make_objects.py lp` | `1dd7cedd29fd3ae3dfc63f5503f991891e60a6f0ab6b7a57dd94e96c3bcdf880` |
| tropical | `src/make_objects.py farkas` | `76e48f83f3ec99df3e1359282265a9402fead7add1f8c781a0fc47456da77c46` |
| tropical | `src/tropical_audit.py s4row4 out/anchor_tropical.stdout` | `d45cca3e9166810b848984954b6aa27c2b6d73a7b68afc91ca0200a57bf9073f` |
| tropical | `src/tropical_audit.py s4row8` | `5404c09c9045a68cc4ea17ae413b9977a90f47125a2b838a55b845b328096713` |
| tropical | `src/tropical_audit.py s4bridge ../hermitian/objects` | `72050d4cc4556ee83ee85389ab5bcc784d45a1ebe9ed76a7c355a4fad62e5589` |
| tropical | `src/tropical_audit.py s4null` | `4ec6bb543f5faedac5dc7a0102900df012ab92e52dd8adf0dbfb1935cd1045f6` |
| tropical | `src/tropical_audit.py s5real` | `c7410d85ecd3e544cd00cfbb2507d9583b4da8e1e244c420c960dc25fbc1853d` |
| tropical | `src/tropical_audit.py s5random` | `d348a28855877b839ecdc96667a909520d08695048322dc58a2ff3c38ada89bc` |
| tropical | `src/tropical_audit.py controls` | `5f523cd7ee65ef8dae849bd46fd07cdce871bf1ad27a1d53c74b93942191a021` |
| law2b | `src/law2b_check.py "$PKG"` | `44957f26500c70bfdf5b33986f56f7b9955ee244eddf004509e5176a0ceecb9b` |
| law2b | `src/feed_team_certifier.py out/law2b_check.mode1.out <team certifier>` | `9ab62f93b3d018bf40777f25b4e898cf2e0881076e5f7897429edbb8d996b0bf` |
| law2b | `clean_room/src/r6.py` | `0130f8857be29aaf12fe17f26f7ebaf56a876b33c9908c11befac08ff7915910` |
| law2b | `clean_room/src/r4.py` | `e2b71e165186c03d380185e31ce74c9a470d49714eba4192723723899c06ca13` |
| law2b | `clean_room/src/r4b.py` | `76016fe596e564b5a5fd6a2a3804906004446f86a216c4c5322f889bd3af956d` |
| law2b | `clean_room/src/r156.py` | `93f9d5c67a824f597aad765e7a60c632991930ecc0333837e6306cc691685d96` |
| law2b | `clean_room/src/lat.py` | `92895e2082f8126823eb9147273bbe2fa85f099ced7f9e634b5aa61a01482926` |
| law2b | `clean_room/src/oth.py` | `a8d87a4eeb38bcb89750f29e543c68f5dfa0b85b6fde66170f245ae61a85fc0d` |
| law2b | `clean_room/src/cert.py <team certifier>` | `46f6f23d5897266083fea0f6685ebc4cc855530f0242f37bde01096683a8b8d8` |

The lattice scripts write their objects into the objects folder, so a full run leaves `lattice/objects/` and `hermitian/objects/` byte-identical to what is shipped. The recorded runs of each part are in `predicate/RESULTS.md`, `hermitian/out/mode_hashes.txt`, `lattice/MANIFEST_sha256.txt`, `tropical/out/hashes.txt` and `second/out/hashes.txt`.
`predicate/results.json` is the stdout of `p_check.py`.

`tropical/src/run_all.sh` calls plain `python3` and rewrites `out/` and `objects/`. The table above was checked with Python 3.12 and the sandbox command instead.

`lattice/src/anchor.py` leaves one file open. Under `-I -B -W error` it prints a ResourceWarning to stderr and still exits 0 with the same stdout (recorded in `lattice/out/anchor_C.err`).

### What was rerun for the 2026-11-22 change

Only `second/src/c4_thmA.py` and `second/src/c5_thmB.py` were rerun for this change, each under `-I -B`, `-I -O -B` and `-I -B -W error` in the sandbox. Their lines are in `second/out/hashes.txt`. `second/src/run_hashes.sh` was edited to take an optional list of scripts (`SCRIPTS="c4_thmA c5_thmB"`) and to print the seconds per run.

The SHA-256 of `run_hashes.sh` listed in `second/REPORT.md` (`d8945b2b...`) is of the version before this edit. `MANIFEST_sha256.txt` has the current one. `c4_thmA.py` took 46, 51 and 51 seconds in the three modes and `c5_thmB.py` took 346, 361 and 287 seconds. Stdout was byte-identical across modes and equal to the recorded output, with empty stderr.
Every other script and its recorded output is unchanged and is carried from the earlier full rerun (81 scripts, three modes, from a clean clone).

### What was rerun for the Law 2b change (2026-11-22)

Both checkers were rerun from inside a fresh clone of this branch, each under `-I -B`, `-I -O -B` and `-I -B -W error` in the sandbox, with `alarm 3600`, using `law2b/run_law2b.sh`. The three modes ran side by side on a busy machine, so the times are long. Stdout was byte-identical across modes, stderr was empty, and the second checker's outputs equal the hashes it recorded before the move.
The team's certifier is not in this repository. The two steps that need it (`feed_team_certifier.py` and `clean_room/src/cert.py`) take its path as an argument. It is Foundation-0/cave-expedition PR #1 at `80606f1`, `symbiosis/round10/arm5-transformational-steelman/transformational_steelman_certifier.py`. Without the argument both steps are skipped.

Seconds in `-I -B` (see `law2b/out/hashes.txt` and `law2b/clean_room/out/hashes.txt` for all three modes):

- `law2b_check`: 675 seconds
- `feed`: 0 seconds
- `r6`: 26 seconds
- `r4`: 10 seconds
- `r4b`: 919 seconds
- `r156`: 0 seconds
- `lat`: 2 seconds
- `oth`: 1 seconds
- `cert`: 0 seconds

The recorded outputs of the team's standalone verifier and of arm 5 are in `law2b/out/team_verifier/` and `law2b/out/team_arm5/`. Every other script and output in this folder is carried from the earlier rerun.

### Checks that need the third-party clones

These read files from the pinned commits in `SOURCES.json`. Their recorded outputs are in the folders. They were not rerun for the check above.

- `second/src/c2_anchor.py` reads `lattice/upstream/pr107/results/expedition-fold-sheaf-collapse/fold_sheaf_collapse.py`. Recorded output: `second/out/c2_anchor.txt` (`df34a49f376f94ddca7d63079dec00b10b52e5df47e4be67ddb0cc3f233d3581`).
- `hermitian/src/anchor_compare.py <absolute path of hermitian/>` reads `hermitian/upstream/gravity/studies/expedition-aest-helmholtz-probes/probe1_aest_results.json` and the files made by `run_anchor.sh`. Recorded stdout hash: see `hermitian/out/mode_hashes.txt`.
- `hermitian/src/run_anchor.sh <absolute path of hermitian/>` runs three upstream scripts in a sandbox. The gravity probe needs numpy and fails without it.
- `lattice/src/up_driver.py` and `lattice/src/run_up.sh <mode> <tag> <script> [args]` call the upstream scripts in `lattice/upstream/pr106` and `lattice/upstream/pr107`. Recorded outputs: `lattice/out/up_*`, hashes in `lattice/MANIFEST_sha256.txt`. The recorded `up_e8_inplace` run exits 1 on purpose, because the sandbox blocks the certificate file the upstream script tries to write.
- `tropical/src/run_anchor.sh` runs three upstream scripts from `tropical/upstream/qlb` and `tropical/upstream/fr`. Recorded outputs: `tropical/out/anchor_*`.

Clone layout, at the commits in `SOURCES.json`: `hermitian/upstream/{fractals,gravity,spectral-inertia,ledger-pr1}`, `lattice/upstream/{pr106,pr107}` and `tropical/upstream/{fr,qlb}`. The `ledger-pr1` folder holds only `check_003_seam01_ropt.py` from the ledger at the PR 1 commit.

`anchor.py` and the `s4row4` section read recorded upstream outputs, so they run without clones.
