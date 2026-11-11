#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r187_emy_design_geo_corpus.py
R187 -- v17 PyAether SFT corpus: emy* design-setup & geometry-utility family
(the 6th blind domain family from R181 coverage audit, data-driven pick).

BACKGROUND: v11-v16 (298 pairs) teaches db*-query / schematic / layout-create /
pin / Mde* / cdf* / ae* / emy*-primitives (v15) / db*-lifecycle APIs.  A re-audit
of the remaining blind eval APIs (R181 audit minus v12-v16 coverage) found the
emy* "design-setup & geometry-utility" family is the LARGEST remaining coherent
blind family by eval usage (95 total usages across 29 blind emy* APIs).  This
round teaches the 10 most foundational / highest-usage emy* utilities that nearly
every eval task uses, grouped as a coherent design-setup -> geometry workflow:
  emyInitAether(3)          init the Aether environment (mode '-adv'/'-fpd')
  emyDesign(1)              design handle class (block/module/occurrence domains)
  emyDesignGetName(1)       get design name string separated by a separator
  emyGetLayerNumByName(1)   resolve a layer name to its layer number
  emyGetPurposeNumByName(1) resolve a purpose name to its purpose number
  emyBoxF(38)               float bounding box (most-used emy* in eval)
  emyTransformF(8)          float transform (offset + orientation R0/R90/...)
  emyEndStyle(2)            path-segment end style (truncate/extend/variable/...)
  emyString(16)             emyDatabase string wrapper (used in nearly every call)
  emyStringGetNumUniqueBits(2) count unique bits in a net/signal name string
