# AUDIT-086R — Aletheia Gate Contracts (`R6`/`R7`, Two-Direction `R3`), Live CLI Reproducer Audit (`#5`/`#7`/`#8`), & `v1.5.0`/`v2.0` Integration Matrix

- **Audit ID:** `AUDIT-086R` (Wave 2 Round 10, Arm R10-3 — Cross-Model Adversarial Synthesis of External Review on `Foundation-0/aletheia`; closes `R6R7-BUG-01..03`)
- **Epistemic Tier:** `N1` (Verified live empirical reproducers across pinned commits, line-by-line red-team audit of PR `#7` and PR `#8`, pure-$\mathbb{Q}$ zero-float executable oracles for `R6`/`R7`, Two-Direction `R3`, Oracle-Class/Feedback Contracts, and Gate-8 Subspace Latch; all upstream gate-contract, statistical, and mutation-testing foundations quarantined explicitly as `N0` under Law 4)
- **Oracle Class:** `exact` (pure Python 3 stdlib `int` / `fractions.Fraction`, zero floats on trust paths or JSON certificates, zero bare `assert`s)
- **Governance Standard:** `Foundation-0/aletheia v1.4.0` (`4/4` isolated `-I` R4 bit-identical parity in both live and standalone modes, `114/114` = `100.0%` R5 mutation kill, `audit-check --strict-ancestors PASS`)
- **External Write Count:** `0` (strictly read-only inspection of `repos/aletheia-live/` (`DIRTY=0`) and `portals/aletheia/`; local `publish/aletheia @ 85830ca0` untouched)
- **Live Certificate SHA-256:** `09bb6b25c4cd4e8bf0ada4d74e4150acde1ec6eebf35ad5cfbf7414e0883eff6` (`aletheia_r6r7_r3_certificate.json`, canonical `--json` stdout SHA-256: `27a38ab720c34a3a0a90c59ec641a5a8951ec07124d2b37c597c0395f994c952`)
- **Standalone Certificate SHA-256:** `bb1da0d4938dd051e639f8d4cb05b4325e553e12ed5ca05c6fba118f234a9968` (`--standalone --json` stdout SHA-256: `e56cac167a3869eef0ad0d6292e74a9e09374428108fde76c94dbd96f3c5adb8`)

---

## 1. Pinned Corpus & Read-Only Provenance Registry

All empirical runs exported clean trees via read-only `git archive` from `symbiosis/round10/repos/aletheia-live/` (`DIRTY=0`), leaving both `repos/aletheia-live/` and `publish/aletheia @ 85830ca0b786f9c9cef753f7fe11f6839f2e5481` completely unmodified.

### 1.1 Verified `repos/aletheia-live/` Git Refs

| Git Ref | Pinned 40-Hex Commit SHA | Role |
|---|---|---|
| `refs/heads/main` | `6a6c1af8fcae1dd7b2bc6d0cc8f471cdbd64747f` | Repository default branch |
| `refs/remotes/origin/pr/1` | `aa471867b21a0645c3290dea55c46b9732765ae9` | `feat/aletheia-v1-framework` after merging PR `#7` (`v1.4.0` `85830ca` + `6` PR `#7` commits) |
| `refs/remotes/origin/pr/7` | `362a8285d16eacdd14d549ccb55dec64c3a527af` | `fix/pr1-review-blockers` (MERGED into PR `#1` at `aa471867`) |
| `refs/remotes/origin/pr/8` | `aa920b1a908b3131c6eb3116f2e9ba21bccd0834` | `fix/pr1-review-followups` (Draft PR, `11` commits atop `aa471867`) |
| `refs/remotes/origin/pr/9` | `ffa0ed4290d782a945eb4f77e3423195460672d0` | `proposal/own-terms-first` (`spec/proposals/OWN_TERMS_FIRST.md`) |

### 1.2 Verified Read-Only Portal Artifacts (`portals/aletheia/`)

| Portal File | Bytes | Verified SHA-256 |
|---|---|---|
| `issue_2.md` | `8,095` | `c3166387362f8d8bca181eebbfffdae6f7af9bf838317f8e1cf86cbda2e82d15` |
| `issue_3.md` | `9,117` | `88b7d14041f36f25603ac27a4a1299472d457194034ec2ce7faee33fba9c05a1` |
| `issue_4.md` | `11,373` | `e3da52efc1e8f44fac4e237f1d08dd8f9b41a48c348a18b89686e65ccbac7fad` |
| `issue_5.md` | `12,335` | `684e5697190b2505e10c048281e49fe307634db3af3146a2143b601c7e7da070` |
| `pr_1.md` | `129,391` | `1a32bd825f1f38000e0cb9edf16f8a943b6c9a725ba126b350cb48ec1b638d5d` |
| `pr_7.md` | `6,535` | `63c2d4283ecb8673bf150f756e910dd0e86321dabb6600b27ff7bc03f5cb043c` |
| `pr_8.md` | `6,353` | `bec1e4a1f8c394f1a5087a6a13af0d6032d890109945cb26766a7d48f750cd14` |
| `pr_9_files/spec/proposals/OWN_TERMS_FIRST.md` | `4,558` | `bd14863344c494f1e0399d486267231fe3002fe7e005d354e2f82a8c105d6746` |

