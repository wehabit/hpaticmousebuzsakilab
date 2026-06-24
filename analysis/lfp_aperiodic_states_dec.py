#!/usr/bin/env python
"""LFP 1/f (aperiodic) slope across STATES: baseline / ON / OFF / post (Dec 3 + Dec 4).

The existing 1/f work ([spectral_slope_itpc_dec4.py]) tests the ON vs OFF trial
windows for a narrowband peak above the aperiodic background. It never compared the
aperiodic fit against the TRUE pre-experiment baseline or post-study state. This
script adds exactly that, to separate the two hypotheses the LFP can't otherwise
distinguish:

  * a change in the APERIODIC fit (slope + offset) across states
        = "the whole spectrum broadly shifted"  (state / E-I / broadband change)
  * a RESIDUAL peak above the per-state aperiodic fit at the driven frequency
        = "a real bump at the stimulation frequency"

For each session x region we tile baseline & post into 3 s epochs (matching the
spike state analysis), take the ON/OFF trial windows, group-median reference the
region's good channels, average Welch PSDs per channel per state, fit the aperiodic
1/f (log-log polyfit over 3-120 Hz excluding 50/100 Hz line noise), and report:
  - aperiodic SLOPE and OFFSET per state (broad-shift answer), and
  - the driven-frequency RESIDUAL above the fit per state (real-bump answer),
all with percentile bootstrap 95% CIs over channels.

Method (fit_aperiodic, group-ref) matches spectral_slope_itpc_dec4.py so the state
slopes are comparable to the existing ON/OFF entrainment slopes.

Outputs -> analysis/outputs/cross_dataset_spike_compare/lfp_aperiodic_states/ and
(via the results builders) results/dec*/05_Frequency_Spectral/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import welch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/Users/paris/Documents/Buzsakli Lab Github")
FS_LFP = 1250.0
WIN = 3.0
START_MARGIN, GAP, END_MARGIN = 60.0, 30.0, 30.0
N_WIN = 120                  # windows sampled per state (per condition for residuals)
NPERSEG = 1250               # 1 s -> 1.25 Hz resolution
FMIN, FMAX = 3.0, 120.0
LINE_EXCL = [(48, 52), (98, 102)]
B_BOOT = 5000
RNG = np.random.default_rng(0)

STATE_COL = {"baseline": "#6c757d", "ON": "#d1495b", "OFF": "#e9c46a", "post": "#457b9d"}

SESSIONS = {
    "dec3": dict(
        lfp=ROOT / "Haptic_Stim_session1_251203_143031/amplifier.lfp", n_ch=128,
        trials=ROOT / "analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv",
        bad_json=ROOT / "analysis/bad_channels_dec3.json",
        regions={"dHPC": range(0, 128)}),
    "dec4": dict(
        lfp=ROOT / "Haptic_Stim_session2_251204_131403/amplifier.lfp", n_ch=256,
        trials=ROOT / "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv",
        bad_json=ROOT / "analysis/bad_channels_dec4.json",
        regions={"dHPC": range(0, 128), "LEC": range(128, 256)}),
}
OUT = ROOT / "analysis/outputs/cross_dataset_spike_compare/lfp_aperiodic_states"


def load_bad(path: Path) -> set:
    d = json.loads(path.read_text())
    for k in ("definite_bad_channels", "candidate_bad_channels"):
        if k in d:
            return set(int(x) for x in d[k])
    return set()


def tile(t0, t1):
    n = int(np.floor((t1 - t0) / WIN))
    return [(t0 + i * WIN, t0 + (i + 1) * WIN) for i in range(max(n, 0))]


def sample(windows, k):
    if len(windows) <= k:
        return windows
    idx = RNG.choice(len(windows), k, replace=False)
    return [windows[i] for i in sorted(idx)]


def fit_aperiodic(f, P, exclude):
    m = (f >= FMIN) & (f <= FMAX)
    for lo, hi in exclude:
        m &= ~((f >= lo) & (f <= hi))
    lf, lp = np.log10(f[m]), np.log10(P[m])
    slope, offset = np.polyfit(lf, lp, 1)
    fit_all = slope * np.log10(np.where(f > 0, f, np.nan)) + offset
    return slope, offset, fit_all


def mean_psd(lfp, good, windows):
    """Average Welch PSD (per good channel) over the sampled windows. group-ref."""
    acc = None; n = 0
    for s, e in windows:
        si, ei = int(s * FS_LFP), int(e * FS_LFP)
        seg = np.asarray(lfp[si:ei, good], dtype=np.float32)
        if seg.shape[0] < NPERSEG:
            continue
        seg = seg - np.median(seg, axis=1, keepdims=True)        # group-median ref
        f, P = welch(seg, FS_LFP, nperseg=NPERSEG, axis=0)        # (nf, nch)
        acc = P if acc is None else acc + P
        n += 1
    return f, (acc / max(n, 1)), n


def boot_ci(v, b=B_BOOT, alpha=0.05):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    if len(v) < 2:
        return (float(v[0]) if len(v) else np.nan,) * 3
    idx = RNG.integers(0, len(v), (b, len(v)))
    m = v[idx].mean(1)
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    per_channel, summary, spectra = [], [], {}

    for sess, cfg in SESSIONS.items():
        lfp = np.memmap(cfg["lfp"], dtype="<i2", mode="r",
                        shape=(cfg["lfp"].stat().st_size // 2 // cfg["n_ch"], cfg["n_ch"]))
        dur = lfp.shape[0] / FS_LFP
        tw = pd.read_csv(cfg["trials"])
        first_on, last_off = float(tw.on_start_s.min()), float(tw.off_end_s.max())
        freqs = sorted(int(x) for x in tw["freq"].unique())
        base_w = sample(tile(START_MARGIN, first_on - GAP), N_WIN)
        post_w = sample(tile(last_off + GAP, dur - END_MARGIN), N_WIN)
        on_w = sample(list(zip(tw.on_start_s, tw.on_end_s)), N_WIN)
        off_w = sample(list(zip(tw.off_start_s, tw.off_end_s)), N_WIN)
        # per driven-freq ON/OFF windows (for the residual/bump)
        onf = {fr: sample(list(zip(tw[tw.freq == fr].on_start_s, tw[tw.freq == fr].on_end_s)), N_WIN) for fr in freqs}
        offf = {fr: sample(list(zip(tw[tw.freq == fr].off_start_s, tw[tw.freq == fr].off_end_s)), N_WIN) for fr in freqs}

        bad = load_bad(cfg["bad_json"])
        for region, rng in cfg["regions"].items():
            good = np.array([c for c in rng if c not in bad])
            states = {"baseline": base_w, "ON": on_w, "OFF": off_w, "post": post_w}
            psd_state, slope_state, offset_state = {}, {}, {}
            for st, w in states.items():
                f, P, n = mean_psd(lfp, good, w)
                psd_state[st] = (f, P)
                sl, of = [], []
                for ci in range(P.shape[1]):
                    s, o, _ = fit_aperiodic(f, P[:, ci], LINE_EXCL)
                    sl.append(s); of.append(o)
                slope_state[st], offset_state[st] = np.array(sl), np.array(of)
                for ci, (s, o) in enumerate(zip(sl, of)):
                    per_channel.append(dict(session=sess, region=region, state=st,
                                            channel=int(good[ci]), slope=round(s, 4),
                                            offset=round(o, 4), n_windows=n))
                sm, slo, shi = boot_ci(sl); om, olo, ohi = boot_ci(of)
                summary.append(dict(session=sess, region=region, state=st, quantity="aperiodic_slope",
                                    mean=round(sm, 4), ci_lo=round(slo, 4), ci_hi=round(shi, 4), n_ch=len(good)))
                summary.append(dict(session=sess, region=region, state=st, quantity="aperiodic_offset",
                                    mean=round(om, 4), ci_lo=round(olo, 4), ci_hi=round(ohi, 4), n_ch=len(good)))
            spectra[(sess, region)] = psd_state

            # ---- residual (bump above 1/f) at each driven freq, per state ----
            for fr in freqs:
                excl = LINE_EXCL + [(fr - 2, fr + 2), (2 * fr - 2, 2 * fr + 2)]
                state_w = {"baseline": base_w, "ON": onf[fr], "OFF": offf[fr], "post": post_w}
                for st, w in state_w.items():
                    f, P, n = mean_psd(lfp, good, w)
                    di = int(np.argmin(np.abs(f - fr)))
                    res = []
                    for ci in range(P.shape[1]):
                        _, _, fit = fit_aperiodic(f, P[:, ci], excl)
                        res.append(np.log10(P[di, ci]) - fit[di])
                    rm, rlo, rhi = boot_ci(res)
                    summary.append(dict(session=sess, region=region, state=st,
                                        quantity=f"residual_{fr}hz_log10",
                                        mean=round(rm, 4), ci_lo=round(rlo, 4),
                                        ci_hi=round(rhi, 4), n_ch=len(good)))

    pd.DataFrame(per_channel).to_csv(OUT / "aperiodic_per_channel.csv", index=False)
    sdf = pd.DataFrame(summary)
    sdf.to_csv(OUT / "aperiodic_state_summary.csv", index=False)
    (OUT / "aperiodic_state_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n")

    _fig_states("dec3", ["dHPC"], sdf, OUT)
    _fig_states("dec4", ["dHPC", "LEC"], sdf, OUT)
    _fig_bump_vs_shift("dec4", ["dHPC", "LEC"], sdf, OUT)
    _fig_bump_vs_shift("dec3", ["dHPC"], sdf, OUT)
    _fig_spectra(spectra, OUT)

    print("=== LFP aperiodic 1/f across states ===")
    print(sdf[sdf.quantity.isin(["aperiodic_slope", "aperiodic_offset"])].to_string(index=False))
    print("\n=== driven-freq residual (bump above 1/f) ===")
    print(sdf[sdf.quantity.str.startswith("residual")].to_string(index=False))


def _err(sdf, sess, region, quantity, state):
    r = sdf[(sdf.session == sess) & (sdf.region == region) & (sdf.quantity == quantity) & (sdf.state == state)]
    if r.empty:
        return np.nan, 0, 0
    m, lo, hi = float(r["mean"].iloc[0]), float(r.ci_lo.iloc[0]), float(r.ci_hi.iloc[0])
    return m, m - lo, hi - m


def _fig_states(sess, regions, sdf, out):
    sts = ["baseline", "ON", "OFF", "post"]
    fig, axes = plt.subplots(2, len(regions), figsize=(6.2 * len(regions), 8), squeeze=False)
    for j, reg in enumerate(regions):
        for row, q, lab in [(0, "aperiodic_slope", "aperiodic slope (1/f exponent)"),
                            (1, "aperiodic_offset", "aperiodic offset (broadband power)")]:
            ax = axes[row][j]
            ms = [_err(sdf, sess, reg, q, s) for s in sts]
            ax.bar(range(4), [m[0] for m in ms], yerr=[[m[1] for m in ms], [m[2] for m in ms]],
                   capsize=4, color=[STATE_COL[s] for s in sts], error_kw=dict(ecolor="#222", lw=1.4))
            ax.axhline(ms[0][0], color="#6c757d", ls="--", lw=1)
            ax.set_xticks(range(4)); ax.set_xticklabels(sts)
            ax.set_ylabel(lab); ax.set_title(f"{sess} {reg}: {lab.split('(')[0].strip()}")
    fig.suptitle(f"{sess} — LFP aperiodic 1/f across states (95% bootstrap CI over channels)", fontsize=12)
    fig.tight_layout(); fig.savefig(out / f"{sess}_aperiodic_states.png", dpi=170); plt.close(fig)


def _fig_bump_vs_shift(sess, regions, sdf, out):
    """The key figure: driven-freq RESIDUAL (bump) across states, per region & freq."""
    sts = ["baseline", "ON", "OFF", "post"]
    freqs = sorted(int(q.split("_")[1].replace("hz", "")) for q in
                   sdf[(sdf.session == sess)].quantity.unique() if q.startswith("residual"))
    fig, axes = plt.subplots(1, len(regions), figsize=(6.6 * len(regions), 4.8), squeeze=False, sharey=True)
    width = 0.8 / max(len(freqs), 1)
    for j, reg in enumerate(regions):
        ax = axes[0][j]
        for fi, fr in enumerate(freqs):
            ms = [_err(sdf, sess, reg, f"residual_{fr}hz_log10", s) for s in sts]
            x = np.arange(4) + (fi - (len(freqs) - 1) / 2) * width
            ax.bar(x, [m[0] for m in ms], width, yerr=[[m[1] for m in ms], [m[2] for m in ms]],
                   capsize=2, label=f"{fr} Hz", error_kw=dict(ecolor="#444", lw=1))
        ax.axhline(0, color="black", lw=1)
        ax.set_xticks(range(4)); ax.set_xticklabels(sts)
        ax.set_title(f"{sess} {reg}"); ax.set_xlabel("state"); ax.legend(fontsize=8, title="driven freq")
    axes[0][0].set_ylabel("residual above 1/f fit  (log10 power)\n>0 = real bump")
    fig.suptitle(f"{sess} — real bump vs broad shift: peak above the aperiodic fit, by state\n"
                 "(bump present in ON only = stimulus-locked peak; flat = no narrowband bump)", fontsize=11)
    fig.tight_layout(); fig.savefig(out / f"{sess}_bump_vs_broadshift.png", dpi=170); plt.close(fig)


def _fig_spectra(spectra, out):
    items = list(spectra.items())
    fig, axes = plt.subplots(1, len(items), figsize=(5.2 * len(items), 4.6), squeeze=False)
    for ax, ((sess, reg), psd) in zip(axes[0], items):
        for st in ["baseline", "ON", "OFF", "post"]:
            f, P = psd[st]
            ax.loglog(f, P.mean(1), color=STATE_COL[st], lw=1.8, label=st)
        ax.set_xlim(2, 120); ax.set_xlabel("frequency (Hz)"); ax.set_ylabel("power")
        ax.set_title(f"{sess} {reg}: mean PSD by state"); ax.legend(fontsize=8)
    fig.suptitle("Region-mean LFP spectra by state (log-log) — slope tilt = broad shift; a peak = a bump", fontsize=11)
    fig.tight_layout(); fig.savefig(out / "state_spectra_loglog.png", dpi=170); plt.close(fig)


if __name__ == "__main__":
    main()
