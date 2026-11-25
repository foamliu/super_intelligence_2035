#!/usr/bin/env python3
"""Quick progress check for 7x300 run."""
import json
from collections import Counter, defaultdict

with open('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/kimi_pilot_results.json') as f:
    data = json.load(f)

classifications = Counter(r.get('classification', '?') for r in data)
print('=== TOTAL RESULTS ===')
print(f'Total entries: {len(data)}')
for c, n in sorted(classifications.items()):
    print(f'  {c}: {n}')

# Count wall>0 (new runs) vs wall=0 (resumed/pre-existing)
wall_pos = sum(1 for r in data if r.get('harness_result', {}).get('wall_s', 0) > 0)
wall_zero = len(data) - wall_pos
print(f'\nwall>0 (new runs): {wall_pos}')
print(f'wall=0 (resumed/pre-existing): {wall_zero}')

# New blocked = blocked with wall>0
new_blocked = [r for r in data if 'block' in str(r.get('classification', '')) and r.get('harness_result', {}).get('wall_s', 0) > 0]
print(f'NEW blocked (wall>0): {len(new_blocked)}')

print('\n=== PER-HARNESS ===')
hs = defaultdict(lambda: {'total': 0, 'resolved': 0, 'pbf': 0, 'blocked': 0, 'wall0': 0, 'wall_pos': 0})
for r in data:
    h = r.get('harness', '?')
    c = r.get('classification', '?')
    hr = r.get('harness_result', {})
    wall = hr.get('wall_s', 0) if isinstance(hr, dict) else 0
    hs[h]['total'] += 1
    if c == 'resolved':
        hs[h]['resolved'] += 1
    elif 'patch' in c and 'fail' in c:
        hs[h]['pbf'] += 1
    elif 'block' in c:
        hs[h]['blocked'] += 1
    if wall == 0:
        hs[h]['wall0'] += 1
    else:
        hs[h]['wall_pos'] += 1

for h in sorted(hs.keys()):
    st = hs[h]
    pct = 100 * st['resolved'] / st['total'] if st['total'] > 0 else 0
    print(f'  {h:20s} total={st["total"]:4d} res={st["resolved"]:4d} pbf={st["pbf"]:4d} '
          f'blk={st["blocked"]:4d} wall0={st["wall0"]:4d} wall>0={st["wall_pos"]:4d} rate={pct:.1f}%')

# Remaining = 2100 - total
total = len(data)
print(f'\nProgress: {total}/2100 ({100*total/2100:.1f}%)')
print(f'Remaining: {2100 - total}')
