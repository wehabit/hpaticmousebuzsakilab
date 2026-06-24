# Dec 4 dHPC Initial Spike PETH / ON-vs-OFF

This folder contains the initial Dec 4 dHPC spike ON/OFF analysis from the
Kilosort4 output. It is useful for audit and triage; final presentation claims
should use the curated/merged Dec 4 spike writeup in
[`DEC4_SPIKE_ONOFF_RESULT.md`](../../../../docs/DEC4_SPIKE_ONOFF_RESULT.md).

## Inputs

- Kilosort output: `analysis/outputs/dec4/kilosort4_results_dhpc`
- Trial windows: `analysis/outputs/dec4/spike_sorting_prep/trial_windows.csv`
- Sampling rate: `20000 Hz`

## Analysis

- Converts Kilosort `spike_times.npy` from samples to seconds.
- Counts spikes for every unit in every 3 s ON interval.
- Counts spikes for every unit in the following 3 s OFF-control interval.
- Computes paired ON-vs-OFF firing-rate deltas by condition.
- Builds onset- and offset-aligned PETH arrays.

## Main Outputs

- `index.html`: clickable visual report.
- `condition_summary_on_off.csv`: condition-level summaries for all units and KS-good units.
- `unit_condition_on_off_stats.csv`: per-unit, per-condition paired ON-vs-OFF statistics.
- `top_units_by_condition_delta.csv`: largest absolute condition effects.
- `condition_mean_on_minus_off.png`: population condition summary.
- `unit_condition_on_minus_off_heatmap_ks_good.png`: KS-good unit heatmap.
- `unit_condition_on_minus_off_heatmap_all_units.png`: all-unit heatmap.
- `peth_onset_ks_good_units.png`: onset-aligned PETH.
- `peth_offset_ks_good_units.png`: offset-aligned PETH.

## Caveat

This is the initial Kilosort-label view, not the final curated-unit result.
Curation/merge outputs are in `analysis/outputs/dec4/curated_merged_dhpc/`.
Exact probe geometry is still provisional for depth/layer claims.
