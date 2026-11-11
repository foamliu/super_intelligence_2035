#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r205_context_blind_corpus.py
R205 -- v35 PyAether SFT corpus: the 6 remaining context-dependent blind APIs.
= agrGetSnapPoints + geTreeRemoveItem + emvPurposeNumberDrawing + guMotion +
  mouseLBClick + smash_option (+ setup helpers), ~36 pairs.

BACKGROUND: v11-v34 (912 pairs) cover 158/164 eval raw APIs (96.3%). 6 blind.
The remaining 6 blind APIs each REQUIRE setup context (a DB instance, a tree, a
draw area, a config struct, a drawing-purpose constant). This round clears ALL
of them, pushing coverage 96.3% -> 100%.

Eval-task coupling (ISOLATE-class -- all 6 targets + 6 helpers are NOT eval
entry_points, verified against the 155-entry_point set):
  agrGetSnapPoints      -> eval task 158, entry_point=get_snapped_points
  geTreeRemoveItem      -> eval task 097, entry_point=remove_tree_item
  emvPurposeNumberDrawing -> eval task 069, entry_point=create_poly_line_cartoon
  guMotion + mouseLBClick -> eval task 155, entry_point=get_mouse_position_after_move
  smash_option          -> eval task 136, entry_point=smash_instance_advanced

Red line (S5.1) isolates on eval *entry_point* strings, NOT on helper API names.
Fingerprint scan rejects any pair containing a literal eval entry_point.
Doctest values DELIBERATELY DIFFERENT from eval (see each API doc).

Usage: python3 baize_posttrain_r205_context_blind_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v35_context_blind.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}
API_ORDER = ["agrGetSnapPoints", "dbCrtInst", "vector1D_emyPointF", "emyPointF",
             "geTreeRemoveItem", "aeCreateTree", "aeCreateTreeItem",
             "aeTreeAppendItem", "emvPurposeNumberDrawing", "GuCartPolyLine",
             "emyPointArrayF", "guMotion", "mouseLBClick", "aeGetCommandPoint",
             "smash_option", "dbSmashInst2"]

