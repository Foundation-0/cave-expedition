# Track S20c — Real Public Raw Physical Telemetry Portal (MP-04)

- **Track ID:** `TRACK-S20C`
- **Oracle Class:** `exact+empirical_physical_telemetry`
- **Novelty Tag:** `N1` (engineering & empirical falsification study applying exact zero-float $\mathbb{Z}/\mathbb{Q}$ relational operators and matched exact surrogates to four real public unauthenticated physical telemetry streams; makes zero unproved universal claims)
- **Arithmetic & Trust Boundary:** Zero IEEE-754 `float` values on any computation, verification, or serialization path; zero bare `assert` statements; full `strict_cert_io`-grade Zone-B hardening (`MAX_INT_BITS=2048`, `MAX_JSON_DEPTH=64`, strict 64-lowercase-ASCII-hex digest validation before `hmac.compare_digest`, unpaired UTF-16 surrogate & NUL path guards, regular-file & symlink-ancestor checks, canonical LF-only JSON).
- **CLI & Library Separation:** `physical_telemetry_audit.py` is the standalone CLI (`--generate` / `--check`, defaulting `--check` to full `99 x 3` surrogate + 6-control replay; `--observed-only` and `--no-replay` are explicit opt-out flags, mutually exclusive with `--full-replay`), while `physical_telemetry_oracle.py` is the pure-stdlib library module.

---

## 1. Gate-8 Pre-Registration & Raw Public Provenance

All four physical telemetry slices were retrieved via live `HTTP 200` unauthenticated public scientific APIs (zero credentials, zero anti-bot bypass), pinned by SHA-256 in `FETCH_MANIFEST.json`, and locked under `PREREG_S20C.json` **before** evaluating held-out confirmatory `Window B` (`[256:512]`). Neither `FETCH_MANIFEST.json` nor `PREREG_S20C.json` was modified after `Window B` evaluation.

- `FETCH_MANIFEST.json` SHA-256: `d582694ae0ae30c369c971794e8da2f65461c5361847599a1cc844086d22687a`
- `PREREG_S20C.json` SHA-256: `16422cc3796e501ac29ea605bdb30271fb216c56669b02a7078f2f3b86f017ef`

### Table 1 — Stage-A Raw Physical Telemetry Provenance (Labels Stripped Before Operator Execution)

| Stripped ID | Physical Domain (Stripped in Stage A) | Public API Source & Event / Station | Local Slice File | Exact Scale ($10^k$) | Raw Slice Bytes | Local Slice SHA-256 |
|---|---|---|---|---:|---:|---|
| `STREAM_A` | Gravitational-Wave Interferometry | LIGO GWOSC Hanford H1 `GW150914` (4096 Hz, samples `[62694:63206]` spanning inspiral -> merger -> ringdown; full `.txt.gz` `1,286,320` B SHA `fefe8717...`) | `raw_telemetry/gwosc_gw150914_h1_512.txt` | $10^{40}$ | 12,004 | `849d0f54a44efb02889791b696f1cfe16bc664b67e809c739e15b859ea1f0439` |
| `STREAM_B` | Magnetospheric Space Weather | USGS INTERMAGNET Boulder (`BOU`), May 10, 2024 G5 Geomagnetic Superstorm ($X$-component, 60 s cadence, first 512 samples) | `raw_telemetry/usgs_geomag_bou_20240510.json` | $10^{3}$ | 20,413 | `084f104eac395bbc24c858da1a36f0e55c13ed854bc242044cd1b2c2574cfac3` |
| `STREAM_C` | Coastal Oceanography | NOAA CO-OPS San Francisco Golden Gate (`9414290`), Jan 1–3, 2024 MLLW tide water level (360 s cadence, first 512 samples) | `raw_telemetry/noaa_coops_9414290_20240101_03.json` | $10^{3}$ | 53,951 | `885e2548b5427c9a774e227839e998341ece9fdd1701917cc97b6e50d37100fc` |
| `STREAM_D` | Fluvial Hydrology | USGS NWIS Potomac River near Washington, DC (`01646500`), Jun 1–6, 2024 instantaneous discharge (`00060`, 900 s cadence, first 512 samples) | `raw_telemetry/usgs_nwis_01646500_20240601_06.json` | $10^{2}$ | 48,006 | `5837857f1508a751227b30405e65b73729914ad55155f6f6b72e120b4c2bd310` |

