# Dec 3 Results Summary

This is the readable interpretation layer for the Dec 3 haptic stimulation
analysis. The detailed run history is in `DEC3_ANALYSIS_LOG.md`; open questions
for collaborators are in `OPEN_QUESTIONS.md`.

## Provisional Final-Pass Settings

The current explicit preprocessing config is:

- `analysis/final_preprocessing_dec3.json`

It chooses:

- confirmed bad channels to exclude in this pass: `5, 6, 7, 32, 33, 34, 43, 66, 67`
- LFP reference: `analysis_group_median`
- sample rate: `1250 Hz`
- channel count: `128`

Important: the listed bad channels are now treated as **confirmed for the
current analysis pass** per user instruction. Anatomy labels are still not
assigned.

## Spike-Sorting Prep Status

Spike-sorting preparation metadata has been generated:

- `analysis/outputs/dec3/spike_sorting_prep/README.md`
- `analysis/outputs/dec3/spike_sorting_prep/spike_sorting_plan.md`
- `analysis/outputs/dec3/spike_sorting_prep/channel_metadata.csv`
- `analysis/outputs/dec3/spike_sorting_prep/kilosort_channel_map.mat`
- `analysis/outputs/dec3/spike_sorting_prep/phy_params.py`
- `analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv`
- `analysis/outputs/dec3/spike_sorting_prep/stim_artifact_intervals.csv`

Kilosort/Pynapple setup notes have been added:

- `docs/KILOSORT_PYNAPPLE_PLAN.md`
- `analysis/envs/kilosort4_dec3_gpu.yml`
- `analysis/envs/setup_kilosort4_dec3_gpu.sh`
- `analysis/modal_kilosort_dec3.py`
- `analysis/stage_dec3_for_modal.sh`
- `analysis/export_pynapple_dec3.py`

Pynapple is now installed in the current Python environment and can be used for
trial intervals, LFP feature time support, and post-Kilosort spike-train
analysis. The immediate bridge is to export Dec 3 baseline, ON, and OFF-control
epochs as Pynapple `IntervalSet` files.

A clean local Kilosort environment has been created:

- env name: `kilosort4-dec3`
- Kilosort version: `4.1.7`
- Torch version: `2.2.2`
- NumPy version: `1.26.4`
- CUDA available on this Mac: `False`
- Kilosort import: verified

This environment is appropriate for setup/GUI/probe sanity checks on this Mac.
The final full-session Kilosort run should happen on an NVIDIA CUDA workstation.
Modal is also available under the local `pardis-stanford` profile and can be
used as the GPU workstation if we want to spend Modal credits. The prepared
workflow uploads `amplifier.dat` plus spike-sorting prep to the
`dec3-kilosort-data` Modal Volume, checks an `A10G` GPU image, then launches
Kilosort4.

Pynapple Dec 3 intervals have been exported:

- `analysis/outputs/dec3/pynapple_intervals/`
- baseline: 1 interval, `1540 s`
- ON intervals: 1200 intervals, total `3600 s`
- OFF-control intervals: 1200 intervals, total `3600 s`

This prep step does **not** modify or copy the 51 GB raw `amplifier.dat`.

SpikeInterface setup has also been verified:

- `analysis/outputs/dec3/spikeinterface_setup/README.md`
- `analysis/outputs/dec3/spikeinterface_setup/recording_json/recording.json`
- `analysis/outputs/dec3/spikeinterface_setup/spikeinterface_trace_sanity.png`
- `analysis/outputs/dec3/spikeinterface_setup/spikeinterface_setup_summary.json`

SpikeInterface can open the raw binary as:

- frames: `212,888,704`
- duration: `10,644.4352 s`
- good channels: `119`

Installed SpikeInterface sorter backends currently detected:

- `tridesclous2`
- `spykingcircus2`
- `simple`
- `lupin`

Kilosort wrappers are known to SpikeInterface but are not installed/runnable in
this environment yet.

A 30-second `tridesclous2` smoke test has been run:

