#!/usr/bin/env python3
"""Lite verify harness v2 for shard B python-only cases.
- Passes reference_submit.zip PATH (not bytes) to check().
- Auto-builds reference_submit.zip if missing, from ref solution .py + arcname.
- Verifies L2 (ref PASS) + L3 (all negs FAIL via selftest).
"""
import os, sys, re, tempfile, zipfile, subprocess, importlib.util, concurrent.futures as cf

REF_ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference"

def find_arcname(refdir):
    """Determine the arcname (script name in submit.zip) from selftest or check.py."""
    for st in [os.path.join(refdir,'negative_selftest.py'), os.path.join(refdir,'negative','negative_selftest.py')]:
        if os.path.isfile(st):
            src=open(st,errors='replace').read()
            m=re.search(r'z\.write\([^,]+,\s*["\']([^"\']+)["\']\)', src) or re.search(r'arcname=["\']([^"\']+)["\']', src) or re.search(r'z\.writestr\(["\']([^"\']+)["\']', src)
            if m: return m.group(1)
    # fallback: from check.py - find a .py name that isn't check.py/negative_selftest.py
    chk=open(os.path.join(refdir,'check.py'),errors='replace').read()
    cands=re.findall(r'\b([a-z_][a-z0-9_]*\.py)\b', chk)
    bad={'check.py','negative_selftest.py','__init__.py','solve.py'}
    for c in cands:
        if c not in bad: return c
    return None

def find_ref_solution(refdir, arcname):
    """Find the reference solution .py file in refdir."""
    pys=[f for f in os.listdir(refdir) if f.endswith('.py') and f!='check.py' and not f.startswith('negative_') and not f.startswith('__')]
    if not pys: return None
    # prefer *_ref.py
    refs=[f for f in pys if f.endswith('_ref.py')]
    if refs and len(refs)==1: return refs[0]
    # prefer a file whose stem matches arcname stem
    if arcname:
        arc_stem=arcname[:-3] if arcname.endswith('.py') else arcname
        for f in pys:
            stem=f[:-3] if f.endswith('.py') else f
            if stem==arc_stem or stem==arc_stem+'_ref': return f
    # prefer single non-gen_*.py helper
    if len(pys)==1: return pys[0]
    # heuristic: the largest .py (ref solutions are usually biggest)
    return max(pys, key=lambda f: os.path.getsize(os.path.join(refdir,f)))

def ensure_ref_zip(refdir):
    """Ensure reference_submit.zip exists. Build if missing. Returns (path, built, note)."""
    rz=os.path.join(refdir,'reference_submit.zip')
    if os.path.isfile(rz): return rz, False, ''
    arc=find_arcname(refdir)
    refpy=find_ref_solution(refdir, arc)
    if not refpy:
        return None, False, 'no ref .py to build from'
    if not arc:
        arc=refpy  # fallback: use refpy name
    try:
        with zipfile.ZipFile(rz,'w') as z:
            z.write(os.path.join(refdir,refpy), arcname=arc)
        return rz, True, 'built from %s as %s' % (refpy, arc)
    except Exception as e:
        return None, False, 'build failed: '+repr(e)[:120]

def load_check(case_id, refdir):
    chk=os.path.join(refdir,'check.py')
    spec=importlib.util.spec_from_file_location("chk_"+case_id.replace('-','_'), chk)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def verify_case(case_id):
    out={"case_id":case_id,"L2":"?","L3":"?","detail":""}
    refdir=os.path.join(REF_ROOT,case_id)
    try:
        mod=load_check(case_id, refdir)
    except Exception as e:
        out["L2"]="ERR"; out["detail"]="import: "+repr(e)[:200]; return out
    rz, built, note = ensure_ref_zip(refdir)
    if not rz:
        out["L2"]="NO_REF"; out["detail"]="no reference_submit.zip: "+note; return out
    if built: out["detail"]="built ref_zip; "
    # ---- L2: reference must PASS (pass PATH, not bytes) ----
    try:
        with tempfile.TemporaryDirectory() as wd:
            res=mod.check(rz, wd)
        ok=(res is True) or (isinstance(res,dict) and (res.get('pass') is True or res.get('ok') is True))
        out["L2"]="PASS" if ok else "FAIL:"+repr(res)[:120]
    except AssertionError as e:
        out["L2"]="FAIL:"+str(e)[:160]
    except Exception as e:
        out["L2"]="ERR:"+repr(e)[:160]
    # ---- L3: negatives must FAIL ----
    st_root=os.path.join(refdir,'negative_selftest.py')
    st_neg=os.path.join(refdir,'negative','negative_selftest.py')
    st=st_root if os.path.isfile(st_root) else st_neg
    if not os.path.isfile(st):
        out["L3"]="NO_SELFTEST"; return out
    try:
        r=subprocess.run([sys.executable, st, refdir], capture_output=True, text=True, cwd=refdir, timeout=180)
        out["L3"]="PASS" if r.returncode==0 else "FAIL(rc=%d)"%r.returncode
        out["detail"]+=" | selftest: "+(r.stdout.strip()[-260:] if r.stdout else r.stderr.strip()[-260:])
    except subprocess.TimeoutExpired:
        out["L3"]="TIMEOUT"
    except Exception as e:
        out["L3"]="ERR:"+repr(e)[:120]
    return out

def main():
    cases=[l.strip() for l in sys.stdin if l.strip()]
    print("case_id\tL2\tL3\tdetail", flush=True)
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs={ex.submit(verify_case,c):c for c in cases}
        for fut in cf.as_completed(futs):
            o=fut.result()
            print("%s\t%s\t%s\t%s"%(o["case_id"],o["L2"],o["L3"],o.get("detail","")), flush=True)

if __name__=="__main__":
    main()
