#!/bin/bash
# Launch limit50 eval on 8 GPUs with LMMS_EVAL_DATASETS_CACHE on /nas_env (not /tmp).
# Step 1: Copy existing /tmp cache → /nas_env (preserves 7h of precache work)
# Step 2: Delete /tmp cache to free 67G on /tmp
# Step 3: Run limit50 8-GPU eval (16 benchmarks: skip vqav2 which needs >28G arrow)
#
# Usage: nohup bash mllm_bridge/launch_limit50_nasenv.sh &

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

# ---- cache on /nas_env (9.7T free, NOT /tmp which is full) ----
NEW_CACHE=/nas_env/app.e0031982/lmms_eval_cache
OLD_CACHE=/tmp/lmms_eval_hf_datasets_app.e0031982
export LMMS_EVAL_DATASETS_CACHE=$NEW_CACHE
mkdir -p "$NEW_CACHE"

LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results
mkdir -p "$LOG_DIR"
SCRIPT_LOG="$LOG_DIR/launch_limit50_nasenv.log"

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

# ---- guard: prevent duplicate runs ----
LOCK_FILE=/tmp/launch_limit50_nasenv.lock
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
    echo "[guard] Another instance is already running (lock $LOCK_FILE held). Exiting." | tee -a "$SCRIPT_LOG"
    exit 0
fi
echo "[guard] Lock acquired at $(date '+%H:%M:%S')" | tee -a "$SCRIPT_LOG"

echo "============================================================" | tee "$SCRIPT_LOG"
echo "  launch_limit50_nasenv started: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$SCRIPT_LOG"
echo "  NEW_CACHE=$NEW_CACHE  OLD_CACHE=$OLD_CACHE" | tee -a "$SCRIPT_LOG"
echo "============================================================" | tee -a "$SCRIPT_LOG"

# ---- Step 1: Copy /tmp cache → /nas_env (if not already done) ----
CACHE_COUNT=$(ls -d "$NEW_CACHE"/*/ 2>/dev/null | wc -l)
if [ "$CACHE_COUNT" -lt 10 ]; then
    echo "[step1] Copying $OLD_CACHE → $NEW_CACHE (67G, ~10min)..." | tee -a "$SCRIPT_LOG"
    CP_START=$(date +%s)
    cp -a "$OLD_CACHE"/* "$NEW_CACHE"/ 2>&1 | tee -a "$SCRIPT_LOG"
    CP_END=$(date +%s)
    echo "[step1] Copy done in $((CP_END - CP_START))s" | tee -a "$SCRIPT_LOG"
    NEW_COUNT=$(ls -d "$NEW_CACHE"/*/ 2>/dev/null | wc -l)
    echo "[step1] Cache dirs in NEW_CACHE: $NEW_COUNT" | tee -a "$SCRIPT_LOG"
else
    echo "[step1] Cache already copied ($CACHE_COUNT dirs). Skipping copy." | tee -a "$SCRIPT_LOG"
fi

# ---- Step 2: Free /tmp by deleting old cache ----
echo "[step2] Freeing /tmp: rm -rf $OLD_CACHE ..." | tee -a "$SCRIPT_LOG"
rm -rf "$OLD_CACHE"
TMP_AVAIL=$(df -P /tmp | tail -1 | awk '{print $4}')
echo "[step2] /tmp now has $((TMP_AVAIL / 1024 / 1024))G free" | tee -a "$SCRIPT_LOG"

# ---- Step 3: Disk check on /nas_env ----
AVAIL_KB=$(df -P "$NEW_CACHE" | tail -1 | awk '{print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
echo "[step3] /nas_env available: ${AVAIL_GB}G" | tee -a "$SCRIPT_LOG"
if [ "$AVAIL_GB" -lt 10 ]; then
    echo "[step3] WARNING: Only ${AVAIL_GB}G free (<10G). Aborting." | tee -a "$SCRIPT_LOG"
    exit 1
fi

# ---- Step 4: Launch limit50 8-GPU eval ----
# 14 benchmarks (skip vqav2_val — needs >28G arrow; skip mmvet + hallusion_bench_image — need GPT-4 API for scoring)
# seedbench IS included — lmms-eval task name is "seedbench", cache dir is "lmms-lab___seed-bench"
#
# FIX 2026-10-16 09:05: Removed mmvet + hallusion_bench_image — both call OpenAI GPT-4 API
# for post-processing/scoring, but no OPENAI_API_KEY is configured → crash during aggregation.
# Will add them back in full eval with API key or local judge.
#
# FIX 2026-10-16: HF_HUB_OFFLINE=1 prevents 429 Too Many Requests when 8 ranks
# try to load uncached datasets simultaneously. All 15 datasets are in the hub
# cache (/nas_env/app.e0031982/hf_home/hub/), so offline mode works.
# Pre-cached missing datasets (vizwiz, infovqa) via precache_missing.py first.
EVAL_TASKS="mmbench_en_dev,mmmu_val,gqa,textvqa_val,docvqa_val,chartqa,ai2d,scienceqa,seedbench,pope,vizwiz_vqa_val,ocrbench,realworldqa,infovqa_val"

# Critical: prevent parallel HF Hub API calls (caused 429 crash on 2026-10-16 08:54)
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1

echo "" | tee -a "$SCRIPT_LOG"
echo "[step4] Launching limit50 8-GPU eval at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$SCRIPT_LOG"
echo "[step4] Tasks: $EVAL_TASKS" | tee -a "$SCRIPT_LOG"
echo "[step4] HF_HUB_OFFLINE=1 (prevent 429 from parallel API calls)" | tee -a "$SCRIPT_LOG"

EVAL_LOG="$LOG_DIR/eval_limit50_nasenv.log"
echo "[step4] Eval log: $EVAL_LOG" | tee -a "$SCRIPT_LOG"

accelerate launch \
    --multi_gpu \
    --num_processes=8 \
    --main_process_port=29560 \
    mllm_bridge/run_lmms_eval.py \
    --limit 50 \
    --batch_size 4 \
    --tasks "$EVAL_TASKS" \
    > "$EVAL_LOG" 2>&1
EVAL_RC=$?

echo "[step4] Eval exit code: $EVAL_RC at $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$SCRIPT_LOG"

if [ $EVAL_RC -eq 0 ]; then
    echo "[step4] ✅ limit50 eval completed successfully!" | tee -a "$SCRIPT_LOG"
    tail -60 "$EVAL_LOG" | tee -a "$SCRIPT_LOG"
else
    echo "[step4] ❌ limit50 eval FAILED (exit $EVAL_RC)" | tee -a "$SCRIPT_LOG"
    tail -80 "$EVAL_LOG" | tee -a "$SCRIPT_LOG"
fi

echo "============================================================" | tee -a "$SCRIPT_LOG"
echo "  launch_limit50_nasenv finished: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$SCRIPT_LOG"
echo "============================================================" | tee -a "$SCRIPT_LOG"
