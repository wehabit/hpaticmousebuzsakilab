# Haptic Mouse Buzsaki Lab Analysis

Python-first analysis pipeline for Intan haptic stimulation recordings from the
Buzsaki Lab mouse study. The repo is organized so each recording/session can be
processed, summarized, and compared without losing the original study notes.

The current completed analysis pass is for the **Dec 3 recording**.

## Start Here

- [Dec 3 Supervisor Summary](analysis/DEC3_SUPERVISOR_SUMMARY.md): clean
  findings, figure links, methods, caveats, and suggested presentation order.
- [Dec 3 Results Dashboard](analysis/outputs/dec3/RESULTS_DASHBOARD.html):
  clickable local HTML dashboard of result pages and figures.
- [Dec 3 Major Images](analysis/DEC3_MAJOR_IMAGES.md): figure-by-figure guide.
- [Reusable Pipeline](docs/RERUN_PIPELINE.md): how to repeat this analysis for
  future recordings/conditions.
- [Study Notes](docs/STUDY_NOTES.md): Dec 3/Dec 4 experiment notes, coordinates,
  channel notes, and original collaborator context.
- [Experiment Setup Photos](https://photos.app.goo.gl/NzK9YqrbCPufYTYV8):
  Google Photos album showing the study/experiment setup.
- [Resources And Guidance](docs/RESOURCES_AND_GUIDANCE.md): links from Nick,
  Mishi, Buzcode, CellExplorer, Pynapple, Kilosort, and related references.

## Current Dec 3 Takeaway

Dec 3 shows clear stimulation-related LFP effects, especially a broadband and
recovery-period response around `amp180_freq26`. The evidence does **not** yet
support a simple final claim of clean sustained 26 Hz entrainment: 26 Hz-band
power and PLV are more cautious. Spike sorting has run, but the cleanest
high-confidence single-unit subset does not show a robust ON-period firing-rate
increase. Spike claims remain provisional until Phy curation and final probe
geometry/channel order are confirmed.

## Study Protocol & Recording Phases (Dec 3)

How the session is set up. After setup, the recording runs a **15-minute
baseline**, a **120-minute stimulation block** (1200 randomized trials, each a
**3 s vibration ON** followed by **3 s OFF**), and a **30-minute
post-experiment** period. The six conditions — amplitude `{100, 180, 250}` ×
commanded frequency `{5, 26}` Hz, ~200 repeats each — are interleaved across the
1200 trials. Stimulation onset is captured by an **accelerometer TTL**
(`digitalin` bit 7) that fires while the device is physically vibrating, so each
TTL burst's first edge marks the true vibration onset.

| Phase | Recording time (s) | Time (min) | Duration | What happens |
|------|-------------------:|-----------:|---------:|--------------|
| Setup / pre-recording | 0 – 640 | 0.0 – 10.7 | ~10.7 min | recording started before the protocol |
| **Baseline** | 640 – 1540 | 10.7 – 25.7 | **15 min** | no stimulation |
| **Stimulation** | 1540 – 8740 | 25.7 – 145.7 | **120 min** | 1200 trials × (3 s ON + 3 s OFF), 6 interleaved conditions |
| **Post-experiment** | 8740 – 10540 | 145.7 – 175.7 | **30 min** | no stimulation |
| Tail | 10540 – 10644 | 175.7 – 177.4 | ~1.7 min | recording stop |
| **Total recording** | 0 – 10644 | 0 – 177.4 | **177.4 min** | |

**Protocol = 15 + 120 + 30 = 165 min.** The 120-min stimulation block matches
`1200 trials × 6 s` exactly. The stimulation window is measured directly from the
accelerometer TTL; the baseline/post boundaries are the intended design mapped
onto recording time (the exact baseline start is derived from the controller
offset).

Generate the timeline and TTL-vs-LFP overview figures with
[`analysis/plot_ttl_lfp_overview_dec3.py`](analysis/plot_ttl_lfp_overview_dec3.py)
→ `analysis/outputs/dec3/ttl_lfp_overview/` (`session_timeline.png`,
`ttl_lfp_trial_zoom.png`, `lfp_burst_onset_aligned.png`).

## Repository Layout

```text
analysis/
  *.py                         Reusable analysis scripts
  DEC3_SUPERVISOR_SUMMARY.md   Main Dec 3 summary for presentation
  DEC3_RESULTS_SUMMARY.md      Longer interpretation and results notes
  DEC3_MAJOR_IMAGES.md         Important figure map
  DEC3_ANALYSIS_LOG.md         Detailed run log
  outputs/dec3/                Dec 3 reports, tables, and normal-sized figures

docs/
  RERUN_PIPELINE.md            Future-study rerun guide
  STUDY_NOTES.md               Experimental notes moved out of front page
  RESOURCES_AND_GUIDANCE.md    External links and collaborator guidance
```

Large raw/intermediate arrays are intentionally kept out of GitHub. The repo
tracks code, Markdown summaries, CSV/JSON summaries, HTML reports, and
normal-sized PNG/JPG figures.

## Analysis Pipeline Overview

1. Parse Intan metadata and digital TTL events.
2. Build the randomized condition schedule and 3 s ON / 3 s OFF trial windows.
3. Confirm/exclude bad channels.
4. Extract LFP and compute event-aligned, broadband, frequency-specific,
   time-frequency, trial-level, OFF-control, adaptation, and phase-locking
   analyses.
5. Prepare spike sorting metadata and run Kilosort/SpikeInterface checks.
6. Export Pynapple-compatible intervals/spikes where useful.
7. Run provisional spike ON-vs-OFF analyses.
8. Perform Phy curation before final spike claims.
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

The latest pushed Dec 3 summary is on `main`. Raw data and large sorter arrays
are not committed; rerunning the full pipeline requires local access to those
files.
