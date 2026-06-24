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

This checklist tracks what has actually been done for Dec 3, what is still
provisional, and what should not be forced because the required external inputs
are absent.

## Current Bottom Line

- The LFP and trial-window analysis pass is now reproducible and has been rerun
  with corrected 128-channel metadata and confirmed bad-channel exclusion.
- Pynapple interval exports are present and verified: 15 `.npz` interval files,
  1200 trials, 200 ON intervals and 200 OFF-control intervals per condition.
- Pynapple **spike** `TsGroup` exports are now also present locally
  (`pynapple_spikes/*.npz`, regenerated from the curated arrays; git-ignored as
  regenerable). They are not required for the ON/OFF stats (which use the Kilosort
  NumPy arrays directly).
- Kilosort spike arrays are now present locally in
  `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/`, and the
  Dec 3 spike analyses have been rerun through curated/merged labels.
- The current curated Dec 3 spike result is final for the present dataset:
  **29 curated good units, 174 unit-condition tests, 0 responsive at q<0.05**.
  This confirms the single-unit null at 5/26 Hz.
- Cell-type and ACG-type analyses were completed in Python as CellExplorer-style
  follow-ups, and ripple participation was run as an exploratory dHPC analysis.
  What is still missing is an official CellExplorer `cell_metrics` export and a
  monosynaptic connection workflow.
- Anatomy/layer labels remain provisional because the exact Cambridge NeuroTech
  site map/adapter wiring and histology are not yet confirmed.

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
| 9 | Ripple detection | Done as exploratory follow-up; CA1 layer still provisional | `analysis/outputs/cross_dataset_spike_compare/ripples/`, [DEC_RIPPLE_STATES.md](DEC_RIPPLE_STATES.md) | Use as descriptive dHPC ripple/state physiology only; no SWR-memory or stimulation-specific ripple claim until channel map/state context are confirmed |
| 10 | Dentate spike detection | Not done; insufficient channel/anatomy decisions | No dentate-spike output is present | Needs dentate/hilus/granule-layer channel assignment and collaborator validation |
| 11 | Up/down state detection | Not done; likely not appropriate from current awake haptic-only context | No state-output folder is present | Requires cortical channels and sleep/quiet-state intervals; skip unless matching data are supplied |
| 12 | Automatic state scoring | Not done; required data absent | No sleep scoring files, EMG, video/tracking, or state annotations | Requires behavioral/sleep-state data |
| 13 | Manual state scoring / TheStateEditor | Not done; required data absent | No manual state files | Requires state-scoring inputs and human review |
| 14 | Spike sorting prep | Done | `spike_sorting_prep`, `spikeinterface_setup`, `spikeinterface_test_sort` outputs | SpikeInterface smoke test succeeds; Kilosort output is the final sorting input |
| 15 | Kilosort sorting | Done for current analysis | `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/spike_times.npy`, `spike_clusters.npy`, `templates.npy`; `modal_kilosort_run_summary.json` | Geometry/depth labels remain provisional until the exact probe map is confirmed |
| 16 | Phy-style curation / merge labels | Done for current analysis | `analysis/outputs/dec3/curated_merged/`, `analysis/outputs/dec3/spike_peth_curated/report.json`, `analysis/outputs/cross_dataset_spike_compare/overview.csv` | Current result: 29 curated good units; 0/174 responsive unit-conditions |
| 17 | CellExplorer-style PYR/INT and ACG typing | Done in Python; no official `cell_metrics.mat` export | [DEC_CELLTYPE_CLASSIFICATION.md](DEC_CELLTYPE_CLASSIFICATION.md), [DEC_ACG_TYPE_CLASSIFICATION.md](DEC_ACG_TYPE_CLASSIFICATION.md), `analysis/outputs/cross_dataset_spike_compare/celltype/`, `acg_type/` | Use putative pyr/interneuron labels cautiously; full official CellExplorer export remains optional/future |
| 18 | Monosynaptic connections | Not done | No CellExplorer monosynaptic output is present | Requires curated units and CellExplorer-compatible session files |
| 19 | Region tagging / anatomical labels | Provisional only | `docs/STUDY_NOTES.md`, `docs/OPEN_QUESTIONS.md` | Need probe orientation/contact-order confirmation before assigning region-level claims |
| 20 | Behavioral analysis | Not done; behavior data absent | No tracking/video/behavior tables found | Requires behavioral files beyond Intan TTL and stimulus schedule |

## Kilosort Arrays

Current local location:

```bash
analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/
```

Key arrays now present locally:

- `spike_times.npy`
- `spike_clusters.npy`
- `templates.npy`
- `ops.npy`
- `amplitudes.npy`
- `channel_map.npy`
- `channel_positions.npy`
- `cluster_group.tsv` or equivalent cluster labels

The Dec 3 spike analyses have already been rerun from these arrays:

```bash
MPLCONFIGDIR=.mplconfig .venv-dec3/bin/python analysis/export_kilosort_pynapple_dec3.py
MPLCONFIGDIR=.mplconfig .venv-dec3/bin/python analysis/spike_peth_on_off_dec3.py
MPLCONFIGDIR=.mplconfig .venv-dec3/bin/python analysis/spike_peth_high_confidence_dec3.py
MPLCONFIGDIR=.mplconfig .venv-dec3/bin/python analysis/spike_peth_curated_dec3.py
```

Note: both Pynapple exports are now present locally — the **interval** files
(`pynapple_intervals/*.npz`) and the **spike** `TsGroup` files
(`pynapple_spikes/kilosort_all_units_tsgroup.npz` and `kilosort_ks_good_units_tsgroup.npz`,
28 KS-good units), regenerated from the curated arrays with:

```bash
.venv-dec3/bin/python analysis/export_kilosort_pynapple_dec3.py \
  --kilosort-dir analysis/outputs/dec3/curated_merged \
  --output-dir analysis/outputs/dec3/pynapple_spikes
```

The spike `.npz` are **git-ignored** (regenerable, and the all-units file is
>100 MB) and are **not required** for the final ON/OFF statistics — those run from
the Kilosort NumPy arrays directly. The trusted final spike story is the curated
ON/OFF result in [DEC3_CURATED_SPIKE_RESULT.md](DEC3_CURATED_SPIKE_RESULT.md) and
[DEC4_SPIKE_ONOFF_RESULT.md](DEC4_SPIKE_ONOFF_RESULT.md).
