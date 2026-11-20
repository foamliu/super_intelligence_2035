#!/usr/bin/env python3
"""Incr eval R1613 summary update: merge swebench results into reports/eval_cline-patched.json.

  cline-patched: sphinx-doc__sphinx-8548 (FAILED per swebench report)

Eval already run by incr_eval_1route_R1613.sh (docker harness). This script
only parses report.json and updates the eval_*.json summaries (same logic as
incr_eval_r1611.py). Hard constraint: NEVER commit result JSON.
"""
import json, os, glob, time

t0 = time.time()
print(f'[incr-eval {time.strftime("%H:%M:%S")}] === R1613 summary update START ===', flush=True)

backlog_by_h = {
    'cline-patched': ['sphinx-doc__sphinx-8548'],
}
model_map = {
    'cline-patched': 'cline-kimi-k2.6-cloud',
}

for h, backlog in backlog_by_h.items():
    run_id = f'verified_full_{h}'
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
            for k in ('no_patch', 'failed', 'infra_or_quota'):
                if iid in ev.get(k, []):
                    ev[k].remove(iid)
            if iid not in ev.get('resolved', []):
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
    print(f'[incr-eval {time.strftime("%H:%M:%S")}] {h}: updated {ev_file}: '
          f'resolved={len(ev["resolved"])} failed={len(ev["failed"])} '
          f'infra={len(ev["infra_or_quota"])} no_patch={len(ev["no_patch"])} n={ev["n"]}', flush=True)

print(f'[incr-eval {time.strftime("%H:%M:%S")}] === R1613 summary update DONE ({time.time()-t0:.0f}s) ===', flush=True)
