#!/usr/bin/env python
"""Provisional Dec 3 Kilosort spike PETH and ON-vs-OFF analysis."""

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


DEFAULT_KILOSORT_DIR = Path(
    "analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results"
)
DEFAULT_TRIAL_WINDOWS = Path("analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv")
DEFAULT_OUTPUT_DIR = Path("analysis/outputs/dec3/spike_peth_on_off")
DEFAULT_FS = 20_000.0


def benjamini_hochberg(p_values: np.ndarray) -> np.ndarray:
    p = np.asarray(p_values, dtype=float)
    q = np.full_like(p, np.nan, dtype=float)
    finite = np.isfinite(p)
    if not finite.any():
        return q
    idx = np.where(finite)[0]
    order = idx[np.argsort(p[finite])]
    ranked = p[order]
    n = len(ranked)
    adjusted = ranked * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    q[order] = np.minimum(adjusted, 1.0)
    return q


def read_cluster_metadata(kilosort_dir: Path, n_clusters: int) -> pd.DataFrame:
    metadata = pd.DataFrame({"cluster_id": np.arange(n_clusters, dtype=int)})
    for filename in ["cluster_group.tsv", "cluster_KSLabel.tsv"]:
        path = kilosort_dir / filename
        if path.exists():
            table = pd.read_csv(path, sep="\t")
            metadata = metadata.merge(table, on="cluster_id", how="left", suffixes=("", "_dup"))
    for filename in ["cluster_ContamPct.tsv", "cluster_Amplitude.tsv"]:
        path = kilosort_dir / filename
        if path.exists():
            table = pd.read_csv(path, sep="\t")
            metadata = metadata.merge(table, on="cluster_id", how="left")

    if "KSLabel" not in metadata.columns and "KSLabel_dup" in metadata.columns:
        metadata["KSLabel"] = metadata["KSLabel_dup"]
    if "KSLabel" not in metadata.columns:
        metadata["KSLabel"] = "unknown"
    metadata = metadata.drop(columns=[c for c in metadata.columns if c.endswith("_dup")])
    metadata["is_ks_good"] = metadata["KSLabel"].eq("good")
    return metadata


def load_sorted_spikes(kilosort_dir: Path, fs: float) -> tuple[np.ndarray, np.ndarray, int]:
    spike_times_samples = np.load(kilosort_dir / "spike_times.npy")
    spike_clusters = np.load(kilosort_dir / "spike_clusters.npy").astype(np.int64, copy=False)
    order = np.argsort(spike_times_samples, kind="mergesort")
    spike_times_s = spike_times_samples[order].astype(np.float64) / fs
    spike_clusters = spike_clusters[order]
    n_clusters = int(spike_clusters.max()) + 1
    return spike_times_s, spike_clusters, n_clusters


def count_intervals(
    spike_times_s: np.ndarray,
    spike_clusters: np.ndarray,
    starts: np.ndarray,
    ends: np.ndarray,
    n_clusters: int,
) -> np.ndarray:
    counts = np.zeros((len(starts), n_clusters), dtype=np.int32)
    left = np.searchsorted(spike_times_s, starts, side="left")
    right = np.searchsorted(spike_times_s, ends, side="left")
    for i, (lo, hi) in enumerate(zip(left, right, strict=True)):
        if hi > lo:
            counts[i, :] = np.bincount(spike_clusters[lo:hi], minlength=n_clusters)
    return counts


