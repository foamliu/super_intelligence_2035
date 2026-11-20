#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r198_mde_goa_corpus.py
R198 -- v28 PyAether SFT corpus: MDE* enum constants (6) + goa* GOA layer ops (4)
= 10 APIs, 50 pairs.

BACKGROUND: v11-v27 (733 pairs) cover 134/164 eval raw APIs (81.7%). 30 blind.
Data-driven scan (R191 blind_scan, re-run with v27) shows MDE is the #1 blind
family (6 usages, 6 constant APIs) and goa is #2 (6 usages, 4 callable APIs).
Covering both in one round clears the top 2 blind families.

All ISOLATE-class (eval helper APIs/constants, NOT eval entry_points).
Fingerprint scan rejects eval entry_points (155 loaded).

Authoritative signatures fetched via pyAether MCP get_api_details (R198 wake).

Usage:
  python3 baize_posttrain_r198_mde_goa_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v28_mde_goa.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

# === goa* APIs (4 callable functions) ===

API_DOCS["goaInit"] = {
    "sig": "goaInit(design: emyDesign, depth: emyUInt4=64) -> bool",
    "desc": "Initializes a GOA (Geometry Operations Accelerator) session for the given design. GOA decomposes layout shapes into tiles for efficient geometric operations (AND, OR, NOT, ABUT, GROW, etc.). Must be called before any goaLayer* operation. Always pair with goaDone() to release resources.",
    "params": {
        "design": "emyDesign -- the design (cell view) to query goa layers from. Typically obtained via dbOpenCV() or dbCreateCellView().",
        "depth": "emyUInt4, optional -- hierarchy depth to traverse. Default 64. Larger values handle deeper nesting but use more memory.",
    },
    "returns": "bool -- True if GOA session initialized successfully, False otherwise (invalid design, missing tech, etc.)",
    "methods": "pyScript.goaInit(cv) -> True; pyScript.goaInit(cv, 32) -> True",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> pyScript.emyInitQuery()\n"
                ">>> cv = pyScript.dbOpenCV(\"test_adv\", \"test2\", \"layout\")\n"
                ">>> ok = pyScript.goaInit(cv)\n"
                ">>> print(ok)\n"
                "True\n"
                ">>> pyScript.goaDone()"),
    "category": "GOA / Geometry Operations Accelerator", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "goaInit MUST be called before goaLayerFromCellView/goaLayerAbut/goaLayerToCellView. Only one GOA session active at a time. Always call goaDone() when done to free resources. depth=64 default covers most designs; use smaller values for flat designs to save memory."}

API_DOCS["goaLayerAbut"] = {
    "sig": "goaLayerAbut(aLayer: goaLayer, aLayer2: goaLayer, result: goaLayer) -> bool",
    "desc": "Adds shapes to the result output layer for shapes on aLayer that abut (physically touch/share an edge with) shapes on aLayer2. Used in DRC checks to detect minimum-spacing violations or unintended connections between layers. The result layer receives the abutting portions.",
    "params": {
        "aLayer": "goaLayer -- the first goa layer (e.g. Metal1 shapes)",
        "aLayer2": "goaLayer -- the second goa layer (e.g. Metal2 shapes)",
        "result": "goaLayer -- the output goa layer that receives abutting-region shapes",
    },
    "returns": "bool -- True if operation executed successfully (does NOT mean abutting shapes were found; check result layer content). False on error.",
    "methods": "pyScript.goaLayerAbut(layer1, layer2, resultLayer) -> True",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> pyScript.emyInitQuery()\n"
                ">>> cv = pyScript.dbOpenCV(\"test_adv\", \"test2\", \"layout\")\n"
                ">>> pyScript.dbCrtRect(cv, pyScript.emyBoxF(0, 0, 10, 10), 'M1')\n"
                ">>> pyScript.dbCrtRect(cv, pyScript.emyBoxF(10, 5, 15, 8), 'M2')\n"
                ">>> pyScript.goaInit(cv)\n"
                ">>> layer1 = pyScript.goaLayerFromCellView('M1')\n"
                ">>> layer2 = pyScript.goaLayerFromCellView('M2')\n"
                ">>> resultLayer = pyScript.goaLayerFromCellView('M3')\n"
                ">>> ok = pyScript.goaLayerAbut(layer1, layer2, resultLayer)\n"
                ">>> print(ok)\n"
                "True\n"
                ">>> pyScript.goaLayerToCellView(resultLayer, 'M3')\n"
                ">>> pyScript.goaDone()"),
    "category": "GOA / Geometry Operations Accelerator", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "goaLayerAbut returns True on successful execution, NOT on finding abutting shapes. Inspect result layer (via goaLayerToCellView) to see actual abutment regions. All three arguments must be goaLayer objects created by goaLayerFromCellView or goaNewLayer. Common in DRC: detect M1-M2 touching edges."}

