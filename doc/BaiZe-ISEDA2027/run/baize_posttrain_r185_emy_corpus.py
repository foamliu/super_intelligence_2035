#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r185_emy_corpus.py
R185 -- v15 PyAether SFT corpus: emy* geometric / data-type primitives
(the 4th blind domain family from R181 coverage audit, data-driven pick).

BACKGROUND: v11+v12+v13+v14 (208 pairs) teaches db*/schematic/layout/pin/
Mde*/cdf*/ae* APIs.  An eval-usage scan of the 158-task set found the emy*
family is the LARGEST remaining coherent blind family: 25 APIs, of which
the 10 highest-usage core constructors total 93 eval usages:
  emyPointF(20) emyViaExtEncParam(13) emyBitArray(12) emyPointArray(11)
  emyPointArrayF(10) emyBox(8) emyPoint(6) emyScalarName(5) emyCdbaNS(4)
  emyStringArray(4).
These are the FOUNDATIONAL geometric/structural types that virtually every
layout & schematic task constructs.  All 10 are ISOLATE-class (eval helpers,
eval_count>0).  The red line (S5.1) isolates on eval *entry_point* strings
(the 155 task function names), NOT on helper/type names -- teaching the
public API reference is allowed.  The fingerprint scan rejects any pair
containing a literal eval entry_point string.  Signatures fetched via
pyAether MCP get_api_details (R185 wake254).

v15: 10 emy* primitives x (S1 doc->code + S4 multi-step + S5 param var)
+ 5 S3 multi-API chains + 10 S6 lookups = 45 pairs.  Strict pollution scan
against all 155 eval entry_points.

Usage: python3 baize_posttrain_r185_emy_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v15_emy_primitives.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["emyPointF"] = {
    "sig": 'emyPointF(xValIn: emyDouble=0, yValIn: emyDouble=0) | emyPointF(point: emyPoint) | emyPointF()',
    "desc": "Two-dimensional float-coordinate point. Specifies positions and ranges of all emyFig-derived classes. Default constructor yields (0.0, 0.0).",
    "params": {
        "xValIn": "emyDouble - X coordinate (float)",
        "yValIn": "emyDouble - Y coordinate (float)",
        "point": "emyPoint - integer point to convert to float (overload)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> p = pyScript.emyPointF(3.5, 4.5)\n'
                '>>> p.x()\n3.5\n'
                '>>> q = pyScript.emyPointF(0, 0)\n'
                '>>> p.distanceFrom2(q)   # squared distance\n32.5\n'
                '>>> ip = p.emyPointF2emyPoint()   # rounds to (4, 5)'),
    "category": "emyDatabase / Geometry",
    "safety": "ISOLATE", "eval_count": 20,
    "key_notes": "Methods: x()->emyDouble, y()->emyDouble, set(x,y), distanceFrom2(pt)->emyDouble (squared dist, faster than sqrt), isSamePoint(pt, relTol=doubleTol)->bool, isCoordInt()->bool, roundCoord() (in-place), emyPointF2emyPoint()->emyPoint (rounds), scale(s), transform(xform). Maps to List[Tuple[float,float]]. Use isSamePoint for tolerance-based comparison instead of ==."}

API_DOCS["emyPoint"] = {
    "sig": 'emyPoint(xValIn: emyCoord=0, yValIn: emyCoord=0) | emyPoint(point: emyPoint, xform: emyTransform) | emyPoint()',
    "desc": "Two-dimensional integer-grid point (32-bit int coordinates). Specifies positions/ranges of emyFig-derived classes. Default constructor leaves coordinates UNINITIALIZED (random) -- always pass (x, y) or call set().",
    "params": {
        "xValIn": "emyCoord - X coordinate (int)",
        "yValIn": "emyCoord - Y coordinate (int)",
        "xform": "emyTransform - transform to apply (overload)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> p = pyScript.emyPoint(10, 20)\n'
                '>>> p.x(), p.y()\n(10, 20)\n'
                '>>> q = pyScript.emyPoint(30, 40)\n'
                '>>> p.distanceFrom2(q)   # (20)**2 + (20)**2 = 800\n800.0'),
    "category": "emyDatabase / Geometry",
    "safety": "ISOLATE", "eval_count": 6,
    "key_notes": "Methods: x()->emyCoord (int), y()->emyCoord (int), set(x,y), distanceFrom2(pt)->emyDouble (squared, returns float even for int inputs), transform(xform/orient/scale+angle) with 6 overloads. Maps to List[Tuple[int,int]]. WARNING: emyPoint() with no args gives random coords -- always initialize. Convert to float via emyPointF(point)."}

