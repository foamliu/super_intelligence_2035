#!/bin/bash
# R1039 incremental eval: 4 routes with 1 uneval straggler each (cline, opencode, claude-code, codex).
# hermes/deepseek have 0 uneval (predict just restarted, caught up).
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=logs/incr_eval_R1039.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1039 START $(date) ==="

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

eval_one() {
    local h="$1"
    local tag="$(echo $h | tr '-' '_')"
    local ids_file="/tmp/${tag}_uneval_new.txt"
    merge_preds "$h"
    local ids=$(tr '\n' ' ' < "$ids_file" 2>/dev/null)
    if [ -z "$ids" ]; then echo "[$(date)] $h: no unevaluated IDs, skip"; return; fi
    echo "[$(date)] === $h eval START $(echo $ids | wc -w) instances: $ids ==="
    sg docker -c "python3 -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${h}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 8 \
      --run_id verified_full_${h} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $h eval DONE ==="
}

eval_one "cline-patched"
eval_one "opencode"
eval_one "claude-code"
eval_one "codex"

echo "[$(date)] === regen summaries ==="
python3 regen_eval_summaries.py 2>&1
echo "=== incr_eval R1039 DONE $(date) ==="