---

## 2. Law-2 Steelman Credit of External Review (`#1`, `#3`, `#5`, `#7`, `#8`)

Applying Aletheia Laws 1–5 honestly to our own repository without defensiveness: the external reviewers (`orda-aska`, `ahrazzle`, `zero-aska`, `10` inline PR `#1` review comments plus issues `#2`–`#5` and PRs `#7`–`#9`) conducted a genuinely rigorous, reproducible code-and-spec audit that surfaced real soundness defects in `aletheia`:

1. **Real PR `#1` Review Blockers Fixed in PR `#7` (`6/6` genuine):** All six fixes merged in PR `#7` (`aa471867`) resolved real bugs in `85830ca`: CI's `--no-build-isolation` failing on clean `setup-python` runners, `audit-check` flagging its own freshly generated `__pycache__` files, `init` silently clobbering existing `verification/AUDIT_LOG.md`, `--strict-unseeded` flagging `random.seed(42)` itself, Lean 4 comment/string stripping silently swallowing trailing `sorry` after an unterminated comment/string, and audit-log substring matching accepting `NOT VERIFIED` or zero-row logs.
2. **Real Correctness & Provenance Hygiene Fixes in PR `#8` (`11/11` genuine):** Missing `C6` probe in `GLYPH_REGISTRY_DATA`, unlabelled `0 / 227,540` Lean 4 corpus collision figure lacking a committed scan script, `calculus --eval` exiting `0` on `False`, unguarded exceptions in `calculus --self-test`, tautological `pythagorean_exact` field in `ratchet.py`, silent `--max-mutants` truncation, `init` crashing when a regular file blocks a scaffold directory, 3-vs-4 R4 mode doc drift, calling demo Stage 5 skip-flag checks "live mutations", overly loose `confirmed`/`beyond` prior-art regexes, and `validate_comparator_config` accepting identical `challenge_module == solution_module`.
3. **Genuine Gate-Contract Completeness Gaps (`aletheia#3`):** Our v1 spec imported `R1`–`R5` from `siliconcordat/loom#9` (`docs/09-gate-contracts.md @ b6d96ea`) while omitting `R6` (pinned checks), `R7` (measured, not declared), Two-Direction `R3` (the costly reject-stays-reject direction), sampled gate-integrity as `NOT_SHOWN`, the distinction between exact arithmetic and an exact oracle, the `anchor` vs `reference replay` split, oracle-class-dependent feedback channels, and the full Gate-8 $\operatorname{col}(\Phi)$ projection / $(m - \operatorname{rank}(\Phi)) s^2$ latch.
4. **Genuine CLI & Schema Gaps (`aletheia#5`):** `11` of the `13` reproducers in `aletheia#5` remain fully open at both `aa471867` and `aa920b1a`, and the remaining `2` (`#1`, `#9`) are only partially resolved.

At the same time, applying Law 1 equally to the external review uncovered **three concrete empirical nuances / discrepancies** (documented below): (i) `aletheia#5` `#1` was true at `58207b4` (v1.3.0) but our v1.4.0 (`85830ca`) AST local wrapper detector already resolves single-file `need()` wrappers; (ii) PR `#8`'s markdown table row 11 cites stale SHA `cc8c3b8`, which does not exist in `aletheia-live` (live HEAD is `aa920b1a`); and (iii) PR `#7` B4's Lean 4 scanner fails closed with a false positive (`LEAN4_UNTERMINATED_STRING`) on Lean 4 raw string literals containing odd double quotes (`r#"has " quote"#`).

---

## 3. Live Empirical Verification of All `13/13` `aletheia#5` Reproducers

Every reproducer in `aletheia#5` was executed live via isolated `git archive` exports from `repos/aletheia-live/` across `58207b4` (v1.3.0), `aa471867` (`pr/1 + pr/7`), and `aa920b1a` (`pr/8`).

Baseline `tests/run_all.py` 3-mode R4 parity (`-I -B`, `-I -O -B`, `-I -B -W error`):
- `aa471867` (`pr/1 + pr/7`): **`3/3` PASS, bit-identical** (`sha256: 1a1c0035cdcf3795d8e017a0358bc8785e054dc049f9c0362b181ad290fa9f53`)
- `aa920b1a` (`pr/8`): **`3/3` PASS, bit-identical** (`sha256: 27a6df31d8b079f2a71abe3a7cdd5493c1261e1e855e0c9d05e7f2141880ac32`)

