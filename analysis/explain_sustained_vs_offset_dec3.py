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
    m = m - np.median(m[t < 0])                            # baseline-subtract -> 0 = baseline level

    def winmean(a, b):
        mask = (t >= a) & (t < b); return float(m[mask].mean())
    sustained = winmean(MARGIN, 3 - MARGIN)
    offset = winmean(3 - MARGIN, 3 + MARGIN)

    fig, ax = plt.subplots(figsize=(13, 6.2))
    # ON / OFF backdrops
    ax.axvspan(0, 3, color="gold", alpha=0.10)
    ax.axvspan(3, 6, color="#3498db", alpha=0.06)
    ax.text(1.5, m.max() * 1.02, "BUZZ ON (3 s)", ha="center", fontsize=10, color="#8a6d00", fontweight="bold")
    ax.text(4.5, m.max() * 1.02, "REST OFF (3 s)", ha="center", fontsize=10, color="#1f6391", fontweight="bold")

    # the two measurement windows
    ax.axvspan(MARGIN, 3 - MARGIN, color="#f1c40f", alpha=0.22)
    ax.axvspan(3 - MARGIN, 3 + MARGIN, color="#c0392b", alpha=0.30)

    ax.plot(t, m, color="#2c3e50", lw=1.3, zorder=5)
    ax.axhline(0, color="black", lw=1.0, ls="--")
    ax.text(-0.95, 2, "baseline level (before any buzz) = 0", fontsize=9, color="#333", va="bottom")

    # sustained level line + label (this is the Y-AXIS measure)
    ax.hlines(sustained, MARGIN, 3 - MARGIN, color="#b8860b", lw=2.2, zorder=6)
    ax.annotate("SUSTAINED window  (0.1-2.9 s, while buzzing)\n"
                "→ this is what the scatter's Y-AXIS measures:\nthe average signal height during the buzz",
                (1.4, sustained), xytext=(0.5, m.max() * 0.60), textcoords="data", fontsize=9.5,
                bbox=dict(boxstyle="round,pad=0.35", fc="#fef9e7", ec="#b8860b"),
                arrowprops=dict(arrowstyle="->", color="#b8860b", lw=1.4))

    # offset surge label (this is the DOT SIZE measure)
    ipk = np.argmin(np.abs(t - 3.0))
    ax.annotate("OFFSET window  (2.9-3.1 s, as the buzz STOPS)\n"
                "→ this is what the scatter's DOT SIZE measures:\n"
                "a brief SURGE UPWARD (signal gets bigger),\nNOT a drop",
                (3.0, m[ipk]), xytext=(3.45, m.max() * 0.82), textcoords="data", fontsize=9.5,
                bbox=dict(boxstyle="round,pad=0.35", fc="#fdecea", ec="#c0392b"),
                arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.6))

    ax.set_xlim(-1, 6); ax.set_ylim(min(0, m.min()) - 5, m.max() * 1.12)
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
