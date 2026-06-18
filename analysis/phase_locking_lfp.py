#!/usr/bin/env python3
"""Trial-to-trial phase-locking analysis for Dec 3 haptic LFP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, hilbert, sosfiltfilt


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

    referenced = segment.copy()
    groups = PHYSICAL_SHANKS if mode == "physical_shank_median" else ANALYSIS_GROUPS
    for channels in groups.values():
        usable = [ch for ch in channels if ch not in excluded_channels]
        if not usable:
            continue
        ref = np.median(segment[:, usable], axis=1, keepdims=True)
        referenced[:, channels] = segment[:, channels] - ref
    return referenced


def bandpass(data: np.ndarray, sample_rate_hz: float, center_hz: float, half_width_hz: float) -> np.ndarray:
    low = max(0.5, center_hz - half_width_hz)
    high = center_hz + half_width_hz
    sos = butter(4, [low, high], btype="bandpass", fs=sample_rate_hz, output="sos")
    return sosfiltfilt(sos, data, axis=1)


def circular_mean_phase(phases: np.ndarray, axis: int = 0) -> np.ndarray:
    return np.angle(np.mean(np.exp(1j * phases), axis=axis))


def compute_plv(phases: np.ndarray, axis: int = 0) -> np.ndarray:
    return np.abs(np.mean(np.exp(1j * phases), axis=axis))


def plot_plv_timecourses(summary_npz: Path, output: Path) -> None:
    data = np.load(summary_npz, allow_pickle=True)
    conditions = list(data["conditions"])
    groups = list(data["groups"])
    time_s = data["time_s"]
    plv = data["plv"]
    colors = {
        "Group 96-127": "#595959",
        "Group 64-95": "#D95F02",
        "Group 32-63": "#1B9E77",
        "Group 0-31": "#2F6BBA",
    }

    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True, sharey=True)
    axes = axes.ravel()
    for ax, condition in zip(axes, conditions):
        condition_idx = conditions.index(condition)
        for group_idx, group in enumerate(groups):
            ax.plot(time_s, plv[condition_idx, group_idx], color=colors.get(group, "#888888"), linewidth=1.5, label=group)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.axvline(3, color="black", linewidth=0.8, linestyle="--")
        ax.axvspan(0, 3, color="gold", alpha=0.12)
        ax.set_title(condition)
        ax.grid(alpha=0.2)
    axes[0].set_ylabel("Trial-to-trial phase locking (PLV)")
    axes[3].set_ylabel("Trial-to-trial phase locking (PLV)")
    for ax in axes[3:]:
        ax.set_xlabel("Time from stimulation onset (s)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4)
    fig.suptitle("Driven-Frequency Phase Locking Across Trials")
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_plv_summary(summary: pd.DataFrame, output: Path) -> None:
    condition_summary = (
        summary.groupby(["condition", "amplitude", "frequency"], as_index=False)
        .agg(
            pre=("pre_plv", "mean"),
            sustained=("sustained_plv", "mean"),
            offset=("offset_plv", "mean"),
            delta=("sustained_minus_pre_plv", "mean"),
        )
        .sort_values(["frequency", "amplitude"])
    )
    conditions = condition_summary["condition"].tolist()
    x = np.arange(len(conditions))
    width = 0.22

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(x - width, condition_summary["pre"], width=width, color="#8A8F98", label="pre")
    ax.bar(x, condition_summary["sustained"], width=width, color="#2F6BBA", label="sustained ON")
    ax.bar(x + width, condition_summary["offset"], width=width, color="#D95F02", label="offset")
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, rotation=30, ha="right")
    ax.set_ylabel("Mean PLV across analysis groups")
    ax.set_title("Driven-Frequency Phase Locking by Condition")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    colors = ["#2F6BBA" if freq == 5 else "#C43A31" for freq in condition_summary["frequency"]]
    ax.bar(x, condition_summary["delta"], color=colors, alpha=0.88)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(conditions, rotation=30, ha="right")
    ax.set_ylabel("Sustained PLV - pre PLV")
    ax.set_title("Phase-Locking Increase During Sustained Stimulation")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output.with_name("plv_sustained_minus_pre.png"), dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lfp", type=Path, required=True)
    parser.add_argument("--sequence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bad-channels-json", type=Path, default=None)
    parser.add_argument("--bad-channel-field", default="candidate_bad_channels")
    parser.add_argument("--reference-mode", choices=["raw", "physical_shank_median", "analysis_group_median"], default="analysis_group_median")
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=1250)
    parser.add_argument("--pre-s", type=float, default=1.0)
    parser.add_argument("--post-s", type=float, default=4.0)
    parser.add_argument("--band-half-width-hz", type=float, default=1.5)
    parser.add_argument("--max-trials-per-condition", type=int, default=200)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    lfp = load_lfp(args.lfp, args.n_channels)
    sequence = pd.read_csv(args.sequence)
    excluded_channels = load_bad_channels(args.bad_channels_json, args.bad_channel_field)
    rng = np.random.default_rng(321)

    pre_samples = int(round(args.pre_s * args.sample_rate_hz))
    post_samples = int(round(args.post_s * args.sample_rate_hz))
    n_samples = pre_samples + post_samples
    time_s = (np.arange(n_samples) - pre_samples) / args.sample_rate_hz
    pre_mask = time_s < 0
    sustained_mask = (time_s >= 0.2) & (time_s <= 2.8)
    offset_mask = (time_s >= 2.8) & (time_s <= 3.4)

    conditions = sorted(sequence["condition"].unique(), key=condition_sort_key)
    groups = list(ANALYSIS_GROUPS)
    plv_maps = np.full((len(conditions), len(groups), n_samples), np.nan, dtype=np.float32)
    rows_out = []

    for condition_idx, condition in enumerate(conditions):
        amp, freq = parse_condition(condition)
        rows = sequence[sequence["condition"] == condition].sort_values("trial_number")
        if len(rows) > args.max_trials_per_condition:
            keep = np.sort(rng.choice(len(rows), args.max_trials_per_condition, replace=False))
            rows = rows.iloc[keep]

        group_trials = {group: [] for group in groups}
        valid_trials = 0
        for row in rows.itertuples(index=False):
            start = int(round(row.recording_start_time_s * args.sample_rate_hz)) - pre_samples
            stop = start + n_samples
            if start < 0 or stop > lfp.shape[0]:
                continue
            segment = np.asarray(lfp[start:stop], dtype=np.float32)
            segment = reference_segment(segment, args.reference_mode, excluded_channels)
            baseline = np.median(segment[pre_mask], axis=0, keepdims=True)
            segment = segment - baseline
            for group, channels in ANALYSIS_GROUPS.items():
                usable = [ch for ch in channels if ch not in excluded_channels]
                if not usable:
                    continue
                group_trials[group].append(np.mean(segment[:, usable], axis=1))
            valid_trials += 1

        for group_idx, group in enumerate(groups):
            if not group_trials[group]:
                continue
            trial_stack = np.asarray(group_trials[group], dtype=np.float32)
            filtered = bandpass(trial_stack, args.sample_rate_hz, freq, args.band_half_width_hz)
            phases = np.angle(hilbert(filtered, axis=1))
            plv_time = compute_plv(phases, axis=0)
            plv_maps[condition_idx, group_idx] = plv_time.astype(np.float32)
            mean_phase = circular_mean_phase(phases[:, sustained_mask], axis=None)
            rows_out.append(
                {
                    "condition": condition,
                    "amplitude": amp,
                    "frequency": freq,
                    "analysis_group": group,
                    "reference_mode": args.reference_mode,
                    "n_trials": valid_trials,
                    "pre_plv": float(np.mean(plv_time[pre_mask])),
                    "sustained_plv": float(np.mean(plv_time[sustained_mask])),
                    "offset_plv": float(np.mean(plv_time[offset_mask])),
                    "sustained_minus_pre_plv": float(np.mean(plv_time[sustained_mask]) - np.mean(plv_time[pre_mask])),
                    "sustained_mean_phase_rad": float(mean_phase),
                }
            )

    np.savez_compressed(
        args.output_dir / "phase_locking_plv_maps.npz",
        conditions=np.asarray(conditions),
        groups=np.asarray(groups),
        time_s=time_s,
        plv=plv_maps,
    )
    summary = pd.DataFrame(rows_out)
    summary.to_csv(args.output_dir / "phase_locking_summary.csv", index=False)
    plot_plv_timecourses(args.output_dir / "phase_locking_plv_maps.npz", args.output_dir / "plv_timecourses.png")
    plot_plv_summary(summary, args.output_dir / "plv_condition_summary.png")

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Phase Locking</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1300px} img{width:100%;border:1px solid #ddd;margin-bottom:32px}</style>",
        "</head><body><h1>Dec 3 Driven-Frequency Phase Locking</h1>",
        f"<p>Reference: <code>{args.reference_mode}</code>. Excluded channels: {sorted(excluded_channels)}.</p>",
        "<p>PLV means phase-locking value across trials. Higher values mean phase is more consistent across trials at the driven frequency.</p>",
        "<h2>PLV Time Courses</h2><img src='plv_timecourses.png'>",
        "<h2>PLV Condition Summary</h2><img src='plv_condition_summary.png'>",
        "<h2>Sustained Minus Pre</h2><img src='plv_sustained_minus_pre.png'>",
        "</body></html>",
    ]
    (args.output_dir / "index.html").write_text("\n".join(html))

    report = {
        "output_dir": str(args.output_dir),
        "summary_csv": str(args.output_dir / "phase_locking_summary.csv"),
        "maps_npz": str(args.output_dir / "phase_locking_plv_maps.npz"),
        "reference_mode": args.reference_mode,
        "excluded_channels": sorted(excluded_channels),
        "band_half_width_hz": args.band_half_width_hz,
        "note": "PLV is inter-trial phase consistency at the condition's driven frequency, aligned to trial onset.",
    }
    (args.output_dir / "phase_locking_run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
