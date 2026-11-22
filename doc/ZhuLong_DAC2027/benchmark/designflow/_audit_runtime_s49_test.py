#!/usr/bin/env python3
"""Proper §4.9 re-test for D k=12 GAP cases.

For each case:
1. Detect the expected SUT filename (from reference_submit.zip namelist, or check.py hints).
2. For each negative: if it's a .py stub, rename to the expected SUT name and zip it;
   if it's a .csv/.zip/pre-built deliverable, pass directly or package appropriately.
3. Run check against reference_submit.zip (ref must PASS) and against each renamed negative.
4. Verdict:
   - SOUND    : ref PASS + at least one of {print_only,core_deleted,empty} negative FAILs
                on a SUBSTANTIVE condition (not the filename check a).
   - WEAK_NEG : negatives only FAIL on shallow/filename conditions (§4.9 untested).
   - TRUE_GAP : ref PASS but a §4.9 negative PASSES check (real violation).
   - REF_FAIL : ref doesn't PASS standalone (harness-dependent or broken).
   - NO_NEG   : no negatives.
"""
import os, sys, re, importlib.util, tempfile, shutil, zipfile

REF_ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference"

def resolve_dir(cid):
    if os.path.isdir(os.path.join(REF_ROOT, cid)):
        return os.path.join(REF_ROOT, cid)
    short = cid.replace("EDA-Eval-DesignFlow-", "")
    if os.path.isdir(os.path.join(REF_ROOT, short)):
        return os.path.join(REF_ROOT, short)
    return None

def load(case_dir):
    cp = os.path.join(case_dir, "check.py")
    if not os.path.isfile(cp): return None
    spec = importlib.util.spec_from_file_location("cc_"+re.sub(r"\W","_",case_dir), cp)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m if hasattr(m,"check") else None

def verd(r):
    if isinstance(r,bool): return r
    if isinstance(r,dict): return r.get("pass",False)
    return bool(r)

def fail_reason(r, exc):
    if exc is not None:
        return ("raise", str(exc)[:80])
    if isinstance(r,dict):
        asrt = r.get("assertions",{}) if isinstance(r.get("assertions"),dict) else {}
        fa = [k for k,v in asrt.items() if isinstance(v,dict) and not v.get("pass", v.get("ok", True))]
        if fa:
            return (fa[0], str(asrt[fa[0]].get("msg",""))[:80])
        return ("dict", "pass=False")
    return ("ret", "falsy")

def expected_sut_name(case_dir, m):
    """Detect expected SUT filename."""
    ref = os.path.join(case_dir, "reference_submit.zip")
    if os.path.isfile(ref):
        try:
            with zipfile.ZipFile(ref) as zf:
                names = zf.namelist()
            # prefer a .py that's not __init__
            pys = [n for n in names if n.endswith(".py") and "__" not in n]
            if pys:
                return os.path.basename(pys[0])
            # csv
            csvs = [n for n in names if n.endswith(".csv")]
            if csvs: return os.path.basename(csvs[0])
            # any single non-dir file
            files = [n for n in names if not n.endswith("/")]
            if len(files)==1: return os.path.basename(files[0])
        except Exception: pass
    # scan check.py source for a literal SUT name
    src = open(os.path.join(case_dir,"check.py"), errors="ignore").read()
    for pat in [r'SUT_NAME\s*=\s*"([^"]+)"', r'SUT\s*=\s*"([^"]+)"',
                r'EXPECTED_SUT\s*=\s*"([^"]+)"', r'contains\s+(?:a\s+)?(\w+\.py)']:
        mm = re.search(pat, src)
        if mm: return mm.group(1)
    return None

def is_shallow(cond_label, reason):
    low = (cond_label + " " + reason).lower()
    shallow_kw = ["missing","not found","not contain","not a zip","extract","no json",
                  "no output","is empty","parser","zip file","not in zip","filenotfound",
                  "must contain","namelist","not a list","none","not found in",
                  "no .json report","does not contain","zip must","missing from"]
    return any(k in low for k in shallow_kw)

