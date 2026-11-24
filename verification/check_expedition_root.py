#!/usr/bin/env python3
"""Compare an EXPEDITION_ROOT layout with the byte pins in verification/expedition_root.pins.json.

What it reports, per entry:
  OK          a present file (or clone HEAD) matches a value the ledger row records
  MISMATCH    the row says it hashed a file, every candidate file is present, and none matches;
              or the clone named for a commit pin is at a different HEAD
  NOT_SHOWN   nothing to compare: the file or clone is absent, git cannot read HEAD, or the row
              does not say whether its value hashes file bytes or an output
  UNRECORDED  the row records no byte pin at all
Post-audit reference entries are public bytes committed after the audits. They are reported
(REFERENCE_MATCH, BEFORE_AUDIT_MATCH, REFERENCE_DIFFERS) but never fail the run, because they are
not the audited bytes.

Before comparing anything it checks the manifest against the ledger: strict JSON, every audited
value present on the ledger line it names, and every audit row listed exactly once across
'audited' and 'unrecorded' and once in 'replay_class'.

Exit codes: 0 no MISMATCH; 1 at least one MISMATCH; 2 manifest or ledger malformed.
Root: --root, else the EXPEDITION_ROOT environment variable, else this repository's root (the
default the check scripts use). A bare clone therefore reports NOT_SHOWN for every file.
Run: python3 -I -B verification/check_expedition_root.py   (also -I -O -B and -I -B -W error)
Needs: Python 3 standard library; git only for commit pins.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PINS = REPO_ROOT / "verification" / "expedition_root.pins.json"
DEFAULT_LEDGER = REPO_ROOT / "verification" / "AUDIT_LOG.md"

SHA256_FULL = re.compile(r"[0-9a-f]{64}\Z")
SHA256_PREFIX = re.compile(r"[0-9a-f]{7,63}\Z")
COMMIT_FULL = re.compile(r"[0-9a-f]{40}\Z")
COMMIT_PREFIX = re.compile(r"[0-9a-f]{7,40}\Z")
ROW_LABEL = re.compile(r"\| \*\*(AUDIT-[^*]+)\*\* \|")
CLASSES = ("bare-clone", "needs EXPEDITION_ROOT", "needs private transcripts")


class Malformed(ValueError):
    """The manifest or the ledger cannot be read as this checker expects."""


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise Malformed(f"duplicate JSON key {key!r}")
        out[key] = value
    return out


def _no_float(text: str) -> Any:
    raise Malformed(f"float {text} in manifest")


def _no_constant(text: str) -> Any:
    raise Malformed(f"non-finite constant {text} in manifest")


def load_pins(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise Malformed(f"cannot read manifest: {exc}") from None
    try:
        data = json.loads(raw, object_pairs_hook=_no_duplicates, parse_float=_no_float, parse_constant=_no_constant)
    except json.JSONDecodeError as exc:
        raise Malformed(f"manifest is not JSON: {exc}") from None
    if not isinstance(data, dict):
        raise Malformed("manifest top level must be an object")
    return data


def ledger_rows(path: Path) -> dict[int, tuple[str, str]]:
    """Map 1-based line number to (row label, line text) for every audit row of the ledger."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise Malformed(f"cannot read ledger: {exc}") from None
    rows = {}
    for number, line in enumerate(lines, start=1):
        match = ROW_LABEL.match(line)
        if match:
            rows[number] = (match.group(1), line)
    if not rows:
        raise Malformed("ledger has no audit rows")
    return rows


def _need(cond: bool, msg: str) -> None:
    if not cond:
        raise Malformed(msg)


def _rel_path(value: Any, where: str) -> str:
    _need(type(value) is str and value != "", f"{where}: path must be a non-empty string")
    pure = PurePosixPath(value)
    _need(not pure.is_absolute() and "\\" not in value and ".." not in pure.parts, f"{where}: path {value!r} must be relative")
    return value


def _row(entry: dict[str, Any], rows: dict[int, tuple[str, str]], where: str) -> int:
    line = entry.get("audit_log_line")
    _need(type(line) is int and line in rows, f"{where}: audit_log_line {line!r} is not an audit row of the ledger")
    _need(entry.get("row_label") == rows[line][0], f"{where}: row_label {entry.get('row_label')!r} does not match ledger line {line} ({rows[line][0]})")
    return line