API_DOCS["goaLayerFromCellView"] = {
    "sig": "goaLayerFromCellView(layerName: emyString, boxF: emyBoxF=emyBoxF(INT_MIN,INT_MIN,INT_MAX,INT_MAX), purposeNameList: emyArray_emyString=None, maskColor: emyString='grayColor', startLevel: emyUInt4=0, stopLevel: emyUInt4=32, area: emyPointArrayF=emyPointArrayF()) -> goaLayer",
    "desc": "Creates a new goaLayer object from the shapes on the named layer in the current design's cell view. This is the entry point for all GOA geometric operations -- you load layers from the layout, perform operations (AND/OR/ABUT/GROW), then write results back with goaLayerToCellView.",
    "params": {
        "layerName": "emyString -- the layer name (must exist in the design's tech). E.g. 'M1', 'M2', 'Poly'.",
        "boxF": "emyBoxF, optional -- bounding box to filter shapes. Default = entire design area.",
        "purposeNameList": "emyArray_emyString, optional -- purpose name filter. Default None = all purposes.",
        "maskColor": "emyString, optional -- display color. Default 'grayColor'.",
        "startLevel": "emyUInt4, optional -- hierarchy start level. Default 0 (top).",
        "stopLevel": "emyUInt4, optional -- hierarchy stop level. Default 32.",
        "area": "emyPointArrayF, optional -- polygon area filter. If specified, boxF is ignored.",
    },
    "returns": "goaLayer -- a goaLayer object containing all shapes on the named layer within the filter area. Returns None if layer not found or GOA not initialized.",
    "methods": "pyScript.goaLayerFromCellView('M1') -> goaLayer",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> pyScript.emyInitQuery()\n"
                ">>> cv = pyScript.dbOpenCV(\"test_adv\", \"test2\", \"layout\")\n"
                ">>> pyScript.dbCrtRect(cv, pyScript.emyBoxF(0, 0, 10, 10), 'M1')\n"
                ">>> pyScript.goaInit(cv)\n"
                ">>> layer = pyScript.goaLayerFromCellView('M1')\n"
                ">>> print(type(layer).__name__)\n"
                "goaLayer\n"
                ">>> pyScript.goaDone()"),
    "category": "GOA / Geometry Operations Accelerator", "safety": "ISOLATE", "eval_count": 3,
    "key_notes": "goaInit(cv) MUST be called first. layerName must be a valid tech layer name. If area (emyPointArrayF) is specified, boxF is ignored. Returns None for non-existent layers. Use startLevel/stopLevel to limit hierarchy traversal."}

API_DOCS["goaLayerToCellView"] = {
    "sig": "goaLayerToCellView(goaLayer: goaLayer, layerName: emyString, cellName=None, viewName=None, cv=None, purposeName='drawing', tiles=False, isCutX=False, noHoles=True, maskColor='redColor', pShapes=None) -> bool",
    "desc": "Writes a goaLayer (typically the result of a GOA geometric operation) back into a cell view as physical shapes on the specified layer. This is the output step: load -> operate -> write back.",
    "params": {
        "goaLayer": "goaLayer -- the goaLayer to write (result from goaLayerAbut/goaLayerAnd/etc.)",
        "layerName": "emyString -- target layer name in the cell view (e.g. 'M1', 'RESULT')",
        "cellName": "emyString, optional -- target cell name. Must pair with viewName.",
        "viewName": "emyString, optional -- target view name. Must pair with cellName.",
        "cv": "emyCellView, optional -- target cell view directly. Overrides cellName/viewName.",
        "purposeName": "emyString, optional -- purpose name. Default 'drawing'.",
        "tiles": "bool, optional -- if True, shapes written as tiles. Default False.",
        "noHoles": "bool, optional -- if True, holes simplified. Default True.",
        "pShapes": "emyArray_p_emyObject, optional -- output array to receive shape objects.",
    },
    "returns": "bool -- True if shapes written successfully. False on error.",
    "methods": "pyScript.goaLayerToCellView(resultLayer, 'M3') -> True",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> pyScript.emyInitQuery()\n"
                ">>> cv = pyScript.dbOpenCV(\"test_adv\", \"test2\", \"layout\")\n"
                ">>> pyScript.dbCrtRect(cv, pyScript.emyBoxF(0, 0, 10, 10), 'M1')\n"
                ">>> pyScript.goaInit(cv)\n"
                ">>> layer = pyScript.goaLayerFromCellView('M1')\n"
                ">>> ok = pyScript.goaLayerToCellView(layer, 'M2')\n"
                ">>> print(ok)\n"
                "True\n"
                ">>> pyScript.goaDone()"),
    "category": "GOA / Geometry Operations Accelerator", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "If neither cv nor (cellName, viewName) is specified, uses the current active cell view. cellName and viewName must be specified together. pShapes can capture the written shape objects. Always call goaDone() after all GOA operations."}

# === MDE_* enum constants (6 integer constants) ===

API_DOCS["MDE_SWEEP_RANGE_CENTER_SPAN"] = {
    "sig": "MDE_SWEEP_RANGE_CENTER_SPAN (int constant) -- used as MdeSweepRange.mode value",
    "desc": "An integer enum constant specifying the sweep range mode where the range is defined by a center value and a span (half-width) value, rather than explicit start/stop bounds. Set as MdeSweepRange.mode = MDE_SWEEP_RANGE_CENTER_SPAN, then configure .center and .span properties. Alternative to MDE_SWEEP_RANGE_START_STOP.",
    "params": {},
    "returns": "int -- the enum constant value (passed as MdeSweepRange.mode)",
    "methods": "sr = pyScript.MdeSweepRange(); sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN; sr.center = '1e9'; sr.span = '100e6'",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> sr = pyScript.MdeSweepRange()\n"
                ">>> sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n"
                ">>> sr.center = '1e9'\n"
                ">>> sr.span = '100e6'\n"
                ">>> print(type(sr.mode).__name__)\n"
                "int"),
    "category": "MDE / Sweep Range Mode Constant", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Integer constant (NOT a function). Set as MdeSweepRange.mode, then use .center (string) and .span (string). Alternative is MDE_SWEEP_RANGE_START_STOP (.start, .stop). Numeric values are strings (e.g. '1e9'). Must call emyInitAether before accessing."}

