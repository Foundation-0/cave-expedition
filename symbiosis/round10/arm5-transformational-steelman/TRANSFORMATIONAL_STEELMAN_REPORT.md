# Wave 2 Round 10 — Arm R10-5 (`AUDIT-088`): Transformational Steelman / Morphism-Before-Dismissal Protocol (`LAW2B_TRANSFORM_BEFORE_DISMISSAL`)

- **Arm / Owner:** Arm R10-5 (`gravity-probe`), Wave 2 Round 10 (`AUDIT-088`)
- **Mandate & Epistemic Architecture:** Formalizes the user's structural/mathematical twin to `Foundation-0/aletheia#9` (`spec/proposals/OWN_TERMS_FIRST.md`):
  > *"some abstract thinking and manipulations should be applied to theorems before being dismissed as inaccurate. it might be that is it touching on something real but needs some transformation to fit."*
  Just as `OWN_TERMS_FIRST` prevents premature dismissal of raw empirical patterns before Phase-1 testing, **Law 2b (`LAW2B_TRANSFORM_BEFORE_DISMISSAL`)** prevents premature `FALSIFIED` rulings on formal claims by requiring an explicit search across **7 typed admissible morphism families ($\mathcal{T}_1..\mathcal{T}_7$)** BEFORE closing a theorem as false — paired with **4 fail-closed Law-3 anti-epicycle guards (`G1..G4`)** that cleanly separate genuine structural rescues from post-hoc rationalization.
- **Oracle Class & Honest Law-4 Novelty Tag:** `exact+anchor` (100% pure Python 3 stdlib `int`/`Fraction`, **ZERO floats** anywhere in code or JSON, **ZERO external deps**, **ZERO bare `assert`s**) | **`N1`** (formal Law-2b protocol + fail-closed zero-float 7-family certifier `certify_transformational_steelman` + pure-$\mathbb{Q}$ retrospective re-audit across `AUDIT-001`–`087` surfacing two previously unrecorded transformed cores in `AUDIT-023` `CS-08` and `AUDIT-080R` Zhihu `L112`, contrasted against exact transform-invariant obstructions and anti-epicycle rejections; all classical mathematical morphisms & prior verified vault audits strictly quarantined under `N0`).
- **Pinned Read-Only Vault Anchors (`8/8` SHA-256 + `8/8` Verbatim 1-Based Line Anchors Verified, `0` GitHub Writes):**
  - `round10/portals/aletheia/pr_9_files/spec/proposals/OWN_TERMS_FIRST.md` (`sha256: bd148633...`, lines `21`, `44`)
  - `round10/portals/aletheia/issue_4.md` (`sha256: e3da52ef...`, lines `31`, `66`)
  - `round10/portals/cave-expedition/pr_5_files/verification/outside/gate5-unification/README.md` (`sha256: 7e8fa8e1...`, line `59`)
  - `round10/portals/cave-expedition/pr_6_files/verification/outside/continuum-four-transformations/PREREG.md` (`sha256: 8ed03fb9...`, lines `85`, `86`, `163`)
  - Frozen `VERIFIED` vault certificates: `zenodo_rns_pnp_certificate.json` (`AUDIT-070R`, `eae51ad6...`), `songe_governance_certificate.json` (`AUDIT-073R`, `479e137e...`), `ripo_riemannian_certificate.json` (`AUDIT-079R`, `2ecbe3f0...`), `bpo_bellman_certificate.json` (`AUDIT-083R`, `4a666179...`).
- **Artifacts (`symbiosis/round10/arm5-transformational-steelman/`):**
  - [transformational_steelman_certifier.py](transformational_steelman_certifier.py) — Zero-float pure-$\mathbb{Q}$ Law-2b certifier, 8-file/8-line live anchor verifier (`--standalone` supported), and exact retrospective proofs across `T1..T7`, `OBS1..OBS3`, and `REJ1..REJ4`
  - [test_transformational_steelman_r5.py](test_transformational_steelman_r5.py) — Assertion-free `-I -O -B -W error` R1–R5 unit, boundary, adversarial red-team, and `100.0%` R5 mutation-kill test suite
  - [transformational_steelman_certificate.json](transformational_steelman_certificate.json) — Live-anchored zero-float canonical JSON certificate (`canonical_sha256: 89a603748228a825c42f54dabe4d6da68059f31b6513122c073f564eeaa03cf0`; live file SHA-256: `e21ceea368a945dfa1f6b6d6152714e8b2ae7df5191620f3ef37436696eb21a6`; standalone SHA-256: `54d07116cf2d9ece84c4217083ce29c4c404f668d3905ded33eafc97573870ef`)
  - [TRANSFORMATIONAL_STEELMAN_REPORT.md](TRANSFORMATIONAL_STEELMAN_REPORT.md) — This report (including concrete drop-in draft section for `aletheia v1.5.0 / v2.0`)

