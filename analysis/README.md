# Analysis Code And Outputs

This folder contains the runnable analysis code and generated working outputs for
the Dec 3 and Dec 4 haptic electrophysiology sessions.

Use this folder for **how the analyses were run**. Use the root
[`README.md`](../README.md), [`CONCLUSIONS.md`](../CONCLUSIONS.md), and the
supervisor summaries for **what the results mean**.

## What Lives Here

- `*.py`: reusable and session-specific analysis scripts.
- `outputs/dec3/`: Dec 3 working outputs, reports, tables, and intermediate figures.
- `outputs/dec4/`: Dec 4 working outputs, reports, tables, and intermediate figures.
- `outputs/cross_dataset_spike_compare/`: analyses that combine Dec 3 and Dec 4.
- `envs/`, `modal_*.py`, `stage_*_for_modal.sh`: spike-sorting environment and
  Modal/GPU helpers.

Large raw files and large sorter arrays are intentionally not part of Git. The
tracked outputs here are small summaries, CSV/JSON metadata, HTML reports, and
normal-sized figures.

## Current Analysis Story

The current analysis is complete through LFP, spike sorting, curation/merges,
baseline/post-study comparisons, drift checks, cell-type/ACG summaries, ripple
state summaries, the Dec 4 LEC slow-oscillation screen, and Dec 4 50 Hz
artifact/coordination controls.

Presentation-safe interpretation:

- Dec 3: clear dHPC LFP response, especially around 26 Hz conditions, but no
  curated single-unit ON/OFF firing-rate effect at 5/26 Hz.
- Dec 4: dHPC again shows no clean frequency-following evidence; LEC has an
  artifact-suspect 50 Hz LFP peak; the cleanest neural result is the curated
  50 Hz single-unit firing-rate modulation in both regions.
- True stimulus-phase entrainment was not directly testable because the delivered
  vibration phase was not recorded.

## Start Here

These are not all the same kind of file, so keep them separate:

### Final Interpretation Docs

- Overall conclusion: [`../CONCLUSIONS.md`](../CONCLUSIONS.md)
- Dec 3 supervisor summary: [`../docs/DEC3_SUPERVISOR_SUMMARY.md`](../docs/DEC3_SUPERVISOR_SUMMARY.md)
- Dec 4 supervisor summary: [`../docs/DEC4_SUPERVISOR_SUMMARY.md`](../docs/DEC4_SUPERVISOR_SUMMARY.md)
- Dec 3 curated spike result: [`../docs/DEC3_CURATED_SPIKE_RESULT.md`](../docs/DEC3_CURATED_SPIKE_RESULT.md)
- Dec 4 spike result: [`../docs/DEC4_SPIKE_ONOFF_RESULT.md`](../docs/DEC4_SPIKE_ONOFF_RESULT.md)
- Dec 4 50 Hz artifact check: [`../docs/DEC4_50HZ_ARTIFACT_CHECK.md`](../docs/DEC4_50HZ_ARTIFACT_CHECK.md)

### Curated Figure Indexes

- Dec 3 curated figures: [`../results/dec3/README.md`](../results/dec3/README.md)
- Dec 4 curated figures: [`../results/dec4/README.md`](../results/dec4/README.md)

These are the best places to browse figures on GitHub because the curated
`results/` folders are smaller and presentation-oriented.

### Generated Analysis Dashboards

- Dec 3 working dashboard: [`outputs/dec3/RESULTS_DASHBOARD.html`](outputs/dec3/RESULTS_DASHBOARD.html)
- Dec 4 working dashboard: [`outputs/dec4/RESULTS_DASHBOARD.html`](outputs/dec4/RESULTS_DASHBOARD.html)

These HTML dashboards are generated working reports. They are useful locally, but
GitHub may show the HTML source instead of rendering an interactive dashboard.

### Key Generated Figures

