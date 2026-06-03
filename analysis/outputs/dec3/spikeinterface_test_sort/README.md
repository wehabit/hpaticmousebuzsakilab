# Dec 3 SpikeInterface Test Sort

This folder is for a short smoke test, not full-session spike sorting.

- Sorter: `tridesclous2`
- Segment: `1540.0` to `1570.0` s
- Good channels: `119`
- Run requested: `True`

To actually run:

```bash
python analysis/run_spikeinterface_test_sort_dec3.py --sorter tridesclous2 --run
```

For final sorting, use a dedicated output folder and a final sorter/backend
choice, preferably Kilosort with the exact H12_2 geometry.
