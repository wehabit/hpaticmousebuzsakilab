#!/usr/bin/env python3
"""Per-trial bootstrap 95% CIs for the per-channel broadband metric.

Reproduces the artifact_aware_lfp broadband definition (per channel: mean |LFP|
in a window minus mean |LFP| in the pre window, averaged over good channels) but
keeps it PER TRIAL, so we can bootstrap a 95% CI across trials for each condition.
Same scale as condition_fingerprint's Sustained/Offset broadband bars.

Windows (artifact margin 0.1 s):  pre = [-1,0],  sustained = [0.1,2.9],  offset = [2.9,3.1].
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np, pandas as pd

NCH = 128
BAD = {5, 6, 7, 32, 33, 34, 43, 66, 67}
COND_ORDER = ["amp100_freq5", "amp180_freq5", "amp250_freq5",
              "amp100_freq26", "amp180_freq26", "amp250_freq26"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lfp", type=Path, required=True)
    p.add_argument("--sequence", type=Path, required=True)
    p.add_argument("--output", type=Path,
                   default=Path("analysis/outputs/dec3/biological_summary/broadband_perchannel_ci.csv"))
    p.add_argument("--fs", type=float, default=1250.0)
    p.add_argument("--n-boot", type=int, default=2000)
    args = p.parse_args()
    fs = args.fs
    good = [c for c in range(NCH) if c not in BAD]
    n = args.lfp.stat().st_size // 2 // NCH
    lfp = np.memmap(args.lfp, dtype="<i2", mode="r", shape=(n, NCH))
    seq = pd.read_csv(args.sequence)
    rng = np.random.default_rng(321)

    pre, post = 1.0, 3.3
    npre = int(pre * fs); ns = int((pre + post) * fs); t = (np.arange(ns) - npre) / fs
    pre_m = t < 0
    sus_m = (t >= 0.1) & (t < 2.9)
    off_m = (t >= 2.9) & (t < 3.1)

    rows = []
    for cond in COND_ORDER:
        sub = seq[seq.condition == cond].sort_values("trial_number")
        sus_vals, off_vals = [], []
        for t0 in sub.recording_start_time_s.to_numpy():
            s = int(round(t0 * fs)) - npre
            if s < 0 or s + ns > n:
                continue
            a = np.abs(np.asarray(lfp[s:s + ns, good], dtype=np.float32))
            pre_lvl = a[pre_m].mean(axis=0)
            sus_vals.append(float((a[sus_m].mean(axis=0) - pre_lvl).mean()))
            off_vals.append(float((a[off_m].mean(axis=0) - pre_lvl).mean()))
        sus_arr = np.array(sus_vals); off_arr = np.array(off_vals); ntr = len(sus_arr)

        def boot_ci(arr):
            idx = rng.integers(0, len(arr), size=(args.n_boot, len(arr)))
            means = arr[idx].mean(axis=1)
            return float(arr.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))

        sm, slo, shi = boot_ci(sus_arr)
        om, olo, ohi = boot_ci(off_arr)
        rows.append(dict(condition=cond, n_trials=ntr,
                         sustained_mean=sm, sustained_ci_low=slo, sustained_ci_high=shi,
                         offset_mean=om, offset_ci_low=olo, offset_ci_high=ohi))
        print(f"{cond}: n={ntr}  sustained={sm:.1f} [{slo:.1f},{shi:.1f}]  offset={om:.1f} [{olo:.1f},{ohi:.1f}]")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    print("wrote", args.output)


if __name__ == "__main__":
    main()