Every stream has $N_{\text{total}} = 512$ lossless scaled integers (`PRECISION_LOSS` fails closed if any decimal digit would truncate), partitioned strictly into:
- **Calibration `Window A`:** indices `[0:256]` (256 samples; descriptive calibration only)
- **Held-Out Confirmatory `Window B`:** indices `[256:512]` (256 samples; sole input to Gate-8 verdicts)

---

## 2. Exact Zero-Float Relational Operators & Matched Surrogate Nulls

Before any operator runs, disciplinary labels and physical units are stripped (`STREAM_A..D`), and each 256-sample window is mapped to monotone-invariant **exact doubled mid-ranks** $r_t \in [0, 2(N-1)]$ ($\sum_t r_t = N(N-1)$ identically) and **exact zero-centered ranks** $c_t = r_t - (N-1)$ ($\sum_t c_t = 0$ identically).

1. **`OP1_SEAM1` (Sliding Rank-1 Sherman–Morrison Leverage Shock):**
   For lag vectors $u_t = (N-1, c_t, c_{t-1}) \in \mathbb{Z}^3$, ridge $\lambda = (N-1)^2$, and sliding window $W = 32$, exact integer Gram updates $G_t = \lambda I_3 + \sum_{s=t-W}^{t-1} u_s u_s^\top$ and exact $3\times 3$ adjugate inverses yield causal leverage $h_t = q_t / (1 + q_t) \in \mathbb{Q}$ ($q_t = u_t^\top G_t^{-1} u_t$) over $K = 223$ steps. Locked primary statistic: $\rho_{\text{S1}} = \max_t h_t / \operatorname{med}_t h_t \in \mathbb{Q}$.
2. **`OP2_SEAM3` (Undirected HVG $H^1$ $\beta_1$ & Directed Ordinal Hodge-Curl $\Phi_{\text{asym}}$):**
   - Exact $O(N)$ monotonic-stack Horizontal Visibility Graph (verified against brute-force $O(N^3)$ in tests) yields $\beta_1^{\text{HVG}} = |E| - (N-1)$ (while the causal forward HVG DAG is always acyclic/grounded).
   - Exact $m=3$ ordinal patterns (states `0..5` for strict permutations, state `6` for any tie) form a $7 \times 7$ transition count matrix $C$, yielding the exact time-irreversibility ratio
     $$\Phi_{\text{asym}} = \frac{\sum_{a < b} (C_{ab} - C_{ba})^2}{\sum_{a < b} (C_{ab} + C_{ba})^2} \in \mathbb{Q} \cap [0, 1]$$
     together with an explicit Farkas directed cycle witness (`2`-cycle or `3`-cycle on positive transitions).
3. **`OP3_F3` (Non-Normal Lag-3 Companion VAR(1), Jury Stability, Sylvester Inertia & Commutator):**
   Ridge lag-3 companion operator $T = C_z (\lambda I_3 + Z^\top Z)^{-1} \in \mathbb{Q}^{3\times 3}$ is checked for strict spectral stability $\rho(T) < 1$ via the exact 3rd-order Jury/Schur–Cohn inequalities, exact Sylvester inertia $\operatorname{In}(I_3 - T^\top T) = (n_+, n_-, n_0)$ via exact $1\times 1$/$2\times 2$ symmetric rational congruence (handling zero-diagonal hyperbolic blocks), and normalized non-normal commutator $\kappa_{\text{F3}} = \|T^\top T - T T^\top\|_F^2 / \operatorname{tr}(T^\top T)^2 \in \mathbb{Q}$.
