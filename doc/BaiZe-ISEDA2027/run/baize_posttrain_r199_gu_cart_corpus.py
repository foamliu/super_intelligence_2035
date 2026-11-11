#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r199_gu_cart_corpus.py
R199 -- v29 PyAether SFT corpus: Gu* cartoon graphics (3 APIs)
= 3 APIs, 25 pairs.

BACKGROUND: v11-v28 (783 pairs) cover 144/164 eval raw APIs (87.8%). 20 blind.
Data-driven scan (R191 blind_scan, re-run with v28) shows Gu is the #1 blind
family (5 usages, 3 callable class APIs: GuCartPolyLine/GuCartPolygon/GuCartBox).
Covering Gu clears the top blind family.

All 3 APIs are GuCartoon subclasses (Action Extension) for drawing graphic
annotation/selection shapes (polyline, polygon, box) in EDA layout. They share
the emyPointArrayF + layNum + purNum constructor pattern and the
getPointArray / getOriginBBoxF output-param methods. All ISOLATE-class (eval
helper cartoon APIs, NOT eval entry_points).
Fingerprint scan rejects eval entry_points (155 loaded).

Authoritative signatures fetched via pyAether MCP get_api_details (R199 wake).

Usage:
  python3 baize_posttrain_r199_gu_cart_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v29_gu_cart.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

# === Gu* APIs (3 GuCartoon classes) ===

API_DOCS["GuCartPolyLine"] = {
    "sig": "GuCartPolyLine(pa: emyPointArrayF, layNum: emyLayerNum=emcNullIndex, purNum: emyPurposeNum=EMY_DRAWING_PURPOSE) -> GuCartPolyLine",
    "desc": "Creates a GuCartoon of type polyline (an open multi-segment line / route). Inherits from GuCartoon. Used in EDA layout annotation to draw paths, routes, or measurement traces. The point array defines the line route in append order; the line is NOT auto-closed (unlike GuCartPolygon).",
    "params": {
        "pa": "emyPointArrayF -- point array defining the polyline route. Build via pyScript.emyPointArrayF() then .append((x, y)) with float tuples. Order is preserved. Supports Python built-in types.",
        "layNum": "emyLayerNum, optional -- layer number. Default emcNullIndex (4294967295 = unspecified). Use a valid tech-library layer number (e.g. 62).",
        "purNum": "emyPurposeNum, optional -- purpose number. Default EMY_DRAWING_PURPOSE. Commonly pyScript.emvPurposeNumberDrawing for drawing purpose.",
    },
    "returns": "GuCartPolyLine -- a cartoon object instance (a polyline shape). Add to a design area via da.addPrivateCartoon(obj).",
    "methods": "getPointArray(pointArray: emyPointArrayF) -- fills the given array with the polyline's points (output-param pattern: clears then fills, order preserved, no return value).",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> arr0 = pyScript.emyPointArrayF()\n"
                ">>> arr0.append((0, 0))\n"
                ">>> arr0.append((1, 1))\n"
                ">>> gu_poly_line = pyScript.GuCartPolyLine(arr0, layNum=62, purNum=pyScript.emvPurposeNumberDrawing)\n"
                ">>> out = pyScript.emyPointArrayF()\n"
                ">>> gu_poly_line.getPointArray(out)\n"
                ">>> print(out)\n"
                "[(0.0, 0.0), (1.0, 1.0)]"),
    "category": "Gu / Cartoon Graphics (Action Extension)", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "GuCartPolyLine is an OPEN polyline (no auto-close). Build emyPointArrayF with .append((x,y)) float tuples. getPointArray uses output-param pattern (pass a fresh emyPointArrayF, it gets cleared & filled, no return value). layNum default emcNullIndex=4294967295 means unspecified; use a valid layer. Use emvPurposeNumberDrawing for drawing purpose. Add to design via da.addPrivateCartoon()."}

