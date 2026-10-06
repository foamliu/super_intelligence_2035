#!/bin/bash
# =============================================================================
# AIMv2 contrast/patch weight-ratio ablation (VISION_NEXT_DIRECTIONS.md 方向 3)
#   4 arms: (contrast_weight : patch_loss_weight) =
#           (1:2), (1:0.5), (0.5:1), (2:1)
#   Question: how much contrastive signal does the flip need?  R11-H proved
#   removing InfoNCE entirely (contrast=0) kills the flip (lp 6.23 vs 12.08).
#   But the RELATIVE ratio of the two weights was never tuned.  Is there an
#   optimal ratio, or is the flip robust to ratio in [0.5, 2.0]?
#
#   Fixed recipe (identical to R11-L arm6-A EXCEPT contrast/patch weights):
#   - Tower: OpenVision2 w512 (126.78M), depth30 / patch16 / 224^2.
#   - Text tower: FROZEN CLIP-768, context 77.
#   - Predictor: PatchPredictor (~0.66M trainable), MAE norm_pix_loss.
#   - mask_ratio = 0.6 (fixed, same as baseline).
#   - Data: CC12M + Amshaker, --data-source wds.
#   - Optimizer: AdamW lr 3e-3 warmup 20, seed 1234, bf16, bs64x8=512.
#   - Budget: 30k steps/arm (N=15.36M), save-every 10000.
#   - Eval: IN-1k frozen-trunk lp (r8_eval_in1k.py) on step{10k,20k,30k}.
#
#   Pre-registered verdict (VISION_NEXT_DIRECTIONS.md 方向 3):
#     - lp >= (1:1)-baseline + 1.5  -> "this ratio is more optimal"
#     - all ratios within +/- 1.5  -> "ratio insensitive in [0.5,2.0];
#       flip driven by co-presence, not proportion"
#     - NOTE: changing weights = changing recipe -> DO NOT merge into
#       R11-G/R12 scaling curve (must be reported separately).
#
#   Baseline: R11-L arm6-A (1:1) lp@30k = 12.08% (already exists, not re-run).
#
#   Cost: 4 arms x ~1.9h x 8 GPUs ~ 61 GPU-h (~7.6h wall-clock serial).
#
# Usage:
#   bash run_weight_ratio_ablation.sh [steps]
#   Default steps = 30000
#
# PREREQUISITE: R12b training must be FINISHED (GPUs free).
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
MASTERLOG=/tmp/ablation_weight_ratio.log

echo "===== weight-ratio ablation START steps=$STEPS $(date '+%F %T') =====" > "$MASTERLOG"
echo "----- hostname -----" >> "$MASTERLOG"
hostname >> "$MASTERLOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$MASTERLOG" 2>&1

# Arms: "CW:PLW" pairs — contrast_weight : patch_loss_weight
ARMS=( "1:2" "1:0.5" "0.5:1" "2:1" )
ALL_CKPTS=()
FAILED_ARMS=()

for PAIR in "${ARMS[@]}"; do
    CW="${PAIR%%:*}"
    PLW="${PAIR##*:}"
    TAG="cw${CW/./p}_plw${PLW/./p}"
    OUT="$OUTROOT/ABL_weight_ratio_${TAG}"
    LOG="/tmp/ablation_weight_ratio_${TAG}.log"
    echo "===== arm contrast=$CW patch=$PLW START $(date '+%F %T') =====" >> "$MASTERLOG"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((31000 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps "$STEPS" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --loss aimv2 --mask-ratio 0.6 --patch-loss-weight "$PLW" --contrast-weight "$CW" \
        --data "$DATA" --data-source wds --output-dir "$OUT" \
        --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
        --save-every 10000 --eval-data "$EVAL" \
        > "$LOG" 2>&1
    rc=$?
    echo "===== arm contrast=$CW patch=$PLW done (exit $rc) $(date '+%F %T') =====" >> "$MASTERLOG"
    if [ "$rc" -ne 0 ]; then
        echo "  [WARN] FAILED, skipping eval" >> "$MASTERLOG"
        FAILED_ARMS+=("$PAIR"); continue
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
echo "===== weight-ratio ablation ALL DONE $(date '+%F %T') =====" >> "$MASTERLOG"

