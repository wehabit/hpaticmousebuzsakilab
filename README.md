# Haptic Stimulation Electrophysiology — Buzsáki Lab Mouse Study

## Abstract

This repository contains the electrophysiological analysis of an awake mouse
implanted with a 128-channel high-density silicon probe (Cambridge NeuroTech;
Intan acquisition, 20 kHz wideband / 1.25 kHz LFP) and recorded during controlled
**vibrotactile ("haptic") stimulation**. After a 15-minute pre-stimulus baseline,
a vibrating actuator delivered **1,200 stimulation trials** across a 120-minute
block — each trial **3 s ON / 3 s OFF** — followed by a 30-minute post-stimulus
period. Trials were drawn from **six interleaved conditions** crossing three drive
amplitudes (100 / 180 / 250) with two carrier frequencies (**5 and 26 Hz**),
~200 repeats each; an accelerometer TTL recorded the physical vibration and
anchors every trial to its true stimulus onset.

The central questions are whether neural activity (i) **responds** to the stimulus
and (ii) **entrains** to its 5/26 Hz rhythm. We characterize the local field
potential and single-unit spiking with event-aligned LFP, broadband and
frequency-specific power, time-frequency and 1/f spectral-slope decomposition,
inter-trial phase locking (PLV/ITPC) tested against an analytic chance floor,
within-trial OFF-window and reference-scheme controls, an LFP-based movement
proxy, and Kilosort spike sorting with peri-event time histograms — all with
trial-level bootstrap 95% confidence intervals over 200 trials per condition.

**Key findings.** (1) A **real, amplitude-graded broadband LFP response**,
strongest for the 26 Hz / amplitude-180 condition and dominated by the
onset/offset *transitions* rather than a sustained lift. (2) **No
frequency-following**: no narrowband peak rises above the 1/f background and phase
locking sits at chance — the brain registers the stimulus but does not entrain to
its frequency. (3) **No reliable ON-vs-OFF change in single-unit firing**
(provisional, pending manual curation). (4) These conclusions are **robust** to
the referencing scheme and to excluding movement-contaminated trials. Methods
follow Buzsáki-lab tooling (buzcode / CellExplorer / Kilosort) and the analysis
conventions in Cohen (2014).

**Important caveat (stimulus delivery).** On later review we found that the
delivered vibration was **not clean at the nominal 5 and 26 Hz** — the input
signal's frequency content at those rates could not be clearly resolved in this
session. The absence of frequency entrainment must therefore be read partly as a
**limitation of stimulus delivery**, not solely as a neural result. The next
recording addresses this directly: it drives the stimulus from a **digital TTL**
and verifies the **clarity of the input signal** at the target frequencies, so a
genuine entrainment test is possible.

The repository is organized so each recording/session can be processed,
summarized, and compared without losing the original study notes. The current
completed analysis pass is the **Dec 3 recording**; spike-level and laminar/CSD
analyses remain provisional pending Phy curation and confirmation of the probe
geometry and channel map.

## Start Here

- [**Results — every figure**](results/README.md): all result figures, curated
  and grouped by analysis type (the canonical place to browse results).
- [Dec 3 Supervisor Summary](docs/DEC3_SUPERVISOR_SUMMARY.md): clean
  findings, figure links, methods, caveats, and suggested presentation order.
- [Dec 3 Results Dashboard](analysis/outputs/dec3/RESULTS_DASHBOARD.html):
  clickable local HTML dashboard of result pages and figures.
- [Dec 3 Major Images](docs/DEC3_MAJOR_IMAGES.md): figure-by-figure guide.
- [Dec 3 Image Walkthrough](docs/DEC3_IMAGE_WALKTHROUGH.md): teaching guide
  explaining how each figure was generated and what to take away from it.
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
- [Spike firing flat ON vs OFF](results/dec3/11_Spikes/peth_onset_ks_good_units.png) — provisional, pre-curation.

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
  dec4/                        Dec 4 session (created when processed)

analysis/
  *.py                         Reusable, session-agnostic analysis scripts
  build_results_folder.py      Rebuilds results/<session>/ from the raw outputs
  DEC3_SUPERVISOR_SUMMARY.md   Main Dec 3 summary for presentation
  DEC3_*.md                    Dec 3 notes (Dec 4 gets parallel DEC4_*.md)
  outputs/dec3/                Raw per-step working files for Dec 3
  outputs/dec4/                Raw per-step working files for Dec 4 (when processed)

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
