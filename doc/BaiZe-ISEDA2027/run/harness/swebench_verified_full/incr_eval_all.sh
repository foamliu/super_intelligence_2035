#!/bin/bash
# Incremental eval for SWE-bench Verified full-500 (R955, 2026-10-30).
#
# Why: predict is still running and has produced NEW patches beyond what was
# evaluated in R947-R954.  swebench run_evaluation SKIPS instances whose
# report.json already exists under the STABLE run_id (verified in source:
# run_evaluation.py:272-273 `if report_path.exists(): return cached`), so
# re-running with the same --run_id only evaluates the NEW / retry patches
# (~51 instances total, ~10-15 min @ 8 workers).  parse_eval / regen then
# read ALL cached+new report.json -> grown coverage in eval_*.json.
#
# Routes: opencode (~19 new) -> cline-patched (~21) -> pi (~8) -> claude-code (~3).
# codex skipped (0 new: 163 patch == 163 report.json).
# After eval: regen_eval_summaries.py (all 5) + gen_report (regenerate HTML).
#
# Hard constraint (运维令 10-28): NEVER commit result JSON.  This script only
# writes untracked predictions/eval/progress/logs (all gitignored).
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs/incr_eval_all_R955.log
exec > >(tee -a "$LOG") 2>&1
echo "=== incr_eval_all START $(date) ==="

merge_and_eval() {
    local harness="$1"
    local ids_file="/tmp/${harness//[-]/_}_incr_eval_ids.txt"
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
    local IDS; IDS=$(tr '\n' ' ' < "$ids_file")
    echo "[$(date)] === ${harness} eval START $(echo $IDS | wc -w) instances (swebench skips already-done) ==="
    sg docker -c "python3 -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions/predictions_${harness}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $IDS \
      --max_workers 8 \
      --run_id verified_full_${harness} \
      --timeout 1800" 2>&1 | tee -a logs/eval_verified_full_${harness}_incr.log
    echo "[$(date)] === ${harness} eval DONE rc=${PIPESTATUS[0]} ==="
}

# Order: highest-value (most new patches) first.
# codex re-added R964 (63 new patches accumulated since it was skipped at 0-new).
merge_and_eval "opencode"
merge_and_eval "cline-patched"
merge_and_eval "pi"
merge_and_eval "claude-code"
merge_and_eval "codex"

echo "[$(date)] === regen eval summaries (all 5) ==="
python3 regen_eval_summaries.py

echo "[$(date)] === regenerate HTML report ==="
python3 ../gen_report_swebench_verified_full500_zh.py 2>&1 | tail -5

echo "=== incr_eval_all DONE $(date) ==="
