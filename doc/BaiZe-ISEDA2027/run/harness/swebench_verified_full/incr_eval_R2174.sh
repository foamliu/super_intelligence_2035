#!/bin/bash
# R2174 incremental eval: 21 truly-new unevaluated real-patch instances across 7 harnesses.
#   Delta at R2174 wake (real_patch_ids - eval_glm53_* evaluated set), all confirmed
#   NOT in-flight (active run_single = django-12039codex/django-13012pi/xarray-3095cline/pytest-7571hermes):
#     cline-patched:1 (matplotlib-23314)
#     codex:1 (django-11999)  [was excluded R2173 as in-flight; now safe]
#     opencode:2 (sympy-24066, sympy-24213)
#     claude-code:2 (matplotlib-20488, matplotlib-20859)
#     pi:1 (sympy-23824)
#     hermes:2 (pytest-7490, pytest-7521)
#     deepseek-harness:12 (sympy-16886,17318,19637,19954,20154,23534,23824,24066,24213,24539,24562,24661)
#   gateway RECOVERED HTTP200 (predict advancing); eval does NOT need gateway.
#   CPU guard: max_workers=3 (per 11-02 令; single proc >8000% => kill).
#   Hard constraint (运维令 10-28): NEVER commit result JSON.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
mkdir -p logs_glm53
LOG=logs_glm53/incr_eval_R2174.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R2174 (21 new ids, 7 harnesses) START $(date) === (py=$PY)"

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
    local run_id="verified_full_glm53_${harness}_incr_R2174"
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
eval_route "cline-patched" "matplotlib__matplotlib-23314"

merge_preds "codex"
eval_route "codex" "django__django-11999"

merge_preds "opencode"
eval_route "opencode" "sympy__sympy-24066" "sympy__sympy-24213"

merge_preds "claude-code"
eval_route "claude-code" "matplotlib__matplotlib-20488" "matplotlib__matplotlib-20859"

merge_preds "pi"
eval_route "pi" "sympy__sympy-23824"

merge_preds "hermes"
eval_route "hermes" "pytest-dev__pytest-7490" "pytest-dev__pytest-7521"

merge_preds "deepseek-harness"
eval_route "deepseek-harness" "sympy__sympy-16886" "sympy__sympy-17318" "sympy__sympy-19637" "sympy__sympy-19954" "sympy__sympy-20154" "sympy__sympy-23534" "sympy__sympy-23824" "sympy__sympy-24066" "sympy__sympy-24213" "sympy__sympy-24539" "sympy__sympy-24562" "sympy__sympy-24661"

echo "[$(date)] === merge R2174 results into eval_glm53_ ==="
$PY merge_R2174_glm53.py 2>&1

echo "=== incr_eval R2174 DONE $(date) ==="