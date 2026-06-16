# Dec 3 Image Walkthrough

This is a learning guide for the Dec 3 figures. Each entry answers two
questions:

- **How it was generated:** what data went into the image and what calculation
  was done.
- **Takeaway:** what you should learn from the image, and what not to overclaim.

The big idea: most figures come from cutting the recording into repeated
trial windows around stimulation, then comparing the 3 s ON period with the
nearby 3 s OFF period, baseline/pre windows, or later recovery windows.

## A. Validation: TTL, Timeline, Movement

Use these first. They check whether the experiment timing and trial definitions
are trustworthy before interpreting biology.

### Timeline And TTL Figures

- [1_session_timeline.png](../analysis/outputs/dec3/REPORT/1_session_timeline.png) and
  [ttl_lfp_overview/session_timeline.png](../analysis/outputs/dec3/ttl_lfp_overview/session_timeline.png)

  **How it was generated:** the script parses the recording timeline, the
  accelerometer/digital TTL signal, and a downsampled LFP summary. It overlays
  the intended baseline, stimulation, and post-stimulation epochs.

  **Takeaway:** the session structure is coherent: baseline comes first, the
  stimulation block occurs in the expected middle window, and the recording
  continues afterward. This is the "do we trust the clock?" figure.

- [2_ttl_lfp_context_and_trials.png](../analysis/outputs/dec3/REPORT/2_ttl_lfp_context_and_trials.png) and
  [ttl_lfp_overview/ttl_lfp_context_and_trials.png](../analysis/outputs/dec3/ttl_lfp_overview/ttl_lfp_context_and_trials.png)

  **How it was generated:** this combines a broad session view with trial-level
  zooms. It plots TTL activity near selected trials together with LFP context.

  **Takeaway:** the 3 s ON / 3 s OFF rhythm is visible and the trial windows
  are aligned to real stimulation delivery. This supports using those windows
  for LFP and spike analyses.

- [3_ttl_on_alignment_per_trial.png](../analysis/outputs/dec3/REPORT/3_ttl_on_alignment_per_trial.png) and
  [ttl_lfp_overview/ttl_on_alignment_per_trial.png](../analysis/outputs/dec3/ttl_lfp_overview/ttl_on_alignment_per_trial.png)

  **How it was generated:** for each trial, the first accelerometer TTL edge is
  compared with the commanded ON start time.

  **Takeaway:** the accelerometer TTL confirms physical vibration delivery, but
  it is not the same thing as the command clock. Most trials have TTL activity
  inside the intended ON window, with a delivery lag. We should align biological
  responses carefully and not pretend the physical vibration starts at exactly
  time zero.

- [4_accelerometer_active_threshold_examples.png](../analysis/outputs/dec3/REPORT/4_accelerometer_active_threshold_examples.png) and
  [ttl_lfp_overview/accelerometer_active_threshold_examples.png](../analysis/outputs/dec3/ttl_lfp_overview/accelerometer_active_threshold_examples.png)

  **How it was generated:** the accelerometer/TTL-like signal is thresholded to
  identify when the device is physically active.

  **Takeaway:** this validates the practical threshold used to mark vibration
  delivery. It is a methods/QC figure, not a biological result.

- [ttl_on_off_audit/ttl_on_off_counts.png](../analysis/outputs/dec3/ttl_on_off_audit/ttl_on_off_counts.png)

  **How it was generated:** trial windows are counted and ON/OFF durations are
  summarized from the TTL-derived schedule.

  **Takeaway:** confirms the expected experimental structure: repeated ON/OFF
  events with the intended 3 s / 3 s timing. If this looked wrong, every later
  result would be suspect.

### Movement Proxy Figures

Important: there is no clean independent EMG channel in this analysis pass. The
"movement" measure is an LFP-derived high-frequency proxy, mainly read from OFF
windows so that the vibration itself does not dominate the measurement.

