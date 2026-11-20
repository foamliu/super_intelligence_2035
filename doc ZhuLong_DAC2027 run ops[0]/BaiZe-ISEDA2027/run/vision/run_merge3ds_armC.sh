#!/bin/bash
# ==============================================================================
# run_merge3ds_armC.sh — Merge 3 datasets experiment, Arm C (LR ×4, linear)
#                        GBS=2048 (MBS=256×8), LR=2e-3, warmup=8000, steps=154500
#                        ~2.85 true epoch @ GBS=2048, ~24h budget
#
# Operator instruction 2026-10-13 (放行执行 + LR 缩放按文献规则):
#   "外部编码器 ProtB 做完后 → 立刻跑「合并三数据集实验」"
#   "GBS ×4 时 LR 应该怎么变" → Goyal linear scaling rule: LR ×4 (5e-4 → 2e-3)
#   "若预算只允许 1 个 LR ⇒ 取线性 ×4（有 Goyal 直接依据）"
#
# Single variable: GBS/MBS/LR changed from ④-4ep baseline; everything else
# byte-identical (same data, tower, loss, mask-ratio, scheduler, etc.)
# NO --resume (fresh training, not continuing from ④-4ep).
#
# Literature: Goyal et al. 2017 (arXiv:1706.02677) — linear scaling + warmup
#
# Launch:
#   setsid bash run_merge3ds_armC.sh > /tmp/merge3ds_armC_train.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

# ---- Data: E1fair frozen snapshot (7437 GPIC tar = 94.0M pairs) + CC12M (1100 tar = 11.0M) + Amshaker (2250 tar = 5.95M) ----
# Total: ~110.9M pairs (snapshot) / ~118.1M (full 8000 GPIC tar)
SNAPSHOT_FILE="data_snapshot_20261009.txt"
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
FAIR_DATA="${SNAPSHOT_FILE},${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

OUT="$OUTROOT/merge3ds_bs4_lrC_w512_d30_p16_224"
LOG=/tmp/merge3ds_armC_train.log
STEPS=154500   # ≈ 2.85 true epoch @ GBS=2048 (110.9M pairs), ~24h budget

echo "===== merge3ds ArmC START (GBS=2048, LR=2e-3 ×4 linear, $STEPS steps) $(date '+%F %T') =====" | tee "$LOG"
echo "[ArmC] data=$FAIR_DATA" >> "$LOG"
echo "[ArmC] snapshot=$SNAPSHOT_FILE (7437 GPIC tar, total_shards=10787, ~110.9M pairs)" >> "$LOG"
echo "[ArmC] schedule: lr=2e-3 (×4), warmup=8000 (×4), cosine, min_lr=2e-4 (×4), steps=$STEPS" >> "$LOG"
echo "[ArmC] batch-size=256 (×4), GBS=256×8=2048 (×4 vs baseline 512)" >> "$LOG"
echo "[ArmC] output_dir=$OUT" >> "$LOG"
echo "[ArmC] NO --resume (fresh training)" >> "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 256 --lr 2e-3 --warmup 8000 --scheduler cosine --min-lr 2e-4 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
    --data "$FAIR_DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
    --log-every 10 --probe-every 300 --probe-n 128 --num-workers 6 \
    --save-every 10000 --eval-data "$EVAL" >> "$LOG" 2>&1

rc=$?
echo "===== merge3ds ArmC done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc
