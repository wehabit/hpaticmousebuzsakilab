# Spike Sorting Plan

## 1. Install Sorting Tools

No spike sorting package was installed in the current Python environment when
this prep was generated. Recommended options:

```bash
pip install spikeinterface probeinterface phylib
```

For Kilosort, install the version you plan to use separately, preferably in a
dedicated environment with GPU support.

## 2. Use Raw Data, Do Not Overwrite

Raw data:

`/Users/paris/Documents/Buzsaki Lab/Haptic_Stim_session1_251203_143031/amplifier.dat`

Keep this file immutable. Let the sorting tool do filtering/CAR, or write any
derived binary to a separate output folder.

## 3. Bad Channels

Use `bad_channels.txt` / `channel_metadata.csv`.

Confirmed current-pass bad channels:

`[5, 6, 7, 32, 33, 34, 43, 66, 67]`

## 4. Artifact Windows

Use `stim_artifact_intervals.csv` to inspect stimulation onset/offset artifacts.
Do not delete these intervals blindly; first decide whether the sorter should
ignore, annotate, or tolerate them.

## 5. Geometry Caveat

`kilosort_channel_map.mat` has provisional two-shank geometry. Replace it with
the exact Cambridge NeuroTech H12_2 map before final sorting if possible.

## 6. After Sorting

After Kilosort/Phy curation, align units to:

- ON: `0-3 s`
- OFF: `3-6 s`
- early/middle/late repeats
- condition: amplitude x frequency

The LFP result to test in spikes is:

`180/26` has sustained-plus-OFF broadband response, and `250/26` adapts downward.
