#!/bin/bash
# R1337b incremental eval: 1 NEW real patch (found by scan_backlog after R1337).
#   hermes: pydata__xarray-6992  (patch_len=1614) produced ~23:53
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# CPU self-check PASSED (运维令 11-02): no this-line proc >8000%CPU, load ~35/224=16%.
# Memory self-check PASSED (运维令 10-30): MemAvail ~1493GB, no this-line proc >50GB.
# NOTE: use setsid to fully detach (R1083 lesson). max_workers=2 (only 1 item, CPU-safe).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1337b.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1337b START $(date) === (py=$PY)"

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
      --max_workers 2 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# Step 1: hermes — merge + eval xarray-6992.
harness=hermes
ids="pydata__xarray-6992"
echo "[$(date)] --- $harness: 1 instance ---"
merge_preds "$harness"
eval_ids "$harness" "$ids"

# Step 2: regen eval summaries.
echo "[$(date)] --- regen eval summaries ---"
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R1337b DONE $(date) ==="
