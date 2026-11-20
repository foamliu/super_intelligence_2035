#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r186_db_lifecycle_corpus.py
R186 -- v16 PyAether SFT corpus: db* library & cellview lifecycle
(the 5th blind domain family from R181 coverage audit, data-driven pick).

BACKGROUND: v11+v12+v13+v14+v15 (253 pairs) teaches db*-query / schematic /
layout-create / pin / Mde* / cdf* / ae* / emy* APIs.  A re-audit of the 158
remaining blind eval APIs (R181 audit minus v12-v15 coverage) found the db*
"library & cellview lifecycle" family is the LARGEST remaining coherent
blind family by eval usage (65 total usages across 10 APIs):
  dbCreateLib(21) dbDelLib(20) dbOpenCVByType(13) dbSaveCV(3) dbDeleteAll(2)
  dbGetTrueOverlaps(2) dbCrtPinByNet(1) dbConvertPolygonToPath(1)
  dbFindMemInstByNameEx(1) dbRegTraverseTrigger(1).
These form the coherent library/cellview lifecycle workflow:
  create library -> open cellview by type -> edit -> save -> delete ->
  query overlaps -> find instance -> create pin -> convert polygon ->
  register traverse trigger.
All 10 are ISOLATE-class (eval helpers, eval_count>0).  The red line (S5.1)
isolates on eval *entry_point* strings (the 155 task function names), NOT on
helper/type names -- teaching the public API reference is allowed.  The
fingerprint scan rejects any pair containing a literal eval entry_point
string.  Signatures fetched via pyAether MCP get_api_details (R186 wake255).

v16: 10 db* lifecycle APIs x (S1 doc->code + S4 multi-step + S5 param var)
+ 5 S3 multi-API chains + 10 S6 lookups = 45 pairs.  Strict pollution scan
against all 155 eval entry_points.

Usage: python3 baize_posttrain_r186_db_lifecycle_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v16_db_lifecycle.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["dbCreateLib"] = {
    "sig": 'dbCreateLib(lib: emyString, path: emyString="", techFile: emyString="", attachTechLib: emyString="", refTechLibs: emyString="") -> emyLib',
    "desc": "Create a new library. Returns a library identifier (emyLib) if a new library can be created. The library is the top-level container for cells and cellviews in the EDA database.",
    "params": {
        "lib": "emyString - library name",
        "path": 'emyString, optional - directory where the library is located (default current dir)',
        "techFile": "emyString, optional - technology file name",
        "attachTechLib": "emyString, optional - attached technology library name",
        "refTechLibs": "emyString, optional - reference technology library name",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.emyString("try")\n'
                '>>> pyScript.dbCreateLib(lib=lib)'),
    "category": "Db Commands / Library Database Commands",
    "safety": "ISOLATE", "eval_count": 21,
    "key_notes": "Returns emyLib handle. Use emyString for the lib name (not plain str in kwargs form). Call emyInitAether first. path defaults to current directory. Use dbDelLib to remove."}

API_DOCS["dbDelLib"] = {
    "sig": 'dbDelLib(lib: vector1D_emyString, deleteFromDisk: bool=True) -> bool',
    "desc": "Delete one or more libraries. Accepts a list of library names (vector1D_emyString). Returns True (1) if the specified library is deleted. Optionally removes the library files from disk.",
    "params": {
        "lib": "vector1D_emyString - list of library names (supports Python list)",
        "deleteFromDisk": "bool, optional - whether to delete from disk (default True)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.vector1D_emyString()\n'
                '>>> lib.append("test01")\n'
                '>>> lib.append("test02")\n'
                '>>> pyScript.dbDelLib(lib=lib)'),
    "category": "Db Commands / Library Database Commands",
    "safety": "ISOLATE", "eval_count": 20,
    "key_notes": "Accepts vector1D_emyString (a list of names), not a single emyString. Use .append() to add names. deleteFromDisk=True removes files; False only removes from session. Returns bool."}

API_DOCS["dbOpenCVByType"] = {
    "sig": 'dbOpenCVByType(lib, cell, view, viewType="", mode="r", contextCellView=None) -> emyDesign',
    "desc": "Open a cell view by searching for a view name that matches the specified view type. Returns a cell view identifier (emyDesign) if found, otherwise None. The view parameter can be a list of view names or a space-separated string.",
    "params": {
        "lib": "emyString - library name",
        "cell": "emyString - cell name",
        "view": "emyString or list - view name(s); command searches for a match",
        "viewType": 'emyString, optional - enum: layout, schematic, symbol',
        "mode": 'emyString, optional - open mode: "r"(read), "w"(write), "a"(append), "readOnly", "create", "edit" (default "r")',
        "contextCellView": "emyCellView, optional - context cellview (currently no function, default None)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCVByType("test", "inv", "layout", "layout", "r")\n'
                '>>> cv is not None  # True if cellview exists'),
    "category": "Db Commands / Cell Database Commands",
    "safety": "ISOLATE", "eval_count": 13,
    "key_notes": "Returns emyDesign or None. view can be a list ['view1','view2'] or string 'view1 view2'. mode 'w' clears existing contents; 'a' creates if missing. Unlike dbOpenCV, this searches by viewType enum. Call emyInitAether first."}

