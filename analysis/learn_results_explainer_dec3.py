#!/usr/bin/env python3
"""Teaching figures: what each Dec-3 analysis WOULD show if the effect were real,
vs what it actually shows. Synthetic/schematic illustrations for comprehension."""
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
OUT = Path("analysis/outputs/dec3/REPORT"); OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(0)

fig, ax = plt.subplots(2, 5, figsize=(19, 7.2))
cols = ["Broadband |LFP|\n(does the signal get bigger?)",
        "Frequency power\n(power at the driven freq?)",
        "Time-frequency\n(sustained band during ON?)",
        "Phase locking / ITPC\n(same phase every trial?)",
        "Spike PETH\n(firing change at onset?)"]
for c, title in enumerate(cols):
    ax[0, c].set_title(title, fontsize=10)

def shade(a):  # ON window 0-3 s
    a.axvspan(0, 3, color="gold", alpha=0.15); a.axvline(0, color="k", lw=0.6)

# ---------- col 0: broadband trace ----------
t = np.linspace(-1, 6, 1400)
for r, real in [(0, True), (1, False)]:
    base = 0.3 * rng.standard_normal(t.size)
    if real:
        env = ((t >= 0) & (t <= 3)) * 1.0
        sig = base + env * 1.4 * np.sin(2 * np.pi * 8 * t)
    else:  # Dec3: onset/offset transients, offset bigger, no sustained lift
        sig = base + 1.6 * np.exp(-((t - 0) ** 2) / 0.02) + 2.4 * np.exp(-((t - 3) ** 2) / 0.03)
    ax[r, 0].plot(t, sig, color="#2c3e50", lw=0.5); shade(ax[r, 0]); ax[r, 0].set_yticks([])

# ---------- col 1: power spectrum ----------
f = np.linspace(1, 40, 400)
for r, real in [(0, True), (1, False)]:
    p = 1.0 / f
    if real:
        p = p + 0.9 * np.exp(-((f - 26) ** 2) / 2)
    ax[r, 1].plot(f, p, color="#c0392b", lw=1.5)
    ax[r, 1].axvline(26, color="gray", ls=":", lw=1); ax[r, 1].set_yticks([])
    ax[r, 1].set_xlabel("Hz" if r == 1 else "")

# ---------- col 2: time-frequency ----------
tt = np.linspace(-1, 5, 120); ff = np.linspace(2, 40, 80)
T, F = np.meshgrid(tt, ff)
for r, real in [(0, True), (1, False)]:
    M = 0.05 * rng.standard_normal(T.shape)
    if real:
        M += 1.0 * np.exp(-((F - 26) ** 2) / 8) * ((T >= 0) & (T <= 3))
    else:
        M += 0.9 * (np.exp(-(T ** 2) / 0.01) + np.exp(-((T - 3) ** 2) / 0.01))  # edge stripes
    ax[r, 2].pcolormesh(tt, ff, M, cmap="coolwarm", vmin=-0.6, vmax=0.9, shading="auto")
    ax[r, 2].axvline(0, color="k", lw=0.6); ax[r, 2].axvline(3, color="k", lw=0.6, ls="--")
    ax[r, 2].set_ylabel("Hz", fontsize=8)

# ---------- col 3: ITPC time course ----------
for r, real in [(0, True), (1, False)]:
    it = 0.07 + 0.03 * rng.standard_normal(t.size)
    if real:
        it = it + 0.75 * ((t >= 0) & (t <= 3))
    it = np.clip(it, 0, 1)
    ax[r, 3].plot(t, it, color="#2a9d8f", lw=1.2); shade(ax[r, 3])
    ax[r, 3].set_ylim(0, 1); ax[r, 3].set_ylabel("ITPC", fontsize=8)

# ---------- col 4: PETH ----------
tp = np.linspace(-1, 4, 500)
for r, real in [(0, True), (1, False)]:
    fr = 5 + 0.6 * rng.standard_normal(tp.size)
    if real:
        fr = fr + 6 * np.exp(-((tp - 0.1) ** 2) / 0.01)
    ax[r, 4].plot(tp, fr, color="#264653", lw=1.2); shade(ax[r, 4])
    ax[r, 4].set_ylim(0, 13); ax[r, 4].set_ylabel("Hz/unit", fontsize=8)

for c in range(5):
    ax[1, c].set_xlabel(ax[1, c].get_xlabel() or "time (s)", fontsize=8)
ax[0, 0].text(-0.35, 0.5, "IF THE EFFECT\nWERE REAL\n(textbook)", transform=ax[0, 0].transAxes,
              fontsize=12, fontweight="bold", color="#27ae60", va="center", ha="right", rotation=0)
ax[1, 0].text(-0.35, 0.5, "DEC 3\n(what we\nactually see)", transform=ax[1, 0].transAxes,
              fontsize=12, fontweight="bold", color="#c0392b", va="center", ha="right", rotation=0)
fig.suptitle("How to read the Dec 3 results: textbook 'effect present' (top) vs what Dec 3 shows (bottom)",
             fontsize=14, fontweight="bold")
fig.tight_layout(rect=(0.05, 0, 1, 0.95))
fig.savefig(OUT / "LEARN_real_vs_dec3.png", dpi=140); plt.close(fig)

# ---------- verdict grid ----------
rows = [("LFP raw + broadband", "broadband response exists (biggest amp180_freq26)", "yes", "#27ae60"),
        ("Frequency power 5/26 Hz", "no reliable power at driven freq (CIs cross 0)", "no", "#c0392b"),
        ("Time-frequency", "edge transients, no sustained 26 Hz band", "no", "#c0392b"),
        ("Phase locking (ITPC/PLV)", "ON not above pre; ~0.07 (also onset-corrected)", "no", "#c0392b"),
        ("OFF-control / transitions", "real but OFFSET/RECOVERY-dominant, metric-sensitive", "partial", "#e67e22"),
        ("Adaptation", "non-stationary (amp250_freq26 declines)", "note", "#e67e22"),
        ("Reference sensitivity", "robust to raw/shank/group median", "robust", "#27ae60"),
        ("Spikes ON-OFF + PETH", "null: 0/28 units, flat PETH", "no", "#c0392b")]
fig, axg = plt.subplots(figsize=(12, 5.2)); axg.axis("off")
axg.set_title("Dec 3 results at a glance", fontsize=14, fontweight="bold")
for i, (name, txt, tag, col) in enumerate(rows):
    y = len(rows) - i
    axg.add_patch(plt.Rectangle((0.02, y - 0.42), 0.96, 0.84, color=col, alpha=0.12, transform=axg.transData))
    axg.text(0.04, y, name, fontsize=11, fontweight="bold", va="center")
    axg.text(0.40, y, txt, fontsize=10, va="center")
    axg.text(0.97, y, tag.upper(), fontsize=11, fontweight="bold", color=col, va="center", ha="right")
axg.set_xlim(0, 1); axg.set_ylim(0, len(rows) + 1)
fig.text(0.5, 0.02, "Bottom line: real broadband/offset LFP modulation (esp. amp180_freq26); NO clean 5/26 Hz entrainment; spike null.",
         ha="center", fontsize=10, style="italic")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "LEARN_results_at_a_glance.png", dpi=140); plt.close(fig)
print("wrote LEARN_real_vs_dec3.png and LEARN_results_at_a_glance.png")
