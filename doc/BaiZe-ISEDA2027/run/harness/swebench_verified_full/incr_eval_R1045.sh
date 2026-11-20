#!/bin/bash
# R1045 incremental eval: 2 harnesses with new real patches since R1044.
# New patches: claude-code django-12858 (684), hermes sympy-16450 (1286).
# Follows R1044 pattern: re-merge predictions FIRST (avoid stale merge bug), stable run_id skips already-done.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1045.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1045 START $(date) === (py=$PY)"

eval_one() {
    local h="$1"
    local IDS_FILE="/tmp/incr_eval_R1045_${h//-/_}_ids.txt"
    echo "[$(date)] === re-merge $h predictions (avoid stale merge) ==="
    $PY -c "
import json, glob, os
R='$(pwd)'
all_preds=[]; patch_ids=[]
for f in sorted(glob.glob(f'{R}/predictions/${h}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds); patch_ids.append(preds[0].get('instance_id',''))
    except: pass
with open(f'{R}/predictions/predictions_${h}.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
with open('${IDS_FILE}','w') as fh:
    fh.write('\n'.join(patch_ids)+'\n')
print(f'${h}: {len(all_preds)} patches merged, {len(patch_ids)} eval IDs')
"
    local IDS=$(tr '\n' ' ' < "$IDS_FILE")
    if [ -z "$IDS" ]; then echo "[$(date)] $h: no patch IDs, skip"; return; fi
    echo "[$(date)] === $h eval START $(echo $IDS | wc -w) instances (stable run_id skips already-done) ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${h}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $IDS \
      --max_workers 8 \
      --run_id verified_full_${h} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $h eval DONE rc=$? ==="
}

eval_one "claude-code"
eval_one "hermes"

echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R1045 DONE $(date) ==="
