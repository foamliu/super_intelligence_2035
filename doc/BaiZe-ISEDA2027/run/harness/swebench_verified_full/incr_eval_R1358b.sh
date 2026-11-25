#!/bin/bash
# R1358b incremental eval: 1 NEW real patch (found by scan_backlog after R1358).
#   codex: sphinx-doc__sphinx-8595  (patch_len=1609)
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# CPU self-check PASSED (运维令 11-02): no this-line proc >8000%CPU, load ~36/224=16%.
# Memory self-check PASSED (运维令 10-30): MemAvail ~1448GB, no this-line proc >50GB.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=reports/incr_eval_R1358b.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1358b START $(date) === (py=$PY)"

harness=codex
ids="sphinx-doc__sphinx-8595"
echo "[$(date '+%H:%M:%S')] --- $harness: 1 instance ---"
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
echo "[$(date '+%H:%M:%S')] === $harness eval START 1 new instances ==="
sg docker -c "$PY -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_${harness}.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids $ids \
  --max_workers 2 \
  --run_id verified_full_${harness} \
  --timeout 1800" 2>&1
echo "[$(date '+%H:%M:%S')] === $harness eval DONE ==="
echo "[$(date '+%H:%M:%S')] --- regen eval summaries ---"
$PY regen_eval_summaries.py 2>&1
echo "=== incr_eval R1358b DONE $(date) ==="
