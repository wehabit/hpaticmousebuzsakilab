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


def genus_evidence_chain():
    fig, ax = plt.subplots(figsize=(11.5, 4.2)); ax.axis("off"); ax.set_xlim(0, 11.5); ax.set_ylim(0, 4.2)
    ax.text(5.75, 3.95, "What each 40 Hz anchor adds", ha="center", fontsize=14, weight="bold", color=NAVY)
    ax.text(5.75, 3.65, "mouse target/pathology -> glymphatic mechanism -> synthesis -> early human extension",
            ha="center", fontsize=8.6, color=GREY)
    cards = [
        ("Tsai / GENUS\n2016-2019",
         "40 Hz light/sound\ndrives gamma activity;\nreduces Aβ/tau pathology;\nengages microglia + circuits",
         "mouse pathology"),
        ("Murdock\nNature 2024",
         "40 Hz audiovisual\nincreases CSF influx\nand ISF efflux;\nAQP4-dependent\namyloid clearance",
         "glymphatic bridge"),
        ("Park & Tsai\nPLOS Biol 2025",
         "Review synthesizes\npreclinical mechanisms\nand early clinical evidence;\nflags open questions",
         "field synthesis"),
        ("Chan et al.\nAlz Dement 2025",
         "Small mild-AD\nopen-label extension:\nfeasible/safe;\nsuggestive longer-term\nsignals, no blinded control",
         "early human"),
    ]
    w, h, gap, y = 2.45, 2.25, 0.28, 1.05
    xs = [0.35 + i * (w + gap) for i in range(4)]
    for i, ((head, body, tag), x) in enumerate(zip(cards, xs), start=1):
        edge = RED if i in (1, 2) else GREY
        box(ax, x, y, w, h, "", FOG_LIGHT, ec=edge, lw=2.0)
        ax.text(x + 0.20, y + h - 0.22, str(i), ha="left", va="center",
                fontsize=8.2, weight="bold", color=RED)
        ax.text(x + w / 2, y + h - 0.46, head, ha="center", va="center",
                fontsize=8.7, weight="bold", color=RED if i == 2 else NAVY, linespacing=1.05)
        ax.text(x + w / 2, y + 1.13, body, ha="center", va="center",
                fontsize=6.55, weight="bold", color=STONE_DARK, linespacing=1.08)
        ax.text(x + w / 2, y + 0.24, tag, ha="center", va="center",
                fontsize=7.0, weight="bold", color=RED)
    for i in range(3):
        arrow(ax, (xs[i] + w + 0.05, y + h / 2), (xs[i + 1] - 0.05, y + h / 2),
              color=GREY, lw=2.1)
    ax.text(5.75, 0.38,
            "takeaway: strong mouse mechanism; human efficacy remains an active controlled-trial question",
            ha="center", va="center", fontsize=9.0, weight="bold", color=RED)
    save(fig, "genus_evidence_chain.png")


