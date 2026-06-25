#!/usr/bin/env python
"""Dec 3 raster + PSTH negative control — parallel to the Dec 4 modulated figure.

Dec 3 has ZERO responsive units (0/174 at q<0.05), so there are no modulated neurons
to show — the null IS the result. To make the Dec 3 / Dec 4 comparison fully parallel
(Dec 4 has raster_psth_examples_dec4.png), this shows the SAME raster+PSTH layout for
the four Dec 3 units with the largest |ON−OFF| at the strongest condition
(amp250_freq26): even those "most-modulated" units (all non-significant) show no
ON-window change. Same pipeline, modulation when it exists (Dec 4 / 50 Hz) and none
when it doesn't (Dec 3 / 5 / 26 Hz).

Outputs -> analysis/outputs/cross_dataset_spike_compare/raster_psth/.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FS = 20_000.0
PRE, POST, BIN = 1.0, 4.0, 0.1
COND = ("amp250", "freq26", 250, 26)            # strongest Dec 3 condition
CURATED = Path("analysis/outputs/dec3/curated_merged")
STATS = Path("analysis/outputs/cross_dataset_spike_compare/dec3_dHPC_unit_condition_stats.csv")
TW = Path("analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv")
OUT = Path("analysis/outputs/cross_dataset_spike_compare/raster_psth")
EDGES = np.arange(-PRE, POST + BIN / 2, BIN)
CTR = (EDGES[:-1] + EDGES[1:]) / 2


def psth(spk, onsets):
    c = np.zeros(len(EDGES) - 1)
    for t0 in onsets:
        c += np.histogram(spk[(spk >= t0 - PRE) & (spk < t0 + POST)] - t0, bins=EDGES)[0]
    return c / (len(onsets) * BIN)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    st = np.load(CURATED / "spike_times.npy").astype(np.int64) / FS
    sc = np.load(CURATED / "spike_clusters.npy").astype(np.int64)
    tw = pd.read_csv(TW)
    d = pd.read_csv(STATS)
    onsets = tw[(tw.amplitude == COND[2]) & (tw.freq == COND[3])].sort_values("trial_number").on_start_s.to_numpy()

    sub = d[d.condition == f"{COND[0]}_{COND[1]}"].copy()
    sub["abs"] = sub.mean_delta_hz.abs()
    top = sub.sort_values("abs", ascending=False).head(4)

    fig, axes = plt.subplots(2, 4, figsize=(14, 6.2), sharex=True,
                             gridspec_kw=dict(height_ratios=[2.2, 1]))
    for j, (_, r) in enumerate(top.iterrows()):
        cid = int(r.cluster_id); spk = st[sc == cid]
        # raster
        ax = axes[0][j]
        for i, t0 in enumerate(onsets):
            rel = spk[(spk >= t0 - PRE) & (spk < t0 + POST)] - t0
            ax.plot(rel, np.full_like(rel, i), "|", color="#2E2D29", ms=2, mew=0.5)
        ax.axvspan(0, 3, color="#8C1515", alpha=0.06); ax.axvline(0, color="#8C1515", lw=1)
        ax.axvline(3, color="#888", lw=1, ls="--")
        qv = float(r.q_value_bh_within_unit_set)
        ax.set_title(f"unit {cid}\nON−OFF {r.mean_delta_hz:+.2f} Hz (q={qv:.2f}, n.s.)", fontsize=10)
        ax.set_ylabel("trial"); ax.set_ylim(0, len(onsets))
        # PSTH
        axp = axes[1][j]
        axp.fill_between(CTR, psth(spk, onsets), color="#53565A", alpha=0.85, step="mid")
        axp.axvspan(0, 3, color="#8C1515", alpha=0.06); axp.axvline(0, color="#8C1515", lw=1)
        axp.axvline(3, color="#888", lw=1, ls="--")
        axp.set_xlabel("time from ON onset (s)"); axp.set_xlim(-PRE, POST)
        if j == 0:
            axp.set_ylabel("rate (Hz)")
    fig.suptitle("Dec 3 NEGATIVE CONTROL — raster + PSTH at the strongest condition (amp250_freq26): "
                 "even the top units show no ON/OFF modulation (0/174 responsive)", fontsize=12)
    fig.tight_layout(); fig.savefig(OUT / "raster_psth_dec3_null.png", dpi=170); plt.close(fig)
    print(f"wrote Dec 3 raster+PSTH null; top units {list(top.cluster_id)} at amp250_freq26")


if __name__ == "__main__":
    main()
