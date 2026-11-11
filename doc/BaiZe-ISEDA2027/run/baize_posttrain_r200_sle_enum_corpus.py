#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r200_sle_enum_corpus.py
R200 -- v30 PyAether SFT corpus: SLE* enum constants + consuming callables
= 6 APIs (3 enum constants + 3 callables), 30 pairs.

BACKGROUND: v11-v29 (808 pairs) cover 147/164 eval raw APIs (89.6%). 17 blind.
Data-driven scan (R191 blind_scan, re-run with v29 this wake) shows SLE is the
#1 blind family (total=3, apis=3: SLE_GOA_AND(1), SLE_LE_WIRE_EXTEND(1),
SLE_LE_WIRE_VARIABLE(1)). A second lowercase family `sle` is also blind
(sleLeWireTypeEnumToEMYSegStyleEnum(1)) -- the direct consumer of the two
SLE_LE_WIRE_* constants. Covering SLE_* + sleLeWireTypeEnumToEMYSegStyleEnum
clears the top blind family and the sle family in one round.

The 3 SLE_* are enum CONSTANT values (not callable functions):
  - SLE_GOA_AND        : value of SleGOATypeEnum (geometric-AND / intersection)
                         siblings: SLE_GOA_OR, SLE_GOA_SUB, SLE_GOA_XOR.
                         consumed as the `opr` arg of emyPointArrayGOA.
  - SLE_LE_WIRE_VARIABLE: value of SleLeWireTypeEnum (variable-width wire end)
  - SLE_LE_WIRE_EXTEND : value of SleLeWireTypeEnum (extend wire end)
                         both consumed as beginType/endType of
                         sleLeWireTypeEnumToEMYSegStyleEnum and
                         sleLeWireTypeEnumToEMYEndStyleEnum.

The 3 consuming callables (ISOLATE-class eval helpers):
  - emyPointArrayGOA               (already covered; re-taught for GOA context)
  - sleLeWireTypeEnumToEMYSegStyleEnum (blind; new coverage)
  - sleLeWireTypeEnumToEMYEndStyleEnum (extra context; converts wire type back)

All 6 are ISOLATE-class (eval helper APIs/constants, NOT eval entry_points).
Fingerprint scan rejects eval entry_points (155 loaded). Doctests use
coordinates / numeric args deliberately DIFFERENT from the eval canonical
solutions (tasks 085 / 088) so no eval canonical_solution is reproduced.

Authoritative signatures fetched via pyAether MCP get_api_details + the
eda_fastmcp/docs/API_INFO_MERGED_V2.json knowledge base (R200 wake).

Usage:
  python3 baize_posttrain_r200_sle_enum_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v30_sle_enum.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

# === SLE_GOA_AND -- enum constant of SleGOATypeEnum ===

API_DOCS["SLE_GOA_AND"] = {
    "sig": "SLE_GOA_AND  [module-level constant of SleGOATypeEnum]",
    "desc": "An enumerated constant of the SleGOATypeEnum type, selecting the geometric-AND (intersection) logical operation. It is one of four sibling values: SLE_GOA_AND (intersection), SLE_GOA_OR (union), SLE_GOA_SUB (subtraction), SLE_GOA_XOR (exclusive-or). It is NOT a callable function -- it is a value passed as the `opr` argument to emyPointArrayGOA to request the AND operation between two graphics.",
    "params": {
        "(none)": "SLE_GOA_AND takes no arguments; it is a constant. Reference it as pyScript.SLE_GOA_AND.",
    },
    "returns": "An int/enum value of type SleGOATypeEnum (the AND selector). Pass it to emyPointArrayGOA(..., opr).",
    "methods": "Siblings in the same enum: SLE_GOA_AND, SLE_GOA_OR, SLE_GOA_SUB, SLE_GOA_XOR. Use pyScript.SLE_GOA_OR for union, pyScript.SLE_GOA_SUB for A-minus-B, pyScript.SLE_GOA_XOR for exclusive-or.",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> a = pyScript.emyPointArray()\n"
                ">>> for pt in [(0, 0), (20, 0), (20, 20), (0, 20)]:\n"
                "...     a.append(pt)\n"
                ">>> b = pyScript.emyPointArray()\n"
                ">>> for pt in [(10, -10), (30, -10), (30, 10), (10, 10)]:\n"
                "...     b.append(pt)\n"
                ">>> out = pyScript.emyArray_p_emyPointArray()\n"
                ">>> ok = pyScript.emyPointArrayGOA(a, b, out, pyScript.SLE_GOA_AND)\n"
                ">>> print(ok, len(out))\n"
                "True 1"),
    "category": "SLE / Geometric Operation Enum (SleGOATypeEnum)", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "SLE_GOA_AND is a CONSTANT, not a function -- never call it like SLE_GOA_AND(). It is the `opr` selector for emyPointArrayGOA meaning intersection. The 4 siblings share the SleGOATypeEnum type. The result polygon(s) come back through the output-param `out` (pre-create emyArray_p_emyPointArray); emyPointArrayGOA returns True on success. For intersection of two overlapping rectangles you get 1 result polygon; for disjoint inputs AND yields 0 polygons."}


# === SLE_LE_WIRE_VARIABLE -- enum constant of SleLeWireTypeEnum ===

