#!/bin/bash
# R11-H — arm 6-B: PURE AR (NO contrast term), 30k steps.
#   ⑥-A kept InfoNCE (to control variables). Official AIMv2 = vision AR + text AR,
#   NO contrast. This arm removes InfoNCE to test whether the flip depends on the
#   contrastive term, or whether caption-INDEPENDENT dense patch supervision alone
#   suffices (closer to official AIMv2 route).
#   ONLY change vs ⑥-A: contrast_weight 1.0 -> 0.0 (total = 1.0 x masked-patch-MSE;
#   text tower NOT in gradient graph). c2-collapse-guard DISABLED (0) because C2_gap
#   measures cross-modal alignment which is N/A without a contrastive objective
#   (C1 feature-collapse + C4 loss-decreasing guards REMAIN active).
#   Pre-registered verdict (task book 2026-10-04 七), vs ⑥-A (11.39/11.14/12.08%):
#     - both @5.12M/@10.24M >= baseline+1.5 AND >= ⑥-A-1.5 -> "flip without contrast"
#     - <= ⑥-A-1.5 but >= baseline+1.5 -> "flip partially depends on contrast"
#     - collapse to random (<1%) or <= baseline+1.5 -> "flip depends on contrast"
#     - C1>0.95 / C4-not-decreasing -> auto-abort -> "not flipped (collapsed)"
# Usage:
#   bash r11h_run_pure_ar.sh [steps=30000] [num_workers=6]
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
STEPS="${1:-30000}"
NW="${2:-6}"

CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r11h_pure_ar.log

OUT="$OUTROOT/R11H_pure_ar_w512"
echo "===== R11-H arm6-B PURE AR (masked-patch-MSE only, NO InfoNCE) START steps=$STEPS $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

echo "===== R11-H openvision2 width=512 loss=aimv2 mask=0.6 lambda=1.0 contrast=0.0 c2guard=0 ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 0.0 --c2-collapse-guard 0 \
    --data "$DATA" --data-source wds --output-dir "$OUT" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== R11-H training done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

CKPTS=()
if [ "$rc" -eq 0 ]; then
    for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
        [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> "$LOG"
    done
    FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL") || echo "[skip missing] $OUT/vision.pt|vision_fused.pt" >> "$LOG"
    echo "===== R11-H IN-1k eval on ${#CKPTS[@]} ckpts =====" >> "$LOG"
    if [ "${#CKPTS[@]}" -gt 0 ]; then
        "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
    fi
else
    echo "===== R11-H FAILED exit $rc; skip eval =====" >> "$LOG"
fi
echo "===== R11-H ALL DONE $(date '+%F %T') =====" >> "$LOG"
