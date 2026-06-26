#!/usr/bin/env python
"""Ripple-band power localization by dHPC shank section / depth (Dec 3 + Dec 4).

We already detect real dHPC sharp-wave ripples on a single data-driven channel
(dec3 ch8, dec4 ch7 = max ripple-band power). This maps WHERE that power lives across
the whole dHPC probe: for every dHPC channel we measure ripple-band (100-250 Hz) RMS over
a quiet baseline slice, then place it at its (shank section, depth). A focal peak in one
section at one depth is consistent with a CA1 ripple zone; that the data-driven detection channel
sits on the peak confirms the channel choice is not arbitrary. This supports CA1-like
dHPC physiology, but exact layer identity still needs histology / CSD.

Same dHPC probe both sessions: section = 1 + ch//32, depth = (ch%32)*20 µm
(verified against the amplifier.xml channelGroups / probe metadata). The Cambridge
H12/L13 map indicates these four 32-channel sections are likely two physical shanks
split into upper/lower halves, so this figure should not be read as four independent
physical dHPC shanks. Reads the raw LFP the same way as ripple_states_dec.

Outputs -> analysis/outputs/cross_dataset_spike_compare/ripples/ and (builders)
results/dec*/11_Spikes/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("/Users/paris/Documents/Buzsakli Lab Github")
FS = 1250.0
BAND = (100.0, 250.0)
BASE_START, BASE_SEC = 60.0, 180.0      # quiet baseline slice for the power profile
N_SECTION, CH_PER = 4, 32
OUT = ROOT / "analysis/outputs/cross_dataset_spike_compare/ripples"
SUMMARY = OUT / "ripple_summary.json"

SESS = {
    "dec3_dHPC": dict(lfp=ROOT / "Haptic_Stim_session1_251203_143031/amplifier.lfp", n_ch=128,
                      bad=ROOT / "analysis/bad_channels_dec3.json",
                      trials=ROOT / "analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv"),
    "dec4_dHPC": dict(lfp=ROOT / "Haptic_Stim_session2_251204_131403/amplifier.lfp", n_ch=256,
                      bad=ROOT / "analysis/bad_channels_dec4.json",
                      trials=ROOT / "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv"),
}


def load_bad(p):
    d = json.loads(Path(p).read_text())
    bad = set()
    for k in ("definite_bad_channels", "candidate_bad_channels"):
        bad.update(int(c) for c in d.get(k, []))
    return bad


def detection_channels():
    s = json.loads(SUMMARY.read_text())
    return {r["session"]: int(r["ripple_channel"]) for r in s}


def band_rms(block, sos):
    """RMS of the band-passed signal per channel; block is (n_samp, n_ch)."""
    bp = sosfiltfilt(sos, block, axis=0)
    return np.sqrt(np.mean(bp ** 2, axis=0))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sos = butter(4, [b / (FS / 2) for b in BAND], btype="band", output="sos")
    det = detection_channels()
    results, rows = {}, []

    for name, cfg in SESS.items():
        tw = pd.read_csv(cfg["trials"])
        first_on = float(tw["on_start_s"].min())
        b0 = BASE_START
        b1 = min(first_on - 30.0, BASE_START + BASE_SEC)
        lfp = np.memmap(cfg["lfp"], dtype="<i2", mode="r",
                        shape=(cfg["lfp"].stat().st_size // 2 // cfg["n_ch"], cfg["n_ch"]))
        bi, be = int(b0 * FS), int(b1 * FS)
        block = np.asarray(lfp[bi:be, :128], dtype=np.float32)        # dHPC = first 128 ch
        rms = band_rms(block, sos)
        del block

        bad = load_bad(cfg["bad"])
        ch = np.arange(128)
        section = 1 + ch // CH_PER
        depth = (ch % CH_PER) * 20.0
        is_bad = np.array([c in bad for c in ch])
        rms_good = np.where(is_bad, np.nan, rms)
        peak = int(np.nanargmax(rms_good))
        results[name] = dict(detection_channel=det.get(name), peak_channel=peak,
                             peak_section=int(section[peak]), peak_depth_um=float(depth[peak]),
                             det_on_peak=bool(det.get(name) == peak),
                             baseline_window_s=[round(b0, 1), round(b1, 1)])
        for c in ch:
            rows.append(dict(session=name, channel=int(c), shank_section=int(section[c]),
                             depth_um=float(depth[c]), ripple_band_rms=round(float(rms[c]), 3),
                             bad=bool(is_bad[c]), is_detection_channel=bool(det.get(name) == c)))

    pd.DataFrame(rows).to_csv(OUT / "ripple_localization_by_channel.csv", index=False)
    (OUT / "ripple_localization_summary.json").write_text(json.dumps(results, indent=2) + "\n")

    # ---- figure: section x depth heatmap + per-section depth profile, per session ----
    df = pd.DataFrame(rows)
    fig, axes = plt.subplots(2, 2, figsize=(13, 10), gridspec_kw=dict(height_ratios=[1.25, 1]))
    shank_cols = ["#2a6f97", "#e9c46a", "#8C1515", "#457b9d"]
    for j, name in enumerate(SESS):
        d = df[df.session == name]
        # normalize within session for the heatmap (relative profile)
        grid = np.full((CH_PER, N_SECTION), np.nan)
        for r in d.itertuples():
            grid[int(r.depth_um // 20), r.shank_section - 1] = r.ripple_band_rms
        vmax = np.nanpercentile(grid, 99)
        axh = axes[0][j]
        im = axh.imshow(grid, aspect="auto", origin="upper", cmap="magma", vmax=vmax,
                        extent=[0.5, N_SECTION + 0.5, CH_PER * 20, 0])
        pk = results[name]
        axh.scatter([pk["peak_section"]], [pk["peak_depth_um"]], s=240, facecolors="none",
                    edgecolors="cyan", linewidths=2.2, label="ripple-band peak")
        det_ch = pk["detection_channel"]
        axh.scatter([1 + det_ch // CH_PER], [(det_ch % CH_PER) * 20], marker="*", s=180,
                    c="white", edgecolors="k", linewidths=0.6, label="detection channel")
        axh.set_xticks(range(1, N_SECTION + 1)); axh.set_xlabel("dHPC section")
        axh.set_ylabel("depth in section (µm)")
        axh.set_title(f"{name}: ripple-band (100–250 Hz) power\npeak section {pk['peak_section']} @ {pk['peak_depth_um']:.0f} µm"
                      + ("  (= detection ch)" if pk["det_on_peak"] else ""))
        axh.legend(fontsize=8, loc="lower right")
        fig.colorbar(im, ax=axh, fraction=0.046, pad=0.02, label="ripple-band RMS (µV)")
        # depth profiles per section
        axp = axes[1][j]
        for sh in range(1, N_SECTION + 1):
            ds = d[d.shank_section == sh].sort_values("depth_um")
            axp.plot(ds.ripple_band_rms, ds.depth_um, color=shank_cols[sh - 1], lw=1.8, label=f"section {sh}")
            badpts = ds[ds.bad]
            axp.scatter(badpts.ripple_band_rms, badpts.depth_um, s=14, c="#bbb", zorder=2)
        axp.scatter([d[d.channel == det_ch].ripple_band_rms.iloc[0]], [(det_ch % CH_PER) * 20],
                    marker="*", s=180, c="k", zorder=5)
        axp.invert_yaxis(); axp.set_xlabel("ripple-band RMS (µV)"); axp.set_ylabel("depth (µm)")
        axp.set_title(f"{name}: depth profile by section (grey = bad ch)"); axp.legend(fontsize=8)
        axp.grid(alpha=0.2)

    fig.suptitle("Where dHPC ripple power lives — ripple-band (100–250 Hz) profile across 4 XML sections\n"
                 "the data-driven detection channel sits on the focal ripple-band peak (CA1-like, not histology-confirmed)",
                 fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT / "ripple_localization_by_shank.png", dpi=160); plt.close(fig)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
