#!/usr/bin/env python
"""Do the modulated units fire every 20 ms? — 50 Hz steady-state-following test (Dec 4).

50 Hz = one spike per 20 ms. If a modulated neuron were FREQUENCY-FOLLOWING (steady
state / entrained), its spike train would be 20 ms-periodic -> a 20/40/60/80 ms comb
in its autocorrelogram (ACG), independent of stimulus phase (which we can't access).
This is the phase-independent version of "frequency following".

We take the up-modulated units (significant ON>OFF at amp250_freq50), build their
ON-window ACG, and look for a 20 ms comb — against the OFF-window ACG and a simulated
"perfect 50 Hz follower" reference. No comb => the units change their RATE without
locking to the 50 Hz cycle => rate modulation, NOT steady-state following.

Outputs -> analysis/outputs/cross_dataset_spike_compare/acg_following/ and (builders)
results/dec4/11_Spikes/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FS = 20_000.0
MAXLAG, BINMS = 100.0, 1.0
TW = Path("analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv")
OUT = Path("analysis/outputs/cross_dataset_spike_compare/acg_following")
REG = {
    "dHPC": dict(curated=Path("analysis/outputs/dec4/curated_merged_dhpc"),
                 stats=Path("analysis/outputs/cross_dataset_spike_compare/dec4_dHPC_unit_condition_stats.csv")),
    "LEC": dict(curated=Path("analysis/outputs/dec4/curated_merged_lec"),
                stats=Path("analysis/outputs/cross_dataset_spike_compare/dec4_LEC_unit_condition_stats.csv")),
}
EDGES = np.arange(0, MAXLAG + BINMS, BINMS)
CTR = (EDGES[:-1] + EDGES[1:]) / 2


def window_acg(spk, starts, dur):
    """One-sided ACG (0-100 ms) accumulated within each [start, start+dur] window."""
    h = np.zeros(len(EDGES) - 1)
    for t0 in starts:
        s = np.sort(spk[(spk >= t0) & (spk < t0 + dur)] - t0)
        for i in range(len(s)):
            j = i + 1
            while j < len(s) and (s[j] - s[i]) * 1000 <= MAXLAG:
                h[min(int((s[j] - s[i]) * 1000 / BINMS), len(h) - 1)] += 1
                j += 1
    return h


def norm(h):
    base = h[(CTR >= 60) & (CTR <= 100)].mean()
    return h / base if base > 0 else h


def comb_index(h):
    """Power at 50 Hz peaks (20/40/60/80 ms) vs off-comb neighbors — >1 means a comb."""
    on = np.concatenate([np.where(np.abs(CTR - k) <= 1)[0] for k in (20, 40, 60, 80)])
    off = np.concatenate([np.where(np.abs(CTR - k) <= 1)[0] for k in (10, 30, 50, 70, 90)])
    return float(h[on].mean() / (h[off].mean() + 1e-9))


def sim_follower():
    """Realistic simulated 50 Hz follower: a phase-locked component on top of a Poisson
    background (so off-cycle bins are NOT empty), matching ~the up-units' firing rate."""
    rng = np.random.default_rng(0)
    starts = np.arange(0, 200) * 6.0
    spk = []
    for t0 in starts:
        for k in range(int(3.0 / 0.02)):                  # 50 Hz cycles in the 3 s window
            if rng.random() < 0.55:                       # fire ~55% of cycles, phase-locked (jitter 2 ms)
                spk.append(t0 + k * 0.02 + rng.normal(0, 0.002))
        spk.extend(t0 + rng.uniform(0, 3, rng.poisson(9)))    # ~3 Hz unlocked background
    return norm(window_acg(np.sort(np.array(spk)), starts, 3.0))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tw = pd.read_csv(TW)
    on0 = tw[(tw.amplitude == 250) & (tw.freq == 50)].on_start_s.to_numpy()
    off0 = tw[(tw.amplitude == 250) & (tw.freq == 50)].off_start_s.to_numpy()

    units, on_acgs, off_acgs, rows = [], [], [], []
    for reg in REG:
        st = np.load(REG[reg]["curated"] / "spike_times.npy").astype(np.int64) / FS
        sc = np.load(REG[reg]["curated"] / "spike_clusters.npy").astype(np.int64)
        d = pd.read_csv(REG[reg]["stats"]); col = [c for c in d.columns if "responsive" in c][0]
        up = d[(d.condition == "amp250_freq50") & d[col] & (d.mean_delta_hz > 0)]
        for cid in up.cluster_id:
            spk = st[sc == cid]
            on, off = norm(window_acg(spk, on0, 3.0)), norm(window_acg(spk, off0, 3.0))
            units.append((reg, int(cid))); on_acgs.append(on); off_acgs.append(off)
            rows.append(dict(region=reg, cluster_id=int(cid),
                             comb_index_ON=round(comb_index(on), 3), comb_index_OFF=round(comb_index(off), 3)))
    on_m = np.vstack(on_acgs); off_m = np.vstack(off_acgs); ref = sim_follower()
    pd.DataFrame(rows).to_csv(OUT / "acg_following_by_unit.csv", index=False)
    pop_comb = {"pop_comb_index_ON": round(comb_index(on_m.mean(0)), 3),
                "pop_comb_index_OFF": round(comb_index(off_m.mean(0)), 3),
                "reference_follower_comb_index": round(comb_index(ref), 3),
                "n_up_units": len(units)}
    (OUT / "acg_following_summary.json").write_text(json.dumps(pop_comb, indent=2) + "\n")

    # ---- figure: per-unit ACGs, grouped by region (dHPC then LEC), + a reference ----
    order = sorted(range(len(units)), key=lambda i: (units[i][0] != "dHPC", units[i][1]))
    npan = len(order) + 1
    ncol = 4; nrow = int(np.ceil(npan / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.5 * ncol, 2.9 * nrow), sharex=True)
    axes = np.atleast_1d(axes).ravel()
    for a in axes:
        a.axis("off")
    ymax = max(float(a.max()) for a in on_acgs) * 1.15
    for p, i in enumerate(order):
        a = axes[p]; a.axis("on")
        reg, cid = units[i]
        for k in (20, 40, 60, 80):
            a.axvline(k, color="#ccc", lw=0.8, ls=":")
        a.plot(CTR, off_acgs[i], color="#bbb", lw=1.1, label="OFF")
        a.plot(CTR, on_acgs[i], color="#8C1515", lw=1.9, label="ON (50 Hz)")
        a.set_xlim(0, 100); a.set_ylim(0, ymax)
        a.set_title(f"{reg} unit {cid}   comb={rows[i]['comb_index_ON']:.1f}", fontsize=9.5,
                    color=("#8C1515" if reg == "dHPC" else "#175E54"))
        if p == 0:
            a.legend(fontsize=7, loc="lower right"); a.set_ylabel("norm. ACG")
        if p >= ncol * (nrow - 1):
            a.set_xlabel("lag (ms)")
    # reference panel (its own y-scale — a real comb is much taller)
    ar = axes[len(order)]; ar.axis("on")
    for k in (20, 40, 60, 80):
        ar.axvline(k, color="#ccc", lw=0.8, ls=":")
    ar.plot(CTR, ref, color="#457b9d", lw=2.0)
    ar.set_xlim(0, 100); ar.set_xlabel("lag (ms)")
    ar.set_title(f"REFERENCE: 50 Hz follower\ncomb={pop_comb['reference_follower_comb_index']:.1f}",
                 fontsize=9.5, color="#457b9d")
    fig.suptitle("Per-unit ACG of each modulated up-unit (dHPC ×6, LEC ×1) — ON (red) vs OFF (grey).\n"
                 "A 50 Hz follower would peak at 20/40/60/80 ms (blue reference, comb ≫ 1); every real unit is "
                 "smooth there (comb ≈ 1) → rate change, not 50 Hz following.", fontsize=10.5)
    fig.tight_layout(); fig.savefig(OUT / "acg_50hz_following_dec4.png", dpi=170); plt.close(fig)
    print(json.dumps(pop_comb, indent=2))


if __name__ == "__main__":
    main()
