#!/usr/bin/env python3
"""
Audit 002: Negative Controls & Adversarial Defect Audit for Session 1 Code Blueprints
and Formulas:
  - pair_25_block_00.py (manifold_cka, h0_persistence_entropy, probe_window)
  - pair_20_block_00.py (extract_blind_invariant: negative slice crash, Welch PSD 1/2 factor, smuggled priors)
  - pair_22_block_05.py (perceptual_invariants: broken phase_coherence, np.roll wraparound)
  - S1:F[440] (Moran without Open Set Condition) & S1:F[447] (Haar wavelet vs C^2 function)

Run via:
  uv run --with scipy --with numpy python3 -B check_002_session1_instruments.py
  uv run --with scipy --with numpy python3 -O -B check_002_session1_instruments.py
  uv run --with scipy --with numpy python3 -B -W error check_002_session1_instruments.py
"""
from __future__ import annotations
import os

import importlib.util
import json
from pathlib import Path
import numpy as np
from scipy.signal import welch

GEMINI_SESSIONS_DIR = Path(os.environ.get("GEMINI_SESSIONS_DIR", "gemini-sessions"))
S1_DIR = GEMINI_SESSIONS_DIR / "gemini-session-488274c3e0040dac/code_blocks"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(f"CHECK FAILED: {msg}")


def load_mod(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, S1_DIR / filename)
    require(spec is not None and spec.loader is not None, f"failed to load {filename}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def audit_pair_25(mod25) -> dict:
    rng = np.random.default_rng(20261120)
    N = 300
    trials = 25

    def stats(vals):
        arr = np.array(vals, dtype=float)
        return {
            "mean": round(float(np.mean(arr)), 4),
            "median": round(float(np.median(arr)), 4),
            "p95": round(float(np.percentile(arr, 95)), 4),
            "min": round(float(np.min(arr)), 4),
            "max": round(float(np.max(arr)), 4),
            "frac_gt_0.3": round(float(np.mean(arr > 0.3)), 4),
            "frac_gt_0.5": round(float(np.mean(arr > 0.5)), 4),
        }

    # 1. Negative Control: Independent Brownian random walks (ZERO physical coupling)
    rw_raw, rw_obs = [], []
    for _ in range(trials):
        x = np.cumsum(rng.normal(size=N))
        y = np.cumsum(rng.normal(size=N))
        res = mod25.probe_window({"x": x, "y": y})
        c = res["cross_modal_coupling"][("x", "y")]
        rw_raw.append(c["manifold_lock"])
        rw_obs.append(c["observer_invariant_lock"])

    # 2. Negative Control: Independent AR(1) phi=0.98 (ZERO physical coupling)
    ar_raw, ar_obs = [], []
    for _ in range(trials):
        x = np.zeros(N)
        y = np.zeros(N)
        ex, ey = rng.normal(size=N), rng.normal(size=N)
        for i in range(1, N):
            x[i] = 0.98 * x[i - 1] + ex[i]
            y[i] = 0.98 * y[i - 1] + ey[i]
        res = mod25.probe_window({"x": x, "y": y})
        c = res["cross_modal_coupling"][("x", "y")]
        ar_raw.append(c["manifold_lock"])
        ar_obs.append(c["observer_invariant_lock"])

    # 3. Negative Control: Independent white Gaussian noise
    wn_raw, wn_obs = [], []
    for _ in range(trials):
        x, y = rng.normal(size=N), rng.normal(size=N)
        res = mod25.probe_window({"x": x, "y": y})
        c = res["cross_modal_coupling"][("x", "y")]
        wn_raw.append(c["manifold_lock"])
        wn_obs.append(c["observer_invariant_lock"])

    # 4. Negative Control: Two completely unrelated smooth monotonic / low-freq drifts
    t = np.linspace(0, 1, N)
    drift_res = mod25.probe_window({"linear": t, "exp": np.exp(3.0 * t)})
    drift_lock = drift_res["cross_modal_coupling"][("linear", "exp")]

    # 5. H0 persistence entropy test: 1-cycle smooth circle, 5-cycle overlapping circle, white noise, 2-cluster
    sin1_sig = np.sin(2.0 * np.pi * 1.0 * t)
    M_sin1 = mod25.takens_embed(sin1_sig, dim=5, tau=3)
    h0_sin1 = round(mod25.h0_persistence_entropy(M_sin1), 6)

    sin_sig = np.sin(2.0 * np.pi * 5.0 * t)
    M_sin = mod25.takens_embed(sin_sig, dim=5, tau=3)
    h0_sin = round(mod25.h0_persistence_entropy(M_sin), 6)

    M_wn = mod25.takens_embed(rng.normal(size=N), dim=5, tau=3)
    h0_wn = round(mod25.h0_persistence_entropy(M_wn), 6)

    # 2 well-separated tight clusters (genuinely fragmented into 2 components)
    M_2cl = np.vstack([rng.normal(0.0, 0.01, size=(100, 5)), rng.normal(10.0, 0.01, size=(100, 5))])
    h0_2cl = round(mod25.h0_persistence_entropy(M_2cl), 6)

    # 6. Non-stationary localized transient vs stationary sinusoid observer_stability
    pulse = np.exp(-0.5 * ((t - 0.5) / 0.04) ** 2) * np.cos(2 * np.pi * 25.0 * t)
    stab_sin = mod25.probe_window({"sin": sin_sig})["observer_stability"]["sin"]
    stab_pulse = mod25.probe_window({"pulse": pulse})["observer_stability"]["pulse"]
    from scipy.signal import hilbert
    cka_phase_sin = round(
        mod25.manifold_cka(M_sin, mod25.takens_embed(np.imag(hilbert(sin_sig)), dim=5, tau=3)),
        4,
    )
    cka_phase_pulse = round(
        mod25.manifold_cka(
            mod25.takens_embed(pulse, dim=5, tau=3),
            mod25.takens_embed(np.imag(hilbert(pulse)), dim=5, tau=3),
        ),
        4,
    )

    return {
        "indep_brownian_raw_cka": stats(rw_raw),
        "indep_brownian_obs_lock": stats(rw_obs),
        "indep_ar1_0.98_raw_cka": stats(ar_raw),
        "indep_ar1_0.98_obs_lock": stats(ar_obs),
        "indep_white_noise_raw_cka": stats(wn_raw),
        "indep_linear_vs_exp_drift": drift_lock,
        "h0_entropy_1cycle_smooth_circle": h0_sin1,
        "h0_entropy_5cycle_sinusoid": h0_sin,
        "h0_entropy_white_noise": h0_wn,
        "h0_entropy_fragmented_2clusters": h0_2cl,
        "observer_stability_sinusoid": stab_sin,
        "observer_stability_localized_pulse": stab_pulse,
        "cka_raw_vs_hilbert_sin": cka_phase_sin,
        "cka_raw_vs_hilbert_pulse": cka_phase_pulse,
    }


def audit_pair_20(mod20) -> dict:
    rng = np.random.default_rng(7)
    fs = 1024  # scaled fs still triggers t0=0, lag=-max_lag < 0
    N = 8 * fs
    x1 = rng.normal(size=N)
    x2 = rng.normal(size=N)

    # 1. Reproduce negative-slice crash directly
    crash_msg = None
    try:
        mod20.extract_blind_invariant(x1, x2, fs=fs)
    except Exception as exc:
        crash_msg = f"{type(exc).__name__}: {exc}"
    require(crash_msg is not None and "ValueError" in crash_msg, "expected negative-slice ValueError crash")

    # 2. Verify Welch PSD scaling factor discrepancy (1/2 factor on one-sided density)
    f_psd, psd = welch(x1, fs=fs, nperseg=4 * fs)
    freqs = np.fft.rfftfreq(N, d=1.0 / fs)
    psd_interp = np.interp(freqs, f_psd, psd)
    X_f = np.fft.rfft(x1)
    # Interior frequencies only (exclude DC and Nyquist)
    interior = (freqs > 10.0) & (freqs < fs / 2 - 10.0)
    ratio = (np.abs(X_f[interior]) ** 2) / (N * fs * psd_interp[interior])
    mean_ratio = float(np.mean(ratio))
    require(abs(mean_ratio - 0.5) < 0.05, f"expected mean Welch ratio ~0.5, got {mean_ratio}")

    # 3. Smuggled band [30, 350] Hz erases an out-of-band chirp at 400-480 Hz
    t = np.arange(N) / fs
    out_of_band = np.sin(2 * np.pi * (410.0 * t + 3.0 * t * t))
    X_oob = np.fft.rfft(out_of_band)
    band = (freqs >= 30.0) & (freqs <= 350.0)
    energy_kept = float(np.sum(np.abs(X_oob[band]) ** 2) / np.sum(np.abs(X_oob) ** 2))
    require(energy_kept < 1e-4, "expected [30,350] Hz band to erase 410+ Hz chirp")

    return {
        "negative_slice_crash_reproduced": crash_msg,
        "welch_ratio_mean_on_white_noise_expected_0.5_not_1.0": round(mean_ratio, 4),
        "out_of_band_410Hz_chirp_energy_retained_fraction": round(energy_kept, 8),
    }


def audit_pair_22(mod22) -> dict:
    N = 2048
    t = np.linspace(0, 1, N, endpoint=False)
    # 1. Clean coherent sinusoid & chirp -> phase_coherence vanishes!
    clean_sin = np.cos(2 * np.pi * 20.0 * t)
    clean_chirp = np.cos(2 * np.pi * (10.0 * t + 40.0 * t * t))
    # Constant-sign localized spike (after zero-mean subtraction)
    spike = np.zeros(N)
    spike[N // 2] = 10.0

    pc_sin = float(mod22.perceptual_invariants(clean_sin, t)["phase_coherence"])
    pc_chirp = float(mod22.perceptual_invariants(clean_chirp, t)["phase_coherence"])
    pc_spike = float(mod22.perceptual_invariants(spike, t)["phase_coherence"])
    require(pc_sin < 1e-12, f"expected clean sinusoid phase_coherence ~ 0, got {pc_sin}")
    require(pc_chirp < 0.05, f"expected clean chirp phase_coherence ~ 0, got {pc_chirp}")

    # 2. np.roll wraparound artifact on non-periodic 2D spectrogram with pulse at t=0
    freqs = np.linspace(4.0, 8.0, 32)
    X_edge = np.zeros((32, 256))
    # Put an UNDISPERSED pulse at column 0 (true kappa = 0)
    X_edge[:, 0] = 1.0
    # Wait: if true kappa = 0, roll by 0 gives kurtosis ~ 256; what if pulse is dispersed
    # across the boundary? Put a pulse that wraps from end to start at kappa=500:
    X_wrap = np.zeros((32, 256))
    for i, f in enumerate(freqs):
        idx = int(round(500.0 * (f ** -2))) % 256
        X_wrap[i, idx] = 1.0
    # Check that an undispersed pulse at t=0 vs a wrapped circular pulse both produce huge kurtosis
    res_wrap = mod22.perceptual_invariants(X_wrap, np.arange(256), freqs=freqs)

    return {
        "phase_coherence_clean_sinusoid": pc_sin,
        "phase_coherence_clean_chirp": round(pc_chirp, 6),
        "phase_coherence_isolated_spike": round(pc_spike, 6),
        "wraparound_circular_pulse_peak": [round(float(res_wrap["shear_kurtosis_peak"][0]), 3),
                                           round(float(res_wrap["shear_kurtosis_peak"][1]), 3)],
    }


def audit_pair_29_formulas() -> dict:
    # 1. F[440] Counterexample to Moran without Open Set Condition:
    # IFS f1(x)=x/2, f2(x)=x/2, f3(x)=x/2 + 1/2 on [0,1].
    # Attractor K* = [0,1], dim_H(K*) = 1, yet sum r_i^{d_f} = 3*(1/2)^{d_f} = 1 => d_f = log2(3) > 1.
    d_moran = float(np.log(3.0) / np.log(2.0))
    dim_H = 1.0
    require(d_moran > dim_H + 0.5, "Moran counterexample check failed")

    # 2. F[447] Counterexample to unconditional wavelet Holder <=> without vanishing-moment hypothesis:
    # f(x) = x^2 is C^infinity (so f in C^2(0)), with Haar wavelet psi = 1_{[0,1/2)} - 1_{[1/2,1)}
    # (only 1 vanishing moment, int x psi(x) dx = -1/4 != 0):
    # (W_psi f)(a, 0) = a^{-1/2} (int_0^{a/2} x^2 dx - int_{a/2}^a x^2 dx)
    #                 = a^{-1/2} (a^3/24 - 7 a^3/24) = -a^{5/2} / 4.
    # For alpha = 2, F[447] claims |(W_psi f)(a, 0)| <= C a^{2 + 1/2} = C a^{5/2} (passes at alpha=2!).
    # Try alpha = 3 (f(x)=x^2 is ALSO in C^3(0) since f'''=0!):
    # F[447] claims |(W_psi f)(a, 0)| <= C a^{3 + 1/2} = C a^{7/2},
    # yet exact |(W_psi f)(a, 0)| = (1/4) a^{5/2} >> a^{7/2} as a -> 0^+!
    # Ratio |(W_psi f)(a,0)| / a^{7/2} = 1/(4a) -> +infinity!
    a_vals = [1e-1, 1e-2, 1e-3, 1e-4]
    haar_exact = [abs(-0.25 * (a ** 2.5)) / (a ** 3.5) for a in a_vals]
    require(haar_exact[-1] == 2500.0, "Haar counterexample exact ratio mismatch")

    return {
        "F440_overlapping_IFS_moran_dim": round(d_moran, 6),
        "F440_true_hausdorff_dim": dim_H,
        "F447_haar_on_x2_at_alpha3_ratio_diverges_1_over_4a": haar_exact,
    }


def main() -> None:
    mod25 = load_mod("pair_25_block_00", "pair_25_block_00.py")
    mod20 = load_mod("pair_20_block_00", "pair_20_block_00.py")
    mod22 = load_mod("pair_22_block_05", "pair_22_block_05.py")

    out = {
        "pair_25_negative_controls": audit_pair_25(mod25),
        "pair_20_defects": audit_pair_20(mod20),
        "pair_22_defects": audit_pair_22(mod22),
        "pair_29_formula_counterexamples": audit_pair_29_formulas(),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
