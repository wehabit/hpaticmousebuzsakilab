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
from matplotlib.transforms import blended_transform_factory

D = Path("analysis/outputs/dec4/artifact_check_50hz")
dat = json.load(open(D / "explainer_data.json"))
z = np.load(D / "artifact_check_arrays.npz")
amps = [100, 180, 250]
UV = 0.195  # Intan RHD 0.195 uV per ADC bit (standard); sort used uncalibrated units


def by(d):  # dict {"100":x,...} -> [x at 100,180,250] in uV
    return [d[str(a)] * UV for a in amps]


# ============================== FIGURE 1 ==============================
fig, ax = plt.subplots(1, 3, figsize=(16, 5.1))
fig.subplots_adjust(bottom=0.30, top=0.80, left=0.06, right=0.98, wspace=0.28)

# --- 1.1 pickup BY AMPLITUDE (the dead-channel test) ---
a = ax[0]
p = dat["pickup_by_amp"]
a.axhline(0, color="#999", lw=0.8)
a.plot(amps, by(p["LEC_dead"]), "-o", color="#d62728", lw=2.4, label="LEC dead (disconnected)")
a.plot(amps, by(p["dHPC_dead_121"]), "-s", color="#9467bd", lw=2, label="dHPC dead (ch121)")
a.plot(amps, by(p["dHPC_tissue"]), "-^", color="#4C78A8", lw=2, label="dHPC tissue (good)")
a.set_xticks(amps); a.set_xlabel("stimulus amplitude")
a.set_ylabel("50 Hz amplitude  ON − OFF  (µV)")
a.legend(fontsize=8, frameon=False, loc="upper left")
a.set_title("1. WHEN/HOW MUCH: pickup scales with drive — LEC huge, dHPC small\n"
            "dHPC dead ≥ dHPC tissue at amp250 ⇒ that bump is PICKUP too", fontsize=9.5)
a.annotate("dHPC only\nleaks at amp250\n(~5× < LEC)", xy=(250, p["dHPC_dead_121"]["250"] * UV),
           xytext=(150, 2.6), fontsize=8, color="#333", arrowprops=dict(arrowstyle="->", color="#666"))

# --- 1.2 spatial: where the 50 Hz lives ---
a = ax[1]
diff = z["diff"] * UV
lec_dead = set(int(c) for c in z["lec_dead"])
for c in range(256):
    col = "#d62728" if (c in lec_dead or c == 121) else ("#4C78A8" if c < 128 else "#2ca02c")
    a.bar(c, diff[c], width=1.0, color=col)
a.axvline(128, color="#888", ls="--", lw=1); a.axhline(0, color="#333", lw=0.8)
ylo = -3.0
a.set_ylim(bottom=ylo)
# red bars BELOW the x-axis mark the dead/disconnected blocks (both regions span their full range)
trans = blended_transform_factory(a.transData, a.transAxes)
for lo, hi in [(121, 121), (128, 141), (224, 255)]:
    a.plot([lo - 0.5, hi + 0.5], [0.04, 0.04], transform=trans, color="#d62728", lw=6, solid_capstyle="butt", clip_on=False)
a.text(255, 0.10, "red = dead/disconnected blocks (can't record neurons)", transform=trans,
       ha="right", fontsize=7.4, color="#b30000")
a.set_xlabel("channel        dHPC = 0–127 (all blue)        |        LEC = 128–255 (green good + red dead)")
a.set_ylabel("50 Hz amplitude  ON − OFF  (µV, pooled)")
a.set_title("2. WHERE: dHPC flat; the LEC 50 Hz piles up at the\ndead blocks (red) AND the deep 'good' channels (green)", fontsize=9.5)
a.text(20, diff.max() * 0.72, "dHPC\nflat ≈ 0", fontsize=8.5, color="#4C78A8")
a.annotate("deep LEC 'good'\nchannels (green) next\nto the dead block —\nalso pick up", xy=(214, diff[214]),
           xytext=(146, diff.max() * 0.80), fontsize=7.4, color="#1a7a1a",
           arrowprops=dict(arrowstyle="->", color="#2ca02c"))

