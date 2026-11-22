# Cave Expedition — Wave 2+ Compute Handoff Specification

**Schema Companion:** [`next_waves_manifest.json`](next_waves_manifest.json) (`expedition.next_waves.v1`)  
**Methodology Companion:** [`METHODOLOGY.md`](METHODOLOGY.md) & [`templates/portal-swarm-protocol.md`](templates/portal-swarm-protocol.md)  
**Verification Standard:** [`verification/PROTOCOL.md`](verification/PROTOCOL.md) & [`verification/AUDIT_LOG.md`](verification/AUDIT_LOG.md) (`AUDIT-001`–`AUDIT-020R`)  
**Master Bus Anchor:** [siliconcordat/.github#5 (Wave 1 Index Comment)](https://github.com/siliconcordat/.github/issues/5#issuecomment-7054768981)

---

## 1. Purpose & Portability Contract

Wave 1 ran on a lightweight local workstation and produced **10 distinct confirmed `N2` breakthroughs** (`AUDIT-002`, `004`, `009`, `010`, `011R`, `014`, `017`, `018`, `019`, `020R`), **`AUDIT-015R` (`N1`/`N2`)**, and hardened `N1` instruments (`AUDIT-001`–`AUDIT-020R`, `0` unresolved defects), all packaged across 2 canonical public repositories and 10 open Draft PRs (`0` merged to default branches). Several high-leverage frontiers surfaced by Wave 1 now require heavier multi-core CPU, larger RAM, a full Lean 4 / Mathlib toolchain, real astrophysical / telemetry archives, or GPU-hosted open-weights checkpoints.

This document is a **zero-context-loss portable execution specification** for any stronger workstation, cluster, or Wave 2+ AI research swarm:
1. **Bootstrap & baseline verification first:** Clone `Foundation-0/cave-expedition` plus the target repo/Draft PR below, and re-run the pinned Wave 1 command under `python3 -I -O -B -W error` before running new experiments.
2. **Portal-Driven Discovery Loop:** Apply `METHODOLOGY.md` and `templates/portal-swarm-protocol.md` continuously — keep an active Portal-Keeper / Cartographer in the loop, steelman anomalies before dismissal, and subject every new claim to independent zero-shared-code adversarial verification (`verification/PROTOCOL.md` Gates G1–G9, R1–R5, `-I -O -B -W error`, full-text prior-art audit).
3. **Publishing discipline:** Never merge to default branches. Open clean Draft PRs (or stacked commits on dedicated `expedition/wave2-*` branches), zero personal paths, zero secrets, LF-only, `0` bare `assert`s on trust paths.

---

## 2. Compute Tiers & Toolchain Prerequisites

| Tier | Recommended Hardware | Required Software / Toolchain | Wave 2 Workloads |
|---|---|---|---|
| **Tier 1 (Multi-Core Exact & Scientific CPU)** | 16–32 CPU cores, 32–64 GiB RAM | Python 3.12+ (`numpy`, `scipy`, `sympy`, `h5py` for GWOSC), Node 18+, `git`, `gh` | `W2A-2`, `W2A-3`, `W2B-1`, `W2B-2`, `W2B-3`, `W2D-1`, `W2D-2` |
| **Tier 2 (Heavy Exact Algebra / Formal Proof)** | 64+ CPU cores, 128–256 GiB RAM | Tier 1 + `elan` / Lean 4 + Mathlib (`lake`), optional `flint`/`pari`/`cvxpy` (proposer-side only; checkers remain pure exact rational!) | `W2A-1`, `W2C-1`, `W2C-2`, `W2C-3` |
| **Tier 3 (GPU Model & Adapter Serving)** | 1–2x 24–80 GB VRAM GPU, 64+ GiB RAM | Tier 1 + `llama.cpp` / `llama-server`, `torch`, open-weights base checkpoint + LoRA adapters | `W2D-3` |

### Universal Wave 1 Baseline Bootstrap
```bash
git clone https://github.com/Foundation-0/cave-expedition.git
cd cave-expedition
gh pr checkout 1   # sync commit 377392b (AUDIT-001..020R + checks 001..014)
python3 -I -O -B -W error verification/checks/check_003_seam01_ropt.py
```

---

## 3. Wave 2A — Heavy Exact Lattice & Combinatorial Search

### `W2A-1`: Global Bar-Preserving Continuation (or Obstruction) for 16D Barnes–Wall $\Lambda_{16}$ & 24D Leech $\Lambda_{24}/\sqrt{2}$
- **Target Repo & PR:** `Foundation-0/incentre-lattices` (`main` `2d374ff`), Draft PR [#106](https://github.com/Foundation-0/incentre-lattices/pull/106) (`expedition/all-n-dn-and-e8-folds`, head `33ff6da`, `results/expedition-dn-e8-folds/`)
- **Wave 1 Verified Baseline:** `AUDIT-020R` (`VERIFIED` | `exact` | `N2`): Irreducible Root-Graph Obstruction ($F_{16}\not\to E_8\oplus E_8$ and all nontrivial orthogonal direct sums), exact positive-orientation bar-preserving realizations of $\Lambda_{16}$ ($\det=+2$, kissing `4,320`, `0` neg / `137,280` contacts) and $\Lambda_{24}/\sqrt{2}$ ($\det=+3/256$, kissing `196,560`, `0` neg / `9,432,672` contacts via Golay self-duality), and certified global-$\mathbb{Z}^n$ expanding bar-preserving Cayley arcs $\tau_{16}^*\in[0,1/4000]$ and $\tau_{24}^*\in[0,10^{-10}]$ (SHA-256 `5dbdeb6f470483242705bb632f6dcaa41ec58bb4f8ee7c3d28f2a6b5ab25cadc`).
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/incentre-lattices.git && cd incentre-lattices
  gh pr checkout 106
  cd results/expedition-dn-e8-folds
  python3 -I -O -B -W error verify_bw16_leech24.py
  ```
- **Compute Tier:** Tier 2 (64+ cores / 128 GiB RAM for exact rational SDP/SOS + parallelized automorphism-orbit pruning). *Algorithmic note:* Direct $R^2=11$ ellipsoid enumeration contains $\sim 4\times 10^7$ points in 16D and $\sim 1.1\times 10^{13}$ points in 24D, so Wave 2A **must** search for a **dimension-free / Loewner / block-diagonal analytical invariant** (analogous to `AUDIT-017`'s exact $2\times 2$ block-diagonalization and $G(s)\succeq G(1)$ Loewner dominance for $F_8\to E_8$) or an exact global obstruction.
- **Hypothesis & Discovery Goal:** Determine whether a continuous, bar-preserving, globally non-overlapping path connects $\Lambda_{16}$ to $F_{16}$ and/or $\Lambda_{24}/\sqrt{2}$ to $F_{24}$ (via symmetric/Hadamard/Golay coset generators `C` with positive-definite Loewner Gram trajectory $G(s)\succeq G(1)$), OR prove a global topological/combinatorial separation obstruction.
- **Oracle & Falsification Gate:** `exact` (pure `Fraction` / $\mathbb{Z}[\sqrt{2}]$ / Bernstein polynomial certificate). **Falsified if** any candidate curve violates exact bar norm $\|u_i(s)\|^2 \equiv 2$, changes $\operatorname{sgn}\det L(s)$, or produces a single contact norm $< 2$ on $\mathbb{Z}^n$ (tested against independent random lattice-vector & shortest-vector LLL/BKZ adversary searches).

### `W2A-2`: 24D Leech $O(24)$-Isotropic Elastic Collapse & Symmetric Hadamard/Golay Generator Search
- **Target Repo & PRs:** `Foundation-0/incentre-lattices` (`main` `2d374ff`), Draft PR [#107](https://github.com/Foundation-0/incentre-lattices/pull/107) (`expedition/fold-sheaf-collapse`, head `edc795b`, `results/expedition-fold-sheaf-collapse/fold_sheaf_collapse.py`) & PR [#106](https://github.com/Foundation-0/incentre-lattices/pull/106) (`33ff6da`)
- **Wave 1 Verified Baseline:** `AUDIT-019` (`VERIFIED` | `exact` | `N2`): Master Rank-1 Stress Formula $\sigma^* = C^\top\operatorname{diag}(\tau^*)C + 2\operatorname{diag}(\tau^*)C$, 8D $F_8\to E_8$ bifurcation (cyclic $\mathbb{Z}/16\mathbb{Z}$ $\ker(\phi)$ rank-0 floppy vs. Sylvester–Hadamard $C_8=\tfrac12 H_8$ rank-1 auxetic `(4,4,0)`), and exact $O(4)/O(8)$ jammed isotropy $A(D_4)=A(E_8)=1$ (vs $A(D_8)=1/3$).
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/incentre-lattices.git && cd incentre-lattices
  gh pr checkout 107
  python3 -I -O -B -W error results/expedition-fold-sheaf-collapse/fold_sheaf_collapse.py
  ```
- **Compute Tier:** Tier 1 (16–32 cores, 32 GiB RAM; exact `Fraction` $300\times 300$ fourth-order Voigt elasticity tensor in 24D and exact orbit search over Golay/Paley/Hadamard $24\times 24$ generators).
- **Hypothesis & Discovery Goal:**
  1. Compute the exact zero-float 24D Cauchy–Born elasticity tensor of the 196,560-vector Leech lattice $\Lambda_{24}/\sqrt{2}$ (a spherical 11-design!) and test exact $O(24)$ isotropy ($A(\Lambda_{24}) = 1$, exact Lamé ratio $\lambda/\mu$ vs. $D_{24}$).
  2. Test whether `U24_WITNESS` (or any diagonally symmetrizable $24\times 24$ Golay/Hadamard coset generator $C_{24}$) produces a **rank-0 floppy vs. rank-1 auxetic bifurcation** in 24D analogous to 8D $F_8\to E_8$ (`AUDIT-019`), and compute exact `C_24` sheaf cohomology $(H^0, H^1)$ and stress inertia.
- **Oracle & Falsification Gate:** `exact` (pure `Fraction` + independent Descartes/LDL inertia). **Falsified if** Cauchy–Born $E_{ijkl}$ breaks exact $O(24)$ isotropy ($C_{11}-C_{12}-2C_{44}\ne 0$) or if no bar-preserving $\Lambda_{24}$ generator is diagonally symmetrizable (which itself would be a verified structural obstruction!).

### `W2A-3`: $m \ge 5$ Dyadic Farkas Extremal-Ray Classification & Multi-Scale Curvature Completeness
- **Target Repo & PR:** `Foundation-0/fractals` (`main` `48b923b`), Draft PR [#60](https://github.com/Foundation-0/fractals/pull/60) (`43therean:expedition/mult-farkas-dsi`, head `f6cb822`, `studies/expedition-mult-farkas-dsi/`)
- **Wave 1 Verified Baseline:** `AUDIT-010` (`VERIFIED` | `exact` + `sampled` | `N2` Thm B): Complete 4-ray zero-log Farkas curvature characterization for $m=4$ dyadic grids (`500/500` vs Fourier–Motzkin), plus `@verifier`'s explicit $m=5$ counterexample ray `(3,2,1)` proving new extremal rays emerge at $m \ge 5$.
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/fractals.git && cd fractals
  gh pr checkout 60
  cd studies/expedition-mult-farkas-dsi
  python3 -I -O -B -W error verify_mult_farkas_dsi.py > /dev/null
  ```
- **Compute Tier:** Tier 1 (16–32 cores, 32–64 GiB RAM; exact double-description / Fourier–Motzkin extremal-ray enumeration in $\mathbb{Q}$ for $m=5, 6, 7, 8$, plus large multi-seed `critical/model.js` & `turbulence/model.js` ensembles).
- **Hypothesis & Discovery Goal:** Enumerate and prove the exact closed-form family of extremal Farkas rays for monotone-curvature / convex-slope zero-log cones on $m$-point dyadic grids ($m = 5, 6, 7, 8 \to$ general $m$ theorem), and deploy the $m \ge 6$ zero-log sheaf/Farkas certificate across 50-seed percolation and full 34-shell Sabra runs.
- **Oracle & Falsification Gate:** `exact` for the cone/ray theorem (bijective primal-dual LP witness match on $\ge 1,000$ random rational instances + Fourier–Motzkin double-check); `sampled` with explicit multi-seed empirical intervals for live Monte Carlo runs. **Falsified if** any feasible-cone violation escapes the proposed ray set.

---

## 4. Wave 2B — Heavy Physics PDEs & Astrophysical Sweeps

### `W2B-1`: Nonlinear AeST Spherical Collapse PDE — $\lambda_s = 0$ Yukawa Branch vs. $\lambda_s > 0$ Anti-Gravity
- **Target Repo & PR:** `Foundation-0/gravity` (`main` `8f96c4b`), Draft PR [#30](https://github.com/Foundation-0/gravity/pull/30) (`43therean:expedition/aest-schur-helmholtz-probes`, head `00d8b1b`, `studies/expedition-aest-helmholtz-probes/`) + existing repo target `research/value-assessment-20261112/closure/caustic_control.py`
- **Wave 1 Verified Baseline:** `AUDIT-011R` (`VERIFIED` | `exact` + numerical | `N2`): Zero-parameter Helmholtz-screened Fenichel slow-manifold closure (`24–27% -> 0.55%/0.00008%`), exact Hamiltonian Schur-Complement Theorem $\min_{(\chi,p)} H_2 = -\frac{G_{AA}}{\widetilde G}\frac{D^2}{2k^2}$, and `AUDIT-013R` certifying the $\lambda_s=0$ Yukawa branch uniformly as `(2,0,1)` (`907` exact rational boxes on $r\in[1,4]$).
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/gravity.git && cd gravity
  gh pr checkout 30
  python3 -I -O -B -W error studies/expedition-aest-helmholtz-probes/probe1_aest_helmholtz_closure.py
  ```
- **Compute Tier:** Tier 1 (16–32 cores, 32 GiB RAM; high-resolution 1D/3D nonlinear PDE time-stepping with grid-convergence sweeps $N \in \{256, 512, 1024, 2048\}$).
- **Hypothesis & Discovery Goal:** Compare nonlinear spherical/pancake collapse evolution in `caustic_control.py` across $\lambda_s = 0$ (exact zero-sound-speed Yukawa cutoff $G_{AA}=M_0^2/(M_0^2+k^2/a^2) > 0$) versus $\lambda_s > 0$ (UV self-repulsive anti-gravity $G_{AA} < 0$): test whether $\lambda_s = 0$ avoids caustic blowup/baryon-segregation instabilities while preserving late-time halo response.
- **Oracle & Falsification Gate:** `sampled`/numerical PDE + `exact` SymPy conservation invariants. Must pass spatial/temporal grid-refinement convergence ($L_2$ error scaling), exact energy/momentum conservation audit, and negative control (turning off coupling reproduces analytic spherical top-hat collapse). **Falsified if** $\lambda_s = 0$ develops finite-time shell-crossing caustics earlier than or indistinguishable from $\lambda_s > 0$ under converged grid resolution.

### `W2B-2`: 2D $(m, r)$ Galactic Dark-Matter Phase Diagram — Sgr A* Horizon vs. Stellar Gravitational Stirring (`tStir`)
- **Target Repo & PR:** `Foundation-0/fractals` (`main` `48b923b`), Draft PR [#59](https://github.com/Foundation-0/fractals/pull/59) (`43therean:expedition/witness-map-zeno-schur`, head `84535c1`, `studies/expedition-witness-zeno-schur/`) + `witness-map/model.js`
- **Wave 1 Verified Baseline:** `AUDIT-018` (`VERIFIED` | `exact` + `anchor` | `N2`): Exact $N^3$ CM vs. $O(k^4)$ quadrupole tidal scaling, exact $16\times 16$ zero-float GKSL Lindblad Zeno Schur-Complement Theorem + Tomita–Takesaki KMS commutation, live `node` match to `witness-map/model.js` (`6.43e-16`), and Sgr A* @ `8.18 kpc` crossover masses `2.83e-20 eV` ($\tau = t_{\text{lump}}$) and `1.34e-19 eV` ($\tau = \text{age}$).
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/fractals.git && cd fractals
  gh pr checkout 59
  python3 -I -O -B -W error studies/expedition-witness-zeno-schur/probe4_witness_zeno_schur.py
  ```
- **Compute Tier:** Tier 1 (16 cores, 32 GiB RAM; dense 2D sweep over $m\in[10^{-22}, 10^{-18}]\text{ eV}$ and galactocentric radius $r\in[10^{-3}, 10^2]\text{ kpc}$ + coupled Lindblad/Schrödinger–Poisson soliton checks).
- **Hypothesis & Discovery Goal:** Map the exact 2D $(m, r)$ crossover phase boundary comparing Sgr A* horizon CM decoherence ($\Gamma_{\mathrm{BH}}^{\mathrm{CM}} \propto m^{-10}$) against stellar gravitational stirring (`tStir` in `witness-map/model.js`), checking both CM classicalization and internal granule survival ($\mathcal{V}_{\mathrm{inv}}$) across dwarf spheroidals, Milky Way disk, and galactic center.
- **Oracle & Falsification Gate:** `exact` for analytical scaling exponents & `anchor` cross-check directly against live `node witness-map/model.js` (relative discrepancy $< 10^{-12}$ on all shared constants). **Falsified if** horizon decoherence is everywhere subdominant to `tStir` across the entire fuzzy-DM window $[10^{-22}, 10^{-18}]\text{ eV}$ or breaks internal-granule invariance.

### `W2B-3`: Real GWOSC HDF5 Strain Benchmark for Repaired Scale-Invariant Box–Cox Chirp Estimator
- **Target Repo & PR:** `Foundation-0/gravity` (`main` `8f96c4b`), Draft PR [#30](https://github.com/Foundation-0/gravity/pull/30) (`studies/expedition-aest-helmholtz-probes/probe2_latch_outside_anchors_and_chirp.py`)
- **Wave 1 Verified Baseline:** `AUDIT-012` (`VERIFIED` | `sampled` | `N1`): Repaired blind scale-invariant Box–Cox chirp estimator achieved `0/15` false positives each on fresh-seed red noise, IAAFT surrogates, and sine-Gaussian glitches ($f_0\in[70,500]\text{ Hz}$), recovering $\hat{\alpha}\approx 11/3$ across `0.7x..3.0x` scale sweeps (scope caveat: up-chirp & high-SNR $\text{noise}\le 0.08$).
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/gravity.git && cd gravity
  gh pr checkout 30
  python3 -I -O -B -W error studies/expedition-aest-helmholtz-probes/probe2_latch_outside_anchors_and_chirp.py
  ```
- **Compute Tier:** Tier 1 (16–32 cores, 32–64 GiB RAM + public GWOSC O1–O4 HDF5 strain downloads for H1/L1/V1 binary inspirals + Gravity Spy glitch catalogs: blip, koi fish, whistle, scattered light).
- **Hypothesis & Discovery Goal:** Evaluate the blind free-exponent estimator $\hat{\alpha}=\arg\min_\alpha \operatorname{Var}(\dot{f}f^{-\alpha})$ (extended to handle both up-chirps and lower-SNR multi-taper ridges!) on real open GWOSC inspiral events (`GW150914`, `GW151226`, `GW170817`, O3/O4 high-SNR BBH/BNS) against real off-source LIGO noise windows, time-slid detector pairs, and Gravity Spy glitches.
- **Oracle & Falsification Gate:** `sampled` with pre-registered ROC / false-alarm rate against time-slid background & real glitch negative controls (Gate G3 & G8). **Falsified if** false-positive rate on real LIGO whistle/blip glitches exceeds pre-registered threshold or $\hat{\alpha}$ fails to concentrate around $11/3$ (post-Newtonian leading order) on real high-SNR inspirals without hardcoded `[30,350]` Hz / `-11/3` priors.

---

## 5. Wave 2C — Higher-Moment SDP/SOS & Machine-Checked Lean 4

### `W2C-1`: Machine-Checked Lean 4 Mechanization of `SpectralInertia` & `project-asma` Möbius Cross-Ratio
- **Target Repos & PRs:**
  - `Foundation-0/spectral-inertia` (`main` `8394da9`, `lean/SpectralInertia/Basic.lean`) + `siliconcordat/loom` PR [#10](https://github.com/siliconcordat/loom/pull/10) (`77d9a7e`)
  - `Foundation-0/project-asma` (`main` `4817821`, `formal/AsmaIdentifiabilityProofs.lean`, `formal/lakefile.toml`) + Draft PR [#101](https://github.com/Foundation-0/project-asma/pull/101) (`0bef037`)
- **Wave 1 Verified Baseline:** `AUDIT-014`/`016R` (`VERIFIED`, with `Basic.lean` honestly tagged `uncompiled_source` because `lean`/`lake` was not installed on the Wave 1 machine) and `AUDIT-006R` (`VERIFIED` SymPy + `Fraction` verification of Portal 11 exact $PGL(2)$ Möbius 3-point `CR3=27/19` & 4-point `CR4=9/7` invariants across all 4 `AsmaIdentifiabilityProofs.lean` worlds).
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/spectral-inertia.git && cd spectral-inertia
  python3 -I -O -B -W error run_all.py
  # On Tier 2 machine with elan/Lean 4 + Mathlib:
  # initialize lakefile.toml pinned to Mathlib and run `lake build`
  ```
- **Compute Tier:** Tier 2 (16–64 cores, 32–64 GiB RAM, `elan` + Lean 4 + Mathlib cache).
- **Hypothesis & Discovery Goal:**
  1. Compile `lean/SpectralInertia/Basic.lean` with zero `sorry` and standard axioms only (`{propext, Quot.sound, Classical.choice}`), and lift from the scalar/polynomial lemmas to full matrix-level Mathlib proofs of: (a) $W\oplus W^\perp$ projected positive-inertia chain $n_+(\Pi_{W^\perp}H\Pi_{W^\perp}) \ge R_{\mathrm{opt}}$, (b) Sylvester's law of inertia for $n\times n$ congruence (`siliconcordat/.github#5` `T8`!), and (c) Higher-Moment Theorems A2–A4 (`AUDIT-014`).
  2. Add and `lake build` the 4-line exact `PGL(2)` Möbius 3-point (`CR3` via fixed point $q(1)=1$) & 4-point (`CR4`) cross-ratio invariance theorem directly in `Foundation-0/project-asma/formal/AsmaIdentifiabilityProofs.lean`.
- **Oracle & Falsification Gate:** `exact` (Lean 4 kernel + `#print axioms` check verifying zero `sorryAx` and zero custom axioms). **Falsified if** any lemma in `Basic.lean` requires an unstated hypothesis or fails under strict Mathlib elaboration.

### `W2C-2`: Degree-6/8 Stieltjes–Hankel & Weighted-Weyl SOS Rank Certificates on Full `project-asma` MS2 Spectra
- **Target Repos & PRs:** `Foundation-0/spectral-inertia` (`main` `8394da9`, `spectral_inertia/higher_moments.py`, `spectral_inertia/examples/scan23848_benchmark.py`) & `Foundation-0/project-asma` Draft PR [#101](https://github.com/Foundation-0/project-asma/pull/101) (`0bef037`)
- **Wave 1 Verified Baseline:** `AUDIT-014` (`VERIFIED` | `exact` | `N2`): Theorems A2 ($R_{H4}, R_{H6}$), A3 (noise-annihilating quartic SOS), and A4 (weighted quartic-Weyl SOS) passed `300/300` fresh non-commuting $\mathbb{Q}(i)$ tests (`0` violations), lifting Scan 23848 Mode B to exact `1` across $\rho\in[0,1)$ and strictly beating $\lceil R_{\mathrm{opt}}\rceil$ on non-commuting complex Hermitian matrices.
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/spectral-inertia.git && cd spectral-inertia
  python3 -I -O -B -W error spectral_inertia/examples/scan23848_benchmark.py
  ```
- **Compute Tier:** Tier 2 (32–64 cores, 64–128 GiB RAM; floating-point SDP solver `SCS`/`Clarabel`/`MOSEK` may serve strictly as an *untrusted witness proposer*, projecting onto exact `Fraction` SOS polynomials checked by pure-stdlib `spectral_inertia/dual_oracle.py`!).
- **Hypothesis & Discovery Goal:** Extend Theorems A2–A4 to degree-6/8 exact rational Stieltjes–Hankel and weighted-Weyl SOS certificates (including fusing Knausgård's clipped-trace $\varphi_c$ with $W\oplus W^\perp$ compression), and benchmark exact zero-float chimeric rank certification on full public multi-scan MS2 Gram matrices from `project-asma` (`pxd023044` and larger scans, matrix dimensions $n = 16..128$).
- **Oracle & Falsification Gate:** `exact` (every proposed rational polynomial witness MUST pass zero-float SOS factorization + dual-oracle `PLDL*`/Faddeev–LeVerrier checking under `-I -O -B -W error`). **Falsified if** higher-degree certificates fail to improve integer ceiling $\lceil \text{bound}\rceil$ over `A2`/`A4` on real MS2 Gram matrices or suffer intractable rational bit-length blowup without rational rounding/projection.

### `W2C-3`: Large-Scale Complex-Hermitian Non-Affine Parametric Box Certification (`incentre-lattices#100`, `relative-equilibria`, `certified-orbits`)
- **Target Repos & PRs:**
  - `Foundation-0/spectral-inertia` (`main` `8394da9`, `spectral_inertia/box_certifier.py`, `examples/bloch_and_hessian_boxes.py`)
  - `Foundation-0/incentre-lattices` (open PR `#100` fixed-angle fold response & spatial instability + PR `#105` Bloch rigidity)
  - `Foundation-0/relative-equilibria` & `Foundation-0/certified-orbits`
- **Wave 1 Verified Baseline:** `AUDIT-015R` (`VERIFIED` | `exact` | `N1`/`N2`): Complex-Hermitian multivariate Bernstein + $1\times 1$/$2\times 2$ block-Gershgorin box certifier validated on `10,000/10,000` polynomial enclosures, `500/500` interior Descartes points across `fibral-rigidity#5`, Bloch gapped, 3x3 Morse saddle, and complex zero-diagonal $2\times 2$ block boxes (`8/8` symbolic non-Hermitian forgeries rejected).
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/spectral-inertia.git && cd spectral-inertia
  python3 -I -O -B -W error spectral_inertia/examples/bloch_and_hessian_boxes.py
  ```
- **Compute Tier:** Tier 2 (64 cores, 128 GiB RAM; parallel branch-and-bound box subdivision in pure `Fraction` or `python-flint` checked by independent `Fraction` leaf verification).
- **Hypothesis & Discovery Goal:** Apply the symbolic-Hermitian Bernstein box certifier to continuous multi-dimensional parameter boxes:
  1. Continuous Bloch wavevector $q \in [0, 2\pi]^n$ and fold-angle boxes for `incentre-lattices#100/#105` ($n=3,4,5$, lifting `#105` from 8 isolated Pythagorean points to full gapped Brillouin zones and isolating exact acoustic/zero-mode sheets).
  2. Exact zero-float Morse-index certification for $n=6..8$ equal-mass central configurations (`relative-equilibria`) and periodic three-body stability monodromy matrices (`certified-orbits`).
- **Oracle & Falsification Gate:** `exact` (every certified leaf passes exact rational Bernstein enclosure + independent Descartes/Sturm inertia check at sampled interior rational points; symbolic Hermitianity enforced). **Falsified if** any interior Descartes evaluation disagrees with a certified box inertia.

---

## 6. Wave 2D — Large-Sample Telemetry, Large Transition Graphs & Real-Checkpoint Contextual Compute

### `W2D-1`: Production Empirical Rank-$p$ ($n_{\text{surrogates}} \ge 1000$) Quadratic-EDMD Koopman-Sheaf Benchmarks on Real Multi-Channel Archives
- **Target Repo & PR:** `Foundation-0/continuum` (`main` `1c9a9ef`), Draft PR [#3](https://github.com/Foundation-0/continuum/pull/3) (`expedition/synthesis-instruments`, head `12a1686`, `expedition-synthesis/audit_continuum_probes.py`)
- **Wave 1 Verified Baseline:** `AUDIT-007R` (`VERIFIED` | `sampled` | `N1`): Repaired `GL(4)`-invariant lag-scanned Quadratic EDMD Koopman-Sheaf passed all 7 nulls (incl. uncoupled Rössler & OOD uncoupled Lorenz `z_mean=+0.25`) while detecting lag-0, lag-12, and `+12` coupled Rössler. *Explicit `AUDIT-007R` calibration finding:* `n_surrogates=40` with max over 41 lags creates a right-skewed single-trial null tail (`6–13%` `z>3`); single-shot production telemetry requires empirical rank $p$-values at `n_surrogates >= 200` (target `>= 1000` on Tier 1 hardware).
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/continuum.git && cd continuum
  gh pr checkout 3
  python3 -I -O -B -W error expedition-synthesis/audit_continuum_probes.py
  ```
- **Compute Tier:** Tier 1 (32 cores, 64 GiB RAM; parallelized IAAFT / Lyapunov-separated circular-shift surrogate ensembles at $n_{\text{surrogates}} = 1,000$ across real public multi-channel EEG, seismic WWSSN/IRIS, and climate/ENSO time series).
- **Hypothesis & Discovery Goal:** Upgrade `audit_continuum_probes.py` from Gaussian $z$-scores to exact empirical rank $p$-values (with Benjamini–Hochberg / Westfall–Young max-lag FWER control at `n_surrogates >= 1000`) and test blind dynamical-coupling detection + lag recovery across real multi-channel physical/biological archives vs. phase-randomized & cross-subject mismatched negative controls.
- **Oracle & Falsification Gate:** `sampled` with pre-registered $\alpha = 0.01$ FWER on mismatched/IAAFT negative controls. **Falsified if** empirical false-positive rate on uncoupled real-archive pairs exceeds $2\alpha$ or fails to beat raw linear cross-correlation / CKA on nonlinearly coupled benchmarks.

### `W2D-2`: Scaling Iterative Multi-Quotient Farkas Peeling & $\mathbb{Q}[q]$ Doob Homotopy to Full `ahrazzle/soko` Transition Graphs
- **Target Repos & PRs:**
  - `Foundation-0/quotient-lp-bounds` (`main` `65d8df3`), Draft PR [#5](https://github.com/Foundation-0/quotient-lp-bounds/pull/5) (`expedition/farkas-peeling-and-doob-homotopy`, head `996108a`, `studies/expedition-farkas-peeling/`)
  - `ahrazzle/soko` (catalog rooms, III-14, III-20, III-21; peer route-replay PR `#72`)
- **Wave 1 Verified Baseline:** `AUDIT-004` (`VERIFIED` | `exact` | `N2`) & `AUDIT-008R` (`VERIFIED` | `exact` | `N1`): Iterative Multi-Quotient Farkas Peeling Tower ($c^{(j)} = c^{(j-1)} + d^0(\pi_j^* h_j^*) \ge 0$) achieved `124` exact 3-layer vs. `64` for `quotient-lp-bounds`'s `zeroSelfLoop_deficit` on a 32-state coupled system, with exact Cohomological Optimality ($H^{(K)} = d^*_G \iff \delta_{\mathrm{emg}}^{\mathrm{trop}} \equiv 0$ on co-reachable $c>0$ graphs).
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/quotient-lp-bounds.git && cd quotient-lp-bounds
  gh pr checkout 5
  python3 -I -O -B -W error studies/expedition-farkas-peeling/tropical_quotient_sheaf_bridge.py
  ```
- **Compute Tier:** Tier 1 (32 cores, 64–128 GiB RAM; exact integer/rational shortest-path + sparse quotient LP solvers over $10^4$–$10^6$ abstract Sokoban states, C++/Rust proposer + independent exact Python/C++ verifier).
- **Hypothesis & Discovery Goal:** Apply Iterative Multi-Quotient Farkas Peeling (and order-permutation maximization $\max_\sigma H_\sigma$) to real `ahrazzle/soko` Part III rooms (especially III-14, III-20, III-21 — testing directly against `soko`'s catalogued routes & `soko#72` route-replay soundness gate!), testing whether non-commutative quotient peeling raises certified lower bounds above existing single-partition operator-counting floors.
- **Oracle & Falsification Gate:** `exact` (independent 1-Lipschitz check $H^{(K)}(u)-H^{(K)}(v) \le c(u,v)$ on every concrete edge + zero-violation replay across all 66 `soko` catalog routes + `soko#76` dead-state handling). **Falsified if** any peeled bound exceeds a catalogued winning route length or fails to improve over single-layer LP bounds on multi-hero rooms.

### `W2D-3`: Real-Checkpoint Contextual Compute (`docs/08`) Sheaf Obstruction & Stacked-Adapter Exact Gram Certification (`warp#15`)
- **Target Repos & PRs:**
  - `siliconcordat/loom` (`main` `0214e87`, PR `#5` `docs/08-contextual-compute.md`, PR `#7` `docs/10`, PR `#9` `docs/09`, PR `#10` `docs/11`)
  - `siliconcordat/warp` (issues `#10`–`#16`, PR `#14`), `siliconcordat/weft` (PR `#10`), `siliconcordat/mde` (PR `#8`), `Moissanite-Labs/weft-loom` (PR `#38`)
  - `Foundation-0/continuum` Draft PR [#3](https://github.com/Foundation-0/continuum/pull/3) & `Foundation-0/project-asma` Draft PR [#101](https://github.com/Foundation-0/project-asma/pull/101) (`optimal_inertia_rank.py`, `tropical_quotient_sheaf_bridge.py`)
- **Wave 1 Verified Baseline:** `AUDIT-004` (`docs/08` cellular sheaf obstruction `[97/1024, 389/4096]` on `bio`/`fluid`/`astro`), `AUDIT-005` (`T3` / `loom#9` Claim 9 omitted-variable phase boundary $0 < \rho_\Phi/\kappa_\perp < 2$), `AUDIT-006R` (`warp#15` exact concatenated Gram `Q_stack(s)` eliminating the $N^2$ Cauchy–Schwarz penalty on synthetic quantized low-rank adapters), and `AUDIT-016R` (dual-oracle $\mathbb{Q}(i)$ inertia checker).
- **Bootstrap & Baseline Check:**
  ```bash
  git clone https://github.com/Foundation-0/project-asma.git && cd project-asma
  gh pr checkout 101
  python3 -I -O -B -W error studies/expedition-mobius-ropt/optimal_inertia_rank.py
  ```
- **Compute Tier:** Tier 3 (1–2x 24–80 GB VRAM GPU, 64+ GiB RAM; real open-weights base checkpoint + real BF16/F16 GGUF LoRA adapters served via `llama-server` / `warp-modeld`).
- **Hypothesis & Discovery Goal:**
  1. Benchmark exact integer/rational concatenated Gram certification $Q_{\text{stack}}(s) = s G_B - G_B G_A G_B \succeq 0$ (`AUDIT-006R` + `spectral-inertia` Track C) directly inside a real `warp-modeld` load gate on real multi-adapter GGUF stacks ($N=2..8$, ranks $r=4..32$), measuring wall-clock latency against `docs/10` §5.4 and quantifying recovered norm headroom over `warp#15`'s $1/N^2$ rule.
  2. Test `docs/08`'s falsifier and `AUDIT-004`'s cellular-sheaf obstruction on real domain-specialized adapters (`biology` vs. `astrophysics` sharing `fluid dynamics` prompts) + test `loom#9` Falsifier #5 (Latch in a real nonlinear LoRA training loop) and Falsifier #6 (`AUDIT-005` phase boundary on real held-out anchors), plus integrate results from `Moissanite-Labs/weft-loom#38` once its 19h small-model run completes.
- **Oracle & Falsification Gate:** `exact` for the GGUF tensor-to-Gram recomputation & inertia gate (must reject `warp#13` `8*B` and `alpha=32` forgeries with zero floats); `sampled` with sealed held-out canary suites (closing `warp#16`) and pre-registered paired tests for real-checkpoint Contextual Compute & Latch trials. **Falsified if** exact Gram recomputation exceeds `warp`'s mount latency budget at production ranks, or if closing an astrophysics adapter still leaks/activates on "fluid dynamics" prompts, or if low-$\sin^2$ Latch audits still track independent gaps in nonlinear training (`docs/09` Falsifier #5).

---

## 7. Quick-Start Summary for Wave 2+ Coordinators

1. Clone `Foundation-0/cave-expedition` (`PR #1`) and read `METHODOLOGY.md`, `templates/portal-swarm-protocol.md`, and `verification/PROTOCOL.md`.
2. Pick a Wave 2 track matching your machine's compute tier (`next_waves_manifest.json` lists every machine-readable dependency, commit SHA, and falsifier).
3. Spawn a small Portal-Driven Swarm (at minimum: **Portal-Keeper**, **Domain Probe**, and **Independent Adversarial Verifier** running zero-shared-code checks under `-I -O -B -W error`).
4. Post verified Wave 2 Draft PRs back onto `siliconcordat/.github#5` (and `Foundation-0/cave-expedition`) using the same strict `verified` / `proposed` / `N0`–`N2` ledger discipline.
