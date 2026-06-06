#!/usr/bin/env python3
"""Accelerometer-TTL vs LFP overview for the Dec 3 haptic session.

Generates exactly three figures (plus their tables / summary):
  - session_timeline.png              whole session in minutes, with the protocol
                                      phases (baseline / stimulation / post-experiment).
  - ttl_lfp_context_and_trials.png    two panels: the whole session (top) and a zoom
                                      into 3 consecutive trials (bottom, each a
                                      different randomized condition), showing the
                                      3 s ON / 3 s OFF slices and the accelerometer
                                      onset/offset.
  - ttl_on_alignment_per_trial.png    per-trial alignment of the accelerometer onset
                                      blip to the commanded ON window, in milliseconds,
                                      with TTL_ON_ALIGNMENT.md + condition CSV.

The accelerometer TTL (digitalin bit 7) fires while the device physically vibrates.
Its first edge in a trial's ON window is the *detected* vibration onset, which lags
the commanded onset (the log-anchored stim-start + k x 6 s grid) by ~80-570 ms
depending on stimulation strength. The command grid is the authoritative onset; the
TTL confirms delivery and gives an approximate physical onset/offset.
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
from matplotlib.patches import ConnectionPatch, Patch, Rectangle
from matplotlib.lines import Line2D


DEFAULT_BAD_CHANNELS = [5, 6, 7, 32, 33, 34, 43, 66, 67]
CONDITION_ORDER = [
    "amp250_freq26", "amp180_freq26", "amp100_freq26",
    "amp250_freq5", "amp180_freq5", "amp100_freq5",
]
CONDITION_COLORS = {
    "amp250_freq26": "#7b241c", "amp180_freq26": "#c0392b", "amp100_freq26": "#e6776d",
    "amp250_freq5": "#1a5276", "amp180_freq5": "#2e86c1", "amp100_freq5": "#85c1e9",
}


# ---------------------------------------------------------------- loading
def load_lfp(path: Path, n_channels: int) -> np.memmap:
    samples = path.stat().st_size // np.dtype("<i2").itemsize // n_channels
    return np.memmap(path, dtype="<i2", mode="r", shape=(samples, n_channels))


def load_rising_edges(edges_csv: Path, ttl_rate_hz: float) -> np.ndarray:
    edges = pd.read_csv(edges_csv)
    return np.sort(edges[edges["edge"] == "rising"]["sample"].to_numpy() / ttl_rate_hz)


def load_all_edges(edges_csv: Path, ttl_rate_hz: float) -> np.ndarray:
    """All transitions (rising + falling) = the toggles of the active-toggling sensor."""
    edges = pd.read_csv(edges_csv)
    return np.sort(edges["sample"].to_numpy() / ttl_rate_hz)


def onset_tolerance(sequence: pd.DataFrame, transitions: np.ndarray, on_s: float, tols_ms) -> dict:
    """How close the first sensor *toggle* in each ON window is to the commanded ON start."""
    on0 = sequence["recording_start_time_s"].to_numpy()
    li = np.searchsorted(transitions, on0)
    ri = np.searchsorted(transitions, on0 + on_s)
    lag = np.full(len(on0), np.nan)
    for i, (lo, hi) in enumerate(zip(li, ri)):
        if hi > lo:
            lag[i] = (transitions[lo] - on0[i]) * 1000.0
    return {
        "total": int(len(on0)),
        "median_ms": float(np.nanmedian(lag)),
        "no_ttl": int(np.isnan(lag).sum()),
        "buckets": [(t, int((np.abs(lag) <= t).sum())) for t in tols_ms],
    }


def session_amplitude(lfp, good, lfp_rate_hz, bin_s):
    n = lfp.shape[0]
    edges_t = np.arange(0, n / lfp_rate_hz, bin_s)
    amp = np.full(len(edges_t) - 1, np.nan)
    for i in range(len(edges_t) - 1):
        a, b = int(edges_t[i] * lfp_rate_hz), int(edges_t[i + 1] * lfp_rate_hz)
        seg = np.asarray(lfp[a:b, good], dtype=np.float32)
        seg -= np.median(seg, axis=0, keepdims=True)
        amp[i] = np.mean(np.abs(seg))
    return 0.5 * (edges_t[:-1] + edges_t[1:]), amp, edges_t


# ---------------------------------------------------------------- alignment
def compute_alignment(sequence: pd.DataFrame, edges_s: np.ndarray, on_s: float) -> pd.DataFrame:
    """Per-trial first/last sensor TOGGLE inside the commanded ON window.

    `edges_s` are all transitions (rising + falling). Using the first toggle of
    either direction as the onset is the correct true-onset read for this
    active-toggling sensor (rising-only misses a leading falling edge)."""
    rows = []
    for r in sequence.itertuples(index=False):
        on0 = float(r.recording_start_time_s)
        on1 = on0 + on_s
        lo = np.searchsorted(edges_s, on0, side="left")
        hi = np.searchsorted(edges_s, on1, side="right")
        if hi > lo:
            first, last = edges_s[lo], edges_s[hi - 1]
            rows.append((int(r.trial_number), r.condition, hi - lo,
                         (first - on0) * 1000.0, (last - on0) * 1000.0, (last - first) * 1000.0, True))
        else:
            rows.append((int(r.trial_number), r.condition, 0, np.nan, np.nan, np.nan, False))
    return pd.DataFrame(rows, columns=["trial", "condition", "n_on_edges",
                                       "onset_ms", "last_ms", "span_ms", "has_blip"])


# ---------------------------------------------------------------- figures
def plot_session_timeline(centers, amp, edges_t, rising_s, phases, output: Path) -> None:
    m = lambda s: s / 60.0
    base0, stim0, stim1, post1, total = (phases["baseline_start_s"], phases["stim_start_s"],
                                         phases["stim_end_s"], phases["post_end_s"], phases["total_s"])
    ttl_hist, _ = np.histogram(rising_s, bins=edges_t)
    bin_s = edges_t[1] - edges_t[0]

    fig, ax = plt.subplots(2, 1, figsize=(15, 7), sharex=True)
    ax[0].bar(centers, ttl_hist, width=bin_s, color="#c0392b")
    ax[0].set_ylabel(f"TTL edges / {bin_s:g} s")
    ax[1].plot(centers, amp, color="#2c3e50", lw=0.8)
    ax[1].set_ylabel("mean |LFP| (a.u.)")
    ax[1].set_xlabel("time in recording (seconds)")
    ax[0].set_title(
        "Dec 3 - accelerometer-TTL (top) vs LFP amplitude over good channels (bottom)\n"
        "Protocol: 15-min baseline + 1200 trials x (3s ON+3s OFF)=120 min + 30-min post-experiment  =>  165 min"
    )
    for a_ in ax:
        a_.axvspan(base0, stim0, color="#9b59b6", alpha=0.10)
        a_.axvspan(stim0, stim1, color="gold", alpha=0.12)
        a_.axvspan(stim1, post1, color="#3498db", alpha=0.10)
        for x in (base0, stim0, stim1, post1):
            a_.axvline(x, color="k", lw=0.9, ls="--")
        a_.grid(alpha=0.2)
    ymax = ax[0].get_ylim()[1]
    for x, lab in [(base0, f"baseline start\n{m(base0):.1f} min ({base0:.0f}s)"),
                   (stim0, f"stim start\n{m(stim0):.1f} min ({stim0:.0f}s)"),
                   (stim1, f"stim end\n{m(stim1):.1f} min ({stim1:.0f}s)"),
                   (post1, f"post-exp end\n{m(post1):.1f} min ({post1:.0f}s)")]:
        ax[0].text(x, ymax * 0.98, lab, fontsize=7.5, va="top", ha="center",
                   bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="0.6", alpha=0.85))
    ax[0].annotate("", xy=(stim1, ymax * 0.55), xytext=(stim0, ymax * 0.55),
                   arrowprops=dict(arrowstyle="<->", color="#b8860b", lw=1.5))
    ax[0].text((stim0 + stim1) / 2, ymax * 0.6, f"stim block = {m(stim1 - stim0):.1f} min",
               ha="center", fontsize=10, color="#8a6d00", fontweight="bold")
    ax[0].text((base0 + stim0) / 2, ymax * 0.35, "15-min\nbaseline", ha="center", fontsize=8, color="#6c3483")
    ax[0].text((stim1 + post1) / 2, ymax * 0.35, "30-min\npost-experiment", ha="center", fontsize=8, color="#1f6391")
    sax = ax[0].secondary_xaxis("top", functions=(lambda s: s / 60.0, lambda mm: mm * 60.0))
    sax.set_xlabel("time in recording (MINUTES)")
    foot = (f"Stim block: {m(stim0):.1f}->{m(stim1):.1f} min = {m(stim1 - stim0):.1f} min (=1200x6s).   "
            f"15-min baseline before; 30-min post-experiment after.   Full protocol = {m(post1 - base0):.1f} min.   "
            f"TOTAL RECORDING = {m(total):.1f} min ({total:.0f}s).")
    fig.text(0.5, 0.005, foot, ha="center", fontsize=9, bbox=dict(boxstyle="round,pad=0.4", fc="#fcf3cf", ec="0.6"))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(output, dpi=150)
    plt.close(fig)


def plot_context_and_trials(lfp, good, rising_s, sequence, alignment, lfp_rate_hz,
                            phases, centers, amp, output: Path, period_s=6.0, on_s=3.0, n_trials_zoom=3) -> None:
    m = lambda s: s / 60.0
    base0, stim0, stim1, post1, total = (phases["baseline_start_s"], phases["stim_start_s"],
                                         phases["stim_end_s"], phases["post_end_s"], phases["total_s"])
    # anchor the zoom on the cleanest strong trial (most ON-window blips, amp250_freq26)
    strong = alignment[alignment.condition == "amp250_freq26"].sort_values("n_on_edges", ascending=False)
    anchor_trial = int(strong.iloc[0].trial) if len(strong) else int(sequence.iloc[0].trial_number)
    t0 = float(sequence.loc[sequence.trial_number == anchor_trial, "recording_start_time_s"].iloc[0])
    zw0, zw1 = t0 - 1.0, t0 + (n_trials_zoom * period_s) - 1.0

    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(3, 1, height_ratios=[0.75, 0.75, 1.4], hspace=0.45)
    axT = fig.add_subplot(gs[0])                 # accelerometer/vibration activity
    axL = fig.add_subplot(gs[1], sharex=axT)     # LFP amplitude (separate row, like session_timeline)
    axB = fig.add_subplot(gs[2])                 # zoom into trials

    # top two rows: whole session in minutes, TTL and LFP as SEPARATE stacked panels
    BIN = 10.0
    et = np.arange(0, total, BIN)
    hist, _ = np.histogram(rising_s, bins=et)
    tc = 0.5 * (et[:-1] + et[1:])
    axT.bar(m(tc), hist, width=m(BIN), color="#c0392b")
    axT.set_ylabel("sensor activity\n(toggles / 10 s)", color="#c0392b")
    axT.tick_params(axis="y", labelcolor="#c0392b")
    axL.plot(m(centers), amp, color="#2c3e50", lw=0.9)
    axL.set_ylabel("brain LFP amplitude\nmean |LFP| (a.u.)", color="#2c3e50")
    axL.tick_params(axis="y", labelcolor="#2c3e50")
    for ax_ in (axT, axL):
        ax_.set_xlim(0, m(total))
        for x0, x1, c in [(base0, stim0, "#9b59b6"), (stim0, stim1, "gold"), (stim1, post1, "#3498db")]:
            ax_.axvspan(m(x0), m(x1), color=c, alpha=0.13)
        for x in (base0, stim0, stim1, post1):
            ax_.axvline(m(x), color="k", lw=0.8, ls="--")
        ax_.grid(alpha=0.2)
    yt = axT.get_ylim()[1]
    axT.text(m((base0 + stim0) / 2), yt * 0.85, "15-min\nbaseline", ha="center", fontsize=9, color="#6c3483")
    axT.text(m((stim0 + stim1) / 2), yt * 0.9, "120-min stimulation (1200 trials, randomized order)",
             ha="center", fontsize=10, color="#8a6d00", fontweight="bold")
    axT.text(m((stim1 + post1) / 2), yt * 0.85, "30-min\npost-experiment", ha="center", fontsize=9, color="#1f6391")
    axT.set_title("WHOLE SESSION - accelerometer/vibration activity (top row) and brain LFP (middle row) as "
                  "SEPARATE panels, like the session timeline.\nBlack box = the trials zoomed below.")
    axL.set_xlabel("time in recording (minutes)")
    # mark the zoom region on both session panels; connect from the LFP (lower) panel to the zoom
    axT.add_patch(Rectangle((m(zw0), 0), m(zw1 - zw0), yt, fill=False, edgecolor="black", lw=1.2, zorder=10))
    ylt0, ylt1 = axL.get_ylim()
    axL.add_patch(Rectangle((m(zw0), ylt0), m(zw1 - zw0), ylt1 - ylt0, fill=False, edgecolor="black", lw=1.2, zorder=10))

    # bottom: zoom into consecutive trials (each a different condition)
    a, b = int(zw0 * lfp_rate_hz), int(zw1 * lfp_rate_hz)
    t = np.arange(a, b) / lfp_rate_hz
    grp = [c for c in range(96, 128) if c in good]
    trace = np.asarray(lfp[a:b, grp], dtype=np.float32).mean(axis=1)
    trace -= np.median(trace)
    axB.plot(m(t), trace, color="#2c3e50", lw=0.7, zorder=5, label="brain signal (LFP)")
    axB.set_xlim(m(zw0), m(zw1))
    axB.set_ylim(trace.min() * 1.18, trace.max() * 1.45)
    ylo, yhi = axB.get_ylim()
    seen: set[str] = set()
    lab = lambda x: None if x in seen else (seen.add(x) or x)
    for r in sequence.itertuples(index=False):
        on0 = float(r.recording_start_time_s)
        if on0 + on_s < zw0 or on0 > zw1:
            continue
        axB.axvspan(m(on0), m(on0 + on_s), color="gold", alpha=0.20, label=lab("ON (vibrating, 3 s)"))
        axB.axvspan(m(on0 + on_s), m(on0 + period_s), color="#95a5a6", alpha=0.13, label=lab("OFF (rest, 3 s)"))
        axB.text(m(on0 + 1.5), yhi * 0.93, f"trial #{int(r.trial_number)}\n{r.condition}", ha="center", va="top",
                 fontsize=9, fontweight="bold", color="#7d6608",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#b8860b", alpha=0.9))
        mm = (rising_s >= on0) & (rising_s < on0 + on_s)
        if mm.any():
            axB.axvline(m(rising_s[mm].min()), color="#c0392b", lw=1.8, label=lab("vibration STARTS (first sensor toggle)"))
            axB.axvline(m(rising_s[mm].max()), color="#c0392b", lw=1.8, ls=":", label=lab("vibration ENDS (last sensor toggle)"))
            axB.text(m((rising_s[mm].min() + rising_s[mm].max()) / 2), ylo * 0.8, f"{int(mm.sum())} toggles",
                     ha="center", fontsize=8, color="#c0392b")
    axB.set_xlabel("time in recording (minutes)")
    axB.set_ylabel("LFP (a.u.)")
    axB.set_title("ZOOM - consecutive trials, each a DIFFERENT condition (order is randomized).   "
                  "gold=ON/vibrating, gray=OFF/rest, red=motion sensor")
    axB.legend(loc="upper right", fontsize=8, ncol=2)
    axB.grid(alpha=0.2)
    for xc in (m(zw0), m(zw1)):
        fig.add_artist(ConnectionPatch(xyA=(xc, ylt0), coordsA=axL.transData, xyB=(xc, yhi),
                                       coordsB=axB.transData, color="black", lw=0.8, ls="--", alpha=0.6))
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_alignment(alignment: pd.DataFrame, output: Path, on_ms=3000.0) -> dict:
    df = alignment.copy()
    tot = len(df)
    has = int(df.has_blip.sum())
    w500 = int((df.onset_ms.abs() <= 500).sum())
    w200 = int((df.onset_ms.abs() <= 200).sum())
    med = float(np.nanmedian(df.onset_ms))

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(15, 8), gridspec_kw={"width_ratios": [2, 1]})
    GAP = 8  # small blank rows just to separate condition blocks
    y = GAP
    yticks, ylabels = [], []
    for cond in CONDITION_ORDER:
        sub = df[(df.condition == cond) & df.has_blip].sort_values("onset_ms")
        ys = np.arange(y, y + len(sub))
        axA.hlines(ys, sub.onset_ms, sub.last_ms, color=CONDITION_COLORS[cond], lw=0.5, alpha=0.5)
        axA.scatter(sub.onset_ms, ys, s=3, color="black", zorder=5)
        cmed = float(np.nanmedian(sub.onset_ms))
        axA.vlines(cmed, y, y + len(sub), color=CONDITION_COLORS[cond], lw=2.5)
        # median value printed in the clear zone to the RIGHT of the ON window (no box, transparent,
        # so it never covers the dense onset dots)
        axA.text(on_ms + 60, y + len(sub) / 2, f"median {cmed:.0f} ms", fontsize=10,
                 color=CONDITION_COLORS[cond], va="center", ha="left", fontweight="bold", alpha=0.85)
        in_on = int(((sub.onset_ms >= 0) & (sub.onset_ms <= on_ms)).sum())
        yticks.append(y + len(sub) / 2)
        ylabels.append(f"{cond}\n{in_on}/200 in ON")
        y += len(sub) + GAP
    axA.axvspan(0, on_ms, color="gold", alpha=0.18, zorder=0)
    axA.axvline(0, color="k", lw=1)
    axA.axvline(on_ms, color="k", lw=1, ls="--")
    axA.set_xlim(-200, 3650)
    axA.set_ylim(0, y - GAP)
    axA.set_yticks(yticks)
    axA.set_yticklabels(ylabels, fontsize=8)
    axA.set_xlabel("time relative to commanded ON onset (ms)")
    axA.set_title("Black dot = aligned onset (first sensor toggle).  Line = detected-vibration span.\n"
                  "Thick bar = condition median onset.  Gold = commanded ON window.  (Onset = first toggle.)")

    axB.hist(df.onset_ms.dropna(), bins=np.arange(-500, 3000, 100), color="#c0392b", alpha=0.85, orientation="horizontal")
    axB.axhspan(0, on_ms, color="gold", alpha=0.18)
    axB.axhline(0, color="k", lw=1)
    axB.axhline(med, color="black", lw=2, ls="--")
    axB.text(axB.get_xlim()[1] * 0.95, med, f" median {med:.0f} ms", va="bottom", ha="right", fontsize=9, fontweight="bold")
    axB.set_ylim(-200, 3100)
    axB.set_ylabel("aligned onset (first toggle) relative to ON onset (ms)")
    axB.set_xlabel("number of trials")
    axB.set_title("Onset-blip lag distribution (ms)")
    axB.text(0.97, 0.97, f"{has}/{tot} blip in ON window\n{w500} within 500 ms\n{w200} within 200 ms\n"
             f"{tot - has} have NO blip\nmedian lag {med:.0f} ms", transform=axB.transAxes, ha="right", va="top",
             fontsize=8, bbox=dict(boxstyle="round", fc="#fcf3cf", ec="0.6"))
    fig.suptitle("TTL (accelerometer) vs commanded ON-time alignment - onset blip marked, all 1200 trials",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return {"total": tot, "in_on": has, "within_500ms": w500, "within_200ms": w200,
            "no_blip": tot - has, "median_onset_ms": round(med)}


def write_alignment_tables(alignment: pd.DataFrame, counts: dict, tolerance: dict, outdir: Path, on_ms=3000.0) -> None:
    df = alignment
    rows = []
    for cond in CONDITION_ORDER:
        s = df[(df.condition == cond) & df.has_blip]
        rows.append(dict(condition=cond, n_trials=200,
                         aligned_in_ON=int(((s.onset_ms >= 0) & (s.onset_ms <= on_ms)).sum()),
                         median_onset_ms=round(float(np.nanmedian(s.onset_ms))),
                         median_span_ms=round(float(np.nanmedian(s.span_ms))),
                         within_500ms=int((s.onset_ms.abs() <= 500).sum()),
                         within_200ms=int((s.onset_ms.abs() <= 200).sum()),
                         no_blip=int(200 - len(s))))
    cs = pd.DataFrame(rows)
    cs.to_csv(outdir / "ttl_on_alignment_condition_summary.csv", index=False)
    df.to_csv(outdir / "ttl_onset_offset_alignment.csv", index=False)

    t = counts
    md = ["# TTL (accelerometer) vs commanded ON-time alignment - Dec 3", "",
          f"{t['in_on']} of {t['total']} trials ({100*t['in_on']//t['total']}%) have the accelerometer "
          "fire inside the commanded ON\nwindow - i.e., TTL and ON time are aligned. Breakdown:", "",
          "| Criterion | Count |", "|---|---|",
          f"| First blip inside the 3 s ON window | {t['in_on']} / {t['total']} ({100*t['in_on']//t['total']}%) |",
          f"| First blip within 0.5 s of ON onset | {t['within_500ms']} / {t['total']} ({round(100*t['within_500ms']/t['total'])}%) |",
          f"| First blip within 0.2 s of ON onset | {t['within_200ms']} / {t['total']} ({round(100*t['within_200ms']/t['total'])}%) |",
          f"| No sensor blip at all (no detected vibration) | {t['no_blip']} / {t['total']} ({round(100*t['no_blip']/t['total'])}%) |",
          "", "And alignment quality tracks the condition (tighter = stronger stimulation):", "",
          "| Condition | aligned (blip in ON) | typical onset lag |", "|---|---|---|"]
    for i, r in cs.iterrows():
        tight = " (tightest)" if i == 0 else ""
        md.append(f"| {r.condition} | {int(r.aligned_in_ON)}/200 | {int(r.median_onset_ms)} ms{tight} |")
    md += ["", "## How precisely does the measured onset match the commanded ON start?", "",
           f"First sensor *toggle* in each ON window vs the commanded ON start. No trial is exactly "
           f"aligned - there is always a physical delivery lag (median {tolerance['median_ms']:.0f} ms), "
           f"because the accelerometer only fires once the device actually vibrates. So the TTL is a "
           f"delivery *validator*, not the onset clock.", "",
           "| Tolerance | Trials |", "|---|---|"]
    tot = tolerance["total"]
    for t, n in tolerance["buckets"]:
        label = "exactly 0 ms" if t == 0 else f"within {t:g} ms"
        md.append(f"| {label} | {n} / {tot} |")
    md += ["", "Figure: `ttl_on_alignment_per_trial.png` · per-trial data: `ttl_onset_offset_alignment.csv`", ""]
    (outdir / "TTL_ON_ALIGNMENT.md").write_text("\n".join(md))


# ---------------------------------------------------------------- main
def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lfp", type=Path, required=True)
    p.add_argument("--edges-csv", type=Path, required=True)
    p.add_argument("--sequence", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=Path("analysis/outputs/dec3/ttl_lfp_overview"))
    p.add_argument("--n-channels", type=int, default=128)
    p.add_argument("--lfp-rate-hz", type=float, default=1250.0)
    p.add_argument("--ttl-rate-hz", type=float, default=20000.0)
    p.add_argument("--bad-channels", type=int, nargs="*", default=DEFAULT_BAD_CHANNELS)
    p.add_argument("--baseline-start-s", type=float, default=640.0)
    p.add_argument("--stim-start-s", type=float, default=1540.0)
    p.add_argument("--stim-end-s", type=float, default=8740.0)
    p.add_argument("--post-end-s", type=float, default=10540.0)
    p.add_argument("--overview-bin-s", type=float, default=10.0)
    p.add_argument("--on-s", type=float, default=3.0)
    args = p.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    good = [c for c in range(args.n_channels) if c not in set(args.bad_channels)]
    lfp = load_lfp(args.lfp, args.n_channels)
    rising = load_rising_edges(args.edges_csv, args.ttl_rate_hz)        # for activity-density figures
    transitions = load_all_edges(args.edges_csv, args.ttl_rate_hz)      # all toggles -> true onset
    sequence = pd.read_csv(args.sequence).sort_values("trial_number").reset_index(drop=True)
    phases = {"baseline_start_s": args.baseline_start_s, "stim_start_s": args.stim_start_s,
              "stim_end_s": args.stim_end_s, "post_end_s": args.post_end_s,
              "total_s": lfp.shape[0] / args.lfp_rate_hz}

    alignment = compute_alignment(sequence, transitions, args.on_s)     # toggle-based onsets
    tolerance = onset_tolerance(sequence, transitions, args.on_s, [0, 1, 5, 10, 20, 50, 100])

    centers, amp, edges_t = session_amplitude(lfp, good, args.lfp_rate_hz, args.overview_bin_s)
    plot_session_timeline(centers, amp, edges_t, rising, phases, args.output_dir / "session_timeline.png")
    plot_context_and_trials(lfp, good, transitions, sequence, alignment, args.lfp_rate_hz, phases,
                            centers, amp, args.output_dir / "ttl_lfp_context_and_trials.png", on_s=args.on_s)
    counts = plot_alignment(alignment, args.output_dir / "ttl_on_alignment_per_trial.png", on_ms=args.on_s * 1000)
    write_alignment_tables(alignment, counts, tolerance, args.output_dir, on_ms=args.on_s * 1000)

    mn = lambda s: round(s / 60.0, 2)
    summary = {
        "n_good_channels": len(good),
        "bad_channels": sorted(args.bad_channels),
        "n_ttl_rising_edges": int(len(rising)),
        "phases_minutes": {
            "baseline_15min": [mn(args.baseline_start_s), mn(args.stim_start_s)],
            "stimulation_120min": [mn(args.stim_start_s), mn(args.stim_end_s)],
            "post_experiment_30min": [mn(args.stim_end_s), mn(args.post_end_s)],
        },
        "total_recording_min": mn(phases["total_s"]),
        "alignment_counts": counts,
        "figures": ["session_timeline.png", "ttl_lfp_context_and_trials.png", "ttl_on_alignment_per_trial.png"],
        "tables": ["TTL_ON_ALIGNMENT.md", "ttl_on_alignment_condition_summary.csv", "ttl_onset_offset_alignment.csv"],
    }
    (args.output_dir / "ttl_lfp_overview_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
