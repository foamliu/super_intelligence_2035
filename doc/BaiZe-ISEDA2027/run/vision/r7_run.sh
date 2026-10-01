#!/bin/bash
# R7 — data-arm comparison (winner arch OpenVision2, fixed R5 recipe, only data differs).
#   Arm C' = CC12M webdataset (short captions, ~11M pairs)  [data-source=wds]
#   Arm B  = Stanford GPIC `short` (20 tok / 0% truncation)  [data-source=gpic]
#   Arm A  = en500k (LLaVA recaption) ~ REUSED from R5 P0 (no re-run).
# Same recipe as R5 P0: OpenVision2 x 3000 steps @224/16 bs64=512 negatives,
#   frozen CLIP-768 text + InfoNCE + lr 3e-3 (warmup 20). Serial, 8 GPU TP1/DP8.
# Usage: bash r7_run.sh [STEPS]   (default 3000; pass a small N for a smoke test)
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
STEPS="${1:-3000}"

CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
GPIC='/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar'
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r7.log

echo "===== R7 START $(date '+%F %T') steps=$STEPS =====" > "$LOG"

echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

echo "----- NFS contention check (pretrain + data state, verbatim) -----" >> "$LOG"
grep -E '^- \*\*本唤醒推进' /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md | head -1 >> "$LOG" 2>&1
echo "--- data agent hf download processes ---" >> "$LOG"
pgrep -af 'hf download|huggingface-cli download' >> "$LOG" 2>&1

run_one () {
    local TAG="$1"; local SRC="$2"; local DS="$3"; local OUT="$4"
    echo "===== R7 $TAG ($STEPS steps @224/16 bs64) START $(date '+%F %T') =====" >> "$LOG"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
        r7_train.py --tower openvision2 --steps "$STEPS" --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --data "$SRC" --data-source "$DS" --output-dir "$OUT" \
        --log-every 50 --probe-every 300 --probe-n 128 --num-workers 2 \
        --eval-data "$EVAL" \
        >> "$LOG" 2>&1
    echo "===== R7 $TAG done (exit $?) $(date '+%F %T') =====" >> "$LOG"
}

# Arm C' = CC12M (webdataset, --data-source wds)
run_one C_cc12m "$CC12M" wds "$OUTROOT/R7_C_cc12m"
# Arm B = GPIC short (GPIC tar json, --data-source gpic)
run_one B_gpic "$GPIC" gpic "$OUTROOT/R7_B_gpic"

echo "===== R7 ALL DONE $(date '+%F %T') =====" >> "$LOG"