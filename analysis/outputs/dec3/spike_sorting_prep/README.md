# Dec 3 Spike-Sorting Prep

This folder contains metadata for preparing spike sorting for:

`Haptic_Stim_session1_251203_143031/amplifier.dat`

The raw `amplifier.dat` is **not modified** by this prep step.

## Current Decisions

- Channel count: `128`
- Sample rate: `20000 Hz`
- Bad channels treated as confirmed for this analysis pass:
  `[5, 6, 7, 32, 33, 34, 43, 66, 67]`
- Phantom channels removed/ignored: `128-255`
- Trial timing source: `analysis/outputs/dec3/dec3_condition_sequence.csv`
- TTL source: `digitalin.dat` bit 7, used as QC, not the sole trial label source.

## Files

- `channel_metadata.csv`: one row per channel, including bad/connected flags.
- `bad_channels.txt`: confirmed bad channels, one per line.
- `good_channels.txt`: connected channels, one per line.
- `kilosort_channel_map.mat`: MATLAB channel map for Kilosort-style tools.
- `phy_params.py`: minimal Phy params file pointing at raw `amplifier.dat`.
- `stim_artifact_intervals.csv`: onset/offset windows to inspect or optionally exclude.
- `trial_windows.csv`: ON/OFF windows for all 1200 trials.
- `spike_sorting_plan.md`: practical next commands and caveats.

## Important Caveat

The `kilosort_channel_map.mat` uses provisional geometry:

- channels `0-63`: physical shank A
- channels `64-127`: physical shank B
- shank spacing: `250 um`
- vertical spacing placeholder: `20 um`

This is enough to start tool setup and sanity checks, but the exact Cambridge
NeuroTech `H12_2` contact geometry/channel order should be substituted before
final spike sorting claims.
