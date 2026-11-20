#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r192_emy_geometry_lib_tech_corpus.py
R192 -- v22 PyAether SFT corpus: emy* geometry / library-access /
SWIG-container / tech-database blind spot (13 APIs, 65 pairs).

BACKGROUND: v11-v21 (483 pairs) cover 84/164 eval raw APIs (51.2%). 80 blind.
Data-driven scan (R191 blind_scan, re-run with v21 this wake) shows emy* is
the largest blind family: 16 usages / 13 APIs. R192 targets 13 emy* APIs.
All ISOLATE-class (eval_count>0). Fingerprint scan rejects eval entry_points.

Authoritative signatures fetched via pyAether MCP get_api_details (R192 wake).

Usage:
  python3 baize_posttrain_r192_emy_geometry_lib_tech_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v22_emy_geometry_lib_tech.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["emyPointArrayIsClockwise"] = {
    "sig": "emyPointArrayIsClockwise(pa: emyPointArray) -> emyBoolean  [overloaded: also (pa: emyPointArrayF)]",
    "desc": "Returns True if the point array direction is clockwise, False if counter-clockwise. Uses the signed-area (shoelace) formula: negative area = clockwise. Degenerate cases (< 3 points, collinear) return False.",
    "params": {"pa": "emyPointArray or emyPointArrayF - polygon vertices in order"},
    "returns": "emyBoolean - True if clockwise, False otherwise",
    "methods": "Overloaded: accepts emyPointArray (int coords) or emyPointArrayF (float coords)",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pts = pyScript.emyPointArray()\n'
                '>>> pts.append(pyScript.emyPoint(0, 0))\n'
                '>>> pts.append(pyScript.emyPoint(0, 10))\n'
                '>>> pts.append(pyScript.emyPoint(10, 10))\n'
                '>>> pts.append(pyScript.emyPoint(10, 0))\n'
                '>>> print(pyScript.emyPointArrayIsClockwise(pts))  # True'),
    "category": "emy Geometry / Winding", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Shoelace formula. emyBox-constructed arrays start at lower-left and are clockwise. Affine transforms preserve winding. Needs >= 3 points."}

API_DOCS["emyPointArrayIsConvex"] = {
    "sig": "emyPointArrayIsConvex(pa: emyPointArray) -> emyBoolean  [overloaded: also (pa: emyPointArrayF)]",
    "desc": "Returns True if the polygon is convex, False if concave or indeterminate (collinear, < 3 pts). Convex if all consecutive edge cross-products have the same sign.",
    "params": {"pa": "emyPointArray or emyPointArrayF - polygon vertices"},
    "returns": "emyBoolean - True if convex, False if concave/indeterminate",
    "methods": "Overloaded: accepts emyPointArray or emyPointArrayF",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> sq = pyScript.emyPointArray()\n'
                '>>> sq.append(pyScript.emyPoint(0, 0))\n'
                '>>> sq.append(pyScript.emyPoint(10, 0))\n'
                '>>> sq.append(pyScript.emyPoint(10, 10))\n'
                '>>> sq.append(pyScript.emyPoint(0, 10))\n'
                '>>> print(pyScript.emyPointArrayIsConvex(sq))  # True'),
    "category": "emy Geometry / Convexity", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Cross-product sign check. Degenerate returns False. Works on int and float arrays."}

API_DOCS["emyPointArrayScaleSegments"] = {
    "sig": "emyPointArrayScaleSegments(src: emyPointArray, dst: emyPointArray) -> emyArray_emySegment",
    "desc": "Gets moved segments from two related point arrays. Returns emyArray_emySegment of segments that differ between source and destination. Useful for geometric deltas.",
    "params": {"src": "emyPointArray - original vertices", "dst": "emyPointArray - modified vertices"},
    "returns": "emyArray_emySegment - array of moved segments",
    "methods": "Returns container; iterate or index",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> src = pyScript.emyPointArray()\n'
                '>>> src.append(pyScript.emyPoint(0, 0))\n'
                '>>> src.append(pyScript.emyPoint(10, 0))\n'
                '>>> dst = pyScript.emyPointArray()\n'
                '>>> dst.append(pyScript.emyPoint(0, 0))\n'
                '>>> dst.append(pyScript.emyPoint(20, 0))\n'
                '>>> segs = pyScript.emyPointArrayScaleSegments(src, dst)\n'
                '>>> print(len(segs))'),
    "category": "emy Geometry / Segment Delta", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Source/dest same vertex count, vertex-to-vertex. Returns only changed segments. Each emySegment has getDeltaX()/getDeltaY()."}


API_DOCS["emyPolygonChopByPolygon"] = {
    "sig": "emyPolygonChopByPolygon(polygon, chopper, outside, inside) -> emyBoolean",
    "desc": "Polygon boolean difference (chop). Cuts 'polygon' with 'chopper': fills 'outside' with exterior (polygon minus chopper) and 'inside' with interior (intersection). Returns True on success, False if no overlap.",
    "params": {
        "polygon": "emyPointArray - polygon to cut",
        "chopper": "emyPointArray - cutting polygon",
        "outside": "emyArray_p_emyPointArray - output: exterior (pre-create)",
        "inside": "emyArray_p_emyPointArray - output: interior (pre-create)",
    },
    "returns": "emyBoolean - True if succeeded, False on failure",
    "methods": "Output arrays pre-created. Results via len() and indexing.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> poly = pyScript.emyPointArray()\n'
                '>>> for pt in [(0,0),(100,0),(100,100),(0,100)]:\n'
                '...     poly.append(pyScript.emyPoint(*pt))\n'
                '>>> chopper = pyScript.emyPointArray()\n'
                '>>> for pt in [(20,20),(80,20),(80,80),(20,80)]:\n'
                '...     chopper.append(pyScript.emyPoint(*pt))\n'
                '>>> outside = pyScript.emyArray_p_emyPointArray()\n'
                '>>> inside = pyScript.emyArray_p_emyPointArray()\n'
                '>>> ok = pyScript.emyPolygonChopByPolygon(poly, chopper, outside, inside)\n'
                '>>> print(ok, len(outside), len(inside))'),
    "category": "emy Geometry / Boolean Difference", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Pre-allocate outside/inside. Polygons implicitly closed. False on no overlap. Integer coords. No exceptions -- check return."}

API_DOCS["emyPointArrayGOA"] = {
    "sig": "emyPointArrayGOA(poly1, poly2, result, op) -> emyBoolean  [3 overloads]",
    "desc": "Geometric Operation on Arrays. Boolean op (AND/OR/SUB/XOR) between polygons, results to output emyArray_p_emyPointArray. True on success.",
    "params": {
        "poly1": "emyPointArray or emyArray_p_emyPointArray - first input",
        "poly2": "emyPointArray or emyArray_p_emyPointArray - second input",
        "result": "emyArray_p_emyPointArray - output (pre-create)",
        "op": "SLE_GOA_AND / SLE_GOA_OR / SLE_GOA_SUB / SLE_GOA_XOR",
    },
    "returns": "emyBoolean - True on success, False on failure",
    "methods": "3 overloads: single-poly, poly-array (with bSplitGraph), single-array-merge",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> p1 = pyScript.emyPointArray()\n'
                '>>> for pt in [(0,0),(10,0),(10,10),(0,10)]:\n'
                '...     p1.append(pyScript.emyPoint(*pt))\n'
                '>>> p2 = pyScript.emyPointArray()\n'
                '>>> for pt in [(5,5),(15,5),(15,15),(5,15)]:\n'
                '...     p2.append(pyScript.emyPoint(*pt))\n'
                '>>> result = pyScript.emyArray_p_emyPointArray()\n'
                '>>> ok = pyScript.emyPointArrayGOA(p1, p2, result, pyScript.SLE_GOA_AND)\n'
                '>>> print(ok, len(result))'),
    "category": "emy Geometry / Boolean Operation", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Enums: AND(intersection), OR(union), SUB(difference), XOR(xor). Pre-create output. bSplitGraph=True splits compound. Invalid enum raises ValueError."}


