#!/bin/bash
# =============================================================================
# AIMv2 AR + InfoNCE hybrid — R13 follow-up (VISION_AIMV2_OFFICIAL_PLAN.md)
#   Arm B (pure AR) collapsed at step 600 (C1=0.9731) without contrastive.
#   This hybrid tests: does adding InfoNCE to the AR paradigm prevent collapse?
#
#   Arm B (pure AR):  causal ViT + cap + pixel, NO InfoNCE → COLLAPSED @600
#   Arm B-hybrid:     causal ViT + InfoNCE + cap + pixel → ???
#   Arm A (baseline): bidirectional + InfoNCE + masked-patch-MSE → lp@30k=12.08%
#
#   Recipe (hybrid):
#   - Same as Arm B but with --contrast-weight 1.0 (adds InfoNCE on causal pooled)
#   - --c2-collapse-guard 1 (C2 gap guard active, since contrastive IS in graph)
#   - Everything else identical to run_aimv2_ar.sh for controlled comparison
#
#   This answers: Is the collapse caused by the AR paradigm itself, or by the
#   absence of contrastive learning?
#     - If hybrid survives (C1<0.95) → contrastive prevents collapse
#     - If hybrid also collapses → causal AR is fundamentally prone to collapse
#
# Usage:
#   bash run_aimv2_ar_hybrid.sh [steps]
#   Default steps = 30000
# =============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
STEPS="${1:-30000}"
NW=6

CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
OUT="$OUTROOT/R13_aimv2_ar_hybrid_w512"
LOG=/tmp/r13_aimv2_ar_hybrid.log

echo "===== AIMv2 AR+InfoNCE hybrid START steps=$STEPS $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

CC12M_N=$(ls $CC12M 2>/dev/null | wc -l)
AMSH_N=$(ls $AMSH 2>/dev/null | wc -l)
echo "----- shards: CC12M=$CC12M_N Amshaker=$AMSH_N -----" >> "$LOG"

echo "===== smoke test (30 steps) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((32000 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps 30 --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss aimv2_ar --alpha-pixel 0.4 --decoder-depth 4 \
    --contrast-weight 1.0 --c2-collapse-guard 1 \
    --data "$DATA" --data-source wds --output-dir "$OUT" \
    --log-every 10 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --save-every 0 --eval-data "$EVAL" \
    >> "$LOG" 2>&1
smoke_rc=$?
echo "===== smoke test done (exit $smoke_rc) $(date '+%F %T') =====" >> "$LOG"
if [ "$smoke_rc" -ne 0 ]; then
    echo "  [FATAL] smoke test FAILED — aborting before full run" >> "$LOG"
    cat "$LOG"
    exit 1
fi

echo "===== smoke throughput check =====" >> "$LOG"
grep 'image/s=' "$LOG" | tail -3 >> "$LOG"

echo "===== full run ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((32100 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss aimv2_ar --alpha-pixel 0.4 --decoder-depth 4 \
    --contrast-weight 1.0 --c2-collapse-guard 1 \
    --data "$DATA" --data-source wds --output-dir "$OUT" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --save-every 10000 --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== full run done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

if [ "$rc" -ne 0 ]; then
    echo "  [WARN] full run FAILED" >> "$LOG"
    cat "$LOG"
    exit 1
fi

# Eval all saved checkpoints
ALL_CKPTS=()
for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
    [ -f "$f" ] && ALL_CKPTS+=("$f") || echo "  [skip missing] $f" >> "$LOG"
done
FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
[ -f "$FINAL" ] && ALL_CKPTS+=("$FINAL")

echo "===== IN-1k eval on ${#ALL_CKPTS[@]} ckpts START $(date '+%F %T') =====" >> "$LOG"
if [ "${#ALL_CKPTS[@]}" -gt 0 ]; then
    "$PY" r8_eval_in1k.py --ckpts "${ALL_CKPTS[@]}" >> "$LOG" 2>&1
fi
echo "===== AIMv2 AR+InfoNCE hybrid ALL DONE $(date '+%F %T') =====" >> "$LOG"