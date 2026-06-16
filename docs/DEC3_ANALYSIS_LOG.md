# Dec 3 Analysis Log

This log tracks the Python version of the Dec 3 pipeline, following Mishi's
Buzcode/CellExplorer workflow while keeping the raw files unchanged unless noted.

## Current Provisional Final-Pass Settings

- Config: `analysis/final_preprocessing_dec3.json`
- Candidate bad channels excluded: `5, 6, 7, 32, 33, 34, 43, 66, 67`
- LFP reference: `analysis_group_median`
- Caveat: this is not yet a collaborator-confirmed visual bad-channel list.
- Anatomy labels remain channel/group-level only until probe orientation is
  confirmed.
- Provisional final-pass outputs:
  `analysis/outputs/dec3/provisional_final_pass/index.html`

## Completed

1. **Instruction repo cloned**
   - Repo: `wehabit/hpaticmousebuzsakilab`
   - Local path: `/Users/paris/Documents/Buzsaki Lab/hpaticmousebuzsakilab`

2. **Dec 3 metadata verified**
   - `info.rhd` reports 128 amplifier channels at 20 kHz.
   - The original `amplifier.xml` declared 256 channels, which was wrong for Dec 3.
   - Original XML was backed up as `amplifier_original_256ch.xml`.
   - Active `amplifier.xml` now declares 128 channels and four 32-channel
     analysis groups.
   - Cambridge NeuroTech's ASSY-350 H12/L13 map indicates this is a two-shank
     128-channel layout:
     - Physical Shank A: channels `0-63`
     - Physical Shank B: channels `64-127`
     - The four 32-channel XML groups should be treated as analysis/spike groups
       until the exact H12_2 contact ordering is confirmed.
   - Heechul's implant metadata says:
     - LEC: AP `3.8 mm`, ML `3.8 mm`, depth as needed, `5 deg`, H15 probe.
     - dHPC: AP `1.8 mm`, ML `1.5 mm`, depth `1-1.8 mm`, H12_2 probe.
     - For Dec 3's 128-channel dHPC recording, the H12_2/H12 map is the relevant
       probe-family reference; the H7/64-electrode atlas screenshot is useful for
       trajectory intuition but should not define the channel map.
   - The anatomical direction of Shank A vs Shank B cannot be assigned from the
     atlas screenshot alone; implant orientation must be confirmed.
   - Running questions to ask collaborators are tracked in
     `docs/OPEN_QUESTIONS.md`.

3. **Dec 3 trial sequence exported**
   - Source: `Haptic_Stim_session1_log/cmd_config_1_Dec3rd.json`
   - Output: `analysis/outputs/dec3/dec3_condition_sequence.csv`
   - Trial 1 starts at recording time `1540.0 s`.
   - Trial 1200 starts at recording time `8734.0 s`.
   - Six conditions, 200 repeats each:
     - `amp100_freq5`
     - `amp100_freq26`
     - `amp180_freq5`
     - `amp180_freq26`
     - `amp250_freq5`
     - `amp250_freq26`

4. **LFP extracted**
   - Source: `amplifier.dat`, 20 kHz, 128 channels.
   - Output: `amplifier.lfp`, 1250 Hz, 128 channels.
   - Raw `amplifier.dat` was not modified.
   - Summary: `analysis/outputs/dec3/lfp_extraction_summary.json`

## Current Step

5. **Event-aligned LFP analysis**
   - Use `dec3_condition_sequence.csv` as the condition/timing source of truth.
   - Use `amplifier.lfp` for lower-rate event-aligned field-potential analysis.
   - Compare baseline, stimulation, and recovery windows across the six conditions.

## Kilosort/Pynapple Setup

Added:

- `docs/KILOSORT_PYNAPPLE_PLAN.md`
- `analysis/envs/kilosort4_dec3_gpu.yml`
- `analysis/envs/setup_kilosort4_dec3_gpu.sh`
- `analysis/modal_kilosort_dec3.py`
- `analysis/stage_dec3_for_modal.sh`
- `analysis/export_pynapple_dec3.py`

Created clean conda env:

```bash
conda activate kilosort4-dec3
```

Verified:

- `kilosort 4.1.7`
- `spikeinterface 0.104.3`
- `probeinterface 0.3.2`
- `phylib 2.7.0`
- `pynapple 0.11.3`
- `torch 2.2.2`
- `numpy 1.26.4`
- `numba 0.65.1`
- `llvmlite 0.47.0`
- `torch.cuda.is_available() == False` on this Mac
- `import kilosort` works

Exported Pynapple intervals:

```bash
python analysis/export_pynapple_dec3.py
```

Outputs:

- `analysis/outputs/dec3/pynapple_intervals/`
- baseline: `1540 s`
- ON intervals: `1200`, total `3600 s`
- OFF-control intervals: `1200`, total `3600 s`

Interpretation:

- The local Mac environment is suitable for Kilosort setup and GUI/probe sanity
  checks.
- Full Dec 3 spike sorting should be run on an NVIDIA CUDA workstation.
- Modal can be used as that GPU workstation under the local `pardis-stanford`
  profile. The prepared Modal workflow stages the 51 GB raw file to the
  `dec3-kilosort-data` Volume, checks an `A10G` CUDA image, and then runs
  Kilosort4.

## Event-Aligned LFP First Pass

Command:

```bash
python analysis/event_aligned_lfp.py \
  --lfp "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.lfp" \
  --sequence analysis/outputs/dec3/dec3_condition_sequence.csv \
  --output-dir analysis/outputs/dec3/event_aligned_lfp \
  --n-channels 128 \
  --sample-rate-hz 1250 \
  --pre-s 1 \
  --post-s 4 \
  --max-trials-per-condition 50
```

Outputs:

- `analysis/outputs/dec3/event_aligned_lfp/condition_channel_lfp_summary.csv`
- `analysis/outputs/dec3/event_aligned_lfp/channel_lfp_response_ranking.csv`
- `analysis/outputs/dec3/event_aligned_lfp/condition_by_channel_lfp_response_heatmap.png`
- `analysis/outputs/dec3/event_aligned_lfp/condition_average_lfp_collapsed.png`
- `analysis/outputs/dec3/event_aligned_lfp/index.html`
- Per-condition mean traces: `*_mean_lfp.npz`

First-pass interpretation:

- This is exploratory only. It does **not** remove stimulation artifacts and does
  **not** median-subtract channels.
- The numeric metric is `mean(abs(LFP)) during stimulation window` minus
  `mean(abs(LFP)) during the 1 s pre-window`.
- 26 Hz conditions show larger average LFP amplitude increases than 5 Hz
  conditions in this first pass.
- The largest condition-level increase was `amp180_freq26`, followed by
  `amp100_freq26` and `amp250_freq26`.
- The strongest channel responses were concentrated around low-numbered channels,
  especially channels `5-10`, with channel `7` ranked highest in the first-pass
  response table.

Important caveat:

- The all-channel collapsed trace plot is noisy and is not the best visualization.
  The heatmap and channel-wise summaries are more useful. Next plotting should
  separate shanks/channels and should consider stimulation-artifact handling.

## Improved LFP Condition Visualizations

The overlaid LFP traces made condition differences hard to see, so a second
summary plotting step was added:

```bash
python analysis/plot_lfp_condition_summary.py \
  --summary-csv analysis/outputs/dec3/event_aligned_lfp/condition_channel_lfp_summary.csv \
  --output-dir analysis/outputs/dec3/event_aligned_lfp/condition_summary_plots
```

Outputs:

- `analysis/outputs/dec3/event_aligned_lfp/condition_summary_plots/index.html`
- `lfp_response_grouped_bars.png`
- `lfp_frequency_difference_by_shank.png`
- `lfp_condition_shank_heatmap_values.png`

Interpretation from these plots:

- 26 Hz responses are larger than 5 Hz responses on most shanks/amplitudes.
- The 26 Hz minus 5 Hz difference is largest at amplitude `180`.
- Shank 4 (`0-31`) shows the strongest frequency effect in this metric.
- These plots use the same exploratory `stim mean |LFP| - pre mean |LFP|`
  metric, so artifact handling still needs to be addressed before final claims.

## Artifact-Aware LFP Check

The next pass separated onset, sustained stimulation, offset, and recovery
windows. It excluded the first and last 100 ms of the stimulation period from
the sustained metric.

Command:

```bash
python analysis/artifact_aware_lfp.py \
  --lfp "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.lfp" \
  --sequence analysis/outputs/dec3/dec3_condition_sequence.csv \
  --output-dir analysis/outputs/dec3/artifact_aware_lfp \
  --n-channels 128 \
  --sample-rate-hz 1250 \
  --pre-s 1 \
  --post-s 4 \
  --artifact-margin-s 0.1 \
  --max-trials-per-condition 100
```

Outputs:

- `analysis/outputs/dec3/artifact_aware_lfp/index.html`
- `artifact_aware_lfp_summary.csv`
- `artifact_window_comparison.png`
- `sustained_response_by_shank.png`

Interpretation:

- Offset windows can be large, especially for the `180 / 26 Hz` condition, so
  stimulation transition artifacts are real and should be considered.
- The sustained response, excluding 100 ms around onset and offset, still shows
  `180 / 26 Hz` as the strongest condition across shanks.
- `250` amplitude responses are weaker than `180` in this metric, suggesting the
  amplitude-response relationship is not simply monotonic.
- This still uses LFP amplitude summaries. A frequency-domain analysis should be
  done next to ask whether 5 Hz and 26 Hz responses are entrained at the stimulus
  frequency.

## Frequency-Specific LFP

Command:

