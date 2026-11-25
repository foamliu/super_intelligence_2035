#!/bin/bash
# launch_12benchmarks_armE_r2_offline.sh - 12-benchmark eval for ArmE MLLM.
# Per operator directive 2026-10-19: ArmE -> Stage-1/1.5/2 -> lmms-eval 12 sets.
#
# CRITICAL FIX vs launch_12benchmarks_armC.sh: that script pointed
#   LMMS_EVAL_DATASETS_CACHE=/nas_env/app.e0031982/lmms_eval_cache (MISSING 8/12)
# which caused ArmC's 8/12 benchmarks to fail and required an offline rerun.
# HERE we point BOTH HF_DATASETS_CACHE + LMMS_EVAL_DATASETS_CACHE to the /tmp
# cache that ArmB's 12/12-success run used, keep proxy ON so missing datasets
# can still download (download-capable, not strictly offline).
#
# 12 benchmarks: ai2d, blink, chartqa, docvqa_val, infovqa_val, mme,
#   mmmu_val, mmstar, ocrbench, realworldqa, countbench, mmmu_pro_standard
# GPU assignment (same as ArmC):
#   GPU 0: mmmu_val            GPU 4: chartqa + ocrbench + countbench
#   GPU 1: mmmu_pro_standard   GPU 5: mme + blink
#   GPU 2: docvqa_val          GPU 6: ai2d + mmstar
#   GPU 3: infovqa_val         GPU 7: realworldqa
#
# Variables: ArmE vs ArmD-R2 = SINGLE VARIABLE (vision tower ViT-B/16 86.2M -> ViT-L/14 304.0M ONLY).
# Usage: setsid bash mllm_bridge/launch_12benchmarks_armE_r2_offline.sh > /tmp/launch_12b_armE_r2.log 2>&1 < /dev/null &
set -uo pipefail
source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_TOKEN=hf_dummy
unset HF_ENDPOINT
export HF_HOME=/nas_env/app.e0031982/hf_home
# FIX: /tmp cache that ArmB's 12/12-success run used (NOT nas_env cache).
TMP_CACHE=/tmp/lmms_eval_hf_datasets_app.e0031982
export HF_DATASETS_CACHE="$TMP_CACHE"
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
export HF_HUB_ENABLE_HF_TRANSFER=1
export LMMS_EVAL_DATASETS_CACHE="$TMP_CACHE"
export OMP_NUM_THREADS=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p "$LMMS_EVAL_DATASETS_CACHE"
LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armE_r2_20261022
mkdir -p "$LOG_DIR"
echo "============================================================"
echo "  launch_12benchmarks_armE_r2 started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  ArmE: open_clip ViT-L/14 1024-d, Stage-2 step3500, batch_size=32"
echo "  HF_DATASETS_CACHE=$HF_DATASETS_CACHE (FIX: /tmp cache, not nas_env)"
echo "  Output dir: $LOG_DIR"
echo "  Variables: ArmE-R2 vs ArmE = LR(1e-3->5e-4)+warmup(2000->3000) TWO vars; vs ArmD-R2 = tower(B/16->L/14)+LR+warmup THREE vars"
echo "============================================================"
AVAIL_KB=$(df -P "$LMMS_EVAL_DATASETS_CACHE" | tail -1 | awk '{print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
if [ "$AVAIL_GB" -lt 10 ]; then echo "  WARNING: Only ${AVAIL_GB}G free (<10G). Aborting."; exit 1; fi
echo "  Disk available: ${AVAIL_GB}G"
PIDS=()
CUDA_VISIBLE_DEVICES=0 python mllm_bridge/run_lmms_eval_r2.py --vision_backend armE_r2 --tasks mmmu_val --batch_size 32 --output "$LOG_DIR/eval_mmmu_val.json" > "$LOG_DIR/eval_mmmu_val.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 0 (PID $!): mmmu_val"
CUDA_VISIBLE_DEVICES=1 python mllm_bridge/run_lmms_eval_r2.py --vision_backend armE_r2 --tasks mmmu_pro_standard --batch_size 32 --output "$LOG_DIR/eval_mmmu_pro.json" > "$LOG_DIR/eval_mmmu_pro.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 1 (PID $!): mmmu_pro_standard"
CUDA_VISIBLE_DEVICES=2 python mllm_bridge/run_lmms_eval_r2.py --vision_backend armE_r2 --tasks docvqa_val --batch_size 32 --output "$LOG_DIR/eval_docvqa.json" > "$LOG_DIR/eval_docvqa.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 2 (PID $!): docvqa_val"
CUDA_VISIBLE_DEVICES=3 python mllm_bridge/run_lmms_eval_r2.py --vision_backend armE_r2 --tasks infovqa_val --batch_size 32 --output "$LOG_DIR/eval_infovqa.json" > "$LOG_DIR/eval_infovqa.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 3 (PID $!): infovqa_val"
CUDA_VISIBLE_DEVICES=4 python mllm_bridge/run_lmms_eval_r2.py --vision_backend armE_r2 --tasks chartqa,ocrbench,countbench --batch_size 32 --output "$LOG_DIR/eval_chart_ocr_count.json" > "$LOG_DIR/eval_chart_ocr_count.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 4 (PID $!): chartqa+ocrbench+countbench"
CUDA_VISIBLE_DEVICES=5 python mllm_bridge/run_lmms_eval_r2.py --vision_backend armE_r2 --tasks mme,blink --batch_size 32 --output "$LOG_DIR/eval_mme_blink.json" > "$LOG_DIR/eval_mme_blink.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 5 (PID $!): mme+blink"
CUDA_VISIBLE_DEVICES=6 python mllm_bridge/run_lmms_eval_r2.py --vision_backend armE_r2 --tasks ai2d,mmstar --batch_size 32 --output "$LOG_DIR/eval_ai2d_mmstar.json" > "$LOG_DIR/eval_ai2d_mmstar.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 6 (PID $!): ai2d+mmstar"
CUDA_VISIBLE_DEVICES=7 python mllm_bridge/run_lmms_eval_r2.py --vision_backend armE_r2 --tasks realworldqa --batch_size 32 --output "$LOG_DIR/eval_realworldqa.json" > "$LOG_DIR/eval_realworldqa.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 7 (PID $!): realworldqa"
echo "[$(date '+%H:%M:%S')] All 8 GPU processes launched (PIDs: ${PIDS[*]})"
echo "[$(date '+%H:%M:%S')] Waiting for all to complete..."
ALL_OK=1
for i in "${!PIDS[@]}"; do wait "${PIDS[$i]}"; RC=$?; echo "[$(date '+%H:%M:%S')] GPU $i exit=$RC"; [ $RC -ne 0 ] && ALL_OK=0; done
if [ $ALL_OK -eq 1 ]; then echo "All 12 benchmarks (ArmE) completed successfully!"; python mllm_bridge/consolidate_12benchmarks.py --results_dir "$LOG_DIR"; else echo "Some tasks failed. Re-run with rerun_failed_benchmarks_armD_offline.sh"; python mllm_bridge/consolidate_12benchmarks.py --results_dir "$LOG_DIR" || true; fi
echo "============================================================"
echo "  launch_12benchmarks_armE_r2 finished: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Results: $LOG_DIR/consolidated_12benchmarks.json"
echo "============================================================"
exit 0
