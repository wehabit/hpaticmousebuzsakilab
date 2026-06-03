#!/usr/bin/env python3
"""Reference and bad-channel sensitivity checks for Dec 3 driven-frequency LFP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ANALYSIS_GROUPS = {
    "Group 96-127": list(range(96, 128)),
    "Group 64-95": list(range(64, 96)),
    "Group 32-63": list(range(32, 64)),
    "Group 0-31": list(range(0, 32)),
}

PHYSICAL_SHANKS = {
    "Physical Shank A (0-63)": list(range(0, 64)),
    "Physical Shank B (64-127)": list(range(64, 128)),
}

REFERENCE_MODES = ("raw", "physical_shank_median", "analysis_group_median")


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
    raise ValueError(f"Unknown channel {channel}")


def physical_shank(channel: int) -> str:
    for name, channels in PHYSICAL_SHANKS.items():
        if channel in channels:
            return name
    raise ValueError(f"Unknown channel {channel}")


def load_bad_channels(path: Path | None, field: str) -> set[int]:
    if path is None:
        return set()
    data = json.loads(path.read_text())
    return {int(ch) for ch in data.get(field, [])}


def reference_segment(segment: np.ndarray, mode: str, excluded_channels: set[int]) -> np.ndarray:
    if mode == "raw":
        return segment

    referenced = segment.copy()
    groups = PHYSICAL_SHANKS if mode == "physical_shank_median" else ANALYSIS_GROUPS
    for channels in groups.values():
        usable = [ch for ch in channels if ch not in excluded_channels]
        if not usable:
            continue
        ref = np.median(segment[:, usable], axis=1, keepdims=True)
        referenced[:, channels] = segment[:, channels] - ref
    return referenced


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


def band_power(data: np.ndarray, sample_rate_hz: float, target_hz: float, half_width_hz: float) -> np.ndarray:
    window = np.hanning(data.shape[1]).astype(np.float32)
    centered = data - np.mean(data, axis=1, keepdims=True)
    spectrum = np.fft.rfft(centered * window[None, :, None], axis=1)
    freqs = np.fft.rfftfreq(data.shape[1], d=1.0 / sample_rate_hz)
    mask = (freqs >= target_hz - half_width_hz) & (freqs <= target_hz + half_width_hz)
    power = np.abs(spectrum[:, mask, :]) ** 2
    return np.mean(power, axis=(0, 1))


def plot_reference_condition_summary(summary: pd.DataFrame, output: Path) -> None:
    condition_summary = (
        summary.groupby(["reference_mode", "condition", "amplitude", "frequency"], as_index=False)
        .agg(driven=("driven_log2_power_change", "mean"))
    )
    conditions = [
        "amp100_freq5",
        "amp180_freq5",
        "amp250_freq5",
        "amp100_freq26",
        "amp180_freq26",
        "amp250_freq26",
    ]
    x = np.arange(len(conditions))
    width = 0.25
    colors = {
        "raw": "#4C78A8",
        "physical_shank_median": "#F58518",
        "analysis_group_median": "#54A24B",
    }

    fig, ax = plt.subplots(figsize=(12, 5))
    for i, mode in enumerate(REFERENCE_MODES):
        rows = condition_summary[condition_summary["reference_mode"] == mode].set_index("condition").reindex(conditions)
        ax.bar(x + (i - 1) * width, rows["driven"], width=width, color=colors[mode], label=mode)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, rotation=30, ha="right")
    ax.set_ylabel("Mean driven-frequency log2(stim / pre)")
    ax.set_title("Driven-Frequency LFP Sensitivity to Reference Choice")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_reference_group_heatmaps(summary: pd.DataFrame, output: Path) -> None:
    group_summary = (
        summary.groupby(["reference_mode", "condition", "analysis_group"], as_index=False)
        .agg(driven=("driven_log2_power_change", "mean"))
    )
    conditions = [
        "amp100_freq5",
        "amp180_freq5",
        "amp250_freq5",
        "amp100_freq26",
        "amp180_freq26",
        "amp250_freq26",
    ]
    groups = list(ANALYSIS_GROUPS)
    vmax = np.nanpercentile(np.abs(group_summary["driven"]), 98)
    vmax = max(vmax, 0.1)

    fig, axes = plt.subplots(1, len(REFERENCE_MODES), figsize=(15, 5), sharey=True)
    for ax, mode in zip(axes, REFERENCE_MODES):
        pivot = (
            group_summary[group_summary["reference_mode"] == mode]
            .pivot(index="condition", columns="analysis_group", values="driven")
            .reindex(conditions)[groups]
        )
        image = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
        ax.set_title(mode)
        ax.set_xticks(np.arange(len(groups)))
        ax.set_xticklabels(groups, rotation=35, ha="right")
        ax.set_yticks(np.arange(len(conditions)))
        ax.set_yticklabels(conditions)
    fig.colorbar(image, ax=axes.ravel().tolist(), fraction=0.025, pad=0.02, label="log2(stim / pre)")
    fig.suptitle("Driven-Frequency Power by Analysis Group and Reference")
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lfp", type=Path, required=True)
    parser.add_argument("--sequence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bad-channels-json", type=Path, default=None)
    parser.add_argument("--bad-channel-field", default="candidate_bad_channels")
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=1250)
    parser.add_argument("--window-duration-s", type=float, default=2.8)
    parser.add_argument("--artifact-margin-s", type=float, default=0.1)
    parser.add_argument("--band-half-width-hz", type=float, default=1.0)
    parser.add_argument("--max-trials-per-condition", type=int, default=200)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    lfp = load_lfp(args.lfp, args.n_channels)
    sequence = pd.read_csv(args.sequence)
    excluded_channels = load_bad_channels(args.bad_channels_json, args.bad_channel_field)
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
        pre_raw = extract_window(
            lfp,
            starts,
            args.sample_rate_hz,
            offset_s=-(args.window_duration_s + args.artifact_margin_s),
            duration_s=args.window_duration_s,
        )
        stim_raw = extract_window(
            lfp,
            starts,
            args.sample_rate_hz,
            offset_s=args.artifact_margin_s,
            duration_s=args.window_duration_s,
        )

        for reference_mode in REFERENCE_MODES:
            pre = np.empty_like(pre_raw)
            stim = np.empty_like(stim_raw)
            for trial_idx in range(pre.shape[0]):
                pre[trial_idx] = reference_segment(pre_raw[trial_idx], reference_mode, excluded_channels)
                stim[trial_idx] = reference_segment(stim_raw[trial_idx], reference_mode, excluded_channels)

            pre_power = band_power(pre, args.sample_rate_hz, freq, args.band_half_width_hz)
            stim_power = band_power(stim, args.sample_rate_hz, freq, args.band_half_width_hz)
            for channel in range(args.n_channels):
                if channel in excluded_channels:
                    continue
                rows_out.append(
                    {
                        "reference_mode": reference_mode,
                        "condition": condition,
                        "amplitude": amp,
                        "frequency": freq,
                        "channel": channel,
                        "analysis_group": channel_group(channel),
                        "physical_shank": physical_shank(channel),
                        "n_trials": len(rows),
                        "pre_power": float(pre_power[channel]),
                        "stim_power": float(stim_power[channel]),
                        "driven_log2_power_change": float(np.log2((stim_power[channel] + eps) / (pre_power[channel] + eps))),
                    }
                )

    summary = pd.DataFrame(rows_out)
    summary.to_csv(args.output_dir / "reference_sensitivity_channel_summary.csv", index=False)
    condition_summary = (
        summary.groupby(["reference_mode", "condition", "amplitude", "frequency"], as_index=False)
        .agg(
            n_channels=("channel", "count"),
            driven_log2_power_change=("driven_log2_power_change", "mean"),
        )
    )
    condition_summary.to_csv(args.output_dir / "reference_sensitivity_condition_summary.csv", index=False)
    group_summary = (
        summary.groupby(["reference_mode", "condition", "amplitude", "frequency", "analysis_group"], as_index=False)
        .agg(
            n_channels=("channel", "count"),
            driven_log2_power_change=("driven_log2_power_change", "mean"),
        )
    )
    group_summary.to_csv(args.output_dir / "reference_sensitivity_group_summary.csv", index=False)

    plot_reference_condition_summary(summary, args.output_dir / "reference_condition_summary.png")
    plot_reference_group_heatmaps(summary, args.output_dir / "reference_group_heatmaps.png")

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Reference Sensitivity</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1300px} img{width:100%;border:1px solid #ddd;margin-bottom:32px}</style>",
        "</head><body><h1>Dec 3 Reference Sensitivity</h1>",
        f"<p>Excluded channels from <code>{args.bad_channel_field}</code>: {sorted(excluded_channels)}</p>",
        "<p>Values are driven-frequency log2(stim power / pre power).</p>",
        "<h2>Condition Summary</h2><img src='reference_condition_summary.png'>",
        "<h2>Group Heatmaps</h2><img src='reference_group_heatmaps.png'>",
        "</body></html>",
    ]
    (args.output_dir / "index.html").write_text("\n".join(html))

    report = {
        "output_dir": str(args.output_dir),
        "bad_channels_json": str(args.bad_channels_json) if args.bad_channels_json else None,
        "bad_channel_field": args.bad_channel_field,
        "excluded_channels": sorted(excluded_channels),
        "reference_modes": list(REFERENCE_MODES),
        "condition_summary_csv": str(args.output_dir / "reference_sensitivity_condition_summary.csv"),
        "group_summary_csv": str(args.output_dir / "reference_sensitivity_group_summary.csv"),
    }
    (args.output_dir / "reference_sensitivity_run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
