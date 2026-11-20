#!/bin/bash
# incr_eval R1182b: 2 new backlog items from re-scan
#   pi:          django__django-12125  (new prediction, patch=4837B)
#   claude-code: sympy__sympy-15349   (new prediction, patch=1694B)
set -euo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
HERE=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=$HERE/logs/incr_eval_R1182b.log
ENRICHED=$HERE/enriched_500.json
EVAL_MAX_WORKERS=8
TIMEOUT_EVAL=1800

echo "=== incr_eval R1182b START $(date) === (py=$PY)" | tee "$LOG"

cd "$HERE"

merge_preds() {
  local h=$1
  echo "[$(date)] === merge $h predictions ===" | tee -a "$LOG"
  $PY -c "
import json
from pathlib import Path
PRED_DIR = Path('predictions')
harness = '$h'
ids = [l.strip() for l in open('verified_500_ids.txt') if l.strip()]
all_preds = []
for iid in ids:
    f = PRED_DIR / f'{harness}__{iid}.json'
    if f.exists() and f.stat().st_size > 30:
        try:
            preds = json.loads(f.read_text())
            preds = [p for p in preds if p.get('model_patch','').strip()]
            all_preds.extend(preds)
        except: pass
merged = PRED_DIR / f'predictions_{harness}.json'
merged.write_text(json.dumps(all_preds, indent=2))
print(f'{harness}: {len(all_preds)} real patches merged')
" 2>&1 | tee -a "$LOG"
}

run_eval() {
  local h=$1
  shift
  local ids="$*"
  local model=$( [ "$h" = "cline-patched" ] && echo "cline" || echo "$h" )-kimi-k2.6-cloud
  local run_id="verified_full_${h}"
  echo "[$(date)] === $h eval START: $ids ===" | tee -a "$LOG"
  local merged="predictions/predictions_${h}.json"
  sg docker -c "$PY -m swebench.harness.run_evaluation \
    --predictions_path $merged \
    --dataset_name $ENRICHED \
    --split test \
    --instance_ids $ids \
    --max_workers $EVAL_MAX_WORKERS \
    --run_id $run_id \
    --timeout $TIMEOUT_EVAL" 2>&1 | tee -a "$LOG"
  echo "[$(date)] === $h eval DONE ===" | tee -a "$LOG"
}

# --- 1. pi: django__django-12125 ---
merge_preds pi
run_eval pi django__django-12125

# --- 2. claude-code: sympy__sympy-15349 ---
merge_preds claude-code
run_eval claude-code sympy__sympy-15349

# --- 3. Regen eval summaries + HTML report ---
echo "[$(date)] === regen eval summaries ===" | tee -a "$LOG"
$PY regen_eval_summaries.py 2>&1 | tee -a "$LOG"
echo "[$(date)] === gen report HTML ===" | tee -a "$LOG"
$PY ../gen_report_swebench_verified_full500_zh.py 2>&1 | tee -a "$LOG" || echo "WARN: report gen failed" | tee -a "$LOG"

echo "=== incr_eval R1182b DONE $(date) ===" | tee -a "$LOG"