- script: `analysis/run_spikeinterface_test_sort_dec3.py`
- output: `analysis/outputs/dec3/spikeinterface_test_sort/`
- segment: `1540-1570 s`
- good channels: `119`
- sorter: `tridesclous2`
- unit count returned: `103`

This is only a pipeline sanity check, not curated spike sorting. Warnings during
the run included mixed OpenMP libraries and a dummy-probe warning, so a dedicated
sorting environment and exact probe geometry are recommended before full-session
sorting.

Current spike-sorting channel status:

- total channels: `128`
- confirmed bad channels: `5, 6, 7, 32, 33, 34, 43, 66, 67`
- connected/good channels: `119`
- channels `128-255` are ignored phantom channels from the old XML issue

Important: the Dec 4 two-probe recording and Vöröslakos metadata confirmed this
Dec 3 recording is the dHPC probe (Cambridge NeuroTech `H12_2`, Port A). The
probe *identity* and map source are settled; the generated Kilosort map remains a
working geometry for sorting, so exact site order and physical shank orientation
are still needed before depth/laminar/spatial claims.

## Current Working Conclusion

The Dec 3 LFP response is real, but it is not a single simple "26 Hz is always
strongest" story.

1. Broadband/event-aligned LFP amplitude points to `amp180_freq26` as the
   strongest condition. "Broadband" means the overall LFP signal got larger
   during stimulation, without asking whether that increase happened exactly at
   26 Hz.
2. Transition windows matter: offset responses are large, especially around
   26 Hz conditions, so onset/offset artifacts or transition-locked neural
   responses must be separated from sustained stimulation responses.
   - Focused broadband transition analysis shows `amp180_freq26` has reliable
     sustained, offset, and recovery broadband increases.
   - `amp250_freq26` is specifically offset-heavy, with a positive transition
     index.
   - When the full 3-second OFF period is used as a within-trial control,
     `amp180_freq26` remains elevated in OFF, so the effect is not purely
     stimulation-ON-specific; it persists into the OFF/recovery period.
   - Trial-order analysis suggests adaptation/recovery dynamics:
     `amp250_freq26` declines strongly across repeats, and late `amp180_freq26`
     trials become more OFF-dominant.
3. Frequency-specific power does not fully match the broadband result.
   - The strongest full-window driven-frequency power increase is
     `amp180_freq5`.
   - `amp100_freq26` shows sustained 26 Hz-band power in the time-frequency
     analysis.
   - `amp180_freq26` has strong broadband LFP but is near zero/negative for
     sustained 26 Hz-band power, with a positive offset-period response.
   - `amp250_freq26` is weak/negative in frequency-specific metrics.
   - Trial-level bootstrap confidence intervals for driven-frequency power cross
     zero for all conditions in the corrected equal-window analysis, so these
     power effects should be treated as suggestive rather than final.
4. The amplitude response is not monotonic. Amplitude `180` often looks stronger
   than `250`.
5. Reference/bad-channel sensitivity supports this split result.
   - After excluding the confirmed bad-channel set for this pass and testing raw,
     physical-shank median, and analysis-group median reference,
     `amp180_freq5` remains the strongest driven-frequency condition.
   - `amp100_freq26` becomes positive with median referencing.
   - `amp180_freq26` and `amp250_freq26` remain near-zero/negative in
     driven-frequency power.
6. Phase-locking does not support strong onset-locked entrainment.
   - PLV values are close to the expected finite-trial baseline.
   - No condition shows a large sustained increase in phase consistency over
     the pre-stim period.
   - True stimulus-phase locking was not directly testable because the delivered
     vibration phase was not recorded.
7. Current channel labels should remain conservative:
   - Physical Shank A: channels `0-63`
   - Physical Shank B: channels `64-127`
   - Analysis groups: `0-31`, `32-63`, `64-95`, `96-127`
   - Do not assign medial/lateral or CA1/DG labels yet.

## Key Numeric Results

## Broadband Response vs Frequency Entrainment

These are related but different questions:

| Question | What it asks | Example result |
| --- | --- | --- |
| Broadband LFP response | Did the total LFP amplitude get larger during stimulation, regardless of exact frequency? | `amp180_freq26` is strongest: sustained broadband change `53.78`. |
| Driven-frequency response / entrainment | Did power specifically increase at the stimulus frequency: 5 Hz for 5 Hz trials, 26 Hz for 26 Hz trials? | `amp180_freq26` is near zero/negative at 26 Hz: raw `-0.062`, shank median `-0.033`, group median `-0.014`. |

So the current interpretation is:

```text
amp180_freq26 causes a large overall LFP response, but that response does not
look like a clean sustained 26 Hz-following oscillation in the current metrics.
```

The current largest positive driven-frequency power changes are:

- `amp180_freq5` for 5 Hz.
- `amp100_freq26` for 26 Hz.

Here, "largest positive 26 Hz power change" means only this:

```text
Among the 26 Hz stimulation conditions, amp100_freq26 currently has the largest
positive increase in 26 Hz-band power under the chosen preprocessing.
```

It does **not** mean the result is statistically final, anatomically localized,
or strongly phase-locked.

Artifact-aware sustained broadband LFP, averaged across channels/groups:

| Condition | Sustained mean abs-LFP change |
| --- | ---: |
| `amp180_freq26` | `53.78` |
| `amp100_freq26` | `19.97` |
| `amp180_freq5` | `16.96` |
| `amp250_freq26` | `6.30` |
| `amp250_freq5` | `1.85` |
| `amp100_freq5` | `1.76` |

Full-window driven-frequency power, `log2(stim / pre)`:

| Condition | Mean driven-frequency change |
| --- | ---: |
| `amp180_freq5` | `0.135` |
| `amp100_freq26` | `-0.015` |
| `amp250_freq5` | `-0.057` |
| `amp180_freq26` | `-0.059` |
| `amp100_freq5` | `-0.083` |
| `amp250_freq26` | `-0.147` |

Time-frequency driven-band summary, `log2(power / pre baseline)`:

| Condition | Onset | Sustained | Offset |
| --- | ---: | ---: | ---: |
| `amp100_freq26` | `-0.003` | `0.091` | `0.265` |
| `amp180_freq5` | `-0.112` | `0.064` | `0.107` |
| `amp250_freq5` | `-0.128` | `0.044` | `0.056` |
| `amp180_freq26` | `-0.089` | `-0.043` | `0.142` |
| `amp100_freq5` | `-0.111` | `-0.046` | `-0.051` |
| `amp250_freq26` | `-0.349` | `-0.300` | `-0.110` |

Reference/bad-channel sensitivity, driven-frequency `log2(stim / pre)`:

| Condition | Raw | Physical-shank median | Analysis-group median |
| --- | ---: | ---: | ---: |
| `amp180_freq5` | `0.136` | `0.126` | `0.124` |
| `amp100_freq26` | `-0.013` | `0.033` | `0.043` |
| `amp250_freq5` | `-0.060` | `-0.026` | `-0.030` |
| `amp180_freq26` | `-0.062` | `-0.033` | `-0.014` |
| `amp100_freq5` | `-0.082` | `-0.100` | `-0.105` |
| `amp250_freq26` | `-0.144` | `-0.131` | `-0.133` |

Phase-locking value (PLV), sustained minus pre:

| Condition | Sustained minus pre PLV |
| --- | ---: |
| `amp180_freq5` | `0.005` |
| `amp180_freq26` | `-0.001` |
| `amp250_freq5` | `-0.001` |
| `amp100_freq26` | `-0.004` |
| `amp250_freq26` | `-0.010` |
| `amp100_freq5` | `-0.013` |

Interpretation: these PLV changes are tiny. The PLV analysis does not show
strong trial-onset-aligned phase consistency at 5 Hz or 26 Hz. It should not be
overstated as a definitive stimulus-phase test because the delivered vibration
phase was not recorded.

Trial-level bootstrap confidence intervals, corrected equal spectral windows:

