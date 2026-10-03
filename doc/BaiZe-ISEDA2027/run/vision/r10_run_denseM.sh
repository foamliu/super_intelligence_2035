#!/bin/bash
# R10-③ (conditional) — densify the M (model-width) axis of the 2D scaling law.
#   Train OpenVision2 @ width{384,640} for 30000 steps (same recipe/data/batch as
#   stage-1's w{512,768,1024}), so they slot directly into the M axis:
#     params ~ 4.8e-4 * width^2  ->  w384=~71M, w640=~197M  (vs 126.8/284.5/505.2M).
#   Serial TP1/DP8, then recover periodic ckpts' IN-1k via r8_eval_in1k.py --ckpts.
# Usage:
#   bash r10_run_denseM.sh [widths="384 640"] [steps=30000]
# NOTE: needs all 8 GPUs free (do NOT run while r10_eval_stage1.sh holds GPU 0).
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
WIDTHS="${1:-384 640}"
STEPS="${2:-30000}"
NW=6

# Same data as stage-1 (CC12M + Amshaker), same recipe -> directly comparable to w{512,768,1024}.
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r10_denseM.log

echo "===== R10-3 denseM START widths='$WIDTHS' steps=$STEPS $(date '+%F %T') =====" > "$LOG"
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

CKPTS=()
for W in $WIDTHS; do
    OUT="$OUTROOT/R10_denseM_w${W}"
    echo "===== R10-3 openvision2 width=$W ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width "$W" --depth 30 \
        --steps "$STEPS" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --data "$DATA" --data-source wds --output-dir "$OUT" \
        --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
        --eval-data "$EVAL" \
        >> "$LOG" 2>&1
    rc=$?
    echo "===== R10-3 openvision2 width=$W done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
    if [ "$rc" -ne 0 ]; then
        echo "===== R10-3 width=$W FAILED with exit $rc; skipping its eval. =====" >> "$LOG"
        continue
    fi
    # collect periodic ckpts + final (vision_step10000/20000/30000 + vision.pt / vision_fused.pt)
    for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
        [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> "$LOG"
    done
    FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL") || echo "[skip missing] $OUT/vision.pt|vision_fused.pt" >> "$LOG"
done

echo "===== R10-3 training done; IN-1k eval on ${#CKPTS[@]} ckpts =====" >> "$LOG"
if [ "${#CKPTS[@]}" -gt 0 ]; then
    "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
fi
echo "===== R10-3 denseM ALL DONE $(date '+%F %T') =====" >> "$LOG"