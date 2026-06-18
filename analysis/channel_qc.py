#!/usr/bin/env python3
"""Detect likely bad Intan amplifier channels from raw DAT samples."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def robust_z(values: np.ndarray) -> np.ndarray:
    median = np.nanmedian(values)
    mad = np.nanmedian(np.abs(values - median))
    if mad == 0 or np.isnan(mad):
        scale = np.nanstd(values)
        if scale == 0 or np.isnan(scale):
            return np.zeros_like(values, dtype=float)
        return (values - median) / scale
    return 0.67448975 * (values - median) / mad


def window_starts(
    total_samples: int,
    window_samples: int,
    n_windows: int,
    start_sample: int = 0,
    end_sample: int | None = None,
) -> np.ndarray:
    if end_sample is None:
        end_sample = total_samples
    if start_sample < 0 or end_sample > total_samples or start_sample >= end_sample:
        raise ValueError("Invalid QC sample range")
    if end_sample - start_sample < window_samples:
        raise ValueError("QC sample range is shorter than the window")
    if n_windows <= 1:
        return np.asarray([start_sample + (end_sample - start_sample - window_samples) // 2], dtype=np.int64)
    max_start = end_sample - window_samples
    return np.linspace(start_sample, max_start, n_windows, dtype=np.int64)


def compute_channel_qc(
    dat_path: Path,
    n_channels: int,
    sample_rate_hz: float,
    window_seconds: float,
    n_windows: int,
    compute_common_corr: bool,
    start_s: float | None,
    end_s: float | None,
) -> tuple[pd.DataFrame, dict]:
    file_samples = dat_path.stat().st_size // np.dtype("<i2").itemsize // n_channels
    window_samples = int(round(window_seconds * sample_rate_hz))
    if window_samples <= 1:
        raise ValueError("window_seconds is too short")
    if window_samples > file_samples:
        raise ValueError("QC window is longer than the recording")

    data = np.memmap(dat_path, dtype="<i2", mode="r", shape=(file_samples, n_channels))
    start_sample = 0 if start_s is None else int(round(start_s * sample_rate_hz))
    end_sample = file_samples if end_s is None else int(round(end_s * sample_rate_hz))
    starts = window_starts(file_samples, window_samples, n_windows, start_sample, end_sample)

    rms = []
    mad = []
    ptp = []
    absmax = []
    zero_fraction = []
    saturation_fraction = []
    rough_mad = []
    common_corr = []

    for start in starts:
        chunk = np.asarray(data[start : start + window_samples], dtype=np.float32)
        centered = chunk - np.median(chunk, axis=0, keepdims=True)
        rms.append(np.sqrt(np.mean(centered**2, axis=0)))
        mad.append(np.median(np.abs(centered), axis=0))
        ptp.append(np.ptp(chunk, axis=0))
        absmax.append(np.max(np.abs(chunk), axis=0))
        zero_fraction.append(np.mean(chunk == 0, axis=0))
        saturation_fraction.append(np.mean(np.abs(chunk) >= 32760, axis=0))
        rough_mad.append(np.median(np.abs(np.diff(chunk, axis=0)), axis=0))

        if compute_common_corr:
            common = np.median(centered, axis=1)
            common_std = float(np.std(common))
            if common_std == 0:
                common_corr.append(np.zeros(n_channels, dtype=float))
                continue
            channel_std = np.std(centered, axis=0)
            covariance = np.mean((centered - np.mean(centered, axis=0)) * (common - np.mean(common))[:, None], axis=0)
            corr = covariance / np.maximum(channel_std * common_std, 1e-12)
            common_corr.append(corr)

    metrics = {
        "rms": np.median(np.vstack(rms), axis=0),
        "mad": np.median(np.vstack(mad), axis=0),
        "ptp": np.median(np.vstack(ptp), axis=0),
        "absmax": np.max(np.vstack(absmax), axis=0),
        "zero_fraction": np.max(np.vstack(zero_fraction), axis=0),
        "saturation_fraction": np.max(np.vstack(saturation_fraction), axis=0),
        "rough_mad": np.median(np.vstack(rough_mad), axis=0),
    }
    if compute_common_corr:
        metrics["common_corr"] = np.median(np.vstack(common_corr), axis=0)

    frame = pd.DataFrame({"channel": np.arange(n_channels), **metrics})
    for name in ["rms", "mad", "ptp", "rough_mad", "absmax"]:
        frame[f"{name}_rz"] = robust_z(frame[name].to_numpy(dtype=float))

    reasons = []
    for row in frame.itertuples(index=False):
        row_reasons = []
        if row.mad <= 1:
            row_reasons.append("near_flat")
        if row.zero_fraction > 0.5:
            row_reasons.append("many_zeros")
        if row.saturation_fraction > 0.001:
            row_reasons.append("saturation")
        if row.rms_rz > 6 or row.mad_rz > 6:
            row_reasons.append("extreme_noise")
        elif row.rms_rz > 4 or row.mad_rz > 4:
            row_reasons.append("high_noise")
        if row.rough_mad_rz > 6:
            row_reasons.append("extreme_hf_noise")
        elif row.rough_mad_rz > 4:
            row_reasons.append("high_hf_noise")
        common_corr = getattr(row, "common_corr", np.nan)
        if not np.isnan(common_corr) and abs(common_corr) > 0.98 and row.rms_rz > 3:
            row_reasons.append("common_artifact_dominated")
        reasons.append(";".join(row_reasons))

    frame["exclude_reasons"] = reasons
    frame["exclude_auto"] = frame["exclude_reasons"] != ""

    summary = {
        "dat_path": str(dat_path),
        "n_channels": n_channels,
        "sample_rate_hz": sample_rate_hz,
        "total_samples": int(file_samples),
        "duration_s": file_samples / sample_rate_hz,
        "window_seconds": window_seconds,
        "n_windows": int(len(starts)),
        "compute_common_corr": compute_common_corr,
        "qc_start_s": start_s,
        "qc_end_s": end_s,
        "window_start_samples": starts.astype(int).tolist(),
        "excluded_channels": frame.loc[frame["exclude_auto"], "channel"].astype(int).tolist(),
        "n_excluded_channels": int(frame["exclude_auto"].sum()),
    }
    return frame, summary


def plot_qc(frame: pd.DataFrame, output_path: Path) -> None:
    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    channels = frame["channel"]
    excluded = frame["exclude_auto"].to_numpy()

    axes[0].plot(channels, frame["rms"], marker=".", linewidth=1)
    axes[0].scatter(channels[excluded], frame.loc[excluded, "rms"], color="crimson", zorder=3)
    axes[0].set_ylabel("RMS")

    axes[1].plot(channels, frame["mad"], marker=".", linewidth=1)
    axes[1].scatter(channels[excluded], frame.loc[excluded, "mad"], color="crimson", zorder=3)
    axes[1].set_ylabel("MAD")

    axes[2].plot(channels, frame["rough_mad"], marker=".", linewidth=1)
    axes[2].scatter(channels[excluded], frame.loc[excluded, "rough_mad"], color="crimson", zorder=3)
    axes[2].set_ylabel("Diff MAD")

    if "common_corr" in frame:
        axes[3].plot(channels, frame["common_corr"], marker=".", linewidth=1)
        axes[3].scatter(channels[excluded], frame.loc[excluded, "common_corr"], color="crimson", zorder=3)
        axes[3].set_ylabel("Median corr")
    else:
        axes[3].plot(channels, frame["ptp"], marker=".", linewidth=1)
        axes[3].scatter(channels[excluded], frame.loc[excluded, "ptp"], color="crimson", zorder=3)
        axes[3].set_ylabel("Peak-to-peak")
    axes[3].set_xlabel("Amplifier channel")

    for ax in axes:
        ax.grid(alpha=0.25)
    fig.suptitle("Dec 3 Channel QC: red = automatically flagged")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dat", type=Path, required=True)
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--sample-rate-hz", type=float, default=20_000)
    parser.add_argument("--window-seconds", type=float, default=10)
    parser.add_argument("--n-windows", type=int, default=24)
    parser.add_argument("--compute-common-corr", action="store_true")
    parser.add_argument("--start-s", type=float, default=None)
    parser.add_argument("--end-s", type=float, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame, summary = compute_channel_qc(
        args.dat,
        args.n_channels,
        args.sample_rate_hz,
        args.window_seconds,
        args.n_windows,
        args.compute_common_corr,
        args.start_s,
        args.end_s,
    )

    frame.to_csv(args.output_dir / "channel_qc_metrics.csv", index=False)
    (args.output_dir / "channel_qc_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    plot_qc(frame, args.output_dir / "channel_qc_metrics.png")

    print(json.dumps(summary, indent=2))
    if summary["excluded_channels"]:
        print("Excluded channels:", ",".join(map(str, summary["excluded_channels"])))
    else:
        print("No channels exceeded automatic exclusion thresholds.")


if __name__ == "__main__":
    main()
