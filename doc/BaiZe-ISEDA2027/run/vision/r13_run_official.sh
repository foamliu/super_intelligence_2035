#!/bin/bash
# R13 — OpenVision2 OFFICIAL weights (L/14 @224) IN-1k evaluation.
# Loads official patch14/d24 vision encoder (HF UCSC-VLAA/openvision2-vit-large-patch14-224-vision-only,
# Apache-2.0) and evaluates IN-1k (frozen-trunk lp + zero-shot-with-caveat) with the SAME
# protocol as our from-scratch towers. PURE EVAL (no training). Operator-approved 2026-10-04 (五).
#
# Usage:
#   bash r13_run_official.sh            # full IN-1k eval (single GPU)
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export TOKENIZERS_PARALLELISM=false
export HF_HOME=/nas_train/app.e0031982/.cache

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/r13_official.log

echo "===== R13 OFFICIAL OpenVision2 L/14 IN-1k eval START $(date '+%F %T') =====" > "$LOG"
echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

"$PY" r13_eval_official.py >> "$LOG" 2>&1
echo "===== R13 OFFICIAL ALL DONE (exit $?) $(date '+%F %T') =====" >> "$LOG"