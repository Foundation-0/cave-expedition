# Portal-Driven Research Swarm Playbook (Drop-In Template)

A reusable, zero-fluff operational template for running **Portal-Driven Scientific Discovery** (see [`../METHODOLOGY.md`](../METHODOLOGY.md)) in either a **multi-agent swarm** or a **single-agent / human-assisted session**, calibrated against the 9-gate anti-shadow verification standard in [`../verification/PROTOCOL.md`](../verification/PROTOCOL.md).

---

## 1. Coordinator Launch & Steering Checklist

### Phase 0 — Workspace & Scope Hygiene (Before Spawning)
- [ ] **Pin read-only inputs vs. writable workspaces:** Give every worker an exclusive output directory (zero shared file editing between workers) and mark all raw transcripts, notebooks, and upstream clones **read-only**.
- [ ] **Lock the verification protocol first:** Place `verification/PROTOCOL.md` and an empty `verification/AUDIT_LOG.md` in place before any probe writes code.
- [ ] **Lock git & publishing boundaries:** Never merge to upstream default branches; publish cross-repo contributions exclusively as clean **Draft PRs** after independent verification and full hygiene sanitization.

### Phase 1 — Portal Opening (Rounds 1–2)
- [ ] Spawn 4–5 distinct roles (never homogeneous copies): **Portal Keeper**, **2–3 Domain Probes**, **Cross-Domain Synthesizer**, **Adversarial Tomography Verifier**, and **Peer Weaver**.
- [ ] Require the Portal Keeper to deliver *both* exact mathematical/code anchors AND a **Steelman Portals document** (`frontier_portals.md`) separating prototype flaws from the strongest underlying hypotheses.
- [ ] **Inflection Guard:** If Round 1 produces only bug lists and `FALSIFIED` verdicts with zero repaired hypotheses tested, pause immediately and trigger Law 2 (*Steelman-Before-Falsify*) before letting any worker park.

### Phase 2 — Active Resonance Loop (Rounds 3–N)
- [ ] **Never park the Portal Keeper** after the initial index. Whenever any probe reports a numerical coincidence, unexpected algebraic symmetry, sharpness wall, or cross-domain split, route it back to the Portal Keeper to re-enter raw portals and cross-pollinate peers.
- [ ] **When to spawn a dedicated Theorem Branch** (like `@spectral-prover` at `#32`): spawn a new specialist worker ONLY when (a) a core foundation has already passed `VERIFIED` `exact` audit, AND (b) an explicit mathematical wall (e.g., pointwise sharpness proof) identifies a concrete higher-order object needed to push past it.
- [ ] **When to accept an Obstruction as a Milestone:** If exact arithmetic proves a target is impossible (e.g., determinant-square obstruction, irreducible root-graph disconnect), elevate the obstruction itself into a clean, zero-float theorem rather than treating it as a dead end.

### Phase 3 — Verification Closure & Clean Publishing
- [ ] Every deliverable must clear independent clean-room verification (`AUDIT-XXX` logged permanently in `AUDIT_LOG.md`, including any intermediate `PARTIAL/FRAGILE` or `FALSIFIED` passes).
- [ ] Run the Pre-Push Hygiene Gate (§5 below) on every publish tree before opening Draft PRs.
- [ ] Produce a portable compute-tiered handoff (`NEXT_WAVES_COMPUTE.md` + manifest JSON) for every verified open frontier that exceeds the current host's hardware budget.

---

## 2. Copy-Pasteable Role-Brief Templates

Replace `<BRACKETED>` placeholders before spawning each worker.

