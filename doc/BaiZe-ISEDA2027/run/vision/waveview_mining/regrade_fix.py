#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the FIXED grade() contract against existing pilot submit.zips.

Bug: run_codegen_v0v1v2.grade() passed the agent's raw workdir (which excludes
`hidden/`) to check.py.  Many code_gen check.py read os.path.join(workdir,
"hidden", ...) (e.g. FsdbMeasRunGen needs hidden/hidden_manifest.json + A sp),
so they RUNTIME-failed even on correct submissions.

Fix: build a FRESH grading workdir = A assets (non-hidden files) + hidden/ dir,
copy submit.zip into it as "submit.zip", call check("submit.zip", gdir).
Agent never sees gdir (built AFTER pi exits) -> anti-hardcode preserved.
"""
import json, os, sys, re, shutil, subprocess, importlib.util, zipfile, tempfile

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
OUTD = "/tmp/wv_cg"


def _zip_n(p):
    try:
        with zipfile.ZipFile(p) as z:
            return len(z.namelist())
    except Exception:
        return 0


def build_gdir(case, submit_zip):
    """Fresh grading workdir: A assets (non-hidden) + hidden/ + submit.zip."""
    gdir = tempfile.mkdtemp(prefix="g_", dir="/tmp/wv_cg_grade")
    adir = os.path.join(BASE, "assets", case)
    if os.path.isdir(adir):
        for fn in os.listdir(adir):
            src = os.path.join(adir, fn)
            if not os.path.isfile(src) or fn == "hidden" or fn.startswith("."):
                continue
            shutil.copy2(src, os.path.join(gdir, fn))
        hsrc = os.path.join(adir, "hidden")
        if os.path.isdir(hsrc):
            shutil.copytree(hsrc, os.path.join(gdir, "hidden"))
    shutil.copy2(submit_zip, os.path.join(gdir, "submit.zip"))
    return gdir


def grade_fixed(case, arm, wd):
    submit = os.path.join(wd, "outputs", "submit.zip")
    if not os.path.isfile(submit):
        for root, _d, files in os.walk(wd):
            if "submit.zip" in files and ".pisess" not in root:
                submit = os.path.join(root, "submit.zip"); break
    if not os.path.isfile(submit):
        return {"verdict": False, "k_pass": 0, "k_total": 0,
                "detail": "no submit.zip produced", "n_zip_members": 0}
    cp = os.path.join(BASE, "reference", case, "check.py")
    if not os.path.isfile(cp):
        return {"verdict": False, "k_pass": 0, "k_total": 0,
                "detail": "check.py not found", "n_zip_members": _zip_n(submit)}
    gdir = build_gdir(case, submit)
    grader = ("import importlib.util, json, sys, re\n"
              "spec = importlib.util.spec_from_file_location('chk', %r)\n"
              "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
              "out = {'pass': False}\n"
              "try:\n"
              "    r = m.check('submit.zip', %r)\n"
              "except AssertionError as e:\n"
              "    out = {'pass': False, 'err': str(e)}\n"
              "except Exception as e:\n"
              "    out = {'pass': False, 'err': 'RUNTIME:' + str(e)[:300]}\n"
              "else:\n"
              "    if isinstance(r, dict):\n"
              "        out = r\n"
              "    elif isinstance(r, bool):\n"
              "        out = {'pass': bool(r)}\n"
              "    elif isinstance(r, str):\n"
              "        m2 = re.search(r'(\\d+)\\s*/\\s*(\\d+)', r)\n"
              "        out = {'pass': r.strip().upper().startswith('PASS'), 'ret': r[:200]}\n"
              "        if m2:\n"
              "            out['k_pass'] = int(m2.group(1)); out['k_total'] = int(m2.group(2))\n"
              "    else:\n"
              "        out = {'pass': False, 'ret': str(r)[:200]}\n"
              "print(json.dumps(out, default=str))\n"
              % (cp, gdir))
    try:
        p = subprocess.run([sys.executable, "-c", grader], capture_output=True,
                           text=True, timeout=120, cwd=gdir)
        out = (p.stdout or "").strip()
        res = json.loads(out.splitlines()[-1]) if out else {"pass": False, "err": "no output"}
    except Exception as e:
        res = {"pass": False, "err": "grade error: " + str(e)[:200]}
    finally:
        shutil.rmtree(gdir, ignore_errors=True)
    verdict = bool(res.get("pass") or res.get("ok"))
    conds = res.get("conditions") or []
    if conds:
        k_total = len(conds); k_pass = sum(1 for c in conds if c.get("ok"))
    elif res.get("k_total"):
        k_total = int(res["k_total"]); k_pass = int(res.get("k_pass", 0))
    else:
        k_total = 0; k_pass = 1 if verdict else 0
    detail = res.get("err") or res.get("detail") or res.get("ret") or ""
    if conds:
        ff = next((c.get("detail") for c in conds if not c.get("ok")), "")
        detail = ff or detail
    return {"verdict": verdict, "k_pass": k_pass, "k_total": k_total,
            "detail": str(detail)[:200], "n_zip_members": _zip_n(submit)}


def main():
    cases = sorted(d for d in os.listdir(OUTD)
                   if d.startswith("EDA-Eval-DesignFlow-") and os.path.isdir(os.path.join(OUTD, d)))
    old = json.load(open(os.path.join(OUTD, "results.json")))
    old_map = {(r["case_id"], r["arm"]): r for r in old["rows"]}
    print("regrade %d cases x 3 arms (FIXED contract)" % len(cases))
    changed = 0
    for case in cases:
        for arm in ["V0", "V1", "V2"]:
            wd = os.path.join(OUTD, case, arm)
            if not os.path.isdir(wd):
                continue
            g = grade_fixed(case, arm, wd)
            o = old_map.get((case, arm), {})
            ov = o.get("verdict"); okp = o.get("k_pass"); okt = o.get("k_total")
            flag = ""
            if ov != g["verdict"]:
                flag = "  <== CHANGED"; changed += 1
            print("  %-42s %s  old=%s(%s/%s) new=%s(%s/%s) nzip=%s%s"
                  % (case.replace("EDA-Eval-DesignFlow-", "")[:40], arm,
                     ov, okp, okt, g["verdict"], g["k_pass"], g["k_total"],
                     g["n_zip_members"], flag))
            if flag or (not g["verdict"] and g["n_zip_members"] > 0):
                print("      detail: %s" % g["detail"][:160])
    print("CHANGED verdicts: %d" % changed)


if __name__ == "__main__":
    main()
