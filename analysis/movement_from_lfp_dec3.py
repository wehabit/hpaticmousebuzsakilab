#!/usr/bin/env python3
"""Movement proxy from LFP (buzcode bz_EMGFromLFP idea) for the Dec 3 session.

When the animal moves, muscle activity injects *correlated* high-frequency signal
across spatially-distant channels; when still, those channels are decorrelated.
So the mean pairwise correlation of band-passed (275-500 Hz) LFP across distant
channels, in sliding windows, is a movement/EMG proxy -- the standard substitute
when no accelerometer is saved (which is our case).

Caveat: during stimulation ON the *vibration* also injects correlated high-freq,
so ON-window EMG is contaminated. Read animal movement from the OFF/rest windows.

Outputs (analysis/outputs/dec3/movement/):
  - movement_emg.png            EMG over the session + per-trial OFF-window movement
  - movement_per_trial.csv      trial, condition, emg_on, emg_off, off_ttl_toggles, moving
  - movement_summary.json
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt

DEFAULT_CHANS = [0, 20, 48, 56, 72, 88, 108, 124]   # spread, good channels (2 per 32-ch group)


def compute_emg(lfp, chans, fs, band, win_s):
    X = np.asarray(lfp[:, chans], dtype=np.float32)
    sos = butter(4, list(band), btype="bandpass", fs=fs, output="sos")
    Xf = sosfiltfilt(sos, X, axis=0).astype(np.float32)
    win = int(win_s * fs); nb = Xf.shape[0] // win
    Xf = Xf[:nb * win].reshape(nb, win, len(chans))
    iu = np.triu_indices(len(chans), k=1)
    emg = np.array([np.nanmean(np.corrcoef(Xf[i].T)[iu]) for i in range(nb)])
    tcen = (np.arange(nb) * win + win / 2) / fs
    return tcen, emg


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lfp", type=Path, required=True)
    p.add_argument("--sequence", type=Path, required=True)
    p.add_argument("--edges-csv", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=Path("analysis/outputs/dec3/movement"))
    p.add_argument("--n-channels", type=int, default=128)
    p.add_argument("--lfp-rate-hz", type=float, default=1250.0)
    p.add_argument("--ttl-rate-hz", type=float, default=20000.0)
    p.add_argument("--channels", type=int, nargs="*", default=DEFAULT_CHANS)
    p.add_argument("--band", type=float, nargs=2, default=[275, 500])
    p.add_argument("--win-s", type=float, default=0.5)
    p.add_argument("--baseline", type=float, nargs=2, default=[640, 1540])
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    n = args.lfp.stat().st_size // 2 // args.n_channels
    lfp = np.memmap(args.lfp, dtype="<i2", mode="r", shape=(n, args.n_channels))
    tcen, emg = compute_emg(lfp, args.channels, args.lfp_rate_hz, args.band, args.win_s)

    seq = pd.read_csv(args.sequence).sort_values("trial_number").reset_index(drop=True)
    def win_emg(t0, t1):
        m = (tcen >= t0) & (tcen < t1)
        return float(np.nanmean(emg[m])) if m.any() else np.nan
    seq["emg_on"] = seq.recording_start_time_s.map(lambda t: win_emg(t, t + 3))
    seq["emg_off"] = seq.recording_start_time_s.map(lambda t: win_emg(t + 3, t + 6))

    # validation: stray bit-7 toggles in the OFF window (the user's movement signal)
    edges = pd.read_csv(args.edges_csv)
    trans = np.sort(edges["sample"].to_numpy() / args.ttl_rate_hz)
    seq["off_ttl_toggles"] = seq.recording_start_time_s.map(
        lambda t: int(((trans >= t + 3) & (trans < t + 6)).sum()))

    off = seq["emg_off"].to_numpy()
    med = np.nanmedian(off); mad = np.nanmedian(np.abs(off - med)) * 1.4826
    thr = med + 3 * mad
    seq["moving"] = seq["emg_off"] > thr

    # cross-check: do EMG-flagged movement trials have more stray OFF toggles?
    mv = seq[seq.moving]; still = seq[~seq.moving]
    corr = float(np.corrcoef(seq["emg_off"].fillna(med), seq["off_ttl_toggles"])[0, 1])

    seq[["trial_number", "condition", "emg_on", "emg_off", "off_ttl_toggles", "moving"]].to_csv(
        args.output_dir / "movement_per_trial.csv", index=False)

    # ---- figure ----
    fig, ax = plt.subplots(2, 1, figsize=(15, 8))
    ax[0].plot(tcen / 60, emg, color="#8e44ad", lw=0.5)
    ax[0].axhline(thr, color="#c0392b", ls="--", lw=1, label=f"movement threshold ({thr:.2f})")
    for x0, x1, c, lab in [(640, 1540, "#9b59b6", "baseline"), (1540, 8740, "gold", "stim"),
                           (8740, 10540, "#3498db", "post")]:
        ax[0].axvspan(x0 / 60, x1 / 60, color=c, alpha=0.10)
    ax[0].set_xlabel("time in recording (min)"); ax[0].set_ylabel("movement proxy\n(mean pairwise hi-freq corr)")
    ax[0].set_title("Movement proxy from LFP (EMGFromLFP idea): high = animal moving / correlated muscle activity.\n"
                    f"{int(seq.moving.sum())}/1200 trials flagged as animal-moving in their OFF/rest window.")
    ax[0].legend(loc="upper right", fontsize=8); ax[0].grid(alpha=0.2)

    ax[1].scatter(still["off_ttl_toggles"], still["emg_off"], s=8, color="#7f8c8d", alpha=0.5, label="still")
    ax[1].scatter(mv["off_ttl_toggles"], mv["emg_off"], s=14, color="#c0392b", label="flagged moving")
    ax[1].axhline(thr, color="#c0392b", ls="--", lw=1)
    ax[1].set_xlabel("stray bit-7 toggles in OFF window (your movement signal)")
    ax[1].set_ylabel("OFF-window movement proxy (EMG)")
    ax[1].set_title(f"Validation: LFP movement proxy vs stray sensor toggles in OFF.   correlation r = {corr:.2f}")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(args.output_dir / "movement_emg.png", dpi=150); plt.close(fig)

    summary = {
        "channels": args.channels, "band_hz": args.band, "win_s": args.win_s,
        "emg_baseline": win_emg(*args.baseline), "emg_stim": win_emg(1540, 8740), "emg_post": win_emg(8740, 10540),
        "emg_on_median": float(np.nanmedian(seq.emg_on)), "emg_off_median": float(np.nanmedian(seq.emg_off)),
        "movement_threshold": float(thr), "n_trials_moving": int(seq.moving.sum()),
        "corr_emg_vs_off_toggles": corr,
        "note": "ON-window EMG is contaminated by vibration; movement is read from OFF windows.",
    }
    (args.output_dir / "movement_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
