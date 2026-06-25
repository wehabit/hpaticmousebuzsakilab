# Analysis Foundations For Dec 3

This note summarizes the outside material Nick and Misi suggested, translated
into concrete choices for the Dec 3 haptic stimulation analysis.

## Why These Materials Matter

The Dec 3 experiment has a clean event structure: baseline, then repeated
3-second stimulation ON epochs followed by 3-second OFF-control epochs. The
analysis should therefore be organized around explicitly represented time
intervals and event-aligned measurements, rather than informal slicing.

The main technical pillars are:

- Buzsaki/CellExplorer style data organization for raw data, events, LFP,
  spikes, and metadata.
- Pynapple time objects for Python-native interval and spike-train analysis.
- Kilosort/Phy for spike sorting and curation.
- Time-frequency methods from Mike Cohen and Kramer-style case studies for
  careful LFP interpretation.
- Electroanatomical caution from the hippocampal mapping paper: LFP and spikes
  become anatomically interpretable only when channel geometry, shank identity,
  and physiological landmarks are correct.

## Nick's Paper

Reference:

- Paleologos, Voroslakos, Gonzalez, Maslarova, Aykan, Liu, and Buzsaki.
  "Electroanatomy of hippocampal activity patterns: theta, gamma waves,
  sharp wave-ripples, and dentate spikes." Frontiers in Behavioral
  Neuroscience, 2025.
  https://www.frontiersin.org/journals/behavioral-neuroscience/articles/10.3389/fnbeh.2025.1685846/full

Important lessons for us:

- Multishank high-density recordings need spatial context. Channel-level
  effects are not automatically anatomical effects.
- LFP interpretation should use channel geometry, shank grouping, and spatial
  gradients. The paper uses CSD and coherence maps to identify hippocampal
  layers and boundaries.
- Event-triggered LFP/CSD is a central method: align many snippets to event
  peaks, remove slow drift/trends, then average across events.
- Frequency bands have different spatial scales. Lower-frequency coherence is
  broader; gamma/ripple-band effects are more localized. This matters when we
  interpret whether a haptic response is local, shank-specific, or global.
- The paper classifies similar-looking events by spatial LFP/CSD shape and
  spiking correlates. For Dec 3, this argues against making claims from one
  heatmap alone; LFP, spike response, channel position, and trial timing should
  agree.

How this applies to Dec 3:

- Keep fine anatomical claims conservative until site order/orientation or
  histology supports them.
- Treat shank-level LFP/spike analyses as working physiological groupings, not
  final medial/lateral or laminar claims.
- Use ON/OFF event-aligned responses first; consider CSD-like analyses only
  after geometry is fixed.
- Compare response localization across shanks/channels rather than averaging
  away all spatial information too early.

## Buzcode And CellExplorer

References:

- Buzcode: https://github.com/buzsakilab/buzcode
- Buzcode data formatting standards:
  https://github.com/buzsakilab/buzcode/wiki/Data-Formatting-Standards
- CellExplorer data structure:
  https://cellexplorer.org/datastructure/data-structure-and-format/
- CellExplorer tutorials: https://cellexplorer.org/tutorials/

Important lessons:

- A session should be a self-contained folder with a base name and standardized
  files.
- Raw `.dat` is channel-interleaved int16 binary:
  `c1(t1), c2(t1), ..., cN(t1), c1(t2), ...`.
- LFP is usually a low-pass filtered/downsampled file with the same channel
  ordering, often around 1250 Hz in Buzsaki/CellExplorer workflows.
- Event files represent intervals or timestamps in seconds relative to the
  start of the raw recording.
- Standard event fields include:
  `timestamps`, `detectorinfo`, and optional event-specific values such as
  `amplitudes`, `frequencies`, and `durations`.
- Bad channels, regions, shank groups, and spike groups should be explicit
  metadata, not buried inside notebooks.

How this applies to Dec 3:

- Our `trial_windows.csv` is the Python equivalent of the session event table.
- ON and OFF intervals should be treated as first-class event structures.
- We should create durable files for:
  - stimulus conditions,
  - ON/OFF intervals,
  - bad channels,
  - channel/shank metadata,
  - Kilosort output location,
  - analysis parameters.
- If collaborators want MATLAB/CellExplorer compatibility later, we can export
  `.events.mat`, `.manipulation.mat`, or `.session.mat` equivalents from our
  Python tables.

## Pynapple

References:

- Pynapple docs: https://pynapple.org/
- Pynapple perievent guide:
  https://pynapple.org/user_guide/08_perievent.html
