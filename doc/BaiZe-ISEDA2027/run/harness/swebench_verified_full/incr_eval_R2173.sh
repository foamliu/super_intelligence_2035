#!/bin/bash
# R2173 incremental eval: 1 truly-new unevaluated real-patch instance.
#   Delta at R2173 wake (real_patch_ids - eval_glm53_* evaluated set):
#     claude-code:1 (sympy__sympy-20801)  [patch final, no active run_single]
#   codex django__django-11999 EXCLUDED (in-flight re-predict PID1908399, race risk).
#   cline-patched/codex(above)/opencode/pi/hermes/deepseek-harness: 0 new (caught up).
# gw_proxy 9092/9093 UP; eval does NOT need gateway. CPU guard: max_workers=3.
# Hard constraint (运维令 10-28): NEVER commit result JSON.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
mkdir -p logs_glm53
LOG=logs_glm53/incr_eval_R2173.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2173 (1 new id) START $(date) === (py=$PY)"

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
    local run_id="verified_full_glm53_${harness}_incr_R2173"
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
eval_route "claude-code" "sympy__sympy-20801"

echo "[$(date)] === merge R2173 results into eval_glm53_ ==="
$PY merge_R2173_glm53.py 2>&1

echo "=== incr_eval R2173 DONE $(date) ==="
