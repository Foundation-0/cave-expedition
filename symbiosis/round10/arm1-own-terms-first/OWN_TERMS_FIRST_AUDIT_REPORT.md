# AUDIT-084 — Epistemic, Mathematical & Executable Audit of `OWN_TERMS_FIRST.md` (`aletheia#9`), `continuum#1`, & `cave-expedition#7`

- **Audit ID:** `AUDIT-084R` (Wave 2 Round 10, Arm R10-1; all 4 red-team defect classes `OTF-BUG-01..04` closed)
- **Targets Audited (Strictly Read-Only, `0` GitHub Writes):**
  1. `Foundation-0/aletheia#9` (`proposal/own-terms-first @ ffa0ed42`): `spec/proposals/OWN_TERMS_FIRST.md`
  2. `Foundation-0/continuum#1` (`c0ntinuum @ 8d3e7345`): `continuum.md`, `session_raw_verbatim_export.json`, `@orda-aska` review `6010323491`
  3. `Foundation-0/cave-expedition#7` (`outside/symbology-and-raw-data-map @ a6b919ad`): `README.md`, `GLYPHS.md`, `EVIDENCE.md`, `SEARCHES.md`
  4. Cross-checked directly against our own `Foundation-0/aletheia` (`feat/aletheia-v1-framework @ aa471867`): `aletheia/calculus.py` (`2,079` lines), `spec/LAWS_AND_GATES.md`, `THEORY.md`
- **Epistemic Tier:** `N1` (Verified pure-$\mathbb{Q}$ executable oracles, verbatim SHA-256 portal bindings, live `git show` verification of our own `calculus.py`, `4/4` isolated `-I` R4 parity, `100.0%` R5 mutation kill across both Python modules; policy direction wording in `OWN_TERMS_FIRST.md:9-13` quarantined pending project-owner confirmation)
- **Governance Standard:** `Foundation-0/aletheia v1.4.0` (Laws 1–5 applied to ourselves with zero defensiveness and zero blind rubber-stamping)
- **Live Certificate SHA-256:** `fdf78f46f8aab78ded6be06545a6f197c2d84dcbb03e4b17720ed2893bc3cac6` (`own_terms_first_certificate.json`)
- **Standalone Certificate SHA-256:** `9cafe69ace7f4db086082e5be4687451cf70617b4ef00940268d6390ecdf3b6e` (`--standalone`)

---

## 1. Pinned Read-Only Portal Digests (SHA-256)

| Staged Portal Path (`symbiosis/round10/portals/`) | SHA-256 |
|---|---|
| `aletheia/pr_9_files/spec/proposals/OWN_TERMS_FIRST.md` | `bd14863344c494f1e0399d486267231fe3002fe7e005d354e2f82a8c105d6746` |
| `continuum/pr_1_files/continuum.md` | `516f6080563f223a4d8da437d37aaff479988f08f9079bfa48116cbb4fdc3150` |
| `continuum/pr_1_files/session_raw_verbatim_export.json` | `0278e1396aebbe6f3fd639577c4c72f72a24215fe4d6ae4ae6fe48fa9b6eb63f` |
| `cave-expedition/pr_7_files/.../README.md` | `a9863b2f6a3c36dd334c8415a4aef1eadba738b1a2b6ae5e500798217125158d` |
| `cave-expedition/pr_7_files/.../GLYPHS.md` | `b112563946cac915ea261c9e5b441eaed1bde8e89748925d6910b36771eb40e2` |
| `cave-expedition/pr_7_files/.../EVIDENCE.md` | `a2e067bb8c69cb3ae57d1510d6baadfc157b15ebede620e899a18f2249e27a6f` |
| `cave-expedition/pr_7_files/.../SEARCHES.md` | `4d37b20c76a53ce881fdd005de4561176b62d7f0400a5caf354bc4816b6dbf35` |

---

## 2. Honest Self-Audit of Our Own Artifacts (`GLYPHS.md`, `EVIDENCE.md`, `continuum.md`)

