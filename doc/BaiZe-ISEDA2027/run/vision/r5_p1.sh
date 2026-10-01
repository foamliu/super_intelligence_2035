#!/bin/bash
# R5 P1 — resolution comparison for the P0 WINNING architecture, fixed recipe.
#   WINNER x {224/16, 336/14, 448/14} x 3000 steps. Batch-matched: all at bs=16/rank
#   (128 negatives) because 448/14 = 1024 tokens cannot fit bs>16 without grad-ckpt
#   (R2 empirical: 441-token already ~37GB @bs32); 224/16 & 336/14 also run at bs=16
#   for comparability. Fixed recipe: frozen CLIP text(768) + InfoNCE + head->768 + lr 3e-3.
# Usage: bash r5_p1.sh <winner-arch>
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

TOWER="${1:-openvision2}"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
DATA='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r5_p1.log

echo "===== R5 P1 ($TOWER resolution sweep) START $(date '+%F %T') =====" > "$LOG"
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1

run_one () {
    local RES="$1" P="$2"
    local OUT="$OUTROOT/R5_P1_${TOWER}_r${RES}_p${P}"
    echo "===== R5 P1 ${TOWER} r${RES}/p${P} (3000 steps, bs16) START $(date '+%F %T') =====" >> "$LOG"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
        r5_train.py --tower "$TOWER" --steps 3000 --resolution "$RES" --patch "$P" \
        --batch-size 16 --lr 3e-3 --warmup 20 --seed 1234 \
        --data "$DATA" --eval-data "$EVAL" --output-dir "$OUT" \
        --log-every 50 --probe-every 300 --probe-n 128 --num-workers 2 \
        >> "$LOG" 2>&1
    echo "===== R5 P1 ${TOWER} r${RES}/p${P} done (exit $?) $(date '+%F %T') =====" >> "$LOG"
}

run_one 224 16
run_one 336 14
run_one 448 14

echo "===== R5 P1 ALL DONE $(date '+%F %T') =====" >> "$LOG"