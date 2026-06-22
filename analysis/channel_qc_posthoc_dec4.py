#!/usr/bin/env python
"""Post-hoc per-channel QC sweep (Dec 4) — hunt for dead/marginal channels that
escaped the original auto RMS pass, and check whether curated good units sit in the
50 Hz pickup zone.

Independent of the original QC: samples 4x60 s windows across the recording,
computes per-channel broadband RMS, 50 Hz power, 60 Hz mains, and flatline fraction,
robust-z within each probe. Reports (1) good channels with extreme RMS, (2) the
Dec-3 'hardware-fixed' dHPC channels' status, (3) good LEC channels with extreme
50 Hz power, (4) peak channels of curated good LEC units vs the pickup zone.

Findings (this session): LEC ch142 hot (RMS z=4.6) -> added to bad list; the deep
half of LEC good channels (173-223) carries the 50 Hz pickup; all 15 good LEC units
peak at 173-214 (none in the clean shallow zone). See DEC4_50HZ_ARTIFACT_CHECK.md.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import welch

LFP = "Haptic_Stim_session2_251204_131403/amplifier.lfp"
NCH = 256
FS = 1250.0


def robz(x, idx):
    v = x[idx]; med = np.median(v); mad = np.median(np.abs(v - med)) + 1e-9
    return (x - med) / (1.4826 * mad)


def main():
    n = Path(LFP).stat().st_size // 2 // NCH
    mm = np.memmap(LFP, dtype="<i2", mode="r", shape=(n, NCH))
    bad = json.load(open("analysis/bad_channels_dec4.json"))
    badset = set(bad["port_a_dHPC_bad"]) | set(bad["port_b_LEC_bad"])

    wins = [int(f * n) for f in (0.15, 0.4, 0.6, 0.85)]
    L = int(60 * FS)
    std = np.zeros(NCH); p50 = np.zeros(NCH); flat = np.zeros(NCH); k = 0
    for s in wins:
        blk = np.asarray(mm[s:s + L], dtype=np.float32); k += 1
        std += blk.std(0)
        f, P = welch(blk, fs=FS, nperseg=2048, axis=0)
        p50 += P[(f >= 48) & (f <= 52)].mean(0)
        flat += (np.abs(np.diff(blk, axis=0)) < 1).mean(0)
    std /= k; p50 /= k; flat /= k

    dh = list(range(0, 128)); le = list(range(128, 256))
    dh_good = [c for c in dh if c not in badset]; le_good = [c for c in le if c not in badset]
    zA = robz(std, dh_good); zB = robz(std, le_good)
    z50 = robz(np.log(p50 + 1e-9), le_good)

    out = {
        "sampled_minutes": round(n / FS / 60, 1),
        "dHPC_good_RMS": {"median": round(float(np.median(std[dh_good])), 0),
                          "min": round(float(std[dh_good].min()), 0), "max": round(float(std[dh_good].max()), 0)},
        "LEC_good_RMS": {"median": round(float(np.median(std[le_good])), 0),
                         "min": round(float(std[le_good].min()), 0), "max": round(float(std[le_good].max()), 0)},
        "good_channels_extreme_RMS_z_gt_4": {
            "dHPC": [(c, round(float(std[c]), 0), round(float(zA[c]), 1)) for c in dh_good if abs(zA[c]) > 4],
            "LEC": [(c, round(float(std[c]), 0), round(float(zB[c]), 1)) for c in le_good if abs(zB[c]) > 4]},
        "dec3_fixed_dhpc_channels": {c: {"std": round(float(std[c]), 0), "z": round(float(zA[c]), 1)}
                                     for c in (5, 6, 7, 32, 33, 34, 43, 66, 67)},
        "good_LEC_channels_extreme_50Hz_z_gt_4": [int(c) for c in le_good if z50[c] > 4],
        "flatlining_good_channels_gt20pct": [int(c) for c in dh_good + le_good if flat[c] > 0.2],
    }

    # curated good LEC unit peak channels vs pickup zone
    try:
        d = "analysis/outputs/dec4/kilosort4_results_lec"
        cg = pd.read_csv("analysis/outputs/dec4/curated_merged_lec/cluster_group.tsv", sep="\t")
        good = cg.loc[cg.group == "good", "cluster_id"].to_numpy()
        tmpl = np.load(f"{d}/templates.npy"); cmap = np.load(f"{d}/channel_map.npy")
        peak = 128 + cmap[np.ptp(tmpl, axis=1).argmax(1)]
        pg = sorted(int(peak[c]) for c in good if c < tmpl.shape[0])
        out["good_LEC_unit_peak_channels"] = pg
        out["good_LEC_units_by_zone"] = {
            "clean_shallow_136_172": int(sum(c < 173 for c in pg)),
            "mid_pickup_173_191": int(sum(173 <= c <= 191 for c in pg)),
            "deep_pickup_192_223": int(sum(192 <= c <= 223 for c in pg))}
    except Exception as e:
        out["good_LEC_unit_peak_channels_error"] = str(e)

    OUT = Path("analysis/outputs/dec4/channel_qc"); OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "posthoc_channel_qc_summary.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