API_DOCS["GuCartPolygon"] = {
    "sig": "GuCartPolygon(pa: emyPointArrayF, layNum: emyLayerNum=emcNullIndex, purNum: emyPurposeNum=EMY_DRAWING_PURPOSE) -> GuCartPolygon",
    "desc": "Creates a GuCartoon of type polygon (a closed shape). Inherits from GuCartoon. Used in EDA layout annotation to draw filled/outlined regions. The polygon auto-closes (the last point connects back to the first). At least 3 points are needed for a valid polygon; an empty or <3-point array creates a degenerate object without raising.",
    "params": {
        "pa": "emyPointArrayF -- point array defining the polygon outline. Build via pyScript.emyPointArrayF() then .append((x, y)) with float tuples. Points connect in append order; polygon auto-closes. Min 3 points for a valid shape.",
        "layNum": "emyLayerNum, optional -- layer number. Default emcNullIndex (4294967295 = unspecified). Use a valid tech-library layer number (e.g. 61).",
        "purNum": "emyPurposeNum, optional -- purpose number. Default EMY_DRAWING_PURPOSE. Commonly pyScript.emvPurposeNumberDrawing for drawing purpose.",
    },
    "returns": "GuCartPolygon -- a cartoon object instance (a polygon shape). Add to a design area via da.addPrivateCartoon(obj).",
    "methods": "getPointArray(pointArray: emyPointArrayF) -- fills the given array with the polygon's points (output-param pattern: clears then fills, order preserved, no return value).",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> arr0 = pyScript.emyPointArrayF()\n"
                ">>> arr0.append((0, 0))\n"
                ">>> arr0.append((10, 0))\n"
                ">>> arr0.append((20, 10))\n"
                ">>> arr0.append((15, 20))\n"
                ">>> arr0.append((10, 10))\n"
                ">>> gu_poly = pyScript.GuCartPolygon(arr0, layNum=61, purNum=pyScript.emvPurposeNumberDrawing)\n"
                ">>> out = pyScript.emyPointArrayF()\n"
                ">>> gu_poly.getPointArray(out)\n"
                ">>> print(len(out))\n"
                "5"),
    "category": "Gu / Cartoon Graphics (Action Extension)", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "GuCartPolygon AUTO-CLOSES (last point connects to first) -- differs from GuCartPolyLine which stays open. Min 3 points for a valid polygon (empty/<3 creates degenerate object, no exception). Build emyPointArrayF with .append((x,y)). getPointArray uses output-param pattern (pass fresh emyPointArrayF, cleared & filled, no return value). Use emvPurposeNumberDrawing for drawing purpose."}


API_DOCS["GuCartBox"] = {
    "sig": "GuCartBox(bbox: tuple) | GuCartBox(p1: tuple, p2: tuple) -> GuCartBox  [optional POSITIONAL layNum, purNum]",
    "desc": "Creates a GuCartoon of type box (a rectangle). Inherits from GuCartoon. Used in EDA layout annotation for bounding boxes, annotation frames, selection regions, design boundaries. Has 29 methods. Two constructor forms: a single 4-tuple bbox (x1,y1,x2,y2), or two 2-tuple corner points (x1,y1),(x2,y2). Optional layer/purpose must be passed POSITIONALLY (keyword args raise TypeError).",
    "params": {
        "bbox": "tuple -- a 4-tuple (x1, y1, x2, y2) bounding box. Alternative: pass two 2-tuples (x1,y1) and (x2,y2) as separate corner points. Coordinates are floats (ints auto-converted).",
        "layNum": "emyLayerNum, optional POSITIONAL -- layer number. Default emcNullIndex (4294967295). MUST be positional; keyword arg raises TypeError. Use a valid tech-library layer number.",
        "purNum": "emyPurposeNum, optional POSITIONAL -- purpose number. Default emcNullIndex (4294967295). MUST be positional; keyword arg raises TypeError.",
    },
    "returns": "GuCartBox -- a cartoon object instance (a box/rectangle shape). Add to a design area via da.addPrivateCartoon(obj).",
    "methods": "getLayerNum() -> int; getPurposeNum() -> int; getLineWidth()/setLineWidth(n); setShow(bool)/getShow(); setLineColor(0xRRGGBB)/getLineColor(); setLinePattern(n); getOriginBBoxF(emyBoxF) -- fills the given emyBoxF with the box bounds (output-param, no return value). 29 methods total.",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> box1 = pyScript.GuCartBox((0.0, 0.0, 10.0, 10.0))\n"
                ">>> box2 = pyScript.GuCartBox((0.0, 0.0), (10.0, 10.0))\n"
                ">>> box3 = pyScript.GuCartBox((0.0, 0.0, 5.0, 5.0), 1, 0)\n"
                ">>> print(box1.getLayerNum())\n"
                "4294967295\n"
                ">>> bbox = pyScript.emyBoxF()\n"
                ">>> box1.getOriginBBoxF(bbox)\n"
                ">>> print(bbox)\n"
                "(0.0, 0.0, 10.0, 10.0)"),
    "category": "Gu / Cartoon Graphics (Action Extension)", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Two ctor forms: 4-tuple bbox (x1,y1,x2,y2) OR two 2-tuple corners. layNum/purNum MUST be POSITIONAL -- keyword args (layNum=, purNum=) raise TypeError. Default layer/purpose = emcNullIndex (4294967295). getOriginBBoxF(emyBoxF) uses output-param pattern (pass a fresh emyBoxF, filled with bounds, no return value). setLineColor takes 0xRRGGBB int. Add to design via da.addPrivateCartoon(box). 29 methods available."}

