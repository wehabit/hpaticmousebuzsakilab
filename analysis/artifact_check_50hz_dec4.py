#!/usr/bin/env python
"""Dedicated 50 Hz LFP artifact check (Dec 4).

The coordination analysis re-raised the question: is the 50 Hz LFP increase a
genuine *neural* signal, or electrical/mechanical *pickup* from the actuator?
With no recorded stimulus channel we cannot test true entrainment, but four
signatures separate a tissue-local neural 50 Hz from a volume-conducted artifact:

  1. DEAD-CHANNEL PICKUP (decisive). A disconnected / out-of-tissue electrode
     cannot record neural LFP, but it WILL pick up a volume-conducted electrical
     artifact. We compare the 50 Hz ON-vs-OFF rise on QC-good (in-tissue) channels
     vs QC-bad (disconnected/noisy) channels. Comparable rise on dead channels
     => pickup. Rise only on good channels => tissue origin.
  2. HARMONICS. A mechanical/piezo drive at 50 Hz makes sharp lines at 100/150 Hz;
     neural gamma does not. We measure line prominence at 50/100/150 Hz.
  3. CROSS-REGION PHASE LAG. ~0-lag + high coherence between dHPC and LEC 50 Hz =
     one shared signal (volume conduction). A consistent nonzero lag = conduction.
  4. AMPLITUDE SCALING with drive level (amp100/180/250).

Spikes-rate change remains the cleanest neural evidence regardless of this result.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.signal import butter, filtfilt, hilbert, welch
import pandas as pd

FS = 1250.0
LFP = "Haptic_Stim_session2_251204_131403/amplifier.lfp"
NCH = 256
TRIALS = "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv"
OUT = Path("analysis/outputs/dec4/artifact_check_50hz"); OUT.mkdir(parents=True, exist_ok=True)

bad = json.load(open("analysis/bad_channels_dec4.json"))
DHPC_BAD = set(bad["port_a_dHPC_bad"])
LEC_BAD = set(bad["port_b_LEC_bad"])
dhpc_good = [c for c in range(0, 128) if c not in DHPC_BAD]
lec_good = [c for c in range(128, 256) if c not in LEC_BAD]
lec_dead = sorted(LEC_BAD)            # the meaningful "out-of-tissue" pickup probe
dhpc_dead = sorted(DHPC_BAD)

B, A = butter(4, [45, 55], btype="band", fs=FS)
PAD = int(0.6 * FS)


def boot_ci(vals, nb=4000, seed=0):
    rng = np.random.default_rng(seed)
    vals = np.asarray(vals, float); vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return float("nan"), float("nan"), float("nan")
    bs = np.array([rng.choice(vals, len(vals), replace=True).mean() for _ in range(nb)])
    return float(vals.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def line_prominence(f, pxx, f0, half=1.0, bglo=2.0, bghi=6.0):
    """dB prominence of a spectral line at f0 vs neighboring background."""
    peak = pxx[(f >= f0 - half) & (f <= f0 + half)].max()
    bg = np.median(pxx[((f >= f0 - bghi) & (f <= f0 - bglo)) | ((f >= f0 + bglo) & (f <= f0 + bghi))])
    return float(10 * np.log10(peak / bg)), float(peak), float(bg)


def main():
    n = Path(LFP).stat().st_size // 2 // NCH
    mm = np.memmap(LFP, dtype="<i2", mode="r", shape=(n, NCH))
    tw = pd.read_csv(TRIALS)
    tw50 = tw[tw.freq == 50].reset_index(drop=True)
    print(f"LFP {n} samp; {len(tw50)} freq50 trials; good dHPC {len(dhpc_good)} / LEC {len(lec_good)}; "
          f"dead LEC {len(lec_dead)} / dHPC {len(dhpc_dead)}", flush=True)

    env_on = np.zeros(NCH); env_off = np.zeros(NCH); nt = 0
    psd_on_dh, psd_off_dh, psd_on_lec = [], [], []
    fvec = None
    cross = []            # per-trial (amp, ON resultant, ON mean-lag-rad)
    amp_scale = {}        # amp -> list of region-mean 50Hz ON-OFF envelope

    for r in tw50.itertuples(index=False):
        on_s, on_e = int(r.on_start_s * FS), int(r.on_end_s * FS)
        off_s, off_e = int(r.off_start_s * FS), int(r.off_end_s * FS)
        seg_s, seg_e = max(0, on_s - PAD), min(n, off_e + PAD)
        blk = np.asarray(mm[seg_s:seg_e], dtype=np.float32)
        bp = filtfilt(B, A, blk, axis=0)
        env = np.abs(hilbert(bp, axis=0))
        on_i = slice(on_s - seg_s, on_e - seg_s); off_i = slice(off_s - seg_s, off_e - seg_s)
        env_on += env[on_i].mean(0); env_off += env[off_i].mean(0); nt += 1

        dh = blk[:, dhpc_good].mean(1); le = blk[:, lec_good].mean(1)
        nps = min(1024, on_e - on_s)
        f, pon = welch(dh[on_i], fs=FS, nperseg=nps); _, poff = welch(dh[off_i], fs=FS, nperseg=nps)
        _, plon = welch(le[on_i], fs=FS, nperseg=nps)
        fvec = f; psd_on_dh.append(pon); psd_off_dh.append(poff); psd_on_lec.append(plon)

        dh_an = hilbert(filtfilt(B, A, dh)); le_an = hilbert(filtfilt(B, A, le))
        dphi = np.angle(dh_an[on_i]) - np.angle(le_an[on_i])
        z = np.mean(np.exp(1j * dphi))
        cross.append((int(r.amplitude), float(np.abs(z)), float(np.angle(z))))

        dh_env_on = np.abs(dh_an[on_i]).mean(); dh_env_off = np.abs(dh_an[off_i]).mean()
        amp_scale.setdefault(int(r.amplitude), []).append(dh_env_on - dh_env_off)

    env_on /= nt; env_off /= nt
    diff = env_on - env_off                      # per-channel 50Hz ON-OFF rise

    def grp(chs):
        m, lo, hi = boot_ci(diff[chs])
        return {"n_ch": len(chs), "mean_ON_minus_OFF": round(m, 2), "ci": [round(lo, 2), round(hi, 2)],
                "mean_ON": round(float(env_on[chs].mean()), 2), "mean_OFF": round(float(env_off[chs].mean()), 2)}

    res = {"n_trials": nt, "per_channel_50Hz_ON_minus_OFF_envelope": {
        "dHPC_good": grp(dhpc_good), "LEC_good": grp(lec_good),
        "LEC_dead": grp(lec_dead), "dHPC_dead": grp(dhpc_dead)}}
    g = res["per_channel_50Hz_ON_minus_OFF_envelope"]
    pickup_ratio = g["LEC_dead"]["mean_ON_minus_OFF"] / max(1e-9, g["LEC_good"]["mean_ON_minus_OFF"])
    res["dead_vs_good_pickup_ratio_LEC"] = round(float(pickup_ratio), 3)

    # harmonics (mean PSD across trials)
    pon_dh = np.mean(psd_on_dh, 0); poff_dh = np.mean(psd_off_dh, 0)
    harm = {}
    for f0 in (50, 100, 150):
        on_db, on_pk, on_bg = line_prominence(fvec, pon_dh, f0)
        off_db, *_ = line_prominence(fvec, poff_dh, f0)
        harm[f"{f0}Hz"] = {"ON_prominence_dB": round(on_db, 2), "OFF_prominence_dB": round(off_db, 2)}
    res["harmonics_dHPC"] = harm
    res["harmonic_ratio_100_over_50_ON_dB"] = round(harm["100Hz"]["ON_prominence_dB"] - harm["50Hz"]["ON_prominence_dB"], 2)

    # cross-region phase lag (ON)
    cr = np.array(cross)
    res_len = float(cr[:, 1].mean())
    mean_lag = float(np.angle(np.mean(np.exp(1j * cr[:, 2]))))
    res["cross_region_phase_ON"] = {
        "mean_resultant_coherence": round(res_len, 4),
        "mean_lag_rad": round(mean_lag, 4),
        "mean_lag_deg": round(np.degrees(mean_lag), 2),
        "mean_lag_ms": round(np.degrees(mean_lag) / 360 / 50 * 1000, 3)}

    # amplitude scaling
    res["amplitude_scaling_dHPC_50Hz_ON_minus_OFF"] = {
        str(a): round(float(np.mean(v)), 2) for a, v in sorted(amp_scale.items())}

    # verdict heuristic
    pr = res["dead_vs_good_pickup_ratio_LEC"]
    h100 = res["harmonic_ratio_100_over_50_ON_dB"]
    flags = []
    flags.append(("dead-channel pickup", "HIGH (artifact-like)" if pr > 0.5 else
                  "moderate" if pr > 0.2 else "LOW (tissue-like)"))
    flags.append(("100 Hz harmonic", "present (drive-like)" if harm["100Hz"]["ON_prominence_dB"] > 3 else "absent (neural-like)"))
    flags.append(("cross-region lag", "~0 (shared signal)" if abs(res["cross_region_phase_ON"]["mean_lag_deg"]) < 20 else "nonzero (conduction)"))
    res["verdict_flags"] = dict(flags)

    (OUT / "artifact_check_summary.json").write_text(json.dumps(res, indent=2) + "\n")
    np.savez(OUT / "artifact_check_arrays.npz", diff=diff, env_on=env_on, env_off=env_off,
             fvec=fvec, pon_dh=pon_dh, poff_dh=poff_dh, pon_lec=np.mean(psd_on_lec, 0),
             cross=cr, dhpc_good=dhpc_good, lec_good=lec_good, lec_dead=lec_dead)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
