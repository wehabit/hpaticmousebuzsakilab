#!/usr/bin/env python3
"""Make readable plots from event-aligned LFP condition mean files."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


SHANKS = {
    "Shank 1 (96-127)": np.arange(96, 128),
    "Shank 2 (64-95)": np.arange(64, 96),
    "Shank 3 (32-63)": np.arange(32, 64),
    "Shank 4 (0-31)": np.arange(0, 32),
}


def condition_label(condition: str) -> tuple[int, int]:
    parts = condition.replace("amp", "").replace("freq", "").split("_")
    return int(parts[0]), int(parts[1])


def load_condition_means(input_dir: Path) -> dict[str, dict[str, np.ndarray]]:
    loaded = {}
    for path in sorted(input_dir.glob("*_mean_lfp.npz")):
        condition = path.name.replace("_mean_lfp.npz", "")
        data = np.load(path)
        loaded[condition] = {
            "time_s": data["time_s"],
            "channels": data["channels"],
            "mean": data["mean"],
            "sem": data["sem"],
        }
    return loaded


def plot_shank_small_multiples(conditions: dict[str, dict[str, np.ndarray]], output: Path) -> None:
    ordered = sorted(conditions, key=condition_label)
    colors = {
        5: "#1f77b4",
        26: "#d62728",
    }
    linestyles = {
        100: "-",
        180: "--",
        250: ":",
    }

    fig, axes = plt.subplots(2, 2, figsize=(15, 9), sharex=True, sharey=True)
    axes = axes.ravel()

    for ax, (shank_name, shank_channels) in zip(axes, SHANKS.items()):
        for condition in ordered:
            amp, freq = condition_label(condition)
            data = conditions[condition]
            channels = data["channels"]
            idx = np.where(np.isin(channels, shank_channels))[0]
            if len(idx) == 0:
                continue
            trace = np.median(data["mean"][:, idx], axis=1)
            ax.plot(
                data["time_s"],
                trace,
                color=colors[freq],
                linestyle=linestyles[amp],
                linewidth=1.4,
                label=f"{amp}, {freq} Hz",
            )
        ax.axvspan(0, 3, color="gold", alpha=0.14)
        ax.axvline(0, color="black", linewidth=0.7)
        ax.axvline(3, color="black", linewidth=0.7, linestyle="--")
        ax.set_title(shank_name)
        ax.grid(alpha=0.22)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=6, frameon=True)
    fig.supxlabel("Time from trial onset (s)")
    fig.supylabel("Median channel LFP, baseline-corrected")
    fig.suptitle("Event-Aligned LFP by Shank")
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_freq_panels(conditions: dict[str, dict[str, np.ndarray]], output: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(16, 8), sharex=True, sharey=True)
    amplitudes = [100, 180, 250]
    freqs = [5, 26]

    for row, freq in enumerate(freqs):
        for col, amp in enumerate(amplitudes):
            ax = axes[row, col]
            condition = f"amp{amp}_freq{freq}"
            data = conditions[condition]
            for shank_name, shank_channels in SHANKS.items():
                idx = np.where(np.isin(data["channels"], shank_channels))[0]
                trace = np.median(data["mean"][:, idx], axis=1)
                ax.plot(data["time_s"], trace, linewidth=1.2, label=shank_name)
            ax.axvspan(0, 3, color="gold", alpha=0.14)
            ax.axvline(0, color="black", linewidth=0.7)
            ax.axvline(3, color="black", linewidth=0.7, linestyle="--")
            ax.set_title(f"{amp} amplitude, {freq} Hz")
            ax.grid(alpha=0.22)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=True)
    fig.supxlabel("Time from trial onset (s)")
    fig.supylabel("Median shank LFP, baseline-corrected")
    fig.suptitle("Event-Aligned LFP: One Panel Per Condition")
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_condition_envelopes(conditions: dict[str, dict[str, np.ndarray]], output: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(15, 5), sharex=True, sharey=True)
    for ax, freq in zip(axes, [5, 26]):
        for amp, color in zip([100, 180, 250], ["#2ca02c", "#ff7f0e", "#9467bd"]):
            condition = f"amp{amp}_freq{freq}"
            data = conditions[condition]
            channel_traces = data["mean"]
            median = np.median(channel_traces, axis=1)
            lo = np.percentile(channel_traces, 25, axis=1)
            hi = np.percentile(channel_traces, 75, axis=1)
            ax.plot(data["time_s"], median, color=color, linewidth=1.5, label=f"amp {amp}")
            ax.fill_between(data["time_s"], lo, hi, color=color, alpha=0.16, linewidth=0)
        ax.axvspan(0, 3, color="gold", alpha=0.14)
        ax.axvline(0, color="black", linewidth=0.7)
        ax.axvline(3, color="black", linewidth=0.7, linestyle="--")
        ax.set_title(f"{freq} Hz")
        ax.grid(alpha=0.22)
        ax.legend()
    fig.supxlabel("Time from trial onset (s)")
    fig.supylabel("Across-channel median LFP with IQR")
    fig.suptitle("Condition LFP Envelopes")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    conditions = load_condition_means(args.input_dir)
    plot_shank_small_multiples(conditions, args.output_dir / "lfp_by_shank_conditions.png")
    plot_freq_panels(conditions, args.output_dir / "lfp_condition_panels_by_shank.png")
    plot_condition_envelopes(conditions, args.output_dir / "lfp_condition_envelopes.png")

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Better LFP Plots</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px} img{width:100%;max-width:1400px;border:1px solid #ddd;margin-bottom:32px}</style>",
        "</head><body><h1>Dec 3 Better Event-Aligned LFP Plots</h1>",
    ]
    for image in [
        "lfp_by_shank_conditions.png",
        "lfp_condition_panels_by_shank.png",
        "lfp_condition_envelopes.png",
    ]:
        html.append(f"<h2>{image}</h2><img src='{image}' alt='{image}'>")
    html.append("</body></html>")
    (args.output_dir / "index.html").write_text("\n".join(html))
    print(args.output_dir / "index.html")


if __name__ == "__main__":
    main()
