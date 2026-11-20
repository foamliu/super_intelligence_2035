#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Incr eval R1607: 2 genuine backlog items.
   cline-patched    : pytest-dev__pytest-7432 (plen=3168)  -- no cline report.json in ANY run dir
   deepseek-harness : psf__requests-2931    (plen=4231)  -- no deepseek report.json in ANY run dir

Genuine backlog = real patch present AND no report.json in ANY verified_full_<h>* run dir.
(Verified 2026-11-05 via regen_eval_summaries: cline infra=1 [pytest-7432], deepseek infra=1 [requests-2931].)

Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
CPU self-check PASSED (运维令 11-02): load 27/224, no proc >8000% CPU, MEM avail 1288GB.
Memory self-check PASSED (运维令 10-30): no proc >50GB RSS.
Guardrails: OMP_NUM_THREADS=8, EVAL_MAX_WORKERS=1 (prevent sklearn n_jobs CPU spiral, 运维令 11-02).
"""
import json, os, glob, subprocess, time, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PY = '/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3'

JOBS = [
    ('cline-patched',    ['pytest-dev__pytest-7432'], 'verified_full_cline-patched_rerun_R1607'),
    ('deepseek-harness', ['psf__requests-2931'],      'verified_full_deepseek-harness_rerun_R1607'),
]

t0 = time.time()
def ts(): return time.strftime("%H:%M:%S")

# 0. Guardrails (运维令 11-02: prevent CPU spiral)
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'

dataset_path = os.path.join(os.getcwd(), 'enriched_500.json')
os.makedirs('logs', exist_ok=True)

results = {}
for harness, backlog, run_id in JOBS:
    print(f'[incr-eval {ts()}] === R1607 {harness}: {backlog} (run_id={run_id}) ===', flush=True)

    # 1. Merge all predictions (only non-empty patches)
    all_preds = []
    pred_files = sorted(glob.glob(f'predictions/{harness}__*.json'))
    for pf in pred_files:
        try:
            preds = json.loads(open(pf).read())
            if isinstance(preds, dict):
                preds = [preds]
            preds = [p for p in preds if p.get('model_patch', '').strip()]
            all_preds.extend(preds)
        except Exception:
            pass
    merged = f'predictions/predictions_{harness}.json'
    open(merged, 'w').write(json.dumps(all_preds, indent=2))
    print(f'[incr-eval {ts()}] merged {len(all_preds)}/{len(pred_files)} -> {merged}', flush=True)

    # 2. Run swebench docker eval on backlog only (sg docker, max_workers=1)
    model_map = {
        'cline-patched': 'cline-kimi-k2.6-cloud',
        'deepseek-harness': 'deepseek-harness-kimi-k2.6-cloud',
    }
    model = model_map[harness]
    cmd = (f'{PY} -m swebench.harness.run_evaluation '
           f'--predictions_path {merged} --dataset_name {dataset_path} --split test '
           f'--instance_ids {" ".join(backlog)} --max_workers 1 '
           f'--run_id {run_id} --timeout 1800')
    print(f'[incr-eval {ts()}] EVAL {harness} on {len(backlog)}: {backlog}', flush=True)
    try:
        proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True,
                              text=True, timeout=1800 * len(backlog) + 900)
        logf = f'logs/eval_incr_verified_full_{harness}_R1607_{int(time.time())}.log'
        open(logf, 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
        print(f'[incr-eval {ts()}] eval rc={proc.returncode}; log -> {logf}', flush=True)
    except subprocess.TimeoutExpired:
        print(f'[incr-eval {ts()}] EVAL {harness} TIMEOUT', flush=True)
        results[harness] = 'TIMEOUT'
        continue

    # 3. Parse result for each instance
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
            results[(harness, iid)] = status
            print(f'[incr-eval {ts()}] {harness} {iid}: {status}', flush=True)
        else:
            results[(harness, iid)] = 'INFRA'
            print(f'[incr-eval {ts()}] {harness} {iid}: INFRA (no report.json)', flush=True)

# 4. Regen eval summaries (all 7 harnesses, idempotent) + HTML report
print(f'[incr-eval {ts()}] === regen eval summaries ===', flush=True)
subprocess.run([PY, 'regen_eval_summaries.py'], cwd=os.getcwd())
print(f'[incr-eval {ts()}] === gen report HTML ===', flush=True)
subprocess.run([PY, 'gen_report_swebench_verified_full500_zh.py'],
               cwd='/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness')

print(f'[incr-eval {ts()}] === incr_eval R1607 DONE ({time.time()-t0:.0f}s) ===', flush=True)
print('SUMMARY:', results, flush=True)
