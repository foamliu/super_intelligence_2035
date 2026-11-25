#!/bin/bash
# R1054b incremental eval: 1 NEW deepseek-harness real patch appeared during R1054.
#   deepseek-harness : astropy__astropy-13236  (1 new, patch_len=1676 REAL)
# Run AFTER incr_eval_2routes_R1054.sh to avoid docker contention.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_deepseek_R1054b.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_deepseek R1054b START $(date) ==="

echo "[$(date)] === merge deepseek-harness predictions ==="
python3 -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions/deepseek-harness__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions/predictions_deepseek-harness.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'deepseek-harness: {len(all_preds)} real patches merged')
"

echo "[$(date)] === deepseek-harness eval START 1 new instance ==="
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_deepseek-harness.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids astropy__astropy-13236 \
  --max_workers 8 \
  --run_id verified_full_deepseek-harness \
  --timeout 1800" 2>&1
echo "[$(date)] === deepseek-harness eval DONE ==="

echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
python3 gen_report_swebench_verified_full500_zh.py 2>&1
echo "=== incr_eval_deepseek R1054b DONE $(date) ==="
