#!/bin/bash
# R1093 incremental eval: 3 NEW real patches (found by scan_backlog.py at R1093).
#   claude-code       : django__django-13590   (patch_len=1806)
#   codex             : django__django-12325   (patch_len=2421)
#   deepseek-harness  : django__django-10880   (patch_len=635)
# 3 independent routes -> no container collision. Eval sequentially.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (132nd): avail ~1.4TiB, no this-line proc >50GB
#   (max cline-hub-daemon ~3.1GB, opencode 1.1GB, gw_proxy 221MB); no partitions() runaway.
# NOTE: use setsid to fully detach (R1083 lesson: `sg docker` child killed under nohup).
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_3routes_R1093.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_3routes R1093 START $(date) === (py=$PY)"

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

# Step 1: claude-code — merge + eval django-13590.
merge_preds "claude-code"
eval_ids "claude-code" "django__django-13590"

# Step 2: codex — merge + eval django-12325.
merge_preds "codex"
eval_ids "codex" "django__django-12325"

# Step 3: deepseek-harness — merge + eval django-10880.
merge_preds "deepseek-harness"
eval_ids "deepseek-harness" "django__django-10880"

# Step 4: regen summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval_3routes R1093 DONE $(date) ==="
