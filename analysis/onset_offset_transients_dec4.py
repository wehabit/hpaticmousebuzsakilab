#!/usr/bin/env python3
"""Are there onset/offset 'clicks' (transition transients), and do they depend on
the buzz frequency? Dec 4, real data.

Best way to see a click: the trial-AVERAGED LFP (an "ERP"). Because it is locked to
stimulus on/off, a true transient survives averaging while the ongoing rhythm
cancels out. We show, per drive frequency (5/10/26/50 Hz, amp250), the trial-
averaged signal across good channels, zoomed on ONSET (t=0) and OFFSET (t=3 s),
for both probes. A sharp deflection at 0 or 3 s = a real onset/offset click.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FREQS = [5, 10, 26, 50]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lfp", type=Path, required=True)
    ap.add_argument("--sequence", type=Path, required=True)
    ap.add_argument("--bad-channels-json", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--amp", type=int, default=250)
    ap.add_argument("--fs", type=float, default=1250.0)
    ap.add_argument("--n-channels", type=int, default=256)
    ap.add_argument("--max-trials", type=int, default=180)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fs = args.fs
    bad = set(json.loads(args.bad_channels_json.read_text())["candidate_bad_channels"])
    probes = {"dHPC": [c for c in range(0, 128) if c not in bad],
              "LEC": [c for c in range(128, 256) if c not in bad]}
    n = args.lfp.stat().st_size // 2 // args.n_channels
    lfp = np.memmap(args.lfp, dtype="<i2", mode="r", shape=(n, args.n_channels))
    seq = pd.read_csv(args.sequence)

    pre, post = 0.6, 3.8
    npre = int(pre * fs); ns = int((pre + post) * fs)
    t = (np.arange(ns) - npre) / fs
    base = t < -0.1

    # erp[probe][freq] = trial-averaged mean-over-good-channels signed LFP (baseline-subtracted)
    erp = {p: {} for p in probes}
    for freq in FREQS:
        cond = f"amp{args.amp}_freq{freq}"
        rows = seq[seq.condition == cond].sort_values("trial_number").iloc[: args.max_trials]
        for pname, good in probes.items():
            acc = None; k = 0
            for r in rows.itertuples(index=False):
                s = int(round(r.recording_start_time_s * fs)) - npre
                if s < 0 or s + ns > n:
                    continue
                seg = np.asarray(lfp[s:s + ns, good], dtype=np.float32)
                seg = seg - np.median(seg, axis=1, keepdims=True)   # common-median ref within probe
                m = seg.mean(1)                                     # mean over good channels (signed)
                m = m - m[base].mean()                              # baseline subtract
                acc = m if acc is None else acc + m; k += 1
            erp[pname][freq] = (acc / k) if k else np.full(ns, np.nan)

    fig, axes = plt.subplots(len(FREQS), 2, figsize=(13, 11), sharex="col")
    onset = (t >= -0.3) & (t <= 0.5)
    offset = (t >= 2.7) & (t <= 3.5)
    for row, freq in enumerate(FREQS):
        for col, (mask, label, t0) in enumerate([(onset, "ONSET", 0.0), (offset, "OFFSET", 3.0)]):
            ax = axes[row, col]
            for pname, color in [("dHPC", "#2F6BBA"), ("LEC", "#C43A31")]:
                ax.plot(t[mask], erp[pname][freq][mask], color=color, lw=1.4, label=pname)
            ax.axvspan(t0 - 0.1, t0 + 0.1, color="red", alpha=0.12)
            ax.axvline(t0, color="k", lw=0.9, ls="--")
            ax.axhline(0, color="gray", lw=0.6)
            ax.grid(alpha=0.2)
            if col == 0:
                ax.set_ylabel(f"amp{args.amp} · {freq} Hz\ntrial-avg LFP")
            if row == 0:
                ax.set_title(f"{label} (shaded = ±100 ms trim)")
                ax.legend(fontsize=8)
            if row == len(FREQS) - 1:
                ax.set_xlabel("time from buzz onset (s)")
    fig.suptitle(f"Dec 4 onset/offset 'clicks' -- AMPLITUDE {args.amp} ONLY (highest drive), "
                 f"trial-averaged over ~{args.max_trials} repeats per frequency\n"
                 "A sharp deflection right on the dashed line = a real click; a flat wiggly line = none.",
                 fontweight="bold", fontsize=12)
    fig.text(0.5, 0.01,
             "Why trial-AVERAGE all ~200 repeats lined up at the on/off moment (dashed line)?\n"
             "Event-locked 'CLAPS' (a click at the same delay every trial) ADD UP and survive;  "
             "random-timing 'HUMS' (ongoing rhythm) CANCEL out.\n"
             "So a bump on the dashed line = a real click;  a flat wiggly line = no click.   "
             "(Sustained 50 Hz has random phase across trials -> it 'hums' and cancels here.)",
             ha="center", va="bottom", fontsize=8.5, style="italic",
             bbox=dict(boxstyle="round", fc="#fff7d6", ec="#e1c542"))
    fig.tight_layout(rect=(0, 0.12, 1, 0.94))
    fig.savefig(args.output_dir / "onset_offset_transients_by_freq.png", dpi=150)
    plt.close(fig)

    # quantify: peak |deflection| in the +/-100 ms window vs baseline std
    out = {}
    for freq in FREQS:
        out[f"freq{freq}"] = {}
        for pname in probes:
            e = erp[pname][freq]
            bstd = float(np.std(e[base]))
            on_pk = float(np.max(np.abs(e[(t >= -0.1) & (t <= 0.1)])))
            off_pk = float(np.max(np.abs(e[(t >= 2.9) & (t <= 3.1)])))
            out[f"freq{freq}"][pname] = {
                "baseline_std": round(bstd, 2),
                "onset_peak": round(on_pk, 2), "onset_peak_over_baseline": round(on_pk / max(bstd, 1e-6), 2),
                "offset_peak": round(off_pk, 2), "offset_peak_over_baseline": round(off_pk / max(bstd, 1e-6), 2),
            }
    (args.output_dir / "onset_offset_transients_summary.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