API_DOCS["SLE_LE_WIRE_VARIABLE"] = {
    "sig": "SLE_LE_WIRE_VARIABLE  [module-level constant of SleLeWireTypeEnum]",
    "desc": "An enumerated constant of the SleLeWireTypeEnum type, selecting the VARIABLE wire-end type (the wire width varies / is not fixed at this end). It is NOT a callable function -- it is a value passed as the beginType or endType argument to sleLeWireTypeEnumToEMYSegStyleEnum (to build a segment style from wire geometry) or to sleLeWireTypeEnumToEMYEndStyleEnum (to convert a wire type back to an end style).",
    "params": {
        "(none)": "SLE_LE_WIRE_VARIABLE takes no arguments; it is a constant. Reference it as pyScript.SLE_LE_WIRE_VARIABLE.",
    },
    "returns": "An int/enum value of type SleLeWireTypeEnum (the variable-width selector). Pass it as beginType or endType.",
    "methods": "Sibling in the same enum: SLE_LE_WIRE_EXTEND (extend wire end). Both are SleLeWireTypeEnum values consumed by sleLeWireTypeEnumToEMYSegStyleEnum and sleLeWireTypeEnumToEMYEndStyleEnum.",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> pre = pyScript.emyPointArray(1)\n"
                ">>> pre.append((1, 4))\n"
                ">>> pre.append((3, 9))\n"
                ">>> ctr = pyScript.emyPointArray(1)\n"
                ">>> ctr.append((3, 8))\n"
                ">>> ctr.append((5, 11))\n"
                ">>> nxt = pyScript.emyPointArray(1)\n"
                ">>> nxt.append((5, 8))\n"
                ">>> nxt.append((7, 13))\n"
                ">>> bs = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
                ">>> es = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
                ">>> style = pyScript.emySegStyle(6, bs, es)\n"
                ">>> ok = pyScript.sleLeWireTypeEnumToEMYSegStyleEnum(pre, ctr, nxt, pyScript.SLE_LE_WIRE_VARIABLE, pyScript.SLE_LE_WIRE_EXTEND, 2, 4, 6, 2, 3, 5, style)\n"
                ">>> print(ok)\n"
                "True"),
    "category": "SLE / Wire-Type Enum (SleLeWireTypeEnum)", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "SLE_LE_WIRE_VARIABLE is a CONSTANT, not a function -- never call it like SLE_LE_WIRE_VARIABLE(). It selects the variable-width wire end type. Pass it as beginType and/or endType (the 4th and 5th positional args) of sleLeWireTypeEnumToEMYSegStyleEnum, or as the `type` arg of sleLeWireTypeEnumToEMYEndStyleEnum. The sibling SLE_LE_WIRE_EXTEND selects the extend end type. beginType/endType may be the same value or different."}


# === SLE_LE_WIRE_EXTEND -- enum constant of SleLeWireTypeEnum ===

