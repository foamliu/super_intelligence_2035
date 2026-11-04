#!/usr/bin/env python3
"""Incr eval R1631b: cline-patched sympy__sympy-21596 (rerun [57/58], patch=2392B at 04:44).

regen_eval_summaries mis-classified it as infra (no report.json yet). Real docker eval here.
Hard constraint: NEVER commit result JSON. Guardrails: OMP=8, workers=1.
"""
import json, os, glob, subprocess, time

h = 'cline-patched'
backlog = ['sympy__sympy-21596']
MODEL_DIR = 'cline-kimi-k2.6-cloud'
t0 = time.time()
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'

ds = '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/enriched_500.json'
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
    rj = f'logs/run_evaluation/{run_id}/{MODEL_DIR}/{iid}/report.json'
    if not os.path.exists(rj):
        c = glob.glob(f'logs/run_evaluation/{run_id}/*/{iid}/report.json'); rj = c[0] if c else None
    if rj and os.path.exists(rj):
        rep = json.loads(open(rj).read()); ir = rep.get(iid, rep) if isinstance(rep, dict) else {}
        res = ir.get('resolved', False)
        for k in ('no_patch','failed','infra_or_quota','resolved'):
            if iid in ev.get(k, []): ev[k].remove(iid)
        ev['resolved' if res else 'failed'].append(iid)
        print(f'[{time.strftime("%H:%M:%S")}] {iid}: {"RESOLVED" if res else "FAILED"}', flush=True)
    else:
        for k in ('no_patch','failed','resolved'):
            if iid in ev.get(k, []): ev[k].remove(iid)
        ev['infra_or_quota'].append(iid); print(f'[{time.strftime("%H:%M:%S")}] {iid}: INFRA', flush=True)
ev['n'] = len(ev['resolved'])+len(ev['failed'])+len(ev['infra_or_quota'])+len(ev['no_patch'])
open(f'reports/eval_{h}.json','w').write(json.dumps(ev, indent=2))
print(f'[{time.strftime("%H:%M:%S")}] {h}: resolved={len(ev["resolved"])} failed={len(ev["failed"])} infra={len(ev["infra_or_quota"])} no_patch={len(ev["no_patch"])} n={ev["n"]}', flush=True)
print(f'[{time.strftime("%H:%M:%S")}] R1631b DONE ({time.time()-t0:.0f}s)', flush=True)