def compute_unit_condition_stats(
    trial_windows: pd.DataFrame,
    on_counts: np.ndarray,
    off_counts: np.ndarray,
    cluster_metadata: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, float | int | str | bool]] = []
    on_rate = on_counts / 3.0
    off_rate = off_counts / 3.0
    delta = on_rate - off_rate

    for condition, idx in trial_windows.groupby("condition", sort=True).groups.items():
        idx_arr = np.asarray(list(idx), dtype=int)
        for cluster_id in range(on_counts.shape[1]):
            on_values = on_rate[idx_arr, cluster_id]
            off_values = off_rate[idx_arr, cluster_id]
            delta_values = delta[idx_arr, cluster_id]
            if np.allclose(delta_values, delta_values[0]):
                p_value = 1.0
                t_stat = 0.0
            else:
                t_stat, p_value = stats.ttest_rel(on_values, off_values, nan_policy="omit")
            rows.append(
                {
                    "cluster_id": cluster_id,
                    "condition": condition,
                    "n_trials": int(len(idx_arr)),
                    "mean_on_hz": float(np.mean(on_values)),
                    "mean_off_hz": float(np.mean(off_values)),
                    "mean_delta_hz": float(np.mean(delta_values)),
                    "sem_delta_hz": float(stats.sem(delta_values)),
                    "median_delta_hz": float(np.median(delta_values)),
                    "t_stat": float(t_stat),
                    "p_value": float(p_value),
                }
            )

    stats_df = pd.DataFrame(rows)
    stats_df["q_value_bh"] = benjamini_hochberg(stats_df["p_value"].to_numpy())
    stats_df = stats_df.merge(cluster_metadata, on="cluster_id", how="left")
    stats_df["direction"] = np.where(
        stats_df["mean_delta_hz"] > 0,
        "ON>OFF",
        np.where(stats_df["mean_delta_hz"] < 0, "ON<OFF", "no_change"),
    )
    stats_df["responsive_q05"] = stats_df["q_value_bh"] < 0.05
    return stats_df


