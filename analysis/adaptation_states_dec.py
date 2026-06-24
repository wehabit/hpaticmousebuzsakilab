#!/usr/bin/env python
"""Early / middle / late adaptation, anchored to the true baseline (Dec 3 + Dec 4).

Splits each condition's repeats into early/middle/late thirds (by trial order) and
asks three questions the static state analyses can't:

  1. Does the 50 Hz single-unit response GROW or FADE with repetition?
     (Dec 4 amp250_freq50 ON-baseline, per third, dHPC & LEC.)
  2. Does the OFF window drift TOWARD or AWAY from baseline over the session?
     (OFF-baseline per third — connects the within-trial control to the global drift.)
  3. Does 26 Hz adaptation explain the Dec 3 LFP response?
     (Dec 3 dHPC 26 Hz driven-band power per third; Dec 4 LEC 50 Hz for comparison.)

Spike effects are referenced to each unit's pre-experiment baseline
(state_rates_by_unit.csv); LFP driven power is dB vs the baseline PSD. Bootstrap 95%
CIs (units for spikes, channels for LFP). Outputs ->
analysis/outputs/cross_dataset_spike_compare/adaptation_states/ and (builders)
results/dec*/08_Adaptation/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lfp_aperiodic_states_dec import mean_psd, load_bad, boot_ci, SESSIONS, FS_LFP, START_MARGIN, GAP
from lfp_bandpower_states_dec import band_power

ROOT = Path("/Users/paris/Documents/Buzsakli Lab Github")
WIN = 3.0
THIRDS = ["early", "middle", "late"]
TC = {"early": "#90be6d", "middle": "#f9c74f", "late": "#f3722c"}
BASE_CSV = ROOT / "analysis/outputs/cross_dataset_spike_compare/baseline_poststudy/state_rates_by_unit.csv"
OUT = ROOT / "analysis/outputs/cross_dataset_spike_compare/adaptation_states"

SPIKE = {
    "dec4_dHPC": dict(peth=ROOT / "analysis/outputs/dec4/spike_peth_on_off_dhpc",
                      curated=ROOT / "analysis/outputs/dec4/curated_merged_dhpc"),
    "dec4_LEC": dict(peth=ROOT / "analysis/outputs/dec4/spike_peth_on_off_lec",
                     curated=ROOT / "analysis/outputs/dec4/curated_merged_lec"),
}
TW4 = ROOT / "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv"


def third_slices(idx):
    n = len(idx); k = n // 3
    return {"early": idx[:k], "middle": idx[k:2 * k], "late": idx[2 * k:]}


def spike_adaptation():
    tw = pd.read_csv(TW4)
    base = pd.read_csv(BASE_CSV)
    rows = []
    cond_mask = (tw.amplitude == 250) & (tw.freq == 50)
    cond_idx = np.where(cond_mask.to_numpy())[0]          # trial rows, in order
    for name, cfg in SPIKE.items():
        on = np.load(cfg["peth"] / "on_counts_by_trial_unit.npy") / WIN
        off = np.load(cfg["peth"] / "off_counts_by_trial_unit.npy") / WIN
        good = pd.read_csv(cfg["curated"] / "cluster_group.tsv", sep="\t")
        gids = good.loc[good.group == "good", "cluster_id"].to_numpy(int)
        bmap = base[base.dataset == name].set_index("cluster_id")["baseline_hz"]
        sl = third_slices(cond_idx)
        for th in THIRDS:
            ti = sl[th]
            on_b, off_b, on_off = [], [], []
            for cid in gids:
                bl = float(bmap.get(cid, np.nan))
                on_b.append(on[ti, cid].mean() - bl)
                off_b.append(off[ti, cid].mean() - bl)
                on_off.append(on[ti, cid].mean() - off[ti, cid].mean())
            for q, v in [("ON_minus_baseline", on_b), ("OFF_minus_baseline", off_b), ("ON_minus_OFF", on_off)]:
                m, lo, hi = boot_ci(np.array(v))
                rows.append(dict(dataset=name, third=th, quantity=q, n_units=len(gids),
                                 mean=round(m, 4), ci_lo=round(lo, 4), ci_hi=round(hi, 4)))
    return pd.DataFrame(rows)


def lfp_adaptation():
    rows = []
    targets = [("dec3", "dHPC", 26, 180), ("dec4", "LEC", 50, 250), ("dec4", "dHPC", 50, 250)]
    cache = {}
    for sess, region, fr, amp in targets:
        cfg = SESSIONS[sess]
        if sess not in cache:
            lfp = np.memmap(cfg["lfp"], dtype="<i2", mode="r",
                            shape=(cfg["lfp"].stat().st_size // 2 // cfg["n_ch"], cfg["n_ch"]))
            tw = pd.read_csv(cfg["trials"])
            cache[sess] = (lfp, tw)
        lfp, tw = cache[sess]
        bad = load_bad(cfg["bad_json"])
        good = np.array([c for c in cfg["regions"][region] if c not in bad])
        first_on = float(tw.on_start_s.min())
        f, Pb, _ = mean_psd(lfp, good, [(START_MARGIN, first_on - GAP)] * 1 +
                            list(zip(tw.on_start_s[:0], tw.on_end_s[:0])))  # baseline ref
        # robust baseline: tile a chunk of baseline
        bw = [(START_MARGIN + i * WIN, START_MARGIN + (i + 1) * WIN) for i in range(120)]
        f, Pb, _ = mean_psd(lfp, good, bw)
        base_bp = band_power(f, Pb, fr - 1.5, fr + 1.5)
        sel = tw[(tw.amplitude == amp) & (tw.freq == fr)].sort_values("trial_number")
        win = list(zip(sel.on_start_s, sel.on_end_s))
        sl = third_slices(np.arange(len(win)))
        for th in THIRDS:
            w = [win[i] for i in sl[th]]
            _, P, _ = mean_psd(lfp, good, w)
            db = 10 * np.log10(band_power(f, P, fr - 1.5, fr + 1.5) / base_bp)
            m, lo, hi = boot_ci(db)
            rows.append(dict(session=sess, region=region, freq=fr, amp=amp, third=th,
                             dB_vs_baseline=round(m, 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3), n_ch=len(good)))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sp = spike_adaptation(); sp.to_csv(OUT / "spike_adaptation_thirds.csv", index=False)
    lf = lfp_adaptation(); lf.to_csv(OUT / "lfp_adaptation_thirds.csv", index=False)
    _fig_spike(sp, OUT); _fig_lfp(lf, OUT)
    print("=== Spike adaptation (amp250_freq50, dB-> Hz vs baseline) ===")
    print(sp.to_string(index=False))
    print("\n=== LFP driven-band adaptation (dB vs baseline) ===")
    print(lf.to_string(index=False))


def _fig_spike(sp, out):
    dsets = sp.dataset.unique()
    quants = ["ON_minus_baseline", "OFF_minus_baseline", "ON_minus_OFF"]
    fig, axes = plt.subplots(1, len(dsets), figsize=(6.2 * len(dsets), 4.8), squeeze=False, sharey=True)
    for ax, ds in zip(axes[0], dsets):
        x = np.arange(len(quants)); w = 0.25
        for i, th in enumerate(THIRDS):
            g = sp[(sp.dataset == ds) & (sp.third == th)].set_index("quantity").reindex(quants)
            ax.bar(x + (i - 1) * w, g["mean"], w, yerr=[g["mean"] - g.ci_lo, g.ci_hi - g["mean"]],
                   capsize=3, color=TC[th], label=th, error_kw=dict(ecolor="#333", lw=1))
        ax.axhline(0, color="black", lw=1)
        ax.set_xticks(x); ax.set_xticklabels(quants, rotation=15, ha="right")
        ax.set_title(f"{ds}: amp250_freq50 by trial-third"); ax.legend(fontsize=8)
    axes[0][0].set_ylabel("firing change (Hz)")
    fig.suptitle("50 Hz single-unit response: early / middle / late (95% bootstrap CI over units)", fontsize=12)
    fig.tight_layout(); fig.savefig(out / "spike_adaptation_50hz.png", dpi=170); plt.close(fig)


def _fig_lfp(lf, out):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    labels = [f"{r.session} {r.region}\n{r.freq}Hz/amp{r.amp}" for _, r in
              lf[["session", "region", "freq", "amp"]].drop_duplicates().iterrows()]
    keys = list(lf[["session", "region", "freq", "amp"]].drop_duplicates().itertuples(index=False))
    x = np.arange(len(keys)); w = 0.25
    for i, th in enumerate(THIRDS):
        vals, lo, hi = [], [], []
        for k in keys:
            g = lf[(lf.session == k.session) & (lf.region == k.region) & (lf.freq == k.freq) & (lf.third == th)]
            vals.append(float(g.dB_vs_baseline.iloc[0])); lo.append(float(g.dB_vs_baseline.iloc[0] - g.ci_lo.iloc[0]))
            hi.append(float(g.ci_hi.iloc[0] - g.dB_vs_baseline.iloc[0]))
        ax.bar(x + (i - 1) * w, vals, w, yerr=[lo, hi], capsize=3, color=TC[th], label=th,
               error_kw=dict(ecolor="#333", lw=1))
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("driven-band power (dB vs baseline)")
    ax.set_title("Driven-band LFP adaptation: early / middle / late (95% bootstrap CI over channels)")
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(out / "lfp_adaptation_driven.png", dpi=170); plt.close(fig)


if __name__ == "__main__":
    main()
