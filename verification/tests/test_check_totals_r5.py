#!/usr/bin/env python3
"""Team-side R5 controls for verification/outside/check_totals.py (optional).

verification/outside/ is the outside observer's contribution and is not edited by the team
(verification/outside/README.md, "Standing"). These controls therefore copy check_totals.py
and the four files it reads into a temporary directory, corrupt one thing per control in
the copy, and require exit 1 plus that check's own FAIL line. Nothing under
verification/outside/ is written.

Run (all three R4 modes):
  python3 -I -B verification/tests/test_check_totals_r5.py
  python3 -I -O -B verification/tests/test_check_totals_r5.py
  python3 -I -B -W error verification/tests/test_check_totals_r5.py
Needs: Python 3 standard library only. Takes under 1 second.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

OUTSIDE = Path(__file__).resolve().parents[1] / "outside"
FILES = ("check_totals.py", "rulings.json", "README.md", "OUTSIDE_AUDIT.md", "REVIEW-RESPONSE.md")
STALE = "13 stood as written, 22 were narrowed and 1 fell"


def interpreter_flags() -> list[str]:
    flags = ["-I", "-B"]
    if sys.flags.optimize:
        flags.append("-O")
    if "error" in sys.warnoptions:
        flags += ["-W", "error"]
    return flags


class CheckTotalsControls(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        for name in FILES:
            shutil.copyfile(OUTSIDE / name, self.dir / name)

    def tearDown(self):
        self._tmp.cleanup()

    def run_copy(self):
        return subprocess.run(
            [sys.executable, *interpreter_flags(), "check_totals.py"],
            cwd=str(self.dir),
            capture_output=True,
            text=True,
            check=False,
        )

    def rulings(self):
        return json.loads((self.dir / "rulings.json").read_text(encoding="utf-8"))

    def write_rulings(self, data):
        (self.dir / "rulings.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    def assertFailLine(self, line):
        run = self.run_copy()
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertIn("FAIL: " + line, run.stdout.splitlines())
        self.assertIn("RESULT check_totals: FAIL", run.stdout)
        return run.stdout

    def test_passing_copy(self):
        run = self.run_copy()
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertNotIn("FAIL", run.stdout)
        self.assertIn("RESULT check_totals: PASS", run.stdout)

    def test_unknown_ruling_label(self):
        data = self.rulings()
        data["areas"][0]["findings"][0]["ruling"] = "maybe"
        self.write_rulings(data)
        kinds = sorted({f["ruling"] for a in data["areas"] for f in a["findings"]})
        out = self.assertFailLine("unknown ruling label %s" % kinds)
        # The sum guard (line 45) fires only for a label outside the three known ones.
        self.assertIn("FAIL: the three totals do not add up to the number of rulings", out.splitlines())

    def test_duplicate_finding_id(self):
        data = self.rulings()
        findings = data["areas"][0]["findings"]
        findings.append(dict(findings[0]))
        self.write_rulings(data)
        self.assertFailLine("duplicate finding id")

    def test_totals_field(self):
        data = self.rulings()
        recount = {k: data["totals"][k] for k in ("stands", "stands_narrowed", "falls")}
        data["totals"]["falls"] += 1
        self.write_rulings(data)
        self.assertFailLine("totals in rulings.json %s differ from the recount %s" % (data["totals"], recount))

    def test_first_pass_findings(self):
        data = self.rulings()
        data["first_pass_findings"] += 1
        self.write_rulings(data)
        self.assertFailLine("first_pass_findings differs from the recount")

    def test_rulings_count(self):
        data = self.rulings()
        data["rulings"] += 1
        self.write_rulings(data)
        self.assertFailLine("rulings differs from the recount")

    def test_sentence_missing_from_readme(self):
        data = self.rulings()
        t = data["totals"]
        sentence = (
            "%d first-pass findings carry %d rulings, because one finding (`folds-dn-e8` F1) had a label part and a "
            "wording part: %d stood as written, %d were narrowed and %d fell"
            % (data["first_pass_findings"], data["rulings"], t["stands"], t["stands_narrowed"], t["falls"])
        )
        readme = self.dir / "README.md"
        text = readme.read_text(encoding="utf-8")
        self.assertIn(sentence, text)
        readme.write_text(text.replace(sentence, ""), encoding="utf-8")
        self.assertFailLine("README.md does not state: %s" % sentence)

    def test_stale_totals_appended(self):
        audit = self.dir / "OUTSIDE_AUDIT.md"
        audit.write_text(audit.read_text(encoding="utf-8") + "\n" + STALE + "\n", encoding="utf-8")
        self.assertFailLine("OUTSIDE_AUDIT.md still states the old totals")


if __name__ == "__main__":
    unittest.main()
