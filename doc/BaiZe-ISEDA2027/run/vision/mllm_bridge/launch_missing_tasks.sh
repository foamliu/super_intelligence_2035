#!/bin/bash
# Launch 6 missing benchmark tasks on idle GPU 0 and GPU 7.
# Uses the NEW batched generate_until code (batch_size=32, log_samples=False).
#
# Tasks already running on GPUs 1-6 (started by previous wake):
#   mmmu_val(done), realworldqa(done), mmmu_pro, docvqa, infovqa,
#   chartqa+ocrbench+countbench, mme+blink, ai2d+mmstar
#
# Missing from the 13-task list:
#   mmbench_en_dev, gqa, textvqa_val, scienceqa, pope, vizwiz_vqa_val

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

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
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# All datasets already in HF Hub cache — prevent 429 rate limiting
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1

export LMMS_EVAL_DATASETS_CACHE=/nas_env/app.e0031982/lmms_eval_cache
mkdir -p "$LMMS_EVAL_DATASETS_CACHE"

LOG_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results
mkdir -p "$LOG_DIR"

echo "[$(date '+%H:%M:%S')] Launching 6 missing tasks on idle GPU 0 and GPU 7"

# ---- GPU 0: mmbench_en_dev + gqa + scienceqa ----
CUDA_VISIBLE_DEVICES=0 \
    python mllm_bridge/run_lmms_eval.py \
    --tasks mmbench_en_dev,gqa,scienceqa \
    --batch_size 32 \
    --output "$LOG_DIR/eval_missing_gpu0.json" \
    > "$LOG_DIR/eval_missing_gpu0.log" 2>&1 &
PID0=$!
echo "[$(date '+%H:%M:%S')] GPU 0 (PID $PID0): mmbench_en_dev, gqa, scienceqa"

# ---- GPU 7: textvqa_val + pope + vizwiz_vqa_val ----
CUDA_VISIBLE_DEVICES=7 \
    python mllm_bridge/run_lmms_eval.py \
    --tasks textvqa_val,pope,vizwiz_vqa_val \
    --batch_size 32 \
    --output "$LOG_DIR/eval_missing_gpu7.json" \
    > "$LOG_DIR/eval_missing_gpu7.log" 2>&1 &
PID7=$!
echo "[$(date '+%H:%M:%S')] GPU 7 (PID $PID7): textvqa_val, pope, vizwiz_vqa_val"

echo "[$(date '+%H:%M:%S')] Both processes launched. Waiting..."
wait $PID0
RC0=$?
wait $PID7
RC7=$?

echo "[$(date '+%H:%M:%S')] GPU 0 exit=$RC0, GPU 7 exit=$RC7"
if [ $RC0 -eq 0 ] && [ $RC7 -eq 0 ]; then
    echo "✅ All 6 missing tasks completed successfully!"
else
    echo "⚠️  Some tasks failed. Check logs in $LOG_DIR/eval_missing_gpu{0,7}.log"
fi