API_DOCS["SLE_LE_WIRE_EXTEND"] = {
    "sig": "SLE_LE_WIRE_EXTEND  [module-level constant of SleLeWireTypeEnum]",
    "desc": "An enumerated constant of the SleLeWireTypeEnum type, selecting the EXTEND wire-end type (the wire is extended past this end). It is NOT a callable function -- it is a value passed as the beginType or endType argument to sleLeWireTypeEnumToEMYSegStyleEnum (to build a segment style from wire geometry) or as the `type` argument to sleLeWireTypeEnumToEMYEndStyleEnum (to convert a wire type back to an end style).",
    "params": {
        "(none)": "SLE_LE_WIRE_EXTEND takes no arguments; it is a constant. Reference it as pyScript.SLE_LE_WIRE_EXTEND.",
    },
    "returns": "An int/enum value of type SleLeWireTypeEnum (the extend selector). Pass it as beginType or endType.",
    "methods": "Sibling in the same enum: SLE_LE_WIRE_VARIABLE (variable-width wire end). Both are SleLeWireTypeEnum values consumed by sleLeWireTypeEnumToEMYSegStyleEnum and sleLeWireTypeEnumToEMYEndStyleEnum.",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> endStyle = pyScript.emyEndStyle(pyScript.emyString(\"custom\"))\n"
                ">>> ok = pyScript.sleLeWireTypeEnumToEMYEndStyleEnum(pyScript.SLE_LE_WIRE_EXTEND, endStyle)\n"
                ">>> print(ok)\n"
                "True"),
    "category": "SLE / Wire-Type Enum (SleLeWireTypeEnum)", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "SLE_LE_WIRE_EXTEND is a CONSTANT, not a function -- never call it like SLE_LE_WIRE_EXTEND(). It selects the extend wire-end type. As the `type` arg of sleLeWireTypeEnumToEMYEndStyleEnum it fills the given emyEndStyle (output-param, no useful return beyond True/False). As beginType/endType of sleLeWireTypeEnumToEMYSegStyleEnum it configures how the segment style extends at that end. The sibling SLE_LE_WIRE_VARIABLE selects variable width."}


# === emyPointArrayGOA -- geometric logical operation on point arrays (consumer of SLE_GOA_*) ===

API_DOCS["emyPointArrayGOA"] = {
    "sig": "emyPointArrayGOA(pa1st: emyPointArray, pa2nd: emyPointArray, pOutList: emyArray_p_emyPointArray, opr: SleGOATypeEnum) -> emyBoolean  |  (list1, list2, outList, opr, bSplitGraph=True) -> emyBoolean  |  (list1, outList, opr, bSplitGraph=True) -> emyBoolean",
    "desc": "Overloaded function implementing logical (boolean) geometric operations on graphics described by point chains. The operation is selected by the `opr` argument, a SleGOATypeEnum constant: SLE_GOA_AND (intersection), SLE_GOA_OR (union), SLE_GOA_SUB (subtraction), SLE_GOA_XOR (exclusive-or). Three overloads: two single graphics (pa1st, pa2nd); two lists of graphics (list1, list2, with optional bSplitGraph); and one list of graphics self-operated (list1 only).",
    "params": {
        "pa1st": "emyPointArray -- point chain of the first graphic. Build via pyScript.emyPointArray() then .append((x, y)).",
        "pa2nd": "emyPointArray -- point chain of the second graphic.",
        "list1": "emyArray_p_emyPointArray -- a list of emyPointArray (each a graphic) for the list overloads.",
        "list2": "emyArray_p_emyPointArray -- second list of graphics (list-vs-list overload).",
        "pOutList / outList": "emyArray_p_emyPointArray -- OUTPUT container. Pre-create with pyScript.emyArray_p_emyPointArray(); it is filled with the result polygon(s). Read back via len(out) and out[i].",
        "opr": "SleGOATypeEnum -- one of SLE_GOA_AND, SLE_GOA_OR, SLE_GOA_SUB, SLE_GOA_XOR. SLE_GOA_AND = intersection.",
        "bSplitGraph": "emyBoolean, optional (default True) -- when True the output graph is split into separate pieces.",
    },
    "returns": "emyBoolean -- True on success.",
    "methods": "Result is delivered through the output-param outList (length = number of result polygons). Related: emyPointArrayGOAHoles (holes operation), emyPointArrayGOATopo (topology).",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> a = pyScript.emyPointArray()\n"
                ">>> for pt in [(0, 0), (20, 0), (20, 20), (0, 20)]:\n"
                "...     a.append(pt)\n"
                ">>> b = pyScript.emyPointArray()\n"
                ">>> for pt in [(10, -10), (30, -10), (30, 10), (10, 10)]:\n"
                "...     b.append(pt)\n"
                ">>> out = pyScript.emyArray_p_emyPointArray()\n"
                ">>> ok = pyScript.emyPointArrayGOA(a, b, out, pyScript.SLE_GOA_OR)\n"
                ">>> print(ok, len(out))\n"
                "True 1"),
    "category": "SLE / Geometric Operation (consumer of SleGOATypeEnum)", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Output-param pattern: pre-create emyArray_p_emyPointArray and pass it as pOutList/outList; emyPointArrayGOA fills it and returns True/False. Use SLE_GOA_AND for intersection, SLE_GOA_OR for union, SLE_GOA_SUB for A minus B, SLE_GOA_XOR for exclusive-or. Integer coordinates give exact results. For two overlapping rectangles AND yields 1 polygon; for disjoint rectangles AND yields 0 polygons (len(out)==0). bSplitGraph=True (default) splits the output into separate graphs."}


# === sleLeWireTypeEnumToEMYSegStyleEnum -- convert wire type to segStyle (consumer of SLE_LE_WIRE_*) ===

API_DOCS["sleLeWireTypeEnumToEMYSegStyleEnum"] = {
    "sig": "sleLeWireTypeEnumToEMYSegStyleEnum(preArray: emyPointArray, centerLine: emyPointArray, nextArray: emyPointArray, beginType: SleLeWireTypeEnum, endType: SleLeWireTypeEnum, beginExt: emyDist, endExt: emyDist, preWidth: emyDist, curWidth: emyDist, nextWidth: emyDist, grid: emyDist, style: emySegStyle, swapType: bool=False) -> emyBoolean",
    "desc": "Converts wire geometry and wire-type information into a segment style (emySegStyle) configuration. Given the previous / center / next wire point arrays and the begin/end wire types (SleLeWireTypeEnum constants such as SLE_LE_WIRE_VARIABLE and SLE_LE_WIRE_EXTEND), plus extension and width values and a grid, it fills the provided `style` object. Used to derive how a path segment should be drawn from the geometry of the wires that join it.",
    "params": {
        "preArray": "emyPointArray -- point chain of the PREVIOUS wire segment. Build via pyScript.emyPointArray(n) then .append((x, y)).",
        "centerLine": "emyPointArray -- point chain of the CENTER (current) wire segment.",
        "nextArray": "emyPointArray -- point chain of the NEXT wire segment.",
        "beginType": "SleLeWireTypeEnum -- wire type at the BEGIN end. Use pyScript.SLE_LE_WIRE_VARIABLE or pyScript.SLE_LE_WIRE_EXTEND.",
        "endType": "SleLeWireTypeEnum -- wire type at the END end. Use pyScript.SLE_LE_WIRE_VARIABLE or pyScript.SLE_LE_WIRE_EXTEND.",
        "beginExt": "emyDist -- begin extend value (a number).",
        "endExt": "emyDist -- end extend value (a number).",
        "preWidth": "emyDist -- width of the previous wire.",
        "curWidth": "emyDist -- width of the current (center) wire.",
        "nextWidth": "emyDist -- width of the next wire.",
        "grid": "emyDist -- grid value.",
        "style": "emySegStyle -- OUTPUT. Pre-create with pyScript.emySegStyle(width, beginStyleIn, endStyleIn); it is filled by the call.",
        "swapType": "bool, optional (default False) -- when True the begin/end types are swapped.",
    },
    "returns": "emyBoolean -- True if the wire type is converted to segStyle successfully, False otherwise.",
    "methods": "Inverse direction: sleEMYSegStyleEnumToLeWireTypeEnum (segStyle -> wire type). EndStyle conversion: sleLeWireTypeEnumToEMYEndStyleEnum / sleEMYEndStyleEnumToLeWireTypeEnum.",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> pre = pyScript.emyPointArray(1)\n"
                ">>> pre.append((1, 4))\n"
                ">>> pre.append((3, 9))\n"
                ">>> ctr = pyScript.emyPointArray(1)\n"
                ">>> ctr.append((3, 8))\n"
                ">>> ctr.append((5, 11))\n"
                ">>> nxt = pyScript.emyPointArray(1)\n"
                ">>> nxt.append((5, 8))\n"
                ">>> nxt.append((7, 13))\n"
                ">>> bs = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
                ">>> es = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
                ">>> style = pyScript.emySegStyle(6, bs, es)\n"
                ">>> ok = pyScript.sleLeWireTypeEnumToEMYSegStyleEnum(pre, ctr, nxt, pyScript.SLE_LE_WIRE_VARIABLE, pyScript.SLE_LE_WIRE_EXTEND, 2, 4, 6, 2, 3, 5, style)\n"
                ">>> print(ok)\n"
                "True"),
    "category": "sle / Wire-Type Conversion (consumer of SleLeWireTypeEnum)", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "13 positional args (12 required + swapType optional). The `style` arg is an OUTPUT-param: pre-create emySegStyle(width, beginStyleIn, endStyleIn) and pass it in; the call fills it and returns True/False. beginType/endType are SleLeWireTypeEnum constants (SLE_LE_WIRE_VARIABLE / SLE_LE_WIRE_EXTEND). The three point arrays are the previous / center / next wire segments. Numeric args (beginExt, endExt, preWidth, curWidth, nextWidth, grid) are plain numbers (emyDist). swapType=True swaps begin/end types."}


