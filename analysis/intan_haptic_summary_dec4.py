#!/usr/bin/env python3
"""Dec 4 session metadata + authoritative condition sequence (NO digitalin.dat).

Dec 4 differs from Dec 3 in two ways that matter here:

1. Two probes / 256 amplifier channels (Port A = dHPC, Port B = LEC).
2. The controller's digital TTL was enabled in the Intan config, but the
   ``digitalin.dat`` (and analog-in) files were NOT shared for this session --
   only ``amplifier.dat`` / ``auxiliary.dat`` / ``time.dat``. So unlike Dec 3
   there is no TTL to audit; trial timing comes entirely from the randomized
   controller schedule (cmd_config JSON) plus the controller log's wall-clock
   START time aligned to the Intan recording start.

Recording-start offset (seconds from Intan recording start to controller START):
  Intan filename timestamp  251204_131403  -> recording start 13:14:03
  Controller log START      13:45:29.78    (cmd_config_..._Dec4th log)
  offset = 13:45:29.78 - 13:14:03 = 1886.78 s
This same method reproduces the Dec 3 offset exactly (Dec 3 START 14:41:11 vs
filename 14:30:31 = 640 s), so it is the validated approach.

Outputs (mirroring the Dec 3 step files):
  - stimulus_config_schedule.csv
  - dec4_condition_sequence.csv   (authoritative trial labels + ON/OFF windows)
  - session_summary.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

# Reuse the verified Dec 3 schedule parser unchanged.
from intan_haptic_summary import (
    add_recording_times,
    load_stimulus_config,
    parse_xml_metadata,
    write_config_schedule,
)


def derive_offset_from_log(session_dir: Path, log_path: Path | None) -> float | None:
    """offset = controller START wall-clock - Intan recording-start (filename)."""
    name = session_dir.name  # e.g. Haptic_Stim_session2_251204_131403
    try:
        stamp = name.split("_")[-1]  # 131403
        date_part = name.split("_")[-2]  # 251204
        rec_start = datetime.strptime(date_part + stamp, "%y%m%d%H%M%S")
    except (ValueError, IndexError):
        return None
    if log_path is None or not log_path.exists():
        return None
    start_dt = None
    for line in log_path.read_text(errors="ignore").splitlines():
        if "START triggered at" in line:
            iso = line.split("START triggered at", 1)[1].strip().split(" ")[0]
            start_dt = datetime.fromisoformat(iso)
            break
    if start_dt is None:
        return None
    return (start_dt - rec_start).total_seconds()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--log", type=Path, default=None,
                        help="Controller log used to derive the recording-start offset.")
    parser.add_argument("--recording-start-offset-s", type=float, default=None,
                        help="Override the auto-derived offset.")
    parser.add_argument("--sequence-name", default="dec4_condition_sequence.csv")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    xml_path = args.session_dir / "amplifier.xml"
    amplifier_path = args.session_dir / "amplifier.dat"
    time_path = args.session_dir / "time.dat"

    metadata = parse_xml_metadata(xml_path)

    offset = args.recording_start_offset_s
    auto_offset = derive_offset_from_log(args.session_dir, args.log)
    if offset is None:
        offset = auto_offset

    stimuli = add_recording_times(load_stimulus_config(args.config), offset)

    # Write stimulus_config_schedule.csv + a dec3-style sequence, then rename the
    # sequence to the dec4 name (write_config_schedule emits dec3_condition_sequence.csv).
    write_config_schedule(args.output_dir, stimuli)
    dec3_seq = args.output_dir / "dec3_condition_sequence.csv"
    dec4_seq = args.output_dir / args.sequence_name
    if dec3_seq.exists():
        dec3_seq.replace(dec4_seq)

    conditions: dict[str, int] = {}
    for s in stimuli:
        conditions[s["condition"]] = conditions.get(s["condition"], 0) + 1

    raw_samples = amplifier_path.stat().st_size // 2 // metadata["n_channels"]
    summary = {
        "session_dir": str(args.session_dir),
        "config": str(args.config),
        "metadata": metadata,
        "files": {
            "amplifier_dat_bytes": amplifier_path.stat().st_size,
            "time_dat_bytes": time_path.stat().st_size if time_path.exists() else None,
            "digitalin_present": (args.session_dir / "digitalin.dat").exists(),
        },
        "n_channels": metadata["n_channels"],
        "raw_samples_per_channel": int(raw_samples),
        "raw_duration_s": raw_samples / metadata["sampling_rate_hz"],
        "recording_start_offset_s": offset,
        "auto_derived_offset_s": auto_offset,
        "stimulus_config_count": len(stimuli),
        "condition_counts": conditions,
        "baseline_start_recording_s": offset,
        "first_trial_recording_start_s": (stimuli[0]["recording_start_time_s"]
                                          if stimuli and offset is not None else None),
        "last_trial_recording_end_s": (stimuli[-1]["recording_end_time_s"]
                                       if stimuli and offset is not None else None),
        "ttl_note": (
            "Dec 4 has no digitalin.dat (TTL/analog-in not shared). Trial timing is "
            "from the controller schedule + log START offset only; there is no TTL QC "
            "table for this session."
        ),
        "sequence_csv": str(dec4_seq),
    }
    with (args.output_dir / "session_summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
