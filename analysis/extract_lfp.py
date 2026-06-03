#!/usr/bin/env python3
"""Extract a Neuroscope-compatible LFP file from Intan amplifier.dat."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.signal import resample_poly


def extract_lfp(
    dat_path: Path,
    output_path: Path,
    n_channels: int,
    sample_rate_hz: float,
    lfp_rate_hz: float,
    chunk_samples: int,
    overwrite: bool,
) -> dict:
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"{output_path} exists; pass --overwrite to replace it")

    downsample = sample_rate_hz / lfp_rate_hz
    if abs(round(downsample) - downsample) > 1e-9:
        raise ValueError("This extractor expects an integer downsampling factor")
    downsample = int(round(downsample))
    if chunk_samples % downsample != 0:
        chunk_samples = (chunk_samples // downsample) * downsample
    if chunk_samples <= 0:
        raise ValueError("chunk_samples is too small")

    total_samples = dat_path.stat().st_size // np.dtype("<i2").itemsize // n_channels
    data = np.memmap(dat_path, dtype="<i2", mode="r", shape=(total_samples, n_channels))
    expected_lfp_samples = int(np.ceil(total_samples / downsample))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunks_written = 0
    lfp_samples_written = 0

    with output_path.open("wb") as handle:
        for start in range(0, total_samples, chunk_samples):
            stop = min(start + chunk_samples, total_samples)
            chunk = np.asarray(data[start:stop], dtype=np.float32)
            lfp = resample_poly(chunk, up=1, down=downsample, axis=0)
            lfp = np.clip(np.rint(lfp), np.iinfo(np.int16).min, np.iinfo(np.int16).max).astype("<i2")
            lfp.tofile(handle)
            chunks_written += 1
            lfp_samples_written += int(lfp.shape[0])
            print(
                f"chunk {chunks_written}: raw {start}:{stop} -> "
                f"{lfp.shape[0]} LFP samples",
                flush=True,
            )

    summary = {
        "dat_path": str(dat_path),
        "output_path": str(output_path),
        "n_channels": n_channels,
        "sample_rate_hz": sample_rate_hz,
        "lfp_rate_hz": lfp_rate_hz,
        "downsample_factor": downsample,
        "raw_samples": int(total_samples),
        "raw_duration_s": total_samples / sample_rate_hz,
        "expected_lfp_samples": expected_lfp_samples,
        "lfp_samples_written": lfp_samples_written,
        "lfp_duration_s": lfp_samples_written / lfp_rate_hz,
        "chunks_written": chunks_written,
        "output_bytes": output_path.stat().st_size,
        "note": (
            "Raw amplifier.dat is unchanged. Chunked polyphase resampling was used; "
            "for most LFP analyses boundary effects are negligible, but avoid using "
            "samples exactly at chunk boundaries for precision artifact measurements."
        ),
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dat", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=20_000)
    parser.add_argument("--lfp-rate-hz", type=float, default=1_250)
    parser.add_argument("--chunk-samples", type=int, default=1_600_000)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    summary = extract_lfp(
        args.dat,
        args.output,
        args.n_channels,
        args.sample_rate_hz,
        args.lfp_rate_hz,
        args.chunk_samples,
        args.overwrite,
    )
    text = json.dumps(summary, indent=2)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
