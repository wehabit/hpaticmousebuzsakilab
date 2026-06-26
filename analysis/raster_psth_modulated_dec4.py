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
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.offsetbox import TextArea, HPacker, VPacker, AnchoredOffsetbox

FS = 20_000.0
PRE, POST, BIN = 1.0, 6.0, 0.1            # show the full 3 s ON + 3 s OFF (to +6 s)
TW = Path("analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv")
OUT = Path("analysis/outputs/cross_dataset_spike_compare/raster_psth")
REG = {
    "dHPC": dict(curated=Path("analysis/outputs/dec4/curated_merged_dhpc"),
                 stats=Path("analysis/outputs/cross_dataset_spike_compare/dec4_dHPC_unit_condition_stats.csv")),
    "LEC": dict(curated=Path("analysis/outputs/dec4/curated_merged_lec"),
                stats=Path("analysis/outputs/cross_dataset_spike_compare/dec4_LEC_unit_condition_stats.csv")),
}
UP, DOWN = "#8C1515", "#2E2D29"           # Stanford cardinal / black
BASE_ORANGE = "#E98300"                    # Stanford "Poppy" — pre-study baseline reference line
PRESTUDY_MIN = 30.0                        # minutes of quiet recording used as the baseline
START_MARGIN, GAP = 60.0, 30.0            # skip first 60 s (settling); 30 s gap before trial 1
ALL_UNIT_CMAP = LinearSegmentedColormap.from_list(
    "stanford_delta_rate", ["#2E2D29", "#F4F4F4", "#8C1515"], N=256
)


def load(reg):
    c = REG[reg]["curated"]
    st = np.load(c / "spike_times.npy").astype(np.int64) / FS
    sc = np.load(c / "spike_clusters.npy").astype(np.int64)
    d = pd.read_csv(REG[reg]["stats"])
    col = [x for x in d.columns if "responsive" in x][0]
    s = d[(d.condition == "amp250_freq50") & d[col]].copy()
    s["abs"] = s.mean_delta_hz.abs()
    return st, sc, s.sort_values("abs", ascending=False)


def load_good_units(reg):
    c = REG[reg]["curated"]
    st = np.load(c / "spike_times.npy").astype(np.int64) / FS
    sc = np.load(c / "spike_clusters.npy").astype(np.int64)
    d = pd.read_csv(REG[reg]["stats"])
    col = [x for x in d.columns if "responsive" in x][0]
    s = d[d.condition == "amp250_freq50"].copy()
    s["responsive"] = s[col].astype(bool)
    s = s.sort_values("mean_delta_hz", ascending=False)
    return st, sc, s


def baseline_rate_lookup(tw):
    """Per-unit mean firing rate (Hz) in the 30 min of quiet recording immediately
    BEFORE the first trial: window = [first_on - 30 s - 30 min, first_on - 30 s], with
    no stimulation. This is the never-stimulated reference drawn on each PSTH; using the
    30 min nearest the study (rather than the whole pre-experiment block) keeps it as
    contemporaneous to the trials as possible. Returns (lut, (start, end, dur))."""
    first_on = float(tw.on_start_s.min())
    bl_end = first_on - GAP
    bl_start = max(START_MARGIN, bl_end - PRESTUDY_MIN * 60.0)
    dur = bl_end - bl_start
    lut = {}
    for reg in REG:
        c = REG[reg]["curated"]
        st = np.load(c / "spike_times.npy").astype(np.int64) / FS
        sc = np.load(c / "spike_clusters.npy").astype(np.int64)
        sel = sc[(st >= bl_start) & (st < bl_end)]
        ids, counts = np.unique(sel, return_counts=True)
        for cid, n in zip(ids, counts):
            lut[(reg, int(cid))] = float(n) / dur
    return lut, (bl_start, bl_end, dur)


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


