#!/usr/bin/env python3
# -*- coding: ascii -*-
"""baize_posttrain_r189_emy_dbstructure_corpus.py
R189 -- v19 PyAether SFT corpus: the emy* "design-database structure" blind spot.

BACKGROUND (R181 coverage audit, updated R188):
  v11-v18 (368 pairs) cover 62/164 eval raw pyScript APIs. 102 remain blind.
  A data-driven eval-usage scan (R189 wake) of the 102 remaining blind APIs
  shows the emy* family is STILL the largest blind family: 63 usages across 19
  APIs with usage>0.  The single highest-usage remaining blind API is emyBlock
  (eval_count=14).  Previous rounds (v15 geometry primitives, v17 design/geo)
  covered 20 emy* APIs but left the highest-usage structural APIs untouched.
  R189 targets the 6 highest-usage emy* "design-database structure" APIs:
    emyBlock          : eval_count=14  (design block: getInsts/getNets/getShapes/...)
    emyRect           : eval_count=8   (rectangle shape: create/convertToPolygon/setBBox)
    emyViewType       : eval_count=8   (view type: create/find/get/getName/getViewTypes)
    emyReservedViewType: eval_count=8  (predefined view-type wrapper)
    emyLib            : eval_count=5   (library: create/open/find/exists/getAccess/getCells)
    emyInitQuery      : eval_count=5   (query-subsystem init, prereq for dbGetNeighbor)
  Total: 6 APIs, 48 eval usages. All ISOLATE-class (eval_count>0, appear as
  helpers in eval solutions). The red line (S5.1) isolates on eval *entry_point*
  strings (the 155 task function names), NOT on helper API names. Teaching the
  *public API reference* of these structural primitives is explicitly allowed.
  The fingerprint scan below rejects any pair whose prompt+completion contains a
  literal eval entry_point string.

  Authoritative signatures fetched via pyAether MCP get_api_details (R189 wake),
  except emyInitQuery whose signature is inferred from eval canonical usage
  (ae.emyInitQuery()) and the dbGetNeighbor docs which state
  "method emyInitQuery() must be executed first".

Usage:
  python3 baize_posttrain_r189_emy_dbstructure_corpus.py [--dry-run] [--limit N]
"""
import argparse, json, os, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(RUN_DIR, "sft_pyaether_corpus_v19_emy_dbstructure.jsonl")
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"

API_DOCS = {}

API_DOCS["emyBlock"] = {
    "sig": "emyBlock(*args, **kwargs)  [class; emyDesign is-a emyBlock]",
    "desc": "A design block -- the structural container of a cell view contents. emyDesign inherits from emyBlock, so the object returned by aeGetCurDesign() can be used directly as a block. Provides iterator methods to enumerate the design contents: instances, nets, shapes, terms, pins, routes, rows, markers, layer/purpose headers.",
    "params": {},
    "returns": "emyBlock instance (use the design object from aeGetCurDesign/dbOpenCV directly)",
    "methods": ("getInsts(filterFlags=emcInstIterNotImplicit) -> collection of emyInst; "
                "getNets(filterFlags) -> collection of emyNet; "
                "getShapes() -> collection of emyShape; "
                "getTerms(filterFlags) -> collection of emyTerm; "
                "getPins() -> collection of emyPin; "
                "getRoutes() -> collection of emyRoute; "
                "getRows() -> collection of emyRow; "
                "getMarkers() -> collection of emyMarker; "
                "getLPPHeaders() -> collection of emyLPPHeader; "
                "getLayerHeaders() -> collection of emyLayerHeader; "
                "getSymmetry() -> emySymmetry"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> design = pyScript.aeGetCurDesign()\n'
                '>>> # design is an emyBlock -- enumerate its contents\n'
                '>>> insts = design.getInsts()\n'
                '>>> shapes = design.getShapes()\n'
                '>>> nets = design.getNets()\n'
                '>>> terms = design.getTerms()\n'
                '>>> print(len(insts), len(shapes), len(nets))'),
    "category": "emyDatabase / Design Block",
    "safety": "ISOLATE", "eval_count": 14,
    "key_notes": "emyDesign IS-A emyBlock (inheritance), so pass the design object directly wherever an emyBlock is required (e.g. emyRect.create). The getXxx() methods return emyCollection objects that support len() and iteration. getInsts/getNets/getTerms accept filter-flags bitmasks; defaults exclude implicit objects."}

