#!/usr/bin/env python3
"""Build a nuanced glymphatic-flow teaching schematic.

The goal is to preserve the simple sleep-vs-awake contrast while avoiding the
misleading "one big downward arrow" version of glymphatic flow.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Circle, Ellipse, FancyArrowPatch, FancyBboxPatch


OUT = Path("presentation/concept_figs")
SVG_OUT = Path("presentation/svg")
OUT.mkdir(parents=True, exist_ok=True)
SVG_OUT.mkdir(parents=True, exist_ok=True)

BLACK = "#2E2D29"
CARDINAL = "#8C1515"
COOL_GREY = "#53565A"
FOG = "#DAD7CB"
FOG_LIGHT = "#F4F4F4"
STONE = "#7F7776"
STONE_LIGHT = "#D4D1D1"
STONE_DARK = "#544948"


def arrow(ax, p0, p1, color=STONE_DARK, lw=2.5, ms=15, rad=0.0, alpha=1.0):
    ax.add_patch(
        FancyArrowPatch(
            p0,
            p1,
            arrowstyle="-|>",
            mutation_scale=ms,
            lw=lw,
            color=color,
            alpha=alpha,
            connectionstyle=f"arc3,rad={rad}",
        )
    )


def label(ax, x, y, text, size=9.5, color=BLACK, weight=None, ha="center", va="center"):
    ax.text(x, y, text, fontsize=size, color=color, weight=weight, ha=ha, va=va)


def rounded_box(ax, x, y, w, h, text, fc=FOG_LIGHT, ec=STONE, color=BLACK, size=9.0, weight=None):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            fc=fc,
            ec=ec,
            lw=1.4,
        )
    )
    label(ax, x + w / 2, y + h / 2, text, size=size, color=color, weight=weight)


def draw_brain_panel(ax, cx, cy, title, awake=False):
    brain_fc = "#EFEDE4" if not awake else "#F6F5F1"
    ax.add_patch(Ellipse((cx, cy), 3.35, 2.2, fc=brain_fc, ec=BLACK, lw=1.7))
    ax.add_patch(Arc((cx - 0.35, cy + 0.15), 1.15, 0.9, theta1=205, theta2=25, color=STONE, lw=1.2))
    ax.add_patch(Arc((cx + 0.35, cy + 0.15), 1.15, 0.9, theta1=155, theta2=-65, color=STONE, lw=1.2))
    ax.plot([cx, cx], [cy - 0.9, cy + 0.9], color=STONE_LIGHT, lw=1.2)
    label(ax, cx, cy + 1.45, title, size=15, weight="bold")

    rng = np.random.default_rng(4 if not awake else 5)
    for _ in range(24 if not awake else 30):
        x = cx + rng.uniform(-1.2, 1.2)
        y = cy + rng.uniform(-0.75, 0.75)
        if ((x - cx) / 1.55) ** 2 + ((y - cy) / 0.95) ** 2 < 0.85:
            ax.add_patch(Circle((x, y), 0.035 if not awake else 0.028, fc=CARDINAL, ec="none", alpha=0.9))

    # periarterial CSF entry, intraparenchymal exchange, and drainage routes
    if not awake:
        flow_lw = 4.3
        flow_alpha = 0.95
        small_lw = 2.5
        waste_count = 8
    else:
        flow_lw = 1.7
        flow_alpha = 0.52
        small_lw = 1.1
        waste_count = 3

    arrow(ax, (cx - 1.65, cy + 0.85), (cx - 0.78, cy + 0.45), color=STONE_DARK, lw=flow_lw, ms=18, rad=-0.12, alpha=flow_alpha)
    arrow(ax, (cx + 1.65, cy + 0.85), (cx + 0.78, cy + 0.45), color=STONE_DARK, lw=flow_lw * 0.8, ms=16, rad=0.12, alpha=flow_alpha)
    arrow(ax, (cx - 0.75, cy + 0.35), (cx - 0.25, cy - 0.1), color=STONE, lw=small_lw, ms=13, rad=0.12, alpha=flow_alpha)
    arrow(ax, (cx + 0.75, cy + 0.35), (cx + 0.25, cy - 0.1), color=STONE, lw=small_lw, ms=13, rad=-0.12, alpha=flow_alpha)
    arrow(ax, (cx, cy - 0.18), (cx, cy - 1.18), color=STONE_DARK, lw=flow_lw, ms=18, alpha=flow_alpha)
    label(ax, cx - 1.85, cy + 0.95, "CSF in\nperiarterial", size=8.2, color=COOL_GREY, ha="right")
    label(ax, cx + 1.85, cy + 0.95, "CSF in", size=8.2, color=COOL_GREY, ha="left")
    label(ax, cx - 1.05, cy - 0.12, "CSF-ISF\nexchange", size=8.0, color=COOL_GREY)
    label(ax, cx + 1.15, cy - 1.05, "outflow via\nperivenous /\nmeningeal lymphatics", size=7.8, color=COOL_GREY, ha="left")

    for i in range(waste_count):
        ax.add_patch(Circle((cx - 0.32 + 0.09 * i, cy - 1.38 - 0.03 * (i % 2)), 0.035, fc=CARDINAL, ec="none"))

    # state physiology boxes
    if not awake:
        ne = "NE: low mean,\nslow oscillations"
        wave = "large slow waves\nvasomotion + CSF pulses"
        clearance = "higher CSF-ISF exchange\nand waste clearance"
        box_ec = CARDINAL
    else:
        ne = "NE: higher tonic tone"
        wave = "smaller CSF pulses\nmore restricted exchange"
        clearance = "clearance still occurs,\nbut is reduced/different"
        box_ec = STONE
    rounded_box(ax, cx - 1.65, cy - 2.05, 1.45, 0.55, ne, fc=FOG_LIGHT, ec=box_ec, color=BLACK, size=7.9, weight="bold")
    rounded_box(ax, cx - 0.05, cy - 2.05, 1.65, 0.55, wave, fc=FOG_LIGHT, ec=box_ec, color=BLACK, size=7.7)
    rounded_box(ax, cx - 0.9, cy - 2.75, 1.8, 0.55, clearance, fc=FOG, ec=box_ec, color=BLACK, size=7.7, weight="bold")

    # small EEG/CSF pulse sketch
    t = np.linspace(0, 1.4, 160)
    if not awake:
        y = 0.10 * np.sin(2 * np.pi * 3.2 * t) + 0.035 * np.sin(2 * np.pi * 8 * t)
    else:
        y = 0.035 * np.sin(2 * np.pi * 8 * t) + 0.015 * np.sin(2 * np.pi * 19 * t)
    ax.plot(cx - 1.52 + t, cy + 1.1 + y, color=CARDINAL if not awake else COOL_GREY, lw=1.4)
    label(ax, cx - 0.8, cy + 1.26, "EEG / state rhythm", size=7.3, color=COOL_GREY)


def main():
    fig, ax = plt.subplots(figsize=(12.5, 7.2))
    ax.axis("off")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.set_facecolor("white")

    label(
        ax,
        6,
        6.65,
        "Glymphatic clearance: accurate simple model",
        size=18,
        weight="bold",
    )
    label(
        ax,
        6,
        6.28,
        "Not one downward drain: CSF enters along perivascular routes, exchanges with ISF, then drains out.",
        size=10.2,
        color=COOL_GREY,
    )

    draw_brain_panel(ax, 3.2, 4.35, "NREM / slow-wave sleep", awake=False)
    draw_brain_panel(ax, 8.8, 4.35, "Awake", awake=True)

    ax.plot([6, 6], [1.08, 5.85], color=STONE_LIGHT, lw=1.4, ls="--")

    rounded_box(
        ax,
        0.75,
        0.42,
        10.5,
        0.78,
        "Evidence nuance: mice have stronger direct tracer evidence for clearance.\n"
        "Humans have strong coupling evidence: slow waves, blood-volume/BOLD waves, and CSF oscillations.",
        fc=FOG_LIGHT,
        ec=STONE_LIGHT,
        color=BLACK,
        size=8.5,
    )
    label(
        ax,
        6,
        0.18,
        "Use as a teaching schematic. For mechanism: Xie 2013; Fultz 2019; Hauglund 2025.",
        size=8.0,
        color=COOL_GREY,
    )

    fig.savefig(OUT / "glymphatic_nuanced.png", dpi=180, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / "glymphatic_nuanced.svg", bbox_inches="tight", facecolor="white")
    fig.savefig(SVG_OUT / "glymphatic_nuanced.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(OUT / "glymphatic_nuanced.png")


if __name__ == "__main__":
    main()
