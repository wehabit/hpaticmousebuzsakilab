#!/usr/bin/env python3
"""Create a SpikeInterface-ready Dec 3 recording view and sanity outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import probeinterface as pi
import spikeinterface as si


DEFAULT_RAW_DAT = Path("Haptic_Stim_session1_251203_143031/amplifier.dat")


def build_probe(channel_metadata: pd.DataFrame) -> pi.Probe:
    probe = pi.Probe(ndim=2, si_units="um")
    positions = channel_metadata[["x_um_provisional", "y_um_provisional"]].to_numpy(dtype=float)
    probe.set_contacts(positions=positions, shapes="circle", shape_params={"radius": 5})
    probe.set_device_channel_indices(channel_metadata["channel"].to_numpy(dtype=int))
    return probe


def plot_sanity_trace(recording, output: Path, start_s: float, duration_s: float, max_channels: int = 32) -> None:
    fs = recording.get_sampling_frequency()
    start_frame = int(round(start_s * fs))
    end_frame = int(round((start_s + duration_s) * fs))
    channel_ids = recording.get_channel_ids()[:max_channels]
    traces = recording.get_traces(start_frame=start_frame, end_frame=end_frame, channel_ids=channel_ids)
    traces = traces.astype(float)
    traces -= np.median(traces, axis=0, keepdims=True)
    scale = np.nanpercentile(np.abs(traces), 95)
    if not np.isfinite(scale) or scale <= 0:
        scale = 1.0
    time_s = np.arange(traces.shape[0]) / fs + start_s

    fig, ax = plt.subplots(figsize=(12, 8))
    for i in range(traces.shape[1]):
        ax.plot(time_s, traces[:, i] / scale + i, color="black", linewidth=0.35)
    ax.set_xlabel("Recording time (s)")
    ax.set_ylabel("Good channel index")
    ax.set_title(f"SpikeInterface raw trace sanity check, {duration_s:g} s from {start_s:g} s")
    ax.set_yticks(np.arange(len(channel_ids)))
    ax.set_yticklabels(channel_ids, fontsize=7)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prep-dir", type=Path, default=Path("analysis/outputs/dec3/spike_sorting_prep"))
    parser.add_argument("--raw-dat", type=Path, default=DEFAULT_RAW_DAT)
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/outputs/dec3/spikeinterface_setup"))
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=20000)
    parser.add_argument("--dtype", default="int16")
    parser.add_argument("--sanity-start-s", type=float, default=1540.0)
    parser.add_argument("--sanity-duration-s", type=float, default=2.0)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    channel_metadata = pd.read_csv(args.prep_dir / "channel_metadata.csv")
    good_channels = channel_metadata.loc[channel_metadata["connected"], "channel"].to_numpy(dtype=int)

    recording = si.read_binary(
        file_paths=[args.raw_dat],
        sampling_frequency=args.sample_rate_hz,
        num_channels=args.n_channels,
        dtype=args.dtype,
        time_axis=0,
        gain_to_uV=1.0,
        offset_to_uV=0.0,
    )
    recording = si.ChannelSliceRecording(recording, channel_ids=good_channels.tolist())

    probe = build_probe(channel_metadata)
    # Attach the full probe before slicing would require exact channel matching;
    # use channel locations directly here for a robust provisional setup.
    locs = channel_metadata.set_index("channel").loc[good_channels, ["x_um_provisional", "y_um_provisional"]].to_numpy()
    recording.set_channel_locations(locs)

    plot_sanity_trace(
        recording,
        args.output_dir / "spikeinterface_trace_sanity.png",
        args.sanity_start_s,
        args.sanity_duration_s,
    )

    dump_folder = args.output_dir / "recording_json"
    recording.dump_to_json(dump_folder / "recording.json")

    summary = {
        "raw_dat": str(args.raw_dat),
        "n_channels_raw": args.n_channels,
        "good_channel_count": int(len(good_channels)),
        "bad_channels": channel_metadata.loc[channel_metadata["is_bad"], "channel"].astype(int).tolist(),
        "sample_rate_hz": args.sample_rate_hz,
        "dtype": args.dtype,
        "recording_num_frames": int(recording.get_num_frames()),
        "recording_duration_s": float(recording.get_num_frames() / args.sample_rate_hz),
        "channel_ids_first_10": [int(x) for x in recording.get_channel_ids()[:10]],
        "channel_locations_status": "provisional_two_shank_geometry_from_spike_sorting_prep",
        "recording_json": str(dump_folder / "recording.json"),
        "sanity_plot": str(args.output_dir / "spikeinterface_trace_sanity.png"),
    }
    (args.output_dir / "spikeinterface_setup_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    readme = f"""# Dec 3 SpikeInterface Setup

This folder verifies that SpikeInterface can open the Dec 3 raw binary.

- Raw data: `{args.raw_dat}`
- Raw channels: `{args.n_channels}`
- Good channels after confirmed bad-channel exclusion: `{len(good_channels)}`
- Sampling rate: `{args.sample_rate_hz} Hz`
- Dtype: `{args.dtype}`

Outputs:

- `recording_json/recording.json`: SpikeInterface recording description.
- `spikeinterface_trace_sanity.png`: short raw-trace sanity plot.
- `spikeinterface_setup_summary.json`: metadata summary.

The raw binary is not modified. Channel locations are provisional until exact
Cambridge NeuroTech H12_2 geometry is confirmed.
"""
    (args.output_dir / "README.md").write_text(readme)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
