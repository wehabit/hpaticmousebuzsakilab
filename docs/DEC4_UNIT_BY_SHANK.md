# Dec 4 — Unit response by shank section / depth

**Question:** are the Dec 4 50 Hz-responsive single units confined to one shank
section / contact zone?

**Answer: in dHPC, the responders are not confined to one 32-channel section.** The
50 Hz single-unit effect appears across all populated dHPC sections, although the
sampling is uneven (most dHPC units are in section 4). LEC is different: almost all
curated LEC units are in one populated LEC shank/group, so LEC cannot support an
across-shank spread claim. The safe conclusion is descriptive: **the dHPC 50 Hz unit
effect is not a one-section recording quirk; LEC remains spatially under-sampled.**

Figure: [`unit_by_shank_dec4.png`](../results/dec4/11_Spikes/unit_by_shank_dec4.png) ·
table: `analysis/outputs/cross_dataset_spike_compare/unit_by_shank/unit_by_shank_dec4.csv`

## What was assembled

For every curated good unit (amp250_freq50) we joined:

- **region** (dHPC / LEC) and **shank section / XML group** (from the curated probe geometry),
- **best channel** and its **contact depth** (the Kilosort `channel_positions` y-coordinate,
  relative microns within that section),
- **putative cell type** (pyramidal-like / interneuron-like, from the width × rate classifier),
- **ON−OFF firing change at 50 Hz** and q<0.05 responsiveness.

Each unit is plotted at its (section, depth), colored by ON−OFF Hz, sized by |effect|,
shaped by cell type, and outlined when significant.

Channel numbering note: for dHPC, `best_channel` is the global Intan channel. For LEC,
`best_channel` is the local sliced-probe Kilosort channel, and `best_channel_global`
adds the +128 Port-B offset so it can be compared to LFP/QC channels.

## Result by region

Shank-count clarification: Dec 4 has **six verified XML channel groups**, not six
independent physical shanks. The dHPC H12_2/H12 map is best treated as two physical
shanks split into four 32-channel sections; LEC H15 contributes two 64-channel
physical shanks. This figure uses the six groups/sections as the finest reliable
spatial bins.

**dHPC (4 sections, 15 units, 9 responsive):** responders appear in **every section** —

| section | responders / units |
|---|---|
| 1 | 1 / 2 |
| 2 | 1 / 1 |
| 3 | 2 / 2 |
| 4 | 5 / 10 |

Responders occur in each dHPC section, with responders at a range of depths. The sampling
is not uniform: section 4 held the most units, so it also contributes the most responders.
So this argues against a single-section artifact, but it is not a formal spatial-uniformity
test.

**LEC (2 shanks/groups, 15 units, 3 responsive):** 14 of 15 units are on group 5
(group 6 had only 1 curated unit), so LEC cannot test *across-shank* spread. Within populated group 5,
the 3 responders are interleaved with non-responders rather than forming an obvious
single-depth band, but this is descriptive only.

## Caveats

- Depth is the relative `channel_positions` y within each section/group; we make **no absolute
  layer / medial-lateral claim** here — fine laminar interpretation still needs histology
  or exact probe orientation (kept deliberately modest per the shank-metadata policy).
- LEC across-shank spread is untestable (single populated group), so the "not confined to
  one section" conclusion is a dHPC statement.
- n is small per group/section; this is a spatial-distribution description, not a formal
  spatial-uniformity test.
