#!/usr/bin/env python3
"""Parse eval report.json for deepseek backlog and update eval report."""
import json, os, glob, time

h = 'deepseek-harness'
backlog = ['matplotlib__matplotlib-23476', 'matplotlib__matplotlib-24026']
run_id = f'verified_full_{h}'
model = f'deepseek-harness-kimi-k2.6-cloud'
ev_file = f'reports/eval_{h}.json'

ev = json.load(open(ev_file))
print(f'[parse {time.strftime("%H:%M:%S")}] BEFORE: resolved={len(ev["resolved"])} failed={len(ev["failed"])} infra={len(ev["infra_or_quota"])} no_patch={len(ev["no_patch"])} n={ev["n"]}', flush=True)

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
        if iid in ev.get('no_patch', []):
            ev['no_patch'].remove(iid)
        if iid in ev.get('failed', []):
            ev['failed'].remove(iid)
        if iid in ev.get('infra_or_quota', []):
            ev['infra_or_quota'].remove(iid)
        if iid not in ev.get('resolved', []):
            if resolved:
                ev['resolved'].append(iid)
            else:
                ev['failed'].append(iid)
        print(f'[parse {time.strftime("%H:%M:%S")}] {iid}: {status}', flush=True)
    else:
        print(f'[parse {time.strftime("%H:%M:%S")}] {iid}: NO REPORT YET (still running?)', flush=True)

ev['n'] = len(ev['resolved']) + len(ev['failed']) + len(ev['infra_or_quota']) + len(ev['no_patch'])
open(ev_file, 'w').write(json.dumps(ev, indent=2))
print(f'[parse {time.strftime("%H:%M:%S")}] AFTER: resolved={len(ev["resolved"])} failed={len(ev["failed"])} infra={len(ev["infra_or_quota"])} no_patch={len(ev["no_patch"])} n={ev["n"]}', flush=True)
