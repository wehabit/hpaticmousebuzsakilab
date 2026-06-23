# Haptic Stimulation Electrophysiology — Buzsáki Lab Mouse Study

## Abstract

This repository contains the electrophysiological analysis of an awake mouse
implanted with **Cambridge NeuroTech silicon probes** (Intan acquisition, 20 kHz
wideband / 1.25 kHz LFP) and recorded during controlled **vibrotactile
("haptic") stimulation**, across **two sessions**:

- **Dec 3** — a single **128-channel probe in dorsal hippocampus** (**dHPC**,
  Cambridge NeuroTech `H12_2`, Intan Port A). 15-min baseline → **1,200 trials**
  (each **3 s ON / 3 s OFF**) over a 120-min block → 30-min post. Six interleaved
  conditions: amplitude `{100, 180, 250}` × frequency `{5, 26}` Hz, ~200 each.
- **Dec 4** — the **same mouse and dHPC probe** plus a **second probe in lateral
  entorhinal cortex** (**LEC**, Port B) = **256 channels**, with two added drive
  frequencies. **2,400 trials** (12 conditions: 3 amplitudes × **{5, 10, 26, 50}
  Hz**) over a ~5-hour session. Port A is the identical dHPC probe/channel map as
  Dec 3, so dHPC is **directly comparable across sessions**.

The delivered vibration was logged only as crude QC (a 1-bit accelerometer TTL on
Dec 3; no stimulus channel shared on Dec 4), and the actuator ran as a
free-running oscillator — see the stimulus caveat below. Trial timing comes from
the randomized controller schedule, validated against the recording-start offset.

The central questions are whether neural activity (i) **responds** to the stimulus
and (ii) **entrains** to its drive frequency. Both sessions use the **same
pipeline**: event-aligned LFP, broadband and frequency-specific power,
time-frequency and 1/f spectral-slope decomposition, inter-trial phase locking
(PLV/ITPC) tested against an analytic chance floor, within-trial OFF-window and
reference-scheme controls, an LFP-based movement proxy, and **Kilosort spike
sorting with over-split/merge detection, curation, and peri-event time
histograms** — all with trial-level bootstrap 95% confidence intervals.

**Key findings.** (each links to the figure(s) that show it)
1. A **real, amplitude-graded broadband LFP response**, strongest for the
   `amp180_freq26` condition (Dec 3). The response is **transition-weighted
   (onset/offset) rather than a sustained lift** — though, on the trial-level
   bootstrap CIs, that offset-heavy asymmetry is statistically reliable only at
   `amp250_freq26` (CI excludes 0) and marginal at `amp180_freq26`.
   → [condition × channel heatmap](results/dec3/04_EventAligned_LFP/condition_by_channel_lfp_response_heatmap.png),
   [transition index](results/dec3/07_Broadband_OFFcontrol_TrialStats/transition_index_condition.png)
2. **No frequency-following in dHPC at any tested frequency** (5/10/26/50 Hz): no
   narrowband peak above the 1/f background, phase locking at chance. This
   **replicates across Dec 3 and Dec 4 on the identical probe** and extends to the
   two new frequencies.
   → [Dec 3 spectral-slope decomposition](results/dec3/05_Frequency_Spectral/spectral_slope_decomposition.png),
   [Dec 3 phase-locking null floor](results/dec3/06_Phase_Locking/phase_locking_null_floor.png),
   [Dec 4 spectral slope + ITPC](results/dec4/05_Frequency_Spectral/spectral_slope_itpc_dec4.png)
3. **LEC (Dec 4) shows an amplitude-graded narrowband 50 Hz LFP power increase that
   is *induced*, not phase-locked** (ITPC at chance) — with no comparable effect at
   5/10/26 Hz or in dHPC. **But a dedicated artifact check shows this LFP effect is
   contaminated by non-neural pickup:** disconnected LEC electrodes (which can't
   record neurons) pick up **~6× more** 50 Hz during ON than tissue, and the
   cross-region 50 Hz lag is ~0 ms (a shared signal). So the LEC 50 Hz *LFP* is not
   clean neural evidence — the single-unit rate change (finding 4) is.
   → [driven-power change by region](results/dec4/05_Frequency_Spectral/driven_power_change_by_analysis_group.png),
   [50 Hz artifact check](analysis/outputs/dec4/artifact_check_50hz/artifact_check_50hz.png),
   [writeup](docs/DEC4_50HZ_ARTIFACT_CHECK.md)
