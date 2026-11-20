#!/bin/bash
# R1127 incremental eval: 2 NEW real patches (found by scan_backlog after R1126).
#   claude-code      : django__django-16819   (patch_len=15275)  produced during predict
#   deepseek-harness : django__django-11400   (patch_len=4497)   produced during predict
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (166th): avail ~1.4TiB, no this-line proc >50GB.
#   + killed stale 17-day hung pi runtests.py tree (PID 3747564, old glm53 era, ~240MB).
# NOTE: use setsid to fully detach (R1083 lesson).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_2route_R1127.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_2route R1127 START $(date) === (py=$PY)"

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

# Step 1: claude-code — merge + eval django-16819.
merge_preds "claude-code"
eval_ids "claude-code" "django__django-16819"

# Step 2: deepseek-harness — merge + eval django-11400.
merge_preds "deepseek-harness"
eval_ids "deepseek-harness" "django__django-11400"

# Step 3: regen summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval_2route R1127 DONE $(date) ==="
