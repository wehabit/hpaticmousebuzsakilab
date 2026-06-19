#!/usr/bin/env python
"""Do dHPC and LEC 'work together' at 50 Hz? Spike-field + cross-region coherence.

Tests, during 50 Hz ON windows vs the matched OFF windows:
  (1) within-region spike-field locking   -- do a region's spikes lock to its own
      50 Hz LFP phase? (the region is internally organized at 50 Hz)
  (2) cross-region spike-field locking     -- do LEC spikes lock to dHPC's 50 Hz
      phase, and vice versa? (direct cross-region coordination; robust to artifact
      because sorted spikes won't lock to a pure LFP artifact)
  (3) cross-region LFP-LFP 50 Hz coherence -- do the two regions' oscillations
      phase-couple? (coordination, but could be inflated by shared artifact)
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.signal import butter, filtfilt, hilbert

FS = 1250.0
SPK_FS = 20000.0
LFP = "Haptic_Stim_session2_251204_131403/amplifier.lfp"
NCH = 256
TRIALS = "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv"
OUT = Path("analysis/outputs/dec4/coordination_50hz"); OUT.mkdir(parents=True, exist_ok=True)
DHPC_BAD = {121}
LEC_BAD = set(json.load(open("analysis/bad_channels_dec4.json"))["port_b_LEC_bad"])


def region_phase(sig):
    b, a = butter(4, [45, 55], btype="band", fs=FS)
    analytic = hilbert(filtfilt(b, a, sig))
    return np.angle(analytic)


def plv(phases):
    if len(phases) < 2:
        return np.nan, np.nan
    R = np.abs(np.mean(np.exp(1j * phases)))
    Z = len(phases) * R * R
    p = np.exp(-Z) * (1 + (2 * Z - Z * Z) / (4 * len(phases)))  # Rayleigh
    return float(R), float(min(max(p, 0), 1))


def spikes_in_mask(t_s, mask):
    idx = np.round(t_s * FS).astype(np.int64)
    ok = (idx >= 0) & (idx < len(mask))
    idx = idx[ok]
    return idx[mask[idx]]


def main():
    import pandas as pd
    n = Path(LFP).stat().st_size // 2 // NCH
    mm = np.memmap(LFP, dtype="<i2", mode="r", shape=(n, NCH))
    dhpc_ch = [c for c in range(0, 128) if c not in DHPC_BAD]
    lec_ch = [c for c in range(128, 256) if c not in LEC_BAD]
    print(f"LFP {n} samples; dHPC {len(dhpc_ch)} ch, LEC {len(lec_ch)} ch", flush=True)

    dhpc = np.empty(n, np.float32); lec = np.empty(n, np.float32)
    chunk = 2_000_000
    for s in range(0, n, chunk):
        e = min(s + chunk, n)
        blk = np.asarray(mm[s:e], dtype=np.float32)
        dhpc[s:e] = blk[:, dhpc_ch].mean(1); lec[s:e] = blk[:, lec_ch].mean(1)
    print("region means done; filtering + hilbert...", flush=True)
    ph_dhpc = region_phase(dhpc); ph_lec = region_phase(lec)

    tw = pd.read_csv(TRIALS); tw50 = tw[tw.freq == 50]
    on_mask = np.zeros(n, bool); off_mask = np.zeros(n, bool)
    for r in tw50.itertuples(index=False):
        on_mask[int(r.on_start_s * FS):int(r.on_end_s * FS)] = True
        off_mask[int(r.off_start_s * FS):int(r.off_end_s * FS)] = True
    print(f"freq50 trials: {len(tw50)}; ON samples {on_mask.sum()}, OFF {off_mask.sum()}", flush=True)

    def good_ids(probe):
        g = pd.read_csv(f"analysis/outputs/dec4/curated_merged_{probe}/cluster_group.tsv", sep="\t")
        return g.loc[g.group == "good", "cluster_id"].to_numpy(int)

    def load_spikes(probe):
        d = f"analysis/outputs/dec4/kilosort4_results_{probe}"
        st = np.load(f"{d}/spike_times.npy").astype(np.float64) / SPK_FS
        sc = np.load(f"{d}/spike_clusters.npy").astype(np.int64)
        return st, sc

    res = {}
    spk = {"dhpc": load_spikes("dhpc"), "lec": load_spikes("lec")}
    gids = {"dhpc": good_ids("dhpc"), "lec": good_ids("lec")}

    # (1)&(2) spike-field locking: region spikes vs each region's phase, ON & OFF.
    for spk_region in ["dhpc", "lec"]:
        st, sc = spk[spk_region]
        for field_region, ph in [("dhpc", ph_dhpc), ("lec", ph_lec)]:
            for win, mask in [("ON", on_mask), ("OFF", off_mask)]:
                per_unit_R, per_unit_sig = [], 0
                pooled = []
                for cid in gids[spk_region]:
                    t = st[sc == cid]
                    idx = spikes_in_mask(t, mask)
                    if len(idx) >= 30:
                        R, p = plv(ph[idx])
                        per_unit_R.append(R); pooled.append(ph[idx])
                        if p < 0.05:
                            per_unit_sig += 1
                pooledR, pooledp = plv(np.concatenate(pooled)) if pooled else (np.nan, np.nan)
                kind = "within" if spk_region == field_region else "cross"
                res[f"{kind}:{spk_region}_spikes_x_{field_region}_phase:{win}"] = {
                    "n_units_tested": len(per_unit_R),
                    "n_units_sig_p05": per_unit_sig,
                    "mean_unit_PLV": round(float(np.nanmean(per_unit_R)), 4) if per_unit_R else None,
                    "pooled_PLV": round(pooledR, 4) if np.isfinite(pooledR) else None,
                    "per_unit_PLV": [round(float(x), 5) for x in per_unit_R],  # for bootstrap CI over units
                }

    # (3) cross-region LFP-LFP 50 Hz coherence, computed PER TRIAL (for a trial-bootstrap CI).
    dphi = ph_dhpc - ph_lec
    min_samp = int(3 * FS / 50)  # >=3 cycles
    for win, (c0, c1) in [("ON", ("on_start_s", "on_end_s")), ("OFF", ("off_start_s", "off_end_s"))]:
        per_trial = []
        for r in tw50.itertuples(index=False):
            s, e = int(getattr(r, c0) * FS), int(getattr(r, c1) * FS)
            if e - s >= min_samp:
                per_trial.append(float(np.abs(np.mean(np.exp(1j * dphi[s:e])))))
        per_trial = np.asarray(per_trial)
        cyc = (3 * FS) / (FS / 50.0)  # ~150 cycles per 3 s trial
        res[f"LFP_coherence_dHPC_LEC_50Hz:{win}"] = {
            "mean_per_trial": round(float(per_trial.mean()), 4),
            "chance_floor_per_trial": round(float(np.sqrt(np.pi) / (2 * np.sqrt(cyc))), 4),
            "per_trial_coherence": [round(float(x), 4) for x in per_trial],
        }

    (OUT / "coordination_summary.json").write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
