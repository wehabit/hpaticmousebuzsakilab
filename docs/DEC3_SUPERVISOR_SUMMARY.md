# Dec 3 Supervisor Summary

This is the clean, supervisor-facing summary of the Dec 3 haptic mouse
analysis. It points to the key figures, findings, tools, and pipeline steps.

Main clickable dashboard:

- [Dec 3 Results Dashboard](../analysis/outputs/dec3/RESULTS_DASHBOARD.html)

Detailed supporting docs:

- [Full Results Summary](DEC3_RESULTS_SUMMARY.md)
- [Major Images Guide](DEC3_MAJOR_IMAGES.md)
- [Image Walkthrough For Learning](DEC3_IMAGE_WALKTHROUGH.md)
- [Misi Preprocessing Checklist](DEC3_MISI_PREPROCESSING_CHECKLIST.md)
- [Run Log](DEC3_ANALYSIS_LOG.md)
- [Open Questions](OPEN_QUESTIONS.md)

## One-Paragraph Takeaway

Dec 3 shows clear stimulation-related LFP effects, but the result is not a
simple "26 Hz entrainment" story. The strongest and most reliable signal is a
broadband LFP/recovery response around `amp180_freq26`, including elevated
activity during the following 3 s OFF-control period. Frequency-specific power
and phase-locking analyses are more cautious: they do not show a robust,
corrected, sustained 26 Hz entrainment effect. Spike sorting has run, but the
cleanest high-confidence single-unit subset does not show a robust ON-period
firing-rate increase; spike claims remain provisional until Phy curation.

## Main Findings

### 1. LFP Broadband Response

- `amp180_freq26` is the strongest sustained broadband LFP condition.
- Broadband here means total LFP amplitude/power increased, not necessarily
  power exactly at the stimulation frequency.
- The effect persists into the 3 s OFF/recovery period, so it is not purely an
  ON-only response.

Key figures:

- [Condition fingerprint](../analysis/outputs/dec3/biological_summary/condition_fingerprint.png)
- [Broadband vs driven power](../analysis/outputs/dec3/biological_summary/broadband_vs_driven_power.png)
- [Broadband transition windows](../analysis/outputs/dec3/broadband_transition/broadband_windows_condition_ci.png)
- [OFF-control broadband effect](../analysis/outputs/dec3/off_control_broadband/off_control_condition_ci.png)

### 2. Frequency-Specific Power Is More Nuanced

- The strongest full-window driven-frequency result is not simply
  `amp180_freq26`.
- `amp180_freq5` is the clearest driven-frequency increase in the current
  preprocessing.
- `amp100_freq26` is the best current 26 Hz-band power candidate among the 26 Hz
  conditions.
- Trial-level corrected confidence intervals for driven-frequency power cross
  zero, so frequency-specific power findings are suggestive rather than final.

Key figures:

- [Time-frequency condition grid](../analysis/outputs/dec3/time_frequency_lfp/time_frequency_condition_grid.png)
- [Driven-frequency time courses](../analysis/outputs/dec3/time_frequency_lfp/driven_frequency_timecourses.png)
- [Frequency specificity by group](../analysis/outputs/dec3/frequency_lfp/frequency_specificity_by_group.png)
- [Driven-power confidence intervals](../analysis/outputs/dec3/trial_level_stats_equal_spectral_windows/driven_power_ci.png)

### 3. Phase-Locking Does Not Support Strong Entrainment Yet

- The first PLV analysis does not show a strong sustained increase in
  trial-to-trial phase consistency.
- This supports the current interpretation that `amp180_freq26` is a strong
  broadband/recovery LFP response, not clean sustained 26 Hz locking.

Key figures:

- [PLV condition summary](../analysis/outputs/dec3/phase_locking_lfp/plv_condition_summary.png)
- [PLV time courses](../analysis/outputs/dec3/phase_locking_lfp/plv_timecourses.png)

### 4. Adaptation And OFF/Recovery Dynamics Matter

- `amp250_freq26` declines strongly over repeats.
- Late `amp180_freq26` trials become more OFF-dominant.
- The timing structure matters: onset, sustained ON, offset, and recovery should
  be analyzed separately.

Key figures:

- [Adaptation time courses](../analysis/outputs/dec3/adaptation_analysis/adaptation_timecourses.png)
- [Adaptation slope summary](../analysis/outputs/dec3/adaptation_analysis/adaptation_slope_summary.png)
- [Transition index](../analysis/outputs/dec3/broadband_transition/transition_index_condition.png)

