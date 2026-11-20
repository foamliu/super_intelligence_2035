#!/bin/bash
# R11-G — AIMv2-style LONG run (108k steps) to re-fit scaling & extrapolate.
#   ⑥-A only gave 30k (N<=15.36M), 3 non-monotonic points -> cannot fit/extrapolate.
#   This run extends to 108k (= 55.3M samples, aligned to R9 stage-2) to answer
#   "what is the asymptote after the AIMv2-style flip?"
#   Same recipe as ⑥-A: InfoNCE + 1.0x masked-patch-MSE (contrast_weight=1.0).
#   ONLY change: steps 30k -> 108k. save-every 10000 (aligned to R9 stage-2) ->
#   ckpts step{10k..100k} + final = 11 points for scaling-curve fit.
#   Pre-registered verdict (task book 2026-10-04 七):
#     - power-law a-b*N^-c + log-linear fit, report R^2 + asymptote a
#     - R^2>=0.90 AND a > 25.1% -> "objective function raises asymptote" (positive)
#     - R^2<0.90 OR non-monotonic -> "not simple power law, need more points" (honest)
#     - baseline: InfoNCE acc=0.251-0.864*N^-0.090 (R^2~0.94)
# Usage:
#   bash r11g_run_aimv2_long.sh [steps=108000] [num_workers=6]
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
STEPS="${1:-108000}"
NW="${2:-6}"

CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r11g_aimv2_long.log

OUT="$OUTROOT/R11G_aimv2_long_w512"
echo "===== R11-G AIMv2-style LONG (MIM+InfoNCE) START steps=$STEPS $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

echo "===== R11-G openvision2 width=512 loss=aimv2 mask=0.6 lambda=1.0 contrast=1.0 ($STEPS steps, save-every 10000) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
    --data "$DATA" --data-source wds --output-dir "$OUT" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --save-every 10000 \
    --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== R11-G training done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

# Collect ALL checkpoints for the scaling curve: vision_step*.pt (sorted) + final
CKPTS=()
if [ "$rc" -eq 0 ]; then
    while IFS= read -r f; do CKPTS+=("$f"); done < <(printf '%s\n' "$OUT"/vision_step*.pt 2>/dev/null | sort -V)
    FINAL="$OUT/vision.pt"
    [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL")
fi

if [ "${#CKPTS[@]}" -eq 0 ]; then
    echo "===== R11-G ERROR: zero checkpoints produced (train exit=$rc). NOT evaluating. =====" >> "$LOG"
    cat "$LOG"
    exit 1
fi

echo "===== R11-G IN-1k eval on ${#CKPTS[@]} ckpts (scaling curve) =====" >> "$LOG"
printf 'ckpt list: %s\n' "${CKPTS[@]}" >> "$LOG"
"$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
echo "===== R11-G ALL DONE $(date '+%F %T') =====" >> "$LOG"
