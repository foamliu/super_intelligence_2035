#!/bin/bash
# Chain eval: pi -> claude-code -> codex (sequential, 8 workers each).
# R949 2026-10-30: launched after opencode+cline evals done.
# Re-merges predictions before each eval (predict still running, may add patches).
set -uo pipefail
cd "$(dirname "$0")"

merge_and_eval() {
    local harness="$1"
    local model="$2"
    local ids_file="/tmp/${harness//[-]/_}_eval_ids.txt"
    
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
    fh.write('\\n'.join(patch_ids)+'\\n')
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
      --timeout 1800" 2>&1 | tee logs/eval_verified_full_${harness}.log
    
    echo "[$(date)] === ${harness} eval DONE rc=${PIPESTATUS[0]} ==="
}

# Phase 1: pi
merge_and_eval "pi" "pi-kimi-k2.6-cloud"

# Phase 2: claude-code
merge_and_eval "claude-code" "claude-code-kimi-k2.6-cloud"

# Phase 3: codex
merge_and_eval "codex" "codex-kimi-k2.6-cloud"

echo "[$(date)] === ALL CHAIN EVALS DONE ==="
