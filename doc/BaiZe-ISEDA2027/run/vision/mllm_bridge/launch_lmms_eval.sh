#!/bin/bash
# Launch lmms-eval 17 benchmarks on BaiZe-LLaVA (8×H100 multi-GPU)
# Usage: bash launch_lmms_eval.sh [--step 3500] [--limit 100] [--batch_size 4]
#
# Proxy: direct to hf.co (NOT mirror)
# Multi-GPU: accelerate launch --multi_gpu --num_processes=8
set -e

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

# ---- proxy: direct to hf.co (NOT mirror) ----
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_TOKEN=hf_dummy  # needed by huggingface_hub 0.36+ for token=True in task configs
# Remove any hf-mirror settings
unset HF_ENDPOINT

export OMP_NUM_THREADS=1

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

OUTPUT_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results
mkdir -p "$OUTPUT_DIR"

# Pass through any extra args
EXTRA_ARGS="$@"

echo "============================================================"
echo "  BaiZe-LLaVA lmms-eval 17 Benchmarks (8×H100 multi-GPU)"
echo "  Proxy: $https_proxy (direct to hf.co)"
echo "  Extra args: $EXTRA_ARGS"
echo "  Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

exec accelerate launch \
    --multi_gpu \
    --num_processes=8 \
    --main_process_port=29556 \
    mllm_bridge/run_lmms_eval.py \
    $EXTRA_ARGS \
    > "$OUTPUT_DIR/eval.log" 2>&1