4. **Three Exact Matched Surrogate Null Families ($M = 99$, $\alpha = 5/100$, deterministic SHA-256 counter PRNG):**
   - `IID_PERM`: exact Fisher–Yates permutation of ranks (destroys all temporal dependence).
   - `BLOCK_16`: exact random circular shift + Fisher–Yates permutation of 16 contiguous blocks of length 16 (preserves short-range local autocorrelation).
   - `WHT_PHASE`: exact integer Walsh–Hadamard Transform $\mathrm{WHT}_{256}$ ($H_{256}^2 = 256 I_{256}$, exact Parseval energy conservation) with deterministic random Rademacher $\pm 1$ sign flips on non-DC sequency components $k = 1..255$, inverse $\mathrm{WHT}_{256}$, and exact re-ranking (preserves the exact integer Walsh–Hadamard power spectrum prior to monotone re-ranking, giving approximate spectral preservation after re-ranking).
5. **Pre-Registered Decision Rule (`PREREG_S20C.json`):**
   - For surrogate-tested hypotheses (`H1`, `H2a`, `H2b`, `H3b`), a domain passes **iff** exact upper-tail empirical $p = (c_{\ge} + 1)/(M + 1) \le 5/100$ simultaneously under **all three** null families (`IID_PERM`, `BLOCK_16`, `WHT_PHASE`).
   - For structural non-normal witness `H3a`, a domain passes **iff** `schur_stable == True` and $n_-(I_3 - T^\top T) \ge 1$ ($\sigma_{\max}(T) > 1$).
   - Cross-domain classification across the 4 domains: `SUPPORTED` ($\ge 3/4$), `PARTIAL` ($1\text{–}2/4$), `FALSIFIED` ($0/4$).

---

## 3. Known-Answer Synthetic Controls (6 / 6 Exact Pass)

| Control | Invariant / Test | Result | Exact Evidence |
|---|---|---|---|
| `KA_MONO_EXACT` | Strict monotone transform $3x^3 + 7x + 10000$ | `PASS` | Exact equality across ranks, `OP1`, `OP2`, `OP3` |
| `KA_TIME_REV_EXACT` | Time reversal of non-dyadic period-13 sawtooth | `PASS` | $\beta_1^{\text{HVG}}$ and $\Phi_{\text{asym}}$ invariant; signed net flux negates exactly |
| `KA_WHT256_PARSEVAL_EXACT` | $\mathrm{WHT}_{256}$ Parseval energy & involution | `PASS` | $\sum \hat{x}_k^2 = 256 \sum x_i^2$ and $H_{256}(H_{256} x) = 256 x$ identically |
| `KA_IID_NULL_CLEAN` | Synthetic SHA-256 IID white noise must fail all gates | `PASS` | `0/5` hypotheses pass (including `H3a = False`, `In = (3,0,0)`) |
| `KA_SAWTOOTH_IRREV_DETECTED` | Non-dyadic period-13 sawtooth irreversibility | `PASS` | $p(\text{IID}) = 1/100$, $p(\text{WHT}) = 1/100$ (note: `BLOCK_16` $p = 71/100$ because block length $16 > 13$ preserves intact sawtooth ramps) |
| `KA_SAWTOOTH_F3_DETECTED` | Non-dyadic sawtooth non-normal transient witness | `PASS` | `schur_stable = True`, `In(I_3 - T^T T) = (2, 1, 0)` |

*Engineering Honesty Note on Synthetic Sawtooth Design:* Our initial synthetic sawtooth fixture used period `16`, which aliased exactly with both `BLOCK_16` ($p = 1$) and dyadic `WHT_256` ($p = 9/20$, because a period-$2^4$ ramp concentrates energy onto 4 Rademacher Walsh functions). Updating only the synthetic sawtooth period to the non-dyadic prime `13` resolved the dyadic aliasing cleanly without touching `FETCH_MANIFEST.json`, `PREREG_S20C.json`, or any real-data Window B computation.

---

## 4. Held-Out `Window B` Results & Pre-Registered Cross-Domain Verdicts

### Table 2 — Pre-Registered Gate-8 Cross-Domain Verdicts (Verbatim)

