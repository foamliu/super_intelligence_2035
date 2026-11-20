#!/bin/bash
# Run ai2d --limit 5 single-GPU test for Part B ③ validation
source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_HOME=/nas_env/app.e0031982/hf_home
export HF_DATASETS_CACHE=$HF_HOME/datasets
export HF_HUB_CACHE=$HF_HOME/hub
export TRANSFORMERS_CACHE=$HF_HOME/transformers
export HF_TOKEN=hf_dummy
export HF_HUB_ENABLE_HF_TRANSFER=1
export LMMS_EVAL_DATASETS_CACHE=/tmp/lmms_eval_hf_datasets_app.e0031982
export OMP_NUM_THREADS=1
export CUDA_VISIBLE_DEVICES=0
unset HF_ENDPOINT

LOG=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results/ai2d_limit5_gpu_test.log

echo "=== ai2d --limit 5 GPU test started: $(date) ===" > "$LOG"

python mllm_bridge/run_lmms_eval.py \
    --tasks ai2d \
    --limit 5 \
    --batch_size 1 \
    --output /nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results/ai2d_limit5_gpu_test.json \
    >> "$LOG" 2>&1

RC=$?
echo "=== ai2d --limit 5 GPU test finished: $(date), exit code=$RC ===" >> "$LOG"
