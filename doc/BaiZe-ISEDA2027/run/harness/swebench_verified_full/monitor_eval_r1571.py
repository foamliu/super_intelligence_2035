#!/usr/bin/env python3
"""Monitor docker eval containers, wait for finish, then parse results."""
import subprocess, time, os, json, glob, sys

h = 'deepseek-harness'
backlog = ['matplotlib__matplotlib-23476', 'matplotlib__matplotlib-24026']
run_id = f'verified_full_{h}'
model = f'deepseek-harness-kimi-k2.6-cloud'
ev_file = f'reports/eval_{h}.json'
logfile = 'reports/incr_eval_R1571.log'

def log(msg):
    line = f'[monitor {time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(logfile, 'a') as f:
        f.write(line + '\n')

log('=== Waiting for docker eval containers to finish ===')

# Wait for docker containers to finish (max 30 min)
max_wait = 1800
t0 = time.time()
while time.time() - t0 < max_wait:
    result = subprocess.run(['sg', 'docker', '-c', 'docker ps --format "{{.Names}}"'],
                          capture_output=True, text=True, timeout=30)
    containers = [c.strip() for c in result.stdout.strip().split('\n') if c.strip() and 'sweb.eval' in c and 'deepseek' in c]
    if not containers:
        log('All deepseek eval containers finished!')
        break
    elapsed = int(time.time() - t0)
    log(f'Still waiting: {len(containers)} containers up ({elapsed}s elapsed): {containers}')
    time.sleep(30)

# Now parse results
log('=== Parsing eval results ===')
ev = json.load(open(ev_file))
log(f'BEFORE: resolved={len(ev["resolved"])} failed={len(ev["failed"])} infra={len(ev["infra_or_quota"])} no_patch={len(ev["no_patch"])} n={ev["n"]}')

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
        log(f'{iid}: {status}')
    else:
        ev['infra_or_quota'].append(iid)
        log(f'{iid}: INFRA (no report.json)')

ev['n'] = len(ev['resolved']) + len(ev['failed']) + len(ev['infra_or_quota']) + len(ev['no_patch'])
open(ev_file, 'w').write(json.dumps(ev, indent=2))
log(f'AFTER: resolved={len(ev["resolved"])} failed={len(ev["failed"])} infra={len(ev["infra_or_quota"])} no_patch={len(ev["no_patch"])} n={ev["n"]}')
log('=== DONE ===')
