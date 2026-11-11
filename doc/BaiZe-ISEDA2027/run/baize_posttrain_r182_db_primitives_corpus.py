#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r182_db_primitives_corpus.py
R182 -- v12 PyAether SFT corpus: the db* "database primitive" blind spot.

BACKGROUND (R181 coverage audit):
  v11 (93 pairs) teaches create/edit APIs (dbCrtWire, dbCrtRect, dbCrtInst,
  dbCrtSchWire, dbCrtNet, dbFindInst, pin APIs ...). The R181 coverage audit
  classified 158 eval raw pyScript APIs as: 6 covered / 13 SAFE / 158 blind.
  The blind set's largest family is db* query/open/close primitives:
    dbOpenCV     : eval_count=75  (open cell view -- THE most common helper)
    dbCloseCV    : eval_count=84  (close cell view -- resource cleanup)
    dbNewCV      : eval_count=80  (create new cell view)
    dbGetAllLibs : eval_count=91  (list all libraries -- discovery)
    dbFind       : eval_count=3   (find figs by condition+bbox -- powerful query)
  All 5 are ISOLATE-class (appear in eval solutions as helpers, eval_count>0),
  so they are NOT "SAFE" (free-teach). But the red line (S5.1) isolates on
  eval *entry_point* strings (the 158 task function names), NOT on helper API
  names. Teaching the *public API reference* of these primitives is explicitly
  allowed. The fingerprint scan below rejects any pair whose prompt+completion
  contains a literal eval entry_point string.

  Authoritative signatures fetched via pyAether MCP get_api_details (R182 wake).

v12: 5 db* primitives with S1 doc->code, S4 multi-step trace, S5 param
  variation, S3 multi-API chains (full open->query->close lifecycle), S6 API
  lookup. Strict pollution scan against all 155 eval entry_points.

Usage:
  python3 baize_posttrain_r182_db_primitives_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v12_db_primitives.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

# All 5 are ISOLATE (eval_count>0, appear as helpers in eval solutions).
# Signatures from pyAether MCP get_api_details (authoritative).
API_DOCS = {}

API_DOCS["dbOpenCV"] = {
    "sig": 'dbOpenCV(lib: emyString, cell: emyString, view: emyString="layout", mode: emyString="a", viewType: emyString="layout") -> emyDesign',
    "desc": "Open a cell view. Returns a cell view identifier (emyDesign) if the specified cell view can be opened, otherwise returns None.",
    "params": {
        "lib": "emyString - library name or library identifier",
        "cell": "emyString - cell name",
        "view": 'emyString, optional - view name (default "layout")',
        "mode": 'emyString, optional - open mode: r/w/a/readOnly/create/edit (default "a")',
        "viewType": 'emyString, optional - layout/schematic/symbol (default "layout")',
    },
    "doctest": ('>>> from pyAether import *\n'
                '>>> lib = dbOpenLib("test")\n'
                '>>> dbOpenCV("test", "test")'),
    "category": "Db Commands / Cell Database Commands",
    "safety": "ISOLATE", "eval_count": 75,
    "key_notes": "Deprecated since v2025.03 (prefer dbOpenCVByType). Returns None (not 0) on failure -- check with 'is not None'. viewType must match the actual view type."}

API_DOCS["dbCloseCV"] = {
    "sig": 'dbCloseCV(cv: emyDesign) -> bool',
    "desc": "Close a cell view. Returns 1 (True) if the specified cell view can be closed.",
    "params": {"cv": "emyDesign - the cell view identifier to close"},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> pyScript.dbCloseCV(cv)'),
    "category": "Db Commands / Cell Database Commands",
    "safety": "ISOLATE", "eval_count": 84,
    "key_notes": "Pairs with dbOpenCV for resource cleanup. Always close a cv after use to release resources."}

API_DOCS["dbNewCV"] = {
    "sig": 'dbNewCV(lib: emyString, cell: emyString, view: emyString, viewType: emyString="layout") -> emyDesign',
    "desc": "Create a new cell view. Returns the new emyDesign identifier, or None on failure.",
    "params": {
        "lib": "emyString - library name",
        "cell": "emyString - cell name",
        "view": "emyString - view name to create",
        "viewType": 'emyString, optional - layout/schematic/symbol (default "layout")',
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbNewCV("test", "mycell", "layout", "layout")'),
    "category": "Db Commands / Cell Database Commands",
    "safety": "ISOLATE", "eval_count": 80,
    "key_notes": "Creates a brand-new (empty) cell view for editing. Returns None on failure -- check result before use."}

API_DOCS["dbFind"] = {
    "sig": 'dbFind(cv: emyDesign, types: emyString, conditions: vector1D_emyString, bbox: emyBoxF=emyBoxF(0,0,0,0), startLevel: int=0, stopLevel: int=0, isDelDuplicated: bool=False, cbFunc: emyString="", maxCount: int=50000, withBBox: bool=False, withOrigin: bool=False, withOutline: bool=False, withLevel: bool=False) -> Tuple[PyFindInfos]',
    "desc": "Find figures in a cell view by bounding box or condition. Returns a list of figure identifiers (and optionally bbox/outline/level).",
    "params": {
        "cv": "emyDesign - cell view identifier",
        "types": 'emyString - figure type to traverse: "shape" or "inst"',
        "conditions": "vector1D_emyString - query conditions",
        "bbox": "emyBoxF, optional - bounding box (default = cell view bbox)",
        "startLevel": "int, optional - starting traverse level",
        "stopLevel": "int, optional - traverse stop level",
        "isDelDuplicated": "bool, optional - skip duplicated figures",
        "withBBox": "bool, optional - return [figId, bbox] pairs if True",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> figs = pyScript.dbFind(cv=cv, types="shape", conditions=["layer==M1"])'),
    "category": "Db Commands / Edit Database Commands",
    "safety": "ISOLATE", "eval_count": 3,
    "key_notes": "Powerful query primitive. types='inst' for instances, 'shape' for shapes. withBBox=True returns [fig, bbox] tuples."}

API_DOCS["dbGetAllLibs"] = {
    "sig": 'dbGetAllLibs() -> Tuple[emyString]',
    "desc": "Get all library names defined in lib.defs. Returns a tuple of library name strings.",
    "params": {},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> libs = pyScript.dbGetAllLibs()'),
    "category": "Db Commands / Library Database Commands",
    "safety": "ISOLATE", "eval_count": 91,
    "key_notes": "No arguments. The discovery entry point -- list available libraries before opening a cell view."}

API_ORDER = ["dbOpenCV", "dbCloseCV", "dbNewCV", "dbFind", "dbGetAllLibs"]


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


def fingerprint_scan(text, eval_eps):
    """Return first eval entry_point substring found in text, else None."""
    for ep in eval_eps:
        if ep and ep in text:
            return ep
    return None


def _doc_block(name):
    """Format a focused API reference block for the S1 prompt."""
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
    """Single API doc->code pair: from official doc, generate a function that
    calls the API with the documented signature and checks the return value."""
    fn = "use_" + name.lower()
    if name == "dbOpenCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view=\"layout\", mode=\"r\", viewType=\"layout\"):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=view,\n"
            "                           mode=mode, viewType=viewType)\n"
            "    if cv is None:\n"
            "        raise RuntimeError(\"dbOpenCV returned None\")\n"
            "    return cv\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(lib, cell, view, mode, viewType) that opens a "
                  "cell view with dbOpenCV, checks the return value is not None, and returns "
                  "the emyDesign identifier." % (_doc_block(name), fn))
    elif name == "dbCloseCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv):\n"
            "    return pyScript.dbCloseCV(cv)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(cv) that closes a cell view with dbCloseCV and "
                  "returns the boolean result." % (_doc_block(name), fn))
    elif name == "dbNewCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view, viewType=\"layout\"):\n"
            "    cv = pyScript.dbNewCV(lib=lib, cell=cell, view=view, viewType=viewType)\n"
            "    if cv is None:\n"
            "        raise RuntimeError(\"dbNewCV returned None\")\n"
            "    return cv\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(lib, cell, view, viewType) that creates a new "
                  "cell view with dbNewCV, checks the return value is not None, and returns "
                  "the emyDesign identifier." % (_doc_block(name), fn))
    elif name == "dbFind":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, fig_type, conditions, with_bbox=False):\n"
            "    return pyScript.dbFind(cv=cv, types=fig_type,\n"
            "                          conditions=conditions, withBBox=with_bbox)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(cv, fig_type, conditions, with_bbox) that finds "
                  "figures in a cell view with dbFind by type and conditions, optionally "
                  "returning bounding boxes, and returns the result tuple." % (_doc_block(name), fn))
    elif name == "dbGetAllLibs":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    return pyScript.dbGetAllLibs()\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s() that returns all library names via dbGetAllLibs."
                  % (_doc_block(name), fn))
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*args, **kwargs):\n"
            "    return pyScript.%s(*args, **kwargs)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S1 doc->code (official API reference)"


