#!/usr/bin/env python
"""Compare Dec 3 spike ON/OFF effects for cleaner Kilosort unit sets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from spike_peth_on_off_dec3 import (
    benjamini_hochberg,
    plot_peth,
)


DEFAULT_SPIKE_PETH_DIR = Path("analysis/outputs/dec3/spike_peth_on_off")
DEFAULT_CLUSTER_QUALITY = Path("analysis/outputs/dec3/cluster_quality/cluster_quality_summary.csv")
DEFAULT_TRIAL_WINDOWS = Path("analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv")
DEFAULT_OUTPUT_DIR = Path("analysis/outputs/dec3/spike_peth_high_confidence")


def compute_subset_stats(
    trial_windows: pd.DataFrame,
    on_counts: np.ndarray,
    off_counts: np.ndarray,
    cluster_metadata: pd.DataFrame,
    cluster_ids: np.ndarray,
    unit_set: str,
) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    on_rate = on_counts[:, cluster_ids] / 3.0
    off_rate = off_counts[:, cluster_ids] / 3.0
    delta = on_rate - off_rate

    for condition, idx in trial_windows.groupby("condition", sort=True).groups.items():
        idx_arr = np.asarray(list(idx), dtype=int)
        for local_i, cluster_id in enumerate(cluster_ids):
            on_values = on_rate[idx_arr, local_i]
            off_values = off_rate[idx_arr, local_i]
            delta_values = delta[idx_arr, local_i]
            if np.allclose(delta_values, delta_values[0]):
                p_value = 1.0
                t_stat = 0.0
            else:
                t_stat, p_value = stats.ttest_rel(on_values, off_values, nan_policy="omit")
            rows.append(
                {
                    "unit_set": unit_set,
                    "cluster_id": int(cluster_id),
                    "condition": condition,
                    "n_trials": int(len(idx_arr)),
                    "mean_on_hz": float(np.mean(on_values)),
                    "mean_off_hz": float(np.mean(off_values)),
                    "mean_delta_hz": float(np.mean(delta_values)),
                    "sem_delta_hz": float(stats.sem(delta_values)) if len(delta_values) > 1 else np.nan,
                    "median_delta_hz": float(np.median(delta_values)),
                    "t_stat": float(t_stat),
                    "p_value": float(p_value),
                }
            )

    out = pd.DataFrame(rows)
    out["q_value_bh_within_unit_set"] = benjamini_hochberg(out["p_value"].to_numpy())
    out["direction"] = np.where(
        out["mean_delta_hz"] > 0,
        "ON>OFF",
        np.where(out["mean_delta_hz"] < 0, "ON<OFF", "no_change"),
    )
    out["responsive_q05_within_unit_set"] = out["q_value_bh_within_unit_set"] < 0.05

    keep_cols = [
        "cluster_id",
        "KSLabel",
        "ContamPct",
        "Amplitude",
        "review_category",
        "review_priority",
        "best_raw_channel",
        "best_channel_shank",
    ]
    available = [c for c in keep_cols if c in cluster_metadata.columns]
    return out.merge(cluster_metadata[available], on="cluster_id", how="left")


def summarize_unit_sets(unit_condition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (unit_set, condition), df in unit_condition.groupby(["unit_set", "condition"], sort=True):
        values = df["mean_delta_hz"].to_numpy(dtype=float)
        rows.append(
            {
                "unit_set": unit_set,
                "condition": condition,
                "n_units": int(len(values)),
                "mean_unit_delta_hz": float(np.mean(values)),
                "sem_unit_delta_hz": float(stats.sem(values)) if len(values) > 1 else np.nan,
                "median_unit_delta_hz": float(np.median(values)),
                "n_units_on_gt_off": int(np.sum(values > 0)),
                "n_units_on_lt_off": int(np.sum(values < 0)),
                "n_responsive_q05_within_unit_set": int(df["responsive_q05_within_unit_set"].sum()),
            }
        )
    return pd.DataFrame(rows)


def plot_condition_comparison(summary: pd.DataFrame, output_dir: Path) -> None:
    unit_sets = ["all_units", "ks_good_units", "high_confidence_ks_good"]
    titles = ["All Kilosort clusters", "KS-good clusters", "High-confidence KS-good"]
    fig, axes = plt.subplots(1, 3, figsize=(17, 5), sharey=True)
    for ax, unit_set, title in zip(axes, unit_sets, titles, strict=True):
        sub = summary[summary["unit_set"] == unit_set].sort_values("condition")
        x = np.arange(len(sub))
        colors = np.where(sub["mean_unit_delta_hz"] >= 0, "#2a9d8f", "#d1495b")
        ax.bar(
            x,
            sub["mean_unit_delta_hz"],
            yerr=sub["sem_unit_delta_hz"],
            color=colors,
            alpha=0.9,
        )
        ax.axhline(0, color="black", lw=1)
        ax.set_xticks(x)
        ax.set_xticklabels(sub["condition"], rotation=45, ha="right")
        ax.set_title(title)
        ax.set_ylabel("Mean unit ON - OFF firing rate (Hz)")
    fig.tight_layout()
    fig.savefig(output_dir / "condition_mean_on_minus_off_unit_set_comparison.png", dpi=180)
    plt.close(fig)


def plot_high_conf_heatmap(unit_condition: pd.DataFrame, output_dir: Path) -> None:
    df = unit_condition[unit_condition["unit_set"] == "high_confidence_ks_good"].copy()
    matrix = df.pivot(index="cluster_id", columns="condition", values="mean_delta_hz")
    matrix = matrix.reindex(sorted(matrix.columns), axis=1)
    order = matrix.abs().max(axis=1).sort_values(ascending=False).index
    matrix = matrix.loc[order]
    fig, ax = plt.subplots(figsize=(10, max(5, 0.25 * len(matrix) + 2)))
    vmax = float(np.nanpercentile(np.abs(matrix.to_numpy()), 98))
    vmax = max(vmax, 0.1)
    im = ax.imshow(matrix.to_numpy(), aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
    ax.set_xticks(np.arange(matrix.shape[1]))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(matrix)))
    ax.set_yticklabels(matrix.index)
    ax.set_xlabel("Condition")
    ax.set_ylabel("Cluster ID")
    ax.set_title("High-confidence KS-good units: ON - OFF firing-rate change")
    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("Hz")
    fig.tight_layout()
    fig.savefig(output_dir / "high_confidence_unit_condition_heatmap.png", dpi=180)
    plt.close(fig)


def write_index(output_dir: Path, summary_json: dict[str, object]) -> None:
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Dec 3 High-Confidence Spike ON/OFF</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 32px; line-height: 1.45; }}
    img {{ max-width: 100%; border: 1px solid #ddd; margin: 12px 0 28px; }}
    code {{ background: #f2f2f2; padding: 2px 4px; }}
    li {{ margin: 4px 0; }}
  </style>
</head>
<body>
  <h1>Dec 3 High-Confidence Spike ON/OFF Analysis</h1>
  <p>This report compares all Kilosort clusters, KS-good clusters, and the
  automated high-confidence KS-good subset. The control is each trial's
  following 3 s OFF interval.</p>
  <ul>
    <li>All clusters: <code>{summary_json["n_all_units"]}</code></li>
    <li>KS-good clusters: <code>{summary_json["n_ks_good_units"]}</code></li>
    <li>High-confidence KS-good clusters: <code>{summary_json["n_high_confidence_units"]}</code></li>
    <li>Trials: <code>{summary_json["n_trials"]}</code></li>
  </ul>
  <h2>Condition Mean ON - OFF Across Unit Sets</h2>
  <img src="condition_mean_on_minus_off_unit_set_comparison.png">
  <h2>High-Confidence Unit Heatmap</h2>
  <img src="high_confidence_unit_condition_heatmap.png">
  <h2>High-Confidence Onset PETH</h2>
  <img src="peth_onset_high_confidence_units.png">
  <h2>High-Confidence Offset PETH</h2>
  <img src="peth_offset_high_confidence_units.png">
  <h2>Tables</h2>
  <ul>
    <li><a href="condition_summary_by_unit_set.csv">condition_summary_by_unit_set.csv</a></li>
    <li><a href="unit_condition_stats_by_unit_set.csv">unit_condition_stats_by_unit_set.csv</a></li>
    <li><a href="top_high_confidence_unit_condition_deltas.csv">top_high_confidence_unit_condition_deltas.csv</a></li>
    <li><a href="run_summary.json">run_summary.json</a></li>
  </ul>
  <p>Caveat: still pre-Phy-curation. This is a cleaner exploratory subset, not
  final unit inclusion.</p>
</body>
</html>
"""
    (output_dir / "index.html").write_text(html)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spike-peth-dir", type=Path, default=DEFAULT_SPIKE_PETH_DIR)
    parser.add_argument("--cluster-quality", type=Path, default=DEFAULT_CLUSTER_QUALITY)
    parser.add_argument("--trial-windows", type=Path, default=DEFAULT_TRIAL_WINDOWS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    trial_windows = pd.read_csv(args.trial_windows)
    cluster_quality = pd.read_csv(args.cluster_quality)
    on_counts = np.load(args.spike_peth_dir / "on_counts_by_trial_unit.npy")
    off_counts = np.load(args.spike_peth_dir / "off_counts_by_trial_unit.npy")
    onset_counts = np.load(args.spike_peth_dir / "peth_onset_counts_condition_unit_bin.npy")
    onset_edges = np.load(args.spike_peth_dir / "peth_onset_bin_edges_s.npy")
    offset_counts = np.load(args.spike_peth_dir / "peth_offset_counts_condition_unit_bin.npy")
    offset_edges = np.load(args.spike_peth_dir / "peth_offset_bin_edges_s.npy")

    all_clusters = cluster_quality["cluster_id"].to_numpy(dtype=int)
    ks_good_clusters = cluster_quality.loc[cluster_quality["is_ks_good"], "cluster_id"].to_numpy(dtype=int)
    high_conf_clusters = cluster_quality.loc[
        cluster_quality["review_category"].eq("high_confidence_ks_good"),
        "cluster_id",
    ].to_numpy(dtype=int)

    unit_condition = pd.concat(
        [
            compute_subset_stats(
                trial_windows,
                on_counts,
                off_counts,
                cluster_quality,
                all_clusters,
                "all_units",
            ),
            compute_subset_stats(
                trial_windows,
                on_counts,
                off_counts,
                cluster_quality,
                ks_good_clusters,
                "ks_good_units",
            ),
            compute_subset_stats(
                trial_windows,
                on_counts,
                off_counts,
                cluster_quality,
                high_conf_clusters,
                "high_confidence_ks_good",
            ),
        ],
        ignore_index=True,
    )
    condition_summary = summarize_unit_sets(unit_condition)
    high_conf_top = (
        unit_condition[unit_condition["unit_set"] == "high_confidence_ks_good"]
        .reindex(
            unit_condition[unit_condition["unit_set"] == "high_confidence_ks_good"][
                "mean_delta_hz"
            ]
            .abs()
            .sort_values(ascending=False)
            .index
        )
        .head(60)
    )

    unit_condition.to_csv(args.output_dir / "unit_condition_stats_by_unit_set.csv", index=False)
    condition_summary.to_csv(args.output_dir / "condition_summary_by_unit_set.csv", index=False)
    high_conf_top.to_csv(args.output_dir / "top_high_confidence_unit_condition_deltas.csv", index=False)
    pd.Series(high_conf_clusters, name="cluster_id").to_csv(
        args.output_dir / "high_confidence_cluster_ids.csv",
        index=False,
    )

    condition_order = sorted(trial_windows["condition"].unique())
    plot_condition_comparison(condition_summary, args.output_dir)
    plot_high_conf_heatmap(unit_condition, args.output_dir)
    plot_peth(
        onset_counts,
        onset_edges,
        trial_windows,
        condition_order,
        high_conf_clusters,
        args.output_dir / "peth_onset_high_confidence_units.png",
        "Onset-aligned PETH, high-confidence KS-good units",
        vertical_lines=[(0.0, "ON"), (3.0, "OFF")],
    )
    plot_peth(
        offset_counts,
        offset_edges,
        trial_windows,
        condition_order,
        high_conf_clusters,
        args.output_dir / "peth_offset_high_confidence_units.png",
        "Offset-aligned PETH, high-confidence KS-good units",
        vertical_lines=[(0.0, "OFF")],
    )

    summary_json = {
        "spike_peth_dir": str(args.spike_peth_dir),
        "cluster_quality": str(args.cluster_quality),
        "output_dir": str(args.output_dir),
        "n_trials": int(len(trial_windows)),
        "conditions": condition_order,
        "n_all_units": int(len(all_clusters)),
        "n_ks_good_units": int(len(ks_good_clusters)),
        "n_high_confidence_units": int(len(high_conf_clusters)),
        "high_confidence_cluster_ids": high_conf_clusters.astype(int).tolist(),
        "control_definition": "Each trial's 3 s OFF interval immediately after stimulation.",
        "caveat": "Cleaner Kilosort subset, still pre-Phy-curation.",
    }
    (args.output_dir / "run_summary.json").write_text(json.dumps(summary_json, indent=2) + "\n")

    readme = """# Dec 3 High-Confidence Spike ON/OFF

This report compares three spike unit sets:

- all Kilosort clusters
- Kilosort `good` clusters
- automated high-confidence KS-good clusters from the cluster-quality report

The high-confidence subset is a cleaner exploratory analysis before manual Phy
curation. It should reduce obvious noise/multiunit contamination, but it is not
a substitute for human curation.
"""
    (args.output_dir / "README.md").write_text(readme)
    write_index(args.output_dir, summary_json)

    print(json.dumps(summary_json, indent=2))


if __name__ == "__main__":
    main()
