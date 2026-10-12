#!/bin/bash
# rerun_e4_eval.sh — Re-run ④-2ep eval after sympy fix (2026-10-12)
# All 4 evals failed due to broken editable sympy install; now fixed with sympy 1.14.0
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
E4_CKPT=/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_2ep_ov2_w512_d30_p16_224/vision.pt
LOG=/tmp/e4_2ep_eval_rerun.log

echo "[$(date '+%F %T')] ===== ④-2ep EVAL RERUN (sympy fixed) =====" | tee "$LOG"
echo "[$(date '+%F %T')] Checkpoint: $E4_CKPT" | tee -a "$LOG"

# 1. Protocol B (3 seeds)
echo "[$(date '+%F %T')] --- Protocol B (3 seeds, full train) ---" | tee -a "$LOG"
"$PY" lp_protocol_bridge.py --ckpts "$E4_CKPT" --protocol B --probe-full-train >> "$LOG" 2>&1
echo "[$(date '+%F %T')] Protocol B done (rc=$?)" | tee -a "$LOG"

# 2. Protocol A
echo "[$(date '+%F %T')] --- Protocol A ---" | tee -a "$LOG"
"$PY" lp_protocol_bridge.py --ckpts "$E4_CKPT" --protocol A >> "$LOG" 2>&1
echo "[$(date '+%F %T')] Protocol A done (rc=$?)" | tee -a "$LOG"

# 3. Zero-shot
echo "[$(date '+%F %T')] --- Zero-shot ---" | tee -a "$LOG"
"$PY" zeroshot_in1k_eval.py --ckpt "$E4_CKPT" >> "$LOG" 2>&1
echo "[$(date '+%F %T')] Zero-shot done (rc=$?)" | tee -a "$LOG"

# 4. k-NN probe
echo "[$(date '+%F %T')] --- k-NN ---" | tee -a "$LOG"
"$PY" probe_comparison_eval.py --ckpt "$E4_CKPT" --knn-only >> "$LOG" 2>&1
echo "[$(date '+%F %T')] k-NN done (rc=$?)" | tee -a "$LOG"

echo "[$(date '+%F %T')] ===== ④-2ep EVAL RERUN DONE =====" | tee -a "$LOG"
