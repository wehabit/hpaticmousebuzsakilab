# Results - dec3 haptic analysis

**Curated, de-duplicated set of every result figure for this session**, grouped by analysis type.
Each figure here is the canonical copy; the raw per-step working files under
`analysis/outputs/dec3/<step>/` are inputs the scripts read from (not duplicates to browse).
Rebuild with `python analysis/build_results_folder.py --session dec3`.

## Headline figures (start here)
- [combined_explainer.png](10_Biological_Summary/combined_explainer.png) - the whole story in one figure: strongest broadband/recovery response at 26 Hz / 180, weak driven-frequency evidence
- [session_timeline.png](01_Session_Timeline/session_timeline.png) - the session at a glance: baseline / stimulation / post
- [condition_by_channel_lfp_response_heatmap.png](04_EventAligned_LFP/condition_by_channel_lfp_response_heatmap.png) - which condition & channels respond (26 Hz / 180 strongest)
- [spectral_slope_decomposition.png](05_Frequency_Spectral/spectral_slope_decomposition.png) - the response is a broadband shift, not a 5/26 Hz oscillation
- [phase_locking_null_floor.png](06_Phase_Locking/phase_locking_null_floor.png) - phase locking stays near the finite-trial floor, so this pass does not support strong entrainment
- [peth_onset_ks_good_units.png](11_Spikes/peth_onset_ks_good_units.png) - firing is flat ON vs OFF (provisional, pre-curation)

## All figures by category

### 01_Session_Timeline
_Session at a glance: baseline -> stimulation -> post, with the accelerometer TTL and LFP._

- [session_timeline.png](01_Session_Timeline/session_timeline.png)
- [ttl_lfp_context_and_trials.png](01_Session_Timeline/ttl_lfp_context_and_trials.png)

### 02_TTL_Alignment
_Accelerometer-TTL vs commanded ON time: alignment, per-trial onset, and ON/OFF edge counts._

- [ttl_on_alignment_per_trial.png](02_TTL_Alignment/ttl_on_alignment_per_trial.png)
- [accelerometer_active_threshold_examples.png](02_TTL_Alignment/accelerometer_active_threshold_examples.png)
- [ttl_on_off_counts.png](02_TTL_Alignment/ttl_on_off_counts.png)

### 03_Movement_DataCleaning
_Movement proxy (EMG-from-LFP) and the data-cleaning sensitivity check._

- [movement_raw.png](03_Movement_DataCleaning/movement_raw.png)
- [movement_emg.png](03_Movement_DataCleaning/movement_emg.png)
- [excluded_vs_kept_examples.png](03_Movement_DataCleaning/excluded_vs_kept_examples.png)
- [movement_sensitivity.png](03_Movement_DataCleaning/movement_sensitivity.png)

### 04_EventAligned_LFP
_Event-aligned broadband LFP per condition, by channel and by shank (200 trials)._

- [condition_average_lfp_collapsed.png](04_EventAligned_LFP/condition_average_lfp_collapsed.png)
- [condition_by_channel_lfp_response_heatmap.png](04_EventAligned_LFP/condition_by_channel_lfp_response_heatmap.png)
- [lfp_by_shank_conditions.png](04_EventAligned_LFP/lfp_by_shank_conditions.png)
- [lfp_condition_envelopes.png](04_EventAligned_LFP/lfp_condition_envelopes.png)
- [lfp_condition_panels_by_shank.png](04_EventAligned_LFP/lfp_condition_panels_by_shank.png)
- [lfp_condition_shank_heatmap_values.png](04_EventAligned_LFP/lfp_condition_shank_heatmap_values.png)
- [lfp_frequency_difference_by_shank.png](04_EventAligned_LFP/lfp_frequency_difference_by_shank.png)
- [lfp_response_grouped_bars.png](04_EventAligned_LFP/lfp_response_grouped_bars.png)
- [artifact_window_comparison.png](04_EventAligned_LFP/artifact_window_comparison.png)
- [sustained_response_by_shank.png](04_EventAligned_LFP/sustained_response_by_shank.png)

### 05_Frequency_Spectral
_Power at the driven 5/26 Hz frequency, frequency specificity, and the 1/f spectral-slope test._

