#!/bin/bash
# rerun_failed_benchmarks_armC_offline.sh - re-run 8 MISSING ArmC benchmarks
# using /tmp HF-datasets cache (NO proxy needed). wake #172, 2026-10-19 19:3x.
# ArmB 12/12 success on 10-18 used /tmp/lmms_eval_hf_datasets_app.e0031982.
# ArmC failed because it pointed caches to nas_env (missing 8 datasets).
# FIX: both HF_DATASETS_CACHE + LMMS_EVAL_DATASETS_CACHE -> /tmp cache, offline.
# Variables: ArmC = min_lr 1e-4->1e-5 + wd 0.1->0.01 (TWO vars, NOT single-var).
# Launch: setsid bash rerun_failed_benchmarks_armC_offline.sh > /tmp/armC_rerun_offline.log 2>&1 < /dev/null &
set -uo pipefail
VISION_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armC_20261018
TMP_CACHE=/tmp/lmms_eval_hf_datasets_app.e0031982
cd "$VISION_DIR"
source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310
export HF_TOKEN=hf_dummy
unset HF_ENDPOINT
export HF_HOME=/nas_env/app.e0031982/hf_home
export HF_DATASETS_CACHE="$TMP_CACHE"
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export LMMS_EVAL_DATASETS_CACHE="$TMP_CACHE"
export OMP_NUM_THREADS=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
unset https_proxy http_proxy HTTPS_PROXY HTTP_PROXY
mkdir -p "$LMMS_EVAL_DATASETS_CACHE" "$LOG_DIR"
echo "============================================================"
echo "  ArmC rerun OFFLINE started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  HF_DATASETS_CACHE=$HF_DATASETS_CACHE"
echo "  LMMS_EVAL_DATASETS_CACHE=$LMMS_EVAL_DATASETS_CACHE"
echo "  HF_HUB_OFFLINE=1 / HF_DATASETS_OFFLINE=1 / no proxy"
echo "  Variables: min_lr 1e-4->1e-5 + wd 0.1->0.01 (TWO vars)"
echo "============================================================"
echo "[$(date '+%H:%M:%S')] Verifying /tmp cache has all 8 missing datasets..."
MISSING_IN_CACHE=()
for d in MMMU___mmmu_pro lmms-lab___chart_qa echo840___ocr_bench vikhyatk___count_bench_qa lmms-lab___mme BLINK-Benchmark___blink Lin-Chen___mm_star lmms-lab___ai2d; do
    [ ! -d "$TMP_CACHE/$d" ] && MISSING_IN_CACHE+=("$d")
done
if [ ${#MISSING_IN_CACHE[@]} -gt 0 ]; then
    echo "[$(date '+%H:%M:%S')] ERROR: /tmp cache missing: ${MISSING_IN_CACHE[*]}"
    exit 3
fi
echo "[$(date '+%H:%M:%S')] All 8 datasets present in /tmp cache. Launching re-run."
echo ""
echo "===== PHASE B: re-running 4 failed GPU-groups ($(date '+%H:%M:%S')) ====="
PIDS=()
CUDA_VISIBLE_DEVICES=1 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks mmmu_pro_standard --batch_size 32 \
    --output "$LOG_DIR/eval_mmmu_pro.json" \
    > "$LOG_DIR/eval_mmmu_pro_rerun.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 1 (PID $!): mmmu_pro_standard"
CUDA_VISIBLE_DEVICES=4 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks chartqa,ocrbench,countbench --batch_size 32 \
    --output "$LOG_DIR/eval_chart_ocr_count.json" \
    > "$LOG_DIR/eval_chart_ocr_count_rerun.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 4 (PID $!): chartqa+ocrbench+countbench"
CUDA_VISIBLE_DEVICES=5 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks mme,blink --batch_size 32 \
    --output "$LOG_DIR/eval_mme_blink.json" \
    > "$LOG_DIR/eval_mme_blink_rerun.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 5 (PID $!): mme+blink"
CUDA_VISIBLE_DEVICES=6 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks ai2d,mmstar --batch_size 32 \
    --output "$LOG_DIR/eval_ai2d_mmstar.json" \
    > "$LOG_DIR/eval_ai2d_mmstar_rerun.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 6 (PID $!): ai2d+mmstar"
echo "[$(date '+%H:%M:%S')] All 4 re-run processes launched (PIDs: ${PIDS[*]})"
echo "[$(date '+%H:%M:%S')] Waiting for all to complete..."
ALL_OK=1
NAMES=("mmmu_pro" "chart_ocr_count" "mme_blink" "ai2d_mmstar")
for i in "${!PIDS[@]}"; do
    wait "${PIDS[$i]}"
    RC=$?
    echo "[$(date '+%H:%M:%S')] group ${NAMES[$i]} (PID ${PIDS[$i]}) exit=$RC"
    [ $RC -ne 0 ] && ALL_OK=0
done
echo ""
echo "===== PHASE C: re-consolidate ($(date '+%H:%M:%S')) ====="
if [ $ALL_OK -eq 1 ]; then
    echo "All 4 re-run groups succeeded! Consolidating all 12 benchmarks..."
else
    echo "Some re-run groups still failed. Consolidating whatever is available..."
fi
python mllm_bridge/consolidate_12benchmarks.py --results_dir "$LOG_DIR" || true
echo ""
echo "============================================================"
echo "  ArmC rerun OFFLINE COMPLETE: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  ALL_OK=$ALL_OK (1=all 4 groups succeeded)"
echo "  Results: $LOG_DIR/consolidated_12benchmarks.json"
echo "  Next (agent): generate report + EXPERIMENTS_VISION.md §13 + MEMORY"
echo "============================================================"
exit 0
