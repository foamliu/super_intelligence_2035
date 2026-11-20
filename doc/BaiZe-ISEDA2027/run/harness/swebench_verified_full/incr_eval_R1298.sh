#!/bin/bash
# Incremental eval for R1298 (2026-11-02 15:1x).
# New prediction: codex scikit-learn__scikit-learn-25931 (patch 2510 chars, 15:12:30).
# swebench run_evaluation SKIPS instances whose report.json already exists,
# so re-running with the same --run_id only evaluates the NEW patch.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_R1298_outer.log
exec > >(tee -a "$LOG") 2>&1
echo "[R1298] start $(date '+%H:%M:%S')"

HARNESS=codex
INSTANCE=scikit-learn__scikit-learn-25931

# 1. Merge all codex predictions into predictions_codex.json
echo "[R1298] === merge $HARNESS predictions ==="
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
print(f'${HARNESS}: {len(all_preds)} patches merged, {len(patch_ids)} eval IDs')
"

# 2. Run swebench eval for the single new instance
echo "[R1298] === $HARNESS eval START $INSTANCE ==="
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_${HARNESS}.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids ${INSTANCE} \
  --max_workers 4 \
  --run_id verified_full_${HARNESS} \
  --timeout 1800" 2>&1 | tee -a logs/eval_verified_full_${HARNESS}_incr_R1298.log
echo "[R1298] === $HARNESS eval DONE rc=${PIPESTATUS[0]} ==="

# 3. Regen eval summaries
echo "[R1298] === regen eval summaries ==="
python3 regen_eval_summaries.py codex 2>&1 | tail -5

echo "[R1298] ALL DONE $(date '+%H:%M:%S')"
