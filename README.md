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
