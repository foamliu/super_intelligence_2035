#!/bin/bash
# launch_mmbench_static_B4.sh - B4 MMBench, CLEAN scoring (no OpenAI API).
#
# WHY THIS EXISTS (2026-10-25):
#   First B4 run used task `mmbench_en_dev` whose `gpt_eval_score` metric uses
#   eval_method="openai": ambiguous predictions fall back to GPT-judge, and with
#   NO OPENAI_API_KEY that path degrades to rd.randint() RANDOM guessing
#   (mmbench_evals.py:196-203). => the 24.14/23.88 numbers are CONTAMINATED.
#   This re-run uses `mmbench_en_dev_static` whose aggregation sets static_only=True
#   -> eval_sub_data uses extract_mcq_answer (regex MCQ extraction, NO API, NO random).
#   Model generation is identical; only scoring is clean/reproducible.
#
# Env identical to launch_mmbench_B4.sh. Output: eval_mmbench_static.json per arm.
# Usage: setsid bash mllm_bridge/launch_mmbench_static_B4.sh > /tmp/launch_mmbench_static_B4.log 2>&1 < /dev/null &
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
echo "  launch_mmbench_static_B4 started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  B4 MMBench CLEAN scoring: mmbench_en_dev_static (regex MCQ, no API)"
echo "  GPU 0 -> ArmB    -> $LOG_DIR_ARMB/eval_mmbench_static.json"
echo "  GPU 1 -> ArmE-R2 -> $LOG_DIR_ARME_R2/eval_mmbench_static.json"
echo "============================================================"

PIDS=()
CUDA_VISIBLE_DEVICES=0 python mllm_bridge/run_lmms_eval_r2.py \
    --vision_backend armB --tasks mmbench_en_dev_static --batch_size 32 \
    --output "$LOG_DIR_ARMB/eval_mmbench_static.json" \
    > "$LOG_DIR_ARMB/eval_mmbench_static.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 0 (PID $!): ArmB mmbench_en_dev_static"

CUDA_VISIBLE_DEVICES=1 python mllm_bridge/run_lmms_eval_r2.py \
    --vision_backend armE_r2 --tasks mmbench_en_dev_static --batch_size 32 \
    --output "$LOG_DIR_ARME_R2/eval_mmbench_static.json" \
    > "$LOG_DIR_ARME_R2/eval_mmbench_static.log" 2>&1 &
PIDS+=($!); echo "[$(date '+%H:%M:%S')] GPU 1 (PID $!): ArmE-R2 mmbench_en_dev_static"

echo "[$(date '+%H:%M:%S')] Both launched (PIDs: ${PIDS[*]}). Waiting..."
ALL_OK=1
for i in "${!PIDS[@]}"; do wait "${PIDS[$i]}"; RC=$?; echo "[$(date '+%H:%M:%S')] GPU $i exit=$RC"; [ $RC -ne 0 ] && ALL_OK=0; done
echo "============================================================"
echo "  launch_mmbench_static_B4 finished: $(date '+%Y-%m-%d %H:%M:%S')  (ALL_OK=$ALL_OK)"
echo "============================================================"
exit 0
