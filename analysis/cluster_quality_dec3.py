#!/usr/bin/env python
"""Summarize Dec 3 Kilosort cluster quality before manual Phy curation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


DEFAULT_KILOSORT_DIR = Path(
    "analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results"
)
DEFAULT_OUTPUT_DIR = Path("analysis/outputs/dec3/cluster_quality")
DEFAULT_FS = 20_000.0


def read_table(path: Path, value_name: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["cluster_id", value_name])
    table = pd.read_csv(path, sep="\t")
    table["cluster_id"] = table["cluster_id"].astype(int)
    return table


def read_metadata(kilosort_dir: Path, n_clusters: int) -> pd.DataFrame:
    metadata = pd.DataFrame({"cluster_id": np.arange(n_clusters, dtype=int)})
    for filename in ["cluster_KSLabel.tsv", "cluster_ContamPct.tsv", "cluster_Amplitude.tsv"]:
        table = read_table(kilosort_dir / filename, "")
        if not table.empty:
            metadata = metadata.merge(table, on="cluster_id", how="left")

    group_table = read_table(kilosort_dir / "cluster_group.tsv", "")
    if not group_table.empty:
        group_table = group_table.rename(columns={"KSLabel": "group"})
        metadata = metadata.merge(group_table, on="cluster_id", how="left")

    if "KSLabel" not in metadata.columns:
        metadata["KSLabel"] = "unknown"
    if "group" not in metadata.columns:
        metadata["group"] = metadata["KSLabel"]
    metadata["KSLabel"] = metadata["KSLabel"].fillna("unknown")
    metadata["is_ks_good"] = metadata["KSLabel"].eq("good")
    return metadata


def compute_isi_metrics(
    spike_times_s: np.ndarray,
    spike_clusters: np.ndarray,
    n_clusters: int,
    refractory_s: float,
) -> tuple[np.ndarray, np.ndarray]:
    isi_violations = np.zeros(n_clusters, dtype=np.int64)
    isi_violation_fraction = np.full(n_clusters, np.nan, dtype=float)

    order = np.lexsort((spike_times_s, spike_clusters))
    sorted_clusters = spike_clusters[order]
    sorted_times = spike_times_s[order]
    starts = np.r_[0, np.flatnonzero(np.diff(sorted_clusters)) + 1]
    ends = np.r_[starts[1:], len(sorted_clusters)]

    for start, end in zip(starts, ends, strict=True):
        cluster_id = int(sorted_clusters[start])
        n_spikes = end - start
        if n_spikes < 2:
            isi_violation_fraction[cluster_id] = 0.0
            continue
        isi = np.diff(sorted_times[start:end])
        n_viol = int(np.sum(isi < refractory_s))
        isi_violations[cluster_id] = n_viol
        isi_violation_fraction[cluster_id] = n_viol / max(n_spikes - 1, 1)

    return isi_violations, isi_violation_fraction


def template_peak_channels(kilosort_dir: Path) -> pd.DataFrame:
    templates = np.load(kilosort_dir / "templates.npy", mmap_mode="r")
    channel_map = np.load(kilosort_dir / "channel_map.npy")
    channel_positions = np.load(kilosort_dir / "channel_positions.npy")
    shanks_path = kilosort_dir / "channel_shanks.npy"
    channel_shanks = np.load(shanks_path) if shanks_path.exists() else np.full(len(channel_map), np.nan)

    rows = []
    for cluster_id in range(templates.shape[0]):
        template = np.asarray(templates[cluster_id])
        ptp_by_channel = np.ptp(template, axis=0)
        local_peak_idx = int(np.argmax(ptp_by_channel))
        rows.append(
            {
                "cluster_id": cluster_id,
                "best_local_channel_index": local_peak_idx,
                "best_raw_channel": int(channel_map[local_peak_idx]),
                "best_channel_x": float(channel_positions[local_peak_idx, 0]),
                "best_channel_y": float(channel_positions[local_peak_idx, 1]),
                "best_channel_shank": int(channel_shanks[local_peak_idx])
                if np.isfinite(channel_shanks[local_peak_idx])
                else -1,
                "template_peak_to_peak": float(ptp_by_channel[local_peak_idx]),
            }
        )
    return pd.DataFrame(rows)


def assign_review_category(df: pd.DataFrame) -> pd.Series:
    contam = df["ContamPct"].fillna(np.inf)
    spike_count = df["spike_count"]
    fr = df["firing_rate_hz"]
    isi_frac = df["isi_violation_fraction"].fillna(np.inf)
    amp = df["Amplitude"].fillna(0.0)
    ks_good = df["is_ks_good"]

    category = pd.Series("manual_review", index=df.index, dtype=object)
    category.loc[
        ks_good
        & (contam <= 10)
        & (spike_count >= 500)
        & (fr >= 0.05)
        & (isi_frac <= 0.02)
    ] = "high_confidence_ks_good"
    category.loc[
        (contam > 50)
        | (isi_frac > 0.10)
        | (spike_count < 100)
        | ((amp > 0) & (amp < 8))
    ] = "likely_noise_or_multiunit"
    category.loc[
        (~ks_good)
        & (contam <= 20)
        & (spike_count >= 1000)
        & (isi_frac <= 0.03)
    ] = "mua_candidate_review"
    return category


def assign_priority(df: pd.DataFrame) -> pd.Series:
    responsive = df.get("max_abs_on_off_delta_hz", pd.Series(0.0, index=df.index)).fillna(0.0)
    priority = (
        responsive.rank(method="dense", ascending=False)
        + df["is_ks_good"].map({True: 0, False: 50})
        + df["review_category"].eq("likely_noise_or_multiunit").map({True: 100, False: 0})
    )
    return priority.rank(method="first").astype(int)


def attach_spike_response_summary(df: pd.DataFrame, peth_stats_path: Path) -> pd.DataFrame:
    if not peth_stats_path.exists():
        df["max_abs_on_off_delta_hz"] = np.nan
        df["best_on_off_condition"] = ""
        df["n_conditions_q05"] = 0
        return df

    stats = pd.read_csv(peth_stats_path)
    idx = stats.groupby("cluster_id")["mean_delta_hz"].apply(lambda s: s.abs().idxmax())
    best = stats.loc[idx, ["cluster_id", "condition", "mean_delta_hz"]].rename(
        columns={
            "condition": "best_on_off_condition",
            "mean_delta_hz": "best_on_off_delta_hz",
        }
    )
    best["max_abs_on_off_delta_hz"] = best["best_on_off_delta_hz"].abs()
    n_sig = (
        stats.assign(sig=stats["q_value_bh"] < 0.05)
        .groupby("cluster_id")["sig"]
        .sum()
        .rename("n_conditions_q05")
        .reset_index()
    )
    return df.merge(best, on="cluster_id", how="left").merge(n_sig, on="cluster_id", how="left")


def plot_label_summary(df: pd.DataFrame, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    df["KSLabel"].value_counts().plot(kind="bar", ax=axes[0], color="#4c78a8")
    axes[0].set_title("Kilosort labels")
    axes[0].set_ylabel("# clusters")
    df["review_category"].value_counts().plot(kind="bar", ax=axes[1], color="#59a14f")
    axes[1].set_title("Automated review categories")
    axes[1].set_ylabel("# clusters")
    fig.tight_layout()
    fig.savefig(output_dir / "cluster_quality_label_counts.png", dpi=180)
    plt.close(fig)


def plot_quality_scatter(df: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = df["review_category"].map(
        {
            "high_confidence_ks_good": "#2a9d8f",
            "manual_review": "#f2c14e",
            "mua_candidate_review": "#4c78a8",
            "likely_noise_or_multiunit": "#d1495b",
        }
    ).fillna("#999999")
    sizes = 20 + 80 * np.clip(df["max_abs_on_off_delta_hz"].fillna(0) / 5.0, 0, 1)
    ax.scatter(
        df["firing_rate_hz"],
        df["ContamPct"],
        c=colors,
        s=sizes,
        alpha=0.8,
        edgecolor="black",
        linewidth=0.25,
    )
    ax.set_xscale("log")
    ax.set_xlabel("Firing rate (Hz, log scale)")
    ax.set_ylabel("Kilosort contamination (%)")
    ax.set_title("Cluster quality overview")
    ax.axhline(10, color="black", lw=1, ls="--")
    ax.axhline(20, color="black", lw=1, ls=":")
    fig.tight_layout()
    fig.savefig(output_dir / "cluster_quality_scatter.png", dpi=180)
    plt.close(fig)


def write_html(df: pd.DataFrame, output_dir: Path, summary: dict[str, object]) -> None:
    cols = [
        "review_priority",
        "cluster_id",
        "review_category",
        "KSLabel",
        "ContamPct",
        "Amplitude",
        "spike_count",
        "firing_rate_hz",
        "isi_violation_fraction",
        "best_raw_channel",
        "best_channel_shank",
        "best_on_off_condition",
        "best_on_off_delta_hz",
        "n_conditions_q05",
    ]
    top_table = df.sort_values("review_priority").head(60)[cols].to_html(index=False, float_format="{:.4g}".format)
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Dec 3 Cluster Quality</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 28px; line-height: 1.45; }}
    img {{ max-width: 100%; border: 1px solid #ddd; }}
    table {{ border-collapse: collapse; font-size: 13px; }}
    th, td {{ border: 1px solid #ddd; padding: 4px 7px; text-align: right; }}
    th {{ background: #f4f4f4; }}
    td:nth-child(3), td:nth-child(4), td:nth-child(12) {{ text-align: left; }}
  </style>
</head>
<body>
  <h1>Dec 3 Cluster Quality</h1>
  <p>This is an automated pre-curation report. It does not replace Phy review.</p>
  <ul>
    <li>Total clusters: {summary['n_clusters']}</li>
    <li>KS good clusters: {summary['n_ks_good']}</li>
    <li>High-confidence KS-good clusters by automated rules: {summary['n_high_confidence']}</li>
    <li>Likely noise/multiunit by automated rules: {summary['n_likely_noise']}</li>
  </ul>
  <h2>Overview</h2>
  <p><a href="cluster_quality_summary.csv">cluster_quality_summary.csv</a> |
     <a href="phy_review_priority.csv">phy_review_priority.csv</a> |
     <a href="cluster_quality_summary.json">cluster_quality_summary.json</a></p>
  <img src="cluster_quality_label_counts.png">
  <img src="cluster_quality_scatter.png">
  <h2>First 60 Clusters To Review</h2>
  {top_table}
</body>
</html>
"""
    (output_dir / "index.html").write_text(html)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kilosort-dir", type=Path, default=DEFAULT_KILOSORT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--peth-stats",
        type=Path,
        default=Path("analysis/outputs/dec3/spike_peth_on_off/unit_condition_on_off_stats.csv"),
    )
    parser.add_argument("--fs", type=float, default=DEFAULT_FS)
    parser.add_argument("--refractory-ms", type=float, default=2.0)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    spike_times_samples = np.load(args.kilosort_dir / "spike_times.npy")
    spike_clusters = np.load(args.kilosort_dir / "spike_clusters.npy").astype(np.int64, copy=False)
    spike_times_s = spike_times_samples.astype(np.float64) / args.fs
    n_clusters = int(spike_clusters.max()) + 1
    recording_duration_s = float(spike_times_s.max() - spike_times_s.min())

    metadata = read_metadata(args.kilosort_dir, n_clusters)
    spike_count = np.bincount(spike_clusters, minlength=n_clusters)
    metadata["spike_count"] = spike_count
    metadata["firing_rate_hz"] = spike_count / recording_duration_s

    isi_counts, isi_fraction = compute_isi_metrics(
        spike_times_s,
        spike_clusters,
        n_clusters,
        refractory_s=args.refractory_ms / 1000.0,
    )
    metadata["isi_violations_lt_2ms"] = isi_counts
    metadata["isi_violation_fraction"] = isi_fraction

    metadata = metadata.merge(template_peak_channels(args.kilosort_dir), on="cluster_id", how="left")
    metadata = attach_spike_response_summary(metadata, args.peth_stats)
    metadata["n_conditions_q05"] = metadata["n_conditions_q05"].fillna(0).astype(int)
    metadata["review_category"] = assign_review_category(metadata)
    metadata["review_priority"] = assign_priority(metadata)

    metadata = metadata.sort_values(["review_priority", "cluster_id"])
    metadata.to_csv(args.output_dir / "cluster_quality_summary.csv", index=False)
    metadata.sort_values("review_priority").to_csv(args.output_dir / "phy_review_priority.csv", index=False)

    summary = {
        "kilosort_dir": str(args.kilosort_dir),
        "output_dir": str(args.output_dir),
        "fs_hz": args.fs,
        "recording_duration_s": recording_duration_s,
        "n_spikes": int(len(spike_times_s)),
        "n_clusters": int(n_clusters),
        "n_ks_good": int(metadata["is_ks_good"].sum()),
        "n_high_confidence": int((metadata["review_category"] == "high_confidence_ks_good").sum()),
        "n_likely_noise": int((metadata["review_category"] == "likely_noise_or_multiunit").sum()),
        "n_manual_review": int((metadata["review_category"] == "manual_review").sum()),
        "n_mua_candidate_review": int((metadata["review_category"] == "mua_candidate_review").sum()),
        "refractory_ms_for_isi_fraction": args.refractory_ms,
        "caveat": "Automated pre-curation only; final inclusion still needs Phy review.",
    }
    (args.output_dir / "cluster_quality_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    readme = """# Dec 3 Cluster Quality

Automated pre-curation summary for the Dec 3 Kilosort4 output.

Use `phy_review_priority.csv` as the checklist for manual Phy review. The
categories are conservative helpers, not final neuroscience claims.

- `high_confidence_ks_good`: KS-good, low contamination, enough spikes, low
  short-ISI fraction.
- `mua_candidate_review`: not KS-good, but clean enough to inspect manually.
- `manual_review`: ambiguous and should be inspected in Phy.
- `likely_noise_or_multiunit`: likely to exclude unless Phy shows otherwise.
"""
    (args.output_dir / "README.md").write_text(readme)

    plot_label_summary(metadata, args.output_dir)
    plot_quality_scatter(metadata, args.output_dir)
    write_html(metadata, args.output_dir, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
