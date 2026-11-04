#!/usr/bin/env python3
"""Incr eval R1603b for deepseek-harness: psf__requests-1724 + psf__requests-1766.

Genuine backlog (real patch, no report.json in ANY eval dir).
New predictions from deepseek predict (ongoing).

Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
CPU self-check PASSED (运维令 11-02): load 27/224, no proc >8000% CPU.
Memory self-check PASSED (运维令 10-30): MEM avail 1293GB, no proc >50GB.
Guardrails: OMP_NUM_THREADS=8, EVAL_MAX_WORKERS=1 (prevent sklearn n_jobs CPU spiral).
"""
import json, os, glob, subprocess, time, sys

h = 'deepseek-harness'
backlog = ['psf__requests-1724', 'psf__requests-1766']

t0 = time.time()
print(f'[incr-eval {time.strftime("%H:%M:%S")}] === incr_eval R1603b for {h}: {backlog} ===', flush=True)

# 0. Guardrails
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'

# 1. Merge all predictions (including new ones) — only those with non-empty patches
all_preds = []
pred_files = sorted(glob.glob(f'predictions/{h}__*.json'))
for pf in pred_files:
    try:
        preds = json.loads(open(pf).read())
        if isinstance(preds, dict):
            preds = [preds]
        preds = [p for p in preds if p.get('model_patch', '').strip()]
        all_preds.extend(preds)
    except Exception:
        pass
merged = f'predictions/predictions_{h}.json'
open(merged, 'w').write(json.dumps(all_preds, indent=2))
print(f'[incr-eval {time.strftime("%H:%M:%S")}] merged {len(all_preds)}/{len(pred_files)} predictions -> {merged}', flush=True)

# 2. Run eval on backlog instances only
run_id = f'verified_full_{h}_rerun_R1603b'
max_workers = 1
dataset_path = '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/enriched_500.json'
cmd = (f'python3 -m swebench.harness.run_evaluation '
       f'--predictions_path {merged} --dataset_name {dataset_path} --split test '
       f'--instance_ids {" ".join(backlog)} --max_workers {max_workers} '
       f'--run_id {run_id} --timeout 1800')
print(f'[incr-eval {time.strftime("%H:%M:%S")}] EVAL {h} on {len(backlog)} instances: {backlog}', flush=True)
proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=1800 * len(backlog) + 600)
logf = f'logs/eval_incr_verified_full_{h}_R1603b_{int(time.time())}.log'
os.makedirs('logs', exist_ok=True)
open(logf, 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
print(f'[incr-eval {time.strftime("%H:%M:%S")}] eval finished rc={proc.returncode}; log -> {logf}', flush=True)

# 3. Parse results and merge into existing eval report
model = f'deepseek-harness-kimi-k2.6-cloud'
ev_file = f'reports/eval_{h}.json'
ev = json.load(open(ev_file))

for iid in backlog:
    rj_path = f'logs/run_evaluation/{run_id}/{model}/{iid}/report.json'
    if not os.path.exists(rj_path):
        cands = glob.glob(f'logs/run_evaluation/{run_id}/*/{iid}/report.json')
        rj_path = cands[0] if cands else None
    if rj_path and os.path.exists(rj_path):
        rep = json.loads(open(rj_path).read())
        inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
        resolved = inst_rep.get('resolved', False)
        status = 'RESOLVED' if resolved else 'FAILED'
        if iid in ev.get('no_patch', []):
            ev['no_patch'].remove(iid)
        if iid in ev.get('infra_or_quota', []):
            ev['infra_or_quota'].remove(iid)
        if iid in ev.get('failed', []):
            ev['failed'].remove(iid)
        if iid not in ev.get('resolved', []):
            if resolved:
                ev['resolved'].append(iid)
            else:
                ev['failed'].append(iid)
        print(f'[incr-eval {time.strftime("%H:%M:%S")}] {iid}: {status}', flush=True)
    else:
        ev['infra_or_quota'].append(iid)
        print(f'[incr-eval {time.strftime("%H:%M:%S")}] {iid}: INFRA (no report.json)', flush=True)

ev['n'] = len(ev['resolved']) + len(ev['failed']) + len(ev['infra_or_quota']) + len(ev.get('no_patch', []))
open(ev_file, 'w').write(json.dumps(ev, indent=2))
print(f'[incr-eval {time.strftime("%H:%M:%S")}] updated {ev_file}: resolved={len(ev["resolved"])} failed={len(ev["failed"])} infra={len(ev["infra_or_quota"])} no_patch={len(ev.get("no_patch",[]))} n={ev["n"]}', flush=True)
print(f'[incr-eval {time.strftime("%H:%M:%S")}] === incr_eval R1603b DONE ({time.time()-t0:.0f}s) ===', flush=True)
