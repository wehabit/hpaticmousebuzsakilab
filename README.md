# Haptic Stimulation Electrophysiology — Buzsáki Lab Mouse Study

## Abstract

This repository contains the electrophysiological analysis of an awake mouse
implanted with **Cambridge NeuroTech silicon probes** (Intan acquisition, 20 kHz
wideband / 1.25 kHz LFP) and recorded during controlled **vibrotactile
("haptic") stimulation**, across **two sessions**:

- **Dec 3** — a single **128-channel probe in dorsal hippocampus** (**dHPC**,
  Cambridge NeuroTech `H12_2`, Intan Port A). 15-min baseline → **1,200 trials**
  (each **3 s ON / 3 s OFF**) over a 120-min block → 30-min post. Six interleaved
  conditions: amplitude `{100, 180, 250}` × frequency `{5, 26}` Hz, 200 each.
- **Dec 4** — the **same mouse and dHPC probe** plus a **second probe in lateral
  entorhinal cortex** (**LEC**, Port B) = **256 channels**, with two added drive
  frequencies. **2,400 trials** (12 conditions: amplitude `{100, 180, 250}` ×
  frequency `{5, 10, 26, 50}` Hz, 200 each) over a ~5-hour session. Port A is
  the identical dHPC probe/channel map as Dec 3, so dHPC is directly comparable
  across sessions.

The delivered vibration was logged only as crude QC (a 1-bit accelerometer TTL on
Dec 3; no stimulus channel shared on Dec 4), and the actuator ran as a
free-running oscillator — see the stimulus caveat below. Trial timing comes from
the randomized controller schedule aligned to recording time by
`add_recording_times(...)`; for Dec 4 the offset is auto-derived with
`derive_offset_from_log(...)`. The resulting `recording_start_time_s` /
`recording_end_time_s` columns are the shared timing reference used by the LFP,
spike, PETH, and state analyses.

The central questions are whether neural activity (i) **responds** to the stimulus
and (ii) shows evidence consistent with **frequency-following / entrainment**. The
second question is limited by the hardware: the delivered vibration phase was not
recorded, so true stimulus-phase entrainment cannot be proven or ruled out from
these sessions. Both sessions use the **same pipeline**: event-aligned LFP,
broadband and frequency-specific power, time-frequency and 1/f spectral-slope
decomposition, onset-aligned inter-trial phase consistency (PLV/ITPC) tested
against an analytic chance floor, within-trial OFF-window and reference-scheme
controls, an LFP-based movement proxy, and **Kilosort spike sorting with
over-split/merge detection, curation, and peri-event time histograms** — all with
trial-level bootstrap 95% confidence intervals.

**Key findings: Dec 4 / 50 Hz.** (each links to the figure(s) that show it)
1. **High-amplitude 50 Hz produced the clearest single-unit modulation.** In Dec 4,
   a subset of curated units changed firing during stimulation in both
   **dHPC** (dorsal hippocampus) and **LEC** (lateral entorhinal cortex). This is
   the cleanest evidence that the 50 Hz condition engaged neural activity.
   -> [Dec 4 frequency-specific PSTH](results/dec4/11_Spikes/psth_frequency_specific_dec4.png),
   [spike ON/OFF writeup](docs/DEC4_SPIKE_ONOFF_RESULT.md)
2. **The exact 50 Hz LFP line is artifact-limited, especially in LEC.** Disconnected
   LEC electrodes pick up a stronger 50 Hz signal than tissue channels, and the
   cross-region 50 Hz lag is near 0 ms. So the LFP peak is not the main neural
   claim; the spike-rate change is.
   -> [50 Hz artifact check](results/dec4/12_ChannelQC_Traces/50hz_artifact_check.png),
   [pickup gradient](results/dec4/12_ChannelQC_Traces/50hz_pickup_gradient_dhpc_vs_lec.png),
   [artifact writeup](docs/DEC4_50HZ_ARTIFACT_CHECK.md)
3. **Across all curated dHPC units, 50 Hz strengthened theta spike-field
   coordination.** During ON, spikes were more aligned with theta-scale hippocampal
   field waves than during baseline/OFF. This population result uses all curated
   dHPC units, not only one example unit.
   -> [all-dHPC coordination summary](results/dec4/06_Phase_Locking/all_dhpc_kipnis_coordination_amp250.png),
   [population spike-triggered waveforms](results/dec4/06_Phase_Locking/all_dhpc_kipnis_waveforms_amp250.png)
4. **50 Hz did not reproduce the Kipnis-like NREM slow-wave pattern.** The
   Kipnis-relevant native sleep signal is slow-wave coordination around
   0.5-4 Hz. In our Dec 4 50 Hz data, the stronger effect is theta-scale
   coordination, not slow-wave coordination.
   -> [all-dHPC coordination summary](results/dec4/06_Phase_Locking/all_dhpc_kipnis_coordination_amp250.png),
   [Kipnis speaker notes](docs/JIANG_XIE_KIPNIS_GLYMPHATIC_SPEAKER_NOTES.md)