- [5_movement_proxy_raw.png](../analysis/outputs/dec3/REPORT/5_movement_proxy_raw.png) and
  [movement/movement_raw.png](../analysis/outputs/dec3/movement/movement_raw.png)

  **How it was generated:** high-frequency activity across LFP channels is
  summarized per trial/window as a movement-like proxy.

  **Takeaway:** some trials contain large high-frequency bursts consistent with
  movement-like contamination. This is a proxy, not direct behavioral video or
  EMG.

- [movement/movement_emg.png](../analysis/outputs/dec3/movement/movement_emg.png)

  **How it was generated:** the same high-frequency proxy is displayed in a
  way that resembles an EMG-style summary.

  **Takeaway:** useful for detecting high-frequency contamination, but should
  not be called real EMG unless a true EMG channel is confirmed.

- [6_excluded_vs_kept_examples.png](../analysis/outputs/dec3/REPORT/6_excluded_vs_kept_examples.png) and
  [movement/excluded_vs_kept_examples.png](../analysis/outputs/dec3/movement/excluded_vs_kept_examples.png)

  **How it was generated:** example trials flagged by the movement proxy are
  plotted beside trials that were kept.

  **Takeaway:** excluded trials show large, synchronized high-frequency bursts.
  This makes the exclusion rule visually understandable.

- [7_movement_sensitivity.png](../analysis/outputs/dec3/REPORT/7_movement_sensitivity.png) and
  [movement/movement_sensitivity.png](../analysis/outputs/dec3/movement/movement_sensitivity.png)

  **How it was generated:** headline LFP/spike results are recomputed after
  excluding movement-flagged trials.

  **Takeaway:** the main LFP interpretation is not only caused by those
  movement-flagged trials. This is a robustness check.

- [supp_movement_proxy_lfp_preliminary.png](../analysis/outputs/dec3/REPORT/supp_movement_proxy_lfp_preliminary.png)

  **How it was generated:** an earlier/preliminary LFP-based movement proxy
  visualization.

  **Takeaway:** useful for documenting how we thought about movement, but use
  the later movement figures above for presentation.

## B. Event-Aligned LFP: Broadband Response

These figures ask: after stimulation starts, does the LFP waveform or total LFP
amplitude change by condition?

- [condition_average_lfp_collapsed.png](../analysis/outputs/dec3/event_aligned_lfp/condition_average_lfp_collapsed.png)

  **How it was generated:** LFP traces were cut around each trial, grouped by
  condition, averaged across trials, and collapsed across channels/groups.

  **Takeaway:** this is a broad first look. The condition traces overlap, so it
  is not the easiest figure for seeing condition differences.

- [condition_by_channel_lfp_response_heatmap.png](../analysis/outputs/dec3/event_aligned_lfp/condition_by_channel_lfp_response_heatmap.png)

  **How it was generated:** a response metric was computed for each channel and
  each condition, then plotted as a heatmap.

  **Takeaway:** shows whether a response is broad across channels or localized
  to particular channels. It helps separate real spatial structure from one bad
  channel dominating the result.

- [better_plots/lfp_by_shank_conditions.png](../analysis/outputs/dec3/event_aligned_lfp/better_plots/lfp_by_shank_conditions.png)

  **How it was generated:** event-aligned LFP averages are grouped by
  provisional shank/channel group and condition.

  **Takeaway:** easier than the collapsed plot because it separates channel
  groups. Use this to see whether the response pattern is similar across
  groups.

- [better_plots/lfp_condition_envelopes.png](../analysis/outputs/dec3/event_aligned_lfp/better_plots/lfp_condition_envelopes.png)

  **How it was generated:** condition means are shown with envelopes/spread
  instead of only overlapping lines.

  **Takeaway:** this is a clearer version of the event-aligned LFP story when
  lines overlap. It shows both average response and variability.

- [better_plots/lfp_condition_panels_by_shank.png](../analysis/outputs/dec3/event_aligned_lfp/better_plots/lfp_condition_panels_by_shank.png)

  **How it was generated:** each condition and shank/group gets its own panel
  around the ON/OFF event.

  **Takeaway:** best visual inspection plot for timing: onset, sustained ON,
  offset, and OFF/recovery can be seen separately.

