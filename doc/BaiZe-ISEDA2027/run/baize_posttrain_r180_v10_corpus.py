#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r180_v10_corpus.py
R180 -- v10 PyAether SFT corpus: closes the v8/v9 "pin query + pin create" blind spot.

BACKGROUND (R178 inventory + R179 v9):
  v9 (49 pairs / 12 APIs) closed the layout-create blind spot but the v8
  "6 pending API signatures" backlog was only partially resolved: dbCrtNet
  was added as a v9 carry-over (ISOLATE, eval_count=5), but the other 5
  pin-related APIs were still pending. All 5 are SAFE (eval_count==0 against
  the 158-task eval set, grep verified):
    emyFigGetPinName : 0   dbGetPinFigName : 0   emyPinGetNames  : 0
    aeLeCreatePin    : 0   dbFindInst      : 0
  These cover the "pin query / pin create / instance lookup" subdomain which
  v9 did NOT touch. Pin handling is central to schematic+layout tasks (the two
  largest eval scenarios: Layout 64 + Schematic 47 = 111/158 tasks).

v10 FIX: adds the 5 SAFE pin APIs (authoritative signatures via pyAether MCP
get_api_details) with S1 doc->code, S4 multi-step trace, S5 param variation,
S3 multi-API chains, S6 API lookup. Strict pollution scan against all 155 eval
entry_points; every completion checked (red line S5.1).

Usage:
  python3 baize_posttrain_r180_v10_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v10_pin_apis.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

# All 5 are SAFE (eval_count==0, grep-verified against the 158-task eval set).
API_DOCS = {}

API_DOCS["emyFigGetPinName"] = {
    "sig": 'emyFigGetPinName(fig: emyFig) -> emyString',
    "desc": "Gets the figure's pin name.",
    "params": {"fig": "emyFig - the figure, should not be None"},
    "doctest": '>>> import pyAether as pyScript\n>>> res = pyScript.emyFigGetPinName(rect)',
    "category": "Extension / Database Extension", "safety": "SAFE", "eval_count": 0}

API_DOCS["dbGetPinFigName"] = {
    "sig": 'dbGetPinFigName(fig: emyFig) -> emyString',
    "desc": "Returns the pin's name associated with the figure.",
    "params": {"fig": "emyFig - the figure identifier"},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.emyString("test")\n'
                '>>> cell = pyScript.emyString("test")\n'
                '>>> view = pyScript.emyString("layout")\n'
                '>>> cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=view)\n'
                '>>> name = pyScript.emyString("name")\n'
                '>>> figId = pyScript.dbFindInst(cv=cv, name=name)\n'
                '>>> pyScript.dbGetPinFigName(fig=figId)'),
    "category": "Db Commands / Edit Database Commands", "safety": "SAFE", "eval_count": 0}

API_DOCS["emyPinGetNames"] = {
    "sig": 'emyPinGetNames(pin: emyPin, names: emyArray_p_emyShape, ignoreVoltageLabel=False)',
    "desc": "Obtain the name of the pin into the provided names array.",
    "params": {"pin": "emyPin - the pin object",
               "names": "emyArray_p_emyShape - array that receives the pin name",
               "ignoreVoltageLabel": "emyBoolean, optional - skip voltageLabel if True"},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pin = pyScript.aeLeCreatePin(cv, "M1", "pin", "Rectangle",\n'
                '...     [(0, 0), (1, 1)], "P1", "input", ["left"])\n'
                '>>> names = pyScript.emyArray_p_emyShape()\n'
                '>>> pyScript.emyPinGetNames(pin, names)'),
    "category": "Extension / Database Extension", "safety": "SAFE", "eval_count": 0}

