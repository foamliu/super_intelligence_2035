#!/bin/bash
# ==============================================================================
# run_e4_2ep.sh — ④ Epoch Scaling: 2-epoch training (374,202 steps)
#
# Operator instruction 2026-10-10 ④ (most decision-relevant):
#   "Same data/target/protocol/schedule as E1fair, only increase epoch count."
#   E1fair = 1 epoch (187,101 steps, 95.8M pairs, total_shards=10787).
#   ④-2ep  = 2 epoch (374,202 steps), SAME frozen snapshot, SAME fair recipe.
#
# Pre-registered criteria (EXPERIMENTS_VISION.md §9.4):
#   2ep ≥ 70%  → budget insufficient → launch 4ep
#   2ep 63.8–70% → moderate gain, diminishing returns
#   2ep ~63% (flat) → feature/objective quality ceiling
#   2ep ≤ 60.8% → overfitting (R12b precedent)
#
# Launch:
#   setsid bash run_e4_2ep.sh > /tmp/e4_2ep_train.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

# ---- Data: E1fair frozen snapshot (total_shards=10787, 95.8M pairs) ----
# CWD is already vision/ (from cd at top), so relative path works
SNAPSHOT_FILE="data_snapshot_20261009.txt"
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
FAIR_DATA="${SNAPSHOT_FILE},${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

OUT="$OUTROOT/scaling_E4_2ep_ov2_w512_d30_p16_224"
LOG=/tmp/e4_2ep_train.log
STEPS=374202   # = 2 × 187101 (2 epochs of E1fair's frozen snapshot)

echo "===== ④-2ep START (w512/d30, 2-epoch, fair recipe) steps=$STEPS $(date '+%F %T') =====" | tee "$LOG"
echo "[④-2ep] data=$FAIR_DATA" >> "$LOG"
echo "[④-2ep] snapshot=$SNAPSHOT_FILE (total_shards=10787, 95.8M pairs)" >> "$LOG"
echo "[④-2ep] schedule: lr=5e-4, warmup=2000, cosine, min_lr=5e-5, steps=$STEPS" >> "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 5e-4 --warmup 2000 --scheduler cosine --min-lr 5e-5 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
    --data "$FAIR_DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
    --log-every 10 --probe-every 300 --probe-n 128 --num-workers 6 \
    --save-every 10000 --eval-data "$EVAL" >> "$LOG" 2>&1

rc=$?
echo "===== ④-2ep done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc
