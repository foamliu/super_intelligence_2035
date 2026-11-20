#!/bin/bash
# incr_eval R1215: 1 backlog item (pi pylint-dev__pylint-7277, patchlen=1612, produced 22:04)
set -euo pipefail
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
HERE=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full
LOG=$HERE/logs/incr_eval_R1215.log
ENRICHED=$HERE/enriched_500.json
echo "=== incr_eval R1215 START $(date) ===" | tee "$LOG"
cd "$HERE"
$PY -c "
import json
from pathlib import Path
PRED_DIR=Path('predictions'); h='pi'
ids=[l.strip() for l in open('verified_500_ids.txt') if l.strip()]
allp=[]
for iid in ids:
    f=PRED_DIR/f'{h}__{iid}.json'
    if f.exists() and f.stat().st_size>30:
        try:
            ps=json.loads(f.read_text()); ps=[p for p in ps if p.get('model_patch','').strip()]; allp.extend(ps)
        except: pass
(PRED_DIR/f'predictions_{h}.json').write_text(json.dumps(allp,indent=2))
print(f'{h}: {len(allp)} real patches merged')
" 2>&1|tee -a "$LOG"
sg docker -c "$PY -m swebench.harness.run_evaluation --predictions_path predictions/predictions_pi.json --dataset_name $ENRICHED --split test --instance_ids pylint-dev__pylint-7277 --max_workers 8 --run_id verified_full_pi --timeout 1800" 2>&1|tee -a "$LOG"
$PY regen_eval_summaries.py pi 2>&1|tee -a "$LOG"
$PY ../gen_report_swebench_verified_full500_zh.py 2>&1|tee -a "$LOG"||echo 'WARN report gen failed'|tee -a "$LOG"
echo "=== incr_eval R1215 DONE $(date) ==="|tee -a "$LOG"
