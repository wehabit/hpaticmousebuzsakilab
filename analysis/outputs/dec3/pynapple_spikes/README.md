# Dec 3 Pynapple Spike Export

Kilosort spike trains were previously exported as Pynapple `TsGroup` objects,
but the `.npz` spike exports are not present in this checkout.

## Files

- `kilosort_all_units_tsgroup.npz`: all `194` Kilosort clusters, currently missing locally.
- `kilosort_ks_good_units_tsgroup.npz`: `28` KS-good clusters, currently missing locally.
- `cluster_metadata.csv`: Kilosort labels, contamination, amplitude, and good flag.
- `pynapple_spike_export_summary.json`: export summary.

To regenerate the missing `.npz` files, first restore the Kilosort `.npy`
arrays (`spike_times.npy`, `spike_clusters.npy`, templates/waveform arrays) to
`analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results/`.

## Example

```python
import pynapple as nap

spikes = nap.load_file("kilosort_ks_good_units_tsgroup.npz")  # after restoring/regenerating it
on = nap.load_file("../pynapple_intervals/all_on_intervals.npz")
counts = spikes.count(3.0, ep=on)
```

Caveat: these spike trains are not Phy-curated yet and use the provisional
probe geometry/channel order.
