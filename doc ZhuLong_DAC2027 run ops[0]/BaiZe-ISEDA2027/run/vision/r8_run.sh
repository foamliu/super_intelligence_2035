#!/bin/bash
# R8 — 6-architecture vision-encoder comparison at ~500-600M (the R5 winner recipe,
# fixed on the R7 data decision = Stanford GPIC `short`), then ImageNet-1k eval.
# Towers: openvision2, mambaeye, moevie, deepencoder_v2, aimv2, fastvithd.
# Recipe = R5 P0 / R7 B_gpic: 3000 steps @224/16 bs64=512 negatives,
#   frozen CLIP-768 text + InfoNCE + lr 3e-3 (warmup 20). Serial, 8 GPU TP1/DP8.
# After training, zero-shot + linear-probe IN-1k (r8_eval_in1k.py) on the self-split val.
# Usage: bash r8_run.sh [STEPS]   (default 3000; pass a small N for a smoke test)
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
STEPS="${1:-3000}"

GPIC='/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar'
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r8.log
CKPTS=()

echo "===== R8 START $(date '+%F %T') steps=$STEPS =====" > "$LOG"

echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

echo "----- NFS contention check (pretrain + data state, verbatim) -----" >> "$LOG"
grep -E '^- \*\*本唤醒推进' \
  /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md | head -1 >> "$LOG" 2>&1
echo "--- data agent hf download processes ---" >> "$LOG"
pgrep -af 'hf download|huggingface-cli download' >> "$LOG" 2>&1

run_one () {
    local TOWER="$1"
    local OUT="$OUTROOT/R8_${TOWER}"
    echo "===== R8 $TOWER ($STEPS steps @224/16 bs64 gpic) START $(date '+%F %T') =====" >> "$LOG"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
        r7_train.py --tower "$TOWER" --steps "$STEPS" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --data "$GPIC" --data-source gpic --output-dir "$OUT" \
        --log-every 50 --probe-every 300 --probe-n 128 --num-workers 2 \
        --eval-data "$EVAL" \
        >> "$LOG" 2>&1
    local rc=$?
    echo "===== R8 $TOWER done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
    if [ -f "$OUT/vision.pt" ]; then
        CKPTS+=("$OUT/vision.pt")
    elif [ -f "$OUT/vision_fused.pt" ]; then
        CKPTS+=("$OUT/vision_fused.pt")
    fi
}

for TOWER in openvision2 mambaeye moevie deepencoder_v2 aimv2 fastvithd; do
    run_one "$TOWER"
done

echo "===== R8 training done; IN-1k eval on ${#CKPTS[@]} checkpoints =====" >> "$LOG"
if [ "${#CKPTS[@]}" -gt 0 ]; then
    "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
fi

echo "===== R8 ALL DONE $(date '+%F %T') =====" >> "$LOG"