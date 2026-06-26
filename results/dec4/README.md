# Results - Dec 4 haptic analysis

Dec 4 contains the curated dHPC + LEC result figures for amplitudes
`{100, 180, 250}` x commanded frequencies `{5, 10, 26, 50}` Hz. These are the
de-duplicated figures meant for browsing, presentation planning, and supervisor review.
Rebuild with `python analysis/build_dec4_results.py`.

Every image currently in `results/dec4/` is indexed below. The curated Dec 4 tree starts
at `03_` because no standalone Dec 4 timeline or TTL-alignment PNG category is exported
here right now.

## Headline figures (start here)
- [combined_explainer.png](10_Biological_Summary/combined_explainer.png) - the whole Dec 4 story: dHPC has no clean LFP frequency-following peak; LEC shows induced 50 Hz power that grows with amplitude but is not phase-locked
- [spike_onoff_cross_dataset.png](11_Spikes/spike_onoff_cross_dataset.png) - the cleanest neural result: single-unit ON/OFF firing; Dec 3 is null at 5/26 Hz, while Dec 4 has 50 Hz/high-amplitude responders in both dHPC and LEC
- [unit87_acg_artifact_screen.png](11_Spikes/unit87_acg_artifact_screen.png) - the soft-spot unit 87 passes the ACG + ISI artifact screens: its 50 Hz rate increase is a real neuron, not pickup
- [explainer_2_evidence.png](13_Teaching_and_Methods/explainer_2_evidence.png) - how we know the 50 Hz spike result is neural, not artifact: direction test + dose-response + the ACG resolution + the trust hierarchy
- [spectral_slope_itpc_dec4.png](05_Frequency_Spectral/spectral_slope_itpc_dec4.png) - LFP rhythm-control panel: a real narrowband 50 Hz peak above 1/f in LEC (amplitude-graded), but ITPC is near chance, so this is not proof of entrainment
- [driven_power_change_by_analysis_group.png](05_Frequency_Spectral/driven_power_change_by_analysis_group.png) - driven-frequency power by probe-group across all 12 conditions
- [reference_condition_summary.png](09_Reference_Sensitivity/reference_condition_summary.png) - the 50 Hz LEC effect survives every reference scheme

## Category map

| Folder | Images | What this category is for |
|---|---:|---|
| `03_Movement_DataCleaning` | 2 | LFP-based movement proxy and robustness to movement/data cleaning. |
| `04_EventAligned_LFP` | 5 | Time-domain LFP examples and average LFP around stimulation onset/offset, by condition, channel, probe, and section/group. |
| `05_Frequency_Spectral` | 14 | Driven-frequency power, spectrograms, 1/f slope, bandpower states, and LFP frequency specificity. |
| `06_Phase_Locking` | 3 | Onset-aligned PLV/ITPC summaries. Useful as a weak timing-control, not a real vibration-phase test. |
| `07_Broadband_OFFcontrol_TrialStats` | 8 | Broadband ON/OFF/recovery windows, OFF controls, and trial-level confidence intervals. |
| `08_Adaptation` | 5 | Early/middle/late and slope analyses for LFP and 50 Hz spike effects. |
| `09_Reference_Sensitivity` | 2 | Whether the LEC 50 Hz LFP result survives different reference schemes. |
| `10_Biological_Summary` | 4 | Presentation-style summary figures and sustained-vs-offset explainers. |
| `11_Spikes` | 32 | Kilosort/curated single-unit results, raster/PSTH views, spike timing controls, cell type, ripples, and drift. |
| `12_ChannelQC_Traces` | 6 | Channel QC, 50 Hz pickup/artifact checks, and LEC slow-oscillation/UP-DOWN-state screens. |
| `13_Teaching_and_Methods` | 4 | Teaching panels and artifact-margin robustness explainers. |

## All figures by category

### 03_Movement_DataCleaning
_LFP-based movement proxy (no accelerometer this session) and the data-cleaning robustness check._

- [movement_raw.png](03_Movement_DataCleaning/movement_raw.png)
- [movement_sensitivity.png](03_Movement_DataCleaning/movement_sensitivity.png)