def response_entrainment_guardrail():
    fig, ax = plt.subplots(figsize=(11.5, 4.2)); ax.axis("off"); ax.set_xlim(0, 11.5); ax.set_ylim(0, 4.2)
    ax.text(5.75, 3.95, "A 40 Hz response can be real without proving native gamma entrainment",
            ha="center", fontsize=13.4, weight="bold", color=NAVY)
    ax.text(5.75, 3.64, "Buzsáki/Soula guardrail: separate sensory following from capture of an endogenous oscillator",
            ha="center", fontsize=8.4, color=GREY)

    cards = [
        ("1. Steady-state response\n≠ entrainment",
         "A 40 Hz line can be\nsensory following.\nFlicker resonance +\nattention can amplify it.\nRefs: Herrmann 2001;\nTiitinen et al. 1993",
         "not native-gamma capture"),
        ("2. Soula/Buzsáki 2023",
         "40 Hz visual flicker:\ntrain-onset response\nV1 20.1% (92/458)\nEC 1.9%; CA1 0.2%\ncycle-locking\nV1 28.8%; CA1 6.7%; EC 3.3%",
         "visual cortex ≫ hippocampus / EC"),
        ("3. Independent caution",
         "Human MEG: rapid flicker\nproduced a strong visual\nresponse, but endogenous\ngamma and flicker response\ncoexisted rather than locking.",
         "independent caution"),
        ("4. What haptics must prove",
         "Record vibration phase;\nshow spikes + LFP lock;\nshow native rhythm is\npulled to the drive;\nrule out pickup; test\nspecificity + carryover.",
         "our next-study bar"),
    ]
    w, h, gap, y = 2.55, 2.35, 0.22, 0.82
    xs = [0.27 + i * (w + gap) for i in range(4)]
    for i, ((head, body, tag), x) in enumerate(zip(cards, xs), start=1):
        edge = RED if i in (2, 4) else GREY
        box(ax, x, y, w, h, "", FOG_LIGHT, ec=edge, lw=2.0)
        ax.text(x + w / 2, y + h - 0.34, head, ha="center", va="center",
                fontsize=8.8, weight="bold", color=RED if i == 2 else NAVY, linespacing=1.05)
        ax.text(x + w / 2, y + 1.18, body, ha="center", va="center",
                fontsize=6.65, weight="bold", color=STONE_DARK, linespacing=1.08)
        ax.text(x + w / 2, y + 0.24, tag, ha="center", va="center",
                fontsize=6.65, weight="bold", color=RED)
    for i in range(3):
        arrow(ax, (xs[i] + w + 0.02, y + h / 2), (xs[i + 1] - 0.02, y + h / 2),
              color=GREY, lw=1.8)
    ax.text(5.75, 0.28,
            "language discipline: response / target engagement first; entrainment only with native-rhythm phase evidence",
            ha="center", va="center", fontsize=8.9, weight="bold", color=RED)
    save(fig, "response_entrainment_guardrail.png")


