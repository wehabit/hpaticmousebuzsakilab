#!/usr/bin/env python3
"""Trial-level broadband transition analysis for the Dec 3 haptic LFP session."""

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

CONDITION_ORDER = [
    "amp100_freq5",
    "amp180_freq5",
    "amp250_freq5",
    "amp100_freq26",
    "amp180_freq26",
    "amp250_freq26",
]


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


def reference_segment(segment: np.ndarray, mode: str, excluded_channels: set[int]) -> np.ndarray:
    if mode == "raw":
        return segment
    if mode != "analysis_group_median":
        raise ValueError(f"Unsupported reference mode: {mode}")
    referenced = segment.copy()
    for channels in ANALYSIS_GROUPS.values():
        usable = [ch for ch in channels if ch not in excluded_channels]
        if not usable:
            continue
        ref = np.median(segment[:, usable], axis=1, keepdims=True)
        referenced[:, channels] = segment[:, channels] - ref
    return referenced


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return np.nan, np.nan, np.nan
    boot = rng.choice(values, size=(n_boot, values.size), replace=True).mean(axis=1)
    return float(values.mean()), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def plot_condition_windows(condition_summary: pd.DataFrame, output: Path) -> None:
    frame = condition_summary.set_index("condition").reindex(CONDITION_ORDER).reset_index()
    windows = [
        ("onset_delta", "Onset"),
        ("sustained_delta", "Sustained"),
        ("offset_delta", "Offset"),
        ("recovery_delta", "Recovery"),
    ]
    x = np.arange(len(frame))
    width = 0.2
    colors = ["#E45756", "#4C78A8", "#F58518", "#54A24B"]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    for i, ((metric, label), color) in enumerate(zip(windows, colors)):
        y = frame[f"{metric}_mean"].to_numpy()
        lo = frame[f"{metric}_ci_low"].to_numpy()
        hi = frame[f"{metric}_ci_high"].to_numpy()
        xpos = x + (i - 1.5) * width
        ax.bar(xpos, y, width=width, color=color, alpha=0.86, label=label)
        ax.errorbar(xpos, y, yerr=[y - lo, hi - y], fmt="none", color="black", linewidth=0.8, capsize=2)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(frame["condition"], rotation=30, ha="right")
    ax.set_ylabel("Mean |LFP| window delta vs pre baseline")
    ax.set_title("Broadband Window Effects with Trial-Level Bootstrap CIs")
    ax.legend(ncol=4)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_transition_index(condition_summary: pd.DataFrame, output: Path) -> None:
    frame = condition_summary.set_index("condition").reindex(CONDITION_ORDER).reset_index()
    x = np.arange(len(frame))
    colors = ["#2F6BBA" if parse_condition(c)[1] == 5 else "#C43A31" for c in frame["condition"]]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(x, frame["transition_index_mean"], color=colors, alpha=0.86)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(frame["condition"], rotation=30, ha="right")
    ax.set_ylabel("Offset delta - sustained delta")
    ax.set_title("Transition Index: Positive Means More Offset-Heavy Than Sustained")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_group_heatmap(group_summary: pd.DataFrame, output: Path) -> None:
    windows = [
        ("onset_delta_mean", "Onset"),
        ("sustained_delta_mean", "Sustained"),
        ("offset_delta_mean", "Offset"),
        ("recovery_delta_mean", "Recovery"),
    ]
    groups = list(ANALYSIS_GROUPS)
    fig, axes = plt.subplots(1, len(windows), figsize=(16, 5), sharey=True)
    for ax, (metric, title) in zip(axes, windows):
        pivot = (
            group_summary.pivot(index="condition", columns="analysis_group", values=metric)
            .reindex(CONDITION_ORDER)[groups]
        )
        vmax = np.nanpercentile(np.abs(pivot.to_numpy()), 98)
        vmax = max(vmax, 1)
        image = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
        ax.set_title(title)
        ax.set_xticks(np.arange(len(groups)))
        ax.set_xticklabels(groups, rotation=35, ha="right")
        ax.set_yticks(np.arange(len(CONDITION_ORDER)))
        ax.set_yticklabels(CONDITION_ORDER)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("Broadband Window Effects by Analysis Group")
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
    parser.add_argument("--n-bootstrap", type=int, default=2000)
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
    masks = {
        "pre": time_s < 0,
        "onset": (time_s >= 0) & (time_s < args.artifact_margin_s),
        "sustained": (time_s >= args.artifact_margin_s) & (time_s < 3 - args.artifact_margin_s),
        "offset": (time_s >= 3 - args.artifact_margin_s) & (time_s < 3 + args.artifact_margin_s),
        "recovery": (time_s >= 3 + args.artifact_margin_s) & (time_s < args.post_s),
    }

    rows_out = []
    for row in sequence.sort_values("trial_number").itertuples(index=False):
        amp, freq = parse_condition(row.condition)
        start = int(round(row.recording_start_time_s * args.sample_rate_hz)) - pre_samples
        stop = start + n_samples
        if start < 0 or stop > lfp.shape[0]:
            continue
        segment = np.asarray(lfp[start:stop], dtype=np.float32)
        segment = reference_segment(segment, args.reference_mode, excluded_channels)
        baseline = np.median(segment[masks["pre"]], axis=0, keepdims=True)
        segment = segment - baseline

        for group, channels in ANALYSIS_GROUPS.items():
            usable = [ch for ch in channels if ch not in excluded_channels]
            if not usable:
                continue
            group_signal = np.mean(segment[:, usable], axis=1)
            pre_abs = float(np.mean(np.abs(group_signal[masks["pre"]])))
            values = {
                name: float(np.mean(np.abs(group_signal[mask])) - pre_abs)
                for name, mask in masks.items()
                if name != "pre"
            }
            rows_out.append(
                {
                    "trial_number": int(row.trial_number),
                    "condition": row.condition,
                    "amplitude": amp,
                    "frequency": freq,
                    "analysis_group": group,
                    "n_channels_used": len(usable),
                    "onset_delta": values["onset"],
                    "sustained_delta": values["sustained"],
                    "offset_delta": values["offset"],
                    "recovery_delta": values["recovery"],
                    "transition_index": values["offset"] - values["sustained"],
                }
            )

    trial_metrics = pd.DataFrame(rows_out)
    trial_metrics.to_csv(args.output_dir / "broadband_transition_trial_metrics.csv", index=False)

    summary_rows = []
    for (condition, group), sub in trial_metrics.groupby(["condition", "analysis_group"], sort=False):
        amp, freq = parse_condition(condition)
        out = {
            "condition": condition,
            "amplitude": amp,
            "frequency": freq,
            "analysis_group": group,
            "n_trials": int(sub["trial_number"].nunique()),
        }
        for metric in ["onset_delta", "sustained_delta", "offset_delta", "recovery_delta", "transition_index"]:
            mean, lo, hi = bootstrap_ci(sub[metric].to_numpy(), rng, args.n_bootstrap)
            out[f"{metric}_mean"] = mean
            out[f"{metric}_ci_low"] = lo
            out[f"{metric}_ci_high"] = hi
        summary_rows.append(out)
    group_summary = pd.DataFrame(summary_rows).sort_values(["frequency", "amplitude", "analysis_group"])
    group_summary.to_csv(args.output_dir / "broadband_transition_group_summary_ci.csv", index=False)

    condition_rows = []
    for condition, sub in trial_metrics.groupby("condition", sort=False):
        amp, freq = parse_condition(condition)
        grouped = sub.groupby("trial_number", as_index=False)[
            ["onset_delta", "sustained_delta", "offset_delta", "recovery_delta", "transition_index"]
        ].mean()
        out = {"condition": condition, "amplitude": amp, "frequency": freq, "n_trials": int(grouped["trial_number"].nunique())}
        for metric in ["onset_delta", "sustained_delta", "offset_delta", "recovery_delta", "transition_index"]:
            mean, lo, hi = bootstrap_ci(grouped[metric].to_numpy(), rng, args.n_bootstrap)
            out[f"{metric}_mean"] = mean
            out[f"{metric}_ci_low"] = lo
            out[f"{metric}_ci_high"] = hi
        condition_rows.append(out)
    condition_summary = pd.DataFrame(condition_rows).sort_values(["frequency", "amplitude"])
    condition_summary.to_csv(args.output_dir / "broadband_transition_condition_summary_ci.csv", index=False)

    plot_condition_windows(condition_summary, args.output_dir / "broadband_windows_condition_ci.png")
    plot_transition_index(condition_summary, args.output_dir / "transition_index_condition.png")
    plot_group_heatmap(group_summary, args.output_dir / "broadband_window_group_heatmaps.png")

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Broadband Transition Analysis</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1300px;line-height:1.45}"
        "img{width:100%;border:1px solid #d9dee5;margin-bottom:30px}"
        "a{color:#0f6b78;font-weight:600}</style></head><body>",
        "<h1>Dec 3 Broadband / Transition Analysis</h1>",
        "<p>Trial-level bootstrap confidence intervals for onset, sustained stimulation, offset, and recovery broadband LFP.</p>",
        "<p>Positive transition index means the offset response is larger than the sustained ON response.</p>",
        "<h2>Window Effects by Condition</h2><img src='broadband_windows_condition_ci.png'>",
        "<h2>Transition Index</h2><img src='transition_index_condition.png'>",
        "<h2>Window Effects by Analysis Group</h2><img src='broadband_window_group_heatmaps.png'>",
        "<p>Back to <a href='../RESULTS_DASHBOARD.html'>main dashboard</a>.</p>",
        "</body></html>",
    ]
    (args.output_dir / "index.html").write_text("\n".join(html))

    report = {
        "output_dir": str(args.output_dir),
        "trial_metrics_csv": str(args.output_dir / "broadband_transition_trial_metrics.csv"),
        "condition_summary_csv": str(args.output_dir / "broadband_transition_condition_summary_ci.csv"),
        "group_summary_csv": str(args.output_dir / "broadband_transition_group_summary_ci.csv"),
        "excluded_channels": sorted(excluded_channels),
        "reference_mode": args.reference_mode,
        "artifact_margin_s": args.artifact_margin_s,
        "n_bootstrap": args.n_bootstrap,
    }
    (args.output_dir / "broadband_transition_run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
