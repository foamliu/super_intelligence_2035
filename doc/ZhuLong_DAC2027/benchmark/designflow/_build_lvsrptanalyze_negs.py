#!/usr/bin/env python3
"""Build 6 negatives + negative_selftest.py for LvsRptAnalyze-001, then verify all FAIL."""
import json, os, shutil, subprocess, sys, tempfile, zipfile, importlib.util

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-LvsRptAnalyze-001"
REF = os.path.join(REPO, "reference", CID)
AST = os.path.join(REPO, "assets", CID)
NEG = os.path.join(REF, "negative")
os.makedirs(NEG, exist_ok=True)

# ── negative 1: empty_shell.py (does nothing) ──
EMPTY = '''#!/usr/bin/env python3
import argparse, os
ap = argparse.ArgumentParser()
ap.add_argument("--report", required=True); ap.add_argument("--ext", required=True)
ap.add_argument("--erc", required=True); ap.add_argument("--outdir", required=True)
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
# do nothing — no output files
print("empty shell")
'''
with open(os.path.join(NEG, "empty_shell.py"), "w") as f: f.write(EMPTY)

# ── negative 2: print_expected.py (prints expected strings, no real parsing) ──
PRINT_EXP = '''#!/usr/bin/env python3
import argparse, os, json
ap = argparse.ArgumentParser()
ap.add_argument("--report", required=True); ap.add_argument("--ext", required=True)
ap.add_argument("--erc", required=True); ap.add_argument("--outdir", required=True)
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
# Hardcode A's expected output (doesn't read B at all)
summary = {
    "top_cell": "Array3G_TOP_L", "lvs_result": "INCORRECT",
    "tool_version": "Calibre v2020.1_36.18", "report_lines": 1986972,
    "layout": "Array3G_TOP_L.gds", "source": "Array3G_TOP_L.cdl",
    "rule_settings": {"recognize_gates": "NONE", "filter_unused_option": "NONE SOURCE LAYOUT",
                      "virtual_connect_colon": "NO", "execute_erc": "YES"},
    "error_counts": {"connectivity_errors": 1, "property_errors": 3, "missing_smashed_mosfet": 1224,
                     "short_circuits": 0, "open_circuits": 2, "correct_cells": 4515, "incorrect_cells": 6},
    "property_errors": [{"disc": "#22", "layout_w": 2.717, "source_w": 1.476, "diff_pct": 84.1, "device": "MP(ptn)"}],
    "ext_warnings": {"open_circuit": 2, "unattached_label": 5, "unattached_port": 6,
                     "virtually_connected": 4, "stamping_conflict": 1},
    "ext_signals": {}, "erc": {"erc_errors": 0, "erc_warnings": 18, "detail": {}}
}
json.dump(summary, open(os.path.join(args.outdir, "error_summary.json"), "w"))
md = "# LVS 结果分析报告 — Array3G_TOP_L\\n\\n## 基本信息\\n...\\n## 根因分析\\n...\\n## 解决方案方向\\n...\\n"
open(os.path.join(args.outdir, "lvs_analysis_report.md"), "w").write(md)
print("print expected (A hardcoded)")
'''
with open(os.path.join(NEG, "print_expected.py"), "w") as f: f.write(PRINT_EXP)

