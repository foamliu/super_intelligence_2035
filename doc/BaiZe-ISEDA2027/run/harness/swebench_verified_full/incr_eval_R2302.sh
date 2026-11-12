#!/bin/bash
# R2302 incremental eval: 3 truly-new unevaluated real-patch instances across 2 harnesses.
#   Delta at R2302 wake (real_patch_ids - eval_glm53_* evaluated set), after cleanup of 18
#   empty patches (codex 8, cc 8, hermes 2 -- all 429/gateway empties):
#     claude-code:1 (scikit-learn__scikit-learn-15100)   [real patch, not yet eval'd]
#     hermes:2 (django__django-14631, django__django-14725) [real patches, not yet eval'd]
#   cline-patched/codex/pi/opencode/deepseek-harness: backlog=0 (all real patches evaluated).
#   gateway HTTP200 (predict advancing); eval does NOT need gateway.
#   CPU guard: max_workers=3 (per 11-02 令; single proc >8000% => kill).
#   Hard constraint (运维令 10-28): NEVER commit result JSON.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
mkdir -p logs_glm53
LOG=logs_glm53/incr_eval_R2302.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2302 (3 new ids, 2 harnesses) START $(date) === (py=$PY)"

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
    local run_id="verified_full_glm53_${harness}_incr_R2302"
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

merge_preds "claude-code"
eval_route "claude-code" "scikit-learn__scikit-learn-15100"

merge_preds "hermes"
eval_route "hermes" "django__django-14631 django__django-14725"

echo "[$(date)] === merge R2302 results into eval_glm53_ ==="
$PY merge_R2302_glm53.py 2>&1

echo "=== incr_eval R2302 DONE $(date) ==="
