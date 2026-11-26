# Historical Exact-Operator Applications & Gate-5 Congruence Boundaries

- **Schema Version:** `cave-expedition.historical-operators-gate5.v1`
- **Arithmetic Domain:** `exact_Z_Q_Qs2_stdlib_zero_floats_zero_logs` (`int`, `fractions.Fraction`, `math.gcd`, exact $\mathbb{Q}(\sqrt{2})$ pairs; zero AST float literals, zero `float()` calls, zero `math.log`, zero bare `assert` statements)
- **Certificate Payload SHA-256:** `dfb35d6970f6157169919f823f16e43ed65ae1c70f9d1a342ee7be34a7d217ae`
- **Sealed Certificate SHA-256:** `af95a89d192ae20fbe239e7ac441fa8b81fd922e8cc0ae9da86e79b7bfa3b933`
- **Related Ledger Entries:** `AUDIT-002`, `AUDIT-004`, `AUDIT-009`, `AUDIT-010`, `AUDIT-014`, `AUDIT-017`, `AUDIT-018`, `AUDIT-019`, `AUDIT-020R`

---

## 1. Architectural Scope & Outside Gate-5 Alignment

In `README.md` §1 (*"What an outside check found"*), the independent outside audit established that eight domain models share **block elimination** rather than a single cross-domain Sylvester congruence. `verify_historical_operators.py` formalizes and machine-checks that exact boundary over $\mathbb{Q}$ without modifying `verification/checks/check_003_seam01_ropt.py` (`ae239507fecea4fdd9d5d0ef2e298483ddf040067b5987dffdeb684873feac86`) or `verification/outside/`:

1. **Self-Certifying Congruence Solver (`certified_symmetric_congruence_inertia_q`):** For every symmetric $M \in \mathbb{Q}^{n \times n}$ (using $1 \times 1$ pivots and $2 \times 2$ hyperbolic splittings when all remaining diagonal entries vanish), the verifier constructs an explicit invertible $P \in GL_n(\mathbb{Q})$ and diagonal vector $d \in \mathbb{Q}^n$, and verifies both $P^\top M P = \operatorname{diag}(d)$ and $\operatorname{rank}_{\mathbb{Q}}(P) = n$ (`verify_congruence_certificate_q`).
2. **Unitriangular Haynsworth Additivity (`schur_pushforward_with_congruence_q`):** For every partitioned matrix $M = \begin{pmatrix} M_{BB} & M_{BI} \\ M_{IB} & M_{II} \end{pmatrix}$ with nonsingular interior $M_{II}$, the verifier constructs the explicit unitriangular elimination matrix $U \in GL_n(\mathbb{Q})$ satisfying
   $$U^\top M_{\mathrm{perm}} U = \operatorname{diag}(M / M_{II},\, M_{II}), \qquad \operatorname{In}(M) = \operatorname{In}(M_{II}) + \operatorname{In}(M / M_{II}).$$
3. **Exact Congruence vs. Non-Congruence Classification:**
   - **Congruent Signed Pair (`[4, 4, 0]`):** `AUDIT-019`'s Sylvester–Hadamard $H_8$ fold-sheaf stress operator $\Sigma_\star = C^\top C + 2C = 2I_8 + H_8$ ($C = \tfrac{1}{2}H_8$) and `AUDIT-017`'s shifted Gram operator $2(G(1) - 2I_8) = 8I_8 + 4H_8$ satisfy $P^\top \Sigma_\star P = 2(G(1) - 2I_8)$ with $P = 2I_8 \in GL_8(\mathbb{Q})$ and matching Sylvester inertia `[4, 4, 0]`.
   - **Non-Congruent Passive M-Matrix Networks (`n_- = 0`):** Every passive hydraulic conductance Laplacian has $n_- = 0$ (`[7, 0, 0]` for vented Petra Siq, `[10, 0, 1]` for 9-pipe Roman Gier, `[12, 0, 1]` for Casarabe $C_{2,6}$, `[7, 0, 1]` for a matched-dimension $8 \times 8$ conduit), proving over $\mathbb{Q}$ and $\mathbb{R}$ that passive hydraulic networks share **block elimination only** and are **not Sylvester-congruent** to `[4, 4, 0]` fold/packing stress operators.

---

## 2. Theorem Family 1 — Physical Schur Pushforwards & Gate-5 Inertia Table

All network models are constructed directly in memory over $\mathbb{Q}$ (`n_nodes <= 128`):

