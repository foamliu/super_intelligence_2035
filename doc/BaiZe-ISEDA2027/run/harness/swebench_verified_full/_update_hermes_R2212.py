#!/usr/bin/env python3
"""Manually update hermes eval report for R2212 (django__django-13410 RESOLVED)."""
import json, glob

h = 'hermes'
iid = 'django__django-13410'
eval_file = f'reports/eval_glm53_{h}.json'
ed = json.load(open(eval_file))
for key in ('resolved', 'failed', 'infra_or_quota'):
    ed.setdefault(key, [])
for key in ('resolved', 'failed', 'infra_or_quota'):
    ed[key] = [x for x in ed[key] if x != iid and not x.startswith(f'{iid}(')]

rj = glob.glob(f'logs/run_evaluation/verified_full_glm53_hermes_incr_R2212/**/{iid}/report.json', recursive=True)
print('report.json found:', rj)
rd = json.load(open(rj[0]))
inst_rep = rd.get(iid, rd) if isinstance(rd, dict) else {}
print('resolved=', inst_rep.get('resolved'), 'infra_failure=', inst_rep.get('infra_failure'))
if inst_rep.get('resolved'):
    ed['resolved'].append(iid)
elif inst_rep.get('infra_failure'):
    ed['infra_or_quota'].append(iid)
else:
    ed['failed'].append(iid)
ed['n'] = len(ed['resolved']) + len(ed['failed']) + len(ed['infra_or_quota'])
ed['resolved_count'] = len(ed['resolved'])
ed['evaluated'] = ed['n']
json.dump(ed, open(eval_file, 'w'), indent=2)
print(f'UPDATED {h}: resolved={ed["resolved_count"]} failed={len(ed["failed"])} infra={len(ed["infra_or_quota"])} total={ed["n"]}')
