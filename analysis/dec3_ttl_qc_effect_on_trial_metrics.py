#!/usr/bin/env python3
"""Check whether Dec 3 TTL delivery QC changes trial-level LFP metrics."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path("analysis/outputs/dec3")
TTL_QUALITY = ROOT / "ttl_phase_reliability" / "ttl_phase_trial_quality.csv"
TRIAL_METRICS = ROOT / "trial_level_stats" / "trial_level_metrics.csv"
OUT = ROOT / "ttl_qc_metric_effect"


def load_ttl() -> dict[int, dict]:
    out = {}
    with TTL_QUALITY.open(newline="") as f:
        for row in csv.DictReader(f):
            trial = int(row["trial_number"])
            n_all = int(row["n_all_on"])
            first = float(row["first_edge_ms"]) if row["first_edge_ms"] else float("nan")
            out[trial] = {
                "n_all_on": n_all,
                "n_rising_on": int(row["n_rising_on"]),
                "first_edge_ms": first,
                "has_edge": n_all > 0,
                "good_le_500ms": n_all > 0 and math.isfinite(first) and first <= 500,
                "tight_le_200ms": n_all > 0 and math.isfinite(first) and first <= 200,
            }
    return out


def load_trial_metrics() -> list[dict]:
    rows = []
    with TRIAL_METRICS.open(newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "trial_number": int(row["trial_number"]),
                    "condition": row["condition"],
                    "analysis_group": row["analysis_group"],
                    "sustained_broadband_delta": float(row["sustained_broadband_delta"]),
                    "offset_broadband_delta": float(row["offset_broadband_delta"]),
                    "driven_power_log2_delta": float(row["driven_power_log2_delta"]),
                }
            )
    return rows


def mean_ci(values: list[float], n_boot: int = 2000, seed: int = 321) -> tuple[float, float, float]:
    vals = np.asarray([v for v in values if math.isfinite(v)], dtype=float)
    if vals.size == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    boot = rng.choice(vals, size=(n_boot, vals.size), replace=True).mean(axis=1)
    return float(vals.mean()), float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def corr(x: list[float], y: list[float]) -> float:
    xx = np.asarray(x, dtype=float)
    yy = np.asarray(y, dtype=float)
    mask = np.isfinite(xx) & np.isfinite(yy)
    if mask.sum() < 3:
        return float("nan")
    xx = xx[mask]
    yy = yy[mask]
    if xx.std() == 0 or yy.std() == 0:
        return float("nan")
    return float(np.corrcoef(xx, yy)[0, 1])


def aggregate_by_trial(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[int, str], dict] = {}
    for row in rows:
        key = (row["trial_number"], row["condition"])
        grouped.setdefault(
            key,
            {
                "trial_number": row["trial_number"],
                "condition": row["condition"],
                "sustained_broadband_delta": [],
                "offset_broadband_delta": [],
                "driven_power_log2_delta": [],
            },
        )
        for metric in ["sustained_broadband_delta", "offset_broadband_delta", "driven_power_log2_delta"]:
            grouped[key][metric].append(row[metric])

    out = []
    for entry in grouped.values():
        out.append(
            {
                "trial_number": entry["trial_number"],
                "condition": entry["condition"],
                "sustained_broadband_delta": float(np.mean(entry["sustained_broadband_delta"])),
                "offset_broadband_delta": float(np.mean(entry["offset_broadband_delta"])),
                "driven_power_log2_delta": float(np.mean(entry["driven_power_log2_delta"])),
            }
        )
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ttl = load_ttl()
    trial_rows = aggregate_by_trial(load_trial_metrics())

    # Add TTL QC fields.
    for row in trial_rows:
        row.update(ttl[row["trial_number"]])

    conditions = sorted({r["condition"] for r in trial_rows})
    metrics = ["sustained_broadband_delta", "offset_broadband_delta", "driven_power_log2_delta"]
    subsets = {
        "all": lambda r: True,
        "has_edge": lambda r: r["has_edge"],
        "good_first_edge_le_500ms": lambda r: r["good_le_500ms"],
        "tight_first_edge_le_200ms": lambda r: r["tight_le_200ms"],
    }

    # Add per-condition high-edge-count subset.
    p75_by_condition = {}
    for condition in conditions:
        counts = [r["n_all_on"] for r in trial_rows if r["condition"] == condition]
        p75_by_condition[condition] = float(np.percentile(np.asarray(counts), 75))
    subsets["high_edge_count_ge_condition_p75"] = lambda r: r["n_all_on"] >= p75_by_condition[r["condition"]]

    summary_rows = []
    for condition in conditions:
        cond_rows = [r for r in trial_rows if r["condition"] == condition]
        for subset_name, predicate in subsets.items():
            sub = [r for r in cond_rows if predicate(r)]
            out = {
                "condition": condition,
                "subset": subset_name,
                "n_trials": len(sub),
                "median_first_edge_ms": float(np.median([r["first_edge_ms"] for r in sub if math.isfinite(r["first_edge_ms"])]))
                if sub and any(math.isfinite(r["first_edge_ms"]) for r in sub)
                else float("nan"),
                "median_n_all_on": float(np.median([r["n_all_on"] for r in sub])) if sub else float("nan"),
            }
            for metric in metrics:
                mean, lo, hi = mean_ci([r[metric] for r in sub], seed=321 + len(summary_rows))
                out[f"{metric}_mean"] = mean
                out[f"{metric}_ci_low"] = lo
                out[f"{metric}_ci_high"] = hi
            summary_rows.append(out)

    corr_rows = []
    for condition in conditions:
        sub = [r for r in trial_rows if r["condition"] == condition]
        out = {"condition": condition, "n_trials": len(sub)}
        for metric in metrics:
            out[f"corr_n_edges_vs_{metric}"] = corr([r["n_all_on"] for r in sub], [r[metric] for r in sub])
            out[f"corr_first_edge_ms_vs_{metric}"] = corr([r["first_edge_ms"] for r in sub], [r[metric] for r in sub])
        corr_rows.append(out)

    summary_fields = list(summary_rows[0].keys())
    with (OUT / "ttl_qc_metric_subset_summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary_rows)

    corr_fields = list(corr_rows[0].keys())
    with (OUT / "ttl_qc_metric_correlations.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=corr_fields)
        writer.writeheader()
        writer.writerows(corr_rows)

    # Markdown summary focusing on the user's conditions.
    focus = {"amp100_freq26", "amp250_freq26", "amp180_freq26"}
    md = [
        "# Dec 3 TTL QC Effect on Trial-Level Metrics",
        "",
        "This asks whether using the TTL as a delivery/onset QC filter changes the existing trial-level LFP metrics.",
        "",
        "Important: this still does not use TTL as stimulus phase. It only filters or stratifies trials by delivery quality.",
        "",
        "## Focus Conditions",
        "",
        "| Condition | Subset | n | Median first edge ms | Median edge count | Sustained broadband mean | Driven power mean |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        if row["condition"] in focus:
            md.append(
                f"| {row['condition']} | {row['subset']} | {row['n_trials']} | "
                f"{row['median_first_edge_ms']:.1f} | {row['median_n_all_on']:.1f} | "
                f"{row['sustained_broadband_delta_mean']:.3f} | {row['driven_power_log2_delta_mean']:.3f} |"
            )

    md.extend(
        [
            "",
            "## Correlations",
            "",
            "| Condition | edge count vs sustained broadband | edge count vs driven power | first-edge lag vs driven power |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in corr_rows:
        if row["condition"] in focus:
            md.append(
                f"| {row['condition']} | {row['corr_n_edges_vs_sustained_broadband_delta']:.3f} | "
                f"{row['corr_n_edges_vs_driven_power_log2_delta']:.3f} | "
                f"{row['corr_first_edge_ms_vs_driven_power_log2_delta']:.3f} |"
            )

    md.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Use `amp250_freq26` TTL as a strong delivery QC signal: nearly all trials have early sensor activity.",
            "- Use `amp100_freq26` more cautiously: many trials have late or sparse sensor activity.",
            "- TTL filtering can test robustness, but it cannot create a cycle-level phase analysis.",
        ]
    )
    (OUT / "README.md").write_text("\n".join(md) + "\n")

    print(json.dumps({"summary_csv": str(OUT / "ttl_qc_metric_subset_summary.csv"), "correlations_csv": str(OUT / "ttl_qc_metric_correlations.csv"), "readme": str(OUT / "README.md")}, indent=2))


if __name__ == "__main__":
    main()
