# Track S20c: Real Public Raw Physical Telemetry Portal (MP-04)

Self-contained zero-float ($\mathbb{Z}/\mathbb{Q}$) physical telemetry verification portal applying exact relational operators and three matched exact surrogate null families (`IID_PERM`, `BLOCK_16`, `WHT_PHASE`, $M = 99$, $\alpha = 5/100$) under strict Gate-8 pre-registration (`PREREG_S20C.json`) to four unauthenticated public scientific telemetry streams (`FETCH_MANIFEST.json`, `raw_telemetry/`):

- **`STREAM_A`:** LIGO GWOSC Hanford H1 `GW150914` (`4096 Hz`, `[62694:63206]`)
- **`STREAM_B`:** USGS INTERMAGNET Boulder `BOU` May 10, 2024 G5 Geomagnetic Superstorm ($X$-component, `60 s`)
- **`STREAM_C`:** NOAA CO-OPS San Francisco Golden Gate `9414290` MLLW Tide Water Level (`360 s`)
- **`STREAM_D`:** USGS NWIS Potomac River `01646500` Instantaneous Discharge (`900 s`)

## Pre-Registered Gate-8 Verdicts (`Window B = [256:512]`, Honest Law-4 Accounting)

- **`H1_SEAM1_SHOCK` (`FALSIFIED`, `0/4`):** Sliding rank-1 Sherman–Morrison leverage shock appears significant on `3/4` streams against naive `IID_PERM` but collapses ($p \ge 91/100$) under matched `BLOCK_16` and `WHT_PHASE` nulls.
- **`H2a_SEAM3_HVG_BETTI1` (`FALSIFIED`, `0/4`):** Smooth physical persistence suppresses Horizontal Visibility Graph chords ($\beta_1 \in \{71, 154, 217, 227\}$) strictly below the IID ceiling ($\approx 256$).
- **`H2b_SEAM3_IRREV_PHI` (`PARTIAL`, `2/4`):** Directed ordinal Hodge-curl $\Phi_{\text{asym}}$ survives all three matched nulls exclusively on driven non-equilibrium transients (`STREAM_A` LIGO merger & `STREAM_B` G5 geomagnetic storm) while failing on quasi-reversible tide (`STREAM_C`) and quantized discharge (`STREAM_D`).
- **`H3a_F3_TRANSIENT_WITNESS` (`SUPPORTED`, `4/4`):** All four held-out physical streams yield strictly Schur-stable lag-3 ridge VAR(1) operators with exact Sylvester inertia $\operatorname{In}(I_3 - T^\top T) = (2, 1, 0)$ (vs. `False` on IID white noise, and driven by linear persistence as confirmed by `99/99` `BLOCK_16`/`WHT_PHASE` surrogates).
- **`H3b_F3_COMMUTATOR` (`FALSIFIED`, `0/4`):** Normalized non-normal commutator $\kappa_{\text{F3}}$ is maximized by the IID nilpotent shift (`0.500`).

## Quick Verification

```bash
cd symbiosis/track-s20c-physical-telemetry-portal

# 1. Zero-skip R5 test suite across all three isolated R4 modes
python3 -I -B test_physical_telemetry_r5.py
python3 -I -O -B test_physical_telemetry_r5.py
python3 -I -B -W error test_physical_telemetry_r5.py

# 2. Full-replay canonical certificate check (99 x 3 surrogates + 6 controls)
python3 -I -B physical_telemetry_audit.py --check physical_telemetry_certificate.json
```

See [`PHYSICAL_TELEMETRY_REPORT.md`](PHYSICAL_TELEMETRY_REPORT.md) for the complete pre-registered protocol, exact rational measurements, known-answer controls, and verification receipts.
