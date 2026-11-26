# -*- coding: utf-8 -*-
"""Build negatives + reference_submit + self-verify for TestModeExtract-001."""
import os, json, zipfile, subprocess, sys, shutil, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-TestModeExtract-001"
AST = os.path.join(BENCH, "assets", CID)
REF = os.path.join(BENCH, "reference", CID)
HID = os.path.join(AST, "hidden")
NEG = os.path.join(REF, "negative")
os.makedirs(NEG, exist_ok=True)

ref_gen = os.path.join(REF, "gen_testmode_report_ref.py")
src_ref = open(ref_gen).read()

# ---------- negatives ----------
# (1) empty shell
with open(os.path.join(NEG, "empty_shell.py"), "w") as f:
    f.write("# empty shell - does nothing\nimport sys\nsys.exit(0)\n")

# (2) hardcode A literals - writes a fixed report mentioning A module names
hardcode = '''# -*- coding: utf-8 -*-
import os, sys, json, argparse
ap = argparse.ArgumentParser(); ap.add_argument('--netlist',required=True); ap.add_argument('--outdir',required=True)
a = ap.parse_args()
os.makedirs(a.outdir, exist_ok=True)
# hardcoded A-specific answer (anti-hardcode violation)
job = {"netlist": os.path.basename(a.netlist),
       "test_modules": [{"name":"SCmosCkeRstCtrl","match_count":3,"first_line":2},
                        {"name":"DL_4PGenTestMode","match_count":2,"first_line":30},
                        {"name":"testmode_buf","match_count":1,"first_line":14}],
       "identifiers": {"test":["DL_4PGenTestMode","SCmosCkeRstCtrl","T_CMLeft_L1","VwlpRDBITestModeEn","testmode","testmodeN","testmode_buf"],
                       "str":["str_mode","str_pad_driver"],"size":["size_ctrl"]},
       "module_defs": {"SCmosCkeRstCtrl":"module SCmosCkeRstCtrl(...); endmodule"},
       "summary": {"n_modules":7,"n_test_modules":4,"n_test_ids":5,"n_str_ids":2,"n_size_ids":1}}
json.dump(job, open(os.path.join(a.outdir,'modules.json'),'w'))
open(os.path.join(a.outdir,'report.md'),'w').write("## Test Mode Modules\\n## Identifier Classification\\n## Module Definitions\\n")
'''
with open(os.path.join(NEG, "hardcode_a.py"), "w") as f:
    f.write(hardcode)

# (3) print expected string only, no real output files
with open(os.path.join(NEG, "print_expected.py"), "w") as f:
    f.write('# just prints, no files\nimport sys\nprint("modules.json report.md PASS")\n')

# (4) ref with core deleted (no module_defs key, empty)
ref_core_del = src_ref.replace("'module_defs': module_defs,", "'module_defs': {},")
with open(os.path.join(NEG, "ref_core_deleted.py"), "w") as f:
    f.write(ref_core_del)

# (5) naive stub - always emits fixed B-shaped output regardless of input
naive = '''# -*- coding: utf-8 -*-
import os, sys, json, argparse
ap = argparse.ArgumentParser(); ap.add_argument('--netlist',required=True); ap.add_argument('--outdir',required=True)
a = ap.parse_args()
os.makedirs(a.outdir, exist_ok=True)
# naive: ignore input, always emit a fixed 2-module answer
job = {"netlist": os.path.basename(a.netlist),
       "test_modules": [{"name":"TmRstCtrl","match_count":3,"first_line":2},{"name":"DL_PGenTm","match_count":2,"first_line":18}],
       "identifiers": {"test":["DL_PGenTm","TmRstCtrl","tm_en","tm_en_n"],"str":["str_clk_buf","str_sel"],"size":["size_div"]},
       "module_defs": {"TmRstCtrl":"module TmRstCtrl(clk,rst_n,tm_en,tm_en_n,rst_out);\\nendmodule","DL_PGenTm":"module DL_PGenTm(clk,tm_en,pgen);\\nendmodule"},
       "summary": {"n_modules":7,"n_test_modules":2,"n_test_ids":4,"n_str_ids":2,"n_size_ids":1}}
json.dump(job, open(os.path.join(a.outdir,'modules.json'),'w'))
open(os.path.join(a.outdir,'report.md'),'w').write("# Report\\n## Test Mode Modules\\n## Identifier Classification\\n## Module Definitions\\n")
'''
with open(os.path.join(NEG, "naive_stub.py"), "w") as f:
    f.write(naive)

# ---------- reference_submit.zip ----------
ref_submit = os.path.join(REF, "reference_submit.zip")
with zipfile.ZipFile(ref_submit, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(ref_gen, arcname="gen_testmode_report.py")

# ---------- negative_selftest.py ----------
nself = os.path.join(REF, "negative_selftest.py")
with open(nself, "w") as f:
    f.write('''# -*- coding: utf-8 -*-
"""Negative selftest: each negative, packaged in submit.zip, must FAIL check.
Run: python3 negative_selftest.py
"""
import os, sys, json, zipfile, subprocess, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
NEG = os.path.join(HERE, "negative")
sys.path.insert(0, HERE)
import check as CHK

NEGATIVES = ["empty_shell.py", "hardcode_a.py", "print_expected.py",
             "ref_core_deleted.py", "naive_stub.py"]

def make_zip(py):
    tmp = tempfile.mkdtemp()
    zp = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zp, "w") as zf:
        zf.write(os.path.join(NEG, py), arcname="gen_testmode_report.py")
    return zp, tmp

results = []
for n in NEGATIVES:
    zp, tmp = make_zip(n)
    try:
        CHK.check(zp, tmp)
        results.append((n, "PASS(BUG! should FAIL)", None))
    except AssertionError as e:
        # extract first FAIL label
        msg = str(e)
        first = msg.split(";")[0] if "FAIL" in msg else msg
        results.append((n, "FAIL(ok)", first))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

allok = True
for n, st, lbl in results:
    print("%-22s %s  %s" % (n, st, lbl or ""))
    if st.startswith("PASS"):
        allok = False
print("\\nALL NEGATIVES FAIL:", allok)
sys.exit(0 if allok else 1)
''')

print("negatives + ref_submit + selftest built")