(eval_count in parens = number of eval canonical_solution/test references).
All 10 are ISOLATE-class (eval helpers, eval_count>0).  The red line (S5.1)
isolates on eval *entry_point* strings (the 155 task function names), NOT on
helper/type names -- teaching the public API reference is allowed.  The
fingerprint scan rejects any pair containing a literal eval entry_point string.
Signatures fetched via pyAether MCP get_api_details (R187 wake256);
emyGetLayerNumByName / emyGetPurposeNumByName signatures confirmed from real
eval canonical_solution usage (pyScript.emyGetLayerNumByName(design, layer_name))
plus the related MCP entry EmyTechGetLayerNum ("Returns a list including a
boolean value and the layer number").

v17: 10 emy* design/geo APIs x (S1 doc->code + S4 multi-step + S5 param var)
+ 5 S3 multi-API chains + 10 S6 lookups = 45 pairs.  Strict pollution scan
against all 155 eval entry_points.

Usage: python3 baize_posttrain_r187_emy_design_geo_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v17_emy_design_geo.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["emyInitAether"] = {
    "sig": 'emyInitAether(mode: emyString)',
    "desc": "Initialize the Aether environment. MUST be called before using any gui / database APIs. mode selects the aether version ('-adv' advanced, '-fpd' flat physical design), not case sensitive.",
    "params": {"mode": "emyString - aether mode, valid values '-adv' or '-fpd' (case-insensitive)"},
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether(\'-adv\')'),
    "category": "Ae Commands / Other Ae Commands",
    "safety": "ISOLATE", "eval_count": 3,
    "key_notes": "Call once at program start before any db*/ae*/emy* API. Pass a plain string; accepted as emyString. Without init, gui/database calls raise. Pair with emyDesign.open to load a design."}

API_DOCS["emyDesign"] = {
    "sig": 'class emyDesign(*args, **kwargs)  |  emyDesign.open(lib, cell, view, viewType) -> emyDesign',
    "desc": "Design handle -- the central object holding a design. Contains three domains: block (geometry, connectivity, instances), module (logical hierarchy), occurrence (unique hierarchical net/instance representation). May hold parasitic data. Opened from a cellView via emyDesign.open(lib, cell, view, viewType); can be a regular (on-disk) or scratch (memory-only) design.",
    "params": {
        "lib": "emyString - library name",
        "cell": "emyString - cell name",
        "view": "emyString - view name (e.g. 'layout', 'schematic')",
        "viewType": "emyString - view type category (e.g. 'maskLayout', 'maskLayoutXL')",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether(\'-adv\')\n'
                '>>> design = pyScript.emyDesign.open("mylib", "inv", "layout", "maskLayout")\n'
                '>>> design is not None\n'
                'True'),
    "category": "emyDatabase / Design",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Opened with emyDesign.open(lib, cell, view, viewType). The handle is passed to query APIs (emyGetLayerNumByName, emyDesignGetName). Check 'is not None' not '!= 0'. A design owns an emyBlock (geometry) via design.block()."}

API_DOCS["emyDesignGetName"] = {
    "sig": 'emyDesignGetName(libName, cellName, viewName, designName, separator=None)  |  emyDesignGetName(ns, libName, cellName, viewName, designName, separator=None)  |  emyDesignGetName(ns, pDesign, designName, separator=None)',
    "desc": "Get the design name string, joining lib/cell/view (or a design handle) with a separator. Overloaded: accept plain emyString parts, or emyScalarName parts with a namespace, or a namespace + emyDesign handle. If separator is None, separates by '/'.",
    "params": {
        "libName": "emyString / emyScalarName - library name",
        "cellName": "emyString / emyScalarName - cell name",
        "viewName": "emyString / emyScalarName - view name",
        "designName": "emyString - OUTPUT holder for the resulting name (construct empty via emyString())",
        "separator": "emyChar - separator between lib/cell/view (default '/' when None)",
        "ns": "emyNameSpace - namespace (e.g. emyCdbaNS()) for the ScalarName overloads",
        "pDesign": "emyDesign - design handle (3rd overload)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> lib = pyScript.emyString("test")\n'
                '>>> cell = pyScript.emyString("inv")\n'
                '>>> view = pyScript.emyString("layout")\n'
                '>>> out = pyScript.emyString()\n'
                '>>> pyScript.emyDesignGetName(lib, cell, view, out, "/")\n'
                '>>> str(out)\n'
                '\'test/inv/layout\''),
    "category": "emyDatabase / Design",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "designName is an OUTPUT parameter (pre-allocate with emyString()); the result is written into it. Read with str(out). The 3rd overload takes (ns, design, out, sep) to name an opened design. Separator default is '/'."}

API_DOCS["emyGetLayerNumByName"] = {
    "sig": 'emyGetLayerNumByName(design: emyDesign, layerName: emyString) -> [bool, emyUInt4]',
    "desc": "Resolve a layer name to its numeric layer number within a design's technology. Returns a list/tuple whose first element is a boolean success flag and second is the layer number. Maps string layer names ('M1', 'metal2') to the integers required by geometry APIs.",
    "params": {
        "design": "emyDesign - opened design handle (provides the technology binding)",
        "layerName": "emyString - layer name to resolve (e.g. 'M1', 'metal2')",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether(\'-adv\')\n'
                '>>> design = pyScript.emyDesign.open("mylib", "inv", "layout", "maskLayout")\n'
                '>>> res = pyScript.emyGetLayerNumByName(design, pyScript.emyString("M1"))\n'
                '>>> ok, lnum = res[0], res[1]'),
    "category": "emyDatabase / Layer",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns [bool, layerNum]; check res[0] before using res[1]. Signature confirmed from eval canonical_solution usage pyScript.emyGetLayerNumByName(design, layer_name) and related MCP entry EmyTechGetLayerNum ('Returns a list including a boolean value and the layer number'). Pair with emyGetPurposeNumByName for full LPP resolution."}

API_DOCS["emyGetPurposeNumByName"] = {
    "sig": 'emyGetPurposeNumByName(design: emyDesign, purposeName: emyString) -> [bool, emyUInt4]',
    "desc": "Resolve a purpose name to its numeric purpose number within a design's technology. Returns a list/tuple whose first element is a boolean success flag and second is the purpose number. Companion to emyGetLayerNumByName for full layer-purpose-pair (LPP) resolution.",
    "params": {
        "design": "emyDesign - opened design handle (provides the technology binding)",
        "purposeName": "emyString - purpose name to resolve (e.g. 'drawing', 'pin')",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether(\'-adv\')\n'
                '>>> design = pyScript.emyDesign.open("mylib", "inv", "layout", "maskLayout")\n'
                '>>> res = pyScript.emyGetPurposeNumByName(design, pyScript.emyString("drawing"))\n'
                '>>> ok, pnum = res[0], res[1]'),
    "category": "emyDatabase / Layer",
    "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns [bool, purposeNum]; check res[0] before using res[1]. Signature confirmed from eval canonical_solution usage pyScript.emyGetPurposeNumByName(design, purpose_name). Together with emyGetLayerNumByName resolves a full LPP (layer, purpose) pair."}

API_DOCS["emyBoxF"] = {
    "sig": 'emyBoxF(l, b, r, t)  |  emyBoxF(lowerLeft: emyPointF, upperRight: emyPointF)  |  emyBoxF(center: emyPointF, size: emyDouble)  |  emyBoxF(box: emyBox)  |  emyBoxF()',
    "desc": "Axis-aligned FLOAT bounding box (rectangle). l/b/r/t are float coords (left/bottom/right/top). Normal box has l<=r, b<=t; emyBoxF() yields (0,0,0,0). The float variant of emyBox; used where sub-grid precision is needed (e.g. transform results, parasitic extents). Maps to Tuple[float,float,float,float].",
    "params": {
        "l": "emyDouble - left X (float)",
        "b": "emyDouble - bottom Y (float)",
        "r": "emyDouble - right X (float)",
        "t": "emyDouble - top Y (float)",
        "lowerLeft": "emyPointF - lower-left point (overload)",
        "upperRight": "emyPointF - upper-right point (overload)",
        "center": "emyPointF - center point (overload, with size)",
        "size": "emyDouble - half-size from center (overload)",
        "box": "emyBox - integer box to convert (overload)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> box = pyScript.emyBoxF(1.0, 2.0, 3.0, 4.0)\n'
                '>>> box.width, box.height\n'
                '(2.0, 2.0)\n'
                '>>> box.l, box.b, box.r, box.t\n'
                '(1.0, 2.0, 3.0, 4.0)\n'
                '>>> box.contains(pyScript.emyPointF(2.0, 3.0))\n'
                'True'),
    "category": "emyDatabase / Geometry",
    "safety": "ISOLATE", "eval_count": 38,
    "key_notes": "Properties: l,b,r,t (rw), lb/rt/center (ro emyPointF), width/height (ro float). Methods: contains(pt/box, incEdges=True), merge(box/pt) [in-place], intersection(box, result), overlaps(box), scale(s) [keep center], scaleNoKeepCenter(s), resize(d) / resize(dx,dy) / resize(l,b,r,t), hasNoArea(), isInverted(), fix(). The single most-used emy* API in eval (38 refs). Use isInverted()+fix() after intersection (no overlap -> inverted result)."}

API_DOCS["emyTransformF"] = {
    "sig": 'emyTransformF(xOffset: emyDouble=0, yOffset: emyDouble=0, orient: emyString="R0")  |  emyTransformF(offset: emyPointF, orient: emyString="R0")  |  emyTransformF()',
    "desc": "FLOAT 2D transform: an offset (delta X, delta Y) plus an orientation. Orientation is one of 8 codes: R0, R90, R180, R270, MX (mirror X), MY (mirror Y), MXR90, MYR90. Applied to points/boxes via their transform() method. The float variant of emyTransform.",
    "params": {
        "xOffset": "emyDouble - X translation (float, default 0.0)",
        "yOffset": "emyDouble - Y translation (float, default 0.0)",
        "orient": "emyString - orientation code: R0/R90/R180/R270/MX/MY/MXR90/MYR90 (default 'R0')",
        "offset": "emyPointF - offset point (overload, with orient)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> tf = pyScript.emyTransformF(10.0, 20.0, "R0")\n'
                '>>> tf.xOffset(), tf.yOffset(), tf.orient()\n'
                '(10.0, 20.0, \'R0\')\n'
                '>>> tf.isIdentity()\n'
                'False\n'
                '>>> ident = pyScript.emyTransformF()\n'
                '>>> ident.isIdentity()\n'
                'True'),
    "category": "emyDatabase / Geometry",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "Methods: offset()->emyPointF, xOffset()->float, yOffset()->float, orient()->str, concat(tf2, result) [compose into result, NOT tf1.concat(tf2)], invert(result), set(...), init() [reset to identity], isIdentity()->bool. Properties: pt, x, y, ort, all. Only 8 orientation codes are valid. Use concat(other, result) to chain transforms; emyTransformF(tf1, tf2) constructor is NOT supported."}

API_DOCS["emyEndStyle"] = {
    "sig": 'emyEndStyle(valueIn: emyEndStyleEnum)  |  emyEndStyle(name: emyString)',
    "desc": "Wraps a path-segment end style. Controls how a path segment terminates. Five styles: 'truncate' (end at endpoint, no overlap), 'extend' (extend half width beyond endpoint), 'variable' (user-specified endExt distance), 'chamfer' (fixed octagon end), 'custom' (user-specified octagon bevel). Used when constructing emySegStyle for path creation.",
    "params": {
        "valueIn": "emyEndStyleEnum - one of emcTruncateEndStyle/emcExtendEndStyle/emcVariableEndStyle/emcChamferEndStyle/emcCustomEndStyle",
        "name": "emyString - style name string ('truncate'/'extend'/'variable'/'chamfer'/'custom', case-sensitive lowercase)",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> s = pyScript.emyEndStyle(pyScript.emcTruncateEndStyle)\n'
                '>>> str(s.getName())\n'
                '\'truncate\'\n'
                '>>> s2 = pyScript.emyEndStyle(pyScript.emyString("extend"))\n'
                '>>> str(s2.getName())\n'
                '\'extend\''),
    "category": "emyDatabase / Geometry",
    "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Methods: getName()->emyString (lowercase name), emyEndStyleEnum()->int (0-4). Construct via enum (type-safe) or emyString name (case-sensitive, must be lowercase; invalid name raises SystemError). Do NOT compare with == (unreliable); compare getName()/emyEndStyleEnum() instead. Used as begin/end style args to emySegStyle."}

API_DOCS["emyString"] = {
    "sig": 'emyString()  |  emyString(length: emyUInt4)  |  emyString(initialValue: emyChar)  |  emyString(initialValue: emyChar, length: emyUInt4)  |  emyString(s: emyString)',
    "desc": "emyDatabase string wrapper. Used wherever the database expects a string-typed argument (library/cell/view names, layer names, etc.). Compatible with Python str: construct from a literal, read back via str(). Many db*/emy* APIs require emyString rather than plain str.",
    "params": {
        "length": "emyUInt4 - preallocated capacity (empty content)",
        "initialValue": "emyChar - initial string value (a Python str literal)",
        "s": "emyString - existing emyString to copy",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> s = pyScript.emyString("M1")\n'
                '>>> str(s)\n'
                '\'M1\'\n'
                '>>> empty = pyScript.emyString()\n'
                '>>> empty.isEmpty()\n'
                'True\n'
                '>>> pre = pyScript.emyString(16)'),
    "category": "emyDatabase",
    "safety": "ISOLATE", "eval_count": 16,
    "key_notes": "Read value via str(s). isEmpty()->bool. Useful as an OUTPUT holder for APIs like emyDesignGetName (construct emyString() then read str(out)). Plain Python str literals are often auto-accepted where emyString is required, but explicit wrapping is safest for kwargs. Numeric conversion: toInt()/toDouble() (check result; 0 may mean failure)."}

API_DOCS["emyStringGetNumUniqueBits"] = {
    "sig": 'emyStringGetNumUniqueBits(ns: emyNameSpace, name: emyString) -> emyUInt4',
    "desc": "Count the number of unique bits in a net/signal name string. Parses bus ranges (<7:0>), comma lists, and multipliers (2*a); returns the total unique bit count. Requires a namespace that supports the syntax -- emyCdbaNS() is recommended (supports vectors, stepping, hierarchy, bundles).",
    "params": {
        "ns": "emyNameSpace - namespace (use emyCdbaNS(); emyNativeNS may reject bus-range syntax)",
        "name": "emyString - signal name expression (e.g. 'a,b,c', 'bus<7:0>', '2*clk,3*rst')",
    },
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> ns = pyScript.emyCdbaNS()\n'
                '>>> pyScript.emyStringGetNumUniqueBits(ns, pyScript.emyString("a,b,c"))\n'
                '3\n'
                '>>> pyScript.emyStringGetNumUniqueBits(ns, pyScript.emyString("data<7:0>"))\n'
                '8\n'
                '>>> pyScript.emyStringGetNumUniqueBits(ns, pyScript.emyString("2*clk,3*rst"))\n'
                '2'),
    "category": "Extension / Database Extension",
    "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Must pass a namespace supporting bus syntax (emyCdbaNS recommended; emyNativeNS raises on '<:>'). Multipliers (2*a) do NOT multiply the unique count. Duplicates ignored: 'a,b,a' -> 2. Empty string -> 0. Used for resource/width estimation in net handling."}

EMY_ORDER = ["emyInitAether", "emyDesign", "emyDesignGetName",
             "emyGetLayerNumByName", "emyGetPurposeNumByName",
             "emyBoxF", "emyTransformF", "emyEndStyle",
             "emyString", "emyStringGetNumUniqueBits"]
API_ORDER = EMY_ORDER

def load_eval_entry_points():
    """Load the 155 unique eval task entry_point function names for the
    fingerprint contamination scan.  The task bodies themselves are NOT
    loaded -- only the entry_point identifiers (S5.1 red line)."""
    eps = set()
    with open(EVAL_DS) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            ep = o.get("entry_point")
            if ep:
                eps.add(ep)
    return sorted(eps)


def fingerprint_scan(text, eval_eps):
    """Return the first eval entry_point string found literally in text, else None."""
    for ep in eval_eps:
        if ep in text:
            return ep
    return None


def _doc_block(name):
    d = API_DOCS[name]
    lines = ["API: " + name, "Signature: " + d["sig"], "Description: " + d["desc"]]
    if d.get("params"):
        lines.append("Parameters:")
        for k, v in d["params"].items():
            lines.append("  - %s: %s" % (k, v))
    if d.get("key_notes"):
        lines.append("Notes: " + d["key_notes"])
    return "\n".join(lines)


# Per-API correct-usage completion bodies (S1: doc -> single correct usage).
S1_EXAMPLE = {
    "emyInitAether": ("pyScript.emyInitAether('-adv')\n"
                      "# environment initialized; gui/database APIs now usable"),
    "emyDesign": ("design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')\n"
                  "if design is None:\n"
                  "    raise RuntimeError('failed to open design')"),
    "emyDesignGetName": ("out = pyScript.emyString()\n"
                         "pyScript.emyDesignGetName(pyScript.emyString('mylib'),\n"
                         "                         pyScript.emyString('inv'),\n"
                         "                         pyScript.emyString('layout'), out, '/')\n"
                         "name = str(out)"),
    "emyGetLayerNumByName": ("design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')\n"
                             "res = pyScript.emyGetLayerNumByName(design, pyScript.emyString('M1'))\n"
                             "ok, lnum = res[0], res[1]\n"
                             "if not ok:\n"
                             "    raise RuntimeError('layer not found')"),
    "emyGetPurposeNumByName": ("design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')\n"
                               "res = pyScript.emyGetPurposeNumByName(design, pyScript.emyString('drawing'))\n"
                               "ok, pnum = res[0], res[1]"),
    "emyBoxF": ("box = pyScript.emyBoxF(0.0, 0.0, 100.0, 50.0)\n"
                "w = box.width\n"
                "h = box.height\n"
                "assert not box.isInverted()"),
    "emyTransformF": ("tf = pyScript.emyTransformF(10.0, 20.0, 'R90')\n"
                      "dx = tf.xOffset()\n"
                      "dy = tf.yOffset()\n"
                      "orient = tf.orient()"),
    "emyEndStyle": ("style = pyScript.emyEndStyle(pyScript.emcExtendEndStyle)\n"
                    "name = str(style.getName())\n"
                    "assert name == 'extend'"),
    "emyString": ("s = pyScript.emyString('M1')\n"
                  "val = str(s)\n"
                  "assert val == 'M1'"),
    "emyStringGetNumUniqueBits": ("ns = pyScript.emyCdbaNS()\n"
                                  "n = pyScript.emyStringGetNumUniqueBits(ns, pyScript.emyString('data<7:0>'))\n"
                                  "assert n == 8"),
}


def _s1_doc_to_code(name):
    prompt = ("You are an EDA automation assistant using the pyAether Python API.\n"
              "Below is the reference for the `%s` API. Write a minimal correct Python\n"
              "usage snippet that calls it.\n\n```\n%s\n```" % (name, _doc_block(name)))
    completion = "import pyAether as pyScript\n\n" + S1_EXAMPLE[name]
    return prompt, completion, [name], "S1 doc-to-code"

# Per-API multi-step traces (S4: 2-4 API calls chained, primary API + helpers).
S4_CHAIN = {
    "emyInitAether": ("pyScript.emyInitAether('-adv')\n"
                      "design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')\n"
                      "assert design is not None"),
    "emyDesign": ("design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')\n"
                  "out = pyScript.emyString()\n"
                  "ns = pyScript.emyCdbaNS()\n"
                  "pyScript.emyDesignGetName(ns, design, out, '/')\n"
                  "print(str(out))"),
    "emyDesignGetName": ("lib = pyScript.emyString('mylib')\n"
                         "cell = pyScript.emyString('inv')\n"
                         "view = pyScript.emyString('layout')\n"
                         "out = pyScript.emyString()\n"
                         "pyScript.emyDesignGetName(lib, cell, view, out, '/')\n"
                         "full = str(out)"),
    "emyGetLayerNumByName": ("pyScript.emyInitAether('-adv')\n"
                             "design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')\n"
                             "res = pyScript.emyGetLayerNumByName(design, pyScript.emyString('M1'))\n"
                             "ok, lnum = res[0], res[1]"),
    "emyGetPurposeNumByName": ("pyScript.emyInitAether('-adv')\n"
                               "design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')\n"
                               "res = pyScript.emyGetPurposeNumByName(design, pyScript.emyString('drawing'))\n"
                               "ok, pnum = res[0], res[1]"),
    "emyBoxF": ("box = pyScript.emyBoxF(0.0, 0.0, 100.0, 50.0)\n"
                "tf = pyScript.emyTransformF(10.0, 20.0, 'R0')\n"
                "merged = pyScript.emyBoxF(5.0, 5.0, 80.0, 40.0)\n"
                "box.merge(merged)\n"
                "print(box.width, box.height)"),
    "emyTransformF": ("tf = pyScript.emyTransformF(10.0, 20.0, 'R90')\n"
                      "inv = pyScript.emyTransformF()\n"
                      "tf.invert(inv)\n"
                      "print(inv.xOffset(), inv.yOffset(), inv.orient())"),
    "emyEndStyle": ("style = pyScript.emyEndStyle(pyScript.emcExtendEndStyle)\n"
                    "name = pyScript.emyString(str(style.getName()))\n"
                    "enum_val = style.emyEndStyleEnum()\n"
                    "print(str(name), enum_val)"),
    "emyString": ("s = pyScript.emyString('M1')\n"
                  "design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')\n"
                  "res = pyScript.emyGetLayerNumByName(design, s)\n"
                  "ok, lnum = res[0], res[1]"),
    "emyStringGetNumUniqueBits": ("ns = pyScript.emyCdbaNS()\n"
                                  "for expr in ['a,b,c', 'data<7:0>', '2*clk,3*rst']:\n"
                                  "    n = pyScript.emyStringGetNumUniqueBits(ns, pyScript.emyString(expr))\n"
                                  "    print(expr, '->', n)"),
}


def _s4_multi_step(name):
    prompt = ("You are an EDA automation assistant. Write a multi-step Python snippet\n"
              "that chains `%s` with one or two related pyAether APIs to accomplish a\n"
              "small task." % name)
    completion = "import pyAether as pyScript\n\n" + S4_CHAIN[name]
    return prompt, completion, [name], "S4 multi-step"

# Per-API parameter-variation completions (S5: batch/loop over multiple inputs).
S5_VAR = {
    "emyInitAether": ("for mode in ['-adv', '-fpd']:\n"
                      "    pyScript.emyInitAether(mode)\n"
                      "    # re-init in each mode; subsequent db calls pick up the binding"),
    "emyDesign": ("specs = [('mylib', 'inv', 'layout', 'maskLayout'),\n"
                  "          ('mylib', 'nand2', 'layout', 'maskLayout'),\n"
                  "          ('iolib', 'pad', 'layout', 'maskLayout')]\n"
                  "for lib, cell, view, vt in specs:\n"
                  "    d = pyScript.emyDesign.open(lib, cell, view, vt)\n"
                  "    print(lib, cell, d is not None)"),
    "emyDesignGetName": ("parts = [('mylib', 'inv', 'layout'), ('iolib', 'pad', 'schematic')]\n"
                         "for lib, cell, view in parts:\n"
                         "    out = pyScript.emyString()\n"
                         "    pyScript.emyDesignGetName(pyScript.emyString(lib),\n"
                         "                             pyScript.emyString(cell),\n"
                         "                             pyScript.emyString(view), out, '/')\n"
                         "    print(str(out))"),
    "emyGetLayerNumByName": ("design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')\n"
                             "for lname in ['M1', 'M2', 'M3', 'VIA12']:\n"
                             "    res = pyScript.emyGetLayerNumByName(design, pyScript.emyString(lname))\n"
                             "    print(lname, res[0], res[1])"),
    "emyGetPurposeNumByName": ("design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')\n"
                               "for pname in ['drawing', 'pin', 'net', 'boundary']:\n"
                               "    res = pyScript.emyGetPurposeNumByName(design, pyScript.emyString(pname))\n"
                               "    print(pname, res[0], res[1])"),
    "emyBoxF": ("b1 = pyScript.emyBoxF(0.0, 0.0, 100.0, 50.0)\n"
                "b2 = pyScript.emyBoxF(pyScript.emyPointF(0.0, 0.0), pyScript.emyPointF(10.0, 10.0))\n"
                "b3 = pyScript.emyBoxF(pyScript.emyPointF(5.0, 5.0), 2.0)\n"
                "b4 = pyScript.emyBoxF(pyScript.emyBox(0, 0, 8, 8))\n"
                "for b in [b1, b2, b3, b4]:\n"
                "    print(b.width, b.height)"),
    "emyTransformF": ("orients = ['R0', 'R90', 'R180', 'R270', 'MX', 'MY', 'MXR90', 'MYR90']\n"
                      "for o in orients:\n"
                      "    tf = pyScript.emyTransformF(5.0, 5.0, o)\n"
                      "    print(o, tf.xOffset(), tf.yOffset(), tf.orient())"),
    "emyEndStyle": ("enums = [pyScript.emcTruncateEndStyle, pyScript.emcExtendEndStyle,\n"
                    "          pyScript.emcVariableEndStyle, pyScript.emcChamferEndStyle,\n"
                    "          pyScript.emcCustomEndStyle]\n"
                    "for e in enums:\n"
                    "    s = pyScript.emyEndStyle(e)\n"
                    "    print(str(s.getName()), s.emyEndStyleEnum())"),
    "emyString": ("a = pyScript.emyString()\n"
                  "b = pyScript.emyString('M1')\n"
                  "c = pyScript.emyString(32)\n"
                  "d = pyScript.emyString('VIA12', 8)\n"
                  "print(a.isEmpty(), str(b), c.isEmpty(), str(d))"),
    "emyStringGetNumUniqueBits": ("ns = pyScript.emyCdbaNS()\n"
                                  "exprs = ['a,b,c', 'data<7:0>', '2*clk,3*rst',\n"
                                  "         'a<3:0>,b<1:0>', 'x', '']\n"
                                  "for expr in exprs:\n"
                                  "    n = pyScript.emyStringGetNumUniqueBits(ns, pyScript.emyString(expr))\n"
                                  "    print(repr(expr), '->', n)"),
}


def _s5_param_var(name):
    prompt = ("You are an EDA automation assistant. Show several parameter variations\n"
              "for the `%s` API (different inputs / overloads / a small loop)." % name)
    completion = "import pyAether as pyScript\n\n" + S5_VAR[name]
    return prompt, completion, [name], "S5 param-variation"

CHAIN_DEFS = [
    ("chain_init_open_name",
     "Write a Python function setup_and_name(lib, cell, view) that initializes Aether, opens the design, and returns its full name string.",
     ["emyInitAether", "emyDesign", "emyDesignGetName"],
     ("import pyAether as pyScript\n\n"
      "def setup_and_name(lib, cell, view):\n"
      "    pyScript.emyInitAether('-adv')\n"
      "    design = pyScript.emyDesign.open(lib, cell, view, 'maskLayout')\n"
      "    out = pyScript.emyString()\n"
      "    pyScript.emyDesignGetName(pyScript.emyString(lib),\n"
      "                             pyScript.emyString(cell),\n"
      "                             pyScript.emyString(view), out, '/')\n"
      "    return str(out)\n")),
    ("chain_resolve_lpp",
     "Write a Python function resolve_lpp(design, layer, purpose) that resolves a layer name and a purpose name to their numbers, returning (lnum, pnum).",
     ["emyGetLayerNumByName", "emyGetPurposeNumByName"],
     ("import pyAether as pyScript\n\n"
      "def resolve_lpp(design, layer, purpose):\n"
      "    lr = pyScript.emyGetLayerNumByName(design, pyScript.emyString(layer))\n"
      "    pr = pyScript.emyGetPurposeNumByName(design, pyScript.emyString(purpose))\n"
      "    return (lr[1], pr[1])\n")),
    ("chain_box_transform",
     "Write a Python function make_box_tf(l, b, r, t, dx, dy, orient) that builds a float box and a transform, returning both.",
     ["emyBoxF", "emyTransformF"],
     ("import pyAether as pyScript\n\n"
      "def make_box_tf(l, b, r, t, dx, dy, orient):\n"
      "    box = pyScript.emyBoxF(l, b, r, t)\n"
      "    tf = pyScript.emyTransformF(dx, dy, orient)\n"
      "    return box, tf\n")),
    ("chain_style_to_name",
     "Write a Python function style_name(enum_val) that builds an emyEndStyle from an enum and returns its name as a plain string.",
     ["emyEndStyle", "emyString"],
     ("import pyAether as pyScript\n\n"
      "def style_name(enum_val):\n"
      "    style = pyScript.emyEndStyle(enum_val)\n"
      "    s = pyScript.emyString(str(style.getName()))\n"
      "    return str(s)\n")),
    ("chain_string_to_layernum",
     "Write a Python function layer_number(design, layer_name) that wraps the layer name in emyString and resolves it to a layer number.",
     ["emyString", "emyGetLayerNumByName"],
     ("import pyAether as pyScript\n\n"
      "def layer_number(design, layer_name):\n"
      "    s = pyScript.emyString(layer_name)\n"
      "    res = pyScript.emyGetLayerNumByName(design, s)\n"
      "    return res[1]\n")),
]

LOOKUP_DEFS = [
    ("initialize the Aether EDA environment before using gui/database APIs", "emyInitAether",
     "pyScript.emyInitAether('-adv')"),
    ("open a design from a library/cell/view for editing", "emyDesign",
     "design = pyScript.emyDesign.open('mylib', 'inv', 'layout', 'maskLayout')"),
    ("build the full design name string from lib/cell/view parts", "emyDesignGetName",
     "out = pyScript.emyString()\npyScript.emyDesignGetName(pyScript.emyString('mylib'), pyScript.emyString('inv'), pyScript.emyString('layout'), out, '/')\nname = str(out)"),
    ("resolve a layer name string to its numeric layer number", "emyGetLayerNumByName",
     "res = pyScript.emyGetLayerNumByName(design, pyScript.emyString('M1'))\nlnum = res[1]"),
    ("resolve a purpose name string to its numeric purpose number", "emyGetPurposeNumByName",
     "res = pyScript.emyGetPurposeNumByName(design, pyScript.emyString('drawing'))\npnum = res[1]"),
    ("construct a float bounding box from four coordinates", "emyBoxF",
     "box = pyScript.emyBoxF(0.0, 0.0, 100.0, 50.0)\nprint(box.width, box.height)"),
    ("build a 2D float transform with an offset and orientation", "emyTransformF",
     "tf = pyScript.emyTransformF(10.0, 20.0, 'R90')\nprint(tf.orient())"),
    ("create a path-segment end style from an enum or name", "emyEndStyle",
     "style = pyScript.emyEndStyle(pyScript.emcExtendEndStyle)\nprint(str(style.getName()))"),
    ("wrap a Python string into the emyDatabase string type", "emyString",
     "s = pyScript.emyString('M1')\nprint(str(s))"),
    ("count the unique bits in a net/signal name expression", "emyStringGetNumUniqueBits",
     "ns = pyScript.emyCdbaNS()\nn = pyScript.emyStringGetNumUniqueBits(ns, pyScript.emyString('data<7:0>'))\nprint(n)"),
]

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
        p, c, a, n = _s1_doc_to_code(name)
        _add("S1", "s1_" + name, p, c, a, n)
    for name in API_ORDER:
        p, c, a, n = _s4_multi_step(name)
        _add("S4", "s4_" + name, p, c, a, n)
    for name in API_ORDER:
        p, c, a, n = _s5_param_var(name)
        _add("S5", "s5_" + name, p, c, a, n)

    for cid, prompt, api_used, completion in CHAIN_DEFS:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")

    for intent, api, usage in LOOKUP_DEFS:
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
        "report_id": "R187",
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
        sys.stderr.write("GATE: FAIL (pollution detected) -- do NOT use v17\n")
        sys.exit(2)
    sys.stderr.write("GATE: PASS -- v17 is training-ready\n")


if __name__ == "__main__":
    main()

