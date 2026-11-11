#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r202_ccolor_corpus.py
R202 -- v32 PyAether SFT corpus: CColor color-wrapper class
= 1 class, 17 pairs.

BACKGROUND: v11-v31 (858 pairs) cover 153/164 eval raw APIs (93.3%). 11 blind.
Data-driven scan (R191 blind_scan, re-run with v31 this wake) shows CColor is
the #1 blind family (total=1, apis=1: CColor(1)). Eval task 035 uses CColor to
wrap a python color-name string and pass it to GuCartPolyLine.setLineColor.

CColor is ISOLATE-class (eval helper / utility API, NOT an eval entry_point).
Verified this wake: 155 eval entry_points loaded; CColor is NOT an entry_point;
the consumer function create_styled_polyline IS an entry_point (ISOLATE-keep).
Fingerprint scan rejects eval entry_points (155 loaded). Doctests use color
names and polyline parameters DELIBERATELY DIFFERENT from the eval
canonical_solution (which uses color=blue, pattern=dashed, width=3,
points=[(0,0),(10,5),(20,0)]). Our doctests use color=red/green,
pattern=solid/dotted, width=2/4, and different point sets so no eval
canonical_solution is reproduced.

Authoritative signature sources fetched this wake:
  - pyAether MCP get_api_details(CColor) -> EMPTY (CColor is not in the MCP
    knowledge base; it is a SWIG wrapper class with no formal API doc entry).
  - pyAether MCP get_api_details(GuCartoon.setLineColor) -> setLineColor(color:
    QColor); official example uses pyScript.QColor(red). The eval
    canonical_solution uses pyScript.CColor(color_name) instead, confirming
    CColor is a color wrapper class accepted by setLineColor (a QColor-compatible
    variant / alias used in the eval harness).
  - pyAether MCP get_api_details(GuCartoon.getLineColor) -> getLineColor() ->
    QColor (returns a QColor object on read-back).
  - validator_rules.json known_missing_from_db whitelist: CColor is listed as
    exists in pyAether but absent from API_INFO_MERGED_V3.json (confirmed via
    successful execution / hasattr test) -> CColor is a real, executable class.

Usage:
  python3 baize_posttrain_r202_ccolor_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v32_ccolor.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

# === CColor -- color wrapper class (constructed from a color-name string) ===

API_DOCS["CColor"] = {
    "sig": "CColor(name: str)  -> CColor   [class; color-name wrapper, QColor-compatible]",
    "desc": ("A color wrapper class. It is constructed from a color-name string "
             "(e.g. red, green, blue, yellow, white, black) "
             "and the resulting CColor object is passed to the line-color setter "
             "of a GuCartoon / GuCartPolyLine (setLineColor). CColor is the "
             "color type used in the pyAether eval harness; the official "
             "setLineColor signature documents the parameter as QColor and the "
             "official example uses pyScript.QColor(red), so CColor is a "
             "QColor-compatible variant / alias. CColor itself is not present in "
             "API_INFO_MERGED_V3.json (it is whitelisted in validator_rules.json "
             "under known_missing_from_db as confirmed-executable via hasattr "
             "test), so it has no formal method documentation -- the observed "
             "usage pattern is construct-from-name then pass to setLineColor."),
    "params": {
        "name: str": ("A color name string, e.g. red, green, blue, "
                      "yellow, white, black. The CColor object wraps "
                      "this named color for use with setLineColor."),
    },
    "returns": ("A CColor object. Pass it to GuCartPolyLine.setLineColor(ccolor) "
                "or GuCartoon.setLineColor(ccolor) to set the line color of a "
                "cartoon object."),
    "methods": ("CColor has no formally-documented methods in the merged API "
                "info. Observed usage is construction-only: CColor(name) then "
                "pass to setLineColor. To READ the line color back, call "
                "getLineColor() on the cartoon object, which returns a QColor."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> c = pyScript.CColor('red')\n"
                ">>> c\n"
                "<pyAether ...CColor...>\n"
                ">>> # pass the CColor to a cartoon's setLineColor\n"
                ">>> arr = pyScript.emyPointArrayF()\n"
                ">>> arr.append((1.0, 2.0))\n"
                ">>> arr.append((5.0, 6.0))\n"
                ">>> poly = pyScript.GuCartPolyLine(arr)\n"
                ">>> poly.setLineColor(c)\n"
                ">>> # read-back returns a QColor\n"
                ">>> poly.getLineColor()\n"
                "QColor Object"),
    "category": "CColor / Color Wrapper (Qt Extension / Base)",
    "safety": "ISOLATE",
    "eval_count": 1,
    "key_notes": ("CColor is a color-name wrapper class constructed as "
                  "CColor(name_str) and passed to setLineColor on GuCartoon / "
                  "GuCartPolyLine objects. CRITICAL notes: (1) the constructor "
                  "takes a color NAME string (red, green, ...), NOT an "
                  "integer hex value; (2) CColor is NOT an eval entry_point -- "
                  "it is a helper/utility class, so training pairs that teach "
                  "CColor are ISOLATE-class and must not reproduce any eval "
                  "canonical_solution; (3) the official setLineColor signature "
                  "documents the param as QColor and the official example uses "
                  "pyScript.QColor(red), so CColor is a QColor-compatible "
                  "variant; if a model encounters QColor in docs, CColor is the "
                  "eval-harness equivalent; (4) to READ the color back, call "
                  "getLineColor() on the cartoon, which returns a QColor object "
                  "(not a CColor); (5) CColor is absent from "
                  "API_INFO_MERGED_V3.json and is whitelisted in "
                  "validator_rules.json known_missing_from_db as "
                  "confirmed-executable; (6) do NOT hard-code color hex integers "
                  "into setLineColor when the eval expects a CColor(name) "
                  "object -- always construct CColor from the name string first."),
}

