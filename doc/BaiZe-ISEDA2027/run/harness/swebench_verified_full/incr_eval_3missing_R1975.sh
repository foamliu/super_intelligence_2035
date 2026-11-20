#!/bin/bash
# R1975: eval 3 truly missing instances (2 claude-code + 1 deepseek-harness)
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs_glm53/incr_eval_3missing_R1975.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_3missing R1975 START $(date) ==="

for H in claude-code deepseek-harness; do
    IDFILE="/tmp/incr_eval_${H}_missing_R1975.txt"
    if [ ! -f "$IDFILE" ]; then continue; fi
    NEW_IDS=$(cat "$IDFILE" | tr '\n' ' ')
    NCOUNT=$(echo $NEW_IDS | wc -w)
    if [ "$NCOUNT" -eq 0 ]; then continue; fi
    echo "[$(date)] === $H: $NCOUNT missing to eval ==="
    # merge predictions
    python3 -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions_glm53/${H}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions_glm53/predictions_${H}.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'${H}: {len(all_preds)} real patches merged')
"
    echo "[$(date)] === $H eval START ==="
    sg docker -c "python3 -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions_glm53/predictions_${H}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $NEW_IDS \
      --max_workers 4 \
      --run_id verified_full_glm53_${H}_R1933 \
      --timeout 1800"
    echo "[$(date)] === $H eval DONE ==="
done
echo "=== incr_eval_3missing R1975 DONE $(date) ==="
