#!/bin/bash
# R2322 incremental eval: 5 new unevaluated real-patch instances.
#   Delta at R2322 wake:
#     cline-patched:1 (django__django-13121)     [real patch, not yet eval'd]
#     pi:4 (scikit-learn__scikit-learn-14496/14629/14710/14894)  [real patch, not yet eval'd]
#   All other routes: backlog=0 (all real patches evaluated).
#   gateway HTTP200 (predict advancing); eval does NOT need gateway.
#   CPU guard: max_workers=3 (per 11-02 令; single proc >8000% => kill).
#   Hard constraint (运维令 10-28): NEVER commit result JSON.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
mkdir -p logs_glm53
LOG=logs_glm53/incr_eval_R2322.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2322 (5 new ids, 2 harnesses) START $(date) === (py=$PY)"

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
    local run_id="verified_full_glm53_${harness}_incr_R2322"
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
eval_route "cline-patched" "django__django-13121"

merge_preds "pi"
eval_route "pi" "scikit-learn__scikit-learn-14496 scikit-learn__scikit-learn-14629 scikit-learn__scikit-learn-14710 scikit-learn__scikit-learn-14894"

echo "[$(date)] === merge R2322 results into eval_glm53_ ==="
$PY merge_R2322_glm53.py 2>&1

echo "=== incr_eval R2322 DONE $(date) ==="