- [driven_power_change_by_analysis_group.png](05_Frequency_Spectral/driven_power_change_by_analysis_group.png)
- [driven_power_change_by_channel.png](05_Frequency_Spectral/driven_power_change_by_channel.png)
- [driven_power_change_by_physical_shank.png](05_Frequency_Spectral/driven_power_change_by_physical_shank.png)
- [frequency_specificity_by_group.png](05_Frequency_Spectral/frequency_specificity_by_group.png)
- [driven_frequency_timecourses.png](05_Frequency_Spectral/driven_frequency_timecourses.png)
- [time_frequency_condition_grid.png](05_Frequency_Spectral/time_frequency_condition_grid.png)
- [spectral_slope_decomposition.png](05_Frequency_Spectral/spectral_slope_decomposition.png)
- [dec3_aperiodic_states.png](05_Frequency_Spectral/dec3_aperiodic_states.png)
- [dec3_bump_vs_broadshift.png](05_Frequency_Spectral/dec3_bump_vs_broadshift.png)
- [state_spectra_loglog.png](05_Frequency_Spectral/state_spectra_loglog.png)
- [bandpower_general_states.png](05_Frequency_Spectral/bandpower_general_states.png)
- [bandpower_driven_states.png](05_Frequency_Spectral/bandpower_driven_states.png)

### 06_Phase_Locking
_Phase locking (PLV/ITPC) against chance, incl. the null-floor and onset-jitter checks._

- [plv_condition_summary.png](06_Phase_Locking/plv_condition_summary.png)
- [plv_sustained_minus_pre.png](06_Phase_Locking/plv_sustained_minus_pre.png)
- [plv_timecourses.png](06_Phase_Locking/plv_timecourses.png)
- [A_itpc_onset_vs_grid.png](06_Phase_Locking/A_itpc_onset_vs_grid.png)
- [phase_locking_null_floor.png](06_Phase_Locking/phase_locking_null_floor.png)

### 07_Broadband_OFFcontrol_TrialStats
_Onset / sustained / offset broadband windows, OFF-control, and trial-level bootstrap CIs._

- [broadband_window_group_heatmaps.png](07_Broadband_OFFcontrol_TrialStats/broadband_window_group_heatmaps.png)
- [broadband_windows_condition_ci.png](07_Broadband_OFFcontrol_TrialStats/broadband_windows_condition_ci.png)
- [transition_index_condition.png](07_Broadband_OFFcontrol_TrialStats/transition_index_condition.png)
- [off_control_condition_ci.png](07_Broadband_OFFcontrol_TrialStats/off_control_condition_ci.png)
- [off_control_group_heatmaps.png](07_Broadband_OFFcontrol_TrialStats/off_control_group_heatmaps.png)
- [driven_power_ci.png](07_Broadband_OFFcontrol_TrialStats/driven_power_ci.png)
- [offset_broadband_ci.png](07_Broadband_OFFcontrol_TrialStats/offset_broadband_ci.png)
- [sustained_broadband_ci.png](07_Broadband_OFFcontrol_TrialStats/sustained_broadband_ci.png)
- [B_broadband_rms.png](07_Broadband_OFFcontrol_TrialStats/B_broadband_rms.png)

### 08_Adaptation
_How the response changes over the course of the trials._

- [adaptation_epoch_summary.png](08_Adaptation/adaptation_epoch_summary.png)
- [adaptation_slope_summary.png](08_Adaptation/adaptation_slope_summary.png)
- [adaptation_timecourses.png](08_Adaptation/adaptation_timecourses.png)
- [lfp_adaptation_driven.png](08_Adaptation/lfp_adaptation_driven.png)

### 09_Reference_Sensitivity
_Robustness of the LFP results to the referencing scheme._

- [reference_condition_summary.png](09_Reference_Sensitivity/reference_condition_summary.png)
- [reference_group_heatmaps.png](09_Reference_Sensitivity/reference_group_heatmaps.png)

### 10_Biological_Summary
_Plain-language summary: does the brain react, and does it follow the buzz frequency? (with 95% CIs)._

- [amplitude_frequency_matrix.png](10_Biological_Summary/amplitude_frequency_matrix.png)
- [broadband_vs_driven_power.png](10_Biological_Summary/broadband_vs_driven_power.png)
- [condition_fingerprint.png](10_Biological_Summary/condition_fingerprint.png)
- [combined_explainer.png](10_Biological_Summary/combined_explainer.png)
- [sustained_vs_offset_explained.png](10_Biological_Summary/sustained_vs_offset_explained.png)

### 11_Spikes
_Kilosort cluster quality, drift, and ON-vs-OFF firing (PETH). Provisional until Phy curation._

