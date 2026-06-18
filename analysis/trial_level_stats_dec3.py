#!/usr/bin/env python3
"""Trial-level Dec 3 LFP metrics with bootstrap confidence intervals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ANALYSIS_GROUPS = {
    "Group 96-127": list(range(96, 128)),
    "Group 64-95": list(range(64, 96)),
    "Group 32-63": list(range(32, 64)),
    "Group 0-31": list(range(0, 32)),
}


def load_lfp(path: Path, n_channels: int) -> np.memmap:
    samples = path.stat().st_size // np.dtype("<i2").itemsize // n_channels
    return np.memmap(path, dtype="<i2", mode="r", shape=(samples, n_channels))


def load_bad_channels(path: Path | None, field: str) -> set[int]:
    if path is None:
        return set()
    data = json.loads(path.read_text())
    return {int(ch) for ch in data.get(field, [])}


def parse_condition(condition: str) -> tuple[int, int]:
    parts = condition.replace("amp", "").replace("freq", "").split("_")
    return int(parts[0]), int(parts[1])


def condition_sort_key(condition: str) -> tuple[int, int]:
    amp, freq = parse_condition(condition)
    return freq, amp


def reference_segment(segment: np.ndarray, mode: str, excluded_channels: set[int]) -> np.ndarray:
    if mode == "raw":
        return segment
    if mode != "analysis_group_median":
        raise ValueError(f"Unsupported reference mode for this script: {mode}")

    referenced = segment.copy()
    for channels in ANALYSIS_GROUPS.values():
        usable = [ch for ch in channels if ch not in excluded_channels]
        if not usable:
            continue
        ref = np.median(segment[:, usable], axis=1, keepdims=True)
        referenced[:, channels] = segment[:, channels] - ref
    return referenced


def band_power_1d(signal: np.ndarray, sample_rate_hz: float, target_hz: float, half_width_hz: float) -> float:
    centered = signal - np.mean(signal)
    window = np.hanning(centered.size)
    spectrum = np.fft.rfft(centered * window)
    freqs = np.fft.rfftfreq(centered.size, d=1.0 / sample_rate_hz)
    mask = (freqs >= target_hz - half_width_hz) & (freqs <= target_hz + half_width_hz)
    return float(np.mean(np.abs(spectrum[mask]) ** 2))


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return np.nan, np.nan, np.nan
    boot = rng.choice(values, size=(n_boot, values.size), replace=True).mean(axis=1)
    return float(values.mean()), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def plot_metric(summary: pd.DataFrame, metric: str, ylabel: str, output: Path) -> None:
    conditions = sorted(summary["condition"].unique(), key=condition_sort_key)
    groups = list(ANALYSIS_GROUPS)
    fig, axes = plt.subplots(1, len(groups), figsize=(16, 4.8), sharey=True)
    colors = {5: "#2F6BBA", 26: "#C43A31"}

    for ax, group in zip(axes, groups):
        sub = summary[summary["analysis_group"] == group].set_index("condition").reindex(conditions)
        x = np.arange(len(conditions))
        y = sub[f"{metric}_mean"].to_numpy()
        lo = sub[f"{metric}_ci_low"].to_numpy()
        hi = sub[f"{metric}_ci_high"].to_numpy()
        freqs = [parse_condition(c)[1] for c in conditions]
        ax.bar(x, y, color=[colors.get(f, "#888888") for f in freqs], alpha=0.86)
        ax.errorbar(x, y, yerr=[y - lo, hi - y], fmt="none", color="black", linewidth=0.8, capsize=3)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(group)
        ax.set_xticks(x)
        ax.set_xticklabels(conditions, rotation=45, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel(ylabel)
    fig.suptitle(ylabel + " by Condition and Analysis Group")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lfp", type=Path, required=True)
    parser.add_argument("--sequence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bad-channels-json", type=Path, default=None)
    parser.add_argument("--bad-channel-field", default="candidate_bad_channels")
    parser.add_argument("--reference-mode", default="analysis_group_median")
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=1250)
    parser.add_argument("--pre-s", type=float, default=1.0)
    parser.add_argument("--post-s", type=float, default=4.0)
    parser.add_argument("--artifact-margin-s", type=float, default=0.1)
    parser.add_argument("--spectral-window-s", type=float, default=2.8)
    parser.add_argument("--band-half-width-hz", type=float, default=1.0)
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    lfp = load_lfp(args.lfp, args.n_channels)
    sequence = pd.read_csv(args.sequence)
    excluded_channels = load_bad_channels(args.bad_channels_json, args.bad_channel_field)
    rng = np.random.default_rng(321)
    eps = np.finfo(np.float64).tiny

    pre_samples = int(round(args.pre_s * args.sample_rate_hz))
    post_samples = int(round(args.post_s * args.sample_rate_hz))
    n_samples = pre_samples + post_samples
    spectral_samples = int(round(args.spectral_window_s * args.sample_rate_hz))
    time_s = (np.arange(n_samples) - pre_samples) / args.sample_rate_hz
    pre_mask = time_s < 0
    sustained_mask = (time_s >= args.artifact_margin_s) & (time_s < 3 - args.artifact_margin_s)
    offset_mask = (time_s >= 3 - args.artifact_margin_s) & (time_s < 3 + args.artifact_margin_s)

    rows_out = []
    for row in sequence.sort_values("trial_number").itertuples(index=False):
        amp, freq = parse_condition(row.condition)
        start = int(round(row.recording_start_time_s * args.sample_rate_hz)) - pre_samples
        stop = start + n_samples
        spectral_pre_start = int(round((row.recording_start_time_s - args.spectral_window_s - args.artifact_margin_s) * args.sample_rate_hz))
        spectral_pre_stop = spectral_pre_start + spectral_samples
        spectral_stim_start = int(round((row.recording_start_time_s + args.artifact_margin_s) * args.sample_rate_hz))
        spectral_stim_stop = spectral_stim_start + spectral_samples
        if start < 0 or stop > lfp.shape[0] or spectral_pre_start < 0 or spectral_stim_stop > lfp.shape[0]:
            continue
        segment = np.asarray(lfp[start:stop], dtype=np.float32)
        segment = reference_segment(segment, args.reference_mode, excluded_channels)
        baseline = np.median(segment[pre_mask], axis=0, keepdims=True)
        segment = segment - baseline

        spectral_pre = np.asarray(lfp[spectral_pre_start:spectral_pre_stop], dtype=np.float32)
        spectral_stim = np.asarray(lfp[spectral_stim_start:spectral_stim_stop], dtype=np.float32)
        spectral_pre = reference_segment(spectral_pre, args.reference_mode, excluded_channels)
        spectral_stim = reference_segment(spectral_stim, args.reference_mode, excluded_channels)
        spectral_baseline = np.median(spectral_pre, axis=0, keepdims=True)
        spectral_pre = spectral_pre - spectral_baseline
        spectral_stim = spectral_stim - spectral_baseline

        for group, channels in ANALYSIS_GROUPS.items():
            usable = [ch for ch in channels if ch not in excluded_channels]
            if not usable:
                continue
            group_signal = np.mean(segment[:, usable], axis=1)
            group_pre_spectral = np.mean(spectral_pre[:, usable], axis=1)
            group_stim_spectral = np.mean(spectral_stim[:, usable], axis=1)
            pre_abs = float(np.mean(np.abs(group_signal[pre_mask])))
            sustained_abs = float(np.mean(np.abs(group_signal[sustained_mask])))
            offset_abs = float(np.mean(np.abs(group_signal[offset_mask])))
            pre_power = band_power_1d(group_pre_spectral, args.sample_rate_hz, freq, args.band_half_width_hz)
            stim_power = band_power_1d(group_stim_spectral, args.sample_rate_hz, freq, args.band_half_width_hz)
            rows_out.append(
                {
                    "trial_number": int(row.trial_number),
                    "condition": row.condition,
                    "amplitude": amp,
                    "frequency": freq,
                    "analysis_group": group,
                    "n_channels_used": len(usable),
                    "sustained_broadband_delta": sustained_abs - pre_abs,
                    "offset_broadband_delta": offset_abs - pre_abs,
                    "driven_power_log2_delta": float(np.log2((stim_power + eps) / (pre_power + eps))),
                }
            )

    trial_metrics = pd.DataFrame(rows_out)
    trial_metrics.to_csv(args.output_dir / "trial_level_metrics.csv", index=False)

    summary_rows = []
    for (condition, group), sub in trial_metrics.groupby(["condition", "analysis_group"], sort=False):
        amp, freq = parse_condition(condition)
        summary = {
            "condition": condition,
            "amplitude": amp,
            "frequency": freq,
            "analysis_group": group,
            "n_trials": int(sub["trial_number"].nunique()),
        }
        for metric in ["sustained_broadband_delta", "offset_broadband_delta", "driven_power_log2_delta"]:
            mean, lo, hi = bootstrap_ci(sub[metric].to_numpy(), rng, args.n_bootstrap)
            summary[f"{metric}_mean"] = mean
            summary[f"{metric}_ci_low"] = lo
            summary[f"{metric}_ci_high"] = hi
        summary_rows.append(summary)

    summary = pd.DataFrame(summary_rows).sort_values(["frequency", "amplitude", "analysis_group"])
    summary.to_csv(args.output_dir / "trial_level_summary_ci.csv", index=False)

    condition_summary_rows = []
    for condition, sub in trial_metrics.groupby("condition", sort=False):
        amp, freq = parse_condition(condition)
        condition_row = {"condition": condition, "amplitude": amp, "frequency": freq}
        grouped = sub.groupby(["trial_number"], as_index=False)[
            ["sustained_broadband_delta", "offset_broadband_delta", "driven_power_log2_delta"]
        ].mean()
        condition_row["n_trials"] = int(grouped["trial_number"].nunique())
        for metric in ["sustained_broadband_delta", "offset_broadband_delta", "driven_power_log2_delta"]:
            mean, lo, hi = bootstrap_ci(grouped[metric].to_numpy(), rng, args.n_bootstrap)
            condition_row[f"{metric}_mean"] = mean
            condition_row[f"{metric}_ci_low"] = lo
            condition_row[f"{metric}_ci_high"] = hi
        condition_summary_rows.append(condition_row)
    condition_summary = pd.DataFrame(condition_summary_rows).sort_values(["frequency", "amplitude"])
    condition_summary.to_csv(args.output_dir / "condition_summary_ci.csv", index=False)

    plot_metric(summary, "sustained_broadband_delta", "Trial-Level Sustained Broadband Delta", args.output_dir / "sustained_broadband_ci.png")
    plot_metric(summary, "offset_broadband_delta", "Trial-Level Offset Broadband Delta", args.output_dir / "offset_broadband_ci.png")
    plot_metric(summary, "driven_power_log2_delta", "Trial-Level Driven-Frequency Power Delta", args.output_dir / "driven_power_ci.png")

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Trial-Level Stats</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1300px;line-height:1.45}"
        "img{width:100%;border:1px solid #d9dee5;margin-bottom:30px}"
        "a{color:#0f6b78;font-weight:600}</style></head><body>",
        "<h1>Dec 3 Trial-Level Statistics</h1>",
        "<p>Bootstrap 95% confidence intervals across trials, using confirmed bad-channel exclusion and analysis-group median reference. Broadband here is group-mean LFP amplitude after channel averaging.</p>",
        "<h2>Sustained Broadband</h2><img src='sustained_broadband_ci.png'>",
        "<h2>Offset Broadband</h2><img src='offset_broadband_ci.png'>",
        "<h2>Driven-Frequency Power</h2><img src='driven_power_ci.png'>",
        "<p>Back to <a href='../RESULTS_DASHBOARD.html'>main dashboard</a>.</p>",
        "</body></html>",
    ]
    (args.output_dir / "index.html").write_text("\n".join(html))

    report = {
        "output_dir": str(args.output_dir),
        "trial_metrics_csv": str(args.output_dir / "trial_level_metrics.csv"),
        "summary_ci_csv": str(args.output_dir / "trial_level_summary_ci.csv"),
        "condition_summary_ci_csv": str(args.output_dir / "condition_summary_ci.csv"),
        "excluded_channels": sorted(excluded_channels),
        "reference_mode": args.reference_mode,
        "spectral_window_s": args.spectral_window_s,
        "n_bootstrap": args.n_bootstrap,
    }
    (args.output_dir / "trial_level_stats_run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
