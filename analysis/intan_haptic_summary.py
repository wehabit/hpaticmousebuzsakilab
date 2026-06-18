#!/usr/bin/env python3
"""Summarize Intan haptic stimulation sessions and align TTL bursts to config."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np


DEFAULT_CHUNK_SAMPLES = 5_000_000


@dataclass
class DigitalEdges:
    channel: int
    rising_samples: list[int]
    falling_samples: list[int]


@dataclass
class Burst:
    burst_index: int
    start_sample: int
    end_sample: int
    start_time_s: float
    end_time_s: float
    duration_s: float
    pulse_count: int
    estimated_freq_hz: float | None


def parse_xml_metadata(xml_path: Path) -> dict:
    root = ET.parse(xml_path).getroot()
    acquisition = root.find("acquisitionSystem")
    if acquisition is None:
        raise ValueError(f"Missing acquisitionSystem in {xml_path}")

    groups = root.findall(".//anatomicalDescription/channelGroups/group")
    channels = root.findall(".//anatomicalDescription/channelGroups/group/channel")
    skipped_channels = [
        int(ch.text)
        for ch in channels
        if ch.text is not None and ch.attrib.get("skip") == "1"
    ]

    return {
        "n_bits": int(acquisition.findtext("nBits", "16")),
        "n_channels": int(acquisition.findtext("nChannels", "0")),
        "sampling_rate_hz": float(acquisition.findtext("samplingRate", "0")),
        "lfp_sampling_rate_hz": float(root.findtext("fieldPotentials/lfpSamplingRate", "0")),
        "channel_group_count": len(groups),
        "channel_group_sizes": [len(group.findall("channel")) for group in groups],
        "skipped_channel_count": len(skipped_channels),
        "skipped_channels": skipped_channels,
    }


def active_digital_channels(digital_path: Path, chunk_samples: int) -> list[int]:
    data = np.memmap(digital_path, dtype="<u2", mode="r")
    word_or = 0
    for start in range(0, len(data), chunk_samples):
        chunk = np.asarray(data[start : start + chunk_samples])
        if len(chunk):
            word_or |= int(np.bitwise_or.reduce(chunk))
    return [bit for bit in range(16) if word_or & (1 << bit)]


def parse_digital_edges(
    digital_path: Path,
    channels: list[int],
    chunk_samples: int,
) -> list[DigitalEdges]:
    data = np.memmap(digital_path, dtype="<u2", mode="r")
    parsed = []

    for channel in channels:
        mask = 1 << channel
        rising: list[int] = []
        falling: list[int] = []
        previous_state = bool(data[0] & mask) if len(data) else False

        for start in range(0, len(data), chunk_samples):
            chunk = np.asarray(data[start : start + chunk_samples])
            states = (chunk & mask) > 0
            if len(states) == 0:
                continue

            first_state = bool(states[0])
            if start > 0:
                if not previous_state and first_state:
                    rising.append(start)
                elif previous_state and not first_state:
                    falling.append(start)

            transitions = np.diff(states.astype(np.int8))
            rising.extend((np.flatnonzero(transitions == 1) + start + 1).astype(int).tolist())
            falling.extend((np.flatnonzero(transitions == -1) + start + 1).astype(int).tolist())
            previous_state = bool(states[-1])

        parsed.append(DigitalEdges(channel, rising, falling))

    return parsed


def load_stimulus_config(config_path: Path) -> list[dict]:
    with config_path.open() as handle:
        config = json.load(handle)

    stimuli = []
    elapsed_s = 0.0
    previous_h_had_stimulation = False
    for item in config["cmds"]:
        if isinstance(item, int | float):
            if not previous_h_had_stimulation:
                elapsed_s += float(item)
            previous_h_had_stimulation = False
            continue
        if not isinstance(item, dict) or "H" not in item:
            previous_h_had_stimulation = False
            continue
        h_had_stimulation = False
        for effect in item["H"].get("effects", []):
            params = effect.get("P", {})
            on_time_s = float(params.get("on_time", 0)) / 1000.0
            off_time_s = float(params.get("off_time", 0)) / 1000.0
            if on_time_s <= 0:
                continue
            h_had_stimulation = True
            stimuli.append(
                {
                    "trial_number": len(stimuli) + 1,
                    "config_index": len(stimuli),
                    "expected_start_time_s": elapsed_s,
                    "expected_end_time_s": elapsed_s + on_time_s,
                    "amplitude": params.get("amplitude"),
                    "freq": params.get("freq"),
                    "condition": f"amp{params.get('amplitude')}_freq{params.get('freq')}",
                    "pin": params.get("pin"),
                    "on_time_s": on_time_s,
                    "off_time_s": off_time_s,
                }
            )
            elapsed_s += on_time_s + off_time_s
        previous_h_had_stimulation = h_had_stimulation
    return stimuli


def group_pulses_into_bursts(
    edges: DigitalEdges,
    sample_rate_hz: float,
    gap_threshold_s: float,
) -> list[Burst]:
    rising = np.asarray(edges.rising_samples, dtype=np.int64)
    falling = np.asarray(edges.falling_samples, dtype=np.int64)
    if len(rising) == 0:
        return []

    gap_threshold_samples = int(round(gap_threshold_s * sample_rate_hz))
    split_after = np.flatnonzero(np.diff(rising) > gap_threshold_samples) + 1
    groups = np.split(rising, split_after)

    bursts = []
    for idx, group in enumerate(groups):
        start_sample = int(group[0])
        relevant_falling = falling[falling >= start_sample]
        end_sample = int(relevant_falling[np.searchsorted(relevant_falling, group[-1], side="left")])
        intervals = np.diff(group) / sample_rate_hz
        estimated_freq = None
        if len(intervals):
            median_interval = float(np.median(intervals))
            if median_interval > 0:
                estimated_freq = 1.0 / median_interval
        bursts.append(
            Burst(
                burst_index=idx,
                start_sample=start_sample,
                end_sample=end_sample,
                start_time_s=start_sample / sample_rate_hz,
                end_time_s=end_sample / sample_rate_hz,
                duration_s=(end_sample - start_sample) / sample_rate_hz,
                pulse_count=len(group),
                estimated_freq_hz=estimated_freq,
            )
        )
    return bursts


def write_edges(output_dir: Path, edges: list[DigitalEdges]) -> None:
    for channel_edges in edges:
        edge_path = output_dir / f"digital_edges_ch{channel_edges.channel}.csv"
        with edge_path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["edge", "sample"])
            writer.writerows(("rising", sample) for sample in channel_edges.rising_samples)
            writer.writerows(("falling", sample) for sample in channel_edges.falling_samples)


def add_recording_times(stimuli: list[dict], recording_start_offset_s: float | None) -> list[dict]:
    if recording_start_offset_s is None:
        return stimuli
    enriched = []
    for stimulus in stimuli:
        row = dict(stimulus)
        row["recording_start_time_s"] = row["expected_start_time_s"] + recording_start_offset_s
        row["recording_end_time_s"] = row["expected_end_time_s"] + recording_start_offset_s
        enriched.append(row)
    return enriched


def write_config_schedule(output_dir: Path, stimuli: list[dict]) -> None:
    schedule_path = output_dir / "stimulus_config_schedule.csv"
    with schedule_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(stimuli[0]) if stimuli else ["config_index"])
        writer.writeheader()
        writer.writerows(stimuli)

    dec3_sequence_path = output_dir / "dec3_condition_sequence.csv"
    with dec3_sequence_path.open("w", newline="") as handle:
        fieldnames = [
            "trial_number",
            "condition",
            "amplitude",
            "freq",
            "expected_start_time_s",
            "expected_end_time_s",
            "recording_start_time_s",
            "recording_end_time_s",
            "on_time_s",
            "off_time_s",
        ]
        fieldnames = [name for name in fieldnames if name in stimuli[0]] if stimuli else fieldnames
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({name: stimulus[name] for name in fieldnames} for stimulus in stimuli)


def write_events(output_dir: Path, stimuli: list[dict], bursts: list[Burst]) -> list[dict]:
    rows = []
    for idx, burst in enumerate(bursts):
        stimulus = stimuli[idx] if idx < len(stimuli) else {}
        row = {
            **asdict(burst),
            "label_source": "ttl_row_join_qc_only",
            "config_index": stimulus.get("config_index"),
            "amplitude": stimulus.get("amplitude"),
            "expected_freq_hz": stimulus.get("freq"),
            "pin": stimulus.get("pin"),
            "expected_start_time_s": stimulus.get("expected_start_time_s"),
            "start_time_error_s": None,
        }
        if stimulus:
            row["start_time_error_s"] = burst.start_time_s - stimulus["expected_start_time_s"]
        rows.append(row)

    events_path = output_dir / "stimulation_events.csv"
    with events_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["burst_index"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--recording-start-offset-s",
        type=float,
        default=None,
        help="Seconds from recording start to controller baseline start.",
    )
    parser.add_argument("--digital-channels", type=int, nargs="*", default=None)
    parser.add_argument(
        "--gap-threshold-s",
        type=float,
        default=2.3,
        help="Split pulse trains into bursts when rising-edge gaps exceed this duration.",
    )
    parser.add_argument("--chunk-samples", type=int, default=DEFAULT_CHUNK_SAMPLES)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    xml_path = args.session_dir / "amplifier.xml"
    digital_path = args.session_dir / "digitalin.dat"
    amplifier_path = args.session_dir / "amplifier.dat"
    time_path = args.session_dir / "time.dat"

    metadata = parse_xml_metadata(xml_path)
    sample_rate_hz = metadata["sampling_rate_hz"]
    active_channels = active_digital_channels(digital_path, args.chunk_samples)
    channels = args.digital_channels if args.digital_channels is not None else active_channels
    edges = parse_digital_edges(digital_path, channels, args.chunk_samples)
    write_edges(args.output_dir, edges)

    stimuli = add_recording_times(
        load_stimulus_config(args.config),
        args.recording_start_offset_s,
    )
    write_config_schedule(args.output_dir, stimuli)
    burst_channel = max(edges, key=lambda item: len(item.rising_samples))
    bursts = group_pulses_into_bursts(burst_channel, sample_rate_hz, args.gap_threshold_s)
    event_rows = write_events(args.output_dir, stimuli, bursts)
    alignment_warning = None
    if len(stimuli) != len(bursts):
        alignment_warning = (
            f"Detected {len(bursts)} TTL bursts but stimulus config contains "
            f"{len(stimuli)} nonzero stimulation effects. Inspect stimulation_events.csv "
            "before treating config labels as final."
        )

    summary = {
        "session_dir": str(args.session_dir),
        "config": str(args.config),
        "metadata": metadata,
        "files": {
            "amplifier_dat_bytes": amplifier_path.stat().st_size,
            "digitalin_dat_bytes": digital_path.stat().st_size,
            "time_dat_bytes": time_path.stat().st_size,
            "digitalin_samples": digital_path.stat().st_size // np.dtype("<u2").itemsize,
        },
        "active_digital_channels": active_channels,
        "parsed_digital_channels": [
            {
                "channel": edge.channel,
                "rising_edge_count": len(edge.rising_samples),
                "falling_edge_count": len(edge.falling_samples),
            }
            for edge in edges
        ],
        "burst_channel": burst_channel.channel,
        "burst_gap_threshold_s": args.gap_threshold_s,
        "stimulus_config_count": len(stimuli),
        "recording_start_offset_s": args.recording_start_offset_s,
        "detected_burst_count": len(bursts),
        "tentative_row_joined_event_count": min(len(stimuli), len(bursts)),
        "event_labeling_note": (
            "dec3_condition_sequence.csv is the authoritative Dec 3 trial schedule. "
            "stimulation_events.csv row-joins detected TTL bursts to config rows for delivery/timing QC only."
        ),
        "alignment_warning": alignment_warning,
        "median_start_time_error_s": (
            float(np.median([row["start_time_error_s"] for row in event_rows if row["start_time_error_s"] is not None]))
            if event_rows and alignment_warning is None
            else None
        ),
    }
    with (args.output_dir / "session_summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
