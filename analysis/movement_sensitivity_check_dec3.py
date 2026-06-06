#!/usr/bin/env python3
"""Sensitivity check: do the headline results survive excluding movement trials?

Recomputes the spike ON-vs-OFF result (KS-good units) and the within-trial
broadband LFP result (OFF-control), once with ALL trials and once with the
EMG-flagged movement trials removed, and compares. Uses saved per-trial counts /
metrics, so no re-sorting or LFP re-read.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

BASE = Path("analysis/outputs/dec3")
OUT = BASE / "movement"
COND_ORDER = ["amp250_freq26", "amp180_freq26", "amp100_freq26",
              "amp250_freq5", "amp180_freq5", "amp100_freq5"]


def bh(p):
    p = np.asarray(p, float); q = np.full_like(p, np.nan)
    fin = np.isfinite(p); idx = np.where(fin)[0]; order = idx[np.argsort(p[fin])]
    n = len(order); adj = p[order] * n / np.arange(1, n + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]; q[order] = np.minimum(adj, 1.0); return q


def spike_sensitivity(keep, tw, on_rate, off_rate, good_cols):
    rows = []
    for cond in COND_ORDER:
        idx = np.where((tw.condition.values == cond) & keep)[0]
        for cl in good_cols:
            on, off = on_rate[idx, cl], off_rate[idx, cl]
            d = on - off
            p = 1.0 if np.allclose(d, d[0]) else stats.ttest_rel(on, off).pvalue
            rows.append((cl, cond, float(np.mean(d)), float(p)))
    df = pd.DataFrame(rows, columns=["cl", "condition", "delta", "p"])
    df["q"] = bh(df.p.values)
    summ = df.groupby("condition").agg(mean_unit_delta_hz=("delta", "mean"),
                                       n_responsive_q05=("q", lambda x: int((x < 0.05).sum()))).reindex(COND_ORDER)
    return summ, int((df.q < 0.05).sum())


def main():
    mv = pd.read_csv(OUT / "movement_raw_per_trial.csv")[["trial_number", "moving"]]
    tw = pd.read_csv(BASE / "spike_sorting_prep/trial_windows.csv").reset_index(drop=True)
    tw = tw.merge(mv, on="trial_number", how="left")
    tw["moving"] = tw["moving"].fillna(False)
    keep_all = np.ones(len(tw), bool); keep_excl = ~tw.moving.values
    n_excl = int(tw.moving.sum())

    # ---- spikes (KS-good) ----
    on = np.load(BASE / "spike_peth_on_off/on_counts_by_trial_unit.npy") / 3.0
    off = np.load(BASE / "spike_peth_on_off/off_counts_by_trial_unit.npy") / 3.0
    meta = pd.read_csv(BASE / "spike_peth_on_off/cluster_metadata.csv")
    good_cols = meta.loc[meta.is_ks_good, "cluster_id"].astype(int).to_numpy()
    sp_all, nr_all = spike_sensitivity(keep_all, tw, on, off, good_cols)
    sp_ex, nr_ex = spike_sensitivity(keep_excl, tw, on, off, good_cols)

    # ---- LFP within-trial broadband (OFF-control), ON-minus-OFF per trial, mean over groups ----
    lm = pd.read_csv(BASE / "off_control_broadband/off_control_trial_metrics.csv")
    lm = lm.groupby(["trial_number", "condition"], as_index=False)["on_minus_off"].mean()
    lm = lm.merge(mv, on="trial_number", how="left"); lm["moving"] = lm["moving"].fillna(False)
    lfp_all = lm.groupby("condition")["on_minus_off"].mean().reindex(COND_ORDER)
    lfp_ex = lm[~lm.moving].groupby("condition")["on_minus_off"].mean().reindex(COND_ORDER)

    # ---- table ----
    tbl = pd.DataFrame({
        "spike_delta_all": sp_all.mean_unit_delta_hz, "spike_delta_excl": sp_ex.mean_unit_delta_hz,
        "spike_nResp_all": sp_all.n_responsive_q05, "spike_nResp_excl": sp_ex.n_responsive_q05,
        "lfp_ONminusOFF_all": lfp_all, "lfp_ONminusOFF_excl": lfp_ex,
    }).round(3)
    tbl.to_csv(OUT / "movement_sensitivity_by_condition.csv")
    print(f"Excluded {n_excl} movement trials (of 1200).  KS-good units: {len(good_cols)}")
    print(f"Total responsive units (q<0.05):  ALL={nr_all}   EXCLUDED={nr_ex}")
    print(tbl.to_string())

    # ---- figure ----
    fig, ax = plt.subplots(1, 2, figsize=(14, 5)); x = np.arange(len(COND_ORDER)); w = 0.38
    ax[0].bar(x - w/2, sp_all.mean_unit_delta_hz, w, label="all trials", color="#7f8c8d")
    ax[0].bar(x + w/2, sp_ex.mean_unit_delta_hz, w, label=f"excl. {n_excl} movement", color="#2a9d8f")
    ax[0].axhline(0, color="k", lw=0.8); ax[0].set_xticks(x); ax[0].set_xticklabels(COND_ORDER, rotation=40, ha="right", fontsize=8)
    ax[0].set_ylabel("mean KS-good unit ON-OFF (Hz)")
    ax[0].set_title(f"Spikes: ON-OFF firing (responsive q<0.05: all={nr_all}, excl={nr_ex})"); ax[0].legend(fontsize=8); ax[0].grid(axis="y", alpha=0.2)
    ax[1].bar(x - w/2, lfp_all, w, label="all trials", color="#7f8c8d")
    ax[1].bar(x + w/2, lfp_ex, w, label=f"excl. {n_excl} movement", color="#c0392b")
    ax[1].axhline(0, color="k", lw=0.8); ax[1].set_xticks(x); ax[1].set_xticklabels(COND_ORDER, rotation=40, ha="right", fontsize=8)
    ax[1].set_ylabel("within-trial ON-OFF mean |LFP|")
    ax[1].set_title("LFP broadband: ON vs within-trial OFF"); ax[1].legend(fontsize=8); ax[1].grid(axis="y", alpha=0.2)
    fig.suptitle("Movement sensitivity: headline results, all trials vs movement-excluded", fontweight="bold")
    fig.tight_layout(); fig.savefig(OUT / "movement_sensitivity.png", dpi=150); plt.close(fig)

    (OUT / "movement_sensitivity_summary.json").write_text(json.dumps({
        "n_movement_excluded": n_excl, "n_ks_good_units": len(good_cols),
        "responsive_q05_all": nr_all, "responsive_q05_excluded": nr_ex,
        "spike_delta_corr": float(np.corrcoef(sp_all.mean_unit_delta_hz, sp_ex.mean_unit_delta_hz)[0, 1]),
        "lfp_delta_corr": float(np.corrcoef(lfp_all, lfp_ex)[0, 1]),
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