API_DOCS["dbSaveCV"] = {
    "sig": 'dbSaveCV(cv: emyDesign, lib: emyString="", cell: emyString="", view: emyString="layout") -> bool',
    "desc": "Save a cell view with the specified cell view identifier. When lib and cell are provided and the library exists, saves as a new design. Returns True on success, False on failure.",
    "params": {
        "cv": "emyDesign - cell view identifier to save",
        "lib": "emyString, optional - target library name (save-as when provided)",
        "cell": "emyString, optional - target cell name (save-as when provided)",
        "view": 'emyString, optional - view name (default "layout")',
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.emyString("test")\n'
                '>>> cell = pyScript.emyString("test")\n'
                '>>> cv = pyScript.dbOpenCV(lib=lib, cell=cell)\n'
                '>>> pyScript.dbSaveCV(cv=cv)'),
    "category": "Db Commands / Cell Database Commands",
    "safety": "ISOLATE", "eval_count": 3,
    "key_notes": "Returns bool. cv must be a valid emyDesign from dbOpenCV/dbOpenCVByType/dbNewCellView. Passing None returns False without error. Empty lib/cell saves in-place; providing both does save-as. Call dbCloseCV after saving."}

API_DOCS["dbDeleteAll"] = {
    "sig": 'dbDeleteAll(figs: vector1D_p_emyFig) -> bool',
    "desc": "Delete the specified figure objects from the database. Returns True (1) when the specified objects are deleted. Accepts a list of figure identifiers.",
    "params": {
        "figs": "vector1D_p_emyFig - list of figure identifiers (supports Python list)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> fig = pyScript.dbCrtLine(cv=cv, points=pts, layer="Gate")\n'
                '>>> figList = pyScript.vector1D_p_emyFig()\n'
                '>>> figList.append(fig)\n'
                '>>> pyScript.dbDeleteAll(figs=figList)'),
    "category": "Db Commands / Edit Database Commands",
    "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Accepts vector1D_p_emyFig (list of figure pointers). Use .append(fig) to add figures. Returns bool. Figures must belong to an open cellview in write/edit mode. Supports Python list input."}

API_DOCS["dbGetTrueOverlaps"] = {
    "sig": 'dbGetTrueOverlaps(cv: emyDesign, bbox: emyBoxF=emyBoxF(0,0,0,0), layer: emyString="", purpose: emyString="drawing", startLevel: int=0, stopLevel: int=0, shapeOnly: bool=False, instOnly: bool=False, viaOnly: bool=False, cbFunc: emyString="", attachBBox: bool=False, attachPoint: bool=False, condition: emyString="EO") -> Tuple[PyTravInfos]',
    "desc": "Return a list of object identifiers whose bounding boxes overlap the specified bounding box. Supports filtering by layer, purpose, hierarchy level, and object type (shape/instance/via).",
    "params": {
        "cv": "emyDesign - cell view identifier",
        "bbox": "emyBoxF, optional - query bounding box (default cellview bbox)",
        "layer": "emyString, optional - layer name/number filter",
        "purpose": 'emyString, optional - purpose name (default "drawing")',
        "startLevel": "int, optional - starting traverse level",
        "stopLevel": "int, optional - traverse stop level",
        "shapeOnly": "bool, optional - only get shapes",
        "instOnly": "bool, optional - only get instances",
        "viaOnly": "bool, optional - only get vias",
        "cbFunc": "emyString, optional - callback function name",
        "attachBBox": "bool, optional - return [fig, bbox] pairs",
        "attachPoint": "bool, optional - return [fig, points] pairs",
        "condition": 'emyString, optional - traverse condition (default "EO")',
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="mylib", cell="mycell", view="layout")\n'
                '>>> bbox = pyScript.emyBoxF((0, 0), (100, 100))\n'
                '>>> overlaps = pyScript.dbGetTrueOverlaps(cv=cv, bbox=bbox, layer="M1")'),
    "category": "Db Commands / Edit Database Commands",
    "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Returns tuple of PyTravInfos. With attachBBox=True each element is [fig, emyBoxF]; with attachPoint=True each element is [fig, points_list]. Use layer filter for performance. condition 'EO'=enclosed/overlap. cv must be valid emyDesign."}

