#!/usr/bin/env python
"""Curated ON/OFF single-unit analysis across all three datasets, compared.

For Dec 3 dHPC, Dec 4 dHPC, Dec 4 LEC: take the curated 'good' units, compute
per-unit per-condition ON-vs-OFF firing change (paired t over trials, BH within
each dataset), and report how many unit-conditions are responsive (q<0.05) plus
the per-condition direction. Answers: does any probe/session show a single-unit
ON/OFF effect, or is the Dec 3 null general?
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from spike_peth_high_confidence_dec3 import compute_subset_stats, summarize_unit_sets

DATASETS = [
    ("dec3_dHPC", "analysis/outputs/dec3/spike_peth_on_off",
     "analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv",
     "analysis/outputs/dec3/curated_merged/cluster_group.tsv",
     "analysis/outputs/dec3/cluster_quality/cluster_quality_summary.csv"),
    ("dec4_dHPC", "analysis/outputs/dec4/spike_peth_on_off_dhpc",
     "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv",
     "analysis/outputs/dec4/curated_merged_dhpc/cluster_group.tsv",
     "analysis/outputs/dec4/cluster_quality_dhpc/cluster_quality_summary.csv"),
    ("dec4_LEC", "analysis/outputs/dec4/spike_peth_on_off_lec",
     "analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv",
     "analysis/outputs/dec4/curated_merged_lec/cluster_group.tsv",
     "analysis/outputs/dec4/cluster_quality/cluster_quality_summary.csv"),
]
OUT = Path("analysis/outputs/cross_dataset_spike_compare")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    per_condition_frames = []
    for name, peth_dir, trials_csv, curated_tsv, qual_csv in DATASETS:
        tw = pd.read_csv(trials_csv)
        on = np.load(Path(peth_dir) / "on_counts_by_trial_unit.npy")
        off = np.load(Path(peth_dir) / "off_counts_by_trial_unit.npy")
        qual = pd.read_csv(qual_csv)
        good = pd.read_csv(curated_tsv, sep="\t")
        good_ids = good.loc[good["group"] == "good", "cluster_id"].to_numpy(int)

        uc = compute_subset_stats(tw, on, off, qual, good_ids, name)
        uc.to_csv(OUT / f"{name}_unit_condition_stats.csv", index=False)
        summ = summarize_unit_sets(uc)
        summ["dataset"] = name
        per_condition_frames.append(summ)

        n_resp = int(uc["responsive_q05_within_unit_set"].sum())
        # session-wide mean ON-OFF (pooled over units & conditions) + direction
        rows.append({
            "dataset": name,
            "n_curated_good": int(len(good_ids)),
            "n_unit_condition_tests": int(len(uc)),
            "n_responsive_q05": n_resp,
            "frac_responsive": round(n_resp / max(len(uc), 1), 4),
            "mean_on_minus_off_hz": round(float(uc["mean_delta_hz"].mean()), 4),
            "median_on_minus_off_hz": round(float(uc["mean_delta_hz"].median()), 4),
            "pct_unit_conditions_ON_gt_OFF": round(
                100 * float((uc["mean_delta_hz"] > 0).mean()), 1),
        })

    overview = pd.DataFrame(rows)
    overview.to_csv(OUT / "overview.csv", index=False)
    pd.concat(per_condition_frames, ignore_index=True).to_csv(
        OUT / "per_condition_by_dataset.csv", index=False)
    (OUT / "overview.json").write_text(json.dumps(rows, indent=2) + "\n")

    print("=== Curated single-unit ON/OFF — cross-dataset overview ===")
    print(overview.to_string(index=False))


if __name__ == "__main__":
    main()
