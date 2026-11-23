"""Every 'Old text' block of the draft AMENDMENT_3.md must be a quotation of the base PREREG.md (commit 1aa53fb) at the cited lines.
Standard library only. Arguments: AMENDMENT_3.md, base PREREG.md (copy of the published file)."""
import sys
with open(sys.argv[1], encoding="utf-8") as fh:
    am = fh.read().split("\n")
with open(sys.argv[2], encoding="utf-8") as fh:
    base = fh.read().split("\n")
fails = []
def block(start):
    """lines between the fence that opens at 1-based line `start` and the next fence"""
    i = start
    out = []
    while am[i].strip() != "```":
        out.append(am[i]); i += 1
    return out
# (first fence line in AMENDMENT_3, cited base line ranges (1-based, inclusive), mode)
spec = [(42, (428, 429), "lines"), (73, (425, 425), "lines"), (89, (426, 426), "sub"), (93, (428, 428), "sub"),
        (112, (421, 421), "sub"), (116, (430, 430), "lines"), (155, (421, 432), "lines"),
        (270, (191, 191), "lines"), (274, (356, 356), "sub"), (278, (358, 358), "sub"), (362, (384, 384), "lines")]
for (fence, (a, b), mode) in spec:
    if am[fence - 1].strip() != "```text":
        fails.append(f"no fence at line {fence}"); continue
    blk = block(fence)
    ref = base[a - 1:b]
    if mode == "lines":
        ok = [x.rstrip() for x in blk if x.strip()] == [x.rstrip() for x in ref if x.strip()]
    else:
        text = " ".join(x.strip() for x in blk)
        ok = any(text in r for r in ref) or all(any(x.strip() in r for r in ref) for x in blk if x.strip())
    print(f"AMENDMENT_3 lines {fence + 1}-{fence + len(blk)} vs PREREG (1aa53fb) lines {a}-{b} ({mode}): {'QUOTE MATCHES' if ok else 'DOES NOT MATCH'}")
    if not ok:
        fails.append(f"{fence}")
# inline quotation in SK6
s = 'Law 2b instance F uses `law2b-F` and the G1 null replicates `law2b-null`.'
print("inline quotation in SK6 found in base line 430: ", s in base[429])
if s not in base[429]:
    fails.append("inline")
# must-fail control: a corrupted quotation is flagged
bad = block(73)[0].replace("K3:<case>", "K3:<kase>")
print("control: a corrupted quotation is flagged:", bad.rstrip() != base[424].rstrip())
print("RESULT", "all quotations match" if not fails else "MISMATCH " + ",".join(fails))
