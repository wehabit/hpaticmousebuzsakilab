#!/usr/bin/env python
"""Raster + PSTH for the MODULATED single units (Dec 4, amp250_freq50).

Misi's request: show raster/PSTH for the responsive neurons, not all units. We take
the units that are significant (q<0.05) at amp250_freq50 (the strongest condition)
in each region, and for each show a spike raster (200 trials, aligned to ON onset)
and the trial-averaged PSTH, with the 3 s ON and 3 s OFF windows marked. We also
show the population PSTH split by direction (driven-up vs suppressed).

Outputs -> analysis/outputs/cross_dataset_spike_compare/raster_psth/ and (builders)
results/dec4/11_Spikes/.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FS = 20_000.0
PRE, POST, BIN = 1.0, 4.0, 0.1            # PSTH window (s) and bin
TW = Path("analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv")
OUT = Path("analysis/outputs/cross_dataset_spike_compare/raster_psth")
REG = {
    "dHPC": dict(curated=Path("analysis/outputs/dec4/curated_merged_dhpc"),
                 stats=Path("analysis/outputs/cross_dataset_spike_compare/dec4_dHPC_unit_condition_stats.csv")),
    "LEC": dict(curated=Path("analysis/outputs/dec4/curated_merged_lec"),
                stats=Path("analysis/outputs/cross_dataset_spike_compare/dec4_LEC_unit_condition_stats.csv")),
}
UP, DOWN = "#8C1515", "#2E2D29"           # Stanford cardinal / black


def load(reg):
    c = REG[reg]["curated"]
    st = np.load(c / "spike_times.npy").astype(np.int64) / FS
    sc = np.load(c / "spike_clusters.npy").astype(np.int64)
    d = pd.read_csv(REG[reg]["stats"])
    col = [x for x in d.columns if "responsive" in x][0]
    s = d[(d.condition == "amp250_freq50") & d[col]].copy()
    s["abs"] = s.mean_delta_hz.abs()
    return st, sc, s.sort_values("abs", ascending=False)


def psth(spk, onsets):
    edges = np.arange(-PRE, POST + BIN / 2, BIN)
    counts = np.zeros(len(edges) - 1)
    for t0 in onsets:
        rel = spk[(spk >= t0 - PRE) & (spk < t0 + POST)] - t0
        counts += np.histogram(rel, bins=edges)[0]
    return (edges[:-1] + edges[1:]) / 2, counts / (len(onsets) * BIN)   # Hz


def raster_spikes(spk, onsets):
    out = []
    for i, t0 in enumerate(onsets):
        rel = spk[(spk >= t0 - PRE) & (spk < t0 + POST)] - t0
        out.append(rel)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tw = pd.read_csv(TW)
    onsets = tw[(tw.amplitude == 250) & (tw.freq == 50)].sort_values("trial_number").on_start_s.to_numpy()

    # ---------- example units: top up + top down per region ----------
    examples = []   # (reg, cid, direction, delta)
    pop = {}        # (reg, dir) -> list of psth arrays
    for reg in REG:
        st, sc, resp = load(reg)
        ups = resp[resp.mean_delta_hz > 0]; downs = resp[resp.mean_delta_hz < 0]
        for grp, lab in [(ups, "up"), (downs, "down")]:
            arrs = []
            for cid in grp.cluster_id:
                _, r = psth(st[sc == cid], onsets); arrs.append(r)
            pop[(reg, lab)] = arrs
        for grp in (ups, downs):
            if len(grp):
                r = grp.iloc[0]
                examples.append((reg, int(r.cluster_id), "up" if r.mean_delta_hz > 0 else "down",
                                 float(r.mean_delta_hz)))

    # ---------- Figure 1: example rasters + PSTHs ----------
    n = len(examples)
    fig, axes = plt.subplots(2, n, figsize=(3.5 * n, 6.2), sharex=True,
                             gridspec_kw=dict(height_ratios=[2.2, 1]))
    for j, (reg, cid, direction, delta) in enumerate(examples):
        st, sc, _ = load(reg)
        spk = st[sc == cid]
        rs = raster_spikes(spk, onsets)
        ax = axes[0][j]
        for i, rel in enumerate(rs):
            ax.plot(rel, np.full_like(rel, i), "|", color="#2E2D29", ms=2, mew=0.5)
        ax.axvspan(0, 3, color="#8C1515", alpha=0.07); ax.axvline(0, color="#8C1515", lw=1)
        ax.axvline(3, color="#888", lw=1, ls="--")
        ax.set_title(f"{reg} unit {cid}\n{direction} ({delta:+.2f} Hz ON−OFF)", fontsize=10)
        ax.set_ylabel("trial"); ax.set_ylim(0, len(rs))
        # PSTH
        axp = axes[1][j]
        ctr, rate = psth(spk, onsets)
        axp.fill_between(ctr, rate, color=UP if direction == "up" else DOWN, alpha=0.85, step="mid")
        axp.axvspan(0, 3, color="#8C1515", alpha=0.07); axp.axvline(0, color="#8C1515", lw=1)
        axp.axvline(3, color="#888", lw=1, ls="--")
        axp.set_xlabel("time from ON onset (s)"); axp.set_xlim(-PRE, POST)
        if j == 0:
            axp.set_ylabel("rate (Hz)")
    fig.suptitle("Modulated single units at amp250_freq50 — raster + PSTH (red = 3 s ON; dashed = OFF onset)",
                 fontsize=12)
    fig.tight_layout(); fig.savefig(OUT / "raster_psth_examples_dec4.png", dpi=170); plt.close(fig)

    # ---------- Figure 2: population PSTH by direction ----------
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharex=True)
    ctr = psth(np.array([0.0]), onsets[:1])[0]
    for ax, reg in zip(axes, REG):
        for lab, col in [("up", UP), ("down", DOWN)]:
            arrs = pop.get((reg, lab), [])
            if not arrs:
                continue
            M = np.vstack(arrs)
            # normalize each unit to its own pre-onset baseline (mean over [-1,0])
            base = M[:, ctr < 0].mean(1, keepdims=True)
            Mn = M - base
            m = Mn.mean(0); sem = Mn.std(0) / np.sqrt(len(arrs))
            ax.plot(ctr, m, color=col, lw=2, label=f"{lab}-modulated (n={len(arrs)})")
            ax.fill_between(ctr, m - sem, m + sem, color=col, alpha=0.2)
        ax.axvspan(0, 3, color="#8C1515", alpha=0.07); ax.axvline(0, color="#8C1515", lw=1)
        ax.axvline(3, color="#888", lw=1, ls="--"); ax.axhline(0, color="#999", lw=0.8)
        ax.set_title(f"{reg}: population PSTH (baseline-subtracted)"); ax.set_xlabel("time from ON onset (s)")
        ax.legend(fontsize=9)
    axes[0].set_ylabel("Δ rate vs pre-onset (Hz)")
    fig.suptitle("Population PSTH of modulated units, amp250_freq50 — dHPC driven-up subset, LEC suppression",
                 fontsize=12)
    fig.tight_layout(); fig.savefig(OUT / "psth_population_modulated_dec4.png", dpi=170); plt.close(fig)
    print(f"wrote raster/PSTH for {len(examples)} example units; population over",
          {k: len(v) for k, v in pop.items()})


if __name__ == "__main__":
    main()
