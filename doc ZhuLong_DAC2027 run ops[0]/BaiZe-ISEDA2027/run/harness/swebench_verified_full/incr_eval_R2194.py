#!/usr/bin/env python3
"""incr_eval R2194: evaluate 4 newly accumulated real-patch instances.

Routes & instances (detected by /tmp/detect_backlog_R2194.py, newest-first):
  claude-code:    django__django-13028  (20:44)
  pi:             django__django-13794  (20:42)
  hermes:         sympy__sympy-17318    (20:44)
  pi:             django__django-13741  (20:35)

cline-patched/codex/opencode/deepseek-harness: 0 backlog (fully caught up).
Guardrails: OMP=8, EVAL_MAX_WORKERS=1. NEVER commit result JSON.
Bugfix from R2193: inst_rep = rd.get(iid, rd) for swebench nested dict {iid:{resolved}}.
"""
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
ROUND = 'R2194'
t0 = time.time()

JOBS = [
    ('claude-code', 'django__django-13028'),
    ('pi', 'django__django-13794'),
    ('hermes', 'sympy__sympy-17318'),
    ('pi', 'django__django-13741'),
]

def update_eval_report(h, iid, run_id):
    eval_file = os.path.join(EVAL_REPORT_DIR, f'eval_glm53_{h}.json')
    try:
        ed = json.load(open(eval_file))
    except:
        ed = {'harness': h, 'harness_code': h, 'resolved': [], 'failed': [], 'infra_or_quota': []}
    for key in ('resolved', 'failed', 'infra_or_quota'):
        ed.setdefault(key, [])
    # Remove iid from all lists first (idempotent re-eval)
    for key in ('resolved', 'failed', 'infra_or_quota'):
        ed[key] = [x for x in ed[key] if x != iid and not x.startswith(f'{iid}(')]
    rj_path = glob.glob(f'logs/run_evaluation/{run_id}/*/{iid}*/report.json')
    if not rj_path:
        rj_path = glob.glob(f'logs/run_evaluation/{run_id}/**/{iid}/report.json', recursive=True)
    if rj_path:
        try:
            rd = json.load(open(rj_path[0]))
            # swebench wraps result under the instance-id key: {iid: {resolved, infra_failure, ...}}
            inst_rep = rd.get(iid, rd) if isinstance(rd, dict) else {}
            resolved = bool(inst_rep.get('resolved', False))
            infra_fail = bool(inst_rep.get('infra_failure', False))
            if resolved:
                ed['resolved'].append(iid)
                print(f'  {iid}: RESOLVED', flush=True)
            elif infra_fail:
                ed['infra_or_quota'].append(iid)
                print(f'  {iid}: infra_failure', flush=True)
            else:
                ed['failed'].append(iid)
                print(f'  {iid}: failed (capability)', flush=True)
        except Exception as e:
            ed['infra_or_quota'].append(iid)
            print(f'  {iid}: error - {e}', flush=True)
    else:
        ed['infra_or_quota'].append(iid)
        print(f'  {iid}: no report.json found (infra)', flush=True)
    ed['n'] = len(ed['resolved']) + len(ed['failed']) + len(ed['infra_or_quota'])
    ed['resolved_count'] = len(ed['resolved'])
    ed['evaluated'] = ed['n']
    ed['run_id'] = run_id
    with open(eval_file, 'w') as f:
        json.dump(ed, f, indent=2)
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval updated (resolved={ed["resolved_count"]}, failed={len(ed["failed"])}, infra={len(ed["infra_or_quota"])})', flush=True)

for h, iid in JOBS:
    print(f'\n=== {h}: {iid} ===', flush=True)
    run_id = f'verified_full_glm53_{h}_incr_{ROUND}'

    # Merge real patches for this route
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
    print(f'  merged {len(all_preds)} real preds -> {merged}', flush=True)

    cmd = (f'python3 -m swebench.harness.run_evaluation --predictions_path {merged} '
           f'--dataset_name {ds} --split test --instance_ids {iid} '
           f'--max_workers 1 --run_id {run_id} --timeout 1800')
    print(f'  [{time.strftime("%H:%M:%S")}] launching eval ...', flush=True)
    try:
        proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=3600)
        logf = f'logs/eval_incr_verified_full_glm53_{h}_{ROUND}.log'
        open(logf, 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
        # Extract key result lines
        for line in proc.stdout.splitlines():
            if 'resolved' in line.lower() or 'unresolved' in line.lower() or 'infrastructure' in line.lower():
                print(f'  {line.strip()}', flush=True)
        print(f'  eval done rc={proc.returncode} (log: {logf})', flush=True)
    except subprocess.TimeoutExpired:
        print(f'  eval TIMEOUT (3600s)', flush=True)
    except Exception as e:
        print(f'  eval ERROR: {e}', flush=True)

    time.sleep(5)
    update_eval_report(h, iid, run_id)

print(f'\n=== incr_eval {ROUND} complete in {time.time()-t0:.1f}s ===', flush=True)
