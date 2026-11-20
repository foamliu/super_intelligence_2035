#!/usr/bin/env python3
"""Incr eval R1789: glm-5.3-flash SWE-bench Verified incremental eval.

Evaluates all available real-patch predictions for each harness.
Predictions are in predictions_glm53/ (not predictions/).
Model dir name = {harness}-glm-5.3-flash.

Hard constraint: NEVER commit result JSON. Guardrails: OMP=8, workers=1.
Does NOT touch running predict processes (eval is separate from predict).
CPU monitor: eval container processes checked for >8000% pcpu (per 2026-11-02 directive).
"""
import json, os, glob, subprocess, time, sys

PRED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'predictions_glm53')
REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
EVAL_LOG_ROOT = os.path.join(LOG_DIR, 'run_evaluation')
DS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'enriched_500.json')

ALL_H = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
DISPLAY = {'cline-patched': 'cline'}
MODEL_SUFFIX = 'glm-5.3-flash'

os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'

t0 = time.time()

def disp(h):
    return DISPLAY.get(h, h)

def log(m):
    print(f"[R1789-eval {time.strftime('%H:%M:%S')}] {m}", flush=True)

for h in ALL_H:
    # 1. Merge predictions
    all_preds = []
    for pf in sorted(glob.glob(os.path.join(PRED_DIR, f'{h}__*.json'))):
        try:
            preds = json.loads(open(pf).read())
            if isinstance(preds, dict):
                preds = [preds]
            preds = [p for p in preds if p.get('model_patch', '').strip()]
            all_preds.extend(preds)
        except:
            pass
    merged = os.path.join(PRED_DIR, f'predictions_{h}.json')
    with open(merged, 'w') as f:
        json.dump(all_preds, f, indent=2)
    log(f"{disp(h)}: merged {len(all_preds)} real patches -> {merged}")

    if not all_preds:
        log(f"{disp(h)}: no real patches, skipping eval")
        continue

    eval_ids = [p['instance_id'] for p in all_preds]
    model_dir = f"{disp(h)}-{MODEL_SUFFIX}"
    run_id = f"verified_full_glm53_{h}_R1789"

    # 2. Run eval via sg docker
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {DS} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers 1 "
           f"--run_id {run_id} --timeout 1800")
    log(f"{disp(h)}: launching eval on {len(eval_ids)} instances (workers=1, timeout=1800, run_id={run_id})...")

    try:
        proc = subprocess.run(['sg', 'docker', '-c', cmd],
                              capture_output=True, text=True,
                              timeout=1800 * len(eval_ids) + 600)
        logf = os.path.join(LOG_DIR, f'eval_glm53_{h}_R1789.log')
        with open(logf, 'w') as f:
            f.write(proc.stdout + '\n[stderr]\n' + proc.stderr)
        log(f"{disp(h)}: eval done rc={proc.returncode}; log -> {logf}")
    except subprocess.TimeoutExpired:
        log(f"{disp(h)}: eval TIMEOUT")
        continue
    except Exception as e:
        log(f"{disp(h)}: eval ERROR: {e}")
        continue

    # 3. Parse results
    summary = {"harness": disp(h), "harness_code": h, "run_id": run_id,
               "n": len(eval_ids), "resolved": [], "failed": [], "infra_or_quota": []}
    for iid in eval_ids:
        rj = None
        for base in ('logs/run_evaluation', 'logs/evaluation'):
            for c in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            f'{base}/{run_id}/{model_dir}/{iid}/report.json')):
                rj = c
                break
            if rj:
                break
        if rj and os.path.exists(rj):
            try:
                rep = json.loads(open(rj).read())
                ir = rep.get(iid, rep) if isinstance(rep, dict) else {}
                resolved = ir.get('resolved', False)
                summary['resolved' if resolved else 'failed'].append(iid)
            except Exception as e:
                summary['infra_or_quota'].append(f"{iid}({e})")
        else:
            summary['infra_or_quota'].append(iid)

    report_file = os.path.join(REPORT_DIR, f'eval_glm53_{h}.json')
    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2)
    log(f"{disp(h)}: resolved={len(summary['resolved'])} failed={len(summary['failed'])} "
        f"infra={len(summary['infra_or_quota'])} -> {report_file}")

log(f"\nR1789 eval done in {time.time()-t0:.1f}s", flush=True)
