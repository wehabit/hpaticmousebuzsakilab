#!/usr/bin/env python
"""Figure: what the 50 Hz single-unit result means (data + inference ladder)."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

D = Path("analysis/outputs/cross_dataset_spike_compare")

def per_unit_50hz(ds):
    d = pd.read_csv(D / f"{ds}_unit_condition_stats.csv")
    d["freq"] = d.condition.str.extract(r"freq(\d+)").astype(int)
    return d[d.freq == 50].groupby("cluster_id").mean_delta_hz.mean().to_numpy()

dhpc, lec = per_unit_50hz("dec4_dHPC"), per_unit_50hz("dec4_LEC")

fig = plt.figure(figsize=(15, 6.2))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.5], wspace=0.25)

# ---- Panel A: per-unit 50 Hz ON-OFF, by region ----
axA = fig.add_subplot(gs[0, 0])
rng = np.random.default_rng(0)
for i, (vals, name, col) in enumerate([(dhpc, "dHPC", "#2a9d8f"), (lec, "LEC", "#e76f51")]):
    x = i + 1 + (rng.random(len(vals)) - 0.5) * 0.22
    axA.scatter(x, vals, s=42, color=col, edgecolor="k", linewidth=0.4, zorder=3, alpha=0.9)
    axA.plot([i + 1 - 0.28, i + 1 + 0.28], [np.mean(vals)] * 2, color="k", lw=2.2, zorder=4)
    axA.text(i + 1, axA.get_ylim()[1] if i else 2.05, f"mean {np.mean(vals):+.2f} Hz\n{int(100*(vals>0).mean())}% up",
             ha="center", va="bottom", fontsize=9)
axA.axhline(0, color="#888", lw=1, ls="--")
axA.set_xlim(0.5, 2.5); axA.set_xticks([1, 2]); axA.set_xticklabels(["dHPC", "LEC"])
axA.set_ylabel("per-unit ON − OFF firing at 50 Hz (Hz)")
axA.set_title("What the units do at 50 Hz\n(each dot = one curated unit)")
axA.text(0.5, -0.16, "dHPC: a driven-up subset (mean ↑).   LEC: mostly suppressed (↓).\nDifferent per region → not a uniform passive echo.",
         transform=axA.transAxes, ha="center", fontsize=8.5, color="#444")

# ---- Panel B: inference ladder ----
axB = fig.add_subplot(gs[0, 1]); axB.axis("off")
axB.set_xlim(0, 10); axB.set_ylim(0, 10)
rungs = [
    ("Is it electrical / mechanical ARTIFACT?", "NO — sorted single units change their\nfiring RATE; pickup can't do that.", "#2a9d8f", "✗"),
    ("Is it a PASSIVE ECHO (brain as a relay)?", "UNLIKELY — regions respond DIFFERENTLY\n(dHPC driven-up subset; LEC suppressed) and\nthe LFP 50 Hz is induced, not phase-locked.\nA relay would look the same everywhere.", "#2a9d8f", "✗"),
    ("ACTIVE, region-specific processing?", "SUPPORTED — the 50 Hz input is transformed\ndifferently by each circuit (not relayed).", "#1d6f63", "✓"),
    ("Are the regions COORDINATING\n(\"working together\")?", "NOT TESTED — needs spike–field coupling +\ncross-region coherence. We showed each region\nresponds, not that they coordinate.", "#b58900", "?"),
]
y = 9.0
for title, body, col, mark in rungs:
    box = FancyBboxPatch((0.3, y - 1.75), 9.4, 1.6, boxstyle="round,pad=0.08,rounding_size=0.15",
                         linewidth=1.4, edgecolor=col, facecolor=col + "1A")
    axB.add_patch(box)
    axB.text(0.6, y - 0.35, mark, fontsize=17, color=col, fontweight="bold", va="center")
    axB.text(1.4, y - 0.45, title, fontsize=10.5, fontweight="bold", va="center")
    axB.text(1.4, y - 1.25, body, fontsize=8.6, va="center", color="#333")
    y -= 2.0
axB.set_title("What does the 50 Hz response mean? — the inference ladder", fontsize=12, pad=2)

fig.suptitle("50 Hz haptic stimulation: an ACTIVE, region-specific neural response (not a passive echo) — coordination not yet tested",
             fontsize=12.5)
fig.tight_layout(rect=[0, 0, 1, 0.95])
out = D / "spike_50hz_interpretation.png"
fig.savefig(out, dpi=160, bbox_inches="tight")
print("wrote", out)
