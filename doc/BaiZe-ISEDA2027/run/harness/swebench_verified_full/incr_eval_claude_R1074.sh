#!/bin/bash
# R1074 incremental eval: 1 NEW real patch found by scan_backlog.py at R1074.
#   claude-code : django__django-13315  (patch_len=4805 REAL, mtime 18:26)
# Other in-flight items (deepseek astropy-14309/14365) are handled by R1071/R1072.
# No claude-code eval container running -> safe to start (independent route).
# swebench eval is idempotent: only the 1 listed NEW id is passed.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (113th): avail ~1.4TiB, no this-line proc >50GB
#   (max cline-hub-daemon ~3.6GB, opencode ~1.1GB); no partitions() runaway.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_claude_R1074.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_claude R1074 START $(date) ==="

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

# Step 2: eval ONLY the 1 new instance id (idempotent; avoids re-eval).
echo "[$(date)] === claude-code eval START 1 new instances ==="
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_claude-code.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids django__django-13315 \
  --max_workers 8 \
  --run_id verified_full_claude-code \
  --timeout 1800" 2>&1
echo "[$(date)] === claude-code eval DONE ==="

# Step 3: regen eval summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
python3 gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval_claude R1074 DONE $(date) ==="
