#!/usr/bin/env python3
"""Fix stale resolved_count/evaluated fields in all eval reports (R2212)."""
import json

routes = ['cline-patched', 'codex', 'opencode', 'claude-code', 'pi', 'hermes', 'deepseek-harness']
tot_res = 0
tot_eval = 0
for h in routes:
    ef = f'reports/eval_glm53_{h}.json'
    e = json.load(open(ef))
    for key in ('resolved', 'failed', 'infra_or_quota'):
        e.setdefault(key, [])
    actual_res = len(e['resolved'])
    actual_fail = len(e['failed'])
    actual_infra = len(e['infra_or_quota'])
    actual_n = actual_res + actual_fail + actual_infra
    e['resolved_count'] = actual_res
    e['evaluated'] = actual_n
    e['n'] = actual_n
    json.dump(e, open(ef, 'w'), indent=2)
    tot_res += actual_res
    tot_eval += actual_n
    print(f'  {h}: res={actual_res} fail={actual_fail} infra={actual_infra} total={actual_n}')
print(f'TOTAL resolved={tot_res} evaluated={tot_eval}')
