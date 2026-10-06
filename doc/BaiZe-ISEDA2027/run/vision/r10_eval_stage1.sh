#!/bin/bash
# R10-① — recover stage-1 PERIODIC ckpts' IN-1k (no re-training; reuse cached ckpts only).
#   3 towers (w512/768/1024) x step{10000,20000,30000} + per-arm final = 12 ckpts.
#   Uses existing vision/r8_eval_in1k.py --ckpts (decodes IN-1k once, reuses across ckpts).
#   ~0.7h GPU (single GPU, frozen trunk zero-shot + linear-probe).
# Usage:
#   bash r10_eval_stage1.sh
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
export TOKENIZERS_PARALLELISM=false

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
LOG=/tmp/r10_stage1_in1k.log

echo "===== R10 stage1 periodic-ckpt IN-1k START $(date '+%F %T') =====" > "$LOG"

echo "----- GPU exclusivity check (verbatim) -----" >> "$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >> "$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >> "$LOG" 2>&1

echo "----- NFS contention check (pretrain/data state, verbatim) -----" >> "$LOG"
echo "--- pretrain WAITING/PHASE ---" >> "$LOG"
grep -m1 '^WAITING' /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md >> "$LOG" 2>&1
grep -m1 'PHASE' /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md >> "$LOG" 2>&1
echo "--- hf download processes (network heavy) ---" >> "$LOG"
pgrep -af 'hf download|huggingface-cli download' >> "$LOG" 2>&1 || echo '(none)' >> "$LOG"

CKPTS=()
for W in 512 768 1024; do
    D="$OUTROOT/R9_stage1_w${W}"
    for f in "$D"/vision_step10000.pt "$D"/vision_step20000.pt "$D"/vision_step30000.pt "$D"/vision.pt; do
        [ -f "$f" ] && CKPTS+=("$f") || echo "[skip missing] $f" >> "$LOG"
    done
done

echo "----- ckpt list (${#CKPTS[@]}) -----" >> "$LOG"
printf 'ckpt: %s\n' "${CKPTS[@]}" >> "$LOG"

if [ "${#CKPTS[@]}" -eq 0 ]; then
    echo "===== R10 stage1 ERROR: zero ckpts found. NOT evaluating. =====" >> "$LOG"
    cat "$LOG"
    exit 1
fi

"$PY" r8_eval_in1k.py --ckpts "${CKPTS[@]}" >> "$LOG" 2>&1
rc=$?
echo "===== R10 stage1 periodic-ckpt IN-1k DONE (exit $rc) $(date '+%F %T') =====" >> "$LOG"
exit $rc