#!/bin/bash
# R2109 incremental eval: eval 5 remaining missing instances across 3 harnesses.
#   codex: 1 (matplotlib__matplotlib-24627)
#   opencode: 2 (sympy__sympy-15976, sympy__sympy-16450)
#   hermes: 2 (django__django-14631, django__django-14725)
#   Reuse run_id=verified_full_glm53_<harness>_R1933 so results accumulate.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs_glm53/incr_eval_R2109.log
mkdir -p logs_glm53
exec >>"$LOG" 2>&1
echo "=== incr_eval_7route R2109 START $(date) ==="

for H in codex opencode hermes; do
    IDFILE="/tmp/incr_eval_${H}_missing_R2109.txt"
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

    echo "[$(date)] === regenerate eval report for $H ==="
    python3 -c "
import json, os
from pathlib import Path
R='$(pwd)'
h='${H}'
EVAL_ROOT=Path(f'{R}/logs/run_evaluation')
REPORT_DIR=Path(f'{R}/reports')
all_resolved=set(); all_failed=set(); all_evaluated=set(); all_no_patch=set()
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
import glob as gl
for f in sorted(gl.glob(f'{R}/predictions_glm53/{h}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        d=json.loads(open(f).read())
        if d and isinstance(d,list):
            iid=d[0].get('instance_id','')
            mp=d[0].get('model_patch','')
            if iid and not mp.strip(): all_no_patch.add(iid)
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

echo "=== incr_eval_7route R2109 DONE $(date) ==="
