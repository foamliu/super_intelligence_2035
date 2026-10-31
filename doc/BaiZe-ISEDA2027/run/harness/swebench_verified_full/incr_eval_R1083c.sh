#!/bin/bash
# R1083c: 1 NEW backlog item emerged during R1083 (hermes predict advanced 58->59).
#   hermes : sympy__sympy-20154  (patchlen=4029, the partitions() task)
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1083c.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1083c START $(date) === (py=$PY)"

echo "[$(date)] === merge hermes predictions ==="
$PY -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions/hermes__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions/predictions_hermes.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'hermes: {len(all_preds)} real patches merged')
"

echo "[$(date)] === hermes eval START 1 instances: sympy__sympy-20154 ==="
sg docker -c "$PY -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_hermes.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids sympy__sympy-20154 \
  --max_workers 8 \
  --run_id verified_full_hermes \
  --timeout 1800" 2>&1
echo "[$(date)] === hermes eval DONE ==="

echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -10
echo "=== incr_eval R1083c DONE $(date) ==="
