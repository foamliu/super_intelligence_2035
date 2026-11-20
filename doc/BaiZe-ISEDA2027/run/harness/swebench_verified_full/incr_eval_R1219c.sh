#!/bin/bash
# incr_eval R1219c: 1 backlog item (hermes django__django-11433)
set -euo pipefail
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
HERE=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=$HERE/logs/incr_eval_R1219c.log
ENRICHED=$HERE/enriched_500.json
cd "$HERE"
echo "=== incr_eval R1219c START $(date) ===" | tee "$LOG"
# merge hermes predictions
$PY -c "
import json
from pathlib import Path
PRED_DIR = Path('predictions')
ids = [l.strip() for l in open('verified_500_ids.txt') if l.strip()]
all_preds = []
for iid in ids:
    f = PRED_DIR / f'hermes__{iid}.json'
    if f.exists() and f.stat().st_size > 30:
        try:
            preds = json.loads(f.read_text())
            preds = [p for p in preds if p.get('model_patch','').strip()]
            all_preds.extend(preds)
        except: pass
merged = PRED_DIR / 'predictions_hermes.json'
merged.write_text(json.dumps(all_preds, indent=2))
print(f'hermes: {len(all_preds)} real patches merged')
" 2>&1 | tee -a "$LOG"
echo "[$(date)] === hermes eval START: django__django-11433 ===" | tee -a "$LOG"
sg docker -c "$PY -m swebench.harness.run_evaluation \
  --predictions_path predictions/predictions_hermes.json \
  --dataset_name $ENRICHED \
  --split test \
  --instance_ids django__django-11433 \
  --max_workers 8 \
  --run_id verified_full_hermes \
  --timeout 1800" 2>&1 | tee -a "$LOG"
echo "[$(date)] === hermes eval DONE ===" | tee -a "$LOG"
$PY regen_eval_summaries.py 2>&1 | tee -a "$LOG"
$PY ../gen_report_swebench_verified_full500_zh.py 2>&1 | tee -a "$LOG" || echo "WARN: report gen failed" | tee -a "$LOG"
echo "=== incr_eval R1219c DONE $(date) ===" | tee -a "$LOG"
