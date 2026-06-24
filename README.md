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
  frequencies. **2,400 trials** (12 conditions: amplitude `{100, 180, 250}` ×
  frequency `{5, 10, 26, 50}` Hz, ~200 each) over a ~5-hour session. Port A is
  the identical dHPC probe/channel map as Dec 3, so dHPC is **directly comparable
  across sessions**.

The delivered vibration was logged only as crude QC (a 1-bit accelerometer TTL on
Dec 3; no stimulus channel shared on Dec 4), and the actuator ran as a
free-running oscillator — see the stimulus caveat below. Trial timing comes from
the randomized controller schedule, validated against the recording-start offset.

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

**Key findings.** (each links to the figure(s) that show it)
1. A **real, amplitude-graded broadband LFP response**, strongest for the
   `amp180_freq26` condition (Dec 3). The response is **transition-weighted
   (onset/offset) rather than a sustained lift** — though, on the trial-level
   bootstrap CIs, that offset-heavy asymmetry is statistically reliable only at
   `amp250_freq26` (CI excludes 0) and marginal at `amp180_freq26`.
   → [condition × channel heatmap](results/dec3/04_EventAligned_LFP/condition_by_channel_lfp_response_heatmap.png),
   [transition index](results/dec3/07_Broadband_OFFcontrol_TrialStats/transition_index_condition.png)
2. **No clean frequency-following evidence in dHPC at any tested frequency**
   (5/10/26/50 Hz): no sustained narrowband peak above the 1/f background, and
   onset-aligned phase consistency sits near chance. This **replicates across
   Dec 3 and Dec 4 on the identical probe** and extends to the two new
   frequencies. True stimulus-phase locking remains untestable without a recorded
   vibration phase reference.
   → [Dec 3 spectral-slope decomposition](results/dec3/05_Frequency_Spectral/spectral_slope_decomposition.png),
   [Dec 3 phase-locking null floor](results/dec3/06_Phase_Locking/phase_locking_null_floor.png),
   [Dec 4 spectral slope + ITPC](results/dec4/05_Frequency_Spectral/spectral_slope_itpc_dec4.png)
3. **LEC (Dec 4) shows an amplitude-graded narrowband 50 Hz LFP power increase**
   with no comparable effect at 5/10/26 Hz or in dHPC. Onset-aligned ITPC sits near
   chance, so this is a stimulus-state power peak, **not a proven entrainment
   result**. **But a dedicated artifact check shows this LFP effect is contaminated
   by non-neural pickup:** disconnected LEC electrodes (which can't record neurons)
   pick up **~6× more** 50 Hz during ON than tissue, and the cross-region 50 Hz lag
   is ~0 ms (a shared signal). So the LEC 50 Hz *LFP* is not clean neural evidence
   — the single-unit rate change (finding 4) is.
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

**What that means.** The 50 Hz response is probably not just a passive echo of the
stimulus: dHPC and LEC transform the same input differently, with a driven-up
subset in dHPC and net suppression in LEC. But the two regions do **not** show
clear 50 Hz coordination, and true entrainment could not be tested because the
delivered vibration phase was not recorded. Anatomy/layer claims still need the
final probe map and histology.

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
   depth/layer claims provisional until the probe map/histology are confirmed.
8. Export Pynapple-compatible intervals/spikes where useful, then run PETH,
   ON-vs-OFF, baseline/post-study, and drift-corrected firing-rate analyses on
   curated unit sets.
9. Run targeted follow-ups: cell-type/ACG summaries, ripple-state summaries,
   Dec 4 50 Hz artifact checks, and dHPC-LEC coordination checks.
10. Build curated result folders and update dashboards, conclusions, supervisor
   summaries, and figure indexes.

## GitHub Notes

The GitHub repository tracks the Dec 3 and Dec 4 analysis code, summaries,
CSV/JSON tables, and normal-sized figures for LFP + sorted/curated spike
results. Raw data, large sorter arrays (`*.npy`/`*.npz`), and curated-merge
working copies are intentionally **not** committed; rerunning the full pipeline
requires local access to those files.