```bash
python analysis/frequency_lfp.py \
  --lfp "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.lfp" \
  --sequence analysis/outputs/dec3/dec3_condition_sequence.csv \
  --output-dir analysis/outputs/dec3/frequency_lfp \
  --n-channels 128 \
  --sample-rate-hz 1250 \
  --window-duration-s 2.8 \
  --artifact-margin-s 0.1 \
  --band-half-width-hz 1.0 \
  --max-trials-per-condition 200
```

Outputs:

- `analysis/outputs/dec3/frequency_lfp/index.html`
- `frequency_lfp_channel_summary.csv`
- `frequency_lfp_group_summary.csv`
- `frequency_lfp_physical_shank_summary.csv`
- `driven_power_change_by_analysis_group.png`
- `driven_power_change_by_physical_shank.png`
- `driven_power_change_by_channel.png`
- `frequency_specificity_by_group.png`

Method:

- Uses `amplifier.lfp` at 1250 Hz.
- Compares a 2.8 s pre window immediately before trial onset with a 2.8 s
  stimulation window beginning 0.1 s after onset.
- Reports `log2(stim power / pre power)` around the driven frequency.
- Driven frequency is 5 Hz for `*_freq5` and 26 Hz for `*_freq26`.
- Channel labels remain conservative:
  - analysis groups: `0-31`, `32-63`, `64-95`, `96-127`
  - physical shanks: `0-63` and `64-127`

Interpretation:

- The strongest group-level driven-frequency increase is `amp180_freq5`.
- `amp180_freq5` is positive across all four 32-channel analysis groups
  (mean log2 changes about `0.12-0.15`).
- The 26 Hz conditions do not show a broad positive 26 Hz power increase in this
  metric. `amp100_freq26` is close to zero, while `amp180_freq26` and
  `amp250_freq26` are negative on average.
- This suggests the large broadband/absolute-LFP response seen in earlier plots
  may include non-frequency-specific transients, offsets, or slower amplitude
  effects rather than clean 26 Hz entrainment.
- Next check: inspect trial-averaged spectrograms or time-frequency maps around
  onset/off periods to see whether 26 Hz power is brief/transient, phase-locked
  but low-power, or masked by artifacts/reference choices.

## Time-Frequency LFP

Command:

```bash
python analysis/time_frequency_lfp.py \
  --lfp "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.lfp" \
  --sequence analysis/outputs/dec3/dec3_condition_sequence.csv \
  --output-dir analysis/outputs/dec3/time_frequency_lfp \
  --n-channels 128 \
  --sample-rate-hz 1250 \
  --pre-s 1 \
  --post-s 4 \
  --nperseg 512 \
  --noverlap 448 \
  --max-freq-hz 80 \
  --max-trials-per-condition 200
```

Outputs:

- `analysis/outputs/dec3/time_frequency_lfp/index.html`
- `time_frequency_condition_grid.png`
- `driven_frequency_timecourses.png`
- `time_frequency_summary.csv`
- `time_frequency_group_maps.npz`

Method:

- Trial window is `-1` to `+4 s` around stimulation onset.
- Spectrograms are computed from the channel-average trace within each
  32-channel analysis group, then averaged across trials.
- Maps report `log2(power / pre-stim baseline)` per frequency.
- Driven-band summaries use `frequency ± 1 Hz`.

Interpretation:

- `amp100_freq26` shows a positive sustained 26 Hz-band increase across analysis
  groups, and a stronger increase in the offset window.
- `amp180_freq26` is near zero/negative during sustained stimulation but positive
  around offset.
- `amp250_freq26` is strongly negative in the sustained 26 Hz-band metric.
- 5 Hz conditions are mixed: `amp180_freq5` and `amp250_freq5` show positive
  sustained driven-band values, while `amp100_freq5` is negative.
- This supports the idea that the 26 Hz response is condition-dependent and
  partly time-locked to transitions/off periods, not simply sustained positive
  entrainment for every 26 Hz amplitude.
- The current STFT settings are a first pass. For final claims, rerun or compare
  with a frequency-resolution-focused setting around 5/26 Hz and with reference
  choices/bad-channel exclusions finalized.

## Reference / Bad-Channel Sensitivity

Bad-channel candidate config:

- `analysis/bad_channels_dec3.json`
- Candidate channels excluded for this sensitivity pass:
  `5, 6, 7, 32, 33, 34, 43, 66, 67`
- These are not final definite bad channels; they are automated-QC review
  candidates.

Command:

```bash
python analysis/reference_sensitivity_lfp.py \
  --lfp "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.lfp" \
  --sequence analysis/outputs/dec3/dec3_condition_sequence.csv \
  --output-dir analysis/outputs/dec3/reference_sensitivity_lfp \
  --bad-channels-json analysis/bad_channels_dec3.json \
  --bad-channel-field candidate_bad_channels \
  --n-channels 128 \
  --sample-rate-hz 1250 \
  --window-duration-s 2.8 \
  --artifact-margin-s 0.1 \
  --band-half-width-hz 1.0 \
  --max-trials-per-condition 200
```

