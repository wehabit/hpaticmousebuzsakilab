"""Run Dec 4 Kilosort4 on Modal — per probe (LEC or dHPC) or full 256 ch.

Assumes the raw binary + the matching kilosort_channel_map_<probe>.mat have been
uploaded to the Modal Volume `dec4-kilosort-data` (see stage_dec4_for_modal.sh).

  modal run          analysis/modal_kilosort_dec4.py --action check --probe lec
  modal run --detach analysis/modal_kilosort_dec4.py --action run   --probe lec
  modal run --detach analysis/modal_kilosort_dec4.py --action run   --probe dhpc
  modal run --detach analysis/modal_kilosort_dec4.py --action run   --probe full   # both, one pass

Always use --detach for run/concat: the sort takes well over an hour and an
attached run is cancelled the moment the client (terminal/agent) disconnects.

Probe -> (raw file in volume, channel count):
  lec  -> /dec4/amplifier_lec.dat   (128)   <- recommended first (the 50 Hz question)
  dhpc -> /dec4/amplifier_dhpc.dat  (128)
  full -> /dec4/amplifier.dat       (256)
"""
from __future__ import annotations

from pathlib import Path

import modal

APP_NAME = "dec4-kilosort"
VOLUME_NAME = "dec4-kilosort-data"
VOLUME_MOUNT = Path("/data")
SESSION_DIR = VOLUME_MOUNT / "dec4"
PREP_DIR = SESSION_DIR / "spike_sorting_prep"

PROBE_CFG = {
    "lec": ("amplifier_lec.dat", "kilosort_channel_map_lec.mat", 128),
    "dhpc": ("amplifier_dhpc.dat", "kilosort_channel_map_dhpc.mat", 128),
    "full": ("amplifier.dat", "kilosort_channel_map_full.mat", 256),
}

app = modal.App(APP_NAME)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "libglib2.0-0", "libgl1", "procps")
    .pip_install("torch==2.2.2", "torchvision==0.17.2", "torchaudio==2.2.2",
                 index_url="https://download.pytorch.org/whl/cu118")
    .pip_install("numpy<2", "scipy", "scikit-learn", "tqdm", "numba", "faiss-cpu", "kilosort==4.1.7")
)


@app.function(image=image, gpu="A10G", volumes={VOLUME_MOUNT: volume}, timeout=20 * 60)
def check_environment(probe: str = "lec") -> dict:
    import importlib.metadata as md
    import torch
    from kilosort import io

    raw_name, map_name, n_chan = PROBE_CFG[probe]
    raw = SESSION_DIR / raw_name
    probe_path = PREP_DIR / map_name
    status = {
        "probe": probe, "n_chan": n_chan,
        "torch": md.version("torch"), "kilosort": md.version("kilosort"),
        "cuda_available": torch.cuda.is_available(),
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "raw_exists": raw.exists(),
        "raw_size_gb": round(raw.stat().st_size / 1024**3, 2) if raw.exists() else None,
        "raw_samples_per_chan": (raw.stat().st_size // 2 // n_chan) if raw.exists() else None,
        "probe_exists": probe_path.exists(),
    }
    if probe_path.exists():
        p = io.load_probe(probe_path)
        status["probe_n_chan"] = int(p.get("n_chan", len(p.get("xc", []))))
    print(status)
    return status


@app.function(image=image, gpu="A10G", volumes={VOLUME_MOUNT: volume}, timeout=24 * 60 * 60)
def run_kilosort_dec4(probe: str = "lec", clear_cache: bool = True) -> dict:
    import json
    import time

    import torch
    from kilosort import io, run_kilosort

    raw_name, map_name, n_chan = PROBE_CFG[probe]
    raw = SESSION_DIR / raw_name
    probe_path = PREP_DIR / map_name
    results_dir = SESSION_DIR / f"kilosort4_results_{probe}"
    if not raw.exists():
        raise FileNotFoundError(f"Missing raw binary in volume: {raw}")
    if not probe_path.exists():
        raise FileNotFoundError(f"Missing probe map in volume: {probe_path}")
    if not torch.cuda.is_available():
        raise RuntimeError("No CUDA GPU visible in the Modal container.")

    results_dir.mkdir(parents=True, exist_ok=True)
    probe_obj = io.load_probe(probe_path)
    settings = {"fs": 20000, "n_chan_bin": n_chan,
                "data_dir": str(SESSION_DIR), "results_dir": str(results_dir)}
    started = time.time()
    result = run_kilosort(settings=settings, probe=probe_obj, filename=raw,
                          data_dtype="int16", clear_cache=clear_cache)
    ops, st, clu = result[:3]
    summary = {
        "probe": probe, "n_chan": n_chan, "raw_binary": str(raw), "probe_map": str(probe_path),
        "results_dir": str(results_dir), "elapsed_s": time.time() - started,
        "n_spikes": int(len(st)),
        "n_clusters": int(len(set(clu.tolist() if hasattr(clu, "tolist") else clu))),
        "cuda_device": torch.cuda.get_device_name(0),
    }
    (results_dir / "modal_kilosort_run_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    volume.commit()
    print(summary)
    return summary


@app.function(image=image, volumes={VOLUME_MOUNT: volume}, timeout=2 * 60 * 60)
def concat_chunks(probe: str = "lec") -> dict:
    """Reassemble /dec4/lec_chunks/chunk_*.bin into the single raw binary."""
    import shutil

    raw_name = PROBE_CFG[probe][0]
    chunk_dir = SESSION_DIR / f"{probe}_chunks"
    out = SESSION_DIR / raw_name
    parts = sorted(p for p in chunk_dir.iterdir() if p.name.startswith("chunk_"))
    if not parts:
        raise FileNotFoundError(f"no chunks in {chunk_dir}")
    with out.open("wb") as o:
        for p in parts:
            with p.open("rb") as fh:
                shutil.copyfileobj(fh, o, length=64 * 1024 * 1024)
    volume.commit()
    info = {"probe": probe, "n_chunks": len(parts), "out": str(out),
            "out_size_gb": round(out.stat().st_size / 1024**3, 2)}
    print(info)
    return info


@app.local_entrypoint()
def main(action: str = "check", probe: str = "lec") -> None:
    if action == "check":
        print(check_environment.remote(probe))
    elif action == "concat":
        print(concat_chunks.remote(probe))
    elif action == "run":
        print(run_kilosort_dec4.remote(probe))
    elif action == "spawn":
        # Fire-and-forget: queues the sort server-side and returns immediately.
        # Unlike .remote(), no streaming input is bound to this client, so the
        # job cannot be cancelled if the local process is killed/disconnected.
        # MUST be launched with --detach so the app outlives this entrypoint:
        #   modal run --detach analysis/modal_kilosort_dec4.py --action spawn --probe lec
        call = run_kilosort_dec4.spawn(probe)
        print(f"SPAWNED run_kilosort_dec4 probe={probe} call_id={call.object_id}")
        print("Poll for completion: modal_kilosort_run_summary.json in "
              f"/dec4/kilosort4_results_{probe} on volume {VOLUME_NAME}")
    else:
        raise ValueError("action must be 'check', 'concat', 'run', or 'spawn'")
