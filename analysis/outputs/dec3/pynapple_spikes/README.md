# Dec 3 Pynapple Spike Export

Kilosort spike trains exported as Pynapple `TsGroup` objects.

## Files

- `kilosort_all_units_tsgroup.npz`: all `194` Kilosort clusters.
- `kilosort_ks_good_units_tsgroup.npz`: `28` KS-good clusters.
- `cluster_metadata.csv`: Kilosort labels, contamination, amplitude, and good flag.
- `pynapple_spike_export_summary.json`: export summary.

## Example

```python
import pynapple as nap

spikes = nap.load_file("kilosort_ks_good_units_tsgroup.npz")
on = nap.load_file("../pynapple_intervals/all_on_intervals.npz")
counts = spikes.count(3.0, ep=on)
```

Caveat: these spike trains are not Phy-curated yet and use the provisional
probe geometry/channel order.
