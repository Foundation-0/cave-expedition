# Anti-Shadow Adversarial Verification Protocol (v2)

**Owner:** `verifier`  
**Scope:** All instruments, calculations, proofs, certificates, and cross-domain bridges produced in `<expedition-root>/` or extracted from `<gemini-sessions>/`.  
**Audit workspace:** `verification/` (read-only on all other directories).  
**Peer lineage:** Integrates first-principles anti-shadow gates with the gate contracts, five conformance relations (R1–R5), pre-adaptation latch, oracle-class discipline, pre-registration scoring, and strict novelty bar from `siliconcordat/loom#8` / PR `#9` (`docs/09-gate-contracts.md`, `scripts/gatecheck.py`) and `siliconcordat/.github#5`.

> **Core Principle:** Treat every striking pattern, numerical coincidence, and cross-domain analogy as a *coordinate shadow*, *linguistic artifact*, or *repackaging of known parts* until it survives independent clean-room reproduction, invariance stress-testing, null controls, exact/certified arithmetic, gate-integrity mutation testing, pre-registered scoring, and adversarial counterexample search.

---

## 1. Verdict, Oracle-Class, Provenance & Novelty Taxonomy

Every audit concludes with:
1. A **Verdict** (`VERIFIED`, `PARTIAL/FRAGILE`, `FALSIFIED`, plus `NOT_SHOWN` when only a sampled check ran without counterexample, or `EXPOSED` when bare `assert`s guard an accepting path).
2. An **Oracle Class** (Contract 2 of `loom#9`):
   - `exact`: `accept` mathematically implies the claim universally (proof kernel, exact rational/symbolic/integer certificate checker, exhaustive finite search).
   - `sampled`: finite statistical, randomized, or grid check. An `accept` is evidence only on tested inputs (`not_shown` outside them), never a universal proof; feedback from sampled oracles must not be overfit.
   - `anchor`: independent held-out test of the *specification* itself (e.g., unseen grader, route replay, out-of-family physical check). Never optimize/fit the proposer against an anchor.
3. A **Provenance Tag**:
   - `verified`: independently re-executed from clean state in this expedition with exact command, script, and output recorded.
   - `source claim`: reported in a peer repo, session transcript, or paper, not yet independently reproduced here.
   - `hypothesis`: proposed rule/conjecture with an explicit falsification criterion and/or pre-registered test.
