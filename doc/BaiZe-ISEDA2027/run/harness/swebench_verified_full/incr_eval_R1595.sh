#!/bin/bash
# R1595 incremental eval: codex 1 item (django-11820) + deepseek 2 items (matplotlib-25775, 26113)
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=logs/incr_eval_R1595.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1595 START $(date) ==="

merge_preds() {
    local h="$1"
    python3 -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions/${h}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip(): all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions/predictions_${h}.json','w') as fh: json.dump(all_preds,fh,indent=2)
print(f'${h}: merged {len(all_preds)} patches')
"
}

eval_items() {
    local h="$1"
    shift
    local ids="$@"
    merge_preds "$h"
    echo "[$(date)] === $h eval START: $ids ==="
    sg docker -c "python3 -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${h}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 4 \
      --run_id verified_full_${h}_R1595 \
      --timeout 1800" 2>&1
    echo "[$(date)] === $h eval DONE ==="
}

eval_items "codex" "django__django-11820"
eval_items "deepseek-harness" "matplotlib__matplotlib-25775" "matplotlib__matplotlib-26113"

echo "[$(date)] === regen summaries ==="
python3 regen_eval_summaries.py 2>&1
echo "=== incr_eval R1595 DONE $(date) ==="
