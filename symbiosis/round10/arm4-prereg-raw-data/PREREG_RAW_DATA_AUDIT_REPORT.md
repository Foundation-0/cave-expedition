# AUDIT-087: Pure-Q Pre-Registration Statistical-Power, Net-Invariance, & Knowledge-Factory Cross-Audit (`cave-expedition#6` & `aletheia#6`)

> **Audit ID:** `AUDIT-087` (Wave 2 — Round 10, Arm R10-4)  
> **Scope (Strictly Read-Only, `0` GitHub writes, `0` real telemetry fetched):**
> - `Foundation-0/cave-expedition` PR `#6` (`outside/continuum-four-transformations-prereg @ 24d7757309b5b6b7b5179be2a65387af58fd5f9b`: `PREREG.md`, `DATA_REQUEST.md`, `ARM_B_OUTLINE.md`, `README.md`) testing `Foundation-0/continuum` PR `#1` (`continuum.md @ 8d3e7345`, Line 16)
> - `Foundation-0/aletheia` PR `#6` (`feat/nichochar-knowledge-factories-capture @ 98db54c39812546e9acb8e7f9f2b39fffd46e487`: `post.md`, `analysis.md`) cross-audited against verified `AUDIT-076R` (`symbiosis/round8/arm5-langchain-knowledge-factory/`, `KF-01..KF-05`)
> **Artifacts:** [prereg_raw_data_certifier.py](prereg_raw_data_certifier.py) · [test_prereg_raw_data_r5.py](test_prereg_raw_data_r5.py) · [prereg_raw_data_certificate.json](prereg_raw_data_certificate.json)  
> **Novelty Classification (Law 4):** **`N1`** (pre-data pure-$\mathbb{Q}$ statistical-power, symmetry-obstruction, and net-invariance audit + fail-closed protocol/knowledge-factory certifiers; all foundational ordinal-pattern, IAAFT, Holm, and knowledge-factory methods quarantined strictly under `N0` below).

---

## 1. Law-2 Steelman Credit (Verified Strengths of Both Outside PRs)

Applying Aletheia Laws 1–5 honestly without defensiveness, both PRs demonstrate high methodological discipline and independently verify several exact mathematical claims:

1. **`Foundation-0/cave-expedition#6` (`orda-aska` @ `24d77573`):**
   - **Pre-data discipline:** Zero telemetry downloaded (`0` bytes fetched); fit/verdict temporal splits pinned before opening data; SHA-256 hash pinning (`DATA_REQUEST.md:58`); deterministic SHA-256 seed derivation (`PREREG.md:231`); zero-shared-code recount requirement (`PREREG.md:233`); and fair non-falsification treatment of `T2`, `T4`, and `T1`-interference (`PREREG.md:99-123`).
   - **Verified exact combinatorics, byte sums, and Holm math:**
     - `DATA_REQUEST.md` byte accounting verifies **`4/4` identically**: `WAVES fit = 64,800,982 B`, `WAVES verdict = 69,121,441 B`, `total = 634,994,866 B`, `drop L1 fit = 509,128,939 B`.
     - Burnside's Lemma on $V_4 = \{I, R, P, R \circ P\}$ acting on $S_4$ ($|S_4| = 24$) verifies **`(24 + 0 + 0 + 8) / 4 = 8` orbits** (`4` orbits of size `2`, `4` orbits of size `4`), confirming `PREREG.md:105`.
     - Laplace smoothing `(n(pi) + 1/2) / (sum n + 3)` (`PREREG.md:65`) sums identically to `1` over `3! = 6` patterns, and the `d = 3` time-reversal/polarity-flip actions (`PREREG.md:68, 84-89`) are algebraically exact.
     - Holm minimum threshold `1/560` (`0.001785...`), `0.05^12`, `0.05^32`, and exact presence counts **`K >= 5` of `12`** (`p = 0.000183... <= 1/560` vs `K = 4`: `0.002236... > 1/560`) and **`K >= 7` of `32`** (`p = 0.000868... <= 1/560` vs `K = 6`: `0.004599... > 1/560`) in `PREREG.md:184, 188` are **100% verified**.
     - Berger's intersection-union principle (`p_inst = max_net p_net`, `PREREG.md:140`) adds **zero** Type-I error inflation.
