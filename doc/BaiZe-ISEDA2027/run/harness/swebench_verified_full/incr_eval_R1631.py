#!/usr/bin/env python3
"""Incr eval R1631: 2 backlog (cline rerun [56/58] sympy-20801 + deepseek xarray-4695).

Backlog scan R1631 found 2 predictions with patch_len>0 not yet eval'd:
  cline-patched      : sympy__sympy-20801 (plen=1260)  <- rerun [56/58] new patch
  deepseek-harness   : pydata__xarray-4695 (plen=573)  <- deepseek predict new patch

Hard constraint: NEVER commit result JSON. Guardrails: OMP=8, workers=1.
Does NOT touch running predict processes (eval is separate from predict).
"""
import json, os, glob, subprocess, time

JOBS = [
    ('cline-patched', ['sympy__sympy-20801']),
    ('deepseek-harness', ['pydata__xarray-4695']),
]
MODEL_DIR = {
    'cline-patched': 'cline-kimi-k2.6-cloud',
    'deepseek-harness': 'deepseek-harness-kimi-k2.6-cloud',
}
t0 = time.time()
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'

ds = '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/enriched_500.json'

for h, backlog in JOBS:
    print(f'\n=== {h}: incr_eval {backlog} ===', flush=True)
    all_preds = []
    for pf in sorted(glob.glob(f'predictions/{h}__*.json')):
        try:
            preds = json.loads(open(pf).read())
            if isinstance(preds, dict): preds = [preds]
            preds = [p for p in preds if p.get('model_patch', '').strip()]
            all_preds.extend(preds)
        except: pass
    merged = f'predictions/predictions_{h}.json'
    open(merged, 'w').write(json.dumps(all_preds, indent=2))
    print(f'[{time.strftime("%H:%M:%S")}] {h}: merged {len(all_preds)} -> {merged}', flush=True)

    run_id = f'verified_full_{h}'
    cmd = (f'python3 -m swebench.harness.run_evaluation --predictions_path {merged} '
           f'--dataset_name {ds} --split test --instance_ids {" ".join(backlog)} '
           f'--max_workers 1 --run_id {run_id} --timeout 1800')
    proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=2400)
    open(f'logs/eval_incr_verified_full_{h}_{int(time.time())}.log', 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)

    ev = json.load(open(f'reports/eval_{h}.json'))
    for iid in backlog:
        rj = f'logs/run_evaluation/{run_id}/{MODEL_DIR[h]}/{iid}/report.json'
        if not os.path.exists(rj):
            c = glob.glob(f'logs/run_evaluation/{run_id}/*/{iid}/report.json'); rj = c[0] if c else None
        if rj and os.path.exists(rj):
            rep = json.loads(open(rj).read()); ir = rep.get(iid, rep) if isinstance(rep, dict) else {}
            res = ir.get('resolved', False)
            for k in ('no_patch','failed','infra_or_quota','resolved'):
                if iid in ev.get(k, []): ev[k].remove(iid)
            ev['resolved' if res else 'failed'].append(iid)
            print(f'[{time.strftime("%H:%M:%S")}] {h} {iid}: {"RESOLVED" if res else "FAILED"}', flush=True)
        else:
            for k in ('no_patch','failed','resolved'):
                if iid in ev.get(k, []): ev[k].remove(iid)
            ev['infra_or_quota'].append(iid); print(f'[{time.strftime("%H:%M:%S")}] {h} {iid}: INFRA', flush=True)
    ev['n'] = len(ev['resolved'])+len(ev['failed'])+len(ev['infra_or_quota'])+len(ev['no_patch'])
    open(f'reports/eval_{h}.json','w').write(json.dumps(ev, indent=2))
    print(f'[{time.strftime("%H:%M:%S")}] {h}: resolved={len(ev["resolved"])} failed={len(ev["failed"])} infra={len(ev["infra_or_quota"])} no_patch={len(ev["no_patch"])} n={ev["n"]}', flush=True)

print(f'\n[{time.strftime("%H:%M:%S")}] R1631 incr_eval DONE ({time.time()-t0:.0f}s)', flush=True)
