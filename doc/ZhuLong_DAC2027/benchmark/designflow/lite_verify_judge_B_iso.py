#!/usr/bin/env python3
"""Subprocess-isolated judge-layout L2 verify: one fresh python process per case."""
import sys, subprocess, json, concurrent.futures as cf
HERE="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow"
RUNNER=os.path.join(HERE,"_iso_runner.py") if False else __import__("os").path.join(HERE,"_iso_runner.py")
import os
RUNNER=os.path.join(HERE,"_iso_runner.py")
cases=[l.strip() for l in sys.stdin if l.strip()]
def run(cid):
    try:
        r=subprocess.run([sys.executable,RUNNER,cid],capture_output=True,text=True,timeout=120)
        if r.returncode!=0:
            return {"case_id":cid,"L2":"ERR","detail":"subprocess rc=%d: %s"%(r.returncode,r.stderr[:200])}
        return json.loads(r.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return {"case_id":cid,"L2":"ERR","detail":"timeout"}
    except Exception as e:
        return {"case_id":cid,"L2":"ERR","detail":"harness: "+repr(e)[:200]}
print("case_id\tL2\tdetail",flush=True)
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    futs={ex.submit(run,c):c for c in cases}
    for fut in cf.as_completed(futs):
        o=fut.result()
        print("%s\t%s\t%s"%(o["case_id"],o["L2"],o.get("detail","")),flush=True)
