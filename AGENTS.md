# Agent guidance (draft for the owner)

**Status: draft, proposed 2026-11-24. The repository owner decides whether to adopt it.** It collects rules that already exist in this repository, each with its source. The only new item is the disclosure expectation in the last section, marked as a proposal. Where this file and a source disagree, the source wins.

Several teams of agents write into this repository: the expedition team, the outside observer (`verification/outside/`) and the symbiosis rounds (`symbiosis/`). These rules keep the record honest for all of them.

## The ledger is permanent

- Never delete or rewrite a row of `verification/AUDIT_LOG.md`, and log every miss there for good. Source: `verification/PROTOCOL.md`, Gate 8 ("never delete or retroactively rewrite misses"); `verification/AUDIT_LOG.md`, line 4.
- When a later ruling supersedes team text, keep the old text visible, verbatim and dated, and put the ruling after it. Source: `verification/outside/gate5-unification/README.md`, "Ruling history" ("Rulings that were replaced stay on record ... with the old text verbatim"); README sections 1 and 2 follow this form.
- Do not add a table to `AUDIT_LOG.md` whose first cell starts with `AUDIT-` unless it is a full ledger row; the aletheia validator reads such tables as malformed rows. Put per-audit tables in their own file, as `verification/OUTSIDE_RULINGS_INDEX.md` does.

## The outside folder is not the team's

- `verification/outside/` is a contribution from outside the expedition team, and it changes no file of theirs. Its labels are the observer's reading, "open to correction in the same way the ledger is". Source: `verification/outside/README.md`, lines 36 to 38. Do not edit files there. Record a disagreement next to the label, for example in `verification/OUTSIDE_RULINGS_INDEX.md`.

## Labels and citations

- Say whose label you use. Here `VERIFIED` means "passed all applicable gates (G1–G8)" (`verification/PROTOCOL.md`, verdict table). `N0` is the default until prior art and a concrete new part are checked (`PROTOCOL.md`, Gate 9). Provenance tags are `verified`, `source claim` and `hypothesis` (`PROTOCOL.md`, section 1). Other repositories use the same words differently: in Foundation-0/project-asma, for example, VERIFIED means a finite check with a recorded re-run command.
- Cite a ledger row by its audit id, its oracle class and its outside ruling. Do not cite an internal `N2` label on its own for any row other than AUDIT-017. Source: `docs/ledger/index.html`, "How to cite a row". The outside rulings are listed in `verification/OUTSIDE_RULINGS_INDEX.md`.

## Checks and replays

- Run every checker in three modes: `python3 -I -B`, `python3 -I -O -B` and `python3 -I -B -W error`, and compare outputs. Source: `PROTOCOL.md`, Gate 7, R4; `.github/workflows/verify.yml`.
- Leave audited scripts byte-identical: `verification/checks/check_*.py` and `verify_round10_standalone.py`. The stdout of `check_003_seam01_ropt.py` is compared across modes in CI and pinned by the outside Gate-5 anchor (`verification/outside/gate5-unification/hermitian/out/anchor_output_hashes_raw.txt`, line 1). Changing a script changes what its recorded audit means.
- Record the exact command, the commit you ran at and the full output; a pass with no recorded command does not count as a replay. Pin each sibling repository to the commit named in the log row before comparing outputs. Source: `docs/reproduce/index.html`, "Folder layout" and "Honesty notes".

## What stays out

- Keep private raw session transcripts, local scratch files, upstream clones, virtual environments and byte-compiled caches out of the repository, and refer to them only through the environment variables named in README section 3, "Deliberately Excluded".
- Do not post to other repositories or archive raw fetches from here. The aletheia prompt `prompts/peer-weaver.md` does both (lines 26 and 32 at aletheia commit `a07d7db`) and is not adopted for this field record.

## Disclosure of automated authorship (proposal)

- Only one file here says which models produced it: `verification/outside/OUTSIDE_AUDIT.md`, lines 120 to 122. The `Author` column of `AUDIT_LOG.md` names agent roles only.
- Proposed expectation: every pull request, and every new ledger row or report written wholly or partly by AI agents, says so, names the agent roles, and names the models used in the pull request description. It also gives the commands that reproduce each claim. Sources of the idea: Foundation-0/project-asma `CONTRIBUTING.md`, lines 16 and 17 at commit `de88b12` ("Disclose AI assistance and models in the pull request"); Foundation-0/aletheia `CONTRIBUTING.md`, line 40 at commit `a07d7db` (automated authorship must be disclosed, with reproducible commands).
- Existing rows are not changed to add this; it applies forward if the owner adopts it.
