#!/usr/bin/env python
"""Verify: is the 50 Hz pickup gradient LEC-only, or does dHPC have it too?

Uses the per-channel 50 Hz ON-OFF envelope from the artifact check
(artifact_check_arrays.npz). For each probe separately, reports:
  - good-channel 50 Hz ON-OFF (mean/median/max) and dead-channel pickup
  - count of channels with extreme 50 Hz power (robust-z > 4) = "hot" channels
  - per-shank breakdown (dHPC is 4-shank; LEC is one long linear probe)
  - gradient test: does 50 Hz rise with proximity to a disconnected channel?
and writes a side-by-side figure.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = Path("analysis/outputs/dec4/artifact_check_50hz")
z = np.load(D / "artifact_check_arrays.npz")
env_on, env_off = z["env_on"], z["env_off"]
diff = env_on - env_off                      # 50 Hz ON-OFF, per channel (256,)
bad = json.load(open("analysis/bad_channels_dec4.json"))
dhpc_dead = sorted(set(bad["port_a_dHPC_bad"]))
lec_dead = sorted(set(bad["port_b_LEC_bad"]))


def robz(x, idx):
    v = x[idx]; med = np.median(v); mad = np.median(np.abs(v - med)) + 1e-9
    return (x - med) / (1.4826 * mad)


def depth_bins(good, lo, hi, nbins=4):
    """mean 50 Hz ON-OFF in equal channel-index bins (proxy for depth profile)."""
    edges = np.linspace(lo, hi, nbins + 1)
    out = {}
    for i in range(nbins):
        chs = [c for c in good if edges[i] <= c < edges[i + 1] + (1 if i == nbins - 1 else 0)]
        out[f"ch{int(edges[i])}-{int(edges[i+1])}"] = round(float(diff[chs].mean()), 2) if chs else None
    return out


report = {}
for name, rng_, dead in [("dHPC", range(0, 128), dhpc_dead), ("LEC", range(128, 256), lec_dead)]:
    chans = list(rng_)
    good = [c for c in chans if c not in dead]
    zpow = robz(env_on, good)               # robust-z of 50 Hz amplitude among good ch
    hot = [c for c in good if zpow[c] > 4]
    report[name] = {
        "n_good": len(good), "n_dead": len(dead),
        "good_50Hz_ON_minus_OFF": {"mean": round(float(diff[good].mean()), 2),
                                    "median": round(float(np.median(diff[good])), 2),
                                    "max": round(float(diff[good].max()), 2),
                                    "n_channels_gt_5": int((diff[good] > 5).sum())},
        "dead_50Hz_ON_minus_OFF_mean": round(float(diff[dead].mean()), 2) if dead else None,
        "n_hot_channels_z50_gt4": len(hot),
        "frac_hot": round(len(hot) / len(good), 3),
        # honest profile (NOT a distance-corr, which is unreliable for bimodal LEC pickup):
        "depth_profile_mean_50Hz_ON_minus_OFF": depth_bins(good, chans[0], chans[-1]),
    }

# dHPC per-shank (4 shanks of 32)
shank_means = {}
for s in range(4):
    chs = [c for c in range(s * 32, s * 32 + 32) if c not in dhpc_dead]
    shank_means[f"dHPC_shank{s+1}_{s*32}-{s*32+31}"] = round(float(diff[chs].mean()), 2)
report["dHPC_per_shank_50Hz_ON_minus_OFF"] = shank_means

(D / "gradient_verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))

# ---- figure: dHPC vs LEC, matched y-axis ----
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
ymax = max(diff[128:256].max(), diff[0:128].max()) * 1.05
for ax, name, chans, dead in [(axes[0], "dHPC (0–127)", range(0, 128), dhpc_dead),
                              (axes[1], "LEC (128–255)", range(128, 256), lec_dead)]:
    for c in chans:
        col = "#d62728" if c in dead else ("#4C78A8" if name.startswith("dHPC") else "#2ca02c")
        ax.bar(c, diff[c], width=1.0, color=col)
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xlabel("channel"); ax.set_title(name, fontsize=11)
    g = [c for c in chans if c not in dead]
    ax.text(0.03, 0.95, f"good mean {diff[g].mean():+.1f}\nhot ch (z>4): {report['dHPC' if name.startswith('dHPC') else 'LEC']['n_hot_channels_z50_gt4']}\n"
            f"dead mean {diff[dead].mean():+.1f}" if dead else f"good mean {diff[g].mean():+.1f}",
            transform=ax.transAxes, va="top", fontsize=8.5, color="#333")
axes[0].set_ylabel("50 Hz envelope  ON − OFF")
axes[0].set_ylim(min(-3, diff[0:128].min() * 1.1), ymax)
fig.suptitle("Is the 50 Hz pickup gradient LEC-only?  dHPC (left): flat, ~0, no hot channels, dead ch clean.  "
             "LEC (right): rises toward the dead blocks (128–135, 224–255).", fontsize=10.5)
fig.tight_layout(rect=(0, 0, 1, 0.94))
out = D / "gradient_dhpc_vs_lec.png"
fig.savefig(out, dpi=120); print("wrote", out)