---

## 1. Strict Law-4 `N0` Prior-Art Quarantine Table (`R10-N0` Aligned)

| Quarantine ID | Established Prior Art / Upstream Artifact (`N0`) | Role in `AUDIT-088` |
|---|---|---|
| `R10-5-N0-01` | Lakatos (1976) *Proofs and Refutations* (monster-barring vs. lemma-incorporation), Popperian falsifiability, principle of charity (`aletheia#3` §9), and statistical degrees-of-freedom / overfitting bounds | Philosophical & statistical foundations of Law 2b & anti-epicycle guards |
| `R10-5-N0-02` | Classical matrix & functional morphisms: diagonal similarity ($D^{-1} M D$), Bregman divergences (1967), Hellinger / Fisher–Rao charts (Amari 1998), shifted lazy-walk adjacency ($A_0 + d_{\max}I$), Maslov tropicalization (`R10-N0-10`), orthogonal subspace projection, mid-rank order statistics, and principal stratification (Frangakis–Rubin 2002) | The 7 mathematical morphism families ($\mathcal{T}_1..\mathcal{T}_7$) |
| `R10-5-N0-03` | Prior verified expedition audits (`AUDIT-004`, `AUDIT-008R`, `AUDIT-023`, `AUDIT-070R`, `AUDIT-073R`, `AUDIT-079R`, `AUDIT-080R`, `AUDIT-083R`, `AUDIT-085`, `AUDIT-087`) and outside review portals (`aletheia#4`, `aletheia#9`, `cave-expedition#5/#6`) | Frozen retrospective re-audit corpus & verbatim anchors |

---

## 2. Formal Law-2b Specification: 7-Family Morphism Taxonomy & 4 Anti-Epicycle Guards

### 2.1 The 7 Typed Admissible Morphism Families ($\mathcal{T}_1..\mathcal{T}_7$)

| Family ID | Morphism Class | Canonical Operator Form | What Kind of Literal Failure It Rescues |
|---|---|---|---|
| **`T1_GAUGE_SIMILARITY`** | Gauge / Diagonal / Conjugacy Similarity | $M' = D^{-1} M D$ | Non-symmetric / non-stochastic coordinate presentation hiding an exact spectral invariant |
| **`T2_AFFINE_BREGMAN`** | Affine / Bregman Divergence Shift | $D_\phi(p\|q) = \phi(p) - \phi(q) - \langle \nabla\phi(q), p-q\rangle$ | Missing linear tangent / normalization term causing sign reversal or Gibbs violation |
| **`T3_METRIC_CHART`** | Metric / Coordinate Chart Reparametrization | $\psi: \Delta \to \mathcal{M}$ (e.g., $\sqrt{p}$ Hellinger / Bernoulli-$\chi^2$) | Boundary dead zones or simplex overflow under Euclidean ratio clipping |
| **`T4_SPECTRAL_PSD_SHIFT`** | Spectral / PSD Regularization Shift | $A \mapsto A + \lambda I \succeq 0$ | Negative-eigenvalue squaring inversion destroying spectral ordering |
| **`T5_SEMIRING_TROPICAL`** | Semiring / Tropicalization / Dequantization | $\mathbb{Q}((q)) \to (\min, +)$ with cancellation gap $\Delta_{\mathcal{T}}$ | Cross-kind algebraic-vs-tropical mismatch when signed walks cancel |
| **`T6_SUBSPACE_PROJECTION`** | Subspace / Quotient / Dual / Complementary Projection | $P_V$, $1 - \pi$, or paired principal stratum | Mixed symmetry sectors (time-even diluting time-odd) or post-treatment collider bias |
| **`T7_ORDER_DOMAIN_RESIDUAL`** | Monotone Order-Chart & Exact Domain-Residual Decomposition | Mid-rank $\operatorname{rk}(x)$; $\Omega_{\mathrm{valid}} \sqcup \Omega_{\mathrm{valid}}^c$ with exact $\Delta_{\mathcal{T}}$ | Amplitude-map leakage or universal sign claim valid on an exact inner-product cone |

