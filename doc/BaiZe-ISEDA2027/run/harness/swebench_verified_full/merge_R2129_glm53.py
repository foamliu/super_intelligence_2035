#!/usr/bin/env python3
"""R2129 merger: merge already-completed R2129 docker eval report.json into
eval_glm53_{h}.json WITHOUT re-running docker eval (incr_eval_R2129.sh already
ran the swebench harness; only the glm53 summary merge was missing)."""
import json, os, glob

BASE = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE, 'reports')
PRED_DIR = os.path.join(BASE, 'predictions_glm53')
ROUND = 'R2129'
MODEL_SUFFIX = 'glm-5.3-flash'

DISPLAY = {'cline-patched': 'cline', 'deepseek-harness': 'deepseek'}
def disp(h): return DISPLAY.get(h, h)

ALL_H = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']

for h in ALL_H:
    eval_file = os.path.join(REPORT_DIR, f'eval_glm53_{h}.json')
    existing = {"resolved": [], "failed": [], "infra_or_quota": []}
    if os.path.isfile(eval_file):
        try:
            existing = json.load(open(eval_file))
        except:
            pass

    resolved = list(existing.get("resolved", []))
    failed = list(existing.get("failed", []))
    infra = list(existing.get("infra_or_quota", []))
    already = set(resolved) | set(failed) | set(infra)

    # Scan R2129 run dirs for report.json (try both disp-name and full-name model dirs)
    run_id = f"verified_full_glm53_{h}_incr_{ROUND}"
    model_dirs = [f"{disp(h)}-{MODEL_SUFFIX}", f"{h}-{MODEL_SUFFIX}"]
    new_resolved, new_failed, new_infra = 0, 0, 0
    for base_dir in ('logs/run_evaluation', 'logs/evaluation'):
        for model_dir in model_dirs:
            for rj in glob.glob(os.path.join(BASE, f'{base_dir}/{run_id}/{model_dir}/*/report.json')):
                iid = os.path.basename(os.path.dirname(rj))
                if iid in already:
                    continue
                try:
                    rep = json.loads(open(rj).read())
                    ir = rep.get(iid, rep) if isinstance(rep, dict) else {}
                    if ir.get('infra_failure', False) or not ir.get('patch_exists', True):
                        infra.append(iid); new_infra += 1
                    elif ir.get('resolved', False):
                        resolved.append(iid); new_resolved += 1
                    else:
                        failed.append(iid); new_failed += 1
                    already.add(iid)
                except Exception as e:
                    infra.append(f"{iid}({e})"); new_infra += 1
                    already.add(iid)

    # Count total real predictions
    total_real = 0
    for pf in glob.glob(os.path.join(PRED_DIR, f'{h}__*.json')):
        try:
            d = json.loads(open(pf).read())
            if isinstance(d, list):
                total_real += sum(1 for p in d if p.get('model_patch', '').strip())
            elif isinstance(d, dict) and d.get('model_patch', '').strip():
                total_real += 1
        except:
            pass

    rc = len(resolved)
    n = len(resolved) + len(failed) + len(infra)
    summary = {
        "harness": disp(h), "harness_code": h, "run_id": run_id,
        "n": n, "resolved": sorted(resolved), "failed": sorted(failed),
        "infra_or_quota": sorted(infra), "no_patch": 0,
        "total_predictions": total_real, "evaluated": n, "resolved_count": rc,
    }
    with open(eval_file, 'w') as f:
        json.dump(summary, f, indent=2)
    delta = "" if (new_resolved + new_failed + new_infra) == 0 else f" (+{new_resolved}res +{new_failed}fail +{new_infra}infra)"
    print(f"{disp(h)}: resolved={rc} failed={len(failed)} infra={len(infra)} evaluated={n} real_pred={total_real}{delta}")

print("R2129 merge done.")