# --- 1.3 high-pass barrier ---
a = ax[2]
f = z["fvec"]
a.loglog(f[1:], z["pon_dh"][1:], color="#4C78A8", lw=1.4, label="dHPC LFP (ON)")
a.loglog(f[1:], z["pon_lec"][1:], color="#2ca02c", lw=1.4, label="LEC LFP (ON)")
a.axvspan(f[1], 300, color="#f2dede", alpha=0.5)
a.axvspan(300, 625, color="#dce8dc", alpha=0.6)
a.axvline(300, color="#b30000", lw=2)
ytop = z["pon_dh"].max()
tr3 = blended_transform_factory(a.transData, a.transAxes)
for f0 in (50, 100, 150):
    a.axvline(f0, color="#444", ls=":", lw=0.9)
    a.text(f0, -0.115, f"{f0} Hz", transform=tr3, fontsize=7.3, color="#444", ha="center", clip_on=False)
a.text(300, -0.155, "~300 Hz high-pass", transform=tr3, fontsize=7.3, color="#b30000", ha="center", clip_on=False)
a.set_xlim(2, 625); a.set_ylim(top=ytop * 1.4)
a.set_xlabel("frequency (Hz)", labelpad=18); a.set_ylabel("LFP power (a.u.)")
a.legend(fontsize=8, frameon=False, loc="lower left")
a.set_title("3. WHY IT CAN'T MAKE SPIKES: pickup (50/100/150 Hz) is in\nthe LFP band — REMOVED by the ~300 Hz spike high-pass", fontsize=9.5)
a.text(6, ytop * 0.06, "pickup lives\nhere (pink) —\nLFP band,\ndiscarded", fontsize=7.6, color="#a33")
a.text(330, ytop * 0.10, "spikes detected\nin this band →\n(300 Hz–5 kHz, on\nthe 20 kHz raw\nfile, off chart)", fontsize=7.3, color="#1a5a1a")

fig.suptitle("THE CONTAMINATION — three independent 'tells' that the LFP 50 Hz is electrical PICKUP, not neural:\n"
             "(1) it scales with drive & appears on DEAD electrodes,  (2) it sits ON the dead electrodes spatially,  "
             "(3) but it lives below the spike band, so it can't DIRECTLY make spikes.",
             fontsize=10.5)
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
    deltas = np.array([u["delta"] for u in units])
    up = int((deltas > 0).sum()); dn = int((deltas < 0).sum()); zero = int((deltas == 0).sum())
    ys = np.full(len(deltas), row) + (np.random.default_rng(1).random(len(deltas)) - 0.5) * 0.28
    cols = ["#d62728" if d > 0 else ("#999" if d == 0 else "#2c7fb8") for d in deltas]
    a.scatter(deltas, ys, c=cols, s=42, edgecolor="#333", lw=0.4, zorder=3)
    lab = f"{reg}:  {dn} down / {up} up" + (f" / {zero}≈0" if zero else "")
    a.text(-2.85, row + 0.36, lab, fontsize=9.5, fontweight="bold")
    for i, u in enumerate(units):   # highlight unit 87 — the soft spot expanded in panels 2 & 3
        if u["cluster_id"] == 87:
            a.scatter([u["delta"]], [ys[i]], s=230, facecolors="none", edgecolors="#6a51a3", lw=2.2, zorder=4)
            a.annotate("#87 → panels 2-3\n(the soft spot)", (u["delta"], ys[i]), fontsize=8.5, fontweight="bold",
                       xytext=(u["delta"] + 0.35, ys[i] - 0.40), color="#6a51a3", ha="center",
                       arrowprops=dict(arrowstyle="->", color="#6a51a3", lw=1.2))
a.axvline(0, color="#333", lw=1)
a.set_xlim(-3.1, 3.3); a.set_ylim(-0.7, 1.8)
a.set_yticks([0, 1]); a.set_yticklabels(["LEC\n(bottom row)", "dHPC\n(top row)"], fontsize=9, fontweight="bold")
a.set_xlabel("per-unit 50 Hz firing-rate change  ON − OFF (Hz)")
a.set_title("1. The direction test — each dot = one unit (top row dHPC, bottom row LEC)\n"
            "LEFT of 0 (blue): pickup CANNOT explain — can't remove spikes | RIGHT (red): pickup could mimic", fontsize=9.5)

