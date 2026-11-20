#!/usr/bin/env python3
"""Incr eval R2165: eval 5 unevaluated real patches (gateway functional for proxied path).

New real patches since R2164 (09:31):
  hermes:      mwaskom__seaborn-3187, pydata__xarray-3305
  claude-code: sympy__sympy-16886
  opencode:    sphinx-doc__sphinx-8459, sphinx-doc__sphinx-8475

Direct gateway probe returns 403 (direct-access artifact) but predict path via
gw_proxy 9092/9093 still producing real patches as of 09:40. Intermittent empties
from 429 throttling (3 new empties cleaned by cleanup_empty_patches_r2165.py).

Hard constraint: NEVER commit result JSON. Guardrails: OMP=8, workers=1.
"""
import json, os, glob, subprocess, time, sys

HARNESSES = ['hermes', 'claude-code', 'opencode']
BACKLOG = {
    'hermes': ['mwaskom__seaborn-3187', 'pydata__xarray-3305'],
    'claude-code': ['sympy__sympy-16886'],
    'opencode': ['sphinx-doc__sphinx-8459', 'sphinx-doc__sphinx-8475'],
}
PRED_DIR = 'predictions_glm53'
EVAL_REPORT_DIR = 'reports'

os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
ds = os.path.join(HERE, 'enriched_500.json')
t0 = time.time()

for h in HARNESSES:
    ids = BACKLOG[h]
    print(f'\n{"="*60}', flush=True)
    print(f'=== {h}: incr_eval R2165 ({len(ids)} instances) ===', flush=True)

    # Merge real predictions (only real patches)
    all_preds = []
    for pf in sorted(glob.glob(f'{PRED_DIR}/{h}__*.json')):
        try:
            preds = json.loads(open(pf).read())
            if isinstance(preds, dict):
                preds = [preds]
            for p in preds:
                if p.get('model_patch', '').strip():
                    all_preds.append(p)
        except:
            pass

    merged = f'{PRED_DIR}/predictions_{h}_glm53.json'
    open(merged, 'w').write(json.dumps(all_preds, indent=2))
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: merged {len(all_preds)} real preds -> {merged}', flush=True)

    run_id = f'verified_full_glm53_{h}_incr_R2165'
    cmd = (f'python3 -m swebench.harness.run_evaluation --predictions_path {merged} '
           f'--dataset_name {ds} --split test --instance_ids {" ".join(ids)} '
           f'--max_workers 1 --run_id {run_id} --timeout 1800')
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: launching eval (workers=1, timeout=1800, {len(ids)} instances)...', flush=True)
    try:
        proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=7200)
        logf = f'logs/eval_incr_verified_full_glm53_{h}_R2165.log'
        open(logf, 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
        print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval done rc={proc.returncode} (log: {logf})', flush=True)
    except subprocess.TimeoutExpired:
        print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval TIMEOUT (7200s)', flush=True)
    except Exception as e:
        print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval ERROR: {e}', flush=True)

    # Update eval report with correct keys: resolved, failed, infra_or_quota
    eval_file = os.path.join(EVAL_REPORT_DIR, f'eval_glm53_{h}.json')
    try:
        ed = json.load(open(eval_file))
    except:
        ed = {'harness': h, 'harness_code': h, 'resolved': [], 'failed': [], 'infra_or_quota': []}

    for key in ('resolved', 'failed', 'infra_or_quota'):
        ed.setdefault(key, [])

    for iid in ids:
        rj_path = glob.glob(f'logs/run_evaluation/{run_id}/*/{iid}*/report.json')
        if not rj_path:
            rj_path = glob.glob(f'logs/run_evaluation/{run_id}/**/{iid}/report.json', recursive=True)
        if rj_path:
            try:
                rd = json.load(open(rj_path[0]))
                resolved = rd.get('resolved', False)
                if resolved:
                    if iid not in ed['resolved']:
                        ed['resolved'].append(iid)
                    print(f'  {iid}: RESOLVED', flush=True)
                else:
                    if iid not in ed['failed']:
                        ed['failed'].append(iid)
                    print(f'  {iid}: failed (capability)', flush=True)
            except Exception as e:
                if iid not in ed['infra_or_quota']:
                    ed['infra_or_quota'].append(iid)
                print(f'  {iid}: error - {e}', flush=True)
        else:
            if iid not in ed['infra_or_quota']:
                ed['infra_or_quota'].append(iid)
            print(f'  {iid}: no report.json found (infra)', flush=True)

    ed['n'] = len(ed['resolved']) + len(ed['failed']) + len(ed['infra_or_quota'])
    with open(eval_file, 'w') as f:
        json.dump(ed, f, indent=2)
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval report updated (n={ed["n"]}, resolved={len(ed["resolved"])}, failed={len(ed["failed"])}, infra={len(ed["infra_or_quota"])})', flush=True)

print(f'\n{"="*60}', flush=True)
print(f'R2165 incr_eval complete in {time.time()-t0:.1f}s', flush=True)
