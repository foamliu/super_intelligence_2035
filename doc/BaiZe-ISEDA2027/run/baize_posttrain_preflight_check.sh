#!/bin/bash
set -euo pipefail

# === Auto-detect paths (R12: /nas_train empty on .17) ===
SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
source "$SCRIPT_DIR/baize_posttrain_paths.sh"
cd "$BAIZE_RUN_DIR"

echo "=== BaiZe Post-Train 11/9 Preflight Check (R12) ==="
echo "Time: $(date)"
echo "NAS_ROOT: $NAS_ROOT"
echo ""

PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    local cmd="$2"
    echo -n "[$name] ... "
    if eval "$cmd" 2>/dev/null; then
        echo "PASS"
        PASS=$((PASS+1))
    else
        echo "FAIL"
        FAIL=$((FAIL+1))
    fi
}

warn_check() {
    local name="$1"
    local cmd="$2"
    echo -n "[$name] ... "
    if eval "$cmd" 2>/dev/null; then
        echo "PASS"
        PASS=$((PASS+1))
    else
        echo "WARN"
        WARN=$((WARN+1))
    fi
}

# 1. Basic
check "CUDA>=12.4" "nvcc --version | grep -q 'release 12.4'"
check "Node=.17" "hostname -I | grep -q '10.252.32.17'"
check "RunDir" "[ -d \"$BAIZE_RUN_DIR\" ]"

# 2. venv (R12: SGLang not vLLM)
VENV_PATH="$BAIZE_VENV_DIR"
check "cu124 venv" "[ -d \"$VENV_PATH\" ]"
if [ -d "$VENV_PATH" ]; then
    check "torch cu124" "$VENV_PATH/bin/python -c 'import torch; print(torch.version.cuda)' | grep -q '12.4'"
    check "cuda available" "$VENV_PATH/bin/python -c 'import torch; exit(0 if torch.cuda.is_available() else 1)'"
    check "SGLang" "$VENV_PATH/bin/python -c 'import sglang; exit(0)'"
    check "verl" "$VENV_PATH/bin/python -c 'import verl; exit(0)'"
    check "ray" "$VENV_PATH/bin/python -c 'import ray; exit(0)'"
    check "flash_attn" "$VENV_PATH/bin/python -c 'import flash_attn; exit(0)'"
fi

# 3. Model & data
check "MiniCPM5-2B" "[ -d \"$BAIZE_MODEL_PATH\" ] && [ -f \"$BAIZE_MODEL_PATH/config.json\" ]"
check "eda_fastmcp" "[ -d \"$BAIZE_EDA_BASE\" ] && [ -f \"$BAIZE_EDA_BASE/docs/API_INFO_MERGED_V3.json\" ]"
check "158-case" "[ -f \"$BAIZE_EDA_BASE/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl\" ]"
check "RL parquet" "[ -f \"$BAIZE_RUN_DIR/rl_pyaether_synth_v2.parquet\" ]"
check "SFT parquet" "[ -f \"$BAIZE_RUN_DIR/sft_pyaether_corpus.parquet\" ]"
check "SFT JSONL" "[ -f \"$BAIZE_RUN_DIR/sft_pyaether_corpus.jsonl\" ]"
check "RL JSONL" "[ -f \"$BAIZE_RUN_DIR/rl_pyaether_synth_v2.jsonl\" ]"
check "contamination gate" "[ -f \"$BAIZE_RUN_DIR/baize_posttrain_contamination_gate.sh\" ]"

# 4. Scripts
check "API profiler py" "python3 -m py_compile \"$BAIZE_RUN_DIR/baize_posttrain_api_profiler.py\""
check "SFT gen py" "python3 -m py_compile \"$BAIZE_RUN_DIR/baize_posttrain_gen_sft_corpus.py\""
check "EDA tool py" "python3 -m py_compile \"$BAIZE_RUN_DIR/baize_posttrain_eda_tool.py\""
check "paths.sh" "BAIZE_PATHS_VERBOSE=1 source \"$BAIZE_RUN_DIR/baize_posttrain_paths.sh\""
check "RL grpo.sh" "bash -n \"$BAIZE_RUN_DIR/baize_posttrain_rl_grpo.sh\""
check "SFT.sh" "bash -n \"$BAIZE_RUN_DIR/baize_posttrain_sft.sh\""
check "eval.sh" "bash -n \"$BAIZE_RUN_DIR/baize_posttrain_eval.sh\""
check "diag.sh" "bash -n \"$BAIZE_RUN_DIR/baize_posttrain_minicpm5_diag.sh\""

# YAML
if [ -d "$VENV_PATH" ]; then
    check "RL YAML" "$VENV_PATH/bin/python -c 'import yaml; yaml.safe_load(open(\"$BAIZE_RUN_DIR/baize_posttrain_rl_verl_config.yaml\")); exit(0)'"
else
    warn_check "RL YAML (sys py)" "python3 -c 'import yaml; yaml.safe_load(open(\"$BAIZE_RUN_DIR/baize_posttrain_rl_verl_config.yaml\")); exit(0)'"
fi

# 5. GPU
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
echo -n "[GPU idle] ... "
if [ -z "$GPU_BUSY" ]; then echo "PASS"; PASS=$((PASS+1)); else echo "WARN (GPU $GPU_BUSY busy)"; WARN=$((WARN+1)); fi

# 6. SSH tunnel
warn_check "SSH .15" "ssh -o ConnectTimeout=5 -o BatchMode=yes 10.251.36.15 echo ok"

# 7. cline
echo -n "[cline] ... "
if command -v cline >/dev/null 2>&1; then echo "PASS"; PASS=$((PASS+1));
elif [ -x "$HOME/.bun/bin/cline" ]; then echo "PASS (~/.bun/bin)"; PASS=$((PASS+1));
else echo "WARN"; WARN=$((WARN+1)); fi

echo ""
echo "=== Results: PASS=$PASS FAIL=$FAIL WARN=$WARN ==="
[ $FAIL -eq 0 ] && { echo "All critical checks passed!"; exit 0; } || { echo "$FAIL failed"; exit 1; }