def summarize_conditions(unit_condition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group_name, group_df in [
        ("all_units", unit_condition),
        ("ks_good_units", unit_condition[unit_condition["is_ks_good"]]),
    ]:
        for condition, condition_df in group_df.groupby("condition", sort=True):
            values = condition_df["mean_delta_hz"].to_numpy(dtype=float)
            rows.append(
                {
                    "unit_set": group_name,
                    "condition": condition,
                    "n_units": int(len(values)),
                    "mean_unit_delta_hz": float(np.mean(values)),
                    "sem_unit_delta_hz": float(stats.sem(values)) if len(values) > 1 else np.nan,
                    "median_unit_delta_hz": float(np.median(values)),
                    "n_units_on_gt_off": int(np.sum(values > 0)),
                    "n_units_on_lt_off": int(np.sum(values < 0)),
                    "n_responsive_q05": int(condition_df["responsive_q05"].sum()),
                }
            )
    return pd.DataFrame(rows)


def compute_peth(
    spike_times_s: np.ndarray,
    spike_clusters: np.ndarray,
    trial_windows: pd.DataFrame,
    event_col: str,
    condition_order: list[str],
    n_clusters: int,
    window: tuple[float, float],
    bin_size: float,
) -> tuple[np.ndarray, np.ndarray]:
    edges = np.arange(window[0], window[1] + bin_size * 0.5, bin_size)
    counts = np.zeros((len(condition_order), n_clusters, len(edges) - 1), dtype=np.int32)
    condition_index = {condition: i for i, condition in enumerate(condition_order)}

    for row in trial_windows.itertuples(index=False):
        event_time = float(getattr(row, event_col))
        condition = getattr(row, "condition")
        cidx = condition_index[condition]
        lo = np.searchsorted(spike_times_s, event_time + window[0], side="left")
        hi = np.searchsorted(spike_times_s, event_time + window[1], side="left")
        if hi <= lo:
            continue
        rel = spike_times_s[lo:hi] - event_time
        bins = np.floor((rel - window[0]) / bin_size).astype(np.int64)
        valid = (bins >= 0) & (bins < len(edges) - 1)
        np.add.at(counts[cidx], (spike_clusters[lo:hi][valid], bins[valid]), 1)
    return counts, edges


def plot_condition_summary(summary: pd.DataFrame, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, unit_set, title in zip(
        axes,
        ["ks_good_units", "all_units"],
        ["KS good units", "All Kilosort units"],
        strict=True,
    ):
        sub = summary[summary["unit_set"] == unit_set].sort_values("condition")
        x = np.arange(len(sub))
        colors = np.where(sub["mean_unit_delta_hz"] >= 0, "#2a9d8f", "#d1495b")
        ax.bar(x, sub["mean_unit_delta_hz"], yerr=sub["sem_unit_delta_hz"], color=colors, alpha=0.9)
        ax.axhline(0, color="black", lw=1)
        ax.set_xticks(x)
        ax.set_xticklabels(sub["condition"], rotation=45, ha="right")
        ax.set_title(title)
        ax.set_ylabel("Mean unit ON - OFF firing rate (Hz)")
    fig.tight_layout()
    fig.savefig(output_dir / "condition_mean_on_minus_off.png", dpi=180)
    plt.close(fig)


def plot_heatmap(
    unit_condition: pd.DataFrame,
    output_dir: Path,
    good_only: bool,
) -> None:
    df = unit_condition[unit_condition["is_ks_good"]].copy() if good_only else unit_condition.copy()
    label = "ks_good" if good_only else "all_units"
    title = "KS good units" if good_only else "All Kilosort units"
    matrix = df.pivot(index="cluster_id", columns="condition", values="mean_delta_hz")
    matrix = matrix.reindex(sorted(matrix.columns), axis=1)
    order = matrix.abs().max(axis=1).sort_values(ascending=False).index
    matrix = matrix.loc[order]
    height = max(5, min(22, 0.13 * len(matrix) + 2))
    fig, ax = plt.subplots(figsize=(10, height))
    vmax = float(np.nanpercentile(np.abs(matrix.to_numpy()), 98))
    vmax = max(vmax, 0.1)
    im = ax.imshow(matrix.to_numpy(), aspect="auto", cmap="coolwarm", vmin=-vmax, vmax=vmax)
    ax.set_xticks(np.arange(matrix.shape[1]))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    y_step = max(1, len(matrix) // 30)
    ax.set_yticks(np.arange(0, len(matrix), y_step))
    ax.set_yticklabels(matrix.index[::y_step])
    ax.set_xlabel("Condition")
    ax.set_ylabel("Cluster ID sorted by max |ON - OFF|")
    ax.set_title(f"ON - OFF firing-rate change, {title}")
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Hz")
    fig.tight_layout()
    fig.savefig(output_dir / f"unit_condition_on_minus_off_heatmap_{label}.png", dpi=180)
    plt.close(fig)


def plot_peth(
    peth_counts: np.ndarray,
    edges: np.ndarray,
    trial_windows: pd.DataFrame,
    condition_order: list[str],
    cluster_ids: np.ndarray,
    output_path: Path,
    title: str,
    vertical_lines: list[tuple[float, str]],
) -> None:
    centers = (edges[:-1] + edges[1:]) / 2
    bin_size = float(np.diff(edges)[0])
    # Size the grid to the number of conditions (6 for Dec 3, 12 for Dec 4, etc.).
    ncols = 3
    nrows = (len(condition_order) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 3.5 * nrows),
                             sharex=True, sharey=True)
    axes = np.atleast_1d(axes).ravel()
    for ax in axes[len(condition_order):]:
        ax.axis("off")  # hide unused cells
    for ax, condition in zip(axes, condition_order, strict=False):
        cidx = condition_order.index(condition)
        n_trials = int((trial_windows["condition"] == condition).sum())
        unit_rates = peth_counts[cidx, cluster_ids, :] / (n_trials * bin_size)
        mean_rate = unit_rates.mean(axis=0)
        sem_rate = stats.sem(unit_rates, axis=0) if len(cluster_ids) > 1 else np.zeros_like(mean_rate)
        ax.plot(centers, mean_rate, color="#264653", lw=1.8)
        ax.fill_between(centers, mean_rate - sem_rate, mean_rate + sem_rate, color="#264653", alpha=0.22)
        for x, line_label in vertical_lines:
            ax.axvline(x, color="#d1495b" if x == 0 else "#777777", lw=1, ls="--")
            if line_label:
                ax.text(x, ax.get_ylim()[1], line_label, rotation=90, va="top", ha="right", fontsize=8)
        ax.set_title(condition)
        ax.set_xlabel("Time from event (s)")
        ax.set_ylabel("Population firing rate (Hz/unit)")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def write_index(output_dir: Path, summary: dict[str, object]) -> None:
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Dec 3 Provisional Spike PETH / ON-OFF</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 32px; line-height: 1.45; }}
    img {{ max-width: 100%; border: 1px solid #ddd; margin: 12px 0 28px; }}
    code {{ background: #f2f2f2; padding: 2px 4px; }}
    table {{ border-collapse: collapse; }}
    td, th {{ border: 1px solid #ddd; padding: 6px 8px; }}
  </style>
</head>
<body>
  <h1>Dec 3 Provisional Spike PETH / ON-OFF Analysis</h1>
  <p>This is an uncurated first pass from Modal Kilosort4 output. The control is
  the 3 s OFF interval immediately after each 3 s stimulation ON interval.</p>
  <ul>
    <li>Total clusters: <code>{summary["n_clusters"]}</code></li>
    <li>KS good clusters: <code>{summary["n_ks_good_clusters"]}</code></li>
    <li>Trials: <code>{summary["n_trials"]}</code></li>
    <li>Spike count: <code>{summary["n_spikes"]}</code></li>
  </ul>
  <h2>Condition Mean ON - OFF</h2>
  <img src="condition_mean_on_minus_off.png">
  <h2>KS Good Unit Heatmap</h2>
  <img src="unit_condition_on_minus_off_heatmap_ks_good.png">
  <h2>All Unit Heatmap</h2>
  <img src="unit_condition_on_minus_off_heatmap_all_units.png">
  <h2>Onset-Aligned PETH, KS Good Units</h2>
  <img src="peth_onset_ks_good_units.png">
  <h2>Offset-Aligned PETH, KS Good Units</h2>
  <img src="peth_offset_ks_good_units.png">
  <h2>Key Tables</h2>
  <ul>
    <li><a href="condition_summary_on_off.csv">condition_summary_on_off.csv</a></li>
    <li><a href="unit_condition_on_off_stats.csv">unit_condition_on_off_stats.csv</a></li>
    <li><a href="top_units_by_condition_delta.csv">top_units_by_condition_delta.csv</a></li>
    <li><a href="run_summary.json">run_summary.json</a></li>
  </ul>
  <p>Caveat: use this for exploratory physiology only. Final spike claims need
  Phy curation and corrected probe geometry/channel order.</p>
</body>
</html>
"""
    (output_dir / "index.html").write_text(html)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kilosort-dir", type=Path, default=DEFAULT_KILOSORT_DIR)
    parser.add_argument("--trial-windows", type=Path, default=DEFAULT_TRIAL_WINDOWS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--fs", type=float, default=DEFAULT_FS)
    parser.add_argument("--peth-bin-s", type=float, default=0.05)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    trial_windows = pd.read_csv(args.trial_windows)
    condition_order = sorted(trial_windows["condition"].unique())
    spike_times_s, spike_clusters, n_clusters = load_sorted_spikes(args.kilosort_dir, args.fs)
    cluster_metadata = read_cluster_metadata(args.kilosort_dir, n_clusters)
    cluster_metadata.to_csv(args.output_dir / "cluster_metadata.csv", index=False)

    on_counts = count_intervals(
        spike_times_s,
        spike_clusters,
        trial_windows["on_start_s"].to_numpy(dtype=float),
        trial_windows["on_end_s"].to_numpy(dtype=float),
        n_clusters,
    )
    off_counts = count_intervals(
        spike_times_s,
        spike_clusters,
        trial_windows["off_start_s"].to_numpy(dtype=float),
        trial_windows["off_end_s"].to_numpy(dtype=float),
        n_clusters,
    )

    np.save(args.output_dir / "on_counts_by_trial_unit.npy", on_counts)
    np.save(args.output_dir / "off_counts_by_trial_unit.npy", off_counts)

    unit_condition = compute_unit_condition_stats(trial_windows, on_counts, off_counts, cluster_metadata)
    condition_summary = summarize_conditions(unit_condition)
    top_units = unit_condition.reindex(
        unit_condition["mean_delta_hz"].abs().sort_values(ascending=False).index
    ).head(60)

    unit_condition.to_csv(args.output_dir / "unit_condition_on_off_stats.csv", index=False)
    condition_summary.to_csv(args.output_dir / "condition_summary_on_off.csv", index=False)
    top_units.to_csv(args.output_dir / "top_units_by_condition_delta.csv", index=False)

    plot_condition_summary(condition_summary, args.output_dir)
    plot_heatmap(unit_condition, args.output_dir, good_only=True)
    plot_heatmap(unit_condition, args.output_dir, good_only=False)

    onset_counts, onset_edges = compute_peth(
        spike_times_s,
        spike_clusters,
        trial_windows,
        "on_start_s",
        condition_order,
        n_clusters,
        window=(-1.0, 4.0),
        bin_size=args.peth_bin_s,
    )
    offset_counts, offset_edges = compute_peth(
        spike_times_s,
        spike_clusters,
        trial_windows,
        "off_start_s",
        condition_order,
        n_clusters,
        window=(-2.0, 3.0),
        bin_size=args.peth_bin_s,
    )
    np.save(args.output_dir / "peth_onset_counts_condition_unit_bin.npy", onset_counts)
    np.save(args.output_dir / "peth_onset_bin_edges_s.npy", onset_edges)
    np.save(args.output_dir / "peth_offset_counts_condition_unit_bin.npy", offset_counts)
    np.save(args.output_dir / "peth_offset_bin_edges_s.npy", offset_edges)

    good_clusters = cluster_metadata.loc[cluster_metadata["is_ks_good"], "cluster_id"].to_numpy(dtype=int)
    all_clusters = cluster_metadata["cluster_id"].to_numpy(dtype=int)
    peth_clusters = good_clusters if len(good_clusters) else all_clusters

    plot_peth(
        onset_counts,
        onset_edges,
        trial_windows,
        condition_order,
        peth_clusters,
        args.output_dir / "peth_onset_ks_good_units.png",
        "Onset-aligned PETH, KS good units",
        vertical_lines=[(0.0, "ON"), (3.0, "OFF")],
    )
    plot_peth(
        offset_counts,
        offset_edges,
        trial_windows,
        condition_order,
        peth_clusters,
        args.output_dir / "peth_offset_ks_good_units.png",
        "Offset-aligned PETH, KS good units",
        vertical_lines=[(0.0, "OFF")],
    )

    summary = {
        "kilosort_dir": str(args.kilosort_dir),
        "trial_windows": str(args.trial_windows),
        "output_dir": str(args.output_dir),
        "fs_hz": args.fs,
        "n_spikes": int(len(spike_times_s)),
        "n_clusters": int(n_clusters),
        "n_ks_good_clusters": int(cluster_metadata["is_ks_good"].sum()),
        "n_trials": int(len(trial_windows)),
        "conditions": condition_order,
        "control_definition": "Each trial's 3 s OFF interval immediately after stimulation.",
        "caveat": "Uncurated Kilosort4 output with provisional geometry; exploratory only.",
    }
    (args.output_dir / "run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    readme = f"""# Dec 3 Provisional Spike PETH / ON-vs-OFF

This folder contains the first spike analysis from the Modal Kilosort4 output.

## Inputs

- Kilosort output: `{args.kilosort_dir}`
- Trial windows: `{args.trial_windows}`
- Sampling rate: `{args.fs:g} Hz`

## Analysis

- Converts Kilosort `spike_times.npy` from samples to seconds.
- Counts spikes for every unit in every 3 s ON interval.
- Counts spikes for every unit in the following 3 s OFF-control interval.
- Computes paired ON-vs-OFF firing-rate deltas by condition.
- Builds onset- and offset-aligned PETH arrays.

## Main Outputs

- `index.html`: clickable visual report.
- `condition_summary_on_off.csv`: condition-level summaries for all units and KS-good units.
- `unit_condition_on_off_stats.csv`: per-unit, per-condition paired ON-vs-OFF statistics.
- `top_units_by_condition_delta.csv`: largest absolute condition effects.
- `condition_mean_on_minus_off.png`: population condition summary.
- `unit_condition_on_minus_off_heatmap_ks_good.png`: KS-good unit heatmap.
- `unit_condition_on_minus_off_heatmap_all_units.png`: all-unit heatmap.
- `peth_onset_ks_good_units.png`: onset-aligned PETH.
- `peth_offset_ks_good_units.png`: offset-aligned PETH.

## Caveat

This is exploratory and uncurated. Use it to decide what to inspect in Phy and
what spike/LFP hypotheses to test next. Do not make final unit or anatomical
claims until Phy curation and exact probe geometry are resolved.
"""
    (args.output_dir / "README.md").write_text(readme)
    write_index(args.output_dir, summary)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
