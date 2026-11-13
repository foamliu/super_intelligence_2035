#!/bin/bash
# R2384 incremental eval: 3 backlog items (found by backlog scan after R2383).
#   cline-patched: django__django-13513, django__django-13551  [2 new predictions]
#   pi:            sympy__sympy-19346                            [1 new prediction]
# Also cleaned 4 empty patches: codex__django-13297, cc__django-14771/14787/15098
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# CPU self-check PASSED (运维令 11-02): load 30/224 ~13% busy, no this-line proc >8000% CPU.
# Memory self-check PASSED (运维令 10-30): no this-line proc >50GB.
# Guardrails: OMP_NUM_THREADS=8, EVAL_MAX_WORKERS=1 (prevent sklearn n_jobs CPU spiral).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs_glm53/incr_eval_R2384.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2384 START $(date) === (py=$PY)"

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
for f in sorted(glob.glob(f'{R}/predictions_glm53/${harness}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions_glm53/predictions_${harness}.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'${harness}: {len(all_preds)} real patches merged')
"
}

eval_ids() {
    local harness="$1"; shift
    local ids="$*"
    echo "[$(date)] === $harness eval START $(echo $ids | wc -w) new instances ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions_glm53/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 1 \
      --run_id verified_full_glm53_${harness}_incr_R2384 \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# Step 1: cline-patched — merge + eval django-13513, django-13551.
merge_preds "cline-patched"
eval_ids "cline-patched" "django__django-13513 django__django-13551"

# Step 2: pi — merge + eval sympy-19346.
merge_preds "pi"
eval_ids "pi" "sympy__sympy-19346"

echo "=== incr_eval R2384 ALL DONE $(date) ==="
