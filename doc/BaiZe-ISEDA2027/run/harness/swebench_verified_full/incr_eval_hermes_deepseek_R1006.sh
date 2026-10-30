#!/bin/bash
# R1006 incremental eval: hermes (14 nonempty) + deepseek-harness (18 nonempty)
# = 32 new instances.  These were gate-failed originally but R988 fixed their
# adapters (hermes 80% / deepseek 60% on verify5b).  Now running full-500 predict.
# WAITS for the current incr_eval (PID 3159156) to finish before starting, to
# avoid docker contention.
# Then: regen_eval_summaries.py (now includes hermes+deepseek) + gen_report.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_hermes_deepseek_R1006.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_hermes_deepseek R1006 START $(date) ==="

# --- wait for current incr_eval (PID 3159156) to finish ---
WAIT_PID=3159156
echo "[$(date)] Waiting for incr_eval PID $WAIT_PID to finish..."
while kill -0 "$WAIT_PID" 2>/dev/null; do
    sleep 30
done
echo "[$(date)] incr_eval PID $WAIT_PID finished. Starting hermes+deepseek eval."

merge_and_eval() {
    local harness="$1"
    local ids_file="/tmp/${harness//[-]/_}_incr_R1006_ids.txt"
    echo "[$(date)] === merge $harness predictions ==="
    python3 -c "
import json, glob, os
R='$(pwd)'
all_preds=[]; patch_ids=[]
for f in sorted(glob.glob(f'{R}/predictions/${harness}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds); patch_ids.append(preds[0].get('instance_id',''))
    except: pass
with open(f'{R}/predictions/predictions_${harness}.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
with open('${ids_file}','w') as fh:
    fh.write('\n'.join(patch_ids)+'\n')
print(f'${harness}: {len(all_preds)} patches merged, {len(patch_ids)} eval IDs')
"
    IDS=$(tr '\n' ' ' < "$ids_file")
    echo "[$(date)] === ${harness} eval START $(echo $IDS | wc -w) instances ==="
    sg docker -c "python3 -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $IDS \
      --max_workers 8 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1 | tee logs/eval_verified_full_${harness}_incr_R1006.log
    echo "[$(date)] === ${harness} eval DONE rc=${PIPESTATUS[0]} ==="
}

merge_and_eval "hermes"
merge_and_eval "deepseek-harness"

echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py 2>&1

echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
python3 gen_report_swebench_verified_full500_zh.py 2>&1

echo "=== incr_eval_hermes_deepseek R1006 DONE $(date) ==="