Outputs:

- `analysis/outputs/dec3/reference_sensitivity_lfp/index.html`
- `reference_condition_summary.png`
- `reference_group_heatmaps.png`
- `reference_sensitivity_condition_summary.csv`
- `reference_sensitivity_group_summary.csv`

Interpretation:

- `amp180_freq5` remains the strongest driven-frequency condition under all
  reference choices:
  - raw: `0.136`
  - physical-shank median: `0.126`
  - analysis-group median: `0.124`
- `amp100_freq26` improves with median referencing and becomes positive:
  - raw: `-0.013`
  - physical-shank median: `0.033`
  - analysis-group median: `0.043`
- `amp180_freq26` remains near-zero/negative under all three reference choices.
- `amp250_freq26` remains negative under all three reference choices.
- This supports the previous conclusion that the clearest driven-frequency
  power response is `180 / 5 Hz`. Among 26 Hz stimulation conditions,
  `100 / 26 Hz` currently has the largest positive 26 Hz-band power change under
  the tested preprocessing, not `180 / 26 Hz`.

## Phase-Locking / Entrainment

Command:

```bash
python analysis/phase_locking_lfp.py \
  --lfp "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.lfp" \
  --sequence analysis/outputs/dec3/dec3_condition_sequence.csv \
  --output-dir analysis/outputs/dec3/phase_locking_lfp \
  --bad-channels-json analysis/bad_channels_dec3.json \
  --bad-channel-field candidate_bad_channels \
  --reference-mode analysis_group_median \
  --n-channels 128 \
  --sample-rate-hz 1250 \
  --pre-s 1 \
  --post-s 4 \
  --band-half-width-hz 1.5 \
  --max-trials-per-condition 200
```

Outputs:

- `analysis/outputs/dec3/phase_locking_lfp/index.html`
- `plv_timecourses.png`
- `plv_condition_summary.png`
- `plv_sustained_minus_pre.png`
- `phase_locking_summary.csv`

Method:

- Uses trial-to-trial phase-locking value (PLV) at the driven frequency.
- 5 Hz conditions are filtered around 5 Hz; 26 Hz conditions around 26 Hz.
- PLV is computed across trials, aligned to stimulation onset.
- Candidate bad channels are excluded and `analysis_group_median` reference is
  used, matching the current sensitivity pass.

Interpretation:

- No condition shows a large sustained PLV increase over the pre-stim baseline.
- Condition-mean sustained-minus-pre PLV values are small:
  - `amp180_freq5`: `0.005`
  - `amp180_freq26`: `-0.001`
  - `amp250_freq5`: `-0.001`
  - `amp100_freq26`: `-0.004`
  - `amp250_freq26`: `-0.010`
  - `amp100_freq5`: `-0.013`
- Baseline and sustained PLV values are around `0.05-0.07`, close to the
  expected finite-trial floor for 200 trials rather than strong entrainment.
- Current conclusion: the Dec 3 LFP has condition-dependent amplitude/power
  responses, but this first PLV pass does not show strong trial-to-trial
  phase-locking to the stimulus rhythm.

## Trial-Level Bootstrap Statistics

Command:

```bash
python analysis/trial_level_stats_dec3.py \
  --lfp "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.lfp" \
  --sequence analysis/outputs/dec3/dec3_condition_sequence.csv \
  --output-dir analysis/outputs/dec3/trial_level_stats_equal_spectral_windows \
  --bad-channels-json analysis/bad_channels_dec3.json \
  --bad-channel-field candidate_bad_channels \
  --reference-mode analysis_group_median \
  --n-channels 128 \
  --sample-rate-hz 1250 \
  --pre-s 1 \
  --post-s 4 \
  --artifact-margin-s 0.1 \
  --spectral-window-s 2.8 \
  --band-half-width-hz 1.0 \
  --n-bootstrap 2000
```

Outputs:

- `analysis/outputs/dec3/trial_level_stats_equal_spectral_windows/index.html`
- `condition_summary_ci.csv`
- `trial_level_summary_ci.csv`
- `trial_level_metrics.csv`
- `sustained_broadband_ci.png`
- `offset_broadband_ci.png`
- `driven_power_ci.png`

Important correction:

- The first trial-level stats attempt used unequal pre/stim spectral windows.
  The linked result above is the corrected version using equal 2.8 s spectral
  windows.

Interpretation:

- `amp180_freq26` has reliable positive trial-level sustained broadband response:
  `6.65 [2.93, 10.71]`.
- `amp180_freq26` also has reliable positive offset broadband response:
  `12.58 [5.51, 20.04]`.
- `amp250_freq26` has reliable positive offset broadband response:
  `7.69 [1.00, 14.33]`.
- Driven-frequency power confidence intervals cross zero for all conditions in
  the corrected trial-level analysis.
- This makes the broadband/transition story more statistically stable than the
  driven-frequency power story at the current preprocessing stage.

