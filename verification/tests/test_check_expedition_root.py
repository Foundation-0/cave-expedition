#!/usr/bin/env python3
"""Controls for verification/check_expedition_root.py and its pin manifest.

Every control runs the checker as a subprocess against a temporary EXPEDITION_ROOT, so no
sibling file is needed and none is written outside the temporary directory.

Run (all three R4 modes):
  python3 -I -B verification/tests/test_check_expedition_root.py
  python3 -I -O -B verification/tests/test_check_expedition_root.py
  python3 -I -B -W error verification/tests/test_check_expedition_root.py
Needs: Python 3 standard library and git (for the commit-pin controls). Takes about 1 second.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

VERIFICATION = Path(__file__).resolve().parents[1]
CHECKER = VERIFICATION / "check_expedition_root.py"
PINS = VERIFICATION / "expedition_root.pins.json"
LEDGER = VERIFICATION / "AUDIT_LOG.md"
MODES = (["-I", "-B"], ["-I", "-O", "-B"], ["-I", "-B", "-W", "error"])


def _load_checker():
    spec = importlib.util.spec_from_file_location("cave_check_expedition_root_under_test", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CHECKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CER = _load_checker()


def run_checker(root: Path, *extra: str, flags=("-I", "-B"), env=None):
    return subprocess.run(
        [sys.executable, *flags, str(CHECKER), "--root", str(root), *extra],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


class ExpeditionRootChecker(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.root = self.tmp / "root"
        self.root.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def put(self, rel: str, data: bytes) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def test_bare_root_is_not_shown_and_identical_in_three_modes(self):
        runs = [run_checker(self.root, flags=flags) for flags in MODES]
        for run in runs:
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(runs[0].stdout, runs[1].stdout)
        self.assertEqual(runs[0].stdout, runs[2].stdout)
        lines = runs[0].stdout.splitlines()
        self.assertIn("  NOT_SHOWN  line 20 AUDIT-011 prefix fa4d3a1b: absent: probes/gravity/probe1_aest_helmholtz_closure.py", lines)
        self.assertIn("  NOT_SHOWN  line 27 AUDIT-015R / 016R commit_prefix dfc8516: branches/spectral-inertia: absent", lines)
        self.assertTrue(lines[-1].startswith("RESULT check_expedition_root: NO_MISMATCH (audited: 0 OK, 0 MISMATCH, 9 NOT_SHOWN;"), lines[-1])
        self.assertTrue(lines[-1].endswith("unrecorded rows: 15)"), lines[-1])

    def test_must_fail_wrong_bytes_for_the_full_hash(self):
        # AUDIT-018 records a full file SHA-256. With both named files present and
        # neither matching, the run must fail.
        self.put("probes/gravity/probe4_witness_zeno_schur.py", b"print('not the audited bytes')\n")
        self.put("probes/gravity/probe4_witness_zeno_results.json", b"{}\n")
        run = run_checker(self.root)
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertIn("  MISMATCH   line 29 AUDIT-018 full 899d65178959: no candidate file matches:", run.stdout)
        self.assertIn("RESULT check_expedition_root: MISMATCH (audited: 0 OK, 1 MISMATCH, 8 NOT_SHOWN;", run.stdout)

    def test_one_named_file_absent_is_not_a_mismatch(self):
        self.put("probes/gravity/probe4_witness_zeno_schur.py", b"print('not the audited bytes')\n")
        run = run_checker(self.root)
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertIn("  NOT_SHOWN  line 29 AUDIT-018 full 899d65178959: present candidates differ, others absent:", run.stdout)

    def test_commit_pin_compares_clone_head(self):
        clone = self.root / "branches" / "spectral-inertia"
        clone.mkdir(parents=True)
        (clone / "run_all.py").write_text("print('x')\n", encoding="utf-8")
        git = ["git", "-C", str(clone), "-c", "user.name=control", "-c", "user.email=control@example.invalid"]
        for cmd in (["init", "-q"], ["add", "run_all.py"], ["commit", "-q", "-m", "control"]):
            subprocess.run(git + cmd, check=True, capture_output=True)
        run = run_checker(self.root)
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertRegex(run.stdout, r"  MISMATCH   line 27 AUDIT-015R / 016R commit_prefix dfc8516: branches/spectral-inertia HEAD [0-9a-f]{12} is not dfc8516")

    def clone_line(self, env=None) -> str:
        run = run_checker(self.root, env=env)
        line = [x for x in run.stdout.splitlines() if " line 27 " in x]
        self.assertEqual(len(line), 1, run.stdout)
        return run.returncode, line[0]

    def test_clone_cases_that_cannot_be_compared(self):
        clone = self.root / "branches" / "spectral-inertia"
        clone.mkdir(parents=True)
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(self.tmp))
        prefix = "  NOT_SHOWN  line 27 AUDIT-015R / 016R commit_prefix dfc8516: branches/spectral-inertia: "
        self.assertEqual(self.clone_line(env), (0, prefix + "not a git work tree"))
        subprocess.run(["git", "-C", str(clone), "init", "-q"], check=True, capture_output=True, env=env)
        self.assertEqual(self.clone_line(env), (0, prefix + "git cannot read HEAD"))
        shutil.rmtree(clone / ".git")
        subprocess.run(["git", "-C", str(self.root), "init", "-q"], check=True, capture_output=True, env=env)
        self.assertEqual(self.clone_line(env), (0, prefix + "inside another git work tree, not a clone of its own"))

    def test_reference_difference_never_fails(self):
        self.put("repos/project-asma/formal/AsmaIdentifiabilityProofs.lean", b"-- other bytes\n")
        run = run_checker(self.root)
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertRegex(run.stdout, r"  REFERENCE_DIFFERS  repos/project-asma/formal/AsmaIdentifiabilityProofs\.lean: [0-9a-f]{12}")

    def malformed(self, data) -> str:
        pins = self.tmp / "pins.json"
        pins.write_text(json.dumps(data), encoding="utf-8")
        run = run_checker(self.root, "--pins", str(pins))
        self.assertEqual(run.returncode, 2, run.stdout)
        self.assertEqual(run.stdout.splitlines()[-1], "RESULT check_expedition_root: MALFORMED")
        return run.stdout.splitlines()[0]

    def test_malformed_manifest(self):
        data = json.loads(PINS.read_text(encoding="utf-8"))
        changed = json.loads(json.dumps(data))
        changed["audited"][0]["value"] = "deadbeef"
        self.assertEqual(self.malformed(changed), "MALFORMED: audited[0]: value deadbeef does not appear on ledger line 20")
        changed = json.loads(json.dumps(data))
        changed["unrecorded"] = changed["unrecorded"][1:]
        self.assertEqual(self.malformed(changed), "MALFORMED: ledger lines in neither 'audited' nor 'unrecorded': [10]")
        self.assertEqual(self.malformed([]), "MALFORMED: manifest top level must be an object")
        empty_ledger = self.tmp / "ledger.md"
        empty_ledger.write_text("# no rows\n", encoding="utf-8")
        run = run_checker(self.root, "--ledger", str(empty_ledger))
        self.assertEqual((run.returncode, run.stdout.splitlines()[0]), (2, "MALFORMED: ledger has no audit rows"))
        duplicate = self.tmp / "dup.json"
        duplicate.write_text(PINS.read_text(encoding="utf-8").replace('"schema":', '"schema": "x", "schema":', 1), encoding="utf-8")
        run = run_checker(self.root, "--pins", str(duplicate))
        self.assertEqual((run.returncode, run.stdout.splitlines()[0]), (2, "MALFORMED: duplicate JSON key 'schema'"))



def _set(path, value):
    """Return an edit that sets the item at path in the manifest to value."""

    def edit(data):
        target = data
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value

    return edit


class ManifestValidation(unittest.TestCase):
    """Each manifest refusal, driven in-process on a corrupted copy of the real manifest."""

    CASES = (
        (_set(("audited",), {}), "section 'audited' must be a list"),
        (_set(("audited", 0), "x"), "audited[0]: must be an object"),
        (_set(("audited", 0, "audit_log_line"), 9), "audited[0]: audit_log_line 9 is not an audit row of the ledger"),
        (_set(("audited", 0, "row_label"), "AUDIT-999"), "audited[0]: row_label 'AUDIT-999' does not match ledger line 20 (AUDIT-011)"),
        (_set(("audited", 0, "pin"), "partial"), "audited[0]: pin must be full, prefix or commit_prefix"),
        (_set(("audited", 0, "value"), "FA4D3A1B"), "audited[0]: value 'FA4D3A1B' is not a valid prefix"),
        (_set(("audited", 0, "hashes"), "maybe"), "audited[0]: hashes must be 'file' or 'not stated'"),
        (_set(("audited", 0, "candidate_paths"), []), "audited[0]: candidate_paths must be a non-empty list"),
        (_set(("audited", 0, "candidate_paths"), [""]), "audited[0]: path must be a non-empty string"),
        (_set(("audited", 0, "candidate_paths"), ["../x.py"]), "audited[0]: path '../x.py' must be relative"),
        (_set(("audited", 4, "clone"), None), "audited[4]: path must be a non-empty string"),
        (_set(("unrecorded", 0), "x"), "unrecorded[0]: must be an object"),
        (lambda d: d["unrecorded"].append(dict(d["unrecorded"][0])), "unrecorded[15]: ledger line 10 listed twice"),
        (
            lambda d: d["unrecorded"].append({"row_label": "AUDIT-011", "audit_log_line": 20}),
            "ledger lines both pinned and unrecorded: [20]",
        ),
        (_set(("post_audit_reference", 0), "x"), "post_audit_reference[0]: must be an object"),
        (_set(("post_audit_reference", 0, "label"), "public bytes"), "post_audit_reference[0]: label must say these are not the audited bytes"),
        (_set(("post_audit_reference", 0, "commit"), "94b70f3"), "post_audit_reference[0]: commit must be 40 hex digits"),
        (_set(("post_audit_reference", 0, "sha256"), "25dcb2e7"), "post_audit_reference[0]: sha256 must be 64 hex digits"),
        (_set(("post_audit_reference", 0, "paths"), []), "post_audit_reference[0]: paths must be a non-empty list"),
        (
            _set(("post_audit_reference", 0, "before_audit", "sha256"), "be155493"),
            "post_audit_reference[0]: before_audit.sha256 must be 64 hex digits",
        ),
        (
            _set(("post_audit_reference", 0, "before_audit", "label"), "last public version"),
            "post_audit_reference[0]: before_audit label must say it is not recorded",
        ),
        (
            _set(("replay_class", 0, "class"), "easy"),
            "replay_class[0]: class must be one of ['bare-clone', 'needs EXPEDITION_ROOT', 'needs private transcripts']",
        ),
        (lambda d: d["replay_class"].pop(), "replay_class must list every ledger row label exactly once"),
    )

    def test_real_manifest_is_valid(self):
        self.assertIsNone(CER.validate(CER.load_pins(PINS), CER.ledger_rows(LEDGER)))

    def test_each_refusal(self):
        rows = CER.ledger_rows(LEDGER)
        for edit, message in self.CASES:
            with self.subTest(message=message):
                data = CER.load_pins(PINS)
                edit(data)
                with self.assertRaises(CER.Malformed) as ctx:
                    CER.validate(data, rows)
                self.assertEqual(str(ctx.exception), message)


if __name__ == "__main__":
    if shutil.which("git") is None:
        sys.exit("git is required for the commit-pin control")
    unittest.main()