2. **`Foundation-0/aletheia#6` (`orda-aska` / `qalam` @ `98db54c3`):**
   - High-fidelity verbatim X API capture (`post.md`) preserving `note_tweet`, HTML-escape notes, media keys, and full reply context.
   - Honest org-wide architectural synthesis (`analysis.md`) crediting existing `ingestion`, `corpus`, `orda-aska`/`ahrazzle` PR sign-off, `siliconcordat` Plane-1 firewall, `exo` SIM retire, `Synbios`, and `ABIOS`, while surfacing **two genuine requirements absent from `AUDIT-076R`'s base blog analysis**: (1) **Charriere's gardener-only write policy** (`post.md:248-253`, butlers express typed intent, never write directly) and (2) **Daniel Lenton's in-flight stale-skill read hazard** (`post.md:242`, `KF-03d`).

---

## 2. Pinned Read-Only Portal & Reference Inventory (`10` Files, `18` Anchors)

All `10` files (`cave-expedition#6`, `aletheia#6`, `continuum#1`, and `AUDIT-076R` certificate) and `18` verbatim `file:line` anchors are live-verified read-only by `audit_live_portals()` in [prereg_raw_data_certifier.py](prereg_raw_data_certifier.py):

| Relative Path (under `symbiosis/`) | Bytes | Exact SHA-256 |
|---|---:|---|
| `round10/portals/cave-expedition/pr_6.md` | `2,245` | `76b2266f81b15a479324a0fa240d73e9866fa842e90a31df9c6c4c7ef5592b5b` |
| `round10/portals/cave-expedition/pr_6_files/.../PREREG.md` | `25,192` | `8ed03fb9f3f5b712d961b04ebdc2f539c398cac6e5e1fbecb6eeacb6041b5483` |
| `round10/portals/cave-expedition/pr_6_files/.../DATA_REQUEST.md` | `5,814` | `0ebf6b137ce13d644b06a4f947d10bdc59947ca369393b471369d0569064a314` |
| `round10/portals/cave-expedition/pr_6_files/.../ARM_B_OUTLINE.md` | `2,476` | `893b7744d6503e2857ac1d9eca97c1a63cb2bab6386d2e90b73071eac4896de1` |
| `round10/portals/cave-expedition/pr_6_files/.../README.md` | `844` | `c7918d85041e4d6c1ceac552cc2f64839971cd1e28608f1b3abd276ce6cb1644` |
| `round10/portals/aletheia/pr_6.md` | `2,048` | `088f40fd8e8e5b0e404dff43295b2b38542edb2ef8651088b287e0358f74269b` |
| `round10/portals/aletheia/pr_6_files/.../post.md` | `22,609` | `d433ac2988fefd9fb3434dfaa5c9fa4257830b3dd71ff3258a0e1068d3dd900b` |
| `round10/portals/aletheia/pr_6_files/.../analysis.md` | `13,707` | `53edaf8612a959a16d0d86401f2fe55f65680c484e8de648ee86759cbee0473c` |
| `round10/portals/continuum/pr_1_files/continuum.md` | `10,121` | `516f6080563f223a4d8da437d37aaff479988f08f9079bfa48116cbb4fdc3150` |
| `round8/arm5-langchain-knowledge-factory/knowledge_factory_certificate.json` | `11,975` | `7f84e852283d072902207ba106f70b3384d00b2fd4041ff12cc21be25e08974b` |

---

## 3. Pillar 1 — Pre-Data Statistical-Power Traps in `PREREG.md` (`PREREG-01a`, `PREREG-01b`)

### 3.1 `PREREG-01a` [HIGH] — `C2/C3/C4` Conjunction Override (`PREREG.md:150, 156`)
- **Verbatim rule (`PREREG.md:150`):** `K below the binomial 1 percent excess point (K < 4 when S = 12, K < 6 when S = 32) and K/S at most 0.10`.
- **Exact Pure-$\mathbb{Q}$ Defect:** Under the conjunction **`and K/S <= 1/10`**, the rate cap strictly overrides the quoted `1%` binomial bound at both `S = 12` (`K <= 1`, failing at `K >= 2`) and `S = 32` (`K <= 3`, failing at `K >= 4`), rendering `K < 4` and `K < 6` dead code! Under a **100% perfectly calibrated null** ($p_0 = 1/20$):

