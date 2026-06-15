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
    # (metric, title, plain-English "what UP means", y-axis unit, is this the REAL effect?, value fmt)
    metrics = [
        ("sustained_broadband", "Sustained broadband",
         "overall signal size DURING the 3 s buzz", "mean |LFP| increase\nvs baseline (a.u.)", True, "{:.0f}"),
        ("offset_broadband", "Offset broadband",
         "signal size just AFTER the buzz ends", "mean |LFP| increase\nvs baseline (a.u.)", True, "{:.0f}"),
        ("driven_power_analysis_group_median", "Driven-frequency power",
         "power AT the 5/26 Hz stim frequency", "log2(stim / baseline)\n(0 = no change)", False, "{:.2f}"),
        ("sustained_timefreq", "Time-frequency band",
         "sustained power at the stim frequency", "normalized power\n(0 = no change)", False, "{:.2f}"),
        ("sustained_minus_pre_plv", "Phase-locking (PLV)",
         "phase consistency across trials", "PLV change vs pre\n(0 = no locking)", False, "{:.3f}"),
    ]
    fig, axes = plt.subplots(1, len(metrics), figsize=(19, 6.2), sharex=False)
    x = np.arange(len(frame))
    labels = [c.replace("amp", "").replace("_freq", "/") for c in frame["condition"]]
    colors = [COLORS[freq] for freq in frame["frequency"]]

    for ax, (metric, title, updesc, unit, is_real, fmt) in zip(axes, metrics):
        values = frame[metric].to_numpy()
        bars = ax.bar(x, values, color=colors, alpha=0.9, edgecolor="black", linewidth=0.4)
        ax.axhline(0, color="black", linewidth=0.9)
        ax.set_title(title, fontsize=12, fontweight="bold", pad=26)
        ax.text(0.5, 1.02, f"↑ = {updesc}", transform=ax.transAxes, ha="center", va="bottom",
                fontsize=8.5, style="italic", color="#444")
        ax.set_ylabel(unit, fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.25)
        # value labels on each bar
        ymax = max(abs(values.min()), abs(values.max())) or 1
        for xi, v in zip(x, values):
            ax.text(xi, v + (0.04 * ymax if v >= 0 else -0.04 * ymax), fmt.format(v),
                    ha="center", va="bottom" if v >= 0 else "top", fontsize=7.5)
        ax.margins(y=0.18)
        # flag the panels that carry a REAL effect vs the near-zero ones
        if is_real:
            ax.text(0.5, 0.93, "REAL response", transform=ax.transAxes, ha="center", fontsize=9,
                    fontweight="bold", color="#1a7a3a", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.25", fc="#e8f6ec", ec="#1a7a3a", alpha=0.4))
        else:
            ax.axhspan(-0.5 * ymax, 0.5 * ymax, color="#bbbbbb", alpha=0.10, zorder=0)
            ax.text(0.5, 0.93, "≈ 0  (no entrainment)", transform=ax.transAxes, ha="center", fontsize=9,
                    fontweight="bold", color="#8a6d00", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.25", fc="#fdf5e0", ec="#b8860b", alpha=0.4))

    legend_handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[5]),
                      plt.Rectangle((0, 0), 1, 1, color=COLORS[26])]
    # legend inside panel 1 (its bars grow rightward, so the top-left is empty) -> no title overlap
    axes[0].legend(legend_handles, ["5 Hz", "26 Hz"], loc="upper left", fontsize=8.5,
                   frameon=True, title="bar color")
    fig.suptitle("Condition Fingerprint — what response does each buzz setting produce?",
                 fontsize=14, fontweight="bold", y=0.985)
    fig.text(0.5, 0.04,
             "Each bar = one condition (amplitude / frequency).   The two LEFT panels show a real, size-graded response;   "
             "the three RIGHT panels are all ≈ 0  →  the brain reacts to the buzz but does NOT follow its frequency.",
             ha="center", fontsize=10, style="italic")
    fig.tight_layout(rect=(0, 0.07, 1, 0.92))
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_biology_quadrants(frame: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 7.5))
    x = frame["driven_power_analysis_group_median"]
    y = frame["sustained_broadband"]
    sizes = np.clip(np.abs(frame["offset_broadband"]), 12, 110) * 5
    colors = [COLORS[freq] for freq in frame["frequency"]]

    xpad = (x.max() - x.min()) * 0.18 or 0.05
    ypad = (y.max() - y.min()) * 0.18 or 1
    ax.set_xlim(x.min() - xpad, x.max() + xpad)
    ax.set_ylim(y.min() - ypad, y.max() + ypad)

    # shade the meaningful halves of the x-axis
    ax.axvspan(0, ax.get_xlim()[1], color="#e8f6ec", alpha=0.6, zorder=0)   # right = power went UP at stim freq
    ax.axvspan(ax.get_xlim()[0], 0, color="#fdeceb", alpha=0.6, zorder=0)   # left  = power went DOWN
    ax.text(0.985, 0.02, "RIGHT half = power INCREASED at the\nstim frequency (true entrainment)",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color="#1a7a3a")
    ax.text(0.015, 0.02, "LEFT half = NO increase at the\nstim frequency", transform=ax.transAxes,
            ha="left", va="bottom", fontsize=8.5, color="#a93226")

    ax.scatter(x, y, s=sizes, c=colors, alpha=0.8, edgecolor="black", linewidth=0.9, zorder=5)
    for row in frame.itertuples(index=False):
        ax.annotate(
            row.condition.replace("amp", "").replace("_freq", " Hz / ") + " Hz",
            (row.driven_power_analysis_group_median, row.sustained_broadband),
            xytext=(8, 8), textcoords="offset points", fontsize=9, fontweight="bold",
        )
    ax.axvline(0, color="black", linewidth=1.0)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Did power increase AT the stim frequency?\ndriven-frequency power, log2(stim / baseline)   — 0 means no change", fontsize=10)
    ax.set_ylabel("How big is the overall response?\nsustained broadband mean |LFP| increase (a.u.)", fontsize=10)
    ax.set_title("Is the response frequency-specific (entrainment) or just broadband?", fontsize=13, fontweight="bold")

    # key takeaway arrow to the biggest responder
    big = frame.loc[frame["sustained_broadband"].idxmax()]
    ax.annotate("biggest response (180/26) sits at x≈0:\nlarge broadband bump, but NO power\nincrease at its own 26 Hz → broadband,\nnot frequency-following",
                (big["driven_power_analysis_group_median"], big["sustained_broadband"]),
                xytext=(0.30, 0.62), textcoords="axes fraction", fontsize=9, color="#222",
                bbox=dict(boxstyle="round,pad=0.35", fc="#fffbe6", ec="#b8860b"),
                arrowprops=dict(arrowstyle="->", color="#b8860b", lw=1.4))

    # legends: color (frequency) + dot size (offset response)
    color_handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS[5], markersize=11, label="5 Hz"),
                     plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS[26], markersize=11, label="26 Hz")]
    leg1 = ax.legend(handles=color_handles, title="stim frequency (color)", loc="upper left", fontsize=9)
    ax.add_artist(leg1)
    size_vals = [25, 50, 100]
    size_handles = [plt.scatter([], [], s=np.clip(v, 12, 110) * 5, c="#888", edgecolor="black",
                                label=f"{v}") for v in size_vals]
    ax.legend(handles=size_handles, title="offset response (dot size)", loc="lower right",
              labelspacing=1.4, borderpad=1.0, fontsize=9, framealpha=0.9)
    ax.grid(alpha=0.2, zorder=1)
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