| Condition | Sustained broadband mean [95% CI] | Offset broadband mean [95% CI] | Driven power mean [95% CI] |
| --- | ---: | ---: | ---: |
| `amp100_freq5` | `1.60 [-2.98, 6.17]` | `4.92 [-1.75, 12.01]` | `-0.082 [-0.225, 0.058]` |
| `amp180_freq5` | `-0.34 [-4.80, 3.98]` | `2.23 [-4.56, 9.39]` | `0.051 [-0.083, 0.188]` |
| `amp250_freq5` | `0.58 [-4.09, 4.81]` | `-0.28 [-7.12, 6.63]` | `-0.042 [-0.204, 0.112]` |
| `amp100_freq26` | `3.27 [-1.23, 7.73]` | `1.33 [-5.09, 8.14]` | `0.076 [-0.053, 0.198]` |
| `amp180_freq26` | `6.65 [2.93, 10.71]` | `12.58 [5.51, 20.04]` | `-0.045 [-0.169, 0.077]` |
| `amp250_freq26` | `0.98 [-3.33, 5.02]` | `7.69 [1.00, 14.33]` | `-0.036 [-0.162, 0.085]` |

Interpretation: at the trial level, the most reliable effects are broadband:
`amp180_freq26` has positive sustained and offset broadband CIs, and
`amp250_freq26` has a positive offset broadband CI. Driven-frequency power CIs
cross zero for all conditions.

Focused broadband transition analysis:

| Condition | Onset | Sustained | Offset | Recovery | Transition index |
| --- | ---: | ---: | ---: | ---: | ---: |
| `amp180_freq26` | `-7.71 [-13.17, -2.47]` | `6.65 [2.91, 10.37]` | `12.58 [5.97, 19.52]` | `8.37 [2.95, 14.00]` | `5.93 [-0.14, 12.17]` |
| `amp250_freq26` | `-12.47 [-18.94, -5.39]` | `0.98 [-2.92, 4.96]` | `7.69 [0.93, 14.22]` | `2.68 [-2.80, 8.18]` | `6.71 [1.14, 12.19]` |
| `amp100_freq26` | `1.37 [-5.82, 9.18]` | `3.27 [-1.36, 7.36]` | `1.33 [-5.34, 8.32]` | `6.41 [0.73, 12.26]` | `-1.94 [-7.58, 3.56]` |

Interpretation: the most supported biological story is a 26 Hz, amplitude-
dependent broadband response. `180 / 26 Hz` produces a sustained-plus-offset
response, while `250 / 26 Hz` is more specifically offset/transition-heavy.
The onset window is negative for `180 / 26 Hz` and `250 / 26 Hz`, so this is
not simply a positive onset artifact.

3-second OFF period as within-trial control:

| Condition | ON vs pre | OFF vs pre | ON - OFF |
| --- | ---: | ---: | ---: |
| `amp100_freq5` | `1.60 [-2.98, 6.17]` | `2.78 [-1.70, 7.34]` | `-1.19 [-4.77, 2.79]` |
| `amp180_freq5` | `-0.34 [-4.80, 3.98]` | `1.67 [-3.11, 6.90]` | `-2.01 [-5.28, 1.39]` |
| `amp250_freq5` | `0.58 [-4.09, 4.81]` | `0.66 [-4.49, 5.39]` | `-0.08 [-3.24, 2.93]` |
| `amp100_freq26` | `3.27 [-1.23, 7.73]` | `2.21 [-2.82, 7.08]` | `1.06 [-2.24, 4.40]` |
| `amp180_freq26` | `6.65 [2.93, 10.71]` | `8.79 [4.82, 12.87]` | `-2.14 [-5.40, 1.09]` |
| `amp250_freq26` | `0.98 [-3.33, 5.02]` | `2.05 [-2.77, 6.64]` | `-1.07 [-4.45, 2.30]` |

Interpretation: the 3-second OFF period is a valid within-trial control, and it
shows that the clearest `amp180_freq26` broadband effect carries into OFF. The
ON-minus-OFF confidence interval crosses zero for all conditions, so the current
result is better described as a sustained/recovery broadband state change than
as an ON-only response.

TTL audit from `digitalin.dat` bit 7:

- `digitalin.dat` is the only TTL-like recording file found in the Intan session
  folder.