def run_one(m, deliverable, wd):
    try:
        r = m.check(deliverable, wd)
        return verd(r), r, None
    except AssertionError as e:
        return False, None, e
    except Exception as e:
        return None, None, e

def main():
    cases = [l.strip() for l in open("/tmp/d_gap_k12.txt") if l.strip()]
    print("case_id\tref\tsut_name\tn_neg\tn_sub_fail\tn_shallow_fail\tn_pass\tverdict\tnote")
    for cid in cases:
        cdir = resolve_dir(cid)
        if cdir is None:
            print("%s\t-\t-\t0\t0\t0\t0\tNO_DIR\treference/ dir not found" % cid); continue
        m = load(cdir)
        if m is None:
            print("%s\t-\t-\t0\t0\t0\t0\tNO_CHECK\tno check.py" % cid); continue
        sut = expected_sut_name(cdir, m) or "candidate.py"
        # ref
        ref = os.path.join(cdir, "reference_submit.zip")
        wd = tempfile.mkdtemp()
        ref_ok = None
        try:
            if os.path.isfile(ref):
                ok,_,exc = run_one(m, ref, wd)
                ref_ok = ok
            else:
                ref_ok = "NO_REF"
        finally: shutil.rmtree(wd, ignore_errors=True)
        neg_dir = os.path.join(cdir, "negative")
        negs = []
        if os.path.isdir(neg_dir):
            negs = [os.path.join(neg_dir,f) for f in sorted(os.listdir(neg_dir))
                    if not f.startswith("__") and f!="negative_selftest.py"]
        n_sub=n_shal=n_pass=0; note=""
        for nf in negs:
            wd = tempfile.mkdtemp()
            try:
                if nf.endswith(".zip") or (not nf.endswith(".py") and not nf.endswith(".csv") and os.path.isfile(nf) and zipfile.is_zipfile(nf)):
                    deliverable = nf  # pre-built submit zip -> pass directly
                elif os.path.isdir(nf):
                    # negative is a dir of files -> zip contents
                    deliverable = os.path.join(wd, "submit.zip")
                    with zipfile.ZipFile(deliverable,"w") as zf:
                        for root,_,fs in os.walk(nf):
                            for fn in fs:
                                p=os.path.join(root,fn); zf.write(p, os.path.relpath(p,nf))
                else:
                    # .py or .csv -> rename to SUT name and zip
                    deliverable = os.path.join(wd, "submit.zip")
                    with zipfile.ZipFile(deliverable,"w") as zf:
                        zf.write(nf, sut)
                ok, r, exc = run_one(m, deliverable, wd)
                if ok:
                    n_pass += 1; note = "NEG_PASS:%s" % os.path.basename(nf)
                elif ok is False:
                    cl, reason = fail_reason(r, exc)
                    if is_shallow(cl, reason):
                        n_shal += 1
                    else:
                        n_sub += 1
                else:
                    n_shal += 1  # error -> inconclusive
            finally:
                shutil.rmtree(wd, ignore_errors=True)
        # verdict
        if ref_ok is True:
            if n_pass > 0:
                verdict = "TRUE_GAP"
            elif n_sub > 0:
                verdict = "SOUND"
            elif n_shal > 0 and n_sub == 0:
                verdict = "WEAK_NEG"
            else:
                verdict = "NO_NEG"
        elif ref_ok == "NO_REF":
            verdict = "NO_REF" if n_neg_count(negs)==0 else ("SOUND" if n_sub>0 else "WEAK_NEG")
        else:
            verdict = "REF_FAIL"
        print("%s\t%s\t%s\t%d\t%d\t%d\t%d\t%s\t%s" % (
            cid, ref_ok, sut, len(negs), n_sub, n_shal, n_pass, verdict, note))

def n_neg_count(negs): return len(negs)

if __name__ == "__main__":
    main()
