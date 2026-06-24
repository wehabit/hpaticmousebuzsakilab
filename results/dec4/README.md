# Results - dec4 haptic analysis (two probes: dHPC + LEC, freqs 5/10/26/50)

Same mouse/probes as Dec 3, now with a second probe (LEC) and four drive
frequencies. Curated, de-duplicated figures grouped by analysis type. Rebuild with
`python analysis/build_dec4_results.py`.

## Headline figures (start here)
- [combined_explainer.png](10_Biological_Summary/combined_explainer.png) - the whole Dec 4 story: dHPC follows no frequency (same probe as Dec 3); LEC shows induced 50 Hz power that grows with amplitude but is not phase-locked
- [spike_onoff_cross_dataset.png](11_Spikes/spike_onoff_cross_dataset.png) - the cleanest neural result: single-unit ON/OFF firing — Dec 3 null at 5/26 Hz, Dec 4 50 Hz/high-amp responders in BOTH dHPC and LEC
- [unit87_acg_artifact_screen.png](11_Spikes/unit87_acg_artifact_screen.png) - the soft-spot unit 87 passes the ACG + ISI artifact screens: its 50 Hz rate increase is a real neuron, not pickup
- [explainer_2_evidence.png](13_Teaching_and_Methods/explainer_2_evidence.png) - how we know the 50 Hz spike result is neural, not artifact: direction test + dose-response + the ACG resolution + the trust hierarchy
- [spectral_slope_itpc_dec4.png](05_Frequency_Spectral/spectral_slope_itpc_dec4.png) - entrainment test: a real narrowband 50 Hz peak above 1/f in LEC (amplitude-graded), but ITPC at chance
- [driven_power_change_by_analysis_group.png](05_Frequency_Spectral/driven_power_change_by_analysis_group.png) - driven-frequency power by probe-group across all 12 conditions
- [reference_condition_summary.png](09_Reference_Sensitivity/reference_condition_summary.png) - the 50 Hz LEC effect survives every reference scheme

## All figures by category

### 03_Movement_DataCleaning
_LFP-based movement proxy (no accelerometer this session) and the data-cleaning robustness check._

- [movement_raw.png](03_Movement_DataCleaning/movement_raw.png)
- [movement_sensitivity.png](03_Movement_DataCleaning/movement_sensitivity.png)

### 04_EventAligned_LFP
_Event-aligned broadband LFP per condition, by channel and by probe (Port A dHPC, Port B LEC)._

- [condition_average_lfp_collapsed.png](04_EventAligned_LFP/condition_average_lfp_collapsed.png)
- [condition_by_channel_lfp_response_heatmap.png](04_EventAligned_LFP/condition_by_channel_lfp_response_heatmap.png)
- [artifact_window_comparison.png](04_EventAligned_LFP/artifact_window_comparison.png)
- [sustained_response_by_shank.png](04_EventAligned_LFP/sustained_response_by_shank.png)

### 05_Frequency_Spectral
_Power at the driven 5/10/26/50 Hz frequency, frequency specificity, time-frequency, and the 1/f + ITPC entrainment test._

- [driven_power_change_by_analysis_group.png](05_Frequency_Spectral/driven_power_change_by_analysis_group.png)
- [driven_power_change_by_channel.png](05_Frequency_Spectral/driven_power_change_by_channel.png)
- [driven_power_change_by_physical_shank.png](05_Frequency_Spectral/driven_power_change_by_physical_shank.png)
- [frequency_specificity_by_group.png](05_Frequency_Spectral/frequency_specificity_by_group.png)
- [driven_frequency_timecourses.png](05_Frequency_Spectral/driven_frequency_timecourses.png)
- [time_frequency_condition_grid.png](05_Frequency_Spectral/time_frequency_condition_grid.png)
- [spectral_slope_itpc_dec4.png](05_Frequency_Spectral/spectral_slope_itpc_dec4.png)
- [dec4_aperiodic_states.png](05_Frequency_Spectral/dec4_aperiodic_states.png)
- [dec4_bump_vs_broadshift.png](05_Frequency_Spectral/dec4_bump_vs_broadshift.png)
- [state_spectra_loglog.png](05_Frequency_Spectral/state_spectra_loglog.png)
- [bandpower_general_states.png](05_Frequency_Spectral/bandpower_general_states.png)
- [bandpower_driven_states.png](05_Frequency_Spectral/bandpower_driven_states.png)

