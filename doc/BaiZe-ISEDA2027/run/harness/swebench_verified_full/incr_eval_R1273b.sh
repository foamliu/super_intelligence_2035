#!/bin/bash
# R1273b incr_eval: codex sklearn-10908 (re-eval, prev crashed) + deepseek django-13363 + hermes django-13569.
# scan_backlog=3 (all real patch, no report.json). 11310 already resolved in R1273.
set -uo pipefail
cd "$(dirname "$0")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3
LOG=logs/incr_eval_R1273b.log
exec >>"$LOG" 2>&1
echo "=== incr_eval R1273b $(date) === (codex sklearn-10908, deepseek django-13363, hermes django-13569)"

merge_preds() {
    local harness="$1"
    echo "[$(date)] === merge $harness predictions ==="
    $PY -c "
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

eval_ids() {
    local harness="$1"; shift
    local ids="$*"
    echo "[$(date)] === $harness eval START $(echo $ids | wc -w) new instances ==="
    sg docker -c "$PY -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $ids \
      --max_workers 8 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1
    echo "[$(date)] === $harness eval DONE ==="
}

# codex — merge + eval 1 instance (10908 re-eval).
merge_preds "codex"
eval_ids "codex" "scikit-learn__scikit-learn-10908"

# deepseek-harness — merge + eval 1 instance.
merge_preds "deepseek-harness"
eval_ids "deepseek-harness" "django__django-13363"

# hermes — merge + eval 1 instance.
merge_preds "hermes"
eval_ids "hermes" "django__django-13569"

# regen summaries + HTML report.
echo "[$(date)] === regen eval summaries ==="
$PY regen_eval_summaries.py 2>&1
echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
$PY gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5
echo "=== incr_eval R1273b DONE $(date) ==="
