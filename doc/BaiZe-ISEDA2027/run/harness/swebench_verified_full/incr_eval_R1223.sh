#!/bin/bash
# incr_eval R1223: 3 backlog items (3 different routes), sequential to avoid container collision
# Backlog found by scan_backlog (R1223):
#   deepseek-harness: django__django-13012 (patchlen=538)
#   hermes:            django__django-11477 (patchlen=2878)
#   pi:                pytest-dev__pytest-5840 (patchlen=2897)
# Memory self-check (262nd) PASSED: avail ~1.37Ti, no this-line proc >50GB.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -euo pipefail

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
HERE=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=$HERE/logs/incr_eval_R1223.log
ENRICHED=$HERE/enriched_500.json
EVAL_MAX_WORKERS=8
TIMEOUT_EVAL=1800

echo "=== incr_eval R1223 START $(date) === (py=$PY)" | tee "$LOG"

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

# --- 1. deepseek-harness: django__django-13012 ---
merge_preds deepseek-harness
run_eval deepseek-harness django__django-13012

# --- 2. hermes: django__django-11477 ---
merge_preds hermes
run_eval hermes django__django-11477

# --- 3. pi: pytest-dev__pytest-5840 ---
merge_preds pi
run_eval pi pytest-dev__pytest-5840

# --- 4. Regen eval summaries + HTML report ---
echo "[$(date)] === regen eval summaries ===" | tee -a "$LOG"
$PY regen_eval_summaries.py 2>&1 | tee -a "$LOG"
echo "[$(date)] === gen report HTML ===" | tee -a "$LOG"
$PY ../gen_report_swebench_verified_full500_zh.py 2>&1 | tee -a "$LOG" || echo "WARN: report gen failed" | tee -a "$LOG"

echo "=== incr_eval R1223 DONE $(date) ===" | tee -a "$LOG"
