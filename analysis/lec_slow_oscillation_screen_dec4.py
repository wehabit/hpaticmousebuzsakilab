#!/usr/bin/env python3
"""Dec 4 LEC slow-oscillation / UP-DOWN-compatible screen.

This is a physiology check prompted by Vöröslakos's metadata reply:
presence of cortical slow oscillations / UP-DOWN states supports the LEC/cortex
assignment, analogous to dHPC ripples supporting CA1/dHPC.

The screen intentionally uses only quiet non-stimulation windows:
baseline before the first trial and post-study after the last trial. It compares
LEC with dHPC on the same recording, using good channels only.

Outputs are CSV/JSON summaries plus a summary figure under:
analysis/outputs/dec4/lec_slow_oscillation_screen/
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

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


def summarize_trace(x: np.ndarray) -> tuple[dict[str, float], pd.DataFrame, pd.DataFrame]:
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
    spectra = pd.DataFrame({"freq_hz": freq, "psd": psd})
    return summary, pd.DataFrame(events).sort_values("time_s"), spectra


def plot_summary(summary_df: pd.DataFrame, spectra_df: pd.DataFrame, out: Path) -> None:
    """Create a presentation-friendly soft slow/delta screen figure."""
    colors = {"LEC": "#8C1515", "dHPC": "#53565A"}
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), gridspec_kw={"height_ratios": [1.3, 1]})

    # Spectra: one panel per quiet state, LEC vs dHPC.
    for ax, state in zip(axes[0], ["baseline", "post"], strict=True):
        for region in ["dHPC", "LEC"]:
            sub = spectra_df[(spectra_df.state == state) & (spectra_df.region == region)]
            sub = sub[(sub.freq_hz >= 0.1) & (sub.freq_hz <= 20.0)]
            ax.plot(sub.freq_hz, sub.psd, color=colors[region], lw=2, label=region)
        ax.axvspan(0.1, 4.0, color="#DAD7CB", alpha=0.45, label="slow/delta 0.1-4 Hz")
        ax.axvspan(6.0, 10.0, color="#B6B1A9", alpha=0.28, label="theta 6-10 Hz")
        ax.set_yscale("log")
        ax.set_xlim(0.1, 20)
        ax.set_xlabel("frequency (Hz)")
        ax.set_ylabel("PSD (a.u.)")
        ax.set_title(f"{state}: quiet-window median LFP spectrum")
        ax.grid(alpha=0.18)
    axes[0][0].legend(fontsize=8.5, loc="upper right")

    # Ratio bars: the key soft placement result.
    ax = axes[1][0]
    order = [("dHPC", "baseline"), ("dHPC", "post"), ("LEC", "baseline"), ("LEC", "post")]
    vals = []
    labels = []
    bar_colors = []
    for region, state in order:
        row = summary_df[(summary_df.region == region) & (summary_df.state == state)].iloc[0]
        vals.append(float(row.slow_0p1_4_to_theta_ratio))
        labels.append(f"{region}\n{state}")
        bar_colors.append(colors[region])
    ax.bar(range(len(vals)), vals, color=bar_colors, alpha=0.9)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("slow/delta-to-theta ratio")
    ax.set_title("Soft cortex-like signature: LEC is slow/delta-dominant")
    ax.grid(axis="y", alpha=0.2)
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.025, f"{v:.1f}", ha="center", va="bottom", fontsize=9)

    # Slow-deflection rates: supportive, not formal UP/DOWN scoring.
    ax = axes[1][1]
    neg = []
    pos = []
    for region, state in order:
        row = summary_df[(summary_df.region == region) & (summary_df.state == state)].iloc[0]
        neg.append(float(row.negative_slow_deflection_rate_hz))
        pos.append(float(row.positive_slow_deflection_rate_hz))
    x = np.arange(len(order))
    width = 0.38
    ax.bar(x - width / 2, neg, width, color="#2E2D29", alpha=0.85, label="negative")
    ax.bar(x + width / 2, pos, width, color="#8C1515", alpha=0.82, label="positive")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("slow-deflection rate (/s)")
    ax.set_title("Slow deflections in quiet windows (supportive only)")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(fontsize=8.5)

    fig.suptitle(
        "Dec 4 LEC soft slow/delta screen — supports cortex-like LEC physiology, not formal UP/DOWN proof\n"
        "Quiet baseline/post only; LEC has strong slow/delta power relative to theta, unlike dHPC",
        fontsize=12.5,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(out / "lec_slow_oscillation_screen_dec4.png", dpi=180)
    plt.close(fig)


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
    spectra_tables = []
    for region, channels in regions.items():
        for state, (start_s, end_s) in windows.items():
            trace = median_lfp(lfp, channels, start_s, end_s)
            summary, events, spectra = summarize_trace(trace)
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
            spectra.insert(0, "state", state)
            spectra.insert(0, "region", region)
            spectra.insert(0, "session", "dec4")
            spectra_tables.append(spectra)

    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(OUT / "slow_oscillation_summary.csv", index=False)
    spectra_df = pd.concat(spectra_tables, ignore_index=True)
    spectra_df.to_csv(OUT / "slow_oscillation_spectra.csv", index=False)
    if event_tables:
        pd.concat(event_tables, ignore_index=True).to_csv(
            OUT / "slow_deflection_events.csv", index=False
        )
    plot_summary(summary_df, spectra_df, OUT)

    lec = summary_df[summary_df["region"] == "LEC"]
    dhpc = summary_df[summary_df["region"] == "dHPC"]
    interpretation = {
        "purpose": (
            "Figure + table screen for Vöröslakos criterion: cortical slow oscillations / "
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
            "lec_slow_oscillation_screen_dec4.png",
            "slow_oscillation_summary.csv",
            "slow_oscillation_spectra.csv",
            "slow_deflection_events.csv",
        ],
    }
    (OUT / "run_summary.json").write_text(json.dumps(interpretation, indent=2) + "\n")
    print(json.dumps(interpretation, indent=2))


if __name__ == "__main__":
    main()
