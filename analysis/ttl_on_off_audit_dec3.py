#!/usr/bin/env python3
"""Audit Intan digital TTL edges against expected Dec 3 ON/OFF trial windows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CONDITION_ORDER = [
    "amp100_freq5",
    "amp180_freq5",
    "amp250_freq5",
    "amp100_freq26",
    "amp180_freq26",
    "amp250_freq26",
]


def load_edges(edges_csv: Path, sample_rate_hz: float) -> pd.DataFrame:
    edges = pd.read_csv(edges_csv)
    edges["time_s"] = edges["sample"] / sample_rate_hz
    return edges


def plot_counts(summary: pd.DataFrame, output: Path) -> None:
    frame = summary.set_index("condition").reindex(CONDITION_ORDER).reset_index()
    x = np.arange(len(frame))
    width = 0.35
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.bar(x - width / 2, frame["mean_on_rising_edges"], width=width, color="#4C78A8", label="ON")
    ax.bar(x + width / 2, frame["mean_off_rising_edges"], width=width, color="#54A24B", label="OFF")
    ax.set_xticks(x)
    ax.set_xticklabels(frame["condition"], rotation=30, ha="right")
    ax.set_ylabel("Mean rising TTL edges per trial")
    ax.set_title("TTL Rising Edges in Expected ON vs OFF Windows")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequence", type=Path, required=True)
    parser.add_argument("--edges-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sample-rate-hz", type=float, default=20000)
    parser.add_argument("--margin-s", type=float, default=0.0)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    sequence = pd.read_csv(args.sequence)
    edges = load_edges(args.edges_csv, args.sample_rate_hz)
    rising = edges[edges["edge"] == "rising"]["time_s"].to_numpy()
    falling = edges[edges["edge"] == "falling"]["time_s"].to_numpy()

    rows_out = []
    for row in sequence.itertuples(index=False):
        on_start = float(row.recording_start_time_s) + args.margin_s
        on_end = float(row.recording_start_time_s) + float(row.on_time_s) - args.margin_s
        off_start = float(row.recording_end_time_s) + args.margin_s
        off_end = float(row.recording_end_time_s) + float(row.off_time_s) - args.margin_s
        on_rising = int(np.sum((rising >= on_start) & (rising < on_end)))
        off_rising = int(np.sum((rising >= off_start) & (rising < off_end)))
        on_falling = int(np.sum((falling >= on_start) & (falling < on_end)))
        off_falling = int(np.sum((falling >= off_start) & (falling < off_end)))
        rows_out.append(
            {
                "trial_number": int(row.trial_number),
                "condition": row.condition,
                "amplitude": int(row.amplitude),
                "frequency": int(row.freq),
                "on_start_s": on_start,
                "on_end_s": on_end,
                "off_start_s": off_start,
                "off_end_s": off_end,
                "on_rising_edges": on_rising,
                "off_rising_edges": off_rising,
                "on_falling_edges": on_falling,
                "off_falling_edges": off_falling,
            }
        )

    trial = pd.DataFrame(rows_out)
    trial.to_csv(args.output_dir / "ttl_on_off_trial_audit.csv", index=False)
    summary = (
        trial.groupby(["condition", "amplitude", "frequency"], as_index=False)
        .agg(
            n_trials=("trial_number", "count"),
            mean_on_rising_edges=("on_rising_edges", "mean"),
            mean_off_rising_edges=("off_rising_edges", "mean"),
            median_on_rising_edges=("on_rising_edges", "median"),
            median_off_rising_edges=("off_rising_edges", "median"),
            trials_with_on_edges=("on_rising_edges", lambda x: int((x > 0).sum())),
            trials_with_off_edges=("off_rising_edges", lambda x: int((x > 0).sum())),
        )
    )
    summary.to_csv(args.output_dir / "ttl_on_off_condition_summary.csv", index=False)
    plot_counts(summary, args.output_dir / "ttl_on_off_counts.png")

    total_on = int(trial["on_rising_edges"].sum())
    total_off = int(trial["off_rising_edges"].sum())
    report = {
        "edges_csv": str(args.edges_csv),
        "sequence": str(args.sequence),
        "output_dir": str(args.output_dir),
        "total_on_rising_edges": total_on,
        "total_off_rising_edges": total_off,
        "trials_with_on_edges": int((trial["on_rising_edges"] > 0).sum()),
        "trials_with_off_edges": int((trial["off_rising_edges"] > 0).sum()),
        "interpretation": "TTL edges are audited against expected config ON/OFF windows. Use as QC because digital bursts include pre/post/test activity and do not cleanly enumerate all trials.",
    }
    (args.output_dir / "ttl_on_off_audit_summary.json").write_text(json.dumps(report, indent=2) + "\n")

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 TTL ON/OFF Audit</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1200px;line-height:1.45}"
        "img{width:100%;border:1px solid #d9dee5;margin-bottom:30px}"
        "a{color:#0f6b78;font-weight:600}</style></head><body>",
        "<h1>Dec 3 TTL ON/OFF Audit</h1>",
        "<p>Counts bit-7 digital rising edges inside expected ON and OFF windows from the Dec 3 schedule.</p>",
        "<p>Use this as timing QC, not as the only source of trial labels.</p>",
        "<h2>TTL Counts</h2><img src='ttl_on_off_counts.png'>",
        "<p>Back to <a href='../RESULTS_DASHBOARD.html'>main dashboard</a>.</p>",
        "</body></html>",
    ]
    (args.output_dir / "index.html").write_text("\n".join(html))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
