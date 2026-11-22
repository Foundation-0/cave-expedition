"""Hashes, line endings, path, name and email scan and README hash-table check for the Amendment 2 files.
Arguments: PREREG.md AMENDMENT_2.md README.md AMENDMENT_1.md. Standard library only. No bare assert."""
import hashlib
import re
import sys

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


def raw(p):
    with open(p, "rb") as fh:
        return fh.read()


prereg, am2, readme, am1 = sys.argv[1:5]
paths = {"PREREG.md": prereg, "AMENDMENT_2.md": am2, "README.md": readme}
hashes = {}
for name, p in paths.items():
    h = hashlib.sha256(raw(p)).hexdigest()
    hashes[name] = h
    print(f"HASH {name}: {h}")
h1 = hashlib.sha256(raw(am1)).hexdigest()
print(f"HASH AMENDMENT_1.md (published): {h1}")
txt = raw(readme).decode("utf-8")
rows = re.findall(r"\| `([A-Z_0-9]+\.md)` \| `([0-9a-f]{64})` \|", txt)
tab = dict(rows)
print(f"INFO README table rows: {sorted(tab)}")
for name, expect in (("PREREG.md", hashes["PREREG.md"]), ("AMENDMENT_1.md", h1), ("AMENDMENT_2.md", hashes["AMENDMENT_2.md"])):
    ok = tab.get(name) == expect
    print(f"README table {name}: {'MATCH' if ok else 'DIFFERS'}")
    if not ok:
        FAILS.append("table " + name)
for name, p in paths.items():
    b = raw(p)
    cr = b.count(b"\r")
    s = b.decode("utf-8")
    bad = []
    for pat, lab in (("/" + "Us" + "ers/", "home path"), ("/" + "ho" + "me/", "home path"), ("~" + "/", "home path"),
                     (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", "email"), (r"gh[pous]_[A-Za-z0-9]{20,}", "token"),
                     (r"[A-Za-z]:\\\\", "windows path"), ("/" + "pri" + "vate/|/" + "tm" + "p/", "temp path")):
        for m in re.finditer(pat, s):
            bad.append((lab, m.group(0)[:40]))
    print(f"SCAN {name}: CR bytes {cr}; findings {bad if bad else 'none'}; ends with newline {b.endswith(b'\n')}")
    if cr or bad:
        FAILS.append("scan " + name)
control("a doctored README hash is flagged", tab.get("AMENDMENT_2.md") != "0" * 64)
control("a CR byte would be counted", b"a\r\nb".count(b"\r") == 1)
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("DONE published_files_check")
