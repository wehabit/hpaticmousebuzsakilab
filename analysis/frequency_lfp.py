#!/usr/bin/env python3
"""Frequency-specific LFP power summaries for the Dec 3 haptic session."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ANALYSIS_GROUPS = {
    "Group 96-127": range(96, 128),
    "Group 64-95": range(64, 96),
    "Group 32-63": range(32, 64),
    "Group 0-31": range(0, 32),
}

PHYSICAL_SHANKS = {
    "Physical Shank A (0-63)": range(0, 64),
    "Physical Shank B (64-127)": range(64, 128),
}


def load_lfp(path: Path, n_channels: int) -> np.memmap:
    samples = path.stat().st_size // np.dtype("<i2").itemsize // n_channels
    return np.memmap(path, dtype="<i2", mode="r", shape=(samples, n_channels))


def parse_condition(condition: str) -> tuple[int, int]:
    parts = condition.replace("amp", "").replace("freq", "").split("_")
    return int(parts[0]), int(parts[1])


def channel_group(channel: int) -> str:
    for name, channels in ANALYSIS_GROUPS.items():
        if channel in channels:
            return name
    raise ValueError(f"Channel {channel} is not in a known analysis group")


def physical_shank(channel: int) -> str:
    for name, channels in PHYSICAL_SHANKS.items():
        if channel in channels:
            return name
    raise ValueError(f"Channel {channel} is not in a known physical shank")


def band_power(
    data: np.ndarray,
    sample_rate_hz: float,
    target_hz: float,
    half_width_hz: float,
) -> np.ndarray:
    """Return average spectral power around target_hz for data shaped trials x time x channels."""
    window = np.hanning(data.shape[1]).astype(np.float32)
    centered = data - np.mean(data, axis=1, keepdims=True)
    spectrum = np.fft.rfft(centered * window[None, :, None], axis=1)
    freqs = np.fft.rfftfreq(data.shape[1], d=1.0 / sample_rate_hz)
    mask = (freqs >= target_hz - half_width_hz) & (freqs <= target_hz + half_width_hz)
    power = np.abs(spectrum[:, mask, :]) ** 2
    return np.mean(power, axis=(0, 1))


def extract_window(
    lfp: np.memmap,
    starts_s: np.ndarray,
    sample_rate_hz: float,
    offset_s: float,
    duration_s: float,
) -> np.ndarray:
    start_offsets = np.round((starts_s + offset_s) * sample_rate_hz).astype(int)
    n_samples = int(round(duration_s * sample_rate_hz))
    out = np.empty((len(start_offsets), n_samples, lfp.shape[1]), dtype=np.float32)
    for i, start in enumerate(start_offsets):
        stop = start + n_samples
        out[i] = np.asarray(lfp[start:stop], dtype=np.float32)
    return out


def plot_group_power(summary: pd.DataFrame, output: Path, group_col: str, title: str) -> None:
    grouped = (
        summary.groupby([group_col, "amplitude", "frequency"], as_index=False)
        .agg(
            driven_log2_change=("driven_log2_power_change", "mean"),
            sem=("driven_log2_power_change", lambda x: x.std(ddof=1) / np.sqrt(len(x))),
        )
    )
    group_names = list(dict.fromkeys(summary[group_col]))
    amps = [100, 180, 250]
    colors = {5: "#2F6BBA", 26: "#C43A31"}
    x = np.arange(len(amps))
    width = 0.34

    fig, axes = plt.subplots(1, len(group_names), figsize=(4.2 * len(group_names), 4.8), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, group_name in zip(axes, group_names):
        sub = grouped[grouped[group_col] == group_name]
        for offset, freq in [(-width / 2, 5), (width / 2, 26)]:
            rows = sub[sub["frequency"] == freq].set_index("amplitude").reindex(amps)
            ax.bar(
                x + offset,
                rows["driven_log2_change"],
                yerr=rows["sem"],
                width=width,
                capsize=3,
                color=colors[freq],
                alpha=0.88,
                label=f"{freq} Hz",
            )
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(group_name)
        ax.set_xticks(x)
        ax.set_xticklabels(amps)
        ax.set_xlabel("Amplitude")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Driven frequency power: log2(stim / pre)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2)
    fig.suptitle(title)
    fig.tight_layout(rect=(0, 0.08, 1, 0.93))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_channel_heatmap(summary: pd.DataFrame, output: Path) -> None:
    ordered_conditions = [
        "amp100_freq5",
        "amp180_freq5",
        "amp250_freq5",
        "amp100_freq26",
        "amp180_freq26",
        "amp250_freq26",
    ]
    pivot = summary.pivot(index="condition", columns="channel", values="driven_log2_power_change")
    pivot = pivot.reindex([c for c in ordered_conditions if c in pivot.index])
    vmax = np.nanpercentile(np.abs(pivot.to_numpy()), 98)

    fig, ax = plt.subplots(figsize=(14, 4.8))
    image = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_xlabel("Channel")
    ax.set_title("Driven Frequency Power Change by Channel")
    for boundary in [32, 64, 96]:
        ax.axvline(boundary - 0.5, color="black", linewidth=0.7, alpha=0.5)
    fig.colorbar(image, ax=ax, label="log2(stim / pre)")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_frequency_specificity(summary: pd.DataFrame, output: Path) -> None:
    grouped = (
        summary.groupby(["condition", "analysis_group"], as_index=False)
        .agg(
            driven=("driven_log2_power_change", "mean"),
            five=("five_hz_log2_power_change", "mean"),
            twenty_six=("twenty_six_hz_log2_power_change", "mean"),
        )
    )
    conditions = sorted(grouped["condition"].unique(), key=lambda c: parse_condition(c)[::-1])
    group_names = list(ANALYSIS_GROUPS)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, value_col, label in zip(
        axes,
        ["five", "twenty_six"],
        ["5 Hz power change", "26 Hz power change"],
    ):
        pivot = grouped.pivot(index="condition", columns="analysis_group", values=value_col)
        pivot = pivot.reindex(conditions)[group_names]
        vmax = np.nanpercentile(np.abs(pivot.to_numpy()), 98)
        image = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
        ax.set_xticks(np.arange(len(group_names)))
        ax.set_xticklabels(group_names, rotation=35, ha="right")
        ax.set_yticks(np.arange(len(conditions)))
        ax.set_yticklabels(conditions)
        ax.set_title(label)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="log2(stim / pre)")
    fig.suptitle("Frequency-Specific LFP Power, Same Trials Viewed at 5 Hz and 26 Hz")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lfp", type=Path, required=True)
    parser.add_argument("--sequence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=1250)
    parser.add_argument("--window-duration-s", type=float, default=2.8)
    parser.add_argument("--artifact-margin-s", type=float, default=0.1)
    parser.add_argument("--band-half-width-hz", type=float, default=1.0)
    parser.add_argument("--max-trials-per-condition", type=int, default=200)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    sequence = pd.read_csv(args.sequence)
    lfp = load_lfp(args.lfp, args.n_channels)
    rng = np.random.default_rng(321)
    eps = np.finfo(np.float64).tiny

    rows_out = []
    for condition, rows in sequence.groupby("condition", sort=True):
        amp, freq = parse_condition(condition)
        rows = rows.sort_values("trial_number")
        if len(rows) > args.max_trials_per_condition:
            keep = np.sort(rng.choice(len(rows), args.max_trials_per_condition, replace=False))
            rows = rows.iloc[keep]
        starts = rows["recording_start_time_s"].to_numpy(dtype=float)

        pre = extract_window(
            lfp,
            starts,
            args.sample_rate_hz,
            offset_s=-(args.window_duration_s + args.artifact_margin_s),
            duration_s=args.window_duration_s,
        )
        stim = extract_window(
            lfp,
            starts,
            args.sample_rate_hz,
            offset_s=args.artifact_margin_s,
            duration_s=args.window_duration_s,
        )

        pre_five = band_power(pre, args.sample_rate_hz, 5, args.band_half_width_hz)
        stim_five = band_power(stim, args.sample_rate_hz, 5, args.band_half_width_hz)
        pre_twenty_six = band_power(pre, args.sample_rate_hz, 26, args.band_half_width_hz)
        stim_twenty_six = band_power(stim, args.sample_rate_hz, 26, args.band_half_width_hz)
        driven_pre = pre_five if freq == 5 else pre_twenty_six
        driven_stim = stim_five if freq == 5 else stim_twenty_six

        for channel in range(args.n_channels):
            rows_out.append(
                {
                    "condition": condition,
                    "amplitude": amp,
                    "frequency": freq,
                    "channel": channel,
                    "analysis_group": channel_group(channel),
                    "physical_shank": physical_shank(channel),
                    "n_trials": len(rows),
                    "pre_5hz_power": float(pre_five[channel]),
                    "stim_5hz_power": float(stim_five[channel]),
                    "five_hz_log2_power_change": float(np.log2((stim_five[channel] + eps) / (pre_five[channel] + eps))),
                    "pre_26hz_power": float(pre_twenty_six[channel]),
                    "stim_26hz_power": float(stim_twenty_six[channel]),
                    "twenty_six_hz_log2_power_change": float(
                        np.log2((stim_twenty_six[channel] + eps) / (pre_twenty_six[channel] + eps))
                    ),
                    "driven_pre_power": float(driven_pre[channel]),
                    "driven_stim_power": float(driven_stim[channel]),
                    "driven_log2_power_change": float(
                        np.log2((driven_stim[channel] + eps) / (driven_pre[channel] + eps))
                    ),
                }
            )

    summary = pd.DataFrame(rows_out)
    summary.to_csv(args.output_dir / "frequency_lfp_channel_summary.csv", index=False)
    group_summary = (
        summary.groupby(["condition", "amplitude", "frequency", "analysis_group"], as_index=False)
        .agg(
            n_channels=("channel", "count"),
            driven_log2_power_change=("driven_log2_power_change", "mean"),
            five_hz_log2_power_change=("five_hz_log2_power_change", "mean"),
            twenty_six_hz_log2_power_change=("twenty_six_hz_log2_power_change", "mean"),
        )
    )
    group_summary.to_csv(args.output_dir / "frequency_lfp_group_summary.csv", index=False)

    shank_summary = (
        summary.groupby(["condition", "amplitude", "frequency", "physical_shank"], as_index=False)
        .agg(
            n_channels=("channel", "count"),
            driven_log2_power_change=("driven_log2_power_change", "mean"),
            five_hz_log2_power_change=("five_hz_log2_power_change", "mean"),
            twenty_six_hz_log2_power_change=("twenty_six_hz_log2_power_change", "mean"),
        )
    )
    shank_summary.to_csv(args.output_dir / "frequency_lfp_physical_shank_summary.csv", index=False)

    plot_group_power(summary, args.output_dir / "driven_power_change_by_analysis_group.png", "analysis_group", "Driven-Frequency LFP Power by Analysis Group")
    plot_group_power(summary, args.output_dir / "driven_power_change_by_physical_shank.png", "physical_shank", "Driven-Frequency LFP Power by Physical Shank")
    plot_channel_heatmap(summary, args.output_dir / "driven_power_change_by_channel.png")
    plot_frequency_specificity(summary, args.output_dir / "frequency_specificity_by_group.png")

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Frequency LFP</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1300px} img{width:100%;border:1px solid #ddd;margin-bottom:32px}</style>",
        "</head><body><h1>Dec 3 Frequency-Specific LFP</h1>",
        f"<p>Pre and stim windows are each {args.window_duration_s:g} s. Stim window starts {args.artifact_margin_s:g} s after onset to avoid onset artifact.</p>",
        "<p>Values are log2(stim power / pre power). Positive values mean power increased during stimulation.</p>",
        "<h2>Driven Power by Analysis Group</h2><img src='driven_power_change_by_analysis_group.png'>",
        "<h2>Driven Power by Physical Shank</h2><img src='driven_power_change_by_physical_shank.png'>",
        "<h2>Driven Power by Channel</h2><img src='driven_power_change_by_channel.png'>",
        "<h2>5 Hz and 26 Hz Specificity</h2><img src='frequency_specificity_by_group.png'>",
        "</body></html>",
    ]
    (args.output_dir / "index.html").write_text("\n".join(html))

    report = {
        "output_dir": str(args.output_dir),
        "channel_summary_csv": str(args.output_dir / "frequency_lfp_channel_summary.csv"),
        "group_summary_csv": str(args.output_dir / "frequency_lfp_group_summary.csv"),
        "physical_shank_summary_csv": str(args.output_dir / "frequency_lfp_physical_shank_summary.csv"),
        "window_duration_s": args.window_duration_s,
        "artifact_margin_s": args.artifact_margin_s,
        "band_half_width_hz": args.band_half_width_hz,
        "max_trials_per_condition": args.max_trials_per_condition,
        "note": "Frequency analysis uses pre window immediately before trial onset and stim window after onset artifact margin.",
    }
    (args.output_dir / "frequency_lfp_run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
