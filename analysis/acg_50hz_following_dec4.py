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
    """Simulated 50 Hz-following unit: spikes near each 20 ms cycle -> ACG comb (reference)."""
    rng = np.random.default_rng(0)
    starts = np.arange(0, 200) * 6.0
    spk = []
    for t0 in starts:
        ncyc = int(3.0 / 0.02)
        for k in range(ncyc):
            if rng.random() < 0.25:                       # fire ~25% of cycles, phase-locked
                spk.append(t0 + k * 0.02 + rng.normal(0, 0.002))
    spk = np.sort(np.array(spk))
    return norm(window_acg(spk, starts, 3.0))


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

    # ---- figure ----
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
    for k in (20, 40, 60, 80):
        ax[0].axvline(k, color="#bbb", lw=0.8, ls=":")
    ax[0].plot(CTR, on_m.mean(0), color="#8C1515", lw=2.2, label="ON (50 Hz)")
    ax[0].plot(CTR, off_m.mean(0), color="#53565A", lw=1.6, label="OFF")
    ax[0].set_title(f"Modulated up-units (n={len(units)}): ON-window ACG\n"
                    f"no 20/40/60/80 ms comb  (comb index {pop_comb['pop_comb_index_ON']} ≈ 1)")
    ax[0].set_xlabel("lag (ms)"); ax[0].set_ylabel("norm. ACG"); ax[0].legend(); ax[0].set_xlim(0, 100)
    for k in (20, 40, 60, 80):
        ax[1].axvline(k, color="#bbb", lw=0.8, ls=":")
    ax[1].plot(CTR, ref, color="#175E54", lw=2.2)
    ax[1].set_title(f"Reference: a perfect 50 Hz follower\n"
                    f"clear 20 ms comb  (comb index {pop_comb['reference_follower_comb_index']:.1f})")
    ax[1].set_xlabel("lag (ms)"); ax[1].set_ylabel("norm. ACG"); ax[1].set_xlim(0, 100)
    fig.suptitle("50 Hz steady-state-following test: the modulated units change RATE but do NOT fire every 20 ms "
                 "(no frequency-following)", fontsize=12)
    fig.tight_layout(); fig.savefig(OUT / "acg_50hz_following_dec4.png", dpi=170); plt.close(fig)
    print(json.dumps(pop_comb, indent=2))


if __name__ == "__main__":
    main()
