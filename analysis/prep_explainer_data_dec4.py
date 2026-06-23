#!/usr/bin/env python
"""Gather data for the 50 Hz explainer figures (Dec 4).

Computes, reproducibly:
  - 50 Hz ON-OFF envelope BY AMPLITUDE for: dHPC tissue, dHPC dead (121),
    LEC dead, unit-87 channel (181), unit-126 channel (120)
  - unit 87 (LEC) and unit 126 (dHPC) ON/OFF firing rate by amplitude
  - per-unit 50 Hz ON-OFF rate delta (mean over amps) + direction, both regions
Saves analysis/outputs/dec4/artifact_check_50hz/explainer_data.json
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, hilbert

FS = 1250.0
LFP = "Haptic_Stim_session2_251204_131403/amplifier.lfp"
NCH = 256
B, A = butter(4, [45, 55], btype="band", fs=FS)
PAD = int(0.6 * FS)
OUT = Path("analysis/outputs/dec4/artifact_check_50hz")

n = Path(LFP).stat().st_size // 2 // NCH
mm = np.memmap(LFP, dtype="<i2", mode="r", shape=(n, NCH))
tw = pd.read_csv("analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv")
tw50 = tw[tw.freq == 50]
bad = json.load(open("analysis/bad_channels_dec4.json"))
lec_bad = set(bad["port_b_LEC_bad"])
dhpc_good = [c for c in range(0, 128) if c != 121]
lec_dead = [c for c in range(128, 256) if c in lec_bad]


def env_by_amp(chans):
    by = {}
    for r in tw50.itertuples(index=False):
        on_s, on_e = int(r.on_start_s * FS), int(r.on_end_s * FS)
        off_s, off_e = int(r.off_start_s * FS), int(r.off_end_s * FS)
        s, e = max(0, on_s - PAD), min(n, off_e + PAD)
        blk = np.asarray(mm[s:e, chans], dtype=np.float32)
        env = np.abs(hilbert(filtfilt(B, A, blk, axis=0), axis=0))
        d = env[on_s - s:on_e - s].mean(0) - env[off_s - s:off_e - s].mean(0)
        by.setdefault(int(r.amplitude), []).append(float(np.mean(d)))
    return {str(a): round(float(np.mean(v)), 2) for a, v in sorted(by.items())}


data = {"pickup_by_amp": {
    "dHPC_tissue": env_by_amp(dhpc_good),
    "dHPC_dead_121": env_by_amp([121]),
    "LEC_dead": env_by_amp(lec_dead),
    "ch181_unit87": env_by_amp([181]),
    "ch120_unit126": env_by_amp([120]),
}}

# unit rate by amplitude
for reg, cid, f in [("unit87_LEC", 87, "analysis/outputs/cross_dataset_spike_compare/dec4_LEC_unit_condition_stats.csv"),
                    ("unit126_dHPC", 126, "analysis/outputs/cross_dataset_spike_compare/dec4_dHPC_unit_condition_stats.csv")]:
    df = pd.read_csv(f)
    u = df[(df.cluster_id == cid) & (df.condition.str.contains("freq50"))]
    d = {}
    for amp in (100, 180, 250):
        row = u[u.condition == f"amp{amp}_freq50"].iloc[0]
        d[str(amp)] = {"on": round(float(row.mean_on_hz), 2), "off": round(float(row.mean_off_hz), 2)}
    data[reg + "_rate_by_amp"] = d

# per-unit 50Hz delta (mean over amps) + direction, both regions
for reg, f in [("dHPC", "analysis/outputs/cross_dataset_spike_compare/dec4_dHPC_unit_condition_stats.csv"),
               ("LEC", "analysis/outputs/cross_dataset_spike_compare/dec4_LEC_unit_condition_stats.csv")]:
    df = pd.read_csv(f)
    d50 = df[df.condition.str.contains("freq50")]
    per_unit = d50.groupby("cluster_id").agg(delta=("mean_delta_hz", "mean"),
                                             responsive=("responsive_q05_within_unit_set", "max")).reset_index()
    data[reg + "_per_unit_delta"] = [
        {"cluster_id": int(r.cluster_id), "delta": round(float(r.delta), 3), "responsive": bool(r.responsive)}
        for r in per_unit.itertuples(index=False)]

(OUT / "explainer_data.json").write_text(json.dumps(data, indent=2) + "\n")
print(json.dumps(data, indent=2))
