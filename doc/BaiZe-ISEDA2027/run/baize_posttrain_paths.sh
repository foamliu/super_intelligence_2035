#!/bin/bash
# baize_posttrain_paths.sh — Common path auto-detection for posttrain scripts
#
# Source this file at the top of any posttrain script:
#   source "$(dirname "$(realpath "${BASH_SOURCE[0]}")")/baize_posttrain_paths.sh"
#
# It auto-detects the correct NFS root:
#   .17 (posttrain): /nas_data is the NFS mount, /nas_train → /H100_train (empty)
#   .29/.12:         /nas_train is the NFS mount
#
# Exports:
#   NAS_ROOT          — /nas_data or /nas_train (whichever has data)
#   BAIZE_CODE_DIR    — super_intelligence_2035 code root
#   BAIZE_RUN_DIR     — this run/ directory
#   BAIZE_EXP_DIR     — nemo_experiments output root (created if missing on .17)
#   BAIZE_PY_ENV      — miniforge py310 bin dir (for pretrain-era scripts)
#   BAIZE_VENV_DIR    — verl cu124 venv path (created by setup script on 11/9)
#   BAIZE_VENV_PY     — verl cu124 venv python (may not exist yet)
#   BAIZE_MODEL_PATH  — MiniCPM5-2B model path
#   BAIZE_EDA_BASE    — eda_fastmcp local clone

# === Auto-detect NFS root ===
if [ -d "/nas_data/app.e0031982/code/super_intelligence_2035" ] && [ ! -d "/nas_train/app.e0031982/code/BaiZe-ISEDA2027" ]; then
    # .17 node: /nas_data is the real NFS mount
    export NAS_ROOT=/nas_data
elif [ -d "/nas_train/app.e0031982/code/super_intelligence_2035" ]; then
    # .29/.12 nodes: /nas_train is the NFS mount
    export NAS_ROOT=/nas_train
else
    echo "⚠️ Cannot detect NFS root — neither /nas_data nor /nas_train has expected structure" >&2
    export NAS_ROOT=/nas_data  # fallback
fi

# === Derived paths ===
export BAIZE_CODE_DIR="${NAS_ROOT}/app.e0031982/code/super_intelligence_2035"
export BAIZE_RUN_DIR="${BAIZE_CODE_DIR}/doc/BaiZe-ISEDA2027/run"
export BAIZE_EXP_DIR="${NAS_ROOT}/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments"
export BAIZE_PY_ENV="${NAS_ROOT}/app.e0031982/miniforge3/envs/py310/bin"

# === verl cu124 venv (created by baize_posttrain_setup_cu124_venv.sh on 11/9) ===
export BAIZE_VENV_DIR="${HOME}/code/verl_cu124_venv"
export BAIZE_VENV_PY="${BAIZE_VENV_DIR}/bin/python"

# === Model and EDA paths (local to .17) ===
export BAIZE_MODEL_PATH="/tmp/models/MiniCPM5-2B"
export BAIZE_EDA_BASE="${HOME}/code/eda_fastmcp"

# === Create output directory if it doesn't exist ===
mkdir -p "${BAIZE_EXP_DIR}/baize_posttrain_rl_grpo" 2>/dev/null || true
mkdir -p "${BAIZE_EXP_DIR}/baize_posttrain_sft" 2>/dev/null || true
mkdir -p "${BAIZE_EXP_DIR}/baize_posttrain_eval" 2>/dev/null || true

# === Echo for debug (sourced scripts can suppress) ===
if [ "${BAIZE_PATHS_VERBOSE:-0}" = "1" ]; then
    echo "[paths] NAS_ROOT=$NAS_ROOT"
    echo "[paths] BAIZE_RUN_DIR=$BAIZE_RUN_DIR"
    echo "[paths] BAIZE_EXP_DIR=$BAIZE_EXP_DIR"
    echo "[paths] BAIZE_VENV_PY=$BAIZE_VENV_PY (exists: $([ -f "$BAIZE_VENV_PY" ] && echo yes || echo no))"
    echo "[paths] BAIZE_MODEL_PATH=$BAIZE_MODEL_PATH (exists: $([ -d "$BAIZE_MODEL_PATH" ] && echo yes || echo no))"
fi