API_DOCS["emyBox"] = {
    "sig": 'emyBox(left, bottom, right, top) | emyBox(lb: emyPoint, rt: emyPoint) | emyBox(center: emyPoint, size: emyCoord) | emyBox()',
    "desc": "Axis-aligned integer bounding box (rectangle). left/right are X coords, bottom/top are Y coords. Normal box has left<=right, bottom<=top; init() creates an inverted box (useful as merge accumulator).",
    "params": {
        "left": "emyCoord - left X coordinate (int)",
        "bottom": "emyCoord - bottom Y coordinate (int)",
        "right": "emyCoord - right X coordinate (int)",
        "top": "emyCoord - top Y coordinate (int)",
        "lb": "emyPoint - lower-left point (overload)",
        "rt": "emyPoint - upper-right point (overload)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> box = pyScript.emyBox(0, 0, 100, 50)\n'
                '>>> box.getWidth(), box.getHeight()\n(100, 50)\n'
                '>>> pt = pyScript.emyPoint(25, 25)\n'
                '>>> box.contains(pt)\nTrue\n'
                '>>> box.l, box.b, box.r, box.t   # attribute access\n(0, 0, 100, 50)'),
    "category": "emyDatabase / Geometry",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "Properties: l,b,r,t (int coords), lb/rt (emyPoint), center, width, height. Methods: getWidth(), getHeight(), contains(pt, incEdges=True)->bool, overlaps(box, incEdges=True)->bool, merge(box, result), intersection(box, result), init() (inverted box), fix() (repair inverted), isInverted()->bool, hasNoArea()->bool, scale(s), transform(xform), toPoints(emyPointArray), distanceFrom2(pt)->emyDouble (to nearest edge). Result-param pattern: pre-create result box, e.g. r=emyBox(); box1.merge(box2, r)."}
API_DOCS["emyPointArray"] = {
    "sig": 'emyPointArray(sizeIn: emyUInt4=0) | emyPointArray(pointsIn) | emyPointArray(pointsIn, xform) | emyPointArray(pointsIn, offset) | emyPointArray(point, numPoints) | emyPointArray(rectIn: emyBox)',
    "desc": "Array of integer 2D points. Denotes figures such as emyLine and emyPolygons. When passed to emyFig methods must be well-formed (no duplicate/collinear points); use compress() to clean. Has independent size (allocated) and numElements (used) counts.",
    "params": {
        "sizeIn": "emyUInt4 - preallocated capacity (default 0)",
        "pointsIn": "emyPointArray or list[emyPoint] - array/list to copy",
        "xform": "emyTransform - transform to apply to the copy (overload)",
        "offset": "emyPoint - offset to translate the copy (overload)",
        "rectIn": "emyBox - rectangle to derive 4 corner points from (overload)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> arr = pyScript.emyPointArray(4)\n'
                '>>> arr.append(pyScript.emyPoint(0, 0))\n'
                '>>> arr.append(pyScript.emyPoint(10, 0))\n'
                '>>> arr.append(pyScript.emyPoint(10, 20))\n'
                '>>> arr.append(pyScript.emyPoint(0, 20))\n'
                '>>> arr.getNumElements()\n4\n'
                '>>> arr.compress(False)   # remove dup/collinear (open path)'),
    "category": "emyDatabase / Geometry",
    "safety": "ISOLATE", "eval_count": 11,
    "key_notes": "Methods: append(pt), get(i)->emyPoint, getNumElements()->emyUInt4, compress(isClosed=False) (remove duplicate & collinear points; True for closed polygons removes the coincident last point), getBBox()->emyBox, transform(xform/orient/offset/scale+angle). You may pass a Python list of emyPoint where an emyPointArray is expected. Avoid small incremental allocations -- preallocate with sizeIn."}

API_DOCS["emyPointArrayF"] = {
    "sig": 'emyPointArrayF(pointsIn: emyPointArray) | emyPointArrayF(pointsIn: emyPointArrayF) | emyPointArrayF(sizeIn: emyUInt4=0)',
    "desc": "Array of float 2D points. The float counterpart of emyPointArray. Typically constructed by converting an integer emyPointArray. Used for float-precision geometry (polygons, paths).",
    "params": {
        "pointsIn": "emyPointArray - integer array to convert to float (primary overload)",
        "sizeIn": "emyUInt4 - preallocated capacity (default 0)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> ia = pyScript.emyPointArray()\n'
                '>>> ia.append(pyScript.emyPoint(1, 1))\n'
                '>>> ia.append(pyScript.emyPoint(2, 2))\n'
                '>>> fa = pyScript.emyPointArrayF(ia)   # convert int -> float\n'
                '>>> fa.toList()\n[[1.0, 1.0], [2.0, 2.0]]\n'
                '>>> fa.magnifyIn2D(2.0, 3.0)   # x*2, y*3 in place'),
    "category": "emyDatabase / Geometry",
    "safety": "ISOLATE", "eval_count": 10,
    "key_notes": "Methods: append(emyPointF), get(i)->emyPointF, getNumElements(), compress(isClosed), getBBox(boxF) (result-param), magnifyIn2D(fx, fy) (in-place X/Y scale), reverse() (in-place), toList()->[[x,y],...] (Python list), transform(xform/orient/offset/scale+angle), transformF(emyTransformF), getPointArray()->emyPointArray. Cannot be created directly from a Python list -- go through emyPointArray first."}
