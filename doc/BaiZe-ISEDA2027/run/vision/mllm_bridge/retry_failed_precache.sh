#!/bin/bash
# Retry failed precache tasks with xet disabled (HF_HUB_ENABLE_HF_TRANSFER=0)
# Usage: nohup bash mllm_bridge/retry_failed_precache.sh [task1,task2,...] &
# If no tasks specified, retries: seedbench
set -e

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

# ---- proxy: direct to hf.co (NOT mirror) ----
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
# DISABLE xet/hf_transfer — seedbench failed with ConnectionError to cas-server-direct.xethub.hf.co
export HF_HUB_ENABLE_HF_TRANSFER=0
export HF_TOKEN=hf_dummy
unset HF_ENDPOINT

# ---- HF cache on large disk ----
export HF_HOME=/nas_env/app.e0031982/hf_home
export HF_DATASETS_CACHE=$HF_HOME/datasets
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
# lmms-eval cache on LOCAL disk (/data, 6.8T) — avoids NFS→/tmp redirect
export LMMS_EVAL_DATASETS_CACHE=/data/app.e0031982/lmms_eval_cache
mkdir -p "$HF_DATASETS_CACHE" "$HF_HUB_CACHE" "$TRANSFORMERS_CACHE" "$LMMS_EVAL_DATASETS_CACHE"

TASKS="${1:-seedbench}"

LOG=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results/precache_retry.log

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

echo "============================================================" | tee "$LOG"
echo "  Retry pre-cache started: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG"
echo "  HF_HOME=$HF_HOME" | tee -a "$LOG"
echo "  HF_HUB_ENABLE_HF_TRANSFER=$HF_HUB_ENABLE_HF_TRANSFER (xet DISABLED)" | tee -a "$LOG"
echo "  Tasks: $TASKS" | tee -a "$LOG"
echo "============================================================" | tee -a "$LOG"

exec python mllm_bridge/precache_benchmarks.py --limit 1 --tasks "$TASKS" 2>&1 | tee -a "$LOG"