def plot_all_good_unit_psth(tw):
    """Compact all-unit view: one heatmap row per curated good unit."""
    onsets = tw[(tw.amplitude == 250) & (tw.freq == 50)].sort_values("trial_number").on_start_s.to_numpy()
    mats = {}
    stats = {}
    ctr = None
    vmax_pool = []
    for reg in REG:
        st, sc, s = load_good_units(reg)
        rows = []
        for cid in s.cluster_id:
            ctr, rate = psth(st[sc == cid], onsets)
            base = rate[ctr < 0].mean()
            row = rate - base
            rows.append(row)
            vmax_pool.append(np.nanpercentile(np.abs(row), 98))
        mats[reg] = np.vstack(rows)
        stats[reg] = s

    vmax = max(0.5, float(np.nanpercentile(vmax_pool, 85)))
    fig = plt.figure(figsize=(15, 9.5), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, width_ratios=[7.5, 1.7, 0.25], wspace=0.12, hspace=0.32)
    heat_axes = []
    bar_axes = []
    ims = []
    for r, reg in enumerate(REG):
        M = mats[reg]
        s = stats[reg].reset_index(drop=True)
        ax = fig.add_subplot(gs[r, 0])
        bx = fig.add_subplot(gs[r, 1], sharey=ax)
        im = ax.imshow(
            M,
            aspect="auto",
            interpolation="nearest",
            origin="upper",
            extent=[ctr[0], ctr[-1], len(s) - 0.5, -0.5],
            cmap=ALL_UNIT_CMAP,
            vmin=-vmax,
            vmax=vmax,
        )
        ims.append(im)
        heat_axes.append(ax)
        bar_axes.append(bx)

        labels = [
            f"u{int(row.cluster_id)}{'*' if row.responsive else ''}"
            for row in s.itertuples()
        ]
        ax.set_yticks(np.arange(len(labels)))
        ax.set_yticklabels(labels, fontsize=8)
        ax.axvspan(0, 3, color="#8C1515", alpha=0.08)
        ax.axvspan(3, 6, color="#B6B1A9", alpha=0.12)
        ax.axvline(0, color="#8C1515", lw=1)
        ax.axvline(3, color="#7A7772", lw=1, ls="--")
        ax.set_xlim(-PRE, POST)
        ax.set_title(f"{reg}: all curated good units (n={len(s)})")
        ax.set_ylabel("unit (* = q<0.05)")
        if r == 1:
            ax.set_xlabel("time from ON onset (s)")

        vals = s.mean_delta_hz.to_numpy()
        colors = np.where(vals >= 0, UP, DOWN)
        bx.barh(np.arange(len(vals)), vals, color=colors, alpha=0.88)
        bx.axvline(0, color="#777", lw=0.9)
        bx.set_title("ON-OFF\nHz", fontsize=9)
        bx.tick_params(axis="y", left=False, labelleft=False)
        bx.set_ylim(len(s) - 0.5, -0.5)
        lim = max(0.5, float(np.nanmax(np.abs(vals))) * 1.15)
        bx.set_xlim(-lim, lim)
        bx.grid(axis="x", alpha=0.18)
        if r == 1:
            bx.set_xlabel("Hz")

    cax = fig.add_subplot(gs[:, 2])
    cb = fig.colorbar(ims[0], cax=cax)
    cb.set_label("PSTH change vs pre-ON baseline (Hz)")
    fig.suptitle(
        "Dec 4 amp250_freq50 — compact PSTH heatmap for all 30 curated good units\n"
        "Each row is one unit, averaged across 200 trials; red shade = 3 s ON, grey shade = 3 s OFF",
        fontsize=12,
    )
    fig.savefig(OUT / "raster_psth_all_good_units_dec4.png", dpi=170)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tw = pd.read_csv(TW)
    onsets = tw[(tw.amplitude == 250) & (tw.freq == 50)].sort_values("trial_number").on_start_s.to_numpy()
    base_lut, base_win = baseline_rate_lookup(tw)

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
        ax.axvspan(0, 3, color="#8C1515", alpha=0.08); ax.axvspan(3, 6, color="#457b9d", alpha=0.08)
        ax.axvline(0, color="#8C1515", lw=1); ax.axvline(3, color="#457b9d", lw=1, ls="--")
        arrow = "↑" if direction == "up" else "↓"
        ax.set_title(f"{reg} unit {cid}\n{arrow} ({delta:+.2f} Hz ON−OFF)", fontsize=10)
        ax.set_ylabel("trial"); ax.set_ylim(0, len(rs))
        # PSTH
        axp = axes[1][j]
        ctr, rate = psth(spk, onsets)
        axp.fill_between(ctr, rate, color=UP if direction == "up" else DOWN, alpha=0.85, step="mid")
        axp.axvspan(0, 3, color="#8C1515", alpha=0.08); axp.axvspan(3, 6, color="#457b9d", alpha=0.08)
        axp.axvline(0, color="#8C1515", lw=1); axp.axvline(3, color="#457b9d", lw=1, ls="--")
        bl = base_lut.get((reg, cid))
        if bl is not None:                                   # 30-min pre-study baseline
            axp.set_ylim(0, max(float(rate.max()), bl) * 1.26)   # headroom so the label clears the data
            axp.axhline(bl, color=BASE_ORANGE, ls=(0, (4, 3)), lw=1.6, zorder=5)
            axp.text(0.98, 0.97, f"baseline {bl:.1f} Hz", color=BASE_ORANGE, fontsize=7.5,
                     va="top", ha="right", transform=axp.transAxes, zorder=6)
        axp.set_xlabel("time from ON onset (s)"); axp.set_xlim(-PRE, POST)
        if j == 0:
            axp.set_ylabel("rate (Hz)")
    fig.suptitle("Modulated single units at amp250_freq50 — raster + PSTH  "
                 "(red shade = 3 s ON · blue shade = 3 s OFF · orange dashed = 30-min pre-study baseline)", fontsize=12)
    fig.tight_layout(rect=[0, 0.075, 1, 1])
    bl_start, bl_end, dur = base_win
    grey = "#444"; fp = dict(size=8.2)
    _ta = lambda s, c: TextArea(s, textprops=dict(color=c, **fp))
    line1 = HPacker(align="baseline", pad=0, sep=0, children=[
        _ta("Orange ", BASE_ORANGE),
        _ta(f"dashed baseline = each unit's mean firing rate over the {dur/60:.0f} min of quiet "
            "recording right before the study", grey)])
    line2 = _ta(f"(t ≈ {bl_start/60:.0f}–{bl_end/60:.0f} min, ending 30 s before the first trial, no "
                "stimulation) — the never-stimulated reference the PSTH is measured against.", grey)
    cap = VPacker(align="center", pad=0, sep=2, children=[line1, line2])
    cax = fig.add_axes([0.0, 0.0, 1.0, 0.075]); cax.axis("off")
    cax.add_artist(AnchoredOffsetbox(loc="center", child=cap, frameon=False,
                                     bbox_to_anchor=(0.5, 0.5), bbox_transform=cax.transAxes, pad=0))
    fig.savefig(OUT / "raster_psth_examples_dec4.png", dpi=170); plt.close(fig)

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
        ax.axvspan(0, 3, color="#8C1515", alpha=0.08); ax.axvspan(3, 6, color="#457b9d", alpha=0.08)
        ax.axvline(0, color="#8C1515", lw=1); ax.axvline(3, color="#457b9d", lw=1, ls="--"); ax.axhline(0, color="#999", lw=0.8)
        ax.set_title(f"{reg}: population PSTH (baseline-subtracted)"); ax.set_xlabel("time from ON onset (s)")
        ax.legend(fontsize=9)
    axes[0].set_ylabel("Δ rate vs pre-onset (Hz)")
    fig.suptitle("Population PSTH of modulated units, amp250_freq50 — dHPC driven-up subset, LEC suppression  "
                 "(ON 0–3 s · OFF 3–6 s)", fontsize=12)
    fig.tight_layout(); fig.savefig(OUT / "psth_population_modulated_dec4.png", dpi=170); plt.close(fig)
    plot_all_good_unit_psth(tw)
    print(f"wrote raster/PSTH for {len(examples)} example units; population over",
          {k: len(v) for k, v in pop.items()})


if __name__ == "__main__":
    main()
