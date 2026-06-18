#!/usr/bin/env python3
"""Resumable chunked upload of a probe slice to the Modal volume.

Generalized from upload_lec_chunked.py. Single-file uploads of ~93 GB kept
failing (CLI timeout; presigned-URL expiry on laptop sleep). This splits the
file into chunks, uploads each separately, and SKIPS chunks already on the
volume -- so if interrupted, just rerun and it resumes. Then concatenate with:

  modal run --detach analysis/modal_kilosort_dec4.py --action concat --probe <probe>

Usage:
  python analysis/upload_probe_chunked.py --probe dhpc
"""
import argparse
from pathlib import Path

import modal

VOL = "dec4-kilosort-data"
CHUNK = 4 * 1024**3          # 4 GiB/chunk
READ = 256 * 1024**2         # 256 MiB streaming reads (low memory)
SESSION = Path("Haptic_Stim_session2_251204_131403")

ap = argparse.ArgumentParser()
ap.add_argument("--probe", choices=["lec", "dhpc", "full"], required=True)
args = ap.parse_args()

src = SESSION / (f"amplifier_{args.probe}.dat" if args.probe != "full" else "amplifier.dat")
dest_dir = f"/dec4/{args.probe}_chunks"
if not src.exists():
    raise SystemExit(f"Missing {src}. Slice it first with slice_probe_dec4.py")

vol = modal.Volume.from_name(VOL, create_if_missing=True)
total = src.stat().st_size
n = (total + CHUNK - 1) // CHUNK

existing = set()
try:
    existing = {Path(e.path).name for e in vol.listdir(dest_dir)}
except Exception:
    pass

print(f"{src} = {total/1024**3:.1f} GiB -> {n} chunks ({len(existing)} already uploaded)", flush=True)
tmp = Path(f"/tmp/{args.probe}_chunk.tmp")
with open(src, "rb") as f:
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
            b.put_file(str(tmp), f"{dest_dir}/{name}")
        print(f"  uploaded {name} ({remaining/1024**3:.2f} GiB)  [{i+1}/{n}]", flush=True)
tmp.unlink(missing_ok=True)
print(f"ALL CHUNKS UPLOADED. Next: "
      f"modal run --detach analysis/modal_kilosort_dec4.py --action concat --probe {args.probe}",
      flush=True)
