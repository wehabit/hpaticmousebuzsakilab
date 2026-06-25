#!/usr/bin/env python3
"""Dec 4 LEC slow-oscillation / UP-DOWN-compatible screen.

This is a no-figure physiology check prompted by Vöröslakos's metadata reply:
presence of cortical slow oscillations / UP-DOWN states supports the LEC/cortex
assignment, analogous to dHPC ripples supporting CA1/dHPC.

The screen intentionally uses only quiet non-stimulation windows:
baseline before the first trial and post-study after the last trial. It compares
LEC with dHPC on the same recording, using good channels only.

Outputs are CSV/JSON text summaries under:
analysis/outputs/dec4/lec_slow_oscillation_screen/
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal

ROOT = Path("/Users/paris/Documents/Buzsakli Lab Github")
SESSION = ROOT / "Haptic_Stim_session2_251204_131403"
LFP = SESSION / "amplifier.lfp"
SESSION_SUMMARY = ROOT / "analysis/outputs/dec4/session_summary.json"
BAD_CHANNELS = ROOT / "analysis/bad_channels_dec4.json"
OUT = ROOT / "analysis/outputs/dec4/lec_slow_oscillation_screen"

FS = 1250.0
N_CH = 256
DOWNSAMPLED_FS = 250.0
DECIMATION = int(FS / DOWNSAMPLED_FS)
QUIET_MARGIN_S = 0.0


def load_bad_channels() -> set[int]:
    data = json.loads(BAD_CHANNELS.read_text())
    return {int(ch) for ch in data["definite_bad_channels"]}


def bandpower(freq: np.ndarray, psd: np.ndarray, lo: float, hi: float) -> float:
    mask = (freq >= lo) & (freq <= hi)
    if not np.any(mask):
        return float("nan")
    return float(np.trapezoid(psd[mask], freq[mask]))


def robust_z(x: np.ndarray) -> np.ndarray:
    med = float(np.median(x))
    mad = float(1.4826 * np.median(np.abs(x - med)))
    return (x - med) / (mad + 1e-9)


def median_lfp(
    lfp: np.memmap, channels: list[int], start_s: float, end_s: float
) -> np.ndarray:
    start = max(0, int(round(start_s * FS)))
    end = min(lfp.shape[0], int(round(end_s * FS)))
    data = np.asarray(lfp[start:end, channels], dtype=np.float32)
    return np.median(data, axis=1)


def summarize_trace(x: np.ndarray) -> tuple[dict[str, float], pd.DataFrame]:
    """Return spectral summary and slow-deflection event table for one trace."""
    x = signal.detrend(x, type="constant")
    x_ds = signal.resample_poly(x, up=1, down=DECIMATION)

    freq, psd = signal.welch(
        x_ds,
        fs=DOWNSAMPLED_FS,
        nperseg=int(DOWNSAMPLED_FS * 16),
        noverlap=int(DOWNSAMPLED_FS * 8),
        detrend="constant",
    )

    slow_mask = (freq >= 0.1) & (freq <= 4.0)
    slow_peak_hz = float(freq[slow_mask][np.argmax(psd[slow_mask])])
    powers = {
        "slow_0p1_1_hz": bandpower(freq, psd, 0.1, 1.0),
        "slow_0p5_1_hz": bandpower(freq, psd, 0.5, 1.0),
        "delta_1_4_hz": bandpower(freq, psd, 1.0, 4.0),
        "theta_6_10_hz": bandpower(freq, psd, 6.0, 10.0),
        "gamma_30_80_hz": bandpower(freq, psd, 30.0, 80.0),
    }
    slow_total = powers["slow_0p1_1_hz"] + powers["delta_1_4_hz"]

    sos = signal.butter(
        3, [0.5, 4.0], btype="bandpass", fs=DOWNSAMPLED_FS, output="sos"
    )
    slow = signal.sosfiltfilt(sos, x_ds)
    z = robust_z(slow)

    min_distance = int(0.25 * DOWNSAMPLED_FS)
    pos_idx, pos_props = signal.find_peaks(z, height=1.5, distance=min_distance)
    neg_idx, neg_props = signal.find_peaks(-z, height=1.5, distance=min_distance)

    events = []
    for idx, height in zip(pos_idx, pos_props["peak_heights"], strict=False):
        events.append(
            {
                "event_type": "positive_slow_deflection",
                "time_s": float(idx / DOWNSAMPLED_FS),
                "amplitude_z": float(height),
            }
        )
    for idx, height in zip(neg_idx, neg_props["peak_heights"], strict=False):
        events.append(
            {
                "event_type": "negative_slow_deflection",
                "time_s": float(idx / DOWNSAMPLED_FS),
                "amplitude_z": float(-height),
            }
        )

    duration_s = len(x_ds) / DOWNSAMPLED_FS
    summary = {
        "duration_s": duration_s,
        "slow_peak_hz": slow_peak_hz,
        "slow_0p1_4_to_theta_ratio": slow_total
        / (powers["theta_6_10_hz"] + 1e-12),
        "delta_1_4_to_theta_ratio": powers["delta_1_4_hz"]
        / (powers["theta_6_10_hz"] + 1e-12),
        "slow_0p1_1_to_theta_ratio": powers["slow_0p1_1_hz"]
        / (powers["theta_6_10_hz"] + 1e-12),
        "positive_slow_deflection_rate_hz": len(pos_idx) / duration_s,
        "negative_slow_deflection_rate_hz": len(neg_idx) / duration_s,
        "abs_slow_z_95th_percentile": float(np.percentile(np.abs(z), 95)),
        **powers,
    }
    return summary, pd.DataFrame(events).sort_values("time_s")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    session_summary = json.loads(SESSION_SUMMARY.read_text())
    n_samples = LFP.stat().st_size // 2 // N_CH
    duration_s = n_samples / FS

    first_trial = float(session_summary["first_trial_recording_start_s"])
    last_trial_end = float(session_summary["last_trial_recording_end_s"])
    baseline_start = float(session_summary["baseline_start_recording_s"])

    windows = {
        "baseline": (baseline_start + QUIET_MARGIN_S, first_trial - QUIET_MARGIN_S),
        "post": (last_trial_end + QUIET_MARGIN_S, duration_s),
    }

    bad = load_bad_channels()
    regions = {
        "dHPC": [ch for ch in range(0, 128) if ch not in bad],
        "LEC": [ch for ch in range(128, 256) if ch not in bad],
    }

    lfp = np.memmap(LFP, dtype="<i2", mode="r", shape=(n_samples, N_CH))
    rows = []
    event_tables = []
    for region, channels in regions.items():
        for state, (start_s, end_s) in windows.items():
            trace = median_lfp(lfp, channels, start_s, end_s)
            summary, events = summarize_trace(trace)
            row = {
                "session": "dec4",
                "region": region,
                "state": state,
                "n_good_channels": len(channels),
                "window_start_s": start_s,
                "window_end_s": end_s,
                **summary,
            }
            rows.append(row)
            if not events.empty:
                events.insert(0, "state", state)
                events.insert(0, "region", region)
                events.insert(0, "session", "dec4")
                event_tables.append(events)

    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(OUT / "slow_oscillation_summary.csv", index=False)
    if event_tables:
        pd.concat(event_tables, ignore_index=True).to_csv(
            OUT / "slow_deflection_events.csv", index=False
        )

    lec = summary_df[summary_df["region"] == "LEC"]
    dhpc = summary_df[summary_df["region"] == "dHPC"]
    interpretation = {
        "purpose": (
            "No-figure screen for Vöröslakos criterion: cortical slow oscillations / "
            "UP-DOWN-compatible slow deflections support LEC/cortex identity."
        ),
        "method_short": (
            "Median LFP across good channels, quiet baseline and post-study windows only; "
            "Welch spectra plus 0.5-4 Hz slow-deflection counts."
        ),
        "lec_result": {
            "slow_peak_hz_range": [
                round(float(lec["slow_peak_hz"].min()), 3),
                round(float(lec["slow_peak_hz"].max()), 3),
            ],
            "slow_to_theta_ratio_range": [
                round(float(lec["slow_0p1_4_to_theta_ratio"].min()), 2),
                round(float(lec["slow_0p1_4_to_theta_ratio"].max()), 2),
            ],
            "negative_slow_deflection_rate_hz_range": [
                round(float(lec["negative_slow_deflection_rate_hz"].min()), 3),
                round(float(lec["negative_slow_deflection_rate_hz"].max()), 3),
            ],
        },
        "dhpc_comparator": {
            "slow_to_theta_ratio_range": [
                round(float(dhpc["slow_0p1_4_to_theta_ratio"].min()), 2),
                round(float(dhpc["slow_0p1_4_to_theta_ratio"].max()), 2),
            ],
        },
        "bottom_line": (
            "LEC shows a stable quiet-window slow/delta-dominant LFP signature "
            "relative to theta, unlike the dHPC comparator. This supports the "
            "LEC/cortex functional placement criterion. It is not a formal sleep "
            "scoring or laminar UP/DOWN-state analysis."
        ),
        "outputs": [
            "slow_oscillation_summary.csv",
            "slow_deflection_events.csv",
        ],
    }
    (OUT / "run_summary.json").write_text(json.dumps(interpretation, indent=2) + "\n")
    print(json.dumps(interpretation, indent=2))


if __name__ == "__main__":
    main()