| Hypothesis ID | Operator & Pre-Registered Claim | Passing Domains (of 4) | Verdict | Scientific Interpretation |
|---|---|---:|---|---|
| `H1_SEAM1_SHOCK` | Sliding rank-1 leverage shock $\rho_{\text{S1}}$ exceeds all 3 nulls | `0 / 4` (`[]`) | **`FALSIFIED`** | **Matched-surrogate false-positive cure:** `3/4` streams (`A, B, D`) look significant under naive `IID_PERM`, yet collapse to $p \ge 91/100$ under `BLOCK_16` and `WHT_PHASE` because block stitches and Walsh phase flips create harsher rank-1 leverage jumps than smooth nature. |
| `H2a_SEAM3_HVG_BETTI1` | Undirected HVG $\beta_1^{\text{HVG}}$ exceeds all 3 nulls (upper tail) | `0 / 4` (`[]`) | **`FALSIFIED`** | Smooth physical persistence *suppresses* HVG chords strictly below the Luque et al. (2009) IID ceiling ($\langle k \rangle = 4 \Rightarrow \beta_1 \approx 256$): observed $\beta_1 \in \{227, 217, 154, 71\}$ gives upper-tail $p = 1$ on `4/4` IID. Locked upper-tail hypothesis is cleanly falsified (lower-tail suppression noted post-hoc only). |
| `H2b_SEAM3_IRREV_PHI` | Directed ordinal Hodge-curl $\Phi_{\text{asym}}$ exceeds all 3 nulls | `2 / 4` (`STREAM_A`, `STREAM_B`) | **`PARTIAL`** | **Sharp physical regime discriminator:** survives all 3 nulls (`IID`, `BLOCK_16`, `WHT_PHASE`) exclusively on driven non-equilibrium transients (LIGO `GW150914` merger/ringdown & USGS Boulder G5 superstorm), while failing on the quasi-reversible semi-diurnal ocean tide (`STREAM_C`) and heavily quantized river discharge (`STREAM_D`). |
| `H3a_F3_TRANSIENT_WITNESS` | Lag-3 ridge VAR(1) is Schur-stable with $n_-(I_3 - T^\top T) \ge 1$ | `4 / 4` (`STREAM_A..D`) | **`SUPPORTED`** | All `4/4` real physical streams (and `4/4` calibration `Window A` streams) yield strictly Schur-stable operators with $\operatorname{In}(I_3 - T^\top T) = (2, 1, 0)$, vs `False` on `KA_IID_NULL`. **Diagnostic qualification:** `IID_PERM` yields the witness in only `1–10/99` draws, whereas autocorrelation-preserving `BLOCK_16` and `WHT_PHASE` yield it in `99/99` draws on all 4 streams — proving this witness captures **linear persistence-coupled companion non-normality** rather than higher-order nonlinearity. |
| `H3b_F3_COMMUTATOR` | Normalized commutator $\kappa_{\text{F3}}$ exceeds all 3 nulls | `0 / 4` (`[]`) | **`FALSIFIED`** | Pure nilpotent shift dynamics (IID white-noise limit) maximize $\kappa_{\text{shift}} = 2/4 = 0.500$, whereas persistent physical dynamics ($\kappa_{\text{F3}} \in [0.122, 0.331]$) grow $\operatorname{tr}(T^\top T)^2$ faster than $\|T^\top T - T T^\top\|_F^2$ ($p \in [99/100, 1]$ on `4/4`). |

### Table 3 — Exact Held-Out `Window B` (`[256:512]`) Measurements & Exact Rational Surrogate $p$-Values

