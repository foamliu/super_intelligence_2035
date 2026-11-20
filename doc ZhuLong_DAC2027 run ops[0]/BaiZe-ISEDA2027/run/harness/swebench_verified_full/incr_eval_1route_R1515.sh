#!/bin/bash
# R1515 incremental eval: 1 NEW real patch (found by scan_backlog.py after R1514).
#   deepseek-harness : django__django-16612 (patch_len=2201)
# Single route -> no container collision.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# CPU self-check PASSED (运维令 11-02): load 35.56/224 ~16% busy, no this-line proc >8000% CPU.
# Memory self-check PASSED (运维令 10-30): avail ~1.35Ti, no this-line proc >50GB.
# Guardrails: OMP_NUM_THREADS=8, EVAL_MAX_WORKERS=1 (prevent sklearn n_jobs CPU spiral).
# NOTE: use setsid to fully detach (R1083 lesson).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_1route_R1515.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_1route R1515 START $(date) === (py=$PY)"

export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export MKL_NUM_THREADS=8
export EVAL_MAX_WORKERS=1

merge_preds() {
    local harness="$1"
    echo "[$(date)] === merge $harness predictions ==="
    $PY -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions/${harness}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions/predictions_${harness}.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'${harness}: {len(all_preds)} real patches merged')
"
}

eval_ids() {
    local harness="$1"; shift
    local ids="$*"
    echo "[$(date)] === $harness eval START $(echo $ids | wc -w) new instances ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 1 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# Step 1: deepseek-harness — merge + eval django-16612.
merge_preds "deepseek-harness"
eval_ids "deepseek-harness" "django__django-16612"

# Step 2: regen summaries.
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "=== incr_eval_1route R1515 DONE $(date) ==="
