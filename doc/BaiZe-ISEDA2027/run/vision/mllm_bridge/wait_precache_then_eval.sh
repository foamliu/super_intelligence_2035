#!/bin/bash
# Automation: wait for precache → retry seedbench → launch limit50 8-GPU eval
# Usage: nohup bash mllm_bridge/wait_precache_then_eval.sh &
#
# This script:
#   1. Waits for precache_benchmarks.py (PID from /tmp/baize_precache.pid) to finish
#   2. Retries seedbench with xet disabled (HF_HUB_ENABLE_HF_TRANSFER=0)
#   3. Launches limit50 8-GPU eval as smoke test
# NOTE: no set -e — we want to continue even if seedbench retry fails

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

# ---- shared env ----
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_TOKEN=hf_dummy
unset HF_ENDPOINT
export HF_HOME=/nas_env/app.e0031982/hf_home
export HF_DATASETS_CACHE=$HF_HOME/datasets
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
export LMMS_EVAL_DATASETS_CACHE=/data/app.e0031982/lmms_eval_cache
export OMP_NUM_THREADS=1
mkdir -p "$HF_DATASETS_CACHE" "$HF_HUB_CACHE" "$TRANSFORMERS_CACHE" "$LMMS_EVAL_DATASETS_CACHE"

LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results
mkdir -p "$LOG_DIR"
WATCHER_LOG="$LOG_DIR/watcher.log"

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

echo "============================================================" | tee "$WATCHER_LOG"
echo "  Watcher started: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$WATCHER_LOG"
echo "============================================================" | tee -a "$WATCHER_LOG"

# ---- Step 1: Wait for precache to finish ----
PRECACHE_PID=2430411
echo "[watcher] Waiting for precache PID $PRECACHE_PID to finish..." | tee -a "$WATCHER_LOG"
WAIT_START=$(date +%s)
while kill -0 "$PRECACHE_PID" 2>/dev/null; do
    sleep 30
done
WAIT_END=$(date +%s)
echo "[watcher] Precache finished after $((WAIT_END - WAIT_START))s" | tee -a "$WATCHER_LOG"

# Print precache summary
echo "[watcher] Precache log tail:" | tee -a "$WATCHER_LOG"
tail -20 "$LOG_DIR/precache.log" | tee -a "$WATCHER_LOG"

# ---- Step 2: Retry seedbench with xet disabled ----
echo "" | tee -a "$WATCHER_LOG"
echo "[watcher] Retrying seedbench (xet disabled)..." | tee -a "$WATCHER_LOG"
export HF_HUB_ENABLE_HF_TRANSFER=0
python mllm_bridge/precache_benchmarks.py --limit 1 --tasks seedbench 2>&1 | tee -a "$LOG_DIR/precache_retry.log"
SEEDBENCH_RC=${PIPESTATUS[0]}
echo "[watcher] Seedbench retry exit code: $SEEDBENCH_RC" | tee -a "$WATCHER_LOG"

# Determine task list: all 17 if seedbench OK, else 16 (skip seedbench)
if [ "$SEEDBENCH_RC" -ne 0 ]; then
    echo "[watcher] ⚠️ seedbench retry failed — will run eval on 16 benchmarks (skip seedbench)" | tee -a "$WATCHER_LOG"
    EVAL_TASKS="mmbench_en_dev,mmmu_val,gqa,textvqa_val,docvqa_val,chartqa,ai2d,scienceqa,pope,vizwiz_vqa_val,ocrbench,mmvet,hallusion_bench_image,realworldqa,vqav2_val,infovqa_val"
else
    echo "[watcher] ✅ seedbench retry succeeded — will run eval on all 17 benchmarks" | tee -a "$WATCHER_LOG"
    EVAL_TASKS=""
fi

# ---- Step 3: Launch limit50 8-GPU eval ----
echo "" | tee -a "$WATCHER_LOG"
echo "[watcher] Launching limit50 8-GPU eval at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$WATCHER_LOG"

# Re-enable hf_transfer for eval (downloads already cached)
export HF_HUB_ENABLE_HF_TRANSFER=1

# Disk space check
AVAIL_KB=$(df -P /data | tail -1 | awk '{print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
echo "[watcher] /data available: ${AVAIL_GB}G" | tee -a "$WATCHER_LOG"
if [ "$AVAIL_GB" -lt 50 ]; then
    echo "[watcher] WARNING: /data has only ${AVAIL_GB}G free. Aborting eval." | tee -a "$WATCHER_LOG"
    exit 1
fi

EVAL_LOG="$LOG_DIR/eval_limit50.log"
echo "[watcher] Eval log: $EVAL_LOG" | tee -a "$WATCHER_LOG"

TASKS_ARG=""
if [ -n "$EVAL_TASKS" ]; then
    TASKS_ARG="--tasks $EVAL_TASKS"
fi

accelerate launch \
    --multi_gpu \
    --num_processes=8 \
    --main_process_port=29556 \
    mllm_bridge/run_lmms_eval.py \
    --limit 50 \
    --batch_size 4 \
    $TASKS_ARG \
    > "$EVAL_LOG" 2>&1
EVAL_RC=$?

echo "[watcher] Eval exit code: $EVAL_RC at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$WATCHER_LOG"

# Print eval summary
if [ $EVAL_RC -eq 0 ]; then
    echo "[watcher] ✅ limit50 eval completed successfully!" | tee -a "$WATCHER_LOG"
    tail -40 "$EVAL_LOG" | tee -a "$WATCHER_LOG"
else
    echo "[watcher] ❌ limit50 eval FAILED (exit $EVAL_RC)" | tee -a "$WATCHER_LOG"
    tail -80 "$EVAL_LOG" | tee -a "$WATCHER_LOG"
fi

echo "============================================================" | tee -a "$WATCHER_LOG"
echo "  Watcher finished: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$WATCHER_LOG"
echo "============================================================" | tee -a "$WATCHER_LOG"
