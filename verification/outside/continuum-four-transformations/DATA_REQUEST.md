# Data request

Status: not yet fetched. No file below has been downloaded. Sizes come from HTTP HEAD requests and archive listings made on 2026-11-21.

Four independent instruments in four domains: gravitational-wave strain (LIGO, via GWOSC), Mars ground motion (InSight SEIS, NASA PDS), solar radio emission (Wind/WAVES, NASA SPDF) and stellar brightness (TESS, NASA MAST).
Each instrument has a fit file set and a verdict file set from a different date (see `PREREG.md` section 8). Total 634,994,866 bytes (about 635 MB).
Less would do: the fit stage only fixes a time scale and a template per instrument, so dropping the L1 fit file saves 126 MB (509,128,939 bytes in all). The instrument net then has no fit-stage check for GW.

## Files

GW: base URL `https://gwosc.org/eventapi/json/GWTC-1-confident/`.

| Role | File | Path under base URL | Bytes |
|---|---|---|---|
| GW fit, H1 | `H-H1_GWOSC_4KHZ_R1-1126257415-4096.hdf5` | `GW150914/v3/` | 130,158,262 |
| GW fit, L1 | `L-L1_GWOSC_4KHZ_R1-1126257415-4096.hdf5` | `GW150914/v3/` | 125,865,927 |
| GW verdict, H1 | `H-H1_GWOSC_4KHZ_R1-1135134303-4096.hdf5` | `GW151226/v2/` | 69,367,295 |
| GW verdict, L1 | `L-L1_GWOSC_4KHZ_R1-1135134303-4096.hdf5` | `GW151226/v2/` | 128,039,935 |

SEIS: base URL `https://pds-geosciences.wustl.edu/insight/urn-nasa-pds-insight_seis/data/xb/continuous_waveform/elyse/`.

| Role | File | Path under base URL | Bytes |
|---|---|---|---|
| SEIS fit, VBB axis U | `xb.elyse.02.bhu.2019.143.1.mseed` | `2019/143/` | 6,480,384 |
| SEIS fit, SP axis U | `xb.elyse.67.shu.2019.143.17.mseed` | `2019/143/` | 5,137,920 |
| SEIS verdict, VBB axis U | `xb.elyse.02.bhu.2019.207.8.mseed` | `2019/207/` | 7,340,032 |
| SEIS verdict, SP axis U | `xb.elyse.67.shu.2019.207.8.mseed` | `2019/207/` | 5,035,008 |

Wind/WAVES RAD2: base URL `https://spdf.gsfc.nasa.gov/pub/data/wind/waves/rad2_l2/2015/`. File names are `wi_l2_wav_rad2_YYYYMMDD_v01.cdf`.

| Role | Dates | Bytes per file, in date order | Bytes |
|---|---|---|---|
| WAVES fit | 20150101 to 20150108 | 8,049,179 / 8,286,263 / 8,806,252 / 6,401,232 / 8,192,307 / 8,270,051 / 8,330,045 / 8,465,653 | 64,800,982 |
| WAVES verdict | 20150701 to 20150708 | 8,861,501 / 8,602,397 / 8,823,131 / 8,727,663 / 8,782,498 / 8,815,711 / 9,109,882 / 7,398,658 | 69,121,441 |

TESS: URL `https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:TESS/product/<file>`, which redirects to the public bucket `https://stpubdata.s3.us-east-1.amazonaws.com/tess/public/tid/`. Target TIC 388857263, a nearby M dwarf with frequent flares, chosen before any data were seen.

| Role | File | Bytes |
|---|---|---|
| TESS fit, sector 38 | `tess2021118034608-s0038-0000000388857263-0209-a_fast-lc.fits` | 11,566,080 |
| TESS verdict, sector 65 | `tess2023124020739-s0065-0000000388857263-0259-a_fast-lc.fits` | 12,081,600 |

## What the values are

| Instrument | Format | Sampling and length | Raw or reduced | Terms as the archive states them |
|---|---|---|---|---|
| GW | HDF5, strain plus 1 Hz data-quality and injection bitmasks | 4,096 Hz, 4,096 s, 16,777,216 samples per file | Reduced: calibrated strain h(t), calibration C02, high-pass filtered at 8 Hz, decimated from 16,384 Hz with a zero-phase filter (GWOSC technical notes). Raw photodiode channels are not public in this form | "Data from this web site are licensed under a Creative Commons Attribution 4.0 International License", with a citation request |
| SEIS | miniSEED, counts | 20 samples per second, one UTC day (the day-207 VBB label states 1,728,003 samples) | Raw: digitiser counts after on-board decimation. The bundle readme says calibration changes only the metadata files, "The raw data files are not changed". No response removal is applied here | No licence text in the bundle readme. Data DOI 10.18715/SEIS.INSIGHT.XB_2016 |
| Wind/WAVES | CDF, variables PSD_V2_Z and PSD_V2_S | One value per frequency channel per sweep. The dataset notes say time resolution "varies with instrument mode ranging from few tenth of seconds to 192 seconds". Exact cadence and frequency list are read from the fit files and recorded before any statistic | Level 2: "Power spectral density before antenna calibration" (CDAWeb notes). On-board receiver processing applies | The SPDF readme asks that publications acknowledge SPDF and the principal investigator |
| TESS | FITS light curve, columns SAP_FLUX, SAP_BKG, QUALITY | 20 s cadence, about 27 days per sector with a mid-sector gap | Reduced: simple aperture photometry from SPOC-calibrated pixels, background subtracted. PDCSAP_FLUX (detrended) is not used | MAST data use policy: most MAST data are public domain and "licensed under CC0", with an acknowledgement expected. Collection DOI 10.17909/t9-st5g-3177 |

The least processed TESS product, the target pixel file with its RAW_CNTS column, is 334,123,200 bytes for sector 38 and 348,713,280 bytes for sector 65. It is left for a later run to keep this one small.

## How each file is pinned on fetch

1. Fetching starts only after the analysis code and the outputs of known-answer tests K1 to K6 are committed.
2. Each file goes into a new, empty directory. No code is run from that directory, and Python reads it with `-I`.
3. SHA-256 is computed on download and written to `DATA_MANIFEST.sha256` together with URL, byte count, HTTP Last-Modified and ETag. The manifest is committed before any file is opened for analysis.
4. Archive cross-checks: for SEIS, the MD5 line for each file in the bundle manifest `urn-nasa-pds-insight_seis.md5`. For TESS, the S3 ETag (equal to the MD5 for single-part objects, checked against a local MD5). GWOSC and SPDF publish no per-file checksum for these files, so byte count and Last-Modified are recorded.
5. Verdict files are hashed and then left unopened until the fit stage is committed.
