# Dec 3 Major Images

This guide lists the most important Dec 3 result figures and what each one is
for. Start with the dashboard, then use these figures when explaining the
analysis.

Main dashboard:

- `analysis/outputs/dec3/RESULTS_DASHBOARD.html`

Supervisor-facing summary:

- `analysis/DEC3_SUPERVISOR_SUMMARY.md`

## Core LFP Results

1. `analysis/outputs/dec3/biological_summary/condition_fingerprint.png`

   Best compact visual summary of each stimulation condition. Use this as the
   first "what happened across conditions" figure.

2. `analysis/outputs/dec3/biological_summary/amplitude_frequency_matrix.png`

   Shows the amplitude/frequency response structure. Useful for the question:
   does the response depend more on amplitude, frequency, or their interaction?

3. `analysis/outputs/dec3/biological_summary/broadband_vs_driven_power.png`

   Separates broadband LFP changes from frequency-specific driven power. This
   supports the current interpretation that `amp180_freq26` is strong in
   broadband LFP, while frequency-specific 26 Hz entrainment is not the cleanest
   result.

4. `analysis/outputs/dec3/event_aligned_lfp/better_plots/lfp_condition_panels_by_shank.png`

   Event-aligned LFP traces split by provisional shank/channel group. Use for
   visual inspection of the ON and OFF response shape.

5. `analysis/outputs/dec3/event_aligned_lfp/better_plots/lfp_condition_envelopes.png`

   Cleaner event-aligned LFP visualization with condition envelopes. Use when
   overlapping raw condition means are hard to read.

6. `analysis/outputs/dec3/event_aligned_lfp/condition_by_channel_lfp_response_heatmap.png`

   Channel-by-condition LFP response heatmap. Useful for seeing whether a result
   is broad across channels or concentrated on specific channels.

## Time-Frequency, Frequency Specificity, And Phase

7. `analysis/outputs/dec3/time_frequency_lfp/time_frequency_condition_grid.png`

   Main time-frequency figure. Use to discuss when frequency-band changes occur
   relative to stimulation onset and offset.

8. `analysis/outputs/dec3/time_frequency_lfp/driven_frequency_timecourses.png`

   Time courses for driven-frequency power. Use to compare sustained ON effects
   with offset/recovery effects.

9. `analysis/outputs/dec3/frequency_lfp/frequency_specificity_by_group.png`

   Frequency-specificity summary by analysis group. Use to explain why the
   26 Hz story is nuanced rather than simply "26 Hz entrainment."

10. `analysis/outputs/dec3/phase_locking_lfp/plv_condition_summary.png`

    Phase-locking summary. Current interpretation: first PLV pass does not show
    strong trial-to-trial phase entrainment.

11. `analysis/outputs/dec3/phase_locking_lfp/plv_timecourses.png`

    PLV time course figure. Use to inspect whether any phase-locking change is
    brief, sustained, or offset-related.

## Trial-Level And OFF-Control Results

12. `analysis/outputs/dec3/trial_level_stats_equal_spectral_windows/sustained_broadband_ci.png`

    Bootstrap confidence intervals for sustained broadband response. This is one
    of the main statistical-support figures.

13. `analysis/outputs/dec3/trial_level_stats_equal_spectral_windows/driven_power_ci.png`

    Bootstrap confidence intervals for driven-frequency power. Current
    interpretation: driven-frequency intervals are suggestive but corrected CIs
    cross zero.

14. `analysis/outputs/dec3/broadband_transition/broadband_windows_condition_ci.png`

    Sustained/offset/recovery broadband windows by condition. Use for the
    transition story: `amp180_freq26` has reliable sustained, offset, and
    recovery broadband effects; `amp250_freq26` is offset-heavy.

15. `analysis/outputs/dec3/broadband_transition/transition_index_condition.png`

    Compact transition-index figure. Use for explaining ON-dominant versus
    OFF/recovery-dominant responses.

16. `analysis/outputs/dec3/off_control_broadband/off_control_condition_ci.png`

    Key control figure. Shows that the following 3 s OFF interval is itself
    elevated for `amp180_freq26`, so the effect is not purely ON-only.

17. `analysis/outputs/dec3/adaptation_analysis/adaptation_timecourses.png`

    Adaptation across repeated trials. Use for the observation that responses
    change across the 200 repeats.

18. `analysis/outputs/dec3/adaptation_analysis/adaptation_slope_summary.png`

    Summary of repeat-dependent slopes. Useful for the finding that
    `amp250_freq26` declines strongly over repeats and late `amp180_freq26`
    becomes OFF-dominant.

## Spike Sorting And Spikes

19. `analysis/outputs/dec3/cluster_quality/cluster_quality_scatter.png`

    Automated pre-curation quality scatter. Use to explain why only a subset of
    Kilosort units should be trusted before Phy curation.

20. `analysis/outputs/dec3/cluster_quality/cluster_quality_label_counts.png`

    Counts of Kilosort labels and automated review categories. Current count:
    194 clusters, 28 KS-good, 19 high-confidence KS-good, 142 likely
    noise/multiunit.

21. `analysis/outputs/dec3/spike_peth_high_confidence/condition_mean_on_minus_off_unit_set_comparison.png`

    Main spike result after cleaner filtering. It compares all clusters,
    KS-good clusters, and high-confidence KS-good clusters.

22. `analysis/outputs/dec3/spike_peth_high_confidence/high_confidence_unit_condition_heatmap.png`

    High-confidence unit-by-condition ON-minus-OFF heatmap.

23. `analysis/outputs/dec3/spike_peth_high_confidence/peth_onset_high_confidence_units.png`

    Onset-aligned PETH for the 19 high-confidence units.

24. `analysis/outputs/dec3/spike_peth_high_confidence/peth_offset_high_confidence_units.png`

    Offset-aligned PETH for the 19 high-confidence units.

25. `analysis/outputs/dec3/spike_peth_on_off/unit_condition_on_minus_off_heatmap_ks_good.png`

    Original KS-good unit heatmap before the stricter high-confidence filter.

## Quality Control And Setup Figures

26. `analysis/outputs/dec3/channel_qc_baseline/channel_qc_metrics.png`

    Baseline channel QC metrics. Use when explaining bad-channel exclusion.

27. `analysis/outputs/dec3/channel_qc_baseline/high_noise_review_traces.png`

    Visual review traces for high-noise candidate channels.

28. `analysis/outputs/dec3/ttl_on_off_audit/ttl_on_off_counts.png`

    TTL event audit figure confirming the 3 s ON / 3 s OFF event structure used
    for the analysis.

29. `analysis/outputs/dec3/spikeinterface_setup/spikeinterface_trace_sanity.png`

    SpikeInterface raw trace sanity check.

30. `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/diagnostics.png`

    Kilosort diagnostic figure. Useful for documenting that Kilosort ran, but
    not a final curation result.

## Short Figure Story

- For the LFP story, lead with figures 1, 3, 14, 16, and 17.
- For the frequency/entrainment caveat, use figures 7, 9, and 10.
- For spikes, lead with figures 19, 21, and 22.
- For methods/QC, use figures 26, 28, and 30.