# ── negative 3: core_deleted.py (parses header but drops property_errors + root cause) ──
CORE_DEL = '''#!/usr/bin/env python3
import argparse, os, re, json
ap = argparse.ArgumentParser()
ap.add_argument("--report", required=True); ap.add_argument("--ext", required=True)
ap.add_argument("--erc", required=True); ap.add_argument("--outdir", required=True)
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
report = open(args.report, errors="replace").read()
top_cell = re.search(r"#\\s*Cell:\\s*(\\S+)", report)
overall = re.search(r"Overall LVS Result:\\s*(\\S+)", report)
smashed = re.search(r"missing smashed mosfet:\\s*(\\d+)", report)
summary = {
    "top_cell": top_cell.group(1) if top_cell else None,
    "lvs_result": overall.group(1) if overall else None,
    "tool_version": None, "report_lines": None, "layout": None, "source": None,
    "rule_settings": {},
    "error_counts": {"connectivity_errors": 0, "property_errors": 0,
                     "missing_smashed_mosfet": int(smashed.group(1)) if smashed else 0,
                     "short_circuits": 0, "open_circuits": 0, "correct_cells": 0, "incorrect_cells": 0},
    "property_errors": [],  # core deleted: no property error parsing
    "ext_warnings": {}, "ext_signals": {}, "erc": {}
}
json.dump(summary, open(os.path.join(args.outdir, "error_summary.json"), "w"))
# report missing root cause + solution sections
md = "# LVS Report\\n\\n## 基本信息\\n| Top Cell | %s |\\n" % summary["top_cell"]
md += "\\n## 总体错误摘要\\n| Result | %s |\\n" % summary["lvs_result"]
# NO 根因 / 解决方案 sections
open(os.path.join(args.outdir, "lvs_analysis_report.md"), "w").write(md)
print("core deleted")
'''
with open(os.path.join(NEG, "core_deleted.py"), "w") as f: f.write(CORE_DEL)

# ── negative 4: naive_hardcode_a.py (hardcodes A's tool version + ext counts, doesn't parse) ──
NAIVE_A = '''#!/usr/bin/env python3
import argparse, os, json
ap = argparse.ArgumentParser()
ap.add_argument("--report", required=True); ap.add_argument("--ext", required=True)
ap.add_argument("--erc", required=True); ap.add_argument("--outdir", required=True)
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
# naive: always report A's tool version + ext counts regardless of input
summary = {
    "top_cell": "generic", "lvs_result": "INCORRECT",
    "tool_version": "Calibre v2020.1_36.18",  # hardcoded A version
    "report_lines": 0, "layout": None, "source": None,
    "rule_settings": {"recognize_gates": "NONE", "filter_unused_option": "NONE",
                      "virtual_connect_colon": "NO", "execute_erc": "YES"},
    "error_counts": {"connectivity_errors": 1, "property_errors": 3, "missing_smashed_mosfet": 1224,
                     "short_circuits": 0, "open_circuits": 2, "correct_cells": 0, "incorrect_cells": 6},
    "property_errors": [{"disc": "#1", "layout_w": 2.717, "source_w": 1.476, "diff_pct": 84.1, "device": "MP"}],
    "ext_warnings": {"open_circuit": 2, "unattached_label": 5, "unattached_port": 6,
                     "virtually_connected": 4, "stamping_conflict": 1},  # hardcoded A counts
    "ext_signals": {}, "erc": {"erc_errors": 0, "erc_warnings": 18, "detail": {}}
}
json.dump(summary, open(os.path.join(args.outdir, "error_summary.json"), "w"))
md = "# LVS Report\\n\\n## 基本信息\\n| Top Cell | generic |\\n| 工具版本 | Calibre v2020.1 |\\n"
md += "\\n## 总体错误摘要\\n| Result | INCORRECT |\\n"
md += "\\n## 根因分析\\n- Smashed MOSFET 匹配混乱\\n"
md += "\\n## 解决方案方向\\n- 修正 label 命名，检查 svdb，用 RVE 可视化\\n"
open(os.path.join(args.outdir, "lvs_analysis_report.md"), "w").write(md)
print("naive hardcode A")
'''
with open(os.path.join(NEG, "naive_hardcode_a.py"), "w") as f: f.write(NAIVE_A)

