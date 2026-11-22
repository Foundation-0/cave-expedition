# AUDIT-099: Exact Pure-Q Graph Topology & Compositional Audit of *A Pattern Language* (`apl-md`) and *The Grammar of Simulation* (`simgrammar`)

- **Audit ID:** `AUDIT-099` (Continuous-Flow Track S3)
- **Honest Novelty Tier:** `N0` (independent zero-shared-code pure-$\mathbb{Q}$ recount, exact graph-cut / Tarjan SCC topology audit, multi-shuffle null testing, and Law-5 structural divergence comparison over two external prior-art corpora; zero `N2` claim)
- **Arithmetic & Execution Discipline:** 100% pure Python 3 stdlib, exact `int` / `fractions.Fraction` arithmetic, ZERO floating-point operations, ZERO bare `assert`s, deterministic local `random.Random(seed)` PRNGs
- **Verification Scripts:** [`pattern_sim_grammar_oracle.py`](pattern_sim_grammar_oracle.py), [`pattern_sim_grammar_audit.py`](pattern_sim_grammar_audit.py), [`test_pattern_sim_grammar_r5.py`](test_pattern_sim_grammar_r5.py)
- **Live Certificate:** [`pattern_sim_grammar_certificate.json`](pattern_sim_grammar_certificate.json)

---

## 1. Prior-Art Quarantine & Pinned Staged Inputs

Both corpora were analyzed strictly read-only from pinned local captures (`DIRTY=0`, zero external writes, zero shared code with either upstream project):

| Source Artifact | Upstream Origin | Pinned Commit / Digest | Scope |
|---|---|---|---|
| `repos/apl-md` | `https://github.com/zenodotus280/apl-md` (Christopher Alexander et al., *A Pattern Language*, 1977; web portal `https://patternlanguage.cc/`) | `c622b25f0b4267363d854eba3da6a82516dd5af9` | `Patterns/*.md` (`253` patterns, IDs `1..253`) |
| `repos/simgrammar` | `https://github.com/yoheinakajima/simgrammar` (Yohei Nakajima, Pedro Lucca, Shrey Kothari; web portal `https://simgrammar.com/`) | `a1156e80714de0221fefdb037bf2732824a6d156` | `data/{games,mechanics,techniques,opportunities,sources}/*.yaml` |
| `sources/simgrammar_paper.md` | `https://simgrammar.com/paper.md` (v0.8, `2026-11-04`, `dataset_sha256: f9ac0d88ac86202e2f48efd28caea7807f09bbde00cfb9ae99b2bea5ab38106e`) | `4f75e9929e34809ff73e4ad6f89dad8fb91cdda00719e81cb588e439765de99a` (`528,025` bytes) | Headline paper claims audited against raw YAML |

`pattern_sim_grammar_audit.py` enforces two explicit, non-interchangeable execution modes:
- **`--live` (default):** Fail-closed verifies both git HEAD commits directly from `.git/`, verifies `simgrammar_paper.md` byte length, SHA-256, and `dataset_sha256`, rejects symlinks and path escapes (`Path.is_relative_to`), re-parses every raw Markdown/YAML file, executes all $B = 200$ multi-shuffle nulls live, and emits `execution_mode: "live_corpus_recount"`, `live_corpus_recounted: true`.
- **`--standalone`:** Explicit offline fixture replay emitting `execution_mode: "standalone_fixture_replay"`, `live_corpus_recounted: false`, running the exact same Law-5 comparison and fail-closed conservation certifier over the pinned live-recounted payload (`payload_sha256` identical to `--live`, distinct envelope `certificate_sha256`). Missing live inputs NEVER silently fall back to standalone mode.

---

## 2. Corpus 1: Exact Graph Topology of *A Pattern Language* (`apl-md`)

### 2.1 Exact Counts & Wikilink Reconciliation
Parsing all `253` pattern files (`Patterns/*.md`, IDs `1..253`) yields:
- **Raw wikilink tokens:** `2,370` total (`0` unresolved) = **`2,265`** unique directed non-self edges + **`1`** self-loop (Pattern `137` *Children's Realm* referencing itself) + **`104`** repeated intra-file mentions. Notice that `2,265 + 1 = 2,266` reconciles the unique directed pair count recorded in `intake_catalog.json` to the exact unit.
- **Undirected skeleton:** **`1,758`** unique undirected edges (`507` mutual pairs + `1,251` one-way directed edges; exact identity $1{,}758 = 507 + 1{,}251$).
- **Reciprocity:** `1,014/2,265` directed edges (`338/755` = `0.447682`) belong to a reciprocal pair (`507` pairs), while `1,251/2,265` (`0.552318`) are one-way.
- **Scale ordering & confidence tags:** Full directed graph has `1,200` downward edges ($u < v$) and `1,065` upward edges ($u > v$). Confidence tags partition all `253` patterns into `high: 84`, `medium: 115`, `low: 54`. Patterns partition into three Alexander scale tiers: `Town (1..94): 94`, `Building (95..204): 110`, `Construction (205..253): 49`.
- **Upper-context vs. lower-completion paragraphs (`### Related Patterns`):**
  - Upper-context paragraphs contain **`921`** directed edges (`880` upward $u > v$, `41` downward $u < v$).
  - Lower-completion paragraphs contain **`1,410`** directed edges (`1,172` downward $u < v$ = `586/705` $\approx 83.12\%$, `238` upward $u > v$ $\approx 16.88\%$).
  - **`68`** directed edges appear in both upper and lower paragraphs of the same pattern.

### 2.2 Tier Transition Matrices (`Town / Building / Construction`)

**Full directed graph (`2,265` edges; `1,636/2,265` = `72.23%` same-tier):**

| From \ To | Town (`1..94`) | Building (`95..204`) | Construction (`205..253`) | Row Total |
|---|---:|---:|---:|---:|
| **Town** | 590 | 199 | 22 | 811 |
| **Building** | 140 | 808 | 140 | 1,088 |
| **Construction** | 3 | 125 | 238 | 366 |

**Lower-completion subgraph (`1,410` edges; ZERO `Construction -> Town` edges):**

| From \ To | Town (`1..94`) | Building (`95..204`) | Construction (`205..253`) | Row Total |
|---|---:|---:|---:|---:|
| **Town** | 324 | 190 | 22 | 536 |
| **Building** | 29 | 527 | 140 | 696 |
| **Construction** | 0 | 14 | 164 | 178 |

### 2.3 Structural Discovery: Cyclic Giant SCC & Strict Biconnectivity
Although *A Pattern Language* is famously presented as a top-down scale hierarchy from regions (`1`) to construction details (`253`), exact Tarjan SCC and DFS cut-vertex / bridge decomposition establish two sharp non-hierarchical invariants:
1. **Even the lower-completion subgraph is NOT a DAG:**
   - Full directed graph (`2,265` edges): `3` SCCs — a giant cyclic SCC of **`250/253`** (`98.81%`), plus `[229, 230]` and singleton `[253]`.
   - Lower-completion subgraph alone (`1,410` edges): `24` SCCs — **`228/253`** (`90.12%`) still collapse into a single giant strongly connected cycle (driven by the `238` upward completion references).
2. **Strict 2-vertex-connectivity (zero single-point cuts):**
   - The `1,758`-edge undirected graph has **`1`** connected component, **`0/253`** articulation points, and **`0/1,758`** bridges. No single pattern or single link disconnects the architectural language.

### 2.4 Exact Degree-Preserving Rewiring Nulls ($B = 200$, `seed = 20261122`)

| Observable | Observed | Null Mean ($B=200$) | $\ge$ Obs | Exact $p$ | Upper Bound |
|---|---:|---:|---:|---:|---:|
| Reciprocated directed edges (full) | `1,014` | `99.1300` | `0/200` | `1/201` | `<= 0.004976` |
| Same-tier directed edges (full) | `1,636` | `884.2050` | `0/200` | `1/201` | `<= 0.004976` |
| Downward edges ($u < v$, lower-completion) | `1,172` | `880.5100` | `0/200` | `1/201` | `<= 0.004976` |

---

## 3. Corpus 2: Independent Zero-Shared-Code Audit of *The Grammar of Simulation* (`simgrammar`)

### 3.1 Reconciliation of `simgrammar_paper.md` (v0.8) Headline Claims
Every headline count and statistical claim in `simgrammar_paper.md` was recomputed directly from raw `data/**/*.yaml` files without executing any upstream repository code (`dist/` is not committed in git):

| Claim / Metric | `simgrammar_paper.md` (v0.8) | Independent Pure-$\mathbb{Q}$ Recount | Exact Fraction | Match |
|---|---|---|---|---|
| Catalog games | `179` | `179` | `179/1` | EXACT |
| Atomic mechanics / families | `199` / `21` | `199` / `21` | `199/1`, `21/1` | EXACT |
| Game–mechanic edges | `2,069` | `2,069` (`598` core + `1,471` supporting) | `2069/1` | EXACT |
| Techniques / `affects` edges | `46` / `225` | `46` / `225` | `46/1`, `225/1` | EXACT |
| Design opportunities | `42` | `42` live (`43` YAML files = `42` live + `1` deprecated) | `42/43` | RESOLVED |
| Sources (`data/sources/*.yaml`) | — | `770` | `770/1` | RECOUNTED |
| Pre-2000 mechanic vocabulary | `69%` | `137/199` (`0.6884`) | `137/199` | MATCH |
| Post-2010 uses from pre-2000 parts | `84%` | `1,197/1,417` (`0.8447`) | `1197/1417` | MATCH |
| Co-occurring mechanic pairs | `28.5%` vs `36.1%` null ($p \le 0.004$) | `5,605/19,701` (`0.2845`) vs `7,110.42/19,701` (`0.3609`), `p = 1/201` (`<= 0.004976`) | `5605/19701` | MATCH |
| Unlinked mechanics / use share | `97` / `49%` | `97/199` carrying `1,008/2,069` (`0.4871`) of uses | `1008/2069` | MATCH |
| Spearman `emergence` vs `legibility` | $\rho = -0.42$ | $\text{sgn} = -1$, $|\rho| = 0.417917$, `p = 1/201` (`<= 0.004976`) | $\rho^2 = \frac{225386613001}{1290470145216}$ | MATCH |
| Spearman `emergence` vs `tuning` | $\rho = 0.61$ | $\text{sgn} = +1$, $|\rho| = 0.611911$, `p = 1/201` (`<= 0.004976`) | $\rho^2 = \frac{17038976983}{45505823736}$ | MATCH |
| Mechanic–mechanic typed relations | `16` req, `4` spec, `102` syn, `11` ten, `55` isolated | `16` req, `4` spec, `102` syn, `11` ten (`133` typed $\to$ `129` undirected, `4` overlap pairs), `55` isolated | `129/19701` (`0.6548%`) | EXACT |

**43-vs-42 Opportunity Discrepancy Resolution:** `data/opportunities/` contains `43` YAML files because `weather-coupled-grids.yaml` carries a top-level `deprecated:` block (`superseded_by: learned-weather-layer`, noting that *Cities: Skylines II* already shipped solar/wind weather coupling with battery storage). Excluding deprecated records leaves exactly `42` live design opportunities.

**Parser Detail Worth Preserving:** Four game files (`caves-of-qud.yaml`, `gran-turismo-7.yaml`, `opus-magnum.yaml`, `spacechem.yaml`) indent list items under `mechanics:` by two spaces (`  - id:`), and `specializes:` appears as a scalar YAML field (`specializes: <id>`) rather than a list. A naive indentation-fixed regex undercounts `gm_edges` (`2,041` instead of `2,069`) and `specializes` (`0` instead of `4`); our indentation-aware stdlib parser captures all `2,069` and `4` edges cleanly.

**Provenance Caveat on Rubric Correlations:** Although the Spearman correlations on the stored scores reproduce cleanly ($\rho \approx -0.4179$ and $+0.6119$, both permutation $p = 1/201$), `simgrammar_paper.md` §2.6 candidly documents that `98` of `102` production runs used one model rater (`claude-opus-5-5`) and a blind second model yielded ordinal $\alpha = 0.10$ on `emergence_potential` and weaker $\rho = -0.21$ (`-0.5` to `0.12`). Those correlations therefore characterize the stored single-rater rubric annotations rather than an independent human-coded ground truth.

### 3.2 Honest Negative Null Result: Global vs. Within-Technique Family Rényi-2 Concentration
The paper observes that `96/225` (`42.67%`) of technique–mechanic `affects` edges land in four families (`agents-behavior: 27`, `narrative-generation: 24`, `physics-materials: 24`, `control-automation: 21`). Testing both global and within-technique family concentration via exact Rényi-2 collision probability against $B = 200$ mechanic-family label permutations (preserving both the `225`-edge technique–mechanic graph and the catalog's exact family sizes across all `199` mechanics) reveals a critical statistical distinction:

| Concentration Metric | Observed Exact $\mathbb{Q}$ | Decimal | Null Mean ($B=200$) | $\ge$ Obs | Exact $p$ | Upper Bound | Honest Verdict ($\alpha = 0.05$) |
|---|---:|---:|---:|---:|---:|---:|---|
| **Global pooled family Rényi-2** ($D_2 = 13.4892 / 21$) | `139/1875` | `0.074133` | `0.068352` | `29/200` | `10/67` (`30/201`) | `<= 0.149254` | **`NON_SIGNIFICANT_AT_ALPHA_005`** |
| **Within-technique family Rényi-2** | `403/1245` | `0.323694` | `0.223204` | `0/200` | `1/201` | `<= 0.004976` | **`SIGNIFICANT_AT_ALPHA_005`** |

**Interpretation:** Individual techniques strongly specialize within single mechanic families (`p = 1/201`), whereas pooled global concentration across the 21 families does **not** beat a catalog-size-matched permutation null (`p = 10/67 <= 0.149254`). Much of the raw edge volume in the top four families reflects the larger number of mechanics cataloged in those families.

### 3.3 Fragile Sparse-Forest Topology of the `simgrammar` Mechanic Relation Graph
Computing exact Tarjan SCCs and undirected cut vertices / bridges on the `199`-node mechanic relation graph (`133` typed edges collapsing to `129` unique undirected pairs after `4` multi-typed `requires`+`synergy` overlaps: `budget-treasury/loans-debt`, `comparative-histograms/design-performance-rating`, `natural-selection/trait-inheritance`, `rci-demand/zoning`):
- **Dependency subgraph (`requires + specializes = 20` directed edges):** **Strict DAG** (`0` non-trivial SCCs).
- **Full undirected relation graph (`199` nodes, `129` undirected edges):** **`55/199`** (`27.64%`) isolated mechanics, **`73`** connected components, **`71/199`** (`35.68%`) articulation points, and **`120/129`** (`40/43` = `93.02%`) bridge edges. Almost every relation edge is a structural cut-edge.

---

## 4. Strict Law-5 Dimensionless Comparison (Documenting Structural Divergence)

Under Law-5 anti-smuggling discipline, we restrict comparison strictly to matched dimensionless graph observables computed from raw files and make **zero** shared-vocabulary unification claim between architectural patterns and simulation game mechanics. The two corpora occupy opposite topological regimes:

| Dimensionless Graph Observable | `apl-md` (`V = 253`) | `simgrammar` Mechanic Graph (`V = 199`) | Structural Regime |
|---|---:|---:|---|
| Directed dependency / completion giant SCC fraction | **`228/253`** (`90.12%`, lower-only) / **`250/253`** (`98.81%`, full) | **`0`** non-trivial SCCs (`dep_strict_dag = true`) | Cyclic mesh vs. strict DAG |
| Undirected connected components | **`1`** (`0` isolated) | **`73`** (`55/199` = `27.64%` isolated) | Single connected component vs. fragmented forest |
| Articulation-point fraction | **`0/253`** (`0.00%`) | **`71/199`** (`35.68%`) | Strictly 2-vertex-connected vs. cut-heavy |
| Bridge-edge fraction | **`0/1,758`** (`0.00%`) | **`120/129` = `40/43`** (`93.02%`) | Zero bridges vs. 93% cut-edges |
| Structural resilience | Strictly biconnected (`biconnected_zero_cuts = true`) | Fragile sparse forest | **Sharp topological divergence** |

This divergence aligns directly with `simgrammar_paper.md` §1's own candid admission that its catalog is *"a taxonomy with relations, in the sense of a designer's working vocabulary, and has no production rules or executable semantics,"* whereas Alexander's *A Pattern Language* is a densely cross-referenced, biconnected, mutually reinforcing web whose lower-completion links themselves form a `90.12%` strongly connected cycle.

---

## 5. Verification, Known-Answer Mini-Corpus, and `aletheia v2.0.0` Receipts

- **Hand-Computed Known-Answer Live-Path Test:** `test_pattern_sim_grammar_r5.py` constructs a synthetic `4`-pattern APL directory ($K_4$ undirected, `1` cyclic lower SCC, `1` self-loop, `2` unresolved wikilinks, `1` upper/lower overlap) and a `3`-game × `4`-mechanic × `2`-family × `2`-technique × `2`-opportunity (`1` live + `1` deprecated) SimGrammar directory with mock loose-ref & `packed-refs` `.git/` trees, executes `run_live_audit(..., n_shuffles=100)` end-to-end, and asserts every exact hand-computed integer, `Fraction`, SCC, cut vertex, bridge, Spearman $\rho^2$, and Rényi-2 value.
- **Live vs. Standalone Payload Parity:** `payload_sha256` = `a72bcd4bd4dd474d836f6239b70918e178cd3d935537d031875397b292ebc0e0` matches identically between `--live` (`live_corpus_recounted: true`, `certificate_sha256: 2607cd653a54b4bcd1affe3c32b537de6b369eabe0a756e29e4ac8ed0945be6d`) and `--standalone` (`live_corpus_recounted: false`).
- **R5 Mutation Kill (`aletheia v2.0.0 mutate --work-root . --add-cwd --max-mutants 0`, `AUDIT-099R`):**
  - `pattern_sim_grammar_oracle.py`: **`119/119` (`100.0%`) KILLED**, `0` survivors, `truncated: false`
  - `pattern_sim_grammar_audit.py`: **`27/27` (`100.0%`) KILLED**, `0` survivors, `truncated: false`
  - Combined `aletheia mutate`: **`146/146` (`100.0%`) KILLED** (`0` survivors)
  - Independent AST single-conjunct deletion sweep across all `_require(A and B ...)` guards: **`100/100` (`oracle`) + `19/19` (`audit`) = `119/119` (`100.0%`) KILLED**, `0` survivors
  - All `4/4` red-team certifier bypasses (`PSG99-BYPASS-01..04`: empty APL edge/component & biconnected edge-min conservation, SimGrammar edge/component/handshaking conservation + bipartite upper bounds `gm_edges <= n_g * n_m` & `tm_edges <= n_t * n_m`, Spearman sign/zero-magnitude consistency, strict `type(...) is bool` enforcement + derived comparison-flag consistency) closed with single-fault R5 witnesses.
- **R1–R4 & Safety Gate (`aletheia v2.0.0 audit-check . --strict-ancestors --safety-scan`):** `PASS` (`5` files scanned, `0` CRLF, `0` `__pycache__`, `0` home-path leaks, `0` bare `assert`s, `0` unseeded RNG warnings, `0` JSON errors, `0` ancestor permission findings, `0` safety findings, `2/2` scripts bit-identical across 3 isolated `-I` R4 modes: `-I -B`, `-I -O -B`, `-I -B -W error`).

### Artifact SHA-256 Inventory (Code & Live Certificate)

| File | SHA-256 | Role |
|---|---|---|
| [`pattern_sim_grammar_oracle.py`](pattern_sim_grammar_oracle.py) | `2b4308858a0f5a5bfa3d29d045a2d5feb89a5017705f6c9932366c281812711f` | Pure-$\mathbb{Q}$ parsers, bitmask $B=200$ nulls, Tarjan SCC / cut / bridge & Spearman engines, fail-closed certifier |
| [`pattern_sim_grammar_audit.py`](pattern_sim_grammar_audit.py) | `f39c709ee1a362d5f851253ee474b86fe15a9ed457ccf040d07678242406e072` | Dual-mode CLI (`--live` pin-verified vs. `--standalone` explicit fixture replay) |
| [`test_pattern_sim_grammar_r5.py`](test_pattern_sim_grammar_r5.py) | `e725d6adbfe5894a770358082e9bad33a4afa8ee25b498ec71e8456ef17a494f` | Hand-computed known-answer live-path mini-corpus + `100.0%` R5 & conjunct-kill suite (`10` test methods) |
| [`pattern_sim_grammar_certificate.json`](pattern_sim_grammar_certificate.json) | `a6034b737fbf2c9229c512d061fd36af26951b1967de5c1fda479e61dd1bc1be` | Live-recounted canonical certificate (`payload_sha256: a72bcd4b...`, `certificate_sha256: 2607cd65...`) |

