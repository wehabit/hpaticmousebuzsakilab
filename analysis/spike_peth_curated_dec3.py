#!/usr/bin/env python
"""Re-run the Dec 3 ON/OFF spike analysis on the CURATED good-unit set.

Compares the human/analysis-curated 29 good units against the original
automated 19 high-confidence set, to test whether the cleaner, larger curated
set reveals a stimulation ON-vs-OFF firing effect the conservative set missed.

  python analysis/spike_peth_curated_dec3.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from spike_peth_high_confidence_dec3 import compute_subset_stats, summarize_unit_sets

PETH = Path("analysis/outputs/dec3/spike_peth_on_off")
QUAL = Path("analysis/outputs/dec3/cluster_quality/cluster_quality_summary.csv")
TRIALS = Path("analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv")
CURATED = Path("analysis/outputs/dec3/curated_merged/cluster_group.tsv")
OUT = Path("analysis/outputs/dec3/spike_peth_curated")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tw = pd.read_csv(TRIALS)
    qual = pd.read_csv(QUAL)
    on = np.load(PETH / "on_counts_by_trial_unit.npy")
    off = np.load(PETH / "off_counts_by_trial_unit.npy")

    hc = qual.loc[qual["review_category"].eq("high_confidence_ks_good"), "cluster_id"].to_numpy(int)
    curated = pd.read_csv(CURATED, sep="\t")
    curated_good = curated.loc[curated["group"].eq("good"), "cluster_id"].to_numpy(int)

    uc = pd.concat([
        compute_subset_stats(tw, on, off, qual, hc, "high_confidence_19"),
        compute_subset_stats(tw, on, off, qual, curated_good, "curated_good_29"),
    ], ignore_index=True)
    uc.to_csv(OUT / "unit_condition_stats.csv", index=False)

    summ = summarize_unit_sets(uc)
    summ.to_csv(OUT / "condition_summary.csv", index=False)

    # Responsive units (BH q<0.05 within set), per set.
    resp = uc[uc["responsive_q05_within_unit_set"]].copy()
    resp.to_csv(OUT / "responsive_units.csv", index=False)

    report = {
        "n_high_confidence_19": int(len(hc)),
        "n_curated_good_29": int(len(curated_good)),
        "n_responsive_unit_conditions": {
            s: int(resp[resp.unit_set == s].shape[0]) for s in uc.unit_set.unique()
        },
        "responsive_units_curated": sorted(
            resp.loc[resp.unit_set == "curated_good_29", "cluster_id"].unique().tolist()
        ),
        "responsive_units_high_conf": sorted(
            resp.loc[resp.unit_set == "high_confidence_19", "cluster_id"].unique().tolist()
        ),
    }
    # Per-condition mean ON-OFF (Hz) for the curated set, with direction count.
    cur_summ = summ[summ.unit_set == "curated_good_29"].sort_values("condition")
    report["curated_per_condition"] = {
        r.condition: {
            "mean_on_minus_off_hz": round(r.mean_unit_delta_hz, 4),
            "n_units_on_gt_off": int(r.n_units_on_gt_off),
            "n_units_on_lt_off": int(r.n_units_on_lt_off),
            "n_responsive_q05": int(r.n_responsive_q05_within_unit_set),
        }
        for r in cur_summ.itertuples()
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
