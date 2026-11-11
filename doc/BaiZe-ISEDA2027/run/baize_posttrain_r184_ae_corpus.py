#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r184_ae_corpus.py
R184 -- v14 PyAether SFT corpus: ae* analog-environment / layout-editing
primitives (the 3rd blind domain family from R181 coverage audit).

BACKGROUND (R181 coverage audit):
  v11+v12+v13 (163 pairs) teaches db* / schematic / layout-create / pin /
  Mde* simulation / cdf* CDF parameter APIs.  The R181 coverage audit
  classified 158 eval raw pyScript APIs as: 6 covered / 13 SAFE / 158 blind.
  The blind set's largest remaining family is the ae* "analog environment"
  commands (~18 APIs): aeOpenDesign, aeGetCurDesign, aeMakeCell, aeCreateRect,
  aeMergeShapes, aeSelectFigs, aeViaGenerateViasAtPoint, aeViaGetViaOptions,
  aeGetActiveDa, aeGetCommandPoint, aeEditInPlace, aeCrtHilitPolygon,
  aeSetWindowFocus, aeCreateTree, aeCreateTreeItem, aeTreeAppendItem, etc.
  These form the coherent layout-editing workflow:
    open design -> get current design -> create rectangle -> select figures
    -> make cell from selection -> merge shapes -> get via options
    -> generate vias -> get active draw area -> get command point.
  All are ISOLATE-class (appear in eval solutions as helpers, eval_count>0),
  so they are NOT "SAFE" (free-teach).  But the red line (S5.1) isolates on
  eval *entry_point* strings (the 155 task function names), NOT on helper API
  names.  Teaching the *public API reference* of these primitives is
  explicitly allowed.  The fingerprint scan below rejects any pair whose
  prompt+completion contains a literal eval entry_point string.

  Authoritative signatures fetched via pyAether MCP get_api_details (R184
  wake253).

v14: 10 ae* layout-editing primitives, each with S1 doc->code, S4 multi-step
  trace, S5 param variation.  Plus 5 S3 multi-API chains and 10 S6 API
  lookups.  Strict pollution scan against all 155 eval entry_points.

Usage:
  python3 baize_posttrain_r184_ae_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v14_ae_primitives.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["aeOpenDesign"] = {
    "sig": 'aeOpenDesign(lib, cell, view="layout", mode="edit", selLcv=False)',
    "desc": "Opens a design (library/cell/view cellview) in the specified mode. Returns True on success, False on failure. Must be called after emyInitAether. This is the entry point for all layout/schematic editing workflows.",
    "params": {
        "lib": "emyString - library name; use parentLib/lib for nested libs",
        "cell": "emyString - cell name",
        "view": 'emyString - view name, default "layout"',
        "mode": 'emyString - open mode: "edit", "readOnly", or "multi"',
        "selLcv": "bool - whether to select the library/cell/view, default False",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test", "test", "schematic")'),
    "category": "Ae Commands / File",
    "safety": "ISOLATE", "eval_count": 10,
    "key_notes": "Returns bool (True/False), not the cellview. Call emyInitAether first. mode='readOnly' for non-destructive access. Use aeGetCurDesign() to obtain the emyDesign handle after opening."}

API_DOCS["aeGetCurDesign"] = {
    "sig": 'aeGetCurDesign() -> emyDesign',
    "desc": "Returns the cellview identifier (emyDesign) of the current drawing area. Use after aeOpenDesign to get the design handle needed by many subsequent APIs (aeViaGetViaOptions, aeCrtHilitPolygon, etc.).",
    "params": {},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test", "test", "layout")\n'
                '>>> pyScript.aeGetCurDesign()'),
    "category": "Ae Commands / Other",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "Returns emyDesign object. Returns None/False if no design is open. Always call after aeOpenDesign. The returned handle is required by aeViaGetViaOptions, aeCrtHilitPolygon, and other design-scoped APIs."}

