# Session 2 Cartography: Formal Verification Consolidation, TCB Architecture & Indefinite Quadratic-Form / Chimeric Rank Bounds

- **Source Directory:** `<gemini-sessions>/20261120-155823_2cf295ad46d56eb5_formal-verification-consolidation/`
- **Transcript:** `session_verbatim_transcript.md` (7 pairs, 14 turns, 796 lines, 51,513 bytes)
- **Formulas:** `formulas_verbatim.json` (176 math elements across Pairs 2–6; 2 display equations: `F[62]` in Pair 5, `F[96]` in Pair 6; zero mismatches)
- **Code Blocks:** `code_blocks/` (2 distinct executable/config blocks):
  1. `pair_01_block_00.yaml` (327 lines, 11,846 bytes) — `.github/workflows/mcproof-ci.yml`
  2. `pair_06_block_00.py` (199 lines, 6,708 bytes) — `verify_chimeric_rank.py` (zero-float `fractions.Fraction` chimeric rank verifier)

---

## 1. Repository & Consolidation Graph

```
                  +---------------------------+
                  |   siliconcordat/.github   |  (Canonical index, twin-hub framing,
                  |   (Profile / TCB Hub)     |   content-addressed spec pinning)
                  +-------------+-------------+
                                |
           +--------------------+--------------------+
           |                                         |
           v                                         v
+------------------------+                +------------------------+
| Proven-Commons/mcproof |<---receipts----|  vaultofsouls (v1.1)   |
|  - mcproof.receipt.v1  |    & citations |  - Formal synthesis    |
|  - Phase 1-6 gates     |                |    preprint            |
|  - LF-only corpus      |                |  - Data-availability   |
|  - Negative fixtures   |                |    gap case study      |
|  - rational_hermitian_ |                +------------------------+
|    cert (proposed)     |
|  - Lean/comparator     |
|    profile (proposed)  |
+----+--------------+----+
     ^              ^
     |              |
     |              +------------------------------------+
     |                                                   |
+----+--------------------------+     +------------------+--------------------+
| ahrazzle/soko (v0.4.0)        |     | Foundation-0 / project-asma           |
|  - soko-verified-mcp          |     |  - Zero-float exact-rational DAG      |
|  - Untrusted C++ PDB / float  |     |    deconvolution (CO-loss doublets)   |
|    LP pre-solvers             |     |  - Fixture: pxd023044_23848           |
|  - Exact-rational LP dual     |     |    (m/z 615.0257, 64.04% CDR2L vs     |
|    verifier (quotient adm. &  |     |     35.96% chimeric 3+)               |
|    cost-partition dominance)  |     |  - Neg fixture: RATIONAL_MASS_DRIFT   |
|  - Neg fixture: III-21        |     |  - Proposed: Mode A/B Lemma 3.2       |
|    COST_PARTITION_OVERALLOC.  |     |    exact-rational chimeric rank gate  |
|  - Future: Q-verified SDP/SoS |     +---------------------------------------+
+-------------------------------+

Auxiliary / Orchestration & External Reference Ecosystem:
- abios / exo: persistent multi-agent harnesses (proposed: post-green proof-compression/ablation
  stage, two-way proof/refutation evaluation, source-only container output boundary).
- External 2026 Lean benchmarks cited (Pairs 2–5):
  * rohanarun/alpoge-rh-replay & alpo.ge (14-part, 239 MB / 175,187-file RH/GRH Lean archive + remark.pdf)
  * August 2026 Alpoge-Furman zeta-23 (arXiv:2608.13637, 67.2% simple critical zeros; Lemma 3.2;
    external cert_N256_blk_b128m.json missing -> "data-availability gap" negative-fixture class)
  * arXiv:2610.08965 (generalized c >= 1 weight for Lemma 3.2)
  * Kernel-replay TCB stack: Challenge.lean + Solution.lean + comparator + landrun (Linux Landlock)
    + lean4export + Palomar content-addressed statement hashes (banning sorryAx, Lean.ofReduceBool /
    native_decide, @[implemented_by], debug.skipKernelTC; allowlist: propext, Quot.sound, Classical.choice).
```

---

## 2. `Proven-Commons/mcproof` CI & TCB Boundary Architecture (`pair_01_block_00.yaml`)

Designed for `.github/workflows/mcproof-ci.yml` under deterministic env (`PYTHON_VERSION=3.12`, `PYTHONHASHSEED=0`, `PYTHONDONTWRITEBYTECODE=1`, `LC_ALL=C.UTF-8`, `TZ=UTC`, `core.autocrlf=false`):

