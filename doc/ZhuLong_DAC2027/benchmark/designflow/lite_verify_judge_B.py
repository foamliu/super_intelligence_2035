#!/usr/bin/env python3
"""Faithful judge-layout L2 re-verify for shard B (replicates run_one.sh symlink tree).

Replicates eval/run_one.sh judge setup:
  $JUDGE/hidden/                  <- assets/<cid>/hidden/ + reference/<cid>/hidden*
  $JUDGE/g1/g2/check.py           <- reference/<cid>/check.py
  $JUDGE/g1/g2/<ref helpers>      <- reference/<cid>/*.py *.json (non-check/selftest)
  $JUDGE/g1/g2/submit.zip         <- reference/<cid>/reference_submit.zip
  symlinks: g1/g2/hidden, g1/hidden, assets/<cid>/hidden, g1/assets/<cid>/hidden,
            hidden_b/hidden_B/... variants -> $JUDGE/hidden
  A attachments (non-hidden) from assets/<cid>/ copied to g1/g2/
Then runs check(submit.zip, '.') with cwd=g1/g2.

Usage: echo CID... | python3 lite_verify_judge_B.py
"""
import os, sys, re, shutil, tempfile, zipfile, subprocess, importlib.util

# Mirror real eval (run_one.sh) env so check.py can locate repo assets via BENCH_CASES_DIR
_BENCH="/nasdata/app.e0031982/code/EDA-Flow-Bench"
os.environ.setdefault("BENCH_CASES_DIR", os.path.join(_BENCH,"benchmarks","EDA-Eval-DesignFlow","cases"))
os.environ.setdefault("BENCH_SCRIPTS_DIR", os.path.join(_BENCH,"scripts"))

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS_ROOT = os.path.join(BENCH, "assets")
REF_ROOT = os.path.join(BENCH, "reference")

def setup_judge(judge, cid):
    assets_src = os.path.join(ASSETS_ROOT, cid)
    ref_dir = os.path.join(REF_ROOT, cid)
    hidden_dst = os.path.join(judge, "hidden")
    g2 = os.path.join(judge, "g1", "g2")
    os.makedirs(hidden_dst, exist_ok=True)
    os.makedirs(g2, exist_ok=True)
    # hidden from assets/hidden
    ah = os.path.join(assets_src, "hidden")
    if os.path.isdir(ah):
        for f in os.listdir(ah):
            src = os.path.join(ah, f)
            dst = os.path.join(hidden_dst, f)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True) if os.path.isdir(dst) else shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
    # hidden from reference/hidden*
    for hd in [d for d in os.listdir(ref_dir) if d.startswith("hidden") and os.path.isdir(os.path.join(ref_dir, d))]:
        src = os.path.join(ref_dir, hd)
        if hd == "hidden":
            for f in os.listdir(src):
                sp = os.path.join(src, f)
                shutil.copy2(sp, os.path.join(hidden_dst, f)) if os.path.isfile(sp) else None
        else:
            shutil.copytree(src, os.path.join(g2, hd), dirs_exist_ok=True)
    # check.py + ref helpers
    shutil.copy2(os.path.join(ref_dir, "check.py"), os.path.join(g2, "check.py"))
    for f in os.listdir(ref_dir):
        if f.endswith(".py") or f.endswith(".json"):
            if f in ("check.py", "negative_selftest.py"):
                continue
            shutil.copy2(os.path.join(ref_dir, f), os.path.join(g2, f))
    # submit.zip = reference_submit.zip
    rz = os.path.join(ref_dir, "reference_submit.zip")
    if not os.path.isfile(rz):
        return None, "no reference_submit.zip"
    shutil.copy2(rz, os.path.join(g2, "submit.zip"))
    # A attachments (non-hidden) from assets/<cid>/
    if os.path.isdir(assets_src):
        for f in os.listdir(assets_src):
            if f == "hidden":
                continue
            sp = os.path.join(assets_src, f)
            if os.path.isfile(sp):
                shutil.copy2(sp, os.path.join(g2, f))
    # symlink tree
    case_full = cid
    ln = os.path.join(g2, "hidden"); os.path.islink(ln) or os.path.exists(ln) or os.symlink(hidden_dst, ln)
    g1 = os.path.join(judge, "g1")
    ln = os.path.join(g1, "hidden"); os.path.islink(ln) or os.path.exists(ln) or os.symlink(hidden_dst, ln)
    for sub in (os.path.join(judge, "assets", case_full), os.path.join(g1, "assets", case_full)):
        os.makedirs(sub, exist_ok=True)
        ln = os.path.join(sub, "hidden"); os.path.islink(ln) or os.path.exists(ln) or os.symlink(hidden_dst, ln)
    for hname in ("hidden_b","hidden_B","hidden_b2","hidden_B2","hidden_b1","hidden_C","hidden_inputs","hidden_root"):
        for base in (g2, g1, os.path.join(judge,"assets",case_full), os.path.join(g1,"assets",case_full)):
            ln = os.path.join(base, hname)
            if not os.path.exists(ln):
                os.symlink(hidden_dst, ln)
    # A attachments reachable via assets/<cid>/
    for f in os.listdir(g2):
        sp = os.path.join(g2, f)
        if os.path.isfile(sp) and f != "check.py":
            for sub in (os.path.join(judge,"assets",case_full), os.path.join(g1,"assets",case_full)):
                ln = os.path.join(sub, f)
                if not os.path.exists(ln):
                    os.symlink(sp, ln)
    return g2, ""

def verify(cid):
    out = {"case_id": cid, "L2": "?", "detail": ""}
    ref_dir = os.path.join(REF_ROOT, cid)
    with tempfile.TemporaryDirectory() as judge:
        g2, err = setup_judge(judge, cid)
        if not g2:
            out["L2"] = "NO_REF"; out["detail"] = err; return out
        # load check.py from g2 (so its __file__ reflects judge layout)
        chk = os.path.join(g2, "check.py")
        spec = importlib.util.spec_from_file_location("chk_"+cid.replace("-","_"), chk)
        mod = importlib.util.module_from_spec(spec)
        os.chdir(g2)
        try:
            spec.loader.exec_module(mod)
            res = mod.check(os.path.join(g2, "submit.zip"), ".")
            ok = (res is True) or (isinstance(res, dict) and (res.get("pass") is True or res.get("ok") is True))
            out["L2"] = "PASS" if ok else "FAIL:"+repr(res)[:160]
        except AssertionError as e:
            out["L2"] = "FAIL:"+str(e)[:200]
        except Exception as e:
            out["L2"] = "ERR:"+repr(e)[:200]
    return out

def main():
    cases = [l.strip() for l in sys.stdin if l.strip()]
    print("case_id\tL2\tdetail", flush=True)
    for c in cases:
        try:
            o = verify(c)
        except Exception as e:
            o = {"case_id": c, "L2": "ERR", "detail": "harness: "+repr(e)[:200]}
        print("%s\t%s\t%s" % (o["case_id"], o["L2"], o["detail"]), flush=True)

if __name__ == "__main__":
    main()
