#!/usr/bin/env python3
"""Incr eval R1643: 1 backlog deepseek-harness (pytest-10081, patchlen=17386, landed 12:08).

Backlog scan R1643 found 1 TRUE backlog deepseek-harness prediction with
patch_len>0 not yet eval'd:
  deepseek-harness : pytest-dev__pytest-10081 (plen=17386)  <- deepseek predict new patch (12:08)

Hard constraint: NEVER commit result JSON. Guardrails: OMP=8, workers=1.
Does NOT touch running predict processes (eval is separate from predict).
CPU monitor: eval container processes checked for >8000% pcpu (per 2026-11-02 directive).
"""
import json, os, glob, subprocess, time

JOBS = [
    ('deepseek-harness', ['pytest-dev__pytest-10081']),
]
MODEL_DIR = {
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

    run_id = f'verified_full_{h}_incr_R1643'
    cmd = (f'python3 -m swebench.harness.run_evaluation --predictions_path {merged} '
           f'--dataset_name {ds} --split test --instance_ids {" ".join(backlog)} '
           f'--max_workers 1 --run_id {run_id} --timeout 1800')
    print(f'[{time.strftime("%H:%M:%S")}] {h}: launching eval (workers=1, timeout=1800, run_id={run_id})...', flush=True)
    proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=2400)
    open(f'logs/eval_incr_verified_full_{h}_{int(time.time())}.log', 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
    print(f'[{time.strftime("%H:%M:%S")}] {h}: eval done rc={proc.returncode}', flush=True)

    ev = json.load(open(f'reports/eval_{h}.json'))
    for iid in backlog:
        # dual-path check: swebench v5.0.2 writes to logs/evaluation/{run_id}/,
        # older runs wrote to logs/run_evaluation/{run_id}/
        rj = None
        for base in ('logs/evaluation', 'logs/run_evaluation'):
            for c in glob.glob(f'{base}/{run_id}/{MODEL_DIR[h]}/{iid}/report.json'):
                rj = c; break
            if rj: break
        # also check the plain run_id (non-incr) path used by earlier full evals
        if not rj:
            plain = f'verified_full_{h}'
            for base in ('logs/evaluation', 'logs/run_evaluation'):
                for c in glob.glob(f'{base}/{plain}/{MODEL_DIR[h]}/{iid}/report.json'):
                    rj = c; break
                if rj: break
        if rj and os.path.exists(rj):
            rep = json.loads(open(rj).read()); ir = rep.get(iid, rep) if isinstance(rep, dict) else {}
            res = ir.get('resolved', False)
            for k in ('no_patch','failed','infra_or_quota','resolved'):
                if iid in ev.get(k, []): ev[k].remove(iid)
            ev['resolved' if res else 'failed'].append(iid)
            print(f'[{time.strftime("%H:%M:%S")}] {h} {iid}: {"RESOLVED" if res else "FAILED"} (from {rj})', flush=True)
        else:
            for k in ('no_patch','failed','resolved'):
                if iid in ev.get(k, []): ev[k].remove(iid)
            ev['infra_or_quota'].append(iid); print(f'[{time.strftime("%H:%M:%S")}] {h} {iid}: INFRA (no report.json found)', flush=True)
    ev['n'] = len(ev['resolved'])+len(ev['failed'])+len(ev['infra_or_quota'])+len(ev['no_patch'])
    open(f'reports/eval_{h}.json','w').write(json.dumps(ev, indent=2))
    print(f'[{time.strftime("%H:%M:%S")}] {h}: resolved={len(ev["resolved"])} failed={len(ev["failed"])} infra={len(ev["infra_or_quota"])} no_patch={len(ev["no_patch"])} n={ev["n"]}', flush=True)

print(f'\n[{time.strftime("%H:%M:%S")}] R1643 incr_eval DONE ({time.time()-t0:.0f}s)', flush=True)
