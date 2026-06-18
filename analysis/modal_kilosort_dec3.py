"""Run Dec 3 Kilosort4 on Modal.

This file assumes the Dec 3 raw binary and spike-sorting prep folder have been
uploaded to the Modal Volume named `dec3-kilosort-data`.

  modal run          analysis/modal_kilosort_dec3.py --action check
  modal run --detach analysis/modal_kilosort_dec3.py --action run

Always use --detach for run: the sort takes well over an hour and an attached
run is cancelled the moment the client (terminal/agent) disconnects.
"""

from __future__ import annotations

from pathlib import Path

import modal


APP_NAME = "dec3-kilosort"
VOLUME_NAME = "dec3-kilosort-data"
VOLUME_MOUNT = Path("/data")
SESSION_DIR = VOLUME_MOUNT / "dec3"
RAW_BINARY = SESSION_DIR / "amplifier.dat"
PREP_DIR = SESSION_DIR / "spike_sorting_prep"
PROBE_PATH = PREP_DIR / "kilosort_channel_map.mat"
RESULTS_DIR = SESSION_DIR / "kilosort4_results"


app = modal.App(APP_NAME)
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "libglib2.0-0", "libgl1", "procps")
    .pip_install(
        "torch==2.2.2",
        "torchvision==0.17.2",
        "torchaudio==2.2.2",
        index_url="https://download.pytorch.org/whl/cu118",
    )
    .pip_install(
        "numpy<2",
        "scipy",
        "scikit-learn",
        "tqdm",
        "numba",
        "faiss-cpu",
        "kilosort==4.1.7",
    )
)


@app.function(
    image=image,
    gpu="A10G",
    volumes={VOLUME_MOUNT: volume},
    timeout=20 * 60,
)
def check_environment() -> dict:
    import importlib.metadata as md
    import torch
    from kilosort import io

    status = {
        "torch": md.version("torch"),
        "kilosort": md.version("kilosort"),
        "cuda_available": torch.cuda.is_available(),
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "raw_exists": RAW_BINARY.exists(),
        "raw_size_gb": round(RAW_BINARY.stat().st_size / 1024**3, 3) if RAW_BINARY.exists() else None,
        "probe_exists": PROBE_PATH.exists(),
    }
    if PROBE_PATH.exists():
        probe = io.load_probe(PROBE_PATH)
        status["probe_keys"] = sorted(probe.keys())
        status["probe_n_chan"] = int(probe.get("n_chan", probe.get("n_chans", -1)))
    print(status)
    return status


@app.function(
    image=image,
    gpu="A10G",
    volumes={VOLUME_MOUNT: volume},
    timeout=24 * 60 * 60,
)
def run_kilosort_dec3(clear_cache: bool = True) -> dict:
    import json
    import time

    import torch
    from kilosort import io, run_kilosort

    if not RAW_BINARY.exists():
        raise FileNotFoundError(f"Missing raw binary in Modal volume: {RAW_BINARY}")
    if not PROBE_PATH.exists():
        raise FileNotFoundError(f"Missing probe file in Modal volume: {PROBE_PATH}")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is not visible inside the Modal container.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    probe = io.load_probe(PROBE_PATH)
    settings = {
        "fs": 20000,
        "n_chan_bin": 128,
        "data_dir": str(SESSION_DIR),
        "results_dir": str(RESULTS_DIR),
    }

    started = time.time()
    result = run_kilosort(
        settings=settings,
        probe=probe,
        filename=RAW_BINARY,
        data_dtype="int16",
        clear_cache=clear_cache,
    )
    ops, st, clu = result[:3]
    elapsed_s = time.time() - started

    summary = {
        "raw_binary": str(RAW_BINARY),
        "probe": str(PROBE_PATH),
        "results_dir": str(RESULTS_DIR),
        "elapsed_s": elapsed_s,
        "n_spikes": int(len(st)),
        "n_clusters": int(len(set(clu.tolist()))) if hasattr(clu, "tolist") else int(len(set(clu))),
        "cuda_device": torch.cuda.get_device_name(0),
    }
    summary_path = RESULTS_DIR / "modal_kilosort_run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")

    # Kilosort writes inside `results_dir` or a `kilosort4` child depending on
    # version/settings. Commit the whole mounted volume so files persist.
    volume.commit()
    print(summary)
    return summary


@app.local_entrypoint()
def main(action: str = "check") -> None:
    if action == "check":
        print(check_environment.remote())
    elif action == "run":
        print(run_kilosort_dec3.remote())
    else:
        raise ValueError("Use action='check' or action='run'.")
