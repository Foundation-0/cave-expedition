"""What can and cannot be derived from the byte counts in FETCH_MANIFEST/DATA_REQUEST and public format facts alone.
No data file is touched. Arithmetic only. Standard library only. No bare assert.
Public facts used (recalled, NOT re-verified offline): FITS is written in 2,880-byte blocks; the SPOC light-curve
table has 20 columns: 5 x 8-byte (TIME, PSF_CENTR1_COL, PSF_CENTR1_ROW, MOM_CENTR1, MOM_CENTR2),
13 x 4-byte float, 2 x 4-byte int (CADENCENO, QUALITY) = 100 bytes per row.
Wind/WAVES RAD2: number of frequency channels F and the list of stored variables are NOT known here."""
import sys

def blocks(n, size):
    return -(-n // size)

print("== TESS ==")
row = 5 * 8 + 13 * 4 + 2 * 4
print(f"row bytes from the recalled column list: {row}")
sizes = {38: 11566080, 65: 12081600}
claims = {38: 115338, 65: 120486}
for H in (10, 11, 12):
    print(f"-- assume {H} non-table blocks (primary header, table header, aperture extension, padding of other HDUs)")
    for sec, s in sizes.items():
        tb = s // 2880 - H
        hi = tb * 2880 // row
        lo = ((tb - 1) * 2880) // row + 1
        print(f"   sector {sec}: table blocks {tb}; rows between {lo} and {hi}; amendment {claims[sec]} inside range: {lo <= claims[sec] <= hi}")
print("Result: size plus row length gives a window of 29 rows; the header-block count shifts it by 29 rows per block.")
print("Exact counts (115,338 and 120,486) are NOT derivable from sizes alone. The only (R,H) pair that reproduces both sizes from the stated counts is R=100, H=11 (tess_size_consistency.py).")
print("Do the conclusions depend on the exact count? Blocks of 4,224 samples at flow level 1 (rows/2):")
for sec in sizes:
    for H in (10, 11, 12):
        tb = sizes[sec] // 2880 - H
        hi = tb * 2880 // row
        lo = ((tb - 1) * 2880) // row + 1
        b_lo, b_hi = (lo // 2) // 4224, (hi // 2) // 4224
        l2_lo, l2_hi = (lo // 4) // 4224, (hi // 4) // 4224
        print(f"   sector {sec}, H={H}: level-1 blocks {b_lo}..{b_hi}; level-2 blocks {l2_lo}..{l2_hi}")
print("Level 2 needs 202,752 rows; the sector length at 20 s cannot supply that (27.4 d x 4,320 = 118,368):", 202752 > 118368)
print("So 'highest populated level is 1' and 'at least 5 of 7 aligned levels empty' follow from sector length and block size alone;")
print("'13 and 14 blocks' follows from size plus the 100-byte row to within the 29-row window (robust: boundaries are 109,824 / 118,272 / 122,496 rows).")
print("'At most' is not guaranteed by sizes: the size bound for sector 38 is 115,344 under H=11, not 115,338.")
print("Gaps and flags (QUALITY != 0, NaN) cannot be known without reading the columns.")

print("== Wind/WAVES RAD2 cadence ==")
waves = [8049179, 8286263, 8806252, 6401232, 8192307, 8270051, 8330045, 8465653]
print("fit-set daily sizes:", waves, "spread", f"{min(waves)/1e6:.2f} to {max(waves)/1e6:.2f} MB")
print("Cadence from size needs bytes per sweep, which depends on F, the stored variables and CDF compression; none is known from sizes.")
for label, bps in (("F=256, two float32 spectra + 8-byte epoch (2,056 B/sweep)", 2056),
                   ("F=256, two float32 spectra + 40 B of other per-sweep fields (2,088)", 2088),
                   ("calibrated so the mean day is 33 s (3,100 B/sweep)", None)):
    if bps is None:
        mean = sum(waves) / len(waves)
        bps = 33 * mean / 86400
        print(f"-- {label}: computed {bps:.0f} B/sweep")
    else:
        print(f"-- {label}")
    cads = [86400 * bps / b for b in waves]
    print("   implied cadence per day (s):", ", ".join(f"{c:.1f}" for c in cads), f"| mean {sum(cads)/len(cads):.1f}")
    best = None
    for N in (4096, 2048, 1024, 512):
        n = int(8 * 86400 / (sum(cads) / len(cads)))
        if n // (N + 128) >= 12:
            best = N
            break
    print(f"   N chosen by the 12-block rule at the mean cadence: {best}")
print("Reading: with two spectra at F=256 the cadence is about 22 s (N=2048); the amendment's 33 s needs about 3,100 B/sweep, i.e. extra stored data or a different F.")
print("The ~20 percent spread in daily size also says cadence is not constant (mode changes), as the dataset notes say (a few tenths of a second to 192 s).")
print("No cadence is derivable from sizes alone; the plan's rule reads N from the fit files, so the validity of the plan does not depend on the 33 s figure.")
print("DONE size_derivations")
