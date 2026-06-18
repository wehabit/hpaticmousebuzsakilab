#!/usr/bin/env python
"""Visualize the cross-dataset single-unit ON/OFF result."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = Path("analysis/outputs/cross_dataset_spike_compare")
df = pd.read_csv(D / "per_condition_by_dataset.csv")
df["freq"] = df.condition.str.extract(r"freq(\d+)").astype(int)
df["amp"] = df.condition.str.extract(r"amp(\d+)").astype(int)

fig, axes = plt.subplots(1, 3, figsize=(16.5, 4.8))

# Panel 1: responsive unit-conditions by drive frequency, per dataset.
ax = axes[0]
freqs = [5, 10, 26, 50]
datasets = ["dec3_dHPC", "dec4_dHPC", "dec4_LEC"]
colors = {"dec3_dHPC": "#999999", "dec4_dHPC": "#2a9d8f", "dec4_LEC": "#e76f51"}
w = 0.26
for i, ds in enumerate(datasets):
    sub = df[df.dataset == ds]
    vals = [int(sub[sub.freq == f].n_responsive_q05_within_unit_set.sum()) if f in sub.freq.values else 0 for f in freqs]
    x = np.arange(len(freqs)) + (i - 1) * w
    ax.bar(x, vals, width=w, color=colors[ds], label=ds)
ax.set_xticks(np.arange(len(freqs)))
ax.set_xticklabels([f"{f} Hz" for f in freqs])
ax.set_ylabel("# responsive units (q<0.05)")
ax.set_title("Single-unit ON/OFF responses\nconcentrate at 50 Hz (Dec 4)")
ax.legend(fontsize=8, frameon=False)
ax.text(0.02, 0.95, "Dec 3 tested only 5 & 26 Hz", transform=ax.transAxes, fontsize=8, color="#666", va="top")

# Panels 2 & 3: Dec 4 mean ON-OFF (Hz) as amplitude x frequency heatmaps, annotated with #responsive.
for ax, ds, title in [(axes[1], "dec4_dHPC", "Dec 4 dHPC"), (axes[2], "dec4_LEC", "Dec 4 LEC")]:
    sub = df[df.dataset == ds]
    amps = [100, 180, 250]
    M = np.full((len(amps), len(freqs)), np.nan)
    R = np.zeros((len(amps), len(freqs)), dtype=int)
    for r, a in enumerate(amps):
        for c, f in enumerate(freqs):
            row = sub[(sub.amp == a) & (sub.freq == f)]
            if len(row):
                M[r, c] = float(row.mean_unit_delta_hz.iloc[0])
                R[r, c] = int(row.n_responsive_q05_within_unit_set.iloc[0])
    vmax = np.nanmax(np.abs(M)); vmax = max(vmax, 0.1)
    im = ax.imshow(M, cmap="coolwarm", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(len(freqs))); ax.set_xticklabels([f"{f}" for f in freqs])
    ax.set_yticks(range(len(amps))); ax.set_yticklabels(amps)
    ax.set_xlabel("drive freq (Hz)"); ax.set_ylabel("amplitude")
    ax.set_title(f"{title}\nmean ON−OFF (Hz); number = #responsive")
    for r in range(len(amps)):
        for c in range(len(freqs)):
            if not np.isnan(M[r, c]):
                ax.text(c, r, R[r, c], ha="center", va="center",
                        fontsize=10, fontweight="bold",
                        color="black" if R[r, c] else "#999")
    fig.colorbar(im, ax=ax, shrink=0.8, label="Hz")

fig.suptitle("Curated single-unit ON-vs-OFF firing — Dec 3 null at 5/26 Hz; Dec 4 effect at 50 Hz / high amplitude",
             fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.96])
out = D / "spike_onoff_cross_dataset.png"
fig.savefig(out, dpi=170)
print("wrote", out)
