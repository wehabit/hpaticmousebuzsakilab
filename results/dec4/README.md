# Results - dec4 haptic analysis (two probes: dHPC + LEC, freqs 5/10/26/50)

Same mouse/probes as Dec 3, now with a second probe (LEC) and four drive
frequencies. Curated, de-duplicated figures grouped by analysis type. Rebuild with
`python analysis/build_dec4_results.py`.

## Headline figures (start here)
- [combined_explainer.png](10_Biological_Summary/combined_explainer.png) - the whole Dec 4 story: dHPC follows no frequency (same probe as Dec 3); LEC shows induced 50 Hz power that grows with amplitude but is not phase-locked
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
_SpikeInterface raw-trace sanity check (256 ch). Full Kilosort/PETH = Modal/GPU next step._

- [spikeinterface_trace_sanity.png](11_Spikes/spikeinterface_trace_sanity.png)

### 12_ChannelQC_Traces
_Per-channel noise QC (pooled view; per-probe bad lists are in analysis/bad_channels_dec4.json)._

- [channel_qc_metrics.png](12_ChannelQC_Traces/channel_qc_metrics.png)

### 13_Teaching_and_Methods
_Artifact-margin (+/-100 ms) robustness test, per probe._

- [margin_exclusion_test.png](13_Teaching_and_Methods/margin_exclusion_test.png)
- [LEC_amp250_freq50_margin_exclusion_test.png](13_Teaching_and_Methods/LEC_amp250_freq50_margin_exclusion_test.png)
