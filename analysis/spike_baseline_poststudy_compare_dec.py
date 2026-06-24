#!/usr/bin/env python
"""Single-unit firing vs TRUE baseline & post-study references (Dec 3 + Dec 4).

The existing ON/OFF analysis ([spike_curated_compare_dec.py]) contrasts each 3 s
ON window with the immediately-following 3 s OFF window. That OFF window is *not*
a neutral baseline — it can carry sustained / rebound effects of the buzz. This
script adds the two missing reference states that bracket the protocol:

  * PRE-experiment BASELINE  — quiet recording before the first trial
  * POST-study               — quiet recording after the last trial

Both are tiled into 3 s epochs (same length as ON/OFF) so firing rates are
directly comparable in Hz. For every curated 'good' unit we then ask:

  1. ON   vs baseline   — is the ON effect a real rise/fall ABOVE baseline?
  2. OFF  vs baseline   — is the OFF window actually back at baseline, or still
                          modulated (carry-over)?  -> validates the ON/OFF control
  3. post vs baseline   — session-long DRIFT control: did firing return to
                          baseline after the whole study?

Two inferential layers:
  * per-unit  : Mann-Whitney U (unpaired), BH-corrected within dataset x family.
  * population: PERCENTILE BOOTSTRAP 95% CIs (resampling the units, B=10000) on
                every population mean / delta — these are the error bars on the
                figures and the CIs in population_bootstrap.csv.

Result figures (-> results/dec*/11_Spikes via the manifest builders):
  dec3_states_vs_baseline.png, dec4_states_vs_baseline.png,
  dec4_freq50_vs_baseline.png
Outputs land in analysis/outputs/cross_dataset_spike_compare/baseline_poststudy/.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from spike_peth_on_off_dec3 import count_intervals, load_sorted_spikes, benjamini_hochberg

FS = 20_000.0
WIN = 3.0                 # epoch length (s) — matches ON/OFF window
START_MARGIN = 60.0       # skip first 60 s (amplifier/probe settling)
GAP = 30.0                # gap between baseline/post and the nearest trial
END_MARGIN = 30.0         # skip last 30 s (end-of-file effects)
B_BOOT = 10_000           # bootstrap resamples
RNG = np.random.default_rng(0)

CARD, GOLD, GREY, BLUE = "#d1495b", "#e9c46a", "#6c757d", "#457b9d"

# (name, curated kilosort dir, trial windows csv, dir holding on/off count npys)
DATASETS = [
    ("dec3_dHPC", "analysis/outputs/dec3/curated_merged",
     "analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv",
     "analysis/outputs/dec3/spike_peth_on_off"),
    ("dec4_dHPC", "analysis/outputs/dec4/curated_merged_dhpc",
     "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv",
     "analysis/outputs/dec4/spike_peth_on_off_dhpc"),
    ("dec4_LEC", "analysis/outputs/dec4/curated_merged_lec",
     "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv",
     "analysis/outputs/dec4/spike_peth_on_off_lec"),
]
OUT = Path("analysis/outputs/cross_dataset_spike_compare/baseline_poststudy")


def tile_epochs(t0: float, t1: float, win: float) -> tuple[np.ndarray, np.ndarray]:
    """Consecutive non-overlapping win-second epochs spanning [t0, t1]."""
    n = int(np.floor((t1 - t0) / win))
    if n <= 0:
        return np.empty(0), np.empty(0)
    starts = t0 + np.arange(n) * win
    return starts, starts + win


def mwu(a: np.ndarray, b: np.ndarray) -> float:
    """Mann-Whitney U p-value (two-sided); 1.0 if degenerate."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 2 or len(b) < 2 or (np.ptp(a) == 0 and np.ptp(b) == 0 and a[0] == b[0]):
        return 1.0
    try:
        return float(stats.mannwhitneyu(a, b, alternative="two-sided").pvalue)
    except ValueError:
        return 1.0


