#!/usr/bin/env python
"""50 Hz LFP pickup by verified XML group / shank section (Dec 4).

The Dec 4 LEC LFP carries a 50 Hz bump, but it is artifact-suspect. This resolves it
per verified channel group: for each of the 6 XML groups / shank sections
(dHPC sections 1-4, LEC shank-groups 5-6)
we plot every channel's 50 Hz ON-minus-OFF envelope amplitude (the established pickup metric, from
artifact_check_50hz), split into tissue-good vs dead/disconnected/excluded channels, and
annotate the dead fraction. A neural 50 Hz LFP should not be strongest on disconnected
channels; the observed 50 Hz tracks the pickup-heavy LEC groups, with dead channels
strongest and tissue-good LEC channels also elevated — strengthening "LFP 50 Hz is
pickup-contaminated, while the single-unit result is the clean readout."

Reuses the per-channel 50 Hz ON-minus-OFF array already computed by the artifact screen
(artifact_check_50hz/artifact_check_arrays.npz, key 'diff') plus channel health from
channel_metadata + channel_qc. No re-derivation of the spectral measure.

Outputs -> analysis/outputs/cross_dataset_spike_compare/lfp_50hz_by_shank/ and (builder)
results/dec4/12_ChannelQC_Traces/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARR = Path("analysis/outputs/dec4/artifact_check_50hz/artifact_check_arrays.npz")
META = Path("analysis/outputs/dec4/spike_sorting_prep/channel_metadata.csv")
QC = Path("analysis/outputs/dec4/channel_qc/channel_qc_metrics_perprobe.csv")
OUT = Path("analysis/outputs/cross_dataset_spike_compare/lfp_50hz_by_shank")
GOOD_C, DEAD_C = "#53565A", "#8C1515"   # grey tissue-good / cardinal dead-pickup


def shank_group_of(ch: int) -> int:
    """Verified XML group / shank section: dHPC 0-127 -> 1-4, LEC 128-255 -> 5-6."""
    if ch < 128:
        return 1 + ch // 32
    return 5 + (ch - 128) // 64


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    diff = np.load(ARR, allow_pickle=True)["diff"]            # per-channel 50 Hz ON-minus-OFF (256,)
    meta = pd.read_csv(META)
    qc = pd.read_csv(QC)[["channel", "exclude_auto"]]
    df = meta.merge(qc, on="channel")
    df["fiftyhz_on_minus_off"] = diff[df.channel.to_numpy()]
    df["bad"] = df.exclude_auto | df.is_bad | (~df.connected)
    df["shank_group"] = df.channel.map(shank_group_of)
    df["region"] = np.where(df.channel < 128, "dHPC", "LEC")
    df.to_csv(OUT / "fiftyhz_by_shank_channels_dec4.csv", index=False)

    groups = sorted(df.shank_group.unique())
    rng = np.random.default_rng(0)
    summary, xs = {}, {s: i for i, s in enumerate(groups)}

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.5, 6.4), gridspec_kw=dict(width_ratios=[2.2, 1]))

    # ---- Panel A: per-channel strip by verified XML group, good vs dead ----
    for s in groups:
        sub = df[df.shank_group == s]
        for bad, color, lab in [(False, GOOD_C, "tissue-good"), (True, DEAD_C, "dead / excluded")]:
            v = sub[sub.bad == bad].fiftyhz_on_minus_off.to_numpy()
            if len(v):
                axA.scatter(xs[s] + rng.uniform(-0.16, 0.16, len(v)), v, s=22, c=color,
                            alpha=0.7, edgecolors="none", zorder=3)
        good = sub[~sub.bad].fiftyhz_on_minus_off
        dead = sub[sub.bad].fiftyhz_on_minus_off
        if len(good):
            axA.plot([xs[s] - 0.22, xs[s] + 0.22], [good.mean()] * 2, color=GOOD_C, lw=3, zorder=4)
        if len(dead):
            axA.plot([xs[s] - 0.22, xs[s] + 0.22], [dead.mean()] * 2, color=DEAD_C, lw=3, zorder=4)
        pct = 100 * sub.bad.mean()
        summary[f"group{s}"] = dict(
            region=sub.region.iloc[0], n=int(len(sub)), n_dead=int(sub.bad.sum()),
            pct_dead=round(pct, 1),
            good_50hz_mean=round(float(good.mean()) if len(good) else np.nan, 2),
            dead_50hz_mean=round(float(dead.mean()) if len(dead) else np.nan, 2))
    axA.axhline(0, color="#333", lw=0.9)
    axA.set_xticks(range(len(groups)))
    axA.set_xticklabels([f"group {s}\n({df[df.shank_group==s].region.iloc[0]})" for s in groups])
    axA.set_ylabel("50 Hz ON − OFF envelope amplitude (a.u., per channel)")
    ytop = axA.get_ylim()[1]
    for s in groups:
        sub = df[df.shank_group == s]
        axA.text(xs[s], ytop * 0.98, f"{int(sub.bad.sum())}/{len(sub)} dead",
                 ha="center", va="top", fontsize=8.5, color="#555")
    axA.set_title("Per-channel 50 Hz pickup by verified XML group — tissue-good (grey) vs dead/excluded (red)")
    axA.legend(handles=[plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=GOOD_C, markersize=8, label="tissue-good channel"),
                        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=DEAD_C, markersize=8, label="dead / excluded channel"),
                        plt.Line2D([0], [0], color="#333", lw=3, label="group mean")],
               fontsize=8.5, loc="lower left")

    # ---- Panel B: dead-fraction vs 50 Hz pickup, one point per group ----
    for s in groups:
        d = summary[f"group{s}"]
        col = "#53565A" if d["region"] == "dHPC" else "#C43A31"
        axB.scatter(d["pct_dead"], d["good_50hz_mean"], s=90, c=col, edgecolors="#222", zorder=3)
        axB.annotate(f"G{s}", (d["pct_dead"], d["good_50hz_mean"]), fontsize=9,
                     xytext=(4, 3), textcoords="offset points")
    axB.axhline(0, color="#333", lw=0.8)
    axB.set_xlabel("% channels dead / excluded in group")
    axB.set_ylabel("mean 50 Hz ON−OFF envelope, tissue-good channels")
    axB.set_title("Pickup-heavy groups carry more 50 Hz\n(dHPC grey, LEC red)")
    axB.grid(alpha=0.2)

    fig.suptitle("Dec 4 — 50 Hz LFP is largest on pickup-heavy LEC groups; dead channels are strongest\n"
                 "dHPC groups sit near 0; tissue-good LEC channels are elevated too, so this is pickup-contaminated rather than clean tissue LFP",
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "fiftyhz_by_shank_dec4.png", dpi=170); plt.close(fig)
    (OUT / "fiftyhz_by_shank_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