### 06_Phase_Locking
_Phase locking (PLV/ITPC) per condition and probe vs the within-trial pre window._

- [plv_condition_summary.png](06_Phase_Locking/plv_condition_summary.png)
- [plv_sustained_minus_pre.png](06_Phase_Locking/plv_sustained_minus_pre.png)
- [plv_timecourses.png](06_Phase_Locking/plv_timecourses.png)

### 07_Broadband_OFFcontrol_TrialStats
_Onset/sustained/offset broadband windows, OFF-control, and trial-level bootstrap CIs._

- [broadband_window_group_heatmaps.png](07_Broadband_OFFcontrol_TrialStats/broadband_window_group_heatmaps.png)
- [broadband_windows_condition_ci.png](07_Broadband_OFFcontrol_TrialStats/broadband_windows_condition_ci.png)
- [transition_index_condition.png](07_Broadband_OFFcontrol_TrialStats/transition_index_condition.png)
- [off_control_condition_ci.png](07_Broadband_OFFcontrol_TrialStats/off_control_condition_ci.png)
- [off_control_group_heatmaps.png](07_Broadband_OFFcontrol_TrialStats/off_control_group_heatmaps.png)
- [driven_power_ci.png](07_Broadband_OFFcontrol_TrialStats/driven_power_ci.png)
- [offset_broadband_ci.png](07_Broadband_OFFcontrol_TrialStats/offset_broadband_ci.png)
- [sustained_broadband_ci.png](07_Broadband_OFFcontrol_TrialStats/sustained_broadband_ci.png)

### 08_Adaptation
_How the response changes over the 200 repeats (early/middle/late + slope)._

- [adaptation_epoch_summary.png](08_Adaptation/adaptation_epoch_summary.png)
- [adaptation_slope_summary.png](08_Adaptation/adaptation_slope_summary.png)
- [adaptation_timecourses.png](08_Adaptation/adaptation_timecourses.png)
- [spike_adaptation_50hz.png](08_Adaptation/spike_adaptation_50hz.png)
- [lfp_adaptation_driven.png](08_Adaptation/lfp_adaptation_driven.png)

### 09_Reference_Sensitivity
_Robustness of the driven-power result to the referencing scheme (raw / probe / group median)._

- [reference_condition_summary.png](09_Reference_Sensitivity/reference_condition_summary.png)
- [reference_group_heatmaps.png](09_Reference_Sensitivity/reference_group_heatmaps.png)

### 10_Biological_Summary
_Dec 4 in one figure: dHPC null at all frequencies; LEC induced, amplitude-graded 50 Hz power without phase locking._

- [combined_explainer.png](10_Biological_Summary/combined_explainer.png)
- [broadband_perchannel_ci.png](10_Biological_Summary/broadband_perchannel_ci.png)
- [sustained_vs_offset_explained.png](10_Biological_Summary/sustained_vs_offset_explained.png)
- [LEC_amp250_freq50_sustained_vs_offset_explained.png](10_Biological_Summary/LEC_amp250_freq50_sustained_vs_offset_explained.png)

### 11_Spikes
_Kilosort4 + curation done (15 good units/probe). Single-unit ON/OFF (50 Hz/high-amp responders in both regions), cross-region 50 Hz coordination, and the unit-87 ACG/ISI artifact screen. See docs/DEC4_SPIKE_ONOFF_RESULT.md, DEC4_COORDINATION_50HZ.md._

