#!/bin/bash
# R9 STAGE 2 — long training (selected tower) + scaling-law curve eval.
#   Purpose (R9.3 阶段二 + R9.4 scaling curve): after stage 1 picks the most
#   sample-efficient tower width, train that ONE tower for ~108,000 steps on the
#   full ~18.5M-pair multi-source data (CC12M + Amshaker), saving a checkpoint
#   every 10,000 steps (11 points incl. final), then measure IN-1k zero-shot /
#   linear-probe at every checkpoint to draw the scaling curve (log-x vs IN-1k lp).
#
# Usage:
#   bash r9_run_stage2.sh <width> [steps=108000] [num_workers=6]
#   e.g.  bash r9_run_stage2.sh 768          # selected tower (stage-1 winner)
#         bash r9_run_stage2.sh 1024 108000
#
# NOTE: kept as a SEPARATE file from r9_run.sh because r9_run.sh may be running
#       (bash reads scripts incrementally; editing a running script is risky).
#       This script also fixes the stage-1 `run_one` weakness: it DOES check the
#       training exit code, so a crash is logged loudly instead of silently
#       proceeding to eval with zero checkpoints.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

WIDTH="${1:?usage: bash r9_run_stage2.sh <width> [steps=108000] [num_workers=6]}"
STEPS="${2:-108000}"
NW="${3:-6}"

CC12M='/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar'
AMSH='/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar'
DATA="${CC12M},${AMSH}"
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
OUT="$OUTROOT/R9_stage2_w${WIDTH}"
LOG=/tmp/r9_stage2.log

# ---------------------------------------------------------------------------
# GPU + NFS contention checks (verbatim, for evidence discipline -> report)
# ---------------------------------------------------------------------------
echo "===== R9 STAGE2 START width=$WIDTH steps=$STEPS $(date '+%F %T') =====" > "$LOG"
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1
echo "----- NFS contention check (pretrain + data state, verbatim) -----" >> "$LOG"
echo "--- data agent hf download processes ---" >> "$LOG"
pgrep -af 'hf download|huggingface-cli download' >> "$LOG" 2>&1

# ---------------------------------------------------------------------------
# Long training (selected tower). Save a ckpt every 10k steps -> scaling curve.
# ---------------------------------------------------------------------------
echo "===== R9 stage2 openvision2 width=$WIDTH ($STEPS steps) START $(date '+%F %T') =====" >> "$LOG"
"$PY" -m torch.distributed.run --nproc_per_node=8 --nnodes=1 \
    --master_addr=$MASTER_ADDR --master_port=$((29400 + RANDOM % 1000)) \
    r9_train.py --tower openvision2 --width "$WIDTH" --depth 30 \
    --steps "$STEPS" --resolution 224 --patch 16 \
    --batch-size 64 --lr 3e-3 --warmup 20 --seed 1234 \
    --data "$DATA" --data-source wds --output-dir "$OUT" \
    --log-every 50 --probe-every 300 --probe-n 128 --num-workers "$NW" \
    --save-every 10000 \
    --eval-data "$EVAL" \
    >> "$LOG" 2>&1
rc=$?
echo "===== R9 stage2 openvision2 width=$WIDTH done (exit $rc) $(date '+%F %T') =====" >> "$LOG"

# ---------------------------------------------------------------------------
# Collect checkpoints for the scaling curve: vision_step*.pt (sorted by step)
# + final vision.pt (or vision_fused.pt if fused). Exit loudly if training
# produced nothing (crash protection, unlike stage-1's silent run_one).
# ---------------------------------------------------------------------------
CKPTS=()
if [ "$rc" -eq 0 ]; then
    while IFS= read -r f; do CKPTS+=("$f"); done < <(printf '%s\n' "$OUT"/vision_step*.pt 2>/dev/null | sort -V)
    FINAL="$OUT/vision.pt"
    [ -f "$FINAL" ] || FINAL="$OUT/vision_fused.pt"
    [ -f "$FINAL" ] && CKPTS+=("$FINAL")
fi

if [ "${#CKPTS[@]}" -eq 0 ]; then
    echo "===== R9 stage2 ERROR: zero checkpoints produced (train exit=$rc). NOT evaluating. =====" >> "$LOG"
    cat "$LOG"
    exit 1
fi

echo "===== R9 stage2 IN-1k eval on ${#CKPTS[@]} ckpts (scaling curve) =====" >> "$LOG"
printf 'ckpt list: %s\n' "${CKPTS[@]}" >> "$LOG"
"$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
echo "===== R9 stage2 ALL DONE $(date '+%F %T') =====" >> "$LOG"