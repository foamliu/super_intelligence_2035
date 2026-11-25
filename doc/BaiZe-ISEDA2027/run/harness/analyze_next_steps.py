#!/usr/bin/env python3
"""Comprehensive analysis of kimi_pilot_results.json for next-step planning."""
import json
from collections import defaultdict

data = json.load(open('kimi_pilot_results.json'))
print(f'Total entries: {len(data)}')

# The 30-instance pilot subset (used by all 7 harnesses)
cline_insts = sorted(set(e['instance_id'] for e in data if e['harness'] == 'cline-patched'))
subset_data = [e for e in data if e['instance_id'] in set(cline_insts)]
print(f'Subset entries (30-inst x 7 harness): {len(subset_data)}')
print(f'Instances: {len(cline_insts)} (django={sum(1 for i in cline_insts if "django" in i)}, sympy={sum(1 for i in cline_insts if "sympy" in i)})')

# Per-harness stats on 30-instance subset
harness_stats = defaultdict(lambda: {'resolved': 0, 'pbf': 0, 'quota': 0, 'other': 0, 'total': 0, 'wall_s': []})
for e in subset_data:
    h = e['harness']
    harness_stats[h]['total'] += 1
    cls = e.get('classification', '')
    hr = e.get('harness_result', {})
    if hr.get('quota_blocked'):
        harness_stats[h]['quota'] += 1
    elif cls == 'resolved':
        harness_stats[h]['resolved'] += 1
    else:
        harness_stats[h]['pbf'] += 1
    if hr.get('wall_s'):
        harness_stats[h]['wall_s'].append(hr['wall_s'])

print('\n=== 30-instance subset per-harness ===')
for h in sorted(harness_stats):
    s = harness_stats[h]
    avg_wall = sum(s['wall_s']) / len(s['wall_s']) if s['wall_s'] else 0
    rate = s['resolved'] / s['total'] * 100 if s['total'] else 0
    print(f'  {h:20s} total={s["total"]:3d} res={s["resolved"]:3d} pbf={s["pbf"]:3d} quota={s["quota"]:3d} other={s["other"]:3d} rate={rate:.1f}% avg_wall={avg_wall:.0f}s')

# Classification breakdown
cls_count = defaultdict(int)
for e in subset_data:
    cls_count[e.get('classification', 'unknown')] += 1
print('\n=== Classification breakdown (210 subset) ===')
for c, n in sorted(cls_count.items(), key=lambda x: -x[1]):
    print(f'  {c:25s} {n:4d} ({n/210*100:.1f}%)')

# Instance-level
inst_results = defaultdict(dict)
for e in subset_data:
    inst_results[e['instance_id']][e['harness']] = (e.get('classification') == 'resolved')
all_pass = sum(1 for v in inst_results.values() if all(v.values()))
none_pass = sum(1 for v in inst_results.values() if not any(v.values()))
some_pass = len(inst_results) - all_pass - none_pass
print(f'\n=== Instance-level (30 instances, 7 harnesses) ===')
print(f'  ALL 7 resolved: {all_pass}')
print(f'  NONE resolved:  {none_pass}')
print(f'  SOME (1-6):     {some_pass}')

# Per-repo per-harness
repo_harness = defaultdict(lambda: defaultdict(lambda: {'resolved': 0, 'total': 0}))
for e in subset_data:
    repo_harness[e['repo']][e['harness']]['total'] += 1
    if e.get('classification') == 'resolved':
        repo_harness[e['repo']][e['harness']]['resolved'] += 1
print('\n=== Per-repo per-harness ===')
for repo in sorted(repo_harness):
    print(f'\n{repo}:')
    for h in sorted(repo_harness[repo]):
        s = repo_harness[repo][h]
        rate = s['resolved'] / s['total'] * 100 if s['total'] else 0
        print(f'  {h:20s} {s["resolved"]}/{s["total"]} = {rate:.1f}%')

# Wall time per harness
print('\n=== Wall time per harness (30-inst subset) ===')
for h in sorted(harness_stats):
    walls = sorted(harness_stats[h]['wall_s'])
    if walls:
        total = sum(walls)
        print(f'  {h:20s} min={walls[0]:.0f}s max={walls[-1]:.0f}s avg={sum(walls)/len(walls):.0f}s med={walls[len(walls)//2]:.0f}s total={total:.0f}s ({total/60:.1f}min)')

# Failure mode: for non-resolved, check eval details
print('\n=== Failure detail (non-resolved, non-quota) ===')
fail_detail = defaultdict(lambda: defaultdict(int))
for e in subset_data:
    if e.get('classification') != 'resolved' and not e.get('harness_result', {}).get('quota_blocked'):
        h = e['harness']
        hr = e.get('harness_result', {})
        ev = hr.get('eval', {})
        if ev.get('patch_applied') == False:
            fail_detail[h]['no-patch-applied'] += 1
        elif ev.get('f2p_pass', 0) < ev.get('f2p_total', 1):
            fail_detail[h]['f2p-fail'] += 1
        elif ev.get('p2p_pass', 0) < ev.get('p2p_total', 1):
            fail_detail[h]['p2p-fail'] += 1
        elif ev.get('resolved') == False and ev.get('patch_applied'):
            fail_detail[h]['wrong-fix'] += 1
        else:
            fail_detail[h]['other-fail'] += 1
        # Check returncode
        if hr.get('returncode', 0) != 0:
            fail_detail[h]['nonzero-rc'] += 1
for h in sorted(fail_detail):
    print(f'  {h:20s} {dict(fail_detail[h])}')

# Patch overlap: for instances where multiple harnesses resolved, check if patches are similar
print('\n=== Instance resolution pattern (which instances are easy/hard) ===')
for inst in sorted(inst_results):
    res_count = sum(1 for v in inst_results[inst].values() if v)
    total_h = len(inst_results[inst])
    if res_count == 0 or res_count == total_h:
        who = 'ALL' if res_count == total_h else 'NONE'
        print(f'  {inst:40s} {res_count}/{total_h} ({who})')
