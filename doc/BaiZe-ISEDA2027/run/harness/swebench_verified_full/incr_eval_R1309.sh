#!/bin/bash
# Incremental eval for R1309 (2026-11-02 18:0x).
# scan_backlog after R1308: 4 items (nonempty patch, no report.json):
#   codex  sphinx-doc__sphinx-10466  (patchlen=1712, produced 17:54)
#   hermes django__django-14311      (patchlen=1960, produced 17:52)
#   hermes django__django-14315      (patchlen=3481, produced 17:59)
#   deepseek-harness django__django-13933 (patchlen=6555, produced 18:00)
# swebench run_evaluation SKIPS instances whose report.json already exists.
# CPU-safe: max_workers=2 (operator note 11-02: watch CPU runaway).
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_R1309_outer.log
exec > >(tee -a "$LOG") 2>&1
echo "[R1309] start $(date '+%H:%M:%S')"

do_eval() {
  local HARNESS="$1"
  local INSTANCE="$2"
  echo "[R1309] === merge $HARNESS predictions ==="
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
  echo "[R1309] === $HARNESS eval START $INSTANCE ==="
  sg docker -c "python3 -m swebench.harness.run_evaluation \
    --predictions_path $(pwd)/predictions/predictions_${HARNESS}.json \
    --dataset_name $(pwd)/enriched_500.json \
    --split test \
    --instance_ids ${INSTANCE} \
    --max_workers 2 \
    --run_id verified_full_${HARNESS} \
    --timeout 1800" 2>&1 | tee -a logs/eval_verified_full_${HARNESS}_incr_R1309.log
  echo "[R1309] === $HARNESS eval DONE rc=${PIPESTATUS[0]} ==="
  echo "[R1309] === regen eval summaries for $HARNESS ==="
  python3 regen_eval_summaries.py "$HARNESS" 2>&1 | tail -5
}

# 1. codex: sphinx-doc__sphinx-10466
do_eval codex sphinx-doc__sphinx-10466

# 2. hermes: django__django-14311 + django__django-14315 (2 items, comma-separated)
do_eval hermes django__django-14311,django__django-14315

# 3. deepseek-harness: django__django-13933
do_eval deepseek-harness django__django-13933

echo "[R1309] ALL DONE $(date '+%H:%M:%S')"
