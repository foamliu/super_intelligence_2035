#!/bin/bash
# R1605 incr_eval: 4 genuine backlog items (cline 2 + deepseek 2).
#   cline-patched    : pytest-dev__pytest-7205 (plen=1517), pytest-dev__pytest-7236 (plen=2958)
#   deepseek-harness : psf__requests-1921 (plen=1688), psf__requests-2317 (plen=3715)
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# CPU/MEM self-check PASSED: load 23.59/224, no this-line proc >8000% CPU, MEM avail 1288GB.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1605.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1605 START $(date) === (py=$PY)"

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
    echo "[$(date)] === $harness eval START $(echo $ids | wc -w) instances ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 4 \
      --run_id verified_full_${harness}_rerun_R1605 \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# Step 1: cline-patched — merge + eval 2 items.
merge_preds "cline-patched"
eval_ids "cline-patched" "pytest-dev__pytest-7205 pytest-dev__pytest-7236"

# Step 2: deepseek-harness — merge + eval 2 items.
merge_preds "deepseek-harness"
eval_ids "deepseek-harness" "psf__requests-1921 psf__requests-2317"

# Step 3: regen eval summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval R1605 DONE $(date) ==="
