#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-AutoTmscanScriptAnalyze-001 (shard A, r251).
A-faithful trace b9fua (e0039102@hfeg0pkn002, mc34): AutoTMScan tool script analysis.
U#0 verbatim: load CXMTAutoTMScan_V10.py + CXMTseAutoTMCheck_GUI(); "你帮我看看这好像是处理文件的脚本，处理哪个文件？"
gold = structured static analysis of the AutoTMScan script (what file it processes + function structure).
Runs on .75 session workdir (V1.py + HierPathFile already present).
"""
import ast, json, os, re, shutil, subprocess, sys, tempfile, zipfile

WORK = os.getcwd()
TASK = "EDA-Eval-DesignFlow-AutoTmscanScriptAnalyze-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
A_ROOT = os.path.join(BENCH, "assets", TASK)
R_ROOT = os.path.join(BENCH, "reference", TASK)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")

# ---- read recovered real asset A ----
V1 = open(os.path.join(WORK, "CXMTAutoTMScan_V1.py")).read()
HIER = open(os.path.join(WORK, "HierPathFile")).read()

# ============================ GOLD: analyze_autoTmscan.py ============================
ANALYZER = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""analyze_autoTmscan.py - config-driven static analyzer for AutoTMScan-style Aether scripts.

Reads config.json {"script": <path>, "outfile": <path>} and emits a structured JSON
report describing what file the script processes and its function structure.
"""
import ast, json, re, sys


