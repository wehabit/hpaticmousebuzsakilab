#!/usr/bin/env python3
"""Time-domain LFP examples for Dec 4.

This figure is meant to answer the practical review question "can you show raw-ish
LFP examples?" It uses the decimated LFP file, not PSD/spectrogram summaries. Traces
are baseline-subtracted per trial and scaled to microvolts for readability.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
LFP_PATH = ROOT / "Haptic_Stim_session2_251204_131403" / "amplifier.lfp"
TRIALS_PATH = ROOT / "analysis" / "outputs" / "dec4" / "spike_sorting_prep" / "trial_windows.csv"
OUT_DIR = ROOT / "analysis" / "outputs" / "dec4" / "event_aligned_lfp"
OUT_PATH = OUT_DIR / "raw_lfp_time_domain_examples_dec4.png"

FS = 1250.0
N_CHANNELS = 256
UV_PER_BIT = 0.195
PRE_S = 1.0
POST_S = 4.0
AMP = 250

# Good tissue contacts chosen to be representative and easy to explain.
# ch60 is dHPC tissue; ch181 is LEC tissue and near the 50 Hz single-unit/artifact
# discussion, but it is not a disconnected electrode.
CHANNELS = {
    "dHPC ch60": 60,
    "LEC ch181": 181,
}

COLORS = {
    5: "#4d4f53",
    10: "#8c1515",
    26: "#b83a4b",
    50: "#d2a44c",
}

# Distinct cool->warm hue ramp for the stacked trial-averaged panel (was: two
# near-identical reds). 50 Hz keeps the cardinal highlight.
HUE = {5: "#4C72B0", 10: "#55A868", 26: "#E6A817", 50: "#8C1515"}


def load_lfp() -> np.memmap:
    samples = LFP_PATH.stat().st_size // np.dtype("<i2").itemsize // N_CHANNELS
    return np.memmap(LFP_PATH, dtype="<i2", mode="r", shape=(samples, N_CHANNELS))


def extract_trace(
    lfp: np.memmap,
    on_start_s: float,
    channel: int,
    pre_s: float = PRE_S,
    post_s: float = POST_S,
) -> np.ndarray | None:
    pre = int(round(pre_s * FS))
    n = int(round((pre_s + post_s) * FS))
    start = int(round(on_start_s * FS)) - pre
    stop = start + n
    if start < 0 or stop > lfp.shape[0]:
        return None
    trace = np.asarray(lfp[start:stop, channel], dtype=np.float32) * UV_PER_BIT
    baseline = np.median(trace[:pre])
    return trace - baseline


def mean_condition_trace(
    lfp: np.memmap,
    trials: pd.DataFrame,
    condition: str,
    channel: int,
) -> tuple[np.ndarray, np.ndarray, int]:
    rows = trials[trials["condition"] == condition].sort_values("trial_number")
    traces = []
    for row in rows.itertuples(index=False):
        trace = extract_trace(lfp, float(row.on_start_s), channel)
        if trace is not None:
            traces.append(trace)
    stack = np.vstack(traces)
    mean = stack.mean(axis=0)
    sem = stack.std(axis=0, ddof=1) / np.sqrt(stack.shape[0])
    return mean, sem, stack.shape[0]


def robust_ylim(values: list[np.ndarray], pad: float = 0.12) -> tuple[float, float]:
    joined = np.concatenate([np.asarray(v).ravel() for v in values])
    lo, hi = np.percentile(joined, [1, 99])
    span = max(hi - lo, 1.0)
    return float(lo - pad * span), float(hi + pad * span)


def decorate_time_axis(ax: plt.Axes) -> None:
    ax.axvspan(0, 3, color="#f4d35e", alpha=0.16, lw=0)
    ax.axvline(0, color="black", lw=0.9)
    ax.axvline(3, color="black", lw=0.9, ls="--")
    ax.set_xlim(-1, 4)
    ax.grid(alpha=0.18)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lfp = load_lfp()
    trials = pd.read_csv(TRIALS_PATH)
    time = (np.arange(int(round((PRE_S + POST_S) * FS))) - int(round(PRE_S * FS))) / FS

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 7.4), sharex=True)
    fig.suptitle(
        "Dec 4 time-domain LFP examples: real traces before the spectral summaries",
        fontsize=15,
        fontweight="bold",
        y=0.985,
    )

    condition = "amp250_freq50"
    rows50 = trials[trials["condition"] == condition].sort_values("trial_number")
    example_row = rows50.iloc[len(rows50) // 2]

    single_values = []
    for ax, (label, ch) in zip(axes[0], CHANNELS.items()):
        trace = extract_trace(lfp, float(example_row.on_start_s), ch)
        if trace is None:
            raise RuntimeError(f"Could not extract {label} example trace")
        single_values.append(trace)
        ax.plot(time, trace, color="#2e2d29", lw=0.8)
        decorate_time_axis(ax)
        ax.set_title(f"Single trial, {condition}, {label}", fontsize=11)
        ax.set_ylabel("LFP (uV), baseline-subtracted")

    ylim = robust_ylim(single_values)
    for ax in axes[0]:
        ax.set_ylim(*ylim)

    freqs = [26, 50]          # focus on 26 & 50 Hz for now (ignore 5/10)
    for ax, (label, ch) in zip(axes[1], CHANNELS.items()):
        means, sems, ns = {}, {}, {}
        for freq in freqs:
            means[freq], sems[freq], ns[freq] = mean_condition_trace(lfp, trials, f"amp{AMP}_freq{freq}", ch)
        # one band per carrier (vertical offset) so the traces never overlap
        spans = [np.percentile(means[f], 99) - np.percentile(means[f], 1) for f in freqs]
        step = max(spans) * 1.35
        ax.axvspan(0, 3, color="#f4d35e", alpha=0.16, lw=0)
        ax.axvline(0, color="black", lw=0.9)
        ax.axvline(3, color="black", lw=0.9, ls="--")
        yticks, yticklabels = [], []
        for i, freq in enumerate(freqs):              # 5 Hz bottom -> 50 Hz top
            y0 = step * i
            ax.axhline(y0, color="#dcdcdc", lw=0.6, zorder=1)
            ax.fill_between(time, means[freq] - sems[freq] + y0, means[freq] + sems[freq] + y0,
                            color=HUE[freq], alpha=0.18, lw=0, zorder=2)
            ax.plot(time, means[freq] + y0, color=HUE[freq], lw=1.1, zorder=3)
            yticks.append(y0)
            yticklabels.append(f"{freq} Hz  (n={ns[freq]})")
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticklabels, fontsize=8.5)
        for tick, freq in zip(ax.get_yticklabels(), freqs):
            tick.set_color(HUE[freq])
        ax.set_xlim(-1, 4)
        ax.set_ylim(-step, step * len(freqs))
        ax.grid(axis="x", alpha=0.18)
        ax.set_title(f"Trial-averaged LFP at amp{AMP}, {label} — stacked by carrier", fontsize=11)
        ax.set_xlabel("Time from vibration ON (s)")
        # amplitude scale bar (since y is now an offset stack, not absolute uV)
        sb = max(5, int(round(step / 4 / 5)) * 5)
        xb, yb = 3.92, step * (len(freqs) - 1)
        ax.plot([xb, xb], [yb - sb / 2, yb + sb / 2], color="black", lw=2.2, zorder=5,
                clip_on=False)
        ax.text(xb - 0.06, yb, f"{sb} µV", rotation=90, va="center", ha="right", fontsize=7.5)

    fig.text(
        0.5,
        0.015,
        "Yellow band = commanded 3 s vibration ON. These are time-domain LFP traces, not evidence of entrainment; "
        "LEC 50 Hz LFP remains artifact-suspect because disconnected LEC contacts also pick up 50 Hz.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.04, 1, 0.955])
    fig.savefig(OUT_PATH, dpi=200)
    plt.close(fig)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