| Segment Count `S` | `1%` Binomial Rule Fail (`K >=`) | Exact `1%` Tail | Conjunction `K/S <= 0.10` Fail (`K >=`) | Exact Conjunction Fail Prob | Inflation Factor | Per-Instrument (`C2,C3,C4`) False-Invalid | `3` Instruments (`>=1` Invalid) | `4` Instruments (`>=1` Invalid) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **`12`** | `4` | `0.002236` | **`2`** | **`0.118359`** | **`52.92x`** | **`31.4710%`** | **`67.8173%`** | **`77.9455%`** |
| **`32`** | `6` | `0.004599` | **`4`** | **`0.073805`** | **`16.05x`** | **`20.5476%`** | **`49.8443%`** | **`60.1501%`** |

Because `PREREG.md:156` marks an instrument `"invalid"` if ANY of `C2`, `C3`, or `C4` fails, and `TESS` is already excluded from the `>= 3` quorum (`L238`), **a perfectly calibrated experiment at `S = 32` has a `49.84%` coin-flip probability of falsely invalidating at least one of its `3` required instruments before testing real data!**
- **Pre-Data Amendment:** Use the exact binomial `1%` bound alone (`control_combine_mode = "binom_only"` — or `"or"` so `K/S <= 0.10` only activates for large `S`), cutting per-instrument false invalidation at `S = 32` from **`20.55%`** down to **`1.37%`**.

### 3.2 `PREREG-01b` [MED] — `K2` Quantile Off-by-One & 21-Class Multiplicity (`PREREG.md:210-211`)
- **Verbatim rule (`PREREG.md:211`):** `The per-segment rejection rate at 0.05 must be at most 0.086 (the 99 percent binomial bound for 200 draws).`
- **Exact Pure-$\mathbb{Q}$ Check:** `0.086 * 200 = 17.2` sets pass `K <= 17` (fail `K >= 18`), whose exact tail is $P(\operatorname{Bin}(200, 1/20) \ge 18) = \mathbf{0.012089... > 0.01}$ (exceeds `1%`!). The true `<= 1%` threshold is `K <= 18` (`0.090`, fail `K >= 19` with exact tail **`0.005823... <= 0.01`**). Across `7 * 3 = 21` noise classes (`PREREG.md:210`), `K >= 18` yields a **`22.5413%`** family-wise chance of falsely flagging a valid Gaussian/monotone-Gaussian class!

---

## 4. Pillar 2 — Exact $R \circ P$ Symmetry Obstruction (`PREREG-02`) & Monotone Offset Leakage (`PREREG-03`)

### 4.1 `PREREG-02` [CRITICAL] — Exact $R \circ P$ Cancellation of $u = a_2 - a_3$ & Time-Even Dilution of `K4` `A -> C` (`PREREG.md:84-89, 214-220`)
- Under $d = 3$ ordinal log-ratios $(a_1, s = a_2 + a_3, u = a_2 - a_3)$:
  - Polarity flip $P$: $(a_1, s, u) \mapsto (-a_1, -s, +u)$
  - Time reversal $R$: $(a_1, s, u) \mapsto (-a_1, -s, -u)$
  - **180° graph rotation $R \circ P$:** $(a_1, s, u) \mapsto (+a_1, +s, -u)$.
- **Exact Symmetry Obstruction Theorem:** Every polarity-invariant, time-odd function of $d = 3$ ordinal counts vanishes identically on the $u = 0$ hyperplane (`n(021)/n(120) = n(102)/n(201)`). Because a sawtooth (and any clean jump-decay pulse train) is **invariant under 180° rotation $R \circ P$**, [prereg_raw_data_certifier.py](prereg_raw_data_certifier.py) verifies on a 256-sample period-16 sawtooth that **`n(021) == n(102)` and `n(120) == n(201) == 0` at EVERY lag $\tau \in \{1, 2, 4, 8\}$**, forcing **`u = a_2 - a_3 = 0` IDENTICALLY** (with `240/240` windows tied at $\tau = 8$)!
- **Impact on `T3` Transfer & `K4` `A -> C` (`PREREG.md:85-86, 219-220`):** **`2/3` (`20/30`) of the `T3` transfer features** (`m1 = |a1|`, `m23 = |a2 + a3|`) are **TIME-EVEN** (`|(-a)| == |a|`)! Under time reversal (`A -> C`), `m1` and `m23` still align **positively** (`cos = +1`) with `w_A`, directly fighting the `10` `u`-features expected to drive `A -> C` below the `2.5th` percentile!
- **Pre-Data Amendment:** Split `T3` transfer into **(i) Polarity-Free Time-Arrow Transfer** (`u` only, `10` features — cleanly reverses sign under `A -> C`) and **(ii) Time-Even Magnitude-Profile Transfer** (`m1, m23`, `20` features — reported separately without an anti-correlation requirement under `A -> C`).

