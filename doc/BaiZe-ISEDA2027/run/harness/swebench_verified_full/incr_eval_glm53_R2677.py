#!/usr/bin/env python3
"""R2677 incremental eval: only eval NEW real patches not yet evaluated."""
import json, os, glob, subprocess, time, sys

BASE = os.path.dirname(os.path.abspath(__file__))
PRED_DIR = os.path.join(BASE, 'predictions_glm53')
REPORT_DIR = os.path.join(BASE, 'reports')
LOG_DIR = os.path.join(BASE, 'logs')
DS = os.path.join(BASE, 'enriched_500.json')

ALL_H = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
DISPLAY = {'cline-patched': 'cline', 'deepseek-harness': 'deepseek'}
MODEL_SUFFIX = 'glm-5.3-flash'
RID = 'R2677'

os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'

t0 = time.time()

def disp(h):
    return DISPLAY.get(h, h)

def log(m):
    print(f"[{RID}-eval {time.strftime('%H:%M:%S')}] {m}", flush=True)

for h in ALL_H:
    eval_file = os.path.join(REPORT_DIR, f'eval_glm53_{h}.json')
    existing = {"resolved": [], "failed": [], "infra_or_quota": []}
    already_evaluated = set()
    if os.path.isfile(eval_file):
        try:
            existing = json.load(open(eval_file))
            already_evaluated = set(existing.get("resolved", []) + existing.get("failed", []) + existing.get("infra_or_quota", []))
        except:
            pass
    log(f"{disp(h)}: {len(already_evaluated)} already evaluated")

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

    new_preds = [p for p in all_preds if p.get('instance_id', '') not in already_evaluated]
    merged = os.path.join(PRED_DIR, f'predictions_{h}.json')
    with open(merged, 'w') as f:
        json.dump(all_preds, f, indent=2)
    log(f"{disp(h)}: {len(all_preds)} total real, {len(new_preds)} new to eval")

    if not new_preds:
        log(f"{disp(h)}: no new instances to eval, skipping")
        continue

    new_merged = os.path.join(PRED_DIR, f'predictions_{h}_new_{RID}.json')
    with open(new_merged, 'w') as f:
        json.dump(new_preds, f, indent=2)

    eval_ids = [p['instance_id'] for p in new_preds]
    model_dir = f"{disp(h)}-{MODEL_SUFFIX}"
    run_id = f"verified_full_glm53_{h}_{RID}"

    PY310 = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"
    cmd = (f"{PY310} -m swebench.harness.run_evaluation "
           f"--predictions_path {new_merged} --dataset_name {DS} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers 1 "
           f"--run_id {run_id} --timeout 1800")
    log(f"{disp(h)}: launching eval on {len(eval_ids)} NEW instances (workers=1, timeout=1800)...")
    log(f"{disp(h)}: eval_ids = {eval_ids}")

    try:
        proc = subprocess.run(['sg', 'docker', '-c', cmd],
                              capture_output=True, text=True,
                              timeout=1800 * len(eval_ids) + 600)
        logf = os.path.join(LOG_DIR, f'eval_glm53_{h}_{RID}.log')
        with open(logf, 'w') as f:
            f.write(proc.stdout + '\n[stderr]\n' + proc.stderr)
        log(f"{disp(h)}: eval done rc={proc.returncode}; log -> {logf}")
    except subprocess.TimeoutExpired:
        log(f"{disp(h)}: eval TIMEOUT")
        continue
    except Exception as e:
        log(f"{disp(h)}: eval ERROR: {e}")
        continue

    new_resolved = list(existing.get("resolved", []))
    new_failed = list(existing.get("failed", []))
    new_infra = list(existing.get("infra_or_quota", []))

    for iid in eval_ids:
        rj = None
        for base_dir in ('logs/run_evaluation', 'logs/evaluation'):
            for c in glob.glob(os.path.join(BASE, f'{base_dir}/{run_id}/{model_dir}/{iid}/report.json')):
                rj = c
                break
            if rj:
                break
        if rj and os.path.exists(rj):
            try:
                rep = json.loads(open(rj).read())
                ir = rep.get(iid, rep) if isinstance(rep, dict) else {}
                resolved = ir.get('resolved', False)
                if resolved:
                    new_resolved.append(iid)
                    log(f"  {iid}: RESOLVED")
                else:
                    new_failed.append(iid)
                    log(f"  {iid}: failed (capability)")
            except Exception as e:
                new_infra.append(f"{iid}({e})")
                log(f"  {iid}: parse error: {e}")
        else:
            new_infra.append(iid)
            log(f"  {iid}: no report.json (infra)")

    total_pred = len(glob.glob(os.path.join(PRED_DIR, f'{h}__*.json')))
    summary = {"harness": disp(h), "harness_code": h, "run_id": f"verified_full_glm53_{h}_{RID}",
               "n": len(new_resolved) + len(new_failed) + len(new_infra),
               "resolved": new_resolved, "failed": new_failed, "infra_or_quota": new_infra,
               "total_predictions": total_pred,
               "evaluated": len(new_resolved) + len(new_failed) + len([x for x in new_infra if '(' not in x]),
               "no_patch": total_pred - len(all_preds)}
    with open(eval_file, 'w') as f:
        json.dump(summary, f, indent=2)
    log(f"{disp(h)}: MERGED resolved={len(new_resolved)} failed={len(new_failed)} "
        f"infra={len(new_infra)} total_pred={total_pred} -> {eval_file}")

    try:
        os.remove(new_merged)
    except:
        pass

log(f"{RID} eval done in {time.time()-t0:.1f}s")