- Dec 3 whole-story figure: [`../results/dec3/10_Biological_Summary/combined_explainer.png`](../results/dec3/10_Biological_Summary/combined_explainer.png)
- Dec 4 whole-story figure: [`../results/dec4/10_Biological_Summary/combined_explainer.png`](../results/dec4/10_Biological_Summary/combined_explainer.png)
- Cross-dataset spike ON/OFF figure: [`../results/dec4/11_Spikes/spike_onoff_cross_dataset.png`](../results/dec4/11_Spikes/spike_onoff_cross_dataset.png)
- Dec 4 50 Hz artifact figure: [`../results/dec4/12_ChannelQC_Traces/50hz_artifact_check.png`](../results/dec4/12_ChannelQC_Traces/50hz_artifact_check.png)
- Drift-corrected spike model: [`../results/dec4/11_Spikes/drift_corrected_model.png`](../results/dec4/11_Spikes/drift_corrected_model.png)

### Supporting State Analyses

These are important follow-up writeups, but they are not the main output entry
points:

- [`../docs/DEC_BASELINE_POSTSTUDY_STATES.md`](../docs/DEC_BASELINE_POSTSTUDY_STATES.md)
- [`../docs/DEC_DRIFT_CORRECTED_MODEL.md`](../docs/DEC_DRIFT_CORRECTED_MODEL.md)
- [`../docs/DEC_LFP_APERIODIC_STATES.md`](../docs/DEC_LFP_APERIODIC_STATES.md)
- [`../docs/DEC_LFP_BANDPOWER_STATES.md`](../docs/DEC_LFP_BANDPOWER_STATES.md)
- [`../docs/DEC_RIPPLE_STATES.md`](../docs/DEC_RIPPLE_STATES.md)
- [`../docs/DEC4_LEC_SLOW_OSCILLATION_SCREEN.md`](../docs/DEC4_LEC_SLOW_OSCILLATION_SCREEN.md)

## Pipeline Map

These are the script families, in the order they matter for reruns.

### 1. Session Timing And Trial Tables

- Dec 3: `intan_haptic_summary.py`, `ttl_on_off_audit_dec3.py`,
  `plot_ttl_lfp_overview_dec3.py`
- Dec 4: `intan_haptic_summary_dec4.py`

Important outputs:

- `outputs/dec3/dec3_condition_sequence.csv`
- `outputs/dec4/dec4_condition_sequence.csv`
- `outputs/*/spike_sorting_prep/trial_windows.csv`

The schedule-derived condition sequence is the source of truth for ON/OFF trial
windows. Dec 3 TTL files are QC for delivery/timing. Dec 4 has no shared TTL or
stimulus waveform, so timing comes from `derive_offset_from_log(...)` in
`intan_haptic_summary_dec4.py` plus `add_recording_times(...)` in
`intan_haptic_summary.py`. Those functions write the shared
`recording_start_time_s` / `recording_end_time_s` timing columns used by later
LFP, spike, PETH, and state analyses.

### 2. Channel QC And LFP Extraction

- `channel_qc.py`
- `channel_qc_perprobe_dec4.py`
- `channel_qc_posthoc_dec4.py`
- `extract_lfp.py`

The Dec 4 LEC probe is noisier than dHPC, so Dec 4 QC is handled per probe.

### 3. LFP Analyses

Core LFP scripts:

- `event_aligned_lfp.py`
- `artifact_aware_lfp.py`
- `frequency_lfp.py`
- `time_frequency_lfp.py`
- `phase_locking_lfp.py`
- `reference_sensitivity_lfp.py`
- `trial_level_stats_dec3.py`
- `off_control_broadband_dec3.py`
- `broadband_transition_stats_dec3.py`
- `adaptation_analysis_dec3.py`
- `run_dec4_lfp_pipeline.py`
- `spectral_slope_itpc_dec4.py`

Cross-session/state LFP scripts:

- `lfp_aperiodic_states_dec.py`
- `lfp_bandpower_states_dec.py`
- `adaptation_states_dec.py`
- `drift_corrected_model_dec.py`
- `lec_slow_oscillation_screen_dec4.py`