### 5. Spike Results Are Provisional And Do Not Yet Match The LFP Story

- Kilosort produced `194` clusters/templates (an over-count: an automated
  over-split detector found templates `{90, 91, 92, 97, 104}` are one neuron
  split into 5, giving ~`190` candidate units; the `19` high-confidence units
  are validated as distinct from each other).
- Kilosort labeled `28` clusters as `good`.
- Automated quality triage identified `19` high-confidence KS-good clusters.
- The high-confidence subset shows no BH-corrected ON-vs-OFF unit/condition
  firing-rate effects.
- Therefore, there is no clean current evidence that stimulation increases
  high-confidence single-unit firing during ON.
- Manual Phy curation is still needed before final spike claims.

Key figures:

- [Cluster quality scatter](../analysis/outputs/dec3/cluster_quality/cluster_quality_scatter.png)
- [Cluster label counts](../analysis/outputs/dec3/cluster_quality/cluster_quality_label_counts.png)
- [High-confidence spike unit-set comparison](../analysis/outputs/dec3/spike_peth_high_confidence/condition_mean_on_minus_off_unit_set_comparison.png)
- [High-confidence spike heatmap](../analysis/outputs/dec3/spike_peth_high_confidence/high_confidence_unit_condition_heatmap.png)
- [High-confidence onset PETH](../analysis/outputs/dec3/spike_peth_high_confidence/peth_onset_high_confidence_units.png)
- [High-confidence offset PETH](../analysis/outputs/dec3/spike_peth_high_confidence/peth_offset_high_confidence_units.png)

## Methods And Pipeline

### Data Scope

- Analysis is restricted to the Dec 3 recording.
- Study structure:
  - at least 15 minutes baseline
  - repeated 3 s ON / 3 s OFF trials
  - 200 repeats for each condition
  - conditions are combinations of amplitude and frequency:
    - amplitudes: `100`, `180`, `250`
    - frequencies: `5 Hz`, `26 Hz`
- The following 3 s OFF period is treated as the within-trial control.

### Preprocessing

Configuration:

- [final_preprocessing_dec3.json](final_preprocessing_dec3.json)

Current channel assumptions:

- Total raw amplifier channels: `128`
- Confirmed bad channels for current analysis pass:
  `5, 6, 7, 32, 33, 34, 43, 66, 67`
- Good/connected channels used for spike sorting: `119`
- Current reference for main LFP pass: `analysis_group_median`
- Probe identity (confirmed via the Dec 4 two-probe recording): the Dec 3
  128-ch recording is the **dHPC probe (Cambridge NeuroTech H12_2), Port A**.
  See [DEC4_SUPERVISOR_SUMMARY.md](DEC4_SUPERVISOR_SUMMARY.md).
- Subregion anatomy labels (CA1/DG/medial/lateral) are still not assigned --
  that needs surgery orientation + histology, not more analysis.

### TTL And Trial Windows

Scripts:

- [intan_haptic_summary.py](intan_haptic_summary.py)
- [ttl_on_off_audit_dec3.py](ttl_on_off_audit_dec3.py)
- [export_pynapple_dec3.py](export_pynapple_dec3.py)

Outputs:

- [TTL audit counts](../analysis/outputs/dec3/ttl_on_off_audit/ttl_on_off_counts.png)
- [Trial windows](../analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv)
- [Condition sequence](../analysis/outputs/dec3/dec3_condition_sequence.csv)
- [Stimulation events](../analysis/outputs/dec3/stimulation_events.csv) -- TTL QC
  only for Dec 3 because burst enumeration is not one-to-one with scheduled
  trials.

Use `dec3_condition_sequence.csv` / `trial_windows.csv` as the source of trial
labels and ON/OFF windows. Use TTL tables and figures to check physical delivery
and missing/merged/pre/post TTL activity.

### LFP Analysis

Scripts:

- [extract_lfp.py](extract_lfp.py)
- [event_aligned_lfp.py](event_aligned_lfp.py)
- [artifact_aware_lfp.py](artifact_aware_lfp.py)
- [frequency_lfp.py](frequency_lfp.py)
- [time_frequency_lfp.py](time_frequency_lfp.py)
- [trial_level_stats_dec3.py](trial_level_stats_dec3.py)
- [off_control_broadband_dec3.py](off_control_broadband_dec3.py)
- [broadband_transition_stats_dec3.py](broadband_transition_stats_dec3.py)
- [adaptation_analysis_dec3.py](adaptation_analysis_dec3.py)
- [phase_locking_lfp.py](phase_locking_lfp.py)
- [reference_sensitivity_lfp.py](reference_sensitivity_lfp.py)

