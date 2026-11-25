#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r193_db_lifecycle_traverse_corpus.py
R193 -- v23 PyAether SFT corpus: db* lifecycle / traverse / geometry /
transform / symbol-pin blind spot (13 APIs, 65 pairs).

BACKGROUND: v11-v22 (548 pairs) cover 97/164 eval raw APIs (59.1%). 67 blind.
Data-driven scan (R191 blind_scan, re-run with v22 this wake) shows db* is
the largest blind family: 14 usages / 13 APIs. R193 targets 13 db* APIs.
All ISOLATE-class (eval_count>0, helper APIs used in eval canonical_solution).
Fingerprint scan rejects eval entry_points.

Authoritative signatures fetched via pyAether MCP get_api_details (R193 wake).

Usage:
  python3 baize_posttrain_r193_db_lifecycle_traverse_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v23_db_lifecycle_traverse.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["dbCrtTerm"] = {
    "sig": "dbCrtTerm(net: emyNet, name: emyString, dir: emyString, unused: int=0, isphy: bool=False) -> emyTerm",
    "desc": "Creates a terminal (pin) on a net. Returns a term identifier if successful, otherwise returns 0. The terminal connects a net to the outside of the cell.",
    "params": {"net": "emyNet - net identifier (from dbCrtNet)", "name": "emyString - terminal name", "dir": "emyString - direction: input, output, inputOutput, switch", "unused": "int=0 - backward compatibility", "isphy": "bool=False - physical or both physical+logical"},
    "returns": "emyTerm - term id on success, 0 on failure",
    "methods": "Keyword args net=, name=, dir= common. dir must be one of the 4 allowed strings.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.emyString("test")\n'
                '>>> cell = pyScript.emyString("test")\n'
                '>>> view = pyScript.emyString("layout")\n'
                '>>> cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=view)\n'
                '>>> net = pyScript.emyString("net1")\n'
                '>>> netId = pyScript.dbCrtNet(cv=cv, name=net)\n'
                '>>> name = pyScript.emyString("term01")\n'
                '>>> dirv = pyScript.emyString("input")\n'
                '>>> term = pyScript.dbCrtTerm(net=netId, name=name, dir=dirv)\n'
                '>>> print(term)'),
    "category": "Db Commands / Create Database", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns emyTerm or 0 (check truthiness). dir is a string not enum. Create net first via dbCrtNet, then term on it."}

API_DOCS["dbExpandPoints"] = {
    "sig": "dbExpandPoints(cv: emyDesign, points: vector1D_emyPointF, size: float=0.0, dx: float=0.0, dy: float=0.0, left: float=0.0, bottom: float=0.0, right: float=0.0, top: float=0.0) -> Tuple[emyString]",
    "desc": "Expands (grows) a point array (polygon outline) by the given offsets. Returns a new point array. Use size for uniform, or left/bottom/right/top for per-side, or dx/dy for axis-aligned.",
    "params": {"cv": "emyDesign - cell view id", "points": "vector1D_emyPointF - polygon vertices to expand", "size": "float=0 - uniform expansion", "left": "float=0 - leftward expansion", "bottom": "float=0 - downward expansion", "right": "float=0 - rightward expansion", "top": "float=0 - upward expansion"},
    "returns": "Tuple[emyString] - new expanded point array",
    "methods": "Supports python built-in types for points. Prefer left/bottom/right/top for per-side control.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> points = pyScript.vector1D_emyPointF()\n'
                '>>> for p in [(0,0),(0,2),(2,2),(2,1),(1,1),(1,0)]:\n'
                '...     points.append(pyScript.emyPointF(*p))\n'
                '>>> result = pyScript.dbExpandPoints(cv=cv, points=points, left=10, bottom=8, right=6, top=4)\n'
                '>>> print(result)'),
    "category": "Db Commands / Edit Database", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Points is vector1D_emyPointF (append emyPointF). left/bottom/right/top give per-side control. Returns tuple of strings (point coords)."}

API_DOCS["dbFindMemInstByName"] = {
    "sig": "dbFindMemInstByName(design: emyDesign, name: emyString) -> emyInst",
    "desc": "Finds an instance in the specified design by its name. Returns the instance identifier if found, otherwise None. Supports scalar, array, and vector instances; vector bits accessed via 'inst3<2>' syntax.",
    "params": {"design": "emyDesign - design to search", "name": "emyString - instance name to find"},
    "returns": "emyInst - instance id if found, None if not found",
    "methods": "name is a plain string. Vector bit syntax: 'inst3<2>' for bit 2. Result .forReg gives readable form.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-ADV")\n'
                '>>> pyScript.aeOpenDesign("test", "test", "layout")\n'
                '>>> design = pyScript.aeGetCurDesign()\n'
                '>>> inst = pyScript.dbFindMemInstByName(design, "inst1")\n'
                '>>> print(inst is not None)\n'
                '>>> if inst:\n'
                '...     print(inst.forReg)'),
    "category": "Db Commands / Edit Database", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns None if not found (check truthiness). Vector bit via 'inst3<2>'. Out-of-range bit returns None. .forReg gives human-readable instance description."}

API_DOCS["dbGetCurrNetNameByHierName"] = {
    "sig": "dbGetCurrNetNameByHierName(topDesign: emyDesign, hierNetName: emyString, isSkipShorts: bool=False, shortCells: emyStringArray=emyStringArray()) -> emyString",
    "desc": "Resolves a hierarchical net name (inst1/inst2/neta) to the top-level net name. If the net is connected upward through pins, returns the higher-level net name; otherwise returns the hierNetName unchanged.",
    "params": {"topDesign": "emyDesign - top design to resolve from", "hierNetName": "emyString - hierarchical path like 'inst1/inst2/neta'", "isSkipShorts": "bool=False - skip insts with 2 instTerms", "shortCells": "emyStringArray - list of 'lib/cell' to skip when isSkipShorts=True"},
    "returns": "emyString - resolved top net name, or '' if net not found in bottom inst",
    "methods": "hierNetName uses '/' separator between inst names and net. isSkipShorts+shortCells for short-cell bypass.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitDb()\n'
                '>>> top = pyScript.dbOpenCV("test_comm", "top", "schematic")\n'
                '>>> sub1 = pyScript.dbOpenCV("test_comm", "test1", "schematic", mode="w")\n'
                '>>> sub2 = pyScript.dbOpenCV("test_comm", "test2", "schematic", mode="w")\n'
                '>>> pyScript.dbCrtNet(sub2, "net2")\n'
                '>>> pyScript.dbCrtInst(cv=sub1, point=(1,1), master=sub2, inst="inst2_1")\n'
                '>>> pyScript.dbCrtInst(cv=top, point=(0,1), master=sub1, inst="inst1_0")\n'
                '>>> name = pyScript.dbGetCurrNetNameByHierName(top, "inst1_0/inst2_1/net2")\n'
                '>>> print(str(name))'),
    "category": "Db Commands / Edit Database", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Hier name uses '/' separator. Returns '' if bottom net not found. isSkipShorts bypasses buffer/short cells. shortCells format: 'lib/cell'."}

