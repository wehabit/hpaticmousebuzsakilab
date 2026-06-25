# Dec 3 + Dec 4 — Putative Cell-Type Classification (CellExplorer-style)

A waveform + spike-timing classification of the curated good units into
**putative pyramidal-like vs interneuron-like** cells. This needs **no fine anatomy /
laminar map** — the features are template-waveform shape and spike statistics — so
it is not gated by per-contact anatomical assignment. Script:
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

**Full ACG-type classification — now done** ([DEC_ACG_TYPE_CLASSIFICATION.md](DEC_ACG_TYPE_CLASSIFICATION.md)):
the CellExplorer triple-exponential ACG fit (τ_rise) + the 3-way Narrow/Wide
Interneuron / Pyramidal scheme. The honest result: it **does not cleanly improve on
the width × rate 2-way here** — its "wide interneuron" bin is dominated by
implausibly low-rate units (median 0.94 Hz), so τ_rise is ambiguous in this small,
low-rate sample. The **width × rate 2-way remains the robust typing** (cross-validated
by ripple participation). So the ACG result is still best stated as: *the 50 Hz
spike-rate effect does not look like a simple 50 Hz artifact in the spike times* —
and the safest cell-type claim is the **2-way pyr/interneuron split**, with the
3-way available but its wide-interneuron category not trustworthy yet.

## Caveats (state plainly)
- **Putative types only** — waveform + spiking, not molecularly or
  optogenetically validated.
- **Small n**, especially **LEC interneurons (n = 2)** — that group's bootstrap CI
  is wide and not interpretable.
- **Ripple participation is now done as an exploratory follow-up**, not as a full
  CellExplorer `cell_metrics` workflow. [DEC_RIPPLE_STATES.md](DEC_RIPPLE_STATES.md)
  detects dHPC ripples on a data-driven channel and shows interneuron-like units
  fire ~2.5x more during ripples than outside, which cross-validates the putative
  cell-type labels. Because exact CA1 layer/contact assignment remains conservative
  and ON windows have a 50 Hz-harmonic caveat, this supports **real ripple
  detection and type-consistent participation**, not a stimulation-specific SWR or
  memory claim.
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
