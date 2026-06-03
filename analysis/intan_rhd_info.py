#!/usr/bin/env python3
"""Read core metadata from an Intan RHD info/header file."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


def _read_qstring(data: bytes, offset: int) -> tuple[str, int]:
    length = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    if length == 0xFFFFFFFF:
        return "", offset
    raw = data[offset : offset + length]
    offset += length
    return raw.decode("utf-16le", errors="replace"), offset


def read_rhd_info(path: Path) -> dict:
    data = path.read_bytes()
    offset = 0

    magic = struct.unpack_from("<I", data, offset)[0]
    offset += 4
    major, minor = struct.unpack_from("<hh", data, offset)
    offset += 4
    sample_rate_hz = struct.unpack_from("<f", data, offset)[0]
    offset += 4
    dsp_enabled = struct.unpack_from("<h", data, offset)[0]
    offset += 2

    (
        actual_dsp_cutoff_hz,
        actual_lower_bandwidth_hz,
        actual_upper_bandwidth_hz,
        desired_dsp_cutoff_hz,
        desired_lower_bandwidth_hz,
        desired_upper_bandwidth_hz,
    ) = struct.unpack_from("<ffffff", data, offset)
    offset += 24

    notch_filter_mode = struct.unpack_from("<h", data, offset)[0]
    offset += 2
    desired_impedance_test_frequency_hz, actual_impedance_test_frequency_hz = struct.unpack_from(
        "<ff", data, offset
    )
    offset += 8

    notes = []
    for _ in range(3):
        note, offset = _read_qstring(data, offset)
        notes.append(note)

    num_temp_sensor_channels = struct.unpack_from("<h", data, offset)[0]
    offset += 2
    eval_board_mode = struct.unpack_from("<h", data, offset)[0]
    offset += 2
    reference_channel, offset = _read_qstring(data, offset)

    num_signal_groups = struct.unpack_from("<h", data, offset)[0]
    offset += 2

    groups = []
    amplifier_channels = []
    enabled_counts_by_type: dict[str, int] = {}
    signal_type_names = {
        0: "amplifier",
        1: "aux_input",
        2: "supply_voltage",
        3: "board_adc",
        4: "board_dig_in",
        5: "board_dig_out",
    }

    for _ in range(num_signal_groups):
        group_name, offset = _read_qstring(data, offset)
        group_prefix, offset = _read_qstring(data, offset)
        group_enabled, group_num_channels, group_num_amp_channels = struct.unpack_from(
            "<hhh", data, offset
        )
        offset += 6

        group = {
            "name": group_name,
            "prefix": group_prefix,
            "enabled": bool(group_enabled),
            "num_channels": group_num_channels,
            "num_amplifier_channels": group_num_amp_channels,
        }
        groups.append(group)

        for _ in range(group_num_channels):
            native_name, offset = _read_qstring(data, offset)
            custom_name, offset = _read_qstring(data, offset)
            (
                native_order,
                custom_order,
                signal_type,
                channel_enabled,
                chip_channel,
                board_stream,
            ) = struct.unpack_from("<hhhhhh", data, offset)
            offset += 12

            trigger_mode, trigger_threshold, trigger_channel, trigger_edge = struct.unpack_from(
                "<hhhh", data, offset
            )
            offset += 8
            impedance_magnitude_ohms, impedance_phase = struct.unpack_from("<ff", data, offset)
            offset += 8

            if not channel_enabled:
                continue

            signal_type_name = signal_type_names.get(signal_type, f"unknown_{signal_type}")
            enabled_counts_by_type[signal_type_name] = enabled_counts_by_type.get(signal_type_name, 0) + 1

            if signal_type == 0:
                amplifier_channels.append(
                    {
                        "native_order": native_order,
                        "custom_order": custom_order,
                        "native_name": native_name,
                        "custom_name": custom_name,
                        "chip_channel": chip_channel,
                        "board_stream": board_stream,
                        "impedance_magnitude_ohms": impedance_magnitude_ohms,
                        "impedance_phase": impedance_phase,
                    }
                )

    return {
        "path": str(path),
        "magic": hex(magic),
        "version": f"{major}.{minor}",
        "sample_rate_hz": sample_rate_hz,
        "dsp_enabled": bool(dsp_enabled),
        "actual_dsp_cutoff_hz": actual_dsp_cutoff_hz,
        "actual_lower_bandwidth_hz": actual_lower_bandwidth_hz,
        "actual_upper_bandwidth_hz": actual_upper_bandwidth_hz,
        "desired_dsp_cutoff_hz": desired_dsp_cutoff_hz,
        "desired_lower_bandwidth_hz": desired_lower_bandwidth_hz,
        "desired_upper_bandwidth_hz": desired_upper_bandwidth_hz,
        "notch_filter_mode": notch_filter_mode,
        "desired_impedance_test_frequency_hz": desired_impedance_test_frequency_hz,
        "actual_impedance_test_frequency_hz": actual_impedance_test_frequency_hz,
        "notes": notes,
        "num_temp_sensor_channels": num_temp_sensor_channels,
        "eval_board_mode": eval_board_mode,
        "reference_channel": reference_channel,
        "groups": groups,
        "enabled_counts_by_type": enabled_counts_by_type,
        "num_amplifier_channels": len(amplifier_channels),
        "amplifier_channels": amplifier_channels,
        "bytes_parsed": offset,
        "file_size_bytes": len(data),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("info_rhd", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    info = read_rhd_info(args.info_rhd)
    text = json.dumps(info, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
