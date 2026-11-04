#!/usr/bin/env python3
"""Incr eval R1576: 4 new real patches found by scan_backlog.py after R1575.

  cline-patched:    django__django-11276 (pl=20443)  [cline rerun 6/58, NEW]
  deepseek-harness: matplotlib__matplotlib-23476 (pl=634)
  deepseek-harness: matplotlib__matplotlib-24026 (pl=2619)
  deepseek-harness: matplotlib__matplotlib-24570 (pl=713)

R1569 adapter fix (gw_proxy routing + stdout passthrough + silent-exit retry)
→ cline rerun of 58 originally-no-patch/failed problems. django-11276 was
no_patch (timeout 1800s), now produces a real 20443B patch. Eval to see if resolves.

Hard constraint (运维令 10-28): NEVER commit result JSON (all gitignored).
CPU self-check PASSED (运维令 11-02): load 24/224 ~11% busy (pretrain-driven),
  no this-line proc >8000% CPU.
Memory self-check PASSED (运维令 10-30): avail ~1320GB, no this-line proc >50GB.
Guardrails: OMP_NUM_THREADS=8, EVAL_MAX_WORKERS=1 (prevent sklearn n_jobs CPU spiral).
"""
import json, os, glob, subprocess, time, sys

# backlog grouped by harness
backlog_by_h = {
    'cline-patched':    ['django__django-11276'],
    'deepseek-harness': ['matplotlib__matplotlib-23476',
                         'matplotlib__matplotlib-24026',
                         'matplotlib__matplotlib-24570'],
}

t0 = time.time()
print(f'[incr-eval {time.strftime("%H:%M:%S")}] === incr_eval R1576 START ===', flush=True)

# 0. Guardrails
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'

dataset_path = '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/enriched_500.json'
model_map = {
    'cline-patched':    'cline-kimi-k2.6-cloud',
    'deepseek-harness': 'deepseek-harness-kimi-k2.6-cloud',
}

for h, backlog in backlog_by_h.items():
    print(f'[incr-eval {time.strftime("%H:%M:%S")}] === {h}: {backlog} ===', flush=True)

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
    print(f'[incr-eval {time.strftime("%H:%M:%S")}] {h}: merged {len(all_preds)}/{len(pred_files)} predictions -> {merged}', flush=True)

    # 2. Run eval on backlog instances only
    run_id = f'verified_full_{h}'
    max_workers = 1
    cmd = (f'python3 -m swebench.harness.run_evaluation '
           f'--predictions_path {merged} --dataset_name {dataset_path} --split test '
           f'--instance_ids {" ".join(backlog)} --max_workers {max_workers} '
           f'--run_id {run_id} --timeout 1800')
    print(f'[incr-eval {time.strftime("%H:%M:%S")}] EVAL {h} on {len(backlog)} instances: {backlog}', flush=True)
    proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=1800 * len(backlog) + 600)
    logf = f'logs/eval_incr_verified_full_{h}_{int(time.time())}.log'
    os.makedirs('logs', exist_ok=True)
    open(logf, 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
    print(f'[incr-eval {time.strftime("%H:%M:%S")}] {h} eval finished rc={proc.returncode}; log -> {logf}', flush=True)

    # 3. Parse results and merge into existing eval report
    model = model_map[h]
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
            # Remove from no_patch if present (it now has a patch and was eval'd)
            if iid in ev.get('no_patch', []):
                ev['no_patch'].remove(iid)
            if iid in ev.get('failed', []):
                ev['failed'].remove(iid)
            if iid in ev.get('resolved', []):
                pass  # already there
            else:
                if resolved:
                    ev['resolved'].append(iid)
                else:
                    ev['failed'].append(iid)
            print(f'[incr-eval {time.strftime("%H:%M:%S")}] {h} {iid}: {status}', flush=True)
        else:
            ev['infra_or_quota'].append(iid)
            print(f'[incr-eval {time.strftime("%H:%M:%S")}] {h} {iid}: INFRA (no report.json)', flush=True)

    ev['n'] = len(ev['resolved']) + len(ev['failed']) + len(ev['infra_or_quota']) + len(ev['no_patch'])
    open(ev_file, 'w').write(json.dumps(ev, indent=2))
    print(f'[incr-eval {time.strftime("%H:%M:%S")}] {h}: updated {ev_file}: resolved={len(ev["resolved"])} failed={len(ev["failed"])} infra={len(ev["infra_or_quota"])} no_patch={len(ev["no_patch"])} n={ev["n"]}', flush=True)

print(f'[incr-eval {time.strftime("%H:%M:%S")}] === incr_eval R1576 DONE ({time.time()-t0:.0f}s) ===', flush=True)
