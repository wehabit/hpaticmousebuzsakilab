#!/usr/bin/env python
"""Does the 50 Hz pickup reach the GOOD LEC tissue channels, or only the dead ones?

One focused figure to land a single point: the 50 Hz LFP is not confined to disconnected
electrodes — a substantial fraction of the tissue-good LEC channels carry it too, while
the dHPC tissue channels carry essentially none. Per-channel 50 Hz ON-OFF envelope
amplitude (the artifact_check_50hz 'diff' metric), split into three groups:
dHPC tissue-good · LEC tissue-good · LEC dead/excluded.

Honest framing: LEC tissue-good has a near-zero MEDIAN but a contaminated tail (~1/3 of
channels above the +5 line), so the contamination is a subset, not every channel — but it
is enough that a single LEC tissue contact (e.g. ch181) cannot be trusted as clean 50 Hz.

Reads the per-channel table written by lfp_50hz_by_shank_dec4.py.
Outputs -> analysis/outputs/cross_dataset_spike_compare/lfp_50hz_by_shank/ and (builder)
results/dec4/12_ChannelQC_Traces/.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

CSV = Path("analysis/outputs/cross_dataset_spike_compare/lfp_50hz_by_shank/fiftyhz_by_shank_channels_dec4.csv")
OUT = CSV.parent / "fiftyhz_tissue_contamination_dec4.png"
YCAP = 22.0          # display cap; dead channels run far higher (up to ~80)
THRESH = 5.0         # "clearly contaminated" line


def main():
    d = pd.read_csv(CSV)
    groups = [
        ("dHPC\ntissue-good", (d.region == "dHPC") & (~d.bad)),
        ("LEC\ntissue-good", (d.region == "LEC") & (~d.bad)),
        ("LEC\ndead / excluded", (d.region == "LEC") & (d.bad)),
    ]
    CLEAN, HOT = "#BDBDBD", "#8C1515"      # grey = below +5; cardinal = contaminated (>+5)
    rng = np.random.default_rng(0)
    fig, ax = plt.subplots(figsize=(8.4, 6.4))

    for i, (name, mask) in enumerate(groups):
        v = d[mask].fiftyhz_on_minus_off.to_numpy()
        x = i + rng.uniform(-0.17, 0.17, len(v))
        vis = np.clip(v, None, YCAP)
        contam, over = v > THRESH, v > YCAP
        ax.scatter(x[~contam], vis[~contam], s=20, color=CLEAN, alpha=0.55, edgecolors="none", zorder=3)
        ax.scatter(x[contam & ~over], vis[contam & ~over], s=30, color=HOT, alpha=0.95,
                   edgecolors="#222", linewidths=0.4, zorder=4)
        if over.any():
            ax.scatter(x[over], np.full(over.sum(), YCAP), s=42, color=HOT, marker="^",
                       edgecolors="#222", linewidths=0.5, zorder=5)
        ax.plot([i - 0.26, i + 0.26], [np.median(v)] * 2, color="#111", lw=2.4, zorder=6)
        ax.text(i, -5.4, f"n = {len(v)}\n{(v > THRESH).mean() * 100:.0f}% above +5\nmedian {np.median(v):+.1f}",
                ha="center", va="top", fontsize=9.5)

    ax.axhline(0, color="#333", lw=0.9)
    ax.axhline(THRESH, color="#999", ls="--", lw=1.0)
    ax.text(2.46, THRESH + 0.2, "+5 = clearly contaminated", fontsize=8, color="#777", va="bottom", ha="right")
    ax.set_xticks(range(3))
    ax.set_xticklabels([g[0] for g in groups], fontsize=11)
    ax.set_xlim(-0.6, 2.6)
    ax.set_ylim(-9.5, YCAP + 1.5)
    ax.set_ylabel("50 Hz ON−OFF envelope amplitude (a.u., per channel)")
    ax.set_title("The 50 Hz LFP pickup reaches the GOOD LEC tissue channels, not only the dead ones\n"
                 "% of channels above +5:  dHPC 0%  ·  LEC tissue-good 34%  ·  LEC dead 53%   "
                 "(▲ = off-scale, to +80)", fontsize=10.5)
    ax.grid(axis="y", alpha=0.15)
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="none", markerfacecolor=CLEAN, markersize=8, label="≤ +5 (clean)"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=HOT, markeredgecolor="#222",
               markersize=8, label="> +5 (50 Hz-contaminated)"),
    ], loc="upper left", fontsize=9, framealpha=0.9)
    fig.text(
        0.5, 0.015,
        "All 15 curated LEC units sit on these contaminated good channels (the neurons cluster where the pickup is); dHPC units sit on clean channels. "
        "The single-unit effect is NOT driven by this LFP\npickup: spikes are detected >300 Hz, above the 50 Hz band, and the responsive units pass the ACG/ISI artifact screens (e.g. unit 87). "
        "Dead/excluded channels are dropped from all analyses.",
        ha="center", va="bottom", fontsize=8.2, color="#444",
    )
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    fig.savefig(OUT, dpi=190)
    plt.close(fig)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