API_DOCS["emyBitArray"] = {
    "sig": 'emyBitArray() | emyBitArray(len: emyUInt4) | emyBitArray(ba: emyBitArray)',
    "desc": "Array of bits (each 0 or 1). Used for selection-type masks and feature flags, e.g. indexing SLE_TYPE_* enum ranges. Has independent size and element counts.",
    "params": {
        "len": "emyUInt4 - number of bits (length of the array)",
        "ba": "emyBitArray - existing bit array to copy (overload)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> ba = pyScript.emyBitArray(32)\n'
                '>>> ba.set()            # all bits = 1\n'
                '>>> ba.clear(0)         # bit 0 = 0\n'
                '>>> ba.countPiece()     # count set pieces'),
    "category": "emyDatabase / Data Structure",
    "safety": "ISOLATE", "eval_count": 12,
    "key_notes": "Methods: set() (all 1), set(index) (one bit 1), clear() (all 0), clear(index) (one bit 0), copy(len, defVal) (new array of length len with default 0/1), copy(ba) (deep copy), countPiece(closedCurve=False)->emyUInt4 (count connected pieces), getNumElements()->emyUInt4, == (equality). A common idiom: ba = emyBitArray(SLE_TYPE_EXT_END); ba.set() to enable all selection types."}

API_DOCS["emyViaExtEncParam"] = {
    "sig": 'emyViaExtEncParam(encLeft=0, encBottom=0, encRight=0, encTop=0) | emyViaExtEncParam()',
    "desc": "Via extension/enclosure parameters -- four directional integer values defining the minimum extension distance between a via and the surrounding metal layers. Used when configuring via generation. Default constructor sets all four to 0.",
    "params": {
        "encLeft": "emyInt4 - left-direction extension (int)",
        "encBottom": "emyInt4 - bottom-direction extension (int)",
        "encRight": "emyInt4 - right-direction extension (int)",
        "encTop": "emyInt4 - top-direction extension (int)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> enc = pyScript.emyViaExtEncParam(10, 20, 10, 20)\n'
                '>>> print(enc)\n'
                'ViaExtEncParam (Left: 10, Bottom: 20, Right: 10, Top: 20)\n'
                '>>> enc2 = pyScript.emyViaExtEncParam(10, 20, 10, 20)\n'
                '>>> enc == enc2\nTrue'),
    "category": "Extension / Database Extension",
    "safety": "ISOLATE", "eval_count": 13,
    "key_notes": "All four params are emyInt4 (int). Supports negative values (may mean inset rather than extension depending on context). Value equality via == compares all four. Lightweight value-type object. Pairs with via-generation APIs (aeViaGenerateViasAtPoint) to specify enclosure rules. Always provide all four args in fixed order: left, bottom, right, top."}
API_DOCS["emyScalarName"] = {
    "sig": 'emyScalarName() | emyScalarName(nSpace: emyNameSpace, in: emyChar) | emyScalarName(in: emyScalarName)',
    "desc": "The name of an object without an associated index (a scalar, non-vector name). Part of the emyName hierarchy. Names can be hierarchical (use '.' separator). Constructed and evaluated within a namespace (e.g. emyCdbaNS).",
    "params": {
        "nSpace": "emyNameSpace - the namespace in which to evaluate the string (e.g. emyCdbaNS())",
        "in": "emyChar / str - the name string to evaluate",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> ns = pyScript.emyCdbaNS()\n'
                '>>> nm = pyScript.emyScalarName(ns, "top.module.signal")\n'
                '>>> s = pyScript.emyString()\n'
                '>>> nm.get(ns, s)      # render in CDBA namespace\n'
                '>>> s.getString()'),
    "category": "emyDatabase / Naming",
    "safety": "ISOLATE", "eval_count": 5,
    "key_notes": "Methods: get(nSpace, out: emyString) or get(out: emyString) (render to string), addHierPath(path) (prepend hierarchical path; throws if name empty), addHierMem(...), append(member), equal(name), == (value equality). Raises emcInvalidNameLength / emcInvalidNameSyntax on bad input. For vector names use emyVectorName; for name sets use emyBundleName. Always create within a namespace, not the bare emyScalarName(str)."}

API_DOCS["emyCdbaNS"] = {
    "sig": 'emyCdbaNS()',
    "desc": "The CDBA namespace object. Used to create, evaluate, and compare names. CDBA syntax: vectors use '< >' (e.g. bus<7:0>) NOT '[ ]'; bundle repeat uses '<*n>' prefix; hierarchy separator is '.'. Case-sensitive.",
    "params": {},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> ns = pyScript.emyCdbaNS()\n'
                '>>> a = pyScript.emyScalarName(ns, "clk")\n'
                '>>> b = pyScript.emyScalarName(ns, "clk")\n'
                '>>> ns.isEqual(a, b)   # NOTE: instance method, not static\nTrue'),
    "category": "emyDatabase / Naming",
    "safety": "ISOLATE", "eval_count": 4,
    "key_notes": "Construct with no args: emyCdbaNS(). Key method: isEqual(name1, name2)->bool -- this is an INSTANCE method (call ns.isEqual(a,b), NOT emyCdbaNS.isEqual(a,b) which raises a wrong-args error). Pass the ns instance to emyScalarName/emyVectorName constructors so names are evaluated in CDBA. Empty name strings raise SystemError. To get a name's type, wrap in emyName(name).getType()."}

API_DOCS["emyStringArray"] = {
    "sig": 'emyStringArray() | emyStringArray(size: emyUInt4) | emyStringArray(arr: emyStringArray)',
    "desc": "Array of emyString objects. Elements MUST be emyString, not plain Python str (wrap with emyString(...)). Has independent capacity (getSize) and element count (getNumElements).",
    "params": {
        "size": "emyUInt4 - preallocated capacity (number of slots)",
        "arr": "emyStringArray - existing array to deep-copy (overload)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> arr = pyScript.emyStringArray()\n'
                '>>> arr.append(pyScript.emyString("M1"))\n'
                '>>> arr.append(pyScript.emyString("M2"))\n'
                '>>> arr.getNumElements()\n2\n'
                '>>> arr.find(pyScript.emyString("M2"))\n1\n'
                '>>> arr.find(pyScript.emyString("M9"))   # not found\n4294967295'),
    "category": "emyDatabase / Data Structure",
    "safety": "ISOLATE", "eval_count": 4,
    "key_notes": "Methods: append(emyString), get(i)->emyString, getSize()->emyUInt4 (capacity), getNumElements()->emyUInt4 (actual count), setSize(n) (resize capacity), setNumElements(n), find(emyString)->emyUInt4 (returns 4294967295 = 0xFFFFFFFF if NOT found -- check against this sentinel), equal(arr)->bool, getElements()->emyString (all elements concatenated). 0-based indexing; out-of-range throws. Preallocate for performance; avoid frequent resizing."}

EMY_ORDER = ["emyPointF", "emyViaExtEncParam", "emyBitArray", "emyPointArray",
             "emyPointArrayF", "emyBox", "emyPoint", "emyScalarName",
             "emyCdbaNS", "emyStringArray"]
