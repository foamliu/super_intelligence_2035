#!/bin/bash
# R5 P0 — architecture comparison under the FIXED recipe (R4-validated, C1-C4 passed).
#   4 architectures x 3000 steps @ anchor 224/16, 8 GPU (TP1/DP8), batch-matched (bs=64/rank = 512 negatives).
#   Fixed recipe: frozen CLIP text tower (768) + CLIP InfoNCE + vision head -> 768 + lr 3e-3 (warmup 20).
# Serial execution (each run uses all 8 GPUs). Run ON 10.239.2.12 (GPU 0-7).
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
DATA='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r5_p0.log

echo "===== R5 P0 START $(date '+%F %T') =====" > "$LOG"

# GPU exclusivity check (verbatim, for the report)
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

# NFS contention check (pretrain on 10.239.2.29 shares /nas_train)
echo "----- pretrain task state (NFS contention check, verbatim head) -----" >> "$LOG"
grep -E '^\- \*\*本唤醒推进' /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md | head -2 >> "$LOG" 2>&1

run_one () {
    local TOWER="$1"
    local OUT="$OUTROOT/R5_P0_$TOWER"
    echo "===== R5 P0 $TOWER (3000 steps @224/16 bs64) START $(date '+%F %T') =====" >> "$LOG"
    "$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
        --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
        r5_train.py --tower "$TOWER" --steps 3000 --resolution 224 --patch 16 \
        --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
        --data "$DATA" --eval-data "$EVAL" --output-dir "$OUT" \
        --log-every 50 --probe-every 300 --probe-n 128 --num-workers 2 \
        >> "$LOG" 2>&1
    echo "===== R5 P0 $TOWER done (exit $?) $(date '+%F %T') =====" >> "$LOG"
}

# fastest-first ordering (each run serial, all 8 GPUs)
run_one openvision2
run_one deepencoder_v2
run_one mambaeye
run_one moevie

echo "===== R5 P0 ALL DONE $(date '+%F %T') =====" >> "$LOG"