API_DOCS["emyLibAccess"] = {
    "sig": "emyLibAccess(valueIn: emyLibAccessEnum)  or  emyLibAccess(name: emyString)  [class]",
    "desc": "Utility wrapper for emyLibAccessEnum (library access permissions). Enums: emcReadLibAccess ('read') and emcWriteLibAccess ('write'). Construct with enum constant or string name.",
    "params": {"valueIn": "emyLibAccessEnum - emcReadLibAccess or emcWriteLibAccess", "name": "emyString/str - 'read' or 'write'"},
    "returns": "emyLibAccess instance",
    "methods": "getName() -> emyString; emyLibAccessEnum() -> int; __eq__(other) (unreliable -- use getName())",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> read_acc = pyScript.emyLibAccess("read")\n'
                '>>> print(str(read_acc.getName()))  # read\n'
                '>>> write_acc = pyScript.emyLibAccess(pyScript.emcWriteLibAccess)\n'
                '>>> print(write_acc.emyLibAccessEnum())  # 1'),
    "category": "emy Library / Access", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "emcReadLibAccess=0 ('read'), emcWriteLibAccess=1 ('write'). __eq__ unreliable -- compare getName(). str gives 'LibAccess: (Name: read)'."}

API_DOCS["emyLibAccessExt"] = {
    "sig": "emyLibAccessExt(lib: emyLib, access: emyLibAccess)  [class]",
    "desc": "Extended library-access wrapper bundling emyLib + emyLibAccess into one passable object. Used for library-search-path config with per-library access control. getLib() retrieves library, getAccess() retrieves permission.",
    "params": {"lib": "emyLib - library object", "access": "emyLibAccess - access permission"},
    "returns": "emyLibAccessExt instance",
    "methods": "getLib() -> emyLib; getAccess() -> emyLibAccess",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.emyLib("my_lib")\n'
                '>>> acc = pyScript.emyLibAccess("read")\n'
                '>>> ext = pyScript.emyLibAccessExt(lib, acc)\n'
                '>>> got_acc = ext.getAccess()\n'
                '>>> print(str(got_acc.getName()))  # read'),
    "category": "emy Library / Extended Access", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Combines emyLib + emyLibAccess. Use getLib()/getAccess() to retrieve components. Useful for per-library access config."}

API_DOCS["emySegStyle"] = {
    "sig": "emySegStyle(...)  [class]",
    "desc": "Defines style of path segments -- expanded size and shape. Used by emyPathSeg.setStyle()/getStyle(). Controls width, end-cap, join style for path-segment expansion in layout.",
    "params": {"...": "constructor params for segment style (width, expansion mode)"},
    "returns": "emySegStyle instance",
    "methods": "Used with emyPathSeg.setStyle(style) and emyPathSeg.getStyle() -> emySegStyle",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> style = pyScript.emySegStyle()\n'
                '>>> seg = pyScript.emyPathSeg()\n'
                '>>> seg.setStyle(style)\n'
                '>>> got = seg.getStyle()\n'
                '>>> print(got is not None)'),
    "category": "emy Geometry / Segment Style", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Controls path-segment expansion. Apply via emyPathSeg.setStyle(); retrieve via getStyle(). Default constructor creates empty style."}


API_DOCS["emyTech"] = {
    "sig": "emyTech  [class; static + instance methods for tech database]",
    "desc": "Technology database class. Access to layers, LPPs, purposes, viaDefs, constraint groups. Static methods work without open db; instance methods require open tech database.",
    "params": {},
    "returns": "emyTech instance (tech db handle)",
    "methods": ("static: getDefaultViewType()->emyViewType; getViewTypes()->collection; "
                "instance: getLayers()/getLPPs()/getPurposes()/getViaDefs()->collection; "
                "getMode()->int; getFileName()->str; getLibName()->str; "
                "isModified()->bool; close()->bool; purge()->None; "
                "setCp(id)->None; undo()/redo()->None; isUndoEnabled()->bool"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> vt = pyScript.emyTech.getDefaultViewType()\n'
                '>>> print(vt is not None)\n'
                '>>> vts = pyScript.emyTech.getViewTypes()\n'
                '>>> print(len(vts))'),
    "category": "emy Database / Technology", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Static methods work without open db. Instance methods need open db. close() decrements refcount; purge() force-removes. Not thread-safe. Properties: layers, lpps, purposes, viaDefs, mode, fileName, path, libName."}

API_DOCS["emyArray_p_emyPointArray"] = {
    "sig": "emyArray_p_emyPointArray  [SWIG container: List[emyPointArray]]",
    "desc": "SWIG container mapping to List[emyPointArray]. Output param in GOA/chop ops. Supports append(), len(), indexing, iteration, transList().",
    "params": {},
    "returns": "emyArray_p_emyPointArray instance (empty)",
    "methods": "append(poly)->None; len()->int; __getitem__(i)->emyPointArray; __iter__(); transList(nested_list)->None",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> arr = pyScript.emyArray_p_emyPointArray()\n'
                '>>> poly = pyScript.emyPointArray()\n'
                '>>> poly.append(pyScript.emyPoint(0, 0))\n'
                '>>> poly.append(pyScript.emyPoint(10, 0))\n'
                '>>> poly.append(pyScript.emyPoint(10, 10))\n'
                '>>> arr.append(poly)\n'
                '>>> print(len(arr))  # 1\n'
                '>>> print(len(arr[0]))  # 3'),
    "category": "emy Container / PointArray List", "safety": "ISOLATE", "eval_count": 3,
    "key_notes": "Pre-create before passing as output to GOA/chop. transList() accepts nested Python lists like [[(0,0),(10,0),(10,10)]]. arr[i] returns emyPointArray."}

API_DOCS["emyArray_emyUInt4"] = {
    "sig": "emyArray_emyUInt4  [SWIG container: List[emyUInt4]  (emyUInt4 -> Python int)]",
    "desc": "SWIG container for emyUInt4 (unsigned 4-byte int) values. Maps to typed list of non-negative ints. Used for layer/purpose number arrays.",
    "params": {},
    "returns": "emyArray_emyUInt4 instance (empty)",
    "methods": "append(val:int)->None; get(i)->int; len()->int; __getitem__(i)->int; __iter__(); getNumElements()->int",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> arr = pyScript.emyArray_emyUInt4()\n'
                '>>> arr.append(1)\n'
                '>>> arr.append(2)\n'
                '>>> arr.append(3)\n'
                '>>> print(len(arr))  # 3\n'
                '>>> print(arr[0])  # 1'),
    "category": "emy Container / UInt4 List", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Values non-negative, fit 32 bits (0-4294967295). Use append() to add, arr[i] or get(i) to retrieve. Common: layer/purpose number arrays."}

API_DOCS["emyArray_emyScalarName"] = {
    "sig": "emyArray_emyScalarName  [type alias: List[emyScalarName]]",
    "desc": "Type alias for List[emyScalarName]. Standard Python list for emyScalarName objects. Used for batch names, net names, hierarchical paths.",
    "params": {},
    "returns": "list (typed emyArray_emyScalarName)",
    "methods": "Standard Python list: append(), len(), [i], iteration, comprehension",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> ns = pyScript.emyNativeNS()\n'
                '>>> names = []  # emyArray_emyScalarName\n'
                '>>> names.append(pyScript.emyScalarName(ns, "inst1"))\n'
                '>>> names.append(pyScript.emyScalarName(ns, "inst2"))\n'
                '>>> print(len(names))  # 2'),
    "category": "emy Container / ScalarName List", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Plain Python list. emyScalarName needs namespace + name string. Ensure same namespace for all elements."}

API_DOCS["emyArray_emySegment"] = {
    "sig": "emyArray_emySegment  [container class for emySegment]",
    "desc": "Type-safe container for emySegment objects. append(), get(), find(), len(), indexing, iteration. Returned by emyPointArrayScaleSegments.",
    "params": {},
    "returns": "emyArray_emySegment instance (empty)",
    "methods": "append(seg)->None; get(i)->emySegment; find(seg)->int(-1 if not found); getNumElements()->int; len()->int; __getitem__(i); __iter__(); sort(); remove(seg)",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> arr = pyScript.emyArray_emySegment()\n'
                '>>> seg1 = pyScript.emySegment(pyScript.emyPoint(0, 0), pyScript.emyPoint(10, 0))\n'
                '>>> seg2 = pyScript.emySegment(pyScript.emyPoint(5, 5), pyScript.emyPoint(15, 5))\n'
                '>>> arr.append(seg1)\n'
                '>>> arr.append(seg2)\n'
                '>>> print(len(arr))  # 2\n'
                '>>> print(arr.find(seg2))  # 1'),
    "category": "emy Container / Segment List", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Type-safe: non-emySegment append raises TypeError. Use arr[i]=seg (not set() -- has bug). remove() takes object not index. find() returns -1 if not found."}


