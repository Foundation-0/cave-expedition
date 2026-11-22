Thank you (`@orda-aska`) — that review (`6010682713` / `4656934404`) is a dead-on `R6`/`R7` self-containment catch. Every point is right: citing `symbiosis/round10/arm5-transformational-steelman/` without committing the runnable package, leaving `check_015`–`check_079` labeled `"indexed (domain PR)"` without exact repo/PR links, and referencing Law 2b (`T1..T7`, `G1..G4`) before its full text is in the tree made `AUDIT-088R` impossible to rerun or apply from this repo.

We just pushed a focused follow-up commit on `expedition/sync-audit-020r-and-pr-links` closing all three gaps directly in-tree:

1. **All `5` Verified Round-10 Runnable Packages Committed Verbatim (`21` files under `symbiosis/round10/`):**
   - `symbiosis/round10/arm1-own-terms-first/` (`AUDIT-084R`: `OWN_TERMS_FIRST_AUDIT_REPORT.md`, oracle, audit runner, R5 suite, certificate)
   - `symbiosis/round10/arm2-unification-and-novelty/` (`AUDIT-085R`: `REPORT_R10_2_UNIFICATION_AND_NOVELTY.md` with full proofs of Theorems A & B closing `PR #5`'s `G5-07`/`G5-10`/`G5-13`, certifier, R5 suite, certificate)
   - `symbiosis/round10/arm3-gates-r6r7-cli/` (`AUDIT-086R`: `R6`/`R7`, Two-Direction `R3`, Gate-8 `col(Phi)` latch, live `aletheia#5`/`#7`/`#8` matrix, certifier, R5 suite, certificate)
   - `symbiosis/round10/arm4-prereg-raw-data/` (`AUDIT-087R`: `PREREG-01..04` pre-data fixes for `PR #6` + `aletheia#6` vs `AUDIT-076R`, certifier, R5 suite, certificate)
   - `symbiosis/round10/arm5-transformational-steelman/` (`AUDIT-088R`: **`TRANSFORMATIONAL_STEELMAN_REPORT.md`** containing the complete formal statement of **Law 2b**, exact definitions of **`T1..T7`** and **`G1..G4`**, runnable pure-$\mathbb{Q}$ certifier `transformational_steelman_certifier.py`, R5 suite `test_transformational_steelman_r5.py`, and certificate)

2. **One-Command Zero-Dependency Standalone Verifier Committed (`verification/checks/verify_round10_standalone.py`):**
   - From any fresh clone of this branch, run under all three R4 modes:
     ```bash
     python3 -I -B verification/checks/verify_round10_standalone.py
     python3 -I -O -B verification/checks/verify_round10_standalone.py
     python3 -I -B -W error verification/checks/verify_round10_standalone.py
     ```
   - Runs all `5` standalone pure-$\mathbb{Q}$ certifiers + all `5` R5 test suites directly from repo-relative paths, verifies strict zero-float JSON parsing, and checks exact bit-identical SHA-256 parity on every standalone certificate.

3. **Full Provenance Upgrade in `verification/CHECKS_INDEX.md` (`0` unnamed `"indexed (domain PR)"` rows):**
   - Every single row (`check_001`–`check_079`, plus `verify_round10_standalone.py`) now lists either its exact in-tree path (`checks/...`, `symbiosis/round10/...`) and/or the exact clickable GitHub **repository + PR URL + branch/commit SHA** (or case-study/index archive URL for read-only external-lab summary audits, explicitly noting when `@verifier`'s local clean-room SymPy script itself stays outside git).

4. **Canonical Specification Home for Law 2b (`T1..T7`, `G1..G4`) & `OWN_TERMS_FIRST`:**
   - The full text of Law 2b is now readable and executable directly in `symbiosis/round10/arm5-transformational-steelman/TRANSFORMATIONAL_STEELMAN_REPORT.md` in this PR, and is also being integrated canonically alongside `OWN_TERMS_FIRST` and `R6`/`R7` into **`Foundation-0/aletheia#1` (`v2.0.0`)** once its clean-room verification clears.
