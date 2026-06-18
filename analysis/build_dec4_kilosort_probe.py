#!/usr/bin/env python3
"""Build Kilosort channel-map .mat files for Dec 4 from channel_metadata.csv.

Writes three probe maps into analysis/outputs/dec4/spike_sorting_prep/:
  - kilosort_channel_map_full.mat   256 ch (both probes; kcoords separate them)
  - kilosort_channel_map_lec.mat    128 ch, LEC only (local index 0-127 -> raw cols 128-255)
  - kilosort_channel_map_dhpc.mat   128 ch, dHPC only (local index 0-127 -> raw cols 0-127)

The per-probe maps assume the raw .dat has been sliced to that probe's columns
(see slice_probe_dec4.py). `connected` masks the Dec 4 bad channels so Kilosort
ignores them. Geometry is PROVISIONAL (probes split in x, linear within group);
replace with the real H12/H15 site maps before any final anatomical claim.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import savemat

PREP = Path("analysis/outputs/dec4/spike_sorting_prep")


def write_map(path: Path, sub: pd.DataFrame) -> None:
    sub = sub.reset_index(drop=True)
    n = len(sub)
    chan0 = np.arange(n, dtype=np.int32)
    savemat(path, {
        "chanMap": (chan0 + 1).reshape(-1, 1),
        "chanMap0ind": chan0.reshape(-1, 1),
        "connected": sub["connected"].to_numpy(bool).reshape(-1, 1),
        "xcoords": sub["x_um_provisional"].to_numpy(float).reshape(-1, 1),
        "ycoords": sub["y_um_provisional"].to_numpy(float).reshape(-1, 1),
        "kcoords": sub["kcoord"].to_numpy(np.int32).reshape(-1, 1),
        "name": np.array([path.stem]),
    })
    print(f"{path.name}: {n} ch, connected={int(sub['connected'].sum())}, "
          f"kcoords={sorted(sub['kcoord'].unique().tolist())}")


def main() -> None:
    meta = pd.read_csv(PREP / "channel_metadata.csv").sort_values("channel")
    write_map(PREP / "kilosort_channel_map_full.mat", meta)
    write_map(PREP / "kilosort_channel_map_lec.mat", meta[meta.probe == "LEC"])
    write_map(PREP / "kilosort_channel_map_dhpc.mat", meta[meta.probe == "dHPC"])


if __name__ == "__main__":
    main()