5. **Next-study interpretation:** use 50 Hz as a target-engagement anchor, then
   test frequencies that map more directly onto the glymphatic literature:
   8-10 Hz for theta-like hippocampal coordination and 1-2 Hz for slow-wave-like
   NREM coordination, with a recorded analog vibration phase and a clearance
   readout.
   -> [frequency reference menu](docs/FREQUENCY_REFERENCE_MENU.md)

**Caveat — our hardware was not equipped to test entrainment.** Neither session
recorded a usable **analog copy of the delivered vibration**, the actuator ran
free-running (phase never reset), and the digital sync channel **never captured the
carrier** (it toggled at ~4 Hz regardless of drive frequency — see the
[TTL diagnostic](analysis/outputs/dec3/ttl_diagnostic/ttl_cannot_recover_tactor_phase.png)).
So the stimulus's instantaneous phase is **unrecoverable**. The correct conclusion
is **not** "the brain cannot entrain"; it is "we do not have evidence of
entrainment in these data, and the definitive phase-following test was not
possible." Band power is measurable, but phase-following cannot be tested without a
phase reference.

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
**spike sorting + curation**. Probe metadata are now confirmed from Vöröslakos's
reply: dHPC = **H12_2**, Port A / Intan `0-127`; LEC = **H15**, Port B / Intan
`128-255`, AP 3.8 / ML 3.8 / **10 degrees**. The `amplifier.xml` `channelGroups`
order is the verified map order, and the Cambridge NeuroTech ASSY-350 maps are the
right probe-map references. Functional physiology supports the placement: dHPC
ripples support CA1/dHPC; LEC quiet-state slow/delta physiology supports cortex/LEC
([metadata note](docs/DEC_PROBE_METADATA_VOROSLAKOS.md)). What remains conservative
is final manual bad-channel review and fine **depth / laminar / subregion /
medial-lateral** interpretation. Plus the analog stimulus recording above (see
[docs/DEC3_EXTERNAL_BLOCKERS.md](docs/DEC3_EXTERNAL_BLOCKERS.md)).

## Start Here

- [**CONCLUSIONS.md**](CONCLUSIONS.md): one-page synthesis across Dec 3 + Dec 4 —
  what is supported, what is explicitly negative, and what the next recording needs.
- [**Results — every figure**](results/README.md): all result figures, curated
  and grouped by analysis type (the canonical place to browse results).
- [Dec 3 Supervisor Summary](docs/DEC3_SUPERVISOR_SUMMARY.md): clean
  findings, figure links, methods, caveats, and suggested presentation order.
- [**Dec 4 Supervisor Summary**](docs/DEC4_SUPERVISOR_SUMMARY.md): two-probe
  (dHPC + LEC) session, four drive frequencies. Headline: dHPC shows no clean
  frequency-following evidence (replicating Dec 3 on the same probe); LEC shows an
  amplitude-graded 50 Hz LFP power peak that is artifact-suspect and not a proven
  entrainment result. Figures in [`results/dec4/`](results/dec4/README.md).
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
  Misi, Buzcode, CellExplorer, Pynapple, Kilosort, and related references.

## Results And Figures

Curated figures live in **[`results/`](results/)**, with one folder per session:
[`results/dec3/`](results/dec3/README.md) and
[`results/dec4/`](results/dec4/README.md). Those per-session README files are the
best way to browse figures on GitHub. The larger `analysis/outputs/` folders are
working outputs used by the scripts; use `results/` for presentation figures.

**Dec 3 figures to start with:**

- [Whole-story figure](results/dec3/10_Biological_Summary/combined_explainer.png) — LFP responds, especially around 26 Hz conditions, but not as clean frequency-following.
- [Condition × channel LFP response](results/dec3/04_EventAligned_LFP/condition_by_channel_lfp_response_heatmap.png) — `amp180_freq26` is the clearest LFP condition.
- [Spike firing around ON](results/dec3/11_Spikes/peth_onset_ks_good_units.png) — no Dec 3 single-unit ON/OFF effect after curation.

**Dec 4 figures to start with:**

- [Whole-story figure](results/dec4/10_Biological_Summary/combined_explainer.png) — dHPC stays non-following; LEC 50 Hz LFP is artifact-suspect; spikes carry the cleaner neural result.
- [Cross-dataset spike ON/OFF](results/dec4/11_Spikes/spike_onoff_cross_dataset.png) — Dec 3 null at 5/26 Hz; Dec 4 50 Hz/high-amplitude responders in both dHPC and LEC.
- [50 Hz artifact check](results/dec4/12_ChannelQC_Traces/50hz_artifact_check.png) — why the LEC 50 Hz LFP peak is not clean neural evidence.
- [Unit 87 artifact screen](results/dec4/11_Spikes/unit87_acg_artifact_screen.png) — example spike-artifact control for a key up-going unit.

## Current Takeaway (Dec 3 + Dec 4)

