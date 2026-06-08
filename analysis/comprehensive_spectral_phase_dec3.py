#!/usr/bin/env python3
"""Two resource-grounded comprehensiveness upgrades for the Dec 3 LFP analysis.

#1  Spectral-slope / aperiodic decomposition  (buzcode bz_PowerSpectrumSlope;
    Cohen 2014 ch. 21.6 "broadband != oscillation").
    Fit the 1/f aperiodic component to the log-log power spectrum (excluding the
    driven band + harmonic), separately for the ON (sustained) and within-trial
    OFF windows. A broadband response shows up as a change in aperiodic OFFSET
    and/or SLOPE with NO narrowband peak rising above the 1/f fit at 5/26 Hz; a
    true oscillation shows a residual peak at the driven frequency.

#2  Phase locking with an explicit null floor (Cohen 2014 ch. 19; Rayleigh).
    ITPC is biased upward by finite trial count: under the null (no locking),
    E[ITPC] = 0.886/sqrt(n) and the p<0.05 Rayleigh threshold = sqrt(-ln a / n).
    Plot observed ITPC per condition with bootstrap CI against both lines so it
    is explicit whether ~0.07 is above chance.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import butter, hilbert, sosfiltfilt, welch

GROUPS = {"G96-127": list(range(96, 128)), "G64-95": list(range(64, 96)),
          "G32-63": list(range(32, 64)), "G0-31": list(range(0, 32))}
COND = ["amp250_freq26", "amp180_freq26", "amp100_freq26", "amp250_freq5", "amp180_freq5", "amp100_freq5"]
COL = {"amp250_freq26": "#7b241c", "amp180_freq26": "#c0392b", "amp100_freq26": "#e6776d",
       "amp250_freq5": "#1a5276", "amp180_freq5": "#2e86c1", "amp100_freq5": "#85c1e9"}
BAD = {5, 6, 7, 32, 33, 34, 43, 66, 67}
RESP_GROUP = "G0-31"                       # the channel cluster (~8-12) that carries the response


def parse_cond(c): return int(c.replace("amp", "").split("_")[0]), int(c.split("freq")[1])


def grp_ref(seg):                          # analysis-group median reference (the chosen reference)
    out = seg.copy()
    for ch in GROUPS.values():
        use = [c for c in ch if c not in BAD]
        out[:, ch] = seg[:, ch] - np.median(seg[:, use], axis=1, keepdims=True)
    return out


def fit_aperiodic(f, P, fmin, fmax, exclude):
    """Robust 1/f fit in log-log space, excluding driven/harmonic bins. Returns slope, offset, fit(logf)."""
    m = (f >= fmin) & (f <= fmax)
    for lo, hi in exclude:
        m &= ~((f >= lo) & (f <= hi))
    lf, lp = np.log10(f[m]), np.log10(P[m])
    slope, offset = np.polyfit(lf, lp, 1)
    lf_all = np.log10(np.where(f > 0, f, np.nan))      # avoid log10(0) at the DC bin
    return slope, offset, (slope * lf_all + offset)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lfp", type=Path, required=True)
    p.add_argument("--sequence", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=Path("analysis/outputs/dec3/comprehensive"))
    p.add_argument("--fs", type=float, default=1250.0)
    p.add_argument("--n-channels", type=int, default=128)
    p.add_argument("--max-trials", type=int, default=200)
    p.add_argument("--half-bw", type=float, default=1.5)
    p.add_argument("--n-boot", type=int, default=1000)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fs = args.fs
    n = args.lfp.stat().st_size // 2 // args.n_channels
    lfp = np.memmap(args.lfp, dtype="<i2", mode="r", shape=(n, args.n_channels))
    seq = pd.read_csv(args.sequence)
    rng = np.random.default_rng(321)

    pre, post = 1.0, 6.0
    npre = int(pre * fs); ns = int((pre + post) * fs); t = (np.arange(ns) - npre) / fs
    on_m  = (t >= 0.2) & (t <= 2.8)        # sustained ON
    off_m = (t >= 3.2) & (t <= 5.7)        # within-trial OFF (matched length)
    sus_m = (t >= 0.2) & (t <= 2.8)        # ITPC integration window
    resp_good = [c for c in GROUPS[RESP_GROUP] if c not in BAD]
    nper = int(fs)                         # 1 s -> 1 Hz bins

    psd = {}                               # cond -> (f, P_on, P_off)
    aper = {}                              # cond -> dict of slope/offset/residual
    itpc_obs, itpc_ci, n_used = {}, {}, {}

    for cond in COND:
        amp, fr = parse_cond(cond)
        rows = seq[seq.condition == cond].sort_values("trial_number")
        if len(rows) > args.max_trials:
            rows = rows.iloc[np.sort(rng.choice(len(rows), args.max_trials, replace=False))]
        sos = butter(4, [max(0.5, fr - args.half_bw), fr + args.half_bw], btype="bandpass", fs=fs, output="sos")

        Pon = Poff = None; non = 0
        phase_tc = []                      # per-trial phase timecourse (responsive group mean signal)
        for r in rows.itertuples(index=False):
            s = int(round(r.recording_start_time_s * fs)) - npre
            if s < 0 or s + ns > n: continue
            seg = grp_ref(np.asarray(lfp[s:s + ns], dtype=np.float32))
            blk = seg[:, resp_good]
            fo, po = welch(blk[on_m],  fs, nperseg=min(nper, on_m.sum()),  axis=0)
            ff, pf = welch(blk[off_m], fs, nperseg=min(nper, off_m.sum()), axis=0)
            po = po.mean(1); pf = pf.mean(1)
            Pon = po if Pon is None else Pon + po; Poff = pf if Poff is None else Poff + pf; non += 1
            gm = blk.mean(1) - np.median(blk[t < 0].mean(1))
            phase_tc.append(np.angle(hilbert(sosfiltfilt(sos, gm))))
        Pon /= non; Poff /= non; f = fo
        psd[cond] = (f, Pon, Poff)

        excl = [(fr - 2, fr + 2), (2 * fr - 2, 2 * fr + 2)]
        s_on, o_on, fit_on   = fit_aperiodic(f, Pon,  3, 120, excl)
        s_off, o_off, fit_off = fit_aperiodic(f, Poff, 3, 120, excl)
        # residual (flattened spectrum) at the driven frequency: peak above 1/f?
        di = np.argmin(np.abs(f - fr))
        res_on  = np.log10(Pon[di])  - fit_on[di]
        res_off = np.log10(Poff[di]) - fit_off[di]
        aper[cond] = dict(slope_on=s_on, slope_off=s_off, off_on=o_on, off_off=o_off,
                          fit_on=fit_on, fit_off=fit_off, res_on=res_on, res_off=res_off, fr=fr)

        # ---- ITPC + bootstrap + null floor ----
        A = np.asarray(phase_tc)           # (ntr, ns)
        ntr = A.shape[0]; n_used[cond] = ntr
        def itpc_of(idx):
            it = np.abs(np.mean(np.exp(1j * A[idx]), axis=0))
            return float(np.mean(it[sus_m]))
        itpc_obs[cond] = itpc_of(np.arange(ntr))
        boot = np.array([itpc_of(rng.integers(0, ntr, ntr)) for _ in range(args.n_boot)])
        itpc_ci[cond] = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)))

    # ================= FIGURE 1: spectral slope =================
    fig, ax = plt.subplots(1, 3, figsize=(19, 5.4))
    c0 = "amp180_freq26"; f, Pon, Poff = psd[c0]; a = aper[c0]
    ax[0].loglog(f, Pon,  color="#c0392b", lw=1.6, label="ON (sustained)")
    ax[0].loglog(f, Poff, color="#7f8c8d", lw=1.6, label="within-trial OFF")
    ax[0].loglog(f, 10**a["fit_on"],  color="#c0392b", lw=1, ls="--", alpha=0.7, label=f"1/f fit ON (slope {a['slope_on']:.2f})")
    ax[0].loglog(f, 10**a["fit_off"], color="#7f8c8d", lw=1, ls="--", alpha=0.7, label=f"1/f fit OFF (slope {a['slope_off']:.2f})")
    ax[0].axvline(26, color="gold", lw=2, alpha=0.6); ax[0].set_xlim(2, 200)
    ax[0].set_xlabel("frequency (Hz)"); ax[0].set_ylabel("power (a.u.)")
    ax[0].set_title(f"A. Power spectrum ON vs OFF + 1/f fit\n({c0}, {RESP_GROUP} good ch)"); ax[0].legend(fontsize=7)

    # flattened (residual) spectrum: peak above 1/f at the driven freq?
    for cond in ["amp180_freq26", "amp250_freq26", "amp100_freq26"]:
        f, Pon, _ = psd[cond]; a = aper[cond]
        ax[1].plot(f, np.log10(Pon) - a["fit_on"], color=COL[cond], lw=1.4, label=cond)
    ax[1].axvline(26, color="gold", lw=2, alpha=0.6, label="driven 26 Hz"); ax[1].axhline(0, color="k", lw=0.8)
    ax[1].set_xlim(2, 60); ax[1].set_xlabel("frequency (Hz)")
    ax[1].set_ylabel("flattened power  log10(P) - 1/f fit")
    ax[1].set_title("B. Oscillation test: residual above 1/f\n(a true 26 Hz oscillation = a bump here)"); ax[1].legend(fontsize=7)

    x = np.arange(len(COND)); w = 0.38
    slope_on = [aper[c]["slope_on"] for c in COND]; slope_off = [aper[c]["slope_off"] for c in COND]
    ax[2].bar(x - w/2, slope_off, w, color="#7f8c8d", label="OFF slope")
    ax[2].bar(x + w/2, slope_on,  w, color="#c0392b", label="ON slope")
    ax[2].set_xticks(x); ax[2].set_xticklabels(COND, rotation=40, ha="right", fontsize=8)
    ax[2].set_ylabel("aperiodic slope (1/f exponent)")
    ax[2].set_title("C. Broadband test: aperiodic slope ON vs OFF\n(steeper/shallower = broadband power shift)"); ax[2].legend(fontsize=8)
    for axx in ax: axx.grid(alpha=0.2)
    fig.suptitle("#1 Spectral-slope decomposition (bz_PowerSpectrumSlope / Cohen 21.6): is the response broadband or a 5/26 Hz oscillation?",
                 fontweight="bold")
    fig.tight_layout(); fig.savefig(args.output_dir / "spectral_slope_decomposition.png", dpi=150); plt.close(fig)

    # ================= FIGURE 2: phase-locking null floor =================
    fig, ax = plt.subplots(figsize=(11, 5.6))
    obs = [itpc_obs[c] for c in COND]
    lo = [max(0.0, itpc_obs[c] - itpc_ci[c][0]) for c in COND]; hi = [max(0.0, itpc_ci[c][1] - itpc_obs[c]) for c in COND]
    bars = ax.bar(x, obs, color=[COL[c] for c in COND], yerr=[lo, hi], capsize=4)
    # null floor and Rayleigh significance use the (shared) trial count
    nmed = int(np.median([n_used[c] for c in COND]))
    floor = 0.886 / np.sqrt(nmed); sig = np.sqrt(-np.log(0.05) / nmed)
    ax.axhline(floor, color="k", ls="--", lw=1.4, label=f"null floor  0.886/√n = {floor:.3f}  (n≈{nmed})")
    ax.axhline(sig,   color="#27ae60", ls="-", lw=1.6, label=f"Rayleigh p<0.05 threshold = {sig:.3f}")
    for i, c in enumerate(COND):
        ax.text(i, obs[i] + hi[i] + 0.004, f"n={n_used[c]}", ha="center", fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels(COND, rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("sustained ITPC (driven freq, 0.2-2.8 s)")
    ax.set_title("#2 Phase locking vs chance: observed ITPC (bootstrap 95% CI) against the finite-n null floor")
    ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.2)
    fig.tight_layout(); fig.savefig(args.output_dir / "phase_locking_null_floor.png", dpi=150); plt.close(fig)

    summary = {
        "channels": resp_good, "resp_group": RESP_GROUP, "max_trials": args.max_trials,
        "aperiodic": {c: {k: round(float(aper[c][k]), 4) for k in
                          ("slope_on", "slope_off", "off_on", "off_off", "res_on", "res_off")} for c in COND},
        "itpc_observed": {c: round(itpc_obs[c], 4) for c in COND},
        "itpc_boot_ci95": {c: [round(v, 4) for v in itpc_ci[c]] for c in COND},
        "n_trials": {c: n_used[c] for c in COND},
        "null_floor": round(float(floor), 4), "rayleigh_p05_threshold": round(float(sig), 4),
        "interpretation": "res_on ~ res_off near 0 => no narrowband peak above 1/f (broadband, not oscillation); "
                          "ITPC below null_floor/threshold => no phase locking above chance.",
    }
    (args.output_dir / "comprehensive_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