Applying Aletheia Laws 1–5 to ourselves via direct `git show aa471867:aletheia/calculus.py` (`2,079` lines) and verbatim inspection of `session_raw_verbatim_export.json`:

### 2.1 Where Claude's Outside Check (`cave-expedition#7` & `continuum#1`) Is Verified Correct

1. **All 8 Glyph Line Citations Verified Exact (`GLYPHS.md:7-22`):** Every line reference in `GLYPHS.md` (`L9-16`, `L76`, `L133/762`, `L160/781`, `L188/800/806`, `L216/827/865`, `L243/875/881`, `L270/898`, `L297/904`, `L324/325/754/919/930`, `L961`, `L1023`, `L1236`, `L1748-1754`) matches live `aa471867:aletheia/calculus.py` verbatim.
2. **Zero File/Measured-Series I/O (`GLYPHS.md:21`):** Confirmed `0` hits for `open(`, `read_text`, `read_bytes`, `csv`, `json.load`, `np.load` in `calculus.py`.
3. **Honest Rule-2 Classification of Our 8 Glyphs (`audit_symbol_utility_rule2`, Pillar 3):**
   - **`7/8` (`87.50%`) are renamings**, NOT new mathematical primitives beyond linear algebra / graph Hodge theory / Reynolds averaging / Sylvester inertia / exact rational equality:
     - `6/8` **`COMPOSITION_SHORTHAND_RENAMING`:** `⧄` (`OP-01`), `⧅` (`OP-02`), `⦷` (`OP-03`), `⧇` (`OP-05`), `⦺` (`OP-06`), `⩩` (`OP-07`).
     - `1/8` **`OVERLOADED_RENAMING`:** `⟠` (`OP-04`) overloads two unrelated operations (finite-group Reynolds average + `k=1`-restricted shifted Bernoulli/Mellin regulator at `L865`) under one glyph — a real notation hygiene defect that should be split or retired.
   - **`1/8` (`12.50%`) is a `TYPED_ENGINEERING_OPERATOR`:** `⫩` (`OP-08` `r5_refusal_gate`) adds a graded rational kill-ratio contract `(passed: bool, kill_ratio in [0,1] cap Q)` rooted in software mutation testing (DeMillo–Lipton–Sayward 1978, `N0`), verified on code artifacts rather than unseen physical telemetry.
   - **`0/8` (`0/1`) are `OPERATIONAL_NEW_PRIMITIVE`** under Rule 2 (*reproducible + adds a rule + predicts unseen physical data*).
4. **`"0 in 227,540"` (`README.md:24-28`, `calculus.py:76`):** Confirmed to be a Lean 4 Unicode collision count whose scan script was never committed (`R7` provenance gap).
5. **`continuum.md:16` (`EVIDENCE.md:7-24`, Review `6010323491`):** *"raw telemetry ... reveals the same four universal transformations"* currently has **zero measured-telemetry run behind it**. Live inspection confirms turns `18` (`GWOSC`) and `20` (`MAST`) in `session_raw_verbatim_export.json` have `role == "model"`. Relabeling line 16 as a **`hypothesis`** until measured raw-data runs exist is **100% required under Aletheia Law 4**.
6. **Input-Hash Pinning Gap (`EVIDENCE.md:56`):** Even the repos fetching real archives (`plate-eclipses`, `plate-novae`, `exoplanets-frontier`) pin output hashes only, not raw input bytes (`R7` gap).

### 2.2 Two Verified Nuances to Preserve Alongside Claude's Critique

1. **Typed Composition Probes (`calculus.py:1428-1898`):** Live `git show` confirms `6` executable cross-operator composition probes (`run_probe_c1_...` through `run_probe_c6_...`) verifying algebraic commutators, associators, Jensen bounds, Woodbury obstructions, exact-vs-float64 killshots, and subadditivity. Individual glyphs `OP-01..07` remain **renamings**, but the honest claim to preserve is that their justification rests strictly on *typed AST composition checks on constructed exact-$\mathbb{Q}$ objects* — not on raw-data discovery.
2. **Mutation-Testing Origin of `⫩` (`OP-08`):** Even the single non-renaming glyph `⫩` is an operational software-verification gate (`N1` implementation of `N0` mutation testing), not a continuum-physics primitive.