### 4.2 `PREREG-03` [HIGH] — End-Matching Offset Selection Leaks Under Monotone Amplitude Maps (`PREREG.md:134, 163`)
- `PREREG.md:134` skips running the amplitude-map net statistically because ordinal patterns are exact invariants of strictly increasing maps (`K1`), yet `PREREG.md:163` chooses the segment start offset `o in 0..128` using raw Euclidean squared end-jumps `(x[-1] - x[0])^2 + ((x[1]-x[0]) - (x[-1]-x[-2]))^2`.
- **Exact Pure-$\mathbb{Q}$ Counterexample:** On 8-sample integer block `[10, 10, 0, 1, 11, 11, 2, 2]` (`N = 6`, offsets `0, 1, 2`):
  - Raw costs = **`[1/1, 65/1, 5/1]`** $\implies$ picks **`offset = 0`**.
  - Under `K1`'s exact strictly increasing map $f(x) = x^3 + x$: mapped costs = **`[110224/1, 1103684/1, 104/1]`** $\implies$ picks **`offset = 2`** (extracting a different window and different ordinal counts!).
- **Exact Pre-Data Fix:** Apply `PREREG.md:163`'s end-matching objective to **exact mid-ranks** (`rank_transform_exact(block)`): `rank_costs_raw == rank_costs_mapped = [4/1, 17/4, 29/4]`, selecting the **unique strict minimum `offset = 0`** identically under EVERY strictly increasing map and polarity flip!

---

## 5. Pillar 3 — Structural Power Budgets, Zero-Margin Quorum, & `ARM_B` Rung Capacities (`PREREG-04`)

1. **Zero-Margin `3/3` Support Quorum (`PREREG.md:138, 238, 242`):** Pre-excluding `TESS` (no second channel) leaves `3` calibrated instruments (`GW, SEIS, WAVES`) to satisfy `>= 3` — zero margin for even one underpowered net or control glitch.
2. **Exact Scale-Flow Sample Budgets (`PREREG.md:104-107`, block length `4,224`, min `12` blocks -> `B(l) = 50,688 * 2^l`):**

| Instrument Case | Samples | `l=0` Blocks | Max Level `l_max` | Populated of `7` Levels | Min Zero-Padded `T1` Features (of `56`) |
|---|---:|---:|---:|---:|---:|
| `GW` (`4,096s @ 4,096 Hz`) | `16,777,216` | `3,971` | `8` | `7/7` | `0` |
| `SEIS VBB` (`1 day @ 20 Hz`) | `1,728,003` | `409` | `5` | `6/7` | `8` |
| `TESS` (`27d @ 20s`, no-gap upper bound) | `116,640` | `27` | **`1`** | **`2/7`** | **`40/56` (`71.43%`)** |
| `WAVES` (`8d * 4ch @ 60s` cadence) | `46,080` | **`10 < 12`** | **`-1` (UNDERPOWERED)** | **`0/7`** | **`56/56`** |
| `WAVES` (`8d * 4ch @ 192s` cadence) | `14,400` | **`3 < 12`** | **`-1` (UNDERPOWERED)** | **`0/7`** | **`56/56`** |

   - Exact maximum average cadence for 4 pooled `Wind/WAVES` channels over 8 days (`691,200 s`) to reach `12` blocks at `l = 0` is **`600/11 s` (`54.545454 s`)**.
3. **Zero-Padded Support Dilution & `S_4/V_4` Linear Dependence (`PREREG.md:91-94, 105-107`):** Permuting `w_A` across zero-padded aligned levels mixes active weights into empty levels, and the `8` `S_4/V_4` orbit frequencies have only `7` independent degrees of freedom (`sum == 1`). **Fix:** restrict permutations strictly to the jointly populated aligned support $\mathcal{L}_A \cap \mathcal{L}_B$ and stratify by feature class.
4. **`ARM_B_OUTLINE.md:14` Finite-Sample Rung Limits:** Requiring `50 * d!` windows/pattern gives `300` (`d=3`), `1,200` (`d=4`), **`6,000` (`d=5` > single `4,096`-sample segment!)**, and **`36,000` (`d=6`)** — and fitting a `d = 6` Markov transition matrix (`720 * 6 = 4,320` outgoing transitions) needs **`216,000 > 131,072` (`32 * 4,096`)** windows!

