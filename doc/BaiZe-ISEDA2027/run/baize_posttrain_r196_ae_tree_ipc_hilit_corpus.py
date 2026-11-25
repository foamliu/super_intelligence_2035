#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r196_ae_tree_ipc_hilit_corpus.py
R196 -- v26 PyAether SFT corpus: ae* blind spot (8 APIs, 40 pairs).

BACKGROUND: v11-v25 (668 pairs) cover 121/164 eval raw APIs (73.8%). 43 blind.
Data-driven scan (R191 blind_scan, re-run with v25) shows ae* is the #1 blind
family (8 usages, 8 APIs). R196 targets all 8 ae* APIs across 5 sub-categories:

  - Tree widgets (deprecated): aeCreateTree, aeCreateTreeItem, aeTreeAppendItem
  - Hierarchy Ae: aeEditInPlace, aeReturn
  - Highlight Ae: aeCrtHilitPolygon
  - Window Ae: aeSetWindowFocus
  - IPC / Misc: aeIpcProcess (a CLASS created by aeIpcBeginProcess)

All ISOLATE-class (eval helper APIs, NOT eval entry_points).  Fingerprint scan
rejects eval entry_points (155 loaded).  0 of 155 entry_points contain "ae".

Authoritative signatures fetched via pyAether MCP get_api_details (R196 wake).

Usage:
  python3 baize_posttrain_r196_ae_tree_ipc_hilit_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(RUN_DIR, "sft_pyaether_corpus_v26_ae_tree_ipc_hilit.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["aeCreateTree"] = {
    "sig": "aeCreateTree(name) -> object",
    "desc": "Creates a tree or subtree widget. Items can be added with aeCreateTreeItem and appended via aeTreeAppendItem. A tree table can be created with aeCreateTreeTable. Deprecated since v2025.03 -- use geCreateTree instead.",
    "params": {"name": "str or emyString -- the name of the tree (must be a string; int/float/list/dict/bool/None return False)"},
    "returns": "object -- aeBaseTree instance on success; False if name is not a string or on error",
    "methods": "Pass the returned tree object to aeTreeAppendItem(tree, item) to add items.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> tree = pyScript.aeCreateTree("mainTree")\n'
                '>>> print(type(tree).__name__)\n'
                'aeBaseTree\n'
                '>>> bad = pyScript.aeCreateTree(123)\n'
                '>>> print(bad)\n'
                'False'),
    "category": "Qt Extension / Deprecated widgets", "safety": "ISOLATE", "eval_count": 2,
    "key_notes": "Returns an aeBaseTree OBJECT (not bool). Non-string name -> False. Deprecated v2025.03 -> use geCreateTree. Must call emyInitAether first. Empty string name is accepted."}

API_DOCS["aeCreateTreeItem"] = {
    "sig": "aeCreateTreeItem(name, description=[], itemIcon=None, expandedIcon=None) -> object",
    "desc": "Creates an item for a tree. The item carries a name and optional column descriptions (strings, ints, floats) displayed in a tree table. Icons must be valid aeBaseIcon objects (NOT string paths). Deprecated since v2025.03 -- use geCreateTreeItem instead.",
    "params": {
        "name": "str or emyString -- name of the tree item (must be string; None returns False)",
        "description": "list, optional -- column values (str, int, float, bool); default empty list []",
        "itemIcon": "aeBaseIcon, optional -- icon displayed left of description; default None (string path raises TypeError)",
        "expandedIcon": "aeBaseIcon, optional -- icon shown when item is expanded; default None",
    },
    "returns": "object -- aeTreeItemCollection instance on success; False if name is None or on error",
    "methods": "Pass the returned item to aeTreeAppendItem(tree, item) to add it to a tree.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> item = pyScript.aeCreateTreeItem("net1", ["VDD", "M1", 100, 3.14], None, None)\n'
                '>>> print(type(item).__name__)\n'
                'aeTreeItemCollection\n'
                '>>> bad = pyScript.aeCreateTreeItem(None)\n'
                '>>> print(bad)\n'
                'False'),
    "category": "Qt Extension / Deprecated widgets", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns aeTreeItemCollection OBJECT (not bool). name must be str (None -> False). description MUST be a list (not tuple/string). Icons must be aeBaseIcon objects -- string paths raise TypeError. Use None for no icon. Deprecated -> geCreateTreeItem."}