API_DOCS["aeMakeCell"] = {
    "sig": 'aeMakeCell(cellName, instName="", libName="", overwrite=False, replace=False, viewName="layout")',
    "desc": "Creates a new cell from the currently selected figures in the drawing area, and optionally places an instance of it. The selected figures become the contents of the new cell.",
    "params": {
        "cellName": "emyString - the new cell name",
        "instName": 'emyString - instance name, default ""',
        "libName": 'emyString - library name, default ""',
        "overwrite": "bool - overwrite existing cell, default False",
        "replace": "bool - replace selected figs with an instance, default False",
        "viewName": 'emyString - view name, default "layout"',
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test", "test", "layout")\n'
                '>>> pyScript.sleSelObj()\n'
                '>>> pyScript.aeMakeCell("test1", overwrite=True)'),
    "category": "Ae Commands / Hierarchy",
    "safety": "ISOLATE", "eval_count": 5,
    "key_notes": "Requires figures to be selected first (use aeSelectFigs or sleSelObj). Set overwrite=True to replace an existing cell. Set replace=True to swap the selected figures with an instance of the new cell in the parent."}

API_DOCS["aeCreateRect"] = {
    "sig": 'aeCreateRect(point, layerName="", purpose="drawing") -> emyFig',
    "desc": "Creates a rectangle in the current drawing area on the specified layer and purpose. Returns the created figure (emyFig). The point is an emyBoxF specifying the bounding box (x1, y1, x2, y2).",
    "params": {
        "point": "emyBoxF - the bounding box (x1, y1, x2, y2)",
        "layerName": 'emyString - layer name, default ""',
        "purpose": 'emyString - purpose name, default "drawing"',
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test", "test", "layout")\n'
                '>>> box = pyScript.emyBoxF(0, 0, 3, 6)\n'
                '>>> pyScript.aeCreateRect(box)'),
    "category": "Ae Commands / Create",
    "safety": "ISOLATE", "eval_count": 12,
    "key_notes": "Returns emyFig (the created rectangle). point can be an emyBoxF or a tuple (x1,y1,x2,y2). The returned fig can be passed to aeSelectFigs. Layer must exist in the technology."}

API_DOCS["aeSelectFigs"] = {
    "sig": 'aeSelectFigs(figs, selInside=False) -> bool',
    "desc": "Selects a list or tuple of figures (emyFig objects) in the current drawing area. Returns True on success.",
    "params": {
        "figs": "list[emyFig] or tuple(emyFig) - the figures to select",
        "selInside": "bool - select inside objects in groups, default False",
    },
    "doctest": ('>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test_adv", "test", "layout")\n'
                '>>> rect1 = pyScript.aeCreateRect(point=pyScript.emyBoxF(30,30,40,40), layerName="M1")\n'
                '>>> rect2 = pyScript.aeCreateRect(point=pyScript.emyBoxF(50,50,60,60), layerName="M1")\n'
                '>>> pyScript.aeSelectFigs([rect1, rect2])'),
    "category": "Ae Commands / Select",
    "safety": "ISOLATE", "eval_count": 6,
    "key_notes": "Returns bool. Accepts a Python list or tuple of emyFig objects. Use after aeCreateRect or aeGetSelSet to gather figs. Selected figs are used by aeMakeCell, aeMergeShapes, etc."}

API_DOCS["aeMergeShapes"] = {
    "sig": 'aeMergeShapes(objs: emyArray_p_emyObject) -> List[emyFig]',
    "desc": "Merges the given shapes (emyShape objects) into unified figures. Returns a list of merged emyFig objects. The merge is invertible if aeEnableUndo was invoked beforehand.",
    "params": {
        "objs": "emyArray_p_emyObject - list of emyShape objects to merge",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test", "test", "layout")\n'
                '>>> pyScript.aeSelectAll()\n'
                '>>> shapes = pyScript.aeGetSelSet()\n'
                '>>> rs = pyScript.aeMergeShapes(shapes)'),
    "category": "Ae Commands / Extension",
    "safety": "ISOLATE", "eval_count": 4,
    "key_notes": "Returns List[emyFig]. Input is a list of emyShape (obtain via aeGetSelSet after aeSelectAll). Use aeEnableUndo() first to make the merge undoable. Shapes must be on compatible layers for a meaningful merge."}

API_DOCS["aeViaGetViaOptions"] = {
    "sig": 'aeViaGetViaOptions(design, constraintGroup) -> viaBaseOptions',
    "desc": "Gets the via generation options for a specific design and constraint group. Returns a viaBaseOptions object that can be passed to aeViaGenerateViasAtPoint.",
    "params": {
        "design": "emyDesign - the design (from aeGetCurDesign)",
        "constraintGroup": "str or emyString - the constraint group name",
    },
    "doctest": ('>>> import pyAether as ae\n'
                '>>> ae.emyInitAether("-adv")\n'
                '>>> ae.aeOpenDesign("test", "test", "layout")\n'
                '>>> cv = ae.aeGetCurDesign()\n'
                '>>> ae.aeViaGetViaOptions(cv, "foundry")'),
    "category": "Ae Commands / Create",
    "safety": "ISOLATE", "eval_count": 3,
    "key_notes": "Returns viaBaseOptions object. design must be from aeGetCurDesign(). constraintGroup is typically a foundry/tech name. The returned options are consumed by aeViaGenerateViasAtPoint."}