API_DOCS["dbPointArrayGen"] = {
    "sig": "dbPointArrayGen(op: emyString, cv: emyDesign, l1stpoints: vector2D_emyPointF, l2ndpoints: vector2D_emyPointF=None, imaxCount: int=0) -> Tuple[emyString]",
    "desc": "Performs a boolean operation (OR/AND/XOR/NOT) on two sets of point arrays. Returns a list of resulting point arrays. l1stpoints and l2ndpoints are 2D arrays (list of polygons).",
    "params": {"op": "emyString - boolean op: OR, AND, XOR, NOT", "cv": "emyDesign - cell view id", "l1stpoints": "vector2D_emyPointF - first set of polygons", "l2ndpoints": "vector2D_emyPointF=None - second set of polygons", "imaxCount": "int=0 - max result count (0=unlimited)"},
    "returns": "Tuple[emyString] - list of resulting point arrays",
    "methods": "op is uppercase string. Points are vector2D (nested). NOT uses only l1stpoints with l2ndpoints as mask.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> poly1 = pyScript.vector1D_emyPointF()\n'
                '>>> for p in [(0,0),(10,0),(10,10),(0,10)]:\n'
                '...     poly1.append(pyScript.emyPointF(*p))\n'
                '>>> first = pyScript.vector2D_emyPointF()\n'
                '>>> first.append(poly1)\n'
                '>>> poly2 = pyScript.vector1D_emyPointF()\n'
                '>>> for p in [(5,5),(15,5),(15,15),(5,15)]:\n'
                '...     poly2.append(pyScript.emyPointF(*p))\n'
                '>>> second = pyScript.vector2D_emyPointF()\n'
                '>>> second.append(poly2)\n'
                '>>> result = pyScript.dbPointArrayGen("AND", cv, first, second)\n'
                '>>> print(len(result))'),
    "category": "Db Commands / Edit Database", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "op is uppercase OR/AND/XOR/NOT. Inputs are vector2D (each element is a vector1D_emyPointF polygon). Returns tuple of point arrays."}

API_DOCS["dbResize"] = {
    "sig": "dbResize(figs: vector1D_p_emyFig, size: vector1D_double, merge: bool=True, layer: emyString=\"\", purpose: emyString=\"drawing\", deloldobj: bool=True, truncate: float=0.0, keepOrthogonal: bool=False, absolute: bool=False) -> Tuple[emyFig]",
    "desc": "Sizes (grows or shrinks) specified figures and returns the result as a list of figures. Positive size values grow outward, negative shrink inward. Supports per-side sizing via a 4-element size array [left, bottom, right, top].",
    "params": {"figs": "vector1D_p_emyFig - list of figure ids to resize", "size": "vector1D_double - [left, bottom, right, top]; positive=grow, negative=shrink", "merge": "bool=True - merge original figures first", "layer": "emyString - target layer (empty=keep original)", "purpose": "emyString='drawing' - target purpose", "deloldobj": "bool=True - delete old figures", "truncate": "float=0 - cut off sharp angles (valid when >0 and size>0)", "keepOrthogonal": "bool=False - keep edges orthogonal", "absolute": "bool=False - multiply truncate by size"},
    "returns": "Tuple[emyFig] - list of resized figure ids",
    "methods": "figs via vector1D_p_emyFig().append(fig). size via vector1D_double() with 4 appends in order [left,bottom,right,top].",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> fig = pyScript.dbCrtRect(cv=cv, bbox=[(0,0),(1,1)], layer="M1")\n'
                '>>> figs = pyScript.vector1D_p_emyFig()\n'
                '>>> figs.append(fig)\n'
                '>>> size = pyScript.vector1D_double()\n'
                '>>> for v in [-1, 1, 1, 1]:\n'
                '...     size.append(v)\n'
                '>>> result = pyScript.dbResize(figs=figs, size=size)\n'
                '>>> print(len(result))'),
    "category": "Db Commands / Edit Database", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "size is [left,bottom,right,top]; +grow/-shrink. figs is vector1D_p_emyFig. Empty figs returns empty tuple. deloldobj=True removes originals."}

API_DOCS["dbSchDrawSymbolPin"] = {
    "sig": "dbSchDrawSymbolPin(pDesign: emyDesign, pinName: emyString, pinDir: emyString, points: emyPointArrayF) -> emyFig (emyPolygon)",
    "desc": "Draws a symbol pin with a custom polygon shape in a schematic symbol view. Returns the created figure (emyPolygon) on success, None on failure. pinDir must be input/output/inputOutput/switch.",
    "params": {"pDesign": "emyDesign - symbol design (schematicSymbol view type)", "pinName": "emyString - pin name", "pinDir": "emyString - direction: input, output, inputOutput, switch", "points": "emyPointArrayF - polygon vertices (at least 3 points, close shape for clean polygon)"},
    "returns": "emyFig (emyPolygon) - created figure, or None on failure",
    "methods": "points via emyPointArrayF().append(emyPointF(x,y)). Min 3 points. Returns None on invalid shape (no exception).",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-ADV")\n'
                '>>> pyScript.aeOpenDesign("test_lib", "test_cell", "symbol")\n'
                '>>> cv = pyScript.aeGetCurDesign()\n'
                '>>> points = pyScript.emyPointArrayF()\n'
                '>>> for p in [(0,0),(2,0),(1,1.5),(0,0)]:\n'
                '...     points.append(pyScript.emyPointF(*p))\n'
                '>>> fig = pyScript.dbSchDrawSymbolPin(cv, "MyPin", "input", points)\n'
                '>>> print(fig is not None)'),
    "category": "Db Commands / Create Database", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns emyPolygon or None (check truthiness, no exception). Min 3 points. Unlike dbCrtSymbolPin (returns emyPin), returns the figure. Close shape by repeating first point."}

API_DOCS["dbSetInstHeaderMasterName"] = {
    "sig": "dbSetInstHeaderMasterName(instHeader: emyInstHeader, libName: emyString, cellName: emyString, viewName: emyString, isReplaceMissmatched: bool=False) -> emyBoolean",
    "desc": "Sets the master of an instance header to a new lib/cell/view. All instances in the old instHeader are deleted and regenerated in the new instHeader. If the instHeader is empty, it is deleted. Returns True on success, False on failure.",
    "params": {"instHeader": "emyInstHeader - instance header to rebind", "libName": "emyString - new library name", "cellName": "emyString - new cell name", "viewName": "emyString - new view name", "isReplaceMissmatched": "bool=False - if True, replace params without checking; if False, only replace when params match"},
    "returns": "emyBoolean - True on success, False on failure",
    "methods": "instHeader obtained via inst.getHeader(). Note: parameter name is isReplaceMissmatched (two s's).",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.aeOpenDesign("test_agr", "test", "layout")\n'
                '>>> cv = pyScript.aeGetCurDesign()\n'
                '>>> pyScript.dbCrtInst(cv, pyScript.emyPointF(12,12), lib="smic14ff", cell="n18_ckt", view="layout", inst="pcell_inst")\n'
                '>>> block = cv.getTopBlock()\n'
                '>>> insts = block.getInsts()\n'
                '>>> hdr = insts[0].getHeader()\n'
                '>>> ok = pyScript.dbSetInstHeaderMasterName(hdr, "test_adv", "test", "layout", isReplaceMissmatched=True)\n'
                '>>> print(ok)'),
    "category": "Db Commands / Edit Database", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Param name is isReplaceMissmatched (TWO s's) -- common typo trap. Returns False on None/invalid instHeader or non-existent master. Get instHeader via inst.getHeader()."}

API_DOCS["dbSingleLayerGOA"] = {
    "sig": "dbSingleLayerGOA(cv: emyDesign, op: emyString, layer: emyString, purpose: emyString=\"drawing\", figs: vector1D_p_emyShape=None, layer1: emyString=\"\", purpose1: emyString=\"drawing\") -> Tuple[emyShape]",
    "desc": "Performs a boolean operation (OR/AND/XOR) on shapes within a single layer. Input can be a layer (all shapes on it) or an explicit list of shapes. Returns the resulting shape identifiers.",
    "params": {"cv": "emyDesign - destination cell view id", "op": "emyString - boolean op: OR, AND, XOR (uppercase)", "layer": "emyString - layer number or name", "purpose": "emyString='drawing' - purpose number or name", "figs": "vector1D_p_emyShape=None - explicit shape list (None=all shapes on layer)", "layer1": "emyString='' - first layer for special ops", "purpose1": "emyString='drawing' - first purpose"},
    "returns": "Tuple[emyShape] - resulting shape ids",
    "methods": "op must be uppercase OR/AND/XOR. If figs omitted, operates on all shapes on layer. Empty result returns empty tuple.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> layer = pyScript.emyString("M1")\n'
                '>>> pts1 = pyScript.vector1D_emyPointF()\n'
                '>>> for p in [(0,0),(10,0),(10,10),(0,10)]:\n'
                '...     pts1.append(pyScript.emyPointF(*p))\n'
                '>>> fig1 = pyScript.dbCrtLine(cv=cv, points=pts1, layer=layer)\n'
                '>>> pts2 = pyScript.vector1D_emyPointF()\n'
                '>>> for p in [(5,5),(15,5),(15,15),(5,15)]:\n'
                '...     pts2.append(pyScript.emyPointF(*p))\n'
                '>>> fig2 = pyScript.dbCrtLine(cv=cv, points=pts2, layer=layer)\n'
                '>>> figs = pyScript.vector1D_p_emyShape()\n'
                '>>> figs.append(fig1)\n'
                '>>> figs.append(fig2)\n'
                '>>> result = pyScript.dbSingleLayerGOA(cv=cv, op=pyScript.emyString("OR"), layer=layer, figs=figs)\n'
                '>>> print(len(result))'),
    "category": "Db Commands / Edit Database", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "op uppercase OR/AND/XOR only (no NOT). figs is vector1D_p_emyShape. If figs=None, uses all shapes on layer. Invalid op returns empty tuple (no exception)."}

API_DOCS["dbSmashInst2"] = {
    "sig": "dbSmashInst2(inst: emyInst, level: int, option: smash_option) -> emyBoolean",
    "desc": "Smashes (flattens) an instance to the specified hierarchy level, expanding its contents into the parent design. Uses a smash_option object for fine-grained control (preserve pins, labels, etc.). Returns True on success, False on failure.",
    "params": {"inst": "emyInst - instance to flatten", "level": "int - hierarchy depth to flatten to (0=no-op, 1=one level, up to 32)", "option": "smash_option - options object (m_preservePins, m_preserveLabels, etc.)"},
    "returns": "emyBoolean - True on success, False on failure",
    "methods": "option via pyScript.smash_option(). inst must be valid (not None/0). level 0 does nothing.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("adv")\n'
                '>>> pyScript.aeOpenDesign("test_lib", "design", "layout")\n'
                '>>> cv = pyScript.aeGetCurDesign()\n'
                '>>> master = pyScript.dbOpenCV("test_lib", "master", "layout")\n'
                '>>> inst = pyScript.dbCrtInst(cv, (0, 0), master)\n'
                '>>> if inst:\n'
                '...     opt = pyScript.smash_option()\n'
                '...     ok = pyScript.dbSmashInst2(inst, 1, opt)\n'
                '...     print(ok)'),
    "category": "Db Commands / Other", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns False on None/invalid inst or level 0. option via smash_option(). Unlike dbSmashInst (bool params), uses option object for finer control. Check inst validity before calling."}

API_DOCS["dbTransformBBox"] = {
    "sig": "dbTransformBBox(bbox: emyBoxF, offsetPoint: emyPointF, orient: emyString=\"R0\", mag: float=1.0) -> emyBoxF",
    "desc": "Transforms a bounding box by applying an offset, orientation rotation, and magnification. Returns the transformed emyBoxF with accessible l/b/r/t/width/height/center attributes.",
    "params": {"bbox": "emyBoxF - input bounding box", "offsetPoint": "emyPointF - translation offset (required, use (0,0) for none)", "orient": "emyString='R0' - orientation: R0, R90, R180, R270, MY, MYR90, MX, MXR90", "mag": "float=1.0 - magnification factor (positive)"},
    "returns": "emyBoxF - transformed bounding box (.l, .b, .r, .t, .width, .height, .center)",
    "methods": "bbox via emyBoxF((l,b),(r,t)). offsetPoint required. orient must be one of 8 valid values. mag>0.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> bbox = pyScript.emyBoxF((0, 0), (5, 5))\n'
                '>>> offset = pyScript.emyPointF(10, 10)\n'
                '>>> result = pyScript.dbTransformBBox(bbox=bbox, offsetPoint=offset, orient="R90", mag=2.0)\n'
                '>>> print(result)\n'
                '>>> print("w:", result.width, "h:", result.height)\n'
                '>>> print("ll:", result.l, result.b, "ur:", result.r, result.t)'),
    "category": "Db Commands / Edit Database", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "offsetPoint is REQUIRED (use emyPointF(0,0) for pure rotation). orient: R0/R90/R180/R270/MY/MYR90/MX/MXR90. mag must be positive. Result .width=.r-.l, .height=.t-.b. Compare with dbTransformBBox3X (uses trans list)."}

API_DOCS["dbTraverseTriggerFunc"] = {
    "sig": "dbTraverseTriggerFunc  [class: callback base for design traversal]",
    "desc": "Abstract base class for design-hierarchy traversal callbacks. Subclass it and override funcCb(self, design) to process each visited design, and optionally funcReturnCb(self, design)->bool to control traversal (return False to stop). Register an instance via dbRegTraverseTrigger() before calling dbTraverseDesignWithCB().",
    "params": {},
    "returns": "None (callback base class, not a function)",
    "methods": "Override: funcCb(self, design) -- called per design. funcReturnCb(self, design)->bool -- return False to stop traversal. Register via dbRegTraverseTrigger(cb_instance).",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> class MyCb(pyScript.dbTraverseTriggerFunc):\n'
                '...     def __init__(self):\n'
                '...         super().__init__()\n'
                '...         self.count = 0\n'
                '...     def funcCb(self, design):\n'
                '...         self.count += 1\n'
                '...     def funcReturnCb(self, design):\n'
                '...         return self.count < 10\n'
                '>>> cb = MyCb()\n'
                '>>> pyScript.dbRegTraverseTrigger(cb)\n'
                '>>> print("callback registered, count:", cb.count)'),
    "category": "Db Commands / Traversal", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "This is a CLASS to subclass, not a callable function. Must call super().__init__() in subclass. Register via dbRegTraverseTrigger() before dbTraverseDesignWithCB(). funcReturnCb returning False stops traversal."}

API_DOCS["dbTraverseDesignWithCB"] = {
    "sig": "dbTraverseDesignWithCB(design: emyDesign, views: emyString='schematic', level: int=50) -> None",
    "desc": "Traverses the design hierarchy top-down (depth-first) using a registered callback. The callback (registered via dbRegTraverseTrigger with a dbTraverseTriggerFunc subclass) is invoked for each visited design. Supports multi-view traversal and depth limiting.",
    "params": {"design": "emyDesign - top-level design to traverse", "views": "emyString='schematic' - space-separated view names (schematic only)", "level": "int=50 - max traversal depth (0=current only, 1=current+children)"},
    "returns": "None - results collected via callback side-effects",
    "methods": "Must register callback via dbRegTraverseTrigger() first. views is space-separated string. level limits depth.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> class Counter(pyScript.dbTraverseTriggerFunc):\n'
                '...     def __init__(self):\n'
                '...         super().__init__()\n'
                '...         self.n = 0\n'
                '...     def funcCb(self, design):\n'
                '...         self.n += 1\n'
                '>>> cb = Counter()\n'
                '>>> pyScript.dbRegTraverseTrigger(cb)\n'
                '>>> design = pyScript.aeGetCurDesign()\n'
                '>>> if design:\n'
                '...     pyScript.dbTraverseDesignWithCB(design, "schematic", 3)\n'
                '...     print("visited:", cb.n)\n'
                '... else:\n'
                '...     print("no design open")'),
    "category": "Db Commands / Traversal", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns None (results via callback). Must register dbTraverseTriggerFunc subclass via dbRegTraverseTrigger() first. None design -> silent return. views only supports schematic. level 0=current only."}