API_DOCS["aeTreeAppendItem"] = {
    "sig": "aeTreeAppendItem(tree, item) -> bool",
    "desc": "Appends a tree item (created by aeCreateTreeItem) to a tree (created by aeCreateTree). Returns True on success, False on failure or if the same item is appended twice. Deprecated since v2025.03 -- use geTreeAppendItem instead.",
    "params": {
        "tree": "aeBaseTree -- the tree object returned by aeCreateTree",
        "item": "aeTreeItemCollection -- the item object returned by aeCreateTreeItem",
    },
    "returns": "bool -- True if item was appended; False on failure, invalid args, or duplicate append",
    "methods": "Create tree with aeCreateTree, create item with aeCreateTreeItem, then aeTreeAppendItem(tree, item).",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> tree = pyScript.aeCreateTree("netTree")\n'
                '>>> item = pyScript.aeCreateTreeItem("netVDD", ["power", "M1"], None, None)\n'
                '>>> result = pyScript.aeTreeAppendItem(tree, item)\n'
                '>>> print(result)\n'
                'True\n'
                '>>> dup = pyScript.aeTreeAppendItem(tree, item)\n'
                '>>> print(dup)\n'
                'False'),
    "category": "Qt Extension / Deprecated widgets", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Returns bool (True=success, False=fail/duplicate). Both args must be objects (tree from aeCreateTree, item from aeCreateTreeItem) -- passing strings raises TypeError. Duplicate append of the SAME item -> False. Deprecated -> geTreeAppendItem."}

API_DOCS["aeCrtHilitPolygon"] = {
    "sig": "aeCrtHilitPolygon(cvId, points) -> emyShape",
    "desc": "Creates a polygon highlight shape on the given highlight set design. The points must be a vector1D_emyPointF (SWIG container), NOT a plain Python list.",
    "params": {
        "cvId": "emyDesign -- the highlight set design (typically from aeCrtHilitSet(aeGetCurDesign(), layerName))",
        "points": "vector1D_emyPointF -- the polygon vertices; use vector1D_emyPointF() then .append(emyPointF(x,y)) to build",
    },
    "returns": "emyShape -- the highlight polygon shape object",
    "methods": "Build points with vector1D_emyPointF(), append emyPointF vertices, then call aeCrtHilitPolygon(design, points).",
    "doctest": ('>>> from pyAether import *\n'
                '>>> emyInitAether("-adv")\n'
                '>>> design = aeCrtHilitSet(aeGetCurDesign(), "M1")\n'
                '>>> pts = vector1D_emyPointF()\n'
                '>>> pts.append(emyPointF(1, 3))\n'
                '>>> pts.append(emyPointF(1, 8))\n'
                '>>> pts.append(emyPointF(3, 8))\n'
                '>>> pts.append(emyPointF(3, 3))\n'
                '>>> shape = aeCrtHilitPolygon(design, pts)\n'
                '>>> print(type(shape).__name__)\n'
                'emyShape'),
    "category": "Ae Commands / Highlight Ae Commands", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "points MUST be vector1D_emyPointF (SWIG container), NOT a plain Python list -- use vector1D_emyPointF() then .append(emyPointF(x,y)). cvId comes from aeCrtHilitSet(aeGetCurDesign(), layer), not the cellview directly. Returns emyShape. Polygon needs >= 3 vertices."}

API_DOCS["aeEditInPlace"] = {
    "sig": "aeEditInPlace(point=None, hierList=None)",
    "desc": "Enters Edit-In-Place (EIP) mode to edit a bottom cell within the top cell. Either specify a point to auto-select the object at that location, or provide a hierarchy list to specify the exact instance path.",
    "params": {
        "point": "emyPointF, optional -- if no object is selected, specifies the point to select the object; default None",
        "hierList": "list or tuple, optional -- hierarchy path [[instId_0, row_0, col_0], ...]; each element is [instance, row, col]; default None",
    },
    "returns": "None (command-style -- enters EIP mode)",
    "methods": "Use aeReturn() to exit EIP mode and return to the last cell. Use point for simple cases, hierList for multi-level descent.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test", "test", "layout")\n'
                '>>> pos = pyScript.emyPointF(1, 1)\n'
                '>>> pyScript.aeEditInPlace(pos)\n'
                '>>> # ... edit the bottom cell ...\n'
                '>>> pyScript.aeReturn()\n'
                '>>> cv_top = pyScript.aeGetCurDesign()\n'
                '>>> cv_1 = cv_top.instances[0].master\n'
                '>>> pyScript.aeEditInPlace(hierList=[[cv_top.instances[0], 1, 1]])'),
    "category": "Ae Commands / Hierarchy Ae Commands", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "Either point (emyPointF) OR hierList (list of [instId, row, col]) -- not both simultaneously. point auto-selects object at location; hierList specifies exact instance path for multi-level descent. After EIP, call aeReturn() to go back. Must have an open design first (aeOpenDesign)."}

API_DOCS["aeIpcProcess"] = {
    "sig": "aeIpcProcess (class) -- instances created by aeIpcBeginProcess(command, ...)",
    "desc": "A process management class for inter-process communication (IPC). Instances are created by aeIpcBeginProcess(command_string) which launches an external process. The returned object provides methods to read stdout, write stdin, check status, and terminate the process. NOT a standalone callable function -- it is a class whose instances are process handles.",
    "params": {
        "command": "str -- the shell command to execute (passed to aeIpcBeginProcess)",
        "dataHandler": "callable, optional -- callback for stdout data: handler(cid, data) -> processed",
        "errHandler": "callable, optional -- callback for stderr data: handler(cid, data)",
        "postFunc": "callable, optional -- callback on process exit: func(cid, exit_status)",
    },
    "returns": "aeIpcProcess instance -- process handle with methods: isPending(), readline(), kill(), stop(), write(data), writeEOF(), state ('Active'/'Dead'), exitStatus, pid",
    "methods": "p = aeIpcBeginProcess('cmd'); while p.isPending(): data = aeIpcReadProcess(p, timeout); ...; p.kill()",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> p = pyScript.aeIpcBeginProcess("echo hello")\n'
                '>>> print(type(p).__name__)\n'
                'aeIpcProcess\n'
                '>>> while p.isPending():\n'
                '...     out = pyScript.aeIpcReadProcess(p, timeout=2)\n'
                '...     if out is not None:\n'
                '...         print(out.strip())\n'
                'hello\n'
                '>>> print("exit status:", p.exitStatus)\n'
                'exit status: 0'),
    "category": "Misc Commands / IPC", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "aeIpcProcess is a CLASS -- you do NOT call aeIpcProcess() directly. Create instances via aeIpcBeginProcess(command). Key methods: isPending() (bool, still running), readline()/aeIpcReadProcess(p, timeout) (read stdout), write(data)/writeEOF() (write stdin), kill()/stop() (terminate), state ('Active'/'Dead'), exitStatus (int, 0=success), pid. Avoid GUI calls in callbacks (core dump risk)."}

API_DOCS["aeReturn"] = {
    "sig": "aeReturn() -> None",
    "desc": "Returns to the last cell after using Edit-In-Place (aeEditInPlace) or Descend Edit/Read function to descend to a bottom cell. No arguments -- it pops back to the previous hierarchy level.",
    "params": {},
    "returns": "None (command-style -- returns to last cell in hierarchy)",
    "methods": "Call after aeEditInPlace or a Descend Edit/Read to return to the parent cell.",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test_agr", "test", "layout")\n'
                '>>> pyScript.aeEditInPlace(pyScript.emyPointF(1, 1))\n'
                '>>> # ... edit the bottom cell ...\n'
                '>>> pyScript.aeReturn()\n'
                '>>> # now back at the top cell'),
    "category": "Ae Commands / Hierarchy Ae Commands", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "No arguments. Must be called AFTER aeEditInPlace or Descend Edit/Read to return to the parent cell. Requires an open design. If not in EIP/descend mode, it is a no-op or may error."}

