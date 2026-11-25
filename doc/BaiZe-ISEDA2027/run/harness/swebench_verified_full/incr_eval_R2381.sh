#!/bin/bash
# R2381 incremental eval: 3 new unevaluated real-patch instances.
#   Delta at R2381 wake:
#     cline-patched:1 (django__django-13297)   [real patch, not yet eval'd]
#     claude-code:1  (django__django-14534)    [real patch, not yet eval'd]
#     pi:1            (sympy__sympy-18763)      [real patch, not yet eval'd]
#   Also cleaned 4 empty patches (1 codex + 3 cc) before this eval.
#   All other routes: backlog=0 (all real patches evaluated).
#   CPU guard: max_workers=3 (per 11-02 令; single proc >8000% => kill).
#   Hard constraint (运维令 10-28): NEVER commit result JSON.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
mkdir -p logs_glm53
LOG=logs_glm53/incr_eval_R2381.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2381 (3 new ids, 3 harnesses) START $(date) === (py=$PY)"

ENRICHED=$(pwd)/enriched_500.json
EVAL_MAX_WORKERS=3
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
    local run_id="verified_full_glm53_${harness}_incr_R2381"
    echo "[$(date)] === $harness eval START $(echo $ids | wc -w) NEW instances ==="
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

merge_preds "cline-patched"
eval_route "cline-patched" "django__django-13297"

merge_preds "claude-code"
eval_route "claude-code" "django__django-14534"

merge_preds "pi"
eval_route "pi" "sympy__sympy-18763"

echo "[$(date)] === merge R2381 results into eval_glm53_ ==="
$PY merge_R2381_glm53.py 2>&1

echo "=== incr_eval R2381 DONE $(date) ==="
