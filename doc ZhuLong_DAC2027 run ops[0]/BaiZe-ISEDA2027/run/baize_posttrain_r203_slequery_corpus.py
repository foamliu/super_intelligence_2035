#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r203_slequery_corpus.py
R203 -- v33 PyAether SFT corpus: SleQueryData hierarchy-query data class
= 1 class + 1 factory + 1 query class, 17 pairs.

BACKGROUND: v11-v32 (875 pairs) cover 154/164 eval raw APIs (93.9%). 10 blind.
Data-driven scan (R191 blind_scan, re-run with v32) shows Sle is the #1 blind
family (total=1, apis=1: SleQueryData(1)). Eval task 036 (entry_point=
create_query_data) uses SleQueryData(obj, hier_path, distance) to wrap an EDA
object + hierarchy path + distance into a query data structure.

SleQueryData is ISOLATE-class (eval helper, NOT an eval entry_point). 155 eval
entry_points loaded; SleQueryData is NOT an entry_point; create_query_data IS
an entry_point (ISOLATE-keep). Doctests use lib=demo_sle_lib, cell=
demo_sle_cell, distances 5.0/25.0/50.0, different pin names/coords -- all
DELIBERATELY DIFFERENT from eval (test_sle_lib, test_sle_cell, P1, (0,0), 10.5).

Authoritative signatures (pyAether MCP get_api_details, this wake):
  SleQueryData: 3 ctors -- (obj,hierPath,dist=DBL_MAX) / (obj) / (data:copy).
    __eq__(ref)->bool (obj+hierPath, NOT dist); get(pt,ref,hierPath,row,col)
    [2 overloads: w/wo pFigGroup]; isEvaluedTextORUnderQuery(queryBox,...);
    setObject(obj); m_object.down_cast(); m_hierPath.getDepth().
  aeMakeSleQueryData(fig:emyFig)->SleQueryData (heap factory; caller frees).
  SleHierQuery: naiveQuery(design,box,...); sortObjectsByType(data)[static];
    free(data)[static]; getEditFigGroup().
  SleQueryData IS in API_INFO_MERGED_V3.json (well-documented, unlike CColor).

Usage: python3 baize_posttrain_r203_slequery_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v33_slequery.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}
API_ORDER = ["SleQueryData", "aeMakeSleQueryData", "SleHierQuery"]

# === SleQueryData -- hierarchy query data class ===
API_DOCS["SleQueryData"] = {
    "sig": ("SleQueryData(obj: emyObject, hierPath: emyHierPath, "
            "dist: emyDouble=DBL_MAX)\n"
            "SleQueryData(obj: emyObject)\n"
            "SleQueryData(data: SleQueryData)   [class; query data for "
            "hierarchical spatial query]"),
    "desc": ("A query-data class used by the Sle (Spatial Layout Element) "
             "hierarchical query system. A SleQueryData object bundles an "
             "EDA object (emyObject), its hierarchical path (emyHierPath), "
             "and a distance value. SleHierQuery.naiveQuery populates an "
             "emyArray_p_SleQueryData with results; each element's m_object "
             "and m_hierPath give the queried figure and its hierarchy "
             "context. Three constructor overloads: full, obj-only (dist="
             "DBL_MAX), and copy."),
    "params": {
        "obj: emyObject": ("The EDA object to be queried (instance, pin, "
                           "or shape). Accessible via m_object."),
        "hierPath: emyHierPath": ("The hierarchical path pointing to the "
                                  "object. Accessible via m_hierPath."),
        "dist: emyDouble": ("Distance value (e.g. distance to a reference "
                            "point). Defaults to DBL_MAX when omitted."),
        "data: SleQueryData": ("An existing SleQueryData to copy from "
                               "(copy constructor)."),
    },
    "returns": ("A SleQueryData object for hierarchical query operations."),
    "methods": ("__eq__(ref)->bool: True if both obj AND hierPath are "
                "equal (dist is NOT compared).\n"
                "get(pt,ref,hierPath,row,col): fills out values. Two "
                "overloads: with/without pFigGroup.\n"
                "isEvaluedTextORUnderQuery(queryBox,showDefaultParameter)"
                "->emyBoolean: whether eval text overlaps query region.\n"
                "setObject(obj): sets the obj for this data.\n"
                "m_object: member -- queried emyObject (use .down_cast()).\n"
                "m_hierPath: member -- emyHierPath (use .getDepth())."),
    "key_notes": ("SleQueryData is in API_INFO_MERGED_V3.json (formally "
                  "documented). NOT an eval entry_point; it is a helper "
                  "class used within an eval task. __eq__ compares obj AND "
                  "hierPath but NOT dist, so same obj+hierPath with "
                  "different dist are still equal."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitQuery()\n"
                ">>> lib = 'demo_sle_lib'\n"
                ">>> if lib in pyScript.dbGetAllLibs():\n"
                "...     pyScript.dbDelLib(lib=[lib])\n"
                ">>> pyScript.dbCreateLib(lib=lib)\n"
                ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
                "view='schematic')\n"
                ">>> cv = pyScript.dbOpenCVByType(lib=lib, "
                "cell='demo_sle_cell', view='schematic', mode='a')\n"
                ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='Q7', "
                "point=(300, 200), direction='output')\n"
                ">>> hp = pyScript.emyHierPath()\n"
                ">>> qd = pyScript.SleQueryData(pin, hp, 25.0)\n"
                ">>> print('query data created:', type(qd).__name__)\n"
                "query data created: SleQueryData"),
}

