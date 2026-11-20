#!/bin/bash
# R2125 incremental eval: 28 missing instances across 6 routes.
#   codex:3, opencode:11, claude-code:5, pi:3, hermes:2, deepseek-harness:4
# cline-patched: 0 missing (fully evaluated).
# CPU guard: max_workers=4 to stay well under 80 cores.
# Hard constraint: NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs_glm53/incr_eval_R2125.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2125 START $(date) === (py=$PY)"

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
    local run_id="verified_full_glm53_${harness}_incr_R2125"
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

# Route 1: codex (3 missing)
merge_preds "codex"
eval_route "codex" "scikit-learn__scikit-learn-11578 scikit-learn__scikit-learn-12585 scikit-learn__scikit-learn-12682"

# Route 2: opencode (11 missing)
merge_preds "opencode"
eval_route "opencode" "sympy__sympy-19637 sympy__sympy-19783 sympy__sympy-19954 sympy__sympy-20154 sympy__sympy-20428 sympy__sympy-20438 sympy__sympy-20590 sympy__sympy-20801 sympy__sympy-21379 sympy__sympy-21596 sympy__sympy-21847"

# Route 3: claude-code (5 missing)
merge_preds "claude-code"
eval_route "claude-code" "django__django-15731 django__django-15851 django__django-15863 django__django-15916 django__django-15957"

# Route 4: pi (3 missing)
merge_preds "pi"
eval_route "pi" "sympy__sympy-21596 sympy__sympy-21847 sympy__sympy-21930"

# Route 5: hermes (2 missing - patch apply failed, retry)
merge_preds "hermes"
eval_route "hermes" "django__django-14631 django__django-14725"

# Route 6: deepseek-harness (4 missing)
merge_preds "deepseek-harness"
eval_route "deepseek-harness" "sympy__sympy-14976 sympy__sympy-15017 sympy__sympy-15345 sympy__sympy-15349"

# Regenerate eval summaries
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R2125 DONE $(date) ==="