- [condition_summary_plots/lfp_condition_shank_heatmap_values.png](../analysis/outputs/dec3/event_aligned_lfp/condition_summary_plots/lfp_condition_shank_heatmap_values.png)

  **How it was generated:** condition responses are summarized numerically by
  shank/group and displayed as a heatmap.

  **Takeaway:** compact answer to "which conditions and groups have the largest
  LFP response?"

- [condition_summary_plots/lfp_frequency_difference_by_shank.png](../analysis/outputs/dec3/event_aligned_lfp/condition_summary_plots/lfp_frequency_difference_by_shank.png)

  **How it was generated:** for each amplitude and shank/group, the response
  difference between frequency conditions is summarized.

  **Takeaway:** helps ask whether 5 Hz and 26 Hz behave differently at the same
  amplitude.

- [condition_summary_plots/lfp_response_grouped_bars.png](../analysis/outputs/dec3/event_aligned_lfp/condition_summary_plots/lfp_response_grouped_bars.png)

  **How it was generated:** condition response values are averaged into grouped
  bar plots.

  **Takeaway:** an easy presentation version of the condition-response ranking.

- [artifact_aware_lfp/artifact_window_comparison.png](../analysis/outputs/dec3/artifact_aware_lfp/artifact_window_comparison.png)

  **How it was generated:** LFP metrics are recomputed with different margins
  around onset/offset excluded.

  **Takeaway:** checks whether a result is just an immediate stimulation
  artifact. If a result survives after excluding onset/offset margins, it is
  more likely to reflect sustained or recovery-related physiology.

- [artifact_aware_lfp/sustained_response_by_shank.png](../analysis/outputs/dec3/artifact_aware_lfp/sustained_response_by_shank.png)

  **How it was generated:** sustained ON-window response is calculated after
  artifact-aware trimming, grouped by shank/channel group.

  **Takeaway:** supports the idea that the strongest broadband LFP effects are
  not only one-frame onset artifacts.

## C. Frequency And Spectral Figures

These ask a different question from broadband LFP: does power increase at the
specific commanded stimulation frequency, such as 5 Hz or 26 Hz?

- [frequency_lfp/driven_power_change_by_analysis_group.png](../analysis/outputs/dec3/frequency_lfp/driven_power_change_by_analysis_group.png)

  **How it was generated:** for each condition, spectral power near the
  commanded frequency is compared between stimulation and baseline/pre windows,
  then summarized by analysis group.

  **Takeaway:** driven-frequency power is not the same as broadband response.
  This is why a strong LFP response does not automatically mean clean
  entrainment.

- [frequency_lfp/driven_power_change_by_channel.png](../analysis/outputs/dec3/frequency_lfp/driven_power_change_by_channel.png)

  **How it was generated:** the driven-frequency power metric is plotted
  channel by channel.

  **Takeaway:** checks whether frequency-specific effects are broadly present
  or concentrated on a few channels.

- [frequency_lfp/driven_power_change_by_physical_shank.png](../analysis/outputs/dec3/frequency_lfp/driven_power_change_by_physical_shank.png)

  **How it was generated:** the same driven-frequency metric is grouped by the
  current provisional physical shank assignments.

  **Takeaway:** useful for spatial organization, but anatomy claims remain
  conservative until probe geometry and channel order are confirmed.

- [frequency_lfp/frequency_specificity_by_group.png](../analysis/outputs/dec3/frequency_lfp/frequency_specificity_by_group.png)

  **How it was generated:** compares how specific the response is to the
  commanded frequency versus general/broad spectral changes.

  **Takeaway:** the 26 Hz story is nuanced. Current results do not support a
  simple final claim of strong sustained 26 Hz entrainment.

- [time_frequency_lfp/driven_frequency_timecourses.png](../analysis/outputs/dec3/time_frequency_lfp/driven_frequency_timecourses.png)

  **How it was generated:** time-varying power at the commanded frequency is
  extracted around each trial and averaged by condition.

  **Takeaway:** shows whether frequency-specific power is sustained during ON
  or appears mostly around transitions/recovery.