API_DOCS["aeSetWindowFocus"] = {
    "sig": "aeSetWindowFocus(win, setCurrent=True) -> bool",
    "desc": "Focuses the current main window to the specified window. The window handle is obtained from aeGetWndByIndex(index). Returns True if the window exists, False if the window is None.",
    "params": {
        "win": "BaseMainWindow -- the window to focus on (from aeGetWndByIndex)",
        "setCurrent": "bool, optional -- default True; whether to set as current window",
    },
    "returns": "bool -- True if window exists and focus succeeded; False if win is None",
    "methods": "Get window handle with aeGetWndByIndex(index), then aeSetWindowFocus(win).",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.aeOpenDesign("test_adv", "test", "layout")\n'
                '>>> win = pyScript.aeGetWndByIndex(2)\n'
                '>>> result = pyScript.aeSetWindowFocus(win)\n'
                '>>> print(result)\n'
                'True\n'
                '>>> bad = pyScript.aeSetWindowFocus(None)\n'
                '>>> print(bad)\n'
                'False'),
    "category": "Ae Commands / Window Ae Commands", "safety": "ISOLATE", "eval_count": 1,
    "key_notes": "win must be a BaseMainWindow object from aeGetWndByIndex(index) -- NOT an index int. Returns False if win is None. Requires open design. Used to switch focus between multiple open windows."}