Interpretation rule: broadband LFP response, driven-frequency power, 1/f residuals,
and phase consistency are different evidence levels. Do not treat a broadband
response as proof that the brain is oscillating at the drive frequency.

### 4. Spike Sorting, Curation, And PETHs

Prep and sorting:

- `prepare_spike_sorting_dec3.py`
- `build_dec4_spike_prep.py`
- `setup_spikeinterface_dec3.py`
- `run_spikeinterface_test_sort_dec3.py`
- `stage_dec3_for_modal.sh`, `stage_dec4_for_modal.sh`
- `modal_kilosort_dec3.py`, `modal_kilosort_dec4.py`

Post-sort analysis:

- `cluster_quality_dec3.py`
- `cluster_merge_candidates_dec3.py`
- `propose_curation.py`
- `apply_cluster_merges.py`
- `spike_peth_on_off_dec3.py`
- `spike_peth_high_confidence_dec3.py`
- `spike_peth_curated_dec3.py`
- `spike_curated_compare_dec.py`
- `spike_baseline_poststudy_compare_dec.py`
- `spike_celltype_classify_dec.py`
- `spike_acg_type_classify_dec.py`

Pynapple bridge:

- `export_pynapple_dec3.py`
- `export_kilosort_pynapple_dec3.py`

The early Kilosort/PETH folders are useful triage views. Final presentation claims
should use the curated/merged spike outputs and the linked docs above.

### 5. Dec 4 50 Hz Artifact And Coordination Checks

- `artifact_check_50hz_dec4.py`
- `deep_diag_50hz_dec4.py`
- `verify_50hz_gradient_dhpc_vs_lec.py`
- `spike_field_coordination_dec4.py`
- `plot_artifact_check_50hz.py`
- `plot_coordination_50hz.py`

These scripts are why the LEC 50 Hz LFP is treated cautiously: it is a real
measured narrowband peak, but disconnected electrodes and near-zero cross-region
lag show pickup contamination. The spike firing-rate result is the cleaner neural
readout.

### 6. Results Folder Builders

- `build_results_folder.py`
- `build_dec4_results.py`
- `plot_biological_summary_dec3.py`
- `build_dec4_interpretation.py`

These copy curated, presentation-sized outputs into `../results/dec3/` and
`../results/dec4/`.

## Rerunning

For a full checklist, use [`../docs/RERUN_PIPELINE.md`](../docs/RERUN_PIPELINE.md).

For a quick orientation:

```bash
# Dec 3 timing/QC
python analysis/intan_haptic_summary.py \
  --session-dir "Haptic_Stim_session1_251203_143031" \
  --config "Haptic_Stim_session1_251203_143031/My log/cmd_config_1_Dec3rd.json" \
  --recording-start-offset-s 640 \
  --output-dir analysis/outputs/dec3

# Dec 4 timing/QC
python analysis/intan_haptic_summary_dec4.py \
  --session-dir "Haptic_Stim_session2_251204_131403" \
  --config "Haptic_Stim_session2_251204_131403/My log/cmd_config_1_Dec4th_randomized_all.json" \
  --log "Haptic_Stim_session2_251204_131403/My log/log" \
  --output-dir analysis/outputs/dec4
```

Run from the repository root so relative paths resolve correctly.

## What To Ignore For Final Claims

- `outputs/*/spike_peth_on_off*/`: initial Kilosort ON/OFF triage, not final
  curated biology.
- `outputs/*/cluster_quality*/`: automated review triage, not cell-type or anatomy
  proof.
- `outputs/dec3/provisional_final_pass/`: historical Dec 3 pass retained for audit.
- Any figure based on onset-aligned PLV/ITPC alone: useful as a limitation check,
  but not a true entrainment test without recorded stimulus phase.

When in doubt, use `../CONCLUSIONS.md` and the supervisor summaries as the
presentation source of truth.
