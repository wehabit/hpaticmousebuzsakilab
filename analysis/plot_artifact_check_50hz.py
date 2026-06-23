#!/usr/bin/env python
"""Figure for the dedicated 50 Hz LFP artifact check (Dec 4)."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = Path("analysis/outputs/dec4/artifact_check_50hz")
z = np.load(D / "artifact_check_arrays.npz")
r = json.load(open(D / "artifact_check_summary.json"))
diff = z["diff"]; fvec = z["fvec"]
dhpc_good = set(int(c) for c in z["dhpc_good"]); lec_good = set(int(c) for c in z["lec_good"])
lec_dead = set(int(c) for c in z["lec_dead"])
cross = z["cross"]

fig, axes = plt.subplots(1, 4, figsize=(17, 4.6))
fig.subplots_adjust(bottom=0.28, top=0.80, left=0.05, right=0.99, wspace=0.30)

# A: per-channel 50 Hz ON-OFF envelope, colored by group
ax = axes[0]
for c in range(256):
    if c in lec_dead or c == 121:
        col = "#d62728"        # dead
    elif c in dhpc_good:
        col = "#4C78A8"        # dHPC tissue
    else:
        col = "#2ca02c"        # LEC tissue
    ax.bar(c, diff[c], width=1.0, color=col)
ax.axvline(128, color="#888", ls="--", lw=1)
ax.axhline(0, color="#333", lw=0.8)
ax.set_xlabel("channel  (0–127 dHPC | 128–255 LEC)"); ax.set_ylabel("50 Hz envelope  ON − OFF")
ax.set_title("1. Where does the 50 Hz ON-rise live?\n(red = disconnected/QC-bad electrodes)", fontsize=10)
ax.text(0.02, 0.96, "blue dHPC tissue\ngreen LEC tissue\nred dead", transform=ax.transAxes,
        fontsize=7.5, va="top", color="#444")

# B: decisive bar — good vs dead
ax = axes[1]
g = r["per_channel_50Hz_ON_minus_OFF_envelope"]
groups = [("dHPC\ntissue", g["dHPC_good"], "#4C78A8"), ("LEC\ntissue", g["LEC_good"], "#2ca02c"),
          ("LEC\nDEAD", g["LEC_dead"], "#d62728")]
for i, (lab, gg, col) in enumerate(groups):
    m = gg["mean_ON_minus_OFF"]; lo, hi = gg["ci"]
    ax.bar(i, m, 0.62, color=col, yerr=[[m - lo], [hi - m]], capsize=5,
           error_kw={"elinewidth": 1.3, "ecolor": "#222"})
ax.axhline(0, color="#333", lw=0.8)
ax.set_xticks(range(3)); ax.set_xticklabels([x[0] for x in groups], fontsize=9)
ax.set_ylabel("50 Hz envelope  ON − OFF  (mean ± 95% CI)")
ax.set_title("2. DECISIVE: dead electrodes pick up\n%.1f× MORE 50 Hz than tissue" % r["dead_vs_good_pickup_ratio_LEC"],
             fontsize=10, color="#b30000", fontweight="bold")
for s in ax.spines.values():
    s.set_edgecolor("#b30000"); s.set_linewidth(2)

# C: PSD ON vs OFF (dHPC region mean) + LEC ON, harmonic lines
ax = axes[2]
ax.semilogy(fvec, z["poff_dh"], color="#9aa0a6", lw=1.2, label="dHPC OFF")
ax.semilogy(fvec, z["pon_dh"], color="#e76f51", lw=1.4, label="dHPC ON")
ax.semilogy(fvec, z["pon_lec"], color="#2ca02c", lw=1.2, label="LEC ON", alpha=0.8)
for f0 in (50, 100, 150):
    ax.axvline(f0, color="#444", ls=":", lw=0.9)
ax.set_xlim(2, 200); ax.set_xlabel("Hz"); ax.set_ylabel("PSD")
ax.legend(fontsize=7.5, frameon=False)
ax.set_title("3. Harmonics? 100/150 Hz lines weak\n(ON 1.4/2.4 dB) — not a sharp drive comb", fontsize=10)

# D: cross-region phase lag (ON), near-zero
ax = axes[3]
lags = np.degrees(cross[:, 2])
ax.hist(lags, bins=40, color="#7b68ee", alpha=0.85)
ml = r["cross_region_phase_ON"]["mean_lag_deg"]
ax.axvline(ml, color="#b30000", lw=2)
ax.axvline(0, color="#333", ls=":", lw=1)
ax.set_xlabel("dHPC − LEC 50 Hz phase lag (deg)"); ax.set_ylabel("trials")
ax.set_title("4. Cross-region lag ≈ 0  (%.1f°, %.2f ms)\ncoh %.2f → shared / volume-conducted" % (
    ml, r["cross_region_phase_ON"]["mean_lag_ms"], r["cross_region_phase_ON"]["mean_resultant_coherence"]),
    fontsize=10)

fig.suptitle("Dedicated 50 Hz LFP artifact check — disconnected LEC electrodes show a LARGER 50 Hz ON-rise than tissue, "
             "with ~0 cross-region lag  ⇒  the LEC 50 Hz LFP has a real non-neural pickup component.\n"
             "Single-unit firing-rate changes are much harder for this pickup to fake and remain the cleaner neural evidence.",
             fontsize=10.5)
out = D / "artifact_check_50hz.png"
fig.savefig(out, dpi=120)
print("wrote", out)
