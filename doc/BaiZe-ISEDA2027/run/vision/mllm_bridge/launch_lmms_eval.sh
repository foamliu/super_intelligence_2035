#!/bin/bash
# Launch lmms-eval 17 benchmarks on BaiZe-LLaVA (8×H100 multi-GPU)
# Usage: bash launch_lmms_eval.sh [--step 3500] [--limit 100] [--batch_size 4]
#
# Proxy: direct to hf.co (NOT mirror)
# Multi-GPU: accelerate launch --multi_gpu --num_processes=8
set -e

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

# ---- proxy: direct to hf.co (NOT mirror) ----
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_TOKEN=hf_dummy  # needed by huggingface_hub 0.36+ for token=True in task configs
# Remove any hf-mirror settings
unset HF_ENDPOINT

# ---- HF cache on large disk (NOT /home which is only 196G) ----
# CRITICAL: /home has only 47G free; 8 ranks writing datasets cache simultaneously
# caused "No space left on device" crash on 2026-10-15 21:24.
# /nas_env has 9.9T free — all ranks share this cache.
export HF_HOME=/nas_env/app.e0031982/hf_home
export HF_DATASETS_CACHE=$HF_HOME/datasets
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
mkdir -p "$HF_DATASETS_CACHE" "$HF_HUB_CACHE" "$TRANSFORMERS_CACHE"

# ---- lmms-eval datasets cache on LOCAL disk (/data, 6.8T free) ----
# CRITICAL: lmms-eval detects NFS (HF_DATASETS_CACHE on /nas_env) and auto-redirects
# to /tmp/lmms_eval_hf_datasets_{user}/ — which only has ~38G free.
# 8 ranks building large datasets (VQAv2, etc.) simultaneously WILL fill /tmp.
# LMMS_EVAL_DATASETS_CACHE overrides this redirect, forcing cache to /data (local, 6.8T).
export LMMS_EVAL_DATASETS_CACHE=/data/app.e0031982/lmms_eval_cache
mkdir -p "$LMMS_EVAL_DATASETS_CACHE"

# ---- disk space check (require >=50G available) ----
AVAIL_KB=$(df -P /data | tail -1 | awk '{print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
echo "[launch] LMMS_EVAL_DATASETS_CACHE=$LMMS_EVAL_DATASETS_CACHE  /data available=${AVAIL_GB}G"
if [ "$AVAIL_GB" -lt 50 ]; then
    echo "[launch] WARNING: /data has only ${AVAIL_GB}G free (<50G threshold). Aborting."
    exit 1
fi

export OMP_NUM_THREADS=1

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

OUTPUT_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results
mkdir -p "$OUTPUT_DIR"

# Pass through any extra args
EXTRA_ARGS="$@"

echo "============================================================"
echo "  BaiZe-LLaVA lmms-eval 17 Benchmarks (8×H100 multi-GPU)"
echo "  Proxy: $https_proxy (direct to hf.co)"
echo "  Extra args: $EXTRA_ARGS"
echo "  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

exec accelerate launch \
    --multi_gpu \
    --num_processes=8 \
    --main_process_port=29556 \
    mllm_bridge/run_lmms_eval.py \
    $EXTRA_ARGS \
    > "$OUTPUT_DIR/eval.log" 2>&1
