# Track S26: Exact Pure-$\mathbb{Q}$ Counterfactual World-Model Holonomy & Tomography on `arXiv:2611.24778v1`

- **Track ID:** `TRACK-S26-COUNTERFACTUAL-WORLD-MODELS-HOLONOMY`
- **Schema:** `aletheia.track_s26.counterfactual_holonomy.v1`
- **Source Paper:** Randall Balestriero, Yann LeCun, and Kerda Varaku, *Counterfactual World Models: JEPAs That Reason About "What If"* (`arXiv:2611.24778v1`, Nov 18, 2026)
- **Methodology:** The Aletheia Method v2.0.0 (`OWN_TERMS_FIRST`, Law 1b, Law 2b Transformational Steelman, Law 4 `CS-13` Prior-Art & Honest `N0`/`N1` Novelty Accounting, Law 5 Beyond-Language Exact-$\mathbb{Z}/\mathbb{Q}$ Operators)
- **Trust-Path Discipline:** Pure Python 3 stdlib (`int`, `fractions.Fraction`, `math.gcd`, `hashlib`, `hmac`, `json`), **`0` IEEE-754 floats**, **`0` bare `assert`s**, **`0` RNG calls**, **`0` external dependencies**.
- **Canonical Certificate Digests:**
  - `payload_sha256`: `8c0aa5509f9a92b0d8bcbc376355868fa26c2e901978895ab4bf5799e4c2de59`
  - `certificate_sha256`: `f92fd218267b8233ff8ddd67310186ea26eabfd689ebd1e6e4084c8ef9c35ba7`
  - `counterfactual_holonomy_certificate.json` file SHA-256: `9683b5ad994bb9a23e74d5c6a934fa41e90c795b734eaabfc90d84cf06fe3eed`

---

## 1. `OWN_TERMS_FIRST` & Law-2b Transformational Steelman

### 1.1 Exact Problem Statement on Its Own Terms (`arXiv:2611.24778v1`)
Balestriero, LeCun, and Varaku (2026) analyze counterfactual prediction from a factual world model $\mu(H_t, a) = \mathbb{E}[Z_{t+h}(a) \mid H_t]$ trained strictly on observational transition data without counterfactual supervision, auxiliary parameters, or retraining. Their central results are:

1. **Factual Gauge Non-Identification (Theorem 2.2 / Appendix H.1):** Two structural transition maps $T_{s,a}$ and $\widetilde{T}_{s,a} = T_{s,a} \circ G_{s,a}$ related by any measure-preserving bijection $G_{s,a} \in \operatorname{Stab}(\mathrm{Law}(\varepsilon))$ generate identical 1-step factual transition distributions $P(Z_{t+h} \mid H_t, a)$ yet distinct counterfactual couplings across actions $a \ne a'$.
2. **Zero-Retraining Residual Reuse (Section 3 / Proposition 3.2):** Under smooth separate-channel ODE dynamics (*natura non facit saltus*), the additive residual-reuse estimator
   $$\hat{z}_{\mathrm{RR}}(a') = z_{\mathrm{obs}}(a) + \mu(H_t, a') - \mu(H_t, a)$$
   achieves $O(h^2)$ pointwise error ($O(h^4)$ MSE) because the $O(h^0)$ and $O(h^1)$ terms cancel identically while the action–disturbance cross-term enters only at $O(h^2)$.
3. **Minimax Rate Optimality Wall (Theorem 3.6 / Appendix E.5, Eq. 56):** On the chiral hard pair in $\mathbb{R} \times \mathbb{R}^2$ with $J = \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix}$ and $\theta \in \{-1, +1\}$,
   $$\dot{q} = a, \qquad \dot{x} = \big(I_2 + 2\theta C q J\big)\,\varepsilon,$$
   with $q_0 = 0$, factual $a = -1$, counterfactual $a' = +1$, and isotropic $\varepsilon$ ($\mathbb{E}[\varepsilon]=0$, $\mathbb{E}\|\varepsilon\|^2 = 1$), any estimator relying solely on unpaired 1-step factual distributions incurs minimax MSE at least $\frac{4 C^2 h^4}{1 + C^2 h^2}$, matching residual reuse's $4 C^2 h^4$ rate up to the factor $1 + C^2 h^2$.

