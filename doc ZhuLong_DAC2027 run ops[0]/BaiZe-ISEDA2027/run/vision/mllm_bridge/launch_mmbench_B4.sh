#!/bin/bash
# launch_mmbench_B4.sh - B4 (next-steps report) feasible subset: MMBench en_dev
# on ArmB (ViT-B/16) + ArmE-R2 (ViT-L/14), full set, batch_size 32, single-GPU each.
#
# WHY ONLY MMBENCH (2026-10-25):
#   B4 report proposed MMBench + MMVet + MathVista + 336/anyres. Feasibility check:
#     - MMBench: rule-based MC scoring, data cached -> FEASIBLE (this script).
#     - MMVet  : gpt_eval_score (GPT judge) -> BLOCKED, no OPENAI_API_KEY.
#     - MathVista: gpt-3.5-turbo / llm_as_judge_eval -> BLOCKED, no API key + not cached.
#     - 336/anyres: bridge hardcodes Resize(224*1.15)/CenterCrop(224) + fixed
#       num_image_tokens (196/256) -> NOT implemented; needs engineering.
#   Pre-registered judgment (report §7): ArmB vs ArmE-R2 MMBench Δ>2pp => encoder
#   difference real (pursue A1 224->336); Δ<2pp => eval/alignment is bottleneck
#   (pursue B1-B3, don't enlarge encoder).
#
# Env mirrors launch_12benchmarks_armE_r2_offline.sh (12/12 success): proxy ON,
# /tmp cache for HF_DATASETS_CACHE + LMMS_EVAL_DATASETS_CACHE, /nas_env/hub for
# HF_HUB_CACHE (MMBench cached there), no OFFLINE flags (download-capable).
#
# Usage: setsid bash mllm_bridge/launch_mmbench_B4.sh > /tmp/launch_mmbench_B4.log 2>&1 < /dev/null &
set -uo pipefail
source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_TOKEN=hf_dummy
unset HF_ENDPOINT
export HF_HOME=/nas_env/app.e0031982/hf_home
TMP_CACHE=/tmp/lmms_eval_hf_datasets_app.e0031982
export HF_DATASETS_CACHE="$TMP_CACHE"
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
export HF_HUB_ENABLE_HF_TRANSFER=1
export LMMS_EVAL_DATASETS_CACHE="$TMP_CACHE"
export OMP_NUM_THREADS=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p "$LMMS_EVAL_DATASETS_CACHE"

LOG_DIR_ARMB=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armB
LOG_DIR_ARME_R2=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armE_r2_20261022
mkdir -p "$LOG_DIR_ARMB" "$LOG_DIR_ARME_R2"

echo "============================================================"
echo "  launch_mmbench_B4 started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  B4 feasible subset: MMBench en_dev (full, batch_size 32)"
echo "  GPU 0 -> ArmB (ViT-B/16, 768-d)   -> $LOG_DIR_ARMB/eval_mmbench.json"
echo "  GPU 1 -> ArmE-R2 (ViT-L/14, 1024-d) -> $LOG_DIR_ARME_R2/eval_mmbench.json"
echo "  HF_HUB_CACHE=$HF_HUB_CACHE  LMMS_EVAL_DATASETS_CACHE=$LMMS_EVAL_DATASETS_CACHE"
echo "============================================================"

AVAIL_KB=$(df -P "$LMMS_EVAL_DATASETS_CACHE" | tail -1 | awk '{print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
if [ "$AVAIL_GB" -lt 10 ]; then echo "  WARNING: Only ${AVAIL_GB}G free (<10G). Aborting."; exit 1; fi
echo "  Disk available (/tmp): ${AVAIL_GB}G"

PIDS=()

# GPU 0: ArmB (ViT-B/16) - uses run_lmms_eval_r2.py which supports --vision_backend armB
CUDA_VISIBLE_DEVICES=0 python mllm_bridge/run_lmms_eval_r2.py \
    --vision_backend armB --tasks mmbench_en_dev --batch_size 32 \
    --output "$LOG_DIR_ARMB/eval_mmbench.json" \
    > "$LOG_DIR_ARMB/eval_mmbench.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 0 (PID $!): ArmB mmbench_en_dev"

# GPU 1: ArmE-R2 (ViT-L/14)
CUDA_VISIBLE_DEVICES=1 python mllm_bridge/run_lmms_eval_r2.py \
    --vision_backend armE_r2 --tasks mmbench_en_dev --batch_size 32 \
    --output "$LOG_DIR_ARME_R2/eval_mmbench.json" \
    > "$LOG_DIR_ARME_R2/eval_mmbench.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 1 (PID $!): ArmE-R2 mmbench_en_dev"

echo "[$(date '+%H:%M:%S')] Both GPU processes launched (PIDs: ${PIDS[*]})"
echo "[$(date '+%H:%M:%S')] Waiting for both to complete..."

ALL_OK=1
for i in "${!PIDS[@]}"; do
    wait "${PIDS[$i]}"
    RC=$?
    echo "[$(date '+%H:%M:%S')] GPU $i exit=$RC"
    [ $RC -ne 0 ] && ALL_OK=0
done

echo "============================================================"
echo "  launch_mmbench_B4 finished: $(date '+%Y-%m-%d %H:%M:%S')  (ALL_OK=$ALL_OK)"
echo "  ArmB    log: $LOG_DIR_ARMB/eval_mmbench.log"
echo "  ArmE-R2 log: $LOG_DIR_ARME_R2/eval_mmbench.log"
echo "============================================================"
exit 0
