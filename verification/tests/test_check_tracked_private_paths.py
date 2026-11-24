#!/usr/bin/env python3
"""Must-fail controls for verification/check_tracked_private_paths.py.

Each control copies the guard into a fresh temporary git repository, stages paths there and
runs the copy, so this checkout's index is never touched.

Run (all three R4 modes):
  python3 -I -B verification/tests/test_check_tracked_private_paths.py
  python3 -I -O -B verification/tests/test_check_tracked_private_paths.py
  python3 -I -B -W error verification/tests/test_check_tracked_private_paths.py
Needs: Python 3 standard library and git. Takes under 1 second.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GUARD = Path(__file__).resolve().parents[1] / "check_tracked_private_paths.py"


class TrackedPrivatePathGuard(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        (self.repo / "verification").mkdir(parents=True)
        shutil.copyfile(GUARD, self.repo / "verification" / GUARD.name)
        # Stop git from finding a repository above the temporary directory.
        self.env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(self.tmp))

    def tearDown(self):
        self._tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True, env=self.env)

    def stage(self, *paths, force=False):
        for rel in paths:
            path = self.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("x\n", encoding="utf-8")
        self.git("add", *(["-f"] if force else []), *paths)

    def run_guard(self, env=None):
        return subprocess.run(
            [sys.executable, "-I", "-B", str(self.repo / "verification" / GUARD.name)],
            capture_output=True,
            text=True,
            check=False,
            env=env or self.env,
        )

    def test_clean_tree_passes(self):
        self.git("init", "-q")
        self.stage("README.md", "docs/repos/notes.md", "verification/probes/x.py")
        run = self.run_guard()
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertTrue(run.stdout.startswith("PASS: none of the 3 tracked paths"), run.stdout)

    def test_top_level_sibling_layout_fails(self):
        for rel in ("synthesis/fold_sheaf_collapse.py", "probes/gravity/p.py", "branches/spectral-inertia/run_all.py", "repos/project-asma/f.lean"):
            with self.subTest(path=rel):
                self.git("init", "-q")
                self.stage("README.md", rel)
                run = self.run_guard()
                self.assertEqual(run.returncode, 1, run.stdout)
                self.assertEqual(run.stdout.splitlines(), ["FAIL: 1 tracked or staged path(s) of the private or sibling layout:", f"  {rel}"])
                self.git("rm", "-q", "--cached", rel)

    def test_forced_add_past_gitignore_fails(self):
        self.git("init", "-q")
        (self.repo / ".gitignore").write_text("/repos/\n", encoding="utf-8")
        self.stage(".gitignore", "repos/fractals/model.js", force=True)
        run = self.run_guard()
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertIn("  repos/fractals/model.js", run.stdout.splitlines())

    def test_session_transcripts_fail_at_any_depth(self):
        self.git("init", "-q")
        self.stage("README.md", "verification/checks/gemini-sessions/s2.txt", "gemini-session-488274c3e0040dac/code_blocks/b.py")
        run = self.run_guard()
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertEqual(
            run.stdout.splitlines()[1:],
            ["  gemini-session-488274c3e0040dac/code_blocks/b.py", "  verification/checks/gemini-sessions/s2.txt"],
        )

    def test_not_a_checkout_is_not_a_pass(self):
        run = self.run_guard()
        self.assertEqual(run.returncode, 2, run.stdout)
        self.assertTrue(run.stdout.startswith("ERROR: git ls-files failed, so the tree was not checked"), run.stdout)

    def test_empty_listing_is_not_a_pass(self):
        self.git("init", "-q")
        run = self.run_guard()
        self.assertEqual(run.returncode, 2, run.stdout)
        self.assertEqual(run.stdout.strip(), "ERROR: git lists no files here, so the tree was not checked")

    def test_missing_git_is_not_a_pass(self):
        empty_bin = self.tmp / "empty-bin"
        empty_bin.mkdir()
        run = self.run_guard(env=dict(self.env, PATH=str(empty_bin)))
        self.assertEqual(run.returncode, 2, run.stdout)
        self.assertTrue(run.stdout.startswith("ERROR: cannot run git, so the tree was not checked"), run.stdout)


if __name__ == "__main__":
    if shutil.which("git") is None:
        sys.exit("git is required for these controls")
    unittest.main()