def validate(data: dict[str, Any], rows: dict[int, tuple[str, str]]) -> None:
    for key in ("audited", "post_audit_reference", "unrecorded", "replay_class"):
        _need(type(data.get(key)) is list, f"section {key!r} must be a list")
    pinned_lines: set[int] = set()
    for i, entry in enumerate(data["audited"]):
        where = f"audited[{i}]"
        _need(type(entry) is dict, f"{where}: must be an object")
        line = _row(entry, rows, where)
        pin, value = entry.get("pin"), entry.get("value")
        pattern = {"full": SHA256_FULL, "prefix": SHA256_PREFIX, "commit_prefix": COMMIT_PREFIX}.get(pin)
        _need(pattern is not None, f"{where}: pin must be full, prefix or commit_prefix")
        _need(type(value) is str and pattern.match(value) is not None, f"{where}: value {value!r} is not a valid {pin}")
        _need(value in rows[line][1], f"{where}: value {value} does not appear on ledger line {line}")
        if pin == "commit_prefix":
            _rel_path(entry.get("clone"), where)
        else:
            _need(entry.get("hashes") in ("file", "not stated"), f"{where}: hashes must be 'file' or 'not stated'")
            paths = entry.get("candidate_paths")
            _need(type(paths) is list and len(paths) > 0, f"{where}: candidate_paths must be a non-empty list")
            for p in paths:
                _rel_path(p, where)
        pinned_lines.add(line)
    unrecorded_lines: set[int] = set()
    for i, entry in enumerate(data["unrecorded"]):
        where = f"unrecorded[{i}]"
        _need(type(entry) is dict, f"{where}: must be an object")
        line = _row(entry, rows, where)
        _need(line not in unrecorded_lines, f"{where}: ledger line {line} listed twice")
        unrecorded_lines.add(line)
    _need(not (pinned_lines & unrecorded_lines), f"ledger lines both pinned and unrecorded: {sorted(pinned_lines & unrecorded_lines)}")
    missing = sorted(set(rows) - pinned_lines - unrecorded_lines)
    _need(not missing, f"ledger lines in neither 'audited' nor 'unrecorded': {missing}")
    for i, entry in enumerate(data["post_audit_reference"]):
        where = f"post_audit_reference[{i}]"
        _need(type(entry) is dict, f"{where}: must be an object")
        _need(type(entry.get("label")) is str and "not the audited bytes" in entry["label"], f"{where}: label must say these are not the audited bytes")
        _need(type(entry.get("commit")) is str and COMMIT_FULL.match(entry["commit"]) is not None, f"{where}: commit must be 40 hex digits")
        _need(type(entry.get("sha256")) is str and SHA256_FULL.match(entry["sha256"]) is not None, f"{where}: sha256 must be 64 hex digits")
        paths = entry.get("paths")
        _need(type(paths) is list and len(paths) > 0, f"{where}: paths must be a non-empty list")
        for p in paths:
            _rel_path(p, where)
        before = entry.get("before_audit")
        if before is not None:
            _need(type(before) is dict and type(before.get("sha256")) is str and SHA256_FULL.match(before["sha256"]) is not None, f"{where}: before_audit.sha256 must be 64 hex digits")
            _need("not recorded" in str(before.get("label")), f"{where}: before_audit label must say it is not recorded")
    labels = [label for label, _ in rows.values()]
    classed = []
    for i, entry in enumerate(data["replay_class"]):
        where = f"replay_class[{i}]"
        _need(type(entry) is dict and entry.get("class") in CLASSES, f"{where}: class must be one of {list(CLASSES)}")
        classed.append(entry.get("row_label"))
    _need(sorted(classed) == sorted(labels), "replay_class must list every ledger row label exactly once")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clone_head(clone: Path) -> tuple[str | None, str]:
    """Return (HEAD, '') for the top of a git work tree, else (None, reason)."""
    if not clone.is_dir():
        return None, "absent"
    try:
        top = subprocess.run(["git", "-C", str(clone), "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False)
        if top.returncode != 0:
            return None, "not a git work tree"
        if Path(top.stdout.strip()).resolve() != clone.resolve():
            return None, "inside another git work tree, not a clone of its own"
        head = subprocess.run(["git", "-C", str(clone), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    except OSError:
        return None, "git not available"
    if head.returncode != 0:
        return None, "git cannot read HEAD"
    return head.stdout.strip(), ""


def check_audited(entry: dict[str, Any], root: Path) -> tuple[str, str]:
    pin, value = entry["pin"], entry["value"]
    if pin == "commit_prefix":
        head, reason = clone_head(root / entry["clone"])
        if head is None:
            return "NOT_SHOWN", f"{entry['clone']}: {reason}"
        if head.startswith(value):
            return "OK", f"{entry['clone']} HEAD {head[:12]}"
        return "MISMATCH", f"{entry['clone']} HEAD {head[:12]} is not {value}"
    present = [(p, sha256_file(root / p)) for p in entry["candidate_paths"] if (root / p).is_file()]
    for p, digest in present:
        if digest.startswith(value):
            return "OK", f"file bytes of {p}"
    if not present:
        return "NOT_SHOWN", "absent: " + ", ".join(entry["candidate_paths"])
    if entry["hashes"] == "file" and len(present) == len(entry["candidate_paths"]):
        return "MISMATCH", "no candidate file matches: " + ", ".join(f"{p} {d[:12]}" for p, d in present)
    if entry["hashes"] == "file":
        return "NOT_SHOWN", "present candidates differ, others absent: " + ", ".join(p for p, _ in present)
    return "NOT_SHOWN", "file bytes differ; the row does not say it hashed the file: " + ", ".join(p for p, _ in present)


def check_reference(entry: dict[str, Any], path: str, root: Path) -> tuple[str, str]:
    target = root / path
    if not target.is_file():
        return "NOT_SHOWN", "absent"
    digest = sha256_file(target)
    if digest == entry["sha256"]:
        return "REFERENCE_MATCH", f"{entry['repository']} {entry['commit'][:7]}"
    before = entry.get("before_audit")
    if before is not None and digest == before["sha256"]:
        return "BEFORE_AUDIT_MATCH", f"{entry['repository']} {str(before.get('commit'))[:7]} (probable, not recorded)"
    return "REFERENCE_DIFFERS", digest[:12]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare an EXPEDITION_ROOT layout with the byte pins in verification/expedition_root.pins.json.")
    parser.add_argument("--root", help="EXPEDITION_ROOT to inspect (default: $EXPEDITION_ROOT, else this repository)")
    parser.add_argument("--pins", default=str(DEFAULT_PINS), help="pin manifest (default: %(default)s)")
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER), help="audit ledger (default: %(default)s)")
    args = parser.parse_args(argv)
    if args.root:
        root, source = Path(args.root), "--root argument"
    elif os.environ.get("EXPEDITION_ROOT"):
        root, source = Path(os.environ["EXPEDITION_ROOT"]), "EXPEDITION_ROOT"
    else:
        root, source = REPO_ROOT, "default (this repository's root)"
    try:
        data = load_pins(Path(args.pins))
        rows = ledger_rows(Path(args.ledger))
        validate(data, rows)
    except Malformed as exc:
        print(f"MALFORMED: {exc}")
        print("RESULT check_expedition_root: MALFORMED")
        return 2

    print(f"root: {source}")
    print("AUDITED (values the ledger rows record)")
    audited = Counter()
    for entry in data["audited"]:
        status, detail = check_audited(entry, root)
        audited[status] += 1
        print(f"  {status:<10} line {entry['audit_log_line']} {entry['row_label']} {entry['pin']} {entry['value'][:12]}: {detail}")
    print("POST-AUDIT REFERENCE (public bytes committed after the audits; not the audited bytes)")
    references = Counter()
    for entry in data["post_audit_reference"]:
        for path in entry["paths"]:
            status, detail = check_reference(entry, path, root)
            references[status] += 1
            print(f"  {status:<18} {path}: {detail}")
    print("UNRECORDED (the ledger row records no byte pin)")
    for entry in data["unrecorded"]:
        print(f"  UNRECORDED line {entry['audit_log_line']} {entry['row_label']}")
    print("REPLAY CLASS (rows per class)")
    by_class: dict[str, list[str]] = {c: [] for c in CLASSES}
    for entry in data["replay_class"]:
        by_class[entry["class"]].append(entry["row_label"])
    for name in CLASSES:
        print(f"  {name}: {len(by_class[name])}")
    status = "MISMATCH" if audited["MISMATCH"] else "NO_MISMATCH"
    print(
        f"RESULT check_expedition_root: {status} (audited: {audited['OK']} OK, {audited['MISMATCH']} MISMATCH, "
        f"{audited['NOT_SHOWN']} NOT_SHOWN; references: {references['REFERENCE_MATCH']} match, "
        f"{references['BEFORE_AUDIT_MATCH']} before-audit match, {references['REFERENCE_DIFFERS']} differ, "
        f"{references['NOT_SHOWN']} not shown; unrecorded rows: {len(data['unrecorded'])})"
    )
    return 1 if audited["MISMATCH"] else 0


if __name__ == "__main__":
    sys.exit(main())