## Focused Broadband Transition Analysis

Command:

```bash
python analysis/broadband_transition_stats_dec3.py \
  --lfp "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.lfp" \
  --sequence analysis/outputs/dec3/dec3_condition_sequence.csv \
  --output-dir analysis/outputs/dec3/broadband_transition \
  --bad-channels-json analysis/bad_channels_dec3.json \
  --bad-channel-field candidate_bad_channels \
  --reference-mode analysis_group_median \
  --n-channels 128 \
  --sample-rate-hz 1250 \
  --pre-s 1 \
  --post-s 4 \
  --artifact-margin-s 0.1 \
  --n-bootstrap 2000
```

Outputs:

- `analysis/outputs/dec3/broadband_transition/index.html`
- `broadband_windows_condition_ci.png`
- `transition_index_condition.png`
- `broadband_window_group_heatmaps.png`
- `broadband_transition_condition_summary_ci.csv`
- `broadband_transition_group_summary_ci.csv`
- `broadband_transition_trial_metrics.csv`

Interpretation:

- `amp180_freq26` has reliable positive sustained broadband response:
  `6.65 [2.91, 10.37]`.
- `amp180_freq26` has reliable positive offset broadband response:
  `12.58 [5.97, 19.52]`.
- `amp180_freq26` has reliable positive recovery broadband response:
  `8.37 [2.95, 14.00]`.
- `amp250_freq26` has a reliable positive offset broadband response:
  `7.69 [0.93, 14.22]`.
- `amp250_freq26` has a reliable positive transition index:
  `6.71 [1.14, 12.19]`, meaning offset is larger than sustained response.
- Onset windows are negative for `amp180_freq26` and `amp250_freq26`, so the
  result is not simply a positive onset artifact.
- Current strongest biological story: 26 Hz stimulation produces an
  amplitude-dependent broadband/transition response. `180 / 26 Hz` has a
  sustained-plus-offset response, while `250 / 26 Hz` is specifically
  offset-heavy.

## 3-Second OFF Control

Command:

```bash
python analysis/off_control_broadband_dec3.py \
  --lfp "/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.lfp" \
  --sequence analysis/outputs/dec3/dec3_condition_sequence.csv \
  --output-dir analysis/outputs/dec3/off_control_broadband \
  --bad-channels-json analysis/bad_channels_dec3.json \
  --bad-channel-field candidate_bad_channels \
  --reference-mode analysis_group_median \
  --n-channels 128 \
  --sample-rate-hz 1250 \
  --margin-s 0.1 \
  --n-bootstrap 2000
```

Outputs:

- `analysis/outputs/dec3/off_control_broadband/index.html`
- `off_control_condition_ci.png`
- `off_control_group_heatmaps.png`
- `off_control_condition_summary_ci.csv`

Method:

- Uses the full 3 s OFF period as within-trial control.
- ON window: `0.1-2.9 s`.
- OFF window: `3.1-5.9 s`.
- `ON - OFF` tests whether the response is larger during active stimulation
  than the immediate within-trial control period.

Interpretation:

- `amp180_freq26` is elevated during ON:
  `6.65 [2.93, 10.71]`.
- `amp180_freq26` is also elevated during OFF:
  `8.79 [4.82, 12.87]`.
- `amp180_freq26` ON-minus-OFF crosses zero:
  `-2.14 [-5.40, 1.09]`.
- ON-minus-OFF crosses zero for every condition.
- Conclusion: using the 3 s OFF period as control, the reliable broadband effect
  is not ON-only; it persists into OFF/recovery.

## TTL ON/OFF Audit

Files checked:

- Recording folder TTL-like file: `digitalin.dat`
- Haptic log/config files: `log_dec3rd`, `cmd_config_1_Dec3rd.json`,
  `generate_randomized_sequence_Dec3rd.py`

Command:

```bash
python analysis/ttl_on_off_audit_dec3.py \
  --sequence analysis/outputs/dec3/dec3_condition_sequence.csv \
  --edges-csv analysis/outputs/dec3/digital_edges_ch7.csv \
  --output-dir analysis/outputs/dec3/ttl_on_off_audit \
  --sample-rate-hz 20000 \
  --margin-s 0.0
```

Outputs:

- `analysis/outputs/dec3/ttl_on_off_audit/index.html`
- `ttl_on_off_counts.png`
- `ttl_on_off_trial_audit.csv`
- `ttl_on_off_condition_summary.csv`

Findings:

- Bit 7 is the usable digital transition channel.
- Total ON-window rising edges: `7878`.
- Total OFF-window rising edges: `1260`.
- Trials with at least one ON-window edge: `1173 / 1200`.
- Trials with at least one OFF-window edge: `791 / 1200`.
- TTL activity is denser during expected ON than OFF, but it is not a clean
  one-edge-per-trial marker. Keep using the schedule CSV for trial labels and
  TTL as QC.

