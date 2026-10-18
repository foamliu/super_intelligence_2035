#!/bin/bash
# Launch 12-benchmark eval for ArmC (open_clip ViT-B/16, 768-d) MLLM.
# Per operator directive 2026-10-18 (P0): ArmC -> Stage-1/1.5/2 -> lmms-eval 12 sets.
# One benchmark per GPU, batch_size=32, full datasets (no --limit).
# Writes to a SEPARATE dir (mllm_eval_results_armC_20261018) so ④-4ep results are not clobbered.
#
# 12 benchmarks: ai2d, blink, chartqa, docvqa_val, infovqa_val, mme,
#   mmmu_val, mmstar, ocrbench, realworldqa, countbench, mmmu_pro_standard
#
# GPU assignment (same as ④ launch_12benchmarks.sh):
#   GPU 0: mmmu_val            GPU 4: chartqa + ocrbench + countbench
#   GPU 1: mmmu_pro_standard   GPU 5: mme + blink
#   GPU 2: docvqa_val          GPU 6: ai2d + mmstar
#   GPU 3: infovqa_val         GPU 7: realworldqa
#
# Usage: setsid bash -c 'exec bash mllm_bridge/launch_12benchmarks_armB.sh' > /tmp/launch_12b_armB.log 2>&1 < /dev/null &

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
export LMMS_EVAL_DATASETS_CACHE=/nas_env/app.e0031982/lmms_eval_cache
mkdir -p "$LMMS_EVAL_DATASETS_CACHE"

LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armC_20261018
mkdir -p "$LOG_DIR"

echo "============================================================"
echo "  launch_12benchmarks_armB started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  ArmC: open_clip ViT-B/16 768-d, Stage-2 step3500, batch_size=32"
echo "  Output dir: $LOG_DIR"
echo "============================================================"

AVAIL_KB=$(df -P "$LMMS_EVAL_DATASETS_CACHE" | tail -1 | awk '{print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
if [ "$AVAIL_GB" -lt 10 ]; then
    echo "  WARNING: Only ${AVAIL_GB}G free (<10G). Aborting."
    exit 1
fi
echo "  Disk available: ${AVAIL_GB}G"

PIDS=()

# GPU 0: mmmu_val
CUDA_VISIBLE_DEVICES=0 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks mmmu_val --batch_size 32 \
    --output "$LOG_DIR/eval_mmmu_val.json" \
    > "$LOG_DIR/eval_mmmu_val.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 0 (PID $!): mmmu_val"

# GPU 1: mmmu_pro_standard
CUDA_VISIBLE_DEVICES=1 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks mmmu_pro_standard --batch_size 32 \
    --output "$LOG_DIR/eval_mmmu_pro.json" \
    > "$LOG_DIR/eval_mmmu_pro.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 1 (PID $!): mmmu_pro_standard"

# GPU 2: docvqa_val
CUDA_VISIBLE_DEVICES=2 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks docvqa_val --batch_size 32 \
    --output "$LOG_DIR/eval_docvqa.json" \
    > "$LOG_DIR/eval_docvqa.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 2 (PID $!): docvqa_val"

# GPU 3: infovqa_val
CUDA_VISIBLE_DEVICES=3 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks infovqa_val --batch_size 32 \
    --output "$LOG_DIR/eval_infovqa.json" \
    > "$LOG_DIR/eval_infovqa.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 3 (PID $!): infovqa_val"

# GPU 4: chartqa + ocrbench + countbench
CUDA_VISIBLE_DEVICES=4 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks chartqa,ocrbench,countbench --batch_size 32 \
    --output "$LOG_DIR/eval_chart_ocr_count.json" \
    > "$LOG_DIR/eval_chart_ocr_count.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 4 (PID $!): chartqa+ocrbench+countbench"

# GPU 5: mme + blink
CUDA_VISIBLE_DEVICES=5 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks mme,blink --batch_size 32 \
    --output "$LOG_DIR/eval_mme_blink.json" \
    > "$LOG_DIR/eval_mme_blink.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 5 (PID $!): mme+blink"

# GPU 6: ai2d + mmstar
CUDA_VISIBLE_DEVICES=6 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks ai2d,mmstar --batch_size 32 \
    --output "$LOG_DIR/eval_ai2d_mmstar.json" \
    > "$LOG_DIR/eval_ai2d_mmstar.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 6 (PID $!): ai2d+mmstar"

# GPU 7: realworldqa
CUDA_VISIBLE_DEVICES=7 python mllm_bridge/run_lmms_eval.py \
    --vision_backend armC --tasks realworldqa --batch_size 32 \
    --output "$LOG_DIR/eval_realworldqa.json" \
    > "$LOG_DIR/eval_realworldqa.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 7 (PID $!): realworldqa"

echo "[$(date '+%H:%M:%S')] All 8 GPU processes launched (PIDs: ${PIDS[*]})"
echo "[$(date '+%H:%M:%S')] Waiting for all to complete..."

ALL_OK=1
for i in "${!PIDS[@]}"; do
    wait "${PIDS[$i]}"
    RC=$?
    echo "[$(date '+%H:%M:%S')] GPU $i exit=$RC"
    [ $RC -ne 0 ] && ALL_OK=0
done

if [ $ALL_OK -eq 1 ]; then
    echo "✅ All 12 benchmarks (ArmC) completed successfully!"
    python mllm_bridge/consolidate_12benchmarks.py --results_dir "$LOG_DIR"
else
    echo "⚠️  Some tasks failed. Check logs in $LOG_DIR/eval_*.log"
    python mllm_bridge/consolidate_12benchmarks.py --results_dir "$LOG_DIR" || true
fi

echo "============================================================"
echo "  launch_12benchmarks_armB finished: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
