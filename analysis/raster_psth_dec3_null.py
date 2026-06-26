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
from matplotlib.colors import LinearSegmentedColormap

FS = 20_000.0
PRE, POST, BIN = 1.0, 4.0, 0.1
COND = ("amp250", "freq26", 250, 26)            # strongest Dec 3 condition
CURATED = Path("analysis/outputs/dec3/curated_merged")
STATS = Path("analysis/outputs/cross_dataset_spike_compare/dec3_dHPC_unit_condition_stats.csv")
TW = Path("analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv")
OUT = Path("analysis/outputs/cross_dataset_spike_compare/raster_psth")
EDGES = np.arange(-PRE, POST + BIN / 2, BIN)
CTR = (EDGES[:-1] + EDGES[1:]) / 2
UP, DOWN = "#8C1515", "#2E2D29"            # Stanford cardinal / black
ALL_UNIT_CMAP = LinearSegmentedColormap.from_list(                  # matches the Dec 4 all-units figure
    "stanford_delta_rate", ["#2E2D29", "#F4F4F4", "#8C1515"], N=256)


def psth(spk, onsets):
    c = np.zeros(len(EDGES) - 1)
    for t0 in onsets:
        c += np.histogram(spk[(spk >= t0 - PRE) & (spk < t0 + POST)] - t0, bins=EDGES)[0]
    return c / (len(onsets) * BIN)


def plot_all_good_units_heatmap():
    """Dec 3 counterpart of the Dec 4 all-good-units PSTH heatmap (raster_psth_all_good_
    units_dec4.png): every curated good unit as one row at the strongest Dec 3 condition
    (amp250_freq26), baseline-subtracted to the per-trial pre-ON second, full ON+OFF
    window. Visual null — nothing changes during ON (0/29 responsive)."""
    PRE_H, POST_H, BIN_H = 1.0, 6.0, 0.1                    # full 3 s ON + 3 s OFF, matches Dec 4
    edges = np.arange(-PRE_H, POST_H + BIN_H / 2, BIN_H)
    ctr = (edges[:-1] + edges[1:]) / 2
    st = np.load(CURATED / "spike_times.npy").astype(np.int64) / FS
    sc = np.load(CURATED / "spike_clusters.npy").astype(np.int64)
    tw = pd.read_csv(TW)
    onsets = tw[(tw.amplitude == COND[2]) & (tw.freq == COND[3])].sort_values("trial_number").on_start_s.to_numpy()
    d = pd.read_csv(STATS)
    col = [c for c in d.columns if "responsive" in c][0]
    s = d[d.condition == f"{COND[0]}_{COND[1]}"].copy()
    s["responsive"] = s[col].astype(bool)
    s = s.sort_values("mean_delta_hz", ascending=False).reset_index(drop=True)

    rows, vmax_pool = [], []
    for cid in s.cluster_id:
        spk = st[sc == int(cid)]
        counts = np.zeros(len(edges) - 1)
        for t0 in onsets:
            counts += np.histogram(spk[(spk >= t0 - PRE_H) & (spk < t0 + POST_H)] - t0, bins=edges)[0]
        rate = counts / (len(onsets) * BIN_H)
        row = rate - rate[ctr < 0].mean()                   # baseline-subtract to pre-ON second
        rows.append(row); vmax_pool.append(np.nanpercentile(np.abs(row), 98))
    M = np.vstack(rows)
    vmax = max(0.5, float(np.nanpercentile(vmax_pool, 85)))

    fig = plt.figure(figsize=(13, 9), constrained_layout=True)
    gs = fig.add_gridspec(1, 3, width_ratios=[7.5, 1.7, 0.25], wspace=0.12)
    ax = fig.add_subplot(gs[0, 0]); bx = fig.add_subplot(gs[0, 1], sharey=ax)
    cax = fig.add_subplot(gs[0, 2])
    im = ax.imshow(M, aspect="auto", interpolation="nearest", origin="upper",
                   extent=[ctr[0], ctr[-1], len(s) - 0.5, -0.5],
                   cmap=ALL_UNIT_CMAP, vmin=-vmax, vmax=vmax)
    labels = [f"u{int(r.cluster_id)}{'*' if r.responsive else ''}" for r in s.itertuples()]
    ax.set_yticks(np.arange(len(labels))); ax.set_yticklabels(labels, fontsize=8)
    ax.axvspan(0, 3, color="#8C1515", alpha=0.08); ax.axvspan(3, 6, color="#B6B1A9", alpha=0.12)
    ax.axvline(0, color="#8C1515", lw=1); ax.axvline(3, color="#7A7772", lw=1, ls="--")
    ax.set_xlim(-PRE_H, POST_H); ax.set_xlabel("time from ON onset (s)")
    ax.set_title(f"dHPC: all curated good units (n={len(s)})")
    ax.set_ylabel("unit (* = q<0.05; none)")

    vals = s.mean_delta_hz.to_numpy(); colors = np.where(vals >= 0, UP, DOWN)
    bx.barh(np.arange(len(vals)), vals, color=colors, alpha=0.88)
    bx.axvline(0, color="#777", lw=0.9); bx.set_title("ON-OFF\nHz", fontsize=9)
    bx.tick_params(axis="y", left=False, labelleft=False); bx.set_ylim(len(s) - 0.5, -0.5)
    lim = max(0.5, float(np.nanmax(np.abs(vals))) * 1.15); bx.set_xlim(-lim, lim)
    bx.grid(axis="x", alpha=0.18); bx.set_xlabel("Hz")

    cb = fig.colorbar(im, cax=cax); cb.set_label("PSTH change vs pre-ON baseline (Hz)")
    fig.suptitle(
        f"Dec 3 NEGATIVE CONTROL — amp250_freq26: compact PSTH heatmap for all {len(s)} curated good units\n"
        "Each row is one unit, averaged across 200 trials; red shade = 3 s ON, grey shade = 3 s OFF "
        "— no ON-driven change (0/29 responsive)", fontsize=12)
    fig.savefig(OUT / "raster_psth_all_good_units_dec3.png", dpi=170); plt.close(fig)
    print(f"wrote Dec 3 all-good-units heatmap: n={len(s)}, responsive={int(s.responsive.sum())}")


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
    plot_all_good_units_heatmap()


if __name__ == "__main__":
    main()