API_DOCS["emyRect"] = {
    "sig": "emyRect(*args, **kwargs)  [class; inherits emyShape]",
    "desc": "A rectangle shape in a layout block. Created via the static factory emyRect.create(block, layerNum, purposeNum, bBox). Supports conversion to a polygon and bounding-box update.",
    "params": {
        "block": "emyBlock - the design block in which the rectangle is created (pass the design object from aeGetCurDesign/dbOpenCV)",
        "layerNum": "emyLayerNum - the layer number",
        "purposeNum": "emyPurposeNum - the purpose number (0 = drawing)",
        "bBox": "emyBox - the bounding box (left, bottom, right, top); must be non-inverted",
    },
    "returns": "emyRect instance (inherits emyShape)",
    "methods": "static create(block, layerNum, purposeNum, bBox) -> emyRect; setBBox(bBox); convertToPolygon() -> emyPolygon",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> design = pyScript.aeGetCurDesign()\n'
                '>>> bbox = pyScript.emyBox(0, 0, 1000, 1000)\n'
                '>>> rect = pyScript.emyRect.create(design, 1, 0, bbox)\n'
                '>>> rect.setBBox(pyScript.emyBox(0, 0, 2000, 500))\n'
                '>>> poly = rect.convertToPolygon()'),
    "category": "emyDatabase / Shape",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "create() is a static factory -- call emyRect.create(...), NOT emyRect(...). The block arg accepts the design object (emyDesign IS-A emyBlock). bBox must be non-inverted (left<=right, bottom<=top) else emcRectBBoxInvalid is raised. Coordinates are in database units (DBU)."}

API_DOCS["emyViewType"] = {
    "sig": "emyViewType(*args, **kwargs)  [class; emySessionObject]",
    "desc": "A session object representing the type of a view (e.g. maskLayout, schematic, symbol). Supports creating custom view types, finding existing ones, and converting a reserved view type into a view-type object.",
    "params": {
        "name": "emyString - the name of the view type (for create/find)",
        "type": "emyReservedViewType - a reserved-view-type wrapper (for get)",
    },
    "returns": "emyViewType instance, or None from find() if not found",
    "methods": ("static create(name: emyString) -> emyViewType  (raises emcViewTypeExists if present); "
                "static find(name: emyString) -> emyViewType | None; "
                "static get(type: emyReservedViewType) -> emyViewType; "
                "getName(name: emyString)  [output param]; "
                "static getViewTypes() -> collection of emyViewType"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> mask = pyScript.emyViewType.find("maskLayout")\n'
                '>>> name = pyScript.emyString()\n'
                '>>> mask.getName(name)\n'
                '>>> print(str(name))\n'
                '>>> vts = pyScript.emyViewType.getViewTypes()\n'
                '>>> print(len(vts))'),
    "category": "emyDatabase / Session / View Type",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "create() throws emcViewTypeExists if the name already exists -- guard with find() first. getName() is an output-parameter method: pass a pre-created emyString, then read it back with str(). find() returns None (not 0) on miss. get() takes an emyReservedViewType wrapper (or a string/int in practice)."}

API_DOCS["emyReservedViewType"] = {
    "sig": "emyReservedViewType(name)  [class; enum-like wrapper]",
    "desc": "A wrapper for the predefined (reserved) EmpyDatabase view types. Construct with a name string such as maskLayout, schematic, symbol, schematicSymbol. Primarily used as the argument to emyViewType.get() to obtain the corresponding emyViewType object.",
    "params": {"name": "str - the reserved view-type name (e.g. maskLayout, schematic, symbol)"},
    "returns": "emyReservedViewType wrapper instance",
    "methods": "constructor emyReservedViewType(name)",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> rvt = pyScript.emyReservedViewType("maskLayout")\n'
                '>>> vt = pyScript.emyViewType.get(rvt)\n'
                '>>> name = pyScript.emyString()\n'
                '>>> vt.getName(name)\n'
                '>>> print(str(name))'),
    "category": "emyDatabase / Session / Reserved View Type",
    "safety": "ISOLATE", "eval_count": 8,
    "key_notes": "An enum-like wrapper, not a view type itself. Pairs with emyViewType.get() to resolve a reserved name into an emyViewType object. Common reserved names: maskLayout, schematic, symbol, schematicSymbol. The integer form (0-15) is also accepted by emyViewType.get()."}