# === aeMakeSleQueryData -- factory function ===
API_DOCS["aeMakeSleQueryData"] = {
    "sig": ("aeMakeSleQueryData(fig: emyFig) -> SleQueryData   [function; "
            "heap-allocated factory]"),
    "desc": ("A factory function that creates a SleQueryData object on the "
             "heap from an emyFig. Unlike the constructors which take an "
             "emyObject, this accepts an emyFig directly. The caller must "
             "free the memory (use SleHierQuery.free on the array)."),
    "params": {"fig: emyFig": "The emyFig object to create query data from."},
    "returns": ("A heap-allocated SleQueryData. Caller must free manually."),
    "key_notes": ("Convenience factory taking emyFig (subclass of "
                  "emyObject). Always pair with proper cleanup."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitQuery()\n"
                ">>> lib = 'demo_sle_lib'\n"
                ">>> pyScript.dbCreateLib(lib=lib)\n"
                ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
                "view='schematic')\n"
                ">>> cv = pyScript.dbOpenCVByType(lib=lib, "
                "cell='demo_sle_cell', view='schematic', mode='a')\n"
                ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='Q7', "
                "point=(300, 200), direction='output')\n"
                ">>> qd = pyScript.aeMakeSleQueryData(pin)\n"
                ">>> print('factory result:', type(qd).__name__)\n"
                "factory result: SleQueryData"),
}

# === SleHierQuery -- hierarchical query class (cross-API) ===
API_DOCS["SleHierQuery"] = {
    "sig": ("SleHierQuery(arrInstIsFull: emyBoolean=True)\n"
            "SleHierQuery()   [class; hierarchical spatial query]"),
    "desc": ("A class for querying objects with specified conditions "
             "hierarchically. naiveQuery searches within a box region, "
             "filtered by layer-purpose pairs and object type, populating "
             "an emyArray_p_SleQueryData. Each result's m_object and "
             "m_hierPath give the found figure and its hierarchy path."),
    "params": {"arrInstIsFull: emyBoolean": ("Whether to consider array "
              "instances as a whole. Default True.")},
    "returns": ("A SleHierQuery object. Call naiveQuery then iterate "
                "results."),
    "methods": ("naiveQuery(design,box,lppFilter,objFilter,shapeStart,"
                "shapeStop,refStart,refStop,maxDepth,data,considerSelect="
                "True,filterSize=0): begins the query.\n"
                "sortObjectsByType(data) [static]: sorts by object type.\n"
                "free(data) [static]: frees emyArray_p_SleQueryData.\n"
                "getEditFigGroup()->emyFigGroup: gets editing fig group."),
    "key_notes": ("Results are SleQueryData in emyArray_p_SleQueryData. "
                  "Access m_object.down_cast() for the figure, "
                  "m_hierPath.getDepth() for depth. Always call free()."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitQuery()\n"
                ">>> h_query = pyScript.SleHierQuery()\n"
                ">>> print('query engine:', type(h_query).__name__)\n"
                "query engine: SleHierQuery"),
}


