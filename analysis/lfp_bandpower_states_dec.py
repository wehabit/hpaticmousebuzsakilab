#!/usr/bin/env python
"""LFP band power across STATES: baseline / ON / OFF / post (Dec 3 + Dec 4).

Complements the aperiodic 1/f analysis ([lfp_aperiodic_states_dec.py]) and the
spike state analysis: how does band-limited LFP power change from the true
pre-experiment baseline through ON/OFF to post-study? Bands:

  broadband (1-100 Hz, line-excluded) · theta (6-10) · gamma (30-80)
  driven bands (5/10/26/50 Hz +-1.5) — ON computed from the MATCHED-frequency trials

Each band's power is expressed as **dB change from that channel's own baseline**
(so baseline = 0 dB by construction; cross-channel scale cancels), with percentile
bootstrap 95% CIs over channels. Group-median referenced good channels per region,
same 3 s windows as the spike/aperiodic state analyses.

Outputs -> analysis/outputs/cross_dataset_spike_compare/lfp_bandpower_states/ and
(via the builders) results/dec*/05_Frequency_Spectral/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lfp_aperiodic_states_dec import (mean_psd, tile, sample, load_bad, boot_ci,
                                      SESSIONS, FS_LFP, START_MARGIN, GAP, END_MARGIN, N_WIN, OUT as _A)

OUT = _A.parent / "lfp_bandpower_states"
STATE_COL = {"ON": "#d1495b", "OFF": "#e9c46a", "post": "#457b9d"}
BANDS = {"broadband": (1, 100), "theta": (6, 10), "gamma": (30, 80)}
LINE = [(48, 52), (98, 102)]


def band_power(f, P, lo, hi, exclude=()):
    m = (f >= lo) & (f <= hi)
    for a, b in exclude:
        m &= ~((f >= a) & (f <= b))
    df = f[1] - f[0]
    return P[m].sum(0) * df            # per channel


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for sess, cfg in SESSIONS.items():
        lfp = np.memmap(cfg["lfp"], dtype="<i2", mode="r",
                        shape=(cfg["lfp"].stat().st_size // 2 // cfg["n_ch"], cfg["n_ch"]))
        dur = lfp.shape[0] / FS_LFP
        tw = pd.read_csv(cfg["trials"])
        first_on, last_off = float(tw.on_start_s.min()), float(tw.off_end_s.max())
        freqs = sorted(int(x) for x in tw["freq"].unique())
        base_w = sample(tile(START_MARGIN, first_on - GAP), N_WIN)
        post_w = sample(tile(last_off + GAP, dur - END_MARGIN), N_WIN)
        on_w = sample(list(zip(tw.on_start_s, tw.on_end_s)), N_WIN)
        off_w = sample(list(zip(tw.off_start_s, tw.off_end_s)), N_WIN)
        onf = {fr: sample(list(zip(tw[tw.freq == fr].on_start_s, tw[tw.freq == fr].on_end_s)), N_WIN) for fr in freqs}
        bad = load_bad(cfg["bad_json"])

        for region, rng in cfg["regions"].items():
            good = np.array([c for c in rng if c not in bad])
            # baseline PSD (reference) + general state PSDs
            f, Pb, _ = mean_psd(lfp, good, base_w)
            psd = {"ON": mean_psd(lfp, good, on_w)[1], "OFF": mean_psd(lfp, good, off_w)[1],
                   "post": mean_psd(lfp, good, post_w)[1]}
            # general bands (broadband/theta/gamma), dB vs baseline per channel
            for band, (lo, hi) in BANDS.items():
                excl = LINE if band == "broadband" else ()
                base_bp = band_power(f, Pb, lo, hi, excl)
                for st in ["ON", "OFF", "post"]:
                    db = 10 * np.log10(band_power(f, psd[st], lo, hi, excl) / base_bp)
                    m, clo, chi = boot_ci(db)
                    rows.append(dict(session=sess, region=region, band=band, state=st,
                                     dB=round(m, 3), ci_lo=round(clo, 3), ci_hi=round(chi, 3), n_ch=len(good)))
            # driven bands: ON from matched-freq trials; OFF/post general
            for fr in freqs:
                lo, hi = fr - 1.5, fr + 1.5
                base_bp = band_power(f, Pb, lo, hi)
                fpsd = {"ON": mean_psd(lfp, good, onf[fr])[1], "OFF": psd["OFF"], "post": psd["post"]}
                for st in ["ON", "OFF", "post"]:
                    db = 10 * np.log10(band_power(f, fpsd[st], lo, hi) / base_bp)
                    m, clo, chi = boot_ci(db)
                    rows.append(dict(session=sess, region=region, band=f"driven_{fr}hz", state=st,
                                     dB=round(m, 3), ci_lo=round(clo, 3), ci_hi=round(chi, 3), n_ch=len(good)))
            print(f"{sess} {region}: bands done (n_ch={len(good)})")

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "bandpower_states.csv", index=False)
    (OUT / "bandpower_states.json").write_text(json.dumps(rows, indent=2) + "\n")
    _fig_general(df, OUT)
    _fig_driven(df, OUT)
    print("\n=== LFP band power (dB vs baseline) ===")
    print(df[df.band.isin(BANDS)].to_string(index=False))


def _bars(ax, sub, title):
    sts = ["ON", "OFF", "post"]
    bands = [b for b in sub.band.unique()]
    x = np.arange(len(bands)); w = 0.26
    for i, st in enumerate(sts):
        ms = [sub[(sub.band == b) & (sub.state == st)] for b in bands]
        vals = [float(m.dB.iloc[0]) if len(m) else 0 for m in ms]
        lo = [float(m.dB.iloc[0] - m.ci_lo.iloc[0]) if len(m) else 0 for m in ms]
        hi = [float(m.ci_hi.iloc[0] - m.dB.iloc[0]) if len(m) else 0 for m in ms]
        ax.bar(x + (i - 1) * w, vals, w, yerr=[lo, hi], capsize=3, color=STATE_COL[st],
               label=st, error_kw=dict(ecolor="#333", lw=1))
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(x); ax.set_xticklabels(bands, rotation=20, ha="right")
    ax.set_ylabel("dB vs baseline"); ax.set_title(title); ax.legend(fontsize=8)


def _fig_general(df, out):
    g = df[df.band.isin(BANDS)]
    keys = g[["session", "region"]].drop_duplicates().itertuples(index=False)
    keys = list(keys)
    fig, axes = plt.subplots(1, len(keys), figsize=(5 * len(keys), 4.6), squeeze=False, sharey=True)
    for ax, (sess, region) in zip(axes[0], keys):
        _bars(ax, g[(g.session == sess) & (g.region == region)], f"{sess} {region}")
    fig.suptitle("LFP band power vs true baseline (broadband / theta / gamma; 95% bootstrap CI over channels)",
                 fontsize=11)
    fig.tight_layout(); fig.savefig(out / "bandpower_general_states.png", dpi=170); plt.close(fig)


def _fig_driven(df, out):
    g = df[df.band.str.startswith("driven")]
    keys = list(g[["session", "region"]].drop_duplicates().itertuples(index=False))
    fig, axes = plt.subplots(1, len(keys), figsize=(5 * len(keys), 4.6), squeeze=False, sharey=True)
    for ax, (sess, region) in zip(axes[0], keys):
        _bars(ax, g[(g.session == sess) & (g.region == region)], f"{sess} {region}")
    fig.suptitle("Driven-band LFP power vs baseline (ON = matched-frequency trials; 95% bootstrap CI)\n"
                 "the 50 Hz LEC elevation in ON is the artifact-suspect peak (see DEC4_50HZ_ARTIFACT_CHECK)",
                 fontsize=10.5)
    fig.tight_layout(); fig.savefig(out / "bandpower_driven_states.png", dpi=170); plt.close(fig)


if __name__ == "__main__":
    main()