| Physical / Statistical Model | Full Dim | Boundary $B$ | Exact Schur Witness | Certified Inertia $(n_+, n_-, n_0)$ |
|---|---:|---|---|---|
| Petra Siq 6-stage conduit (unvented vs. 5-basin vented) | $7 \times 7$ | $\{0, 6\}$ | Surge transfer drops $1/3 \to 64/1365$ ($455/64\times$ attenuation) | Vented: `[7, 0, 0]` |
| Roman Lyon Gier 9-pipe inverted siphon ($k \in \{9, 8, 7\}$) | $11 \times 11$ | $\{0, 10\}$ | $g_{\mathrm{eff}} = 9/1,\, 8/1,\, 7/1$ (ratios $8/9,\, 7/9$) | Full `[10, 0, 1]` = Int `[9, 0, 0]` + Schur `[1, 0, 1]` |
| Amazonian Casarabe radial-ring canal graph $C_{2,6}$ ($b_1 = 12$) | $13 \times 13$ | $\{0, 7\}$ | $g(C_{2,6}) = 2755/1806 > g(C_{13}) = 13/42 > g(T_{13}) = 1/12$; 1-spoke cut retains $427248/498655$ ($1656/1267$) | `[12, 0, 1]` |
| Ibn al-Nafis 3-variable covariance pushforward (`AUDIT-018`) | $3 \times 3$ | $\{0, 1\}$ | $\det$: $34/625 \to 688/15625$; trace drop $81/1250$ | Schur: `[2, 0, 0]` |
| Matched-dimension passive hydraulic conduit | $8 \times 8$ | — | Gate-5 non-congruence witness vs. $\Sigma_\star$ | `[7, 0, 1]` ($\neq [4, 4, 0]$) |
| Fold-sheaf stress $\Sigma_\star = 2I_8 + H_8$ (`AUDIT-019`) | $8 \times 8$ | — | $P^\top \Sigma_\star P = 2(G(1)-2I_8)$ at $P = 2I_8$ | `[4, 4, 0]` |
| Shifted packing Gram $2(G(1) - 2I_8)$ (`AUDIT-017`) | $8 \times 8$ | — | Exact Sylvester match with $\Sigma_\star$; $G(1)$ has `[8, 0, 0]` | `[4, 4, 0]` |

---

## 3. Theorem Family 2 — Discrete Parity, Chokwe Sona Sheaf Nullity & Al-Biruni Stereographic Folds

1. **Pingala `nasta(3, k)` & Sylvester–Hadamard $H_8$ (`n_syllables <= 32`):** Evaluating $(-1)^{\langle \operatorname{nasta}(3, a),\, \operatorname{nasta}(3, b) \rangle}$ across $1 \le a, b \le 8$ reproduces $H_8 = H_2^{\otimes 3}$ entry-for-entry (`64/64`).
2. **Yoruba Ifa Even-Parity Spinor Roots (`AUDIT-017`):** Filtering $\operatorname{nasta}(8, k)$ ($1 \le k \le 256$) by even parity yields $128$ distinct half-integer vectors $\tfrac{1}{2}(\pm 1)^8$ of squared norm $2$; combined with the $4 \times \binom{8}{2} = 112$ integer roots of $D_8$, they form all $128 + 112 = 240$ minimal vectors of $E_8$.
3. **Bamana $\mathbb{F}_2^4$ First-Order Reed–Muller Code $\operatorname{RM}(1, 4)$ (`AUDIT-020R`):** Generating all $32$ affine Boolean functions on $\mathbb{F}_2^4$ yields weight enumerator $1 \cdot x^0 + 30 \cdot x^8 + 1 \cdot x^{16}$ and exact $\mathbb{F}_2^{16}$ orthogonality against all $5$ parity-check rows of the extended Hamming $[16, 11, 4]$ code underlying the Barnes–Wall lattice $\Lambda_{16}$.
4. **Chokwe Sona Cellular Sheaf Nullity (`sona_sheaf_laplacian_nullity_q`, `m_rows, n_cols <= 8`):** Across all $16$ rectangular sand-drawing grids $1 \le m, n \le 4$, exact row-echelon rank of the $4mn$-segment coboundary matrix $d_0$ over $\mathbb{Q}$ certifies
   $$\dim \ker \Delta_{\mathcal{F}}(m, n) = \dim \ker d_0(m, n) = \gcd(m, n),$$
   so monolinear (`gcd(m, n) = 1`) drawings have zero internal floppy modes (`sheaf_ker_dim - 1 == 0`). Inserting an internal vertical mirror wall at $(2, 1)$ merges $[2 \to 1]$ on $2 \times 2$ (`AUDIT-019` monolinearization) and splits $[1 \to 2]$ on $2 \times 3$.
5. **Al-Biruni Stereographic Meridian Unification (`AUDIT-009` & `AUDIT-017`):** In exact $\mathbb{Q}(\sqrt{2})$ field arithmetic (`Qs2`), the rational meridian parametrization $(-Z_{\mathrm{Biruni}}(s),\, X_{\mathrm{Biruni}}^2(s)) = \left(\frac{1 - \kappa^2 s^2}{1 + \kappa^2 s^2},\, \frac{4\kappa^2 s^2}{(1 + \kappa^2 s^2)^2}\right)$ unifies:
   - `AUDIT-009` ($F_n \to D_n$) at $\kappa^2 = 1$, preserving bar norm $\|b_i(s)\|^2 = 2$; and
   - `AUDIT-017` ($F_8 \to E_8$) at conjugate moduli $\kappa_\pm^2 = \frac{9 \mp 4\sqrt{2}}{7} \in \mathbb{Q}(\sqrt{2})$, satisfying $a_\pm(s) - 2 = \sqrt{2}\,(-Z_{\mathrm{Biruni}}(\kappa_\pm s))$, $7\,b_\pm(s)^2 = 2\,X_{\mathrm{Biruni}}^2(\kappa_\pm s)$, exact norm preservation $(a_\pm(s)-2)^2 + 7b_\pm(s)^2 = 2$ at $s \in \{0, \tfrac{1}{4}, \tfrac{1}{3}, \tfrac{1}{2}, 1\}$, and strict positive definiteness of the interior $2 \times 2$ cross-Gram defect on $s \in \{\tfrac{1}{4}, \tfrac{1}{3}, \tfrac{1}{2}\}$.