## Trial-Order / Adaptation Analysis

Command:

```bash
python analysis/adaptation_analysis_dec3.py \
  --trial-metrics analysis/outputs/dec3/off_control_broadband/off_control_trial_metrics.csv \
  --output-dir analysis/outputs/dec3/adaptation_analysis \
  --rolling-window 15 \
  --n-bootstrap 2000
```

Outputs:

- `analysis/outputs/dec3/adaptation_analysis/index.html`
- `adaptation_timecourses.png`
- `adaptation_epoch_summary.png`
- `adaptation_slope_summary.png`
- `adaptation_epoch_summary_ci.csv`
- `adaptation_slope_summary.csv`

Interpretation:

- `amp250_freq26` adapts downward strongly:
  - ON slope per 100 repeats: `-9.90`, p=`0.0059`
  - OFF slope per 100 repeats: `-10.64`, p=`0.0107`
- `amp180_freq26` shows a weaker trend toward OFF dominance:
  - ON-OFF slope per 100 repeats: `-5.10`, p=`0.0692`
  - late ON-OFF mean: `-5.87 [-10.95, -1.02]`
- `amp180_freq5` OFF response increases across repeats:
  - OFF slope per 100 repeats: `8.89`, p=`0.0435`
- Current interpretation: the 26 Hz broadband response has recovery/adaptation
  dynamics. `180 / 26 Hz` becomes more OFF-dominant late in the session, while
  `250 / 26 Hz` declines over repeats.

## Spike-Sorting Prep

Command:

```bash
python analysis/prepare_spike_sorting_dec3.py
```

Outputs:

- `analysis/outputs/dec3/spike_sorting_prep/README.md`
- `analysis/outputs/dec3/spike_sorting_prep/spike_sorting_plan.md`
- `analysis/outputs/dec3/spike_sorting_prep/channel_metadata.csv`
- `analysis/outputs/dec3/spike_sorting_prep/bad_channels.txt`
- `analysis/outputs/dec3/spike_sorting_prep/good_channels.txt`
- `analysis/outputs/dec3/spike_sorting_prep/kilosort_channel_map.mat`
- `analysis/outputs/dec3/spike_sorting_prep/phy_params.py`
- `analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv`
- `analysis/outputs/dec3/spike_sorting_prep/stim_artifact_intervals.csv`

Status:

- Raw `amplifier.dat` was not modified or copied.
- Channel count: `128`.
- Confirmed bad channels: `5, 6, 7, 32, 33, 34, 43, 66, 67`.
- Connected/good channels: `119`.
- The current Python environment does not have `kilosort`, `spikeinterface`,
  `probeinterface`, or `phylib` installed.
- `kilosort_channel_map.mat` uses provisional two-shank geometry:
  channels `0-63` = physical shank A, channels `64-127` = physical shank B.
- Replace provisional geometry with the exact Cambridge NeuroTech `H12_2` map
  before final spike-sorting claims if possible.

## SpikeInterface Setup

Installed packages:

```bash
python -m pip install spikeinterface probeinterface phylib
```

Verification:

- `spikeinterface 0.104.3`
- `probeinterface 0.3.2`
- `phylib 2.7.0`

Command:

```bash
python analysis/setup_spikeinterface_dec3.py
```

Outputs:

- `analysis/outputs/dec3/spikeinterface_setup/README.md`
- `analysis/outputs/dec3/spikeinterface_setup/recording_json/recording.json`
- `analysis/outputs/dec3/spikeinterface_setup/spikeinterface_trace_sanity.png`
- `analysis/outputs/dec3/spikeinterface_setup/spikeinterface_setup_summary.json`

Result:

- SpikeInterface can open raw `amplifier.dat` lazily.
- Raw frames: `212,888,704`.
- Duration: `10,644.4352 s`.
- Good channels after bad-channel exclusion: `119`.
- Raw data was not modified or copied.

Sorter backend status:

- Installed/runnable backends detected by SpikeInterface:
  `lupin`, `simple`, `spykingcircus2`, `tridesclous2`.
- Kilosort wrappers are known to SpikeInterface but Kilosort itself is not
  installed/runnable in this environment yet.

Dry-run command:

```bash
python analysis/run_spikeinterface_test_sort_dec3.py --sorter tridesclous2
```

Dry-run output:

- `analysis/outputs/dec3/spikeinterface_test_sort/README.md`
- `analysis/outputs/dec3/spikeinterface_test_sort/test_sort_summary.json`
- Segment planned: `1540-1570 s`.
- Sorter: `tridesclous2`.
- Run requested: `false`.

Smoke-test command:

```bash
python analysis/run_spikeinterface_test_sort_dec3.py --sorter tridesclous2 --run
```

Smoke-test result:

- Completed successfully on the 30 s segment `1540-1570 s`.
- Output folder:
  `analysis/outputs/dec3/spikeinterface_test_sort/tridesclous2/`
