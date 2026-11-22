### Pre-Data Pure-$\mathbb{Q}$ Statistical-Power, Symmetry & Net-Invariance Audit (`AUDIT-087R` @ `24d77573`)

Strong pre-registration discipline here: zero telemetry fetched, temporal fit/verdict splits pinned before opening data, SHA-256 input pinning (`DATA_REQUEST.md:58`), deterministic SHA-256 seeds (`PREREG.md:231`), zero-shared-code recount (`PREREG.md:233`), and fair non-falsification author requests for `T2`, `T4`, and `T1`-interference (`PREREG.md:99-123`).

We audited `PREREG.md`, `DATA_REQUEST.md`, and `ARM_B_OUTLINE.md` in pure $\mathbb{Q}$ (`AUDIT-087R`, `check_077`, `108/108` R5 mutants killed, `0` telemetry fetched). All four `DATA_REQUEST.md` byte sums (`634,994,866 B` total), Burnside's Lemma on $S_4/V_4$ (`8` orbits: `4` size-2 + `4` size-4), Laplace smoothing, Holm `1/560` presence cutoffs (`K >= 5/12`, `K >= 7/32`), and Berger intersection-union conservation verify identically.

Before any data are downloaded, we found **four concrete pre-data traps (`PREREG-01..04`)** that will distort verdicts on clean data unless amended now:

#### 1. `PREREG-01a/b` [HIGH/MED] — Control Conjunction Override (`PREREG.md:150, 156`) & `K2` Quantile Off-by-One (`PREREG.md:210-211`)
- **`PREREG.md:150`:** `K < K_1%` (`K < 4` at `S=12`, `K < 6` at `S=32`) **AND** `K/S <= 0.10`. The `AND K/S <= 0.10` clause strictly overrides both `1%` binomial bounds down to `K <= 1` (`S=12`) and `K <= 3` (`S=32`), making `K < 4` and `K < 6` dead code! Under a **100% calibrated null** ($p_0 = 1/20$):
  - At `S = 12`: single-control fail prob jumps **`52.92x`** (`0.002236 -> 0.118359`), per-instrument (`C2, C3, C4`) false invalidation hits **`31.47%`**, and `>= 1` of `3` instruments invalid hits **`67.82%`** (`77.95%` for `4`).
  - At `S = 32`: single-control fail prob jumps **`16.05x`** (`0.004599 -> 0.073805`), per-instrument hits **`20.55%`**, and `>= 1` of `3` instruments invalid hits **`49.84%`** (a coin flip before opening real data!).
  - **Fix:** Drop the `AND K/S <= 0.10` override (use exact `1%` binomial `K < 4` / `K < 6`, or `OR` for large $S$), reducing per-instrument false invalidation at `S = 32` from `20.55%` to **`1.37%`** (`5.38%` across 4 instruments).
- **`PREREG.md:211`:** `0.086` on `200` draws sets pass `K <= 17` (fail `K >= 18`), whose exact tail is $P(\operatorname{Bin}(200, 1/20) \ge 18) = \mathbf{0.012089 > 0.01}$ (`22.54%` FWER across `21` noise classes!). True `<= 1%` cutoff is `K <= 18` (`0.090`, tail `0.005823`), and `K <= 20` brings `21`-class FWER to **`2.41%`**.

#### 2. `PREREG-02` [CRITICAL] — Exact $R \circ P$ Symmetry Forces $u \equiv 0$ & `2/3` Time-Even Dilution of `K4` `A -> C` (`PREREG.md:84-89, 214-220`)
- Under $d = 3$ ordinal log-ratios, polarity flip $P$ gives $(a_1, s, u) \mapsto (-a_1, -s, +u)$, time reversal $R$ gives $(-a_1, -s, -u)$, and **180° rotation $R \circ P$** gives $(+a_1, +s, -u)$.
- Therefore every $R \circ P$-invariant asymmetric waveform (such as a clean sawtooth or jump-decay pulse train) satisfies `n(021) == n(102)` and `n(120) == n(201) == 0` at every lag $\tau \in \{1, 2, 4, 8\}$, forcing **`u = a_2 - a_3 == 0` identically**.
- Simultaneously, **`20/30` (`2/3`) of the `T3` transfer features** (`m1 = |a1|`, `m23 = |a2 + a3|`) are **TIME-EVEN** (`|(-a)| == |a|`)! Under time reversal (`A -> C`), those `20` features still align **positively** (`cos = +1`) with `w_A`, directly fighting the `10` time-odd `u` features expected to drive `A -> C` below the `2.5th` percentile (`K4`).
- **Fix:** Split `T3` transfer cleanly into **(i) Polarity-Free Time-Arrow Transfer** (`u` only, `10` features — strictly reverses sign under `A -> C`) and **(ii) Time-Even Magnitude-Profile Transfer** (`m1, m23`, `20` features — reported separately without an anti-correlation gate under `A -> C`).

#### 3. `PREREG-03` [HIGH] — End-Matching Offset Selection Breaks Monotone-Map Invariance (`PREREG.md:134, 163`)
- `PREREG.md:134` skips the monotone-amplitude net analytically, yet `PREREG.md:163` picks segment offset `o in 0..128` using raw Euclidean squared end-jumps `(x[-1]-x[0])^2 + ((x[1]-x[0])-(x[-1]-x[-2]))^2`.
- **Exact counterexample (`N = 6` on `[10, 10, 0, 1, 11, 11, 2, 2]`):** Raw costs = `[1, 65, 5]` $\implies$ selects **`o = 0`**. Under `K1`'s strictly increasing map $f(x) = x^3 + x$: mapped costs = `[110224, 1103684, 104]` $\implies$ flips to **`o = 2`** (selecting a different window and different ordinal counts!).
- **Fix:** Apply the identical end-matching objective to **exact mid-ranks** (`rank_transform_exact(block)`): raw and mapped rank costs are both `[4/1, 17/4, 29/4]`, selecting unique **`o = 0`** identically under every strictly increasing map and polarity flip.

#### 4. `PREREG-04` [MED] — Quorum Margin, Scale-Flow Sample Budgets & `ARM_B` Capacity (`PREREG.md:104-107, 138, 238`; `ARM_B_OUTLINE.md:14`)
- Pre-excluding `TESS` leaves a zero-margin `3/3` quorum (`GW, SEIS, WAVES`) for `>= 3`.
- With `B(l) = 50,688 * 2^l` (`12` blocks of `4,224` samples): `TESS` (`27d @ 20s`, `116,640` samples) reaches at most `l_max = 1` (`>= 40/56 = 71.43%` of `T1` features zero-padded), and `Wind/WAVES` (`8d * 4ch`) needs average cadence **`<= 600/11 = 54.55 s`** (`60s` gives `10 < 12` blocks, `192s` gives `3 < 12`).
- Restrict `w_A` feature permutations strictly to the jointly populated support $\mathcal{L}_A \cap \mathcal{L}_B$ (avoiding zero-pad dilution and accounting for the `7` independent DoF of the `8` $S_4/V_4$ orbit proportions).
- In `ARM_B_OUTLINE.md:14`, `50 * d!` reaches `6,000 > 4,096` at `d = 5`, and `d = 6` Markov transitions (`4,320 * 50 = 216,000`) exceed `32 * 4,096 = 131,072` windows; pin the exact segment pooling or cap $d$ before running Arm B.

Once `PREREG-01..04` are amended in commit before fetching data, this will be a rock-solid pre-registration!