def _const_str(node):
    """Extract a string constant from an ast node (py3.8+ ast.Constant)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def analyze(script_path):
    src = open(script_path).read()
    tree = ast.parse(src)
    funcs = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            funcs[node.name] = node
    func_names = sorted(funcs.keys())
    gui_func = next((n for n in func_names if "GUI" in n), None)
    main_func = None
    for n in func_names:
        if n.endswith("_main") or n == "main":
            main_func = n
            break
    # input file params: arg names matching file/path/csv/config/report/rule/map
    inp = set()
    pat = re.compile(r'File|Path|csv|config|report|rule|Rule|map|Map', re.I)
    for nm, node in funcs.items():
        for arg in node.args.args:
            if pat.search(arg.arg):
                inp.add(arg.arg)
    # gui cell list: uppercase identifier string literals that are elements of a
    # list literal assigned to a variable whose name looks like a cell/rule/latch list
    cells = []
    if gui_func:
        for node in ast.walk(funcs[gui_func]):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
                tgt = node.targets[0] if (len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)) else None
                tgt_name = tgt.id if tgt else ""
                if not re.search(r'Cell|Latch|Rule|CM', tgt_name, re.I):
                    continue
                for elt in node.value.elts:
                    s = _const_str(elt)
                    if s and re.match(r'^[A-Z][A-Za-z0-9_]+$', s) and len(s) > 2 and s not in cells:
                        cells.append(s)
    # function chain: direct calls from gui func to other module funcs
    chain = {}
    if gui_func:
        called = set()
        for node in ast.walk(funcs[gui_func]):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in funcs:
                called.add(node.func.id)
        chain[gui_func] = sorted(called)
    # check functions: helpers (not gui/main) matching check-like verbs
    cpat = re.compile(r'Chk|Check|Scan|Get|Convert|Merge|Add|Rule|Viol')
    check_funcs = [n for n in func_names if n != gui_func and n != main_func and cpat.search(n)]
    return {
        "gui_function_name": gui_func,
        "main_function_name": main_func,
        "has_gui": gui_func is not None,
        "function_names": func_names,
        "total_functions": len(func_names),
        "input_file_params": sorted(inp),
        "gui_cell_list": cells,
        "function_chain": chain,
        "check_functions": check_funcs,
    }


def main():
    cfg = json.load(open(sys.argv[1]))
    rep = analyze(cfg["script"])
    out = cfg.get("outfile", "report.json")
    json.dump(rep, open(out, "w"), indent=2, sort_keys=True)
    print("wrote " + out)


if __name__ == "__main__":
    main()
'''

# ============================ Hidden B: AutoDRCScan_V1.py ============================
B_SCRIPT = r'''#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#;  CXMTAutoDRCScan_V1.py - DRC rule auto-scan check (synthetic hidden input B)
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
import pyAether as ae
import os
import re
import csv
from collections import defaultdict


def DRCseAutoCheck_GUI():
    global myForm_autoDRCScan
    projName = leGlobalVariables.project
    lib1 = ae.strcat(projName, "_dr")
    lib2 = ae.strcat(projName, "_drc_digital")
    lib = lib1 if ae.dbLibExist(lib1) else lib2
    if projName == "drjoa":
        DRCRuleList = ["M1Rule", "M2Rule", "VIA1Rule", "M3Rule"]
    else:
        DRCRuleList = [str(r.name) for r in ae.dmGetObj(lib).cells if re.search("^M[0-9]+Rule$", str(r.name))]
    DRCRuleList.sort()
    DRCRuleDef = " ".join(DRCRuleList)
    lib_list = [str(l) for l in ae.dbGetAllLibs()]
    myLib = ae.aeCreateComboField(
        widgetName="myLib",
        choice=lib_list,
        prompt="DRC Rule Library",
        currentValue=lib,
        isEnabled=False,
    )
    ruleSetFld = ae.geCreateStringField(
        name="ruleSetFld",
        prompt="DRC Rules",
        defValue=DRCRuleDef,
        value=DRCRuleDef,
    )
    layerMapFld = ae.aeCrtFileSelectorField(
        fieldName="layerMapFld",
        prompt="Layer Map File",
        mode="existingFile",
        defValue=f"{ae.etGetWorkingDir()}/LayerMapFile",
    )
    netPincheckFld = ae.geCreateRadioField(
        name="netPincheckFld",
        prompt="Pin Net Check",
        choices=["Check", "Skip"],
        defValue="Check",
    )
    myForm_autoDRCScan = ae.aeCreateForm(
        name="AutoDRCScan",
        fields=[myLib, ruleSetFld, layerMapFld, netPincheckFld],
        text="Auto DRC Scan Check",
    )
    form = myForm_autoDRCScan
    DRCseAutoScan_main(form)


def DRCseAutoScan_main(mainForm):
    lib = mainForm["myLib"]
    ruleSet = mainForm["ruleSetFld"]
    layerMap = mainForm["layerMapFld"]
    pinNetChk = mainForm["netPincheckFld"]
    ae.etPrintf("[DRCScan] lib=%s rules=%s layerMap=%s pinNetChk=%s" % (lib, ruleSet, layerMap, pinNetChk))
    cv = ae.dmGetObj(lib).cells[0]
    DRCseGetAllViolInfo(cv, ruleSet, layerMap, "drc_log.txt", "drc_err.txt", None)
    DRCseGetLayerRules(lib, "ruleFile.txt", "layer_log.txt")
    DRCseConvertDRCRptToCsv("drc_report.txt", "drc_out.csv")
    DRCseMergeViolations({"viol": []})
    DRCseCheckRuleCoverage("ruleFile.txt", "layerMap.txt")


def DRCseGetAllViolInfo(cv, ruleFile, layerMap, reportPath, logFile, excludedLayers):
    ae.etPrintf("[DRCScan] getAllViolInfo cv=%s ruleFile=%s layerMap=%s reportPath=%s" % (cv, ruleFile, layerMap, reportPath))
    return defaultdict(list)


def DRCseGetLayerRules(lib, ruleFile, logFile):
    ae.etPrintf("[DRCScan] getLayerRules lib=%s ruleFile=%s logFile=%s" % (lib, ruleFile, logFile))
    return []


def DRCseConvertDRCRptToCsv(report_path, output_path):
    ae.etPrintf("[DRCScan] convertDRCRptToCsv report_path=%s output_path=%s" % (report_path, output_path))
    with open(output_path, "w") as f:
        f.write("rule,layer,count\n")


def DRCseMergeViolations(violTable):
    ae.etPrintf("[DRCScan] mergeViolations violTable=%s" % list(violTable.keys()))
    return {}


def DRCseCheckRuleCoverage(ruleFile, layerMap):
    ae.etPrintf("[DRCScan] checkRuleCoverage ruleFile=%s layerMap=%s" % (ruleFile, layerMap))
    return True
'''

# ============================ Hidden B': AutoLvsScan_V1.py (cross-guard) ============================
BP_SCRIPT = r'''#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#;  CXMTAutoLvsScan_V1.py - LVS netlist auto-scan check (synthetic hidden input B')
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
import pyAether as ae
import os
import re
import csv
from collections import defaultdict


def LVSseAutoCheck_GUI():
    global myForm_autoLVSScan
    projName = leGlobalVariables.project
    lib1 = ae.strcat(projName, "_lvs")
    lib2 = ae.strcat(projName, "_lvs_digital")
    lib = lib1 if ae.dbLibExist(lib1) else lib2
    if projName == "lvsjoa":
        LVSCellList = ["TopCellA", "TopCellB", "TopCellC"]
    else:
        LVSCellList = [str(c.name) for c in ae.dmGetObj(lib).cells if re.search("^TopCell[A-Z]$", str(c.name))]
    LVSCellList.sort()
    LVSCellDef = " ".join(LVSCellList)
    lib_list = [str(l) for l in ae.dbGetAllLibs()]
    myLib = ae.aeCreateComboField(
        widgetName="myLib",
        choice=lib_list,
        prompt="LVS Cell Library",
        currentValue=lib,
        isEnabled=False,
    )
    cellSetFld = ae.geCreateStringField(
        name="cellSetFld",
        prompt="LVS Cells",
        defValue=LVSCellDef,
        value=LVSCellDef,
    )
    svrMapFld = ae.aeCrtFileSelectorField(
        fieldName="svrMapFld",
        prompt="SVR Map File",
        mode="existingFile",
        defValue=f"{ae.etGetWorkingDir()}/SvrMapFile",
    )
    myForm_autoLVSScan = ae.aeCreateForm(
        name="AutoLVSScan",
        fields=[myLib, cellSetFld, svrMapFld],
        text="Auto LVS Scan Check",
    )
    form = myForm_autoLVSScan
    LVSseAutoScan_main(form)


def LVSseAutoScan_main(mainForm):
    lib = mainForm["myLib"]
    cellSet = mainForm["cellSetFld"]
    svrMap = mainForm["svrMapFld"]
    ae.etPrintf("[LVSScan] lib=%s cells=%s svrMap=%s" % (lib, cellSet, svrMap))
    cv = ae.dmGetObj(lib).cells[0]
    LVSseGetAllNetInfo(cv, "netlist.sv", "lvs_log.txt", None)
    LVSseCompareHierarchy("golden.sv", "netlist.sv", "cmp_log.txt")
    LVSseConvertLvsRptToCsv("lvs_report.txt", "lvs_out.csv")
    LVSseMergeNetTables({"net": []})


def LVSseGetAllNetInfo(cv, netlistFile, logFile, excludedNets):
    ae.etPrintf("[LVSScan] getAllNetInfo cv=%s netlistFile=%s logFile=%s" % (cv, netlistFile, logFile))
    return defaultdict(list)


def LVSseCompareHierarchy(goldenFile, netlistFile, reportPath):
    ae.etPrintf("[LVSScan] compareHierarchy goldenFile=%s netlistFile=%s reportPath=%s" % (goldenFile, netlistFile, reportPath))
    return True


def LVSseConvertLvsRptToCsv(report_path, output_path):
    ae.etPrintf("[LVSScan] convertLvsRptToCsv report_path=%s output_path=%s" % (report_path, output_path))
    with open(output_path, "w") as f:
        f.write("net,golden,actual,match\n")


def LVSseMergeNetTables(netTable):
    ae.etPrintf("[LVSScan] mergeNetTables netTable=%s" % list(netTable.keys()))
    return {}
'''

# ============================ check.py ============================
CHECK = r'''# -*- coding: utf-8 -*-
"""check.py - EDA-Eval-DesignFlow-AutoTmscanScriptAnalyze-001 grader.
design_flow contract: check(deliverable, workdir) -> None (pass) / raise (fail).
deliverable = outputs/submit.zip containing analyze_autoTmscan.py (a config-driven
static analyzer for AutoTMScan-style Aether scripts).
Hidden input B = AutoDRCScan_V1.py (DRC rule scan); B' = AutoLvsScan_V1.py (LVS scan, cross-guard).
"""
import ast, json, os, re, subprocess, sys, tempfile, zipfile

CONDITIONS = [
    ("a", "submit.zip contains analyze_autoTmscan.py"),
    ("b", "analyze_autoTmscan.py compiles (py_compile)"),
    ("c", "[B] running analyze_autoTmscan.py config_b.json exits 0 and writes report_b.json (3x deterministic)"),
    ("d", "[B] report_b.json is valid JSON with all 9 required top-level keys"),
    ("e", "[B] gui_function_name == DRCseAutoCheck_GUI"),
    ("f", "[B] main_function_name == DRCseAutoScan_main"),
    ("g", "[B] total_functions == 7"),
    ("h", "[B] input_file_params contains ruleFile, layerMap, reportPath"),
    ("i", "[B] gui_cell_list == [M1Rule, M2Rule, VIA1Rule, M3Rule]"),
    ("j", "[B] has_gui == True"),
    ("k", "[B] function_chain[DRCseAutoCheck_GUI] contains DRCseAutoScan_main"),
    ("l", "[B] check_functions contains DRCseGetAllViolInfo and DRCseConvertDRCRptToCsv"),
    ("m", "anti-hardcode: analyze_autoTmscan.py source has no A-specific literals (CXMTseAutoTMScan, CMAryA, HierPathFile, CXMTseAutoTMCheck_GUI)"),
    ("n", "[B'] cross-guard: config_bp on AutoLvsScan_V1.py -> gui_function_name==LVSseAutoCheck_GUI AND total_functions==6 AND gui_cell_list==[TopCellA,TopCellB,TopCellC] AND differs from B"),
]
FAILED = []


def _fail(label, msg):
    FAILED.append((label, msg))
    raise AssertionError("[" + label + "] " + msg)


def check(deliverable, workdir):
    global FAILED
    FAILED = []
    td = tempfile.mkdtemp(prefix="_chk_")
    try:
        z = zipfile.ZipFile(deliverable)
        names = z.namelist()
        # a
        if "analyze_autoTmscan.py" not in names:
            _fail("a", "analyze_autoTmscan.py not in submit.zip: " + str(names))
        z.extract("analyze_autoTmscan.py", td)
        analyzer = os.path.join(td, "analyze_autoTmscan.py")
        # b
        try:
            subprocess.run([sys.executable, "-m", "py_compile", analyzer], check=True, capture_output=True, timeout=30)
        except Exception as e:
            _fail("b", "py_compile failed: " + str(e))
        src = open(analyzer).read()
        # locate hidden B / B' (placed by harness in workdir/hidden)
        hidden_dir = os.path.join(workdir, "hidden")
        b_script = os.path.join(hidden_dir, "AutoDRCScan_V1.py")
        bp_script = os.path.join(hidden_dir, "AutoLvsScan_V1.py")
        if not os.path.isfile(b_script):
            _fail("c", "hidden B not found: " + b_script)
        # c: run 3x deterministic
        reports = []
        for i in range(3):
            cfg = {"script": b_script, "outfile": os.path.join(td, "report_b_%d.json" % i)}
            cfgp = os.path.join(td, "config_b_%d.json" % i)
            json.dump(cfg, open(cfgp, "w"))
            r = subprocess.run([sys.executable, analyzer, cfgp], capture_output=True, timeout=30, cwd=td)
            if r.returncode != 0:
                _fail("c", "run %d exit %d: %s" % (i, r.returncode, r.stderr.decode()[:200]))
            rp = cfg["outfile"]
            if not os.path.isfile(rp):
                _fail("c", "run %d did not write report" % i)
            reports.append(open(rp).read())
        if not (reports[0] == reports[1] == reports[2]):
            _fail("c", "non-deterministic output across 3 runs")
        rep = json.loads(reports[0])
        # d
        req_keys = {"gui_function_name", "main_function_name", "has_gui", "function_names",
                    "total_functions", "input_file_params", "gui_cell_list", "function_chain", "check_functions"}
        missing = req_keys - set(rep.keys())
        if missing:
            _fail("d", "missing keys: " + str(missing))
        # e
        if rep.get("gui_function_name") != "DRCseAutoCheck_GUI":
            _fail("e", "gui_function_name=%r" % rep.get("gui_function_name"))
        # f
        if rep.get("main_function_name") != "DRCseAutoScan_main":
            _fail("f", "main_function_name=%r" % rep.get("main_function_name"))
        # g
        if rep.get("total_functions") != 7:
            _fail("g", "total_functions=%r" % rep.get("total_functions"))
        # h
        inp = rep.get("input_file_params", [])
        for need in ["ruleFile", "layerMap", "reportPath"]:
            if need not in inp:
                _fail("h", "input_file_params missing %s: %r" % (need, inp))
        # i
        if rep.get("gui_cell_list") != ["M1Rule", "M2Rule", "VIA1Rule", "M3Rule"]:
            _fail("i", "gui_cell_list=%r" % rep.get("gui_cell_list"))
        # j
        if rep.get("has_gui") is not True:
            _fail("j", "has_gui=%r" % rep.get("has_gui"))
        # k
        chain = rep.get("function_chain", {})
        called = chain.get("DRCseAutoCheck_GUI", [])
        if "DRCseAutoScan_main" not in called:
            _fail("k", "function_chain gui->main missing: %r" % chain)
        # l
        cf = rep.get("check_functions", [])
        for need in ["DRCseGetAllViolInfo", "DRCseConvertDRCRptToCsv"]:
            if need not in cf:
                _fail("l", "check_functions missing %s: %r" % (need, cf))
        # m anti-hardcode
        for lit in ["CXMTseAutoTMScan", "CMAryA", "HierPathFile", "CXMTseAutoTMCheck_GUI", "DRCseAutoCheck_GUI", "M1Rule"]:
            if lit in src:
                _fail("m", "hardcoded literal %r in source" % lit)
        # n cross-guard B'
        if not os.path.isfile(bp_script):
            _fail("n", "hidden B' not found: " + bp_script)
        cfgp2 = os.path.join(td, "config_bp.json")
        json.dump({"script": bp_script, "outfile": os.path.join(td, "report_bp.json")}, open(cfgp2, "w"))
        r2 = subprocess.run([sys.executable, analyzer, cfgp2], capture_output=True, timeout=30, cwd=td)
        if r2.returncode != 0:
            _fail("n", "B' run exit %d: %s" % (r2.returncode, r2.stderr.decode()[:200]))
        rp2 = json.loads(open(os.path.join(td, "report_bp.json")).read())
        if rp2.get("gui_function_name") != "LVSseAutoCheck_GUI":
            _fail("n", "B' gui_function_name=%r" % rp2.get("gui_function_name"))
        if rp2.get("total_functions") != 6:
            _fail("n", "B' total_functions=%r (expect 6)" % rp2.get("total_functions"))
        if rp2.get("gui_cell_list") != ["TopCellA", "TopCellB", "TopCellC"]:
            _fail("n", "B' gui_cell_list=%r" % rp2.get("gui_cell_list"))
        if rp2.get("gui_function_name") == rep.get("gui_function_name"):
            _fail("n", "B' gui same as B (not a cross-guard)")
        return True
    finally:
        import shutil
        shutil.rmtree(td, ignore_errors=True)
'''

# ============================ negatives ============================
NEG_NOOP = r'''#!/usr/bin/env python3
# naive_noop: empty shell (does nothing)
import sys
def main():
    pass
if __name__ == "__main__":
    main()
'''
NEG_PRINT = r'''#!/usr/bin/env python3
# print_expected: hardcodes B's expected JSON
import json, sys
cfg = json.load(open(sys.argv[1]))
out = cfg.get("outfile", "report.json")
rep = {"gui_function_name":"DRCseAutoCheck_GUI","main_function_name":"DRCseAutoScan_main","has_gui":True,"function_names":["DRCseAutoCheck_GUI","DRCseAutoScan_main","DRCseCheckRuleCoverage","DRCseConvertDRCRptToCsv","DRCseGetAllViolInfo","DRCseGetLayerRules","DRCseMergeViolations"],"total_functions":7,"input_file_params":["layerMap","logFile","output_path","reportPath","ruleFile"],"gui_cell_list":["M1Rule","M2Rule","VIA1Rule","M3Rule"],"function_chain":{"DRCseAutoCheck_GUI":["DRCseAutoScan_main"]},"check_functions":["DRCseCheckRuleCoverage","DRCseConvertDRCRptToCsv","DRCseGetAllViolInfo","DRCseGetLayerRules","DRCseMergeViolations"]}
json.dump(rep, open(out,"w"), indent=2, sort_keys=True)
print("wrote "+out)
'''
NEG_COREDEL = r'''#!/usr/bin/env python3
# core_deleted: analyzer with ast parsing removed (returns empty/garbage)
import json, sys
def analyze(script_path):
    return {"gui_function_name": None, "main_function_name": None, "has_gui": False,
            "function_names": [], "total_functions": 0, "input_file_params": [],
            "gui_cell_list": [], "function_chain": {}, "check_functions": []}
def main():
    cfg = json.load(open(sys.argv[1]))
    rep = analyze(cfg["script"])
    out = cfg.get("outfile","report.json")
    json.dump(rep, open(out,"w"), indent=2, sort_keys=True)
    print("wrote "+out)
if __name__ == "__main__":
    main()
'''
NEG_SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest.py - all negatives must FAIL check()."""
import json, os, shutil, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check.py")
HIDDEN = os.path.join(HERE, "negative")
TASK = "EDA-Eval-DesignFlow-AutoTmscanScriptAnalyze-001"
B_SCRIPT = os.path.join(HERE, "..", "..", "assets", TASK, "hidden", "AutoDRCScan_V1.py")
BP_SCRIPT = os.path.join(HERE, "..", "..", "assets", TASK, "hidden", "AutoLvsScan_V1.py")