- [time_frequency_lfp/time_frequency_condition_grid.png](../analysis/outputs/dec3/time_frequency_lfp/time_frequency_condition_grid.png)

  **How it was generated:** spectrogram/time-frequency power is computed around
  trials for each condition.

  **Takeaway:** this is the main visual for asking whether there is a clean
  frequency-following response. Current reading: no strong final sustained
  26 Hz entrainment claim yet.

## D. Phase Locking

Phase locking asks whether trial-to-trial phase becomes consistent at the
stimulation frequency. This is stricter than "power increased."

- [phase_locking_lfp/plv_condition_summary.png](../analysis/outputs/dec3/phase_locking_lfp/plv_condition_summary.png)

  **How it was generated:** phase-locking value (PLV) is calculated across
  trials for each condition and summarized.

  **Takeaway:** current PLV results do not show a strong sustained locking
  effect. This supports the cautious interpretation: broadband LFP response,
  not final proof of entrainment.

- [phase_locking_lfp/plv_sustained_minus_pre.png](../analysis/outputs/dec3/phase_locking_lfp/plv_sustained_minus_pre.png)

  **How it was generated:** sustained ON PLV is compared against a pre-window.

  **Takeaway:** asks whether phase consistency actually increases during
  stimulation. Current evidence is not strong enough for a final entrainment
  claim.

- [phase_locking_lfp/plv_timecourses.png](../analysis/outputs/dec3/phase_locking_lfp/plv_timecourses.png)

  **How it was generated:** PLV is tracked over time around onset and offset.

  **Takeaway:** useful for seeing whether any phase effect is brief, sustained,
  or offset-related.

- [cohen_corrected/A_itpc_onset_vs_grid.png](../analysis/outputs/dec3/cohen_corrected/A_itpc_onset_vs_grid.png)

  **How it was generated:** Cohen-style inter-trial phase clustering/coherence
  is calculated around onset and compared across conditions.

  **Takeaway:** an independent teaching/check version of the PLV idea. It does
  not rescue a strong final 26 Hz entrainment claim.

- `provisional_final_pass/.../plv_*.png`

  **How it was generated:** duplicate/provisional copies of the PLV figures.

  **Takeaway:** use the canonical `phase_locking_lfp/` versions for
  presentation.

## E. Broadband Windows, OFF Control, Trial Statistics

These figures split a trial into biologically meaningful time windows:
sustained ON, offset, and the following OFF/recovery period.

- [broadband_transition/broadband_window_group_heatmaps.png](../analysis/outputs/dec3/broadband_transition/broadband_window_group_heatmaps.png)

  **How it was generated:** broadband LFP amplitude/power is computed in
  multiple trial windows and plotted by condition and analysis group.

  **Takeaway:** shows that timing matters. Some conditions are sustained-ON
  dominant; others are more offset/recovery dominant.

- [broadband_transition/broadband_windows_condition_ci.png](../analysis/outputs/dec3/broadband_transition/broadband_windows_condition_ci.png)

  **How it was generated:** bootstrap confidence intervals are computed for
  broadband response in each time window and condition.

  **Takeaway:** one of the clearest statistical-support figures for the
  broadband story, especially the `amp180_freq26` sustained/recovery pattern.

- [broadband_transition/transition_index_condition.png](../analysis/outputs/dec3/broadband_transition/transition_index_condition.png)

  **How it was generated:** a compact index compares response timing, such as
  ON-dominant versus OFF/recovery-dominant.

  **Takeaway:** use this to explain response timing in one compact plot.

- [off_control_broadband/off_control_condition_ci.png](../analysis/outputs/dec3/off_control_broadband/off_control_condition_ci.png)

  **How it was generated:** the 3 s OFF period after stimulation is treated as
  the within-trial control and compared by condition.

  **Takeaway:** `amp180_freq26` remains elevated into OFF/recovery. That means
  the result is not purely "during vibration only"; it includes recovery
  dynamics.

