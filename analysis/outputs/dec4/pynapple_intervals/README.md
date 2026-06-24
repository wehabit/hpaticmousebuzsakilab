# Dec 4 Pynapple Intervals

These files export Dec 4 timing into Pynapple-friendly interval objects.

## Files

- `baseline_interval.npz`: baseline interval, `1886.78` to `2786.78` s.
- `all_on_intervals.npz`: all 2400 stimulation ON windows.
- `all_off_control_intervals.npz`: all 2400 within-trial OFF control windows.
- `*_on_intervals.npz`: condition-specific ON windows.
- `*_off_control_intervals.npz`: condition-specific OFF control windows.
- `trial_interval_metadata.csv`: trial number, condition, amplitude, frequency, and ON/OFF times.
- `pynapple_interval_export_summary.json`: export summary.

## Example

```python
import pynapple as nap

on = nap.load_file("all_on_intervals.npz")
off = nap.load_file("all_off_control_intervals.npz")
```

Curated spike times can be loaded as a `nap.TsGroup`, then restricted/count-binned
against these ON and OFF control intervals.