- Bit 7 has the usable digital transitions.
- Across expected Dec 3 trial windows:
  - total ON-window rising edges: `7878`
  - total OFF-window rising edges: `1260`
  - trials with at least one ON-window edge: `1173 / 1200`
  - trials with at least one OFF-window edge: `791 / 1200`
- TTL activity is much denser during expected ON than OFF, but it is not a clean
  one-edge-per-trial marker, so the schedule CSV remains the trial-label source
  and TTL is used as QC.

Trial-order / adaptation analysis:

| Condition | ON slope / 100 repeats | OFF slope / 100 repeats | ON-OFF slope / 100 repeats | Interpretation |
| --- | ---: | ---: | ---: | --- |
| `amp180_freq26` | `-3.42` | `1.68` | `-5.10` | ON weakens relative to OFF; late trials are OFF-dominant. |
| `amp250_freq26` | `-9.90` | `-10.64` | `0.75` | Strong downward adaptation in both ON and OFF. |
| `amp180_freq5` | `5.25` | `8.89` | `-3.64` | OFF response increases across repeats. |

For `amp180_freq26`, early/middle/late ON-OFF means are:

- early: `1.59 [-3.81, 7.02]`
- middle: `-2.13 [-7.89, 3.22]`
- late: `-5.87 [-10.95, -1.02]`

Interpretation: `amp180_freq26` starts with ON and OFF closer together, then
late repeats become significantly OFF-dominant. This supports a recovery/state
shift interpretation rather than a purely immediate ON response.

## Clickable Result Pages

- Overall clickable dashboard:
  `analysis/outputs/dec3/RESULTS_DASHBOARD.html`
- Provisional final-pass rerun:
  `analysis/outputs/dec3/provisional_final_pass/index.html`
- Condition-level biological interpretation:
  `analysis/outputs/dec3/condition_interpretation/index.html`
- Biological summary figures:
  `analysis/outputs/dec3/biological_summary/index.html`
- Trial-level statistics with bootstrap CIs:
  `analysis/outputs/dec3/trial_level_stats_equal_spectral_windows/index.html`
- Focused broadband transition analysis:
  `analysis/outputs/dec3/broadband_transition/index.html`
- 3-second OFF control:
  `analysis/outputs/dec3/off_control_broadband/index.html`
- TTL ON/OFF audit:
  `analysis/outputs/dec3/ttl_on_off_audit/index.html`
- Trial-order / adaptation analysis:
  `analysis/outputs/dec3/adaptation_analysis/index.html`
- Spike-sorting prep:
  `analysis/outputs/dec3/spike_sorting_prep/README.md`
- SpikeInterface setup:
  `analysis/outputs/dec3/spikeinterface_setup/README.md`
- SpikeInterface 30-second smoke sort:
  `analysis/outputs/dec3/spikeinterface_test_sort/README.md`
- Time-frequency LFP:
  `analysis/outputs/dec3/time_frequency_lfp/index.html`
- Frequency-specific LFP:
  `analysis/outputs/dec3/frequency_lfp/index.html`
- Artifact-aware LFP:
  `analysis/outputs/dec3/artifact_aware_lfp/index.html`
- Reference/bad-channel sensitivity:
  `analysis/outputs/dec3/reference_sensitivity_lfp/index.html`
- Phase-locking / PLV:
  `analysis/outputs/dec3/phase_locking_lfp/index.html`
- Event-aligned LFP:
  `analysis/outputs/dec3/event_aligned_lfp/index.html`
- Improved event-LFP condition summaries:
  `analysis/outputs/dec3/event_aligned_lfp/condition_summary_plots/index.html`
- LFP trace pages:
  `analysis/outputs/dec3/lfp_trace_pages/index.html`
- Raw trace pages:
  `analysis/outputs/dec3/channel_trace_pages/index.html`
- Analysis foundations / reading map:
  `docs/ANALYSIS_FOUNDATIONS.md`
- Provisional Kilosort spike PETH / ON-OFF analysis:
  `analysis/outputs/dec3/spike_peth_on_off/index.html`
- Pynapple spike export:
  `analysis/outputs/dec3/pynapple_spikes/README.md`

## What We Should Do Next