---

## 4. Theorem Family 3 — Zero-Log Multiplicative Farkas & Madhava–Hankel Spectral Tightening

1. **Al-Farabi 53-TET Pairwise Multiplicative Farkas Obstruction (`AUDIT-010`):** On the 4-node chain $m \in (0, 18, 36, 53)$ with relative tolerance $\pm 1/1200$ around $(3/2)^m$, all three adjacent local steps satisfy the cleared-denominator 53-TET slope test $(y_j^+ / y_i^-)^{53} \ge 2^{31\Delta m} \ge (y_j^- / y_i^+)^{53}$, whereas the global $(0, 53)$ span fails (`farabi_global_span_pass_31_53 == False`), anchored by Holder's comma $3^{53} / 2^{84} = 19383245667680019896796723 / 19342813113834066795298816 > 1$ and the Zalzal non-closure $12^{53} \neq 11^{53} \cdot 2^7$.
2. **Zu Chongzhi $355/113$ Four-Ray Log-Concavity Refutation:** On $Y = ([355/113, 4], [2, 3], [2, 3], [355/113, 4])$, both local 3-point rays $(1, 0)$ and $(0, 1)$ pass (`355/113 * 2 = 710/113 <= 9`), whereas the non-local 4-point Farkas rays $(2, 1)$ and $(1, 2)$ directly refute global log-concavity (`(355/113)^2 * (355/113) = 44738875/1442897 > 27`); the 4-ray condition itself is also cross-checked on exact dyadic exponent boxes ($y_k = 2^{h_k}$) against an independent additive $\mathbb{Q}$ Fourier–Motzkin elimination oracle (`fourier_motzkin_log_concave_additive_q`).
3. **Madhava $(R_2(n), R_3(n))$ Closure of `AUDIT-014` Stieltjes–Hankel Rank Certification (`n_even <= 128`):** For the rank-3 benchmark $P(\sigma) = \operatorname{diag}(2, 1, \tfrac{4}{5} - \sigma)$ at $\sigma = \pi/4$:
   - At $n = 2$ terms, raw Leibniz partial sums $[2/3, 1]$ cannot even certify $\tfrac{4}{5} - \sigma > 0$, leaving $\lceil R_{H,4}^{\mathrm{raw}}(2) \rceil = 2$, while the 2-moment bound `R_opt` satisfies $\lceil R_{\mathrm{opt}}(2) \rceil = 2 < 3$.
   - Madhava's rational correction pair $R_2(2) = 2/17$ and $R_3(2) = 5/42$ encloses $\sigma \in [40/51, 11/14]$ and $\lambda_3 \in [1/70, 4/255]$, pushing the 4th-moment Stieltjes–Hankel lower bound strictly above $2$ (`n2_rh4_madhava_lower = 3386788761049388311736/1657858848278228557931 > 2`) so $\lceil R_{H,4}^{\mathrm{Madhava}}(2) \rceil = 3 = \operatorname{rank}(P)$.
   - At $n = 20$ terms, Madhava $(R_2(20), R_3(20))$ narrows the rational $R_{H,4}$ enclosure width by a certified integer floor factor of $1{,}314{,}575\times$.

---

## 5. Provenance Anchors & Hardened Validation Contract

`PROVENANCE_ARTIFACT_DIGESTS` pins eight `64`-hex SHA-256 reference digests (`andean_khipu_amazonian_networks_cert`, `east_asian_egyptian_maya_operators_cert`, `logfree_53tet_power_unifier_cert`, `mediterranean_african_operators_cert`, `outside_anchor_check_003_seam01_ropt_py`, `primary_arabic_heritage_engines_cert`, `south_asian_prosody_panini_madhava_cert`, and `spinor_hippopede_readable_records_cert`). `validate_certificate()` enforces:

1. Schema, arithmetic-domain, Gate-5 scope, and `is_hex64()` validation across all provenance and envelope digests;
2. Per-theorem invariant checks (`verify_core_invariants`);
3. Canonical UTF-8 SHA-256 verification of `payload_sha256` and `certificate_sha256`; and
4. Byte-exact canonical JSON identity (`canonical_json_bytes(cert) == canonical_json_bytes(build_certificate())`) against a fresh pure-$\mathbb{Q}$ oracle run, rejecting both re-hashed forged numerical witnesses and Python `bool`-for-`int` (`True == 1`) type confusion.