| # | `aletheia#5` Finding | Live at `58207b4` (v1.3.0) | Live at `aa471867` (`pr/1+pr/7`) | Live at `aa920b1a` (`pr/8`) | Honest Verdict & Nuance |
|---|---|---|---|---|---|
| **1** | `need()` wrapper missed by mutator (`checker.py`) | **REPRODUCED** (`rc=0`, `1/1 = 100.0%`, `wrappers=None`) | **PARTIALLY RESOLVED BY v1.4.0** (`rc=1`, `2/5 = 40.0%`, `wrappers=['need']`) | **PARTIALLY RESOLVED** (`rc=1`, `2/5 = 40.0%`, `wrappers=['need']`) | True at `58207b4`; v1.4.0 (`85830ca`) fixed single-file local wrappers (`need`). **Still open** for cross-module imports (`from helpers import need` $\to$ `rc=2 NO_MUTANTS_DISCOVERED`) and missing coverage-line / `--guards` reporting. |
| **2** | R4 passes when `unittest` skips tests under `-O` | OPEN | **OPEN** (`rc=0`, `status=PASS`, `B` stderr=`OK` vs `O_B` stderr=`OK (skipped=1)`) | **OPEN** (identical) | R4 compares only `stdout` hash and exit code, ignoring `unittest` skip summary on `stderr`. |
| **3** | JSON schemas unused & disagree with hand-coded checks | OPEN | **OPEN** (`tool_loads_schema=False`; CLI accepts `AUDIT-0001` against schema `^AUDIT-[0-9]{3}[A-Z]?$`, rejects `r4_parity=False` where schema permits any `bool`) | **OPEN** (identical) | Genuine single-source-of-truth drift between `schemas/*.v1.schema.json` and `aletheia/audit_check.py`. |
| **4** | Handoff schema rejects live `next_waves_manifest.json` | OPEN | **OPEN** (`3` live tasks `W2B-1`, `W2B-2`, `W2D-3` fail `oracle_class` regex due to parenthetical qualifiers) | **OPEN** (identical) | Verified directly against live `publish/cave-expedition/next_waves_manifest.json`: e.g. `W2B-1` has `'sampled (converged PDE) + exact (conservation laws)'`. |
| **5** | `$` regex anchor in schemas matches trailing `\n` in Python `re` | OPEN | **OPEN** (`12` `$`-ending regexes across `audit_receipt` [5], `compute_handoff` [2], `frontier_portal` [5] without `(?!\n)$`) | **OPEN** (identical) | Python `re` matches `$` before a trailing `\n` (unlike ECMA-262); must align Python validators (`\Z` / `(?!\n)$`) and schemas. |
| **6** | Forced `-I` breaks `python3 test_checker.py` without hinting `--add-cwd` | OPEN | **OPEN** (`rc=2 BASELINE_TEST_FAILED`, error text omits `-I` and `--add-cwd`; adding `--add-cwd` fixes import) | **OPEN** (identical) | Genuine UX/diagnostic defect; error message should explicitly hint `--add-cwd` on `ModuleNotFoundError`. |
| **7** | Baseline test timeout raises unhandled traceback | OPEN | **OPEN** (`rc=1`, raw `subprocess.TimeoutExpired` Python traceback) | **OPEN** (identical) | Must catch `TimeoutExpired` and emit structured `BASELINE_TEST_TIMEOUT` JSON/CLI error with exit `2`. |
| **8** | `diagnose` reads only `cartography/frontier_portals.md` | OPEN | **OPEN** (`rc=1`, `overall_status=RELAPSE_DETECTED`, `alert_count=1` on root `frontier_portals.md`) | **OPEN** (identical) | Should either accept root `frontier_portals.md` or support `--portals-path`. |
| **9** | `seeded.py` (`random.seed(1); random.random()`) flagged by `--strict-unseeded` | OPEN (`count=2`) | **PARTIALLY ADDRESSED BY PR `#7` B3** (`rc=1`, `count=1`: only `random.random()`) | **PARTIALLY ADDRESSED** (`rc=1`, `count=1`) | PR `#7` B3 stopped flagging `random.seed(1)`; remaining `1` warning should clarify "module-global RNG state; prefer local `random.Random(seed)`" or recognize module-level seeding. |
| **10** | `claude-code` install writes broken paths in `.claude-plugin/plugin.json` | OPEN | **OPEN** (`plugin.json` lists `commands/aletheia.md`, `agents/...`, while files are written to `.claude/commands/...`, `.claude/agents/...`) | **OPEN** (identical) | Confirmed `3/3` listed paths missing relative to dest root. |
| **11** | Mutator misses string, tuple, multi-statement refusal shapes & `rule.py` | OPEN | **OPEN** (`shapes.py`: only `d` dict & `e` list.append found; `a` string, `b` tuple, `c` print+raise missed; `rule.py` $\to$ `rc=2 NO_MUTANTS_DISCOVERED`) | **OPEN** (identical) | Confirmed `4` sites on `shapes.py` (`L18`, `L24` only) and `0` on `rule.py`. |
| **12** | Self-checking script hits structural `50.0%` kill ceiling | OPEN | **OPEN** (`selfcheck.py`: `2/4 = 50.0%`, boundary mutants KILLED, call-deletion mutants SURVIVED) | **OPEN** (identical) | Structural property of self-checking scripts lacking negative inputs; needs documented guidance or separate positive/negative test harness requirement. |
| **13** | `from random import randint` missed by `--strict-unseeded` | OPEN | **OPEN** (`rc=0`, `unseeded_rng_warning_count=0`) | **OPEN** (identical) | AST scanner tracks `random.*` attribute calls but misses `from random import ...` aliases and bare calls. |

