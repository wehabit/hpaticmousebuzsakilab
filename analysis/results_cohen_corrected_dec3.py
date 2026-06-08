#!/usr/bin/env python3
"""Resource-corrected result figures (Cohen 2014).

A) ITPC (phase locking) aligned to the MEASURED vibration onset vs the command
   grid -- Cohen 19.5 (temporal jitter suppresses ITPC). Tests whether the weak
   26 Hz phase locking is partly an alignment artifact.
B) Broadband response as RMS / band POWER instead of mean(|LFP|) -- Cohen ch. 18
   (use power, not amplitude-of-deviation), with the within-trial OFF control.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import butter, hilbert, sosfiltfilt

GROUPS = {"G96-127": list(range(96, 128)), "G64-95": list(range(64, 96)),
          "G32-63": list(range(32, 64)), "G0-31": list(range(0, 32))}
COND = ["amp250_freq26", "amp180_freq26", "amp100_freq26", "amp250_freq5", "amp180_freq5", "amp100_freq5"]
COL = {"amp250_freq26": "#7b241c", "amp180_freq26": "#c0392b", "amp100_freq26": "#e6776d",
       "amp250_freq5": "#1a5276", "amp180_freq5": "#2e86c1", "amp100_freq5": "#85c1e9"}
BAD = {5, 6, 7, 32, 33, 34, 43, 66, 67}


def parse_cond(c): return int(c.replace("amp", "").split("_")[0]), int(c.split("freq")[1])


def grp_ref(seg, excl):  # analysis-group median reference
    out = seg.copy()
    for ch in GROUPS.values():
        use = [c for c in ch if c not in excl]
        out[:, ch] = seg[:, ch] - np.median(seg[:, use], axis=1, keepdims=True)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lfp", type=Path, required=True)
    p.add_argument("--sequence", type=Path, required=True)
    p.add_argument("--alignment", type=Path, required=True, help="ttl_onset_offset_alignment.csv (onset_ms per trial)")
    p.add_argument("--output-dir", type=Path, default=Path("analysis/outputs/dec3/cohen_corrected"))
    p.add_argument("--fs", type=float, default=1250.0)
    p.add_argument("--n-channels", type=int, default=128)
    p.add_argument("--max-trials", type=int, default=150)
    p.add_argument("--half-bw", type=float, default=1.5)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fs = args.fs
    n = args.lfp.stat().st_size // 2 // args.n_channels
    lfp = np.memmap(args.lfp, dtype="<i2", mode="r", shape=(n, args.n_channels))
    seq = pd.read_csv(args.sequence)
    al = pd.read_csv(args.alignment)[["trial", "onset_ms", "has_blip"]].rename(columns={"trial": "trial_number"})
    seq = seq.merge(al, on="trial_number", how="left")
    rng = np.random.default_rng(321)
    pre, post = 1.0, 4.0
    npre, npost = int(pre * fs), int(post * fs); ns = npre + npost
    t = (np.arange(ns) - npre) / fs
    pre_m, sus_m = t < 0, (t >= 0.2) & (t <= 2.8)
    on_m, off_m = (t >= 0.1) & (t < 2.9), (t >= 3.1) & (t < 3.9)  # for RMS within-trial control

    itpc_grid, itpc_onset, rms_on, rms_off = {}, {}, {}, {}
    tc_grid, tc_onset = {}, {}  # timecourse for the figure (mean over groups)
    for cond in COND:
        amp, fr = parse_cond(cond)
        rows = seq[seq.condition == cond].sort_values("trial_number")
        if len(rows) > args.max_trials:
            rows = rows.iloc[np.sort(rng.choice(len(rows), args.max_trials, replace=False))]
        sos = butter(4, [max(0.5, fr - args.half_bw), fr + args.half_bw], btype="bandpass", fs=fs, output="sos")
        gsig_grid = {g: [] for g in GROUPS}; gsig_onset = {g: [] for g in GROUPS}
        on_r, off_r = [], []
        for r in rows.itertuples(index=False):
            for mode, store in (("grid", gsig_grid), ("onset", gsig_onset)):
                if mode == "onset":
                    if not (r.has_blip is True or r.has_blip == True) or pd.isna(r.onset_ms):
                        continue
                    t0 = r.recording_start_time_s + r.onset_ms / 1000.0
                else:
                    t0 = r.recording_start_time_s
                s = int(round(t0 * fs)) - npre
                if s < 0 or s + ns > n:
                    continue
                seg = grp_ref(np.asarray(lfp[s:s + ns], dtype=np.float32), BAD)
                seg = seg - np.median(seg[pre_m], axis=0, keepdims=True)
                for g, ch in GROUPS.items():
                    use = [c for c in ch if c not in BAD]
                    store[g].append(np.mean(seg[:, use], axis=1))
                if mode == "grid":  # RMS within-trial control (grid timing is fine for 3s windows)
                    gm = np.mean(seg[:, [c for c in range(128) if c not in BAD]], axis=1)
                    on_r.append(np.sqrt(np.mean(gm[on_m] ** 2))); off_r.append(np.sqrt(np.mean(gm[off_m] ** 2)))
        # ITPC per group then average groups
        def itpc(store):
            vals, tcs = [], []
            for g in GROUPS:
                if len(store[g]) < 5: continue
                arr = np.asarray(store[g])
                ph = np.angle(hilbert(sosfiltfilt(sos, arr, axis=1), axis=1))
                it = np.abs(np.mean(np.exp(1j * ph), axis=0))
                vals.append(np.mean(it[sus_m])); tcs.append(it)
            return (float(np.mean(vals)) if vals else np.nan), (np.mean(tcs, axis=0) if tcs else np.full(ns, np.nan))
        itpc_grid[cond], tc_grid[cond] = itpc(gsig_grid)
        itpc_onset[cond], tc_onset[cond] = itpc(gsig_onset)
        rms_on[cond], rms_off[cond] = float(np.mean(on_r)), float(np.mean(off_r))

    # ---- Figure A: ITPC grid vs onset ----
    fig, ax = plt.subplots(1, 2, figsize=(15, 5.5))
    x = np.arange(len(COND)); w = 0.38
    ax[0].bar(x - w/2, [itpc_grid[c] for c in COND], w, color="#7f8c8d", label="aligned to command grid")
    ax[0].bar(x + w/2, [itpc_onset[c] for c in COND], w, color="#2a9d8f", label="aligned to MEASURED onset")
    ax[0].set_xticks(x); ax[0].set_xticklabels(COND, rotation=40, ha="right", fontsize=8)
    ax[0].set_ylabel("sustained ITPC (driven freq, 0.2-2.8 s)")
    ax[0].set_title("A. Phase locking: grid vs measured-onset alignment (Cohen 19.5)"); ax[0].legend(fontsize=8); ax[0].grid(axis="y", alpha=0.2)
    for c in ["amp250_freq26", "amp180_freq26"]:
        ax[1].plot(t, tc_grid[c], color=COL[c], lw=1, ls="--", alpha=0.7, label=f"{c} grid")
        ax[1].plot(t, tc_onset[c], color=COL[c], lw=1.8, label=f"{c} onset-aligned")
    ax[1].axvspan(0, 3, color="gold", alpha=0.12); ax[1].axvline(0, color="k", lw=0.8)
    ax[1].set_xlabel("time from onset (s)"); ax[1].set_ylabel("ITPC")
    ax[1].set_title("ITPC time course (26 Hz conditions)"); ax[1].legend(fontsize=7); ax[1].grid(alpha=0.2)
    fig.suptitle("A) Phase-locking corrected for onset jitter (Cohen 19.5)", fontweight="bold")
    fig.tight_layout(); fig.savefig(args.output_dir / "A_itpc_onset_vs_grid.png", dpi=150); plt.close(fig)

    # ---- Figure B: broadband RMS (Cohen ch.18) ----
    fig, ax = plt.subplots(figsize=(11, 5))
    on = [rms_on[c] for c in COND]; off = [rms_off[c] for c in COND]
    ax.bar(x - w/2, on, w, color="#4C78A8", label="ON RMS")
    ax.bar(x + w/2, off, w, color="#54A24B", label="within-trial OFF RMS")
    for i, c in enumerate(COND):
        ax.text(i, max(on[i], off[i]) + 1, f"ON-OFF={on[i]-off[i]:+.1f}", ha="center", fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels(COND, rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("broadband RMS (a.u.)  [= sqrt power, Cohen ch.18]")
    ax.set_title("B. Broadband response as RMS/power (not mean|LFP|), with within-trial OFF control")
    ax.legend(); ax.grid(axis="y", alpha=0.2)
    fig.tight_layout(); fig.savefig(args.output_dir / "B_broadband_rms.png", dpi=150); plt.close(fig)

    summary = {"itpc_sustained_grid": {c: round(itpc_grid[c], 4) for c in COND},
               "itpc_sustained_onset_aligned": {c: round(itpc_onset[c], 4) for c in COND},
               "broadband_rms_on": {c: round(rms_on[c], 2) for c in COND},
               "broadband_rms_off": {c: round(rms_off[c], 2) for c in COND},
               "max_trials": args.max_trials,
               "note": "A: Cohen 19.5 onset-jitter correction. B: Cohen ch.18 power instead of mean|LFP|."}
    (args.output_dir / "cohen_corrected_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
