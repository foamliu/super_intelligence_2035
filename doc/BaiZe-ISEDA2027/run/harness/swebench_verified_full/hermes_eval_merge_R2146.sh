#!/bin/bash
# R2146b: hermes eval (3 instances) + merge (opencode 2 already evaluated).
# Re-launch after R2146 process group was killed before hermes eval.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
mkdir -p logs_glm53
LOG=logs_glm53/incr_eval_R2146.log
exec >>"$LOG" 2>&1

ENRICHED=$(pwd)/enriched_500.json
EVAL_MAX_WORKERS=4
export EVAL_MAX_WORKERS

echo "[$(date)] === R2146b: merge hermes predictions ==="
$PY -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions_glm53/hermes__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions_glm53/predictions_hermes.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'hermes: {len(all_preds)} real patches merged')
"

echo "[$(date)] === R2146b: hermes eval START 3 NEW instances ==="
sg docker -c "$PY -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions_glm53/predictions_hermes.json \
  --dataset_name $ENRICHED \
  --split test \
  --instance_ids django__django-16661 django__django-16877 django__django-17087 \
  --max_workers $EVAL_MAX_WORKERS \
  --run_id verified_full_glm53_hermes_incr_R2146 \
  --timeout 1800" 2>&1
echo "[$(date)] === R2146b: hermes eval DONE ==="

echo "[$(date)] === R2146b: merge R2146 results into eval_glm53_ ==="
$PY merge_R2146_glm53.py 2>&1

echo "=== incr_eval R2146b DONE $(date) ==="