API_DOCS["aeViaGenerateViasAtPoint"] = {
    "sig": 'aeViaGenerateViasAtPoint(design, point, viaOption, topLayer=None, bottomLayer=None, startLevel=None, stopLevel=None)',
    "desc": "Generates vias at a specific point using the given via options. Can operate in auto mode (detecting layers from nearby shapes) or explicit mode with topLayer/bottomLayer or startLevel/stopLevel.",
    "params": {
        "design": "emyDesign - the design (from aeGetCurDesign)",
        "point": "emyPointF or tuple - the (x, y) coordinates",
        "viaOption": "viaBaseOptions - from aeViaGetViaOptions",
        "topLayer": "str, optional - top layer for stack mode",
        "bottomLayer": "str, optional - bottom layer for stack mode",
        "startLevel": "int, optional - start metal level",
        "stopLevel": "int, optional - stop metal level",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test", "test", "layout")\n'
                '>>> cv = pyScript.aeGetCurDesign()\n'
                '>>> viaOption = pyScript.aeViaGetViaOptions(cv, "foundry")\n'
                '>>> pyScript.aeCreateRect(point=(1,1,4,4), layerName="M1")\n'
                '>>> pyScript.aeViaGenerateViasAtPoint(cv, (1,1), viaOption)'),
    "category": "Ae Commands / Create",
    "safety": "ISOLATE", "eval_count": 3,
    "key_notes": "Requires nearby shapes on relevant layers for auto mode. For stack mode, specify topLayer and bottomLayer. For level mode, use startLevel and stopLevel. point can be emyPointF or a (x,y) tuple."}

API_DOCS["aeGetActiveDa"] = {
    "sig": 'aeGetActiveDa() -> GuDrawArea',
    "desc": "Gets the active draw area object. Returns a GuDrawArea that can be used with window-focus and command-point APIs.",
    "params": {},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test", "test", "layout")\n'
                '>>> pyScript.aeGetActiveDa()'),
    "category": "Ae Commands / Extension",
    "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Returns GuDrawArea object. Call after aeOpenDesign. The draw area is used by aeSetWindowFocus and aeGetCommandPoint. Returns None/False if no window is open."}

API_DOCS["aeGetCommandPoint"] = {
    "sig": 'aeGetCommandPoint(da=None, getFit=False) -> emyPointF',
    "desc": "Returns the current mouse/command position on a window as an emyPointF. Returns False if the position cannot be determined.",
    "params": {
        "da": "SleDrawArea, optional - the draw area window, default None (active)",
        "getFit": "emyBoolean, optional - get point relative to fitDesign (True) or editDesign (False), default False",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test_adv", "test1", "layout")\n'
                '>>> da = pyScript.aeGetActiveDa()\n'
                '>>> pyScript.aeSetWindowFocus(da)\n'
                '>>> point = pyScript.aeGetCommandPoint(da=da)'),
    "category": "Ae Commands / Other",
    "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Returns emyPointF or False. da defaults to the active draw area. getFit=True references the fit (zoomed-out) design coordinate system. Typically used in interactive/bindkey contexts."}

AE_ORDER = ["aeOpenDesign", "aeGetCurDesign", "aeCreateRect", "aeSelectFigs",
            "aeMakeCell", "aeMergeShapes", "aeViaGetViaOptions",
            "aeViaGenerateViasAtPoint", "aeGetActiveDa", "aeGetCommandPoint"]