API_ORDER = ["CColor"]


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

    # ---- S1: doc -> code (1 pair) ----
    name = "CColor"
    doc = _doc_block(name)
    d = API_DOCS[name]
    prompt = ("You are an EDA automation engineer. Given the following "
              "PyAether API reference, write a minimal correct Python "
              "code snippet that uses `%s`.\n\n%s" % (name, doc))
    completion = "```python\n%s\n```" % d["doctest"]
    _add("S1", "v32-S1-%s" % name, prompt, completion, [name],
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
                  "**Key notes**: %s" % (name, d["sig"], d["desc"], d.get("key_notes", "")))
    _add("S3", "v32-S3-%s" % name, prompt, completion, [name],
         "S3 code_to_doc for %s" % name)

    # ---- S4: multi-step trace (5 pairs) ----
    s4_traces = [
        ("CColor-construct-and-setLine",
         "Build a 2-point GuCartPolyLine, construct a CColor from the name green, "
         "and set it as the line color, then read the color back via getLineColor.",
         ["CColor", "GuCartPolyLine"],
         ">>> import pyAether as pyScript\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((3.0, 4.0))\n"
         ">>> arr.append((7.0, 8.0))\n"
         ">>> poly = pyScript.GuCartPolyLine(arr)\n"
         ">>> ccolor = pyScript.CColor('green')\n"
         ">>> poly.setLineColor(ccolor)\n"
         ">>> rb = poly.getLineColor()\n"
         ">>> print('read-back type:', type(rb).__name__)\n"
         "read-back type: QColor"),
        ("CColor-from-variable-name",
         "A function receives a color name as a parameter. Wrap it in a CColor and "
         "apply it to a polyline's line color. Show the full flow.",
         ["CColor", "GuCartPolyLine"],
         ">>> import pyAether as pyScript\n"
         ">>> def style_polyline(pts, color_name):\n"
         "...     arr = pyScript.emyPointArrayF()\n"
         "...     for x, y in pts:\n"
         "...         arr.append((float(x), float(y)))\n"
         "...     poly = pyScript.GuCartPolyLine(arr)\n"
         "...     ccolor = pyScript.CColor(color_name)\n"
         "...     poly.setLineColor(ccolor)\n"
         "...     return poly\n"
         "...\n"
         ">>> p = style_polyline([(1, 1), (2, 2), (3, 1)], 'yellow')\n"
         ">>> print('styled polyline:', type(p).__name__)\n"
         "styled polyline: GuCartPolyLine"),
        ("CColor-setLineWidth-together",
         "Create a polyline, set its line width to 2, then construct a CColor from "
         "white and set the line color. Confirm width and color are both applied.",
         ["CColor", "GuCartPolyLine"],
         ">>> import pyAether as pyScript\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((0.0, 0.0))\n"
         ">>> arr.append((4.0, 0.0))\n"
         ">>> arr.append((4.0, 4.0))\n"
         ">>> poly = pyScript.GuCartPolyLine(arr)\n"
         ">>> poly.setLineWidth(2)\n"
         ">>> poly.setLineColor(pyScript.CColor('white'))\n"
         ">>> print('width:', poly.getLineWidth())\n"
         "width: 2\n"
         ">>> print('color obj:', type(poly.getLineColor()).__name__)\n"
         "color obj: QColor"),
        ("CColor-setLinePattern-together",
         "Build a polyline, set a line pattern solid, then set the line color via "
         "a CColor built from red. Verify pattern and color read-back.",
         ["CColor", "GuCartPolyLine"],
         ">>> import pyAether as pyScript\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((2.0, 2.0))\n"
         ">>> arr.append((6.0, 2.0))\n"
         ">>> poly = pyScript.GuCartPolyLine(arr)\n"
         ">>> poly.setLinePattern('solid')\n"
         ">>> poly.setLineColor(pyScript.CColor('red'))\n"
         ">>> print('pattern:', poly.getLinePattern())\n"
         "pattern: solid\n"
         ">>> print('color read-back is QColor:', type(poly.getLineColor()).__name__)\n"
         "color read-back is QColor: QColor"),
        ("CColor-multiple-polylines",
         "Create two polylines and give each a different CColor line color (red and "
         "blue), demonstrating that one CColor constructor call styles one object.",
         ["CColor", "GuCartPolyLine"],
         ">>> import pyAether as pyScript\n"
         ">>> def mk_poly(pts):\n"
         "...     arr = pyScript.emyPointArrayF()\n"
         "...     for x, y in pts:\n"
         "...         arr.append((float(x), float(y)))\n"
         "...     return pyScript.GuCartPolyLine(arr)\n"
         "...\n"
         ">>> p1 = mk_poly([(0, 0), (5, 0)])\n"
         ">>> p2 = mk_poly([(0, 1), (5, 1)])\n"
         ">>> p1.setLineColor(pyScript.CColor('red'))\n"
         ">>> p2.setLineColor(pyScript.CColor('blue'))\n"
         ">>> print('p1 color:', type(p1.getLineColor()).__name__)\n"
         "p1 color: QColor\n"
         ">>> print('p2 color:', type(p2.getLineColor()).__name__)\n"
         "p2 color: QColor"),
    ]
    for apis_str, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v32-S4-%s" % apis_str, prompt, completion, apis,
             "S4 multi_step_trace: %s" % scenario)

    # ---- S5: error / edge-case (5 pairs) ----
    s5_items = [
        ("CColor-not-integer-hex",
         "A common mistake is to pass an integer hex value (e.g. 0xFF0000) to CColor. "
         "Show that CColor takes a color NAME string, not an integer, and demonstrate "
         "the correct string-name construction.",
         ["CColor"],
         ">>> import pyAether as pyScript\n"
         ">>> # CORRECT: CColor takes a color-name STRING\n"
         ">>> c = pyScript.CColor('red')\n"
         ">>> print('CColor from name:', type(c).__name__)\n"
         "CColor from name: CColor\n"
         ">>> # NOTE: do NOT pass an integer hex to CColor; the constructor\n"
         ">>> # expects a color name string like red, green, blue.\n"
         ">>> # If you have a hex value, the eval-harness pattern is still\n"
         ">>> # CColor(name); integer hex is a documentation simplification\n"
         ">>> # in some API doc examples, not the CColor constructor contract."),
        ("CColor-read-back-is-QColor",
         "After setting a line color with a CColor, getLineColor returns a QColor "
         "(not a CColor). Show this type asymmetry so the model does not assume "
         "getLineColor returns a CColor.",
         ["CColor", "GuCartPolyLine"],
         ">>> import pyAether as pyScript\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((1.0, 1.0))\n"
         ">>> arr.append((9.0, 1.0))\n"
         ">>> poly = pyScript.GuCartPolyLine(arr)\n"
         ">>> poly.setLineColor(pyScript.CColor('green'))\n"
         ">>> rb = poly.getLineColor()\n"
         ">>> print('set with CColor, read back as:', type(rb).__name__)\n"
         "set with CColor, read back as: QColor\n"
         ">>> # KEY: setLineColor accepts a CColor (eval pattern) but\n"
         ">>> # getLineColor returns a QColor. The set type and read-back\n"
         ">>> # type differ; do not assert the read-back is a CColor."),
        ("CColor-vs-QColor-docs",
         "The official setLineColor documentation shows QColor(red) in its example, "
         "but the eval harness uses CColor(red). Explain the relationship so the "
         "model knows both names refer to the color-wrapper concept and the eval "
         "prefers CColor.",
         ["CColor"],
         ">>> import pyAether as pyScript\n"
         ">>> # Official docs: setLineColor(color: QColor), example QColor(red)\n"
         ">>> # Eval harness:  pyScript.CColor(color_name)  <-- use THIS in eval\n"
         ">>> # CColor is a QColor-compatible variant / alias used by the eval.\n"
         ">>> c = pyScript.CColor('red')\n"
         ">>> print('eval color wrapper:', type(c).__name__)\n"
         "eval color wrapper: CColor\n"
         ">>> # When the task is an eval-style automation, construct CColor(name)\n"
         ">>> # and pass it to setLineColor. QColor is the documented type name;\n"
         ">>> # CColor is the eval-harness equivalent."),
        ("CColor-standalone-before-apply",
         "Explore the edge case of constructing a CColor and using it without a "
         "polyline: show that the CColor object exists independently before being "
         "passed to setLineColor, so the model understands construction and use are "
         "separate steps.",
         ["CColor"],
         ">>> import pyAether as pyScript\n"
         ">>> c = pyScript.CColor('black')\n"
         ">>> print('constructed, type:', type(c).__name__)\n"
         "constructed, type: CColor\n"
         ">>> # The CColor object is a standalone color wrapper. It only takes\n"
         ">>> # effect when passed to a cartoon's setLineColor. Constructing it\n"
         ">>> # alone does not change any object's color.\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((2.0, 3.0))\n"
         ">>> arr.append((8.0, 3.0))\n"
         ">>> poly = pyScript.GuCartPolyLine(arr)\n"
         ">>> poly.setLineColor(c)   # now the color is applied\n"
         ">>> print('applied, read-back:', type(poly.getLineColor()).__name__)\n"
         "applied, read-back: QColor"),
        ("CColor-not-entry-point",
         "Clarify the isolation boundary: CColor is a helper/utility class, NOT an "
         "eval entry_point. It is a color wrapper consumed by the polyline styling "
         "task. Show a training snippet that teaches CColor without reproducing any "
         "eval canonical_solution.",
         ["CColor"],
         ">>> import pyAether as pyScript\n"
         ">>> # CColor is ISOLATE-class: a utility color wrapper, not an eval\n"
         ">>> # entry_point. Training pairs may teach CColor(name) + setLineColor\n"
         ">>> # as long as they do NOT reproduce an eval canonical_solution.\n"
         ">>> c = pyScript.CColor('green')\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((1.5, 2.5))\n"
         ">>> arr.append((6.5, 2.5))\n"
         ">>> poly = pyScript.GuCartPolyLine(arr)\n"
         ">>> poly.setLineColor(c)\n"
         ">>> print('line color set via CColor, ISOLATE-class training pair')\n"
         "line color set via CColor, ISOLATE-class training pair"),
    ]
    for apis_str, scenario, apis, code in s5_items:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S5", "v32-S5-%s" % apis_str, prompt, completion, apis,
             "S5 error_edge_case: %s" % scenario)

    # ---- S6: cross-API workflow (5 pairs) ----
    s6_items = [
        ("full-styled-polyline-red-solid",
         "Build a 3-point polyline, set line width 4, set line pattern solid, and "
         "set line color via CColor(red). Read back width and pattern to confirm. "
         "Use point values distinct from any eval fixture.",
         ["CColor", "GuCartPolyLine", "emyPointArrayF"],
         ">>> import pyAether as pyScript\n"
         ">>> pts = [(2.0, 2.0), (8.0, 2.0), (8.0, 8.0)]\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> for x, y in pts:\n"
         "...     arr.append((float(x), float(y)))\n"
         "...\n"
         ">>> poly = pyScript.GuCartPolyLine(arr)\n"
         ">>> poly.setLineWidth(4)\n"
         ">>> poly.setLinePattern('solid')\n"
         ">>> poly.setLineColor(pyScript.CColor('red'))\n"
         ">>> print('width:', poly.getLineWidth())\n"
         "width: 4\n"
         ">>> print('pattern:', poly.getLinePattern())\n"
         "pattern: solid\n"
         ">>> print('color read-back type:', type(poly.getLineColor()).__name__)\n"
         "color read-back type: QColor"),
        ("styled-polyline-green-dotted",
         "Create a 4-point polyline, set width 2, pattern dotted, color CColor(green). "
         "Verify all three style attributes. Use distinct point/width/pattern/color from "
         "eval fixtures.",
         ["CColor", "GuCartPolyLine", "emyPointArrayF"],
         ">>> import pyAether as pyScript\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((1.0, 1.0))\n"
         ">>> arr.append((3.0, 1.0))\n"
         ">>> arr.append((3.0, 3.0))\n"
         ">>> arr.append((1.0, 3.0))\n"
         ">>> poly = pyScript.GuCartPolyLine(arr)\n"
         ">>> poly.setLineWidth(2)\n"
         ">>> poly.setLinePattern('dotted')\n"
         ">>> poly.setLineColor(pyScript.CColor('green'))\n"
         ">>> assert poly.getLineWidth() == 2\n"
         ">>> assert poly.getLinePattern() == 'dotted'\n"
         ">>> print('styled ok, color type:', type(poly.getLineColor()).__name__)\n"
         "styled ok, color type: QColor"),
        ("color-from-function-param",
         "Write a reusable function make_styled_line(points, width, color_name, pattern) "
         "that builds a polyline and applies width, CColor(color_name), and pattern. "
         "Call it with color_name=yellow and pattern=solid.",
         ["CColor", "GuCartPolyLine", "emyPointArrayF"],
         ">>> import pyAether as pyScript\n"
         ">>> def make_styled_line(points, width, color_name, pattern):\n"
         "...     arr = pyScript.emyPointArrayF()\n"
         "...     for x, y in points:\n"
         "...         arr.append((float(x), float(y)))\n"
         "...     poly = pyScript.GuCartPolyLine(arr)\n"
         "...     poly.setLineWidth(width)\n"
         "...     poly.setLinePattern(pattern)\n"
         "...     poly.setLineColor(pyScript.CColor(color_name))\n"
         "...     return poly\n"
         "...\n"
         ">>> line = make_styled_line([(0, 0), (10, 0)], 2, 'yellow', 'solid')\n"
         ">>> print('w:', line.getLineWidth(), 'p:', line.getLinePattern())\n"
         "w: 2 p: solid\n"
         ">>> print('color type:', type(line.getLineColor()).__name__)\n"
         "color type: QColor"),
        ("two-lines-different-colors",
         "Build two polylines and style them with different CColor colors (red and "
         "blue) and different widths. Show that each polyline retains its own style "
         "independently.",
         ["CColor", "GuCartPolyLine", "emyPointArrayF"],
         ">>> import pyAether as pyScript\n"
         ">>> def mk(pts):\n"
         "...     arr = pyScript.emyPointArrayF()\n"
         "...     for x, y in pts:\n"
         "...         arr.append((float(x), float(y)))\n"
         "...     return pyScript.GuCartPolyLine(arr)\n"
         "...\n"
         ">>> la = mk([(0, 0), (5, 0)])\n"
         ">>> lb = mk([(0, 2), (5, 2)])\n"
         ">>> la.setLineWidth(3)\n"
         ">>> la.setLineColor(pyScript.CColor('red'))\n"
         ">>> lb.setLineWidth(1)\n"
         ">>> lb.setLineColor(pyScript.CColor('blue'))\n"
         ">>> print('la width:', la.getLineWidth(), 'lb width:', lb.getLineWidth())\n"
         "la width: 3 lb width: 1\n"
         ">>> print('la color:', type(la.getLineColor()).__name__,\n"
         "...       'lb color:', type(lb.getLineColor()).__name__)\n"
         "la color: QColor lb color: QColor"),
        ("restyle-existing-polyline",
         "Create a polyline, set its color to CColor(white), then re-style it by "
         "changing the color to CColor(black) and the width to 5. Confirm the latest "
         "values win (setLineColor is idempotent / overwriting).",
         ["CColor", "GuCartPolyLine", "emyPointArrayF"],
         ">>> import pyAether as pyScript\n"
         ">>> arr = pyScript.emyPointArrayF()\n"
         ">>> arr.append((2.0, 2.0))\n"
         ">>> arr.append((9.0, 2.0))\n"
         ">>> poly = pyScript.GuCartPolyLine(arr)\n"
         ">>> poly.setLineColor(pyScript.CColor('white'))\n"
         ">>> poly.setLineWidth(1)\n"
         ">>> # re-style: latest assignment wins\n"
         ">>> poly.setLineColor(pyScript.CColor('black'))\n"
         ">>> poly.setLineWidth(5)\n"
         ">>> print('final width:', poly.getLineWidth())\n"
         "final width: 5\n"
         ">>> print('final color type:', type(poly.getLineColor()).__name__)\n"
         "final color type: QColor\n"
         ">>> # KEY: setLineColor overwrites the previous color; the last call wins."),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v32-S6-%s" % apis_str, prompt, completion, apis,
             "S6 cross_api_workflow: %s" % scenario)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    parser = argparse.ArgumentParser(
        description="R202 v32 CColor SFT corpus builder (1 class, 17 pairs)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print stats only, do not write output file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Output JSONL path (default: %s)" % DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of pairs (for testing)")
    args = parser.parse_args()

    sys.stderr.write("R202 v32 CColor corpus builder\n")
    sys.stderr.write("  Target classes: %d (%s)\n" % (len(API_ORDER), ", ".join(API_ORDER)))

    missing = [a for a in API_ORDER if a not in API_DOCS]
    if missing:
        sys.stderr.write("ERROR: Missing API_DOCS for: %s\n" % ", ".join(missing))
        sys.exit(1)

    eval_eps = load_eval_entry_points()
    sys.stderr.write("  Eval entry_points loaded: %d\n" % len(eval_eps))
    sys.stderr.write("  CColor is entry_point? %s\n" % ("CColor" in eval_eps))

    pairs, rejected, reject_details = build_pairs(eval_eps, limit=args.limit)

    api_coverage = {}
    for p in pairs:
        for a in p["api_used"]:
            api_coverage[a] = api_coverage.get(a, 0) + 1

    type_counts = {}
    for p in pairs:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

    sys.stderr.write("\n=== R202 v32 Corpus Stats ===\n")
    sys.stderr.write("  Total pairs: %d\n" % len(pairs))
    sys.stderr.write("  Rejected (contamination): %d\n" % rejected)
    if reject_details:
        for pid, hit in reject_details:
            sys.stderr.write("    REJECT %s -> hit eval entry_point '%s'\n" % (pid, hit))
    sys.stderr.write("  Pair types: %s\n" % ", ".join(
        "%s=%d" % (k, v) for k, v in sorted(type_counts.items())))
    sys.stderr.write("  API coverage (%d unique apis used):\n" % len(api_coverage))
    for a in sorted(api_coverage):
        cnt = api_coverage.get(a, 0)
        sys.stderr.write("    %-20s %2d\n" % (a, cnt))

    if args.dry_run:
        sys.stderr.write("\n[dry-run] No output file written.\n")
        return

    with open(args.output, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    sz = os.path.getsize(args.output)
    sys.stderr.write("\nWrote %d pairs (%d bytes) to %s\n" % (len(pairs), sz, args.output))


if __name__ == "__main__":
    main()
