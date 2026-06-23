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

Tests are Mann-Whitney U (unpaired; firing rates are non-normal), BH-corrected
within each dataset x comparison family. Outputs land in
analysis/outputs/cross_dataset_spike_compare/baseline_poststudy/.
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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    overview = []
    long_rows = []        # per-unit per-comparison (incl. per-condition)
    wide_frames = []

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

        wide = []
        # collect p-values per comparison family for BH within this dataset
        fam = {"ON_all_vs_baseline": [], "OFF_all_vs_baseline": [], "post_vs_baseline": [],
               "ON_vs_baseline": [], "OFF_vs_baseline": []}
        fam_rowidx = {k: [] for k in fam}

        for cid in good_ids:
            base = bl_rate[:, cid]; post = po_rate[:, cid]
            on_all = on_rate[:, cid]; off_all = off_rate[:, cid]
            base_mean = float(base.mean()); base_sd = float(base.std(ddof=1)) if len(base) > 1 else np.nan
            post_mean = float(post.mean())
            drift_pct = float(100 * (post_mean - base_mean) / base_mean) if base_mean > 0 else np.nan

            wide.append({
                "dataset": name, "cluster_id": int(cid),
                "baseline_hz": round(base_mean, 4), "baseline_sd_hz": round(base_sd, 4),
                "post_hz": round(post_mean, 4),
                "on_all_hz": round(float(on_all.mean()), 4),
                "off_all_hz": round(float(off_all.mean()), 4),
                "off_minus_baseline_hz": round(float(off_all.mean()) - base_mean, 4),
                "on_minus_baseline_hz": round(float(on_all.mean()) - base_mean, 4),
                "post_minus_baseline_hz": round(post_mean - base_mean, 4),
                "drift_post_vs_base_pct": round(drift_pct, 1) if np.isfinite(drift_pct) else np.nan,
                "n_baseline_epochs": int(len(base)), "n_post_epochs": int(len(post)),
            })

            # pooled (all-condition) tests
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

            # per-condition ON-vs-baseline and OFF-vs-baseline
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

        # BH within each (dataset, family)
        for famkey, ps in fam.items():
            if not ps:
                continue
            q = benjamini_hochberg(np.asarray(ps))
            for ridx, qv in zip(fam_rowidx[famkey], q):
                long_rows[ridx]["q_value_bh"] = float(qv)

        wide_df = pd.DataFrame(wide)
        wide_frames.append(wide_df)

        # ---- dataset-level summary ----
        n = len(good_ids)
        off_base = wide_df["off_minus_baseline_hz"]
        post_base = wide_df["post_minus_baseline_hz"]
        # how many units have OFF significantly != baseline (pooled), and post != baseline
        ld = pd.DataFrame(long_rows)
        ld = ld[ld["dataset"] == name]
        off_sig = ld[(ld["comparison"] == "OFF_all_vs_baseline")]
        post_sig = ld[(ld["comparison"] == "post_vs_baseline")]
        n_off_ne_base = int((off_sig["q_value_bh"] < 0.05).sum())
        n_post_ne_base = int((post_sig["q_value_bh"] < 0.05).sum())
        overview.append({
            "dataset": name, "n_curated_good": int(n),
            "mean_baseline_hz": round(float(wide_df["baseline_hz"].mean()), 3),
            "mean_off_hz": round(float(wide_df["off_all_hz"].mean()), 3),
            "mean_on_hz": round(float(wide_df["on_all_hz"].mean()), 3),
            "mean_post_hz": round(float(wide_df["post_hz"].mean()), 3),
            "mean_OFF_minus_base_hz": round(float(off_base.mean()), 3),
            "mean_post_minus_base_hz": round(float(post_base.mean()), 3),
            "n_units_OFF_ne_baseline_q05": n_off_ne_base,
            "n_units_post_ne_baseline_q05": n_post_ne_base,
            "baseline_window_s": [round(bl_start, 1), round(bl_end, 1)],
            "post_window_s": [round(po_start, 1), round(po_end, 1)],
            "n_baseline_epochs": int(len(bl_s)), "n_post_epochs": int(len(po_s)),
        })

        _plot_dataset(name, wide_df, OUT)

    wide_all = pd.concat(wide_frames, ignore_index=True)
    long_all = pd.DataFrame(long_rows)
    wide_all.to_csv(OUT / "state_rates_by_unit.csv", index=False)
    long_all.to_csv(OUT / "state_comparisons_long.csv", index=False)
    ov = pd.DataFrame(overview)
    ov.to_csv(OUT / "state_overview.csv", index=False)
    (OUT / "state_overview.json").write_text(json.dumps(overview, indent=2) + "\n")

    _plot_overview_states(wide_all, OUT)
    _plot_50hz_vs_baseline(long_all, OUT)

    print("=== Single-unit firing vs baseline & post-study ===")
    print(ov.to_string(index=False))


