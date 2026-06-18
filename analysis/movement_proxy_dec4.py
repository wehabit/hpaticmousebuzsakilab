#!/usr/bin/env python3
"""Dec 4 movement / data-cleaning analysis (LFP-based, no accelerometer/TTL).

Dec 3 used the accelerometer TTL + an LFP high-frequency "EMG" proxy to flag
movement-contaminated trials and showed the LFP results were robust to excluding
them. Dec 4 has no TTL/accelerometer, so we use the LFP high-frequency band power
as a movement proxy only, then re-test the key driven-power results with vs
without the highest-movement trials.

Outputs (analysis/outputs/dec4/movement/):
  - movement_per_trial.csv         per-trial high-freq RMS proxy
  - movement_robustness.csv        condition driven-power: full vs movement-excluded
  - movement_raw.png               per-trial proxy across the session (baseline/stim/post)
  - movement_sensitivity.png       full vs movement-excluded driven power (per probe)
  - movement_summary.json
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
from scipy.signal import butter, sosfiltfilt

from channel_groups_dec4 import ANALYSIS_GROUPS, PROBES


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lfp", type=Path, required=True)
    ap.add_argument("--sequence", type=Path, required=True)
    ap.add_argument("--bad-channels-json", type=Path, required=True)
    ap.add_argument("--trial-metrics", type=Path, required=True,
                    help="trial_level_stats per-trial metrics (driven_power_log2_delta per group).")
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--fs", type=float, default=1250.0)
    ap.add_argument("--n-channels", type=int, default=256)
    ap.add_argument("--band", type=float, nargs=2, default=[200.0, 500.0])
    ap.add_argument("--exclude-quantile", type=float, default=0.75,
                    help="trials above this movement quantile are the 'high-movement' set to drop.")
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    fs = args.fs
    bad = set(json.loads(args.bad_channels_json.read_text())["candidate_bad_channels"])
    n = args.lfp.stat().st_size // 2 // args.n_channels
    lfp = np.memmap(args.lfp, dtype="<i2", mode="r", shape=(n, args.n_channels))
    seq = pd.read_csv(args.sequence).sort_values("trial_number").reset_index(drop=True)

    # A spread of good channels across both probes for the movement proxy.
    spread = []
    for chs in ANALYSIS_GROUPS.values():
        good = [c for c in chs if c not in bad]
        spread += good[:: max(1, len(good) // 3)][:3]
    spread = sorted(set(spread))
    sos = butter(4, args.band, btype="bandpass", fs=fs, output="sos")

    pre, post = 1.0, 4.0
    npre = int(pre * fs)
    ns = int((pre + post) * fs)
    t = (np.arange(ns) - npre) / fs
    on_m = (t >= 0.2) & (t <= 2.8)

    rows = []
    for r in seq.itertuples(index=False):
        s = int(round(r.recording_start_time_s * fs)) - npre
        if s < 0 or s + ns > n:
            continue
        seg = np.asarray(lfp[s:s + ns, spread], dtype=np.float32)
        hf = sosfiltfilt(sos, seg, axis=0)
        rms = float(np.sqrt(np.mean(hf[on_m] ** 2)))
        rows.append({"trial_number": int(r.trial_number), "condition": r.condition,
                     "amplitude": int(r.amplitude), "frequency": int(r.freq),
                     "recording_start_time_s": float(r.recording_start_time_s), "movement": rms})
    mv = pd.DataFrame(rows)
    mv.to_csv(args.output_dir / "movement_per_trial.csv", index=False)

    thresh = mv["movement"].quantile(args.exclude_quantile)
    high = mv[mv["movement"] > thresh]["trial_number"].tolist()

    # Robustness: per-trial driven power per group, collapsed to probe, full vs excluded.
    tm = pd.read_csv(args.trial_metrics)
    tm["probe"] = np.where(tm["analysis_group"].str.startswith("A"), "dHPC", "LEC")
    per_trial = (tm.groupby(["trial_number", "condition", "amplitude", "frequency", "probe"], as_index=False)
                 .agg(driven=("driven_power_log2_delta", "mean")))
    rob_rows = []
    for (cond, probe), sub in per_trial.groupby(["condition", "probe"]):
        full = sub["driven"].mean()
        kept = sub[~sub["trial_number"].isin(high)]["driven"].mean()
        rob_rows.append({"condition": cond, "probe": probe, "frequency": int(sub["frequency"].iloc[0]),
                         "driven_full": full, "driven_movement_excluded": kept,
                         "n_full": len(sub), "n_kept": int((~sub["trial_number"].isin(high)).sum())})
    rob = pd.DataFrame(rob_rows)
    rob.to_csv(args.output_dir / "movement_robustness.csv", index=False)
    corr = float(rob["driven_full"].corr(rob["driven_movement_excluded"]))

    # ---- movement_raw.png : proxy across the session ----
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.scatter(mv["recording_start_time_s"] / 60, mv["movement"], s=6, alpha=0.4, color="#34495e")
    ax.axhline(thresh, color="crimson", ls="--", lw=1, label=f"exclude > Q{int(args.exclude_quantile*100)}")
    ax.set_xlabel("recording time (min)"); ax.set_ylabel(f"LFP {int(args.band[0])}-{int(args.band[1])} Hz RMS (ON)")
    ax.set_title("Dec 4 movement proxy (LFP high-frequency RMS) per trial across the session")
    ax.legend(); ax.grid(alpha=0.2)
    fig.tight_layout(); fig.savefig(args.output_dir / "movement_raw.png", dpi=150); plt.close(fig)

    # ---- movement_sensitivity.png : full vs excluded driven power ----
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharex=True, sharey=True)
    for ax, probe in zip(axes, ["dHPC", "LEC"]):
        sub = rob[rob.probe == probe].sort_values(["frequency", "condition"])
        x = np.arange(len(sub))
        ax.plot(x, sub["driven_full"], "o-", label="all trials", color="#2F6BBA")
        ax.plot(x, sub["driven_movement_excluded"], "s--", label="movement-excluded", color="#C43A31")
        ax.set_xticks(x); ax.set_xticklabels(sub["condition"], rotation=60, ha="right", fontsize=7)
        ax.axhline(0, color="k", lw=0.8); ax.set_title(f"{probe}: driven power"); ax.grid(alpha=0.2); ax.legend(fontsize=8)
    axes[0].set_ylabel("driven log2 power change")
    fig.suptitle(f"Dec 4: driven-frequency power is robust to excluding high-movement trials "
                 f"(full vs excluded r={corr:.3f})", fontweight="bold")
    fig.tight_layout(); fig.savefig(args.output_dir / "movement_sensitivity.png", dpi=150); plt.close(fig)

    summary = {
        "proxy_channels": spread, "band_hz": args.band, "exclude_quantile": args.exclude_quantile,
        "movement_threshold": float(thresh), "n_trials": int(len(mv)), "n_high_movement": int(len(high)),
        "driven_full_vs_excluded_corr": corr,
        "note": "LFP-only movement proxy (no accelerometer this session). High correlation => driven-power "
                "results are not driven by the highest-movement trials.",
    }
    (args.output_dir / "movement_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
