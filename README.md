# Cave Expedition — First-Principles Discovery, Cartography & Adversarial Verification Ledger

**Start here:** [foundation-0.github.io/cave-expedition](https://foundation-0.github.io/cave-expedition/) · [Ledger](https://foundation-0.github.io/cave-expedition/ledger/) · [Joint map](https://foundation-0.github.io/cave-expedition/joint-map/) · [Reproduce](https://foundation-0.github.io/cave-expedition/reproduce/) · Twin site: [Aletheia](https://foundation-0.github.io/aletheia/)

This repo is the field record of one expedition. It holds the maps, the open questions between repos, and the independent check ledger. The method that grew out of the run lives in [Foundation-0/aletheia](https://github.com/Foundation-0/aletheia). The two sites link claim to proof in both directions. Start with the joint map on either site if you want the pair in one view.

Umbrella index, cross-domain cartography, peer-web frontier seam catalog, and independent adversarial verification ledger for the **Cave Expedition** (November 2026): an autonomous multi-agent first-principles mathematical, physical, and formal-verification expedition across the [`siliconcordat`](https://github.com/siliconcordat) and [`Foundation-0`](https://github.com/Foundation-0) repository ecosystem.

> **Provenance & Verification Discipline** *(team text, kept verbatim as on `main` at commit `9729839`)*: Every claim marked `VERIFIED` below was independently re-executed and adversarially audited against the 9-gate, R1–R5 anti-shadow protocol in [`verification/PROTOCOL.md`](verification/PROTOCOL.md) (extending `siliconcordat/loom#8` / `#9`). Exact algebraic claims are certified in zero-float rational (`Fraction`), Gaussian rational ($\mathbb{Q}(i)$), $\mathbb{Z}[\sqrt{2}]$, or exact symbolic (`SymPy`) arithmetic and independently cross-checked by clean-room Faddeev–LeVerrier/Descartes/Sturm oracles under all Python optimizer/warning parity modes (`-B`, `-O -B`, `-B -W error`). Failed prototypes and intermediate `PARTIAL/FRAGILE` / `FALSIFIED` audits are logged permanently in [`verification/AUDIT_LOG.md`](verification/AUDIT_LOG.md) per Gate 8.
>
> **Who re-executed, stated plainly:** "independently re-executed" above means re-executed by the `verifier` role of the same multi-agent expedition ([`verification/AUDIT_LOG.md`](verification/AUDIT_LOG.md), line 3). The 22 ledger rows are timestamped 2026-11-20 17:24 to 18:29. A separate team of AI agents made the outside check in [`verification/outside/`](verification/outside/). Its file says "No human has reviewed this file" ([`OUTSIDE_AUDIT.md`](verification/outside/OUTSIDE_AUDIT.md), line 114), and its disclosure says it was "Written by an automated agent team with human oversight" (line 122). `VERIFIED` is this repository's verdict: passed all applicable gates G1–G8 ([`verification/PROTOCOL.md`](verification/PROTOCOL.md), verdict table).

---

## 1. The Eight-Way Schur-Complement Claim and Its Gate-5 Ruling

**Team claim, kept verbatim** (as on `main` at commit `9729839`, 2026-11-23):

> A central empirical and mathematical finding of the expedition is that **eight distinct physical, geometric, statistical, and formal-verification frontiers across `siliconcordat` and `Foundation-0` are governed by the exact same Schur-complement / quadratic-block elimination invariant**:

**Outside ruling.** A separate outside check tested this sentence against Gate 5 of [`verification/PROTOCOL.md`](verification/PROTOCOL.md). In its weakest reading, that each row uses block elimination, the sentence is true of any block system. The check ruled: "Gate 5 is not met for the eight-way claim" ([`verification/outside/gate5-unification/README.md`](verification/outside/gate5-unification/README.md), line 157). It found rows 4 and 6 outside the stated invariant, and row 8 citing a ledger entry that contains no such reduction (Finding 2 in the same file). It proposed this wording (line 161):

> Eight frontiers each use block elimination. One pair, AUDIT-017 and AUDIT-019, is linked by an exact congruence. A shared invariant beyond the elimination identity has not been shown.

The outside team's labels are its own reading and open to correction ([`verification/outside/README.md`](verification/outside/README.md), line 38). The outside label for each row is in [`verification/OUTSIDE_RULINGS_INDEX.md`](verification/OUTSIDE_RULINGS_INDEX.md). Short references below such as `OUTSIDE_AUDIT.md`:80 are lines of [`verification/outside/OUTSIDE_AUDIT.md`](verification/outside/OUTSIDE_AUDIT.md), and `rulings.json` is [`verification/outside/rulings.json`](verification/outside/rulings.json).

### The team's original sorting (kept as recorded; novelty labels are internal)

| # | Domain / Repo | Exact Schur-Complement Mechanism | Audit & Novelty | Key Certified Invariant |
|---|---|---|---|---|
| **1** | Spectral Inertia (`siliconcordat/spectral-inertia`, `loom#7`) | Optimal scale-invariant projected-inertia envelope $R_{\mathrm{opt}}(u,t,S,b)$ | [`AUDIT-002`](verification/AUDIT_LOG.md) (**`N2`**, `exact`) | $\operatorname{rank}(P)\ge\operatorname{rank}(\Pi_{W^\perp}P\Pi_{W^\perp})\ge n_+(\Pi_{W^\perp}H\Pi_{W^\perp})\ge R_{\mathrm{opt}} = \frac{u^2}{S-t^2/b}$, integer-exact pointwise sharp |
| **2** | Higher-Moment Spectral Bounds (`siliconcordat/spectral-inertia`, `loom#10`) | Stieltjes–Hankel moment hierarchy $R_{H,2m}$ + noise-annihilating quartic SOS ($R_{W4}$) | [`AUDIT-014`](verification/AUDIT_LOG.md) (**`N2`**, `exact`) | Scan 23848 Mode B *(a two-weight model named for scan 23848: $w_1 = 0.6404^2$, $w_2 = 0.3596^2$, provenance tag `source claim` ([`verification/PROTOCOL.md`](verification/PROTOCOL.md), section 1), taken from a session transcript ([`cartography/session2_verification_map.md`](cartography/session2_verification_map.md), "Claimed Scan 23848 Calibration"); no spectrum data used)* lifted to exact `1` across $\rho\in[0,0.95]$; $R_{H4}/R_{W4}$ strictly beat $R_{\mathrm{opt}}$ on complex non-commuting $\mathbb{Q}(i)$ witnesses |
| **3** | Lattice Elasticity & Context Sheaves (`Foundation-0/incentre-lattices`, `continuum`, `loom#5`) | Cellular sheaf Laplacian elastic stiffness tensor $C = 2^{-n}(K - B^\top \Delta_{\mathcal{F}}^{-1} B)$ | [`AUDIT-004`](verification/AUDIT_LOG.md) (`N1`), [`AUDIT-019`](verification/AUDIT_LOG.md) (**`N2`**, `exact`) | Zero-float elastic Schur complement + Master Rank-1 Stress Collapse $\sigma^* = C^\top\operatorname{diag}(\tau^*)C + 2\operatorname{diag}(\tau^*)C$ along $F_n \to D_n, E_8$ |
| **4** | Coarse-Graining & Maslov Homotopy (`Foundation-0/quotient-lp-bounds`, `continuum`) | Tropical multi-quotient Farkas peeling tower + $\mathbb{Q}[q]$ Doob $h$-transform | [`AUDIT-004`](verification/AUDIT_LOG.md) (**`N2`** Part A), [`AUDIT-008R`](verification/AUDIT_LOG.md) (`N1`, `exact`) | Tightens single-quotient LP `64` $\to$ `124` (exact) *(outside: 64 is not the fair baseline, `OUTSIDE_AUDIT.md`:80)*; proves bidirectional linear-vs-tropical emergence separation & 5-state single-$q$ accidental lumpability |
| **5** | Relativistic Gravity / AeST (`Foundation-0/gravity`) | Exact Hamiltonian Schur-Complement Theorem + non-local Helmholtz Fenichel slow manifold | [`AUDIT-011R`](verification/AUDIT_LOG.md) (**`N2`**, `exact`+`num`) | $\min_{(\chi,p)} H_2 = -\frac{G_{AA}}{\widetilde{G}}\frac{D^2}{2k^2}$; closes `aest-response-gate/slow-mode` 1% gate (`24–185%` $\to$ `0.55%` / `0.00008%`) with zero fitted parameters *(outside: the 0.00008% is measured from the closure's own starting condition, not the host protocol's, `OUTSIDE_AUDIT.md`:82)* |
| **6** | Open Quantum Dynamics / Witness Map (`Foundation-0/fractals/witness-map`, `gravity`) | $16\times 16$ GKSL Lindblad Zeno Schur complement + Tomita–Takesaki KMS + EP2 Jordan blocks | [`AUDIT-018`](verification/AUDIT_LOG.md) (**`N2`**, `exact`+`anchor`) | $\Gamma_{\mathrm{eff}}^{\mathrm{int}} = 2\gamma_{\mathrm{tid}} + \frac{2g^2}{N^2\gamma_1}$; exact dipole cancellation $W_{\mathrm{CM}}=N^3 W_1$ vs $O(k^4)$ tidal rate; exact Sgr A* crossover laws matched to live `model.js` |
| **7** | High-Dimensional Optimal Packing (`Foundation-0/incentre-lattices`) | Sylvester–Hadamard ($H_8 = H_2^{\otimes 3}$) $2\times 2$ Schur-complement Loewner monotonicity along $F_8 \to E_8$ | [`AUDIT-017`](verification/AUDIT_LOG.md) (**`N2` LANDMARK**, `exact`) | Zero-trig bar-preserving fold $F_8\to E_8$ ($\det=16$, kissing 240), $G(s)\succeq 6I_8+2H_8$, zero-subdivision 293,760-coeff degree-8 $\mathbb{Z}[\sqrt{2}]$ Bernstein proof, $E_6/E_7/D_n^+$ uniqueness *(outside: a dimension obstruction, not a uniqueness theorem, `OUTSIDE_AUDIT.md`:87)* |
| **8** | Fractal Analysis & Self-Similarity (`Foundation-0/fractals`, Portal 10) | Kigami resistance renormalization Schur complement $L_{n+1}/L_{\mathrm{int}} = \rho^{-1} L_n$ | [`cartography/frontier_portals.md`](cartography/frontier_portals.md) (Portal 10) | Exact discrete resistance renormalization bridging `fractals` scaling laws, zero-log 4-ray multiplicative Farkas (`AUDIT-010`, **`N2`** Thm B), and sheaf elasticity |

---

## 2. Verified Discovery Ledger (`AUDIT-001` – `AUDIT-019`)

Every active expedition track reached `VERIFIED` status, except two early audits that did not survive their own check and have no closing row: `AUDIT-001` is `FALSIFIED` and `AUDIT-003` is `PARTIAL/FRAGILE` (see full evidence, SHA-256 digests, counterexamples, and scope notes in [`verification/AUDIT_LOG.md`](verification/AUDIT_LOG.md)):

`VERIFIED` here is this repository's verdict: passed all applicable gates G1–G8 ([`verification/PROTOCOL.md`](verification/PROTOCOL.md), verdict table). Each table shows the outside ruling next to the internal label. The outside column is copied from [`verification/OUTSIDE_RULINGS_INDEX.md`](verification/OUTSIDE_RULINGS_INDEX.md), the single source for those rulings, which also gives the internal label from each `AUDIT_LOG.md` row and the source line of each ruling. Cite a row by its audit id, its oracle class and its outside ruling (the citation rule on the [ledger page](https://foundation-0.github.io/cave-expedition/ledger/#outside)). Where a team summary uses a phrase that the outside check repaired, the repair follows it in italics. The other rows of the outside repair table ([`verification/outside/OUTSIDE_AUDIT.md`](verification/outside/OUTSIDE_AUDIT.md), lines 79 to 95) concern text in sibling drafts, not in this repository.

### Results with an internal `N2` label

*Team heading as on `main` at commit `9729839`: "Confirmed `N2` Breakthroughs (Genuine New Ground)". The outside check kept `N2` for one of these rows, AUDIT-017, with medium confidence.*

| Audit | Branch / Artifact | Oracle | Outside ruling | Summary (team wording) |
|---|---|---|---|---|
| **`AUDIT-002`** | `spectral-inertia` / `check_003_seam01_ropt.py` | `exact` | `N1`, upper end; the sharpness theorem has no written proof yet | Non-commuting complex Hermitian projected-inertia chain $\operatorname{rank}(P)\ge\operatorname{rank}(\Pi_{W^\perp}P\Pi_{W^\perp})\ge n_+(\Pi_{W^\perp}H\Pi_{W^\perp})\ge R_{\mathrm{opt}}(u,t,S,b)$ with constructive integer-exact pointwise sharpness $\min\operatorname{rank}(P)=\max(1,\lceil R_{\mathrm{opt}}\rceil)$. |
| **`AUDIT-004`** | `continuum-bridge` (`tropical_quotient_sheaf_bridge.py`) | `exact` | Part A `N0`; optimality theorem `N0`; Parts B and C not rated | Tropical multi-quotient Farkas peeling tower (`64` $\to$ `124`) *(outside: 64 is not the fair baseline, `OUTSIDE_AUDIT.md`:80)*, bidirectional linear-vs-tropical emergence counterexamples, zero-float `incentre-lattices` Bloch sheaf elastic Schur complement, and `docs/08` Context-Site Sheaf formalization. |
| **`AUDIT-009`** | `fractals-probe` (`ALL_N_DN_FOLD_PROOF.md`) | `exact` | strong `N1`, candidate `N2` | Universal all-dimension ($n\ge 3$) continuous bar-preserving non-overlapping fold $F_n \to D_n$ (discrete path Sobolev + degree-4 $\mathbb{Q}(\sqrt{2})$ Bernstein proof) + 4D Clifford-nilpotent fold $C_4^{\mathrm{nilp}}$ ($C_4^2=0$, optimal $D_4$, kissing 24) *(outside repair: "the densest lattice packing in four dimensions", `OUTSIDE_AUDIT.md`:86)*. |
| **`AUDIT-010`** | `fractals-probe` (`MULTIPLICATIVE_FARKAS_DSI_NOTE.md`) | `exact` + `sampled` | Theorems A and B `N0`; Theorem C `N1`, unchanged | Complete 4-ray zero-log multiplicative Farkas curvature theorem (`N2` Thm B for $m=4$ dyadic grids), live Sabra $\pm 5\text{ SE}$ sheaf obstructions, Portal 2 refutation of Sabra period-3 *(outside repair: the statistic has no power against period 3; no period-3 signal was detected, and Sabra has none by construction, `OUTSIDE_AUDIT.md`:83)* (exposing decaying period-2 helicity ripple), and BigInt percolation refutation of falling $D_{\mathrm{eff}}$. |
| **`AUDIT-011R`** | `gravity-probe` (`probe1_aest_helmholtz_closure.py`) | `exact` + `num` | `N1` | Zero-parameter AeST non-local Helmholtz Fenichel slow-manifold closure (`24–185%` $\to$ `0.55%` / `0.00008%`) *(outside: the 0.00008% is measured from the closure's own starting condition, `OUTSIDE_AUDIT.md`:82)*, exact Riccati lift & pole-zero duality, exact Hamiltonian Schur-Complement Theorem, and $\lambda_s=0$ Yukawa branch. |
| **`AUDIT-014`** | `spectral-prover` Track A (`higher_moments.py`) | `exact` | A2 `N0` as a theorem, `N1` for the closed form; A4 `N1`; A3 not rated | Higher-moment indefinite non-commuting spectral rank bounds: Stieltjes–Hankel $R_{H,2m}$ (Thm A2), noise-annihilating quartic SOS (Thm A3), and weighted quartic-Weyl SOS $R_{W4}$ (Thm A4); exact `1` on Scan 23848 Mode B *(the two-weight model named for scan 23848, a `source claim`; see section 1)* across $\rho\in[0,0.95]$. |
| **`AUDIT-015R`** | `spectral-prover` Track B (`box_certifier.py`) | `exact` | not checked beyond its statement | Complex $\mathbb{Q}(i)$ congruence-preconditioned multivariate Bernstein + $1\times 1$/$2\times 2$ block-Gershgorin non-affine inertia box certifier (`N1`/`N2`), hardened with symbolic & interval Hermitianity guards (`fibral#5`, 2D Bloch Dirac, 3x3 Morse saddle). |
| **`AUDIT-017`** | `fractals-probe` (`E8_SPINOR_FOLD_PROOF.md`) | `exact` | `N2`, medium confidence (bounded prior-art search) | **LANDMARK:** *(outside: "landmark" is not a protocol label, `rulings.json` folds-dn-e8 F1b)* Canonical Sylvester–Hadamard ($H_8 = H_2^{\otimes 3}$) continuous zero-trig bar-preserving non-overlapping fold $F_8 \to E_8$ (optimal 8D sphere packing, $\det=16$, kissing 240, zero-subdivision 293,760-coeff degree-8 $\mathbb{Z}[\sqrt{2}]$ Bernstein certificate over all of $\mathbb{Z}^8$) + exact $E_6/E_7/D_n^+$ uniqueness theorem *(outside repair: a dimension obstruction; the $E_6$/$E_7$ part is elementary, `OUTSIDE_AUDIT.md`:87)*. |
| **`AUDIT-018`** | `gravity-probe` (`probe4_witness_zeno_schur.py`) | `exact` + `anchor` | `N0` mathematics, `N1` at most for the model calibration | Exact $16\times 16$ symbolic GKSL Zeno Schur complement + EP2 Jordan blocks + Tomita–Takesaki KMS detailed balance + $W_{\mathrm{CM}}=N^3 W_1$ dipole cancellation unifying `loom`, `witness-map/model.js` (`0.0` / `6.43e-16` live `node` match), and `gravity` `C-03` + Sgr A* crossover masses. |
| **`AUDIT-019`** | `continuum-bridge` (`fold_sheaf_collapse.py`) | `exact` | `N1` | Universal Instantaneous Rank-1 Elastic Collapse along $F_n\to D_n$ ($\forall n\ge 3$) & $F_8\to E_8$ interior, Master Rank-1 Stress Formula, 4D Clifford-nilpotent pure-shear/zero-axial duality, 8D cyclic rank-0 floppy vs. Sylvester–Hadamard $H_8$ rank-1 auxetic `(4,4,0)` bifurcation, and exact $O(8)$-isotropic jammed $E_8$ ($A=1$) vs. $D_8$ ($A=1/3$). |

### Verified `N1` Concrete Advances & Repaired Audits

| Audit | Branch / Artifact | Oracle | Outside ruling | Summary (team wording) |
|---|---|---|---|---|
| **`AUDIT-005`** | `continuum-bridge` (`two_loop_omitted_variable.py`) | `exact` | `N0` identity, `N1` application | Exact Pythagorean inflation $\|r_{\mathrm{adapt}}\|^2=\|r^*\|^2+e_1^2/\|p_1\|^2$ and Falsifier #6 phase boundary $0<\rho_\Phi/\kappa_\perp<2$ settling `loom#9` Claim 9 *(outside repair: a tie at exactly 0 and 2; an exact first half and the total-residual form of the second half in the noiseless model; it does not settle the claim, `OUTSIDE_AUDIT.md`:91)* (`96/96` correlated non-orthonormal rational instances). |
| **`AUDIT-006R`** | `continuum-bridge` (`optimal_inertia_rank.py`) | `exact` | `Q_stack` `N0`; trace-slack `N0`, a certified sufficient condition; cross-ratio study not checked | `warp#15` stacked-adapter Gram $Q_{\mathrm{stack}}(s)$ (eliminating $16\times$ Cauchy–Schwarz tax), trace-slack law $\Delta t^*=w^2/q$ *(outside ruling, `rulings.json` twoloop-stack F5: a trace-slack threshold, not an exact law; a certified sufficient condition, worst case 4.8% above 1/360; `N0`, first-order perturbation estimate)*, hardened canonical `to_frac`, and Portal 11 `project-asma` $PGL(2)$ Möbius cross-ratio invariance (`CR3=27/19`, `CR4=9/7`) *(not checked by the outside team, `OUTSIDE_AUDIT.md`:115; `N0` per project-asma and aletheia; tests the model class and does not separate the four Lean worlds; see Portal 11 in [`cartography/frontier_portals.md`](cartography/frontier_portals.md))*. |
| **`AUDIT-007R`** | `continuum-bridge` (`audit_continuum_probes.py`) | `sampled` | not checked | Repaired lag-scanned quadratic Koopman-Sheaf probe (`z_mean=+3.39..+5.17` on lag-0/$\pm 12$ coupled Rössler vs. all 7 nulls incl. twin uncoupled Rössler & OOD Lorenz). |
| **`AUDIT-008R`** | `continuum-bridge` (`portal78_homotopy_bregman_bridge.py`) | `exact` | Maslov–Doob identity `N0`; other parts not rated | Portal 7 $\mathbb{Q}[q]$ Maslov–Doob homotopy + 5-state row-normalized single-$q$ accidental lumpability (`q=1/2`) + Portal 8 exact finite-step cubic-Bregman Pythagoras on curved Pythagorean cones. |
| **`AUDIT-012`** | `gravity-probe` (`probe2_latch_outside_anchors_and_chirp.py`) | `sampled` + `exact` | `N1`, reworded; chirp estimator not checked | Decisive sample-disjoint LOCO falsification of `wave7` 185 km/s threshold (`73.9` / `60.15 km/s` ODR) *(outside repair: the zero-parameter model is not falsified, its chi-squared is acceptable on every catalog, and 60.15 is an optimiser artifact, `OUTSIDE_AUDIT.md`:81)*, `SPARC -> KiDS-1000` `d_s=0.94` failure, and repaired blind scale-invariant Box–Cox chirp (`0/15` FPs on red noise/IAAFT/glitches). |
| **`AUDIT-013R`** | `gravity-probe` (`probe3_nonaffine_inertia_box_certifier.py`) | `exact` | `N1` | Zero-float `Fraction`+`isqrt` Bunch–Kaufman congruence + Levy–Desplanques Gershgorin inertia box certifier on real piecewise `fibral-rigidity#5` ($L_1+L_2=2$), AeST $H_2$ (incl. $\lambda_s=0$ Box D `[2,0,1]`), and `point-charges` $C_3/C_4$. |
| **`AUDIT-016R`** | `spectral-prover` Track C (`dual_oracle.py`, `exact_qi.py`) | `exact` | `N1` for the checker | Hardened dual-oracle $\mathbb{Q}(i)$ TCB (`PLDL*`, `C M C*=D`, Faddeev–LeVerrier+Descartes+Sturm), `41/41` killed R5 mutants (`0` survivors), plus `uncompiled_source` Lean 4 `Basic.lean` *(outside note: it compiles against a current Mathlib after small edits; no script in this repository reruns that, `OUTSIDE_AUDIT.md`:95)*. |
| **`AUDIT-001` / `003`** | Early session blueprint audits (`FALSIFIED` / `PARTIAL`) | `exact` / `sampled` | not checked | Exposed missing $P\succeq 0$ forgery (`Q=diag(10,0)` certifying `rank>=117`) + 5 TCB bugs in raw Session 2 draft and CKA/persistence-entropy false positives in raw Session 1 prototypes — directly motivating the hardened verified replacements above. |

> **Team note, kept verbatim** (as on `main` at commit `9729839`): **Active Frontier (Pending Independent Audit — Not Yet Included as `VERIFIED`):** `fractals-probe` has submitted Deliverable 4 (`BW16_LEECH24_UNJAMMING_PROOF.md` / `verify_bw16_leech24.py`: irreducible root-graph obstruction $F_{16}\not\to E_8\oplus E_8$ + exact bar-preserving realizations and zero-float global-$\mathbb{Z}^n$ unjamming of 16D Barnes–Wall $\Lambda_{16}$ and 24D Leech $\Lambda_{24}/\sqrt{2}$) to the verifier queue. Its verdict will be recorded in `AUDIT_LOG.md` only after independent clean-room audit completes.
>
> **State at commit `9729839`:** this deliverable is AUDIT-020, with its re-audit AUDIT-020R; `verification/checks/check_013_bw16_leech24.py` and `check_014_bw16_leech24_reaudit.py` name those ids. Both rows are recorded only on pull request [#1](https://github.com/Foundation-0/cave-expedition/pull/1) (branch `expedition/sync-audit-020r-and-pr-links`), not in `verification/AUDIT_LOG.md` on `main` ([`verification/outside/README.md`](verification/outside/README.md), lines 22 to 28). The outside check read AUDIT-020R at that branch's commit `872fffd` as `N1` ([`OUTSIDE_AUDIT.md`](verification/outside/OUTSIDE_AUDIT.md), line 57) and repaired "unjamming" to "all non-bar inter-cell contacts strictly open" (line 88).

---

## 3. Repository Map

```text
cave-expedition/
├── README.md                                  # Executive map, 8-way Schur claim with its Gate-5 ruling, ledger & repro guide
├── LICENSE                                    # Apache License 2.0
├── cartography/
│   ├── session1_instrument_map.md             # Extracted mathematical objects, operators/sheaves & falsifiable entry points (Session 1)
│   ├── session2_verification_map.md           # Formal verification architecture, quadratic-form/chimeric rank bounds & repo graph (Session 2)
│   ├── frontier_portals.md                    # 11 steelmanned cross-domain discovery portals (Portals 1–11) & full audit tracking
│   └── entry_points.json                      # Machine-readable catalog of 11 falsifiable entry points (ep-01..ep-11)
├── peer-web/
│   ├── PEER_WEB.md                            # Live multi-repo frontier map across siliconcordat, Foundation-0, Proven-Commons & peers
│   └── frontier_seams.json                    # Structured catalog of high-leverage cross-repo seams (SEAM-01..SEAM-09)
├── docs/                                      # GitHub Pages site (foundation-0.github.io/cave-expedition), twin of aletheia site
└── verification/
    ├── PROTOCOL.md                            # 9-gate, R1–R5 anti-shadow adversarial verification protocol (v2)
    ├── AUDIT_LOG.md                           # Permanent chronological ledger of all audits (AUDIT-001..AUDIT-019)
    ├── OUTSIDE_RULINGS_INDEX.md               # Internal label beside the outside ruling, per audit (single source)
    ├── outside/                               # Outside-observer checks and rulings (contributed from outside; not edited by the team)
    └── checks/                                # All 12 independent adversarial verification scripts (check_001..check_012)
        ├── check_001_lemma32_and_tcb.py
        ├── check_002_session1_instruments.py
        ├── check_003_seam01_ropt.py           # Zero-dependency standalone stdlib verifier (AUDIT-002)
        ├── check_004_continuum_bridge_suite.py
        ├── check_005_portal78.py
        ├── check_006_fractals_deliverables.py
        ├── check_007_gravity_probes.py
        ├── check_008_spectral_inertia.py
        ├── check_009_e8_spinor_fold.py
        ├── check_010_spectral_inertia_reaudit.py
        ├── check_011_gravity_reaudit_and_probe4.py
        └── check_012_continuum_bridge_reaudit_and_fold_sheaf.py
```

**Deliberately Excluded:** Private raw conversation session dumps (`<gemini-sessions>/`), local machine scratch/workshop files (`<local-workshop>/`), upstream repo clones, virtual environments, and byte-compiled caches are excluded from this repository. All file paths in docs and check scripts have been sanitized and parameterized via environment variables (`EXPEDITION_ROOT`, `GEMINI_SESSIONS_DIR`).

---

## 4. Sibling Repositories & Draft PRs

This umbrella repository holds the expedition's shared cartography, peer-web seam map, and independent verifier suite. Domain-specific proofs, instruments, and certificates live in their dedicated standalone repositories and Draft PRs (master live index maintained on [`siliconcordat/.github#5`](https://github.com/siliconcordat/.github/issues/5)):

- **Spectral Inertia & Higher-Moment Bounds (Standalone Public Repo):** [`siliconcordat/spectral-inertia`](https://github.com/siliconcordat/spectral-inertia) (`AUDIT-002`, `014`, `015R`, `016R`)
- **Loom Higher-Moment Note (Draft PR):** [`siliconcordat/loom#10`](https://github.com/siliconcordat/loom/pull/10) (`docs/11-spectral-inertia-higher-moments.md`)
- **Relativistic Gravity — AeST Helmholtz Schur, Latch LOCO & Box Certifier (Draft PR):** [`Foundation-0/gravity#30`](https://github.com/Foundation-0/gravity/pull/30) (Probes 1–3: `AUDIT-011R`, `012`, `013R`)
- **Witness-Map GKSL Zeno Schur Complement (Draft PR):** [`Foundation-0/fractals#59`](https://github.com/Foundation-0/fractals/pull/59) (Probe 4: `AUDIT-018`)
- **Lattice Folding ($F_n\to D_n$, $F_8\to E_8$) & Multiplicative Farkas DSI (Sibling Draft PRs):** [`Foundation-0/incentre-lattices`](https://github.com/Foundation-0/incentre-lattices) (`AUDIT-009`, `017`) and [`Foundation-0/fractals`](https://github.com/Foundation-0/fractals) (`AUDIT-010`)
- **Sheaf Elastic Collapse, Tropical Peeling, Contextual Compute & Asma Cross-Ratio (Sibling Draft PRs):** [`Foundation-0/continuum`](https://github.com/Foundation-0/continuum), [`Foundation-0/incentre-lattices`](https://github.com/Foundation-0/incentre-lattices), [`Foundation-0/quotient-lp-bounds`](https://github.com/Foundation-0/quotient-lp-bounds), and [`Foundation-0/project-asma`](https://github.com/Foundation-0/project-asma) (`AUDIT-004`, `005`, `006R`, `007R`, `008R`, `019`). The project-asma part is no longer a draft: it was merged as pull request 101 (commit `f2f92ee`, 2026-11-22) into `studies/expedition-mobius-ropt/`, where project-asma labels it "Author self-checked", with "no in-repo second checker or ledger row yet" and novelty `N0` (`studies/expedition-mobius-ropt/README.md`, line 3, at project-asma commit `de88b12`)

---

## 5. Exact Reproduction

### Standalone Zero-Dependency Verification (`AUDIT-002`, pure Python 3 stdlib)

Run under all three Gate 7 (R4) optimizer/warning parity modes directly from a fresh clone of this repository:

```bash
python3 -I -B verification/checks/check_003_seam01_ropt.py
python3 -I -O -B verification/checks/check_003_seam01_ropt.py
python3 -I -B -W error verification/checks/check_003_seam01_ropt.py
```

### Cross-Repository Audit Suite (`check_001` – `check_012`)

Scripts `check_004`–`check_012` independently import and audit the sibling instruments, proofs, and upstream reference models via `EXPEDITION_ROOT` (defaulting to the repo root if unset). Scripts `check_001`–`check_002` target the private raw session transcripts via `GEMINI_SESSIONS_DIR`.

| Script | Audits Covered | Oracle Class | Runtime Dependencies | Target Layout Under `EXPEDITION_ROOT` |
|---|---|---|---|---|
| `check_001_lemma32_and_tcb.py` | `AUDIT-001`, `002` | `exact` | Python 3 stdlib | `GEMINI_SESSIONS_DIR` (raw S2 `pair_06_block_00.py`) |
| `check_002_session1_instruments.py` | `AUDIT-003` | `sampled` + `exact` | `numpy`, `scipy` | `GEMINI_SESSIONS_DIR` (raw S1 `code_blocks/`) |
| `check_003_seam01_ropt.py` | `AUDIT-002` | `exact` | **Python 3 stdlib only** | **Standalone (no external files required)** |
| `check_004_continuum_bridge_suite.py` | `AUDIT-004`, `005`, `006`, `007` | `exact` + `sampled` | `numpy` | `synthesis/` |
| `check_005_portal78.py` | `AUDIT-008` | `exact` | Python 3 stdlib | `synthesis/` |
| `check_006_fractals_deliverables.py` | `AUDIT-009`, `010` | `exact` + `sampled` | `numpy`, `node` | `probes/fractals/`, `repos/fractals/` |
| `check_007_gravity_probes.py` | `AUDIT-011`, `012`, `013` | `exact` + `sampled` | `sympy`, `numpy`, `scipy` | `probes/gravity/`, `repos/gravity/`, `repos/point-charges/` |
| `check_008_spectral_inertia.py` | `AUDIT-014`, `015`, `016` | `exact` | `sympy` | `branches/spectral-inertia/` (`siliconcordat/spectral-inertia`) |
| `check_009_e8_spinor_fold.py` | `AUDIT-017` | `exact` | `sympy` | `probes/fractals/` |
| `check_010_spectral_inertia_reaudit.py` | `AUDIT-015R`, `016R` | `exact` | Python 3 stdlib | `branches/spectral-inertia/` (`siliconcordat/spectral-inertia`) |
| `check_011_gravity_reaudit_and_probe4.py` | `AUDIT-011R`, `013R`, `018` | `exact` + `anchor` | `sympy`, `node` | `probes/gravity/`, `repos/fractals/witness-map/` |
| `check_012_continuum_bridge_reaudit_and_fold_sheaf.py` | `AUDIT-006R`, `007R`, `008R`, `019` | `exact` + `sampled` | `sympy`, `numpy` | `synthesis/`, `repos/project-asma/` (imports `optimal_inertia_rank` from `synthesis/`; its public copy is project-asma `studies/expedition-mobius-ropt/optimal_inertia_rank.py` at `f2f92ee`. Reads `repos/project-asma/formal/AsmaIdentifiabilityProofs.lean` and matches four literal substrings, two with double spaces, line 399 of the script) |

**About the name "Scan 23848".** In these checks it names a two-weight synthetic model, not a spectrum: `check_003_seam01_ropt.py` (lines 460 to 470) hard-codes $w_1 = (6404/10000)^2$ and $w_2 = (3596/10000)^2$ and reads no file. Its output key `scan23848_mode_b_comparison` stays as it is, because renaming it would change the stdout bytes that CI and the outside Gate-5 anchor pin. The name also comes from upstream: `check_008_spectral_inertia.py` (line 60) imports `spectral_inertia.examples.scan23848_benchmark` from `siliconcordat/spectral-inertia`, and the AUDIT-014 row cites `scan23848_benchmark.py`. The source-verified record of the real scan is in Foundation-0/project-asma, `CLAIMS.md` row V38; see the provenance note in [`cartography/session2_verification_map.md`](cartography/session2_verification_map.md).

Example cross-repo audit invocation:

```bash
export EXPEDITION_ROOT=/path/to/expedition
python3 -I -B verification/checks/check_010_spectral_inertia_reaudit.py
python3 -I -O -B verification/checks/check_010_spectral_inertia_reaudit.py
python3 -I -B -W error verification/checks/check_010_spectral_inertia_reaudit.py
```

---

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
