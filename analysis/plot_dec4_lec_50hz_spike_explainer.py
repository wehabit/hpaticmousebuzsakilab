#!/usr/bin/env python3
"""Write a dependency-free SVG explainer for Dec 4 LEC 50 Hz spikes."""

from __future__ import annotations

import csv
from pathlib import Path


IN = Path("analysis/outputs/cross_dataset_spike_compare/dec4_LEC_unit_condition_stats.csv")
OUT = Path("analysis/outputs/dec4/teaching/lec_50hz_spike_population_vs_responsive.svg")


def scale(value: float, xmin: float, xmax: float, left: float, width: float) -> float:
    return left + (value - xmin) / (xmax - xmin) * width


def bar(svg: list[str], x0: float, x1: float, y: float, h: float, color: str) -> None:
    x = min(x0, x1)
    w = abs(x1 - x0)
    svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{color}" opacity="0.88"/>')


def text(svg: list[str], x: float, y: float, body: str, size: int = 12, anchor: str = "start", weight: str = "400") -> None:
    svg.append(
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="#222">{body}</text>'
    )


def main() -> None:
    rows = list(csv.DictReader(IN.open()))
    f50 = [r for r in rows if r["condition"].endswith("freq50")]
    clusters = sorted({r["cluster_id"] for r in f50}, key=lambda x: int(x))

    per_unit = []
    for cid in clusters:
        ur = sorted(
            [r for r in f50 if r["cluster_id"] == cid],
            key=lambda r: int(r["condition"].split("_")[0].replace("amp", "")),
        )
        deltas = [float(r["mean_delta_hz"]) for r in ur]
        per_unit.append({"cluster_id": cid, "mean": sum(deltas) / len(deltas), "deltas": deltas})

    per_unit = sorted(per_unit, key=lambda r: r["mean"])
    responsive = sorted(
        [r for r in f50 if r["responsive_q05_within_unit_set"] == "True"],
        key=lambda r: float(r["mean_delta_hz"]),
    )

    w, h = 1280, 620
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    text(svg, 640, 34, "Dec 4 LEC 50 Hz spikes: population suppression is not the same as every responsive unit being suppressed", 18, "middle", "700")

    # Panel 1: per-unit mean.
    left, top, width, row_h = 70, 78, 310, 24
    axis0 = scale(0, -1.5, 1.5, left, width)
    text(svg, left, top - 22, "Population view: 11 down, 4 up", 15, weight="700")
    svg.append(f'<line x1="{axis0:.1f}" y1="{top-8}" x2="{axis0:.1f}" y2="{top + row_h*len(per_unit)+4}" stroke="#111" stroke-width="1"/>')
    for i, row in enumerate(per_unit):
        y = top + i * row_h
        val = row["mean"]
        x = scale(val, -1.5, 1.5, left, width)
        color = "#1B9E77" if val >= 0 else "#C43A31"
        bar(svg, axis0, x, y, row_h - 5, color)
        text(svg, left - 12, y + 14, row["cluster_id"], 10, "end")
        text(svg, x + (4 if val >= 0 else -4), y + 14, f"{val:+.2f}", 10, "start" if val >= 0 else "end")
    text(svg, left + width / 2, top + row_h * len(per_unit) + 34, "mean ON-OFF firing change across 50 Hz amps (Hz)", 11, "middle")

    # Panel 2: responsive tests only.
    left, top, width, row_h = 495, 105, 320, 35
    axis0 = scale(0, -2.4, 2.4, left, width)
    text(svg, left, 56, "Responsive tests only: 4 down, 4 up", 15, weight="700")
    text(svg, left, 77, "These are the unit-condition rows that pass q<0.05.", 11)
    svg.append(f'<line x1="{axis0:.1f}" y1="{top-8}" x2="{axis0:.1f}" y2="{top + row_h*len(responsive)+4}" stroke="#111" stroke-width="1"/>')
    for i, row in enumerate(responsive):
        y = top + i * row_h
        val = float(row["mean_delta_hz"])
        x = scale(val, -2.4, 2.4, left, width)
        color = "#1B9E77" if val >= 0 else "#C43A31"
        label = f"cl {row['cluster_id']} {row['condition'].split('_')[0]}"
        bar(svg, axis0, x, y, row_h - 8, color)
        text(svg, left - 12, y + 17, label, 10, "end")
        text(svg, x + (4 if val >= 0 else -4), y + 17, f"{val:+.2f}", 10, "start" if val >= 0 else "end")
    text(svg, left + width / 2, top + row_h * len(responsive) + 34, "ON-OFF firing change (Hz)", 11, "middle")

    # Panel 3: unit 87 dose line with context units.
    left, top, width, height = 930, 115, 250, 300
    text(svg, left, 56, "Soft spot: up-going unit 87", 15, weight="700")
    text(svg, left, 77, "Dose-like increase could be neural or pickup-related.", 11)
    amps = [100, 180, 250]
    xmin, xmax, ymin, ymax = 90, 260, -2.4, 2.4
    xpts = [scale(a, xmin, xmax, left, width) for a in amps]
    y0 = top + height - (0 - ymin) / (ymax - ymin) * height
    svg.append(f'<line x1="{left}" y1="{y0:.1f}" x2="{left+width}" y2="{y0:.1f}" stroke="#111" stroke-width="1"/>')
    for tick in [-2, -1, 0, 1, 2]:
        y = top + height - (tick - ymin) / (ymax - ymin) * height
        svg.append(f'<line x1="{left-4}" y1="{y:.1f}" x2="{left+width}" y2="{y:.1f}" stroke="#ddd" stroke-width="1"/>')
        text(svg, left - 10, y + 4, str(tick), 10, "end")
    for a, x in zip(amps, xpts):
        text(svg, x, top + height + 22, str(a), 10, "middle")

    by_cluster = {r["cluster_id"]: r for r in per_unit}
    for cid, color, stroke in [("72", "#C43A31", 2), ("82", "#C43A31", 2), ("87", "#1B9E77", 4), ("88", "#1B9E77", 2)]:
        vals = by_cluster[cid]["deltas"]
        pts = []
        for x, val in zip(xpts, vals):
            y = top + height - (val - ymin) / (ymax - ymin) * height
            pts.append(f"{x:.1f},{y:.1f}")
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
        svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="{stroke}" opacity="0.9"/>')
        text(svg, xpts[-1] + 8, top + height - (vals[-1] - ymin) / (ymax - ymin) * height + 4, f"cl {cid}", 10)
    text(svg, left + width / 2, top + height + 44, "50 Hz amplitude", 11, "middle")
    text(svg, left - 45, top + height / 2, "Hz", 11, "middle")

    svg.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
