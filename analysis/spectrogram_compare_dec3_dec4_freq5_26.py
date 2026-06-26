#!/usr/bin/env python
"""Matched Dec 3 vs Dec 4 trial-averaged spectrograms for shared 5/26 Hz drives.

Rows:
  - Dec 3 dHPC
  - Dec 4 dHPC
  - Dec 4 LEC

Columns:
  - freq5 amp100/180/250
  - freq26 amp100/180/250

This is a presentation comparison figure: same method, same time/frequency window,
and same color scale as the Dec 3/Dec 4 trial-averaged spectrogram figures.
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
AMPS = [100, 180, 250]
FREQS = [5, 26]
OUT = ROOT / "analysis/outputs/cross_dataset_spike_compare/spectrogram"


DATASETS = [
    {
        "label": "Dec 3 dHPC",
        "lfp": ROOT / "Haptic_Stim_session1_251203_143031/amplifier.lfp",
        "nch": 128,
        "trial_windows": ROOT / "analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv",
        "bad_json": ROOT / "analysis/bad_channels_dec3.json",
        "channels": range(0, 128),
    },
    {
        "label": "Dec 4 dHPC",
        "lfp": ROOT / "Haptic_Stim_session2_251204_131403/amplifier.lfp",
        "nch": 256,
        "trial_windows": ROOT / "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv",
        "bad_json": ROOT / "analysis/bad_channels_dec4.json",
        "channels": range(0, 128),
    },
    {
        "label": "Dec 4 LEC",
        "lfp": ROOT / "Haptic_Stim_session2_251204_131403/amplifier.lfp",
        "nch": 256,
        "trial_windows": ROOT / "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv",
        "bad_json": ROOT / "analysis/bad_channels_dec4.json",
        "channels": range(128, 256),
    },
]


def good_channels(spec: dict) -> np.ndarray:
    bad = set(int(x) for x in json.loads(spec["bad_json"].read_text()).get("definite_bad_channels", []))
    return np.array([c for c in spec["channels"] if int(c) not in bad], dtype=int)


def trial_avg_spec(lfp: np.memmap, good: np.ndarray, onsets: np.ndarray):
    """Average per-trial spectrogram of the group-referenced region-mean LFP."""
    pre_n, post_n = int(PRE * FS), int(POST * FS)
    need = pre_n + post_n
    acc = None
    nseg = 0
    f = t = None
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
        raise RuntimeError("No complete trial segments found.")
    return f, t - PRE, acc / nseg, nseg


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(
        len(DATASETS),
        len(FREQS) * len(AMPS),
        figsize=(3.2 * len(FREQS) * len(AMPS), 3.25 * len(DATASETS)),
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )
    summary = {}
    im = None

    opened = {}
    trials = {}
    goods = {}
    for spec in DATASETS:
        key = spec["label"]
        opened[key] = np.memmap(
            spec["lfp"],
            dtype="<i2",
            mode="r",
            shape=(spec["lfp"].stat().st_size // 2 // spec["nch"], spec["nch"]),
        )
        trials[key] = pd.read_csv(spec["trial_windows"])
        goods[key] = good_channels(spec)
        summary[key] = {"n_good_channels": int(len(goods[key])), "conditions": {}}

    col_labels = [(freq, amp) for freq in FREQS for amp in AMPS]
    for r, spec in enumerate(DATASETS):
        key = spec["label"]
        for c, (freq, amp) in enumerate(col_labels):
            ax = axes[r][c]
            tw = trials[key]
            onsets = tw[(tw.amplitude == amp) & (tw.freq == freq)].on_start_s.to_numpy()
            f, t, S, nseg = trial_avg_spec(opened[key], goods[key], onsets)
            summary[key]["conditions"][f"amp{amp}_freq{freq}"] = int(nseg)
            fm = f <= FMAX
            base = S[:, t < 0].mean(1, keepdims=True)
            db = 10 * np.log10(S[fm] / base[fm])
            im = ax.pcolormesh(t, f[fm], db, cmap="RdBu_r", vmin=-4, vmax=4, shading="gouraud")
            ax.axvline(0, color="k", lw=1.0)
            ax.axvline(3, color="k", lw=1.0, ls="--")
            ax.axhline(freq, color="#8C1515", lw=0.9, ls=":")
            if r == 0:
                ax.set_title(f"{freq} Hz / amp{amp}\n(n={nseg})", fontsize=9)
            if c == 0:
                ax.set_ylabel(f"{key}\nfrequency (Hz)")
            if r == len(DATASETS) - 1:
                ax.set_xlabel("time (s)")

    cbar = fig.colorbar(im, ax=axes, shrink=0.84, pad=0.01)
    cbar.set_label("power vs pre-onset (dB)")
    fig.suptitle(
        "Shared 5 Hz and 26 Hz stimulation: Dec 3 vs Dec 4 trial-averaged LFP spectrograms\n"
        "Same method and color scale; dotted line = commanded frequency; black lines = ON 0-3 s",
        fontsize=12,
    )
    out = OUT / "trial_avg_spectrogram_dec3_dec4_freq5_26.png"
    fig.savefig(out, dpi=170)
    plt.close(fig)
    (OUT / "trial_avg_spectrogram_dec3_dec4_freq5_26_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