### 1.2 Law-2b Transformational Steelman
Before probing where Theorem 3.6 breaks, we state **precisely where Balestriero, LeCun & Varaku's result is genuinely sharp and mathematically irreducible**:
- **Sharp under its exact assumptions:** If an agent observes *only* unpaired 1-step factual laws $P(S_h \mid s_0, a)$ **and** the latent disturbance law $\nu = \mathrm{Law}(\varepsilon)$ is strictly $SO(2)$-invariant (isotropic), then Theorem 1 below verifies via an exact rational Cayley rotation $R(u) \in SO(2, \mathbb{Q})$ that $\theta = +1$ and $\theta = -1$ are *information-theoretically indistinguishable*. In that exact regime, the midpoint $\bar{g}(X) = (h, \frac{1-k^2}{1+k^2} X)$ is minimax-optimal (and exact Bayes-optimal for isotropic Gaussian $\varepsilon$), and unshrunk residual reuse $T_R$ is rate-optimal up to exact factor $1 + k^2$.
- **Practical strength:** Residual reuse requires zero knowledge of $\Sigma_\varepsilon$, zero architectural changes to a frozen JEPA backbone, and zero multi-step history alignment when only a single factual transition is available.
- **Exact structural cleavage:** The $O(h^4)$ minimax wall relies simultaneously on **two fragile idealizations**: (i) exact $SO(2)$ isotropy of $\mathrm{Law}(\varepsilon)$ so the chiral gauge $R(u)$ lies inside $\operatorname{Stab}(\mathrm{Law}(\varepsilon))$, and (ii) discarding the multi-step trajectory history $H_t$ already present in Section 3.1 of the paper. Relaxing **either** assumption alone collapses Eq. (56)'s counterfactual error from $O(h^4)$ MSE to **exact `0`** over pure $\mathbb{Q}$.

---

## 2. Certified Exact-$\mathbb{Q}$ Theorems (`counterfactual_holonomy_oracle.py`)

### Theorem 1 — Exact Algebraic Reproduction & Audit of `arXiv:2611.24778v1`
1. **Exact Closed-Form Flow & Step-2 Nilpotent Lie Bracket:**
   Integrating Eq. (56) from $(q_0, x_0)$ under constant action $a$ and held disturbance $\varepsilon$ gives the exact time-$h$ flow matrix
   $$M_\theta(q_0, a, h) = h\big(I_2 + \theta C (2 q_0 + a h) J\big), \qquad q_1 = q_0 + a h, \quad \Delta x = M_\theta \varepsilon,$$
   verified with exact `0` quadrature residual across rational parameter triples. The vector fields $X_a = (a, 0)$ and $X_\varepsilon = (0, (I_2 + 2\theta C q J)\varepsilon)$ satisfy $[X_a, X_\varepsilon] = (0, 2\theta C a J\varepsilon)$ with all higher iterated brackets identically zero (step-2 nilpotent, explaining why the 2nd-order BCH/Magnus series is exact).
2. **Exact Cayley $SO(2, \mathbb{Q})$ Factual Gauge Equivalence (Zero Square Roots):**
   Setting $u = C(2q_0 + ah)$, the rational Cayley matrix
   $$R(u) := M_-^{-1} M_+ = \frac{1}{1 + u^2}\begin{pmatrix} 1 - u^2 & -2u \\ 2u & 1 - u^2 \end{pmatrix} \in SO(2, \mathbb{Q})$$
   satisfies $R(u)^\top R(u) = I_2$, $\det R(u) = 1$, $M_+ = M_- R(u)$, and $M_+ M_+^\top = M_- M_-^\top = h^2(1 + u^2) I_2$ identically.
