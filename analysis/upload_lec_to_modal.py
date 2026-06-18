#!/usr/bin/env python3
"""Robust large-file upload of the Dec 4 LEC slice to the Modal volume.

The `modal volume put` CLI times out on a single ~93 GB file. Volume.batch_upload
is the SDK path designed for large files. Run with the active modal profile.
"""
import time
from pathlib import Path

import modal

VOL = "dec4-kilosort-data"
SRC = Path("Haptic_Stim_session2_251204_131403/amplifier_lec.dat")
DEST = "/dec4/amplifier_lec.dat"

vol = modal.Volume.from_name(VOL, create_if_missing=True)
print(f"uploading {SRC} ({SRC.stat().st_size/1024**3:.1f} GB) -> {VOL}{DEST}", flush=True)
t0 = time.time()
with vol.batch_upload(force=True) as batch:
    batch.put_file(str(SRC), DEST)
print(f"upload committed in {(time.time()-t0)/60:.1f} min", flush=True)
print("volume now contains:", flush=True)
for entry in vol.listdir("/dec4"):
    print("  ", entry.path, flush=True)
