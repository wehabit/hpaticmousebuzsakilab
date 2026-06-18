#!/usr/bin/env python3
"""Plot condition summaries that make LFP differences easier to compare."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SHANK_MAP = {
    "Shank 1 (96-127)": range(96, 128),
    "Shank 2 (64-95)": range(64, 96),
    "Shank 3 (32-63)": range(32, 64),
    "Shank 4 (0-31)": range(0, 32),
}


def add_condition_parts(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    parts = frame["condition"].str.extract(r"amp(?P<amplitude>\d+)_freq(?P<frequency>\d+)")
    frame["amplitude"] = parts["amplitude"].astype(int)
    frame["frequency"] = parts["frequency"].astype(int)
    frame["shank"] = "unknown"
    for shank, channels in SHANK_MAP.items():
        frame.loc[frame["channel"].isin(list(channels)), "shank"] = shank
    return frame


def plot_grouped_bars(frame: pd.DataFrame, output: Path) -> None:
    summary = (
        frame.groupby(["shank", "amplitude", "frequency"], as_index=False)
        .agg(
            response=("stim_minus_pre_abs_lfp", "mean"),
            sem=("stim_minus_pre_abs_lfp", lambda x: x.std(ddof=1) / np.sqrt(len(x))),
        )
    )

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharey=True)
    axes = axes.ravel()
    width = 0.35
    amps = [100, 180, 250]
    x = np.arange(len(amps))
    colors = {5: "#4C78A8", 26: "#E45756"}

    for ax, shank in zip(axes, SHANK_MAP):
        sub = summary[summary["shank"] == shank]
        for offset, freq in [(-width / 2, 5), (width / 2, 26)]:
            rows = sub[sub["frequency"] == freq].set_index("amplitude").reindex(amps)
            ax.bar(
                x + offset,
                rows["response"],
                width=width,
                yerr=rows["sem"],
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
    axes[0].set_ylabel("Stim - pre mean |LFP|")
    axes[2].set_ylabel("Stim - pre mean |LFP|")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2)
    fig.suptitle("LFP Response by Shank, Amplitude, and Frequency")
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_frequency_difference(frame: pd.DataFrame, output: Path) -> None:
    summary = (
        frame.groupby(["shank", "amplitude", "frequency"], as_index=False)
        .agg(response=("stim_minus_pre_abs_lfp", "mean"))
    )
    pivot = summary.pivot(index=["shank", "amplitude"], columns="frequency", values="response").reset_index()
    pivot["freq26_minus_freq5"] = pivot[26] - pivot[5]

    fig, ax = plt.subplots(figsize=(11, 6))
    amps = [100, 180, 250]
    for shank in SHANK_MAP:
        sub = pivot[pivot["shank"] == shank].set_index("amplitude").reindex(amps)
        ax.plot(amps, sub["freq26_minus_freq5"], marker="o", linewidth=1.8, label=shank)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(amps)
    ax.set_xlabel("Amplitude")
    ax.set_ylabel("26 Hz response - 5 Hz response")
    ax.set_title("Frequency Effect by Shank")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_condition_heatmap_by_shank(frame: pd.DataFrame, output: Path) -> None:
    summary = (
        frame.groupby(["condition", "shank"], as_index=False)
        .agg(response=("stim_minus_pre_abs_lfp", "mean"))
    )
    order = ["amp100_freq5", "amp100_freq26", "amp180_freq5", "amp180_freq26", "amp250_freq5", "amp250_freq26"]
    pivot = summary.pivot(index="condition", columns="shank", values="response").reindex(order)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    vmax = np.nanmax(np.abs(pivot.to_numpy()))
    image = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=30, ha="right")
    ax.set_title("Mean LFP Response by Condition and Shank")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            value = pivot.iloc[i, j]
            ax.text(j, i, f"{value:.1f}", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax, label="Stim - pre mean |LFP|")
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame = add_condition_parts(pd.read_csv(args.summary_csv))
    plot_grouped_bars(frame, args.output_dir / "lfp_response_grouped_bars.png")
    plot_frequency_difference(frame, args.output_dir / "lfp_frequency_difference_by_shank.png")
    plot_condition_heatmap_by_shank(frame, args.output_dir / "lfp_condition_shank_heatmap_values.png")

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 LFP Condition Summary</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px} img{width:100%;max-width:1200px;border:1px solid #ddd;margin-bottom:32px}</style>",
        "</head><body><h1>Dec 3 LFP Condition Summary</h1>",
        "<p>Summary metric: mean |LFP| during 0-3 s stimulation minus mean |LFP| during the 1 s pre-window.</p>",
    ]
    for image in [
        "lfp_response_grouped_bars.png",
        "lfp_frequency_difference_by_shank.png",
        "lfp_condition_shank_heatmap_values.png",
    ]:
        html.append(f"<h2>{image}</h2><img src='{image}' alt='{image}'>")
    html.append("</body></html>")
    (args.output_dir / "index.html").write_text("\n".join(html))
    print(args.output_dir / "index.html")


if __name__ == "__main__":
    main()
