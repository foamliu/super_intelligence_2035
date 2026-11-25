#!/bin/bash
# ==============================================================================
# run_probe_x5.sh — ② Stronger probe comparison on E1fair checkpoint
#
# Operator instruction 2026-10-10 ②:
#   "Same checkpoint, add: k-NN probe · longer probe steps (×5=450ep) · wd/LR sweep"
#   Purpose: separate "features are bad" vs "probe is underfitting"
#
# k-NN already done (k=20 → 37.68%). This script runs the REMAINING arms:
#   1. Protocol B ×5 epochs (450 instead of 90) — tests probe underfitting
#   2. wd/LR micro-sweep — tests if different hyperparams raise lp
#
# Checkpoint: E1fair vision.pt (w512/d30, 126.8M, 1-epoch, ProtB=62.34±0.01%)
#
# Launch (after V3 eval completes, GPU free):
#   setsid bash run_probe_x5.sh > /tmp/probe_x5.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

E1FAIR_CKPT=/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E1fair_ov2_w512_d30_p16_224/vision.pt
LOG=/tmp/probe_x5.log

echo "===== ② ×5 probe START $(date '+%F %T') =====" | tee "$LOG"
echo "[②] checkpoint=$E1FAIR_CKPT" >> "$LOG"

if [ ! -f "$E1FAIR_CKPT" ]; then
    echo "[②] 🚫 E1fair checkpoint not found! Aborting." | tee -a "$LOG"
    exit 1
fi

# Run probe_comparison_eval.py (handles ×5 epochs + wd/LR sweep internally)
"$PY" probe_comparison_eval.py --ckpt "$E1FAIR_CKPT" --probe-only >> "$LOG" 2>&1

rc=$?
echo "===== ② ×5 probe done (exit $rc) $(date '+%F %T') =====" >> "$LOG"
echo "" >> "$LOG"
echo "--- Key results ---" >> "$LOG"
grep -E 'lp_top1|ProtB|×5|450ep|wd|LR|sweep|underfit' "$LOG" 2>/dev/null | tail -30 >> "$LOG"
exit $rc
