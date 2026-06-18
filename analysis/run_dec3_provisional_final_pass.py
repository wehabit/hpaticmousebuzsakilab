#!/usr/bin/env python3
"""Run Dec 3 analyses using the explicit provisional final-pass settings."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(command: list[str], cwd: Path) -> None:
    print("\n" + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("analysis/final_preprocessing_dec3.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/outputs/dec3/provisional_final_pass"))
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    config = json.loads((repo / args.config).read_text())
    source_files = config["source_files"]
    channels = config["channels"]
    reference = config["reference"]["chosen_for_provisional_final_pass"]
    bad_channel_field = config.get("bad_channel_field_for_final_pass", "definite_bad_channels")
    bad_channel_json = source_files.get("bad_channel_definite", source_files["bad_channel_candidates"])

    output_dir = repo / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "settings_used.json").write_text(json.dumps(config, indent=2) + "\n")

    common = [
        "--lfp",
        source_files["lfp"],
        "--sequence",
        source_files["sequence"],
        "--bad-channels-json",
        bad_channel_json,
        "--bad-channel-field",
        bad_channel_field,
        "--n-channels",
        str(channels["n_channels"]),
        "--sample-rate-hz",
        str(channels["sample_rate_hz"]),
    ]

    run(
        [
            sys.executable,
            "analysis/reference_sensitivity_lfp.py",
            *common,
            "--output-dir",
            str(output_dir / "reference_sensitivity_lfp"),
            "--window-duration-s",
            "2.8",
            "--artifact-margin-s",
            "0.1",
            "--band-half-width-hz",
            "1.0",
            "--max-trials-per-condition",
            "200",
        ],
        cwd=repo,
    )

    run(
        [
            sys.executable,
            "analysis/phase_locking_lfp.py",
            *common,
            "--output-dir",
            str(output_dir / "phase_locking_lfp"),
            "--reference-mode",
            reference,
            "--pre-s",
            "1",
            "--post-s",
            "4",
            "--band-half-width-hz",
            "1.5",
            "--max-trials-per-condition",
            "200",
        ],
        cwd=repo,
    )

    html = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Dec 3 Provisional Final Pass</title>",
        "<style>body{font-family:Arial,sans-serif;margin:24px;max-width:1200px} a{color:#0f6b78;font-weight:600}</style>",
        "</head><body><h1>Dec 3 Provisional Final Pass</h1>",
        "<p>These outputs used <code>analysis/final_preprocessing_dec3.json</code>.</p>",
        "<p>Bad channels are treated as confirmed for the current Dec 3 analysis pass. Anatomy labels remain provisional.</p>",
        "<ul>",
        "<li><a href='settings_used.json'>settings_used.json</a></li>",
        "<li><a href='reference_sensitivity_lfp/index.html'>reference_sensitivity_lfp</a></li>",
        "<li><a href='phase_locking_lfp/index.html'>phase_locking_lfp</a></li>",
        "</ul>",
        "</body></html>",
    ]
    (output_dir / "index.html").write_text("\n".join(html))
    print(json.dumps({"output_dir": str(output_dir), "index": str(output_dir / "index.html")}, indent=2))


if __name__ == "__main__":
    main()