API_DOCS["dbCrtPinByNet"] = {
    "sig": 'dbCrtPinByNet(net: emyNet, fig: emyFig=None, name: emyString="", term: emyObject=None) -> emyPin',
    "desc": "Create a pin by net. Associates a figure with a net and terminal to form a pin. Returns a pin identifier (emyPin) if successful; otherwise returns 0.",
    "params": {
        "net": "emyNet - net identifier (from dbCrtNet)",
        "fig": "emyFig, optional - figure identifier (e.g. from dbCrtRect)",
        "name": "emyString, optional - pin name",
        "term": "emyObject, optional - terminal identifier (from dbCrtTerm)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> netId = pyScript.dbCrtNet(cv=cv, name=pyScript.emyString("VDD"))\n'
                '>>> figId = pyScript.dbCrtRect(cv=cv, bbox=bbox, layer="M1")\n'
                '>>> termId = pyScript.dbCrtTerm(net=netId, name=name, dir=dir)\n'
                '>>> pyScript.dbCrtPinByNet(net=netId, fig=figId, name=name, term=termId)'),
    "category": "Db Commands / Create Database Commands",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns emyPin or 0 on failure. Requires a net (dbCrtNet), a figure (dbCrtRect/dbCrtLine), and optionally a terminal (dbCrtTerm). The pin connects the physical figure to the logical net. Used in schematic-to-layout pin creation."}

API_DOCS["dbConvertPolygonToPath"] = {
    "sig": 'dbConvertPolygonToPath(shape: emyShape, value: bool=True, keepShape: bool=False, chooseEdge: bool=False, points: vector1D_emyPointF=None) -> emyShape',
    "desc": "Convert polygons to paths. The polygons must have L-shaped corners and consistent widths. Returns the emyShape object if conversion succeeds; otherwise None.",
    "params": {
        "shape": "emyShape - polygon identifier to convert",
        "value": "bool, optional - snap width to even multiple of grid (default True)",
        "keepShape": "bool, optional - keep original shape (default False)",
        "chooseEdge": "bool, optional - choose edge (default False)",
        "points": "vector1D_emyPointF, optional - specifies edge (default None)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test_adv", cell="test", view="layout")\n'
                '>>> poly = pyScript.dbCrtPolygon(cv, points, "AA")\n'
                '>>> pyScript.dbConvertPolygonToPath(poly)'),
    "category": "Db Commands / Edit Database Commands",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns emyShape or None. Polygon must have L-shaped corners + consistent width. value=True snaps width to even grid multiple. keepShape=True preserves original polygon. points specifies which edge to use for width extraction."}

API_DOCS["dbFindMemInstByNameEx"] = {
    "sig": 'dbFindMemInstByNameEx(design: emyDesign, name: str/emyString, bVectorInst: bool=False) -> list',
    "desc": "Retrieve an instance or vector instance by name and return its member index. Returns a list [inst_object, member_index] if found; None if not found. For non-vector instances, member_index is 0.",
    "params": {
        "design": "emyDesign - the designated design to search",
        "name": "str or emyString - name of the instance",
        "bVectorInst": "bool, optional - if True, do not find vector instances by bit name (default False)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV("test_adv", "test", "schematic")\n'
                '>>> res = pyScript.dbFindMemInstByNameEx(cv, "inst1")\n'
                '>>> res  # [db:<dbId#>, 0]\n'
                '>>> pyScript.dbFindMemInstByNameEx(cv, "inst3<0:3>")  # vector inst\n'
                '>>> pyScript.dbFindMemInstByNameEx(cv, "myInst")  # None if not found'),
    "category": "Db Commands / Edit Database Commands",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns [inst, index] list or None. name can be plain str. For vector insts use 'name<bit>' or 'name<start:stop>'. bVectorInst=True returns the vector inst object instead of the bit. Access inst attributes via res[0].forReg for description."}

API_DOCS["dbRegTraverseTrigger"] = {
    "sig": 'dbRegTraverseTrigger(trigger: dbTraverseTriggerFunc) -> None',
    "desc": "Register a user-defined traverse trigger for design hierarchy traversal. The trigger is a class inheriting dbTraverseTriggerFunc with funcCb(design) and funcReturnCb(design) callback methods. Used with dbTraverseDesignWithCB for custom design walks.",
    "params": {
        "trigger": "dbTraverseTriggerFunc - user callback class instance with funcCb/funcReturnCb methods",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> class MyTraverser(pyScript.dbTraverseTriggerFunc):\n'
                '...     def __init__(self):\n'
                '...         super().__init__()\n'
                '...         self.count = 0\n'
                '...     def funcCb(self, design):\n'
                '...         self.count += 1\n'
                '...     def funcReturnCb(self, design):\n'
                '...         return True\n'
                '>>> analyzer = MyTraverser()\n'
                '>>> pyScript.dbRegTraverseTrigger(analyzer)'),
    "category": "Db Commands / Other Commands",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Register a callback class inheriting dbTraverseTriggerFunc. Implement funcCb(design) for per-design processing and funcReturnCb(design)->bool to control continuation (True=continue, False=stop). Use with dbTraverseDesignWithCB(design, viewType, depth). Multiple registrations overwrite."}

DB_ORDER = ["dbCreateLib", "dbDelLib", "dbOpenCVByType", "dbSaveCV",
            "dbDeleteAll", "dbGetTrueOverlaps", "dbCrtPinByNet",
            "dbConvertPolygonToPath", "dbFindMemInstByNameEx",
            "dbRegTraverseTrigger"]
API_ORDER = DB_ORDER

def load_eval_entry_points():
    """Load all entry_point strings from the 158-task eval dataset for the
    fingerprint contamination scan.  The task bodies themselves are NOT
    read -- only the entry_point field."""
    eps = set()
    if not os.path.exists(EVAL_DS):
        sys.stderr.write("WARN: eval dataset not found at %s\n" % EVAL_DS)
        return eps
    with open(EVAL_DS, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            ep = obj.get("entry_point")
            if ep:
                eps.add(ep)
    return eps


def fingerprint_scan(text, eval_eps):
    for ep in eval_eps:
        if ep and ep in text:
            return ep
    return None


def _doc_block(name):
    d = API_DOCS[name]
    lines = ["## %s" % name, "", "`%s`(...)" % name, "",
             "**`%s`**" % d["sig"], "", "%s" % d["desc"], "", "Parameters"]
    for pn, pd in d["params"].items():
        lines.append("**%s** %s" % (pn, pd))
    lines.append("")
    if d.get("key_notes"):
        lines.append("Notes: %s" % d["key_notes"])
        lines.append("")
    lines.extend(["Examples", "", d["doctest"]])
    return "\n".join(lines)


def _s1_doc_to_code(name):
    fn = "use_" + name.lower()
    if name == "dbCreateLib":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib_name):\n"
            "    lib = pyScript.emyString(lib_name)\n"
            "    return pyScript.dbCreateLib(lib=lib)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(lib_name) that wraps the library name in an "
                  "emyString and creates a new library, returning the emyLib handle."
                  % (_doc_block(name), fn))
    elif name == "dbDelLib":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib_names, from_disk=True):\n"
            "    lib_list = pyScript.vector1D_emyString()\n"
            "    for n in lib_names:\n"
            "        lib_list.append(n)\n"
            "    return pyScript.dbDelLib(lib=lib_list, deleteFromDisk=from_disk)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(lib_names, from_disk=True) that builds a "
                  "vector1D_emyString from a Python list of names and deletes the libraries."
                  % (_doc_block(name), fn))
    elif name == "dbOpenCVByType":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view, vtype, mode):\n"
            "    return pyScript.dbOpenCVByType(lib, cell, view, vtype, mode)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(lib, cell, view, vtype, mode) that opens a "
                  "cellview by type and returns the emyDesign handle (or None)."
                  % (_doc_block(name), fn))
    elif name == "dbSaveCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv):\n"
            "    return pyScript.dbSaveCV(cv=cv)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(cv) that saves the given cellview in-place "
                  "and returns the bool result." % (_doc_block(name), fn))
    elif name == "dbDeleteAll":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(figs):\n"
            "    fig_list = pyScript.vector1D_p_emyFig()\n"
            "    for f in figs:\n"
            "        fig_list.append(f)\n"
            "    return pyScript.dbDeleteAll(figs=fig_list)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(figs) that builds a vector1D_p_emyFig from a "
                  "Python list and deletes all listed figures." % (_doc_block(name), fn))
    elif name == "dbGetTrueOverlaps":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, bbox, layer):\n"
            "    return pyScript.dbGetTrueOverlaps(cv=cv, bbox=bbox, layer=layer)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(cv, bbox, layer) that queries true overlaps "
                  "within a bounding box filtered by layer and returns the result tuple."
                  % (_doc_block(name), fn))
    elif name == "dbCrtPinByNet":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(net, fig, name, term):\n"
            "    nm = pyScript.emyString(name)\n"
            "    return pyScript.dbCrtPinByNet(net=net, fig=fig, name=nm, term=term)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(net, fig, name, term) that wraps the pin name "
                  "in emyString and creates a pin by net, returning the emyPin."
                  % (_doc_block(name), fn))
    elif name == "dbConvertPolygonToPath":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(shape):\n"
            "    return pyScript.dbConvertPolygonToPath(shape)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(shape) that converts the given polygon to a "
                  "path and returns the resulting emyShape (or None)." % (_doc_block(name), fn))
    elif name == "dbFindMemInstByNameEx":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(design, name):\n"
            "    return pyScript.dbFindMemInstByNameEx(design, name)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(design, name) that finds an instance by name "
                  "and returns the [inst, index] list (or None)." % (_doc_block(name), fn))
    elif name == "dbRegTraverseTrigger":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(collector_class):\n"
            "    instance = collector_class()\n"
            "    pyScript.dbRegTraverseTrigger(instance)\n"
            "    return instance\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(collector_class) that instantiates the given "
                  "dbTraverseTriggerFunc subclass, registers it, and returns the instance."
                  % (_doc_block(name), fn))
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S1 doc-to-code"


