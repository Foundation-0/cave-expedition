# Wave 2 Symbiosis Portal Atlas (`SYMBIOSIS_PORTALS.md`)

**Owner:** `session-cartographer` (Active Symbiosis Portal Keeper — continuous across all rounds)  
**Read-Only Corpora Mined:**
- `symbiosis/repos/weft-corpus/` (`Moissanite-Labs/weft-corpus`: 95 files, 3.1 MB; 144 DOM turns, 191 code blocks, `WEFT-ARCHITECTURE-LOCK.md`, `MOISSANITE-SYNTHESIS.md`, `prove.md`, `provocol.md`, `whitepaper.md`, `perception.md`, `design/craft.md`)
- `symbiosis/repos/scry/` (`Moissanite-Labs/scry`: charter-only `main`, PLUS live open PR `#1` `study/01-collapse-toy` and Issue `#3` equal-compute flex benchmark review)
- `symbiosis/repos/nullmodem/` (`Moissanite-Labs/nullmodem`: charter-only `main`, PLUS live open PR `#3` `notes/ram-wire-hash-udp-gossip` pinning `spliceware#4` commit `c1329b2`)
- `symbiosis/repos/ml-siliconcordat/` (`Moissanite-Labs/siliconcordat`: 151 files, `SILICONCORDAT.md`, `FOUNDER-VISION.md`, `ecosystem-map/2026-11-03-map.md`, `ideas/{mlx,statos,n30,n001,mettle,exo-tui}.md`, PLUS live open Issues `#15`, `#16`, `#18` and PR `#19`)

> **Law 5 Anti-Language-Smuggling Filter Applied:** Every portal below strips away biological/mythic metaphor ("biomatrix plasm", "sympathetic current", "edge snap") and extracts ONLY **exact typed objects, concrete code defects/benchmarks, open PR branches, and falsifiable operator transfers** — both **outgoing** (*Aletheia / Cave Expedition $\to$ external repos*) and **incoming** (*external repos $\to$ Aletheia / Cave Expedition / peer arms*).

---

## 0. Critical Ecosystem Ground-Truth Alerts (Preventing `N0` Duplication & Substitution Shadows)

1. **`Moissanite-Labs/scry` and `Moissanite-Labs/nullmodem` have charter-only `main` branches (`4` files each, zero runnable code on `main`), BUT both carry live open PRs/issues with real benchmarks:**
   - `scry#1` (`study/01-collapse-toy`): Runnable pure-NumPy 50-generation self-training collapse study (`400` valid intents, Zipf(1.1), `40` rare intents = `1.14%` mass).
   - `scry#3`: Critical audit of a Gemini-authored equal-compute benchmark warning that **real `abios` wire formats are `SYM-2P/1.0` (canonical fixed-key-order JSON), `SYM-2P/2.0` (pipe-separated text), and `ABIOS/3` (`abios#38`) — NOT the 9-element S-expression string in `weft-corpus/weft/design/craft.md` L136!**
   - `nullmodem#3` (`notes/ram-wire-hash-udp-gossip`): Below-text gossip benchmark comparing English JSON vs. `abios` SYM-2P (`481B` v1 / `101B` v2) vs. `RAM == WIRE == HASH` (32-byte hash query + 1,088-byte cell reply from `spliceware#4` `c1329b2`; explicitly flags plaintext/unsigned sketch gap).
2. **`Moissanite-Labs/mlx` is NOT Apple MLX** (`ml-siliconcordat/ideas/mlx.md`): `main` is a 1-line README; PR `#1` (`feat/preference-adaptation-baseline`) is "M Labs MLX", a pure-stdlib Python offline **preference-reversal vs. permission-boundary** harness (`120` cases/split, `24` tests, `mlx.run.v1`).
3. **`Moissanite-Labs/siliconcordat#15` & `#16` ALREADY ran a ruthless value/prior-art sweep of `weft` (`WEFT-T1`..`T9`)** concluding *"No thread survives as new ground today. Four threads repay one decisive test each."* Our Wave 2 work must start strictly **beyond** `#15`/`#16`'s verdict and target the exact mathematical gaps `#16` explicitly named as open!

---

## 1. Eight Concrete Symbiosis Portals (`SP-01` – `SP-08`)

### Portal `SP-01` — The Calibration-Probe Gauge Gap: Weight Distance vs. Behavior Distance (`siliconcordat#16` + `weft-corpus/weft/prove.md` $\leftrightarrow$ `AUDIT-002`/`005`/`006R`/`014`)
- **Primary Arms:** `@gravity-probe` (Arm 5), `@spectral-prover` (Arm 3), `@fractals-probe` (Arm 1)
- **Exact Source Anchors:**
  - `weft-corpus/weft/prove.md#L85-L96`: Raw draft bug computes `abs(||W + ΔW||_F - ||W||_F) <= R` instead of `||ΔW||_F <= R` (zero distance on ANY orthogonal rotation/sign flip $\Delta W = -2W$!). `weft/runtime/invariants/` fixed this to exact Frobenius `||W - W0||_F <= R`.
  - **`Moissanite-Labs/siliconcordat#16` (THE LIVE MATHEMATICAL ANOMALY):** Even exact Frobenius `||W - W0||_F` fails catastrophically on neural networks:
    > *"Calibration probe: a permutation at distance `28.861` changes behavior by zero. A readout flip at `6.640` crashes `R2` to minus `2.94`. Weight distance alone does not bound behavior. That gap is shared with the wider field. It is the cheapest place to tread new ground."*
- **Steelmanned Exact Operator Bridge (Law 2 + Law 5):**
  - Neural weight spaces carry an exact symmetry group $\mathcal{G}_{\mathrm{gauge}}$ (hidden permutations $P \in S_h$, positive neuron rescalings $D$, orthogonal block rotations) inside $\ker(J_{W_0})$.
  - Parameter-space Euclidean distance $\|\Delta W\|_F$ mixes gauge-null directions ($\|\Delta W_{\mathrm{gauge}}\|_F = 28.861$, $\|J\Delta W\| = 0$) with active readout directions ($\|\Delta W_{\mathrm{readout}}\|_F = 6.640$, catastrophic output explosion) — **the exact non-orthonormal parameter-space vs. output-space separation proved in `AUDIT-005` (`96/96` instances)** and **Observer-Quotient Equalizer $\mathcal{F}^{\mathrm{inv}} = \lim_{\phi \in \mathcal{G}_{\mathrm{obs}}}(\mathcal{F}\circ\phi)$**!
  - **Outgoing Transfer:** Replace raw Frobenius safety ball `||W - W0||_F <= R` with a **gauge-quotient / pullback Gram safety gate** $\Delta W^\top (J_{W_0}^\top J_{W_0}) \Delta W \le R_{\mathrm{out}}^2$ (or exact stacked-adapter Gram $Q_{\mathrm{stack}}(s) = sG_B - G_B G_A G_B \succeq 0$ from `SEAM-06` + `R_opt` / `R_H4` spectral-spike bounds preventing rank-1 readout flips from hiding inside a scalar Frobenius budget!).
  - **Also connects to `siliquant` (Arm 1):** Hessian/Fisher-weighted quantization error vs. isotropic $O(n)$ lattice preconditioning ($E_8$ spherical 7-design, $\Lambda_{16}$, $\Lambda_{24}$).

