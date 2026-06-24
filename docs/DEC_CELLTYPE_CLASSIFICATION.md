# Dec 3 + Dec 4 — Putative Cell-Type Classification (CellExplorer-style)

A waveform + spike-timing classification of the curated good units into
**putative pyramidal-like vs interneuron-like** cells. This needs **no anatomy /
channel-map** — the features are template-waveform shape and spike statistics — so
it is not gated by the provisional electrode map. Script:
[spike_celltype_classify_dec.py](../analysis/spike_celltype_classify_dec.py);
outputs in `analysis/outputs/cross_dataset_spike_compare/celltype/`.

## Features (per curated good unit)
- **Waveform (peak channel):** trough-to-peak width (ms), half-width (ms),
  peak/trough asymmetry — from `templates.npy`.
- **Firing rate (Hz):** spikes / recording duration.
- **ACG / ISI (descriptive only):** burst %, refractory-violation %, CV2 of ISI —
  reported per unit, **not** used as a classification axis (see the ACG note below).

## Classification
A 2-component **Gaussian mixture** on [trough-to-peak, log10 firing rate] over the
**pooled** 59 units; the narrow-waveform / high-rate component is labelled
interneuron-like. A literature trough-to-peak cut (0.5 ms) is shown for reference —
**the data-driven GMM boundary lands essentially on it**, and the width histogram is
clearly **bimodal** (`celltype_classification.png`). So the split is robust, not an
arbitrary threshold.

**The classification axis is waveform width + firing rate only.** We did **not**
perform a full CellExplorer-style autocorrelogram-*type* classification (the
triple-exponential ACG fit → τ_rise → bursty / wide / narrow ACG classes). So this
is a width/rate typing, not an ACG-type typing — don't describe it as the latter.

| dataset | n | pyramidal-like | interneuron-like | median TtP pyr / int | median rate pyr / int |
|---|---|---|---|---|---|
| Dec 3 dHPC | 29 | 19 | 10 | 0.70 / 0.30 ms | ~1 / ~9 Hz |
| Dec 4 dHPC | 15 | 9 | 6 | 0.75 / 0.25 ms | 1.5 / 10.2 Hz |
| Dec 4 LEC | 15 | 13 | **2** | 0.90 / 0.38 ms | 1.1 / 14.3 Hz |

Interneuron-like units are narrow-waveform and fast-firing (~9–14 Hz);
pyramidal-like are broad and slow (~1–1.5 Hz) — the canonical separation.

## Payoff: which cell types carry the 50 Hz response?
Cross-referencing type with the 50 Hz single-unit response (amp250_freq50 ON −
true baseline, from [DEC_BASELINE_POSTSTUDY_STATES.md](DEC_BASELINE_POSTSTUDY_STATES.md);
`dec4_celltype_vs_50hz.png`, 95% bootstrap CIs):

- **dHPC — the up-drive is interneuron-led.** Interneuron-like units rise
  **+2.0 Hz [+0.55, +2.8]** at 50 Hz (CI excludes 0); pyramidal-like are
  ~flat **+0.4 Hz [−0.25, +1.0]** (CI includes 0). So the dHPC 50 Hz increase is
  carried mainly by **fast-spiking interneurons**.
- **LEC — the suppression is in principal cells.** Pyramidal-like units are
  **−0.8 Hz [−1.5, −0.1]** (CI excludes 0); the interneuron-like group is **n = 2**
  (one up, one down) → **uninterpretable**, so we cannot say whether LEC inhibition
  is locally driven.

Read together: 50 Hz vibrotactile drive **recruits dHPC interneurons** while
**suppressing LEC principal cells** — an excitation/inhibition-balance pattern, the
kind of mechanism the bare "dHPC up / LEC down" result couldn't resolve.

## Autocorrelogram: what we did and did NOT do
To avoid overstating the ACG work:

**What we have** — refractory-violation %, burst %, CV2 (per unit, descriptive);
example ACGs (`celltype_acg_examples.png`); and the **50 Hz artifact screen** in
[DEC4_50HZ_ARTIFACT_CHECK.md](DEC4_50HZ_ARTIFACT_CHECK.md): the up-going 50 Hz units
show **no ON-specific 20 ms ACG comb**, so a 20 ms-periodic (50 Hz) electrical/
movement artifact is **not** manufacturing those spikes.

**What we did NOT do** — a full CellExplorer-style **autocorrelogram-type
classification** (τ_rise / bursty-vs-wide ACG classes used as a typing axis). So the
ACG result is: *the 50 Hz spike-rate effect does not look like a simple 50 Hz
artifact in the spike times* — **not** "we classified ACG cell types." The safest
claim remains **50 Hz firing-rate modulation**, not ACG-type or ripple modulation.

## Caveats (state plainly)
- **Putative types only** — waveform + spiking, not molecularly or
  optogenetically validated.
- **Small n**, especially **LEC interneurons (n = 2)** — that group's bootstrap CI
  is wide and not interpretable.
- **Ripple participation is NOT done** (a standard CellExplorer feature). We cannot
  yet say whether any unit participates in sharp-wave ripples, is ripple-modulated,
  or changes ripple firing during stimulation — and we make **no** hippocampal-memory
  or SWR claims. Doing it properly is a **separate** analysis, gated by the provisional
  channel-map:
  1. pick likely **CA1 ripple channels**;
  2. detect ripple events (~100–250 Hz envelope threshold);
  3. compare ripple **rate / amplitude / duration** across baseline / ON / OFF / post;
  4. ask **which units fire during ripples**;
  5. compare ripple participation **by cell type** (pyramidal- vs interneuron-like).

  Until then it stays secondary. The safest current claim is **50 Hz firing-rate
  modulation**, not ripple modulation.
- The LEC 50 Hz pyramidal suppression carries the same **session-drift** caveat as
  the parent analysis (LEC drifts −26 %); the **local ON/OFF** contrast remains the
  drift-immune measure.
- Pooling dHPC and LEC for the GMM assumes the width/rate separation transfers
  across regions — reasonable for waveform typing, but reported per-dataset.

## Files
- `celltype_features_by_unit.csv` — every unit's features + type + 50 Hz response.
- `celltype_summary.json` — per-dataset type counts and medians.
- Figures: `celltype_classification.png` (pooled), `dec3_celltype.png`,
  `dec4_celltype.png`, `celltype_acg_examples.png`, `dec4_celltype_vs_50hz.png`.
