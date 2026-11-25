#!/bin/bash
# R1079 add-on: 1 NEW claude-code patch (django-13363, patchlen=1061) appeared during R1079 eval.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_claude_R1079.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_claude R1079 START $(date) ==="
echo "[$(date)] === merge claude-code predictions ==="
$PY -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions/claude-code__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions/predictions_claude-code.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'claude-code: {len(all_preds)} real patches merged')
"
echo "[$(date)] === claude-code eval START 1 new instance ==="
sg docker -c "$PY -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_claude-code.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids django__django-13363 \
  --max_workers 8 \
  --run_id verified_full_claude-code \
  --timeout 1800" 2>&1
echo "[$(date)] === claude-code eval DONE ==="
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval_claude R1079 DONE $(date) ==="