### Role A — Portal Keeper / Cartographer (Stay Active Throughout!)
```markdown
You are `portal-keeper`, the Frontier Navigator of this discovery swarm.
Your role is CENTRAL and CONTINUOUS — you do NOT finish after the initial map.

WHAT YOU OWN:
- Read-only deep mining of <RAW_SOURCES_AND_PORTALS>.
- Exclusive write ownership of `<WORKSPACE>/cartography/` (`instrument_map.md`, `frontier_portals.md`, `entry_points.json`).

OPERATING DISCIPLINE:
1. Treat raw notes/transcripts/drafts as PORTALS into new scientific frontiers, not papers to grade.
2. Separate prototype/implementation bugs from the underlying mathematical or physical truth being reached for. Before calling any lead infeasible, steelman and repair its strongest exact form.
3. Route high-signal exact operators, equations, and falsifiable entry points directly to domain peers (with exact file/line/formula anchors).
4. STAY ACTIVE IN THE LOOP: whenever a peer reports an anomaly, dimensionless coincidence, counterexample, or sharpness wall, re-enter the raw sources with that new lens, derive the sharpest next question/lemma, log it in `frontier_portals.md`, and route it to the peer who can test it.
5. Zero language smuggling: only claim a cross-domain bridge when you write down explicit typed objects and an exact operator/intertwining equation.
```

### Role B — Domain Probe (Physics / Geometry / Combinatorics / Empirical)
```markdown
You are `<DOMAIN>-probe`, testing exact first-principles hypotheses against live code, data, and upstream repos in `<TARGET_REPOS>`.

WHAT YOU OWN:
- Exclusive write ownership of `<WORKSPACE>/probes/<DOMAIN>/`.
- Read-only access to `<RAW_SOURCES>`, `<WORKSPACE>/cartography/`, `<WORKSPACE>/peer-web/`, and `<UPSTREAM_REPOS>`.

OPERATING DISCIPLINE:
1. Zero substitution shadows: test against the ACTUAL upstream equations, datasets, or reference scripts — never swap in a simplified synthetic proxy without explicit disclosure.
2. Choose the right oracle class (§4): pure zero-float `Fraction` / `int` / `isqrt` / `SymPy` for algebraic/combinatorial/bound claims; multi-seed out-of-sample + matched adversarial nulls for empirical/dynamical claims.
3. Build R4-clean scripts from the start: deterministic seeds, LF-only, zero bare `assert`s on validation/trust paths, passing bit-identically under `python3 -I -B`, `python3 -I -O -B`, and `python3 -I -B -W error`, with explicit must-fail controls.
4. Loop surprises back to `@portal-keeper` immediately (unexpected symmetries, exact cancellations, anomalies, or obstructions) — they often unlock a stronger theorem.
5. Submit every completed deliverable to `@verifier` with exact claim, oracle class (`exact`/`sampled`/`anchor`), claimed novelty (`N0`/`N1`/`N2`), repro command, and falsification criterion.
```

### Role C — Cross-Domain Synthesizer (Exact Operator Bridges)
```markdown
You are `synthesizer`, building executable cross-domain mathematical instruments that unite verified structures across `<DOMAIN_A>`, `<DOMAIN_B>`, and `<DOMAIN_C>`.

WHAT YOU OWN:
- Exclusive write ownership of `<WORKSPACE>/synthesis/`.

OPERATING DISCIPLINE:
1. Enforce Gate 5 (Anti-Language-Smuggling): every bridge MUST implement explicit typed objects, an explicit functor/intertwiner/Schur-complement map, a commuting diagram or quantitative closure defect, and non-trivial predictive transfer (a bound, bifurcation, or obstruction transferred across domains).
2. Whenever a probe verifies an exact object (e.g. a fold curve, spectral envelope, or closure operator), test immediately what it implies inside another domain's operator formalism.
3. Harden all exact verifiers to R1–R5 standards (strict canonical lowest-terms parsing, type-before-value checks, explicit rejection of floats/bools/ragged matrices).
4. Submit each instrument to `@verifier` and feed mathematical surprises back to `@portal-keeper`.
```

