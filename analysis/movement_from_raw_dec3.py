#!/usr/bin/env python3
"""Movement proxy from the RAW 20 kHz data (full 300-600 Hz EMG band).

Same idea as bz_EMGFromLFP, but on amplifier.dat (20 kHz) so the muscle band is
real, not anti-aliased like the 1250 Hz LFP. Reads only short per-trial snippets
(OFF/rest windows) rather than the whole 51 GB file. Animal movement = correlated
high-frequency across spatially-distant channels in the OFF window.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt

DEFAULT_CHANS = [0, 20, 48, 56, 72, 88, 108, 124]


def window_emg(raw, chans, sos, iu, start, nsamp):
    seg = np.asarray(raw[start:start + nsamp, chans], dtype=np.float32)
    seg = sosfiltfilt(sos, seg, axis=0)
    c = np.corrcoef(seg.T)
    return float(np.nanmean(c[iu]))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--sequence", type=Path, required=True)
    p.add_argument("--edges-csv", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=Path("analysis/outputs/dec3/movement"))
    p.add_argument("--n-channels", type=int, default=128)
    p.add_argument("--raw-rate-hz", type=float, default=20000.0)
    p.add_argument("--channels", type=int, nargs="*", default=DEFAULT_CHANS)
    p.add_argument("--band", type=float, nargs=2, default=[300, 600])
    p.add_argument("--win-s", type=float, default=3.0)
    p.add_argument("--baseline", type=float, nargs=2, default=[640, 1540])
    p.add_argument("--n-baseline", type=int, default=100)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    fs = args.raw_rate_hz
    n = args.raw.stat().st_size // 2 // args.n_channels
    raw = np.memmap(args.raw, dtype="<i2", mode="r", shape=(n, args.n_channels))
    sos = butter(4, list(args.band), btype="bandpass", fs=fs, output="sos")
    iu = np.triu_indices(len(args.channels), k=1)
    nsamp = int(args.win_s * fs)

    # baseline "still" reference distribution
    bt = np.linspace(args.baseline[0], args.baseline[1] - args.win_s, args.n_baseline)
    base_emg = np.array([window_emg(raw, args.channels, sos, iu, int(t * fs), nsamp) for t in bt])
    bmed = float(np.median(base_emg)); bmad = float(np.median(np.abs(base_emg - bmed)) * 1.4826)
    thr = bmed + 3 * bmad

    seq = pd.read_csv(args.sequence).sort_values("trial_number").reset_index(drop=True)
    off_emg = np.empty(len(seq))
    for i, t in enumerate(seq.recording_start_time_s.to_numpy()):
        s = int((t + 3.0) * fs)                      # OFF window = [on+3, on+6]
        off_emg[i] = window_emg(raw, args.channels, sos, iu, s, nsamp) if s + nsamp <= n else np.nan
        if i % 200 == 0:
            print(f"  trial {i}/{len(seq)}", flush=True)
    seq["emg_off_raw"] = off_emg
    seq["moving"] = seq["emg_off_raw"] > thr

    edges = pd.read_csv(args.edges_csv)
    trans = np.sort(edges["sample"].to_numpy() / 20000.0)
    seq["off_ttl_toggles"] = seq.recording_start_time_s.map(
        lambda t: int(((trans >= t + 3) & (trans < t + 6)).sum()))
    corr = float(np.corrcoef(np.nan_to_num(seq.emg_off_raw, nan=bmed), seq.off_ttl_toggles)[0, 1])

    seq[["trial_number", "condition", "emg_off_raw", "off_ttl_toggles", "moving"]].to_csv(
        args.output_dir / "movement_raw_per_trial.csv", index=False)

    fig, ax = plt.subplots(1, 2, figsize=(15, 5.5))
    ax[0].hist(base_emg, bins=30, color="#7f8c8d", alpha=0.7, label=f"baseline 'still' (n={args.n_baseline})", density=True)
    ax[0].hist(seq.emg_off_raw.dropna(), bins=40, color="#8e44ad", alpha=0.5, label="trial OFF windows", density=True)
    ax[0].axvline(thr, color="#c0392b", ls="--", label=f"movement threshold ({thr:.2f})")
    ax[0].set_xlabel("OFF-window movement proxy (raw 300-600 Hz corr)"); ax[0].set_ylabel("density")
    ax[0].set_title(f"Raw-20kHz EMG: {int(seq.moving.sum())}/1200 OFF windows above 'still' baseline")
    ax[0].legend(fontsize=8)
    still = seq[~seq.moving]; mv = seq[seq.moving]
    ax[1].scatter(still.off_ttl_toggles, still.emg_off_raw, s=8, color="#7f8c8d", alpha=0.5, label="still")
    ax[1].scatter(mv.off_ttl_toggles, mv.emg_off_raw, s=14, color="#c0392b", label="flagged moving")
    ax[1].axhline(thr, color="#c0392b", ls="--")
    ax[1].set_xlabel("stray bit-7 toggles in OFF (your movement signal)")
    ax[1].set_ylabel("OFF-window EMG (raw)")
    ax[1].set_title(f"Validation vs stray toggles:  r = {corr:.2f}")
    ax[1].legend(fontsize=8)
    for a in ax: a.grid(alpha=0.2)
    fig.tight_layout(); fig.savefig(args.output_dir / "movement_raw.png", dpi=150); plt.close(fig)

    summary = {
        "source": "raw 20 kHz", "channels": args.channels, "band_hz": args.band, "win_s": args.win_s,
        "baseline_emg_median": bmed, "baseline_emg_mad": bmad, "movement_threshold": thr,
        "off_emg_median": float(np.nanmedian(off_emg)), "n_trials_moving": int(seq.moving.sum()),
        "corr_emg_vs_off_toggles": corr,
    }
    (args.output_dir / "movement_raw_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
