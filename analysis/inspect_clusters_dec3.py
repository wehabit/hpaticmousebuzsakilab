#!/usr/bin/env python
"""Render Phy-style diagnostics (waveform, autocorrelogram, amplitude-over-time)
for a list of clusters, so each can be judged good/mua/noise from the data.

  python analysis/inspect_clusters_dec3.py --kilosort-dir <dir> --clusters 102 187 173 ...
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FS = 20000.0


def acg(times_s, window=0.05, bin_s=0.001):
    """Symmetric autocorrelogram counts over +/- window."""
    t = np.sort(times_s)
    n = len(t)
    nb = int(round(window / bin_s))
    edges = (np.arange(-nb, nb + 1)) * bin_s
    counts = np.zeros(len(edges) - 1)
    hi = np.searchsorted(t, t + window, side="right")
    for i in range(n):
        d = t[i + 1:hi[i]] - t[i]
        if d.size:
            counts += np.histogram(np.r_[d, -d], bins=edges)[0]
    centers = (edges[:-1] + edges[1:]) / 2 * 1000  # ms
    return centers, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kilosort-dir", type=Path, required=True)
    ap.add_argument("--clusters", type=int, nargs="+", required=True)
    ap.add_argument("--out", type=Path, default=Path("/tmp/cluster_inspect.png"))
    ap.add_argument("--duration-s", type=float, default=10644.4)
    args = ap.parse_args()

    ks = args.kilosort_dir
    st = np.load(ks / "spike_times.npy").astype(np.float64) / FS
    sc = np.load(ks / "spike_clusters.npy").astype(np.int64)
    templates = np.load(ks / "templates.npy", mmap_mode="r")
    amps = np.load(ks / "amplitudes.npy").astype(np.float64)

    cl = args.clusters
    n = len(cl)
    fig, axes = plt.subplots(n, 3, figsize=(12, 2.2 * n))
    if n == 1:
        axes = axes[None, :]
    for r, c in enumerate(cl):
        m = sc == c
        t = st[m]
        a = amps[m]
        tmpl = np.asarray(templates[c])              # (T, C)
        ptp = np.ptp(tmpl, axis=0)
        pk = int(np.argmax(ptp))
        nbrs = np.argsort(ptp)[::-1][:4]             # 4 strongest channels

        # waveform on peak + neighbours
        ax = axes[r, 0]
        for ch in nbrs:
            ax.plot(tmpl[:, ch], lw=1, alpha=0.5 if ch != pk else 1.0,
                    color="k" if ch == pk else "0.6")
        ax.set_title(f"cl {c}: waveform (pk ch idx {pk})", fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])

        # ACG
        ax = axes[r, 1]
        cen, co = acg(t)
        ax.bar(cen, co, width=1.0, color="steelblue")
        ax.axvspan(-2, 2, color="red", alpha=0.15)   # refractory zone
        ax.set_title(f"ACG +/-50ms (refractory shaded)  n={len(t)}", fontsize=9)
        ax.set_xlabel("lag (ms)", fontsize=8)

        # amplitude over time
        ax = axes[r, 2]
        ax.scatter(t, a, s=1, alpha=0.2, color="darkgreen")
        ax.set_xlim(0, args.duration_s)
        ax.set_title(f"amp over time  fr={len(t)/args.duration_s:.2f}Hz", fontsize=9)
        ax.set_xlabel("time (s)", fontsize=8); ax.set_yticks([])

    fig.tight_layout()
    fig.savefig(args.out, dpi=110)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
