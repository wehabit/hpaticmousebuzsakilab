#!/usr/bin/env python
"""Sharp-wave ripple (SWR) detection across STATES (Dec 3 + Dec 4 dHPC).

EXPLORATORY hippocampal physiology — secondary to the haptic 50 Hz result, and
explicitly caveated:
  * The CA1 pyramidal layer is NOT confirmed (provisional channel-map). The ripple
    channel is chosen DATA-DRIVEN (max ripple-band power in the quiet baseline); its
    layer identity is provisional.
  * Ripples are a hippocampal (CA1) event, so this runs on the dHPC probe only.
  * 50 Hz stimulus HARMONICS (100/150/200/250 Hz) fall inside the 100-250 Hz ripple
    band, so ON-state counts during freq50 trials may include harmonic artifact.
    The clean comparisons are baseline / OFF / post (no active stimulus); ON is
    flagged.

For the data-driven ripple channel we detect ripples over the whole recording
(bandpass 100-250 Hz -> Hilbert envelope -> smooth -> z; peak >5 SD, edges >2 SD,
15-200 ms, merge <30 ms), assign each event to baseline / ON / OFF / post, and report
ripple RATE, AMPLITUDE, DURATION per state (bootstrap 95% CIs), plus single-unit
ripple PARTICIPATION by putative cell type (pyramidal- vs interneuron-like).

Outputs -> analysis/outputs/cross_dataset_spike_compare/ripples/ and (via builders)
results/dec*/11_Spikes/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt, hilbert
from scipy.ndimage import gaussian_filter1d

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/Users/paris/Documents/Buzsakli Lab Github")
FS = 1250.0
RIPPLE_BAND = (100.0, 250.0)
PEAK_SD, EDGE_SD = 5.0, 2.0
MIN_MS, MAX_MS, MERGE_MS = 15.0, 200.0, 30.0
WIN, START_MARGIN, GAP, END_MARGIN = 3.0, 60.0, 30.0, 30.0
B_BOOT = 5000
RNG = np.random.default_rng(0)
STATE_COL = {"baseline": "#6c757d", "ON": "#d1495b", "OFF": "#e9c46a", "post": "#457b9d"}
C_PYR, C_INT = "#2a6f97", "#e76f51"

SESS = {
    "dec3_dHPC": dict(lfp=ROOT / "Haptic_Stim_session1_251203_143031/amplifier.lfp", n_ch=128,
                      dhpc=range(0, 128), bad=ROOT / "analysis/bad_channels_dec3.json",
                      trials=ROOT / "analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv",
                      curated=ROOT / "analysis/outputs/dec3/curated_merged"),
    "dec4_dHPC": dict(lfp=ROOT / "Haptic_Stim_session2_251204_131403/amplifier.lfp", n_ch=256,
                      dhpc=range(0, 128), bad=ROOT / "analysis/bad_channels_dec4.json",
                      trials=ROOT / "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv",
                      curated=ROOT / "analysis/outputs/dec4/curated_merged_dhpc"),
}
CELLTYPE = ROOT / "analysis/outputs/cross_dataset_spike_compare/celltype/celltype_features_by_unit.csv"
OUT = ROOT / "analysis/outputs/cross_dataset_spike_compare/ripples"


def load_bad(p):
    d = json.loads(Path(p).read_text())
    for k in ("definite_bad_channels", "candidate_bad_channels"):
        if k in d:
            return set(int(x) for x in d[k])
    return set()


def bp(x):
    sos = butter(4, [RIPPLE_BAND[0], RIPPLE_BAND[1]], btype="band", fs=FS, output="sos")
    return sosfiltfilt(sos, x)


def boot_ci(v, b=B_BOOT):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    if len(v) < 2:
        return (float(v[0]) if len(v) else np.nan,) * 3
    idx = RNG.integers(0, len(v), (b, len(v)))
    m = v[idx].mean(1)
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def tile(t0, t1):
    n = int(np.floor((t1 - t0) / WIN))
    return [(t0 + i * WIN, t0 + (i + 1) * WIN) for i in range(max(n, 0))]


def detect_ripples(env_z):
    """env_z: z-scored smoothed ripple envelope. Returns list of (start,peak,end) samples."""
    above = env_z > EDGE_SD
    edges = np.diff(above.astype(int))
    starts = np.where(edges == 1)[0] + 1
    ends = np.where(edges == -1)[0] + 1
    if above[0]:
        starts = np.r_[0, starts]
    if above[-1]:
        ends = np.r_[ends, len(env_z)]
    ev = []
    for s, e in zip(starts, ends):
        seg = env_z[s:e]
        if seg.max() < PEAK_SD:
            continue
        dur_ms = (e - s) / FS * 1000
        if dur_ms < MIN_MS or dur_ms > MAX_MS:
            continue
        ev.append((s, s + int(seg.argmax()), e))
    # merge events whose gap < MERGE_MS
    merged = []
    for s, p, e in ev:
        if merged and (s - merged[-1][2]) / FS * 1000 < MERGE_MS:
            ps, pp, pe = merged[-1]
            merged[-1] = (ps, pp if env_z[pp] >= env_z[p] else p, e)
        else:
            merged.append((s, p, e))
    return merged


def state_of(t, base, post, ons, offs):
    if base[0] <= t < base[1]:
        return "baseline"
    if post[0] <= t < post[1]:
        return "post"
    if np.any((ons[:, 0] <= t) & (t < ons[:, 1])):
        return "ON"
    if np.any((offs[:, 0] <= t) & (t < offs[:, 1])):
        return "OFF"
    return "other"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ct = pd.read_csv(CELLTYPE)
    rate_rows, ev_rows, part_rows, summary, onfreq_rows = [], [], [], [], []
    example = {}

    for name, cfg in SESS.items():
        lfp = np.memmap(cfg["lfp"], dtype="<i2", mode="r",
                        shape=(cfg["lfp"].stat().st_size // 2 // cfg["n_ch"], cfg["n_ch"]))
        dur = lfp.shape[0] / FS
        tw = pd.read_csv(cfg["trials"])
        first_on, last_off = float(tw.on_start_s.min()), float(tw.off_end_s.max())
        base = (START_MARGIN, first_on - GAP); post = (last_off + GAP, dur - END_MARGIN)
        ons = tw[["on_start_s", "on_end_s"]].to_numpy(); offs = tw[["off_start_s", "off_end_s"]].to_numpy()
        bad = load_bad(cfg["bad"]); good = [c for c in cfg["dhpc"] if c not in bad]

        # --- data-driven ripple channel: max ripple-band RMS over a baseline slice ---
        bi, be = int((base[0] + 5) * FS), int((base[0] + 205) * FS)   # 200 s of baseline
        rms = []
        for c in good:
            rms.append(np.sqrt(np.mean(bp(np.asarray(lfp[bi:be, c], float)) ** 2)))
        rip_ch = good[int(np.argmax(rms))]

        # --- detect ripples on that channel, whole recording ---
        sig = np.asarray(lfp[:, rip_ch], dtype=np.float32)
        filt = bp(sig)
        env = np.abs(hilbert(filt))
        env = gaussian_filter1d(env, sigma=int(0.008 * FS))           # ~8 ms smooth
        env_z = (env - np.median(env)) / (1.4826 * np.median(np.abs(env - np.median(env))) + 1e-9)
        events = detect_ripples(env_z)

        # --- assign to state, collect rate/amp/dur ---
        peaks_t = np.array([p / FS for _, p, _ in events])
        states = np.array([state_of(t, base, post, ons, offs) for t in peaks_t])
        amps = np.array([env_z[p] for _, p, _ in events])
        durs = np.array([(e - s) / FS * 1000 for s, _, e in events])
        state_dur = {"baseline": base[1] - base[0], "post": post[1] - post[0],
                     "ON": float((ons[:, 1] - ons[:, 0]).sum()), "OFF": float((offs[:, 1] - offs[:, 0]).sum())}
        state_epochs = {"baseline": tile(*base), "post": tile(*post),
                        "ON": list(map(tuple, ons)), "OFF": list(map(tuple, offs))}

        for st in ["baseline", "ON", "OFF", "post"]:
            m = states == st
            # rate via per-epoch event counts (bootstrap over epochs)
            ep = state_epochs[st]
            counts = []
            for (s, e) in ep:
                counts.append(int(((peaks_t >= s) & (peaks_t < e)).sum()))
            counts = np.array(counts)
            rmean, rlo, rhi = boot_ci(counts / WIN)                    # events/s
            amean, alo, ahi = boot_ci(amps[m]); dmean, dlo, dhi = boot_ci(durs[m])
            rate_rows.append(dict(session=name, state=st, n_ripples=int(m.sum()),
                                  state_dur_s=round(state_dur[st], 1),
                                  rate_hz=round(rmean, 4), rate_ci=[round(rlo, 4), round(rhi, 4)],
                                  amp_z=round(amean, 3), amp_ci=[round(alo, 3), round(ahi, 3)],
                                  dur_ms=round(dmean, 1), dur_ci=[round(dlo, 1), round(dhi, 1)]))
        # --- stricter artifact control: ON ripple rate split by stimulus frequency ---
        # 50 Hz stimulus harmonics (100/150/200/250 Hz) fall in the ripple band, so a
        # genuine harmonic artifact would inflate the 50 Hz-ON "ripple" rate specifically.
        base_rate = float(rate_rows[-4]["rate_hz"])           # baseline rate for this session (first of the 4)
        on_arr = tw[["on_start_s", "on_end_s", "freq"]].to_numpy()
        stim_freqs = sorted(int(x) for x in tw["freq"].unique())
        for fr in stim_freqs + ["ON_excl_50"]:
            fw = (on_arr[on_arr[:, 2] != 50] if fr == "ON_excl_50" else on_arr[on_arr[:, 2] == fr])[:, :2]
            counts = np.array([int(((peaks_t >= s) & (peaks_t < e)).sum()) for s, e in fw])
            rmean, rlo, rhi = boot_ci(counts / WIN)
            onfreq_rows.append(dict(session=name, stim_freq=fr, n_on_ripples=int(counts.sum()),
                                    on_dur_s=round(float((fw[:, 1] - fw[:, 0]).sum()), 1),
                                    rate_hz=round(rmean, 4), rate_ci=[round(rlo, 4), round(rhi, 4)],
                                    baseline_rate_hz=round(base_rate, 4)))
        # save one example ripple (highest-amp baseline event)
        base_ev = [(s, p, e) for (s, p, e), st in zip(events, states) if st == "baseline"]
        if base_ev:
            s, p, e = max(base_ev, key=lambda P: env_z[P[1]])
            w0, w1 = p - int(0.1 * FS), p + int(0.1 * FS)
            example[name] = dict(raw=sig[w0:w1].copy(), filt=filt[w0:w1].copy(),
                                 t=(np.arange(w0, w1) - p) / FS * 1000, ch=rip_ch)

        # --- unit ripple participation by cell type ---
        st_samp = np.load(cfg["curated"] / "spike_times.npy").astype(np.int64)
        sc = np.load(cfg["curated"] / "spike_clusters.npy").astype(np.int64)
        spk_t = st_samp / 20000.0                                      # spikes were sampled at 20 kHz
        rip_iv = np.array([(s / FS, e / FS) for s, _, e in events])
        total_rip = float((rip_iv[:, 1] - rip_iv[:, 0]).sum())
        cset = ct[ct.dataset == name][["cluster_id", "cell_type"]]
        for _, row in cset.iterrows():
            cid = int(row.cluster_id); ts = np.sort(spk_t[sc == cid])
            inr = 0; participated = 0
            for (rs, re) in rip_iv:
                k = np.searchsorted(ts, [rs, re])
                c = k[1] - k[0]; inr += c; participated += (c > 0)
            in_rate = inr / total_rip if total_rip else np.nan
            out_rate = (len(ts) - inr) / (dur - total_rip) if (dur - total_rip) > 0 else np.nan
            part_rows.append(dict(session=name, cluster_id=cid, cell_type=row.cell_type,
                                  in_ripple_rate_hz=round(in_rate, 3), out_ripple_rate_hz=round(out_rate, 3),
                                  modulation=round(in_rate / out_rate, 3) if out_rate else np.nan,
                                  participation_frac=round(participated / max(len(events), 1), 3)))

        summary.append(dict(session=name, ripple_channel=int(rip_ch), n_ripples=len(events),
                            median_amp_z=round(float(np.median(amps)), 2),
                            median_dur_ms=round(float(np.median(durs)), 1),
                            note="data-driven channel; CA1 layer provisional; ON has 50 Hz-harmonic caveat"))
        print(f"{name}: ripple ch={rip_ch}  n_ripples={len(events)}  "
              f"rates/s " + " ".join(f"{r['state']}={r['rate_hz']:.3f}" for r in rate_rows if r['session'] == name))

    pd.DataFrame(rate_rows).to_csv(OUT / "ripple_rate_by_state.csv", index=False)
    pd.DataFrame(part_rows).to_csv(OUT / "ripple_participation_by_unit.csv", index=False)
    pd.DataFrame(onfreq_rows).to_csv(OUT / "ripple_on_rate_by_stim_freq.csv", index=False)
    (OUT / "ripple_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    _fig_rates(rate_rows, OUT)
    _fig_examples(example, OUT)
    _fig_participation(pd.DataFrame(part_rows), OUT)
    _fig_onfreq(pd.DataFrame(onfreq_rows), OUT)
    print("\n=== ripple summary ===")
    print(json.dumps(summary, indent=2))


def _fig_rates(rows, out):
    df = pd.DataFrame(rows); sess = df.session.unique(); sts = ["baseline", "ON", "OFF", "post"]
    fig, axes = plt.subplots(len(sess), 3, figsize=(13, 4.2 * len(sess)), squeeze=False)
    for i, sname in enumerate(sess):
        g = df[df.session == sname].set_index("state").reindex(sts)
        for j, (col, lab) in enumerate([("rate_hz", "ripple rate (events/s)"),
                                        ("amp_z", "ripple amplitude (z)"), ("dur_ms", "ripple duration (ms)")]):
            ax = axes[i][j]
            ci = g[col.split("_")[0] + "_ci"]
            lo = [g[col].iloc[k] - ci.iloc[k][0] for k in range(4)]
            hi = [ci.iloc[k][1] - g[col].iloc[k] for k in range(4)]
            ax.bar(range(4), g[col], yerr=[lo, hi], capsize=4,
                   color=[STATE_COL[s] for s in sts], error_kw=dict(ecolor="#222", lw=1.3))
            ax.set_xticks(range(4)); ax.set_xticklabels(sts); ax.set_ylabel(lab)
            ax.set_title(f"{sname}: {lab.split('(')[0].strip()}")
            if j == 1:
                ax.text(0.5, 0.97, "ON: 50 Hz-harmonic caveat", transform=ax.transAxes,
                        ha="center", va="top", fontsize=8, color="#b00")
    fig.suptitle("Sharp-wave ripples by state (95% bootstrap CI) — dHPC, data-driven channel (CA1 provisional)",
                 fontsize=12)
    fig.tight_layout(); fig.savefig(out / "ripple_rate_by_state.png", dpi=170); plt.close(fig)


def _fig_examples(example, out):
    if not example:
        return
    fig, axes = plt.subplots(len(example), 1, figsize=(8, 3 * len(example)), squeeze=False)
    for ax, (name, d) in zip(axes[:, 0], example.items()):
        ax.plot(d["t"], d["raw"], color="#999", lw=0.8, label="raw LFP")
        ax.plot(d["t"], d["filt"], color="#264653", lw=1.2, label="100–250 Hz")
        ax.set_title(f"{name}: example ripple (ch {d['ch']})"); ax.set_xlabel("time from peak (ms)")
        ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(out / "ripple_examples.png", dpi=170); plt.close(fig)


def _fig_onfreq(df, out):
    """ON ripple rate split by stimulus frequency — isolates the 50 Hz-harmonic confound."""
    if df.empty:
        return
    sess = df.session.unique()
    fig, axes = plt.subplots(1, len(sess), figsize=(6 * len(sess), 4.6), squeeze=False, sharey=True)
    for ax, sname in zip(axes[0], sess):
        gs = df[df.session == sname]
        order = sorted([x for x in gs.stim_freq.unique() if x != "ON_excl_50"], key=lambda v: int(v)) + ["ON_excl_50"]
        g = gs.set_index("stim_freq").reindex(order)
        x = np.arange(len(order))
        cols = ["#d1495b" if str(f) == "50" else ("#457b9d" if f == "ON_excl_50" else "#adb5bd") for f in order]
        lo = [g.rate_hz.iloc[k] - g.rate_ci.iloc[k][0] for k in range(len(order))]
        hi = [g.rate_ci.iloc[k][1] - g.rate_hz.iloc[k] for k in range(len(order))]
        ax.bar(x, g.rate_hz, yerr=[lo, hi], capsize=3, color=cols, error_kw=dict(ecolor="#222", lw=1.2))
        ax.axhline(float(g.baseline_rate_hz.iloc[0]), color="#000", ls="--", lw=1.2, label="baseline rate")
        ax.set_xticks(x); ax.set_xticklabels([f"{f} Hz" if str(f).isdigit() else f for f in order], rotation=20, ha="right")
        ax.set_ylabel("ON ripple rate (events/s)"); ax.set_title(f"{sname}: ON ripples by stimulus freq"); ax.legend(fontsize=8)
    fig.suptitle("Ripple artifact control: if 50 Hz harmonics faked ripples, the 50 Hz-ON bar would tower over "
                 "the others & baseline", fontsize=10.5)
    fig.tight_layout(); fig.savefig(out / "ripple_on_rate_by_stim_freq.png", dpi=170); plt.close(fig)


def _fig_participation(df, out):
    if df.empty:
        return
    sess = df.session.unique()
    fig, axes = plt.subplots(1, len(sess), figsize=(6 * len(sess), 4.6), squeeze=False, sharey=True)
    for ax, sname in zip(axes[0], sess):
        g = df[df.session == sname]
        for i, (t, c) in enumerate([("pyramidal-like", C_PYR), ("interneuron-like", C_INT)]):
            vals = g.loc[g.cell_type == t, "modulation"].to_numpy()
            vals = vals[np.isfinite(vals)]
            if len(vals) == 0:
                continue
            m, lo, hi = boot_ci(vals)
            ax.bar(i, m, 0.6, yerr=[[m - lo], [hi - m]], capsize=4, color=c, label=f"{t} (n={len(vals)})")
            ax.scatter(np.full(len(vals), i) + RNG.uniform(-0.1, 0.1, len(vals)), vals, color="#444", s=16, zorder=3)
        ax.axhline(1, color="black", lw=1, ls="--")
        ax.set_xticks([0, 1]); ax.set_xticklabels(["pyr-like", "int-like"])
        ax.set_title(f"{sname}: ripple firing modulation"); ax.legend(fontsize=8)
    axes[0][0].set_ylabel("in-ripple / out-ripple firing rate")
    fig.suptitle("Single-unit ripple participation by cell type (>1 = fires more in ripples; 95% boot CI)", fontsize=11)
    fig.tight_layout(); fig.savefig(out / "ripple_participation_by_celltype.png", dpi=170); plt.close(fig)


if __name__ == "__main__":
    main()