### 2.2 Four Mandatory Law-3 Anti-Epicycle / Non-Degeneracy Guards (`G1..G4`)

`certify_transformational_steelman(spec)` enforces strict exact-key schema, printable trimmed ASCII strings, duplicate-free `families_searched`, an immutable null false-pass ceiling **`MAX_ALLOWED_NULL_RATE = 1/10`**, and four fail-closed guards:

- **Guard G1 (Non-Vacuity & Null Discrimination):** Rejects rank-0 / zero-projection maps (`transform_rank < 1` $\to$ `G1_DEGENERATE_ZERO_RANK_TRANSFORM`), failing transformed targets (`target_pass_count < target_total_count`), vacuous maps whose null false-pass rate exceeds `max_null_false_pass_rate <= 1/10` (`G1_VACUOUS_NULL_DISCRIMINATION_FAILED`, enforced across all verdicts), and under-resolved rescue null suites (`max_null_rate > 0 and null_total * max_null_rate < 1` $\to$ `G1_INSUFFICIENT_NULL_RESOLUTION`).
- **Guard G2 (Global Scope & Degrees-of-Freedom Budget):** Rejects per-instance post-hoc patching (`fixed_globally_before_holdout == False` $\to$ `G2_POST_HOC_PER_INSTANCE_PATCHING`, enforced across all verdicts) and over-parameterized polynomial epicycles (`transform_dof >= held_out_constraints` $\to$ `G2_OVERPARAMETERIZED_EPICYCLE_DOF`).
- **Guard G3 (Explicit Scope-Delta Ledger — Zero Silent Goalpost-Moving):** Always refuses `relabelled_as_literal == True` (`G3_SILENT_GOALPOST_MOVING`); requires non-empty `preserved_invariant_core` and `modified_hypotheses` (`G3_INCOMPLETE_SCOPE_DELTA_LEDGER`), exact `residual_gap == 0` AND `max_residual_gap == 0` for `TRANSFORMED_EXACT`, and `0 < residual_gap <= max_residual_gap` for `BOUNDED_TRANSFORM_CORE`.
- **Guard G4 (Transform-Invariant Obstruction Gate for True `FALSIFIED`):** Unconditionally refuses raw dismissal (`FALSIFIED_RAW` $\to$ `G4_PREMATURE_FALSIFIED_NO_MORPHISM_GATE`). Certifies `INVARIANT_FALSIFIED` ONLY when **all `7/7` distinct morphism families** have been searched (`G4_INSUFFICIENT_MORPHISM_SEARCH`), no rescue family is applied, no contradictory rescue fields (`preserved_invariant_core`, `modified_hypotheses`, `transform_rank != 0`, `transform_dof != 0`) or zero gap (`residual_gap == 0`) are present (`G4_CONTRADICTORY_RESCUE_FIELDS_ON_FALSIFIED`, `G4_FALSIFIED_HAS_ZERO_GAP`), at least one target genuinely fails (`target_pass < target_total`), and an explicit `obstruction_invariant` survives every searched family (`obstruction_survives_all_searched == True`). Symmetrically rejects contradictory obstruction metadata on rescue verdicts (`G0_CONTRADICTORY_OBSTRUCTION_ON_RESCUE`).

---

## 3. Retrospective Pure-$\mathbb{Q}$ Re-Audit of the Expedition Vault (`AUDIT-001`–`087`)

### 3.1 Seven Certified Structural Rescues Across All 7 Families (Including 2 Newly Surfaced Vault Cores!)