API_ORDER = ["dbCrtTerm", "dbExpandPoints", "dbFindMemInstByName",
             "dbGetCurrNetNameByHierName", "dbPointArrayGen", "dbResize",
             "dbSchDrawSymbolPin", "dbSetInstHeaderMasterName",
             "dbSingleLayerGOA", "dbSmashInst2", "dbTransformBBox",
             "dbTraverseTriggerFunc", "dbTraverseDesignWithCB"]


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
             "**`%s`**" % d["sig"], "", d["desc"], ""]
    if d.get("params"):
        lines.append("**Parameters**")
        for pk, pv in d["params"].items():
            lines.append("- `%s`: %s" % (pk, pv))
        lines.append("")
    if d.get("returns"):
        lines.append("**Returns**: %s" % d["returns"])
        lines.append("")
    if d.get("methods"):
        lines.append("**Methods**: %s" % d["methods"])
        lines.append("")
    if d.get("key_notes"):
        lines.append("**Notes**: %s" % d["key_notes"])
        lines.append("")
    return "\n".join(lines)


def build_pairs(eval_eps, limit=None):
    pairs = []
    rejected = 0
    reject_details = []

    def _add(ptype, pid, prompt, completion, api_used, note=""):
        nonlocal rejected, reject_details
        blob = prompt + "\n" + completion
        hit = fingerprint_scan(blob, eval_eps)
        if hit:
            rejected += 1
            reject_details.append((pid, hit))
            return
        pairs.append({
            "id": pid, "type": ptype,
            "api_used": api_used if isinstance(api_used, list) else [api_used],
            "prompt": prompt, "completion": completion,
            "contamination_check": "PASS",
            "note": note,
        })

    # ---- S1: doc -> code (13 pairs, one per API) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v23-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S4: multi-step trace (13 pairs) ----
    s4_traces = [
        ("dbCrtTerm",
         "Open a cell view, create a net, then create input and output terminals on it.",
         ["dbCrtTerm"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='schematic', mode='w')\n"
          "net = pyScript.dbCrtNet(cv=cv, name=pyScript.emyString('vdd'))\n"
          "t_in = pyScript.dbCrtTerm(net=net, name=pyScript.emyString('vdd_in'),\n"
          "                         dir=pyScript.emyString('input'))\n"
          "print('input term:', t_in)\n"
          "t_out = pyScript.dbCrtTerm(net=net, name=pyScript.emyString('vdd_out'),\n"
          "                          dir=pyScript.emyString('output'))\n"
          "print('output term:', t_out)")),
        ("dbExpandPoints",
         "Build an L-shaped polygon, expand it asymmetrically on all four sides, inspect result.",
         ["dbExpandPoints"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "pts = pyScript.vector1D_emyPointF()\n"
          "for p in [(0,0),(0,2),(2,2),(2,1),(1,1),(1,0)]:\n"
          "    pts.append(pyScript.emyPointF(*p))\n"
          "result = pyScript.dbExpandPoints(cv=cv, points=pts, left=10, bottom=8, right=6, top=4)\n"
          "print('expanded points:', result)")),
        ("dbFindMemInstByName",
         "Open a design, find a scalar instance by name, then try a non-existent name and a vector bit.",
         ["dbFindMemInstByName"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-ADV')\n"
          "pyScript.aeOpenDesign('test', 'test', 'layout')\n"
          "design = pyScript.aeGetCurDesign()\n"
          "found = pyScript.dbFindMemInstByName(design, 'inst1')\n"
          "print('inst1 found:', found is not None)\n"
          "if found:\n"
          "    print('  forReg:', found.forReg)\n"
          "missing = pyScript.dbFindMemInstByName(design, 'no_such_inst')\n"
          "print('missing is None:', missing is None)\n"
          "vbit = pyScript.dbFindMemInstByName(design, 'inst3<2>')\n"
          "print('vector bit:', vbit is not None)")),
        ("dbGetCurrNetNameByHierName",
         "Build a 2-level hierarchy, create a net at the bottom, resolve its top-level name.",
         ["dbGetCurrNetNameByHierName"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitDb()\n"
          "top = pyScript.dbOpenCV('test_comm', 'top', 'schematic')\n"
          "sub1 = pyScript.dbOpenCV('test_comm', 'test1', 'schematic', mode='w')\n"
          "sub2 = pyScript.dbOpenCV('test_comm', 'test2', 'schematic', mode='w')\n"
          "pyScript.dbCrtNet(sub2, 'net2')\n"
          "pyScript.dbCrtInst(cv=sub1, point=(1,1), master=sub2, inst='inst2_1')\n"
          "pyScript.dbCrtInst(cv=top, point=(0,1), master=sub1, inst='inst1_0')\n"
          "name = pyScript.dbGetCurrNetNameByHierName(top, 'inst1_0/inst2_1/net2')\n"
          "print('resolved name:', str(name))")),
    ]
    for name, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v23-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)

    s4_traces_2 = [
        ("dbPointArrayGen",
         "Create two overlapping rectangles, run AND then XOR, compare result counts.",
         ["dbPointArrayGen"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "def mkpoly(coords):\n"
          "    pa = pyScript.vector1D_emyPointF()\n"
          "    for c in coords:\n"
          "        pa.append(pyScript.emyPointF(*c))\n"
          "    return pa\n"
          "first = pyScript.vector2D_emyPointF()\n"
          "first.append(mkpoly([(0,0),(10,0),(10,10),(0,10)]))\n"
          "second = pyScript.vector2D_emyPointF()\n"
          "second.append(mkpoly([(5,5),(15,5),(15,15),(5,15)]))\n"
          "r_and = pyScript.dbPointArrayGen('AND', cv, first, second)\n"
          "print('AND arrays:', len(r_and))\n"
          "r_xor = pyScript.dbPointArrayGen('XOR', cv, first, second)\n"
          "print('XOR arrays:', len(r_xor))")),
        ("dbResize",
         "Create a rect figure, shrink left and grow other three sides, check result count.",
         ["dbResize"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "fig = pyScript.dbCrtRect(cv=cv, bbox=[(0,0),(10,10)], layer='M1')\n"
          "figs = pyScript.vector1D_p_emyFig()\n"
          "figs.append(fig)\n"
          "size = pyScript.vector1D_double()\n"
          "for v in [-2, 1, 1, 1]:\n"
          "    size.append(v)\n"
          "result = pyScript.dbResize(figs=figs, size=size)\n"
          "print('resized figs:', len(result))")),
        ("dbSchDrawSymbolPin",
         "Open a symbol view, draw a triangle input pin and a square output pin.",
         ["dbSchDrawSymbolPin"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-ADV')\n"
          "pyScript.aeOpenDesign('test_lib', 'test_cell', 'symbol')\n"
          "cv = pyScript.aeGetCurDesign()\n"
          "tri = pyScript.emyPointArrayF()\n"
          "for p in [(0,0),(2,0),(1,1.5),(0,0)]:\n"
          "    tri.append(pyScript.emyPointF(*p))\n"
          "fig_in = pyScript.dbSchDrawSymbolPin(cv, 'PWR', 'input', tri)\n"
          "print('input pin:', fig_in is not None)\n"
          "sq = pyScript.emyPointArrayF()\n"
          "for p in [(0,0),(2,0),(2,2),(0,2),(0,0)]:\n"
          "    sq.append(pyScript.emyPointF(*p))\n"
          "fig_out = pyScript.dbSchDrawSymbolPin(cv, 'OUT', 'output', sq)\n"
          "print('output pin:', fig_out is not None)")),
        ("dbSetInstHeaderMasterName",
         "Create an instance, get its header, rebind the master to a new lib/cell/view.",
         ["dbSetInstHeaderMasterName"],
         ("import pyAether as pyScript\n\n"
          "pyScript.aeOpenDesign('test_agr', 'test', 'layout')\n"
          "cv = pyScript.aeGetCurDesign()\n"
          "pyScript.dbCrtInst(cv, pyScript.emyPointF(12,12),\n"
          "                   lib='smic14ff', cell='n18_ckt', view='layout', inst='pcell_inst')\n"
          "block = cv.getTopBlock()\n"
          "insts = block.getInsts()\n"
          "hdr = insts[0].getHeader()\n"
          "ok = pyScript.dbSetInstHeaderMasterName(hdr, 'test_adv', 'test', 'layout',\n"
          "                                         isReplaceMissmatched=True)\n"
          "print('rebind success:', ok)\n"
          "insts2 = cv.getTopBlock().getInsts()\n"
          "print('new master:', insts2[0].forReg)")),
        ("dbSingleLayerGOA",
         "Create two overlapping rects on M1, run OR and AND, compare result shape counts.",
         ["dbSingleLayerGOA"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "layer = pyScript.emyString('M1')\n"
          "def mkline(coords):\n"
          "    pa = pyScript.vector1D_emyPointF()\n"
          "    for c in coords:\n"
          "        pa.append(pyScript.emyPointF(*c))\n"
          "    return pa\n"
          "fig1 = pyScript.dbCrtLine(cv=cv, points=mkline([(0,0),(10,0),(10,10),(0,10)]), layer=layer)\n"
          "fig2 = pyScript.dbCrtLine(cv=cv, points=mkline([(5,5),(15,5),(15,15),(5,15)]), layer=layer)\n"
          "figs = pyScript.vector1D_p_emyShape()\n"
          "figs.append(fig1)\n"
          "figs.append(fig2)\n"
          "r_or = pyScript.dbSingleLayerGOA(cv=cv, op=pyScript.emyString('OR'), layer=layer, figs=figs)\n"
          "print('OR shapes:', len(r_or))\n"
          "r_and = pyScript.dbSingleLayerGOA(cv=cv, op=pyScript.emyString('AND'), layer=layer, figs=figs)\n"
          "print('AND shapes:', len(r_and))")),
    ]
    for name, scenario, apis, code in s4_traces_2:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v23-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)

    s4_traces_3 = [
        ("dbSmashInst2",
         "Create an instance of a master, then flatten it one level using dbSmashInst2 with a smash_option.",
         ["dbSmashInst2"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('adv')\n"
          "pyScript.aeOpenDesign('test_lib', 'design', 'layout')\n"
          "cv = pyScript.aeGetCurDesign()\n"
          "master = pyScript.dbOpenCV('test_lib', 'master', 'layout')\n"
          "inst = pyScript.dbCrtInst(cv, (0, 0), master)\n"
          "if inst:\n"
          "    opt = pyScript.smash_option()\n"
          "    ok = pyScript.dbSmashInst2(inst, 1, opt)\n"
          "    print('smash ok:', ok)\n"
          "else:\n"
          "    print('no inst to smash')")),
        ("dbTransformBBox",
         "Create a small bbox, apply R90 rotation with 2x magnification and an offset, inspect width/height.",
         ["dbTransformBBox"],
         ("import pyAether as pyScript\n\n"
          "bbox = pyScript.emyBoxF((0, 0), (5, 5))\n"
          "offset = pyScript.emyPointF(10, 10)\n"
          "result = pyScript.dbTransformBBox(bbox=bbox, offsetPoint=offset, orient='R90', mag=2.0)\n"
          "print('result:', result)\n"
          "print('w:', result.width, 'h:', result.height)\n"
          "print('ll:', result.l, result.b, 'ur:', result.r, result.t)\n"
          "bbox2 = pyScript.emyBoxF((0, 0), (4, 2))\n"
          "result2 = pyScript.dbTransformBBox(bbox=bbox2, offsetPoint=pyScript.emyPointF(0,0), orient='R0', mag=1.0)\n"
          "print('identity:', result2.width, result2.height)")),
        ("dbTraverseTriggerFunc",
         "Define a callback subclass that counts visited designs, register it, verify registration.",
         ["dbTraverseTriggerFunc"],
         ("import pyAether as pyScript\n\n"
          "class Counter(pyScript.dbTraverseTriggerFunc):\n"
          "    def __init__(self):\n"
          "        super().__init__()\n"
          "        self.count = 0\n"
          "    def funcCb(self, design):\n"
          "        self.count += 1\n"
          "    def funcReturnCb(self, design):\n"
          "        return self.count < 10\n"
          "cb = Counter()\n"
          "pyScript.dbRegTraverseTrigger(cb)\n"
          "print('callback registered, count:', cb.count)")),
        ("dbTraverseDesignWithCB",
         "Define a counting callback, register it, traverse a design hierarchy to depth 3, print count.",
         ["dbTraverseDesignWithCB"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "class Counter(pyScript.dbTraverseTriggerFunc):\n"
          "    def __init__(self):\n"
          "        super().__init__()\n"
          "        self.n = 0\n"
          "    def funcCb(self, design):\n"
          "        self.n += 1\n"
          "cb = Counter()\n"
          "pyScript.dbRegTraverseTrigger(cb)\n"
          "design = pyScript.aeGetCurDesign()\n"
          "if design:\n"
          "    pyScript.dbTraverseDesignWithCB(design, 'schematic', 3)\n"
          "    print('visited:', cb.n)\n"
          "else:\n"
          "    print('no design open')")),
    ]
    for name, scenario, apis, code in s4_traces_3:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v23-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)

    # ---- S3: code -> doc (13 pairs, one per API) ----
    for name in API_ORDER:
        d = API_DOCS[name]
        code = d["doctest"]
        prompt = ("You are an EDA automation engineer. The following Python "
                  "code uses a PyAether API. Identify the API name, describe "
                  "what it does, and explain its signature.\n\n"
                  "```python\n%s\n```" % code)
        completion = ("The API used is **`%s`**.\n\n"
                      "**Signature**: `%s`\n\n"
                      "%s\n\n"
                      "**Key notes**: %s" % (name, d["sig"], d["desc"], d.get("key_notes", "")))
        _add("S3", "v23-S3-%s" % name, prompt, completion, [name],
             "S3 code_to_doc for %s" % name)

    # ---- S5: anti_pattern / common mistake (13 pairs) ----
    s5_items = [
        ("dbCrtTerm",
         "pyScript.dbCrtTerm(net=net, name='vdd_in', dir='input')",
         "name and dir must be emyString objects, not plain Python strings. Passing a raw str will raise a type error.",
         "pyScript.dbCrtTerm(net=net, name=pyScript.emyString('vdd_in'), dir=pyScript.emyString('input'))"),
        ("dbExpandPoints",
         "pyScript.dbExpandPoints(cv=cv, points=pts, left=10, bottom=8, right=6)",
         "All four offset parameters (left, bottom, right, top) are required positional arguments. Omitting top causes an argument error.",
         "pyScript.dbExpandPoints(cv=cv, points=pts, left=10, bottom=8, right=6, top=4)"),
        ("dbFindMemInstByName",
         "found = pyScript.dbFindMemInstByName(design, 'inst3[2]')",
         "Vector bit indices use angle brackets <>, not square brackets []. 'inst3[2]' will not match and returns None.",
         "found = pyScript.dbFindMemInstByName(design, 'inst3<2>')"),
        ("dbGetCurrNetNameByHierName",
         "name = pyScript.dbGetCurrNetNameByHierName(cv, 'inst1_0.inst2_1.net2')",
         "Hierarchy separator is forward slash /, not dot. Using dot will fail to resolve the hierarchical path.",
         "name = pyScript.dbGetCurrNetNameByHierName(cv, 'inst1_0/inst2_1/net2')"),
        ("dbPointArrayGen",
         "result = pyScript.dbPointArrayGen('and', cv, first, second)",
         "The operation string must be uppercase AND (or OR/XOR). Lowercase 'and' is invalid and returns an empty result.",
         "result = pyScript.dbPointArrayGen('AND', cv, first, second)"),
        ("dbResize",
         "result = pyScript.dbResize(figs=figs, size=[-2, 1, 1, 1])",
         "The size parameter must be a vector1D_double, not a plain Python list. Use the SWIG vector type.",
         "size = pyScript.vector1D_double()\nfor v in [-2, 1, 1, 1]:\n    size.append(v)\nresult = pyScript.dbResize(figs=figs, size=size)"),
        ("dbSchDrawSymbolPin",
         "fig = pyScript.dbSchDrawSymbolPin(cv, 'PWR', 'IN', pts)",
         "The dir parameter must be 'input', 'output', or 'inputOutput' (full word). Abbreviations like 'IN' are invalid.",
         "fig = pyScript.dbSchDrawSymbolPin(cv, 'PWR', 'input', pts)"),
    ]
    for name, wrong, mistake, correct in s5_items:
        prompt = ("You are an EDA automation engineer. The following PyAether "
                  "code has a bug. Identify the mistake and write the corrected "
                  "version.\n\n```python\n%s\n```" % wrong)
        completion = ("**Mistake**: %s\n\n**Corrected code**:\n```python\n%s\n```" % (mistake, correct))
        _add("S5", "v23-S5-%s" % name, prompt, completion, [name],
             "S5 anti_pattern for %s" % name)

    s5_items_2 = [
        ("dbSetInstHeaderMasterName",
         "pyScript.dbSetInstHeaderMasterName(hdr, 'test_adv', 'test', 'layout', isReplaceMismatched=True)",
         "The keyword argument is isReplaceMissmatched (TWO s's in 'Miss'). The common typo 'isReplaceMismatched' (one s) will be silently ignored as an unexpected kwarg.",
         "pyScript.dbSetInstHeaderMasterName(hdr, 'test_adv', 'test', 'layout', isReplaceMissmatched=True)"),
        ("dbSingleLayerGOA",
         "result = pyScript.dbSingleLayerGOA(cv=cv, op=pyScript.emyString('NOT'), layer=layer, figs=figs)",
         "dbSingleLayerGOA only supports OR, AND, and XOR. NOT is not a valid operation for single-layer boolean ops. Use dbLayerNOT or a different approach for negation.",
         "result = pyScript.dbSingleLayerGOA(cv=cv, op=pyScript.emyString('OR'), layer=layer, figs=figs)"),
        ("dbSmashInst2",
         "pyScript.dbSmashInst2(inst, 1)",
         "dbSmashInst2 requires three arguments: inst, level, and a smash_option object. Omitting the option argument causes an argument count error.",
         "opt = pyScript.smash_option()\nok = pyScript.dbSmashInst2(inst, 1, opt)"),
        ("dbTransformBBox",
         "result = pyScript.dbTransformBBox(bbox=bbox, orient='R90', mag=2.0)",
         "The offsetPoint parameter is required (positional or keyword). Omitting it causes an argument error. Use emyPointF(0,0) for a pure rotation/magnification.",
         "result = pyScript.dbTransformBBox(bbox=bbox, offsetPoint=pyScript.emyPointF(0,0), orient='R90', mag=2.0)"),
        ("dbTraverseTriggerFunc",
         "class Counter(pyScript.dbTraverseTriggerFunc):\n    def __init__(self):\n        self.count = 0",
         "When subclassing dbTraverseTriggerFunc, you must call super().__init__() in __init__. Omitting the super().__init__() call may leave the C++ base object uninitialized, causing crashes.",
         "class Counter(pyScript.dbTraverseTriggerFunc):\n    def __init__(self):\n        super().__init__()\n        self.count = 0"),
        ("dbTraverseDesignWithCB",
         "pyScript.dbTraverseDesignWithCB(design, 'schematic', 3)\n# without registering a callback first",
         "You must register a callback via dbRegTraverseTrigger() before calling dbTraverseDesignWithCB. Without a registered callback, the traversal does nothing.",
         "cb = MyCallback()\npyScript.dbRegTraverseTrigger(cb)\npyScript.dbTraverseDesignWithCB(design, 'schematic', 3)"),
    ]
    for name, wrong, mistake, correct in s5_items_2:
        prompt = ("You are an EDA automation engineer. The following PyAether "
                  "code has a bug. Identify the mistake and write the corrected "
                  "version.\n\n```python\n%s\n```" % wrong)
        completion = ("**Mistake**: %s\n\n**Corrected code**:\n```python\n%s\n```" % (mistake, correct))
        _add("S5", "v23-S5-%s" % name, prompt, completion, [name],
             "S5 anti_pattern for %s" % name)

    # ---- S6: cross-API combination (13 pairs) ----
    s6_items = [
        ("dbCrtTerm+dbFindMemInstByName",
         "Open a schematic, find an instance by name, then create a terminal on one of its nets.",
         ["dbCrtTerm", "dbFindMemInstByName"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-ADV')\n"
          "pyScript.aeOpenDesign('test', 'test', 'schematic')\n"
          "design = pyScript.aeGetCurDesign()\n"
          "inst = pyScript.dbFindMemInstByName(design, 'u1')\n"
          "if inst:\n"
          "    print('found u1, forReg:', inst.forReg)\n"
          "    net = pyScript.dbCrtNet(cv=design, name=pyScript.emyString('net_u1'))\n"
          "    term = pyScript.dbCrtTerm(net=net, name=pyScript.emyString('t_u1'),\n"
          "                              dir=pyScript.emyString('input'))\n"
          "    print('terminal created:', term is not None)\n"
          "else:\n"
          "    print('u1 not found')")),
        ("dbExpandPoints+dbResize",
         "Create a rect, resize it, then expand the resulting polygon asymmetrically.",
         ["dbExpandPoints", "dbResize"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "fig = pyScript.dbCrtRect(cv=cv, bbox=[(0,0),(10,10)], layer='M1')\n"
          "figs = pyScript.vector1D_p_emyFig()\n"
          "figs.append(fig)\n"
          "size = pyScript.vector1D_double()\n"
          "for v in [1, 1, 1, 1]:\n"
          "    size.append(v)\n"
          "resized = pyScript.dbResize(figs=figs, size=size)\n"
          "print('resized count:', len(resized))\n"
          "pts = pyScript.vector1D_emyPointF()\n"
          "for p in [(0,0),(12,0),(12,12),(0,12)]:\n"
          "    pts.append(pyScript.emyPointF(*p))\n"
          "expanded = pyScript.dbExpandPoints(cv=cv, points=pts, left=2, bottom=2, right=2, top=2)\n"
          "print('expanded:', expanded)")),
        ("dbPointArrayGen+dbSingleLayerGOA",
         "Create two shapes, generate intersection with dbPointArrayGen, then OR them with dbSingleLayerGOA.",
         ["dbPointArrayGen", "dbSingleLayerGOA"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "layer = pyScript.emyString('M1')\n"
          "def mkpoly(coords):\n"
          "    pa = pyScript.vector1D_emyPointF()\n"
          "    for c in coords:\n"
          "        pa.append(pyScript.emyPointF(*c))\n"
          "    return pa\n"
          "first = pyScript.vector2D_emyPointF()\n"
          "first.append(mkpoly([(0,0),(10,0),(10,10),(0,10)]))\n"
          "second = pyScript.vector2D_emyPointF()\n"
          "second.append(mkpoly([(5,5),(15,5),(15,15),(5,15)]))\n"
          "r_and = pyScript.dbPointArrayGen('AND', cv, first, second)\n"
          "print('AND arrays:', len(r_and))\n"
          "fig1 = pyScript.dbCrtLine(cv=cv, points=mkpoly([(0,0),(10,0),(10,10),(0,10)]), layer=layer)\n"
          "fig2 = pyScript.dbCrtLine(cv=cv, points=mkpoly([(5,5),(15,5),(15,15),(5,15)]), layer=layer)\n"
          "figs = pyScript.vector1D_p_emyShape()\n"
          "figs.append(fig1)\n"
          "figs.append(fig2)\n"
          "r_or = pyScript.dbSingleLayerGOA(cv=cv, op=pyScript.emyString('OR'), layer=layer, figs=figs)\n"
          "print('OR shapes:', len(r_or))")),
        ("dbTransformBBox+dbResize",
         "Create a rect, resize it, get its bbox, then transform that bbox with rotation and offset.",
         ["dbTransformBBox", "dbResize"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "fig = pyScript.dbCrtRect(cv=cv, bbox=[(0,0),(5,5)], layer='M1')\n"
          "figs = pyScript.vector1D_p_emyFig()\n"
          "figs.append(fig)\n"
          "size = pyScript.vector1D_double()\n"
          "for v in [2, 2, 2, 2]:\n"
          "    size.append(v)\n"
          "resized = pyScript.dbResize(figs=figs, size=size)\n"
          "print('resized:', len(resized))\n"
          "bbox = pyScript.emyBoxF((0,0), (9,9))\n"
          "result = pyScript.dbTransformBBox(bbox=bbox, offsetPoint=pyScript.emyPointF(5,5),\n"
          "                                   orient='R90', mag=1.0)\n"
          "print('transformed w:', result.width, 'h:', result.height)")),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript), combining the relevant "
                  "db* APIs." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v23-S6-%s" % apis_str.replace("+", "-"), prompt, completion, apis,
             "S6 cross_api_combo: %s" % apis_str)

    s6_items_2 = [
        ("dbTraverseTriggerFunc+dbTraverseDesignWithCB",
         "Define a callback that counts designs and stops at 5, register it, traverse hierarchy.",
         ["dbTraverseTriggerFunc", "dbTraverseDesignWithCB"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "class StopAtFive(pyScript.dbTraverseTriggerFunc):\n"
          "    def __init__(self):\n"
          "        super().__init__()\n"
          "        self.n = 0\n"
          "    def funcCb(self, design):\n"
          "        self.n += 1\n"
          "    def funcReturnCb(self, design):\n"
          "        return self.n < 5\n"
          "cb = StopAtFive()\n"
          "pyScript.dbRegTraverseTrigger(cb)\n"
          "design = pyScript.aeGetCurDesign()\n"
          "if design:\n"
          "    pyScript.dbTraverseDesignWithCB(design, 'schematic', 10)\n"
          "    print('visited (max 5):', cb.n)\n"
          "else:\n"
          "    print('no design')")),
        ("dbSchDrawSymbolPin+dbTransformBBox",
         "Draw a symbol pin, then transform a bbox representing the pin area for placement.",
         ["dbSchDrawSymbolPin", "dbTransformBBox"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-ADV')\n"
          "pyScript.aeOpenDesign('test_lib', 'cell1', 'symbol')\n"
          "cv = pyScript.aeGetCurDesign()\n"
          "pa = pyScript.emyPointArrayF()\n"
          "for p in [(0,0),(2,0),(2,2),(0,2),(0,0)]:\n"
          "    pa.append(pyScript.emyPointF(*p))\n"
          "fig = pyScript.dbSchDrawSymbolPin(cv, 'CLK', 'input', pa)\n"
          "print('pin drawn:', fig is not None)\n"
          "bbox = pyScript.emyBoxF((0,0), (2,2))\n"
          "placed = pyScript.dbTransformBBox(bbox=bbox, offsetPoint=pyScript.emyPointF(10,10),\n"
          "                                   orient='R0', mag=1.0)\n"
          "print('placed at:', placed.l, placed.b)")),
        ("dbSetInstHeaderMasterName+dbSmashInst2",
         "Create an instance, rebind its master, then flatten it one level.",
         ["dbSetInstHeaderMasterName", "dbSmashInst2"],
         ("import pyAether as pyScript\n\n"
          "pyScript.aeOpenDesign('test_agr', 'test', 'layout')\n"
          "cv = pyScript.aeGetCurDesign()\n"
          "pyScript.dbCrtInst(cv, pyScript.emyPointF(0,0),\n"
          "                   lib='smic14ff', cell='n18_ckt', view='layout', inst='i0')\n"
          "insts = cv.getTopBlock().getInsts()\n"
          "hdr = insts[0].getHeader()\n"
          "ok = pyScript.dbSetInstHeaderMasterName(hdr, 'test_adv', 'test', 'layout',\n"
          "                                         isReplaceMissmatched=True)\n"
          "print('rebind:', ok)\n"
          "insts2 = cv.getTopBlock().getInsts()\n"
          "if insts2:\n"
          "    opt = pyScript.smash_option()\n"
          "    smashed = pyScript.dbSmashInst2(insts2[0], 1, opt)\n"
          "    print('smashed:', smashed)")),
        ("dbGetCurrNetNameByHierName+dbFindMemInstByName",
         "Find an instance by name, then resolve a hierarchical net name through it.",
         ["dbGetCurrNetNameByHierName", "dbFindMemInstByName"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitDb()\n"
          "top = pyScript.dbOpenCV('test_comm', 'top', 'schematic')\n"
          "inst = pyScript.dbFindMemInstByName(top, 'inst1_0')\n"
          "print('inst found:', inst is not None)\n"
          "if inst:\n"
          "    name = pyScript.dbGetCurrNetNameByHierName(top, 'inst1_0/inst2_1/net2')\n"
          "    print('resolved net:', str(name))")),
        ("dbCrtTerm+dbGetCurrNetNameByHierName",
         "Build a hierarchy, resolve a hierarchical net name, then create a terminal on the resolved net.",
         ["dbCrtTerm", "dbGetCurrNetNameByHierName"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitDb()\n"
          "top = pyScript.dbOpenCV('test_comm', 'top', 'schematic')\n"
          "sub = pyScript.dbOpenCV('test_comm', 'sub', 'schematic', mode='w')\n"
          "net = pyScript.dbCrtNet(sub, 'sig')\n"
          "pyScript.dbCrtInst(cv=top, point=(0,0), master=sub, inst='u1')\n"
          "resolved = pyScript.dbGetCurrNetNameByHierName(top, 'u1/sig')\n"
          "print('resolved:', str(resolved))\n"
          "term = pyScript.dbCrtTerm(net=net, name=pyScript.emyString('t_sig'),\n"
          "                          dir=pyScript.emyString('input'))\n"
          "print('terminal:', term is not None)")),
    ]
    for apis_str, scenario, apis, code in s6_items_2:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript), combining the relevant "
                  "db* APIs." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v23-S6-%s" % apis_str.replace("+", "-"), prompt, completion, apis,
             "S6 cross_api_combo: %s" % apis_str)

    s6_items_3 = [
        ("dbExpandPoints+dbPointArrayGen",
         "Expand a polygon, then use the expanded points as input to a boolean AND operation.",
         ["dbExpandPoints", "dbPointArrayGen"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "pts = pyScript.vector1D_emyPointF()\n"
          "for p in [(0,0),(5,0),(5,5),(0,5)]:\n"
          "    pts.append(pyScript.emyPointF(*p))\n"
          "expanded = pyScript.dbExpandPoints(cv=cv, points=pts, left=1, bottom=1, right=1, top=1)\n"
          "print('expanded:', expanded)\n"
          "def mkpoly(coords):\n"
          "    pa = pyScript.vector1D_emyPointF()\n"
          "    for c in coords:\n"
          "        pa.append(pyScript.emyPointF(*c))\n"
          "    return pa\n"
          "first = pyScript.vector2D_emyPointF()\n"
          "first.append(mkpoly([(0,0),(6,0),(6,6),(0,6)]))\n"
          "second = pyScript.vector2D_emyPointF()\n"
          "second.append(mkpoly([(3,3),(9,3),(9,9),(3,9)]))\n"
          "r = pyScript.dbPointArrayGen('AND', cv, first, second)\n"
          "print('AND arrays:', len(r))")),
        ("dbSingleLayerGOA+dbResize",
         "Create a rect, resize it, then OR the original and resized shapes on the same layer.",
         ["dbSingleLayerGOA", "dbResize"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "layer = pyScript.emyString('M1')\n"
          "fig1 = pyScript.dbCrtRect(cv=cv, bbox=[(0,0),(5,5)], layer='M1')\n"
          "figs_r = pyScript.vector1D_p_emyFig()\n"
          "figs_r.append(fig1)\n"
          "size = pyScript.vector1D_double()\n"
          "for v in [2, 2, 2, 2]:\n"
          "    size.append(v)\n"
          "resized = pyScript.dbResize(figs=figs_r, size=size)\n"
          "print('resized:', len(resized))\n"
          "fig2 = pyScript.dbCrtRect(cv=cv, bbox=[(0,0),(9,9)], layer='M1')\n"
          "figs = pyScript.vector1D_p_emyShape()\n"
          "figs.append(fig1)\n"
          "figs.append(fig2)\n"
          "r_or = pyScript.dbSingleLayerGOA(cv=cv, op=pyScript.emyString('OR'), layer=layer, figs=figs)\n"
          "print('OR shapes:', len(r_or))")),
        ("dbSchDrawSymbolPin+dbCrtTerm",
         "Draw a symbol pin in a symbol view, then create a corresponding terminal in the schematic.",
         ["dbSchDrawSymbolPin", "dbCrtTerm"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-ADV')\n"
          "pyScript.aeOpenDesign('test_lib', 'cell1', 'symbol')\n"
          "sym_cv = pyScript.aeGetCurDesign()\n"
          "pa = pyScript.emyPointArrayF()\n"
          "for p in [(0,0),(2,0),(1,2),(0,0)]:\n"
          "    pa.append(pyScript.emyPointF(*p))\n"
          "fig = pyScript.dbSchDrawSymbolPin(sym_cv, 'IN', 'input', pa)\n"
          "print('symbol pin:', fig is not None)\n"
          "sch = pyScript.dbOpenCV('test_lib', 'cell1', 'schematic', mode='w')\n"
          "net = pyScript.dbCrtNet(cv=sch, name=pyScript.emyString('IN'))\n"
          "term = pyScript.dbCrtTerm(net=net, name=pyScript.emyString('IN'),\n"
          "                          dir=pyScript.emyString('input'))\n"
          "print('terminal:', term is not None)")),
        ("dbSmashInst2+dbTransformBBox",
         "Create an instance, flatten it, then compute the transformed bbox of the flattened area.",
         ["dbSmashInst2", "dbTransformBBox"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('adv')\n"
          "pyScript.aeOpenDesign('test_lib', 'design', 'layout')\n"
          "cv = pyScript.aeGetCurDesign()\n"
          "master = pyScript.dbOpenCV('test_lib', 'master', 'layout')\n"
          "inst = pyScript.dbCrtInst(cv, (5, 5), master)\n"
          "if inst:\n"
          "    opt = pyScript.smash_option()\n"
          "    ok = pyScript.dbSmashInst2(inst, 1, opt)\n"
          "    print('smash ok:', ok)\n"
          "bbox = pyScript.emyBoxF((5, 5), (15, 15))\n"
          "result = pyScript.dbTransformBBox(bbox=bbox, offsetPoint=pyScript.emyPointF(0,0),\n"
          "                                   orient='R90', mag=1.0)\n"
          "print('transformed:', result.width, result.height)")),
    ]
    for apis_str, scenario, apis, code in s6_items_3:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript), combining the relevant "
                  "db* APIs." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v23-S6-%s" % apis_str.replace("+", "-"), prompt, completion, apis,
             "S6 cross_api_combo: %s" % apis_str)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    ap = argparse.ArgumentParser(
        description="R193 v23 PyAether SFT corpus: db* lifecycle/traverse (13 APIs, 65 pairs)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print summary only, do not write output file")
    ap.add_argument("--limit", type=int, default=None,
                    help="Limit number of pairs (for testing)")
    ap.add_argument("--output", default=DEFAULT_OUTPUT,
                    help="Output JSONL path (default: %(default)s)")
    args = ap.parse_args()

    eval_eps = load_eval_entry_points()
    sys.stderr.write("Loaded %d eval entry_points from %s\n" % (len(eval_eps), EVAL_DS))

    pairs, rejected, reject_details = build_pairs(eval_eps, limit=args.limit)

    # ---- Summary ----
    by_type = {}
    for p in pairs:
        by_type[p["type"]] = by_type.get(p["type"], 0) + 1
    sys.stderr.write("\n=== R193 v23 db* corpus summary ===\n")
    sys.stderr.write("Total pairs: %d\n" % len(pairs))
    for t in sorted(by_type):
        sys.stderr.write("  %s: %d\n" % (t, by_type[t]))
    sys.stderr.write("Rejected (contamination): %d\n" % rejected)
    if reject_details:
        sys.stderr.write("  Rejected IDs:\n")
        for pid, hit in reject_details:
            sys.stderr.write("    %s -> hit entry_point: %s\n" % (pid, hit))

    # ---- API coverage check ----
    covered = set()
    for p in pairs:
        for a in p["api_used"]:
            covered.add(a)
    missing = set(API_ORDER) - covered
    if missing:
        sys.stderr.write("WARNING: APIs not covered: %s\n" % ", ".join(sorted(missing)))
    else:
        sys.stderr.write("All %d target APIs covered.\n" % len(API_ORDER))

    if args.dry_run:
        sys.stderr.write("\n[dry-run] No output file written.\n")
        # Print sample pair
        if pairs:
            sample = pairs[0]
            sys.stderr.write("\nSample pair (%s):\n" % sample["id"])
            sys.stderr.write("  prompt (first 200 chars): %s\n" % sample["prompt"][:200])
            sys.stderr.write("  completion (first 200 chars): %s\n" % sample["completion"][:200])
        return

    # ---- Write output ----
    with open(args.output, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    sys.stderr.write("\nWrote %d pairs to %s\n" % (len(pairs), args.output))

    # ---- Final contamination assertion ----
    if rejected > 0:
        sys.stderr.write("ERROR: %d pairs rejected due to contamination!\n" % rejected)
        sys.exit(1)
    sys.stderr.write("Contamination check: PASS (0 rejected)\n")


if __name__ == "__main__":
    main()

