#!/bin/bash
# R1085 incremental eval: 1 NEW real patch (found by scan_backlog.py after R1084).
#   deepseek-harness : astropy__astropy-7671 (patch_len=927)
# Single route -> no container collision.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (124th): avail ~1.4TiB, no this-line proc >50GB.
# NOTE: use setsid to fully detach (R1083 lesson).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_1route_R1085.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_1route R1085 START $(date) === (py=$PY)"

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
      --max_workers 8 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# Step 1: deepseek-harness — merge + eval astropy-7671.
merge_preds "deepseek-harness"
eval_ids "deepseek-harness" "astropy__astropy-7671"

# Step 2: regen summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval_1route R1085 DONE $(date) ==="