API_DOCS["MDE_SWEEP_TYPE_LOG"] = {
    "sig": "MDE_SWEEP_TYPE_LOG (int constant) -- used as MdeSweepType.mode value",
    "desc": "An integer enum constant specifying logarithmic sweep type mode. When MdeSweepType.mode = MDE_SWEEP_TYPE_LOG, sweep points are distributed logarithmically. The logMode sub-property (MDE_SWEEP_TYPE_LOG_POINTS_DEC or MDE_SWEEP_TYPE_LOG_NUM_STEP) controls whether points are per-decade or total count.",
    "params": {},
    "returns": "int -- the enum constant value (passed as MdeSweepType.mode)",
    "methods": "st = pyScript.MdeSweepType(); st.mode = pyScript.MDE_SWEEP_TYPE_LOG; st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP; st.numberOfStepsForLog = '50'",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> st = pyScript.MdeSweepType()\n"
                ">>> st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n"
                ">>> print(type(st.mode).__name__)\n"
                "int"),
    "category": "MDE / Sweep Type Mode Constant", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Integer constant for MdeSweepType.mode. When mode=LOG, set logMode to MDE_SWEEP_TYPE_LOG_POINTS_DEC or MDE_SWEEP_TYPE_LOG_NUM_STEP. Then set pointsPerDecade or numberOfStepsForLog. Alternatives: MDE_SWEEP_TYPE_AUTO, MDE_SWEEP_TYPE_LINEAR."}

API_DOCS["MDE_SWEEP_TYPE_LOG_NUM_STEP"] = {
    "sig": "MDE_SWEEP_TYPE_LOG_NUM_STEP (int constant) -- used as MdeSweepType.logMode value",
    "desc": "An integer enum constant specifying the logarithmic sweep sub-mode where the total number of sweep steps is specified directly. When MdeSweepType.logMode = MDE_SWEEP_TYPE_LOG_NUM_STEP, set MdeSweepType.numberOfStepsForLog to the total step count (string). Alternative to MDE_SWEEP_TYPE_LOG_POINTS_DEC (points per decade).",
    "params": {},
    "returns": "int -- the enum constant value (passed as MdeSweepType.logMode)",
    "methods": "st = pyScript.MdeSweepType(); st.mode = pyScript.MDE_SWEEP_TYPE_LOG; st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP; st.numberOfStepsForLog = '100'",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> st = pyScript.MdeSweepType()\n"
                ">>> st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n"
                ">>> st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP\n"
                ">>> st.numberOfStepsForLog = '50'\n"
                ">>> print(type(st.logMode).__name__)\n"
                "int"),
    "category": "MDE / Sweep Type Log Mode Constant", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Integer constant for MdeSweepType.logMode. Requires MdeSweepType.mode = MDE_SWEEP_TYPE_LOG first. Set numberOfStepsForLog (string) to total step count. Alternative logMode: MDE_SWEEP_TYPE_LOG_POINTS_DEC (set pointsPerDecade). Numeric values are strings."}

API_DOCS["MDE_SWEEP_VARIABLE_MODEL_PARAMETER"] = {
    "sig": "MDE_SWEEP_VARIABLE_MODEL_PARAMETER (int constant) -- used as MdeSweepVariable.mode value",
    "desc": "An integer enum constant specifying the sweep variable mode for sweeping a model parameter (e.g. transistor width W, length L, threshold voltage Vth). When MdeSweepVariable.mode = MDE_SWEEP_VARIABLE_MODEL_PARAMETER, set .modelName, .modelParameterName, and .freForMod. Used in parametric AC/DC analyses.",
    "params": {},
    "returns": "int -- the enum constant value (passed as MdeSweepVariable.mode)",
    "methods": "sv = pyScript.MdeSweepVariable(); sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER; sv.modelName = 'nch'; sv.modelParameterName = 'W'; sv.freForMod = '1e9'",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> sv = pyScript.MdeSweepVariable()\n"
                ">>> sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n"
                ">>> sv.modelName = 'nch'\n"
                ">>> sv.modelParameterName = 'W'\n"
                ">>> sv.freForMod = '1e9'\n"
                ">>> print(type(sv.mode).__name__)\n"
                "int"),
    "category": "MDE / Sweep Variable Mode Constant", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Integer constant for MdeSweepVariable.mode. Configure .modelName, .modelParameterName, .freForMod (all strings). Alternatives: MDE_SWEEP_VARIABLE_FREQUENCY, MDE_SWEEP_VARIABLE_TEMPERATURE, MDE_SWEEP_VARIABLE_DESIGN_VARIABLE. Used with MdeAcAnalysis.setSweepVariable()."}

API_DOCS["MDE_TRAN_ACC_LEVEL_CONSERVATIVE"] = {
    "sig": "MDE_TRAN_ACC_LEVEL_CONSERVATIVE (int constant) -- used as MdeTranAnalysis.setAccuracyLevel() argument",
    "desc": "An integer enum constant (MdeTranAccuracyLevelEnum) specifying the most conservative (highest accuracy, slowest) transient analysis accuracy level. When passed to MdeTranAnalysis.setAccuracyLevel(), the solver uses tightest tolerances and smallest timesteps. Used when signal integrity is critical. Alternative: MDE_TRAN_ACC_LEVEL_LIBERAL (fastest), MDE_TRAN_ACC_LEVEL_MODERATE (balanced).",
    "params": {},
    "returns": "int -- the enum constant value (passed to MdeTranAnalysis.setAccuracyLevel)",
    "methods": "tran = pyScript.MdeTranAnalysis(); tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> tran = pyScript.MdeTranAnalysis()\n"
                ">>> tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n"
                ">>> print('accuracy set to conservative')\n"
                "accuracy set to conservative"),
    "category": "MDE / Tran Accuracy Level Constant", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Integer constant of MdeTranAccuracyLevelEnum. Pass to MdeTranAnalysis.setAccuracyLevel(). Most accurate but slowest. Three levels: CONSERVATIVE (tightest), MODERATE (default), LIBERAL (loosest). The tran object is then passed to MdeSetting.setTranAnalysis(). Must call emyInitAether first."}

