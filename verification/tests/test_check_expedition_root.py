#!/usr/bin/env python3
"""Controls for verification/check_expedition_root.py and its pin manifest.

The controls run the checker against a temporary EXPEDITION_ROOT, as a subprocess or in process,
so no sibling file is needed and none is written outside the temporary directory. The positive
control for AUDIT-018 copies the outside Gate-5 check's copy of probe4_witness_zeno_results.json
(read only) into that directory.

Run (all three R4 modes):
  python3 -I -B verification/tests/test_check_expedition_root.py
  python3 -I -O -B verification/tests/test_check_expedition_root.py
  python3 -I -B -W error verification/tests/test_check_expedition_root.py
Needs: Python 3 standard library and git (for the commit-pin controls). Takes about 2 seconds.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

VERIFICATION = Path(__file__).resolve().parents[1]
CHECKER = VERIFICATION / "check_expedition_root.py"
PINS = VERIFICATION / "expedition_root.pins.json"
LEDGER = VERIFICATION / "AUDIT_LOG.md"
# The outside Gate-5 check kept this copy of the probe 4 results; its bytes are the ones AUDIT-018 records.
PROBE4_COPY = VERIFICATION / "outside" / "gate5-unification" / "hermitian" / "out" / "anchor_fractals" / "probe4_witness_zeno_results.json"
PROBE1 = "probes/gravity/probe1_aest_results.json"
PROBE4 = "probes/gravity/probe4_witness_zeno_results.json"
# A small JSON object and its canonical form, written out by hand: sorted keys, compact
# separators, non-ASCII escaped (json.dumps defaults, as check_007 and check_011 use them).
SAMPLE = {"b": [1, 2.5, "\u00e9"], "a": {"z": None}}
SAMPLE_CANONICAL = b'{"a":{"z":null},"b":[1,2.5,"\\u00e9"]}'
SAMPLE_DIGEST = hashlib.sha256(SAMPLE_CANONICAL).hexdigest()
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
        self.assertIn(f"  NOT_SHOWN  line 20 AUDIT-011 prefix fa4d3a1b: {PROBE1}: absent", lines)
        self.assertIn("  NOT_SHOWN  line 27 AUDIT-015R / 016R commit_prefix dfc8516: branches/spectral-inertia: absent", lines)
        self.assertTrue(lines[-1].startswith("RESULT check_expedition_root: NO_MISMATCH (audited: 0 OK, 0 OTHER_ROW, 0 MISMATCH, 9 NOT_SHOWN;"), lines[-1])
        self.assertTrue(lines[-1].endswith("unrecorded rows: 15)"), lines[-1])

    def test_positive_control_audited_probe4_bytes(self):
        # Real audited bytes: AUDIT-018's full file SHA-256 must come out OK.
        self.put(PROBE4, PROBE4_COPY.read_bytes())
        run = run_checker(self.root)
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertIn(f"  OK         line 29 AUDIT-018 full 899d65178959: file bytes of {PROBE4}", run.stdout.splitlines())
        self.assertIn("RESULT check_expedition_root: NO_MISMATCH (audited: 1 OK, 0 OTHER_ROW, 0 MISMATCH, 8 NOT_SHOWN;", run.stdout)

    def test_must_fail_wrong_bytes_for_the_full_hash(self):
        data = PROBE4_COPY.read_bytes() + b"\n"
        self.put(PROBE4, data)
        run = run_checker(self.root)
        self.assertEqual(run.returncode, 1, run.stdout)
        digest = hashlib.sha256(data).hexdigest()
        self.assertIn(
            f"  MISMATCH   line 29 AUDIT-018 full 899d65178959: file bytes of {PROBE4} is {digest[:12]}, which no audited row records for it",
            run.stdout.splitlines(),
        )
        self.assertIn("RESULT check_expedition_root: MISMATCH (audited: 0 OK, 0 OTHER_ROW, 1 MISMATCH, 8 NOT_SHOWN;", run.stdout)

    def test_canonical_digest_matches_the_hand_written_form(self):
        # Keys out of order, indented, non-ASCII kept raw: only the canonical form is hashed.
        body = {"sha256_canonical": SAMPLE_DIGEST, **SAMPLE}
        self.put("x.json", json.dumps(body, indent=2, ensure_ascii=False).encode("utf-8"))
        self.assertEqual(CER.file_digest(self.root / "x.json", "canonical JSON"), (SAMPLE_DIGEST, ""))
        self.assertEqual(CER.file_digest(self.root / "x.json", "file bytes")[0], hashlib.sha256((self.root / "x.json").read_bytes()).hexdigest())

    def test_must_fail_canonical_json_no_row_records(self):
        # A self-consistent results file whose canonical hash is neither row's value.
        self.put(PROBE1, json.dumps({**SAMPLE, "sha256_canonical": SAMPLE_DIGEST}).encode("utf-8"))
        run = run_checker(self.root)
        self.assertEqual(run.returncode, 1, run.stdout)
        lines = run.stdout.splitlines()
        tail = f"canonical JSON of {PROBE1} is {SAMPLE_DIGEST[:12]}, which no audited row records for it"
        self.assertIn(f"  MISMATCH   line 20 AUDIT-011 prefix fa4d3a1b: {tail}", lines)
        self.assertIn(f"  MISMATCH   line 28 AUDIT-011R / 013R prefix bcde49380e: {tail}", lines)
        self.assertIn("RESULT check_expedition_root: MISMATCH (audited: 0 OK, 0 OTHER_ROW, 2 MISMATCH, 7 NOT_SHOWN;", run.stdout)

    def test_must_fail_files_the_check_scripts_would_refuse(self):
        cases = (
            (b"\xff\n", "not UTF-8 JSON (UnicodeDecodeError)"),
            (b"{\n", "not UTF-8 JSON (JSONDecodeError)"),
            (b"[]\n", "no top-level sha256_canonical field"),
            (json.dumps(SAMPLE).encode("utf-8"), "no top-level sha256_canonical field"),
            (
                json.dumps({**SAMPLE, "sha256_canonical": "bcde49380e"}).encode("utf-8"),
                f"its sha256_canonical field 'bcde49380e' is not the recomputed {SAMPLE_DIGEST[:12]}",
            ),
        )
        for data, why in cases:
            with self.subTest(why=why):
                self.put(PROBE1, data)
                run = run_checker(self.root)
                self.assertEqual(run.returncode, 1, run.stdout)
                lines = run.stdout.splitlines()
                self.assertIn(f"  MISMATCH   line 20 AUDIT-011 prefix fa4d3a1b: {PROBE1}: {why}; check_007_gravity_probes.py would refuse it", lines)
                self.assertIn(f"  MISMATCH   line 28 AUDIT-011R / 013R prefix bcde49380e: {PROBE1}: {why}; check_011_gravity_reaudit_and_probe4.py would refuse it", lines)

    def test_other_row_is_reported_and_does_not_fail(self):
        # AUDIT-011 and AUDIT-011R pin two versions of probe 1's results. No real file with
        # either hash is at hand, so the digest is patched in to the value line 28 records.
        self.put(PROBE1, b"{}\n")
        out = io.StringIO()
        with mock.patch.object(CER, "file_digest", return_value=("bcde49380e" + "0" * 54, "")), contextlib.redirect_stdout(out):
            code = CER.main(["--root", str(self.root)])
        self.assertEqual(code, 0, out.getvalue())
        lines = out.getvalue().splitlines()
        self.assertIn(f"  OTHER_ROW  line 20 AUDIT-011 prefix fa4d3a1b: canonical JSON of {PROBE1} matches line 28 AUDIT-011R / 013R bcde49380e instead", lines)
        self.assertIn(f"  OK         line 28 AUDIT-011R / 013R prefix bcde49380e: canonical JSON of {PROBE1}", lines)
        self.assertIn("RESULT check_expedition_root: NO_MISMATCH (audited: 1 OK, 1 OTHER_ROW, 0 MISMATCH, 7 NOT_SHOWN;", lines[-1])

    def test_commit_pin_compares_clone_head(self):
        clone = self.root / "branches" / "spectral-inertia"
        clone.mkdir(parents=True)
        (clone / "run_all.py").write_text("print('x')\n", encoding="utf-8")
        git = ["git", "-C", str(clone), "-c", "user.name=control", "-c", "user.email=control@example.invalid", "-c", "commit.gpgsign=false"]
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

    def test_must_fail_unreadable_inputs_and_missing_root(self):
        # A manifest or ledger that is not valid UTF-8 is MALFORMED (exit 2), not a traceback (exit 1,
        # the MISMATCH code).
        bad_pins = self.tmp / "latin1.json"
        bad_pins.write_bytes(b'{"schema": "\xff"}')
        run = run_checker(self.root, "--pins", str(bad_pins))
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertTrue(run.stdout.startswith("MALFORMED: cannot read manifest:"), run.stdout)
        self.assertEqual(run.stderr, "")
        bad_ledger = self.tmp / "latin1.md"
        bad_ledger.write_bytes(b"| **`AUDIT-001`** | \xff |\n")
        run = run_checker(self.root, "--ledger", str(bad_ledger))
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertTrue(run.stdout.startswith("MALFORMED: cannot read ledger:"), run.stdout)
        # A root that does not exist must not report a clean run.
        missing = self.tmp / "no-such-root"
        run = run_checker(missing)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertEqual(run.stdout.splitlines()[0], f"MALFORMED: root {missing} (--root argument) is not a directory")
        self.assertEqual(run.stdout.splitlines()[-1], "RESULT check_expedition_root: MALFORMED")



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
        (
            _set(("audited", 0, "ledger_words"), "SHA-256 `fa4d3a1b` for probe1"),
            "audited[0]: ledger_words must quote ledger line 20 around the value",
        ),
        (_set(("audited", 0, "hash_kind"), "sha256"), "audited[0]: hash_kind must be one of ['canonical JSON', 'file bytes']"),
        (_set(("audited", 0, "path"), ""), "audited[0]: path must be a non-empty string"),
        (_set(("audited", 0, "path"), "../x.json"), "audited[0]: path '../x.json' must be relative"),
        (_set(("audited", 0, "basis"), "check_007"), "audited[0]: basis must be an object"),
        (
            _set(("audited", 0, "basis", "script"), "verification/checks/check_999.py"),
            "audited[0]: cannot read basis script verification/checks/check_999.py",
        ),
        (_set(("audited", 0, "basis", "lines"), []), "audited[0]: basis lines must be a non-empty list of [first, last] pairs"),
        (
            _set(("audited", 0, "basis", "lines"), [[89, 82]]),
            "audited[0]: basis lines [89, 82] are not a line range of verification/checks/check_007_gravity_probes.py",
        ),
        (_set(("audited", 0, "basis", "lines"), [[64, 64], [82, 89]]), "audited[0]: value fa4d3a1b is not on the cited lines of the basis script"),
        (
            _set(("audited", 0, "path"), "probes/gravity/probe1_aest_helmholtz_closure.py"),
            "audited[0]: file name probe1_aest_helmholtz_closure.py is not on the cited lines of the basis script",
        ),
        (
            _set(("audited", 0, "path"), "probes/fractals/probe1_aest_results.json"),
            "audited[0]: folder probes/fractals is not on the cited lines of the basis script",
        ),
        (_set(("audited", 0, "hash_kind"), "file bytes"), "audited[0]: the cited lines do not show the file bytes recipe (no read_bytes())"),
        (
            _set(("audited", 3, "hash_kind"), "canonical JSON"),
            'audited[3]: the cited lines do not show the canonical JSON recipe (no pop("sha256_canonical") or sort_keys=True, separators=(",", ":"))',
        ),
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