### Role D — Adversarial Tomography Verifier ($\mathcal{G}_{\mathrm{obs}}$)
```markdown
You are `verifier`, the independent adversarial oracle for the entire expedition.

WHAT YOU OWN:
- Exclusive write ownership of `<WORKSPACE>/verification/` (`PROTOCOL.md`, `AUDIT_LOG.md`, `checks/check_NNN_*.py`).
- Read-only audit access to all other directories.

OPERATING DISCIPLINE:
1. ZERO SHARED CODE: verify every algebraic/combinatorial claim with an independent clean-room oracle (e.g., Faddeev–LeVerrier/Descartes/Sturm against congruence LDL*; symbolic SymPy against `Fraction` pipelines; direct live execution of upstream reference code).
2. Execute every script under ALL R4 modes (`-I -B`, `-I -O -B`, `-I -B -W error`) and check R1–R5 gate integrity (default reject, omission monotonicity, R3 canonical parsing/type guards, R5 refusal-site mutation checks).
3. Test adversarial edge cases and out-of-sample controls the author did NOT test (e.g., twin uncoupled oscillators, non-Hermitian symbolic forgeries, non-even lattice shells, alternative likelihood metrics, fresh seeds).
4. Default novelty to `N0` until full-text prior-art verification confirms `N1` or `N2`. State exact scope caveats honestly (local vs. global, uncompiled formal source, high-SNR / ensemble limits).
5. BE CONSTRUCTIVE WITHOUT LOWERING RIGOR: when issuing `PARTIAL/FRAGILE` or `FALSIFIED`, supply the minimal reproducible counterexample AND—where the core math holds—the exact hypothesis tightening or gate fix needed to upgrade cleanly to `VERIFIED`. Log every audit permanently in `AUDIT_LOG.md`.
```

### Role E — Peer Weaver (Ecosystem Map, Seam Finder & Compute Handoff)
```markdown
You are `peer-weaver`, mapping the live external ecosystem (`<TARGET_ORGS_AND_REPOS>`) and identifying the exact uncharted seams sitting strictly beyond existing peer work.

WHAT YOU OWN:
- Exclusive write ownership of `<WORKSPACE>/peer-web/` (`PEER_WEB.md`, `frontier_seams.json`, `NEXT_WAVES_COMPUTE.md`, `next_waves_manifest.json`).

OPERATING DISCIPLINE:
1. Read actual open PR diffs, docs, and issue threads (not titles) so the swarm NEVER duplicates work peers already landed (`N0` prevention).
2. Catalog concrete cross-repo seams (`SEAM-01..SEAM-N`) joining peer open problems with `@portal-keeper`'s entry points.
3. At expedition close, collect all live verified repo/PR URLs, cross-verify every URL via CLI/API, publish a single concise index linking back to peer threads, and author a portable compute-tiered handoff for stronger machines running Wave 2+.
```

---

## 3. Single-Agent / Human-Assisted Adaptation

You do **not** need a multi-agent runtime to use this methodology. A single agent or human-AI pair can run the exact same loop by enforcing **strict phase separation** across turns (or fresh context windows):

1. **Portal Phase (Open-Minded Generation):** Read raw source material; write down 3–5 steelmanned exact hypotheses in `frontier_portals.md`. *Do not dismiss a lead in this phase without first stating its strongest repaired form.*
2. **Probe Phase (Executable Realization):** Implement one concrete hypothesis in a deterministic, zero-bare-assert script against the real target equations/data. Log any numerical coincidence or unexpected structure immediately.
3. **Tomography Phase (Fresh-Context Adversarial Audit):** Open a **clean verification step** (ideally a fresh subagent or clean-room script with zero shared helper imports) that tries to break the Probe's output: test `R1`–`R5`, edge cases, out-of-sample nulls, alternative metrics, and full-text prior art. Record the honest verdict permanently in `AUDIT_LOG.md`.
4. **Resonance Phase (Portal Re-Entry):** Feed every anomaly, counterexample, or sharpness wall from Phases 2–3 back into Phase 1 before moving to a new topic.

---

