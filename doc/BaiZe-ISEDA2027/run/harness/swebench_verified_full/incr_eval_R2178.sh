#!/bin/bash
# R2178 incremental eval: 7 truly-new unevaluated real-patch instances across 3 harnesses.
#   Delta at R2178 wake (real_patch_ids - eval_glm53_* evaluated set), all confirmed NOT
#   in-flight (active run_single at wake: django-11141/12143/13033/15280, xarray-4075,
#   sklearn-14629 -- none of the 7 delta ids is in-flight):
#     cline-patched:1 (pydata__xarray-3993)      [completed since R2177, not yet eval'd]
#     opencode:4 (django__django-12209/12262/12276/12406) [completed since R2177]
#     hermes:2 (scikit-learn__scikit-learn-10297/10844)    [completed since R2177]
#   codex/claude-code/pi/dsh: delta=0 (all real patches already evaluated).
#   gateway HTTP200 (predict advancing); eval does NOT need gateway.
#   CPU guard: max_workers=3 (per 11-02 令; single proc >8000% => kill).
#   Hard constraint (运维令 10-28): NEVER commit result JSON.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
mkdir -p logs_glm53
LOG=logs_glm53/incr_eval_R2178.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2178 (7 new ids, 3 harnesses) START $(date) === (py=$PY)"

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
    local run_id="verified_full_glm53_${harness}_incr_R2178"
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
eval_route "cline-patched" "pydata__xarray-3993"

merge_preds "opencode"
eval_route "opencode" "django__django-12209 django__django-12262 django__django-12276 django__django-12406"

merge_preds "hermes"
eval_route "hermes" "scikit-learn__scikit-learn-10297 scikit-learn__scikit-learn-10844"

echo "[$(date)] === merge R2178 results into eval_glm53_ ==="
$PY merge_R2178_glm53.py 2>&1

echo "=== incr_eval R2178 DONE $(date) ==="
