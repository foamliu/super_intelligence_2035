#!/bin/bash
# R1460 incremental eval: 1 backlog item found by scan_backlog (after R1459 regen).
#   hermes : sphinx-doc__sphinx-7889  (real patch patchlen=957)
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASS (MemAvailable~1.3TB, no RSS>50GB) + CPU self-check PASS
#   (运维令 11-02: load ~30/224≈13%, <80%; top harness proc <8000%).
# CPU guardrail (R1409): OMP_NUM_THREADS=8 to prevent sklearn n_jobs runaway.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_1route_R1460.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_1route R1460 START $(date) === (py=$PY)"

export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export MKL_NUM_THREADS=8

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

# Step 1: hermes — merge + eval 1 new instance.
merge_preds "hermes"
eval_ids "hermes" "sphinx-doc__sphinx-7889"

# Step 2: regen summaries.
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1

echo "=== incr_eval_1route R1460 DONE $(date) ==="