def _plot_dataset(name: str, wide: pd.DataFrame, out: Path) -> None:
    """Per-unit baseline/ON/OFF/post rates + OFF-vs-baseline scatter."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    # (a) population: paired lines baseline -> ON -> OFF -> post for each unit
    ax = axes[0]
    states = ["baseline_hz", "on_all_hz", "off_all_hz", "post_hz"]
    labels = ["baseline", "ON (all)", "OFF (all)", "post"]
    X = np.arange(4)
    for _, r in wide.iterrows():
        ax.plot(X, [r[s] for s in states], color="#999", lw=0.7, alpha=0.5, marker="o", ms=3)
    ax.plot(X, [wide[s].mean() for s in states], color="#264653", lw=2.6, marker="o",
            ms=8, label="mean", zorder=5)
    ax.set_xticks(X); ax.set_xticklabels(labels)
    ax.set_ylabel("Firing rate (Hz)")
    ax.set_title(f"{name}: per-unit rate by state")
    ax.legend()
    # (b) OFF vs baseline scatter (is OFF back at baseline?)
    ax = axes[1]
    lim = float(max(wide["baseline_hz"].max(), wide["off_all_hz"].max())) * 1.1 + 0.1
    ax.plot([0, lim], [0, lim], color="#d1495b", ls="--", lw=1, label="OFF = baseline")
    ax.scatter(wide["baseline_hz"], wide["off_all_hz"], color="#264653", s=28, alpha=0.8)
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.set_xlabel("Baseline rate (Hz)"); ax.set_ylabel("OFF-window rate (Hz)")
    ax.set_title(f"{name}: OFF vs true baseline")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / f"{name}_state_rates.png", dpi=170)
    plt.close(fig)


def _plot_overview_states(wide: pd.DataFrame, out: Path) -> None:
    """One panel per dataset: mean+-sem unit rate in each state, baseline-referenced."""
    datasets = ["dec3_dHPC", "dec4_dHPC", "dec4_LEC"]
    states = ["baseline_hz", "on_all_hz", "off_all_hz", "post_hz"]
    labels = ["baseline", "ON", "OFF", "post"]
    colors = ["#6c757d", "#d1495b", "#e9c46a", "#457b9d"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    for ax, ds in zip(axes, datasets):
        g = wide[wide["dataset"] == ds]
        means = [g[s].mean() for s in states]
        sems = [stats.sem(g[s]) for s in states]
        ax.bar(np.arange(4), means, yerr=sems, color=colors, alpha=0.92)
        ax.axhline(means[0], color="#6c757d", ls="--", lw=1)
        ax.set_xticks(np.arange(4)); ax.set_xticklabels(labels)
        drift = 100 * (means[3] - means[0]) / means[0]
        ax.set_title(f"{ds}  (n={len(g)})\nsession drift base→post {drift:+.0f}%")
        ax.set_ylabel("Mean unit firing rate (Hz)")
    fig.suptitle("Single-unit firing by state — ON/OFF referenced to true pre-experiment baseline & post-study",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(out / "overview_states_by_dataset.png", dpi=170)
    plt.close(fig)


def _plot_50hz_vs_baseline(ld: pd.DataFrame, out: Path) -> None:
    """Dec4 dHPC & LEC: ON and OFF firing change FROM baseline at each 50 Hz amplitude."""
    amps = ["amp100_freq50", "amp180_freq50", "amp250_freq50"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    for ax, ds in zip(axes, ["dec4_dHPC", "dec4_LEC"]):
        on_d, on_e, off_d, off_e = [], [], [], []
        for a in amps:
            on = ld[(ld.dataset == ds) & (ld.comparison == "ON_vs_baseline") & (ld.condition == a)]["delta_hz"]
            off = ld[(ld.dataset == ds) & (ld.comparison == "OFF_vs_baseline") & (ld.condition == a)]["delta_hz"]
            on_d.append(on.mean()); on_e.append(stats.sem(on))
            off_d.append(off.mean()); off_e.append(stats.sem(off))
        x = np.arange(3); w = 0.38
        ax.bar(x - w / 2, on_d, w, yerr=on_e, label="ON − baseline", color="#d1495b")
        ax.bar(x + w / 2, off_d, w, yerr=off_e, label="OFF − baseline", color="#e9c46a")
        ax.axhline(0, color="black", lw=1)
        ax.set_xticks(x); ax.set_xticklabels(["amp100", "amp180", "amp250"])
        ax.set_title(f"{ds}: 50 Hz drive vs true baseline")
        ax.set_xlabel("amplitude")
        ax.legend()
    axes[0].set_ylabel("Firing change from baseline (Hz)")
    fig.suptitle("50 Hz single-unit response referenced to baseline — dHPC drives UP, LEC suppressed (carry-over into OFF)",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(out / "freq50_vs_baseline_dec4.png", dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()
