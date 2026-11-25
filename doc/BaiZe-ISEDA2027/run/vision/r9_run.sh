#!/bin/bash
# R9 — data scale-up + long training. Stage 1 first = "shrink-tower pilot" (R9.3 阶段一).
#   Tower: OpenVision2 @ width {512,768,1024} (depth 30) = ~126M / ~284M / 505M.
#   Data: CC12M (wds) + Amshaker (wds) combined multi-source (NO re-packing; both are
#         already webdataset .jpg/.txt shards, verified on disk).
#   Recipe (unchanged from R8): frozen CLIP-768 text + InfoNCE + lr 3e-3 (warmup 20),
#         @224/16 bs64 x 8 GPU = 512 negatives. Serial TP1/DP8.
# Usage:
#   bash r9_run.sh smoke 100        # per-scale img/s for R9.0 ETA estimation
#   bash r9_run.sh stage1 30000     # full shrink-tower pilot + IN-1k eval
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
MODE="${1:-stage1}"
STEPS="${2:-30000}"
NW="${3:-6}"   # 6 relieves the CC12M+Amshaker data-loading bottleneck
               # (smoke: w1024 2084 img/s @nw2 -> 2827 img/s @nw6)

CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r9.log

echo "===== R9 START mode=$MODE steps=$STEPS $(date '+%F %T') =====" > "$LOG"

echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

echo "----- NFS contention check (pretrain + data state, verbatim) -----" >> "$LOG"
grep -E '^- \*\*本唤醒推进' \
  /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md | head -1 >> "$LOG" 2>&1
echo "--- data agent hf download processes ---" >> "$LOG"
pgrep -af 'hf download|huggingface-cli download' >> "$LOG" 2>&1

run_one () {
    local W="$1"; local OUT="$2"
    echo "===== R9 openvision2 width=$W ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
        r9_train.py --tower openvision2 --width "$W" --depth 30 \
        --steps "$STEPS" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --data "$DATA" --data-source wds --output-dir "$OUT" \
        --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
        --eval-data "$EVAL" \
        >> "$LOG" 2>&1
    echo "===== R9 openvision2 width=$W done (exit $?) $(date '+%F %T') =====" >> "$LOG"
}

case "$MODE" in
  smoke)
    for W in 512 768 1024; do
        run_one "$W" "$OUTROOT/R9_smoke_w${W}"
    done
    ;;
  stage1)
    CKPTS=()
    for W in 512 768 1024; do
        run_one "$W" "$OUTROOT/R9_stage1_w${W}"
        C="$OUTROOT/R9_stage1_w${W}/vision.pt"
        [ -f "$C" ] || C="$OUTROOT/R9_stage1_w${W}/vision_fused.pt"
        [ -f "$C" ] && CKPTS+=("$C")
    done
    echo "===== R9 stage1 training done; IN-1k eval on ${#CKPTS[@]} ckpts =====" >> "$LOG"
    if [ "${#CKPTS[@]}" -gt 0 ]; then
        "$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
    fi
    ;;
esac

echo "===== R9 ALL DONE ($MODE) $(date '+%F %T') =====" >> "$LOG"