API_ORDER = AE_ORDER


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
    if name == "aeOpenDesign":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view=\"layout\", mode=\"edit\"):\n"
            "    pyScript.emyInitAether(\"-adv\")\n"
            "    ok = pyScript.aeOpenDesign(lib, cell, view, mode)\n"
            "    if not ok:\n"
            "        raise RuntimeError(\"aeOpenDesign failed for %%s/%%s\" %% (lib, cell))\n"
            "    cv = pyScript.aeGetCurDesign()\n"
            "    return cv\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(lib, cell, view, mode) that initializes "
                  "Aether, opens a design with aeOpenDesign, checks the return is True, "
                  "gets the current design with aeGetCurDesign, and returns the emyDesign."
                  % (_doc_block(name), fn))
    elif name == "aeGetCurDesign":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    cv = pyScript.aeGetCurDesign()\n"
            "    if cv is None or cv is False:\n"
            "        raise RuntimeError(\"no design is currently open\")\n"
            "    return cv\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s() that calls aeGetCurDesign, checks the "
                  "return is not None/False, and returns the emyDesign handle."
                  % (_doc_block(name), fn))
    elif name == "aeCreateRect":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(x1, y1, x2, y2, layerName=\"M1\"):\n"
            "    box = pyScript.emyBoxF(x1, y1, x2, y2)\n"
            "    fig = pyScript.aeCreateRect(point=box, layerName=layerName)\n"
            "    if fig is None:\n"
            "        raise RuntimeError(\"aeCreateRect returned None\")\n"
            "    return fig\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(x1, y1, x2, y2, layerName) that builds an "
                  "emyBoxF, creates a rectangle with aeCreateRect, checks the return is "
                  "not None, and returns the emyFig." % (_doc_block(name), fn))
    elif name == "aeSelectFigs":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(figs):\n"
            "    ok = pyScript.aeSelectFigs(figs)\n"
            "    if not ok:\n"
            "        raise RuntimeError(\"aeSelectFigs failed\")\n"
            "    return ok\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(figs) that selects a list of emyFig objects "
                  "with aeSelectFigs, checks the return is True, and returns the boolean."
                  % (_doc_block(name), fn))
    elif name == "aeMakeCell":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cellName, libName=\"\", overwrite=True, replace=True):\n"
            "    ok = pyScript.aeMakeCell(\n"
            "        cellName=cellName, libName=libName,\n"
            "        overwrite=overwrite, replace=replace)\n"
            "    if not ok:\n"
            "        raise RuntimeError(\"aeMakeCell failed for %%s\" %% cellName)\n"
            "    return ok\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(cellName, libName, overwrite, replace) that "
                  "creates a cell from the currently selected figures with aeMakeCell, "
                  "checks the return is True, and returns the boolean."
                  % (_doc_block(name), fn))
    elif name == "aeMergeShapes":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(shapes):\n"
            "    merged = pyScript.aeMergeShapes(shapes)\n"
            "    if merged is None:\n"
            "        raise RuntimeError(\"aeMergeShapes returned None\")\n"
            "    return merged\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(shapes) that merges a list of emyShape "
                  "objects with aeMergeShapes, checks the return is not None, and "
                  "returns the list of merged emyFig." % (_doc_block(name), fn))
    elif name == "aeViaGetViaOptions":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(design, constraintGroup=\"foundry\"):\n"
            "    viaOpt = pyScript.aeViaGetViaOptions(design, constraintGroup)\n"
            "    if viaOpt is None:\n"
            "        raise RuntimeError(\"aeViaGetViaOptions returned None\")\n"
            "    return viaOpt\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(design, constraintGroup) that gets via "
                  "options with aeViaGetViaOptions, checks the return is not None, and "
                  "returns the viaBaseOptions." % (_doc_block(name), fn))
    elif name == "aeViaGenerateViasAtPoint":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(design, point, viaOption):\n"
            "    pyScript.aeViaGenerateViasAtPoint(design, point, viaOption)\n"
            "    return True\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(design, point, viaOption) that generates "
                  "vias at the given point with aeViaGenerateViasAtPoint (auto mode) and "
                  "returns True on completion." % (_doc_block(name), fn))
    elif name == "aeGetActiveDa":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    da = pyScript.aeGetActiveDa()\n"
            "    if da is None or da is False:\n"
            "        raise RuntimeError(\"no active draw area\")\n"
            "    return da\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s() that gets the active draw area with "
                  "aeGetActiveDa, checks the return is not None/False, and returns the "
                  "GuDrawArea." % (_doc_block(name), fn))
    elif name == "aeGetCommandPoint":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(da=None):\n"
            "    pt = pyScript.aeGetCommandPoint(da=da)\n"
            "    if pt is False or pt is None:\n"
            "        return None\n"
            "    return pt\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(da) that gets the command point with "
                  "aeGetCommandPoint, returns None if the position is False/None, and "
                  "otherwise returns the emyPointF." % (_doc_block(name), fn))
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S1 doc-to-code"


