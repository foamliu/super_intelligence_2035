#!/bin/bash
# R1057 incremental eval: 3 BACKLOG real patches (unevald, found by systematic scan).
#   codex           : django__django-11815   (patch_len=17758 REAL, missing report.json)
#   deepseek-harness: astropy__astropy-13398 (patch_len=12476 REAL, missing report.json)  [R1057 prior attempt died at 0%]
#   deepseek-harness: astropy__astropy-13453 (patch_len=1383  REAL, missing report.json)
# claude-code (312/312) & hermes (30/30) fully caught up -> 0 backlog.
# 3 done routes (cline/opencode/pi) have 0 new -> skipped.
# swebench eval is idempotent: only the listed NEW ids are passed.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (96th): avail ~1472 GiB, no this-line proc >50GB (max ~1.1GB opencode); no partitions() runaway.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_R1057.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1057 START $(date) ==="

# Step 1: regenerate merged predictions (include the new real patches).
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
merge_preds "deepseek-harness"

# Step 2: eval ONLY the new instance ids (idempotent; avoids re-eval).
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

eval_ids "codex"            "django__django-11815"
eval_ids "deepseek-harness" "astropy__astropy-13398 astropy__astropy-13453"

# Step 3: regen summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
python3 gen_report_swebench_verified_full500_zh.py 2>&1
echo "=== incr_eval R1057 END $(date) ==="
