#!/bin/bash
# Launch 12-benchmark eval (per user directive 2026-10-16) on 8 GPUs.
# One benchmark per GPU (single-process, no accelerate, no gather OOM).
# batch_size=32, full datasets (no --limit).
#
# 12 benchmarks: ai2d, blink, chartqa, docvqa_val, infovqa_val, mme,
#   mmmu_val, mmstar, ocrbench, realworldqa, countbench, mmmu_pro_standard
#
# GPU assignment (large benchmarks get own GPU, small ones share):
#   GPU 0: mmmu_val            (11550 samples)
#   GPU 1: mmmu_pro_standard   (3300 samples)
#   GPU 2: docvqa_val          (6349 samples)
#   GPU 3: infovqa_val         (2400 samples)
#   GPU 4: chartqa + ocrbench + countbench
#   GPU 5: mme + blink
#   GPU 6: ai2d + mmstar
#   GPU 7: realworldqa         (2456 samples)
#
# Usage: setsid bash -c 'exec bash mllm_bridge/launch_12benchmarks.sh' > /tmp/launch_12b.log 2>&1 < /dev/null &

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

LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results
mkdir -p "$LOG_DIR"

echo "============================================================"
echo "  launch_12benchmarks started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  12 benchmarks, per-GPU (no accelerate), batch_size=32"
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
    --tasks mmmu_val --batch_size 32 \
    --output "$LOG_DIR/eval_12b_mmmu_val.json" \
    > "$LOG_DIR/eval_12b_mmmu_val.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 0 (PID $!): mmmu_val"

# GPU 1: mmmu_pro_standard
CUDA_VISIBLE_DEVICES=1 python mllm_bridge/run_lmms_eval.py \
    --tasks mmmu_pro_standard --batch_size 32 \
    --output "$LOG_DIR/eval_12b_mmmu_pro.json" \
    > "$LOG_DIR/eval_12b_mmmu_pro.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 1 (PID $!): mmmu_pro_standard"

# GPU 2: docvqa_val
CUDA_VISIBLE_DEVICES=2 python mllm_bridge/run_lmms_eval.py \
    --tasks docvqa_val --batch_size 32 \
    --output "$LOG_DIR/eval_12b_docvqa.json" \
    > "$LOG_DIR/eval_12b_docvqa.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 2 (PID $!): docvqa_val"

# GPU 3: infovqa_val
CUDA_VISIBLE_DEVICES=3 python mllm_bridge/run_lmms_eval.py \
    --tasks infovqa_val --batch_size 32 \
    --output "$LOG_DIR/eval_12b_infovqa.json" \
    > "$LOG_DIR/eval_12b_infovqa.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 3 (PID $!): infovqa_val"

# GPU 4: chartqa + ocrbench + countbench
CUDA_VISIBLE_DEVICES=4 python mllm_bridge/run_lmms_eval.py \
    --tasks chartqa,ocrbench,countbench --batch_size 32 \
    --output "$LOG_DIR/eval_12b_chart_ocr_count.json" \
    > "$LOG_DIR/eval_12b_chart_ocr_count.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 4 (PID $!): chartqa+ocrbench+countbench"

# GPU 5: mme + blink
CUDA_VISIBLE_DEVICES=5 python mllm_bridge/run_lmms_eval.py \
    --tasks mme,blink --batch_size 32 \
    --output "$LOG_DIR/eval_12b_mme_blink.json" \
    > "$LOG_DIR/eval_12b_mme_blink.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 5 (PID $!): mme+blink"

# GPU 6: ai2d + mmstar
CUDA_VISIBLE_DEVICES=6 python mllm_bridge/run_lmms_eval.py \
    --tasks ai2d,mmstar --batch_size 32 \
    --output "$LOG_DIR/eval_12b_ai2d_mmstar.json" \
    > "$LOG_DIR/eval_12b_ai2d_mmstar.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 6 (PID $!): ai2d+mmstar"

# GPU 7: realworldqa
CUDA_VISIBLE_DEVICES=7 python mllm_bridge/run_lmms_eval.py \
    --tasks realworldqa --batch_size 32 \
    --output "$LOG_DIR/eval_12b_realworldqa.json" \
    > "$LOG_DIR/eval_12b_realworldqa.log" 2>&1 &
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
    echo "✅ All 12 benchmarks completed successfully!"
    python mllm_bridge/consolidate_12benchmarks.py
else
    echo "⚠️  Some tasks failed. Check logs in $LOG_DIR/eval_12b_*.log"
fi

echo "============================================================"
echo "  launch_12benchmarks finished: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