- [off_control_broadband/off_control_group_heatmaps.png](../analysis/outputs/dec3/off_control_broadband/off_control_group_heatmaps.png)

  **How it was generated:** OFF-control broadband response is shown by group
  and condition.

  **Takeaway:** spatial/group version of the OFF-control finding.

- [trial_level_stats/driven_power_ci.png](../analysis/outputs/dec3/trial_level_stats/driven_power_ci.png),
  [trial_level_stats/offset_broadband_ci.png](../analysis/outputs/dec3/trial_level_stats/offset_broadband_ci.png), and
  [trial_level_stats/sustained_broadband_ci.png](../analysis/outputs/dec3/trial_level_stats/sustained_broadband_ci.png)

  **How it was generated:** trial-level bootstrap confidence intervals are
  computed for driven-frequency power and broadband windows.

  **Takeaway:** early version of the statistical summaries. Kept for
  provenance.

- [trial_level_stats_equal_spectral_windows/driven_power_ci.png](../analysis/outputs/dec3/trial_level_stats_equal_spectral_windows/driven_power_ci.png),
  [trial_level_stats_equal_spectral_windows/offset_broadband_ci.png](../analysis/outputs/dec3/trial_level_stats_equal_spectral_windows/offset_broadband_ci.png), and
  [trial_level_stats_equal_spectral_windows/sustained_broadband_ci.png](../analysis/outputs/dec3/trial_level_stats_equal_spectral_windows/sustained_broadband_ci.png)

  **How it was generated:** same idea as above, but using more comparable
  spectral/statistical windows.

  **Takeaway:** prefer this set for presentation. Broadband results are more
  supported than driven-frequency power; driven-frequency CIs are more cautious.

- [cohen_corrected/B_broadband_rms.png](../analysis/outputs/dec3/cohen_corrected/B_broadband_rms.png)

  **How it was generated:** Cohen-style broadband RMS check, used as an
  independent correction/teaching version of the broadband result.

  **Takeaway:** supports the broadband response interpretation.

## F. Adaptation

Adaptation asks whether responses change across repeated trials.

- [adaptation_analysis/adaptation_epoch_summary.png](../analysis/outputs/dec3/adaptation_analysis/adaptation_epoch_summary.png)

  **How it was generated:** each condition's repeats are split into early,
  middle, and late epochs.

  **Takeaway:** responses are not necessarily stationary across the 200 repeats.

- [adaptation_analysis/adaptation_slope_summary.png](../analysis/outputs/dec3/adaptation_analysis/adaptation_slope_summary.png)

  **How it was generated:** response metrics are regressed against trial repeat
  number to estimate whether they increase or decrease over time.

  **Takeaway:** captures adaptation/habituation trends. Current reading:
  `amp250_freq26` declines strongly, and late `amp180_freq26` becomes more
  OFF/recovery dominated.

- [adaptation_analysis/adaptation_timecourses.png](../analysis/outputs/dec3/adaptation_analysis/adaptation_timecourses.png)

  **How it was generated:** response metrics are plotted across repeated trials
  as timecourses.

  **Takeaway:** best visual for explaining how the response evolves over the
  stimulation block.

## G. Reference Sensitivity

Reference sensitivity asks whether the LFP result depends on the chosen
referencing scheme.

- [reference_sensitivity_lfp/reference_condition_summary.png](../analysis/outputs/dec3/reference_sensitivity_lfp/reference_condition_summary.png)

  **How it was generated:** condition summaries are recomputed under alternate
  referencing choices.

  **Takeaway:** checks robustness. If a conclusion only appears under one
  reference, we should be cautious.

- [reference_sensitivity_lfp/reference_group_heatmaps.png](../analysis/outputs/dec3/reference_sensitivity_lfp/reference_group_heatmaps.png)

  **How it was generated:** reference-sensitive condition metrics are plotted
  by group.

  **Takeaway:** shows where reference choice changes the apparent spatial
  pattern.