| Family & Vault Case | Literal Failure Witness (Exact Pure-$\mathbb{Q}$) | Admissible Morphism $\mathcal{T}$ & Preserved Core | Law-2b Verdict & Certifier Status |
|---|---|---|---|
| **`T1` — `AUDIT-008R / AUDIT-004` (`Q[q]` `issue_4.md:31`)** | Diagonal conjugate $K' = D^{-1} K D = \begin{pmatrix}1/2 & 1 \\ 1/4 & 1/2\end{pmatrix}$ (from $K = \begin{pmatrix}1/2 & 1/2 \\ 1/2 & 1/2\end{pmatrix}, D = \operatorname{diag}(1,2)$) has non-stochastic row sums **`[3/2, 3/4] != [1, 1]`** (NOT a classical Doob $h$-transform!) | Relabelling to diagonal gauge similarity $D^{-1} K D$ preserves exact characteristic polynomial ($\operatorname{tr} = 1, \det = 0$) and max-times row-0 peak (`1/1`) | **`CERTIFIED_TRANSFORMED_EXACT`** (`gap = 0/1`) |
| **`T2` — `AUDIT-073R` (`songe` `SNG-01`)** | At $p = 1/2, q = 1/64, c = 2$, ratio-clipped quadratic KL reverses logit gradient to **`+1/504 > 0`** (anti-teacher) | Bregman affine normalization restores teacher-aligned **`-496/63 < 0`** (forward KL **`-31/64 < 0`**), Gibbs $\ge 0$ | **`CERTIFIED_TRANSFORMED_EXACT`** (`gap = 0/1`) |
| **`T3` — `AUDIT-079R` (`RIPO`)** | At $\delta = 1/20$, raw RIPO hits negative lower bound **`-1`** ($p=1/80$) AND simplex overflow **`q_max = 1`** ($p=4/5$) | Symmetric Bernoulli-$\chi^2$ chart gives exact interior `[18/25, 22/25]` at $\delta = 1/50$ and simplex edge distance **`1/8 > 1/20`** at $p = 4/5$ | **`CERTIFIED_TRANSFORMED_EXACT`** (`gap = 0/1`) |
| **`T4` — `AUDIT-070R` (Zenodo Pillar B `Teorema 3.2`)** | On $G_{10} = K_{4,4} \cup \{(7,8)\} \cup K_2$, exact Bunch–Kaufman congruence gives `inertia(A-3I) = (1,9,0)` & `inertia(A+3I) = (9,1,0)` $\implies \lambda_{\min}^2 > 9 > \lambda_2^2$ | Spectral shift $A_0 + 5I$ yields exact inertia **`(10, 0, 0)`** (strictly PD, eliminating squaring inversion; `N0` lazy walk, does not touch `P=NP`) | **`CERTIFIED_TRANSFORMED_EXACT`** (`gap = 0/1`) |
| **`T5` — `AUDIT-085` (Thm A & `OWN_TERMS_FIRST:44`)** | Signed Laurent walk $(+1)q^2 + (-1)q^2 + (+1)q^3 = q^3$ shifts valuation `val_S = 3 != 2 = T_trop` | Cross-kind algebraic–tropical bridge: exact `gap = 0` when cancellation-free (`2q^2`), measurable **`gap = 1`** under cancellation | **`CERTIFIED_BOUNDED_TRANSFORM_CORE`** (`gap = 1/1`) |
| **`T6` — `AUDIT-083R` (BPO) + `AUDIT-087` (`PREREG-02`) + *NEWLY SURFACED `AUDIT-023` (`CS-08`)* (`issue_4.md:66`)** | (i) Raw `PREREG-02` `T3` mixes `20` time-even (`+1`) & `10` time-odd (`-1`) $\to$ `+1/3` dilution; (ii) Raw `CS-08` strata fail Simpson (`-16/2881`, `-1/14`, `-2/25`, all `< 0`) | (i) BPO $1-\pi \equiv$ Top-1 SC (`50/1`, Jacobian cancels to $2(1-\mu) = 1/1$); (ii) Odd subspace restores **`-1/1`**; (iii) **Newly surfaced `CS-08` core:** projecting onto the `66` paired clean instances (`issue_4.md:66`) flips sign to **`44/66 - 43/66 = +1/66 > 0`** (causal mediation core!) | **`CERTIFIED_BOUNDED_TRANSFORM_CORE`** (`gap = 1/66`) |
| **`T7` — `AUDIT-087` (`PREREG-03`) + *NEWLY SURFACED `AUDIT-080R` (Zhihu `L112`)* ** | (i) Raw end-matching flips offset `0 -> 2` under $x^3 + x$; (ii) Zhihu `L112` fails at `A=(3,-1)` (`delta_L2^2 = +1/8 > 0`) | (i) Exact mid-rank chart keeps `offset = 0` identically; (ii) **Newly surfaced `L112` core:** exact Pythagorean identity $\|e_{\mathrm{SC}}\|_2^2 - \|e_{\mathrm{off}}\|_2^2 = -(\|d\|_2^2 + 2\langle e_{\mathrm{SC}}, d\rangle)$ proves strict bias reduction (`-1/8 < 0`) across the entire explicit cone $\Omega_{\mathrm{valid}} = \{2\langle e_{\mathrm{SC}}, d\rangle + \|d\|_2^2 > 0\}$! | **`CERTIFIED_BOUNDED_TRANSFORM_CORE`** (`gap = 1/8`) |

