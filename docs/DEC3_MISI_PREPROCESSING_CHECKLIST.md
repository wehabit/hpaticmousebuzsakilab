# Dec 3 Misi Preprocessing Checklist

Scope: Dec 3 session `Haptic_Stim_session1_251203_143031`.

Primary guidance checked:

- `resources/Data_preprocessing.docx`
- `resources/data_processing.md`
- `resources/Ephys_workshop/code/matlab/preprocessing_pipeline.m`
- `resources/Ephys_workshop/code/matlab/preprocessing_pipeline_Raw_data.m`
- `resources/Ephys_workshop/code/matlab/Process_IntanDigitalChannels.m`
- `resources/Ephys_workshop/code/matlab/RemoveArtefact_dat.m`
- `resources/Ephys_workshop/code/matlab/removeNoiseFromDat.m`
- `resources/Ephys_workshop/docs/modules/12_preprocessing_spikesorting.md`

This checklist tracks what has actually been done for Dec 3, what is
provisional, and what should not be forced because the required data are not
available in this checkout.

## Current Bottom Line

- The LFP and trial-window analysis pass is now reproducible and has been rerun
  with corrected 128-channel metadata and confirmed bad-channel exclusion.
- Pynapple interval exports are present and verified: 15 `.npz` interval files,
  1200 trials, 200 ON intervals and 200 OFF-control intervals per condition.
- Kilosort spike arrays are not present locally. The expected storage location is
  the Modal volume `dec3-kilosort-data`, under `/dec3/kilosort4_results`.
- Spike-level summaries already in the repo are therefore historical/provisional
  until the Kilosort `.npy` arrays are restored and the spike/Pynapple/PETH
  scripts are rerun.
- Manual Phy curation, CellExplorer metrics, monosynaptic connection analysis,
  and anatomy/region tagging remain incomplete because they require curated
  units and confirmed probe geometry/region labels.

## Checklist

