#!/bin/bash
# ==============================================================================
# run_e4_4ep.sh — ④ Epoch Scaling: 4-epoch training (748,404 steps)
#                 RESUME from 2ep checkpoint (374,202 steps done → 374,202 new)
#
# Operator instruction 2026-10-12 (user direct order, highest priority):
#   "vision 可以在现有 2ep 检查点基础上继续训练的方式启动 4ep 吗？
#    4ep 结果如果超过 70%，也是胜利。"
#
#   Resume from 2ep final checkpoint, --steps 748404 (= 4 × 187101).
#   All other parameters IDENTICAL to 2ep (run_e4_2ep.sh).
#   New output directory: scaling_E4_4ep_ov2_w512_d30_p16_224 (do NOT overwrite 2ep).
#
# Resume mechanism (verified from r9_train.py source):
#   - Loads vision + logit_scale + predictor + decoder state
#   - Does NOT load optimizer (AdamW restarts = minor transient)
#   - C4 guard disabled on resume; C1/C2 remain active
#   - LR recalculated for full 748404-step cosine (at step 374202, lr ≈ 2.5e-4,
#     jumping back from 2ep's min_lr=5e-5 — expected, AdamW re-warmup)
#   - Data sampler not restored, re-shuffled (correct for "4 epoch over same snapshot")
#
# Launch:
#   setsid bash run_e4_4ep.sh > /tmp/e4_4ep_train.log 2>&1 < /dev/null &
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
SNAPSHOT_FILE="data_snapshot_20261009.txt"
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
FAIR_DATA="${SNAPSHOT_FILE},${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

# ---- Resume from 2ep final checkpoint ----
RESUME_CKPT="$OUTROOT/scaling_E4_2ep_ov2_w512_d30_p16_224/vision.pt"
if [ ! -f "$RESUME_CKPT" ]; then
    RESUME_CKPT="$OUTROOT/scaling_E4_2ep_ov2_w512_d30_p16_224/vision_fused.pt"
fi
if [ ! -f "$RESUME_CKPT" ]; then
    RESUME_CKPT=$(ls "$OUTROOT"/scaling_E4_2ep_ov2_w512_d30_p16_224/vision_step*.pt 2>/dev/null | sort -V | tail -1)
fi

OUT="$OUTROOT/scaling_E4_4ep_ov2_w512_d30_p16_224"
LOG=/tmp/e4_4ep_train.log
STEPS=748404   # = 4 × 187101 (4 epochs of E1fair's frozen snapshot)

echo "===== ④-4ep START (resume from 2ep, w512/d30, 4-epoch, fair recipe) steps=$STEPS $(date '+%F %T') =====" | tee "$LOG"
echo "[④-4ep] resume_ckpt=$RESUME_CKPT" >> "$LOG"
echo "[④-4ep] data=$FAIR_DATA" >> "$LOG"
echo "[④-4ep] snapshot=$SNAPSHOT_FILE (total_shards=10787, 95.8M pairs)" >> "$LOG"
echo "[④-4ep] schedule: lr=5e-4, warmup=2000, cosine, min_lr=5e-5, steps=$STEPS" >> "$LOG"
echo "[④-4ep] output_dir=$OUT (NEW, does NOT overwrite 2ep)" >> "$LOG"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 5e-4 --warmup 2000 --scheduler cosine --min-lr 5e-5 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
    --data "$FAIR_DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
    --resume "$RESUME_CKPT" \
    --log-every 10 --probe-every 300 --probe-n 128 --num-workers 6 \
    --save-every 10000 --eval-data "$EVAL" >> "$LOG" 2>&1

rc=$?
echo "===== ④-4ep done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc
