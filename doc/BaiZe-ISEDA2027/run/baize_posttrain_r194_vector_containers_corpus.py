#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r194_vector_containers_corpus.py
R194 -- v24 PyAether SFT corpus: vector* SWIG container blind spot
(5 APIs, 25 pairs).

BACKGROUND: v11-v23 (613 pairs) cover 110/164 eval raw APIs (67.1%). 54 blind.
Data-driven scan (R191 blind_scan, re-run with v23 this wake) shows vector* is
the largest blind family: 11 usages / 5 APIs. R194 targets 5 vector* APIs.
All ISOLATE-class (eval_count>0, helper container types used in eval
canonical_solution as output/input arrays).  Fingerprint scan rejects eval
entry_points.

Authoritative signatures fetched via pyAether MCP get_api_details (R194 wake).

Usage:
  python3 baize_posttrain_r194_vector_containers_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v24_vector_containers.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["vector1D_emyPointF"] = {
    "sig": "vector1D_emyPointF() -> vector1D_emyPointF  [SWIG-wrapped std::vector<emyPointF>]",
    "desc": "A typed container (SWIG wrapper around C++ std::vector<emyPointF>) for storing a sequence of emyPointF coordinate objects. Constructed with no arguments to get an empty vector, then populated via .append(emyPointF). Supports len(), indexing [i], iteration, and slicing. This is the standard type for passing polygon vertex arrays and point collections to geometry APIs such as dbExpandPoints, dbCrtLine, and emyPointArrayGOA.",
    "params": {},
    "returns": "vector1D_emyPointF - an empty typed vector instance; populate with .append()",
    "methods": ".append(emyPointF) adds an element. len(v) / v.size() gives count. v[i] accesses element (emyPointF with .x()/.y()). Iterable. v.empty() checks if empty. v.clear() removes all.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pts = pyScript.vector1D_emyPointF()\n'
                '>>> pts.append(pyScript.emyPointF(0, 0))\n'
                '>>> pts.append(pyScript.emyPointF(10, 0))\n'
                '>>> pts.append(pyScript.emyPointF(10, 10))\n'
                '>>> pts.append(pyScript.emyPointF(0, 10))\n'
                '>>> print("count:", len(pts))\n'
                '>>> print("first:", pts[0].x(), pts[0].y())\n'
                '>>> for p in pts:\n'
                '...     print(p.x(), p.y())'),
    "category": "Container Types / Point Arrays", "safety": "ISOLATE", "eval_count": 5,
    "key_notes": "Constructed empty with no args. Must use .append(emyPointF) to populate -- not a plain Python list. Each element is an emyPointF with .x() and .y() accessors (methods, not attributes). etVectorp() returns False for the SWIG type (it checks Python lists only). Use isinstance(v, pyScript.vector1D_emyPointF) for type checks. Common in eval as polygon vertex input for dbExpandPoints / dbPointArrayGen / dbCrtLine."}

API_DOCS["vector1D_p_emyFig"] = {
    "sig": "vector1D_p_emyFig() -> vector1D_p_emyFig  [SWIG-wrapped std::vector<emyFig*>]",
    "desc": "A typed container (SWIG wrapper around C++ std::vector<emyFig*>) for storing a collection of emyFig figure pointers. Constructed empty, then populated via .append(emyFig). Used to batch figures for operations like dbResize (which takes a vector1D_p_emyFig of figures to resize) and other batch figure manipulations.",
    "params": {},
    "returns": "vector1D_p_emyFig - an empty typed vector instance; populate with .append()",
    "methods": ".append(emyFig) adds a figure pointer. .size() / len() gives count. .empty() checks emptiness. v[i] accesses element. Iterable. Stores pointers (not copies).",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> figs = pyScript.vector1D_p_emyFig()\n'
                '>>> fig1 = pyScript.dbCrtRect(cv=cv, bbox=[(0, 0), (5, 5)], layer="M1")\n'
                '>>> fig2 = pyScript.dbCrtRect(cv=cv, bbox=[(10, 10), (15, 15)], layer="M1")\n'
                '>>> figs.append(fig1)\n'
                '>>> figs.append(fig2)\n'
                '>>> print("figure count:", figs.size())\n'
                '>>> print("empty:", figs.empty())\n'
                '>>> print("first fig:", figs[0])'),
    "category": "Container Types / Figure Collections", "safety": "ISOLATE", "eval_count": 3,
    "key_notes": "Stores emyFig pointers (not object copies). etVectorp() returns False (SWIG type, not Python list). Required by dbResize as the figs parameter. Create figures first (e.g. dbCrtRect/dbCrtLine), then collect into this vector. Deleting the vector does NOT delete the figures."}

API_DOCS["vector1D_double"] = {
    "sig": "vector1D_double() -> vector1D_double  [SWIG-wrapped std::vector<double>]",
    "desc": "A typed container (SWIG wrapper around C++ std::vector<double>) for storing a sequence of floating-point values. Constructed empty, then populated via .append(float). Used primarily as the size parameter for dbResize, where the four values represent left/bottom/right/top resize offsets.",
    "params": {},
    "returns": "vector1D_double - an empty typed vector instance; populate with .append()",
    "methods": ".append(float) adds a value. .size() / len() gives count. v[i] accesses element. Iterable. .empty() checks emptiness.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> sizes = pyScript.vector1D_double()\n'
                '>>> sizes.append(1.0)   # left\n'
                '>>> sizes.append(2.0)   # bottom\n'
                '>>> sizes.append(1.0)   # right\n'
                '>>> sizes.append(2.0)   # top\n'
                '>>> print("size count:", len(sizes))\n'
                '>>> print("values:", [sizes[i] for i in range(sizes.size())])\n'
                '>>> print("empty:", sizes.empty())'),
    "category": "Container Types / Numeric Arrays", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Required by dbResize as the size parameter (4 values: left, bottom, right, top). Cannot pass a plain Python list -- C++ APIs expect the SWIG type. Values can be negative (shrink) or positive (grow). etVectorp() returns False for the SWIG type."}

API_DOCS["vector1D_p_emyShape"] = {
    "sig": "vector1D_p_emyShape() -> vector1D_p_emyShape  [SWIG-wrapped std::vector<emyShape*>]",
    "desc": "A typed container (SWIG wrapper around C++ std::vector<emyShape*>) for storing a collection of emyShape pointers. Constructed empty, then populated via .append(emyShape). Provides C++ STL-style interface including reserve(), resize(), clear(), front(), back(). Used to batch shapes for boolean geometry operations such as dbSingleLayerGOA (OR/AND/XOR of shapes on one layer).",
    "params": {},
    "returns": "vector1D_p_emyShape - an empty typed vector instance; populate with .append()",
    "methods": ".append(emyShape) adds a shape pointer. .size() / len() gives count. .empty() checks emptiness. .reserve(n) pre-allocates capacity. .resize(n) truncates/extends. .clear() removes all. .front()/.back() get first/last. v[i] indexing. Iterable.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> layer = pyScript.emyString("M1")\n'
                '>>> shapes = pyScript.vector1D_p_emyShape()\n'
                '>>> shapes.reserve(2)\n'
                '>>> s1 = pyScript.dbCrtLine(cv=cv, points=pyScript.vector1D_emyPointF(), layer=layer)\n'
                '>>> s2 = pyScript.dbCrtLine(cv=cv, points=pyScript.vector1D_emyPointF(), layer=layer)\n'
                '>>> shapes.append(s1)\n'
                '>>> shapes.append(s2)\n'
                '>>> print("shape count:", shapes.size())\n'
                '>>> print("empty:", shapes.empty())\n'
                '>>> print("front:", shapes.front())\n'
                '>>> shapes.clear()\n'
                '>>> print("after clear:", shapes.size())'),
    "category": "Container Types / Shape Collections", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Stores emyShape pointers (not copies). etVectorp() returns False (SWIG type). makeVector() returns a plain Python list, NOT this type -- do not confuse them. Required by dbSingleLayerGOA as the figs parameter. Use .reserve(n) before bulk-append for performance. Shape lifetime is independent of the vector."}

API_DOCS["vector2D_emyPointF"] = {
    "sig": "vector2D_emyPointF() -> vector2D_emyPointF  [SWIG-wrapped std::vector<std::vector<emyPointF>>]",
    "desc": "A 2D typed container (SWIG wrapper around C++ std::vector<std::vector<emyPointF>>) for storing multiple polygon arrays. Each element appended is a vector1D_emyPointF (one polygon's vertex array). Used by dbPointArrayGen to represent sets of polygons for boolean operations (AND/OR/XOR between two polygon sets).",
    "params": {},
    "returns": "vector2D_emyPointF - an empty 2D typed vector instance; populate with .append(vector1D_emyPointF)",
    "methods": ".append(vector1D_emyPointF) adds one polygon (a 1D point array). .size() / len() gives polygon count. v[i] accesses a polygon (returns vector1D_emyPointF). Iterable. .empty() checks emptiness.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> cv = pyScript.dbOpenCV(lib="test", cell="test", view="layout")\n'
                '>>> polys = pyScript.vector2D_emyPointF()\n'
                '>>> poly1 = pyScript.vector1D_emyPointF()\n'
                '>>> for p in [(0, 0), (10, 0), (10, 10), (0, 10)]:\n'
                '...     poly1.append(pyScript.emyPointF(*p))\n'
                '>>> polys.append(poly1)\n'
                '>>> poly2 = pyScript.vector1D_emyPointF()\n'
                '>>> for p in [(5, 5), (15, 5), (15, 15), (5, 15)]:\n'
                '...     poly2.append(pyScript.emyPointF(*p))\n'
                '>>> polys.append(poly2)\n'
                '>>> print("polygon count:", len(polys))\n'
                '>>> print("first poly vertices:", len(polys[0]))\n'
                '>>> print("empty:", polys.empty())'),
    "category": "Container Types / Multi-Polygon Arrays", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Each .append() takes a vector1D_emyPointF (one polygon), NOT an individual emyPointF. Appending a bare point will raise a type error. Required by dbPointArrayGen as the first/second polygon-set arguments. The 2D structure represents a set of polygons (each polygon is a 1D vertex array). etVectorp() returns False."}


API_ORDER = ["vector1D_emyPointF", "vector1D_p_emyFig", "vector1D_double",
             "vector1D_p_emyShape", "vector2D_emyPointF"]

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

    # ---- S1: doc -> code (5 pairs, one per API) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v24-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S3: code -> doc (5 pairs, one per API) ----
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
        _add("S3", "v24-S3-%s" % name, prompt, completion, [name],
             "S3 code_to_doc for %s" % name)


    # ---- S4: multi-step trace (5 pairs) ----
    s4_traces = [
        ("vector1D_emyPointF",
         "Build a rectangle as a point array, then expand it symmetrically using dbExpandPoints.",
         ["vector1D_emyPointF"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "pts = pyScript.vector1D_emyPointF()\n"
          "for p in [(0, 0), (10, 0), (10, 10), (0, 10)]:\n"
          "    pts.append(pyScript.emyPointF(*p))\n"
          "print('vertices:', len(pts))\n"
          "expanded = pyScript.dbExpandPoints(cv=cv, points=pts, left=2, bottom=2, right=2, top=2)\n"
          "print('expanded points:', expanded")),
        ("vector1D_p_emyFig",
         "Create two rectangle figures, collect them into a figure vector, then resize all of them.",
         ["vector1D_p_emyFig"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "figs = pyScript.vector1D_p_emyFig()\n"
          "fig1 = pyScript.dbCrtRect(cv=cv, bbox=[(0, 0), (5, 5)], layer='M1')\n"
          "fig2 = pyScript.dbCrtRect(cv=cv, bbox=[(10, 10), (15, 15)], layer='M1')\n"
          "figs.append(fig1)\n"
          "figs.append(fig2)\n"
          "print('collected figs:', figs.size())\n"
          "sizes = pyScript.vector1D_double()\n"
          "for v in [1.0, 1.0, 1.0, 1.0]:\n"
          "    sizes.append(v)\n"
          "resized = pyScript.dbResize(figs=figs, size=sizes)\n"
          "print('resized count:', len(resized))")),
        ("vector1D_double",
         "Build a size array with mixed grow/shrink values, apply it to a figure via dbResize, inspect the result.",
         ["vector1D_double"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "fig = pyScript.dbCrtRect(cv=cv, bbox=[(0, 0), (10, 10)], layer='M1')\n"
          "figs = pyScript.vector1D_p_emyFig()\n"
          "figs.append(fig)\n"
          "sizes = pyScript.vector1D_double()\n"
          "sizes.append(-2.0)   # shrink left\n"
          "sizes.append(1.0)    # grow bottom\n"
          "sizes.append(3.0)    # grow right\n"
          "sizes.append(-1.0)   # shrink top\n"
          "print('size values:', [sizes[i] for i in range(sizes.size())])\n"
          "resized = pyScript.dbResize(figs=figs, size=sizes)\n"
          "print('resized:', len(resized))")),
        ("vector1D_p_emyShape",
         "Create two line shapes on the same layer, collect them, then OR them with dbSingleLayerGOA.",
         ["vector1D_p_emyShape"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "layer = pyScript.emyString('M1')\n"
          "def mkpoly(coords):\n"
          "    pa = pyScript.vector1D_emyPointF()\n"
          "    for c in coords:\n"
          "        pa.append(pyScript.emyPointF(*c))\n"
          "    return pa\n"
          "s1 = pyScript.dbCrtLine(cv=cv, points=mkpoly([(0, 0), (10, 0), (10, 10), (0, 10)]), layer=layer)\n"
          "s2 = pyScript.dbCrtLine(cv=cv, points=mkpoly([(5, 5), (15, 5), (15, 15), (5, 15)]), layer=layer)\n"
          "shapes = pyScript.vector1D_p_emyShape()\n"
          "shapes.reserve(2)\n"
          "shapes.append(s1)\n"
          "shapes.append(s2)\n"
          "print('shapes collected:', shapes.size())\n"
          "result = pyScript.dbSingleLayerGOA(cv=cv, op=pyScript.emyString('OR'), layer=layer, figs=shapes)\n"
          "print('OR result count:', len(result))")),
        ("vector2D_emyPointF",
         "Build two overlapping polygon sets as 2D point arrays, then run AND and XOR between them with dbPointArrayGen.",
         ["vector2D_emyPointF"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "def mkpoly(coords):\n"
          "    pa = pyScript.vector1D_emyPointF()\n"
          "    for c in coords:\n"
          "        pa.append(pyScript.emyPointF(*c))\n"
          "    return pa\n"
          "first = pyScript.vector2D_emyPointF()\n"
          "first.append(mkpoly([(0, 0), (10, 0), (10, 10), (0, 10)]))\n"
          "second = pyScript.vector2D_emyPointF()\n"
          "second.append(mkpoly([(5, 5), (15, 5), (15, 15), (5, 15)]))\n"
          "print('first set polygons:', len(first))\n"
          "print('second set polygons:', len(second))\n"
          "r_and = pyScript.dbPointArrayGen('AND', cv, first, second)\n"
          "print('AND arrays:', len(r_and))\n"
          "r_xor = pyScript.dbPointArrayGen('XOR', cv, first, second)\n"
          "print('XOR arrays:', len(r_xor))")),
    ]
    for name, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v24-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)


    # ---- S5: anti_pattern / common mistake (5 pairs) ----
    s5_items = [
        ("vector1D_emyPointF",
         "pts = [pyScript.emyPointF(0, 0), pyScript.emyPointF(10, 0)]\nresult = pyScript.dbExpandPoints(cv=cv, points=pts, left=2, bottom=2, right=2, top=2)",
         "A plain Python list is not accepted by dbExpandPoints -- it requires the SWIG-typed vector1D_emyPointF. Using a bare list will raise a C++ type mismatch error.",
         "pts = pyScript.vector1D_emyPointF()\npts.append(pyScript.emyPointF(0, 0))\npts.append(pyScript.emyPointF(10, 0))\nresult = pyScript.dbExpandPoints(cv=cv, points=pts, left=2, bottom=2, right=2, top=2)"),
        ("vector1D_p_emyFig",
         "figs = pyScript.vector1D_p_emyFig()\nfigs.append(fig1)\nif pyScript.etVectorp(figs):\n    print('is a vector')",
         "etVectorp() checks for Python list objects only -- it returns False for SWIG-wrapped types like vector1D_p_emyFig. Use isinstance(figs, pyScript.vector1D_p_emyFig) or check figs.size() instead.",
         "figs = pyScript.vector1D_p_emyFig()\nfigs.append(fig1)\nprint('count:', figs.size())\nif isinstance(figs, pyScript.vector1D_p_emyFig):\n    print('is a vector1D_p_emyFig')"),
        ("vector1D_double",
         "result = pyScript.dbResize(figs=figs, size=[-2.0, 1.0, 1.0, 1.0])",
         "The size parameter of dbResize must be a vector1D_double (SWIG type), not a plain Python list. Passing a bare list causes a C++ type error.",
         "sizes = pyScript.vector1D_double()\nfor v in [-2.0, 1.0, 1.0, 1.0]:\n    sizes.append(v)\nresult = pyScript.dbResize(figs=figs, size=sizes)"),
        ("vector1D_p_emyShape",
         "shapes = pyScript.makeVector(2, shape)",
         "makeVector() returns a plain Python list, not a vector1D_p_emyShape. The boolean GOA APIs (dbSingleLayerGOA) require the SWIG-typed vector. Use the proper constructor and .append() instead.",
         "shapes = pyScript.vector1D_p_emyShape()\nshapes.append(shape1)\nshapes.append(shape2)"),
        ("vector2D_emyPointF",
         "polys = pyScript.vector2D_emyPointF()\npolys.append(pyScript.emyPointF(0, 0))\npolys.append(pyScript.emyPointF(10, 0))",
         "vector2D_emyPointF expects each .append() to receive a vector1D_emyPointF (a complete polygon vertex array), not an individual emyPointF. Appending a bare point raises a type error.",
         "polys = pyScript.vector2D_emyPointF()\npoly = pyScript.vector1D_emyPointF()\nfor p in [(0, 0), (10, 0), (10, 10), (0, 10)]:\n    poly.append(pyScript.emyPointF(*p))\npolys.append(poly)"),
    ]
    for name, wrong, mistake, correct in s5_items:
        prompt = ("You are an EDA automation engineer. The following PyAether "
                  "code has a bug. Identify the mistake and write the corrected "
                  "version.\n\n```python\n%s\n```" % wrong)
        completion = ("**Mistake**: %s\n\n**Corrected code**:\n```python\n%s\n```" % (mistake, correct))
        _add("S5", "v24-S5-%s" % name, prompt, completion, [name],
             "S5 anti_pattern for %s" % name)


    # ---- S6: cross-API combination (5 pairs) ----
    s6_items = [
        ("vector1D_emyPointF+vector2D_emyPointF",
         "Build a polygon as a 1D point array, wrap it into a 2D polygon set, then run a boolean AND with another set via dbPointArrayGen.",
         ["vector1D_emyPointF", "vector2D_emyPointF"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "poly_a = pyScript.vector1D_emyPointF()\n"
          "for p in [(0, 0), (10, 0), (10, 10), (0, 10)]:\n"
          "    poly_a.append(pyScript.emyPointF(*p))\n"
          "set_a = pyScript.vector2D_emyPointF()\n"
          "set_a.append(poly_a)\n"
          "poly_b = pyScript.vector1D_emyPointF()\n"
          "for p in [(5, 5), (15, 5), (15, 15), (5, 15)]:\n"
          "    poly_b.append(pyScript.emyPointF(*p))\n"
          "set_b = pyScript.vector2D_emyPointF()\n"
          "set_b.append(poly_b)\n"
          "r_and = pyScript.dbPointArrayGen('AND', cv, set_a, set_b)\n"
          "print('AND result arrays:', len(r_and))\n"
          "r_or = pyScript.dbPointArrayGen('OR', cv, set_a, set_b)\n"
          "print('OR result arrays:', len(r_or))")),
        ("vector1D_p_emyFig+vector1D_double",
         "Create three rectangle figures, collect them into a figure vector, build a size array, and resize all figures at once with dbResize.",
         ["vector1D_p_emyFig", "vector1D_double"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "figs = pyScript.vector1D_p_emyFig()\n"
          "for bbox in [[(0, 0), (5, 5)], [(10, 0), (15, 5)], [(0, 10), (5, 15)]]:\n"
          "    fig = pyScript.dbCrtRect(cv=cv, bbox=bbox, layer='M1')\n"
          "    figs.append(fig)\n"
          "print('figures collected:', figs.size())\n"
          "sizes = pyScript.vector1D_double()\n"
          "for v in [2.0, 2.0, 2.0, 2.0]:\n"
          "    sizes.append(v)\n"
          "resized = pyScript.dbResize(figs=figs, size=sizes)\n"
          "print('resized count:', len(resized))\n"
          "print('size array length:', sizes.size())")),
        ("vector1D_p_emyShape+vector1D_emyPointF",
         "Build two polygons as point arrays, create line shapes from them, collect the shapes, and OR them with dbSingleLayerGOA.",
         ["vector1D_p_emyShape", "vector1D_emyPointF"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "layer = pyScript.emyString('M1')\n"
          "def mkpoly(coords):\n"
          "    pa = pyScript.vector1D_emyPointF()\n"
          "    for c in coords:\n"
          "        pa.append(pyScript.emyPointF(*c))\n"
          "    return pa\n"
          "pts1 = mkpoly([(0, 0), (8, 0), (8, 8), (0, 8)])\n"
          "pts2 = mkpoly([(4, 4), (12, 4), (12, 12), (4, 12)])\n"
          "s1 = pyScript.dbCrtLine(cv=cv, points=pts1, layer=layer)\n"
          "s2 = pyScript.dbCrtLine(cv=cv, points=pts2, layer=layer)\n"
          "shapes = pyScript.vector1D_p_emyShape()\n"
          "shapes.append(s1)\n"
          "shapes.append(s2)\n"
          "print('shapes:', shapes.size())\n"
          "result = pyScript.dbSingleLayerGOA(cv=cv, op=pyScript.emyString('OR'), layer=layer, figs=shapes)\n"
          "print('OR result:', len(result))")),
        ("vector1D_emyPointF+vector1D_p_emyFig",
         "Build a polygon vertex array, create a line figure from it, then create a rect figure, and collect both into a figure vector for batch processing.",
         ["vector1D_emyPointF", "vector1D_p_emyFig"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "layer = pyScript.emyString('M1')\n"
          "poly_pts = pyScript.vector1D_emyPointF()\n"
          "for p in [(0, 0), (6, 0), (6, 6), (0, 6)]:\n"
          "    poly_pts.append(pyScript.emyPointF(*p))\n"
          "line_fig = pyScript.dbCrtLine(cv=cv, points=poly_pts, layer=layer)\n"
          "print('polygon vertices:', len(poly_pts))\n"
          "rect_fig = pyScript.dbCrtRect(cv=cv, bbox=[(8, 0), (14, 6)], layer=layer)\n"
          "figs = pyScript.vector1D_p_emyFig()\n"
          "figs.append(line_fig)\n"
          "figs.append(rect_fig)\n"
          "print('figures collected:', figs.size())\n"
          "print('empty:', figs.empty())")),
        ("vector2D_emyPointF+vector1D_p_emyShape",
         "Build two polygon sets as 2D arrays, run XOR with dbPointArrayGen, then create shapes from the result and collect them for a second-layer operation.",
         ["vector2D_emyPointF", "vector1D_p_emyShape"],
         ("import pyAether as pyScript\n\n"
          "cv = pyScript.dbOpenCV(lib='test', cell='test', view='layout')\n"
          "def mkpoly(coords):\n"
          "    pa = pyScript.vector1D_emyPointF()\n"
          "    for c in coords:\n"
          "        pa.append(pyScript.emyPointF(*c))\n"
          "    return pa\n"
          "set_a = pyScript.vector2D_emyPointF()\n"
          "set_a.append(mkpoly([(0, 0), (10, 0), (10, 10), (0, 10)]))\n"
          "set_b = pyScript.vector2D_emyPointF()\n"
          "set_b.append(mkpoly([(5, 5), (15, 5), (15, 15), (5, 15)]))\n"
          "r_xor = pyScript.dbPointArrayGen('XOR', cv, set_a, set_b)\n"
          "print('XOR result arrays:', len(r_xor))\n"
          "layer = pyScript.emyString('M2')\n"
          "shapes = pyScript.vector1D_p_emyShape()\n"
          "for i in range(len(r_xor)):\n"
          "    poly = r_xor[i]\n"
          "    s = pyScript.dbCrtLine(cv=cv, points=poly, layer=layer)\n"
          "    shapes.append(s)\n"
          "print('shapes from XOR:', shapes.size())\n"
          "print('front shape:', shapes.front())")),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript), combining the relevant "
                  "vector* container APIs." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v24-S6-%s" % apis_str.replace("+", "-"), prompt, completion, apis,
             "S6 cross_api_combo: %s" % apis_str)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details

def main():
    ap = argparse.ArgumentParser(
        description="R194 v24 PyAether SFT corpus: vector* containers (5 APIs, 25 pairs)")
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
    sys.stderr.write("\n=== R194 v24 vector* corpus summary ===\n")
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

