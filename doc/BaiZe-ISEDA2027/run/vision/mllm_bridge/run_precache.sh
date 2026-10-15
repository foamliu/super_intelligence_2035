#!/bin/bash
# Pre-cache all 17 lmms-eval benchmark datasets (SINGLE PROCESS)
# Usage: nohup bash mllm_bridge/run_precache.sh &
set -e

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

# ---- proxy: direct to hf.co (NOT mirror) ----
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_TOKEN=hf_dummy
unset HF_ENDPOINT

# ---- HF cache on large disk ----
export HF_HOME=/nas_env/app.e0031982/hf_home
export HF_DATASETS_CACHE=$HF_HOME/datasets
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
mkdir -p "$HF_DATASETS_CACHE" "$HF_HUB_CACHE" "$TRANSFORMERS_CACHE"

LOG=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results/precache.log

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

echo "============================================================" | tee "$LOG"
echo "  Pre-cache started: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
echo "  HF_HOME=$HF_HOME" | tee -a "$LOG"
echo "  Proxy=$https_proxy" | tee -a "$LOG"
echo "============================================================" | tee -a "$LOG"

exec python mllm_bridge/precache_benchmarks.py --limit 1 2>&1 | tee -a "$LOG"
