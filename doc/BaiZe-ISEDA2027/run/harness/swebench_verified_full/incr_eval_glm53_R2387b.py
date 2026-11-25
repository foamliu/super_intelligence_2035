#!/usr/bin/env python3
"""R2387b: Merge cline results + eval cc/pi new instances."""
import json, os, glob, subprocess, time

BASE = os.path.dirname(os.path.abspath(__file__))
PRED_DIR = os.path.join(BASE, 'predictions_glm53')
REPORT_DIR = os.path.join(BASE, 'reports')
LOG_DIR = os.path.join(BASE, 'logs')
DS = os.path.join(BASE, 'enriched_500.json')
DISPLAY = {'cline-patched': 'cline', 'deepseek-harness': 'deepseek'}
MODEL_SUFFIX = 'glm-5.3-flash'
ROUND = 'R2387b'
MAX_WORKERS = 4
os.environ['OMP_NUM_THREADS'] = '8'
t0 = time.time()

def disp(h): return DISPLAY.get(h, h)
def log(m): print(f"[R2387b {time.strftime('%H:%M:%S')}] {m}", flush=True)

def load_eval(h):
    ef = os.path.join(REPORT_DIR, f'eval_glm53_{h}.json')
    if os.path.isfile(ef):
        try: return json.load(open(ef))
        except: pass
    return {"resolved": [], "failed": [], "infra_or_quota": []}

def save_eval(h, s):
    with open(os.path.join(REPORT_DIR, f'eval_glm53_{h}.json'), 'w') as f:
        json.dump(s, f, indent=2)

def count_real(h):
    preds = []
    for pf in sorted(glob.glob(os.path.join(PRED_DIR, f'{h}__*.json'))):
        try:
            p = json.loads(open(pf).read())
            if isinstance(p, dict): p = [p]
            preds.extend(x for x in p if x.get('model_patch', '').strip())
        except: pass
    return preds

def parse_report(run_id, model_dir, iid):
    for bd in ('logs/run_evaluation', 'logs/evaluation'):
        rj = os.path.join(BASE, f'{bd}/{run_id}/{model_dir}/{iid}/report.json')
        if os.path.exists(rj) and os.path.getsize(rj) > 10:
            try:
                rep = json.loads(open(rj).read())
                ir = rep.get(iid, rep) if isinstance(rep, dict) else {}
                return ir.get('resolved', False)
            except: return None
    return None

def finalize(h, existing, all_preds):
    rc = len(existing.get("resolved", []))
    n = rc + len(existing.get("failed", [])) + len(existing.get("infra_or_quota", []))
    existing["resolved_count"] = rc
    existing["total_predictions"] = len(all_preds)
    existing["evaluated"] = n
    existing["no_patch"] = 0
    save_eval(h, existing)
    return rc, n

# ---- Step 1: Merge cline results from existing report.json ----
log("=== Step 1: Merge cline results ===")
h = 'cline-patched'
ex = load_eval(h)
already = set(ex.get("resolved",[]) + ex.get("failed",[]) + ex.get("infra_or_quota",[]))
ap = count_real(h)
with open(os.path.join(PRED_DIR, f'predictions_{h}.json'), 'w') as f:
    json.dump(ap, f, indent=2)
for iid in ['django__django-13569','django__django-13590','django__django-13658']:
    if iid in already: continue
    res = parse_report('verified_full_glm53_cline-patched_incr_R2387','cline-glm-5.3-flash',iid)
    if res is True: ex.setdefault("resolved",[]).append(iid); log(f"  cline {iid}: RESOLVED")
    elif res is False: ex.setdefault("failed",[]).append(iid); log(f"  cline {iid}: FAILED")
    else: ex.setdefault("infra_or_quota",[]).append(iid); log(f"  cline {iid}: INFRA")
rc,n = finalize(h, ex, ap)
log(f"  cline: resolved={rc} total={n}")

# ---- Step 2: Eval cc (3 new) and pi (4 new) ----
for h in ['claude-code', 'pi']:
    log(f"=== Step 2: Eval {disp(h)} ===")
    ex = load_eval(h)
    already = set(ex.get("resolved",[]) + ex.get("failed",[]) + ex.get("infra_or_quota",[]))
    ap = count_real(h)
    with open(os.path.join(PRED_DIR, f'predictions_{h}.json'), 'w') as f:
        json.dump(ap, f, indent=2)
    new_preds = [p for p in ap if p.get('instance_id','') not in already]
    log(f"  {disp(h)}: {len(ap)} total real, {len(new_preds)} new")
    if not new_preds:
        rc,n = finalize(h, ex, ap); log(f"  {disp(h)}: no new, skip"); continue
    nm = os.path.join(PRED_DIR, f'predictions_{h}_new_{ROUND}.json')
    with open(nm, 'w') as f: json.dump(new_preds, f, indent=2)
    eval_ids = [p['instance_id'] for p in new_preds]
    md = f"{disp(h)}-{MODEL_SUFFIX}"
    rid = f"verified_full_glm53_{h}_incr_{ROUND}"
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {nm} --dataset_name {DS} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers {MAX_WORKERS} "
           f"--run_id {rid} --timeout 1800")
    log(f"  {disp(h)}: eval {len(eval_ids)} instances: {eval_ids}")
    try:
        proc = subprocess.run(['sg','docker','-c',cmd], capture_output=True, text=True,
                              timeout=1800*len(eval_ids)+600)
        with open(os.path.join(LOG_DIR, f'eval_glm53_{h}_{ROUND}.log'), 'w') as f:
            f.write(proc.stdout + '\n[stderr]\n' + proc.stderr)
        log(f"  {disp(h)}: eval done rc={proc.returncode}")
    except subprocess.TimeoutExpired:
        log(f"  {disp(h)}: TIMEOUT"); os.remove(nm) if os.path.exists(nm) else None; continue
    except Exception as e:
        log(f"  {disp(h)}: ERROR: {e}"); os.remove(nm) if os.path.exists(nm) else None; continue
    for iid in eval_ids:
        res = parse_report(rid, md, iid)
        if res is True: ex.setdefault("resolved",[]).append(iid); log(f"  {disp(h)} {iid}: RESOLVED")
        elif res is False: ex.setdefault("failed",[]).append(iid); log(f"  {disp(h)} {iid}: FAILED")
        else: ex.setdefault("infra_or_quota",[]).append(iid); log(f"  {disp(h)} {iid}: INFRA")
    rc,n = finalize(h, ex, ap)
    log(f"  {disp(h)}: resolved={rc} total={n}")
    if os.path.exists(nm): os.remove(nm)

# ---- Step 3: Refresh other harnesses ----
for h in ['codex','opencode','hermes','deepseek-harness']:
    ex = load_eval(h)
    ap = count_real(h)
    with open(os.path.join(PRED_DIR, f'predictions_{h}.json'), 'w') as f:
        json.dump(ap, f, indent=2)
    rc,n = finalize(h, ex, ap)
    log(f"  {disp(h)}: refreshed resolved={rc} total={n}")

log(f"\nR2387b done in {time.time()-t0:.1f}s")
