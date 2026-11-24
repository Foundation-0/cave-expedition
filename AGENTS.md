# Agent guidance (draft for the owner)

**Status: draft, proposed 2026-11-24. The repository owner decides whether to adopt it.** Items with a "Source:" restate something a file in this repository already says, and name that file. Items marked **(proposal)** are new: either no file in this repository states them, or they go further than their source. Each proposal says where the idea comes from. Where this file and a source disagree, the source wins.

Several teams of agents write into this repository: the expedition team, the outside observer (`verification/outside/`) and the symbiosis rounds (`symbiosis/`). These rules are meant to keep the record honest for all of them.

## The ledger is permanent

- Log pre-registered predictions and misses in `verification/AUDIT_LOG.md` for good: "never delete or retroactively rewrite misses". Source: `verification/PROTOCOL.md`, Gate 8 (line 103); `verification/AUDIT_LOG.md`, line 4. The README calls the log the "Permanent chronological ledger of all audits" (section 3) and says failed and partial audits "are logged permanently" (opening note).
- **(proposal)** Never delete or rewrite any row of `AUDIT_LOG.md`, whatever its verdict. Gate 8 covers predictions and misses only. The idea comes from the practice the site's ledger page describes: "The ledger did not rewrite its rows" (`docs/ledger/index.html`, section "Outside check").
- **(proposal)** When a later ruling supersedes a sentence the team wrote, keep the old sentence visible, verbatim and dated, and put the ruling after it. The source of the idea covers only the outside team's own rulings: "Rulings that were replaced stay on record in `RULINGS.json` ... with the old text verbatim" (`verification/outside/gate5-unification/README.md`, line 138). README sections 1 and 2 follow this form.
- **(proposal)** Do not add a table to `AUDIT_LOG.md` whose first cell holds an audit id unless the row is a full ledger row. No file in this repository says this. The reason is outside it: aletheia's audit-log validator reports a table row whose first cell matches `AUDIT-` plus three or four digits and that has fewer than 8 cells as `MALFORMED_AUDIT_ROW` (`aletheia/audit_check.py`, lines 58 and 362, at aletheia commit `a07d7db`). Put per-audit tables in their own file, as `verification/OUTSIDE_RULINGS_INDEX.md` does.

## The outside folder is not the team's

- `verification/outside/` is "a contribution from outside the expedition team. It changes no file of theirs." Its labels are "the observer's reading and are open to correction in the same way the ledger is". Source: `verification/outside/README.md`, line 38.
- **(proposal)** The team does not edit files under `verification/outside/`, and records a disagreement next to the label instead, for example in `verification/OUTSIDE_RULINGS_INDEX.md`. The outside README states only the other direction: the folder changes no file of the team's.

## Labels and citations

- `VERIFIED` means "passed all applicable gates (G1–G8)" (`verification/PROTOCOL.md`, verdict table). `N0` is the default unless prior art and a concrete new part are checked (`PROTOCOL.md`, section 1, item 4, and Gate 9, line 110). Provenance tags are `verified`, `source claim` and `hypothesis` (`PROTOCOL.md`, section 1, item 3). Source: as named in each sentence.
- **(proposal)** When citing a label across repositories, say whose label it is. Other repositories use the same words differently: in Foundation-0/project-asma, `VERIFIED` means a "finite check with a recorded re-run command (not a proof)" (`CONTRIBUTING.md`, line 12, at project-asma commit `de88b12`).
- Cite a ledger row by its audit id, its oracle class and its outside ruling. Do not cite an internal `N2` label on its own for any row other than AUDIT-017. Source: `docs/ledger/index.html`, "How to cite a row". The outside rulings are listed in `verification/OUTSIDE_RULINGS_INDEX.md`.

## Checks and replays

- Run every checker under `python3 -B`, `python3 -O -B` and `python3 -B -W error`. Source: `PROTOCOL.md`, Gate 7, R4. CI runs `check_003_seam01_ropt.py` in those three modes with `-I` added and compares the three outputs byte for byte (`.github/workflows/verify.yml`).
- **(proposal)** Leave audited scripts byte-identical: `verification/checks/check_*.py` and `verify_round10_standalone.py`. No file in this repository states this. What exists: CI compares the stdout of `check_003_seam01_ropt.py` across modes, and the outside Gate-5 check recorded the SHA-256 of that script's bytes and of its stdout (`verification/outside/gate5-unification/hermitian/out/anchor_input_hashes.txt`, line 5, and `anchor_output_hashes_raw.txt`, line 1). No other check script has a recorded hash on `main`. The reason for the proposal: changing a script changes what its recorded audit means.
- Record the exact command, the commit you ran at and the full output; a pass with no recorded command does not count as a replay. Pin each sibling repository to the commit named in the log row before comparing outputs. Source: `docs/reproduce/index.html`, "Folder layout" and "Honesty notes".

## What stays out

- Private raw session transcripts, local scratch files, upstream clones, virtual environments and byte-compiled caches are kept out of the repository, and paths to them go through the environment variables `EXPEDITION_ROOT` and `GEMINI_SESSIONS_DIR`. Source: README section 3, "Deliberately Excluded".
- **(proposal)** Do not post to other repositories, and do not archive raw fetches, from work in this repository. No file in this repository says this. The idea comes from Foundation-0/project-asma `AGENTS.md` at commit `de88b12`: automated sessions "must never post" its outreach draft (lines 31 to 37), and bounded inspection should "keep only aggregates" (lines 25 and 26). The aletheia prompt `prompts/peer-weaver.md` at aletheia commit `a07d7db` asks for the opposite (line 26: archiving raw fetches under `peer-web/raw/`; lines 21 and 32: posting after sign-off). This draft proposes not to adopt that prompt for this field record.

## Disclosure of automated authorship (proposal)

- Only one file here has a disclosure that says which models wrote it: `verification/outside/OUTSIDE_AUDIT.md`, lines 120 to 122. Model names appear elsewhere only in passing, for example `peer-web/PEER_WEB.md`, line 15 (about the master plan on `siliconcordat/.github#5`), and the round-10 reports under `symbiosis/`. The `Author` column of `AUDIT_LOG.md` names agent roles only.
- **(proposal)** Every pull request, and every new ledger row or report written wholly or partly by AI agents, says so, names the agent roles, and names the models used in the pull request description. It also gives the commands that reproduce each claim. Sources of the idea: Foundation-0/project-asma `CONTRIBUTING.md`, lines 16 and 17 at commit `de88b12` ("Disclose AI assistance and models in the pull request"); Foundation-0/aletheia `CONTRIBUTING.md`, line 40 at commit `a07d7db` (automated authorship must be disclosed, with reproducible commands).
- Existing rows are not changed to add this; it would apply forward if the owner adopts it.
