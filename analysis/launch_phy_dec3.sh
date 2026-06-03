#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KS_DIR="${REPO_DIR}/analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results"
LOG_PATH="${KS_DIR}/phy_launch.log"
PHY_BIN="/opt/anaconda3/envs/phy-dec3-legacy/bin/phy"

COMMAND="cd $(printf '%q' "${KS_DIR}") && $(printf '%q' "${PHY_BIN}") template-gui --clear-state params.py 2>&1 | tee $(printf '%q' "${LOG_PATH}")"

osascript - "${COMMAND}" <<'APPLESCRIPT'
on run argv
tell application "Terminal"
    activate
    do script item 1 of argv
end tell
end run
APPLESCRIPT

echo "Opened Phy in a Terminal window."
echo "Log: ${LOG_PATH}"