1. Review the biological summary figures and decide which story to pursue:
   - broadband/offset response,
   - driven-frequency power,
   - amplitude non-monotonicity,
   - or anatomy/channel-group specificity.
   - With the adaptation result, the strongest current story is
     broadband/recovery dynamics for 26 Hz stimulation.
2. Finalize bad-channel exclusion.
   - Use the corrected 128-channel XML.
   - Combine visual review with automated QC.
   - Save an explicit bad-channel list file and rerun LFP metrics using it.
3. Decide final referencing for LFP.
   - First sensitivity pass now compares raw, physical-shank median, and
     analysis-group median reference.
   - Choose one final reference strategy before making final plots/statistics.
4. Rerun time-frequency analysis with a frequency-resolution-focused setting.
   - The current STFT is a good first pass, but a narrower analysis around
     5 Hz and 26 Hz should be used before final claims.
5. Separate sustained neural response from transition response.
   - Analyze onset, sustained ON, offset, and OFF/recovery as separate endpoints.
6. Consider more rigorous stimulus-locked modeling if exact actuator cycle timing
   can be recovered from TTL/controller logs.
   - The current PLV analysis assumes trial-onset alignment is the correct phase
     reference.
7. Keep anatomy labels conservative until probe orientation is confirmed.
   - Ask collaborators the open questions in `OPEN_QUESTIONS.md`.
   - See `docs/ANALYSIS_FOUNDATIONS.md` for why the hippocampal
     electroanatomy paper makes this caution important.
8. Install/run spike sorting.
   - Spike-sorting prep and SpikeInterface setup are ready.
   - `spikeinterface`, `probeinterface`, and `phylib` are installed.
   - Current installed sorter backends include `tridesclous2` and
     `spykingcircus2`.
   - A 30-second `tridesclous2` smoke test completed and returned `103` units.
   - Full-session Kilosort4 completed on Modal using an NVIDIA A10 GPU.
   - Local Kilosort4 output:
     `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/`
   - Run summary:
     - elapsed wall time from runner: `3165.96 s` (`~52.8 min`)
     - Kilosort reported runtime: `3068.10 s` (`~51.1 min`)
     - total units: `194`
     - good refractory-period units: `28`
     - spikes in final Kilosort summary: `7,311,421`
     - spikes in runner summary: `7,370,558`
   - Important figures:
     - `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/diagnostics.png`
     - `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/drift_amount.png`
     - `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/drift_scatter.png`
     - `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/spike_positions.png`
   - Caveat: this run used the working Kilosort geometry and confirmed
     bad-channel list. Treat it as a full-session sort for inspection/curation,
     not final anatomy or unit-depth evidence.

## Kilosort4 Modal Run

The Dec 3 full raw file was sorted with Kilosort4 on Modal after staging the
51 GB `amplifier.dat` and spike-sorting prep folder to the Modal volume
`dec3-kilosort-data`.

Run URL:

- `https://modal.com/apps/pardis-stanford/main/ap-98jIARtjd6sXnqLgEOCynL`

Inputs:

- Raw binary:
  `Haptic_Stim_session1_251203_143031/amplifier.dat`
- Sampling rate: `20000 Hz`
- Binary channels: `128`
- Bad channels excluded in the prep metadata:
  `5, 6, 7, 32, 33, 34, 43, 66, 67`
- Probe map:
  `analysis/outputs/dec3/spike_sorting_prep/kilosort_channel_map.mat`
  using working two-shank geometry.

Outputs:

- Main local folder:
  `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/`
- Summary JSON:
  `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/modal_kilosort_run_summary.json`
- Phy/Kilosort files include:
  `spike_times.npy`, `spike_clusters.npy`, `templates.npy`,
  `cluster_group.tsv`, `cluster_KSLabel.tsv`, `cluster_ContamPct.tsv`,
  and `params.py`.

## Initial Kilosort Spike ON-vs-OFF Triage

Script:

- `analysis/spike_peth_on_off_dec3.py`
- `analysis/export_kilosort_pynapple_dec3.py`

Output:

- `analysis/outputs/dec3/spike_peth_on_off/index.html`
- `analysis/outputs/dec3/pynapple_spikes/`