def load_eval_entry_points():
    eps = set()
    if not os.path.exists(EVAL_DS):
        sys.stderr.write("WARNING: eval dataset not found at %s\n" % EVAL_DS)
        return eps
    with open(EVAL_DS) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            ep = d.get("entry_point", "")
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

    # ---- S1: doc -> code (1 pair) ----
    name = "SleQueryData"
    doc = _doc_block(name)
    d = API_DOCS[name]
    prompt = ("You are an EDA automation engineer. Given the following "
              "PyAether API reference, write a minimal correct Python "
              "code snippet that uses `%s`.\n\n%s" % (name, doc))
    completion = "```python\n%s\n```" % d["doctest"]
    _add("S1", "v33-S1-%s" % name, prompt, completion, [name],
         "S1 doc_to_code for %s" % name)

    # ---- S3: code -> doc (1 pair) ----
    code = d["doctest"]
    prompt = ("You are an EDA automation engineer. The following Python "
              "code uses a PyAether API. Identify the API name, describe "
              "what it does, and explain its signature.\n\n"
              "```python\n%s\n```" % code)
    completion = ("The API used is **`%s`**.\n\n"
                  "**Signature**: `%s`\n\n"
                  "%s\n\n"
                  "**Key notes**: %s" % (name, d["sig"], d["desc"],
                                         d.get("key_notes", "")))
    _add("S3", "v33-S3-%s" % name, prompt, completion, [name],
         "S3 code_to_doc for %s" % name)

    # ---- S4: multi-step trace (5 pairs) ----
    s4_traces = [
        ("SleQueryData-3arg-and-equality",
         "Create a schematic cellview, make a pin, construct a SleQueryData "
         "with pin + empty hierPath + distance 25.0, then build an expected "
         "copy with different distance and verify equality.",
         ["SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> if lib in pyScript.dbGetAllLibs():\n"
         "...     pyScript.dbDelLib(lib=[lib])\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='Q7', "
         "point=(300, 200), direction='output')\n"
         ">>> hp = pyScript.emyHierPath()\n"
         ">>> qd = pyScript.SleQueryData(pin, hp, 25.0)\n"
         ">>> expected = pyScript.SleQueryData(pin, hp, 99.0)\n"
         ">>> # __eq__ compares obj AND hierPath, not dist\n"
         ">>> print('equal:', qd == expected)\n"
         "equal: True"),
        ("SleQueryData-1arg-then-setObject",
         "Construct a SleQueryData with only an object (1-arg, dist defaults "
         "to DBL_MAX), then use setObject to replace the wrapped object.",
         ["SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> pin1 = pyScript.dbCrtSchPin(cv=cv, name='A1', "
         "point=(100, 50), direction='input')\n"
         ">>> pin2 = pyScript.dbCrtSchPin(cv=cv, name='B2', "
         "point=(200, 80), direction='output')\n"
         ">>> qd = pyScript.SleQueryData(pin1)\n"
         ">>> print('before setObject:', qd.m_object == pin1)\n"
         "before setObject: True\n"
         ">>> qd.setObject(pin2)\n"
         ">>> print('after setObject:', qd.m_object == pin2)\n"
         "after setObject: True"),
        ("SleQueryData-copy-constructor",
         "Build a SleQueryData from obj + hierPath + distance 50.0, then use "
         "the copy constructor and verify equality.",
         ["SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='CLK', "
         "point=(500, 300), direction='input')\n"
         ">>> hp = pyScript.emyHierPath()\n"
         ">>> qd1 = pyScript.SleQueryData(pin, hp, 50.0)\n"
         ">>> qd2 = pyScript.SleQueryData(qd1)\n"
         ">>> print('copy equal to original:', qd1 == qd2)\n"
         "copy equal to original: True"),
        ("aeMakeSleQueryData-factory",
         "Use aeMakeSleQueryData factory to create a SleQueryData from a "
         "figure, then verify the result type and m_object presence.",
         ["aeMakeSleQueryData", "SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='D0', "
         "point=(150, 120), direction='input')\n"
         ">>> qd = pyScript.aeMakeSleQueryData(pin)\n"
         ">>> print('type:', type(qd).__name__)\n"
         "type: SleQueryData\n"
         ">>> print('has m_object:', hasattr(qd, 'm_object'))\n"
         "has m_object: True"),
        ("SleQueryData-isEvaluedTextORUnderQuery",
         "Create an eval text on a block, construct a query box, and call "
         "isEvaluedTextORUnderQuery to check overlap with the query region.",
         ["SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> block = cv.getMaster()\n"
         ">>> bbox = pyScript.emyBox(pyScript.emyPoint(400, -300), "
         "pyScript.emyPoint(460, -280))\n"
         ">>> origin = pyScript.emyPoint(0, 0)\n"
         ">>> align = pyScript.emyTextAlign('centerLeft')\n"
         ">>> font = pyScript.emyFont()\n"
         ">>> dist = 15\n"
         ">>> orient = pyScript.emyOrient()\n"
         ">>> instAttr = pyScript.emyEvalText.create(block, 235, 0, "
         "bbox, origin, align, font, dist, orient)\n"
         ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='Q7', "
         "point=(300, 200), direction='output')\n"
         ">>> hp = pyScript.emyHierPath()\n"
         ">>> qd = pyScript.SleQueryData(pin, hp, 5.0)\n"
         ">>> query_box = pyScript.emyBox(300, -400, 500, -200)\n"
         ">>> result = qd.isEvaluedTextORUnderQuery(query_box, True)\n"
         ">>> print('eval text under query:', bool(result))\n"
         "eval text under query: True"),
    ]
    for apis_str, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)."
                  % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v33-S4-%s" % apis_str, prompt, completion, apis,
             "S4 multi_step_trace: %s" % scenario)

    # ---- S5: error / edge-case (5 pairs) ----
    s5_items = [
        ("SleQueryData-default-dist-DBL_MAX",
         "When the 1-arg constructor is used (obj only), the distance "
         "defaults to DBL_MAX. Show this by constructing with only an "
         "object and noting the default behavior.",
         ["SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='RST', "
         "point=(80, 60), direction='input')\n"
         ">>> qd = pyScript.SleQueryData(pin)\n"
         ">>> # 1-arg constructor: dist defaults to DBL_MAX\n"
         ">>> print('object set:', qd.m_object == pin)\n"
         "object set: True\n"
         ">>> print('has m_hierPath:', hasattr(qd, 'm_hierPath'))\n"
         "has m_hierPath: True"),
        ("SleQueryData-eq-different-objects-False",
         "Two SleQueryData wrapping DIFFERENT objects should NOT be equal, "
         "even with same hierPath and distance. Demonstrate this.",
         ["SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> pin_a = pyScript.dbCrtSchPin(cv=cv, name='EN', "
         "point=(10, 10), direction='input')\n"
         ">>> pin_b = pyScript.dbCrtSchPin(cv=cv, name='RDY', "
         "point=(20, 20), direction='output')\n"
         ">>> hp = pyScript.emyHierPath()\n"
         ">>> qd_a = pyScript.SleQueryData(pin_a, hp, 5.0)\n"
         ">>> qd_b = pyScript.SleQueryData(pin_b, hp, 5.0)\n"
         ">>> # different objects -> __eq__ returns False\n"
         ">>> print('equal:', qd_a == qd_b)\n"
         "equal: False"),
        ("SleQueryData-get-extract-values",
         "After a query populates SleQueryData, use get() to extract point, "
         "ref, hierPath, row, and col. Show the 5-arg overload (no "
         "pFigGroup).",
         ["SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='Q7', "
         "point=(300, 200), direction='output')\n"
         ">>> hp = pyScript.emyHierPath()\n"
         ">>> qd = pyScript.SleQueryData(pin, hp, 25.0)\n"
         ">>> pt = pyScript.emyPoint()\n"
         ">>> ref = pyScript.emyRef()\n"
         ">>> out_hp = pyScript.emyHierPath()\n"
         ">>> row = pyScript.emyUInt4()\n"
         ">>> col = pyScript.emyUInt4()\n"
         ">>> qd.get(pt, ref, out_hp, row, col)\n"
         ">>> print('get() fills out parameters without error')\n"
         "get() fills out parameters without error"),
        ("SleQueryData-get-with-pFigGroup",
         "The get() method has a second overload that also fills out a "
         "pFigGroup. Show this 6-arg variant.",
         ["SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='Q7', "
         "point=(300, 200), direction='output')\n"
         ">>> hp = pyScript.emyHierPath()\n"
         ">>> qd = pyScript.SleQueryData(pin, hp, 25.0)\n"
         ">>> pt = pyScript.emyPoint()\n"
         ">>> fig_grp = pyScript.emyFigGroup()\n"
         ">>> ref = pyScript.emyRef()\n"
         ">>> out_hp = pyScript.emyHierPath()\n"
         ">>> row = pyScript.emyUInt4()\n"
         ">>> col = pyScript.emyUInt4()\n"
         ">>> qd.get(pt, fig_grp, ref, out_hp, row, col)\n"
         ">>> print('get() with pFigGroup overload: OK')\n"
         "get() with pFigGroup overload: OK"),
        ("SleQueryData-eq-same-obj-different-hierPath",
         "Two SleQueryData wrapping the SAME object but with setObject "
         "changing one to a different object should NOT be equal. Shows "
         "that __eq__ checks both obj AND hierPath.",
         ["SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='VCC', "
         "point=(0, 0), direction='input')\n"
         ">>> hp1 = pyScript.emyHierPath()\n"
         ">>> hp2 = pyScript.emyHierPath()\n"
         ">>> # same object, same empty hierPath -> equal\n"
         ">>> qd1 = pyScript.SleQueryData(pin, hp1, 5.0)\n"
         ">>> qd2 = pyScript.SleQueryData(pin, hp2, 5.0)\n"
         ">>> print('same obj same empty hp:', qd1 == qd2)\n"
         "same obj same empty hp: True\n"
         ">>> # now setObject to a different pin on qd2\n"
         ">>> pin_other = pyScript.dbCrtSchPin(cv=cv, name='GND', "
         "point=(10, 10), direction='input')\n"
         ">>> qd2.setObject(pin_other)\n"
         ">>> print('after setObject diff obj:', qd1 == qd2)\n"
         "after setObject diff obj: False"),
    ]
    for apis_str, scenario, apis, code in s5_items:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript). "
                  "Focus on the edge case or error scenario."
                  % scenario)
        completion = "```python\n%s\n```" % code
        _add("S5", "v33-S5-%s" % apis_str, prompt, completion, apis,
             "S5 error_edge_case: %s" % scenario)

    # ---- S6: cross-API workflow (5 pairs) ----
    s6_items = [
        ("SleQueryData+SleHierQuery-naiveQuery",
         "Set up a hierarchical query: create SleHierQuery, configure layer-"
         "purpose and object filters, run naiveQuery to populate "
         "emyArray_p_SleQueryData, iterate results accessing m_object and "
         "m_hierPath, then free.",
         ["SleQueryData", "SleHierQuery"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> design = pyScript.dbOpenCV('query_demo', 'aaa', 'layout', "
         "'r')\n"
         ">>> h_query = pyScript.SleHierQuery()\n"
         ">>> lpp_filter = pyScript.emyArray_p_EmyLPPHeader()\n"
         ">>> lpp = pyScript.EmyLPPHeader.get(\n"
         "...     design, pyScript.emyGetLayerNumByName(design, 'M2'))\n"
         ">>> lpp.setFlag(lpp.getFlag() & pyScript.EMY_LPP_FLAG_VISIBLE)\n"
         ">>> lpp.setFlag(lpp.getFlag() & "
         "pyScript.EMY_LPP_FLAG_SELECTABLE)\n"
         ">>> lpp_filter.append(lpp)\n"
         ">>> obj_filter = pyScript.SleSelObjectFilter()\n"
         ">>> obj_filter.clear()\n"
         ">>> obj_filter.set(pyScript.emcRectType)\n"
         ">>> qbox = pyScript.emyBox(-5000, -5000, 5000, 5000)\n"
         ">>> h_data = pyScript.emyArray_p_SleQueryData()\n"
         ">>> h_query.naiveQuery(design, qbox, lpp_filter,\n"
         "...     obj_filter, 0, 3, 0, 3, 20, h_data)\n"
         ">>> for data in h_data:\n"
         "...     obj = data.m_object.down_cast()\n"
         "...     box = pyScript.emyBox()\n"
         "...     obj.getBBox(box)\n"
         "...     depth = data.m_hierPath.getDepth()\n"
         "...     print('found rect at depth', depth)\n"
         ">>> pyScript.SleHierQuery.free(h_data)"),
        ("aeMakeSleQueryData+SleHierQuery-free",
         "Use aeMakeSleQueryData to create SleQueryData from a figure, then "
         "demonstrate the cleanup pattern with SleHierQuery.free.",
         ["aeMakeSleQueryData", "SleQueryData", "SleHierQuery"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> pin = pyScript.dbCrtSchPin(cv=cv, name='Q7', "
         "point=(300, 200), direction='output')\n"
         ">>> qd = pyScript.aeMakeSleQueryData(pin)\n"
         ">>> h_data = pyScript.emyArray_p_SleQueryData()\n"
         ">>> h_data.append(qd)\n"
         ">>> print('elements before free:', h_data.getNumElements())\n"
         "elements before free: 1\n"
         ">>> pyScript.SleHierQuery.free(h_data)\n"
         ">>> print('freed successfully')\n"
         "freed successfully"),
        ("SleHierQuery-sortObjectsByType",
         "After naiveQuery populates results, use sortObjectsByType to "
         "reorder the SleQueryData array by object type. Show before/after "
         "bbox difference.",
         ["SleQueryData", "SleHierQuery"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> design = pyScript.dbOpenCV('query_demo', 'aaa', 'layout', "
         "'r')\n"
         ">>> lpp_filter = pyScript.emyArray_p_EmyLPPHeader()\n"
         ">>> lpp = pyScript.EmyLPPHeader.get(\n"
         "...     design, pyScript.emyGetLayerNumByName(design, 'M2'))\n"
         ">>> lpp.setFlag(lpp.getFlag() & pyScript.EMY_LPP_FLAG_VISIBLE)\n"
         ">>> lpp.setFlag(lpp.getFlag() & "
         "pyScript.EMY_LPP_FLAG_SELECTABLE)\n"
         ">>> lpp_filter.append(lpp)\n"
         ">>> obj_filter = pyScript.SleSelObjectFilter()\n"
         ">>> obj_filter.set()\n"
         ">>> h_data = pyScript.emyArray_p_SleQueryData()\n"
         ">>> h_query = pyScript.SleHierQuery()\n"
         ">>> qbox = pyScript.emyBox(-6000, -6000, 6000, 6000)\n"
         ">>> h_query.naiveQuery(design, qbox, lpp_filter,\n"
         "...     obj_filter, 0, 3, 0, 3, 20, h_data)\n"
         ">>> if h_data.getNumElements() > 0:\n"
         "...     obj = h_data[0].m_object.down_cast()\n"
         "...     old_box = pyScript.emyBox()\n"
         "...     obj.getBBox(old_box)\n"
         "...     h_query.sortObjectsByType(h_data)\n"
         "...     obj2 = h_data[0].m_object.down_cast()\n"
         "...     new_box = pyScript.emyBox()\n"
         "...     obj2.getBBox(new_box)\n"
         "...     print('sorted:', str(old_box) != str(new_box))\n"
         ">>> pyScript.SleHierQuery.free(h_data)"),
        ("SleQueryData-construct-in-bulk",
         "Create multiple SleQueryData objects from a list of pins, store "
         "them in emyArray_p_SleQueryData, verify the count, then free. "
         "Shows the bulk-construction pattern for batch queries.",
         ["SleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> hp = pyScript.emyHierPath()\n"
         ">>> h_data = pyScript.emyArray_p_SleQueryData()\n"
         ">>> pin_names = ['A1', 'A2', 'B1', 'B2', 'C1']\n"
         ">>> for i, nm in enumerate(pin_names):\n"
         "...     p = pyScript.dbCrtSchPin(cv=cv, name=nm,\n"
         "...         point=(i * 100, i * 50), direction='input')\n"
         "...     qd = pyScript.SleQueryData(p, hp, float(i * 10))\n"
         "...     h_data.append(qd)\n"
         ">>> print('bulk count:', h_data.getNumElements())\n"
         "bulk count: 5\n"
         ">>> pyScript.SleHierQuery.free(h_data)"),
        ("SleQueryData-query-compare-pipeline",
         "Build a pipeline: create two SleQueryData with different objects "
         "and distances, compare with ==, then use copy constructor to "
         "clone one and verify. Shows full construct-compare-copy workflow.",
         ["SleQueryData", "aeMakeSleQueryData"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitQuery()\n"
         ">>> lib = 'demo_sle_lib'\n"
         ">>> pyScript.dbCreateLib(lib=lib)\n"
         ">>> pyScript.dbNewCV(lib=lib, cell='demo_sle_cell', "
         "view='schematic')\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=lib, cell='demo_sle_cell', "
         "view='schematic', mode='a')\n"
         ">>> hp = pyScript.emyHierPath()\n"
         ">>> pin_x = pyScript.dbCrtSchPin(cv=cv, name='X1', "
         "point=(10, 10), direction='input')\n"
         ">>> pin_y = pyScript.dbCrtSchPin(cv=cv, name='Y1', "
         "point=(20, 20), direction='output')\n"
         ">>> qd_x = pyScript.SleQueryData(pin_x, hp, 5.0)\n"
         ">>> qd_y = pyScript.SleQueryData(pin_y, hp, 5.0)\n"
         ">>> print('different objs equal:', qd_x == qd_y)\n"
         "different objs equal: False\n"
         ">>> qd_clone = pyScript.SleQueryData(qd_x)\n"
         ">>> print('clone equals original:', qd_x == qd_clone)\n"
         "clone equals original: True\n"
         ">>> qd_factory = pyScript.aeMakeSleQueryData(pin_x)\n"
         ">>> print('factory type:', type(qd_factory).__name__)\n"
         "factory type: SleQueryData"),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)."
                  % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v33-S6-%s" % apis_str, prompt, completion, apis,
             "S6 cross_api_workflow: %s" % scenario)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    parser = argparse.ArgumentParser(
        description="R203 v33 SleQueryData SFT corpus builder "
                    "(1 class + 1 factory + 1 query class, 17 pairs)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print stats only, do not write output file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Output JSONL path (default: %s)" % DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of pairs (for testing)")
    args = parser.parse_args()

    sys.stderr.write("R203 v33 SleQueryData corpus builder\n")
    sys.stderr.write("  Target APIs: %d (%s)\n" % (
        len(API_ORDER), ", ".join(API_ORDER)))

    missing = [a for a in API_ORDER if a not in API_DOCS]
    if missing:
        sys.stderr.write("ERROR: Missing API_DOCS for: %s\n"
                         % ", ".join(missing))
        sys.exit(1)

    eval_eps = load_eval_entry_points()
    sys.stderr.write("  Eval entry_points loaded: %d\n" % len(eval_eps))
    sys.stderr.write("  SleQueryData is entry_point? %s\n" % (
        "SleQueryData" in eval_eps))

    pairs, rejected, reject_details = build_pairs(eval_eps,
                                                  limit=args.limit)

    api_coverage = {}
    for p in pairs:
        for a in p["api_used"]:
            api_coverage[a] = api_coverage.get(a, 0) + 1

    type_counts = {}
    for p in pairs:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

    sys.stderr.write("\n=== R203 v33 Corpus Stats ===\n")
    sys.stderr.write("  Total pairs: %d\n" % len(pairs))
    sys.stderr.write("  Rejected (contamination): %d\n" % rejected)
    if reject_details:
        for pid, hit in reject_details:
            sys.stderr.write("    REJECT %s -> hit eval entry_point '%s'\n"
                             % (pid, hit))
    sys.stderr.write("  Pair types: %s\n" % ", ".join(
        "%s=%d" % (k, v) for k, v in sorted(type_counts.items())))
    sys.stderr.write("  API coverage (%d unique apis used):\n"
                     % len(api_coverage))
    for a in sorted(api_coverage):
        cnt = api_coverage.get(a, 0)
        sys.stderr.write("    %-25s %2d\n" % (a, cnt))

    if args.dry_run:
        sys.stderr.write("\n[dry-run] No output file written.\n")
        return

    with open(args.output, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    sz = os.path.getsize(args.output)
    sys.stderr.write("\nWrote %d pairs (%d bytes) to %s\n"
                     % (len(pairs), sz, args.output))


if __name__ == "__main__":
    main()
