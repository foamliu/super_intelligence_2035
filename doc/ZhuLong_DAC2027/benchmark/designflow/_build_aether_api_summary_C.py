#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-AetherApiSummary-001 (shard C, layout_aether).
B-档 synthesized L1-boundary: analyze mock aether python_ae codebase -> structured report.

Generates:
  assets/AetherApiSummary-001/inputs/python_ae_A/...   (visible fixture A)
  assets/AetherApiSummary-001/inputs/prompt_aether_api_summary.md
  assets/AetherApiSummary-001/inputs/task_brief.md
  assets/AetherApiSummary-001/hidden/python_ae_B/...   (hidden fixture B)
  assets/AetherApiSummary-001/hidden/hidden_manifest.json
  reference/AetherApiSummary-001/aether_api_summary_ref.py
  reference/AetherApiSummary-001/check.py
  reference/AetherApiSummary-001/negative/*.py
  reference/AetherApiSummary-001/negative_selftest.py
  reference/AetherApiSummary-001/reference_submit.zip
"""
import os, json, zipfile, io, textwrap

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "AetherApiSummary-001"
ASSET = os.path.join(ROOT, "assets", CASE)
REF = os.path.join(ROOT, "reference", CASE)

# ---------- fixture A (visible) ----------
A_FILES = {
"python_ae_A/le/leBasicEdit.py": '''# le basic edit - layout editor helpers (CXMTleBasicFuncs family)
# @attrs CellView: libName, cellName, viewName, cellViewType, instances, shapes, signals
import ae
import db

def open_cell(lib, cell):
    try:
        cv = ae.aeGetCurDesign()
        if cv is None:
            cv = db.dbOpenCV(lib, cell, "layout", "r")
        return cv
    except Exception as e:
        print(e)
        return None

def find_overlaps(cv, bbox):
    try:
        shapes = db.dbGetTrueOverlapsEx(cv, bbox, 0)
        return shapes
    except Exception as e:
        print(e)
        return []

def close_cell(cv):
    try:
        db.dbCloseCV(cv)
    except Exception as e:
        print(e)
''',
"python_ae_A/le/lePlace.py": '''# le place - placement helpers
# @attrs Instance: name, libName, cellName, master, origin, orient, bbox, cdfParameter
import ae
import db

def place_inst(cv, master, x, y):
    try:
        cur = ae.aeGetCurDesign()
        db.dbOpenCV(cur.libName, cur.cellName, "layout", "r")
        inst = db.dbCreateInst(cur, master, "I0", (x, y), "R0")
        return inst
    except Exception as e:
        print(e)
    finally:
        try:
            db.dbCloseCV(cur)
        except Exception as e:
            print(e)
''',
"python_ae_A/se/seSchematic.py": '''# se schematic - circuit editor helpers
# @attrs Net: name, figs, terms
# @attrs Terminal: name, net
import db

def find_net(cv, netname):
    try:
        net = db.dbFindNetByName(cv, netname)
        return net
    except Exception as e:
        print(e)
        return None

def switch_master(cv, inst, newmaster):
    try:
        db.dbGetAnyInstSwitchMaster(cv, inst, newmaster)
        db.dbFindNetByName(cv, "vdd!")
    except Exception as e:
        print(e)

def open_se(lib, cell):
    try:
        cv = db.dbOpenCV(lib, cell, "schematic", "r")
        return cv
    except Exception as e:
        print(e)
    finally:
        try:
            db.dbCloseCV(cv)
        except Exception as e:
            pass
''',
"python_ae_A/db/CXMTdbCommonFunc.py": '''# CXMT db common funcs - DB base utilities
import db

def CXMTleStreamOut(cv, path):
    try:
        db.dbOpenCV(cv.libName, cv.cellName, "layout", "r")
        out = stream_out(cv, path)
        return out
    except Exception as e:
        print(e)
    finally:
        try:
            db.dbCloseCV(cv)
        except Exception as e:
            print(e)

def CXMTleStreamIn(cv, path):
    try:
        db.dbOpenCV(cv.libName, cv.cellName, "layout", "r")
        return stream_in(cv, path)
    except Exception as e:
        print(e)
    finally:
        try:
            db.dbCloseCV(cv)
        except Exception as e:
            print(e)
''',
"python_ae_A/ut/IMCutHierarchyTraverser.py": '''# hierarchy traverser - ut utilities
# @attrs HierQueryResult: object, hierPath, getDepth
import db

class InnoutHierarchyTraverser:
    def __init__(self, cv):
        self.cv = cv
        self.visited = set()
    def walk(self):
        try:
            res = db.dbGetAnyInstSwitchMaster(self.cv, None, None)
            return InnoutHierarchyTraverser(self.cv)
        except Exception as e:
            print(e)
    def deep(self):
        try:
            return InnoutHierarchyTraverser(self.cv)
        except Exception as e:
            print(e)
''',
"python_ae_A/IAPR/cxmt_AIAPR_getPinInfo.py": '''# AI APR - pin info extraction (GOA geometry op API)
import goa
import ae

def get_pin_info(cv):
    try:
        goa.goaInit(cv)
        layer = goa.goaLayerFromCellView(cv)
        nl = goa.goaNewLayer(cv, "M1")
        return layer
    except Exception as e:
        print(e)

def aiapr_flow(cv):
    try:
        tech = getTech(cv)
        insts = getInstsInfo(cv)
        pins = getPinInfo(cv)
        nets = getNetInfo(cv)
        sch = getSchInfo(cv)
        pre = getPreRoutingInfo(cv)
        drawRouting(cv)
        doBatch(cv)
        return {"tech": tech, "insts": insts}
    except Exception as e:
        print(e)
''',
"python_ae_A/py_cck_code/ep_form.py": '''# CCK - form / net probe helpers
import ae

def make_form(name):
    try:
        form = ae.aeCrtAppForm(name)
        ae.aeCrtAppForm(name + "_2")
        return form
    except Exception as e:
        print(e)

def add_probe(cv, net):
    try:
        ae.aeAddNetProbe(cv, net)
    except Exception as e:
        print(e)
''',
"python_ae_A/common/common_set.py": '''# common settings - bindkey / callback / Config / lisp helpers
import ae

class Config:
    def __init__(self, d):
        self._d = d
    def __getattr__(self, k):
        return self._d.get(k)

leGlobalVariables = Config({"projRunsetPath": ".", "techLibPath": ".", "layerMap": "layer.map"})

def setup_bindkeys():
    try:
        ae.aeSetBindKey("Layout", "7", "route()")
        ae.aeSetBindKey("Layout", "0", "cancel()")
        ae.aeSetBindKey("Layout", "Del", "delete()")
        ae.aeRegisterCallback("form", open_form)
        ae.aeRegisterCallback("menu", open_menu)
    except Exception as e:
        print(e)

# lisp-style helpers
def car(lst): return lst[0]
def cadr(lst): return lst[1]
def mapc(fn, lst):
    for x in lst:
        fn(x)
def mapcar(fn, lst):
    return [fn(x) for x in lst]
''',
"python_ae_A/common/bindkeyBasic.py": '''# bindkey basics
import ae

def bind_basic():
    try:
        ae.aeSetBindKey("Layout", "Ctrl+a", "selectAll()")
        ae.aeSetBindKey("Layout", "Ctrl+s", "save()")
        ae.aeRegisterCallback("post_save", on_save)
    except Exception as e:
        print(e)
''',
}

# ---------- fixture B (hidden) ----------
B_FILES = {
"python_ae_B/le/leEdit.py": '''# le edit - layout editor (B fixture)
# @attrs CellView: libName, cellName, viewName, cellViewType, figs
# @attrs Shape: objType, layerName, purposeName, bbox, net, pin, lpName, text
import ae
import db

def open_layout(lib, cell):
    try:
        cv = ae.aeGetCurDesign()
        if cv is None:
            cv = db.dbOpenCV(lib, cell, "layout", "r")
        return cv
    except Exception as e:
        print(e)
        return None

def overlap_scan(cv, bbox):
    try:
        s1 = db.dbGetTrueOverlapsEx(cv, bbox, 0)
        s2 = db.dbGetTrueOverlapsEx(cv, bbox, 1)
        return s1 + s2
    except Exception as e:
        print(e)
        return []

def reopen(cv):
    try:
        db.dbOpenCV(cv.libName, cv.cellName, "layout", "r")
        ov = db.dbGetTrueOverlapsEx(cv, None, 0)
        db.dbCloseCV(cv)
    except Exception as e:
        print(e)
''',
"python_ae_B/se/seNet.py": '''# se net - circuit editor net helpers (B fixture)
# @attrs Net: name, figs, terms, driver
import db

def find_nets(cv, names):
    try:
        out = []
        for n in names:
            out.append(db.dbFindNetByName(cv, n))
        db.dbFindNetByName(cv, "vss!")
        return out
    except Exception as e:
        print(e)
        return []

def swap_master(cv, inst, m):
    try:
        db.dbGetAnyInstSwitchMaster(cv, inst, m)
        db.dbGetAnyInstSwitchMaster(cv, inst, m)
    except Exception as e:
        print(e)

def open_se(lib, cell):
    try:
        cv = db.dbOpenCV(lib, cell, "schematic", "r")
        db.dbCloseCV(cv)
        return cv
    except Exception as e:
        print(e)
''',
"python_ae_B/db/dbFuncs.py": '''# db funcs - DB base utilities (B fixture)
import db
import ae

def stream_in(cv, path):
    try:
        db.dbOpenCV(cv.libName, cv.cellName, "layout", "r")
        ae.dbUndoEnable(cv)
        return db.CXMTleStreamIn(cv, path)
    except Exception as e:
        print(e)
    finally:
        try:
            ae.dbUndoDisable(cv)
            db.dbCloseCV(cv)
        except Exception as e:
            print(e)

def stream_in_2(cv, path):
    try:
        db.dbOpenCV(cv.libName, cv.cellName, "layout", "r")
        db.dbOpenCV(cv.libName, cv.cellName, "layout", "r")
        return db.CXMTleStreamIn(cv, path)
    except Exception as e:
        print(e)
''',
"python_ae_B/ut/HierarchyTrav.py": '''# hierarchy traverser (B fixture)
# @attrs HierQueryResult: object, hierPath, getDepth
import db

class InnoutHierarchyTraverser:
    def __init__(self, cv):
        self.cv = cv
        self.visited = set()
    def walk(self):
        try:
            return InnoutHierarchyTraverser(self.cv)
        except Exception as e:
            print(e)
''',
"python_ae_B/IAPR/aiapr_route.py": '''# AI APR - routing flow (B fixture, GOA API)
import goa

def route_flow(cv):
    try:
        goa.goaInit(cv)
        nl1 = goa.goaNewLayer(cv, "M2")
        nl2 = goa.goaNewLayer(cv, "M3")
        drawRouting(cv)
        doBatch(cv)
        return nl1
    except Exception as e:
        print(e)
    try:
        goa.goaInit(cv)
    except Exception as e:
        print(e)
''',
"python_ae_B/mentor/calibre_wrap.py": '''# calibre wrapper - physical verify (B-only subdir)
import calibre

def run_drc(gds, deck):
    try:
        r1 = calibre.calibreDrc(gds, deck)
        r2 = calibre.calibreDrc(gds, deck + "_alt")
        return r1
    except Exception as e:
        print(e)

def run_lvs(gds, cdl, deck):
    try:
        return calibre.calibreLvs(gds, cdl, deck)
    except Exception as e:
        print(e)
''',
"python_ae_B/common/bindkey.py": '''# bindkey setup (B fixture, no Config, no lisp helpers)
import ae

def bind_setup():
    try:
        ae.aeSetBindKey("Layout", "Ctrl+a", "selectAll()")
        ae.aeSetBindKey("Layout", "Ctrl+d", "delete()")
        ae.aeRegisterCallback("post", on_post)
    except Exception as e:
        print(e)
''',
}

# ---------- ref generator (aether_api_summary_ref.py) ----------
REF_GEN = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Aether pyAether API & DB-processing summary report generator.
Scans a mock python_ae codebase, categorizes files by subdirectory, extracts API
call sites, DB-processing patterns, object attributes and design patterns, and
emits a structured markdown report + a machine-readable summary.json.

Spec (API extraction):
  API identifier = prefix in {ae,db,goa,calibre,CXMT,IMC,Innout} + camelCase rest.
  For prefix in {CXMT,IMC,Innout} the rest may start lowercase; otherwise the rest
  must contain >= 1 uppercase letter (this excludes the plain word "aether").
  The word "aether" itself is excluded explicitly.
DB patterns:
  dbOpenCV_count / dbCloseCV_count / dbGet_count (keys starting dbGet) /
  undo_enabled (any key starting dbUndo) / readonly_mode_used (mode = "r").
Object attributes: lines `# @attrs <Class>: a1, a2, ...`.
Design patterns: try_except_count (^\s*try:) / config_class_used (Config( or class Config) /
  lisp_helpers_used (car|cadr|caddr|cddr|cons|append1|assoc|nthelem|mapc|mapcar|mapcan|maplist|
                     rexCompile|rexExecute|rexSubstitute|rexReplace) \(
  goa_api_used (any key starting goa).
"""
import os, re, sys, json, argparse, hashlib

API_RE = re.compile(r'\b(ae|db|goa|calibre|CXMT|IMC|Innout)([A-Za-z][A-Za-z0-9_]*)')
LISP_RE = re.compile(r'\b(car|cadr|caddr|cddr|cons|append1|assoc|nthelem|mapc|mapcar|mapcan|maplist|rexCompile|rexExecute|rexSubstitute|rexReplace)\s*\(')
TRY_RE = re.compile(r'^\s*try\s*:', re.MULTILINE)
RO_RE = re.compile(r'mode\s*=\s*("r"|\'r\')')
ATTRS_RE = re.compile(r'#\s*@attrs\s+(\w+)\s*:\s*([A-Za-z0-9_,\s]+)')

CATEGORY_DESC = {
    "le": "layout-edit", "se": "schematic-edit", "db": "db-base",
    "ut": "hierarchy-traverse", "IAPR": "ai-apr", "py_cck_code": "cck",
    "common": "bindkey-menu", "mentor": "calibre-wrap",
}

def extract_apis(text):
    apis = {}
    for m in API_RE.finditer(text):
        prefix, rest = m.group(1), m.group(2)
        full = prefix + rest
        if full == "aether":
            continue
        if prefix in ("CXMT", "IMC", "Innout"):
            ok = True
        else:
            ok = any(c.isupper() for c in rest)
        if ok:
            apis[full] = apis.get(full, 0) + 1
    return apis

def analyze_codebase(root):
    cats = {}
    obj_attrs = {}
    dbOpenCV = dbCloseCV = dbGet = 0
    undo = False
    readonly = False
    try_count = 0
    config = False
    lisp = False
    goa = False
    total_files = 0
    total_apis = 0
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        sub = rel.split(os.sep)[0] if rel != "." else "."
        pyfiles = [f for f in filenames if f.endswith(".py")]
        if not pyfiles:
            continue
        if sub not in cats:
            cats[sub] = {"name": sub, "desc": CATEGORY_DESC.get(sub, sub),
                         "file_count": 0, "api_count": 0, "apis": {}, "files": []}
        for f in pyfiles:
            fp = os.path.join(dirpath, f)
            text = open(fp, encoding="utf-8", errors="replace").read()
            total_files += 1
            cats[sub]["file_count"] += 1
            cats[sub]["files"].append(f)
            apis = extract_apis(text)
            for k, v in apis.items():
                cats[sub]["apis"][k] = cats[sub]["apis"].get(k, 0) + v
                total_apis += v
                if k == "dbOpenCV": dbOpenCV += v
                if k == "dbCloseCV": dbCloseCV += v
                if k.startswith("dbGet"): dbGet += v
                if k.startswith("dbUndo"): undo = True
                if k.startswith("goa"): goa = True
            if RO_RE.search(text): readonly = True
            try_count += len(TRY_RE.findall(text))
            if "Config(" in text or "class Config" in text: config = True
            if LISP_RE.search(text): lisp = True
            for am in ATTRS_RE.finditer(text):
                cls = am.group(1)
                attrs = [a.strip() for a in am.group(2).split(",") if a.strip()]
                obj_attrs.setdefault(cls, set()).update(attrs)
    # build top_apis per category
    cat_list = []
    for sub in sorted(cats.keys()):
        c = cats[sub]
        top = sorted(c["apis"].items(), key=lambda x: (-x[1], x[0]))[:5]
        cat_list.append({
            "name": c["name"], "desc": c["desc"],
            "file_count": c["file_count"], "api_count": c["api_count"] if False else sum(c["apis"].values()),
            "top_apis": [{"name": k, "count": v} for k, v in top],
            "files": sorted(c["files"]),
        })
    obj_attrs_out = {cls: sorted(attrs) for cls, attrs in sorted(obj_attrs.items())}
    summary = {
        "categories": cat_list,
        "db_patterns": {
            "dbOpenCV_count": dbOpenCV, "dbCloseCV_count": dbCloseCV,
            "dbGet_count": dbGet, "undo_enabled": undo, "readonly_mode_used": readonly,
        },
        "object_attributes": obj_attrs_out,
        "design_patterns": {
            "try_except_count": try_count, "config_class_used": config,
            "lisp_helpers_used": lisp, "goa_api_used": goa,
        },
        "best_practices": [],
        "total_files": total_files, "total_apis": total_apis,
    }
    if dbOpenCV > 0:
        summary["best_practices"].append("release: call dbCloseCV after every dbOpenCV")
    if readonly:
        summary["best_practices"].append("readonly: use mode=\"r\" for non-mutating ops")
    if undo:
        summary["best_practices"].append("transaction: wrap mutations with dbUndoEnable/dbUndoDisable")
    if try_count > 0:
        summary["best_practices"].append("exception-safety: wrap aether API calls in try/except")
    return summary

def gen_report_md(summary):
    L = []
    L.append("# Aether pyAether API & DB-processing Reference")
    L.append("")
    L.append("## 1. File categorization")
    L.append("| subdir | desc | files | api_count |")
    L.append("|--------|------|-------|-----------|")
    for c in summary["categories"]:
        L.append("| %s | %s | %d | %d |" % (c["name"], c["desc"], c["file_count"], c["api_count"]))
    L.append("")
    L.append("## 2. API reference (top per category)")
    for c in summary["categories"]:
        L.append("### %s (%s)" % (c["name"], c["desc"]))
        for a in c["top_apis"]:
            L.append("- %s : %d" % (a["name"], a["count"]))
        L.append("")
    L.append("## 3. DB processing patterns")
    dbp = summary["db_patterns"]
    L.append("- dbOpenCV count: %d" % dbp["dbOpenCV_count"])
    L.append("- dbCloseCV count: %d" % dbp["dbCloseCV_count"])
    L.append("- dbGet* count: %d" % dbp["dbGet_count"])
    L.append("- undo enabled: %s" % dbp["undo_enabled"])
    L.append("- readonly mode used: %s" % dbp["readonly_mode_used"])
    L.append("")
    L.append("## 4. Object attributes")
    for cls, attrs in summary["object_attributes"].items():
        L.append("- %s: %s" % (cls, ", ".join(attrs)))
    L.append("")
    L.append("## 5. Design patterns")
    dp = summary["design_patterns"]
    L.append("- try/except count: %d" % dp["try_except_count"])
    L.append("- Config class used: %s" % dp["config_class_used"])
    L.append("- Lisp helpers used: %s" % dp["lisp_helpers_used"])
    L.append("- GOA API used: %s" % dp["goa_api_used"])
    L.append("")
    L.append("## 6. Best practices")
    for bp in summary["best_practices"]:
        L.append("- %s" % bp)
    L.append("")
    L.append("## 7. Totals")
    L.append("- total files: %d" % summary["total_files"])
    L.append("- total api occurrences: %d" % summary["total_apis"])
    L.append("")
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codebase", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    summary = analyze_codebase(args.codebase)
    md = gen_report_md(summary)
    out = args.out
    if out.endswith(".md"):
        md_path = out
        json_path = out[:-3] + "_summary.json"
    else:
        md_path = out + ".md"
        json_path = out + "_summary.json"
    os.makedirs(os.path.dirname(os.path.abspath(md_path)) or ".", exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, sort_keys=True)
    print("wrote " + md_path)
    print("wrote " + json_path)

if __name__ == "__main__":
    main()
'''

# ---------- check.py (independent re-derivation) ----------
CHECK_PY = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check(deliverable, workdir) for EDA-Eval-DesignFlow-AetherApiSummary-001.
16 independent conditions (a-p). Runs the candidate on the HIDDEN B fixture,
independently re-derives expected values from B, and compares the candidate's
summary.json + report.md against them. Also runs on A for a couple of A-side
structural checks. Determinism via 3x md5.
"""
import os, re, sys, json, zipfile, shutil, subprocess, tempfile, hashlib, argparse

API_RE = re.compile(r'\b(ae|db|goa|calibre|CXMT|IMC|Innout)([A-Za-z][A-Za-z0-9_]*)')
LISP_RE = re.compile(r'\b(car|cadr|caddr|cddr|cons|append1|assoc|nthelem|mapc|mapcar|mapcan|maplist|rexCompile|rexExecute|rexSubstitute|rexReplace)\s*\(')
TRY_RE = re.compile(r'^\s*try\s*:', re.MULTILINE)
RO_RE = re.compile(r'mode\s*=\s*("r"|\'r\')')
ATTRS_RE = re.compile(r'#\s*@attrs\s+(\w+)\s*:\s*([A-Za-z0-9_,\s]+)')

def extract_apis(text):
    apis = {}
    for m in API_RE.finditer(text):
        prefix, rest = m.group(1), m.group(2)
        full = prefix + rest
        if full == "aether":
            continue
        ok = True if prefix in ("CXMT", "IMC", "Innout") else any(c.isupper() for c in rest)
        if ok:
            apis[full] = apis.get(full, 0) + 1
    return apis

def analyze(root):
    cats = {}; obj_attrs = {}
    dbOpenCV = dbCloseCV = dbGet = 0; undo = False; readonly = False
    try_count = 0; config = False; lisp = False; goa = False
    total_files = 0; total_apis = 0
    for dp_, dn, fns in os.walk(root):
        rel = os.path.relpath(dp_, root)
        sub = rel.split(os.sep)[0] if rel != "." else "."
        pys = [f for f in fns if f.endswith(".py")]
        if not pys: continue
        cats.setdefault(sub, {"file_count": 0, "apis": {}})
        for f in pys:
            text = open(os.path.join(dp_, f), encoding="utf-8", errors="replace").read()
            total_files += 1
            cats[sub]["file_count"] += 1
            for k, v in extract_apis(text).items():
                cats[sub]["apis"][k] = cats[sub]["apis"].get(k, 0) + v
                total_apis += v
                if k == "dbOpenCV": dbOpenCV += v
                if k == "dbCloseCV": dbCloseCV += v
                if k.startswith("dbGet"): dbGet += v
                if k.startswith("dbUndo"): undo = True
                if k.startswith("goa"): goa = True
            if RO_RE.search(text): readonly = True
            try_count += len(TRY_RE.findall(text))
            if "Config(" in text or "class Config" in text: config = True
            if LISP_RE.search(text): lisp = True
            for am in ATTRS_RE.finditer(text):
                obj_attrs.setdefault(am.group(1), set()).update(
                    [a.strip() for a in am.group(2).split(",") if a.strip()])
    return {
        "subdirs": set(cats.keys()),
        "cat_filecount": {s: cats[s]["file_count"] for s in cats},
        "cat_apis": {s: cats[s]["apis"] for s in cats},
        "cat_top": {s: sorted(cats[s]["apis"].items(), key=lambda x: (-x[1], x[0]))[:5] for s in cats},
        "dbOpenCV": dbOpenCV, "dbCloseCV": dbCloseCV, "dbGet": dbGet,
        "undo": undo, "readonly": readonly, "try_count": try_count,
        "config": config, "lisp": lisp, "goa": goa,
        "obj_attrs": {c: sorted(a) for c, a in obj_attrs.items()},
        "total_files": total_files, "total_apis": total_apis,
    }

def _cond(name, ok, detail=""):
    if not ok:
        raise AssertionError("COND %s FAIL: %s" % (name, detail))

def check(deliverable, workdir):
    # deliverable = submit.zip; workdir has assets/.../hidden/python_ae_B available? No -
    # check.py resolves hidden B from the repo assets path passed via env or default.
    # Convention: hidden B fixture path is given by env AE_HIDDEN_B, else default repo path.
    hidden_b = os.environ.get("AE_HIDDEN_B")
    if not hidden_b:
        # default: <repo>/assets/AetherApiSummary-001/hidden/python_ae_B
        cand = os.path.join(workdir, "assets", "AetherApiSummary-001", "hidden", "python_ae_B")
        hidden_b = cand if os.path.isdir(cand) else "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/assets/AetherApiSummary-001/hidden/python_ae_B"
    exp = analyze(hidden_b)
    # also analyze A for cross-input purity (A-only subdirs)
    hidden_a = os.environ.get("AE_HIDDEN_A")
    if not hidden_a:
        ca = os.path.join(workdir, "assets", "AetherApiSummary-001", "inputs", "python_ae_A")
        hidden_a = ca if os.path.isdir(ca) else "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/assets/AetherApiSummary-001/inputs/python_ae_A"
    expA = analyze(hidden_a)
    a_only_subdirs = expA["subdirs"] - exp["subdirs"]
    b_only_subdirs = exp["subdirs"] - expA["subdirs"]

    tmp = tempfile.mkdtemp(prefix="chk_aether_api_")
    try:
        # (a) zip + py_compile + stdlib-only + size
        _cond("a", zipfile.is_zipfile(deliverable), "not a zip")
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            py = [n for n in names if n.endswith("aether_api_summary.py")]
            _cond("a", py, "no aether_api_summary.py in zip: %s" % names)
            data = z.read(py[0])
            _cond("a", len(data) >= 800, "py too small: %d" % len(data))
            src = data.decode("utf-8", errors="replace")
            _cond("a", "\x00" not in src, "NUL in py")
            # stdlib-only import check: forbid third-party imports
            bad = re.findall(r'^\s*(?:import|from)\s+([A-Za-z_][A-Za-z0-9_]*)', src, re.MULTILINE)
            THIRD = {"reportlab", "numpy", "pandas", "matplotlib", "PIL", "requests", "bs4"}
            _cond("a", not (set(bad) & THIRD), "third-party import: %s" % (set(bad) & THIRD))
            # extract
            z.extract(py[0], tmp)
        cand_py = os.path.join(tmp, "aether_api_summary.py")
        r = subprocess.run([sys.executable, "-c", "import py_compile; py_compile.compile(%r, doraise=True)" % cand_py],
                           capture_output=True, text=True)
        _cond("a", r.returncode == 0, "py_compile fail: %s" % r.stderr[:200])

        # run candidate on B
        outdir = os.path.join(tmp, "outB")
        os.makedirs(outdir)
        r = subprocess.run([sys.executable, cand_py, "--codebase", hidden_b, "--out", os.path.join(outdir, "report.md")],
                           capture_output=True, text=True, timeout=120)
        _cond("b", r.returncode == 0, "CLI B exit %d: %s" % (r.returncode, r.stderr[:300]))
        md_path = os.path.join(outdir, "report.md")
        json_path = os.path.join(outdir, "report_summary.json")
        _cond("b", os.path.isfile(md_path) and os.path.getsize(md_path) >= 1, "report.md missing/empty")
        _cond("b", os.path.isfile(json_path), "summary.json missing")
        summary = json.load(open(json_path, encoding="utf-8"))
        md = open(md_path, encoding="utf-8").read()

        # (c) summary top-level keys
        need = {"categories", "db_patterns", "object_attributes", "design_patterns", "best_practices", "total_files"}
        _cond("c", need.issubset(summary.keys()), "missing keys: %s" % (need - set(summary.keys())))

        # (d) total_files == independent B count
        _cond("d", summary["total_files"] == exp["total_files"],
              "total_files %r != %r" % (summary.get("total_files"), exp["total_files"]))

        # (e) categories subdirs == B subdirs (set equality): covers all B, no A-only
        got_subs = {c["name"] for c in summary["categories"]}
        _cond("e", got_subs == exp["subdirs"], "subdirs %r != %r (A-only=%r)" % (got_subs, exp["subdirs"], a_only_subdirs))
        _cond("e", a_only_subdirs.isdisjoint(got_subs), "A-only subdirs leaked: %r" % (a_only_subdirs & got_subs))

        # (f) per-category file_count == independent B count
        for c in summary["categories"]:
            _cond("f", c["file_count"] == exp["cat_filecount"].get(c["name"]),
                  "cat %s file_count %r != %r" % (c["name"], c["file_count"], exp["cat_filecount"].get(c["name"])))

        # (g) per-category top_apis names are subset of B fixture APIs for that subdir;
        #     the #1 top API name must equal the independent most-frequent API for that subdir
        for c in summary["categories"]:
            sub = c["name"]
            b_apis = exp["cat_apis"].get(sub, {})
            names = [a["name"] for a in c.get("top_apis", [])]
            _cond("g", all(n in b_apis for n in names), "cat %s top_apis not in B: %r" % (sub, names))
            if b_apis:
                b_top = exp["cat_top"][sub][0][0] if exp["cat_top"][sub] else None
                _cond("g", names and names[0] == b_top,
                      "cat %s top api %r != independent %r" % (sub, names[0] if names else None, b_top))

        # (h) dbOpenCV_count == independent B count (numeric)
        _cond("h", summary["db_patterns"]["dbOpenCV_count"] == exp["dbOpenCV"],
              "dbOpenCV %r != %r" % (summary["db_patterns"]["dbOpenCV_count"], exp["dbOpenCV"]))

        # (i) dbGet_count == independent B count (numeric)
        _cond("i", summary["db_patterns"]["dbGet_count"] == exp["dbGet"],
              "dbGet %r != %r" % (summary["db_patterns"]["dbGet_count"], exp["dbGet"]))

        # (j) object_attributes: for each class in B fixture, attribute set matches
        got_attrs = summary["object_attributes"]
        for cls, attrs in exp["obj_attrs"].items():
            _cond("j", cls in got_attrs, "missing obj class %s" % cls)
            _cond("j", set(got_attrs[cls]) == set(attrs),
                  "obj %s attrs %r != %r" % (cls, got_attrs.get(cls), attrs))
        _cond("j", set(got_attrs.keys()) == set(exp["obj_attrs"].keys()),
              "obj classes %r != %r" % (set(got_attrs.keys()), set(exp["obj_attrs"].keys())))

        # (k) try_except_count == independent B count (numeric)
        _cond("k", summary["design_patterns"]["try_except_count"] == exp["try_count"],
              "try_except %r != %r" % (summary["design_patterns"]["try_except_count"], exp["try_count"]))

        # (l) config_class_used == independent B bool
        _cond("l", summary["design_patterns"]["config_class_used"] == exp["config"],
              "config %r != %r" % (summary["design_patterns"]["config_class_used"], exp["config"]))

        # (m) lisp_helpers_used == independent B bool
        _cond("m", summary["design_patterns"]["lisp_helpers_used"] == exp["lisp"],
              "lisp %r != %r" % (summary["design_patterns"]["lisp_helpers_used"], exp["lisp"]))

        # (n) best_practices includes resource-release note iff B has dbOpenCV
        bps = summary["best_practices"]
        has_release = any("dbCloseCV" in str(b) for b in bps)
        _cond("n", has_release == (exp["dbOpenCV"] > 0),
              "release note %r but dbOpenCV=%r" % (has_release, exp["dbOpenCV"]))

        # (o) determinism: 3x run summary.json md5 identical
        md5s = []
        for _ in range(3):
            od = os.path.join(tmp, "det%d" % _)
            os.makedirs(od)
            subprocess.run([sys.executable, cand_py, "--codebase", hidden_b, "--out", os.path.join(od, "report.md")],
                           capture_output=True, text=True, timeout=120)
            jp = os.path.join(od, "report_summary.json")
            md5s.append(hashlib.md5(open(jp, "rb").read()).hexdigest())
        _cond("o", len(set(md5s)) == 1, "non-deterministic: %r" % md5s)

        # (p) cross-input guard: B report.md must mention a B-only subdir (e.g. mentor) AND
        #     a B-only API (calibreDrc or calibreLvs) that does NOT appear in A fixture.
        a_api_set = set()
        for s, m in expA["cat_apis"].items():
            a_api_set.update(m.keys())
        b_unique_apis = set()
        for s, m in exp["cat_apis"].items():
            b_unique_apis.update(m.keys())
        b_unique_apis -= a_api_set
        _cond("p", b_only_subdirs, "no B-only subdir (test design)")
        mentioned_b_sub = any(s in md for s in b_only_subdirs)
        _cond("p", mentioned_b_sub, "report.md lacks B-only subdir %r" % b_only_subdirs)
        mentioned_b_api = any(api in md for api in b_unique_apis)
        _cond("p", mentioned_b_api, "report.md lacks B-unique API %r" % list(b_unique_apis)[:5])
        # summary.json categories must include B-only subdir (already covered by e) and its B-unique API
        ment_cat = [c for c in summary["categories"] if c["name"] in b_only_subdirs]
        _cond("p", ment_cat, "summary lacks B-only category")
        ment_apis = {a["name"] for c in ment_cat for a in c.get("top_apis", [])}
        _cond("p", ment_apis & b_unique_apis, "B-only cat has no B-unique API: %r vs %r" % (ment_apis, b_unique_apis))

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return True

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("deliverable")
    ap.add_argument("workdir")
    a = ap.parse_args()
    print(check(a.deliverable, a.workdir))
'''

# ---------- negatives ----------
NEG_EMPTY = '''#!/usr/bin/env python3
import sys
# fake_empty: does nothing
def main():
    pass
if __name__ == "__main__":
    main()
'''

NEG_PRINT = r'''#!/usr/bin/env python3
# fake_print_expected: hardcodes A's expected output (no codebase analysis)
import sys, json, argparse
ap = argparse.ArgumentParser(); ap.add_argument("--codebase", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
md = a.out
jp = a.out[:-3] + "_summary.json" if a.out.endswith(".md") else a.out + "_summary.json"
# hardcode A's categories (will fail B: B has mentor, not py_cck_code)
summary = {
  "categories": [
    {"name":"le","desc":"layout-edit","file_count":2,"api_count":7,"top_apis":[{"name":"aeGetCurDesign","count":2},{"name":"dbOpenCV","count":3}],"files":["leBasicEdit.py","lePlace.py"]},
    {"name":"se","desc":"schematic-edit","file_count":1,"api_count":5,"top_apis":[{"name":"dbFindNetByName","count":2}],"files":["seSchematic.py"]},
    {"name":"db","desc":"db-base","file_count":1,"api_count":6,"top_apis":[{"name":"dbOpenCV","count":2}],"files":["CXMTdbCommonFunc.py"]},
    {"name":"ut","desc":"hierarchy-traverse","file_count":1,"api_count":4,"top_apis":[{"name":"InnoutHierarchyTraverser","count":3}],"files":["IMCutHierarchyTraverser.py"]},
    {"name":"IAPR","desc":"ai-apr","file_count":1,"api_count":9,"top_apis":[{"name":"goaInit","count":1}],"files":["cxmt_AIAPR_getPinInfo.py"]},
    {"name":"py_cck_code","desc":"cck","file_count":1,"api_count":3,"top_apis":[{"name":"aeCrtAppForm","count":2}],"files":["ep_form.py"]},
    {"name":"common","desc":"bindkey-menu","file_count":2,"api_count":8,"top_apis":[{"name":"aeSetBindKey","count":5}],"files":["common_set.py","bindkeyBasic.py"]},
  ],
  "db_patterns": {"dbOpenCV_count":6,"dbCloseCV_count":6,"dbGet_count":2,"undo_enabled":False,"readonly_mode_used":True},
  "object_attributes": {"CellView":["libName","cellName","viewName","cellViewType","instances","shapes","signals"],"Instance":["name","libName","cellName","master","origin","orient","bbox","cdfParameter"],"Net":["name","figs","terms"],"Terminal":["name","net"],"HierQueryResult":["object","hierPath","getDepth"]},
  "design_patterns": {"try_except_count":12,"config_class_used":True,"lisp_helpers_used":True,"goa_api_used":True},
  "best_practices": ["release: call dbCloseCV after every dbOpenCV","readonly: use mode=\"r\"","exception-safety"],
  "total_files":9, "total_apis":42,
}
open(md,"w").write("# Aether API Reference\n\n(hardcoded A summary)\n")
json.dump(summary, open(jp,"w"), indent=2)
'''

NEG_CORE = r'''#!/usr/bin/env python3
# fake_core_deleted: ref with DB-pattern + object-attr + design-pattern extraction REMOVED
# (still does categorization + API extraction, so passes a-g, but fails h-m)
import os, re, sys, json, argparse
API_RE = re.compile(r'\b(ae|db|goa|calibre|CXMT|IMC|Innout)([A-Za-z][A-Za-z0-9_]*)')
def extract_apis(text):
    apis = {}
    for m in API_RE.finditer(text):
        p, r = m.group(1), m.group(2); full = p + r
        if full == "aether": continue
        ok = True if p in ("CXMT","IMC","Innout") else any(c.isupper() for c in r)
        if ok: apis[full] = apis.get(full,0)+1
    return apis
def analyze(root):
    cats = {}; total_files = 0; total_apis = 0
    for dp_, dn, fns in os.walk(root):
        rel = os.path.relpath(dp_, root); sub = rel.split(os.sep)[0] if rel != "." else "."
        pys = [f for f in fns if f.endswith(".py")]
        if not pys: continue
        cats.setdefault(sub, {"file_count":0, "apis":{}})
        for f in pys:
            text = open(os.path.join(dp_, f), encoding="utf-8", errors="replace").read()
            total_files += 1; cats[sub]["file_count"] += 1
            for k, v in extract_apis(text).items():
                cats[sub]["apis"][k] = cats[sub]["apis"].get(k,0)+v; total_apis += v
    cat_list = []
    for sub in sorted(cats):
        top = sorted(cats[sub]["apis"].items(), key=lambda x:(-x[1],x[0]))[:5]
        cat_list.append({"name":sub,"desc":sub,"file_count":cats[sub]["file_count"],"api_count":sum(cats[sub]["apis"].values()),"top_apis":[{"name":k,"count":v} for k,v in top],"files":[]})
    # core deleted: DB patterns / obj attrs / design patterns all zero/empty
    return {"categories":cat_list,"db_patterns":{"dbOpenCV_count":0,"dbCloseCV_count":0,"dbGet_count":0,"undo_enabled":False,"readonly_mode_used":False},"object_attributes":{},"design_patterns":{"try_except_count":0,"config_class_used":False,"lisp_helpers_used":False,"goa_api_used":False},"best_practices":[],"total_files":total_files,"total_apis":total_apis}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--codebase", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    s = analyze(a.codebase)
    md = a.out; jp = a.out[:-3]+"_summary.json" if a.out.endswith(".md") else a.out+"_summary.json"
    open(md,"w").write("# Aether API Reference\n")
    json.dump(s, open(jp,"w"), indent=2)
if __name__ == "__main__": main()
'''

NEG_NAIVE_NOATTR = r'''#!/usr/bin/env python3
# naive_no_attrs: does categorization + API + DB + design patterns but IGNORES @attrs
# (fails j: object_attributes empty)
import os, re, sys, json, argparse
API_RE = re.compile(r'\b(ae|db|goa|calibre|CXMT|IMC|Innout)([A-Za-z][A-Za-z0-9_]*)')
LISP_RE = re.compile(r'\b(car|cadr|caddr|cddr|cons|append1|assoc|nthelem|mapc|mapcar|mapcan|maplist|rexCompile|rexExecute|rexSubstitute|rexReplace)\s*\(')
TRY_RE = re.compile(r'^\s*try\s*:', re.MULTILINE)
RO_RE = re.compile(r'mode\s*=\s*["\']r["\']')
def extract_apis(text):
    apis = {}
    for m in API_RE.finditer(text):
        p, r = m.group(1), m.group(2); full = p + r
        if full == "aether": continue
        ok = True if p in ("CXMT","IMC","Innout") else any(c.isupper() for c in r)
        if ok: apis[full] = apis.get(full,0)+1
    return apis
def analyze(root):
    cats = {}; dbOpenCV=dbCloseCV=dbGet=0; undo=False; ro=False; tc=0; cfg=False; lisp=False; goa=False; tf=0; ta=0
    for dp_, dn, fns in os.walk(root):
        rel = os.path.relpath(dp_, root); sub = rel.split(os.sep)[0] if rel != "." else "."
        pys = [f for f in fns if f.endswith(".py")]
        if not pys: continue
        cats.setdefault(sub, {"file_count":0,"apis":{}})
        for f in pys:
            text = open(os.path.join(dp_, f), encoding="utf-8", errors="replace").read()
            tf += 1; cats[sub]["file_count"] += 1
            for k, v in extract_apis(text).items():
                cats[sub]["apis"][k]=cats[sub]["apis"].get(k,0)+v; ta+=v
                if k=="dbOpenCV": dbOpenCV+=v
                if k=="dbCloseCV": dbCloseCV+=v
                if k.startswith("dbGet"): dbGet+=v
                if k.startswith("dbUndo"): undo=True
                if k.startswith("goa"): goa=True
            if RO_RE.search(text): ro=True
            tc += len(TRY_RE.findall(text))
            if "Config(" in text or "class Config" in text: cfg=True
            if LISP_RE.search(text): lisp=True
    cl=[]
    for sub in sorted(cats):
        top=sorted(cats[sub]["apis"].items(), key=lambda x:(-x[1],x[0]))[:5]
        cl.append({"name":sub,"desc":sub,"file_count":cats[sub]["file_count"],"api_count":sum(cats[sub]["apis"].values()),"top_apis":[{"name":k,"count":v} for k,v in top],"files":[]})
    bp=[]
    if dbOpenCV>0: bp.append("release: call dbCloseCV after every dbOpenCV")
    return {"categories":cl,"db_patterns":{"dbOpenCV_count":dbOpenCV,"dbCloseCV_count":dbCloseCV,"dbGet_count":dbGet,"undo_enabled":undo,"readonly_mode_used":ro},"object_attributes":{},"design_patterns":{"try_except_count":tc,"config_class_used":cfg,"lisp_helpers_used":lisp,"goa_api_used":goa},"best_practices":bp,"total_files":tf,"total_apis":ta}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--codebase", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    s = analyze(a.codebase); md=a.out; jp=a.out[:-3]+"_summary.json" if a.out.endswith(".md") else a.out+"_summary.json"
    open(md,"w").write("# Aether API Reference\n"); json.dump(s, open(jp,"w"), indent=2)
if __name__=="__main__": main()
'''

NEG_NAIVE_FLAT = r'''#!/usr/bin/env python3
# naive_flat_no_category: dumps all APIs across the whole tree without per-subdir categorization
# (fails e/f: categories wrong)
import os, re, sys, json, argparse
API_RE = re.compile(r'\b(ae|db|goa|calibre|CXMT|IMC|Innout)([A-Za-z][A-Za-z0-9_]*)')
def extract_apis(text):
    apis = {}
    for m in API_RE.finditer(text):
        p, r = m.group(1), m.group(2); full = p + r
        if full == "aether": continue
        ok = True if p in ("CXMT","IMC","Innout") else any(c.isupper() for c in r)
        if ok: apis[full] = apis.get(full,0)+1
    return apis
def analyze(root):
    all_apis = {}; tf=0
    for dp_, dn, fns in os.walk(root):
        for f in fns:
            if not f.endswith(".py"): continue
            text = open(os.path.join(dp_, f), encoding="utf-8", errors="replace").read()
            tf += 1
            for k, v in extract_apis(text).items(): all_apis[k]=all_apis.get(k,0)+v
    # single flat category "all"
    top = sorted(all_apis.items(), key=lambda x:(-x[1],x[0]))[:5]
    return {"categories":[{"name":"all","desc":"all","file_count":tf,"api_count":sum(all_apis.values()),"top_apis":[{"name":k,"count":v} for k,v in top],"files":[]}],"db_patterns":{"dbOpenCV_count":0,"dbCloseCV_count":0,"dbGet_count":0,"undo_enabled":False,"readonly_mode_used":False},"object_attributes":{},"design_patterns":{"try_except_count":0,"config_class_used":False,"lisp_helpers_used":False,"goa_api_used":False},"best_practices":[],"total_files":tf,"total_apis":sum(all_apis.values())}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--codebase", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
    s = analyze(a.codebase); md=a.out; jp=a.out[:-3]+"_summary.json" if a.out.endswith(".md") else a.out+"_summary.json"
    open(md,"w").write("# Aether API Reference\n"); json.dump(s, open(jp,"w"), indent=2)
if __name__=="__main__": main()
'''

NEG_SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest: run check.py against each negative submission; all must FAIL."""
import os, sys, json, zipfile, tempfile, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
HIDDEN_B = os.path.join(REPO, "assets", "AetherApiSummary-001", "hidden", "python_ae_B")
HIDDEN_A = os.path.join(REPO, "assets", "AetherApiSummary-001", "inputs", "python_ae_A")
NEG = os.path.join(HERE, "negative")
import importlib.util
spec = importlib.util.spec_from_file_location("chk", os.path.join(HERE, "check.py"))
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)

def make_zip(pyname, src):
    tmp = tempfile.mkdtemp()
    zp = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("aether_api_summary.py", src)
    return zp, tmp

def run_one(name):
    src = open(os.path.join(NEG, name), encoding="utf-8").read()
    zp, tmp = make_zip(name, src)
    try:
        env = dict(os.environ); env["AE_HIDDEN_B"] = HIDDEN_B; env["AE_HIDDEN_A"] = HIDDEN_A
        # call check via subprocess with env
        r = subprocess.run([sys.executable, os.path.join(HERE, "check.py"), zp, HERE],
                           capture_output=True, text=True, env=env, timeout=180)
        passed = (r.returncode == 0)
        return name, passed, (r.stdout + r.stderr)[-400:]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

fails = []
for name in sorted(os.listdir(NEG)):
    if not name.endswith(".py") or name.startswith("_"):
        continue
    n, passed, detail = run_one(name)
    print("%s: %s" % (n, "PASS(UNEXPECTED!)" if passed else "FAIL(ok)"))
    if passed:
        fails.append((n, detail))
print("\nNEG_RC=%d" % len(fails))
sys.exit(1 if fails else 0)
'''

PROMPT = '''# Aether pyAether API 与 DB 处理方式参考手册生成

## 场景
你是 EDA 版图工具链的文档工程师 taodu，主机 hfeg0plg55。你拿到了 Empyrean Aether 的 pyAether
代码库目录 `/apps/imctf/cad/init/settings_aether/python_ae`——里面是按子目录组织的 Python 脚本
（版图编辑 `le`、电路编辑 `se`、DB 基础 `db`、层次遍历 `ut`、AI APR `IAPR`、CCK `py_cck_code`、
快捷键/菜单 `common` 等），每条脚本里大量调用 aether 的 API（`aeGetCurDesign` / `dbOpenCV` /
`dbGetTrueOverlapsEx` / `dbCloseCV` / `aeSetBindKey` / `goaInit` / `goaLayerFromCellView` /
`CXMTleStreamOut` / `InnoutHierarchyTraverser` / `aeCrtAppForm` / `aeAddNetProbe` …）并对 DB 做各种处理。

你需要**程序化地分析这个代码库**，总结出 aether 常用 API 和常用 DB 处理方式，产出一份**结构化参考手册**。

## 交付
写一个能在终端直接跑的 Python3 脚本 `aether_api_summary.py`（**纯标准库、ASCII、无第三方依赖**）：

```
python3 aether_api_summary.py --codebase <代码库根目录> --out <报告输出路径>
```

程序扫描 `--codebase` 指向的代码库，按**子目录**把脚本分类（每个含 `.py` 的子目录 = 一个类别），
对每个类别提取出现的 API 调用并计数（API 标识符 = 前缀 `ae`/`db`/`goa`/`calibre`/`CXMT`/`IMC`/`Innout`
+ 驼峰名；前缀为 `CXMT`/`IMC`/`Innout` 时后半可小写起头，其余后半须含至少一个大写字母；排除单词
`aether` 本身），识别 **DB 处理模式**（`dbOpenCV`/`dbCloseCV` 计数、`dbGet*` 计数、是否用了
`dbUndo*`、是否用了只读 `mode="r"`），从 `# @attrs <类名>: <属性行>` 注解里提取**对象属性**，
统计**设计模式**（`try:` 块计数、是否用 `Config` 类、是否用 Lisp 风格辅助函数 `car`/`cadr`/`mapcar`
等、是否用 GOA API），并给出**最佳实践**清单（如「每次 `dbOpenCV` 后必须 `dbCloseCV`」）。

输出两份文件：
1. `<out>` —— 中文 Markdown 参考手册（含文件分类表、各类 API 速查、DB 处理模式、对象属性、
   设计模式、最佳实践、统计总计等章节）；
2. `<out>` 去掉 `.md` 后缀接 `_summary.json`（若 `<out>` 不以 `.md` 结尾则 `<out>_summary.json`）
   —— 结构化 JSON，顶层键：`categories`（每个类别 `name`/`desc`/`file_count`/`api_count`/
   `top_apis`[{name,count}]/`files`）、`db_patterns`（`dbOpenCV_count`/`dbCloseCV_count`/
   `dbGet_count`/`undo_enabled`/`readonly_mode_used`）、`object_attributes`（类名→属性列表）、
   `design_patterns`（`try_except_count`/`config_class_used`/`lisp_helpers_used`/`goa_api_used`）、
   `best_practices`（字符串列表）、`total_files`、`total_apis`。

## 约束
- 纯标准库，**不得** import reportlab/numpy/pandas 等第三方包。
- 对代码库的解析必须**真实**（按上述规则扫文件、计数），不得硬编码任何 API 名或计数。
- 同一输入多次运行结果必须**确定一致**。
'''

TASK_BRIEF = '''交付接口：脚本 aether_api_summary.py，CLI `--codebase <dir> --out <report.md>`，产出 report.md + report_summary.json。
可见输入：assets/inputs/python_ae_A/（fixture 代码库）。判分用隐藏输入 B（结构不同）。'''

HIDDEN_MANIFEST = {
    "case_id": "EDA-Eval-DesignFlow-AetherApiSummary-001",
    "hidden_inputs": ["python_ae_B/"],
    "note": "B fixture: subdirs le/se/db/ut/IAPR/mentor/common (no py_cck_code; mentor is B-only with calibreDrc/calibreLvs). Different API counts, no Config class, no Lisp helpers, different @attrs. check.py runs candidate on B only.",
}

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# write fixtures
for rel, content in A_FILES.items():
    write(os.path.join(ASSET, "inputs", rel), content)
for rel, content in B_FILES.items():
    write(os.path.join(ASSET, "hidden", rel), content)
write(os.path.join(ASSET, "inputs", "prompt_aether_api_summary.md"), PROMPT)
write(os.path.join(ASSET, "inputs", "task_brief.md"), TASK_BRIEF)
write(os.path.join(ASSET, "hidden", "hidden_manifest.json"), json.dumps(HIDDEN_MANIFEST, ensure_ascii=False, indent=2))

# write reference
write(os.path.join(REF, "aether_api_summary_ref.py"), REF_GEN)
write(os.path.join(REF, "check.py"), CHECK_PY)
write(os.path.join(REF, "negative", "fake_empty.py"), NEG_EMPTY)
write(os.path.join(REF, "negative", "fake_print_expected.py"), NEG_PRINT)
write(os.path.join(REF, "negative", "fake_core_deleted.py"), NEG_CORE)
write(os.path.join(REF, "negative", "naive_no_attrs.py"), NEG_NAIVE_NOATTR)
write(os.path.join(REF, "negative", "naive_flat_no_category.py"), NEG_NAIVE_FLAT)
write(os.path.join(REF, "negative_selftest.py"), NEG_SELFTEST)

# build reference_submit.zip (ref solution packaged as candidate submission)
ref_src = REF_GEN
zp = os.path.join(REF, "reference_submit.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("aether_api_summary.py", ref_src)

print("built case %s" % CASE)
print("assets: %s" % ASSET)
print("reference: %s" % REF)