Inputs:

- Modal Kilosort4 output:
  `analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/`
- Trial windows:
  `analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv`

Method:

- Converted Kilosort `spike_times.npy` from samples to seconds.
- Counted spikes for each cluster in each 3 s stimulation ON interval.
- Counted spikes for the matched 3 s OFF-control interval immediately after
  each stimulation.
- Computed paired ON-vs-OFF firing-rate deltas by condition.
- Built onset- and offset-aligned PETHs.
- Exported Kilosort spike trains as Pynapple `TsGroup` objects:
  - all clusters:
    `analysis/outputs/dec3/pynapple_spikes/kilosort_all_units_tsgroup.npz`
  - KS-good clusters:
    `analysis/outputs/dec3/pynapple_spikes/kilosort_ks_good_units_tsgroup.npz`

Main result:

- This initial Kilosort spike pass does **not** show a clean KS-good-unit
  ON-spiking increase.
- Across the `28` KS-good clusters, condition-average ON-minus-OFF deltas are
  small or negative:
  - `amp100_freq26`: `+0.041 Hz`
  - `amp100_freq5`: `-0.112 Hz`
  - `amp180_freq26`: `-0.148 Hz`
  - `amp180_freq5`: `-0.141 Hz`
  - `amp250_freq26`: `-0.199 Hz`
  - `amp250_freq5`: `-0.238 Hz`
- No KS-good cluster/condition comparison survives BH correction at `q < 0.05`.
- Three MUA-labeled low-rate clusters survive `q < 0.05`, all with `ON < OFF`.
- The largest positive `amp180_freq26` ON-minus-OFF effects are in MUA-labeled
  clusters, not KS-good clusters.
- Pynapple sanity check: loading the KS-good `TsGroup` and counting spikes in
  the 1200 ON intervals returns a `1200 x 28` Pynapple `TsdFrame`.

Interpretation:

- The initial spike result is not aligned with a simple "stimulation increases
  good unit firing during ON" story.
- The LFP `amp180_freq26` broadband/recovery effect may reflect local field
  synchrony, subthreshold/synaptic activity, movement/artifact/recovery
  dynamics, or multiunit structure.
- This triage pass is superseded for presentation by the curated/merged result
  below.

## Automated Cluster Quality Pre-Curation

New report:

- `analysis/outputs/dec3/cluster_quality/index.html`
- `analysis/outputs/dec3/cluster_quality/cluster_quality_summary.csv`
- `analysis/outputs/dec3/cluster_quality/phy_review_priority.csv`

What this does:

- Reads the Dec 3 Kilosort4 output directly.
- Adds objective pre-curation metrics:
  - spike count
  - mean firing rate
  - Kilosort label
  - Kilosort contamination percent
  - Kilosort amplitude
  - short-ISI fraction using a 2 ms refractory threshold
  - best template channel and working shank/group
  - strongest triage ON-minus-OFF spike response from the existing PETH
    analysis

Current automated counts:

- Total clusters/templates: `194`
- Kilosort-good clusters: `28`
- High-confidence KS-good by conservative automated rules: `19`
- Manual-review clusters: `33`
- Likely noise or multiunit by automated rules: `142`

Important interpretation:

- This was not final curation. It was a triage list for cluster review.
- `phy_review_priority.csv` was used as a review/merge checklist.
- The first clusters to review are KS-good clusters with the largest
  condition-linked ON-minus-OFF changes, followed by ambiguous high-response
  MUA/noise-labeled clusters.
- The current presentation-safe spike claim comes from the curated/merged result
  below.

## High-Confidence Spike ON-vs-OFF Subset

New report:

- `analysis/outputs/dec3/spike_peth_high_confidence/index.html`
- `analysis/outputs/dec3/spike_peth_high_confidence/condition_summary_by_unit_set.csv`
- `analysis/outputs/dec3/spike_peth_high_confidence/unit_condition_stats_by_unit_set.csv`

Unit sets compared:

- All Kilosort clusters: `194`
- Kilosort-good clusters: `28`
- Automated high-confidence KS-good clusters: `19`

