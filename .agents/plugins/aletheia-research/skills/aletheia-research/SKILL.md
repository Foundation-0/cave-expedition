---
name: aletheia-research
description: >-
  The Aletheia Method (Portal-Driven Resonance & Adversarial Tomography): the default
  research methodology for scientific, mathematical, physical, and cross-repository
  discovery. Activate when running open-ended research, designing a discovery swarm,
  mining transcripts/notebooks/repos as live portals, steelmanning rough prototypes
  into exact theorems, or running independent multi-basis adversarial verification.
---

# The Aletheia Method (Portal-Driven Resonance & Adversarial Tomography)

Use this runbook to execute **The Aletheia Method** in either a **multi-agent swarm** or a **single-agent session**. It prevents the twin failure modes of AI research: *premature dismissal of new truths due to prototype bugs* and *hallucinated unity / repackaging of known parts*.

For full empirical case studies and copy-pasteable role briefs, consult:
- [METHODOLOGY.md](./references/METHODOLOGY.md) — Empirical Pass 1 vs. Pass 2+ anatomy & the 5 chain reactions
- [portal-swarm-protocol.md](./references/portal-swarm-protocol.md) — Drop-in swarm briefs, single-agent adaptation & pre-push script

---

## 1. Multi-Agent Swarm Architecture

Spawn **4–5 distinct, non-colliding roles** (each with an exclusive write directory; raw sources and upstream repos strictly read-only):

1. **`portal-keeper` (Cartographer — CENTRAL & CONTINUOUS):**
   - Never parks after Round 1. Mines raw sources into structured entry points AND a steelmanned `frontier_portals.md`.
   - Re-enters raw sources whenever any probe reports an anomaly, coincidence, obstruction, or sharpness wall, deriving the sharpest next equation/question and routing it to peers.
2. **`<domain>-probe` (2–3 Domain Explorers):**
   - Test steelmanned hypotheses directly against real upstream equations, code, or data (zero synthetic proxy substitution).
   - Loop every surprise, exact cancellation, or obstruction back to `@portal-keeper` immediately.
3. **`synthesizer` (Cross-Domain Operator Architect):**
   - Tests whether structures across domains share exact algebraic/operator maps, dualities, or Schur complements (Gate 5: zero language smuggling).
4. **`verifier` (Adversarial Tomography Oracle $\mathcal{G}_{\mathrm{obs}}$):**
   - Writes zero-shared-code independent verifiers in `verification/checks/check_NNN_*.py` and logs every verdict (`VERIFIED`, `PARTIAL/FRAGILE`, `FALSIFIED`) permanently in `verification/AUDIT_LOG.md`.
   - When finding a defect, provides both the minimal failing witness and—where the core math holds—the exact hypothesis/gate repair.
5. **`peer-weaver` (Ecosystem & Compute Handoff):**
   - Reads actual peer PR diffs and full-text prior art so the swarm never duplicates `N0` work, maps uncharted seams, indexes verified PRs, and packages Wave 2+ compute manifests for heavier machines.

**Spawning Rule for New Specialist Branches:** Spawn a dedicated theorem/prover branch ONLY once (a) a core foundation has cleared `VERIFIED` `exact` audit, and (b) an explicit mathematical obstruction or sharpness proof pinpoints the higher-order object needed to break past it.

---

## 2. Single-Agent Execution Loop (Strict Phase Separation)

When working without a swarm, run four explicit phases rather than blending critique and invention in one pass:

1. **Portal Phase (Unconcealment):** Extract 3–5 steelmanned exact hypotheses from raw sources into `frontier_portals.md`. Do not dismiss any rough lead before writing down its strongest repaired form.
2. **Probe Phase (Realization):** Implement one concrete hypothesis deterministically against real target equations/data; log anomalies and coincidences immediately.
3. **Tomography Phase (Clean-Room Audit):** Run an independent verification script (ideally via a fresh subagent or zero-shared-code script) enforcing exact/null oracles, R1–R5 gates, and full-text prior-art checks; log the honest verdict in `AUDIT_LOG.md`.
4. **Resonance Phase (Portal Re-Entry):** Feed every anomaly, counterexample, or sharpness wall back into the Portal Phase before moving to a new topic.

---

## 3. Oracle-Class & Verification Gate Checklist

- **`exact` claims** (rank bounds, inertia, SOS/Farkas duals, lattice contacts, symbolic reductions): Pure integer / `Fraction` / $\mathbb{Q}(i)$ / $\mathbb{Z}[\sqrt{2}]$ / `math.isqrt` / exact `SymPy` + independent clean-room cross-check oracle + explicit must-fail controls. Never accept `eigvalsh > 1e-12` or unverified solver `"optimal"` flags as proofs.
- **`sampled` claims** (dynamics, catalogs, Monte Carlo, time-series): Logged RNG seeds, held-out / sample-disjoint splits, matched adversarial nulls (IAAFT, twin uncoupled systems, glitches, permutations), unseen-seed replay, and pre-adaptation latch reporting.
- **`anchor` claims** (upstream model parity): Execute the untouched upstream simulator/CLI live and verify quantitative agreement.
- **R4 / Gate 7 Runtime Parity:** Every verification script must have zero bare `assert`s on validation paths, LF-only line endings, and produce identical results under:
  ```bash
  python3 -I -B <script.py> && python3 -I -O -B <script.py> && python3 -I -B -W error <script.py>
  ```
- **Novelty Bar:** Default `N0` until full-text prior-art audit confirms `N1` (sharper formulation/fix) or `N2` (genuinely new verified theorem, obstruction, or phenomenon). Never inflate `Draft PR` to "merged" or `uncompiled_source` to "machine-checked."

---

## 4. Live Anti-Pattern Red Flags (Catch Cave-Shadow Relapse)

- **Cartographer parks in Round 1:** Re-engage immediately; portals must stay open across every probe cycle.
- **String of `FALSIFIED` / `N0` reports with zero repaired hypotheses tested:** Trigger Law 2 (*Steelman-Before-Falsify*) before closing any thread.
- **Verbal analogy ("both have a sheaf/duality") with no executable map:** Reject under Law 5 until typed objects and an intertwining/Schur equation exist.
- **Toy proxy tested instead of real upstream equations/data:** Flag as a *Substitution Shadow* and re-run against the live upstream target.
- **Sharpness wall or counterexample terminates a branch:** Elevate the obstruction into a theorem or spawn a targeted branch introducing the missing invariant.

---

## 5. Pre-Push Hygiene & Portable Wave Handoff

Before pushing any verified work to GitHub:
1. Run the hygiene gate in [portal-swarm-protocol.md](./references/portal-swarm-protocol.md) (verify `0` CRLF, `0` personal home-directory path leaks, `0` secrets, `0` `__pycache__`, valid JSON & Python AST, R4 parity).
2. Publish cross-repo work strictly on feature branches as **Draft PRs** (never merge to default branches without explicit user approval).
3. For frontiers exceeding the local machine's compute budget, emit a portable `NEXT_WAVES_COMPUTE.md` + machine-readable manifest JSON so stronger machines can pick up Wave 2+ directly.
