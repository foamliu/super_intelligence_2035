#!/usr/bin/env python3
"""Finish incr_eval R2167 after the parent process was killed by a tool timeout.

The cline-patched matplotlib-24177 docker eval container is already running
(sweb.eval.matplotlib__matplotlib-24177.verified_full_glm53_cline-patched_incr_R2167).
This script:
  1. Waits for that container to finish, then collects its report.json and
     updates eval_glm53_cline-patched.json.
  2. Runs the opencode sympy-13757 eval end-to-end (merge preds, launch eval
     via sg docker -c, collect report, update eval_glm53_opencode.json).

Guardrails: OMP=8, workers=1. NEVER commit result JSON.
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
t0 = time.time()

CONTAINER = 'sweb.eval.matplotlib__matplotlib-24177.verified_full_glm53_cline-patched_incr_R2167'

def docker_ps(name):
    try:
        out = subprocess.run(['sg','docker','-c', f"docker ps -a --filter name={name} --format {{{{.Status}}}}"],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return out
    except Exception as e:
        return f'ERR {e}'

def update_eval_report(h, iid, run_id):
    eval_file = os.path.join(EVAL_REPORT_DIR, f'eval_glm53_{h}.json')
    try:
        ed = json.load(open(eval_file))
    except:
        ed = {'harness': h, 'harness_code': h, 'resolved': [], 'failed': [], 'infra_or_quota': []}
    for key in ('resolved', 'failed', 'infra_or_quota'):
        ed.setdefault(key, [])
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
    ed['run_id'] = run_id
    with open(eval_file, 'w') as f:
        json.dump(ed, f, indent=2)
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval report updated (n={ed["n"]}, resolved={len(ed["resolved"])}, failed={len(ed["failed"])}, infra={len(ed["infra_or_quota"])})', flush=True)

# ---- 1. Wait for cline-patched matplotlib-24177 container ----
print(f'\n=== Step 1: wait for cline-patched container {CONTAINER} ===', flush=True)
run_id_cline = 'verified_full_glm53_cline-patched_incr_R2167'
waited = 0
while True:
    st = docker_ps(CONTAINER)
    if not st or 'Up' not in st:
        print(f'  [{time.strftime("%H:%M:%S")}] container finished/not-found: {st!r} (waited {waited}s)', flush=True)
        break
    if waited == 0:
        print(f'  [{time.strftime("%H:%M:%S")}] container still Up: {st}', flush=True)
    time.sleep(20)
    waited += 20
    if waited > 2400:
        print(f'  TIMEOUT waiting for container after {waited}s', flush=True)
        break

# small grace for logs to flush
time.sleep(5)
update_eval_report('cline-patched', 'matplotlib__matplotlib-24177', run_id_cline)

# ---- 2. Run opencode sympy-13757 eval end-to-end ----
print(f'\n=== Step 2: opencode sympy__sympy-13757 eval ===', flush=True)
h = 'opencode'
iid = 'sympy__sympy-13757'
run_id_oc = f'verified_full_glm53_{h}_incr_R2167'

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

cmd = (f'python3 -m swebench.harness.run_evaluation --predictions_path {merged} '
       f'--dataset_name {ds} --split test --instance_ids {iid} '
       f'--max_workers 1 --run_id {run_id_oc} --timeout 1800')
print(f'  [{time.strftime("%H:%M:%S")}] {h}: launching eval ...', flush=True)
try:
    proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=7200)
    logf = f'logs/eval_incr_verified_full_glm53_{h}_R2167.log'
    open(logf, 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval done rc={proc.returncode} (log: {logf})', flush=True)
except subprocess.TimeoutExpired:
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval TIMEOUT (7200s)', flush=True)
except Exception as e:
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval ERROR: {e}', flush=True)

time.sleep(5)
update_eval_report(h, iid, run_id_oc)

print(f'\n=== finish_incr_eval_R2167 complete in {time.time()-t0:.1f}s ===', flush=True)
