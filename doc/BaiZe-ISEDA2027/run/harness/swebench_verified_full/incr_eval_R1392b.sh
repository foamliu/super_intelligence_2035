#!/bin/bash
# R1392b incremental eval: 1 NEW real patch (found by scan_backlog after R1392).
#   hermes: scikit-learn__scikit-learn-13124 (patchlen=1013, completed ~08:5x)
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# CPU self-check PASSED (运维令 11-02): load 35.9/224≈16% (<80%), top harness proc <8000% CPU.
# Memory self-check PASSED (运维令 10-30): MemAvail ~1426GB, no runaway RSS.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=reports/incr_eval_R1392b.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1392b START $(date) === (py=$PY)"

merge_preds() {
    local harness="$1"
    echo "[$(date '+%H:%M:%S')] === merge $harness predictions ==="
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
    echo "[$(date '+%H:%M:%S')] === $harness eval START $(echo $ids | wc -w) new instances ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 2 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date '+%H:%M:%S')] === $harness eval DONE ==="
}

harness=hermes
ids="scikit-learn__scikit-learn-13124"
echo "[$(date '+%H:%M:%S')] --- $harness: 1 instance ---"
merge_preds "$harness"
eval_ids "$harness" "$ids"

echo "[$(date '+%H:%M:%S')] --- regen eval summaries ---"
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R1392b DONE $(date) ==="
