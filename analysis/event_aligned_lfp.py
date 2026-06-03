#!/usr/bin/env python3
"""Compute condition-wise event-aligned LFP summaries for Dec 3."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_lfp(lfp_path: Path, n_channels: int) -> np.memmap:
    samples = lfp_path.stat().st_size // np.dtype("<i2").itemsize // n_channels
    return np.memmap(lfp_path, dtype="<i2", mode="r", shape=(samples, n_channels))


def robust_baseline_correct(segment: np.ndarray, time_axis: np.ndarray, baseline_end_s: float = 0.0) -> np.ndarray:
    baseline_mask = time_axis < baseline_end_s
    baseline = np.median(segment[baseline_mask], axis=0, keepdims=True)
    return segment - baseline


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lfp", type=Path, required=True)
    parser.add_argument("--sequence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=1250)
    parser.add_argument("--pre-s", type=float, default=1.0)
    parser.add_argument("--post-s", type=float, default=4.0)
    parser.add_argument("--max-trials-per-condition", type=int, default=50)
    parser.add_argument("--channels", type=int, nargs="*", default=None)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    sequence = pd.read_csv(args.sequence)
    lfp = load_lfp(args.lfp, args.n_channels)

    channels = args.channels if args.channels else list(range(args.n_channels))
    pre_samples = int(round(args.pre_s * args.sample_rate_hz))
    post_samples = int(round(args.post_s * args.sample_rate_hz))
    n_samples = pre_samples + post_samples
    time_axis = (np.arange(n_samples) - pre_samples) / args.sample_rate_hz

    rng = np.random.default_rng(321)
    condition_summaries = []
    condition_mean_by_channel = {}

    for condition, rows in sequence.groupby("condition", sort=True):
        rows = rows.sort_values("trial_number")
        if len(rows) > args.max_trials_per_condition:
            rows = rows.iloc[np.sort(rng.choice(len(rows), size=args.max_trials_per_condition, replace=False))]

        trial_means = []
        valid_trials = []
        for row in rows.itertuples(index=False):
            start = int(round(row.recording_start_time_s * args.sample_rate_hz)) - pre_samples
            stop = start + n_samples
            if start < 0 or stop > lfp.shape[0]:
                continue
            segment = np.asarray(lfp[start:stop, channels], dtype=np.float32)
            segment = robust_baseline_correct(segment, time_axis)
            trial_means.append(segment)
            valid_trials.append(int(row.trial_number))

        if not trial_means:
            continue

        stack = np.stack(trial_means, axis=0)
        mean = np.mean(stack, axis=0)
        sem = np.std(stack, axis=0, ddof=1) / np.sqrt(stack.shape[0]) if stack.shape[0] > 1 else np.zeros_like(mean)
        condition_mean_by_channel[condition] = mean

        stim_mask = (time_axis >= 0) & (time_axis < 3)
        pre_mask = time_axis < 0
        recovery_mask = time_axis >= 3
        abs_mean = np.mean(np.abs(stack), axis=(0, 1))
        stim_abs = np.mean(np.abs(stack[:, stim_mask, :]), axis=(0, 1))
        pre_abs = np.mean(np.abs(stack[:, pre_mask, :]), axis=(0, 1))
        recovery_abs = np.mean(np.abs(stack[:, recovery_mask, :]), axis=(0, 1))

        for channel_index, channel in enumerate(channels):
            condition_summaries.append(
                {
                    "condition": condition,
                    "channel": channel,
                    "n_trials": stack.shape[0],
                    "mean_abs_lfp": float(abs_mean[channel_index]),
                    "pre_abs_lfp": float(pre_abs[channel_index]),
                    "stim_abs_lfp": float(stim_abs[channel_index]),
                    "recovery_abs_lfp": float(recovery_abs[channel_index]),
                    "stim_minus_pre_abs_lfp": float(stim_abs[channel_index] - pre_abs[channel_index]),
                }
            )

        np.savez_compressed(
            args.output_dir / f"{condition}_mean_lfp.npz",
            time_s=time_axis,
            channels=np.asarray(channels),
            mean=mean,
            sem=sem,
            trial_numbers=np.asarray(valid_trials),
        )

    summary_df = pd.DataFrame(condition_summaries)
    summary_df.to_csv(args.output_dir / "condition_channel_lfp_summary.csv", index=False)

    channel_summary = (
        summary_df.groupby("channel", as_index=False)
        .agg(
            mean_stim_minus_pre_abs_lfp=("stim_minus_pre_abs_lfp", "mean"),
            max_stim_minus_pre_abs_lfp=("stim_minus_pre_abs_lfp", "max"),
            mean_pre_abs_lfp=("pre_abs_lfp", "mean"),
            mean_stim_abs_lfp=("stim_abs_lfp", "mean"),
        )
        .sort_values("mean_stim_minus_pre_abs_lfp", ascending=False)
    )
    channel_summary.to_csv(args.output_dir / "channel_lfp_response_ranking.csv", index=False)

    # Plot condition average collapsed across channels.
    fig, ax = plt.subplots(figsize=(11, 6))
    for condition in sorted(condition_mean_by_channel):
        mean = condition_mean_by_channel[condition]
        collapsed = np.mean(mean, axis=1)
        ax.plot(time_axis, collapsed, label=condition, linewidth=1.4)
    ax.axvspan(0, 3, color="gold", alpha=0.18, label="stim on")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.axvline(3, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Time from trial onset (s)")
    ax.set_ylabel("Mean baseline-corrected LFP")
    ax.set_title("Condition-Averaged LFP, Collapsed Across Channels")
    ax.legend(ncol=2, fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(args.output_dir / "condition_average_lfp_collapsed.png", dpi=180)
    plt.close(fig)

    # Heatmap of stim-pre amplitude change by condition and channel.
    pivot = summary_df.pivot(index="condition", columns="channel", values="stim_minus_pre_abs_lfp")
    fig, ax = plt.subplots(figsize=(14, 4.5))
    image = ax.imshow(pivot.to_numpy(), aspect="auto", interpolation="nearest", cmap="coolwarm")
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_xlabel("Channel")
    ax.set_title("Stimulus Window Minus Pre Window: Mean |LFP|")
    fig.colorbar(image, ax=ax, label="Mean |LFP| difference")
    fig.tight_layout()
    fig.savefig(args.output_dir / "condition_by_channel_lfp_response_heatmap.png", dpi=180)
    plt.close(fig)

    summary = {
        "lfp": str(args.lfp),
        "sequence": str(args.sequence),
        "output_dir": str(args.output_dir),
        "n_channels_input": args.n_channels,
        "channels_analyzed": channels,
        "sample_rate_hz": args.sample_rate_hz,
        "pre_s": args.pre_s,
        "post_s": args.post_s,
        "max_trials_per_condition": args.max_trials_per_condition,
        "conditions": sorted(condition_mean_by_channel),
        "summary_csv": str(args.output_dir / "condition_channel_lfp_summary.csv"),
        "channel_ranking_csv": str(args.output_dir / "channel_lfp_response_ranking.csv"),
        "note": "This is an exploratory LFP summary. It does not remove stimulation artifacts or median-subtract channels.",
    }
    (args.output_dir / "event_aligned_lfp_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
