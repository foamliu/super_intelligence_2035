#!/bin/bash
# Incremental eval for R1301 (2026-11-02 16:1x).
# New predictions since R1300 (16:09):
#   codex            scikit-learn__scikit-learn-26323  (patch ~2408B) ⚠️ sklearn n_jobs CPU watch
#   hermes           django__django-14089              (patch ~929B)
#   deepseek-harness django__django-13810              (patch ~2824B)
# swebench run_evaluation SKIPS instances whose report.json already exists,
# so re-running with the same --run_id only evaluates the NEW patch.
# CPU-safe: max_workers=2 (operator note 11-02: watch for sklearn n_jobs runaway).
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_R1301_outer.log
exec > >(tee -a "$LOG") 2>&1
echo "[R1301] start $(date '+%H:%M:%S')"

# --- helper: merge + eval one harness ---
do_eval() {
  local HARNESS="$1"
  local INSTANCE="$2"
  echo "[R1301] === merge $HARNESS predictions ==="
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
  echo "[R1301] === $HARNESS eval START $INSTANCE ==="
  sg docker -c "python3 -m swebench.harness.run_evaluation \
    --predictions_path $(pwd)/predictions/predictions_${HARNESS}.json \
    --dataset_name $(pwd)/enriched_500.json \
    --split test \
    --instance_ids ${INSTANCE} \
    --max_workers 2 \
    --run_id verified_full_${HARNESS} \
    --timeout 1800" 2>&1 | tee -a logs/eval_verified_full_${HARNESS}_incr_R1301.log
  echo "[R1301] === $HARNESS eval DONE rc=${PIPESTATUS[0]} ==="
  echo "[R1301] === regen eval summaries for $HARNESS ==="
  python3 regen_eval_summaries.py "$HARNESS" 2>&1 | tail -5
}

# 1. codex: scikit-learn-26323 (⚠️ sklearn — watch CPU)
do_eval codex scikit-learn__scikit-learn-26323

# 2. hermes: django-14089
do_eval hermes django__django-14089

# 3. deepseek-harness: django-13810
do_eval deepseek-harness django__django-13810

echo "[R1301] ALL DONE $(date '+%H:%M:%S')"
