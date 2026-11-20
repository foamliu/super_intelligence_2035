#!/bin/bash
# R1059 incremental eval: 1 BACKLOG real patch (unevald, found by systematic scan).
#   claude-code: django__django-13121  (patch_len=2166 REAL, missing report.json)
# All other routes: 0 backlog (cline/opencode/pi DONE & fully evald;
#   codex/hermes/deepseek caught up at R1057/R1058).
# swebench eval is idempotent: only the listed NEW id is passed.
# regen_eval_summaries.py rebuilds FULL summary from ALL report.json (safe).
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (98th): avail ~1470 GiB, no this-line proc >50GB
#   (max ~3.0GB cline hub daemon, opencode ~1.1GB); no partitions() runaway.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_R1059.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1059 START $(date) ==="

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

merge_preds "claude-code"

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

eval_ids "claude-code" "django__django-13121"

# Step 3: regen summaries (rebuilds FULL eval_*.json from ALL report.json) + HTML report.
echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
python3 gen_report_swebench_verified_full500_zh.py 2>&1
echo "=== incr_eval R1059 END $(date) ==="