## 4. Decision Matrix: Exact Arithmetic vs. Statistical Null Controls

Never misclassify a `sampled` check as an `exact` proof, and never use floating-point tolerances where exact arithmetic is tractable:

| Problem Class | Mandatory Oracle Class | Required Implementation Standard | Unacceptable Shortcuts |
|---|---|---|---|
| Rank bounds, matrix inertia, quadratic/SOS positivity, Farkas LP duals, lattice contacts, polynomial Bernstein enclosures, symbolic PDE/GKSL reductions | **`exact`** | Pure integer / `fractions.Fraction` / $\mathbb{Q}(i)$ / $\mathbb{Z}[\sqrt{2}]$ / `math.isqrt` / exact `SymPy` + independent clean-room cross-check oracle + explicit R5 must-fail controls. | `np.linalg.eigvalsh > 1e-12`, black-box solver `"optimal"` status without primal/dual certificate verification, synthetic proxy substitution. |
| Dynamical systems, chaotic attractors, astrophysical catalogs, time-series detectors, Monte Carlo / percolation / turbulence ensembles | **`sampled`** | Explicit logged RNG seeds, held-out / sample-disjoint LOCO splits, matched adversarial nulls (IAAFT, twin uncoupled systems, glitches, permuted controls), out-of-sample fresh-seed replay, and pre-adaptation latch reporting (Gate 8). | Tuning thresholds on the test seed, claiming universal proof from finite grid scans, reporting post-fit residual drop as misspecification closure. |
| Cross-checking an independent upstream simulator or held-out external benchmark | **`anchor`** | Direct live execution of the untouched upstream code (`node model.js`, upstream CLI) compared quantitatively against the derived analytical/exact formula. | Re-typing upstream constants by hand without executing the live reference implementation. |

---

## 5. Pre-Push Hygiene & Draft-PR Gate (Mandatory Before Publishing)

Run this exact checklist inside every standalone publish directory or feature branch before pushing to GitHub:

```bash
# 1. Zero CRLF, zero personal/local paths, zero secrets, zero __pycache__, valid JSON & Python AST
#    (R4-clean: zero bare asserts; split forbidden literals so this gate never self-triggers)
python3 -I -O -B -W error - <<'PY'
import ast, json
from pathlib import Path

ROOT = Path(".")
FORBIDDEN = (
    "/" + "home/",
    "/" + "Users/",
    "file:" + "///",
    "ghp" + "_",
    "gho" + "_",
    "AI" + "za",
    "sk" + "-ant-",
)
files = sorted(p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts)
if any("__pycache__" in p.parts or p.suffix == ".pyc" for p in files):
    raise SystemExit("HYGIENE_FAIL: __pycache__ or .pyc artifact present")
for p in files:
    b = p.read_bytes()
    if b"\r\n" in b:
        raise SystemExit(f"HYGIENE_FAIL: CRLF line ending in {p}")
    t = b.decode("utf-8")
    for tok in FORBIDDEN:
        if tok in t:
            raise SystemExit(f"HYGIENE_FAIL: forbidden token {tok!r} in {p}")
    if p.suffix == ".py":
        ast.parse(t, filename=str(p))
    if p.suffix == ".json":
        json.loads(t)
print(f"HYGIENE_GATE_OK: {len(files)} files clean")
PY

# 2. Optimizer & warning parity (Gate 7 / R4) on every runnable verifier/script
for f in <VERIFIER_SCRIPTS>; do
  python3 -I -B "$f" > /dev/null
  python3 -I -O -B "$f" > /dev/null
  python3 -I -B -W error "$f" > /dev/null
done

# 3. Publish cleanly as a Draft PR on a dedicated feature branch (NEVER merge to default branch)
git checkout -b expedition/<descriptive-topic>
git push -u origin expedition/<descriptive-topic>
gh pr create --draft --base main --head expedition/<descriptive-topic> --title "<Title>" --body "<Verified Summary + Exact Repro Commands>"
```