1. **`phase1-6-gates`:** Strict LF check on `harness/` and `corpus/` (`{.json,.py,.sha256,.txt,.md}`); executes `python harness/run_phase1_6.py --corpus-dir corpus`; runs `compile/tests/test_*determinism*.py`.
2. **`receipt-schema-determinism`:** Validates all positive `*receipt*.json` files against `schema == "mcproof.receipt.v1"` via `harness/validate_mcproof_receipt.py --corpus-root corpus`; performs **Phase 6 fresh-clone reproducibility** (two local `git clone --no-hardlinks` copies run `run_phase1_6.py` and assert bit-identical SHA-256 across all non-`.git` `.json` artifacts).
3. **`negative-fixtures` (matrix):**
   - `corpus/soko/III-21/*overallocation*.json` $\to$ `--expect-fail COST_PARTITION_OVERALLOCATION`
   - `corpus/asma/pxd023044_23848/*mass_drift*.json` $\to$ `--expect-fail RATIONAL_MASS_DRIFT`
4. **`boundary-probes`:**
   - **Sandbox confinement:** Copies valid receipt outside `--corpus-root` (tempdir) and asserts non-zero exit.
   - **LF determinism:** Mutates valid receipt `\n` $\to$ `\r\n` inside corpus and asserts non-zero exit.
5. **`ci-gate`:** Single branch-protection rollup requiring all four jobs to succeed.

---

## 3. Extracted Dependency Spine of `remark.pdf` (`alpoge-rh-replay`, Pairs 2–3, `F[0–54]`)

- **Layer A — Function-Field Positivity & Determinant Bootstrap:**
  - Toy Weil/Deligne sign-only proof: $qN = M^k + R$ via path quadric $x_1 x_2 + \cdots + x_{k-1}x_k$; variance test-function sum $\sum_{h, x_1,\dots,x_k} t(x_1)\cdots t(x_k)e_q(h(x_1x_2+\cdots+x_{k-1}x_k))$; Bertini + middle cohomology gives definite sign opposing zero-mode $M^k$, while $k$-fold iterated Parseval bounds $R$ at square-root quality.
  - Over $\mathbb{Q}$: Guinand–Weil functional $A = \sum_{n\le X}\Lambda(n)\left(\frac{X}{n}-1\right)_+ - X\log X + (1+\gamma)$; multiplicity-1 determinant positivity $W(1_S)\ge 0$ and $W(1_{(0,1)}+(\sim X)1_{(0,1/x)})\ge 0$ yielding $>1-\eta$.
- **Layer B — Automorphic Multiplicity via Chained Theta Lifts:**
  - GGP periods on $O(2,n)$ (multiplicity 2); chained iterated theta lifts $U(X_0)\to U(X_1)\to\cdots\to U(X_m)$ between totally definite unitary groups ($\pi\mapsto\pi\oplus\mu_j[t]$) with chain length $m\sim\sqrt{X}$; Rallis seesaw converts iterated-lift period into Hecke-character-independent Bessel period.
- **Layer C — Breaking the $2/3$ Lift-Cost Wall:**
  - CM-curve vanishing ($D^p\equiv 0$ for inert $p$ in $K$) gives divisibility of $D^\alpha\theta(0)/\Omega^\alpha$ by $p^{\frac{a}{p}+\frac{a}{p^3}+\cdots - O(\log a)}$; Chowla–Selberg, Weyl, Siegel mass, and Bost slope inequality.
  - Step 14 stalls a priori at lift cost $2/3$; circumvented by gluing an integral structure across Hecke characters for extra "gcd" averaging controlled via relative trace formula (linked to automorphy on a sixfold cover of $GL_5$) + Cauchy–Schwarz on a projected Poincaré series.
- **Layer D — Arithmetic/Cohomological Cleanup:**
  - Iwasawa tower selected via Behrend *(explicit ablation candidate suspected unnecessary)*; weakened Vandiver on $H^1(\mathfrak{o}_E[1/l], \mathbb{Q}_l/\mathbb{Z}_l(-e))$; $K$-groups of $\mathbb{Z}$ / Lichtenbaum.

---

## 4. Indefinite Quadratic-Form / Chimeric Rank Bounds (Pairs 5–6, `F[62]`, `F[96]`, `pair_06_block_00.py`)

### 4.1 Exact Mathematical Claims
1. **Unscaled Lemma 3.2 (Pair 5, `F[62]`, cited to `arXiv:2608.13637`):**
   For Hermitian $P_1 \succeq 0$ and indefinite Hermitian $Q'$ with positive inertia $n_+(Q') \le b$:
   $$\operatorname{rank} P_1 \ge 2\operatorname{tr} P_1 + 4\operatorname{tr} Q' - 4b - \Vert P_1 + Q'\Vert_{\mathrm{HS}}^2$$
