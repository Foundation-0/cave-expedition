# Wave 2 Round 10 — Arm R10-2 Report (`AUDIT-085`)
## Outside Unification & Novelty Reconciliation, Exact Algebraic–Tropical Bridge (`G5-10`/`G5-13`), and Exact Cross-Polytope Symmetrizer Rank Theorem (`G5-07`)

- **Audit ID:** `AUDIT-085R` (patched after `#513` closing `UNIF-BUG-01..03`)
- **Novelty Classification:** `N1` (Honest bounded extension & rigorous closure of external unproved `PARTIAL` claims; zero `N2` claims; strict Law-4 quarantine over `R10-N0-01`..`R10-N0-12`)
- **Primary Deliverables:**
  - `unification_bridge_audit.py` — Pure-$\mathbb{Q}$ (`int`, `Fraction`, stdlib-only, zero floats, zero bare asserts) 5-pillar reconciliation, live read-only 12-file staged digest verifier (`--standalone` to skip disk I/O), theorem certifier, taxonomy auditor, and fail-closed Gate-5 bridge certifier
  - `test_r5_unification_bridge.py` — Independent R5 mutation-hardened test suite (`38/38` mutants killed, `100.0%`, `0` survivors under `aletheia v1.4.0 mutate`)
  - `unification_bridge_certificate.json` — Exact deterministic live certificate (`canonical_sha256: c1ce29d8b38ce831828a6d53a4e9ef2a4bc7e315b33f0087baacb5b91bf83f44`, `4/4` isolated `-I` live stdout/file SHA-256 `a662374cdb5e08adab3323477584b155ce92dbdbcb54e45871d354fccaf17642`; `--standalone` `canonical_sha256: b8e0ec60d0c24711ec66fcc05ea2dd4e7d5f77360f99d26232e57b5d3b303b13`, `3/3` isolated `-I` stdout SHA-256 `86dc7577334bc121defbb20f7f647b3853302b760c6e9ae3d7e8021df938eaba`)
  - `REPORT_R10_2_UNIFICATION_AND_NOVELTY.md` — This report

---

## 1. Executive Summary & Epistemic Posture (Aletheia Laws 1–5 Applied to Ourselves)

