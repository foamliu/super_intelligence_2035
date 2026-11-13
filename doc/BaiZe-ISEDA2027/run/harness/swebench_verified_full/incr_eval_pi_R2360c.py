#!/usr/bin/env python3
"""Incr eval for pi: 2 new real-patch instances (sympy-12096, sympy-12489).
Fix: instance_ids must be unquoted space-separated for nargs='+'.
"""
import json, os, glob, subprocess, time, pathlib
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
run_id = 'verified_full_glm53_pi_incr_R2360c'
new_iids = ['sympy__sympy-12096', 'sympy__sympy-12489']
merged = 'predictions_glm53/predictions_pi_glm53.json'
ds = os.path.join(HERE, 'enriched_500.json')
# NO quotes around instance_ids - nargs="+" expects space-separated
cmd = (
    f'python3 -m swebench.harness.run_evaluation '
    f'--predictions_path {merged} --dataset_name {ds} --split test '
    f'--instance_ids {" ".join(new_iids)} '
    f'--max_workers 1 --run_id {run_id} --timeout 1800'
)
print('CMD:', cmd, flush=True)
t0 = time.time()
try:
    proc = subprocess.run(
        ['sg', 'docker', '-c', cmd],
        capture_output=True, text=True, timeout=7200
    )
    open('logs_glm53/incr_eval_pi_R2360c.log', 'w').write(
        proc.stdout + '\n[stderr]\n' + proc.stderr
    )
    print(f'eval done rc={proc.returncode} in {time.time()-t0:.1f}s', flush=True)
except Exception as e:
    print(f'eval ERROR: {e}', flush=True)
time.sleep(3)
eval_file = os.path.join(HERE, 'reports/eval_glm53_pi.json')
ed = json.load(open(eval_file))
for key in ('resolved', 'failed', 'infra_or_quota'):
    ed.setdefault(key, [])
# Remove from infra if they were incorrectly added before
for iid in new_iids:
    if iid in ed.get('infra_or_quota', []):
        ed['infra_or_quota'].remove(iid)
for iid in new_iids:
    rj = list(
        pathlib.Path(HERE).rglob(
            f'logs/run_evaluation/{run_id}/**/{iid}/report.json'
        )
    )
    if rj:
        rd = json.load(open(rj[0]))
        if rd.get('resolved', False):
            if iid not in ed['resolved']:
                ed['resolved'].append(iid)
            print(f'  {iid}: RESOLVED', flush=True)
        else:
            if iid not in ed['failed']:
                ed['failed'].append(iid)
            print(f'  {iid}: failed', flush=True)
    else:
        if iid not in ed['infra_or_quota']:
            ed['infra_or_quota'].append(iid)
        print(f'  {iid}: no report (infra)', flush=True)
ed['n'] = len(ed['resolved']) + len(ed['failed']) + len(ed['infra_or_quota'])
ed['evaluated'] = ed['n']
ed['total_predictions'] = 274
ed['resolved_count'] = len(ed['resolved'])
with open(eval_file, 'w') as f:
    json.dump(ed, f, indent=2)
print(
    f'pi eval: resolved={len(ed["resolved"])} '
    f'failed={len(ed["failed"])} infra={len(ed["infra_or_quota"])}',
    flush=True
)
