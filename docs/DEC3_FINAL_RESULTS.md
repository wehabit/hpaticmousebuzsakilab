# Dec 3 — Final Results (Locked)

Status date: 2026-06-24. This is the claim-graded summary of the Dec 3
haptic-stimulation recording. It states what is **confirmed**, what is
**suggestive**, what is **provisional**, and what is **blocked on external
input**. For the narrative version with figure links see
[DEC3_SUPERVISOR_SUMMARY.md](DEC3_SUPERVISOR_SUMMARY.md); for full detail see
[DEC3_RESULTS_SUMMARY.md](DEC3_RESULTS_SUMMARY.md). Remaining non-analysis items
are tracked in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) and the external-blockers
list at the end of this file.

## Recording

- Single 128-ch recording, ~10,644 s. fs = 20 kHz, int16.
- **Probe identity confirmed** (via the Dec 4 two-probe recording): this is the
  **dHPC probe, Cambridge NeuroTech H12_2, on Intan Port A**.
  See [DEC4_SUPERVISOR_SUMMARY.md](DEC4_SUPERVISOR_SUMMARY.md).
- Bad channels excluded this pass: `5, 6, 7, 32, 33, 34, 43, 66, 67`
  (119 good channels). Treated as a confirmed analysis decision for this pass.
- Design: ≥15 min baseline, then repeated 3 s ON / 3 s OFF trials, 200 repeats
  per condition. Conditions = amplitude {100, 180, 250} × frequency {5, 26} Hz.
  The following 3 s OFF period is the within-trial control.

## Claim grading

### Confirmed (robust under current preprocessing + corrections)
- **There is a real stimulation-related LFP response.** The strongest, most
  reliable signal is a **broadband LFP increase around `amp180_freq26`** —
  total LFP amplitude/power, not necessarily power exactly at 26 Hz.
- **The effect persists into the 3 s OFF/recovery period** for `amp180_freq26`;
  it is not a purely ON-only response. This is reproduced across the broadband,
  transition-window, and OFF-control analyses.

### Suggestive (directional, but CIs cross zero / not corrected-significant)
- Frequency-specific (driven-frequency) power: `amp180_freq5` is the clearest
  driven-frequency increase; `amp100_freq26` is the best 26 Hz-band candidate.
  Trial-level BH-corrected CIs for driven-frequency power cross zero.
- Adaptation across the long block: late `amp180_freq26` trials become more
  OFF-dominant. Onset / sustained-ON / offset / recovery behave differently and
  should be reported separately, not pooled.

### Not supported as a strong claim
- **Clean, sustained 26 Hz frequency-following / entrainment.** 26 Hz-band power
  and onset-aligned phase consistency (PLV) do not show a robust, corrected,
  sustained following response. Present this as "strong LFP response at a 26 Hz
  stimulation condition," **not** "26 Hz entrainment." True stimulus-phase
  entrainment was not directly testable because the delivered vibration phase was
  not recorded.

### Confirmed spike result after curation
- Kilosort4 produced **194 clusters/templates**, **28** auto-labeled `good`,
  **7,311,421** spikes. Automated QC triage flagged **19** high-confidence
  KS-good clusters.
- **194 is an over-count of neurons.** An automated over-split detector
  (0-lag cross-correlogram duplication; see
  [cluster_merge_candidates_dec3.py](../analysis/cluster_merge_candidates_dec3.py))
  found one genuine over-split group — templates **{90, 91, 92, 97, 104}** are
  a single high-rate neuron shattered into 5 (one pair duplicates >100% of its
  spikes). Collapsing it gives **~190 candidate units**. The true neuron count
  sits between the **19** high-confidence floor and ~190; curation pins it down.
- **The 19 are validated by this check:** none of them are over-split
  duplicates of each other, and the over-split group does not touch the 19.
  (Visual "twins" like 112/106 and 156/159 turned out to be mostly-separate
  neurons — only 4–7% spike overlap — a correction the metric caught that the
  eye did not.)
- The high-confidence subset shows **no BH-corrected ON-vs-OFF firing-rate
  effect**.
- The current curated/merged analysis confirms the null: **29 curated good units,
  174 unit-condition tests, 0 responsive at q<0.05**. So Dec 3 has no clean
  single-unit ON/OFF firing-rate effect at 5/26 Hz.

### Not assigned (needs external input — see blockers)
- Subregion anatomy (CA1/DG/medial/lateral). Refer only to channel groups or
  provisional physical shanks until orientation + histology are confirmed.

## What would change a grade
- A confirmed `H12_2` site-order / shank-orientation map would enable shank- and
  depth-resolved claims and any anatomical interpretation.
- A recorded stimulus copy (absent in Dec 3/Dec 4) would let entrainment be
  tested directly rather than inferred from LFP band power.

## External blockers (cannot be closed by more analysis)
See the dedicated list in [DEC3_EXTERNAL_BLOCKERS.md](DEC3_EXTERNAL_BLOCKERS.md).
