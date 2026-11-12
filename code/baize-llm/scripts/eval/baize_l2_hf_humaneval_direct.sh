#!/usr/bin/env bash
# L2 HumanEval HF Direct Eval — sglang env (transformers 5.18.0, no lm_eval/sklearn)
# CPU only, nice 19, OMP_NUM_THREADS=4 — must not affect training
set -uo pipefail
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=4
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"

# 优先用本目录内的脚本副本（随 baize-llm 仓库走）；找不到再回退到 doc run/ 的原路径
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/baize_l2_hf_humaneval_direct.py"
[ -f "$SCRIPT" ] || SCRIPT="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_l2_hf_humaneval_direct.py"
PY="/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python"
LOG="/tmp/baize_l2_hf_humaneval_direct.log"

MODEL="${1:-/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000}"
LIMIT="${2:-50}"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting HF HumanEval direct eval (limit=$LIMIT, model=$MODEL)" | tee "$LOG"
echo "  CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES  OMP_NUM_THREADS=$OMP_NUM_THREADS" | tee -a "$LOG"

nice -n 19 "$PY" "$SCRIPT" --model_path "$MODEL" --limit "$LIMIT" 2>&1 | tee -a "$LOG"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done." | tee -a "$LOG"