- [cluster_quality_label_counts.png](11_Spikes/cluster_quality_label_counts.png)
- [cluster_quality_scatter.png](11_Spikes/cluster_quality_scatter.png)
- [diagnostics.png](11_Spikes/diagnostics.png)
- [drift_amount.png](11_Spikes/drift_amount.png)
- [drift_scatter.png](11_Spikes/drift_scatter.png)
- [spike_positions.png](11_Spikes/spike_positions.png)
- [spikeinterface_trace_sanity.png](11_Spikes/spikeinterface_trace_sanity.png)
- [condition_mean_on_minus_off.png](11_Spikes/condition_mean_on_minus_off.png)
- [peth_onset_ks_good_units.png](11_Spikes/peth_onset_ks_good_units.png)
- [peth_offset_ks_good_units.png](11_Spikes/peth_offset_ks_good_units.png)
- [unit_condition_on_minus_off_heatmap_all_units.png](11_Spikes/unit_condition_on_minus_off_heatmap_all_units.png)
- [unit_condition_on_minus_off_heatmap_ks_good.png](11_Spikes/unit_condition_on_minus_off_heatmap_ks_good.png)
- [condition_mean_on_minus_off_unit_set_comparison.png](11_Spikes/condition_mean_on_minus_off_unit_set_comparison.png)
- [high_confidence_unit_condition_heatmap.png](11_Spikes/high_confidence_unit_condition_heatmap.png)
- [peth_onset_high_confidence_units.png](11_Spikes/peth_onset_high_confidence_units.png)
- [peth_offset_high_confidence_units.png](11_Spikes/peth_offset_high_confidence_units.png)
- [psth_dec3_null_control.png](11_Spikes/psth_dec3_null_control.png)
- [raster_psth_dec3_null.png](11_Spikes/raster_psth_dec3_null.png)
- [raster_psth_all_good_units_dec3.png](11_Spikes/raster_psth_all_good_units_dec3.png)
- [raster_psth_all_good_units_combined.png](11_Spikes/raster_psth_all_good_units_combined.png)
- [dec3_states_vs_baseline.png](11_Spikes/dec3_states_vs_baseline.png)
- [dec3_celltype.png](11_Spikes/dec3_celltype.png)
- [celltype_classification.png](11_Spikes/celltype_classification.png)
- [celltype_acg_examples.png](11_Spikes/celltype_acg_examples.png)
- [acg_type_classification_plane.png](11_Spikes/acg_type_classification_plane.png)
- [acg_type_fits.png](11_Spikes/acg_type_fits.png)
- [ripple_rate_by_state.png](11_Spikes/ripple_rate_by_state.png)
- [ripple_participation_by_celltype.png](11_Spikes/ripple_participation_by_celltype.png)
- [ripple_on_rate_by_stim_freq.png](11_Spikes/ripple_on_rate_by_stim_freq.png)
- [ripple_examples.png](11_Spikes/ripple_examples.png)

### 12_ChannelQC_Traces
_Per-channel noise QC plus raw/LFP trace-browsing pages._

- [channel_qc_metrics.png](12_ChannelQC_Traces/channel_qc_metrics.png)
- [channel_qc_baseline_channel_qc_metrics.png](12_ChannelQC_Traces/channel_qc_baseline_channel_qc_metrics.png)
- [high_noise_review_traces.png](12_ChannelQC_Traces/high_noise_review_traces.png)
- `raw_trace_pages/` - 12 trace-browsing pages
- `lfp_trace_pages/` - 8 trace-browsing pages

### 13_Teaching_and_Methods
_Teaching/methods explainers: how to read the results, the +/-100 ms margin, and the probe map._

- [LEARN_real_vs_dec3.png](13_Teaching_and_Methods/LEARN_real_vs_dec3.png)
- [LEARN_results_at_a_glance.png](13_Teaching_and_Methods/LEARN_results_at_a_glance.png)
- [margin_exclusion_test.png](13_Teaching_and_Methods/margin_exclusion_test.png)
- [trial_window_diagram.png](13_Teaching_and_Methods/trial_window_diagram.png)
- [supp_provisional_probe_map_H12_UNRESOLVED.png](13_Teaching_and_Methods/supp_provisional_probe_map_H12_UNRESOLVED.png)

---
_Not copied here (intentional):_
- REPORT/1-7_*  (mirror of ttl_lfp_overview + movement)
- provisional_final_pass/*  (mirror of phase_locking + reference_sensitivity)