def whitespace():
    fig, ax = plt.subplots(figsize=(11, 4.2)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 4.2)
    ax.text(5.5, 3.95, "GENUS clinical context and our wearable haptic path", ha="center", fontsize=14, weight="bold", color=NAVY)
    box(ax, 0.35, 0.30, 4.95, 3.00, "", LIGHT, ec=GREY, lw=1.5)
    ax.text(2.825, 3.00, "Audiovisual 40 Hz (GENUS)", ha="center", fontsize=12.7, weight="bold", color=GREY)
    ax.text(2.825, 2.62, "Cognito Spectris / GammaSense device", ha="center", va="center", fontsize=8.9, weight="bold", color=GREY)
    ax.text(2.825, 2.40, "Alzheimer's disease trials (mostly mild-to-moderate AD)",
            ha="center", va="center", fontsize=6.9, color=GREY)
    ax.text(0.70, 2.05,
            "OVERTURE (n=76): safe/tolerable;\nprimary endpoint did not separate;\nexploratory ADCS-ADL/MMSE/MRI signals",
            ha="left", va="center", fontsize=6.0, color=GREY, linespacing=1.08)
    ax.text(4.35, 2.05, "feasibility\npublished",
            ha="center", va="center", fontsize=5.7, weight="bold", color=RED, linespacing=1.05)
    ax.text(0.70, 1.38,
            "HOPE (n=670): testing 12-mo ADCS-ADL/MMSE slowing\nOLE (n=402): all-active extension",
            ha="left", va="center", fontsize=6.0, color=GREY, linespacing=1.08)
    ax.text(4.35, 1.38, "pivotal +\nextension",
            ha="center", va="center", fontsize=5.7, weight="bold", color=RED, linespacing=1.05)
    ax.text(0.70, 0.93,
            "ETUDE (n=20): dosing/safety/amyloid PET;\nno posted results",
            ha="left", va="center", fontsize=6.0, color=GREY, linespacing=1.08)
    ax.text(4.35, 0.93, "dose-\nranging",
            ha="center", va="center", fontsize=5.7, weight="bold", color=RED, linespacing=1.05)
    ax.text(0.70, 0.52,
            "Mlinarič 2025: human iEEG target engagement\n(n=11 epilepsy; 490 contacts; independent)",
            ha="left", va="center", fontsize=5.8, color=GREY, linespacing=1.05)
    ax.text(4.35, 0.52, "hippocampus\nengagement",
            ha="center", va="center", fontsize=5.7, weight="bold", color=RED, linespacing=1.05)
    box(ax, 6.1, 0.62, 4.4, 2.68, "", LIGHT, ec=RED, lw=2.6)
    ax.text(8.3, 2.95, "Haptics (us)", ha="center", fontsize=13, weight="bold", color=RED)
    ax.text(8.3, 2.64, "Vibrotactile device applied to fingertips",
            ha="center", va="center", fontsize=8.9, weight="bold", color=NAVY)
    ax.text(8.3, 2.23,
            "Benefits: wearable for long sessions;\nsleep-compatible; pairs with sensing",
            ha="center", va="center", fontsize=7.4, weight="bold", color=RED, linespacing=1.08)
    ax.text(8.3, 1.73, "2-finger glove:\nindex + middle finger",
            ha="center", va="center", fontsize=8.5, color=NAVY, linespacing=1.12)
    ax.text(8.3, 1.12,
            "Potential human testing:\nStanford Hospital iEEG,\nstroke, or AD patients\n(resource/funding-driven)",
            ha="center", va="center", fontsize=6.4, color=NAVY, linespacing=1.10)
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
    fig, ax = plt.subplots(figsize=(11.5, 4.1))
    ax.axis("off")
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 4.1)

    def flow(p0, p1, *, lw=2.4, ms=18, rad=0.0, alpha=1.0, color=STONE_DARK, zorder=8):
        ax.add_patch(FancyArrowPatch(
            p0, p1, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw,
            alpha=alpha, connectionstyle=f"arc3,rad={rad}", zorder=zorder
        ))

    def text(x, y, s, *, fs=9.5, color=NAVY, weight=None, ha="center", va="center", style=None, zorder=20):
        ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, weight=weight, style=style, zorder=zorder)

    # One large faint brain, split into sleep vs awake halves.
    brain_clip = Ellipse((5.75, 2.55), 9.70, 3.05, fc="#FAF9F5", ec="none", zorder=1)
    ax.add_patch(brain_clip)
    left_bg = Rectangle((0.90, 1.03), 4.85, 3.08, fc="#F0EAE0", ec="none", alpha=0.78, zorder=2)
    right_bg = Rectangle((5.75, 1.03), 4.85, 3.08, fc="#FFFFFF", ec="none", alpha=0.96, zorder=2)
    for patch in (left_bg, right_bg):
        patch.set_clip_path(brain_clip)
        ax.add_patch(patch)
    ax.add_patch(Ellipse((5.75, 2.55), 9.70, 3.05, fc="none", ec=STONE_LIGHT, lw=1.9, zorder=4))
    ax.plot([5.75, 5.75], [1.10, 4.00], color=STONE_LIGHT, lw=1.6, ls="--", zorder=5)

    # Mouse-brain overlay: small and central, so the slide says "mouse model" without clutter.
    mouse_clip = Ellipse((5.75, 2.48), 4.40, 1.22, fc="#FFFFFF", ec="none", alpha=0.92, zorder=6)
    ax.add_patch(mouse_clip)
    mouse_sleep = Rectangle((3.55, 1.87), 2.20, 1.25, fc="#F8EFE8", ec="none", alpha=0.95, zorder=6)
    mouse_awake = Rectangle((5.75, 1.87), 2.20, 1.25, fc="#FFFFFF", ec="none", alpha=0.96, zorder=6)
    for patch in (mouse_sleep, mouse_awake):
        patch.set_clip_path(mouse_clip)
        ax.add_patch(patch)
    ax.add_patch(Ellipse((5.75, 2.48), 4.40, 1.22, fc="none", ec=CARDINAL, lw=2.4, alpha=0.9, zorder=9))
    ax.add_patch(Ellipse((3.42, 2.56), 0.68, 0.46, fc="#FFFFFF", ec=CARDINAL, lw=1.8, alpha=0.9, zorder=9))
    ax.add_patch(Ellipse((7.88, 2.39), 0.55, 0.62, fc="#FFFFFF", ec=CARDINAL, lw=1.8, alpha=0.9, zorder=9))
    ax.plot([5.75, 5.75], [1.88, 3.09], color=CARDINAL, lw=1.0, ls="--", alpha=0.45, zorder=10)

    # Left half: big simple "more" story.
    text(3.25, 3.72, "NREM sleep", fs=15.5, weight="bold")
    text(3.25, 3.40, "more CSF flow", fs=10.3, color=GREY)
    flow((1.95, 3.28), (3.12, 2.82), lw=4.8, ms=25, rad=-0.14)
    flow((4.80, 3.22), (3.86, 2.82), lw=4.2, ms=23, rad=0.12)
    flow((3.80, 2.18), (2.95, 1.22), lw=5.0, ms=25, rad=-0.04)
    text(2.15, 1.30, "more\nwaste out", fs=10.0, color=CARDINAL, weight="bold")
    text(3.16, 1.03, "toward cervical\nlymph nodes", fs=7.6, color=GREY)

    # Right half: small simple "less" story.
    text(8.25, 3.72, "Awake", fs=15.5, weight="bold")
    text(8.25, 3.40, "less CSF flow", fs=10.3, color=GREY)
    flow((9.70, 3.25), (8.58, 2.82), lw=2.2, ms=17, rad=0.14, alpha=0.55, color=STONE)
    flow((8.28, 2.15), (8.78, 1.35), lw=2.1, ms=16, alpha=0.55, color=STONE)
    text(9.30, 1.32, "clearance\ncontinues", fs=8.9, color=GREY)

    # A few solute dots: enough to explain, not enough to distract.
    rng = np.random.default_rng(11)
    for _ in range(8):
        ax.add_patch(Circle((rng.uniform(2.70, 4.55), rng.uniform(2.10, 2.85)),
                            0.045, fc=CARDINAL, ec="none", alpha=0.78, zorder=11))
    for _ in range(18):
        ax.add_patch(Circle((rng.uniform(6.85, 9.20), rng.uniform(2.05, 2.95)),
                            0.045, fc=CARDINAL, ec="none", alpha=0.82, zorder=11))
    text(9.18, 2.70, "amyloid-β / tau", fs=9.4, color=CARDINAL, ha="left")

    text(5.75, 0.46,
         "Direct tracer evidence is strongest in mice/rodents; human studies show coupled sleep, blood-flow, and CSF rhythms.",
         fs=7.9, color=GREY)
    text(5.75, 0.22,
         "Refs: Xie 2013; Hablitz 2019; Fultz 2019; Hauglund 2025.",
         fs=7.3, color=GREY)

    svg_out = Path("presentation/svg")
    svg_out.mkdir(parents=True, exist_ok=True)
    for name in ("glymphatic.png", "glymphatic_species_overlay.png"):
        fig.savefig(OUT / name, dpi=180, bbox_inches="tight", facecolor="white")
    for name in ("glymphatic.svg", "glymphatic_species_overlay.svg"):
        fig.savefig(OUT / name, bbox_inches="tight", facecolor="white")
    fig.savefig(svg_out / "glymphatic.svg", bbox_inches="tight", facecolor="white")
    fig.savefig(svg_out / "glymphatic_species_overlay.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", OUT / "glymphatic.png")


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
    ax.text(1.45, 2.92, "synchronized neurons", ha="center", va="bottom", fontsize=9.4, weight="bold", color=NAVY)
    arrow(ax, (2.1, 2.35), (2.82, 2.35), color=GREY, lw=2.1)
    ax.plot([2.95, 3.25, 3.55, 3.85], [2.35, 2.70, 2.00, 2.35], color=POPPY, lw=2.4)
    ax.text(3.4, 1.82, "ionic waves\nin tissue", ha="center", fontsize=9.2, color=NAVY)
    arrow(ax, (3.98, 2.35), (4.75, 2.35), color=POPPY, lw=2.4)
    ax.text(4.73, 2.72, "CSF → ISF\nperfusion", ha="center", fontsize=9.2, weight="bold", color=POPPY)
    ax.text(2.9, 1.28, "method: flatten waves (chemogenetic) ↓ clearance\nsynthesize waves (transcranial optogenetic) ↑ perfusion",
            ha="center", va="bottom", fontsize=8.5, color=GREY)

    # Converging evidence panel.
    ax.add_patch(FancyBboxPatch((5.8, 0.78), 5.35, 2.95,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=FOG_LIGHT, ec=NAVY, lw=1.7))
    ax.text(8.48, 3.48, "not alone: converging support",
            ha="center", va="center", fontsize=10.6, weight="bold", color=NAVY)
    rows = [
        ("human sleep", "Fultz 2019, Science", "slow waves + BOLD + CSF oscillate together"),
        ("sleep/glymphatic state", "Hablitz 2019; Hauglund 2025", "delta / norepinephrine / vasomotion link to influx"),
        ("neurovascular control", "Chuang 2025; Broggini 2024", "cholinergic and vascular waves regulate flow/perfusion"),
        ("external rhythm example", "Murdock 2024, Nature", "40 Hz light+sound drives glymphatic Aβ clearance in mice"),
    ]
    y0 = 3.12
    for i, (label, cite, point) in enumerate(rows):
        y = y0 - i * 0.62
        ax.text(6.1, y + 0.15, label, fontsize=8.5, weight="bold", color=NAVY, ha="left", va="center")
        ax.text(6.1, y - 0.02, cite, fontsize=8.0, color=POPPY if i < 3 else RED, ha="left", va="center")
        ax.text(6.1, y - 0.20, point, fontsize=7.5, color=GREY, ha="left", va="center")

    ax.text(5.75, 0.28,
            "take-home: brain rhythms and state can gate clearance biology — motivating a vibrotactile rhythm test",
            ha="center", fontsize=9.8, weight="bold", color=RED)
    save(fig, "csf_wave_evidence.png")