This arm performs a zero-defensiveness, zero-rubber-stamp independent verification of the external critiques staged in Wave 2 Round 10:
- `aletheia#2` (*Prior Work by Mechanism*, `8` rows + Gate 9 / Anti-Patterns `#12` & `#13` + Two-Pass Advocate summary),
- `aletheia#4` (*Sentence-Level & Novelty Corrections*, `17` table rows + `CS-08` addendum comment `7068580116` + `7` "where v1 is right" items),
- `cave-expedition#4` (*Two-Pass Outside Audit*, `36` rulings = `13 stands`, `22 stands_narrowed`, `1 falls`, plus `zero-aska`'s `8`-item `CHANGES_REQUESTED` review `6009780996`), and
- `cave-expedition#5` (*Gate-5 Unification Audit*, `16` rulings = `11 VERIFIED`, `3 PARTIAL`, `1 FALSIFIED`, `1 NOT_SHOWN`).

**Four Headline Outcomes:**

1. **Full Honest Acceptance of Valid Outside Critiques:** Every confirmed prior-work match (`8/8` rows of `aletheia#2`), every confirmed wording/prose/math defect (`17+1` rows of `aletheia#4`, including exact pure-$\mathbb{Q}$ verification that `AUDIT-023` `CS-08` exhibits **zero Simpson reversal**), and the decisive Gate-5 falsification of our unqualified `"8-Way / 30-Way Exact Schur-Complement Unification"` headline (`G5-01`, `G5-02`, `G5-14`) are independently reproduced and confirmed without defensiveness.
2. **Exact Nuances & Outside-PR Gaps Also Documented:** We simultaneously verify the `7` items where our shipped code/proofs were already correct (only prose or READMEs overclaimed), document `zero-aska`'s `8` concrete defects inside `cave-expedition#4`, and identify that `cave-expedition#5` missed a genuine post-Round-1 verified cross-domain Fisher-Schur pullback (`M2`: `AUDIT-064 WI-4 <-> AUDIT-079R RIPO-FS-04`) and misclassified `judegomila/canculus` (`AUDIT-050`) as `QH` instead of `QN`.
3. **Complete Formal Proofs Closing ALL `3/3` Unproved `PARTIAL` Claims of `cave-expedition#5` (`G5-07`, `G5-10`, `G5-13`):**
   - **Theorem A (Pillar 2 — Closing `G5-10` & `G5-13`):** Complete pure-$\mathbb{Q}$ proof over $\mathbb{Q}[[q]]/\mathbb{Q}(q)$ of the **Algebraic–Tropical Elimination Bridge & Measurable Cancellation-Gap Theorem**: under pivot regularity $\operatorname{val}(K_{BB}) \ge 1$, $\operatorname{val}(S_{ij}) \ge T_{ij}$ holds universally; $[q^{T_{ij}}] S_{ij}(q) = L_{ij}$ (sum of leading-coefficient products over all minimizing walks); $\operatorname{val}(S_{ij}) = T_{ij} \iff L_{ij} \ne 0$; whenever $L_{ij} = 0$ and $S_{ij} \not\equiv 0$, the exact cancellation gap satisfies $1 \le \Delta_{\mathrm{cancel}}(i,j) \le (|B|+1)\deg(K) - T_{ij}$; strictly positive leading coefficients force $\Delta_{\mathrm{cancel}} \equiv 0$; and pivot regularity $\operatorname{val}(K_{BB}) \ge 1$ is **necessary** (certified negative-gap witness $\Delta = -1$ when $K_{22} = 1 - q$).
   - **Theorem B (Pillar 3 — Closing `G5-07` + Sharpness at $n=2$):** Complete 5-step pure-$\mathbb{Q}$ proof for **all $n \ge 3$ and all $L \in \mathbb{Q}^{n \times n}$** of the exact cross-polytope symmetrizer rank formula $\operatorname{rank}(S_{\mathrm{el}}) = \dim Z_B - \dim\{z \in Z_B : z_i = 0 \text{ whenever row } i \text{ of } L(L-2I) \ne 0\}$, including an elementary 4-character $\{\pm 1\}^2$ rigidity proof for all $n \ge 3$, exact automatic symmetry of $\operatorname{diag}(z) L(L-2I)$ on $Z_B$, **and exact $n=2$ square-flex sharpness counterexamples** ($L = \operatorname{diag}(3,2)$ giving $\operatorname{rank} S_{\mathrm{el}} = 0 \ne 1$, and $L = 3 I_2$ giving $\operatorname{rank} S_{\mathrm{el}} = 1 \ne 2$).
4. **Honest Upgrade of `SF-01` & Fail-Closed Gate-5 Certifier (Pillars 4 & 5):** `structural_fingerprints.json` `SF-01` contains **`29` entries** (not `30`; prose `#26..#30` drifted by `+2/+3`), strictly partitioned into **`23 QH + 4 QN + 0 T + 2 L`**. Shared mechanism taxonomy is strictly separated from the **3 verified Gate-5 cross-domain morphisms (`M1`, `M2`, `M3`)**, enforced fail-closed by `certify_unification_bridge_hardened`.

---

## 2. Row-by-Row Reconciliation of `aletheia#2` (`8/8` Prior-Work Mechanism Matches)

All `8` mechanism matches in `aletheia#2` (and corresponding Law-4 quarantine items `R10-N0-01`..`R10-N0-07`) were independently checked. Every mechanism classification below is accepted cleanly.

| # | Audit / Study | Our Original Mechanism Name | Known Literature Mechanism (`aletheia#2`) | Quarantine ID | Arm R10-2 Independent Verdict & Nuance |
|---|---|---|---|---|---|
| 1 | `AUDIT-004` | Iterative Multi-Quotient Farkas Peeling Tower | Saturated State-Dependent Cost Partitioning (Keller et al. IJCAI 2016 Def. 4; Seipp, Keller & Helmert JAIR 2020 Def. 13) | `R10-N0-01` | **CONFIRMED `N0` mechanism.** Exact LP/Farkas certificate engineering (`N1` at most). Weak dominance theorem proved in `peeling/F2` holds only when $\phi$ is constant on $\pi_2$-fibers; strict-dominance docstring is refuted (`hardin`: $114 < 237/2$, deficit `-9/2`). |
| 2 | `AUDIT-004` | Cohomological Optimality Theorem | Bellman equation / LP complementary slackness on shortest paths | `R10-N0-01` | **CONFIRMED `N0`.** Standard characterization of shortest-path potential $d^*$. |
| 3 | `AUDIT-008R` | Maslov–Doob Transform $K_q(c + dH) = D^{-1} K_q(c) D$ | Diagonal similarity / Johnson reweighting (ordinary); max-times tropical Doob transform (under Maslov dequantization) | `R10-N0-02` | **CONFIRMED `N0` + exact nuance verified in Pillar 1.** In ordinary $(+,\times)$ arithmetic, row `0` sums to `5/4 != 1` even at $H = d^*$ (NOT an ordinary Doob $h$-transform). Under max-times dequantization, row maxima equal $q^{\delta_{\mathrm{trop}}(u)} = 1$ iff $H = d^*$ (at perturbed feasible $H'=(2,1,0)$, row `0` max drops to `1/2`). |
| 4 | `AUDIT-005` | Identity 1 ($\|r_{\mathrm{adapt}}\|^2 - \|r_{\mathrm{OLS}}\|^2 = e_1^2 / (r+1)$) | Restricted Least Squares (RLS) / single-constraint Gauss–Markov residual update | `R10-N0-04` | **CONFIRMED `N0` formula; `N1` application retained.** Applying exact RLS to `gravity/docs/09` Claim 9 exposed the host's miscalibrated Falsifier 6. Boundary ties at $x = 0, 2$ verified exact in Pillar 1. |
| 5 | `AUDIT-010` | Theorem A (chain of scales with error boxes) | Simple Temporal Problem (STP) consistency on a chain (Dechter–Meiri–Pearl 1991) | `R10-N0-03` | **CONFIRMED `N0`.** Exact shortest-path / transitive inequality consistency. |
| 6 | `AUDIT-010` | Theorem B (four rays complete for log-convexity of 4 points in boxes) | Discrete convexity sandwich ($m=4$ case of Baron–Matkowski–Nikodem 1994) | `R10-N0-03` | **CONFIRMED `N0` + README bug verified in Pillar 1.** Code rays `(2,-3,0,1)` and `(1,0,-3,2)` have first moment `0` and exact conic decompositions `2(1,-2,1,0)+(0,1,-2,1)` and `(1,-2,1,0)+2(0,1,-2,1)`. README rays `(2,-4,3,-1)` and `(1,-3,4,-2)` have first moment `-1` and falsely reject genuinely convex `(1,1,1,2)`. |
| 7 | `AUDIT-018` | $16 \times 16$ Lindblad $s=0$ Schur complement (`2*g_tid + 2*g^2/g_CM`) | Second-order Markovian adiabatic elimination (Azouit–Sarlette–Rouchon 2016 line, block-diagonal kernel) | `R10-N0-05` | **CONFIRMED `N0` mathematics; `N1` model-calibration artifact.** Pillar 1 verifies at $(\gamma_{\mathrm{CM}}, \gamma_{\mathrm{tid}}, g) = (10, 1, 1/2)$: $\Gamma_{\mathrm{Schur}} = 41/20$, $O(g^2)$ true slow rate $= 37/18$, exact $O(g^2)$ gap $= 1/180 > 0$, exact product identity $\det(M) = 2\gamma_{\mathrm{CM}} \Gamma_{\mathrm{Schur}} = 41$. Our own code already computed the exact eigenvalue and Riccati lift; only the headline lacked "leading order". |
| 8 | `AUDIT-019` | Fold-sheaf stiffness & rank-1 collapse | Relaxed Cauchy–Born elasticity tensor (Lubensky et al. 2015 eq. A4) & pentamode / extremal rank-1 stiffness (Norris 2014) | `R10-N0-06` | **CONFIRMED `N0` mechanism; `N1` explicit multi-node $n$-dim classification.** Upgraded further in Pillar 3 by our exact universal proof of `G5-07` for all $n \ge 3$ and $n=2$ sharpness. |

**Process Additions from `aletheia#2` Endorsed for Round 10 Adoption:**
- **Gate 9 Addition & Anti-Pattern `#12` (Citation-Trail Search):** Searching ONLY by our own coined names (`"peeling tower"`, `"fold-sheaf"`, `"Maslov-Doob"`) misses standard prior art; every novelty claim requires a stripped-jargon mechanism search (already enforced via Law 4).
- **Two-Pass Advocate & Anti-Pattern `#13` (One-Sided Verifier):** `cave-expedition#4` demonstrated why a single adversarial pass is biased too: pass-2 steelmanning narrowed `22` of `36` first-pass findings and overturned `1` (`folds-dn-e8/F4`), recovering `N2` (medium confidence) for `AUDIT-017` `F_8 -> E_8` and recovering the catalog-disagreement signal in `AUDIT-012`.

---

## 3. Row-by-Row Reconciliation of `aletheia#4` (`17` Table Rows + `CS-08` Comment `7068580116` + `7` v1-Right Items)

| Row | Target / File | Outside Critique (`aletheia#4`) | Independent Arm R10-2 Verdict |
|---|---|---|---|
| 1 | `AUDIT-002` (`417/420`) | `203` of `417` are vacuous (`docs/10` gives `0`); of the remaining `217` nontrivial cases, `202` strictly beat `docs/10` and `15` are worse (`202 + 15 + 203 = 420`). | **CONFIRMED.** Report both `417/420` overall and the non-vacuous breakdown (`202` beat / `15` worse / `203` vacuous), plus note `R_opt` sharpness requires free matrix size and a written proof (`N1` upper end). |
| 2 | `AUDIT-002` (`A2` & `A4`) | `A2` is classical Stieltjes–Hankel / Chebyshev–Markov–Stieltjes (`N0`); `A4` beats both `R_opt` and `A2` only on hand-picked points. | **CONFIRMED.** Narrow `A2` to `N0` and scope `A4` strictly to witnessed regimes. |
| 3 | `AUDIT-004` (`hardin` docstring) | `tropical_quotient_sheaf_bridge.py` claims strict dominance over `single + zsl`, refuted by `hardin` (`114 < 237/2`, deficit `-9/2`) and `pi_imb->pi_y` (`52 < 56`). | **CONFIRMED (Pillar 1).** Replace strict dominance with weak pointwise dominance when $\phi$ is constant on $\pi_2$-fibers. |
| 4 | `AUDIT-004` (`64 -> 112` baseline) | Fair single-quotient baseline on the 32-state benchmark is `84` (`pi_y`), not `64` (`pi_x`), so 2-layer gain is `+28`, not `+48`; greedy tower (`60`) trails LP (`68`) and optimum (`80`) on repo instance 3. | **CONFIRMED (Pillar 1).** All rational inequalities (`112 - 84 = 28`, `60 < 68 < 80`) verified exact. |
| 5 | `AUDIT-004` (`AUDIT-008R` Doob) | `K_q(c+dH) = D^{-1} K_q(c) D` is NOT an ordinary Doob $h$-transform (`0/31` rows sum to `1`). | **CONFIRMED WITH NUANCE (Pillar 1).** Diagonal similarity in $(+,\times)$ (`row0 sum = 5/4 != 1`); exact **max-times (tropical) Doob transform** under Maslov dequantization (`max = 1` iff $H = d^*$). |
| 6 | `AUDIT-005` (`x = 0, 2` wording) | Prose said "HURTS" for `x <= 0` or `x >= 2`, whereas exact code & table show ties (`adapt^2 = OLS^2`) at `x = 0` and `x = 2`. | **CONFIRMED (Pillar 1).** Wording-only fix: helps iff `0 < x < 2`, tie at `x = 0, 2`, hurts iff `x < 0` or `x > 2`. |
| 7 | `AUDIT-005` (`Claim 9 / Falsifier 6`) | Does not "settle Claim 9"; gives exact algebraic condition exposing miscalibrated Falsifier 6. | **CONFIRMED.** Scope wording to Falsifier 6 calibration. |
| 8 | `AUDIT-006R` (`Q_stack` & trace-slack) | `Q_stack(s)` is `docs/10 §5.1` applied to `warp#15` (`N0` mechanism); trace-slack law is a first-order conservative sufficient bound (`4.8%` slack), not exact crossing. | **CONFIRMED.** |
| 9 | `AUDIT-010` (`README` rays) | Two witness inequalities in `README` mistranscribed (`U0^2 L2^3 >= L1^4 U3` and `U0 L1^3 U2^4 >= ...`), first moment `-1 != 0`. | **CONFIRMED (Pillar 1).** Code & note are correct (`U0^2 U3 >= L1^3`, `U0 U3^2 >= L2^3`); fix `README` only. |
| 10 | `AUDIT-010` (`Sabra` period-3) | "Refutes period 3" overstates a low-power statistic (L'vov 1998 has no period-3 by construction); seed-7 `0.659` disagrees with certificate. | **CONFIRMED.** Narrow prose to descriptive fit comparison and reconcile seed-7 figure. |
| 11 | `AUDIT-009` (`D_4` optimal) | "Optimal 4D packing $D_4$" overclaims; $D_4$ is optimal among **lattice** packings in 4D (non-lattice optimality remains open). | **CONFIRMED.** Insert "lattice" qualifier; `F_n -> D_n` all-$n$ fold stays strong `N1` / candidate `N2`. |
| 12 | `AUDIT-017` (`E_6, E_7` & `F_8 -> E_8`) | $E_6, E_7$ index obstruction is elementary (`N0`); `F_8 -> E_8` keeps `N2` (medium confidence) after full read of Borcea & Streinu (2021 §7), drop "landmark/confirmed" hype. | **CONFIRMED.** |
| 13 | `AUDIT-020R` (`BW16 / Leech`) | Downgrade `N2 -> N1`; rename "unjamming" to "bar-preserving release arc" (volume strictly increases, intra-motif contacts unchanged); fix proof sec. 3 (`A_sym >= (lambda_0 tau / 2) I`); note canonical `Pi(I)` fails on 28 contacts for Leech (seed found by search). | **CONFIRMED.** |
| 14 | `AUDIT-012` (`185 km/s` & `60.15`) | Zero-parameter `185.59 km/s` is NOT falsified; `60.15` was an optimizer artifact (profile `~145-150`); true sharper `N1` defect is **catalog disagreement** ($\Delta\chi^2 = 11.6$–$17.1$ on groups/clusters vs $\ge 173$ on galaxies) + `KiDS-1000` disjoint-anchor harm (adopted by host). | **CONFIRMED.** |
| 15 | `AUDIT-018` (`Lindblad O(g^2)`) | Headline omitted "leading order": exact slow rate differs at $O(g^2)$ by `2 g^2 gt / (gcm (gcm - gt))` when `gt != 0`; math is `N0` adiabatic elimination, artifact `N1`. | **CONFIRMED (Pillar 1).** Exact `1/180` gap verified at `(10, 1, 1/2)`. |
| 16 | `AUDIT-016` (`AeST 0.00008%` & `Inertia Box`) | `0.00008%` compares against invariant-manifold IC (protocol IC leak `0.37%` already diagnosed in our cartography; `5/65` is near-optimal ceiling). Inertia box certifier is sound (`N0` method extending Skalna/Hladik from PD to arbitrary inertia in exact $\mathbb{Q}$, `N1` application); drop "isolates singular line". | **CONFIRMED.** |
| 17 | `check_007` / `check_008` / `loom#7` | `check_007` pins stale hashes (`fa4d3a1b`, `35e16732`); `check_008` Track B fails against updated `loom` head; `loom#7` `"1/1"`/`"0/1"` formatting regression after `dfc8516`. | **CONFIRMED.** (Track B / `loom#7` live reproduction deferred to Phase 3 cleanup / Arm R10-1.) |
| **18 (`CS-08`)** | `AUDIT-023` (`aletheia#4` comment `7068580116`) | Label "Compute-Leakage Simpson's Paradox" is mathematically false: no subgroup reverses! | **CONFIRMED IN PURE $\mathbb{Q}$ (Pillar 1):** No-tool `56/86 - 44/67 = -16/2881 < 0`; Tool `13/14 - 33/33 = -1/14 < 0`; Aggregate `69/100 - 77/100 = -2/25 < 0`. All three point strictly in the same direction (`A < B`). Rename to **post-treatment compute-leakage mediation**; the matched-budget comparison remedy remains completely valid (and adopted by the host). |

**The `7` Items Where Our v1 Artifacts Held (Confirmed by Claude's Own Second Pass):**
1. `AUDIT-017` `F_8 -> E_8` fold survives Borcea & Streinu (2021 §7) (`N2`, medium confidence).
2. `AUDIT-002` `R_opt` sharpness (`N1`, upper end) is absent from Knausgard / Alpoge–Furman.
3. `AUDIT-012` catalog disagreement ($\Delta\chi^2 = 11.6$–$17.1$ vs $\ge 173$) and `KiDS-1000` disjoint-anchor harm (`N1`) are genuine defects in the host's C-27 leg.
4. `AUDIT-016` AeST `0.37%` residual is a real host-protocol IC leak (`5/65` ceiling).
5. `AUDIT-018` our shipped code ALREADY computed the exact slow eigenvalue, product identity, $O(N^{-4})$ ratio, and Riccati lift.
6. `AUDIT-016` inertia box certifier is `100%` sound on `2,795` boxes / `22,360` exact sample points including indefinite signatures `(1,0,2)`, `(2,0,1)`, `(2,0,2)`, `(3,0,1)`, `(1,0,3)`, `(3,0,0)`.
7. `folds-dn-e8/F4` ("computer-free") was ALREADY accurately scoped to `C_n` and the `E_8` endpoint lemma -> sole outside finding ruled **`falls`**.

---

## 4. Audit of `cave-expedition#4` (`36` Rulings + `zero-aska`'s `8` Review Findings) & `cave-expedition#5` (`16` Rulings)

### 4.1 Exact Audit of `cave-expedition#4`
- **Tally Verified:** `36` findings across `7` areas (`spectral`: 6, `leech-sheaf`: 6, `twoloop-stack`: 5, `peeling`: 5, `zerolog`: 5, `physics`: 5, `folds-dn-e8`: 4) -> **`13 stands`, `22 stands_narrowed`, `1 falls` (`folds-dn-e8/F4`)**.
- **Defects Inside `cave-expedition#4` Flagged by `zero-aska`'s `CHANGES_REQUESTED` Review (`6009780996` — All `8` Confirmed Substantive):**
  1. `eval_stack_certificate.py` `d < 0` guard is not isolated by a dedicated must-fail test.
  2. `check_recount_420.py` prints `417 / 3 / 202 / 15` counts without explicit assertions verifying them.
  3. `folds_dn_e8` verification suite has `0` must-fail controls.
  4. `AUDIT-010` Theorem C ("seasonal differencing") is asserted in prose with `0` backing rulings and `0` literature citations.
  5. `folds-dn-e8/F1` mixes a surviving `N2` technical core with a fallen `"landmark/confirmed"` prose label, yet is coded `stands_narrowed` rather than split (`21/2` if split).
  6. Several prior-work rows lack exact equation/theorem pinpoint citations.
  7. Ledger references mix `main` and `pr/1` revisions inconsistently.
  8. Minor script/manifest reproducibility hygiene items required before upstream merge.

### 4.2 Exact Audit of `cave-expedition#5` (`16` Gate-5 Unification Rulings)
- **Tally Verified:** `16` rulings (`G5-01`..`G5-16`) -> **`11 VERIFIED`, `3 PARTIAL` (`G5-07`, `G5-10`, `G5-13`), `1 FALSIFIED` (`G5-14`), `1 NOT_SHOWN` (`G5-16`)**.
- **What We Accept Without Qualification (`G5-01`, `G5-02`, `G5-14`):**
  - Every Hermitian/quadratic Schur identity in the ledger (`P0`–`P8`) is a textbook theorem satisfied by `100%` of applicable matrices in the `720`-system null panel (`2` independent seeds of `360` unrelated systems). Therefore, calling them `"instances of the Schur-complement invariant"` has **zero discriminating power** (Gate 5 item 4).
  - The 8-row README / Portal 10 table is **not uniform**: `6 QH` + `1 QN` (Lindblad, where Haynsworth inertia is undefined) + `1 T` (tropical `(min,+)`, where additive inverses and literal `D - C A^{-1} B` do not exist).
  - Mixing congruences (`P4c`) change `In(S)` in `49/359` and `40/351` indefinite cases: Schur inertia is an invariant of `(form, partition)`, NOT coordinate-free on the form alone.
- **What We Close & Upgrade Here (`3/3` `PARTIAL` Claims + Missed Post-Round-1 Morphism):**
  - `cave-expedition#5` explicitly left **`G5-07`** ("Not proved", 904 sampled lattices) and **`G5-10` / `G5-13`** ("No proof is included", 1,000 sampled matrices) as **`PARTIAL`**. Sections 5 and 6 below provide complete elementary pure-$\mathbb{Q}$ formal proofs closing ALL THREE `PARTIAL` rulings (including sharp failure boundaries!).
  - Furthermore, `cave-expedition#5` audited only `pr1` (27 `SF-01` entries) and therefore missed our Round-6/Round-9 verified cross-domain Fisher-Schur pullback (`M2`: `AUDIT-064 WI-4 <-> AUDIT-079R RIPO-FS-04`) AND miscounted `judegomila/canculus` (`AUDIT-050`) as `QH` instead of `QN`.

---

## 5. Theorem A (Closing `G5-10` & `G5-13`): Algebraic–Tropical Elimination Bridge & Measurable Cancellation-Gap Theorem

**Setting.** Let $K(q) \in \mathbb{Q}[q]^{n \times n}$ with degree $D = \max_{u,v} \deg K_{uv}$ (with $\deg 0 = -1$), partitioned into disjoint non-empty index blocks $A \sqcup B = \{0, \dots, n-1\}$. Write $t_{uv} = \operatorname{val}_q(K_{uv}) \in \mathbb{Z}_{\ge 0} \cup \{+\infty\}$ (with $\operatorname{val}_q(0) = +\infty$) and $\operatorname{lead}(K_{uv}) = [q^{t_{uv}}] K_{uv} \in \mathbb{Q} \setminus \{0\}$ for $K_{uv} \ne 0$. Define:
- **Exact algebraic Schur complement** in $\mathbb{Q}(q)^{|A| \times |A|}$ (whenever $Q(q) \triangleq \det(I - K_{BB}) \not\equiv 0$):
  $$S(q) = K_{AA} + K_{AB}(I - K_{BB})^{-1} K_{BA} = \frac{1}{Q(q)} P(q), \qquad P_{ij}(q) = Q(q) K_{ij} + \sum_{b,c \in B} K_{ib} \operatorname{adj}(I - K_{BB})_{bc} K_{cj}.$$
- **Exact $(\min,+)$ tropical Kleene-star elimination:**
  $$T_{ij} = \min\!\Big(t_{ij},\; \min_{b,c \in B} \big(t_{ib} + t^*_{bc} + t_{cj}\big)\Big) \in \mathbb{Z}_{\ge 0} \cup \{+\infty\},$$
  where $t^*_{bc}$ is the shortest-path distance from $b$ to $c$ inside $B$ (with $t^*_{bb} = 0$).
- **Minimizing-walk leading-coefficient sum:** Let $\mathcal{W}^*_{ij}$ be the set of all directed walks $\gamma = (v_0, v_1, \dots, v_r)$ with $v_0 = i$, $v_r = j$, internal vertices $v_1, \dots, v_{r-1} \in B$, and total weight $\sum_{s=0}^{r-1} t_{v_s v_{s+1}} = T_{ij}$. Define
  $$L_{ij} \triangleq \sum_{\gamma \in \mathcal{W}^*_{ij}} \prod_{s=0}^{r-1} \operatorname{lead}(K_{v_s v_{s+1}}) \in \mathbb{Q}.$$

**Theorem A.** *Suppose the eliminated block satisfies the **pivot regularity condition** $\operatorname{val}_q(K_{BB}) \ge 1$ (every nonzero entry of $K_{BB}$ is divisible by $q$). Then:*
1. *(Invertibility & formal power series)* $Q(q) = \det(I - K_{BB}) \in 1 + q\mathbb{Q}[q]$, so $\operatorname{val}_q(Q) = 0$, $I - K_{BB}$ is invertible in $\mathbb{Q}[[q]]^{|B| \times |B|}$, $(I - K_{BB})^{-1} = \sum_{m=0}^\infty K_{BB}^m$ converges in the $q$-adic topology, and $\mathcal{W}^*_{ij}$ is finite for every $(i,j) \in A \times A$ with $T_{ij} < \infty$.
2. *(Universal lower bound)* For every $(i,j) \in A \times A$, $\operatorname{val}_q(S_{ij}) \ge T_{ij}$.
3. *(Exact leading-coefficient identity & iff criterion)* For every $(i,j) \in A \times A$ with $T_{ij} < \infty$,
   $$[q^{T_{ij}}] S_{ij}(q) = [q^{T_{ij}}] P_{ij}(q) = L_{ij}, \qquad \text{and hence} \qquad \operatorname{val}_q(S_{ij}) = T_{ij} \iff L_{ij} \ne 0.$$
4. *(Measurable cancellation-gap bound)* Define $\Delta_{\mathrm{cancel}}(i,j) \triangleq \operatorname{val}_q(S_{ij}) - T_{ij} \in \mathbb{Z}_{\ge 0} \cup \{+\infty\}$. Whenever $L_{ij} = 0$ and $S_{ij} \not\equiv 0$, the gap is strictly positive and bounded explicitly by
   $$1 \le \Delta_{\mathrm{cancel}}(i,j) \le (|B| + 1) D - T_{ij}.$$
5. *(Positive-coefficient exact functoriality)* If $\operatorname{lead}(K_{uv}) > 0$ for every nonzero entry $K_{uv}$ (in particular for all Cole–Hopf Gibbs matrices $K_{uv} = q^{c(u,v)}$), then $L_{ij} > 0$ whenever $T_{ij} < \infty$, so $\Delta_{\mathrm{cancel}} \equiv 0$ identically.
6. *(Necessity of pivot regularity)* If $\operatorname{val}_q(K_{BB}) = 0$, the universal lower bound $\operatorname{val}_q(S_{ij}) \ge T_{ij}$ can fail strictly ($\Delta_{\mathrm{cancel}} < 0$).

**Proof.**
- *(1)* Since $K_{BB} \equiv 0 \pmod{q}$, $I - K_{BB} \equiv I \pmod{q}$, so $Q(0) = \det(I) = 1$ and $\operatorname{val}_q(Q) = 0$. Moreover, $K_{BB}^m \equiv 0 \pmod{q^m}$, so the Neumann series $\sum_{m=0}^\infty K_{BB}^m$ converges $q$-adically to $(I - K_{BB})^{-1}$ in $\mathbb{Q}[[q]]^{|B| \times |B|}$. Every internal step inside $B$ has weight $\ge 1$, so any walk of total weight $T_{ij}$ has length $\le T_{ij} + 2$; thus $\mathcal{W}^*_{ij}$ is finite.
- *(2)–(3)* Expanding $S_{ij}(q) = K_{ij} + \sum_{m=0}^\infty \sum_{b_0,\dots,b_m \in B} K_{i,b_0} K_{b_0,b_1} \cdots K_{b_m,j}$ in $\mathbb{Q}[[q]]$, every walk $\gamma = (v_0, \dots, v_r)$ contributes the polynomial product $\prod_{s=0}^{r-1} K_{v_s v_{s+1}}(q)$, whose valuation equals $\sum_s t_{v_s v_{s+1}} \ge T_{ij}$ (by definition of $T_{ij}$ as minimum walk weight). Hence every term has valuation $\ge T_{ij}$, proving $\operatorname{val}_q(S_{ij}) \ge T_{ij}$. Collecting the coefficient of $q^{T_{ij}}$ retains precisely those walks $\gamma$ with weight equal to $T_{ij}$, each contributing $\prod_s \operatorname{lead}(K_{v_s v_{s+1}})$; summing gives $[q^{T_{ij}}] S_{ij}(q) = L_{ij}$. Because $Q(q) = 1 + q\tilde{Q}(q)$ and $P_{ij}(q) = Q(q) S_{ij}(q)$, we also have $[q^{T_{ij}}] P_{ij}(q) = Q(0) [q^{T_{ij}}] S_{ij}(q) = L_{ij}$. Thus $\operatorname{val}_q(S_{ij}) = T_{ij}$ iff $[q^{T_{ij}}] S_{ij}(q) \ne 0$, i.e. iff $L_{ij} \ne 0$.
- *(4)* Since $\operatorname{val}_q(Q) = 0$, whenever $S_{ij} \not\equiv 0$ we have $\operatorname{val}_q(S_{ij}) = \operatorname{val}_q(P_{ij}) \le \deg(P_{ij})$. Now $\deg(Q) \le |B| D$ and every entry of $\operatorname{adj}(I - K_{BB})$ is a $(|B|-1) \times (|B|-1)$ minor of degree $\le (|B|-1) D$, so $\deg(Q K_{ij}) \le (|B|+1)D$ and $\deg(K_{ib} \operatorname{adj}(I-K_{BB})_{bc} K_{cj}) \le D + (|B|-1)D + D = (|B|+1)D$. Thus $\operatorname{val}_q(S_{ij}) \le (|B|+1)D$, giving $\Delta_{\mathrm{cancel}}(i,j) \le (|B|+1)D - T_{ij}$.
- *(5)* If $\operatorname{lead}(K_e) > 0$ on all nonzero edges and $T_{ij} < \infty$, then $\mathcal{W}^*_{ij}$ is non-empty and every summand in $L_{ij}$ is strictly positive, so $L_{ij} > 0 \implies \Delta_{\mathrm{cancel}}(i,j) = 0$.
- *(6)* Certified explicitly by Regime 5 below. $\square$

### Certified Pure-$\mathbb{Q}$ Witnesses Across All 5 Regimes (`unification_bridge_certificate.json`, Pillar 2)

| Regime | Witness Construction | Regular? | $\operatorname{val}(Q)$ | Entry $(0,1)$: $\operatorname{val}(S)$ vs $T$ | $L_{01}$ | Exact Gap $\Delta_{\mathrm{cancel}}$ | What It Proves |
|---|---|---|---|---|---|---|---|
| `R1` | Positive Gibbs with 2-node $B$-cycle ($|A|=2, |B|=2$) | `True` | `0` | `3` vs `3` (all 4 pairs match) | `1/1` | `0` | Exact functorial commutation with cycles (`deg bound = 15`) |
| `R2` | Signed non-cancelling ($K_{01}=q^2, K_{02}=q, K_{21}=-2q, K_{22}=q$) | `True` | `0` | `2` vs `2` | `-1/1` | `0` | Signed entries still commute iff $L_{ij} \ne 0$ |
| `R3` | Signed finite cancellation ($K_{21}=-q, K_{22}=q \implies S_{01}=-q^3/(1-q)$) | `True` | `0` | `3` vs `2` | `0/1` | **`1`** ($\le 2$) | Strict finite cancellation gap bounded by $(|B|+1)D - T_{01}$ |
| `R4` | Exact total annihilation ($K_{21}=-q, K_{22}=0 \implies S_{01} \equiv 0$) | `True` | `0` | `INF` vs `2` | `0/1` | **`INF`** | Complete algebraic annihilation despite finite $T_{01}=2$ |
| `R5` | Non-regular pivot ($K_{22} = 1 - q \implies Q = q, S_{01} = q$) | **`False`** | **`1`** | **`1` vs `2`** | N/A | **`-1`** | **Necessity of $\operatorname{val}(K_{BB}) \ge 1$**: Laurent pole breaks lower bound! |

---

## 6. Theorem B (Closing `G5-07` + $n=2$ Sharpness): Cross-Polytope Symmetrizer Rank Theorem

**Setting (`cave-expedition#5` `lattice/SPEC.md` & `lat.py`).** For $n \ge 2$ and any $L \in \mathbb{Q}^{n \times n}$, consider the periodic cross-polytope bar framework in $\mathbb{Q}^n$ with $2n$ unit-cell vertices $x_{2i} = +e_i$, $x_{2i+1} = -e_i$ ($i=0,\dots,n-1$), $2n(n-1)$ intra-cell bars connecting every non-antipodal pair $(x_{2i+s_i}, x_{2j+s_j})$ ($i < j$, $m=0$), and $n$ inter-cell bars connecting $x_{2i}$ to $x_{2i+1}$ with cell shift $m = e_i$ and bar vector $\ell_i = (x_{2i+1} - x_{2i}) + L_i = L_i - 2 e_i = \text{row } i \text{ of } B \triangleq L - 2I$. Let $d_0$ be the bar-displacement rigidity matrix, $a_e$ the symmetric-strain matrix ($E \mapsto (\ell_b^\top E \ell_b)_b$), $S_{\mathrm{el}}$ the relaxed Cauchy–Born elasticity Schur complement of $\frac{1}{2}[d_0 \mid a_e]^\top [d_0 \mid a_e]$, and $Z_B \triangleq \{z \in \mathbb{Q}^n : \operatorname{diag}(z) L = L^\top \operatorname{diag}(z)\}$.

**Theorem B.**
1. *(Universal rank theorem for all $n \ge 3$)* For **every $n \ge 3$** and **every $L \in \mathbb{Q}^{n \times n}$**,
   $$\operatorname{rank}(S_{\mathrm{el}}) = \dim Z_B - \dim\!\big\{z \in Z_B : z_i = 0 \text{ whenever row } i \text{ of } L(L - 2I) \ne 0\big\}.$$
2. *(Sharpness at $n = 2$)* The condition $n \ge 3$ is **strictly necessary**: at $n = 2$, the intra-cell square has a 1-dimensional non-rigid flex imposing the extra constraint $z_1(L_{11}-2) = z_2(L_{22}-2)$, strictly reducing $\operatorname{rank}(S_{\mathrm{el}})$ below the formula (e.g. $L = \operatorname{diag}(3,2)$ gives $\operatorname{rank} S_{\mathrm{el}} = 0$ vs formula `1`; $L = 3I_2$ gives $\operatorname{rank} S_{\mathrm{el}} = 1$ vs formula `2`).

**Complete 5-Step Proof.**
- **Step 1 (Gram Schur–virial rank equivalence).** Because $H = \frac{1}{2}[d_0 \mid a_e]^\top [d_0 \mid a_e]$ is a Gram matrix, its generalized Schur complement is $S_{\mathrm{el}} = \frac{1}{2} a_e^\top P_{\ker(d_0^\top)} a_e$, where $P_{\ker(d_0^\top)}$ is orthogonal projection onto the self-stress space $\ker(d_0^\top) = (\operatorname{im} d_0)^\perp$. Hence $\operatorname{rank}(S_{\mathrm{el}}) = \operatorname{rank}(a_e^\top N)$ for any basis $N$ of $\ker(d_0^\top)$.
- **Step 2 (Exact intra-cell rigidity for all $n \ge 3$ via 4-character $\{\pm 1\}^2$ decomposition).** Write each vertex displacement as $u_{i,\sigma} = s_i + \sigma a_i$ for $\sigma \in \{+1,-1\}$ ($x_{i,\sigma} = \sigma e_i$). For every distinct pair $i \ne j$, the four intra-cell bar equations $(\sigma e_i - \tau e_j) \cdot (u_{i,\sigma} - u_{j,\tau}) = 0$ ($\sigma, \tau \in \{\pm 1\}$) expand in the four orthogonal characters $\{1, \sigma, \tau, \sigma\tau\}$ on $\{\pm 1\}^2$ as:
  - coeff. of $1$: $a_{ii} + a_{jj} = 0$ for all $i \ne j$;
  - coeff. of $\sigma\tau$: $a_{ij} + a_{ji} = 0$ for all $i \ne j$;
  - coeff. of $\sigma$ and $\tau$: $s_{j,i} = s_{i,i}$ and $s_{i,j} = s_{j,j}$ for all $i \ne j$.
  Because $n \ge 3$, choosing three distinct indices $i, j, k$ gives $a_{ii} + a_{jj} = a_{jj} + a_{kk} = a_{kk} + a_{ii} = 0 \implies a_{ii} = 0$ for all $i$. Thus $A = (a_{ij})$ is skew-symmetric ($A \in \mathfrak{so}(n)$) and $s_i = c$ is a constant translation vector $c \in \mathbb{Q}^n$. Therefore $\ker(d_0^{\mathrm{intra}}) = \{u_{i,\sigma} = c + \sigma A^\top e_i : c \in \mathbb{Q}^n, A \in \mathfrak{so}(n)\}$ has exact dimension $n + \binom{n}{2}$ for **every $n \ge 3$**. *(At $n = 2$, only the single equation $a_{11} + a_{22} = 0$ exists, leaving the 1D flex $a_{11} = -a_{22} = 1$, i.e. $u_{\mathrm{flex}} = (+e_1, -e_1, -e_2, +e_2)$.)*
- **Step 3 (Admissible inter-cell stresses equal $Z_B$).** An inter-cell stress vector $z \in \mathbb{Q}^n$ completes to a global self-stress $(\omega_{\mathrm{intra}}, z) \in \ker(d_0^\top)$ iff $(d_0^{\mathrm{inter}})^\top z \in \operatorname{im}((d_0^{\mathrm{intra}})^\top) = (\ker d_0^{\mathrm{intra}})^\perp$. For every rigid motion $u_{i,\sigma} = c + \sigma A^\top e_i$:
  $$\langle (d_0^{\mathrm{inter}})^\top z,\, u \rangle = \sum_{i=1}^n z_i\, \ell_i \cdot (u_{i,-1} - u_{i,+1}) = -2 \sum_{i=1}^n z_i\, \ell_i \cdot (A^\top e_i) = -2 \operatorname{tr}\!\big(A\, B^\top \operatorname{diag}(z)\big).$$
  This vanishes for all $A \in \mathfrak{so}(n)$ iff $B^\top \operatorname{diag}(z)$ is symmetric. Since $B = L - 2I$ and $2 \operatorname{diag}(z)$ is already symmetric, $B^\top \operatorname{diag}(z)$ is symmetric iff $\operatorname{diag}(z) L$ is symmetric, i.e. iff $z \in Z_B$. *(At $n = 2$, orthogonality against $u_{\mathrm{flex}}$ imposes the extra constraint $\sum_i (-1)^{i-1} z_i \ell_i \cdot (-2 e_i) = 0 \iff z_1 (L_{11}-2) = z_2 (L_{22}-2)$.)*
- **Step 4 (Affine virial identity kills all intra-cell self-stresses).** For any symmetric strain $E \in \operatorname{Sym}_n(\mathbb{Q})$, let $u^{\mathrm{aff}}_v = E x_v$. On every intra-cell bar $(u,v)$, $\ell_b = x_v - x_u$ gives $(d_0^{\mathrm{intra}} u^{\mathrm{aff}})_b = \ell_b^\top E \ell_b = (a_e^{\mathrm{intra}} E)_b$. On inter-cell bar $i$, $x_{2i+1} - x_{2i} = \ell_i - L_i$ gives $(d_0^{\mathrm{inter}} u^{\mathrm{aff}})_i = (a_e^{\mathrm{inter}} E)_i - \ell_i^\top E L_i$. Pairing with ANY global self-stress $\omega = (\omega_{\mathrm{intra}}, z) \in \ker(d_0^\top)$ cancels $\langle \omega, d_0 u^{\mathrm{aff}} \rangle = \langle d_0^\top \omega, u^{\mathrm{aff}} \rangle = 0$, leaving:
  $$\langle a_e^\top \omega,\, E \rangle = \sum_{i=1}^n z_i\, \ell_i^\top E L_i = \operatorname{tr}\!\big(E\, L^\top \operatorname{diag}(z) B\big).$$
  In particular, every pure intra-cell self-stress ($z = 0$) has identically zero virial tensor, and $\sigma(\omega) = \operatorname{sym}(L^\top \operatorname{diag}(z) B)$ depends ONLY on $z \in Z_B$.
- **Step 5 (Automatic symmetry & exact kernel on $Z_B$).** For every $z \in Z_B$, we have $L^\top \operatorname{diag}(z) = \operatorname{diag}(z) L$, whence
  $$L^\top \operatorname{diag}(z) B = \big(L^\top \operatorname{diag}(z)\big)(L - 2I) = \operatorname{diag}(z) L(L - 2I),$$
  AND simultaneously
  $$L^\top \operatorname{diag}(z)(L - 2I) = \underbrace{L^\top \operatorname{diag}(z) L}_{\text{always symmetric}} - 2 \underbrace{\operatorname{diag}(z) L}_{\text{symmetric on } Z_B}$$
  is **automatically symmetric**! Hence $\sigma(z) = \operatorname{diag}(z) M$ identically on $Z_B$ where $M \triangleq L(L-2I)$. Clearly $\operatorname{diag}(z) M = 0 \iff (z_i = 0 \text{ whenever row } i \text{ of } M \ne 0)$. Applying rank-nullity to $\sigma|_{Z_B}$ gives $\operatorname{rank}(S_{\mathrm{el}}) = \operatorname{rank}(\sigma|_{Z_B}) = \dim Z_B - \dim \ker(\sigma|_{Z_B})$. $\square$

### Certified Pure-$\mathbb{Q}$ Witnesses (`unification_bridge_certificate.json`, Pillar 3)

| Case | $n$ | Intra Motions / Rigid | $\dim Z_B$ | Nonzero Rows of $L(L-2I)$ | `G5-07` Formula | Actual $\operatorname{rank} S_{\mathrm{el}}$ | Result |
|---|---|---|---|---|---|---|---|
| `n3_diag_3_2_2` | 3 | `6 / 6` (rigid) | 3 | `[0]` | `1` | `1` | Exact match (refutes naive $\operatorname{rank} = \dim Z_B$) |
| `n3_low_tri_2` | 3 | `6 / 6` (rigid) | 1 | `[1, 2]` | `0` | `0` | Exact match (nonzero $Z_B$ killed by row support) |
| `n3_two_I` | 3 | `6 / 6` (rigid) | 3 | `[]` | `0` | `0` | Exact match ($L(L-2I) \equiv 0$) |
| `n3_nonsym_symmetrizable` | 3 | `6 / 6` (rigid) | 1 | `[0, 1, 2]` | `1` | `1` | Exact match (non-symmetric $L$, $z=(6,3,2)$) |
| `n4_D4_upper` | 4 | `10 / 10` (rigid) | 1 | `[0, 1, 2, 3]` | `1` | `1` | Exact match (4D $D_4$ fold lattice) |
| **`n2_sharpness_diag_3_2`** | **2** | **`4 / 3` (1 flex!)** | 2 | `[0]` | `1` | **`0`** | **Sharp counterexample: $n \ge 3$ is necessary!** |
| **`n2_sharpness_diag_3_3`** | **2** | **`4 / 3` (1 flex!)** | 2 | `[0, 1]` | `2` | **`1`** | **Sharp counterexample: square flex forces $z_1 = z_2$!** |

---

## 7. Honest Upgrade of `SF-01` ("30-Way Schur Unification") into Strict Mechanism Classes vs. Verified Morphisms (Pillar 4)

Auditing `structural_fingerprints.json` `SF-01` directly at Round 9 HEAD reveals:
- **Exact Count Drift Caught Honestly:** The `SF-01` array contains **`29` entries**, NOT `30` (prose labels `#26..#30` inside `label_stripped` / `ref` drifted by `+2/+3` relative to the JSON array length).
- **Exact Partition into 4 Strict Mechanism Classes (`23 QH + 4 QN + 0 T + 2 L = 29`):**
  - **`QH` (`23` entries):** Hermitian/symmetric quadratic Schur where Haynsworth inertia applies — by Gate 5, shared membership in `QH` is a **mechanism taxonomy**, NOT a discriminating cross-domain unification invariant.
  - **`QN` (`4` entries):** Non-Hermitian / non-normal operator Schur where Haynsworth inertia is **undefined**: `#3` `Foundation-0/fractals` (`AUDIT-018` GKSL Lindblad), `#18` `judegomila/canculus` (`AUDIT-050` asymmetric feedback loop `S = 1 + alpha*g*h` — missed as `QN` in `cave-expedition#5`!), `#21` `Foundation-0/continuum#3` (`AUDIT-054` 16×16 GKSL), and `#28` `ShivamDuggal4/latent-lattice-language-models` (`AUDIT-072R` non-normal 2D block Schur `S_J0`).
  - **`T` (`0` entries in `SF-01` JSON; `1` entry in README/Portal-10 8-row table):** Tropical `(min,+)` infimal projection — no additive inverse; linked to algebraic `Q[q]` elimination ONLY via Theorem A (`M3`).
  - **`L` (`2` entries):** Label-only / non-elimination entries (`#5` `Moissanite-Labs/heedle`, `#7` `anthropics/jacobian-lens`) — should be separated from literal block-Schur lists.
- **3 Genuinely Verified Gate-5 Cross-Domain Morphisms (What Survives as Real Unification):**
  1. **`M1` (`AUDIT-017 <-> AUDIT-019`):** Exact block-upper-triangular congruence $H_{\mathrm{el}} = \Phi^\top H_{\mathrm{lat}} \Phi \implies S_{\mathrm{el}} = R_L^\top S_{\mathrm{lat}} R_L$ (confirmed in `cave-expedition#5` `G5-05`), now completed by Theorem B (`G5-07` universal proof + $n=2$ sharpness).
  2. **`M2` (`AUDIT-064 WI-4 <-> AUDIT-079R RIPO-FS-04`):** Exact Fisher-Schur simplex pullback $F_p = (J_p U)^\top \operatorname{diag}(1/p)(J_p U) = \operatorname{diag}(9/4, 49/2, 0)$ (verified exact in Pillar 4 for $p = (1/2, 1/4, 1/4)$, unobserved in Round-1-only `cave-expedition#5`).
  3. **`M3` (`Q[q] Schur <-> (min,+) Kleene Star`):** Exact valuation–cancellation-gap functor $\operatorname{val}(S_{ij}) \ge T_{ij}$ with exact iff equality $L_{ij} \ne 0$ and measurable gap $\Delta_{\mathrm{cancel}}$ (Theorem A, closing `G5-10` & `G5-13`).

---

## 8. Fail-Closed Gate-5 Certifier (`Pillar 5`) & Verification Ledger

`certify_unification_bridge_hardened` and `verify_pinned_digests` operationalize Gate 5, Theorem A, and staged-manifest integrity fail-closed in pure $\mathbb{Q}$, enforcing exact refusal codes on every invalid or overclaimed input:
- `ERR_INVALID_CLASS`, `ERR_INVALID_INVARIANT`, `ERR_INVALID_BOOL` (strict type & vocabulary guards),
- `ERR_INVALID_MANIFEST`, `ERR_INVALID_DIGEST_TYPE`, `ERR_INVALID_DIGEST_FORMAT`, `ERR_EXTRA_DIGEST_KEY`, `ERR_MISSING_DIGEST`, `ERR_DIGEST_MISMATCH`, `ERR_STAGED_ROOT_MISSING`, `ERR_STAGED_FILE_MISSING` (strict live 12-file SHA-256 verification rejecting raw floats, non-str entries, malformed hex, extra/missing keys, or disk tampering),
- `ERR_INCOMPLETE_BRIDGE_DATA`, `ERR_NON_EXACT_RATIONAL`, `ERR_NONSYMMETRIC_QH_MATRIX` (unconditional validation whenever `k_poly`/`part_a`/`part_b` are supplied — even when `tropical_bridge_*` is not claimed — rejecting raw IEEE-754 floats, partial arguments, singular pivots, and asymmetric `QH` matrices),
- `ERR_LABEL_ONLY_UNBUILT` (refuses any operator invariant on class `L`),
- `ERR_TAXONOMY_CONFLATED_WITH_UNIFICATION` (refuses `claim_cross_domain_unification=True` without `explicit_morphism_provided=True`),
- `ERR_INERTIA_UNDEFINED_FOR_CLASS` (refuses `haynsworth_inertia` on `QN` or `T`),
- `ERR_NO_ADDITIVE_INVERSE_IN_TROPICAL` (refuses `additive_schur` or `schur_exists` on `T`),
- `ERR_MISSING_BRIDGE_DATA`, `ERR_SINGULAR_PIVOT`, `ERR_NONREGULAR_PIVOT_CONSTANT_TERM` (refuses $\operatorname{val}(K_{BB}) = 0$ on tropical bridge),
- `ERR_CANCELLATION_DEFECT_NONZERO` (refuses `tropical_bridge_exact` whenever $L_{ij} = 0$, while `tropical_bridge_bound` certifies exact `max_finite_gap` and `annihilated_pairs`).

### Verification & Reproducibility Summary

| Gate | Command / Check | Result |
|---|---|---|
| Exact Live Certificate | `python3 -I -B -W error unification_bridge_audit.py --write-cert` | `mode = live`, `disk_io_performed = true`, `12/12` staged SHA-256s live-verified, `all_pillars_verified = true`, `canonical_sha256 = c1ce29d8b38ce831828a6d53a4e9ef2a4bc7e315b33f0087baacb5b91bf83f44` |
| R4 Live Determinism (`4/4`) | `-I -B`, `-I -O -B`, `-I -B -W error`, saved JSON | `4/4` bit-identical SHA-256: `a662374cdb5e08adab3323477584b155ce92dbdbcb54e45871d354fccaf17642` |
| R4 Standalone Determinism (`3/3`) | `-I -B --standalone`, `-I -O -B --standalone`, `-I -B -W error --standalone` | `3/3` bit-identical SHA-256: `86dc7577334bc121defbb20f7f647b3853302b760c6e9ae3d7e8021df938eaba` (`canonical_sha256 = b8e0ec60d0c24711ec66fcc05ea2dd4e7d5f77360f99d26232e57b5d3b303b13`, `disk_io_performed = false`) |
| R5 Test Suite | `python3 -I -O -B -W error test_r5_unification_bridge.py` | `ALL_R5_TESTS_PASSED` (`stdout_sha256 = c1cf4f1bcaeb1c864ba254d13b592c8043960ce8fc551ffd469b7d5564938672`) |
| Aletheia Hygiene | `aletheia v1.4.0 audit-check . --strict-ancestors --scripts unification_bridge_audit.py test_r5_unification_bridge.py` | `PASS` (`4` files, `0` CRLF, `0` pycache, `0` leaks, `0` bare asserts, `2/2` R4, `ancestor_permissions: passed: true`) |
| R5 Mutation Gate | `aletheia v1.4.0 mutate unification_bridge_audit.py --add-cwd --work-root . --test-cmd "python3 -I -O -B -W error test_r5_unification_bridge.py"` | **`38/38` KILLED (`100.0%`, `0` survivors)** |
| Staged Portal Pinning | Live `compute_staged_digests_from_root` + `verify_pinned_digests` executed on default CLI run | `12/12` exact SHA-256 match against Round 10 read-only staging (`aletheia#2`, `aletheia#4`, `cave-expedition#4`, `cave-expedition#5`, `structural_fingerprints.json`, `ROUND10_PORTALS.md`) |

### Law-4 Quarantine & Scope Limits
- **No `N2` claim is made in `AUDIT-085`.** Every known prior-art mechanism (`R10-N0-01`..`R10-N0-12`) remains explicitly quarantined as `N0`.
- **Theorems A and B are classified honestly as `N1`:** elementary, exact, self-contained pure-$\mathbb{Q}$ proofs closing the `3/3` unproved `PARTIAL` claims (`G5-07`, `G5-10`, `G5-13`) of `cave-expedition#5` together with sharp necessity counterexamples (`R5` negative gap `-1` and `n=2` square flex).
- **Read-only Phase 2 boundary respected:** Zero GitHub writes, comments, PRs, or modifications outside this arm's output directory.