API_ORDER = ["emyPointArrayIsClockwise", "emyPointArrayIsConvex",
             "emyPointArrayScaleSegments", "emyPolygonChopByPolygon",
             "emyPointArrayGOA", "emyLibAccess", "emyLibAccessExt",
             "emySegStyle", "emyTech",
             "emyArray_p_emyPointArray", "emyArray_emyUInt4",
             "emyArray_emyScalarName", "emyArray_emySegment"]


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
        _add("S1", "v22-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)


    # ---- S4: multi-step trace (13 pairs) ----
    s4_traces = [
        ("emyPointArrayIsClockwise",
         "Build a clockwise square, check winding, then a counter-clockwise one and compare.",
         ["emyPointArrayIsClockwise"],
         ("import pyAether as pyScript\n\n"
          "cw = pyScript.emyPointArray()\n"
          "cw.append(pyScript.emyPoint(0, 0))\n"
          "cw.append(pyScript.emyPoint(0, 10))\n"
          "cw.append(pyScript.emyPoint(10, 10))\n"
          "cw.append(pyScript.emyPoint(10, 0))\n"
          "print(pyScript.emyPointArrayIsClockwise(cw))  # True\n\n"
          "ccw = pyScript.emyPointArray()\n"
          "ccw.append(pyScript.emyPoint(0, 0))\n"
          "ccw.append(pyScript.emyPoint(10, 0))\n"
          "ccw.append(pyScript.emyPoint(10, 10))\n"
          "ccw.append(pyScript.emyPoint(0, 10))\n"
          "print(pyScript.emyPointArrayIsClockwise(ccw))  # False")),
        ("emyPointArrayIsConvex",
         "Create a convex square and a concave L-shape, check convexity on both.",
         ["emyPointArrayIsConvex"],
         ("import pyAether as pyScript\n\n"
          "sq = pyScript.emyPointArray()\n"
          "sq.append(pyScript.emyPoint(0, 0))\n"
          "sq.append(pyScript.emyPoint(10, 0))\n"
          "sq.append(pyScript.emyPoint(10, 10))\n"
          "sq.append(pyScript.emyPoint(0, 10))\n"
          "print(pyScript.emyPointArrayIsConvex(sq))  # True\n\n"
          "lshape = pyScript.emyPointArray()\n"
          "lshape.append(pyScript.emyPoint(0, 0))\n"
          "lshape.append(pyScript.emyPoint(10, 0))\n"
          "lshape.append(pyScript.emyPoint(10, 5))\n"
          "lshape.append(pyScript.emyPoint(5, 5))\n"
          "lshape.append(pyScript.emyPoint(5, 10))\n"
          "lshape.append(pyScript.emyPoint(0, 10))\n"
          "print(pyScript.emyPointArrayIsConvex(lshape))  # False")),
        ("emyPointArrayScaleSegments",
         "Create source rect, modify one edge in dest, extract moved segments.",
         ["emyPointArrayScaleSegments", "emyArray_emySegment"],
         ("import pyAether as pyScript\n\n"
          "src = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(10,0),(10,10),(0,10)]:\n"
          "    src.append(pyScript.emyPoint(*pt))\n"
          "dst = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(20,0),(20,10),(0,10)]:\n"
          "    dst.append(pyScript.emyPoint(*pt))\n"
          "segs = pyScript.emyPointArrayScaleSegments(src, dst)\n"
          "print(len(segs))\n"
          "for s in segs:\n"
          "    print(s.getDeltaX(), s.getDeltaY())")),
        ("emyPolygonChopByPolygon",
         "Chop a 100x100 polygon with centered 60x60 rect, report outside/inside.",
         ["emyPolygonChopByPolygon", "emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "poly = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(100,0),(100,100),(0,100)]:\n"
          "    poly.append(pyScript.emyPoint(*pt))\n"
          "chopper = pyScript.emyPointArray()\n"
          "for pt in [(20,20),(80,20),(80,80),(20,80)]:\n"
          "    chopper.append(pyScript.emyPoint(*pt))\n"
          "outside = pyScript.emyArray_p_emyPointArray()\n"
          "inside = pyScript.emyArray_p_emyPointArray()\n"
          "ok = pyScript.emyPolygonChopByPolygon(poly, chopper, outside, inside)\n"
          "print(ok, len(outside), len(inside))\n"
          "if ok:\n"
          "    for i in range(len(outside)):\n"
          "        print('outside poly', i, 'has', len(outside[i]), 'pts')")),
        ("emyPointArrayGOA",
         "Compute intersection (AND) and union (OR) of two overlapping squares.",
         ["emyPointArrayGOA", "emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "p1 = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(10,0),(10,10),(0,10)]:\n"
          "    p1.append(pyScript.emyPoint(*pt))\n"
          "p2 = pyScript.emyPointArray()\n"
          "for pt in [(5,5),(15,5),(15,15),(5,15)]:\n"
          "    p2.append(pyScript.emyPoint(*pt))\n"
          "res_and = pyScript.emyArray_p_emyPointArray()\n"
          "ok1 = pyScript.emyPointArrayGOA(p1, p2, res_and, pyScript.SLE_GOA_AND)\n"
          "print(ok1, len(res_and))\n"
          "res_or = pyScript.emyArray_p_emyPointArray()\n"
          "ok2 = pyScript.emyPointArrayGOA(p1, p2, res_or, pyScript.SLE_GOA_OR)\n"
          "print(ok2, len(res_or))")),
    ]
    for name, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v22-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)


    s4_traces_2 = [
        ("emyLibAccess",
         "Create read/write access via string and enum constructors, compare them.",
         ["emyLibAccess"],
         ("import pyAether as pyScript\n\n"
          "read1 = pyScript.emyLibAccess('read')\n"
          "write1 = pyScript.emyLibAccess('write')\n"
          "read2 = pyScript.emyLibAccess(pyScript.emcReadLibAccess)\n"
          "write2 = pyScript.emyLibAccess(pyScript.emcWriteLibAccess)\n"
          "print(str(read1.getName()))   # read\n"
          "print(str(write1.getName()))  # write\n"
          "print(read1.emyLibAccessEnum())   # 0\n"
          "print(write2.emyLibAccessEnum())  # 1\n"
          "print(read1.emyLibAccessEnum() == read2.emyLibAccessEnum())")),
        ("emyLibAccessExt",
         "Create a library, wrap with read access, retrieve both components.",
         ["emyLibAccessExt", "emyLibAccess"],
         ("import pyAether as pyScript\n\n"
          "lib = pyScript.emyLib('design_lib')\n"
          "acc = pyScript.emyLibAccess('read')\n"
          "ext = pyScript.emyLibAccessExt(lib, acc)\n"
          "got_lib = ext.getLib()\n"
          "got_acc = ext.getAccess()\n"
          "print(str(got_acc.getName()))  # read\n"
          "print(got_lib is not None)")),
        ("emySegStyle",
         "Create a segment style, apply to a path segment, retrieve and verify.",
         ["emySegStyle"],
         ("import pyAether as pyScript\n\n"
          "style = pyScript.emySegStyle()\n"
          "seg = pyScript.emyPathSeg()\n"
          "seg.setStyle(style)\n"
          "got = seg.getStyle()\n"
          "print(got is not None)\n"
          "print(type(got).__name__)")),
        ("emyTech",
         "Use static methods to get default view type and list all view types.",
         ["emyTech"],
         ("import pyAether as pyScript\n\n"
          "vt = pyScript.emyTech.getDefaultViewType()\n"
          "print(vt is not None)\n"
          "vts = pyScript.emyTech.getViewTypes()\n"
          "print(len(vts))\n"
          "for v in vts:\n"
          "    print(type(v).__name__)")),
        ("emyArray_p_emyPointArray",
         "Create container, append two polygons, iterate and count points each.",
         ["emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "arr = pyScript.emyArray_p_emyPointArray()\n"
          "for corners in [[(0,0),(10,0),(10,10)], [(5,5),(15,5),(15,15),(5,15)]]:\n"
          "    poly = pyScript.emyPointArray()\n"
          "    for pt in corners:\n"
          "        poly.append(pyScript.emyPoint(*pt))\n"
          "    arr.append(poly)\n"
          "print(len(arr))  # 2\n"
          "for i in range(len(arr)):\n"
          "    print('poly', i, 'has', len(arr[i]), 'pts')")),
        ("emyArray_emyUInt4",
         "Create container, append layer numbers, iterate and compute sum.",
         ["emyArray_emyUInt4"],
         ("import pyAether as pyScript\n\n"
          "arr = pyScript.emyArray_emyUInt4()\n"
          "for n in [1, 2, 3, 5, 8]:\n"
          "    arr.append(n)\n"
          "print(len(arr))  # 5\n"
          "total = 0\n"
          "for i in range(len(arr)):\n"
          "    total += arr[i]\n"
          "print(total)  # 19")),
        ("emyArray_emyScalarName",
         "Create namespace, build list of scalar names, iterate and print each.",
         ["emyArray_emyScalarName"],
         ("import pyAether as pyScript\n\n"
          "ns = pyScript.emyNativeNS()\n"
          "names = []\n"
          "for n in ['inst1', 'inst2', 'inst3']:\n"
          "    names.append(pyScript.emyScalarName(ns, n))\n"
          "print(len(names))  # 3\n"
          "for nm in names:\n"
          "    out = pyScript.emyString()\n"
          "    nm.get(out)\n"
          "    print(str(out))")),
        ("emyArray_emySegment",
         "Create segments, add to container, find by identity, then iterate.",
         ["emyArray_emySegment"],
         ("import pyAether as pyScript\n\n"
          "arr = pyScript.emyArray_emySegment()\n"
          "seg1 = pyScript.emySegment(pyScript.emyPoint(0, 0), pyScript.emyPoint(10, 0))\n"
          "seg2 = pyScript.emySegment(pyScript.emyPoint(5, 5), pyScript.emyPoint(15, 5))\n"
          "arr.append(seg1)\n"
          "arr.append(seg2)\n"
          "print(len(arr))  # 2\n"
          "print(arr.find(seg2))  # 1\n"
          "for s in arr:\n"
          "    print(s.getDeltaX(), s.getDeltaY())")),
    ]
    for name, scenario, apis, code in s4_traces_2:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v22-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)


    # ---- S5: param variation (13 pairs) ----
    s5_variants = [
        ("emyPointArrayIsClockwise",
         "Show a triangle and a pentagon, check winding on both.",
         ["emyPointArrayIsClockwise"],
         ("import pyAether as pyScript\n\n"
          "# clockwise triangle\n"
          "tri = pyScript.emyPointArray()\n"
          "tri.append(pyScript.emyPoint(0, 0))\n"
          "tri.append(pyScript.emyPoint(2, 5))\n"
          "tri.append(pyScript.emyPoint(5, 0))\n"
          "print(pyScript.emyPointArrayIsClockwise(tri))  # True\n\n"
          "# counter-clockwise pentagon\n"
          "pent = pyScript.emyPointArray()\n"
          "pent.append(pyScript.emyPoint(0, 0))\n"
          "pent.append(pyScript.emyPoint(5, 0))\n"
          "pent.append(pyScript.emyPoint(7, 4))\n"
          "pent.append(pyScript.emyPoint(3, 7))\n"
          "pent.append(pyScript.emyPoint(-1, 4))\n"
          "print(pyScript.emyPointArrayIsClockwise(pent))  # False")),
        ("emyPointArrayIsConvex",
         "Show a triangle (always convex) and a star (concave).",
         ["emyPointArrayIsConvex"],
         ("import pyAether as pyScript\n\n"
          "# triangle (always convex)\n"
          "tri = pyScript.emyPointArray()\n"
          "tri.append(pyScript.emyPoint(0, 0))\n"
          "tri.append(pyScript.emyPoint(10, 0))\n"
          "tri.append(pyScript.emyPoint(5, 8))\n"
          "print(pyScript.emyPointArrayIsConvex(tri))  # True\n\n"
          "# concave star\n"
          "star = pyScript.emyPointArray()\n"
          "star.append(pyScript.emyPoint(0, 5))\n"
          "star.append(pyScript.emyPoint(4, 4))\n"
          "star.append(pyScript.emyPoint(5, 0))\n"
          "star.append(pyScript.emyPoint(6, 4))\n"
          "star.append(pyScript.emyPoint(10, 5))\n"
          "star.append(pyScript.emyPoint(6, 6))\n"
          "star.append(pyScript.emyPoint(5, 10))\n"
          "star.append(pyScript.emyPoint(4, 6))\n"
          "print(pyScript.emyPointArrayIsConvex(star))  # False")),
        ("emyPointArrayScaleSegments",
         "Show two scenarios: (a) no change -> 0 segments, (b) all edges moved.",
         ["emyPointArrayScaleSegments"],
         ("import pyAether as pyScript\n\n"
          "# (a) no change\n"
          "src = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(10,0),(10,10),(0,10)]:\n"
          "    src.append(pyScript.emyPoint(*pt))\n"
          "dst_a = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(10,0),(10,10),(0,10)]:\n"
          "    dst_a.append(pyScript.emyPoint(*pt))\n"
          "segs_a = pyScript.emyPointArrayScaleSegments(src, dst_a)\n"
          "print(len(segs_a))  # 0\n\n"
          "# (b) all edges moved (scaled 2x)\n"
          "dst_b = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(20,0),(20,20),(0,20)]:\n"
          "    dst_b.append(pyScript.emyPoint(*pt))\n"
          "segs_b = pyScript.emyPointArrayScaleSegments(src, dst_b)\n"
          "print(len(segs_b))")),
        ("emyPolygonChopByPolygon",
         "Show (a) chopper fully inside, (b) chopper partially outside (no overlap edge).",
         ["emyPolygonChopByPolygon", "emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "# (a) chopper fully inside\n"
          "poly = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(100,0),(100,100),(0,100)]:\n"
          "    poly.append(pyScript.emyPoint(*pt))\n"
          "chop_a = pyScript.emyPointArray()\n"
          "for pt in [(30,30),(70,30),(70,70),(30,70)]:\n"
          "    chop_a.append(pyScript.emyPoint(*pt))\n"
          "out_a = pyScript.emyArray_p_emyPointArray()\n"
          "in_a = pyScript.emyArray_p_emyPointArray()\n"
          "print(pyScript.emyPolygonChopByPolygon(poly, chop_a, out_a, in_a))\n\n"
          "# (b) chopper completely outside -> False\n"
          "chop_b = pyScript.emyPointArray()\n"
          "for pt in [(200,200),(300,200),(300,300),(200,300)]:\n"
          "    chop_b.append(pyScript.emyPoint(*pt))\n"
          "out_b = pyScript.emyArray_p_emyPointArray()\n"
          "in_b = pyScript.emyArray_p_emyPointArray()\n"
          "print(pyScript.emyPolygonChopByPolygon(poly, chop_b, out_b, in_b))  # False")),
        ("emyPointArrayGOA",
         "Show AND, SUB, and XOR on the same two overlapping squares.",
         ["emyPointArrayGOA", "emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "p1 = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(10,0),(10,10),(0,10)]:\n"
          "    p1.append(pyScript.emyPoint(*pt))\n"
          "p2 = pyScript.emyPointArray()\n"
          "for pt in [(5,5),(15,5),(15,15),(5,15)]:\n"
          "    p2.append(pyScript.emyPoint(*pt))\n"
          "for op_name, op in [('AND', pyScript.SLE_GOA_AND),\n"
          "                     ('SUB', pyScript.SLE_GOA_SUB),\n"
          "                     ('XOR', pyScript.SLE_GOA_XOR)]:\n"
          "    res = pyScript.emyArray_p_emyPointArray()\n"
          "    ok = pyScript.emyPointArrayGOA(p1, p2, res, op)\n"
          "    print(op_name, ok, len(res))")),
    ]
    for name, scenario, apis, code in s5_variants:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S5", "v22-S5-%s" % name, prompt, completion, apis,
             "S5 param_variation for %s" % name)


    s5_variants_2 = [
        ("emyLibAccess",
         "Show all four access types (read, write, update, delete) via both constructor styles.",
         ["emyLibAccess"],
         ("import pyAether as pyScript\n\n"
          "for name, const in [('read', pyScript.emcReadLibAccess),\n"
          "                    ('write', pyScript.emcWriteLibAccess),\n"
          "                    ('update', pyScript.emcUpdateLibAccess),\n"
          "                    ('delete', pyScript.emcDeleteLibAccess)]:\n"
          "    a1 = pyScript.emyLibAccess(name)\n"
          "    a2 = pyScript.emyLibAccess(const)\n"
          "    print(str(a1.getName()), a1.emyLibAccessEnum(),\n"
          "          a1.emyLibAccessEnum() == a2.emyLibAccessEnum())")),
        ("emyLibAccessExt",
         "Show wrapping with different access levels (read, write, update).",
         ["emyLibAccessExt", "emyLibAccess"],
         ("import pyAether as pyScript\n\n"
          "lib = pyScript.emyLib('design_lib')\n"
          "for acc_name in ['read', 'write', 'update']:\n"
          "    acc = pyScript.emyLibAccess(acc_name)\n"
          "    ext = pyScript.emyLibAccessExt(lib, acc)\n"
          "    got = ext.getAccess()\n"
          "    print(acc_name, str(got.getName()), got.emyLibAccessEnum())")),
        ("emySegStyle",
         "Show creating a style, setting it on two segments, and checking identity.",
         ["emySegStyle"],
         ("import pyAether as pyScript\n\n"
          "style = pyScript.emySegStyle()\n"
          "seg1 = pyScript.emyPathSeg()\n"
          "seg2 = pyScript.emyPathSeg()\n"
          "seg1.setStyle(style)\n"
          "seg2.setStyle(style)\n"
          "g1 = seg1.getStyle()\n"
          "g2 = seg2.getStyle()\n"
          "print(g1 is not None, g2 is not None)\n"
          "print(type(g1).__name__, type(g2).__name__)")),
        ("emyTech",
         "Show getViewTypes and getDefaultViewType, then check if default is in the list.",
         ["emyTech"],
         ("import pyAether as pyScript\n\n"
          "dv = pyScript.emyTech.getDefaultViewType()\n"
          "print('default:', dv is not None)\n"
          "vts = pyScript.emyTech.getViewTypes()\n"
          "print('count:', len(vts))\n"
          "found = False\n"
          "for v in vts:\n"
          "    if str(v) == str(dv):\n"
          "        found = True\n"
          "        break\n"
          "print('default in list:', found)")),
        ("emyArray_p_emyPointArray",
         "Show transList() to bulk-load polygons, then iterate.",
         ["emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "arr = pyScript.emyArray_p_emyPointArray()\n"
          "nested = [[(0,0),(10,0),(10,10)], [(5,5),(15,5),(15,15),(5,15)]]\n"
          "arr.transList(nested)\n"
          "print(len(arr))  # 2\n"
          "for i in range(len(arr)):\n"
          "    poly = arr[i]\n"
          "    print('poly', i, 'pts:', len(poly))")),
        ("emyArray_emyUInt4",
         "Show bulk-load via __init__ and getNumElements(), then get().",
         ["emyArray_emyUInt4"],
         ("import pyAether as pyScript\n\n"
          "arr = pyScript.emyArray_emyUInt4()\n"
          "for n in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:\n"
          "    arr.append(n)\n"
          "print(arr.getNumElements())  # 10\n"
          "for i in range(arr.getNumElements()):\n"
          "    print(arr.get(i))")),
        ("emyArray_emyScalarName",
         "Show building names from different namespaces and mixing them.",
         ["emyArray_emyScalarName"],
         ("import pyAether as pyScript\n\n"
          "ns1 = pyScript.emyNativeNS()\n"
          "ns2 = pyScript.emyNativeNS()\n"
          "names = []\n"
          "names.append(pyScript.emyScalarName(ns1, 'inst_a'))\n"
          "names.append(pyScript.emyScalarName(ns2, 'inst_b'))\n"
          "names.append(pyScript.emyScalarName(ns1, 'inst_c'))\n"
          "print(len(names))  # 3\n"
          "for nm in names:\n"
          "    out = pyScript.emyString()\n"
          "    nm.get(out)\n"
          "    print(str(out))")),
        ("emyArray_emySegment",
         "Show add, find, remove, then iterate to confirm removal.",
         ["emyArray_emySegment"],
         ("import pyAether as pyScript\n\n"
          "arr = pyScript.emyArray_emySegment()\n"
          "seg1 = pyScript.emySegment(pyScript.emyPoint(0, 0), pyScript.emyPoint(10, 0))\n"
          "seg2 = pyScript.emySegment(pyScript.emyPoint(5, 5), pyScript.emyPoint(15, 5))\n"
          "seg3 = pyScript.emySegment(pyScript.emyPoint(0, 10), pyScript.emyPoint(10, 10))\n"
          "arr.append(seg1)\n"
          "arr.append(seg2)\n"
          "arr.append(seg3)\n"
          "print(len(arr))  # 3\n"
          "arr.remove(seg2)\n"
          "print(len(arr))  # 2\n"
          "print(arr.find(seg2))  # -1\n"
          "for s in arr:\n"
          "    print(s.getDeltaX(), s.getDeltaY())")),
    ]
    for name, scenario, apis, code in s5_variants_2:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S5", "v22-S5-%s" % name, prompt, completion, apis,
             "S5 param_variation for %s" % name)


    # ---- S3: error / edge-case (13 pairs) ----
    s3_cases = [
        ("emyPointArrayIsClockwise",
         "What happens with a degenerate polygon (collinear points) or fewer than 3 points?",
         ["emyPointArrayIsClockwise"],
         ("import pyAether as pyScript\n\n"
          "# fewer than 3 points (degenerate)\n"
          "two_pts = pyScript.emyPointArray()\n"
          "two_pts.append(pyScript.emyPoint(0, 0))\n"
          "two_pts.append(pyScript.emyPoint(10, 0))\n"
          "try:\n"
          "    print(pyScript.emyPointArrayIsClockwise(two_pts))\n"
          "except Exception as e:\n"
          "    print('Error:', e)\n\n"
          "# collinear points (no area)\n"
          "collinear = pyScript.emyPointArray()\n"
          "collinear.append(pyScript.emyPoint(0, 0))\n"
          "collinear.append(pyScript.emyPoint(5, 0))\n"
          "collinear.append(pyScript.emyPoint(10, 0))\n"
          "try:\n"
          "    print(pyScript.emyPointArrayIsClockwise(collinear))\n"
          "except Exception as e:\n"
          "    print('Error:', e)")),
        ("emyPointArrayIsConvex",
         "What happens with a self-intersecting polygon or a single point?",
         ["emyPointArrayIsConvex"],
         ("import pyAether as pyScript\n\n"
          "# single point\n"
          "one = pyScript.emyPointArray()\n"
          "one.append(pyScript.emyPoint(5, 5))\n"
          "try:\n"
          "    print(pyScript.emyPointArrayIsConvex(one))\n"
          "except Exception as e:\n"
          "    print('Error:', e)\n\n"
          "# self-intersecting (bowtie)\n"
          "bowtie = pyScript.emyPointArray()\n"
          "bowtie.append(pyScript.emyPoint(0, 0))\n"
          "bowtie.append(pyScript.emyPoint(10, 10))\n"
          "bowtie.append(pyScript.emyPoint(10, 0))\n"
          "bowtie.append(pyScript.emyPoint(0, 10))\n"
          "try:\n"
          "    print(pyScript.emyPointArrayIsConvex(bowtie))\n"
          "except Exception as e:\n"
          "    print('Error:', e)")),
        ("emyPointArrayScaleSegments",
         "What if source and destination have different point counts?",
         ["emyPointArrayScaleSegments"],
         ("import pyAether as pyScript\n\n"
          "src = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(10,0),(10,10),(0,10)]:\n"
          "    src.append(pyScript.emyPoint(*pt))\n"
          "# dest has only 3 points (mismatch)\n"
          "dst = pyScript.emyPointArray()\n"
          "dst.append(pyScript.emyPoint(0, 0))\n"
          "dst.append(pyScript.emyPoint(20, 0))\n"
          "dst.append(pyScript.emyPoint(20, 20))\n"
          "try:\n"
          "    segs = pyScript.emyPointArrayScaleSegments(src, dst)\n"
          "    print(len(segs))\n"
          "except Exception as e:\n"
          "    print('Error:', e)")),
        ("emyPolygonChopByPolygon",
         "What if chopper touches the polygon boundary exactly (shared edge)?",
         ["emyPolygonChopByPolygon", "emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "poly = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(100,0),(100,100),(0,100)]:\n"
          "    poly.append(pyScript.emyPoint(*pt))\n"
          "# chopper shares left edge with poly\n"
          "chopper = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(50,0),(50,50),(0,50)]:\n"
          "    chopper.append(pyScript.emyPoint(*pt))\n"
          "outside = pyScript.emyArray_p_emyPointArray()\n"
          "inside = pyScript.emyArray_p_emyPointArray()\n"
          "try:\n"
          "    ok = pyScript.emyPolygonChopByPolygon(poly, chopper, outside, inside)\n"
          "    print(ok, len(outside), len(inside))\n"
          "except Exception as e:\n"
          "    print('Error:', e)")),
        ("emyPointArrayGOA",
         "What happens with identical polygons (self AND self) or non-overlapping polygons?",
         ["emyPointArrayGOA", "emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "p1 = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(10,0),(10,10),(0,10)]:\n"
          "    p1.append(pyScript.emyPoint(*pt))\n"
          "# identical -> AND = same polygon\n"
          "res1 = pyScript.emyArray_p_emyPointArray()\n"
          "print(pyScript.emyPointArrayGOA(p1, p1, res1, pyScript.SLE_GOA_AND), len(res1))\n\n"
          "# non-overlapping -> AND = empty\n"
          "p3 = pyScript.emyPointArray()\n"
          "for pt in [(100,100),(110,100),(110,110),(100,110)]:\n"
          "    p3.append(pyScript.emyPoint(*pt))\n"
          "res2 = pyScript.emyArray_p_emyPointArray()\n"
          "print(pyScript.emyPointArrayGOA(p1, p3, res2, pyScript.SLE_GOA_AND), len(res2))")),
    ]
    for name, scenario, apis, code in s3_cases:
        prompt = ("You are an EDA automation engineer. %s Show the edge-case "
                  "behavior with try/except in Python using PyAether "
                  "(import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S3", "v22-S3-%s" % name, prompt, completion, apis,
             "S3 error_edge_case for %s" % name)


    s3_cases_2 = [
        ("emyLibAccess",
         "What happens with an invalid access name string?",
         ["emyLibAccess"],
         ("import pyAether as pyScript\n\n"
          "try:\n"
          "    bad = pyScript.emyLibAccess('invalid_access')\n"
          "    print(str(bad.getName()))\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)\n\n"
          "# empty string\n"
          "try:\n"
          "    empty = pyScript.emyLibAccess('')\n"
          "    print(str(empty.getName()))\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)")),
        ("emyLibAccessExt",
         "What happens with None as lib or None as access?",
         ["emyLibAccessExt"],
         ("import pyAether as pyScript\n\n"
          "acc = pyScript.emyLibAccess('read')\n"
          "try:\n"
          "    ext = pyScript.emyLibAccessExt(None, acc)\n"
          "    print('created with None lib')\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)\n\n"
          "lib = pyScript.emyLib('design_lib')\n"
          "try:\n"
          "    ext2 = pyScript.emyLibAccessExt(lib, None)\n"
          "    print('created with None access')\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)")),
        ("emySegStyle",
         "What happens when getStyle() is called on a segment without a style set?",
         ["emySegStyle"],
         ("import pyAether as pyScript\n\n"
          "seg = pyScript.emyPathSeg()\n"
          "try:\n"
          "    got = seg.getStyle()\n"
          "    print(got)\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)")),
        ("emyTech",
         "What happens with instance methods without an open tech database?",
         ["emyTech"],
         ("import pyAether as pyScript\n\n"
          "# static method works\n"
          "vt = pyScript.emyTech.getDefaultViewType()\n"
          "print('static ok:', vt is not None)\n\n"
          "# instance method without open db -> error\n"
          "try:\n"
          "    tech = pyScript.emyTech()\n"
          "    layers = tech.getLayers()\n"
          "    print('instance layers:', len(layers))\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)")),
        ("emyArray_p_emyPointArray",
         "What happens with empty container and out-of-range indexing?",
         ["emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "arr = pyScript.emyArray_p_emyPointArray()\n"
          "print(len(arr))  # 0\n"
          "try:\n"
          "    poly = arr[0]\n"
          "    print('got:', poly)\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)\n\n"
          "# transList with wrong structure\n"
          "try:\n"
          "    arr2 = pyScript.emyArray_p_emyPointArray()\n"
          "    arr2.transList([1, 2, 3])  # not nested\n"
          "    print(len(arr2))\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)")),
        ("emyArray_emyUInt4",
         "What happens with negative values or out-of-range indexing?",
         ["emyArray_emyUInt4"],
         ("import pyAether as pyScript\n\n"
          "arr = pyScript.emyArray_emyUInt4()\n"
          "# negative value (unsigned type)\n"
          "try:\n"
          "    arr.append(-1)\n"
          "    print(arr[0])\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)\n\n"
          "# out of range\n"
          "arr.append(42)\n"
          "try:\n"
          "    print(arr[100])\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)")),
        ("emyArray_emyScalarName",
         "What happens with None as namespace when creating a ScalarName?",
         ["emyArray_emyScalarName"],
         ("import pyAether as pyScript\n\n"
          "try:\n"
          "    nm = pyScript.emyScalarName(None, 'inst1')\n"
          "    print('created with None ns')\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)\n\n"
          "# empty name string\n"
          "ns = pyScript.emyNativeNS()\n"
          "try:\n"
          "    nm2 = pyScript.emyScalarName(ns, '')\n"
          "    out = pyScript.emyString()\n"
          "    nm2.get(out)\n"
          "    print('empty name:', repr(str(out)))\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)")),
        ("emyArray_emySegment",
         "What happens when appending a non-emySegment object?",
         ["emyArray_emySegment"],
         ("import pyAether as pyScript\n\n"
          "arr = pyScript.emyArray_emySegment()\n"
          "try:\n"
          "    arr.append('not a segment')\n"
          "    print('appended string')\n"
          "except Exception as e:\n"
          "    print('Error:', type(e).__name__, e)\n\n"
          "# find on empty\n"
          "seg = pyScript.emySegment(pyScript.emyPoint(0, 0), pyScript.emyPoint(10, 0))\n"
          "print(arr.find(seg))  # -1")),
    ]
    for name, scenario, apis, code in s3_cases_2:
        prompt = ("You are an EDA automation engineer. %s Show the edge-case "
                  "behavior with try/except in Python using PyAether "
                  "(import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S3", "v22-S3-%s" % name, prompt, completion, apis,
             "S3 error_edge_case for %s" % name)


    # ---- S6: cross-API composition (13 pairs) ----
    s6_chains = [
        ("emy_geometry_pipeline",
         "Build a polygon, check convexity and winding, then chop it and "
         "verify the resulting pieces.",
         ["emyPointArrayIsClockwise", "emyPointArrayIsConvex",
          "emyPolygonChopByPolygon", "emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "# Step 1: build a convex clockwise polygon\n"
          "poly = pyScript.emyPointArray()\n"
          "poly.append(pyScript.emyPoint(0, 0))\n"
          "poly.append(pyScript.emyPoint(0, 100))\n"
          "poly.append(pyScript.emyPoint(100, 100))\n"
          "poly.append(pyScript.emyPoint(100, 0))\n"
          "print('clockwise:', pyScript.emyPointArrayIsClockwise(poly))\n"
          "print('convex:', pyScript.emyPointArrayIsConvex(poly))\n\n"
          "# Step 2: chop with inner rectangle\n"
          "chopper = pyScript.emyPointArray()\n"
          "for pt in [(30,30),(70,30),(70,70),(30,70)]:\n"
          "    chopper.append(pyScript.emyPoint(*pt))\n"
          "outside = pyScript.emyArray_p_emyPointArray()\n"
          "inside = pyScript.emyArray_p_emyPointArray()\n"
          "ok = pyScript.emyPolygonChopByPolygon(poly, chopper, outside, inside)\n"
          "print('chop ok:', ok, 'outside:', len(outside), 'inside:', len(inside))\n\n"
          "# Step 3: verify each outside piece\n"
          "for i in range(len(outside)):\n"
          "    piece = outside[i]\n"
          "    print('piece', i, 'convex:', pyScript.emyPointArrayIsConvex(piece))")),
        ("emy_goa_batch_pipeline",
         "Perform AND, SUB, XOR batch GOA on two polygons and store results "
         "in an emyArray_p_emyPointArray container.",
         ["emyPointArrayGOA", "emyArray_p_emyPointArray",
          "emyPointArrayIsConvex"],
         ("import pyAether as pyScript\n\n"
          "p1 = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(20,0),(20,20),(0,20)]:\n"
          "    p1.append(pyScript.emyPoint(*pt))\n"
          "p2 = pyScript.emyPointArray()\n"
          "for pt in [(10,10),(30,10),(30,30),(10,30)]:\n"
          "    p2.append(pyScript.emyPoint(*pt))\n\n"
          "results = pyScript.emyArray_p_emyPointArray()\n"
          "ops = [('AND', pyScript.SLE_GOA_AND),\n"
          "       ('SUB', pyScript.SLE_GOA_SUB),\n"
          "       ('XOR', pyScript.SLE_GOA_XOR)]\n"
          "for op_name, op in ops:\n"
          "    res = pyScript.emyArray_p_emyPointArray()\n"
          "    ok = pyScript.emyPointArrayGOA(p1, p2, res, op)\n"
          "    print(op_name, 'ok:', ok, 'polys:', len(res))\n"
          "    for i in range(len(res)):\n"
          "        print('  convex:', pyScript.emyPointArrayIsConvex(res[i]))\n"
          "    results.append(res[0])\n"
          "print('total stored:', len(results))")),
        ("emy_scale_and_extract",
         "Scale a polygon and extract changed segments, then verify using "
         "the segment container.",
         ["emyPointArrayScaleSegments", "emyArray_emySegment",
          "emyPointArrayIsConvex"],
         ("import pyAether as pyScript\n\n"
          "src = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(10,0),(10,10),(0,10)]:\n"
          "    src.append(pyScript.emyPoint(*pt))\n"
          "dst = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(20,0),(20,20),(0,20)]:\n"
          "    dst.append(pyScript.emyPoint(*pt))\n\n"
          "segs = pyScript.emyPointArrayScaleSegments(src, dst)\n"
          "print('changed segments:', len(segs))\n\n"
          "seg_arr = pyScript.emyArray_emySegment()\n"
          "for s in segs:\n"
          "    seg_arr.append(s)\n"
          "print('in container:', len(seg_arr))\n"
          "for i in range(len(seg_arr)):\n"
          "    seg = seg_arr[i]\n"
          "    print('  dx:', seg.getDeltaX(), 'dy:', seg.getDeltaY())\n\n"
          "print('dst convex:', pyScript.emyPointArrayIsConvex(dst))")),
        ("emy_lib_access_pipeline",
         "Create a library, set up read and write access, wrap in "
         "emyLibAccessExt, and demonstrate access-level checking.",
         ["emyLibAccess", "emyLibAccessExt"],
         ("import pyAether as pyScript\n\n"
          "lib = pyScript.emyLib('cell_lib')\n\n"
          "# Create all access levels\n"
          "access_levels = []\n"
          "for name in ['read', 'write', 'update', 'delete']:\n"
          "    acc = pyScript.emyLibAccess(name)\n"
          "    access_levels.append(acc)\n"
          "    print(name, 'enum:', acc.emyLibAccessEnum())\n\n"
          "# Wrap read access\n"
          "read_ext = pyScript.emyLibAccessExt(lib, access_levels[0])\n"
          "print('read ext access:', str(read_ext.getAccess().getName()))\n"
          "print('read ext lib:', read_ext.getLib() is not None)\n\n"
          "# Wrap write access\n"
          "write_ext = pyScript.emyLibAccessExt(lib, access_levels[1])\n"
          "print('write ext access:', str(write_ext.getAccess().getName()))")),
    ]
    for name, scenario, apis, code in s6_chains:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v22-S6-%s" % name, prompt, completion, apis,
             "S6 cross_api_composition: %s" % name)


    s6_chains_2 = [
        ("emy_tech_and_containers",
         "Query tech view types, store layer numbers in emyArray_emyUInt4 "
         "and names in emyArray_emyScalarName.",
         ["emyTech", "emyArray_emyUInt4", "emyArray_emyScalarName"],
         ("import pyAether as pyScript\n\n"
          "vt = pyScript.emyTech.getDefaultViewType()\n"
          "vts = pyScript.emyTech.getViewTypes()\n"
          "print('view types:', len(vts))\n\n"
          "layer_nums = pyScript.emyArray_emyUInt4()\n"
          "for n in [1, 2, 3, 4, 5]:\n"
          "    layer_nums.append(n)\n"
          "print('layers:', len(layer_nums))\n\n"
          "ns = pyScript.emyNativeNS()\n"
          "layer_names = []\n"
          "for nm in ['metal1', 'metal2', 'metal3', 'via1', 'via2']:\n"
          "    layer_names.append(pyScript.emyScalarName(ns, nm))\n"
          "print('names:', len(layer_names))\n"
          "for nm in layer_names:\n"
          "    out = pyScript.emyString()\n"
          "    nm.get(out)\n"
          "    print('  ', str(out))")),
        ("emy_pointarray_full_check",
         "Build a polygon, run clockwise + convex checks, then GOA with itself.",
         ["emyPointArrayIsClockwise", "emyPointArrayIsConvex",
          "emyPointArrayGOA", "emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "poly = pyScript.emyPointArray()\n"
          "poly.append(pyScript.emyPoint(0, 0))\n"
          "poly.append(pyScript.emyPoint(0, 50))\n"
          "poly.append(pyScript.emyPoint(50, 50))\n"
          "poly.append(pyScript.emyPoint(50, 0))\n"
          "print('clockwise:', pyScript.emyPointArrayIsClockwise(poly))\n"
          "print('convex:', pyScript.emyPointArrayIsConvex(poly))\n\n"
          "res = pyScript.emyArray_p_emyPointArray()\n"
          "ok = pyScript.emyPointArrayGOA(poly, poly, res, pyScript.SLE_GOA_OR)\n"
          "print('GOA OR self:', ok, len(res))\n"
          "if ok and len(res) > 0:\n"
          "    print('result convex:', pyScript.emyPointArrayIsConvex(res[0]))")),
        ("emy_chop_and_scale",
         "Chop a polygon, scale the outside piece, extract changed segments.",
         ["emyPolygonChopByPolygon", "emyArray_p_emyPointArray",
          "emyPointArrayScaleSegments", "emyArray_emySegment"],
         ("import pyAether as pyScript\n\n"
          "poly = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(100,0),(100,100),(0,100)]:\n"
          "    poly.append(pyScript.emyPoint(*pt))\n"
          "chopper = pyScript.emyPointArray()\n"
          "for pt in [(40,40),(60,40),(60,60),(40,60)]:\n"
          "    chopper.append(pyScript.emyPoint(*pt))\n"
          "outside = pyScript.emyArray_p_emyPointArray()\n"
          "inside = pyScript.emyArray_p_emyPointArray()\n"
          "ok = pyScript.emyPolygonChopByPolygon(poly, chopper, outside, inside)\n"
          "print('chop:', ok, 'outside:', len(outside), 'inside:', len(inside))\n"
          "if ok and len(outside) > 0:\n"
          "    piece = outside[0]\n"
          "    scaled = pyScript.emyPointArray()\n"
          "    for i in range(len(piece)):\n"
          "        p = piece[i]\n"
          "        scaled.append(pyScript.emyPoint(p.x * 2, p.y * 2))\n"
          "    segs = pyScript.emyPointArrayScaleSegments(piece, scaled)\n"
          "    print('changed segments after scale:', len(segs))")),
        ("emy_segment_and_style",
         "Create segments, store in emyArray_emySegment, apply emySegStyle.",
         ["emyArray_emySegment", "emySegStyle"],
         ("import pyAether as pyScript\n\n"
          "style = pyScript.emySegStyle()\n"
          "seg_arr = pyScript.emyArray_emySegment()\n"
          "path_segs = []\n"
          "for (x1, y1, x2, y2) in [(0,0,10,0), (10,0,10,10), (10,10,0,10)]:\n"
          "    seg = pyScript.emySegment(\n"
          "        pyScript.emyPoint(x1, y1), pyScript.emyPoint(x2, y2))\n"
          "    seg_arr.append(seg)\n"
          "    ps = pyScript.emyPathSeg()\n"
          "    ps.setStyle(style)\n"
          "    path_segs.append(ps)\n"
          "print('segments in container:', len(seg_arr))\n"
          "print('path segments styled:', len(path_segs))\n"
          "for i in range(len(seg_arr)):\n"
          "    s = seg_arr[i]\n"
          "    print('  seg', i, 'dx:', s.getDeltaX(), 'dy:', s.getDeltaY())")),
        ("emy_name_and_layer_arrays",
         "Build emyArray_emyUInt4 for layers and emyArray_emyScalarName for "
         "net names, then cross-reference.",
         ["emyArray_emyUInt4", "emyArray_emyScalarName"],
         ("import pyAether as pyScript\n\n"
          "ns = pyScript.emyNativeNS()\n"
          "layer_nums = pyScript.emyArray_emyUInt4()\n"
          "net_names = []\n"
          "layers = ['M1', 'M2', 'M3', 'V1', 'V2']\n"
          "nums = [1, 2, 3, 11, 12]\n"
          "for i in range(len(layers)):\n"
          "    layer_nums.append(nums[i])\n"
          "    net_names.append(pyScript.emyScalarName(ns, layers[i]))\n"
          "print('layers:', len(layer_nums), 'names:', len(net_names))\n"
          "for i in range(len(layer_nums)):\n"
          "    out = pyScript.emyString()\n"
          "    net_names[i].get(out)\n"
          "    print('  layer', layer_nums[i], '=', str(out))")),
    ]
    for name, scenario, apis, code in s6_chains_2:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v22-S6-%s" % name, prompt, completion, apis,
             "S6 cross_api_composition: %s" % name)


    s6_chains_3 = [
        ("emy_clockwise_chop_verify",
         "Build two overlapping clockwise polygons, chop one by the other, "
         "verify winding of all result pieces.",
         ["emyPointArrayIsClockwise", "emyPolygonChopByPolygon",
          "emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "poly1 = pyScript.emyPointArray()\n"
          "poly1.append(pyScript.emyPoint(0, 0))\n"
          "poly1.append(pyScript.emyPoint(0, 80))\n"
          "poly1.append(pyScript.emyPoint(80, 80))\n"
          "poly1.append(pyScript.emyPoint(80, 0))\n"
          "print('poly1 clockwise:', pyScript.emyPointArrayIsClockwise(poly1))\n"
          "poly2 = pyScript.emyPointArray()\n"
          "poly2.append(pyScript.emyPoint(50, 50))\n"
          "poly2.append(pyScript.emyPoint(50, 120))\n"
          "poly2.append(pyScript.emyPoint(120, 120))\n"
          "poly2.append(pyScript.emyPoint(120, 50))\n"
          "print('poly2 clockwise:', pyScript.emyPointArrayIsClockwise(poly2))\n"
          "outside = pyScript.emyArray_p_emyPointArray()\n"
          "inside = pyScript.emyArray_p_emyPointArray()\n"
          "ok = pyScript.emyPolygonChopByPolygon(poly1, poly2, outside, inside)\n"
          "print('chop:', ok, 'outside:', len(outside), 'inside:', len(inside))\n"
          "for i in range(len(outside)):\n"
          "    print('  outside', i, 'cw:',\n"
          "          pyScript.emyPointArrayIsClockwise(outside[i]))")),
        ("emy_goa_and_scale",
         "GOA AND two polygons, scale result 3x, extract changed segments.",
         ["emyPointArrayGOA", "emyArray_p_emyPointArray",
          "emyPointArrayScaleSegments"],
         ("import pyAether as pyScript\n\n"
          "p1 = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(20,0),(20,20),(0,20)]:\n"
          "    p1.append(pyScript.emyPoint(*pt))\n"
          "p2 = pyScript.emyPointArray()\n"
          "for pt in [(10,10),(30,10),(30,30),(10,30)]:\n"
          "    p2.append(pyScript.emyPoint(*pt))\n"
          "res = pyScript.emyArray_p_emyPointArray()\n"
          "ok = pyScript.emyPointArrayGOA(p1, p2, res, pyScript.SLE_GOA_AND)\n"
          "print('AND:', ok, len(res))\n"
          "if ok and len(res) > 0:\n"
          "    inter = res[0]\n"
          "    scaled = pyScript.emyPointArray()\n"
          "    for i in range(len(inter)):\n"
          "        p = inter[i]\n"
          "        scaled.append(pyScript.emyPoint(p.x * 3, p.y * 3))\n"
          "    segs = pyScript.emyPointArrayScaleSegments(inter, scaled)\n"
          "    print('changed segs after 3x:', len(segs))")),
        ("emy_convex_goa_pipeline",
         "Build two convex polygons, run GOA AND/OR, check convexity of results.",
         ["emyPointArrayIsConvex", "emyPointArrayGOA",
          "emyArray_p_emyPointArray"],
         ("import pyAether as pyScript\n\n"
          "p1 = pyScript.emyPointArray()\n"
          "for pt in [(0,0),(20,0),(20,20),(0,20)]:\n"
          "    p1.append(pyScript.emyPoint(*pt))\n"
          "p2 = pyScript.emyPointArray()\n"
          "for pt in [(10,0),(30,0),(30,20),(10,20)]:\n"
          "    p2.append(pyScript.emyPoint(*pt))\n"
          "print('p1 convex:', pyScript.emyPointArrayIsConvex(p1))\n"
          "print('p2 convex:', pyScript.emyPointArrayIsConvex(p2))\n"
          "for op_name, op in [('AND', pyScript.SLE_GOA_AND),\n"
          "                     ('OR', pyScript.SLE_GOA_OR)]:\n"
          "    res = pyScript.emyArray_p_emyPointArray()\n"
          "    ok = pyScript.emyPointArrayGOA(p1, p2, res, op)\n"
          "    print(op_name, ok, len(res))\n"
          "    if ok and len(res) > 0:\n"
          "        print('  convex:', pyScript.emyPointArrayIsConvex(res[0]))")),
        ("emy_lib_and_tech",
         "Create a library with read access, query tech view types for "
         "compatibility.",
         ["emyLibAccessExt", "emyLibAccess", "emyTech"],
         ("import pyAether as pyScript\n\n"
          "vt = pyScript.emyTech.getDefaultViewType()\n"
          "vts = pyScript.emyTech.getViewTypes()\n"
          "print('default view type:', vt is not None)\n"
          "print('view type count:', len(vts))\n\n"
          "lib = pyScript.emyLib('tech_lib')\n"
          "acc = pyScript.emyLibAccess('read')\n"
          "ext = pyScript.emyLibAccessExt(lib, acc)\n"
          "print('lib access:', str(ext.getAccess().getName()))\n"
          "print('lib ok:', ext.getLib() is not None)")),
    ]
    for name, scenario, apis, code in s6_chains_3:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v22-S6-%s" % name, prompt, completion, apis,
             "S6 cross_api_composition: %s" % name)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    parser = argparse.ArgumentParser(
        description="R192: emy* geometry/library/tech SFT corpus generator (v22)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print stats only, do not write output file")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of pairs (for testing)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Output JSONL path (default: %s)" % DEFAULT_OUTPUT)
    args = parser.parse_args()

    print("=" * 72)
    print("R192: emy* geometry/library/tech corpus generator (v22)")
    print("=" * 72)
    print()

    # ---- GATE 1: eval entry points loaded ----
    eval_eps = load_eval_entry_points()
    print("[GATE] eval entry points loaded: %d" % len(eval_eps))
    if len(eval_eps) == 0:
        print("[GATE] WARNING: no eval entry points found - "
              "contamination scan disabled")
    else:
        print("[GATE] sample entry points: %s" %
              ", ".join(sorted(eval_eps)[:5]))
    print()

    # ---- Build pairs ----
    pairs, rejected, reject_details = build_pairs(eval_eps, limit=args.limit)
    print("[BUILD] total pairs generated: %d" % len(pairs))
    print("[BUILD] pairs rejected (contamination): %d" % rejected)
    if reject_details:
        print("[BUILD] rejection details:")
        for pid, hit in reject_details:
            print("  %s -> matched eval entry_point: %s" % (pid, hit))
    print()

    # ---- GATE 2: pollution isolation check ----
    all_api_used = set()
    for p in pairs:
        for a in p["api_used"]:
            all_api_used.add(a)
    print("[GATE] unique APIs covered: %d / %d" %
          (len(all_api_used), len(API_ORDER)))
    missing = set(API_ORDER) - all_api_used
    if missing:
        print("[GATE] WARNING: APIs not covered: %s" % ", ".join(sorted(missing)))
    print()

    # ---- Stats by type ----
    type_counts = {}
    for p in pairs:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1
    print("[STATS] pairs by type:")
    for pt in sorted(type_counts):
        print("  %s: %d" % (pt, type_counts[pt]))
    print()

    # ---- GATE 3: all contamination checks PASS ----
    fail_count = sum(1 for p in pairs
                     if p["contamination_check"] != "PASS")
    print("[GATE] contamination check failures: %d" % fail_count)
    if fail_count > 0:
        print("[GATE] FATAL: contamination check failed - aborting write")
        sys.exit(1)
    print()

    # ---- Write output ----
    if args.dry_run:
        print("[DRY-RUN] skipping output file write")
    else:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w") as fh:
            for p in pairs:
                fh.write(json.dumps(p, ensure_ascii=False) + "\n")
        print("[WRITE] %d pairs -> %s" % (len(pairs), args.output))
        fsize = os.path.getsize(args.output)
        print("[WRITE] file size: %d bytes (%.1f KB)" % (fsize, fsize / 1024.0))
    print()
    print("=" * 72)
    print("R192 DONE. pairs=%d rejected=%d apis_covered=%d/%d" %
          (len(pairs), rejected, len(all_api_used), len(API_ORDER)))
    print("=" * 72)


if __name__ == "__main__":
    main()