### 04_EventAligned_LFP
_Time-domain/event-aligned broadband LFP per condition, by channel, probe, and verified section/group. Legacy filenames that say `shank` here are section/group summaries, not strong anatomical claims._

- [raw_lfp_time_domain_examples_dec4.png](04_EventAligned_LFP/raw_lfp_time_domain_examples_dec4.png) - representative time-domain LFP traces before the spectral summaries
- [condition_average_lfp_collapsed.png](04_EventAligned_LFP/condition_average_lfp_collapsed.png)
- [condition_by_channel_lfp_response_heatmap.png](04_EventAligned_LFP/condition_by_channel_lfp_response_heatmap.png)
- [artifact_window_comparison.png](04_EventAligned_LFP/artifact_window_comparison.png)
- [sustained_response_by_shank.png](04_EventAligned_LFP/sustained_response_by_shank.png) - sustained response by verified section/group; legacy filename

### 05_Frequency_Spectral
_Power at the driven 5/10/26/50 Hz frequency, frequency specificity, time-frequency, state spectra, 1/f slope, and ITPC controls. The LEC 50 Hz peak is a real LFP frequency-specific response, but not proof of entrainment._

- [driven_power_change_by_analysis_group.png](05_Frequency_Spectral/driven_power_change_by_analysis_group.png)
- [driven_power_change_by_channel.png](05_Frequency_Spectral/driven_power_change_by_channel.png)
- [driven_power_change_by_physical_shank.png](05_Frequency_Spectral/driven_power_change_by_physical_shank.png) - verified section/group summary; legacy filename
- [frequency_specificity_by_group.png](05_Frequency_Spectral/frequency_specificity_by_group.png)
- [driven_frequency_timecourses.png](05_Frequency_Spectral/driven_frequency_timecourses.png)
- [time_frequency_condition_grid.png](05_Frequency_Spectral/time_frequency_condition_grid.png)
- [spectral_slope_itpc_dec4.png](05_Frequency_Spectral/spectral_slope_itpc_dec4.png)
- [dec4_aperiodic_states.png](05_Frequency_Spectral/dec4_aperiodic_states.png)
- [dec4_bump_vs_broadshift.png](05_Frequency_Spectral/dec4_bump_vs_broadshift.png)
- [state_spectra_loglog.png](05_Frequency_Spectral/state_spectra_loglog.png)
- [bandpower_general_states.png](05_Frequency_Spectral/bandpower_general_states.png)
- [bandpower_driven_states.png](05_Frequency_Spectral/bandpower_driven_states.png)
- [trial_avg_spectrogram_dec4.png](05_Frequency_Spectral/trial_avg_spectrogram_dec4.png)
- [trial_avg_spectrogram_dec3_dec4_freq5_26.png](05_Frequency_Spectral/trial_avg_spectrogram_dec3_dec4_freq5_26.png)

### 06_Phase_Locking
_Phase locking (PLV/ITPC) per condition and probe vs the within-trial pre window. Because the continuous vibration waveform was not recorded, this is onset-aligned timing evidence, not a definitive per-cycle entrainment test._

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
_How the response changes over the 200 repeats per condition (early/middle/late + slope)._

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
_Dec 4 in one figure: dHPC LFP lacks a clean driven-band elevation; LEC has induced, amplitude-graded 50 Hz power without phase locking._

- [combined_explainer.png](10_Biological_Summary/combined_explainer.png)
- [broadband_perchannel_ci.png](10_Biological_Summary/broadband_perchannel_ci.png)
- [sustained_vs_offset_explained.png](10_Biological_Summary/sustained_vs_offset_explained.png)
- [LEC_amp250_freq50_sustained_vs_offset_explained.png](10_Biological_Summary/LEC_amp250_freq50_sustained_vs_offset_explained.png)