---

## 4. Line-by-Line Verification & Adversarial Red-Team of PR `#7` and PR `#8`

### 4.1 PR `#7` (`362a8285`, Merged into PR `#1` at `aa471867`) — `6/6` Verified

| Commit | Item | Live Verification Result | Adversarial Red-Team Notes |
|---|---|---|---|
| `355e670` | CI install (`--no-build-isolation` removed) | **VERIFIED** (`aletheia-ci.yml` uses `pip install --no-deps .`) | Clean fix for modern PEP 517 isolated build runners without preinstalled `setuptools`. |
| `f5c0bbf` | B1 Self-`__pycache__` exemption (`_pyc_matches_source`) | **VERIFIED** (`test_15`..`test_20` PASS; checks PEP 552 hash `flags & 0b1` and mtime+size header for loaded `sys.modules`) | Sound trade-off matching Python's import loader; pre-existing valid cache for a loaded module is documented as exempt (PR `#7` body L30). |
| `450770f` | B2 `init` preflight check across all 9 targets | **VERIFIED** (checks all 9 targets before writing any file) | Closed silent clobber of `verification/AUDIT_LOG.md`; regular-file-blocking-dir case finished in PR `#8` commit `5a65736`. |
| `a5fb8c3` | B3 Remove `seed` from `_UNSEEDED_RANDOM_FUNCS` | **VERIFIED** (`random.seed(42)` alone gives `count=0`) | Leaves `#5` `#9` (`random.random()` after `random.seed(1)`) and `#13` (`from random import randint`) open for v1.5.0. |
| `0811aaf` | B4 Lean 4 unterminated comment/string scanner (`_strip_lean4_with_report`) | **VERIFIED** on escaped quotes `\"`, `\\`, char literal `'"'`, nested `/- /- -/ -/`, line comments `--`, and unterminated blocks/strings | **Red-team nuance found:** Lean 4 raw string literal `r#"has " quote"#` triggers `LEAN4_UNTERMINATED_STRING` (`errs` non-empty, `sorry_found=False`). Fails closed (false positive, not a silent bypass); add Lean 4 raw-string support in v1.5.0. |
| `362a828` | F8 Whole-token `_VERDICT_TOKEN_RE` + `NO_AUDIT_ROWS` | **VERIFIED** via `.match()` + `(?![A-Za-z0-9_/])`: accepts `VERIFIED`, `**VERIFIED**`, `VERIFIED (pass)`, `PARTIAL/FRAGILE`; cleanly rejects `UNVERIFIED`, `NON_VERIFIED`, `NOT VERIFIED`, `NO VERIFIED`, `VERIFIED_BY_X`, `UNVERIFIED — VERIFIED`, `PASS`, `BYPASS`, and empty tables | Solid fail-closed verdict parser. |

### 4.2 PR `#8` (`aa920b1a`, Draft atop `aa471867`) — `11/11` Verified + `3` Red-Team Findings

All `11` commits on `refs/remotes/origin/pr/8` (`603accd` through `aa920b1`) were tested live on an isolated archive export of `aa920b1a`:

