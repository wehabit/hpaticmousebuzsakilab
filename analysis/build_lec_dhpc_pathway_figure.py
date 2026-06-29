#!/usr/bin/env python3
"""Pathway schematic: how back/trunk vibration could reach LEC and dorsal hippocampus.

Presentation teaching figure (NOT an atlas plate). Two elements:
  (1) a small stylized sagittal mouse-brain inset marking S1, dHPC, and LEC in
      their approximate positions, and
  (2) the canonical somatosensory -> medial-temporal route as a labelled flow:
      back/trunk skin -> spinal cord/thalamus -> S1 -> S2/parietal ->
      perirhinal/postrhinal cortex -> LEC -> (perforant path) -> dHPC,
      with the parallel arousal/neuromodulatory route shown as a dashed input.

The point the figure makes: our probes (LEC, dHPC) are deep medial-temporal
targets many synapses downstream of first-touch cortex, so low/theta frequencies
can follow but ~40-50 Hz degrades with each relay.

References for the wording (canonical anatomy + verified primary sources):
Allen Mouse Brain Atlas/CCF; Burwell & Amaral 1998; Doan et al. 2019;
Deshmukh & Knierim 2011; Witter (perforant path); Kandel PNS (DCML).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
CARD_LIGHT = "#F1E0E0"
S1_FILL = "#EFE9DF"


def text(ax, x, y, s, size=10, color=BLACK, weight=None, ha="center", va="center", z=25, style=None):
    ax.text(x, y, s, fontsize=size, color=color, weight=weight, ha=ha, va=va, zorder=z, style=style)


def arrow(ax, p0, p1, color=STONE_DARK, lw=2.0, ms=14, rad=0.0, ls="-", z=4):
    ax.add_patch(
        FancyArrowPatch(
            p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color,
            linestyle=ls, connectionstyle=f"arc3,rad={rad}", zorder=z,
        )
    )


def box(ax, cx, cy, w, h, title, sub=None, fc=FOG_LIGHT, ec=STONE, lw=1.6,
        title_color=BLACK, title_size=11.5, sub_color=COOL_GREY, sub_size=8.2, z=6):
    ax.add_patch(
        FancyBboxPatch(
            (cx - w / 2, cy - h / 2), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=lw, zorder=z,
        )
    )
    if sub:
        text(ax, cx, cy + h * 0.17, title, size=title_size, color=title_color, weight="bold", z=z + 2)
        text(ax, cx, cy - h * 0.24, sub, size=sub_size, color=sub_color, z=z + 2)
    else:
        text(ax, cx, cy, title, size=title_size, color=title_color, weight="bold", z=z + 2)
    return (cx, cy, w, h)


def draw_brain_inset(ax):
    """Stylized sagittal mouse brain (anterior left), marking S1, dHPC, LEC."""
    # Brain silhouette.
    pts = [
        (0.42, 3.02), (0.50, 3.42), (0.82, 3.74), (1.35, 3.96), (1.95, 4.02),
        (2.55, 3.92), (2.95, 3.60), (3.16, 3.12), (3.12, 2.70), (2.92, 2.44),
        (2.55, 2.34), (2.05, 2.32), (1.55, 2.34), (1.08, 2.40), (0.70, 2.58),
        (0.50, 2.80),
    ]
    ax.add_patch(Polygon(pts, closed=True, fc="#FAF9F5", ec=STONE, lw=1.7, zorder=3))
    # Olfactory bulb nub.
    ax.add_patch(Ellipse((0.42, 3.02), 0.42, 0.50, angle=18, fc="#FAF9F5", ec=STONE, lw=1.5, zorder=3))
    text(ax, 1.78, 4.35, "mouse brain — sagittal", size=8.6, color=COOL_GREY)
    text(ax, 0.55, 3.74, "ant.", size=7.2, color=COOL_GREY)
    text(ax, 3.05, 3.86, "post.", size=7.2, color=COOL_GREY)

    # S1 — dorsal cortex.
    ax.add_patch(Ellipse((1.70, 3.66), 0.74, 0.32, angle=-8, fc=S1_FILL, ec=STONE_DARK, lw=1.5, zorder=6))
    text(ax, 1.70, 3.66, "S1", size=10, weight="bold", color=BLACK, z=8)
    text(ax, 1.70, 4.02, "trunk area", size=7.0, color=COOL_GREY, z=8)

    # dHPC — under dorsal cortex (comma / curved band).
    ax.add_patch(Ellipse((2.05, 3.10), 0.62, 0.26, angle=-22, fc=CARD_LIGHT, ec=CARDINAL, lw=1.6, zorder=6))
    text(ax, 2.52, 3.16, "dHPC", size=9.0, weight="bold", color=CARDINAL, ha="left", z=8)

    # LEC — ventral / caudal (temporal).
    ax.add_patch(Ellipse((2.58, 2.62), 0.50, 0.24, angle=18, fc=CARD_LIGHT, ec=CARDINAL, lw=1.6, zorder=6))
    text(ax, 2.62, 2.36, "LEC", size=9.0, weight="bold", color=CARDINAL, z=8)

    # Vibration-on-back input cue.
    bx, by = 0.95, 1.55
    for i, dy in enumerate((0.0, 0.16, 0.32)):
        ax.plot([bx - 0.34, bx - 0.20, bx - 0.06, bx + 0.08, bx + 0.22],
                [by + dy, by + dy + 0.07, by + dy, by + dy - 0.07, by + dy],
                color=CARDINAL, lw=1.5, solid_capstyle="round", zorder=5)
    text(ax, bx + 0.06, by - 0.30, "vibration on back", size=7.6, color=CARDINAL, weight="bold")
    arrow(ax, (1.15, 2.02), (1.55, 2.55), color=CARDINAL, lw=1.4, ms=10, rad=-0.2, z=5)


def main():
    fig, ax = plt.subplots(figsize=(14.0, 5.7))
    ax.axis("off")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5.7)
    ax.set_facecolor("white")

    text(ax, 7.0, 5.46, "From the body to our probes: how back vibration could reach LEC & dorsal hippocampus",
         size=16.5, weight="bold")
    text(ax, 7.0, 5.12,
         "Canonical somatosensory → medial-temporal route — many synapses from the body surface to our probes.",
         size=9.4, color=COOL_GREY)

    # draw_brain_inset(ax)   # removed per request — the upper-left is left open (e.g. for the setup video)

    # ---- Flow: top row (periphery -> S1), left to right ----
    yt = 3.60
    w, h = 2.7, 1.34
    A = box(ax, 5.2, yt, w, h, "Back / trunk skin", "RA hair-follicle\nafferents (flutter)", fc=FOG_LIGHT, ec=STONE, title_size=12.5, sub_size=9.2)
    B = box(ax, 8.6, yt, w, h, "Spinal cord", "DRG · dorsal columns\n(gracile/cuneate)", fc=FOG_LIGHT, ec=STONE, title_size=12.5, sub_size=9.2)
    C = box(ax, 12.0, yt, w, h, "S1 — trunk area", "primary somatosensory\n(first cortical stage)",
            fc=S1_FILL, ec=STONE_DARK, lw=2.0, title_size=13.0, sub_size=9.2)
    arrow(ax, (A[0] + w / 2, yt), (B[0] - w / 2, yt))
    arrow(ax, (B[0] + w / 2, yt), (C[0] - w / 2, yt))

    # ---- Right-side turn down (cortico-cortical hierarchy) ----
    yb = 1.58
    arrow(ax, (C[0], yt - h / 2), (C[0], yb + h / 2 + 0.02), color=STONE_DARK, lw=2.0, ms=14)
    text(ax, C[0] + 0.22, (yt + yb) / 2, "cortico-cortical\nhierarchy", size=8.2, color=COOL_GREY, ha="left")

    # ---- Flow: bottom row (cortex -> MTL), right to left ----
    D = box(ax, 12.0, yb, w, h, "S2 / posterior", "parietal & insular\nassociation cortex", fc=FOG_LIGHT, ec=STONE, title_size=12.5, sub_size=9.2)
    E = box(ax, 8.6, yb, w, h, "Perirhinal / postrhinal", "cortex · multimodal\ngateway → LEC", fc=FOG_LIGHT, ec=STONE, title_size=11.5, sub_size=9.2)
    F = box(ax, 5.2, yb, w, h, "LEC", "lateral entorhinal\n(our probe)",
            fc=CARDINAL, ec=CARDINAL, title_color="white", sub_color="#F3DADA", title_size=14.0, sub_size=9.4)
    G = box(ax, 2.0, yb, w, h, "dHPC", "dorsal hippocampus\n(our probe)",
            fc=CARDINAL, ec=CARDINAL, title_color="white", sub_color="#F3DADA", title_size=13.5, sub_size=9.4)
    arrow(ax, (D[0] - w / 2, yb), (E[0] + w / 2, yb))
    arrow(ax, (E[0] - w / 2, yb), (F[0] + w / 2, yb))
    arrow(ax, (F[0] - w / 2, yb), (G[0] + w / 2, yb), color=CARDINAL, lw=2.2)
    text(ax, (F[0] + G[0]) / 2, yb + 0.86, "perforant path", size=8.6, color=CARDINAL, weight="bold", style="italic")

    for out in [OUT / "lec_dhpc_pathway.png", OUT / "lec_dhpc_pathway.svg", SVG_OUT / "lec_dhpc_pathway.svg"]:
        fig.savefig(out, dpi=180 if out.suffix == ".png" else None, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(OUT / "lec_dhpc_pathway.png")


if __name__ == "__main__":
    main()
