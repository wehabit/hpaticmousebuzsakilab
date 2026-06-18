#!/usr/bin/env python3
"""Run a tiny SpikeInterface sorter smoke test on a short Dec 3 segment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import spikeinterface as si
import spikeinterface.preprocessing as spre
import spikeinterface.sorters as ss


DEFAULT_RAW_DAT = Path("Haptic_Stim_session1_251203_143031/amplifier.dat")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dat", type=Path, default=DEFAULT_RAW_DAT)
    parser.add_argument("--prep-dir", type=Path, default=Path("analysis/outputs/dec3/spike_sorting_prep"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/outputs/dec3/spikeinterface_test_sort"))
    parser.add_argument("--sorter", default="tridesclous2")
    parser.add_argument("--start-s", type=float, default=1540.0)
    parser.add_argument("--duration-s", type=float, default=30.0)
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=20000.0)
    parser.add_argument("--dtype", default="int16")
    parser.add_argument("--run", action="store_true", help="Actually run the sorter. Without this, only writes a dry-run plan.")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    channel_metadata = pd.read_csv(args.prep_dir / "channel_metadata.csv")
    good_channels = channel_metadata.loc[channel_metadata["connected"], "channel"].astype(int).tolist()

    recording = si.read_binary(
        file_paths=[args.raw_dat],
        sampling_frequency=args.sample_rate_hz,
        num_channels=args.n_channels,
        dtype=args.dtype,
        time_axis=0,
        gain_to_uV=1.0,
        offset_to_uV=0.0,
    )
    recording = si.ChannelSliceRecording(recording, channel_ids=good_channels)
    locs = channel_metadata.set_index("channel").loc[good_channels, ["x_um_provisional", "y_um_provisional"]].to_numpy()
    recording.set_channel_locations(locs)
    start_frame = int(round(args.start_s * args.sample_rate_hz))
    end_frame = int(round((args.start_s + args.duration_s) * args.sample_rate_hz))
    recording = si.FrameSliceRecording(recording, start_frame=start_frame, end_frame=end_frame)
    recording = spre.bandpass_filter(recording, freq_min=300, freq_max=6000)
    recording = spre.common_reference(recording, reference="global", operator="median")

    installed = ss.installed_sorters()
    summary = {
        "sorter": args.sorter,
        "run_requested": args.run,
        "sorter_installed": args.sorter in installed,
        "installed_sorters": installed,
        "start_s": args.start_s,
        "duration_s": args.duration_s,
        "good_channel_count": len(good_channels),
        "note": "This is a smoke test on a short segment, not full-session sorting.",
    }

    if args.run:
        if args.sorter not in installed:
            raise RuntimeError(f"Sorter {args.sorter!r} is not installed. Installed: {installed}")
        sorting = ss.run_sorter(
            sorter_name=args.sorter,
            recording=recording,
            folder=args.output_dir / args.sorter,
            remove_existing_folder=True,
            verbose=True,
        )
        units = [int(u) for u in sorting.get_unit_ids()]
        summary["unit_count"] = len(units)
        summary["unit_ids"] = units[:50]

    (args.output_dir / "test_sort_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    readme = f"""# Dec 3 SpikeInterface Test Sort

This folder is for a short smoke test, not full-session spike sorting.

- Sorter: `{args.sorter}`
- Segment: `{args.start_s}` to `{args.start_s + args.duration_s}` s
- Good channels: `{len(good_channels)}`
- Run requested: `{args.run}`

To actually run:

```bash
python analysis/run_spikeinterface_test_sort_dec3.py --sorter {args.sorter} --run
```

For final sorting, use a dedicated output folder and a final sorter/backend
choice, preferably Kilosort with the exact H12_2 geometry.
"""
    (args.output_dir / "README.md").write_text(readme)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
