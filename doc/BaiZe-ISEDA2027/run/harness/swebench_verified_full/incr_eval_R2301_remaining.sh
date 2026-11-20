#!/bin/bash
# R2301 remaining evals: claude-code (4) + pi (2) = 6 instances
# cline-patched (1) and codex (1) already completed.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
ENRICHED=$(pwd)/enriched_500.json
export EVAL_MAX_WORKERS=3
LOG=logs_glm53/incr_eval_R2301_remaining.log
exec >>"$LOG" 2>&1

echo "=== R2301 remaining START $(date) ==="

# merge_preds function
merge_preds() {
    local harness="$1"
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

# claude-code: 4 instances
merge_preds "claude-code"
echo "[$(date)] === claude-code eval START 4 instances ==="
sg docker -c "$PY -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions_glm53/predictions_claude-code.json \
  --dataset_name $ENRICHED \
  --split test \
  --instance_ids django__django-13569 django__django-13670 django__django-13741 django__django-13786 \
  --max_workers 3 \
  --run_id verified_full_glm53_claude-code_incr_R2301 \
  --timeout 1800" 2>&1
echo "[$(date)] === claude-code eval DONE ==="

# pi: 2 instances
merge_preds "pi"
echo "[$(date)] === pi eval START 2 instances ==="
sg docker -c "$PY -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions_glm53/predictions_pi.json \
  --dataset_name $ENRICHED \
  --split test \
  --instance_ids pydata__xarray-4687 pydata__xarray-4695 \
  --max_workers 3 \
  --run_id verified_full_glm53_pi_incr_R2301 \
  --timeout 1800" 2>&1
echo "[$(date)] === pi eval DONE ==="

echo "=== R2301 remaining DONE $(date) ==="
