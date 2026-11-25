#!/usr/bin/env python3
"""incr_eval R2272: eval 1 real patch + record 10 empty as failed(capability).
  - cline-patched/sympy__sympy-23413 (REAL 3592chars -> docker eval)
  - cline-patched: sympy-21930,22456,22714 (EMPTY -> failed)
  - codex: xarray-7393,pylint-4551,4604,4661,4970,6386,6528 (EMPTY -> failed)
Guardrails: OMP=8, EVAL_MAX_WORKERS=1. NEVER commit result JSON.
"""
import json, os, glob, subprocess, time
os.environ['OMP_NUM_THREADS']='8'; os.environ['OPENBLAS_NUM_THREADS']='8'
os.environ['MKL_NUM_THREADS']='8'; os.environ['EVAL_MAX_WORKERS']='1'
HERE=os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
PRED_DIR='predictions_glm53'; EVAL_REPORT_DIR='reports'
ds=os.path.join(HERE,'enriched_500.json'); ROUND='R2272'; t0=time.time()
REAL_JOBS=[('cline-patched','sympy__sympy-23413')]
EMPTY_JOBS=[('cline-patched','sympy__sympy-21930'),('cline-patched','sympy__sympy-22456'),
('cline-patched','sympy__sympy-22714'),('codex','pydata__xarray-7393'),
('codex','pylint-dev__pylint-4551'),('codex','pylint-dev__pylint-4604'),
('codex','pylint-dev__pylint-4661'),('codex','pylint-dev__pylint-4970'),
('codex','pylint-dev__pylint-6386'),('codex','pylint-dev__pylint-6528')]
def load_eval(h):
    ef=os.path.join(EVAL_REPORT_DIR,f'eval_glm53_{h}.json')
    try: ed=json.load(open(ef))
    except: ed={'harness':h,'harness_code':h,'resolved':[],'failed':[],'infra_or_quota':[]}
    for k in ('resolved','failed','infra_or_quota'): ed.setdefault(k,[])
    return ed,ef
def save_eval(ed,ef):
    ed['n']=len(ed['resolved'])+len(ed['failed'])+len(ed['infra_or_quota'])
    ed['resolved_count']=len(ed['resolved']); ed['evaluated']=ed['n']
    with open(ef,'w') as f: json.dump(ed,f,indent=2)
def update_eval_report(h,iid,run_id):
    ed,ef=load_eval(h)
    for k in ('resolved','failed','infra_or_quota'):
        ed[k]=[x for x in ed[k] if x!=iid and not x.startswith(f'{iid}(')]
    rj=glob.glob(f'logs/run_evaluation/{run_id}/*/{iid}*/report.json')
    if not rj: rj=glob.glob(f'logs/run_evaluation/{run_id}/**/{iid}/report.json',recursive=True)
    if rj:
        try:
            rd=json.load(open(rj[0])); ir=rd.get(iid,rd) if isinstance(rd,dict) else {}
            if bool(ir.get('resolved',False)): ed['resolved'].append(iid); print(f'  {iid}: RESOLVED',flush=True)
            elif bool(ir.get('infra_failure',False)): ed['infra_or_quota'].append(iid); print(f'  {iid}: infra_failure',flush=True)
            else: ed['failed'].append(iid); print(f'  {iid}: failed(capability)',flush=True)
        except Exception as e: ed['infra_or_quota'].append(iid); print(f'  {iid}: error-{e}',flush=True)
    else: ed['infra_or_quota'].append(iid); print(f'  {iid}: no report.json(infra)',flush=True)
    ed['run_id']=run_id; save_eval(ed,ef)
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: resolved={ed["resolved_count"]} failed={len(ed["failed"])} infra={len(ed["infra_or_quota"])}',flush=True)
print(f'=== Recording {len(EMPTY_JOBS)} empty patches as failed(capability) ===',flush=True)
for h,iid in EMPTY_JOBS:
    ed,ef=load_eval(h)
    if iid not in ed['resolved'] and iid not in ed['failed'] and iid not in ed['infra_or_quota']:
        ed['failed'].append(iid); print(f'  {h}/{iid}: EMPTY->failed(capability)',flush=True)
    else: print(f'  {h}/{iid}: already in report, skip',flush=True)
    save_eval(ed,ef)
for h,iid in REAL_JOBS:
    print(f'\n=== {h}: {iid} (REAL -> docker eval) ===',flush=True)
    run_id=f'verified_full_glm53_{h}_incr_{ROUND}'; ap=[]
    for pf in sorted(glob.glob(f'{PRED_DIR}/{h}__*.json')):
        try:
            ps=json.loads(open(pf).read())
            if isinstance(ps,dict): ps=[ps]
            for p in ps:
                if p.get('model_patch','').strip(): ap.append(p)
        except: pass
    merged=f'{PRED_DIR}/predictions_{h}_glm53.json'
    open(merged,'w').write(json.dumps(ap,indent=2))
    print(f'  merged {len(ap)} real preds',flush=True)
    cmd=(f'python3 -m swebench.harness.run_evaluation --predictions_path {merged} '
         f'--dataset_name {ds} --split test --instance_ids {iid} '
         f'--max_workers 1 --run_id {run_id} --timeout 1800')
    print(f'  [{time.strftime("%H:%M:%S")}] launching eval ...',flush=True)
    try:
        proc=subprocess.run(['sg','docker','-c',cmd],capture_output=True,text=True,timeout=3600)
        os.makedirs('logs',exist_ok=True)
        logf=f'logs/eval_incr_verified_full_glm53_{h}_{ROUND}.log'
        open(logf,'w').write(proc.stdout+'\n[stderr]\n'+proc.stderr)
        for line in proc.stdout.splitlines():
            if 'resolved' in line.lower() or 'unresolved' in line.lower(): print(f'  {line.strip()}',flush=True)
        print(f'  eval done rc={proc.returncode}',flush=True)
    except subprocess.TimeoutExpired: print('  eval TIMEOUT(3600s)',flush=True)
    except Exception as e: print(f'  eval ERROR: {e}',flush=True)
    time.sleep(5); update_eval_report(h,iid,run_id)
print(f'\n=== incr_eval {ROUND} complete in {time.time()-t0:.1f}s ===',flush=True)