- `provisional_final_pass/.../reference_*.png`

  **How it was generated:** duplicate/provisional copies.

  **Takeaway:** use the canonical `reference_sensitivity_lfp/` versions.

## H. Biological Summary Figures

These are the best top-level results figures.

- [biological_summary/amplitude_frequency_matrix.png](../analysis/outputs/dec3/biological_summary/amplitude_frequency_matrix.png)

  **How it was generated:** condition-level metrics are arranged by amplitude
  and frequency.

  **Takeaway:** shows whether the response depends more on amplitude,
  frequency, or their interaction.

- [biological_summary/broadband_vs_driven_power.png](../analysis/outputs/dec3/biological_summary/broadband_vs_driven_power.png)

  **How it was generated:** broadband LFP response and driven-frequency power
  are plotted side by side.

  **Takeaway:** this is the key conceptual figure. `amp180_freq26` can be
  strong in broadband LFP while not being a clean sustained 26 Hz entrainment
  result.

- [biological_summary/condition_fingerprint.png](../analysis/outputs/dec3/biological_summary/condition_fingerprint.png)

  **How it was generated:** multiple metrics are summarized for every
  condition in one compact figure.

  **Takeaway:** best first slide for "what happened across the six conditions?"

## I. Spikes

Spike results are pre-Phy-curation. That means Kilosort grouped candidate
spikes, but a human has not yet inspected/merged/split/rejected clusters in
Phy. Treat these as provisional triage, not final single-unit claims.

- [cluster_quality/cluster_quality_label_counts.png](../analysis/outputs/dec3/cluster_quality/cluster_quality_label_counts.png)

  **How it was generated:** Kilosort labels and automated quality categories
  are counted.

  **Takeaway:** shows how many clusters are likely usable before manual
  curation. Current summary: many clusters are noise/multiunit; a smaller set
  is high confidence.

- [cluster_quality/cluster_quality_scatter.png](../analysis/outputs/dec3/cluster_quality/cluster_quality_scatter.png)

  **How it was generated:** automated quality metrics are plotted for each
  cluster.

  **Takeaway:** explains why some clusters are treated as cleaner than others.

- [modal_kilosort4_results/kilosort4_results/diagnostics.png](../analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/diagnostics.png),
  [drift_amount.png](../analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/drift_amount.png),
  [drift_scatter.png](../analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/drift_scatter.png), and
  [spike_positions.png](../analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/spike_positions.png)

  **How it was generated:** Kilosort4 diagnostic outputs from the Modal GPU
  sorting run.

  **Takeaway:** documents that spike sorting ran and gives drift/position
  diagnostics. These are not the same as manual curation.

- `spike_positions_modal_kilosort4.png`

  **How it was generated:** larger local spike-position overview.

  **Takeaway:** useful locally, but too large for normal GitHub presentation.
  Use the Kilosort diagnostics folder for supervisor-facing links.

- [spikeinterface_setup/spikeinterface_trace_sanity.png](../analysis/outputs/dec3/spikeinterface_setup/spikeinterface_trace_sanity.png)

  **How it was generated:** SpikeInterface opens the raw binary and plots a
  short trace sanity check.

  **Takeaway:** confirms the raw data can be loaded correctly by Python tools.

- [spike_peth_on_off/condition_mean_on_minus_off.png](../analysis/outputs/dec3/spike_peth_on_off/condition_mean_on_minus_off.png)

  **How it was generated:** spike firing rates are compared between ON and OFF
  periods by condition using the initial Kilosort-good set.

  **Takeaway:** preliminary ON-minus-OFF spike effect summary.

- [spike_peth_on_off/peth_onset_ks_good_units.png](../analysis/outputs/dec3/spike_peth_on_off/peth_onset_ks_good_units.png) and
  [spike_peth_on_off/peth_offset_ks_good_units.png](../analysis/outputs/dec3/spike_peth_on_off/peth_offset_ks_good_units.png)

  **How it was generated:** peri-event time histograms are aligned to
  stimulation onset and offset for Kilosort-good units.

  **Takeaway:** shows whether firing changes around onset or offset, before
  stricter quality filtering.