# ── negative 5: naive_no_correct.py (always says INCORRECT, doesn't handle CORRECT case) ──
NAIVE_CORR = '''#!/usr/bin/env python3
import argparse, os, re, json
ap = argparse.ArgumentParser()
ap.add_argument("--report", required=True); ap.add_argument("--ext", required=True)
ap.add_argument("--erc", required=True); ap.add_argument("--outdir", required=True)
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
report = open(args.report, errors="replace").read()
# naive: parse top_cell + ext counts, but ALWAYS report INCORRECT (never handles CORRECT case)
top_cell = re.search(r"#\\s*Cell:\\s*(\\S+)", report)
ext = open(args.ext, errors="replace").read()
oc = ext.count("Open circuit - Same name")
ul = ext.count("Unattached label")
summary = {
    "top_cell": top_cell.group(1) if top_cell else None,
    "lvs_result": "INCORRECT",  # always INCORRECT — fails B2 (CORRECT case)
    "tool_version": None, "report_lines": None, "layout": None, "source": None,
    "rule_settings": {},
    "error_counts": {"connectivity_errors": 1, "property_errors": 0, "missing_smashed_mosfet": 0,
                     "short_circuits": 0, "open_circuits": 0, "correct_cells": 0, "incorrect_cells": 0},
    "property_errors": [],
    "ext_warnings": {"open_circuit": oc, "unattached_label": ul, "unattached_port": 0,
                     "virtually_connected": 0, "stamping_conflict": 0},
    "ext_signals": {}, "erc": {}
}
json.dump(summary, open(os.path.join(args.outdir, "error_summary.json"), "w"))
md = "# LVS Report\\n\\n## 基本信息\\n| Top Cell | %s |\\n" % summary["top_cell"]
md += "\\n## 总体错误摘要\\n| Result | INCORRECT |\\n"
md += "\\n## 根因分析\\n- 信号交叉\\n\\n## 解决方案方向\\n- 修正 label，检查 svdb，RVE 可视化\\n"
open(os.path.join(args.outdir, "lvs_analysis_report.md"), "w").write(md)
print("naive no correct")
'''
with open(os.path.join(NEG, "naive_no_correct.py"), "w") as f: f.write(NAIVE_CORR)

# ── negative 6: naive_wrong_smashed.py (parses but counts smashed wrong — uses 'Unbalanced' count from wrong place) ──
NAIVE_SMASH = '''#!/usr/bin/env python3
import argparse, os, re, json
ap = argparse.ArgumentParser()
ap.add_argument("--report", required=True); ap.add_argument("--ext", required=True)
ap.add_argument("--erc", required=True); ap.add_argument("--outdir", required=True)
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
report = open(args.report, errors="replace").read()
ext = open(args.ext, errors="replace").read()
top_cell = re.search(r"#\\s*Cell:\\s*(\\S+)", report)
overall = re.search(r"Overall LVS Result:\\s*(\\S+)", report)
# naive: smashed = count of 'smashed' word in whole report (over-counts: matches 'Unbalanced smashed' + 'missing smashed')
smashed = report.lower().count("smashed")
oc = ext.count("Open circuit - Same name")
ul = ext.count("Unattached label")
# parse property errors
pes = []
for m in re.finditer(r"Property Error\\s+(#\\d+):.*?Layout W\\s*=\\s*([\\d.]+)u.*?Source W\\s*=\\s*([\\d.]+)u", report):
    pes.append({"disc": m.group(1), "layout_w": float(m.group(2)), "source_w": float(m.group(3)), "diff_pct": 50.0, "device": "?"})
summary = {
    "top_cell": top_cell.group(1) if top_cell else None,
    "lvs_result": overall.group(1) if overall else None,
    "tool_version": None, "report_lines": None, "layout": None, "source": None,
    "rule_settings": {"recognize_gates": None, "filter_unused_option": None,
                      "virtual_connect_colon": None, "execute_erc": None},
    "error_counts": {"connectivity_errors": 1, "property_errors": len(pes),
                     "missing_smashed_mosfet": smashed,  # WRONG: counts all 'smashed' occurrences
                     "short_circuits": 0, "open_circuits": 0, "correct_cells": 0, "incorrect_cells": 0},
    "property_errors": pes,
    "ext_warnings": {"open_circuit": oc, "unattached_label": ul, "unattached_port": 0,
                     "virtually_connected": 0, "stamping_conflict": 0},
    "ext_signals": {}, "erc": {}
}
json.dump(summary, open(os.path.join(args.outdir, "error_summary.json"), "w"))
md = "# LVS Report\\n\\n## 基本信息\\n| Top Cell | %s |\\n" % summary["top_cell"]
md += "\\n## 总体错误摘要\\n| Result | %s |\\n" % summary["lvs_result"]
md += "\\n## 错误类型详细分类\\n- Connectivity errors\\n- Property errors\\n"
md += "\\n## 根因分析\\n- 信号交叉\\n\\n## 解决方案方向\\n- 修正 label，检查 svdb，RVE 可视化\\n"
open(os.path.join(args.outdir, "lvs_analysis_report.md"), "w").write(md)
print("naive wrong smashed")
'''
with open(os.path.join(NEG, "naive_wrong_smashed.py"), "w") as f: f.write(NAIVE_SMASH)

