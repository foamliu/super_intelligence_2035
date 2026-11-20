#!/bin/bash
# R2146 incremental eval: 5 truly-new unevaluated real-patch instances across 2 routes.
#   Computed by delta (real_patch_ids - evaluated_set) at R2146 wake:
#     opencode:2   (pytest-dev__pytest-10051, pytest-dev__pytest-10081)
#     hermes:3     (django__django-16661, django__django-16877, django__django-17087)
#   cline-patched:0, codex:0, claude-code:0, pi:0, deepseek-harness:0 (fully evaluated -> skipped)
# GATEWAY 429 (quota exhausted) -> predict stalled; eval does NOT need gateway.
# CPU guard: max_workers=4. Hard constraint (运维令 10-28): NEVER commit result JSON.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
mkdir -p logs_glm53
LOG=logs_glm53/incr_eval_R2146.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2146 (5 new ids) START $(date) === (py=$PY)"

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
    local run_id="verified_full_glm53_${harness}_incr_R2146"
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

merge_preds "opencode"
eval_route "opencode" "pytest-dev__pytest-10051 pytest-dev__pytest-10081"

merge_preds "hermes"
eval_route "hermes" "django__django-16661 django__django-16877 django__django-17087"

echo "[$(date)] === merge R2146 results into eval_glm53_ ==="
$PY merge_R2146_glm53.py 2>&1

echo "=== incr_eval R2146 DONE $(date) ==="