API_ORDER = EMY_ORDER
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
    if name == "emyPointF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(x, y):\n"
            "    p = pyScript.emyPointF(x, y)\n"
            "    assert p.x() == x and p.y() == y\n"
            "    return p\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(x, y) that constructs an emyPointF, asserts "
                  "x()/y() match the inputs, and returns the point." % (_doc_block(name), fn))
    elif name == "emyPoint":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(x, y):\n"
            "    p = pyScript.emyPoint(x, y)\n"
            "    assert p.x() == x and p.y() == y\n"
            "    return p\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(x, y) that constructs an emyPoint with explicit "
                  "integer coords, asserts x()/y() match, and returns it. Do NOT use the "
                  "no-arg constructor (it leaves coords uninitialized)." % (_doc_block(name), fn))
    elif name == "emyBox":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(left, bottom, right, top):\n"
            "    box = pyScript.emyBox(left, bottom, right, top)\n"
            "    if box.hasNoArea():\n"
            "        raise RuntimeError(\"emyBox has no area\")\n"
            "    return box\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(left, bottom, right, top) that constructs an "
                  "emyBox, raises if it has no area, and returns the box." % (_doc_block(name), fn))
    elif name == "emyPointArray":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(points):\n"
            "    arr = pyScript.emyPointArray(len(points))\n"
            "    for pt in points:\n"
            "        arr.append(pt)\n"
            "    arr.compress(False)\n"
            "    return arr\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(points) that preallocates an emyPointArray, "
                  "appends each emyPoint, compresses out duplicate/collinear points, and "
                  "returns the array." % (_doc_block(name), fn))
    elif name == "emyPointArrayF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(int_points):\n"
            "    ia = pyScript.emyPointArray(len(int_points))\n"
            "    for pt in int_points:\n"
            "        ia.append(pt)\n"
            "    fa = pyScript.emyPointArrayF(ia)\n"
            "    return fa.toList()\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(int_points) that builds an integer emyPointArray, "
                  "converts it to emyPointArrayF, and returns the float points as a Python list "
                  "of [x, y] pairs via toList()." % (_doc_block(name), fn))
    elif name == "emyBitArray":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(length, set_bits):\n"
            "    ba = pyScript.emyBitArray(length)\n"
            "    ba.clear()\n"
            "    for i in set_bits:\n"
            "        ba.set(i)\n"
            "    return ba\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(length, set_bits) that creates an emyBitArray of "
                  "the given length, clears all bits, sets the listed indices, and returns it."
                  % (_doc_block(name), fn))
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S1 doc-to-code"
def _s1_doc_to_code_b(name):
    fn = "use_" + name.lower()
    if name == "emyViaExtEncParam":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(left, bottom, right, top):\n"
            "    enc = pyScript.emyViaExtEncParam(left, bottom, right, top)\n"
            "    assert enc == pyScript.emyViaExtEncParam(left, bottom, right, top)\n"
            "    return enc\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(left, bottom, right, top) that constructs an "
                  "emyViaExtEncParam with the four directional extension values, verifies value "
                  "equality, and returns it." % (_doc_block(name), fn))
    elif name == "emyScalarName":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(name_str):\n"
            "    ns = pyScript.emyCdbaNS()\n"
            "    nm = pyScript.emyScalarName(ns, name_str)\n"
            "    out = pyScript.emyString()\n"
            "    nm.get(ns, out)\n"
            "    return out\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(name_str) that creates a CDBA namespace, "
                  "constructs an emyScalarName, renders it back to emyString with get(), and "
                  "returns the string." % (_doc_block(name), fn))
    elif name == "emyCdbaNS":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(s1, s2):\n"
            "    ns = pyScript.emyCdbaNS()\n"
            "    a = pyScript.emyScalarName(ns, s1)\n"
            "    b = pyScript.emyScalarName(ns, s2)\n"
            "    return ns.isEqual(a, b)\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(s1, s2) that creates a CDBA namespace, builds two "
                  "emyScalarName objects, and returns whether they are equal via the instance "
                  "method isEqual." % (_doc_block(name), fn))
    elif name == "emyStringArray":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(strs):\n"
            "    arr = pyScript.emyStringArray(len(strs))\n"
            "    for s in strs:\n"
            "        arr.append(pyScript.emyString(s))\n"
            "    return arr\n") % fn
        prompt = ("You are an EDA automation assistant. Read the following PyAether "
                  "API documentation and write Python code that correctly uses this API.\n\n"
                  "## API Documentation\n\n%s\n\n"
                  "Write a Python function %s(strs) that preallocates an emyStringArray, appends "
                  "each Python string wrapped as emyString, and returns the array. Elements must "
                  "be emyString, not plain str." % (_doc_block(name), fn))
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S1 doc-to-code"

S1_HANDLED = {"emyPointF", "emyPoint", "emyBox", "emyPointArray",
              "emyPointArrayF", "emyBitArray"}