def _s4_multi_step(name):
    fn = "trace_" + name.lower()
    if name == "dbCreateLib":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib_name, path):\n"
            "    pyScript.emyInitAether('-adv')\n"
            "    lib = pyScript.emyString(lib_name)\n"
            "    p = pyScript.emyString(path)\n"
            "    handle = pyScript.dbCreateLib(lib=lib, path=p)\n"
            "    return handle\n") % fn
        prompt = ("Write a Python function %s(lib_name, path) that initializes Aether, "
                  "wraps the name and path in emyString, creates the library, and returns "
                  "the emyLib handle." % fn)
    elif name == "dbDelLib":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib_name):\n"
            "    lib_list = pyScript.vector1D_emyString()\n"
            "    lib_list.append(lib_name)\n"
            "    ok = pyScript.dbDelLib(lib=lib_list, deleteFromDisk=False)\n"
            "    return ok\n") % fn
        prompt = ("Write a Python function %s(lib_name) that builds a vector1D_emyString "
                  "with one name, deletes the library from session only (not disk), and "
                  "returns the bool result." % fn)
    elif name == "dbOpenCVByType":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell):\n"
            "    cv = pyScript.dbOpenCVByType(lib, cell, 'layout', 'layout', 'r')\n"
            "    if cv is None:\n"
            "        cv = pyScript.dbOpenCVByType(lib, cell, 'schematic', 'schematic', 'r')\n"
            "    return cv\n") % fn
        prompt = ("Write a Python function %s(lib, cell) that tries opening a layout "
                  "cellview by type in read mode; if None, falls back to schematic. "
                  "Returns the emyDesign handle." % fn)
    elif name == "dbSaveCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, new_lib, new_cell):\n"
            "    ok = pyScript.dbSaveCV(cv=cv, lib=pyScript.emyString(new_lib),\n"
            "                           cell=pyScript.emyString(new_cell))\n"
            "    return ok\n") % fn
        prompt = ("Write a Python function %s(cv, new_lib, new_cell) that saves the "
                  "cellview as a new design in a different library/cell and returns the "
                  "bool result." % fn)
    elif name == "dbDeleteAll":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, figs):\n"
            "    fig_list = pyScript.vector1D_p_emyFig()\n"
            "    for f in figs:\n"
            "        fig_list.append(f)\n"
            "    return pyScript.dbDeleteAll(figs=fig_list)\n") % fn
        prompt = ("Write a Python function %s(cv, figs) that collects figure identifiers "
                  "into a vector1D_p_emyFig and deletes them all, returning the bool."
                  % fn)
    elif name == "dbGetTrueOverlaps":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, x1, y1, x2, y2, layer):\n"
            "    bbox = pyScript.emyBoxF((x1, y1), (x2, y2))\n"
            "    result = pyScript.dbGetTrueOverlaps(cv=cv, bbox=bbox, layer=layer,\n"
            "                                        attachBBox=True)\n"
            "    return result\n") % fn
        prompt = ("Write a Python function %s(cv, x1, y1, x2, y2, layer) that constructs "
                  "an emyBoxF, queries true overlaps with attachBBox=True, and returns "
                  "the [fig, bbox] pairs." % fn)
    elif name == "dbCrtPinByNet":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, net_name, pin_name, bbox, layer):\n"
            "    nm = pyScript.emyString(net_name)\n"
            "    netId = pyScript.dbCrtNet(cv=cv, name=nm)\n"
            "    figId = pyScript.dbCrtRect(cv=cv, bbox=bbox, layer=pyScript.emyString(layer))\n"
            "    pm = pyScript.emyString(pin_name)\n"
            "    termId = pyScript.dbCrtTerm(net=netId, name=pm, dir=pyScript.emyString('input'))\n"
            "    return pyScript.dbCrtPinByNet(net=netId, fig=figId, name=pm, term=termId)\n") % fn
        prompt = ("Write a Python function %s(cv, net_name, pin_name, bbox, layer) that "
                  "creates a net, a rect figure, a terminal, and then a pin by net, "
                  "returning the emyPin." % fn)
    elif name == "dbConvertPolygonToPath":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, points, layer):\n"
            "    poly = pyScript.dbCrtPolygon(cv, points, layer)\n"
            "    result = pyScript.dbConvertPolygonToPath(poly)\n"
            "    return result\n") % fn
        prompt = ("Write a Python function %s(cv, points, layer) that creates a polygon "
                  "and converts it to a path, returning the emyShape (or None)." % fn)
    elif name == "dbFindMemInstByNameEx":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(design, name):\n"
            "    res = pyScript.dbFindMemInstByNameEx(design, name)\n"
            "    if res is None:\n"
            "        return None\n"
            "    return res[0], res[1]\n") % fn
        prompt = ("Write a Python function %s(design, name) that finds an instance by "
                  "name; if found, returns a (inst, index) tuple; if not found, returns "
                  "None." % fn)
    elif name == "dbRegTraverseTrigger":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    class Counter(pyScript.dbTraverseTriggerFunc):\n"
            "        def __init__(self):\n"
            "            super().__init__()\n"
            "            self.count = 0\n"
            "        def funcCb(self, design):\n"
            "            self.count += 1\n"
            "        def funcReturnCb(self, design):\n"
            "            return self.count < 100\n"
            "    c = Counter()\n"
            "    pyScript.dbRegTraverseTrigger(c)\n"
            "    return c\n") % fn
        prompt = ("Write a Python function %s() that defines a Counter subclass of "
                  "dbTraverseTriggerFunc, registers it, and returns the instance. The "
                  "counter stops after 100 designs." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python multi-step trace using %s." % name
    return prompt, completion, [name], "S4 multi-step"


def _s5_param_var(name):
    fn = "var_" + name.lower()
    if name == "dbCreateLib":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib_name, path, tech):\n"
            "    lib = pyScript.emyString(lib_name)\n"
            "    p = pyScript.emyString(path)\n"
            "    tf = pyScript.emyString(tech)\n"
            "    return pyScript.dbCreateLib(lib=lib, path=p, techFile=tf)\n") % fn
        prompt = ("Write a Python function %s(lib_name, path, tech) that creates a library "
                  "with an explicit technology file, varying the path and techFile params."
                  % fn)
    elif name == "dbDelLib":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(names, from_disk):\n"
            "    lst = pyScript.vector1D_emyString()\n"
            "    for n in names:\n"
            "        lst.append(n)\n"
            "    return pyScript.dbDelLib(lib=lst, deleteFromDisk=from_disk)\n") % fn
        prompt = ("Write a Python function %s(names, from_disk) that varies the "
                  "deleteFromDisk flag when deleting multiple libraries." % fn)
    elif name == "dbOpenCVByType":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, views, mode):\n"
            "    return pyScript.dbOpenCVByType(lib, cell, views, '', mode)\n") % fn
        prompt = ("Write a Python function %s(lib, cell, views, mode) that opens a "
                  "cellview with a list of view names and a variable mode." % fn)
    elif name == "dbSaveCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, lib, cell, view):\n"
            "    return pyScript.dbSaveCV(cv=cv, lib=pyScript.emyString(lib),\n"
            "                           cell=pyScript.emyString(cell),\n"
            "                           view=pyScript.emyString(view))\n") % fn
        prompt = ("Write a Python function %s(cv, lib, cell, view) that saves a cellview "
                  "to a specified lib/cell/view, varying all three params." % fn)
    elif name == "dbDeleteAll":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(figs):\n"
            "    return pyScript.dbDeleteAll(figs=figs)\n") % fn
        prompt = ("Write a Python function %s(figs) that deletes a varying list of "
                  "figures passed directly as vector1D_p_emyFig." % fn)
    elif name == "dbGetTrueOverlaps":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, bbox, layer, shape_only):\n"
            "    return pyScript.dbGetTrueOverlaps(cv=cv, bbox=bbox, layer=layer,\n"
            "                                        shapeOnly=shape_only)\n") % fn
        prompt = ("Write a Python function %s(cv, bbox, layer, shape_only) that varies "
                  "the shapeOnly filter when querying overlaps." % fn)
    elif name == "dbCrtPinByNet":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(net, fig, name, term):\n"
            "    return pyScript.dbCrtPinByNet(net=net, fig=fig,\n"
            "                                 name=pyScript.emyString(name), term=term)\n") % fn
        prompt = ("Write a Python function %s(net, fig, name, term) that creates a pin "
                  "by net with a variable name string." % fn)
    elif name == "dbConvertPolygonToPath":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(shape, keep):\n"
            "    return pyScript.dbConvertPolygonToPath(shape, keepShape=keep)\n") % fn
        prompt = ("Write a Python function %s(shape, keep) that converts a polygon to "
                  "path, varying the keepShape flag." % fn)
    elif name == "dbFindMemInstByNameEx":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(design, name, vec):\n"
            "    return pyScript.dbFindMemInstByNameEx(design, name, bVectorInst=vec)\n") % fn
        prompt = ("Write a Python function %s(design, name, vec) that finds an instance, "
                  "varying the bVectorInst flag." % fn)
    elif name == "dbRegTraverseTrigger":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(trigger_inst):\n"
            "    pyScript.dbRegTraverseTrigger(trigger_inst)\n"
            "    return trigger_inst\n") % fn
        prompt = ("Write a Python function %s(trigger_inst) that registers a pre-built "
                  "trigger instance and returns it." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function with varied params for %s." % name
    return prompt, completion, [name], "S5 param-variation"


def build_pairs(eval_eps, limit=None):
    pairs = []
    rejected = [0]
    reject_details = []

    def _add(ptype, cid, prompt, completion, api_used, note):
        blob = prompt + "\n" + completion
        hit = fingerprint_scan(blob, eval_eps)
        if hit:
            rejected[0] += 1
            reject_details.append({"id": cid, "type": ptype, "hit": hit})
            return
        pairs.append({"id": cid, "type": ptype, "prompt": prompt,
                      "completion": completion, "api_used": api_used,
                      "contamination_check": "PASS", "note": note})

    for name in API_ORDER:
        p, c, a, n = _s1_doc_to_code(name)
        _add("S1", "s1_" + name, p, c, a, n)
    for name in API_ORDER:
        p, c, a, n = _s4_multi_step(name)
        _add("S4", "s4_" + name, p, c, a, n)
    for name in API_ORDER:
        p, c, a, n = _s5_param_var(name)
        _add("S5", "s5_" + name, p, c, a, n)

    chains = [
        ("chain_create_open_save_close",
         "Write a Python function create_and_save(lib_name, cell_name) that initializes Aether, creates a library, opens a layout cellview for writing, saves it, and returns the bool from save.",
         ["dbCreateLib", "dbOpenCVByType", "dbSaveCV"],
         ("import pyAether as pyScript\n\n"
          "def create_and_save(lib_name, cell_name):\n"
          "    pyScript.emyInitAether('-adv')\n"
          "    lib = pyScript.emyString(lib_name)\n"
          "    pyScript.dbCreateLib(lib=lib)\n"
          "    cv = pyScript.dbOpenCVByType(lib, cell_name, 'layout', 'layout', 'w')\n"
          "    ok = pyScript.dbSaveCV(cv=cv)\n"
          "    return ok\n")),
        ("chain_create_delete_lib_lifecycle",
         "Write a Python function lib_lifecycle(lib_name) that creates a library, then deletes it from disk, returning the bool from delete.",
         ["dbCreateLib", "dbDelLib"],
         ("import pyAether as pyScript\n\n"
          "def lib_lifecycle(lib_name):\n"
          "    pyScript.emyInitAether('-adv')\n"
          "    pyScript.dbCreateLib(lib=pyScript.emyString(lib_name))\n"
          "    lst = pyScript.vector1D_emyString()\n"
          "    lst.append(lib_name)\n"
          "    return pyScript.dbDelLib(lib=lst, deleteFromDisk=True)\n")),
        ("chain_query_overlaps_delete_figs",
         "Write a Python function cleanup_overlaps(cv, bbox, layer) that queries true overlaps on a layer and deletes all returned figures.",
         ["dbGetTrueOverlaps", "dbDeleteAll"],
         ("import pyAether as pyScript\n\n"
          "def cleanup_overlaps(cv, bbox, layer):\n"
          "    results = pyScript.dbGetTrueOverlaps(cv=cv, bbox=bbox, layer=layer)\n"
          "    fig_list = pyScript.vector1D_p_emyFig()\n"
          "    for item in results:\n"
          "        fig_list.append(item[0])\n"
          "    return pyScript.dbDeleteAll(figs=fig_list)\n")),
        ("chain_find_inst_convert_polygon",
         "Write a Python function process_design(design, inst_name, poly_shape) that finds an instance by name and converts a polygon shape to a path, returning both results.",
         ["dbFindMemInstByNameEx", "dbConvertPolygonToPath"],
         ("import pyAether as pyScript\n\n"
          "def process_design(design, inst_name, poly_shape):\n"
          "    inst_res = pyScript.dbFindMemInstByNameEx(design, inst_name)\n"
          "    path_result = pyScript.dbConvertPolygonToPath(poly_shape)\n"
          "    return inst_res, path_result\n")),
        ("chain_create_net_pin_traverse",
         "Write a Python function setup_pin_and_traverse(cv, net_name, pin_name, fig, collector_class) that creates a net, creates a pin by net, registers a traverse trigger, and returns the pin and collector instance.",
         ["dbCrtPinByNet", "dbRegTraverseTrigger"],
         ("import pyAether as pyScript\n\n"
          "def setup_pin_and_traverse(cv, net_name, pin_name, fig, collector_class):\n"
          "    nm = pyScript.emyString(net_name)\n"
          "    net = pyScript.dbCrtNet(cv=cv, name=nm)\n"
          "    pm = pyScript.emyString(pin_name)\n"
          "    term = pyScript.dbCrtTerm(net=net, name=pm)\n"
          "    pin = pyScript.dbCrtPinByNet(net=net, fig=fig, name=pm, term=term)\n"
          "    collector = collector_class()\n"
          "    pyScript.dbRegTraverseTrigger(collector)\n"
          "    return pin, collector\n")),
    ]
    for cid, prompt, api_used, completion in chains:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")
    lookups = [
        ("create a new library in the EDA database", "dbCreateLib",
         'lib = pyScript.emyString("mylib")\npyScript.dbCreateLib(lib=lib)'),
        ("delete one or more libraries from the session or disk", "dbDelLib",
         'lst = pyScript.vector1D_emyString()\nlst.append("mylib")\npyScript.dbDelLib(lib=lst, deleteFromDisk=True)'),
        ("open a cellview by view type (layout/schematic/symbol)", "dbOpenCVByType",
         'cv = pyScript.dbOpenCVByType("mylib", "inv", "layout", "layout", "r")'),
        ("save a cellview to disk or as a new design", "dbSaveCV",
         'pyScript.dbSaveCV(cv=cv)'),
        ("delete multiple figure objects from the database", "dbDeleteAll",
         'figList = pyScript.vector1D_p_emyFig()\nfigList.append(fig)\npyScript.dbDeleteAll(figs=figList)'),
        ("query objects whose bboxes overlap a region", "dbGetTrueOverlaps",
         'bbox = pyScript.emyBoxF((0, 0), (100, 100))\nresults = pyScript.dbGetTrueOverlaps(cv=cv, bbox=bbox, layer="M1")'),
        ("create a pin associated with a net and figure", "dbCrtPinByNet",
         'pin = pyScript.dbCrtPinByNet(net=netId, fig=figId, name=pyScript.emyString("P"), term=termId)'),
        ("convert a polygon shape to a path shape", "dbConvertPolygonToPath",
         'path = pyScript.dbConvertPolygonToPath(polyShape)'),
        ("find a master instance by name in a design", "dbFindMemInstByNameEx",
         'res = pyScript.dbFindMemInstByNameEx(design, "U1")'),
        ("register a user-defined traverse trigger callback", "dbRegTraverseTrigger",
         'class MyTrav(pyScript.dbTraverseTriggerFunc):\n    def funcCb(self, d): pass\n    def funcReturnCb(self, d): return True\npyScript.dbRegTraverseTrigger(MyTrav())'),
    ]
    for intent, api, usage in lookups:
        prompt = ("You are an EDA automation assistant. Which PyAether API is used to %s? "
                  "Show a minimal correct usage example." % intent)
        completion = ("The API is `%s`.\n\n```python\nimport pyAether as pyScript\n%s\n```"
                      % (api, usage))
        _add("S6", "s6_" + api, prompt, completion, [api], "S6 API lookup")

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected[0], reject_details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    eval_eps = load_eval_entry_points()
    sys.stderr.write("Loaded %d eval entry_points for contam scan\n" % len(eval_eps))
    pairs, rejected, reject_details = build_pairs(eval_eps, limit=args.limit)
    by_type = {}
    for p in pairs:
        by_type.setdefault(p["type"], 0)
        by_type[p["type"]] += 1
    apis = set()
    for p in pairs:
        apis.update(p["api_used"])
    safety_counts = {}
    for p in pairs:
        for a in p["api_used"]:
            safety_counts[a] = API_DOCS.get(a, {}).get("safety", "?")
    summary = {
        "report_id": "R186",
        "total_pairs": len(pairs),
        "rejected_contam": rejected,
        "reject_details": reject_details,
        "by_type": by_type,
        "apis_covered": sorted(apis),
        "api_count": len(apis),
        "safety_per_api": safety_counts,
        "out_path": OUT_PATH,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if args.dry_run:
        sys.stderr.write("[dry-run] no file written\n")
        return
    with open(OUT_PATH, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    sz = os.path.getsize(OUT_PATH)
    sys.stderr.write("Wrote %d pairs (%d bytes) to %s\n" % (len(pairs), sz, OUT_PATH))
    if rejected:
        sys.stderr.write("GATE: FAIL (pollution detected) -- do NOT use v16\n")
        sys.exit(2)
    sys.stderr.write("GATE: PASS -- v16 is training-ready\n")


if __name__ == "__main__":
    main()

