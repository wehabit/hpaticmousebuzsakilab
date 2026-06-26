# Shank-Aware Analysis TODO

Now that probe identity and shank grouping are clearer, the core Dec 3/Dec 4
results do **not** need to be reinterpreted from scratch. The main remaining work
is spatial packaging: where on the probe/shanks the effects appear, and which
claims still need histology or exact orientation.

## Already Done

- LFP summaries by channel and shank/group.
- Driven-frequency power by physical shank.
- Bad-channel QC, including Dec 4 per-probe QC.
- Spike sorting, merge/curation, and ON-vs-OFF firing analyses.
- Curated unit metadata with best channel/shank fields.
- dHPC ripple detection and ripple participation.
- LEC slow-oscillation / UP-DOWN sanity screens.

## Highest-Value TODOs

1. **Dec 3 matching all-units PSTH heatmap**
   - Create `raster_psth_all_good_units_dec3.png`.
   - Purpose: visual symmetry with `raster_psth_all_good_units_dec4.png`.
   - Scientific status: presentation/teaching figure only; the Dec 3 curated
     spike null is already analyzed (`29` good units, `0/174` responsive
     unit-conditions).

2. **Unit response by shank section/depth**
   - Table/figure per curated unit: region, shank, best channel, putative cell
     type, ON-vs-OFF effect, and 50 Hz responder flag.
   - Question: are Dec 4 50 Hz-responsive units clustered on one shank/contact
     zone or spread across the probe?

3. **50 Hz artifact by verified shank section / XML group**
   - Especially for LEC: show whether the 50 Hz LFP bump is concentrated on
     dead/disconnected/pickup-heavy shanks versus tissue-good shanks.
   - Purpose: strengthen the presentation-safe story that the LFP 50 Hz peak is
     artifact-suspect, while the curated spike firing-rate result is the cleaner
     neural readout.

4. **Ripple localization by shank section/channel**
   - We already detect real dHPC ripples. Add a channel/shank localization summary
     of ripple-band power or detected ripple amplitude.
   - Purpose: supports dHPC/CA1 functional placement more cleanly.

5. **Clean shank metadata docs/figures**
   - Remove or replace stale "provisional shank/map unresolved" language where the
     metadata are now answered.
   - Keep caveats for fine depth, laminar, medial/lateral, CA1-vs-DG/subiculum,
     and contact-specific claims unless orientation/histology supports them.

## Lower Priority / Only If Needed

- **CSD / laminar profile:** only if exact contact depth and probe orientation are
  trusted.
- **Dentate spike detection:** only if likely DG/hilus contacts can be assigned.
- **Monosynaptic connections:** possible, but likely small-n and not central for
  this presentation.
- **True phase locking / entrainment:** not fixable from shank metadata; requires
  the delivered vibration waveform recorded on the same clock.

## Recommended Next Step

Do **unit response by shank section/depth** and the **Dec 3 all-units PSTH heatmap** first.
Together they answer "where are the responsive neurons?" and make the Dec 3 null
vs Dec 4 50 Hz effect visually easier to present.