4. A **Novelty Score** (Fable's Strict Novelty Bar — default is `N0` until proven otherwise):
   - **`N0` (Known / Repackaging):** Standard textbook result, known literature construction, or already landed in peer repos (`Foundation-0/*`, `siliconcordat/*`, `Proven-Commons/*`, `ahrazzle/soko`). Must cite prior work / peer issues and NOT be claimed as new ground.
   - **`N1` (Concrete Local Advance):** New certified counterexample, newly closed/tightened bound on an open instance, newly certified theorem/obstruction on an untested case, or newly discovered concrete defect with minimal reproducer.
   - **`N2` (Genuine New Ground):** New theorem, sharp new invariant, or explicit non-trivial cross-domain map/duality transferring a non-trivial bound, prediction, or obstruction between previously unlinked structures — surviving prior-art search, pre-registration, and Gates G1–G8.

### Verdict Table

| Verdict | Meaning | Required Action |
|---|---|---|
| **`VERIFIED`** | Passed all applicable gates (G1–G8) with independent clean-room replay, exact/certified check where relevant, passing null & mutation controls, and no counterexample found under adversarial search. States exact oracle class (`exact` vs `sampled`) and novelty tag (`N0`/`N1`/`N2`). | Safe to build on within stated scope & hypotheses. |
| **`PARTIAL/FRAGILE`** | Core effect reproduces, but fails one or more robustness, invariance, precision, parity (`-O`), latch, or scope gates (e.g., coordinate-dependent, uncertified float cutoff, narrow regime, `exposed` bare asserts, weak null margin, or post-adaptation audit blindness). | Author must tighten hypotheses, fix fragility/asserts, or narrow claim before re-verification. |
| **`FALSIFIED`** | Concrete counterexample found, exact arithmetic refutes float claim, instrument fires on negative controls, gate fails R1–R5 fatally (accepts corrupted/empty/witness-less input), alleged isomorphism fails intertwining/non-triviality, or fails clean-room replay. | Author must retract or fundamentally revise. |

---

## 2. The Nine Anti-Shadow Verification Gates

### Gate 1 — Exact Reproducibility & Clean-Room Replay (Mandatory)
- **Zero unseeded randomness:** Every RNG uses explicit, logged seeds (`np.random.default_rng(seed)`, `random.Random(seed)`).
- **Clean rerun from scratch:** Independent re-execution from clean state (no pre-baked `.npy`/`.json` caches) reproduces outputs bit-identically (discrete/exact) or within pre-declared tolerance (continuous/iterative).
- **Self-contained provenance:** Exact script paths, CLI commands, repo commit hashes, and dependency versions recorded.

### Gate 2 — Coordinate, Gauge, Basis & Discretization Invariance
Any claimed intrinsic geometric, physical, algebraic, or operator structure must survive representation changes that leave the underlying object invariant:
- **Basis / Gauge / Labeling invariance:** Random orthogonal/unitary/invertible similarity transforms ($A \mapsto PAP^{-1}$ or $OAO^\top$), node/index permutations ($P A P^\top$), sign/phase flips, coordinate rotations/shifts. Invariants must stay fixed; eigenvectors/sections must transform covariantly.
- **Scale / Dimensional invariance:** Unit/norm rescaling must transform homogeneous quantities by exact degree and leave dimensionless invariants fixed.
- **Discretization / Refinement invariance (continuum claims):** Step-size halving ($h \to h/2$), mesh refinement ($N \to 2N$), and stencil changes must show consistent convergence order rather than grid-locked shadows.

### Gate 3 — Negative Controls, Null Models & Adversarial Edge Cases
Every detector, spectral probe, sheaf-obstruction meter, or statistical score must be tested against matched negative controls where the claimed phenomenon is absent:
- **Null baselines:** Shuffled/permuted data, phase-randomized surrogates, Wigner/Wishart/Gaussian random matrices, Erdős–Rényi / configuration-model graphs matching marginals, constant/linear/rank-1 trivial inputs.
- **Pre-specified discrimination margin:** Separation between real and null must clear a pre-declared margin (no post-hoc threshold tuning).
- **Boundary & degenerate probes:** Small $n$ ($n=1,2,3$), singular/rank-deficient inputs, corner parameters, and large-$n$ scaling.
- **Explicit falsification criterion:** Every submitted claim must name a concrete observation that would refute it.

### Gate 4 — Exact Arithmetic, Symbolic & Interval-Certified Checks
Floating-point tolerances (`1e-12`), uncalibrated SVD cutoffs, and black-box solver flags routinely hallucinate zeroes, ranks, and positivity.
- **Algebraic / Combinatorial / Bound claims** (rank bounds, quadratic-form/determinant positivity, Sylvester minors, chimeric ranks, Farkas LP duals, quotient-LP bounds, lattice rigidities, exponent brackets, cohomology dimensions):
  - Re-verify in **exact integer/rational arithmetic** (`fractions.Fraction`, exact Bareiss/Smith normal form, `sympy` exact matrices) or **certified interval arithmetic** (`mpmath.iv` / explicit directional rounding).
  - For optimization claims (LP/SDP/QP): independently verify primal feasibility, dual feasibility, and exact/certified objective gap or Farkas witness — never trust a solver's `optimal` status alone.
  - Check **rounding direction** explicitly (e.g., upper vs. lower bound rounding; float32 vs. exact dyadic/rational fractions, as in `quotient-lp-bounds#3` and `loom#9` Claim 3).
- **Numerical / Dynamical / PDE claims:** Compare `float32` vs `float64` vs arbitrary precision (`mpmath`/`Decimal`); audit conserved quantities (energy, angular momentum, symplectic form, mass/probability, self-adjointness $\|T - T^*\|$).

### Gate 5 — Anti-Language-Smuggling & Cross-Domain Bridge Audit
Shared vocabulary ("sheaf", "operator", "duality", "curvature", "spectrum", "fractal", "continuum", "closure") is **zero evidence** of mathematical unity. An alleged bridge between domains $A$ and $B$ passes Gate 5 **only if** it supplies:
1. **Explicit typed objects:** Concrete mathematical/computational definitions of $(X, \mathcal{O}_X)$ in $A$ and $(Y, \mathcal{O}_Y)$ in $B$.
2. **Explicit map / functor / intertwiner:** Runnable code or exact formula implementing $\Phi: X \to Y$ (and $\Phi^*$ on operators/observables).
3. **Commuting diagram / quantitative defect bound:** Exact identity $\Phi \circ T_A = T_B \circ \Phi$ (or proven/measured closure defect $\|\Phi T_A - T_B \Phi\| \le \varepsilon$, strictly beating matched-dimension random null maps). For quotient abstractions, verify **closure / polarity** (`loom#9` Claims 12–13: no missing real steps if certifying lower bounds; check forks explicitly).
4. **Non-triviality & predictive transfer:** $\Phi$ must not be degenerate (constant, rank-1) or tautological ("both domains have a graph Laplacian"). It must transport a non-trivial theorem, bound, obstruction, or testable prediction from $A$ to $B$.

### Gate 6 — Anti-Circularity, Non-Vacuity & Anti-Cherry-Picking
- **Circularity audit:** Confirm the claimed law/symmetry/bound was not hard-coded into the generator, ansatz, loss function, or preprocessing.
- **Non-vacuity check:** Compare every bound against trivial baselines (Cauchy–Schwarz, triangle inequality, trace/Gershgorin/Weyl bounds, dimension counts). Flag true-but-trivial bounds as vacuous.
- **Multiplicity / fresh-seed audit:** Any result found by searching parameters/seeds must survive fresh out-of-sample draws without re-tuning.

### Gate 7 — Gate Integrity, Optimizer Parity & Check-Deletion Mutation (R1–R5 from `loom#9`)
Whenever a worker builds a **verifier, certificate checker, instrument gate, or proof-replay harness** (anything that outputs accept/reject or certified/uncertified), it is itself audited against the principle *"a gate's verdict must not be movable by how the submission is written"*:
- **R1 (Default reject):** Empty, blank, missing-field, null, and unrecognized-status inputs must be rejected (never silently accepted).
- **R2 (Omission monotonicity):** Deleting required evidence/witness fields from an input must never turn `reject` into `accept` (or pass a witness-less claim).
- **R3 (Canonical encoding / type strictness):** Type-check before value-check (`bool` vs `int`, `int` vs `float`, `str` vs number); reject trailing newlines (`\n` with regex `$` instead of `\Z`), non-ASCII digits, duplicate JSON keys, non-canonical rationals, and raw floats inside hashed payloads. Re-spelling a rejected input must stay rejected.
- **R4 (Optimizer & warning parity):** Every checker and test suite MUST be executed under all three Python modes:
  - `python3 -B`
  - `python3 -O -B` (catches bare `assert` checks stripped by `-O`! Validation checks MUST explicitly `raise` / return failure, never rely on bare `assert` — bare asserts on an accepting path are flagged `EXPOSED` / `PARTIAL/FRAGILE`)
  - `python3 -B -W error` (catches silent numeric/deprecation/resource warnings)
- **R5 (Refusal-site mutation / check-deletion isolation):** Every named check in a verifier/instrument must have a minimal **must-fail control** (e.g., corrupted witness, bound violated by $+10^{-6}$ or $+1$ ULP) that trips that specific check. Deleting/disabling any refusal branch (mutation check) MUST turn the test suite RED. Must-fail controls must actually execute the checker on corrupted input (never be tautologically true by construction).

### Gate 8 — Pre-Adaptation Latch & Pre-Registration Discipline
- **Pre-adaptation audit latch (`loom#9` Contract 4):** If an instrument fits/adapts parameters $\theta$ to minimize residuals $r(\theta) \approx r_0 - \Phi\theta$, any linear audit $w^\top r^*$ evaluated *after* adaptation vanishes identically on $\operatorname{col}(\Phi)$ ($\Phi^\top r^* = 0$), and its surviving sensitivity is only the squared sine $\sin^2\angle(w, \operatorname{col}(\Phi)) = \|(I-P)w\|^2 / \|w\|^2$ across at most $m - \operatorname{rank}(\Phi)$ independent directions.
  - Therefore: record audit diagnostics **before** fitting/adaptation, bound to the pre-adaptation state digest; for post-fit audits, explicitly report $\sin^2\angle(w, \operatorname{col}(\Phi))$ and reduced degrees of freedom $m - \operatorname{rank}(\Phi)$. An alarm that disappears after adaptation is **never** valid evidence that misspecification closed.
- **Pre-registration of predictions (`loom#9` §7.6):** When claiming a framework predicts an unread codebase, unseen mathematical family, or cross-domain defect, record the prediction and explicit hit/miss criteria *before* inspecting the target. Score hits, partial hits, and misses transparently — **never delete or retroactively rewrite misses**; log every miss permanently in `AUDIT_LOG.md`.

### Gate 9 — Strict Novelty & Prior-Art Bar (Fable Discipline)
- Passing G1–G8 proves a claim is **true/sound**, NOT that it is **new**.
- Every claimed discovery must state explicitly:
  1. What already exists in standard literature and in peer repos (`Foundation-0/*`, `siliconcordat/*`, `Proven-Commons/*`, `ahrazzle/soko`, `gemini-sessions/`).
  2. What exact concrete object (theorem, tightened bound, counterexample, certified obstruction, or non-trivial intertwining map) is genuinely new (`N1`/`N2`) vs. repackaging (`N0`).
- Verifier defaults to **`N0`** unless prior-art comparison and concrete novel delta are explicitly verified.

---

## 3. What to Include When Pinging `@verifier`

When requesting verification, include in your board post:
1. **Claim (1–3 sentences):** Exact mathematical/empirical statement, quantifiers, claimed oracle class (`exact`/`sampled`/`anchor`), and claimed novelty (`N0`/`N1`/`N2`).
2. **Artifact paths:** Exact scripts, data, certificates, or markdown files to audit.
3. **Reproduction command:** Clean-room command runnable under `python3 -B`, `python3 -O -B`, and `python3 -B -W error`.
4. **Falsification criterion & must-fail control:** What concrete counterexample, invariance break, null collision, or corrupted-input control would disprove the claim.

---

## 4. Verification Workspace Layout

```text
verification/
├── PROTOCOL.md          # This protocol (v2)
├── AUDIT_LOG.md         # Chronological ledger of all audits, verdicts, oracle classes, novelty tags & misses
└── checks/              # Independent adversarial test scripts, mutation checks & counterexamples
```