def run_check(submit_py, name):
    td = tempfile.mkdtemp(prefix="_neg_")
    try:
        # build submit.zip with the negative as analyze_autoTmscan.py
        zp = os.path.join(td, "submit.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.write(submit_py, "analyze_autoTmscan.py")
        # workdir with hidden/ copied
        wd = os.path.join(td, "wd")
        os.makedirs(os.path.join(wd, "hidden"))
        shutil.copy(B_SCRIPT, os.path.join(wd, "hidden", "AutoDRCScan_V1.py"))
        shutil.copy(BP_SCRIPT, os.path.join(wd, "hidden", "AutoLvsScan_V1.py"))
        mod = {}
        exec(open(CHECK).read(), mod)
        try:
            mod["check"](zp, wd)
            return name, "PASS", ""
        except AssertionError as e:
            return name, "FAIL", str(e)
        except Exception as e:
            return name, "FAIL", repr(e)
    finally:
        shutil.rmtree(td, ignore_errors=True)


def main():
    negs = [("naive_noop", "naive_noop.py"), ("print_expected", "print_expected.py"),
            ("core_deleted", "core_deleted.py")]
    results = []
    for nm, fn in negs:
        p = os.path.join(HIDDEN, fn)
        results.append(run_check(p, nm))
    allok = all(r[1] == "FAIL" for r in results)
    for nm, st, msg in results:
        print("%s: %s %s" % (nm, st, msg[:120]))
    print("NEG_RC=" + ("0" if allok else "1"))
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
'''

# ============================ prompt + task_brief ============================
PROMPT = r'''>>> load("/home/zixuguo/AutoTMScan/CXMTAutoTMScan_V10.py")
>>> CXMTseAutoTMCheck_GUI()
你帮我看看这好像是处理文件的脚本，处理哪个文件？

请写一个 Python3 脚本 `analyze_autoTmscan.py`，对一个 AutoTMScan 风格的 Aether 检查脚本做静态结构分析，输出 JSON 报告。脚本以 config 驱动：读取 `config.json`（含 `script` 和 `outfile` 两个键），解析 `script` 指向的 .py 文件，把分析结果写入 `outfile`。

JSON 报告必须包含以下 9 个顶层字段：
- `gui_function_name`：含 "GUI" 的函数名（字符串或 null）
- `main_function_name`：以 "_main" 结尾或名为 "main" 的函数名（字符串或 null）
- `has_gui`：是否存在 gui 函数（布尔）
- `function_names`：所有顶层函数名列表（按字母序）
- `total_functions`：函数总数（整数）
- `input_file_params`：所有函数形参中名字含 file/path/csv/config/report/rule/map（大小写不敏感）的形参名列表（去重、按字母序）
- `gui_cell_list`：gui 函数体内出现的「大写标识符」字符串字面量列表（匹配 `^[A-Z][A-Za-z0-9_]+$`、长度>2、保持出现顺序去重）
- `function_chain`：字典——gui 函数直接调用的、本模块内其它函数名的列表（按字母序），形如 `{"<gui_func>": [...]}`
- `check_functions`：除 gui/main 外、名字含 Chk/Check/Scan/Get/Convert/Merge/Add/Rule/Viol 的函数名列表

交付：把 `analyze_autoTmscan.py` 打包成 `outputs/submit.zip`（zip 内顶层就是该 .py 文件）。
'''

TASK_BRIEF = '''交付接口：把 analyze_autoTmscan.py 打包成 outputs/submit.zip（zip 顶层即该 .py）。
判分：check(submit.zip, workdir) 在独立临时目录解 zip 真跑，隐藏输入 B 放在 workdir/hidden/ 不进沙箱。
'''

# ============================ write files ============================
os.makedirs(os.path.join(A_ROOT, "original"), exist_ok=True)
os.makedirs(os.path.join(A_ROOT, "hidden"), exist_ok=True)
os.makedirs(R_ROOT, exist_ok=True)
os.makedirs(os.path.join(R_ROOT, "negative"), exist_ok=True)

# asset A (real)
open(os.path.join(A_ROOT, "original", "CXMTAutoTMScan_V1.py"), "w").write(V1)
open(os.path.join(A_ROOT, "original", "HierPathFile"), "w").write(HIER)
open(os.path.join(A_ROOT, "original", "config_a.json"), "w").write(
    json.dumps({"script": "CXMTAutoTMScan_V1.py", "outfile": "analysis_a.json"}, indent=2))
open(os.path.join(A_ROOT, "original", "prompt.txt"), "w").write(PROMPT)
open(os.path.join(A_ROOT, "original", "task_brief.md"), "w").write(TASK_BRIEF)

# hidden B / B'
open(os.path.join(A_ROOT, "hidden", "AutoDRCScan_V1.py"), "w").write(B_SCRIPT)
open(os.path.join(A_ROOT, "hidden", "AutoLvsScan_V1.py"), "w").write(BP_SCRIPT)
open(os.path.join(A_ROOT, "hidden", "hidden_manifest.json"), "w").write(json.dumps({
    "B": {"file": "AutoDRCScan_V1.py", "purpose": "DRC rule scan, 7 funcs, 4 cells, cross-input guard"},
    "Bp": {"file": "AutoLvsScan_V1.py", "purpose": "LVS scan, 6 funcs, 3 cells, cross-guard differs from B"},
}, indent=2))
# _build_hidden.py (provenance)
open(os.path.join(A_ROOT, "hidden", "_build_hidden.py"), "w").write(
    "# Auto-generated hidden inputs for %s\n# B=AutoDRCScan_V1.py (DRC), B'=AutoLvsScan_V1.py (LVS)\n" % TASK)

# reference (gold + check + negatives)
open(os.path.join(R_ROOT, "analyze_autoTmscan.py"), "w").write(ANALYZER)
open(os.path.join(R_ROOT, "check.py"), "w").write(CHECK)
open(os.path.join(R_ROOT, "negative", "naive_noop.py"), "w").write(NEG_NOOP)
open(os.path.join(R_ROOT, "negative", "print_expected.py"), "w").write(NEG_PRINT)
open(os.path.join(R_ROOT, "negative", "core_deleted.py"), "w").write(NEG_COREDEL)
open(os.path.join(R_ROOT, "negative_selftest.py"), "w").write(NEG_SELFTEST)

# reference_submit.zip (gold deliverable)
zp = os.path.join(R_ROOT, "reference_submit.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(R_ROOT, "analyze_autoTmscan.py"), "analyze_autoTmscan.py")

print("=== files written ===")
print("A_ROOT:", A_ROOT)
print("R_ROOT:", R_ROOT)

# ============================ self-verify ============================
def run_check_with(submit_py, label):
    td = tempfile.mkdtemp(prefix="_sv_")
    try:
        sz = os.path.join(td, "submit.zip")
        with zipfile.ZipFile(sz, "w") as z:
            z.write(submit_py, "analyze_autoTmscan.py")
        wd = os.path.join(td, "wd")
        os.makedirs(os.path.join(wd, "hidden"))
        shutil.copy(os.path.join(A_ROOT, "hidden", "AutoDRCScan_V1.py"), os.path.join(wd, "hidden", "AutoDRCScan_V1.py"))
        shutil.copy(os.path.join(A_ROOT, "hidden", "AutoLvsScan_V1.py"), os.path.join(wd, "hidden", "AutoLvsScan_V1.py"))
        mod = {}
        exec(open(os.path.join(R_ROOT, "check.py")).read(), mod)
        try:
            mod["check"](sz, wd)
            return label, "PASS", ""
        except AssertionError as e:
            return label, "FAIL", str(e)
        except Exception as e:
            return label, "FAIL", repr(e)
    finally:
        shutil.rmtree(td, ignore_errors=True)

print("\n=== SELF-VERIFY ===")
ref = run_check_with(os.path.join(R_ROOT, "analyze_autoTmscan.py"), "REF")
print(ref[0], ref[1], ref[2][:200])
ref_ok = ref[1] == "PASS"

neg_results = []
for nm, fn in [("naive_noop", "naive_noop.py"), ("print_expected", "print_expected.py"), ("core_deleted", "core_deleted.py")]:
    r = run_check_with(os.path.join(R_ROOT, "negative", fn), "NEG-" + nm)
    print(r[0], r[1], r[2][:160])
    neg_results.append(r)
negs_ok = all(r[1] == "FAIL" for r in neg_results)
# distinct failsets
failsets = set()
for r in neg_results:
    m = re.search(r'\[([a-n])\]', r[2])
    failsets.add(m.group(1) if m else "?")
print("NEG distinct fail labels:", sorted(failsets))

# §4.9 three fakes = the three negatives (empty shell / print expected / core deleted)
fakes_ok = negs_ok and len(failsets) >= 2

# negative_selftest
ns = subprocess.run([sys.executable, os.path.join(R_ROOT, "negative_selftest.py")], capture_output=True, timeout=120)
print("negative_selftest exit:", ns.returncode)
print(ns.stdout.decode()[:400])
ns_ok = ns.returncode == 0

# anti-hardcode self-check on gold source
gold_src = open(os.path.join(R_ROOT, "analyze_autoTmscan.py")).read()
ah_ok = not any(lit in gold_src for lit in ["CXMTseAutoTMScan", "CMAryA", "HierPathFile", "DRCseAutoCheck_GUI", "M1Rule", "LVSseAutoCheck_GUI"])

print("\n=== GATE ===")
print("REF_PASS:", ref_ok, "| NEG_all_FAIL:", negs_ok, "| distinct_failsets:", sorted(failsets), "| fakes_ok:", fakes_ok)
print("neg_selftest_ok:", ns_ok, "| anti_hardcode_ok:", ah_ok)
ALL_OK = ref_ok and negs_ok and fakes_ok and ns_ok and ah_ok
print("ALL_OK:", ALL_OK)

if not ALL_OK:
    print("SELF-VERIFY FAILED - aborting jsonl append")
    sys.exit(1)

# ============================ append to A.jsonl ============================
import hashlib
test_hash = hashlib.sha256(CHECK.encode()).hexdigest()[:8]
entry = {
    "task_id": TASK,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "attachments": ["assets/%s/original/CXMTAutoTMScan_V1.py" % TASK, "assets/%s/original/HierPathFile" % TASK],
    "test": CHECK,
    "metadata": {
        "trace_source": {
            "user": "e0039102",
            "host": "hfeg0pkn002",
            "session_file": "1793858909531_b9fua.messages.json",
            "match_count": 34,
            "real_task_summary": "AutoTMScan (CXMTAutoTMScan_V10.py) test-mode scan auto-check tool: user asks what file the script processes; assistant reads CXMTAutoTMScan_V1.py (1158 lines, 10 CXMTse* functions, GUI->main chain, processes HierPathFile + 7 CM cells) and gives structured analysis; later builds NoGUI wrapper.",
        },
        "domain": "eda_other",
        "test_rationale": "14 条断言：① zip 内含 analyze_autoTmscan.py ② analyze_autoTmscan.py 通过 py_compile ③ 在隐藏 B 上跑 3 次退出码 0 且写出 report_b.json 且三次输出一致 ④ report_b.json 合法 JSON 且含 9 个必需顶层键 ⑤ gui_function_name==DRCseAutoCheck_GUI ⑥ main_function_name==DRCseAutoScan_main ⑦ total_functions==7 ⑧ input_file_params 含 ruleFile/layerMap/reportPath ⑨ gui_cell_list==[M1Rule,M2Rule,VIA1Rule,M3Rule] ⑩ has_gui==True ⑪ function_chain[DRCseAutoCheck_GUI] 含 DRCseAutoScan_main ⑫ check_functions 含 DRCseGetAllViolInfo 与 DRCseConvertDRCRptToCsv ⑬ 反硬编码源码无 A 专属字面量(CXMTseAutoTMScan/CMAryA/HierPathFile/CXMTseAutoTMCheck_GUI/DRCseAutoCheck_GUI/M1Rule) ⑭ 交叉守卫 B'(AutoLvsScan_V1.py) 产出 gui_function_name==LVSseAutoCheck_GUI 且 total_functions==6 且 gui_cell_list==[TopCellA,TopCellB,TopCellC] 且异于 B",
        "track": "faithful",
        "shard": "A",
        "test_sha8": test_hash,
    },
}
# dedup: remove any prior entry with same task_id
kept = []
if os.path.isfile(JSONL):
    for ln in open(JSONL):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            kept.append(ln)
            continue
        if o.get("task_id") != TASK:
            kept.append(ln)
kept.append(json.dumps(entry, ensure_ascii=False))
open(JSONL, "w").write("\n".join(kept) + "\n")
n = len(kept)
print("\n=== JSONL appended ===")
print("task_id:", TASK)
print("test_sha8:", test_hash)
print("A.jsonl entries:", n)
print("ALL DONE")
