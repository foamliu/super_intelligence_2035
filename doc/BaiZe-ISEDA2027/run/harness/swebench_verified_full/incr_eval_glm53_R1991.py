#!/usr/bin/env python3
"""R1991 incremental eval: only eval NEW real patches not yet evaluated."""
import json, os, glob, subprocess, time, sys

BASE = os.path.dirname(os.path.abspath(__file__))
PRED_DIR = os.path.join(BASE, 'predictions_glm53')
REPORT_DIR = os.path.join(BASE, 'reports')
LOG_DIR = os.path.join(BASE, 'logs')
DS = os.path.join(BASE, 'enriched_500.json')
ALL_H = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
DISPLAY = {'cline-patched': 'cline', 'deepseek-harness': 'deepseek'}
MODEL_SUFFIX = 'glm-5.3-flash'
RUN_TAG = 'R1991'
os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
t0 = time.time()

def disp(h):
    return DISPLAY.get(h, h)

def log(m):
    print(f"[R1991-eval {time.strftime('%H:%M:%S')}] {m}", flush=True)

for h in ALL_H:
    eval_file = os.path.join(REPORT_DIR, f'eval_glm53_{h}.json')
    existing = {"resolved": [], "failed": [], "infra_or_quota": [], "no_patch": []}
    already_evaluated = set()
    if os.path.isfile(eval_file):
        try:
            existing = json.load(open(eval_file))
            already_evaluated = set(existing.get("resolved", []) + existing.get("failed", []) + existing.get("infra_or_quota", []))
        except:
            pass
    log(f"{disp(h)}: {len(already_evaluated)} already evaluated")
    all_preds = []
    no_patch_ids = list(existing.get("no_patch", []))
    for pf in sorted(glob.glob(os.path.join(PRED_DIR, f'{h}__*.json'))):
        try:
            preds = json.loads(open(pf).read())
            if isinstance(preds, dict):
                preds = [preds]
            for p in preds:
                iid = p.get('instance_id', '')
                if p.get('model_patch', '').strip():
                    all_preds.append(p)
                elif iid and iid not in no_patch_ids:
                    no_patch_ids.append(iid)
        except:
            pass
    new_preds = [p for p in all_preds if p.get('instance_id', '') not in already_evaluated]
    merged = os.path.join(PRED_DIR, f'predictions_{h}.json')
    with open(merged, 'w') as f:
        json.dump(all_preds, f, indent=2)
    log(f"{disp(h)}: {len(all_preds)} total real, {len(new_preds)} new, {len(no_patch_ids)} no_patch")

    def write_summary(resolved_l, failed_l, infra_l):
        summary = {"harness": disp(h), "harness_code": h, "run_id": f"verified_full_glm53_{h}_{RUN_TAG}",
                   "n": len(resolved_l) + len(failed_l) + len(infra_l),
                   "resolved": resolved_l, "failed": failed_l, "infra_or_quota": infra_l,
                   "no_patch": no_patch_ids, "total_predictions": len(all_preds) + len(no_patch_ids),
                   "evaluated": len(resolved_l) + len(failed_l) + len(infra_l),
                   "resolved_count": len(resolved_l)}
        with open(eval_file, 'w') as f:
            json.dump(summary, f, indent=2)
        log(f"{disp(h)}: MERGED resolved={len(resolved_l)} failed={len(failed_l)} infra={len(infra_l)} -> {eval_file}")

    if not new_preds:
        log(f"{disp(h)}: no new instances to eval, updating summary only")
        r_l = existing.get("resolved", [])
        f_l = existing.get("failed", [])
        i_l = [x for x in existing.get("infra_or_quota", []) if '(' not in str(x)]
        write_summary(r_l, f_l, i_l)
        continue

    new_merged = os.path.join(PRED_DIR, f'predictions_{h}_new_{RUN_TAG}.json')
    with open(new_merged, 'w') as f:
        json.dump(new_preds, f, indent=2)
    eval_ids = [p['instance_id'] for p in new_preds]
    model_dir = f"{disp(h)}-{MODEL_SUFFIX}"
    run_id = f"verified_full_glm53_{h}_{RUN_TAG}"
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {new_merged} --dataset_name {DS} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers 1 "
           f"--run_id {run_id} --timeout 1800")
    log(f"{disp(h)}: launching eval on {len(eval_ids)} NEW instances...")
    try:
        proc = subprocess.run(['sg', 'docker', '-c', cmd], capture_output=True, text=True,
                              timeout=1800 * len(eval_ids) + 600)
        logf = os.path.join(LOG_DIR, f'eval_glm53_{h}_{RUN_TAG}.log')
        with open(logf, 'w') as f:
            f.write(proc.stdout + '\n[stderr]\n' + proc.stderr)
        log(f"{disp(h)}: eval done rc={proc.returncode}")
    except subprocess.TimeoutExpired:
        log(f"{disp(h)}: eval TIMEOUT"); continue
    except Exception as e:
        log(f"{disp(h)}: eval ERROR: {e}"); continue

    new_resolved = list(existing.get("resolved", []))
    new_failed = list(existing.get("failed", []))
    new_infra = [x for x in existing.get("infra_or_quota", []) if '(' not in str(x)]
    for iid in eval_ids:
        rj = None
        for base_dir in ('logs/run_evaluation', 'logs/evaluation'):
            for c in glob.glob(os.path.join(BASE, f'{base_dir}/{run_id}/{model_dir}/{iid}/report.json')):
                rj = c; break
            if rj: break
        if rj and os.path.exists(rj):
            try:
                rep = json.loads(open(rj).read())
                ir = rep.get(iid, rep) if isinstance(rep, dict) else {}
                if ir.get('resolved', False):
                    new_resolved.append(iid)
                else:
                    new_failed.append(iid)
            except Exception as e:
                new_infra.append(f"{iid}({e})")
        else:
            new_infra.append(iid)
    write_summary(new_resolved, new_failed, new_infra)
    try:
        os.remove(new_merged)
    except:
        pass

log(f"\nR1991 eval done in {time.time()-t0:.1f}s", flush=True)
