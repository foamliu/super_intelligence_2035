#!/bin/bash
# R1004 incremental eval: pi (gap=3) -> claude-code (gap=4) = 7 new non-empty
# patches since R1001/R1000 evals.  Sequential (8 workers each) to avoid docker
# contention with the still-running predict jobs.
# Then: regen_eval_summaries.py + gen_report_swebench_verified_full500_zh.py.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_pi_claude_R1004.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_pi_claude R1004 START $(date) ==="

merge_and_eval() {
    local harness="$1"
    local ids_file="/tmp/${harness//[-]/_}_incr_R1004_ids.txt"
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
    echo "[$(date)] === ${harness} eval START $(echo $IDS | wc -w) instances (swebench skips already-done) ==="
    sg docker -c "python3 -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $IDS \
      --max_workers 8 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1 | tee logs/eval_verified_full_${harness}_incr_R1004.log
    echo "[$(date)] === ${harness} eval DONE rc=${PIPESTATUS[0]} ==="
}

merge_and_eval "pi"
merge_and_eval "claude-code"

echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py 2>&1

echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
python3 gen_report_swebench_verified_full500_zh.py 2>&1

echo "=== incr_eval_pi_claude R1004 DONE $(date) ==="
