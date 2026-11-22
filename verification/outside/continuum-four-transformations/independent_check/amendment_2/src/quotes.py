"""Check every old-text quotation in the Amendment 2 draft (B1 to B12) against the base commit at the cited lines.
The base files are read from commit f584897 with git, so run it from inside the repository.
Argument: path of AMENDMENT_2.md. Standard library only. No bare assert."""
import subprocess
import re
import sys

FAILS = []


def slurp(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


BASE = "f584897"
PKG = "verification/outside/continuum-four-transformations/"


def git_show(name):
    return subprocess.run(["git", "show", f"{BASE}:{PKG}{name}"], capture_output=True, text=True, check=True).stdout


d2 = sys.argv[1]
P = git_show("PREREG.md").split("\n")
A1 = git_show("AMENDMENT_1.md").split("\n")
D = slurp(d2).split("\n")


def where(doc, text):
    return [i + 1 for i, l in enumerate(doc) if text in l]


# walk the draft: remember the last "Old text" / "New text" marker before each fenced block
marker = None
sec = None
blocks = []
i = 0
while i < len(D):
    l = D[i]
    m = re.match(r"## (B\d+)\.", l)
    if m:
        sec = m.group(1)
    if l.startswith("Old text") or l.startswith("New text"):
        marker = (l.split(",")[0].split(":")[0], l)
    if l.startswith("```text"):
        j = i + 1
        blk = []
        while not D[j].startswith("```"):
            blk.append(D[j])
            j += 1
        blocks.append((sec, marker[0] if marker else None, marker[1] if marker else "", i + 1, blk))
        i = j
    i += 1
print(f"INFO fenced blocks: {[(s, k, ln) for s, k, _, ln, _ in blocks]}")
cited = {"B1": [286, 287], "B2": [480], "B4": [335, 336], "B5": [273, 274], "B6": [277], "B7": [216], "B9": [316]}
for sec, kind, intro, ln, blk in blocks:
    if kind != "Old text":
        continue
    print(f"-- {sec} old text (draft line {ln}); cited: {intro[:110]}")
    found = []
    for b in blk:
        if not b.strip():
            continue
        h = where(P, b.strip())
        found.append(h)
        print(f"   {'FOUND' if h else 'NOT FOUND'} at base line(s) {h}: {b.strip()[:70]}")
        if not h:
            FAILS.append(sec + ": " + b[:40])
    want = cited.get(sec)
    flat = sorted({x for h in found for x in h})
    if want and not set(flat) <= set(want):
        print(f"   NOTE found lines {flat} differ from the cited lines {want}")
        FAILS.append(sec + " cited lines")
# inline quotes
inline = [("B8 old text line 102", "Values within 1e-12 relative of each other count as ties against the real series.", 102),
          ("B11 K2 control line 291", "must be flagged by the K2a rule", 291),
          ("B11 K4 control line 307", "Neither the arrow transfer nor the profile transfer may reach p at most 0.01 in more than 1 of the 10 seeds", 307)]
for lab, q, ln in inline:
    h = where(P, q)
    print(f"-- {lab}: {'FOUND' if ln in h else 'NOT FOUND'} at base line(s) {h}")
    if ln not in h:
        FAILS.append(lab)
# B3 change log lines 18 to 21
order = [re.match(r"- (A\d+) ", P[k - 1]).group(1) if re.match(r"- (A\d+) ", P[k - 1]) else None for k in (18, 19, 20, 21)]
print(f"INFO base lines 18 to 21: {order} (draft says A12, A14, A13, A11)")
if order != ["A12", "A14", "A13", "A11"]:
    FAILS.append("B3 order")
# B1 figures in A1 line 500
for fig in ("0.0117", "0.0043", "0.0008", "0.046", "0.013"):
    if fig not in A1[499]:
        FAILS.append("A14 item 1 figure " + fig)
print("INFO the five A14 item 1 figures are in base AMENDMENT_1 line 500")
# B4 line 335 and 336 starts
print(f"INFO base 335: {P[334][:50]} | base 336: {P[335][:50]}")
# B10: references to the old amendment-1 text in the draft
control("a doctored quotation is not found", not where(P, "A rate up to 0.10 does not stop it. A series whose segment rate is 0.10 passes one presence run with probability at most 0.0118"))
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE quotes")
