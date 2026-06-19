#!/usr/bin/env python
"""Figure: do dHPC & LEC coordinate at 50 Hz? Bootstrap-CI, annotated for clarity."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = Path("analysis/outputs/dec4/coordination_50hz")
r = json.load(open(D / "coordination_summary.json"))
rng = np.random.default_rng(0)


def boot(vals, nb=5000):
    vals = np.asarray(vals, float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return np.nan, np.nan, np.nan
    bs = np.array([np.mean(rng.choice(vals, len(vals), replace=True)) for _ in range(nb)])
    return float(vals.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def bars(ax, items, chance, ylabel, title, highlight=False):
    """items: list of (label, on_vals, off_vals)."""
    x = np.arange(len(items)); w = 0.36
    for j, side, col, off in [(0, "50 Hz ON", "#e76f51", -w/2), (1, "OFF (control)", "#9aa0a6", +w/2)]:
        ms, los, his = [], [], []
        for _, on_v, off_v in items:
            m, lo, hi = boot(on_v if j == 0 else off_v)
            ms.append(m); los.append(m - lo); his.append(hi - m)
        ax.bar(x + off, ms, w, yerr=[los, his], capsize=4, color=col,
               error_kw={"elinewidth": 1.2, "ecolor": "#333"}, label=side)
    if chance is not None:
        ax.axhline(chance, color="#444", ls=":", lw=1.2)
        ax.text(ax.get_xlim()[1], chance, " chance", fontsize=8, va="bottom", ha="right", color="#444")
    ax.set_xticks(x); ax.set_xticklabels([it[0] for it in items], fontsize=9)
    ax.set_ylabel(ylabel); ax.legend(fontsize=8, frameon=False, loc="upper right")
    tcol = "#b5179e" if highlight else "black"
    ax.set_title(title, fontsize=11, color=tcol, fontweight="bold" if highlight else "normal")
    if highlight:
        for s in ax.spines.values():
            s.set_edgecolor("#b5179e"); s.set_linewidth(2)


def pu(key):  # per-unit PLV list
    return r[key]["per_unit_PLV"]


fig, axes = plt.subplots(1, 3, figsize=(13, 4.9))
fig.subplots_adjust(bottom=0.34, top=0.83, left=0.07, right=0.985, wspace=0.26)

bars(axes[0],
     [("dHPC", pu("within:dhpc_spikes_x_dhpc_phase:ON"), pu("within:dhpc_spikes_x_dhpc_phase:OFF")),
      ("LEC", pu("within:lec_spikes_x_lec_phase:ON"), pu("within:lec_spikes_x_lec_phase:OFF"))],
     None, "spike–field PLV (mean ± 95% CI)", "1. Each region vs its OWN 50 Hz rhythm")

bars(axes[1],
     [("dHPC→LEC", pu("cross:dhpc_spikes_x_lec_phase:ON"), pu("cross:dhpc_spikes_x_lec_phase:OFF")),
      ("LEC→dHPC", pu("cross:lec_spikes_x_dhpc_phase:ON"), pu("cross:lec_spikes_x_dhpc_phase:OFF"))],
     None, "spike–field PLV (mean ± 95% CI)",
     "2. SPIKES vs the OTHER region's rhythm\n(the decisive, artifact-proof test)", highlight=True)

on = r["LFP_coherence_dHPC_LEC_50Hz:ON"]["per_trial_coherence"]
off = r["LFP_coherence_dHPC_LEC_50Hz:OFF"]["per_trial_coherence"]
bars(axes[2], [("dHPC↔LEC", on, off)],
     r["LFP_coherence_dHPC_LEC_50Hz:ON"]["chance_floor_per_trial"],
     "50 Hz phase coherence (mean ± 95% CI)", "3. The two LFPs' 50 Hz coupling")

# captions at fixed figure positions, well below the axes (no overlap)
caps = [
    (0.215, "Weak; ON ≈ OFF (CIs overlap).\nBaseline gamma coupling,\nnot stimulus-driven.", "#444"),
    (0.545, "Very weak; ON ≈ OFF (CIs overlap).\nNeurons do NOT track the other\nregion → no coordination.", "#b5179e"),
    (0.875, "ON > OFF (CIs separate) — looks like\ncoupling, BUT inflated by a SHARED\nsignal; spikes (panel 2) don't follow\nit → not real coordination.", "#9a6700"),
]
for x, txt, col in caps:
    fig.text(x, 0.235, txt, ha="center", va="top", fontsize=8.6, color=col)

fig.suptitle("Do dHPC & LEC 'work together' at 50 Hz?  —  If they did, panel 2 (cross-region SPIKES) would rise\n"
             "during ON; it does NOT. Panel 3 (LFP) rises but is fooled by a shared signal.  ⇒  NO clear coordination.",
             fontsize=11)
fig.text(0.5, 0.02, "50 Hz trials, all amplitudes pooled (amp100+180+250, 600 trials). ON = 3 s buzz; OFF = following 3 s gap.",
         ha="center", fontsize=8.3, color="#666")
out = D / "coordination_50hz.png"
fig.savefig(out, dpi=120)
print("wrote", out)
