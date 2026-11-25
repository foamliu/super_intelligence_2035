#!/usr/bin/env python3
"""Incr eval for pi: 2 new real-patch instances (sympy__sympy-12096, sympy__sympy-12489)."""
import json, os, glob, subprocess, time, sys
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
PRED_DIR = 'predictions_glm53'
EVAL_REPORT_DIR = 'reports'
ds = os.path.join(HERE, 'enriched_500.json')
h = 'pi'
new_iids = ['sympy__sympy-12096', 'sympy__sympy-12489']
run_id = 'verified_full_glm53_pi_incr_R2360'
t0 = time.time()

# Merge pi real predictions
all_preds = []
for pf in sorted(glob.glob(f'{PRED_DIR}/{h}__*.json')):
    try:
        preds = json.loads(open(pf).read())
        if isinstance(preds, dict): preds = [preds]
        for p in preds:
            if p.get('model_patch', '').strip():
                all_preds.append(p)
    except: pass
merged = f'{PRED_DIR}/predictions_{h}_glm53.json'
open(merged, 'w').write(json.dumps(all_preds, indent=2))
print(f'[{time.strftime("%H:%M:%S")}] {h}: merged {len(all_preds)} real preds', flush=True)

# Eval only new instances
cmd = (f'python3 -m swebench.harness.run_evaluation --predictions_path {merged} '
       f'--dataset_name {ds} --split test --instance_ids {",".join(new_iids)} '
       f'--max_workers 1 --run_id {run_id} --timeout 1800')
print(f'[{time.strftime("%H:%M:%S")}] {h}: launching eval for {new_iids} ...', flush=True)
try:
    proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=7200)
    logf = f'logs_glm53/incr_eval_pi_R2360.log'
    open(logf, 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
    print(f'[{time.strftime("%H:%M:%S")}] {h}: eval done rc={proc.returncode}', flush=True)
except subprocess.TimeoutExpired:
    print(f'[{time.strftime("%H:%M:%S")}] {h}: eval TIMEOUT', flush=True)
except Exception as e:
    print(f'[{time.strftime("%H:%M:%S")}] {h}: eval ERROR: {e}', flush=True)

# Update eval report
time.sleep(5)
eval_file = os.path.join(EVAL_REPORT_DIR, f'eval_glm53_{h}.json')
ed = json.load(open(eval_file))
for key in ('resolved', 'failed', 'infra_or_quota'):
    ed.setdefault(key, [])
for iid in new_iids:
    rj_path = glob.glob(f'logs/run_evaluation/{run_id}/*/{iid}*/report.json')
    if not rj_path:
        rj_path = glob.glob(f'logs/run_evaluation/{run_id}/**/{iid}/report.json', recursive=True)
    if rj_path:
        rd = json.load(open(rj_path[0]))
        if rd.get('resolved', False):
            if iid not in ed['resolved']: ed['resolved'].append(iid)
            print(f'  {iid}: RESOLVED', flush=True)
        else:
            if iid not in ed['failed']: ed['failed'].append(iid)
            print(f'  {iid}: failed (capability)', flush=True)
    else:
        if iid not in ed['infra_or_quota']: ed['infra_or_quota'].append(iid)
        print(f'  {iid}: no report.json (infra)', flush=True)
ed['n'] = len(ed['resolved']) + len(ed['failed']) + len(ed['infra_or_quota'])
ed['evaluated'] = ed['n']
ed['total_predictions'] = len(all_preds)
ed['resolved_count'] = len(ed['resolved'])
ed['no_patch'] = 0
ed['run_id'] = run_id
with open(eval_file, 'w') as f:
    json.dump(ed, f, indent=2)
print(f'[{time.strftime("%H:%M:%S")}] {h}: eval report updated (resolved={len(ed["resolved"])}, failed={len(ed["failed"])}, infra={len(ed["infra_or_quota"])})', flush=True)
print(f'=== incr_eval_pi_R2360 done in {time.time()-t0:.1f}s ===', flush=True)
