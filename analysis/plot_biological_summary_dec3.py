#!/usr/bin/env python3
"""Plot compact biological summary figures for the Dec 3 haptic LFP results."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUTPUT = Path("analysis/outputs/dec3/biological_summary")
CONDITION_ORDER = [
    "amp100_freq5",
    "amp180_freq5",
    "amp250_freq5",
    "amp100_freq26",
    "amp180_freq26",
    "amp250_freq26",
]
COLORS = {
    5: "#2F6BBA",
    26: "#C43A31",
}


def load_summary() -> pd.DataFrame:
    path = Path("analysis/outputs/dec3/condition_interpretation/condition_interpretation_summary.csv")
    frame = pd.read_csv(path)
    return frame.set_index("condition").reindex(CONDITION_ORDER).reset_index()


def plot_condition_fingerprint(frame: pd.DataFrame, output: Path) -> None:
    metrics = [
        ("sustained_broadband", "Sustained\nbroadband LFP"),
        ("offset_broadband", "Offset\nbroadband LFP"),
        ("driven_power_analysis_group_median", "Driven-frequency\npower"),
        ("sustained_timefreq", "Sustained\nTF driven band"),
        ("sustained_minus_pre_plv", "Phase-locking\nPLV delta"),
    ]
    fig, axes = plt.subplots(1, len(metrics), figsize=(17, 5), sharex=False)
    x = np.arange(len(frame))
    labels = frame["condition"].tolist()

    for ax, (metric, title) in zip(axes, metrics):
        values = frame[metric].to_numpy()
        colors = [COLORS[freq] for freq in frame["frequency"]]
        ax.bar(x, values, color=colors, alpha=0.88)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Metric value")
    fig.suptitle("Dec 3 Condition Fingerprint: What Kind of Response Does Each Condition Produce?")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_biology_quadrants(frame: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    x = frame["driven_power_analysis_group_median"]
    y = frame["sustained_broadband"]
    sizes = np.clip(np.abs(frame["offset_broadband"]), 12, 110) * 5
    colors = [COLORS[freq] for freq in frame["frequency"]]
    ax.scatter(x, y, s=sizes, c=colors, alpha=0.72, edgecolor="black", linewidth=0.8)
    for row in frame.itertuples(index=False):
        ax.annotate(
            row.condition.replace("amp", "").replace("_freq", "/"),
            (row.driven_power_analysis_group_median, row.sustained_broadband),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=9,
        )
    ax.axvline(0, color="black", linewidth=0.8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Driven-frequency power, log2(stim / pre)")
    ax.set_ylabel("Sustained broadband LFP change")
    ax.set_title("Broadband Response vs Driven-Frequency Power\nDot size reflects offset broadband response")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_frequency_amplitude_matrix(frame: pd.DataFrame, output: Path) -> None:
    metrics = [
        ("sustained_broadband", "Broadband"),
        ("driven_power_analysis_group_median", "Driven power"),
        ("sustained_timefreq", "TF driven band"),
        ("sustained_minus_pre_plv", "PLV delta"),
    ]
    amps = [100, 180, 250]
    freqs = [5, 26]
    fig, axes = plt.subplots(1, len(metrics), figsize=(14, 4), sharey=True)

    for ax, (metric, title) in zip(axes, metrics):
        matrix = np.full((len(freqs), len(amps)), np.nan)
        for i, freq in enumerate(freqs):
            for j, amp in enumerate(amps):
                row = frame[(frame["frequency"] == freq) & (frame["amplitude"] == amp)]
                if not row.empty:
                    matrix[i, j] = row.iloc[0][metric]
        vmax = np.nanpercentile(np.abs(matrix), 100)
        if metric == "sustained_broadband":
            image = ax.imshow(matrix, aspect="auto", cmap="viridis")
        else:
            vmax = max(vmax, 0.01)
            image = ax.imshow(matrix, aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
        for i in range(len(freqs)):
            for j in range(len(amps)):
                ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=9)
        ax.set_title(title)
        ax.set_xticks(np.arange(len(amps)))
        ax.set_xticklabels(amps)
        ax.set_yticks(np.arange(len(freqs)))
        ax.set_yticklabels([f"{f} Hz" for f in freqs])
        ax.set_xlabel("Amplitude")
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("Amplitude x Frequency Summary")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def write_html(output: Path) -> None:
    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Biological Summary</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1300px;line-height:1.45}"
        "img{width:100%;border:1px solid #d9dee5;margin-bottom:30px}"
        "a{color:#0f6b78;font-weight:600}</style></head><body>",
        "<h1>Dec 3 Biological Summary Figures</h1>",
        "<p>These figures combine the current condition-level metrics into a small number of biological views.</p>",
        "<p><strong>Reading guide:</strong> broadband LFP is overall response size; driven-frequency power asks whether power increased specifically at 5 Hz or 26 Hz; PLV asks whether phase became consistent across trials.</p>",
        "<h2>Condition Fingerprint</h2><img src='condition_fingerprint.png'>",
        "<h2>Broadband vs Driven-Frequency Power</h2><img src='broadband_vs_driven_power.png'>",
        "<h2>Amplitude x Frequency Matrix</h2><img src='amplitude_frequency_matrix.png'>",
        "<p>Back to <a href='../RESULTS_DASHBOARD.html'>main dashboard</a>.</p>",
        "</body></html>",
    ]
    (output / "index.html").write_text("\n".join(html))


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    frame = load_summary()
    plot_condition_fingerprint(frame, OUTPUT / "condition_fingerprint.png")
    plot_biology_quadrants(frame, OUTPUT / "broadband_vs_driven_power.png")
    plot_frequency_amplitude_matrix(frame, OUTPUT / "amplitude_frequency_matrix.png")
    write_html(OUTPUT)
    print({"output": str(OUTPUT / "index.html")})


if __name__ == "__main__":
    main()
