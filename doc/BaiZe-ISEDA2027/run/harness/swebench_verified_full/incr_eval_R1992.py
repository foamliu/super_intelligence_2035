#!/usr/bin/env python3
"""Incr eval R1992: 269 new real predictions across 7 routes (glm53).

Backlog:
  cline-patched: 36, codex: 26, opencode: 72, claude-code: 39,
  pi: 34, hermes: 34, deepseek-harness: 28

Hard constraint: NEVER commit result JSON. Guardrails: OMP=8, workers=1.
Does NOT touch running predict processes (eval is separate from predict).
CPU monitor: eval container processes checked for >8000% pcpu (per 2026-11-02 directive).
"""
import json, os, glob, subprocess, time, sys

HARNESSES = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
PRED_DIR = 'predictions_glm53'
EVAL_REPORT_DIR = 'reports'

os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'

ds = os.path.join(os.path.dirname(__file__), 'enriched_500.json')
t0 = time.time()

for h in HARNESSES:
    print(f'\n{"="*60}', flush=True)
    print(f'=== {h}: incr_eval R1992 ===', flush=True)

    # Find all real predictions
    all_preds = []
    pred_instances = set()
    for pf in sorted(glob.glob(f'{PRED_DIR}/{h}__*.json')):
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
    eval_file = os.path.join(EVAL_REPORT_DIR, f'eval_glm53_{h}.json')
    evaluated = set()
    try:
        ed = json.load(open(eval_file))
        evaluated = set(ed.get('resolved', [])) | set(ed.get('unresolved', [])) | set(ed.get('errored', []))
    except:
        pass

    backlog = sorted(pred_instances - evaluated)
    if not backlog:
        print(f'  {h}: no backlog, skipping', flush=True)
        continue

    print(f'  {h}: {len(backlog)} new instances to eval (total real preds: {len(pred_instances)}, already evaluated: {len(evaluated)})', flush=True)

    # Merge predictions (only real patches)
    merged = f'{PRED_DIR}/predictions_{h}_glm53.json'
    open(merged, 'w').write(json.dumps(all_preds, indent=2))
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: merged {len(all_preds)} -> {merged}', flush=True)

    # Run eval for backlog only
    run_id = f'verified_full_glm53_{h}_incr_R1992'
    cmd = (f'python3 -m swebench.harness.run_evaluation --predictions_path {merged} '
           f'--dataset_name {ds} --split test --instance_ids {" ".join(backlog)} '
           f'--max_workers 1 --run_id {run_id} --timeout 1800')
    print(f'  [{time.strftime("%H:%M:%S")}] {h}: launching eval (workers=1, timeout=1800, {len(backlog)} instances)...', flush=True)
    try:
        proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True, timeout=7200)
        logf = f'logs/eval_incr_verified_full_glm53_{h}_R1992.log'
        open(logf, 'w').write(proc.stdout + '\n[stderr]\n' + proc.stderr)
        print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval done rc={proc.returncode} (log: {logf})', flush=True)
    except subprocess.TimeoutExpired:
        print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval TIMEOUT (7200s)', flush=True)
    except Exception as e:
        print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval ERROR: {e}', flush=True)

    # Regenerate eval summary
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
            'harness': h.replace('-patched', ''),
            'harness_code': h,
            'run_id': run_id,
            'n': len(all_resolved) + len(all_unresolved) + len(all_errored),
            'resolved': all_resolved,
            'unresolved': all_unresolved,
            'errored': all_errored,
        }
        json.dump(summary, open(eval_file, 'w'), indent=2)
        print(f'  [{time.strftime("%H:%M:%S")}] {h}: eval summary updated: {len(all_resolved)}/{summary["n"]} resolved ({100*len(all_resolved)/max(summary["n"],1):.1f}%)', flush=True)
    except Exception as e:
        print(f'  [{time.strftime("%H:%M:%S")}] {h}: summary update ERROR: {e}', flush=True)

elapsed = time.time() - t0
print(f'\n{"="*60}', flush=True)
print(f'R1992 incr_eval complete in {elapsed:.0f}s ({elapsed/60:.1f}min)', flush=True)
