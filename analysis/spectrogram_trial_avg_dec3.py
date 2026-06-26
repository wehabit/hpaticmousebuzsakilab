#!/usr/bin/env python
"""Trial-averaged LFP spectrogram around ON onset (Dec 3), per frequency/amplitude.

This is the Dec 3 counterpart to spectrogram_trial_avg_dec4.py. Dec 3 only has
dHPC and two drive frequencies (5 and 26 Hz), so the figure is arranged as:

  rows = commanded frequency (26 Hz, 5 Hz)
  cols = amplitude (100, 180, 250)

Each panel averages the group-referenced dHPC region-mean LFP across the 200
trials for that condition and expresses power as dB vs the pre-onset baseline.

Outputs -> analysis/outputs/cross_dataset_spike_compare/spectrogram/ and
results/dec3/05_Frequency_Spectral/ via build_results_folder.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import spectrogram

ROOT = Path("/Users/paris/Documents/Buzsakli Lab Github")
FS = 1250.0
PRE, POST = 1.0, 4.0
FMAX = 100.0
LFP = ROOT / "Haptic_Stim_session1_251203_143031/amplifier.lfp"
NCH = 128
TW = ROOT / "analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv"
BAD = ROOT / "analysis/bad_channels_dec3.json"
OUT = ROOT / "analysis/outputs/cross_dataset_spike_compare/spectrogram"
AMPS = [100, 180, 250]
FREQS = [26, 5]


def good_channels() -> np.ndarray:
    bad = set(int(x) for x in json.loads(BAD.read_text()).get("definite_bad_channels", []))
    return np.array([c for c in range(NCH) if c not in bad], dtype=int)


def trial_avg_spec(lfp: np.memmap, good: np.ndarray, onsets: np.ndarray):
    """Average per-trial spectrogram of the group-referenced dHPC mean LFP."""
    pre_n, post_n = int(PRE * FS), int(POST * FS)
    acc = None
    nseg = 0
    f = t = None
    need = pre_n + post_n
    for t0 in onsets:
        s = int(t0 * FS) - pre_n
        if s < 0 or s + need > lfp.shape[0]:
            continue
        seg = np.asarray(lfp[s:s + need, good], dtype=np.float32)
        seg = seg - np.median(seg, axis=1, keepdims=True)
        x = seg.mean(1)
        f, t, Sxx = spectrogram(x, FS, nperseg=625, noverlap=565, scaling="density")
        acc = Sxx if acc is None else acc + Sxx
        nseg += 1
    if acc is None:
        raise RuntimeError("No complete Dec 3 trial segments found for spectrogram.")
    return f, t - PRE, acc / nseg, nseg


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lfp = np.memmap(
        LFP,
        dtype="<i2",
        mode="r",
        shape=(LFP.stat().st_size // 2 // NCH, NCH),
    )
    tw = pd.read_csv(TW)
    good = good_channels()

    fig, axes = plt.subplots(
        len(FREQS),
        len(AMPS),
        figsize=(4.6 * len(AMPS), 4.3 * len(FREQS)),
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )
    im = None
    counts = {}
    for i, freq in enumerate(FREQS):
        for j, amp in enumerate(AMPS):
            ax = axes[i][j]
            onsets = tw[(tw.amplitude == amp) & (tw.freq == freq)].on_start_s.to_numpy()
            f, t, S, nseg = trial_avg_spec(lfp, good, onsets)
            counts[f"amp{amp}_freq{freq}"] = int(nseg)
            fm = f <= FMAX
            base = S[:, t < 0].mean(1, keepdims=True)
            db = 10 * np.log10(S[fm] / base[fm])
            im = ax.pcolormesh(t, f[fm], db, cmap="RdBu_r", vmin=-4, vmax=4, shading="gouraud")
            ax.axvline(0, color="k", lw=1.2)
            ax.axvline(3, color="k", lw=1.2, ls="--")
            ax.axhline(freq, color="#8C1515", lw=1.0, ls=":")
            if freq == 26 and amp == 180:
                ax.annotate(
                    "26 Hz",
                    xy=(1.45, 26),
                    xytext=(1.45, 42),
                    ha="center",
                    va="bottom",
                    color="#8C1515",
                    fontsize=10,
                    weight="bold",
                    arrowprops=dict(arrowstyle="->", color="#8C1515", lw=1.5),
                )
            ax.set_title(f"dHPC freq{freq} / amp{amp}  (n={nseg})")
            if i == len(FREQS) - 1:
                ax.set_xlabel("time from ON onset (s)")
            if j == 0:
                ax.set_ylabel("frequency (Hz)")

    cbar = fig.colorbar(im, ax=axes, shrink=0.85, pad=0.01)
    cbar.set_label("power vs pre-onset (dB)")
    fig.suptitle(
        "Dec 3 trial-averaged dHPC LFP spectrogram around ON onset — all conditions\n"
        "Rows: commanded frequency; columns: amplitude. Dotted line = commanded frequency; black = ON 0-3 s.",
        fontsize=11,
    )
    fig.savefig(OUT / "trial_avg_spectrogram_dec3.png", dpi=170)
    plt.close(fig)
    (OUT / "trial_avg_spectrogram_dec3_summary.json").write_text(
        json.dumps({"good_channels": good.tolist(), "n_trials_used": counts}, indent=2) + "\n"
    )
    print("wrote trial_avg_spectrogram_dec3.png (2x3: freq26/freq5 x amp100/180/250)")


if __name__ == "__main__":
    main()
