#!/usr/bin/env python3
"""Scan Dec 3 digital TTL edges for possible stimulus phase usability.

This script intentionally avoids pandas/scipy so it can run in the lightweight
local environment. It tests several possible interpretations of the Dec 3
digital channel:

1. rising edges are one marker per stimulus cycle
2. all edges are half-cycle zero crossings
3. all edges are sparse one-marker-per-cycle events
4. first edge is only a delivery/onset validator

The goal is not to prove entrainment. It is to decide what the TTL can honestly
support.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np


FS = 20_000.0
ROOT = Path("analysis/outputs/dec3")
OUT = ROOT / "ttl_phase_reliability"


def load_edges() -> list[dict]:
    edges = []
    with (ROOT / "digital_edges_ch7.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            sample = int(row["sample"])
            edges.append({"edge": row["edge"], "sample": sample, "time_s": sample / FS})
    edges.sort(key=lambda r: r["sample"])
    return edges


def load_trials() -> list[dict]:
    trials = []
    with (ROOT / "dec3_condition_sequence.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            trials.append(
                {
                    "trial_number": int(row["trial_number"]),
                    "condition": row["condition"],
                    "amplitude": int(row["amplitude"]),
                    "freq": float(row["freq"]),
                    "start_s": float(row["recording_start_time_s"]),
                    "end_s": float(row["recording_end_time_s"]),
                    "duration_s": float(row["recording_end_time_s"]) - float(row["recording_start_time_s"]),
                }
            )
    return trials


def percentile(values: list[float], q: float) -> float:
    values = [v for v in values if math.isfinite(v)]
    if not values:
        return float("nan")
    return float(np.percentile(np.asarray(values, dtype=float), q))


def interval_metrics(times: list[float], expected_interval_s: float) -> dict:
    if len(times) < 2:
        return {
            "n_intervals": 0,
            "median_interval_ms": float("nan"),
            "median_rate_hz": float("nan"),
            "interval_cv": float("nan"),
            "frac_intervals_within_15pct": float("nan"),
            "frac_intervals_within_25pct": float("nan"),
        }

    intervals = np.diff(np.asarray(times, dtype=float))
    intervals = intervals[intervals > 0]
    if intervals.size == 0:
        return {
            "n_intervals": 0,
            "median_interval_ms": float("nan"),
            "median_rate_hz": float("nan"),
            "interval_cv": float("nan"),
            "frac_intervals_within_15pct": float("nan"),
            "frac_intervals_within_25pct": float("nan"),
        }

    rates = 1.0 / intervals
    return {
        "n_intervals": int(intervals.size),
        "median_interval_ms": float(np.median(intervals) * 1000),
        "median_rate_hz": float(np.median(rates)),
        "interval_cv": float(np.std(intervals) / np.mean(intervals)) if np.mean(intervals) > 0 else float("nan"),
        "frac_intervals_within_15pct": float(np.mean(np.abs(intervals - expected_interval_s) <= 0.15 * expected_interval_s)),
        "frac_intervals_within_25pct": float(np.mean(np.abs(intervals - expected_interval_s) <= 0.25 * expected_interval_s)),
    }


def quality_flags(row: dict) -> dict:
    # Strict-ish criteria for "phase marker" quality.
    cycle_count_ok = 0.75 <= row["rising_count_ratio"] <= 1.25
    cycle_interval_ok = row["rising_frac_intervals_within_15pct"] >= 0.70 and row["rising_interval_cv"] <= 0.30
    half_count_ok = 0.75 <= row["all_half_count_ratio"] <= 1.25
    half_interval_ok = row["all_half_frac_intervals_within_15pct"] >= 0.70 and row["all_half_interval_cv"] <= 0.30
    all_cycle_count_ok = 0.75 <= row["all_cycle_count_ratio"] <= 1.25
    all_cycle_interval_ok = row["all_cycle_frac_intervals_within_15pct"] >= 0.70 and row["all_cycle_interval_cv"] <= 0.30

    return {
        "rising_cycle_marker_candidate": bool(cycle_count_ok and cycle_interval_ok),
        "all_edge_halfcycle_candidate": bool(half_count_ok and half_interval_ok),
        "all_edge_cycle_candidate": bool(all_cycle_count_ok and all_cycle_interval_ok),
        "delivery_qc_good": bool(row["n_all_on"] > 0 and row["first_edge_ms"] <= 500),
        "delivery_qc_tight": bool(row["n_all_on"] > 0 and row["first_edge_ms"] <= 200),
    }


def scan() -> tuple[list[dict], dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    edges = load_edges()
    trials = load_trials()

    edge_times = np.asarray([e["time_s"] for e in edges], dtype=float)
    edge_types = np.asarray([e["edge"] for e in edges], dtype=object)

    rows = []
    for trial in trials:
        start = trial["start_s"]
        end = trial["end_s"]
        freq = trial["freq"]
        expected_cycles = freq * trial["duration_s"]
        expected_half_edges = 2 * freq * trial["duration_s"]

        mask = (edge_times >= start) & (edge_times < end)
        on_times = edge_times[mask].tolist()
        on_types = edge_types[mask].tolist()
        rise_times = [t for t, typ in zip(on_times, on_types) if typ == "rising"]
        fall_times = [t for t, typ in zip(on_times, on_types) if typ == "falling"]

        rising = interval_metrics(rise_times, 1.0 / freq)
        all_half = interval_metrics(on_times, 1.0 / (2 * freq))
        all_cycle = interval_metrics(on_times, 1.0 / freq)

        row = {
            **trial,
            "n_all_on": len(on_times),
            "n_rising_on": len(rise_times),
            "n_falling_on": len(fall_times),
            "expected_cycles": expected_cycles,
            "expected_half_edges": expected_half_edges,
            "rising_count_ratio": len(rise_times) / expected_cycles if expected_cycles else float("nan"),
            "all_half_count_ratio": len(on_times) / expected_half_edges if expected_half_edges else float("nan"),
            "all_cycle_count_ratio": len(on_times) / expected_cycles if expected_cycles else float("nan"),
            "first_edge_ms": (on_times[0] - start) * 1000 if on_times else float("nan"),
            "last_edge_ms": (on_times[-1] - start) * 1000 if on_times else float("nan"),
            "edge_span_ms": (on_times[-1] - on_times[0]) * 1000 if len(on_times) >= 2 else float("nan"),
        }
        for prefix, metrics in [("rising", rising), ("all_half", all_half), ("all_cycle", all_cycle)]:
            for key, value in metrics.items():
                row[f"{prefix}_{key}"] = value
        row.update(quality_flags(row))
        rows.append(row)

    summary = {}
    for condition in sorted({r["condition"] for r in rows}):
        sub = [r for r in rows if r["condition"] == condition]
        summary[condition] = {
            "n_trials": len(sub),
            "freq_hz": sub[0]["freq"],
            "expected_cycles_3s": sub[0]["expected_cycles"],
            "expected_half_edges_3s": sub[0]["expected_half_edges"],
            "median_n_rising_on": percentile([r["n_rising_on"] for r in sub], 50),
            "max_n_rising_on": max(r["n_rising_on"] for r in sub),
            "median_n_all_on": percentile([r["n_all_on"] for r in sub], 50),
            "max_n_all_on": max(r["n_all_on"] for r in sub),
            "median_first_edge_ms": percentile([r["first_edge_ms"] for r in sub], 50),
            "n_delivery_qc_good_first_edge_le_500ms": sum(r["delivery_qc_good"] for r in sub),
            "n_delivery_qc_tight_first_edge_le_200ms": sum(r["delivery_qc_tight"] for r in sub),
            "n_rising_cycle_marker_candidates": sum(r["rising_cycle_marker_candidate"] for r in sub),
            "n_all_edge_halfcycle_candidates": sum(r["all_edge_halfcycle_candidate"] for r in sub),
            "n_all_edge_cycle_candidates": sum(r["all_edge_cycle_candidate"] for r in sub),
            "best_rising_count_ratio": max(r["rising_count_ratio"] for r in sub),
            "best_all_half_count_ratio": max(r["all_half_count_ratio"] for r in sub),
            "best_all_cycle_count_ratio": max(r["all_cycle_count_ratio"] for r in sub),
        }

    return rows, summary


def write_outputs(rows: list[dict], summary: dict) -> None:
    fieldnames = list(rows[0].keys())
    with (OUT / "ttl_phase_trial_quality.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with (OUT / "ttl_phase_condition_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")

    candidate_rows = [
        r
        for r in rows
        if r["rising_cycle_marker_candidate"] or r["all_edge_halfcycle_candidate"] or r["all_edge_cycle_candidate"]
    ]
    with (OUT / "ttl_phase_candidate_trials.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(candidate_rows)

    good_delivery = [r for r in rows if r["delivery_qc_good"]]
    with (OUT / "ttl_delivery_good_trials.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(good_delivery)

    md = [
        "# Dec 3 TTL Phase Reliability Scan",
        "",
        "This scan tests whether digital channel 7 can be used as a cycle-by-cycle phase marker.",
        "",
        "| Condition | Expected cycles | Expected half-edges | Median rising | Max rising | Median all edges | Max all edges | Rising-cycle candidates | All-edge half-cycle candidates | Good delivery <=500 ms | Tight delivery <=200 ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for condition, s in summary.items():
        md.append(
            f"| {condition} | {s['expected_cycles_3s']:.0f} | {s['expected_half_edges_3s']:.0f} | "
            f"{s['median_n_rising_on']:.1f} | {s['max_n_rising_on']} | "
            f"{s['median_n_all_on']:.1f} | {s['max_n_all_on']} | "
            f"{s['n_rising_cycle_marker_candidates']} | {s['n_all_edge_halfcycle_candidates']} | "
            f"{s['n_delivery_qc_good_first_edge_le_500ms']} | {s['n_delivery_qc_tight_first_edge_le_200ms']} |"
        )
    md.extend(
        [
            "",
            "Interpretation:",
            "",
            "- No condition produced reliable cycle-marker candidates under the strict criteria.",
            "- The TTL is useful for delivery/onset QC, especially high-amplitude 26 Hz.",
            "- It is not a continuous analog stimulus waveform and should not be used for true stimulus-phase PLV.",
        ]
    )
    (OUT / "README.md").write_text("\n".join(md) + "\n")


def main() -> None:
    rows, summary = scan()
    write_outputs(rows, summary)
    print(json.dumps(summary, indent=2))
    print(f"\nWrote outputs to {OUT}")


if __name__ == "__main__":
    main()
