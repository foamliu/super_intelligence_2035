#!/bin/bash
# R1284 incremental eval: 2 NEW real patches (found by backlog scan after R1283).
#   deepseek-harness : django__django-13512  (patch_len=533)  produced ~11:22
#   hermes           : django__django-13810  (patch_len=3193) produced ~11:1x
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (323rd): avail ~1.34TiB, no this-line proc >50GB.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1284.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1284 START $(date) === (py=$PY)"

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
      --max_workers 8 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# Step 1: deepseek-harness — merge + eval django__django-13512.
harness=deepseek-harness
ids="django__django-13512"
echo "[$(date)] --- $harness: 1 instance ---"
merge_preds "$harness"
eval_ids "$harness" "$ids"

# Step 2: hermes — merge + eval django__django-13810.
harness=hermes
ids="django__django-13810"
echo "[$(date)] --- $harness: 1 instance ---"
merge_preds "$harness"
eval_ids "$harness" "$ids"

# Step 3: regen eval summaries.
echo "[$(date)] --- regen eval summaries ---"
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R1284 DONE $(date) ==="
