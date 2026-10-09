#!/usr/bin/env python3
"""Check new blocked entries and recent results."""
import json

with open('/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/kimi_pilot_results.json') as f:
    data = json.load(f)

# New blocked (wall>0)
new_blk = [r for r in data if 'block' in str(r.get('classification', '')) and r.get('harness_result', {}).get('wall_s', 0) > 0]
print(f'=== NEW blocked (wall>0): {len(new_blk)} ===')
for r in new_blk:
    hr = r.get('harness_result', {})
    h = r.get('harness', '?')
    inst = r.get('instance_id', '?')
    repo = r.get('repo', '?')
    cls = r.get('classification', '?')
    wall = hr.get('wall_s', 0)
    print(f'  harness={h} instance={inst} repo={repo} class={cls} wall={wall:.1f}')
    print(f'  workdir_setup: {r.get("workdir_setup", {})}')
    print(f'  rootfs_setup: {r.get("rootfs_setup", {})}')
    tail = hr.get('stdout_tail', '')
    print(f'  stdout_tail (last 500): {tail[-500:]}')
    print()

# Recent results by wall_s
recent = sorted([r for r in data if r.get('harness_result', {}).get('wall_s', 0) > 0],
                key=lambda r: r['harness_result']['wall_s'], reverse=True)
print('=== Most recent 10 results (by wall_s) ===')
for r in recent[:10]:
    hr = r['harness_result']
    h = r.get('harness', '?')
    inst = r.get('instance_id', '?')
    wall = hr.get('wall_s', 0)
    cls = r.get('classification', '?')
    print(f'  {h:20s} {inst:40s} wall={wall:8.1f}s class={cls}')