2. **Scale-Optimized Generalized $c \ge 1$ Form (Pair 6, `F[96]`, cited to `arXiv:2610.08965`):**
   For symmetric/Hermitian decomposition $H = P + Q$ with $P \succeq 0$, $n_+(Q) \le b$, rational $c \ge 1$, and $T_c := \operatorname{tr}(P) + c\operatorname{tr}(Q) > 0$:
   $$\operatorname{rank}(P) \ge \frac{T_c^2}{\Vert H\Vert_{\mathrm{HS}}^2} - c^2 b \quad\Longleftrightarrow\quad T_c^2 > (r_0 + c^2 b)\,\operatorname{tr}(H^2) \implies \operatorname{rank}(P) \ge r_0 + 1$$
3. **Zero-Float Exact-Rational Inertia Witness (Sylvester's Law of Inertia):**
   Instead of floating-point eigenvalues/SVD, an untrusted solver supplies rational $(C, C^{-1}, D)$ such that $C C^{-1} = I$ and $C Q C^T = \operatorname{diag}(D)$; exact `Fraction` multiplication verifies $n_+(Q) = \#\{i : D_i > 0\}$ without square roots or zero-pivot $LDL^T$ breakdown.
4. **Two Operational Modes for `project-asma` (`pxd023044_23848`):**
   - *Constraint:* A single MS2 scan ($173$ peaks) has rank-1 outer product $vv^T$ identically; requires $X\in\mathbb{Q}^{T\times M}$ across $T\approx 5\text{–}9$ local MS1 elution scans around $m/z\ 615.0257$ (or repeated MS2 scans) to build $G = X X^T \in \mathbb{Q}^{T\times T}$.
   - **Mode A ($b=0, c=1$, sequence-agnostic):** Model $G = P_{\mathrm{sig}} + N$ with $N \preceq D_\tau$; set $H = G - D_\tau$ so $Q = N - D_\tau \preceq 0$ ($b=0$). Checking $\operatorname{tr}(H) > 0$ and $(\operatorname{tr} H)^2 > r_0 \operatorname{tr}(H^2)$ certifies $\operatorname{rank}(P_{\mathrm{sig}}) \ge r_0 + 1$ with no congruence witness.
   - **Mode B ($b=1, c=2$, targeted residual):** Absorb rank-1 `CDR2L` backbone + bounded noise into $Q = P_{\mathrm{CDR2L}} + (N - D_\tau)$ ($n_+(Q)\le 1$ via Weyl), certify $\operatorname{rank}(P_{\mathrm{chim}})\ge 1$ via $T_2^2 > 4\operatorname{tr}(H^2)$ + rational congruence witness for $Q$.
   - *Claimed Scan 23848 Calibration ($w_1 = 0.6404^2, w_2 = 0.3596^2$, $T=5$):* Mode A gives exact lower bounds $1.574$ ($\rho=0, \tau=0$), $1.376$ ($\rho=0.5, \tau=0$), $1.074$ ($\rho=0.9, \tau=0$), $1.191$ ($\rho=0.5, \tau=0.01$), $1.007$ ($\rho=0.5, \tau=0.02$); Mode B ($\rho=0, \tau=0, c=2, b=1$) gives $0.876 \implies \operatorname{rank}\ge 1$.

---

## 5. CRITICAL AUDIT FINDINGS & SUSPECT CLAIMS (Immediate Targets for `@verifier`)

### Finding 1 — CRITICAL TCB SOUNDNESS BUGS in `pair_06_block_00.py` (`AUDIT-001`: `FALSIFIED` prototype impl)
`certify_mode_b_lemma32(H, Q, C, C_inv, D_diag, c, target_rank_gt)` **NEVER checks that $P := H - Q$ is positive semidefinite ($P \succeq 0$)**, nor does it verify `is_symmetric(H)` or matching matrix dimensions!
- **Explicit Exploit / Forged Certificate (verified in `AUDIT-001`):** Pass $H = \operatorname{diag}(1, 0)$ (symmetric, rank 1), $Q = \operatorname{diag}(10, 0)$ (symmetric, valid inertia witness $C=C^{-1}=I_2, D=[10,0] \implies b=1$), $c=2$. Then $P = H - Q = \operatorname{diag}(-9, 0) \not\succeq 0$, yet `exact_bound = 117`, so `target_rank_gt = 116` **falsely certifies $\operatorname{rank}(H - Q) \ge 117$ on a $2\times 2$ matrix** (with $Q = \operatorname{diag}(11,0)$, certifies `>= 140`!).
- **Additional TCB/R3 Defects Caught by `@verifier` (`AUDIT-001`):** Missing `is_symmetric(H)` & `len(H) == len(Q)` in Mode B; `verify_congruence_inertia` / `mat_mul` omit dimension checks (non-square $3\times 2$ `C` + extra `D_diag=[0,0,5]` returns `n_+(0)=1`); `to_frac` accepts `bool`, `"1/2\n"`, `"0.5"`, `"1_000"`, Arabic-Indic `"\u0661/\u0662"`; negative `target_rank_gt = -5` accepted.
- **Required Fix:** Any sound `mcproof` `rational_hermitian_cert` TCB for Mode B MUST verify square/matching shapes, `is_symmetric(H)`, `target_rank_gt >= 0`, strict canonical integer/rational parsing, AND a second rational congruence witness $(C_P, C_P^{-1}, D_P)$ proving $C_P(H - Q)C_P^T = \operatorname{diag}(D_P)$ with **all $D_{P,i} \ge 0$** (certifying $P \succeq 0$).

### Finding 2 — SETTLED & STRENGTHENED (`AUDIT-002`: `VERIFIED`, exact oracle, provisional `N2`): Non-Commuting Lemma 3.2 & Sharp Envelope $R_{\mathrm{opt}}^\perp$
- Via $W \oplus W^\perp$ block decomposition ($W = \operatorname{range}(Q_+)$, where $Q = \operatorname{diag}(Q_+, -Q_-)$ has zero off-diagonal block; full 5-line proof in `frontier_portals.md` Portal 1), generalized Lemma 3.2 holds **unconditionally for ALL non-commuting complex Hermitian** $P \succeq 0, n_+(Q) \le b, c \ge 1$, AND bounds the strictly stronger projected positive inertia and novel-subspace rank:
  $$\operatorname{rank}(P) \;\ge\; \operatorname{rank}(\Pi_{W^\perp} P \Pi_{W^\perp}) \;\ge\; n_+\!\big(\Pi_{W^\perp}(P+Q)\Pi_{W^\perp}\big) \;\ge\; R_{\mathrm{opt}}(u,t,S,b)$$
  where $R_{\mathrm{opt}}(u,t,S,b) = 0$ if $u \le 0$ or $u+t \le 0$; else $b u^2 / (b S - t^2)$ if $b>0, t>0, t(u+t)\ge b S$; else $\max(0, (u+t)^2/S - b)$.
- Verified by `@verifier` (`AUDIT-002`) with 0 violations on 420 exact $\mathbb{Q}(i)$ complex Hermitian matrices (independent Faddeev–LeVerrier + Descartes checker), strictly beating Fable's `docs/10` $R_G$ on 417/420 instances, proving **integer-exact pointwise sharpness** $\min \operatorname{rank}(P) = \max(1, \lceil R_{\mathrm{opt}}\rceil)$ (so higher spectral moments $\operatorname{tr} H^3, \operatorname{tr} H^4$ are strictly needed to go further), and lifting Scan 23848 Mode B to exact `1` at $\rho=0$ while staying $>0$ for all $\rho \in [0, 1)$.

### Finding 3 — Mode A Noise-Floor Trust Boundary & Calibration Check
- Mode A assumes $N \preceq D_\tau$ externally; correlated rank-1 Orbitrap baseline drift exceeding $\tau I_T$ can violate $Q = N - D_\tau \preceq 0$ and produce a false rank $\ge 2$ certification on a single-species scan.
- In `pair_06_block_00.py` (`_self_test`, lines 156–196), verify exact self-test execution and confirm the six table entries in Pair 6 (lines 565–573) match exact `Fraction` arithmetic.

### Finding 4 — Cross-Domain Leverage for Swarm Peers
- **`@continuum-bridge` & `Foundation-0/project-asma` + `Proven-Commons/mcproof`:** Reusable zero-float `rational_hermitian_cert` primitive (exact congruence inertia + trace + Hilbert–Schmidt norm) bridges spectral/operator problems (including Sheaf Laplacian PSD/rank bounds and Koopman/Gram spectral ranks) into `mcproof.receipt.v1`.
- **`@fractals-probe` & `quotient-lp-bounds` / `ahrazzle/soko`:** Exact-rational congruence PSD certification ($C M C^T = D \ge 0$) lifts exact LP dual verification (`quotient-lp-bounds`, `soko` v0.4.0) to **exact-rational SDP / Sum-of-Squares / quadratic dominance certificates** without floating-point eigensolvers in the TCB!
- **`@gravity-probe`:** Exact-rational inertia witnesses ($C Q C^T = D$) can certify Hessian index / stability signatures (e.g. relative equilibria / Morse index $\mathrm{sgn}(\delta^2 S)$) without floating-point eigenvalue ambiguity!
