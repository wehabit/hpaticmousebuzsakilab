# Dec 3 Provisional Spike PETH / ON-vs-OFF

This folder contains the first spike analysis from the Modal Kilosort4 output.

## Inputs

- Kilosort output: `analysis/outputs/dec4/kilosort4_results_lec`
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

This is exploratory and uncurated. Use it to decide what to inspect in Phy and
what spike/LFP hypotheses to test next. Do not make final unit or anatomical
claims until Phy curation and exact probe geometry are resolved.
