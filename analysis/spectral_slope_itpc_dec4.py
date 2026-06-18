#!/usr/bin/env python3
"""Dec 4 entrainment test: 1/f decomposition + ITPC null floor, per probe x 4 freqs.

Same proven methods as the Dec 3 comprehensive_spectral_phase script
(bz_PowerSpectrumSlope / Cohen 2014 ch. 21.6 & 19), generalised to:
  - the two Dec 4 probes (dHPC Port A vs LEC Port B), using one responsive group
    per probe, and
  - all four driven frequencies 5/10/26/50 Hz.

For each (probe-group, condition) it computes, over <=200 trials:
  - ON-window PSD (Welch) on the group-median-referenced, bad-excluded channels
  - a robust 1/f aperiodic fit (log-log, EXCLUDING the driven band +- 2 Hz and its
    2nd harmonic), then the RESIDUAL = log10(P[driven]) - fit[driven]. residual>0
    means a narrowband peak rises above the 1/f background = a real oscillation;
    residual ~ 0 means the power change is broadband, not an oscillation.
  - inter-trial phase coherence (ITPC) at the driven frequency in the sustained
    window, compared to the analytic finite-n null floor 0.886/sqrt(n) and the
    Rayleigh p<0.05 threshold sqrt(-ln a / n).

Headline question: the LEC probe shows a large amplitude-graded 50 Hz POWER
increase. Is it (a) a real narrowband 50 Hz oscillation (residual>0) and/or
(b) phase-locked to the stimulus (ITPC above floor)? Or is it broadband/induced?
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

from channel_groups_dec4 import ANALYSIS_GROUPS, FREQUENCIES, AMPLITUDES

# One responsive group per probe. dHPC: the Dec 3 responsive cluster (A 0-31).
# LEC: the shank carrying the largest 50 Hz driven-power change (B 192-255).
PROBE_GROUPS = {
    "dHPC (A 0-31)": "A_dHPC_0-31",
    "LEC (B 192-255)": "B_LEC_192-255",
}


def parse_cond(c: str) -> tuple[int, int]:
    return int(c.replace("amp", "").split("_")[0]), int(c.split("freq")[1])


def grp_ref(seg: np.ndarray, groups: dict, bad: set) -> np.ndarray:
    out = seg.copy()
    for ch in groups.values():
        use = [c for c in ch if c not in bad]
        if use:
            out[:, ch] = seg[:, ch] - np.median(seg[:, use], axis=1, keepdims=True)
    return out


def fit_aperiodic(f, P, fmin, fmax, exclude):
    m = (f >= fmin) & (f <= fmax)
    for lo, hi in exclude:
        m &= ~((f >= lo) & (f <= hi))
    lf, lp = np.log10(f[m]), np.log10(P[m])
    slope, offset = np.polyfit(lf, lp, 1)
    lf_all = np.log10(np.where(f > 0, f, np.nan))
    return slope, offset, slope * lf_all + offset


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lfp", type=Path, required=True)
    ap.add_argument("--sequence", type=Path, required=True)
    ap.add_argument("--bad-channels-json", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--fs", type=float, default=1250.0)
    ap.add_argument("--n-channels", type=int, default=256)
    ap.add_argument("--max-trials", type=int, default=200)
    ap.add_argument("--half-bw", type=float, default=1.5)
    ap.add_argument("--n-boot", type=int, default=600)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    fs = args.fs
    bad = set(json.loads(args.bad_channels_json.read_text())["candidate_bad_channels"])
    n = args.lfp.stat().st_size // 2 // args.n_channels
    lfp = np.memmap(args.lfp, dtype="<i2", mode="r", shape=(n, args.n_channels))
    seq = pd.read_csv(args.sequence)
    rng = np.random.default_rng(321)

    pre, post = 1.0, 6.0
    npre = int(pre * fs)
    ns = int((pre + post) * fs)
    t = (np.arange(ns) - npre) / fs
    on_m = (t >= 0.2) & (t <= 2.8)
    off_m = (t >= 3.2) & (t <= 5.7)
    sus_m = (t >= 0.2) & (t <= 2.8)
    nper = int(fs)

    rows_out = []
    for probe_label, group_key in PROBE_GROUPS.items():
        resp_good = [c for c in ANALYSIS_GROUPS[group_key] if c not in bad]
        for freq in FREQUENCIES:
            for amp in AMPLITUDES:
                cond = f"amp{amp}_freq{freq}"
                rows = seq[seq.condition == cond].sort_values("trial_number")
                if len(rows) > args.max_trials:
                    rows = rows.iloc[np.sort(rng.choice(len(rows), args.max_trials, replace=False))]
                sos = butter(4, [max(0.5, freq - args.half_bw), freq + args.half_bw],
                             btype="bandpass", fs=fs, output="sos")
                Pon = Poff = None
                non = 0
                phase_tc = []
                for r in rows.itertuples(index=False):
                    s = int(round(r.recording_start_time_s * fs)) - npre
                    if s < 0 or s + ns > n:
                        continue
                    seg = grp_ref(np.asarray(lfp[s:s + ns], dtype=np.float32), ANALYSIS_GROUPS, bad)
                    blk = seg[:, resp_good]
                    fo, po = welch(blk[on_m], fs, nperseg=min(nper, int(on_m.sum())), axis=0)
                    _, pf = welch(blk[off_m], fs, nperseg=min(nper, int(off_m.sum())), axis=0)
                    po = po.mean(1)
                    pf = pf.mean(1)
                    Pon = po if Pon is None else Pon + po
                    Poff = pf if Poff is None else Poff + pf
                    non += 1
                    gm = blk.mean(1) - np.median(blk[t < 0].mean(1))
                    phase_tc.append(np.angle(hilbert(sosfiltfilt(sos, gm))))
                if non == 0:
                    continue
                Pon /= non
                Poff /= non
                f = fo
                excl = [(freq - 2, freq + 2), (2 * freq - 2, 2 * freq + 2)]
                s_on, o_on, fit_on = fit_aperiodic(f, Pon, 3, 120, excl)
                s_off, o_off, fit_off = fit_aperiodic(f, Poff, 3, 120, excl)
                di = int(np.argmin(np.abs(f - freq)))
                res_on = float(np.log10(Pon[di]) - fit_on[di])
                res_off = float(np.log10(Poff[di]) - fit_off[di])

                A = np.asarray(phase_tc)
                ntr = A.shape[0]

                def itpc_of(idx, A=A):
                    it = np.abs(np.mean(np.exp(1j * A[idx]), axis=0))
                    return float(np.mean(it[sus_m]))

                itpc = itpc_of(np.arange(ntr))
                boot = np.array([itpc_of(rng.integers(0, ntr, ntr)) for _ in range(args.n_boot)])
                floor = 0.886 / np.sqrt(ntr)
                rayleigh = np.sqrt(-np.log(0.05) / ntr)
                rows_out.append(dict(
                    probe=probe_label, group=group_key, condition=cond, amplitude=amp,
                    frequency=freq, n_trials=ntr, n_channels=len(resp_good),
                    slope_on=round(s_on, 4), slope_off=round(s_off, 4),
                    residual_above_1f_on=round(res_on, 4), residual_above_1f_off=round(res_off, 4),
                    itpc=round(itpc, 4), itpc_ci_low=round(float(np.percentile(boot, 2.5)), 4),
                    itpc_ci_high=round(float(np.percentile(boot, 97.5)), 4),
                    itpc_null_floor=round(float(floor), 4),
                    rayleigh_p05=round(float(rayleigh), 4),
                    itpc_above_floor=bool(itpc > floor),
                    peak_above_1f=bool(res_on > 0.05),
                ))
                print(f"{probe_label:18s} {cond:14s} res_on={res_on:+.3f} itpc={itpc:.3f} "
                      f"floor={floor:.3f} {'PEAK' if res_on>0.05 else '   '} "
                      f"{'LOCKED' if itpc>floor else ''}", flush=True)

    df = pd.DataFrame(rows_out)
    df.to_csv(args.output_dir / "spectral_slope_itpc_summary.csv", index=False)

    # ---- Figure: residual-above-1/f and ITPC, per probe x frequency x amplitude ----
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    probes = list(PROBE_GROUPS)
    fcolors = {5: "#2F6BBA", 10: "#54A24B", 26: "#E6A817", 50: "#C43A31"}
    for col, probe in enumerate(probes):
        sub = df[df.probe == probe]
        # top row: residual above 1/f at the driven frequency (oscillation test)
        axr = axes[0, col]
        for freq in FREQUENCIES:
            d = sub[sub.frequency == freq].sort_values("amplitude")
            axr.plot(d.amplitude, d.residual_above_1f_on, marker="o", color=fcolors[freq], label=f"{freq} Hz")
        axr.axhline(0, color="k", lw=0.8)
        axr.axhline(0.05, color="gray", ls=":", lw=1, label="peak threshold")
        axr.set_title(f"{probe}: narrowband peak above 1/f (ON)\n(>0 = real oscillation at driven freq)")
        axr.set_xlabel("amplitude"); axr.set_ylabel("residual log10(P) - 1/f fit"); axr.set_xticks(AMPLITUDES)
        axr.grid(alpha=0.2); axr.legend(fontsize=8)
        # bottom row: ITPC vs null floor
        axi = axes[1, col]
        for freq in FREQUENCIES:
            d = sub[sub.frequency == freq].sort_values("amplitude")
            axi.plot(d.amplitude, d.itpc, marker="o", color=fcolors[freq], label=f"{freq} Hz")
        floor = float(sub.itpc_null_floor.median())
        ray = float(sub.rayleigh_p05.median())
        axi.axhline(floor, color="k", ls="--", lw=1.2, label=f"null floor {floor:.3f}")
        axi.axhline(ray, color="#27ae60", lw=1.4, label=f"Rayleigh p<.05 {ray:.3f}")
        axi.set_title(f"{probe}: ITPC at driven freq vs chance")
        axi.set_xlabel("amplitude"); axi.set_ylabel("sustained ITPC"); axi.set_xticks(AMPLITUDES)
        axi.grid(alpha=0.2); axi.legend(fontsize=8)
    fig.suptitle("Dec 4 entrainment test: is the driven-frequency LFP a real oscillation (peak above 1/f) "
                 "and/or phase-locked (ITPC>floor)?", fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(args.output_dir / "spectral_slope_itpc_dec4.png", dpi=150)
    plt.close(fig)
    print(f"\nWrote {args.output_dir}/spectral_slope_itpc_summary.csv and .png")


if __name__ == "__main__":
    main()
