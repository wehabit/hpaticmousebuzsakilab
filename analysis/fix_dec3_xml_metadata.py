#!/usr/bin/env python3
"""Repair Dec 3 XML metadata to the 128 recorded amplifier channels."""

from __future__ import annotations

import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


DEFAULT_SESSION_DIR = Path("Haptic_Stim_session1_251203_143031")
DEFAULT_OUTPUT = Path("analysis/outputs/dec3/metadata_correction_summary.json")


def channel_value(element: ET.Element) -> int | None:
    if element.tag != "channel" or element.text is None:
        return None
    try:
        return int(element.text.strip())
    except ValueError:
        return None


def remove_invalid_channels(root: ET.Element, n_channels: int) -> dict[str, int]:
    parent = {child: parent for parent in root.iter() for child in parent}
    removed = 0
    for element in list(root.iter("channel")):
        value = channel_value(element)
        if value is None or value < n_channels:
            continue
        parent[element].remove(element)
        removed += 1

    empty_groups = 0
    for group in list(root.iter("group")):
        if any(channel_value(ch) is not None for ch in group.iter("channel")):
            continue
        group_parent = parent.get(group)
        if group_parent is not None:
            group_parent.remove(group)
            empty_groups += 1

    return {"invalid_channel_elements_removed": removed, "empty_groups_removed": empty_groups}


def group_sizes(root: ET.Element) -> list[int]:
    groups = root.findall(".//anatomicalDescription/channelGroups/group")
    return [len(group.findall("channel")) for group in groups]


def repair_xml(path: Path, n_channels: int, backup: bool) -> dict[str, object]:
    if backup:
        backup_path = path.with_name(path.stem + "_pre_repair.xml")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
    else:
        backup_path = None

    tree = ET.parse(path)
    root = tree.getroot()

    acquisition = root.find("acquisitionSystem")
    if acquisition is None:
        raise ValueError(f"Missing acquisitionSystem in {path}")
    n_channels_node = acquisition.find("nChannels")
    if n_channels_node is None:
        n_channels_node = ET.SubElement(acquisition, "nChannels")
    n_channels_before = n_channels_node.text
    n_channels_node.text = str(n_channels)

    removal = remove_invalid_channels(root, n_channels)
    ET.indent(tree, space=" ")
    tree.write(path, encoding="utf-8", xml_declaration=True)

    repaired = ET.parse(path).getroot()
    remaining_invalid = [
        value for value in (channel_value(ch) for ch in repaired.iter("channel"))
        if value is not None and value >= n_channels
    ]
    return {
        "path": str(path),
        "backup": str(backup_path) if backup_path else None,
        "n_channels_before": n_channels_before,
        "n_channels_after": n_channels,
        "channel_group_sizes_after": group_sizes(repaired),
        "remaining_invalid_channel_count": len(remaining_invalid),
        **removal,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-dir", type=Path, default=DEFAULT_SESSION_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--n-channels", type=int, default=128)
    parser.add_argument("--no-backup", action="store_true")
    args = parser.parse_args()

    active = args.session_dir / "amplifier.xml"
    corrected = args.session_dir / "amplifier_corrected_128ch.xml"
    targets = [active]
    if corrected.exists() and corrected != active:
        targets.append(corrected)

    results = [repair_xml(path, args.n_channels, backup=not args.no_backup) for path in targets]
    summary = {
        "session_dir": str(args.session_dir),
        "reason": (
            "info.rhd and file-size checks show Dec 3 has 128 amplifier channels; "
            "XML metadata must not expose phantom channels 128-255."
        ),
        "n_channels_after": args.n_channels,
        "valid_amplifier_channels": f"0-{args.n_channels - 1}",
        "invalid_phantom_channels_removed": f"{args.n_channels}-255",
        "targets": results,
        "note": (
            "This fixes channel count and removes phantom channel elements from "
            "XML metadata. Exact Cambridge NeuroTech H12_2 site order still needs "
            "probe-map confirmation before anatomical claims."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
