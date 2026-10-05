#!/bin/bash
# R12 — Full-data AIMv2-style run (GPIC + CC12M + Amshaker).
#   Operator instruction 2026-10-05 (evening): "用全部现有的数据训练（41% GPIC + 以前两个数据集）"
#   Recipe = AIMv2-style = ⑥-A / R11-G identical:
#     InfoNCE + 1.0×masked-patch-MSE (--loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0)
#     w512 (OpenVision2) + frozen CLIP-768.
#   ONLY change vs R11-G: data = ALL existing (GPIC all types + CC12M + Amshaker).
#
# Data (2026-10-05 evening):
#   GPIC     3305 tar × 12,639 pairs/tar ≈ 41.8M  (all caption_types, --caption-type all)
#   CC12M    1100 tar × 10,000 pairs/tar ≈ 11.0M
#   Amshaker 2250 tar ×  2,646 pairs/tar ≈  5.95M
#   Total unique ≈ 58.75M  (1 epoch ≈ 114,746 steps)
#
# Usage:
#   bash r12_run_fulldata_aimv2.sh [steps] [num_workers]
#   Default steps = 120000 (≈1.05 epoch, aligned to R11-G's 108k+ for scaling curve)
#   Throughput test: bash r12_run_fulldata_aimv2.sh 200 6
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
STEPS="${1:-120000}"
NW="${2:-6}"

GPIC='/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar'
CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${GPIC},${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r12_fulldata_aimv2.log

OUT="$OUTROOT/R12_fulldata_aimv2_w512"
echo "===== R12 full-data AIMv2 START steps=$STEPS $(date '+%F %T') =====" > "$LOG"
echo "----- hostname -----" >> "$LOG"
hostname >> "$LOG" 2>&1
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

# Count shards for the log
GPIC_N=$(ls $GPIC 2>/dev/null | wc -l)
CC12M_N=$(ls $CC12M 2>/dev/null | wc -l)
AMSH_N=$(ls $AMSH 2>/dev/null | wc -l)
echo "----- shard counts: GPIC=$GPIC_N CC12M=$CC12M_N Amshaker=$AMSH_N total=$((GPIC_N+CC12M_N+AMSH_N)) -----" >> "$LOG"

echo "===== R12 openvision2 width=512 loss=aimv2 mask=0.6 lambda=1.0 contrast=1.0 data=mixed caption_type=all ($STEPS steps, save-every 10000) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width 512 --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0 --contrast-weight 1.0 \
    --data "$DATA" --data-source mixed --caption-type all --output-dir "$OUT" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --save-every 10000 \
    --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== R12 training done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

# If steps > 1000, collect checkpoints and run IN-1k eval (scaling curve)
if [ "$STEPS" -gt 1000 ] && [ "$rc" -eq 0 ]; then
    CKPTS=()
    while IFS= read -r f; do CKPTS+=("$f"); done < <(printf '%s\n' "$OUT"/vision_step*.pt 2>/dev/null | sort -V)
    FINAL="$OUT/vision.pt"
    [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL")

    if [ "${#CKPTS[@]}" -eq 0 ]; then
        echo "===== R12 ERROR: zero checkpoints produced. NOT evaluating. =====" >> "$LOG"
        cat "$LOG"
        exit 1
    fi

    echo "===== R12 IN-1k eval on ${#CKPTS[@]} ckpts (scaling curve) =====" >> "$LOG"
    printf 'ckpt list: %s\n' "${CKPTS[@]}" >> "$LOG"
    "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
    echo "===== R12 ALL DONE $(date '+%F %T') =====" >> "$LOG"
else
    echo "===== R12 throughput test (steps=$STEPS ≤ 1000, skipping eval) ALL DONE $(date '+%F %T') =====" >> "$LOG"
fi