---

## 6. Pillar 4 — Cross-Audit of `Foundation-0/aletheia#6` vs. `AUDIT-076R` (`KF-01..KF-05`) & Fail-Closed Certifiers

| Trust Dimension | `aletheia#6` (`post.md` + `qalam` `analysis.md`) | `AUDIT-076R` (`KF-01..KF-05`) | Synthesis Verdict |
|---|---|---|---|
| **Role & Write Boundary (`KF-00`, `KF-05`)** | **STRENGTH:** Charriere gardener-only write policy (`post.md:248-253`); `orda-aska` drafts -> `ahrazzle` reviews (`analysis.md:29, 47`). **GAP:** `pr_6` targets stub `main` without CLI/R4/R5 receipts (`pr_6.md:16`). | 3-role `Worker != Curator != Verifier` + Tao R4/R5 process gate + SHA-256 hash-chained ledger. | Adopt Charriere's **gardener-only write-intent packet** into `KF-05` + require R4/R5 process receipts on gardener PRs. |
| **Integrity & Confidentiality (`KF-01`)** | **GAP:** `analysis.md:47, 55` feeds raw traces + flags into gardener draft PRs with no Biba/BLP lattice (`analysis.md:87` addresses copyright only for captures, not trace-to-skill promotion). | Exact Biba × BLP lattice blocking external prompt injection (`blast_prob = 1 - (19/20)^120 = 0.997877...` truncated, `99.7878%` rounded) & private-DM leaks. | **Mandatory tightening:** bind Biba/BLP checks to gardener trace ingestion BEFORE draft PR generation. |
| **Goodhart Drift (`KF-02`)** | **GAP:** `analysis.md:81` relies on subjective curator quality / `deferred`/`rejected` statuses. | Frozen orthogonal outside-anchor latch (`+105.31%` true error explosion under `68.36%` proxy drop halted at step 1). | **Mandatory tightening:** attach frozen outside-anchor suite to every gardener cadence cycle. |
| **Concurrency & Stale Reads (`KF-03`)** | **GENUINE ADDITION (`KF-03d`):** Daniel Lenton's in-flight stale-skill read hazard (`post.md:242`, `analysis.md:37, 85`) was NOT modeled in `AUDIT-076R`. **GAP:** misses LWW oscillation, CAS split-brain, and skill cycles. | LWW batch conflict halt, CAS revision check, 3-color DFS skill-cycle detector (`KF-03a..c`). | **Unified `KF-03a..d`:** add `butler_loaded_epoch < store_epoch => require in_flight_nudge_sent` to `AUDIT-076R`'s governor! |
| **Auto-Merge Confused Deputy (`KF-04`)** | **CRITICAL LOOPHOLE (`analysis.md:33, 61`, `post.md:314`):** Endorses human sign-off for *skills* while allowing *"other forms of memory"* to auto-merge — leaving **Data Access Guidance** (query endpoints/tables) & **Domain Knowledge** (metric rules) auto-mergeable! | Monotone capability/endpoint/cron attenuation + Ring-0 immutability across skills AND data-access guidance. | **Mandatory fix:** require human sign-off on `skill`, `data_access_guidance`, AND `domain_knowledge`; allow auto-merge **ONLY** on `ephemeral_memory`! |