Reports:

- [Event-aligned LFP](../analysis/outputs/dec3/event_aligned_lfp/index.html)
- [Time-frequency LFP](../analysis/outputs/dec3/time_frequency_lfp/index.html)
- [Frequency LFP](../analysis/outputs/dec3/frequency_lfp/index.html)
- [Trial-level stats](../analysis/outputs/dec3/trial_level_stats_equal_spectral_windows/index.html)
- [OFF-control broadband](../analysis/outputs/dec3/off_control_broadband/index.html)
- [Broadband transition](../analysis/outputs/dec3/broadband_transition/index.html)
- [Adaptation](../analysis/outputs/dec3/adaptation_analysis/index.html)
- [Phase locking](../analysis/outputs/dec3/phase_locking_lfp/index.html)
- [Reference sensitivity](../analysis/outputs/dec3/reference_sensitivity_lfp/index.html)

### Spike Sorting And Spike Analysis

Tools used:

- Kilosort4 on Modal GPU
- SpikeInterface for raw binary loading and smoke-test sorting
- Phy setup attempted locally and through Modal noVNC
- Pynapple used for interval/spike export compatibility

Scripts:

- [prepare_spike_sorting_dec3.py](prepare_spike_sorting_dec3.py)
- [setup_spikeinterface_dec3.py](setup_spikeinterface_dec3.py)
- [run_spikeinterface_test_sort_dec3.py](run_spikeinterface_test_sort_dec3.py)
- [modal_kilosort_dec3.py](modal_kilosort_dec3.py)
- [modal_phy_dec3.py](modal_phy_dec3.py)
- [export_kilosort_pynapple_dec3.py](export_kilosort_pynapple_dec3.py)
- [cluster_quality_dec3.py](cluster_quality_dec3.py)
- [spike_peth_on_off_dec3.py](spike_peth_on_off_dec3.py)
- [spike_peth_high_confidence_dec3.py](spike_peth_high_confidence_dec3.py)

Reports:

- [Spike sorting prep](../analysis/outputs/dec3/spike_sorting_prep/README.md)
- [SpikeInterface setup](../analysis/outputs/dec3/spikeinterface_setup/README.md)
- [Kilosort output summary](../analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/README.md)
- [Cluster quality](../analysis/outputs/dec3/cluster_quality/index.html)
- [Uncurated spike ON/OFF](../analysis/outputs/dec3/spike_peth_on_off/index.html)
- [High-confidence spike ON/OFF](../analysis/outputs/dec3/spike_peth_high_confidence/index.html)
- [Phy setup status](PHY_DEC3_SETUP.md)

## Important Caveats

- Spike results are pre-Phy-curation. This means Kilosort has detected and
  grouped candidate spike clusters, but a human has not yet inspected those
  clusters in Phy to decide which are true single units, which are multiunit
  activity, which are duplicates/merge candidates, and which are noise. The
  current spike figures are therefore useful for triage and hypothesis
  generation, but they should not be presented as final single-neuron results.

- Probe *identity* is now confirmed: the Dec 4 two-probe recording established
  that this Dec 3 128-ch recording is the dHPC probe (Cambridge NeuroTech
  H12_2) on Port A. What still needs final confirmation is probe *geometry* --
  the exact site order within H12_2 and the physical shank orientation
  (which shank is medial/lateral/anterior/posterior). This matters most for
  spike sorting, shank-level summaries, and any spatial interpretation across
  the probe.

- Anatomy labels should remain conservative; no CA1/DG/medial/lateral claims
  are made yet. At this stage we can refer to channel groups or provisional
  physical shanks, but we should not say that a response comes from a specific
  hippocampal subregion until the implant orientation, histology/surgery notes,
  and probe map are confirmed.

- Frequency-specific 26 Hz power and PLV do not yet support a strong final
  entrainment claim. The LFP response around `amp180_freq26` is strong in
  broadband/recovery metrics, but the analyses that specifically test
  stimulation-frequency following -- 26 Hz-band power and phase-locking value
  -- are not yet robust after the current corrections. In presentation language:
  "strong LFP response at a 26 Hz stimulation condition" is supported better
  than "clean sustained 26 Hz entrainment."

