#!/bin/bash
# Replacement watcher: wait for seedbench retry → launch limit50 eval WITHOUT vqav2
# vqav2 arrow cache cannot build on /tmp (28G free, needs ~29G+).
# For limit50 smoke test, we exclude vqav2 and reuse existing 15 caches on /tmp.
# For full eval later, use launch_full_eval.sh --cache /nas_env to build vqav2 on large disk.
#
# Usage: nohup bash mllm_bridge/eval_no_vqav2.sh &

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

# ---- shared env (same as watcher) ----
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_TOKEN=hf_dummy
unset HF_ENDPOINT
export HF_HOME=/nas_env/app.e0031982/hf_home
export HF_DATASETS_CACHE=$HF_HOME/datasets
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
export LMMS_EVAL_DATASETS_CACHE=/tmp/lmms_eval_hf_datasets_app.e0031982
export OMP_NUM_THREADS=1

LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results
WATCHER_LOG="$LOG_DIR/watcher.log"
SEEDBENCH_PID=1790024

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

echo "============================================================" | tee -a "$WATCHER_LOG"
echo "  eval_no_vqav2 started: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$WATCHER_LOG"
echo "  (vqav2 EXCLUDED — /tmp too small for arrow cache)" | tee -a "$WATCHER_LOG"
echo "============================================================" | tee -a "$WATCHER_LOG"

# ---- Step 1: Wait for seedbench retry to finish ----
echo "[eval_no_vqav2] Waiting for seedbench retry PID $SEEDBENCH_PID to finish..." | tee -a "$WATCHER_LOG"
WAIT_START=$(date +%s)
while kill -0 "$SEEDBENCH_PID" 2>/dev/null; do
    sleep 10
done
WAIT_END=$(date +%s)
echo "[eval_no_vqav2] Seedbench retry finished after $((WAIT_END - WAIT_START))s" | tee -a "$WATCHER_LOG"

# Check if seedbench cache was built successfully
SEEDBENCH_CACHE="/tmp/lmms_eval_hf_datasets_app.e0031982/lmms-lab___seedbench"
if [ -d "$SEEDBENCH_CACHE" ] && [ "$(find "$SEEDBENCH_CACHE" -name '*.arrow' 2>/dev/null | head -1)" ]; then
    echo "[eval_no_vqav2] ✅ seedbench cache found — will run 16 benchmarks (skip vqav2 only)" | tee -a "$WATCHER_LOG"
    EVAL_TASKS="mmbench_en_dev,mmmu_val,gqa,textvqa_val,docvqa_val,chartqa,ai2d,scienceqa,seedbench,pope,vizwiz_vqa_val,ocrbench,mmvet,hallusion_bench_image,realworldqa,infovqa_val"
else
    echo "[eval_no_vqav2] ⚠️ seedbench cache not found — will run 15 benchmarks (skip seedbench + vqav2)" | tee -a "$WATCHER_LOG"
    EVAL_TASKS="mmbench_en_dev,mmmu_val,gqa,textvqa_val,docvqa_val,chartqa,ai2d,scienceqa,pope,vizwiz_vqa_val,ocrbench,mmvet,hallusion_bench_image,realworldqa,infovqa_val"
fi

# ---- Step 2: Launch limit50 8-GPU eval (without vqav2) ----
echo "" | tee -a "$WATCHER_LOG"
echo "[eval_no_vqav2] Launching limit50 8-GPU eval at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$WATCHER_LOG"
echo "[eval_no_vqav2] Tasks: $EVAL_TASKS" | tee -a "$WATCHER_LOG"

export HF_HUB_ENABLE_HF_TRANSFER=1

# Disk space check
AVAIL_KB=$(df -P /tmp | tail -1 | awk '{print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
echo "[eval_no_vqav2] /tmp available: ${AVAIL_GB}G" | tee -a "$WATCHER_LOG"
if [ "$AVAIL_GB" -lt 5 ]; then
    echo "[eval_no_vqav2] WARNING: /tmp has only ${AVAIL_GB}G free (<5G threshold). Aborting eval." | tee -a "$WATCHER_LOG"
    exit 1
fi

EVAL_LOG="$LOG_DIR/eval_limit50.log"
echo "[eval_no_vqav2] Eval log: $EVAL_LOG" | tee -a "$WATCHER_LOG"

accelerate launch \
    --multi_gpu \
    --num_processes=8 \
    --main_process_port=29556 \
    mllm_bridge/run_lmms_eval.py \
    --limit 50 \
    --batch_size 4 \
    --tasks $EVAL_TASKS \
    > "$EVAL_LOG" 2>&1
EVAL_RC=$?

echo "[eval_no_vqav2] Eval exit code: $EVAL_RC at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$WATCHER_LOG"

if [ $EVAL_RC -eq 0 ]; then
    echo "[eval_no_vqav2] ✅ limit50 eval completed successfully!" | tee -a "$WATCHER_LOG"
    tail -60 "$EVAL_LOG" | tee -a "$WATCHER_LOG"
else
    echo "[eval_no_vqav2] ❌ limit50 eval FAILED (exit $EVAL_RC)" | tee -a "$WATCHER_LOG"
    tail -80 "$EVAL_LOG" | tee -a "$WATCHER_LOG"
fi

echo "============================================================" | tee -a "$WATCHER_LOG"
echo "  eval_no_vqav2 finished: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$WATCHER_LOG"
echo "============================================================" | tee -a "$WATCHER_LOG"
