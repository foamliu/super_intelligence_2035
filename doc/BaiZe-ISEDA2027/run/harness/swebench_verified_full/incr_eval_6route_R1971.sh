#!/bin/bash
# R1971 incremental eval: 6 harnesses with NEW real patches (post-R1933 eval).
#   cline-patched: 64 new | codex: 9 new | opencode: 126 new
#   claude-code: 57 new | pi: 56 new | deepseek-harness: 48 new
#   Total: 360 new instances across 6 harnesses.
#   Eval sequentially (1 harness at a time, max_workers=4) to stay <80 cores.
#   Reuse run_id=verified_full_glm53_<harness>_R1933 so results accumulate.
# Hard constraint: NEVER commit result JSON (all gitignored).
# CPU guard: max_workers=4, sequential harnesses -> peak ~4-8 cores.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs_glm53/incr_eval_6route_R1971.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_6route R1971 START $(date) ==="

HARNESSES="cline-patched codex opencode claude-code pi deepseek-harness"

for H in $HARNESSES; do
    IDFILE="/tmp/incr_eval_${H}_new_ids.txt"
    NEW_IDS=$(cat "$IDFILE" 2>/dev/null | tr '\n' ' ')
    NCOUNT=$(echo $NEW_IDS | wc -w)
    if [ "$NCOUNT" -eq 0 ]; then
        echo "[$(date)] === $H: 0 new IDs, skip ==="
        continue
    fi
    echo "[$(date)] === $H: $NCOUNT new instances to eval ==="

    # Step 1: merge predictions
    echo "[$(date)] === merge $H predictions ==="
    python3 -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions_glm53/${H}__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions_glm53/predictions_${H}.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'${H}: {len(all_preds)} real patches merged')
"

    # Step 2: eval ONLY the new instance ids
    echo "[$(date)] === $H eval START $NCOUNT new instances ==="
    sg docker -c "python3 -m swebench.harness.run_evaluation \
      --predictions_path $(pwd)/predictions_glm53/predictions_${H}.json \
      --dataset_name $(pwd)/enriched_500.json \
      --split test \
      --instance_ids $NEW_IDS \
      --max_workers 4 \
      --run_id verified_full_glm53_${H}_R1933 \
      --timeout 1800" 2>&1
    echo "[$(date)] === $H eval DONE rc=$? ==="

    # Step 3: re-parse ALL results (old+new) to update eval report
    echo "[$(date)] === re-parse $H eval results ==="
    python3 -c "
import json, glob, os
HERE='$(pwd)'
EVAL_ROOT=HERE+'/logs/run_evaluation'
run_id='verified_full_glm53_${H}_R1933'
harness='${H}'
run_dir=f'{EVAL_ROOT}/{run_id}'
resolved=[]; failed=[]; infra=[]
for rj in glob.glob(f'{run_dir}/*/*/report.json'):
    iid=rj.split('/')[-2]
    try:
        rep=json.loads(open(rj).read())
        inst_rep=rep.get(iid,rep) if isinstance(rep,dict) else {}
        r=inst_rep.get('resolved',False)
        (resolved if r else failed).append(iid)
    except:
        infra.append(iid)
summary={'harness':harness,'harness_code':harness,'run_id':run_id,
         'n':len(resolved)+len(failed)+len(infra),
         'resolved':sorted(resolved),'failed':sorted(failed),'infra_or_quota':sorted(infra)}
out=HERE+f'/reports/eval_glm53_${H}.json'
json.dump(summary,open(out,'w'),indent=2)
print(f'{harness}: n={summary[\"n\"]} resolved={len(resolved)} failed={len(failed)} infra={len(infra)} -> {out}')
"
done

echo "=== incr_eval_6route R1971 END $(date) ==="
