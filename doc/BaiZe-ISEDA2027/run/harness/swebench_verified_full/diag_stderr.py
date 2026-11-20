#!/usr/bin/env python3
import json, sys
for h in ['opencode','pi','hermes','deepseek-harness']:
    try:
        d = json.load(open(f'reports/progress_{h}.json'))
    except Exception:
        print(f'=== {h} === (no file)')
        continue
    print(f'=== {h} (done={d["done"]}/{d["total"]} patch={d["patch_produced"]} no_patch={d["no_patch"]}) ===')
    for r in d['results']:
        iid = r['instance_id']
        rc = r.get('returncode', -1)
        wall = r.get('wall_s', 0)
        print(f'\n  [{iid}] rc={rc} wall={wall}s')
        se = r.get('stderr_tail', '')
        so = r.get('stdout_tail', '')
        if se:
            print(f'  STDERR: {se[:400]}')
        if so:
            print(f'  STDOUT: {so[:400]}')
    print()
