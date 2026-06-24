# Dec 3 Pynapple Spike Export

Kilosort spike trains exported as Pynapple `TsGroup` objects. These files are
convenience objects for interval-count and PETH-style analyses; the final
presentation spike claim comes from the curated/merged ON/OFF analysis, not from
the KS-good export alone.

## Files

- `kilosort_all_units_tsgroup.npz`: all `194` Kilosort clusters.
- `kilosort_ks_good_units_tsgroup.npz`: `28` historical KS-good clusters.
- `cluster_metadata.csv`: Kilosort labels, optional curated `group`, contamination, amplitude, and good flag.
- `pynapple_spike_export_summary.json`: export summary.

## Example

```python
import pynapple as nap

spikes = nap.load_file("kilosort_ks_good_units_tsgroup.npz")
on = nap.load_file("../pynapple_intervals/all_on_intervals.npz")
counts = spikes.count(3.0, ep=on)
```

Caveat: the KS-good `TsGroup` follows Kilosort `KSLabel`. The final Dec 3
presentation result uses the curated/merged spike analyses: 29 curated good units
and 0/174 responsive unit-conditions. Probe geometry/channel order remains
provisional for depth/layer claims.
