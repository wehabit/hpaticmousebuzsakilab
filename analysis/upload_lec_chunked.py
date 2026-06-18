#!/usr/bin/env python3
"""Resumable chunked upload of the LEC slice to the Modal volume.

Single-file uploads of ~93 GB kept failing (CLI timeout; presigned-URL expiry when
the laptop slept mid-transfer). This splits the file into small chunks, uploads each
separately (fast, fresh URL each time), and SKIPS chunks already on the volume — so
if it's interrupted, just rerun and it resumes. A Modal function then concatenates
the chunks back into one binary (see modal_kilosort_dec4.concat_chunks).
"""
import sys
from pathlib import Path

import modal

VOL = "dec4-kilosort-data"
SRC = Path("Haptic_Stim_session2_251204_131403/amplifier_lec.dat")
CHUNK = 4 * 1024**3          # 4 GiB/chunk -> ~22 chunks, each ~2 min at 35 MB/s
READ = 256 * 1024**2         # stream in 256 MiB reads (low memory)
DEST_DIR = "/dec4/lec_chunks"

vol = modal.Volume.from_name(VOL, create_if_missing=True)
total = SRC.stat().st_size
n = (total + CHUNK - 1) // CHUNK

existing = set()
try:
    existing = {Path(e.path).name for e in vol.listdir(DEST_DIR)}
except Exception:
    pass

print(f"{SRC} = {total/1024**3:.1f} GiB -> {n} chunks ({len(existing)} already uploaded)", flush=True)
tmp = Path("/tmp/lec_chunk.tmp")
with open(SRC, "rb") as f:
    for i in range(n):
        name = f"chunk_{i:03d}.bin"
        if name in existing:
            print(f"  skip {name} (already on volume)", flush=True)
            continue
        f.seek(i * CHUNK)
        remaining = min(CHUNK, total - i * CHUNK)
        with open(tmp, "wb") as out:
            got = 0
            while got < remaining:
                buf = f.read(min(READ, remaining - got))
                if not buf:
                    break
                out.write(buf)
                got += len(buf)
        with vol.batch_upload(force=True) as b:
            b.put_file(str(tmp), f"{DEST_DIR}/{name}")
        print(f"  uploaded {name} ({remaining/1024**3:.2f} GiB)  [{i+1}/{n}]", flush=True)
tmp.unlink(missing_ok=True)
print("ALL CHUNKS UPLOADED. Next: modal run --detach analysis/modal_kilosort_dec4.py --action concat --probe lec", flush=True)