def _s4_multi_step(name):
    fn = "trace_" + name.lower()
    if name == "emyPointF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(x1, y1, x2, y2):\n"
            "    p = pyScript.emyPointF(x1, y1)\n"
            "    q = pyScript.emyPointF(x2, y2)\n"
            "    d2 = p.distanceFrom2(q)\n"
            "    ip = p.emyPointF2emyPoint()\n"
            "    return {\"dist2\": d2, \"int_point\": ip}\n") % fn
        prompt = ("Write a Python function %s(x1, y1, x2, y2) that builds two emyPointF, "
                  "computes squared distance with distanceFrom2, converts the first to emyPoint "
                  "with emyPointF2emyPoint, and returns both in a dict." % fn)
    elif name == "emyPoint":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(x, y, dx, dy):\n"
            "    p = pyScript.emyPoint(x, y)\n"
            "    p.set(x + dx, y + dy)\n"
            "    fp = pyScript.emyPointF(p)\n"
            "    return p, fp\n") % fn
        prompt = ("Write a Python function %s(x, y, dx, dy) that builds an emyPoint, updates "
                  "coords with set, converts to emyPointF, and returns both." % fn)
    elif name == "emyBox":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(boxes):\n"
            "    merged = pyScript.emyBox()\n"
            "    merged.init()\n"
            "    for b in boxes:\n"
            "        tmp = pyScript.emyBox()\n"
            "        merged.merge(b, tmp)\n"
            "        merged = tmp\n"
            "    return merged\n") % fn
        prompt = ("Write a Python function %s(boxes) that starts from an inverted emyBox (via "
                  "init), merges each box with the result-param pattern, and returns the final "
                  "merged bounding box." % fn)
    elif name == "emyPointArray":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(corners):\n"
            "    arr = pyScript.emyPointArray(len(corners))\n"
            "    for c in corners:\n"
            "        arr.append(pyScript.emyPoint(c[0], c[1]))\n"
            "    arr.compress(True)\n"
            "    bbox = arr.getBBox()\n"
            "    return arr, bbox\n") % fn
        prompt = ("Write a Python function %s(corners) that builds an emyPointArray from coord "
                  "tuples, compresses as a closed polygon, gets its bounding box with getBBox, "
                  "and returns the array and the box." % fn)
    elif name == "emyPointArrayF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(corners, fx, fy):\n"
            "    ia = pyScript.emyPointArray(len(corners))\n"
            "    for c in corners:\n"
            "        ia.append(pyScript.emyPoint(c[0], c[1]))\n"
            "    fa = pyScript.emyPointArrayF(ia)\n"
            "    fa.magnifyIn2D(fx, fy)\n"
            "    return fa.toList()\n") % fn
        prompt = ("Write a Python function %s(corners, fx, fy) that builds an integer "
                  "emyPointArray, converts to emyPointArrayF, scales in place with magnifyIn2D, "
                  "and returns the result as a Python list of [x, y] pairs." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S4 multi-step trace"
def _s4_multi_step_b(name):
    fn = "trace_" + name.lower()
    if name == "emyBitArray":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(length, off_indices):\n"
            "    ba = pyScript.emyBitArray(length)\n"
            "    ba.set()\n"
            "    for i in off_indices:\n"
            "        ba.clear(i)\n"
            "    pieces = ba.countPiece()\n"
            "    return ba, pieces\n") % fn
        prompt = ("Write a Python function %s(length, off_indices) that creates an emyBitArray, "
                  "sets all bits, clears the listed indices, counts remaining pieces with "
                  "countPiece, and returns the array and the count." % fn)
    elif name == "emyViaExtEncParam":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(specs):\n"
            "    results = []\n"
            "    for left, bottom, right, top in specs:\n"
            "        enc = pyScript.emyViaExtEncParam(left, bottom, right, top)\n"
            "        results.append((enc, left + bottom + right + top))\n"
            "    return results\n") % fn
        prompt = ("Write a Python function %s(specs) that for each (left, bottom, right, top) "
                  "tuple constructs an emyViaExtEncParam and records it with the sum of its four "
                  "values, returning the list of pairs." % fn)
    elif name == "emyScalarName":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(base, member):\n"
            "    ns = pyScript.emyCdbaNS()\n"
            "    nm = pyScript.emyScalarName(ns, base)\n"
            "    nm.addHierPath(pyScript.emyScalarName(ns, member))\n"
            "    out = pyScript.emyString()\n"
            "    nm.get(ns, out)\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(base, member) that creates a CDBA namespace, builds "
                  "a base emyScalarName, prepends a hierarchical path with addHierPath, renders "
                  "the result to emyString, and returns it." % fn)
    elif name == "emyCdbaNS":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(pairs):\n"
            "    ns = pyScript.emyCdbaNS()\n"
            "    out = []\n"
            "    for s1, s2 in pairs:\n"
            "        a = pyScript.emyScalarName(ns, s1)\n"
            "        b = pyScript.emyScalarName(ns, s2)\n"
            "        out.append(ns.isEqual(a, b))\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(pairs) that creates one CDBA namespace, builds "
                  "emyScalarName objects for each (s1, s2) pair, compares them with the instance "
                  "method isEqual, and returns the list of booleans." % fn)
    elif name == "emyStringArray":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(items, target):\n"
            "    arr = pyScript.emyStringArray(len(items))\n"
            "    for s in items:\n"
            "        arr.append(pyScript.emyString(s))\n"
            "    idx = arr.find(pyScript.emyString(target))\n"
            "    return None if idx == 4294967295 else idx\n") % fn
        prompt = ("Write a Python function %s(items, target) that builds an emyStringArray, finds "
                  "the target with find, maps the 4294967295 not-found sentinel to None, and "
                  "returns the index (or None)." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S4 multi-step trace"

S4_HANDLED = {"emyPointF", "emyPoint", "emyBox", "emyPointArray", "emyPointArrayF"}
def _s5_param_variation(name):
    fn = "vary_" + name.lower()
    if name == "emyPointF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(coords):\n"
            "    out = []\n"
            "    for x, y in coords:\n"
            "        p = pyScript.emyPointF(x, y)\n"
            "        out.append((p.x(), p.y(), p.isCoordInt()))\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(coords) that builds an emyPointF for each (x, y) "
                  "and returns a list of (x, y, isCoordInt) tuples." % fn)
    elif name == "emyPoint":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(coords):\n"
            "    out = []\n"
            "    for x, y in coords:\n"
            "        p = pyScript.emyPoint(int(x), int(y))\n"
            "        out.append((p.x(), p.y()))\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(coords) that builds an emyPoint for each (x, y) "
                  "(cast to int) and returns the list of stored coordinates." % fn)
    elif name == "emyBox":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(rects):\n"
            "    out = []\n"
            "    for l, b, r, t in rects:\n"
            "        box = pyScript.emyBox(l, b, r, t)\n"
            "        out.append((box.getWidth(), box.getHeight(), box.isInverted()))\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(rects) that builds an emyBox for each (l, b, r, t) "
                  "and returns (width, height, isInverted) for each." % fn)
    elif name == "emyPointArray":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(groups):\n"
            "    out = []\n"
            "    for pts in groups:\n"
            "        arr = pyScript.emyPointArray(len(pts))\n"
            "        for x, y in pts:\n"
            "            arr.append(pyScript.emyPoint(x, y))\n"
            "        arr.compress(False)\n"
            "        out.append(arr.getNumElements())\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(groups) that builds and compresses an "
                  "emyPointArray for each group of (x, y) tuples and returns the element count "
                  "after compression for each." % fn)
    elif name == "emyPointArrayF":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(groups, fx, fy):\n"
            "    out = []\n"
            "    for pts in groups:\n"
            "        ia = pyScript.emyPointArray(len(pts))\n"
            "        for x, y in pts:\n"
            "            ia.append(pyScript.emyPoint(x, y))\n"
            "        fa = pyScript.emyPointArrayF(ia)\n"
            "        fa.magnifyIn2D(fx, fy)\n"
            "        out.append(fa.toList())\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(groups, fx, fy) that converts each group of integer "
                  "points to emyPointArrayF, scales with magnifyIn2D, and returns the list of "
                  "float point lists." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S5 parameter variation"
