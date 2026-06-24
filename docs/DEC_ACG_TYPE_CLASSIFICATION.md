# Dec 3 + Dec 4 — Full CellExplorer-style ACG-type Classification

This completes the one feature the cell-type analysis had explicitly **not** done: a
real autocorrelogram-**type** classification (not just descriptive ACG metrics).
Script: [spike_acg_type_classify_dec.py](../analysis/spike_acg_type_classify_dec.py);
outputs in `analysis/outputs/cross_dataset_spike_compare/acg_type/`.

## Method (the actual CellExplorer model)
Each curated good unit's autocorrelogram (0–50 ms, 0.5 ms bins) is fit with the
CellExplorer triple-exponential (Petersen, Hernandez & Buzsáki 2021):

    ACG(t) = max( c·(e^(−(t−t0)/τ_decay) − d·e^(−(t−t0)/τ_rise))
                  + h·e^(−(t−t0)²/τ_burst²) + asymptote , 0 )

We extract **τ_rise / τ_decay / τ_burst / refractory** (all 59 fits converged), and
apply the CellExplorer 3-way scheme combining waveform width with the ACG rise time:

| rule | type |
|---|---|
| trough-to-peak ≤ 0.425 ms | **Narrow Interneuron** |
| TtP > 0.425 ms **and** τ_rise ≤ 6 ms | **Wide Interneuron** |
| TtP > 0.425 ms **and** τ_rise > 6 ms | **Pyramidal Cell** |

## Result — and the honest catch
3-way counts: **16 Narrow Interneuron · 27 Wide Interneuron · 15 Pyramidal Cell**
(`acg_type_classification_plane.png`, `acg_type_fits.png`). The pyramidal cells sit
in the expected upper-right (broad waveform **and** slow ACG rise); narrow
interneurons sit left of the 0.425 ms cut.

**But the 27 "Wide Interneurons" are physiologically implausible as interneurons:**
their **median firing rate is 0.94 Hz** (most < 2 Hz), whereas real fast-spiking
interneurons fire ~10 Hz+. By contrast the "Pyramidal Cell" group fires ~4.85 Hz
(median τ_rise 9.4 ms) and the narrow interneurons fire ~9–14 Hz. So a fast ACG rise
(τ_rise < 6 ms) in a **broad-waveform, < 1 Hz** unit almost certainly reflects
**sparse / irregular firing**, not fast-spiking physiology — these are most likely
**low-rate pyramidal cells mis-labelled** by τ_rise. (A spike-count floor flags only
the very sparsest ACG, because bursty low-rate units still have short-lag pairs, so
the count filter alone does not rescue this.)

## What to conclude
- **The full ACG-type classification is now done** (the deliverable), not deferred.
- **It does not cleanly improve on the width + firing-rate 2-way typing here.** The
  τ_rise dimension only splits the broad units into a "wide interneuron" bin that is
  dominated by implausibly low-rate cells, so the 3-way **"wide interneuron" category
  is not trustworthy** in this small, low-rate sample.
- **The robust typing remains the width × rate 2-way**
  ([DEC_CELLTYPE_CLASSIFICATION.md](DEC_CELLTYPE_CLASSIFICATION.md)): narrow/fast =
  interneuron, broad/slow = pyramidal — and it is **independently cross-validated**
  by ripple participation (interneuron-like units fire ~2.5× more in ripples;
  [DEC_RIPPLE_STATES.md](DEC_RIPPLE_STATES.md)). Where the two schemes agree (clear
  narrow fast-spikers; clear high-rate broad pyramidals) the labels are solid.
- A trustworthy ACG-type classification needs **more spikes per unit** (longer/denser
  sampling) and **more units** — i.e. replication — which is on the next-round list.

## Files
- `acg_type_by_unit.csv` — per unit: τ_rise/τ_decay/τ_burst/refractory, ACG counts,
  reliability flag, 3-way ACG type, and the 2-way width/rate type for comparison.
- `acg_type_summary.json`; figures `acg_type_classification_plane.png`,
  `acg_type_fits.png`.
