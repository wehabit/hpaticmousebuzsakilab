#!/usr/bin/env python
"""Combined all-curated-good-units PSTH heatmap — Dec 4 (dHPC, LEC) + Dec 3 (dHPC), 3 rows.

One figure, three session/region rows, every curated good unit as a row:
  * Dec 4 dHPC @ amp250_freq50 — driven during the 50 Hz ON window (the effect)
  * Dec 4 LEC  @ amp250_freq50 — mixed / principal-cell suppression during ON
  * Dec 3 dHPC @ amp250_freq26 — negative control, 0/29 responsive (flat null)

Each row is one unit's trial-averaged PSTH minus its own pre-ON-second baseline, over the
full 3 s ON + 3 s OFF window. A single shared color scale and a side bar of ON-OFF Hz make
the Dec 4 effect and the Dec 3 null directly comparable in one view. Rows are sized by unit
count (height_ratios), so cell height is the same across panels.

Outputs -> analysis/outputs/cross_dataset_spike_compare/raster_psth/ and (builders)
results/dec3/11_Spikes/ + results/dec4/11_Spikes/.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

FS = 20_000.0
PRE, POST, BIN = 1.0, 6.0, 0.1            # full 3 s ON + 3 s OFF
OUT = Path("analysis/outputs/cross_dataset_spike_compare/raster_psth")
UP, DOWN = "#8C1515", "#2E2D29"            # Stanford cardinal / black
ALL_UNIT_CMAP = LinearSegmentedColormap.from_list(
    "stanford_delta_rate", ["#2E2D29", "#F4F4F4", "#8C1515"], N=256)

PANELS = [
    dict(label="Dec 4  dHPC  ·  amp250_freq50",
         curated="analysis/outputs/dec4/curated_merged_dhpc",
         stats="analysis/outputs/cross_dataset_spike_compare/dec4_dHPC_unit_condition_stats.csv",
         tw="analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv",
         amp=250, freq=50, cond="amp250_freq50"),
    dict(label="Dec 4  LEC  ·  amp250_freq50",
         curated="analysis/outputs/dec4/curated_merged_lec",
         stats="analysis/outputs/cross_dataset_spike_compare/dec4_LEC_unit_condition_stats.csv",
         tw="analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv",
         amp=250, freq=50, cond="amp250_freq50"),
    dict(label="Dec 3  dHPC  ·  amp250_freq26   (negative control)",
         curated="analysis/outputs/dec3/curated_merged",
         stats="analysis/outputs/cross_dataset_spike_compare/dec3_dHPC_unit_condition_stats.csv",
         tw="analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv",
         amp=250, freq=26, cond="amp250_freq26"),
]
EDGES = np.arange(-PRE, POST + BIN / 2, BIN)
CTR = (EDGES[:-1] + EDGES[1:]) / 2


def build_panel(p):
    """Per-unit baseline-subtracted PSTH matrix for one session/region, sorted by ON-OFF."""
    st = np.load(Path(p["curated"]) / "spike_times.npy").astype(np.int64) / FS
    sc = np.load(Path(p["curated"]) / "spike_clusters.npy").astype(np.int64)
    tw = pd.read_csv(p["tw"])
    onsets = tw[(tw.amplitude == p["amp"]) & (tw.freq == p["freq"])].sort_values("trial_number").on_start_s.to_numpy()
    d = pd.read_csv(p["stats"])
    col = [c for c in d.columns if "responsive" in c][0]
    s = d[d.condition == p["cond"]].copy()
    s["responsive"] = s[col].astype(bool)
    s = s.sort_values("mean_delta_hz", ascending=False).reset_index(drop=True)
    rows, vpool = [], []
    for cid in s.cluster_id:
        spk = st[sc == int(cid)]
        counts = np.zeros(len(EDGES) - 1)
        for t0 in onsets:
            counts += np.histogram(spk[(spk >= t0 - PRE) & (spk < t0 + POST)] - t0, bins=EDGES)[0]
        rate = counts / (len(onsets) * BIN)
        row = rate - rate[CTR < 0].mean()                  # baseline-subtract to pre-ON second
        rows.append(row); vpool.append(np.nanpercentile(np.abs(row), 98))
    return dict(M=np.vstack(rows), s=s, vpool=vpool, n=len(s), n_trials=len(onsets))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    panels = [build_panel(p) for p in PANELS]
    vmax = max(0.5, float(np.nanpercentile(np.concatenate([pp["vpool"] for pp in panels]), 85)))
    bar_lim = max(0.5, float(max(np.nanmax(np.abs(pp["s"].mean_delta_hz.to_numpy())) for pp in panels)) * 1.20)

    fig = plt.figure(figsize=(14, 13), constrained_layout=True)
    gs = fig.add_gridspec(len(panels), 3, width_ratios=[7.5, 1.6, 0.22],
                          height_ratios=[pp["n"] for pp in panels], wspace=0.10, hspace=0.16)
    ims = []
    for r, (p, pp) in enumerate(zip(PANELS, panels)):
        M, s = pp["M"], pp["s"]
        ax = fig.add_subplot(gs[r, 0]); bx = fig.add_subplot(gs[r, 1], sharey=ax)
        im = ax.imshow(M, aspect="auto", interpolation="nearest", origin="upper",
                       extent=[CTR[0], CTR[-1], pp["n"] - 0.5, -0.5],
                       cmap=ALL_UNIT_CMAP, vmin=-vmax, vmax=vmax)
        ims.append(im)
        labels = [f"u{int(rr.cluster_id)}{'*' if rr.responsive else ''}" for rr in s.itertuples()]
        ax.set_yticks(np.arange(len(labels))); ax.set_yticklabels(labels, fontsize=7)
        ax.axvspan(0, 3, color="#8C1515", alpha=0.08); ax.axvspan(3, 6, color="#B6B1A9", alpha=0.12)
        ax.axvline(0, color="#8C1515", lw=1); ax.axvline(3, color="#7A7772", lw=1, ls="--")
        ax.set_xlim(-PRE, POST)
        nresp = int(s.responsive.sum())
        ax.set_title(f"{p['label']}   (n={pp['n']} units · {nresp} responsive at q<0.05)", fontsize=11)
        ax.set_ylabel("unit (* = q<0.05)")
        if r == len(panels) - 1:
            ax.set_xlabel("time from ON onset (s)")

        vals = s.mean_delta_hz.to_numpy()
        bx.barh(np.arange(len(vals)), vals, color="#53565A", alpha=0.9)   # single neutral color; sign read by direction
        bx.axvline(0, color="#777", lw=0.9)
        bx.tick_params(axis="y", left=False, labelleft=False)
        bx.set_ylim(pp["n"] - 0.5, -0.5); bx.set_xlim(-bar_lim, bar_lim)
        bx.grid(axis="x", alpha=0.18)
        # label the largest |ON-OFF| change in this panel, always on the right side of the bar axis
        imax = int(np.nanargmax(np.abs(vals))); vmx = float(vals[imax]); cidmx = int(s.cluster_id.iloc[imax])
        bx.text(0.98, imax, f"u{cidmx}: {vmx:+.2f} Hz",
                transform=bx.get_yaxis_transform(), va="center", ha="right",
                fontsize=7.6, fontweight="bold", color="#2E2D29", zorder=6,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.82))
        if r == 0:
            bx.set_title("ON-OFF\nHz", fontsize=9)
        if r == len(panels) - 1:
            bx.set_xlabel("Hz")

    cax = fig.add_subplot(gs[:, 2])
    cb = fig.colorbar(ims[0], cax=cax); cb.set_label("PSTH change vs pre-ON baseline (Hz)")
    fig.suptitle(
        "All curated good units — Dec 4 (dHPC, LEC @ 50 Hz) vs Dec 3 dHPC negative control (@ 26 Hz)\n"
        "Each row is one unit's trial-averaged PSTH (baseline-subtracted), shared color & bar scale · "
        "red shade = 3 s ON, grey shade = 3 s OFF", fontsize=12.5)
    fig.savefig(OUT / "raster_psth_all_good_units_combined.png", dpi=160); plt.close(fig)
    print("wrote combined 3-row heatmap:",
          {p["label"].split("·")[0].strip(): f"n={pp['n']}, resp={int(pp['s'].responsive.sum())}"
           for p, pp in zip(PANELS, panels)})


if __name__ == "__main__":
    main()