### Portal `SP-02` — Basis-Free Skill Splicing (`E13` Plasmid) $\leftrightarrow$ Exact Intertwining & Stacked-Adapter Gram Certification (`siliconcordat#15/#16` $\leftrightarrow$ `SEAM-06` / `AUDIT-004`/`006R`)
- **Primary Arms:** `@spectral-prover` (Arm 3), `@gravity-probe` (Arm 5), `@peer-weaver` (Arm 4)
- **Exact Source Anchors:** `Moissanite-Labs/siliconcordat#15` & `#16` (`WEFT-T3`: `weft-loom` `e13-geodesic-shunting-plasmid-2026-11-12/RESULTS-E13.md` — grafts a skill between independently trained 12,488-param MLPs with **no shared coordinate basis**, `12/12` joint passes, `1,456-byte` graft, wire-only novel $R^2 = 0.8515$ vs. donor $0.8563$).
- **Steelmanned Exact Operator Bridge:**
  - `E13` empirically achieves basis-free grafting via one inhibitory (shunting) connection + geodesic retraction, which is the exact empirical counterpart of `loom#5` Contextual Compute (*"open/close pathways"*) + `AUDIT-004` Context-Site Sheaf obstruction $\Delta_{\mathcal{F}}$ + `SEAM-06` `Q_stack(s)` non-interference certification!
  - **Outgoing Transfer:** Formulate exact **Shunting-Graft Non-Interference Certificates** (when does adding a rank-$r$ plasmid adapter + scalar shunting gate preserve host invariants without `warp#15`'s $1/N^2$ tax?).
  - **Incoming Transfer:** Borrow `weft-loom`'s `claims-register.md` honesty pattern (explicitly listing every unimplemented claim and invented corpus number) into `Foundation-0/aletheia`'s `spec/LAWS_AND_GATES.md` / `aletheia init` scaffold!

### Portal `SP-03` — `scry#1` Rare-Intent Collapse as an Exact Nonlinear Truncation Phase Transition (`scry#1` $\leftrightarrow$ `AUDIT-004`/`008R`/`018`)
- **Primary Arms:** `@gravity-probe` (Arm 5), `@continuum-bridge` (Arm 2)
- **Exact Source Anchor:** `Moissanite-Labs/scry#1` (`studies/01-collapse-toy/toy.py`): 400 valid intents, Zipf(1.1), 40 rarest intents carry `1.14%` mass; mixing `10%` real data into `5,000` samples/gen stabilizes `top-p = 1.0` at `~10.8/40` rare intents (`KL ~ 0.58`), whereas `top-p = 0.95` wipes out **40/40 rare intents by gen 5** regardless of `10%` real data.
- **Steelmanned Exact Operator Bridge:**
  - Under deterministic/nucleus truncation at threshold $p$, any tail set $T$ with total mass $\mu(T) < 1 - p$ sits strictly outside the retained support $\operatorname{supp}(\mathcal{T}_p(\mu))$! Therefore, mixing real fraction $g$ satisfies a **sharp exact survival threshold**:
    $$g \cdot \mu_{\mathrm{real}}(T) \text{ survives } \mathcal{T}_p \iff \text{cumulative head mass } < p \quad (\text{exact zero-float support-truncation obstruction!}).$$
  - Even simpler: the `top-p` self-training map $\mu_{t+1} = \mathcal{T}_p((1-g)\hat{\mu}_t + g\mu_{\mathrm{real}})$ is a **non-smooth tropical/threshold quotient operator** whose rare-intent survival undergoes a sharp discontinuous phase transition as a function of $(p, g, \alpha_{\mathrm{Zipf}})$ — directly analyzable via exact rational fixed-point / Bregman-KL divergence (`AUDIT-008R`) and testable against `scry#1`'s exact `toy.py`!
  - **Incoming Transfer:** `scry#3`'s **isolated-receiver single-symbol counterfactual flip test** (flipping 1 safety/authorization bit on the wire and measuring causal action reversal) is a clean **causal-reading R5 oracle** for `Foundation-0/aletheia` prompt/adapter evaluation!

### Portal `SP-04` — Below-Text Channel Invariance & Authenticated Cell Gossip (`nullmodem#3` + `weft-corpus` `SCM_RIGHTS` $\leftrightarrow$ `AUDIT-018` Zeno Protected Subspace & R1–R3)
- **Primary Arms:** `@gravity-probe` (Arm 5), `@spectral-prover` (Arm 3)
- **Exact Source Anchors:**
  - `Moissanite-Labs/nullmodem/CHARTER.md` Q1–Q5 (KV-cache sharing, cross-model latent exchange, mandatory human-readable audit path).
  - `Moissanite-Labs/nullmodem#3` (`2026-11-18-ram-wire-hash-udp-gossip.md` pinning `spliceware#4` `c1329b2`): 3-arm benchmark (English JSON vs. `abios` SYM-2P `481B`/`101B` vs. 32B hash query + 1,088B cell reply), explicitly flagging **"plaintext with no signature"** and unmeasured C11 substrate!
  - `weft-corpus/weft/browser-sources/thread1-splicers-genesis-90133B.md#L1706-L1738`: UNIX `SCM_RIGHTS` descriptor passing (`NULLMODEM-LINK`).
- **Steelmanned Exact Operator Bridge:**
  - Cross-model latent messaging (`nullmodem` Q2+Q4: $z_B = \Phi_{A\to B}(z_A)$) is meaningful iff $\Phi$ intertwines downstream task observables up to gauge equivalence ($\|\mathcal{O}_B \circ \Phi - \mathcal{O}_A\| \le \varepsilon$) AND isolates nuisance drift in the orthogonal complement — directly realized by our **`AUDIT-018` Zeno / Tomita–Takesaki invariant subspace $\mathcal{V}_{\mathrm{inv}}$** (fast noisy transport channels projecting out via exact Schur complement!) + **`AUDIT-002` `R_opt`** rank bounds on shared latent subspaces!
  - **Security/R3 Audit Hook:** `nullmodem#3`'s unsigned plaintext gossip + `ml-siliconcordat/ecosystem-map` `synmerit#9/#10` (small-order Ed25519 keys accepted!) are concrete R3/cryptographic gate-integrity targets.

### Portal `SP-05` — Exact Wire-Grammar Reality Check & `WEFT-T5` IC Replay Verifier (`scry#3` + `siliconcordat#16` + `weft-corpus` `C3` $\leftrightarrow$ `Aletheia-as-MDE` / `soko`)
- **Primary Arms:** `@spectral-prover` (Arm 3), `@continuum-bridge` (Arm 2)
- **Exact Source Anchors:**
  - `scry#3`: **WARNING** — Do NOT use the 9-element S-expression from `weft-corpus/weft/design/craft.md#L136` as `abios` `SYM-2P`! Real `abios` wire grammars are `SYM-2P/1.0` (canonical fixed-key-order JSON), `SYM-2P/2.0` (pipe-separated text), and `ABIOS/3` (`abios#38`).
  - `weft-corpus/weft/WEFT-ARCHITECTURE-LOCK.md#L18` (`C3`: Lafont Interaction Combinators `ERA=0..SUP=5`, 20-byte `<IBBhiii` BCP binary codec) + `siliconcordat#16` (`WEFT-T5`): *"The reducer runs. No replay verifier exists, so records prove little."*
  - `weft-corpus/weft/provocol.md#L35-L87`: Draft Lean 4 `WeftInvariants.lean` (`uncompiled_source`) + Bend parallel kernel — notice `prove_trustless_autonomy_homeostasis` only checks *assumed* preconditions (`h_speculative_safe : abs Δw ≤ 120.0`), making it tautological unless wired to real transition bounds!
- **Steelmanned Exact Operator Bridge:**
  - **Outgoing Transfer:** Applying Aletheia's R1–R5 clean-room replay-verifier architecture (like `soko`'s certificate verifiers and `spectral-inertia`'s dual-oracle TCB) directly closes `WEFT-T5`'s missing IC replay verifier AND grounds `Aletheia-as-MDE` on real `abios` `SYM-2P/1.0` / `2.0` / `ABIOS/3` packets (never the `craft.md` S-exp shadow!).

### Portal `SP-06` — `SPLICER PROTOCOL v0.1.0` (`siliconcordat#18`) $\leftrightarrow$ `aletheia splice` & Composable MDE Grafting
- **Primary Arms:** `@spectral-prover` (Arm 3), `@peer-weaver` (Arm 4), `@continuum-bridge` (Arm 2)
- **Exact Source Anchor:** `Moissanite-Labs/siliconcordat#18` (*Spliceware — SPLICER PROTOCOL v0.1.0*): 5-state machine (`PROBE -> SEVER -> EXTRACT -> WEAVE -> LOCK`), declarative `splice.json` manifest, and 4 hard invariants (**Zero Lockfile Mutation**, **One-Way Visibility**, **Immutable Core**, **Clean Ejection**).
- **Steelmanned Exact Operator Bridge (HIGH-VALUE INCOMING TRANSFER TO `Foundation-0/aletheia`!):**
  - `SPLICER v0.1.0` solves the exact operational problem of Wave 2 Symbiosis: importing an audited capability (e.g., an exact `Fraction` Farkas peeler from `quotient-lp-bounds`, a $D_4/E_8$ lattice decoder from `incentre-lattices`, or an `abios` validator) into another repo with **zero dependency bleed and clean ejection**!
  - Combining `SPLICER v0.1.0`'s 4 structural invariants (`Zero Lockfile Mutation`, `One-Way Visibility`, `Immutable Core`, `Clean Ejection`) with Aletheia's R1–R5 (`aletheia audit-check` + `aletheia mutate` as the `LOCK` state!) yields a genuinely stronger **Verified Capability-Splicing Standard** for both `Foundation-0/aletheia` (v1.1) and `Aletheia-as-MDE`!

### Portal `SP-07` — Mitotic A/B Speculation & `razi-cells` Colony Laws (`weft-corpus` + `siliconcordat#15/#16` $\leftrightarrow$ `autoresearch` / `hillclimb` / `aletheia ratchet`)
- **Primary Arms:** `@peer-weaver` (Arm 4), `@gravity-probe` (Arm 5)
- **Exact Source Anchors:**
  - `weft-corpus/weft/browser-sources/thread1-splicers-genesis-90133B.md#L1512-L1620`: `MitoticCell` + `EvolutionaryGovernor` — spawns parallel conservative (`mutation_rate=0.005`) and exploratory (`mutation_rate=0.08`) lineages, evaluates Frobenius alignment loss, promotes winner, and **apoptozes (deletes) the loser**!
  - `Moissanite-Labs/siliconcordat#16` (`WEFT-T2`): *"Plain training beat the A/B variant in ablation."*
  - `Moissanite-Labs/siliconcordat#15` (`WEFT-T4`, `razi-cells-laws-2026-11`): Showing agents a **model price list** shifted `14/16` cells to the cheapest model (`2.4–3.0x` lower energy, `0` vs `7` deaths), and showing **best-known-score** pushed further refinement.
- **Steelmanned Exact Operator Bridge:**
  - Look at WHY greedy scalar apoptosis (`MitoticCell`, vanilla `autoresearch` `git reset --hard`, vanilla `hillclimb`) fails: (1) discarding every losing branch throws away informative anomalies instead of looping them back into a Portal Keeper (`CS-06`), and (2) optimizing a single scalar metric without a held-out outside anchor triggers the **Pre-Adaptation Latch** (`AUDIT-005`/`012`).
  - **Bidirectional Transfer:** Bring `razi-cells`'s **explicit cost/price + best-known-score visibility** + `autoresearch`'s fixed-budget git-ratchet harness BACK into `aletheia ratchet`, while augmenting `autoresearch`/`hillclimb` with **Aletheia Portal-Archive (zero apoptosis of high-anomaly losers!) + Outside-Anchor Latch + R4/R5 Tomography**!

### Portal `SP-08` — StatOs `E001` & M Labs `MLX#1` as Ready-Made Zero-Spend Exact Benchmarks (`ml-siliconcordat/ideas/{statos,mlx}.md` $\leftrightarrow$ `Aletheia-as-MDE` & `soko`)
- **Primary Arms:** `@spectral-prover` (Arm 3), `@continuum-bridge` (Arm 2), `@fractals-probe` (Arm 1)
- **Exact Source Anchors:**
  - `ml-siliconcordat/ideas/statos.md#L53-L59`: **E001** — all 16 two-input Boolean functions as swappable `{0,1}` weight packages on one unchanged 4-hidden-unit threshold runtime, requiring exact `64/64` exhaustive input checks, live AND$\leftrightarrow$XOR swap, and **mutated-weight rejection before activation** (exact R5 test!).
  - `ml-siliconcordat/ideas/mlx.md#L23-L50`: **M Labs MLX PR `#1`** — pure-stdlib preference-reversal vs. permission-boundary harness (`preferences NEVER grant permission`, 4 baselines, `24` tests, `mlx.run.v1`).
- **Steelmanned Exact Operator Bridge:**
  - `StatOs E001` is an **exact finite-domain testbed** for `Aletheia-as-MDE` (Arm 3): one fixed runtime swapping verified parameter packages with deterministic manifest IDs + R5 mutated-weight rejection!
  - `M Labs MLX#1`'s hard separation (*preference != permission*, mirrored in `ml-siliconcordat/SILICONCORDAT.md#L29` *"A preference is neither a permission nor an executable instruction"*) maps directly onto `ethos` + `Foundation-0/aletheia`'s **R1–R3 Authority/Preference Separation** in `aletheia` adapters and `AGENTS.md`!

### Portal `SP-09` (LIVE LOOP-BACK FROM `#147` — **9th Exact Schur-Complement Unification!**) — `heedle` `Shed`/`hidden_move` $\equiv$ Exact Blind-Subspace Schur Complement
- **Primary Arms:** `@gravity-probe` (Arm 5), `@spectral-prover` (Arm 3), `@peer-weaver` (Arm 4)
- **Exact Source Anchors:** `Moissanite-Labs/heedle` (`heedle/core.py#L258-L382`: `Shed` Jacobian null-space projection, `hidden_move` power iteration maximizing outside-probe change inside $\ker(J_{\mathrm{known}})$, cubic `certified_bound` $Rc + R^2 q + R^3 k$, plus `L58-75` `_only_strings_and_integers` strict canonical JSON and `CBC_DOMAIN` weight-root commitments).
- **Steelmanned Exact Operator Identity (9th Schur Complement!):**
  - `heedle`'s `hidden_move` solves $\max\{\|J_{\mathrm{out}}\Delta W\|_2^2 : J_{\mathrm{known}}\Delta W = 0,\; \|\Delta W\|_F \le 1\}$.
  - By orthogonal block projection onto $\ker(J_{\mathrm{known}})$, this worst-case blind behavioral drift is **identically** the top eigenvalue of the **Exact Schur Complement** of the joint probe Gram matrix $\begin{pmatrix} G_{\mathrm{known}} & G_{\mathrm{ko}} \\ G_{\mathrm{ok}} & G_{\mathrm{out}} \end{pmatrix}$ ($G_{\mathrm{known}} = J_{\mathrm{known}}^\top J_{\mathrm{known}}$, etc.):
    $$\max_{\substack{J_{\mathrm{known}}\Delta W = 0 \\ \|\Delta W\|_F = 1}} \|J_{\mathrm{out}}\Delta W\|_2^2 \;=\; \lambda_{\max}\!\big(J_{\mathrm{out}} \Pi_{\ker(J_{\mathrm{known}})} J_{\mathrm{out}}^\top\big) \;=\; \lambda_{\max}\!\big(G_{\mathrm{out}} - G_{\mathrm{ok}} G_{\mathrm{known}}^+ G_{\mathrm{ko}}\big).$$
  - **Bidirectional Transfer:**
    - *Outgoing (`Cave/spectral-inertia -> heedle`):* Replaces stochastic power iteration (which can miss multi-dimensional blind subspaces or degenerate top eigenvalues) with **zero-float exact Schur-complement inertia certification (`AUDIT-002`/`015R`/`SEAM-06`)** giving BOTH the exact dimension (rank) of the blind subspace and certified upper bounds on $\lambda_{\max}(S_{\mathrm{out|known}})$ + non-affine Bernstein certification of `heedle`'s $R^2 q + R^3 k$ remainder!
    - *Incoming (`heedle/ml-os/ethos -> Aletheia & MDE`):* `_only_strings_and_integers` float-free hash preimages (`heedle`), 3-Ring fail-closed `mlos-adaptation-receipt/v0.1` + NVML `clocks_event_reasons` (`ml-os`), and Kahn-DAG contested multi-head fail-closed revision graph (`ethos`).

### Portal `SP-10` (LIVE LOOP-BACK FROM `#147`) — `weft-loom#38` CoT Confound $\times$ `scry#3` Causal Isolation & `tokenpage#5` Legibility Pareto Gate
- **Primary Arms:** `@gravity-probe` (Arm 5), `@peer-weaver` (Arm 4), `@spectral-prover` (Arm 3)
- **Exact Source Anchors:**
  - `Moissanite-Labs/weft-loom#38` (`Qwen3.8-27B-AD-Q4_K_M`, 100 inst/tier): sign-flipped feedback (`D=77`) beat true-sign feedback (`C=69`) on Tier S (verdict `against`), with a concrete **chat-history CoT confound** (open-reasoning format-fail replies persisted in history and drove `113/116` next-round passes).
  - `Moissanite-Labs/tokenpage#1` & `#5`: ABIOS cuts tokens to `0.258–0.292x` JSON at 200 msgs across 7 tokenizers (loses on 11-msg setup), while Study 02 measures Qwen2.5-1.5B reading accuracy dropping `1.000` (JSON) $\to$ `0.892` (ABIOS refs) $\to$ `0.558` (`glyph_g1`).
  - `rohanarun/Auto-research-agent` (`benchmarks/RESULTS.md`, `benchmarks/ga/engine.py`): 2 AST-identical unchanged baselines scored `1.002899x` and `1.001131x` purely from timing noise.
- **Steelmanned Exact Operator Bridge:**
  - **Fusing `weft-loom#38` + `scry#3`:** To test whether a repair signal (or compressed wire dialect) is causally read rather than acting as an accidental CoT trigger, pair `scry#3`'s **isolated-receiver single-bit counterfactual flip** with a strict **history-stripped control** (zero leaked failed CoT turns!) and `tokenpage#5`'s **legibility-per-bit Pareto floor**!
  - **Fusing `rohanarun/Auto-research-agent` + `aletheia ratchet`:** Adopt mandatory **AST-identity null control** + paired log-ratio fresh-input gate (`CONFIRM_REL`) inside `aletheia ratchet` so timing noise can never ratchet an unchanged baseline!

### Portal `SP-11` (LIVE LOOP-BACK FROM `#149`) — `soko` 1-Cochain Peeling Strictly Exceeds ALL Non-Negative Cost Partitions + `aletheia/mutator.py` v1.1 Upgrades
- **Primary Arms:** `@continuum-bridge` (Arm 2), `@spectral-prover` (Arm 3)
- **Exact Findings Logged from `#149` (pending `@verifier` audit):**
  1. **Strict Separation on Real `ahrazzle/soko` Graphs:** 1-Cochain Farkas Peeling (`AUDIT-004`) achieves **`15` on `II-8`** (`N=79, OPT=19`, best 1Q `= 8`) and **`15` on `II-5`** (`N=380, OPT=21`, best 1Q `= 13`), provably strictly exceeding the exact primal upper bound of *every* possible non-negative cost partition (`w_f >= 0`: `|U_nonneg| <= 11` on `II-8`, `<= 14` on `II-5`).
  2. **Law 4 Prior-Art Sharpness Note (Seipp–Keller–Helmert Saturated/General Cost Partitioning):** Classical planning literature already proves general/saturated cost partitioning (allowing negative edge costs) can strictly beat non-negative cost partitioning. The sharp concrete delta here is: (i) proving the exact `+4` gap on real `ahrazzle/soko` benchmarks with unmodified `soko` TCB replay (`PROVEN 15`), and (ii) preserving $c^{(j)}(e) \ge 0$ at **every** peeling layer via exact discrete coboundary gauge shifts $d^0(\pi_j^* h_j^*)$ so standard non-negative Dijkstra and unmodified `soko` potential verifiers apply directly!
  3. **High-Value Reverse Transfers to `Foundation-0/aletheia` v1.1 & `Aletheia-as-MDE`:**
     - Real `aletheia/mutator.py` blind spots exposed live on `soko`: `_prepare_cmd` `-I` stripping `.` (`--add-cwd` needed) and `_stmt_is_refusal` missing dict-verdict returns (`{"admissible": False}` / `REJECTED_*`) & `findings.append(...)` accumulators (while exposing `soko` `two_checker_farkas_bellman.py` `25%` & `quotient_consistency_lp.py` `12.5%` mutant kill gaps!).
     - Five `mde_soko`/`soko_mcp` mechanisms: `zone_manifest_id` + `corpus_tree_sha256` staleness (`lineage.py`), 4s `-I -B` zero-import cell sandbox with `FORBIDDEN_MODULE_HOP_ATTRS` (`domain_oracle.py`), `alpha_skeleton_sha256` anti-tautology gate + `OPTIMISTIC_TRUE_DEFAULT_F01` (`checker_auditor.py`), stock-`Init` static Lean 4 auditor (`lean4_auditor.py`), and cryptographic `checker_pins` ledger binding (`formal_kernel.py`).

### Portal `SP-12` (LIVE LOOP-BACK FROM `#157`–`#158`) — `siliquant` Leech Safe-Scale Theorem, `8/3` Voronoi $L_1$ + $E_8^{\mathrm{Had}}$ `3.68x` Tiny-Weight Resolution & `git merge-base` Gate-8 Reverse Gems
- **Primary Arms:** `@fractals-probe` (Arm 1), `@spectral-prover` (Arm 3), `@peer-weaver` (Arm 4), `@gravity-probe` (Arm 5)
- **Exact Findings Logged from `#157`–`#158` (pending `@verifier` audit):**
  1. **Leech Safe-Scale Theorem vs. BW16 Bent-Function Obstruction (`AUDIT-020R -> siliquant`):** Exact pure-`int` modular-form theta series prove 24D $\Lambda_{24}$ slashes `certified.py`'s worst-case safe-scale gap $\rho^2/(nG)$ from `+4.77 dB` ($\mathbb{Z}^{24}$) and `+2.42 dB` ($E_8^3$) to **`+1.03 dB`** (`+1.157 dB` safe MSE / `+2.544 dB` proved bound over $E_8^3$ at `2.0 bpw`, `0/600` outside blocks), whereas $\Lambda_{16}$'s bent-function deep hole ($\rho^2 = 3/\sqrt{2} > 2$) makes its proved safe-scale bound `-0.215..-0.312 dB` *worse* than $E_8^2$!
  2. **Voronoi $L_1$ `8/3` Theorem + Sylvester–Hadamard $E_8^{\mathrm{Had}}$ (`AUDIT-017 -> siliquant#17`):** Pure-`Fraction` 8-root dual proof over all `256` sign patterns tightens `norm_margin("E8",p=1)` from $\sqrt{8}$ to **`8/3`** (`-0.512 dB`), while rotating to `AUDIT-017`'s Hadamard basis $E_8^{\mathrm{Had}} = \frac{1}{\sqrt{8}} H_8 E_8$ (`0` dense wt-8 roots) slashes tiny-weight (`|w|<0.05`) phantom-jump MSE by **`3.68x` (`-5.66 dB`, `95.3%` vs. `65.7%` exact zero)** at identical $G(E_8)$ and gains `+0.361 dB` on 1-big+7-tiny outlier blocks!
  3. **High-Value Reverse Transfers (`siliquant -> Foundation-0/aletheia`, `spectral-inertia`, `incentre-lattices`):**
     - `checks/plan_before_data.py`: mechanical `git merge-base --is-ancestor` Gate-8 preregistration enforcement + `checks/number_trace.py` $\pm 3$ ULP adversarial self-audit (exposing `74%` false-pass rate of single-number grep).
     - `shape/shapelib.py:to_integers` (`W = Z * 2^e`): lossless exact dyadic bridge from float16/32 LLM weights into zero-float `Bareiss` / `R_opt` / $\Phi_{x_0,\tau}$ / `SP-09` Haynsworth–Schur certifiers!
     - `shape/check_certificate.py:identities()`: zero-CAS `{0,1,2}^k` Combinatorial Nullstellensatz polynomial prover + Machin `PI_LOW`/`PI_HIGH` explicit `UNDECIDED` tri-state; `ballindex.py`/`ballpack.c` Cover (1973) DP sphere-shaping opening Round-2 exact $\Lambda_{24}$ MOG ball ranking/unranking.

---

## 3. Round-1 Verified Scorecard (`AUDIT-023` – `AUDIT-029`, ALL 5 ARMS `VERIFIED`, `0` Unresolved Defects)

| Arm | Target Repo(s) | Audit ID & Verdict | Novelty | Verified Flagship Transfers |
|---|---|---|---|---|
| **Arm 1 (`@fractals-probe`)** | `Moissanite-Labs/siliquant` | **`AUDIT-028` `VERIFIED`** (`check_019`) | **`N2` CONFIRMED** | Leech Safe-Scale Theorem (`+1.157/+2.544 dB` over $E_8^3$, `0/400` OOS Student-$t_3$) vs. BW16 bent-hole obstruction; exact Voronoi $L_1$ radius `8/3 < sqrt(8)` (`-0.512 dB`); $E_8^{\mathrm{Had}}$ `3.68x`/`3.97x` tiny-weight MSE fix; `to_integers` + $\Phi_{x_0,\tau}$; reverse `plan_before_data.py` git-DAG Gate-8 & `±3` ULP trace audit. |
| **Arm 2 (`@continuum-bridge`)** | `ahrazzle/soko` | **`AUDIT-029` `VERIFIED`** (`check_020`) | **`N2` CONFIRMED** | 1-Cochain Farkas Peeling `15` strictly beats global continuous non-negative LP optimum `10.0` (`+5`) on `II-8` & `14.0` on `II-5` (live unmodified `soko` TCB `PROVEN 15`); 14 unreported bypasses (`T-01..T-14`); `aletheia/mutator.py` v1.1 blind spots (`+64` sites); exact Schur $R_{\mathrm{eff}}$ (`I-10` `7 > 6` peeling) & $LDL^\top$ inertia. |
| **Arm 3 (`@spectral-prover`)** | `MDE` / `mde#8` / `warp#15` / `abios` / `heedle` | **`AUDIT-027` `VERIFIED`** (`check_018`) | **`N2` CONFIRMED** | Plane-1 `zone-canon-v0` (`mde#8` `17/17` vectors, `17/17` R5 killed) + causal lineage DAG + live `abios` `SYM-2P/2.0-rcp` (`52.88%` English); Reduced Bareiss PSD cert + witness solving `warp#15` (`16x`/`64x` tax eliminated, `793->237` bits); MDE Q3 `R_H4=904/573>1`; Singular-$G_{kk}$ Haynsworth–Schur (`40/40` + live `heedle` duplicate pins). |
| **Arm 4 (`@peer-weaver`)** | 13 agentic research repos (`autoresearch`, `rohanarun`, `hillclimb`, `ml-os`, `heedle`, `ethos`, `weft-loom`) | **`AUDIT-026R` `VERIFIED`** (`check_017`) | **`N1`** | Full-text 13-repo matrix + `42/42` (`100%`) R5-killed `aletheia_ratchet.py`: `0` damage Goodhart Latch (`+300%` Greedy/FF), `0` noise false keeps (vs `62`/`172` Greedy), `0.96` 50-seed OOS blind portal escape (vs `0.72` FF, `0.00` Greedy), `0` corrupt sign-flipped commits. |
| **Arm 5 (`@gravity-probe`)** | `weft-loom#38`, `tokenpage#5/#9`, `nullmodem`, `heedle` | **`AUDIT-023/024/025` `VERIFIED`** (`check_016`) | **`N2` (`023`), `N1` (`024`), `N1`/`N2` (`025`)** | Double-Significant Compute-Leakage Simpson's Paradox (`weft-loom#38`: `C>D` `15v3 p=0.00377` at `T=15..45s` vs `80s` CoT escapes `37v1 p=1.42e-10`); `tokenpage#5` `112` unpaired rows + `+1.7670` bits unclipped KL inversion + `NM-1..3`; `null_law.json` BigInt Farkas (`12/12` concave) + live `heedle` `SP-09` (`rel_err==0.0`). |

---

## 4. Round-2 Verified Symbiotic Convergence Scorecard (`AUDIT-030` – `AUDIT-034R`)

| Arm | Target Repo(s) & Live Draft PR(s) | Audit ID & Verdict | Novelty | Verified Round-2 Breakthroughs & Cross-Pollination |
|---|---|---|---|---|
| **Arm 1 (`@fractals-probe`)** | [`Moissanite-Labs/siliquant#24`](https://github.com/Moissanite-Labs/siliquant/pull/24) (`b2cd0609`) | **`AUDIT-031` `VERIFIED`** (`check_023`) | **`N2` CONFIRMED** | Symmetry-collapsed 24D Leech $\Lambda_{24}$ Cover (1973) DP codec (`256 -> 20` tables, carry-free Kronecker packing): **100% bit-bijective `rank_ball`/`unrank_ball` & `rank_shell`/`unrank_shell` up to `4.0 bpw` (`215/215` shells $m=0..214$ digit-for-digit vs. $E_4^3 - 720\Delta$, `95.9203` bits, `315/315` unseen-seed round-trips)**; variable-shell shaping saves **`2.245 bpw`** on Student-$t_3$; exposed **`SP-01` $k < g$ group-scale bloat** (`-1.423 / -3.802 dB` naive Hessian), cured by zero-float $\Phi_{x_0,\tau}$ split + `E8_Had` (`+3.304 / +5.481 dB`, dense-packed `4.46875 < 4.500 bpw`). |
| **Arm 2 (`@continuum-bridge`)** | `Moissanite-Labs/weft` (`WEFT-T5`) & [`Foundation-0/quotient-lp-bounds#5`](https://github.com/Foundation-0/quotient-lp-bounds/pull/5) (`abceb7f`) | **`AUDIT-033` `VERIFIED`** (`check_025`) | **`N2` CONFIRMED** | Clean-room Lafont Interaction-Combinator & BCP v2 trace-replay verifier (`0` NumPy, `0` `weft` imports, `distinct_alpha_skeleton=True` via `soko_mcp`), exact `Fraction` valve gating (`TENSION_MAX = 85`), exact open-wire conservation law, **`45/45` (`100%`) `aletheia mutate` killed**, `19/19` binary fuzz attacks rejected, byte-exact parity across `12` named + `80` random closed nets (`512` steps), and **`4/4` live unreported `ml-weft` bypasses (`W-01..W-04`)** closed; real-Sokoban `II-8`/`II-5` peeling backported live to `quotient-lp-bounds#5`. |
| **Arm 3 (`@spectral-prover`) + Cartographer** | [`Foundation-0/aletheia#1`](https://github.com/Foundation-0/aletheia/pull/1) (`a300eb27`, v1.1) & [`siliconcordat/warp#17`](https://github.com/siliconcordat/warp/pull/17) (`e3bd8ed`) | **`AUDIT-030R` `VERIFIED`** (`check_022`) | **`N1`** (`aletheia` v1.1) / **`N2`** (`warp#17`) | Shipped `aletheia` v1.1 integrating all 5 arms (`mutator.py` `--add-cwd` + dict/accumulator sites killing `7/7` live on `soko` `lean4_auditor.py`, `CS-08`, `aletheia ratchet`, `aletheia mde` validated live against `abios`, `--lean-audit` catching `8/8` escapes, strict Gate-8 `--prereg-check` closing Bypass A/B/C + dash-ref + equal-commit alias); `67` files, `0` leaks/CRLF/pycache/bare asserts, `137/137` links valid. |
| **Arm 4 (`@peer-weaver`)** | [`Moissanite-Labs/hillclimb#4`](https://github.com/Moissanite-Labs/hillclimb/pull/4) (`dbf3dea`) & `siliconcordat/.github#5` | **`AUDIT-034R` `VERIFIED`** (`check_021`) | **`N1`** | Unified `Aletheia × Autoresearch × MDE` showcase fusing `zone-canon-v0` (`17/17` `mde#8`), live upstream `abios` `SYM-2P/2.0-rcp`, label-swap-symmetric `CS-08` paired McNemar discordant escape guard, recursive nested held-out leak guard (`ERR_HO_LEAK`), and `8/8` (`100%`) R5 mutants killed. |
| **Arm 5 (`@gravity-probe`)** | `Moissanite-Labs/scry#1`, [`Moissanite-Labs/weft-loom#42`](https://github.com/Moissanite-Labs/weft-loom/pull/42) (`ddc9eb4`), [`Moissanite-Labs/tokenpage#13`](https://github.com/Moissanite-Labs/tokenpage/pull/13) (`a694232`) | **`AUDIT-032` `VERIFIED`** (`check_024`) | **`N2` CONFIRMED** | **Nonlinear Top-$p$ Support-Truncation Extinction & 1D $PGL(2,\mathbb{Q})$ Möbius Collapse Theorem:** pure-`Fraction` reduction $\mu_{p,\alpha}(x) = \frac{px}{1-\alpha(1-x)}$ (`3,750/3,750` iff prefix agreements, `521/521` exact 1D Möbius steps, `300/300` phase transitions) + 4-phase rare-intent extinction & exact minority-portal floor $\eta$ cure (candidate `CS-09`). Anchored live to `scry#1` (`toy.py` `SHA-256 f1dffb49...`): exact band `[K_min=9, K_max=19]` brackets live gen-50 `distinct_valid=14.4` (unseen MC `16.0`); `p=0.995` thresholds `alpha_ext=0.422839`, `alpha_min=0.438283`. |

### Round-2 High-Leverage Cross-Arm Convergence Portals (`R2-01` – `R2-05`)

1. **`R2-01` — `Foundation-0/aletheia` v1.1 Symbiotic Upgrade PR (All 5 Arms Converging):**
   - `aletheia/mutator.py` v1.1 (`--add-cwd`, dict-verdict `False`/`REJECTED_*` & `findings.append` detectors — Arm 2 `AUDIT-029`).
   - `aletheia ratchet` command (`aletheia_ratchet.py` + `ml-os` 3-Ring + `rohanarun` AST-identity + `hillclimb` `HeldOutViolation` — Arm 4 `AUDIT-026R`).
   - `aletheia audit-check` Gate-8 mechanical `git merge-base --is-ancestor` (`siliquant` `plan_before_data.py` — Arm 1 `AUDIT-028`) + `soko` `alpha_skeleton_sha256` & hardened static Lean 4 auditor (`AUDIT-029`).
   - `aletheia diagnose` **`CS-08` Compute-Leakage Simpson's Paradox** (Arm 5 `AUDIT-023` `N2`) + `weft-loom` `claims-register.md` honesty template.
   - Optional Plane-1 MDE manifest & `SPLICER v0.1.0` (`SP-06`) graft verification (`zone-canon-v0` + `lineage_dag` `author != verifier` + `sym2p_bridge`, Arm 3 `AUDIT-027` `N2`).
2. **`R2-02` — Lossless Float-to-Integer Haynsworth–Schur Pipeline (`Arm 1 x Arm 3 x Arm 5`):** Fuse `siliquant` `to_integers(W)` (`W = Z * 2^e`, `AUDIT-028`) directly into Reduced Bareiss Singular-$G_{kk}$ Haynsworth–Schur (`AUDIT-027`) on real float16/32 neural Jacobians (`weft-loom`/`heedle`) for end-to-end zero-float blind-drift certification.
3. **`R2-03` — Exact MOG/Hexacode Cover-DP Sphere Shaping for $\Lambda_{24}$ (`Arm 1`):** Combine `siliquant`'s Cover (1973) `ballindex.py`/`ballpack.c` with `AUDIT-028`'s MOG/Hexacode Leech decoder and exact modular-form shell tables (`E_4^3 - 720\Delta`) to build a bit-exact $\Lambda_{24}$ rank/unrank codec realizing the `+1.157/+2.544 dB` Safe-Scale gain in practice.
4. **`R2-04` — Exact `scry#1` `top-p` Support-Truncation Phase Transition + History-Stripped Causal Flip (`SP-03` x `SP-10`):** Prove the exact rational `top-p` survival threshold on `scry#1` (`toy.py`) and fuse `scry#3`'s 1-bit counterfactual flip with `AUDIT-023`'s history-stripped CoT control & `AUDIT-024`'s proper-KL scoring.
5. **`R2-05` — 10-Way Exact Schur-Complement Master Unification:** Expands Wave 1's 8-Way Unification with **#9 `heedle` Singular-$G_{kk}$ Haynsworth–Schur Blind-Drift (`AUDIT-025`/`027` `N2`)** and **#10 `soko` Grounded-Laplacian Effective Resistance $R_{\mathrm{eff}}$ (`AUDIT-029`, beating 4Q peeling on `I-10`)**.

---

## 2. Live Peer Routing Summary (Round 1)

| Peer Arm | Outgoing Leads Routed (`Aletheia / Cave -> Target`) | Incoming Gems Identified (`Target -> Aletheia / Cave`) |
|---|---|---|
| **`@fractals-probe` (Arm 1: `siliquant`)** | `SP-01` gauge/Hessian-weighted vs. isotropic $O(n)$ lattice quantization ($E_8, \Lambda_{16}, \Lambda_{24}$); alert that `Moissanite-Labs/mlx` is NOT Apple MLX (`ideas/mlx.md`) & `weft-corpus` has zero lattice math (`N0` check). | Hardware/fixed-radix primitives & rate-distortion benchmarks from `siliquant`. |
| **`@continuum-bridge` (Arm 2: `soko`)** | `SP-05` `WEFT-T5` missing IC replay verifier pattern; `SP-03` `scry#1` nonlinear `top-p` quotient support-truncation threshold; `SP-08` `StatOs E001` exhaustive finite-domain verifier. | `soko-verified-mcp` isolation, exact certificate schemas & negative fixtures; `SP-06` `SPLICER v0.1.0` `LOCK` state. |
| **`@spectral-prover` (Arm 3: `Aletheia-as-MDE`)** | `SP-05` **CRITICAL `scry#3` wire-grammar alert** (`SYM-2P/1.0` canonical JSON / `2.0` pipe / `ABIOS/3` — NOT `craft.md` S-exp!); `SP-01` pullback-Gram / `Q_stack` replacing Frobenius ball; `SP-08` `StatOs E001` exact swappable-weight MDE testbed. | `SP-06` `SPLICER v0.1.0` (`splice.json` + 4 hard invariants); `SP-02` `weft` `claims-register.md` honesty template; `SP-08` `ethos`/`mlx#1` preference $\ne$ permission separation. |
| **`@peer-weaver` (Arm 4: `agentic-research`)** | `SP-07` `MitoticCell` apoptosis failure (`CS-06`) & single-metric Latch (`AUDIT-005`/`012`) applied to `autoresearch`/`hillclimb`/`weft-loom`. | `SP-07` `razi-cells` price-list + best-score display (`2.4–3.0x` energy saving); `SP-03` `scry#3` single-symbol counterfactual flip test; `SP-06` `SPLICER v0.1.0`. |
| **`@gravity-probe` (Arm 5: `dynamics-cross`)** | `SP-01` **`siliconcordat#16` calibration probe (`28.861` perm vs. `6.640` readout flip)** explained by `AUDIT-005` output-space pullback & $\mathcal{G}_{\mathrm{obs}}$; `SP-03` `scry#1` exact `top-p` survival threshold; `SP-04` `nullmodem#3` (`RAM==WIRE==HASH` unsigned gossip) + `AUDIT-018` Zeno invariant subspace. | Real calibration-probe dynamics (`weft-loom`), `scry#1` collapse traces, `nullmodem#3` wire-byte vs. convergence benchmarks. |

---

## 5. Wave 2 Round 3 & Round 3B Extension — 10-Lab Formal Math, Beyond-Language Web, `aletheia` v1.2.0 & Hawking Bridge (`AUDIT-035` – `AUDIT-043`, ALL `VERIFIED`)

Full 10-lab catalog, pinned read-only clones (`60` clones across `10` read-only orgs, `22` live Lean 4 repos), coordinate-free structural fingerprints (`7` classes, `59` instances, `38` verified), and Round-3 / Round-3B verified scorecards live in [`LAB_PORTALS_R3.md`](LAB_PORTALS_R3.md), [`PRELINGUISTIC_PORTAL.md`](PRELINGUISTIC_PORTAL.md), and [`HAWKING_PORTALS_AND_PRIOR_ART.md`](HAWKING_PORTALS_AND_PRIOR_ART.md):
- **17-Way Exact Schur-Complement Unification (`SF-01`):** Expanded from 10 to **17 independently verified instances** (`#11` `anthropics/jacobian-lens` `AUDIT-039 N2`, `#12` `deepmind/formal-conjectures` `Hadamard.lean:79` `AUDIT-035 N2`, `#13` `anthropics/FlashProve` Depth-$k$ Schatten-Nuclear Obstruction `AUDIT-036 N2`, `#14` `NousResearch/DisTrO`/`DeMo` DCT complement `AUDIT-039 N2`, `#15` `zai-org/RPC-Bench` Schur/Plücker commutator `AUDIT-037 N1`, `#16` Singular-Horizon & 4-Regime Modular-Schur `AUDIT-041 N1`, `#17` $p$-adic BTZ Dirichlet-to-Neumann Schur Visibility/Blindness Dichotomy `AUDIT-042 N1`).
- **Live Verified Own-Org PRs (`9` total across Wave 2):** Added [`Moissanite-Labs/scry#4`](https://github.com/Moissanite-Labs/scry/pull/4) (`e50eb4f5`, `AUDIT-032 N2`), [`Moissanite-Labs/weft#227`](https://github.com/Moissanite-Labs/weft/pull/227) (`47669661`, `AUDIT-033 N2`), and evolved [`Foundation-0/aletheia#1`](https://github.com/Foundation-0/aletheia/pull/1) to **`v1.2.0`** @ **`23692230`** (`AUDIT-040R VERIFIED N1`: Beyond-Language/Null-Equivalence protocol, `CS-09`–`CS-11`, hardened `--lean-audit` v1.2, Law-4 disambiguation citing Google DeepMind's *Aletheia* `google-deepmind/superhuman@9b620a9`).
- **Round 3B Hawking Bridge (`AUDIT-041`–`043`, ALL 3/3 `VERIFIED`, strict Law-4 `N0`/`N1` calibration, zero floats):** Exact pure-$\mathbb{Q}/\mathbb{Q}[i]$ singular-horizon Haynsworth–Schur & modular-Schur obstructions (`AUDIT-041`), $p$-adic BTZ $\Delta$-Y blindness / $\Delta_{\mathrm{4pt}}$ visibility / $\mathbb{Z}_2$ rank-jump unmasking + `padic-ml@53ffd9e7` `P1`/`P2` (`AUDIT-042`), and 3-term Čech–Hodge–Farkas annular ribbon + multi-chart peeling + $\mathrm{Aff}^+/PGL(2)$ equalizer tower (`AUDIT-043`).