4. **Single-unit ON/OFF firing is frequency-specific.** At **5/26 Hz there is no
   effect** (Dec 3: 0/174 unit-conditions responsive, post-curation). But Dec 4
   added 10/50 Hz, and at **50 Hz / high amplitude a subset of single units *are*
   modulated** — in **both** dHPC (19/180 responsive) and LEC (13/180),
   concentrated at 50 Hz (15/19 and 8/13). This matches the LEC 50 Hz LFP effect
   and turns "no single-unit effect" into "none *at 5/26 Hz*." Curated units:
   Dec 3 dHPC 29, Dec 4 dHPC 15, LEC 15.
   → [cross-dataset spike ON/OFF figure](analysis/outputs/cross_dataset_spike_compare/spike_onoff_cross_dataset.png),
   [writeup](docs/DEC4_SPIKE_ONOFF_RESULT.md),
   [Dec 3 onset PETH](results/dec3/11_Spikes/peth_onset_ks_good_units.png)
5. **The 50 Hz response is active and region-specific — but the regions do *not*
   demonstrably coordinate.** It is not a passive echo (dHPC shows a driven-up
   subset, LEC mostly suppresses; an echo would look the same everywhere). But a
   coordination test found **no clear cross-region "working together"**: the
   cross-region spike–field coupling (harder for pickup to fake than the LFP) does
   **not** rise with stimulation, so the parallel rise in LFP coherence is best
   explained by a
   **shared 50 Hz signal** — and a **dedicated artifact check then confirmed a real
   non-neural 50 Hz pickup** (disconnected electrodes pick up ~6× more than tissue,
   ~0 ms cross-region lag), making the single-unit *rate* change the cleanest
   neural evidence.
   → [interpretation figure](analysis/outputs/cross_dataset_spike_compare/spike_50hz_interpretation.png),
   [coordination test figure](analysis/outputs/dec4/coordination_50hz/coordination_50hz.png),
   [writeup](docs/DEC4_COORDINATION_50HZ.md)
6. Conclusions are **robust** to referencing scheme and to excluding
   movement-contaminated trials. Hardware note: the dHPC probe was improved before
   Dec 4 (the nine Dec-3 bad channels are clean on Dec 4); the LEC probe is
   noisier (LEC: 82 good / 45 disconnected-dead incl. the dead block 224–255 / 1
   hot-excluded ch142). Methods follow Buzsáki-lab
   tooling (buzcode / CellExplorer / Kilosort) and Cohen (2014).
   → [reference-scheme sensitivity](results/dec3/09_Reference_Sensitivity/reference_condition_summary.png),
   [movement: excluded vs kept trials](results/dec3/03_Movement_DataCleaning/excluded_vs_kept_examples.png)

**Caveat — our hardware was not equipped to test entrainment.** Neither session
recorded a usable **analog copy of the delivered vibration**, the actuator ran
free-running (phase never reset), and the digital sync channel **never captured the
carrier** (it toggled at ~4 Hz regardless of drive frequency — see the
[TTL diagnostic](analysis/outputs/dec3/ttl_diagnostic/ttl_cannot_recover_tactor_phase.png)).
So the stimulus's instantaneous phase is **unrecoverable**, and "no entrainment" is a
**hardware/measurement limitation, not a neural result** — band power is measurable,
but phase-following cannot be tested without a phase reference.

**Caveat — stimulus fidelity at low frequencies.** We also determined, after the
study, that the delivered vibration was **not a clean sine wave at the lower carriers
(5 / 10 / 26 Hz)** — the actuator did not produce clean sinusoids at low frequencies.
This limits interpretation of those conditions, and means the apparent
frequency-specificity (effect concentrated at 50 Hz) is **partly confounded with
stimulus quality**: 50 Hz was delivered more cleanly than 5/10/26 Hz, so we cannot
fully separate "the brain prefers 50 Hz" from "50 Hz was the best-delivered stimulus."

The next recording fixes both by capturing the **delivered vibration as a continuous
analog waveform** — a thin PVDF force sensor in the tactor→skin path, into an Intan
analog input on the shared 20 kHz clock — plus per-cycle and per-trial digital sync
lines, making a genuine entrainment test (and stimulus-fidelity check) possible (see
[docs/HARDWARE_ENG_MESSAGE_NEXT_ROUND.md](docs/HARDWARE_ENG_MESSAGE_NEXT_ROUND.md)).