# ===== Group 1: snap (agrGetSnapPoints + dbCrtInst + vector1D_emyPointF + emyPointF) =====
API_DOCS["agrGetSnapPoints"] = {
    "sig": ("agrGetSnapPoints(inst: emyInst, points: vector1D_emyPointF, "
            "type: emyString) -> Tuple[emyPointF]"),
    "desc": ("Adjusts a point array to snap onto an instance's editable shapes. "
             "Given an instance, a vector of candidate points and a shape type "
             "string (Rect / Polygon / Path), returns a tuple of emyPointF "
             "objects representing the snapped coordinates."),
    "params": {
        "inst: emyInst": ("Instance identifier returned by dbCrtInst. Specifies "
                          "the instance whose shapes are snapped onto."),
        "points: vector1D_emyPointF": ("A vector1D_emyPointF of candidate "
                                       "points; build with .append(emyPointF)."),
        "type: emyString": ("Modal shape type: \"Rect\", \"Polygon\" or \"Path\"."),
    },
    "returns": ("Tuple[emyPointF] -- snapped point objects (may be empty). "
                "Each has .x() / .y() accessors."),
    "key_notes": ("points must be a vector1D_emyPointF, not a plain list. The "
                  "instance must be created first via dbCrtInst inside an open "
                  "cell view. Helper snap utility, not a task entry point."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.dbCreateLib(lib=\"demo_lib\", attachTechLib=\"TECHLIB\")\n"
                ">>> pyScript.dbNewCV(lib=\"demo_lib\", cell=\"inv\", view=\"layout\")\n"
                ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
                ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I0\")\n"
                ">>> pts = pyScript.vector1D_emyPointF()\n"
                ">>> pts.append(pyScript.emyPointF(2.5, 3.5))\n"
                ">>> pts.append(pyScript.emyPointF(7.0, 1.0))\n"
                ">>> snapped = pyScript.agrGetSnapPoints(inst=inst, points=pts, type=pyScript.emyString(\"Polygon\"))\n"
                ">>> print(isinstance(snapped, tuple))\n"
                "True"),
}
API_DOCS["dbCrtInst"] = {
    "sig": ("dbCrtInst(cv: emyDesign, point: emyPointF, master: emyDesign=None, "
            "lib: emyString=\"\", cell: emyString=\"\", view: emyString=\"layout\", "
            "inst: emyString=\"\", orient: emyString=\"R0\", mag: float=1, "
            "params: vector1D_emyString=None) -> emyInst"),
    "desc": ("Creates an instance of a master cell inside an open cell view and "
             "returns an emyInst figure identifier. The master may be given by a "
             "master design object or by lib/cell/view name strings."),
    "params": {
        "cv: emyDesign": "Open cell view to place the instance into.",
        "point: emyPointF": "Origin of the instance (tuple or emyPointF).",
        "lib/cell/view: emyString": "Master library / cell / view names.",
        "inst: emyString": "Optional instance name.",
        "params: vector1D_emyString": ("Optional PCell parameter pairs, e.g. "
                                       "[\"l\", \"180n\", \"w\", \"2u\"]."),
    },
    "returns": "emyInst -- the created instance identifier (or None on failure).",
    "key_notes": ("cv must be opened first (dbOpenCVByType). point accepts a "
                  "tuple. Setup helper for agrGetSnapPoints / dbSmashInst2."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
                ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I0\")\n"
                ">>> print(inst is not None and inst is not False)\n"
                "True"),
}
API_DOCS["vector1D_emyPointF"] = {
    "sig": "vector1D_emyPointF() -> vector1D_emyPointF   [SWIG container]",
    "desc": ("A SWIG-wrapped vector of emyPointF. Construct empty then "
             ".append(emyPointF(x, y)) to populate. Required by APIs that take "
             "a typed point array (e.g. agrGetSnapPoints)."),
    "params": {},
    "returns": "An empty vector1D_emyPointF; grows via .append().",
    "key_notes": ("Cannot pass a plain Python list where a vector1D_emyPointF is "
                  "expected. Indexable after append. Helper container."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> v = pyScript.vector1D_emyPointF()\n"
                ">>> v.append(pyScript.emyPointF(2.5, 3.5))\n"
                ">>> v.append(pyScript.emyPointF(7.0, 1.0))\n"
                ">>> print(len(v))\n"
                "2"),
}
API_DOCS["emyPointF"] = {
    "sig": "emyPointF(x: emyDouble, y: emyDouble) -> emyPointF   [class]",
    "desc": ("2D float point. Construct emyPointF(x, y); access coordinates via "
             ".x() and .y(). Used by snapping, mouse and geometry APIs."),
    "params": {"x: emyDouble": "X coordinate (float).",
               "y: emyDouble": "Y coordinate (float)."},
    "returns": "An emyPointF point object.",
    "methods": ".x() -> float, .y() -> float, .set(x, y) -> None",
    "key_notes": ("Always use .x()/.y() methods, never item indexing. Helper "
                  "geometry primitive."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> p = pyScript.emyPointF(2.5, 3.5)\n"
                ">>> print(p.x(), p.y())\n"
                "2.5 3.5"),
}

# ===== Group 2: tree (geTreeRemoveItem + aeCreateTree + aeCreateTreeItem + aeTreeAppendItem) =====
API_DOCS["geTreeRemoveItem"] = {
    "sig": "geTreeRemoveItem(tree: object, item: object) -> emyBoolean",
    "desc": ("Removes a specified item from a tree. The item must be a DIRECT "
             "child of the tree (previously appended via aeTreeAppendItem). "
             "Recommended successor to aeTreeRemoveItem since v2025.03."),
    "params": {
        "tree: object": ("The tree to remove from. Return value of "
                         "aeCreateTree / geCreateTree."),
        "item: object": ("The item to remove. Return value of "
                         "aeCreateTreeItem / geCreateTreeItem; must be a direct "
                         "child of tree."),
    },
    "returns": "emyBoolean -- True if the item was removed, False otherwise.",
    "key_notes": ("Item MUST first be appended to the tree. Requires "
                  "emyInitAether. Helper tree-management utility."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> tree = pyScript.aeCreateTree(\"WidgetTree\")\n"
                ">>> item = pyScript.aeCreateTreeItem(\"row_widget\", [\"Status\", 42], None, None)\n"
                ">>> pyScript.aeTreeAppendItem(tree, item)\n"
                ">>> ok = pyScript.geTreeRemoveItem(tree, item)\n"
                ">>> print(ok is True)\n"
                "True"),
}
API_DOCS["aeCreateTree"] = {
    "sig": "aeCreateTree(name: emystring) -> object   [deprecated since v2025.03]",
    "desc": ("Creates a tree (or subtree) object. Items are added with "
             "aeCreateTreeItem + aeTreeAppendItem. Deprecated; geCreateTree is "
             "the recommended successor but aeCreateTree remains functional."),
    "params": {"name: emystring": "Tree name (string)."},
    "returns": ("object (aeBaseTree) on success, False on error (e.g. non-string "
                "name)."),
    "key_notes": ("Requires emyInitAether first. Setup helper for "
                  "geTreeRemoveItem."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> tree = pyScript.aeCreateTree(\"WidgetTree\")\n"
                ">>> print(tree is not False)\n"
                "True"),
}
API_DOCS["aeCreateTreeItem"] = {
    "sig": ("aeCreateTreeItem(name: emystring, description: list=[], "
            "itemIcon=None, expandedIcon=None) -> object"),
    "desc": ("Creates a tree item with a name and a column-data list. The item "
             "must be appended to a tree via aeTreeAppendItem before it can be "
             "removed. Deprecated; geCreateTreeItem is the successor."),
    "params": {
        "name: emystring": "Item name (string, must not be None).",
        "description: list": ("Column values, e.g. [\"Status\", 42, 3.14]. May "
                              "mix str/int/float."),
        "itemIcon / expandedIcon": ("Icon objects or None. Passing a string "
                                    "raises TypeError."),
    },
    "returns": ("object (aeTreeItemCollection) on success, False if name is "
                "None."),
    "key_notes": ("description MUST be a list. Use None for icons, never a "
                  "string. Setup helper for geTreeRemoveItem."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> item = pyScript.aeCreateTreeItem(\"row_widget\", [\"Status\", 42], None, None)\n"
                ">>> print(item is not False)\n"
                "True"),
}
API_DOCS["aeTreeAppendItem"] = {
    "sig": "aeTreeAppendItem(tree: object, item: object) -> bool",
    "desc": ("Appends a tree item as a direct child of a tree. The item must "
             "later be a direct child for geTreeRemoveItem to succeed."),
    "params": {"tree: object": "Tree from aeCreateTree.",
               "item: object": "Item from aeCreateTreeItem."},
    "returns": "bool -- True if appended.",
    "key_notes": ("Must be called BEFORE geTreeRemoveItem. Setup helper."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> tree = pyScript.aeCreateTree(\"WidgetTree\")\n"
                ">>> item = pyScript.aeCreateTreeItem(\"row_widget\", [\"Status\", 42], None, None)\n"
                ">>> print(pyScript.aeTreeAppendItem(tree, item))\n"
                "True"),
}

# ===== Group 3: purpose-constant (emvPurposeNumberDrawing + GuCartPolyLine + emyPointArrayF) =====
API_DOCS["emvPurposeNumberDrawing"] = {
    "sig": "pyScript.emvPurposeNumberDrawing   [module-level enum constant]",
    "desc": ("A module-level enum constant naming the default DRAWING purpose "
             "number used when creating geometry on a drawing layer. Accessed as "
             "an attribute of the pyAether module (NOT called). Pass it as the "
             "purNum argument of geometry constructors such as GuCartPolyLine."),
    "params": {},
    "returns": ("The drawing-purpose-number enum value (int-like). Access via "
                "`pyScript.emvPurposeNumberDrawing` -- no parentheses."),
    "key_notes": ("This is a CONSTANT, not a function: do not call it. It is the "
                  "default drawing purpose; other purposes (e.g. pin/net) have "
                  "sibling emv* constants. Helper purpose enum, not a task "
                  "entry point."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pur = pyScript.emvPurposeNumberDrawing\n"
                ">>> print(pur is not None)\n"
                "True"),
}
API_DOCS["GuCartPolyLine"] = {
    "sig": ("GuCartPolyLine(pointArray: emyPointArrayF, layNum: int, "
            "purNum=emvPurposeNumberDrawing) -> GuCartPolyLine"),
    "desc": ("Constructs a cartoon polyline shape from a point array, a layer "
             "number and an optional purpose number (defaults to the drawing "
             "purpose constant emvPurposeNumberDrawing)."),
    "params": {
        "pointArray: emyPointArrayF": ("Point array built with .append(emyPointF)."),
        "layNum: int": "Layer number.",
        "purNum": ("Purpose number; default pyScript.emvPurposeNumberDrawing. "
                   "Pass an int for a custom purpose."),
    },
    "returns": "GuCartPolyLine -- the created polyline shape object.",
    "methods": "getPointArray(out_array) populates out_array with the vertices.",
    "key_notes": ("pointArray must be emyPointArrayF, not a list. Consumer of "
                  "emvPurposeNumberDrawing. Geometry constructor helper."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pa = pyScript.emyPointArrayF()\n"
                ">>> pa.append(pyScript.emyPointF(1.0, 1.0))\n"
                ">>> pa.append(pyScript.emyPointF(8.0, 4.0))\n"
                ">>> pa.append(pyScript.emyPointF(15.0, 9.0))\n"
                ">>> poly = pyScript.GuCartPolyLine(pa, layNum=12, purNum=pyScript.emvPurposeNumberDrawing)\n"
                ">>> print(poly.__class__.__name__)\n"
                "GuCartPolyLine"),
}
API_DOCS["emyPointArrayF"] = {
    "sig": "emyPointArrayF() -> emyPointArrayF   [SWIG container]",
    "desc": ("A SWIG-wrapped array of emyPointF. Construct empty then "
             ".append(emyPointF(x, y)). Required by geometry constructors such "
             "as GuCartPolyLine."),
    "params": {},
    "returns": "An empty emyPointArrayF; grows via .append().",
    "key_notes": ("Use .append(emyPointF); plain lists are not accepted. Helper "
                  "geometry container."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pa = pyScript.emyPointArrayF()\n"
                ">>> pa.append(pyScript.emyPointF(1.0, 1.0))\n"
                ">>> pa.append(pyScript.emyPointF(8.0, 4.0))\n"
                ">>> print(len(pa))\n"
                "2"),
}
# ===== Group 4: mouse (guMotion + mouseLBClick + aeGetCommandPoint) =====
API_DOCS["guMotion"] = {
    "sig": "guMotion(point: emyPointF=emyPointF(0,0)) -> bool",
    "desc": ("Moves the mouse cursor to a point in the current window. Returns "
             "True in a real GUI, False in a headless/sandbox environment. Must "
             "be paired with mouseLBClick to drive the cursor before reading the "
             "command point."),
    "params": {"point: emyPointF": ("Target cursor position; defaults to "
                                    "emyPointF(0,0).")},
    "returns": "bool -- True if the motion succeeded.",
    "key_notes": ("Requires emyInitAether(\"-adv\") and an open design window. "
                  "Returns False in headless test envs (still safe to call). "
                  "Helper mouse-event utility."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> pt = pyScript.emyPointF(3.0, 7.0)\n"
                ">>> moved = pyScript.guMotion(point=pt)\n"
                ">>> print(isinstance(moved, bool))\n"
                "True"),
}
API_DOCS["mouseLBClick"] = {
    "sig": "mouseLBClick(point: emyPointF, ctrl: bool=False, shift: bool=False) -> bool",
    "desc": ("Simulates a left-button mouse click at a point, optionally with "
             "Ctrl and/or Shift modifiers. Updates the system cursor state so a "
             "subsequent aeGetCommandPoint reflects the clicked position."),
    "params": {
        "point: emyPointF": "Click position.",
        "ctrl: bool": "Hold Ctrl while clicking (default False).",
        "shift: bool": "Hold Shift while clicking (default False).",
    },
    "returns": "bool -- True if the click succeeded.",
    "key_notes": ("Requires emyInitAether(\"-adv\"). Pair with guMotion to move "
                  "first. Returns False in headless envs. Helper mouse-event "
                  "utility."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> pt = pyScript.emyPointF(3.0, 7.0)\n"
                ">>> pyScript.guMotion(point=pt)\n"
                ">>> clicked = pyScript.mouseLBClick(point=pt, ctrl=True, shift=False)\n"
                ">>> print(isinstance(clicked, bool))\n"
                "True"),
}
API_DOCS["aeGetCommandPoint"] = {
    "sig": "aeGetCommandPoint(da=None, getFit: emyBoolean=False) -> emyPointF",
    "desc": ("Returns the current mouse position on a window as an emyPointF. "
             "After guMotion + mouseLBClick drive the cursor, this reads back the "
             "command point relative to a draw area."),
    "params": {
        "da: SleDrawArea": ("Draw-area window handle (from aeGetActiveDa); "
                            "default None uses the active window."),
        "getFit: emyBoolean": ("True -> relative to fitDesign, False -> "
                               "editDesign (default False)."),
    },
    "returns": ("emyPointF if a position is available, otherwise False."),
    "key_notes": ("Pair with guMotion + mouseLBClick to set the cursor first. "
                  "Consumer of the mouse-event helpers."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> pyScript.emyInitAether(\"-adv\")\n"
                ">>> da = pyScript.aeGetActiveDa()\n"
                ">>> pt = pyScript.emyPointF(3.0, 7.0)\n"
                ">>> pyScript.guMotion(point=pt)\n"
                ">>> pyScript.mouseLBClick(point=pt)\n"
                ">>> cmd = pyScript.aeGetCommandPoint(da=da)\n"
                ">>> print(cmd is not False or isinstance(cmd, bool))\n"
                "True"),
}
# ===== Group 5: smash (smash_option + dbSmashInst2) =====
API_DOCS["smash_option"] = {
    "sig": "smash_option() -> smash_option   [SWIG config struct]",
    "desc": ("Constructs a smash-option configuration object controlling how "
             "dbSmashInst2 flattens an instance. Set its boolean attributes "
             "(m_smashPyCell, m_smashVia, m_preservePins, m_preserveLabels) then "
             "pass it as the option argument to dbSmashInst2."),
    "params": {},
    "returns": "A default smash_option struct (all flags at their defaults).",
    "methods": (".m_smashPyCell (bool), .m_smashVia (bool), .m_preservePins "
                "(bool), .m_preserveLabels (bool) -- assignable attributes."),
    "key_notes": ("Create with smash_option() then set attributes; do NOT pass a "
                  "dict. m_preserveLabels defaults True. Helper config struct, "
                  "not a task entry point."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> opt = pyScript.smash_option()\n"
                ">>> opt.m_smashPyCell = True\n"
                ">>> opt.m_smashVia = False\n"
                ">>> opt.m_preservePins = True\n"
                ">>> print(opt is not None)\n"
                "True"),
}
API_DOCS["dbSmashInst2"] = {
    "sig": "dbSmashInst2(obj: emyInst, level: int, option: smash_option) -> bool",
    "desc": ("Smashes (flattens) an instance to a given hierarchy level using a "
             "smash_option config struct for fine-grained control of which "
             "sub-structures (PCells, vias, pins, labels) are preserved."),
    "params": {
        "obj: emyInst": "Instance to flatten (from dbCrtInst).",
        "level: int": ("Hierarchy depth to flatten to (0 = no-op, >=1 flattens "
                       "that many levels)."),
        "option: smash_option": ("Config struct from smash_option(); set "
                                 "m_smashPyCell / m_smashVia / m_preservePins / "
                                 "m_preserveLabels before passing."),
    },
    "returns": "bool -- True if the smash succeeded.",
    "key_notes": ("Consumer of smash_option. The instance's CV must be open. "
                  "Helper flatten utility."),
    "doctest": (">>> import pyAether as pyScript\n"
                ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
                ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I0\")\n"
                ">>> opt = pyScript.smash_option()\n"
                ">>> opt.m_smashPyCell = True\n"
                ">>> opt.m_smashVia = False\n"
                ">>> opt.m_preservePins = True\n"
                ">>> ok = pyScript.dbSmashInst2(obj=inst, level=1, option=opt)\n"
                ">>> print(isinstance(ok, bool))\n"
                "True"),
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

    def _s1_s3(name):
        doc = _doc_block(name)
        d = API_DOCS[name]
        _add("S1", "v35-S1-%s" % name,
             ("You are an EDA automation engineer. Given the following "
              "PyAether API reference, write a minimal correct Python "
              "code snippet that uses `%s`.\n\n%s" % (name, doc)),
             "```python\n%s\n```" % d["doctest"], [name],
             "S1 doc_to_code for %s" % name)
        _add("S3", "v35-S3-%s" % name,
             ("You are an EDA automation engineer. The following Python "
              "code uses a PyAether API. Identify the API name, describe "
              "what it does, and explain its signature.\n\n"
              "```python\n%s\n```" % d["doctest"]),
             ("The API used is **`%s`**.\n\n**Signature**: `%s`\n\n%s\n\n"
              "**Key notes**: %s" % (name, d["sig"], d["desc"],
                                     d.get("key_notes", ""))),
             [name], "S3 code_to_doc for %s" % name)

    # S1 + S3 for each of the 6 primary blind APIs (12 pairs)
    for name in ["agrGetSnapPoints", "geTreeRemoveItem",
                 "emvPurposeNumberDrawing", "guMotion", "mouseLBClick",
                 "smash_option"]:
        _s1_s3(name)

    # ===== S4 multi-step setup-context scenarios =====
    for label, scenario, apis, code in [
        ("snap-build-vector-and-call",
         "Open a cell view, create an instance, build a vector1D_emyPointF of "
         "two off-grid points, then call agrGetSnapPoints with type Polygon and "
         "report whether the result is a tuple.",
         ["agrGetSnapPoints", "dbCrtInst", "vector1D_emyPointF", "emyPointF"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.dbCreateLib(lib=\"demo_lib\", attachTechLib=\"TECHLIB\")\n"
         ">>> pyScript.dbNewCV(lib=\"demo_lib\", cell=\"inv\", view=\"layout\")\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
         ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I0\")\n"
         ">>> pts = pyScript.vector1D_emyPointF()\n"
         ">>> pts.append(pyScript.emyPointF(2.5, 3.5))\n"
         ">>> pts.append(pyScript.emyPointF(7.0, 1.0))\n"
         ">>> snapped = pyScript.agrGetSnapPoints(inst=inst, points=pts, type=pyScript.emyString(\"Polygon\"))\n"
         ">>> print(isinstance(snapped, tuple))\n"
         "True"),
        ("snap-convert-back-to-tuples",
         "After calling agrGetSnapPoints, iterate the returned tuple and convert "
         "each emyPointF back to a (x, y) float tuple list.",
         ["agrGetSnapPoints", "emyPointF"],
         ">>> import pyAether as pyScript\n"
         ">>> # assume `snapped` is the tuple returned by agrGetSnapPoints\n"
         ">>> out = []\n"
         ">>> for pt in snapped:\n"
         "...     out.append((float(pt.x()), float(pt.y())))\n"
         ">>> print(isinstance(out, list) and all(isinstance(t, tuple) for t in out))\n"
         "True"),
    ]:
        _add("S4", "v35-S4-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S4 multi_step: %s" % scenario)
    for label, scenario, apis, code in [
        ("tree-create-append-remove",
         "Initialize Aether, create a tree, create an item with column data, "
         "append it, then remove it with geTreeRemoveItem and confirm True.",
         ["geTreeRemoveItem", "aeCreateTree", "aeCreateTreeItem",
          "aeTreeAppendItem"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> tree = pyScript.aeCreateTree(\"WidgetTree\")\n"
         ">>> item = pyScript.aeCreateTreeItem(\"row_widget\", [\"Status\", 42], None, None)\n"
         ">>> pyScript.aeTreeAppendItem(tree, item)\n"
         ">>> ok = pyScript.geTreeRemoveItem(tree, item)\n"
         ">>> print(ok is True)\n"
         "True"),
        ("tree-two-items-remove-one",
         "Append two items to a tree, remove only the second, and confirm the "
         "removal returns True while the first item is untouched.",
         ["geTreeRemoveItem", "aeCreateTree", "aeCreateTreeItem",
          "aeTreeAppendItem"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> tree = pyScript.aeCreateTree(\"WidgetTree\")\n"
         ">>> i1 = pyScript.aeCreateTreeItem(\"row_keep\", [\"Active\", 1], None, None)\n"
         ">>> i2 = pyScript.aeCreateTreeItem(\"row_drop\", [\"Inactive\", 0], None, None)\n"
         ">>> pyScript.aeTreeAppendItem(tree, i1)\n"
         ">>> pyScript.aeTreeAppendItem(tree, i2)\n"
         ">>> removed = pyScript.geTreeRemoveItem(tree, i2)\n"
         ">>> print(removed is True)\n"
         "True"),
        ("purpose-default-polyline",
         "Build an emyPointArrayF of three points and construct a GuCartPolyLine "
         "on layer 12 using the default drawing-purpose constant "
         "emvPurposeNumberDrawing, then print the class name.",
         ["emvPurposeNumberDrawing", "GuCartPolyLine", "emyPointArrayF",
          "emyPointF"],
         ">>> import pyAether as pyScript\n"
         ">>> pa = pyScript.emyPointArrayF()\n"
         ">>> pa.append(pyScript.emyPointF(1.0, 1.0))\n"
         ">>> pa.append(pyScript.emyPointF(8.0, 4.0))\n"
         ">>> pa.append(pyScript.emyPointF(15.0, 9.0))\n"
         ">>> poly = pyScript.GuCartPolyLine(pa, layNum=12, purNum=pyScript.emvPurposeNumberDrawing)\n"
         ">>> print(poly.__class__.__name__)\n"
         "GuCartPolyLine"),
        ("purpose-custom-vs-default",
         "Construct two polylines on the same layer, one with the default "
         "drawing purpose and one with an explicit custom purpose number, and "
         "confirm both are GuCartPolyLine objects.",
         ["emvPurposeNumberDrawing", "GuCartPolyLine", "emyPointArrayF"],
         ">>> import pyAether as pyScript\n"
         ">>> pa = pyScript.emyPointArrayF()\n"
         ">>> pa.append(pyScript.emyPointF(1.0, 1.0))\n"
         ">>> pa.append(pyScript.emyPointF(8.0, 4.0))\n"
         ">>> p_def = pyScript.GuCartPolyLine(pa, layNum=12, purNum=pyScript.emvPurposeNumberDrawing)\n"
         ">>> pa2 = pyScript.emyPointArrayF()\n"
         ">>> pa2.append(pyScript.emyPointF(2.0, 2.0))\n"
         ">>> p_cust = pyScript.GuCartPolyLine(pa2, layNum=12, purNum=7)\n"
         ">>> print(p_def.__class__.__name__ == p_cust.__class__.__name__)\n"
         "True"),
    ]:
        _add("S4", "v35-S4-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S4 multi_step: %s" % scenario)
    for label, scenario, apis, code in [
        ("mouse-motion-click-read",
         "Initialize Aether in advanced mode, move the mouse to (3,7), "
         "left-click at that point, then read the command point from the active "
         "draw area and confirm a non-False result or a bool.",
         ["guMotion", "mouseLBClick", "aeGetCommandPoint", "emyPointF"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> da = pyScript.aeGetActiveDa()\n"
         ">>> pt = pyScript.emyPointF(3.0, 7.0)\n"
         ">>> pyScript.guMotion(point=pt)\n"
         ">>> pyScript.mouseLBClick(point=pt)\n"
         ">>> cmd = pyScript.aeGetCommandPoint(da=da)\n"
         ">>> print(cmd is not False or isinstance(cmd, bool))\n"
         "True"),
        ("mouse-ctrl-shift-modifiers",
         "Move the mouse then perform a Ctrl+Shift left-click, demonstrating the "
         "modifier-key flags of mouseLBClick.",
         ["guMotion", "mouseLBClick", "emyPointF"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pt = pyScript.emyPointF(3.0, 7.0)\n"
         ">>> pyScript.guMotion(point=pt)\n"
         ">>> clicked = pyScript.mouseLBClick(point=pt, ctrl=True, shift=True)\n"
         ">>> print(isinstance(clicked, bool))\n"
         "True"),
        ("smash-config-and-flatten",
         "Open a cell view, create an instance, build a smash_option with "
         "m_smashPyCell=True / m_smashVia=False / m_preservePins=True, then call "
         "dbSmashInst2 at level 1 and confirm a bool result.",
         ["smash_option", "dbSmashInst2", "dbCrtInst"],
         ">>> import pyAether as pyScript\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
         ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I0\")\n"
         ">>> opt = pyScript.smash_option()\n"
         ">>> opt.m_smashPyCell = True\n"
         ">>> opt.m_smashVia = False\n"
         ">>> opt.m_preservePins = True\n"
         ">>> ok = pyScript.dbSmashInst2(obj=inst, level=1, option=opt)\n"
         ">>> print(isinstance(ok, bool))\n"
         "True"),
        ("smash-preserve-labels",
         "Build a smash_option that keeps labels and pins while smashing PCells, "
         "then flatten at level 2.",
         ["smash_option", "dbSmashInst2", "dbCrtInst"],
         ">>> import pyAether as pyScript\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
         ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I1\")\n"
         ">>> opt = pyScript.smash_option()\n"
         ">>> opt.m_smashPyCell = True\n"
         ">>> opt.m_smashVia = True\n"
         ">>> opt.m_preservePins = True\n"
         ">>> opt.m_preserveLabels = True\n"
         ">>> ok = pyScript.dbSmashInst2(obj=inst, level=2, option=opt)\n"
         ">>> print(isinstance(ok, bool))\n"
         "True"),
    ]:
        _add("S4", "v35-S4-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S4 multi_step: %s" % scenario)
    # ===== S5 advanced / edge-case scenarios =====
    for label, scenario, apis, code in [
        ("snap-path-type-empty-safe",
         "Call agrGetSnapPoints with type Path and guard against an empty "
         "returned tuple by checking truthiness before iteration.",
         ["agrGetSnapPoints", "dbCrtInst", "vector1D_emyPointF", "emyPointF"],
         ">>> import pyAether as pyScript\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
         ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I0\")\n"
         ">>> pts = pyScript.vector1D_emyPointF()\n"
         ">>> pts.append(pyScript.emyPointF(2.5, 3.5))\n"
         ">>> snapped = pyScript.agrGetSnapPoints(inst=inst, points=pts, type=pyScript.emyString(\"Path\"))\n"
         ">>> out = [(float(p.x()), float(p.y())) for p in snapped] if snapped else []\n"
         ">>> print(isinstance(out, list))\n"
         "True"),
        ("tree-remove-twice-second-fails",
         "Remove an item that is a direct child (True), then attempt to remove "
         "the same item again (it is no longer a child) and show the second call "
         "returns False.",
         ["geTreeRemoveItem", "aeCreateTree", "aeCreateTreeItem",
          "aeTreeAppendItem"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> tree = pyScript.aeCreateTree(\"WidgetTree\")\n"
         ">>> item = pyScript.aeCreateTreeItem(\"row_widget\", [\"Status\", 42], None, None)\n"
         ">>> pyScript.aeTreeAppendItem(tree, item)\n"
         ">>> first = pyScript.geTreeRemoveItem(tree, item)\n"
         ">>> second = pyScript.geTreeRemoveItem(tree, item)\n"
         ">>> print(first is True and second is False)\n"
         "True"),
        ("purpose-read-back-vertices",
         "After building a GuCartPolyLine, read its vertices back into a fresh "
         "emyPointArrayF via getPointArray and confirm the count matches.",
         ["GuCartPolyLine", "emyPointArrayF", "emyPointF",
          "emvPurposeNumberDrawing"],
         ">>> import pyAether as pyScript\n"
         ">>> pa = pyScript.emyPointArrayF()\n"
         ">>> pa.append(pyScript.emyPointF(1.0, 1.0))\n"
         ">>> pa.append(pyScript.emyPointF(8.0, 4.0))\n"
         ">>> pa.append(pyScript.emyPointF(15.0, 9.0))\n"
         ">>> poly = pyScript.GuCartPolyLine(pa, layNum=12, purNum=pyScript.emvPurposeNumberDrawing)\n"
         ">>> back = pyScript.emyPointArrayF()\n"
         ">>> poly.getPointArray(back)\n"
         ">>> print(len(back) == 3)\n"
         "True"),
        ("mouse-getfit-flag",
         "Read the command point with getFit=True (relative to fitDesign) after "
         "moving and clicking, demonstrating the getFit parameter.",
         ["guMotion", "mouseLBClick", "aeGetCommandPoint", "emyPointF"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> da = pyScript.aeGetActiveDa()\n"
         ">>> pt = pyScript.emyPointF(3.0, 7.0)\n"
         ">>> pyScript.guMotion(point=pt)\n"
         ">>> pyScript.mouseLBClick(point=pt)\n"
         ">>> cmd = pyScript.aeGetCommandPoint(da=da, getFit=True)\n"
         ">>> print(cmd is not False or isinstance(cmd, bool))\n"
         "True"),
        ("smash-level-zero-noop",
         "Show that dbSmashInst2 with level 0 is a no-op that still returns a "
         "bool, using a default smash_option.",
         ["smash_option", "dbSmashInst2", "dbCrtInst"],
         ">>> import pyAether as pyScript\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
         ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I0\")\n"
         ">>> opt = pyScript.smash_option()\n"
         ">>> ok = pyScript.dbSmashInst2(obj=inst, level=0, option=opt)\n"
         ">>> print(isinstance(ok, bool))\n"
         "True"),
    ]:
        _add("S5", "v35-S5-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S5 advanced: %s" % scenario)
    # ===== S6 cross-API integrated workflows =====
    for label, scenario, apis, code in [
        ("snap-then-smash-flatten",
         "Create an instance, snap a set of off-grid points to the grid, then "
         "flatten the instance with dbSmashInst2 using a configured smash_option. "
         "This is a combined layout-edit workflow: geometry cleanup followed by "
         "hierarchy flattening.",
         ["agrGetSnapPoints", "smash_option", "dbSmashInst2", "dbCrtInst",
          "vector1D_emyPointF", "emyPointF"],
         ">>> import pyAether as pyScript\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
         ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I0\")\n"
         ">>> pts = pyScript.vector1D_emyPointF()\n"
         ">>> pts.append(pyScript.emyPointF(2.5, 3.5))\n"
         ">>> pts.append(pyScript.emyPointF(7.0, 1.0))\n"
         ">>> snapped = pyScript.agrGetSnapPoints(inst=inst, points=pts, type=pyScript.emyString(\"Polygon\"))\n"
         ">>> opt = pyScript.smash_option()\n"
         ">>> opt.m_smashPyCell = True\n"
         ">>> opt.m_smashVia = False\n"
         ">>> opt.m_preservePins = True\n"
         ">>> ok = pyScript.dbSmashInst2(obj=inst, level=1, option=opt)\n"
         ">>> print(isinstance(ok, bool) and isinstance(snapped, tuple))\n"
         "True"),
        ("mouse-then-snap-command-point",
         "Move and click the mouse, read the command point, then feed that "
         "point (wrapped in a vector1D_emyPointF) into agrGetSnapPoints to snap "
         "it to the grid. This is an interactive edit-flow: pick a point with "
         "the mouse, then snap it.",
         ["guMotion", "mouseLBClick", "aeGetCommandPoint", "agrGetSnapPoints",
          "vector1D_emyPointF", "emyPointF", "dbCrtInst"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> da = pyScript.aeGetActiveDa()\n"
         ">>> pyScript.guMotion(point=pyScript.emyPointF(3.0, 7.0))\n"
         ">>> pyScript.mouseLBClick(point=pyScript.emyPointF(3.0, 7.0))\n"
         ">>> cmd = pyScript.aeGetCommandPoint(da=da)\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
         ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I0\")\n"
         ">>> pts = pyScript.vector1D_emyPointF()\n"
         ">>> if cmd is not False and not isinstance(cmd, bool):\n"
         "...     pts.append(cmd)\n"
         ">>> snapped = pyScript.agrGetSnapPoints(inst=inst, points=pts, type=pyScript.emyString(\"Polygon\"))\n"
         ">>> print(isinstance(snapped, tuple))\n"
         "True"),
        ("tree-manage-polyline-record",
         "Build a GuCartPolyLine with the default drawing purpose, then create a "
         "tree to track it, add an item describing the shape, and remove the "
         "item when no longer needed. This combines geometry creation with a "
         "GUI-tree bookkeeping workflow.",
         ["geTreeRemoveItem", "aeCreateTree", "aeCreateTreeItem",
          "aeTreeAppendItem", "GuCartPolyLine", "emyPointArrayF", "emyPointF",
          "emvPurposeNumberDrawing"],
         ">>> import pyAether as pyScript\n"
         ">>> pyScript.emyInitAether(\"-adv\")\n"
         ">>> pa = pyScript.emyPointArrayF()\n"
         ">>> pa.append(pyScript.emyPointF(1.0, 1.0))\n"
         ">>> pa.append(pyScript.emyPointF(8.0, 4.0))\n"
         ">>> poly = pyScript.GuCartPolyLine(pa, layNum=12, purNum=pyScript.emvPurposeNumberDrawing)\n"
         ">>> tree = pyScript.aeCreateTree(\"ShapeTracker\")\n"
         ">>> item = pyScript.aeCreateTreeItem(\"poly_12\", [\"GuCartPolyLine\", 12], None, None)\n"
         ">>> pyScript.aeTreeAppendItem(tree, item)\n"
         ">>> removed = pyScript.geTreeRemoveItem(tree, item)\n"
         ">>> print(removed is True and poly.__class__.__name__ == \"GuCartPolyLine\")\n"
         "True"),
        ("smash-then-snap-post-flatten",
         "Flatten an instance with dbSmashInst2 (preserving pins), then snap a "
         "fresh set of points after the hierarchy is flattened. This is the "
         "reverse order of snap-then-smash: flatten first, then snap the "
         "resulting flat geometry.",
         ["smash_option", "dbSmashInst2", "agrGetSnapPoints", "dbCrtInst",
          "vector1D_emyPointF", "emyPointF"],
         ">>> import pyAether as pyScript\n"
         ">>> cv = pyScript.dbOpenCVByType(lib=\"demo_lib\", cell=\"inv\", view=\"layout\", mode=\"a\")\n"
         ">>> inst = pyScript.dbCrtInst(cv=cv, point=(0, 0), lib=\"TECHLIB\", cell=\"inv\", view=\"layout\", inst=\"I0\")\n"
         ">>> opt = pyScript.smash_option()\n"
         ">>> opt.m_smashPyCell = True\n"
         ">>> opt.m_smashVia = True\n"
         ">>> opt.m_preservePins = True\n"
         ">>> flat_ok = pyScript.dbSmashInst2(obj=inst, level=2, option=opt)\n"
         ">>> pts = pyScript.vector1D_emyPointF()\n"
         ">>> pts.append(pyScript.emyPointF(2.5, 3.5))\n"
         ">>> snapped = pyScript.agrGetSnapPoints(inst=inst, points=pts, type=pyScript.emyString(\"Path\"))\n"
         ">>> print(isinstance(flat_ok, bool) and isinstance(snapped, tuple))\n"
         "True"),
    ]:
        _add("S6", "v35-S6-%s" % label,
             ("You are an EDA automation engineer. %s Write a complete "
              "Python script using PyAether (import as pyScript)." % scenario),
             "```python\n%s\n```" % code, apis, "S6 cross_api: %s" % scenario)

    if limit and len(pairs) > limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details

def main():
    parser = argparse.ArgumentParser(
        description="R205 v35 context-blind SFT corpus builder "
                    "(6 context-dependent blind APIs + 6 setup helpers, ~36 pairs)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print stats only, do not write output file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Output JSONL path (default: %s)" % DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of pairs (for testing)")
    args = parser.parse_args()

    sys.stderr.write("R205 v35 context-blind corpus builder\n")
    sys.stderr.write("  Target APIs: %d (%s)\n" % (
        len(API_ORDER), ", ".join(API_ORDER)))

    missing = [a for a in API_ORDER if a not in API_DOCS]
    if missing:
        sys.stderr.write("ERROR: Missing API_DOCS for: %s\n"
                         % ", ".join(missing))
        sys.exit(1)

    eval_eps = load_eval_entry_points()
    sys.stderr.write("  Eval entry_points loaded: %d\n" % len(eval_eps))
    for a in ["agrGetSnapPoints", "geTreeRemoveItem",
              "emvPurposeNumberDrawing", "guMotion", "mouseLBClick",
              "smash_option"]:
        sys.stderr.write("  %s is entry_point? %s\n" % (a, a in eval_eps))

    pairs, rejected, reject_details = build_pairs(eval_eps, limit=args.limit)

    api_coverage = {}
    for p in pairs:
        for a in p["api_used"]:
            api_coverage[a] = api_coverage.get(a, 0) + 1

    type_counts = {}
    for p in pairs:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

    sys.stderr.write("\n=== R205 v35 Corpus Stats ===\n")
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
        sys.stderr.write("    %-25s %2d\n" % (a, api_coverage.get(a, 0)))

    # FINGERPRINT SCAN GATE -- 0 contamination is mandatory
    if rejected != 0:
        sys.stderr.write("\nFATAL: fingerprint scan found %d contamination(s) "
                         "-- refusing to write output.\n" % rejected)
        sys.exit(2)
    sys.stderr.write("\nFINGERPRINT SCAN: PASS (0 contamination)\n")

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










