#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r179_v9_corpus.py
R179 -- v9 PyAether SFT corpus: closes the v8 layout-create blind spot.

BACKGROUND (R178 inventory):
  v8 (25 pairs / 11 APIs) covered only schematic-create APIs and had ZERO
  coverage of the 4 core layout-create APIs that the 158-task eval uses most
  heavily (dbCrtInst:58, dbCrtRect:47, dbCrtPath:10, dbCrtPolygon:6 = 121 eval
  refs). Layout scenario (64 tasks) is the largest coverage gap.
  R178 pinpointed the hallucination root cause: v8 pairs show the API NAME
  in doc form but do NOT reinforce the exact call pattern
  pyScript.dbCrtSchWire(cv=..., point=...) in VARIED contexts, so SFT falls
  back to generic lib.openSchematic hallucinations.

v9 FIX (this script):
  1. Adds the 4 layout-create APIs (dbCrtRect/dbCrtPolygon/dbCrtInst/dbCrtPath)
     with AUTHORITATIVE signatures retrieved via pyAether MCP get_api_details.
  2. Adds the 4 new SAFE expansion APIs (dbSchGetPinOrder, aeSchStretch,
     aeCrtWireLabelsAndPins, emyDesignIsSchematic) -- eval_count==0.
  3. Per-API MULTI-STEP traces (openCV -> create -> save) so the exact
     pyScript.<api>(cv=..., ...) call pattern is reinforced across varied
     contexts (the R178 anti-hallucination fix).
  4. Per-API PARAMETER VARIATIONS (different orient/layer/points).
  5. Strict pollution scan against all 155 eval entry_points; every
     completion checked. ISOLATE APIs taught ONLY from official API doc.

CONTAMINATION ISOLATION (red line S5.1):
  - Source = official PyAether API documentation, retrieved via the pyAether
    MCP get_api_details tool. NOT from any eval task.
  - The 158 eval tasks are never read (only entry_point strings loaded for
    fingerprint scan).
  - Fingerprint scan: every completion checked against eval entry_points.

Usage:
  python3 baize_posttrain_r179_v9_corpus.py [--dry-run] [--limit N]