### 11_Spikes
_Kilosort4 + curation done (15 good units/probe). This category includes single-unit ON/OFF results, curated raster/PSTH views, 50 Hz spike-timing controls, cell-type/ACG summaries, ripple analyses, cross-region 50 Hz coordination, baseline/post drift checks, and the unit-87 ACG/ISI artifact screen. Older initial Kilosort-label onset PETHs remain audit-only in `analysis/outputs/dec4/spike_peth_on_off_*`. See docs/DEC4_SPIKE_ONOFF_RESULT.md, DEC4_COORDINATION_50HZ.md._

- [spikeinterface_trace_sanity.png](11_Spikes/spikeinterface_trace_sanity.png)
- [spike_onoff_cross_dataset.png](11_Spikes/spike_onoff_cross_dataset.png)
- [spike_50hz_interpretation.png](11_Spikes/spike_50hz_interpretation.png)
- [dHPC_condition_mean_on_minus_off.png](11_Spikes/dHPC_condition_mean_on_minus_off.png)
- [dHPC_unit_condition_heatmap.png](11_Spikes/dHPC_unit_condition_heatmap.png)
- [LEC_condition_mean_on_minus_off.png](11_Spikes/LEC_condition_mean_on_minus_off.png)
- [LEC_unit_condition_heatmap.png](11_Spikes/LEC_unit_condition_heatmap.png)
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
- [ripple_localization_by_shank.png](11_Spikes/ripple_localization_by_shank.png) - dHPC ripple-band localization by verified section/depth
- [drift_corrected_model.png](11_Spikes/drift_corrected_model.png)
- [raster_psth_examples_dec4.png](11_Spikes/raster_psth_examples_dec4.png)
- [raster_psth_all_good_units_dec4.png](11_Spikes/raster_psth_all_good_units_dec4.png)
- [raster_psth_all_good_units_combined.png](11_Spikes/raster_psth_all_good_units_combined.png)
- [psth_population_modulated_dec4.png](11_Spikes/psth_population_modulated_dec4.png)
- [psth_frequency_specific_dec4.png](11_Spikes/psth_frequency_specific_dec4.png)
- [raster_frequency_specific_dec4.png](11_Spikes/raster_frequency_specific_dec4.png)
- [acg_50hz_following_dec4.png](11_Spikes/acg_50hz_following_dec4.png)
- [unit_by_shank_dec4.png](11_Spikes/unit_by_shank_dec4.png) - curated units by verified section/depth

### 12_ChannelQC_Traces
_Per-channel noise QC (pooled view; per-probe bad lists in analysis/bad_channels_dec4.json). This also includes the 50 Hz LFP artifact check and LEC cortex-support screens: disconnected LEC electrodes pick up ~6x more 50 Hz than tissue; dHPC is much cleaner (LEC: 82 good / 45 disconnected-dead / 1 hot-excluded ch142)._

- [channel_qc_metrics.png](12_ChannelQC_Traces/channel_qc_metrics.png)
- [50hz_artifact_check.png](12_ChannelQC_Traces/50hz_artifact_check.png)
- [50hz_pickup_gradient_dhpc_vs_lec.png](12_ChannelQC_Traces/50hz_pickup_gradient_dhpc_vs_lec.png)
- [fiftyhz_by_shank_dec4.png](12_ChannelQC_Traces/fiftyhz_by_shank_dec4.png) - 50 Hz pickup by verified XML group/section; legacy filename
- [lec_updown_states_dec4.png](12_ChannelQC_Traces/lec_updown_states_dec4.png)
- [lec_slow_oscillation_screen_dec4.png](12_ChannelQC_Traces/lec_slow_oscillation_screen_dec4.png)

### 13_Teaching_and_Methods
_Artifact-margin robustness test, plus the 50 Hz 'is it pickup or neural?' explainers (contamination + evidence). See docs/DEC4_50HZ_ARTIFACT_CHECK.md._

- [margin_exclusion_test.png](13_Teaching_and_Methods/margin_exclusion_test.png)
- [LEC_amp250_freq50_margin_exclusion_test.png](13_Teaching_and_Methods/LEC_amp250_freq50_margin_exclusion_test.png)
- [explainer_1_contamination.png](13_Teaching_and_Methods/explainer_1_contamination.png)
- [explainer_2_evidence.png](13_Teaching_and_Methods/explainer_2_evidence.png)