- Unit count returned: `103`.
- This is not curated and not biology-ready; it only verifies the sorting
  pipeline can run.
- Warnings:
  - mixed Intel/LLVM OpenMP libraries were detected;
  - SpikeInterface emitted dummy-probe warnings despite provisional locations.
- Recommendation before full-session sorting: use a dedicated sorting
  environment and exact H12_2 geometry, preferably with Kilosort if available.

## Modal Kilosort4 Full-Session Run

Command flow:

```bash
./analysis/stage_dec3_for_modal.sh
modal run analysis/modal_kilosort_dec3.py --action check
modal run analysis/modal_kilosort_dec3.py --action run
modal volume get --force dec3-kilosort-data /dec3/kilosort4_results \
  analysis/outputs/dec3/modal_kilosort4_results
```

Run URL:

- `https://modal.com/apps/pardis-stanford/main/ap-98jIARtjd6sXnqLgEOCynL`

Environment check before sorting:

- Kilosort: `4.1.7`
- Torch: `2.2.2+cu118`
- CUDA device: `NVIDIA A10`
- Raw file on Modal: `50.757 GiB`
- Probe map loaded with `128` channels

Run result:

- Completed successfully.
- Local output:
  `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/`
- Runner elapsed time: `3165.96 s`
- Kilosort reported runtime: `3068.10 s`
- Total units: `194`
- Kilosort good refractory-period units: `28`
- Final Kilosort summary spikes: `7,311,421`
- Runner summary spikes: `7,370,558`
- Mean absolute drift: `0.8 um`

Runtime by Kilosort step:

- preprocessing: `48.6 s`
- drift correction: `860.2 s`
- spike detection with universal templates: `865.0 s`
- first clustering: `196.6 s`
- spike detection with learned templates: `287.6 s`
- final clustering: `659.3 s`
- cluster merge: `5.9 s`
- postprocessing/export: `91.8 s`

Caveat:

- This is a first full-session Kilosort4 pass with provisional H12_2/two-shank
  geometry and the current confirmed bad-channel exclusions. It is ready for
  Phy inspection and downstream trial-aligned exploratory analysis, but not yet
  final for anatomical claims.

## Provisional Kilosort Spike PETH / ON-vs-OFF Analysis

Command:

```bash
python analysis/export_kilosort_pynapple_dec3.py
python analysis/spike_peth_on_off_dec3.py
```

Output:

- `analysis/outputs/dec3/pynapple_spikes/kilosort_all_units_tsgroup.npz`
- `analysis/outputs/dec3/pynapple_spikes/kilosort_ks_good_units_tsgroup.npz`
- `analysis/outputs/dec3/spike_peth_on_off/index.html`
- `analysis/outputs/dec3/spike_peth_on_off/condition_summary_on_off.csv`
- `analysis/outputs/dec3/spike_peth_on_off/unit_condition_on_off_stats.csv`
- `analysis/outputs/dec3/spike_peth_on_off/top_units_by_condition_delta.csv`
- `analysis/outputs/dec3/spike_peth_on_off/peth_onset_ks_good_units.png`
- `analysis/outputs/dec3/spike_peth_on_off/peth_offset_ks_good_units.png`
- `analysis/outputs/dec3/spike_peth_on_off/unit_condition_on_minus_off_heatmap_ks_good.png`

Run summary:

- Spikes analyzed: `7,311,421`
- Clusters analyzed: `194`
- KS-good clusters: `28`
- Trials: `1200`
- Control: each trial's 3 s OFF interval immediately after stimulation.
- Pynapple export: `TsGroup` files for all units and KS-good units.
- Pynapple sanity check: KS-good `TsGroup.count(3.0, ep=all_on_intervals)`
  returns a `1200 x 28` `TsdFrame`.

Condition-average ON-minus-OFF firing-rate deltas across KS-good clusters:

- `amp100_freq26`: `+0.041 Hz`
- `amp100_freq5`: `-0.112 Hz`
- `amp180_freq26`: `-0.148 Hz`
- `amp180_freq5`: `-0.141 Hz`
- `amp250_freq26`: `-0.199 Hz`
- `amp250_freq5`: `-0.238 Hz`

Statistical result:

- No KS-good cluster/condition pair survives BH correction at `q < 0.05`.
- Three MUA-labeled cluster/condition pairs survive `q < 0.05`, all with
  `ON < OFF`.
- The largest positive `amp180_freq26` ON-minus-OFF spike effects are
  MUA-labeled, not KS-good.

Interpretation:

- This uncurated first pass does not support a simple clean-unit firing-rate
  increase during stimulation ON.
- It strengthens the need for Phy curation before biological spike claims.
- It also suggests the LFP broadband/recovery result may not correspond to a
  simple increase in KS-good unit firing during ON.

## Phy Setup Attempt

Commands:

