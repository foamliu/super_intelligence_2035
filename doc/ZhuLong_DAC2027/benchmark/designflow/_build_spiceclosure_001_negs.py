#!/usr/bin/env python3
"""Build negatives + reference_submit.zip + self-verify for SpiceClosureExtract-001."""
import os, json, zipfile, subprocess, sys, shutil, tempfile

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-SpiceClosureExtract-001"
R = os.path.join(ROOT, "reference", CID)
NEG = os.path.join(R, "negative")

REF_GEN_NAME = "gen_spice_closure_ref.py"
REF_GEN = os.path.join(R, REF_GEN_NAME)

# ---------- 5 negatives ----------
# (1) empty_shell: generator that does nothing
open(os.path.join(NEG,"empty_shell.py"),"w").write(
'import sys\nif __name__=="__main__":\n    pass\n')
# (2) hardcode_a: hardcoded to emit A's manifest regardless of input
open(os.path.join(NEG,"hardcode_a.py"),"w").write(
'''import os, json, sys, argparse
ap=argparse.ArgumentParser(); ap.add_argument("--lib",required=True); ap.add_argument("--roots",required=True); ap.add_argument("--outdir",required=True); a=ap.parse_args()
os.makedirs(a.outdir,exist_ok=True)
# hardcoded A manifest (ignores input)
m={"roots":["Ras_Tscodecomp","Ras_SaNPCtrl"],"n_roots":2,"n_subckts_in_closure":9,"n_leaf_models":2,
"closure":[],"topo_order":["ptn_lv","ntn_lv","nand_x2","inv_x1","Ras_SaNPCtrl","nand_x1","nor_x1","inv_x2","Ras_Tscodecomp"],
"missing":[],"leaf_models":["ntn","ptn"]}
json.dump(m,open(os.path.join(a.outdir,"manifest.json"),"w"))
open(os.path.join(a.outdir,"closure.sp"),"w").write("* hardcoded\\n")
''')
# (3) print_expected: writes manifest.json with B's correct top-level scalars
#     (roots/n_roots/n_subckts/n_leaf_models/leaf_models/missing all correct) BUT
#     empty closure[] and closure.sp with 0 .SUBCKT lines -> fails at (k)
open(os.path.join(NEG,"print_expected.py"),"w").write(
'''import os, json, sys, argparse
ap=argparse.ArgumentParser(); ap.add_argument("--lib",required=True); ap.add_argument("--roots",required=True); ap.add_argument("--outdir",required=True); a=ap.parse_args()
roots=json.load(open(a.roots))["roots"]
os.makedirs(a.outdir,exist_ok=True)
m={"roots":["CmpCore","BiasGen"],"n_roots":2,"n_subckts_in_closure":7,"n_leaf_models":2,
"closure":[],"topo_order":[],"missing":[],"leaf_models":["ntn_mos","ptn_mos"]}
json.dump(m,open(os.path.join(a.outdir,"manifest.json"),"w"))
open(os.path.join(a.outdir,"closure.sp"),"w").write("* printed expected values, no real closure\\n")
''')
# (4) ref_core_deleted: real parser but closure = roots only (no transitive deps);
#     lies n_subckts_in_closure=7 but closure has only 2 entries -> fails at (m)
open(os.path.join(NEG,"ref_core_deleted.py"),"w").write(
'''import os, json, sys, argparse
def parse_lib(text):
    subckts={}; cur=None
    for ln in text.splitlines():
        s=ln.strip(); low=s.lower()
        if low.startswith(".subckt"):
            toks=s.split(); subckts[toks[1]]={"ports":toks[2:],"body":[ln],"xrefs":[],"mrefs":[]}; cur=toks[1]
        elif low.startswith(".ends"): cur=None
        elif cur is not None:
            subckts[cur]["body"].append(ln)
            if s and s[0] in ("X","x"):
                subckts[cur]["xrefs"].append(s.split()[-1])
            elif s and s[0] in ("M","m") and len(s.split())>=6:
                subckts[cur]["mrefs"].append(s.split()[5])
    return subckts
ap=argparse.ArgumentParser(); ap.add_argument("--lib",required=True); ap.add_argument("--roots",required=True); ap.add_argument("--outdir",required=True); a=ap.parse_args()
subckts=parse_lib(open(a.lib).read()); roots=json.load(open(a.roots))["roots"]
os.makedirs(a.outdir,exist_ok=True)
# BUG: closure = roots only (no transitive deps); lie the count
clos=[r for r in roots if r in subckts]
m={"roots":roots,"n_roots":len(roots),"n_subckts_in_closure":7,"n_leaf_models":2,
"closure":[{"name":n,"type":"root","ports":subckts[n]["ports"],"deps":[],"n_xi":len(subckts[n]["xrefs"]),"n_mos":len(subckts[n]["mrefs"])} for n in clos],
"topo_order":clos,"missing":[],"leaf_models":["ntn_mos","ptn_mos"]}
json.dump(m,open(os.path.join(a.outdir,"manifest.json"),"w"))
with open(os.path.join(a.outdir,"closure.sp"),"w") as f:
    for n in clos:
        for ln in subckts[n]["body"]: f.write(ln+"\\n")
''')
# (5) naive_stub: writes correct roots/n_roots/n_subckts but n_leaf_models=0 +
#     leaf_models=[] (refuses to parse M rows) -> fails at (h)
open(os.path.join(NEG,"naive_stub.py"),"w").write(
'''import os, json, sys, argparse
ap=argparse.ArgumentParser(); ap.add_argument("--lib",required=True); ap.add_argument("--roots",required=True); ap.add_argument("--outdir",required=True); a=ap.parse_args()
roots=json.load(open(a.roots))["roots"]
os.makedirs(a.outdir,exist_ok=True)
m={"roots":roots,"n_roots":len(roots),"n_subckts_in_closure":7,"n_leaf_models":0,
"closure":[],"topo_order":[],"missing":[],"leaf_models":[]}
json.dump(m,open(os.path.join(a.outdir,"manifest.json"),"w"))
open(os.path.join(a.outdir,"closure.sp"),"w").write("* naive, no leaf model parsing\\n")
''')

# ---------- negative_selftest.py ----------
SELFTEST = '''#!/usr/bin/env python3
"""Negative self-test: all 5 negatives must FAIL check(). All must FAIL."""
import sys, os, zipfile, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check import check

NEG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "negative")
negs = ["empty_shell.py","hardcode_a.py","print_expected.py","ref_core_deleted.py","naive_stub.py"]
fails = []
for n in negs:
    src = os.path.join(NEG, n)
    with tempfile.TemporaryDirectory() as td:
        zp = os.path.join(td, "submit.zip")
        with zipfile.ZipFile(zp, "w") as zf:
            zf.write(src, "cand.py")
        try:
            check("submit.zip", td)
            fails.append((n, "PASS (expected FAIL)"))
        except AssertionError as e:
            print("OK negative %s -> FAIL: %s" % (n, str(e)[:80]))
if fails:
    print("NEGATIVE SELFTEST FAILED:")
    for n, why in fails:
        print("  ", n, why)
    sys.exit(1)
print("all 5 negatives FAIL as expected")
'''
open(os.path.join(R,"negative_selftest.py"),"w").write(SELFTEST)

# ---------- reference_submit.zip (the ref generator, for self-verify) ----------
ref_zip = os.path.join(R, "reference_submit.zip")
with zipfile.ZipFile(ref_zip, "w") as zf:
    zf.write(REF_GEN, "gen_spice_closure.py")

print("negatives + selftest + reference_submit.zip written")
