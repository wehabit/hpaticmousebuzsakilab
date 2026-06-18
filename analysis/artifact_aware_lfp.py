#!/usr/bin/env python3
"""Artifact-aware event-aligned LFP summaries for Dec 3."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SHANKS = {
    "Shank 1 (96-127)": range(96, 128),
    "Shank 2 (64-95)": range(64, 96),
    "Shank 3 (32-63)": range(32, 64),
    "Shank 4 (0-31)": range(0, 32),
}


def load_lfp(path: Path, n_channels: int) -> np.memmap:
    samples = path.stat().st_size // np.dtype("<i2").itemsize // n_channels
    return np.memmap(path, dtype="<i2", mode="r", shape=(samples, n_channels))


def parse_condition(condition: str) -> tuple[int, int]:
    parts = condition.replace("amp", "").replace("freq", "").split("_")
    return int(parts[0]), int(parts[1])


def window_mean_abs(stack: np.ndarray, time_s: np.ndarray, start_s: float, end_s: float) -> np.ndarray:
    mask = (time_s >= start_s) & (time_s < end_s)
    return np.mean(np.abs(stack[:, mask, :]), axis=(0, 1))


def plot_artifact_windows(summary: pd.DataFrame, output: Path) -> None:
    shank_summary = (
        summary.groupby(["condition", "shank"], as_index=False)
        .agg(
            onset=("onset_minus_pre_abs_lfp", "mean"),
            sustained=("sustained_minus_pre_abs_lfp", "mean"),
            offset=("offset_minus_pre_abs_lfp", "mean"),
            recovery=("recovery_minus_pre_abs_lfp", "mean"),
        )
    )
    condition_summary = shank_summary.groupby("condition", as_index=False)[["onset", "sustained", "offset", "recovery"]].mean()
    condition_summary["amplitude"], condition_summary["frequency"] = zip(*condition_summary["condition"].map(parse_condition))
    condition_summary = condition_summary.sort_values(["frequency", "amplitude"])

    fig, axes = plt.subplots(1, 2, figsize=(15, 5), sharey=True)
    colors = {"onset": "#E45756", "sustained": "#4C78A8", "offset": "#F58518", "recovery": "#54A24B"}
    width = 0.2
    x = np.arange(3)
    amps = [100, 180, 250]
    for ax, freq in zip(axes, [5, 26]):
        sub = condition_summary[condition_summary["frequency"] == freq].set_index("amplitude").reindex(amps)
        for i, name in enumerate(["onset", "sustained", "offset", "recovery"]):
            ax.bar(x + (i - 1.5) * width, sub[name], width=width, color=colors[name], label=name)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"{freq} Hz")
        ax.set_xticks(x)
        ax.set_xticklabels(amps)
        ax.set_xlabel("Amplitude")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Window mean |LFP| - pre mean |LFP|")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4)
    fig.suptitle("Artifact Check: Onset/Offset vs Sustained LFP")
    fig.tight_layout(rect=(0, 0.1, 1, 0.93))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_sustained_by_shank(summary: pd.DataFrame, output: Path) -> None:
    shank_summary = (
        summary.groupby(["shank", "amplitude", "frequency"], as_index=False)
        .agg(
            response=("sustained_minus_pre_abs_lfp", "mean"),
            sem=("sustained_minus_pre_abs_lfp", lambda x: x.std(ddof=1) / np.sqrt(len(x))),
        )
    )
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharey=True)
    axes = axes.ravel()
    amps = [100, 180, 250]
    x = np.arange(len(amps))
    width = 0.35
    colors = {5: "#4C78A8", 26: "#E45756"}

    for ax, shank in zip(axes, SHANKS):
        sub = shank_summary[shank_summary["shank"] == shank]
        for offset, freq in [(-width / 2, 5), (width / 2, 26)]:
            rows = sub[sub["frequency"] == freq].set_index("amplitude").reindex(amps)
            ax.bar(
                x + offset,
                rows["response"],
                yerr=rows["sem"],
                width=width,
                capsize=3,
                color=colors[freq],
                alpha=0.85,
                label=f"{freq} Hz",
            )
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(amps)
        ax.set_title(shank)
        ax.set_xlabel("Amplitude")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Sustained stim - pre mean |LFP|")
    axes[2].set_ylabel("Sustained stim - pre mean |LFP|")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2)
    fig.suptitle("Sustained LFP Response, Onset/Offset Excluded")
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lfp", type=Path, required=True)
    parser.add_argument("--sequence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=1250)
    parser.add_argument("--pre-s", type=float, default=1.0)
    parser.add_argument("--post-s", type=float, default=4.0)
    parser.add_argument("--artifact-margin-s", type=float, default=0.1)
    parser.add_argument("--max-trials-per-condition", type=int, default=100)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    lfp = load_lfp(args.lfp, args.n_channels)
    sequence = pd.read_csv(args.sequence)
    pre_samples = int(round(args.pre_s * args.sample_rate_hz))
    post_samples = int(round(args.post_s * args.sample_rate_hz))
    n_samples = pre_samples + post_samples
    time_s = (np.arange(n_samples) - pre_samples) / args.sample_rate_hz
    rng = np.random.default_rng(321)

    rows_out = []
    for condition, rows in sequence.groupby("condition", sort=True):
        amp, freq = parse_condition(condition)
        rows = rows.sort_values("trial_number")
        if len(rows) > args.max_trials_per_condition:
            rows = rows.iloc[np.sort(rng.choice(len(rows), args.max_trials_per_condition, replace=False))]

        segments = []
        trial_numbers = []
        for row in rows.itertuples(index=False):
            start = int(round(row.recording_start_time_s * args.sample_rate_hz)) - pre_samples
            stop = start + n_samples
            if start < 0 or stop > lfp.shape[0]:
                continue
            segment = np.asarray(lfp[start:stop], dtype=np.float32)
            baseline = np.median(segment[time_s < 0], axis=0, keepdims=True)
            segments.append(segment - baseline)
            trial_numbers.append(int(row.trial_number))

        if not segments:
            continue
        stack = np.stack(segments, axis=0)

        pre_abs = window_mean_abs(stack, time_s, -args.pre_s, 0)
        onset_abs = window_mean_abs(stack, time_s, 0, args.artifact_margin_s)
        sustained_abs = window_mean_abs(stack, time_s, args.artifact_margin_s, 3 - args.artifact_margin_s)
        offset_abs = window_mean_abs(stack, time_s, 3 - args.artifact_margin_s, 3 + args.artifact_margin_s)
        recovery_abs = window_mean_abs(stack, time_s, 3 + args.artifact_margin_s, args.post_s)

        for channel in range(args.n_channels):
            shank = next(name for name, chs in SHANKS.items() if channel in chs)
            rows_out.append(
                {
                    "condition": condition,
                    "amplitude": amp,
                    "frequency": freq,
                    "channel": channel,
                    "shank": shank,
                    "n_trials": len(trial_numbers),
                    "pre_abs_lfp": float(pre_abs[channel]),
                    "onset_abs_lfp": float(onset_abs[channel]),
                    "sustained_abs_lfp": float(sustained_abs[channel]),
                    "offset_abs_lfp": float(offset_abs[channel]),
                    "recovery_abs_lfp": float(recovery_abs[channel]),
                    "onset_minus_pre_abs_lfp": float(onset_abs[channel] - pre_abs[channel]),
                    "sustained_minus_pre_abs_lfp": float(sustained_abs[channel] - pre_abs[channel]),
                    "offset_minus_pre_abs_lfp": float(offset_abs[channel] - pre_abs[channel]),
                    "recovery_minus_pre_abs_lfp": float(recovery_abs[channel] - pre_abs[channel]),
                }
            )

    summary = pd.DataFrame(rows_out)
    summary.to_csv(args.output_dir / "artifact_aware_lfp_summary.csv", index=False)
    plot_artifact_windows(summary, args.output_dir / "artifact_window_comparison.png")
    plot_sustained_by_shank(summary, args.output_dir / "sustained_response_by_shank.png")

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Artifact-Aware LFP</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px} img{width:100%;max-width:1200px;border:1px solid #ddd;margin-bottom:32px}</style>",
        "</head><body><h1>Dec 3 Artifact-Aware LFP</h1>",
        f"<p>Artifact margin: {args.artifact_margin_s} s around onset and offset. Sustained window is {args.artifact_margin_s} to {3 - args.artifact_margin_s} s.</p>",
        "<h2>artifact_window_comparison.png</h2><img src='artifact_window_comparison.png'>",
        "<h2>sustained_response_by_shank.png</h2><img src='sustained_response_by_shank.png'>",
        "</body></html>",
    ]
    (args.output_dir / "index.html").write_text("\n".join(html))

    report = {
        "output_dir": str(args.output_dir),
        "summary_csv": str(args.output_dir / "artifact_aware_lfp_summary.csv"),
        "artifact_margin_s": args.artifact_margin_s,
        "max_trials_per_condition": args.max_trials_per_condition,
        "note": "Sustained response excludes the first/last artifact-margin seconds around stimulation onset/offset.",
    }
    (args.output_dir / "artifact_aware_lfp_run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
