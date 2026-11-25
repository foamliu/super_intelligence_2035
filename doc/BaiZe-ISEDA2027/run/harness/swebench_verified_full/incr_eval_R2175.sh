#!/bin/bash
# R2175 incremental eval: 5 truly-new unevaluated real-patch instances across 4 harnesses.
#   Delta at R2175 wake (real_patch_ids - eval_glm53_* evaluated set), all confirmed
#   NOT in-flight (active run_single at wake: cline=xarray-3305 / hermes=pytest-8399 /
#   pi=django-13028 / codex=django-12125 -- none of the 5 below):
#     cline-patched:1 (pydata__xarray-3095)   [was in-flight R2174, now complete]
#     codex:2 (django__django-12039, django__django-12050)  [12050 was in-flight R2174]
#     pi:1 (django__django-13023)              [new 14:25:58]
#     hermes:1 (pytest-dev__pytest-7982)       [new 14:24:11]
#   gateway HTTP200 (predict advancing); eval does NOT need gateway.
#   CPU guard: max_workers=3 (per 11-02 令; single proc >8000% => kill).
#   Hard constraint (运维令 10-28): NEVER commit result JSON.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
mkdir -p logs_glm53
LOG=logs_glm53/incr_eval_R2175.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2175 (5 new ids, 4 harnesses) START $(date) === (py=$PY)"

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
    local run_id="verified_full_glm53_${harness}_incr_R2175"
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
eval_route "cline-patched" "pydata__xarray-3095"

merge_preds "codex"
eval_route "codex" "django__django-12039" "django__django-12050"

merge_preds "pi"
eval_route "pi" "django__django-13023"

merge_preds "hermes"
eval_route "hermes" "pytest-dev__pytest-7982"

echo "[$(date)] === merge R2175 results into eval_glm53_ ==="
$PY merge_R2175_glm53.py 2>&1

echo "=== incr_eval R2175 DONE $(date) ==="
