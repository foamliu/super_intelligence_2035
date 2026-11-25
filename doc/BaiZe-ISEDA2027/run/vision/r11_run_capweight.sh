#!/bin/bash
# R11-L caption-loss-weight 3-point ablation (replacement for the SKIPPED arm⑤ GenLIP).
#   Question: is caption supervision itself orthogonal to IN-1k frozen-trunk features,
#   or does caption_loss_weight=2.0 specifically crush the trunk?
#   Fixed recipe (identical to arm④ CoCa, ONLY the caption weight changes):
#   - Tower: OpenVision2 w512 (126.78M), depth30 / patch16 / 224².
#   - Text tower: FROZEN CLIP-768 (openai/clip-vit-large-patch14-336), context 77.
#   - Decoder: CoCaDecoder depth4/w768/h12 (+76.2M trainable), shared frozen CLIP vocab 49408.
#   - Data: CC12M + Amshaker (same globs as R9/R10/R11-L).
#   - Optimizer/schedule: AdamW lr 3e-3 warmup 20, seed 1234, bf16, bs64×8=512.
#   - Sample budget: N=15.36M = 30k steps (= arm④ anchor).
#   - Eval: IN-1k frozen-trunk lp (r8_eval_in1k.py) on step{10k,20k,30k}+final.
#   Weights: {0.5, 1.0} — 2.0 is already arm④ CoCa (lp 0.47% ≈ random).
#   Pre-registered verdict (EXPERIMENTS_VISION_ROUND11.md §12.2):
#     - 0.5 OR 1.0 lp@15.36M >= baseline(6.08%) - 1.5 (=4.58%)  -> weight=2.0 is the killer.
#     - 0.5 AND 1.0 lp@15.36M both < 4.58%                       -> caption supervision orthogonal.
# Usage:
#   bash r11_run_capweight.sh [steps=30000]
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
WEIGHTS="0.5 1.0"

CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r11_capweight.log

echo "===== R11-L caption-weight ablation START steps=$STEPS weights=[$WEIGHTS] $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

for W in $WEIGHTS; do
    TAG="$(echo "$W" | tr '.' 'p')"   # 0.5 -> 0p5, 1.0 -> 1p0
    OUT="$OUTROOT/R11L_capw${TAG}_w512"
    echo "===== R11-L caption-weight=$W openvision2 width=512 loss=coca ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width 512 --depth 30 \
        --steps "$STEPS" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --loss coca --caption-loss-weight "$W" --decoder-depth 4 \
        --data "$DATA" --data-source wds --output-dir "$OUT" \
        --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
        --eval-data "$EVAL" \
        >> "$LOG" 2>&1
    rc=$?
    echo "===== R11-L caption-weight=$W done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

    CKPTS=()
    if [ "$rc" -eq 0 ]; then
        for f in "$OUT"/vision_step10000.pt "$OUT"/vision_step20000.pt "$OUT"/vision_step30000.pt; do
            [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> "$LOG"
        done
        FINAL="$OUT/vision.pt"; [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
        [ -f "$FINAL" ] && CKPTS+=("$FINAL") || echo "[skip missing] $OUT/vision.pt|vision_fused.pt" >> "$LOG"
        echo "===== caption-weight=$W training done; IN-1k eval on ${#CKPTS[@]} ckpts =====" >> "$LOG"
        if [ "${#CKPTS[@]}" -gt 0 ]; then
            "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
        fi
    else
        echo "===== caption-weight=$W FAILED exit $rc; skip eval =====" >> "$LOG"
    fi
done
echo "===== R11-L caption-weight ablation ALL DONE $(date '+%F %T') =====" >> "$LOG"