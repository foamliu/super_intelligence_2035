#!/bin/bash
# R11-L arm6-A (AIMv2-style: InfoNCE + masked patch reconstruction).
#   Question (EXPERIMENTS_VISION_ROUND11.md section 14): can caption-INDEPENDENT dense
#   supervision (MAE-style masked patch pixel prediction) break the R9 25.1% asymptote,
#   where caption-DEPENDENT dense supervision (CoCa arm4) collapsed to random (0.47%)?
#   Isolates "caption-dependence" as the SOLE variable vs arm1 (InfoNCE only).
#   Fixed recipe (identical to arm1/arm4 EXCEPT the dense term):
#   - Tower: OpenVision2 w512 (126.78M), depth30 / patch16 / 224^2.
#   - Text tower: FROZEN CLIP-768 (openai/clip-vit-large-patch14-336), context 77.
#   - Predictor: PatchPredictor (~0.66M trainable) on masked patches, MAE norm_pix_loss.
#   - Trunk forward UNCHANGED (all patches seen, no token drop / mask token) -> frozen-trunk
#     linear-probe eval directly comparable to arm1. mask_ratio=0.6, patch_loss_weight=1.0.
#   - Data: CC12M + Amshaker (same globs as R9/R10/R11-L).
#   - Optimizer/schedule: AdamW lr 3e-3 warmup 20, seed 1234, bf16, bs64x8=512.
#   - Sample budget: N=15.36M = 30k steps (= arm4 anchor).
#   - Eval: IN-1k frozen-trunk lp (r8_eval_in1k.py) on step{10k,20k,30k}+final.
#   Pre-registered verdict (section 14.4):
#     - lp >= baseline + 1.5 at BOTH 5.12M(10k) and 10.24M(20k) -> "flipped" -> run 6-B/lambda sweep.
#     - lp <= baseline - 1.5                                  -> "worse".
#     - otherwise                                             -> hypothesis falsified (negative result).
# Usage:
#   bash r11_run_aimv2.sh [steps=30000]
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
LOG=/tmp/r11_aimv2.log

echo "===== R11-L arm6-A AIMv2-style (MIM+InfoNCE) START steps=$STEPS $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

OUT="$OUTROOT/R11L_aimv2_w512"
echo "===== arm6-A openvision2 width=512 loss=aimv2 mask=0.6 lambda=1.0 ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 \
    --data "$DATA" --data-source wds --output-dir "$OUT" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== arm6-A training done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

CKPTS=()
if [ "$rc" -eq 0 ]; then
    for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
        [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> "$LOG"
    done
    FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL") || echo "[skip missing] $OUT/vision.pt|vision_fused.pt" >> "$LOG"
    echo "===== arm6-A training done; IN-1k eval on ${#CKPTS[@]} ckpts =====" >> "$LOG"
    if [ "${#CKPTS[@]}" -gt 0 ]; then
        "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
    fi
else
    echo "===== arm6-A FAILED exit $rc; skip eval =====" >> "$LOG"
fi
echo "===== R11-L arm6-A ALL DONE $(date '+%F %T') =====" >> "$LOG"