| # | Commit | Fix Summary | Live Verification on `aa920b1a` |
|---|---|---|---|
| 1 | `603accd` | Add `C6` entry to `GLYPH_REGISTRY_DATA["commutator_probes"]` | **PASS** (`['C1', 'C2', 'C3', 'C4', 'C5', 'C6']` matches self-test) |
| 2 | `31f6dfd` | Label `0 / 227,540` collision figure as `"reported ... not reproduced here"` | **PASS** (`provenance` field present; `test_22` scans all `.py`/`.md`) |
| 3 | `e1c70fc` | `calculus --eval` exits `1` on boolean `False` (`0` on `True`/values, `2` on errors) | **PASS** (`true_rc=0`, `false_rc=1`, `err_rc=2`) |
| 4 | `33dd4c7` | Guard `calculus --self-test` sections with structured `errors` list | **PASS** (`verdict=ALETHEIA_OPERATOR_CALCULUS_ALL_LAWS_VERIFIED`, `errors=[]`, `test_24` exercises failure path) |
| 5 | `0beb001` | Remove tautological `pythagorean_exact` field from `ratchet.py` | **PASS** (`'pythagorean_exact' in ratchet --demo` is `False`) |
| 6 | `0e33828` | Report `mutants_discovered`, `truncated`, and `warning` on `--max-mutants` cut | **PASS** (`discovered=4, total=1, truncated=True, warning='max_mutants=1 cut 3 of 4...'`) |
| 7 | `5a65736` | `init` returns `rc=2 WORKSPACE_EXISTS` when regular file blocks scaffold dir | **PASS** (`rc=2`, `code=WORKSPACE_EXISTS`) |
| 8 | `ddee630` | Standardize R4 documentation to 3 modes everywhere (`-I -B`, `-I -O -B`, `-I -B -W error`) | **PASS** (`0` stray 4-mode references in `.md` / checked `.py`; `test_28` green) |
| 9 | `0234ba4` | Label worked demo Stage 5 as `"Simulated Guard-Deletion Mutations"` | **PASS** (`stage5.name` updated; `test_29` green) |
| 10 | `2c6f32b` | Tighten N2 prior-art hint regex (drop bare `confirmed` / `beyond`) | **PASS** (`'confirmed beyond doubt'` triggers `N2_MISSING_PRIOR_ART_NOTE` on `aa920b1a` vs `[]` on `aa471867`) |
| 11 | `aa920b1` | Reject comparator config where `challenge_module == solution_module` | **PASS** (`rc=1`, `CHALLENGE_EQUALS_SOLUTION_MODULE:Same`) |

**Three Honest Red-Team Findings on PR `#8`:**
1. **Stale Commit SHA in PR `#8` Description Table (`pr_8.md:28`):** Row 11 of PR `#8`'s markdown table cites commit `` `cc8c3b8` ``, which does **not exist** in `repos/aletheia-live/` (`git cat-file -t cc8c3b8` fails); the live commit at `refs/remotes/origin/pr/8` is `aa920b1` (`aa920b1a908b3131c6eb3116f2e9ba21bccd0834`). Update the PR body table before merging.
2. **Truncation Still Needs `aletheia#3` §4 `NOT_SHOWN` Verdict Upgrade:** Commit `0e33828` (`#6`) adds `truncated=True` and a warning, which is necessary but not yet sufficient under `aletheia#3` §4: when `tested_count < mutants_discovered` with `0` survivors, the verdict must be **`NOT_SHOWN`** (`passed=False`), never `PASS`. Operationalized in `evaluate_sampled_integrity` below.
3. **All `9` `"Left for the author"` Items in PR `#8` (`pr_8.md:54-68`) Tracked Explicitly:** (1) mutator first-statement refusal & non-zero-as-kill semantics, (2) `diagnose` keyword heuristics, (3) comparator transitive imports, (4) pinned-manifest base directory, (5) Round 4 hawking review state, (6) external evidence provenance, (7) doc counts (`7` vs `8` N1 / `AUDIT-030` / `2` unpinned Round 3 SHAs), (8) ratchet demo fixed seed, (9) committed Lean 4 collision scan script.

---

## 5. Pure-$\mathbb{Q}$ Executable Certifier for `aletheia#3` Gate Contracts

Implemented in [`aletheia_r6r7_r3_gate_audit.py`](aletheia_r6r7_r3_gate_audit.py) with **`114/114` (`100.0%`)** R5 mutation kill via [`test_aletheia_r6r7_r3_r5.py`](test_aletheia_r6r7_r3_r5.py) and canonical zero-float output in [`aletheia_r6r7_r3_certificate.json`](aletheia_r6r7_r3_certificate.json):

### 5.1 `R6` (Pinned Checks) & `R7` (Measured, Not Declared) — `Record B` Exact Witnesses

`evaluate_r6_r7_gate(pinned_rules, submission, artifact_bytes)` enforces strict owner-pinned check specifications (`PINNED_RULE_KEYS`) separated from untrusted submitter bundles (`SUBMISSION_KEYS`), rejects any non-empty `submitter_rule_overrides`, rejects duplicate keys / floats / `NaN` / non-UTF-8 in raw payload bytes, recomputes SHA-256 and exact squared norm $\|v\|_2^2 \in \mathbb{Q}$ directly from `artifact_bytes`, and verifies declared values *against* measured values before testing pinned bounds.

