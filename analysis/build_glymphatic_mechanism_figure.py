#!/usr/bin/env python3
"""Build a more mechanistic glymphatic-flow schematic.

This is the "less high-level" companion to glymphatic_nuanced.png. It is still a
cartoon, but it explicitly draws the compartments and control signals that the
one-slide overview compresses away.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, PathPatch
from matplotlib.path import Path as MplPath


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
PARCHMENT = "#F8F6EF"


def label(ax, x, y, text, size=9, color=BLACK, weight=None, ha="center", va="center", style=None):
    ax.text(x, y, text, fontsize=size, color=color, weight=weight, ha=ha, va=va, style=style)


def box(ax, x, y, w, h, text, fc=FOG_LIGHT, ec=STONE_LIGHT, size=8.8, color=BLACK, weight=None):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.025,rounding_size=0.08",
        fc=fc,
        ec=ec,
        lw=1.25,
    )
    ax.add_patch(patch)
    label(ax, x + w / 2, y + h / 2, text, size=size, color=color, weight=weight)
    return patch


def arrow(ax, p0, p1, color=STONE_DARK, lw=2.0, ms=14, alpha=1.0, rad=0.0):
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


def curve(ax, points, color=STONE_DARK, lw=3, alpha=1.0, ls="-"):
    verts = [points[0]]
    codes = [MplPath.MOVETO]
    for p in points[1:]:
        verts.append(p)
        codes.append(MplPath.LINETO)
    ax.add_patch(PathPatch(MplPath(verts, codes), fill=False, color=color, lw=lw, alpha=alpha, ls=ls, capstyle="round"))


def draw_microanatomy(ax):
    label(ax, 3.45, 5.96, "1. Where the fluid moves", size=13.5, weight="bold")
    label(
        ax,
        3.45,
        5.69,
        "CSF enters along vessels, exchanges with interstitial fluid, then drains out",
        size=8.6,
        color=COOL_GREY,
    )

    # Brain tissue field.
    ax.add_patch(
        FancyBboxPatch(
            (0.35, 1.08),
            6.2,
            4.45,
            boxstyle="round,pad=0.03,rounding_size=0.18",
            fc=PARCHMENT,
            ec=STONE_LIGHT,
            lw=1.3,
        )
    )
    label(ax, 0.58, 5.28, "brain tissue / interstitial space", size=8.3, color=COOL_GREY, ha="left")

    # Periarterial inflow vessel, drawn as a double tube.
    curve(ax, [(0.65, 4.55), (1.55, 4.82), (2.45, 4.55), (3.1, 4.18)], color=STONE_DARK, lw=15, alpha=0.18)
    curve(ax, [(0.65, 4.55), (1.55, 4.82), (2.45, 4.55), (3.1, 4.18)], color=CARDINAL, lw=6.5, alpha=0.92)
    curve(ax, [(0.65, 4.55), (1.55, 4.82), (2.45, 4.55), (3.1, 4.18)], color=BLACK, lw=0.8, alpha=0.9)
    label(ax, 1.42, 5.18, "artery", size=8.8, color=CARDINAL, weight="bold")
    label(ax, 2.65, 4.95, "periarterial\nCSF space", size=8.0, color=STONE_DARK)
    arrow(ax, (0.72, 4.96), (2.82, 4.55), color=STONE_DARK, lw=3.2, ms=18, rad=-0.08)
    label(ax, 1.58, 5.45, "CSF influx", size=9.2, color=STONE_DARK, weight="bold")

    # Astrocyte endfeet around the vessel.
    for x, y in [(1.05, 4.1), (1.45, 4.28), (1.95, 4.2), (2.38, 4.05), (2.78, 3.88)]:
        ax.add_patch(Ellipse((x, y), 0.28, 0.15, angle=-25, fc=FOG, ec=STONE, lw=0.7))
    label(ax, 2.15, 3.62, "astrocyte endfeet\nAQP4-rich water route", size=7.7, color=COOL_GREY)

    # CSF -> ISF exchange arrows.
    for p0, p1, rad in [((2.75, 4.1), (3.45, 3.45), 0.1), ((2.15, 4.0), (2.65, 3.25), -0.12), ((3.0, 3.86), (3.85, 3.12), 0.14)]:
        arrow(ax, p0, p1, color=STONE, lw=1.8, ms=12, rad=rad)
    label(ax, 3.55, 3.72, "CSF mixes\nwith ISF", size=8.6, color=BLACK, weight="bold")

    # Solutes / waste and drainage toward venous/meningeal routes.
    rng = np.random.default_rng(12)
    for _ in range(34):
        x = rng.uniform(2.8, 5.65)
        y = rng.uniform(1.75, 4.2)
        ax.add_patch(Circle((x, y), 0.035, fc=CARDINAL, ec="none", alpha=0.85))
    label(ax, 5.7, 4.12, "amyloid/tau-like\nsolutes", size=8.0, color=CARDINAL, ha="right")

    curve(ax, [(5.95, 1.92), (5.2, 2.04), (4.65, 2.28), (4.05, 2.55)], color=STONE_DARK, lw=13, alpha=0.20)
    curve(ax, [(5.95, 1.92), (5.2, 2.04), (4.65, 2.28), (4.05, 2.55)], color=STONE_DARK, lw=5.4, alpha=0.86)
    label(ax, 5.9, 1.55, "vein / outflow\nroute", size=8.4, color=STONE_DARK, ha="right")
    for p0, p1 in [((4.2, 2.75), (5.28, 2.08)), ((4.75, 2.35), (5.85, 1.95)), ((3.75, 2.95), (4.9, 2.2))]:
        arrow(ax, p0, p1, color=STONE_DARK, lw=1.7, ms=12, alpha=0.82)
    label(ax, 4.9, 1.22, "clearance toward perivenous /\nmeningeal lymphatic drainage", size=8.2, color=COOL_GREY)

    # Important anti-overclaim.
    box(
        ax,
        0.58,
        1.28,
        2.85,
        0.72,
        "Not a single drain:\nlocal exchange + perivascular outflow",
        fc=FOG_LIGHT,
        ec=CARDINAL,
        size=7.8,
        weight="bold",
    )


def trace(ax, x0, y0, w, amp, freq, color, label_text, y_label=None, phase=0.0, noise=0.0):
    t = np.linspace(0, 1, 300)
    rng = np.random.default_rng(1)
    y = y0 + amp * np.sin(2 * np.pi * freq * t + phase) + noise * rng.normal(size=t.size)
    ax.plot(x0 + w * t, y, color=color, lw=1.55)
    if y_label:
        label(ax, x0 - 0.08, y0, y_label, size=7.5, color=COOL_GREY, ha="right")
    label(ax, x0 + w + 0.08, y0, label_text, size=7.2, color=color, ha="left")


def draw_state_control(ax):
    label(ax, 9.55, 5.96, "2. What changes in NREM sleep", size=13.5, weight="bold")
    label(ax, 9.55, 5.69, "Slow neural/vascular rhythms act like a pump", size=8.6, color=COOL_GREY)

    # Two state cards.
    ax.add_patch(
        FancyBboxPatch((7.12, 3.45), 4.65, 1.9, boxstyle="round,pad=0.025,rounding_size=0.08",
                       fc=PARCHMENT, ec=CARDINAL, lw=1.35)
    )
    ax.add_patch(
        FancyBboxPatch((7.12, 1.18), 4.65, 1.78, boxstyle="round,pad=0.025,rounding_size=0.08",
                       fc=FOG_LIGHT, ec=STONE, lw=1.35)
    )
    label(ax, 7.45, 5.15, "NREM / slow-wave sleep", size=9.8, weight="bold", ha="left")
    label(ax, 7.45, 2.78, "Awake", size=9.8, weight="bold", ha="left")

    # NREM traces.
    trace(ax, 7.55, 4.82, 1.25, 0.10, 2.5, CARDINAL, "slow waves", "EEG")
    trace(ax, 7.55, 4.45, 1.25, 0.08, 1.5, STONE_DARK, "NE oscill.", "NE", phase=0.9)
    trace(ax, 7.55, 4.08, 1.25, 0.075, 1.5, BLACK, "diameter", "vessel", phase=1.45)
    trace(ax, 7.55, 3.72, 1.25, 0.075, 1.5, STONE, "CSF pulses", "CSF", phase=2.15)

    arrow(ax, (9.18, 4.28), (9.75, 4.28), color=CARDINAL, lw=2.2, ms=15)
    label(ax, 10.58, 4.52, "larger perivascular\npulses", size=8.0, color=BLACK, weight="bold")
    label(ax, 10.58, 3.94, "higher CSF-ISF exchange\nand solute clearance", size=8.0, color=CARDINAL, weight="bold")

    # Awake traces.
    trace(ax, 7.55, 2.47, 1.25, 0.032, 9.0, COOL_GREY, "desync.", "EEG", noise=0.01)
    trace(ax, 7.55, 2.14, 1.25, 0.018, 4.0, STONE_DARK, "tonic NE", "NE", noise=0.008)
    trace(ax, 7.55, 1.82, 1.25, 0.025, 3.8, BLACK, "small pulses", "vessel", noise=0.006)
    trace(ax, 7.55, 1.50, 1.25, 0.024, 3.0, STONE, "CSF pulses", "CSF", noise=0.004)

    arrow(ax, (9.18, 1.98), (9.75, 1.98), color=STONE, lw=1.7, ms=12, alpha=0.8)
    label(ax, 10.55, 2.20, "clearance still occurs", size=8.0, color=BLACK, weight="bold")
    label(ax, 10.55, 1.68, "but is reduced / different\nfrom NREM", size=8.0, color=COOL_GREY)

    box(
        ax,
        7.18,
        0.34,
        4.55,
        0.5,
        "Key nuance: low NE is not just off;\nslow NE/vascular oscillations appear important.",
        fc=FOG_LIGHT,
        ec=STONE_LIGHT,
        size=7.4,
        color=COOL_GREY,
    )


def main():
    fig, ax = plt.subplots(figsize=(14.2, 8.0))
    ax.axis("off")
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 6.65)

    label(ax, 6.2, 6.48, "Glymphatic flow: mechanistic cartoon", size=18, weight="bold")
    label(
        ax,
        6.2,
        6.25,
        "Still simplified, but now showing compartments, exchange, drainage, and state-dependent pumping.",
        size=8.8,
        color=COOL_GREY,
    )
    ax.plot([6.85, 6.85], [0.25, 6.08], color=STONE_LIGHT, lw=1.2, ls="--")

    draw_microanatomy(ax)
    draw_state_control(ax)

    box(
        ax,
        0.55,
        0.18,
        6.0,
        0.55,
        "Evidence strength: direct tracer clearance is strongest in mice/rodents;\nhuman work mainly shows coupled EEG, blood-volume/BOLD, and CSF-flow oscillations.",
        fc=FOG_LIGHT,
        ec=STONE_LIGHT,
        size=7.25,
        color=COOL_GREY,
    )
    label(ax, 9.45, 0.12, "Mechanism anchors: Xie 2013; Fultz 2019; Hauglund 2025", size=7.8, color=COOL_GREY)

    fig.savefig(OUT / "glymphatic_mechanistic_detail.png", dpi=180, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / "glymphatic_mechanistic_detail.svg", bbox_inches="tight", facecolor="white")
    fig.savefig(SVG_OUT / "glymphatic_mechanistic_detail.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(OUT / "glymphatic_mechanistic_detail.png")


if __name__ == "__main__":
    main()
