#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KS_DIR="${REPO_DIR}/analysis/outputs/dec3/modal_kilosort4_results/kilosort4_results"
PHY_BIN="/opt/anaconda3/envs/phy-dec3-legacy/bin/phy"
LOG_PATH="${KS_DIR}/phy_launch.log"

cd "${KS_DIR}"
"${PHY_BIN}" template-gui --clear-state params.py 2>&1 | tee "${LOG_PATH}"
