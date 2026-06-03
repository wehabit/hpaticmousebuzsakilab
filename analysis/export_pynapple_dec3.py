#!/usr/bin/env python
"""Export Dec 3 trial timing as Pynapple interval objects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import pynapple as nap


DEFAULT_TRIAL_WINDOWS = Path("analysis/outputs/dec3/spike_sorting_prep/trial_windows.csv")
DEFAULT_OUTPUT_DIR = Path("analysis/outputs/dec3/pynapple_intervals")


def make_interval_set(
    table: pd.DataFrame,
    start_col: str,
    end_col: str,
    metadata_cols: list[str],
) -> nap.IntervalSet:
    metadata = table.loc[:, metadata_cols].reset_index(drop=True).copy()
    return nap.IntervalSet(
        start=table[start_col].to_numpy(),
        end=table[end_col].to_numpy(),
        time_units="s",
        metadata=metadata,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-windows", type=Path, default=DEFAULT_TRIAL_WINDOWS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--baseline-start-s", type=float, default=0.0)
    parser.add_argument("--baseline-end-s", type=float, default=1540.0)
    args = parser.parse_args()

    trial_windows = pd.read_csv(args.trial_windows)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metadata_cols = ["trial_number", "condition", "amplitude", "freq"]

    baseline = nap.IntervalSet(
        start=args.baseline_start_s,
        end=args.baseline_end_s,
        time_units="s",
        metadata={"label": ["baseline"]},
    )
    on_epochs = make_interval_set(trial_windows, "on_start_s", "on_end_s", metadata_cols)
    off_epochs = make_interval_set(trial_windows, "off_start_s", "off_end_s", metadata_cols)

    baseline.save(str(args.output_dir / "baseline_interval.npz"))
    on_epochs.save(str(args.output_dir / "all_on_intervals.npz"))
    off_epochs.save(str(args.output_dir / "all_off_control_intervals.npz"))

    trial_windows.to_csv(args.output_dir / "trial_interval_metadata.csv", index=False)

    condition_counts: dict[str, dict[str, int]] = {}
    for condition, condition_rows in trial_windows.groupby("condition", sort=True):
        condition_on = make_interval_set(condition_rows, "on_start_s", "on_end_s", metadata_cols)
        condition_off = make_interval_set(condition_rows, "off_start_s", "off_end_s", metadata_cols)
        condition_on.save(str(args.output_dir / f"{condition}_on_intervals.npz"))
        condition_off.save(str(args.output_dir / f"{condition}_off_control_intervals.npz"))
        condition_counts[condition] = {
            "n_on_intervals": int(len(condition_rows)),
            "n_off_intervals": int(len(condition_rows)),
        }

    summary = {
        "trial_windows": str(args.trial_windows),
        "output_dir": str(args.output_dir),
        "baseline_start_s": args.baseline_start_s,
        "baseline_end_s": args.baseline_end_s,
        "n_trials": int(len(trial_windows)),
        "conditions": condition_counts,
        "pynapple_version": nap.__version__,
        "notes": [
            "OFF intervals are the within-trial 3 s control periods after stimulation.",
            "Interval metadata are also kept in trial_interval_metadata.csv because Pynapple npz saves are best for interval times.",
        ],
    }
    (args.output_dir / "pynapple_interval_export_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )

    readme = f"""# Dec 3 Pynapple Intervals

These files export Dec 3 timing into Pynapple-friendly interval objects.

## Files

- `baseline_interval.npz`: baseline interval, `{args.baseline_start_s:g}` to `{args.baseline_end_s:g}` s.
- `all_on_intervals.npz`: all 1200 stimulation ON windows.
- `all_off_control_intervals.npz`: all 1200 within-trial OFF control windows.
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

After spike sorting and curation, curated spike times can be loaded as a
`nap.TsGroup`, then restricted/count-binned against these ON and OFF control
intervals.
"""
    (args.output_dir / "README.md").write_text(readme)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