All `6` negative witnesses reproducing `aletheia#3` §1 Record B are rejected deterministically (exact vector `[27, 4, 3/5, 6/5]` attains $\|v\|_2^2 = 729 + 16 + \frac{9}{25} + \frac{36}{25} = \mathbf{3734/5} = 746.8 > 20$):

| Witness Case | Attack / Record B Mechanism | Exact Refusal Code |
|---|---|---|
| `B1a_declared_norm_forgery` | Bytes hold `3734/5`, submitter declares `18` | `R7_DECLARED_NORM_MISMATCH` |
| `B1b_scaled_factor_x8_sq_norm_3734_over_5` | Honest declaration `3734/5` against pinned `max_sq_norm = 20` | `R6_MEASURED_NORM_ABOVE_MAX` |
| `B1c_header_alpha_32_vs_pinned_4` | Header alpha changed `4 -> 32` against pinned `4` | `R6_HEADER_ALPHA_OUT_OF_SPEC` |
| `B2_null_adapter_empty_bytes` | Null adapter path (`b""`) | `R7_NULL_ARTIFACT_BYTES` |
| `B3_r6_submitter_threshold_override` | Submitter injects `{"max_sq_norm": "1000"}` | `R6_SUBMITTER_RULE_OVERRIDE` |
| `B4_declared_sha256_mismatch` | Forged declared SHA-256 digest | `R7_DECLARED_SHA256_MISMATCH` |

### 5.2 Two-Direction `R3` Re-Spelling Certifier — `Note D` Witness

`certify_two_direction_r3` tests BOTH Direction (i) (accepted input with any checked value re-spelled $\to$ rejected, `8` cases) AND Direction (ii) (rejected input with any checked value re-spelled as `1`, `0`, `"true"`, `"false"`, trailing `\n` $\to$ MUST stay rejected, `6` cases):
- **`hardened_r3_multi_oracle_gate`:** **`8/8`** Direction (i) rejected AND **`6/6`** Direction (ii) stayed rejected (`passed: true`).
- **`vulnerable_note_d_gate`** (reproducing `aletheia#3` Note D where `flag is True` / `flag is False` leaves integer `1` unchecked): **EXPOSED** in Direction (ii) — `bool_true_as_int_1_note_d` flips a `FAILED` multi-oracle record from rejection to acceptance (`note_d_dir2_flip_exposed: true`).

### 5.3 Sampled Gate-Integrity `NOT_SHOWN`, Oracle Contracts, & Exact Pure-$\mathbb{Q}$ Gate-8 Subspace Latch

