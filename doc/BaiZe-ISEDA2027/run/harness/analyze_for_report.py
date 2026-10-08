#!/usr/bin/env python3
"""Deep analysis of kimi_pilot_results.json for the analysis report."""
import json
from collections import defaultdict

with open('kimi_pilot_results.json') as f:
    data = json.load(f)

target_ids = set(e['instance_id'] for e in data if e.get('harness') == 'cline-patched')
data30 = [e for e in data if e['instance_id'] in target_ids]
HARNESS_ORDER = ['cline-patched', 'codex', 'opencode', 'claude-code', 'deepseek-harness', 'pi', 'hermes']

# 1. claude-code 'other' case
print('=== CLAUDE-CODE OTHER CASE ===')
for e in data30:
    if e.get('harness') == 'claude-code' and e.get('classification') not in ('resolved', 'patch-but-failed', 'quota-blocked'):
        iid = e['instance_id']
        cls = e.get('classification')
        hr = e.get('harness_result', {})
        rc = hr.get('returncode')
        wall = hr.get('wall_s')
        stdout = hr.get('stdout_tail', '')
        ev = hr.get('eval')
        print('Instance:', iid)
        print('Classification:', cls)
        print('Returncode:', rc)
        print('Wall:', wall)
        print('Stdout tail (last 500):', stdout[-500:] if stdout else '(empty)')
        print('Eval:', ev)
        print()

# 2. Timeout examples
print('=== TIMEOUT EXAMPLES (wall >= 1790, rc=1) ===')
count = 0
for e in data30:
    hr = e.get('harness_result', {})
    if hr.get('wall_s', 0) >= 1790 and hr.get('returncode') == 1:
        h = e['harness']
        iid = e['instance_id']
        wall = hr['wall_s']
        rc = hr['returncode']
        stdout = hr.get('stdout_tail', '')
        print(f'{h} / {iid}: wall={wall}s rc={rc}')
        if stdout:
            print(f'  ...{stdout[-200:]}')
        print()
        count += 1
        if count >= 3:
            break

# 3. f2p_fail_only example
print('=== EXAMPLE: f2p_fail_only ===')
for e in data30:
    if e.get('classification') == 'patch-but-failed':
        ev = e.get('harness_result', {}).get('eval', {})
        if ev.get('f2p_pass', 0) < ev.get('f2p_total', 0) and ev.get('p2p_pass', 0) >= ev.get('p2p_total', 0):
            h = e['harness']
            iid = e['instance_id']
            f2p = f'{ev.get("f2p_pass", 0)}/{ev.get("f2p_total", 0)}'
            p2p = f'{ev.get("p2p_pass", 0)}/{ev.get("p2p_total", 0)}'
            print(f'{h} / {iid}: f2p={f2p} p2p={p2p}')
            stdout = e.get('harness_result', {}).get('stdout_tail', '')
            if 'model_patch:' in stdout:
                ps = stdout.split('model_patch:')[1].split('bytes')[0].strip()
                print(f'  patch_size={ps} bytes')
            break

# 4. Nobody solved / everybody solved
inst_results = defaultdict(dict)
for e in data30:
    inst_results[e['instance_id']][e['harness']] = e.get('classification')

print('\n=== INSTANCE NOBODY SOLVED (0/7 resolved) ===')
nobody = [iid for iid, r in sorted(inst_results.items()) if sum(1 for v in r.values() if v == 'resolved') == 0]
print(f'Count: {len(nobody)}/30')
for iid in nobody:
    print(f'  {iid}')

print('\n=== INSTANCE EVERYBODY SOLVED (7/7 resolved) ===')
everybody = [iid for iid, r in sorted(inst_results.items()) if sum(1 for v in r.values() if v == 'resolved') == 7]
print(f'Count: {len(everybody)}/30')
for iid in everybody:
    print(f'  {iid}')

# 5. Per-harness wall time stats for cost analysis
print('\n=== WALL TIME STATS ===')
for h in HARNESS_ORDER:
    entries = [e for e in data30 if e.get('harness') == h]
    walls = [e.get('harness_result', {}).get('wall_s', 0) for e in entries if isinstance(e.get('harness_result', {}).get('wall_s'), (int, float))]
    total_wall = sum(walls)
    avg = total_wall / len(walls) if walls else 0
    print(f'{h}: total={total_wall:.0f}s avg={avg:.0f}s count={len(walls)}')

# 6. Correlation: avg patch size vs resolve rate
print('\n=== PATCH SIZE vs RESOLVE RATE ===')
for h in HARNESS_ORDER:
    entries = [e for e in data30 if e.get('harness') == h]
    resolved = sum(1 for e in entries if e.get('classification') == 'resolved')
    patch_sizes = []
    for e in entries:
        stdout = e.get('harness_result', {}).get('stdout_tail', '')
        if 'model_patch:' in stdout:
            try:
                ps = stdout.split('model_patch:')[1].split('bytes')[0].strip()
                patch_sizes.append(int(ps))
            except:
                pass
    avg_ps = sum(patch_sizes) / len(patch_sizes) if patch_sizes else 0
    print(f'{h}: resolve_rate={resolved}/30 avg_patch={avg_ps:.0f}B')
