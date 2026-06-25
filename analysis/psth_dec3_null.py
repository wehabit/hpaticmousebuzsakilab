#!/usr/bin/env python
"""Dec 3 single-unit PSTH — the negative control (no modulation at 5/26 Hz).

Dec 3 has ZERO responsive units (0/174 unit-conditions at q<0.05), and only tested
5 and 26 Hz. So there are no "modulated neurons" to raster — that null IS the result.
This figure shows it directly: the curated good dHPC population PSTH stays flat at
both Dec 3 carriers, and even the single most-modulated unit (largest |ON−OFF|, still
non-significant) is unremarkable. It is the negative control for the Dec 4 50 Hz
effect — the same pipeline finds modulation when it exists (Dec 4 / 50 Hz) and none
when it does not (Dec 3 / 5 / 26 Hz).

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
FREQS = [5, 26]
FCOL = {5: "#9ecae1", 26: "#fdae6b"}
CURATED = Path("analysis/outputs/dec3/curated_merged")
STATS = Path("analysis/outputs/cross_dataset_spike_compare/dec3_dHPC_unit_condition_stats.csv")
TW = Path("analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv")
OUT = Path("analysis/outputs/cross_dataset_spike_compare/raster_psth")
EDGES = np.arange(-PRE, POST + BIN / 2, BIN)
CTR = (EDGES[:-1] + EDGES[1:]) / 2


def psth(spk, onsets):
    counts = np.zeros(len(EDGES) - 1)
    for t0 in onsets:
        rel = spk[(spk >= t0 - PRE) & (spk < t0 + POST)] - t0
        counts += np.histogram(rel, bins=EDGES)[0]
    return counts / (len(onsets) * BIN)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    st = np.load(CURATED / "spike_times.npy").astype(np.int64) / FS
    sc = np.load(CURATED / "spike_clusters.npy").astype(np.int64)
    g = pd.read_csv(CURATED / "cluster_group.tsv", sep="\t")
    gids = g.loc[g.group == "good", "cluster_id"].to_numpy(int)
    tw = pd.read_csv(TW)
    d = pd.read_csv(STATS)
    onsets = {fr: tw[(tw.amplitude == 250) & (tw.freq == fr)].sort_values("trial_number").on_start_s.to_numpy()
              for fr in FREQS}

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharex=False)
    # (a) population PSTH across Dec 3 carriers — flat
    ax = axes[0]
    for fr in FREQS:
        arrs = [psth(st[sc == cid], onsets[fr]) - psth(st[sc == cid], onsets[fr])[CTR < 0].mean() for cid in gids]
        M = np.vstack(arrs); m = M.mean(0); sem = M.std(0) / np.sqrt(len(arrs))
        ax.plot(CTR, m, color=FCOL[fr], lw=2, label=f"{fr} Hz")
        ax.fill_between(CTR, m - sem, m + sem, color=FCOL[fr], alpha=0.2)
    ax.axvspan(0, 3, color="#8C1515", alpha=0.06); ax.axvline(0, color="#8C1515", lw=1)
    ax.axvline(3, color="#888", lw=1, ls="--"); ax.axhline(0, color="#999", lw=0.8)
    ax.set_ylim(-3, 6)                                  # same scale as Dec 4 for honest comparison
    ax.set_title(f"dHPC population (n={len(gids)} good units) — flat at both carriers")
    ax.set_xlabel("time from ON onset (s)"); ax.set_ylabel("Δ rate vs pre-onset (Hz)"); ax.legend(title="carrier")
    # (b) the single most-modulated unit (largest |ON-OFF|, still non-significant)
    ax = axes[1]
    best = d.reindex(d.mean_delta_hz.abs().sort_values(ascending=False).index).iloc[0]
    cid, cond = int(best.cluster_id), best.condition
    fr = int(cond.split("freq")[1]); amp = int(cond.split("amp")[1].split("_")[0])
    on = tw[(tw.amplitude == amp) & (tw.freq == fr)].sort_values("trial_number").on_start_s.to_numpy()
    ctr, rate = CTR, psth(st[sc == cid], on)
    ax.fill_between(ctr, rate, color="#53565A", alpha=0.85, step="mid")
    ax.axvspan(0, 3, color="#8C1515", alpha=0.06); ax.axvline(0, color="#8C1515", lw=1)
    ax.axvline(3, color="#888", lw=1, ls="--")
    qv = float(best.q_value_bh_within_unit_set)
    ax.set_title(f"most-modulated unit {cid} @ {cond}\n(ON−OFF {best.mean_delta_hz:+.2f} Hz, q={qv:.2f} — n.s.)")
    ax.set_xlabel("time from ON onset (s)"); ax.set_ylabel("rate (Hz)")
    fig.suptitle("Dec 3 NEGATIVE CONTROL: no single-unit ON/OFF modulation at 5 or 26 Hz (0/174 responsive) — "
                 "contrast the Dec 4 50 Hz effect", fontsize=12)
    fig.tight_layout(); fig.savefig(OUT / "psth_dec3_null_control.png", dpi=170); plt.close(fig)
    print(f"wrote Dec 3 null control; most-modulated unit {cid} @ {cond} ({best.mean_delta_hz:+.2f} Hz, n.s.)")


if __name__ == "__main__":
    main()
