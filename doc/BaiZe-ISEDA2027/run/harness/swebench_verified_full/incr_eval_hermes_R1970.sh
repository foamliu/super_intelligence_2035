#!/bin/bash
# R1970 incremental eval: hermes 22 NEW real patches (post-R1933 eval).
#   Eval only the 22 new instance IDs, reuse run_id=verified_full_glm53_hermes_R1933
#   so results land in the same directory (idempotent, no re-eval of 279 done).
# swebench eval is idempotent: only the 22 listed NEW ids are passed.
# Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
# CPU guard (运维令 11-02): max_workers=4 to stay <80 cores.
set -uo pipefail
cd "$(dirname "$0")"
LOG=logs_glm53/incr_eval_hermes_R1970.log
exec >>"$LOG" 2>&1
echo "=== incr_eval_hermes R1970 START $(date) ==="

# Step 1: merge hermes predictions (include all real patches).
echo "[$(date)] === merge hermes predictions ==="
python3 -c "
import json, glob, os
R='$(pwd)'
all_preds=[]
for f in sorted(glob.glob(f'{R}/predictions_glm53/hermes__*.json')):
    if os.path.getsize(f)<30: continue
    try:
        preds=json.loads(open(f).read())
        if preds and preds[0].get('model_patch','').strip():
            all_preds.extend(preds)
    except: pass
with open(f'{R}/predictions_glm53/predictions_hermes.json','w') as fh:
    json.dump(all_preds,fh,indent=2)
print(f'hermes: {len(all_preds)} real patches merged')
"

# Step 2: eval ONLY the 22 new instance ids (idempotent; avoids re-eval).
NEW_IDS=$(cat /tmp/incr_eval_hermes_new_ids.txt | tr '\n' ' ')
echo "[$(date)] === hermes eval START 22 new instances ==="
echo "[$(date)] new_ids: $NEW_IDS"
sg docker -c "python3 -m swebench.harness.run_evaluation \
  --predictions_path $(pwd)/predictions_glm53/predictions_hermes.json \
  --dataset_name $(pwd)/enriched_500.json \
  --split test \
  --instance_ids $NEW_IDS \
  --max_workers 4 \
  --run_id verified_full_glm53_hermes_R1933 \
  --timeout 1800" 2>&1
echo "[$(date)] === hermes eval DONE rc=$? ==="

# Step 3: re-parse ALL results (old+new) to update eval report.
echo "[$(date)] === re-parse hermes eval results ==="
python3 -c "
import json, glob, os
HERE='$(pwd)'
EVAL_ROOT=HERE+'/logs/run_evaluation'
run_id='verified_full_glm53_hermes_R1933'
harness='hermes'
model='hermes-glm-5.3-flash'
run_dir=f'{EVAL_ROOT}/{run_id}'
resolved=[]; failed=[]; infra=[]
# find all report.json under run_dir
for rj in glob.glob(f'{run_dir}/*/*/report.json'):
    iid=rj.split('/')[-2]
    try:
        rep=json.loads(open(rj).read())
        inst_rep=rep.get(iid,rep) if isinstance(rep,dict) else {}
        r=inst_rep.get('resolved',False)
        (resolved if r else failed).append(iid)
    except:
        infra.append(iid)
summary={'harness':'hermes','harness_code':'hermes','run_id':run_id,
         'n':len(resolved)+len(failed)+len(infra),
         'resolved':sorted(resolved),'failed':sorted(failed),'infra_or_quota':sorted(infra)}
out=HERE+f'/reports/eval_glm53_hermes.json'
json.dump(summary,open(out,'w'),indent=2)
print(f'hermes: n={summary[\"n\"]} resolved={len(resolved)} failed={len(failed)} infra={len(infra)} -> {out}')
"
echo "=== incr_eval_hermes R1970 END $(date) ==="