| Stream (Domain) | `OP1` $\rho_{\text{S1}}$ (approx) | `OP1` $p$ `(IID / BLK16 / WHT)` | `OP2` $\beta_1^{\text{HVG}}$ | `OP2` $\Phi_{\text{asym}}$ (exact / approx) | `OP2` $\Phi_{\text{asym}}$ $p$ `(IID / BLK16 / WHT)` | `OP3` Inertia & Schur | `OP3` `H3a` Surr. Witness `(IID / BLK16 / WHT)` | `OP3` $\kappa_{\text{F3}}$ (approx) & $p$ |
|---|---:|---|---:|---|---|---|---:|---|
| `STREAM_A` (LIGO `GW150914`) | `3.2267` | `1/20` / `1` / `99/100` | `227` | `2699/2835` (`0.9520`) | **`1/100` / `3/100` / `3/100`** | `(2,1,0)`, `True` | `10 / 99 / 99` | `0.1959` (`1 / 1 / 1`) |
| `STREAM_B` (USGS `BOU` G5 Storm) | `3.6363` | `1/50` / `1` / `99/100` | `217` | `65/69` (`0.9420`) | **`1/100` / `1/25` / `1/100`** | `(2,1,0)`, `True` | `4 / 99 / 99` | `0.2447` (`1 / 1 / 1`) |
| `STREAM_C` (NOAA `9414290` Tide) | `1.7759` | `1` / `1` / `1` | `154` | `167/323` (`0.5170`) | `23/50` / `19/20` / `9/25` | `(2,1,0)`, `True` | `6 / 99 / 99` | `0.1220` (`1 / 1 / 1`) |
| `STREAM_D` (USGS `01646500` River) | `3.8855` | `1/100` / `1` / `91/100` | `71` | `55/419` (`0.1313`) | `1` / `9/50` / `1` | `(2,1,0)`, `True` | `1 / 99 / 99` | `0.3307` (`1 / 1 / 99/100`) |

All 4 held-out streams produce explicit Farkas directed cycle witnesses on `OP2` (`[1, 3, 1]` for `STREAM_A` and `STREAM_B`; `[0, 6, 0]` involving the tie state `6` for `STREAM_C` and `STREAM_D`), and all 4 satisfy `forward_hvg_dag_grounded = True`.

### Table 4 — Calibration `Window A` (`[0:256]`, Descriptive Only)

| Stream | Unique Values (of 256) | Scaled Int Bit Range | `OP1` $\rho_{\text{S1}}$ (approx) | `OP2` $\beta_1^{\text{HVG}}$ | `OP2` $\Phi_{\text{asym}}$ (exact) | `OP3` Inertia & Witness |
|---|---:|---|---:|---:|---|---|
| `STREAM_A` | 256 | `70..72` bits | `2.8399` | `206` | `1` | `(2,1,0)`, `True` |
| `STREAM_B` | 256 | `25..25` bits | `11.1164` | `229` | `2021/2277` (`0.8876`) | `(2,1,0)`, `True` |
| `STREAM_C` | 222 | `8..11` bits | `1.9163` | `189` | `103/177` (`0.5819`) | `(2,1,0)`, `True` |
| `STREAM_D` | 26 | `19..20` bits | `3.4901` | `64` | `13/233` (`0.0558`) | `(2,1,0)`, `True` |

---

## 5. Mechanistic Scientific Conclusions (What Survived Real Nature vs. What Was Falsified)

1. **Matched Surrogates Prevent Severe False Positives (`H1_SEAM1_SHOCK`):** Testing only against IID shuffles would have falsely declared rank-1 leverage shocks significant in `3/4` natural domains (`STREAM_A`, `STREAM_B`, `STREAM_D`). Adding exact `BLOCK_16` and `WHT_PHASE` nulls cleanly exposed that smooth physical trajectories actually generate *smaller* local leverage spikes than stitched blocks or Walsh-phase-randomized spectra.
2. **Smooth Persistence Suppresses HVG Loops Below IID (`H2a_SEAM3_HVG_BETTI1`):** Physical continuity creates monotone segments whose visibility graphs are sparser than IID noise ($\beta_1 < 256$). Any future track testing HVG topology on continuous physical series should pre-register a lower-tail or two-sided test rather than an upper-tail excess over IID.
3. **Directed Ordinal Hodge-Curl $\Phi_{\text{asym}}$ Cleanly Separates Driven Non-Equilibrium Transients (`H2b_SEAM3_IRREV_PHI`):** Out of all four surrogate-tested statistics, $\Phi_{\text{asym}}$ is the sole relational invariant that survives all three matched nulls (`IID`, `BLOCK_16`, `WHT_PHASE`) on real nature — and its pass/fail split (`STREAM_A` LIGO merger + `STREAM_B` G5 geomagnetic storm PASS; `STREAM_C` semi-diurnal tide + `STREAM_D` quantized river discharge FAIL) maps directly onto physical non-equilibrium irreversibility vs. harmonic reversibility and sensor quantization!
4. **Lag-3 Companion Non-Normality Is Universal Across Persistent Nature — and Driven by Linear Persistence (`H3a` vs. `H3b`):** While `H3a_F3_TRANSIENT_WITNESS` is strictly `4/4` on real streams vs `1–10/99` on `IID_PERM`, `99/99` of `BLOCK_16` and `WHT_PHASE` surrogates share $\operatorname{In}(I_3 - T^\top T) = (2, 1, 0)$ because lag-1 autocorrelation $a_1 \approx 1$ in a delay companion matrix forces $\|T e_1\|_2^2 \ge 1 + a_1^2 > 1$. Conversely, raw commutator normalization $\kappa_{\text{F3}}$ (`H3b`) is maximized by the IID nilpotent shift (`0.500`), explaining its clean `0/4` falsification.

