#!/bin/bash
# R2140 incremental eval: ONLY 10 truly-new unevaluated instances across 4 routes.
#   Computed by /tmp/compute_eval_delta_R2140.py (real_patch_ids - evaluated_set):
#     opencode:3  (django-13112, django-13401, django-13406)
#     pi:5        (astropy-14182, astropy-14369, astropy-14598, astropy-7671, astropy-8872)
#     hermes:1    (django-14608)
#     deepseek-harness:1 (sympy-19346)
#   claude-code:0, cline-patched:0, codex:0 (fully evaluated -> skipped)
# NOTE: first launch used a round-suffixed run_id with ALL ids -> swebench re-evald
#   everything (no cache under new run_id). Fixed: pass ONLY the new instance_ids.
# CPU guard: max_workers=4. Hard constraint (运维令 10-28): NEVER commit result JSON.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
mkdir -p logs_glm53
LOG=logs_glm53/incr_eval_R2140.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2140 (fixed: 10 new ids) START $(date) === (py=$PY)"

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
    local run_id="verified_full_glm53_${harness}_incr_R2140"
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
eval_route "opencode" "django__django-13112 django__django-13401 django__django-13406"

merge_preds "pi"
eval_route "pi" "astropy__astropy-14182 astropy__astropy-14369 astropy__astropy-14598 astropy__astropy-7671 astropy__astropy-8872"

merge_preds "hermes"
eval_route "hermes" "django__django-14608"

merge_preds "deepseek-harness"
eval_route "deepseek-harness" "sympy__sympy-19346"

echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R2140 (fixed) DONE $(date) ==="