---

## 3. Law-2 Steelman & Five Formal Tightenings for `OWN_TERMS_FIRST.md` (`OTF-TIGHT-01..05`)

`OWN_TERMS_FIRST.md` (`aletheia#9`) makes a genuinely valuable epistemic upgrade: decoupling **Phase 1 (empirical validity on a pattern's own terms)** from **Phase 2 (prior-art & translation mapping)** resolves the conflation in `LAWS_AND_GATES.md:15, 57` without weakening novelty bars, while Rule 6 (*"hand unmeasurable claims back, never invent a definition to knock down"*) enforces anti-strawman discipline.

Before adopting `OWN_TERMS_FIRST.md` into Aletheia v1.5/v2.0, **five formal mathematical and governance tightenings** are required and proved in pure $\mathbb{Q}$ in `own_terms_first_oracle.py`:

### 3.1 `OTF-TIGHT-01` [HIGH] — Multiple-Testing FWER Inflation & Trivial-Constant Degeneracy in Rule 3 (`L23`)

- **Vulnerability:** Searching over $M$ candidate nets/windows/quantisations at nominal per-test $\alpha_{\mathrm{per}} = 1/20$ (`5%`) inflates the exact independent family-wise error rate to $1 - (19/20)^{10} = \mathbf{4108933742199/10240000000000 = 40.13\%}$ and exact dependence-free Bonferroni upper bound to $\mathbf{1/2 = 50.00\%}$! Furthermore, a constant statistic trivially achieves `obs_spread == 0/1` across all 5 net axes.
- **Formal Tightening (Enforced in `audit_phase1_net_invariance_gate`):**
  1. Require **R6 pre-pinned net families** covering all 5 axes (`sampling_rate`, `quantisation`, `amplitude_scale`, `window`, `instrument`) BEFORE opening unseen data.
  2. Enforce **dependence-free Bonferroni budget** $\min(1, M \cdot \alpha_{\mathrm{per}}) \le \alpha_{\mathrm{FWER}}$ (since net transforms on the same dataset are dependent; closes the loophole where independent FWER $= 4.95\% < 5\%$ while Bonferroni $= 5.05\% > 5\%$).
  3. Enforce **AND-conjunction** across every net with magnitude-safe null margins (`obs - abs(null) >= min_signal_margin`), absolute control cap (`max(abs(ctrl)) <= max_control_score`), AND signal-over-control dominance (`min(obs - abs(ctrl)) >= min_signal_margin`, closing `OTF-BUG-02`).
  4. Enforce strict zero-float screening on `net_measurements` and `pinned_spec` BEFORE Rule-6 early return (closing `OTF-BUG-01`).

### 3.2 `OTF-TIGHT-02` [HIGH] — Identifiability Confound in the Direct Continuum-Remainder Test (`L34-39`)

- **Vulnerability (`OWN_TERMS_FIRST.md:38`):** A structured remainder after fitting ONE fixed model $\mathcal{M}_1$ that recurs in unseen data and vanishes in scrambled copies **does NOT distinguish an uncountable continuum from ordinary finite-class model misspecification!**
- **Exact Pure-$\mathbb{Q}$ Walsh–Hadamard Witness (`audit_continuum_remainder_ladder_exact`, Pillar 2):**
  - Take exact length-8 orthogonal Walsh vectors $w_1, w_2, w_3 \in \{\pm 1\}^8$ and a purely discrete 2-mode fixed signal $y = 4 w_1 + 2 w_2$ (`train_energy = 160/1`, zero continuum!).
  - **Rung 1 ($\mathcal{M}_1 = \mathrm{span}(w_1)$):** leaves exact residual energy ratio **`1/5` (`20.00%`)**, exact unseen residual squared alignment **`1/1` (`100%`, positive sign)**, beating scrambled null `1/10` — **falsely triggering a 1-model continuum-remainder claim!**
  - **Rung 2 ($\mathcal{M}_2 = \mathrm{span}(w_1, w_2)$):** residual energy ratio collapses identically to **`0/1`**, exposing **`FINITE_MODEL_MISSPECIFICATION`** (`single_model_test_confounded = True`)!
  - By contrast, $y_{\mathrm{3mode}} = 4 w_1 + 2 w_2 + 2 w_3$ (`train_energy = 192/1`) retains `1/3` at rung 1 and `1/6` at rung 2 with `unseen_positive_alignment = True` and `corr_sq = 1/1`, earning the narrow, honest label **`STRUCTURED_REMAINDER_SURVIVING_LADDER`** (still `N1` relative to the tested ladder $\mathcal{M}_1..\mathcal{M}_K$, NEVER an `N2` proof of cardinality $\mathfrak{c}$!).
  - Our oracle projects `y_unseen` orthogonally onto $\mathcal{M}_k^\perp$ (`r_un = y_unseen - P_{M_k}(y_unseen)`) so in-model shifts $P_{\mathcal{M}_k}(y_{\mathrm{unseen}} - y_{\mathrm{train}})$ cannot contaminate out-of-model energy ratios or break amplitude-scale invariance (closing `OTF-BUG-03`), while also rejecting anti-correlated unseen sign flips (`dot(r_tr, r_un) <= 0`) and vanishing-amplitude unseen residuals (`e_r_un / e_unseen < min_eratio`).

### 3.3 `OTF-TIGHT-03` [HIGH] — Stratified Scrambled Nulls Against Colored / Red Noise (`L24`)

- **Vulnerability:** Under naive IID time-shuffling alone, plain autocorrelated red noise (e.g., AR(1)) produces high lag-1 correlation that recurs in unseen data and disappears under IID permutation, passing Rule 4 as a false positive.
- **Formal Tightening:** Stratify Rule 4 into mandatory **Tier 4A (IID permutation null)** AND **Tier 4B (spectrum-/phase-preserving or block-circular null)**. Our Pillar-1 witness (`obs = 3/5`, `iid_null = 1/20` -> margin `11/20 >= 1/2`, `spec_null = 11/20` -> margin `1/20 < 1/2`) cleanly rejects colored-noise artifacts as **`RULE4B_RED_NOISE_SPECTRUM_NULL_FAILED`** (`P1_FAILED_NULL_OR_CONTROL`).

### 3.4 `OTF-TIGHT-04` [MED] — Quantified 5-Class Rule-2 Symbol Decision Table (`L22`)

Formalizes Rule 2 cleanly into `OPERATIONAL_NEW_PRIMITIVE`, `TYPED_ENGINEERING_OPERATOR`, `COMPOSITION_SHORTHAND_RENAMING`, `OVERLOADED_RENAMING`, and `NON_REPRODUCIBLE_SYMBOL` (producing the verified `7/8` renaming / `1/8` engineering-operator split for our own 8 glyphs).

### 3.5 `OTF-TIGHT-05` [MED] — Decoupled Phase-1 / Phase-2 Integration with Laws 1–5 & `R6`/`R7` (`aletheia#3`)

Enforced in `compose_phase1_phase2_verdict`:
- Phase 1 enforces `R6` (pre-pinned axes, thresholds, model ladder, FWER budget), `R7` (input raw-bytes SHA-256 pinned & gate-measured), and Rules 3–6.
- Phase 2 runs *independently* after Phase 1: `N0_KNOWN_BY_MECHANISM` or `DOES_NOT_TRANSLATE` NEVER revokes `phase1_empirical_valid = True`, while `N1`/`N2`/`DOES_NOT_TRANSLATE` require `full_text_prior_art_checked = True`, failed Phase 1 blocks `N1`/`N2`/`DOES_NOT_TRANSLATE`, and `P1_UNMEASURABLE_RETURNED` blocks premature Phase-2 verdicts (`PREMATURE_PHASE2_ON_UNMEASURABLE`).

---

## 4. Law-4 Quarantine & Owner Confirmation Gate (`OWN_TERMS_FIRST.md:3, 9-13`)

- **`N1` (Mechanically Verified in `AUDIT-084`):** Exact pure-$\mathbb{Q}$ Phase-1 gate, Bonferroni/FWER exact bounds, Walsh–Hadamard 2-rung identifiability witness, 5-class Rule-2 symbol audit of our 8 glyphs against live `aa471867:aletheia/calculus.py`, Phase-1/Phase-2 orthogonality composer, all `7/7` staged portal SHA-256 bindings, `4/4` isolated `-I` R4 parity, and `100.0%` R5 mutation kill across both Python modules.
- **`N0` / Owner-Gated Quarantine:**
  1. **Project Direction Wording (`OWN_TERMS_FIRST.md:3, 9-13`):** Items 1–3 (*"existing approach to mathematics, down to its number systems and notation, is assumed to be flawed..."*) are explicitly marked as the outside checker's understanding of conversational guidance (`SEARCHES.md:12-13` confirms no written repo policy states them). Policy adoption stays strictly gated (`owner_direction_confirmed = False -> policy_adoption_ready = False`) until the project owner confirms or revises the wording.
  2. Classical Bonferroni/FWER bounds, orthogonal Walsh–Hadamard projection, IAAFT/spectrum-preserving surrogates, and DeMillo–Lipton–Sayward mutation testing are prior art (`N0`).
  3. Zero measured raw-telemetry datasets were executed in `AUDIT-084`; real-data testing of `continuum.md:16` belongs to the pre-registered study (`cave-expedition#6`, Arm R10-4 `AUDIT-087`).

---

## 5. Reproduction & Falsification Criteria

### Exact Reproduction Commands (Run from `symbiosis/round10/arm1-own-terms-first/`)

```bash
# 1. Live read-only audit against staged Round-10 portals & aletheia-live
python3 -I -B -W error own_terms_first_audit.py --output own_terms_first_certificate.json

# 2. Standalone pure-Q verification (zero external files or git repos required)
python3 -I -B -W error own_terms_first_audit.py --standalone --json

# 3. Full R5 & adversarial red-team test suite (-I -O -B -W error)
python3 -I -O -B -W error test_own_terms_first_r5.py

# 4. Aletheia v1.4.0 mutation kill verification (requires PYTHONPATH=<aletheia-repo>)
python3 -B -W error -m aletheia mutate own_terms_first_oracle.py \
  --test-cmd "python3 -I -O -B -W error test_own_terms_first_r5.py" --add-cwd
python3 -B -W error -m aletheia mutate own_terms_first_audit.py \
  --test-cmd "python3 -I -O -B -W error test_own_terms_first_r5.py" --add-cwd
```

### Falsification Criteria

`AUDIT-084` is falsified if any of the following is demonstrated:
1. Any non-determinism across isolated `python3 -I -B -W error` runs (live or `--standalone`).
2. Any IEEE-754 `float` accepted by any oracle entry point or emitted in `own_terms_first_certificate.json`.
3. Any bypass of `audit_phase1_net_invariance_gate` (FWER/Bonferroni, missing net axis, negative-control sign flip, red-noise Tier-4B failure, Rule 6), `audit_continuum_remainder_ladder_exact` (anti-correlated sign flip, vanishing unseen residual, non-orthogonal basis), `audit_symbol_utility_rule2`, or `compose_phase1_phase2_verdict`.
4. Any surviving mutant under `aletheia v1.4.0 mutate --add-cwd` in `own_terms_first_oracle.py` or `own_terms_first_audit.py`.
5. Any discrepancy between our reported line/I/O/turn counts and live `aa471867:aletheia/calculus.py` or the 7 SHA-256-pinned Round-10 portal files.