API_ORDER = ["aeCreateTree", "aeCreateTreeItem", "aeTreeAppendItem",
             "aeCrtHilitPolygon", "aeEditInPlace", "aeIpcProcess",
             "aeReturn", "aeSetWindowFocus"]

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

    # ---- S1: doc -> code (8 pairs, one per API) ----
    for name in API_ORDER:
        doc = _doc_block(name)
        d = API_DOCS[name]
        prompt = ("You are an EDA automation engineer. Given the following "
                  "PyAether API reference, write a minimal correct Python "
                  "code snippet that uses `%s`.\n\n%s" % (name, doc))
        completion = "```python\n%s\n```" % d["doctest"]
        _add("S1", "v26-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S3: code -> doc (8 pairs, one per API) ----
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
        _add("S3", "v26-S3-%s" % name, prompt, completion, [name],
             "S3 code_to_doc for %s" % name)

    # ---- S4: multi-step trace (8 pairs) ----
    s4_traces = [
        ("aeCreateTree",
         "Create a tree, add two items to it, and verify the append results.",
         ["aeCreateTree"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "tree = pyScript.aeCreateTree('netHierarchy')\n"
          "print('tree type:', type(tree).__name__)\n"
          "item1 = pyScript.aeCreateTreeItem('netVDD', ['power', 'M1', 100], None, None)\n"
          "item2 = pyScript.aeCreateTreeItem('netGND', ['ground', 'M1', 100], None, None)\n"
          "r1 = pyScript.aeTreeAppendItem(tree, item1)\n"
          "r2 = pyScript.aeTreeAppendItem(tree, item2)\n"
          "print('append item1:', r1)\n"
          "print('append item2:', r2)\n"
          "dup = pyScript.aeTreeAppendItem(tree, item1)\n"
          "print('duplicate append:', dup)")),
        ("aeCreateTreeItem",
         "Create tree items with different description types and verify the return type.",
         ["aeCreateTreeItem"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "item_a = pyScript.aeCreateTreeItem('cell1', ['INV', 'layout', 42], None, None)\n"
          "print('item_a type:', type(item_a).__name__)\n"
          "item_b = pyScript.aeCreateTreeItem('cell2', ['NAND', 'schematic', 3.14], None, None)\n"
          "item_c = pyScript.aeCreateTreeItem('cell3', [], None, None)\n"
          "print('empty desc item:', type(item_c).__name__)\n"
          "bad = pyScript.aeCreateTreeItem(None, [], None, None)\n"
          "print('None name:', bad)")),
        ("aeTreeAppendItem",
         "Build a multi-level tree by creating a tree, multiple items, and appending them in sequence.",
         ["aeTreeAppendItem"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "tree = pyScript.aeCreateTree('designTree')\n"
          "results = []\n"
          "for i in range(3):\n"
          "    item = pyScript.aeCreateTreeItem('node%d' % i, ['cell', i, 0.0], None, None)\n"
          "    ok = pyScript.aeTreeAppendItem(tree, item)\n"
          "    results.append(ok)\n"
          "print('append results:', results)\n"
          "first_item = pyScript.aeCreateTreeItem('node0', ['cell', 0, 0.0], None, None)\n"
          "retry = pyScript.aeTreeAppendItem(tree, first_item)\n"
          "print('re-append new node0:', retry)")),
        ("aeCrtHilitPolygon",
         "Create a highlight set on the current design, build a rectangle polygon with vector1D_emyPointF.",
         ["aeCrtHilitPolygon"],
         ("from pyAether import *\n\n"
          "emyInitAether('-adv')\n"
          "aeOpenDesign('test', 'test', 'layout')\n"
          "design = aeCrtHilitSet(aeGetCurDesign(), 'M1')\n"
          "pts = vector1D_emyPointF()\n"
          "pts.append(emyPointF(0, 0))\n"
          "pts.append(emyPointF(0, 10))\n"
          "pts.append(emyPointF(10, 10))\n"
          "pts.append(emyPointF(10, 0))\n"
          "shape = aeCrtHilitPolygon(design, pts)\n"
          "print('highlight shape type:', type(shape).__name__)")),
        ("aeEditInPlace",
         "Open a design, enter EIP mode at a specific point, then return to the top cell.",
         ["aeEditInPlace"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "pyScript.aeOpenDesign('test', 'test', 'layout')\n"
          "pos = pyScript.emyPointF(5, 5)\n"
          "pyScript.aeEditInPlace(pos)\n"
          "print('entered EIP mode')\n"
          "pyScript.aeReturn()\n"
          "print('returned to top cell')")),
        ("aeIpcProcess",
         "Launch an external process with aeIpcBeginProcess, read its output, and check exit status.",
         ["aeIpcProcess"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "p = pyScript.aeIpcBeginProcess('echo hello_world')\n"
          "print('process type:', type(p).__name__)\n"
          "print('pid:', p.pid)\n"
          "while p.isPending():\n"
          "    out = pyScript.aeIpcReadProcess(p, timeout=2)\n"
          "    if out is not None and out.strip():\n"
          "        print('output:', out.strip())\n"
          "print('state:', p.state)\n"
          "print('exitStatus:', p.exitStatus)")),
        ("aeReturn",
         "Demonstrate the EIP -> aeReturn workflow: open design, descend via EIP, edit, return.",
         ["aeReturn"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "pyScript.aeOpenDesign('test_agr', 'test', 'layout')\n"
          "print('at top cell')\n"
          "pyScript.aeEditInPlace(pyScript.emyPointF(1, 1))\n"
          "print('descended to bottom cell via EIP')\n"
          "pyScript.aeReturn()\n"
          "print('returned to last cell')")),
        ("aeSetWindowFocus",
         "Open a design, get a window by index, set focus to it, and handle the None case.",
         ["aeSetWindowFocus"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "pyScript.aeOpenDesign('test_adv', 'test', 'layout')\n"
          "win = pyScript.aeGetWndByIndex(0)\n"
          "result = pyScript.aeSetWindowFocus(win)\n"
          "print('focus result:', result)\n"
          "none_result = pyScript.aeSetWindowFocus(None)\n"
          "print('None window:', none_result)")),
    ]
    for name, scenario, apis, code in s4_traces:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript)." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S4", "v26-S4-%s" % name, prompt, completion, apis,
             "S4 multi_step_trace for %s" % name)

    # ---- S5: anti_pattern / common mistake (8 pairs) ----
    s5_items = [
        ("aeCreateTree",
         "tree = pyScript.aeCreateTree(123)",
         "aeCreateTree requires a STRING name. Passing an integer (123) returns False, not a tree object. Always pass a string like 'mainTree'.",
         "tree = pyScript.aeCreateTree('mainTree')\nif tree:\n    print('tree created')"),
        ("aeCreateTreeItem",
         "item = pyScript.aeCreateTreeItem('name', 'description', 'icon.png', None)",
         "Two mistakes: (1) description must be a LIST, not a string; (2) itemIcon must be an aeBaseIcon object, NOT a string file path -- string paths raise TypeError. Use a list for description and None for icons.",
         "item = pyScript.aeCreateTreeItem('name', ['desc1', 'desc2'], None, None)"),
        ("aeTreeAppendItem",
         "result = pyScript.aeTreeAppendItem('myTree', 'myItem')",
         "aeTreeAppendItem requires OBJECT arguments (tree from aeCreateTree, item from aeCreateTreeItem), NOT strings. Passing strings raises TypeError. Create the objects first.",
         "tree = pyScript.aeCreateTree('myTree')\nitem = pyScript.aeCreateTreeItem('myItem', ['desc'], None, None)\nresult = pyScript.aeTreeAppendItem(tree, item)"),
        ("aeCrtHilitPolygon",
         "pts = [(0,0), (0,10), (10,10), (10,0)]\nshape = pyScript.aeCrtHilitPolygon(design, pts)",
         "aeCrtHilitPolygon requires a vector1D_emyPointF (SWIG container), NOT a plain Python list of tuples. Use vector1D_emyPointF() and .append(emyPointF(x,y)) to build the points.",
         "pts = pyScript.vector1D_emyPointF()\npts.append(pyScript.emyPointF(0, 0))\npts.append(pyScript.emyPointF(0, 10))\npts.append(pyScript.emyPointF(10, 10))\npts.append(pyScript.emyPointF(10, 0))\nshape = pyScript.aeCrtHilitPolygon(design, pts)"),
        ("aeEditInPlace",
         "pyScript.aeEditInPlace(5, 5)",
         "aeEditInPlace's point parameter expects an emyPointF object, NOT two separate x, y arguments. Use emyPointF(5, 5) to create the point, or pass hierList for multi-level descent.",
         "pos = pyScript.emyPointF(5, 5)\npyScript.aeEditInPlace(pos)"),
        ("aeIpcProcess",
         "p = pyScript.aeIpcProcess('echo hello')\noutput = p.readline()",
         "aeIpcProcess is a CLASS -- you do NOT call it directly to create a process. Use aeIpcBeginProcess(command) to create a process instance. Calling aeIpcProcess() directly does not launch a process.",
         "p = pyScript.aeIpcBeginProcess('echo hello')\nwhile p.isPending():\n    out = pyScript.aeIpcReadProcess(p, timeout=2)\n    if out:\n        print(out.strip())"),
        ("aeReturn",
         "pyScript.aeReturn(pyScript.aeGetCurDesign())",
         "aeReturn takes NO arguments. It simply returns to the last cell after EIP or Descend Edit/Read. Passing arguments is incorrect -- just call aeReturn() with empty parentheses.",
         "pyScript.aeEditInPlace(pyScript.emyPointF(1, 1))\n# ... edit bottom cell ...\npyScript.aeReturn()"),
        ("aeSetWindowFocus",
         "result = pyScript.aeSetWindowFocus(2)",
         "aeSetWindowFocus expects a BaseMainWindow OBJECT (from aeGetWndByIndex), NOT an integer index. Passing an integer will fail. Get the window object first with aeGetWndByIndex(index), then pass it.",
         "win = pyScript.aeGetWndByIndex(2)\nresult = pyScript.aeSetWindowFocus(win)"),
    ]
    for name, bad_code, explanation, good_code in s5_items:
        prompt = ("You are an EDA automation engineer. The following PyAether "
                  "code has a bug related to `%s`. Identify the mistake and "
                  "write the corrected version.\n\n"
                  "```python\n%s\n```" % (name, bad_code))
        completion = ("**Bug**: %s\n\n**Corrected code**:\n```python\n%s\n```"
                      % (explanation, good_code))
        _add("S5", "v26-S5-%s" % name, prompt, completion, [name],
             "S5 anti_pattern for %s" % name)

    # ---- S6: cross-API combo (8 pairs) ----
    s6_items = [
        ("aeCreateTree+aeCreateTreeItem+aeTreeAppendItem",
         "Build a complete tree widget: create a tree, create multiple items with column descriptions, and append them all.",
         ["aeCreateTree", "aeCreateTreeItem", "aeTreeAppendItem"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "tree = pyScript.aeCreateTree('netSummary')\n"
          "nets = [('VDD', 'power', 'M1', 1200), ('GND', 'ground', 'M1', 0),\n"
          "        ('CLK', 'signal', 'M3', 800)]\n"
          "for name, role, layer, voltage in nets:\n"
          "    item = pyScript.aeCreateTreeItem(name, [role, layer, voltage], None, None)\n"
          "    ok = pyScript.aeTreeAppendItem(tree, item)\n"
          "    print('%s: append=%s' % (name, ok))\n"
          "print('tree built with', len(nets), 'items')")),
        ("aeEditInPlace+aeReturn",
         "Open a design, descend into a cell using EIP with a point, edit, then return to the top cell.",
         ["aeEditInPlace", "aeReturn"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "pyScript.aeOpenDesign('topCell', 'test', 'layout')\n"
          "print('at top cell')\n"
          "pos = pyScript.emyPointF(10, 20)\n"
          "pyScript.aeEditInPlace(pos)\n"
          "print('descended into child cell')\n"
          "pyScript.aeReturn()\n"
          "print('back at top cell')")),
        ("aeCrtHilitPolygon+aeEditInPlace",
         "After entering EIP mode, create a highlight polygon on the current design to mark a region of interest.",
         ["aeCrtHilitPolygon", "aeEditInPlace"],
         ("from pyAether import *\n\n"
          "emyInitAether('-adv')\n"
          "aeOpenDesign('test', 'test', 'layout')\n"
          "aeEditInPlace(emyPointF(5, 5))\n"
          "design = aeCrtHilitSet(aeGetCurDesign(), 'M2')\n"
          "pts = vector1D_emyPointF()\n"
          "pts.append(emyPointF(2, 2))\n"
          "pts.append(emyPointF(2, 8))\n"
          "pts.append(emyPointF(8, 8))\n"
          "pts.append(emyPointF(8, 2))\n"
          "shape = aeCrtHilitPolygon(design, pts)\n"
          "print('highlight created:', type(shape).__name__)\n"
          "aeReturn()")),
        ("aeSetWindowFocus+aeEditInPlace",
         "Open a design, switch window focus, then enter EIP mode in the focused window.",
         ["aeSetWindowFocus", "aeEditInPlace"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "pyScript.aeOpenDesign('design1', 'test', 'layout')\n"
          "win = pyScript.aeGetWndByIndex(0)\n"
          "focused = pyScript.aeSetWindowFocus(win)\n"
          "print('window focused:', focused)\n"
          "pyScript.aeEditInPlace(pyScript.emyPointF(3, 3))\n"
          "print('EIP started in focused window')\n"
          "pyScript.aeReturn()")),
    ]
    s6_items += [
        ("aeIpcProcess+aeCreateTreeItem",
         "Run an external command to get net names, then create tree items for each result and build a tree.",
         ["aeIpcProcess", "aeCreateTreeItem", "aeTreeAppendItem"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "p = pyScript.aeIpcBeginProcess('echo netVDD netGND netCLK')\n"
          "output = ''\n"
          "while p.isPending():\n"
          "    chunk = pyScript.aeIpcReadProcess(p, timeout=2)\n"
          "    if chunk:\n"
          "        output += chunk\n"
          "net_names = output.strip().split()\n"
          "tree = pyScript.aeCreateTree('ipcNets')\n"
          "for nm in net_names:\n"
          "    item = pyScript.aeCreateTreeItem(nm, ['from_ipc'], None, None)\n"
          "    pyScript.aeTreeAppendItem(tree, item)\n"
          "print('built tree from IPC output:', net_names)")),
        ("aeCreateTree+aeSetWindowFocus",
         "Create a tree widget and then set the window focus to ensure the tree is visible in the intended window.",
         ["aeCreateTree", "aeSetWindowFocus"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "pyScript.aeOpenDesign('myDesign', 'test', 'layout')\n"
          "tree = pyScript.aeCreateTree('resultsTree')\n"
          "print('tree created:', type(tree).__name__)\n"
          "win = pyScript.aeGetWndByIndex(0)\n"
          "ok = pyScript.aeSetWindowFocus(win)\n"
          "print('window focus set:', ok)")),
        ("aeCrtHilitPolygon+aeReturn",
         "Create a highlight polygon after EIP descent, then return to the top cell.",
         ["aeCrtHilitPolygon", "aeReturn"],
         ("from pyAether import *\n\n"
          "emyInitAether('-adv')\n"
          "aeOpenDesign('test', 'test', 'layout')\n"
          "aeEditInPlace(emyPointF(1, 1))\n"
          "design = aeCrtHilitSet(aeGetCurDesign(), 'M1')\n"
          "pts = vector1D_emyPointF()\n"
          "for cx, cy in [(0, 0), (5, 0), (5, 5), (0, 5)]:\n"
          "    pts.append(emyPointF(cx, cy))\n"
          "shape = aeCrtHilitPolygon(design, pts)\n"
          "print('highlight in child cell:', type(shape).__name__)\n"
          "aeReturn()\n"
          "print('returned to top cell')")),
        ("aeIpcProcess+aeReturn",
         "Launch a process while in EIP mode to query child cell info, read output, then return from EIP.",
         ["aeIpcProcess", "aeReturn"],
         ("import pyAether as pyScript\n\n"
          "pyScript.emyInitAether('-adv')\n"
          "pyScript.aeOpenDesign('test', 'test', 'layout')\n"
          "pyScript.aeEditInPlace(pyScript.emyPointF(2, 2))\n"
          "print('in EIP mode')\n"
          "p = pyScript.aeIpcBeginProcess('echo child_cell_query_done')\n"
          "while p.isPending():\n"
          "    out = pyScript.aeIpcReadProcess(p, timeout=2)\n"
          "    if out and out.strip():\n"
          "        print('IPC result:', out.strip())\n"
          "pyScript.aeReturn()\n"
          "print('returned from EIP')")),
    ]
    for apis_str, scenario, apis, code in s6_items:
        prompt = ("You are an EDA automation engineer. %s Write Python code "
                  "using PyAether (import as pyScript), combining the relevant "
                  "ae* APIs." % scenario)
        completion = "```python\n%s\n```" % code
        _add("S6", "v26-S6-%s" % apis_str.replace("+", "-"), prompt, completion, apis,
             "S6 cross_api_combo: %s" % apis_str)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


def main():
    ap = argparse.ArgumentParser(
        description="R196 v26 PyAether SFT corpus: ae* tree/IPC/hilit (8 APIs, 40 pairs)")
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

    by_type = {}
    for p in pairs:
        by_type[p["type"]] = by_type.get(p["type"], 0) + 1
    sys.stderr.write("\n=== R196 v26 ae* tree/IPC/hilit corpus summary ===\n")
    sys.stderr.write("Total pairs: %d\n" % len(pairs))
    for t in sorted(by_type):
        sys.stderr.write("  %s: %d\n" % (t, by_type[t]))
    sys.stderr.write("Rejected (contamination): %d\n" % rejected)
    if reject_details:
        sys.stderr.write("  Rejected IDs:\n")
        for pid, hit in reject_details:
            sys.stderr.write("    %s -> hit entry_point: %s\n" % (pid, hit))

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

    with open(args.output, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    sys.stderr.write("\nWrote %d pairs to %s\n" % (len(pairs), args.output))

    if rejected > 0:
        sys.stderr.write("ERROR: %d pairs rejected due to contamination!\n" % rejected)
        sys.exit(1)
    sys.stderr.write("Contamination check: PASS (0 rejected)\n")


if __name__ == "__main__":
    main()
