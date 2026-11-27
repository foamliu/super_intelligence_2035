import json
from collections import defaultdict

def load(path):
    d={}
    try:
        for l in open(path):
            if not l.strip(): continue
            r=json.loads(l)
            d[r['task_id']]=r.get('verdict')
    except FileNotFoundError:
        return None
    return d

r1=load('/nasdata/app.e0031982/code/EDA-Flow-Bench/eval/status_thermo_r1.jsonl')
# try r3' (rerun#2 round 3) as the previous baseline
r3p=load('/nasdata/app.e0031982/code/EDA-Flow-Bench/eval/status_doubao_pro_rerun2_r3.jsonl')
if r3p is None:
    # fallback names
    for nm in ['status_doubao_pro_rerun2_r3.jsonl','status_doubao_pro_r3.jsonl']:
        r3p=load('/nasdata/app.e0031982/code/EDA-Flow-Bench/eval/'+nm)
        if r3p: break

out=[]
if r3p is None:
    out.append("NO_PREVIOUS_BASELINE: no rerun#2 r3' status found; r1 is first thermo round, no FAIL diff available.")
else:
    out.append(f"baseline=r3' (rerun#2 round 3, status_doubao_pro_rerun2_r3.jsonl, {len(r3p)} cases)")
    out.append(f"r1 cases={len(r1)}")
    common=set(r1)&set(r3p)
    out.append(f"common cases={len(common)}")
    new_err=sorted([t for t in common if r1[t]=='ERROR' and r3p[t]!='ERROR'])
    new_fail=sorted([t for t in common if r1[t]=='FAIL' and r3p[t]=='PASS'])
    new_pass=sorted([t for t in common if r1[t]=='PASS' and r3p[t]=='FAIL'])
    err_rec=sorted([t for t in common if r1[t]!='ERROR' and r3p[t]=='ERROR'])  # recovered from ERROR
    out.append(f"\n## newly ERROR (was PASS/FAIL in r3', now ERROR in r1): {len(new_err)}")
    for t in new_err: out.append(f"  - {t}  (r3'={r3p[t]} -> r1=ERROR)")
    out.append(f"\n## newly FAIL (was PASS in r3', now FAIL in r1): {len(new_fail)}")
    for t in new_fail: out.append(f"  - {t}  (r3'=PASS -> r1=FAIL)")
    out.append(f"\n## newly PASS (was FAIL in r3', now PASS in r1): {len(new_pass)}")
    for t in new_pass: out.append(f"  - {t}  (r3'=FAIL -> r1=PASS)")
    out.append(f"\n## recovered from ERROR (was ERROR in r3', now PASS/FAIL in r1): {len(err_rec)}")
    for t in err_rec: out.append(f"  - {t}  (r3'=ERROR -> r1={r1[t]})")

print('\n'.join(out))
