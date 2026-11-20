#!/bin/bash
# R1056 incremental eval: 2 BACKLOG real patches (unevald, found by systematic scan).
#   codex  : django__django-11790  (patch_len=965  REAL, missing report.json)
#   hermes : sympy__sympy-16886    (patch_len=460  REAL, missing report.json)
# claude-code (312/312) & deepseek-harness (36/36) fully caught up -> skipped.
# 3 done routes (cline/opencode/pi) have 0 new -> skipped.
# swebench eval is idempotent: only the listed NEW ids are passed.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (95th): avail ~1473 GiB, no this-line proc >50GB (max ~32MB); no partitions() runaway.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_2routes_R1056.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_2routes R1056 START $(date) ==="

# Step 1: regenerate merged predictions (include the new real patch).
merge_preds() {
    local harness="$1"
    echo "[$(date)] === merge $harness predictions ==="
    python3 -c "
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

merge_preds "codex"
merge_preds "hermes"

# Step 2: eval ONLY the new instance id (idempotent; avoids re-eval).
eval_ids() {
    local harness="$1"; shift
    local ids="$*"
    echo "[$(date)] === $harness eval START $(echo $ids | wc -w) new instances ==="
    sg docker -c "python3 -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 8 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

eval_ids "codex"  "django__django-11790"
eval_ids "hermes" "sympy__sympy-16886"

# Step 3: regen summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
python3 gen_report_swebench_verified_full500_zh.py 2>&1
echo "=== incr_eval_2routes R1056 END $(date) ==="
