#!/bin/bash
# Launch Stage-2 Instruct training (8×H100 DDP)
# Usage: bash launch_stage2.sh
set -e

source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
export OMP_NUM_THREADS=1

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

OUTPUT_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2
mkdir -p "$OUTPUT_DIR"

exec torchrun --nproc_per_node=8 --master_port=29555 \
    mllm_bridge/stage2_train.py \
    > "$OUTPUT_DIR/train.log" 2>&1
