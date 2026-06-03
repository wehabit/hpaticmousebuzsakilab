#!/usr/bin/env python3
"""Create Neuroscope-like channel trace pages from an Intan amplifier.dat file."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


SHANK_GROUPS = {
    "shank1_ch96_127": list(range(96, 128)),
    "shank2_ch64_95": list(range(64, 96)),
    "shank3_ch32_63": list(range(32, 64)),
    "shank4_ch0_31": list(range(0, 32)),
}


def plot_group(
    data: np.memmap,
    channels: list[int],
    sample_rate_hz: float,
    start_s: float,
    duration_s: float,
    output_path: Path,
) -> None:
    start = int(round(start_s * sample_rate_hz))
    n_samples = int(round(duration_s * sample_rate_hz))
    chunk = np.asarray(data[start : start + n_samples, channels], dtype=np.float32)
    chunk -= np.median(chunk, axis=0, keepdims=True)

    # Robust spacing keeps large outliers visible without crushing all channels.
    scale = np.nanpercentile(np.abs(chunk), 98)
    if not np.isfinite(scale) or scale <= 0:
        scale = 500.0
    spacing = scale * 5
    time = np.arange(n_samples) / sample_rate_hz + start_s

    fig, ax = plt.subplots(figsize=(16, 11))
    for row, channel in enumerate(channels):
        ax.plot(time, chunk[:, row] + row * spacing, linewidth=0.45, color="black")
        ax.text(time[0], row * spacing, f"{channel}", ha="right", va="center", fontsize=8)

    ax.set_title(f"{output_path.stem}: {start_s:.1f}-{start_s + duration_s:.1f} s")
    ax.set_xlabel("Recording time (s)")
    ax.set_yticks([])
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dat", type=Path, required=True)
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=20_000)
    parser.add_argument("--start-s", type=float, action="append", required=True)
    parser.add_argument("--duration-s", type=float, default=2)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    total_samples = args.dat.stat().st_size // np.dtype("<i2").itemsize // args.n_channels
    data = np.memmap(args.dat, dtype="<i2", mode="r", shape=(total_samples, args.n_channels))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for start_s in args.start_s:
        for group_name, channels in SHANK_GROUPS.items():
            output = args.output_dir / f"{group_name}_start{int(round(start_s))}s.png"
            plot_group(data, channels, args.sample_rate_hz, start_s, args.duration_s, output)
            print(output)


if __name__ == "__main__":
    main()
