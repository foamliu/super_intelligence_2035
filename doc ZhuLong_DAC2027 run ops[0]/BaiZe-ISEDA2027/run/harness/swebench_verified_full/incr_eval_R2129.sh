#!/bin/bash
# R2129 incremental eval: 4 missing instances across 3 routes.
#   cline-patched:1, pi:2, deepseek-harness:1
#   codex:0, opencode:0, claude-code:0, hermes:0 (fully evaluated, skipped)
# CPU guard: max_workers=4 to stay well under 80 cores.
# Hard constraint: NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs_glm53/incr_eval_R2129.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2129 START $(date) === (py=$PY)"

ENRICHED=$(pwd)/enriched_500.json
EVAL_MAX_WORKERS=4
export EVAL_MAX_WORKERS

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

eval_route() {
    local harness="$1"; shift
    local ids="$*"
    local run_id="verified_full_glm53_${harness}_incr_R2129"
    echo "[$(date)] === $harness eval START $(echo $ids | wc -w) instances ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions_glm53/predictions_${harness}.json \
      --dataset_name $ENRICHED \
      --split test \
      --instance_ids $ids \
      --max_workers $EVAL_MAX_WORKERS \
      --run_id $run_id \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# Route 1: cline-patched (1 missing)
merge_preds "cline-patched"
eval_route "cline-patched" "django__django-15037"

# Route 2: pi (2 missing)
merge_preds "pi"
eval_route "pi" "sympy__sympy-24213 sympy__sympy-24539"

# Route 3: deepseek-harness (1 missing)
merge_preds "deepseek-harness"
eval_route "deepseek-harness" "sympy__sympy-15976"

# Regenerate eval summaries
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R2129 DONE $(date) ==="