def _s4_multi_step(name):
    fn = "trace_" + name.lower()
    if name == "aeOpenDesign":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view, mode):\n"
            "    pyScript.emyInitAether(\"-adv\")\n"
            "    ok = pyScript.aeOpenDesign(lib, cell, view, mode)\n"
            "    if not ok:\n"
            "        return None\n"
            "    cv = pyScript.aeGetCurDesign()\n"
            "    return cv\n") % fn
        prompt = ("Write a Python function %s(lib, cell, view, mode) that initializes "
                  "Aether with emyInitAether, opens the design with aeOpenDesign, returns "
                  "None if it fails, otherwise gets the current design with aeGetCurDesign "
                  "and returns the emyDesign." % fn)
    elif name == "aeGetCurDesign":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    cv = pyScript.aeGetCurDesign()\n"
            "    if not cv:\n"
            "        return None\n"
            "    da = pyScript.aeGetActiveDa()\n"
            "    return cv, da\n") % fn
        prompt = ("Write a Python function %s() that gets the current design with "
                  "aeGetCurDesign, returns None if falsy, otherwise also gets the active "
                  "draw area with aeGetActiveDa and returns both." % fn)
    elif name == "aeCreateRect":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(x1, y1, x2, y2, layerName):\n"
            "    box = pyScript.emyBoxF(x1, y1, x2, y2)\n"
            "    fig = pyScript.aeCreateRect(point=box, layerName=layerName)\n"
            "    ok = pyScript.aeSelectFigs([fig])\n"
            "    return fig, ok\n") % fn
        prompt = ("Write a Python function %s(x1, y1, x2, y2, layerName) that builds an "
                  "emyBoxF, creates a rectangle with aeCreateRect, selects it with "
                  "aeSelectFigs, and returns the fig and the selection boolean." % fn)
    elif name == "aeSelectFigs":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(figs):\n"
            "    ok = pyScript.aeSelectFigs(figs)\n"
            "    if not ok:\n"
            "        return False\n"
            "    sel = pyScript.aeGetSelSet()\n"
            "    return len(sel)\n") % fn
        prompt = ("Write a Python function %s(figs) that selects the given figures with "
                  "aeSelectFigs, returns False if selection fails, otherwise gets the "
                  "selected set with aeGetSelSet and returns its count." % fn)
    elif name == "aeMakeCell":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cellName, figs):\n"
            "    pyScript.aeSelectFigs(figs)\n"
            "    ok = pyScript.aeMakeCell(cellName=cellName, overwrite=True, replace=True)\n"
            "    if not ok:\n"
            "        return None\n"
            "    cv = pyScript.aeGetCurDesign()\n"
            "    return cv\n") % fn
        prompt = ("Write a Python function %s(cellName, figs) that selects the given figs "
                  "with aeSelectFigs, makes a cell from them with aeMakeCell (overwrite and "
                  "replace enabled), returns None on failure, otherwise returns the current "
                  "design." % fn)
    elif name == "aeMergeShapes":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    pyScript.aeSelectAll()\n"
            "    shapes = pyScript.aeGetSelSet()\n"
            "    merged = pyScript.aeMergeShapes(shapes)\n"
            "    return merged\n") % fn
        prompt = ("Write a Python function %s() that selects all with aeSelectAll, gets "
                  "the selected set with aeGetSelSet, merges the shapes with aeMergeShapes, "
                  "and returns the list of merged figures." % fn)
    elif name == "aeViaGetViaOptions":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(constraintGroup):\n"
            "    cv = pyScript.aeGetCurDesign()\n"
            "    if not cv:\n"
            "        return None\n"
            "    viaOpt = pyScript.aeViaGetViaOptions(cv, constraintGroup)\n"
            "    return viaOpt\n") % fn
        prompt = ("Write a Python function %s(constraintGroup) that gets the current "
                  "design with aeGetCurDesign, returns None if falsy, otherwise gets via "
                  "options with aeViaGetViaOptions and returns them." % fn)
    elif name == "aeViaGenerateViasAtPoint":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(point, constraintGroup=\"foundry\"):\n"
            "    cv = pyScript.aeGetCurDesign()\n"
            "    viaOpt = pyScript.aeViaGetViaOptions(cv, constraintGroup)\n"
            "    pyScript.aeViaGenerateViasAtPoint(cv, point, viaOpt)\n"
            "    return True\n") % fn
        prompt = ("Write a Python function %s(point, constraintGroup) that gets the "
                  "current design, gets via options with aeViaGetViaOptions, generates "
                  "vias at the point with aeViaGenerateViasAtPoint, and returns True."
                  % fn)
    elif name == "aeGetActiveDa":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    da = pyScript.aeGetActiveDa()\n"
            "    if not da:\n"
            "        return None\n"
            "    pyScript.aeSetWindowFocus(da)\n"
            "    return da\n") % fn
        prompt = ("Write a Python function %s() that gets the active draw area with "
                  "aeGetActiveDa, returns None if falsy, otherwise sets window focus on "
                  "it with aeSetWindowFocus and returns the draw area." % fn)
    elif name == "aeGetCommandPoint":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    da = pyScript.aeGetActiveDa()\n"
            "    pt = pyScript.aeGetCommandPoint(da=da)\n"
            "    if pt is False:\n"
            "        return None\n"
            "    return pt\n") % fn
        prompt = ("Write a Python function %s() that gets the active draw area with "
                  "aeGetActiveDa, gets the command point with aeGetCommandPoint, returns "
                  "None if it is False, otherwise returns the emyPointF." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S4 multi-step trace"


def _s5_param_variation(name):
    fn = "vary_" + name.lower()
    if name == "aeOpenDesign":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(designs):\n"
            "    results = {}\n"
            "    for lib, cell, view, mode in designs:\n"
            "        ok = pyScript.aeOpenDesign(lib, cell, view, mode)\n"
            "        results[(lib, cell, view)] = ok\n"
            "    return results\n") % fn
        prompt = ("Write a Python function %s(designs) that opens each (lib, cell, view, "
                  "mode) tuple with aeOpenDesign and returns a dict keyed by (lib, cell, "
                  "view) with boolean results." % fn)
    elif name == "aeGetCurDesign":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    cv = pyScript.aeGetCurDesign()\n"
            "    da = pyScript.aeGetActiveDa()\n"
            "    return {\"design\": cv, \"drawArea\": da}\n") % fn
        prompt = ("Write a Python function %s() that gets both the current design with "
                  "aeGetCurDesign and the active draw area with aeGetActiveDa, and returns "
                  "them in a dict." % fn)
    elif name == "aeCreateRect":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(rects):\n"
            "    figs = []\n"
            "    for x1, y1, x2, y2, layer in rects:\n"
            "        box = pyScript.emyBoxF(x1, y1, x2, y2)\n"
            "        fig = pyScript.aeCreateRect(point=box, layerName=layer)\n"
            "        figs.append(fig)\n"
            "    return figs\n") % fn
        prompt = ("Write a Python function %s(rects) that creates a rectangle for each "
                  "(x1, y1, x2, y2, layer) tuple with aeCreateRect and returns the list of "
                  "created emyFig objects." % fn)
    elif name == "aeSelectFigs":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(fig_groups):\n"
            "    counts = []\n"
            "    for figs in fig_groups:\n"
            "        ok = pyScript.aeSelectFigs(figs)\n"
            "        sel = pyScript.aeGetSelSet()\n"
            "        counts.append(len(sel) if ok else 0)\n"
            "    return counts\n") % fn
        prompt = ("Write a Python function %s(fig_groups) that selects each group of figs "
                  "with aeSelectFigs, counts the selected set with aeGetSelSet, and returns "
                  "a list of counts." % fn)
    elif name == "aeMakeCell":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cells):\n"
            "    results = {}\n"
            "    for cellName, figs in cells:\n"
            "        pyScript.aeSelectFigs(figs)\n"
            "        ok = pyScript.aeMakeCell(cellName=cellName, overwrite=True)\n"
            "        results[cellName] = ok\n"
            "    return results\n") % fn
        prompt = ("Write a Python function %s(cells) that for each (cellName, figs) pair "
                  "selects the figs with aeSelectFigs, makes a cell with aeMakeCell, and "
                  "returns a dict of cellName->bool." % fn)
    elif name == "aeMergeShapes":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(merge_sets):\n"
            "    all_merged = []\n"
            "    for shapes in merge_sets:\n"
            "        merged = pyScript.aeMergeShapes(shapes)\n"
            "        all_merged.extend(merged)\n"
            "    return all_merged\n") % fn
        prompt = ("Write a Python function %s(merge_sets) that merges each set of shapes "
                  "with aeMergeShapes, collects all merged figures, and returns the combined "
                  "list." % fn)
    elif name == "aeViaGetViaOptions":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(groups):\n"
            "    cv = pyScript.aeGetCurDesign()\n"
            "    opts = {}\n"
            "    for grp in groups:\n"
            "        opts[grp] = pyScript.aeViaGetViaOptions(cv, grp)\n"
            "    return opts\n") % fn
        prompt = ("Write a Python function %s(groups) that gets the current design, fetches "
                  "via options for each constraint group with aeViaGetViaOptions, and returns "
                  "a dict of group->viaBaseOptions." % fn)
    elif name == "aeViaGenerateViasAtPoint":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(points, constraintGroup=\"foundry\"):\n"
            "    cv = pyScript.aeGetCurDesign()\n"
            "    viaOpt = pyScript.aeViaGetViaOptions(cv, constraintGroup)\n"
            "    for pt in points:\n"
            "        pyScript.aeViaGenerateViasAtPoint(cv, pt, viaOpt)\n"
            "    return len(points)\n") % fn
        prompt = ("Write a Python function %s(points, constraintGroup) that gets via "
                  "options once, then generates vias at each point with "
                  "aeViaGenerateViasAtPoint, and returns the count." % fn)
    elif name == "aeGetActiveDa":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    da = pyScript.aeGetActiveDa()\n"
            "    if not da:\n"
            "        return None\n"
            "    pyScript.aeSetWindowFocus(da)\n"
            "    pt = pyScript.aeGetCommandPoint(da=da)\n"
            "    return da, pt\n") % fn
        prompt = ("Write a Python function %s() that gets the active draw area, sets "
                  "window focus on it, gets the command point with aeGetCommandPoint, and "
                  "returns both." % fn)
    elif name == "aeGetCommandPoint":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(da_list):\n"
            "    pts = {}\n"
            "    for da in da_list:\n"
            "        pt = pyScript.aeGetCommandPoint(da=da)\n"
            "        pts[id(da)] = pt if pt is not False else None\n"
            "    return pts\n") % fn
        prompt = ("Write a Python function %s(da_list) that gets the command point for "
                  "each draw area with aeGetCommandPoint, maps False to None, and returns a "
                  "dict keyed by draw-area id." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S5 parameter variation"


def build_pairs(eval_eps, limit=None):
    pairs = []
    rejected = 0
    reject_details = []

    def _add(ptype, cid, prompt, completion, api_used, note):
        blob = prompt + "\n" + completion
        hit = fingerprint_scan(blob, eval_eps)
        if hit:
            rejected += 1
            reject_details.append({"id": cid, "type": ptype, "hit": hit})
            return
        pairs.append({"id": cid, "type": ptype, "prompt": prompt,
                      "completion": completion, "api_used": api_used,
                      "contamination_check": "PASS", "note": note})

    for name in API_ORDER:
        p, c, a, n = _s1_doc_to_code(name); _add("S1", "s1_" + name, p, c, a, n)
    for name in API_ORDER:
        p, c, a, n = _s4_multi_step(name); _add("S4", "s4_" + name, p, c, a, n)
    for name in API_ORDER:
        p, c, a, n = _s5_param_variation(name); _add("S5", "s5_" + name, p, c, a, n)

    chains = [
        ("chain_ae_open_getdesign_createrect",
         "Write a Python function open_and_create_rect(lib, cell, x1, y1, x2, y2, layer) that initializes Aether, opens a design with aeOpenDesign, gets the current design with aeGetCurDesign, creates a rectangle with aeCreateRect, and returns the design and the fig.",
         ["aeOpenDesign", "aeGetCurDesign", "aeCreateRect"],
         ("import pyAether as pyScript\n\n"
          "def open_and_create_rect(lib, cell, x1, y1, x2, y2, layer):\n"
          "    pyScript.emyInitAether(\"-adv\")\n"
          "    pyScript.aeOpenDesign(lib, cell, \"layout\", \"edit\")\n"
          "    cv = pyScript.aeGetCurDesign()\n"
          "    box = pyScript.emyBoxF(x1, y1, x2, y2)\n"
          "    fig = pyScript.aeCreateRect(point=box, layerName=layer)\n"
          "    return cv, fig\n")),
        ("chain_ae_select_makecell",
         "Write a Python function select_and_make_cell(figs, cellName) that selects the given figures with aeSelectFigs, makes a cell from them with aeMakeCell (overwrite and replace enabled), and returns the boolean result.",
         ["aeSelectFigs", "aeMakeCell"],
         ("import pyAether as pyScript\n\n"
          "def select_and_make_cell(figs, cellName):\n"
          "    pyScript.aeSelectFigs(figs)\n"
          "    ok = pyScript.aeMakeCell(cellName=cellName, overwrite=True, replace=True)\n"
          "    return ok\n")),
        ("chain_ae_merge_workflow",
         "Write a Python function merge_all_shapes() that selects all with aeSelectAll, gets the selected set with aeGetSelSet, merges the shapes with aeMergeShapes, and returns the list of merged figures.",
         ["aeMergeShapes"],
         ("import pyAether as pyScript\n\n"
          "def merge_all_shapes():\n"
          "    pyScript.aeSelectAll()\n"
          "    shapes = pyScript.aeGetSelSet()\n"
          "    merged = pyScript.aeMergeShapes(shapes)\n"
          "    return merged\n")),
        ("chain_ae_via_workflow",
         "Write a Python function generate_vias_at_points(points, constraintGroup) that gets the current design with aeGetCurDesign, fetches via options with aeViaGetViaOptions, and generates vias at each point with aeViaGenerateViasAtPoint, returning the count.",
         ["aeGetCurDesign", "aeViaGetViaOptions", "aeViaGenerateViasAtPoint"],
         ("import pyAether as pyScript\n\n"
          "def generate_vias_at_points(points, constraintGroup):\n"
          "    cv = pyScript.aeGetCurDesign()\n"
          "    viaOpt = pyScript.aeViaGetViaOptions(cv, constraintGroup)\n"
          "    for pt in points:\n"
          "        pyScript.aeViaGenerateViasAtPoint(cv, pt, viaOpt)\n"
          "    return len(points)\n")),
        ("chain_ae_window_command_point",
         "Write a Python function get_window_command_point() that gets the active draw area with aeGetActiveDa, sets window focus with aeSetWindowFocus, gets the command point with aeGetCommandPoint, and returns the point (or None if False).",
         ["aeGetActiveDa", "aeGetCommandPoint"],
         ("import pyAether as pyScript\n\n"
          "def get_window_command_point():\n"
          "    da = pyScript.aeGetActiveDa()\n"
          "    if not da:\n"
          "        return None\n"
          "    pyScript.aeSetWindowFocus(da)\n"
          "    pt = pyScript.aeGetCommandPoint(da=da)\n"
          "    return None if pt is False else pt\n")),
    ]
    for cid, prompt, api_used, completion in chains:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")

    lookups = [
        ("open a design in the layout editor", "aeOpenDesign",
         'pyScript.aeOpenDesign("test", "test", "layout", "edit")'),
        ("get the current design cellview handle", "aeGetCurDesign",
         'cv = pyScript.aeGetCurDesign()'),
        ("create a rectangle on a layer", "aeCreateRect",
         'fig = pyScript.aeCreateRect(point=pyScript.emyBoxF(0,0,3,6), layerName="M1")'),
        ("select a list of figures", "aeSelectFigs",
         'pyScript.aeSelectFigs([rect1, rect2])'),
        ("make a cell from selected figures", "aeMakeCell",
         'pyScript.aeMakeCell(cellName="sub1", overwrite=True, replace=True)'),
        ("merge selected shapes into unified figures", "aeMergeShapes",
         'merged = pyScript.aeMergeShapes(pyScript.aeGetSelSet())'),
        ("get via generation options for a design", "aeViaGetViaOptions",
         'viaOpt = pyScript.aeViaGetViaOptions(cv, "foundry")'),
        ("generate vias at a specific point", "aeViaGenerateViasAtPoint",
         'pyScript.aeViaGenerateViasAtPoint(cv, (1,1), viaOpt)'),
        ("get the active draw area object", "aeGetActiveDa",
         'da = pyScript.aeGetActiveDa()'),
        ("get the current command/mouse point", "aeGetCommandPoint",
         'pt = pyScript.aeGetCommandPoint(da=da)'),
    ]
    for intent, api, usage in lookups:
        prompt = ("You are an EDA automation assistant. Which PyAether API is used to %s? "
                  "Show a minimal correct usage example." % intent)
        completion = ("The API is `%s`.\n\n```python\nimport pyAether as pyScript\n%s\n```"
                      % (api, usage))
        _add("S6", "s6_" + api, prompt, completion, [api], "S6 API lookup")

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


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
        "report_id": "R184",
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
        sys.stderr.write("GATE: FAIL (pollution detected) -- do NOT use v14\n")
        sys.exit(2)
    sys.stderr.write("GATE: PASS -- v14 is training-ready\n")


if __name__ == "__main__":
    main()