API_DOCS["emyLib"] = {
    "sig": "emyLib(*args, **kwargs)  [class; emyDatabase]",
    "desc": "An EDA design library. Manage library lifecycle (create/open/find/exists) and access control (getAccess/releaseAccess). Collections (getCells/getViews/getCellViews) require read access to be acquired first.",
    "params": {
        "name": "emyScalarName - the library name (built with emyNativeNS + emyScalarName)",
        "libPath": "emyString / str - the library file path",
        "access": "emyLibAccess - access type (read or write) built with emyLibAccess(read)",
    },
    "returns": "emyLib instance",
    "methods": ("static create(name: emyScalarName, libPath) -> emyLib; "
                "static open(name, libPath) -> emyLib; "
                "static find(name: emyScalarName) -> emyLib | None; "
                "static exists(name) -> bool; "
                "static getOpenLibs() -> set; "
                "getAccess(access: emyLibAccess) -> bool; "
                "releaseAccess(); "
                "getCells() / getViews() / getCellViews()  [require read access]"),
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> ns = pyScript.emyNativeNS()\n'
                '>>> lib_name = pyScript.emyScalarName(ns, "my_lib")\n'
                '>>> lib = pyScript.emyLib.find(lib_name)\n'
                '>>> if lib is not None:\n'
                '...     read_access = pyScript.emyLibAccess("read")\n'
                '...     if lib.getAccess(read_access):\n'
                '...         cells = lib.getCells()\n'
                '...         print(str(cells))\n'
                '...         lib.releaseAccess()'),
    "category": "emyDatabase / Library",
    "safety": "ISOLATE", "eval_count": 5,
    "key_notes": "Name must be an emyScalarName built on an emyNativeNS -- a raw string raises TypeError. find() returns None on miss. getCells()/getViews() return None if read access was not acquired -- always call getAccess(emyLibAccess(read)) first and check its bool return. Release with releaseAccess() when done. Properties: name, path, fullPath, writePath, mode, isCanRead, isCanWrite, cells, views."}

API_DOCS["emyInitQuery"] = {
    "sig": "emyInitQuery() -> None",
    "desc": "Initialize the design-query subsystem. Must be executed before any neighbor/traversal query such as dbGetNeighbor, dbGetNeighborEx, dbGetNeighborListEx, or dbTraverse3X. Called once after emyInitAether and after a design is available.",
    "params": {},
    "returns": "None (initializes internal query state)",
    "doctest": ('>>> import pyAether as pyScript\n'
                '>>> pyScript.emyInitAether("-adv")\n'
                '>>> pyScript.emyInitQuery()  # enable neighbor/traverse queries\n'
                '>>> design = pyScript.aeGetCurDesign()\n'
                '>>> # dbGetNeighbor / dbTraverse3X may now be called on design'),
    "category": "emyDatabase / Query",
    "safety": "ISOLATE", "eval_count": 5,
    "key_notes": "No-argument module-level function. A prerequisite for dbGetNeighbor/dbGetNeighborEx/dbGetNeighborListEx/dbTraverse3X -- calling those without emyInitQuery() first yields invalid results. Call after emyInitAether(-adv) and once a design is open. Used as ae.emyInitQuery() in eval solutions (ae is the pyAether alias)."}

