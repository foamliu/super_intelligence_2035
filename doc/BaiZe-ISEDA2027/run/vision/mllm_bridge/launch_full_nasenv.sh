#!/bin/bash
# Launch FULL eval (no --limit) on 8 GPUs with LMMS_EVAL_DATASETS_CACHE on /nas_env.
# Based on launch_limit50_nasenv.sh — same 14 benchmarks, no sample limit.
# Expected runtime: ~60-120 min (GQA alone has ~12k samples).
#
# Usage: setsid bash -c 'exec bash mllm_bridge/launch_full_nasenv.sh' > /tmp/launch_full.log 2>&1 < /dev/null &

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
export HF_HUB_ENABLE_HF_TRANSFER=1
export OMP_NUM_THREADS=1
# Fix CUDA memory fragmentation (recommended by PyTorch OOM error message)
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# ---- cache on /nas_env (9.7T free, NOT /tmp which is full) ----
NEW_CACHE=/nas_env/app.e0031982/lmms_eval_cache
OLD_CACHE=/tmp/lmms_eval_hf_datasets_app.e0031982
export LMMS_EVAL_DATASETS_CACHE=$NEW_CACHE
mkdir -p "$NEW_CACHE"

LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results
mkdir -p "$LOG_DIR"
SCRIPT_LOG="$LOG_DIR/launch_full_nasenv.log"

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

# ---- guard: prevent duplicate runs ----
LOCK_FILE=/tmp/launch_full_nasenv.lock
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
    echo "[guard] Another instance is already running (lock $LOCK_FILE held). Exiting." | tee -a "$SCRIPT_LOG"
    exit 0
fi
echo "[guard] Lock acquired at $(date '+%H:%M:%S')" | tee -a "$SCRIPT_LOG"

echo "============================================================" | tee "$SCRIPT_LOG"
echo "  launch_full_nasenv started: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$SCRIPT_LOG"
echo "  NEW_CACHE=$NEW_CACHE  OLD_CACHE=$OLD_CACHE" | tee -a "$SCRIPT_LOG"
echo "============================================================" | tee -a "$SCRIPT_LOG"

# ---- Step 1: Verify cache (should already be in /nas_env from limit50 run) ----
CACHE_COUNT=$(ls -d "$NEW_CACHE"/*/ 2>/dev/null | wc -l)
echo "[step1] Cache dirs in NEW_CACHE: $CACHE_COUNT" | tee -a "$SCRIPT_LOG"
if [ "$CACHE_COUNT" -lt 10 ]; then
    echo "[step1] WARNING: Only $CACHE_COUNT cache dirs. Expected 15+. Aborting." | tee -a "$SCRIPT_LOG"
    exit 1
fi

# ---- Step 2: Disk check on /nas_env ----
AVAIL_KB=$(df -P "$NEW_CACHE" | tail -1 | awk '{print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
echo "[step2] /nas_env available: ${AVAIL_GB}G" | tee -a "$SCRIPT_LOG"
if [ "$AVAIL_GB" -lt 10 ]; then
    echo "[step2] WARNING: Only ${AVAIL_GB}G free (<10G). Aborting." | tee -a "$SCRIPT_LOG"
    exit 1
fi

# ---- Step 3: Launch FULL 8-GPU eval (no --limit) ----
# 14 benchmarks (skip vqav2 — needs >28G arrow; skip mmvet + hallusion_bench — need GPT-4 API)
# 13 benchmarks (skip vqav2 — needs >28G arrow; skip seedbench — precache FAIL per user;
#                   skip mmvet + hallusion_bench — need GPT-4 API)
EVAL_TASKS="mmbench_en_dev,mmmu_val,gqa,textvqa_val,docvqa_val,chartqa,ai2d,scienceqa,pope,vizwiz_vqa_val,ocrbench,realworldqa,infovqa_val"

# Critical: prevent parallel HF Hub API calls (caused 429 crash on 2026-10-16 08:54)
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1

echo "" | tee -a "$SCRIPT_LOG"
echo "[step3] Launching FULL 8-GPU eval at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$SCRIPT_LOG"
echo "[step3] Tasks: $EVAL_TASKS" | tee -a "$SCRIPT_LOG"
echo "[step3] No --limit (full datasets)" | tee -a "$SCRIPT_LOG"
echo "[step3] HF_HUB_OFFLINE=1 (prevent 429)" | tee -a "$SCRIPT_LOG"

EVAL_LOG="$LOG_DIR/eval_full_nasenv.log"
echo "[step3] Eval log: $EVAL_LOG" | tee -a "$SCRIPT_LOG"

accelerate launch \
    --multi_gpu \
    --num_processes=8 \
    --main_process_port=29561 \
    mllm_bridge/run_lmms_eval.py \
    --batch_size 32 \
    --tasks "$EVAL_TASKS" \
    > "$EVAL_LOG" 2>&1
EVAL_RC=$?

echo "[step3] Eval exit code: $EVAL_RC at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$SCRIPT_LOG"

if [ $EVAL_RC -eq 0 ]; then
    echo "[step3] ✅ FULL eval completed successfully!" | tee -a "$SCRIPT_LOG"
    tail -80 "$EVAL_LOG" | tee -a "$SCRIPT_LOG"
else
    echo "[step3] ❌ FULL eval FAILED (exit $EVAL_RC)" | tee -a "$SCRIPT_LOG"
    tail -120 "$EVAL_LOG" | tee -a "$SCRIPT_LOG"
fi

echo "============================================================" | tee -a "$SCRIPT_LOG"
echo "  launch_full_nasenv finished: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$SCRIPT_LOG"
echo "============================================================" | tee -a "$SCRIPT_LOG"