- Pynapple `TsGroup.count`:
  https://pynapple.org/generated/pynapple.TsGroup.count.html

Important lessons:

- Pynapple is designed for exactly our kind of data: spike times, event times,
  time intervals, and trial/state restrictions.
- Use `IntervalSet` for baseline, ON epochs, OFF-control epochs, and
  condition-specific epochs.
- Use `TsGroup` for spike trains after Kilosort/Phy.
- Use interval restriction and spike counting for firing-rate comparisons.
- Use perievent tools for PETH/raster-style views.

How this applies to Dec 3:

- We already exported Pynapple intervals in:
  `analysis/outputs/dec3/pynapple_intervals/`
- Next Python spike-analysis step:
  - load `spike_times.npy` and `spike_clusters.npy`,
  - convert sample indices to seconds,
  - build one `Ts` per unit and a `TsGroup`,
  - compute ON vs OFF firing rates by condition,
  - make PETH/raster summaries around stimulation onset and offset.

## Mike Cohen Time-Frequency Material

Reference:

- Python conversion of Mike Cohen's "Analyzing Neural Time Series Data":
  https://agencyenterprise.github.io/AnalyzingNeuralTimeSeries-Python/chapter02.html

Important lessons:

- Time-domain averages and time-frequency power answer different questions.
- Trial averages can hide non-phase-locked power changes.
- Wavelet convolution is useful for event-aligned time-frequency analysis.
- Frequency-specific claims depend on method choices such as time window,
  wavelet width, baseline correction, and whether we examine phase-locking or
  power.

How this applies to Dec 3:

- Do not call the 26 Hz result "entrainment" unless phase-locking or
  frequency-specific evidence supports it.
- Keep separate endpoints:
  - broadband amplitude,
  - 5 Hz power,
  - 26 Hz power,
  - onset transient,
  - sustained ON,
  - offset/OFF recovery,
  - phase-locking / PLV.
- Because stimulation epochs are only 3 seconds, frequency resolution is
  limited. A 26 Hz result should be interpreted with care.

## Kramer Case Studies

Reference:

- Mark Kramer, "Case Studies in Neural Data Analysis":
  https://mark-kramer.github.io/Case-Studies-Python/01.html

Important lessons:

- Keep analysis arrays explicit and inspect shapes/dimensions often.
- Use Python/Numpy operations deliberately; avoid hidden transformations.
- Build analyses as reproducible, readable scripts rather than manual GUI-only
  steps.

How this applies to Dec 3:

- Every derived result should have a script and an output folder.
- Each summary figure should be traceable back to:
  - raw file,
  - channels used,
  - bad channels excluded,
  - event intervals,
  - reference method,
  - analysis parameters.

## Kilosort And Phy

References:

- Kilosort repository: https://github.com/MouseLand/Kilosort
- Kilosort docs: https://kilosort.readthedocs.io/

Important lessons:

- Kilosort4 should be run directly when possible.
- Probe files matter. `.mat` probe files are recommended because they can
  exclude off channels correctly.
- Phy curation is expected after Kilosort.
- Kilosort "good" labels are useful but not final biological truth.

How this applies to Dec 3:

- We ran Kilosort4 directly on Modal, not through SpikeInterface.
- Output is ready for Phy:
  `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/params.py`
- Treat `194` total units and `28` good refractory-period units as the first
  sorting result, not final curated units.
- The geometry caveat remains important.

## Dec 3 Working Analysis Contract

For the next analysis steps, we should follow this contract:

1. Use seconds relative to the start of `amplifier.dat` for all events.
2. Use the schedule-derived condition table as the condition source of truth.
3. Use TTL only as timing/QC unless we prove it fully encodes condition labels.
4. Treat the 3-second OFF epoch after each stimulation as the matched control.
5. Keep baseline as a separate state, not as the primary control for each trial.
6. Keep bad-channel exclusions explicit and versioned.
7. Keep fine shank/anatomy labels conservative until orientation/histology supports them.
8. Use curated/merged spike outputs for final spike claims.
9. Do not make final entrainment claims without phase/frequency-specific support.
10. Every figure should link back to the script and data files that produced it.

## Immediate Next Steps

1. Inspect Kilosort output in Phy or curated/merged outputs.
2. Use the exported Pynapple interval/spike objects where useful.
3. Generate spike PETHs:
   - onset-aligned,
   - offset-aligned,
   - ON vs OFF firing-rate deltas,
   - condition-by-unit heatmaps.
4. Compare spike condition effects with LFP condition effects.
5. Revisit fine geometry/anatomy only after orientation/histology supports it.