**Status.** Both Dec 3 and Dec 4 are fully processed through LFP analysis and
**spike sorting + curation**. **Anatomical targeting is known** (surgeon's
coordinates: dHPC = **H12_2** @ AP 1.8 / ML 1.5 / depth 1–1.8 mm, Port A; LEC =
**H15** @ AP 3.8 / ML 3.8 / 5°, Port B). What remains is the exact **electrode
channel-map** — the Cambridge NeuroTech site map (`.prb`) for H12_2 and H15 plus the
adapter/headstage wiring — which is still **provisional** in the analysis (a linear
placeholder). That gates only **depth / laminar / subregion** claims; the
**region-level** findings (dHPC vs LEC) are unaffected. Plus the analog stimulus
recording above (see [docs/DEC3_EXTERNAL_BLOCKERS.md](docs/DEC3_EXTERNAL_BLOCKERS.md)).

## Start Here

- [**CONCLUSIONS.md**](CONCLUSIONS.md): one-page synthesis across Dec 3 + Dec 4 —
  what is supported, what is explicitly negative, and what the next recording needs.
- [**Results — every figure**](results/README.md): all result figures, curated
  and grouped by analysis type (the canonical place to browse results).
- [Dec 3 Supervisor Summary](docs/DEC3_SUPERVISOR_SUMMARY.md): clean
  findings, figure links, methods, caveats, and suggested presentation order.
- [**Dec 4 Supervisor Summary**](docs/DEC4_SUPERVISOR_SUMMARY.md): two-probe
  (dHPC + LEC) session, four drive frequencies. Headline: dHPC follows no
  frequency (replicating Dec 3 on the same probe); LEC shows an induced,
  amplitude-graded 50 Hz power increase that is **not** phase-locked. Figures in
  [`results/dec4/`](results/dec4/README.md).
- [Dec 3 Results Dashboard](analysis/outputs/dec3/RESULTS_DASHBOARD.html):
  clickable local HTML dashboard of result pages and figures.
- [Dec 3 Major Images](docs/DEC3_MAJOR_IMAGES.md): figure-by-figure guide.
- [Dec 3 Image Walkthrough](docs/DEC3_IMAGE_WALKTHROUGH.md): teaching guide
  explaining how each figure was generated and what to take away from it.
- [Dec 3 Misi Preprocessing Checklist](docs/DEC3_MISI_PREPROCESSING_CHECKLIST.md):
  status of each collaborator preprocessing step, including blocked/no-data
  items.
- [Reusable Pipeline](docs/RERUN_PIPELINE.md): how to repeat this analysis for
  future recordings/conditions.
- [Study Notes](docs/STUDY_NOTES.md): Dec 3/Dec 4 experiment notes, coordinates,
  channel notes, and original collaborator context.
