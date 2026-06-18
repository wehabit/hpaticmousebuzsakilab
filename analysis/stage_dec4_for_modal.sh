#!/usr/bin/env bash
# Stage Dec 4 data to a Modal volume for Kilosort. Requires `modal token new` first.
#   PROBE=lec  bash analysis/stage_dec4_for_modal.sh   # upload LEC slice (~93 GB) [recommended]
#   PROBE=dhpc bash analysis/stage_dec4_for_modal.sh   # upload dHPC slice (~93 GB)
#   PROBE=full bash analysis/stage_dec4_for_modal.sh   # upload full 256-ch (~185 GB)
set -euo pipefail

PROBE="${PROBE:-lec}"
VOLUME_NAME="${VOLUME_NAME:-dec4-kilosort-data}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SESSION_DIR="${SESSION_DIR:-${REPO_DIR}/Haptic_Stim_session2_251204_131403}"
PREP_DIR="${PREP_DIR:-analysis/outputs/dec4/spike_sorting_prep}"

modal volume create "${VOLUME_NAME}" || true

case "${PROBE}" in
  lec)  RAW="${SESSION_DIR}/amplifier_lec.dat";  DEST="/dec4/amplifier_lec.dat" ;;
  dhpc) RAW="${SESSION_DIR}/amplifier_dhpc.dat"; DEST="/dec4/amplifier_dhpc.dat" ;;
  full) RAW="${SESSION_DIR}/amplifier.dat";      DEST="/dec4/amplifier.dat" ;;
  *) echo "PROBE must be lec|dhpc|full"; exit 1 ;;
esac

if [ ! -f "${RAW}" ]; then
  echo "Missing ${RAW}."
  [ "${PROBE}" != "full" ] && echo "Create it first:  python analysis/slice_probe_dec4.py --probe ${PROBE} --out ${RAW}"
  exit 1
fi

echo "Uploading prep folder (channel maps)..."
modal volume put -f "${VOLUME_NAME}" "${PREP_DIR}" /dec4/spike_sorting_prep
echo "Uploading ${RAW} -> ${DEST} (large; may take hours)..."
modal volume put -f "${VOLUME_NAME}" "${RAW}" "${DEST}"
modal volume ls "${VOLUME_NAME}" /dec4

cat <<EOF

Next:
  modal run analysis/modal_kilosort_dec4.py --action check --probe ${PROBE}
  modal run analysis/modal_kilosort_dec4.py --action run   --probe ${PROBE}
Download results when done:
  modal volume get ${VOLUME_NAME} /dec4/kilosort4_results_${PROBE} analysis/outputs/dec4/modal_kilosort4_results_${PROBE}
EOF
