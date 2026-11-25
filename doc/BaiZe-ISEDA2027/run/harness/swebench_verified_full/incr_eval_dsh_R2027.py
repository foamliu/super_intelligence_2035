#!/usr/bin/env python3
"""Incr eval R2027: deepseek-harness catch-up (R1992 completed, 37 backlog).

R1992 finished at 02:06:48 (deepseek 90/91 resolved). incr_eval_R2026 skips
deepseek (it was running when R2026 launched). Now R1992 is done, so this
script handles the remaining 37 deepseek instances.

Hard constraint: NEVER commit result JSON. Guardrails: OMP=8, workers=1.
CPU monitor: eval container processes checked for >8000% pcpu.
"""
import json, os, glob, subprocess, time, sys

H = 'deepseek-harness'
PRED_DIR = 'predictions_glm53'
EVAL_REPORT_DIR = 'reports'

os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'

ds = os.path.join(os.path.dirname(__file__), 'enriched_500.json')
t0 = time.time()

print(f'\n{"="*60}', flush=True)
print(f'=== {H}: incr_eval R2027 ===', flush=True)

# Find all real predictions
all_preds = []
pred_instances = set()
for pf in sorted(glob.glob(f'{PRED_DIR}/{H}__*.json')):
    try:
        preds = json.loads(open(pf).read())
        if isinstance(preds, dict):
            preds = [preds]
        for p in preds:
            if p.get('model_patch', '').strip():
                all_preds.append(p)
                pred_instances.add(p.get('instance_id', ''))
    except:
        pass

# Find already evaluated instances
eval_file = os.path.join(EVAL_REPORT_DIR, f'eval_glm53_{H}.json')
evaluated = set()
try:
    ed = json.load(open(eval_file))
    evaluated = set(ed.get('resolved', [])) | set(ed.get('unresolved', [])) | set(ed.get('errored', []))
except:
    pass

backlog = sorted(pred_instances - evaluated)
if not backlog:
    print(f'  {H}: no backlog, skipping', flush=True)
    sys.exit(0)

print(f'  {H}: {len(backlog)} new instances to eval (total real preds: {len(pred_instances)}, already evaluated: {len(evaluated)})', flush=True)

# Merge predictions (only real patches)
merged = f'{PRED_DIR}/predictions_{H}_glm53.json'
open(merged, 'w').write(json.dumps(all_preds, indent=2))
print(f'  [{time.strftime("%H:%M:%S")}] {H}: merged {len(all_preds)} -> {merged}', flush=True)

# Run eval for backlog only
run_id = f'verified_full_glm53_{H}_incr_R2027'
cmd = (f'python3 -m swebench.harness.run_evaluation --predictions_path {merged} '
       f'--dataset_name {ds} --split test --instance_ids {" ".join(backlog)} '
       f'--max_workers 1 --run_id {run_id} --timeout 1800')
print(f'  [{time.strftime("%H:%M:%S")}] {H}: launching eval (workers=1, timeout=1800, {len(backlog)} instances)...', flush=True)
try:
    proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=7200)
    logf = f'logs/eval_incr_verified_full_glm53_{H}_R2027.log'
    open(logf, 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
    print(f'  [{time.strftime("%H:%M:%S")}] {H}: eval done rc={proc.returncode} (log: {logf})', flush=True)
except subprocess.TimeoutExpired:
    print(f'  [{time.strftime("%H:%M:%S")}] {H}: eval TIMEOUT (7200s)', flush=True)
except Exception as e:
    print(f'  [{time.strftime("%H:%M:%S")}] {H}: eval ERROR: {e}', flush=True)

# Regenerate eval summary (same approach as incr_eval_R2026.py)
try:
    results_dir = f'/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/logs/run_evaluation/{run_id}'
    resolved = []
    unresolved = []
    errored = []
    for rf in glob.glob(f'{results_dir}/*.json'):
        try:
            rd = json.load(open(rf))
            iid = rd.get('instance_id', os.path.basename(rf).replace('.json', ''))
            if rd.get('resolved', False):
                resolved.append(iid)
            elif rd.get('errored', False):
                errored.append(iid)
            else:
                unresolved.append(iid)
        except:
            pass
    # Merge with existing eval results
    existing = {}
    try:
        existing = json.load(open(eval_file))
    except:
        pass
    existing_resolved = set(existing.get('resolved', []))
    existing_unresolved = set(existing.get('unresolved', []))
    existing_errored = set(existing.get('errored', []))
    all_resolved = sorted(existing_resolved | set(resolved))
    all_unresolved = sorted((existing_unresolved | set(unresolved)) - set(all_resolved))
    all_errored = sorted((existing_errored | set(errored)) - set(all_resolved) - set(all_unresolved))
    summary = {
        'harness': H.replace('-patched', ''),
        'harness_code': H,
        'run_id': run_id,
        'n': len(all_resolved) + len(all_unresolved) + len(all_errored),
        'resolved': all_resolved,
        'unresolved': all_unresolved,
        'errored': all_errored,
    }
    json.dump(summary, open(eval_file, 'w'), indent=2)
    print(f'  [{time.strftime("%H:%M:%S")}] {H}: eval summary updated: {len(all_resolved)}/{summary["n"]} resolved ({100*len(all_resolved)/max(summary["n"],1):.1f}%)', flush=True)
except Exception as e:
    print(f'  [{time.strftime("%H:%M:%S")}] {H}: summary update ERROR: {e}', flush=True)

print(f'\nR2027 incr_eval complete in {time.time()-t0:.0f}s ({(time.time()-t0)/60:.1f}min)', flush=True)