def boot_ci(values: np.ndarray, b: int = B_BOOT, alpha: float = 0.05) -> tuple[float, float, float]:
    """Percentile bootstrap of the MEAN of `values` (resampling units)."""
    v = np.asarray(values, float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return (np.nan, np.nan, np.nan)
    if len(v) == 1:
        return (float(v[0]), float(v[0]), float(v[0]))
    idx = RNG.integers(0, len(v), size=(b, len(v)))
    means = v[idx].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return (float(v.mean()), float(lo), float(hi))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    overview = []
    long_rows = []          # per-unit per-comparison (incl. per-condition)
    boot_rows = []          # population bootstrap CIs
    wide_frames = []
    perunit = {}            # name -> dict of per-unit state vectors (for figures)

    for name, ksdir, tw_csv, peth in DATASETS:
        ksdir = Path(ksdir); peth = Path(peth)
        spike_t, spike_c, n_clusters = load_sorted_spikes(ksdir, FS)
        good = pd.read_csv(ksdir / "cluster_group.tsv", sep="\t")
        good_ids = good.loc[good["group"] == "good", "cluster_id"].to_numpy(int)
        tw = pd.read_csv(tw_csv)

        first_on = float(tw["on_start_s"].min())
        last_off = float(tw["off_end_s"].max())
        rec_end = float(spike_t.max())

        bl_start, bl_end = START_MARGIN, first_on - GAP
        po_start, po_end = last_off + GAP, rec_end - END_MARGIN
        bl_s, bl_e = tile_epochs(bl_start, bl_end, WIN)
        po_s, po_e = tile_epochs(po_start, po_end, WIN)

        # per-epoch per-unit rates (Hz) for the two reference states
        bl_rate = count_intervals(spike_t, spike_c, bl_s, bl_e, n_clusters) / WIN
        po_rate = count_intervals(spike_t, spike_c, po_s, po_e, n_clusters) / WIN

        # existing per-trial ON/OFF counts -> rates; rows align with tw order
        on_rate = np.load(peth / "on_counts_by_trial_unit.npy") / WIN
        off_rate = np.load(peth / "off_counts_by_trial_unit.npy") / WIN
        cond_of_trial = tw["condition"].to_numpy()
        conditions = sorted(tw["condition"].unique())

        # ---- per-unit mean rates (vectors over good units) for population stats ----
        g = good_ids
        base_u = bl_rate[:, g].mean(0)
        post_u = po_rate[:, g].mean(0)
        on_u = on_rate[:, g].mean(0)
        off_u = off_rate[:, g].mean(0)
        perunit[name] = dict(baseline=base_u, on=on_u, off=off_u, post=post_u)

        # ---- per-unit table + per-unit Mann-Whitney comparisons ----
        wide = []
        fam = {"ON_all_vs_baseline": [], "OFF_all_vs_baseline": [], "post_vs_baseline": [],
               "ON_vs_baseline": [], "OFF_vs_baseline": []}
        fam_rowidx = {k: [] for k in fam}

        for cid in good_ids:
            base = bl_rate[:, cid]; post = po_rate[:, cid]
            on_all = on_rate[:, cid]; off_all = off_rate[:, cid]
            base_mean = float(base.mean())
            wide.append({
                "dataset": name, "cluster_id": int(cid),
                "baseline_hz": round(base_mean, 4),
                "baseline_sd_hz": round(float(base.std(ddof=1)) if len(base) > 1 else np.nan, 4),
                "post_hz": round(float(post.mean()), 4),
                "on_all_hz": round(float(on_all.mean()), 4),
                "off_all_hz": round(float(off_all.mean()), 4),
                "off_minus_baseline_hz": round(float(off_all.mean()) - base_mean, 4),
                "on_minus_baseline_hz": round(float(on_all.mean()) - base_mean, 4),
                "post_minus_baseline_hz": round(float(post.mean()) - base_mean, 4),
                "n_baseline_epochs": int(len(base)), "n_post_epochs": int(len(post)),
            })
            for famkey, vec in (("ON_all_vs_baseline", on_all),
                                ("OFF_all_vs_baseline", off_all),
                                ("post_vs_baseline", post)):
                p = mwu(vec, base)
                long_rows.append({"dataset": name, "cluster_id": int(cid),
                                  "comparison": famkey, "condition": "(all)",
                                  "ref_hz": round(base_mean, 4),
                                  "test_hz": round(float(np.mean(vec)), 4),
                                  "delta_hz": round(float(np.mean(vec)) - base_mean, 4),
                                  "p_value": p})
                fam[famkey].append(p); fam_rowidx[famkey].append(len(long_rows) - 1)
            for cond in conditions:
                m = cond_of_trial == cond
                for famkey, vec in (("ON_vs_baseline", on_rate[m, cid]),
                                    ("OFF_vs_baseline", off_rate[m, cid])):
                    p = mwu(vec, base)
                    long_rows.append({"dataset": name, "cluster_id": int(cid),
                                      "comparison": famkey, "condition": cond,
                                      "ref_hz": round(base_mean, 4),
                                      "test_hz": round(float(np.mean(vec)), 4),
                                      "delta_hz": round(float(np.mean(vec)) - base_mean, 4),
                                      "p_value": p})
                    fam[famkey].append(p); fam_rowidx[famkey].append(len(long_rows) - 1)

        for famkey, ps in fam.items():
            if not ps:
                continue
            q = benjamini_hochberg(np.asarray(ps))
            for ridx, qv in zip(fam_rowidx[famkey], q):
                long_rows[ridx]["q_value_bh"] = float(qv)

        wide_df = pd.DataFrame(wide)
        wide_frames.append(wide_df)

        # ---- population BOOTSTRAP CIs (resampling units) ----
        def add_boot(quantity, vals, condition="(all)"):
            pt, lo, hi = boot_ci(vals)
            boot_rows.append({"dataset": name, "quantity": quantity, "condition": condition,
                              "mean": round(pt, 4), "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
                              "n_units": int(len(vals))})
            return pt, lo, hi

        add_boot("baseline_hz", base_u)
        add_boot("on_hz", on_u)
        add_boot("off_hz", off_u)
        add_boot("post_hz", post_u)
        _, dlo, dhi = add_boot("post_minus_baseline_hz", post_u - base_u)
        _, olo, ohi = add_boot("off_minus_baseline_hz", off_u - base_u)
        # per-condition ON/OFF minus baseline (for the 50 Hz figure & table)
        for cond in conditions:
            msk = cond_of_trial == cond
            on_c = on_rate[msk][:, g].mean(0)
            off_c = off_rate[msk][:, g].mean(0)
            add_boot("ON_minus_baseline_hz", on_c - base_u, condition=cond)
            add_boot("OFF_minus_baseline_hz", off_c - base_u, condition=cond)

        # ---- dataset summary (with bootstrap CI on the headline numbers) ----
        ld = pd.DataFrame(long_rows); ld = ld[ld["dataset"] == name]
        n_off_ne = int((ld[ld.comparison == "OFF_all_vs_baseline"]["q_value_bh"] < 0.05).sum())
        n_post_ne = int((ld[ld.comparison == "post_vs_baseline"]["q_value_bh"] < 0.05).sum())
        overview.append({
            "dataset": name, "n_curated_good": int(len(good_ids)),
            "mean_baseline_hz": round(float(base_u.mean()), 3),
            "mean_on_hz": round(float(on_u.mean()), 3),
            "mean_off_hz": round(float(off_u.mean()), 3),
            "mean_post_hz": round(float(post_u.mean()), 3),
            "drift_post_minus_base_hz": round(float((post_u - base_u).mean()), 3),
            "drift_ci95_hz": [round(dlo, 3), round(dhi, 3)],
            "drift_pct": round(100 * float((post_u - base_u).mean()) / float(base_u.mean()), 1),
            "OFF_minus_base_hz": round(float((off_u - base_u).mean()), 3),
            "OFF_minus_base_ci95_hz": [round(olo, 3), round(ohi, 3)],
            "n_units_OFF_ne_baseline_q05": n_off_ne,
            "n_units_post_ne_baseline_q05": n_post_ne,
            "baseline_window_s": [round(bl_start, 1), round(bl_end, 1)],
            "post_window_s": [round(po_start, 1), round(po_end, 1)],
            "n_baseline_epochs": int(len(bl_s)), "n_post_epochs": int(len(po_s)),
        })

    # ---- write tables ----
    pd.concat(wide_frames, ignore_index=True).to_csv(OUT / "state_rates_by_unit.csv", index=False)
    pd.DataFrame(long_rows).to_csv(OUT / "state_comparisons_long.csv", index=False)
    boot_df = pd.DataFrame(boot_rows)
    boot_df.to_csv(OUT / "population_bootstrap.csv", index=False)
    ov = pd.DataFrame(overview)
    ov.to_csv(OUT / "state_overview.csv", index=False)
    (OUT / "state_overview.json").write_text(json.dumps(overview, indent=2) + "\n")

    # ---- figures (bootstrap 95% CI error bars) ----
    _fig_states("dec3_states_vs_baseline.png", ["dec3_dHPC"], perunit, boot_df, OUT,
                "Dec 3 dHPC — single-unit firing vs true baseline & post-study (95% bootstrap CI)")
    _fig_states("dec4_states_vs_baseline.png", ["dec4_dHPC", "dec4_LEC"], perunit, boot_df, OUT,
                "Dec 4 — single-unit firing vs true baseline & post-study (95% bootstrap CI)")
    _fig_freq50("dec4_freq50_vs_baseline.png", ["dec4_dHPC", "dec4_LEC"], boot_df, OUT)

    print("=== Single-unit firing vs baseline & post-study (bootstrap CIs) ===")
    print(ov.to_string(index=False))


def _ci_err(boot_df, dataset, quantity, condition="(all)"):
    r = boot_df[(boot_df.dataset == dataset) & (boot_df.quantity == quantity)
                & (boot_df.condition == condition)]
    if r.empty:
        return np.nan, 0.0, 0.0
    m, lo, hi = float(r["mean"].iloc[0]), float(r.ci_lo.iloc[0]), float(r.ci_hi.iloc[0])
    return m, m - lo, hi - m


def _fig_states(fname, datasets, perunit, boot_df, out, suptitle):
    states = [("baseline_hz", "baseline", GREY), ("on_hz", "ON", CARD),
              ("off_hz", "OFF", GOLD), ("post_hz", "post", BLUE)]
    fig, axes = plt.subplots(1, len(datasets), figsize=(6.4 * len(datasets), 4.8), squeeze=False)
    for ax, ds in zip(axes[0], datasets):
        means, errlo, errhi, cols = [], [], [], []
        for q, _lab, col in states:
            m, elo, ehi = _ci_err(boot_df, ds, q)
            means.append(m); errlo.append(elo); errhi.append(ehi); cols.append(col)
        x = np.arange(4)
        ax.bar(x, means, yerr=[errlo, errhi], capsize=4, color=cols, alpha=0.92,
               error_kw=dict(ecolor="#222", lw=1.4))
        # overlay individual units (thin grey)
        pu = perunit[ds]
        for i, key in enumerate(["baseline", "on", "off", "post"]):
            ax.scatter(np.full_like(pu[key], x[i], dtype=float) + RNG.uniform(-0.12, 0.12, len(pu[key])),
                       pu[key], s=10, color="#999", alpha=0.5, zorder=3)
        ax.axhline(means[0], color=GREY, ls="--", lw=1)
        drift_m, _, _ = _ci_err(boot_df, ds, "post_minus_baseline_hz")
        ax.set_xticks(x); ax.set_xticklabels([s[1] for s in states])
        ax.set_ylabel("Mean unit firing rate (Hz)")
        ax.set_title(f"{ds}  (n={len(pu['baseline'])})   drift base→post {100*drift_m/means[0]:+.0f}%")
    fig.suptitle(suptitle, fontsize=12)
    fig.tight_layout()
    fig.savefig(out / fname, dpi=170)
    plt.close(fig)


def _fig_freq50(fname, datasets, boot_df, out):
    amps = ["amp100_freq50", "amp180_freq50", "amp250_freq50"]
    fig, axes = plt.subplots(1, len(datasets), figsize=(6.2 * len(datasets), 4.8),
                             sharey=True, squeeze=False)
    for ax, ds in zip(axes[0], datasets):
        x = np.arange(len(amps)); w = 0.38
        on_m = [_ci_err(boot_df, ds, "ON_minus_baseline_hz", a) for a in amps]
        off_m = [_ci_err(boot_df, ds, "OFF_minus_baseline_hz", a) for a in amps]
        ax.bar(x - w / 2, [m[0] for m in on_m], w,
               yerr=[[m[1] for m in on_m], [m[2] for m in on_m]], capsize=3,
               label="ON − baseline", color=CARD, error_kw=dict(ecolor="#222", lw=1.3))
        ax.bar(x + w / 2, [m[0] for m in off_m], w,
               yerr=[[m[1] for m in off_m], [m[2] for m in off_m]], capsize=3,
               label="OFF − baseline", color=GOLD, error_kw=dict(ecolor="#222", lw=1.3))
        ax.axhline(0, color="black", lw=1)
        ax.set_xticks(x); ax.set_xticklabels(["amp100", "amp180", "amp250"])
        ax.set_title(f"{ds}: 50 Hz drive vs true baseline"); ax.set_xlabel("amplitude")
        ax.legend()
    axes[0][0].set_ylabel("Firing change from baseline (Hz)")
    fig.suptitle("50 Hz single-unit response vs baseline (95% bootstrap CI) — "
                 "dHPC drives UP, LEC suppressed (carry-over into OFF)", fontsize=11.5)
    fig.tight_layout()
    fig.savefig(out / fname, dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()
