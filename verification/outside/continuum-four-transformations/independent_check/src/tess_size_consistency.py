"""Arithmetic only, on byte counts printed in DATA_REQUEST.md and cadence counts printed in AMENDMENT_1.md.
Question: could the TESS cadence counts 115,338 and 120,486 have come from file sizes alone, so that no FITS header had to be read?
FITS files are written in 2,880-byte blocks. Assume a fixed row length R bytes and a fixed number H of header blocks.
Standard library only. No bare assert."""
import sys

sizes = {38: (11566080, 115338), 65: (12081600, 120486)}
print("Both file sizes are multiples of 2880:", all(s % 2880 == 0 for s, _ in sizes.values()))
found = []
for R in range(40, 400):
    for H in range(2, 40):
        ok = True
        for s, rows in sizes.values():
            blocks = -(-rows * R // 2880)       # ceil
            if (H + blocks) * 2880 != s:
                ok = False
        if ok:
            found.append((R, H))
print("(row bytes R, header blocks H) pairs that reproduce BOTH file sizes exactly from the stated row counts:", found)
for R, H in found[:3]:
    for sec, (s, rows) in sizes.items():
        lo = ((s // 2880 - H) * 2880 - 2879) // R + 1
        hi = ((s // 2880 - H) * 2880) // R
        print(f"  R={R}, H={H}, sector {sec}: file size alone allows {lo} to {hi} rows; amendment says {rows} (upper bound from size: {hi})")
print("Reading: the stated counts fit a fixed-row-length layout, so they could have come from sizes, but a size alone gives a range, not the exact count.")
if not found:
    print("no (R,H) found: the counts did not come from a size-only calculation under this model")
print("DONE tess_size_consistency")