- [Experiment Setup Photos](https://photos.app.goo.gl/NzK9YqrbCPufYTYV8):
  Google Photos album showing the study/experiment setup.
- [Resources And Guidance](docs/RESOURCES_AND_GUIDANCE.md): links from Nick,
  Mishi, Buzcode, CellExplorer, Pynapple, Kilosort, and related references.

## Results — Every Figure

Result figures live in **[`results/`](results/)**, organized **one folder per
recording session** (`results/dec3/`, `results/dec4/`, …). Each session folder
holds the curated, **de-duplicated** figures grouped into 13 numbered categories
(`01_Session_Timeline` … `13_Teaching_and_Methods`) plus a per-figure index. See
**[`results/README.md`](results/README.md)** for the session list, and
**[`results/dec3/README.md`](results/dec3/README.md)** for the Dec 3 per-figure
index with descriptions.

> **About "duplicate" images.** The per-step folders under
> `analysis/outputs/<session>/<step>/` are the raw **working files** that scripts
> read from and write to. `results/<session>/` holds the single **canonical copy**
> of each figure for browsing. A figure can appear in both places by design — read
> it in `results/`. Rebuild a session anytime with
> `python analysis/build_results_folder.py --session dec3` (one figure per result,
> no duplicates).

**Headline figures (Dec 3 — start here):**

- [The whole story in one figure](results/dec3/10_Biological_Summary/combined_explainer.png) — reacts to the buzz (yes, at 26 Hz) but does **not** follow its frequency.
- [Session timeline](results/dec3/01_Session_Timeline/session_timeline.png) — baseline / stimulation / post.
- [Condition × channel response](results/dec3/04_EventAligned_LFP/condition_by_channel_lfp_response_heatmap.png) — `amp180_freq26` strongest.
- [Broadband, not oscillation](results/dec3/05_Frequency_Spectral/spectral_slope_decomposition.png) — 1/f spectral-slope test.
- [No entrainment](results/dec3/06_Phase_Locking/phase_locking_null_floor.png) — phase locking at chance.
- [Spike firing flat ON vs OFF](results/dec3/11_Spikes/peth_onset_ks_good_units.png) — no single-unit effect (confirmed after curation; 29 good units).

**Headline figures (Dec 4 — two probes, four frequencies):**

- [Driven-power change by region](results/dec4/05_Frequency_Spectral/driven_power_change_by_analysis_group.png) — LEC's amplitude-graded **50 Hz** increase; dHPC flat at all frequencies.
- [Spectral slope + ITPC](results/dec4/05_Frequency_Spectral/spectral_slope_itpc_dec4.png) — the 50 Hz power is a real narrowband peak, but **induced, not phase-locked**.
- [Phase locking by condition](results/dec4/06_Phase_Locking/plv_condition_summary.png) — ITPC at the chance floor, including LEC 50 Hz.
- [Full Dec 4 supervisor summary](docs/DEC4_SUPERVISOR_SUMMARY.md) and [Dec 4 figure index](results/dec4/README.md).

## Current Takeaway (Dec 3 + Dec 4)

**Dec 3 (dHPC).** Clear stimulation-related LFP effects — a broadband and
recovery-period response around `amp180_freq26` — but **no clean frequency
entrainment** (26 Hz-band power and PLV sit at chance). After spike sorting **and
curation** (29 good single units), there is **no ON-vs-OFF firing-rate effect**;
that null now holds *post*-curation, not just provisionally.

**Dec 4 (dHPC + LEC).** On the same dHPC probe, the **no-frequency-following
result replicates** and extends to 10 and 50 Hz. The new region, **LEC**, shows a
genuine **amplitude-graded 50 Hz power increase that is *induced*, not
phase-locked** — a frequency-specific power change without onset entrainment.
Both probes are sorted and curated (dHPC 15, LEC 15 good units). And at the
**single-unit** level, **50 Hz / high-amplitude** stimulation modulates a subset
of units in **both** regions (absent at 5/26 Hz) — coherent with the 50 Hz LFP
effect. This response is **active and region-specific** (not a passive echo), but
a coordination test found the two regions do **not** demonstrably "work together"
at 50 Hz (the cross-region LFP coherence rise is best explained by a shared signal,
not neural coordination) ([details](docs/DEC4_COORDINATION_50HZ.md)).

**Across both:** the brain *registers* the stimulus (broadband; and in LEC, 50 Hz
power) but does **not entrain** to its rhythm — with the important caveat that
entrainment could not be properly tested because the delivered vibration was never
recorded as an analog phase reference (fixed in the next round). Laminar/anatomical
claims await probe-geometry confirmation.

## Study Protocol & Recording Phases (Dec 3)

How the session is set up. After setup, the recording runs a **15-minute
baseline**, a **120-minute stimulation block** (1200 randomized trials, each a
**3 s vibration ON** followed by **3 s OFF**), and a **30-minute
post-experiment** period. The six conditions — amplitude `{100, 180, 250}` ×
commanded frequency `{5, 26}` Hz, ~200 repeats each — are interleaved across the
1200 trials. Trial labels and ON/OFF windows come from the randomized controller
schedule in `analysis/outputs/dec3/dec3_condition_sequence.csv`. The
**accelerometer TTL** (`digitalin` bit 7) fires while the device is physically
vibrating and is audited as a delivery/timing QC signal, but it is not used as
the sole trial enumerator.

| Phase | Recording time (s) | Time (min) | Duration | What happens |
|------|-------------------:|-----------:|---------:|--------------|
| Setup / pre-recording | 0 – 640 | 0.0 – 10.7 | ~10.7 min | recording started before the protocol |
| **Baseline** | 640 – 1540 | 10.7 – 25.7 | **15 min** | no stimulation |
| **Stimulation** | 1540 – 8740 | 25.7 – 145.7 | **120 min** | 1200 trials × (3 s ON + 3 s OFF), 6 interleaved conditions |
| **Post-experiment** | 8740 – 10540 | 145.7 – 175.7 | **30 min** | no stimulation |
| Tail | 10540 – 10644 | 175.7 – 177.4 | ~1.7 min | recording stop |
| **Total recording** | 0 – 10644 | 0 – 177.4 | **177.4 min** | |

**Protocol = 15 + 120 + 30 = 165 min.** The 120-min stimulation block matches
`1200 trials × 6 s` exactly. The stimulation window is derived from the command
schedule mapped onto recording time; TTL edges are overlaid to check delivery
and reveal missing/merged/pre/post activity.

Generate the timeline and TTL-vs-LFP overview figures with
[`analysis/plot_ttl_lfp_overview_dec3.py`](analysis/plot_ttl_lfp_overview_dec3.py).
The figures land in `results/dec3/01_Session_Timeline/` and `results/dec3/02_TTL_Alignment/`
([`session_timeline.png`](results/dec3/01_Session_Timeline/session_timeline.png),
[`ttl_lfp_context_and_trials.png`](results/dec3/01_Session_Timeline/ttl_lfp_context_and_trials.png),
[`ttl_on_alignment_per_trial.png`](results/dec3/02_TTL_Alignment/ttl_on_alignment_per_trial.png)).

## Repository Layout

```text
results/                       Curated result figures, ONE FOLDER PER SESSION
  README.md                    Parent index (lists sessions)
  dec3/                        Dec 3 session
    01_Session_Timeline/ … 13_Teaching_and_Methods/
    README.md                  Per-figure index for Dec 3
  dec4/                        Dec 4 session (two probes: dHPC + LEC)

analysis/
  *.py                         Reusable, session-agnostic analysis scripts
  build_results_folder.py      Rebuilds results/<session>/ from the raw outputs
  DEC3_SUPERVISOR_SUMMARY.md   Main Dec 3 summary for presentation
  DEC3_*.md                    Dec 3 notes (Dec 4 gets parallel DEC4_*.md)
  outputs/dec3/                Raw per-step working files for Dec 3
  outputs/dec4/                Raw per-step working files for Dec 4 (dHPC + LEC)

docs/
  RERUN_PIPELINE.md            How to process a new session
  STUDY_NOTES.md               Experimental notes moved out of front page
  RESOURCES_AND_GUIDANCE.md    External links and collaborator guidance
```

Large raw/intermediate arrays are intentionally kept out of GitHub. The repo
tracks code, Markdown summaries, CSV/JSON summaries, HTML reports, and
normal-sized PNG/JPG figures.

## Adding a New Session (e.g. Dec 4)

Dec 4 uses the **same protocol and the same pipeline** as Dec 3 — only the input
data and the output folder change. The scripts are session-agnostic (they take
`--lfp` / `--sequence` / `--output-dir` arguments), so for a new session you:

1. Keep the new recording in its own folder, e.g.
   `~/Documents/Buzsaki Lab/Dec4_session_<date>/…`.
2. Run the pipeline scripts pointed at that data, writing under
   `analysis/outputs/dec4/<step>/` (mirror the `dec3` step folders).
3. Build the curated figures: `python analysis/build_results_folder.py --session dec4`
   → creates `results/dec4/` and updates the parent `results/README.md`.
4. Add `DEC4_*.md` notes alongside the `DEC3_*.md` set.

See [docs/RERUN_PIPELINE.md](docs/RERUN_PIPELINE.md) for the step-by-step checklist.
`results/dec3/` and `results/dec4/` stay completely separate.

## Analysis Pipeline Overview

1. Parse Intan metadata and digital TTL events for QC.
2. Build the randomized condition schedule and authoritative 3 s ON / 3 s OFF
   trial windows.
3. Confirm/exclude bad channels.
4. Extract LFP and compute event-aligned, broadband, frequency-specific,
   time-frequency, trial-level, OFF-control, adaptation, and phase-locking
   analyses.
5. Prepare spike sorting metadata and run Kilosort/SpikeInterface checks.
6. Export Pynapple-compatible intervals/spikes where useful.
7. Run spike ON-vs-OFF analyses (per curated unit set).
8. Detect over-split clusters, curate (good/mua/noise + merges), and confirm
   spike claims against the curated set.
9. Update supervisor summary, dashboard, and major-image guide.

## Rerunning For A Future Study

Use [docs/RERUN_PIPELINE.md](docs/RERUN_PIPELINE.md) as the checklist. The main
inputs to change for a new recording are:

- session directory containing Intan files
- stimulus config/log file
- recording start offset, if needed
- channel count and channel map
- confirmed bad-channel list
- condition schedule and trial timing assumptions
- output folder, for example `analysis/outputs/dec4`

The goal is that future studies can produce a new folder like
`analysis/outputs/<session_id>/` plus a matching supervisor summary and figure
guide.

## GitHub Notes

Both the Dec 3 and Dec 4 analyses (LFP + sorted/curated spikes) are pushed to
`main`. Raw data, large sorter arrays (`*.npy`/`*.npz`), and the curated-merge
working copies are intentionally **not** committed; rerunning the full pipeline
requires local access to those files.
