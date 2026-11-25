#!/usr/bin/env python3
"""Incr eval R1636: deepseek-harness 2 backlog items (xarray-6938 patch=1818B,
xarray-6992 patch=472B) landed 07:03/07:20, predict moved on to xarray-7229.

Standing order (2026-11-02 11:2x CPU guardrail): OMP=8, workers=1 to avoid
HistGradientBoosting-style CPU runaway. Hard constraint: NEVER commit result JSON.
"""
import json, os, glob, subprocess, time

h = 'deepseek-harness'
backlog = ['pydata__xarray-6938', 'pydata__xarray-6992']
MODEL_DIR = 'deepseek-harness-kimi-k2.6-cloud'
t0 = time.time()

# CPU guardrails (standing order 2026-11-02): cap threads, serial eval
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['NUMEXPR_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'

ds = '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/enriched_500.json'

# Step 1: re-merge all deepseek predictions with real patches (avoid stale merge)
all_preds = []
for pf in sorted(glob.glob('predictions/{}__*.json'.format(h))):
    try:
        preds = json.loads(open(pf).read())
        if isinstance(preds, dict):
            preds = [preds]
        preds = [p for p in preds if p.get('model_patch', '').strip()]
        all_preds.extend(preds)
    except Exception:
        pass
merged = 'predictions/predictions_{}.json'.format(h)
open(merged, 'w').write(json.dumps(all_preds, indent=2))
print('[{}] {}: merged {} real patches -> {}'.format(
    time.strftime('%H:%M:%S'), h, len(all_preds), merged), flush=True)

# Step 2: docker eval only the 2 backlog instances (stable run_id skips already-done)
run_id = 'verified_full_{}'.format(h)
cmd = ('python3 -m swebench.harness.run_evaluation --predictions_path {} '
       '--dataset_name {} --split test --instance_ids {} '
       '--max_workers 1 --run_id {} --timeout 1800'.format(
           merged, ds, ' '.join(backlog), run_id))
print('[{}] EVAL {} on {} instances (workers=1, OMP=8)'.format(
    time.strftime('%H:%M:%S'), h, len(backlog)), flush=True)
proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True,
                      text=True, timeout=4800)
logf = 'logs/incr_eval_deepseek_R1636.log'
open(logf, 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
print('[{}] eval finished rc={}; log -> {}'.format(
    time.strftime('%H:%M:%S'), proc.returncode, logf), flush=True)

# Step 3: parse the 2 new report.json and print results
for iid in backlog:
    rj = 'logs/run_evaluation/{}/{}/{}/report.json'.format(run_id, MODEL_DIR, iid)
    if not os.path.exists(rj):
        c = glob.glob('logs/run_evaluation/{}/' + '*/{}/report.json'.format(run_id, iid))
        rj = c[0] if c else None
    if rj and os.path.exists(rj):
        rep = json.loads(open(rj).read())
        ir = rep.get(iid, rep) if isinstance(rep, dict) else {}
        res = ir.get('resolved', False)
        print('[{}] {}: {}'.format(time.strftime('%H:%M:%S'), iid,
              'RESOLVED' if res else 'FAILED'), flush=True)
    else:
        print('[{}] {}: INFRA (no report.json)'.format(
            time.strftime('%H:%M:%S'), iid), flush=True)

print('[{}] R1636 incr_eval DONE ({:.0f}s)'.format(
    time.strftime('%H:%M:%S'), time.time() - t0), flush=True)
