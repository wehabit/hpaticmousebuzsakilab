#!/usr/bin/env python
"""Trial-averaged LFP spectrogram around ON onset (Dec 4), per amplitude.

Misi's request: a trial-averaged spectrogram (1-100 Hz) to show the 50 Hz response
directly and clarify amplitude effects. The 60 Hz line is minimal in this figure
(checked separately: ~0.99-1.05x neighboring bins), so the 1-100 Hz version is kept
rather than cropping to 1-40 Hz. We align the region-mean LFP (group-referenced
good channels) to ON onset, compute a per-trial spectrogram, average across the 200
trials, and express power as dB vs the pre-onset baseline. Shown for LEC freq50 at
amp100/180/250 (the artifact-suspect 50 Hz band) and dHPC freq50/amp250 (contrast).

Outputs -> analysis/outputs/cross_dataset_spike_compare/spectrogram/ and (builders)
results/dec4/05_Frequency_Spectral/.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import spectrogram

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/Users/paris/Documents/Buzsakli Lab Github")
FS = 1250.0
PRE, POST = 1.0, 4.0
FMAX = 100.0
LFP = ROOT / "Haptic_Stim_session2_251204_131403/amplifier.lfp"
NCH = 256
TW = ROOT / "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv"
BAD = ROOT / "analysis/bad_channels_dec4.json"
OUT = ROOT / "analysis/outputs/cross_dataset_spike_compare/spectrogram"
REGIONS = {"dHPC": range(0, 128), "LEC": range(128, 256)}


def good_channels(region):
    import json
    bad = set(int(x) for x in json.loads(BAD.read_text()).get("definite_bad_channels", []))
    return np.array([c for c in REGIONS[region] if c not in bad])


def trial_avg_spec(lfp, good, onsets):
    """Average per-trial spectrogram of the group-referenced region-mean LFP."""
    pre_n, post_n = int(PRE * FS), int(POST * FS)
    acc = None; nseg = 0
    f = t = None
    for t0 in onsets:
        s = int(t0 * FS) - pre_n
        seg = np.asarray(lfp[s:s + pre_n + post_n, good], dtype=np.float32)
        if seg.shape[0] < pre_n + post_n:
            continue
        seg = seg - np.median(seg, axis=1, keepdims=True)     # group-median ref
        x = seg.mean(1)                                        # region-mean
        f, t, Sxx = spectrogram(x, FS, nperseg=625, noverlap=565, scaling="density")
        acc = Sxx if acc is None else acc + Sxx
        nseg += 1
    return f, t - PRE, acc / max(nseg, 1)                       # t relative to onset


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    lfp = np.memmap(LFP, dtype="<i2", mode="r",
                    shape=(LFP.stat().st_size // 2 // NCH, NCH))
    tw = pd.read_csv(TW)

    # full matrix: rows = region (LEC top, dHPC bottom), cols = amplitude (100/180/250)
    regions, amps = ["LEC", "dHPC"], [100, 180, 250]
    fig, axes = plt.subplots(len(regions), len(amps), figsize=(4.6 * len(amps), 4.3 * len(regions)),
                             sharex=True, sharey=True, constrained_layout=True)
    im = None
    for i, reg in enumerate(regions):
        good = good_channels(reg)
        for j, amp in enumerate(amps):
            ax = axes[i][j]
            onsets = tw[(tw.amplitude == amp) & (tw.freq == 50)].on_start_s.to_numpy()
            f, t, S = trial_avg_spec(lfp, good, onsets)
            fm = f <= FMAX
            base = S[:, t < 0].mean(1, keepdims=True)          # pre-onset baseline per freq
            db = 10 * np.log10(S[fm] / base[fm])
            im = ax.pcolormesh(t, f[fm], db, cmap="RdBu_r", vmin=-4, vmax=4, shading="gouraud")
            ax.axvline(0, color="k", lw=1.2); ax.axvline(3, color="k", lw=1.2, ls="--")
            ax.axhline(50, color="#175E54", lw=1.0, ls=":")
            if reg == "LEC" and amp == 250:
                ax.annotate("50 Hz", xy=(1.5, 50), xytext=(1.5, 68), ha="center", va="bottom",
                            color="#175E54", fontsize=10, weight="bold",
                            arrowprops=dict(arrowstyle="->", color="#175E54", lw=1.5))
            ax.set_title(f"{reg} freq50 / amp{amp}  (n={len(onsets)})")
            if i == len(regions) - 1:
                ax.set_xlabel("time from ON onset (s)")
            if j == 0:
                ax.set_ylabel("frequency (Hz)")
    cbar = fig.colorbar(im, ax=axes, shrink=0.85, pad=0.01); cbar.set_label("power vs pre-onset (dB)")
    fig.suptitle("Trial-averaged LFP spectrogram around ON onset — all amplitudes\n"
                 "LEC 50 Hz band grows with amplitude (top row); dHPC shows no 50 Hz band, only broadband "
                 "suppression (bottom row)   (50 Hz = dotted · black = ON 0–3 s)", fontsize=11)
    fig.savefig(OUT / "trial_avg_spectrogram_dec4.png", dpi=170); plt.close(fig)
    print("wrote trial_avg_spectrogram_dec4.png (2x3: LEC/dHPC x amp100/180/250)")


if __name__ == "__main__":
    main()
