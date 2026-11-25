#!/bin/bash
# R1384 incremental eval: 2 backlog items found by scan_backlog_R1384.
#   hermes           : pytest-dev__pytest-8399  (real patch patchlen=1720)
#   deepseek-harness : django__django-14855     (real patch patchlen=630)
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check 423rd PASS + CPU self-check PASS (load ~15%, <80%).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_1route_R1384.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_1route R1384 START $(date) === (py=$PY)"

merge_preds() {
    local harness="$1"
    echo "[$(date)] === merge $harness predictions ==="
    $PY -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions/${harness}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions/predictions_${harness}.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'${harness}: {len(all_preds)} real patches merged')
"
}

eval_ids() {
    local harness="$1"; shift
    local ids="$*"
    echo "[$(date)] === $harness eval START $(echo $ids | wc -w) new instances ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 2 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# Step 1: hermes — merge + eval pytest-8399.
merge_preds "hermes"
eval_ids "hermes" "pytest-dev__pytest-8399"

# Step 2: deepseek-harness — merge + eval django-14855.
merge_preds "deepseek-harness"
eval_ids "deepseek-harness" "django__django-14855"

# Step 3: regen summaries.
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "=== incr_eval_1route R1384 DONE $(date) ==="