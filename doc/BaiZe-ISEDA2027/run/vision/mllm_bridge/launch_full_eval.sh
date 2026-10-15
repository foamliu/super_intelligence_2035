#!/bin/bash
# Full 17-benchmark eval (no --limit) on 8 GPUs.
# Usage: bash mllm_bridge/launch_full_eval.sh [--skip-vqav2] [--cache /nas_env]
#
# This script is launched AFTER the limit50 smoke test (watcher) succeeds.
# It reuses existing lmms-eval caches from /tmp by default.
# Use --cache /nas_env to move cache to /nas_env (for vqav2 which needs >28G).
#
# Usage examples:
#   bash mllm_bridge/launch_full_eval.sh                    # 17 benchmarks, /tmp cache
#   bash mllm_bridge/launch_full_eval.sh --skip-vqav2       # 16 benchmarks, /tmp cache
#   bash mllm_bridge/launch_full_eval.sh --cache /nas_env   # 17 benchmarks, /nas_env cache

set -e

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

# ---- shared env (same as watcher) ----
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_TOKEN=hf_dummy
unset HF_ENDPOINT
export HF_HOME=/nas_env/app.e0031982/hf_home
export HF_DATASETS_CACHE=$HF_HOME/datasets
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
export HF_HUB_ENABLE_HF_TRANSFER=1
export OMP_NUM_THREADS=1

# ---- parse args ----
SKIP_VQAV2=false
CACHE_DIR=/tmp  # default: reuse existing /tmp caches

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-vqav2)  SKIP_VQAV2=true; shift ;;
        --cache)
            CACHE_DIR="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

if [ "$CACHE_DIR" = "/nas_env" ]; then
    export LMMS_EVAL_DATASETS_CACHE=/nas_env/app.e0031982/lmms_eval_cache
    mkdir -p "$LMMS_EVAL_DATASETS_CACHE"
    # Copy existing /tmp caches if /nas_env cache is empty
    if [ -z "$(ls -A "$LMMS_EVAL_DATASETS_CACHE" 2>/dev/null)" ]; then
        echo "[full_eval] Copying /tmp caches to /nas_env (this may take a few minutes)..."
        cp -a /tmp/lmms_eval_hf_datasets_app.e0031982/* "$LMMS_EVAL_DATASETS_CACHE/" 2>/dev/null || true
        echo "[full_eval] Copy done."
    fi
else
    export LMMS_EVAL_DATASETS_CACHE=/tmp/lmms_eval_hf_datasets_app.e0031982
fi

echo "[full_eval] LMMS_EVAL_DATASETS_CACHE=$LMMS_EVAL_DATASETS_CACHE"

# ---- build task list ----
ALL_TASKS="mmbench_en_dev,mmmu_val,gqa,textvqa_val,docvqa_val,chartqa,ai2d,scienceqa,seedbench,pope,vizwiz_vqa_val,ocrbench,mmvet,hallusion_bench_image,realworldqa,infovqa_val"
if [ "$SKIP_VQAV2" = false ]; then
    ALL_TASKS="${ALL_TASKS},vqav2_val"
fi

NUM_TASKS=$(echo "$ALL_TASKS" | tr ',' '\n' | wc -l)
echo "[full_eval] Tasks: $NUM_TASKS benchmarks"
echo "[full_eval] Task list: $ALL_TASKS"

# ---- disk check ----
AVAIL_KB=$(df -P "$LMMS_EVAL_DATASETS_CACHE" | tail -1 | awk '{print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
echo "[full_eval] Cache dir available: ${AVAIL_GB}G"
if [ "$AVAIL_GB" -lt 10 ]; then
    echo "[full_eval] WARNING: Only ${AVAIL_GB}G free (<10G). Aborting."
    exit 1
fi

# ---- launch full eval ----
LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results
mkdir -p "$LOG_DIR"
EVAL_LOG="$LOG_DIR/eval_full_$(date +%Y%m%d_%H%M%S).log"
echo "[full_eval] Eval log: $EVAL_LOG"
echo "[full_eval] Start: $(date '+%Y-%m-%d %H:%M:%S')"

accelerate launch \
    --multi_gpu \
    --num_processes=8 \
    --main_process_port=29557 \
    mllm_bridge/run_lmms_eval.py \
    --batch_size 4 \
    --tasks "$ALL_TASKS" \
    > "$EVAL_LOG" 2>&1

EVAL_RC=$?
echo "[full_eval] Eval exit code: $EVAL_RC at $(date '+%Y-%m-%d %H:%M:%S')"

if [ $EVAL_RC -eq 0 ]; then
    echo "[full_eval] ✅ Full eval completed successfully!"
    tail -60 "$EVAL_LOG"
else
    echo "[full_eval] ❌ Full eval FAILED (exit $EVAL_RC)"
    tail -80 "$EVAL_LOG"
fi
