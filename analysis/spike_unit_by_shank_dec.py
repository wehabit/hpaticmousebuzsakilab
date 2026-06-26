#!/usr/bin/env python
"""Unit response by shank section / depth (Dec 4).

For every curated good unit we assemble: region, shank section / XML group,
best local/global channel, contact depth (y within the section, from the probe geometry), putative cell type, and the
amp250_freq50 ON-OFF firing change (+ q<0.05 responsiveness). We then place each unit at its
(section, depth) and color it by ON-OFF effect, outline the responders, and shape it by
cell type — so the question "do the 50 Hz-responsive units sit on one contact
zone?" is answered by eye, with a per-section tally alongside.

Depth uses the Kilosort channel_positions y-coordinate (relative, in microns). We make
NO absolute layer/medial-lateral claim here — only relative position on the verified
groups/sections; fine laminar interpretation still needs histology / exact orientation.

Outputs -> analysis/outputs/cross_dataset_spike_compare/unit_by_shank/ and (builders)
results/dec4/11_Spikes/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D

OUT = Path("analysis/outputs/cross_dataset_spike_compare/unit_by_shank")
CELLTYPE = Path("analysis/outputs/cross_dataset_spike_compare/celltype/celltype_features_by_unit.csv")
COND = "amp250_freq50"
UP, DOWN = "#8C1515", "#2E2D29"
REG = {
    "dHPC": dict(dataset="dec4_dHPC",
                 curated=Path("analysis/outputs/dec4/curated_merged_dhpc"),
                 stats=Path("analysis/outputs/cross_dataset_spike_compare/dec4_dHPC_unit_condition_stats.csv")),
    "LEC": dict(dataset="dec4_LEC",
                curated=Path("analysis/outputs/dec4/curated_merged_lec"),
                stats=Path("analysis/outputs/cross_dataset_spike_compare/dec4_LEC_unit_condition_stats.csv")),
}
MARKER = {"pyramidal-like": "o", "interneuron-like": "^"}


def channel_lookup(curated: Path):
    """raw channel id -> (shank section, x_um, y_um) from the curated probe geometry."""
    cmap = np.load(curated / "channel_map.npy").astype(int)
    pos = np.load(curated / "channel_positions.npy").astype(float)
    shk = np.load(curated / "channel_shanks.npy").astype(int)
    return {int(c): (int(shk[i]), float(pos[i, 0]), float(pos[i, 1])) for i, c in enumerate(cmap)}


def build_table():
    ct = pd.read_csv(CELLTYPE)
    rows = []
    for reg, cfg in REG.items():
        lut = channel_lookup(cfg["curated"])
        st = pd.read_csv(cfg["stats"])
        col = [c for c in st.columns if "responsive" in c][0]
        s = st[st.condition == COND].copy()
        cmap = ct[ct.dataset == cfg["dataset"]].set_index("cluster_id")["cell_type"].to_dict()
        for r in s.itertuples():
            ch = int(r.best_raw_channel)
            shank, x_um, y_um = lut.get(ch, (int(r.best_channel_shank), np.nan, np.nan))
            global_ch = ch if reg == "dHPC" else ch + 128
            rows.append(dict(
                region=reg, cluster_id=int(r.cluster_id), shank_section=int(shank),
                best_channel=ch, best_channel_global=global_ch, x_um=x_um, depth_um=y_um,
                cell_type=cmap.get(int(r.cluster_id), "unknown"),
                on_off_hz=round(float(r.mean_delta_hz), 4),
                responsive=bool(getattr(r, col)),
            ))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = build_table()
    df.to_csv(OUT / "unit_by_shank_dec4.csv", index=False)

    vmax = max(0.5, float(np.nanpercentile(np.abs(df.on_off_hz), 95)))
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    cmap = plt.get_cmap("RdGy_r")
    rng = np.random.default_rng(0)

    fig, axes = plt.subplots(1, 2, figsize=(13, 7.5), gridspec_kw=dict(width_ratios=[2, 1]))
    summary = {}
    for ax, reg in zip(axes, REG):
        sub = df[df.region == reg]
        shanks = sorted(sub.shank_section.unique())
        xmap = {sh: i for i, sh in enumerate(shanks)}
        for r in sub.itertuples():
            xj = xmap[r.shank_section] + rng.uniform(-0.18, 0.18)
            ax.scatter(xj, r.depth_um, s=120 + 260 * abs(r.on_off_hz) / vmax,
                       c=[cmap(norm(r.on_off_hz))], marker=MARKER.get(r.cell_type, "s"),
                       edgecolors=("#111" if r.responsive else "none"),
                       linewidths=(1.8 if r.responsive else 0), zorder=3, alpha=0.95)
        ax.set_xticks(range(len(shanks))); ax.set_xticklabels([f"section {s}" for s in shanks])
        ax.set_xlim(-0.6, len(shanks) - 0.4); ax.invert_yaxis()          # larger y plotted lower
        ax.set_ylabel("contact depth in section/group — y (µm, relative)")
        nresp = int(sub.responsive.sum())
        ax.set_title(f"Dec 4 {reg} — {COND}\n{len(sub)} units · {nresp} responsive (q<0.05)", fontsize=11)
        # per-section responder tally
        tally = (sub[sub.responsive].groupby("shank_section").size().reindex(shanks, fill_value=0))
        tot = sub.groupby("shank_section").size().reindex(shanks, fill_value=0)
        txt = "responders / units:\n" + "  ".join(f"G{s}: {int(tally[s])}/{int(tot[s])}" for s in shanks)
        ax.text(0.02, 0.02, txt, transform=ax.transAxes, fontsize=8.5, va="bottom",
                bbox=dict(boxstyle="round,pad=0.3", fc="#F4F4F4", ec="#bbb"))
        ax.grid(axis="y", alpha=0.15)
        summary[reg] = dict(n_units=len(sub), n_responsive=nresp,
                            responders_by_section={int(s): int(tally[s]) for s in shanks},
                            units_by_section={int(s): int(tot[s]) for s in shanks})

    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cb = fig.colorbar(sm, ax=axes, fraction=0.04, pad=0.02)
    cb.set_label("ON−OFF firing change at 50 Hz (Hz)")
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor="#999", markersize=10, label="pyramidal-like"),
               Line2D([0], [0], marker="^", color="none", markerfacecolor="#999", markersize=10, label="interneuron-like"),
               Line2D([0], [0], marker="o", color="none", markerfacecolor="none", markeredgecolor="#111",
                      markeredgewidth=1.8, markersize=11, label="responsive (q<0.05)")]
    axes[0].legend(handles=handles, loc="upper right", fontsize=8.5, framealpha=0.9)
    fig.suptitle("Unit response by shank section & depth (Dec 4) — dHPC responders span sections\n"
                 "marker color = ON−OFF Hz · size = |effect| · shape = putative type · black outline = significant",
                 fontsize=12)
    fig.savefig(OUT / "unit_by_shank_dec4.png", dpi=170, bbox_inches="tight"); plt.close(fig)
    (OUT / "unit_by_shank_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
