#!/usr/bin/env python3
"""Trial-order/adaptation analysis for Dec 3 ON/OFF broadband responses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress


CONDITION_ORDER = [
    "amp100_freq5",
    "amp180_freq5",
    "amp250_freq5",
    "amp100_freq26",
    "amp180_freq26",
    "amp250_freq26",
]


def parse_condition(condition: str) -> tuple[int, int]:
    parts = condition.replace("amp", "").replace("freq", "").split("_")
    return int(parts[0]), int(parts[1])


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return np.nan, np.nan, np.nan
    boot = rng.choice(values, size=(n_boot, values.size), replace=True).mean(axis=1)
    return float(values.mean()), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def add_repeat_index(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.sort_values("trial_number").copy()
    out["condition_repeat_index"] = out.groupby("condition").cumcount() + 1
    out["condition_repeat_fraction"] = (out["condition_repeat_index"] - 1) / (
        out.groupby("condition")["condition_repeat_index"].transform("max") - 1
    )
    out["epoch"] = pd.cut(
        out["condition_repeat_fraction"],
        bins=[-0.001, 1 / 3, 2 / 3, 1.001],
        labels=["early", "middle", "late"],
    )
    return out


def condition_trial_means(trial_metrics: pd.DataFrame) -> pd.DataFrame:
    return (
        trial_metrics.groupby(["condition", "amplitude", "frequency", "trial_number"], as_index=False)
        .agg(
            on_delta=("on_delta", "mean"),
            off_delta=("off_delta", "mean"),
            on_minus_off=("on_minus_off", "mean"),
        )
        .pipe(add_repeat_index)
    )


def compute_epoch_summary(frame: pd.DataFrame, rng: np.random.Generator, n_boot: int) -> pd.DataFrame:
    rows = []
    for (condition, epoch), sub in frame.groupby(["condition", "epoch"], observed=False):
        amp, freq = parse_condition(condition)
        out = {
            "condition": condition,
            "amplitude": amp,
            "frequency": freq,
            "epoch": str(epoch),
            "n_trials": int(sub["trial_number"].nunique()),
        }
        for metric in ["on_delta", "off_delta", "on_minus_off"]:
            mean, lo, hi = bootstrap_ci(sub[metric].to_numpy(), rng, n_boot)
            out[f"{metric}_mean"] = mean
            out[f"{metric}_ci_low"] = lo
            out[f"{metric}_ci_high"] = hi
        rows.append(out)
    return pd.DataFrame(rows)


def compute_slope_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for condition, sub in frame.groupby("condition"):
        amp, freq = parse_condition(condition)
        x = sub["condition_repeat_index"].to_numpy(dtype=float)
        out = {"condition": condition, "amplitude": amp, "frequency": freq, "n_trials": int(sub["trial_number"].nunique())}
        for metric in ["on_delta", "off_delta", "on_minus_off"]:
            y = sub[metric].to_numpy(dtype=float)
            result = linregress(x, y)
            out[f"{metric}_slope_per_trial"] = float(result.slope)
            out[f"{metric}_slope_per_100_trials"] = float(result.slope * 100)
            out[f"{metric}_pvalue"] = float(result.pvalue)
            out[f"{metric}_rvalue"] = float(result.rvalue)
        rows.append(out)
    return pd.DataFrame(rows).sort_values(["frequency", "amplitude"])


def rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return values
    series = pd.Series(values)
    return series.rolling(window=window, center=True, min_periods=max(3, window // 3)).mean().to_numpy()


def plot_timecourses(frame: pd.DataFrame, output: Path, window: int) -> None:
    metrics = [
        ("on_delta", "ON vs pre"),
        ("off_delta", "OFF vs pre"),
        ("on_minus_off", "ON - OFF"),
    ]
    colors = {"on_delta": "#4C78A8", "off_delta": "#54A24B", "on_minus_off": "#E45756"}
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True, sharey=False)
    axes = axes.ravel()

    for ax, condition in zip(axes, CONDITION_ORDER):
        sub = frame[frame["condition"] == condition].sort_values("condition_repeat_index")
        x = sub["condition_repeat_index"].to_numpy()
        for metric, label in metrics:
            y = rolling_mean(sub[metric].to_numpy(), window)
            ax.plot(x, y, color=colors[metric], linewidth=1.6, label=label)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(condition)
        ax.grid(alpha=0.25)
    for ax in axes[3:]:
        ax.set_xlabel("Repeat index within condition")
    axes[0].set_ylabel("Broadband delta")
    axes[3].set_ylabel("Broadband delta")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3)
    fig.suptitle(f"Trial-Order Adaptation, Rolling Mean Window = {window} Repeats")
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_epoch_summary(epoch_summary: pd.DataFrame, output: Path) -> None:
    metrics = [
        ("on_delta", "ON vs pre"),
        ("off_delta", "OFF vs pre"),
        ("on_minus_off", "ON - OFF"),
    ]
    epochs = ["early", "middle", "late"]
    colors = {"early": "#9AA1AA", "middle": "#4C78A8", "late": "#E45756"}
    fig, axes = plt.subplots(1, len(metrics), figsize=(16, 5), sharey=False)
    x = np.arange(len(CONDITION_ORDER))
    width = 0.24

    for ax, (metric, title) in zip(axes, metrics):
        for i, epoch in enumerate(epochs):
            sub = epoch_summary[epoch_summary["epoch"] == epoch].set_index("condition").reindex(CONDITION_ORDER)
            y = sub[f"{metric}_mean"].to_numpy()
            lo = sub[f"{metric}_ci_low"].to_numpy()
            hi = sub[f"{metric}_ci_high"].to_numpy()
            xpos = x + (i - 1) * width
            ax.bar(xpos, y, width=width, color=colors[epoch], alpha=0.86, label=epoch)
            ax.errorbar(xpos, y, yerr=[y - lo, hi - y], fmt="none", color="black", linewidth=0.7, capsize=2)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(CONDITION_ORDER, rotation=35, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Broadband delta")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3)
    fig.suptitle("Early vs Middle vs Late Repeats")
    fig.tight_layout(rect=(0, 0.08, 1, 0.92))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_slope_summary(slope_summary: pd.DataFrame, output: Path) -> None:
    metrics = [
        ("on_delta_slope_per_100_trials", "ON slope / 100 repeats"),
        ("off_delta_slope_per_100_trials", "OFF slope / 100 repeats"),
        ("on_minus_off_slope_per_100_trials", "ON-OFF slope / 100 repeats"),
    ]
    fig, axes = plt.subplots(1, len(metrics), figsize=(15, 4.8), sharey=True)
    x = np.arange(len(CONDITION_ORDER))
    for ax, (metric, title) in zip(axes, metrics):
        sub = slope_summary.set_index("condition").reindex(CONDITION_ORDER)
        colors = ["#2F6BBA" if parse_condition(c)[1] == 5 else "#C43A31" for c in CONDITION_ORDER]
        ax.bar(x, sub[metric], color=colors, alpha=0.86)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(CONDITION_ORDER, rotation=35, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Broadband delta change")
    fig.suptitle("Linear Adaptation Slopes")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial-metrics", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--rolling-window", type=int, default=15)
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(321)
    trial_metrics = pd.read_csv(args.trial_metrics)
    frame = condition_trial_means(trial_metrics)
    frame.to_csv(args.output_dir / "condition_trial_means_with_repeat_index.csv", index=False)

    epoch_summary = compute_epoch_summary(frame, rng, args.n_bootstrap)
    epoch_summary.to_csv(args.output_dir / "adaptation_epoch_summary_ci.csv", index=False)

    slope_summary = compute_slope_summary(frame)
    slope_summary.to_csv(args.output_dir / "adaptation_slope_summary.csv", index=False)

    plot_timecourses(frame, args.output_dir / "adaptation_timecourses.png", args.rolling_window)
    plot_epoch_summary(epoch_summary, args.output_dir / "adaptation_epoch_summary.png")
    plot_slope_summary(slope_summary, args.output_dir / "adaptation_slope_summary.png")

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Adaptation Analysis</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1300px;line-height:1.45}"
        "img{width:100%;border:1px solid #d9dee5;margin-bottom:30px}"
        "a{color:#0f6b78;font-weight:600}</style></head><body>",
        "<h1>Dec 3 Trial-Order / Adaptation Analysis</h1>",
        "<p>Uses the 3 s OFF-control broadband metrics. Repeat index is within each condition, not absolute session trial number.</p>",
        "<h2>Rolling Time Courses</h2><img src='adaptation_timecourses.png'>",
        "<h2>Early / Middle / Late</h2><img src='adaptation_epoch_summary.png'>",
        "<h2>Linear Slopes</h2><img src='adaptation_slope_summary.png'>",
        "<p>Back to <a href='../RESULTS_DASHBOARD.html'>main dashboard</a>.</p>",
        "</body></html>",
    ]
    (args.output_dir / "index.html").write_text("\n".join(html))

    report = {
        "output_dir": str(args.output_dir),
        "trial_metrics": str(args.trial_metrics),
        "rolling_window": args.rolling_window,
        "n_bootstrap": args.n_bootstrap,
    }
    (args.output_dir / "adaptation_run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
