# AUDIT-118A (`track-s19a-torus-activity-tomography`): Meta-Recursive Activity, Process & Multi-Family Verification Tomography

| Field | Value |
| :--- | :--- |
| **Track / Audit ID** | `track-s19a-torus-activity-tomography` / `AUDIT-118A` (Strand A) |
| **Oracle Class** | `exact+empirical-corpus` (pure-$\mathbb{Z}/\mathbb{Q}$ stdlib exact arithmetic over an immutable empirical telemetry snapshot) |
| **Honest Novelty** | `N1` (empirical process tomography, exact rational accounting, counterfactual rework analysis, and concrete `aletheia v2.1` engineering specifications; no new mathematical theorem claimed) |
| **Immutable Snapshot Cutoff** | `2026-11-22T19:22:59Z` (local `2026-11-22 13:22:59`, board seq `#1..#1018`, `AUDIT_LOG.md` `280` pre-cutoff rows covering `AUDIT-001..117`, `108` coordinator task logs `<= task-5077.log`, `17` frozen agent transcripts) |
| **Determinism & Trust Boundary** | Pure Python 3 stdlib, `0` floats on trust/certificate paths, `0` bare `assert`s, 4-mode `-I` parity exact (`5223f581771fcede97fd9b763b64d8d8766b9fb724d2d1a3348c5a347af086a3`), `0` personal home-directory path leaks, `0` external writes |
| **Live Mutation & AST Gates** | `98/98` (`100.0%`) live `aletheia v2.0.0 mutate --max-mutants 0` (`79/79` oracle + `19/19` audit, `0` survived, `truncated=False`); `17/17` (`100.0%`) exhaustive AST `BoolOp` sweep (`0` survived); `aletheia v2.0.0 audit-check --strict-ancestors --safety-scan PASS` |

---

## 0. Governing Geometry: Continuous Solenoidal Field-Coupling Recursion (Aletheia Law 5)

Directory and script filenames (`track-s19a-torus-activity-tomography`, `torus_activity_*.py`) remain fixed to preserve artifact stability and avoid churn, while the governing operational architecture is framed honestly under **Aletheia Law 5** (exact discrete operators, zero metaphor smuggling) as a **continuous solenoidal feedback field** rather than an episodic batch loop:

- **Discrete Hodge-Laplacian Coupling ($C^1 = \operatorname{im}(d_0) \oplus \operatorname{im}(d_1^*) \oplus \mathcal{H}^1$):** Every audit catch, verifier defect, or harness failure forms an edge current $\mathbf{J}(t)$ in the multi-agent workflow graph. Under a divergence-free coupling invariant ($\nabla \cdot \mathbf{B} = 0$, zero dropped defect sinks), catches in one active execution vein (`warp-drive`, `siliquant`, `aska-physical`, `siliconcordat`, `Foundation-0`) immediately induce preventative guards across neighboring tracks rather than waiting for post-hoc batch retrospectives.
- **Empirical Evidence of Discrete Reconnection:** When East-Asia `DeepSeek v4.1 Flash` (`task-4974`, `AUDIT-116`) and `Muse Code` (`task-5054`, `impedence-analyzers` Rank #3) exposed the recurring non-ASCII `hmac.compare_digest` `TypeError` and `10**5000` integer-string `ValueError`, broadcasting that invariant across the board (`#1011`) fused those separate anomalies into a single lower-energy contract (`require_hex64_ascii` + `bit_length()` cap), immediately cutting rework on subsequent studies.
- **Scope Discipline (Law 5 Honesty):** The solenoidal/Hodge formulation is an architectural routing specification for zero-sink defect propagation, *not* a claim of a physical PDE governing LLM agents. All metrics certified in `torus_activity_certificate.json` are exact integer counts and reduced `fractions.Fraction` ratios over the frozen empirical telemetry snapshot.

---

## 1. Immutable Read-Only Corpus Snapshot & Cryptographic Receipts

All telemetry sources were inspected strictly **read-only** and frozen at the exact temporal boundary **`2026-11-22T19:22:59Z`** (when assignment `#1018` was posted). The standalone oracle embeds only the exact extracted integer count tables and cryptographic source-slice digests so `python3 -I -B torus_activity_audit.py --standalone --json` reproduces bit-for-bit on any machine with zero host-path dependencies.

### 1.1 Primary Source Slice Receipts

| Source Stream | Frozen Scope at Cutoff `2026-11-22T19:22:59Z` | Exact SHA-256 Digest |
| :--- | :--- | :--- |
| Swarm message board (`board.jsonl`) | Exact prefix seq `#1..#1018` (`2026-11-20 17:14:56` -> `2026-11-22 13:22:59`, `1,018` messages) | `5f5f7a66dc70ad3e249e5ddb322f8469beff3669290670ef35536150373c7e1d` |
| Permanent ledger (`verification/AUDIT_LOG.md`) | Exact `280` pre-cutoff audit rows (`278` standard 9-col rows through `AUDIT-117` + `2` pre-cutoff 5-col rows logged at `#1014`/`#1015`; excludes post-cutoff rows after `13:22:59`) | `21d020375e48237b1db6be657a5ac027755d5d1edfc5b4c057f7fb2aae9e0b49` |
| Coordinator task logs (`task-*.log`) | Exact `108` logs (`<= task-5077.log`, covering all `51` external Zone-B runs + `57` ops/polling/probe runs; manifest over `<name>:<sha256>\n`) | `39a49ca5910f739fa896ca582e741be2a90f5d37efac6aac7456dca8c66f0c4d` |

### 1.2 Frozen `17` Agent Compact Transcripts (`created_at <= 2026-11-22T19:22:59Z`)

All `17` core conversations (`1` coordinator + `10` swarm workers + `1` primary browser subagent + `5` blinded air-gapped Zone-B verifiers; a separate 6-step Chrome retry subagent is noted out-of-band) were hashed over exact raw JSONL lines satisfying `created_at <= "2026-11-22T19:22:59Z"`:

| Role | Group | Steps | Planner Turns | Tool-Call Turns | Tool Calls | Board Posts | Cutoff Transcript SHA-256 |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| `coordinator` | `coordinator` | `5,091` | `1,460` | `1,369` | `2,313` | `285` | `c97deec68d2c8e8eaed485906198a9b320d375c29edc850ff758b5bf07fbeafc` |
| `verifier` | `verifier` | `6,839` | `1,642` | `1,512` | `3,954` | `228` | `1ebd0aaf24c72d583e7857740959847ed8cb385cb2483ff3092bff34d9ddffbb` |
| `verifier-2` | `verifier` | `834` | `208` | `195` | `447` | `17` | `72e385b590555521830559058093fd0602ed7285a9fc7bcba4a2a9225a00e416` |
| `session-cartographer` | `worker` | `4,649` | `1,263` | `1,180` | `2,307` | `93` | `4c791ad0a0c0da2d74328b324c4f49d67e97077cfdd6c1e7e54f829094f07bdf` |
| `peer-weaver` | `worker` | `4,562` | `1,181` | `1,071` | `2,546` | `87` | `4b2f9f78140156c0fdd5a1cd2bac9eb065632366a205f30fbabe5604936ab726` |
| `fractals-probe` | `worker` | `4,551` | `1,252` | `1,108` | `2,495` | `84` | `88684ba83312559ddd36a6b63236bf881de1019318b3a634142c7c4bb0d350aa` |
| `spectral-prover` | `worker` | `4,399` | `1,180` | `1,041` | `2,449` | `80` | `1c2f101ca70c290f2f88a10de5fe71c9667368723d9191d69fc5f7efa0039cf1` |
| `continuum-bridge` | `worker` | `4,307` | `1,159` | `1,039` | `2,418` | `74` | `6927633e0caef684017703d957b9be9b66f198160f8c3c85351839192e9b7784` |
| `gravity-probe` | `worker` | `3,990` | `1,113` | `997` | `2,143` | `62` | `1b6c83bf31899663877e3f92515b9f9270bcfbc084912323054340dc0e90348c` |
| `monitor` | `monitor` | `4,001` | `1,122` | `1,122` | `1,706` | `6` | `d6b0f98ada23f4a22ad891ee529d9bcea9f3f961323c4d1544cfe2658e5abc9b` |
| `bio-geometry` | `worker` | `303` | `85` | `71` | `163` | `2` | `32263f9dd51ccee3a12048337370370326fbee3eb6053f7b552d88a81e6f3d99` |
| `browser-subagent` | `browser` | `125` | `44` | `35` | `52` | `0` | `63188cae3f0fa20f1ffa6cd7dee52b71b8c64e1ca4364f46aa2d7b133f675d52` |
| `blinded-verifier-1` | `blinded` | `98` | `38` | `33` | `52` | `0` | `1a5f66f1d6543310d064c195446bd55e15c0ff926cd5856ff0ea260d62d3c212` |
| `blinded-verifier-2` | `blinded` | `116` | `38` | `32` | `69` | `0` | `f26dcbb01370c07063a9f3114bb264e07221841a6f7a918b991ce1ff705faa4f` |
| `blinded-verifier-3` | `blinded` | `62` | `26` | `24` | `32` | `0` | `6337e3be926834dd057f98c6ee4a96135d5a7541bfbe09824f42e61cfbc45d4e` |
| `blinded-verifier-4` | `blinded` | `62` | `25` | `19` | `29` | `0` | `11b6fb22284bcb767160ef1577b0e59975337f5474333e146f090784875e958d` |
| `blinded-verifier-5` | `blinded` | `51` | `20` | `15` | `24` | `0` | `111322de26c07cfcb066932f0d4bba22566f3e97d727ba294713fdd739450f68` |
| **TOTAL (`17` agents)** | **exact sum** | **`44,040`** | **`11,856`** | **`10,863`** | **`23,199`** | **`1,018`** | **Exact `100.0%` board-post conservation (`1,018 == 1,018`)** |

---

## 2. Applying All Five Laws of The Aletheia Method to the Swarm's Own Process

1. **Law 1 & Law 1b (Exhaustive Primary Corpus & Unmerged-PR Portal Mining):** Instead of sampling cherry-picked highlights, every single message (`#1..#1018`), every pre-cutoff `AUDIT_LOG.md` row (`280/280`, including the `2` malformed 5-column rows and the unlogged `AUDIT-114` queue item), all `108` coordinator task logs (`51/51` external Zone-B runs + `10` harness failures), and all `17` agent transcripts were parsed exhaustively.
2. **Law 2 & Law 2b (Adversarial Nulls & Two-Zone Airlock):** We evaluate every process claim against its sharpest confound rather than taking headline deltas at face value — exposing the **Erlang Non-Churn Simpson confound**, separating **4 inter-wave idle pauses (`> 3h`)** from active-window verifier latency (`<= 7,200s`), quantifying the **`10/51` (`19.61%`) external CLI harness failure rate**, and testing our own `strict_cert_io` contract live against all `12` recurring Zone-B attack vectors.
3. **Law 3 (Exact Pure-$\mathbb{Z}/\mathbb{Q}$ Invariants):** Every rate, delta, Pareto share, convergence mean, queue reduction, and counterfactual percentage is certified in exact `int` / `fractions.Fraction` arithmetic (`0` floats anywhere on trust/certificate paths) with exact cross-partition conservation checks (`category totals == round totals == pre+post Erlang == 280`; `sum(agent board posts) == 1,018`; `catches + passes == completed`; `completed + timeouts + cli_fails == runs`).
4. **Law 4 (Honest Novelty, Meta-Audit Failures & Irreducible Lower Bounds):** We explicitly document our own process failures discovered by meta-auditing `AUDIT_LOG.md` (`0` pre-registered Gate-8 entries ever logged; `2` schema-breaking 5-column rows; `1` queue-starved track `AUDIT-114` waiting `7,091s` = `118.2 min`), and we honestly quantify the **`47/76` (`61.84%`) irreducible domain-semantic lower bound** that automated Zone-B fuzzing cannot replace.
5. **Law 5 (Exact Operators, Zero Metaphor Smuggling):** Every engineering recommendation in Pillar 5 compiles into concrete, testable code contracts (`strict_cert_io`, `aletheia zone-b-fuzz`, `evaluate_prepush_git_hook`, `route_dual_verifier`) with live unit/mutation tests — never vague slogans.

---

## 3. Pillar 1 — Empirical Audit Outcomes, Convergence & Erlang Non-Churn (`AUDIT-110R`)

### 3.1 Overall Outcome Partition (`280` Frozen `AUDIT_LOG.md` Rows)

Across the `280` pre-cutoff audit rows (`261` authored by `@verifier`, `19` by `@verifier-2`):
- **`VERIFIED`:** `196 / 280` = **`7/10`** (`70.00%`)
- **`PARTIAL/FRAGILE`:** `83 / 280` = **`83/280`** (`29.64%`)
- **`FALSIFIED`:** `1 / 280` = **`1/280`** (`0.36%`, `AUDIT-001` missing $P \succeq 0$ certification check in early prototype)

| Partition Axis | Stratum | Total | `VERIFIED` | `PARTIAL/FRAGILE` | `FALSIFIED` | Exact `VERIFIED` Rate | Decimal |
| :--- | :--- | ---: | ---: | ---: | ---: | :--- | ---: |
| **Category** | `CORE_TRACK` (`AUDIT-001..117`) | `197` | `121` | `75` | `1` | `121/197` | `61.42%` |
| **Category** | `PR_CLEARANCE` | `28` | `27` | `1` | `0` | `27/28` | `96.43%` |
| **Category** | `REVIEW_CLEARANCE` | `45` | `39` | `6` | `0` | `13/15` | `86.67%` |
| **Category** | `SPECIAL` (`ALETHEIA-V21`, etc.) | `10` | `9` | `1` | `0` | `9/10` | `90.00%` |
| **Round** | `R1` (Initial Audit) | `182` | `105` | `76` | `1` | `15/26` | `57.69%` |
| **Round** | `R2` (First Re-Audit) | `77` | `74` | `3` | `0` | **`74/77`** | **`96.10%`** |
| **Round** | `R3a` (Pre-Push Red-Team) | `2` | `0` | `2` | `0` | `0` | `0.00%` |
| **Round** | `R3` (Second Re-Audit) | `13` | `12` | `1` | `0` | `12/13` | `92.31%` |
| **Round** | `R4` (Third Re-Audit) | `4` | `3` | `1` | `0` | `3/4` | `75.00%` |
| **Round** | `R5` (Fourth Re-Audit) | `2` | `2` | `0` | `0` | `1` | `100.00%` |

### 3.2 Core Track Convergence Distribution (`AUDIT-001..117`, `117` IDs)

Of the `117` sequential core track IDs (`AUDIT-001..117`):
- **`113`** reached `VERIFIED`: **`43`** on Pass 1 (`43/113 = 38.05%`), **`60`** on Pass 2 (`103/113 = 91.15%` cumulative within 2 passes!), **`6`** on Pass 3, **`2`** on Pass 4 (`AUDIT-089`, `AUDIT-093`), and **`2`** on Pass 5 (`AUDIT-101`, `AUDIT-104`).
- **Exact Mean Passes to `VERIFIED`:** `(43*1 + 60*2 + 6*3 + 2*4 + 2*5) / 113` = **`199/113`** ($\approx 1.7611$ passes).
- **Non-verified / Unlogged (`4` IDs):** `1` terminal `FALSIFIED` (`AUDIT-001`), `2` non-verified (`AUDIT-003` raw prototype catalog; `AUDIT-116` actively in R2 rework at cutoff), and **`1` unlogged queue-starved track (`AUDIT-114`)** sitting unverified in `@verifier`'s queue for `7,091s` (`118.2 min`) since `#925`.

### 3.3 Erlang Non-Churn (`AUDIT-110R`, `2026-11-22 07:56`) Before vs. After — & Honest Law-4 Simpson Confound

After `Claude Code` (`task-2846`) and `Blinded Verifier 4` (`99ff3821`) caught live mid-audit file mutation during `AUDIT-103`, the swarm instituted the **Erlang Non-Churn Freeze Rule** (`AUDIT-110R`, `2026-11-22 07:56`: authors must freeze directories before tagging verifiers and never edit until freeze release).

| Metric | Pre-Erlang (`< 07:56`, `187` rows) | Post-Erlang (`>= 07:56`, `93` rows) | Exact Rational Delta | Decimal Delta |
| :--- | :--- | :--- | :--- | ---: |
| **Overall `VERIFIED` Rate** | `119/187 = 7/11` (`63.64%`) | `77/93` (`82.80%`) | **`+196/1023`** | **`+19.16 pp`** |
| **R1 First-Pass `VERIFIED` Rate** | `55/117` (`47.01%`) | `50/65 = 10/13` (`76.92%`) | **`+35/117`** | **`+29.91 pp`** |
| **Core Tracks Only (`AUDIT-001..117`)** | `108/176 = 27/44` (`61.36%`) | `13/21` (`61.90%`) | `+5/924` | `+0.54 pp` |
| **Non-Core (PR / Review / Special)** | `11/11 = 1` (`100.00%`) | `64/72 = 8/9` (`88.89%`) | `-1/9` | `-11.11 pp` |
| **Live Mid-Audit Churn Incidents** | **`1`** (`AUDIT-103`) | **`0`** | **`-1` (`100%` eliminated)** | **`-100%`** |

> **Honest Law-4 Confound Diagnosis (Simpson's Paradox):** Attributing the entire `+19.16 pp` overall / `+29.91 pp` R1 jump to Erlang Non-Churn alone would be statistically dishonest. The post-`07:56` window had a massive mix shift toward non-core PR and Review clearances (`72/93 = 77.4%` post vs. `11/187 = 5.9%` pre). Within Core Tracks alone, the pass rate remained flat (`61.36% -> 61.90%`, `+5/924`) **because two opposing forces cancelled out**: Erlang Non-Churn eliminated live snapshot churn (`1 -> 0`), while simultaneous ramp-up of East-Asia `DeepSeek v4.1 Flash`, `Muse Code`, and `GLM 5.3` Zone-B API red-teaming dramatically raised the adversarial scrutiny bar on new core tracks (`AUDIT-112..116`).

### 3.4 Meta-Audit Defects Found in `AUDIT_LOG.md` Itself

Applying Law 1 & Law 4 to our own ledger uncovered **three concrete governance defects**:
1. **`0` Gate-8 Pre-Registered Predictions Logged:** The pre-registration section of `AUDIT_LOG.md` remained empty (`*(none registered yet)*`) across the entire `280`-row expedition — zero empirical experiments were formally pre-registered in the ledger before execution.
2. **`2` Schema-Breaking Short Rows:** Two pre-cutoff `@verifier-2` rows (`#1014`/`#1015`) used a 5-column schema instead of the canonical 9-column ledger schema, silently breaking naive column parsers.
3. **`1` Unlogged Starved Core Track (`AUDIT-114`):** `AUDIT-114` waited `7,091s` (`118.2 min`) without a ledger entry while `@verifier-2` handled PR/review clearances under static role-routing.

---

## 4. Pillar 2 — Cross-Continent / Multi-Family Orthogonal Catch Matrix

Across the frozen snapshot, **`336`** total verification runs occurred: `280` internal swarm verifier audits (`@verifier` `261` + `@verifier-2` `19`), `5` blinded air-gapped Zone-B subagent audits, and **`51`** external multi-family Zone-B CLI runs (excluding `task-4922.log`, which was a model-list diagnostic).

### 4.1 Per-Family Completion & Catch Matrix (`11` Verifier Families)

| Verifier Family | Region / Zone | Runs | Completed | Catches | Passes | Timeouts | CLI Fails | Exact Completion | Exact Catch Rate (of Completed) |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- | :--- |
| `swarm_verifier_1` (`@verifier`) | `internal` | `261` | `261` | `78` | `183` | `0` | `0` | `1` (`100.0%`) | `26/87` (`29.89%`) |
| `swarm_verifier_2` (`@verifier-2`) | `internal` | `19` | `19` | `6` | `13` | `0` | `0` | `1` (`100.0%`) | `6/19` (`31.58%`) |
| `blinded_airgapped` (`5` subagents) | `internal_zone_b` | `5` | `5` | **`4`** | `1` | `0` | `0` | `1` (`100.0%`) | **`4/5` (`80.00%`)** |
| `deepseek_v41_flash` | `east_asia` | `16` | `16` | **`7`** | `9` | `0` | `0` | **`1` (`100.0%`)** | **`7/16` (`43.75%`)** |
| `muse_code` | `east_asia` | `15` | `14` | `3` | `11` | `0` | `1` | `14/15` (`93.33%`) | `3/14` (`21.43%`) |
| `glm_53` | `east_asia` | `4` | `4` | **`3`** | `1` | `0` | `0` | **`1` (`100.0%`)** | **`3/4` (`75.00%`)** |
| `claude_code` | `us_eu` | `5` | `4` | **`4`** | `0` | `0` | `1` | `4/5` (`80.00%`) | **`1` (`100.0%`)** |
| `gpt_6_luna` | `us_eu` | `1` | `1` | `1` | `0` | `0` | `0` | `1` (`100.0%`) | `1` (`100.0%`) |
| `grok_cli` | `us_eu` | `3` | `1` | `0` | `1` | `0` | `2` | `1/3` (`33.33%`) | `0` (`0.00%`) |
| `mistral_vibe` | `us_eu` | `4` | `1` | `0` | `1` | `3` | `0` | `1/4` (`25.00%`) | `0` (`0.00%`) |
| `qwen_code` | `us_eu_or_ea_tui` | `3` | `0` | `0` | `0` | `2` | `1` | `0` (`0.00%`) | `0` (`n/a`) |
| **External Subtotal (`8` families)** | **Cross-Continent** | **`51`** | **`41`** | **`18`** | **`23`** | **`5`** | **`5`** | **`41/51` (`80.39%`)** | **`18/41` (`43.90%`)** |
| — East-Asia (`DeepSeek` + `Muse` + `GLM`) | `east_asia` | `35` | **`34`** | **`13`** | `21` | `0` | `1` | **`34/35` (`97.14%`)** | **`13/34` (`38.24%`)** |
| — US/EU + Interactive TUI | `us_eu` + `tui` | `16` | `7` | `5` | `2` | `5` | `4` | `7/16` (`43.75%`) | `5/7` (`71.43%`) |

Key operational finding: **`10 / 51` (`19.61%`)** of all external Zone-B runs were lost to **CLI harness failures** (`5` timeouts on `mistral-vibe`/`qwen-code` + `5` flag/workspace/TUI failures on `claude-code` `task-2841`, `grok` `task-3111`/`task-3122`, `qwen-code` `task-3110`, and `muse-code` `task-3741`). East-Asia headless CLIs (`deepseek-v4.1-flash`, `muse-code`, `glm-5.3`) delivered **`34/35` (`97.14%`)** completion vs. **`7/16` (`43.75%`)** for the remaining CLIs.

### 4.2 Orthogonal Failure-Signature Coverage (`8` Distinct Signatures — Proof of Non-Redundancy)

No single verifier family covered more than **`3 / 8` (`37.50%`)** of the distinct failure signatures encountered across the expedition, and **`5 / 8` (`62.50%`)** were uncovered **exclusively by one model family**:

| # | Failure Signature | Discovering Family / Families | Exclusive? | Concrete Verified Incident(s) |
| :-: | :--- | :--- | :-: | :--- |
| 1 | C11 vs. Python/JS `±Inf`/`NaN` divergence + hidden C test skip (`test_invariants_c.c:373`) | **`deepseek_v41_flash` ONLY** | **YES** | `weft#224` (`task-4306`, caught *after* `@verifier` cleared R1!) |
| 2 | Zone-B `4,300`-digit `ValueError`, `1,500`-deep `RecursionError`, `LyingSeq`, non-ASCII `hmac.compare_digest` | `deepseek_v41_flash`, `muse_code`, `claude_code`, `swarm_verifier_1` | Shared (`4`) | `AUDIT-115` (`task-4654`), `AUDIT-116` (`task-4974`), `ap-rank3` (`task-5054`), `AUDIT-104R2/R3` |
| 3 | Mixed/tuple dict-key `sorted()` `TypeError` & self-triggering home-directory prose leak | `glm_53`, `muse_code`, `swarm_verifier_1` | Shared (`3`) | `wd#30` (`task-2927`), `AUDIT-105R` (`task-2971`), `aletheia-v21` (`task-3880`), `AUDIT-114` (`task-4533`) |
| 4 | Surviving AST `BoolOp` / disjunct deletions past `100%` `aletheia mutate` | **`blinded_airgapped` ONLY** | **YES** | `AUDIT-104R` (`0eec5607`: `24` survivors) & `AUDIT-103` (`99ff3821`: `20` survivors) |
| 5 | Live mid-audit in-place file churn breaking R4 parity | `claude_code`, `blinded_airgapped` | Shared (`2`) | `AUDIT-103` (`task-2846` + `99ff3821`) -> catalyzed Erlang Non-Churn (`AUDIT-110R`) |
| 6 | UTF-32-LE BOM Trojan-Source evasion & `75%` UTF-16 threshold mutant survivor | **`claude_code` ONLY** | **YES** | `Foundation-0/aletheia#1` (`task-3238`) |
| 7 | GitHub GraphQL `100`-file cap truncation (`463` vs `100` files) & `5,488`-box exact Krawczyk enclosure | **`swarm_verifier_2` ONLY** | **YES** | `mcproof#17` (`AUDIT-REV-GAMEPLAY-EVIDENCE`) & `rigid#21` |
| 8 | Deep domain proof, OTP semantics, IEEE-754 binade rounding & API defects missed by `Muse Code` | **`swarm_verifier_1` ONLY** | **YES** | `AUDIT-020` ($\|w\|^2=3$), `AUDIT-107` (`142` false overshoots), `AUDIT-108/109/110/112/113` (all `PASS` on `Muse Code`!) |

**Falsifiable Conclusion:** Replacing multi-family Zone-B verification with *any* single family — even our strongest internal verifier (`@verifier`) or strongest external family (`DeepSeek v4.1 Flash`) — would have leaked real, severe defects (`weft#224` C11 `NaN` divergence, `aletheia#1` UTF-32-LE Trojan-Source bypass, `44` surviving `BoolOp` disjuncts, `mcproof#17` `463`-file GraphQL truncation, and `AUDIT-107..113` domain/API defects).

---

## 5. Pillar 3 — Pareto-Ranked Recurring Defect-Class Taxonomy (`15` Classes, `93` Deduplicated Incidents)

Deduplicating all recurring technical and operational defect classes across the `280` frozen `AUDIT_LOG.md` rows, `1,018` board messages (`345` defect-class citations), and `51` external task logs yields **`15`** distinct defect classes spanning **`93`** deduplicated incidents:
- **Zone-B API / Certifier Contract Defects (`8` classes):** **`57 / 93` = `19/31` (`61.29%`)**
- **Hygiene / Operations / Tooling Defects (`7` classes):** **`36 / 93` = `12/31` (`38.71%`)**
- **Top-5 Concentration:** **`52 / 93` (`55.91%`)**
- **80% Pareto Knee (`cumulative >= 4/5`):** **Rank `9`** (`76/93 = 81.72%`, crossing `4/5 = 80.0%` at `DEF-09`).

| Rank | ID | Defect Class | Zone | Incidents | Share ($\mathbb{Q}$) | Cum. Share ($\mathbb{Q}$) | Cum. % | Board Msgs | Representative Incidents |
| :-: | :--- | :--- | :--- | ---: | :--- | :--- | ---: | ---: | :--- |
| 1 | `DEF-01` | Non-canonical JSON / raw float / `int` dict keys / non-reduced rationals | `zone_b_api` | `14` | `14/93` | `14/93` | `15.05%` | `67` | `AUDIT-006, 098, 104R2, 109, ALETHEIA-V21` |
| 2 | `DEF-02` | `bool`-as-`int` (`1 == True`) / `bool()` coercion forgery | `zone_b_api` | `11` | `11/93` | `25/93` | `26.88%` | `34` | `AUDIT-071, 104R2, 106, 108, 113, 114, exo#7` |
| 3 | `DEF-03` | Symlink / `0o022` / CRLF / UTF-8 / UTF-32 / personal home-path leak | `hygiene_ops` | `10` | `10/93` | `35/93` | `37.63%` | `89` | `AUDIT-040, 089R2a, 090, 101R, wd#30, aletheia#1` |
| 4 | `DEF-04` | Bare `assert`s stripped under `python3 -O` (`26` in `aska-physical` alone) | `hygiene_ops` | `9` | `3/31` | `44/93` | `47.31%` | `14` | `AUDIT-053`, `aska-physical` (`4` repos / `26` asserts), `mcproof` |
| 5 | `DEF-05` | Surviving R5 / AST `BoolOp` mutants & hollow-cert validators | `zone_b_api` | `8` | `8/93` | `52/93` | `55.91%` | `32` | `AUDIT-067, 069, 097, 098, 103, 104R, 111` |
| 6 | `DEF-06` | Journal-vs-ledger / `sim.jsonl` / `AUDIT_LOG` / `INDEX.md` / `SHA256SUMS` drift | `zone_b_api` | `7` | `7/93` | `59/93` | `63.44%` | `17` | `exo#8` R1/R2 (`task-4825/5002`), `cave` (`task-2948`), `AUDIT-101R` |
| 7 | `DEF-07` | Citation / line-anchor / prose count drift in reports & reviews | `hygiene_ops` | `7` | `7/93` | `22/31` | `70.97%` | `24` | `AUDIT-058, 071`, `6/6` `REVIEW_CLEARANCE` `PF` rows |
| 8 | `DEF-08` | Lying `Sequence` / `Mapping` / hostile builtin subclasses | `zone_b_api` | `5` | `5/93` | `71/93` | `76.34%` | `10` | `AUDIT-115` (`task-4654`), `exo#7` (`task-5055`), `AUDIT-006` |
| 9 | `DEF-09` | `RecursionError` on deep JSON (`100+`) & Python list (`1,500+`) nesting | `zone_b_api` | `5` | `5/93` | `76/93` | **`81.72%`** | `14` | `AUDIT-104R3` (`task-3464`), `AUDIT-115` (`task-4654`), `AUDIT-114` |
| 10 | `DEF-10` | `4,300`-digit integer `ValueError` DoS / missing `bit_length()` cap | `zone_b_api` | `4` | `4/93` | `80/93` | `86.02%` | `13` | `AUDIT-104R2` (`task-3186`), `AUDIT-115` (`task-4654`), `AUDIT-116` (`task-4974`) |
| 11 | `DEF-11` | Stale upstream pins / head-SHA drift / mid-audit snapshot churn | `hygiene_ops` | `4` | `4/93` | `28/31` | `90.32%` | `5` | `AUDIT-086`, `AUDIT-103`, `AUDIT-112` (`S15-BUG-05`), `AUDIT-114` (`S17-BUG-06`) |
| 12 | `DEF-12` | Non-ASCII `hmac.compare_digest` `TypeError` (`'\u00e9'*64` / surrogate) | `zone_b_api` | `3` | `1/31` | `29/31` | `93.55%` | `7` | `exo#8` (`task-4825`), `AUDIT-116` (`task-4974`), `ap-rank3` (`task-5054`) |
| 13 | `DEF-13` | Missing DCO `Signed-off-by:` (`git commit -s`) trailer | `hygiene_ops` | `3` | `1/31` | `30/31` | `96.77%` | `10` | Upstream DCO CI rejections requiring commit amend |
| 14 | `DEF-14` | OpenBLAS thread deadlock & self-authored/unquoted `gh pr review` `422` | `hygiene_ops` | `2` | `2/93` | `92/93` | `98.92%` | `7` | `OPENBLAS_NUM_THREADS=1` pin + GitHub `422` on own PR review |
| 15 | `DEF-15` | GitHub GraphQL `100`-file cap truncation (`463` -> `100` files) | `hygiene_ops` | `1` | `1/93` | `1` | `100.00%` | `2` | `mcproof#17` (`MC17-REV-01`: `100` reported vs `463` real) |

---

## 6. Pillar 4 — Swarm Throughput, Latency & Bottleneck Tomography

### 6.1 Tool-Call Batching Efficiency Across All `17` Agents

- **Swarm Totals (`17` agents):** `44,040` steps, `11,856` planner turns, `10,863` tool-call turns (`4,816` serial + `6,047` batched = **`6047/10863` = `55.67%`** batched), `23,199` total tool calls (**`7733/3621` $\approx 2.136$** calls per tool-call turn).
- **Best Core Batcher:** `verifier` — **`3,954 / 1,512 = 659/252` $\approx 2.615$** tool calls per tool-call turn (`1063/1512 = 70.30%` batched turns), delivering `228` board posts and `261` permanent `AUDIT_LOG.md` verifications.
- **Worst Core Batcher (Process Drag #1 — `monitor`):** `monitor` — **`1,706 / 1,122 = 853/561` $\approx 1.520$** calls/tc-turn, burning **`1,122` planner turns (`187/1976 = 9.46%` of the entire swarm's turn budget!)** to produce only **`6`** board posts (**`187` turns per board post**). Almost every monitor wake consisted of a serial `read_board`/`status`/`schedule` polling loop.
- **Process Drag #2 (`coordinator` Serial Polling):** `coordinator` ran `665 / 1,369` (`48.58%`) serial tool-call turns and spent **`32 / 108 = 8/27` (`29.63%`)** of all coordinator background tasks manually polling `Foundation-0/aletheia#1` status (`51` external Zone-B runs, `32` `aletheia#1` polling tasks, `13` git/GH ops, `10` misc shell, `2` CLI probes).

### 6.2 Verifier Turnaround Latency & Queue Depth: Before vs. After Adding `@verifier-2` (`#908`)

Matching author-to-verifier handoff posts to verifier resolution posts across `#1..#1018` (`230` matched handoffs: `203` pre-`v2` `#1..#907` + `27` post-`v2` `#908..#1018`):

| Verifier Era | Matched Handoffs | Mean Latency ($\mathbb{Q}$ s) | Mean (s) | Median (s) | p90 (s) | Max Latency (s) | Max Queue Depth |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| **Pre-`v2` All (incl. `4` inter-wave pauses `> 3h`)** | `203` | `165017/203` | `812.9s` | `415.0s` | `1,299s` | `12,638s` | `7` |
| **Pre-`v2` Active Window (`<= 7,200s`, honest baseline)** | `199` | `117940/199` | `592.7s` | `412.0s` | `1,180s` | `3,867s` | `7` |
| **Post-`v2` Active (`18` `@verifier` + `9` `@verifier-2`)** | `27` | `14455/27` | **`535.4s`** | **`361.0s`** | **`1,176s`** | **`1,660s`** | **`4`** |
| **Honest Active-Window Improvement (`Pre -> Post`)** | — | **`-61567/636876`** | **`-9.67%`** | **`-12.38%`** | `-0.34%` | **`2.33x` (`3867/1660`, `-57.07%`)** | **`-3/7` (`-42.86%`)** |

> **Process Drag #3 (Static Role-Routing Starvation):** Adding `@verifier-2` slashed active-window max tail latency by **`2.33x`** (`3,867s -> 1,660s`) and cut peak queue depth by **`42.86%`** (`7 -> 4`). However, because routing remained static by author/category rather than queue-depth/wait-time balanced, **`AUDIT-114`** sat unserved in `@verifier`'s queue for **`7,091s` (`118.2 min`)** while `@verifier-2` had empty slots — demonstrating why a starvation-capped load-balanced router is mandatory.

---

## 7. Pillar 5 — Looping Back In: Concrete Actionable Upgrades (`aletheia v2.1` & Swarm SOPs)

> **Complementary Alignment with Staged `aletheia-v21-proposals` (`f837303`):** `publish/aletheia-v21-proposals/aletheia/supervision_airlock.py` already stages Law 1b + Two-Zone Airlock + OTP supervision. The five upgrades below are **100% complementary** — closing the exact Zone-B I/O, pre-flight fuzzing, git-hook, CLI-dispatch, and verifier-routing gaps uncovered by this tomography.

### 7.1 Exact Counterfactual Rework Elimination (`AUDIT-001..117` & All `84` `PF/F` Rows)

Hand-auditing every single `PARTIAL/FRAGILE` and `FALSIFIED` verdict across all `280` frozen `AUDIT_LOG.md` rows into four mutually exclusive counterfactual buckets quantifies exactly what a commit-time `aletheia zone-b-fuzz` + unified `strict_cert_io` gate eliminates pre-freeze:

| Stratum | Total `PF/F` Loops | **100% Eliminated** (`zone-b-fuzz` + `strict_cert_io`) | **Hybrid Partially Caught** (Zone-B + Domain) | **Any Zone-B Pre-Flight Impact** | **Doc-Linter / Anchor Hooks** | **Irreducible Domain / Semantic** |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **All Core `AUDIT-001..117`** | `76` | **`10`** (`5/38 = 13.16%`) | **`17`** (`17/76 = 22.37%`) | **`27/76` (`35.53%`)** | `2` (`1/38 = 2.63%`) | **`47/76` (`61.84%`)** |
| **Modern Zone-B Era `AUDIT-097..117`** | `22` | **`7`** (`7/22 = 31.82%`) | **`8`** (`4/11 = 36.36%`) | **`15/22` (`68.18%`)** | `0` (`0.00%`) | `7/22` (`31.82%`) |
| **Latest Wave `AUDIT-112, 113, 115, 116`** | `4` | **`3`** (`3/4 = 75.00%`) | **`1`** (`1/4 = 25.00%`) | **`4/4` (`100.00%`)** | `0` (`0.00%`) | `0` (`0.00%`) |
| **All `84` `PF/F` Rows (Core + Non-Core)** | `84` | **`10`** (`5/42 = 11.90%`) | **`19`** (`19/84 = 22.62%`) | **`29/84` (`34.52%`)** | `8` (`2/21 = 9.52%`) | `47/84` (`55.95%`) |

- **Exact `10` Core Tracks 100% Eliminated Pre-Freeze:** `AUDIT-006`, `AUDIT-053`, `AUDIT-069`, `AUDIT-097`, `AUDIT-098`, `AUDIT-106`, `AUDIT-109`, `AUDIT-113`, `AUDIT-115`, `AUDIT-116` *(plus unlogged `AUDIT-114` caught by `Muse Code` `task-4533` = `4/5` in the latest wave!)*.
- **Exact `6/6` (`100%`) Review Clearances Caught by Doc-Linter Hooks:** Every single `REVIEW_CLEARANCE` `PARTIAL/FRAGILE` row (`AUDIT-REV-GAMEPLAY-EVIDENCE`, `URG3-OPTIFAB13-SILIQUANT2325`, `ALETHEIA-ISSUE11`, `MLABS-PAGES-ECOSYSTEM`, `GFQ19-SYNMERIT10-INCENTRE`, `EXO-1217`) was a pure citation, line-anchor, GraphQL `100`-file cap, or numeric transcription defect.
- **Honest Lower Bound:** `47/76` (`61.84%`) of historical Core rework loops were deep domain mathematics, formal proof gaps, OTP/conformal semantics, or adversarial nulls — proving that automated Zone-B fuzzing **eliminates boilerplate API churn (`75%` of latest-wave core bounces) so human/multi-family verifiers focus on irreducible semantic truth**.

### 7.2 Concrete Upgrade #1 — Unified `strict_cert_io` Module (Closing `aletheia-v2/aletheia/strict_io.py:53-118`)

Direct inspection of `publish/aletheia-v2/aletheia/strict_io.py:53-118` confirmed **6 live gaps** that caused recurring Zone-B bounces (`DEF-01, 02, 03, 08, 09, 10, 12`):

| `strict_io.py` Anchor | Live Gap in `aletheia v2.0.0` | Concrete `aletheia v2.1` Fix (Implemented Live in `torus_activity_oracle.py`) |
| :--- | :--- | :--- |
| `strict_io.py:53` | Uses `isinstance(raw_text, str)` (admits hostile `str` subclasses) and has no byte-size cap or unpaired-surrogate check | Enforce `type(text) is str`, wrap `text.encode("utf-8")` against `UnicodeEncodeError`, enforce `len(encoded) <= MAX_JSON_BYTES` |
| `strict_io.py:70-78` | No `parse_int` hook -> `10**5000` causes raw `ValueError` on `json.dumps` / Python `4,300`-digit limit | Add `parse_int=_parse_capped_int_token` enforcing `len(digits) <= 620` AND `val.bit_length() <= 2048` before returning |
| `strict_io.py:78-86` | No iterative depth validation (`max_depth=64`) and uses `isinstance(obj, dict)` instead of strict `type()` | Add iterative stack-based `validate_json_value(obj, max_depth=64)` rejecting depth `> 64`, cycles, `bool`-as-`int`, `float`, non-`str` keys, and all builtin subclasses (`_IntSub`/`_ListSub`/`_DictSub`/`_StrSub`) |
| `strict_io.py:110-112` | Checks `b"\r\n" not in raw` (misses bare `b"\r"`), omits symlink & symlink-ancestor checks, reads file before size-cap check | Enforce `_require_no_symlink_path(path)` (file + all parents), `path.stat().st_size <= MAX_JSON_BYTES` *before* `read_bytes()`, and `b"\r" not in raw` |
| Missing helper | No constant-time digest helper -> callers pass raw strings to `hmac.compare_digest`, crashing with raw `TypeError` on `'\u00e9'*64` or `chr(0xD800)*64` | Export `require_hex64_ascii()` + `constant_time_hex64_equal()` validating strict 64-char lowercase ASCII `[0-9a-f]` **before** calling `hmac.compare_digest` |
| Missing canonical check | No canonical-bytes roundtrip check on certificate files | Enforce `raw in (canonical_raw, canonical_raw + b"\n")` in `check_certificate_file` |

### 7.3 Concrete Upgrade #2 — `aletheia zone-b-fuzz` Commit-Time Pre-Flight Checker

Add an `aletheia zone-b-fuzz <audit_script.py> [--cert <cert.json>]` subcommand to `aletheia/cli.py` that automatically fires **12 standardized Zone-B attacks** against every track *before* freezing (and fails closed if any attack returns exit `0` or raises an uncaught raw `TypeError`/`ValueError`/`RecursionError`/`KeyError`):
- **`V01–V02`:** Non-ASCII `"\u00e9"*64` and lone-surrogate `chr(0xD800)*64` digests against `hmac.compare_digest`
- **`V03–V04`:** In-memory `10**5000` integer and JSON `5,000`-digit integer token
- **`V05–V06`:** `1,500`-deep Python list (plus cyclic list) and `100`-deep JSON text
- **`V07–V10`:** `bool`-as-`int` forgery (`True == 1`), `_IntSub`, `_ListSub`/`LyingSequence`, `_DictSub`/`LyingMapping`
- **`V11–V12`:** Duplicate JSON keys and float/`NaN`/`Infinity` literals.

Our own `torus_activity_oracle.py:run_zone_b_preflight_fuzz_matrix()` executes all **`12/12` vectors live** during every certificate build (`12/12` blocked with typed `TorusActivityError`, positive control `True`).

### 7.4 Concrete Upgrades #3, #4, #5 — Git Hooks, Standardized `zone-b-dispatch` & Dual-Verifier Routing SOPs

1. **Deterministic Pre-Push & Pre-Review Git Hook (`evaluate_prepush_git_hook`):** Automatically blocks (`5` enforceable gates): (a) missing `Signed-off-by:` DCO trailer (`DEF-13`), (b) pushing/commenting on `isPrivate=true` repos without explicit owner override, (c) GitHub GraphQL `100`-file cap truncation (`git_changed_files > graphql_files_listed`, closing `DEF-15` `mcproof#17`), (d) unpinned `OPENBLAS_NUM_THREADS != 1` (`DEF-14`), and (e) `gh pr review --approve/--request-changes` on self-authored PRs (`HTTP 422`, `DEF-14`).
2. **Standardized `zone-b-dispatch` Wrapper:** Eliminates the `10/51` (`19.61%`) external CLI harness failure rate by locking per-CLI non-interactive flags, `0700` read-only temp snapshots, strict `--max-wall-s` budgets, and automatic fallback from interactive-TUI failures (`qwen-code`/`mistral-vibe`) to high-completion headless runners (`deepseek-v4.1-flash` `16/16`, `glm-5.3` `4/4`, `muse-code` `14/15`).
3. **Starvation-Capped Dual-Verifier Router (`route_dual_verifier`) + Event-Driven Monitor/PR-Watch SOP:**
   - Route incoming verifications to `verifier-2` whenever `v2_queue < v1_queue` **or** `oldest_wait_s > 1800` (`30 min`), preventing `AUDIT-114`-class `7,091s` starvation (`route_dual_verifier(4, 0, 7091) -> target="verifier-2", starvation_reroute=True`).
   - Replace `monitor`'s serial polling loop (`1,122` turns for `6` posts = `9.46%` of swarm turns) and `coordinator`'s `32/108` (`29.63%`) manual `aletheia#1` polling tasks with a single event-driven GitHub webhook/ETag check + `swarm_wait` backoff (`>= 15 min` idle cadence), reclaiming **`~10–15%`** of total swarm turns without losing stall detection.

---

## 8. Verification, Mutation & Clean-Room Hardening Receipts

### 8.1 Frozen Deliverable Manifest (`4` Core Artifacts + This Report)

| File | Lines | Bytes | Exact SHA-256 |
| :--- | ---: | ---: | :--- |
| `torus_activity_oracle.py` | `1,059` | `52,150` | `0596be581b52f4bdea091adee77f78508ab914677840434b76809031a4bb1f86` |
| `torus_activity_audit.py` | `193` | `8,210` | `127f4bf92f6da9b7d734a8f7fbda47c2cb3e197268d2d2d54afdd68fd189ebbd` |
| `test_torus_activity_r5.py` | `803` | `41,048` | `c46285ac2c8f17be732c809cded3f17c6fd7f2cd7aa977a7e4e9f415ee1de2c5` |
| `torus_activity_certificate.json` | `1` | `13,797` | `5223f581771fcede97fd9b763b64d8d8766b9fb724d2d1a3348c5a347af086a3` |

### 8.2 Executed Gate Summary

- **Certificate Digests:**
  - `payload_sha256`: `95b2942034ac203f365cc9a8fc0ed8cf800cfdb13552b270f7b6e9685a30f981`
  - `certificate_sha256`: `4d7309aefd6c30bc85001be46c924b38462357da6bae6ac438abd7ad06bf1cd8`
- **4-Mode Isolated `-I` Parity (`-I -B`, `-I -O -B`, `-I -B -W error`, `PYTHONHASHSEED=42 -I -B`):**
  - `--standalone --json` bit-identical across all 4 modes and exact vs. disk (`5223f581771fcede97fd9b763b64d8d8766b9fb724d2d1a3348c5a347af086a3`)
  - `--check torus_activity_certificate.json`: `OK AUDIT-118A` across all 4 modes
  - `test_torus_activity_r5.py`: `9/9 OK` (`0` skipped, `0` warnings, `0` bare `assert`s) across all 4 modes
- **Live `aletheia v2.0.0 mutate --max-mutants 0 --add-cwd` (`-I -O -B -W error`):**
  - `torus_activity_oracle.py`: **`79/79` (`100.0%`) KILLED**, `0` survived, `truncated=False`, `verdict=PASS`
  - `torus_activity_audit.py`: **`19/19` (`100.0%`) KILLED**, `0` survived, `truncated=False`, `verdict=PASS`
  - **Combined:** **`98/98` (`100.0%`) KILLED**
- **Exhaustive AST `BoolOp` (`and` <-> `or`) Sweep (`-I -O -B`):**
  - `torus_activity_oracle.py`: **`17/17` (`100.0%`) KILLED**, `0` survived
  - `torus_activity_audit.py`: `0/0` (`0` `BoolOp` nodes), `0` survived
- **Clean-Room Static & Safety Gate (`aletheia v2.0.0 audit-check --strict-ancestors --safety-scan`):**
  - **`PASS`** (`5` files scanned, `2/2` R4 scripts passed, `0` CRLF, `0` `__pycache__`, `0` path leaks, `0` bare `assert`s, `0` ancestor permission findings, `0` safety findings).