---

## 6. Verification Receipts

- **Frozen Canonical Certificate (`physical_telemetry_certificate.json`):**
  - `file_sha256`: `fe55c61820db1a05d52c40a3a91f5e526103cb31a9bd2cf256fb031126dbf289`
  - `payload_sha256`: `418bb7392f1a17c73a926816f8acafecd74e5cdd2e186f492664855b409b3bf5`
  - `certificate_sha256`: `1bca18ef58817936f79d1b07e6990d6e27c2914e4e4f18a060c2103665892be6`
- **4-Mode Isolated `-I` Parity (`-I -B`, `-I -O -B`, `-I -B -W error`, `PYTHONHASHSEED=42 -I -B`):**
  - `physical_telemetry_audit.py --generate --out <tmp>` x4: bit-identical `fe55c61820db1a05d52c40a3a91f5e526103cb31a9bd2cf256fb031126dbf289`.
  - `physical_telemetry_audit.py --check physical_telemetry_certificate.json` (default full `99 x 3` surrogate + 6-control replay) and `--observed-only` x4: bit-identical `valid: true`.
  - `test_physical_telemetry_r5.py` x4: `15/15 OK` (zero bare `assert`s; independent zero-shared-code brute-force HVG, SEAM-1, and VAR(1) cross-checks).
- **Live Mutation & AST `BoolOp` Testing:**
  - `aletheia v2.0.0 mutate --max-mutants 0 --work-root . --add-cwd` (`-s -O -B -W error`): `physical_telemetry_oracle.py` **`123/123`** + `physical_telemetry_audit.py` **`7/7`** = **`130/130` (`100.0%`, `survived=0`, `truncated=False`) KILLED**.
  - Exhaustive AST `BoolOp` (`and` <-> `or`) sweep: `physical_telemetry_oracle.py` **`18/18`** + `physical_telemetry_audit.py` **`1/1`** = **`19/19` (`100.0%`, `survived=[]`) KILLED**.
- **Reusable 16-Vector Zone-B Adversarial Fuzzer (`zone_b_fuzzer.py`):**
  - CLI surface (`physical_telemetry_audit.py --check`, default full-replay): **`23/23` `REJECTED_CLEAN`** (`baseline_ok=true`, `bypasses=0`, `crashes=0`, `PASS`).
  - In-memory validator surface (`validate_certificate_payload`): **`18/18` `REJECTED_CLEAN`** (`bypasses=0`, `crashes=0`).
  - Combined: **`41/41` (`100.0%`) `REJECTED_CLEAN`**, plus full public-API Zone-B hardening across all vector/matrix/path/decimal/surrogate/CLI entry points.
- **Static & Hygiene Gate (`aletheia v2.0.0 audit-check . --strict-ancestors --safety-scan --scripts physical_telemetry_audit.py test_physical_telemetry_r5.py`):**
  - `PASS` (`11` files scanned, `3` `.py`, `6` `.json`, `2/2` R4 3-mode parity, `0` bare asserts, `0` AST float literals/`float()` calls on oracle & audit CLI, `0` CRLF, `0` `__pycache__`, `0` path leaks, `0` ancestor permission findings, `0` safety findings).
