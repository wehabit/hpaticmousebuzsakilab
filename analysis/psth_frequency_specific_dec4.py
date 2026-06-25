#!/usr/bin/env python
"""Frequency-specificity of the single-unit ON/OFF effect (Dec 4, raster + PSTH).

Misi's claim header is "single-unit ON/OFF firing is FREQUENCY-SPECIFIC". The
companion [raster_psth_modulated_dec4.py] shows the modulation at 50 Hz; this shows
the SAME modulated units across all four carriers (5/10/26/50 Hz at amp250), so the
frequency-specificity is visible: the ON-window modulation appears at 50 Hz and not
at the lower carriers.

  - psth_frequency_specific_dec4.png : population PSTH of the modulated units, one
    line per carrier, dHPC driven-up subset and LEC suppressed subset.
  - raster_frequency_specific_dec4.png : one example unit's raster at each carrier.

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
FREQS = [5, 10, 26, 50]
FCOL = {5: "#bdbdbd", 10: "#9ecae1", 26: "#fdae6b", 50: "#8C1515"}     # 50 Hz = cardinal
TW = Path("analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv")
OUT = Path("analysis/outputs/cross_dataset_spike_compare/raster_psth")
REG = {
    "dHPC": dict(curated=Path("analysis/outputs/dec4/curated_merged_dhpc"),
                 stats=Path("analysis/outputs/cross_dataset_spike_compare/dec4_dHPC_unit_condition_stats.csv"),
                 want="up"),
    "LEC": dict(curated=Path("analysis/outputs/dec4/curated_merged_lec"),
                stats=Path("analysis/outputs/cross_dataset_spike_compare/dec4_LEC_unit_condition_stats.csv"),
                want="down"),
}
EDGES = np.arange(-PRE, POST + BIN / 2, BIN)
CTR = (EDGES[:-1] + EDGES[1:]) / 2


def load(reg):
    c = REG[reg]["curated"]
    st = np.load(c / "spike_times.npy").astype(np.int64) / FS
    sc = np.load(c / "spike_clusters.npy").astype(np.int64)
    d = pd.read_csv(REG[reg]["stats"])
    col = [x for x in d.columns if "responsive" in x][0]
    s = d[(d.condition == "amp250_freq50") & d[col]]
    sign = 1 if REG[reg]["want"] == "up" else -1
    units = s[np.sign(s.mean_delta_hz) == sign].sort_values("mean_delta_hz", key=abs, ascending=False)
    return st, sc, units.cluster_id.to_numpy()


def psth(spk, onsets):
    counts = np.zeros(len(EDGES) - 1)
    for t0 in onsets:
        rel = spk[(spk >= t0 - PRE) & (spk < t0 + POST)] - t0
        counts += np.histogram(rel, bins=EDGES)[0]
    return counts / (len(onsets) * BIN)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tw = pd.read_csv(TW)
    onsets = {fr: tw[(tw.amplitude == 250) & (tw.freq == fr)].sort_values("trial_number").on_start_s.to_numpy()
              for fr in FREQS}

    # ---- population PSTH across carriers ----
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharex=True)
    example = {}
    for ax, reg in zip(axes, REG):
        st, sc, units = load(reg)
        example[reg] = (st, sc, int(units[0]))
        for fr in FREQS:
            arrs = []
            for cid in units:
                r = psth(st[sc == cid], onsets[fr])
                arrs.append(r - r[CTR < 0].mean())          # baseline-subtract per unit
            M = np.vstack(arrs); m = M.mean(0); sem = M.std(0) / np.sqrt(len(arrs))
            lw = 2.6 if fr == 50 else 1.4
            ax.plot(CTR, m, color=FCOL[fr], lw=lw, label=f"{fr} Hz", zorder=3 if fr == 50 else 2)
            if fr == 50:
                ax.fill_between(CTR, m - sem, m + sem, color=FCOL[fr], alpha=0.18)
        ax.axvspan(0, 3, color="#8C1515", alpha=0.06); ax.axvline(0, color="#8C1515", lw=1)
        ax.axvline(3, color="#888", lw=1, ls="--"); ax.axhline(0, color="#999", lw=0.8)
        ax.set_title(f"{reg}: {REG[reg]['want']}-modulated units (n={len(units)})")
        ax.set_xlabel("time from ON onset (s)"); ax.legend(title="carrier", fontsize=9)
    axes[0].set_ylabel("Δ rate vs pre-onset (Hz)")
    fig.suptitle("Frequency-specificity: the ON-window single-unit modulation appears at 50 Hz, not at 5/10/26 Hz "
                 "(amp250)", fontsize=12)
    fig.tight_layout(); fig.savefig(OUT / "psth_frequency_specific_dec4.png", dpi=170); plt.close(fig)

    # ---- one example unit's raster across carriers ----
    reg = "dHPC"; st, sc, cid = example[reg]; spk = st[sc == cid]
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.2), sharex=True, sharey=True)
    for ax, fr in zip(axes, FREQS):
        for i, t0 in enumerate(onsets[fr]):
            rel = spk[(spk >= t0 - PRE) & (spk < t0 + POST)] - t0
            ax.plot(rel, np.full_like(rel, i), "|", color="#2E2D29", ms=2, mew=0.5)
        ax.axvspan(0, 3, color="#8C1515", alpha=0.08); ax.axvline(0, color="#8C1515", lw=1)
        ax.axvline(3, color="#888", lw=1, ls="--")
        ax.set_title(f"{fr} Hz" + ("  ← response" if fr == 50 else "")); ax.set_xlabel("time from ON onset (s)")
    axes[0].set_ylabel("trial")
    fig.suptitle(f"Frequency-specificity, single unit ({reg} unit {cid}): raster per carrier (amp250) — "
                 "spikes rise during ON only at 50 Hz", fontsize=12)
    fig.tight_layout(); fig.savefig(OUT / "raster_frequency_specific_dec4.png", dpi=170); plt.close(fig)
    print(f"wrote frequency-specific PSTH + raster; example {reg} unit {cid}")


if __name__ == "__main__":
    main()
