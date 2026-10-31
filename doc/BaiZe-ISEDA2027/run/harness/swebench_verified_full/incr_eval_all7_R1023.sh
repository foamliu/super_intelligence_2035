#!/bin/bash
# R1023 incremental eval: ALL 7 paths with unevaluated new predictions.
#   cline 58 new (predict DONE 500) · opencode 11 new (DONE 499)
#   pi 31 new · claude-code 84 new · codex 71 new · hermes 9 new · deepseek 6 new
#   = 270 new instances to eval. swebench skips already-evaluated (idempotent).
# Sequential per-harness, 8 docker workers each.  Then regen summaries + HTML.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# Memory self-check PASSED (62nd): no runaway, avail 1.3Ti, no >50GB this-line proc.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_all7_R1023.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_all7 R1023 START $(date) ==="

merge_and_eval() {
    local harness="$1"
    local ids_file="/tmp/${harness//[-]/_}_eval_ids_R1023.txt"
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
      --timeout 1800" 2>&1 | tee logs/eval_verified_full_${harness}_incr_R1023.log
    echo "[$(date)] === ${harness} eval DONE rc=${PIPESTATUS[0]} ==="
}

# Order: done-predict paths first (cline, opencode) to complete their eval,
# then alive paths by new-batch size desc.
merge_and_eval "cline-patched"
merge_and_eval "opencode"
merge_and_eval "claude-code"
merge_and_eval "codex"
merge_and_eval "pi"
merge_and_eval "hermes"
merge_and_eval "deepseek-harness"

echo "[$(date)] === regen eval summaries ==="
python3 regen_eval_summaries.py 2>&1

echo "[$(date)] === gen report HTML ==="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness
python3 gen_report_swebench_verified_full500_zh.py 2>&1

echo "=== incr_eval_all7 R1023 DONE $(date) ==="