def glymphatic_measurement_methods():
    fig, ax = plt.subplots(figsize=(11.5, 4.55)); ax.axis("off"); ax.set_xlim(0, 11.5); ax.set_ylim(0, 4.55)
    ax.text(5.75, 4.22,
            "Measurement strength: human CSF motion -> direct mouse tracer flow -> causal 40 Hz clearance test",
            ha="center", fontsize=9.7, weight="bold", color=GREY)

    cards = [
        ("Human CSF motion",
         "Fultz 2019 Science;\nWilliams 2023 PLOS Biol",
         "EFFECT:\nFultz +5.5 dB CSF power;\nWilliams +6-10% evoked CSF signal",
         "MEASURED:\nfast EEG/fMRI; BOLD and\nventricular CSF inflow waves",
         "TAKEAWAY:\nbrain state / sensory-evoked\nhemodynamics can move CSF",
         "LIMIT:\nnoninvasive but indirect;\nCSF motion ≠ solute clearance",
         LAGUNITA),
        ("Neural waves drive flow",
         "Jiang-Xie / Kipnis\nNature 2024",
         "EFFECT:\ntracer flow sleep/wake ~1.5-2x;\nsilencing impairs entry/clearance",
         "MEASURED:\nionic waves + CSF tracers;\nflatten waves ↓ clearance;\nsynthetic waves ↑ perfusion",
         "TAKEAWAY:\nneuronal dynamics can direct\nCSF-to-ISF perfusion",
         "LIMIT:\nmouse/preclinical;\nnot AD-specific or 40 Hz-specific",
         PALO_ALTO),
        ("40 Hz amyloid clearance",
         "Murdock / Tsai\nNature 2024",
         "EFFECT:\nCSF influx ~4x; ISF efflux ~1.5x;\ncortical Aβ ↓~30%",
         "MEASURED:\ncisterna magna tracer influx,\nISF efflux, Aβ in cervical nodes,\nAQP4 blockade",
         "TAKEAWAY:\n40 Hz light+sound increased\nglymphatic flow and Aβ clearance",
         "LIMIT:\nclosest to our story, but still\nmouse; audiovisual not haptic",
         RED),
    ]

    x0s = [0.35, 4.10, 7.85]
    w, h, y = 3.30, 3.22, 0.78
    for i, (head, cite, effect, measured, takeaway, limit, col) in enumerate(cards):
        x = x0s[i]
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.018,rounding_size=0.08",
                                    fc=FOG_LIGHT, ec=col, lw=2.1 if i == 2 else 1.7))
        ax.text(x + w / 2, y + h - 0.26, head, ha="center", va="center",
                fontsize=10.0, weight="bold", color=col)
        ax.text(x + w / 2, y + h - 0.62, cite, ha="center", va="center",
                fontsize=7.5, weight="bold", color=NAVY, linespacing=1.05)
        ax.text(x + 0.24, y + h - 0.87, effect, ha="left", va="top",
                fontsize=5.95, weight="bold", color=col, linespacing=1.05)
        ax.plot([x + 0.22, x + w - 0.22], [y + h - 1.34, y + h - 1.34],
                color=STONE_LIGHT, lw=1.0)
        ax.text(x + 0.24, y + h - 1.48, measured, ha="left", va="top",
                fontsize=6.55, color=STONE_DARK, linespacing=1.05)
        ax.text(x + 0.24, y + h - 2.17, takeaway, ha="left", va="top",
                fontsize=6.55, weight="bold", color=NAVY, linespacing=1.05)
        ax.text(x + 0.24, y + 0.47, limit, ha="left", va="top",
                fontsize=6.05, color=GREY, linespacing=1.05)

    for i in range(2):
        arrow(ax, (x0s[i] + w + 0.06, y + h / 2), (x0s[i + 1] - 0.06, y + h / 2),
              color=STONE, lw=1.7)

    ax.add_patch(FancyBboxPatch((0.80, 0.04), 9.90, 0.42,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc="#FFF7F4", ec=RED, lw=1.2))
    ax.text(5.75, 0.27,
            "Program payoff: evaluate haptics with flow / clearance biomarkers, not entrainment language alone.",
            ha="center", va="center", fontsize=8.5, weight="bold", color=RED)
    save(fig, "glymphatic_measurement_methods.png")