High-confidence condition means, ON minus following 3 s OFF control:

- `amp100_freq26`: `+0.013 Hz`
- `amp100_freq5`: `-0.112 Hz`
- `amp180_freq26`: `-0.136 Hz`
- `amp180_freq5`: `-0.159 Hz`
- `amp250_freq26`: `-0.179 Hz`
- `amp250_freq5`: `-0.235 Hz`

Statistical result:

- High-confidence KS-good subset: `0` unit/condition tests survive BH
  correction at `q < 0.05`.
- KS-good subset: `0` unit/condition tests survive BH correction at `q < 0.05`.
- All clusters: `3` unit/condition tests survive BH correction, but these are
  not KS-good units and are therefore not a basis for clean single-unit claims.

Interpretation:

- Filtering to the cleanest automated unit set does not reveal a hidden
  ON-period spike-rate increase.
- The spike story remains unlike the LFP story: Dec 3 has clear LFP effects,
  but good/high-confidence single units do not show a robust ON > OFF firing
  increase under the current analysis.
- The high-confidence subset agrees with the later curated/merged result: no
  robust Dec 3 single-unit ON/OFF firing-rate effect at 5/26 Hz.

## Curated/Merged Spike Conclusion (Current)

Current writeup:

- `docs/DEC3_CURATED_SPIKE_RESULT.md`

Current presentation-safe result:

- `29` curated good units.
- `174` unit-condition ON-vs-OFF tests.
- `0` responsive unit-conditions after BH correction at `q < 0.05`.

Interpretation:

- The Dec 3 spike conclusion is now a curated null result, not just a provisional
  Kilosort screen.
- This does not erase the LFP response; it means the Dec 3 5/26 Hz LFP effect did
  not translate into a detectable single-unit firing-rate change in the curated
  unit set.
- Remaining spike-related caveats are fine anatomy/layer/spatial claims, not the
  ON/OFF firing-rate result itself.

## Historical Phy Setup Status

Setup note:

- `docs/PHY_DEC3_SETUP.md`

What works:

- A clean local conda environment named `phy-dec3` was created.
- The official GitHub Phy install is available as `phy==2.0b6`.
- `params.py` now points to the local Dec 3 raw data:
  `Haptic_Stim_session1_251203_143031/amplifier.dat`
- Phy validates the dataset with `template-describe`.

Phy validation result:

- Duration: `10644.4 s`
- Sample rate: `20.0 kHz`
- Raw channels: `128`
- Active channels in Kilosort output: `119`
- Templates/clusters: `194`
- Spikes: `7,311,421`

Current blocker:

- The Phy GUI starts loading but several OpenGL views fail locally on this
  macOS/Qt setup with shader errors: `version '120' is not supported`,
  `#version required and missing`, and `varying syntax error`.
- Trying `QT_OPENGL=software` did not fix it.
- This looks like a local OpenGL/Qt rendering compatibility problem, not a data
  or Kilosort-output problem.
- A second conservative env, `phy-dec3-legacy`, was created with Python 3.10.
  It validates the dataset and gets farther in foreground GUI launch, but still
  reports `Could not create view TemplateFeatureView`.

Interpretation:

- These notes document the earlier local GUI/Modal setup issue.
- The current scientific conclusion should use the curated/merged spike result
  above, not this historical setup status.

## Current One-Sentence Takeaway

Dec 3 shows clear stimulation-related LFP effects, strongest in broadband
amplitude for `180 amplitude / 26 Hz`. The most supported story is a
26 Hz, amplitude-dependent broadband/recovery response with adaptation:
`180 / 26 Hz` has reliable ON and OFF-period broadband increases, but late
repeats become OFF-dominant; `250 / 26 Hz` adapts downward strongly across
repeats. Frequency-specific power patterns are suggestive, but corrected
trial-level confidence intervals cross zero, and PLV does not show strong
trial-onset-aligned phase consistency. The current curated/merged spike analysis
also shows no Dec 3 ON/OFF firing-rate effect: `29` curated good units, `174`
unit-condition tests, `0` responsive after correction.
