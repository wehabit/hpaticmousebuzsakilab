#!/usr/bin/env python3
"""Slice the Dec 4 256-ch amplifier.dat down to one probe's 128 channels.

Halves the Modal upload (185 GB -> ~93 GB) and lets Kilosort sort one probe with
a clean 0-127 channel map. dHPC = raw columns 0-127; LEC = raw columns 128-255.

  python analysis/slice_probe_dec4.py --probe lec   --out <path>/amplifier_lec.dat
  python analysis/slice_probe_dec4.py --probe dhpc  --out <path>/amplifier_dhpc.dat
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dat", type=Path,
                    default=Path("Haptic_Stim_session2_251204_131403/amplifier.dat"))
    ap.add_argument("--probe", choices=["lec", "dhpc"], required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n-channels", type=int, default=256)
    ap.add_argument("--chunk-samples", type=int, default=2_000_000)
    args = ap.parse_args()

    cols = slice(128, 256) if args.probe == "lec" else slice(0, 128)
    n = args.dat.stat().st_size // 2 // args.n_channels
    data = np.memmap(args.dat, dtype="<i2", mode="r", shape=(n, args.n_channels))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with args.out.open("wb") as fh:
        for s in range(0, n, args.chunk_samples):
            e = min(s + args.chunk_samples, n)
            np.asarray(data[s:e, cols]).tofile(fh)
            written += e - s
            if (s // args.chunk_samples) % 20 == 0:
                print(f"  {written}/{n} samples ({100*written/n:.0f}%)", flush=True)
    print(f"wrote {args.out} ({args.out.stat().st_size/1024**3:.1f} GB, 128 ch)")


if __name__ == "__main__":
    main()
