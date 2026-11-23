"""Amendment 4: every quotation in AMENDMENT_4.md against the published files at 4c6ecd1, character for character.
Arguments: AMENDMENT_4.md, then base files PREREG.md AMENDMENT_2.md (copies of the files at 4c6ecd1). Standard library only. No bare assert."""
import re
import sys
with open(sys.argv[1], encoding="utf-8") as fh:
    am = fh.read().split("\n")
with open(sys.argv[2], encoding="utf-8") as fh:
    pre = fh.read().split("\n")
with open(sys.argv[3], encoding="utf-8") as fh:
    am2 = fh.read().split("\n")
fails = []
def locate(text, lines):
    return [i + 1 for i, l in enumerate(lines) if text in l]
# 1. fenced old-text blocks: must equal a whole published line
w1 = []
i = 0
blocks = []
while i < len(am):
    if am[i].strip() == "```text":
        j = i + 1
        body = []
        while am[j].strip() != "```":
            body.append(am[j]); j += 1
        blocks.append((i + 2, body))
        i = j
    i += 1
old_specs = {0: ("PREREG.md", 440), 1: ("AMENDMENT_2.md", 179)}
for k, (src, ln) in old_specs.items():
    start, body = blocks[k]
    ref = (pre if src == "PREREG.md" else am2)[ln - 1]
    ok = len(body) == 1 and body[0] == ref
    print(f"AMENDMENT_4.md line {start}: block equals {src} line {ln}: {'EXACT' if ok else 'DIFFERENT'}")
    if not ok:
        fails.append(f"block {k}")
# 2. the quotations the amendment makes of published text
INTENDED = [
    ("adopted, with ties not counted as below (B8)", "AMENDMENT_2.md"),
    ("no tie can produce a finding in either direction", "AMENDMENT_2.md"),
    ("only away from a verdict", "AMENDMENT_2.md"),
    ("not as \"below\" when deciding an adverse transfer", "AMENDMENT_2.md"),
    ("the 2.5th percentile", "PREREG.md"),
    ("Before data are opened, each instance passes, with the instance applied and at window length 4,096 only, K2 with 200 seeds per class, K3 on the native net, and the paired K4 or K5 test.", "PREREG.md"),
    ("evidence against at the confirmatory level, Law 2b search unresolved", "PREREG.md"),
]
for q, name in INTENDED:
    lines = pre if name == "PREREG.md" else am2
    in_am4 = q in "\n".join(am)
    hits = locate(q, lines)
    print(f"quotation in AMENDMENT_4.md: {'yes' if in_am4 else 'NO'}; found in {name} at line {hits}: {q[:75]}")
    if not (in_am4 and hits):
        fails.append("quote " + q[:30])
# 3. short quoted phrases that are rules
for q, src in (("not as below", am2), ("below", None)):
    pass
print("short phrases:")
for q, lines, name in (("not as \"below\"", am2, "AMENDMENT_2.md"), ("the 2.5th percentile", pre, "PREREG.md")):
    print(f"   {q!r}: lines {locate(q, lines)} in {name}")
# 4. cited line descriptions
checks = {
    "PREREG 166 carries the transfer p-value and the 2.5th percentile": "2.5th percentile" in pre[165] and "at least S_B(w_A)" in pre[165],
    "PREREG 361 is the K4 A to C criterion": "A to C must give an arrow transfer score" in pre[360],
    "PREREG 379 is the K5 transfer criterion with p": "flow transfer p at most 0.001" in pre[378],
    "PREREG 516 is the pair result rule": "the arrow transfer is \"pass\"" in pre[515],
    "PREREG 613 is the G4 obstruction": "adverse both ways, not merely failing" in pre[612],
    "PREREG 310 is the gate": pre[309].startswith("Gate. No data file is opened"),
    "PREREG 311 allows amendment before data": "amended again, with the date logged, before any data file is opened" in pre[310],
    "PREREG 400 allows a dated amendment before the verdict files": "added as a dated amendment" in pre[399],
    "PREREG 584 holds the instance pre-data checks": "Before data are opened, each instance passes" in pre[583],
    "PREREG 440 is D8": pre[439].startswith("- D8."),
    "PREREG 520 to 526 are rules 1 to 7": pre[519].startswith("1. Invalid") and pre[525].startswith("7. Inconclusive"),
    "PREREG 530 to 535 are the flow rules": pre[529].startswith("1. Invalid") and pre[534].startswith("6. Inconclusive"),
    "PREREG 611 is G4": pre[610].startswith("G4, obstruction"),
    "PREREG 585 flags a check": pre[584].startswith("A null class is flagged"),
    "AMENDMENT_2 183 holds the reason": "no tie can produce a finding in either direction" in am2[182],
    "AMENDMENT_2 186 holds the effect": "only away from a verdict" in am2[185],
}
for k, v in checks.items():
    print(f"   {k}: {'yes' if v else 'NO'}")
    if not v:
        fails.append(k)
print("control: a corrupted quotation is not found:", not locate("not as below!", am2))
print("RESULT", "all quotations and cited lines match" if not fails else "MISMATCH " + ", ".join(fails))
