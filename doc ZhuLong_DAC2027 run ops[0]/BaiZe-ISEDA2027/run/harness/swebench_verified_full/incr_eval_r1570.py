#!/usr/bin/env python3
"""Incr eval for deepseek-harness: 2 new predictions with patches."""
import json, os, glob, subprocess, time, sys

h = 'deepseek-harness'
backlog = ['matplotlib__matplotlib-23314', 'matplotlib__matplotlib-23412']

t0 = time.time()
print(f'[incr-eval {time.strftime("%H:%M:%S")}] === incr_eval for {h}: {backlog} ===', flush=True)

# 1. Merge all predictions (including new ones)
all_preds = []
pred_files = sorted(glob.glob(f'predictions/{h}__*.json'))
for pf in pred_files:
    try:
        preds = json.loads(open(pf).read())
        preds = [p for p in preds if p.get('model_patch', '').strip()]
        all_preds.extend(preds)
    except Exception:
        pass
merged = f'predictions/predictions_{h}.json'
open(merged, 'w').write(json.dumps(all_preds, indent=2))
print(f'[incr-eval {time.strftime("%H:%M:%S")}] merged {len(all_preds)}/{len(pred_files)} predictions -> {merged}', flush=True)

# 2. Run eval on backlog instances only
run_id = f'verified_full_{h}'
max_workers = 4
cmd = (f'python3 -m swebench.harness.run_evaluation '
       f'--predictions_path {merged} --dataset_name /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/enriched_500.json --split test '
       f'--instance_ids {" ".join(backlog)} --max_workers {max_workers} '
       f'--run_id {run_id} --timeout 1800')
print(f'[incr-eval {time.strftime("%H:%M:%S")}] EVAL {h} on {len(backlog)} instances: {backlog}', flush=True)
proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=1800 * len(backlog) + 600)
logf = f'logs/eval_incr_verified_full_{h}_{int(time.time())}.log'
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
        if resolved:
            ev['resolved'].append(iid)
        else:
            ev['failed'].append(iid)
        print(f'[incr-eval {time.strftime("%H:%M:%S")}] {iid}: {status}', flush=True)
    else:
        ev['infra_or_quota'].append(iid)
        print(f'[incr-eval {time.strftime("%H:%M:%S")}] {iid}: INFRA (no report.json)', flush=True)

ev['n'] = len(ev['resolved']) + len(ev['failed']) + len(ev['infra_or_quota']) + len(ev['no_patch'])
open(ev_file, 'w').write(json.dumps(ev, indent=2))
print(f'[incr-eval {time.strftime("%H:%M:%S")}] updated {ev_file}: resolved={len(ev["resolved"])} failed={len(ev["failed"])} infra={len(ev["infra_or_quota"])} no_patch={len(ev["no_patch"])} n={ev["n"]}', flush=True)
print(f'[incr-eval {time.strftime("%H:%M:%S")}] === incr_eval DONE ({time.time()-t0:.0f}s) ===', flush=True)
