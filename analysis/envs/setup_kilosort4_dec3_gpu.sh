#!/usr/bin/env bash
set -euo pipefail

# Clean Kilosort4 environment for the Dec 3 haptic mouse recording.
# Intended for a Linux/Windows workstation with an NVIDIA GPU.

ENV_NAME="${1:-kilosort4-dec3}"
CUDA_INDEX_URL="${CUDA_INDEX_URL:-https://download.pytorch.org/whl/cu118}"

echo "Creating conda environment: ${ENV_NAME}"
conda env create -n "${ENV_NAME}" -f "$(dirname "$0")/kilosort4_dec3_gpu.yml"

echo "Installing CUDA PyTorch from: ${CUDA_INDEX_URL}"
conda run -n "${ENV_NAME}" python -m pip uninstall -y torch torchvision torchaudio || true
conda run -n "${ENV_NAME}" python -m pip install torch torchvision torchaudio --index-url "${CUDA_INDEX_URL}"

echo "Verification:"
conda run -n "${ENV_NAME}" python - <<'PY'
import importlib.metadata as md
import torch

print("python environment ok")
print("torch:", torch.__version__)
print("cuda_available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("cuda_device:", torch.cuda.get_device_name(0))
print("kilosort:", md.version("kilosort"))
print("spikeinterface:", md.version("spikeinterface"))
print("probeinterface:", md.version("probeinterface"))
print("pynapple:", md.version("pynapple"))
PY

echo
echo "Activate with:"
echo "  conda activate ${ENV_NAME}"
echo
echo "Open Kilosort GUI with:"
echo "  python -m kilosort"