# --- 2.2 dose-response of unit 87: WHY it looks ambiguous (rate & pickup rise together) ---
a = ax[0, 1]
rate = dat["unit87_LEC_rate_by_amp"]
on = [rate[str(am)]["on"] for am in amps]; off = [rate[str(am)]["off"] for am in amps]
pick = by(dat["pickup_by_amp"]["ch181_unit87"])
l1, = a.plot(amps, on, "-o", color="#d62728", lw=2.2, label="firing rate ON")
l2, = a.plot(amps, off, "-o", color="#9aa0a6", lw=2.2, label="firing rate OFF")
a.set_xticks(amps); a.set_xlabel("stimulus amplitude"); a.set_ylabel("firing rate (Hz)", color="#b30000")
a2 = a.twinx()
l3, = a2.plot(amps, pick, "--D", color="#6a51a3", lw=2, label="50 Hz pickup on its channel")
a2.axhline(0, color="#bbb", lw=0.8); a2.set_ylabel("50 Hz pickup ON−OFF (µV)", color="#6a51a3")
a.legend(handles=[l1, l2, l3], fontsize=8, frameon=False, loc="upper left")
a.set_title("2. Unit 87 (LEC, ch181) dose-response — looks AMBIGUOUS\nrate & pickup rise together  →  resolved in panel 3",
            fontsize=10, color="#b3860b")

# --- 2.3 the RESOLUTION: unit 87's autocorrelogram grows no 20 ms comb during ON ---
a = ax[1, 0]
acg = np.load(D / "unit87_acg.npz")
a.plot(acg["lags"], acg["c_on"], color="#d62728", lw=1.8, label="ON (50 Hz buzz)")
a.plot(acg["lags"], acg["c_off"], color="#9aa0a6", lw=1.8, label="OFF")
for L in (-40, -20, 20, 40):
    a.axvline(L, color="#b59", ls=":", lw=0.9)
a.text(20, a.get_ylim()[1] * 0.93, "50 Hz\n= 20 ms", fontsize=7.5, color="#a14", ha="center")
a.set_xlabel("autocorrelogram lag (ms)"); a.set_ylabel("normalised count")
a.legend(fontsize=8, frameon=False, loc="lower center")
a.set_title("3. RESOLVED: unit 87's ACG grows NO 20 ms comb during ON\n"
            "(ISI<2ms stable: %.2f%% ON / %.2f%% OFF)  →  spikes are NOT pickup" % (acg["isi_on"], acg["isi_off"]),
            fontsize=10, color="#1a7a1a")

# --- 2.4 the hierarchy ladder ---
a = ax[1, 1]; a.axis("off")
tiers = [
    ("#1a7a1a", "CLEANEST", "Suppressed units (ON<OFF), both regions + dHPC up-units at amp100/180.\nPickup can only ADD apparent spikes — it cannot cause suppression."),
    ("#7cb342", "STRONG", "LEC population leans down at 50 Hz (10 of 15 units down, mean −0.08 Hz).\nA net loss of spikes can't be additive artifact."),
    ("#3a7fc1", "CLEARED BY ACG + ISI", "amp250 up-going increases: pickup present in both probes, BUT 0/8 units show\nan ON 50 Hz comb OR an ON refractory-violation rise (incl. unit 87)."),
    ("#d62728", "CONTAMINATED / RESIDUAL", "50 Hz LFP power (LEC strongly; dHPC only at amp250) = NOT neural evidence.\nResidual caveat: arousal/state, n=1 & indirect sensory-network effects — NOT pickup."),
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

fig.suptitle("THE EVIDENCE — direction defeats the artifact (pickup can ADD apparent spikes, never REMOVE them), so suppression is clean;\n"
             "and the up-going units — incl. unit 87 — PASS the ACG + ISI spike-artifact screens. Residual caveat: arousal/state, n=1, "
             "indirect sensory-network effects — NOT 50 Hz pickup.",
             fontsize=10.5)
fig.savefig(D / "explainer_2_evidence.png", dpi=120)
print("wrote", D / "explainer_2_evidence.png")