API_DOCS["aeLeCreatePin"] = {
    "sig": 'aeLeCreatePin(cv, layerName, purposeName, shape, points, pinName, type, accessDir) -> emyPin',
    "desc": "Create a pin in a layout-type design. Returns the emyPin object.",
    "params": {"cv": "emyDesign - the design to create the pin",
               "layerName": "string - layer name of the pin",
               "purposeName": "emyString - purpose name of the pin",
               "shape": "emyString - Polygon or Rectangle",
               "points": "list - points of the shape",
               "pinName": "string - pin name",
               "type": "string - input/output/inputOutput/switch",
               "accessDir": "vector1D_emyString - access directions (None/top/bottom/right/left)"},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test", "test", "layout")\n'
                '>>> cv = pyScript.aeGetCurDesign()\n'
                '>>> points = [(5, 1), (6, 2)]\n'
                '>>> pyScript.aeLeCreatePin(cv, "M1", "pin", "Rectangle",\n'
                '...     points, "TEST_P4", "switch", ["left"])'),
    "category": "Layout / Create", "safety": "SAFE", "eval_count": 0}

API_DOCS["dbFindInst"] = {
    "sig": 'dbFindInst(cv, name, bVectorInst=False) -> emyInst',
    "desc": "Find an instance by name in a cell view. Returns the instance or None.",
    "params": {"cv": "emyDesign - cell view identifier",
               "name": "emyString - instance name to find",
               "bVectorInst": "bool, optional - search vector instances if True"},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.emyString("test")\n'
                '>>> cell = pyScript.emyString("test")\n'
                '>>> view = pyScript.emyString("layout")\n'
                '>>> cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=view)\n'
                '>>> name = pyScript.emyString("I0")\n'
                '>>> inst = pyScript.dbFindInst(cv=cv, name=name)'),
    "category": "Db Commands / Edit Database Commands", "safety": "SAFE", "eval_count": 0}

API_ORDER = ["emyFigGetPinName", "dbGetPinFigName", "emyPinGetNames",
             "aeLeCreatePin", "dbFindInst"]


def load_eval_entry_points():
    """Load all entry_point strings from the 158-task eval dataset for the
    fingerprint contamination scan. The task bodies themselves are NOT read."""
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


def fingerprint_scan(completion, eval_eps):
    """Return first eval entry_point substring found in completion, else None."""
    for ep in eval_eps:
        if ep and ep in completion:
            return ep
    return None


def _s1_doc_to_code(name, doc):
    """Single API doc->code pair: from official doc, generate a function that
    calls the API with the documented signature."""
    fn = "use_" + name.lower()
    if name == "emyFigGetPinName":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(fig):\n"
            "    return pyScript.emyFigGetPinName(fig)\n") % fn
        prompt = ("Write a Python function %s(fig) that returns the pin name "
                  "of a figure using emyFigGetPinName." % fn)
    elif name == "dbGetPinFigName":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(fig):\n"
            "    return pyScript.dbGetPinFigName(fig=fig)\n") % fn
        prompt = ("Write a Python function %s(fig) that returns the pin name "
                  "associated with a figure using dbGetPinFigName." % fn)
    elif name == "emyPinGetNames":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(pin, ignore_voltage=False):\n"
            "    names = pyScript.emyArray_p_emyShape()\n"
            "    pyScript.emyPinGetNames(pin, names, ignoreVoltageLabel=ignore_voltage)\n"
            "    return names\n") % fn
        prompt = ("Write a Python function %s(pin, ignore_voltage) that fills an "
                  "emyArray_p_emyShape with the pin's names via emyPinGetNames and "
                  "returns it." % fn)
    elif name == "aeLeCreatePin":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, layer, purpose, shape, points, pin_name, pin_type, access_dirs):\n"
            "    pin = pyScript.aeLeCreatePin(cv, layer, purpose, shape, points,\n"
            "        pin_name, pin_type, access_dirs)\n"
            "    return pin\n") % fn
        prompt = ("Write a Python function %s(cv, layer, purpose, shape, points, "
                  "pin_name, pin_type, access_dirs) that creates a layout pin with "
                  "aeLeCreatePin and returns the emyPin object." % fn)
    elif name == "dbFindInst":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, inst_name, vector=False):\n"
            "    name = pyScript.emyString(inst_name)\n"
            "    return pyScript.dbFindInst(cv=cv, name=name, bVectorInst=vector)\n") % fn
        prompt = ("Write a Python function %s(cv, inst_name, vector) that looks up "
                  "an instance by name using dbFindInst and returns it (or None)." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*args, **kwargs):\n"
            "    return pyScript.%s(*args, **kwargs)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S1 doc->code (official API reference)"


