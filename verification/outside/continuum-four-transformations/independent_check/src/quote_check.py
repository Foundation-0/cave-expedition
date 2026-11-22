"""Check that each quoted 'Old text' block in AMENDMENT_1.md appears verbatim in the frozen PREREG.md at the line
numbers the amendment cites, and that quoted 'New text' blocks appear verbatim in the amended PREREG.md.
Standard library only. argv[1] frozen plan, argv[2] amend1 folder."""
import re
import sys


def slurp(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

FROZEN = sys.argv[1]
D = sys.argv[2]
fz = slurp(FROZEN).split("\n")
am = slurp(f"{D}/PREREG.md")
amd = slurp(f"{D}/AMENDMENT_1.md").split("\n")
fails = 0


def find_line(text):
    return [i + 1 for i, l in enumerate(fz) if text.strip() in l]


i = 0
cur_old = None
section = None
while i < len(amd):
    l = amd[i]
    if l.startswith("## "):
        section = l[:6]
    m = re.match(r"Old text(?:,| )(?: lines?| line)? ?([\d, and]*)", l)
    if l.startswith("Old text") and i + 2 < len(amd):
        cite = l
    if l.startswith("```text"):
        j = i + 1
        blk = []
        while not amd[j].startswith("```"):
            blk.append(amd[j])
            j += 1
        for b in blk:
            hits = find_line(b)
            in_amended = b.strip() in am
            print(f"[{section}] block line (amendment line {i+2}): frozen plan line(s) {hits or 'NOT FOUND'}; "
                  f"present in amended plan: {in_amended} | {b[:70]}")
            if not hits and not in_amended:
                fails += 1
        i = j
    i += 1
# new-text quotes
for q in ("K below the binomial 1 percent excess point, the smallest k with P(Binomial(S, 0.05) >= k) at most 0.01 (K < 4 when S = 12, K < 5 when S = 24, K < 6 when S = 32)",
          "A class is flagged if 68 or more of its 1,000 segments have p at most 0.05. 68 is the smallest k with P(Binomial(1000, 0.05) >= k) at most 0.01 (the tail at 68 is 0.0074).",
          "K2 Nothing found in noise. 1,000 seeds per class at each window length."):
    print("new text present in amended plan:", q in am, "|", q[:60])
    if q not in am:
        fails += 1
print("FAILS", fails)
sys.exit(1 if fails else 0)