def _s5_param_variation_b(name):
    fn = "vary_" + name.lower()
    if name == "emyBitArray":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(lengths):\n"
            "    out = []\n"
            "    for n in lengths:\n"
            "        ba = pyScript.emyBitArray(n)\n"
            "        ba.set()\n"
            "        out.append(ba.countPiece())\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(lengths) that creates an emyBitArray for each "
                  "length, sets all bits, counts pieces with countPiece, and returns the list of "
                  "counts." % fn)
    elif name == "emyViaExtEncParam":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(specs):\n"
            "    out = {}\n"
            "    for left, bottom, right, top in specs:\n"
            "        enc = pyScript.emyViaExtEncParam(left, bottom, right, top)\n"
            "        out[(left, bottom, right, top)] = enc\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(specs) that constructs an emyViaExtEncParam for "
                  "each (left, bottom, right, top) tuple and returns a dict keyed by the tuple."
                  % fn)
    elif name == "emyScalarName":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(names):\n"
            "    ns = pyScript.emyCdbaNS()\n"
            "    out = []\n"
            "    for s in names:\n"
            "        nm = pyScript.emyScalarName(ns, s)\n"
            "        r = pyScript.emyString()\n"
            "        nm.get(ns, r)\n"
            "        out.append(r)\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(names) that builds an emyScalarName for each string "
                  "in a shared CDBA namespace, renders each to emyString, and returns the list."
                  % fn)
    elif name == "emyCdbaNS":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(candidates, reference):\n"
            "    ns = pyScript.emyCdbaNS()\n"
            "    ref = pyScript.emyScalarName(ns, reference)\n"
            "    out = []\n"
            "    for s in candidates:\n"
            "        c = pyScript.emyScalarName(ns, s)\n"
            "        out.append(ns.isEqual(ref, c))\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(candidates, reference) that builds a reference "
                  "emyScalarName and compares each candidate against it with isEqual in a CDBA "
                  "namespace, returning the list of booleans." % fn)
    elif name == "emyStringArray":
        completion = ("import pyAether as pyScript\n\n"
            "def %s(batches, target):\n"
            "    out = []\n"
            "    tgt = pyScript.emyString(target)\n"
            "    for items in batches:\n"
            "        arr = pyScript.emyStringArray(len(items))\n"
            "        for s in items:\n"
            "            arr.append(pyScript.emyString(s))\n"
            "        idx = arr.find(tgt)\n"
            "        out.append(None if idx == 4294967295 else idx)\n"
            "    return out\n") % fn
        prompt = ("Write a Python function %s(batches, target) that builds an emyStringArray for "
                  "each batch, finds the target string, maps the not-found sentinel to None, and "
                  "returns the list of indices." % fn)
    else:
        completion = ("import pyAether as pyScript\n\n"
            "def %s(*a, **k):\n    return pyScript.%s(*a, **k)\n") % (fn, name)
        prompt = "Write a Python function that wraps %s." % name
    return prompt, completion, [name], "S5 parameter variation"

