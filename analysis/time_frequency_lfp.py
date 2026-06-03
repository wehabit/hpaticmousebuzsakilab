#!/usr/bin/env python3
"""Time-frequency LFP maps for the Dec 3 haptic session."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import spectrogram


ANALYSIS_GROUPS = {
    "Group 96-127": list(range(96, 128)),
    "Group 64-95": list(range(64, 96)),
    "Group 32-63": list(range(32, 64)),
    "Group 0-31": list(range(0, 32)),
}


def load_lfp(path: Path, n_channels: int) -> np.memmap:
    samples = path.stat().st_size // np.dtype("<i2").itemsize // n_channels
    return np.memmap(path, dtype="<i2", mode="r", shape=(samples, n_channels))


def parse_condition(condition: str) -> tuple[int, int]:
    parts = condition.replace("amp", "").replace("freq", "").split("_")
    return int(parts[0]), int(parts[1])


def condition_sort_key(condition: str) -> tuple[int, int]:
    amp, freq = parse_condition(condition)
    return freq, amp


def compute_group_spectrogram(
    signal: np.ndarray,
    sample_rate_hz: float,
    nperseg: int,
    noverlap: int,
    max_freq_hz: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    freqs, times, power = spectrogram(
        signal,
        fs=sample_rate_hz,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        detrend="constant",
        scaling="density",
        mode="psd",
    )
    keep = freqs <= max_freq_hz
    return freqs[keep], times, power[keep]


def baseline_log2_change(power: np.ndarray, times: np.ndarray) -> np.ndarray:
    baseline_mask = times < 0
    baseline = np.nanmedian(power[:, baseline_mask], axis=1, keepdims=True)
    eps = np.finfo(np.float64).tiny
    return np.log2((power + eps) / (baseline + eps))


def plot_condition_grid(
    condition_maps: dict[str, dict[str, np.ndarray]],
    freqs: np.ndarray,
    times: np.ndarray,
    output: Path,
) -> None:
    conditions = sorted(condition_maps, key=condition_sort_key)
    groups = list(ANALYSIS_GROUPS)
    all_values = np.concatenate([condition_maps[c][g].ravel() for c in conditions for g in groups])
    vmax = np.nanpercentile(np.abs(all_values), 98)
    vmax = max(vmax, 0.25)

    fig, axes = plt.subplots(len(conditions), len(groups), figsize=(16, 16), sharex=True, sharey=True)
    for row, condition in enumerate(conditions):
        for col, group in enumerate(groups):
            ax = axes[row, col]
            image = ax.pcolormesh(
                times,
                freqs,
                condition_maps[condition][group],
                shading="auto",
                cmap="coolwarm",
                vmin=-vmax,
                vmax=vmax,
            )
            ax.axvline(0, color="black", linewidth=0.8)
            ax.axvline(3, color="black", linewidth=0.8, linestyle="--")
            ax.axvspan(0, 3, color="gold", alpha=0.08)
            if row == 0:
                ax.set_title(group)
            if col == 0:
                ax.set_ylabel(f"{condition}\nHz")
            if row == len(conditions) - 1:
                ax.set_xlabel("Time from onset (s)")
    fig.suptitle("Dec 3 LFP Time-Frequency Maps: log2(power / pre baseline)")
    cbar = fig.colorbar(image, ax=axes.ravel().tolist(), fraction=0.018, pad=0.01)
    cbar.set_label("log2 power change")
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_driven_frequency_timecourses(
    condition_maps: dict[str, dict[str, np.ndarray]],
    freqs: np.ndarray,
    times: np.ndarray,
    output: Path,
) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True, sharey=True)
    axes = axes.ravel()
    colors = {
        "Group 96-127": "#595959",
        "Group 64-95": "#D95F02",
        "Group 32-63": "#1B9E77",
        "Group 0-31": "#2F6BBA",
    }

    for ax, condition in zip(axes, sorted(condition_maps, key=condition_sort_key)):
        _, freq = parse_condition(condition)
        band = (freqs >= freq - 1) & (freqs <= freq + 1)
        for group, color in colors.items():
            trace = np.nanmean(condition_maps[condition][group][band], axis=0)
            ax.plot(times, trace, color=color, linewidth=1.6, label=group)
        ax.axhline(0, color="black", linewidth=0.7)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.axvline(3, color="black", linewidth=0.8, linestyle="--")
        ax.axvspan(0, 3, color="gold", alpha=0.12)
        ax.set_title(condition)
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("Driven band log2 power change")
    axes[3].set_ylabel("Driven band log2 power change")
    for ax in axes[3:]:
        ax.set_xlabel("Time from onset (s)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4)
    fig.suptitle("Driven-Frequency Time Course by Analysis Group")
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
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
    parser.add_argument("--nperseg", type=int, default=512)
    parser.add_argument("--noverlap", type=int, default=448)
    parser.add_argument("--max-freq-hz", type=float, default=80)
    parser.add_argument("--max-trials-per-condition", type=int, default=200)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    lfp = load_lfp(args.lfp, args.n_channels)
    sequence = pd.read_csv(args.sequence)
    rng = np.random.default_rng(321)

    pre_samples = int(round(args.pre_s * args.sample_rate_hz))
    post_samples = int(round(args.post_s * args.sample_rate_hz))
    n_samples = pre_samples + post_samples

    condition_maps: dict[str, dict[str, np.ndarray]] = {}
    rows_out = []
    freqs_out = None
    times_out = None

    for condition, rows in sequence.groupby("condition", sort=True):
        rows = rows.sort_values("trial_number")
        if len(rows) > args.max_trials_per_condition:
            keep = np.sort(rng.choice(len(rows), args.max_trials_per_condition, replace=False))
            rows = rows.iloc[keep]

        accumulators: dict[str, np.ndarray | None] = {name: None for name in ANALYSIS_GROUPS}
        valid_trials = 0

        for row in rows.itertuples(index=False):
            start = int(round(row.recording_start_time_s * args.sample_rate_hz)) - pre_samples
            stop = start + n_samples
            if start < 0 or stop > lfp.shape[0]:
                continue
            segment = np.asarray(lfp[start:stop], dtype=np.float32)
            time_axis = (np.arange(n_samples) - pre_samples) / args.sample_rate_hz
            baseline = np.nanmedian(segment[time_axis < 0], axis=0, keepdims=True)
            segment = segment - baseline

            for group, channels in ANALYSIS_GROUPS.items():
                group_signal = np.nanmean(segment[:, channels], axis=1)
                freqs, times, power = compute_group_spectrogram(
                    group_signal,
                    args.sample_rate_hz,
                    args.nperseg,
                    args.noverlap,
                    args.max_freq_hz,
                )
                times = times - args.pre_s
                if accumulators[group] is None:
                    accumulators[group] = power.astype(np.float64)
                    freqs_out = freqs
                    times_out = times
                else:
                    accumulators[group] += power
            valid_trials += 1

        condition_maps[condition] = {}
        amp, driven_freq = parse_condition(condition)
        for group, accumulator in accumulators.items():
            if accumulator is None:
                continue
            mean_power = accumulator / valid_trials
            tf_map = baseline_log2_change(mean_power, times_out)
            condition_maps[condition][group] = tf_map

            baseline_mask = times_out < 0
            sustained_mask = (times_out >= 0.2) & (times_out <= 2.8)
            onset_mask = (times_out >= 0) & (times_out < 0.4)
            offset_mask = (times_out >= 2.8) & (times_out <= 3.4)
            driven_band = (freqs_out >= driven_freq - 1) & (freqs_out <= driven_freq + 1)
            rows_out.append(
                {
                    "condition": condition,
                    "amplitude": amp,
                    "frequency": driven_freq,
                    "analysis_group": group,
                    "n_trials": valid_trials,
                    "baseline_driven_log2_power": float(np.nanmean(tf_map[driven_band][:, baseline_mask])),
                    "onset_driven_log2_power": float(np.nanmean(tf_map[driven_band][:, onset_mask])),
                    "sustained_driven_log2_power": float(np.nanmean(tf_map[driven_band][:, sustained_mask])),
                    "offset_driven_log2_power": float(np.nanmean(tf_map[driven_band][:, offset_mask])),
                }
            )

    if freqs_out is None or times_out is None:
        raise RuntimeError("No valid trials were available for time-frequency analysis")

    np.savez_compressed(
        args.output_dir / "time_frequency_group_maps.npz",
        freqs=freqs_out,
        times=times_out,
        conditions=np.asarray(sorted(condition_maps, key=condition_sort_key)),
        groups=np.asarray(list(ANALYSIS_GROUPS)),
        maps=np.asarray(
            [
                [condition_maps[condition][group] for group in ANALYSIS_GROUPS]
                for condition in sorted(condition_maps, key=condition_sort_key)
            ]
        ),
    )
    summary = pd.DataFrame(rows_out)
    summary.to_csv(args.output_dir / "time_frequency_summary.csv", index=False)

    plot_condition_grid(condition_maps, freqs_out, times_out, args.output_dir / "time_frequency_condition_grid.png")
    plot_driven_frequency_timecourses(
        condition_maps,
        freqs_out,
        times_out,
        args.output_dir / "driven_frequency_timecourses.png",
    )

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Time-Frequency LFP</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1400px} img{width:100%;border:1px solid #ddd;margin-bottom:32px}</style>",
        "</head><body><h1>Dec 3 Time-Frequency LFP</h1>",
        "<p>Maps are averaged across trials and channels within each 32-channel analysis group.</p>",
        "<p>Color is log2(power / pre-stim baseline) at each frequency.</p>",
        "<h2>Condition Grid</h2><img src='time_frequency_condition_grid.png'>",
        "<h2>Driven Frequency Time Courses</h2><img src='driven_frequency_timecourses.png'>",
        "</body></html>",
    ]
    (args.output_dir / "index.html").write_text("\n".join(html))

    report = {
        "output_dir": str(args.output_dir),
        "summary_csv": str(args.output_dir / "time_frequency_summary.csv"),
        "maps_npz": str(args.output_dir / "time_frequency_group_maps.npz"),
        "pre_s": args.pre_s,
        "post_s": args.post_s,
        "nperseg": args.nperseg,
        "noverlap": args.noverlap,
        "max_freq_hz": args.max_freq_hz,
        "max_trials_per_condition": args.max_trials_per_condition,
        "note": "Time-frequency maps are trial-averaged group mean LFP spectrograms, baseline normalized by pre-stim power.",
    }
    (args.output_dir / "time_frequency_run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
