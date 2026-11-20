#!/bin/bash
# R1042 incremental eval: deepseek-harness ONLY (1 new patch since R1041).
# New patch: sphinx-doc__sphinx-10466 (patch_len=632).
# Follows R1040b pattern: fixed python path + re-merge predictions FIRST (avoid stale merge bug).
# Stable run_id=verified_full_deepseek-harness => swebench skips 32 already-done, runs 1 new.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_deepseek_R1042.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_deepseek R1042 START $(date) === (py=$PY)"

HARNESS=deepseek-harness
IDS_FILE=/tmp/deepseek_harness_uneval_R1042.txt

echo "[$(date)] === re-merge $HARNESS predictions (avoid stale merge) ==="
$PY -c "
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
echo "[$(date)] === ${HARNESS} eval START $(echo $IDS | wc -w) instances (stable run_id skips already-done) ==="
sg docker -c "$PY -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_${HARNESS}.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids $IDS \
  --max_workers 8 \
  --run_id verified_full_${HARNESS} \
  --timeout 1800" 2>&1
echo "[$(date)] === ${HARNESS} eval DONE rc=$? ==="

echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1

echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5

echo "=== incr_eval_deepseek R1042 DONE $(date) ==="
