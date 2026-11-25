#!/bin/bash
# ==============================================================================
# rerun_failed_benchmarks_armC.sh — re-run the 8 MISSING ArmC ④ benchmarks
#
# Context (wake #171, 2026-10-19 18:0x):
#   ArmC ④ 12-benchmark chain completed 17:27 but 8/12 FAILED with
#   `tenacity.RetryError: ConnectionError` during task.download(). Root cause =
#   PROXY DOWN at 17:17 (both 172.19.92.25:13128 and 172.19.92.23:13128 unreachable).
#   The 8 failing tasks use tenacity-wrapped DIRECT-URL downloads (requests/urllib)
#   that bypass HF_HUB_OFFLINE; they NEED a working proxy. ArmB succeeded 12/12
#   on 10-18 with the SAME script because the proxy was up. -> NOT a model/config
#   problem. Re-running with the proxy down fails identically.
#
#   4 benchmarks SUCCEEDED (data cached, no direct-URL download) -> jsons KEPT:
#     eval_mmmu_val.json (0.4256) / eval_docvqa.json (0.0758) /
#     eval_infovqa.json (0.1709) / eval_realworldqa.json (0.4497)
#   8 MISSING (re-run here, 4 GPU-groups, same GPUs as original):
#     GPU1 mmmu_pro_standard -> eval_mmmu_pro.json
#     GPU4 chartqa,ocrbench,countbench -> eval_chart_ocr_count.json
#     GPU5 mme,blink -> eval_mme_blink.json
#     GPU6 ai2d,mmstar -> eval_ai2d_mmstar.json
#
# Strategy: POLL proxy every 300s (<=240 tries ≈20h). When a proxy reaches
#   huggingface.co, run the 4 groups with the ORIGINAL launch env (offline ON +
#   HF_HUB_ENABLE_HF_TRANSFER=1 = ArmB known-good config), then re-consolidate
#   (merges 4 kept + 4 new jsons = all 12 benchmarks).
#   Variables: ArmC = min_lr 1e-4->1e-5 + wd 0.1->0.01 (TWO vars, NOT single-var).
# Launch: setsid bash rerun_failed_benchmarks_armC.sh > /tmp/armC_rerun_benchmarks.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail

VISION_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armC_20261018
PROXY_25=http://172.19.92.25:13128
PROXY_23=http://172.19.92.23:13128

cd "$VISION_DIR"

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

export HF_TOKEN=hf_dummy
unset HF_ENDPOINT
export HF_HOME=/nas_env/app.e0031982/hf_home
export HF_DATASETS_CACHE=$HF_HOME/datasets
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export LMMS_EVAL_DATASETS_CACHE=/nas_env/app.e0031982/lmms_eval_cache
export OMP_NUM_THREADS=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p "$LMMS_EVAL_DATASETS_CACHE" "$LOG_DIR"

echo "============================================================"
echo "  ArmC rerun_failed_benchmarks started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Re-run 8 MISSING benchmarks (4 GPU-groups); keep 4 successful jsons"
echo "  Variables: min_lr 1e-4->1e-5 + wd 0.1->0.01 (TWO vars)"
echo "============================================================"

# PHASE A: poll for a working proxy (huggingface.co reachability)
WORKING_PROXY=""
ATTEMPT=0
MAX_ATTEMPTS=240
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "[$(date '+%H:%M:%S')] proxy poll attempt $ATTEMPT/$MAX_ATTEMPTS"
    for P in "$PROXY_25" "$PROXY_23"; do
        CODE=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 8 --proxy "$P" https://huggingface.co 2>/dev/null || echo "000")
        echo "[$(date '+%H:%M:%S')]   $P -> HTTP $CODE"
        case "$CODE" in 200|301|302|307|308) WORKING_PROXY="$P"; break;; esac
    done
    if [ -n "$WORKING_PROXY" ]; then
        echo "[$(date '+%H:%M:%S')] ✅ Working proxy found: $WORKING_PROXY"
        break
    fi
    echo "[$(date '+%H:%M:%S')] no proxy yet; sleeping 300s..."
    sleep 300
done

if [ -z "$WORKING_PROXY" ]; then
    echo "[$(date '+%H:%M:%S')] ERROR: no working proxy after $MAX_ATTEMPTS attempts (~20h). Giving up."
    echo "  4 successful benchmarks kept; 8 remain MISSING (proxy infra)."
    exit 2
fi

export https_proxy="$WORKING_PROXY"
export http_proxy="$WORKING_PROXY"
echo "[$(date '+%H:%M:%S')] https_proxy=$https_proxy  http_proxy=$http_proxy"

# PHASE B: run the 4 failed GPU-groups (parallel, GPUs 1/4/5/6, all free)
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

# PHASE C: re-consolidate (merges 4 kept + 4 new jsons = all 12 benchmarks)
echo ""
echo "===== PHASE C: re-consolidate ($(date '+%H:%M:%S')) ====="
if [ $ALL_OK -eq 1 ]; then
    echo "✅ All 4 re-run groups succeeded! Consolidating all 12 benchmarks..."
else
    echo "⚠️  Some re-run groups still failed. Consolidating whatever is available..."
fi
python mllm_bridge/consolidate_12benchmarks.py --results_dir "$LOG_DIR" || true

echo ""
echo "============================================================"
echo "  ArmC rerun_failed_benchmarks COMPLETE: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  ALL_OK=$ALL_OK (1=all 4 groups succeeded)"
echo "  Results: $LOG_DIR/consolidated_12benchmarks.json"
echo "  Re-run logs: $LOG_DIR/eval_*_rerun.log"
echo "  Next (agent): generate report + EXPERIMENTS_VISION.md §13 + MEMORY"
echo "============================================================"
exit 0