| # | Misi / Buzcode-style step | Dec 3 status | Evidence | Resolution / next action |
|---:|---|---|---|---|
| 1 | Concatenate daily recordings | Not needed for current Dec 3 pass | One Intan session folder is being analyzed as Dec 3 session 1 | If multiple fragments are later supplied, concatenate before LFP/spike sorting and rebuild metadata |
| 2 | Parse Intan metadata and digital channels | Done | `analysis/outputs/dec3/info_rhd_summary.json`, `session_summary.json`, `digital_edges_ch*.csv`, `stimulation_events.csv` | Keep controller schedule as authoritative; use TTL only as delivery/timing QC |
| 3 | Fix/verify XML and channel groups | Done | `amplifier.xml`, `amplifier_original_256ch.xml`, `analysis/outputs/dec3/metadata_correction_summary.json` | Active XML is 128 channels with four 32-channel analysis/spike groups |
| 4 | Extract LFP | Done | `Haptic_Stim_session1_251203_143031/amplifier.lfp`, `analysis/outputs/dec3/lfp_extraction_summary.json` | LFP sample count and size match 20 kHz to 1250 Hz decimation |
| 5 | Bad-channel identification/removal | Done for analysis; still not Neuroscope-manual | `analysis/final_preprocessing_dec3.json`, `analysis/outputs/dec3/channel_qc*` | Current excluded channels: `5, 6, 7, 32, 33, 34, 43, 66, 67`; manual Neuroscope review can refine this |
| 6 | Artifact-aware handling | Done for LFP metrics; raw `.dat` not modified | `artifact_aware_lfp`, `broadband_transition`, `off_control_broadband`, `trial_level_stats_equal_spectral_windows` outputs | Transition windows are analyzed separately; raw artifact removal was not applied to preserve original data |
| 7 | Median subtraction / referencing | Done for analysis pass | `analysis/final_preprocessing_dec3.json`, `reference_sensitivity_lfp` outputs | Main LFP pass uses analysis-group median reference; reference sensitivity checked |
| 8 | Trial schedule and event alignment | Done | `dec3_condition_sequence.csv`, `spike_sorting_prep/trial_windows.csv`, `pynapple_intervals/*.npz` | 1200 trials, 6 conditions, 200 repeats each, 3 s ON / 3 s OFF |
| 9 | Ripple detection | Not done; insufficient channel/anatomy decisions | No ripple-output folder is present | Needs hippocampal layer/channel selection and sleep/quiet-state context before calling ripples |
| 10 | Dentate spike detection | Not done; insufficient channel/anatomy decisions | No dentate-spike output is present | Needs dentate/hilus/granule-layer channel assignment and collaborator validation |
| 11 | Up/down state detection | Not done; likely not appropriate from current awake haptic-only context | No state-output folder is present | Requires cortical channels and sleep/quiet-state intervals; skip unless matching data are supplied |
| 12 | Automatic state scoring | Not done; required data absent | No sleep scoring files, EMG, video/tracking, or state annotations | Requires behavioral/sleep-state data |
| 13 | Manual state scoring / TheStateEditor | Not done; required data absent | No manual state files | Requires state-scoring inputs and human review |
| 14 | Spike sorting prep | Done | `spike_sorting_prep`, `spikeinterface_setup`, `spikeinterface_test_sort` outputs | SpikeInterface smoke test succeeds; this is not final sorting |
| 15 | Kilosort sorting | Historical/provisional only; arrays missing locally | Local folder has small summaries/TSV/PNG/logs, but no `spike_times.npy` or `spike_clusters.npy` | Authenticate Modal, restore arrays, then rerun spike exports and PETH analyses |
| 16 | Manual Phy curation | Not done | `docs/PHY_DEC3_SETUP.md`; no curated Phy output is present | Requires restored Kilosort output and manual curation |
| 17 | CellExplorer metrics / PYR-INT curation | Not done | No CellExplorer `cell_metrics` output is present | Requires curated spike sorting and confirmed region/channel metadata |
| 18 | Monosynaptic connections | Not done | No CellExplorer monosynaptic output is present | Requires curated units and CellExplorer-compatible session files |
| 19 | Region tagging / anatomical labels | Provisional only | `docs/STUDY_NOTES.md`, `docs/OPEN_QUESTIONS.md` | Need probe orientation/contact-order confirmation before assigning region-level claims |
| 20 | Behavioral analysis | Not done; behavior data absent | No tracking/video/behavior tables found | Requires behavioral files beyond Intan TTL and stimulus schedule |

## Kilosort Arrays

Expected remote location:

```bash
dec3-kilosort-data:/dec3/kilosort4_results
```

Expected local restore target:

```bash
analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/
```

Files needed before the spike side can be trusted/rerun:

- `spike_times.npy`
- `spike_clusters.npy`
- `templates.npy`
- `ops.npy`
- `amplitudes.npy`
- `channel_map.npy`
- `channel_positions.npy`
- `cluster_group.tsv` or equivalent cluster labels

Modal CLI is installed in `.venv-dec3`, but this machine is not authenticated
with Modal yet. After authentication, use:

```bash
.venv-dec3/bin/modal token new --profile default --activate --verify
.venv-dec3/bin/modal volume ls dec3-kilosort-data /dec3/kilosort4_results
.venv-dec3/bin/modal volume get dec3-kilosort-data /dec3/kilosort4_results analysis/outputs/dec3/modal_kilosort4_results
```

Then rerun:

```bash
MPLCONFIGDIR=.mplconfig .venv-dec3/bin/python analysis/export_kilosort_pynapple_dec3.py
MPLCONFIGDIR=.mplconfig .venv-dec3/bin/python analysis/spike_peth_on_off_dec3.py
MPLCONFIGDIR=.mplconfig .venv-dec3/bin/python analysis/spike_peth_high_confidence_dec3.py
```

Until this is done, Dec 3 spike claims should remain labeled provisional.