```bash
conda create -y -n phy-dec3 python=3.11 pip
conda run -n phy-dec3 python -m pip install --upgrade git+https://github.com/cortex-lab/phy.git
conda run -n phy-dec3 phy --version
conda run --no-capture-output -n phy-dec3 phy template-describe params.py
```

Output:

- Phy version: `2.0b6`
- `template-gui` is available after installing Phy from GitHub.
- `template-describe` validates the Dec 3 Kilosort output and raw data path:
  - duration: `10644.4 s`
  - sample rate: `20.0 kHz`
  - raw channels: `128`
  - active channels: `119`
  - templates: `194`
  - spikes: `7,311,421`

GUI status:

- `phy template-gui --clear-state params.py` starts loading but the local
  macOS/Qt OpenGL layer rejects Phy's shader code.
- Main error pattern:
  - `Could not create view TemplateFeatureView`
  - `version '120' is not supported`
  - `#version required and missing`
  - `'varying' : syntax error`
- `QT_OPENGL=software` was also tested and gave the same shader errors.

Conclusion:

- Phy/Kilosort file validation passes.
- Manual Phy curation is blocked by local GUI/OpenGL compatibility, not by the
  Dec 3 data.
- Spike analyses remain provisional until curation is completed on a compatible
  Phy setup.

## Conservative Phy Environment Attempt

Commands:

```bash
conda create -y -n phy-dec3-legacy python=3.10 pip
conda run -n phy-dec3-legacy python -m pip install 'numpy<2' 'scipy<1.12' 'matplotlib<3.9' h5py joblib click requests traitlets tqdm phylib qtpy 'PyOpenGL==3.1.6' 'PyQt5==5.15.10' 'PyQtWebEngine==5.15.6'
conda run -n phy-dec3-legacy python -m pip install --upgrade git+https://github.com/cortex-lab/phy.git
```

Result:

- Direct executable path works:
  `/opt/anaconda3/envs/phy-dec3-legacy/bin/phy --version`
- Version: `phy, version 2.0b6`
- Dataset validation passes with the same Dec 3 counts:
  - duration: `10644.4 s`
  - sample rate: `20.0 kHz`
  - raw channels: `128`
  - active channels: `119`
  - templates: `194`
  - spikes: `7,311,421`

GUI result:

- Best local command:

```bash
bash analysis/launch_phy_dec3_foreground.sh
```

- Foreground launch produced a visible `python` GUI process on macOS.
- The GUI still reported:
  `Could not create view TemplateFeatureView.`
- Detached/nohup launching exited silently, and AppleScript Terminal launching
  was blocked by macOS automation permissions.

Conclusion:

- The legacy env is the best local attempt so far, but it is only partially
  successful.
- If the visible Phy window contains the main views needed for curation, it can
  be used cautiously.
- For a clean complete Phy session, a Linux/remote GUI machine with compatible
  OpenGL remains the stronger path.

## Modal noVNC Phy Attempt

Script:

```bash
analysis/modal_phy_dec3.py
```

Command:

```bash
modal run analysis/modal_phy_dec3.py
```

Latest run:

- Modal app: `dec3-phy-novnc`
- Modal run URL:
  `https://modal.com/apps/pardis-stanford/main/ap-O0vVndFQm109iop2498p3B`
- noVNC URL:
  `https://ta-01kt7qere5egsvkkgaqavqrw1g-6080-g3z4bza5hovjt0iym527zpvvd.w.modal.host/vnc.html?autoconnect=true&resize=scale`

Setup:

- Reuses Modal Volume `dec3-kilosort-data`.
- Mounts volume at `/data`.
- Uses existing raw data:
  `/data/dec3/amplifier.dat`
- Uses existing Kilosort output:
  `/data/dec3/kilosort4_results`
- Writes Modal-specific Phy params:
  `/data/dec3/kilosort4_results/params_modal.py`
- Starts:
  - `Xvfb`
  - `fluxbox`
  - `x11vnc`
  - `websockify`/`noVNC`
  - `phy template-gui`

Current status:

- Modal image build succeeded.
- noVNC endpoint returned `HTTP 200`.
- Phy successfully reads the Dec 3 raw/Kilosort files on Modal:
  - duration: `10644.4 s`
  - sample rate: `20.0 kHz`
  - raw channels: `128`
  - active channels: `119`
  - templates: `194`
  - spikes: `7,311,421`
- Fixed Modal GUI dependency failures:
  - missing `libsmime3.so` fixed with `libnss3`
  - missing `libasound.so.2` fixed with `libasound2`
  - Qt `xcb` plugin failure fixed with additional X11/xcb libraries
  - QtWebEngine root/Chromium sandbox failure fixed with no-sandbox flags
- Latest launch log gets past the previous crashes. The remaining check is
  visual confirmation in the browser that the Phy windows render and respond.

Caveat:

- This is an interactive temporary Modal tunnel. It remains usable only while
  the `modal run` process is alive.
- It still requires visual confirmation in the browser that Phy fully renders
  inside the remote Linux desktop.