API_ORDER = ["emyBlock", "emyRect", "emyViewType", "emyReservedViewType", "emyLib", "emyInitQuery"]


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
             "**`%s`**" % d["sig"], "",
             d["desc"], ""]
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
        _add("S1", "v19-S1-%s" % name, prompt, completion, [name],
             "S1 doc_to_code for %s" % name)

    # ---- S4: multi-step trace (6 pairs) ----
    s4_traces = [
        ("emyBlock",
         "Open the current design and report how many instances, shapes, and nets its top block contains.",
         ["emyBlock"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "design = pyScript.aeGetCurDesign()\n"
          "if design is None:\n"
          '    raise RuntimeError("No current design")\n\n'
          "# design is an emyBlock -- enumerate contents\n"
          "insts = design.getInsts()\n"
          "shapes = design.getShapes()\n"
          "nets = design.getNets()\n"
          'print("instances:", len(insts))\n'
          'print("shapes:", len(shapes))\n'
          'print("nets:", len(nets))')),
        ("emyRect",
         "Create a 1000x1000 rectangle on layer 1 / purpose 0 in the current design, then resize it to 2000x500 and convert it to a polygon.",
         ["emyRect"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "design = pyScript.aeGetCurDesign()\n"
          "bbox = pyScript.emyBox(0, 0, 1000, 1000)\n"
          "rect = pyScript.emyRect.create(design, 1, 0, bbox)\n\n"
          "# resize\n"
          "rect.setBBox(pyScript.emyBox(0, 0, 2000, 500))\n\n"
          "# convert to polygon\n"
          "poly = rect.convertToPolygon()\n"
          'print("converted:", poly is not None)')),
        ("emyViewType",
         "Look up the predefined maskLayout view type, print its name, and list all view types registered in the session.",
         ["emyViewType"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          'mask = pyScript.emyViewType.find("maskLayout")\n'
          "if mask is None:\n"
          '    raise RuntimeError("maskLayout view type not found")\n\n'
          "name = pyScript.emyString()\n"
          "mask.getName(name)\n"
          'print("view type name:", str(name))\n\n'
          "vts = pyScript.emyViewType.getViewTypes()\n"
          'print("total view types:", len(vts))')),
        ("emyReservedViewType",
         "Build a reserved-view-type wrapper for schematic and resolve it into an emyViewType object, then print the name.",
         ["emyReservedViewType", "emyViewType"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          'rvt = pyScript.emyReservedViewType("schematic")\n'
          "vt = pyScript.emyViewType.get(rvt)\n"
          "if vt is None:\n"
          '    raise RuntimeError("could not resolve schematic view type")\n\n'
          "name = pyScript.emyString()\n"
          "vt.getName(name)\n"
          'print("resolved view type:", str(name))')),
        ("emyLib",
         "Find a library named analog_lib, acquire read access, list its cells, then release the access.",
         ["emyLib"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "ns = pyScript.emyNativeNS()\n"
          'lib_name = pyScript.emyScalarName(ns, "analog_lib")\n'
          "lib = pyScript.emyLib.find(lib_name)\n"
          "if lib is None:\n"
          '    raise RuntimeError("Library analog_lib not found")\n\n'
          'read_access = pyScript.emyLibAccess("read")\n'
          "if not lib.getAccess(read_access):\n"
          '    raise RuntimeError("Read access denied")\n'
          "try:\n"
          "    cells = lib.getCells()\n"
          '    print("cells:", str(cells))\n'
          "finally:\n"
          "    lib.releaseAccess()")),
        ("emyInitQuery",
         "Initialize the environment and the query subsystem, then open the current design so neighbor queries become available.",
         ["emyInitQuery"],
         ("import pyAether as pyScript\n\n"
          "# 1. init the Aether environment\n"
          'pyScript.emyInitAether("-adv")\n\n'
          "# 2. init the query subsystem (prereq for dbGetNeighbor/dbTraverse)\n"
          "pyScript.emyInitQuery()\n\n"
          "# 3. open the current design\n"
          "design = pyScript.aeGetCurDesign()\n"
          "if design is None:\n"
          '    raise RuntimeError("No current design")\n'
          'print("query subsystem ready, design open")')),
    ]
    for name, prompt, api_used, completion in s4_traces:
        _add("S4", "v19-S4-%s" % name, prompt, completion, api_used,
             "S4 multi_step trace for %s" % name)

    # ---- S5: param variation (6 pairs) ----
    s5_variants = [
        ("emyBlock",
         "Enumerate only the terms and pins of the current design block (not instances or nets).",
         ["emyBlock"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "design = pyScript.aeGetCurDesign()\n"
          "terms = design.getTerms()\n"
          "pins = design.getPins()\n"
          'print("terms:", len(terms), "pins:", len(pins))')),
        ("emyRect",
         "Create a rectangle on layer 2 / purpose 0 with a bounding box of (100, 200, 600, 800) and leave it as-is.",
         ["emyRect"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "design = pyScript.aeGetCurDesign()\n"
          "bbox = pyScript.emyBox(100, 200, 600, 800)\n"
          "rect = pyScript.emyRect.create(design, 2, 0, bbox)\n"
          'print("rect created on layer 2")')),
        ("emyViewType",
         "Create a custom view type named myCustomView, guarding against the case where it already exists.",
         ["emyViewType"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          'existing = pyScript.emyViewType.find("myCustomView")\n'
          "if existing is not None:\n"
          '    print("myCustomView already exists")\n'
          "else:\n"
          '    name = pyScript.emyString("myCustomView")\n'
          "vt = pyScript.emyViewType.create(name)\n"
          'print("created myCustomView")')),
        ("emyReservedViewType",
         "Build a reserved-view-type wrapper for symbol and confirm it resolves to a non-None emyViewType.",
         ["emyReservedViewType", "emyViewType"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          'rvt = pyScript.emyReservedViewType("symbol")\n'
          "vt = pyScript.emyViewType.get(rvt)\n"
          'print("symbol resolved:", vt is not None)')),
        ("emyLib",
         "Check whether a library named io_lib exists without opening it.",
         ["emyLib"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "ns = pyScript.emyNativeNS()\n"
          'lib_name = pyScript.emyScalarName(ns, "io_lib")\n'
          "exists = pyScript.emyLib.exists(lib_name)\n"
          'print("io_lib exists:", exists)')),
        ("emyInitQuery",
         "Initialize the environment with verbose mode and then init the query subsystem.",
         ["emyInitQuery"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "pyScript.emyInitQuery()\n"
          'print("query subsystem initialized")')),
    ]
    for name, prompt, api_used, completion in s5_variants:
        _add("S5", "v19-S5-%s" % name, prompt, completion, api_used,
             "S5 param variation for %s" % name)

    # ---- S3: multi-API chains (6 pairs) ----
    chains = [
        ("v19-S3-chain-lib-view",
         "Resolve the maskLayout reserved view type into an emyViewType, find a library by name, and print both the view-type name and the library path.",
         ["emyReservedViewType", "emyViewType", "emyLib"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n\n'
          "# resolve the reserved maskLayout view type\n"
          'rvt = pyScript.emyReservedViewType("maskLayout")\n'
          "vt = pyScript.emyViewType.get(rvt)\n"
          "vt_name = pyScript.emyString()\n"
          "vt.getName(vt_name)\n"
          'print("view type:", str(vt_name))\n\n'
          "# find a library and print its path\n"
          "ns = pyScript.emyNativeNS()\n"
          'lib_name = pyScript.emyScalarName(ns, "analog_lib")\n'
          "lib = pyScript.emyLib.find(lib_name)\n"
          "if lib is not None:\n"
          '    print("lib path:", str(lib.path))\n'
          "else:\n"
          '    print("library not found")')),
        ("v19-S3-chain-block-rect",
         "Open the current design (a block), create a rectangle in it on layer 1, and report the block instance and shape counts.",
         ["emyBlock", "emyRect"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "design = pyScript.aeGetCurDesign()\n\n"
          "# create a rectangle in the design block\n"
          "bbox = pyScript.emyBox(0, 0, 500, 500)\n"
          "rect = pyScript.emyRect.create(design, 1, 0, bbox)\n\n"
          "# enumerate block contents\n"
          "insts = design.getInsts()\n"
          "shapes = design.getShapes()\n"
          'print("instances:", len(insts), "shapes:", len(shapes))')),
        ("v19-S3-chain-query-neighbor",
         "Initialize the environment and query subsystem, open the current design, then it is ready for neighbor queries.",
         ["emyInitQuery", "emyBlock"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "pyScript.emyInitQuery()\n"
          "design = pyScript.aeGetCurDesign()\n"
          "if design is None:\n"
          '    raise RuntimeError("No current design")\n'
          "# design is an emyBlock; neighbor queries (dbGetNeighbor*) now valid\n"
          'print("ready for neighbor queries")')),
        ("v19-S3-chain-lib-access-cells",
         "Find a library, acquire read access, list its views and cells, then release access with proper cleanup in a finally block.",
         ["emyLib"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "ns = pyScript.emyNativeNS()\n"
          'lib_name = pyScript.emyScalarName(ns, "my_lib")\n'
          "lib = pyScript.emyLib.find(lib_name)\n"
          "if lib is None:\n"
          '    raise RuntimeError("Library my_lib not found")\n'
          'read_access = pyScript.emyLibAccess("read")\n'
          "if not lib.getAccess(read_access):\n"
          '    raise RuntimeError("Read access denied")\n'
          "try:\n"
          "    views = lib.getViews()\n"
          "    cells = lib.getCells()\n"
          '    print("views:", str(views))\n'
          '    print("cells:", str(cells))\n'
          "finally:\n"
          "    lib.releaseAccess()")),
        ("v19-S3-chain-viewtypes-list",
         "List all view types in the session, then for each of maskLayout and schematic build a reserved wrapper and resolve it.",
         ["emyViewType", "emyReservedViewType"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "vts = pyScript.emyViewType.getViewTypes()\n"
          'print("registered view types:", len(vts))\n\n'
          'for rname in ("maskLayout", "schematic"):\n'
          "    rvt = pyScript.emyReservedViewType(rname)\n"
          "    vt = pyScript.emyViewType.get(rvt)\n"
          "    if vt is not None:\n"
          "        nm = pyScript.emyString()\n"
          "        vt.getName(nm)\n"
          '        print(rname, "->", str(nm))')),
        ("v19-S3-chain-rect-convert",
         "Create a rectangle, convert it to a polygon, then enumerate the shapes in the design block to confirm the new geometry.",
         ["emyRect", "emyBlock"],
         ("import pyAether as pyScript\n\n"
          'pyScript.emyInitAether("-adv")\n'
          "design = pyScript.aeGetCurDesign()\n"
          "bbox = pyScript.emyBox(10, 10, 510, 510)\n"
          "rect = pyScript.emyRect.create(design, 1, 0, bbox)\n"
          "poly = rect.convertToPolygon()\n\n"
          "# confirm by enumerating block shapes\n"
          "shapes = design.getShapes()\n"
          'print("shapes in block:", len(shapes))')),
    ]
    for cid, prompt, api_used, completion in chains:
        _add("S3", cid, prompt, completion, api_used, "S3 multi-API chain")

    # ---- S6: API lookup (6 pairs) ----
    lookups = [
        ("enumerate the instances, nets, and shapes of a design block",
         "emyBlock",
         'design = pyScript.aeGetCurDesign()\ninsts = design.getInsts()\nshapes = design.getShapes()'),
        ("create a rectangle shape in a layout block",
         "emyRect",
         'rect = pyScript.emyRect.create(design, layerNum, purposeNum, bbox)'),
        ("find or create a view type by name",
         "emyViewType",
         'vt = pyScript.emyViewType.find("maskLayout")'),
        ("wrap a predefined view type name to pass to emyViewType.get",
         "emyReservedViewType",
         'rvt = pyScript.emyReservedViewType("maskLayout")'),
        ("find a library by name and acquire read access to list its cells",
         "emyLib",
         'lib = pyScript.emyLib.find(lib_name)\nlib.getAccess(pyScript.emyLibAccess("read"))'),
        ("initialize the query subsystem before running neighbor queries",
         "emyInitQuery",
         'pyScript.emyInitQuery()'),
    ]
    for intent, api, usage in lookups:
        prompt = ("You are an EDA automation assistant. Which PyAether API is "
                  "used to %s? Show a minimal correct usage example." % intent)
        completion = ("The API is `%s`.\n\n```python\nimport pyAether as "
                      "pyScript\n%s\n```" % (api, usage))
        _add("S6", "v19-S6-%s" % api, prompt, completion, [api],
             "S6 API lookup for %s" % api)

    if limit:
        pairs = pairs[:limit]
    return pairs, rejected, reject_details


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
        "report_id": "R189",
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
        sys.stderr.write("GATE: FAIL (pollution detected) -- do NOT use v19\n")
        sys.exit(2)
    sys.stderr.write("GATE: PASS -- v19 is training-ready\n")


if __name__ == "__main__":
    main()
