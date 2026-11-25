#!/usr/bin/env python3
"""R2000 cline special report (§10:10 C1-C5). Self-contained Chinese HTML."""
import json, os, datetime, glob

REPORT_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
EVAL_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports"
PRED_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_glm53"
TB21_JOBS = "/tmp/tb21_glm53_jobs"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
ROUND = "R2000"

HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
DISPLAY = {"cline-patched":"cline","deepseek-harness":"deepseek"}
def disp(h): return DISPLAY.get(h, h)

cline_files = sorted(glob.glob(os.path.join(PRED_DIR, "cline-patched__*.json")))
cline_total = len(cline_files); cline_real = 0; cline_empty_tasks = []
for f in cline_files:
    try:
        d = json.load(open(f))
        p = d[0].get("model_patch","") if isinstance(d, list) else d.get("model_patch","")
        if p.strip(): cline_real += 1
        else: cline_empty_tasks.append(os.path.basename(f).split("__")[-1].replace(".json",""))
    except: cline_empty_tasks.append(os.path.basename(f)+"(ERR)")
cline_empty = cline_total - cline_real

eval_data = {}
for h in HARNESSES:
    ef = os.path.join(EVAL_DIR, f"eval_glm53_{h}.json")
    if os.path.isfile(ef):
        d = json.load(open(ef))
        eval_data[disp(h)] = (len(d.get("resolved",[])), d.get("n",0))

pred_data = {}
for h in HARNESSES:
    files = glob.glob(os.path.join(PRED_DIR, f"{h}__*.json"))
    total = len(files); real = 0
    for f in files:
        try:
            d = json.load(open(f))
            if isinstance(d, list): real += sum(1 for p in d if p.get("model_patch","").strip())
            elif isinstance(d, dict) and d.get("model_patch","").strip(): real += 1
        except: pass
    pred_data[disp(h)] = (total, real)

def count_tb21(dirname):
    hjobs = os.path.join(TB21_JOBS, dirname)
    done = 0; passed = 0
    if os.path.isdir(hjobs):
        for rd in os.listdir(hjobs):
            rdp = os.path.join(hjobs, rd)
            if not os.path.isdir(rdp): continue
            for td in os.listdir(rdp):
                tdp = os.path.join(rdp, td)
                if not os.path.isdir(tdp): continue
                done += 1
                rw_file = os.path.join(tdp, "verifier", "reward.txt")
                if os.path.isfile(rw_file) and open(rw_file).read().strip() in ("1","1.0"):
                    passed += 1
    return done, passed

tb21_cline_done, tb21_cline_pass = count_tb21("cline-patched")
tb21_all = {}
for dn, dirname in [("cline","cline-patched"),("codex","codex"),("hermes","hermes"),("opencode","opencode"),("claude-code","claude-code"),("deepseek","deepseek-harness"),("pi","pi")]:
    tb21_all[dn] = count_tb21(dirname)
tb21_total_d = sum(v[0] for v in tb21_all.values())
tb21_total_p = sum(v[1] for v in tb21_all.values())

empty_str = ", ".join(cline_empty_tasks[:10]) + (f" ... (+{len(cline_empty_tasks)-10})" if len(cline_empty_tasks) > 10 else "")
cr, cn = eval_data.get("cline", (0, 0))
cpct = f"{100*cr/max(cn,1):.1f}%"

# Store vars for HTML part
import pickle
with open("/tmp/cline_r2000_data.pkl", "wb") as pf:
    pickle.dump(dict(cline_total=cline_total, cline_real=cline_real, cline_empty=cline_empty,
                     cline_empty_tasks=cline_empty_tasks, empty_str=empty_str,
                     eval_data=eval_data, pred_data=pred_data,
                     tb21_cline_done=tb21_cline_done, tb21_cline_pass=tb21_cline_pass,
                     tb21_all=tb21_all, tb21_total_d=tb21_total_d, tb21_total_p=tb21_total_p,
                     NOW=NOW, ROUND=ROUND, HARNESSES=HARNESSES, cr=cr, cn=cn, cpct=cpct), pf)
print(f"Data saved. cline: {cline_total}pred {cline_real}r {cline_empty}e eval={cr}/{cn}={cpct} TB21={tb21_cline_pass}p/{tb21_cline_done}d total={tb21_total_p}p/{tb21_total_d}d")