def vibrotactile_anchor_suk():
    fig, ax = plt.subplots(figsize=(11.5, 4.25)); ax.axis("off"); ax.set_xlim(0, 11.5); ax.set_ylim(0, 4.25)
    ax.text(5.75, 4.02, "Suk 2023 is the haptic precedent — and it defines the missing measurement",
            ha="center", fontsize=13.4, weight="bold", color=NAVY)
    ax.text(5.75, 3.74, "whole-body 40 Hz vibration in AD-model mice; activity/pathology readouts, not direct electrophysiology",
            ha="center", fontsize=8.6, color=GREY)

    cards = [
        ("1. Stimulus route",
         "40 Hz whole-body\nvibration using a\nlarge speaker / platform",
         "not a wearable\nfingertip device",
         GREY),
        ("2. Brain readout",
         "immunostaining:\nincreased c-Fos activity\nmarkers in superficial\nSSp + MOp cortex",
         "activity marker,\nnot phase timing",
         PALO_ALTO),
        ("3. What was not tested",
         "no probes; no LFP phase-locking;\nno single-unit entrainment;\nno hippocampus or entorhinal\nrecordings",
         "the gap our study targets",
         RED),
    ]
    x0s = [0.35, 4.10, 7.85]
    w, h, y = 3.30, 2.55, 0.80
    for i, (head, body, tag, col) in enumerate(cards):
        x = x0s[i]
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.018,rounding_size=0.08",
                                    fc=FOG_LIGHT, ec=col, lw=2.2 if i == 2 else 1.7))
        ax.text(x + w / 2, y + h - 0.30, head, ha="center", va="center",
                fontsize=9.7, weight="bold", color=col if i else NAVY)
        ax.text(x + w / 2, y + 1.33, body, ha="center", va="center",
                fontsize=8.1, weight="bold", color=NAVY, linespacing=1.08)
        ax.text(x + w / 2, y + 0.30, tag, ha="center", va="center",
                fontsize=7.4, weight="bold", color=RED if i == 2 else GREY, linespacing=1.05)

    for i in range(2):
        arrow(ax, (x0s[i] + w + 0.06, y + h / 2), (x0s[i + 1] - 0.06, y + h / 2),
              color=STONE, lw=1.8)

    ax.add_patch(FancyBboxPatch((0.86, 0.18), 9.78, 0.42,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc="#FFF7F4", ec=RED, lw=1.2))
    ax.text(5.75, 0.39,
            "Bridge to us: keep the haptic promise, but prove direct medial-temporal target engagement with spikes + LFP.",
            ha="center", va="center", fontsize=8.5, weight="bold", color=RED)
    save(fig, "vibrotactile_anchor_suk.png")