### 3.2 Three Certified Transform-Invariant Obstructions (`INVARIANT_FALSIFIED` After Exhaustive `7/7` Family Search)

| Obstruction Case | Exact Pure-$\mathbb{Q}$ Witness Computed From Scratch | Transform-Invariant Obstruction Surviving All `7/7` Families | Certifier Status |
|---|---|---|---|
| **`OBS1` — `AUDIT-070R` Pillar A (Tseitin-$K_4$ 3-SAT)** | Brute-force enumeration over `16` 3-clauses on `{0,1}^6`: `b=0` has `8` models (`SAT`), `b=1` has `0` models (`UNSAT`), YET $W_{\mathrm{SAT}} = 8 I_6 = W_{\mathrm{UNSAT}}$ and $\mathbf{1}^\top B_{\mathrm{SAT}} = \mathbf{0} = \mathbf{1}^\top B_{\mathrm{UNSAT}}$ | **Data-processing invariant:** identical observable `(8 I_6, 0)` maps to opposite `SAT`/`UNSAT` truths ($\mathbb{Z}_2$ cohomology `0 != 1`) under EVERY transform of `(W, 1^T B)` | **`CERTIFIED_INVARIANT_FALSIFIED`** (`7/7` families) |
| **`OBS2` — `AUDIT-070R` Pillar C (`Teorema 4.1` TSP)** | Exhaustive enumeration of all `12` undirected 5-tours on `{(0,0),(0,8),(-15,0),(15,0),(0,8008)}` ($\sigma_0 = 1000$): `best_without_01 = 16055 < 16056 = best_with_01` (`penalty >= +1` for all $M > 8$) | **Unbounded isolation invariant:** $\sigma_0 = (M-8)/8 \to \infty$ outruns every finite threshold rescaling $\tau \mapsto \mathcal{T}(\tau)$ while keeping `(0,1)` strictly suboptimal | **`CERTIFIED_INVARIANT_FALSIFIED`** (`7/7` families) |
| **`OBS3` — `AUDIT-073R` `SNG-02` ($n=1$ Bootstrap)** | Singleton sample `[1]` has exact variance `0/1`, per-scale null false-accept `1/2`, and 2-scale FWER **`3/4`** | **Rank-0 sample-cardinality invariant:** no scalar transform creates non-zero variance from $n = 1$ observation | **`CERTIFIED_INVARIANT_FALSIFIED`** (`7/7` families) |

### 3.3 Four Fail-Closed Anti-Epicycle Rejections (`G1..G4`)

| Rejection Witness | Adversarial Violation | Exact Refusal Codes Returned by `certify_transformational_steelman` |
|---|---|---|
| **`REJ1` (Zero-Rank Projection)** | `transform_rank = 0`, `null_false_pass = 10/10` | `G1_DEGENERATE_ZERO_RANK_TRANSFORM`, `G1_VACUOUS_NULL_DISCRIMINATION_FAILED` |
| **`REJ2` (Over-Parameterized Poly Fudge)** | `fixed_globally_before_holdout = False`, `transform_dof = 6 >= 5 = held_out_constraints` | `G2_POST_HOC_PER_INSTANCE_PATCHING`, `G2_OVERPARAMETERIZED_EPICYCLE_DOF` |
| **`REJ3` (Silent Goalpost-Moving)** | `relabelled_as_literal = True`, `modified_hypotheses = None` | `G3_SILENT_GOALPOST_MOVING`, `G3_INCOMPLETE_SCOPE_DELTA_LEDGER` |
| **`REJ4` (Premature Dismissal)** | `INVARIANT_FALSIFIED` after searching only `1/7` families with `obstruction_invariant = None` | `G4_INSUFFICIENT_MORPHISM_SEARCH`, `G4_MISSING_TRANSFORM_INVARIANT_OBSTRUCTION`, `G4_OBSTRUCTION_NOT_INVARIANT_ACROSS_FAMILIES` |

