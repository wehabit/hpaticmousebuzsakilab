#!/usr/bin/env python3
"""Two teaching figures (from real Dec 4 LEC data) explaining the metrics.

FIG 1 — Narrowband peak above 1/f ("residual"): log-log spectrum, the fitted 1/f
line (drive band excluded from the fit), and how far the drive frequency pokes
above the fit. Shows 50 Hz (clear bump) vs 26 Hz (no bump) on the SAME probe.

FIG 2 — ITPC / phase locking: per-trial phase at 50 Hz as a trials x time map, the
ITPC timecourse vs the chance floor and Rayleigh line, and polar phase histograms
across trials (resultant-vector length = ITPC) at onset vs mid-sustained.
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
from scipy.signal import butter, hilbert, sosfiltfilt, welch

GROUP = list(range(192, 256))  # LEC shank B 192-255 (good = 192-223)


def fit_aperiodic(f, P, fmin, fmax, exclude):
    m = (f >= fmin) & (f <= fmax)
    for lo, hi in exclude:
        m &= ~((f >= lo) & (f <= hi))
    lf, lp = np.log10(f[m]), np.log10(P[m])
    slope, offset = np.polyfit(lf, lp, 1)
    lf_all = np.log10(np.where(f > 0, f, np.nan))
    return slope, offset, slope * lf_all + offset


def gather(lfp, n, seq, cond, good, fs, max_trials=150):
    rows = seq[seq.condition == cond].sort_values("trial_number").iloc[:max_trials]
    pre, post = 1.0, 6.0
    npre = int(pre * fs); ns = int((pre + post) * fs)
    t = (np.arange(ns) - npre) / fs
    on = (t >= 0.2) & (t <= 2.8)
    Pacc = None; k = 0
    sig = []  # per-trial group-mean signal (full window)
    for r in rows.itertuples(index=False):
        s = int(round(r.recording_start_time_s * fs)) - npre
        if s < 0 or s + ns > n:
            continue
        seg = np.asarray(lfp[s:s + ns], dtype=np.float32)
        seg = seg - np.median(seg[:, good], axis=1, keepdims=True)
        blk = seg[:, good]
        f, P = welch(blk[on], fs, nperseg=2500, axis=0)
        P = P.mean(1)
        Pacc = P if Pacc is None else Pacc + P; k += 1
        sig.append(blk.mean(1))
    return f, Pacc / k, t, np.asarray(sig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lfp", type=Path, required=True)
    ap.add_argument("--sequence", type=Path, required=True)
    ap.add_argument("--bad-channels-json", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--fs", type=float, default=1250.0)
    ap.add_argument("--n-channels", type=int, default=256)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fs = args.fs
    bad = set(json.loads(args.bad_channels_json.read_text())["candidate_bad_channels"])
    good = [c for c in GROUP if c not in bad]
    n = args.lfp.stat().st_size // 2 // args.n_channels
    lfp = np.memmap(args.lfp, dtype="<i2", mode="r", shape=(n, args.n_channels))
    seq = pd.read_csv(args.sequence)

    f50, P50, t, sig50 = gather(lfp, n, seq, "amp250_freq50", good, fs)
    f26, P26, _, _ = gather(lfp, n, seq, "amp250_freq26", good, fs)

    # ---------- FIGURE 1: residual above 1/f ----------
    def fit_and_res(f, P, drive):
        excl = [(drive - 2, drive + 2), (2 * drive - 2, 2 * drive + 2)]
        s, o, fit = fit_aperiodic(f, P, 3, 120, excl)
        di = int(np.argmin(np.abs(f - drive)))
        return fit, float(np.log10(P[di]) - fit[di]), di

    fit50, res50, di50 = fit_and_res(f50, P50, 50)
    fit26, res26, di26 = fit_and_res(f26, P26, 26)

    fig, ax = plt.subplots(2, 2, figsize=(15, 9))
    for a, (f, P, fit, drive, di, res, title) in zip(
        ax[0],
        [(f50, P50, fit50, 50, di50, res50, "amp250_freq50 — 50 Hz HAS a peak above 1/f"),
         (f26, P26, fit26, 26, di26, res26, "amp250_freq26 — 26 Hz has NO peak above 1/f")]):
        a.loglog(f, P, color="#1c2833", lw=1.6, label="LEC power spectrum")
        a.loglog(f, 10 ** fit, color="#C43A31", ls="--", lw=1.5, label="1/f fit (drive band excluded)")
        a.axvspan(drive - 2, drive + 2, color="gold", alpha=0.25, label="excluded from fit")
        a.loglog(f[di], P[di], "o", color="#27ae60", ms=10)
        a.annotate(f"residual = {res:+.2f}\n(gap above fit)", xy=(f[di], P[di]),
                   xytext=(f[di] * 1.6, P[di] * (3 if res > 0 else 0.3)),
                   arrowprops=dict(arrowstyle="->", color="#27ae60"), color="#27ae60", fontsize=10, fontweight="bold")
        a.set_xlim(2, 200); a.set_xlabel("frequency (Hz)"); a.set_ylabel("power")
        a.set_title(title); a.legend(fontsize=8); a.grid(alpha=0.2, which="both")
    # flattened residual spectra for all 4 freqs (LEC)
    a = ax[1, 0]
    fc = {5: "#2F6BBA", 10: "#54A24B", 26: "#E6A817", 50: "#C43A31"}
    for drive in [5, 10, 26, 50]:
        f, P, _, _ = gather(lfp, n, seq, f"amp250_freq{drive}", good, fs)
        excl = [(drive - 2, drive + 2), (2 * drive - 2, 2 * drive + 2)]
        _, _, fit = fit_aperiodic(f, P, 3, 120, excl)
        a.plot(f, np.log10(P) - fit, color=fc[drive], lw=1.4, label=f"{drive} Hz drive")
        a.axvline(drive, color=fc[drive], ls=":", lw=1)
    a.axhline(0, color="k", lw=0.9); a.axhline(0.05, color="gray", ls="--", lw=1, label="peak threshold 0.05")
    a.set_xlim(2, 70); a.set_ylim(-0.6, 0.8); a.set_xlabel("frequency (Hz)")
    a.set_ylabel("flattened power  log10(P) − 1/f fit")
    a.set_title("Flattened spectra: only the 50 Hz drive pokes above 0 (a real bump)")
    a.legend(fontsize=8); a.grid(alpha=0.2)
    # residual vs amplitude at 50 Hz
    a = ax[1, 1]
    amps = [100, 180, 250]
    rr = []
    for amp in amps:
        f, P, _, _ = gather(lfp, n, seq, f"amp{amp}_freq50", good, fs)
        _, r, _ = fit_and_res(f, P, 50)
        rr.append(r)
    a.bar([str(x) for x in amps], rr, color="#C43A31")
    a.axhline(0.05, color="gray", ls="--", lw=1, label="peak threshold 0.05")
    a.set_title("50 Hz residual grows with drive amplitude"); a.set_xlabel("drive amplitude")
    a.set_ylabel("residual above 1/f"); a.legend(fontsize=8); a.grid(alpha=0.2, axis="y")
    fig.suptitle("FIG 1 — Narrowband peak above 1/f (LEC). A real oscillation = a bump sticking up above the 1/f line.",
                 fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(args.output_dir / "teaching_1f_residual.png", dpi=150); plt.close(fig)

    # ---------- FIGURE 2: ITPC / phase locking ----------
    sos50 = butter(4, [48, 52], btype="bandpass", fs=fs, output="sos")
    sos_low = butter(4, [3, 8], btype="bandpass", fs=fs, output="sos")
    phase50 = np.angle(hilbert(sosfiltfilt(sos50, sig50, axis=1), axis=1))   # (ntr, ns) at 50 Hz
    phaselow = np.angle(hilbert(sosfiltfilt(sos_low, sig50, axis=1), axis=1))  # 3-8 Hz onset-evoked
    ntr = phase50.shape[0]
    itpc50 = np.abs(np.mean(np.exp(1j * phase50), axis=0))
    itpclow = np.abs(np.mean(np.exp(1j * phaselow), axis=0))
    floor = 0.886 / np.sqrt(ntr); rayleigh = np.sqrt(-np.log(0.05) / ntr)
    rng = np.random.default_rng(0)

    fig = plt.figure(figsize=(15, 9.5))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.1])

    # --- top row: calibrate the eye with polar plots ---
    def polar_scatter(ax_, phases, color, title):
        r = float(np.abs(np.mean(np.exp(1j * phases))))
        ang = float(np.angle(np.mean(np.exp(1j * phases))))
        jitter = 1 + 0.04 * rng.standard_normal(len(phases))
        ax_.scatter(phases, jitter, s=8, color=color, alpha=0.5)
        ax_.annotate("", xy=(ang, r), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="-|>", color="#111", lw=3))
        ax_.set_ylim(0, 1.15); ax_.set_yticklabels([]); ax_.set_xticklabels([])
        ax_.set_title(f"{title}\nITPC (arrow length) = {r:.3f}", fontsize=9)

    # reference: simulated strong vs no locking
    ax_ref1 = fig.add_subplot(gs[0, 0], projection="polar")
    polar_scatter(ax_ref1, 0.5 + 0.25 * rng.standard_normal(ntr), "#27ae60",
                  "REFERENCE: strong locking\n(all trials ~same phase)")
    ax_ref2 = fig.add_subplot(gs[0, 1], projection="polar")
    polar_scatter(ax_ref2, rng.uniform(-np.pi, np.pi, ntr), "#7f8c8d",
                  "REFERENCE: no locking\n(phase random across trials)")
    # real: 50 Hz mid-buzz
    idx_sus = int(np.argmin(np.abs(t - 1.5)))
    ax_real = fig.add_subplot(gs[0, 2], projection="polar")
    polar_scatter(ax_real, phase50[:, idx_sus], "#C43A31",
                  "REAL DATA: LEC 50 Hz, mid-buzz\n(this is what we observe)")

    # --- bottom: ITPC timecourses (real positive control vs 50 Hz) ---
    a = fig.add_subplot(gs[1, :])
    a.plot(t, itpclow, color="#2F6BBA", lw=1.7,
           label="ITPC 3–8 Hz (onset-evoked) — POSITIVE CONTROL: real locking exists & is detectable")
    a.plot(t, itpc50, color="#C43A31", lw=1.7, label="ITPC 50 Hz (the drive) — stays near chance during the buzz")
    a.axhline(floor, color="k", ls="--", lw=1.2, label=f"chance floor {floor:.3f}")
    a.axhline(rayleigh, color="#27ae60", lw=1.4, label=f"Rayleigh p<.05 {rayleigh:.3f}")
    a.axvspan(0, 3, color="gold", alpha=0.12); a.axvline(0, color="k", lw=0.8); a.axvline(3, color="k", lw=0.8, ls="--")
    a.set_ylim(0, max(0.4, float(itpclow.max()) * 1.1)); a.set_xlabel("time from onset (s)"); a.set_ylabel("ITPC")
    a.set_title("Same trials, same analysis: the onset-evoked 3–8 Hz response IS phase-locked (blue spikes at t=0);\n"
                "the 50 Hz drive is NOT phase-locked during the buzz (red stays at the floor) -> induced, not entrained")
    a.legend(fontsize=8, loc="upper right"); a.grid(alpha=0.2)
    fig.suptitle("FIG 2 — Phase locking (ITPC). Same 50 Hz power, but is its timing the same on every trial?",
                 fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(args.output_dir / "teaching_itpc.png", dpi=150); plt.close(fig)
    itpc = itpc50

    print(json.dumps({"residual_50": res50, "residual_26": res26, "residual_by_amp_50": rr,
                      "n_trials": int(ntr), "itpc_floor": float(floor), "rayleigh": float(rayleigh),
                      "itpc_onset_max": float(itpc[(t >= -0.05) & (t <= 0.3)].max()),
                      "itpc_sustained_mean": float(itpc[(t >= 0.2) & (t <= 2.8)].mean())}, indent=2))


if __name__ == "__main__":
    main()