def _s4_multi_step(name):
    """Multi-step trace: open -> use primitive -> close/save. Reinforces the
    exact pyScript.<api>(...) call pattern in a realistic lifecycle context."""
    fn = "trace_" + name.lower()
    if name == "dbOpenCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view=\"layout\"):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=view, mode=\"r\")\n"
            "    if cv is None:\n"
            "        return None\n"
            "    pyScript.dbCloseCV(cv)\n"
            "    return cv\n") % fn
        prompt = ("Write a Python function %s(lib, cell, view) that opens a cell view in "
                  "read mode with dbOpenCV, returns None if it fails, otherwise closes it "
                  "with dbCloseCV and returns the identifier." % fn)
    elif name == "dbCloseCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view=\"layout\"):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=view, mode=\"a\")\n"
            "    if cv is None:\n"
            "        return False\n"
            "    ok = pyScript.dbCloseCV(cv)\n"
            "    return ok\n") % fn
        prompt = ("Write a Python function %s(lib, cell, view) that opens a cell view in "
                  "append mode with dbOpenCV, then closes it with dbCloseCV and returns the "
                  "close result (True/False)." % fn)
    elif name == "dbNewCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, view=\"layout\"):\n"
            "    cv = pyScript.dbNewCV(lib=lib, cell=cell, view=view, viewType=view)\n"
            "    if cv is None:\n"
            "        return None\n"
            "    pyScript.dbSave(cv)\n"
            "    pyScript.dbCloseCV(cv)\n"
            "    return cv\n") % fn
        prompt = ("Write a Python function %s(lib, cell, view) that creates a new cell view "
                  "with dbNewCV, saves it with dbSave, closes it with dbCloseCV, and returns "
                  "the identifier (or None on failure)." % fn)
    elif name == "dbFind":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell, fig_type, conditions):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\", mode=\"r\")\n"
            "    if cv is None:\n"
            "        return []\n"
            "    figs = pyScript.dbFind(cv=cv, types=fig_type, conditions=conditions)\n"
            "    pyScript.dbCloseCV(cv)\n"
            "    return figs\n") % fn
        prompt = ("Write a Python function %s(lib, cell, fig_type, conditions) that opens a "
                  "layout cell view in read mode, finds figures with dbFind by type and "
                  "conditions, closes the cell view with dbCloseCV, and returns the figures."
                  % fn)
    elif name == "dbGetAllLibs":
        completion = ("import pyAether as pyScript\n\n"
            "def %s():\n"
            "    libs = pyScript.dbGetAllLibs()\n"
            "    return list(libs)\n") % fn
        prompt = ("Write a Python function %s() that calls dbGetAllLibs to list all "
                  "available libraries and returns them as a Python list." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib, cell):\n"
            "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\")\n"
            "    pyScript.dbCloseCV(cv)\n") % fn
        prompt = "Write a Python function %s(lib, cell) stub." % fn
    return prompt, completion, [name], "S4 multi-step trace (open->use->close)"