---

## 4. Concrete Drop-In Draft Section for `Foundation-0/aletheia v1.5.0 / v2.0` (`LAWS_AND_GATES.md` Integration)

The section below is drafted to sit directly alongside `spec/proposals/OWN_TERMS_FIRST.md` (`aletheia#9`) and `R6`/`R7` (`aletheia#3`, `AUDIT-086`) — ready for user approval in Phase 3 (ZERO GitHub writes made here):

```markdown
### Law 2b — Transformational Steelman (Morphism Before Dismissal)

**Scope & Symmetry with `OWN_TERMS_FIRST`:**
- `OWN_TERMS_FIRST` (Phase 1 / Phase 2 separation) protects *empirical raw-data patterns* from premature dismissal via borrowed literature labels.
- **Law 2b (`LAW2B_TRANSFORM_BEFORE_DISMISSAL`)** is its exact structural twin for *formal theorems, identities, and algorithms*: before ruling a literal failure `FALSIFIED`, the verifier MUST test whether an admissible, globally fixed mathematical transformation $\mathcal{T} \in \{\mathcal{T}_1..\mathcal{T}_7\}$ rescues an invariant core — while enforcing Law 3 anti-epicycle guards (`G1..G4`).

**Composition with `R6`/`R7` and `OWN_TERMS_FIRST`:**
1. **R6 Pre-Pinning:** Any candidate transformation family $\mathcal{T}_k$ and its exact parameter budget (`transform_dof`) MUST be fixed globally before opening held-out verdict data (`G2` + `R6`).
2. **R7 Measured-Residual Accounting:** If $\mathcal{T}$ rescues the claim up to a bounded gap $\Delta_{\mathcal{T}} > 0$ (`BOUNDED_TRANSFORM_CORE`), the gap MUST be measured cleanly on held-out controls (`G3` + `R7`), never silently absorbed into the original wording.
3. **Exhaustive Obstruction Rule for `FALSIFIED`:** A final `FALSIFIED` verdict requires an `INVARIANT_FALSIFIED` certificate proving a concrete obstruction invariant that survives all `7/7` admissible morphism families (`G4`).
```

---

## 5. Exact Reproduction Receipts (`aletheia v1.4.0`)

```bash
# 1. 4-mode isolated -I R4 test suite (12/12 tests OK in all 4 modes)
for f in "-I -B" "-I -O -B" "-I -B -W error" "-I -O -B -W error"; do
  PYTHONDONTWRITEBYTECODE=1 python3 $f test_transformational_steelman_r5.py
done

# 2. 4-mode isolated -I bit-identical live & standalone JSON certificates
for f in "-I -B" "-I -O -B" "-I -B -W error" "-I -O -B -W error"; do
  PYTHONDONTWRITEBYTECODE=1 python3 $f transformational_steelman_certifier.py --json | sha256sum
  PYTHONDONTWRITEBYTECODE=1 python3 $f transformational_steelman_certifier.py --standalone --json | sha256sum
done
# Live JSON (4/4):       e21ceea368a945dfa1f6b6d6152714e8b2ae7df5191620f3ef37436696eb21a6
# Standalone JSON (4/4): 54d07116cf2d9ece84c4217083ce29c4c404f668d3905ded33eafc97573870ef
# Canonical SHA-256:     89a603748228a825c42f54dabe4d6da68059f31b6513122c073f564eeaa03cf0

# 3. Aletheia v1.4.0 R5 AST Mutation Gate (55/55 = 100.0% KILLED, 0 survivors)
PYTHONPATH=../../../publish/aletheia python3 -m aletheia mutate \
  transformational_steelman_certifier.py --work-root . --max-mutants 0 \
  --test-cmd "python3 -I -O -B -W error test_transformational_steelman_r5.py" --add-cwd --json

# 4. Aletheia v1.4.0 Strict Ancestor Hygiene & R4 Audit Check (PASS, 0 defects)
PYTHONPATH=../../../publish/aletheia python3 -m aletheia audit-check . \
  --strict-ancestors --scripts transformational_steelman_certifier.py test_transformational_steelman_r5.py --json
```