- [spike_peth_on_off/unit_condition_on_minus_off_heatmap_all_units.png](../analysis/outputs/dec3/spike_peth_on_off/unit_condition_on_minus_off_heatmap_all_units.png) and
  [unit_condition_on_minus_off_heatmap_ks_good.png](../analysis/outputs/dec3/spike_peth_on_off/unit_condition_on_minus_off_heatmap_ks_good.png)

  **How it was generated:** each unit's ON-minus-OFF firing change is plotted
  for each condition.

  **Takeaway:** compares all clusters with Kilosort-good clusters. All-cluster
  plots are more vulnerable to noise/multiunit contamination.

- [spike_peth_high_confidence/condition_mean_on_minus_off_unit_set_comparison.png](../analysis/outputs/dec3/spike_peth_high_confidence/condition_mean_on_minus_off_unit_set_comparison.png)

  **How it was generated:** ON-minus-OFF firing is compared across all units,
  Kilosort-good units, and stricter high-confidence units.

  **Takeaway:** main spike caveat figure. The cleaner the unit set gets, the
  less it supports a strong stimulation-driven firing-rate increase.

- [spike_peth_high_confidence/high_confidence_unit_condition_heatmap.png](../analysis/outputs/dec3/spike_peth_high_confidence/high_confidence_unit_condition_heatmap.png)

  **How it was generated:** high-confidence units only, ON-minus-OFF by
  condition.

  **Takeaway:** current cleanest unit subset does not show robust corrected
  condition effects.

- [spike_peth_high_confidence/peth_onset_high_confidence_units.png](../analysis/outputs/dec3/spike_peth_high_confidence/peth_onset_high_confidence_units.png) and
  [peth_offset_high_confidence_units.png](../analysis/outputs/dec3/spike_peth_high_confidence/peth_offset_high_confidence_units.png)

  **How it was generated:** onset- and offset-aligned PETHs for the
  high-confidence unit subset.

  **Takeaway:** use these for the most conservative pre-curation spike view.

## J. Channel QC And Trace Pages

These are mostly sanity/QC figures, not final biological claims.

- [channel_qc/channel_qc_metrics.png](../analysis/outputs/dec3/channel_qc/channel_qc_metrics.png)

  **How it was generated:** channel-level noise and signal metrics are
  computed across the recording.

  **Takeaway:** helps identify channels that are disconnected, very noisy, or
  otherwise unreliable.

- [channel_qc_baseline/channel_qc_metrics.png](../analysis/outputs/dec3/channel_qc_baseline/channel_qc_metrics.png)

  **How it was generated:** similar QC metrics, focused on baseline periods.

  **Takeaway:** baseline QC is useful because it avoids stimulation artifacts.

- [channel_qc_baseline/high_noise_review_traces.png](../analysis/outputs/dec3/channel_qc_baseline/high_noise_review_traces.png)

  **How it was generated:** traces from high-noise candidate channels are
  plotted for visual inspection.

  **Takeaway:** supports the bad-channel exclusion list.

- Raw trace pages:
  [s1 1000s](../analysis/outputs/dec3/channel_trace_pages/shank1_ch96_127_start1000s.png),
  [s1 1540s](../analysis/outputs/dec3/channel_trace_pages/shank1_ch96_127_start1540s.png),
  [s1 2000s](../analysis/outputs/dec3/channel_trace_pages/shank1_ch96_127_start2000s.png),
  [s2 1000s](../analysis/outputs/dec3/channel_trace_pages/shank2_ch64_95_start1000s.png),
  [s2 1540s](../analysis/outputs/dec3/channel_trace_pages/shank2_ch64_95_start1540s.png),
  [s2 2000s](../analysis/outputs/dec3/channel_trace_pages/shank2_ch64_95_start2000s.png),
  [s3 1000s](../analysis/outputs/dec3/channel_trace_pages/shank3_ch32_63_start1000s.png),
  [s3 1540s](../analysis/outputs/dec3/channel_trace_pages/shank3_ch32_63_start1540s.png),
  [s3 2000s](../analysis/outputs/dec3/channel_trace_pages/shank3_ch32_63_start2000s.png),
  [s4 1000s](../analysis/outputs/dec3/channel_trace_pages/shank4_ch0_31_start1000s.png),
  [s4 1540s](../analysis/outputs/dec3/channel_trace_pages/shank4_ch0_31_start1540s.png),
  [s4 2000s](../analysis/outputs/dec3/channel_trace_pages/shank4_ch0_31_start2000s.png)

  **How it was generated:** raw/high-rate traces are shown by provisional shank
  and time point.

  **Takeaway:** these are the Python analogue of looking in Neuroscope. Use
  them to visually inspect noisy channels and large artifacts.

