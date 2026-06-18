#!/usr/bin/env bash
# Pull the full Dec 4 Kilosort output off the Modal volume for local re-analysis.
# Run AFTER the sort finishes (check: `modal app list` shows dec4-kilosort stopped,
# and /dec4/kilosort4_results_lec contains spike_times.npy + run summary).
#
#   PROBE=lec bash analysis/download_dec4_kilosort.sh
set -euo pipefail

PROBE="${PROBE:-lec}"
VOL="${VOL:-dec4-kilosort-data}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODAL="${REPO_DIR}/.venv-dec3/bin/modal"
REMOTE="/dec4/kilosort4_results_${PROBE}"
DEST="${REPO_DIR}/analysis/outputs/dec4/modal_kilosort4_results_${PROBE}"

export MODAL_PROFILE="${MODAL_PROFILE:-pardis-stanford}"

echo "Remote listing (${REMOTE}):"
"${MODAL}" volume ls "${VOL}" "${REMOTE}"

mkdir -p "${DEST}"
echo "Downloading ${VOL}:${REMOTE} -> ${DEST} (force-overwrite) ..."
"${MODAL}" volume get -f "${VOL}" "${REMOTE}" "${DEST}"

echo ""
echo "Downloaded files:"
ls -la "${DEST}" 2>/dev/null || true
echo ""
echo "Re-analysis inputs that must be present (Kilosort/Phy standard set):"
for f in spike_times.npy spike_clusters.npy amplitudes.npy templates.npy \
         channel_map.npy channel_positions.npy ops.npy params.py \
         cluster_KSLabel.tsv modal_kilosort_run_summary.json; do
  if [ -e "${DEST}/${f}" ] || compgen -G "${DEST}/**/${f}" >/dev/null 2>&1; then
    echo "  OK   ${f}"
  else
    echo "  MISS ${f}  (check listing above; name may differ by KS version)"
  fi
done
echo ""
echo "Note: raw slice (amplifier_lec.dat) + probe map are already local, so Kilosort can"
echo "be re-run without re-downloading. The Modal volume persists until explicitly deleted."
