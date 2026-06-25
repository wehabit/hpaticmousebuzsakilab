#!/usr/bin/env python
"""UP/DOWN states + slow oscillation in LEC — cortical confirmation (Dec 4).

Vöröslakos's anatomy criterion: "presence of UP/DOWN states and slow oscillations
confirm cortex (LEC)" (just as ripples confirm CA1/dHPC). This detects, in the quiet
pre-experiment baseline:

  * DOWN states  — population-silence periods (the LEC good+MUA population goes
    quiet for >=50 ms), the hallmark of cortical UP/DOWN dynamics;
  * the slow oscillation — a ~0.5-2 Hz rhythm in the LEC LFP and in the population
    rate (DOWN states recur rhythmically);
  * DOWN-triggered LFP average — the characteristic slow-wave deflection.

dHPC is shown alongside as a contrast (hippocampus is not a classic UP/DOWN
structure). Outputs ->
analysis/outputs/cross_dataset_spike_compare/updown/ and (builders)
results/dec4/05_Frequency_Spectral/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt, welch
from scipy.ndimage import gaussian_filter1d

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/Users/paris/Documents/Buzsakli Lab Github")
FS_LFP, FS_SPK = 1250.0, 20_000.0
LFP = ROOT / "Haptic_Stim_session2_251204_131403/amplifier.lfp"
NCH = 256
TW = ROOT / "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv"
BAD = ROOT / "analysis/bad_channels_dec4.json"
OUT = ROOT / "analysis/outputs/cross_dataset_spike_compare/updown"
REG = {"LEC": dict(chans=range(128, 256), curated=ROOT / "analysis/outputs/dec4/curated_merged_lec"),
       "dHPC": dict(chans=range(0, 128), curated=ROOT / "analysis/outputs/dec4/curated_merged_dhpc")}
BINSPK = 0.010                              # 10 ms population-rate bin
DOWN_MIN_MS = 50.0                          # min DOWN duration
START_MARGIN, GAP = 60.0, 30.0


def good_chans(region):
    bad = set(int(x) for x in json.loads(BAD.read_text()).get("definite_bad_channels", []))
    return np.array([c for c in REG[region]["chans"] if c not in bad])


def pop_spikes(curated):
    """All good+MUA spike times (s), for population-silence detection."""
    st = np.load(curated / "spike_times.npy").astype(np.int64) / FS_SPK
    sc = np.load(curated / "spike_clusters.npy").astype(np.int64)
    g = pd.read_csv(curated / "cluster_group.tsv", sep="\t")
    keep = set(g.loc[g.group.isin(["good", "mua"]), "cluster_id"])
    return np.sort(st[np.isin(sc, list(keep))]), len(keep)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lfp = np.memmap(LFP, dtype="<i2", mode="r", shape=(LFP.stat().st_size // 2 // NCH, NCH))
    tw = pd.read_csv(TW)
    b0, b1 = START_MARGIN, float(tw.on_start_s.min()) - GAP        # quiet baseline window
    summary, store = {}, {}

    for region in REG:
        good = good_chans(region)
        # region-mean LFP over baseline
        seg = np.asarray(lfp[int(b0 * FS_LFP):int(b1 * FS_LFP), good], dtype=np.float32)
        seg = seg - np.median(seg, axis=1, keepdims=True)
        x = seg.mean(1)
        sos = butter(3, [0.5, 2.0], btype="band", fs=FS_LFP, output="sos")
        slow = sosfiltfilt(sos, x)

        # population rate (good+MUA) over baseline
        spk, nunit = pop_spikes(REG[region]["curated"])
        spk = spk[(spk >= b0) & (spk < b1)] - b0
        edges = np.arange(0, (b1 - b0) + BINSPK, BINSPK)
        rate = np.histogram(spk, bins=edges)[0] / BINSPK / max(nunit, 1)     # Hz/unit
        rate_s = gaussian_filter1d(rate, sigma=2)                            # ~20 ms smooth
        trate = (edges[:-1] + edges[1:]) / 2

        # DOWN states = population silence (rate below 15% of median) for >= DOWN_MIN_MS
        thr = 0.15 * np.median(rate_s[rate_s > 0]) if (rate_s > 0).any() else 0
        below = rate_s <= thr
        d = np.diff(below.astype(int)); starts = np.where(d == 1)[0] + 1; ends = np.where(d == -1)[0] + 1
        if below[0]:
            starts = np.r_[0, starts]
        if below[-1]:
            ends = np.r_[ends, len(below)]
        downs = [(s, e) for s, e in zip(starts, ends) if (e - s) * BINSPK * 1000 >= DOWN_MIN_MS]
        dur_ms = np.array([(e - s) * BINSPK * 1000 for s, e in downs])
        down_rate = len(downs) / (b1 - b0)                                  # events/s

        # slow-oscillation peak in the LFP PSD (0.2-4 Hz)
        f, P = welch(x, FS_LFP, nperseg=int(20 * FS_LFP))
        band = (f >= 0.3) & (f <= 2.0)
        so_peak = float(f[band][np.argmax(P[band])])

        store[region] = dict(x=x, slow=slow, trate=trate, rate=rate_s, downs=downs, thr=thr)
        summary[region] = dict(n_units_pop=int(nunit), n_down_states=len(downs),
                               down_rate_hz=round(down_rate, 3),
                               median_down_dur_ms=round(float(np.median(dur_ms)) if len(dur_ms) else 0, 1),
                               slow_osc_peak_hz=round(so_peak, 3))
        print(f"{region}: {len(downs)} DOWN states ({down_rate:.2f}/s, "
              f"median {np.median(dur_ms) if len(dur_ms) else 0:.0f} ms); slow-osc peak {so_peak:.2f} Hz")

    (OUT / "updown_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    _fig(store, summary, OUT)


def _fig(store, summary, out):
    fig, axes = plt.subplots(2, 2, figsize=(14, 7))
    for col, region in enumerate(["LEC", "dHPC"]):
        s = store[region]
        # example 8 s baseline segment
        ax = axes[0][col]
        t0 = 100.0; i0, i1 = int(t0 * FS_LFP), int((t0 + 8) * FS_LFP)
        tt = np.arange(i0, i1) / FS_LFP
        ax.plot(tt, s["x"][i0:i1] / 1000, color="#999", lw=0.6, label="LFP")
        ax.plot(tt, s["slow"][i0:i1] / 1000, color="#2E2D29", lw=1.6, label="0.5–2 Hz")
        for ds, de in s["downs"]:
            ts, te = s["trate"][ds], s["trate"][min(de, len(s["trate"]) - 1)]
            if t0 <= ts <= t0 + 8:
                ax.axvspan(ts, te, color="#8C1515", alpha=0.18)
        ax.set_title(f"{region}: baseline LFP + DOWN states (shaded)"); ax.set_xlabel("time (s)")
        ax.set_ylabel("mV"); ax.legend(fontsize=8, loc="upper right")
        # population rate with DOWN threshold
        ax = axes[1][col]
        m = (s["trate"] >= t0) & (s["trate"] <= t0 + 8)
        ax.plot(s["trate"][m], s["rate"][m], color="#007C92", lw=1)
        ax.axhline(s["thr"], color="#8C1515", ls="--", lw=1, label="DOWN threshold")
        for ds, de in s["downs"]:
            ts, te = s["trate"][ds], s["trate"][min(de, len(s["trate"]) - 1)]
            if t0 <= ts <= t0 + 8:
                ax.axvspan(ts, te, color="#8C1515", alpha=0.18)
        sm = summary[region]
        ax.set_title(f"{region}: population rate — {sm['n_down_states']} DOWN states "
                     f"({sm['down_rate_hz']}/s, {sm['median_down_dur_ms']} ms); slow-osc {sm['slow_osc_peak_hz']} Hz")
        ax.set_xlabel("time (s)"); ax.set_ylabel("pop. rate (Hz/unit)"); ax.legend(fontsize=8)
    fig.suptitle("Awake-baseline UP/DOWN test — NO stereotyped cortical UP/DOWN or slow oscillation in EITHER "
                 "region (LEC≈dHPC; needs NREM/anesthesia).\nUP/DOWN cannot confirm LEC=cortex on awake data; "
                 "ripples DO confirm dHPC=CA1 — see DEC_RIPPLE_STATES.md", fontsize=10.5)
    fig.tight_layout(); fig.savefig(out / "lec_updown_states_dec4.png", dpi=170); plt.close(fig)


if __name__ == "__main__":
    main()