- LFP trace pages:
  [s1 1000s](../analysis/outputs/dec3/lfp_trace_pages/shank1_ch96_127_start1000s.png),
  [s1 1540s](../analysis/outputs/dec3/lfp_trace_pages/shank1_ch96_127_start1540s.png),
  [s2 1000s](../analysis/outputs/dec3/lfp_trace_pages/shank2_ch64_95_start1000s.png),
  [s2 1540s](../analysis/outputs/dec3/lfp_trace_pages/shank2_ch64_95_start1540s.png),
  [s3 1000s](../analysis/outputs/dec3/lfp_trace_pages/shank3_ch32_63_start1000s.png),
  [s3 1540s](../analysis/outputs/dec3/lfp_trace_pages/shank3_ch32_63_start1540s.png),
  [s4 1000s](../analysis/outputs/dec3/lfp_trace_pages/shank4_ch0_31_start1000s.png),
  [s4 1540s](../analysis/outputs/dec3/lfp_trace_pages/shank4_ch0_31_start1540s.png)

  **How it was generated:** downsampled/filtered LFP traces are plotted by
  provisional shank and time point.

  **Takeaway:** these show the signal used for LFP analyses after filtering and
  downsampling.

## K. Teaching And Probe Figures

- [REPORT/LEARN_real_vs_dec3.png](../analysis/outputs/dec3/REPORT/LEARN_real_vs_dec3.png)

  **How it was generated:** teaching schematic comparing an idealized clean
  entrainment result with the actual Dec 3 pattern.

  **Takeaway:** helps explain the core distinction: Dec 3 has strong LFP
  responses, but not a clean final 26 Hz entrainment story.

- [REPORT/LEARN_results_at_a_glance.png](../analysis/outputs/dec3/REPORT/LEARN_results_at_a_glance.png)

  **How it was generated:** simplified teaching summary of the major result
  categories.

  **Takeaway:** good first-pass teaching figure before showing detailed plots.

- [methods/margin_exclusion_test.png](../analysis/outputs/dec3/methods/margin_exclusion_test.png)

  **How it was generated:** analysis windows are recomputed after excluding
  margins around stimulation onset/offset.

  **Takeaway:** teaches why artifact-aware windows matter. The user-facing name
  "LEARN_margin_test.png" refers to this methods figure.

- [REPORT/supp_provisional_probe_map_H12_UNRESOLVED.png](../analysis/outputs/dec3/REPORT/supp_provisional_probe_map_H12_UNRESOLVED.png)

  **How it was generated:** provisional probe/shank geometry is drawn from the
  current best guess.

  **Takeaway:** use only to explain uncertainty. Do not make CA1/DG or
  medial/lateral claims until probe model, channel order, and anatomy are
  confirmed.

## Best Order For Learning The Results

1. Start with validation: timeline, TTL alignment, and movement sensitivity.
2. Then learn the LFP story: condition fingerprint, broadband vs driven power,
   event-aligned LFP by shank, and OFF-control broadband.
3. Then learn the caution: time-frequency grid, driven power CIs, and PLV.
4. Then learn adaptation: timecourses and slope summary.
5. End with spikes: cluster quality first, then high-confidence PETH/heatmaps,
   always saying these are pre-Phy-curation.

