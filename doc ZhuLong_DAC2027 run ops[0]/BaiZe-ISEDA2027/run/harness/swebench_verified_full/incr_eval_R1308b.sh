#!/bin/bash
# Incremental eval for R1308b (2026-11-02 17:4x).
# scan_backlog after R1308: deepseek django__django-13925 (patch 93447B, produced ~17:4x).
# (codex sphinx-doc__sphinx-10449 had EMPTY patch -> no_patch, not eval'd.)
# swebench run_evaluation SKIPS instances whose report.json already exists.
# CPU-safe: max_workers=2 (operator note 11-02: watch CPU runaway).
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_R1308b_outer.log
exec > >(tee -a "$LOG") 2>&1
echo "[R1308b] start $(date '+%H:%M:%S')"

do_eval() {
  local HARNESS="$1"
  local INSTANCE="$2"
  echo "[R1308b] === merge $HARNESS predictions ==="
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
  echo "[R1308b] === $HARNESS eval START $INSTANCE ==="
  sg docker -c "python3 -m swebench.harness.run_evaluation \
    --predictions_path $(pwd)/predictions/predictions_${HARNESS}.json \
    --dataset_name $(pwd)/enriched_500.json \
    --split test \
    --instance_ids ${INSTANCE} \
    --max_workers 2 \
    --run_id verified_full_${HARNESS} \
    --timeout 1800" 2>&1 | tee -a logs/eval_verified_full_${HARNESS}_incr_R1308b.log
  echo "[R1308b] === $HARNESS eval DONE rc=${PIPESTATUS[0]} ==="
  echo "[R1308b] === regen eval summaries for $HARNESS ==="
  python3 regen_eval_summaries.py "$HARNESS" 2>&1 | tail -5
}

# 1. deepseek: django-13925
do_eval deepseek-harness django__django-13925

echo "[R1308b] ALL DONE $(date '+%H:%M:%S')"
