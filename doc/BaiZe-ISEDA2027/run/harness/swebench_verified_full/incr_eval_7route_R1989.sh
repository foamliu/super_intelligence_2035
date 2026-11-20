#!/bin/bash
# R1989 incremental eval: eval missing instances across 7 harnesses.
#   cline-patched: 1 | codex: 4 | opencode: 5 | claude-code: 3 | pi: 2 | hermes: 4 | deepseek-harness: 2
#   Total: 21 instances across 7 harnesses.
#   Eval sequentially (1 harness at a time, max_workers=4) to stay <80 cores.
#   Reuse run_id=verified_full_glm53_<harness>_R1933 so results accumulate.
# Hard constraint: NEVER commit result JSON (all gitignored).
# CPU guard: max_workers=4, sequential harnesses -> peak ~4-8 cores.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs_glm53/incr_eval_7route_R1989.log
mkdir -p logs_glm53
exec >>"$LOG" 2>&1
echo "=== incr_eval_7route R1989 START $(date) ==="

HARNESSES="cline-patched codex opencode claude-code pi hermes deepseek-harness"

for H in $HARNESSES; do
    IDFILE="/tmp/incr_eval_${H}_missing_R1989.txt"
    if [ ! -f "$IDFILE" ]; then
        echo "[$(date)] === $H: no missing IDs file, skip ==="
        continue
    fi
    NEW_IDS=$(cat "$IDFILE" | tr '\n' ' ')
    NCOUNT=$(echo $NEW_IDS | wc -w)
    if [ "$NCOUNT" -eq 0 ]; then
        echo "[$(date)] === $H: 0 missing IDs, skip ==="
        continue
    fi
    echo "[$(date)] === $H: $NCOUNT missing instances to eval ==="

    # Step 1: merge predictions (only real patches)
    echo "[$(date)] === merge $H predictions ==="
    python3 -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions_glm53/${H}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and isinstance(preds,list) and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions_glm53/predictions_${H}.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'${H}: {len(all_preds)} real patches merged')
"

    # Step 2: eval ONLY the missing instance ids
    echo "[$(date)] === $H eval START $NCOUNT missing instances ==="
    sg docker -c "python3 -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions_glm53/predictions_${H}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $NEW_IDS \
      --max_workers 4 \
      --run_id verified_full_glm53_${H}_R1933 \
      --timeout 1800"
    echo "[$(date)] === $H eval DONE ==="

    # Step 3: regenerate eval report for this harness (glm53 run_id only)
    echo "[$(date)] === regenerate eval report for $H ==="
    python3 -c "
import json, os
from pathlib import Path
R='$(pwd)'
h='${H}'
EVAL_ROOT=Path(f'{R}/logs/run_evaluation')
REPORT_DIR=Path(f'{R}/reports')
all_resolved=set()
all_failed=set()
all_evaluated=set()
all_no_patch=set()
# Only glob glm53 run_ids to avoid mixing with old kimi results
for rd in EVAL_ROOT.glob(f'verified_full_glm53_{h}*'):
    for rj in rd.glob('*/*/report.json'):
        iid=rj.parent.name
        all_evaluated.add(iid)
        try:
            rep=json.loads(rj.read_text())
            inst_rep=rep.get(iid,rep) if isinstance(rep,dict) else {}
            resolved=inst_rep.get('resolved',False)
            if resolved: all_resolved.add(iid)
            elif iid not in all_resolved: all_failed.add(iid)
        except: pass
all_failed-=all_resolved
# Count no_patch (predictions with empty model_patch)
import glob as gl
for f in sorted(gl.glob(f'{R}/predictions_glm53/{h}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        d=json.loads(open(f).read())
        if d and isinstance(d,list):
            iid=d[0].get('instance_id','')
            mp=d[0].get('model_patch','')
            if iid and not mp.strip():
                all_no_patch.add(iid)
    except: pass
harness_name=h.replace('-patched','').replace('-harness','')
summary={'harness':harness_name,'harness_code':h,
         'run_id':f'verified_full_glm53_{h}_R1933','n':len(all_evaluated),
         'resolved':sorted(all_resolved),'failed':sorted(all_failed),
         'infra_or_quota':[],'no_patch':sorted(all_no_patch),
         'total_predictions':len(gl.glob(f'{R}/predictions_glm53/{h}__*.json')),
         'evaluated':len(all_evaluated),'resolved_count':len(all_resolved)}
(REPORT_DIR/f'eval_glm53_{h}.json').write_text(json.dumps(summary,indent=2))
print(f'{h}: {len(all_resolved)} resolved / {len(all_failed)} failed / {len(all_evaluated)} evaluated / {len(all_no_patch)} no_patch')
"
    echo "[$(date)] === $H report regenerated ==="
done

echo "=== incr_eval_7route R1989 DONE $(date) ==="