- [spikeinterface_trace_sanity.png](11_Spikes/spikeinterface_trace_sanity.png)
- [spike_onoff_cross_dataset.png](11_Spikes/spike_onoff_cross_dataset.png)
- [spike_50hz_interpretation.png](11_Spikes/spike_50hz_interpretation.png)
- [dHPC_condition_mean_on_minus_off.png](11_Spikes/dHPC_condition_mean_on_minus_off.png)
- [dHPC_unit_condition_heatmap.png](11_Spikes/dHPC_unit_condition_heatmap.png)
- [dHPC_peth_onset_good_units.png](11_Spikes/dHPC_peth_onset_good_units.png)
- [LEC_condition_mean_on_minus_off.png](11_Spikes/LEC_condition_mean_on_minus_off.png)
- [LEC_unit_condition_heatmap.png](11_Spikes/LEC_unit_condition_heatmap.png)
- [LEC_peth_onset_good_units.png](11_Spikes/LEC_peth_onset_good_units.png)
- [coordination_50hz_pooled.png](11_Spikes/coordination_50hz_pooled.png)
- [coordination_50hz_amp250.png](11_Spikes/coordination_50hz_amp250.png)
- [unit87_acg_artifact_screen.png](11_Spikes/unit87_acg_artifact_screen.png)
- [dec4_states_vs_baseline.png](11_Spikes/dec4_states_vs_baseline.png)
- [dec4_freq50_vs_baseline.png](11_Spikes/dec4_freq50_vs_baseline.png)
- [dec4_celltype.png](11_Spikes/dec4_celltype.png)
- [dec4_celltype_vs_50hz.png](11_Spikes/dec4_celltype_vs_50hz.png)
- [celltype_classification_pooled.png](11_Spikes/celltype_classification_pooled.png)
- [celltype_acg_examples.png](11_Spikes/celltype_acg_examples.png)
- [acg_type_classification_plane.png](11_Spikes/acg_type_classification_plane.png)
- [acg_type_fits.png](11_Spikes/acg_type_fits.png)
- [ripple_rate_by_state.png](11_Spikes/ripple_rate_by_state.png)
- [ripple_participation_by_celltype.png](11_Spikes/ripple_participation_by_celltype.png)
- [ripple_on_rate_by_stim_freq.png](11_Spikes/ripple_on_rate_by_stim_freq.png)
- [ripple_examples.png](11_Spikes/ripple_examples.png)
- [drift_corrected_model.png](11_Spikes/drift_corrected_model.png)

### 12_ChannelQC_Traces
_Per-channel noise QC (pooled view; per-probe bad lists in analysis/bad_channels_dec4.json). Plus the 50 Hz LFP artifact check: disconnected LEC electrodes pick up ~6x more 50 Hz than tissue; dHPC is much cleaner (LEC: 82 good / 45 disconnected-dead / 1 hot-excluded ch142)._

- [channel_qc_metrics.png](12_ChannelQC_Traces/channel_qc_metrics.png)
- [50hz_artifact_check.png](12_ChannelQC_Traces/50hz_artifact_check.png)
- [50hz_pickup_gradient_dhpc_vs_lec.png](12_ChannelQC_Traces/50hz_pickup_gradient_dhpc_vs_lec.png)

### 13_Teaching_and_Methods
_Artifact-margin robustness test, plus the 50 Hz 'is it pickup or neural?' explainers (contamination + evidence). See docs/DEC4_50HZ_ARTIFACT_CHECK.md._

- [margin_exclusion_test.png](13_Teaching_and_Methods/margin_exclusion_test.png)
- [LEC_amp250_freq50_margin_exclusion_test.png](13_Teaching_and_Methods/LEC_amp250_freq50_margin_exclusion_test.png)
- [explainer_1_contamination.png](13_Teaching_and_Methods/explainer_1_contamination.png)
- [explainer_2_evidence.png](13_Teaching_and_Methods/explainer_2_evidence.png)
