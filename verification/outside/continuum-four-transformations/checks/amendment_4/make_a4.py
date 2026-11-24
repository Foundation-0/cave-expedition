"""Builds amend4/PREREG.md and amend4/README.md from the published text at 4c6ecd1 with only the changes Amendment 4 states."""
import hashlib, re, subprocess
CL = "../amend3/clone"
D = "verification/outside/continuum-four-transformations/"
def show(path):
    return subprocess.run(["git", "-C", CL, "show", "4c6ecd1:" + D + path], capture_output=True, text=True, check=True).stdout
A4 = open("AMENDMENT_4.md").read()
def block(after):
    i = A4.index(after)
    j = A4.index("```text\n", i) + 8
    return A4[j:A4.index("\n```", j)]
P = show("PREREG.md")
def rep(a, b):
    global P
    if P.count(a) != 1:
        raise SystemExit("PREREG count %d: %r" % (P.count(a), a[:60]))
    P = P.replace(a, b)
d8_old = "- D8. A transfer is adverse if fewer than 1/40 of the random detectors score below S_B(w_A) by more than the tie tolerance. No interpolated percentile is used."
rep("Status: plan as amended by Amendments 1, 2 and 3.", "Status: plan as amended by Amendments 1 to 4.")
rep("A transfer is \"adverse\" when S_B(w_A) is below the 2.5th percentile of the random detectors' S_B.",
    "A transfer is \"adverse\" when S_B(w_A) is below the 2.5th percentile of the random detectors' S_B, as reading D8 defines it.")
rep("  - A to C must give an arrow transfer score S_B(w_A) below the 2.5th percentile of its random detectors in every run,",
    "  - A to C must give an arrow transfer score S_B(w_A) below the 2.5th percentile of its random detectors, as reading D8 defines it, in every run,")
rep("\"adverse\" (S_B(w_A) below the 2.5th percentile of its random detectors in every run)",
    "\"adverse\" (S_B(w_A) below the 2.5th percentile of its random detectors, as reading D8 defines it, in every run)")
rep("## 11a. Implementation readings fixed by Amendments 2 and 3", "## 11a. Implementation readings fixed by Amendments 2 to 4")
rep(d8_old, block("New text, replacing reading D8"))
gate2 = "If any test fails, or any must-fail control is not flagged, the plan is amended again, with the date logged, before any data file is opened."
rep(gate2 + "\n", gate2 + "\n" + block("New text (section 10, after the gate)") + "\n")
l586 = [l for l in P.split("\n") if l.startswith("With 200 seeds these checks find only large miscalibration")]
if len(l586) != 1:
    raise SystemExit("line 586")
rep(l586[0] + "\n", l586[0] + "\n" + block("New text (section 12a, after line 586)") + "\n")
rep("  - Draws not listed here follow the names above.", block("New text, reading D14 (section 11a), before its last item") + "\n  - Draws not listed here follow the names above.")
log = """Amendment 4 (`AMENDMENT_4.md`, 2026-11-23) was made before any data file was opened and before the plan's author saw any outcome of the code built for Amendment 3. Its disclosure section says who had seen what and who shaped each item. It changes no threshold, level, existing seed key, test count or compute figure.

- C1 ties in the adverse decision: in each run a transfer is adverse if and only if fewer than R/40 of the random detectors score at or below S_B(w_A), ties counted as at or below (reading D8, sections 4.3, 10 and 12).
  It only removes "adverse", so it moves outcomes towards Partial or weaker negative outcomes, never towards Supported or Net-dependent.
- C2 a Law 2b instance that fails its pre-data check is not tested: it cannot rescue, and an adverse outcome it leaves unsearched stays unresolved unless another instance rescues it (section 12a).
- C3 a round of repair to a known-answer test defined, with at most two rounds per test counted from Amendment 4, each rerun on a new key epoch (section 10, reading D14).

The original text stays in git history."""
rep("\nThe original text stays in git history.", "\n" + log)
open("PREREG.md", "w").write(P)
R = show("README.md")
def rr(a, b):
    global R
    if R.count(a) != 1:
        raise SystemExit("README count %d: %r" % (R.count(a), a[:60]))
    R = R.replace(a, b)
rr("then amended three times (`AMENDMENT_1.md`, `AMENDMENT_2.md`, `AMENDMENT_3.md`)", "then amended four times (`AMENDMENT_1.md` to `AMENDMENT_4.md`)")
rr("and `AMENDMENT_1.md` to `AMENDMENT_3.md` list every change.", "and `AMENDMENT_1.md` to `AMENDMENT_4.md` list every change.")
rr("with the full 10 seeds for K4 and K5 under Amendment 1, and smoke runs of the ported code since.", "with the full 10 seeds for K4 and K5 under Amendment 1 and again on the ported code, and smoke runs of K1 to K3 on the ported code.")
rr("SHA-256 of the plan files as of Amendment 3:", "SHA-256 of the plan files as of Amendment 4:")
h = {f: hashlib.sha256(open(f, "rb").read()).hexdigest() for f in ("PREREG.md", "AMENDMENT_4.md")}
R = re.sub(r"\| `PREREG.md` \| `[0-9a-f]{64}` \|", "| `PREREG.md` | `%s` |" % h["PREREG.md"], R)
a3 = re.search(r"\| `AMENDMENT_3.md` \| `[0-9a-f]{64}` \|", R).group(0)
rr(a3, a3 + "\n| `AMENDMENT_4.md` | `%s` |" % h["AMENDMENT_4.md"])
open("README.md", "w").write(R)