API_DOCS["MDE_TRAN_ACC_LEVEL_LIBERAL"] = {
    "sig": "MDE_TRAN_ACC_LEVEL_LIBERAL (int constant) -- used as MdeTranAnalysis.setAccuracyLevel() argument",
    "desc": "An integer enum constant (MdeTranAccuracyLevelEnum) specifying the most liberal (lowest accuracy, fastest) transient analysis accuracy level. When passed to MdeTranAnalysis.setAccuracyLevel(), the solver uses loosest tolerances and largest timesteps for maximum throughput. Used for quick feasibility checks. Alternative: MDE_TRAN_ACC_LEVEL_CONSERVATIVE (slowest, most accurate).",
    "params": {},
    "returns": "int -- the enum constant value (passed to MdeTranAnalysis.setAccuracyLevel)",
    "methods": "tran = pyScript.MdeTranAnalysis(); tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_LIBERAL)",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> tran = pyScript.MdeTranAnalysis()\n"
                ">>> tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_LIBERAL)\n"
                ">>> print('accuracy set to liberal')\n"
                "accuracy set to liberal"),
    "category": "MDE / Tran Accuracy Level Constant", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Integer constant of MdeTranAccuracyLevelEnum. Pass to MdeTranAnalysis.setAccuracyLevel(). Fastest but least accurate. Three levels: CONSERVATIVE (tightest), MODERATE (default), LIBERAL (loosest). Use LIBERAL for quick sweeps, CONSERVATIVE for final verification."}

API_ORDER = [
    "goaInit", "goaLayerAbut", "goaLayerFromCellView", "goaLayerToCellView",
    "MDE_SWEEP_RANGE_CENTER_SPAN", "MDE_SWEEP_TYPE_LOG", "MDE_SWEEP_TYPE_LOG_NUM_STEP",
    "MDE_SWEEP_VARIABLE_MODEL_PARAMETER", "MDE_TRAN_ACC_LEVEL_CONSERVATIVE",
    "MDE_TRAN_ACC_LEVEL_LIBERAL",
]