def _s4_multi_step(name, doc):
    """Multi-step trace: openCV -> find/inspect/create -> save. Reinforces the
    exact pyScript.<api>(...) call pattern in a realistic multi-step context
    (the R178 anti-hallucination fix)."""
    fn = "trace_" + name.lower()
    if name == "emyFigGetPinName":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, fig):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\")\n"
            "    pname = pyScript.emyFigGetPinName(fig)\n"
            "    pyScript.dbSave(cv)\n"
            "    return pname\n") % fn
        prompt = ("Write a Python function %s(lib, cell, fig) that opens a layout "
                  "cell view, reads the figure's pin name with emyFigGetPinName, "
                  "saves the cell view, and returns the pin name." % fn)
    elif name == "dbGetPinFigName":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, inst_name):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\")\n"
            "    name = pyScript.emyString(inst_name)\n"
            "    figId = pyScript.dbFindInst(cv=cv, name=name)\n"
            "    pname = pyScript.dbGetPinFigName(fig=figId)\n"
            "    pyScript.dbSave(cv)\n"
            "    return pname\n") % fn
        prompt = ("Write a Python function %s(lib, cell, inst_name) that opens a "
                  "layout cell view, finds an instance with dbFindInst, reads its "
                  "pin figure name with dbGetPinFigName, saves the cell view, and "
                  "returns the pin name." % fn)
    elif name == "emyPinGetNames":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, layer, pin_name):\n"
            "    pts = [(0, 0), (1, 1)]\n"
            "    pin = pyScript.aeLeCreatePin(cv, layer, \"pin\", \"Rectangle\",\n"
            "        pts, pin_name, \"input\", [\"left\"])\n"
            "    names = pyScript.emyArray_p_emyShape()\n"
            "    pyScript.emyPinGetNames(pin, names, ignoreVoltageLabel=False)\n"
            "    pyScript.dbSave(cv)\n"
            "    return names\n") % fn
        prompt = ("Write a Python function %s(cv, layer, pin_name) that creates a "
                  "layout pin with aeLeCreatePin, reads its names into an "
                  "emyArray_p_emyShape via emyPinGetNames, saves the cell view, and "
                  "returns the names array." % fn)
    elif name == "aeLeCreatePin":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, layer, pin_name, pin_type):\n"
            "    pts = [(5, 1), (6, 2)]\n"
            "    pin = pyScript.aeLeCreatePin(cv, layer, \"pin\", \"Rectangle\",\n"
            "        pts, pin_name, pin_type, [\"left\"])\n"
            "    pyScript.dbSave(cv)\n"
            "    return pin\n") % fn
        prompt = ("Write a Python function %s(cv, layer, pin_name, pin_type) that "
                  "creates a rectangular layout pin with aeLeCreatePin, saves the "
                  "cell view, and returns the emyPin object." % fn)
    elif name == "dbFindInst":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, inst_name):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\")\n"
            "    name = pyScript.emyString(inst_name)\n"
            "    inst = pyScript.dbFindInst(cv=cv, name=name)\n"
            "    pyScript.dbSave(cv)\n"
            "    return inst\n") % fn
        prompt = ("Write a Python function %s(lib, cell, inst_name) that opens a "
                  "layout cell view, finds an instance by name with dbFindInst, "
                  "saves the cell view, and returns the instance (or None)." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\")\n"
            "    pyScript.dbSave(cv)\n") % fn
        prompt = "Write a Python function %s(lib, cell) stub." % fn
    return prompt, completion, [name], "S4 multi-step trace (openCV->find/create->save)"