Both executable fail-closed certifiers (`certify_prereg_protocol` — enforcing non-vacuous thresholds `2*(eff_fail_k-1) < S` and `4*k2_max_rejects < k2_seeds`, experiment-wide false-invalidation & `K2` FWER ceilings `<= 1/10`, and minimum Holm presence power `alpha^S <= 1/560` — and `certify_knowledge_factory_promotion` — enforcing per-layer Biba integrity floors `LAYER_MIN_INTEGRITY` and BLP confidentiality ceilings `LAYER_MAX_CONFIDENTIALITY` so callers cannot spoof weaker layer bounds) in [prereg_raw_data_certifier.py](prereg_raw_data_certifier.py) certify the exact before/after state: `PREREG.md` as written triggers `7` concrete violations (all `0` after the pre-data amendments with `k2_max_rejects = 20`, giving `21`-class FWER `2.4077% < 10%` and `4`-instrument false invalidation `5.3821% < 10%`), and `aletheia#6`'s `data_access_guidance` auto-merge + unnotified stale-epoch scenario triggers both `KF03D_INFLIGHT_STALE_READ_UNNOTIFIED` and `KF04_HIGH_IMPACT_LAYER_REQUIRES_SIGNOFF`.

---

## 7. Law-4 `N0` Prior-Art Quarantine & Honest `N1` Attribution

Aligned verbatim with `../cartography/ROUND10_PORTALS.md`:
- **`N0` (Quarantined Prior Art — NOT claimed as new):**
  - `R10-N0-09`: Bandt–Pompe (2002) ordinal patterns & permutation irreversibility, Schreiber–Schmitz (1996) IAAFT surrogates, Berger (1982) intersection-union test, and Holm–Bonferroni FWER control.
  - `R10-N0-11`: Nicholas Charriere (`@nichochar`) & Harrison Chase (LangChain, Nov 2026) Knowledge Factory / Gardener-Butler essays and replies (`aletheia#6`), plus `AUDIT-076R` (`KF-01..KF-05`).
  - `cave-expedition#6` (`PREREG.md`, `DATA_REQUEST.md`, `ARM_B_OUTLINE.md`) and `continuum#1` (`continuum.md`) verbatim source texts and pinned digests.
- **`N1` (Honest Engineering & Verification Contribution of `AUDIT-087`):**
  1. Pure-$\mathbb{Q}$ pre-data audit of `cave-expedition#6` catching `PREREG-01a/b` (`C2/C3/C4` `16.05x–52.92x` false-invalidation override & `K2` quantile off-by-one), `PREREG-02` ($R \circ P$ symmetry obstruction forcing $u \equiv 0$ + `2/3` time-even dilution of `K4` `A -> C`), `PREREG-03` (monotone-map end-matching offset leakage + rank-transform fix), and `PREREG-04` (zero-margin quorum, `TESS`/`WAVES` scale-flow starvation, `ARM_B` transition capacity).
  2. Bidirectional cross-audit of `aletheia#6` vs `AUDIT-076R` incorporating Charriere's write policy + Lenton's `KF-03d` in-flight epoch-nudge while closing `analysis.md:33,61`'s `KF-04` Data-Access/Domain-Knowledge auto-merge loophole.
  3. Two fail-closed pure-$\mathbb{Q}$ certifiers (`certify_prereg_protocol`, `certify_knowledge_factory_promotion`) verified to `100.0%` R5 mutation kill.

---

## 8. Reproducibility & Verification Receipts (Aletheia v1.4.0)

- **Live-anchored certificate:** [prereg_raw_data_certificate.json](prereg_raw_data_certificate.json) (`certificate_sha256: 8afb84e301efb95c338bed6cb6eab640211832ead320044c260d6ce71eee47a6`, `10/10` portal files & `18/18` verbatim anchors verified, `0` floats).
- **Standalone pure-$\mathbb{Q}$ certificate:** `certificate_sha256: 1ba1d540a2b627d9079899e2b0458e47bbfab1293c44ea26e13edadf7354b66d`.
- **Aletheia v1.4.0 Audit Gate:** `aletheia audit-check . --strict-ancestors --scripts prereg_raw_data_certifier.py test_prereg_raw_data_r5.py` `PASS` (`4` files, `0` defects, `8/8` ancestor dirs clean, `0` bare `assert`s, `0` floats, `0` personal-path or `file:///` leaks, `0` CRLF, `0` `__pycache__`).
- **R4 Determinism:** `4/4` isolated `python3 -I -O -B -W error` runs bit-identical (`live --json`, `standalone --json`, human summary, `test_prereg_raw_data_r5.py`).
- **R5 Mutation Gate:** `aletheia v1.4.0 mutate prereg_raw_data_certifier.py --work-root . --add-cwd --max-mutants 0 --test-cmd "python3 -I -O -B -W error test_prereg_raw_data_r5.py"` **`108/108` (`100.0%`) KILLED, `0` survivors**.