- The 3 s OFF-control period is not a neutral baseline for every condition.
  It is the planned within-trial control, but for `amp180_freq26` the OFF period
  itself remains elevated. That is biologically interesting, but it means the
  effect includes recovery/offset dynamics and cannot be summarized as purely
  stimulation-ON activity.

- The current bad-channel list is treated as confirmed for this analysis pass,
  but it should still be documented as an analysis decision. Channels
  `5, 6, 7, 32, 33, 34, 43, 66, 67` were excluded. If the final probe map or
  visual review changes, the LFP and spike analyses should be rerun.

- Large raw/intermediate arrays are kept local and intentionally excluded from
  GitHub. GitHub contains code, summaries, CSVs, HTML reports, and normal-sized
  figures. This keeps the repository usable, but it also means that full
  re-analysis requires access to the local/raw data files and the excluded large
  Kilosort/Pynapple arrays.

## Suggested Presentation Order

1. Start with
   [Condition fingerprint](../analysis/outputs/dec3/biological_summary/condition_fingerprint.png).

   Main point: this is the quick overview of how the six amplitude/frequency
   conditions differ. Use it to orient the audience before going into details.
   The broad takeaway is that the response is condition-specific, with
   `amp180_freq26` standing out in the LFP features.

2. Explain broadband vs driven-frequency using
   [Broadband vs driven power](../analysis/outputs/dec3/biological_summary/broadband_vs_driven_power.png).

   Main point: broadband LFP response and frequency-specific entrainment are
   different measurements. `amp180_freq26` is strong in broadband LFP, but that
   does not automatically mean the signal is cleanly oscillating at 26 Hz.
   This figure is the clearest way to explain why our conclusion is nuanced.

3. Show timing/recovery with
   [Broadband transition windows](../analysis/outputs/dec3/broadband_transition/broadband_windows_condition_ci.png).

   Main point: the response depends on time window. `amp180_freq26` has
   sustained, offset, and recovery broadband increases, while some other
   conditions are more offset-heavy. This supports the idea that onset/offset
   and recovery dynamics matter, not just average ON-period activity.

4. Then show the 3 s OFF-control result with
   [OFF-control broadband effect](../analysis/outputs/dec3/off_control_broadband/off_control_condition_ci.png).

   Main point: the following OFF period is not always flat. For `amp180_freq26`,
   the OFF-control interval remains elevated, so the response persists after
   stimulation turns off. This is important because the experiment design uses
   3 s ON followed by 3 s OFF, and the OFF period is part of the biology we are
   measuring.

5. Show the entrainment caveat with
   [Time-frequency condition grid](../analysis/outputs/dec3/time_frequency_lfp/time_frequency_condition_grid.png).

   Main point: the time-frequency plot shows when spectral changes occur around
   stimulation. It helps separate sustained ON-period frequency changes from
   onset/offset/recovery changes. The current pattern does not support a simple
   "26 Hz stimulation equals sustained 26 Hz entrainment" interpretation.

6. Pair that with
   [PLV condition summary](../analysis/outputs/dec3/phase_locking_lfp/plv_condition_summary.png).

   Main point: PLV asks whether the LFP phase is consistent across trials at
   the stimulation frequency. The first PLV pass does not show strong sustained
   phase-locking, which further weakens a final entrainment claim.

7. Show spike caveat with
   [High-confidence spike unit-set comparison](../analysis/outputs/dec3/spike_peth_high_confidence/condition_mean_on_minus_off_unit_set_comparison.png).

   Main point: when we restrict to the cleanest automated KS-good units, the
   spike response does not show a robust ON > OFF firing-rate increase. This
   means the current spike analysis does not mirror the strong LFP response.
   The honest interpretation is: strong LFP effect, but no clean
   high-confidence single-unit firing-rate effect yet.

8. If there is time, show
   [Cluster quality scatter](../analysis/outputs/dec3/cluster_quality/cluster_quality_scatter.png)
   or
   [Cluster label counts](../analysis/outputs/dec3/cluster_quality/cluster_quality_label_counts.png).

   Main point: these explain why spike claims are provisional. Kilosort found
   194 clusters, but only 28 were KS-good and 19 passed the conservative
   automated high-confidence screen. This motivates manual Phy curation.

9. End with next steps.

   Main point: the next scientific step is not another broad exploratory plot.
   It is targeted cleanup: complete Phy curation, confirm final probe geometry
   and channel order, then rerun the spike ON/OFF analysis on curated good units
   and keep anatomy labels conservative until probe orientation is confirmed.