**Plain English.** The brain clearly noticed the haptic stimulation, but these
recordings do **not** prove that brain rhythms synchronized to the vibration. The
strongest neural finding is in Dec 4: high-amplitude **50 Hz** stimulation changes
single-unit firing rates.

**Dec 3 (dHPC only).** The hippocampal LFP changed during stimulation, especially
around the 26 Hz conditions. That signal looks more like a broad onset/offset and
recovery response than a clean 26 Hz rhythm. After spike sorting and curation
(`29` good units), single units did **not** show a reliable ON-vs-OFF firing-rate
change. So Dec 3 is: **clear LFP/population response, no curated single-unit rate
effect**.

**Dec 4 (dHPC + LEC).** The same dHPC probe again shows no clean
frequency-following evidence, even with 10 and 50 Hz added. LEC shows a strong
50 Hz LFP peak during stimulation, but that LFP peak is contaminated by pickup and
is **not** clean neural evidence. The cleaner result is spikes: curated units in
both dHPC and LEC change firing rate most strongly at **50 Hz / high amplitude**
(Dec 4 dHPC: `19/180` responsive unit-conditions; Dec 4 LEC: `13/180`), while Dec 3
at 5/26 Hz stayed null (`0/174`).

**What that means.** The 50 Hz response is probably not just one identical passive
artifact/readout: dHPC and LEC transform the same input differently, with a
driven-up subset in dHPC and net suppression in LEC. But the two regions do **not**
show clear 50 Hz coordination, and true entrainment could not be tested because the
delivered vibration phase was not recorded. Region/probe identity is now supported
by metadata and physiology; fine anatomy/layer claims remain conservative.

## Repository Layout

```text
README.md                      Front-page study summary and navigation
CONCLUSIONS.md                 One-page scientific synthesis across Dec 3 + Dec 4

results/                       Curated presentation figures
  README.md                    Session list
  dec3/README.md               Dec 3 figure index
  dec4/README.md               Dec 4 figure index

analysis/
  README.md                    Map of scripts, outputs, and analysis entry points
  *.py                         Timing, LFP, spike, state, artifact, and plotting scripts
  envs/                        Environment setup helpers
  outputs/dec3/                Dec 3 working outputs and generated reports
  outputs/dec4/                Dec 4 working outputs and generated reports
  outputs/cross_dataset_*/     Combined Dec 3/Dec 4 analyses

docs/
  DEC3_SUPERVISOR_SUMMARY.md   Dec 3 presentation-facing summary
  DEC4_SUPERVISOR_SUMMARY.md   Dec 4 presentation-facing summary
  DEC4_SPIKE_ONOFF_RESULT.md   Main Dec 4 single-unit result
  DEC4_50HZ_ARTIFACT_CHECK.md  LEC 50 Hz artifact control
  DEC*_*.md                    Supporting result, method, and teaching notes

resources/                     Reference papers, workshop material, probe docs
firmware/                      Stimulator firmware snippet used for timing/phase audit
```

Raw Intan recordings, large sorter arrays, local virtual environments, and the
draft presentation are intentionally kept out of GitHub. The repo tracks code,
Markdown summaries, CSV/JSON summaries, HTML reports, reference resources, and
normal-sized PNG/JPG figures.

## Analysis Pipeline Overview

1. Parse Intan metadata, controller logs/stimulus configs, and sync signals where
   available (Dec 3 TTL QC; Dec 4 log-offset timing).
2. Build the authoritative condition table: baseline, stimulation, post-study,
   and every 3 s ON / 3 s OFF trial window.
3. Run channel QC per probe; define disconnected/hot/bad channels and reference
   schemes.
4. Extract LFP and run core LFP analyses: event-aligned response, broadband and
   OFF/recovery windows, driven-frequency/time-frequency power, 1/f residuals,
   onset-aligned PLV/ITPC, reference sensitivity, movement/artifact controls,
   and adaptation.
5. Compare baseline / ON / OFF / post-study states and model session drift.
6. Prepare spike-sorting metadata/channel maps, run SpikeInterface sanity checks,
   and run Kilosort for each sorted probe.
7. Run cluster-quality checks, detect over-splits, apply curation/merges, and keep
   fine depth/layer/subregion claims conservative unless implant orientation or
   histology supports them.
8. Export Pynapple-compatible intervals/spikes where useful, then run PETH,
   ON-vs-OFF, baseline/post-study, and drift-corrected firing-rate analyses on
   curated unit sets.
9. Run targeted follow-ups: cell-type/ACG summaries, ripple-state summaries,
   Dec 4 LEC slow-oscillation screen, Dec 4 50 Hz artifact checks, and dHPC-LEC
   coordination checks.
10. Build curated result folders and update dashboards, conclusions, supervisor
   summaries, and figure indexes.

## GitHub Notes

The GitHub repository tracks the Dec 3 and Dec 4 analysis code, summaries,
CSV/JSON tables, and normal-sized figures for LFP + sorted/curated spike
results. Raw data, large sorter arrays (`*.npy`/`*.npz`), and curated-merge
working copies are intentionally **not** committed; rerunning the full pipeline
requires local access to those files.