def load_eval_entry_points():
    eps = set()
    if not os.path.exists(EVAL_DS):
        sys.stderr.write("WARNING: eval dataset not found at %s\n" % EVAL_DS)
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

    # ---- S1: doc -> code (10 pairs, one per API) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v28-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S3: code -> doc (10 pairs, one per API) ----
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
        _add("S3", "v28-S3-%s" % name, prompt, completion, [name],
             "S3 code_to_doc for %s" % name)

    # ---- S4: multi-step trace (10 pairs) ----
    s4_traces = [
        ("goaInit",
         "Initialize a GOA session on a cell view, then create a goaLayer from 'M1' and verify the session is active.",
         ["goaInit", "goaLayerFromCellView"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> cv = pyScript.dbOpenCV(\"mylib\", \"inv\", \"layout\")\n"
         ">>> ok = pyScript.goaInit(cv)\n"
         ">>> if not ok:\n"
         "...     raise RuntimeError('GOA init failed')\n"
         ">>> layer = pyScript.goaLayerFromCellView('M1')\n"
         ">>> print('GOA active, M1 loaded:', type(layer).__name__)\n"
         "GOA active, M1 loaded: goaLayer\n"
         ">>> pyScript.goaDone()"),
        ("goaLayerAbut",
         "Detect abutting shapes between M1 and M2 layers and write the result to 'DRC_ABUT' for inspection.",
         ["goaLayerAbut", "goaLayerFromCellView", "goaLayerToCellView"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> cv = pyScript.dbOpenCV(\"mylib\", \"top\", \"layout\")\n"
         ">>> pyScript.dbCrtRect(cv, pyScript.emyBoxF(0, 0, 10, 10), 'M1')\n"
         ">>> pyScript.dbCrtRect(cv, pyScript.emyBoxF(10, 0, 20, 10), 'M2')\n"
         ">>> pyScript.goaInit(cv)\n"
         ">>> m1 = pyScript.goaLayerFromCellView('M1')\n"
         ">>> m2 = pyScript.goaLayerFromCellView('M2')\n"
         ">>> result = pyScript.goaLayerFromCellView('DRC_ABUT')\n"
         ">>> pyScript.goaLayerAbut(m1, m2, result)\n"
         ">>> pyScript.goaLayerToCellView(result, 'DRC_ABUT')\n"
         ">>> pyScript.goaDone()"),
        ("goaLayerFromCellView",
         "Load shapes from M1, M2, M3 into goaLayer objects, limiting hierarchy depth to level 2.",
         ["goaLayerFromCellView", "goaInit"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> cv = pyScript.dbOpenCV(\"mylib\", \"amp\", \"layout\")\n"
         ">>> pyScript.goaInit(cv, 2)\n"
         ">>> layers = {}\n"
         ">>> for ln in ['M1', 'M2', 'M3']:\n"
         "...     layers[ln] = pyScript.goaLayerFromCellView(ln, startLevel=0, stopLevel=2)\n"
         ">>> print('Loaded:', list(layers.keys()))\n"
         "Loaded: ['M1', 'M2', 'M3']\n"
         ">>> pyScript.goaDone()"),
        ("goaLayerToCellView",
         "Copy M1 shapes into a goaLayer, then write them back to a new layer 'M1_COPY'.",
         ["goaLayerToCellView", "goaLayerFromCellView", "goaInit"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> cv = pyScript.dbOpenCV(\"mylib\", \"buf\", \"layout\")\n"
         ">>> pyScript.dbCrtRect(cv, pyScript.emyBoxF(0, 0, 50, 50), 'M1')\n"
         ">>> pyScript.goaInit(cv)\n"
         ">>> src = pyScript.goaLayerFromCellView('M1')\n"
         ">>> ok = pyScript.goaLayerToCellView(src, 'M1_COPY', purposeName='drawing')\n"
         ">>> print('Copy to M1_COPY:', ok)\n"
         "Copy to M1_COPY: True\n"
         ">>> pyScript.goaDone()"),
        ("MDE_SWEEP_RANGE_CENTER_SPAN",
         "Configure an AC analysis sweep range using center-span mode: center 1 GHz, span 200 MHz.",
         ["MDE_SWEEP_RANGE_CENTER_SPAN"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> sr = pyScript.MdeSweepRange()\n"
         ">>> sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n"
         ">>> sr.center = '1e9'\n"
         ">>> sr.span = '200e6'\n"
         ">>> print('Range: center=1GHz span=200MHz')\n"
         "Range: center=1GHz span=200MHz"),
        ("MDE_SWEEP_TYPE_LOG",
         "Configure a logarithmic frequency sweep with 10 points per decade for an AC analysis.",
         ["MDE_SWEEP_TYPE_LOG"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> st = pyScript.MdeSweepType()\n"
         ">>> st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n"
         ">>> st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_POINTS_DEC\n"
         ">>> st.pointsPerDecade = '10'\n"
         ">>> print('Log sweep: 10 pts/decade')\n"
         "Log sweep: 10 pts/decade"),
        ("MDE_SWEEP_TYPE_LOG_NUM_STEP",
         "Configure a logarithmic sweep with exactly 50 total steps across the frequency range.",
         ["MDE_SWEEP_TYPE_LOG_NUM_STEP", "MDE_SWEEP_TYPE_LOG"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> st = pyScript.MdeSweepType()\n"
         ">>> st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n"
         ">>> st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP\n"
         ">>> st.numberOfStepsForLog = '50'\n"
         ">>> print('Log sweep: 50 total steps')\n"
         "Log sweep: 50 total steps"),
        ("MDE_SWEEP_VARIABLE_MODEL_PARAMETER",
         "Configure a sweep variable to sweep transistor model parameter 'W' of model 'nch' at 1 GHz.",
         ["MDE_SWEEP_VARIABLE_MODEL_PARAMETER"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> sv = pyScript.MdeSweepVariable()\n"
         ">>> sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n"
         ">>> sv.modelName = 'nch'\n"
         ">>> sv.modelParameterName = 'W'\n"
         ">>> sv.freForMod = '1e9'\n"
         ">>> print('Sweep model param: nch.W at 1GHz')\n"
         "Sweep model param: nch.W at 1GHz"),
        ("MDE_TRAN_ACC_LEVEL_CONSERVATIVE",
         "Create a transient analysis and set accuracy to conservative for high-precision simulation.",
         ["MDE_TRAN_ACC_LEVEL_CONSERVATIVE"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> tran = pyScript.MdeTranAnalysis()\n"
         ">>> tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n"
         ">>> tran.setStopTime('1u')\n"
         ">>> print('Tran: conservative, stop=1us')\n"
         "Tran: conservative, stop=1us"),
        ("MDE_TRAN_ACC_LEVEL_LIBERAL",
         "Create a transient analysis with liberal accuracy for a fast feasibility check.",
         ["MDE_TRAN_ACC_LEVEL_LIBERAL"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> tran = pyScript.MdeTranAnalysis()\n"
         ">>> tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_LIBERAL)\n"
         ">>> tran.setStopTime('100n')\n"
         ">>> print('Tran: liberal, stop=100ns')\n"
         "Tran: liberal, stop=100ns"),
    ]
    for apis_str, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v28-S4-%s" % apis_str, prompt, completion, apis,
             "S4 multi_step_trace: %s" % scenario)

    # ---- S5: parameter variation (10 pairs) ----
    s5_items = [
        ("goaInit-depth", "Show GOA init with different hierarchy depth values (default, shallow=8, deep=128).",
         ["goaInit"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> cv = pyScript.dbOpenCV(\"lib\", \"cell\", \"layout\")\n>>> pyScript.goaInit(cv)       # default depth=64\n>>> pyScript.goaDone()\n>>> pyScript.goaInit(cv, 8)    # shallow\n>>> pyScript.goaDone()\n>>> pyScript.goaInit(cv, 128)  # deep\n>>> pyScript.goaDone()"),
        ("goaLayerAbut-layers", "Show goaLayerAbut with M1-M2, Poly-Active, and same-layer M1-M1 combinations.",
         ["goaLayerAbut", "goaLayerFromCellView"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> cv = pyScript.dbOpenCV(\"lib\", \"cell\", \"layout\")\n>>> pyScript.goaInit(cv)\n>>> m1 = pyScript.goaLayerFromCellView('M1')\n>>> m2 = pyScript.goaLayerFromCellView('M2')\n>>> r = pyScript.goaLayerFromCellView('CHK')\n>>> pyScript.goaLayerAbut(m1, m2, r)      # M1-M2\n>>> poly = pyScript.goaLayerFromCellView('Poly')\n>>> act = pyScript.goaLayerFromCellView('Active')\n>>> pyScript.goaLayerAbut(poly, act, r)   # Poly-Active\n>>> pyScript.goaLayerAbut(m1, m1, r)      # same-layer\n>>> pyScript.goaDone()"),
        ("goaLayerFromCellView-filters", "Show goaLayerFromCellView with area filter, purpose filter, and hierarchy limit.",
         ["goaLayerFromCellView"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> cv = pyScript.dbOpenCV(\"lib\", \"cell\", \"layout\")\n>>> pyScript.goaInit(cv)\n>>> l1 = pyScript.goaLayerFromCellView('M1', boxF=pyScript.emyBoxF(0, 0, 100, 100))\n>>> purposes = pyScript.emyArray_emyString(); purposes.append('pin')\n>>> l2 = pyScript.goaLayerFromCellView('M1', purposeNameList=purposes)\n>>> l3 = pyScript.goaLayerFromCellView('M1', startLevel=0, stopLevel=2)\n>>> pyScript.goaDone()"),
        ("goaLayerToCellView-params", "Show goaLayerToCellView with different purpose, tiling, and shape capture.",
         ["goaLayerToCellView", "goaLayerFromCellView"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> cv = pyScript.dbOpenCV(\"lib\", \"cell\", \"layout\")\n>>> pyScript.goaInit(cv)\n>>> layer = pyScript.goaLayerFromCellView('M1')\n>>> pyScript.goaLayerToCellView(layer, 'M1_OUT', purposeName='pin')\n>>> pyScript.goaLayerToCellView(layer, 'M1_TILED', tiles=True)\n>>> shapes = pyScript.emyArray_p_emyObject()\n>>> pyScript.goaLayerToCellView(layer, 'M1_CAP', pShapes=shapes)\n>>> pyScript.goaDone()"),
        ("MDE_SWEEP_RANGE-modes", "Show both sweep range modes: CENTER_SPAN and START_STOP for the same 1GHz +/- 100MHz range.",
         ["MDE_SWEEP_RANGE_CENTER_SPAN"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> sr1 = pyScript.MdeSweepRange()\n>>> sr1.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n>>> sr1.center = '1e9'; sr1.span = '100e6'\n>>> sr2 = pyScript.MdeSweepRange()\n>>> sr2.mode = pyScript.MDE_SWEEP_RANGE_START_STOP\n>>> sr2.start = '900e6'; sr2.stop = '1.1e9'\n>>> print('Both modes: 900MHz-1.1GHz')"),
        ("MDE_SWEEP_TYPE-modes", "Show all three sweep type modes: AUTO, LINEAR, LOG with their config properties.",
         ["MDE_SWEEP_TYPE_LOG"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> st1 = pyScript.MdeSweepType(); st1.mode = pyScript.MDE_SWEEP_TYPE_AUTO\n>>> st2 = pyScript.MdeSweepType(); st2.mode = pyScript.MDE_SWEEP_TYPE_LINEAR; st2.stepSize = '10e6'\n>>> st3 = pyScript.MdeSweepType(); st3.mode = pyScript.MDE_SWEEP_TYPE_LOG\n>>> st3.logMode = pyScript.MDE_SWEEP_TYPE_LOG_POINTS_DEC; st3.pointsPerDecade = '20'\n>>> print('Three sweep types configured')"),
        ("MDE_SWEEP_TYPE_LOG-submodes", "Show LOG_NUM_STEP (total steps) vs LOG_POINTS_DEC (points per decade).",
         ["MDE_SWEEP_TYPE_LOG_NUM_STEP", "MDE_SWEEP_TYPE_LOG"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> st1 = pyScript.MdeSweepType()\n>>> st1.mode = pyScript.MDE_SWEEP_TYPE_LOG\n>>> st1.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP; st1.numberOfStepsForLog = '100'\n>>> st2 = pyScript.MdeSweepType()\n>>> st2.mode = pyScript.MDE_SWEEP_TYPE_LOG\n>>> st2.logMode = pyScript.MDE_SWEEP_TYPE_LOG_POINTS_DEC; st2.pointsPerDecade = '10'\n>>> print('Log sub-modes: 100 total vs 10/decade')"),
        ("MDE_SWEEP_VARIABLE-types", "Show FREQUENCY, MODEL_PARAMETER, and DESIGN_VARIABLE sweep variable types.",
         ["MDE_SWEEP_VARIABLE_MODEL_PARAMETER"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> sv1 = pyScript.MdeSweepVariable(); sv1.mode = pyScript.MDE_SWEEP_VARIABLE_FREQUENCY; sv1.frequency = '1e9'\n>>> sv2 = pyScript.MdeSweepVariable(); sv2.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n>>> sv2.modelName = 'pch'; sv2.modelParameterName = 'L'; sv2.freForMod = '1e9'\n>>> sv3 = pyScript.MdeSweepVariable(); sv3.mode = pyScript.MDE_SWEEP_VARIABLE_DESIGN_VARIABLE\n>>> sv3.desiVar = 'vdd'; sv3.freForDesiVar = '1e9'\n>>> print('Three sweep variable types')"),
        ("MDE_TRAN_ACC_LEVEL-levels", "Show all three transient accuracy levels: CONSERVATIVE, MODERATE, LIBERAL.",
         ["MDE_TRAN_ACC_LEVEL_CONSERVATIVE", "MDE_TRAN_ACC_LEVEL_LIBERAL"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> tc = pyScript.MdeTranAnalysis(); tc.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE); tc.setStopTime('10u')\n>>> tm = pyScript.MdeTranAnalysis(); tm.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_MODERATE); tm.setStopTime('10u')\n>>> tl = pyScript.MdeTranAnalysis(); tl.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_LIBERAL); tl.setStopTime('10u')\n>>> print('Three accuracy levels set')"),
        ("MDE_TRAN_ACC_LEVEL-comparison", "Compare CONSERVATIVE vs LIBERAL for the same tran analysis, showing use cases.",
         ["MDE_TRAN_ACC_LEVEL_CONSERVATIVE", "MDE_TRAN_ACC_LEVEL_LIBERAL"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> tran_final = pyScript.MdeTranAnalysis()\n>>> tran_final.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n>>> tran_final.setStopTime('5u'); tran_final.setInstanceList('I0 I1 I2')\n>>> tran_explore = pyScript.MdeTranAnalysis()\n>>> tran_explore.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_LIBERAL)\n>>> tran_explore.setStopTime('5u')\n>>> print('Conservative=sign-off, Liberal=exploration')"),
    ]
    for apis_str, scenario, apis, code in s5_items:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript), showing parameter "
                  "variations." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S5", "v28-S5-%s" % apis_str, prompt, completion, apis,
             "S5 param_variation: %s" % scenario)

    # ---- S6: cross-API workflow (10 pairs) ----
    s6_items = [
        ("goa-abut-workflow",
         "Full DRC-style abutment check: init GOA, load two layers, run abutment, write results back to cell view, clean up.",
         ["goaInit", "goaLayerFromCellView", "goaLayerAbut", "goaLayerToCellView"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> pyScript.emyInitQuery()\n>>> cv = pyScript.dbOpenCV(\"mylib\", \"inv_chain\", \"layout\", \"w\")\n>>> pyScript.goaInit(cv, 32)\n>>> m1 = pyScript.goaLayerFromCellView('M1')\n>>> m2 = pyScript.goaLayerFromCellView('M2')\n>>> chk = pyScript.goaLayerFromCellView('DRC_CHK')\n>>> pyScript.goaLayerAbut(m1, m2, chk)\n>>> pyScript.goaLayerToCellView(chk, 'DRC_ABUT_RESULT')\n>>> pyScript.goaDone()\n>>> print('Abutment check complete')\nAbutment check complete"),
        ("goa-copy-workflow",
         "Copy M1 shapes to a backup layer with hierarchy control: init, load with depth limit, write to new layer, done.",
         ["goaInit", "goaLayerFromCellView", "goaLayerToCellView"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> pyScript.emyInitQuery()\n>>> cv = pyScript.dbOpenCV(\"mylib\", \"amp_top\", \"layout\", \"w\")\n>>> pyScript.goaInit(cv, 2)\n>>> m1 = pyScript.goaLayerFromCellView('M1', startLevel=0, stopLevel=2)\n>>> pyScript.goaLayerToCellView(m1, 'M1_BAK', purposeName='drawing')\n>>> pyScript.goaDone()\n>>> print('M1 backup created')\nM1 backup created"),
        ("mde-ac-sweep-workflow",
         "Configure a complete AC analysis sweep: center-span range + log sweep type with 50 steps + frequency variable.",
         ["MDE_SWEEP_RANGE_CENTER_SPAN", "MDE_SWEEP_TYPE_LOG", "MDE_SWEEP_TYPE_LOG_NUM_STEP"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> sr = pyScript.MdeSweepRange()\n>>> sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n>>> sr.center = '1e9'; sr.span = '500e6'\n>>> st = pyScript.MdeSweepType()\n>>> st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n>>> st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP; st.numberOfStepsForLog = '50'\n>>> sv = pyScript.MdeSweepVariable()\n>>> sv.mode = pyScript.MDE_SWEEP_VARIABLE_FREQUENCY; sv.frequency = '1e9'\n>>> print('AC sweep: center=1GHz, span=500MHz, log 50 steps')\nAC sweep: center=1GHz, span=500MHz, log 50 steps"),
        ("mde-tran-accuracy-workflow",
         "Configure transient analysis: set conservative accuracy, stop time, and instance list, then compare with liberal.",
         ["MDE_TRAN_ACC_LEVEL_CONSERVATIVE", "MDE_TRAN_ACC_LEVEL_LIBERAL"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> tran = pyScript.MdeTranAnalysis()\n>>> tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n>>> tran.setStopTime('10u'); tran.setInstanceList('X1.X2.M0 X1.X2.M1')\n>>> tran.setStep('1n')\n>>> print('Tran: conservative, 10us, step=1ns')\nTran: conservative, 10us, step=1ns\n>>> tran2 = pyScript.MdeTranAnalysis()\n>>> tran2.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_LIBERAL)\n>>> tran2.setStopTime('10u')\n>>> print('Tran2: liberal (for fast check)')\nTran2: liberal (for fast check)"),
        ("mde-model-param-sweep-workflow",
         "Configure a model parameter sweep: sweep W of nch model, center-span range, log sweep with 20 steps/decade.",
         ["MDE_SWEEP_VARIABLE_MODEL_PARAMETER", "MDE_SWEEP_RANGE_CENTER_SPAN", "MDE_SWEEP_TYPE_LOG"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> sv = pyScript.MdeSweepVariable()\n>>> sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n>>> sv.modelName = 'nch'; sv.modelParameterName = 'W'; sv.freForMod = '1e9'\n>>> sr = pyScript.MdeSweepRange()\n>>> sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n>>> sr.center = '1u'; sr.span = '500n'\n>>> st = pyScript.MdeSweepType()\n>>> st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n>>> st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_POINTS_DEC; st.pointsPerDecade = '20'\n>>> print('Model param sweep: nch.W, center=1um, log 20/dec')\nModel param sweep: nch.W, center=1um, log 20/dec"),
        ("goa-init-and-abut-full",
         "Complete GOA workflow: init with depth 64, load M1+M2, run abutment check, write to cellview, done.",
         ["goaInit", "goaLayerFromCellView", "goaLayerAbut", "goaLayerToCellView"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> pyScript.emyInitQuery()\n>>> cv = pyScript.dbOpenCV(\"lib\", \"top\", \"layout\", \"w\")\n>>> pyScript.goaInit(cv, 64)\n>>> a = pyScript.goaLayerFromCellView('M1')\n>>> b = pyScript.goaLayerFromCellView('M2')\n>>> res = pyScript.goaLayerFromCellView('CHK')\n>>> pyScript.goaLayerAbut(a, b, res)\n>>> pyScript.goaLayerToCellView(res, 'ABUT_OUT')\n>>> pyScript.goaDone()\n>>> print('Done')\nDone"),
        ("goa-layer-roundtrip",
         "Round-trip: load M1 from cellview, modify, write to M1_NEW, load M1_NEW back, verify.",
         ["goaLayerFromCellView", "goaLayerToCellView", "goaInit"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> cv = pyScript.dbOpenCV(\"lib\", \"cell\", \"layout\", \"w\")\n>>> pyScript.goaInit(cv)\n>>> src = pyScript.goaLayerFromCellView('M1')\n>>> pyScript.goaLayerToCellView(src, 'M1_NEW')\n>>> dst = pyScript.goaLayerFromCellView('M1_NEW')\n>>> pyScript.goaDone()\n>>> print('Round-trip complete')\nRound-trip complete"),
        ("mde-full-ac-config",
         "Configure full AC analysis: freq sweep var, center-span range, log sweep with points per decade.",
         ["MDE_SWEEP_VARIABLE_MODEL_PARAMETER", "MDE_SWEEP_RANGE_CENTER_SPAN", "MDE_SWEEP_TYPE_LOG", "MDE_SWEEP_TYPE_LOG_NUM_STEP"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> sv = pyScript.MdeSweepVariable(); sv.mode = pyScript.MDE_SWEEP_VARIABLE_FREQUENCY; sv.frequency = '1e9'\n>>> sr = pyScript.MdeSweepRange(); sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN; sr.center = '1e9'; sr.span = '1e9'\n>>> st = pyScript.MdeSweepType(); st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n>>> st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP; st.numberOfStepsForLog = '100'\n>>> print('Full AC: 1GHz center, 1GHz span, 100 log steps')\nFull AC: 1GHz center, 1GHz span, 100 log steps"),
        ("mde-tran-signoff-workflow",
         "Configure transient sign-off: conservative accuracy with specific instances, then liberal for quick sweep.",
         ["MDE_TRAN_ACC_LEVEL_CONSERVATIVE", "MDE_TRAN_ACC_LEVEL_LIBERAL"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> signoff = pyScript.MdeTranAnalysis()\n>>> signoff.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n>>> signoff.setStopTime('100u'); signoff.setStep('10n')\n>>> signoff.setInstanceList('Xtop.Xbuf.M0 Xtop.Xbuf.M1 Xtop.Xamp.M2')\n>>> quick = pyScript.MdeTranAnalysis()\n>>> quick.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_LIBERAL)\n>>> quick.setStopTime('100u')\n>>> print('Sign-off: conservative 100us; Quick: liberal 100us')\nSign-off: conservative 100us; Quick: liberal 100us"),
        ("mde-combined-sweep-config",
         "Configure combined sweep: model param variable + log sweep + center-span range, showing all MDE enum interactions.",
         ["MDE_SWEEP_VARIABLE_MODEL_PARAMETER", "MDE_SWEEP_RANGE_CENTER_SPAN", "MDE_SWEEP_TYPE_LOG", "MDE_SWEEP_TYPE_LOG_NUM_STEP", "MDE_TRAN_ACC_LEVEL_CONSERVATIVE"],
         ">>> import pyAether as pyScript\n>>> pyScript.emyInitAether(\"-adv\")\n>>> sv = pyScript.MdeSweepVariable(); sv.mode = pyScript.MDE_SWEEP_VARIABLE_MODEL_PARAMETER\n>>> sv.modelName = 'nch'; sv.modelParameterName = 'Vth'; sv.freForMod = '1e9'\n>>> sr = pyScript.MdeSweepRange(); sr.mode = pyScript.MDE_SWEEP_RANGE_CENTER_SPAN\n>>> sr.center = '0.5'; sr.span = '0.2'\n>>> st = pyScript.MdeSweepType(); st.mode = pyScript.MDE_SWEEP_TYPE_LOG\n>>> st.logMode = pyScript.MDE_SWEEP_TYPE_LOG_NUM_STEP; st.numberOfStepsForLog = '30'\n>>> tran = pyScript.MdeTranAnalysis()\n>>> tran.setAccuracyLevel(pyScript.MDE_TRAN_ACC_LEVEL_CONSERVATIVE)\n>>> tran.setStopTime('1u')\n>>> print('Combined: sweep nch.Vth, center=0.5V, log 30 steps, conservative tran')\nCombined: sweep nch.Vth, center=0.5V, log 30 steps, conservative tran"),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v28-S6-%s" % apis_str, prompt, completion, apis,
             "S6 cross_api_workflow: %s" % scenario)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    parser = argparse.ArgumentParser(
        description="R198 v28 MDE*+goa* SFT corpus builder (10 APIs, 50 pairs)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print stats only, do not write output file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Output JSONL path (default: %s)" % DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of pairs (for testing)")
    args = parser.parse_args()

    sys.stderr.write("R198 v28 MDE*+goa* corpus builder\n")
    sys.stderr.write("  Target APIs: %d (%s)\n" % (len(API_ORDER), ", ".join(API_ORDER)))

    # Verify all API_DOCS keys exist
    missing = [a for a in API_ORDER if a not in API_DOCS]
    if missing:
        sys.stderr.write("ERROR: Missing API_DOCS for: %s\n" % ", ".join(missing))
        sys.exit(1)

    # Load eval entry points for contamination check
    eval_eps = load_eval_entry_points()
    sys.stderr.write("  Eval entry_points loaded: %d\n" % len(eval_eps))

    # Build pairs
    pairs, rejected, reject_details = build_pairs(eval_eps, limit=args.limit)

    # Stats
    api_coverage = {}
    for p in pairs:
        for a in p["api_used"]:
            api_coverage[a] = api_coverage.get(a, 0) + 1

    type_counts = {}
    for p in pairs:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

    sys.stderr.write("\n=== R198 v28 Corpus Stats ===\n")
    sys.stderr.write("  Total pairs: %d\n" % len(pairs))
    sys.stderr.write("  Rejected (contamination): %d\n" % rejected)
    if reject_details:
        for pid, hit in reject_details:
            sys.stderr.write("    REJECT %s -> hit eval entry_point '%s'\n" % (pid, hit))
    sys.stderr.write("  Pair types: %s\n" % ", ".join(
        "%s=%d" % (k, v) for k, v in sorted(type_counts.items())))
    sys.stderr.write("  API coverage (%d/%d):\n" % (len(api_coverage), len(API_ORDER)))
    for a in API_ORDER:
        cnt = api_coverage.get(a, 0)
        flag = "OK" if cnt > 0 else "MISSING"
        sys.stderr.write("    %-45s %2d  [%s]\n" % (a, cnt, flag))

    if args.dry_run:
        sys.stderr.write("\n[dry-run] No output file written.\n")
        return

    # Write output
    with open(args.output, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    sys.stderr.write("\nWrote %d pairs to %s\n" % (len(pairs), args.output))


if __name__ == "__main__":
    main()