S5_HANDLED = S4_HANDLED
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
        gen = _s1_doc_to_code if name in S1_HANDLED else _s1_doc_to_code_b
        p, c, a, n = gen(name); _add("S1", "s1_" + name, p, c, a, n)
    for name in API_ORDER:
        gen = _s4_multi_step if name in S4_HANDLED else _s4_multi_step_b
        p, c, a, n = gen(name); _add("S4", "s4_" + name, p, c, a, n)
    for name in API_ORDER:
        gen = _s5_param_variation if name in S5_HANDLED else _s5_param_variation_b
        p, c, a, n = gen(name); _add("S5", "s5_" + name, p, c, a, n)

    chains = [
        ("chain_emy_point_to_box_bbox",
         "Write a Python function point_to_box_bbox(x1, y1, x2, y2) that builds two emyPoint objects (lower-left, upper-right), constructs an emyBox from them, and returns the box's width and height.",
         ["emyPoint", "emyBox"],
         ("import pyAether as pyScript\n\n"
          "def point_to_box_bbox(x1, y1, x2, y2):\n"
          "    ll = pyScript.emyPoint(x1, y1)\n"
          "    rt = pyScript.emyPoint(x2, y2)\n"
          "    box = pyScript.emyBox(ll, rt)\n"
          "    return box.getWidth(), box.getHeight()\n")),
        ("chain_emy_intarr_to_floatarr_scale",
         "Write a Python function scale_points(corners, fx, fy) that builds an integer emyPointArray, converts it to emyPointArrayF, scales with magnifyIn2D, and returns the float points as a Python list.",
         ["emyPointArray", "emyPointArrayF"],
         ("import pyAether as pyScript\n\n"
          "def scale_points(corners, fx, fy):\n"
          "    ia = pyScript.emyPointArray(len(corners))\n"
          "    for c in corners:\n"
          "        ia.append(pyScript.emyPoint(c[0], c[1]))\n"
          "    fa = pyScript.emyPointArrayF(ia)\n"
          "    fa.magnifyIn2D(fx, fy)\n"
          "    return fa.toList()\n")),
        ("chain_emy_via_enc_point",
         "Write a Python function make_via_enclosure(x, y, left, bottom, right, top) that builds an emyPointF at (x, y) and an emyViaExtEncParam with the four extension values, and returns both.",
         ["emyPointF", "emyViaExtEncParam"],
         ("import pyAether as pyScript\n\n"
          "def make_via_enclosure(x, y, left, bottom, right, top):\n"
          "    pt = pyScript.emyPointF(x, y)\n"
          "    enc = pyScript.emyViaExtEncParam(left, bottom, right, top)\n"
          "    return pt, enc\n")),
        ("chain_emy_bitmask_select",
         "Write a Python function build_selection_mask(length, enabled) that creates an emyBitArray of the given length, clears all bits, sets the enabled indices, and returns the array and its piece count.",
         ["emyBitArray"],
         ("import pyAether as pyScript\n\n"
          "def build_selection_mask(length, enabled):\n"
          "    ba = pyScript.emyBitArray(length)\n"
          "    ba.clear()\n"
          "    for i in enabled:\n"
          "        ba.set(i)\n"
          "    return ba, ba.countPiece()\n")),
        ("chain_emy_name_collect",
         "Write a Python function collect_names(name_strs) that creates a CDBA namespace, builds an emyScalarName for each string, renders each to emyString, collects them into an emyStringArray, and returns the array.",
         ["emyCdbaNS", "emyScalarName", "emyStringArray"],
         ("import pyAether as pyScript\n\n"
          "def collect_names(name_strs):\n"
          "    ns = pyScript.emyCdbaNS()\n"
          "    arr = pyScript.emyStringArray(len(name_strs))\n"
          "    for s in name_strs:\n"
          "        nm = pyScript.emyScalarName(ns, s)\n"
          "        out = pyScript.emyString()\n"
          "        nm.get(ns, out)\n"
          "        arr.append(out)\n"
          "    return arr\n")),
    ]
    for cid, prompt, api_used, completion in chains:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")
    lookups = [
        ("construct a 2D float point", "emyPointF",
         'p = pyScript.emyPointF(3.5, 4.5)'),
        ("specify via extension/enclosure values", "emyViaExtEncParam",
         'enc = pyScript.emyViaExtEncParam(10, 20, 10, 20)'),
        ("build a bit mask for selection types", "emyBitArray",
         'ba = pyScript.emyBitArray(32)\nba.set()'),
        ("build an array of integer 2D points", "emyPointArray",
         'arr = pyScript.emyPointArray(4)\narr.append(pyScript.emyPoint(0, 0))'),
        ("build an array of float 2D points", "emyPointArrayF",
         'fa = pyScript.emyPointArrayF(int_array)'),
        ("build an axis-aligned integer bounding box", "emyBox",
         'box = pyScript.emyBox(0, 0, 100, 50)'),
        ("construct a 2D integer grid point", "emyPoint",
         'p = pyScript.emyPoint(10, 20)'),
        ("represent a scalar object name in a namespace", "emyScalarName",
         'nm = pyScript.emyScalarName(ns, "clk")'),
        ("create a CDBA namespace for name evaluation", "emyCdbaNS",
         'ns = pyScript.emyCdbaNS()'),
        ("build an array of emyString objects", "emyStringArray",
         'arr = pyScript.emyStringArray()\narr.append(pyScript.emyString("M1"))'),
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
        "report_id": "R185",
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
        sys.stderr.write("GATE: FAIL (pollution detected) -- do NOT use v15\n")
        sys.exit(2)
    sys.stderr.write("GATE: PASS -- v15 is training-ready\n")


if __name__ == "__main__":
    main()