def frequency_menu():
    fig, ax = plt.subplots(figsize=(13.3, 5.0)); ax.axis("off"); ax.set_xlim(0, 13.3); ax.set_ylim(0, 5.0)
    ax.text(6.65, 4.74, "Frequency menu: each condition answers a different question",
            ha="center", fontsize=14.5, weight="bold", color=NAVY)
    ax.text(6.65, 4.44, "Not one magic number: test literature anchor, our strongest response, and controls",
            ha="center", fontsize=9.2, color=GREY)

    rows = [
        ("~0.05-1 Hz\nslow / sleep-state",
         "Fultz 2019;\nJiang-Xie/Kipnis 2024",
         "CSF waves during sleep; synthetic 1 Hz neural waves\npotentiate CSF-to-ISF perfusion",
         "clearance biology may be slow-state, not gamma-only",
         PALO_ALTO),
        ("5 / 10 Hz\nlow flutter controls",
         "Mountcastle/Romo;\nHayashi 2018",
         "classic tactile flutter range; mouse S1 responds\nfrequency-selectively to vibration",
         "asks whether any periodic touch drives the brain",
         GREY),
        ("20 / 26 Hz\nmid controls",
         "Romo/Hayashi;\nour Dec 3/4",
         "mid-flutter / beta comparator; 26 Hz gave large\nLFP transients but not the clean unit peak",
         "protects against cherry-picking 40/50 Hz",
         STONE_DARK),
        ("40 Hz\nAD anchor",
         "Tsai/GENUS;\nMurdock 2024; Suk 2023",
         "AD-model pathology/glymphatic anchor; whole-body\nvibration precedent, but no direct entrainment test",
         "required literature comparator",
         RED),
        ("50 Hz\nour candidate",
         "Romo/Hayashi;\nour Dec 4 spikes",
         "upper flutter; strongest clean single-unit firing-rate\nmodulation in dHPC + LEC",
         "test with phase reference + artifact controls",
         LAGUNITA),
        ("250 Hz pattern\noptional CR",
         "Tass 2017;\nPfeifer/Tass 2021",
         "fingertip vibrotactile coordinated-reset uses high-frequency\nbursts with a slow multi-site pattern",
         "patterning idea; not AD-gamma evidence",
         POPPY),
    ]

    x0, y0 = 0.35, 3.95
    widths = [1.7, 2.15, 4.65, 4.3]
    row_h = 0.56
    headers = ["Frequency", "Reference paper(s)", "Finding / prompt", "Why include it"]
    xs = [x0]
    for w in widths[:-1]:
        xs.append(xs[-1] + w)
    total_w = sum(widths)
    ax.add_patch(Rectangle((x0, y0), total_w, 0.40, fc=FOG_LIGHT, ec=STONE_LIGHT, lw=1.0))
    for label, x, w in zip(headers, xs, widths):
        ax.text(x + 0.10, y0 + 0.20, label, ha="left", va="center",
                fontsize=7.8, weight="bold", color=NAVY)
    y = y0 - row_h
    for idx, (freq, refs, finding, why, col) in enumerate(rows):
        bg = "#FFFFFF" if idx % 2 else "#FAFAFA"
        ax.add_patch(Rectangle((x0, y), total_w, row_h, fc=bg, ec=STONE_LIGHT, lw=0.7))
        ax.add_patch(Rectangle((x0, y), 0.10, row_h, fc=col, ec=col, lw=0))
        ax.text(xs[0] + 0.18, y + row_h / 2, freq, ha="left", va="center",
                fontsize=7.0, weight="bold", color=col, linespacing=1.05)
        ax.text(xs[1] + 0.10, y + row_h / 2, refs, ha="left", va="center",
                fontsize=6.5, weight="bold", color=NAVY, linespacing=1.05)
        ax.text(xs[2] + 0.10, y + row_h / 2, finding, ha="left", va="center",
                fontsize=6.2, color=STONE_DARK, linespacing=1.08)
        ax.text(xs[3] + 0.10, y + row_h / 2, why, ha="left", va="center",
                fontsize=6.2, weight="bold", color=NAVY, linespacing=1.05)
        y -= row_h
    for x in xs[1:]:
        ax.plot([x, x], [y0 + 0.40, y0 - row_h * len(rows)], color=STONE_LIGHT, lw=0.8)

    ax.add_patch(FancyBboxPatch((0.55, 0.10), 12.25, 0.40,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc="#FFF7F4", ec=RED, lw=1.2))
    ax.text(6.65, 0.30,
            "Core panel: 5, 10, 20, 26, 40, 50 Hz; slow/patterned = optional clearance or CR extensions.",
            ha="center", va="center", fontsize=8.2, weight="bold", color=RED)
    save(fig, "frequency_menu.png")


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
    vision_chain(); genus_evidence_chain(); response_entrainment_guardrail(); whitespace(); landscape()
    glymphatic(); csf_wave_evidence(); glymphatic_measurement_methods(); vibrotactile_anchor_suk(); frequency_menu(); driving_clearance()
    mouse("white", "mouse_white.png"); mouse("#53565A", "mouse_grey.png")
