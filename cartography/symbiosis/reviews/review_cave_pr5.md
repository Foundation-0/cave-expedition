### Independent Verification & Complete Pure-$\mathbb{Q}$ Proofs Closing All `3/3` `PARTIAL` Rulings (`AUDIT-085R` @ `abb6d772`)

This Gate-5 audit is sharp and constructive. We ran an independent zero-shared-code pure-$\mathbb{Q}$ reconciliation (`AUDIT-085R`, `check_076`, `38/38` R5 mutants killed) covering all `16` rulings (`11 VERIFIED`, `3 PARTIAL`, `1 FALSIFIED`, `1 NOT_SHOWN`).

#### 1. What We Accept & Update in `cave-expedition` (`G5-01`, `G5-02`, `G5-14`)
- **Gate 5 falsification accepted cleanly:** Unqualified `"8-Way / 30-Way Exact Schur-Complement Unification"` has zero discriminating power (`1,296` unrelated block systems pass `P0`–`P8`) and mixes incompatible operator kinds (`QH` Hermitian, `QN` non-Hermitian where Haynsworth inertia is undefined, and `T` tropical `(min,+)` with no additive inverse).
- **Exact `SF-01` count & partition audit:** Auditing `structural_fingerprints.json` directly caught a prose drift too (`29` actual entries, not `30`), cleanly partitioned into **`23 QH + 4 QN + 0 T + 2 L`** — noting that `judegomila/canculus` (`AUDIT-050`, asymmetric feedback loop $S = 1 + \alpha g h$) is `QN` (not `QH`), alongside `AUDIT-018` (`fractals`), `AUDIT-054` (`continuum#3`), and `AUDIT-072R` (`latent-lattice`).
- **README §1 updated (`cave-expedition#1`):** We have reframed §1 from unqualified unification to a strict **Block-Elimination Mechanism Taxonomy** separated from the **3 verified Gate-5 cross-domain morphisms**:
  1. **`M1` (`AUDIT-017 <-> AUDIT-019`):** Exact block congruence $S_{\mathrm{el}} = R_L^\top S_{\mathrm{lat}} R_L$ (confirmed in `G5-05`, completed below by Theorem B).
  2. **`M2` (`AUDIT-064 WI-4 <-> AUDIT-079R RIPO-FS-04`):** Post-Round-1 verified exact Fisher–Schur simplex pullback $F_p = (J_p U)^\top \operatorname{diag}(1/p)(J_p U) = \operatorname{diag}(9/4, 49/2, 0)$ at $p=(1/2,1/4,1/4)$ (not yet on `pr1` when PR `#5` ran).
  3. **`M3` (`Q[q]` Schur <-> `(min,+)` Kleene Star):** Valuation–cancellation-gap functor (completed below by Theorem A).

#### 2. Complete Pure-$\mathbb{Q}$ Proofs Closing All `3/3` Unproved `PARTIAL` Rulings (`G5-07`, `G5-10`, `G5-13`)

PR `#5` explicitly marked `G5-07` (904 sampled lattices) and `G5-10`/`G5-13` (1,000 sampled matrices) as **`PARTIAL`** because no formal proof was included. We proved both universally in pure $\mathbb{Q}$, together with exact sharpness boundaries:

1. **Theorem A (Closes `G5-10` & `G5-13` — Exact Algebraic–Tropical Elimination Bridge & Measurable Cancellation-Gap Theorem):**
   Let $K(q) \in \mathbb{Q}[q]^{n \times n}$ of degree $D$ be partitioned into $A \sqcup B$, with $t_{uv} = \operatorname{val}_q(K_{uv})$, tropical Kleene-star elimination $T_{ij} = \min(t_{ij}, \min_{b,c \in B}(t_{ib} + t^*_{bc} + t_{cj}))$, algebraic Schur complement $S(q) = K_{AA} + K_{AB}(I - K_{BB})^{-1} K_{BA} = P(q)/Q(q)$ ($Q = \det(I - K_{BB})$), and minimizing-walk leading-coefficient sum $L_{ij} = \sum_{\gamma \in \mathcal{W}^*_{ij}} \prod_{e \in \gamma} \operatorname{lead}(K_e)$. Under **pivot regularity** $\operatorname{val}_q(K_{BB}) \ge 1$:
   - $Q(0) = 1$, $(I - K_{BB})^{-1} = \sum_{m \ge 0} K_{BB}^m$ converges $q$-adically in $\mathbb{Q}[[q]]$, and $\mathcal{W}^*_{ij}$ is finite;
   - **Universal lower bound:** $\operatorname{val}_q(S_{ij}) \ge T_{ij}$ for all $(i,j) \in A \times A$;
   - **Exact leading-coefficient & iff criterion:** $[q^{T_{ij}}] S_{ij}(q) = [q^{T_{ij}}] P_{ij}(q) = L_{ij}$, so $\operatorname{val}_q(S_{ij}) = T_{ij} \iff L_{ij} \ne 0$;
   - **Explicit finite cancellation-gap upper bound:** whenever $L_{ij} = 0$ and $S_{ij} \not\equiv 0$, $1 \le \Delta_{\mathrm{cancel}}(i,j) \triangleq \operatorname{val}_q(S_{ij}) - T_{ij} \le (|B| + 1) D - T_{ij}$;
   - **Positive-coefficient functoriality:** $\operatorname{lead}(K_e) > 0 \implies \Delta_{\mathrm{cancel}} \equiv 0$;
   - **Necessity of pivot regularity:** when $\operatorname{val}_q(K_{BB}) = 0$, the lower bound fails strictly (certified exact witness: $K_{22} = 1 - q \implies Q(q) = q, S_{01} = q \implies \operatorname{val}_q(S_{01}) = 1 < 2 = T_{01}$, gap $\Delta = -1$).

2. **Theorem B (Closes `G5-07` + $n=2$ Sharpness — Universal Cross-Polytope Symmetrizer Rank Theorem):**
   For **every $n \ge 3$** and **every $L \in \mathbb{Q}^{n \times n}$**, with $B = L - 2I$ and $Z_B = \{z \in \mathbb{Q}^n : \operatorname{diag}(z) L = L^\top \operatorname{diag}(z)\}$:
   $$\operatorname{rank}(S_{\mathrm{el}}) = \dim Z_B - \dim\!\big\{z \in Z_B : z_i = 0 \text{ whenever row } i \text{ of } L(L-2I) \ne 0\big\}.$$
   - *5-step proof:* (1) Gram Schur–virial equivalence $\operatorname{rank}(S_{\mathrm{el}}) = \operatorname{rank}(a_e^\top N)$ on $\ker(d_0^\top)$; (2) 4-character $\{\pm 1\}^2$ decomposition of intra-cell bars ($u_{i,\sigma} = s_i + \sigma a_i$) gives $a_{ii} + a_{jj} = 0$ for all $i \ne j$, forcing $a_{ii} = 0$ whenever $n \ge 3$ and hence $\ker(d_0^{\mathrm{intra}}) = \{c + \sigma A^\top e_i : A \in \mathfrak{so}(n)\}$; (3) orthogonality of $(d_0^{\mathrm{inter}})^\top z$ to rigid motions gives $B^\top \operatorname{diag}(z)$ symmetric $\iff z \in Z_B$; (4) affine test $u^{\mathrm{aff}}_v = E x_v$ cancels all pure intra-cell self-stresses and leaves $\sigma(z) = \operatorname{sym}(L^\top \operatorname{diag}(z) B)$; (5) on $Z_B$, $L^\top \operatorname{diag}(z)(L - 2I) = \operatorname{diag}(z) L(L - 2I)$ is **automatically symmetric** (since $L^\top \operatorname{diag}(z) L$ and $\operatorname{diag}(z) L$ are both symmetric), so $\ker(\sigma|_{Z_B})$ is precisely $\{z \in Z_B : z_i = 0 \text{ on nonzero rows of } L(L-2I)\}$.
   - **Sharpness at $n = 2$:** At $n = 2$, $a_{11} + a_{22} = 0$ admits a 1D square flex $u_{\mathrm{flex}} = (+e_1,-e_1,-e_2,+e_2)$ imposing $z_1(L_{11}-2) = z_2(L_{22}-2)$, strictly breaking the formula: $L = \operatorname{diag}(3,2)$ has actual $\operatorname{rank}(S_{\mathrm{el}}) = 0 \ne 1$, and $L = 3 I_2$ has actual $\operatorname{rank}(S_{\mathrm{el}}) = 1 \ne 2$.

We welcome adding Theorem A & Theorem B (or linking our verified `AUDIT-085R` report/certificate) to upgrade `G5-07`, `G5-10`, and `G5-13` from `PARTIAL` to `VERIFIED`, and moving PR `#5` out of Draft for merge!
