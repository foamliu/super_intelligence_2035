#!/bin/bash
# R12 续跑 — Resume from R12 final ckpt (step 120k ≈ 1.05 epoch) to 344k steps (≈ 3 epochs).
#   Operator instruction 2026-10-05 (deep-night):
#     「R12 结束后安排续跑到 3 个 epoch，在 epoch=1/2/3 时分别评测对比，
#      做 scaling law 的计算，刷新原来的数据无限外推上限（25.1%）」
#
#   Recipe UNCHANGED (AIMv2-style = R11-G / R12 identical):
#     InfoNCE + 1.0×masked-patch-MSE, w512, frozen CLIP-768, bs64×8=512, seed 1234, bf16.
#   ONLY change: --steps 344000 (≈ 3 × 114,746) + --resume <R12 final ckpt>.
#
# Data (same as R12): GPIC (all types) + CC12M + Amshaker ≈ 58.8M unique pairs.
#   1 epoch ≈ 114,746 steps.  3 epochs ≈ 344,238 steps → use 344000.
#   R12 ran 120k (1.05 epoch).  续跑 adds 224k new steps (≈ 1.95 more epochs).
#
# save-every 10000 (consistent with R12) → dense (lp, N) curve.
#   Epoch-aligned ckpts:  120k≈1.05ep(R12) · 170k≈1.5ep · 230k≈2.0ep · 285k≈2.5ep · 340k≈3.0ep
#
# Usage:
#   bash r12_continue_3epoch.sh [resume_ckpt] [num_workers]
#   Default resume_ckpt = <OUT>/vision.pt (R12 final); num_workers = 6.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
OUT="$OUTROOT/R12_fulldata_aimv2_w512"
RESUME="${1:-$OUT/vision.pt}"
# fallback: if vision.pt missing, try vision_fused.pt, then latest vision_step*.pt
if [ ! -f "$RESUME" ]; then
    ALT="$OUT/vision_fused.pt"
    [ -f "$ALT" ] && RESUME="$ALT"
fi
if [ ! -f "$RESUME" ]; then
    RESUME=$(ls -t "$OUT"/vision_step*.pt 2>/dev/null | head -1)
fi
if [ ! -f "$RESUME" ]; then
    echo "ERROR: no resume checkpoint found in $OUT" >&2
    exit 1
fi
NW="${2:-6}"

GPIC='/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar'
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${GPIC},${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
LOG=/tmp/r12_continue_3epoch.log

echo "===== R12 续跑 (3 epoch) START resume=$RESUME $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

GPIC_N=$(ls $GPIC 2>/dev/null | wc -l)
CC12M_N=$(ls $CC12M 2>/dev/null | wc -l)
AMSH_N=$(ls $AMSH 2>/dev/null | wc -l)
echo "----- shard counts: GPIC=$GPIC_N CC12M=$CC12M_N Amshaker=$AMSH_N total=$((GPIC_N+CC12M_N+AMSH_N)) -----" >> "$LOG"
echo "----- resume ckpt: $RESUME -----" >> "$LOG"

echo "===== R12-continue openvision2 w512 loss=aimv2 mask=0.6 lambda=1.0 contrast=1.0 data=mixed caption_type=all --resume $RESUME --steps 344000 START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29500 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps 344000 --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
    --data "$DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
    --resume "$RESUME" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --save-every 10000 \
    --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== R12-continue training done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

# Collect ALL checkpoints (R12's 10k..120k + 续 run's 130k..340k + finals) and eval.
if [ "$rc" -eq 0 ]; then
    CKPTS=()
    while IFS= read -r f; do CKPTS+=("$f"); done < <(printf '%s\n' "$OUT"/vision_step*.pt 2>/dev/null | sort -V)
    FINAL="$OUT/vision.pt"
    [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL")

    if [ "${#CKPTS[@]}" -eq 0 ]; then
        echo "===== R12-continue ERROR: zero checkpoints produced. NOT evaluating. =====" >> "$LOG"
        cat "$LOG"
        exit 1
    fi

    echo "===== R12-continue IN-1k eval on ${#CKPTS[@]} ckpts (full scaling curve) =====" >> "$LOG"
    printf 'ckpt list: %s\n' "${CKPTS[@]}" >> "$LOG"
    "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
    echo "===== R12-continue ALL DONE $(date '+%F %T') =====" >> "$LOG"
else
    echo "===== R12-continue training FAILED (exit $rc), skipping eval =====" >> "$LOG"
fi
