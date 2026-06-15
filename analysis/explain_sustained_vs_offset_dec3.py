#!/usr/bin/env python3
"""Teaching figure: what 'sustained' (y-axis) vs 'offset' (dot size) mean.

Plots the trial-averaged brain signal size (mean |LFP|, baseline-subtracted) across
one ON/OFF trial for the strongest condition, with the exact measurement windows
shaded, so the difference between the two biological-summary measures is visible:
  - SUSTAINED (0.1-2.9 s, while buzzing)         -> the scatter's Y-AXIS
  - OFFSET    (2.9-3.1 s, as the buzz turns off) -> the scatter's DOT SIZE
The offset value is positive -> a transient SURGE at buzz-off, not a drop.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

NCH = 128
BAD = {5, 6, 7, 32, 33, 34, 43, 66, 67}
MARGIN = 0.1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lfp", type=Path, required=True)
    p.add_argument("--sequence", type=Path, required=True)
    p.add_argument("--condition", default="amp180_freq26")
    p.add_argument("--output-dir", type=Path, default=Path("analysis/outputs/dec3/biological_summary"))
    p.add_argument("--fs", type=float, default=1250.0)
    p.add_argument("--max-trials", type=int, default=200)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fs = args.fs
    good = [c for c in range(NCH) if c not in BAD]
    n = args.lfp.stat().st_size // 2 // NCH
    lfp = np.memmap(args.lfp, dtype="<i2", mode="r", shape=(n, NCH))
    seq = pd.read_csv(args.sequence)

    pre, post = 1.0, 6.0
    npre = int(pre * fs); ns = int((pre + post) * fs)
    t = (np.arange(ns) - npre) / fs                       # 0 = buzz ON onset
    rows = seq[seq.condition == args.condition].sort_values("trial_number")
    if len(rows) > args.max_trials:
        rng = np.random.default_rng(321)
        rows = rows.iloc[np.sort(rng.choice(len(rows), args.max_trials, replace=False))]

    acc = np.zeros(ns); k = 0
    for t0 in rows.recording_start_time_s.to_numpy():
        s = int(round(t0 * fs)) - npre
        if s < 0 or s + ns > n:
            continue
        seg = np.asarray(lfp[s:s + ns, good], dtype=np.float32)
        env = np.abs(seg).mean(axis=1)
        acc += env; k += 1
    m = acc / k
    m = m - np.mean(m[t < 0])                              # reference to pre-stim MEAN -> baseline average = exactly 0

    def winmean(a, b):
        mask = (t >= a) & (t < b); return float(m[mask].mean())
    sustained = winmean(MARGIN, 3 - MARGIN)
    offset = winmean(3 - MARGIN, 3 + MARGIN)

    fig, ax = plt.subplots(figsize=(13, 7.4))
    data_lo = min(0.0, float(m.min())); data_hi = float(m.max()) * 1.12
    band = (data_hi - data_lo) * 0.62                 # empty band below the trace for the text boxes
    band_y = data_lo - band * 0.55
    ax.set_xlim(-1, 6); ax.set_ylim(data_lo - band, data_hi)
    lbl_y = data_hi * 0.96

    # PRE / ON / OFF backdrops
    ax.axvspan(-1, 0, color="#9b59b6", alpha=0.07)
    ax.axvspan(0, 3, color="gold", alpha=0.10)
    ax.axvspan(3, 6, color="#3498db", alpha=0.06)
    ax.text(-0.5, lbl_y, "PRE (baseline)", ha="center", fontsize=10, color="#6c3483", fontweight="bold")
    ax.text(1.5, lbl_y, "BUZZ ON (3 s)", ha="center", fontsize=10, color="#8a6d00", fontweight="bold")
    ax.text(4.5, lbl_y, "REST OFF (3 s)", ha="center", fontsize=10, color="#1f6391", fontweight="bold")

    # the two measurement windows
    ax.axvspan(MARGIN, 3 - MARGIN, color="#f1c40f", alpha=0.18)
    ax.axvspan(3 - MARGIN, 3 + MARGIN, color="#c0392b", alpha=0.25)

    ax.plot(t, m, color="#2c3e50", lw=1.3, zorder=5)
    ax.axhline(0, color="black", lw=1.0, ls="--")
    ax.axhline(data_lo, color="#cccccc", lw=0.8)          # divider: trace above, text boxes below

    # average-level lines (these are the values the scatter encodes)
    ax.hlines(sustained, MARGIN, 3 - MARGIN, color="#b8860b", lw=2.4, zorder=6)
    ax.hlines(offset, 3 - MARGIN, 3 + MARGIN, color="#c0392b", lw=3.0, zorder=7)

    # all explanation boxes sit in the band BELOW the trace, arrows pointing up to their lines
    ax.annotate("Baseline = 0\npre-stim average subtracted,\nso all values are relative to rest",
                xy=(-0.5, 0), xytext=(0.0, band_y), ha="center", va="center", fontsize=8.2,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#888"),
                arrowprops=dict(arrowstyle="->", color="#888", lw=1.2))
    ax.annotate("SUSTAINED  (0.1-2.9 s, while buzzing)\n= the scatter's Y-AXIS\ngold line = AVERAGE signal height",
                xy=(1.4, sustained), xytext=(2.6, band_y), ha="center", va="center", fontsize=8.4,
                bbox=dict(boxstyle="round,pad=0.3", fc="#fef9e7", ec="#b8860b"),
                arrowprops=dict(arrowstyle="->", color="#b8860b", lw=1.4))
    ax.annotate("OFFSET  (2.9-3.1 s, as buzz STOPS)\n= the scatter's DOT SIZE\nred line = AVERAGE\n(a SURGE up, not a drop)",
                xy=(3.0, offset), xytext=(4.8, band_y), ha="center", va="center", fontsize=8.4,
                bbox=dict(boxstyle="round,pad=0.3", fc="#fdecea", ec="#c0392b"),
                arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.6))

    ax.set_xlabel("time from buzz onset (s)")
    ax.set_ylabel("brain signal size above baseline\nmean |LFP| - baseline (a.u.)")
    ax.set_title("What the two measures mean: SAME signal size, TWO different time windows  (26 Hz / 180)",
                 fontsize=12.5, fontweight="bold")
    ax.grid(alpha=0.2)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.text(0.5, 0.01,
             "Illustrative trace = mean |LFP| over good channels. The scatter's exact values use group-median referencing, "
             "so absolute a.u. differ — but the shape (a sustained level, then a LARGER offset surge) is the same.",
             ha="center", fontsize=8.5, style="italic", color="#555")
    out = args.output_dir / "sustained_vs_offset_explained.png"
    fig.savefig(out, dpi=160); plt.close(fig)
    print(f"wrote {out}  (n={k} trials; sustained={sustained:.1f}, offset={offset:.1f})")


if __name__ == "__main__":
    main()
