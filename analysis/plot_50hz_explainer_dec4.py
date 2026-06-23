#!/usr/bin/env python
"""Two explainer figures for the Dec 4 50 Hz artifact reasoning.

Fig 1 (contamination): how much 50 Hz pickup, where it lives, why it can't directly
                       become spikes (high-pass barrier).
Fig 2 (evidence):      the direction test (suppression is bulletproof), the unit-87
                       vs unit-126 dose-response ambiguity, and the trust hierarchy.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

D = Path("analysis/outputs/dec4/artifact_check_50hz")
dat = json.load(open(D / "explainer_data.json"))
z = np.load(D / "artifact_check_arrays.npz")
amps = [100, 180, 250]


def by(d):  # dict {"100":x,...} -> [x at 100,180,250]
    return [d[str(a)] for a in amps]


# ============================== FIGURE 1 ==============================
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
fig.subplots_adjust(bottom=0.22, top=0.80, left=0.06, right=0.98, wspace=0.28)

# --- 1.1 pickup BY AMPLITUDE (the dead-channel test) ---
a = ax[0]
p = dat["pickup_by_amp"]
a.axhline(0, color="#999", lw=0.8)
a.plot(amps, by(p["LEC_dead"]), "-o", color="#d62728", lw=2.4, label="LEC dead (disconnected)")
a.plot(amps, by(p["dHPC_dead_121"]), "-s", color="#9467bd", lw=2, label="dHPC dead (ch121)")
a.plot(amps, by(p["dHPC_tissue"]), "-^", color="#4C78A8", lw=2, label="dHPC tissue (good)")
a.set_xticks(amps); a.set_xlabel("stimulus amplitude"); a.set_ylabel("50 Hz envelope  ON − OFF")
a.legend(fontsize=8, frameon=False, loc="upper left")
a.set_title("1. Pickup grows with amplitude — LEC huge, dHPC small\n"
            "dHPC dead ≥ dHPC tissue at amp250 ⇒ that bump is PICKUP too", fontsize=10)
a.annotate("dHPC only\nleaks at amp250\n(~5× < LEC)", xy=(250, 8), xytext=(170, 22),
           fontsize=8, color="#333", arrowprops=dict(arrowstyle="->", color="#666"))

# --- 1.2 spatial: where the 50 Hz lives ---
a = ax[1]
diff = z["diff"]
lec_dead = set(int(c) for c in z["lec_dead"])
for c in range(256):
    col = "#d62728" if (c in lec_dead or c == 121) else ("#4C78A8" if c < 128 else "#2ca02c")
    a.bar(c, diff[c], width=1.0, color=col)
a.axvline(128, color="#888", ls="--", lw=1); a.axhline(0, color="#333", lw=0.8)
a.set_xlabel("channel  (0–127 dHPC | 128–255 LEC)"); a.set_ylabel("50 Hz envelope  ON − OFF (pooled)")
a.set_title("2. Where it lives: dHPC flat; LEC piles up\nat the dead blocks (red) and deep good ch", fontsize=10)
a.text(20, diff.max() * 0.75, "dHPC\nflat ≈ 0", fontsize=8.5, color="#4C78A8")

# --- 1.3 high-pass barrier ---
a = ax[2]
f = z["fvec"]
a.loglog(f[1:], z["pon_dh"][1:], color="#4C78A8", lw=1.4, label="dHPC LFP (ON)")
a.loglog(f[1:], z["pon_lec"][1:], color="#2ca02c", lw=1.4, label="LEC LFP (ON)")
a.axvspan(f[1], 300, color="#f2dede", alpha=0.5)
a.axvline(300, color="#b30000", lw=2)
for f0 in (50, 100, 150):
    a.axvline(f0, color="#444", ls=":", lw=0.9)
a.set_xlim(2, 625); a.set_xlabel("frequency (Hz)"); a.set_ylabel("LFP power")
a.legend(fontsize=8, frameon=False)
a.set_title("3. The high-pass barrier: 50 Hz pickup (pink) is\nREMOVED before spikes are detected (>300 Hz)", fontsize=10)
a.text(8, z["pon_lec"].max() * 0.5, "pickup\n50/100/150 Hz\nlives here", fontsize=8, color="#a33")
a.text(330, z["pon_lec"].max() * 0.5, "spikes\ndetected\n→ (off chart,\n300 Hz–5 kHz)", fontsize=8, color="#b30000")

fig.suptitle("THE CONTAMINATION — the 50 Hz LFP is pickup (LEC strongly, dHPC only at amp250), "
             "but it lives below the spike-detection band, so it cannot DIRECTLY create spikes.",
             fontsize=11)
fig.savefig(D / "explainer_1_contamination.png", dpi=120)
print("wrote", D / "explainer_1_contamination.png")
plt.close(fig)

# ============================== FIGURE 2 ==============================
fig, ax = plt.subplots(2, 2, figsize=(14.5, 9.2))
fig.subplots_adjust(bottom=0.07, top=0.90, left=0.07, right=0.97, wspace=0.24, hspace=0.42)

# --- 2.1 direction test ---
a = ax[0, 0]
a.axvspan(-100, 0, color="#dbe7f3", alpha=0.7)   # down = bulletproof
a.axvspan(0, 100, color="#f7dede", alpha=0.7)     # up = pickup-could-mimic
for row, reg in [(1, "dHPC"), (0, "LEC")]:
    units = dat[reg + "_per_unit_delta"]
    deltas = [u["delta"] for u in units]
    up = sum(d > 0 for d in deltas); dn = sum(d < 0 for d in deltas); zero = sum(d == 0 for d in deltas)
    ys = np.full(len(deltas), row) + (np.random.default_rng(1).random(len(deltas)) - 0.5) * 0.28
    cols = ["#d62728" if d > 0 else ("#999" if d == 0 else "#2c7fb8") for d in deltas]
    a.scatter(deltas, ys, c=cols, s=42, edgecolor="#333", lw=0.4, zorder=3)
    lab = f"{reg}:  {dn} down / {up} up" + (f" / {zero}≈0" if zero else "")
    a.text(-2.7, row + 0.34, lab, fontsize=9, fontweight="bold")
    for u in units:   # label 87 and 126
        if u["cluster_id"] in (87, 126):
            a.annotate(f"#{u['cluster_id']}", (u["delta"], row), fontsize=8, fontweight="bold",
                       xytext=(u["delta"], row + 0.18), ha="center", color="#333")
a.axvline(0, color="#333", lw=1)
a.set_xlim(-3, 3.2); a.set_ylim(-0.6, 1.7); a.set_yticks([])
a.set_xlabel("per-unit 50 Hz firing-rate change  ON − OFF (Hz)")
a.set_title("1. The direction test — suppression is bulletproof\n"
            "LEFT of 0: pickup CANNOT explain (can't remove spikes) | RIGHT: pickup could mimic", fontsize=10)

# --- 2.2 & 2.3 dose-response: unit 87 (ambiguous) vs unit 126 (clean at low amp) ---
for a, reg, cid, ch, verdict, vcol in [
        (ax[0, 1], "unit87_LEC", 87, "ch181", "AMBIGUOUS: rate & pickup rise together", "#b30000"),
        (ax[1, 0], "unit126_dHPC", 126, "ch120", "CLEANER: rate rises at amp100/180 where pickup is ≤0", "#1a7a1a")]:
    rate = dat[reg + "_rate_by_amp"]
    on = [rate[str(am)]["on"] for am in amps]; off = [rate[str(am)]["off"] for am in amps]
    pick = by(dat["pickup_by_amp"][ch + ("_unit87" if cid == 87 else "_unit126")])
    a.plot(amps, on, "-o", color="#d62728", lw=2.2, label="firing rate ON")
    a.plot(amps, off, "-o", color="#9aa0a6", lw=2.2, label="firing rate OFF")
    a.set_xticks(amps); a.set_xlabel("stimulus amplitude"); a.set_ylabel("firing rate (Hz)", color="#b30000")
    a.legend(fontsize=8, frameon=False, loc="upper left")
    a2 = a.twinx()
    a2.plot(amps, pick, "--D", color="#6a51a3", lw=2, label="50 Hz pickup on its channel")
    a2.axhline(0, color="#bbb", lw=0.8)
    a2.set_ylabel("50 Hz pickup ON−OFF", color="#6a51a3")
    a2.legend(fontsize=8, frameon=False, loc="lower right")
    a.set_title(f"{'2' if cid==87 else '3'}. Unit {cid} ({reg.split('_')[1]}, {ch}) dose-response\n{verdict}",
                fontsize=10, color=vcol)

# --- 2.4 the hierarchy ladder ---
a = ax[1, 1]; a.axis("off")
tiers = [
    ("#1a7a1a", "CLEANEST", "Suppressed units (ON<OFF), both regions + dHPC up-units at amp100/180.\nPickup can only ADD apparent spikes — it cannot cause these."),
    ("#7cb342", "STRONG", "LEC population net-suppression (10 down / 5 up, mean −0.08 Hz).\nA net loss of spikes can't be additive artifact."),
    ("#f9a825", "USE CARE", "amp250 up-going increases. Pickup exists in BOTH probes at amp250,\nbut it's below the spike band (high-pass) — likely neural, not certain."),
    ("#d62728", "CONTAMINATED", "50 Hz LFP power (LEC strongly; dHPC at amp250). NOT neural evidence.\nSOFT SPOT: unit 87 — up, dose-graded, in the hottest pickup zone."),
]
a.text(0.5, 1.02, "4. The trust hierarchy", ha="center", fontsize=11, fontweight="bold", transform=a.transAxes)
for i, (col, lab, txt) in enumerate(tiers):
    y = 0.80 - i * 0.225
    a.add_patch(FancyBboxPatch((0.02, y - 0.10), 0.96, 0.165, boxstyle="round,pad=0.01",
                               transform=a.transAxes, facecolor=col, alpha=0.22, edgecolor=col, lw=1.6))
    a.text(0.05, y + 0.012, lab, transform=a.transAxes, fontsize=9.5, fontweight="bold", color=col, va="center")
    a.text(0.05, y - 0.058, txt, transform=a.transAxes, fontsize=7.8, color="#222", va="center")
a.text(0.5, -0.06, "humility: n = 1 animal · ~7–11% of tests responsive (some expected false) · arousal/state not fully excluded",
       ha="center", fontsize=7.6, style="italic", color="#666", transform=a.transAxes)

fig.suptitle("THE EVIDENCE — direction (not magnitude) is what defeats the artifact: pickup can ADD apparent spikes but never REMOVE them.\n"
             "So suppression is clean; amp250 increases need the high-pass argument; unit 87 is the one genuinely soft data point.",
             fontsize=11)
fig.savefig(D / "explainer_2_evidence.png", dpi=120)
print("wrote", D / "explainer_2_evidence.png")
