#!/usr/bin/env python3
"""Build a simple mouse cortical sensory-area schematic.

This is a presentation-safe teaching figure, not an atlas plate. It places the
major primary sensory areas in their approximate dorsal/lateral positions and
marks the S1 trunk/back representation (Allen label: SSp-tr).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Polygon


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


def label(ax, x, y, text, size=10, color=BLACK, weight=None, ha="center", va="center", zorder=20):
    ax.text(x, y, text, fontsize=size, color=color, weight=weight, ha=ha, va=va, zorder=zorder)


def arrow(ax, p0, p1, color=STONE_DARK, lw=1.8, ms=12, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            p0,
            p1,
            arrowstyle="-|>",
            mutation_scale=ms,
            lw=lw,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
        )
    )


def blob(ax, points, fc, ec, lw=1.4, alpha=0.88, z=5):
    patch = Polygon(points, closed=True, fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=z)
    ax.add_patch(patch)
    return patch


def draw_mouse_body_inset(ax):
    x0, y0 = 8.35, 0.75
    ax.add_patch(Ellipse((x0 + 0.62, y0 + 0.30), 1.22, 0.58, fc=FOG_LIGHT, ec=STONE_LIGHT, lw=1.0))
    ax.add_patch(Circle((x0 - 0.05, y0 + 0.33), 0.28, fc=FOG_LIGHT, ec=STONE_LIGHT, lw=1.0))
    ax.add_patch(Circle((x0 - 0.16, y0 + 0.58), 0.14, fc=FOG_LIGHT, ec=STONE_LIGHT, lw=1.0))
    ax.plot([x0 + 1.23, x0 + 1.75, x0 + 1.95], [y0 + 0.32, y0 + 0.60, y0 + 0.80],
            color=STONE_LIGHT, lw=2.2, solid_capstyle="round")
    # Back/trunk skin target.
    ax.add_patch(Ellipse((x0 + 0.52, y0 + 0.47), 0.58, 0.20, angle=7, fc=CARDINAL, ec="none", alpha=0.78))
    label(ax, x0 + 0.62, y0 - 0.12, "skin target:\nback / trunk", size=8.0, color=COOL_GREY)


def main():
    fig, ax = plt.subplots(figsize=(10.8, 5.3))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.3)
    ax.set_facecolor("white")

    label(ax, 5.0, 5.02, "Where body vibration first maps in mouse cortex", size=17, weight="bold")
    label(ax, 5.0, 4.70, "S1 contains a body map; the back/trunk zone is in primary somatosensory trunk area (SSp-tr).",
          size=9.2, color=COOL_GREY)

    # Dorsal mouse cortex silhouette, anterior left / posterior right.
    ax.add_patch(Ellipse((4.78, 2.58), 6.95, 3.15, fc="#FAF9F5", ec=STONE_LIGHT, lw=1.7, zorder=1))
    ax.plot([4.78, 4.78], [1.18, 3.97], color=STONE_LIGHT, lw=1.0, ls="--", zorder=2)
    label(ax, 1.45, 4.18, "anterior", size=8.8, color=COOL_GREY)
    label(ax, 8.15, 4.18, "posterior", size=8.8, color=COOL_GREY)
    label(ax, 4.78, 4.18, "midline", size=8.0, color=COOL_GREY)

    # Approximate primary sensory areas, one hemisphere emphasized.
    s1 = blob(
        ax,
        [(4.28, 3.50), (5.12, 3.55), (5.83, 3.12), (5.88, 2.35), (5.25, 1.82),
         (4.25, 1.78), (3.62, 2.22), (3.55, 2.96)],
        fc="#EFE9DF",
        ec=STONE_DARK,
        lw=1.4,
        alpha=0.95,
        z=4,
    )
    v1 = blob(
        ax,
        [(6.18, 3.45), (7.15, 3.28), (7.64, 2.74), (7.55, 2.05), (6.72, 1.76),
         (6.08, 2.20), (5.94, 2.90)],
        fc="#FFFFFF",
        ec=STONE,
        lw=1.35,
        alpha=0.95,
        z=4,
    )
    a1 = blob(
        ax,
        [(6.18, 1.72), (6.92, 1.62), (7.42, 1.30), (7.25, 0.92), (6.40, 0.92),
         (5.92, 1.20)],
        fc="#F7F7F5",
        ec=STONE,
        lw=1.35,
        alpha=0.98,
        z=4,
    )

    label(ax, 4.78, 2.95, "S1", size=21, weight="bold", color=BLACK)
    label(ax, 4.78, 2.62, "somatosensory", size=8.5, color=COOL_GREY)
    label(ax, 6.78, 2.58, "V1", size=17, weight="bold", color=STONE_DARK)
    label(ax, 6.78, 2.27, "visual", size=8.0, color=COOL_GREY)
    label(ax, 6.70, 1.25, "A1", size=16, weight="bold", color=STONE_DARK)
    label(ax, 6.70, 1.02, "auditory", size=8.0, color=COOL_GREY)

    # S1 trunk/back representation: approximate SSp-tr zone.
    rng = np.random.default_rng(8)
    dot_center = np.array([4.42, 2.28])
    for dx, dy in rng.normal(scale=[0.13, 0.10], size=(14, 2)):
        ax.add_patch(Circle(dot_center + [dx, dy], 0.045, fc=CARDINAL, ec="white", lw=0.25, zorder=8))
    ax.add_patch(Ellipse(dot_center, 0.78, 0.52, angle=-12, fc="none", ec=CARDINAL, lw=1.7, zorder=7))
    label(ax, 3.08, 1.30, "dots = S1 trunk/back map\n(approx. Allen SSp-tr)", size=8.6,
          color=CARDINAL, weight="bold", ha="left")
    arrow(ax, (3.82, 1.62), (4.23, 2.10), color=CARDINAL, lw=1.5, ms=11, rad=-0.16)

    # Recorded regions from this project. These are not first-order touch maps.
    ax.add_patch(Ellipse((5.58, 1.58), 0.72, 0.28, angle=-8, fc="#FFFFFF", ec=CARDINAL,
                         lw=1.35, ls="--", alpha=0.88, zorder=8))
    label(ax, 5.82, 1.34, "dHPC\n(deep)", size=7.2, color=CARDINAL, weight="bold")
    ax.add_patch(Ellipse((7.45, 0.86), 0.70, 0.25, angle=8, fc="#FFFFFF", ec=CARDINAL,
                         lw=1.35, ls="--", alpha=0.88, zorder=8))
    label(ax, 7.48, 0.62, "LEC\nventral/lateral", size=7.1, color=CARDINAL, weight="bold")

    # Tiny route reminder.
    ax.add_patch(FancyBboxPatch((0.50, 0.42), 3.10, 0.58, boxstyle="round,pad=0.018,rounding_size=0.07",
                                fc=FOG_LIGHT, ec=STONE_LIGHT, lw=1.0))
    label(ax, 2.05, 0.71, "skin vibration → thalamus → S1", size=8.7, color=BLACK, weight="bold")

    draw_mouse_body_inset(ax)

    label(ax, 5.0, 0.14,
          "Schematic, not an atlas plate. Dashed dHPC/LEC markers = recorded downstream regions, not first touch maps. Reference: Allen Mouse Brain Atlas/CCF.",
          size=7.6, color=COOL_GREY)

    for out in [OUT / "mouse_cortical_sensory_map.png", OUT / "mouse_cortical_sensory_map.svg",
                SVG_OUT / "mouse_cortical_sensory_map.svg"]:
        fig.savefig(out, dpi=180 if out.suffix == ".png" else None, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(OUT / "mouse_cortical_sensory_map.png")


if __name__ == "__main__":
    main()