3. **Exact Eq. (56) Minimax Risk & Strict $1 + k^2$ Gap ($q_0 = 0, a = -1, a' = +1, k = C h$):**

   | $C$ | $h$ | $k = Ch$ | Shrinkage $\frac{1-k^2}{1+k^2}$ | $\operatorname{MSE}(T_R)$ | $\operatorname{MSE}(\bar{g})$ | Exact Gap $\frac{\operatorname{MSE}(T_R)}{\operatorname{MSE}(\bar{g})} = 1 + k^2$ |
   |---|---|---|---|---|---|---|
   | `1` | `1/2` | `1/2` | `3/5` | `1/4` | `1/5` | `5/4` |
   | `1` | `1/4` | `1/4` | `15/17` | `1/64` | `1/68` | `17/16` |
   | `1` | `1/8` | `1/8` | `63/65` | `1/1024` | `1/1040` | `65/64` |
   | `3/2` | `1/4` | `3/8` | `55/73` | `9/256` | `9/292` | `73/64` |

4. **Exact Pythagorean Variance-Matched Transport Improvement ($q_0 \ne 0$ vs. $q_0 = 0$ Tie):**
   For general $q_0$, $u = C(2q_0 + ah)$, $u' = C(2q_0 + a'h)$, factual covariance matching scales $X$ by $\rho_{\mathrm{VM}} = \sqrt{\frac{1+u'^2}{1+u^2}}$, which is strictly rational on Pythagorean pairs:
   - **$u = 3/4 \to u' = 4/3$ ($q_0 = 1/2, \rho_{\mathrm{VM}} = 4/3$):** $\operatorname{MSE}(\bar{g}_{\mathrm{Bayes}}) = \frac{49}{225} < \operatorname{MSE}(T_{\mathrm{VM}}) = \frac{2}{9} < \operatorname{MSE}(T_R) = \frac{49}{144}$.
   - **$u = 5/12 \to u' = 12/5$ ($q_0 = 1, \rho_{\mathrm{VM}} = 12/5$):** $\operatorname{MSE}(\bar{g}_{\mathrm{Bayes}}) = \frac{14161}{4225} < \operatorname{MSE}(T_{\mathrm{VM}}) = \frac{98}{25} < \operatorname{MSE}(T_R) = \frac{14161}{3600}$.
   - **Symmetric control ($q_0 = 0, u = -1, u' = +1, \rho_{\mathrm{VM}} = 1$):** $\operatorname{MSE}(T_{\mathrm{VM}}) = \operatorname{MSE}(T_R) = 4 > \operatorname{MSE}(\bar{g}_{\mathrm{Bayes}}) = 2$.
   - **Exact iff characterization of $T_{\mathrm{VM}}$ vs. $T_R$:** Variance-matched transport $T_{\mathrm{VM}}$ strictly beats $T_R$ **if and only if** $(\rho_{\mathrm{VM}} - 1)(\rho_{\mathrm{VM}} + 1 - 2\alpha_{\mathrm{Bayes}}) < 0$. It does *not* improve on $T_R$ for all $q_0 \ne 0$: for example, at the Pythagorean counterexample $q_0 = 1/2, a = -7/4, a' = 1/3, C = 1, h = 1$ ($u = -3/4, u' = 4/3, \rho_{\mathrm{VM}} = 4/3, \alpha_{\mathrm{Bayes}} = 0$), $\operatorname{MSE}(T_{\mathrm{VM}}) = 50/9 = 800/144 > 625/144 = \operatorname{MSE}(T_R)$. By contrast, the linear Bayes/minimax estimator $\bar{g}_{\mathrm{Bayes}}(X) = \frac{1+uu'}{1+u^2}X$ strictly beats $T_R$ iff $u \ne 0$ and $u' \ne u$.

---

### Theorem 2 — Gauge-Stabilizer Anisotropy Theorem (Unpaired 1-Step Factual Data Alone)
Let $\Sigma_\varepsilon = \operatorname{Cov}(\varepsilon)$ be any symmetric PSD $2\times 2$ covariance matrix with eigenvalue-splitting discriminant $\Delta_\lambda^2(\Sigma_\varepsilon) := (\lambda_1 - \lambda_2)^2 = (\operatorname{tr}\Sigma_\varepsilon)^2 - 4\det\Sigma_\varepsilon \in \mathbb{Q}_{\ge 0}$.
- **Diagonal Case ($\Sigma_\varepsilon = \operatorname{diag}(\sigma_1^2, \sigma_2^2)$):** Whenever $\sigma_1^2 \ne \sigma_2^2$, $\operatorname{Stab}_{SO(2)}(\Sigma_\varepsilon)$ collapses from $SO(2)$ to $\{\pm I_2\}$, excluding the chiral gauge $R(u)$ for every $u \ne 0$, and the 1-step unpaired factual off-diagonal covariance satisfies identically:
  $$\Sigma_{12}^\theta(q_0, a) \equiv h^2 \theta C (2q_0 + a h)(\sigma_1^2 - \sigma_2^2) \implies \theta C \equiv \frac{\Sigma_{12}^\theta(q_0, a)}{h^2 (2q_0 + a h)(\sigma_1^2 - \sigma_2^2)}.$$
- **Coordinate-Free General Symmetric PSD Case (Arbitrary Rotated Eigenbasis):** Writing $\Sigma_\varepsilon = \bar{\sigma}^2 I_2 + D_\varepsilon$ with $J D_\varepsilon = -D_\varepsilon J$ yields two basis-free pure-$\mathbb{Q}$ identities (verified on non-diagonal SPD matrices `[[5,2],[2,3]]` ($\Delta_\lambda^2 = 20$) and `[[7,-3],[-3,4]]` ($\Delta_\lambda^2 = 45$)):
  $$\big[\Sigma_{\Delta x}^\theta,\, \Sigma_\varepsilon\big] \equiv h^2 \theta C (2q_0 + a h)\,\Delta_\lambda^2(\Sigma_\varepsilon)\, J, \qquad \theta C \equiv \frac{\operatorname{tr}\big(J^\top \Sigma_{\Delta x}^\theta \Sigma_\varepsilon\big)}{h^2 (2q_0 + a h)\big((\operatorname{tr}\Sigma_\varepsilon)^2 - 4\det\Sigma_\varepsilon\big)}.$$
- **Exact `0`-Error Counterfactuals & Negative Control:** Inverting $\hat{\varepsilon} = h^{-1}(1 + u^2)^{-1}(I_2 - \theta u J)\Delta x = \varepsilon$ drives counterfactual squared error to **exact `0`** across all anisotropic test cases (where residual reuse incurs nonzero error `1261/900`, `31525/9216`, `1261/3600`). Conversely, at $\sigma_1^2 = \sigma_2^2 = 4$ (isotropic negative control), $\Sigma_{12} = 0$, $[\Sigma_{\Delta x}, \Sigma_\varepsilon] = 0$, $R(u)\Sigma_\varepsilon R(u)^\top = \Sigma_\varepsilon$, and recovery fails closed with `ISOTROPIC_UNIDENTIFIABLE`.

---

### Theorem 3 — Exact 2-Step Rational Signed-Area Recovery (100% Isotropic $\varepsilon$), Nonlinear $O(h^6)$ Commutator Elimination, & Curved-Encoder $D^2\mathcal{E}$ Obstruction
1. **Exact General-$q_0$ Norm-Difference & Universal $q_0$-Free Signed-Area Formulas:**
   Along a single 2-step rollout $(q_0, x_0) \xrightarrow{a_0} (q_1, x_1) \xrightarrow{a_1} (q_2, x_2)$ under held disturbance $\varepsilon \ne 0$ (even for 100% $SO(2)$-isotropic $\mathrm{Law}(\varepsilon)$!), the increments $\Delta x_1, \Delta x_2$ satisfy:
   $$\det[\Delta x_1, \Delta x_2] \equiv \theta C h^3 (a_0 + a_1)\|\varepsilon\|^2, \qquad \|\Delta x_2\|^2 - \|\Delta x_1\|^2 \equiv C^2 h^3 (a_0 + a_1)\big(4q_0 + (3a_0 + a_1)h\big)\|\varepsilon\|^2,$$
   $$\|\Delta x_2 - \Delta x_1\|^2 \equiv C^2 h^4 (a_0 + a_1)^2 \|\varepsilon\|^2.$$
   Dividing cancels $\|\varepsilon\|^2$ identically with **zero square roots**, yielding two exact rational recoveries:
   $$\theta C \equiv \frac{\|\Delta x_2\|^2 - \|\Delta x_1\|^2}{\big(4q_0 + (3a_0 + a_1)h\big)\det[\Delta x_1, \Delta x_2]} \qquad \big(a_0 + a_1 \ne 0,\; 4q_0 + (3a_0 + a_1)h \ne 0\big),$$
   $$\theta C \equiv \frac{\|\Delta x_2 - \Delta x_1\|^2}{h\,(a_0 + a_1)\,\det[\Delta x_1, \Delta x_2]} \qquad \big(\text{iff } a_0 + a_1 \ne 0 \text{ and } \varepsilon \ne 0\text{ — independent of } q_0\text{!}\big).$$
   Both exact algebraic inversion $\hat{\varepsilon} \mapsto F_h^{\widehat{\theta C}}(s_0, a', \hat{\varepsilon})$ and the 1-line commutator extrapolation
   $$\hat{Y}_{\mathrm{cf}}^{\mathrm{comm}}(a') := x_0 + \Delta x_1 + \frac{a' - a_0}{a_0 + a_1}(\Delta x_2 - \Delta x_1)$$
   achieve **exact `0` counterfactual error** across all 4 certified `(q0, a0, a1, a', h)` test cases.
2. **Exact Degenerate-Action Boundary Controls:**
   - **$a_0 + a_1 = 0$** (`a0=2, a1=-2`): $\Delta x_2 \equiv \Delta x_1$, $\det[\Delta x_1, \Delta x_2] \equiv 0$; both estimators fail closed with `DEGENERATE_ACTION_SUM` (exact persistence-of-excitation boundary).
   - **$4q_0 + (3a_0 + a_1)h = 0$ with $a_0 + a_1 \ne 0$** (`q0=-1, h=1, a0=1, a1=1, theta=-1, C=3/2`): $\|\Delta x_2\|^2 - \|\Delta x_1\|^2 \equiv 0$ (norm-difference formula rejects cleanly with `SYMMETRIC_NORM_DEGENERACY`), **yet** $\operatorname{sgn}((a_0 + a_1)\det_{12}) = -1$ still identifies chirality $\theta$ AND the universal difference-norm formula still recovers exact $\theta C = -3/2$!
3. **Nonlinear Cross-Channel $O(h^4) \to O(h^6)$ MSE Elimination & Self-Advection Obstruction ($Dg \cdot g \ne 0$):**
   - On the quadratic cross-channel ODE $\dot{q} = a$, $\dot{x} = (I_2 + 2\theta C q J + 3 D q^2 K)\varepsilon$ ($K = \operatorname{diag}(1, -1)$) at $q_0 = 1/3$, 2-step commutator extrapolation cancels the entire $O(h^2)$ Lie bracket $[X_a, X_\varepsilon](q_0)$ identically, leaving exact pure-$O(h^3)$ remainder $D h^3 (a'-a_0)(a'-a_0-a_1) K\varepsilon$ (`two_step_err_sq / h^6 == 3825/2` identically across $h \in \{1/2, 1/4, 1/8, 1/16\}$, vs $O(h^4)$ RR error `7281/8 .. 581337/512`, and exact `0` at resonance $a' = a_0 + a_1$).
   - **Honest $Dg \cdot g \ne 0$ Obstruction:** Adding exact self-advection $\dot{x}_2 = \varepsilon_2 + 2\theta C q \varepsilon_1 + 2\beta x_1 \varepsilon_1$ introduces exact $O(h^2)$ 2-step bias $-\frac{a'-a_0}{a_0+a_1} 2\beta h^2 \varepsilon_1^2 = 9/20$ (`sa_h=1/4, beta=3/5`), proving honestly that $Dg \cdot g = 0$ is necessary for 2-step $O(h^6)$ MSE — while a **3-step second difference** $(a_0, a_1, a_2)$ with $a_2 \ne a_0$ cancels $2\beta h^2 \varepsilon_1^2$ identically and restores **exact `0` error**.
4. **Exact Curved-Encoder $D^2\mathcal{E}$ Obstruction (JEPA Latent Space):**
   Even for **strictly additive zero-interaction physics** $s_h(a,\varepsilon) = s_0 + h a + h\varepsilon$ (state-space RR error $= 0$), encoding via $\mathcal{E}(s) = (s, \kappa s^2)$ ($\kappa = 3/5$) manufactures exact nonzero latent residual-reuse error
   $$z_2(a',\varepsilon) - \hat{z}_2^{\mathrm{RR}}(a') \equiv 2\kappa h^2 (a' - a)\varepsilon \equiv h^2 D^2\mathcal{E}(a'-a, \varepsilon) = -\frac{9}{56}, \qquad \operatorname{MSE}_{\mathrm{lat}} = \frac{729}{6400} = O(h^4),$$
   vanishing identically for the flat/affine control ($\kappa = 0$).

---

### Theorem 4 — Multiplicative & Mixed Additive-Multiplicative Steelman (`Appendix E.4`)
1. **Pure Multiplicative ($\dot{s} = a\varepsilon$):** Additive residual reuse incurs exact $O(h)$ error $h(a'-a)\varepsilon$ ($O(h^2)$ MSE), whereas multiplicative ratio reuse $\hat{s}_h^{\mathrm{mult}}(a') = s_0 + \frac{a'}{a}(s_h - s_0)$ achieves **exact `0` error** for all $a \ne 0$ (and fails closed at singular boundary $a = 0$ with `ZERO_FACTUAL_ACTION`).
2. **Mixed Additive + Multiplicative ($\dot{s} = v_0 a + \varepsilon_{\mathrm{add}} + a\varepsilon_{\mathrm{mult}}$):** On 1 step, *both* additive reuse (`-9/16`, `-3/4`) and multiplicative ratio reuse (`-21/40`, `-2/3`) fail; on 2 steps with $a_0 \ne a_1$, exact $2\times 2$ inversion ($\det = h^2(a_1 - a_0)$) recovers $(\varepsilon_{\mathrm{add}}, \varepsilon_{\mathrm{mult}})$ identically with **exact `0` counterfactual error**. At the singular control $a_0 = a_1 = 2$, the oracle rejects with `SINGULAR_ACTION_PAIR`, and the explicit shifted pair $(\varepsilon_{\mathrm{add}} + \delta a_0, \varepsilon_{\mathrm{mult}} - \delta)$ proves identical factual residuals with exact counterfactual divergence $h(a_0 - a')\delta = 35/2 \ne 0$.

---

## 3. Honest Law-4 `CS-13` Prior-Art Audit & Epistemic Novelty Accounting (`N0` / `N1`)

### 3.1 Mechanism-First Prior Art Across Neighboring Disciplines
1. **Econometric Difference-in-Differences (DiD), Synthetic Controls & Interactive Fixed Effects (`N0` classical mechanism):**
   - Additive 1-step residual reuse $\hat{z}(a') = z_{\mathrm{obs}}(a) + \mu(a') - \mu(a)$ is mathematically isomorphic to classical Difference-in-Differences under parallel trends (Card & Krueger, 1994) and synthetic-control linear factor differencing (Abadie, Diamond & Hainmueller, 2010).
   - **Jushan Bai (2009, *Econometrica*, "Panel Data Models with Interactive Fixed Effects")** established that when unobserved unit effects interact multiplicatively with time/treatment factors ($\lambda_i^\top f_t$, the econometric analogue of action–disturbance coupling), 1-period differencing fails while multi-period panel histories identify interactive factor loadings under full-rank excitation.
2. **Nonlinear Control Theory, Lie-Bracket Observability, Magnus Expansions & Persistence of Excitation (`N0` classical mechanism):**
   - **Robert Hermann & Arthur J. Krener (1977, *IEEE TAC*, "Nonlinear Controllability and Observability")** and **Héctor J. Sussmann (1977)** established that observability of hidden state/parameter variables under controlled flows is governed by iterated Lie derivatives and brackets $[X_a, X_\varepsilon]$, requiring non-degenerate ("universal" / persistently exciting) control inputs — directly corresponding to our exact $a_0 + a_1 \ne 0$ and $a_0 \ne a_1$ persistence-of-excitation conditions.
   - **Wilhelm Magnus (1954)** / Baker–Campbell–Hausdorff expansions govern the commutator cancellation underlying our 2-step $O(h^4) \to O(h^6)$ nonlinear MSE improvement.
   - **Judea Pearl (2009, *Causality*)** formalized Abduction–Action–Prediction counterfactual semantics and non-identification under distribution-preserving latent transformations.
3. **Contemporaneous 2026 World-Model Identifiability & Counterfactual Literature (Live-Verified via alphaXiv):**
   - **Yibin Dong (`arXiv:2608.00591`, Aug 2026, *Why Does the Future Branch? Identifiable Closure Tests for Stochastic Physical World Models*):** Proves ordinary 1-step transitions cannot separate state aliasing from process noise, achieving identification via `ClosurePairs` crossing compatible microstates with repeated exogenous disturbances. *Contrast:* our Theorem 2 breaks Eq. (56) on strictly **unpaired** 1-step data via covariance anisotropy without microstate crossing, and Theorem 3 breaks isotropic Eq. (56) from a **single** 2-step rollout without resetting/crossing microstates.
   - **Xiangteng Zhang, Yang Guan, Bo Zhang, Hongyang Li, Ya-Qin Zhang & Shengbo Eben Li (`arXiv:2607.22430`, Jul 2026, *On the Identifiability of Controlled World Models*):** Studies identifiability of latent controlled world models under action interventions.
   - **Somasundhar Venkatasubramanian, Anirudh Venkat & Advaidh Venkat (`arXiv:2605.05717`, May 2026, *Space-Time Diversity in Observability and Estimation on Product Lie Groups*):** Analyzes cross-factor Lie-group observability via spatial/temporal diversity (conceptually related to how temporal 2-step diversity unlocks cross-channel $[X_a, X_\varepsilon]$ observability in Theorem 3).
   - **Arjun Subramanian (`arXiv:2610.02860`, Oct 2026, *Counterfactual Action Evaluation, Observation Bottlenecks, and Representation Geometry in Joint-Embedding Predictive World Models*):** Traces interventions through simulator state, observations, and JEPA target embeddings — empirically complementing our exact algebraic $D^2\mathcal{E}$ curved-encoder obstruction in Theorem 3.
   - **Junlin Chen, Ruijie Wang & Jianxin Li (`arXiv:2608.22092`, Aug 2026, *Counterfactual Quotient Models*)** and **Yu Ma, Hongli Shi & Xinran Xu (`arXiv:2608.08982`, Aug 2026, *Twin Rollouts*)**: Related action-difference and noise-coupled rollout approaches in RL/video world models.

### 3.2 Honest `N0` / `N1` Grading & Scope Boundaries
- **`N0` (Classical Prior Art):** $SO(2)$ covariance stabilizers, Cayley rational rotations, Hermann–Krener / Sussmann Lie-bracket observability, persistence of excitation, Bai (2009) multi-period interactive-factor identification, Magnus commutator cancellation, and curved pushforward Hessian $D^2\mathcal{E}$ terms.
- **`N1` (Verified Exact Specialization & Machine-Certified Synthesis on `arXiv:2611.24778v1`):**
  1. Coordinate-free general-PSD commutator/trace identification breaking Eq. (56) on unpaired 1-step data (`Theorem 2`),
  2. Exact $q_0$-free rational 2-step difference-norm signed-area identity $\theta C = \frac{\|\Delta x_2 - \Delta x_1\|^2}{h(a_0+a_1)\det[\Delta x_1, \Delta x_2]}$ resolving the symmetric reflection degeneracy $4q_0 + (3a_0+a_1)h = 0$ (`Theorem 3`),
  3. Exact closed-form Pythagorean variance-matched transport strict chain (`Theorem 1`), exact $O(h^6)$ nonlinear cross-channel commutator remainder + $Dg\cdot g \ne 0$ 3-step separation (`Theorem 3`), and zero-float stdlib certification suite (`counterfactual_holonomy_oracle.py` / `counterfactual_holonomy_audit.py`).
- **Explicit Non-Claims:** We do **not** claim `N2` (the underlying Lie-observability and multi-period identification principles are classical), nor do we claim empirical vision-JEPA benchmark improvements on high-dimensional pixels where finite-sample covariance estimation noise and nonlinear encoder drift must be estimated statistically rather than solved noise-free.

---

## 4. Verification & Zone-B Hardening Ledger

All gates executed strictly sequentially (`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, `0` GitHub writes). In `--check` mode, `counterfactual_holonomy_audit.py` performs **full pure-$\mathbb{Q}$ deterministic replay** (`validate_certificate_payload(..., full_replay=True)`) paired with a **secondary algebraic cross-check** (`independent_audit_payload`) over the parsed rational strings (reserving the term "zero-shared-code" strictly for independent external verifiers):

- **3-Mode Isolated Parity (`-I -B`, `-I -O -B`, `-I -B -W error`) + `-I -O -B -W error` & `PYTHONHASHSEED=42 -I -B`:** `--standalone --json` matches `counterfactual_holonomy_certificate.json` (`9683b5ad...`, `0o600`) byte-for-byte; `--check` passes (`valid: true`, `independent_audit_passed: true`); `test_counterfactual_holonomy_r5.py` passes `7/7 OK` across all modes.
- **Live `aletheia v2.0.0 mutate --max-mutants 0 --work-root . --add-cwd`:**
  - `counterfactual_holonomy_oracle.py`: **`67/67` (`100.0%`, `survived=0`, `truncated=False`) KILLED**.
  - `counterfactual_holonomy_audit.py`: **`58/58` (`100.0%`, `survived=0`, `truncated=False`) KILLED**.
  - Combined: **`125/125` (`100.0%`) KILLED**.
- **Exhaustive AST `BoolOp` (`SWAP` + `SUBCOND_DEL`, `timeout=30`) Sweep:**
  - `counterfactual_holonomy_oracle.py`: **`27/27` (`100.0%`, `surv=[]`) KILLED**.
  - `counterfactual_holonomy_audit.py`: **`15/15` (`100.0%`, `surv=[]`) KILLED**.
  - Combined: **`42/42` (`100.0%`) KILLED**.
- **Live Zone-B Adversarial Fuzzer:** **`23/23` CLI + `18/18` Memory = `41/41` (`100.0%`, `bypasses=0`, `crashes=0`) PASS**.
- **Hardened Zone-B Surface:**
  - **Race-free per-component `dir_fd` (`openat`) traversal:** Every intermediate directory component is opened atomically via `os.open(part, O_RDONLY | O_DIRECTORY | O_NOFOLLOW, dir_fd=dfd)` and the final leaf is opened via `os.open(leaf, flags | O_NOFOLLOW | O_NONBLOCK, dir_fd=dfd)` followed by `os.fstat(fd)`. Live 2,000-iteration concurrent `renameat2(RENAME_EXCHANGE)` read+write swap hammer confirmed `0` leaks and `0` outside clobbers.
  - **Deleted-CWD & Path Guards:** Relative paths wrap `Path.cwd()` cleanly into `CounterfactualHolonomyError("CWD_UNAVAILABLE", ...)` (`rc=2`, zero traceback), walk logical `PWD` components via `openat`, and refuse `S_ISREG` violations (`/dev/null`, FIFOs, directories), hardlink pre-`ftruncate` clobbering (`st_nlink > 1`), zero-size pseudofile OOM (`/proc/kallsyms`, bounded chunked `os.read`), `chmod 000` `OSError`s, flag-like CLI values (`--check --json`, `--write --json`), lone UTF-16 surrogates, non-ASCII digest `hmac.compare_digest` `TypeError`, and 5,000-digit integer / depth-65 DoS.
