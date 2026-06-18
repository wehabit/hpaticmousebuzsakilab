#!/usr/bin/env python3
"""Dec 4 spike-sorting prep: channel map / probe geometry / trial windows.

Writes the metadata SpikeInterface + Kilosort need, WITHOUT touching raw data.
Two probes: dHPC (Port A, 0-127, four 32-ch groups) and LEC (Port B, 128-255,
two 64-ch shanks). Geometry is PROVISIONAL (probes separated in x; linear within
group) — sufficient for a SpikeInterface recording view; final Kilosort runs on
Modal/GPU and should use the real H12/H15 site maps.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from channel_groups_dec4 import ANALYSIS_GROUPS

OUT = Path("analysis/outputs/dec4/spike_sorting_prep")
RAW = Path("Haptic_Stim_session2_251204_131403/amplifier.dat")
SEQ = Path("analysis/outputs/dec4/dec4_condition_sequence.csv")
BADJSON = Path("analysis/bad_channels_dec4.json")
N_CH = 256
FS = 20000.0


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    bad = set(json.loads(BADJSON.read_text())["candidate_bad_channels"])

    group_list = list(ANALYSIS_GROUPS.items())
    rows = []
    for kcoord, (gname, chans) in enumerate(group_list, start=1):
        probe = "dHPC" if gname.startswith("A") else "LEC"
        probe_x = 0.0 if probe == "dHPC" else 1500.0          # probes far apart in x
        col_x = probe_x + (kcoord % 4) * 60.0                  # spread groups within a probe
        for i, ch in enumerate(chans):
            rows.append({
                "channel": int(ch), "probe": probe, "group": gname, "kcoord": kcoord,
                "x_um_provisional": float(col_x),
                "y_um_provisional": float(i * 20),
                "is_bad": bool(ch in bad),
                "connected": bool(ch not in bad),
            })
    meta = pd.DataFrame(rows).sort_values("channel").reset_index(drop=True)
    meta.to_csv(OUT / "channel_metadata.csv", index=False)

    # params.py for Phy / Kilosort
    (OUT / "params.py").write_text(
        f'dat_path = r"{RAW}"\nn_channels_dat = {N_CH}\ndtype = "int16"\noffset = 0\n'
        f'sample_rate = {FS}\nhp_filtered = False\n'
    )

    # trial windows for ON/OFF spike analysis (recording-time seconds)
    seq = pd.read_csv(SEQ)
    tw = seq[["trial_number", "condition", "amplitude", "freq",
              "recording_start_time_s", "recording_end_time_s"]].copy()
    tw["on_start_s"] = tw["recording_start_time_s"]
    tw["on_end_s"] = tw["recording_start_time_s"] + 3.0
    tw["off_start_s"] = tw["recording_start_time_s"] + 3.0
    tw["off_end_s"] = tw["recording_start_time_s"] + 6.0
    tw.to_csv(OUT / "trial_windows.csv", index=False)

    summary = {
        "raw_dat": str(RAW), "n_channels": N_CH, "sample_rate_hz": FS,
        "good_channels": int(meta["connected"].sum()),
        "bad_channels": sorted(int(c) for c in bad),
        "probes": {"dHPC": "0-127 (4x32, H12_2)", "LEC": "128-255 (2x64, H15)"},
        "n_trials": int(len(tw)),
        "geometry_note": "PROVISIONAL (probes split in x, linear within group). "
                         "Final Kilosort should use the real H12/H15 site maps.",
        "next_step": "GPU Kilosort on Modal (adapt analysis/modal_kilosort_dec3.py: n_channels=256, "
                     "this channel map), then cluster_quality / spike_peth_on_off / high_confidence "
                     "on the curated output, as for Dec 3.",
    }
    (OUT / "spike_sorting_prep_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
