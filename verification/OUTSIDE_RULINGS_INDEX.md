# Outside rulings index

This file lists, for every audit number, the internal label from [`AUDIT_LOG.md`](AUDIT_LOG.md) next to the label the outside check gave it. The "Outside ruling" columns in README section 2 and on the site's ledger page (`docs/ledger/index.html`) are copied from this file. Other places restate some rulings in shorter form: README section 1, the italic notes in README sections 1 and 2, the site's home page and joint map, and the Portal 11 standing note in `cartography/frontier_portals.md`. If a copy differs from this file, check the outside file and line named here.

It adds no ruling of its own. Each entry is copied from the file and line given in its row.

## How to read it

- **Internal label.** Copied from the row in `AUDIT_LOG.md` (line number given). Those rows stay as written: Gate 8 of [`PROTOCOL.md`](PROTOCOL.md) says misses are never deleted or rewritten, and `AUDIT_LOG.md` line 4 says the same.
- **Outside label.** Copied from [`outside/OUTSIDE_AUDIT.md`](outside/OUTSIDE_AUDIT.md) (line given) or from [`outside/rulings.json`](outside/rulings.json) (area and finding id, with the ruling: `stands`, `stands_narrowed` or `falls`). The outside team says its labels are "the observer's reading and are open to correction in the same way the ledger is" ([`outside/README.md`](outside/README.md), line 38). This index shows both labels. It does not adopt either one.
- **not checked** means the row is listed under "Not checked" in `OUTSIDE_AUDIT.md` line 115. **not rated** means the outside files give no label for that part.
- **Whose labels.** `VERIFIED`, `PARTIAL/FRAGILE` and `FALSIFIED` are this repository's verdicts. `VERIFIED` means "passed all applicable gates (G1–G8)" (`PROTOCOL.md`, verdict table). `N0`, `N1` and `N2` are this repository's novelty labels (`PROTOCOL.md`, section 1, item 4). The outside check uses the same labels (`OUTSIDE_AUDIT.md` line 20).
- **N2 prerequisites.** `PROTOCOL.md` (section 1, the `N2` definition) requires an `N2` result to survive "prior-art search, pre-registration, and Gates G1–G8". For each row with an internal `N2` label, the last column lists which of G1–G8 appear in the row's "Gates Tested" column, whether G9 (the prior-art bar) appears, and whether a pre-registered prediction is recorded. The predictions table in `AUDIT_LOG.md` (line 37) reads "(none registered yet)".

## Rows on `main`

| Audit | `AUDIT_LOG.md` line | Internal label (verdict; novelty) | Outside label | Source of the outside label | N2 prerequisites in the row |
|---|---|---|---|---|---|
| AUDIT-001 | 10 | `FALSIFIED`; `N1` (TCB exploits) | not checked (raw session drafts are not public) | `OUTSIDE_AUDIT.md`:115 | no internal `N2` |
| AUDIT-002 | 11 | `VERIFIED`; `N2` (CONFIRMED) | `N1`, upper end. New: the joint optimum in closed form, the compression and the sharpness theorem. The sharpness theorem has no written proof yet. | `OUTSIDE_AUDIT.md`:59, :31; `rulings.json` spectral F1 (`stands_narrowed`), F6 (`stands_narrowed`) | G1–G8 listed: G1, G2, G4, G6, G7. Not listed: G3, G5, G8. G9 listed. No pre-registration recorded. |
| AUDIT-003 | 12 | `PARTIAL/FRAGILE`; `N0`/`N1` | not checked (raw session drafts are not public) | `OUTSIDE_AUDIT.md`:115 | no internal `N2` |
| AUDIT-004 | 13 | `VERIFIED`; `N2` Part A (peeling and semiring split), `N1` Parts B and C | Part A, peeling tower: `N0` (saturated state-dependent cost partitioning). Optimality theorem: `N0` (Bellman's equation). The headline "64 to 124" uses a baseline that is not the fair one (fair baseline at `OUTSIDE_AUDIT.md`:80). Parts B and C: not rated. | `OUTSIDE_AUDIT.md`:64, :65, :80; `rulings.json` peeling F1 (`stands`), F3 (`stands_narrowed`), F5 (`stands`) | G1–G8 listed: G1, G2, G3, G4, G5, G7. Not listed: G6, G8. G9 listed. No pre-registration recorded. |
| AUDIT-005 | 14 | `VERIFIED`; `N1` | `N0` identity (restricted least squares), `N1` application. It does not settle Claim 9 of the gate-contract document. | `OUTSIDE_AUDIT.md`:62, :91; `rulings.json` twoloop-stack F1 (`stands`), F2 (`stands_narrowed`), F3 (`stands_narrowed`) | no internal `N2` |
| AUDIT-006 | 15 | `PARTIAL/FRAGILE`; `N1` | rated on the re-audit row, AUDIT-006R | — | no internal `N2` |
| AUDIT-006R | 31 (joint row with 007R and 008R) | `VERIFIED`; `N1` ("all 3 instruments") | `Q_stack`: `N0`. Trace-slack law: `N0` (first-order perturbation estimate); oracle class corrected from "exact law" to "certified sufficient condition", worst case 4.8 percent above 1/360. Portal 11 cross-ratio study: not checked. | `OUTSIDE_AUDIT.md`:63, :92, :115; `rulings.json` twoloop-stack F4 (`stands`), F5 (`stands_narrowed`) | no internal `N2` |
| AUDIT-007 | 16 | `PARTIAL/FRAGILE`; `N1` | rated on the re-audit row, AUDIT-007R | — | no internal `N2` |
| AUDIT-007R | 31 | `VERIFIED`; `N1` | not checked | `OUTSIDE_AUDIT.md`:115 | no internal `N2` |
| AUDIT-008 | 17 | `VERIFIED`; `N1` | rated on the re-audit row, AUDIT-008R | — | no internal `N2` |
| AUDIT-008R | 31 | `VERIFIED`; `N1` | "Maslov–Doob" identity: `N0` (a diagonal similarity in the ordinary semiring, a max-times Doob transform only when `H = d*`). The 008R identities were checked symbolically (`OUTSIDE_AUDIT.md`:37). Other parts: not rated. | `rulings.json` peeling F4 (`stands_narrowed`); `OUTSIDE_AUDIT.md`:37 | no internal `N2` |
| AUDIT-009 | 18 | `VERIFIED`; `N2` (CONFIRMED) | strong `N1`, candidate `N2`. "Optimal 4D packing `D_4`" repaired to "the densest lattice packing in four dimensions" (`OUTSIDE_AUDIT.md`:86). | `OUTSIDE_AUDIT.md`:56, :86; `rulings.json` folds-dn-e8 F2 (`stands`), F4 (`falls`) | G1–G8 listed: G1, G2, G3, G4, G6, G7. Not listed: G5, G8. G9 listed. No pre-registration recorded. |
| AUDIT-010 | 19 | `VERIFIED`; `N1` Theorems A and C and live falsification, `N2` Theorem B | Theorems A and B: `N0`. Theorem C: `N1`, unchanged. "Refutes period 3" repaired: the statistic has no power against period 3 (`OUTSIDE_AUDIT.md`:83). | `OUTSIDE_AUDIT.md`:66, :67, :83; `rulings.json` zerolog F1 (`stands`), F2 (`stands`), F4 (`stands_narrowed`) | G1–G8 listed: G1, G2, G3, G4, G6, G7, G8. Not listed: G5. G9 listed. G8 is listed, but no prediction is registered in the table at `AUDIT_LOG.md`:37. |
| AUDIT-011 | 20 | `VERIFIED`; `N2` (CONFIRMED) | rated on the re-audit row, AUDIT-011R | — | G1–G8 listed: G1, G2, G3, G4, G6, G7. Not listed: G5, G8. G9 listed. No pre-registration recorded. |
| AUDIT-011R | 28 (joint row with 013R) | `VERIFIED`; `N2` (Probe 1) | `N1` (a standard quasi-static and slow-manifold closure; new: it closes the host's open gate with no fitted parameter). The "0.00008 percent" figure is measured from the closure's own starting condition (`OUTSIDE_AUDIT.md`:82). | `OUTSIDE_AUDIT.md`:68, :82; `rulings.json` physics F2 (`stands_narrowed`) | G1–G8 listed: G1, G2, G3, G4, G6, G7. Not listed: G5, G8. G9 listed. No pre-registration recorded. |
| AUDIT-012 | 21 | `VERIFIED`; `N1` | `N1`, reworded: the zero-parameter model is not falsified, and "decisively falsifies" is repaired (`OUTSIDE_AUDIT.md`:81). The chirp estimator was not checked. | `OUTSIDE_AUDIT.md`:69, :81, :115; `rulings.json` physics F1 (`stands_narrowed`) | no internal `N2` |
| AUDIT-013 | 22 | `PARTIAL/FRAGILE`; `N1` | rated on the re-audit row, AUDIT-013R | — | no internal `N2` |
| AUDIT-013R | 28 | `VERIFIED`; `N1` (Probe 3) | `N1` (the ruling splits it: method `N0`, application `N1`) | `OUTSIDE_AUDIT.md`:70; `rulings.json` physics F5 (`stands`) | no internal `N2` |
| AUDIT-014 | 23 | `VERIFIED`; `N2` (CONFIRMED) | A2: `N0` as a theorem, `N1` for the closed form. A4: `N1`. A3: not rated. | `OUTSIDE_AUDIT.md`:60, :61; `rulings.json` spectral F2 (`stands_narrowed`), F3 (`stands_narrowed`) | G1–G8 listed: G1, G2, G3, G4, G6, G7. Not listed: G5, G8. G9 listed. No pre-registration recorded. |
| AUDIT-015 | 24 | `PARTIAL/FRAGILE`; `N1`/`N2` | rated on the re-audit row, AUDIT-015R | — | G1–G8 listed: G1, G3, G4, G6, G7. Not listed: G2, G5, G8. G9 listed. No pre-registration recorded. |
| AUDIT-015R | 27 (joint row with 016R) | `VERIFIED`; `N1`/`N2` (Track B) | not checked beyond its statement | `OUTSIDE_AUDIT.md`:115 | G1–G8 listed: G1, G4, G6, G7. Not listed: G2, G3, G5, G8. G9 listed. No pre-registration recorded. |
| AUDIT-016 | 25 | `VERIFIED`; `N1` | rated on the re-audit row, AUDIT-016R | — | no internal `N2` |
| AUDIT-016R | 27 | `VERIFIED`; `N1` (Track C) | `N1` for the checker, "as a second independent implementation". The sentence "supports loom#7 certificates" in `siliconcordat/loom` draft 10 is not true at the checker's head (`OUTSIDE_AUDIT.md`:93). | `rulings.json` spectral F5 (`stands_narrowed`); `OUTSIDE_AUDIT.md`:33, :93 | no internal `N2` |
| AUDIT-017 | 26 | `VERIFIED`; `N2` (CONFIRMED — LANDMARK RESULT) | `N2`, medium confidence (bounded prior-art search). Drop "landmark"; replace "CONFIRMED" with the bounded-search statement. "Uniqueness theorem" repaired to a dimension obstruction (`OUTSIDE_AUDIT.md`:87). | `OUTSIDE_AUDIT.md`:55, :87; `rulings.json` folds-dn-e8 F1a (`falls`: the doubt about the `N2` label), F1b (`stands`), F3 (`stands_narrowed`) | G1–G8 listed: G1, G2, G3, G4, G6, G7. Not listed: G5, G8. G9 listed. No pre-registration recorded. |
| AUDIT-018 | 29 | `VERIFIED`; `N2` (CONFIRMED — CROSS-REPO MILESTONE) | `N0` mathematics (second-order adiabatic elimination), `N1` at most for the model calibration | `OUTSIDE_AUDIT.md`:71; `rulings.json` physics F4 (`stands_narrowed`) | G1–G8 listed: G1, G2, G3, G4, G6, G7. Not listed: G5, G8. G9 listed. No pre-registration recorded. |
| AUDIT-019 | 30 | `VERIFIED`; `N2` (CONFIRMED — CROSS-DOMAIN MILESTONE) | `N1` (the object is the relaxed Cauchy-Born tensor of periodic-truss mechanics) | `OUTSIDE_AUDIT.md`:58; `rulings.json` leech-sheaf F5 (`stands_narrowed`) | G1–G8 listed: G1, G2, G3, G4, G6, G7. Not listed: G5, G8. G9 listed. No pre-registration recorded. |

## Rows that are not on `main`

AUDIT-020, AUDIT-020R and AUDIT-021 exist only on the authors' pull request 1, branch `expedition/sync-audit-020r-and-pr-links`, which `outside/README.md` (lines 22 to 28) describes as open. None of the three has a row in `AUDIT_LOG.md` on `main` at commit `9729839`.

| Audit | Where | Internal label | Outside label | Source |
|---|---|---|---|---|
| AUDIT-020R | pull request 1, read by the outside check at `872fffd` | `N2` (the "Ledger" column of `OUTSIDE_AUDIT.md`:57) | `N1`. "Unjamming" and "all contacts" repaired to "all non-bar inter-cell contacts strictly open" (`OUTSIDE_AUDIT.md`:88). | `OUTSIDE_AUDIT.md`:57, :88; `rulings.json` leech-sheaf F1 to F4 (`stands_narrowed`) |
| AUDIT-021 | pull request 1 | not read here | not checked | `OUTSIDE_AUDIT.md`:115 |

## Rulings on sentences, not rows

- **The eight-way Schur-complement sentence (README section 1).** The outside Gate-5 check ruled: "Gate 5 is not met for the eight-way claim" ([`outside/gate5-unification/README.md`](outside/gate5-unification/README.md), line 157). It proposed this wording (line 161): "Eight frontiers each use block elimination. One pair, AUDIT-017 and AUDIT-019, is linked by an exact congruence. A shared invariant beyond the elimination identity has not been shown."
- **The repair table, `OUTSIDE_AUDIT.md` lines 79 to 95.** Rows 81 to 83 repair ledger wording (AUDIT-012, AUDIT-011R, AUDIT-010) that the README also restates. Row 94 concerns this repository's `check_007` and `check_008`, which pin code from before the probes were patched; the verdicts they back still reproduce (row 94). Those scripts stay byte-identical as audited. Every other row repairs text in a sibling draft. Rows 80, 86, 87, 88, 91, 92 and 95 are also restated in the README. In README sections 1 and 2 each of those restatements, and of rows 81 to 83, is followed by the repair. Rows 79, 84, 85, 89, 90 and 93 concern text that lives only in sibling repositories.

## Pre-registration gap (a reading, recorded here and not in the protocol)

`PROTOCOL.md` requires pre-registration for an `N2` label (section 1, the `N2` definition). The predictions table at `AUDIT_LOG.md` line 37 reads "(none registered yet)". G8 (which carries the pre-registration rule) appears in 2 of the 22 rows (AUDIT-010 at line 19 and AUDIT-012 at line 21), and G5 in 1 of the 22 (AUDIT-004 at line 13). Read as written, no row with an internal `N2` label records the pre-registration that the `N2` definition asks for. This is a reading of the protocol text by the compiler of this index. It is not a ruling by the `verifier` or by the outside team.

## How the counts here were made

The Gates lists come from the fifth column ("Gates Tested") of each row in `AUDIT_LOG.md`, read on 2026-11-24 at commit `9729839`. Only the gate numbers G1 to G9 are read; the R1 to R5 contracts in brackets are not gates. The worst-case trace-slack figure was recomputed in exact arithmetic for the worst case that `rulings.json` twoloop-stack F5 names, noise aligned with the known component, in the setting stated in `outside/checks/twoloop_stack/advocate_trace_slack.py` (`n = 5`, `q = 9/10`, `w = 1/20`). There `w^2/q = 1/360`, the certificate holds at `5 tau = 1/360` with `R = 32761/32019 > 1`, and the crossing is `5 tau = (43 - sqrt(1838))/44 = 0.0029113...`, which is 1.04807... times 1/360.

## Provenance of this file

Compiled on 2026-11-24 by an automated agent session, as a proposed change for the repository owner's review, from the files cited in each row. No human had reviewed it when it was written.
