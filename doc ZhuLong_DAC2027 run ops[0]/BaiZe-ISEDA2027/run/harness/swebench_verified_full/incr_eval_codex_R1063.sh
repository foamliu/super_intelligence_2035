#!/bin/bash
# R1063 incremental eval: 1 BACKLOG real patch (unevald, found by scan_backlog.py).
#   codex  : django__django-11848  (patch_len=683  REAL, missing report.json, predicted 16:17)
# Other 6 routes: no new backlog (claude-code/deepseek/hermes caught up; cline/opencode/pi DONE).
# swebench eval is idempotent: only the listed NEW id is passed.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (102nd): avail ~1.4 TiB, no this-line proc >50GB (max cline-hub-daemon 2.64GB); no partitions() runaway.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_codex_R1063.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_codex R1063 START $(date) ==="

# Step 1: regenerate merged predictions (include the new real patch).
echo "[$(date)] === merge codex predictions ==="
python3 -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions/codex__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions/predictions_codex.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'codex: {len(all_preds)} real patches merged')
"

# Step 2: eval ONLY the new instance id (idempotent; avoids re-eval).
echo "[$(date)] === codex eval START 1 new instance ==="
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions/predictions_codex.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids django__django-11848 \
  --max_workers 8 \
  --run_id verified_full_codex \
  --timeout 1800" 2>&1
echo "[$(date)] === codex eval DONE ==="

# Step 3: regen summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
python3 gen_report_swebench_verified_full500_zh.py 2>&1
echo "=== incr_eval_codex R1063 END $(date) ==="
