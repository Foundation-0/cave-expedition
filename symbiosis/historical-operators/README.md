# Historical Exact-Operator Applications & Gate-5 Congruence Verifier

Standalone pure Python 3 standard-library verification package (`int`, `fractions.Fraction`, `math.gcd`, and exact $\mathbb{Q}(\sqrt{2})$ pairs; zero floating-point literals, zero `float()` calls, zero `math.log`, zero bare `assert` statements, CPU-only) extending `AUDIT-002`, `AUDIT-004`, `AUDIT-009`, `AUDIT-010`, `AUDIT-014`, `AUDIT-017`, `AUDIT-018`, `AUDIT-019`, and `AUDIT-020R`.

## Scope & Outside Gate-5 Alignment

In accordance with `README.md` §1 (*"What an outside check found"*), this directory leaves `verification/checks/check_003_seam01_ropt.py` (`ae239507fecea4fdd9d5d0ef2e298483ddf040067b5987dffdeb684873feac86`) and `verification/outside/` completely untouched, and enforces the exact mathematical distinction between **shared block elimination** and **true Sylvester congruence**:

- **True Sylvester Congruence (`[4, 4, 0]`):** `AUDIT-019`'s $H_8$ fold-sheaf stress operator $\Sigma_\star = 2I_8 + H_8$ and `AUDIT-017`'s shifted Gram operator $2(G(1) - 2I_8)$ satisfy the explicit invertible rational congruence $P^\top \Sigma_\star P = 2(G(1) - 2I_8)$ with $P = 2I_8 \in GL_8(\mathbb{Q})$ and certified Sylvester inertia $(n_+, n_-, n_0) = (4, 4, 0)$.
- **Shared Block Elimination Without Congruence (`n_- = 0`):** Every passive grounded or ungrounded hydraulic M-matrix conductance Laplacian (Petra Siq `[7, 0, 0]`, Roman Gier `[10, 0, 1]`, Casarabe `[12, 0, 1]`, matched-dimension $8 \times 8$ conduit `[7, 0, 1]`) and `AUDIT-018`'s readable-record covariance block (`[2, 0, 0]`) has $n_- = 0$ and is therefore **provably non-congruent** over $\mathbb{R}$ and $\mathbb{Q}$ to `[4, 4, 0]` operators by Sylvester's Law of Inertia, sharing block elimination (`U^T M U = diag(M / M_II, M_II)`) only.

## Directory Contents

- `verify_historical_operators.py` — Standalone pure-$\mathbb{Z}/\mathbb{Q}/\mathbb{Q}(\sqrt{2})$ verifier and hardened certificate validator for Theorems 1–3.
- `test_historical_operators_r5.py` — Isolated `unittest` suite covering static AST hygiene, predicate truth tables, bounded domain guards, per-field invariant checks, and re-hashed certificate forgery refusal (including boolean-for-integer type confusion).
- `historical_operators_certificate.json` — Canonical deterministic JSON certificate (`payload_sha256 = dfb35d6970f6157169919f823f16e43ed65ae1c70f9d1a342ee7be34a7d217ae`, `certificate_sha256 = af95a89d192ae20fbe239e7ac441fa8b81fd922e8cc0ae9da86e79b7bfa3b933`).
- `HISTORICAL_OPERATORS_REPORT.md` — Detailed mathematical specification, derivations, witness tables, and provenance documentation.

## CLI Usage & Verification

All commands run with Python 3 standard library only under isolated interpreter flags (`-I -B`):

```bash
# Default mode (validates on-disk historical_operators_certificate.json against fresh pure-Q recomputation)
python3 -I -B symbiosis/historical-operators/verify_historical_operators.py

# Explicit check mode (identical to default mode)
python3 -I -B symbiosis/historical-operators/verify_historical_operators.py --check

# Print canonical JSON certificate to stdout without writing disk files
python3 -I -B symbiosis/historical-operators/verify_historical_operators.py --json

# Recompute and write canonical certificate JSON (optionally overriding path via --cert-path <PATH>)
python3 -I -B symbiosis/historical-operators/verify_historical_operators.py --write

# Run the negative-control and static-hygiene unit test suite
python3 -I -B symbiosis/historical-operators/test_historical_operators_r5.py
```

### Provenance vs. In-Module Execution

All algebraic, graph-theoretic, Diophantine, and spectral-enclosure witnesses in Theorems 1–3 are constructed and verified directly in memory by `verify_historical_operators.py` with zero external file dependencies. The eight `64`-character lowercase hexadecimal SHA-256 entries in `PROVENANCE_ARTIFACT_DIGESTS` record immutable upstream reference digests (including `verification/checks/check_003_seam01_ropt.py`) and are validated for exact `64`-hex format and pinned equality.
