#!/bin/bash
# ==============================================================================
# run_armA_openclip.sh — ArmA: open_clip ViT-B/16 from-scratch CLIP training
#
# Operator instruction 2026-10-16:
#   "启动 vision ArmA（open_clip 从头训 encoder）"
#   - open_clip 标准 ViT-B/16 224px (86.2M visual / 149.6M total)
#   - 从头对比学习 (both towers random init, standard ClipLoss InfoNCE)
#   - 数据复用 GPIC(7437) + CC12M(1100) + Amshaker(2250) = 10787 shards ~118M
#   - 训完能被 open_clip.create_model_and_transforms(pretrained=ckpt) 加载
#   - 主判据 ProtB, 对齐 ④-4ep 口径
#
# Config (aligned with ArmC compute budget):
#   GBS=2048 (MBS=256×8), LR=2e-3, warmup=8000, cosine->2e-4, steps=154500 (~2.7ep)
#   AdamW wd=0.1 betas=(0.9,0.98), bf16, grad_clip=1.0
#
# Launch:
#   setsid bash run_armA_openclip.sh > /tmp/armA_openclip_train.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

SNAPSHOT_FILE="data_snapshot_20261009.txt"
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
FAIR_DATA="${SNAPSHOT_FILE},${CC12M},${AMSH}"
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
OUT="$OUTROOT/armA_openclip_vitb16_224"

LOG=/tmp/armA_openclip_train.log
STEPS=154500

echo "===== ArmA open_clip ViT-B/16 START $(date '+%F %T') =====" | tee "$LOG"
echo "[ArmA] model=open_clip ViT-B/16 224px (86.2M visual, 149.6M total, from scratch)" >> "$LOG"
echo "[ArmA] objective=CLIP InfoNCE (open_clip.loss.ClipLoss, global gather)" >> "$LOG"
echo "[ArmA] data=$FAIR_DATA" >> "$LOG"
echo "[ArmA] schedule: lr=2e-3, warmup=8000, cosine->min_lr=2e-4, steps=$STEPS" >> "$LOG"
echo "[ArmA] batch=256/GPU, GBS=2048, AdamW wd=0.1 betas=(0.9,0.98), bf16" >> "$LOG"
echo "[ArmA] output_dir=$OUT" >> "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
    armA_openclip_train.py \
    --data "$FAIR_DATA" --data-source mixed --caption-type all \
    --output-dir "$OUT" --steps "$STEPS" \
    --batch-size 256 --lr 2e-3 --min-lr 2e-4 --warmup 8000 \
    --wd 0.1 --beta1 0.9 --beta2 0.98 --precision bf16 --grad-clip 1.0 \
    --save-every 10000 --log-every 20 --num-workers 6 --seed 1234 >> "$LOG" 2>&1

rc=$?
echo "===== ArmA done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc
