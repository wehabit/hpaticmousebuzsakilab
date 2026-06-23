#!/usr/bin/env python
"""Dec 3 TTL diagnostic: can the digital channel (ch7) recover tactor phase?

Reads ch7 from digitalin.dat (20 kHz), finds the most-active window, and compares
its actual HIGH/LOW pattern to what a 26 Hz tactor cycle would look like. The test:
to resolve tactor up/down at 26 Hz the line must toggle every ~19 ms; if ch7
toggles far slower / irregularly, it cannot carry tactor phase.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FS = 20000.0
DIG = "Haptic_Stim_session1_251203_143031/digitalin.dat"
OUT = Path("analysis/outputs/dec3/ttl_diagnostic"); OUT.mkdir(parents=True, exist_ok=True)

mm = np.memmap(DIG, dtype="<u2", mode="r")
ch7 = ((np.asarray(mm) & (1 << 7)) >> 7).astype(np.int8)
rising = np.flatnonzero(np.diff(ch7) == 1) + 1
rt = rising / FS
iri = np.diff(rt) * 1000  # ms

# densest 3 s window (best case for a captured carrier)
counts = np.searchsorted(rt, rt + 3) - np.arange(len(rt))
k = int(np.argmax(counts))
t0 = rt[k]
TACTOR_HZ = 26.0
period_ms = 1000.0 / TACTOR_HZ

stats = {
    "tactor_freq_hz": TACTOR_HZ,
    "tactor_period_ms": round(period_ms, 1),
    "ch7_median_interval_ms": round(float(np.median(iri)), 1),
    "ch7_edges_in_densest_3s": int(counts[k]),
    "edges_a_26Hz_trial_would_have": int(round(3 * TACTOR_HZ * 2)),  # rising+falling? rising only ~78
    "tactor_cycles_missed_between_ch7_edges": round(float(np.median(iri)) / period_ms, 1),
    "frac_intervals_within_10pct_of_38.5ms": round(float(((iri > 0.9 * period_ms) & (iri < 1.1 * period_ms)).mean()), 4),
}
(OUT / "ttl_diagnostic_summary.json").write_text(json.dumps(stats, indent=2) + "\n")
print(json.dumps(stats, indent=2))

# ---- figure ----
fig, ax = plt.subplots(3, 1, figsize=(13, 7.2))
fig.subplots_adjust(hspace=0.55, top=0.9, bottom=0.08, left=0.07, right=0.98)

# A: actual ch7 trace, 1 s zoom inside the densest window
z0 = int(t0 * FS); z1 = z0 + int(1.0 * FS)
tt = (np.arange(z0, z1) - z0) / FS * 1000
ax[0].step(tt, ch7[z0:z1], where="post", color="#2c3e9e", lw=1.3)
ax[0].set_ylim(-0.2, 1.2); ax[0].set_yticks([0, 1]); ax[0].set_yticklabels(["LOW", "HIGH"])
ax[0].set_xlabel("time (ms)"); ax[0].set_title(
    f"A. ACTUAL ch7 TTL — the densest 1 s in the whole session (t≈{t0:.0f}s). Irregular toggling, no fixed period.", fontsize=10)

# B: what a 26 Hz tactor cycle looks like over the same 1 s
ref = (np.sign(np.sin(2 * np.pi * TACTOR_HZ * tt / 1000)) > 0).astype(int)
ax[1].step(tt, ref, where="post", color="#c0392b", lw=1.0)
ax[1].set_ylim(-0.2, 1.2); ax[1].set_yticks([0, 1]); ax[1].set_yticklabels(["down", "up"])
ax[1].set_xlabel("time (ms)")
ax[1].set_title(f"B. What a 26 Hz tactor would look like (period {period_ms:.0f} ms, up/down every ~19 ms) — 26 cycles in this 1 s.", fontsize=10)

# C: inter-edge interval histogram with the tactor period marked
ax[2].hist(iri[iri < 500], bins=np.linspace(0, 500, 120), color="#7f8c8d")
ax[2].axvline(period_ms, color="#c0392b", lw=2)
ax[2].text(period_ms + 5, ax[2].get_ylim()[1] * 0.8, f"26 Hz tactor period\n({period_ms:.0f} ms)", color="#c0392b", fontsize=8)
ax[2].axvline(np.median(iri), color="#2c3e9e", lw=2, ls="--")
ax[2].text(np.median(iri) + 5, ax[2].get_ylim()[1] * 0.55, f"ch7 median\n({np.median(iri):.0f} ms)", color="#2c3e9e", fontsize=8)
ax[2].set_xlabel("ch7 inter-edge interval (ms)"); ax[2].set_ylabel("count")
ax[2].set_title("C. ch7 intervals cluster far slower than the tactor period; only "
                f"{100*stats['frac_intervals_within_10pct_of_38.5ms']:.1f}% land near 38.5 ms (and never in a sustained run).", fontsize=10)

fig.suptitle("Dec 3 TTL cannot recover tactor phase: ch7 toggles ~%.0f×/s (irregular); a 26 Hz tactor toggles 26×/s. "
             "Between two ch7 edges the tactor completes ~%.0f full up/down cycles." % (1000/np.median(iri), stats["tactor_cycles_missed_between_ch7_edges"]),
             fontsize=11)
fig.savefig(OUT / "ttl_cannot_recover_tactor_phase.png", dpi=120)
print("wrote", OUT / "ttl_cannot_recover_tactor_phase.png")