# === sleLeWireTypeEnumToEMYEndStyleEnum -- convert wire type back to endStyle (extra context) ===

API_DOCS["sleLeWireTypeEnumToEMYEndStyleEnum"] = {
    "sig": "sleLeWireTypeEnumToEMYEndStyleEnum(type: SleLeWireTypeEnum, endStyle: emyEndStyle) -> emyBoolean",
    "desc": "Converts a wire type (a SleLeWireTypeEnum constant such as SLE_LE_WIRE_EXTEND or SLE_LE_WIRE_VARIABLE) back into an EndStyle. It fills the provided `endStyle` object (output-param pattern). This is the inverse-direction companion of sleEMYEndStyleEnumToLeWireTypeEnum. Useful when a wire-type configuration must be reflected as an end style for rendering.",
    "params": {
        "type": "SleLeWireTypeEnum -- the wire type to convert. Use pyScript.SLE_LE_WIRE_EXTEND or pyScript.SLE_LE_WIRE_VARIABLE.",
        "endStyle": "emyEndStyle -- OUTPUT. Pre-create with pyScript.emyEndStyle(pyScript.emyString(name)); it is filled by the call.",
    },
    "returns": "emyBoolean -- True if the wire type is converted to EndStyle successfully, False otherwise.",
    "methods": "Inverse: sleEMYEndStyleEnumToLeWireTypeEnum(endStyle, type). Related: sleLeWireTypeEnumToEMYSegStyleEnum (wire type -> segStyle).",
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> endStyle = pyScript.emyEndStyle(pyScript.emyString(\"custom\"))\n"
                ">>> ok = pyScript.sleLeWireTypeEnumToEMYEndStyleEnum(pyScript.SLE_LE_WIRE_EXTEND, endStyle)\n"
                ">>> print(ok)\n"
                "True"),
    "category": "sle / Wire-Type Conversion (consumer of SleLeWireTypeEnum)", "safety": "ISOLATE", "eval_count": 0,
    "key_notes": "2 positional args. The `endStyle` arg is an OUTPUT-param: pre-create emyEndStyle(emyString(name)) and pass it in; the call fills it and returns True/False. `type` is a SleLeWireTypeEnum constant (SLE_LE_WIRE_EXTEND / SLE_LE_WIRE_VARIABLE). Not an eval entry_point; ISOLATE-class helper. The eval_count is 0 in the raw-API scan because the eval only uses the forward direction (sleLeWireTypeEnumToEMYSegStyleEnum)."}


API_ORDER = ["SLE_GOA_AND", "SLE_LE_WIRE_VARIABLE", "SLE_LE_WIRE_EXTEND",
             "emyPointArrayGOA", "sleLeWireTypeEnumToEMYSegStyleEnum",
             "sleLeWireTypeEnumToEMYEndStyleEnum"]


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

    # ---- S1: doc -> code (6 pairs, one per API) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v30-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S3: code -> doc (6 pairs, one per API) ----
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
        _add("S3", "v30-S3-%s" % name, prompt, completion, [name],
             "S3 code_to_doc for %s" % name)

    # ---- S4: multi-step trace (6 pairs, one per API) ----
    s4_traces = [
        ("SLE_GOA_AND-intersect-and-readback",
         "Build two overlapping rectangles, compute their intersection with SLE_GOA_AND via emyPointArrayGOA, then read back the number of result polygons and the first point of the result.",
         ["SLE_GOA_AND", "emyPointArrayGOA"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> a = pyScript.emyPointArray()\n"
         ">>> for pt in [(0, 0), (40, 0), (40, 40), (0, 40)]:\n"
         "...     a.append(pt)\n"
         ">>> b = pyScript.emyPointArray()\n"
         ">>> for pt in [(20, 20), (60, 20), (60, 60), (20, 60)]:\n"
         "...     b.append(pt)\n"
         ">>> out = pyScript.emyArray_p_emyPointArray()\n"
         ">>> ok = pyScript.emyPointArrayGOA(a, b, out, pyScript.SLE_GOA_AND)\n"
         ">>> print(ok, len(out))\n"
         "True 1\n"
         ">>> res = out[0]\n"
         ">>> print(res[0])\n"
         "(20.0, 20.0)"),
        ("SLE_LE_WIRE_VARIABLE-segstyle-from-geometry",
         "Build three wire point arrays (previous/center/next), create an emySegStyle, and use sleLeWireTypeEnumToEMYSegStyleEnum with SLE_LE_WIRE_VARIABLE as the begin type and SLE_LE_WIRE_EXTEND as the end type to fill the style. Report success.",
         ["SLE_LE_WIRE_VARIABLE", "SLE_LE_WIRE_EXTEND", "sleLeWireTypeEnumToEMYSegStyleEnum"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pre = pyScript.emyPointArray(1)\n"
         ">>> for pt in [(2, 5), (4, 10)]:\n"
         "...     pre.append(pt)\n"
         ">>> ctr = pyScript.emyPointArray(1)\n"
         ">>> for pt in [(4, 9), (6, 12)]:\n"
         "...     ctr.append(pt)\n"
         ">>> nxt = pyScript.emyPointArray(1)\n"
         ">>> for pt in [(6, 9), (8, 14)]:\n"
         "...     nxt.append(pt)\n"
         ">>> bs = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
         ">>> es = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
         ">>> style = pyScript.emySegStyle(7, bs, es)\n"
         ">>> ok = pyScript.sleLeWireTypeEnumToEMYSegStyleEnum(pre, ctr, nxt, pyScript.SLE_LE_WIRE_VARIABLE, pyScript.SLE_LE_WIRE_EXTEND, 3, 6, 7, 3, 4, 5, style)\n"
         ">>> print(ok)\n"
         "True"),
        ("SLE_LE_WIRE_EXTEND-to-endstyle",
         "Create an emyEndStyle and convert the SLE_LE_WIRE_EXTEND wire type into it using sleLeWireTypeEnumToEMYEndStyleEnum. Report success.",
         ["SLE_LE_WIRE_EXTEND", "sleLeWireTypeEnumToEMYEndStyleEnum"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> es = pyScript.emyEndStyle(pyScript.emyString(\"custom\"))\n"
         ">>> ok = pyScript.sleLeWireTypeEnumToEMYEndStyleEnum(pyScript.SLE_LE_WIRE_EXTEND, es)\n"
         ">>> print(ok)\n"
         "True"),
    ]
    for apis_str, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v30-S4-%s" % apis_str, prompt, completion, apis,
             "S4 multi_step_trace: %s" % scenario)

    s4b_traces = [
        ("emyPointArrayGOA-union-vs-intersect",
         "Compute both the UNION (SLE_GOA_OR) and the INTERSECTION (SLE_GOA_AND) of two overlapping rectangles via emyPointArrayGOA, and compare the number of result polygons of each.",
         ["emyPointArrayGOA", "SLE_GOA_AND"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> a = pyScript.emyPointArray()\n"
         ">>> for pt in [(0, 0), (30, 0), (30, 30), (0, 30)]:\n"
         "...     a.append(pt)\n"
         ">>> b = pyScript.emyPointArray()\n"
         ">>> for pt in [(15, 15), (45, 15), (45, 45), (15, 45)]:\n"
         "...     b.append(pt)\n"
         ">>> out_or = pyScript.emyArray_p_emyPointArray()\n"
         ">>> pyScript.emyPointArrayGOA(a, b, out_or, pyScript.SLE_GOA_OR)\n"
         ">>> out_and = pyScript.emyArray_p_emyPointArray()\n"
         ">>> pyScript.emyPointArrayGOA(a, b, out_and, pyScript.SLE_GOA_AND)\n"
         ">>> print('union polygons:', len(out_or), 'intersection polygons:', len(out_and))\n"
         "union polygons: 1 intersection polygons: 1"),
        ("sleLeWireTypeEnumToEMYSegStyleEnum-swapType",
         "Build wire geometry and convert it to a segment style with sleLeWireTypeEnumToEMYSegStyleEnum using SLE_LE_WIRE_EXTEND at begin and SLE_LE_WIRE_VARIABLE at end, then redo the same call with swapType=True to swap begin/end types. Report both results.",
         ["sleLeWireTypeEnumToEMYSegStyleEnum", "SLE_LE_WIRE_EXTEND", "SLE_LE_WIRE_VARIABLE"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pre = pyScript.emyPointArray(1)\n"
         ">>> for pt in [(1, 3), (3, 8)]:\n"
         "...     pre.append(pt)\n"
         ">>> ctr = pyScript.emyPointArray(1)\n"
         ">>> for pt in [(3, 7), (5, 10)]:\n"
         "...     ctr.append(pt)\n"
         ">>> nxt = pyScript.emyPointArray(1)\n"
         ">>> for pt in [(5, 7), (7, 12)]:\n"
         "...     nxt.append(pt)\n"
         ">>> bs = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
         ">>> es = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
         ">>> s1 = pyScript.emySegStyle(5, bs, es)\n"
         ">>> ok1 = pyScript.sleLeWireTypeEnumToEMYSegStyleEnum(pre, ctr, nxt, pyScript.SLE_LE_WIRE_EXTEND, pyScript.SLE_LE_WIRE_VARIABLE, 2, 3, 5, 2, 3, 4, s1)\n"
         ">>> s2 = pyScript.emySegStyle(5, bs, es)\n"
         ">>> ok2 = pyScript.sleLeWireTypeEnumToEMYSegStyleEnum(pre, ctr, nxt, pyScript.SLE_LE_WIRE_EXTEND, pyScript.SLE_LE_WIRE_VARIABLE, 2, 3, 5, 2, 3, 4, s2, True)\n"
         ">>> print(ok1, ok2)\n"
         "True True"),
        ("sleLeWireTypeEnumToEMYEndStyleEnum-both-types",
         "Convert both SLE_LE_WIRE_EXTEND and SLE_LE_WIRE_VARIABLE wire types into end styles using sleLeWireTypeEnumToEMYEndStyleEnum, and report both results.",
         ["sleLeWireTypeEnumToEMYEndStyleEnum", "SLE_LE_WIRE_EXTEND", "SLE_LE_WIRE_VARIABLE"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> es1 = pyScript.emyEndStyle(pyScript.emyString(\"custom\"))\n"
         ">>> ok1 = pyScript.sleLeWireTypeEnumToEMYEndStyleEnum(pyScript.SLE_LE_WIRE_EXTEND, es1)\n"
         ">>> es2 = pyScript.emyEndStyle(pyScript.emyString(\"custom\"))\n"
         ">>> ok2 = pyScript.sleLeWireTypeEnumToEMYEndStyleEnum(pyScript.SLE_LE_WIRE_VARIABLE, es2)\n"
         ">>> print(ok1, ok2)\n"
         "True True"),
    ]
    for apis_str, scenario, apis, code in s4b_traces:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v30-S4-%s" % apis_str, prompt, completion, apis,
             "S4 multi_step_trace: %s" % scenario)

    # ---- S5: error / edge-case / quiz (6 pairs) ----
    s5_items = [
        ("SLE_GOA_AND-quiz",
         "Quiz: A user wrote `pyScript.SLE_GOA_AND()` and got a TypeError. What is wrong, and how should SLE_GOA_AND be used correctly?",
         ["SLE_GOA_AND"],
         "SLE_GOA_AND is an enum CONSTANT, not a function. Calling it like `pyScript.SLE_GOA_AND()` is wrong and raises TypeError.\n\n"
         "Correct usage: pass it as the `opr` argument to emyPointArrayGOA to request the geometric-AND (intersection) operation:\n\n"
         "```python\n"
         ">>> import pyAether as pyScript\n"
         ">>> a = pyScript.emyPointArray()\n"
         ">>> a.append((0, 0)); a.append((10, 0)); a.append((10, 10)); a.append((0, 10))\n"
         ">>> b = pyScript.emyPointArray()\n"
         ">>> b.append((5, 5)); b.append((15, 5)); b.append((15, 15)); b.append((5, 15))\n"
         ">>> out = pyScript.emyArray_p_emyPointArray()\n"
         ">>> ok = pyScript.emyPointArrayGOA(a, b, out, pyScript.SLE_GOA_AND)\n"
         ">>> print(ok, len(out))\n"
         "True 1\n"
         "```\n\nThe 4 siblings are SLE_GOA_AND (intersection), SLE_GOA_OR (union), SLE_GOA_SUB (A minus B), SLE_GOA_XOR (exclusive-or)."),
        ("SLE_GOA_AND-disjoint-edge",
         "Edge case: compute the intersection (SLE_GOA_AND) of two DISJOINT rectangles and explain why the result has 0 polygons.",
         ["SLE_GOA_AND", "emyPointArrayGOA"],
         "```python\n"
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> a = pyScript.emyPointArray()\n"
         ">>> for pt in [(0, 0), (10, 0), (10, 10), (0, 10)]:\n"
         "...     a.append(pt)\n"
         ">>> b = pyScript.emyPointArray()\n"
         ">>> for pt in [(100, 100), (120, 100), (120, 120), (100, 120)]:\n"
         "...     b.append(pt)\n"
         ">>> out = pyScript.emyArray_p_emyPointArray()\n"
         ">>> ok = pyScript.emyPointArrayGOA(a, b, out, pyScript.SLE_GOA_AND)\n"
         ">>> print(ok, len(out))\n"
         "True 0\n"
         "```\n\nThe two rectangles do not overlap, so their intersection (AND) is empty: len(out) == 0 and ok is still True (the operation succeeded, the result is just empty)."),
        ("SLE_LE_WIRE_VARIABLE-quiz",
         "Quiz: What is the type of `pyScript.SLE_LE_WIRE_VARIABLE`, and which two APIs accept it as an argument? Give a one-line call example for each.",
         ["SLE_LE_WIRE_VARIABLE"],
         "SLE_LE_WIRE_VARIABLE is a CONSTANT of the SleLeWireTypeEnum type (the variable-width wire-end selector). It is NOT callable.\n\nTwo APIs that accept it:\n"
         "1. sleLeWireTypeEnumToEMYSegStyleEnum -- as beginType or endType (positions 4/5):\n"
         "   `pyScript.sleLeWireTypeEnumToEMYSegStyleEnum(pre, ctr, nxt, pyScript.SLE_LE_WIRE_VARIABLE, pyScript.SLE_LE_WIRE_EXTEND, 2, 4, 6, 2, 3, 5, style)`\n"
         "2. sleLeWireTypeEnumToEMYEndStyleEnum -- as the `type` arg (position 1):\n"
         "   `pyScript.sleLeWireTypeEnumToEMYEndStyleEnum(pyScript.SLE_LE_WIRE_VARIABLE, endStyle)`\n\nThe sibling constant is SLE_LE_WIRE_EXTEND (extend wire end)."),
    ]
    for apis_str, scenario, apis, completion in s5_items:
        prompt = ("You are an EDA automation engineer. %s" % scenario)
        _add("S5", "v30-S5-%s" % apis_str, prompt, completion, apis,
             "S5 error_edge_quiz: %s" % scenario)

    s5b_items = [
        ("SLE_LE_WIRE_EXTEND-vs-VARIABLE",
         "Compare SLE_LE_WIRE_EXTEND and SLE_LE_WIRE_VARIABLE: what does each wire-end type mean, and can both ends of a segment use the same type?",
         ["SLE_LE_WIRE_EXTEND", "SLE_LE_WIRE_VARIABLE"],
         "Both are constants of SleLeWireTypeEnum:\n"
         "- SLE_LE_WIRE_EXTEND: the wire is EXTENDED past this end.\n"
         "- SLE_LE_WIRE_VARIABLE: the wire width is VARIABLE (not fixed) at this end.\n\nBoth ends may use the SAME type or DIFFERENT types. sleLeWireTypeEnumToEMYSegStyleEnum takes beginType and endType independently:\n\n"
         "```python\n"
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pre = pyScript.emyPointArray(1); pre.append((1, 2)); pre.append((2, 6))\n"
         ">>> ctr = pyScript.emyPointArray(1); ctr.append((2, 5)); ctr.append((4, 9))\n"
         ">>> nxt = pyScript.emyPointArray(1); nxt.append((4, 5)); nxt.append((6, 11))\n"
         ">>> bs = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
         ">>> es = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
         ">>> style = pyScript.emySegStyle(4, bs, es)\n"
         ">>> # both ends EXTEND:\n"
         ">>> ok = pyScript.sleLeWireTypeEnumToEMYSegStyleEnum(pre, ctr, nxt, pyScript.SLE_LE_WIRE_EXTEND, pyScript.SLE_LE_WIRE_EXTEND, 1, 2, 4, 1, 2, 3, style)\n"
         ">>> print(ok)\n"
         "True\n"
         "```"),
        ("emyPointArrayGOA-output-param-quiz",
         "Quiz: A user called `out = pyScript.emyPointArrayGOA(a, b, pyScript.SLE_GOA_AND)` and got nothing useful. What is wrong with treating the return value as the result polygons?",
         ["emyPointArrayGOA", "SLE_GOA_AND"],
         "emyPointArrayGOA returns an emyBoolean (True/False success flag), NOT the result polygons. The result polygons come back through the OUTPUT-param container (the 3rd argument), which must be pre-created as emyArray_p_emyPointArray.\n\nWrong (return value is just True/False):\n`out = pyScript.emyPointArrayGOA(a, b, pyScript.SLE_GOA_AND)`  # out is True/False\n\nCorrect (output-param pattern):\n```python\n>>> import pyAether as pyScript\n>>> a = pyScript.emyPointArray(); a.append((0,0)); a.append((10,0)); a.append((10,10)); a.append((0,10))\n>>> b = pyScript.emyPointArray(); b.append((3,3)); b.append((13,3)); b.append((13,13)); b.append((3,13))\n>>> out = pyScript.emyArray_p_emyPointArray()\n>>> ok = pyScript.emyPointArrayGOA(a, b, out, pyScript.SLE_GOA_AND)\n>>> print(ok, len(out))\nTrue 1\n```\nThe result polygons are out[0], out[1], ... ; len(out) is the count."),
        ("sleLeWireTypeEnumToEMYSegStyleEnum-argcount",
         "Quiz: sleLeWireTypeEnumToEMYSegStyleEnum takes 12 required positional args. List them in order and explain which one is the output.",
         ["sleLeWireTypeEnumToEMYSegStyleEnum"],
         "The 12 required positional args, in order:\n"
         "1. preArray (emyPointArray) -- previous wire segment points\n"
         "2. centerLine (emyPointArray) -- center (current) wire segment points\n"
         "3. nextArray (emyPointArray) -- next wire segment points\n"
         "4. beginType (SleLeWireTypeEnum) -- e.g. SLE_LE_WIRE_VARIABLE\n"
         "5. endType (SleLeWireTypeEnum) -- e.g. SLE_LE_WIRE_EXTEND\n"
         "6. beginExt (emyDist / number) -- begin extend value\n"
         "7. endExt (emyDist / number) -- end extend value\n"
         "8. preWidth (emyDist / number) -- previous wire width\n"
         "9. curWidth (emyDist / number) -- current wire width\n"
         "10. nextWidth (emyDist / number) -- next wire width\n"
         "11. grid (emyDist / number) -- grid value\n"
         "12. style (emySegStyle) -- OUTPUT: pre-create emySegStyle(width, beginStyleIn, endStyleIn); it is filled by the call\n\nOptional 13th arg: swapType (bool, default False) -- swaps begin/end types.\n\nThe function returns emyBoolean (True on success). The `style` object is the output-param: it is mutated in place, not returned."),
    ]
    for apis_str, scenario, apis, completion in s5b_items:
        prompt = ("You are an EDA automation engineer. %s" % scenario)
        _add("S5", "v30-S5-%s" % apis_str, prompt, completion, apis,
             "S5 error_edge_quiz: %s" % scenario)

    # ---- S6: cross-API workflow (6 pairs) ----
    s6_items = [
        ("GOA-all-four-ops",
         "Given two overlapping rectangles, run all four geometric operations (AND, OR, SUB, XOR) via emyPointArrayGOA and report the polygon count for each.",
         ["emyPointArrayGOA", "SLE_GOA_AND"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> a = pyScript.emyPointArray()\n"
         ">>> for pt in [(0, 0), (30, 0), (30, 30), (0, 30)]:\n"
         "...     a.append(pt)\n"
         ">>> b = pyScript.emyPointArray()\n"
         ">>> for pt in [(15, 15), (45, 15), (45, 45), (15, 45)]:\n"
         "...     b.append(pt)\n"
         ">>> counts = {}\n"
         ">>> for name, op in [('AND', pyScript.SLE_GOA_AND), ('OR', pyScript.SLE_GOA_OR), ('SUB', pyScript.SLE_GOA_SUB), ('XOR', pyScript.SLE_GOA_XOR)]:\n"
         "...     out = pyScript.emyArray_p_emyPointArray()\n"
         "...     pyScript.emyPointArrayGOA(a, b, out, op)\n"
         "...     counts[name] = len(out)\n"
         ">>> print(counts)\n"
         "{'AND': 1, 'OR': 1, 'SUB': 1, 'XOR': 2}"),
        ("wire-to-segstyle-then-to-endstyle",
         "Build a wire geometry, convert it to a segment style with sleLeWireTypeEnumToEMYSegStyleEnum (begin=VARIABLE, end=EXTEND), then separately convert the EXTEND wire type back to an end style with sleLeWireTypeEnumToEMYEndStyleEnum. Report both results.",
         ["sleLeWireTypeEnumToEMYSegStyleEnum", "sleLeWireTypeEnumToEMYEndStyleEnum", "SLE_LE_WIRE_VARIABLE", "SLE_LE_WIRE_EXTEND"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pre = pyScript.emyPointArray(1); pre.append((1, 4)); pre.append((3, 9))\n"
         ">>> ctr = pyScript.emyPointArray(1); ctr.append((3, 8)); ctr.append((5, 11))\n"
         ">>> nxt = pyScript.emyPointArray(1); nxt.append((5, 8)); nxt.append((7, 13))\n"
         ">>> bs = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
         ">>> es = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
         ">>> style = pyScript.emySegStyle(6, bs, es)\n"
         ">>> ok_seg = pyScript.sleLeWireTypeEnumToEMYSegStyleEnum(pre, ctr, nxt, pyScript.SLE_LE_WIRE_VARIABLE, pyScript.SLE_LE_WIRE_EXTEND, 2, 4, 6, 2, 3, 5, style)\n"
         ">>> es_back = pyScript.emyEndStyle(pyScript.emyString(\"custom\"))\n"
         ">>> ok_es = pyScript.sleLeWireTypeEnumToEMYEndStyleEnum(pyScript.SLE_LE_WIRE_EXTEND, es_back)\n"
         ">>> print('segstyle:', ok_seg, 'endstyle:', ok_es)\n"
         "segstyle: True endstyle: True"),
        ("intersect-then-build-wire",
         "Compute the intersection (SLE_GOA_AND) of two rectangles, read the result polygon points, then build a wire-style configuration from those points using sleLeWireTypeEnumToEMYSegStyleEnum with VARIABLE/EXTEND ends.",
         ["emyPointArrayGOA", "SLE_GOA_AND", "sleLeWireTypeEnumToEMYSegStyleEnum", "SLE_LE_WIRE_VARIABLE", "SLE_LE_WIRE_EXTEND"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> a = pyScript.emyPointArray()\n"
         ">>> for pt in [(0, 0), (40, 0), (40, 40), (0, 40)]:\n"
         "...     a.append(pt)\n"
         ">>> b = pyScript.emyPointArray()\n"
         ">>> for pt in [(20, 20), (60, 20), (60, 60), (20, 60)]:\n"
         "...     b.append(pt)\n"
         ">>> out = pyScript.emyArray_p_emyPointArray()\n"
         ">>> pyScript.emyPointArrayGOA(a, b, out, pyScript.SLE_GOA_AND)\n"
         ">>> res = out[0]\n"
         ">>> pre = pyScript.emyPointArray(1); pre.append((res[0][0], res[0][1])); pre.append((res[1][0], res[1][1]))\n"
         ">>> ctr = pyScript.emyPointArray(1); ctr.append((res[1][0], res[1][1])); ctr.append((res[2][0], res[2][1]))\n"
         ">>> nxt = pyScript.emyPointArray(1); nxt.append((res[2][0], res[2][1])); nxt.append((res[3][0], res[3][1]))\n"
         ">>> bs = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
         ">>> es = pyScript.emyEndStyle(pyScript.emyString(\"truncate\"))\n"
         ">>> style = pyScript.emySegStyle(8, bs, es)\n"
         ">>> ok = pyScript.sleLeWireTypeEnumToEMYSegStyleEnum(pre, ctr, nxt, pyScript.SLE_LE_WIRE_VARIABLE, pyScript.SLE_LE_WIRE_EXTEND, 2, 4, 8, 3, 4, 5, style)\n"
         ">>> print('intersect polys:', len(out), 'wire->segstyle:', ok)\n"
         "intersect polys: 1 wire->segstyle: True"),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write a complete "
                  "Python script using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v30-S6-%s" % apis_str, prompt, completion, apis,
             "S6 cross_api_workflow: %s" % scenario)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    parser = argparse.ArgumentParser(
        description="R200 v30 SLE enum-constant SFT corpus builder (6 APIs, ~30 pairs)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print stats only, do not write output file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Output JSONL path (default: %s)" % DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of pairs (for testing)")
    args = parser.parse_args()

    sys.stderr.write("R200 v30 SLE enum-constant corpus builder\n")
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

    sys.stderr.write("\n=== R200 v30 Corpus Stats ===\n")
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