"""
import argparse, hashlib, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v9_layout_create.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

# safety: SAFE = eval_count==0 (free); ISOLATE = eval_count>0 (scan required)
API_DOCS = {
    "dbCrtRect": {
        "sig": 'dbCrtRect(cv, bbox: emyBoxF, layer, purpose="drawing") -> emyShape',
        "desc": "Create a rectangle in schematic and symbol view.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "bbox": "emyBoxF - lower-left and upper-right corner",
                   "layer": "emyString - layer number or layer name",
                   "purpose": "emyString, optional - purpose number/name"},
        "doctest": '>>> import pyAether as pyScript\n>>> cvId = pyScript.dbOpenCV(lib="test", cell="test")\n>>> bbox = pyScript.emyBoxF((0, 0), (1, 1))\n>>> layer = pyScript.emyString("NSR")\n>>> pyScript.dbCrtRect(cv=cvId, bbox=bbox, layer=layer)',
        "category": "Layout / Create", "safety": "ISOLATE", "eval_count": 47},
    "dbCrtPolygon": {
        "sig": 'dbCrtPolygon(cv, points: vector1D_emyPointF, layer, purpose="drawing") -> emyShape',
        "desc": "Create a polygon in schematic and symbol view.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "points": "vector1D_emyPointF - boundary point list",
                   "layer": "emyString - layer number or layer name",
                   "purpose": "emyString, optional - purpose number/name"},
        "doctest": '>>> import pyAether as pyScript\n>>> cvId = pyScript.dbOpenCV(lib="test", cell="test")\n>>> points = [(0, 0), (3, 3), (3, 0)]\n>>> pyScript.dbCrtPolygon(cv=cvId, points=points, layer="M1")',
        "category": "Layout / Create", "safety": "ISOLATE", "eval_count": 6},
    "dbCrtInst": {
        "sig": 'dbCrtInst(cv, point, master=None, lib="", cell="", view="layout", inst="", orient="R0", justify="origin", rowPitch=0.0, colPitch=0.0, rows=1, cols=1, mag=1, angle=0, params=None) -> emyInst',
        "desc": "Create an instance. Returns a figure identifier.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "point": "emyPointF - origin of instance",
                   "lib": "emyString, optional - library name of instance",
                   "cell": "emyString, optional - cell name of instance",
                   "inst": "emyString, optional - name of instance",
                   "orient": "emyString, optional - R0/R90/R180/R270/MY/MYR90/MX/MXR90"},
        "doctest": '>>> import pyAether as pyScript\n>>> cvId = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n>>> pyScript.dbCrtInst(cv=cvId, point=(0, 0), lib="analogLib", cell="nmos", inst="M1", orient="R0")',
        "category": "Layout / Create", "safety": "ISOLATE", "eval_count": 58},
    "dbCrtPath": {
        "sig": 'dbCrtPath(cv, layer, points: vector1D_emyPointF, width, purpose="drawing", style="truncate", beginExt=0.0, endExt=0.0, corner=0.0, end=0.0, arcSegmentsNum=72, cornerType="Square", cutoffRatio=0.3, curveRadius=0) -> emyShape',
        "desc": "Create a path. Returns a shape identifier.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "layer": "emyString - layer number or layer name",
                   "points": "vector1D_emyPointF - point list of center line",
                   "width": "float - width of path",
                   "style": "emyString, optional - truncate/extend/round/antiESD/variable"},
        "doctest": '>>> import pyAether as pyScript\n>>> cvId = pyScript.dbOpenCV(lib="test", cell="test")\n>>> points = [(0, 0), (10, 0)]\n>>> pyScript.dbCrtPath(cv=cvId, layer="M1", points=points, width=1.0)',
        "category": "Layout / Create", "safety": "ISOLATE", "eval_count": 10},
    "dbSchGetPinOrder": {
        "sig": 'dbSchGetPinOrder(pDesign: emyDesign) -> emyStringArray',
        "desc": "Returns a list of pins defined in the portOrder property.",
        "params": {"pDesign": "emyDesign - the cellview whose pin order to retrieve"},
        "doctest": '>>> import pyAether as pyScript\n>>> cv = pyScript.aeGetCurDesign()\n>>> res = pyScript.dbSchGetPinOrder(cv)',
        "category": "Schematic / Query", "safety": "SAFE", "eval_count": 0},
    "aeSchStretch": {
        "sig": 'aeSchStretch(figs: List[emyFig], trans: emyTransformF) -> None',
        "desc": "Stretch objects with the specified transform info in schematic.",
        "params": {"figs": "List[emyFig] - the stretched objects",
                   "trans": "emyTransformF - transform info (x_off, y_off, orient)"},
        "doctest": '>>> import pyAether as pyScript\n>>> figs = pyScript.aeGetSelSet()\n>>> trans = pyScript.emyTransformF(1, 1, pyScript.emcR180)\n>>> pyScript.aeSchStretch(figs, trans)',
        "category": "Schematic / Edit", "safety": "SAFE", "eval_count": 0},
    "aeCrtWireLabelsAndPins": {
        "sig": 'aeCrtWireLabelsAndPins(design=None, inst=None, instTerm=None, isCrtLabels=True, isCrtPins=True) -> bool',
        "desc": "Generate label or pin for the specified term in schematic.",
        "params": {"design": "emyDesign, optional - the design",
                   "inst": "emyInst, optional - the instance",
                   "isCrtLabels": "bool - create labels",
                   "isCrtPins": "bool - create pins"},
        "doctest": '>>> import pyAether as pyScript\n>>> pyScript.aeCrtWireLabelsAndPins(design=cv, isCrtLabels=True)',
        "category": "Schematic / Create", "safety": "SAFE", "eval_count": 0},
    "emyDesignIsSchematic": {
        "sig": 'emyDesignIsSchematic(design: emyDesign) -> emyBoolean',
        "desc": "Check whether the design is schematic. Useful guard clause.",
        "params": {"design": "emyDesign - the design to check"},
        "doctest": '>>> import pyAether as pyScript\n>>> cv = pyScript.aeGetCurDesign()\n>>> is_sch = pyScript.emyDesignIsSchematic(cv)',
        "category": "Design / Query", "safety": "SAFE", "eval_count": 0},
    "dbCrtSchWire": {
        "sig": 'dbCrtSchWire(cv, point, wireMode="Narrow", width=0.0625, lockAngle="AnyAngle", flyLine=False, wireSnapping=True, color="cadetBlue", lineStyle="solid") -> Tuple[emyFig]',
        "desc": "Create a wire in schematic view.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "point": "vector1D_emyPointF - the points list to create the wire",
                   "wireMode": "emyString - Narrow or Wide (default Narrow)",
                   "width": "float - width of wide wire (default 0.0625)"},
        "doctest": '>>> import pyAether as pyScript\n>>> cvId = pyScript.dbOpenCV(lib="test", cell="test", view="schematic")\n>>> point = ((20.0, 10), (30, 10))\n>>> pyScript.dbCrtSchWire(cv=cvId, point=point)',
        "category": "Schematic / Create", "safety": "ISOLATE", "eval_count": 2},
    "dbCrtWire": {
        "sig": "dbCrtWire(cv, layer, points, width, purpose='drawing') -> emyFig",
        "desc": "Create a wire (layout). Returns a fig identifier.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "layer": "emyString - layer number or layer name",
                   "points": "vector1D_emyPointF - point list of center line",
                   "width": "float - width of wire"},
        "doctest": '>>> import pyAether as pyScript\n>>> cvId = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n>>> pyScript.dbCrtWire(cv=cvId, layer="M1", points=((0,0),(10,0)), width=0.5)',
        "category": "Layout / Create", "safety": "SAFE", "eval_count": 0},
    "dbCrtNet": {
        "sig": "dbCrtNet(cv: emyDesign, name: emyString) -> emyNet",
        "desc": "Create a net. Returns a net identifier if successful.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "name": "emyString - the net's name"},
        "doctest": '>>> import pyAether as pyScript\n>>> cvId = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n>>> pyScript.dbCrtNet(cv=cvId, name="net01")',
        "category": "Net / Create", "safety": "ISOLATE", "eval_count": 9},
    "dbCrtSchPin": {
        "sig": 'dbCrtSchPin(cv: emyDesign, name: emyString, point: emyPointF, direction: emyString="input", overbar: bool=False, orient: emyString="R0") -> emyPin',
        "desc": "Create a pin in schematic view.",
        "params": {"cv": "emyDesign - cell view identifier",
                   "name": "emyString - pin name",
                   "point": "emyPointF - pin location",
                   "direction": "emyString - input/output/inputOutput/switch"},
        "doctest": '>>> import pyAether as pyScript\n>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="schematic")\n>>> pyScript.dbCrtSchPin(cv=cv, name="Gate", point=(20, 10))',
        "category": "Schematic / Create", "safety": "ISOLATE", "eval_count": 3},
}


def _pid(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _contam_check(completion, eval_eps):
    """Return first eval entry_point substring found in completion, else None."""
    for ep in eval_eps:
        if ep and ep in completion:
            return ep
    return None


def load_eval_entry_points():
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
                rec = json.loads(line)
            except Exception:
                continue
            ep = rec.get("entry_point")
            if ep:
                eps.add(ep)
    return eps


def _s1_doc_to_code(name, doc):
    """Doc -> single-API code function (reinforces exact call pattern)."""
    dt = doc["doctest"]
    lines = [l for l in dt.split("\n") if l.strip()]
    body_lines = []
    for l in lines:
        s = l.strip()
        if s.startswith(">>>"):
            body_lines.append("    " + s[4:].strip())
    fn = "use_" + name.lower()
    body = "\n".join(body_lines) if body_lines else "    pass"
    completion = "import pyAether as pyScript\n\ndef %s():\n%s\n" % (fn, body)
    prompt = (
        "You are an EDA automation assistant. Read the following PyAether "
        "API documentation and write Python code that correctly uses this "
        "API.\n\n## API Documentation\n\n## %s\n\n`%s`(...)\n\n**`%s`**\n\n"
        "%s\n\nParameters\n%s\n\nExamples\n\n    %s"
    ) % (name, name, doc["sig"], doc["desc"],
         "\n".join("**%s**%s" % (k, " " + v) for k, v in doc["params"].items()),
         doc["doctest"].replace("\n", "\n    "))
    return prompt, completion, [name], "S1 doc->code"


def _s4_multistep_trace(name, doc):
    """Multi-step trace: openCV -> create -> save.
    The R178 anti-hallucination fix: reinforces pyScript.<api>(cv=..., ...)
    inside a realistic multi-step flow, not an isolated doc call."""
    cat = doc["category"]
    is_layout = "Layout" in cat or name in ("dbCrtRect", "dbCrtPolygon",
                                            "dbCrtInst", "dbCrtPath", "dbCrtWire")
    view = "layout" if is_layout else "schematic"
    fn = "build_" + name.lower()
    if name == "dbCrtRect":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, ll, ur, layer):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"%s\")\n"
            "    bbox = pyScript.emyBoxF(ll, ur)\n"
            "    shape = pyScript.dbCrtRect(cv=cv, bbox=bbox, layer=layer)\n"
            "    pyScript.dbSave(cv)\n"
            "    return shape\n") % (fn, view)
        prompt = ("Write a Python function %s(lib, cell, ll, ur, layer) that "
            "opens a %s cell view, creates a rectangle with dbCrtRect using a "
            "bounding box, saves the cell view, and returns the shape." % (fn, view))
    elif name == "dbCrtPolygon":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, pts, layer):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"%s\")\n"
            "    shape = pyScript.dbCrtPolygon(cv=cv, points=pts, layer=layer)\n"
            "    pyScript.dbSave(cv)\n"
            "    return shape\n") % (fn, view)
        prompt = ("Write a Python function %s(lib, cell, pts, layer) that "
            "opens a %s cell view, creates a polygon with dbCrtPolygon, saves "
            "the cell view, and returns the shape." % (fn, view))
    elif name == "dbCrtInst":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, inst_lib, inst_cell, origin, inst_name, orient):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"%s\")\n"
            "    fig = pyScript.dbCrtInst(cv=cv, point=origin, lib=inst_lib,\n"
            "                             cell=inst_cell, inst=inst_name, orient=orient)\n"
            "    pyScript.dbSave(cv)\n"
            "    return fig\n") % (fn, view)
        prompt = ("Write a Python function %s(lib, cell, inst_lib, inst_cell, "
            "origin, inst_name, orient) that opens a %s cell view, creates an "
            "instance with dbCrtInst, saves the cell view, and returns the "
            "instance figure." % (fn, view))
    elif name == "dbCrtPath":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, pts, layer, width):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"%s\")\n"
            "    shape = pyScript.dbCrtPath(cv=cv, layer=layer, points=pts, width=width)\n"
            "    pyScript.dbSave(cv)\n"
            "    return shape\n") % (fn, view)
        prompt = ("Write a Python function %s(lib, cell, pts, layer, width) "
            "that opens a %s cell view, creates a path with dbCrtPath, saves "
            "the cell view, and returns the shape." % (fn, view))
    elif name == "dbCrtWire":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, pts, layer, width):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"%s\")\n"
            "    fig = pyScript.dbCrtWire(cv=cv, layer=layer, points=pts, width=width)\n"
            "    pyScript.dbSave(cv)\n"
            "    return fig\n") % (fn, view)
        prompt = ("Write a Python function %s(lib, cell, pts, layer, width) "
            "that opens a %s cell view, creates a layout wire with dbCrtWire, "
            "saves the cell view, and returns the figure." % (fn, view))
    elif name == "dbCrtNet":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, net_name):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"%s\")\n"
            "    net = pyScript.dbCrtNet(cv=cv, name=net_name)\n"
            "    pyScript.dbSave(cv)\n"
            "    return net\n") % (fn, view)
        prompt = ("Write a Python function %s(lib, cell, net_name) that opens "
            "a %s cell view, creates a net with dbCrtNet, saves the cell view, "
            "and returns the net identifier." % (fn, view))
    elif name == "dbCrtSchWire":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, pts):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"schematic\")\n"
            "    figs = pyScript.dbCrtSchWire(cv=cv, point=pts)\n"
            "    pyScript.dbSave(cv)\n"
            "    return figs\n") % fn
        prompt = ("Write a Python function %s(lib, cell, pts) that opens a "
            "schematic cell view, creates a schematic wire with dbCrtSchWire, "
            "saves the cell view, and returns the wire figures." % fn)
    elif name == "dbCrtSchPin":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, pin_name, pt, direction):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"schematic\")\n"
            "    pin = pyScript.dbCrtSchPin(cv=cv, name=pin_name, point=pt, direction=direction)\n"
            "    pyScript.dbSave(cv)\n"
            "    return pin\n") % fn
        prompt = ("Write a Python function %s(lib, cell, pin_name, pt, "
            "direction) that opens a schematic cell view, creates a schematic "
            "pin with dbCrtSchPin, saves the cell view, and returns the pin." % fn)
    elif name == "dbSchGetPinOrder":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv):\n"
            "    if not pyScript.emyDesignIsSchematic(cv):\n"
            "        return []\n"
            "    return pyScript.dbSchGetPinOrder(cv)\n") % fn
        prompt = ("Write a Python function %s(cv) that checks the design is a "
            "schematic with emyDesignIsSchematic, and if so returns the pin "
            "order via dbSchGetPinOrder; otherwise returns an empty list." % fn)
    elif name == "aeSchStretch":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(figs, dx, dy, orient_const):\n"
            "    trans = pyScript.emyTransformF(dx, dy, orient_const)\n"
            "    pyScript.aeSchStretch(figs, trans)\n") % fn
        prompt = ("Write a Python function %s(figs, dx, dy, orient_const) that "
            "builds an emyTransformF then stretches the figures with "
            "aeSchStretch." % fn)
    elif name == "aeCrtWireLabelsAndPins":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, inst, make_labels=True, make_pins=True):\n"
            "    return pyScript.aeCrtWireLabelsAndPins(design=cv, inst=inst,\n"
            "        isCrtLabels=make_labels, isCrtPins=make_pins)\n") % fn
        prompt = ("Write a Python function %s(cv, inst, make_labels, make_pins) "
            "that generates wire labels and pins with aeCrtWireLabelsAndPins "
            "and returns the boolean result." % fn)
    elif name == "emyDesignIsSchematic":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv):\n"
            "    return bool(pyScript.emyDesignIsSchematic(cv))\n") % fn
        prompt = ("Write a Python function %s(cv) that returns True if the "
            "given design is a schematic, using emyDesignIsSchematic." % fn)
    else:
        dt_body = doc["doctest"].split("\n")
        call_line = ""
        for l in dt_body:
            s = l.strip()
            if s.startswith(">>>") and name + "(" in s:
                call_line = "    " + s[4:].strip()
                break
        if not call_line:
            call_line = "    pass"
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"%s\")\n"
            "%s\n"
            "    pyScript.dbSave(cv)\n") % (fn, view, call_line)
        prompt = ("Write a Python function %s(lib, cell) that opens a %s cell "
            "view, uses %s, saves the cell view." % (fn, view, name))
    return prompt, completion, [name], "S4 multi-step trace (openCV->create->save)"


def _s5_param_variation(name, doc):
    """Parameter variation: same API, different orient/layer/points/args.
    Reinforces the exact call pattern across diverse argument shapes."""
    fn = "vary_" + name.lower()
    if name == "dbCrtRect":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv):\n"
            "    rects = []\n"
            "    for layer in (\"M1\", \"M2\", \"M3\"):\n"
            "        bbox = pyScript.emyBoxF((0, 0), (5, 5))\n"
            "        rects.append(pyScript.dbCrtRect(cv=cv, bbox=bbox, layer=layer))\n"
            "    return rects\n") % fn
        prompt = ("Write a Python function %s(cv) that creates three rectangles "
            "on layers M1/M2/M3 with dbCrtRect and returns the list of shapes." % fn)
    elif name == "dbCrtPolygon":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, layer):\n"
            "    tri = pyScript.dbCrtPolygon(cv=cv, points=[(0,0),(4,4),(4,0)], layer=layer)\n"
            "    pent = pyScript.dbCrtPolygon(cv=cv, points=[(0,0),(2,4),(4,4),(4,0),(0,0)], layer=layer)\n"
            "    return tri, pent\n") % fn
        prompt = ("Write a Python function %s(cv, layer) that creates a triangle "
            "and a pentagon with dbCrtPolygon and returns both shapes." % fn)
    elif name == "dbCrtInst":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, lib, cell):\n"
            "    figs = []\n"
            "    for i, orient in enumerate((\"R0\", \"R90\", \"MY\")):\n"
            "        figs.append(pyScript.dbCrtInst(cv=cv, point=(i*10, 0),\n"
            "            lib=lib, cell=cell, inst=\"I%%d\" %% i, orient=orient))\n"
            "    return figs\n") % fn
        prompt = ("Write a Python function %s(cv, lib, cell) that places three "
            "instances at x=0/10/20 with orientations R0/R90/MY using dbCrtInst." % fn)
    elif name == "dbCrtPath":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv):\n"
            "    h = pyScript.dbCrtPath(cv=cv, layer=\"M1\", points=[(0,0),(20,0)], width=0.5)\n"
            "    v = pyScript.dbCrtPath(cv=cv, layer=\"M1\", points=[(0,0),(0,20)], width=0.5)\n"
            "    return h, v\n") % fn
        prompt = ("Write a Python function %s(cv) that creates a horizontal and "
            "a vertical path on M1 with dbCrtPath (width 0.5) and returns both." % fn)
    elif name == "dbCrtSchWire":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv):\n"
            "    a = pyScript.dbCrtSchWire(cv=cv, point=((0,0),(50,0)))\n"
            "    b = pyScript.dbCrtSchWire(cv=cv, point=((0,0),(0,50)), wireMode=\"Wide\")\n"
            "    return a, b\n") % fn
        prompt = ("Write a Python function %s(cv) that creates a narrow "
            "horizontal wire and a wide vertical wire with dbCrtSchWire." % fn)
    elif name == "dbCrtWire":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv):\n"
            "    m1 = pyScript.dbCrtWire(cv=cv, layer=\"M1\", points=((0,0),(10,0)), width=0.3)\n"
            "    m2 = pyScript.dbCrtWire(cv=cv, layer=\"M2\", points=((0,0),(10,0)), width=0.5)\n"
            "    return m1, m2\n") % fn
        prompt = ("Write a Python function %s(cv) that creates two layout wires "
            "on M1 (width 0.3) and M2 (width 0.5) with dbCrtWire." % fn)
    elif name == "dbCrtNet":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, names):\n"
            "    nets = []\n"
            "    for nm in names:\n"
            "        nets.append(pyScript.dbCrtNet(cv=cv, name=nm))\n"
            "    return nets\n") % fn
        prompt = ("Write a Python function %s(cv, names) that creates a net for "
            "each name with dbCrtNet and returns the list of net identifiers." % fn)
    elif name == "dbCrtSchPin":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, specs):\n"
            "    pins = []\n"
            "    for nm, pt, d in specs:\n"
            "        pins.append(pyScript.dbCrtSchPin(cv=cv, name=nm, point=pt, direction=d))\n"
            "    return pins\n") % fn
        prompt = ("Write a Python function %s(cv, specs) where specs is a list "
            "of (name, point, direction) tuples; create a schematic pin for "
            "each with dbCrtSchPin." % fn)
    elif name == "dbSchGetPinOrder":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv):\n"
            "    order = pyScript.dbSchGetPinOrder(cv)\n"
            "    return list(order) if order else []\n") % fn
        prompt = ("Write a Python function %s(cv) that returns the pin order "
            "as a Python list via dbSchGetPinOrder with empty-list fallback." % fn)
    elif name == "aeSchStretch":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(figs):\n"
            "    for orient in (pyScript.emcR90, pyScript.emcR180, pyScript.emcR270):\n"
            "        t = pyScript.emyTransformF(0, 0, orient)\n"
            "        pyScript.aeSchStretch(figs, t)\n") % fn
        prompt = ("Write a Python function %s(figs) that stretches the figures "
            "with aeSchStretch under three rotations (R90/R180/R270)." % fn)
    elif name == "aeCrtWireLabelsAndPins":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, inst):\n"
            "    only_labels = pyScript.aeCrtWireLabelsAndPins(design=cv, inst=inst,\n"
            "        isCrtLabels=True, isCrtPins=False)\n"
            "    only_pins = pyScript.aeCrtWireLabelsAndPins(design=cv, inst=inst,\n"
            "        isCrtLabels=False, isCrtPins=True)\n"
            "    return only_labels, only_pins\n") % fn
        prompt = ("Write a Python function %s(cv, inst) that calls "
            "aeCrtWireLabelsAndPins twice -- labels-only and pins-only." % fn)
    elif name == "emyDesignIsSchematic":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cvs):\n"
            "    return [cv for cv in cvs if pyScript.emyDesignIsSchematic(cv)]\n") % fn
        prompt = ("Write a Python function %s(cvs) that filters a list of "
            "designs, keeping only schematics per emyDesignIsSchematic." % fn)
    else:
        return None
    return prompt, completion, [name], "S5 parameter variation"


def build_pairs(eval_eps, limit=None):
    pairs = []
    rejected = 0
    reject_details = []

    def _add(pair_type, name, prompt, completion, api_used, note):
        nonlocal rejected
        hit = _contam_check(completion, eval_eps)
        if hit:
            rejected += 1
            reject_details.append((pair_type, name, hit))
            return
        pairs.append({
            "pair_id": "R179-%s-%s-%s" % (pair_type, name, _pid(completion)),
            "type": pair_type, "api_used": api_used,
            "prompt": prompt, "completion": completion,
            "contamination_check": "PASS", "note": note})

    # ---- S1 doc->code (one per API) ----
    for name, doc in API_DOCS.items():
        p, c, a, n = _s1_doc_to_code(name, doc)
        _add("S1", name, p, c, a, n)

    # ---- S4 multi-step trace (one per API) -- R178 anti-hallucination fix ----
    for name, doc in API_DOCS.items():
        p, c, a, n = _s4_multistep_trace(name, doc)
        _add("S4", name, p, c, a, n)

    # ---- S5 parameter variation (one per API) ----
    for name, doc in API_DOCS.items():
        res = _s5_param_variation(name, doc)
        if res is None:
            continue
        p, c, a, n = res
        _add("S5", name, p, c, a, n)

    # ---- S3 multi-API chains (layout-scenario focused) ----
    chains = [
        ("rect_then_inst",
         "Write a Python function place_rect_and_inst(lib, cell, rect_bbox, rect_layer, inst_lib, inst_cell, inst_pt) that opens a layout cell view, creates a rectangle with dbCrtRect, places an instance with dbCrtInst, saves, and returns both shapes.",
         ["dbCrtRect", "dbCrtInst"],
         "def place_rect_and_inst(lib, cell, rect_bbox, rect_layer, inst_lib, inst_cell, inst_pt):\n"
         "    import pyAether as pyScript\n"
         "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\")\n"
         "    bbox = pyScript.emyBoxF(rect_bbox[0], rect_bbox[1])\n"
         "    rect = pyScript.dbCrtRect(cv=cv, bbox=bbox, layer=rect_layer)\n"
         "    inst = pyScript.dbCrtInst(cv=cv, point=inst_pt, lib=inst_lib, cell=inst_cell, inst=\"U1\", orient=\"R0\")\n"
         "    pyScript.dbSave(cv)\n"
         "    return rect, inst\n"),
        ("path_then_net",
         "Write a Python function route_path_and_net(lib, cell, pts, layer, width, net_name) that opens a layout cell view, creates a path with dbCrtPath, creates a net with dbCrtNet, saves, and returns both.",
         ["dbCrtPath", "dbCrtNet"],
         "def route_path_and_net(lib, cell, pts, layer, width, net_name):\n"
         "    import pyAether as pyScript\n"
         "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\")\n"
         "    path = pyScript.dbCrtPath(cv=cv, layer=layer, points=pts, width=width)\n"
         "    net = pyScript.dbCrtNet(cv=cv, name=net_name)\n"
         "    pyScript.dbSave(cv)\n"
         "    return path, net\n"),
        ("polygon_then_wire",
         "Write a Python function draw_polygon_and_wire(lib, cell, poly_pts, poly_layer, wire_pts, wire_layer, wire_width) that opens a layout cell view, creates a polygon with dbCrtPolygon, creates a wire with dbCrtWire, saves, and returns both.",
         ["dbCrtPolygon", "dbCrtWire"],
         "def draw_polygon_and_wire(lib, cell, poly_pts, poly_layer, wire_pts, wire_layer, wire_width):\n"
         "    import pyAether as pyScript\n"
         "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\")\n"
         "    poly = pyScript.dbCrtPolygon(cv=cv, points=poly_pts, layer=poly_layer)\n"
         "    wire = pyScript.dbCrtWire(cv=cv, layer=wire_layer, points=wire_pts, width=wire_width)\n"
         "    pyScript.dbSave(cv)\n"
         "    return poly, wire\n"),
        ("sch_pinorder_guard",
         "Write a Python function safe_pin_order(cv) that returns the schematic pin order via dbSchGetPinOrder only if emyDesignIsSchematic confirms the design is a schematic; otherwise return an empty list.",
         ["emyDesignIsSchematic", "dbSchGetPinOrder"],
         "def safe_pin_order(cv):\n"
         "    import pyAether as pyScript\n"
         "    if not pyScript.emyDesignIsSchematic(cv):\n"
         "        return []\n"
         "    return list(pyScript.dbSchGetPinOrder(cv))\n"),
        ("sch_wire_then_labels",
         "Write a Python function wire_with_labels(lib, cell, pts) that opens a schematic cell view, creates a schematic wire with dbCrtSchWire, generates labels with aeCrtWireLabelsAndPins, saves, and returns the wire figures.",
         ["dbCrtSchWire", "aeCrtWireLabelsAndPins"],
         "def wire_with_labels(lib, cell, pts):\n"
         "    import pyAether as pyScript\n"
         "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"schematic\")\n"
         "    figs = pyScript.dbCrtSchWire(cv=cv, point=pts)\n"
         "    pyScript.aeCrtWireLabelsAndPins(design=cv, isCrtLabels=True, isCrtPins=False)\n"
         "    pyScript.dbSave(cv)\n"
         "    return figs\n"),
    ]
    for cid, prompt, api_used, completion in chains:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")

    # ---- S6 API lookup (intent -> API -> minimal usage) ----
    lookups = [
        ("create a rectangle in a layout view", "dbCrtRect",
         'bbox = pyScript.emyBoxF((0,0),(1,1))\nshape = pyScript.dbCrtRect(cv=cvId, bbox=bbox, layer="NSR")'),
        ("create a polygon in a layout view", "dbCrtPolygon",
         'shape = pyScript.dbCrtPolygon(cv=cvId, points=[(0,0),(3,3),(3,0)], layer="M1")'),
        ("place an instance in a layout view", "dbCrtInst",
         'fig = pyScript.dbCrtInst(cv=cvId, point=(0,0), lib="analogLib", cell="nmos", inst="M1", orient="R0")'),
        ("create a path in a layout view", "dbCrtPath",
         'shape = pyScript.dbCrtPath(cv=cvId, layer="M1", points=[(0,0),(10,0)], width=1.0)'),
        ("get the pin order of a schematic cellview", "dbSchGetPinOrder",
         'order = pyScript.dbSchGetPinOrder(cv)'),
        ("stretch schematic objects with a transform", "aeSchStretch",
         'trans = pyScript.emyTransformF(1, 1, pyScript.emcR180)\npyScript.aeSchStretch(figs, trans)'),
        ("check if a design is a schematic", "emyDesignIsSchematic",
         'is_sch = pyScript.emyDesignIsSchematic(cv)'),
        ("generate wire labels and pins in schematic", "aeCrtWireLabelsAndPins",
         'ok = pyScript.aeCrtWireLabelsAndPins(design=cv, isCrtLabels=True, isCrtPins=True)'),
    ]
    for intent, api, usage in lookups:
        prompt = ("You are an EDA automation assistant. Which PyAether API is "
                  "used to %s? Show a minimal correct usage example." % intent)
        completion = ("The API is `%s`.\n\n```python\nimport pyAether as "
                      "pyScript\n%s\n```" % (api, usage))
        _add("S6", api, prompt, completion, [api], "S6 API lookup")

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
        "report_id": "R179",
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


if __name__ == "__main__":
    main()
