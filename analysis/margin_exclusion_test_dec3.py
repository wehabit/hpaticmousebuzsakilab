#!/usr/bin/env python3
"""Margin-exclusion test (Misi step 9, artifact-aware windows).

For the sustained-window LFP measures we drop a +/-100 ms margin at the START and
END of each 3 s ON window, so onset/offset transients can't leak into the
"sustained" estimate. This figure shows trial-averaged mean|LFP| across the whole
ON window with BOTH cut zones shaded, plus zoomed views (in milliseconds) of the
onset and offset, so it is visible exactly what the +/-100 ms removes -- and that
it is ordinary ongoing signal, not a discarded response.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

NCH = 128
BAD = {5, 6, 7, 32, 33, 34, 43, 66, 67}
MARGIN_MS = 100


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lfp", type=Path, required=True)
    p.add_argument("--sequence", type=Path, required=True)
    p.add_argument("--condition", default="amp180_freq26")
    p.add_argument("--output-dir", type=Path, default=Path("analysis/outputs/dec3/methods"))
    p.add_argument("--fs", type=float, default=1250.0)
    p.add_argument("--max-trials", type=int, default=200)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fs = args.fs
    good = [c for c in range(NCH) if c not in BAD]
    n = args.lfp.stat().st_size // 2 // NCH
    lfp = np.memmap(args.lfp, dtype="<i2", mode="r", shape=(n, NCH))
    seq = pd.read_csv(args.sequence)

    pre, post = 0.6, 3.6
    npre = int(pre * fs); ns = int((pre + post) * fs)
    t_ms = (np.arange(ns) - npre) / fs * 1000.0           # time in ms, 0 = ON onset
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
        seg -= np.median(seg[:npre], axis=0, keepdims=True)
        acc += np.abs(seg).mean(axis=1); k += 1
    m = acc / k
    ON_MS = 3000.0

    def shade_cuts(ax):
        ax.axvspan(-MARGIN_MS, MARGIN_MS, color="#c0392b", alpha=0.25)
        ax.axvspan(ON_MS - MARGIN_MS, ON_MS + MARGIN_MS, color="#c0392b", alpha=0.25)

    fig = plt.figure(figsize=(15, 8))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1.0], hspace=0.35, wspace=0.18)

    # --- top: full ON window, both cuts visible ---
    axt = fig.add_subplot(gs[0, :])
    axt.axvspan(0, ON_MS, color="gold", alpha=0.12, label="3 s ON window")
    axt.plot(t_ms, m, color="#2c3e50", lw=1.1)
    shade_cuts(axt)
    axt.axvline(0, color="k", lw=0.8, ls="--"); axt.axvline(ON_MS, color="k", lw=0.8, ls="--")
    axt.annotate(f"cut first {MARGIN_MS} ms", xy=(0, m.max()), xytext=(250, m.max()),
                 fontsize=9, color="#c0392b", va="top")
    axt.annotate(f"cut last {MARGIN_MS} ms", xy=(ON_MS, m.max()), xytext=(ON_MS - 1150, m.max()),
                 fontsize=9, color="#c0392b", va="top")
    axt.set_xlim(-500, 3500); axt.set_xlabel("time from ON onset (ms)")
    axt.set_ylabel("mean |LFP| over good channels")
    axt.set_title(f"We exclude +/-{MARGIN_MS} ms at the START and END of the 3 s ON window  "
                  f"({args.condition}, n={k} trials)")
    axt.legend(loc="upper right", fontsize=8); axt.grid(alpha=0.2)

    # --- bottom-left: onset zoom (ms) ---
    axo = fig.add_subplot(gs[1, 0])
    axo.plot(t_ms, m, color="#2c3e50", lw=1.3)
    axo.axvspan(-MARGIN_MS, MARGIN_MS, color="#c0392b", alpha=0.25, label=f"excluded +/-{MARGIN_MS} ms")
    axo.axvline(0, color="k", lw=0.8, ls="--")
    axo.set_xlim(-400, 600); axo.set_xlabel("time from ON onset (ms)")
    axo.set_ylabel("mean |LFP|"); axo.set_title("ONSET zoom"); axo.legend(fontsize=8); axo.grid(alpha=0.2)

    # --- bottom-right: offset zoom (ms, relative to offset) ---
    axf = fig.add_subplot(gs[1, 1], sharey=axo)
    axf.plot(t_ms - ON_MS, m, color="#2c3e50", lw=1.3)
    axf.axvspan(-MARGIN_MS, MARGIN_MS, color="#c0392b", alpha=0.25)
    axf.axvline(0, color="k", lw=0.8, ls="--")
    axf.set_xlim(-400, 600); axf.set_xlabel("time from ON offset (ms)")
    axf.set_title("OFFSET zoom"); axf.grid(alpha=0.2)

    fig.suptitle("Margin-exclusion test: what the +/-100 ms cuts remove (it is ordinary ongoing LFP, not a response)",
                 fontweight="bold")
    out = args.output_dir / "margin_exclusion_test.png"
    fig.savefig(out, dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"wrote {out}  (n={k} trials)")


if __name__ == "__main__":
    main()
