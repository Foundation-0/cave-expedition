"""Clean-room consistency check of FETCH_MANIFEST.tsv against DATA_REQUEST.md and AMENDMENT_1.md (text only).
Standard library only. No bare assert. argv[1] = amend1 folder."""
import re
import sys


def slurp(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()

D = sys.argv[1] if len(sys.argv) > 1 else ".."
FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)
        print(f"FAIL control not flagged: {tag}")


def verdict(tag, desc, claimed, mine, ok):
    print(f"CLAIM {tag} | {desc} | amendment={claimed} | mine={mine} | {'REPRODUCED' if ok else 'DIFFERS'}")


man = [l.split("\t") for l in slurp(f"{D}/FETCH_MANIFEST.tsv").split("\n") if l]
hdr, rows = man[0], man[1:]
print("INFO manifest header:", hdr)
req = slurp(f"{D}/DATA_REQUEST.md")
amd = slurp(f"{D}/AMENDMENT_1.md")

# bytes per file from DATA_REQUEST
req_bytes = {}
for m in re.finditer(r"\| [^|]+ \| `([^`]+)` \| `[^`]*` \| ([\d,]+) \|", req):
    req_bytes[m.group(1)] = int(m.group(2).replace(",", ""))
for m in re.finditer(r"\| `([^`]+\.(?:mseed|fits|hdf5))` \| (?:`[^`]*` \| )?([\d,]+) \|", req):
    req_bytes.setdefault(m.group(1), int(m.group(2).replace(",", "")))
# WAVES per-file list
for m in re.finditer(r"\| WAVES (fit|verdict) \| (\d{8}) to (\d{8}) \| ([\d,/ ]+) \| ([\d,]+) \|", req):
    d0 = int(m.group(2))
    vals = [int(v.replace(",", "")) for v in m.group(4).split("/")]
    for i, v in enumerate(vals):
        req_bytes[f"wi_l2_wav_rad2_{d0 + i}_v01.cdf"] = v
    tot = sum(vals)
    verdict(f"waves-{m.group(1)}-sum", f"WAVES {m.group(1)} per-file bytes sum to stated total", m.group(5), tot,
            tot == int(m.group(5).replace(",", "")))
print(f"INFO files with a byte count parsed from DATA_REQUEST.md: {len(req_bytes)}")
bad = 0
for r in rows:
    name, url, nbytes, sha, ft = r
    want = req_bytes.get(name)
    if want is None or want != int(nbytes):
        bad += 1
        print(f"  byte mismatch or missing: {name} manifest {nbytes} request {want}")
verdict("bytes-per-file", "every manifest byte count equals DATA_REQUEST", "every byte count matches", f"{bad} mismatches of {len(rows)}", bad == 0)
tot = sum(int(r[2]) for r in rows)
verdict("total", "total bytes", "634,994,866", f"{tot:,}", tot == 634994866)
verdict("less-would-do", "dropping L1 fit saves 126 MB: 509,128,939", "509,128,939", f"{tot - 125865927:,}", tot - 125865927 == 509128939)
verdict("rows", "26 files", 26, len(rows), len(rows) == 26)
times = sorted(r[4] for r in rows)
verdict("times", "fetch window 04:25:04 to 04:28:56 UTC on 2026-11-22", "04:25:04 to 04:28:56",
        f"{times[0][11:19]} to {times[-1][11:19]}", times[0] == "2026-11-22T04:25:04Z" and times[-1] == "2026-11-22T04:28:56Z")
shas_ok = all(re.fullmatch(r"[0-9a-f]{64}", r[3]) for r in rows) and len({r[3] for r in rows}) == len(rows)
verdict("sha-format", "26 distinct 64-hex SHA-256 values", "(implied)", "yes" if shas_ok else "no", shas_ok)
paths = [r for r in rows if any(f.startswith("/") or f.startswith("~") or "\\" in f for f in r)]
verdict("no-local-path", "FETCH_MANIFEST.tsv holds no local path", "sanitised", f"{len(paths)} rows with a local path", not paths)
urls_ok = all(r[1].startswith("https://") and r[1].split("/")[-1].split("uri=mast:TESS/product/")[-1].endswith(r[0].split("/")[-1]) for r in rows)
verdict("url-names", "each URL ends in its file name", "(implied)", "yes" if urls_ok else "no", urls_ok)
# must-fail: a doctored row must be flagged
fake = list(rows[0]); fake[2] = str(int(fake[2]) + 1)
control("doctored byte count flagged", req_bytes.get(fake[0]) != int(fake[2]))
fake2 = list(rows[0]); fake2[1] = "/example/dir/file"
control("doctored local path flagged", any(f.startswith("/") for f in fake2))
# stale statements elsewhere
stale = []
rd = slurp(f"{D}/README.md")
if "before any data are fetched" in rd:
    stale.append("README.md: 'fixes, before any data are fetched'")
if "all marked not yet fetched" in rd:
    stale.append("README.md: 'all marked not yet fetched' (DATA_REQUEST.md now says fetched)")
if "DATA_MANIFEST.sha256" in req:
    stale.append("DATA_REQUEST.md step 3 names DATA_MANIFEST.sha256 with Last-Modified and ETag; the file is FETCH_MANIFEST.tsv with neither column")
if "Fetching starts only after" in req:
    stale.append("DATA_REQUEST.md step 1 still reads as the rule 'Fetching starts only after...' (deviation noted just above it)")
for s in stale:
    print("FINDING stale:", s)
if FAILS:
    print("FAILED CONTROLS:", FAILS)
    sys.exit(1)
print("DONE manifest_check")
