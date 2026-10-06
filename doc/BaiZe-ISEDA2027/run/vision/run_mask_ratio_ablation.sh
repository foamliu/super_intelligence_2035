#!/bin/bash
# =============================================================================
# AIMv2 mask-ratio ablation (VISION_NEXT_DIRECTIONS.md 方向 2)
#   5 arms: mask_ratio = 0.3 / 0.5 / 0.6 / 0.75 / 0.9
#   Question: what is the optimal dense-supervision density for the AIMv2-style
#   recipe (InfoNCE + masked-patch-MSE)?  mask_ratio=0.6 was chosen from MAE
#   literature (75%) but never ablated with a contrastive term present.
#
#   Fixed recipe (identical to R11-L arm6-A EXCEPT mask_ratio):
#   - Tower: OpenVision2 w512 (126.78M), depth30 / patch16 / 224^2.
#   - Text tower: FROZEN CLIP-768, context 77.
#   - Predictor: PatchPredictor (~0.66M trainable), MAE norm_pix_loss.
#   - Trunk forward UNCHANGED (all patches seen, no mask token).
#   - Data: CC12M + Amshaker (same globs as R9/R10/R11-L), --data-source wds.
#   - Optimizer: AdamW lr 3e-3 warmup 20, seed 1234, bf16, bs64x8=512.
#   - Budget: 30k steps/arm (N=15.36M), save-every 10000 (3 ckpts/arm).
#   - Eval: IN-1k frozen-trunk lp (r8_eval_in1k.py) on step{10k,20k,30k}.
#
#   Pre-registered verdict (VISION_NEXT_DIRECTIONS.md 方向 2):
#     - lp >= 0.6-baseline + 1.5  -> "this mask_ratio is more optimal"
#     - highest leads next by >= 1.5 -> "significantly optimal"
#     - noise band: +/- 1.5 pp
#     - NOTE: changing mask_ratio = changing recipe -> DO NOT merge into
#       R11-G/R12 scaling curve (must be reported separately).
#
#   Baseline: R11-L arm6-A mask_ratio=0.6 lp@30k = 12.08% (already exists).
#   Arm 0.6 is re-run here as a controlled reproduction.
#
#   Cost: 5 arms x ~1.9h x 8 GPUs ~ 76 GPU-h (~9.5h wall-clock serial).
#
# Usage:
#   bash run_mask_ratio_ablation.sh [arms] [steps]
#   Default arms = "0.3 0.5 0.6 0.75 0.9", steps = 30000
#   To skip 0.6: bash run_mask_ratio_ablation.sh "0.3 0.5 0.75 0.9"
#
# PREREQUISITE: R12b training must be FINISHED (GPUs free). Do NOT run while
#   R12b is still training -- this script uses all 8 GPUs.
# =============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
ARMS="${1:-0.3 0.5 0.6 0.75 0.9}"
STEPS="${2:-30000}"

CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
MASTERLOG=/tmp/ablation_mask_ratio.log

echo "===== mask-ratio ablation START arms=[$ARMS] steps=$STEPS $(date '+%F %T') =====" > "$MASTERLOG"
echo "----- hostname -----" >> "$MASTERLOG"
hostname >> "$MASTERLOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$MASTERLOG" 2>&1

CC12M_N=$(ls $CC12M 2>/dev/null | wc -l)
AMSH_N=$(ls $AMSH 2>/dev/null | wc -l)
echo "----- shards: CC12M=$CC12M_N Amshaker=$AMSH_N -----" >> "$MASTERLOG"

ALL_CKPTS=()
FAILED_ARMS=()

for MR in $ARMS; do
    MR_TAG="${MR/./p}"
    OUT="$OUTROOT/ABL_mask_ratio_${MR_TAG}"
    LOG="/tmp/ablation_mask_ratio_${MR_TAG}.log"
    echo "===== arm mask_ratio=$MR START $(date '+%F %T') =====" >> "$MASTERLOG"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((30000 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps "$STEPS" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --loss aimv2 --mask-ratio "$MR" --patch-loss-weight 1.0 --contrast-weight 1.0 \
        --data "$DATA" --data-source wds --output-dir "$OUT" \
        --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
        --save-every 10000 --eval-data "$EVAL" \
        > "$LOG" 2>&1
    rc=$?
    echo "===== arm mask_ratio=$MR done (exit $rc) $(date '+%F %T') =====" >> "$MASTERLOG"
    if [ "$rc" -ne 0 ]; then
        echo "  [WARN] FAILED, skipping eval" >> "$MASTERLOG"
        FAILED_ARMS+=("$MR"); continue
    fi
    for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
        [ -f "$f" ] && ALL_CKPTS+=("$f") || echo "  [skip missing] $f" >> "$MASTERLOG"
    done
    FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && ALL_CKPTS+=("$FINAL")
done

echo "===== IN-1k eval on ${#ALL_CKPTS[@]} ckpts START $(date '+%F %T') =====" >> "$MASTERLOG"
if [ "${#ALL_CKPTS[@]}" -gt 0 ]; then
    "$PY" r8_eval_in1k.py --ckpts "${ALL_CKPTS[@]}" >> "$MASTERLOG" 2>&1
fi
[ "${#FAILED_ARMS[@]}" -gt 0 ] && echo "===== WARNING: failed arms: ${FAILED_ARMS[*]} =====" >> "$MASTERLOG"
echo "===== mask-ratio ablation ALL DONE $(date '+%F %T') =====" >> "$MASTERLOG"

