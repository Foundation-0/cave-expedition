#!/usr/bin/env python3
"""Fail if git tracks or stages a path of the default EXPEDITION_ROOT or GEMINI_SESSIONS_DIR layout.

README section 3 says private session dumps and upstream clones stay out of this repository.
The check scripts default EXPEDITION_ROOT to this repository's root, so the documented sibling
layout (synthesis/, probes/, branches/, repos/) lands inside the checkout, and check_001 and
check_002 default GEMINI_SESSIONS_DIR to a working-directory-relative gemini-sessions/. .gitignore
keeps those paths out of `git add`; this guard catches anything added anyway, including with
`git add -f`.

Exit codes: 0 when git lists this tree's files and none matches; 1 when a matching path is
tracked or staged; 2 when the tree was not checked, because an unchecked tree must not pass
(git missing, not a checkout, a git error, or git lists no files here).
Modelled on project-asma tools/check_tracked_study_sources.py, made fail-closed.
Run: python3 -I -B verification/check_tracked_private_paths.py   (also -I -O -B and -I -B -W error)
Needs: Python 3 standard library and git.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# git ls-files prints repository-relative paths with no leading slash.
PATTERNS = (
    # The default EXPEDITION_ROOT is this repository's root, so the sibling layout is top-level.
    re.compile(r"(synthesis|probes|branches|repos)/"),
    # GEMINI_SESSIONS_DIR defaults to a path relative to the working directory, so match at any depth.
    re.compile(r"(.*/)?gemini-sessions/"),
    # Same set as the .gitignore entry gemini-session-*/ (check_002 reads gemini-session-<hex>/).
    re.compile(r"(.*/)?gemini-session-[^/]*/"),
)
UNCHECKED = "the tree was not checked"


class NotListed(RuntimeError):
    """git did not list this tree's files."""


def tracked_paths(root: Path = ROOT) -> list[str]:
    # -z prints each path verbatim; without it git quotes unusual names and the patterns could miss them.
    try:
        done = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=False)
    except OSError as exc:
        raise NotListed(f"cannot run git, so {UNCHECKED} ({exc})") from None
    if done.returncode != 0:
        detail = done.stderr.decode("utf-8", "replace").strip().splitlines()
        raise NotListed(f"git ls-files failed, so {UNCHECKED} ({detail[0] if detail else 'exit ' + str(done.returncode)})")
    paths = [p for p in done.stdout.decode("utf-8", "replace").split("\0") if p]
    if not paths:
        raise NotListed(f"git lists no files here, so {UNCHECKED}")
    return paths


def violations(paths: list[str]) -> list[str]:
    return sorted(p for p in paths if any(pattern.match(p) for pattern in PATTERNS))


def main() -> int:
    try:
        paths = tracked_paths()
    except NotListed as exc:
        print(f"ERROR: {exc}")
        return 2
    found = violations(paths)
    if found:
        print(f"FAIL: {len(found)} tracked or staged path(s) of the private or sibling layout:")
        for path in found:
            print(f"  {path}")
        return 1
    print(f"PASS: none of the {len(paths)} tracked paths is under synthesis/, probes/, branches/, repos/ or a gemini-sessions folder")
    return 0


if __name__ == "__main__":
    sys.exit(main())
