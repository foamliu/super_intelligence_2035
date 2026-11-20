#!/bin/bash
# R1001 incremental eval: pi only (gap=2 new non-empty patches since R999).
# merge + swebench eval (stable run_id -> skips 398 already-done, runs 2 new).
# NO regen/report here: the R1000 watcher (watch_regen_R1000.sh) will run the
# single regen_eval_summaries.py + gen_report covering BOTH claude-code's
# scikit-learn-14710 (when its container ends) AND these pi results, avoiding a
# write race on eval_*.json / HTML.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_pi_R1001.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_pi START $(date) ==="

HARNESS=pi
IDS_FILE=/tmp/${HARNESS}_incr_eval_R1001_ids.txt

echo "[$(date)] === merge $HARNESS predictions ==="
python3 -c "
import json, glob, os
R='$(pwd)'
all_preds=[]; patch_ids=[]
for f in sorted(glob.glob(f'{R}/predictions/${HARNESS}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds); patch_ids.append(preds[0].get('instance_id',''))
    except: pass
with open(f'{R}/predictions/predictions_${HARNESS}.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
with open('${IDS_FILE}','w') as fh:
    fh.write('\n'.join(patch_ids)+'\n')
print(f'${HARNESS}: {len(all_preds)} patches merged, {len(patch_ids)} eval IDs')
"

IDS=$(tr '\n' ' ' < "$IDS_FILE")
echo "[$(date)] === ${HARNESS} eval START $(echo $IDS | wc -w) instances (swebench skips already-done) ==="
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_${HARNESS}.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids $IDS \
  --max_workers 8 \
  --run_id verified_full_${HARNESS} \
  --timeout 1800" 2>&1 | tee -a logs/eval_verified_full_${HARNESS}_incr_R1001.log
echo "[$(date)] === ${HARNESS} eval DONE rc=${PIPESTATUS[0]} ==="
echo "=== incr_eval_pi DONE $(date) ==="