# ── negative_selftest.py ──
SELFTTEST = '''#!/usr/bin/env python3
"""negative_selftest.py — run all negatives against check.py, expect ALL FAIL (NEG_RC=0)."""
import importlib.util, os, shutil, subprocess, sys, tempfile, zipfile, json

REF = os.path.dirname(os.path.abspath(__file__))
CHECK_PY = os.path.join(os.path.dirname(REF), "check.py")
CID_DIR = os.path.dirname(REF)
AST = os.path.join(os.path.dirname(CID_DIR), "..", "assets", "EDA-Eval-DesignFlow-LvsRptAnalyze-001")
AST = os.path.abspath(AST)

CHECK_PY = os.path.join(os.path.dirname(REF), "check.py")
spec = importlib.util.spec_from_file_location("check_mod", CHECK_PY)
check_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(check_mod)

negs = [f for f in os.listdir(REF) if f.endswith(".py") and f != "negative_selftest.py" and not f.startswith("_")]
negs.sort()
n_pass = 0; n_fail = 0; fails = []
for neg in negs:
    neg_py = os.path.join(REF, neg)
    tmp = tempfile.mkdtemp()
    submit_zip = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(submit_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(neg_py, arcname="analyze_lvs.py")
    try:
        r = check_mod.check(submit_zip, AST)
        ok = r.startswith("PASS")
    except Exception as e:
        r = "FAIL: " + str(e)[:120]; ok = False
    label = "PASS(BUG!)" if ok else "FAIL(ok)"
    if ok: n_pass += 1; fails.append(neg + " -> " + r)
    else: n_fail += 1
    print("  %s: %s -> %s" % (neg, label, r[:90]))
    shutil.rmtree(tmp, ignore_errors=True)

print("\\nNEG_RC=%d  (n_pass=%d n_fail=%d)" % (n_fail, n_pass, n_fail))
if n_pass > 0:
    print("FAILURES (negatives that incorrectly PASSED):")
    for f in fails: print("  ", f)
    sys.exit(1)
print("ALL NEGATIVES FAIL — OK")
'''
with open(os.path.join(NEG, "negative_selftest.py"), "w") as f: f.write(SELFTTEST)

# ── run negative_selftest ──
print("\n=== running negative_selftest ===")
r = subprocess.run([sys.executable, os.path.join(NEG, "negative_selftest.py")], capture_output=True, text=True, timeout=180)
print(r.stdout)
if r.returncode != 0:
    print("!!! NEGATIVE SELFTEST FAILED (some negative passed check)"); print(r.stderr); sys.exit(1)
print("negative_selftest OK — all 6 negatives FAIL")

# ── §4.9 three-fake submission test ──
# (a) empty_shell  (b) print_expected  (c) ref_core_deleted  — all must FAIL
print("\n=== §4.9 three-fake test ===")
spec2 = importlib.util.spec_from_file_location("check_mod", os.path.join(REF, "check.py"))
cm = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(cm)
submit_zip_ref = os.path.join(REF, "reference_submit.zip")
three_fake = ["empty_shell.py", "print_expected.py", "core_deleted.py"]
for neg in three_fake:
    tmp = tempfile.mkdtemp()
    sz = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(sz, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(NEG, neg), arcname="analyze_lvs.py")
    try:
        r = cm.check(sz, AST); ok = r.startswith("PASS")
    except Exception as e:
        r = "FAIL: " + str(e)[:120]; ok = False
    print("  %s: %s -> %s" % (neg, "PASS(BUG!)" if ok else "FAIL(ok)", r[:90]))
    if ok: print("!!! §4.9 fake %s PASSED — BUG" % neg); sys.exit(1)
    shutil.rmtree(tmp, ignore_errors=True)
print("§4.9 three-fake all FAIL — OK")