1. **Sampled Gate-Integrity (`evaluate_sampled_integrity`, `aletheia#3` §4):** `tested_count=1, total_discovered=4, hits_found=0` $\to$ `verdict="NOT_SHOWN"`, `passed=False`, `coverage_fraction="1/4"`; `4/4` with `0` hits $\to$ `"PASS"`; `hits_found > 0` $\to$ `"FAIL"`.
2. **Oracle Class & Feedback Contract (`certify_oracle_contract`, `aletheia#3` §§5–7):** Rejects `oracle_class="exact"` backed by `random_finite_sample_exact_arithmetic` (`ORACLE_EXACT_REQUIRES_NON_SAMPLED_BASIS`), separates `anchor` (routes failure to `spec_owner`, proposer receives `none_to_proposer_spec_owner_only`) from `reference_replay` (`diff_against_upstream_reference`), and enforces exact feedback channels across all 4 classes.
3. **Gate-8 Exact Pure-$\mathbb{Q}$ Subspace Latch (`certify_gate8_subspace_latch`, `aletheia#3` §8):** Computes exact pivot basis $\Phi_{\text{ind}}$ of $\operatorname{col}(\Phi) \subset \mathbb{Q}^m$ via pure-$\mathbb{Q}$ RREF, solves exact Gram normal equations $(\Phi_{\text{ind}}^T \Phi_{\text{ind}}) c = \Phi_{\text{ind}}^T a$, verifies $a_{\parallel} \cdot a_{\perp} = 0$ and $\|a\|^2 - (\|a_{\parallel}\|^2 + \|a_{\perp}\|^2) = 0$ identically, computes exact $\sin^2\theta = \|a_{\perp}\|^2 / \|a\|^2$, and compares total post-fit residual against $(m - \operatorname{rank}(\Phi)) s^2$:
   - Oblique probe ($m=4, \operatorname{rank}(\Phi)=2$, $a=[1,0,2,0]$, residual $5 > 2 \cdot 2 = 4$): $\sin^2\theta = \mathbf{4/5}$, `LATCH_HALT`.
   - Orthogonal boundary ($m=4, \operatorname{rank}(\Phi)=2$, $a=[0,0,1,0]$, residual $4 = 4$): $\sin^2\theta = \mathbf{1}$, `WITHIN_POSTFIT_BUDGET`.
   - In-span blind probe ($a=[3,4,0,0] \in \operatorname{col}(\Phi)$): $\sin^2\theta = \mathbf{0}$ (zero post-fit visibility $\to$ **`BLIND_AUDIT_IN_COL_PHI`**, `halt=True`, enforcing `aletheia#3` §8's rule that an audit with zero outside component cannot clear a post-adaptation gate).
   - Saturated adaptation ($m=2, \operatorname{rank}(\Phi)=2 \implies d_{\text{surv}} = 0$): `SATURATED_NO_SURVIVING_AUDITS` (`halt=True`).

---

## 6. Unified Aletheia `v1.5.0` / `v2.0` Integration & Status Matrix

Folding together `aletheia#2`, `#3`, `#4`, `#5`, `#7`, `#8`, `#9` (`OWN_TERMS_FIRST.md`) and `jdpru` `CYA-GAP-01..06` (`AUDIT-078R`):

| Stream / Source | Scope & Verified Current State | Target Release | Action Required |
|---|---|---|---|
| `aletheia#7` (`6` commits) | Merged at `aa471867`; `6/6` verified (`3/3` R4 green) | **MERGED** | Add Lean 4 raw-string `r#"..."#` case to `_strip_lean4_with_report` in `v1.5.0`. |
| `aletheia#8` (`11` commits + `9` author items) | Draft `aa920b1a`; `11/11` verified (`3/3` R4 green) | **READY TO MERGE** | Fix stale `cc8c3b8 -> aa920b1` in PR `#8` table row 11; upgrade `#6` truncation to `NOT_SHOWN` in `v1.5.0`; track all `9` `"Left for the author"` items. |
| `aletheia#3` (`I3-01..07`, `09..10`) | `R6`/`R7`, Two-Direction `R3`, `R4` write-path, `NOT_SHOWN`, `exact`-vs-`sampled`, `anchor`-vs-`replay`, feedback budgets, `THEORY.md` prior-work/falsification, `CONTRIBUTING.md` | **`v1.5.0`** | Port `AUDIT-086` pure-$\mathbb{Q}$ oracles into `aletheia/gates.py` + `spec/LAWS_AND_GATES.md`; add `CONTRIBUTING.md` & `evidence/outside/`. |
| `aletheia#3` (`I3-08`) | Gate-8 full $\operatorname{col}(\Phi)$ projection latch + preregistration hashing/second-reader scoring | **`v2.0`** | Promote `certify_gate8_subspace_latch` into `aletheia ratchet --subspace-latch` + preregistration commit-hash verifier. |
| `aletheia#5` (`I5-01..13`) | `11` fully open + `2` partially resolved (`#1` local wrappers, `#9` B3 `seed`) | **`v1.5.0`** | Fix `#2` (`unittest` `-O` skip detection), `#3`/`#4`/`#5` (single-source schema validation, `oracle_class` alignment, `\Z`/`(?!\n)$`), `#6`/`#7` (`--add-cwd` hint, `BASELINE_TEST_TIMEOUT`), `#8` (root `frontier_portals.md`), `#9`/`#13` (AST `from random import` + global RNG wording), `#10` (`claude-code` `plugin.json` paths), `#11`/`#12` (broader refusal shapes, `--guards`/coverage line, self-check guidance). |
| `aletheia#2` | Prior work by mechanism (`CS-12` / Gate 9), Advocate pass (`CS-13` / Gate 10), outside observer before `> N0` | **`v1.5.0`** | Adopt in `spec/LAWS_AND_GATES.md` + `prompts/advocate.md` + `prompts/outside-observer.md`. |
| `aletheia#4` | `17` sentence corrections + `CS-08` Compute-Leakage rename (non-reversing stratified counts) | **`v1.5.0`** | Apply prose corrections across `README.md`, `THEORY.md`, `spec/`, `evidence/`, `domains/`. |
| `aletheia#9` (`OWN_TERMS_FIRST.md`) | Two-phase mechanism-first evaluation (pending Project Owner confirmation on `L9-13`) | **`v1.5.0`** | Integrate with `AUDIT-084` (`OTF-TIGHT-01..05`) once Owner confirms `OWN_TERMS_FIRST.md:9-13`. |
| `jdpru` `CYA-GAP-01..05` (`AUDIT-078R`) | Hidden Trojan-Source Unicode, unpinned MCP / auto-approve flags, unguarded recursive variable deletion, `pull_request_target` CI privs, prose-only rules + home-relative paths | **`v1.5.0`** | Fold deterministic static scanners from `AUDIT-078R` into `aletheia audit-check --safety-scan`. |
| `jdpru` `CYA-GAP-06` (`AUDIT-078R`) | Non-interactive shell `alias rm=` illusions & cloud-sync (`iCloud`/`Dropbox`/`OneDrive`) 0-byte stubs | **`v2.0`** | Optional host-environment hygiene module (kept strictly opt-in so `audit-check` stays deterministic). |

---

## 7. Law-4 Prior-Art Quarantine (`N0` vs. `N1`) & Falsification Criteria

- **Law-4 Prior-Art Quarantine (`R10-N0-08`, `R10-N0-12`, all classified `N0`):**
  - Gate-contract taxonomy (`R1`–`R7`, Two-Direction `R3`, `anchor` vs `reference replay`, `Record B`, `Note D`, `NOT_SHOWN`, and post-fit $\operatorname{col}(\Phi)$ latch): directly attributed to `siliconcordat/loom#9` (`docs/09-gate-contracts.md @ b6d96ea`) and `Foundation-0/aletheia#3` (`N0` upstream specification).
  - Classical foundations (`R10-N0-08`, `R10-N0-12`): mutation testing (DeMillo–Lipton–Sayward 1978), metamorphic testing (Chen et al. 1998), N-version programming (Avizienis 1985), adaptive data analysis / holdout reuse (Dwork et al. 2015), orthogonal projection / Gram normal equations / Cochran degrees of freedom $m - \operatorname{rank}(\Phi)$ (`N0` textbook mathematics).
  - External code-audit defects & fixes (`aletheia#5`, `#7`, `#8`) and safety-checklist threat classes (`jdpru/cover-your-ais`, `AUDIT-078R` `CYA-GAP-01..06`): attributed explicitly to their respective authors (`N0` / prior `AUDIT-078R`).
- **`N1` Verified Contribution in `AUDIT-086R`:** Live empirical cross-commit reproduction of all `13/13` `aletheia#5` reproducers (`58207b4` vs `aa471867` vs `aa920b1a`), line-by-line verification and red-teaming of all `6` PR `#7` commits and all `11` PR `#8` commits (catching `#1`'s v1.4.0 resolution nuance, PR `#8`'s stale `cc8c3b8` table SHA, PR `#7` B4's raw-string edge case, and PR `#8` `#6`'s `NOT_SHOWN` bridge), the `114/114` (`100.0%`) R5-killed pure-$\mathbb{Q}$ `R6`/`R7` + Two-Direction `R3` (enforcing unique case-insensitive labels & strict typed non-noop mutations) + Oracle/Gate-8 (`BLIND_AUDIT_IN_COL_PHI` fail-closed) certifier, and the unified `v1.5.0`/`v2.0` integration matrix.
- **Explicit Falsification Criteria:** Any finding in `AUDIT-086` is immediately falsified if: (a) a clean-room `git archive` export of `aa471867` or `aa920b1a` yields a different pass/fail or mutant count on any of `aletheia#5` `#1`–`#13` or PR `#7`/`#8`; (b) any malformed input, float, re-spelling in Direction (i)/(ii), or submitter rule override bypasses `evaluate_r6_r7_gate`, `hardened_r3_multi_oracle_gate`, `certify_oracle_contract`, `certify_gate8_subspace_latch`, or `_resolve_git_ref_sha40`; or (c) any isolated `-I` R4 mode diverges or any R5 mutant survives under `aletheia mutate --add-cwd --max-mutants 0`.

---

## 8. Reproducible Clean-Room Verification Commands

```bash
# 1. Run R5 test suite across all 4 isolated modes
python3 -I -B -W error -m unittest test_aletheia_r6r7_r3_r5 -v
python3 -I -O -B -W error -m unittest test_aletheia_r6r7_r3_r5 -v

# 2. Verify 4/4 isolated R4 parity (live & standalone) and regenerate canonical certificate
python3 -I -B aletheia_r6r7_r3_gate_audit.py --write-cert aletheia_r6r7_r3_certificate.json
python3 -I -O -B -W error aletheia_r6r7_r3_gate_audit.py --json | sha256sum
python3 -I -O -B -W error aletheia_r6r7_r3_gate_audit.py --standalone --json | sha256sum

# 3. Verify 114/114 (100.0%) R5 mutation kill and audit-check --strict-ancestors PASS
PYTHONPATH=../../../publish/aletheia python3 -B -m aletheia mutate \
  aletheia_r6r7_r3_gate_audit.py --test-cmd "python3 test_aletheia_r6r7_r3_r5.py" --add-cwd --max-mutants 0
PYTHONPATH=../../../publish/aletheia python3 -B -m aletheia audit-check . \
  --strict-ancestors --scripts aletheia_r6r7_r3_gate_audit.py test_aletheia_r6r7_r3_r5.py
```
