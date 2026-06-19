#!/usr/bin/env python
"""Figure: do dHPC & LEC coordinate at 50 Hz? (spike-field + LFP coherence)."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = Path("analysis/outputs/dec4/coordination_50hz")
r = json.load(open(D / "coordination_summary.json"))

fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))


def grp(ax, labels, on, off, ylabel, title, floor=None):
    x = np.arange(len(labels)); w = 0.36
    ax.bar(x - w/2, on, w, color="#e76f51", label="50 Hz ON")
    ax.bar(x + w/2, off, w, color="#9aa0a6", label="OFF (control)")
    if floor is not None:
        ax.axhline(floor, color="#444", ls=":", lw=1)
        ax.text(ax.get_xlim()[1], floor, " chance", fontsize=8, va="bottom", ha="right", color="#444")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel(ylabel); ax.set_title(title, fontsize=11)
    ax.legend(fontsize=8, frameon=False)


# A: within-region spike-field locking
grp(axes[0], ["dHPC→dHPC", "LEC→LEC"],
    [r["within:dhpc_spikes_x_dhpc_phase:ON"]["mean_unit_PLV"], r["within:lec_spikes_x_lec_phase:ON"]["mean_unit_PLV"]],
    [r["within:dhpc_spikes_x_dhpc_phase:OFF"]["mean_unit_PLV"], r["within:lec_spikes_x_lec_phase:OFF"]["mean_unit_PLV"]],
    "mean spike–field PLV", "Within-region spike–field at 50 Hz\n(weak; barely ON>OFF)")

# B: cross-region spike-field locking (the artifact-robust coordination test)
grp(axes[1], ["dHPC spk→LEC ϕ", "LEC spk→dHPC ϕ"],
    [r["cross:dhpc_spikes_x_lec_phase:ON"]["mean_unit_PLV"], r["cross:lec_spikes_x_dhpc_phase:ON"]["mean_unit_PLV"]],
    [r["cross:dhpc_spikes_x_lec_phase:OFF"]["mean_unit_PLV"], r["cross:lec_spikes_x_dhpc_phase:OFF"]["mean_unit_PLV"]],
    "mean spike–field PLV", "Cross-region spike–field (artifact-robust)\nvery weak; NOT ON>OFF")

# C: cross-region LFP-LFP 50 Hz coherence
grp(axes[2], ["dHPC ↔ LEC LFP"],
    [r["LFP_coherence_dHPC_LEC_50Hz:ON"]["coherence"]],
    [r["LFP_coherence_dHPC_LEC_50Hz:OFF"]["coherence"]],
    "50 Hz phase coherence", "Cross-region LFP coherence\nON>OFF — but likely SHARED signal",
    floor=r["LFP_coherence_dHPC_LEC_50Hz:ON"]["chance_floor"])
axes[2].text(0.5, 0.97, "spikes don't follow it →\nnot proof of coordination", transform=axes[2].transAxes,
             ha="center", va="top", fontsize=8.5, color="#9a3", fontstyle="italic")

fig.suptitle("Do dHPC & LEC 'work together' at 50 Hz?  —  LFP coherence rises, but the artifact-robust spike test does NOT → no clear coordination",
             fontsize=11.5)
fig.tight_layout(rect=[0, 0, 1, 0.94])
out = D / "coordination_50hz.png"
fig.savefig(out, dpi=160)
print("wrote", out)