def _s5_param_variation(name, doc):
    """Parameter variation: same API, different args, to reinforce the exact
    call pattern across diverse argument shapes."""
    fn = "vary_" + name.lower()
    if name == "emyFigGetPinName":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(figs):\n"
            "    return [pyScript.emyFigGetPinName(f) for f in figs]\n") % fn
        prompt = ("Write a Python function %s(figs) that returns the pin name of "
                  "each figure in a list using emyFigGetPinName." % fn)
    elif name == "dbGetPinFigName":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(figs):\n"
            "    out = []\n"
            "    for f in figs:\n"
            "        out.append(pyScript.dbGetPinFigName(fig=f))\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(figs) that collects the pin figure "
                  "name of each figure using dbGetPinFigName and returns the list." % fn)
    elif name == "emyPinGetNames":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(pins):\n"
            "    results = []\n"
            "    for p in pins:\n"
            "        names = pyScript.emyArray_p_emyShape()\n"
            "        pyScript.emyPinGetNames(p, names, ignoreVoltageLabel=True)\n"
            "        results.append(names)\n"
            "    return results\n") % fn
        prompt = ("Write a Python function %s(pins) that reads the names of each "
                  "pin in a list with emyPinGetNames (ignoring voltage labels) and "
                  "returns the list of name arrays." % fn)
    elif name == "aeLeCreatePin":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, layer, names):\n"
            "    pins = []\n"
            "    for i, nm in enumerate(names):\n"
            "        pts = [(i, 0), (i + 1, 1)]\n"
            "        ptype = \"input\" if i %% 2 == 0 else \"output\"\n"
            "        pins.append(pyScript.aeLeCreatePin(cv, layer, \"pin\",\n"
            "            \"Rectangle\", pts, nm, ptype, [\"left\"]))\n"
            "    return pins\n") % fn
        prompt = ("Write a Python function %s(cv, layer, names) that creates one "
                  "rectangular layout pin per name with aeLeCreatePin, alternating "
                  "input/output type, and returns the list of pins." % fn)
    elif name == "dbFindInst":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, names, vector=False):\n"
            "    found = []\n"
            "    for nm in names:\n"
            "        name = pyScript.emyString(nm)\n"
            "        inst = pyScript.dbFindInst(cv=cv, name=name, bVectorInst=vector)\n"
            "        found.append(inst)\n"
            "    return found\n") % fn
        prompt = ("Write a Python function %s(cv, names, vector) that looks up each "
                  "instance name in a list with dbFindInst and returns the results." % fn)
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
        hit = fingerprint_scan(completion, eval_eps)
        if hit:
            rejected += 1
            reject_details.append({"id": cid, "type": ptype, "hit": hit})
            return
        pairs.append({
            "id": cid, "type": ptype, "prompt": prompt,
            "completion": completion, "api_used": api_used,
            "contamination_check": "PASS", "note": note,
        })

    # ---- S1 doc->code (one per API) ----
    for name in API_ORDER:
        doc = API_DOCS[name]
        prompt, completion, apis, note = _s1_doc_to_code(name, doc)
        _add("S1", "s1_" + name, prompt, completion, apis, note)

    # ---- S4 multi-step trace (one per API) ----
    for name in API_ORDER:
        doc = API_DOCS[name]
        prompt, completion, apis, note = _s4_multi_step(name, doc)
        _add("S4", "s4_" + name, prompt, completion, apis, note)

    # ---- S5 parameter variation (one per API) ----
    for name in API_ORDER:
        doc = API_DOCS[name]
        prompt, completion, apis, note = _s5_param_variation(name, doc)
        _add("S5", "s5_" + name, prompt, completion, apis, note)

    # ---- S3 multi-API chains (pin query + create + instance lookup) ----
    chains = [
        ("chain_findinst_getpinname",
         "Write a Python function find_inst_pin_name(lib, cell, inst_name) that "
         "opens a layout cell view, finds an instance with dbFindInst, reads its "
         "pin figure name with dbGetPinFigName, and returns the pin name.",
         ["dbFindInst", "dbGetPinFigName"],
         ("import pyAether as pyScript\n\n"
          "def find_inst_pin_name(lib, cell, inst_name):\n"
          "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\")\n"
          "    name = pyScript.emyString(inst_name)\n"
          "    figId = pyScript.dbFindInst(cv=cv, name=name)\n"
          "    return pyScript.dbGetPinFigName(fig=figId)\n")),
        ("chain_createpin_getnames",
         "Write a Python function make_pin_and_read_names(cv, layer, pin_name) "
         "that creates a layout pin with aeLeCreatePin, then reads its names with "
         "emyPinGetNames, and returns the names array.",
         ["aeLeCreatePin", "emyPinGetNames"],
         ("import pyAether as pyScript\n\n"
          "def make_pin_and_read_names(cv, layer, pin_name):\n"
          "    pts = [(0, 0), (1, 1)]\n"
          "    pin = pyScript.aeLeCreatePin(cv, layer, \"pin\", \"Rectangle\",\n"
          "        pts, pin_name, \"input\", [\"left\"])\n"
          "    names = pyScript.emyArray_p_emyShape()\n"
          "    pyScript.emyPinGetNames(pin, names, ignoreVoltageLabel=False)\n"
          "    return names\n")),
        ("chain_findinst_figname_pinname",
         "Write a Python function inst_pin_names(lib, cell, inst_name) that finds "
         "an instance with dbFindInst, gets its pin figure name with "
         "dbGetPinFigName, then the figure pin name with emyFigGetPinName, and "
         "returns both names.",
         ["dbFindInst", "dbGetPinFigName", "emyFigGetPinName"],
         ("import pyAether as pyScript\n\n"
          "def inst_pin_names(lib, cell, inst_name):\n"
          "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\")\n"
          "    name = pyScript.emyString(inst_name)\n"
          "    figId = pyScript.dbFindInst(cv=cv, name=name)\n"
          "    figname = pyScript.dbGetPinFigName(fig=figId)\n"
          "    pinname = pyScript.emyFigGetPinName(figId)\n"
          "    return figname, pinname\n")),
        ("chain_createpin_vary_types",
         "Write a Python function make_pins_multi_type(cv, layer, names) that "
         "creates one layout pin per name with aeLeCreatePin, cycling pin types "
         "input/output/inputOutput/switch, and returns the list of pins.",
         ["aeLeCreatePin"],
         ("import pyAether as pyScript\n\n"
          "def make_pins_multi_type(cv, layer, names):\n"
          "    types = [\"input\", \"output\", \"inputOutput\", \"switch\"]\n"
          "    pins = []\n"
          "    for i, nm in enumerate(names):\n"
          "        pts = [(i, 0), (i + 1, 1)]\n"
          "        pins.append(pyScript.aeLeCreatePin(cv, layer, \"pin\",\n"
          "            \"Rectangle\", pts, nm, types[i %% len(types)], [\"left\"]))\n"
          "    return pins\n")),
    ]
    for cid, prompt, api_used, completion in chains:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")

    # ---- S6 API lookup (intent -> API -> minimal usage) ----
    lookups = [
        ("get the pin name of a figure", "emyFigGetPinName",
         'pname = pyScript.emyFigGetPinName(fig)'),
        ("get the pin name associated with a figure", "dbGetPinFigName",
         'pname = pyScript.dbGetPinFigName(fig=figId)'),
        ("read a pin's names into an array", "emyPinGetNames",
         'names = pyScript.emyArray_p_emyShape()\npyScript.emyPinGetNames(pin, names, ignoreVoltageLabel=False)'),
        ("create a pin in a layout design", "aeLeCreatePin",
         'pin = pyScript.aeLeCreatePin(cv, "M1", "pin", "Rectangle", [(5, 1), (6, 2)], "P1", "input", ["left"])'),
        ("find an instance by name in a cell view", "dbFindInst",
         'name = pyScript.emyString("I0")\ninst = pyScript.dbFindInst(cv=cv, name=name)'),
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
        "report_id": "R180",
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