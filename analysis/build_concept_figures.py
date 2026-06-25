#!/usr/bin/env python
"""Clean schematic illustrations for the lay-audience talk's concept slides.
Outputs presentation/concept_figs/*.png in the deck's navy/teal style.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Arc, Polygon, Ellipse

OUT = Path("presentation/concept_figs"); OUT.mkdir(parents=True, exist_ok=True)
BLACK = "#2E2D29"
CARDINAL = "#8C1515"
COOL_GREY = "#53565A"
FOG = "#DAD7CB"
FOG_LIGHT = "#F4F4F4"
STONE = "#7F7776"
STONE_LIGHT = "#D4D1D1"
STONE_DARK = "#544948"
LAGUNITA = "#007C92"
POPPY = "#E98300"
PALO_ALTO = "#175E54"

# Legacy variable names kept for the figure code; mapped to Stanford neutrals.
NAVY, TEAL, GOLD, RED, GREEN = BLACK, STONE, STONE_DARK, CARDINAL, STONE_DARK
GREY, LIGHT = COOL_GREY, FOG


def box(ax, x, y, w, h, text, fc, tc="white", fs=12, ec=None, lw=1.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.08",
                                fc=fc, ec=ec or fc, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc, fontsize=fs, weight="bold")


def arrow(ax, p0, p1, color=NAVY, text=None, lw=2.4, fs=10, dy=0.12):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=20, color=color, lw=lw))
    if text:
        ax.text((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + dy, text, ha="center", va="bottom", fontsize=fs, color=color)


def newfig(w=11, h=4.8):
    fig, ax = plt.subplots(figsize=(w, h)); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10 * h / w)
    return fig, ax


def save(fig, name):
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight", facecolor="white"); plt.close(fig)
    print("wrote", OUT / name)


# ---------------- 7. STADIUM: LFP vs spikes ----------------
def stadium():
    fig, ax = plt.subplots(figsize=(11, 5.2)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 5.2)
    ax.text(5, 4.95, "One electrode, two readouts: LFP vs. single-unit activity", ha="center", fontsize=16, weight="bold", color=NAVY)
    t = np.linspace(0, 10, 2000); rng = np.random.default_rng(1)
    ax.text(0.0, 4.45, "CROWD ROAR  (field potential, LFP)", fontsize=13, weight="bold", color=TEAL)
    lfp = 0.5 * np.sin(2 * np.pi * 0.45 * t) + 0.27 * np.sin(2 * np.pi * 0.23 * t + 1) + 0.05 * rng.standard_normal(t.size)
    ax.plot(t, 3.45 + lfp, color=TEAL, lw=2)
    ax.text(0.0, 2.75, "the blended slow hum of thousands of cells — easy to hear, but vague\nand easily fooled by background noise.", fontsize=10.5, color=GREY, va="top")
    base = 1.25
    ax.text(0.0, 2.05, "INDIVIDUAL VOICES  (single neurons firing = spikes)", fontsize=13, weight="bold", color=NAVY)
    ax.plot([0, 10], [base, base], color=NAVY, lw=1)
    sp = np.sort(rng.uniform(0.3, 9.7, 13)); sp = sp[np.insert(np.diff(sp) > 0.4, 0, True)]
    for x in sp:
        ax.plot([x, x], [base, base + 0.7], color=NAVY, lw=2.2)
    ax.text(0.0, 0.85, "each is a real, unambiguous event the machine's hum can't fake.  ← our gold standard.", fontsize=10.5, color=GREY, va="top")
    save(fig, "stadium.png")


# ---------------- 6. TWO REGIONS ----------------
def two_regions():
    fig, ax = newfig(11, 4.4)
    H = 10 * 4.4 / 11
    box(ax, 0.6, H / 2 - 0.9, 3.4, 1.8, "Entorhinal cortex", TEAL, fs=15)
    ax.text(2.3, H / 2 - 1.25, "principal cortical input\nto the hippocampus", ha="center", va="top", fontsize=10.5, color=GREY)
    box(ax, 6.0, H / 2 - 0.9, 3.4, 1.8, "Hippocampus", NAVY, fs=15)
    ax.text(7.7, H / 2 - 1.25, "spatial navigation &\nepisodic memory", ha="center", va="top", fontsize=10.5, color=GREY)
    arrow(ax, (4.05, H / 2), (5.95, H / 2), color=GOLD, text="main input", fs=11, dy=0.15)
    ax.text(5, H - 0.4, "Two connected regions, recorded simultaneously", ha="center", fontsize=14, weight="bold", color=NAVY)
    save(fig, "two_regions.png")


# ---------------- 3. EXPERIMENT ----------------
def experiment():
    fig, ax = newfig(11, 5.0)
    H = 10 * 5.0 / 11
    ax.text(5, H - 0.35, "Parametric design: carrier frequency × amplitude", ha="center", fontsize=16, weight="bold", color=NAVY)
    # body + tactor
    box(ax, 0.4, H - 2.6, 3.0, 1.5, "Tactor on the body\n(a buzzing motor)", TEAL, fs=12)
    arrow(ax, (3.5, H - 1.85), (4.5, H - 1.85), color=GOLD, text="at the\nsame time", fs=9, dy=0.18)
    box(ax, 4.6, H - 2.6, 3.0, 1.5, "Electrodes\nin the brain", NAVY, fs=12)
    ax.text(8.4, H - 1.85, "record\nLFP + spikes", ha="center", va="center", fontsize=10.5, color=GREY)
    # timeline
    y0 = 0.7
    ax.text(0.4, y0 + 1.55, "Each trial:", fontsize=11, weight="bold", color=NAVY)
    x = 0.4
    for i in range(4):
        ax.add_patch(Rectangle((x, y0), 0.9, 0.9, fc=RED, ec="none")); ax.text(x + 0.45, y0 + 0.45, "ON", ha="center", va="center", color="white", fontsize=9, weight="bold")
        x += 0.9
        ax.add_patch(Rectangle((x, y0), 0.9, 0.9, fc=LIGHT, ec=GREY)); ax.text(x + 0.45, y0 + 0.45, "off", ha="center", va="center", color=GREY, fontsize=9)
        x += 0.9
    ax.text(x + 0.2, y0 + 0.45, "…  ×200", va="center", fontsize=12, weight="bold", color=NAVY)
    ax.text(0.4, y0 - 0.2, "3 s buzz  /  3 s rest", fontsize=10.5, color=GREY, va="top")
    box(ax, 6.7, y0 - 0.05, 3.0, 1.05, "Speeds tested:\n5 · 10 · 26 · 50 per second", GREEN, fs=11)
    save(fig, "experiment.png")


# ---------------- 11. ENTRAINMENT (swing) ----------------
def entrainment():
    fig, ax = newfig(11, 4.6)
    H = 10 * 4.6 / 11
    ax.text(5, H - 0.35, "Entrainment: phase-locking of neural activity to the stimulus", ha="center", fontsize=15, weight="bold", color=NAVY)
    # swing on the left
    cx, cy = 1.9, H - 0.9
    ax.plot([cx, cx - 0.9], [cy, cy - 1.9], color=GREY, lw=1.5)
    ax.plot([cx, cx + 0.0], [cy, cy - 2.1], color=NAVY, lw=1.5)
    ax.add_patch(Arc((cx, cy), 3.0, 3.0, theta1=235, theta2=305, color=GOLD, lw=1.4, ls=":"))
    ax.add_patch(Circle((cx + 0.0, cy - 2.1), 0.22, fc=NAVY))
    for ang, lab in [(255, ""), (285, "")]:
        pass
    arrow(ax, (cx - 1.4, cy - 1.9), (cx - 0.85, cy - 2.0), color=RED, lw=2)
    ax.text(cx, cy - 2.7, "push in rhythm →\nthe swing goes higher", ha="center", va="top", fontsize=10.5, color=GREY)
    # aligned waves on the right
    t = np.linspace(0, 6, 800)
    bx0 = 4.4
    buzz = 0.45 * np.sin(2 * np.pi * t)
    brain = 0.45 * np.sin(2 * np.pi * t - 0.5)
    ax.plot(bx0 + t * 0.9, (H - 1.2) + buzz, color=GOLD, lw=2.2)
    ax.plot(bx0 + t * 0.9, (H - 2.7) + brain, color=TEAL, lw=2.2)
    ax.text(bx0 - 0.1, H - 1.2, "buzz", ha="right", va="center", fontsize=11, weight="bold", color=GOLD)
    ax.text(bx0 - 0.1, H - 2.7, "brain", ha="right", va="center", fontsize=11, weight="bold", color=TEAL)
    for k in range(1, 6):
        ax.plot([bx0 + (k - 0.25) * 0.9] * 2, [H - 3.0, H - 0.9], color="#cccccc", lw=0.8, zorder=0)
    ax.text(9.9, H - 1.95, "if entrained,\nthey line up", ha="right", va="center", fontsize=10.5, color=NAVY, weight="bold")
    save(fig, "entrainment.png")


# ---------------- 14. THE TRAP (mic + speaker) ----------------
def trap():
    fig, ax = plt.subplots(figsize=(11, 4.9)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 4.9)
    ax.text(5.5, 4.6, "The confound: stimulator-coupled 50 Hz electrical artifact", ha="center", fontsize=15, weight="bold", color=NAVY)
    midy, mx, sx = 2.85, 5.5, 8.3
    # mic in middle
    ax.add_patch(FancyBboxPatch((mx - 0.35, midy - 0.05), 0.7, 1.0, boxstyle="round,pad=0.02,rounding_size=0.3", fc=NAVY, ec=NAVY))
    ax.plot([mx, mx], [midy - 0.55, midy - 0.05], color=NAVY, lw=3)
    ax.text(mx, midy - 0.8, "our recording", ha="center", va="top", fontsize=10.5, color=NAVY, weight="bold")
    # brain (want)
    ax.add_patch(Circle((1.7, midy + 0.35), 0.85, fc=TEAL, ec=TEAL))
    ax.text(1.7, midy + 0.35, "brain", ha="center", va="center", color="white", fontsize=13, weight="bold")
    arrow(ax, (2.65, midy + 0.35), (mx - 0.55, midy + 0.6), color=GREEN, text="what we WANT", fs=10, dy=0.18)
    # speaker (machine hum)
    ax.add_patch(Rectangle((sx, midy - 0.15), 1.1, 1.0, fc=RED, ec=RED))
    ax.add_patch(Polygon([(sx, midy + 0.05), (sx, midy + 0.65), (sx - 0.5, midy + 1.0), (sx - 0.5, midy - 0.3)], closed=True, fc=RED, ec=RED))
    ax.text(sx + 0.55, midy + 0.35, "machine\n50 Hz hum", ha="center", va="center", color="white", fontsize=10, weight="bold")
    arrow(ax, (sx - 0.6, midy + 0.35), (mx + 0.55, midy + 0.6), color=RED, text="leaks in", fs=10, dy=0.18)
    ax.text(5.5, 0.45, "The mic records BOTH → a clean '50 Hz' could be the SPEAKER, not the brain.",
            ha="center", fontsize=12.5, weight="bold", color=NAVY)
    save(fig, "trap.png")


# ---------------- 23. THE FIX (block diagram) ----------------
def fix():
    fig, ax = plt.subplots(figsize=(12, 6.2)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 6.2)
    ax.text(6, 5.9, "Fix: record the stimulus 3 ways on the acquisition clock", ha="center", fontsize=16, weight="bold", color=NAVY)
    srcs = [("Firmware: sync pin\n(1 edge per buzz cycle)", TEAL),
            ("Firmware: trial gate\n(ON / OFF)", TEAL),
            ("Force sensor on skin\n(the REAL vibration)", GOLD),
            ("Drive-signal copy (backup)", GOLD)]
    ys = [4.55, 3.55, 2.55, 1.55]  # box bottoms
    for (lab, col), yb in zip(srcs, ys):
        box(ax, 0.4, yb, 3.2, 0.8, lab, col, fs=10.5)
    hx, hy, hw, hh = 6.3, 2.1, 3.2, 3.0
    box(ax, hx, hy, hw, hh, "", LIGHT, ec=NAVY, lw=2)
    ax.text(hx + hw / 2, hy + hh - 0.45, "Intan recorder", ha="center", fontsize=13, weight="bold", color=NAVY)
    ax.text(hx + hw / 2, hy + hh - 1.0, "SHARED 20 kHz clock", ha="center", fontsize=11.5, weight="bold", color=TEAL)
    box(ax, hx + 0.45, hy + 0.45, hw - 0.9, 1.0, "Brain electrodes\n(LFP + spikes)", NAVY, fs=10.5)
    for yb in ys:
        arrow(ax, (3.65, yb + 0.4), (hx - 0.05, hy + hh / 2), color=GREY, lw=1.6)
    arrow(ax, (hx + hw + 0.05, hy + hh / 2), (hx + hw + 1.0, hy + hh / 2), color=NAVY)
    ax.text(hx + hw + 1.15, hy + hh / 2, "stimulus phase &\nbrain, perfectly\ntime-aligned\n→ entrainment\ntestable", va="center", fontsize=10.5, color=NAVY, weight="bold")
    ax.text(6, 0.5, "+ a 2-minute verification recording BEFORE the real session", ha="center", fontsize=12, weight="bold", color=RED)
    save(fig, "fix.png")


# ---------------- Part 1 vision figures ----------------
def vision_chain():
    fig, ax = plt.subplots(figsize=(12, 3.4)); ax.axis("off"); ax.set_xlim(0, 12); ax.set_ylim(0, 3.4)
    ax.text(6, 3.15, "The proposal — a mechanism hypothesis to test", ha="center", fontsize=14, weight="bold", color=NAVY)
    boxes = [("Wearable\nvibrotactile\nstimulation", RED, RED),
             ("Brain rhythms\n(entrainment)", NAVY, NAVY),
             ("Glymphatic\nclearance ↑", STONE_DARK, NAVY),
             ("Amyloid-β /\ntau cleared", RED, RED)]
    w, gap, y, h = 2.4, 0.7, 1.05, 1.5
    xs = [0.15 + k * (w + gap) for k in range(4)]
    for (lab, edge_col, text_col), x in zip(boxes, xs):
        box(ax, x, y, w, h, lab, FOG_LIGHT, tc=text_col, ec=edge_col, lw=2.2, fs=12)
    for k in range(3):
        arrow(ax, (xs[k] + w, y + h / 2), (xs[k + 1], y + h / 2), color=GREY, lw=2.6)
    ax.text(6, 0.45, "a mechanism hypothesis — to be tested, not yet a treatment claim",
            ha="center", fontsize=10.5, style="italic", color=GREY)
    save(fig, "vision_chain.png")


def whitespace():
    fig, ax = plt.subplots(figsize=(11, 4.2)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 4.2)
    ax.text(5.5, 3.95, "Vibrotactile is the open frontier — next to light & sound", ha="center", fontsize=14, weight="bold", color=NAVY)
    box(ax, 0.5, 1.0, 4.4, 2.3, "", LIGHT, ec=GREY, lw=1.5)
    ax.text(2.7, 2.95, "Audiovisual 40 Hz (GENUS)", ha="center", fontsize=13, weight="bold", color=GREY)
    ax.text(2.7, 1.85, "developed, evidence base —\nbut lab-bound, hard to wear\ndaily, not sleep-friendly", ha="center", va="center", fontsize=10.5, color=GREY)
    box(ax, 6.1, 1.0, 4.4, 2.3, "", LIGHT, ec=RED, lw=2.6)
    ax.text(8.3, 2.95, "Vibrotactile (this program)", ha="center", fontsize=13, weight="bold", color=RED)
    ax.text(8.3, 1.85, "wearable · sleep-compatible\n· pairs with sensing", ha="center", va="center", fontsize=10.5, color=NAVY)
    ax.text(8.3, 0.55, "← the white space", ha="center", fontsize=11.5, weight="bold", color=RED)
    save(fig, "whitespace.png")


def landscape():
    fig, ax = plt.subplots(figsize=(11.5, 4.25)); ax.axis("off"); ax.set_xlim(0, 11.75); ax.set_ylim(0, 4.25)
    ax.text(5.75, 4.02, "Approaches to Alzheimer's and the open frontier",
            ha="center", fontsize=14, weight="bold", color=NAVY)
    items = [
        ("Pharmacology",
         [("method: anti-amyloid antibodies", True),
          ("lecanemab: van Dyck NEJM 2023", False),
          ("donanemab: Sims JAMA 2023", False),
          ("impact: ~27-36% slower decline", True),
          ("but BBB + ARIA/MRI burden", False)],
         GREY),
        ("Lifestyle / multidomain",
         [("method: exercise/diet/cognitive/social", True),
          ("FINGER: Ngandu Lancet 2015", False),
          ("U.S. POINTER: Baker JAMA 2025", False),
          ("Stanford CT: Gozdas/Hosseini", False),
          ("Transl Psychiatry 2024", False),
          ("impact: +0.029 SD/yr; CT d~0.7", True),
          ("scope differs; MIND NEJM 2023 null", False)],
         GREEN),
        ("Non-invasive\nneuromodulation",
         [("method: rTMS / gamma tACS / 40 Hz", True),
          ("rTMS: Koch Alz Res Ther 2025", False),
          ("tACS: Cantoni JAMA Netw Open 2025", False),
          ("GENUS: Chan PLOS ONE 2022", False),
          ("impact: early / small trials", True)],
         RED),
    ]
    w, gap, y, h = 3.4, 0.5, 0.62, 2.85
    xs = [0.4 + k * (w + gap) for k in range(3)]
    for (title, lines, col), x in zip(items, xs):
        box(ax, x, y, w, h, "", LIGHT, ec=col, lw=2.6 if col == RED else 1.5)
        title_y = y + h - (0.52 if "\n" in title else 0.42)
        ax.text(x + w / 2, title_y, title, ha="center", va="center",
                fontsize=12.3, weight="bold", color=col, linespacing=1.12)
        body_top = y + h * 0.56
        line_step = 0.175 if len(lines) > 5 else 0.19
        for j, (line, is_bold) in enumerate(lines):
            ax.text(x + w / 2, body_top - j * line_step, line, ha="center", va="center",
                    fontsize=7.9, weight=("bold" if is_bold else "normal"),
                    color=(NAVY if col != GREY else GREY))
    ax.annotate("", xy=(xs[2] + w / 2, y + 0.03), xytext=(xs[2] + w / 2, 0.23),
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.2, shrinkA=2, shrinkB=4))
    save(fig, "landscape.png")


# ---------------- glymphatic bridge figures (slide 3->4 story) ----------------
def glymphatic():
    fig, ax = plt.subplots(figsize=(11.5, 4.9)); ax.axis("off"); ax.set_xlim(0, 11.5); ax.set_ylim(0, 4.9)
    ax.text(5.75, 4.65, "The glymphatic system: the brain's waste-clearance pathway", ha="center", fontsize=14, weight="bold", color=NAVY)
    ax.add_patch(Ellipse((5.6, 2.75), 4.4, 2.1, fc=LIGHT, ec=NAVY, lw=1.5))
    ax.text(5.6, 3.5, "brain", ha="center", fontsize=11, color=GREY)
    rng = np.random.default_rng(3)
    for _ in range(15):
        ax.add_patch(Circle((5.6 + rng.uniform(-1.7, 1.7), 2.65 + rng.uniform(-0.6, 0.45)), 0.07, fc=RED, ec="none"))
    ax.text(8.05, 2.0, "amyloid-β / tau", fontsize=9.5, color=RED)
    for x in (4.6, 5.6, 6.6):                       # CSF in (top)
        arrow(ax, (x, 4.3), (x, 3.7), color=TEAL, lw=2.4)
    ax.text(8.45, 4.05, "CSF in\n(along vessels)", fontsize=10, color=TEAL, va="center")
    arrow(ax, (5.6, 1.6), (5.6, 1.0), color=GREEN, lw=2.8)   # waste out -> lymph
    box(ax, 4.2, 0.35, 2.8, 0.6, "cervical lymph nodes", GREEN, fs=10)
    ax.text(7.45, 1.25, "waste out →", fontsize=10, color=GREEN)
    ax.text(0.25, 2.75, "boosted by\nsleep &\nvascular\npulsation\n(AQP4)", fontsize=9.5, color=GREY, va="center")
    ax.text(5.75, 0.05, "impaired clearance → Aβ/tau accumulate — an active but still-unsettled AD hypothesis", ha="center", fontsize=9.5, style="italic", color=GREY)
    save(fig, "glymphatic.png")


def csf_wave_evidence():
    fig, ax = plt.subplots(figsize=(11.5, 4.55)); ax.axis("off"); ax.set_xlim(0, 11.5); ax.set_ylim(0, 4.55)
    ax.text(5.75, 4.28, "Neural waves can organize CSF perfusion and clearance", ha="center",
            fontsize=14, weight="bold", color=NAVY)
    ax.text(5.75, 4.02, "Causal anchor plus converging sleep, vascular, and neuromodulator evidence",
            ha="center", fontsize=9.6, color=GREY)

    # Causal Jiang-Xie panel.
    ax.add_patch(FancyBboxPatch((0.35, 0.78), 5.15, 2.95,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=FOG_LIGHT, ec=RED, lw=2.4))
    ax.text(2.93, 3.48, "causal anchor: Jiang-Xie et al., Nature 2024",
            ha="center", va="center", fontsize=10.6, weight="bold", color=RED)
    t = np.linspace(0, 2 * np.pi, 220)
    x = 0.85 + 1.05 * t / (2 * np.pi)
    y = 2.55 + 0.18 * np.sin(3 * t)
    for k in range(3):
        ax.plot(x + k * 0.18, y - k * 0.32, color=NAVY, lw=1.8, alpha=0.9)
    ax.text(1.35, 1.82, "synchronized\nneurons", ha="center", fontsize=9.2, color=NAVY)
    arrow(ax, (2.1, 2.35), (2.82, 2.35), color=GREY, lw=2.1)
    ax.plot([2.95, 3.25, 3.55, 3.85], [2.35, 2.70, 2.00, 2.35], color=POPPY, lw=2.4)
    ax.text(3.4, 1.82, "ionic waves\nin tissue", ha="center", fontsize=9.2, color=NAVY)
    arrow(ax, (3.98, 2.35), (4.75, 2.35), color=LAGUNITA, lw=2.4)
    ax.text(4.73, 2.72, "CSF → ISF\nperfusion", ha="center", fontsize=9.2, weight="bold", color=LAGUNITA)
    for yy in [1.22, 1.02, 0.82]:
        ax.plot([0.7, 5.05], [yy, yy], color=LAGUNITA, lw=1.2, alpha=0.42)
        ax.add_patch(FancyArrowPatch((4.65, yy), (5.05, yy), arrowstyle="-|>", mutation_scale=9,
                                     color=LAGUNITA, lw=1.2, alpha=0.65))
    ax.text(2.9, 1.28, "method: flatten waves (chemogenetic) ↓ clearance\nsynthesize waves (transcranial optogenetic) ↑ perfusion",
            ha="center", va="bottom", fontsize=8.5, color=GREY)

    # Converging evidence panel.
    ax.add_patch(FancyBboxPatch((5.8, 0.78), 5.35, 2.95,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=FOG_LIGHT, ec=PALO_ALTO, lw=1.7))
    ax.text(8.48, 3.48, "not alone: converging support",
            ha="center", va="center", fontsize=10.6, weight="bold", color=PALO_ALTO)
    rows = [
        ("human sleep", "Fultz 2019, Science", "slow waves + BOLD + CSF oscillate together"),
        ("sleep/glymphatic state", "Hablitz 2019; Hauglund 2025", "delta / norepinephrine / vasomotion link to influx"),
        ("neurovascular control", "Chuang 2025; Broggini 2024", "cholinergic and vascular waves regulate flow/perfusion"),
        ("external rhythm example", "Murdock 2024, Nature", "40 Hz light+sound drives glymphatic Aβ clearance in mice"),
    ]
    y0 = 3.12
    for i, (label, cite, point) in enumerate(rows):
        y = y0 - i * 0.62
        ax.add_patch(Circle((6.18, y - 0.02), 0.08, fc=LAGUNITA if i < 3 else RED, ec="none"))
        ax.text(6.38, y + 0.15, label, fontsize=8.5, weight="bold", color=NAVY, ha="left", va="center")
        ax.text(6.38, y - 0.02, cite, fontsize=8.0, color=LAGUNITA if i < 3 else RED, ha="left", va="center")
        ax.text(6.38, y - 0.20, point, fontsize=7.5, color=GREY, ha="left", va="center")

    ax.text(5.75, 0.28,
            "take-home: brain rhythms and state can gate clearance biology — motivating a vibrotactile rhythm test",
            ha="center", fontsize=9.8, weight="bold", color=RED)
    save(fig, "csf_wave_evidence.png")


def driving_clearance():
    fig, ax = plt.subplots(figsize=(11.5, 3.9)); ax.axis("off"); ax.set_xlim(0, 11.5); ax.set_ylim(0, 3.9)
    ax.text(5.75, 3.65, "Preclinical proof: clearance can be driven non-invasively", ha="center", fontsize=14, weight="bold", color=NAVY)
    ax.text(5.75, 3.35, "External stimulation examples in animals — still not human clinical proof", ha="center", fontsize=9.3, color=GREY)
    box(ax, 0.4, 2.05, 3.0, 0.95, "40 Hz light + sound\n(GENUS)", FOG_LIGHT, tc=NAVY, ec=NAVY, lw=2.1, fs=11)
    arrow(ax, (3.45, 2.525), (4.3, 2.525), color=GREY, lw=2.4)
    box(ax, 4.35, 2.05, 6.75, 0.95, "mice: ~4× CSF influx · ~30% less amyloid · AQP4-dependent\n(Murdock 2024, Nature)", FOG_LIGHT, tc=STONE_DARK, ec=STONE_DARK, lw=2.1, fs=10.5)
    box(ax, 0.4, 0.75, 3.0, 0.95, "Focused ultrasound\n(Stanford)", FOG_LIGHT, tc=STONE_DARK, ec=STONE, lw=2.1, fs=11)
    arrow(ax, (3.45, 1.225), (4.3, 1.225), color=GREY, lw=2.4)
    box(ax, 4.35, 0.75, 6.75, 0.95, "rodents: ↑ CSF influx · faster debris clearance\n(Aryal 2022 · Azadian 2025, Nat Biotech)", FOG_LIGHT, tc=STONE_DARK, ec=STONE, lw=2.1, fs=10.5)
    ax.text(5.75, 0.25, "open question: can VIBROTACTILE stimulation enhance glymphatic clearance?", ha="center", fontsize=10.7, weight="bold", color=RED)
    save(fig, "driving_clearance.png")


# ---------------- mouse silhouette (species cue for the title slide) ----------------
def mouse(col="white", name="mouse_white.png"):
    fig, ax = plt.subplots(figsize=(2.6, 1.7)); ax.axis("off")
    ax.set_xlim(0, 2.6); ax.set_ylim(0, 1.7); ax.set_aspect("equal")
    tx = np.linspace(0, 1, 60)                       # curled tail behind the body
    ax.plot(1.9 + 0.72 * tx, 0.55 + 0.62 * tx ** 2, color=col, lw=3.4, solid_capstyle="round")
    ax.add_patch(Ellipse((1.35, 0.72), 1.35, 0.92, fc=col, ec="none"))   # body
    ax.add_patch(Circle((0.62, 0.64), 0.40, fc=col, ec="none"))          # head
    ax.add_patch(Circle((0.52, 1.00), 0.26, fc=col, ec="none"))          # ear
    ax.add_patch(Polygon([(0.30, 0.70), (0.06, 0.58), (0.30, 0.48)], closed=True, fc=col, ec="none"))  # snout
    fig.savefig(OUT / name, dpi=200, transparent=True, bbox_inches="tight"); plt.close(fig)
    print("wrote", name)


if __name__ == "__main__":
    stadium(); two_regions(); experiment(); entrainment(); trap(); fix()
    vision_chain(); whitespace(); landscape()
    glymphatic(); csf_wave_evidence(); driving_clearance()
    mouse("white", "mouse_white.png"); mouse("#53565A", "mouse_grey.png")
