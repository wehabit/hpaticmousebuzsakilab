#!/usr/bin/env bash
set -euo pipefail

VOLUME_NAME="${VOLUME_NAME:-dec3-kilosort-data}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SESSION_DIR="${SESSION_DIR:-${REPO_DIR}/Haptic_Stim_session1_251203_143031}"
PREP_DIR="${PREP_DIR:-analysis/outputs/dec3/spike_sorting_prep}"

echo "Creating Modal volume if needed: ${VOLUME_NAME}"
modal volume create "${VOLUME_NAME}" || true

echo "Uploading Dec 3 raw amplifier.dat. This is about 51 GB and may take a while."
modal volume put -f "${VOLUME_NAME}" "${SESSION_DIR}/amplifier.dat" /dec3/amplifier.dat

echo "Uploading spike-sorting prep folder."
modal volume put -f "${VOLUME_NAME}" "${PREP_DIR}" /dec3/spike_sorting_prep

echo "Volume contents:"
modal volume ls "${VOLUME_NAME}" /dec3

echo
echo "Next sanity check:"
echo "  modal run analysis/modal_kilosort_dec3.py --action check"
echo
echo "Run Kilosort:"
echo "  modal run analysis/modal_kilosort_dec3.py --action run"
echo
echo "Download outputs after completion:"
echo "  modal volume get ${VOLUME_NAME} /dec3/kilosort4_results analysis/outputs/dec3/modal_kilosort4_results"