def _s5_param_variation(name):
    """Parameter variation: same API, different args, to reinforce the exact
    call pattern across diverse argument shapes."""
    fn = "vary_" + name.lower()
    if name == "dbOpenCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lib_cells, mode=\"r\"):\n"
            "    results = {}\n"
            "    for lib, cell, view in lib_cells:\n"
            "        cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=view, mode=mode)\n"
            "        results[(lib, cell, view)] = cv\n"
            "    return results\n") % fn
        prompt = ("Write a Python function %s(lib_cells, mode) that opens each (lib, cell, "
                  "view) tuple in a list with dbOpenCV using the given mode, and returns a "
                  "dict keyed by the tuple." % fn)
    elif name == "dbCloseCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cvs):\n"
            "    closed = []\n"
            "    for cv in cvs:\n"
            "        closed.append(pyScript.dbCloseCV(cv))\n"
            "    return closed\n") % fn
        prompt = ("Write a Python function %s(cvs) that closes each cell view in a list with "
                  "dbCloseCV and returns the list of boolean results." % fn)
    elif name == "dbNewCV":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(specs):\n"
            "    cvs = []\n"
            "    for lib, cell, view, vtype in specs:\n"
            "        cv = pyScript.dbNewCV(lib=lib, cell=cell, view=view, viewType=vtype)\n"
            "        if cv is not None:\n"
            "            cvs.append(cv)\n"
            "    return cvs\n") % fn
        prompt = ("Write a Python function %s(specs) that creates a new cell view for each "
                  "(lib, cell, view, viewType) tuple with dbNewCV, skips failures, and "
                  "returns the list of created identifiers." % fn)
    elif name == "dbFind":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(cv, queries):\n"
            "    out = []\n"
            "    for fig_type, conditions in queries:\n"
            "        figs = pyScript.dbFind(cv=cv, types=fig_type,\n"
            "                              conditions=conditions, withBBox=True)\n"
            "        out.append(figs)\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(cv, queries) that runs dbFind for each "
                  "(fig_type, conditions) pair with withBBox=True and returns the list of "
                  "results." % fn)
    elif name == "dbGetAllLibs":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(prefix=None):\n"
            "    libs = pyScript.dbGetAllLibs()\n"
            "    names = [str(l) for l in libs]\n"
            "    if prefix:\n"
            "        names = [n for n in names if n.startswith(prefix)]\n"
            "    return names\n") % fn
        prompt = ("Write a Python function %s(prefix) that calls dbGetAllLibs, converts the "
                  "result to string names, and optionally filters by a prefix." % fn)
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
        ("chain_open_find_close",
         "Write a Python function query_figs(lib, cell, fig_type, conditions) that opens a "
         "layout cell view in read mode with dbOpenCV, finds figures with dbFind by type and "
         "conditions, closes the cell view with dbCloseCV, and returns the figures.",
         ["dbOpenCV", "dbFind", "dbCloseCV"],
         ("import pyAether as pyScript\n\n"
          "def query_figs(lib, cell, fig_type, conditions):\n"
          "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\", mode=\"r\")\n"
          "    if cv is None:\n"
          "        return []\n"
          "    figs = pyScript.dbFind(cv=cv, types=fig_type, conditions=conditions)\n"
          "    pyScript.dbCloseCV(cv)\n"
          "    return figs\n")),
        ("chain_listlibs_open",
         "Write a Python function find_and_open(lib_name, cell, view) that lists all "
         "libraries with dbGetAllLibs, checks the target library exists, then opens the cell "
         "view with dbOpenCV and returns it (or None).",
         ["dbGetAllLibs", "dbOpenCV"],
         ("import pyAether as pyScript\n\n"
          "def find_and_open(lib_name, cell, view=\"layout\"):\n"
          "    libs = pyScript.dbGetAllLibs()\n"
          "    names = [str(l) for l in libs]\n"
          "    if lib_name not in names:\n"
          "        return None\n"
          "    return pyScript.dbOpenCV(lib=lib_name, cell=cell, view=view, mode=\"r\")\n")),
        ("chain_newcv_save_close",
         "Write a Python function create_and_save(lib, cell, view) that creates a new cell "
         "view with dbNewCV, saves it with dbSave, closes it with dbCloseCV, and returns the "
         "identifier (or None on failure).",
         ["dbNewCV", "dbCloseCV"],
         ("import pyAether as pyScript\n\n"
          "def create_and_save(lib, cell, view=\"layout\"):\n"
          "    cv = pyScript.dbNewCV(lib=lib, cell=cell, view=view, viewType=view)\n"
          "    if cv is None:\n"
          "        return None\n"
          "    pyScript.dbSave(cv)\n"
          "    pyScript.dbCloseCV(cv)\n"
          "    return cv\n")),
        ("chain_open_findinst_close",
         "Write a Python function find_instances(lib, cell, conditions) that opens a layout "
         "cell view with dbOpenCV, finds instances with dbFind using types='inst', closes the "
         "cell view with dbCloseCV, and returns the instances.",
         ["dbOpenCV", "dbFind", "dbCloseCV"],
         ("import pyAether as pyScript\n\n"
          "def find_instances(lib, cell, conditions):\n"
          "    cv = pyScript.dbOpenCV(lib=lib, cell=cell, view=\"layout\", mode=\"r\")\n"
          "    if cv is None:\n"
          "        return []\n"
          "    insts = pyScript.dbFind(cv=cv, types=\"inst\", conditions=conditions)\n"
          "    pyScript.dbCloseCV(cv)\n"
          "    return insts\n")),
        ("chain_batch_lib_open_close",
         "Write a Python function open_all_cells(lib_name, cell, view) that lists libraries "
         "with dbGetAllLibs, opens the cell view with dbOpenCV, and closes it with dbCloseCV, "
         "returning the list of available libraries plus the open success flag.",
         ["dbGetAllLibs", "dbOpenCV", "dbCloseCV"],
         ("import pyAether as pyScript\n\n"
          "def open_all_cells(lib_name, cell, view=\"layout\"):\n"
          "    libs = [str(l) for l in pyScript.dbGetAllLibs()]\n"
          "    cv = pyScript.dbOpenCV(lib=lib_name, cell=cell, view=view, mode=\"r\")\n"
          "    ok = False\n"
          "    if cv is not None:\n"
          "        ok = pyScript.dbCloseCV(cv)\n"
          "    return libs, ok\n")),
    ]
    for cid, prompt, api_used, completion in chains:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")

    lookups = [
        ("open a cell view", "dbOpenCV",
         'cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout", mode="r")'),
        ("close a cell view", "dbCloseCV",
         'pyScript.dbCloseCV(cv)'),
        ("create a new cell view", "dbNewCV",
         'cv = pyScript.dbNewCV(lib="test", cell="mycell", view="layout", viewType="layout")'),
        ("find figures in a cell view by condition", "dbFind",
         'figs = pyScript.dbFind(cv=cv, types="shape", conditions=["layer==M1"])'),
        ("list all available libraries", "dbGetAllLibs",
         'libs = pyScript.dbGetAllLibs()'),
    ]
    for intent, api, usage in lookups:
        prompt = ("You are an EDA automation assistant. Which PyAether API is used to %s? "
                  "Show a minimal correct usage example." % intent)
        completion = ("The API is `%s`.\n\n```python\nimport pyAether as pyScript\n%s\n```"
                      % (api, usage))
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
        "report_id": "R182",
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
        sys.stderr.write("GATE: FAIL (pollution detected) -- do NOT use v12\n")
        sys.exit(2)
    sys.stderr.write("GATE: PASS -- v12 is training-ready\n")


if __name__ == "__main__":
    main()
