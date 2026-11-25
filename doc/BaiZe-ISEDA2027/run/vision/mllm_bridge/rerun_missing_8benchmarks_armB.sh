#!/bin/bash
# Re-run the 8 MISSING benchmarks from the ArmB 12-benchmark eval (wake #152).
#
# ROOT CAUSE (diagnosed 2026-10-18 16:3x):
#   launch_12benchmarks_armB.sh set LMMS_EVAL_DATASETS_CACHE=/nas_env/.../lmms_eval_cache
#   which is MISSING 5 datasets (MMStar, MME, blink, CountBenchQA, MMMU_Pro).
#   With HF_HUB_OFFLINE=1 these cannot be downloaded -> ConnectionError -> the
#   whole per-GPU task group crashes (lmms-eval loads ALL tasks upfront).
#   The ④-4ep run succeeded because it used LMMS_EVAL_DATASETS_CACHE=/tmp/...
#   (see wait_precache_then_eval.sh) where precache_benchmarks.py downloaded all 12.
#
# FIX: point LMMS_EVAL_DATASETS_CACHE to /tmp/lmms_eval_hf_datasets_app.e0031982
#   (verified: MMStar 43M, MME 1.7G, blink 768M, CountBench 23M, MMMU_Pro 652M — all present).
#
# Only re-runs the 4 FAILED GPU tasks (8 benchmarks). The 4 that succeeded
# (mmmu_val, docvqa, infovqa, realworldqa) already have JSONs and are NOT touched.
#
# Usage: setsid bash -c 'exec bash mllm_bridge/rerun_missing_8benchmarks_armB.sh' \
#        > /tmp/rerun_8b_armB.log 2>&1 < /dev/null &

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

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
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
# === THE FIX: use /tmp cache where ALL 12 datasets are precached ===
export LMMS_EVAL_DATASETS_CACHE=/tmp/lmms_eval_hf_datasets_app.e0031982
mkdir -p "$LMMS_EVAL_DATASETS_CACHE"

LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armB
mkdir -p "$LOG_DIR"

echo "============================================================"
echo "  rerun_missing_8benchmarks_armB started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  ArmB: open_clip ViT-B/16 768-d, Stage-2 step3500, batch_size=32"
echo "  Cache: $LMMS_EVAL_DATASETS_CACHE (ALL 12 datasets precached)"
echo "  Output dir: $LOG_DIR"
echo "  Re-running 8 MISSING benchmarks (4 failed GPU tasks)"
echo "============================================================"

# Verify the 5 previously-missing datasets are in the /tmp cache
for d in Lin-Chen___mm_star lmms-lab___mme BLINK-Benchmark___blink vikhyatk___count_bench_qa MMMU___mmmu_pro; do
    if [ -d "$LMMS_EVAL_DATASETS_CACHE/$d" ]; then
        echo "  [cache OK] $d"
    else
        echo "  [cache MISSING!] $d — ABORTING"
        exit 1
    fi
done

AVAIL_KB=$(df -P /tmp | tail -1 | awk '{print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
echo "  /tmp available: ${AVAIL_GB}G"
if [ "$AVAIL_GB" -lt 5 ]; then
    echo "  WARNING: /tmp has only ${AVAIL_GB}G free. Aborting."
    exit 1
fi

PIDS=()

# GPU 0: ai2d + mmstar  -> eval_ai2d_mmstar.json
CUDA_VISIBLE_DEVICES=0 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armB --tasks ai2d,mmstar --batch_size 32 \
    --output "$LOG_DIR/eval_ai2d_mmstar.json" \
    > "$LOG_DIR/eval_ai2d_mmstar.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 0 (PID $!): ai2d+mmstar"

# GPU 1: mme + blink  -> eval_mme_blink.json
CUDA_VISIBLE_DEVICES=1 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armB --tasks mme,blink --batch_size 32 \
    --output "$LOG_DIR/eval_mme_blink.json" \
    > "$LOG_DIR/eval_mme_blink.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 1 (PID $!): mme+blink"

# GPU 2: chartqa + ocrbench + countbench  -> eval_chart_ocr_count.json
CUDA_VISIBLE_DEVICES=2 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armB --tasks chartqa,ocrbench,countbench --batch_size 32 \
    --output "$LOG_DIR/eval_chart_ocr_count.json" \
    > "$LOG_DIR/eval_chart_ocr_count.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 2 (PID $!): chartqa+ocrbench+countbench"

# GPU 3: mmmu_pro_standard  -> eval_mmmu_pro.json
CUDA_VISIBLE_DEVICES=3 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armB --tasks mmmu_pro_standard --batch_size 32 \
    --output "$LOG_DIR/eval_mmmu_pro.json" \
    > "$LOG_DIR/eval_mmmu_pro.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 3 (PID $!): mmmu_pro_standard"

echo "[$(date '+%H:%M:%S')] All 4 GPU processes launched (PIDs: ${PIDS[*]})"
echo "[$(date '+%H:%M:%S')] Waiting for all to complete..."

ALL_OK=1
for i in "${!PIDS[@]}"; do
    wait "${PIDS[$i]}"
    RC=$?
    echo "[$(date '+%H:%M:%S')] GPU $i exit=$RC"
    [ $RC -ne 0 ] && ALL_OK=0
done

if [ $ALL_OK -eq 1 ]; then
    echo "✅ All 8 missing benchmarks (ArmB) completed successfully!"
else
    echo "⚠️  Some tasks failed. Check logs in $LOG_DIR/eval_*.log"
fi

# Consolidate ALL 12 (4 already-succeeded + 8 re-run) into final summary
echo "[$(date '+%H:%M:%S')] Consolidating all 12 benchmarks..."
python mllm_bridge/consolidate_12benchmarks.py --results_dir "$LOG_DIR"

echo "============================================================"
echo "  rerun_missing_8benchmarks_armB finished: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
