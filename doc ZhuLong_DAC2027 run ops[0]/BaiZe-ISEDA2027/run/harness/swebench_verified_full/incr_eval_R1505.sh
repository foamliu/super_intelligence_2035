#!/bin/bash
# R1505 incremental eval: 1 new backlog item (deepseek produced django-16485).
#   deepseek-harness: django__django-16485  (patchlen=548)
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# CPU self-check PASSED (运维令 11-02): load 36.08/224≈16% busy. Memory self-check PASSED (运维令 10-30): ~1357GB avail.
# CPU guard (运维令 11-02 R1409): OMP_NUM_THREADS/OPENBLAS/MKL/NUMEXPR/JOBLIB=8 to prevent n_jobs runaway.
# NOTE: use setsid to fully detach. EVAL_MAX_WORKERS=1 (CPU-safe, avoid 80% threshold).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=reports/incr_eval_R1505.log
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8 VECLIB_MAXIMUM_THREADS=8 JOBLIB_CPU_COUNT=8
export EVAL_MAX_WORKERS=1
exec >>"$LOG" 2>&1
echo "=== incr_eval R1505 START $(date) === (py=$PY) (CPU guard: OMP=8, EVAL_MAX_WORKERS=1)"

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
        if isinstance(preds, dict): preds=[preds]
        preds = [p for p in preds if p.get('model_patch','').strip()]
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
    echo "[$(date '+%H:%M:%S')] === $harness eval START $(echo $ids | wc -w) instances ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 1 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date '+%H:%M:%S')] === $harness eval DONE ==="
}

# Step 1: deepseek-harness — merge + eval 1 django instance.
harness=deepseek-harness
ids="django__django-16485"
echo "[$(date '+%H:%M:%S')] --- $harness: 1 instance ($ids) ---"
merge_preds "$harness"
eval_ids "$harness" "$ids"

# Step 2: regen eval summaries.
echo "[$(date '+%H:%M:%S')] --- regen eval summaries (with no-patch detection) ---"
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval R1505 DONE $(date) ==="