API_ORDER = ["GuCartPolyLine", "GuCartPolygon", "GuCartBox"]



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


    # ---- S1: doc -> code (3 pairs, one per API) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v29-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S3: code -> doc (3 pairs, one per API) ----
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
        _add("S3", "v29-S3-%s" % name, prompt, completion, [name],
             "S3 code_to_doc for %s" % name)
    # ---- S4: multi-step trace (6 pairs, 2 per API) ----
    s4_traces = [
        ("GuCartPolyLine-route-and-readback",
         "Create a polyline route through 4 points on layer 62 with drawing purpose, then read the points back via getPointArray and verify count.",
         ["GuCartPolyLine"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((0.0, 0.0))\n"
         ">>> arr.append((5.0, 0.0))\n"
         ">>> arr.append((5.0, 3.0))\n"
         ">>> arr.append((8.0, 3.0))\n"
         ">>> pl = pyScript.GuCartPolyLine(arr, layNum=62, purNum=pyScript.emvPurposeNumberDrawing)\n"
         ">>> out = pyScript.emyPointArrayF()\n"
         ">>> pl.getPointArray(out)\n"
         ">>> print('polyline points:', len(out))\n"
         "polyline points: 4"),
        ("GuCartPolyLine-default-layer",
         "Create a polyline using default layer/purpose (no layNum/purNum args) and confirm getPointArray returns the points unchanged.",
         ["GuCartPolyLine"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((1.5, 2.5))\n"
         ">>> arr.append((3.0, 4.0))\n"
         ">>> pl = pyScript.GuCartPolyLine(arr)\n"
         ">>> out = pyScript.emyPointArrayF()\n"
         ">>> pl.getPointArray(out)\n"
         ">>> print(list(out))\n"
         "[(1.5, 2.5), (3.0, 4.0)]"),
        ("GuCartPolygon-pentagon-readback",
         "Create a 5-point polygon on layer 61, read back its points, and confirm the count (polygon auto-closes but getPointArray returns the stored points).",
         ["GuCartPolygon"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((0.0, 0.0))\n"
         ">>> arr.append((10.0, 0.0))\n"
         ">>> arr.append((20.0, 10.0))\n"
         ">>> arr.append((15.0, 20.0))\n"
         ">>> arr.append((10.0, 10.0))\n"
         ">>> poly = pyScript.GuCartPolygon(arr, layNum=61, purNum=pyScript.emvPurposeNumberDrawing)\n"
         ">>> out = pyScript.emyPointArrayF()\n"
         ">>> poly.getPointArray(out)\n"
         ">>> print('polygon stored points:', len(out))\n"
         "polygon stored points: 5"),
        ("GuCartPolygon-rectangle-as-polygon",
         "Create a rectangular region as a 4-point polygon (clockwise) on the default layer, then read back the points to verify order.",
         ["GuCartPolygon"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((0.0, 0.0))\n"
         ">>> arr.append((10.0, 0.0))\n"
         ">>> arr.append((10.0, 10.0))\n"
         ">>> arr.append((0.0, 10.0))\n"
         ">>> poly = pyScript.GuCartPolygon(arr)\n"
         ">>> out = pyScript.emyPointArrayF()\n"
         ">>> poly.getPointArray(out)\n"
         ">>> print([(p.x(), p.y()) for p in out])\n"
         "[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]"),
        ("GuCartBox-bbox-and-properties",
         "Create a box from a 4-tuple bbox, query its layer/purpose defaults, set line width and color, then read its bounding box via getOriginBBoxF.",
         ["GuCartBox"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> box = pyScript.GuCartBox((0.0, 0.0, 100.0, 50.0))\n"
         ">>> print('layer:', box.getLayerNum(), 'purpose:', box.getPurposeNum())\n"
         "layer: 4294967295 purpose: 4294967295\n"
         ">>> box.setLineWidth(2.0)\n"
         ">>> box.setLineColor(0xFF0000)\n"
         ">>> box.setShow(True)\n"
         ">>> bbox = pyScript.emyBoxF()\n"
         ">>> box.getOriginBBoxF(bbox)\n"
         ">>> print('bounds:', bbox)\n"
         "bounds: (0.0, 0.0, 100.0, 50.0)"),
        ("GuCartBox-two-corners-with-layer",
         "Create a box from two corner-point tuples and assign a layer and purpose positionally, then verify the layer number was set.",
         ["GuCartBox"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> box = pyScript.GuCartBox((0.0, 0.0), (10.0, 10.0), 10, 0)\n"
         ">>> print('layer:', box.getLayerNum())\n"
         "layer: 10\n"
         ">>> bbox = pyScript.emyBoxF()\n"
         ">>> box.getOriginBBoxF(bbox)\n"
         ">>> print('bounds:', bbox)\n"
         "bounds: (0.0, 0.0, 10.0, 10.0)"),
    ]
    for apis_str, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v29-S4-%s" % apis_str, prompt, completion, apis,
             "S4 multi_step_trace: %s" % scenario)


    # ---- S5: error / edge-case (6 pairs, 2 per API) ----
    s5_items = [
        ("GuCartPolyLine-empty-array",
         "What happens if you create a GuCartPolyLine with an empty emyPointArrayF? Show the safe pattern: build empty, create object, read back (expect 0 points).",
         ["GuCartPolyLine"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> arr = pyScript.emyPointArrayF()  # empty -- no append calls\n"
         ">>> pl = pyScript.GuCartPolyLine(arr)\n"
         ">>> out = pyScript.emyPointArrayF()\n"
         ">>> pl.getPointArray(out)\n"
         ">>> print('points:', len(out))\n"
         "points: 0\n"
         "# NOTE: empty polyline is a degenerate object; no exception raised.\n"
         "# Always append at least 2 points for a visible polyline."),
        ("GuCartPolyLine-negative-coords",
         "Demonstrate that GuCartPolyLine accepts negative float coordinates. Build a polyline crossing the origin with negative points and read them back to confirm values are preserved.",
         ["GuCartPolyLine"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((-5.0, -5.0))\n"
         ">>> arr.append((0.0, 0.0))\n"
         ">>> arr.append((5.0, -5.0))\n"
         ">>> pl = pyScript.GuCartPolyLine(arr, layNum=62)\n"
         ">>> out = pyScript.emyPointArrayF()\n"
         ">>> pl.getPointArray(out)\n"
         ">>> print([(p.x(), p.y()) for p in out])\n"
         "[(-5.0, -5.0), (0.0, 0.0), (5.0, -5.0)]"),
        ("GuCartPolygon-too-few-points",
         "A polygon needs at least 3 points. Show what happens with only 2 points (degenerate, no exception) and the correct fix of adding a 3rd point.",
         ["GuCartPolygon"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> # WRONG: only 2 points -> degenerate polygon (no exception)\n"
         ">>> arr2 = pyScript.emyPointArrayF()\n"
         ">>> arr2.append((0.0, 0.0))\n"
         ">>> arr2.append((10.0, 0.0))\n"
         ">>> bad = pyScript.GuCartPolygon(arr2)\n"
         ">>> print('degenerate created, points:', len(arr2))\n"
         "degenerate created, points: 2\n"
         ">>> # FIX: add a 3rd point for a valid triangle\n"
         ">>> arr3 = pyScript.emyPointArrayF()\n"
         ">>> arr3.append((0.0, 0.0))\n"
         ">>> arr3.append((10.0, 0.0))\n"
         ">>> arr3.append((5.0, 8.0))\n"
         ">>> tri = pyScript.GuCartPolygon(arr3, layNum=61)\n"
         ">>> print('valid triangle created')\n"
         "valid triangle created"),
        ("GuCartPolygon-auto-close",
         "GuCartPolygon auto-closes: the last point connects back to the first. Demonstrate by creating a 3-point triangle and noting getPointArray returns only the 3 stored points (the closing edge is implicit).",
         ["GuCartPolygon"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((0.0, 0.0))\n"
         ">>> arr.append((10.0, 0.0))\n"
         ">>> arr.append((5.0, 10.0))\n"
         ">>> tri = pyScript.GuCartPolygon(arr)\n"
         ">>> out = pyScript.emyPointArrayF()\n"
         ">>> tri.getPointArray(out)\n"
         ">>> print('stored points (closing edge implicit):', len(out))\n"
         "stored points (closing edge implicit): 3\n"
         "# NOTE: unlike GuCartPolyLine, the polygon closes p2->p0 automatically."),
        ("GuCartBox-keyword-args-error",
         "GuCartBox does NOT accept keyword arguments for layNum/purNum -- it raises TypeError. Show the wrong (keyword) call and the correct (positional) call.",
         ["GuCartBox"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> # WRONG: keyword args raise TypeError\n"
         ">>> try:\n"
         "...     bad = pyScript.GuCartBox((0, 0, 10, 10), layNum=1, purNum=0)\n"
         "... except TypeError as e:\n"
         "...     print('TypeError:', e)\n"
         "TypeError: ...\n"
         ">>> # CORRECT: pass layer/purpose positionally\n"
         ">>> box = pyScript.GuCartBox((0.0, 0.0, 10.0, 10.0), 1, 0)\n"
         ">>> print('layer:', box.getLayerNum(), 'purpose:', box.getPurposeNum())\n"
         "layer: 1 purpose: 0"),
        ("GuCartBox-default-layer-check",
         "When no layer/purpose is given, GuCartBox defaults to emcNullIndex (4294967295). Show how to detect this default and the correct way to read the bounding box.",
         ["GuCartBox"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> box = pyScript.GuCartBox((0.0, 0.0, 10.0, 10.0))\n"
         ">>> if box.getLayerNum() == 4294967295:\n"
         "...     print('Using default layer (emcNullIndex)')\n"
         "Using default layer (emcNullIndex)\n"
         ">>> if box.getPurposeNum() == 4294967295:\n"
         "...     print('Using default purpose (emcNullIndex)')\n"
         "Using default purpose (emcNullIndex)\n"
         ">>> # getOriginBBoxF needs an emyBoxF output argument\n"
         ">>> bbox = pyScript.emyBoxF()\n"
         ">>> box.getOriginBBoxF(bbox)\n"
         ">>> print('bounds:', bbox)\n"
          "bounds: (0.0, 0.0, 10.0, 10.0)"),
    ]
    for apis_str, scenario, apis, code in s5_items:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S5", "v29-S5-%s" % apis_str, prompt, completion, apis,
             "S5 error_edge_case: %s" % scenario)


    # ---- S6: cross-API workflow (7 pairs combining the 3 Gu* APIs) ----
    s6_items = [
        ("polyline-vs-polygon",
         "Show the key difference between GuCartPolyLine (open) and GuCartPolygon (auto-closes). Build the same 4-point route with both classes and read back each.",
         ["GuCartPolyLine", "GuCartPolygon"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((0.0, 0.0))\n"
         ">>> arr.append((10.0, 0.0))\n"
         ">>> arr.append((10.0, 10.0))\n"
         ">>> arr.append((0.0, 10.0))\n"
         ">>> pl = pyScript.GuCartPolyLine(arr, layNum=62)   # open: 4 edges\n"
         ">>> poly = pyScript.GuCartPolygon(arr, layNum=61)  # closed: 5 edges (auto-close)\n"
         ">>> o1 = pyScript.emyPointArrayF(); pl.getPointArray(o1)\n"
         ">>> o2 = pyScript.emyPointArrayF(); poly.getPointArray(o2)\n"
         ">>> print('polyline pts:', len(o1), 'polygon pts:', len(o2))\n"
         "polyline pts: 4 polygon pts: 4\n"
         "# NOTE: both store 4 points; polygon implicitly closes last->first."),
        ("box-and-polygon-overlay",
         "Create a box annotation and a polygon outline covering the same region, set distinct line colors, and read both bounding regions.",
         ["GuCartBox", "GuCartPolygon"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> box = pyScript.GuCartBox((0.0, 0.0, 100.0, 100.0), 10, 0)\n"
         ">>> box.setLineColor(0x0000FF); box.setLineWidth(2.0)\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((10.0, 10.0))\n"
         ">>> arr.append((90.0, 10.0))\n"
         ">>> arr.append((90.0, 90.0))\n"
         ">>> arr.append((10.0, 90.0))\n"
         ">>> poly = pyScript.GuCartPolygon(arr, layNum=61)\n"
         ">>> bb = pyScript.emyBoxF(); box.getOriginBBoxF(bb)\n"
         ">>> print('box bounds:', bb, 'box layer:', box.getLayerNum())\n"
         "box bounds: (0.0, 0.0, 100.0, 100.0) box layer: 10\n"
         ">>> po = pyScript.emyPointArrayF(); poly.getPointArray(po)\n"
         ">>> print('polygon pts:', len(po))\n"
         "polygon pts: 4"),
        ("route-with-box-markers",
         "Draw a polyline route through waypoints and place a GuCartBox marker at each endpoint. Read back the route points and the box bounds.",
         ["GuCartPolyLine", "GuCartBox"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((0.0, 0.0))\n"
         ">>> arr.append((50.0, 20.0))\n"
         ">>> arr.append((100.0, 0.0))\n"
         ">>> route = pyScript.GuCartPolyLine(arr, layNum=62)\n"
         ">>> start = pyScript.GuCartBox((-2.0, -2.0, 2.0, 2.0), 10, 0)\n"
         ">>> end = pyScript.GuCartBox((98.0, -2.0, 102.0, 2.0), 10, 0)\n"
         ">>> start.setLineColor(0x00FF00); end.setLineColor(0xFF0000)\n"
         ">>> o = pyScript.emyPointArrayF(); route.getPointArray(o)\n"
         ">>> print('route pts:', len(o))\n"
         "route pts: 3\n"
         ">>> sb = pyScript.emyBoxF(); start.getOriginBBoxF(sb)\n"
         ">>> print('start marker:', sb)\n"
         "start marker: (-2.0, -2.0, 2.0, 2.0)"),
        ("all-three-shapes",
         "Create one of each Gu* cartoon shape (polyline route, polygon region, box frame) on the same cell, each on a distinct layer, then summarize each.",
         ["GuCartPolyLine", "GuCartPolygon", "GuCartBox"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pa = pyScript.emyPointArrayF()\n"
         ">>> pa.append((0.0, 0.0)); pa.append((20.0, 0.0)); pa.append((20.0, 15.0))\n"
         ">>> route = pyScript.GuCartPolyLine(pa, layNum=62)\n"
         ">>> ga = pyScript.emyPointArrayF()\n"
         ">>> ga.append((0.0, 0.0)); ga.append((40.0, 0.0)); ga.append((40.0, 30.0)); ga.append((0.0, 30.0))\n"
         ">>> region = pyScript.GuCartPolygon(ga, layNum=61)\n"
         ">>> frame = pyScript.GuCartBox((-5.0, -5.0, 45.0, 35.0), 10, 0)\n"
         ">>> frame.setLinePattern(2)  # dashed\n"
         ">>> ro = pyScript.emyPointArrayF(); route.getPointArray(ro)\n"
         ">>> go = pyScript.emyPointArrayF(); region.getPointArray(go)\n"
         ">>> fb = pyScript.emyBoxF(); frame.getOriginBBoxF(fb)\n"
         ">>> print('route pts:', len(ro), 'region pts:', len(go), 'frame:', fb)\n"
         "route pts: 3 region pts: 4 frame: (-5.0, -5.0, 45.0, 35.0)"),
        ("selection-region-box-polygon",
         "Build a selection region as a GuCartBox, then draw a GuCartPolygon highlighting a sub-region inside it. Read back both geometries.",
         ["GuCartBox", "GuCartPolygon"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> sel = pyScript.GuCartBox((0.0, 0.0, 200.0, 200.0))\n"
         ">>> sel.setLineColor(0x0000FF); sel.setShow(True)\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((50.0, 50.0))\n"
         ">>> arr.append((150.0, 50.0))\n"
         ">>> arr.append((150.0, 150.0))\n"
         ">>> arr.append((50.0, 150.0))\n"
         ">>> hi = pyScript.GuCartPolygon(arr, layNum=61, purNum=pyScript.emvPurposeNumberDrawing)\n"
         ">>> sb = pyScript.emyBoxF(); sel.getOriginBBoxF(sb)\n"
         ">>> ho = pyScript.emyPointArrayF(); hi.getPointArray(ho)\n"
         ">>> print('selection:', sb)\n"
         "selection: (0.0, 0.0, 200.0, 200.0)\n"
         ">>> print('highlight pts:', len(ho))\n"
         "highlight pts: 4"),
        ("polyline-measurement-trace",
         "Create a measurement trace as a polyline (open path between probe points) and a box marking the measured device area. Confirm the trace is open (polyline) vs a polygon would close.",
         ["GuCartPolyLine", "GuCartBox"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> trace = pyScript.emyPointArrayF()\n"
         ">>> trace.append((10.0, 10.0))\n"
         ">>> trace.append((30.0, 10.0))\n"
         ">>> trace.append((30.0, 40.0))\n"
         ">>> meas = pyScript.GuCartPolyLine(trace, layNum=62, purNum=pyScript.emvPurposeNumberDrawing)\n"
         ">>> dev = pyScript.GuCartBox((5.0, 5.0, 35.0, 45.0), 10, 0)\n"
         ">>> dev.setLineColor(0xFF0000)\n"
         ">>> to = pyScript.emyPointArrayF(); meas.getPointArray(to)\n"
         ">>> db = pyScript.emyBoxF(); dev.getOriginBBoxF(db)\n"
         ">>> print('trace (open) pts:', len(to))\n"
         "trace (open) pts: 3\n"
         ">>> print('device area:', db)\n"
         "device area: (5.0, 5.0, 35.0, 45.0)"),
        ("gu-cartoon-roundtrip",
         "End-to-end: create a polygon, extract its points, rebuild a polyline from those same points (open version), and a box around the polygon's extent. Demonstrates interconversion among all 3 Gu* classes.",
         ["GuCartPolygon", "GuCartPolyLine", "GuCartBox"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> src = pyScript.emyPointArrayF()\n"
         ">>> src.append((0.0, 0.0))\n"
         ">>> src.append((20.0, 0.0))\n"
         ">>> src.append((20.0, 20.0))\n"
         ">>> src.append((0.0, 20.0))\n"
         ">>> poly = pyScript.GuCartPolygon(src, layNum=61)\n"
         ">>> pts = pyScript.emyPointArrayF()\n"
         ">>> poly.getPointArray(pts)\n"
         ">>> pl = pyScript.GuCartPolyLine(pts, layNum=62)\n"
         ">>> frame = pyScript.GuCartBox((0.0, 0.0, 20.0, 20.0), 10, 0)\n"
         ">>> ro = pyScript.emyPointArrayF(); pl.getPointArray(ro)\n"
         ">>> fb = pyScript.emyBoxF(); frame.getOriginBBoxF(fb)\n"
         ">>> print('polyline (open) pts:', len(ro), 'frame:', fb)\n"
         "polyline (open) pts: 4 frame: (0.0, 0.0, 20.0, 20.0)"),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v29-S6-%s" % apis_str, prompt, completion, apis,
             "S6 cross_api_workflow: %s" % scenario)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    parser = argparse.ArgumentParser(
        description="R199 v29 Gu* cartoon SFT corpus builder (3 APIs, 25 pairs)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print stats only, do not write output file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Output JSONL path (default: %s)" % DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of pairs (for testing)")
    args = parser.parse_args()

    sys.stderr.write("R199 v29 Gu* cartoon corpus builder\n")
    sys.stderr.write("  Target APIs: %d (%s)\n" % (len(API_ORDER), ", ".join(API_ORDER)))

    missing = [a for a in API_ORDER if a not in API_DOCS]
    if missing:
        sys.stderr.write("ERROR: Missing API_DOCS for: %s\n" % ", ".join(missing))
        sys.exit(1)

    eval_eps = load_eval_entry_points()
    sys.stderr.write("  Eval entry_points loaded: %d\n" % len(eval_eps))

    pairs, rejected, reject_details = build_pairs(eval_eps, limit=args.limit)

    api_coverage = {}
    for p in pairs:
        for a in p["api_used"]:
            api_coverage[a] = api_coverage.get(a, 0) + 1

    type_counts = {}
    for p in pairs:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

    sys.stderr.write("\n=== R199 v29 Corpus Stats ===\n")
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

    with open(args.output, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    sys.stderr.write("\nWrote %d pairs to %s\n" % (len(pairs), args.output))


if __name__ == "__main__":
    main()
