#!/bin/bash
# ==============================================================================
# run_merge3ds_smoke.sh — Smoke test for merge3ds experiment
#                          MBS=256 (×4), 10 steps, verify no OOM + C1 normal
#
# Operator instruction 2026-10-13 (放行执行):
#   "外部编码器 ProtB 做完后 → 立刻跑「合并三数据集实验」"
#   GBS/MBS ×4, 3-arm LR scan; if budget allows 1 arm → Arm C (×4 linear, Goyal)
#
# This smoke test verifies MBS=256 doesn't OOM before launching full training.
# Launch: bash run_merge3ds_smoke.sh 2>&1 | tee /tmp/merge3ds_smoke.log
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

# ---- Data: E1fair frozen snapshot (7437 GPIC tar) + CC12M + Amshaker ----
SNAPSHOT_FILE="data_snapshot_20261009.txt"
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
FAIR_DATA="${SNAPSHOT_FILE},${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

OUT="$OUTROOT/merge3ds_smoke_bs4_w512_d30_p16_224"
STEPS=10

echo "===== merge3ds SMOKE TEST (MBS=256, $STEPS steps) $(date '+%F %T') =====" | tee /tmp/merge3ds_smoke.log
echo "[smoke] data=$FAIR_DATA" >> /tmp/merge3ds_smoke.log
echo "[smoke] batch-size=256 (×4), lr=2e-3 (×4), warmup=8000 (×4)" >> /tmp/merge3ds_smoke.log
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv >> /tmp/merge3ds_smoke.log 2>&1

"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 256 --lr 2e-3 --warmup 8000 --scheduler cosine --min-lr 2e-4 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
    --data "$FAIR_DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
    --log-every 1 --probe-every 300 --probe-n 128 --num-workers 6 \
    --save-every 0 --eval-data "$EVAL" >> /tmp/merge3ds_smoke.log 2>&1

rc=$?
echo "===== merge3ds smoke done (exit $rc) $(date '+%F %T') =====" >> /tmp/merge3ds_smoke.log
nvidia-smi --query-gpu=index,memory.used --format=csv >> /tmp/merge3ds_smoke.log 2>&1
exit $rc
