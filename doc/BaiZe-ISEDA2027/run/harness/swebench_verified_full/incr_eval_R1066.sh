#!/bin/bash
# R1066 incremental eval: 4 BACKLOG real patches (unevald, found by scan_backlog.py).
#   claude-code      : django__django-13195 (patchlen=6053)
#                      django__django-13212 (patchlen=6648)
#   deepseek-harness : astropy__astropy-14096 (patchlen=94969)  [large patch, docker-contained]
#   hermes           : sympy__sympy-18199 (patchlen=1357)
# Other routes: 0 backlog (cline/opencode/pi DONE & fully evald; codex caught up).
# swebench eval is idempotent: only the listed NEW ids are passed (skip already-evald).
# Lesson from R1040: MUST re-merge predictions_<h>.json (include latest patches) BEFORE eval.
# regen_eval_summaries.py rebuilds FULL summary from ALL report.json (safe).
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (105th): avail ~1461 GiB, no this-line proc >50GB
#   (max ~3.2GB cline hub daemon, opencode ~1.1GB); no partitions() runaway.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_R1066.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1066 START $(date) ==="

# Step 1: regenerate merged predictions (include the new real patches) per harness.
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
merge_preds "deepseek-harness"
merge_preds "hermes"

# Step 2: eval ONLY the new instance ids per harness (idempotent; avoids re-eval).
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

eval_ids "claude-code" "django__django-13195 django__django-13212"
eval_ids "deepseek-harness" "astropy__astropy-14096"
eval_ids "hermes" "sympy__sympy-18199"

# Step 3: regen summaries (rebuilds FULL eval_*.json from ALL report.json) + HTML report.
echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
python3 gen_report_swebench_verified_full500_zh.py 2>&1
echo "=== incr_eval R1066 END $(date) ==="
